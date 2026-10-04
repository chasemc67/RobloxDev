"""AERO (concept C05; trust the FRONT view of concepts/c05-turnaround.png + c05-parts.png): round white/teal hover
bot, ~3 heads tall and nearly as wide as tall with the fans. Big round head with a dark visor and cyan eyes, teal
brow, one short antenna; two big ducted fans on the shoulders (rotors are Fan1/Fan2); a straight forearm cannon on
the RIGHT arm; an open clamshell of six spotted yellow bombs on the LEFT arm; three small eye drones behind the
right fan (the Pod); level hover boots with a glowing thruster ring under each. Colors from c05-palette.md.
Headless:  Blender -b -P make_aero.py -- [outdir]"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rca_common import Builder, reset_scene, finish, xf

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv and len(sys.argv) > sys.argv.index("--") + 1 else \
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "export")


def hexc(h):
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


SHELL = hexc("E5F0EE")
TEAL = hexc("288FA2")
DTEAL = hexc("21626C")
YELLOW = hexc("F1C63C")
DGOLD = hexc("BB932E")
GLOW = hexc("AEF5F7")
BLACK = hexc("1B2123")

reset_scene()
b = Builder("Aero")

FANS = [((2.45, 6.0, 0.35), (0, 0, -12)), ((-2.45, 6.0, 0.35), (0, 0, 12))]
GX, GY = 2.05, 3.55
# ---------------------------------------------------------------- rig
b.joint("RootJoint", "Torso", "HumanoidRootPart", (0, 3.6, 0))
b.joint("Neck", "Head", "Torso", (0, 4.65, 0))
b.joint("RShoulder", "GunArm", "Torso", (1.45, 4.25, 0))
b.joint("LShoulder", "BombArm", "Torso", (-1.45, 4.25, 0))
b.joint("RHip", "LegR", "Torso", (0.68, 2.55, 0))
b.joint("LHip", "LegL", "Torso", (-0.68, 2.55, 0))
b.joint("PodJoint", "Pod", "Torso", (0.6, 5.2, 0.95))
for i, (p, r) in enumerate(FANS):
    b.joint("Fan%dJoint" % (i + 1), "Fan%d" % (i + 1), "Torso", p, anim="spin", r=r)
b.attach("GunTip", "GunArm", (GX, GY, -2.75))
b.attach("BombTip", "BombArm", (-GX, 3.95, -1.0))
b.attach("PodTip", "Pod", (1.75, 7.0, 1.2))

# ---------------------------------------------------------------- torso
T = "Torso"
b.sphere(T, 1.15, (0, 3.55, 0.02), color=SHELL, scale=(1.12, 1.0, 0.95), segs=(20, 12))
b.hull(T, [(-0.62, 0.55, 0), (0.62, 0.55, 0), (-0.6, -0.2, 0), (0.6, -0.2, 0), (-0.3, -0.75, 0), (0.3, -0.75, 0),
           (-0.52, 0.48, -0.18), (0.52, 0.48, -0.18), (-0.5, -0.18, -0.18), (0.5, -0.18, -0.18), (-0.24, -0.62, -0.18),
           (0.24, -0.62, -0.18)], (0, 3.6, -0.95), color=TEAL, bevel=0.06)
b.torus(T, 0.3, 0.07, (0, 3.68, -1.15), (90, 0, 0), color=YELLOW, segs=16, rsegs=5)
b.cyl(T, 0.25, 0.1, (0, 3.68, -1.14), (90, 0, 0), color=GLOW, segs=14, bevel=0, glow=True)
for sx in (1, -1):
    b.box(T, (0.22, 0.4, 0.3), (1.12 * sx, 3.9, -0.55), (0, 30 * sx, 0), color=YELLOW, bevel=0.07)
b.cyl(T, 0.55, 0.4, (0, 2.62, 0.02), color=BLACK, segs=14)
b.box(T, (1.5, 0.4, 1.05), (0, 2.45, 0.02), color=TEAL, bevel=0.16)
# backpack (drone dock)
b.box(T, (1.3, 1.2, 0.5), (0, 3.85, 0.95), color=SHELL, bevel=0.18)
b.box(T, (0.9, 0.18, 0.54), (0, 4.2, 0.97), color=YELLOW, bevel=0.06)
# fan ducts on struts off the shoulders
DUCT = [(0.88, 0.28), (1.08, 0.28), (1.16, 0.08), (1.16, -0.12), (1.06, -0.3), (0.88, -0.3), (0.88, 0.28)]
for i, (p, r) in enumerate(FANS):
    sx = 1 if p[0] > 0 else -1
    b.lathe(T, DUCT, p, r, colors=[SHELL, SHELL, TEAL, TEAL, TEAL, DTEAL], segs=24)
    b.cyl(T, 0.88, 0.06, (p[0], p[1] - 0.24, p[2]), r, color=DTEAL, segs=20, bevel=0)
    for k in range(3):
        sp = xf(p, r) @ xf((0, -0.15, 0), (0, k * 120 + 30, 0)) @ xf((0.5, 0, 0))
        b.box(T, (0.85, 0.06, 0.1), tuple(sp.to_translation()), tuple(math.degrees(a) for a in sp.to_euler('ZYX')),
              color=DTEAL, bevel=0)
    start = (0.9 * sx, 4.45, 0.35)
    end = (p[0] - 1.0 * sx, p[1] - 0.25, p[2])
    mid = tuple((start[j] + end[j]) / 2 for j in range(3))
    ang = math.degrees(math.atan2(end[1] - start[1], abs(end[0] - start[0])))
    b.box(T, (math.dist(start, end) + 0.3, 0.32, 0.36), mid, (0, 0, ang * sx), color=SHELL, bevel=0.12)
    b.box(T, (0.4, 0.34, 0.38), (end[0] + 0.05 * sx, end[1], end[2]), color=TEAL, bevel=0.1)
    # rotor: yellow hub + 8 teal blades (spins on its joint)
    F = "Fan%d" % (i + 1)
    b.sphere(F, 0.24, (p[0], p[1] + 0.02, p[2]), r, color=YELLOW, segs=(12, 7))
    for k in range(8):
        bl = xf(p, r) @ xf((0, 0, 0), (0, k * 45, 0)) @ xf((0.55, 0, 0), (24, 0, 0))
        b.box(F, (0.62, 0.05, 0.28), tuple(bl.to_translation()), tuple(math.degrees(a) for a in bl.to_euler('ZYX')),
              color=TEAL, bevel=0, taper=None)

# ---------------------------------------------------------------- head
H = "Head"
b.cyl(H, 0.4, 0.4, (0, 4.75, 0), color=BLACK, segs=12)
b.sphere(H, 1.25, (0, 5.9, 0.0), color=SHELL, scale=(1.12, 0.95, 1.0), segs=(22, 12))
b.sphere(H, 1.02, (0, 5.75, -0.62), color=BLACK, scale=(1.0, 0.62, 0.62), segs=(20, 10))
for sx in (1, -1):
    b.box(H, (0.3, 0.42, 0.12), (0.4 * sx, 5.8, -1.22), (6, 0, 0), color=GLOW, bevel=0.12, glow=True)
    b.cyl(H, 0.45, 0.24, (1.36 * sx, 5.85, 0.05), (0, 0, 90), color=TEAL, segs=16)
    b.cyl(H, 0.24, 0.28, (1.4 * sx, 5.85, 0.05), (0, 0, 90), color=YELLOW, segs=12)
b.hull(H, [(-0.75, 0, 0.0), (0.75, 0, 0.0), (-0.45, 0.32, 0.2), (0.45, 0.32, 0.2), (0, -0.12, -0.1),
           (-0.7, 0.05, 0.45), (0.7, 0.05, 0.45), (-0.3, 0.42, 0.7), (0.3, 0.42, 0.7)],
       (0, 6.55, -0.95), (-20, 0, 0), color=TEAL, bevel=0.06)
b.box(H, (0.18, 0.75, 0.42), (0, 7.3, 0.25), (-12, 0, 0), color=TEAL, bevel=0.07, taper=(0.6, 0.6))
b.box(H, (0.16, 0.22, 0.3), (0, 7.75, 0.18), (-12, 0, 0), color=YELLOW, bevel=0.05)


# ---------------------------------------------------------------- arms
def upper(part, sx):
    b.sphere(part, 0.45, (1.5 * sx, 4.25, 0), color=TEAL, segs=(12, 8))
    b.box(part, (0.55, 0.6, 0.6), (1.8 * sx, 3.95, 0), color=SHELL, bevel=0.18)
    b.box(part, (0.58, 0.14, 0.62), (1.8 * sx, 3.7, 0), color=YELLOW, bevel=0.05)


upper("GunArm", 1)
upper("BombArm", -1)

G = "GunArm"
b.lathe(G, [(0.0, 0.45), (0.42, 0.45), (0.55, 0.3), (0.56, 0.0), (0.56, -1.0), (0.6, -1.05), (0.6, -1.3),
            (0.54, -1.35), (0.54, -1.75), (0.6, -1.8), (0.6, -2.1), (0.42, -2.15), (0.0, -2.15)],
        (GX, GY, -0.45), (90, 0, 0), colors=[TEAL, TEAL, SHELL, SHELL, YELLOW, YELLOW, YELLOW, SHELL, TEAL, TEAL, TEAL,
                                              TEAL], segs=20)
b.cyl(G, 0.38, 0.12, (GX, GY, -2.62), (90, 0, 0), color=GLOW, segs=16, bevel=0, glow=True)
b.torus(G, 0.46, 0.07, (GX, GY, -2.56), (90, 0, 0), color=GLOW, segs=16, rsegs=5, glow=True)
b.box(G, (0.5, 0.1, 0.1), (GX, GY + 0.55, -2.35), color=GLOW, bevel=0.03, glow=True)

# open clamshell (bowl + lid hinged back) holding six spotted yellow bombs
L = "BombArm"
CB = (-GX, 3.45, -0.85)
b.sphere(L, 0.85, CB, (180, 0, 0), color=SHELL, segs=(18, 9), cut=0.0)
b.torus(L, 0.84, 0.05, (CB[0], CB[1] + 0.02, CB[2]), color=TEAL, segs=18, rsegs=4)
b.sphere(L, 0.85, (CB[0], CB[1] + 0.8, CB[2] + 1.14), (110, 0, 0), color=SHELL, segs=(18, 9), cut=0.0)
b.box(L, (0.3, 0.1, 0.12), (CB[0], CB[1] - 0.05, CB[2] - 0.86), color=TEAL, bevel=0.03)


def spotted(f, M):
    c = f.calc_center_median()
    return DTEAL if (int((c.x + 2) * 7) * 3 + int((c.y + 2) * 7) * 5 + int((c.z + 2) * 7)) % 5 == 0 else YELLOW


for dx, dy, dz in ((-0.4, 0.22, -0.32), (0.0, 0.22, -0.48), (0.4, 0.22, -0.32), (-0.25, 0.22, 0.15),
                   (0.25, 0.22, 0.15), (0.0, 0.62, -0.1)):
    b.sphere(L, 0.28, (CB[0] + dx, CB[1] + dy, CB[2] + dz), color=spotted, segs=(10, 7))


# ---------------------------------------------------------------- legs (level hover boots)
def leg(part, mirror_name):
    s = dict(mirror=mirror_name)
    x = 0.72
    b.sphere(part, 0.34, (0.68, 2.5, 0.02), color=BLACK, segs=(12, 8), **s)
    b.box(part, (0.6, 0.6, 0.62), (x, 2.05, 0.02), color=SHELL, bevel=0.2, **s)
    b.box(part, (0.82, 0.26, 0.82), (x, 1.66, 0.02), color=TEAL, bevel=0.1, **s)
    b.lathe(part, [(0.0, 1.55), (0.36, 1.55), (0.38, 1.0), (0.48, 0.62), (0.56, 0.5), (0.0, 0.5)],
            (x, 0, 0.02), colors=[SHELL, SHELL, SHELL, SHELL, SHELL], segs=16, **s)
    b.box(part, (0.12, 0.62, 0.06), (x, 1.05, -0.43), (-12, 0, 22), color=YELLOW, bevel=0.02, **s)
    b.lathe(part, [(0.0, 0.62), (0.6, 0.62), (0.7, 0.45), (0.68, 0.35), (0.0, 0.35)], (x, 0, 0.02),
            colors=[TEAL, TEAL, TEAL, DTEAL], segs=18, **s)
    b.torus(part, 0.5, 0.07, (x, 0.34, 0.02), color=GLOW, segs=18, rsegs=5, glow=True, **s)
    b.cyl(part, 0.36, 0.04, (x, 0.34, 0.02), color=GLOW, segs=14, bevel=0, glow=True, **s)


leg("LegR", "LegL")

# ---------------------------------------------------------------- pod: three eye drones behind the right fan
P = "Pod"


def drone_col(f, M):
    c = f.calc_center_median()
    return YELLOW if c.z < -0.05 and c.x > -0.1 else SHELL


for c, rr in (((1.05, 7.35, 1.0), 0.42), ((1.85, 7.05, 1.3), 0.38), ((2.6, 6.95, 1.05), 0.34)):
    b.sphere(P, rr, c, (0, 25, 0), color=drone_col, segs=(14, 9))
    b.cyl(P, rr * 0.45, 0.12, (c[0], c[1], c[2] - rr * 0.95), (90, 0, 0), color=BLACK, segs=12, bevel=0.02)
    b.cyl(P, rr * 0.28, 0.05, (c[0], c[1], c[2] - rr * 1.02), (90, 0, 0), color=GLOW, segs=10, bevel=0, glow=True)
b.box(P, (0.16, 1.6, 0.16), (0.75, 6.1, 1.0), (0, 0, -12), color=BLACK, bevel=0.04)

finish(b, OUT, focus_y=4.0, spacing=10.0)
