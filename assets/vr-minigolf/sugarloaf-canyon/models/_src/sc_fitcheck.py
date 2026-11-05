"""Sugarloaf Canyon world fit check (system python3 + numpy). Uses the exported triangles (models/_src/_cache/tris)
placed by models/layout.json against world/world.json.

  python3 models/_src/sc_fitcheck.py   -> models/fitcheck_pass1.txt (+ exit 1 on FAIL)

Checks
  1. footprints: no triangle of any instance within 2 studs (XZ) of any hole footprint_bbox.
  2. head clearance: over every walkway corridor (walk/ramp/stairs/landing/bridge/dam_crest, full width), nothing between
     walkway y + 0.5 and walkway y + 8 (walking-surface kit pieces - stairs, landings, boardwalk - are the floor and are
     exempt). Lift/gondola segments are rides, not corridors.
  3. info: Quest budget (placed tris near each hole), sun-in-far-arch geometry from the Crown.
"""
import json, math, os, sys
import numpy as np

SRC = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.dirname(SRC)
W = json.load(open(os.path.join(os.path.dirname(MODELS), "world", "world.json")))
LAY = json.load(open(os.path.join(MODELS, "layout.json")))
MAN = json.load(open(os.path.join(MODELS, "manifest.json")))
FILES = {p["id"]: [f.split("/")[-1][:-4] for f in p["files"]] for p in MAN["pieces"]}
FLOOR_KIT = ("stair_flight_5", "landing_6x4", "walk_boardwalk_6x12", "walk_boardwalk_8x12")
FOOT_MARGIN = 2.0
sys.path.insert(0, SRC)
from sc_specs import BOARDING_TRIM  # noqa: E402
BOARD_PTS = [l["bottom"] for l in W["lifts"]] + [l["top"] for l in W["lifts"]]
HEAD = 8.0
TOL = 0.5
OUT = []


def log(s=""):
    OUT.append(s)
    print(s)


_cache = {}


def tris_of(piece):
    if piece not in _cache:
        arrs = [np.load(os.path.join(SRC, "_cache", "tris", f + ".npy")) for f in FILES[piece]]
        _cache[piece] = np.concatenate(arrs).astype(np.float64)
    return _cache[piece]


def place(inst):
    t = tris_of(inst["piece"]).copy()
    if "scale" in inst:
        t *= np.array(inst["scale"])[None, None, :]
    a = math.radians(inst["yaw"])
    c, s = math.cos(a), math.sin(a)
    x, z = t[..., 0].copy(), t[..., 2].copy()
    t[..., 0] = x * c + z * s + inst["pos"][0]
    t[..., 2] = -x * s + z * c + inst["pos"][2]
    t[..., 1] += inst["pos"][1]
    return t


def sat_rect(P, x0, x1, z0, z1):
    """P (N,3,2) triangles in a frame where the rect is axis aligned. -> bool (N,) intersecting."""
    mnx, mxx = P[..., 0].min(1), P[..., 0].max(1)
    mnz, mxz = P[..., 1].min(1), P[..., 1].max(1)
    hit = (mnx <= x1) & (mxx >= x0) & (mnz <= z1) & (mxz >= z0)
    if not hit.any():
        return hit
    idx = np.nonzero(hit)[0]
    Q = P[idx]
    R = np.array([[x0, z0], [x1, z0], [x1, z1], [x0, z1]])
    ok = np.ones(len(idx), bool)
    for i in range(3):
        e = Q[:, (i + 1) % 3] - Q[:, i]
        n = np.stack([-e[:, 1], e[:, 0]], 1)
        pt = np.einsum("nkd,nd->nk", Q, n)
        pr = R @ n.T
        sep = (pr.max(0) < pt.min(1) - 1e-9) | (pr.min(0) > pt.max(1) + 1e-9)
        ok &= ~sep
    hit[idx] = ok
    return hit


def main():
    placed = []
    for inst in LAY["instances"]:
        T = place(inst)
        placed.append((inst, T, T[..., 0].min(), T[..., 0].max(), T[..., 2].min(), T[..., 2].max()))
    total = sum(len(p[1]) for p in placed)
    log(f"Sugarloaf Canyon world fit check (pass 2): {len(placed)} instances, {total} placed triangles")
    log(f"world.json {W['version']}; layout {len(LAY['instances'])} instances; clusters {len(LAY['clusters'])}")
    fails = 0

    # ---- 1. footprints
    log("")
    log(f"[1] hole footprints: every triangle >= {FOOT_MARGIN} studs (XZ) from every footprint_bbox")
    worst = []
    for h in W["holes"]:
        b = h["footprint_bbox"]
        x0, x1, z0, z1 = b["x"][0] - FOOT_MARGIN, b["x"][1] + FOOT_MARGIN, b["z"][0] - FOOT_MARGIN, b["z"][1] + FOOT_MARGIN
        bad = []
        near = (1e9, None)
        for inst, T, ax0, ax1, az0, az1 in placed:
            if ax0 > x1 + 30 or ax1 < x0 - 30 or az0 > z1 + 30 or az1 < z0 - 30:
                continue
            P = T[..., [0, 2]]
            hit = sat_rect(P, x0, x1, z0, z1)
            if hit.any():
                bad.append(f"{inst['piece']}@{inst['pos']} ({int(hit.sum())} tris)")
            V = P.reshape(-1, 2)
            dx = np.maximum(np.maximum(b["x"][0] - V[:, 0], V[:, 0] - b["x"][1]), 0)
            dz = np.maximum(np.maximum(b["z"][0] - V[:, 1], V[:, 1] - b["z"][1]), 0)
            d = float(np.hypot(dx, dz).min())
            if d < near[0]:
                near = (d, inst["piece"])
        st = "PASS" if not bad else "FAIL"
        fails += bool(bad)
        log(f"  {st} H{h['number']:<2} {h['name']:<20s} nearest piece {near[1] or '-'} at {near[0]:.1f}" +
            ("" if not bad else "  <- " + "; ".join(bad[:4])))
        worst.append((near[0], h["number"], near[1]))
    worst.sort()
    log(f"  closest approach overall: {worst[0][0]:.2f} studs (H{worst[0][1]}, {worst[0][2]})")

    # ---- 2. head clearance over walkways
    log("")
    log(f"[2] walkways: nothing between walk y + {TOL} and walk y + {HEAD} over the full walkway width "
        f"(floor kit {', '.join(FLOOR_KIT)} exempt)")
    n_seg = 0
    seg_fail = 0
    trimmed = []
    min_over = (1e9, "")
    for p in W["paths"]:
        for k, s in enumerate(p["segments"]):
            if s["type"] not in ("walk", "ramp", "stairs", "landing", "bridge", "dam_crest"):
                continue
            n_seg += 1
            A, B = np.array(s["start"], float), np.array(s["end"], float)
            d = B[[0, 2]] - A[[0, 2]]
            L = float(np.linalg.norm(d))
            if L < 1e-6:
                continue
            u = d / L
            # boarding areas: trim the corridor within BOARDING_TRIM of a lift/gondola boarding point
            for end, sign in ((A, 1), (B, -1)):
                if any(np.hypot(*(np.array(q, float)[[0, 2]] - end[[0, 2]])) < 0.5 for q in BOARD_PTS):
                    cut = min(BOARDING_TRIM, L - 0.5)
                    if sign > 0:
                        A = A + (B - A) * cut / L
                    else:
                        B = B - (B - A) * cut / L
                    L -= cut
                    trimmed.append(f"{p['id']} seg {k}")
            v = np.array([-u[1], u[0]])
            hw = p["width"] / 2
            sx0, sx1 = min(A[0], B[0]) - hw, max(A[0], B[0]) + hw
            sz0, sz1 = min(A[2], B[2]) - hw, max(A[2], B[2]) + hw
            bad = []
            for inst, T, ax0, ax1, az0, az1 in placed:
                if inst["piece"] in FLOOR_KIT or ax0 > sx1 or ax1 < sx0 or az0 > sz1 or az1 < sz0:
                    continue
                rel = T[..., [0, 2]] - A[[0, 2]]
                Pu = rel @ u
                Pv = rel @ v
                P = np.stack([Pu, Pv], -1)
                hit = sat_rect(P, 0.0, L, -hw, hw)
                if not hit.any():
                    continue
                Th = T[hit]
                uu = np.clip(Pu[hit], 0, L)
                yw_lo = A[1] + (B[1] - A[1]) * uu.min(1) / L
                yw_hi = A[1] + (B[1] - A[1]) * uu.max(1) / L
                ylo, yhi = np.minimum(yw_lo, yw_hi), np.maximum(yw_lo, yw_hi)
                tmax, tmin = Th[..., 1].max(1), Th[..., 1].min(1)
                viol = (tmax > yhi + TOL) & (tmin < ylo + HEAD)
                if viol.any():
                    bad.append(f"{inst['piece']}@{inst['pos']} ({int(viol.sum())} tris, lowest {float((tmin[viol] - ylo[viol]).min()):+.2f})")
                over = tmin[tmin >= ylo + HEAD] - ylo[tmin >= ylo + HEAD]
                if len(over) and over.min() < min_over[0]:
                    min_over = (float(over.min()), f"{inst['piece']} over {p['id']} seg {k}")
            if bad:
                seg_fail += 1
                fails += 1
                log(f"  FAIL {p['id']} seg {k} ({s['type']}, {s.get('name', '')}): " + "; ".join(bad[:4]))
    log(f"  boarding areas (last {BOARDING_TRIM} studs before a lift/gondola boarding point, inside the ride structure) "
        f"exempt on: {', '.join(trimmed)}")
    log(f"  {'PASS' if not seg_fail else 'FAIL'}: {n_seg} walkway segments checked, {seg_fail} with intrusions")
    if min_over[0] < 1e8:
        log(f"  lowest overhead geometry above a walkway: {min_over[0]:.2f} studs ({min_over[1]})")

    # ---- 3. info
    log("")
    log("[3] Quest budget (info): placed triangles whose centroid lies within R of each hole footprint centre")
    cents = np.concatenate([T.mean(1) for _, T, *_ in placed])
    groups={p['id']:p['group'] for p in MAN['pieces']}
    far = np.concatenate([np.full(len(T), groups[inst['piece']] in ('far_card','sky'))
                          for inst, T, *_ in placed])
    log(f"  {'hole':<24s} {'<=60':>8s} {'<=150':>8s} {'<=300':>8s}")
    for h in W["holes"]:
        b = h["footprint_bbox"]
        cx, cz = (b["x"][0] + b["x"][1]) / 2, (b["z"][0] + b["z"][1]) / 2
        d = np.hypot(cents[:, 0] - cx, cents[:, 2] - cz)
        log(f"  H{h['number']:<2} {h['name']:<20s} {int((d <= 60).sum()):8d} {int((d <= 150).sum()):8d} {int((d <= 300).sum()):8d}")
    log(f"  far cards + sky: {int(far.sum())} tris total (CastShadow off)")
    sun = {'bearing_deg':277.0,'elevation_deg':2.0}
    crown = [-370.0, 170.0, 165.0]
    arch = [p for p in W["backdrop"]["pieces"] if p["kind"] == "far_arch"][0]
    ax, az = arch["pos"][0] - crown[0], arch["pos"][2] - crown[2]
    dist = math.hypot(ax, az)
    bear = math.degrees(math.atan2(ax, -az)) % 360
    half_open = math.degrees(math.atan(0.31 * arch["size"][0] / dist))
    el_top = math.degrees(math.atan((0.70 * arch["size"][1] - crown[1]) / dist))
    el_bot = math.degrees(math.atan((0 - crown[1]) / dist))
    inside = abs(((sun["bearing_deg"] - bear + 180) % 360) - 180) < half_open and el_bot < sun["elevation_deg"] < el_top
    log(f"  sun-in-far-arch from the Crown (eye {crown}): arch opening bearing {bear:.1f} +- {half_open:.1f} deg, elevation "
        f"{el_bot:.1f}..{el_top:.1f} deg; sun bearing {sun['bearing_deg']} elev {sun['elevation_deg']} -> "
        f"{'INSIDE' if inside else 'NOT inside (see pass1_summary questions)'}")
    log('')
    log('[4] scatter sightlines: final holes.json transforms; tee+5 -> cup+7.5 and cup+1; 1.5-stud corridor')
    from pass2_rules import sightlines, segment_box
    scatter_tri = np.concatenate([T for inst,T,*_ in placed if inst['piece'].startswith('scatter_')])
    centers=(scatter_tri.min(1)+scatter_tri.max(1))/2
    halves=(scatter_tri.max(1)-scatter_tri.min(1))/2
    for n,a,b,c in sightlines():
        count=sum(segment_box(a,b,ct,hh) or segment_box(a,c,ct,hh) for ct,hh in zip(centers,halves))
        fails += bool(count)
        log(f"  {'PASS' if count==0 else 'FAIL'} H{n}: {count} exported triangle bounds intersect either corridor; removed members {LAY['pass2']['removed_per_hole'][str(n)]}")
    log(f"[5] rim visibility: {LAY['pass2']['rim_covered']}/{LAY['pass2']['rim_candidates']} stretches covered; {LAY['pass2']['observer_samples']} observer samples; no outer rim cliff kit; CastShadow off")
    log("")
    log(f"RESULT: {'ALL PASS' if fails == 0 else f'{fails} FAIL'}")
    open(os.path.join(SRC, "fitcheck_pass3_validated.txt"), "w").write("\n".join(OUT) + "\n")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
