"""Social group: Birdie Bites shack, bench, picnic table, barrel, crate, planter, umbrella, lantern post, string lights."""
import math, random
from mathutils import Vector, Matrix
import bwlib as L
from registry import prop, FRONT_SOUTH, FRONT_NORTH, FRONT_NONE
from props_board import front_quad, open_slab, lantern_box

WOOD = ("trim", "beam", 5.0)
PLANK = ("trim", "deck", 10.0)


# ----------------------------------------------------------------------------- shack
def cupcake(pb, x, y, z, s=1.0, frost="awn_cream", seed=0):
    pb.lathe([(0.32 * s, 0.0), (0.42 * s, 0.42 * s), (0.0, 0.42 * s)], segs=10, loc=(x, y, z),
             mapping=("stripes", "awn_red", "plank", 10), smooth=False)
    pb.blob((0.95 * s, 0.95 * s, 0.55 * s), loc=(x, y, z + 0.6 * s), seed=seed, amp=0.08, ico=2,
            mapping=("flat", frost))
    pb.sphere(0.16 * s, loc=(x, y, z + 0.92 * s), segs=6, rings=4, mapping=("flat", "leaf_red"))


def lollipop(pb, x, y, z, h, r, cols=("awn_red", "awn_cream")):
    pb.cyl(0.15, 0.15, h, segs=6, loc=(x, y, z + h / 2), mapping=("flat", "awn_cream"))
    pb.cyl(r, r, 0.35, segs=14, loc=(x, y, z + h + r * 0.9), rot=(90, 0, 0),
           mapping=("stripes", cols[0], cols[1], 8, 0.3), smooth=False)


@prop("bw_birdie_bites_shack", "social", target=[16, 14, 18], tris_max=12000, front=FRONT_NORTH,
      notes="Built in its own frame: W 16 (X) x H 14 x D 18 (Z). Counter, striped awning, menu board and candy props "
            "are on the local -Z (north) side so that yaw 90 puts the counter on the WEST (lobby.json counterFaces). "
            "Candy props are merged into the BW_Atlas mesh; 2 Neon lanterns flank the window.")
def shack(pb):
    # Blender frame: front (counter) = +Y. Footprint x +-8, y +-9.
    # platform
    pb.box_minmax((-7.6, -8.6, 0.0), (7.6, 6.2, 0.5), mapping=PLANK, bevel=0.15)
    # walls: back + sides (planked), front wall with a serving window
    body = ((-7.0, -8.0), (7.0, 5.0))
    zt = 9.0
    pb.box_minmax((-7.0, -8.0, 0.5), (7.0, -7.4, zt), mapping=PLANK, bevel=0.2)            # back (south)
    for s in (-1, 1):
        x0, x1 = (-7.0, -6.4) if s < 0 else (6.4, 7.0)
        pb.box_minmax((x0, -7.4, 0.5), (x1, 5.0, zt), mapping=PLANK, bevel=0.2)
        # corner posts
        pb.box((0.9, 0.9, zt), loc=(s * 7.0, 5.0, zt / 2), mapping=WOOD, bevel=0.2)
        pb.box((0.9, 0.9, zt), loc=(s * 7.0, -8.0, zt / 2), mapping=WOOD, bevel=0.2)
    # front wall pieces around the window x -5..5, z 3.6..7.6
    fy0, fy1 = 4.4, 5.0
    pb.box_minmax((-6.4, fy0, 0.5), (6.4, fy1, 3.6), mapping=PLANK, bevel=0.15)
    pb.box_minmax((-6.4, fy0, 7.6), (6.4, fy1, zt), mapping=PLANK, bevel=0.15)
    pb.box_minmax((-6.4, fy0, 3.6), (-5.0, fy1, 7.6), mapping=PLANK, bevel=0.15)
    pb.box_minmax((5.0, fy0, 3.6), (6.4, fy1, 7.6), mapping=PLANK, bevel=0.15)
    # dark interior back panel seen through the window
    pb.box_minmax((-5.0, 0.0, 3.6), (5.0, 0.4, 7.6), mapping=("flat", "plank_dark"))
    # shelf with jars inside
    pb.box_minmax((-4.6, 0.4, 5.4), (4.6, 1.4, 5.7), mapping=WOOD)
    for i, x in enumerate((-3.6, -1.8, 0.0, 1.8, 3.6)):
        pb.cyl(0.45, 0.45, 0.9, segs=8, loc=(x, 0.9, 6.15), mapping=("flat", ("leaf_yellow", "awn_red", "crystal_tip",
                                                                             "leaf_orange", "crystal")[i]))
    # counter (brass edge) + counter front with stripes
    pb.box_minmax((-6.0, 5.0, 3.3), (6.0, 7.2, 3.75), mapping=("trim", "brass", 4.0), bevel=0.12)
    pb.box_minmax((-5.6, 5.0, 0.5), (5.6, 6.8, 3.3), mapping=("trim", "awning", 16.0), bevel=0.12)
    # awning: sloped striped canopy from the wall top out to y 9 + scalloped valance
    yA0, zA0, yA1, zA1 = 5.0, 9.4, 9.0, 7.7
    t = L.bmesh.new()
    v = [t.verts.new(p) for p in ((-8, yA0, zA0), (8, yA0, zA0), (8, yA1, zA1), (-8, yA1, zA1),
                                  (-8, yA0, zA0 - 0.25), (8, yA0, zA0 - 0.25), (8, yA1, zA1 - 0.25),
                                  (-8, yA1, zA1 - 0.25))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (3, 0, 4, 7)):
        t.faces.new([v[i] for i in f])
    L.bmesh.ops.recalc_face_normals(t, faces=t.faces)
    pb.add(t, ("trim", "awning", 16.0, 0.0))
    for i in range(8):
        x = -7.0 + 2.0 * i
        poly = [(x - 1.0, zA1), (x + 1.0, zA1)] + [(x + math.cos(a) * 1.0, zA1 - math.sin(a) * 0.75)
                                                   for a in (math.pi * k / 6 for k in range(1, 6))]
        pb.prism(poly, 0.15, loc=(0, yA1 - 0.08, 0), rot=(90, 0, 0),
                 mapping=("flat", "awn_red" if i % 2 == 0 else "awn_cream"))
    for s in (-1, 1):   # awning support posts
        pb.box((0.4, 0.4, zA1 - 0.5), loc=(s * 7.6, 8.6, 0.5 + (zA1 - 0.5) / 2), mapping=WOOD, bevel=0.1, segs=1)
    # gable roof (ridge along Y), overhangs
    rz0, rz1 = zt, 13.0
    for s in (-1, 1):
        t = L.bmesh.new()
        p = [(0, -8.8, rz1), (0, 5.6, rz1), (s * 7.9, 5.6, rz0 - 0.3), (s * 7.9, -8.8, rz0 - 0.3)]
        vv = [t.verts.new(q) for q in p] + [t.verts.new((q[0], q[1], q[2] - 0.35)) for q in p]
        for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
            t.faces.new([vv[i] for i in f])
        L.bmesh.ops.recalc_face_normals(t, faces=t.faces)
        pb.add(t, ("trim", "beam", 5.0))
    # gable ends (triangles) front and back
    for y in (5.0, -8.0):
        pb.prism([(-7.0, zt), (7.0, zt), (0.0, rz1 - 0.3)], 0.6, loc=(0, y - 0.3 if y > 0 else y + 0.3, 0),
                 rot=(90, 0, 0), mapping=PLANK)
    # sign board on the front gable (text = SurfaceGui on sign_face)
    pb.box_minmax((-4.2, 5.0, 9.6), (4.2, 5.35, 11.6), mapping=("trim", "brass", 4.0), bevel=0.1)
    open_slab(pb, (-3.9, 5.35, 9.85), (3.9, 5.5, 11.35), ("fit", "parch"), omit="+y")
    pb.quad([(3.9, 5.5, 9.85), (-3.9, 5.5, 9.85), (-3.9, 5.5, 11.35), (3.9, 5.5, 11.35)],
            mapping=("fit", "parch_panel"), part="sign_face")
    # giant cupcake topper on the ridge
    cupcake(pb, 0, -1.5, rz1 - 0.2, s=1.3, frost="awn_cream", seed=5)
    # menu board on an easel at the front-left
    mx, my = -6.4, 8.0
    pb.box((2.2, 0.25, 3.0), loc=(mx, my, 2.6), rot=(8, 0, 0), mapping=WOOD, bevel=0.08, segs=1)
    pb.quad([(mx + 0.9, my + 0.32, 1.35), (mx - 0.9, my + 0.32, 1.35), (mx - 0.9, my - 0.03, 3.85),
             (mx + 0.9, my - 0.03, 3.85)], mapping=("fit", "parch"), part="menu_face")
    for dx in (-0.8, 0.8):
        pb.box((0.3, 0.3, 4.0), loc=(mx + dx, my - 0.1, 2.0), rot=(8, 0, 0), mapping=WOOD)
    pb.box((0.3, 0.3, 3.7), loc=(mx, my - 0.75, 1.8), rot=(-17, 0, 0), mapping=WOOD)
    # candy props on the counter (merged)
    for i, (x, fr) in enumerate(((-4.6, "awn_cream"), (-3.2, "crystal_tip"), (3.4, "leaf_yellow"),
                                 (4.7, "awn_red"))):
        cupcake(pb, x, 6.1, 3.75, s=0.9, frost=fr, seed=10 + i)
    pb.torus(0.42, 0.2, segs=10, rsegs=5, loc=(-1.6, 6.2, 3.95), mapping=("flat", "leaf_orange"))
    pb.torus(0.42, 0.2, segs=10, rsegs=5, loc=(1.7, 6.2, 3.95), mapping=("flat", "crystal"))
    pb.cyl(0.8, 0.7, 0.9, segs=10, loc=(0.0, 6.0, 4.2), mapping=("flat", "crystal_tip"))     # candy jar
    pb.sphere(0.5, loc=(0.0, 6.0, 4.9), segs=8, rings=5, mapping=("flat", "awn_red"))
    lollipop(pb, 7.0, 8.4, 0.5, 4.4, 0.9)
    lollipop(pb, -7.25, -6.0, 0.5, 2.8, 0.7, cols=("leaf_yellow", "crystal"))
    # 2 Neon lanterns on brackets beside the window
    for s in (-1, 1):
        pb.box((0.3, 0.9, 0.3), loc=(s * 5.7, 5.4, 7.9), mapping=WOOD)
        lantern_box(pb, s * 5.7, 5.85, 6.2, glass_h=0.8, r=0.35)
    # back door
    pb.box_minmax((-1.4, -8.15, 0.5), (1.4, -7.95, 5.6), mapping=("trim", "beam", 3.0), bevel=0.06, segs=1)


# ----------------------------------------------------------------------------- bench
@prop("bw_bench", "social", target=[6, 2.5, 2], tris_max=600, front=FRONT_NORTH,
      notes="Sitter faces local -Z (north) at yaw 0 (lobby.json frame); builder yaw 180 turns the pier and "
            "promenade benches to face south (sunset).")
def bench(pb):
    # seat (slatted via the deck strip), backrest on the south (-Y) side
    pb.box_minmax((-3.0, -0.55, 1.2), (3.0, 1.0, 1.5), mapping=("trim", "deck", 20.0), bevel=0.1, segs=2)
    pb.box((6.0, 0.3, 0.8), loc=(0, -0.85, 2.05), rot=(-10, 0, 0), mapping=("trim", "deck", 20.0), bevel=0.1, segs=2)
    for s in (-1, 1):
        x = s * 2.55
        prof = [(-0.85, 0.0), (-0.45, 0.0), (-0.35, 1.2), (0.6, 1.2), (0.75, 0.0), (1.0, 0.0), (0.85, 1.7),
                (-0.55, 1.7), (-0.72, 2.5), (-1.0, 2.5)]
        pb.prism(prof, 0.4, loc=(x, 0, 0), rot=(90, 0, 90), mapping=("flat", "post"))
    pb.box((5.0, 0.3, 0.3), loc=(0, 0.1, 0.55), mapping=WOOD)


# ----------------------------------------------------------------------------- picnic table
@prop("bw_picnic_table", "social", target=[6, 3, 6], tris_max=900, front=FRONT_NONE,
      notes="Table top 6x2.6 at Y 3, two attached bench planks, A-frame legs.")
def picnic(pb):
    pb.box_minmax((-3.0, -1.3, 2.65), (3.0, 1.3, 3.0), mapping=("trim", "deck", 20.0), bevel=0.1, segs=2)
    for s in (-1, 1):
        y0, y1 = (2.0, 3.0) if s > 0 else (-3.0, -2.0)
        pb.box_minmax((-3.0, y0, 1.45), (3.0, y1, 1.75), mapping=("trim", "deck", 20.0), bevel=0.1, segs=2)
    for x in (-2.2, 2.2):
        for s in (-1, 1):
            # slanted leg from the bench foot to under the top
            a = Vector((x, s * 2.3, 0.2))
            b = Vector((x, s * 0.5, 2.55))
            d = b - a
            ang = math.degrees(math.atan2(d.y, d.z))
            pb.box((0.4, 0.4, d.length), loc=tuple((a + b) / 2), rot=(-ang, 0, 0), mapping=WOOD, bevel=0.06, segs=1)
        pb.box((0.35, 5.6, 0.35), loc=(x, 0, 1.3), mapping=WOOD, bevel=0.06, segs=1)


# ----------------------------------------------------------------------------- barrel / crate / planter
@prop("bw_barrel", "social", target=[2, 3, 2], tris_max=300, front=FRONT_NONE, notes="Bulged barrel, 2 brass hoops.")
def barrel(pb):
    prof = [(0.0, 0.0), (0.82, 0.0), (0.92, 0.5), (1.0, 1.5), (0.92, 2.5), (0.82, 2.95), (0.0, 2.95)]
    pb.lathe(prof, segs=12, mapping=("trim", "beam", 2.0), smooth=True)
    for z, r in ((0.55, 0.95), (2.45, 0.95)):
        pb.cyl(r, r, 0.3, segs=12, loc=(0, 0, z), mapping=("flat", "brass"), caps=False, smooth=True)
    pb.cyl(0.7, 0.7, 0.05, segs=12, loc=(0, 0, 2.97), mapping=("flat", "plank_dark"), smooth=False)


@prop("bw_crate", "social", target=[2, 2, 2], tris_max=50, front=FRONT_NONE, notes="Chamfered plank crate (44 tris).")
def crate(pb):
    pb.box((2.0, 2.0, 2.0), loc=(0, 0, 1.0), mapping=("trim", "deck", 10.0), bevel=0.15, segs=1)


@prop("bw_flower_planter", "social", target=[4, 2, 2], tris_max=1000, front=FRONT_NONE,
      notes="Plank box with leafy mound and chunky blossoms in leaf/awning palette colours.")
def planter(pb):
    pb.box_minmax((-2.0, -1.0, 0.0), (2.0, 1.0, 1.1), mapping=("trim", "deck", 10.0), bevel=0.12, segs=2)
    pb.box_minmax((-1.75, -0.75, 1.05), (1.75, 0.75, 1.15), mapping=("flat", "plank_dark"))
    for i, x in enumerate((-1.1, 0.0, 1.1)):
        pb.blob((1.5, 1.4, 0.9), loc=(x, 0, 1.25), seed=60 + i, amp=0.1, ico=2, mapping=("flat", "fringe"))
    rnd = random.Random(4)
    cols = ("awn_red", "leaf_yellow", "leaf_orange", "awn_cream", "crystal")
    for i in range(11):
        x = -1.5 + 3.0 * i / 10 + rnd.uniform(-0.1, 0.1)
        y = rnd.uniform(-0.45, 0.45)
        z = 1.45 + rnd.uniform(0.0, 0.3)
        pb.sphere(0.27, loc=(x, y, z), segs=6, rings=4, mapping=("flat", cols[i % len(cols)]))


# ----------------------------------------------------------------------------- umbrella
@prop("bw_beach_umbrella", "social", target=[6, 7, 6], tris_max=700, front=FRONT_NONE,
      notes="Red/cream striped canopy (16 panels), weighted base.")
def umbrella(pb):
    pb.cyl(0.8, 0.9, 0.3, segs=10, loc=(0, 0, 0.15), mapping=("flat", "stone"), smooth=False)
    pb.cyl(0.15, 0.15, 6.4, segs=8, loc=(0, 0, 3.4), mapping=("flat", "awn_cream"))
    prof = [(0.0, 6.95), (1.0, 6.75), (2.1, 6.3), (3.0, 5.7), (3.0, 5.55), (2.1, 6.1), (1.0, 6.55), (0.18, 6.7)]
    pb.lathe(prof, segs=16, mapping=("stripes", "awn_red", "awn_cream", 16, 0.0), smooth=False, phase=0.0)
    pb.sphere(0.2, loc=(0, 0, 6.95), segs=8, rings=4, mapping=("flat", "brass"))


# ----------------------------------------------------------------------------- lantern post / string lights
@prop("bw_lantern_post", "social", target=[1, 7, 1], tris_max=400, front=FRONT_NONE,
      notes="Wooden post, brass lantern housing, Neon glass (own MeshPart). Good PointLight host.")
def lantern_post(pb):
    pb.box((1.0, 1.0, 0.5), loc=(0, 0, 0.25), mapping=("trim", "stone", 2.0), bevel=0.1, segs=1)
    pb.cyl(0.25, 0.25, 4.9, segs=8, loc=(0, 0, 0.5 + 2.45), mapping=("trim", "beam", 3.0), smooth=False)
    pb.cyl(0.42, 0.42, 0.2, segs=8, loc=(0, 0, 5.5), mapping=("flat", "brass"), smooth=False)
    pb.box((0.65, 0.65, 0.85), loc=(0, 0, 6.025), part="neon")
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        pb.box((0.3, 0.3, 0.85), loc=(math.cos(a) * 0.38, math.sin(a) * 0.38, 6.025), mapping=("flat", "brass_lo"))
    pb.cyl(0.5, 0.12, 0.45, segs=8, loc=(0, 0, 6.675), mapping=("flat", "brass"), smooth=False)
    pb.sphere(0.15, loc=(0, 0, 6.9), segs=6, rings=4, mapping=("flat", "brass"))


@prop("bw_string_lights", "social", target=[24, 1.1, 0.5], tris_max=400, front=FRONT_NONE, scalable="x",
      notes="24-stud span (ends at local X +-12, at the top of the bbox), cable with a gentle 0.6-stud parabolic sag "
            "and 12 Neon bulbs hung directly below; scale X for other spans (12-24).")
def string_lights(pb):
    SPAN, SAG, N = 24.0, 0.6, 12
    zc = lambda x: 0.47 + SAG * (2.0 * x / SPAN) ** 2
    pts = [(-SPAN / 2 + SPAN * k / 12, 0, zc(-SPAN / 2 + SPAN * k / 12)) for k in range(13)]
    pb.tube(pts, 0.06, segs=4, mapping=("flat", "ink"), caps=False)
    for i in range(N):
        x = -SPAN / 2 + 1.0 + 2.0 * i
        pb.sphere(0.23, loc=(x, 0, zc(x) - 0.24), scale=(1, 1.17, 1), segs=6, rings=3, part="neon")
