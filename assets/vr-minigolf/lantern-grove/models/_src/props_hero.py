"""P1 static hero props."""
import math, random
import bmesh
from mathutils import Vector, Matrix, noise
from registry import prop
from lglib import M, R, TAU, superellipse_ring, shell, apply_boolean
import lglib
from props_moving import mushroom_cap, ring_box


def RS(sx, sy, sz):
    """Roblox box size -> Blender size."""
    return (sx, sz, sy)


def arch_poly(w, h_wall, h_top, bottom=0.0, n=10):
    """Arch outline in (u, v): width w, vertical sides to h_wall, elliptical top to h_top."""
    pts = [(-w / 2, bottom), (-w / 2, h_wall)]
    for i in range(1, n):
        a = math.pi - math.pi * i / n
        pts.append((w / 2 * math.cos(a), h_wall + (h_top - h_wall) * math.sin(a)))
    pts += [(w / 2, h_wall), (w / 2, bottom)]
    return pts


def arch_band(w, h_wall, h_top, t, bottom=0.0, n=10):
    """U-shaped band polygon around an arch opening (thickness t)."""
    inner = arch_poly(w, h_wall, h_top, bottom, n)
    outer = arch_poly(w + 2 * t, h_wall, h_top + t, bottom, n)
    return outer + list(reversed(inner))


# local prism frame: poly (u,v) -> Blender (Y,Z), extrude along X
FRAME_X = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
# poly (u,v) -> Blender (X,Z), extrude along -Y  (faces -Y = Roblox +Z)
FRAME_Y = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def window(pb, center, normal, r=0.35, frame_mat="Oak"):
    q = Vector((0, 0, 1)).rotation_difference(Vector(normal).normalized())
    m = Matrix.Translation(center) @ q.to_matrix().to_4x4()
    pb.cyl("Glow", r, r, 0.12, 12, matrix=m, smooth=False)
    pb.torus(frame_mat, r + 0.05, 0.07, 12, 5, matrix=m @ Matrix.Translation((0, 0, 0.05)))
    pb.box(frame_mat, (r * 2, 0.06, 0.06), matrix=m @ Matrix.Translation((0, 0, 0.07)))
    pb.box(frame_mat, (0.06, r * 2, 0.06), matrix=m @ Matrix.Translation((0, 0, 0.07)))


# ============================================================================ torii gate
@prop("lantern_torii_gate", ["H1"], "P1", target=[9, 7, 1.2], group="hero",
      notes="Welcome arch over the H1 ramp. Pillars at x=+-4.4 stand outside the visual rails (rail outer faces at "
            "x=+-4.0; plinths inner face 4.05). 2 lanterns (1.6 tall) hang from the tie beam at x=+-1.9.",
      front="symmetric; spans local X",
      placements=[dict(hole="H1", pos=[0, 0, -21], yaw=0, note="anchor lantern_gate; ground at the ramp side")])
def torii(pb):
    for sx in (-1, 1):
        x = sx * 4.4
        pb.box("Slate", (0.66, 0.66, 0.4), loc=(x, 0, 0.2), bevel=0.08)
        pb.cyl("Lacquer", 0.29, 0.25, 6.0, 12, loc=(x, 0, 0.4 + 3.0))
        pb.cyl("RootBark", 0.31, 0.31, 0.3, 12, loc=(x, 0, 0.55), smooth=False)
    # nuki (tie beam) and shimaki
    pb.box("Lacquer", (9.2, 0.32, 0.42), loc=(0, 0, 5.3), bevel=0.05)
    pb.box("Lacquer", (9.0, 0.5, 0.32), loc=(0, 0, 6.28), bevel=0.05)
    # kasagi: curved top beam with upturned tips
    secs = []
    secs2 = []
    for i in range(17):
        x = -4.75 + 9.5 * i / 16
        u = abs(x) / 4.75
        zc = 6.62 + 0.32 * u ** 3
        sec = [Vector((x, -0.38, zc - 0.17)), Vector((x, 0.38, zc - 0.17)), Vector((x, 0.38, zc + 0.17)),
               Vector((x, -0.38, zc + 0.17))]
        secs.append(sec)
        sec2 = [Vector((x, -0.42, zc + 0.17)), Vector((x, 0.42, zc + 0.17)), Vector((x, 0.38, zc + 0.35)),
                Vector((x, -0.38, zc + 0.35))]
        secs2.append(sec2)
    pb.loft("Lacquer", secs, smooth=False)
    pb.loft("RootBark", secs2, smooth=False)
    # gakuzuka plaque
    pb.box("RootBark", (0.9, 0.2, 0.85), loc=(0, 0, 5.85), bevel=0.04)
    pb.box("Oak", (0.7, 0.24, 0.65), loc=(0, 0, 5.85), bevel=0.03)
    pb.lantern(0.42, loc=(0, -0.14, 5.62), hook=False)
    # hanging lanterns
    for sx in (-1, 1):
        x = sx * 1.9
        pb.cyl("RootBark", 0.025, 0.025, 0.25, 6, loc=(x, 0, 4.98), smooth=False)
        pb.lantern(1.6, loc=(x, 0, 3.25))


# ============================================================================ mushroom houses
def stem_windows_door(pb, stem_r_at, door_angle=-90, windows=((-40, 3.0), (40, 3.0), (150, 3.4)), door_h=1.8,
                      door_w=1.1):
    """Door + round windows on a lathe stem; stem_r_at(z) gives radius at height z."""
    a = math.radians(door_angle)
    nrm = Vector((math.cos(a), math.sin(a), 0))
    r0 = stem_r_at(0.9)
    base = nrm * (r0 - 0.06)
    rot = Matrix.Rotation(a + math.pi / 2, 4, "Z")  # FRAME_Y faces -Y; rotate so it faces nrm
    mt = Matrix.Translation(base) @ rot @ FRAME_Y
    pb.prism("RootBark", arch_poly(door_w + 0.3, door_h * 0.6, door_h + 0.15, 0.0), 0.2, matrix=mt)
    pb.prism("Oak", arch_poly(door_w, door_h * 0.6, door_h, 0.0), 0.2, matrix=mt @ Matrix.Translation((0, 0, 0.08)))
    pb.sphere("Iron", 0.07, matrix=mt @ Matrix.Translation((door_w * 0.3, 0.9, 0.22)), segs=6, rings=4)
    for (deg, z) in windows:
        aw = math.radians(deg + door_angle + 90)
        n = Vector((math.cos(aw), math.sin(aw), 0))
        window(pb, n * (stem_r_at(z) - 0.02) + Vector((0, 0, z)), n)
    return nrm


@prop("mushroom_house_medium", ["H3", "H4"], "P1", target=[7.5, 9.5, 7.5], group="hero",
      notes="Red-cap mushroom house with arched door, porch awning + lantern, 3 round glowing windows. Reuse at "
            "scale 0.9-1.1 and recolour the ToadRed cap part (alt colour Pumpkin #E8862E) for variety.",
      placements=[
          dict(hole="H3", pos=[26, 0, -14], yaw=-90, scale=0.95, note="house_2 (door faces -X toward the course)"),
          dict(hole="H4", pos=[-12, 0, -21], yaw=90, scale=1.05, note="mushroom_house_L, door faces +X"),
          dict(hole="H4", pos=[12, 0, -24], yaw=-90, scale=0.95, note="mushroom_house_R, door faces -X, cap Pumpkin"),
      ])
def mushroom_house_medium(pb):
    prof = [(2.7, 0), (2.5, 0.35), (2.3, 1.2), (2.2, 2.6), (2.1, 4.0), (1.95, 5.2), (0, 5.2)]

    def r_at(z):
        for (r1, z1), (r2, z2) in zip(prof, prof[1:]):
            if z1 <= z <= z2:
                return r1 + (r2 - r1) * (z - z1) / (z2 - z1 + 1e-9)
        return prof[-2][0]
    pb.lathe("Cream", prof, 18, wobble=0.025, seed=2)
    mushroom_cap(pb, 3.6, 4.85, 4.15, spots=9, seed=7, segs=20)
    nrm = stem_windows_door(pb, r_at)
    # porch: deck, two posts, little awning, lantern
    pb.box("Oak", (2.0, 1.1, 0.18), loc=(0, -2.85, 0.09), bevel=0.04)
    pb.box("Slate", (1.0, 0.5, 0.12), loc=(0, -3.55, 0.06), bevel=0.04)
    for sx in (-1, 1):
        pb.box("Oak", (0.14, 0.14, 2.3), loc=(sx * 0.85, -3.25, 1.15 + 0.18), bevel=0.02)
    pb.box("Shingle", (2.2, 1.2, 0.12), loc=(0, -2.95, 2.55), rot=(-18, 0, 0), bevel=0.03)
    pb.torus("Iron", 0.05, 0.015, 8, 4, loc=(0.85, -3.25, 2.36), rot=(90, 0, 0))
    pb.lantern(0.62, loc=(0.85, -3.25, 1.68))
    # chimney on the cap
    pb.cyl("Slate", 0.28, 0.24, 1.4, 8, loc=(-1.6, 1.2, 8.1), rot=(-8, -10, 0), smooth=False)
    pb.cyl("RootBark", 0.32, 0.32, 0.14, 8, loc=(-1.72, 1.3, 8.8), rot=(-8, -10, 0), smooth=False)
    # moss and pebbles at the base
    for k in range(6):
        a = TAU * k / 6 + 0.4
        if abs(math.sin(a) + 1) < 0.3:  # keep the door clear
            continue
        pb.rock("Moss", (1.1, 0.8, 0.35), loc=(math.cos(a) * 2.6, math.sin(a) * 2.6, 0), rot=(0, 0, math.degrees(a)),
                seed=k + 3, amp=0.1)


TUNNEL_W, TUNNEL_WALL, TUNNEL_H = 7.0, 2.1, 3.0


@prop("mushroom_house_large_tunnel", ["H3"], "P1", target=[10, 12, 10], group="hero",
      notes=("Landmark house; the felt tunnel runs through its stem along local X: opening 7.0 wide (local Z, "
             "+-3.5), 3.0 high at the crown (2.1 at the walls), 5.0 deep (local X -2.5..+2.5). Rails rail4/rail12 "
             "run into the stem walls. Door + porch lantern on the +Z side."),
      front="tunnel along local X; door faces +Z", view="x",
      placements=[dict(hole="H3", pos=[8.5, 0, -12], yaw=0, note="anchor stem_house = tunnel felt centre")])
def mushroom_house_large(pb):
    heights = [(0.0, 1.07), (0.4, 1.02), (1.5, 0.99), (3.0, 0.98), (4.5, 0.96), (5.6, 0.92), (6.6, 0.84)]
    secs = []
    for z, s in heights:
        secs.append([Vector((p.x * s, p.y * s, z)) for p in
                     superellipse_ring(2.95, 4.75, 4.0, 40, 0, wob=lambda a, zz: 1 + 0.015 * math.sin(a * 9 + z))])
    pb.loft("Cream", secs, smooth=True)
    mushroom_cap(pb, 5.1, 6.0, 6.0, spots=12, seed=11, segs=24)
    # portal frames on both flat faces
    for sx in (-1, 1):
        mt = Matrix.Translation((sx * 2.55, 0, 0)) @ FRAME_X
        pb.prism("Oak", arch_band(TUNNEL_W, TUNNEL_WALL, TUNNEL_H, 0.32, 0.0, 12), 0.22, matrix=mt)
        pb.box("RootBark", (0.3, 0.6, 0.5), loc=(sx * 2.62, 0, TUNNEL_H + 0.2), bevel=0.05)  # keystone
        window(pb, Vector((sx * 2.52, 0, 4.7)), (sx, 0, 0), r=0.45)
        for sy in (-1, 1):
            # bracket lanterns beside the portal (outside the opening)
            pb.box("Oak", (0.5, 0.12, 0.12), loc=(sx * 2.75, sy * 4.15, 3.4), bevel=0.02)
            pb.lantern(0.6, loc=(sx * 2.95, sy * 4.15, 2.62))
    # side windows (asymmetric so the wall doesn't read as a face)
    for (x, sy, z, r) in ((-1.3, -1, 4.6, 0.42), (1.5, -1, 3.2, 0.34), (0.9, 1, 4.4, 0.42), (-1.2, 1, 2.6, 0.32)):
        window(pb, Vector((x, sy * 4.5, z)), (0, sy, 0), r=r)
    # ground-level door on the -Y (Roblox +Z) outer wall: outside the felt, which ends at |y|=3.5
    pb.prism("RootBark", arch_poly(1.35, 1.2, 2.05, 0.0), 0.24, matrix=Matrix.Translation((0.3, -4.62, 0.0)) @ FRAME_Y)
    pb.prism("Oak", arch_poly(1.1, 1.15, 1.9, 0.0), 0.24, matrix=Matrix.Translation((0.3, -4.7, 0.0)) @ FRAME_Y)
    pb.sphere("Iron", 0.07, loc=(0.65, -4.86, 0.95), segs=6, rings=4)
    pb.box("Slate", (1.4, 0.6, 0.12), loc=(0.3, -5.1, 0.06), bevel=0.04)
    pb.box("Oak", (0.12, 0.6, 0.12), loc=(-0.75, -4.95, 2.35))
    pb.lantern(0.6, loc=(-0.75, -5.2, 1.55))
    pb.cyl("Slate", 0.32, 0.27, 1.6, 8, loc=(2.3, 2.0, 11.0), rot=(-10, 12, 0), smooth=False)

    def post(root, objs):
        stem = [o for o in objs if o.name.endswith("__Cream")][0]

        def cut_slabs(c):
            for sx in (-1, 1):
                c.box("Cut", (3, 12, 6.0), loc=(sx * (2.5 + 1.5), 0, 6.0 / 2 - 0.2))

        def cut_tunnel(c):
            c.prism("Cut", arch_poly(TUNNEL_W, TUNNEL_WALL, TUNNEL_H, -0.5, 16), 8.0, matrix=FRAME_X)
        apply_boolean(stem, cut_slabs)
        apply_boolean(stem, cut_tunnel)
    return post


# ============================================================================ water mill
MILL_ORIGIN = (8.5, -1.0, 3.0)


@prop("water_mill_house", ["H6"], "P1", target=[9, 10, 8], group="hero",
      notes=("Timber-frame mill on a stone plinth, thatch roof. Built in H6 hole-local coords: footprint x 4.2..12.8, "
             "z -1..7 (north wall at z=-1, behind the millrace; anchor said [7.5,0,0] but that overlaps the "
             "millrace hazard and rail2, so the house sits 3 studs south). The wheel axle (course x 7.5, y 3.6) "
             "enters the iron bearing boss on the north wall. Plinth bottom y=-1 (below the water at -0.8)."),
      front="north wall (local -Z) faces the course",
      placements=[dict(hole="H6", pos=list(MILL_ORIGIN), yaw=0)])
def water_mill(pb):
    pb.set_origin_at(R(*MILL_ORIGIN))
    x0, x1, z0, z1 = 4.2, 12.8, -1.0, 7.0
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    # plinth
    pb.box("Slate", RS(8.6, 1.6, 8.0), loc=R(cx, -0.2, cz), bevel=0.12)
    rnd = random.Random(4)
    for k in range(14):
        side = k % 4
        if side == 0:
            p = (rnd.uniform(x0, x1), rnd.uniform(-0.8, 0.4), z0)
        elif side == 1:
            p = (rnd.uniform(x0, x1), rnd.uniform(-0.8, 0.4), z1)
        elif side == 2:
            p = (x0, rnd.uniform(-0.8, 0.4), rnd.uniform(z0, z1))
        else:
            p = (x1, rnd.uniform(-0.8, 0.4), rnd.uniform(z0, z1))
        pb.box("Limestone", (0.9, 0.9, 0.45), loc=R(*p), rot=(0, 0, rnd.uniform(0, 30)), bevel=0.08)
    # ground floor plaster + timber frame
    pb.box("Cream", RS(8.0, 4.4, 7.4), loc=R(cx, 2.8, cz))
    for (x, z) in ((x0 + 0.3, z0 + 0.3), (x1 - 0.3, z0 + 0.3), (x0 + 0.3, z1 - 0.3), (x1 - 0.3, z1 - 0.3)):
        pb.box("Oak", RS(0.4, 4.6, 0.4), loc=R(x, 2.8, z), bevel=0.04)
    for y in (0.75, 4.95):
        pb.box("Oak", RS(8.3, 0.3, 0.3), loc=R(cx, y, z0 + 0.3), bevel=0.03)
        pb.box("Oak", RS(8.3, 0.3, 0.3), loc=R(cx, y, z1 - 0.3), bevel=0.03)
        pb.box("Oak", RS(0.3, 0.3, 7.7), loc=R(x0 + 0.3, y, cz), bevel=0.03)
        pb.box("Oak", RS(0.3, 0.3, 7.7), loc=R(x1 - 0.3, y, cz), bevel=0.03)
    # diagonal braces on the north face (away from the axle boss)
    for (xa, xb) in ((x0 + 0.4, x0 + 2.2), (x1 - 0.4, x1 - 2.2)):
        pb.tube("Oak", [R(xa, 0.9, z0 + 0.12), R(xb, 4.8, z0 + 0.12)], 0.12, 4, smooth=False)
    # upper floor (jettied)
    pb.box("Cream", RS(8.6, 1.5, 8.0), loc=R(cx, 5.75, cz))
    for y in (5.05, 6.95):
        pb.box("Oak", RS(8.8, 0.25, 8.2), loc=R(cx, y, cz), bevel=0.03) if y == 5.05 else None
    for x in (x0, x0 + 2.15, cx, x1 - 2.15, x1):
        for z in (z0 - 0.02, z1 + 0.02):
            pb.box("Oak", RS(0.25, 1.5, 0.12), loc=R(x, 5.75, z))
    # thatch roof (gable along X)
    roof = [(-4.15, 0), (4.15, 0), (0.25, 2.4), (-0.25, 2.4)]
    pb.prism("Thatch", roof, 9.0, matrix=Matrix.Translation(R(cx, 6.4, cz)) @ FRAME_X)
    pb.box("RootBark", RS(9.1, 0.3, 0.7), loc=R(cx, 8.85, cz), bevel=0.1)
    # gable-end plaster triangles are covered by the thatch prism; add an eave trim line
    for z in (cz - 4.35, cz + 4.35):
        pb.box("RootBark", RS(9.0, 0.18, 0.25), loc=R(cx, 6.45, z))
    # chimney
    pb.box("Slate", RS(0.9, 2.2, 0.9), loc=R(x1 - 1.6, 8.0, cz + 1.6), bevel=0.06)
    # windows (north + south + east)
    for (x, y) in ((11.0, 2.7), (5.6, 5.75), (10.8, 5.75)):
        pb.box("Glow", RS(1.0, 1.0, 0.12), loc=R(x, y, z0 - 0.02))
        pb.box("Oak", RS(1.2, 0.12, 0.2), loc=R(x, y - 0.55, z0 - 0.06))
        pb.box("Oak", RS(1.2, 0.12, 0.2), loc=R(x, y + 0.55, z0 - 0.06))
        pb.box("Oak", RS(0.1, 1.0, 0.18), loc=R(x, y, z0 - 0.06))
    for (x, y) in ((6.0, 2.8), (11.0, 5.75)):
        pb.box("Glow", RS(1.0, 1.0, 0.12), loc=R(x, y, z1 + 0.02))
        pb.box("Oak", RS(0.1, 1.0, 0.18), loc=R(x, y, z1 + 0.06))
    pb.box("Glow", RS(0.12, 0.9, 1.0), loc=R(x1 + 0.02, 5.75, cz))
    # door on the south side + lantern
    pb.prism("RootBark", arch_poly(1.6, 1.6, 2.5, 0.0), 0.2, matrix=Matrix.Translation(R(8.5, 0.6, z1 + 0.05)) @ FRAME_Y)
    pb.prism("Oak", arch_poly(1.3, 1.5, 2.3, 0.0), 0.2, matrix=Matrix.Translation(R(8.5, 0.6, z1 + 0.12)) @ FRAME_Y)
    pb.box("Oak", RS(0.12, 0.12, 0.35), loc=R(9.9, 3.1, z1 + 0.2))
    pb.lantern(0.7, loc=R(9.9, 2.32, z1 + 0.33))
    # axle bearing boss on the north wall at the wheel axle
    ax, ay = 7.5, 3.6
    pb.cyl("RootBark", 0.75, 0.75, 0.42, 12, loc=R(ax, ay, z0 - 0.2), rot=(90, 0, 0), smooth=False)
    pb.cyl("Iron", 0.5, 0.5, 0.5, 12, loc=R(ax, ay, z0 - 0.3), rot=(90, 0, 0), smooth=False)
    pb.box("Oak", RS(2.2, 0.3, 0.25), loc=R(ax, ay + 0.95, z0 - 0.1), bevel=0.03)
    pb.box("Oak", RS(2.2, 0.3, 0.25), loc=R(ax, ay - 0.95, z0 - 0.1), bevel=0.03)
    # wall-mounted lantern on the north face for the course side
    pb.box("Oak", RS(0.12, 0.12, 0.35), loc=R(4.9, 4.4, z0 - 0.2))
    pb.lantern(0.7, loc=R(4.9, 3.62, z0 - 0.33))


# ============================================================================ bridges (H5)
def felt_h5_root(z):
    return 0.4 - 0.4 * abs(z + 21.5) / 6.5


RB_ORIGIN = (0.0, -2.6, -21.5)


@prop("root_bridge_arched", ["H5"], "P1", target=[3.5, 3, 14], group="hero",
      notes=("Gnarled root arch under the rail-less felt strip (root1/root2, 1.8 wide). Deck top is 0.2 below the "
             "felt surface (felt slab sits on it) and follows the 0.4 peak; deck 2.2 wide. No root rises above the "
             "felt top (no visual rails). Roots dive into the banks at both ends."),
      front="runs along local Z",
      placements=[dict(hole="H5", pos=list(RB_ORIGIN), yaw=0)])
def root_bridge(pb):
    pb.set_origin_at(R(*RB_ORIGIN))
    zs = [-28.4 + 13.8 * i / 28 for i in range(29)]
    secs = []
    for z in zs:
        top = min(felt_h5_root(max(min(z, -15), -28)), 0.4) - 0.2
        secs.append([R(-1.1, top - 0.38, z), R(1.1, top - 0.38, z), R(1.1, top, z), R(-1.1, top, z)])
    pb.loft("RootBark", secs, smooth=False)
    # side roots hugging the deck edge (tops stay >=0.05 below the felt)
    for sx in (-1, 1):
        for j, (xo, yo, rr) in enumerate(((1.12, -0.36, 0.26), (1.3, -0.72, 0.3))):
            pts = []
            for z in zs:
                top = felt_h5_root(max(min(z, -15), -28)) - 0.2
                pts.append(R(sx * (xo + 0.06 * math.sin(z * 1.7 + j)), top + yo + 0.04 * math.sin(z * 2.3), z))
            pb.tube("RootBark", pts, rr, 7, wobble=0.18, seed=sx * 3 + j)
    # arch roots underneath: low at the banks, meeting the deck in the middle
    for k, (x, rr, sag) in enumerate(((-0.8, 0.32, 1.55), (0.0, 0.36, 1.75), (0.8, 0.32, 1.5), (-0.4, 0.24, 1.2),
                                       (0.45, 0.24, 1.3))):
        pts = []
        for i in range(25):
            z = -28.6 + 14.2 * i / 24
            u = (z + 21.5) / 7.1
            top = felt_h5_root(max(min(z, -15), -28)) - 0.2 - 0.38
            pts.append(R(x + 0.25 * math.sin(u * 4 + k), top - rr * 0.6 - sag * u * u, z))
        pb.tube("RootBark", pts, [rr * (1.6 if abs(i - 12) > 9 else 1.0) for i in range(25)], 7, wobble=0.2, seed=k)
    # roots wrapping over the deck edges (stay below the felt top)
    for k in range(6):
        z0 = -27.0 + k * 2.2
        sx = 1 if k % 2 else -1
        pts = []
        for i in range(7):
            u = i / 6
            z = z0 + u * 1.6
            top = felt_h5_root(max(min(z, -15), -28)) - 0.2
            ang = math.pi * u
            pts.append(R(sx * (1.15 + 0.15 * math.sin(ang)), top - 0.08 - 0.9 * (1 - math.sin(ang)) * 0.8, z))
        pb.tube("RootBark", pts, [0.12, 0.16, 0.17, 0.17, 0.16, 0.12, 0.08], 6, wobble=0.15, seed=40 + k)
    # hanging tendrils + moss
    rnd = random.Random(6)
    for k in range(8):
        z = rnd.uniform(-25.5, -17.5)
        x = rnd.choice((-1, 1)) * rnd.uniform(0.9, 1.3)
        top = felt_h5_root(z) - 0.6
        pb.tube("RootBark", [R(x, top, z), R(x * 1.05, top - 0.5, z + 0.1), R(x * 1.1, top - 0.9, z)], [0.08, 0.06, 0.02], 5)
    for z, sx in ((-26.0, -1), (-22.5, 1), (-19.5, -1), (-16.5, 1)):
        top = felt_h5_root(z) - 0.2
        pb.sphere("Moss", 0.45, loc=R(sx * 1.35, top - 0.5, z), scale=(0.7, 2.4, 0.5), segs=8, rings=4)


CB_ORIGIN = (-10.5, -1.4, -21.5)


@prop("covered_bridge", ["H5"], "P1", target=[7, 6, 14], group="hero",
      notes=("Roofed plank bridge over the 'covered' felt (5 wide, x -13..-8). Deck top 0.2 under the felt. Side "
             "walls/posts at x=+-3.25 from centre are outside the collision rails (rail outer faces at +-3.0), so "
             "the inside is 6.0 clear between posts; headroom 3.3. Lanterns hang at both portals."),
      front="runs along local Z",
      placements=[dict(hole="H5", pos=list(CB_ORIGIN), yaw=0)])
def covered_bridge(pb):
    pb.set_origin_at(R(*CB_ORIGIN))
    cx = -10.5
    # deck planks (across X), stringers, stone abutments and a mid pier
    n = 28
    for i in range(n):
        z = -28.5 + 14.0 * (i + 0.5) / n
        pb.box("Oak", RS(6.9, 0.2, 14.0 / n - 0.04), loc=R(cx, -0.3, z), bevel=0.02)
    for sx in (-1, 1):
        pb.box("RootBark", RS(0.35, 0.45, 14.0), loc=R(cx + sx * 2.6, -0.62, -21.5), bevel=0.05)
    for z in (-28.0, -15.0):
        pb.box("Slate", RS(7.2, 1.2, 1.2), loc=R(cx, -0.8 - 0.2, z), bevel=0.12)
    pb.box("Slate", RS(1.4, 1.0, 1.4), loc=R(cx, -0.9, -21.5), bevel=0.15)
    pb.box("Slate", RS(5.6, 0.25, 0.8), loc=R(cx, -0.55, -21.5), bevel=0.06)
    # posts, side walls, X-braces
    zpos = [-28.2, -24.85, -21.5, -18.15, -14.8]
    for sx in (-1, 1):
        x = cx + sx * 3.25
        for z in zpos:
            pb.box("Oak", RS(0.32, 3.75, 0.32), loc=R(x, 3.35 / 2 - 0.2 + 0.2, z), bevel=0.04)
        pb.box("Oak", RS(0.2, 0.18, 14.0), loc=R(x, 1.1, -21.5), bevel=0.03)
        pb.box("Oak", RS(0.12, 1.0, 13.4), loc=R(x + sx * 0.05, 0.4, -21.5))
        for za, zb in zip(zpos, zpos[1:]):
            pb.tube("RootBark", [R(x + sx * 0.12, 1.15, za), R(x + sx * 0.12, 3.2, zb)], 0.07, 4, smooth=False)
            pb.tube("RootBark", [R(x + sx * 0.12, 3.2, za), R(x + sx * 0.12, 1.15, zb)], 0.07, 4, smooth=False)
        pb.box("Oak", RS(0.3, 0.3, 14.2), loc=R(x, 3.4, -21.5), bevel=0.04)
    # trusses
    for z in zpos:
        pb.box("Oak", RS(6.8, 0.25, 0.25), loc=R(cx, 3.4, z), bevel=0.03)
        pb.box("Oak", RS(0.2, 1.2, 0.2), loc=R(cx, 4.0, z))
    # gable roof (ridge along Z)
    for sx in (-1, 1):
        ang = math.degrees(math.atan2(1.25, 3.75))
        pb.box("Shingle", RS(4.05, 0.18, 14.4), loc=R(cx + sx * 1.92, 4.05 + 0.08, -21.5),
               rot=(0, sx * ang, 0), bevel=0.04)
        for k in range(5):
            # shingle rows
            t = (k + 0.5) / 5
            pb.box("Shingle", RS(0.1, 0.1, 14.4), loc=R(cx + sx * (0.3 + t * 3.4), 4.6 - t * 1.13 + 0.18, -21.5),
                   rot=(0, sx * ang, 0))
    pb.box("RootBark", RS(0.4, 0.3, 14.6), loc=R(cx, 4.75, -21.5), bevel=0.06)
    # gable boards
    for z in (-28.45, -14.55):
        pb.prism("Oak", [(-3.4, 0), (3.4, 0), (0, 1.15)], 0.1, matrix=Matrix.Translation(R(cx, 3.5, z)) @ FRAME_Y)
    # lanterns: one centre lantern per portal + corner brackets
    for z in (-28.3, -14.7):
        pb.lantern(1.1, loc=R(cx, 2.15, z))
        for sx in (-1, 1):
            pb.box("Oak", RS(0.35, 0.12, 0.12), loc=R(cx + sx * 3.42, 2.9, z))
            pb.lantern(0.6, loc=R(cx + sx * 3.5, 2.15, z))


# ============================================================================ cascade + small waterfall
def flat_rock(pb, mat, size, loc, top, seed, amp=0.08, ico=2, cube=0.65):
    """Boxy displaced rock (blend of cube and sphere) whose top is clamped flat at absolute height `top`."""
    t = bmesh.new()
    bmesh.ops.create_icosphere(t, subdivisions=ico, radius=0.5)
    off = Vector((seed * 3.1, seed * 1.3, seed * 2.7))
    for v in t.verts:
        c = v.co / (2 * max(abs(v.co.x), abs(v.co.y), abs(v.co.z)))
        v.co = v.co.lerp(c, cube)
        k = amp * 2 * noise.noise(v.co * 2.0 + off)
        v.co.x *= 1 + k
        v.co.y *= 1 + k
        v.co.z *= 1 + k * 0.1
    bmesh.ops.scale(t, vec=Vector(size), verts=t.verts)
    bmesh.ops.translate(t, vec=Vector(loc), verts=t.verts)
    for v in t.verts:
        v.co.z = max(0.0, min(v.co.z, top))
    bmesh.ops.remove_doubles(t, verts=t.verts, dist=0.02)
    pb.add(mat, t, None, False)


def fall_sheet(pb, y_lip, z_top, y_bot, z_bot, w, x=0.0, segs=8, mat="Foam"):
    secs = []
    for i in range(segs + 1):
        u = i / segs
        y = y_lip + (y_bot - y_lip) * (1 - (1 - u) ** 2) * 0.9 + 0.0
        z = z_top + (z_bot - z_top) * u ** 1.6
        ww = w * (1 + 0.12 * u)
        secs.append([Vector((x - ww / 2, y, z)), Vector((x + ww / 2, y, z)), Vector((x + ww / 2, y - 0.1, z)),
                     Vector((x - ww / 2, y - 0.1, z))])
    pb.loft("Water", secs, smooth=True)
    for fx in (-0.3, 0.05, 0.33):
        pts = [Vector((x + fx * w * (1 + 0.12 * i / segs), sec[0].y - 0.12, sec[0].z)) for i, sec in enumerate(secs)]
        pb.tube(mat, pts, 0.06 * w, 4, smooth=True)
    # splash
    rnd = random.Random(int(z_top * 10))
    for k in range(6):
        pb.sphere("Foam", rnd.uniform(0.25, 0.45), loc=(x + rnd.uniform(-w / 2, w / 2), y_bot - rnd.uniform(0, 0.4), z_bot + 0.05),
                  scale=(1.4, 1.0, 0.45), segs=8, rings=4)


def rock_block(pb, size, loc, seed, mat="Slate", n=6, moss=True):
    """Terrace block: bevelled box core + boulders on its faces + mossy top. loc = base centre."""
    sx, sy, sz = size
    rnd = random.Random(seed)
    pb.box(mat, (sx, sy, sz), loc=(loc[0], loc[1], loc[2] + sz / 2), bevel=min(0.45, sz * 0.2), segs=1)
    for k in range(n):
        side = k % 3
        if side == 0:      # front face boulders
            p = (loc[0] + rnd.uniform(-sx / 2, sx / 2) * 0.8, loc[1] - sy / 2, loc[2] + rnd.uniform(0.15, 0.8) * sz)
        elif side == 1:    # left/right faces
            p = (loc[0] + rnd.choice((-1, 1)) * sx / 2, loc[1] + rnd.uniform(-sy / 2, sy / 2) * 0.8,
                 loc[2] + rnd.uniform(0.1, 0.8) * sz)
        else:              # top-edge boulders
            p = (loc[0] + rnd.uniform(-sx / 2, sx / 2) * 0.85, loc[1] + rnd.uniform(-sy / 2, sy / 2) * 0.85,
                 loc[2] + sz - 0.5)
        s_ = rnd.uniform(1.0, 1.8)
        pb.rock(rnd.choice((mat, mat, "Limestone")), (s_, s_ * 0.9, s_ * 0.8), loc=(p[0], p[1], p[2] - s_ * 0.3),
                rot=(0, 0, rnd.uniform(0, 90)), seed=seed * 10 + k, amp=0.12)
    if moss:
        pb.rock("Moss", (sx * 0.5, sy * 0.4, 0.35), loc=(loc[0] + rnd.uniform(-0.6, 0.6), loc[1] + sy * 0.15, loc[2] + sz - 0.1),
                seed=seed + 99, amp=0.1)


@prop("waterfall_cascade_3step", ["H7"], "P1", target=[8, 14, 10], group="hero",
      notes=("Three stacked rock terraces with falling-water sheets (Water part + Foam ribbons: swap for "
             "Beams/ParticleEmitters or keep) and small Water basins. Water exits toward local +Z into the H7 pool."),
      front="+Z = waterfall face / outflow",
      placements=[dict(hole="H7", pos=[-16, -3.6, -18], yaw=90,
                       note="outflow faces +X into the pool (x -14..-10); base 0.6 under the pool surface")])
def cascade(pb):
    tiers = [(1.6, 4.4, 12.2), (-1.4, 1.6, 8.2), (-4.0, -1.4, 4.2)]  # (y0, y1 (Blender), top height)
    for i, (y0, y1, top) in enumerate(tiers):
        yc = (y0 + y1) / 2
        rock_block(pb, (3.0, y1 - y0 + 0.4, top - 0.1), (0, yc, 0), seed=i + 1, n=3, moss=False)
        for sx in (-1, 1):
            rock_block(pb, (2.4, y1 - y0 + 0.6, top + 1.0), (sx * 2.6, yc + 0.2, 0), seed=10 + i * 2 + (sx > 0), n=5)
        pb.plane("Water", 2.6, (y1 - y0) - 0.1, loc=(0, yc, top + 0.02), nx=3, ny=3, ripple=0.02)
    fall_sheet(pb, 1.45, 12.22, 0.9, 8.22, 2.2)
    fall_sheet(pb, -1.55, 8.22, -2.1, 4.22, 2.4)
    fall_sheet(pb, -4.15, 4.22, -4.8, 0.6, 2.6)
    pb.rock("Slate", (3.0, 1.6, 1.2), loc=(-0.6, 4.2, 12.0), seed=41)
    pb.rock("Moss", (2.4, 1.4, 0.45), loc=(-0.6, 4.2, 12.9), seed=42)
    for k, (x, y, z, mat) in enumerate(((2.6, 3.6, 13.0, "MapleRed"), (-2.7, 3.3, 13.0, "Pumpkin"), (2.7, 0.5, 9.0, "Gold"))):
        pb.rock(mat, (1.5, 1.3, 1.1), loc=(x, y, z), seed=50 + k, amp=0.2)
    for k, x in enumerate((-3.4, -2.0, 2.1, 3.4)):
        pb.rock("Slate", (1.0, 1.0, 0.8), loc=(x, -4.5, 0), seed=60 + k)


@prop("waterfall_small", ["H6", "H5"], "P1", target=[6, 12, 4], group="hero",
      notes="Single tall fall down a mossy rock face with a mid ledge (H6 beside the green, P1); reuse at 0.67 "
            "scale as the upstream waterfall at H5 (P2).",
      front="+Z = waterfall face",
      placements=[dict(hole="H6", pos=[24, 0.25, -24], yaw=-90, note="faces -X toward the green"),
                  dict(hole="H5", pos=[10, -1.2, -21], yaw=-90, scale=0.67, note="waterfall_bg, upstream right")])
def waterfall_small(pb):
    for sx in (-1, 1):
        rock_block(pb, (2.3, 3.0, 11.6), (sx * 1.75, 0.4, 0), seed=3 + (sx > 0), n=7)
    rock_block(pb, (1.6, 2.6, 10.8), (0, 0.8, 0), seed=5, n=2, moss=False)
    rock_block(pb, (2.0, 1.4, 5.0), (-1.6, -1.2, 0), seed=6, n=3)
    pb.plane("Water", 1.4, 2.4, loc=(0, 0.6, 10.82), nx=2, ny=3)
    fall_sheet(pb, -0.45, 10.82, -1.6, 0.3, 1.4, x=0.0, segs=10)
    pb.rock("Pumpkin", (1.5, 1.2, 1.0), loc=(2.0, 1.2, 11.5), seed=21, amp=0.2)
    pb.rock("MapleRed", (1.3, 1.1, 1.0), loc=(-1.9, 1.3, 11.5), seed=22, amp=0.2)
    for k, x in enumerate((-2.2, -1.0, 1.4)):
        pb.rock("Slate", (0.9, 0.9, 0.7), loc=(x, -1.8, 0), seed=30 + k)


# ============================================================================ firefly rings
def horseshoe(pb, mat, R_, r, gap_deg, center, plane="YZ", segs=28, rsegs=8):
    """Torus arc with a gap at the bottom (so the ball rolls through). plane YZ: normal X; XZ: normal Y."""
    g = math.radians(gap_deg)
    pts = []
    n = segs
    for i in range(n + 1):
        a = -math.pi / 2 + g / 2 + (TAU - g) * i / n
        u, v = math.cos(a) * R_, math.sin(a) * R_
        if plane == "YZ":
            pts.append(Vector(center) + Vector((0, u, v)))
        else:
            pts.append(Vector(center) + Vector((u, 0, v)))
    pb.tube(mat, pts, r, rsegs)
    for p in (pts[0], pts[-1]):
        pb.sphere(mat, r * 1.15, loc=p, segs=8, rings=5)


def motes(pb, center, spread, n, seed, r=(0.035, 0.06)):
    rnd = random.Random(seed)
    for k in range(n):
        p = Vector(center) + Vector((rnd.uniform(-1, 1) * spread[0], rnd.uniform(-1, 1) * spread[1],
                                     rnd.uniform(-1, 1) * spread[2]))
        pb.sphere("Firefly", rnd.uniform(*r), loc=p, segs=6, rings=4)


FR_ORIGIN = (8.5, 0.0, -11.5)
import dressing_lib as _DL
RING_R = [h for h in _DL.load_holes() if h["number"] == 8][0]["teleports"][0]["entry"]["radius"]   # trigger radius


@prop("firefly_ring_entry", ["H8"], "P1", target=[3, 4, 4], group="hero",
      notes=("Root-knot arch with the glowing entry ring. Built in H8 hole-local coords: ring (horseshoe R 0.85, 120-deg "
             "gap at the bottom) stands at the trigger x=7.0, z=-11.5, facing -X (the approach); flat glow disc "
             f"{2 * RING_R:g} across = the {RING_R:g} trigger radius (Round 7). The arch's feet land on the "
             "alcove end rail line (x~9.3) and the knot mass sits behind it (x>9.4), so nothing visual stands on the "
             "felt. Hood root overhangs the ring at y>=2."),
      front="ring faces local -X",
      placements=[dict(hole="H8", pos=list(FR_ORIGIN), yaw=0)])
def ring_entry(pb):
    pb.set_origin_at(R(*FR_ORIGIN))
    # arch in the plane x=9.3, feet at z=-13.4 / -9.6
    for k, (dx, ph, rr) in enumerate(((0.0, 0.0, 0.32), (0.18, 1.3, 0.22), (-0.15, 2.4, 0.18))):
        pts = []
        for i in range(17):
            a = math.pi * i / 16
            z = -11.5 - 1.9 * math.cos(a) + 0.08 * math.sin(i * 1.4 + ph)
            y = 3.5 * math.sin(a) + 0.1 * math.sin(i + ph)
            pts.append(R(9.3 + dx + 0.12 * math.sin(i * 0.9 + ph), y, z))
        radii = [rr * (1.5 if i in (0, 16) else 1.25 if i in (1, 15) else 1.0) for i in range(17)]
        pb.tube("RootBark", pts, radii, 7, wobble=0.2, seed=k)
    # hood: root from the arch top overhanging the ring
    pb.tube("RootBark", [R(9.3, 3.45, -11.5), R(8.6, 3.2, -11.3), R(7.6, 2.75, -11.6), R(6.9, 2.3, -11.5)],
            [0.3, 0.24, 0.17, 0.08], 7, wobble=0.15, seed=7)
    pb.tube("RootBark", [R(8.4, 3.1, -11.4), R(8.0, 2.5, -12.4), R(7.8, 2.1, -12.6)], [0.12, 0.08, 0.03], 5)
    # knot mass behind the end rail
    for k, (z, y, s) in enumerate(((-12.6, 0.0, 1.5), (-10.5, 0.0, 1.4), (-11.5, 0.6, 1.3))):
        pb.rock("RootBark", (1.3, s, s * 0.9), loc=R(10.1, y, z), seed=70 + k, amp=0.2, smooth=True)
    pb.rock("Moss", (1.5, 2.4, 0.4), loc=R(10.1, 1.25, -11.5), seed=75, amp=0.12)
    # ring + glow pad + fireflies
    # pass 6 (Round 5): trigger radius 0.35 -> 0.55. Glow disc 1.1 across = the trigger; the ring is opened up
    # (R 0.85, 120 deg bottom gap = 1.47 wide at its ends) so a ball anywhere in the trigger passes through it
    horseshoe(pb, "Firefly", 0.85, 0.07, 120, R(7.0, 0.95, -11.5), "YZ")
    pb.cyl("Firefly", RING_R, RING_R, 0.02, 20, loc=R(7.0, 0.01, -11.5), smooth=False)   # Round 7: r 0.45
    motes(pb, R(7.6, 1.95, -11.5), (0.9, 1.5, 0.9), 14, 3)      # pass 6: all motes >= 1 above the felt
    for k, z in enumerate((-13.3, -9.7)):
        pb.cyl("Cream", 0.05, 0.06, 0.3, 6, loc=R(9.75, 0.15, z))
        pb.sphere("ShroomGlow", 0.16, loc=R(9.75, 0.32, z), scale=(1, 1, 0.55), segs=8, rings=4)


@prop("firefly_ring_exit", ["H8"], "P1", target=[2.5, 3, 1], group="hero",
      notes=("Hovering firefly ring on the H8 upper green. The ball pops out at its bottom-centre moving along "
             "local +Z; the ring has a gap at the bottom and no feet, so nothing visual stands on the felt except a "
             "flat glow pad (0.02 tall)."),
      front="+Z = exit direction",
      placements=[dict(hole="H8", pos=[9.0, 1.5, -47.0], yaw=-26.57,
                       note="pass 6: north-east corner of the green; yaw -26.57 turns local +Z to the exit dir "
                            "(-0.4472, 0.8944), toward the cup")])
def ring_exit(pb):
    horseshoe(pb, "Firefly", 1.12, 0.1, 44, (0, 0, 1.36), "XZ", segs=32)
    pb.cyl("Firefly", 0.42, 0.42, 0.02, 16, loc=(0, 0, 0.01), smooth=False)
    motes(pb, (0, 0, 1.5), (1.2, 0.45, 1.4), 18, 5)
    # a few floating leaves caught in the glow
    rnd = random.Random(8)
    for k in range(5):
        a = TAU * k / 5
        pb.sphere(rnd.choice(["MapleRed", "Gold", "Pumpkin"]), 0.12,
                  loc=(math.cos(a) * 1.3, rnd.uniform(-0.3, 0.3), 1.36 + math.sin(a) * 1.3), scale=(1.6, 0.25, 1.0),
                  rot=(rnd.uniform(0, 60), 0, rnd.uniform(0, 180)), segs=6, rings=3, smooth=False)


# ============================================================================ H2 acorn + stump
@prop("giant_acorn", ["H2"], "P1", target=[3, 4, 3], group="hero",
      notes="Glossy acorn with a scaly cap; sits on the stump top (y=1.2).",
      placements=[dict(hole="H2", pos=[0, 1.2, -19.5], yaw=0, note="on stump_cladding")])
def acorn(pb):
    prof = [(0.0, 0.0), (0.45, 0.04), (0.9, 0.3), (1.2, 0.75), (1.38, 1.3), (1.4, 1.9), (1.32, 2.4), (0.0, 2.45)]
    pb.lathe("Oak", prof, 20)
    pb.sphere("Cream", 0.28, loc=(-0.55, -1.12, 1.6), scale=(0.6, 0.2, 1.2), segs=8, rings=5)  # highlight
    cap = [(1.3, 2.25), (1.52, 2.4), (1.56, 2.75), (1.4, 3.15), (1.0, 3.45), (0.4, 3.6), (0.0, 3.62)]
    pb.lathe("RootBark", cap, 20)
    for row, (z, r) in enumerate(((2.5, 1.55), (2.85, 1.5), (3.2, 1.25), (3.45, 0.85))):
        n = int(20 - row * 3)
        for k in range(n):
            a = TAU * (k + 0.5 * (row % 2)) / n
            q = Vector((0, 0, 1)).rotation_difference(Vector((math.cos(a), math.sin(a), 0.6)).normalized())
            pb.sphere("Shingle", 0.17, matrix=Matrix.Translation((math.cos(a) * r, math.sin(a) * r, z)) @
                      q.to_matrix().to_4x4() @ Matrix.Diagonal((1, 1, 0.4, 1)), segs=6, rings=3, smooth=False)
    pb.tube("RootBark", [(0, 0, 3.55), (0.05, 0, 3.8), (0.2, 0, 4.0)], [0.14, 0.12, 0.1], 6)


@prop("stump_cladding", ["H2"], "P1", target=[3, 3.2, 1], group="hero",
      notes="Bark cladding for the 'stump' bumper block (3 x 3.2 x 1, y -2..1.2): straddles the ledge, bottom on "
            "the lower felt level. Kept within ~0.15 of the block so the ball never passes through visuals.",
      placements=[dict(hole="H2", pos=[0, -2.0, -19.5], yaw=0)])
def stump(pb):
    S = Matrix.Diagonal((1.0, 0.36, 1.0, 1))
    prof = [(1.62, 0), (1.56, 0.4), (1.52, 1.5), (1.5, 2.8), (1.48, 3.2)]
    pb.lathe("RootBark", prof, 24, matrix=S, wobble=0.04, seed=4)
    pb.cyl("Oak", 1.45, 1.45, 0.06, 24, loc=(0, 0, 3.2), matrix=S, smooth=False)
    for r in (0.5, 0.95, 1.3):
        pb.torus("RootBark", r, 0.025, 20, 3, loc=(0, 0, 3.23), matrix=S)
    pb.rock("Moss", (1.0, 0.5, 0.25), loc=(-0.9, 0.0, 3.1), seed=2, amp=0.1)
    for sx in (-1, 1):
        pb.sphere("Moss", 0.4, loc=(sx * 1.45, 0, 2.0), scale=(0.4, 0.9, 1.0), segs=8, rings=4)


# ============================================================================ hollow tree
TREE_ORIGIN = (23.0, -1.0, -36.0)
CAV = (11.5, 20.5, 6.0)   # cavity superellipse rx (x), ry (z), n
OUT = (15.6, 23.2, 2.5)   # outer superellipse


@prop("hollow_tree", ["H9", "H8"], "P1", target=[34, 60, 34], group="hero",
      notes=("Giant hollow golden tree. The cavity (superellipse 23 x 41) contains H9's chamber + heart rails "
             "(x 13.5..32.5, z -54.5..-17.5), so the trunk is 34 wide x 48 deep instead of 34 x 34 (holes.json "
             "geometry needs the extra depth). Openings: west tunnel (8 wide, 4.5 high above the corridor felt, "
             "z -29.5..-21.5) where the root gate sits at its mouth; big south arch (10 wide) looking in from the "
             "approach; open top ringed by the canopy (light into the heart). Origin placed at x=23 (anchor said 22) "
             "and y=-1 (below the heart felt -0.8)."),
      front="local -X = tunnel side",
      placements=[dict(hole="H9", pos=list(TREE_ORIGIN), yaw=0)])
def hollow_tree(pb):
    segs = 56
    levels = [(0.0, 1.08, 1.0), (1.5, 1.03, 1.0), (4.0, 1.0, 1.0), (8.0, 0.97, 1.0), (14.0, 0.92, 0.9),
              (21.0, 0.86, 0.8), (28.0, 0.8, 0.7), (34.0, 0.76, 0.64), (38.0, 0.75, 0.62)]

    def wob(a, z):
        return 1 + 0.03 * math.sin(a * 23 + z * 0.13) + 0.02 * noise.noise(Vector((math.cos(a) * 3, math.sin(a) * 3, z * 0.1)))
    outer, inner = [], []
    for z, so, si in levels:
        zz = z
        o = superellipse_ring(OUT[0] * so, OUT[1] * so, OUT[2], segs, zz, wob=wob)
        i_ = superellipse_ring(CAV[0] * si, CAV[1] * si, CAV[2], segs, zz, wob=lambda a, z_: 1 + 0.01 * math.sin(a * 17))
        if z >= 38.0:
            for k in range(segs):
                dz = 2.0 * noise.noise(Vector((k * 0.35, 1.0, 0)))
                o[k].z += dz
                i_[k].z += dz - 0.6
        outer.append(o)
        inner.append(i_)
    shell(pb, "RootBark#trunk", outer, inner)
    # buttress roots (N, E, S sides only; west side is the H9 lane/landing)
    rnd = random.Random(12)
    for k, deg in enumerate((-80, -50, -20, 10, 35, 60, 85, 110, 130, -105)):
        a = math.radians(deg)
        d = Vector((math.cos(a), math.sin(a), 0))
        c, s = math.cos(a), math.sin(a)
        rx = OUT[0] * math.copysign(abs(c) ** (2 / OUT[2]), c)
        ry = OUT[1] * math.copysign(abs(s) ** (2 / OUT[2]), s)
        base = Vector((rx, ry, 0)) * 1.0
        L = rnd.uniform(2.6, 3.6)
        pts = [base * 0.93 + Vector((0, 0, 7.5)), base * 0.98 + Vector((0, 0, 4.5)), base + d * L * 0.4 + Vector((0, 0, 1.6)),
               base + d * L * 0.8 + Vector((0, 0, 0.3)), base + d * L + Vector((0, 0, -0.3))]
        pb.tube("RootBark", pts, [2.0, 1.6, 1.1, 0.6, 0.25], 8, wobble=0.15, seed=k)
    # branches + canopy (canopy is allowed to spread wider than the trunk)
    blobs = []
    for k in range(8):
        a = TAU * k / 8 + 0.2
        c, s_ = math.cos(a), math.sin(a)
        p0 = Vector((c * 10.5, s_ * 15.0, 33.0))
        p1 = Vector((c * 15.0, s_ * 20.0, 41.0))
        p2 = Vector((c * 18.5, s_ * 24.0, 46.0))
        pb.tube("RootBark", [p0, p0 + Vector((c, s_, 0)) * 2.0 + Vector((0, 0, 4)), p1, p2], [1.8, 1.4, 1.0, 0.5], 7,
                wobble=0.12, seed=30 + k)
        blobs.append((p2 + Vector((0, 0, 2.5)), 6.0))
        blobs.append(((p1 + p0) / 2 + Vector((0, 0, 9.0)), 6.5))
    for k in range(6):
        a = TAU * k / 6 + 0.5
        blobs.append((Vector((math.cos(a) * 8.0, math.sin(a) * 11.0, 53.5)), 5.5))
    mats = ["Gold", "Gold", "Pumpkin", "Gold", "MapleRed", "Pumpkin"]
    for k, (p, r) in enumerate(blobs):
        p.z = min(p.z, 60 - r * 0.85 * 0.65)
        pb.rock(mats[k % len(mats)], (r * 2, r * 2, r * 1.6), loc=p - Vector((0, 0, r * 0.8 * 0.35)), seed=80 + k,
                amp=0.14, ico=2, flat_bottom=False)
    # bracket fungi + glowing windows on the outside, fungi inside
    for k, (deg, z) in enumerate(((60, 9), (75, 12), (-40, 15), (20, 22), (100, 6))):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        p = Vector((OUT[0] * math.copysign(abs(c) ** 0.8, c) * 0.95, OUT[1] * math.copysign(abs(s) ** 0.8, s) * 0.95, z))
        pb.cyl("CapOrange", 1.2, 0.9, 0.3, 10, loc=p, smooth=False)
    for k, (deg, z) in enumerate(((10, 16), (40, 24), (-25, 11))):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        so = 0.96
        p = Vector((OUT[0] * so * math.copysign(abs(c) ** 0.8, c), OUT[1] * so * math.copysign(abs(s) ** 0.8, s), z))
        window(pb, p, (c, s, 0), r=0.8)
    for k, (deg, z) in enumerate(((0, 7), (30, 9), (160, 8), (200, 10), (-60, 6.5), (90, 11), (120, 7.5))):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        p = Vector((CAV[0] * 0.985 * math.copysign(abs(c) ** (2 / 6), c), CAV[1] * 0.985 * math.copysign(abs(s) ** (2 / 6), s), z))
        pb.cyl("CapOrange" if k % 2 else "CapGold", 0.9, 0.7, 0.22, 10, loc=p, smooth=False)

    def post(root, objs):
        bark = [o for o in objs if o.name.endswith("__RootBark_trunk")][0]
        # tunnel (prop-local: world corridor z -29.5..-21.5 -> Blender y -6.5..-14.5; felt at y=1 -> z=2)
        def cut(c):
            m1 = Matrix.Translation((-14.0, 10.5 * -1, 2.0)) @ FRAME_X
            c.prism("Cut", arch_poly(8.0, 2.6, 4.6, -0.5, 14), 10.0, matrix=m1)
        apply_boolean(bark, cut)

        def cut2(c):
            m2 = Matrix.Translation((0, -21.5, 3.5)) @ FRAME_Y
            c.prism("Cut", arch_poly(10.0, 6.0, 11.0, 0.0, 16), 8.0, matrix=m2)
        apply_boolean(bark, cut2)
    return post


# ============================================================================ H8 root arch + heart lanterns
@prop("root_arch_large", ["H8"], "P1", target=[16, 10, 3], group="hero",
      notes=("Big intertwined root arch (hollow-tree roots arching over the course, h08 'hollow_tree_base'). Span "
             "16 (feet at local x=+-8), clear height ~9. Feet must stand outside rails."),
      front="spans local X",
      placements=[
          dict(hole="H8", pos=[0, 0, -3.5], yaw=0, note="over the tee lane (rails x=+-3.75)"),
          dict(hole="H8", pos=[-16.5, 0.75, -22.0], yaw=0, note="over the climb ramp c2 (rails x -20.25/-12.75; "
               "pass 6: c2 moved 9 toward the tee)"),
          dict(hole="H8", pos=[-6.0, 0, -11.5], yaw=90, note="over the junction (rails z -15.25/-7.75)"),
      ])
def root_arch(pb):
    for k, (dy, ph, rr) in enumerate(((0.0, 0.0, 0.6), (0.45, 1.7, 0.42), (-0.4, 3.1, 0.38))):
        pts = []
        for i in range(25):
            a = math.pi * i / 24
            x = -7.6 * math.cos(a) * (1 - 0.04 * math.sin(a * 3 + ph))
            z = 9.2 * math.sin(a) ** 0.85 + 0.25 * math.sin(i * 0.9 + ph)
            pts.append((x, dy + 0.3 * math.sin(i * 0.6 + ph), z))
        radii = [rr * (1.8 if i in (0, 24) else 1.35 if i in (1, 23) else 1.0) for i in range(25)]
        pb.tube("RootBark", pts, radii, 8, wobble=0.18, seed=k)
    rnd = random.Random(3)
    for k in range(6):
        x = rnd.uniform(-4.5, 4.5)
        top = 9.2 * math.sin(math.acos(max(min(-x / 8, 1), -1))) ** 0.85
        pb.tube("RootBark", [(x, 0, top - 0.3), (x + 0.2, 0.1, top - 1.2), (x + 0.1, 0, top - 1.9)], [0.12, 0.08, 0.02], 5)
    for k, x in enumerate((-3.0, 2.5)):
        top = 9.2 * math.sin(math.acos(-x / 8)) ** 0.85
        pb.tube("Iron", [(x, 0, top - 0.5), (x, 0, top - 1.1)], 0.02, 4)
        pb.lantern(0.8, loc=(x, 0, top - 1.95))
    for x in (-6.5, -2.0, 4.0, 6.8):
        top = 9.2 * math.sin(math.acos(-x / 8)) ** 0.85
        pb.sphere("Moss", 0.7, loc=(x, 0.0, top + 0.45), scale=(1.4, 0.8, 0.35), segs=8, rings=4)
    for sx in (-1, 1):
        for k in range(3):
            pb.cyl("Cream", 0.06, 0.08, 0.35, 6, loc=(sx * (7.9 + 0.25 * k), 0.9 - 0.5 * k, 0.17))
            pb.sphere("ShroomGlow", 0.2, loc=(sx * (7.9 + 0.25 * k), 0.9 - 0.5 * k, 0.37), scale=(1, 1, 0.55), segs=8, rings=4)


@prop("heart_lantern_cluster", ["H9"], "P1", target=[16, 6, 12], group="hero",
      notes="NOT PLACED since pass 8 (holes.json Round 7: the 3 hanging amber lanterns, lantern_large_hanging, "
            "replace it). Dozens of paper lanterns on cords hanging from two crossbeams. Lowest lantern bottom = "
            "origin.",
      placements=[])         # pass 8 / Round 7: replaced by 3 hanging amber lanterns (props.md); kept, not placed
def heart_lanterns(pb):
    rnd = random.Random(21)
    top = 6.0
    for sy in (-3.5, 3.5):
        pb.box("RootBark", (16.0, 0.35, 0.35), loc=(0, sy, top - 0.17), bevel=0.06)
    count = 0
    for i in range(7):
        for j in range(5):
            x = -7.0 + i * (14.0 / 6) + rnd.uniform(-0.5, 0.5)
            y = -4.6 + j * 2.3 + rnd.uniform(-0.4, 0.4)
            if rnd.random() < 0.15:
                continue
            h = rnd.choice((0.8, 0.8, 1.2, 1.2, 2.0))
            drop = rnd.uniform(0.4, top - h - 0.2)
            hang = top - 0.3 - drop
            pb.tube("Iron", [(x, y, top - 0.2), (x, y, hang)], 0.015, 3, smooth=False)
            pb.lantern(h, loc=(x, y, hang - h), lod=1)
            count += 1
    # string links between neighbouring cords near the top
    for sy in (-3.5, 3.5):
        pts = [(x, sy, top - 0.5 - 0.3 * math.sin(math.pi * (x + 8) / 16)) for x in [-8 + k * 0.8 for k in range(21)]]
        pb.tube("RootBark", pts, 0.03, 4)
