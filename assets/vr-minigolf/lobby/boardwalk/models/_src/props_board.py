"""Board / UI group: course-select board, leaderboard wall, signpost, arch nameplate, coming-soon sign.
All built in their own yaw-0 frame with the viewer side on Roblox +Z (south) = Blender -Y."""
import math
from mathutils import Vector
import bwlib as L
from registry import prop, FRONT_SOUTH

BRASS = ("trim", "brass", 4.0)
WOOD = ("trim", "beam", 5.0)
STONE = ("trim", "stone", 4.0)


def front_quad(pb, x0, x1, z0, z1, y, part, mapping=("fit", "parch_panel")):
    """Quad facing -Y (south / viewer), UV left->right, bottom->top."""
    pb.quad([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], mapping=mapping, part=part)


def back_quad(pb, x0, x1, z0, z1, y, part, mapping=("fit", "parch_panel")):
    """Quad facing +Y (north / back)."""
    pb.quad([(x1, y, z0), (x0, y, z0), (x0, y, z1), (x1, y, z1)], mapping=mapping, part=part)


def open_slab(pb, mn, mx, mapping, omit="-y"):
    """Box without its front (-Y) face, so a separately named face can close it without z-fighting."""
    t = L.bmesh.new()
    L.bmesh.ops.create_cube(t, size=1.0)
    size = Vector(mx) - Vector(mn)
    L.bmesh.ops.scale(t, vec=size, verts=t.verts)
    L.bmesh.ops.translate(t, vec=(Vector(mn) + Vector(mx)) / 2, verts=t.verts)
    t.normal_update()
    L.bmesh.ops.delete(t, geom=[f for f in t.faces if (f.normal.y < -0.5 if omit == "-y" else f.normal.y > 0.5)],
                       context="FACES_ONLY")
    pb.add(t, mapping)


def frame_bars(pb, x0, x1, z0, z1, w, y0, y1, mapping=BRASS, segs=1, bevel=0.06):
    """Rectangular frame of bars (width w) around the rect x0..x1, z0..z1, depth y0..y1."""
    pb.box_minmax((x0 - w, y0, z1), (x1 + w, y1, z1 + w), mapping=mapping, bevel=bevel, segs=segs)
    pb.box_minmax((x0 - w, y0, z0 - w), (x1 + w, y1, z0), mapping=mapping, bevel=bevel, segs=segs)
    pb.box_minmax((x0 - w, y0, z0), (x0, y1, z1), mapping=mapping, bevel=bevel, segs=segs)
    pb.box_minmax((x1, y0, z0), (x1 + w, y1, z1), mapping=mapping, bevel=bevel, segs=segs)


def crest(pb, width, z0, rise, depth, y, mapping=BRASS, n=10):
    pts = [(-width / 2, z0)]
    for i in range(n + 1):
        a = math.pi * i / n
        pts.append((-width / 2 * math.cos(a), z0 + rise * math.sin(a)))
    pts.append((width / 2, z0))
    # dedupe the duplicated end points
    poly = [pts[0]] + pts[2:-2] + [pts[-1]]
    pb.prism(poly, depth, loc=(0, y, 0), rot=(90, 0, 0), mapping=mapping, bevel=0.06, segs=1)


def lantern_box(pb, x, y, z0, glass_h=1.0, r=0.5):
    """Brass base + Neon glass + brass hat; returns top z."""
    pb.cyl(r + 0.25, r + 0.25, 0.25, segs=8, loc=(x, y, z0 + 0.125), mapping=("flat", "brass"), smooth=False)
    pb.cyl(r, r, glass_h, segs=8, loc=(x, y, z0 + 0.25 + glass_h / 2), part="neon", smooth=False)
    for k in range(4):                       # 4 chunky brass corner bars around the glass
        a = math.pi / 4 + k * math.pi / 2
        pb.box((0.3, 0.3, glass_h), loc=(x + math.cos(a) * r * 0.95, y + math.sin(a) * r * 0.95,
                                         z0 + 0.25 + glass_h / 2), mapping=("flat", "brass_lo"))
    zt = z0 + 0.25 + glass_h
    pb.cyl(r + 0.3, 0.15, 0.55, segs=8, loc=(x, y, zt + 0.275), mapping=("flat", "brass"), smooth=False)
    return zt + 0.55


# ----------------------------------------------------------------------------- course board
CARD_X = (-8.0, 0.0, 8.0)
CARD_W, CARD_H, CARD_CY = 6.0, 8.0, 5.5
FRONT_Y = -1.0          # front surface of the frame (Roblox z = +1.0)
INSET = 0.15            # card faces sit 0.15 behind the frame surface


def _board_extras(objs):
    import bwlib as LL
    faces = []
    for i in range(3):
        o = next(o for o in objs if o.name == f"card_face_{i + 1}")
        mn, mx = LL.bbox_blender([o])
        size, c = LL.to_roblox_bbox(mn, mx)
        faces.append(dict(name=o.name, courseIndex=i + 1, size=[round(size[0], 3), round(size[1], 3)],
                          insetDepth=INSET, center=[round(v, 3) for v in c], normal=[0, 0, 1],
                          note="flat quad (2 tris), BW_Atlas parchment UVs; RobloxDevBot puts card art on it "
                               "(SurfaceGui/Decal on the +Z face)"))
    return {"cardFaces": faces,
            "cardFaces_note": "center = local Roblox studs from the pivot (base centre). Front frame surface at "
                              "local z=+1.0; faces recessed 0.15 -> z=+0.85, normal +Z (south, toward spawn)."}


@prop("bw_course_board", "board", target=[26, 10, 2], tris_max=6000, front=FRONT_SOUTH,
      notes="Course-select board: stone footing, wooden posts with Neon lanterns, brass frame, 3 recessed card "
            "faces card_face_1..3 (6x8, centres X -8/0/+8, Y 5.5, inset 0.15). Lantern hats reach Y 10.8.")
def course_board(pb):
    pb.box((26, 2, 1.0), loc=(0, 0, 0.5), mapping=STONE, bevel=0.15)
    for s in (-1, 1):
        pb.box((1.6, 2.0, 8.0), loc=(s * 12.2, 0, 5.0), mapping=("trim", "beam", 4.0), bevel=0.2)
        lantern_box(pb, s * 12.2, 0, 9.0, glass_h=0.95, r=0.45)
    # wooden body (behind the card plane)
    pb.box_minmax((-11.4, -0.8, 1.0), (11.4, 0.6, 10.0), mapping=("trim", "deck", 10.0), bevel=0.2)
    # brass front frame: top, bottom, outer stiles, two mullions (front surface at y = -1.0)
    y0, y1 = FRONT_Y, -0.8
    z0, z1 = CARD_CY - CARD_H / 2, CARD_CY + CARD_H / 2
    pb.box_minmax((-11.4, y0, z1), (11.4, y1, 10.0), mapping=BRASS, bevel=0.08, segs=2)
    pb.box_minmax((-11.4, y0, 1.0), (11.4, y1, z0), mapping=BRASS, bevel=0.08, segs=2)
    edges = [(-11.4, CARD_X[0] - CARD_W / 2), (CARD_X[0] + CARD_W / 2, CARD_X[1] - CARD_W / 2),
             (CARD_X[1] + CARD_W / 2, CARD_X[2] - CARD_W / 2), (CARD_X[2] + CARD_W / 2, 11.4)]
    for a, b in edges:
        pb.box_minmax((a, y0, z0), (b, y1, z1), mapping=BRASS, bevel=0.08, segs=2)
    # crest on top centre
    crest(pb, 9.0, 9.95, 0.8, 0.8, -0.3, mapping=("trim", "beam", 4.0))
    crest(pb, 7.0, 9.95, 0.55, 0.9, -0.3, mapping=BRASS)
    # card faces (recess floors)
    for i, cx in enumerate(CARD_X):
        front_quad(pb, cx - CARD_W / 2, cx + CARD_W / 2, z0, z1, FRONT_Y + INSET, f"card_face_{i + 1}",
                   mapping=("fit", "parch"))
    return _board_extras


# ----------------------------------------------------------------------------- leaderboard
@prop("bw_leaderboard_wall", "board", target=[14, 10, 2], tris_max=3000, front=FRONT_SOUTH,
      notes="Parchment panels panel_1..3 (left->right seen from the front) on the +Z face for SurfaceGui. The back "
            "(-Z) carries matching decorative parchment panels so the wall reads from both sides (see README: yaw).")
def leaderboard(pb):
    pb.box((14, 2, 0.8), loc=(0, 0, 0.4), mapping=STONE, bevel=0.15)
    for s in (-1, 1):
        x_in, x_out = s * 5.8, s * 7.0
        pb.box_minmax((min(x_in, x_out), -1.0, 0.8), (max(x_in, x_out), 1.0, 8.6), mapping=("trim", "beam", 4.0),
                      bevel=0.2)
    pb.box_minmax((-5.8, -0.6, 0.8), (5.8, 0.6, 8.6), mapping=("trim", "deck", 10.0), bevel=0.1)
    # brass header plate + crest
    pb.box_minmax((-7.0, -0.9, 8.6), (7.0, 0.9, 9.5), mapping=BRASS, bevel=0.15, segs=2)
    crest(pb, 7.0, 9.45, 0.55, 1.0, 0.0, mapping=BRASS)
    xs = [(-5.5, -2.1), (-1.7, 1.7), (2.1, 5.5)]
    pz0, pz1 = 1.7, 7.7
    for i, (a, b) in enumerate(xs):
        # front: frame bars proud of the wall, named parchment face
        frame_bars(pb, a, b, pz0, pz1, 0.3, -0.8, -0.6)
        front_quad(pb, a, b, pz0, pz1, -0.65, f"panel_{i + 1}", mapping=("fit", "parch"))
        # back: decorative twin
        frame_bars(pb, a, b, pz0, pz1, 0.3, 0.6, 0.8)
        back_quad(pb, a, b, pz0, pz1, 0.65, "atlas", mapping=("fit", "parch"))


# ----------------------------------------------------------------------------- signpost
def arrow_poly(direction, h=0.8, head=0.55):
    pts = [(-1.4, -h / 2), (1.5 - head, -h / 2), (1.5, 0.0), (1.5 - head, h / 2), (-1.4, h / 2)]
    if direction < 0:
        pts = [(-x, y) for x, y in reversed(pts)]
    return pts


@prop("bw_signpost", "board", target=[3, 7, 1], tris_max=800, front=FRONT_SOUTH,
      notes="Arrows (top->bottom): Practice (->east/+X), Leaderboards (<-west/-X), Pier (->east/+X). Text is not "
            "modelled: arrow_face_1..3 are parchment faces for SurfaceGui text on the +Z side.")
def signpost(pb):
    pb.box((1.0, 1.0, 0.6), loc=(0, 0, 0.3), mapping=STONE, bevel=0.12)
    pb.box((0.6, 0.6, 5.85), loc=(0, 0, 0.6 + 5.85 / 2), mapping=("trim", "beam", 3.0), bevel=0.1, segs=1)
    pb.sphere(0.35, loc=(0, 0, 6.65), segs=8, rings=5, mapping=("flat", "brass"))
    for i, (zc, d) in enumerate(((5.6, 1), (4.5, -1), (3.4, 1))):
        poly = [(x, zc + y) for x, y in arrow_poly(d)]
        pb.prism(poly, 0.3, loc=(0, -0.4, 0), rot=(90, 0, 0), mapping=("trim", "beam", 3.0), bevel=0.05, segs=1)
        x0, x1 = (-1.2, 0.85) if d > 0 else (-0.85, 1.2)
        front_quad(pb, x0, x1, zc - 0.28, zc + 0.28, -0.555, f"arrow_face_{i + 1}", mapping=("fit", "parch"))


# ----------------------------------------------------------------------------- nameplate / coming soon
@prop("bw_arch_nameplate", "board", target=[8, 2, 0.5], tris_max=400, front=FRONT_SOUTH,
      notes="Brass plate with parchment face plate_face (+Z) for the course name SurfaceGui. Sits on the arch "
            "lintel front (builder Y 14, Z +2.3 from the arch centre).")
def nameplate(pb):
    pb.box_minmax((-4.0, 0.0, 0.0), (4.0, 0.25, 2.0), mapping=BRASS, bevel=0.1, segs=2)
    open_slab(pb, (-3.6, -0.25, 0.25), (3.6, 0.0, 1.75), ("fit", "parch"))
    front_quad(pb, -3.6, 3.6, 0.25, 1.75, -0.25, "plate_face")
    for s in (-1, 1):   # brass rosettes at the ends
        pb.cyl(0.25, 0.25, 0.12, segs=8, loc=(s * 3.75, -0.06, 1.0), rot=(90, 0, 0), mapping=("flat", "brass_hi"))


@prop("bw_coming_soon_sign", "board", target=[6, 2, 0.5], tris_max=400, front=FRONT_SOUTH,
      notes="Hanging wooden sign with parchment face plate_face (+Z) for 'Coming soon' text; two rope rings on top.")
def coming_soon(pb):
    pb.box_minmax((-3.0, -0.15, 0.0), (3.0, 0.25, 1.3), mapping=("trim", "beam", 3.0), bevel=0.1, segs=1)
    open_slab(pb, (-2.6, -0.25, 0.2), (2.6, -0.15, 1.1), ("fit", "parch"))
    front_quad(pb, -2.6, 2.6, 0.2, 1.1, -0.25, "plate_face")
    for s in (-1, 1):
        pb.torus(0.22, 0.13, segs=8, rsegs=4, loc=(s * 2.2, 0.05, 1.65), rot=(90, 0, 0),
                 mapping=("trim", "rope", 1.0))
