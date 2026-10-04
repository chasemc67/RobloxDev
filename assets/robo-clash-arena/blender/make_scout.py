"""SCOUT (concept C01): sleek white/cyan humanoid, dark visor with cyan glow, twin arm blasters,
sticky-mine backpack. Headless:
  Blender -b -P make_scout.py -- [outdir]
Writes scout.fbx, scout_rig.json, scout_preview.png. Roblox coords (see rca_common)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rca_common import Builder, rgb, reset_scene, finish

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv and len(sys.argv) > sys.argv.index("--") + 1 else \
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "export")

WHITE = rgb(242, 245, 250)
CYAN = rgb(30, 175, 230)
DARK = rgb(46, 52, 64)
GREY = rgb(140, 150, 166)
VISOR = rgb(18, 22, 32)
GLOW = rgb(90, 235, 255)

reset_scene()
b = Builder("Scout")

# ---------------------------------------------------------------- rig
b.joint("RootJoint", "Torso", "HumanoidRootPart", (0, 4.6, 0))
b.joint("Neck", "Head", "Torso", (0, 6.25, 0))
b.joint("RShoulder", "GunArm", "Torso", (1.55, 5.85, 0))
b.joint("LShoulder", "BombArm", "Torso", (-1.55, 5.85, 0))
b.joint("RHip", "LegR", "Torso", (0.7, 3.75, 0))
b.joint("LHip", "LegL", "Torso", (-0.7, 3.75, 0))
b.joint("PodJoint", "Pod", "Torso", (0, 5.4, 0.95))
b.attach("GunTip", "GunArm", (1.65, 4.65, -3.0))
b.attach("GunTip2", "BombArm", (-1.65, 4.65, -3.0))
b.attach("BombTip", "BombArm", (-1.65, 5.15, -1.2))
b.attach("PodTip", "Pod", (0, 6.1, 1.5))

# ---------------------------------------------------------------- torso
T = "Torso"
b.box(T, (1.75, 0.75, 1.2), (0, 3.85, 0.05), color=WHITE, bevel=0.22)
b.box(T, (0.8, 0.55, 0.9), (0, 3.5, 0.05), color=DARK, bevel=0.15)
b.cyl(T, 0.55, 0.75, (0, 4.4, 0.05), color=DARK, segs=14)
b.box(T, (1.25, 0.32, 0.25), (0, 4.42, -0.52), color=WHITE, bevel=0.1)
b.box(T, (2.3, 1.5, 1.55), (0, 5.35, 0), color=WHITE, bevel=0.42, segs=3, taper=(1.12, 1.04))
b.box(T, (0.82, 0.62, 0.2), (0.48, 5.55, -0.8), (0, 0, -6), color=CYAN, bevel=0.08, mirror=True)
b.torus(T, 0.34, 0.08, (0, 5.0, -0.8), (90, 0, 0), color=CYAN, segs=16, rsegs=6)
b.sphere(T, 0.27, (0, 5.0, -0.8), color=GLOW, segs=(12, 8), glow=True)
b.box(T, (1.35, 0.3, 1.1), (0, 6.1, 0.02), color=DARK, bevel=0.1)
b.box(T, (0.5, 0.9, 0.35), (1.05, 5.2, 0.55), color=CYAN, bevel=0.1, mirror=True)

# ---------------------------------------------------------------- head
H = "Head"
b.cyl(H, 0.3, 0.45, (0, 6.38, 0.02), color=DARK, segs=12)
b.sphere(H, 1.02, (0, 7.25, 0.05), color=WHITE, scale=(1.0, 0.92, 1.0), segs=(18, 10))
b.sphere(H, 0.9, (0, 7.1, -0.26), color=VISOR, scale=(1.02, 0.6, 0.92), segs=(20, 10))
b.box(H, (1.12, 0.15, 0.12), (0, 7.14, -1.06), (8, 0, 0), color=GLOW, bevel=0.05, glow=True)
b.box(H, (0.34, 0.92, 0.95), (0.96, 7.08, 0.05), color=CYAN, bevel=0.15, mirror=True)
b.sphere(H, 0.26, (1.14, 7.08, 0.05), color=WHITE, scale=(0.5, 1, 1), segs=(12, 8), mirror=True)
b.box(H, (0.28, 0.22, 1.25), (0, 8.08, 0.15), (-8, 0, 0), color=CYAN, bevel=0.09)
EAR = [(-0.42, 0, -0.2), (0.42, 0, -0.2), (-0.42, 0, 0.22), (0.42, 0, 0.22), (0.05, 1.35, 0.0), (0.1, 1.3, 0.06)]
EAR_IN = [(-0.26, 0.12, 0), (0.26, 0.12, 0), (-0.26, 0.12, -0.08), (0.26, 0.12, -0.08), (0.05, 1.0, -0.04)]
b.hull(H, EAR, (0.66, 7.8, 0.1), (0, 0, -28), color=WHITE, bevel=0.06, mirror=True)
b.hull(H, EAR_IN, (0.66, 7.8, -0.12), (0, 0, -28), color=CYAN, bevel=0.03, mirror=True)


# ---------------------------------------------------------------- arms (twin blasters)
def arm(part, mirror_name):
    s = dict(mirror=mirror_name)
    b.sphere(part, 0.62, (1.62, 5.95, 0), color=WHITE, segs=(16, 10), **s)
    b.torus(part, 0.5, 0.09, (1.95, 5.95, 0), (0, 0, 90), color=CYAN, segs=16, rsegs=6, **s)
    b.cyl(part, 0.3, 1.0, (1.65, 5.2, 0), color=DARK, segs=12, **s)
    b.sphere(part, 0.36, (1.65, 4.75, 0), color=GREY, segs=(12, 8), **s)
    # cylindrical blaster housing along -Z with cyan rings, twin dark barrels in front
    b.lathe(part, [(0.0, 0.55), (0.32, 0.55), (0.5, 0.35), (0.55, 0.0), (0.55, -1.2), (0.6, -1.25),
                   (0.6, -1.55), (0.5, -1.62), (0.5, -1.75), (0.0, -1.75)],
            (1.65, 4.65, -0.5), (90, 0, 0), color=WHITE, segs=18, **s)
    b.torus(part, 0.56, 0.08, (1.65, 4.65, -0.25), (90, 0, 0), color=CYAN, segs=18, rsegs=6, **s)
    b.torus(part, 0.6, 0.09, (1.65, 4.65, -1.45), (90, 0, 0), color=CYAN, segs=18, rsegs=6, **s)
    b.box(part, (0.3, 0.2, 1.1), (1.65, 5.2, -0.8), color=CYAN, bevel=0.07, **s)
    for dx in (-0.22, 0.22):
        b.cyl(part, 0.19, 0.8, (1.65 + dx, 4.65, -2.5), (90, 0, 0), color=DARK, segs=12, bevel=0.04, **s)
        b.torus(part, 0.16, 0.05, (1.65 + dx, 4.65, -2.88), (90, 0, 0), color=GLOW, segs=12, rsegs=5, glow=True, **s)


arm("GunArm", "BombArm")

# ---------------------------------------------------------------- legs
def leg(part, mirror_name):
    s = dict(mirror=mirror_name)
    b.sphere(part, 0.38, (0.72, 3.68, 0.02), color=DARK, segs=(12, 8), **s)
    b.box(part, (0.72, 1.2, 0.82), (0.75, 3.0, 0.0), color=WHITE, bevel=0.26, **s)
    b.box(part, (0.3, 0.8, 0.1), (0.75, 3.05, -0.43), color=CYAN, bevel=0.04, **s)
    b.sphere(part, 0.36, (0.78, 2.35, -0.08), color=CYAN, segs=(12, 8), **s)
    b.box(part, (0.78, 1.55, 0.98), (0.8, 1.45, 0.02), color=WHITE, bevel=0.28, taper=(0.86, 0.8), **s)
    b.box(part, (0.36, 0.9, 0.1), (0.8, 1.5, -0.5), color=CYAN, bevel=0.04, **s)
    b.cyl(part, 0.26, 0.3, (0.8, 0.72, 0.02), color=DARK, segs=12, **s)
    b.box(part, (0.98, 0.56, 1.8), (0.8, 0.31, -0.25), color=WHITE, bevel=0.22, **s)
    b.box(part, (1.0, 0.42, 0.48), (0.8, 0.26, -1.0), color=CYAN, bevel=0.14, **s)
    b.box(part, (1.02, 0.14, 1.85), (0.8, 0.07, -0.25), color=DARK, bevel=0.05, **s)
    b.cyl(part, 0.17, 0.2, (0.8, 0.42, 0.66), (90, 0, 0), color=GLOW, segs=10, glow=True, **s)


leg("LegR", "LegL")

# ---------------------------------------------------------------- pod (sticky-mine pack)
P = "Pod"
b.box(P, (1.5, 1.3, 0.72), (0, 5.45, 1.05), color=WHITE, bevel=0.26)
b.box(P, (1.3, 0.28, 0.62), (0, 6.08, 1.05), color=CYAN, bevel=0.1)
for x in (-0.38, 0.38):
    b.cyl(P, 0.33, 0.22, (x, 5.35, 1.46), (90, 0, 0), color=DARK, segs=14, bevel=0.05)
    b.sphere(P, 0.14, (x, 5.35, 1.58), color=GLOW, segs=(10, 6), glow=True)
    b.cyl(P, 0.17, 0.42, (x * 1.15, 4.72, 1.1), color=GREY, segs=10, radius2=0.22)

finish(b, OUT, focus_y=4.3, spacing=8.0)
