"""holes.json / world.json access for the Aurora prop generators and fitcheck (pure python; no bpy).
holes.json is the source of truth for holes, movers, anchors and collision; world.json only for world placements."""
import json, math, os

SRC = os.path.dirname(os.path.abspath(__file__))
IN = os.environ.get("AA_IN", os.path.join(os.path.dirname(os.path.dirname(SRC)), "props_in", "aurora-archipelago"))
HOLES = json.load(open(os.path.join(IN, "holes.json")))["holes"]
WORLD = json.load(open(os.path.join(IN, "world", "world.json")))
H = {h["number"]: h for h in HOLES}


def anchor(n, name):
    return next(a for a in H[n]["decoration_anchors"] if a["name"] == name)


def wall(n, wid):
    return next(w for w in H[n]["walls"] if w["id"] == wid)


def felt(n, fid):
    return next(f for f in H[n]["felt"] if f["id"] == fid)


def mover(n, mid):
    return next(m for m in H[n]["moving_parts"] if m["id"] == mid)


def yaw_rot(x, z, yaw):
    """Roblox R_y(yaw) applied to local (x, z): x' = x cos + z sin, z' = -x sin + z cos."""
    a = math.radians(yaw)
    return x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)


def to_world(n, p):
    h = H[n]
    x, z = yaw_rot(p[0], p[2], h["world_yaw"])
    o = h["world_offset"]
    return [x + o[0], p[1] + o[1], z + o[2]]


def world_to_local(n, p):
    h = H[n]
    o = h["world_offset"]
    x, z = yaw_rot(p[0] - o[0], p[2] - o[2], -h["world_yaw"])
    return [x, p[1] - o[1], z]


def yaw_facing(f):
    """Yaw so that a prop's local +Z front faces the player who reads a sign pointing along `f` (local x,z):
    front normal = -f (toward the approaching player)."""
    return math.degrees(math.atan2(-f[0], -f[1]))


def yaw_pointing(f):
    """Yaw so that a decal arrow modelled pointing local -Z points along f."""
    return math.degrees(math.atan2(-f[0], -f[1]))


def in_box_xz(px, pz, c, s, yaw, pad=0.0):
    lx, lz = yaw_rot(px - c[0], pz - c[2], -yaw)
    return abs(lx) <= s[0] / 2 + pad and abs(lz) <= s[-1] / 2 + pad


def box_dist_xz(px, pz, c, s, yaw):
    """Horizontal distance from (px,pz) to a yawed box footprint (0 inside)."""
    lx, lz = yaw_rot(px - c[0], pz - c[2], -yaw)
    dx = max(abs(lx) - s[0] / 2, 0.0)
    dz = max(abs(lz) - s[-1] / 2, 0.0)
    return math.hypot(dx, dz)


def felt_top_at(n, px, pz, pad=0.0):
    """Highest felt top surface over (px, pz) in hole-local coords (slopes included), or None."""
    best = None
    for f in H[n]["felt"]:
        c, s, yaw = f["center"], f["size"], f.get("yaw", 0.0)
        lx, lz = yaw_rot(px - c[0], pz - c[2], -yaw)
        if abs(lx) <= s[0] / 2 + pad and abs(lz) <= s[1] / 2 + pad:
            y = c[1]
            sl = f.get("slope")
            if sl:
                u = (lx / s[0]) if sl["axis"] == "x" else (lz / s[1])
                y += u * sl["rise"]
            best = y if best is None else max(best, y)
    return best


def nearest_felt_top(n, px, pz):
    """Felt top under the point, else the top of the nearest felt piece (ground reference for heights)."""
    y = felt_top_at(n, px, pz)
    if y is not None:
        return y
    bd, by = 1e9, 0.0
    for f in H[n]["felt"]:
        d = box_dist_xz(px, pz, f["center"], [f["size"][0], 0, f["size"][1]], f.get("yaw", 0.0))
        if d < bd:
            bd, by = d, f["center"][1]
    return by


def tee_teleport(n):
    h = next(x for x in WORLD["holes"] if x["number"] == n)
    return h.get("tee_teleport")
