"""P1 set dressing: lanterns, lantern post, tee signs, rail kit, deflector board, bank backing, drop faces, water."""
import math
from mathutils import Vector, Matrix
from registry import prop
from lglib import M, R, text_bm, TAU
import lglib

FONT = "/usr/share/fonts/truetype/sand-box/google/Lilita One/LilitaOne-Regular.ttf"


def strip_outline(pts, w):
    """Polygon outline of a strip of width w along polyline pts (2D tuples), mitred joints."""
    P = [Vector(p) for p in pts]
    left, right = [], []
    for i, p in enumerate(P):
        if i == 0:
            d = (P[1] - P[0]).normalized()
            n = Vector((-d.y, d.x))
            off = n * (w / 2)
        elif i == len(P) - 1:
            d = (P[-1] - P[-2]).normalized()
            n = Vector((-d.y, d.x))
            off = n * (w / 2)
        else:
            d1 = (P[i] - P[i - 1]).normalized()
            d2 = (P[i + 1] - P[i]).normalized()
            n1 = Vector((-d1.y, d1.x))
            n2 = Vector((-d2.y, d2.x))
            m = (n1 + n2).normalized()
            off = m * (w / 2) / max(m.dot(n1), 0.3)
        left.append(tuple(p + off))
        right.append(tuple(p - off))
    return right + list(reversed(left))


# ----------------------------------------------------------------------------- lanterns
for _nm, _h, _pl in (("lantern_small", 0.8, []), ("lantern_medium", 1.2, []), ("lantern_large", 2.0, [])):
    def _mk(h):
        def fn(pb):
            tass = h * 0.12
            pb.lantern(h - tass * 0.5, loc=(0, 0, tass * 0.5 + 0.0))
        return fn
    prop(_nm, ["all"], "P1", target=[_h * 0.72, _h, _h * 0.72], group="lanterns",
         notes=(f"Paper lantern {_h} studs tall. Hang point (top of iron ring) is at y={_h:.2f} above the origin. "
                "Neon 'Glow' core inside: add PointLight (Range 8, Brightness 0.6 day / 1.6 night, Color #FFB347). "
                "Paper part can use Transparency 0.1-0.2 at night."))(_mk(_h))


@prop("lantern_post", ["H2", "H4", "H7"], "P1", target=[0.5, 3.5, 0.5], group="lanterns",
      notes="Timber post 3.5 tall, arm + small lantern hanging toward local +X (bbox x includes the arm). "
            "Rotate so the lantern hangs over/toward the felt.",
      placements=[
          dict(hole="H2", pos=[-4.65, 0, -19.6], yaw=0, note="left chute edge, lantern toward chute"),
          dict(hole="H2", pos=[4.65, 0, -19.6], yaw=180, note="right chute edge"),
          dict(hole="H4", pos=[-7, 0.6, -41], yaw=0, note="flanking raised green (anchor green_lanterns)"),
          dict(hole="H4", pos=[7, 0.6, -41], yaw=180, note="mirror"),
          dict(hole="H7", pos=[3.75, -1.2, -27.25], yaw=0, note="lower gap west edge (on rail7 end; pass 6 gap x 4..6.5)"),
          dict(hole="H7", pos=[6.75, -1.2, -27.25], yaw=180, note="lower gap east edge (on rail8 end)"),
      ])
def lantern_post(pb):
    pb.box("Slate", (0.52, 0.52, 0.28), loc=(0, 0, 0.14), bevel=0.06)
    pb.box("Oak", (0.34, 0.34, 3.3), loc=(0, 0, 0.28 + 1.65), bevel=0.04)
    # little roof on top
    pb.cyl("Shingle", 0.36, 0.02, 0.28, 4, loc=(0, 0, 3.36), rot=(0, 0, 45), smooth=False)
    # arm + brace
    pb.box("Oak", (0.95, 0.16, 0.16), loc=(0.45, 0, 3.08), bevel=0.03)
    pb.tube("Oak", [(0.0, 0, 2.6), (0.3, 0, 2.85), (0.55, 0, 3.02)], 0.055, 6, smooth=False)
    pb.torus("Iron", 0.06, 0.018, 8, 4, loc=(0.78, 0, 2.96), rot=(90, 0, 0))
    pb.lantern(0.78, loc=(0.78, 0, 2.0))


# ----------------------------------------------------------------------------- tee signs
def _tee_sign(num):
    def fn(pb):
        pb.box("Slate", (0.4, 0.34, 0.22), loc=(0, 0, 0.11), bevel=0.05)
        pb.box("Oak", (0.22, 0.22, 2.25), loc=(0, 0.04, 0.22 + 1.12), bevel=0.03)
        # plaque
        pb.box("RootBark", (1.0, 0.1, 0.74), loc=(0, -0.09, 1.72), bevel=0.04)
        pb.box("Oak", (0.86, 0.06, 0.6), loc=(0, -0.13, 1.72), bevel=0.02)
        t = text_bm(str(num), size=0.52, extrude=0.02, font_path=FONT)
        pb.add("Cream", t, M((0, -0.17, 1.53)))
        # lantern on top, sitting in a bracket
        pb.box("Iron", (0.3, 0.3, 0.04), loc=(0, 0.04, 2.49))
        pb.lantern(0.5, loc=(0, 0.04, 2.51), hook=False)
        pb.sphere("Iron", 0.04, loc=(0, 0.04, 2.98), segs=6, rings=4)
    return fn


for _n in range(1, 10):
    prop(f"tee_sign_h{_n:02d}", [f"H{_n}"], "P1", target=[1, 3, 0.3], group="tee_sign",
         notes=f"Hole-number sign '{_n}', lantern on top (Neon core). Number faces +Z.",
         placements=[dict(hole=f"H{_n}", pos=[5.2 if _n == 1 else -5.2, 0, 0.6], yaw=0,
                          note="beside the tee, outside the rail, facing +Z (back toward the walk-up)")])(_tee_sign(_n))


# ----------------------------------------------------------------------------- rail kit
RAIL_NOTE = ("Visual rail = limestone block + oak cap, 1.0 tall, 0.5 thick, run along local Z. For each holes.json "
             "rail wall: pos = (wall.center.x, top of the highest felt it borders, wall.center.z), yaw = wall.yaw, "
             "then set Size.Z = wall length (straight pieces stretch cleanly; flat colours). Stays 1 stud tall even "
             "where the invisible collision wall is taller.")


def _rail_straight(L, block="Limestone", cap="Oak"):
    def fn(pb):
        n = max(1, int(round(L / 2)))
        seg = L / n
        for i in range(n):
            y = -L / 2 + seg * (i + 0.5)
            pb.box(block, (0.48, seg - 0.04, 0.72), loc=(0, y, 0.36), bevel=0.06)
        pb.box(cap, (0.56, L, 0.28), loc=(0, 0, 0.86), bevel=0.05)
    return fn


prop("rail_straight_4", ["all"], "P1", target=[0.5, 1, 4], group="rail_kit", notes=RAIL_NOTE)(_rail_straight(4.0))
prop("rail_straight_2", ["all"], "P1", target=[0.5, 1, 2], group="rail_kit", notes=RAIL_NOTE)(_rail_straight(2.0))


def _rail_bend(angle):
    def fn(pb):
        a = math.radians(angle)
        pts = [(0, -1.0), (0, 0), (math.sin(a) * 1.0, math.cos(a) * 1.0)]
        pb.prism("Limestone", strip_outline(pts, 0.48), 0.72, loc=(0, 0, 0.36))
        pb.prism("Oak", strip_outline(pts, 0.56), 0.28, loc=(0, 0, 0.86))
    return fn


prop("rail_corner_45", ["all"], "P1", target=[1.2, 1, 2], group="rail_kit",
     origin="bend point (corner vertex), bottom",
     notes="Rail bend: one 1-stud arm along -Z... +Z, second arm turned 45 deg toward +X. Origin at the bend. "
           + RAIL_NOTE)(_rail_bend(45))
prop("rail_corner_90", ["all"], "P1", target=[1.25, 1, 1.25], group="rail_kit",
     origin="bend point (corner vertex), bottom",
     notes="Rail L-corner, 1-stud arms. Origin at the bend. " + RAIL_NOTE)(_rail_bend(90))


@prop("rail_end_post", ["all"], "P1", target=[0.7, 1.15, 0.7], group="rail_kit",
      notes="Chunky end/joint post. Drop one on every rail end and on any odd-angle joint to hide seams.")
def rail_end_post(pb):
    pb.box("Limestone", (0.64, 0.64, 0.8), loc=(0, 0, 0.4), bevel=0.07)
    pb.box("Oak", (0.72, 0.72, 0.22), loc=(0, 0, 0.9), bevel=0.05)
    pb.cyl("Oak", 0.2, 0.12, 0.16, 8, loc=(0, 0, 1.08), smooth=False)


# pass 5 rail variants (same 0.5 x 1.0 profile and origin as the base kit, so they drop onto the same walls):
#   _trim: H8 + H9 (dark holes under the root arch / inside the tree): light TrimStone blocks + cream TrimCream cap, so
#          the lane edge reads against the bark floor and the felt;  _mill: H6 (mill race): dark MillSlate blocks +
#          painted MillBlue cap, a clearly different rail for the mill hole.
RAIL_VARIANTS = {"trim": ("TrimStone", "TrimCream", ["H8", "H9"]), "mill": ("MillSlate", "MillBlue", ["H6"])}
for _v, (_blk, _cap, _holes) in RAIL_VARIANTS.items():
    for _L in (4, 2):
        prop(f"rail_straight_{_L}_{_v}", _holes, "P1", target=[0.5, 1, _L], group="rail_kit",
             notes=f"Pass-5 rail variant for {'/'.join(_holes)}: {_blk} blocks + {_cap} cap. " + RAIL_NOTE)(
            _rail_straight(float(_L), _blk, _cap))

    def _post(blk, cap):
        def fn(pb):
            pb.box(blk, (0.64, 0.64, 0.8), loc=(0, 0, 0.4), bevel=0.07)
            pb.box(cap, (0.72, 0.72, 0.22), loc=(0, 0, 0.9), bevel=0.05)
            pb.cyl(cap, 0.2, 0.12, 0.16, 8, loc=(0, 0, 1.08), smooth=False)
        return fn
    prop(f"rail_end_post_{_v}", _holes, "P1", target=[0.7, 1.15, 0.7], group="rail_kit",
         notes=f"Pass-5 end post matching rail_straight_*_{_v}.")(_post(_blk, _cap))


@prop("cup_lantern_stake", ["H8", "H9"], "P1", target=[0.6, 1.95, 0.6], group="lanterns",
      notes="Pass 5: short glowing lantern on a stake (1.95 tall, under the 2-stud 'tall prop' line so it may stand "
            "right outside the rail) marking the cups of H8/H9 and the H9 root gate. Placed as dressing "
            "(manifest.dressing.holes.H8/H9, role 'accent'). Neon core: PointLight Range 10, Brightness 2, #FFC873.")
def cup_lantern_stake(pb):
    pb.box("Slate", (0.5, 0.5, 0.2), loc=(0, 0, 0.1), bevel=0.05)
    pb.box("Oak", (0.18, 0.18, 0.9), loc=(0, 0, 0.2 + 0.45), bevel=0.03)
    pb.box("Iron", (0.42, 0.42, 0.05), loc=(0, 0, 1.1))
    pb.lantern(0.8, loc=(0, 0, 1.12), hook=False, paper="PaperOrange")


@prop("timber_deflector_board", ["H1", "H6", "H9"], "P1", target=[0.5, 1, 10], group="rail_kit",
      notes="Plank cladding for deflector walls (H1 deflector, H6 board1/board2, H9 root_deflector). "
            "Stretch Size.Z to the wall length. Base at felt top.",
      placements=[
          dict(hole="H1", pos=[0.0, 0.5, -32.5], yaw=-135, scale_z_to=11.31, note="wall 'deflector'"),
          dict(hole="H6", pos=[-0.5, 0.0, -8.5], yaw=135, scale_z_to=10.9, note="wall 'board1'"),
          dict(hole="H6", pos=[15.0, 0.0, -8.0], yaw=135, scale_z_to=10.9, note="wall 'board2'"),
          dict(hole="H9", pos=[23.0, 1.0, -27.0], yaw=135, scale_z_to=20.8, note="wall 'root_deflector'"),
      ])
def timber_board(pb):
    L = 10.0
    for i, z in enumerate((0.17, 0.5, 0.83)):
        pb.box("Oak", (0.42, L - 0.1 * (i % 2), 0.3), loc=(0.0, 0, z), bevel=0.05)
    for y in (-L / 2 + 0.35, -1.6, 1.6, L / 2 - 0.35):
        pb.box("RootBark", (0.5, 0.26, 1.0), loc=(0, y, 0.5), bevel=0.04)
        pb.box("Iron", (0.52, 0.1, 0.12), loc=(0, y, 0.78))
    pb.box("RootBark", (0.5, L, 0.08), loc=(0, 0, 1.0 - 0.04), bevel=0.02)


@prop("bank_backing_stone", ["H3", "H8", "H9"], "P1", target=[0.5, 2.2, 12.2], group="rail_kit",
      notes="Tall stone backing behind each banked-plane corner (collision: *_backing walls). Visual top = 1 stud "
            "above the bank's high edge (2.2 above base felt).",
      placements=[
          dict(hole="H3", pos=[-1.2753, 0.0, -13.2753], yaw=135, note="bank1_backing"),
          dict(hole="H3", pos=[18.7753, 0.0, -10.7247], yaw=135, note="bank2_backing"),
          dict(hole="H8", pos=[-17.7753, 0.0, -10.2247], yaw=-135, note="bank1_backing"),
          dict(hole="H8", pos=[-17.7753, 1.5, -49.7753], yaw=135, note="bank2_backing"),
          dict(hole="H9", pos=[-1.2753, 1.0, -26.7753], yaw=135, note="bank1_backing"),
      ])
def bank_backing(pb):
    L = 12.19
    import random
    rnd = random.Random(3)
    for row, (z0, z1) in enumerate(((0.0, 0.98), (0.98, 1.95))):
        y = -L / 2
        first = True
        while y < L / 2 - 0.01:
            seg = (0.8 if first and row == 1 else rnd.uniform(1.1, 1.7))
            first = False
            seg = min(seg, L / 2 - y)
            pb.box("Limestone", (0.48, seg - 0.05, z1 - z0 - 0.04), loc=(0, y + seg / 2, (z0 + z1) / 2), bevel=0.07)
            y += seg
    pb.box("Oak", (0.58, L, 0.27), loc=(0, 0, 2.07), bevel=0.05)
    for y in (-4.0, 0.5, 3.6):
        pb.rock("Moss", (0.5, 0.9, 0.22), loc=(0.05, y, 1.95), seed=int(y * 10) + 50, amp=0.1)


@prop("drop_face_stone", ["H2", "H5", "H6", "H7", "H9"], "P1", target=[4, 1, 0.4], group="stream",
      notes="Stone cladding for vertical felt edges (drops, stream banks). Front face at local z=+0.2 faces +Z "
            "(the LOW side); body hides under the upper felt. Scale X to the edge length, Y to the drop height. "
            "pos = edge point moved 0.2 back under the upper felt, y = lower level.",
      placements=[
          dict(hole="H2", pos=[0, -1.5, -19.8], yaw=0, scale=[2.0, 1.5, 1], note="ledge z=-20, full width 8"),
          dict(hole="H7", pos=[0, -1.2, -13.8], yaw=0, scale=[2.0, 1.2, 1], note="drop d1 z=-14"),
          dict(hole="H7", pos=[0, -2.4, -26.8], yaw=0, scale=[5.0, 1.2, 1], note="t2 north edge z=-27"),
          dict(hole="H9", pos=[22, -0.5, -39.8], yaw=0, scale=[4.0, 1.5, 1], note="heart-well drop z=-40"),
          dict(hole="H5", pos=[-4.5, -1.2, -15.2], yaw=180, scale=[5.25, 1.2, 1], note="shore edge over stream"),
          dict(hole="H5", pos=[-4.5, -1.2, -27.8], yaw=0, scale=[5.25, 1.2, 1], note="north felt edge over stream"),
          dict(hole="H6", pos=[7.0, -1.0, -5.2], yaw=0, scale=[1.25, 1.0, 1], note="channel edge over millrace"),
      ])
def drop_face(pb):
    import random
    rnd = random.Random(7)
    pb.box("Limestone", (4.0, 0.3, 0.98), loc=(0, 0.05, 0.49))
    for row in range(2):
        x = -2.0 + (0.35 if row else 0)
        if row:
            pb.box("Slate", (0.33, 0.12, 0.44), loc=(-2.0 + 0.165, -0.14, 0.27 + 0.47), bevel=0.05)
        while x < 2.0 - 0.05:
            w = min(rnd.uniform(0.6, 0.95), 2.0 - x)
            mat = "Slate" if rnd.random() < 0.45 else "Limestone"
            pb.box(mat, (w - 0.05, 0.14, 0.44), loc=(x + w / 2, -0.13, 0.25 + row * 0.47), bevel=0.06)
            x += w
    pb.box("Moss", (4.0, 0.06, 0.07), loc=(0, -0.17, 0.92), bevel=0.02)


@prop("water_surface", ["H5", "H6", "H7"], "P1", target=[4, 0.05, 4], group="stream",
      origin="surface centre (y=0 is the water surface)",
      notes="4x4 water module with gentle facets + foam flecks; stretch X/Z to the hazard footprint and put "
            "origin at the hazard centre (y = hazard center.y). Glass, Transparency 0.4, add a scrolling texture.",
      placements=[
          dict(hole="H5", pos=[-4.5, -1.0, -21.5], yaw=0, scale=[6.25, 1, 3.25], note="hazard 'stream' 25x13"),
          dict(hole="H6", pos=[7.0, -0.8, -3.0], yaw=0, scale=[1.25, 1, 1.0], note="hazard 'millrace' 5x4"),
          dict(hole="H7", pos=[-12.0, -3.0, -21.0], yaw=0, scale=[1.0, 1, 2.5], note="hazard 'pool' 4x10"),
      ])
def water_surface(pb):
    pb.plane("Water", 4, 4, nx=8, ny=8, ripple=0.025, seed=2)
    import random
    rnd = random.Random(5)
    for i in range(9):
        x, y = rnd.uniform(-1.7, 1.7), rnd.uniform(-1.7, 1.7)
        pb.sphere("Foam", rnd.uniform(0.08, 0.18), loc=(x, y, 0.02), scale=(2.2, 0.7, 0.12), rot=(0, 0, rnd.uniform(0, 180)),
                  segs=8, rings=4)


@prop("stream_bank_rocks", ["H5", "H6", "H7"], "P1", target=[1.6, 1.4, 4], group="stream",
      notes="4-stud bank module: cobbles + moss from the water line (origin y) up ~1.2. Run along local Z; the "
            "water side is +X. Put it on open hazard edges that have no felt (e.g. H5 stream ends at x=-17 and "
            "x=8, H7 pool west side, H6 millrace south side). Origin at water level minus 0.2.",
      placements=[
          dict(hole="H5", pos=[-17.6, -1.2, -17.5], yaw=0, note="west end of stream, repeat at z=-21.5,-25.5"),
          dict(hole="H5", pos=[8.6, -1.2, -17.5], yaw=180, note="east end, repeat at z=-21.5,-25.5"),
          dict(hole="H6", pos=[7.0, -1.0, -0.6], yaw=-90, note="millrace south side (in front of the mill)"),
          dict(hole="H7", pos=[-14.6, -3.2, -24.0], yaw=0, note="pool west side (cascade covers the rest)"),
      ])
def bank_rocks(pb):
    import random
    rnd = random.Random(11)
    for i in range(7):
        y = -1.75 + i * 0.58 + rnd.uniform(-0.1, 0.1)
        s = rnd.uniform(0.7, 1.05)
        pb.rock("Slate", (s * 0.95, s, s * 0.8), loc=(rnd.uniform(0.1, 0.4), y, 0.0), rot=(0, 0, rnd.uniform(0, 90)),
                seed=i + 1)
        if i % 2 == 0:
            s2 = rnd.uniform(0.6, 0.8)
            pb.rock("Limestone", (s2, s2 * 1.1, s2 * 0.75), loc=(-0.35, y + 0.2, 0.45), seed=i + 20)
    for i in range(4):
        y = -1.5 + i * 1.0
        pb.rock("Moss", (0.9, 0.8, 0.35), loc=(-0.45, y, 0.95), seed=i + 40, amp=0.12)
