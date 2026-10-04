"""KITSUNE (concept R05): floating fox-mask spirit in a red/white robe with gold trim, an ornate
red/gold spirit-flame cannon, paper charms (ofuda), blue spirit-flame tails and floating wisps.
Headless:  Blender -b -P make_kitsune.py -- [outdir]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rca_common import Builder, rgb, reset_scene, finish

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv and len(sys.argv) > sys.argv.index("--") + 1 else \
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "export")

RED = rgb(200, 28, 40)
DRED = rgb(130, 18, 30)
WHITE = rgb(246, 242, 236)
GOLD = rgb(232, 178, 58)
BLACK = rgb(34, 28, 34)
PAPER = rgb(250, 244, 222)
FLAME = rgb(70, 160, 255)
FLAME2 = rgb(185, 230, 255)

reset_scene()
b = Builder("Kitsune")

# ---------------------------------------------------------------- rig
b.joint("RootJoint", "Torso", "HumanoidRootPart", (0, 5.4, 0))
b.joint("Neck", "Head", "Torso", (0, 6.95, 0))
b.joint("RShoulder", "GunArm", "Torso", (1.3, 6.55, 0))
b.joint("LShoulder", "BombArm", "Torso", (-1.3, 6.55, 0))
b.joint("RHip", "LegR", "Torso", (0.5, 4.4, 0))
b.joint("LHip", "LegL", "Torso", (-0.5, 4.4, 0))
b.joint("PodJoint", "Pod", "Torso", (0, 6.2, 0.75))
b.joint("TailJoint", "Tails", "Torso", (0, 4.3, 0.6), anim="wobble")
b.joint("WispJoint", "Wisps", "Torso", (0, 7.2, 0.2), anim="orbit")
b.attach("GunTip", "GunArm", (1.8, 5.25, -3.45))
b.attach("BombTip", "BombArm", (-1.75, 5.3, -1.2))
b.attach("PodTip", "Pod", (0, 7.2, 1.05))

# ---------------------------------------------------------------- torso (robe)
T = "Torso"
b.box(T, (1.75, 1.85, 1.25), (0, 5.8, 0), color=RED, bevel=0.42, segs=3, taper=(1.08, 1.0))
for s in (-1, 1):
    b.box(T, (0.3, 1.45, 0.1), (0.24 * s, 6.12, -0.63), (0, 0, 24 * s), color=WHITE, bevel=0.04)
    b.box(T, (0.09, 1.45, 0.1), (0.42 * s, 6.1, -0.64), (0, 0, 24 * s), color=GOLD, bevel=0.03)
b.box(T, (1.85, 0.55, 1.35), (0, 4.85, 0), color=GOLD, bevel=0.2)
b.box(T, (1.9, 0.14, 1.4), (0, 4.85, 0), color=DRED, bevel=0.05)
b.sphere(T, 0.24, (0, 4.85, -0.72), color=RED, segs=(10, 7))
b.box(T, (0.85, 1.5, 0.1), (0, 3.9, -0.7), color=PAPER, bevel=0.04)
b.box(T, (0.12, 1.1, 0.12), (0, 3.95, -0.76), color=RED, bevel=0.03)
b.box(T, (0.5, 0.1, 0.12), (0, 4.35, -0.76), color=RED, bevel=0.03)
b.box(T, (0.5, 0.1, 0.12), (0, 3.6, -0.76), color=RED, bevel=0.03)
b.torus(T, 0.55, 0.2, (0, 6.75, 0.02), color=WHITE, segs=16, rsegs=6)
b.box(T, (1.6, 0.9, 0.5), (0, 5.95, 0.62), color=DRED, bevel=0.2)

# ---------------------------------------------------------------- head (fox mask)
H = "Head"
b.sphere(H, 0.82, (0, 7.75, 0.18), color=WHITE, scale=(1.0, 0.95, 1.0))
MASK = [(-0.75, 0.5, 0.1), (0.75, 0.5, 0.1), (-0.8, 0.05, 0.2), (0.8, 0.05, 0.2), (-0.68, -0.32, -0.08),
        (0.68, -0.32, -0.08), (-0.5, 0.38, -0.5), (0.5, 0.38, -0.5), (-0.22, -0.12, -1.15), (0.22, -0.12, -1.15),
        (-0.17, -0.38, -1.0), (0.17, -0.38, -1.0), (-0.36, -0.55, -0.3), (0.36, -0.55, -0.3), (0, 0.48, -0.72)]
b.hull(H, MASK, (0, 7.72, -0.2), color=WHITE, bevel=0.05)
for s in (-1, 1):
    b.box(H, (0.5, 0.09, 0.06), (0.36 * s, 7.92, -0.84), (-18, 14 * s, 18 * s), color=RED, bevel=0.02)
    b.box(H, (0.34, 0.07, 0.06), (0.33 * s, 7.78, -0.86), (-18, 14 * s, 16 * s), color=BLACK, bevel=0.02)
    b.box(H, (0.06, 0.4, 0.05), (0.42 * s, 7.45, -0.66), (-25, 0, -20 * s), color=RED, bevel=0.02)
b.box(H, (0.11, 0.38, 0.06), (0, 8.12, -0.64), (-40, 0, 0), color=RED, bevel=0.02)
b.sphere(H, 0.1, (0, 7.56, -1.38), color=BLACK, segs=(8, 6))
EAR = [(-0.38, 0, -0.18), (0.38, 0, -0.18), (-0.38, 0, 0.2), (0.38, 0, 0.2), (0.0, 1.25, 0.02), (0.06, 1.2, 0.08)]
EAR_IN = [(-0.22, 0.12, 0), (0.22, 0.12, 0), (-0.22, 0.12, -0.08), (0.22, 0.12, -0.08), (0.02, 0.95, -0.03)]
b.hull(H, EAR, (0.5, 8.25, 0.12), (0, 0, -16), color=WHITE, bevel=0.05, mirror=True)
b.hull(H, EAR_IN, (0.5, 8.25, -0.09), (0, 0, -16), color=RED, bevel=0.03, mirror=True)
b.cyl(H, 0.06, 0.5, (0.86, 8.0, 0.1), color=GOLD, segs=8, bevel=0, mirror=True)
b.box(H, (0.22, 0.4, 0.22), (0.86, 7.62, 0.1), color=RED, bevel=0.06, mirror=True)
b.box(H, (1.3, 0.75, 0.25), (0, 7.45, 0.85), (20, 0, 0), color=RED, bevel=0.1)


# ---------------------------------------------------------------- sleeves (both arms)
def sleeve(part, mirror_name):
    s = dict(mirror=mirror_name)
    b.sphere(part, 0.52, (1.42, 6.6, 0), color=RED, **s)
    b.box(part, (1.25, 1.85, 1.55), (1.7, 5.8, 0.1), color=RED, bevel=0.3, taper=(0.62, 0.68), **s)
    b.box(part, (1.36, 0.28, 1.66), (1.7, 4.9, 0.1), color=WHITE, bevel=0.1, **s)
    b.box(part, (1.38, 0.12, 1.68), (1.7, 5.08, 0.1), color=GOLD, bevel=0.05, **s)


sleeve("GunArm", "BombArm")

# ---------------------------------------------------------------- spirit-flame cannon (right)
G = "GunArm"
prof = [(0.0, 0.95), (0.45, 0.95), (0.6, 0.8), (0.62, 0.5), (0.72, 0.45), (0.72, 0.22), (0.6, 0.17),
        (0.6, -1.15), (0.7, -1.2), (0.7, -1.45), (0.58, -1.5), (0.58, -2.35), (0.74, -2.45), (0.88, -2.82),
        (0.88, -3.05), (0.52, -3.05), (0.46, -2.85), (0.0, -2.85)]
cols = [RED, RED, RED, GOLD, GOLD, GOLD, RED, GOLD, GOLD, GOLD, RED, GOLD, GOLD, GOLD, GOLD, BLACK, BLACK]
b.lathe(G, prof, (1.8, 5.25, -0.4), (90, 0, 0), colors=cols, segs=18)
b.torus(G, 0.66, 0.07, (1.8, 5.25, -3.45), (90, 0, 0), color=FLAME, segs=18, rsegs=5, glow=True)
b.cyl(G, 0.45, 0.06, (1.8, 5.25, -3.2), (90, 0, 0), color=FLAME2, segs=14, bevel=0, glow=True)
b.hull(G, [(-0.06, 0, -0.4), (0.06, 0, -0.4), (-0.06, 0, 0.4), (0.06, 0, 0.4), (0, 0.45, 0.25)],
       (1.8, 5.85, -1.9), color=GOLD, bevel=0.02)
b.box(G, (0.04, 0.75, 0.32), (2.42, 4.95, -1.6), (0, 0, -6), color=PAPER, bevel=0.01)
b.box(G, (0.05, 0.45, 0.07), (2.43, 4.97, -1.6), (0, 0, -6), color=RED, bevel=0.01)
b.box(G, (0.04, 0.7, 0.3), (2.4, 4.98, -0.95), (0, 0, 4), color=PAPER, bevel=0.01)
b.box(G, (0.05, 0.42, 0.07), (2.41, 5.0, -0.95), (0, 0, 4), color=RED, bevel=0.01)

# ---------------------------------------------------------------- charm hand (left)
L = "BombArm"
for i, a in enumerate((-30, -10, 10, 30)):
    b.box(L, (0.32, 0.78, 0.04), (-1.75, 5.05, -0.9 - i * 0.02), (0, 0, a), color=PAPER, bevel=0.01)
    b.box(L, (0.07, 0.48, 0.05), (-1.75, 5.08, -0.93 - i * 0.02), (0, 0, a), color=RED, bevel=0.01)
b.sphere(L, 0.28, (-1.7, 4.75, -0.75), color=WHITE, segs=(10, 7))
b.sphere(L, 0.22, (-1.75, 5.55, -1.0), color=FLAME, segs=(10, 7), glow=True)


# ---------------------------------------------------------------- legs (hakama panels on flames)
def leg(part, mirror_name):
    s = dict(mirror=mirror_name)
    b.box(part, (1.0, 2.5, 1.35), (0.56, 3.1, 0.02), color=RED, bevel=0.25, taper=(0.75, 0.8), **s)
    b.box(part, (1.12, 0.26, 1.48), (0.58, 1.92, 0.02), color=WHITE, bevel=0.1, **s)
    b.box(part, (1.14, 0.11, 1.5), (0.58, 2.1, 0.02), color=GOLD, bevel=0.04, **s)
    b.lathe(part, [(0.0, 1.85), (0.5, 1.85), (0.42, 1.4), (0.26, 0.95), (0.0, 0.45)], (0.58, 0, 0.0),
            colors=[FLAME2, FLAME2, FLAME, FLAME], segs=10, glow=True, **s)


leg("LegR", "LegL")

# ---------------------------------------------------------------- pod (charm case on the back)
P = "Pod"
b.box(P, (1.0, 1.15, 0.6), (0, 6.25, 0.95), color=DRED, bevel=0.15)
b.box(P, (1.08, 0.12, 0.68), (0, 6.75, 0.95), color=GOLD, bevel=0.04)
b.box(P, (1.08, 0.12, 0.68), (0, 5.75, 0.95), color=GOLD, bevel=0.04)
for i, x in enumerate((-0.28, 0, 0.28)):
    b.box(P, (0.22, 0.7, 0.04), (x, 7.05, 0.95), (0, 0, (i - 1) * -12), color=PAPER, bevel=0.01)
    b.box(P, (0.06, 0.4, 0.05), (x, 7.08, 0.95), (0, 0, (i - 1) * -12), color=RED, bevel=0.01)

# ---------------------------------------------------------------- tails (spirit flame)
import math
for yaw, up in ((-55, 38), (0, 48), (55, 38)):
    # each tail: a long ellipsoid sweeping up and back from the waist, with a pale tip
    d = (math.sin(math.radians(yaw)) * math.cos(math.radians(up)), math.sin(math.radians(up)),
         math.cos(math.radians(yaw)) * math.cos(math.radians(up)))
    c = (d[0] * 1.6, 4.4 + d[1] * 1.6, 0.6 + d[2] * 1.6)
    b.sphere("Tails", 0.55, c, (-up, yaw, 0), color=FLAME, scale=(1.0, 0.9, 3.0), segs=(10, 8), glow=True)
    t = (d[0] * 3.1, 4.4 + d[1] * 3.1, 0.6 + d[2] * 3.1)
    b.sphere("Tails", 0.5, t, color=FLAME2, segs=(10, 7), glow=True)

# ---------------------------------------------------------------- floating wisps (hitodama)
for s in (-1, 1):
    b.sphere("Wisps", 0.4, (2.05 * s, 7.6, 0.35), color=FLAME2, segs=(10, 7), glow=True)
    b.hull("Wisps", [(-0.32, 0, -0.32), (0.32, 0, -0.32), (-0.32, 0, 0.32), (0.32, 0, 0.32), (0, 1.05, 0.15)],
           (2.05 * s, 7.65, 0.38), color=FLAME, glow=True)

finish(b, OUT, focus_y=4.9, spacing=8.5)
