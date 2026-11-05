"""Dressing keep-out volumes + preview ground heights, built from ../holes.json (source of truth) and the hero
placements in manifest.json. Pure numpy (used by dressing.py, fitcheck.py and assembly.py inside Blender).

Coordinates: Roblox axes (x, y up, z), WORLD frame (world = R_y(world_yaw) * local + world_offset), so dressing of
one hole is also checked against every neighbouring hole.

A dressing vertex is a violation when it is inside any keep-out volume:
  felt      felt footprint grown by FELT_MARGIN (covers the 0.5 rails + 0.75 walk-by gap), below felt top + CLEAR
  wall      collision wall footprint grown by WALL_MARGIN, below wall top + CLEAR - 1.5 (tall bank walls)
  hazard    water / pit footprint grown by 0.3, below surface + CLEAR
  sweep     every moving part's blockers AND its visual mesh bbox, swept through its full motion, grown by 0.5
  teleport  entry / exit radius + 0.8, from 1 below to 3 above
  hero      oriented bbox (+0.3) of every placed hero prop (trees: trunk column only); hollow_tree: trunk wall
            annulus (cavity x0.96 .. outer x1.22) at any height; inside its cavity only props <= 4.5 tall
  path      walking corridor cup(N) -> tee(N+1), 2.5 half-width, and a 3.5-radius tee pad + 8-stud run-up behind
            each tee, below path height + CLEAR
CLEAR = 6.5 studs: things may hang over felt/paths only if they stay higher than that (lantern spans, tree canopies).
"""
import json, math, os
import numpy as np

SRC = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.dirname(SRC)
COURSE = os.path.dirname(MODELS)

CLEAR = 6.5
FELT_MARGIN = 1.25
WALL_MARGIN = 0.4
GROUND_DROP = 0.6          # preview ground sits this far below the nearest felt top
TREE_ORIGIN_LOCAL = (23.0, -1.0, -36.0)   # hollow_tree placement in H9 (props_hero.TREE_ORIGIN)
TREE_CAV = (11.5, 20.5, 6.0)
TREE_OUT = (15.6, 23.2, 2.5)


def load_holes():
    # pass 8: LG_HOLES_JSON = an alternative holes.json (e.g. a design-round snapshot) for validation runs
    return json.load(open(os.environ.get("LG_HOLES_JSON") or os.path.join(COURSE, "holes.json")))["holes"]


def yaw_mat(yaw_deg):
    """3x3 Roblox rotation about +Y (x' = x cos + z sin; z' = -x sin + z cos)."""
    a = math.radians(yaw_deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float64)


def axis_angle(axis, ang_deg):
    a = math.radians(ang_deg)
    k = np.asarray(axis, float)
    k = k / np.linalg.norm(k)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


def hole_xf(h):
    return yaw_mat(h.get("world_yaw", 0.0)), np.asarray(h["world_offset"], float)


def to_world(h, p_local):
    Rw, off = hole_xf(h)
    return np.asarray(p_local, float) @ Rw.T + off


def instance_matrix(pos, yaw, scale):
    s = np.array([scale] * 3 if np.isscalar(scale) else [scale[0], scale[1], scale[2]], float)
    return yaw_mat(yaw) * s[None, :], np.asarray(pos, float)


def transform_verts(verts, pos, yaw, scale, h=None):
    """Prop-local Roblox verts (N,3) -> hole-local (and world if h given)."""
    Rm, t = instance_matrix(pos, yaw, scale)
    v = verts @ Rm.T + t
    return to_world(h, v) if h is not None else v


# ----------------------------------------------------------------------------- keep-out volumes
class Vol:
    """Oriented box: centre c, rotation Rm (columns = local axes, world), half extents hf.
    kind2d=True ignores y except `ymax` (vertex violates only if y < ymax)."""

    def __init__(self, label, c, Rm, hf, ymax=None, ymin=None):
        self.label, self.c, self.Rm, self.hf = label, np.asarray(c, float), np.asarray(Rm, float), np.asarray(hf, float)
        self.ymax, self.ymin = ymax, ymin
        hx, hz = self.hf[0], self.hf[2]
        if self.hf[1] < 1e5:
            hx, hz = np.linalg.norm(self.hf), np.linalg.norm(self.hf)
        self.cxz, self.rxz = self.c[[0, 2]], float(math.hypot(hx, hz))

    def inside(self, P):
        L = (P - self.c) @ self.Rm
        m = (np.abs(L[:, 0]) < self.hf[0]) & (np.abs(L[:, 1]) < self.hf[1]) & (np.abs(L[:, 2]) < self.hf[2])
        if self.ymax is not None:
            m &= P[:, 1] < self.ymax
        if self.ymin is not None:
            m &= P[:, 1] > self.ymin
        return m


class Capsule2D:
    def __init__(self, label, a, b, r, ymax):
        self.label, self.a, self.b, self.r, self.ymax = label, np.asarray(a, float), np.asarray(b, float), r, ymax
        self.cxz = (self.a[[0, 2]] + self.b[[0, 2]]) / 2
        self.rxz = float(np.linalg.norm(self.a[[0, 2]] - self.b[[0, 2]]) / 2 + r)

    def inside(self, P):
        a, b = self.a[[0, 2]], self.b[[0, 2]]
        q = P[:, [0, 2]]
        ab = b - a
        t = np.clip(((q - a) @ ab) / max(ab @ ab, 1e-9), 0, 1)
        d = np.linalg.norm(q - (a + t[:, None] * ab), axis=1)
        return (d < self.r) & (P[:, 1] < self.ymax)


class TreeAnnulus:
    """hollow_tree trunk wall (world coords); small props allowed inside the cavity, nothing in the wall."""

    def __init__(self, label, origin_w, max_cavity_h=4.5):
        self.label, self.o, self.maxh = label, np.asarray(origin_w, float), max_cavity_h

    @staticmethod
    def S(P, o, rx, rz, n, k):
        u = np.abs((P[:, 0] - o[0]) / (rx * k))
        v = np.abs((P[:, 2] - o[2]) / (rz * k))
        return u ** n + v ** n

    def inside(self, P, prop_height=0.0):
        outer = self.S(P, self.o, TREE_OUT[0], TREE_OUT[1], TREE_OUT[2], 1.22) < 1
        cav = self.S(P, self.o, TREE_CAV[0], TREE_CAV[1], TREE_CAV[2], 0.96) < 1
        m = outer & ~cav
        if prop_height > self.maxh:
            m |= cav
        return m


def felt_top(f):
    return f["center"][1] + abs((f.get("slope") or {}).get("rise", 0.0)) / 2


def _box2d(h, label, c, sx, sz, yaw, grow, ymax):
    Rw, off = hole_xf(h)
    cw = to_world(h, c)
    Rm = Rw @ yaw_mat(yaw)
    return Vol(label, cw, Rm, (sx / 2 + grow, 1e6, sz / 2 + grow), ymax=ymax)


def sweep_vols(h, mp, visual=None):
    """OBBs covering a moving part's blockers (+ visual bbox) through its full motion."""
    out = []
    Rw, off = hole_xf(h)
    piv = np.asarray(mp["pivot"], float)
    boxes = [(np.asarray(b["center"], float), np.asarray(b["size"], float), b.get("yaw", 0.0), b.get("roll", 0.0))
             for b in mp["blockers"]]
    if visual is not None:
        boxes.append((np.asarray(visual[0], float), np.asarray(visual[1], float), 0.0, 0.0))
    if mp["type"] in ("rotate", "swing"):          # pass 6: 'swing' (pendulum) = rotation over [-amp, amp]
        rng = mp.get("range") or ([-mp["amplitude_deg"], mp["amplitude_deg"]] if mp["type"] == "swing" else [0, 360])
        steps = [rng[0] + (rng[1] - rng[0]) * i / 36 for i in range(37)]
    else:
        rng = mp["range"] or [0, 0]
        steps = [rng[0] + (rng[1] - rng[0]) * i / 8 for i in range(9)]
    for st in steps:
        for (c, sz, yaw, roll) in boxes:
            if mp["type"] in ("rotate", "swing"):
                Rr = axis_angle(mp["axis"], st + roll)
                cc = piv + Rr @ c
                Rm = Rr @ yaw_mat(yaw)
            else:
                cc = piv + c + np.asarray(mp["axis"], float) * st
                Rm = yaw_mat(yaw)
            out.append(Vol(f"sweep:{mp['id']}", to_world(h, cc), Rw @ Rm, sz / 2 + 0.5))
    return out


def build_keepouts(holes, manifest_props):
    vols, trees = [], []
    by_motion = {}
    for p in manifest_props:
        mo = p.get("motion")
        if mo and mo.get("holes_json_id"):
            by_motion[(mo.get("hole"), mo["holes_json_id"])] = p
    for h in holes:
        H = f"H{h['number']}"
        for f in h["felt"]:
            vols.append(_box2d(h, f"{H}:felt:{f['id']}", f["center"], f["size"][0], f["size"][1], f.get("yaw", 0),
                               FELT_MARGIN, to_world(h, [0, felt_top(f), 0])[1] + CLEAR))
        for w in h["walls"]:
            top = w["center"][1] + w["size"][1] / 2
            vols.append(_box2d(h, f"{H}:wall:{w['id']}", w["center"], w["size"][0], w["size"][2], w.get("yaw", 0),
                               WALL_MARGIN, to_world(h, [0, top, 0])[1] + CLEAR - 1.5))
        for z in h["hazards"]:
            vols.append(_box2d(h, f"{H}:hazard:{z['id']}", z["center"], z["size"][0], z["size"][1], z.get("yaw", 0),
                               0.3, to_world(h, z["center"])[1] + CLEAR))
        for mp in h["moving_parts"]:
            vis = None
            p = by_motion.get((H, mp["id"]))
            if p:
                vis = (p["bbox_center_from_origin"], p["bbox_size_studs"])
            vols += sweep_vols(h, mp, vis)
        for t in h["teleports"]:
            for nm, c, r in (("entry", t["entry"]["center"], t["entry"]["radius"]), ("exit", t["exit"]["center"], 0.6)):
                cw = to_world(h, c)
                vols.append(Vol(f"{H}:teleport:{t['id']}:{nm}", cw, np.eye(3), (r + 0.8, 2.0, r + 0.8), ymin=cw[1] - 1))
        # tee pad + run-up behind the tee
        tee = np.asarray(h["tee"]["position"], float)
        aim = np.array([h["tee"]["aim_hint"][0], 0, h["tee"]["aim_hint"][1]], float)
        vols.append(Capsule2D(f"{H}:tee_pad", to_world(h, tee), to_world(h, tee - aim * 8), 3.5,
                              to_world(h, tee)[1] + CLEAR))
    # walking corridors cup(N) -> tee(N+1)
    for a, b in zip(holes, holes[1:]):
        pa = to_world(a, a["cup"]["position"])
        pb = to_world(b, b["tee"]["position"])
        vols.append(Capsule2D(f"path:H{a['number']}->H{b['number']}", pa, pb, 2.5, max(pa[1], pb[1]) + CLEAR))
    # hero props (manifest placements)
    hmap = {f"H{h['number']}": h for h in holes}
    for p in manifest_props:
        if p.get("group") == "dressing":
            continue
        for pl in p.get("placements", []):
            h = hmap.get(pl["hole"])
            if h is None:
                continue
            if p["name"] == "hollow_tree":
                trees.append(TreeAnnulus(f"{pl['hole']}:hero:hollow_tree", to_world(h, pl["pos"])))
                continue
            if p["name"] in ("water_surface",):
                continue
            s = pl.get("scale", 1.0)
            if pl.get("scale_z_to"):
                s = [1, 1, pl["scale_z_to"] / max(p["bbox_size_studs"][2], 1e-6)]
            S = np.array([s] * 3 if np.isscalar(s) else s, float)
            c = np.asarray(p["bbox_center_from_origin"], float) * S
            hf = np.asarray(p["bbox_size_studs"], float) * S / 2 + 0.3
            if "tree" in p["name"]:
                c = np.array([0, 4.0, 0]) * S
                hf = np.array([1.4, 4.0, 1.4]) * S
            Rw, off = hole_xf(h)
            Rm = Rw @ yaw_mat(pl.get("yaw", 0))
            cw = to_world(h, np.asarray(pl["pos"], float) + yaw_mat(pl.get("yaw", 0)) @ c)
            vols.append(Vol(f"{pl['hole']}:hero:{p['name']}", cw, Rm, hf))
    return vols, trees


def violations(P, vols, trees, prop_height=0.0, first_only=False):
    """P: (N,3) world verts. Returns {label: count}. Volumes whose xz bounding circle misses P's are skipped."""
    out = {}
    cxz = (P[:, [0, 2]].min(0) + P[:, [0, 2]].max(0)) / 2
    rxz = float(np.linalg.norm(P[:, [0, 2]].max(0) - P[:, [0, 2]].min(0)) / 2)
    for v in vols:
        if np.linalg.norm(v.cxz - cxz) > v.rxz + rxz + 0.01:
            continue
        n = int(v.inside(P).sum())
        if n:
            out[v.label] = n
            if first_only:
                return out
    for t in trees:
        n = int(t.inside(P, prop_height).sum())
        if n:
            out[t.label] = n
            if first_only:
                return out
    return out


# ----------------------------------------------------------------------------- distances / ground
def felt_rects(h):
    """[(cx, cz, hx, hz, yaw_deg, top_y)] hole-local."""
    return [(f["center"][0], f["center"][2], f["size"][0] / 2, f["size"][1] / 2, f.get("yaw", 0.0), felt_top(f))
            for f in h["felt"]]


def rect_dist(X, Z, r):
    cx, cz, hx, hz, yaw, _ = r
    a = math.radians(yaw)
    c, s = math.cos(a), math.sin(a)
    dx, dz = X - cx, Z - cz
    # inverse yaw: local = R^T d ; R maps local->parent with x' = x c + z s, z' = -x s + z c
    lx = dx * c - dz * s
    lz = dx * s + dz * c
    ox = np.maximum(np.abs(lx) - hx, 0)
    oz = np.maximum(np.abs(lz) - hz, 0)
    return np.hypot(ox, oz)


def felt_distance(h, X, Z):
    d = np.full(np.shape(X), 1e9)
    for r in felt_rects(h):
        d = np.minimum(d, rect_dist(X, Z, r))
    return d


class Ground:
    """Preview-only stepped ground for one hole (hole-local): nearest felt top - 0.6 (water: surface - 0.5),
    blurred, then clamped back under every felt/hazard piece. Dressing `pos.y` is sampled from it."""

    def __init__(self, h, margin=56.0, res=1.0):
        rects = felt_rects(h)
        pieces = [(r, r[5] - GROUND_DROP) for r in rects]
        for z in h["hazards"]:
            pieces.append(((z["center"][0], z["center"][2], z["size"][0] / 2, z["size"][1] / 2, z.get("yaw", 0.0), 0),
                           z["center"][1] - 0.5))
        xs = [r[0] - r[2] - r[3] for r in rects] + [r[0] + r[2] + r[3] for r in rects]
        zs = [r[1] - r[2] - r[3] for r in rects] + [r[1] + r[2] + r[3] for r in rects]
        self.x0, self.z0 = min(xs) - margin, min(zs) - margin
        self.res = res
        nx = int((max(xs) + margin - self.x0) / res) + 1
        nz = int((max(zs) + margin - self.z0) / res) + 1
        X, Z = np.meshgrid(self.x0 + np.arange(nx) * res, self.z0 + np.arange(nz) * res)
        D = np.stack([rect_dist(X, Z, r) for r, _ in pieces])
        Hs = np.array([y for _, y in pieces])
        H = Hs[np.argmin(D, axis=0)]
        caps = [(D[i] < 1.0, Hs[i]) for i in range(len(pieces))]
        for _ in range(4):
            H = self._blur(H, 3)
            for m, y in caps:
                H = np.where(m, np.minimum(H, y), H)
        self.X, self.Z, self.H = X, Z, H

    @staticmethod
    def _blur(H, r):
        k = np.ones(2 * r + 1) / (2 * r + 1)
        P = np.pad(H, r, mode="edge")
        P = np.apply_along_axis(lambda m: np.convolve(m, k, mode="valid"), 0, P)
        P = np.apply_along_axis(lambda m: np.convolve(m, k, mode="valid"), 1, P)
        return P

    def y(self, x, z):
        fx = np.clip((x - self.x0) / self.res, 0, self.H.shape[1] - 1.001)
        fz = np.clip((z - self.z0) / self.res, 0, self.H.shape[0] - 1.001)
        i, j = int(fz), int(fx)
        u, v = fx - j, fz - i
        H = self.H
        return float(H[i, j] * (1 - u) * (1 - v) + H[i, j + 1] * u * (1 - v) + H[i + 1, j] * (1 - u) * v + H[i + 1, j + 1] * u * v)
