"""Shared world helpers for Lantern Grove (world.json <-> holes.json).

Conventions (same as holes.json):
  studs, +Y up, map view +X right (east), -Z up (north).
  Placement: world = R_y(yaw) * local + origin, with
      x' =  lx*cos(yaw) + lz*sin(yaw)
      z' = -lx*sin(yaw) + lz*cos(yaw)
      y' =  ly + origin_y
  (Roblox: CFrame.new(origin) * CFrame.Angles(0, math.rad(yaw), 0) * localCFrame.)

The heightfield is a pure function of world.json (see height_at / terrain "method" text), so
validate.py and make_maps.py evaluate exactly the same terrain.
"""
import json
import math
import os

import numpy as np
from matplotlib.path import Path as MplPath

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD_DIR = os.path.dirname(HERE)
COURSE_DIR = os.path.dirname(WORLD_DIR)
HOLES_JSON = os.path.join(COURSE_DIR, "holes.json")
WORLD_JSON = os.path.join(WORLD_DIR, "world.json")


def load_holes():
    with open(HOLES_JSON) as f:
        return json.load(f)


def load_world(path=WORLD_JSON):
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------- transforms
def rot(lx, lz, yaw_deg):
    a = math.radians(yaw_deg)
    c, s = math.cos(a), math.sin(a)
    return lx * c + lz * s, -lx * s + lz * c


def to_world(pl, p):
    """pl = {origin:[x,y,z], yaw_deg}; p = local [x,y,z] -> world [x,y,z]."""
    x, z = rot(p[0], p[2], pl["yaw_deg"])
    o = pl["origin"]
    return [o[0] + x, o[1] + p[1], o[2] + z]


def rect_corners(cx, cz, sx, sz, yaw):
    out = []
    for dx, dz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        x, z = rot(dx * sx / 2, dz * sz / 2, yaw)
        out.append((cx + x, cz + z))
    return out


def felt_world(hole, pl):
    """Felt pieces in world: dicts with corners, centre, yaw, surface params."""
    out = []
    for f in hole["felt"]:
        c = to_world(pl, f["center"])
        yaw = f["yaw"] + pl["yaw_deg"]
        sx, sz = f["size"]
        sl = f.get("slope") or None
        out.append(dict(id=f["id"], cx=c[0], cy=c[1], cz=c[2], sx=sx, sz=sz, yaw=yaw,
                        slope=sl, corners=rect_corners(c[0], c[2], sx, sz, yaw),
                        overlay=bool(f.get("overlay")),
                        bridge=(f.get("kind") == "bridge" or f.get("solid") is False)))
    return out


def walls_world(hole, pl):
    out = []
    for w in hole["walls"]:
        c = to_world(pl, w["center"])
        yaw = w["yaw"] + pl["yaw_deg"]
        sx, sy, sz = w["size"]
        out.append(dict(id=w["id"], cx=c[0], cy=c[1], cz=c[2], sx=sx, sy=sy, sz=sz, yaw=yaw,
                        corners=rect_corners(c[0], c[2], sx, sz, yaw)))
    return out


def footprint_rects(hole, pl):
    """All felt + wall rectangles (world corner lists) = the hole footprint."""
    return [f["corners"] for f in felt_world(hole, pl)] + [w["corners"] for w in walls_world(hole, pl)]


def local_frame(px, pz, cx, cz, yaw):
    """World points -> rect-local coords (u along local x, v along local z)."""
    a = math.radians(yaw)
    c, s = math.cos(a), math.sin(a)
    dx, dz = px - cx, pz - cz
    # inverse of x' = u c + v s ; z' = -u s + v c
    u = dx * c - dz * s
    v = dx * s + dz * c
    return u, v


def felt_surface(f, px, pz):
    """Surface height of felt piece f at world points (no bounds check)."""
    u, v = local_frame(px, pz, f["cx"], f["cz"], f["yaw"])
    y = np.full(np.shape(px), f["cy"], dtype=float)
    sl = f["slope"]
    if sl:
        L = f["sx"] if sl["axis"] == "x" else f["sz"]
        t = u if sl["axis"] == "x" else v
        y = y + sl["rise"] * (t / L)
    return y


def in_rect(px, pz, cx, cz, sx, sz, yaw, grow=0.0):
    u, v = local_frame(px, pz, cx, cz, yaw)
    return (np.abs(u) <= sx / 2 + grow) & (np.abs(v) <= sz / 2 + grow)


def rect_dist(px, pz, cx, cz, sx, sz, yaw):
    """Distance from points to a rotated rectangle (0 inside)."""
    u, v = local_frame(px, pz, cx, cz, yaw)
    du = np.maximum(np.abs(u) - sx / 2, 0)
    dv = np.maximum(np.abs(v) - sz / 2, 0)
    return np.hypot(du, dv)


# ---------------------------------------------------------------- 2D geometry
def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def poly_contains(poly, px, pz):
    path = MplPath(np.asarray(poly, dtype=float))
    pts = np.column_stack([np.ravel(px), np.ravel(pz)])
    return path.contains_points(pts).reshape(np.shape(px))


def poly_edge_dist(poly, px, pz):
    poly = np.asarray(poly, dtype=float)
    d = np.full(np.shape(px), np.inf)
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        d = np.minimum(d, seg_dist(px, pz, a, b)[0])
    return d


def seg_dist(px, pz, a, b):
    ax, az = a[0], a[1]
    bx, bz = b[0], b[1]
    vx, vz = bx - ax, bz - az
    L2 = vx * vx + vz * vz
    if L2 == 0:
        return np.hypot(px - ax, pz - az), np.zeros(np.shape(px))
    t = np.clip(((px - ax) * vx + (pz - az) * vz) / L2, 0, 1)
    return np.hypot(px - (ax + t * vx), pz - (az + t * vz)), t


def polyline_nearest(pts, px, pz):
    """Nearest distance to polyline + (segment index, t) of nearest point."""
    d = np.full(np.shape(px), np.inf)
    si = np.zeros(np.shape(px), dtype=int)
    tt = np.zeros(np.shape(px))
    for i in range(len(pts) - 1):
        di, ti = seg_dist(px, pz, pts[i], pts[i + 1])
        m = di < d
        d = np.where(m, di, d)
        si = np.where(m, i, si)
        tt = np.where(m, ti, tt)
    return d, si, tt


def convex_overlap_dist(A, B):
    """Min distance between two convex polygons (0 if they overlap)."""
    A = np.asarray(A, float)
    B = np.asarray(B, float)

    def sep_axis(P, Q):
        n = len(P)
        for i in range(n):
            e = P[(i + 1) % n] - P[i]
            ax = np.array([-e[1], e[0]])
            pa = P @ ax
            pb = Q @ ax
            if pa.max() < pb.min() or pb.max() < pa.min():
                return True
        return False

    if not (sep_axis(A, B) or sep_axis(B, A)):
        return 0.0
    best = np.inf
    for P, Q in ((A, B), (B, A)):
        for p in P:
            for i in range(len(Q)):
                d, _ = seg_dist(np.array(p[0]), np.array(p[1]), Q[i], Q[(i + 1) % len(Q)])
                best = min(best, float(d))
    return best


def min_enclosing_circle(points):
    """Welzl-style (iterative, deterministic order) minimal enclosing circle."""
    P = [tuple(map(float, p)) for p in points]

    def circ2(a, b):
        cx, cz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        return cx, cz, math.hypot(a[0] - cx, a[1] - cz)

    def circ3(a, b, c):
        ax, ay = a
        bx, by = b
        cx, cy = c
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(d) < 1e-12:
            return None
        ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
        uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
        return ux, uy, math.hypot(ax - ux, ay - uy)

    def inside(c, p):
        return c is not None and math.hypot(p[0] - c[0], p[1] - c[1]) <= c[2] + 1e-9

    c = None
    for i, p in enumerate(P):
        if inside(c, p):
            continue
        c = (p[0], p[1], 0.0)
        for j in range(i):
            q = P[j]
            if inside(c, q):
                continue
            c = circ2(p, q)
            for k in range(j):
                r = P[k]
                if inside(c, r):
                    continue
                c = circ3(p, q, r) or c
    return c


# ---------------------------------------------------------------- paths
def path_profile(path):
    """Expand a path's legs into a flat list of 3D polyline vertices (x, y, z, kind)
    following stairs flights/landings exactly. Stairs are already expanded in world.json
    ("segments"), so this just reads them."""
    pts = []
    for s in path["segments"]:
        a, b = s["start"], s["end"]
        if not pts:
            pts.append((a[0], a[1], a[2], s["type"]))
        pts.append((b[0], b[1], b[2], s["type"]))
    return pts


def segment_len3(s):
    a, b = s["start"], s["end"]
    return math.dist(a, b)


def segment_len2(s):
    a, b = s["start"], s["end"]
    return math.hypot(b[0] - a[0], b[2] - a[2])


# ---------------------------------------------------------------- heightfield
def _noise(base, X, Z):
    h = np.zeros(np.shape(X))
    for n in base.get("noise", []):
        h += n["amp"] * np.sin(2 * np.pi * X / n["wx"] + n["phase"][0]) * np.sin(2 * np.pi * Z / n["wz"] + n["phase"][1])
    return h


def _shape_dist(shape, X, Z):
    """Signed-ish distance: 0 inside, >0 outside (distance to shape)."""
    if shape["type"] == "polygon":
        inside = poly_contains(shape["points"], X, Z)
        d = poly_edge_dist(shape["points"], X, Z)
        return np.where(inside, 0.0, d)
    if shape["type"] == "ellipse":
        cx, cz = shape["center"]
        rx, rz = shape["radii"]
        r = np.hypot((X - cx) / rx, (Z - cz) / rz)
        return np.maximum(r - 1, 0) * min(rx, rz)
    if shape["type"] == "circle":
        cx, cz = shape["center"]
        return np.maximum(np.hypot(X - cx, Z - cz) - shape["radius"], 0)
    raise ValueError(shape["type"])


def height_natural(world, X, Z):
    """Steps 1-3: base + regions + rim (no paths/pads/water)."""
    T = world["terrain"]
    base = T["base"]
    H = np.full(np.shape(X), float(base["height"])) + _noise(base, X, Z)
    for r in T["regions"]:
        if r["op"] == "hill":
            cx, cz = r["center"]
            rx, rz = r["radii"] if "radii" in r else (r["radius"], r["radius"])
            q = np.hypot((X - cx) / rx, (Z - cz) / rz)
            bump = np.where(q < 1, np.cos(np.pi / 2 * q) ** 2, 0.0)
            H = H + r["peak"] * bump
        elif r["op"] == "set":
            d = _shape_dist(r["shape"], X, Z)
            w = 1 - smoothstep(d / r["falloff"])
            H = H + (r["height"] - H) * w
        elif r["op"] == "max":
            d = _shape_dist(r["shape"], X, Z)
            w = 1 - smoothstep(d / r["falloff"])
            H = np.maximum(H, H + (r["height"] - H) * w)
        else:
            raise ValueError(r["op"])
    rim = T["rim"]
    cx, cz = rim["center"]
    hx, hz = rim["half_size"]
    p = rim["exponent"]
    q = ((np.abs(X - cx) / hx) ** p + (np.abs(Z - cz) / hz) ** p) ** (1 / p)
    ang = np.arctan2(Z - cz, X - cx)
    var = 1 + rim["variation"] * np.sin(rim["lobes"] * ang + rim["phase"])
    t = smoothstep((q - rim["start"]) / (rim["full"] - rim["start"]))
    H = np.maximum(H, H + t * rim["height"] * var) if rim["height"] > 0 else H
    H = H + _noise(dict(noise=base.get("detail_noise", [])), X, Z)
    return H


def path_set(world, X, Z, H):
    """Step 4: walkway corridors graded to their profile."""
    for p in world["paths"]:
        segs = [s for s in p["segments"] if s["type"] not in ("on_hole", "bridge")]
        if not segs:
            continue
        hw = p["width"] / 2
        sh = world["terrain"]["path_grading"]["shoulder"]
        bestd = np.full(np.shape(X), np.inf)
        prof = np.zeros(np.shape(X))
        for s in segs:
            a, b = s["start"], s["end"]
            d, t = seg_dist(X, Z, (a[0], a[2]), (b[0], b[2]))
            y = a[1] + (b[1] - a[1]) * t
            if s["type"] == "stairs":
                y = y - world["terrain"]["path_grading"]["stair_bed_drop"]
            m = d < bestd
            bestd = np.where(m, d, bestd)
            prof = np.where(m, y, prof)
        w = 1 - smoothstep((bestd - hw - 1.0) / sh)
        H = H + (prof - H) * w
    return H


def pad_set(world, holes, X, Z, H):
    """Step 5: hole pads. Felt floor = felt top - thickness under every felt piece;
    around it the ground follows cones from each piece's floor (slope k) floored at the hole's
    lowest floor, inside footprint+margin; blended to the existing terrain over `falloff`;
    hazard rectangles are cut to (hazard surface - depth)."""
    P = world["terrain"]["pads"]
    th = P["felt_thickness"]
    k = P["cone_slope"]
    byn = {h["number"]: h for h in holes["holes"]}
    for hp in world["holes"]:
        hole = byn[hp["number"]]
        pl = hp["placement"]
        felts = [f for f in felt_world(hole, pl) if not f["overlay"]]
        walls = walls_world(hole, pl)
        # bbox
        allc = [c for f in felts for c in f["corners"]] + [c for w in walls for c in w["corners"]]
        xs = [c[0] for c in allc]
        zs = [c[1] for c in allc]
        R = P["margin"] + P["falloff"] + 1
        m = (X >= min(xs) - R) & (X <= max(xs) + R) & (Z >= min(zs) - R) & (Z <= max(zs) + R)
        if not m.any():
            continue
        x, z = X[m], Z[m]
        h0 = H[m]
        # distance to footprint
        dfoot = np.full(x.shape, np.inf)
        for f in felts:
            dfoot = np.minimum(dfoot, rect_dist(x, z, f["cx"], f["cz"], f["sx"], f["sz"], f["yaw"]))
        for w in walls:
            dfoot = np.minimum(dfoot, rect_dist(x, z, w["cx"], w["cz"], w["sx"], w["sz"], w["yaw"]))
        floors = []
        cone = np.full(x.shape, -np.inf)
        for f in felts:
            corners_y = felt_surface(f, np.array([c[0] for c in f["corners"]]), np.array([c[1] for c in f["corners"]]))
            fl = float(np.min(corners_y)) - th
            floors.append(fl)
            if f["bridge"]:
                continue
            dd = rect_dist(x, z, f["cx"], f["cz"], f["sx"], f["sz"], f["yaw"])
            cone = np.maximum(cone, fl - k * dd)
        ground = min(floors)
        pad = np.maximum(cone, ground)
        w = 1 - smoothstep((dfoot - P["margin"]) / P["falloff"])
        h = h0 + (pad - h0) * w
        # exact felt floor under felt (min over covering pieces)
        F = np.full(x.shape, np.inf)
        for f in felts:
            if f["bridge"]:
                continue
            inside = in_rect(x, z, f["cx"], f["cz"], f["sx"], f["sz"], f["yaw"])
            F = np.where(inside, np.minimum(F, felt_surface(f, x, z) - th), F)
        h = np.where(np.isfinite(F), F, h)
        for hz in hole["hazards"]:
            c = to_world(pl, hz["center"])
            depth = P["hazard_depth"][hz["type"]]
            inside = in_rect(x, z, c[0], c[2], hz["size"][0], hz["size"][1], hz["yaw"] + pl["yaw_deg"])
            h = np.where(inside, np.minimum(h, c[1] - depth), h)
        H = H.copy()
        H[m] = h
    return H


def felt_clamp(world, holes, X, Z, H):
    """Step 5b: walkway shoulders may never raise terrain above a felt floor."""
    th = world["terrain"]["pads"]["felt_thickness"]
    byn = {h["number"]: h for h in holes["holes"]}
    H = H.copy()
    for hp in world["holes"]:
        for f in felt_world(byn[hp["number"]], hp["placement"]):
            if f["overlay"] or f["bridge"]:
                continue
            inside = in_rect(X, Z, f["cx"], f["cz"], f["sx"], f["sz"], f["yaw"])
            if inside.any():
                H = np.where(inside, np.minimum(H, felt_surface(f, X, Z) - th), H)
    return H


def water_profile(world, X, Z):
    """Carve profile (terrain must be <= this) and water surface where wet."""
    prof = np.full(np.shape(X), np.inf)
    surf = np.full(np.shape(X), np.nan)
    st = world["stream"]
    pts = [(v["x"], v["z"]) for v in st["points"]]
    lv = np.array([v["level"] for v in st["points"]])
    wd = np.array([v["width"] for v in st["points"]])
    d, si, t = polyline_nearest(pts, X, Z)
    level = lv[si] + (lv[si + 1] - lv[si]) * t
    width = wd[si] + (wd[si + 1] - wd[si]) * t
    depth = st["depth"]
    bank = st["bank_slope"]
    hw = width / 2
    bed = level - depth + depth * smoothstep((d - (hw - 2.0)) / 2.0)
    p = np.where(d <= hw, bed, level + bank * (d - hw))
    prof = np.minimum(prof, p)
    wet = d <= hw
    surf = np.where(wet, level, surf)
    for lk in world["lakes"]:
        cx, cz = lk["center"]
        rx, rz = lk["radii"]
        q = np.hypot((X - cx) / rx, (Z - cz) / rz)
        dd = (q - 1) * min(rx, rz)  # <0 inside
        bw = lk["beach_width"]
        p = np.where(dd <= 0, lk["level"] - np.minimum(lk["depth"], -dd * 0.25 + 0.6),
                     np.where(dd <= bw, lk["level"] + lk["beach_slope"] * dd,
                              lk["level"] + lk["beach_slope"] * bw + lk["bank_slope"] * (dd - bw)))
        prof = np.minimum(prof, p)
        surf = np.where(dd <= 0, lk["level"], surf)
    return prof, surf


def height_at(world, holes, X, Z, stages=False):
    X = np.asarray(X, float)
    Z = np.asarray(Z, float)
    H1 = height_natural(world, X, Z)
    H2 = pad_set(world, holes, X, Z, H1)
    H3 = felt_clamp(world, holes, X, Z, path_set(world, X, Z, H2))
    prof, surf = water_profile(world, X, Z)
    H4 = np.minimum(H3, prof)
    if stages:
        return dict(natural=H1, pads=H2, paths=H3, final=H4, water_surface=surf)
    return H4


def water_surface(world, holes, X, Z):
    """Water surface height (nan = dry): stream + lakes + hole water hazards."""
    _, surf = water_profile(world, X, Z)
    byn = {h["number"]: h for h in holes["holes"]}
    for hp in world["holes"]:
        hole = byn[hp["number"]]
        pl = hp["placement"]
        for hz in hole["hazards"]:
            if hz["type"] != "water":
                continue
            c = to_world(pl, hz["center"])
            inside = in_rect(X, Z, c[0], c[2], hz["size"][0], hz["size"][1], hz["yaw"] + pl["yaw_deg"])
            surf = np.where(inside, c[1], surf)
    return surf


def grid(world, step=None):
    b = world["bounds"]
    step = step or world["heightmap"]["stud_per_px"]
    xs = np.arange(b["x"][0] + step / 2, b["x"][1], step)
    zs = np.arange(b["z"][0] + step / 2, b["z"][1], step)
    X, Z = np.meshgrid(xs, zs)
    return xs, zs, X, Z
