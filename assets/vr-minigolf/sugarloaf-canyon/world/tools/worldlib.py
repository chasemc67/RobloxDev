"""Shared world helpers for Sugarloaf Canyon (adapted from lantern-grove/world/tools/worldlib.py).

Conventions (same as Lantern Grove's holes.json / world.json):
  studs (1 stud = 0.3 m), +Y up, map view +X right (east), -Z up (north).
  Placement: world = R_y(yaw) * local + origin, with
      x' =  lx*cos(yaw) + lz*sin(yaw) + origin.x
      z' = -lx*sin(yaw) + lz*cos(yaw) + origin.z
      y' =  ly + origin.y
  (Roblox: CFrame.new(origin) * CFrame.Angles(0, math.rad(yaw), 0) * localCFrame.)
  A hole's local frame has its tee at the origin and plays toward local -Z.

Differences from Lantern Grove: there is no holes.json yet. Every hole is a `concept_footprint`: one or more flat
pad boxes (tiers) in the hole's local frame, plus optional `spans` (local z ranges where the hole bridges a gap and the
terrain is left alone). The heightfield adds slot-canyon carves, several streams and lifts/gondolas on paths.

The heightfield is a pure function of world.json (height_at), so validate.py and make_maps.py see the same terrain.
"""
import json
import math
import os

import numpy as np
from matplotlib.path import Path as MplPath

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD_DIR = os.path.dirname(HERE)
COURSE_DIR = os.path.dirname(WORLD_DIR)
WORLD_JSON = os.path.join(WORLD_DIR, "world.json")

UNGRADED = ("on_hole", "bridge", "lift", "gondola", "dam_crest")   # path segments that don't shape terrain


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


def play_dir(yaw_deg):
    """World (dx, dz) of the local -Z play direction."""
    a = math.radians(yaw_deg)
    return -math.sin(a), -math.cos(a)


def bearing(dx, dz):
    """Compass bearing in degrees (0 = north = -Z, 90 = east = +X)."""
    return math.degrees(math.atan2(dx, -dz)) % 360


def rect_corners(cx, cz, sx, sz, yaw):
    out = []
    for dx, dz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        x, z = rot(dx * sx / 2, dz * sz / 2, yaw)
        out.append((cx + x, cz + z))
    return out


def pads_world(hole):
    """Concept pad boxes of a hole in world space: dicts with cx, cz, sx, sz, yaw, y, corners, id."""
    pl = hole["placement"]
    out = []
    for p in hole["concept"]["pads"]:
        (x0, x1), (z0, z1) = p["x"], p["z"]
        c = to_world(pl, [(x0 + x1) / 2, p["y"], (z0 + z1) / 2])
        sx, sz = x1 - x0, z1 - z0
        yaw = pl["yaw_deg"]
        out.append(dict(id=p["id"], cx=c[0], cz=c[2], y=c[1], sx=sx, sz=sz, yaw=yaw,
                        lx=(x0, x1), lz=(z0, z1), corners=rect_corners(c[0], c[2], sx, sz, yaw)))
    return out


def local_frame(px, pz, cx, cz, yaw):
    """World points -> rect-local coords (u along local x, v along local z)."""
    a = math.radians(yaw)
    c, s = math.cos(a), math.sin(a)
    dx, dz = px - cx, pz - cz
    return dx * c - dz * s, dx * s + dz * c


def hole_local(hole, px, pz):
    pl = hole["placement"]
    return local_frame(px, pz, pl["origin"][0], pl["origin"][2], pl["yaw_deg"])


def in_rect(px, pz, cx, cz, sx, sz, yaw, grow=0.0):
    u, v = local_frame(px, pz, cx, cz, yaw)
    return (np.abs(u) <= sx / 2 + grow) & (np.abs(v) <= sz / 2 + grow)


def rect_dist(px, pz, cx, cz, sx, sz, yaw):
    """Distance from points to a rotated rectangle (0 inside)."""
    u, v = local_frame(px, pz, cx, cz, yaw)
    du = np.maximum(np.abs(u) - sx / 2, 0)
    dv = np.maximum(np.abs(v) - sz / 2, 0)
    return np.hypot(du, dv)


def in_span(hole, px, pz):
    """True where a point is inside one of the hole's declared spans (local z ranges bridged over a gap/water)."""
    spans = hole["concept"].get("spans") or []
    if not spans:
        return np.zeros(np.shape(px), bool)
    _, v = hole_local(hole, px, pz)
    m = np.zeros(np.shape(px), bool)
    for s in spans:
        m |= (v >= s["z"][0]) & (v <= s["z"][1])
    return m


# ---------------------------------------------------------------- 2D geometry
def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def poly_contains(poly, px, pz):
    path = MplPath(np.asarray(poly, dtype=float))
    pts = np.column_stack([np.ravel(px), np.ravel(pz)])
    return path.contains_points(pts).reshape(np.shape(px))


def seg_dist(px, pz, a, b):
    ax, az = a[0], a[1]
    bx, bz = b[0], b[1]
    vx, vz = bx - ax, bz - az
    L2 = vx * vx + vz * vz
    if L2 == 0:
        return np.hypot(px - ax, pz - az), np.zeros(np.shape(px))
    t = np.clip(((px - ax) * vx + (pz - az) * vz) / L2, 0, 1)
    return np.hypot(px - (ax + t * vx), pz - (az + t * vz)), t


def poly_edge_dist(poly, px, pz):
    poly = np.asarray(poly, dtype=float)
    d = np.full(np.shape(px), np.inf)
    n = len(poly)
    for i in range(n):
        d = np.minimum(d, seg_dist(px, pz, poly[i], poly[(i + 1) % n])[0])
    return d


def polyline_nearest(pts, px, pz):
    """Nearest distance to a polyline + (segment index, t) of the nearest point."""
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
            pa, pb = P @ ax, Q @ ax
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


# ---------------------------------------------------------------- paths
def segment_len3(s):
    return math.dist(s["start"], s["end"])


def segment_len2(s):
    a, b = s["start"], s["end"]
    return math.hypot(b[0] - a[0], b[2] - a[2])


# ---------------------------------------------------------------- heightfield
def _noise(spec, X, Z):
    h = np.zeros(np.shape(X))
    for n in spec:
        h += n["amp"] * np.sin(2 * np.pi * X / n["wx"] + n["phase"][0]) * np.sin(2 * np.pi * Z / n["wz"] + n["phase"][1])
    return h


def _shape_dist(shape, X, Z):
    """0 inside, >0 = distance outside the shape."""
    if shape["type"] == "polygon":
        inside = poly_contains(shape["points"], X, Z)
        return np.where(inside, 0.0, poly_edge_dist(shape["points"], X, Z))
    if shape["type"] == "ellipse":
        cx, cz = shape["center"]
        rx, rz = shape["radii"]
        r = np.hypot((X - cx) / rx, (Z - cz) / rz)
        return np.maximum(r - 1, 0) * min(rx, rz)
    if shape["type"] == "circle":
        cx, cz = shape["center"]
        return np.maximum(np.hypot(X - cx, Z - cz) - shape["radius"], 0)
    raise ValueError(shape["type"])


def _slot(r, X, Z, H):
    """Slot canyon: carve to the floor (linear between vertices) within width/2, cliff walls over `wall` studs."""
    pts = [(p[0], p[1]) for p in r["points"]]
    fl = np.array([p[2] for p in r["points"]], float)
    wd = np.array([p[3] for p in r["points"]], float)
    d, si, t = polyline_nearest(pts, X, Z)
    floor = fl[si] + (fl[si + 1] - fl[si]) * t
    hw = (wd[si] + (wd[si + 1] - wd[si]) * t) / 2
    w = 1 - smoothstep((d - hw) / r["wall"])
    return np.minimum(H, H + (floor - H) * w)


def height_natural(world, X, Z):
    """base + regions (set / max / hill / slot, in list order) + rim + detail noise."""
    T = world["terrain"]
    base = T["base"]
    H = np.full(np.shape(X), float(base["height"])) + _noise(base.get("noise", []), X, Z)
    for r in T["regions"]:
        op = r["op"]
        if op == "superellipse_dome":
            cx, _, cz = r["center"]
            p = r["params"]
            q = np.hypot(X-cx, Z-cz) / p["radius"]
            dome = p["base"] + p["height"] * np.sqrt(np.maximum(0, 1-q**p["exponent"]))
            H = np.where(q <= 1, dome, H)
        elif op == "hill":
            cx, cz = r["center"]
            rx, rz = r["radii"] if "radii" in r else (r["radius"], r["radius"])
            q = np.hypot((X - cx) / rx, (Z - cz) / rz)
            H = H + r["peak"] * np.where(q < 1, np.cos(np.pi / 2 * q) ** 2, 0.0)
        elif op in ("set", "max"):
            d = _shape_dist(r["shape"], X, Z)
            w = 1 - smoothstep(d / r["falloff"])
            Hn = H + (r["height"] - H) * w
            H = np.maximum(H, Hn) if op == "max" else Hn
        elif op == "slot":
            H = _slot(r, X, Z, H)
        else:
            raise ValueError(op)
    rim = T["rim"]
    cx, cz = rim["center"]
    hx, hz = rim["half_size"]
    p = rim["exponent"]
    q = ((np.abs(X - cx) / hx) ** p + (np.abs(Z - cz) / hz) ** p) ** (1 / p)
    ang = np.arctan2(Z - cz, X - cx)
    var = 1 + rim["variation"] * np.sin(rim["lobes"] * ang + rim["phase"])
    t = smoothstep((q - rim["start"]) / (rim["full"] - rim["start"]))
    H = np.maximum(H, rim["height"] * var * t + (1 - t) * H)
    detail = _noise(base.get("detail_noise", []), X, Z)
    for feature in T["regions"]:
        if feature["op"] == "superellipse_dome":
            cx, _, cz = feature["center"]
            detail = np.where(np.hypot(X-cx, Z-cz) <= feature["params"]["radius"], 0, detail)
    H = H + detail
    return H


def pad_set(world, X, Z, H):
    """Hole pads: every concept pad box is flattened to its y; around it the ground blends back to the natural terrain
    over `falloff` studs beyond `margin`. Points inside a declared span keep min(natural, pad) (a bridged gap)."""
    P = world["terrain"]["pads"]
    H = H.copy()
    for hole in world["holes"]:
        pads = pads_world(hole)
        allc = [c for p in pads for c in p["corners"]]
        xs = [c[0] for c in allc]
        zs = [c[1] for c in allc]
        R = P["margin"] + P["falloff"] + 1
        m = (X >= min(xs) - R) & (X <= max(xs) + R) & (Z >= min(zs) - R) & (Z <= max(zs) + R)
        if not m.any():
            continue
        x, z = X[m], Z[m]
        h0 = H[m]
        dbest = np.full(x.shape, np.inf)
        ybest = np.zeros(x.shape)
        for p in pads:
            d = rect_dist(x, z, p["cx"], p["cz"], p["sx"], p["sz"], p["yaw"])
            better = d < dbest - 1e-9
            dbest = np.where(better, d, dbest)
            ybest = np.where(better, p["y"], ybest)
        w = 1 - smoothstep((dbest - P["margin"]) / P["falloff"])
        h = h0 + (ybest - h0) * w
        sp = in_span(hole, x, z) & (dbest <= P["margin"])
        h = np.where(sp, np.minimum(h0, ybest), h)
        H[m] = h
    return H


def path_set(world, X, Z, H):
    """Walkway corridors graded to their profile (stairs: profile - stair_bed_drop). Ungraded segment types
    (on_hole, bridge, lift, gondola, dam_crest) leave the terrain alone."""
    PG = world["terrain"]["path_grading"]
    sh = PG["shoulder"]
    H = H.copy()
    for p in world["paths"]:
        segs = [s for s in p["segments"] if s["type"] not in UNGRADED]
        if not segs:
            continue
        hw = p["width"] / 2
        R = hw + 1.0 + sh
        allx = [v for s in segs for v in (s["start"][0], s["end"][0])]
        allz = [v for s in segs for v in (s["start"][2], s["end"][2])]
        m = (X >= min(allx) - R) & (X <= max(allx) + R) & (Z >= min(allz) - R) & (Z <= max(allz) + R)
        if not m.any():
            continue
        x, z = X[m], Z[m]
        bestd = np.full(x.shape, np.inf)
        prof = np.zeros(x.shape)
        for s in segs:
            a, b = s["start"], s["end"]
            d, t = seg_dist(x, z, (a[0], a[2]), (b[0], b[2]))
            y = a[1] + (b[1] - a[1]) * t
            if s["type"] == "stairs":
                y = y - PG["stair_bed_drop"]
            better = d < bestd
            bestd = np.where(better, d, bestd)
            prof = np.where(better, y, prof)
        w = 1 - smoothstep((bestd - hw - 1.0) / sh)
        h = H[m]
        H[m] = h + (prof - h) * w
    return H


def pad_clamp(world, X, Z, H):
    """Path shoulders may never change the ground inside a pad box (outside declared spans)."""
    H = H.copy()
    for hole in world["holes"]:
        for p in pads_world(hole):
            inside = in_rect(X, Z, p["cx"], p["cz"], p["sx"], p["sz"], p["yaw"])
            inside &= ~in_span(hole, X, Z)
            if inside.any():
                H = np.where(inside, p["y"], H)
    return H


def water_profile(world, X, Z):
    """Carve profile (terrain must be <= this) and water surface (nan = dry) for streams + lakes."""
    prof = np.full(np.shape(X), np.inf)
    surf = np.full(np.shape(X), np.nan)
    for st in world["streams"]:
        pts = [(v["x"], v["z"]) for v in st["points"]]
        lv = np.array([v["level"] for v in st["points"]])
        wd = np.array([v["width"] for v in st["points"]])
        d, si, t = polyline_nearest(pts, X, Z)
        level = lv[si] + (lv[si + 1] - lv[si]) * t
        hw = (wd[si] + (wd[si + 1] - wd[si]) * t) / 2
        depth = st["depth"]
        bed = level - depth + depth * smoothstep((d - (hw - 2.0)) / 2.0)
        reach = st.get("bank_reach", 10.0)
        p = np.where(d <= hw, bed, np.where(d <= hw + reach, level + st["bank_slope"] * (d - hw), np.inf))
        prof = np.minimum(prof, p)
        surf = np.where(d <= hw, np.where(np.isnan(surf), level, np.maximum(surf, level)), surf)
    for lk in world["lakes"]:
        cx, cz = lk["center"]
        rx, rz = lk["radii"]
        q = np.hypot((X - cx) / rx, (Z - cz) / rz)
        dd = (q - 1) * min(rx, rz)  # < 0 inside
        bw = lk["beach_width"]
        p = np.where(dd <= 0, lk["level"] - np.minimum(lk["depth"], -dd * 0.25 + 0.6),
                     np.where(dd <= bw, lk["level"] + lk["beach_slope"] * dd,
                              np.where(dd <= bw + lk.get("bank_reach", 12.0),
                                       lk["level"] + lk["beach_slope"] * bw + lk["bank_slope"] * (dd - bw), np.inf)))
        prof = np.minimum(prof, p)
        surf = np.where(dd <= 0, lk["level"], surf)
    return prof, surf


def height_at(world, X, Z, stages=False):
    X = np.asarray(X, float)
    Z = np.asarray(Z, float)
    H1 = height_natural(world, X, Z)
    H2 = pad_set(world, X, Z, H1)
    H3 = pad_clamp(world, X, Z, path_set(world, X, Z, H2))
    prof, surf = water_profile(world, X, Z)
    H4 = np.minimum(H3, prof)
    if stages:
        return dict(natural=H1, pads=H2, paths=H3, final=H4, water_surface=surf)
    return H4


def water_surface(world, X, Z):
    return water_profile(world, np.asarray(X, float), np.asarray(Z, float))[1]


def grid(world, step=None):
    b = world["bounds"]
    step = step or world["heightmap"]["stud_per_px"]
    xs = np.arange(b["x"][0] + step / 2, b["x"][1], step)
    zs = np.arange(b["z"][0] + step / 2, b["z"][1], step)
    X, Z = np.meshgrid(xs, zs)
    return xs, zs, X, Z
