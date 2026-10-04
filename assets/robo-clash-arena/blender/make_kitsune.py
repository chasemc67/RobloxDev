"""KITSUNE (concept R05, see concepts/r05-turnaround.png + r05-parts.png): floating fox-mask spirit, no legs.
White kitsune mask with red paint over dark hair, dark-red robe with white lapels and gold trim, a paper-lantern
cannon (longer than the torso) in the RIGHT hand, a talisman box launcher in the LEFT hand (sized from the parts
sheet, not the turnaround), three black-and-gold flame lantern pods on the shoulders and back, and a pale-blue
spirit-flame tail as the lower body (its two lobes are the LegR/LegL limbs). Colors from r05-palette.md.
Headless:  Blender -b -P make_kitsune.py -- [outdir]"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rca_common import Builder, reset_scene, finish

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv and len(sys.argv) > sys.argv.index("--") + 1 else \
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "export")


def hexc(h):
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


WHITE = hexc("EBEFEE")
RED = hexc("A34136")
DRED = hexc("6C2721")
GOLD = hexc("E8C19D")
DGOLD = hexc("B87A5C")
FLAME = hexc("B0D7FA")
FLAME_D = hexc("92A5D1")
BLACK = hexc("201212")
LANTERN = hexc("F7E2B8")

reset_scene()
b = Builder("Kitsune")

GX, GY = 1.85, 4.75
# ---------------------------------------------------------------- rig
b.joint("RootJoint", "Torso", "HumanoidRootPart", (0, 5.0, 0))
b.joint("Neck", "Head", "Torso", (0, 6.5, 0))
b.joint("RShoulder", "GunArm", "Torso", (1.25, 6.05, 0))
b.joint("LShoulder", "BombArm", "Torso", (-1.25, 6.05, 0))
b.joint("RHip", "LegR", "Torso", (0.38, 3.4, 0.1))
b.joint("LHip", "LegL", "Torso", (-0.38, 3.4, 0.1))
b.joint("PodJoint", "Pod", "Torso", (0, 6.3, 0.5))
b.joint("TailJoint", "Tails", "Torso", (0, 3.3, 0.6), anim="wobble")
b.attach("GunTip", "GunArm", (GX, GY, -3.7))
b.attach("BombTip", "BombArm", (-GX, GY, -1.7))
b.attach("PodTip", "BombArm", (-GX, GY, -1.8))

# ---------------------------------------------------------------- torso (robe)
T = "Torso"
b.box(T, (1.6, 1.45, 1.15), (0, 5.6, 0.05), color=DRED, bevel=0.36, segs=3, taper=(1.12, 1.0))
b.torus(T, 0.55, 0.22, (0, 6.32, 0.0), color=WHITE, segs=16, rsegs=6)
skirt = [(0.0, 4.75), (0.82, 4.75), (0.9, 4.3), (1.05, 3.72), (1.17, 3.36), (1.2, 3.2), (1.02, 3.12), (0.0, 3.12)]
b.lathe(T, skirt, (0, 0, 0.05), colors=[DRED, DRED, DRED, RED, WHITE, DRED, DRED], segs=20)
# white lapels / scarf tails down the front, red outer border, gold diamonds
for sx in (1, -1):
    lap = (0.3 * sx, 4.8, -0.9)
    rr = (11.7, 0, 7 * sx)
    b.box(T, (0.42, 2.86, 0.1), lap, rr, color=WHITE, bevel=0.03)
    b.box(T, (0.08, 2.86, 0.12), (lap[0] + 0.2 * sx, lap[1], lap[2]), rr, color=RED, bevel=0.02)
    for k, dy in enumerate((0.75, 0.0, -0.75)):
        b.box(T, (0.17, 0.17, 0.13), (lap[0] + 0.02 * sx + math.sin(math.radians(-7 * sx)) * dy, lap[1] + dy,
                                       lap[2] - math.tan(math.radians(11.7)) * dy - 0.01), (11.7, 0, 45),
              color=GOLD if k != 1 else RED, bevel=0.02)
b.box(T, (1.76, 0.3, 1.25), (0, 4.85, 0.05), color=GOLD, bevel=0.1)
b.box(T, (1.8, 0.09, 1.29), (0, 4.85, 0.05), color=RED, bevel=0.03)
b.sphere(T, 0.17, (0, 4.6, -0.76), color=GOLD, segs=(10, 7))
b.box(T, (0.14, 0.38, 0.14), (0, 4.28, -0.78), color=RED, bevel=0.04)
# back panel with a gold crest
b.box(T, (0.8, 1.3, 0.1), (0, 5.55, 0.66), color=WHITE, bevel=0.03)
b.box(T, (0.3, 0.3, 0.12), (0, 5.55, 0.69), (0, 0, 45), color=GOLD, bevel=0.03)

# ---------------------------------------------------------------- head (fox mask over dark hair)
H = "Head"
b.sphere(H, 0.92, (0, 7.35, 0.32), color=BLACK, scale=(1.08, 1.0, 1.0), segs=(16, 10))
b.box(H, (1.75, 0.9, 1.0), (0, 6.85, 0.48), color=BLACK, bevel=0.38)
MC = (0, 7.3, -0.32)
MASK = [(-0.75, 0.5, 0.1), (0.75, 0.5, 0.1), (-0.8, 0.05, 0.2), (0.8, 0.05, 0.2), (-0.68, -0.32, -0.08),
        (0.68, -0.32, -0.08), (-0.5, 0.38, -0.5), (0.5, 0.38, -0.5), (-0.22, -0.12, -1.15), (0.22, -0.12, -1.15),
        (-0.17, -0.38, -1.0), (0.17, -0.38, -1.0), (-0.36, -0.55, -0.3), (0.36, -0.55, -0.3), (0, 0.48, -0.72)]
S = 1.2
b.hull(H, [(x * S, y * S, z * S + 0.25) for x, y, z in MASK], MC, color=WHITE, bevel=0.05)
for sx in (1, -1):
    # eye slits (black) with a red sweep above, red cheek marks
    b.box(H, (0.46, 0.1, 0.08), (0.36 * sx, MC[1] + 0.12, -1.0), (-20, 16 * sx, 16 * sx), color=BLACK, bevel=0.03)
    b.box(H, (0.56, 0.08, 0.06), (0.4 * sx, MC[1] + 0.3, -0.98), (-20, 16 * sx, 22 * sx), color=RED, bevel=0.02)
    b.box(H, (0.07, 0.42, 0.05), (0.5 * sx, MC[1] - 0.3, -0.84), (-25, 0, -22 * sx), color=RED, bevel=0.02)
    b.box(H, (0.06, 0.3, 0.05), (0.33 * sx, MC[1] - 0.34, -0.95), (-25, 0, -14 * sx), color=RED, bevel=0.02)
# forehead flame mark + nose
b.hull(H, [(-0.12, 0, 0), (0.12, 0, 0), (0, 0.42, -0.05), (0, -0.1, -0.04), (0, 0.2, 0.05)],
       (0, MC[1] + 0.48, -0.86), (-38, 0, 0), color=RED)
b.sphere(H, 0.09, (0, MC[1] - 0.12, -1.42), color=RED, segs=(8, 6))
EAR = [(-0.4, 0, -0.18), (0.4, 0, -0.18), (-0.4, 0, 0.2), (0.4, 0, 0.2), (0.02, 1.35, 0.02), (0.08, 1.3, 0.08)]
EAR_IN = [(-0.24, 0.12, 0), (0.24, 0.12, 0), (-0.24, 0.12, -0.08), (0.24, 0.12, -0.08), (0.03, 1.05, -0.03)]
b.hull(H, EAR, (0.6, 7.9, -0.05), (0, 0, -15), color=WHITE, bevel=0.05, mirror=True)
b.hull(H, EAR_IN, (0.6, 7.9, -0.27), (0, 0, -15), color=RED, bevel=0.03, mirror=True)
b.hull(H, [(-0.05, 0.15, 0), (0.05, 0.15, 0), (-0.05, 0.15, -0.05), (0.03, 0.85, -0.03)],
       (0.82, 7.9, -0.29), (0, 0, -15), color=GOLD, mirror=True)
# side ornaments: gold ring, red tassel
b.torus(H, 0.12, 0.04, (1.0, 7.15, -0.15), (0, 0, 90), color=GOLD, segs=10, rsegs=4, mirror=True)
b.box(H, (0.16, 0.42, 0.16), (1.0, 6.82, -0.15), color=RED, bevel=0.05, mirror=True)


# ---------------------------------------------------------------- sleeves (both arms)
def sleeve(part, sx):
    b.sphere(part, 0.45, (1.3 * sx, 6.1, 0), color=DRED, segs=(12, 8))
    b.box(part, (1.0, 1.35, 1.35), (1.8 * sx, 5.38, -0.12), color=DRED, bevel=0.25, taper=(0.72, 0.75))
    b.box(part, (1.06, 0.3, 1.42), (1.8 * sx, 4.78, -0.12), color=WHITE, bevel=0.08)
    b.box(part, (1.08, 0.09, 1.44), (1.8 * sx, 4.66, -0.12), color=RED, bevel=0.03)
    b.box(part, (0.06, 0.42, 0.42), (2.31 * sx, 5.35, -0.12), (45, 0, 0), color=GOLD, bevel=0.03)
    b.cyl(part, 0.1, 0.08, (2.35 * sx, 5.35, -0.12), (0, 0, 90), color=RED, segs=8, bevel=0)


sleeve("GunArm", 1)
sleeve("BombArm", -1)

# ---------------------------------------------------------------- lantern cannon (right hand, longer than the torso)
G = "GunArm"
b.sphere(G, 0.24, (GX, GY - 0.2, -0.35), color=WHITE, segs=(10, 7))
prof = [(0.0, 0.6), (0.5, 0.6), (0.62, 0.5), (0.62, 0.28), (0.55, 0.28), (0.55, -0.25), (0.64, -0.25),
        (0.64, -0.42), (0.5, -0.42), (0.5, -1.62), (0.64, -1.62), (0.64, -1.78), (0.58, -1.78), (0.58, -2.2),
        (0.66, -2.2), (0.66, -3.0), (0.76, -3.0), (0.76, -3.25), (0.72, -3.25), (0.78, -3.32), (0.78, -3.62),
        (0.5, -3.62), (0.44, -3.42), (0.0, -3.42)]
cols = [GOLD, GOLD, GOLD, BLACK, BLACK, BLACK, GOLD, GOLD, BLACK, BLACK, GOLD, GOLD, BLACK, BLACK, BLACK, WHITE,
        GOLD, GOLD, GOLD, GOLD, GOLD, BLACK, BLACK]
b.lathe(G, prof, (GX, GY, 0.0), (90, 0, 0), colors=cols, segs=20)
b.lathe(G, [(0.0, -0.42), (0.56, -0.42), (0.74, -0.65), (0.78, -1.02), (0.74, -1.4), (0.56, -1.62), (0.0, -1.62)],
        (GX, GY, 0.0), (90, 0, 0), color=LANTERN, segs=20, glow=True)
# gold lantern ribs + red flame prints
for a in (0, 90, 180, 270):
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    b.box(G, (0.07, 0.07, 1.18), (GX + ca * 0.76, GY + sa * 0.76, -1.02), color=DGOLD, bevel=0.02)
FLAME_PTS = [(-0.16, 0, -0.18), (0.16, 0, -0.18), (0.0, 0, 0.32), (0.0, 0.05, 0.0), (-0.06, 0, 0.12), (0.06, 0, 0.12)]
b.hull(G, FLAME_PTS, (GX, GY + 0.79, -1.0), (0, 0, 0), color=RED)
b.hull(G, FLAME_PTS, (GX + 0.79, GY, -1.0), (0, 0, -90), color=RED)
b.box(G, (0.3, 0.06, 0.4), (GX, GY + 0.67, -2.6), color=RED, bevel=0.02)
b.box(G, (0.06, 0.3, 0.4), (GX + 0.67, GY, -2.6), color=RED, bevel=0.02)
b.box(G, (0.12, 0.3, 0.5), (GX, GY + 0.72, -1.85), color=DGOLD, bevel=0.03)
# hanging bell + tassel
b.cyl(G, 0.03, 0.4, (GX, GY - 0.95, -1.0), color=GOLD, segs=6, bevel=0)
b.sphere(G, 0.13, (GX, GY - 1.2, -1.0), color=GOLD, segs=(10, 7))
b.box(G, (0.18, 0.45, 0.18), (GX, GY - 1.55, -1.0), color=RED, bevel=0.05, taper=(0.6, 0.6))

# ---------------------------------------------------------------- talisman box launcher (left hand, parts-sheet size)
L = "BombArm"
LB = (-GX, GY, -0.95)
b.sphere(L, 0.24, (-GX, GY - 0.2, -0.25), color=WHITE, segs=(10, 7))
b.box(L, (0.98, 0.98, 1.35), LB, color=WHITE, bevel=0.08)
b.box(L, (1.03, 1.03, 0.36), (LB[0], LB[1], LB[2] + 0.4), color=RED, bevel=0.06)
b.box(L, (1.03, 1.03, 0.22), (LB[0], LB[1], LB[2] - 0.42), color=RED, bevel=0.05)
b.box(L, (1.1, 1.1, 0.12), (LB[0], LB[1], LB[2] - 0.66), color=GOLD, bevel=0.04)
b.box(L, (1.1, 1.1, 0.1), (LB[0], LB[1], LB[2] + 0.66), color=GOLD, bevel=0.03)
b.box(L, (0.78, 0.78, 0.12), (LB[0], LB[1], LB[2] - 0.7), color=BLACK, bevel=0.03)
for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
    b.box(L, (0.08, 0.08, 1.34), (LB[0] + 0.5 * sx, LB[1] + 0.5 * sy, LB[2]), color=DGOLD, bevel=0.02)
b.cyl(L, 0.2, 0.08, (LB[0] - 0.52, LB[1], LB[2]), (0, 0, 90), color=GOLD, segs=12, bevel=0.02)
b.cyl(L, 0.2, 0.08, (LB[0], LB[1] + 0.52, LB[2]), color=GOLD, segs=12, bevel=0.02)
CHARM = [(-0.16, 0, 0.0), (0.16, 0, 0.0), (0.0, 0, -0.5), (-0.16, 0.03, 0.0), (0.16, 0.03, 0.0), (0.0, 0.03, -0.5)]
b.hull(L, CHARM, (LB[0] - 0.15, LB[1] + 0.12, LB[2] - 0.7), (0, 18, 0), color=WHITE)
b.hull(L, CHARM, (LB[0] + 0.15, LB[1] - 0.1, LB[2] - 0.72), (10, -14, 30), color=WHITE)
b.box(L, (0.08, 0.04, 0.22), (LB[0] - 0.2, LB[1] + 0.15, LB[2] - 0.98), (0, 18, 0), color=RED, bevel=0.01)


# ---------------------------------------------------------------- flame tail lobes (LegR/LegL)
def lobe(part, mirror_name):
    b.lathe(part, [(0.0, 3.45), (0.72, 3.35), (0.88, 2.85), (0.8, 2.25), (0.55, 1.65), (0.26, 1.15), (0.0, 0.85)],
            (0.95, 0, 0.1), (0, 0, 13), colors=[FLAME, FLAME, FLAME, FLAME_D, FLAME_D, FLAME_D], segs=14, glow=True,
            mirror=mirror_name)
    # curled wisp at the bottom, flicking outwards
    b.lathe(part, [(0.0, 0.0), (0.16, 0.12), (0.17, 0.35), (0.1, 0.6), (0.0, 0.8)], (0.78, 1.05, 0.12), (0, 0, -140),
            color=FLAME_D, segs=10, glow=True, mirror=mirror_name)


lobe("LegR", "LegL")

# ---------------------------------------------------------------- trailing flame (Tails)
TEAR = [(0.0, 0.0), (0.42, 0.25), (0.55, 0.75), (0.45, 1.35), (0.26, 1.9), (0.0, 2.35)]
b.lathe("Tails", TEAR, (0, 3.05, 0.55), (100, 0, 0), color=FLAME, segs=12, glow=True)
b.lathe("Tails", [(x * 0.6, y * 0.6) for x, y in TEAR], (0, 2.7, 2.6), (35, 0, 0), color=FLAME_D, segs=10, glow=True)


# ---------------------------------------------------------------- pods: three black-and-gold flame lanterns
def lantern(c, rod_from):
    P = "Pod"
    b.sphere(P, 0.36, c, color=BLACK, segs=(14, 9))
    b.torus(P, 0.36, 0.05, c, color=GOLD, segs=14, rsegs=4)
    b.cyl(P, 0.15, 0.1, (c[0], c[1] + 0.36, c[2]), color=GOLD, segs=10, bevel=0)
    b.cyl(P, 0.2, 0.06, (c[0], c[1], c[2] - 0.34), (90, 0, 0), color=FLAME, segs=12, bevel=0, glow=True)
    b.hull(P, [(0.2 * math.cos(a * math.pi / 4), 0, 0.2 * math.sin(a * math.pi / 4)) for a in range(8)] +
           [(0.0, 0.65, 0.06), (0.05, 0.35, 0.18)], (c[0], c[1] + 0.42, c[2]), color=FLAME_D, glow=True, smooth=True)
    b.hull(P, [(0.12 * math.cos(a * math.pi / 3), 0, 0.12 * math.sin(a * math.pi / 3)) for a in range(6)] +
           [(0.0, 0.42, 0.04)], (c[0], c[1] + 0.44, c[2] - 0.06), color=FLAME, glow=True, smooth=True)
    for sx in (1, -1):
        b.box(P, (0.1, 0.32, 0.1), (c[0] + 0.4 * sx, c[1] - 0.25, c[2]), color=RED, bevel=0.03, taper=(0.6, 0.6))
    b.sphere(P, 0.08, (c[0], c[1] - 0.45, c[2]), color=GOLD, segs=(8, 6))
    b.box(P, (0.13, 0.3, 0.13), (c[0], c[1] - 0.68, c[2]), color=RED, bevel=0.04, taper=(0.6, 0.6))
    d = [c[i] - rod_from[i] for i in range(3)]
    ln = math.sqrt(sum(v * v for v in d))
    mid = tuple((c[i] + rod_from[i]) / 2 for i in range(3))
    ax = math.degrees(math.atan2(d[2], d[1]))
    az = -math.degrees(math.atan2(d[0], math.hypot(d[1], d[2])))
    b.cyl(P, 0.05, ln, mid, (ax, 0, az), color=DGOLD, segs=6, bevel=0)


lantern((1.62, 7.2, 0.25), (1.05, 6.3, 0.45))
lantern((-1.62, 7.2, 0.25), (-1.05, 6.3, 0.45))
lantern((0, 8.45, 0.95), (0, 7.4, 0.7))

finish(b, OUT, focus_y=4.9, spacing=8.5)
