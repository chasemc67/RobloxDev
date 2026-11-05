"""Structure group: deck tiles, railing section, pier piling cluster (instanced many times: keep tris low)."""
import math
from mathutils import Vector
import bwlib as L
from registry import prop, FRONT_NONE

WOOD = ("trim", "beam", 6.0)


def _deck(pb, variant):
    # 10 x 10 x 1, top + 4 sides (bottom never visible). Planks + gaps live in the atlas deck strip.
    t = L.bmesh.new()
    L.bmesh.ops.create_cube(t, size=1.0)
    L.bmesh.ops.scale(t, vec=(10, 10, 1), verts=t.verts)
    L.bmesh.ops.translate(t, vec=(0, 0, 0.5), verts=t.verts)
    t.normal_update()
    L.bmesh.ops.delete(t, geom=[f for f in t.faces if f.normal.z < -0.5], context="FACES_ONLY")
    pb.add(t, ("deck", variant))


@prop("bw_deck_plank_a", "structure", target=[10, 1, 10], tris_max=100, scalable="xz",
      notes="Deck tile variant A (atlas deck strip U 0.0-0.5). Top + sides only; plank gaps are in the texture.")
def deck_a(pb):
    _deck(pb, "a")


@prop("bw_deck_plank_b", "structure", target=[10, 1, 10], tris_max=100, scalable="xz",
      notes="Deck tile variant B (atlas deck strip U 0.5-1.0, different board joints/tints than A).")
def deck_b(pb):
    _deck(pb, "b")


@prop("bw_railing", "structure", target=[10, 3.5, 0.6], tris_max=350, scalable="x",
      notes="One 10-stud section: post at the section centre, continuous handrail, rope swag dipping at the "
            "section ends so consecutive sections read as one railing. Scale X for the 8-stud pier ends.")
def railing(pb):
    # post (centre), brass cap, handrail, rope swag
    pb.box((0.6, 0.6, 3.05), loc=(0, 0, 1.525), mapping=("trim", "beam", 4.0), bevel=0.1, segs=1)
    pb.lathe([(0.27, 3.05), (0.3, 3.15), (0.24, 3.38), (0.0, 3.5)], segs=6, mapping=("flat", "brass"))
    pb.box((10.0, 0.42, 0.3), loc=(0, 0, 2.85), mapping=("trim", "beam", 5.0), bevel=0.08, segs=1)
    pts = []
    for i in range(11):
        x = -5 + i
        u = abs(x) / 5.0                      # 0 at the post, 1 at the section ends
        z = 2.1 - 0.75 * math.sin(u * math.pi / 2)
        pts.append((x, 0, z))
    pb.tube(pts, 0.16, segs=5, mapping=("trim", "rope", 2.0), caps=False)


@prop("bw_pier_piling", "structure", target=[2, 6, 2], tris_max=250,
      notes="Cluster of 3 weathered posts lashed with rope; top at local Y=6 (builder base Y=-6 -> top flush with "
            "deck underside region).")
def piling(pb):
    posts = [((0.5, 0.0), 0.45, 6.0), ((-0.33, 0.5), 0.42, 5.75), ((-0.33, -0.5), 0.4, 5.5)]
    for (x, y), r, h in posts:
        pb.cyl(r, r * 0.92, h, segs=7, loc=(x, y, h / 2), mapping=("trim", "beam", 3.0), smooth=True)
    pb.torus(0.86, 0.15, segs=10, rsegs=4, loc=(0, 0, 4.4), mapping=("trim", "rope", 1.5))
    pb.torus(0.86, 0.15, segs=10, rsegs=4, loc=(0, 0, 1.4), mapping=("trim", "rope", 1.5))
