#!/usr/bin/env python3
"""Mover clearance check (Round 3 clearance fix): exact OBB-OBB distances between each mover collider and the static rails/walls over a
densely sampled motion cycle, plus floor clearance (lowest collider corner above the felt surface) for the blocking movers.

  python3 tools/check_clearance.py                                   # ../holes.json
  python3 tools/check_clearance.py --holes tools/out/holes-p2-preclear.json --tag preclear

Targets: H5 geyser_column, H11 ice_floe, H17 aurora_span (its timed felt collider) >= 0.15 to every rail/wall over the whole cycle;
H12 paddle_wheel and H14 icicle_bell: every corner of every collider >= 0.06 above the felt at every angle, while the lowest blocker edge
still sits below the ball's top (0.16) at the bottom of the motion, so the ball is still blocked.
Distance = 0 for touching boxes, negative = overlap (SAT penetration). Felt contacts are reported for information only (the column rides
its cliff face, the floe slides on its felt, the span joins its piers).

Round 4 (wall clearance, fitcheck): every wall box is checked, including the collision_cut residual pieces (rail5__cut0-3 / berg18__cut0-3,
sill/lintel/sides). The exact OBB distance covers all blocker corners, edges and faces. Two rows were added:
  - H11 ice_floe VISUAL envelope: the blocker footprints extended up to the floe mesh top (VISUAL_TOP, 1.12: snow + snowpuff on top,
    3D Model Bot fitcheck "floe top <= 1.12"). The 1.0-tall colliders alone miss the lintel (cut1) gap.
  - H12 paddle_wheel vs rails/hull walls over a full turn (target 0.06): paddles are z +-0.2 about the axle at z -17.75.
"""
import argparse, json, math, os
import numpy as np
import sim as S

TARGET_STATIC = 0.15
TARGET_FLOOR = 0.06
TARGET_WHEEL = 0.06
VISUAL_TOP = {"ice_floe": 1.12}   # mover-local top of the modelled mesh where it is taller than the collider
BALL_D = 2 * S.BALL_RADIUS
SIGNS = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)], float)
EDGES = [(a, b) for a in range(8) for b in range(a + 1, 8) if np.sum(SIGNS[a] != SIGNS[b]) == 1]


def corners(c, h, R):
    return c + (SIGNS * h) @ R.T


def point_box(p, c, h, R):
    l = (p - c) @ R
    return float(np.linalg.norm(l - np.clip(l, -h, h)))


def seg_seg(p1, q1, p2, q2):
    d1, d2, r = q1 - p1, q2 - p2, p1 - p2
    a, e, f = d1 @ d1, d2 @ d2, d2 @ r
    c, b = d1 @ r, d1 @ d2
    den = a * e - b * b
    s = np.clip((b * f - c * e) / den, 0, 1) if den > 1e-12 else 0.0
    t = (b * s + f) / e
    if t < 0: t, s = 0.0, np.clip(-c / a, 0, 1)
    elif t > 1: t, s = 1.0, np.clip((b - c) / a, 0, 1)
    return float(np.linalg.norm(p1 + d1 * s - (p2 + d2 * t)))


def sat_gap(c1, h1, R1, c2, h2, R2):
    best = -1e9
    axes = [R1[:, i] for i in range(3)] + [R2[:, i] for i in range(3)] + \
           [np.cross(R1[:, i], R2[:, j]) for i in range(3) for j in range(3)]
    for ax in axes:
        n = np.linalg.norm(ax)
        if n < 1e-9: continue
        ax = ax / n
        best = max(best, abs((c2 - c1) @ ax) - np.abs(ax @ R1) @ h1 - np.abs(ax @ R2) @ h2)
    return best


def obb_dist(c1, h1, R1, c2, h2, R2):
    """exact min distance between two boxes (<= 0: touching/overlapping, SAT depth)."""
    g = sat_gap(c1, h1, R1, c2, h2, R2)
    if g <= 1e-9 or g > 0.5:  # overlap depth, or far apart (SAT gap is a lower bound; exact below 0.5)
        return g
    A, B = corners(c1, h1, R1), corners(c2, h2, R2)
    d = min(min(point_box(p, c2, h2, R2) for p in A), min(point_box(p, c1, h1, R1) for p in B))
    for a0, a1 in EDGES:
        for b0, b1 in EDGES:
            d = min(d, seg_seg(A[a0], A[a1], B[b0], B[b1]))
    return d


def felt_box(f):
    th = f.get("thickness", .4); R = S.yaw_R(f.get("yaw", 0)); h = np.array([f["size"][0] / 2, th / 2, f["size"][1] / 2]); c = np.array(f["center"], float)
    sl = f.get("slope")
    if sl:
        ax = 0 if sl["axis"] == "x" else 2; ang = math.atan(sl["rise"] / f["size"][0 if ax == 0 else 1]); co, si = math.cos(ang), math.sin(ang)
        tilt = np.array([[co, -si, 0], [si, co, 0], [0, 0, 1]]) if ax == 0 else np.array([[1, 0, 0], [0, co, si], [0, -si, co]])
        R = R @ tilt; h[ax] /= co
    return c - R[:, 1] * th / 2, h, R


def statics(hole):
    W = [(w["id"], np.array(w["center"], float), np.array(w["size"], float) / 2, S.yaw_R(w.get("yaw", 0))) for w in hole["walls"]]
    F = [("felt:" + f["id"], *felt_box(f)) for f in hole["felt"]]
    return W, F


def mover_boxes(ha, j, t):
    Rth, Rw, cen = np.empty(9), np.empty(9), np.empty(3)
    out = []
    for k in range(ha.nMB):
        if int(ha.MB[k, 0]) != j: continue
        S.blocker_pose(ha.MP, ha.MB, k, t, Rth, Rw, cen)
        out.append((k, cen.copy(), ha.MB[k, 4:7].copy(), Rw.reshape(3, 3).copy()))
    return out


def near(boxes, lst, pad=1.0):
    """prefilter statics by AABB overlap (+pad) with the swept boxes."""
    lo = np.min([c - np.abs(R) @ h for _, c, h, R in boxes], axis=0) - pad
    hi = np.max([c + np.abs(R) @ h for _, c, h, R in boxes], axis=0) + pad
    keep = []
    for s in lst:
        e = np.abs(s[3]) @ s[2]
        if np.all(s[1] + e >= lo) and np.all(s[1] - e <= hi): keep.append(s)
    return keep


def visual_hole(hole, part):
    """copy of hole with part's blockers extended up to VISUAL_TOP (unrotated slide blockers only)."""
    h = json.loads(json.dumps(hole)); top = VISUAL_TOP[part]
    for b in next(m for m in h["moving_parts"] if m["id"] == part)["blockers"]:
        lo = b["center"][1] - b["size"][1] / 2
        b["center"][1] = (lo + top) / 2; b["size"][1] = top - lo
    return h


def static_check(hole, part, samples, target=TARGET_STATIC, label=None):
    ha = S.HoleArrays(hole); W, F = statics(hole)
    j = [m["id"] for m in hole["moving_parts"]].index(part); m = hole["moving_parts"][j]
    if m["type"] == "toggle":  # collider = the timed felt piece(s), fixed in place while solid
        ids = set(m["felt_ids"])
        sweep = [[(i, *felt_box(f)) for i, f in enumerate(hole["felt"]) if f["id"] in ids]]
        F = [s for s in F if s[0][5:] not in ids]
        ts = [m["solid_window"][0]]
    else:
        per = S.cycle_period(m)
        ts = list(np.linspace(0, per, samples, endpoint=False))
        sweep = [mover_boxes(ha, j, t) for t in ts]
    allb = [b for bs in sweep for b in bs]
    Wn, Fn = near(allb, W), near(allb, F)
    res = dict(hole=hole["number"], part=part, label=label or "collider", samples=len(ts), walls={}, felt={})
    for t, bs in zip(ts, sweep):
        for key, lst in (("walls", Wn), ("felt", Fn)):
            for sid, sc, sh, sR in lst:
                d = min(obb_dist(c, h, R, sc, sh, sR) for _, c, h, R in bs)
                cur = res[key].get(sid)
                if cur is None or d < cur[0]: res[key][sid] = (d, float(t))
    wmin = min(res["walls"].items(), key=lambda kv: kv[1][0]) if res["walls"] else ("-", (math.inf, 0))
    fmin = min(res["felt"].items(), key=lambda kv: kv[1][0]) if res["felt"] else ("-", (math.inf, 0))
    res.update(min_wall=wmin[1][0], min_wall_id=wmin[0], min_wall_t=wmin[1][1], min_felt=fmin[1][0], min_felt_id=fmin[0],
               target=target, ok=wmin[1][0] >= target - 1e-6)
    if m["type"] != "toggle":   # motion position at the minimum: slide offset (studs) / rotation angle (deg)
        v = S.part_state(ha.MP, j, res["min_wall_t"])[0]
        res["min_wall_at"] = (math.degrees(v) % 360, "deg") if m["type"] == "rotate" else (v, "studs")
    res["walls"] = {k: round(float(v[0]), 4) for k, v in sorted(res["walls"].items(), key=lambda kv: kv[1][0])}
    res["felt"] = {k: round(float(v[0]), 4) for k, v in sorted(res["felt"].items(), key=lambda kv: kv[1][0])}
    return res


def floor_check(hole, part, n):
    """lowest corner of every blocker above the felt surface under it, over n angles of the part's motion."""
    ha = S.HoleArrays(hole)
    j = [m["id"] for m in hole["moving_parts"]].index(part); m = hole["moving_parts"][j]
    if m["type"] == "swing":
        angs = np.linspace(-m["amplitude_deg"], m["amplitude_deg"], n)
    else:
        angs = np.linspace(0, 360, n, endpoint=False)
    nb = sum(1 for k in range(ha.nMB) if int(ha.MB[k, 0]) == j)
    per_blk = [dict(min=math.inf, at=None, rest=None) for _ in range(nb)]
    lowest_at_bottom = math.inf
    for a in angs:
        MPx = ha.MP.copy(); MPx[j, 0] = 0; MPx[j, 7] = 0.0; MPx[j, 8] = 0.0; MPx[j, 11] = math.radians(a)  # frozen at angle a
        hhx = S.HoleArrays.__new__(S.HoleArrays); hhx.MP = MPx; hhx.MB = ha.MB; hhx.nMB = ha.nMB
        for q, (k, c, h, R) in enumerate(mover_boxes(hhx, j, 0.0)):
            g = math.inf
            for p in corners(c, h, R):
                b, bh, _ = S.support(ha.P, p[0], p[2], p[1] + 5.0, 0.0, S.BALL_RADIUS)
                if b >= 0: g = min(g, p[1] - bh)
            if g < per_blk[q]["min"]: per_blk[q].update(min=g, at=float(a))
            if abs(a) < 1e-9: per_blk[q]["rest"] = g
            lowest_at_bottom = min(lowest_at_bottom, g)
    mn = min(b["min"] for b in per_blk)
    res = dict(hole=hole["number"], part=part, samples=n, min_floor=mn, target=TARGET_FLOOR, blocks_ball=mn < BALL_D - 0.05,
               blockers=[{k: (round(v, 4) if isinstance(v, float) else v) for k, v in b.items()} for b in per_blk])
    if m["type"] == "swing":
        res["foot_rest"] = min(b["rest"] for b in per_blk[1:]); res["bell_rest"] = per_blk[0]["rest"]; res["bell_min"] = per_blk[0]["min"]
    res["ok"] = mn >= TARGET_FLOOR - 1e-6 and res["blocks_ball"]
    return res


def run(path, samples=2001, n_ang=7201):
    H = {h["number"]: h for h in json.load(open(path))["holes"]}
    out = [static_check(H[5], "geyser_column", samples), static_check(H[11], "ice_floe", samples),
           static_check(visual_hole(H[11], "ice_floe"), "ice_floe", samples, label=f"visual top {VISUAL_TOP['ice_floe']}"),
           static_check(H[12], "paddle_wheel", samples, target=TARGET_WHEEL), static_check(H[17], "aurora_span", 1),
           floor_check(H[12], "paddle_wheel", n_ang), floor_check(H[14], "icicle_bell", n_ang)]
    return out


def slot_probe(path, n=40000, seed=5):
    """fire balls into the 0.15 slots the rail trims leave (H5 upper_rail ends beside the column, H17 pier rail ends beside the span):
    random start near the slot, aim within 70 deg of it, any power, any phase. Counts escapes, timeouts and rests inside the slot."""
    H = {h["number"]: h for h in json.load(open(path))["holes"]}
    rng = np.random.default_rng(seed); PH = S.ph_array(); out = []
    cases = [(5, [(sx * 1.575, 4.0, -28.0) for sx in (-1, 1)], [(sx * 1.575, 4.0, -29.0) for sx in (-1, 1)], (1.42, 1.73, -28.1, -27.4)),
             (5, [(sx * 1.575, 0.0, -28.0) for sx in (-1, 1)], [(sx * 1.9, 0.0, -26.0) for sx in (-1, 1)], (1.42, 1.73, -28.1, -27.4)),
             (17, [(sx * 1.5, 0.0, z) for sx in (-1, 1) for z in (-24.925, -33.075)], [(sx * 1.2, 0.0, z) for sx in (-1, 1) for z in (-23.8, -34.2)],
              (1.35, 1.65, -25.1, -24.75)), ]
    for hn, slots, starts, box in cases:
        ha = S.HoleArrays(H[hn]); per = max(S.cycle_period(m) for m in H[hn]["moving_parts"])
        res = dict(hole=hn, n=0, escapes=0, timeouts=0, slot_rests=0, outcomes={})
        for (tx, ty, tz), (x0, y0, z0) in zip(slots, starts):
            m = n // len(slots)
            X = x0 + rng.uniform(-.25, .25, m); Z = z0 + rng.uniform(-.25, .25, m); Y = np.full(m, y0)
            A = np.arctan2(tz - Z, tx - X) + np.radians(rng.uniform(-70, 70, m)); V = rng.uniform(0.3, 10.0, m); T = rng.uniform(0, per, m)
            oc, ex = S.fuzz_batch(*ha.args(), PH, X, Z, Y, A, V, T)
            res["n"] += m; res["escapes"] += int((oc == 3).sum()); res["timeouts"] += int((oc == 4).sum())
            ax, az = np.abs(ex[:, 0]), ex[:, 2]
            res["slot_rests"] += int(((oc == 0) & (ax > box[0]) & (ax < box[1]) & (az > box[2]) & (az < box[3])).sum())
            for o, c in zip(*np.unique(oc, return_counts=True)): res["outcomes"][int(o)] = res["outcomes"].get(int(o), 0) + int(c)
        out.append(res)
    return out


def table(rs):
    lines = ["| Hole | Mover | Check | Min clearance | Nearest | Target | OK |", "|---|---|---|---|---|---|---|"]
    for r in rs:
        if "min_wall" in r:
            lines.append(f"| H{r['hole']} | {r['part']} | {r['label']} vs rails/walls (full cycle, {r['samples']} samples; at t {r['min_wall_t']:.3f} s{(f", {r['min_wall_at'][0]:+.2f} {r['min_wall_at'][1]}" if "min_wall_at" in r else "")}) | {r['min_wall']:.3f} | "
                         f"{r['min_wall_id']} | >= {r['target']} | {'yes' if r['ok'] else 'NO'} |")
        else:
            extra = f"; foot at rest {r['foot_rest']:.3f}, bell min {r['bell_min']:.3f}" if "foot_rest" in r else ""
            lines.append(f"| H{r['hole']} | {r['part']} | lowest corner over felt ({r['samples']} angles{extra}) | {r['min_floor']:.3f} | "
                         f"felt | >= {r['target']}, < {BALL_D} | {'yes' if r['ok'] else 'NO'} |")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--holes", default=os.path.join(S.HERE, "..", "holes.json"))
    ap.add_argument("--tag", default="post")
    ap.add_argument("--samples", type=int, default=2001)
    ap.add_argument("--angles", type=int, default=7201)
    ap.add_argument("--probe", action="store_true", help="only the slot probe (balls fired into the trimmed rail-end slots)")
    o = ap.parse_args()
    if o.probe:
        pr = slot_probe(o.holes)
        for r in pr: print(r)
        json.dump(pr, open(os.path.join(S.HERE, "out", f"slot-probe-{o.tag}.json"), "w"), indent=1)
        raise SystemExit
    rs = run(o.holes, o.samples, o.angles)
    print(table(rs))
    for r in rs:
        if "min_wall" in r:
            print(f"  H{r['hole']} {r['part']} ({r['label']}): walls {dict(list(r['walls'].items())[:4])}; felt (info) {r['min_felt_id']} {r['min_felt']:.3f}")
    os.makedirs(os.path.join(S.HERE, "out"), exist_ok=True)
    json.dump(rs, open(os.path.join(S.HERE, "out", f"clearance-{o.tag}.json"), "w"), indent=1, default=float)
