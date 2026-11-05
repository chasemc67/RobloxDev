"""Shared constants for the Sugarloaf world pipeline (used by sc_layout.py and the Blender build; no bpy)."""
import zlib

CLIFF_STEP = 21.0          # panel spacing along a cliff line (panels are 24 wide -> ~3 studs overlap)
CLIFF_LIMIT = 600.0        # beyond |x| or |z| 600 the terrain rim takes over
CLIFF_MIN_DROP = 10.0      # only dress cliffs at least this tall
KIT_HEIGHTS = (6, 12, 24, 48)
SLOT_HEIGHTS = (24, 48)
MINE_HEAD_POS = (134.0, 392.0)
N_DUNES = 10

LIFT_KEYS = {"Rock Candy Lift": "rock_candy", "Taffy Cliff Lift": "taffy_cliff", "Gumdrop Lift": "gumdrop",
             "Crown Lift": "crown"}

VARIANTS = {"hoodoo": "abcd", "crystal": "abc", "cactus": "abc"}

SCATTER_KINDS = {
    "Sugarloaf Junction": ["scrub_a", "scrub_b", "rock_a", "rock_b", "scrub_a"],
    "Rock Candy Narrows": ["rock_a", "rock_b", "scrub_b"],
    "Taffy Mesa": ["gumdrop_boulder_a", "gumdrop_boulder_b", "scrub_a", "rock_a", "gumdrop_boulder_a"],
    "Sugarloaf Dam": ["rock_a", "rock_b", "scrub_b", "scrub_a"],
    "Hoodoo Garden": ["rock_a", "rock_b", "scrub_b", "gumdrop_boulder_b"],
    "Sugarloaf Crown": ["gumdrop_boulder_a", "gumdrop_boulder_b", "rock_b", "scrub_a"],
}
SCATTER_RADIUS = {"scrub_a": 1.6, "scrub_b": 1.4, "rock_a": 1.8, "rock_b": 2.6, "gumdrop_boulder_a": 2.6,
                  "gumdrop_boulder_b": 3.4}

# card piece, reference size [width, height] of the exported card
CARD_REF = {"distant_mesa": ("distant_mesa_card", (400.0, 200.0)),
            "butte_spire": ("butte_spire_card", (80.0, 200.0)),
            "far_arch": ("far_arch_card", (420.0, 300.0)),
            "far_butte": ("far_butte_card", (260.0, 380.0))}


def variant_for(kind, ident):
    v = VARIANTS[kind]
    return f"{kind}_{v[zlib.crc32(ident.encode()) % len(v)]}"


def _yaw_facing(dx, dz):
    import math
    return math.degrees(math.atan2(-dx, -dz))


def lift_params(world):
    """key -> dict(rise, D, yaw, gang): shaft yaw bisects the arriving walk and the top direction; `gang` = gangway angle
    (deg, Blender +Z rotation) relative to the shaft's local -Z (Blender +Y)."""
    import math
    out = {}
    for p in world["paths"]:
        segs = p["segments"]
        for i, s in enumerate(segs):
            if s["type"] != "lift":
                continue
            b, t = s["start"], s["end"]
            prev = segs[i - 1]
            ya = _yaw_facing(b[0] - prev["start"][0], b[2] - prev["start"][2])     # arrival direction
            yt = _yaw_facing(t[0] - b[0], t[2] - b[2])                             # toward the top point
            d = (yt - ya + 180) % 360 - 180
            yaw = ya + d / 2
            out[LIFT_KEYS[s["name"]]] = dict(rise=t[1] - b[1], D=math.hypot(t[0] - b[0], t[2] - b[2]), yaw=round(yaw, 2),
                                             gang=round(d / 2, 2), bottom=b, top=t)
    return out


BOARDING_TRIM = 6.0     # walkway corridor within this distance of a lift/gondola boarding point = boarding area
