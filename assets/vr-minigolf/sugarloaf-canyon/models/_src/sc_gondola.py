"""Sugarloaf Canyon pass 5: Sunset Gondola haul ropes + support tower (gondola_cable) and the moving cabin
(gondola_cabin). Blender bpy/bmesh builders in the sc_pieces style (Blender coords: x east, y north = Roblox -Z, z up).
Line geometry (attach points, tower, sags, motion) lives in gondola_geom.py so the fitcheck uses the same numbers.
"""
import math
from mathutils import Vector, Matrix
import gondola_geom as G
from sc_pieces import Part, T, beam, rod

ROPE_R = 0.18          # haul rope radius (6-sided tube)
CAB_W, CAB_D = 5.2, 6.0  # cabin body across the line (local X) x along the line (local Z)
CHAMFER = 0.8


def rb(p, o=(0.0, 0.0, 0.0)):
    """Roblox world point -> Blender, relative to Roblox origin o."""
    return Vector((p[0] - o[0], -(p[2] - o[2]), p[1] - o[1]))


def gondola_cable():
    """World-placed static piece. Pivot = bottom bull-wheel centre G.ORIGIN, yaw 0 (geometry baked at world offsets)."""
    pb = Part("gondola_cable", y0=G.ORIGIN[1], role="Sunset Gondola haul ropes (up + down line) + Crown-lip support tower")
    o = G.ORIGIN
    for name, rope in G.ropes().items():
        A, Tw, B = rope
        pts = []
        for P, Q, sag, n in ((A, Tw, G.SAG[0], 28), (Tw, B, G.SAG[1], 10)):
            seg = [G.span_point(P, Q, i / n, sag) for i in range(n + 1)]
            pts += seg if not pts else seg[1:]
        pb.tube("Licorice", [rb(p, o) for p in pts], ROPE_R, segs=6, smooth=True, caps=True)
    # ---- support tower: portal frame across the line, crossbeam above the ropes, sheave cradles under each rope.
    # pass 6 recolour (same primitives, so tris/bbox are unchanged): sun-weathered timber legs, lattice and crossbeam
    # (TimberWeathered), dark iron fittings (leg-top saddles, hanger links, cradle beams), brass bolt plates on the
    # cradles; only the turning sheave wheels keep the red/cream candy bands (moving parts).
    tc = G.tower_centre()
    ground = 190.0
    base = rb((tc[0], ground, tc[2]), o)
    H = G.TOWER_ROPE_Y - ground                      # rope crest height above the ground (31)
    d = Vector((G.UDIR[0], -G.UDIR[1], 0.0))         # Blender plan direction bottom -> top
    x = Vector((d.y, -d.x, 0.0))                     # across the line (right of travel)
    Mt = Matrix(((x.x, d.x, 0, base.x), (x.y, d.y, 0, base.y), (0, 0, 1, base.z), (0, 0, 0, 1)))

    def tp(px, py, pz):
        return Mt @ Vector((px, py, pz))

    top = H + 3.2
    for sx in (-1, 1):
        pb.box("SandBlock", (3.4, 5.2, 1.4), matrix=Mt @ T(sx * 11.0, 0, -0.2))
        for sy in (-1, 1):
            beam(pb, "TimberWeathered", tp(sx * 11.0, sy * 1.9, -0.8), tp(sx * 9.4, sy * 0.6, top), 0.6)
        # lattice: horizontal ties + diagonals on each leg pair
        zs = [0.8, 8.0, 15.0, 22.0, top - 0.6]
        for za, zb in zip(zs, zs[1:]):
            ka, kb = za / (top + 0.8), zb / (top + 0.8)
            xa, xb = 11.0 - 1.6 * ka, 11.0 - 1.6 * kb
            ya, yb = 1.9 - 1.3 * ka, 1.9 - 1.3 * kb
            beam(pb, "TimberWeathered", tp(sx * xa, -ya, za), tp(sx * xb, yb, zb), 0.22)
            beam(pb, "TimberWeathered", tp(sx * xb, -yb, zb), tp(sx * xb, yb, zb), 0.25)
        pb.box("Iron", (1.0, 2.0, 1.0), matrix=Mt @ T(sx * 9.4, 0, top - 1.0))       # iron leg-top saddle
    # timber crossbeam: 7 butted baulks alternating weathered / older timber (separate meshes, so the butt faces are
    # kept and the tri count stays identical to pass 5)
    n = 7
    for k in range(n):
        xa = -10.5 + 21.0 * k / n
        pb.box("TimberWeathered" if k % 2 == 0 else "Timber", (21.0 / n, 1.2, 1.2), matrix=Mt @ T(xa + 10.5 / n, 0, top + 0.6))
    for sx in (-1, 1):
        rx = sx * G.WHEEL_R
        # inboard hanger link from the crossbeam down to the cradle (the cabin hanger passes on the outboard side)
        lx = rx - sx * 0.55
        pb.box("Iron", (0.3, 0.3, top - (H - 0.9)), matrix=Mt @ T(lx, 0, (top + H - 0.9) / 2))
        pb.box("Iron", (0.35, 5.4, 0.3), matrix=Mt @ T(rx - sx * 0.3, 0, H - 0.75))
        for k, wy in enumerate((-1.95, -0.65, 0.65, 1.95)):
            m = Mt @ T(rx, wy, H - ROPE_R - 0.45) @ Matrix.Rotation(math.radians(90), 4, "Y")
            pb.torus("PepRed" if k % 2 == 0 else "MintWhite", 0.4, 0.08, 10, 4, matrix=m)     # turning sheaves
        pb.box("Brass", (0.2, 1.2, 0.8), matrix=Mt @ T(rx - sx * 0.6, 0, H - 0.75))            # brass bolt plate
    return [pb]


def _octagon(w, d, c, s=1.0):
    hw, hd = w / 2 * s, d / 2 * s
    c *= s
    return [(hw - c, -hd), (hw, -hd + c), (hw, hd - c), (hw - c, hd), (-hw + c, hd), (-hw, hd - c), (-hw, -hd + c),
            (-hw + c, -hd)]


def gondola_cabin():
    """Moving piece. Pivot = cable grip point (on the haul rope centreline); body hangs HANG below it.
    Front (Roblox local -Z = Blender +Y) faces the direction of travel; the hanger arm steps out to local +X
    (outboard of the rope on both lines) so it clears the tower sheave cradles."""
    pb = Part("gondola_cabin", y0=0.0, role="seated enclosed cabin: hanger + grip (meshes *_hanger) and body")
    zb = -G.HANG                                     # -6.4 floor bottom
    # ---- body (stacked chamfered octagon slabs)
    def slab(mat, z0, z1, s=1.0):
        pb.prism(mat, _octagon(CAB_W, CAB_D, CHAMFER, s), z1 - z0, loc=(0, 0, (z0 + z1) / 2))
    slab("PepRed", zb, zb + 0.6, 0.94)               # under-skirt
    slab("MintWhite", zb + 0.6, zb + 1.2)
    slab("PepRed", zb + 1.2, zb + 1.6)
    slab("MintWhite", zb + 1.6, zb + 2.1)
    slab("Window", zb + 2.1, zb + 3.9, 0.97)         # glazing band
    slab("PepRed", zb + 3.9, zb + 4.3)
    slab("MintWhite", zb + 4.3, zb + 4.55, 1.05)     # roof overhang
    slab("PepRed", zb + 4.55, zb + 4.7, 0.7)         # roof cap
    # window pillars at the 8 octagon corners
    for (px, py) in _octagon(CAB_W, CAB_D, CHAMFER, 0.985):
        pb.box("MintWhite", (0.32, 0.32, 1.8), loc=(px, py, zb + 3.0))
    # sliding door outline on both long sides (local +-X) + door handles
    for sx in (-1, 1):
        xx = sx * (CAB_W / 2 + 0.02)
        for yy in (-1.1, 1.1):
            pb.box("Licorice", (0.06, 0.12, 3.6), loc=(xx, yy, zb + 2.6))
        pb.box("Licorice", (0.06, 2.3, 0.12), loc=(xx, 0, zb + 0.8))
        pb.box("GumLemon", (0.12, 0.5, 0.12), loc=(xx + sx * 0.05, 0.6, zb + 2.0))
    # ---- hanger + grip (separate *_hanger meshes)
    roof = zb + 4.7
    pb.box("Iron#hanger", (0.7, 1.6, 0.6), loc=(0, 0, 0))                          # grip jaws around the rope
    pb.box("PepRed#hanger", (0.8, 1.0, 0.25), loc=(0, 0, 0.42))                    # grip cap
    beam(pb, "Iron#hanger", (0.3, 0, 0), (1.15, 0, 0), 0.35)
    beam(pb, "Iron#hanger", (1.15, 0, 0.17), (1.15, 0, -1.1), 0.35)
    beam(pb, "Iron#hanger", (1.15, 0, -1.1), (0, 0, roof + 0.35), 0.35)
    beam(pb, "Iron#hanger", (0, 0, roof + 0.4), (0, 0, roof - 0.05), 0.4)
    pb.box("Iron#hanger", (0.4, 3.4, 0.3), loc=(0, 0, roof + 0.1))                 # roof saddle
    pb.box("Iron#hanger", (2.6, 0.3, 0.25), loc=(0, 0, roof + 0.1))
    return [pb]
