"""AERO (concept C05): round white/teal hover bot with a big dark-screen head and cyan eyes, four ducted
hover fans, a glowing arm cannon (right) and a cluster-bomb launcher (left), hover drone on the back.
Headless:  Blender -b -P make_aero.py -- [outdir]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rca_common import Builder, rgb, reset_scene, finish

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv and len(sys.argv) > sys.argv.index("--") + 1 else \
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "export")

WHITE = rgb(242, 245, 248)
TEAL = rgb(0, 128, 130)
TEAL2 = rgb(25, 165, 160)
YELLOW = rgb(248, 192, 40)
DARK = rgb(40, 46, 56)
VISOR = rgb(16, 22, 30)
GLOW = rgb(80, 240, 255)

reset_scene()
b = Builder("Aero")

FANS = [((2.45, 5.55, 1.25), (0, 0, -22)), ((-2.45, 5.55, 1.25), (0, 0, 22)),
        ((1.55, 7.45, 1.05), (0, 0, -14)), ((-1.55, 7.45, 1.05), (0, 0, 14))]

# ---------------------------------------------------------------- rig
b.joint("RootJoint", "Torso", "HumanoidRootPart", (0, 3.9, 0))
b.joint("Neck", "Head", "Torso", (0, 4.85, 0))
b.joint("RShoulder", "GunArm", "Torso", (1.85, 4.35, 0))
b.joint("LShoulder", "BombArm", "Torso", (-1.85, 4.35, 0))
b.joint("RHip", "LegR", "Torso", (0.75, 2.65, 0))
b.joint("LHip", "LegL", "Torso", (-0.75, 2.65, 0))
b.joint("PodJoint", "Pod", "Torso", (0, 4.3, 1.35))
for i, (p, r) in enumerate(FANS):
    b.joint("Fan%dJoint" % (i + 1), "Fan%d" % (i + 1), "Torso", p, anim="spin", r=r)
b.attach("GunTip", "GunArm", (2.15, 3.9, -3.0))
b.attach("BombTip", "BombArm", (-2.2, 4.25, -1.75))
b.attach("PodTip", "Pod", (0, 5.0, 1.9))

# ---------------------------------------------------------------- torso
T = "Torso"
b.sphere(T, 1.25, (0, 3.75, 0), color=WHITE, scale=(1.15, 0.92, 1.0), segs=(18, 10))
b.torus(T, 1.3, 0.12, (0, 3.45, 0), color=TEAL, segs=20, rsegs=6, scale_y=1.4)
b.torus(T, 0.36, 0.09, (0, 3.75, -1.18), (90, 0, 0), color=TEAL2, segs=14, rsegs=6)
b.sphere(T, 0.3, (0, 3.75, -1.15), color=GLOW, segs=(12, 8), glow=True)
b.box(T, (1.45, 0.55, 1.15), (0, 2.82, 0.05), color=TEAL, bevel=0.2)
b.box(T, (1.1, 0.9, 0.7), (0, 4.0, 1.1), color=TEAL, bevel=0.25)
for i, (p, r) in enumerate(FANS):
    from rca_common import xf
    import math
    # duct ring + strut back to the body
    b.torus(T, 0.8, 0.17, p, r, color=WHITE, segs=16, rsegs=6, scale_y=1.6)
    b.torus(T, 0.82, 0.09, (p[0], p[1] - 0.2, p[2]), r, color=TEAL2, segs=16, rsegs=4)
    b.cyl(T, 0.12, 0.25, p, r, color=DARK, segs=8, bevel=0)
    sx = 1 if p[0] > 0 else -1
    start = (0.55 * sx, 4.2 if p[1] < 6.5 else 4.6, 1.15)
    mid = ((start[0] + p[0]) / 2, (start[1] + p[1]) / 2, (start[2] + p[2]) / 2)
    dx, dy = p[0] - start[0], p[1] - start[1]
    length = math.hypot(dx, dy) - 0.75
    ang = math.degrees(math.atan2(dx, dy))
    b.box(T, (0.26, length, 0.26), mid, (0, 0, -ang), color=DARK, bevel=0.06)
    # rotor (spins)
    F = "Fan%d" % (i + 1)
    b.sphere(F, 0.2, p, r, color=YELLOW, segs=(10, 6))
    for k in range(3):
        bl = xf(p, r) @ xf((0, 0, 0), (0, k * 120, 0))
        loc = bl @ xf((0.4, 0, 0), (18, 0, 0))
        b.box(F, (0.66, 0.06, 0.3), tuple(loc.to_translation()), tuple(math.degrees(a) for a in loc.to_euler('ZYX')),
              color=TEAL, bevel=0.02)

# ---------------------------------------------------------------- head
H = "Head"
b.cyl(H, 0.42, 0.45, (0, 4.95, 0), color=DARK, segs=12)
b.sphere(H, 1.5, (0, 6.15, 0.05), color=WHITE, scale=(1.06, 0.95, 1.0), segs=(20, 11))
b.sphere(H, 1.28, (0, 6.05, -0.72), color=VISOR, scale=(1.0, 0.74, 0.62), segs=(20, 10))
for s in (-1, 1):
    b.box(H, (0.36, 0.52, 0.14), (0.42 * s, 6.1, -1.45), (4, 0, 0), color=GLOW, bevel=0.15, glow=True)
b.cyl(H, 0.52, 0.3, (1.55, 6.05, 0.05), (0, 0, 90), color=TEAL, segs=14, mirror=True)
b.cyl(H, 0.25, 0.34, (1.6, 6.05, 0.05), (0, 0, 90), color=YELLOW, segs=12, mirror=True)
b.box(H, (0.5, 0.25, 1.9), (0, 7.5, 0.15), (-6, 0, 0), color=TEAL, bevel=0.1)
b.cyl(H, 0.06, 0.65, (0.35, 7.85, 0.35), color=DARK, segs=6, bevel=0)
b.sphere(H, 0.19, (0.35, 8.2, 0.35), color=YELLOW, segs=(10, 6))

# ---------------------------------------------------------------- arms
for part, sx in (("GunArm", 1), ("BombArm", -1)):
    b.sphere(part, 0.6, (1.95 * sx, 4.45, 0), color=TEAL)
    b.box(part, (0.7, 0.8, 0.75), (2.05 * sx, 3.95, 0), color=WHITE, bevel=0.22)

G = "GunArm"
b.lathe(G, [(0.0, 0.65), (0.45, 0.65), (0.62, 0.45), (0.65, 0.0), (0.65, -1.1), (0.55, -1.25), (0.5, -1.25),
            (0.0, -1.25)], (2.15, 3.9, -0.55), (90, 0, 0), color=WHITE, segs=18)
b.torus(G, 0.66, 0.09, (2.15, 3.9, -0.6), (90, 0, 0), color=TEAL, segs=18, rsegs=6)
b.torus(G, 0.66, 0.09, (2.15, 3.9, -1.25), (90, 0, 0), color=TEAL, segs=18, rsegs=6)
b.cyl(G, 0.36, 1.1, (2.15, 3.9, -2.35), (90, 0, 0), color=GLOW, segs=14, bevel=0.08, glow=True)
b.torus(G, 0.4, 0.08, (2.15, 3.9, -1.85), (90, 0, 0), color=YELLOW, segs=14, rsegs=5)

L = "BombArm"
b.box(L, (1.35, 1.3, 1.55), (-2.2, 3.95, -0.75), color=WHITE, bevel=0.3)
b.box(L, (0.12, 0.9, 1.2), (-2.9, 3.95, -0.75), color=TEAL, bevel=0.05)
b.box(L, (1.2, 1.15, 0.2), (-2.2, 3.95, -1.55), color=TEAL, bevel=0.06)
for gx in (-0.38, 0, 0.38):
    for gy in (-0.36, 0, 0.36):
        b.cyl(L, 0.15, 0.4, (-2.2 + gx, 3.95 + gy, -1.75), (90, 0, 0), color=DARK, segs=10, bevel=0.03)
        b.torus(L, 0.14, 0.04, (-2.2 + gx, 3.95 + gy, -1.95), (90, 0, 0), color=YELLOW, segs=10, rsegs=4)


# ---------------------------------------------------------------- legs
def leg(part, mirror_name):
    s = dict(mirror=mirror_name)
    b.sphere(part, 0.4, (0.78, 2.6, 0.02), color=TEAL, segs=(12, 8), **s)
    b.box(part, (0.82, 0.95, 0.9), (0.86, 1.95, 0.02), color=WHITE, bevel=0.26, **s)
    b.sphere(part, 0.3, (0.88, 1.45, -0.32), color=YELLOW, segs=(10, 7), **s)
    b.box(part, (0.98, 0.95, 1.08), (0.9, 1.0, 0.02), color=TEAL, bevel=0.26, taper=(0.85, 0.85), **s)
    b.box(part, (1.2, 0.5, 1.65), (0.9, 0.3, -0.15), color=WHITE, bevel=0.2, **s)
    b.box(part, (1.22, 0.36, 0.42), (0.9, 0.26, -0.85), color=YELLOW, bevel=0.12, **s)
    b.cyl(part, 0.42, 0.08, (0.9, 0.03, 0.0), color=GLOW, segs=14, bevel=0, glow=True, **s)


leg("LegR", "LegL")

# ---------------------------------------------------------------- pod (docked hover drone)
P = "Pod"
b.sphere(P, 0.55, (0, 4.45, 1.55), color=WHITE, segs=(14, 8))
b.torus(P, 0.56, 0.07, (0, 4.45, 1.55), color=TEAL, segs=14, rsegs=5)
b.sphere(P, 0.16, (0, 4.5, 2.07), color=GLOW, segs=(10, 6), glow=True)
b.cyl(P, 0.05, 0.3, (0, 5.05, 1.55), color=DARK, segs=6, bevel=0)
b.box(P, (0.95, 0.04, 0.16), (0, 5.2, 1.55), (0, 30, 0), color=DARK, bevel=0.01)

finish(b, OUT, focus_y=4.3, spacing=10.0)
