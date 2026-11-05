"""Remaining props: H3 toadstool stool (P1), P2 theming, P3 polish."""
import math, random
import bmesh
from mathutils import Vector, Matrix
from registry import prop
from lglib import M, R, TAU, superellipse_ring, text_bm
from props_moving import mushroom_cap
from props_hero import RS, arch_poly, FRAME_Y, window
from props_dressing import FONT


def mushroom(pb, h, r_cap, loc=(0, 0, 0), tilt=(0, 0), cap="ToadRed", stem="Cream", spots=5, seed=0, segs=12,
             spot_mat="Cream"):
    m = M(loc, (tilt[0], tilt[1], 0))
    sr = max(0.06, r_cap * 0.28)
    pb.lathe(stem, [(sr * 1.25, 0), (sr, h * 0.3), (sr * 0.9, h * 0.75), (sr * 0.85, h * 0.8), (0, h * 0.8)], max(6, segs - 4),
             matrix=m)
    mushroom_cap(pb, r_cap, h * 0.62, h * 0.38, mat_cap=cap, spots=spots, seed=seed, segs=segs, matrix=m,
                 spot_mat=spot_mat)


# ============================================================================ H3 stool (P1)
@prop("toadstool_stool", ["H3"], "P1", target=[2, 1.8, 2], group="hero",
      notes="Fat spotted toadstool guarding the H3 cup; cladding for the 'toadstool_stool' bumper (1.6x2x1.6, "
            "top at y=1.5).",
      placements=[dict(hole="H3", pos=[17.0, 0, -28.8], yaw=0)])
def toadstool_stool(pb):
    pb.lathe("Cream", [(0.82, 0), (0.8, 0.2), (0.7, 0.6), (0.62, 1.0), (0, 1.0)], 14, wobble=0.03)
    mushroom_cap(pb, 1.0, 0.95, 0.85, spots=7, seed=3, segs=16)
    pb.torus("Moss", 0.78, 0.08, 14, 4, loc=(0, 0, 0.05))


# ============================================================================ P2 H9 bits
@prop("trunk_tunnel_arch", ["H9"], "P2", target=[7, 5, 8], group="hero",
      notes="Three root-buttress ribs over the H9 trunk tunnel felt (x 8..14). Rib feet sit on the rail lines "
            "(z=+-3.75 from centre), clear opening 7.0 wide, ~4.4 high. Overlaps the hollow_tree tunnel bore.",
      placements=[dict(hole="H9", pos=[11, 1.0, -25.5], yaw=0)])
def trunk_tunnel_arch(pb):
    for k, x in enumerate((-2.9, 0.0, 2.9)):
        pts = []
        for i in range(15):
            a = math.pi * i / 14
            y = -3.95 * math.cos(a)
            z = 4.3 * math.sin(a) ** 0.8          # pass 6: top <= y 6 (flag sightline clears it by 0.2)
            pts.append((x + 0.15 * math.sin(i * 1.1 + k), y, z))
        radii = [0.38 * (1.7 if i in (0, 14) else 1.3 if i in (1, 13) else 1.0) for i in range(15)]
        pb.tube("RootBark", pts, radii, 7, wobble=0.2, seed=k)
    for sy in (-1, 1):
        pb.tube("RootBark", [(-3.4, sy * 4.05, 0.3), (0, sy * 4.15, 0.6), (3.4, sy * 4.05, 0.3)], 0.32, 6, wobble=0.2, seed=9)
    for x in (-2.9, 0.0, 2.9):
        pb.sphere("Moss", 0.5, loc=(x, 0, 4.5), scale=(1.0, 1.6, 0.3), segs=8, rings=4)
    pb.torus("Iron", 0.06, 0.015, 6, 3, loc=(0, 0, 3.82), rot=(90, 0, 0))
    pb.lantern(0.7, loc=(0, 0, 3.06))


@prop("lantern_knot", ["H9"], "P2", target=[1.2, 0.6, 1.2], group="hero",
      notes=("Secret glowing knot-hole, set INTO the felt: top only 0.06 above the felt, the rest sinks below. "
             "Glow disc radius 0.3 = teleport entry radius. Same mesh marks the exit knot on the heart green."),
      placements=[dict(hole="H9", pos=[6.5, 0.46, -23.0], yaw=0, note="entry (felt y=1.0)"),
                  dict(hole="H9", pos=[15.0, -1.34, -52.0], yaw=0, note="exit marker (felt y=-0.8)")])
def lantern_knot(pb):
    base = 0.54
    pb.cyl("RootBark", 0.6, 0.5, base, 14, loc=(0, 0, base / 2), smooth=False)
    pb.torus("RootBark", 0.44, 0.12, 16, 6, loc=(0, 0, base - 0.02))
    pb.cyl("Glow", 0.3, 0.3, 0.04, 14, loc=(0, 0, base + 0.01), smooth=False)
    for k in range(5):
        a = TAU * k / 5
        pts = [(math.cos(a + d) * (0.45 + d * 0.15), math.sin(a + d) * (0.45 + d * 0.15), base + 0.02) for d in (0, 0.3, 0.6)]
        pb.tube("Oak", pts, 0.035, 4)


@prop("heart_well_rim", ["H9"], "P2", target=[8, 0.6, 1], group="hero",
      notes=("Carved root log along the heart-well drop (chamber north edge z=-40, x 18..26). Sits UNDER the "
             "chamber felt edge with its face flush at z=-40 (top 0.02 below the felt), so it never blocks the ball."),
      placements=[dict(hole="H9", pos=[22, 0.4, -39.5], yaw=0)])
def heart_well_rim(pb):
    rot = Matrix.Rotation(math.radians(90), 4, "Y")
    pb.lathe("RootBark", [(0.26, -4.0)] + [(0.3, -4.0 + 8 * i / 8) for i in range(1, 8)] + [(0.26, 4.0)], 8,
             matrix=Matrix.Translation((0, 0, 0.29)) @ rot @ Matrix.Diagonal((1, 1.6, 1, 1)), wobble=0.08)
    for k, x in enumerate((-3.0, -1.0, 1.2, 3.1)):
        pb.tube("RootBark", [(x, -0.5, 0.05), (x + 0.3, -0.45, 0.35), (x + 0.6, -0.48, 0.55)], [0.14, 0.11, 0.07], 5)
    for x in (-3.6, 3.6):
        pb.lantern(0.42, loc=(x, -0.5, 0.06), hook=False)


@prop("rabbit_hole_rim", ["H2"], "P2", target=[3, 0.5, 3], group="hero",
      notes=("Roots + moss lining the 2x2 rabbit-hole pit. Only a 0.06-high lip shows above the lower felt; "
             "the rest (dark shaft + roots) sits inside the pit, so the opening stays a clean 2x2."),
      placements=[dict(hole="H2", pos=[-5, -1.92, -30], yaw=0, note="lower felt y=-1.5, pit 2x2")])
def rabbit_hole_rim(pb):
    d = 0.42
    outer = [superellipse_ring(1.05, 1.05, 4, 24, z) for z in (0, d)]
    inner = [superellipse_ring(0.99, 0.99, 4, 24, z) for z in (0.02, d)]
    from lglib import shell
    shell(pb, "Ink", outer, inner)
    pb.box("Ink", (2.0, 2.0, 0.04), loc=(0, 0, 0.02))
    path = superellipse_ring(1.22, 1.22, 4, 24, d - 0.08)
    pb.tube("RootBark", path + [path[0]], 0.13, 6, caps=False, wobble=0.25, seed=2)
    for k in range(8):
        a = TAU * k / 8 + 0.2
        p = Vector((math.cos(a), math.sin(a), 0))
        pb.tube("RootBark", [p * 1.3 + Vector((0, 0, d - 0.05)), p * 1.02 + Vector((0, 0, d - 0.12)), p * 0.98 + Vector((0, 0, 0.1))],
                [0.08, 0.06, 0.03], 5)
    for k in range(5):
        a = TAU * k / 5 + 0.6
        pb.sphere("Moss", 0.28, loc=(math.cos(a) * 1.25, math.sin(a) * 1.25, d - 0.03), scale=(1.4, 1.0, 0.25), segs=8, rings=4)


# ============================================================================ P2 lantern string
@prop("lantern_string", ["H3", "H9"], "P2", target=[12, 1, 0.3], group="lanterns",
      notes="Catenary rope with 6 small lanterns. Rope ends (attach points) at local x=+-6, y = bbox top. "
            "Hang between two lantern_posts / tree branches.",
      placements=[dict(hole="H3", pos=[17.5, 3.4, -22], yaw=0, note="across the green entrance"),
                  dict(hole="H9", pos=[23, 3.0, -44], yaw=0, note="over the heart (with heart_lantern_cluster)")])
def lantern_string(pb):
    top = 1.05
    pts = [(x, 0, top - 0.45 * (1 - (x / 6) ** 2)) for x in [-6 + 0.5 * i for i in range(25)]]
    pb.tube("RootBark", pts, 0.03, 4, smooth=False)
    for k in range(6):
        x = -5 + 2 * k
        zc = top - 0.45 * (1 - (x / 6) ** 2)
        pb.lantern(0.55, loc=(x, 0, zc - 0.58), lod=0)
    for sx in (-1, 1):
        pb.torus("Iron", 0.06, 0.015, 6, 3, loc=(sx * 6, 0, top), rot=(90, 0, 0))


# ============================================================================ P2 trees, boulders, mushrooms
def tree(pb, trunk_mat, trunk_h, trunk_r, branches, blobs, leaf_mats, seed):
    rnd = random.Random(seed)
    pb.tube(trunk_mat, [(0, 0, 0), (0.15, 0.05, trunk_h * 0.4), (-0.1, 0.1, trunk_h * 0.75), (0.05, 0, trunk_h)],
            [trunk_r * 1.35, trunk_r, trunk_r * 0.8, trunk_r * 0.55], 9, wobble=0.12, seed=seed)
    for k in range(4):
        a = TAU * k / 4 + 0.4
        pb.tube(trunk_mat, [(math.cos(a) * trunk_r, math.sin(a) * trunk_r, 0.5),
                            (math.cos(a) * trunk_r * 2.0, math.sin(a) * trunk_r * 2.0, 0.0)], [trunk_r * 0.5, trunk_r * 0.2], 5)
    for (a, z, L, up) in branches:
        a = math.radians(a)
        p0 = Vector((0, 0, z))
        p1 = p0 + Vector((math.cos(a) * L * 0.6, math.sin(a) * L * 0.6, up * 0.6))
        p2 = p0 + Vector((math.cos(a) * L, math.sin(a) * L, up))
        pb.tube(trunk_mat, [p0, p1, p2], [trunk_r * 0.55, trunk_r * 0.35, trunk_r * 0.15], 6, wobble=0.1)
    for k, (p, r) in enumerate(blobs):
        pb.rock(leaf_mats[k % len(leaf_mats)], (r * 2, r * 2, r * 1.7), loc=Vector(p) - Vector((0, 0, r * 0.6)),
                seed=seed * 7 + k, amp=0.16, ico=2, flat_bottom=False)


@prop("red_maple_tree", ["H1", "all"], "P2", target=[10, 16, 10], group="nature",
      notes="Stylised red maple (Ember red + Pumpkin canopy). Scale 0.8-1.2 and yaw freely.",
      placements=[dict(hole="H1", pos=[8, 0, -15], yaw=0, note="outside the right rail")])
def red_maple(pb):
    blobs = [((0, 0, 13.0), 3.2), ((2.6, 1.0, 11.0), 2.6), ((-2.5, 1.2, 11.2), 2.6), ((0.8, -2.6, 11.0), 2.5),
             ((-1.0, 2.6, 10.6), 2.4), ((2.0, -1.2, 13.4), 2.0), ((-2.0, -1.4, 13.0), 2.2), ((0.3, 0.5, 15.0), 2.0)]
    tree(pb, "RootBark", 9.5, 0.6, [(20, 6.5, 3.0, 3.0), (150, 7.0, 3.0, 3.2), (260, 7.5, 2.6, 3.0)], blobs,
         ["MapleRed", "Pumpkin", "MapleRed"], 3)


@prop("golden_birch_tree", ["all"], "P2", target=[8, 14, 8], group="nature",
      notes="Slender birch with a harvest-gold canopy for the background.",
      placements=[])
def birch(pb):
    blobs = [((0, 0, 11.5), 2.6), ((1.8, 0.8, 10.0), 2.1), ((-1.8, 0.6, 10.2), 2.1), ((0.4, -1.9, 9.6), 2.0),
             ((-0.5, 1.8, 12.3), 1.9), ((0.2, -0.4, 13.2), 1.6)]
    tree(pb, "BirchBark", 9.5, 0.38, [(40, 6.0, 2.0, 2.5), (200, 6.8, 2.0, 2.4)], blobs, ["Gold", "Gold", "Pumpkin"], 5)
    rnd = random.Random(1)
    for k in range(9):
        z = rnd.uniform(0.6, 8.5)
        a = rnd.uniform(0, TAU)
        r = 0.4 * (1 - z / 25)
        pb.box("Ink", (0.32, 0.08, 0.07), loc=(math.cos(a) * r, math.sin(a) * r, z), rot=(0, 0, math.degrees(a) + 90))


@prop("mossy_boulder", ["H1", "H5", "H6", "H7"], "P2", target=[4, 3, 4], group="nature",
      notes="Mossy boulder; scale 0.5-1.5, yaw freely.",
      placements=[dict(hole="H1", pos=[-8, 0.5, -21], yaw=30, note="outside the green's front-left rail")])
def boulder(pb):
    pb.rock("Slate", (4.0, 3.6, 3.2), seed=5, amp=0.14, ico=2)
    pb.rock("Slate", (1.4, 1.2, 1.0), loc=(1.9, -1.0, 0), seed=6)
    pb.rock("Moss", (2.8, 2.6, 0.7), loc=(-0.2, 0.2, 2.45), seed=7, amp=0.12, ico=2)
    for k in range(3):
        a = TAU * k / 3
        pb.tube("Moss", [(math.cos(a) * 1.6, math.sin(a) * 1.6, 0), (math.cos(a) * 2.0, math.sin(a) * 2.0, 0.6)], [0.12, 0.02], 4)


@prop("toadstool_cluster", ["H3", "H8"], "P2", target=[3, 2.5, 3], group="nature",
      notes="Three small red toadstools.",
      placements=[dict(hole="H3", pos=[-6, 0, -6], yaw=0)])
def toadstool_cluster(pb):
    mushroom(pb, 2.5, 0.9, (0.2, 0.2, 0), (0, 0), seed=1, segs=14)
    mushroom(pb, 1.7, 0.65, (-0.9, -0.4, 0), (8, -10), seed=2)
    mushroom(pb, 1.1, 0.45, (0.8, -0.8, 0), (-10, 8), seed=3)
    pb.rock("Moss", (2.4, 2.2, 0.3), seed=4, amp=0.1)


@prop("glowing_mushrooms", ["H8", "H9"], "P2", target=[2.5, 1.8, 2.5], group="nature",
      notes="Bioluminescent cluster: caps are Neon (accent #7FE3D0); add a faint PointLight (range 6) at night.",
      placements=[dict(hole="H8", pos=[-22.4, 0, -22.0], yaw=0, note="along the climb, outside rail5 (pass 6: was on the c2 felt)"),
                  dict(hole="H9", pos=[30, -0.5, -52], yaw=0, note="heart corner (outside rail15 if needed)")])
def glowing_mushrooms(pb):
    for k, (x, y, h, r, tx, ty) in enumerate(((0, 0, 1.8, 0.55, 0, 0), (0.8, 0.4, 1.2, 0.4, -8, 10),
                                               (-0.7, 0.5, 1.0, 0.35, 10, -6), (0.3, -0.8, 0.8, 0.3, 12, 4),
                                               (-0.5, -0.6, 0.6, 0.25, -6, -8))):
        mushroom(pb, h, r, (x, y, 0), (tx, ty), cap="ShroomGlow", stem="Cream", spots=3, seed=k, segs=10,
                 spot_mat="Firefly")
    pb.rock("Moss", (2.2, 2.0, 0.25), seed=9, amp=0.1)


@prop("welcome_sign", ["H1"], "P2", target=[2, 3, 0.4], group="nature",
      notes="'LANTERN GROVE' carved board on two posts with a little roof and lantern; lettering faces +Z.",
      placements=[dict(hole="H1", pos=[-6, 0, 1], yaw=0)])
def welcome_sign(pb):
    for sx in (-1, 1):
        pb.box("Oak", (0.2, 0.2, 2.75), loc=(sx * 0.85, 0, 1.375), bevel=0.03)
    pb.box("RootBark", (2.0, 0.14, 0.95), loc=(0, -0.05, 1.85), bevel=0.04)
    pb.box("Oak", (1.82, 0.08, 0.78), loc=(0, -0.11, 1.85), bevel=0.02)
    t = text_bm("LANTERN", size=0.3, extrude=0.015, font_path=FONT)
    pb.add("Cream", t, M((0, -0.16, 1.92)))
    t = text_bm("GROVE", size=0.3, extrude=0.015, font_path=FONT)
    pb.add("Cream", t, M((0, -0.16, 1.57)))
    for sx in (-1, 1):
        pb.box("Shingle", (1.25, 0.6, 0.08), loc=(sx * 0.55, 0, 2.86), rot=(0, sx * 22, 0), bevel=0.02)
    pb.torus("Iron", 0.05, 0.015, 6, 3, loc=(0, -0.2, 2.62), rot=(90, 0, 0))
    pb.box("Oak", (0.08, 0.32, 0.08), loc=(0, -0.08, 2.72))
    pb.lantern(0.42, loc=(0, -0.2, 2.24))
    pb.rock("Moss", (1.6, 0.6, 0.25), seed=3, amp=0.1)


# ============================================================================ P3 polish
@prop("fern_clump", ["all"], "P3", target=[3, 2, 3], group="nature", notes="Fern clump.",
      placements=[dict(hole="H7", pos=[12, -2.4, -34], yaw=0)])
def fern(pb):
    rnd = random.Random(4)
    for k in range(9):
        a = TAU * k / 9 + rnd.uniform(-0.2, 0.2)
        L = rnd.uniform(1.1, 1.5)
        c, s = math.cos(a), math.sin(a)
        pts = [(c * 0.1, s * 0.1, 0.1), (c * L * 0.5, s * L * 0.5, 1.3 + rnd.uniform(-0.2, 0.3)), (c * L, s * L, 0.9)]
        pb.tube("Moss", pts, [0.12, 0.2, 0.04], 4, flatten=0.25)
    pb.sphere("Moss", 0.35, loc=(0, 0, 0.1), scale=(1, 1, 0.5), segs=8, rings=4)


@prop("red_leaf_bush", ["all"], "P3", target=[3, 2, 3], group="nature", notes="Autumn bush.", placements=[])
def leaf_bush(pb):
    for k, (x, y, z, r, m) in enumerate(((0, 0, 0.9, 1.0, "MapleRed"), (0.8, 0.3, 0.6, 0.7, "Pumpkin"),
                                          (-0.8, 0.2, 0.6, 0.75, "MapleRed"), (0.1, -0.7, 0.55, 0.65, "Pumpkin"))):
        pb.rock(m, (r * 2, r * 2, r * 1.6), loc=(x, y, z - r * 0.6), seed=k + 3, amp=0.18, ico=2, flat_bottom=False)


@prop("leaf_pile", ["H1", "H2"], "P3", target=[2, 0.6, 2], group="nature", notes="Pile of fallen leaves.",
      placements=[])
def leaf_pile(pb):
    pb.sphere("Pumpkin", 0.9, scale=(1.0, 0.9, 0.32), segs=10, rings=5, smooth=False)
    rnd = random.Random(2)
    for k in range(16):
        a, r = rnd.uniform(0, TAU), rnd.uniform(0.2, 0.95)
        z = 0.3 * math.sqrt(max(0.0, 1 - (r / 0.95) ** 2)) + 0.02
        pb.sphere(rnd.choice(("MapleRed", "Gold", "Pumpkin")), 0.16, loc=(math.cos(a) * r, math.sin(a) * r, z),
                  scale=(1.6, 0.9, 0.15), rot=(rnd.uniform(-20, 20), rnd.uniform(-20, 20), rnd.uniform(0, 180)), segs=6,
                  rings=3, smooth=False)


@prop("flour_sacks_crates", ["H6"], "P3", target=[2, 1.5, 2], group="nature", notes="Mill sacks + crate.",
      placements=[dict(hole="H6", pos=[-6, 0, -6], yaw=20)])
def sacks(pb):
    pb.box("Oak", (0.95, 0.95, 0.9), loc=(0.45, 0.35, 0.45), bevel=0.05)
    pb.box("RootBark", (0.98, 0.98, 0.1), loc=(0.45, 0.35, 0.85))
    pb.box("RootBark", (0.98, 0.98, 0.1), loc=(0.45, 0.35, 0.08))
    for k, (x, y, z, rz) in enumerate(((-0.5, 0.2, 0, 10), (-0.4, -0.55, 0, -25), (0.45, 0.35, 0.9, 40))):
        pb.lathe("Cream", [(0.32, 0), (0.42, 0.1), (0.44, 0.35), (0.36, 0.55), (0.12, 0.66), (0.14, 0.75), (0, 0.76)], 10,
                 loc=(x, y, z), rot=(0, 0, rz), wobble=0.06, seed=k)
        pb.torus("Oak", 0.13, 0.03, 8, 3, loc=(x, y, z + 0.66))


@prop("squirrel_hut", ["H2"], "P3", target=[3, 5, 3], group="nature", notes="Tiny squirrel hut on a post.",
      placements=[dict(hole="H2", pos=[11, -1.5, -28], yaw=-90, note="outside the right rail, door facing the green")])
def squirrel_hut(pb):
    pb.tube("RootBark", [(0, 0, 0), (0.05, 0, 1.5), (0, 0, 3.0)], [0.3, 0.22, 0.2], 7, wobble=0.1)
    pb.cyl("Oak", 1.35, 1.35, 0.15, 10, loc=(0, 0, 3.0), smooth=False)
    for k in range(10):
        a = TAU * k / 10
        pb.box("RootBark", (0.08, 0.08, 0.35), loc=(math.cos(a) * 1.3, math.sin(a) * 1.3, 3.25))
    pb.torus("RootBark", 1.3, 0.04, 10, 3, loc=(0, 0, 3.42))
    pb.lathe("Oak", [(0.8, 3.05), (0.78, 3.95), (0, 3.95)], 10)
    window(pb, Vector((0, -0.76, 3.5)), (0, -1, 0), r=0.22)
    acorn_cap = [(1.0, 3.9), (1.2, 4.05), (1.1, 4.4), (0.7, 4.7), (0.0, 4.8)]
    pb.lathe("RootBark", acorn_cap, 12)
    pb.tube("RootBark", [(0, 0, 4.7), (0.1, 0, 4.95), (0.25, 0, 5.0)], 0.07, 5)
    for k in range(3):
        a = TAU * k / 3 + 0.5
        pb.tube("RootBark", [(0, 0, 1.6 + k * 0.4), (math.cos(a) * 0.9, math.sin(a) * 0.9, 2.95)], [0.08, 0.05], 4)
    pb.lantern(0.45, loc=(0.95, -0.55, 3.1), hook=False)


@prop("stepping_stones", ["H5"], "P3", target=[2, 1, 2], group="nature",
      notes="Three mossy stepping stones (decor in the stream, outside ball paths).",
      placements=[dict(hole="H5", pos=[4, -1.4, -21], yaw=0, note="stream_rocks anchor; tops ~0.4 above the water")])
def stepping_stones(pb):
    for k, (x, y, s) in enumerate(((0, 0, 1.0), (0.5, 0.9, 0.75), (-0.5, -0.8, 0.8))):
        pb.rock("Slate", (s, s * 0.9, 0.9), loc=(x, y, 0), seed=k + 2, amp=0.1)
        pb.rock("Moss", (s * 0.7, s * 0.6, 0.2), loc=(x, y, 0.72), seed=k + 12, amp=0.1)
