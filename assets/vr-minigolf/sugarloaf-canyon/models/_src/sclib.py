"""Sugarloaf Canyon prop library: Lantern Grove's lglib (PB builder, primitives, export helpers) re-skinned with the
course.md palette, plus the world-y strata UVs.

Conventions (unchanged from lglib):
* 1 Blender unit = 1 stud, Z-up. Roblox (x, y, z) = Blender (x, z, -y). FBX forward -Z, up Y, scale 1.
* Every piece = root Empty + one child mesh per material (<piece>__<Material>), all sharing the piece origin.
* Front of a building / kit piece = Roblox local -Z = Blender +Y.

Strata: material "Strata" uses textures/strata.png, a 6-band strip covering 36 studs. Its UVs are V = (local_z + Y0)/36
and U = horizontal/36, where Y0 = the WORLD y of the piece origin (set STRATA_Y0 before finalize). Every striped mesh
therefore shows band floor(y/6) mod 6 at world height y, so stripes line up across all cliffs. Kit pieces that are
instanced at many heights are exported in 6 phase variants (_p0.._p5, phase = (base_y/6) mod 6).
"""
import math, os
import bmesh
from mathutils import Vector, Matrix
import lglib
from lglib import PB, M, R, TAU, tri_count, bbox_blender, to_roblox_bbox  # noqa: F401  (re-export)

STRATA_BAND = 6.0
STRATA_REPEAT = 36.0
STRATA_Y0 = 0.0
STRATA_WAVE = None       # optional f(x, y) -> stud offset added to V (pass-6 cliff kit), set per piece by finalize

# name: (hex, roblox_material, emission_strength, transparency, note)
MATS = {
    "Strata":     ("#F2B48A", "Sandstone", 0, 0, "candy strata rock; SurfaceAppearance ColorMap textures/strata.png (V = world y/36)"),
    "MesaTop":    ("#E59C7C", "Sand", 0, 0, "mesa-top peach sand"),
    "FloorSand":  ("#D88E5C", "Sand", 0, 0, "canyon floor brown-sugar sand"),
    "SandBlock":  ("#E39A82", "Sandstone", 0, 0, "pink sandstone blocks (rail stone, footings, steps)"),
    "Timber":     ("#8A5A33", "WoodPlanks", 0, 0, "weathered timber"),
    "Rope":       ("#C9A46A", "Fabric", 0, 0, "hemp rope"),
    "PepRed":     ("#D9343A", "SmoothPlastic", 0, 0, "peppermint red (dam, roofs, flags, stripes)"),
    "MintWhite":  ("#FFF8F0", "SmoothPlastic", 0, 0, "peppermint white"),
    "CandyPink":  ("#FF6FA8", "Glass", 0, 0.25, "rock candy (Glass, Transparency 0.25, Reflectance 0.1)"),
    "CandyAmber": ("#FFB347", "Glass", 0, 0.25, "rock candy 2 (Glass, Transparency 0.25, Reflectance 0.1)"),
    "CandyCore":  ("#FF9EC8", "Neon", 1.5, 0, "faint neon core inside the crystals"),
    "Cactus":     ("#3E8E41", "SmoothPlastic", 0, 0, "saguaro green"),
    "Bubblegum":  ("#F78FB3", "SmoothPlastic", 0, 0, "lollipop swirl (Reflectance 0.05)"),
    "GumLemon":   ("#FFD84A", "SmoothPlastic", 0, 0, "gumball / gumdrop lemon"),
    "GumLime":    ("#9BDB4D", "SmoothPlastic", 0, 0, "gumball / gumdrop lime"),
    "GumCherry":  ("#E8304A", "SmoothPlastic", 0, 0, "gumball / gumdrop cherry"),
    "Apricot":    ("#F2B48A", "SmoothPlastic", 0, 0, "apricot paint (strata 4)"),
    "Water":      ("#3FB7C9", "Glass", 0, 0.4, "canyon turquoise"),
    "Foam":       ("#E6FAFF", "SmoothPlastic", 0, 0.2, "foam"),
    "PowderSugar": ("#FFF8F0", "Sand", 0, 0, "powdered-sugar dune caps"),
    "Iron":       ("#3B3A3F", "Metal", 0, 0, "lift frames, wheels, bands (accent, not in course.md)"),
    "Licorice":   ("#2B1D20", "SmoothPlastic", 0, 0, "licorice-black ropes, lettering, door/window holes (accent)"),
    "Window":     ("#3A2A30", "Glass", 0, 0, "dark window glass (accent)"),
    "Scrub":      ("#8FA35A", "Grass", 0, 0, "desert scrub (accent, sage between Cactus and Spring felt)"),
    "SunGold":    ("#FFD36B", "Neon", 2.0, 0, "sun disc (textures/sun_disc.png, alpha-cut)"),
    "CardMesa":   ("#C9A6BE", "SmoothPlastic", 0, 0, "distant-mesa card (textures/card_mesa.png, alpha-cut)"),
    "CardButte":  ("#D9A79A", "SmoothPlastic", 0, 0, "butte-spire card (textures/card_butte.png, alpha-cut)"),
    "CardArch":   ("#C9A6BE", "SmoothPlastic", 0, 0, "far-arch card (textures/card_far_arch.png, alpha-cut)"),
    "CardTwins":  ("#C9A6BE", "SmoothPlastic", 0, 0, "far-butte card (textures/card_twins.png, alpha-cut)"),
    "CardCloud":  ("#F7A1A6", "SmoothPlastic", 0, 0, "cloud-streak card (textures/card_cloud.png, alpha-cut)"),
    # pass 6 (art rework): weathered wood + brass, trading post, lanterns, ground dressing
    "TimberWeathered": ("#9C7B5C", "WoodPlanks", 0, 0, "sun-weathered timber (gondola tower, trading post, barrels)"),
    "Brass":      ("#C9973A", "Metal", 0, 0, "brass bolts, lantern caps, barrel bands (accent)"),
    "LanternGlow": ("#FFC46B", "Neon", 3.0, 0, "lantern Neon core (CastShadow off)"),
    "Canvas":     ("#F4E4C6", "Fabric", 0, 0, "awning canvas, cream stripe"),
    "CanvasRed":  ("#C8453B", "Fabric", 0, 0, "awning canvas, red stripe"),
    "ClayBrick":  ("#B65C3E", "Brick", 0, 0, "rounded clay-brick lane edging / curbs"),
    "RedDirt":    ("#B9643F", "Ground", 0, 0, "packed red canyon dirt (ground patches)"),
    "RedDirtLight": ("#C98055", "Ground", 0, 0, "lighter red dirt (ground patches, second tone)"),
    "Pebble":     ("#A9785F", "Pebble", 0, 0, "loose pebbles and fallen-rock chips"),
}
# material: (png, studs per texture repeat)
TEX = {
    "Strata": ("strata", STRATA_REPEAT),
    "MesaTop": ("sand_peach", 8.0),
    "FloorSand": ("sand_floor", 8.0),
    "SandBlock": ("sandstone_block", 4.0),
    "Timber": ("timber", 4.0),
    "Rope": ("rope", 2.0),
    "PepRed": ("concrete_red", 8.0),
    "MintWhite": ("concrete_white", 8.0),
    "CandyPink": ("crystal_pink", 4.0),
    "CandyAmber": ("crystal_amber", 4.0),
    "Cactus": ("cactus", 3.0),
    "PowderSugar": ("powder_sugar", 8.0),
    "SunGold": ("sun_disc", 1.0),
    "CardMesa": ("card_mesa", 1.0),
    "CardButte": ("card_butte", 1.0),
    "CardArch": ("card_far_arch", 1.0),
    "CardTwins": ("card_twins", 1.0),
    "CardCloud": ("card_cloud", 1.0),
    "TimberWeathered": ("timber_weathered", 4.0),
    "ClayBrick": ("clay_brick", 2.0),
    "RedDirt": ("red_dirt", 12.0),
    "RedDirtLight": ("red_dirt_light", 12.0),
}
CARDS = {"SunGold", "CardMesa", "CardButte", "CardArch", "CardTwins", "CardCloud"}
NO_SHADOW = CARDS | {"CandyCore", "Water", "Foam", "LanternGlow", "RedDirt", "RedDirtLight"}

lglib.MATS = MATS
lglib.TEX = TEX
lglib.CARD_MATS = set(CARDS)
lglib.EMIT_TEX = {"SunGold"}


def strata_uv(b):
    uv = b.loops.layers.uv.get("UVMap") or b.loops.layers.uv.new("UVMap")
    b.normal_update()
    k = 1.0 / STRATA_REPEAT
    for f in b.faces:
        n = f.normal
        horiz_x = abs(n.y) >= abs(n.x)
        for l in f.loops:
            c = l.vert.co
            u = c.x if horiz_x else c.y
            if abs(n.z) > 0.92:          # near-flat tops: stripe still follows height, U spread over both axes
                u = c.x + c.y
            w = STRATA_WAVE(c.x, c.y) if STRATA_WAVE else 0.0      # pass 6: gently wavy strata (0 at panel edges)
            l[uv].uv = (u * k, (c.z + STRATA_Y0 + w) * k)


def _uv_bmesh(b, mat):
    if mat == "Strata":
        strata_uv(b)
    elif mat in CARDS:
        if not b.loops.layers.uv.get("UVMap"):
            lglib.card_uv_bmesh(b)
    else:
        lglib.box_uv_bmesh(b, TEX.get(mat, (None, 4.0))[1])


lglib.uv_bmesh = _uv_bmesh


def finalize(pb, col, y0=0.0):
    global STRATA_Y0, STRATA_WAVE
    STRATA_Y0 = y0
    STRATA_WAVE = getattr(pb, "wave", None)
    try:
        return pb.finalize(col)
    finally:
        STRATA_WAVE = None


# ----------------------------------------------------------------------------- shared shape helpers
def smooth01(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ledge(zw, amp=1.0):
    """Strata ledge relief at WORLD height zw: each 6-stud band bulges toward its top lip, then steps back."""
    f = (zw / STRATA_BAND) % 1.0
    return amp * (0.25 + 0.75 * f ** 1.6)


def band_rows(z0, z1, y0, per_band=(0.0, 0.35, 0.7, 0.9, 0.97)):
    """Sorted local z values covering [z0, z1] with extra rows near every world band boundary (sharp ledges)."""
    zs = {z0, z1}
    b0 = math.floor((z0 + y0) / STRATA_BAND) - 1
    b1 = math.ceil((z1 + y0) / STRATA_BAND) + 1
    for b in range(b0, b1):
        for f in per_band:
            z = b * STRATA_BAND + f * STRATA_BAND - y0
            if z0 < z < z1:
                zs.add(z)
    return sorted(zs)


def nz(x, y, z, s=1.0, seed=0):
    from mathutils import noise
    return noise.noise(Vector((x * s + seed * 7.13, y * s + seed * 3.7, z * s)))


def grid_bm(cols, rows, fn):
    """bmesh quad grid; fn(i, j) -> Vector. cols/rows = vertex counts."""
    t = bmesh.new()
    V = [[t.verts.new(fn(i, j)) for i in range(cols)] for j in range(rows)]
    for j in range(rows - 1):
        for i in range(cols - 1):
            t.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
    return t, V
