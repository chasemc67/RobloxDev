"""Sugarloaf Canyon pass 6 piece generators (Blender bpy/bmesh): trading post, props, ground dressing, the per-hole merged
dressing (built from _cache/pass6_layout.json, written by sc_dress_pass6.py) and the reworked cliff kit
(sc_cliffs_pass6.py). registry() feeds sc_build_pass6.py.

Every prop builder is fn(pb, m) with m a Blender placement matrix, so the stand-alone kit piece (m = identity) and the
per-hole merges (m = world offset @ yaw @ scale) are the same geometry; sc_dress_pass6.py places members with the
stand-alone pieces' exported triangles (_cache/tris/<id>.npy) and the fitcheck's exact 0.15 test.
Blender coords: x east, y north (= Roblox -Z), z up. Front of a piece = Blender +Y = Roblox local -Z.
"""
import math, random, json
from pathlib import Path
import bmesh
from mathutils import Vector, Matrix
import sclib as L
from sc_pieces import Part, T, Rz, S, beam, add_faces_bm, crystal, sign_text, catenary, GUMS

SRC = Path(__file__).resolve().parent
LAYOUT6 = SRC / "_cache" / "pass6_layout.json"
TAU = math.tau


def place(x=0.0, y=0.0, z=0.0, yaw=0.0, s=1.0):
    return T(x, y, z) @ Rz(yaw) @ S(s, s, s)


# ============================================================================= props
def barrel(pb, m, kind="a"):
    """Weathered stave barrel 1.6 wide x 1.9 tall, two iron hoops + brass rivets; a = lidded, b = open, full of gumballs."""
    H = 1.9
    prof = [(0.62, 0.0), (0.74, 0.28), (0.8, 0.95), (0.74, 1.62), (0.62, H)]
    pb.lathe("TimberWeathered", prof, 10, matrix=m, smooth=False)
    for z, r in ((0.32, 0.765), (1.58, 0.765)):
        pb.lathe("Iron", [(r, z - 0.07), (r, z + 0.07)], 10, matrix=m, smooth=False)
    for k in range(3):
        a = TAU * k / 3 + 0.4
        pb.box("Brass", (0.08, 0.08, 0.08), loc=(0.8 * math.cos(a), 0.8 * math.sin(a), 0.95), matrix=m)
    if kind == "a":
        pb.cyl("Timber", 0.6, 0.6, 0.08, 10, loc=(0, 0, H + 0.02), matrix=m, smooth=False)
        pb.box("Iron", (0.5, 0.12, 0.06), loc=(0, 0, H + 0.09), matrix=m)
    else:
        rnd = random.Random(11)
        pb.cyl("Timber", 0.6, 0.6, 0.05, 10, loc=(0, 0, H - 0.18), matrix=m, smooth=False)
        for k, (x, y) in enumerate(((0, 0), (0.32, 0.12), (-0.28, 0.22), (0.05, -0.33), (-0.22, -0.2), (0.3, -0.25))):
            mat = ("GumCherry", "GumLemon", "GumLime", "Bubblegum")[k % 4]
            pb.sphere(mat, 0.22, loc=(x, y, H - 0.02 + rnd.uniform(-0.04, 0.08)), segs=8, rings=5, matrix=m)


def hanging_lantern(pb, m, s=1.0):
    """Iron-framed lantern, Neon core, brass cap; pivot = hook top, hangs down 1.3*s."""
    q = m @ S(s, s, s)
    pb.torus("Iron", 0.09, 0.025, 6, 3, loc=(0, 0, -0.09), rot=(90, 0, 0), matrix=q)
    pb.cyl("Brass", 0.12, 0.32, 0.22, 6, loc=(0, 0, -0.3), matrix=q, smooth=False)
    pb.box("Iron", (0.58, 0.58, 0.07), loc=(0, 0, -0.44), matrix=q)
    pb.box("Iron", (0.62, 0.62, 0.09), loc=(0, 0, -1.22), matrix=q)
    for sx in (-1, 1):
        for sy in (-1, 1):
            pb.box("Iron", (0.06, 0.06, 0.78), loc=(sx * 0.26, sy * 0.26, -0.83), matrix=q)
    pb.cyl("LanternGlow", 0.17, 0.17, 0.52, 6, loc=(0, 0, -0.83), matrix=q, smooth=False)
    pb.cyl("Window", 0.24, 0.24, 0.66, 4, loc=(0, 0, -0.83), rot=(0, 0, 45), matrix=q, smooth=False, caps=False)


def lantern_post(pb, m):
    """5.6-tall weathered post with a rope wrap, bracket arm and a hanging lantern (Neon core, CastShadow off)."""
    pb.box("SandBlock", (0.9, 0.9, 0.5), loc=(0, 0, 0.15), matrix=m)
    pb.box("TimberWeathered", (0.36, 0.36, 5.4), loc=(0, 0, 0.4 + 2.7), matrix=m)
    pb.cyl("Rope", 0.27, 0.27, 0.5, 8, loc=(0, 0, 1.6), matrix=m, smooth=False)
    pb.box("TimberWeathered", (0.26, 1.5, 0.26), loc=(0, 0.6, 5.35), matrix=m)
    beam(pb, "TimberWeathered", m @ Vector((0, 0.05, 4.6)), m @ Vector((0, 0.95, 5.25)), 0.18)
    pb.box("Brass", (0.12, 0.08, 0.12), loc=(0, 0.25, 5.35), matrix=m)
    hanging_lantern(pb, m @ T(0, 1.2, 5.22), 0.95)


def mini_cactus(pb, m, h, seed=0, lolli_r=None):
    """Low-poly lollipop saguaro (one swirl lollipop on top, one or two arms, gumball fruit). Base z=0, height h."""
    rnd = random.Random(seed)
    tr = max(0.28, h * 0.07)
    top = h * 0.68
    pb.tube("Cactus", [Vector((0, 0, -0.3)), Vector((0, 0, top))], [tr * 1.05, tr * 0.95], segs=6, matrix=m, caps=False,
            smooth=True)
    pb.sphere("Cactus", tr * 0.95, loc=(0, 0, top), segs=6, rings=3, matrix=m)
    for k in range(1 + (seed % 2)):
        side = 1 if k == 0 else -1
        z0 = top * rnd.uniform(0.35, 0.5)
        reach = h * 0.2
        up = h * rnd.uniform(0.16, 0.24)
        pts = [Vector((0, 0, z0)), Vector((side * reach, 0, z0 + 0.1)), Vector((side * reach, 0, z0 + up))]
        mm = m @ Rz(rnd.uniform(-30, 30))
        pb.tube("Cactus", pts, tr * 0.68, segs=5, matrix=mm, caps=False, smooth=True)
        pb.sphere("Cactus", tr * 0.68, loc=pts[-1], segs=5, rings=3, matrix=mm)
        pb.sphere(GUMS[(seed + k) % 3], tr * 0.5, loc=pts[-1] + Vector((0, 0, tr * 0.75)), segs=5, rings=3, matrix=mm)
    rr = lolli_r or max(0.55, h * 0.16)
    lm = m @ T(0, 0, top + tr * 0.6 + rr * 1.05) @ Rz(rnd.uniform(-40, 40))
    swirl_disc(pb, lm, rr)
    pb.cyl("MintWhite", 0.07, 0.07, rr * 1.1, 4, loc=(0, 0, -rr * 0.95), matrix=lm, smooth=False)


def swirl_disc(pb, m, R_, thick=None):
    """Cheap swirl lollipop: 8-sector disc alternating Bubblegum / MintWhite on both faces + rim (faces +-Y)."""
    th = thick or max(0.18, R_ * 0.22)
    sect = 8
    for side in (1, -1):
        y = side * th / 2
        for i in range(sect):
            a0, a1 = TAU * i / sect + 0.5, TAU * (i + 1) / sect + 0.5
            v = [(0, y, 0), (R_ * math.cos(a0), y, R_ * math.sin(a0)), (R_ * 0.55 * math.cos(a1 + 0.6), y,
                                                                         R_ * 0.55 * math.sin(a1 + 0.6)),
                 (R_ * math.cos(a1), y, R_ * math.sin(a1))]
            f = [(0, 1, 2), (2, 1, 3)] if side < 0 else [(2, 1, 0), (3, 1, 2)]
            add_faces_bm(pb, "Bubblegum" if i % 2 else "MintWhite", v, f, matrix=m)
    pb.cyl("Bubblegum", R_, R_, th, sect, matrix=m @ Matrix.Rotation(math.radians(90), 4, "X"), caps=False, smooth=True)


def lollipop_cactus_cluster(pb, m):
    """3 low-poly lollipop cacti (6.4 / 4.6 / 3.2 tall) + gumball pebbles; footprint radius ~2.4."""
    mini_cactus(pb, m @ T(0.0, 0.0, 0.0), 6.4, seed=3)
    mini_cactus(pb, m @ T(1.5, -0.9, 0.0) @ Rz(70), 4.6, seed=6)
    mini_cactus(pb, m @ T(-1.3, -0.8, 0.0) @ Rz(-50), 3.2, seed=9)
    for k, (x, y) in enumerate(((0.7, 1.2), (-0.9, 0.9), (1.9, 0.6))):
        pb.sphere(GUMS[k % 3], 0.24, loc=(x, y, 0.15), segs=6, rings=4, matrix=m)


def rock_candy_cluster(pb, m):
    """Pink/amber rock-candy crystals (tallest 3.4) on a striped rock, footprint radius ~1.8."""
    pb.rock("Strata", (2.6, 2.2, 0.9), loc=(0, 0, -0.15), seed=21, amp=0.22, ico=2, matrix=m)
    rnd = random.Random(5)
    for i, (x, y, Lc, tilt) in enumerate(((0, 0, 3.4, 0), (0.7, 0.3, 2.3, 26), (-0.6, 0.4, 2.0, 30), (0.2, -0.7, 1.7, 34),
                                         (-0.5, -0.5, 1.4, 38))):
        a = math.atan2(y, x) if (x or y) else 0.0
        mm = m @ T(x, y, 0.35) @ Rz(math.degrees(a)) @ Matrix.Rotation(math.radians(tilt), 4, "Y") @ Rz(rnd.uniform(0, 60))
        crystal(pb, mm, Lc, Lc * 0.15, "CandyPink" if i % 3 != 1 else "CandyAmber", core=(i == 0))


def gumdrop_shrub(pb, m, kind="a"):
    """Round desert shrub (Scrub) dotted with gumdrop berries; a 1.5 tall, b 1.9 tall + agave spikes, c low 1.2 x 3."""
    rnd = random.Random({"a": 31, "b": 37, "c": 41}[kind])
    if kind == "a":
        lobes = [(0, 0, 0.7, 1.0), (0.55, 0.2, 0.45, 0.7), (-0.5, 0.25, 0.45, 0.65), (0.05, -0.55, 0.5, 0.7)]
    elif kind == "b":
        lobes = [(0, 0, 0.9, 1.0), (0.7, -0.2, 0.55, 0.75)]
    else:
        lobes = [(0, 0, 0.75, 0.6), (0.9, 0.3, 0.6, 0.5), (-0.9, -0.2, 0.6, 0.5), (0.2, 0.8, 0.5, 0.45)]
    for k, (x, y, r, hz) in enumerate(lobes):
        pb.rock("Scrub", (r * 2.0, r * 2.0, hz * 1.9), loc=(x, y, -0.15), seed=rnd.randint(0, 99), amp=0.16, ico=2,
                matrix=m, smooth=True)
        for j in range(2 if kind != "c" else 1):
            a = rnd.uniform(0, TAU)
            px, py, pz = x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8, hz * 0.95 + rnd.uniform(-0.15, 0.1)
            gm = m @ T(px, py, pz)
            pb.lathe(GUMS[(k + j) % 3] if kind != "b" else "Bubblegum",
                     [(0.17, 0), (0.15, 0.12), (0.08, 0.24), (0, 0.27)], 6, matrix=gm, smooth=True)
    if kind == "b":
        for k in range(5):
            a = TAU * k / 5 + 0.3
            tip = Vector((math.cos(a) * 0.9, math.sin(a) * 0.9, 1.9))
            beam(pb, "Cactus", m @ Vector((math.cos(a) * 0.2, math.sin(a) * 0.2, 0.5)), m @ tip, 0.12)


def boulder_scatter(pb, m):
    """Three striped boulders (2.2 / 1.4 / 0.9 tall), footprint radius ~2.5."""
    pb.rock("Strata", (3.0, 2.5, 2.4), loc=(0, 0, -0.3), seed=51, amp=0.2, ico=2, matrix=m)
    pb.rock("Strata", (1.9, 1.6, 1.6), loc=(1.75, -0.9, -0.2), seed=53, amp=0.22, ico=2, matrix=m)
    pb.rock("Strata", (1.2, 1.1, 1.0), loc=(-1.6, -0.6, -0.15), seed=57, amp=0.25, ico=1, matrix=m)


def fallen_rock_scatter(pb, m):
    """Tumbled slabs and chips (<= 0.8 tall) - safe right outside the rails; footprint radius ~2.0."""
    rnd = random.Random(61)
    for k, (x, y, sx, sy, sz) in enumerate(((0, 0, 1.6, 1.1, 0.75), (1.3, 0.5, 1.0, 0.8, 0.5), (-1.2, 0.4, 0.9, 0.7, 0.45),
                                            (0.4, -1.1, 0.8, 0.6, 0.4), (-0.6, -0.9, 0.6, 0.5, 0.35))):
        pb.rock("Strata" if k % 2 == 0 else "Pebble", (sx, sy, sz * 1.4), loc=(x, y, -0.12), rot=(0, 0, rnd.uniform(0, 180)),
                seed=63 + k, amp=0.28, ico=0 if k else 1, matrix=m)


def pebble(pb, m, r, mat="Pebble"):
    """Flattened octahedron pebble (8 tris)."""
    v = [(r, 0, 0.0), (0, r * 0.8, 0.0), (-r * 0.9, 0, 0.0), (0, -r * 0.85, 0.0), (0, 0, r * 0.7), (0, 0, -r * 0.3)]
    f = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (1, 0, 5), (2, 1, 5), (3, 2, 5), (0, 3, 5)]
    add_faces_bm(pb, mat, v, f, matrix=m)


def pebble_scatter(pb, m):
    rnd = random.Random(71)
    for k in range(10):
        a, d = rnd.uniform(0, TAU), 1.4 * math.sqrt(rnd.random())
        pebble(pb, m @ T(math.cos(a) * d, math.sin(a) * d, 0.05) @ Rz(rnd.uniform(0, 360)), rnd.uniform(0.12, 0.3),
               "Pebble" if k % 3 else "Strata")


def brick(pb, m, length=1.2, w=0.7, h=0.45, mat="ClayBrick"):
    """Rounded clay brick: 6-vertex rounded-top profile (in local XZ) extruded along local Y (20 tris)."""
    hw = w / 2
    prof = [(-hw, 0.0), (hw, 0.0), (hw, h * 0.62), (hw * 0.55, h), (-hw * 0.55, h), (-hw, h * 0.62)]
    sec = [[Vector((x, y, z)) for x, z in prof] for y in (-length / 2, length / 2)]
    pb.loft(mat, sec, matrix=m, smooth=False, caps=True)


def clay_brick_edging(pb, m):
    """8-stud straight curb: 6 rounded bricks 1.25 long with 0.1 joints (local Y = run direction)."""
    for k in range(6):
        brick(pb, m @ T(0, -3.75 + k * 1.35, 0), 1.25)


def dirt_patch(pb, m, kind="a"):
    """Flat irregular red-dirt decal (hand placement on flat ground): 12-gon fan, light rim ring, 0.08 thick look."""
    rnd = random.Random({"a": 81, "b": 83}[kind])
    R0 = {"a": 3.2, "b": 4.6}[kind]
    n = 12
    rad = [R0 * (0.75 + 0.35 * rnd.random()) for _ in range(n)]
    inner = [(rad[i] * 0.68 * math.cos(TAU * i / n), rad[i] * 0.68 * math.sin(TAU * i / n), 0.06) for i in range(n)]
    outer = [(rad[i] * math.cos(TAU * i / n + 0.1), rad[i] * math.sin(TAU * i / n + 0.1), 0.03) for i in range(n)]
    add_faces_bm(pb, "RedDirt", [(0, 0, 0.06)] + inner, [(0, i + 1, (i + 1) % n + 1) for i in range(n)], matrix=m)
    add_faces_bm(pb, "RedDirtLight", inner + outer, [(i, n + i, n + (i + 1) % n, (i + 1) % n) for i in range(n)], matrix=m)


# ============================================================================= trading post (H1 tee)
def trading_post_deck(pb, m=None):
    """Boardwalk trading post beside the H1 tee. Local (Blender): deck 22 wide (x) x 10 deep (y), front = +y (faces
    the lane), store-front wall along the back (y -5), three striped canvas awnings from the wall to four rope-wrapped
    front posts, plank rails on the front/sides (front entry gap at x -2..+2... and stairs), sign, barrels, crates,
    hanging lanterns. Deck top 0.8; awning eaves 5.6, wall 7.0, sign top 8.2."""
    m = m or Matrix.Identity(4)
    W_, D_ = 22.0, 10.0
    top = 0.8
    # deck: plank top (TimberWeathered texture runs along x), joists, footings
    pb.box("TimberWeathered", (W_, D_, 0.3), loc=(0, 0, top - 0.15), matrix=m)
    pb.box("Timber", (W_, 0.3, 0.5), loc=(0, D_ / 2 - 0.15, top - 0.55), matrix=m)        # front fascia
    for x in (-10.6, -3.6, 3.6, 10.6):
        for y in (-4.4, 0.0, 4.4):
            pb.box("SandBlock", (0.8, 0.8, 0.5), loc=(x, y, 0.1), matrix=m)
    # two entry steps in the middle of the front edge (towards the tee / lane)
    for k, (z, dy) in enumerate(((0.55, 0.9), (0.3, 1.8))):
        pb.box("TimberWeathered", (4.0, 0.9, 0.25), loc=(0, D_ / 2 + dy - 0.45, z - 0.12), matrix=m)
        pb.box("Timber", (4.0, 0.15, z), loc=(0, D_ / 2 + dy - 0.05, z / 2 - 0.12), matrix=m)
    # store-front wall (back), door + window holes, trim
    pb.box("TimberWeathered", (W_, 0.4, 6.2), loc=(0, -D_ / 2 + 0.2, top + 3.1), matrix=m)
    for x in (-6.5, 6.5):
        pb.box("Window", (3.0, 0.1, 2.0), loc=(x, -D_ / 2 + 0.43, top + 2.6), matrix=m)
        pb.box("Timber", (3.4, 0.2, 0.2), loc=(x, -D_ / 2 + 0.5, top + 1.5), matrix=m)
        pb.box("Timber", (3.4, 0.2, 0.2), loc=(x, -D_ / 2 + 0.5, top + 3.7), matrix=m)
    pb.box("Licorice", (2.4, 0.1, 3.6), loc=(0, -D_ / 2 + 0.43, top + 1.8), matrix=m)
    pb.box("Timber", (2.8, 0.22, 0.25), loc=(0, -D_ / 2 + 0.5, top + 3.75), matrix=m)
    # false-front parapet + sign board
    pb.box("TimberWeathered", (12.0, 0.4, 1.4), loc=(0, -D_ / 2 + 0.2, top + 6.9), matrix=m)
    pb.box("MintWhite", (10.0, 0.15, 1.3), loc=(0, -D_ / 2 + 0.48, top + 6.75), matrix=m)
    sign_text(pb, "TRADING POST", 0.95, m @ T(0, -D_ / 2 + 0.6, top + 6.33) @ Rz(180), mat="PepRed")   # reads from +Y
    # front posts (rope wraps) + header beam
    posts = (-10.6, -3.6, 3.6, 10.6)
    eave = 5.6
    for x in posts:
        pb.box("TimberWeathered", (0.5, 0.5, eave + 0.3), loc=(x, D_ / 2 - 0.4, top + (eave + 0.3) / 2 - 0.3), matrix=m)
        pb.cyl("Rope", 0.36, 0.36, 0.55, 8, loc=(x, D_ / 2 - 0.4, top + 1.2), matrix=m, smooth=False)
        pb.box("Brass", (0.12, 0.1, 0.12), loc=(x, D_ / 2 - 0.12, top + eave - 0.6), matrix=m)
    pb.box("Timber", (W_, 0.4, 0.4), loc=(0, D_ / 2 - 0.4, top + eave), matrix=m)
    # three striped canvas awnings: sloped sheet from the wall (z 7.0) down to the header (z eave + 0.2),
    # 8 alternating red / cream stripes each, scalloped valance on the front edge
    for a0, a1 in ((-11.0, -3.8), (-3.4, 3.4), (3.8, 11.0)):
        n = 8
        for k in range(n):
            xa, xb = a0 + (a1 - a0) * k / n, a0 + (a1 - a0) * (k + 1) / n
            mat = "CanvasRed" if k % 2 == 0 else "Canvas"
            zb, zf = top + 6.2, top + eave + 0.25
            yb, yf = -D_ / 2 + 0.45, D_ / 2 + 0.3
            v = [(xa, yb, zb), (xb, yb, zb), (xb, yf, zf), (xa, yf, zf)]
            add_faces_bm(pb, mat, v, [(0, 1, 2, 3), (3, 2, 1, 0)], matrix=m)
            xm = (xa + xb) / 2                                          # scallop tab
            tv = [(xa, yf, zf), (xb, yf, zf), (xm, yf + 0.05, zf - 0.55)]
            add_faces_bm(pb, mat, tv, [(0, 1, 2), (2, 1, 0)], matrix=m)
    # plank railing along both short sides and the front (gap at the steps x -2..2)
    rail_h = 1.1
    def rail_run(a, b):
        a, b = Vector(a), Vector(b)
        L_ = (b - a).length
        nposts = max(1, int(round(L_ / 2.4)))
        for i in range(nposts + 1):
            p = a.lerp(b, i / nposts)
            pb.box("TimberWeathered", (0.22, 0.22, rail_h), loc=(p.x, p.y, top + rail_h / 2), matrix=m)
        for z in (top + 0.5, top + rail_h - 0.08):
            beam(pb, "TimberWeathered", m @ (a + Vector((0, 0, z))), m @ (b + Vector((0, 0, z))), 0.14, 0.32)
    rail_run((-W_ / 2 + 0.2, -D_ / 2 + 0.5, 0), (-W_ / 2 + 0.2, D_ / 2 - 0.7, 0))
    rail_run((W_ / 2 - 0.2, -D_ / 2 + 0.5, 0), (W_ / 2 - 0.2, D_ / 2 - 0.7, 0))
    rail_run((-10.3, D_ / 2 - 0.15, 0), (-2.1, D_ / 2 - 0.15, 0))
    rail_run((2.1, D_ / 2 - 0.15, 0), (10.3, D_ / 2 - 0.15, 0))
    # goods on the deck: barrels (gumball + lidded), crates, a hanging lantern under each awning
    deck = m @ T(0, 0, top)
    barrel(pb, deck @ T(-8.4, -3.2, 0), "b")
    barrel(pb, deck @ T(-6.7, -3.5, 0) @ Rz(40), "a")
    barrel(pb, deck @ T(8.6, -3.1, 0) @ Rz(15), "b")
    barrel(pb, deck @ T(-9.2, 2.6, 0) @ Rz(70), "a")
    for (x, y, s, yaw) in ((7.0, -3.3, 1.2, 10), (6.95, -3.3, 0.8, 35), (9.3, 2.8, 1.0, -20)):
        c = deck @ T(x, y, 0) @ Rz(yaw)
        z0 = 0.0 if s > 0.9 else 1.2
        pb.box("Timber", (s, s, s), loc=(0, 0, z0 + s / 2), matrix=c)
        pb.box("TimberWeathered", (s * 1.02, s * 0.2, s * 0.8), loc=(0, 0, z0 + s / 2), matrix=c)
    for x in (-7.2, 0.0, 7.2):
        hanging_lantern(pb, m @ T(x, D_ / 2 - 1.6, top + eave + 0.3), 0.9)
    return pb


# ============================================================================= registry
def _single(name, fn, y0=18.0, role="kit piece"):
    def build():
        pb = Part(name, y0=y0, role=role)
        fn(pb, Matrix.Identity(4))
        return [pb]
    return build


KIT = [
    ("trading_post_deck", lambda pb, m: trading_post_deck(pb, m),
     "Trading-post boardwalk for the H1 tee: 22 x 10 weathered plank deck (top 0.8) with two entry steps, store-front "
     "wall + 'TRADING POST' sign, three red/cream striped canvas awnings on four rope-wrapped posts, plank rails, "
     "barrels (lidded + gumball), crates and three hanging lanterns (Neon cores, CastShadow off). Front = local -Z."),
    ("barrel_a", lambda pb, m: barrel(pb, m, "a"), "Lidded weathered barrel 1.6 x 1.9, iron hoops, brass rivets."),
    ("barrel_b", lambda pb, m: barrel(pb, m, "b"), "Open weathered barrel 1.6 x 1.9 heaped with gumballs."),
    ("lantern_post", lantern_post,
     "5.6-tall rope-wrapped post with bracket arm and hanging lantern (LanternGlow Neon core, CastShadow off)."),
    ("lantern_hanging", lambda pb, m: hanging_lantern(pb, m @ T(0, 0, 1.4), 1.0),
     "Hanging lantern 0.6 x 1.4 (iron frame, brass cap, LanternGlow Neon core - CastShadow off); pivot = base centre, "
     "hook at +1.4 (hang under eaves/arms)."),
    ("lollipop_cactus_cluster", lollipop_cactus_cluster, "Three low-poly lollipop saguaros (6.4 / 4.6 / 3.2) + gumballs."),
    ("rock_candy_cluster", rock_candy_cluster, "Rock-candy crystals (tallest 3.4) on a striped rock."),
    ("gumdrop_shrub_a", lambda pb, m: gumdrop_shrub(pb, m, "a"), "Round scrub shrub 1.5 tall with gumdrop berries."),
    ("gumdrop_shrub_b", lambda pb, m: gumdrop_shrub(pb, m, "b"), "Taller scrub 1.9 with pink gumdrops and agave spikes."),
    ("gumdrop_shrub_c", lambda pb, m: gumdrop_shrub(pb, m, "c"), "Low spreading scrub 1.2 x 3 with gumdrop berries."),
    ("boulder_scatter", boulder_scatter, "Three striped boulders (2.2 / 1.4 / 0.9 tall)."),
    ("fallen_rock_scatter", fallen_rock_scatter, "Tumbled striped slabs and pebble chips, <= 0.8 tall."),
    ("red_dirt_patch_a", lambda pb, m: dirt_patch(pb, m, "a"), "Flat red-dirt decal patch ~6 across (two tones)."),
    ("red_dirt_patch_b", lambda pb, m: dirt_patch(pb, m, "b"), "Flat red-dirt decal patch ~9 across (two tones)."),
    ("pebble_scatter", pebble_scatter, "Clump of 10 low-poly pebbles within r 1.5 (8 tris each)."),
    ("clay_brick_edging", clay_brick_edging,
     "8-stud straight lane-edging curb: 6 rounded clay bricks 1.25 x 0.7 x 0.45 (local Z = run direction)."),
]
KIT_FN = {k: fn for k, fn, _ in KIT}
PLANT_KINDS = ("lollipop_cactus_cluster", "gumdrop_shrub_a", "gumdrop_shrub_b", "gumdrop_shrub_c")


def hole_piece(name, part):
    """Per-hole merged dressing from _cache/pass6_layout.json: part = props | plants | ground."""
    def build():
        lay = json.loads(LAYOUT6.read_text())
        hole = lay["holes"][name.split("_")[0]]
        piv = hole["pivot"]
        pb = Part(name, y0=piv[1], role=f"merged per-hole {part} ({hole['name']})")
        if part in ("props", "plants"):
            for mem in hole["members"]:
                if (mem["kind"] in PLANT_KINDS) != (part == "plants"):
                    continue
                p = mem["pos"]
                m = place(p[0] - piv[0], -(p[2] - piv[2]), p[1] - piv[1], mem["yaw"], mem.get("scale", 1.0))
                KIT_FN[mem["kind"]](pb, m)
        else:
            g = hole["ground"]
            for mat, mesh in g["meshes"].items():          # dirt carpet: verts (Roblox world) + faces
                verts = [(v[0] - piv[0], -(v[2] - piv[2]), v[1] - piv[1]) for v in mesh["verts"]]
                add_faces_bm(pb, mat, verts, [tuple(f) for f in mesh["faces"]])
            for b in g["bricks"]:
                p = b["pos"]
                brick(pb, place(p[0] - piv[0], -(p[2] - piv[2]), p[1] - piv[1], b["yaw"]), b["len"])
            for pbl in g["pebbles"]:
                p = pbl["pos"]
                pebble(pb, place(p[0] - piv[0], -(p[2] - piv[2]), p[1] - piv[1], pbl["yaw"]), pbl["r"], pbl["mat"])
        return [pb]
    return build


def registry():
    out = []
    for k, fn, notes in KIT:
        out.append(dict(id_=k, group="hole_dressing" if k == "trading_post_deck" else "dressing_kit",
                        build=_single(k, fn), notes=notes, cast_shadow_off=("LanternGlow", "RedDirt", "RedDirtLight")))
    if LAYOUT6.exists():
        lay = json.loads(LAYOUT6.read_text())
        for hid, hole in lay["holes"].items():
            for part in ("props", "plants", "ground"):
                if not hole["counts"].get(part):
                    continue
                name = f"{hid}_dress_{part}" if part != "ground" else f"{hid}_ground"
                out.append(dict(id_=name, group="hole_dressing", build=hole_piece(name, part),
                                notes=f"H{hole['number']} {hole['name']}: merged per-material {part} dressing "
                                      f"({hole['counts'][part]} members/elements) baked at world offsets.",
                                origin=f"hole tee world position {hole['pivot']} (geometry baked at world offsets, yaw 0)",
                                cast_shadow_off=("LanternGlow", "RedDirt", "RedDirtLight"), preview="world"))
    try:
        import sc_cliffs_pass6 as C
        out += C.registry()
    except ImportError:
        pass
    return out
