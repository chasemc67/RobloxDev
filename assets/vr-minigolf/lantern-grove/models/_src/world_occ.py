"""Pass 4: world-piece occupancy for dressing clash tests (Blender: needs the FBX importer).

Every world FBX part (models/world/fbx) is re-imported, placed with models/world/layout.json, and rasterised into a
1-stud xz grid per (part, instance): for each cell the min and max y of the part's surface over that cell, dilated
by one cell (so ~1 stud of clearance sideways). A dressing vertex at (x, y, z) CLASHES with a part when its cell is
occupied and ymin - 0.3 <= y <= ymax + 0.3. Per-part (not merged) intervals keep e.g. the tree interior lanterns
(high) and the wall-foot mushrooms (low) separate, so cells under a canopy or a dome stay free near the ground.
Thick solids (trunk wall, roots, rock kits) are covered because their top and bottom surfaces bound the interval.

Skipped (never near dressing): mountains, far hills, cloud cards, sky lanterns, mere boats (on water), and the crown
(base y 139.6, 40+ studs above any dressing top).
Cache: _src/cache/world_occ.npz (rebuilt when any world FBX or layout.json is newer).
"""
import os, json, math, glob
import numpy as np

SRC = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.dirname(SRC)
WDIR = os.path.join(MODELS, "world")
CACHE = os.path.join(SRC, "cache", "world_occ.npz")
SKIP = ("mountain_", "far_hill_", "cloud_card_", "sky_lantern", "mere_lantern_boat", "hollow_tree_crown")
PAD = 0.3


def load_tris(path):
    import bpy
    for o in list(bpy.data.objects):
        o.select_set(False)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y")
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    T = []
    for o in new:
        if o.type != "MESH":
            continue
        me = o.data
        me.calc_loop_triangles()
        mw = np.array(o.matrix_world)
        V = np.array([v.co[:] for v in me.vertices], float)
        V = V @ mw[:3, :3].T + mw[:3, 3]
        idx = np.array([t.vertices[:] for t in me.loop_triangles], int)
        if len(idx):
            T.append(V[idx])
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    T = np.concatenate(T) if T else np.zeros((0, 3, 3))
    return np.stack([T[..., 0], T[..., 2], -T[..., 1]], axis=-1)      # Blender -> Roblox


def place(R, inst):
    a = math.radians(inst.get("yaw", 0.0))
    c, s = math.cos(a), math.sin(a)
    S = np.array(inst.get("scale", [1, 1, 1]), float)
    L = R * S
    x = L[..., 0] * c + L[..., 2] * s
    z = -L[..., 0] * s + L[..., 2] * c
    p = inst["pos"]
    return np.stack([x + p[0], L[..., 1] + p[1], z + p[2]], axis=-1)


def sample_tris(T, step=0.5):
    """Points on every triangle with spacing <= step (barycentric grid)."""
    out = [T.reshape(-1, 3)]
    e = np.maximum(np.linalg.norm(T[:, 1] - T[:, 0], axis=1), np.linalg.norm(T[:, 2] - T[:, 0], axis=1))
    e = np.maximum(e, np.linalg.norm(T[:, 2] - T[:, 1], axis=1))
    n = np.ceil(e / step).astype(int)
    for k in np.unique(n):
        if k < 2:
            continue
        sel = T[n == k]
        ij = [(i, j) for i in range(k + 1) for j in range(k + 1 - i)]
        B = np.array([[1 - (i + j) / k, i / k, j / k] for i, j in ij])
        out.append(np.einsum("bk,nkd->nbd", B, sel).reshape(-1, 3))
    return np.concatenate(out)


def raster(P, label):
    x0, z0 = math.floor(P[:, 0].min()) - 1, math.floor(P[:, 2].min()) - 1
    nx = int(math.ceil(P[:, 0].max())) + 2 - x0
    nz = int(math.ceil(P[:, 2].max())) + 2 - z0
    ix = (P[:, 0] - x0).astype(int)
    iz = (P[:, 2] - z0).astype(int)
    lo = np.full((nz, nx), np.inf)
    hi = np.full((nz, nx), -np.inf)
    np.minimum.at(lo, (iz, ix), P[:, 1])
    np.maximum.at(hi, (iz, ix), P[:, 1])
    # dilate by one cell
    L2, H2 = lo.copy(), hi.copy()
    for dz in (-1, 0, 1):
        for dx in (-1, 0, 1):
            L2 = np.minimum(L2, np.roll(np.roll(lo, dz, 0), dx, 1))
            H2 = np.maximum(H2, np.roll(np.roll(hi, dz, 0), dx, 1))
    return dict(label=label, x0=x0, z0=z0, lo=L2, hi=H2)


class Occ:
    def __init__(self, grids):
        self.g = grids
        self.bb = np.array([[g["x0"], g["z0"], g["x0"] + g["lo"].shape[1], g["z0"] + g["lo"].shape[0]] for g in grids])

    def hits(self, P, pad=PAD, first_only=False):
        """{label: n_points} of points inside any part's occupied interval."""
        out = {}
        if len(P) == 0:
            return out
        mn, mx = P[:, [0, 2]].min(0), P[:, [0, 2]].max(0)
        cand = np.nonzero((self.bb[:, 0] <= mx[0]) & (self.bb[:, 2] >= mn[0]) & (self.bb[:, 1] <= mx[1]) &
                          (self.bb[:, 3] >= mn[1]))[0]
        for k in cand:
            g = self.g[k]
            ix = np.floor(P[:, 0] - g["x0"]).astype(int)
            iz = np.floor(P[:, 2] - g["z0"]).astype(int)
            ok = (ix >= 0) & (iz >= 0) & (ix < g["lo"].shape[1]) & (iz < g["lo"].shape[0])
            if not ok.any():
                continue
            y = P[ok, 1]
            lo = g["lo"][iz[ok], ix[ok]]
            hi = g["hi"][iz[ok], ix[ok]]
            n = int(((y >= lo - pad) & (y <= hi + pad)).sum())
            if n:
                out[g["label"]] = out.get(g["label"], 0) + n
                if first_only:
                    return out
        return out


def build_or_load(force=False):
    files = sorted(glob.glob(os.path.join(WDIR, "fbx", "*.fbx")))
    lay_p = os.path.join(WDIR, "layout.json")
    newest = max([os.path.getmtime(f) for f in files] + [os.path.getmtime(lay_p)])
    if not force and os.path.exists(CACHE) and os.path.getmtime(CACHE) > newest:
        z = np.load(CACHE, allow_pickle=True)
        return Occ(list(z["grids"]))
    lay = json.load(open(lay_p))
    grids = []
    for f in files:
        base = os.path.basename(f)[:-4]
        if base.startswith(SKIP):
            continue
        pid = base.split("_part")[0]
        if pid not in lay:
            continue
        R = load_tris(f)
        if len(R) == 0:
            continue
        for k, inst in enumerate(lay[pid]):
            P = sample_tris(place(R, inst))
            grids.append(raster(P, f"world:{base}" + (f"#{k}" if len(lay[pid]) > 1 else "")))
        print(f"[occ] {base}: {len(R)} tris x {len(lay[pid])}")
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    np.savez_compressed(CACHE, grids=np.array(grids, dtype=object))
    return Occ(grids)
