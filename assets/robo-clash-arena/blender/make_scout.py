"""SCOUT (concept C01, see concepts/c01-turnaround.png + c01-parts.png): white/cyan, ~3 heads tall, big
eared helmet with one horizontal visor slit, twin-barrel blaster on the RIGHT arm, 2x2 sticky-mine launcher
on the LEFT forearm, reverse-joint legs on two-wheel roller skates, two eyed drone pods on short arms off
the back. Colors are the c01-palette.md hex values. Headless:
  Blender -b -P make_scout.py -- [outdir]
Writes scout.fbx, scout_rig.json, scout_preview.png. Roblox coords (see rca_common)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rca_common import Builder, reset_scene, finish

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv and len(sys.argv) > sys.argv.index("--") + 1 else \
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "export")


def hexc(h):
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


SHELL = hexc("E8E9EC")
CYAN = hexc("35BDE1")
DCYAN = hexc("2298BB")
TEAL = hexc("1A6B82")
GLOW = hexc("90E2F0")
BLACK = hexc("17191B")

reset_scene()
b = Builder("Scout")

# ---------------------------------------------------------------- rig
b.joint("RootJoint", "Torso", "HumanoidRootPart", (0, 4.3, 0))
b.joint("Neck", "Head", "Torso", (0, 5.75, 0))
b.joint("RShoulder", "GunArm", "Torso", (1.35, 5.3, 0))
b.joint("LShoulder", "BombArm", "Torso", (-1.35, 5.3, 0))
b.joint("RHip", "LegR", "Torso", (0.62, 3.85, 0))
b.joint("LHip", "LegL", "Torso", (-0.62, 3.85, 0))
b.joint("PodJoint", "Pod", "Torso", (0, 5.5, 0.8))
GX, GY = 2.0, 4.15
b.attach("GunTip", "GunArm", (GX, GY + 0.25, -2.75))
b.attach("GunTip2", "GunArm", (GX, GY - 0.25, -2.75))
b.attach("BombTip", "BombArm", (-GX, 4.2, -1.75))
b.attach("PodTip", "BombArm", (-GX, 4.2, -1.85))

# ---------------------------------------------------------------- torso
T = "Torso"
b.box(T, (0.95, 0.5, 0.8), (0, 3.9, 0.05), color=BLACK, bevel=0.15)
b.box(T, (1.35, 0.45, 1.05), (0, 4.2, 0.05), color=SHELL, bevel=0.18, taper=(1.15, 1.0))
b.cyl(T, 0.42, 0.4, (0, 4.5, 0.05), color=BLACK, segs=12)
b.box(T, (1.9, 1.25, 1.3), (0, 5.15, 0.05), color=SHELL, bevel=0.36, segs=3, taper=(1.12, 1.05))
# cyan chest plate (shield shape) with a dark centre slot
b.hull(T, [(-0.62, 0.45, 0), (0.62, 0.45, 0), (-0.5, -0.15, 0), (0.5, -0.15, 0), (0, -0.55, 0),
           (-0.55, 0.4, -0.12), (0.55, 0.4, -0.12), (-0.42, -0.12, -0.12), (0.42, -0.12, -0.12), (0, -0.45, -0.12)],
       (0, 5.15, -0.66), color=CYAN, bevel=0.04)
b.box(T, (0.26, 0.5, 0.1), (0, 5.05, -0.8), color=TEAL, bevel=0.04)
b.box(T, (1.0, 0.28, 0.9), (0, 5.8, 0.05), color=BLACK, bevel=0.1)
# back block with a dark vent
b.box(T, (1.2, 1.0, 0.45), (0, 5.15, 0.78), color=SHELL, bevel=0.15)
for i in range(3):
    b.box(T, (0.6, 0.09, 0.08), (0, 4.95 + i * 0.18, 1.02), color=BLACK, bevel=0.02)

# ---------------------------------------------------------------- head (big eared helmet)
H = "Head"
R = 1.32
HC = (0, 7.05, 0.05)


def helmet_col(f, M):
    c = f.calc_center_median()  # local: Y axis = world X (pole), x = world Y, z = world Z
    wx, wy, wz = -c.y / R, c.x / R, c.z / R
    if -0.6 < wy < 0.0 and wz < -0.45:
        return BLACK  # faceplate
    if wy < -0.82 or (wy < -0.35 and wz > 0.5):
        return BLACK
    if abs(wx) < 0.17:
        return CYAN  # crown stripe
    return SHELL


b.cyl(H, 0.34, 0.6, (0, 5.95, 0.05), color=BLACK, segs=12)
b.sphere(H, R, HC, (0, 0, 90), color=helmet_col, scale=(0.95, 1.06, 1.0), segs=(26, 14))
# visor slit: thin curved glow bar across the faceplate
arc = []
for a in range(-48, 49, 12):
    for rr in (R + 0.03, R - 0.25):
        for dy in (-0.075, 0.075):
            arc.append((rr * 1.06 * math.sin(math.radians(a)), dy, -rr * math.cos(math.radians(a))))
b.hull(H, arc, (0, HC[1] - 0.32, HC[2]), color=GLOW, glow=True)
# ear discs: white rim, cyan ring, dark centre
b.cyl(H, 0.66, 0.24, (1.36, 6.95, 0.12), (0, 0, 90), color=SHELL, segs=18, mirror=True)
b.torus(H, 0.45, 0.09, (1.5, 6.95, 0.12), (0, 0, 90), color=CYAN, segs=18, rsegs=6, mirror=True)
b.cyl(H, 0.34, 0.26, (1.47, 6.95, 0.12), (0, 0, 90), color=BLACK, segs=14, mirror=True)
# ear fins: cyan blades, up and out, swept back
FIN = [(-0.45, 0, -0.14), (0.45, 0, -0.14), (-0.45, 0, 0.14), (0.45, 0, 0.14), (0.2, 1.4, -0.05), (0.24, 1.36, 0.06)]
b.hull(H, FIN, (0.98, 7.95, 0.15), (0, 0, -30), color=CYAN, bevel=0.06, mirror=True)
b.hull(H, [(-0.26, 0, -0.04), (0.26, 0, -0.04), (-0.26, 0, 0.04), (0.26, 0, 0.04), (0.12, 0.9, 0)], (0.98, 8.0, -0.13), (0, 0, -30),
       color=DCYAN, mirror=True)


# ---------------------------------------------------------------- arms
def shoulder(part, sx):
    b.hull(part, [(-0.45, -0.25, -0.5), (0.45, -0.25, -0.5), (-0.45, -0.25, 0.5), (0.45, -0.25, 0.5),
                  (-0.32, 0.35, -0.38), (0.32, 0.35, -0.38), (-0.32, 0.35, 0.38), (0.32, 0.35, 0.38)],
           (1.55 * sx, 5.45, 0), (0, 0, -14 * sx), color=CYAN, bevel=0.12)
    b.sphere(part, 0.34, (1.6 * sx, 5.2, 0), color=BLACK, segs=(12, 8))
    b.cyl(part, 0.24, 0.8, (1.75 * sx, 4.75, 0), color=BLACK, segs=10)


shoulder("GunArm", 1)
shoulder("BombArm", -1)

# right: twin-barrel blaster (barrels stacked vertically, like the parts sheet)
G = "GunArm"
b.box(G, (1.0, 1.05, 1.9), (GX, GY, -0.75), color=SHELL, bevel=0.26)
b.box(G, (1.08, 1.12, 0.55), (GX, GY, -0.6), color=CYAN, bevel=0.14)
b.box(G, (0.55, 0.32, 1.0), (GX, GY + 0.62, -0.85), color=SHELL, bevel=0.12)
b.cyl(G, 0.38, 0.4, (GX, GY, 0.32), (90, 0, 0), color=BLACK, segs=12)
b.box(G, (0.86, 1.0, 0.35), (GX, GY, -1.78), color=BLACK, bevel=0.1)
for dy in (0.25, -0.25):
    b.cyl(G, 0.22, 0.75, (GX, GY + dy, -2.25), (90, 0, 0), color=BLACK, segs=14, bevel=0.04)
    b.torus(G, 0.17, 0.05, (GX, GY + dy, -2.63), (90, 0, 0), color=GLOW, segs=14, rsegs=5, glow=True)

# left: sticky-mine launcher (box, cyan side plates, 2x2 barrels)
L = "BombArm"
b.box(L, (1.05, 1.0, 1.55), (-GX, 4.2, -0.6), color=SHELL, bevel=0.24)
b.box(L, (0.1, 0.75, 1.1), (-GX - 0.55, 4.2, -0.55), color=CYAN, bevel=0.04)
b.cyl(L, 0.15, 0.08, (-GX - 0.6, 4.2, -0.45), (0, 0, 90), color=CYAN, segs=10, bevel=0)
b.box(L, (0.62, 0.22, 1.2), (-GX, 4.78, -0.6), color=CYAN, bevel=0.08)
b.box(L, (0.98, 0.95, 0.25), (-GX, 4.2, -1.45), color=BLACK, bevel=0.07)
for dx in (-0.22, 0.22):
    for dy in (-0.22, 0.22):
        b.cyl(L, 0.15, 0.2, (-GX + dx, 4.2 + dy, -1.6), (90, 0, 0), color=BLACK, segs=10, bevel=0.03)
        b.torus(L, 0.12, 0.035, (-GX + dx, 4.2 + dy, -1.7), (90, 0, 0), color=GLOW, segs=10, rsegs=4, glow=True)


# ---------------------------------------------------------------- legs (reverse joint + roller skates)
def leg(part, mirror_name):
    s = dict(mirror=mirror_name)
    x = 0.64
    b.sphere(part, 0.34, (0.62, 3.85, 0), color=BLACK, segs=(12, 8), **s)
    b.box(part, (0.62, 1.2, 0.72), (x, 3.25, -0.25), (22.6, 0, 0), color=SHELL, bevel=0.22, **s)
    b.box(part, (0.4, 0.75, 0.12), (x, 3.25, -0.62), (22.6, 0, 0), color=CYAN, bevel=0.05, **s)
    b.sphere(part, 0.3, (x, 2.62, -0.52), color=BLACK, segs=(12, 8), **s)
    b.hull(part, [(-0.32, -0.2, -0.3), (0.32, -0.2, -0.3), (-0.3, 0.3, -0.22), (0.3, 0.3, -0.22),
                  (0, 0.42, -0.1), (-0.3, -0.2, 0.15), (0.3, -0.2, 0.15)], (x, 2.65, -0.6), color=CYAN, bevel=0.06, **s)
    b.box(part, (0.48, 1.55, 0.5), (x, 1.82, -0.12), (-28.7, 0, 0), color=SHELL, bevel=0.18, **s)
    b.box(part, (0.52, 0.6, 0.55), (x, 1.55, 0.02), (-28.7, 0, 0), color=CYAN, bevel=0.16, **s)
    b.cyl(part, 0.12, 1.2, (x, 1.9, 0.2), (-28.7, 0, 0), color=BLACK, segs=8, bevel=0, **s)
    b.sphere(part, 0.26, (x, 1.02, 0.3), color=BLACK, segs=(10, 7), **s)
    # skate: cyan housing, white boot cap, two black wheels with glowing hubs
    b.hull(part, [(-0.34, 0.0, -0.75), (0.34, 0.0, -0.75), (-0.34, 0.0, 0.65), (0.34, 0.0, 0.65),
                  (-0.3, 0.55, -0.35), (0.3, 0.55, -0.35), (-0.3, 0.75, 0.35), (0.3, 0.75, 0.35)],
           (x, 0.42, -0.02), color=DCYAN, bevel=0.1, **s)
    b.box(part, (0.56, 0.32, 0.55), (x, 1.05, -0.12), color=SHELL, bevel=0.12, **s)
    for wz in (-0.5, 0.52):
        b.cyl(part, 0.3, 0.3, (x, 0.3, wz), (0, 0, 90), color=BLACK, segs=14, bevel=0.06, **s)
        b.cyl(part, 0.14, 0.34, (x, 0.3, wz), (0, 0, 90), color=GLOW, segs=10, bevel=0, glow=True, **s)


leg("LegR", "LegL")

# ---------------------------------------------------------------- pod: two eyed drones on short back arms
P = "Pod"
for sx in (1, -1):
    c = (1.85 * sx, 7.35, 0.75)
    start = (0.5 * sx, 5.6, 0.95)
    mid = ((start[0] + c[0]) / 2, (start[1] + c[1]) / 2, (start[2] + c[2]) / 2)
    ln = math.dist(start, c)
    ang = math.degrees(math.atan2(c[0] - start[0], c[1] - start[1]))
    b.box(P, (0.22, ln, 0.22), mid, (0, 0, -ang), color=BLACK, bevel=0.05)
    b.sphere(P, 0.5, c, color=SHELL, segs=(16, 10))
    b.cyl(P, 0.27, 0.16, (c[0], c[1], c[2] - 0.44), (90, 0, 0), color=BLACK, segs=14, bevel=0.03)
    b.cyl(P, 0.15, 0.06, (c[0], c[1], c[2] - 0.53), (90, 0, 0), color=GLOW, segs=12, bevel=0, glow=True)
    b.hull(P, [(-0.1, 0, -0.22), (0.1, 0, -0.22), (-0.1, 0, 0.22), (0.1, 0, 0.22), (0.0, 0.62, 0.05)],
           (c[0] + 0.32 * sx, c[1] + 0.25, c[2]), (0, 0, -55 * sx), color=CYAN, bevel=0.03)
    b.torus(P, 0.4, 0.06, (c[0], c[1], c[2]), (0, 0, 90), color=CYAN, segs=14, rsegs=4)

finish(b, OUT, focus_y=4.6, spacing=8.0)
