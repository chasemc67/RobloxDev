"""World-scale fit helpers (pass 3): holes.json elements placed with world.json placements, walkway corridors,
terrain sampling and an exact triangle-vs-oriented-box test. Pure numpy, used by world_pieces.py (to keep the hero
tree's roots off the course) and world_fitcheck.py (verification).

Coordinates: Roblox world studs (x east, y up, z south). Hole placement (world/README.md):
    x' =  lx*cos(yaw) + lz*sin(yaw) + origin.x
    z' = -lx*sin(yaw) + lz*cos(yaw) + origin.z
    y' =  ly + origin.y
That is exactly dressing_lib.to_world with world_offset = origin and world_yaw = yaw, so the hole dicts are
patched and dressing_lib's keep-out primitives (felt / wall / hazard / moving-part sweep / teleport) are reused.
"""
import json, math, os, copy
import numpy as np
import dressing_lib as DL

SRC = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.dirname(SRC)
COURSE = os.path.dirname(MODELS)
WORLD = os.path.join(COURSE, "world")

CLEAR = 6.5          # anything may pass over felt / walkways only this high above them
DOOR_CLEAR = 12.0    # Heartwood Door: the 7-wide walkway must be open this high (arch is 20 high)
PATH_MARGIN = 0.75   # walkway corridor = width/2 + this


def load_world():
    return json.load(open(os.path.join(WORLD, "world.json")))


def holes_world(world=None):
    """holes.json holes with world_offset/world_yaw replaced by the world.json placement."""
    world = world or load_world()
    pl = {h["number"]: h["placement"] for h in world["holes"]}
    out = []
    for h in DL.load_holes():
        h = copy.deepcopy(h)
        p = pl[h["number"]]
        h["world_offset"] = list(p["origin"])
        h["world_yaw"] = p["yaw_deg"]
        out.append(h)
    return out


# ----------------------------------------------------------------------------- terrain
class Terrain:
    def __init__(self):
        t = json.load(open(os.path.join(WORLD, "terrain-4stud.json")))
        self.x0, self.z0, self.cell = t["x0"], t["z0"], t["cell"]
        self.H = np.array(t["height"], float)
        self.W = np.array([[np.nan if v is None else v for v in row] for row in t["water"]], float)
        self.M = np.array(t["mat"], int)
        self.mats = t["materials"]
        self.rows, self.cols = self.H.shape

    def height(self, x, z):
        x = np.asarray(x, float)
        z = np.asarray(z, float)
        i = np.clip((x - self.x0) / self.cell - 0.5, 0, self.cols - 1.001)
        j = np.clip((z - self.z0) / self.cell - 0.5, 0, self.rows - 1.001)
        i0, j0 = np.floor(i).astype(int), np.floor(j).astype(int)
        fi, fj = i - i0, j - j0
        H = self.H
        return (H[j0, i0] * (1 - fi) * (1 - fj) + H[j0, i0 + 1] * fi * (1 - fj) +
                H[j0 + 1, i0] * (1 - fi) * fj + H[j0 + 1, i0 + 1] * fi * fj)


# ----------------------------------------------------------------------------- boxes
class OBB:
    """Closed oriented box: centre c, rotation Rm (columns = box axes in world), half extents hf."""

    def __init__(self, label, c, Rm, hf):
        self.label = label
        self.c = np.asarray(c, float)
        self.Rm = np.asarray(Rm, float)
        self.hf = np.asarray(hf, float)
        self.rad = float(np.linalg.norm(self.hf))


def vol_to_obb(v, ylo=-50.0):
    """dressing_lib.Vol (2D footprint below ymax, or full OBB) -> OBB."""
    if v.hf[1] > 1e5:
        top = v.ymax if v.ymax is not None else 400.0
        lo = v.ymin if v.ymin is not None else ylo
        c = v.c.copy()
        c[1] = (top + lo) / 2
        return OBB(v.label, c, v.Rm, (v.hf[0], (top - lo) / 2, v.hf[2]))
    return OBB(v.label, v.c, v.Rm, v.hf)


def seg_obb(label, a, b, half_w, y_above, y_below=2.0, extend=0.5):
    """Corridor box along the segment a->b (world), half width half_w, from min(y)-y_below to max(y)+y_above."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = np.array([b[0] - a[0], 0.0, b[2] - a[2]])
    L = float(np.linalg.norm(d))
    d = d / L if L > 1e-6 else np.array([0, 0, 1.0])
    side = np.array([d[2], 0.0, -d[0]])
    Rm = np.column_stack([side, [0, 1, 0], d])
    lo, hi = min(a[1], b[1]) - y_below, max(a[1], b[1]) + y_above
    c = (a + b) / 2
    c[1] = (lo + hi) / 2
    return OBB(label, c, Rm, (half_w, (hi - lo) / 2, L / 2 + extend))


def hole_obbs(holes, numbers=None, include_heroes=True):
    """Every gameplay element of the selected holes as OBBs (world): felt (+1.25, up to felt top + 6.5), walls,
    hazards, moving-part sweeps (blockers + hero visual bbox, +0.5), teleports, tee pad + run-up, and the hero props
    placed on those holes (except the old pass-1 hollow_tree, replaced in the world by the world-scale shell)."""
    man = json.load(open(os.path.join(MODELS, "manifest.json")))["props"]
    by_motion = {}
    for p in man:
        mo = p.get("motion")
        if mo and mo.get("holes_json_id"):
            by_motion[(mo.get("hole"), mo["holes_json_id"])] = p
    out = []
    sel = [h for h in holes if numbers is None or h["number"] in numbers]
    for h in sel:
        H = f"H{h['number']}"
        vols = []
        for f in h["felt"]:
            vols.append(DL._box2d(h, f"{H}:felt:{f['id']}", f["center"], f["size"][0], f["size"][1], f.get("yaw", 0),
                                  DL.FELT_MARGIN, DL.to_world(h, [0, DL.felt_top(f), 0])[1] + CLEAR))
        for w in h["walls"]:
            top = w["center"][1] + w["size"][1] / 2
            vols.append(DL._box2d(h, f"{H}:wall:{w['id']}", w["center"], w["size"][0], w["size"][2], w.get("yaw", 0),
                                  DL.WALL_MARGIN, DL.to_world(h, [0, top, 0])[1] + CLEAR - 1.5))
        for z in h["hazards"]:
            vols.append(DL._box2d(h, f"{H}:hazard:{z['id']}", z["center"], z["size"][0], z["size"][1], z.get("yaw", 0),
                                  0.3, DL.to_world(h, z["center"])[1] + CLEAR))
        for mp in h["moving_parts"]:
            p = by_motion.get((H, mp["id"]))
            vis = (p["bbox_center_from_origin"], p["bbox_size_studs"]) if p else None
            vols += DL.sweep_vols(h, mp, vis)
        for t in h["teleports"]:
            for nm, c, r in (("entry", t["entry"]["center"], t["entry"]["radius"]), ("exit", t["exit"]["center"], 0.6)):
                cw = DL.to_world(h, c)
                vols.append(DL.Vol(f"{H}:teleport:{t['id']}:{nm}", cw, np.eye(3), (r + 0.8, 2.0, r + 0.8)))
        out += [vol_to_obb(v) for v in vols]
        tee = np.asarray(h["tee"]["position"], float)
        aim = np.array([h["tee"]["aim_hint"][0], 0, h["tee"]["aim_hint"][1]], float)
        a, b = DL.to_world(h, tee), DL.to_world(h, tee - aim * 8)
        out.append(seg_obb(f"{H}:tee_pad", a, b, 3.5, CLEAR, extend=3.5))
        if include_heroes:
            for p in man:
                if p.get("group") == "dressing" or p["name"] in ("hollow_tree", "water_surface"):
                    continue
                for pl in p.get("placements", []):
                    if pl["hole"] != H:
                        continue
                    s = pl.get("scale", 1.0)
                    S = np.array([s] * 3 if np.isscalar(s) else s, float)
                    c = np.asarray(p["bbox_center_from_origin"], float) * S
                    hf = np.asarray(p["bbox_size_studs"], float) * S / 2 + 0.3
                    Rw, off = DL.hole_xf(h)
                    Rm = Rw @ DL.yaw_mat(pl.get("yaw", 0))
                    cw = DL.to_world(h, np.asarray(pl["pos"], float) + DL.yaw_mat(pl.get("yaw", 0)) @ c)
                    out.append(OBB(f"{H}:hero:{p['name']}", cw, Rm, hf))
    return out


def path_obbs(world, ids=None, door_ids=("p_h8_h9",), door_center=None, door_r=(36.0, 50.0)):
    """Walkway corridors from world.json paths (each segment a box, width/2 + PATH_MARGIN, CLEAR high).
    Segments of the door walkway within door_r of the trunk centre get DOOR_CLEAR."""
    out = []
    for p in world["paths"]:
        if ids and p["id"] not in ids:
            continue
        hw = p["width"] / 2 + PATH_MARGIN
        for k, s in enumerate(p["segments"]):
            above = CLEAR
            if door_center is not None and p["id"] in door_ids:
                for q in (s["start"], s["end"]):
                    if door_r[0] - 4 < math.hypot(q[0] - door_center[0], q[2] - door_center[2]) < door_r[1] + 4:
                        above = DOOR_CLEAR
            out.append(seg_obb(f"path:{p['id']}:{k}:{s['type']}", s["start"], s["end"], hw, above))
    return out


def lantern_obbs(world):
    out = []
    for k, q in enumerate(world["lanterns"]["points"]):
        c = np.array(q["pos"], float) + np.array([0, 2.5, 0])
        out.append(OBB(f"lantern_post:{q['path']}:{k}", c, np.eye(3), (1.0, 3.0, 1.0)))
    return out


# ----------------------------------------------------------------------------- triangle vs OBB (separating axes)
def tris_hit_obb(T, box):
    """T: (N,3,3) world triangles. Returns bool (N,) = triangle intersects the closed box (SAT, 13 axes)."""
    if len(T) == 0:
        return np.zeros(0, bool)
    V = (T - box.c) @ box.Rm          # box-local
    h = box.hf
    hit = np.ones(len(T), bool)
    # box face normals
    for a in range(3):
        hit &= (V[:, :, a].min(1) <= h[a]) & (V[:, :, a].max(1) >= -h[a])
    if not hit.any():
        return hit
    idx = np.nonzero(hit)[0]
    V = V[idx]
    e = [V[:, 1] - V[:, 0], V[:, 2] - V[:, 1], V[:, 0] - V[:, 2]]
    n = np.cross(e[0], e[1])
    ok = np.ones(len(idx), bool)

    def sep(ax):
        p = np.einsum("nij,nj->ni", V, ax)
        r = np.abs(ax) @ h
        return (p.min(1) > r) | (p.max(1) < -r)
    ok &= ~sep(n)
    I = np.eye(3)
    for a in range(3):
        for ed in e:
            ax = np.cross(np.broadcast_to(I[a], ed.shape), ed)
            ok &= ~sep(ax)
    out = np.zeros(len(T), bool)
    out[idx] = ok
    return out


def check_tris(T, boxes, labels_only=False):
    """{label: n_tris_hitting}. Coarse prefilter by xz circle."""
    res = {}
    if len(T) == 0:
        return res
    cen = T.mean(1)
    rad = np.linalg.norm(T - cen[:, None, :], axis=2).max(1)
    for b in boxes:
        m = np.linalg.norm((cen - b.c)[:, [0, 2]], axis=1) < rad + b.rad + 0.01
        if not m.any():
            continue
        hit = tris_hit_obb(T[m], b)
        n = int(hit.sum())
        if n:
            res[b.label] = n
    return res


def points_clear(P, boxes, grow=0.0):
    """bool (N,) = point is outside every box grown by `grow` (used when growing roots)."""
    P = np.atleast_2d(np.asarray(P, float))
    ok = np.ones(len(P), bool)
    for b in boxes:
        L = (P - b.c) @ b.Rm
        ok &= ~np.all(np.abs(L) < b.hf + grow, axis=1)
    return ok


def dressing_keepouts(world=None, holes=None):
    """Pass 4: every keep-out a dressing prop must stay out of, in world space (OBBs): all holes (hole_obbs), every
    walkway / stair / landing segment (12 high at the Heartwood Door), the lantern posts, plazas and viewpoints with
    a radius, the Mere View bench and the mill flume. Shared by dressing_world.py and fitcheck.py."""
    world = world or load_world()
    holes = holes or holes_world(world)
    TO = np.array(world["hollow_tree"]["center"], float)
    KO = hole_obbs(holes) + path_obbs(world, door_center=TO) + lantern_obbs(world)
    for q in world["pois"]:
        if q.get("radius") and q["kind"] in ("plaza", "viewpoint"):
            c = np.array(q["pos"], float) + [0, CLEAR / 2 - 1, 0]
            KO.append(OBB(f"poi:{q['id']}", c, np.eye(3), (q["radius"], CLEAR / 2 + 1, q["radius"])))
        if q["id"] == "mere_view":
            KO.append(OBB("poi:mere_view", np.array(q["pos"]) + [0, 2, 0], np.eye(3), (3.0, 3.0, 3.0)))
    fl = world["mill_flume"]
    for a, b in zip(fl["points"], fl["points"][1:]):
        KO.append(seg_obb("mill_flume", a, b, fl["width"] / 2 + 0.6, 3.0, extend=0.6))
    return KO
