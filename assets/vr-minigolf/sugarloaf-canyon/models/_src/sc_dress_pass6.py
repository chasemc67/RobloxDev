"""Sugarloaf Canyon pass 6: per-hole dressing placement (system python + numpy + matplotlib) -> _src/_cache/pass6_layout.json

  python _src/sc_dress_pass6.py          (needs the pass-6 kit pieces built first: _cache/tris/<kit id>.npy)

For every hole (holes.json is the source of truth, world = R_y(world_yaw) * local + world_offset):
  * prop clusters of 3-5 members at the tee and at every turn (route tee -> felt centres in list order -> cup; a turn
    is an interior route point where the direction changes by >= 30 deg), on the outside of the turn;
  * the trading_post_deck beside the H1 tee (west of the lane, front facing the lane);
  * ground dressing: a terrain-hugging red-dirt carpet (two tones, 3-stud jittered grid, +0.2 above the world
    heightfield incl. the Old Sugarloaf dome patch) over the open floor around the hole, stopping 3+ studs short of
    cliffs/steep ground so sand shows at the edges; pebble clumps on it; rounded clay-brick edging outside every rail
    (0.2 from the rail, following the felt outline).
Every member/brick/pebble/carpet triangle is tested with the exported kit triangles against
  - every hole's play volumes (sc_fitcheck_holes.hole_volumes, SAT vs the box grown by 0.15 + SLACK),
  - the lane rules (nothing taller than 2 within 3 studs of a rail; no plants within 1.5 of the rail strip),
  - walkway corridors incl. on_hole approaches (+0.5) and lift/gondola boarding points (4 studs),
  - existing placed kit geometry (sampled points, +0.3), holes.json decoration_anchors (their approx_size),
  - terrain slope / water.
"""
import json, math, os, sys, zlib, time
import numpy as np

SRC = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.dirname(SRC)
COURSE = os.path.dirname(MODELS)
sys.path.insert(0, os.path.join(COURSE, "world", "tools"))
sys.path.insert(0, SRC)
import worldlib as WL                 # noqa: E402
import sc_fitcheck as F               # noqa: E402
import sc_fitcheck_holes as FH        # noqa: E402

W = F.W
HOLES = FH.HOLES
WH = {h["number"]: h for h in W["holes"]}
LAY = json.load(open(os.path.join(MODELS, "layout.json")))
MAN = json.load(open(os.path.join(MODELS, "manifest.json")))
GROUP = {p["id"]: p["group"] for p in MAN["pieces"]}
CACHE = os.path.join(SRC, "_cache")
OUT = os.path.join(CACHE, "pass6_layout.json")
SLACK = 0.1          # extra clearance on top of the 0.15 test for props / carpet
BRICK_SLACK = 0.02
PLANTS = ("lollipop_cactus_cluster", "gumdrop_shrub_a", "gumdrop_shrub_b", "gumdrop_shrub_c")
LOG = []


def log(s):
    LOG.append(s)
    print(s, flush=True)


def Ry(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def hsh(*a):
    return zlib.crc32(("|".join(str(x) for x in a)).encode()) / 2 ** 32


# ----------------------------------------------------------------------------- terrain
def Hgt(X, Z):
    X = np.asarray(X, float)
    Z = np.asarray(Z, float)
    h = WL.height_at(W, X, Z)
    q = np.hypot(X - 80.0, Z + 130.0) / 72.0
    return np.where(q < 1, 18 + 110 * np.sqrt(np.maximum(0, 1 - q ** 4)), h)


def wet(X, Z):
    return ~np.isnan(WL.water_surface(W, np.asarray(X, float), np.asarray(Z, float)))


# ----------------------------------------------------------------------------- play volumes + rails (all holes)
VOLS, VLO, VHI = [], [], []
RAILS = []          # (hole, c, R, hs, felt_y, id)
for h in HOLES:
    for v in FH.hole_volumes(h):
        VOLS.append(v)
        VLO.append(v.wlo)
        VHI.append(v.whi)
    for c, R, hs, rid in FH.rail_boxes(h):
        RAILS.append((h["number"], c, R, hs, c[1] + hs[1] - 1.0, rid))
VLO, VHI = np.array(VLO), np.array(VHI)
RC = np.array([r[1] for r in RAILS])
RR = max(np.linalg.norm(r[3][[0, 2]]) for r in RAILS)


def vol_hit(T, slack=SLACK):
    """True per triangle if it comes within 0.15 + slack of any play volume (conservative SAT on the grown box)."""
    lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)
    m = np.all(VLO <= hi + slack, 1) & np.all(VHI >= lo - slack, 1)
    hit = np.zeros(len(T), bool)
    for i in np.nonzero(m)[0]:
        v = VOLS[i]
        ctr = (v.lo + v.hi) / 2
        hh = (v.hi - v.lo) / 2 + FH.CLR + slack
        Tq = (T - v.c) @ v.Mv.T - ctr
        tl, th = Tq.min(1), Tq.max(1)
        cand = np.all(tl <= hh, 1) & np.all(th >= -hh, 1) & ~hit
        if cand.any():
            hit[np.nonzero(cand)[0][FH.tri_box_sat(Tq[cand], hh)]] = True
    return hit


def lane_bad(T, plant):
    """Fitcheck [C] rules (with 0.1 slack): tall (> 1.9 above the rail's felt level) within 3.1 of a rail, or plant
    geometry within 1.6 of a rail strip."""
    lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)
    near = np.nonzero((RC[:, 0] > lo[0] - RR - 3.2) & (RC[:, 0] < hi[0] + RR + 3.2) & (RC[:, 2] > lo[2] - RR - 3.2)
                      & (RC[:, 2] < hi[2] + RR + 3.2) & (RC[:, 1] > lo[1] - 10) & (RC[:, 1] < hi[1] + 10))[0]
    if not len(near):
        return False
    S = np.concatenate([T, (T + np.roll(T, 1, axis=1)) / 2, T.mean(1, keepdims=True)], 1)
    P = S.reshape(-1, 3)
    for i in near:
        _, c, R, hs, felt_y, _ = RAILS[i]
        d = FH.xz_dist_to_box(P, c, R, hs).reshape(len(T), -1).min(1)
        m = d < 3.1
        if m.any() and (T[m][..., 1].max(1) - felt_y > 1.9).any():
            return True
        if plant and (d < 1.6).any():
            return True
    return False


def lane_bad_tris(T):
    """Per-triangle version of the [C] tall rule (ground pieces: carpet / pebbles / bricks)."""
    bad = np.zeros(len(T), bool)
    lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)
    near = np.nonzero((RC[:, 0] > lo[0] - RR - 3.2) & (RC[:, 0] < hi[0] + RR + 3.2) & (RC[:, 2] > lo[2] - RR - 3.2)
                      & (RC[:, 2] < hi[2] + RR + 3.2) & (RC[:, 1] > lo[1] - 10) & (RC[:, 1] < hi[1] + 10))[0]
    if not len(near):
        return bad
    S = np.concatenate([T, (T + np.roll(T, 1, axis=1)) / 2, T.mean(1, keepdims=True)], 1)
    P = S.reshape(-1, 3)
    top = T[..., 1].max(1)
    for i in near:
        _, c, R, hs, felt_y, _ = RAILS[i]
        d = FH.xz_dist_to_box(P, c, R, hs).reshape(len(T), -1).min(1)
        bad |= (d < 3.1) & (top - felt_y > 1.9)
    return bad


# ----------------------------------------------------------------------------- walkways + boarding points
WALKS = []
for p in W["paths"]:
    for s in p["segments"]:
        if s["type"] in ("walk", "ramp", "stairs", "landing", "bridge", "dam_crest", "on_hole"):
            A, B = np.array(s["start"], float), np.array(s["end"], float)
            d = B[[0, 2]] - A[[0, 2]]
            Ln = float(np.linalg.norm(d))
            if Ln < 1e-6:
                continue
            u = d / Ln
            WALKS.append((A, B, u, np.array([-u[1], u[0]]), Ln, p["width"] / 2, p["id"], s["type"]))
BOARD = np.array([l["bottom"] for l in W["lifts"]] + [l["top"] for l in W["lifts"]], float)


def walk_hit(T, margin=0.5):
    hit = np.zeros(len(T), bool)
    lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)
    for A, B, u, v, Ln, hw, pid, typ in WALKS:
        if min(A[0], B[0]) - hw - 2 > hi[0] or max(A[0], B[0]) + hw + 2 < lo[0] or \
                min(A[2], B[2]) - hw - 2 > hi[2] or max(A[2], B[2]) + hw + 2 < lo[2]:
            continue
        if min(A[1], B[1]) - 3 > hi[1] or max(A[1], B[1]) + 8 < lo[1]:
            continue
        rel = T[..., [0, 2]] - A[[0, 2]]
        hit |= F.sat_rect(np.stack([rel @ u, rel @ v], -1), -margin, Ln + margin, -hw - margin, hw + margin)
    if len(BOARD):
        c = T.mean(1)
        dd = np.hypot(c[:, None, 0] - BOARD[None, :, 0], c[:, None, 2] - BOARD[None, :, 2])
        hit |= ((dd < 4.0) & (np.abs(c[:, None, 1] - BOARD[None, :, 1]) < 10)).any(1)
    return hit


# ----------------------------------------------------------------------------- existing kit geometry (point samples)
SKIP_KIT = ("far_card", "sky", "hole_dressing")
SKIP_IDS = ("gondola_cable", "gondola_cabin", "rim_silhouette")


def sample_tris(T, step=0.6):
    out = [T.reshape(-1, 3), T.mean(1)]
    e = np.linalg.norm(T - np.roll(T, 1, axis=1), axis=-1).max(1)
    n = np.ceil(e / step).astype(int)
    for k in np.unique(n):
        if k <= 1:
            continue
        sel = T[n == k]
        g = np.array([(i / k, j / k) for i in range(k + 1) for j in range(k + 1 - i)])
        a, b = g[:, 0], g[:, 1]
        P = sel[:, None, 0] * (1 - a - b)[None, :, None] + sel[:, None, 1] * a[None, :, None] + sel[:, None, 2] * b[None, :, None]
        out.append(P.reshape(-1, 3))
    return np.concatenate(out)


class Points:
    """Bucketed point cloud (4-stud XZ cells) of existing geometry for cylinder-overlap queries."""

    def __init__(self):
        self.cells = {}

    def add(self, P):
        key = np.floor(P[:, [0, 2]] / 4.0).astype(int)
        order = np.lexsort((key[:, 1], key[:, 0]))
        key, P = key[order], P[order]
        brk = np.nonzero(np.any(np.diff(key, axis=0) != 0, 1))[0] + 1
        for ks, ps in zip(np.split(key, brk), np.split(P, brk)):
            k = (int(ks[0, 0]), int(ks[0, 1]))
            self.cells[k] = np.concatenate([self.cells[k], ps]) if k in self.cells else ps

    def near(self, x, z, r):
        out = []
        for i in range(int(math.floor((x - r) / 4)), int(math.floor((x + r) / 4)) + 1):
            for j in range(int(math.floor((z - r) / 4)), int(math.floor((z + r) / 4)) + 1):
                if (i, j) in self.cells:
                    out.append(self.cells[(i, j)])
        return np.concatenate(out) if out else np.zeros((0, 3))

    def hits_box(self, lo, hi, pad=0.3):
        P = self.near((lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2, max(hi[0] - lo[0], hi[2] - lo[2]) / 2 + pad + 1)
        if not len(P):
            return False
        return bool(np.all((P >= lo - pad) & (P <= hi + pad), 1).any())

    def hits_tris(self, T, pad=0.3):
        """Any existing point within pad of a triangle's XZ AABB and the member's y band (per-triangle AABB test)."""
        lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)
        P = self.near((lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2, max(hi[0] - lo[0], hi[2] - lo[2]) / 2 + pad + 1)
        if not len(P):
            return False
        P = P[np.all((P >= lo - pad) & (P <= hi + pad), 1)]
        if not len(P):
            return False
        tl, th = T.min(1) - pad, T.max(1) + pad
        for q in np.array_split(P, max(1, len(P) // 2000)):
            if (np.all(q[None, :, :] >= tl[:, None, :], 2) & np.all(q[None, :, :] <= th[:, None, :], 2)).any():
                return True
        return False


EXIST = Points()


def load_existing():
    n = 0
    for inst in LAY["instances"]:
        pc = inst["piece"]
        if GROUP.get(pc) in SKIP_KIT or pc in SKIP_IDS or pc.startswith(("cliff_", "slot_")):
            continue
        T = F.place(inst)
        EXIST.add(sample_tris(T))
        n += 1
    # cliff panels: their reworked pass-6 geometry stays inside the pass-5 panel envelope, so the envelope box
    # (local x +-12.5, z -2.6..8.5, full height) is used -> dressing never depends on the cliff rebuild order
    for inst in LAY["instances"]:
        pc = inst["piece"]
        if not pc.startswith(("cliff_", "slot_")):
            continue
        h = float(pc.split("_h")[1].split("_")[0])
        R = Ry(inst["yaw"])
        xs, zs, ys = np.arange(-12.5, 12.51, 0.75), np.arange(-2.6, 8.51, 0.75), np.arange(0, h + 0.01, 1.5)
        G = np.array(np.meshgrid(xs, ys, zs, indexing="ij")).reshape(3, -1).T
        surf = (np.isclose(G[:, 0], -12.5) | np.isclose(G[:, 0], xs[-1]) | np.isclose(G[:, 2], -2.6) | (G[:, 1] == 0))
        P = G[surf] @ R.T + np.array(inst["pos"])
        EXIST.add(P)
        n += 1
    log(f"existing kit sampled: {n} instances (cliff panels by their pass-5 envelope)")


# ----------------------------------------------------------------------------- decoration anchors (holes.json)
# keep-outs: the anchor's occluder boxes if it has any, else its approx_size footprint rectangle (hole frame), + 0.5.
# Region-describing anchors (footprint > 600 sq studs, e.g. dam_view, slot_walls, the sugar dune face, the hour-stone
# ring) are not keep-outs: their real geometry is play volumes (tested exactly) or existing kit pieces (tested).
ANCH, ANCH_SKIPPED = [], []
for h in HOLES:
    off, Rh = np.array(h["world_offset"], float), Ry(h["world_yaw"])
    for a in h.get("decoration_anchors", []):
        if a["name"] == "cup_flag":
            continue
        boxes = [(o["center"], o["size"], o.get("yaw", 0.0)) for o in a.get("occluders") or []]
        if not boxes:
            sz = a.get("approx_size") or [2, 2, 2]
            sx, sz_ = sz[0], sz[2] if len(sz) > 2 else sz[0]
            if sx * sz_ > 600:
                ANCH_SKIPPED.append(f"H{h['number']}:{a['name']} {sx}x{sz_}")
                continue
            boxes = [(a["position"], [sx, sz[1] if len(sz) > 1 else 2, sz_], 0.0)]
        for c, size, yw in boxes:
            p = off + Rh @ np.array(c, float)
            ang = math.radians(h["world_yaw"] + yw)
            R2 = np.array([[math.cos(ang), math.sin(ang)], [-math.sin(ang), math.cos(ang)]])
            ANCH.append((p, R2, np.array([size[0], size[2]], float) / 2 + 0.5, f"H{h['number']}:{a['name']}"))


def anchor_hit(x, z, y, r):
    for p, R2, hs, _ in ANCH:
        if abs(p[1] - y) > 12 or abs(p[0] - x) > hs.max() + r + 1 or abs(p[2] - z) > hs.max() + r + 1:
            continue
        q = (np.array([x, z]) - p[[0, 2]]) @ R2
        if math.hypot(max(abs(q[0]) - hs[0], 0), max(abs(q[1]) - hs[1], 0)) < r:
            return True
    return False


# ----------------------------------------------------------------------------- kit geometry
KIT = {}


def kit(kind):
    if kind not in KIT:
        T = np.load(os.path.join(CACHE, "tris", kind + ".npy")).astype(np.float64)
        r = float(np.hypot(T[..., 0], T[..., 2]).max())
        KIT[kind] = (T, r, float(T[..., 1].max()))
    return KIT[kind]


def place_kit(kind, pos, yaw, s=1.0):
    T, r, h = kit(kind)
    return (T * s) @ Ry(yaw).T + np.asarray(pos, float)


# ----------------------------------------------------------------------------- member validity
PLACED = []          # (x, z, r, hole) of accepted members / trading post


def member_ok(kind, x, z, yaw, s, hole_y, why=None):
    T0, r0, h0 = kit(kind)
    r = r0 * s
    ring = [(x + math.cos(a) * r * 0.75, z + math.sin(a) * r * 0.75) for a in np.linspace(0, math.tau, 8, endpoint=False)]
    X = np.array([x] + [p[0] for p in ring])
    Z = np.array([z] + [p[1] for p in ring])
    hs = Hgt(X, Z)
    flat = 0.45 if kind.startswith(("barrel", "lantern")) else 0.9
    if hs.max() - hs.min() > flat:
        return None, "slope"
    if abs(hs[0] - hole_y) > 8:
        return None, "level"
    if wet(X, Z).any() or wet([x], [z + r + 1]).any() or wet([x], [z - r - 1]).any():
        return None, "water"
    y = float(hs.min()) - 0.05
    for (px, pz, pr, _) in PLACED:
        if math.hypot(px - x, pz - z) < 0.8 * (pr + r):
            return None, "member"
    if anchor_hit(x, z, y, r * 0.85):
        return None, "anchor"
    T = place_kit(kind, (x, y, z), yaw, s)
    if EXIST.hits_tris(T, 0.3):
        return None, "kit"
    if walk_hit(T).any():
        return None, "walk"
    if lane_bad(T, kind in PLANTS):
        return None, "lane"
    if vol_hit(T).any():
        return None, "volume"
    return (x, y, z, r), "ok"


# ----------------------------------------------------------------------------- hole geometry helpers
def hole_world(h, p):
    return np.array(h["world_offset"], float) + Ry(h["world_yaw"]) @ np.array(p, float)


def felt_rects(h):
    """[(centre xz, R2 (2x2 world<-local), half sizes)] of every felt piece in world XZ."""
    out = []
    for f in h["felt"]:
        c = hole_world(h, f["center"])
        a = math.radians(h["world_yaw"] + f.get("yaw", 0.0))
        R2 = np.array([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]])
        out.append((c[[0, 2]], R2, np.array(f["size"], float) / 2, c[1]))
    return out


def felt_dist(rects, X, Z):
    P = np.stack([np.asarray(X, float), np.asarray(Z, float)], -1)
    best = np.full(P.shape[:-1], np.inf)
    for c, R2, hs, _ in rects:
        q = (P - c) @ R2           # world -> local (R2 orthonormal: local = R2^T (p - c) -> (p - c) @ R2)
        d = np.hypot(np.maximum(np.abs(q[..., 0]) - hs[0], 0), np.maximum(np.abs(q[..., 1]) - hs[1], 0))
        best = np.minimum(best, d)
    return best


def route(h):
    pts = [hole_world(h, h["tee"]["position"])] + [hole_world(h, f["center"]) for f in h["felt"]] + \
          [hole_world(h, h["cup"]["position"])]
    out = [pts[0]]
    for p in pts[1:]:
        if np.hypot(*(p - out[-1])[[0, 2]]) > 2.0:
            out.append(p)
    return out


def turns(h):
    pts = route(h)
    out = []
    for i in range(1, len(pts) - 1):
        a = (pts[i] - pts[i - 1])[[0, 2]]
        b = (pts[i + 1] - pts[i])[[0, 2]]
        a /= np.linalg.norm(a)
        b /= np.linalg.norm(b)
        ang = math.degrees(math.acos(max(-1, min(1, float(a @ b)))))
        if ang >= 30:
            outer = a - b
            if np.linalg.norm(outer) < 1e-6:
                outer = np.array([-a[1], a[0]])
            outer /= np.linalg.norm(outer)
            if all(np.hypot(*(pts[i] - q)[[0, 2]]) > 8 for q, _, _ in out):
                out.append((pts[i], outer, round(ang)))
    return out


ZONE_POOL = {
    "Sugarloaf Junction": dict(tee=["barrel_b", "barrel_a", "lantern_post", "gumdrop_shrub_a", "rock_candy_cluster"],
                               turn=["lollipop_cactus_cluster", "gumdrop_shrub_c", "boulder_scatter", "fallen_rock_scatter",
                                     "rock_candy_cluster"]),
    "Rock Candy Narrows": dict(tee=["lantern_post", "rock_candy_cluster", "barrel_a", "fallen_rock_scatter"],
                               turn=["rock_candy_cluster", "fallen_rock_scatter", "boulder_scatter", "rock_candy_cluster",
                                     "gumdrop_shrub_c"]),
    "Taffy Mesa": dict(tee=["barrel_b", "lantern_post", "gumdrop_shrub_b", "gumdrop_shrub_a"],
                       turn=["gumdrop_shrub_a", "lollipop_cactus_cluster", "gumdrop_shrub_c", "boulder_scatter",
                             "fallen_rock_scatter"]),
    "Sugarloaf Dam": dict(tee=["lantern_post", "barrel_a", "barrel_b", "fallen_rock_scatter"],
                          turn=["boulder_scatter", "fallen_rock_scatter", "gumdrop_shrub_c", "rock_candy_cluster"]),
    "Hoodoo Garden": dict(tee=["lantern_post", "barrel_a", "gumdrop_shrub_b", "fallen_rock_scatter"],
                          turn=["boulder_scatter", "lollipop_cactus_cluster", "fallen_rock_scatter", "gumdrop_shrub_a",
                                "rock_candy_cluster"]),
    "Sugarloaf Crown": dict(tee=["lantern_post", "barrel_b", "gumdrop_shrub_a", "lollipop_cactus_cluster"],
                            turn=["lollipop_cactus_cluster", "gumdrop_shrub_b", "boulder_scatter", "fallen_rock_scatter"]),
}
# small fallbacks that fit tight spots (low, non-plant) - tried when a pool member does not fit
FALLBACK = ["fallen_rock_scatter", "barrel_a", "gumdrop_shrub_c", "rock_candy_cluster"]


def place_cluster(h, anchor, outer, kinds, tag, hole_y, avoid=None, dmin=2.5, dmax=22.0):
    """Try cluster centres outward from the anchor; first centre that holds >= 3 members wins (max 5)."""
    seed = hsh(h["id"], tag)
    angs = [0, 25, -25, 50, -50, 75, -75, 100, -100, 130, -130, 160, -160, 180]
    tried = 0
    best = None
    for dist in np.arange(dmin, dmax + 0.01, 1.0):
        for a in angs:
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            d = np.array([outer[0] * ca - outer[1] * sa, outer[0] * sa + outer[1] * ca])
            cx, cz = anchor[0] + d[0] * dist, anchor[2] + d[1] * dist
            if avoid is not None and avoid(cx, cz):
                continue
            tried += 1
            got = []
            snapshot = len(PLACED)
            for k, kind in enumerate(kinds):
                options = [kind] + [f for f in FALLBACK if f != kind] if k >= 2 else [kind]
                done = False
                for kd in options:
                    T0, r0, _ = kit(kd)
                    s = 0.9 + 0.25 * hsh(seed, k, kd)
                    yaw = 360 * hsh(seed, "yaw", k)
                    rings = [(0.0, 0.0)] if not got else [
                        (math.cos(t) * rr, math.sin(t) * rr)
                        for rr in (got[0][3] + r0 * s + 0.4, got[0][3] + r0 * s + 1.6)
                        for t in np.linspace(0, math.tau, 10, endpoint=False) + seed * 6]
                    for ox, oz in rings:
                        res, why = member_ok(kd, cx + ox, cz + oz, yaw, s, hole_y)
                        if res:
                            x, y, z, r = res
                            got.append((kd, (x, y, z), yaw, r, s))
                            PLACED.append((x, z, r, h["number"]))
                            done = True
                            break
                    if done:
                        break
                if not got:
                    break
            if len(got) >= 3:
                return [dict(kind=kd, pos=[round(v, 3) for v in p], yaw=round(yaw, 1), scale=round(s, 3), anchor=tag)
                        for kd, p, yaw, r, s in got], (round(cx, 2), round(cz, 2)), tried
            del PLACED[snapshot:]
            if got and (best is None or len(got) > best[0]):
                best = (len(got), (cx, cz))
    return [], best, tried


# ----------------------------------------------------------------------------- trading post (H1)
TP = dict(pos=[47.5, None, 469.0], yaw=-90.0)


def trading_post(h):
    x, z = TP["pos"][0], TP["pos"][2]
    T0, r0, _ = kit("trading_post_deck")
    Tl = T0 @ Ry(TP["yaw"]).T
    xs = np.linspace(Tl[..., 0].min(), Tl[..., 0].max(), 7) + x
    zs = np.linspace(Tl[..., 2].min(), Tl[..., 2].max(), 9) + z
    X, Z = np.meshgrid(xs, zs)
    y = float(Hgt(X, Z).min()) - 0.02
    T = Tl + np.array([x, y, z])
    checks = dict(volume=int(vol_hit(T, 0.05).sum()), lane=bool(lane_bad(T, False)), walk=int(walk_hit(T, 0.3).sum()),
                  kit=bool(EXIST.hits_tris(T, 0.2)))
    ok = checks["volume"] == 0 and not checks["lane"] and checks["walk"] == 0 and not checks["kit"]
    log(f"  trading_post_deck at ({x}, {y:.2f}, {z}) yaw {TP['yaw']}: {'OK' if ok else 'BLOCKED'} {checks}")
    if not ok:
        raise SystemExit("trading post placement blocked")
    EXIST.add(sample_tris(T))
    PLACED.append((x, z, 6.0, 1))
    lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)
    return dict(piece="trading_post_deck", pos=[x, round(y, 3), z], yaw=TP["yaw"],
                world_bbox=[[round(v, 2) for v in lo], [round(v, 2) for v in hi]], checks=checks)


# ----------------------------------------------------------------------------- ground: carpet, pebbles, bricks
CELL = 3.0


def carpet(h, owner_of, region_y):
    """Two-tone red-dirt carpet cells for hole h. owner_of(X, Z) -> hole number owning each point (Voronoi)."""
    b = WH[h["number"]]["footprint_bbox"]
    ext = 30.0
    x0, x1 = math.floor((b["x"][0] - ext) / CELL) * CELL, math.ceil((b["x"][1] + ext) / CELL) * CELL
    z0, z1 = math.floor((b["z"][0] - ext) / CELL) * CELL, math.ceil((b["z"][1] + ext) / CELL) * CELL
    gx, gz = np.arange(x0, x1 + 0.01, CELL), np.arange(z0, z1 + 0.01, CELL)
    nx, nz = len(gx), len(gz)
    GX, GZ = np.meshgrid(gx, gz, indexing="ij")
    jx = np.array([[hsh("jx", i, j) for j in range(nz)] for i in range(nx)]) - 0.5
    jz = np.array([[hsh("jz", i, j) for j in range(nz)] for i in range(nx)]) - 0.5
    VX, VZ = GX + jx * 1.3, GZ + jz * 1.3
    VY = Hgt(VX, VZ) + 0.2
    VW = wet(VX, VZ)
    # cells
    cx, cz = (GX[:-1, :-1] + GX[1:, 1:]) / 2, (GZ[:-1, :-1] + GZ[1:, 1:]) / 2
    corners = np.stack([VY[:-1, :-1], VY[1:, :-1], VY[1:, 1:], VY[:-1, 1:]], -1)
    rng_y = corners.max(-1) - corners.min(-1)
    steep = rng_y > 1.4
    # stay 1 cell (3 studs) off steep ground so a sand band shows at the cliff feet
    st = steep.copy()
    st[1:, :] |= steep[:-1, :]
    st[:-1, :] |= steep[1:, :]
    st[:, 1:] |= steep[:, :-1]
    st[:, :-1] |= steep[:, 1:]
    lvl = (corners.min(-1) > region_y[0] - 0.5) & (corners.max(-1) < region_y[1] + 0.5)
    own = owner_of(cx, cz) == h["number"]
    wetc = VW[:-1, :-1] | VW[1:, :-1] | VW[1:, 1:] | VW[:-1, 1:]
    rects = felt_rects(h)
    df = felt_dist(rects, cx, cz)
    # ragged outer edge: full cover to 16 studs from the felt, then thinning by noise to the 30-stud region edge
    nse = np.array([[hsh("cov", i, j) for j in range(nz - 1)] for i in range(nx - 1)])
    blob = np.sin(cx * 0.11 + 1.3) * np.cos(cz * 0.09 - 0.4) * 0.5 + 0.5
    keep = own & lvl & ~st & ~wetc & ((df < 16) | (nse * 0.6 + blob * 0.4 > (df - 16) / 14))
    keep &= df > 0.9
    tone = (np.sin(cx * 0.21) + np.cos(cz * 0.17 + cx * 0.05) + 0.6 * (nse - 0.5)) > 0.15
    return dict(VX=VX, VZ=VZ, VY=VY, keep=keep, tone=tone, nx=nx, nz=nz)


def carpet_tris(C, cells):
    VX, VZ, VY = C["VX"], C["VZ"], C["VY"]
    i, j = cells[:, 0], cells[:, 1]
    p = lambda a, b: np.stack([VX[a, b], VY[a, b], VZ[a, b]], -1)
    v00, v10, v11, v01 = p(i, j), p(i + 1, j), p(i + 1, j + 1), p(i, j + 1)
    return np.stack([np.stack([v00, v01, v11], 1), np.stack([v00, v11, v10], 1)], 1)     # (n, 2, 3, 3)


def ground(h, owner_of, region_y):
    C = carpet(h, owner_of, region_y)
    cells = np.argwhere(C["keep"])
    T = carpet_tris(C, cells)
    flat = T.reshape(-1, 3, 3)
    bad = (vol_hit(flat) | walk_hit(flat, 0.3) | lane_bad_tris(flat)).reshape(-1, 2).any(1)
    # existing ground-level kit (boardwalks, buildings, cliff feet): drop cells that touch it
    kb = np.array([EXIST.hits_box(t.reshape(-1, 3).min(0) - [0, 0.6, 0], t.reshape(-1, 3).max(0) + [0, 1.0, 0], 0.1)
                   for t in T])
    keep = ~bad & ~kb
    # failed cells: split into 4 bilinear sub-cells (outer edges stay collinear with the neighbours) and keep the
    # sub-cells that pass, so the dirt reaches closer to rails / walkways / kit
    sub_T, sub_tone = [], []
    for (i, j), ok in zip(cells, keep):
        if ok:
            continue
        P = np.array([[C["VX"][a, b], C["VY"][a, b], C["VZ"][a, b]] for a, b in ((i, j), (i + 1, j), (i + 1, j + 1),
                                                                                  (i, j + 1))])
        bil = lambda u, v: P[0] * (1 - u) * (1 - v) + P[1] * u * (1 - v) + P[2] * u * v + P[3] * (1 - u) * v
        for u0 in (0.0, 0.5):
            for v0 in (0.0, 0.5):
                q00, q10, q11, q01 = bil(u0, v0), bil(u0 + .5, v0), bil(u0 + .5, v0 + .5), bil(u0, v0 + .5)
                t = np.array([[q00, q01, q11], [q00, q11, q10]])
                if vol_hit(t).any() or walk_hit(t, 0.3).any() or lane_bad_tris(t).any():
                    continue
                if EXIST.hits_box(t.reshape(-1, 3).min(0) - [0, 0.6, 0], t.reshape(-1, 3).max(0) + [0, 1.0, 0], 0.1):
                    continue
                sub_T.append(t)
                sub_tone.append(bool(C["tone"][i, j]))
    tone_all = C["tone"][cells[:, 0], cells[:, 1]]
    cells, T, tone = cells[keep], T[keep], tone_all[keep]
    if sub_T:
        T = np.concatenate([T, np.array(sub_T)])
        tone = np.concatenate([tone, np.array(sub_tone)])
    meshes = {}
    for mat, sel in (("RedDirt", tone), ("RedDirtLight", ~tone)):
        if not sel.any():
            continue
        tri = T[sel].reshape(-1, 3, 3)
        verts, idx = np.unique(np.round(tri.reshape(-1, 3), 4), axis=0, return_inverse=True)
        meshes[mat] = dict(verts=verts.round(3).tolist(), faces=idx.reshape(-1, 3).tolist())
    stats = dict(cells_region=int(C["keep"].size), cells_candidate=int(C["keep"].sum()), cells_kept=int(len(cells)),
                 subcells_kept=len(sub_T), dropped_volume_or_walk=int(bad.sum()), dropped_kit=int((kb & ~bad).sum()),
                 tris=int(len(T) * 2))
    return meshes, cells, C, stats


def pebble_tris(pos, yaw, r):
    v = np.array([(r, 0, 0.0), (0, r * 0.8, 0.0), (-r * 0.9, 0, 0.0), (0, -r * 0.85, 0.0), (0, 0, r * 0.7), (0, 0, -r * 0.3)])
    f = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (1, 0, 5), (2, 1, 5), (3, 2, 5), (0, 3, 5)]
    rb = np.stack([v[:, 0], v[:, 2], -v[:, 1]], -1)            # Blender -> Roblox local
    return rb[np.array(f)] @ Ry(yaw).T + np.asarray(pos, float)


def pebbles(h, cells, C, n_groups):
    out = []
    if not len(cells):
        return out
    for g in range(n_groups * 3):
        if len(out) >= n_groups * 5:
            break
        c = cells[int(hsh(h["id"], "pg", g) * len(cells))]
        gx = (C["VX"][c[0], c[1]] + C["VX"][c[0] + 1, c[1] + 1]) / 2
        gz = (C["VZ"][c[0], c[1]] + C["VZ"][c[0] + 1, c[1] + 1]) / 2
        grp = []
        for k in range(3 + int(hsh(h["id"], "pn", g) * 4)):
            a, d = hsh(g, k, "a") * math.tau, 1.2 * math.sqrt(hsh(g, k, "d"))
            x, z = gx + math.cos(a) * d, gz + math.sin(a) * d
            r = 0.12 + 0.2 * hsh(g, k, "r")
            y = float(Hgt([x], [z])[0]) + 0.17
            yaw = 360 * hsh(g, k, "y")
            T = pebble_tris((x, y, z), yaw, r)
            if vol_hit(T).any() or walk_hit(T, 0.3).any() or lane_bad_tris(T).any() or EXIST.hits_tris(T, 0.15):
                continue
            grp.append(dict(pos=[round(x, 3), round(y, 3), round(z, 3)], yaw=round(yaw, 1), r=round(r, 3),
                            mat="Pebble" if k % 3 else "Strata"))
        out += grp
    return out


def brick_tris(pos, yaw, length, w=0.7, hgt=0.45):
    hw = w / 2
    prof = [(-hw, 0.0), (hw, 0.0), (hw, hgt * 0.62), (hw * 0.55, hgt), (-hw * 0.55, hgt), (-hw, hgt * 0.62)]
    # Blender loft along local Y; Roblox local: x = x, y = z_blender (profile height), z = -y_blender
    a = np.array([(x, zz, length / 2) for x, zz in prof])
    b = np.array([(x, zz, -length / 2) for x, zz in prof])
    tris = []
    n = len(prof)
    for k in range(n):
        tris += [(a[k], a[(k + 1) % n], b[(k + 1) % n]), (a[k], b[(k + 1) % n], b[k])]
    for cap in (a, b):
        for k in range(1, n - 1):
            tris.append((cap[0], cap[k], cap[k + 1]))
    return np.array(tris) @ Ry(yaw).T + np.asarray(pos, float)


def bricks(h):
    rects = felt_rects(h)
    out, centres = [], []
    skipped = dict(no_side=0, level=0, volume=0, walk=0, kit=0, overlap=0)
    for c, R, hs, rid in FH.rail_boxes(h):
        wyaw = h["world_yaw"] + next(w.get("yaw", 0.0) for w in h["walls"] if w["id"] == rid)
        side = []
        for sgn in (-1, 1):
            p = c + R @ np.array([sgn * (hs[0] + 0.6), 0, 0])
            side.append(felt_dist(rects, [p[0]], [p[2]])[0] < 0.05)
        if side[0] == side[1]:
            skipped["no_side"] += 1
            continue
        sgn = 1 if side[0] else -1             # felt on -x -> bricks on +x
        n = max(1, int(round(2 * hs[2] / 1.3)))
        L_ = 2 * hs[2] / n
        for k in range(n):
            lz = -hs[2] + L_ * (k + 0.5)
            p = c + R @ np.array([sgn * (hs[0] + 0.2 + 0.35), 0, lz])
            if any(math.hypot(p[0] - q[0], p[2] - q[2]) < 0.75 for q in centres):
                skipped["overlap"] += 1
                continue
            g = float(Hgt([p[0]], [p[2]])[0])
            rail_base = c[1] - hs[1]
            if abs(g - (rail_base + 0.5)) > 1.2:
                skipped["level"] += 1
                continue
            pos = (p[0], g - 0.08, p[2])
            T = brick_tris(pos, wyaw, L_ - 0.1)
            if vol_hit(T, BRICK_SLACK).any():
                skipped["volume"] += 1
                continue
            if lane_bad_tris(T).any():
                skipped["level"] += 1
                continue
            if walk_hit(T, 0.2).any():
                skipped["walk"] += 1
                continue
            if EXIST.hits_tris(T, 0.1):
                skipped["kit"] += 1
                continue
            centres.append(p)
            out.append(dict(pos=[round(v, 3) for v in pos], yaw=round(wyaw, 2), len=round(L_ - 0.1, 3), rail=rid))
    return out, skipped


# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    log(f"Pass 6 dressing placement ({time.strftime('%Y-%m-%d %H:%M')}): {len(VOLS)} play volumes, {len(RAILS)} rails, "
        f"{len(WALKS)} walkway segments, {len(ANCH)} decoration-anchor keep-out boxes (region anchors not used as "
        f"keep-outs: {ANCH_SKIPPED})")
    load_existing()
    # Voronoi ownership for the ground carpet (distance to each hole's felt)
    allrects = {h["number"]: felt_rects(h) for h in HOLES}

    def owner_of(X, Z):
        D = np.stack([felt_dist(allrects[n], X, Z) for n in sorted(allrects)], 0)
        return np.array(sorted(allrects))[np.argmin(D, 0)]
    res = dict(generated=time.strftime("%Y-%m-%d %H:%M"), rules=dict(
        clearance=f"0.15 + {SLACK} (props, carpet, pebbles) / 0.15 + {BRICK_SLACK} (bricks) vs every hole's play volumes",
        lane="nothing > 2 above the felt within 3 of a rail; plants >= 1.5 from the rail strip (placed with 0.1 slack)",
        walkways="walk/ramp/stairs/landing/bridge/dam_crest/on_hole corridors + 0.5 (props) / 0.3 (ground) / 0.2 (bricks); "
                 "boarding points 4", kit="existing placed geometry + 0.3", anchors="holes.json decoration_anchors "
                 "approx_size/2 + 0.5"), holes={})
    for h in HOLES:
        hid = h["id"]
        n = h["number"]
        piv = [round(v, 3) for v in hole_world(h, h["tee"]["position"])]
        fys = [hole_world(h, f["center"])[1] for f in h["felt"]]
        region_y = (min(fys) - 6, max(fys) + 4)
        log(f"H{n} {h['name']} ({h['zone']}): pivot {piv}")
        members = []
        if n == 1:
            res["trading_post"] = trading_post(h)
        pool = ZONE_POOL[h["zone"]]
        tee = hole_world(h, h["tee"]["position"])
        aim = Ry(h["world_yaw"]) @ np.array([h["tee"]["aim_hint"][0], 0, h["tee"]["aim_hint"][1]], float)
        aim2 = aim[[0, 2]] / np.linalg.norm(aim[[0, 2]])
        side = np.array([-aim2[1], aim2[0]])
        clusters = []
        # tee: try the side away from the arriving walkway first, then the other side, then behind-diagonals
        kinds = [pool["tee"][(i + n) % len(pool["tee"])] for i in range(5)]
        best = None
        for k, d in enumerate((side, -side, (side - aim2) / math.sqrt(2), (-side - aim2) / math.sqrt(2))):
            mem, info, tried = place_cluster(h, tee, d, kinds, f"tee{k}", tee[1],
                                             avoid=lambda x, z: math.hypot(x - tee[0], z - tee[2]) < 4.5, dmin=4.5)
            if mem:
                clusters.append(dict(anchor="tee", centre=info, members=len(mem), tried=tried))
                members += mem
                break
        else:
            clusters.append(dict(anchor="tee", centre=None, members=0, note=f"no spot with >= 3 members (best {best})"))
        for k, (p, outer, ang) in enumerate(turns(h)):
            kinds = [pool["turn"][(i + n + k) % len(pool["turn"])] for i in range(4 + (k + n) % 2)]
            mem, info, tried = place_cluster(h, p, outer, kinds, f"turn{k}", p[1])
            clusters.append(dict(anchor=f"turn{k} ({ang} deg at {[round(float(v), 1) for v in p]})",
                                 centre=info if mem else None, members=len(mem), tried=tried,
                                 **({} if mem else {"note": f"no spot with >= 3 members (best {info})"})))
            members += mem
        for c in clusters:
            log(f"   cluster {c['anchor']}: {c['members']} members" + (f" at {c['centre']}" if c.get("centre") else
                                                                     f"  [{c.get('note')}]"))
        meshes, cells, C, gstats = ground(h, owner_of, region_y)
        peb = pebbles(h, cells, C, 30)
        brk, bskip = bricks(h)
        log(f"   ground: carpet {gstats['cells_kept']} cells + {gstats['subcells_kept']} sub-cells ({gstats['tris']} tris), "
            f"{len(peb)} pebbles, {len(brk)} bricks "
            f"(skipped {bskip})")
        counts = dict(props=sum(1 for m in members if m["kind"] not in PLANTS),
                      plants=sum(1 for m in members if m["kind"] in PLANTS),
                      ground=len(peb) + len(brk) + gstats["cells_kept"])
        res["holes"][hid] = dict(number=n, name=h["name"], zone=h["zone"], pivot=piv, members=members, clusters=clusters,
                                 ground=dict(meshes=meshes, bricks=brk, pebbles=peb, stats=gstats, brick_skips=bskip),
                                 counts=counts)
    json.dump(res, open(OUT, "w"), separators=(",", ":"))
    open(os.path.join(CACHE, "p6", "dress_log.txt"), "w").write("\n".join(LOG) + "\n")
    log(f"wrote {OUT} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
