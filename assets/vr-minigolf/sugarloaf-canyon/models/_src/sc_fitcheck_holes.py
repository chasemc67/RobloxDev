"""Sugarloaf Canyon full-kit fit check vs holes.json at 0.15 clearance (system python + numpy). Pass 6 edition.

  python _src/sc_fitcheck_holes.py   -> models/fitcheck_pass6.txt (+ _src/fitcheck_pass6_validated.txt if ALL PASS)

Pass 6 additions (see the [A]/[B]/[C]/[D] headers in the report):
  [A] per-hole dressing (manifest group "hole_dressing": trading post, per-hole prop/plant/ground merges) is placed
      INSIDE the hole areas by design, so it is exempt from the coarse 2-stud footprint_bbox rule and is judged by the
      exact 0.15 play-volume test [1] plus the lane rules [C].
  [B] edge railings: railing_12 and the peppermint_dam crest parapet stand ON the walkway edge (rails: ['left',
      'right'] in world.json). Their triangles are not overhead when they lie entirely in the outer EDGE_BAND studs of
      the corridor and top out <= EDGE_TOP above the walk; such triangles are skipped and counted as INFO. Anything
      of those pieces further in, or higher, is still a FAIL. Also reports the minimum clearance of the gondola
      (cable + cabin sweep) over every walkway segment it crosses, e.g. p_h18_hub seg 3.
  [C] lane rules for hole dressing: nothing taller than 2 studs above the felt within 3 studs (XZ) of a rail, and
      no plant geometry (pieces *_plants) within 1.5 studs of the rail strip.
  [D] info: Quest near-field triangles per hole (centroid within 60 / 150 studs of the footprint centre), before
      (pass-5 layout) and after.

Every placed layout.json instance (exported triangles from _src/_cache/tris, same placement as sc_fitcheck.place) plus
the Sunset Gondola cabin swept along both haul ropes (every 1 stud of arc length, both directions) is tested against
each hole's play elements from holes.json (the source of truth), placed by world = R_y(world_yaw) * local +
world_offset (x' = lx cos + lz sin, z' = -lx sin + lz cos; same convention as world.json placement_convention).

Volumes (hole local frame, then element yaw, then hole yaw/offset):
  felt         box = footprint x [surface - thickness, surface + 8] in a frame sheared by the slope plane, expanded
               0.15 in x/z and below: covers "within 0.15 (3D) of the felt" and "inside the play column above the
               felt (up to +8) within 0.15 XZ". Moving-part felt (lock gate top, lift deck, quay lip) is swept.
  wall/bumper  full 3D box, 0.15.
  cup          cylinder r 0.5 as a 1.0 x 1.0 box from cup y - 0.6 to cup y + 0.15; flag pole box (pole_diameter, from
               the felt to pole_height); banner swept round the pole (it turns to face the tee): 2*w square, banner h.
  tee          1.5 x 1.5 pad from tee y - 0.15 to tee y + 8.
  drop         lower ('to') felt footprint from its surface up to the upper ('from') felt surface + 8.
  hazard       the water/pit surface rectangle (0.15 above/below it).
  moving_parts every blocker (and moving felt) over its swept range: rotate range null = 360 deg in 1 deg steps,
               slide/lift/swing ranges in <= 0.05-stud / 0.25-deg steps; each sampled box is padded by half the
               maximum chord travelled between samples so the sampled union covers the continuous sweep.
  teleports    entry: radius (or half_size rectangle) from y - 0.15 to y + 1.0; exit: 1.0 radius box, y -0.15..+1.0.
Intrusion = any triangle within 0.15 studs of a volume: conservative SAT test against the 0.15-expanded box, then
the exact triangle-box distance (0 if they intersect; otherwise min of triangle-edge-to-box and box-corner-to-triangle
distances, which is exact for disjoint convex sets). Felt distances are measured in the slope-sheared frame (slopes
<= 0.25, error < 3 %).
Also kept from sc_fitcheck.py: [A] 2-stud XZ footprint check vs world.json footprint_bbox, [B] walkway head clearance.
"""
import json, math, os, sys, time
import numpy as np

SRC = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.dirname(SRC)
COURSE = os.path.dirname(MODELS)
sys.path.insert(0, SRC)
import sc_fitcheck as F          # noqa: E402  (helpers: place, sat_rect, FLOOR_KIT, W, LAY, MAN; main() not run)
import gondola_geom as G         # noqa: E402

HOLES = json.load(open(os.path.join(COURSE, "holes.json")))["holes"]
LAY = json.load(open(os.path.join(MODELS, "layout.json")))
MAN = json.load(open(os.path.join(MODELS, "manifest.json")))
W = F.W
GROUP = {p["id"]: p["group"] for p in MAN["pieces"]}
DRESS = {p["id"] for p in MAN["pieces"] if p["group"] == "hole_dressing"}
EDGE_RAIL_PIECES = ("railing_12", "peppermint_dam")
EDGE_BAND = 0.6
EDGE_TOP = 4.0
PASS = "6"
CLR = 0.15
COL = 8.0
OUT = []


def log(s=""):
    OUT.append(s)
    print(s, flush=True)


# ----------------------------------------------------------------------------- math
def Ry(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Raxis(axis, deg):
    k = np.array(axis, float)
    k /= np.linalg.norm(k)
    a = math.radians(deg)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


class Vol:
    """Box [lo, hi] in a local q-frame: q = Mv @ (p - c). Mv = (optional shear) @ R^T."""
    __slots__ = ("hole", "elem", "kind", "c", "Mv", "Minv", "lo", "hi", "pad", "wlo", "whi")

    def __init__(self, hole, elem, kind, c, R, lo, hi, shear=(0.0, 0.0), pad=0.0):
        self.hole, self.elem, self.kind = hole, elem, kind
        S = np.array([[1, 0, 0], [-shear[0], 1, -shear[1]], [0, 0, 1]], float)
        self.c = np.asarray(c, float)
        self.Mv = S @ R.T
        self.Minv = np.linalg.inv(self.Mv)
        self.lo = np.asarray(lo, float) - pad
        self.hi = np.asarray(hi, float) + pad
        self.pad = pad
        cs = np.array([[x, y, z] for x in (self.lo[0], self.hi[0]) for y in (self.lo[1], self.hi[1])
                       for z in (self.lo[2], self.hi[2])])
        wc = cs @ self.Minv.T + self.c
        self.wlo, self.whi = wc.min(0) - CLR, wc.max(0) + CLR


def tri_box_sat(T, h):
    """T (N,3,3) in box-centred frame, h (3,) half extents -> bool (N,) intersecting (separating axis theorem)."""
    v0, v1, v2 = T[:, 0], T[:, 1], T[:, 2]
    hit = np.ones(len(T), bool)
    for i in range(3):
        mn = np.minimum(np.minimum(v0[:, i], v1[:, i]), v2[:, i])
        mx = np.maximum(np.maximum(v0[:, i], v1[:, i]), v2[:, i])
        hit &= (mn <= h[i]) & (mx >= -h[i])
    e = [v1 - v0, v2 - v1, v0 - v2]
    n = np.cross(e[0], e[1])
    d = np.einsum("ij,ij->i", n, v0)
    r = np.abs(n) @ h
    hit &= np.abs(d) <= r + 1e-9
    I = np.eye(3)
    for ei in e:
        for k in range(3):
            a = np.cross(np.broadcast_to(I[k], ei.shape), ei)
            p0, p1, p2 = (np.einsum("ij,ij->i", a, v) for v in (v0, v1, v2))
            rr = np.abs(a) @ h
            mn = np.minimum(np.minimum(p0, p1), p2)
            mx = np.maximum(np.maximum(p0, p1), p2)
            hit &= ~((mn > rr + 1e-9) | (mx < -rr - 1e-9))
    return hit


def pt_box(P, h):
    q = np.maximum(np.abs(P) - h, 0.0)
    return np.linalg.norm(q, axis=-1)


def seg_box(A, B, h, it=48):
    """Exact (ternary search on a convex function) distance of segments A->B (N,3) to the box; returns d, point."""
    lo = np.zeros(len(A))
    hi = np.ones(len(A))
    for _ in range(it):
        m1 = lo + (hi - lo) / 3
        m2 = hi - (hi - lo) / 3
        f1 = pt_box(A + (B - A) * m1[:, None], h)
        f2 = pt_box(A + (B - A) * m2[:, None], h)
        left = f1 > f2
        lo = np.where(left, m1, lo)
        hi = np.where(left, hi, m2)
    t = (lo + hi) / 2
    P = A + (B - A) * t[:, None]
    return pt_box(P, h), P


def pt_seg(P, A, B):
    d = B - A
    t = np.clip(np.einsum("ij,ij->i", P - A, d) / np.maximum(np.einsum("ij,ij->i", d, d), 1e-12), 0, 1)
    Q = A + d * t[:, None]
    return np.linalg.norm(P - Q, axis=1), Q


def pt_tri(P, T):
    """Distance from points P (N,3) to triangles T (N,3,3) and the closest point on the triangle."""
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    n = np.cross(b - a, c - a)
    nn = np.maximum(np.einsum("ij,ij->i", n, n), 1e-18)
    t = np.einsum("ij,ij->i", P - a, n) / nn
    Q = P - n * t[:, None]
    # barycentric inside test
    def side(u, v):
        return np.einsum("ij,ij->i", np.cross(v - u, Q - u), n)
    inside = (side(a, b) >= 0) & (side(b, c) >= 0) & (side(c, a) >= 0)
    best = np.where(inside, np.linalg.norm(P - Q, axis=1), np.inf)
    bq = Q.copy()
    for u, v in ((a, b), (b, c), (c, a)):
        d, q = pt_seg(P, u, v)
        m = d < best
        best = np.where(m, d, best)
        bq[m] = q[m]
    return best, bq


def tri_box_dist(T, h):
    """Exact distance triangle(s)-box (box-centred frame). Returns d (N,), closest point on the triangle (N,3)."""
    best = np.full(len(T), np.inf)
    bp = T.mean(1).copy()
    inter = tri_box_sat(T, h)
    for i in range(3):
        d, P = seg_box(T[:, i], T[:, (i + 1) % 3], h)
        m = d < best
        best = np.where(m, d, best)
        bp[m] = P[m]
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                corner = np.broadcast_to(h * np.array([sx, sy, sz]), (len(T), 3))
                d, Q = pt_tri(corner, T)
                m = d < best
                best = np.where(m, d, best)
                bp[m] = Q[m]
    best[inter] = 0.0
    return best, bp


# ----------------------------------------------------------------------------- hole volumes
def hole_frame(h):
    return np.array(h["world_offset"], float), Ry(h["world_yaw"])


def felt_vol(h, f, kind="felt", offset=None, pad=0.0, tag=""):
    off, Rh = hole_frame(h)
    R = Rh @ Ry(f.get("yaw", 0.0))
    cl = np.array(f["center"], float) + (np.asarray(offset) if offset is not None else 0)
    c = off + Rh @ cl
    sx, sz = f["size"]
    a = b = 0.0
    if f.get("slope"):
        if f["slope"]["axis"] == "x":
            a = f["slope"]["rise"] / sx
        else:
            b = f["slope"]["rise"] / sz
    th = f.get("thickness", 0.4)
    return Vol(h["number"], f"{kind}:{f['id']}{tag}", kind, c, R, (-sx / 2, -th, -sz / 2), (sx / 2, COL, sz / 2),
               shear=(a, b), pad=pad)


def box_vol(h, elem, kind, center_local, size, R_local, pad=0.0):
    off, Rh = hole_frame(h)
    c = off + Rh @ np.asarray(center_local, float)
    hs = np.asarray(size, float) / 2
    return Vol(h["number"], elem, kind, c, Rh @ R_local, -hs, hs, pad=pad)


def felt_by_id(h):
    return {f["id"]: f for f in h["felt"]}


def mover_states(m):
    """[(label, R_mover (3x3 hole-local), translation (3,) hole-local, pad)] covering the swept range."""
    piv = np.array(m.get("pivot", [0, 0, 0]), float)
    ax = np.array(m.get("axis", [0, 1, 0]), float)
    ax /= np.linalg.norm(ax)
    out = []
    rmax = 0.0
    for b in m.get("blockers", []):
        rmax = max(rmax, np.linalg.norm(b["center"]) + np.linalg.norm(b["size"]) / 2)
    t = m["type"]
    if t in ("rotate", "swing"):
        rng = m.get("range") or [0.0, 360.0]
        if t == "swing":
            rng = [-m["amplitude_deg"], m["amplitude_deg"]]
        step = 1.0 if rng[1] - rng[0] > 60 else 0.25
        angs = np.arange(rng[0], rng[1] + 1e-9, step)
        pad = rmax * 2 * math.sin(math.radians(step / 2)) / 2
        for a in angs:
            out.append((f"{a:.2f}deg", Raxis(ax, a), piv, pad))
    else:
        if t == "lift":
            rng = [0.0, m["schedule"]["height"]]
        elif t == "quay_lip":
            rng = [-max(f.get("thickness", 0) for f in m.get("felt", [{"thickness": 0}])), 0.0]
        else:
            rng = m["range"] or [0.0, 0.0]
        n = max(1, int(math.ceil((rng[1] - rng[0]) / 0.05)))
        pad = (rng[1] - rng[0]) / n / 2
        for k in range(n + 1):
            o = rng[0] + (rng[1] - rng[0]) * k / n
            out.append((f"{o:+.2f}", np.eye(3), piv + ax * o, pad))
    return out


def hole_volumes(h):
    V = []
    fb = felt_by_id(h)
    for f in h["felt"]:
        V.append(felt_vol(h, f))
    for w in h["walls"]:
        kind = "bumper" if w.get("kind") == "bumper" else "wall"
        V.append(box_vol(h, f"{kind}:{w['id']}", kind, w["center"], w["size"], Ry(w.get("yaw", 0.0))))
    cup = h["cup"]
    cp = np.array(cup["position"], float)
    V.append(box_vol(h, "cup", "cup", cp + [0, -0.225, 0], [2 * cup["radius"], 0.75, 2 * cup["radius"]], np.eye(3)))
    fl = cup.get("flag") or {}
    if fl:
        ph, pdm = fl["pole_height"], fl["pole_diameter"]
        V.append(box_vol(h, "flag:pole", "flag", cp + [0, ph / 2, 0], [pdm, ph, pdm], np.eye(3)))
        bw, bh = fl["banner_size"][:2]
        V.append(box_vol(h, "flag:banner(swept)", "flag", cp + [0, ph - bh / 2, 0], [2 * bw, bh, 2 * bw], np.eye(3)))
    tp = np.array(h["tee"]["position"], float)
    V.append(box_vol(h, "tee", "tee", tp + [0, (COL - CLR) / 2, 0], [1.5, COL + CLR, 1.5], np.eye(3)))
    for d in h["drops"]:
        a, b = fb.get(d["from"]), fb.get(d["to"])
        if not (a and b):
            continue
        top = a["center"][1] + COL - b["center"][1]
        f2 = dict(b)
        V.append(Vol(*_drop_args(h, d, b, max(top, COL))))
    for z in h["hazards"]:
        V.append(box_vol(h, f"hazard:{z['id']}({z['type']})", "hazard", z["center"], [z["size"][0], 0.0, z["size"][1]],
                     Ry(z.get("yaw", 0.0))))
    for t in h["teleports"]:
        e = t["entry"]
        hs = e.get("half_size")
        sx, sz = (2 * hs[0], 2 * hs[1]) if hs else (2 * e["radius"], 2 * e["radius"])
        V.append(box_vol(h, f"teleport:{t['id']}:entry", "teleport", np.array(e["center"]) + [0, 0.425, 0],
                         [sx, 1.15, sz], np.eye(3)))
        x = t["exit"]
        V.append(box_vol(h, f"teleport:{t['id']}:exit", "teleport", np.array(x["center"]) + [0, 0.425, 0],
                         [2.0, 1.15, 2.0], np.eye(3)))
    for m in h["moving_parts"]:
        for lab, Rm, tr, pad in mover_states(m):
            for k, b in enumerate(m.get("blockers", [])):
                Rb = Rm @ Raxis(m.get("axis", [0, 1, 0]), b.get("roll", 0.0)) @ Ry(b.get("yaw", 0.0))
                cl = tr + Rm @ Raxis(m.get("axis", [0, 1, 0]), b.get("roll", 0.0)) @ np.array(b["center"], float)
                V.append(box_vol(h, f"moving:{m['id']}:blocker{k}@{lab}", "moving", cl, b["size"], Rb, pad=pad))
            if m["type"] in ("slide", "lift", "quay_lip"):
                for f in m.get("felt", []):
                    V.append(felt_vol(h, f, "moving_felt", offset=tr - np.array(m.get("pivot", [0, 0, 0])), pad=pad,
                                      tag=f"@{lab}"))
    return V


def _drop_args(h, d, b, top):
    off, Rh = hole_frame(h)
    R = Rh @ Ry(b.get("yaw", 0.0))
    c = off + Rh @ np.array(b["center"], float)
    sx, sz = b["size"]
    a = bb = 0.0
    if b.get("slope"):
        if b["slope"]["axis"] == "x":
            a = b["slope"]["rise"] / sx
        else:
            bb = b["slope"]["rise"] / sz
    return (h["number"], f"drop:{d['id']}({d['from']}->{d['to']})", "drop", c, R, (-sx / 2, 0.0, -sz / 2),
            (sx / 2, top, sz / 2), (a, bb))


# ----------------------------------------------------------------------------- placed triangles
def instances():
    """[(label, piece, inst_index, tris world (N,3,3))] incl. the swept gondola cabin."""
    out = []
    for k, inst in enumerate(LAY["instances"]):
        out.append((f"{inst['piece']}#{k}@{[round(v, 1) for v in inst['pos']]}", inst["piece"], k, F.place(inst)))
    cab = F.tris_of("gondola_cabin")
    for name, rope in G.ropes().items():
        fs, pts = G.samples(rope, 1.0)
        yaw = G.CABIN_YAW_UP if name == "up_line" else G.CABIN_YAW_UP + 180
        R = Ry(yaw)
        base = cab @ R.T
        allt = np.concatenate([base + np.array(p)[None, None, :] for p in pts])
        out.append((f"gondola_cabin SWEEP {name} ({len(pts)} positions, yaw {yaw:.2f})", "gondola_cabin(sweep)", -1,
                    allt))
    return out


def main():
    t0 = time.time()
    log(f"Sugarloaf Canyon pass {PASS} fit check vs holes.json @ {CLR} studs  ({time.strftime('%Y-%m-%d %H:%M')})")
    log(f"holes.json: {len(HOLES)} holes (source of truth; world_offset/world_yaw, world = R_y(yaw)*local + offset)")
    INST = instances()
    ntri = sum(len(t[3]) for t in INST)
    log(f"layout.json: {len(LAY['instances'])} instances + 2 gondola cabin sweeps; {ntri} triangles tested "
        f"(tri cache verified against manifest tris + bbox for all placed pieces; gondola_cable/cabin freshly cached)")
    # per-instance aabb
    boxes = [(lab, pc, k, T, T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)) for lab, pc, k, T in INST]
    fails = 0
    intr = {}
    near_hole = {}
    counts = {}
    for h in HOLES:
        V = hole_volumes(h)
        counts[h["number"]] = len(V)
        hlo = np.min([v.wlo for v in V], 0) - 1.0
        hhi = np.max([v.whi for v in V], 0) + 1.0
        cand = []
        for ii, (lab, pc, k, T, lo, hi) in enumerate(boxes):
            if (lo > hhi).any() or (hi < hlo).any():
                continue
            tl, th = T.min(1), T.max(1)
            m = ((tl <= hhi) & (th >= hlo)).all(1)
            if m.any():
                cand.append((ii, T[m], tl[m], th[m]))
        near = (np.inf, None)
        if cand:
            CI = np.concatenate([np.full(len(c[1]), c[0]) for c in cand])
            CT = np.concatenate([c[1] for c in cand])
            CL = np.concatenate([c[2] for c in cand])
            CH = np.concatenate([c[3] for c in cand])
        for v in (V if cand else []):
            lo1, hi1 = v.wlo - 0.85, v.whi + 0.85          # 1-stud info halo
            m = ((CL <= hi1) & (CH >= lo1)).all(1)
            if not m.any():
                continue
            ctr = (v.lo + v.hi) / 2
            hh = (v.hi - v.lo) / 2
            Tq = (CT[m] - v.c) @ v.Mv.T - ctr
            s = tri_box_sat(Tq, hh + 1.0)
            if not s.any():
                continue
            idx = CI[m][s]
            d, P = tri_box_dist(Tq[s], hh)
            i = int(np.argmin(d))
            if d[i] < near[0]:
                near = (float(d[i]), f"{boxes[idx[i]][0]} vs {v.elem}")
            for ii in np.unique(idx[d < CLR]):
                sel = (idx == ii) & (d < CLR)
                j = int(np.argmin(np.where(sel, d, np.inf)))
                wp = (P[j] + ctr) @ v.Minv.T + v.c
                lab, pc = boxes[ii][0], boxes[ii][1]
                key = (lab, h["number"], v.elem)
                cur = intr.get(key)
                cnt = int(sel.sum()) + (cur[0] if cur else 0)
                if cur is None or d[j] < cur[1]:
                    intr[key] = (cnt, float(d[j]), wp, pc, v.kind)
                else:
                    intr[key] = (cnt,) + cur[1:]
        near_hole[h["number"]] = near
    # ---- report
    log("")
    log(f"[1] hole play volumes (felt+column, walls/bumpers, cup+flag, tee, drops, hazards, moving sweeps, teleports)")
    for h in HOLES:
        n = h["number"]
        hits = {k: v for k, v in intr.items() if k[1] == n}
        st = "PASS" if not hits else "FAIL"
        nr = near_hole[n]
        log(f"  {st} H{n:<2} {h['name']:<22s} {counts[n]:5d} volumes; nearest geometry "
            + (f"{nr[0]:.3f} studs ({nr[1]})" if nr[1] else "none within 1 stud"))
    if intr:
        fails += len(intr)
        log("")
        log("  INTRUSIONS (piece instance | hole | element | tris | min distance | world location of the closest point)")
        for (lab, n, el), (cnt, d, wp, pc, kind) in sorted(intr.items(), key=lambda x: (x[0][1], x[1][1])):
            log(f"  FAIL {lab} | H{n} | {el} | {cnt} tris | {d:.3f} | ({wp[0]:.2f}, {wp[1]:.2f}, {wp[2]:.2f})")
        bypc = {}
        for (lab, n, el), v in intr.items():
            bypc.setdefault(v[3], set()).add(f"H{n}")
        log("  by piece: " + "; ".join(f"{k}: {', '.join(sorted(v))}" for k, v in sorted(bypc.items())))
    dress_hits = sorted({k[0] for k in intr if boxes_piece(k[0]) in DRESS})
    log(f"  pass-6 hole dressing in [1]: {len(DRESS)} pieces, intrusions: "
        + ("ZERO" if not dress_hits else "; ".join(dress_hits)))
    # ---- [A] footprints (sc_fitcheck rule) + [B] walkways + [C] lane rules + [D] budget
    fails += legacy_checks(INST)
    fails += lane_rules(INST)
    nearfield(INST)
    log("")
    log(f"RESULT: {'ALL PASS' if fails == 0 else f'{fails} FAIL'}  ({time.time() - t0:.0f}s)")
    txt = "\n".join(OUT) + "\n"
    open(os.path.join(MODELS, f"fitcheck_pass{PASS}.txt"), "w", encoding="utf-8").write(txt)
    if fails == 0:
        open(os.path.join(SRC, f"fitcheck_pass{PASS}_validated.txt"), "w", encoding="utf-8").write(txt)
    return fails


def boxes_piece(label):
    return label.split("#")[0]


def rail_boxes(h):
    """[(centre world (3,), R world (3x3), half size (3,), rail id)] for every non-bumper wall of hole h."""
    off, Rh = hole_frame(h)
    out = []
    for w in h["walls"]:
        if w.get("kind") == "bumper":
            continue
        R = Rh @ Ry(w.get("yaw", 0.0))
        out.append((off + Rh @ np.array(w["center"], float), R, np.array(w["size"], float) / 2, w["id"]))
    return out


def xz_dist_to_box(P, c, R, hs):
    """XZ distance of points P (N,3) to the vertical prism over a yawed box footprint."""
    q = (P - c) @ R                      # box-local
    dx = np.maximum(np.abs(q[:, 0]) - hs[0], 0)
    dz = np.maximum(np.abs(q[:, 2]) - hs[2], 0)
    return np.hypot(dx, dz)


def lane_rules(INST):
    """[C] skill lane rules for the pass-6 hole dressing (triangle level, sampled at vertices/edge midpoints/centroid)."""
    log("")
    log("[C] lane rules (pass-6 hole dressing): nothing taller than 2 studs above the felt within 3 studs of a rail; no "
        "plant geometry (pieces *_plants) within 1.5 studs of the rail strip. Distances in XZ to the rail box footprint, "
        "height vs the rail's felt level (rail top - 1.0)")
    fails = 0
    dress = [(lab, pc, T) for lab, pc, k, T in INST if pc in DRESS]
    if not dress:
        log("  (no hole dressing placed)")
        return 0
    for h in HOLES:
        rails = rail_boxes(h)
        bad = []
        n_checked = 0
        for lab, pc, T in dress:
            lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)
            S = None
            for c, R, hs, rid in rails:
                ext = np.abs(R[[0, 2]][:, [0, 2]]) @ hs[[0, 2]] + 3.5
                if (lo[0] > c[0] + ext[0]) or (hi[0] < c[0] - ext[0]) or (lo[2] > c[2] + ext[1]) or (hi[2] < c[2] - ext[1]):
                    continue
                if lo[1] > c[1] + hs[1] + 8 or hi[1] < c[1] - hs[1] - 8:
                    continue
                if S is None:
                    S = np.concatenate([T, (T + np.roll(T, 1, axis=1)) / 2, T.mean(1, keepdims=True)], 1)
                d = xz_dist_to_box(S.reshape(-1, 3), c, R, hs).reshape(len(T), -1).min(1)
                m = d < 3.0
                if not m.any():
                    continue
                n_checked += int(m.sum())
                felt_y = c[1] + hs[1] - 1.0
                top = T[m][..., 1].max(1) - felt_y
                tall = top > 2.0
                if tall.any():
                    bad.append(f"{lab} vs {rid}: {int(tall.sum())} tris taller than 2 within 3 (max {float(top[tall].max()):.2f}"
                               f" at {float(d[m][tall].min()):.2f})")
                if pc.endswith("_plants"):
                    mp = d < 1.5
                    if mp.any():
                        bad.append(f"{lab} vs {rid}: {int(mp.sum())} plant tris within 1.5 (min {float(d[mp].min()):.2f})")
        fails += bool(bad)
        log(f"  {'PASS' if not bad else 'FAIL'} H{h['number']:<2} {h['name']:<22s} {n_checked:6d} dressing tris within 3 "
            f"of a rail" + ("" if not bad else "  <- " + "; ".join(bad[:4])))
    return fails


def nearfield(INST):
    log("")
    log("[D] Quest near-field budget (info): placed triangles whose centroid lies within 60 / 150 studs of each hole "
        "footprint centre (before = pass-5 layout, _cache/p6/nearfield_before.json); budget ~40k per hole")
    bfile = os.path.join(SRC, "_cache", "p6", "nearfield_before.json")
    before = json.load(open(bfile)) if os.path.exists(bfile) else {}
    keep = [(pc, T) for lab, pc, k, T in INST if pc != "gondola_cabin(sweep)"]
    cents = np.concatenate([T.mean(1) for pc, T in keep])
    grp = np.concatenate([np.full(len(T), GROUP.get(pc, "?")) for pc, T in keep])
    log(f"  {'hole':<26s} {'<=60 before':>12s} {'<=60 after':>11s} {'cliff':>7s} {'dressing':>9s} {'<=150 after':>12s}")
    rows = {}
    for h in W["holes"]:
        b = h["footprint_bbox"]
        cx, cz = (b["x"][0] + b["x"][1]) / 2, (b["z"][0] + b["z"][1]) / 2
        d = np.hypot(cents[:, 0] - cx, cents[:, 2] - cz)
        m = d <= 60
        bf = before.get(str(h["number"]), {}).get("r60", -1)
        rows[h["number"]] = dict(r60_before=bf, r60=int(m.sum()), cliff=int((m & (grp == "cliff_kit")).sum()),
                                 dressing=int((m & (grp == "hole_dressing")).sum()), r150=int((d <= 150).sum()))
        r = rows[h["number"]]
        log(f"  H{h['number']:<2} {h['name']:<22s} {bf:12d} {r['r60']:11d} {r['cliff']:7d} {r['dressing']:9d} {r['r150']:12d}")
    json.dump(rows, open(os.path.join(SRC, "_cache", "p6", "nearfield_after.json"), "w"), indent=1)


def legacy_checks(INST):
    fails = 0
    GON = ("gondola_cable", "gondola_cabin", "gondola_cabin(sweep)")
    placed = [(lab, pc, T, T[..., 0].min(), T[..., 0].max(), T[..., 2].min(), T[..., 2].max()) for lab, pc, k, T in INST]
    log("")
    log(f"[A] hole footprints (sc_fitcheck rule): every triangle >= {F.FOOT_MARGIN} studs (XZ) from every world.json "
        "footprint_bbox. Gondola line (cable, tower, cabin sweep): triangles whose lowest point is more than 8 studs "
        "above the hole's tee/origin y are overflight (judged by the 3D play-column test in [1]) and listed as INFO. "
        f"Pass-6 hole dressing ({len(DRESS)} pieces, group hole_dressing) is exempt here (placed inside hole areas by "
        "design; judged by [1] at 0.15 and the lane rules [C]).")
    for h in W["holes"]:
        b = h["footprint_bbox"]
        oy = h["placement"]["origin"][1]
        x0, x1 = b["x"][0] - F.FOOT_MARGIN, b["x"][1] + F.FOOT_MARGIN
        z0, z1 = b["z"][0] - F.FOOT_MARGIN, b["z"][1] + F.FOOT_MARGIN
        bad, info = [], []
        near = (1e9, None)
        for lab, pc, T, ax0, ax1, az0, az1 in placed:
            if ax0 > x1 + 30 or ax1 < x0 - 30 or az0 > z1 + 30 or az1 < z0 - 30 or pc in DRESS:
                continue
            P = T[..., [0, 2]]
            hit = F.sat_rect(P, x0, x1, z0, z1)
            if pc in GON and hit.any():
                low = T[hit][..., 1].min(1) - oy
                over = low > COL
                if over.any():
                    info.append(f"{pc} overflight {int(over.sum())} tris, lowest {float(low[over].min()):.1f} above origin y")
                hit2 = hit.copy()
                hit2[np.nonzero(hit)[0][over]] = False
                hit = hit2
            if hit.any():
                bad.append(f"{lab} ({int(hit.sum())} tris)")
            V = P.reshape(-1, 2)
            dx = np.maximum(np.maximum(b["x"][0] - V[:, 0], V[:, 0] - b["x"][1]), 0)
            dz = np.maximum(np.maximum(b["z"][0] - V[:, 1], V[:, 1] - b["z"][1]), 0)
            dmin = float(np.hypot(dx, dz).min())
            if dmin < near[0] and pc not in GON:
                near = (dmin, pc)
        fails += bool(bad)
        log(f"  {'PASS' if not bad else 'FAIL'} H{h['number']:<2} {h['name']:<20s} nearest ground piece {near[1] or '-'} "
            f"at {near[0]:.2f}" + ("" if not bad else "  <- " + "; ".join(bad[:6])) +
            ("" if not info else "  [INFO " + "; ".join(info) + "]"))
    log("")
    log(f"[B] walkways: nothing between walk y + {F.TOL} and walk y + {F.HEAD} over the full walkway width (floor kit "
        f"exempt; last {F.BOARDING_TRIM} studs before a lift/gondola boarding point exempt), incl. gondola cable + cabin "
        f"sweep. Edge railings ({', '.join(EDGE_RAIL_PIECES)}): triangles lying entirely within the outer {EDGE_BAND} "
        f"studs of the corridor width and topping out <= {EDGE_TOP} above the walk are railings AT the walkway edge, "
        "not overhead geometry -> skipped (INFO); any other triangle of those pieces still counts")
    n_seg = seg_fail = 0
    min_over = (1e9, "")
    edge_info = {}
    gon_min = {}
    for p in W["paths"]:
        for k, s in enumerate(p["segments"]):
            if s["type"] not in ("walk", "ramp", "stairs", "landing", "bridge", "dam_crest"):
                continue
            n_seg += 1
            A, B = np.array(s["start"], float), np.array(s["end"], float)
            d = B[[0, 2]] - A[[0, 2]]
            Ln = float(np.linalg.norm(d))
            if Ln < 1e-6:
                continue
            u = d / Ln
            for end, sign in ((A, 1), (B, -1)):
                if any(np.hypot(*(np.array(q, float)[[0, 2]] - end[[0, 2]])) < 0.5 for q in F.BOARD_PTS):
                    cut = min(F.BOARDING_TRIM, Ln - 0.5)
                    if sign > 0:
                        A = A + (B - A) * cut / Ln
                    else:
                        B = B - (B - A) * cut / Ln
                    Ln -= cut
            v = np.array([-u[1], u[0]])
            hw = p["width"] / 2
            sx0, sx1 = min(A[0], B[0]) - hw, max(A[0], B[0]) + hw
            sz0, sz1 = min(A[2], B[2]) - hw, max(A[2], B[2]) + hw
            bad = []
            for lab, pc, T, ax0, ax1, az0, az1 in placed:
                if pc in F.FLOOR_KIT or ax0 > sx1 or ax1 < sx0 or az0 > sz1 or az1 < sz0:
                    continue
                rel = T[..., [0, 2]] - A[[0, 2]]
                Pu, Pv = rel @ u, rel @ v
                hit = F.sat_rect(np.stack([Pu, Pv], -1), 0.0, Ln, -hw, hw)
                if not hit.any():
                    continue
                Th = T[hit]
                uu = np.clip(Pu[hit], 0, Ln)
                ya = A[1] + (B[1] - A[1]) * uu.min(1) / Ln
                yb = A[1] + (B[1] - A[1]) * uu.max(1) / Ln
                ylo, yhi = np.minimum(ya, yb), np.maximum(ya, yb)
                tmax, tmin = Th[..., 1].max(1), Th[..., 1].min(1)
                viol = (tmax > yhi + F.TOL) & (tmin < ylo + F.HEAD)
                if pc in EDGE_RAIL_PIECES and viol.any():
                    edge = (np.abs(Pv[hit]).min(1) >= hw - EDGE_BAND) & (tmax <= ylo + EDGE_TOP)
                    sk = viol & edge
                    if sk.any():
                        edge_info.setdefault(f"{p['id']} seg {k}", []).append(f"{lab} {int(sk.sum())} tris")
                    viol = viol & ~edge
                if pc in ("gondola_cable", "gondola_cabin(sweep)"):
                    key = (p["id"], k)
                    gon_min[key] = min(gon_min.get(key, 1e9), float((tmin - ylo).min()))
                if viol.any():
                    bad.append(f"{lab} ({int(viol.sum())} tris, lowest {float((tmin[viol] - ylo[viol]).min()):+.2f})")
                ok = tmin >= ylo + F.HEAD
                if ok.any() and float((tmin[ok] - ylo[ok]).min()) < min_over[0]:
                    min_over = (float((tmin[ok] - ylo[ok]).min()), f"{pc} over {p['id']} seg {k}")
            if bad:
                seg_fail += 1
                log(f"  FAIL {p['id']} seg {k} ({s['type']}): " + "; ".join(bad[:4]))
    fails += seg_fail
    for key, v in edge_info.items():
        log(f"  INFO edge railing skipped on {key}: " + "; ".join(v))
    for (pid, k), v in sorted(gon_min.items()):
        log(f"  INFO gondola (cable + cabin sweep) lowest triangle over {pid} seg {k}: {v:.2f} studs above the walk "
            f"({'PASS' if v >= F.HEAD else 'FAIL'} vs >= {F.HEAD})")
    log(f"  {'PASS' if not seg_fail else 'FAIL'}: {n_seg} walkway segments checked, {seg_fail} with intrusions; lowest "
        f"overhead geometry {min_over[0]:.2f} studs ({min_over[1]})")
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
