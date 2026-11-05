"""Pass 2 variety props for the dressing layouts: tree shapes, toadstools, bushes, ground cover, lantern spans."""
import math, random
from mathutils import Vector, Matrix
from registry import prop
from lglib import M, TAU
from props_p2p3 import mushroom


# ============================================================================ trees
def canopy(pb, blobs, mats, seed, ico=2, squash=0.82):
    for k, (p, r) in enumerate(blobs):
        pb.rock(mats[k % len(mats)], (r * 2, r * 2, r * 2 * squash), loc=Vector(p) - Vector((0, 0, r * squash * 0.6)),
                seed=seed * 7 + k, amp=0.17, ico=ico if r < 3.0 else ico + 1, flat_bottom=False, smooth=True)


def trunk(pb, mat, h, r, seed, lean=(0.15, 0.05), roots=5, flare=2.0):
    rnd = random.Random(seed)
    pb.tube(mat, [(0, 0, -0.3), (lean[0] * 0.5, lean[1] * 0.5, h * 0.35), (lean[0], lean[1], h * 0.7),
                  (lean[0] * 0.6, lean[1], h)], [r * 1.45, r, r * 0.8, r * 0.5], 10, wobble=0.12, seed=seed)
    for k in range(roots):
        a = TAU * k / roots + rnd.uniform(-0.3, 0.3)
        c, s = math.cos(a), math.sin(a)
        L = r * flare * rnd.uniform(0.9, 1.3)
        pb.tube(mat, [(c * r * 0.6, s * r * 0.6, 0.9), (c * r * 1.3, s * r * 1.3, 0.25), (c * (r + L), s * (r + L), -0.2)],
                [r * 0.5, r * 0.33, r * 0.12], 5, wobble=0.1, seed=seed + k)


def branch(pb, mat, z, ang, L, up, r):
    a = math.radians(ang)
    p0 = Vector((0, 0, z))
    d = Vector((math.cos(a), math.sin(a), 0))
    p1 = p0 + d * L * 0.55 + Vector((0, 0, up * 0.45))
    p2 = p0 + d * L + Vector((0, 0, up))
    pb.tube(mat, [p0, p1, p2], [r, r * 0.65, r * 0.3], 6, wobble=0.1)
    return p2


@prop("maple_tree_round", ["all"], "P2", target=[12, 14, 12], group="nature",
      notes="Broad round red maple (Ember red / Pumpkin canopy, leaf textures). Dressing tree; yaw/scale 0.8-1.25.")
def maple_round(pb):
    trunk(pb, "RootBark", 8.0, 0.7, 11)
    tips = [branch(pb, "RootBark", 5.5 + k * 0.6, a, 3.6, 2.6, 0.4) for k, a in enumerate((15, 135, 250, 320))]
    blobs = [((0, 0, 11.6), 3.6), ((3.2, 0.6, 10.0), 2.8), ((-3.0, 1.0, 10.2), 2.9), ((0.6, -3.2, 10.0), 2.7),
             ((-0.8, 3.2, 9.8), 2.6), ((2.4, -2.2, 12.2), 2.3), ((-2.4, -1.8, 12.0), 2.4), ((0.4, 1.2, 13.6), 2.4),
             ((2.4, 2.6, 11.6), 2.0)]
    canopy(pb, blobs, ["MapleRed", "Pumpkin", "MapleRed", "MapleRed"], 11)


@prop("maple_tree_tall", ["all"], "P2", target=[8, 19, 8], group="nature",
      notes="Tall layered red maple for framing tee views; narrow footprint.")
def maple_tall(pb):
    trunk(pb, "RootBark", 14.0, 0.55, 12, lean=(-0.2, 0.1), roots=4)
    for k, (z, a) in enumerate(((7.0, 30), (8.5, 160), (10.0, 270), (11.5, 80))):
        branch(pb, "RootBark", z, a, 2.6, 1.8, 0.3)
    blobs = []
    for tier, (z, R_, n, r) in enumerate(((9.5, 2.6, 5, 2.2), (12.5, 2.0, 4, 2.0), (15.2, 1.2, 3, 1.8), (17.4, 0, 1, 1.6))):
        for k in range(n):
            a = TAU * k / n + tier * 0.7
            blobs.append(((math.cos(a) * R_, math.sin(a) * R_, z), r))
    canopy(pb, blobs, ["MapleRed", "MapleRed", "Pumpkin"], 12)


@prop("oak_tree_orange", ["all"], "P2", target=[14, 13, 14], group="nature",
      notes="Wide spreading autumn oak (Pumpkin / Harvest gold canopy) with a thick flared trunk.")
def oak_orange(pb):
    trunk(pb, "RootBark", 6.5, 1.05, 13, lean=(0.1, -0.1), roots=6, flare=2.2)
    for k, a in enumerate((0, 72, 144, 216, 288)):
        branch(pb, "RootBark", 4.8 + (k % 2) * 0.6, a + 10, 4.6, 2.4, 0.55)
    blobs = []
    for k in range(7):
        a = TAU * k / 7 + 0.3
        blobs.append(((math.cos(a) * 4.4, math.sin(a) * 4.4, 8.6 + (k % 2) * 0.6), 2.9))
    blobs += [((0, 0, 10.2), 3.6), ((1.5, 1.0, 11.6), 2.6), ((-1.6, -1.2, 11.4), 2.6)]
    canopy(pb, blobs, ["Pumpkin", "Gold", "Pumpkin", "MapleRed"], 13, squash=0.7)


@prop("maple_tree_lanterns", ["all"], "P2", target=[11, 15, 11], group="nature",
      notes="Red maple with two long low boughs, each hanging a paper lantern (Glow core) about 6 studs up; "
            "the lanterns hang toward local +X and -X, so yaw the tree to swing them beside (not over) the felt.")
def maple_lanterns(pb):
    trunk(pb, "RootBark", 9.0, 0.62, 14)
    for sx, paper in ((1, "Paper"), (-1, "PaperOrange")):
        p2 = branch(pb, "RootBark", 6.0, 0 if sx > 0 else 180, 4.6, 1.4, 0.36)
        pb.tube("RootBark", [p2 + Vector((0, 0, 0.05)), p2 + Vector((0, 0, -0.65))], 0.03, 4, smooth=False)
        pb.lantern(1.2, loc=p2 + Vector((0, 0, -1.85)), paper=paper)
    for a in (100, 260):
        branch(pb, "RootBark", 7.0, a, 3.0, 2.6, 0.34)
    blobs = [((0, 0, 12.4), 3.2), ((2.6, 1.0, 10.8), 2.6), ((-2.6, 1.2, 11.0), 2.6), ((0.8, -2.6, 10.8), 2.5),
             ((-1.0, 2.6, 10.6), 2.4), ((2.0, -1.4, 13.0), 2.0), ((-2.0, -1.4, 12.8), 2.2), ((0.3, 0.5, 14.4), 2.0),
             ((4.2, 0.2, 9.0), 1.8), ((-4.2, 0.0, 9.0), 1.8)]
    canopy(pb, blobs, ["MapleRed", "Pumpkin", "MapleRed"], 14)


@prop("maple_tree_overhang", ["all"], "P2", target=[13, 15, 10], group="nature",
      notes=("Leaning red maple whose canopy reaches ~7 studs toward local +X, with two lanterns hanging from the "
             "outer bough. Every part on the +X side stays >= 7.3 above the base so it may overhang felt/rails "
             "(fitcheck: >= 6.5 over felt). Yaw local +X toward the lane to frame tee views from above."))
def maple_overhang(pb):
    pb.tube("RootBark", [(-0.6, 0, -0.3), (-0.4, 0, 3.0), (0.4, 0.1, 6.5), (1.8, 0.0, 9.0), (3.4, 0, 10.6)],
            [0.95, 0.7, 0.58, 0.45, 0.3], 10, wobble=0.12, seed=16)
    for k in range(5):
        a = TAU * k / 5 + 0.3
        c, s_ = math.cos(a), math.sin(a)
        pb.tube("RootBark", [(-0.6 + c * 0.5, s_ * 0.5, 0.9), (-0.6 + c * 1.1, s_ * 1.1, 0.25), (-0.6 + c * 2.3, s_ * 2.3, -0.2)],
                [0.42, 0.28, 0.1], 5, wobble=0.1, seed=16 + k)
    b1 = [Vector((1.8, 0.0, 9.0)), Vector((3.8, 0.4, 10.0)), Vector((6.2, 0.6, 10.3))]
    pb.tube("RootBark", b1, [0.32, 0.22, 0.1], 6, wobble=0.1)
    pb.tube("RootBark", [Vector((0.4, 0.1, 6.5)), Vector((-1.6, 0.8, 9.0)), Vector((-2.4, 1.2, 10.6))], [0.3, 0.2, 0.1], 6)
    for (x, y, paper) in ((4.6, 0.5, "Paper"), (6.0, 0.6, "PaperOrange")):
        pb.tube("RootBark", [(x, y, 10.15), (x, y, 9.55)], 0.03, 4, smooth=False)
        pb.lantern(1.2, loc=(x, y, 9.55 - 1.2), paper=paper)
    blobs = [((3.6, 0.0, 12.6), 3.0), ((6.4, 0.8, 12.3), 2.4), ((5.0, -2.0, 12.4), 2.3), ((4.6, 2.4, 12.6), 2.2),
             ((1.4, 0.4, 13.6), 2.8), ((-1.6, 0.8, 12.4), 2.6), ((-0.6, -1.6, 13.4), 2.2), ((2.4, 0.6, 15.0), 2.2),
             ((7.6, 0.0, 11.8), 1.7)]
    canopy(pb, blobs, ["MapleRed", "Pumpkin", "MapleRed", "MapleRed", "Pumpkin"], 16)


@prop("maple_sapling", ["all"], "P3", target=[5, 7, 5], group="nature",
      notes="Young maple for mid-ground filling between bushes and big trees.")
def sapling(pb):
    trunk(pb, "RootBark", 4.5, 0.28, 15, roots=3, flare=1.6)
    blobs = [((0, 0, 5.8), 1.8), ((1.3, 0.4, 4.9), 1.4), ((-1.2, 0.5, 5.0), 1.4), ((0.2, -1.3, 4.8), 1.3),
             ((0.1, 0.4, 6.8), 1.2)]
    canopy(pb, blobs, ["Pumpkin", "MapleRed", "Gold"], 15)


@prop("tree_backdrop_cluster", ["all"], "P3", target=[14, 15, 9], group="nature",
      notes="Cheap (~1k tris) clump of three autumn trees for the far background ring (>= 25 studs from felt).")
def backdrop(pb):
    for k, (x, y, h, r) in enumerate(((-4.0, 0.5, 8.5, 0.5), (0.5, -0.6, 10.0, 0.6), (4.2, 0.8, 7.5, 0.45))):
        pb.tube("RootBark", [(x, y, -0.3), (x + 0.1, y, h * 0.5), (x - 0.1, y, h)], [r * 1.3, r, r * 0.6], 7, wobble=0.1,
                seed=k)
    rnd = random.Random(17)
    mats = ["MapleRed", "Pumpkin", "Gold", "MapleRed", "Pumpkin", "MapleRed"]
    blobs = []
    for k, (x, h) in enumerate(((-4.0, 8.5), (0.5, 10.0), (4.2, 7.5))):
        for j in range(3):
            a = TAU * j / 3 + k
            blobs.append(((x + math.cos(a) * 1.6, math.sin(a) * 1.4, h + 1.6 + (j == 0) * 1.2), 2.5 + rnd.uniform(-0.3, 0.3)))
    for k, (p, r) in enumerate(blobs):
        pb.rock(mats[k % len(mats)], (r * 2, r * 2, r * 1.6), loc=Vector(p) - Vector((0, 0, r * 0.5)), seed=170 + k,
                amp=0.17, ico=2, flat_bottom=False, smooth=True)


# ============================================================================ toadstools
@prop("toadstool_tall", ["all"], "P2", target=[2.8, 3.6, 2.8], group="nature",
      notes="Single tall spotted toadstool (stand-alone accent, like the concepts' big roadside toadstools).")
def toadstool_tall(pb):
    mushroom(pb, 3.6, 1.35, (0, 0, 0), (4, -3), seed=21, segs=16)
    mushroom(pb, 1.0, 0.4, (1.0, -0.6, 0), (-12, 10), seed=22)
    pb.rock("Moss", (2.2, 2.0, 0.3), seed=23, amp=0.1)


@prop("toadstool_orange_cluster", ["all"], "P2", target=[3, 2.2, 3], group="nature",
      notes="Four orange-capped (CapOrange) toadstools with cream spots.")
def toadstool_orange(pb):
    for k, (x, y, h, r, tx, ty) in enumerate(((0, 0, 2.2, 0.8, 0, 0), (0.9, 0.5, 1.5, 0.55, -8, 10),
                                               (-0.9, 0.3, 1.3, 0.5, 10, -6), (0.2, -0.9, 0.9, 0.38, 12, 4))):
        mushroom(pb, h, r, (x, y, 0), (tx, ty), cap="CapOrange", seed=30 + k, segs=10, spots=4 if k < 2 else 2)
    pb.rock("Moss", (2.6, 2.4, 0.3), seed=34, amp=0.1)


@prop("toadstool_trio_small", ["all"], "P3", target=[1.6, 1.0, 1.6], group="nature",
      notes="Tiny rail-side toadstools (<= 1 stud tall) that can sit right next to the rails.")
def toadstool_small(pb):
    for k, (x, y, h, r) in enumerate(((0, 0, 1.0, 0.36), (0.45, 0.3, 0.7, 0.26), (-0.4, 0.35, 0.55, 0.22))):
        mushroom(pb, h, r, (x, y, 0), ((k - 1) * 8, k * 5), seed=40 + k, segs=8, spots=3 if k == 0 else 2)


# ============================================================================ bushes, ground cover
def bush(pb, parts, seed):
    for k, (x, y, z, r, m) in enumerate(parts):
        pb.rock(m, (r * 2, r * 2, r * 1.6), loc=(x, y, z - r * 0.6), seed=seed + k, amp=0.2, ico=2, flat_bottom=False,
                smooth=True)


@prop("orange_leaf_bush", ["all"], "P3", target=[3.2, 2.2, 3], group="nature", notes="Pumpkin / gold autumn bush.")
def orange_bush(pb):
    bush(pb, ((0, 0, 1.1, 1.15, "Pumpkin"), (0.95, 0.4, 0.7, 0.8, "Gold"), (-0.95, 0.2, 0.75, 0.85, "Pumpkin"),
              (0.1, -0.85, 0.65, 0.75, "Gold"), (-0.3, 0.8, 0.6, 0.7, "Pumpkin")), 50)


@prop("gold_leaf_bush", ["all"], "P3", target=[2.6, 2, 2.6], group="nature", notes="Harvest-gold round bush.")
def gold_bush(pb):
    bush(pb, ((0, 0, 1.0, 1.05, "Gold"), (0.8, 0.3, 0.7, 0.7, "Gold"), (-0.7, 0.4, 0.65, 0.7, "Pumpkin"),
              (0.1, -0.7, 0.6, 0.65, "Gold")), 60)


@prop("red_bush_tall", ["all"], "P3", target=[2.6, 3.2, 2.6], group="nature", notes="Upright ember-red shrub.")
def red_tall_bush(pb):
    pb.tube("RootBark", [(0, 0, 0), (0, 0, 1.2)], [0.2, 0.12], 6)
    bush(pb, ((0, 0, 1.4, 1.1, "MapleRed"), (0.3, 0.2, 2.3, 0.85, "MapleRed"), (-0.2, -0.1, 3.0, 0.6, "Pumpkin"),
              (0.7, -0.3, 1.0, 0.7, "MapleRed"), (-0.7, 0.3, 1.0, 0.7, "Pumpkin")), 70)


@prop("grass_tuft", ["all"], "P3", target=[1.6, 1.6, 1.6], group="nature",
      notes="Tall autumn grass blades (Moss + Gold), foreground filler along rails.")
def grass(pb):
    rnd = random.Random(80)
    for k in range(16):
        a = rnd.uniform(0, TAU)
        r0 = rnd.uniform(0, 0.25)
        L = rnd.uniform(0.9, 1.6)
        lean = rnd.uniform(0.3, 0.7)
        c, s = math.cos(a), math.sin(a)
        pts = [(c * r0, s * r0, 0), (c * (r0 + lean * 0.35), s * (r0 + lean * 0.35), L * 0.55), (c * (r0 + lean), s * (r0 + lean), L)]
        pb.tube("Gold" if k % 3 == 0 else "Moss", pts, [0.07, 0.05, 0.01], 3, flatten=0.3, smooth=False)


@prop("fern_clump_large", ["all"], "P3", target=[4, 2.4, 4], group="nature", notes="Big fern clump (12 fronds).")
def fern_large(pb):
    rnd = random.Random(90)
    for k in range(12):
        a = TAU * k / 12 + rnd.uniform(-0.15, 0.15)
        L = rnd.uniform(1.5, 2.0)
        c, s = math.cos(a), math.sin(a)
        pts = [(c * 0.15, s * 0.15, 0.1), (c * L * 0.4, s * L * 0.4, 1.6 + rnd.uniform(-0.2, 0.4)), (c * L * 0.8, s * L * 0.8, 1.6),
               (c * L, s * L, 1.0)]
        pb.tube("Moss", pts, [0.14, 0.26, 0.18, 0.03], 4, flatten=0.22)
    pb.sphere("Moss", 0.45, loc=(0, 0, 0.1), scale=(1, 1, 0.5), segs=8, rings=4)


@prop("leaf_pile_wide", ["all"], "P3", target=[3.5, 0.6, 3], group="nature", notes="Wide low drift of red leaves.")
def leaf_pile_wide(pb):
    pb.sphere("MapleRed", 1.0, scale=(1.6, 1.25, 0.28), segs=12, rings=5, smooth=False)
    pb.sphere("Pumpkin", 0.7, loc=(0.9, 0.5, 0), scale=(1.2, 1.0, 0.3), segs=10, rings=4, smooth=False)
    rnd = random.Random(91)
    for k in range(18):
        a, r = rnd.uniform(0, TAU), rnd.uniform(0.3, 1.6)
        z = 0.28 * math.sqrt(max(0.0, 1 - (r / 1.7) ** 2)) + 0.02
        pb.sphere(rnd.choice(("MapleRed", "Gold", "Pumpkin")), 0.17, loc=(math.cos(a) * r, math.sin(a) * r * 0.8, z),
                  scale=(1.6, 0.9, 0.15), rot=(rnd.uniform(-20, 20), rnd.uniform(-20, 20), rnd.uniform(0, 180)), segs=6,
                  rings=3, smooth=False)


@prop("leaf_scatter", ["all"], "P3", target=[4, 0.1, 4], group="nature",
      notes="Flat scatter of ~40 fallen leaves (cheap ground detail; lies on the terrain).")
def leaf_scatter(pb):
    rnd = random.Random(92)
    for k in range(40):
        a, r = rnd.uniform(0, TAU), 2.0 * math.sqrt(rnd.random())
        pb.box(rnd.choice(("MapleRed", "Gold", "Pumpkin", "MapleRed")), (0.34, 0.22, 0.02),
               loc=(math.cos(a) * r, math.sin(a) * r, 0.02 + 0.01 * (k % 3)), rot=(rnd.uniform(-8, 8), rnd.uniform(-8, 8), rnd.uniform(0, 180)))


@prop("rock_outcrop", ["all"], "P2", target=[8, 5, 6], group="nature",
      notes="Stacked mossy rock outcrop for backgrounds (scale 0.7-1.6).")
def outcrop(pb):
    for k, (x, y, z, sx, sy, sz) in enumerate(((0, 0, 0, 5.0, 4.2, 3.4), (2.6, 0.8, 0, 3.4, 3.0, 2.4), (-2.4, -0.6, 0, 3.2, 3.0, 2.8),
                                               (0.4, 0.2, 2.4, 3.2, 2.8, 2.2), (-1.0, 1.4, 0, 2.2, 2.0, 1.6))):
        pb.rock("Slate", (sx, sy, sz), loc=(x, y, z), seed=100 + k, amp=0.13, ico=2)
    pb.rock("Moss", (3.4, 3.0, 0.7), loc=(0.3, 0.2, 4.3), seed=110, amp=0.12, ico=2)
    pb.rock("Moss", (2.4, 2.2, 0.5), loc=(2.6, 0.8, 2.2), seed=111, amp=0.12, ico=2)
    pb.rock("Moss", (2.2, 2.2, 0.5), loc=(-2.4, -0.6, 2.6), seed=112, amp=0.12, ico=2)


# ============================================================================ lanterns
def catenary_lanterns(pb, half, top, sag, n, size=0.8, lod=0):
    pts = [(x, 0, top - sag * (1 - (x / half) ** 2)) for x in [-half + (2 * half) * i / 24 for i in range(25)]]
    pb.tube("RootBark", pts, 0.035, 4, smooth=False)
    for k in range(n):
        x = -half + 2 * half * (k + 1) / (n + 1)
        zc = top - sag * (1 - (x / half) ** 2)
        pb.lantern(size, loc=(x, 0, zc - size - 0.05), lod=lod, paper="PaperOrange" if k % 2 else "Paper")


def pole(pb, x, h, arm=False):
    pb.box("Slate", (0.6, 0.6, 0.3), loc=(x, 0, 0.15), bevel=0.06)
    pb.box("Oak", (0.34, 0.34, h), loc=(x, 0, h / 2), bevel=0.04)
    pb.cyl("Shingle", 0.34, 0.02, 0.3, 4, loc=(x, 0, h + 0.15), rot=(0, 0, 45), smooth=False)
    pb.torus("Iron", 0.07, 0.02, 6, 3, loc=(x - math.copysign(0.22, x), 0, h - 0.35), rot=(90, 0, 0))


def _span(width):
    half = width / 2
    def fn(pb):
        top = 9.6
        for sx in (-1, 1):
            pole(pb, sx * half, top + 0.4)
        n = max(3, int(round(width / 2.2)))
        catenary_lanterns(pb, half - 0.22, top + 0.05, 0.9, n, 0.8, lod=1)
    return fn


for _w in (12, 16, 20):
    prop(f"lantern_span_{_w}", ["all"], "P2", target=[_w, 10, 0.6], group="lanterns",
         notes=(f"Two 10-stud timber poles {_w} studs apart (local x = +-{_w // 2}) carrying a lantern string ACROSS "
                "the felt. Lowest lantern bottom is about 7.9 above the pole bases, so over the felt it clears the "
                "ball and a 5-stud player (fitcheck: >= 6.5 above any felt it crosses). Yaw so local X runs across the lane."),
         view="y")(_span(_w))


@prop("lantern_string_poles", ["all"], "P2", target=[10, 6.5, 0.6], group="lanterns",
      notes="Two 6-stud poles 10 apart with a sagging string of 4 lanterns, run beside (parallel to) a rail.", view="y")
def string_poles(pb):
    for sx in (-1, 1):
        pole(pb, sx * 5.0, 6.0)
    catenary_lanterns(pb, 4.78, 5.65, 0.8, 4, 0.8, lod=1)


@prop("lantern_hook_pair", ["all"], "P2", target=[2.6, 4.6, 0.5], group="lanterns",
      notes="Shepherd's-crook post with two hanging lanterns (one each side, local +-X); rail-side lighting.")
def hook_pair(pb):
    pb.box("Slate", (0.55, 0.55, 0.28), loc=(0, 0, 0.14), bevel=0.06)
    pb.tube("RootBark", [(0, 0, 0.2), (0.05, 0, 2.2), (0, 0, 4.2)], [0.16, 0.13, 0.11], 7, wobble=0.08)
    for sx, paper in ((1, "Paper"), (-1, "PaperOrange")):
        pts = [(0, 0, 3.6)] + [(sx * 0.6 * math.sin(a), 0, 4.0 + 0.45 * math.sin(a * 0.5) + 0.2 * (1 - math.cos(a))) for a in
                               [math.pi * 0.5 * i / 5 for i in range(1, 6)]] + [(sx * 1.05, 0, 4.25), (sx * 1.2, 0, 4.0)]
        pb.tube("RootBark", pts, 0.06, 5)
        pb.torus("Iron", 0.06, 0.018, 6, 3, loc=(sx * 1.2, 0, 3.92), rot=(90, 0, 0))
        pb.lantern(1.0, loc=(sx * 1.2, 0, 2.8), paper=paper)
