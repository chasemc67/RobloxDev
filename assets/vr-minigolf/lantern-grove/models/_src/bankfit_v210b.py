"""v210b helpers: bank backings vs rail-kit visuals in the holes.json hole-local frame (Roblox axes, studs).

The rail kit is placed in Studio (not in the manifest), so its visuals are modelled from holes.json with BOTH
documented rules (they disagree on the height):
  'note'     manifest RAIL_NOTE: pos = (wall.center.x, top of the felt it borders, wall.center.z), yaw = wall.yaw,
             Size.Z = wall length (one stretched piece); end posts on both rail ends.
  'assembly' _src/assembly.py previews: base = wall top - 1.0 (repeated rail_straight_4 pieces).
For the 'note' rule the felt under each rail end is used (a rail that meets a bank's high edge sits on the bank top
there), so both the low and the high variant of every rail end next to a backing are tested.
"""
import math
import numpy as np
import bpy
import lglib
import registry
import hole_skins

TIMBER = {"Oak", "OakDeep", "RootBark", "Shingle"}
STONE = {"Limestone"}


def yaw_mat(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def to_rbx(V):
    V = np.asarray(V, float)
    return np.stack([V[:, 0], V[:, 2], -V[:, 1]], -1)


def build_tris(name, col=None):
    """Fresh generator build of a registered prop -> {material: (n,3,3) tris in the Roblox prop frame}."""
    REG = {p["name"]: p for p in registry.PROPS}
    p = REG[name]
    col = col or bpy.context.scene.collection
    pb = lglib.PB("_bf_" + name)
    post = p["fn"](pb)
    root, objs = pb.finalize(col, p.get("smooth_angle", 40))
    if callable(post):
        post(root, objs)
    bpy.context.view_layer.update()
    out = {}
    for o in objs:
        me = o.data
        me.calc_loop_triangles()
        mw = np.array(o.matrix_world)
        V = np.array([v.co[:] for v in me.vertices], float) @ mw[:3, :3].T + mw[:3, 3]
        idx = np.array([t.vertices[:] for t in me.loop_triangles], int).reshape(-1, 3)
        mat = o.get("lg_mat") or o.name.split("__", 1)[1]
        out[mat] = to_rbx(V)[idx]
    for o in objs + [root]:
        me = o.data if o.type == "MESH" else None
        bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)
    return out


def place(T, pos, yaw, scale=(1, 1, 1)):
    T = np.asarray(T, float) * np.asarray(scale, float)
    return T @ yaw_mat(yaw).T + np.asarray(pos, float)


def felt_height_at(h, x, z, pad=0.35):
    """Highest felt surface within pad of (x, z) (sloped felts: plane height clamped to the rectangle)."""
    best = None
    for f in h["felt"]:
        c = np.array(f["center"], float)
        R = yaw_mat(f.get("yaw", 0))
        l = (np.array([x, c[1], z]) - c) @ R          # felt-local
        hx, hz = f["size"][0] / 2, f["size"][1] / 2
        if abs(l[0]) > hx + pad or abs(l[2]) > hz + pad:
            continue
        lx, lz = np.clip(l[0], -hx, hx), np.clip(l[2], -hz, hz)
        y = c[1]
        s = f.get("slope")
        if s:
            t = (lx / (2 * hx)) if s["axis"] == "x" else (lz / (2 * hz))
            y = c[1] + s["rise"] * t
        best = y if best is None else max(best, y)
    return best


def rail_visuals(h, rule, kit, near=None, near_pad=2.0):
    """Rail-kit visual instances for every plain rail wall of hole h.
    kit = dict(straight=tris of a 4-stud straight piece, post=tris of the end post).
    Returns [(wall_id, piece, material, T)]. near = (center, halfsize, R) box: keep only rails whose end lies near."""
    out = []
    for w in h["walls"]:
        if w.get("kind") is not None or not w["id"].startswith("rail"):
            continue
        c = np.array(w["center"], float)
        L = w["size"][2]
        R = yaw_mat(w.get("yaw", 0))
        ends = [c + R @ np.array([0, 0, s * L / 2]) for s in (-1, 1)]
        if near is not None:        # any point of the rail line within near_pad of the box footprint
            nc, nh, NR = near
            line = [c + R @ np.array([0, 0, t]) for t in np.arange(-L / 2, L / 2 + 1e-9, 0.25)]
            if not any(np.all(np.abs((e - nc) @ NR)[[0, 2]] <= nh[[0, 2]] + near_pad) for e in line):
                continue
        if rule == "assembly":
            bases = [w["center"][1] + w["size"][1] / 2 - 1.0]
        else:
            bases = sorted({round(felt_height_at(h, e[0], e[2]) or 0.0, 4) for e in ends})
        for b in bases:
            for mat, T in kit["straight"].items():
                out.append((w["id"], f"straight@{b:g}", mat, place(T, [c[0], b, c[2]], w.get("yaw", 0), (1, 1, L / 4.0))))
            for e in ends:
                for mat, T in kit["post"].items():
                    out.append((w["id"], f"post@{b:g}", mat, place(T, [e[0], b, e[2]], w.get("yaw", 0))))
    return out


def _bvh(T):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    return BVHTree.FromPolygons([Vector(v) for v in T.reshape(-1, 3)], [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(T))])


def _inside(B, p, d=(0.3127, 0.9131, 0.2614)):
    from mathutils import Vector
    o, dv, hits = Vector(p), Vector(d).normalized(), 0
    for _ in range(64):
        r = B.ray_cast(o, dv)
        if r[0] is None:
            break
        hits += 1
        o = r[0] + dv * 1e-5
    return hits % 2 == 1


def surface_samples(T, step=0.04):
    """Points (+ owning-triangle area weight) on triangles T, about one per step^2."""
    P, W = [], []
    for t in T:
        a, b, c = t
        area = 0.5 * np.linalg.norm(np.cross(b - a, c - a))
        if area < 1e-9:
            continue
        n = max(1, int(math.ceil(math.sqrt(area) / step)))
        pts = []
        for i in range(n):
            for j in range(n - i):
                u, v = (i + 1 / 3) / n, (j + 1 / 3) / n
                pts.append(a + u * (b - a) + v * (c - a))
        P += pts
        W += [area / len(pts)] * len(pts)
    return np.array(P), np.array(W)


def hidden_stone(stone_T, timber_vols, eps=0.003, step=0.04, occluders=()):
    """Area of the stone surface that lies inside (or within eps of the surface of) a timber volume.
    timber_vols: list of (label, T) closed meshes. occluders: closed stone meshes of the same prop - samples inside
    them are never visible (e.g. block tops inside the stone cap) and are skipped. Returns (area, {label: area})."""
    if not timber_vols:
        return 0.0, {}
    N = np.cross(stone_T[:, 1] - stone_T[:, 0], stone_T[:, 2] - stone_T[:, 0])
    N /= np.maximum(np.linalg.norm(N, axis=1), 1e-12)[:, None]
    by, total = {}, 0.0
    occ = [(T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0), _bvh(T)) for T in occluders]
    vols = []
    for lab, T in timber_vols:
        mn, mx = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)
        vols.append((lab, mn, mx, _bvh(T)))
    for k, t in enumerate(stone_T):
        tmn, tmx = t.min(0), t.max(0)
        cand = [v for v in vols if np.all(tmx >= v[1] - eps) and np.all(tmn <= v[2] + eps)]
        if not cand:
            continue
        P, W = surface_samples(t[None], step)
        Pq = P + N[k] * eps            # just outside the stone face: what the eye would see there
        for p, wgt in zip(Pq, W):
            if any(np.all(p >= a - 1e-9) and np.all(p <= b + 1e-9) and _inside(B, p) for a, b, B in occ):
                continue
            for lab, mn, mx, B in cand:
                if np.all(p >= mn - 1e-9) and np.all(p <= mx + 1e-9) and _inside(B, p):
                    by[lab] = by.get(lab, 0.0) + wgt
                    total += wgt
                    break
    return total, by
