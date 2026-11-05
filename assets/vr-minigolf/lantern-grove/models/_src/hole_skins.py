"""Pass 5: per-hole felt + rail-kit variants (pure python; used by registry.manifest_header -> manifest.hole_skins,
world_scene.py previews and make_docs.py).

H8 (under the giant root arch) and H9 (inside the hollow tree) read too dark: brighter felt (FeltBright,
felt_bright.png) and a light edge trim (rail_*_trim: TrimStone blocks + cream TrimCream cap). H6 (mill race) gets a
clearly different rail (rail_*_mill: dark MillSlate blocks + painted MillBlue cap). Every other hole keeps the base
kit. Variants have the same 0.5 x 1.0 profile and origin as the base rail kit, so they drop onto the same walls.
"""
BASE = dict(felt_material="Felt", felt_texture="textures/felt.png", rail_straight_4="rail_straight_4",
            rail_straight_2="rail_straight_2", rail_end_post="rail_end_post", rail_block="Limestone", rail_cap="Oak")
TRIM = dict(felt_material="FeltBright", felt_texture="textures/felt_bright.png",
            rail_straight_4="rail_straight_4_trim", rail_straight_2="rail_straight_2_trim",
            rail_end_post="rail_end_post_trim", rail_block="TrimStone", rail_cap="TrimCream",
            why="dark hole (root arch / inside the tree): brighter felt + light cream edge trim")
MILL = dict(BASE, rail_straight_4="rail_straight_4_mill", rail_straight_2="rail_straight_2_mill",
            rail_end_post="rail_end_post_mill", rail_block="MillSlate", rail_cap="MillBlue",
            why="mill hole: clearly different rail colour / material")
# v210b (H9 game-art review): H9 keeps the bright felt but its rails are OakDeep #7A4E32 (Reflectance 0) on tops and
# faces; limestone #B8AFA0 only on the end posts (and the bank backing). Do not put rail-kit pieces on *_backing walls.
H9 = dict(TRIM, rail_straight_4="rail_straight_4_h9", rail_straight_2="rail_straight_2_h9",
          rail_end_post="rail_end_post_h9", rail_block="OakDeep", rail_cap="OakDeep", rail_post="Limestone",
          why="inside the hollow tree: bright felt; v210b oak rails (OakDeep, Reflectance 0) with limestone posts")
SKINS = {f"H{n}": dict(BASE) for n in range(1, 10)}
SKINS["H6"] = MILL
SKINS["H8"] = dict(TRIM)
SKINS["H9"] = H9


def manifest_block():
    import lglib
    out = dict(note=("Pass 5 per-hole skins. felt_material: set the felt Parts/MeshParts of that hole to this "
                     "colour/material (+ SurfaceAppearance ColorMap = felt_texture, NormalMap = textures/felt_normal.png). "
                     "rail_*: use these rail-kit props on that hole's rail walls (same placement rule as the base kit). "
                     "v210b: rail walls only - never on *_backing walls (bank_backing_stone is their visual)."),
               holes={})
    for h, s in SKINS.items():
        d = dict(s)
        for k in ("felt_material", "rail_block", "rail_cap", "rail_post"):
            if k not in s:
                continue
            hexv, rbx = lglib.MATS[s[k]][:2]
            d[k + "_color"], d[k + "_roblox_material"] = hexv, rbx
            if s[k] in lglib.REFLECTANCE:           # v210b: OakDeep rails -> Reflectance 0
                d[k + "_reflectance"] = lglib.REFLECTANCE[s[k]]
        out["holes"][h] = d
    return out
