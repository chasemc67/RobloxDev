"""Homework Desk arena props (S04): pencils, crayon, ruler, toy bricks, eraser, desk lamp, book, notebook,
pencil cup and center star. Each prop is one MeshPart (vertex colored). Props meant to be tinted per instance in
Studio (Crayon, Brick*, BookCover, Star) are modeled near-white so MeshPart.Color sets their color.

Run: Blender -b -P make_props.py  ->  ../export/deskprops.fbx (+ _rig.json with sizes, _preview.png)
Coordinates are Roblox studs (x right, y up, -z forward); every prop sits on y = 0, laid out apart from the others.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rca_common import Builder, rgb, reset_scene, finish  # noqa: E402

YELLOW = rgb(250, 196, 40)
YELLOW2 = rgb(236, 170, 28)
WOOD = rgb(232, 196, 148)
GRAPHITE = rgb(58, 60, 70)
METAL = rgb(196, 200, 210)
METAL2 = rgb(150, 156, 168)
PINK = rgb(246, 140, 160)
RED = rgb(224, 64, 58)
RED2 = rgb(178, 40, 40)
BLUE = rgb(48, 110, 214)
WHITE = rgb(246, 246, 246)
TINT_DARK = rgb(206, 206, 206)
TINT_BAND = rgb(132, 132, 132)
RULER = rgb(238, 206, 140)
INK = rgb(64, 48, 36)
PAPER = rgb(250, 246, 234)
LINE = rgb(150, 190, 230)
WARM = rgb(255, 238, 196)
BULB = rgb(255, 226, 150)

reset_scene()
b = Builder("DeskProps")
sizes = {}


def note(name, size, center):
    sizes[name] = {"size": list(size), "center": list(center)}


def pencil(name, length, radius, body, ox, oz):
    """Lying along X, centered at (ox, radius, oz). Eraser at -X, tip at +X."""
    y = radius
    tip_wood, tip_lead, ferrule, eraser = radius * 3.0, radius * 0.9, radius * 1.8, radius * 1.4
    body_len = length - tip_wood - tip_lead - ferrule - eraser
    x0 = ox - length / 2
    xb = x0 + eraser + ferrule
    b.cyl(name, radius, body_len, (xb + body_len / 2, y, oz), (30, 0, -90), color=body, segs=6, bevel=0.12)
    # darker stripe so the hex facets read from far away
    b.cyl(name, radius * 1.01, body_len * 0.06, (xb + body_len * 0.2, y, oz), (30, 0, -90), color=GRAPHITE, segs=6,
          bevel=0)
    xt = xb + body_len
    b.cyl(name, radius * 0.98, tip_wood, (xt + tip_wood / 2, y, oz), (0, 0, -90), color=WOOD, segs=12, bevel=0,
          radius2=radius * 0.3)
    b.cyl(name, radius * 0.3, tip_lead, (xt + tip_wood + tip_lead / 2, y, oz), (0, 0, -90), color=GRAPHITE, segs=10,
          bevel=0, radius2=radius * 0.04)
    xf_ = x0 + eraser
    b.cyl(name, radius * 1.04, ferrule, (xf_ + ferrule / 2, y, oz), (0, 0, -90), color=METAL, segs=14, bevel=0.05)
    for k in (0.25, 0.75):
        b.torus(name, radius * 1.04, radius * 0.07, (xf_ + ferrule * k, y, oz), (0, 0, 90), color=METAL2, segs=14,
                rsegs=4)
    b.cyl(name, radius * 0.96, eraser, (x0 + eraser / 2, y, oz), (0, 0, -90), color=PINK, segs=14,
          bevel=radius * 0.3)
    note(name, (length, radius * 2, radius * 2), (ox, y, oz))


# ---------------------------------------------------------------- pencils (perimeter rails + decor)
pencil("PencilLong", 120, 2.25, YELLOW, 0, 0)
pencil("PencilShort", 38, 1.4, YELLOW, -30, 24)
pencil("PencilRed", 38, 1.4, RED, 20, 24)

# ---------------------------------------------------------------- crayon (tinted), lying along X
CX, CZ, CR, CL = -40, 46, 2.25, 28
y = CR
b.cyl("Crayon", CR, CL - 5, (CX - 2.5, y, CZ), (0, 0, -90), color=WHITE, segs=16, bevel=0.3)
b.cyl("Crayon", CR, 3.6, (CX + CL / 2 - 3.2, y, CZ), (0, 0, -90), color=WHITE, segs=16, bevel=0,
      radius2=CR * 0.45)
b.cyl("Crayon", CR * 0.45, 0.6, (CX + CL / 2 - 1.1, y, CZ), (0, 0, -90), color=WHITE, segs=16, bevel=0.15)
b.cyl("Crayon", CR * 1.05, CL * 0.62, (CX - 3.5, y, CZ), (0, 0, -90), color=TINT_DARK, segs=16, bevel=0)
for dx in (-11.2, -10.2, 3.2, 4.2):
    b.cyl("Crayon", CR * 1.08, 0.4, (CX + dx - 0.5, y, CZ), (0, 0, -90), color=TINT_BAND, segs=16, bevel=0)
note("Crayon", (CL, CR * 2, CR * 2), (CX, y, CZ))

# ---------------------------------------------------------------- ruler on edge, ticks on the +Z face
RL, RH, RT, RZ = 116, 4.5, 1.4, -26
b.box("Ruler", (RL, RH, RT), (0, RH / 2, RZ), color=RULER, bevel=0.25)
for i in range(int(-RL / 2) + 2, int(RL / 2) - 1):
    h = 1.7 if i % 10 == 0 else (1.1 if i % 5 == 0 else 0.6)
    w = 0.22 if i % 10 == 0 else 0.14
    b.box("Ruler", (w, h, 0.08), (i, RH - 0.2 - h / 2, RZ + RT / 2 + 0.02), color=INK, bevel=0)
b.box("Ruler", (RL - 1, 0.12, 0.08), (0, RH - 0.25, RZ + RT / 2 + 0.03), color=INK, bevel=0)
note("Ruler", (RL, RH, RT), (0, RH / 2, RZ))


# ---------------------------------------------------------------- toy bricks (tinted)
def brick(name, nx, nz, ox, oz, h=16 / 3):
    unit = 3.5
    sx, sz = nx * unit, nz * unit
    b.box(name, (sx, h, sz), (ox, h / 2, oz), color=WHITE, bevel=0.22)
    b.box(name, (sx + 0.02, 0.18, sz + 0.02), (ox, 0.25, oz), color=TINT_DARK, bevel=0)
    for i in range(nx):
        for k in range(nz):
            px = ox - sx / 2 + unit * (i + 0.5)
            pz = oz - sz / 2 + unit * (k + 0.5)
            b.cyl(name, 1.05, 0.9, (px, h + 0.45, pz), color=WHITE, segs=14, bevel=0.12)
    note(name, (sx, h + 0.9, sz), (ox, (h + 0.9) / 2, oz))


brick("Brick2x2", 2, 2, 40, -46)
brick("Brick2x4", 4, 2, 60, -46)

# ---------------------------------------------------------------- eraser cover 14 x 5 x 2.5
EX, EZ = -10, -46
b.box("Eraser", (14, 5, 2.5), (EX, 2.5, EZ), color=PINK, bevel=0.6, segs=3)
b.box("Eraser", (8.4, 5.12, 2.62), (EX + 2.2, 2.5, EZ), color=BLUE, bevel=0.12)
b.box("Eraser", (8.45, 0.7, 2.66), (EX + 2.2, 3.4, EZ), color=WHITE, bevel=0.05)
b.box("Eraser", (8.45, 0.3, 2.66), (EX + 2.2, 1.6, EZ), color=WHITE, bevel=0.03)
note("Eraser", (14, 5, 2.5), (EX, 2.5, EZ))

# ---------------------------------------------------------------- desk lamp (reaches toward +X)
LX, LZ = -80, 0
b.cyl("DeskLamp", 7, 1.6, (LX, 0.8, LZ), color=RED, segs=24, bevel=0.5)
b.cyl("DeskLamp", 2.2, 1.6, (LX, 2.2, LZ), color=RED2, segs=16, bevel=0.3)
elbow = (LX + 7, 30, LZ)
head = (LX + 27, 40, LZ)


def rod(a, c, rad, color, spread):
    dx, dy = c[0] - a[0], c[1] - a[1]
    ln = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dx, dy))
    for s in (-spread, spread):
        b.cyl("DeskLamp", rad, ln, ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2, a[2] + s), (0, 0, -ang), color=color,
              segs=10, bevel=0.1)


rod((LX, 2.5, LZ), elbow, 0.55, RED, 0.9)
rod(elbow, head, 0.5, RED, 0.75)
for p in ((LX, 3.0, LZ), elbow, head):
    b.cyl("DeskLamp", 1.3, 3.2, p, (90, 0, 0), color=METAL2, segs=14, bevel=0.2)
# spring between the lower rods
for k in range(10):
    t = 0.15 + k * 0.06
    b.torus("DeskLamp", 0.45, 0.1, (LX + 7 * t, 2.5 + 27.5 * t, LZ), (0, 0, -14), color=METAL, segs=8, rsegs=4)
# shade: thick shell cone opening toward (+0.55, -1); warm inner bands
shade = [(0, 0), (2.4, 0), (3.0, -1.2), (7.6, -9.5), (7.0, -9.5), (2.4, -1.6), (0, -1.6)]
cols = [RED, RED, RED, RED, WARM, WARM, WARM]
tilt = math.degrees(math.atan2(0.55, 1.0))
b.lathe("DeskLamp", shade, (head[0] + 0.8, head[1] - 0.6, LZ), (0, 0, tilt), segs=20, colors=cols)
b.sphere("DeskLamp", 2.1, (head[0] + 0.3, head[1] - 0.2, LZ), color=RED2, segs=(12, 8))
bulb = (head[0] + 0.8 + 3.2 * math.sin(math.radians(tilt)), head[1] - 0.6 - 3.2 * math.cos(math.radians(tilt)), LZ)
b.sphere("DeskLamp", 2.2, bulb, color=BULB, segs=(12, 8), glow=True)
note("DeskLamp", (36, 42, 14), (LX + 13, 21, LZ))
sizes["DeskLamp"]["bulb"] = list(bulb)

# ---------------------------------------------------------------- book (tinted cover + cream pages)
BX, BZ, BW, BH, BD = 40, 30, 26, 5, 34
b.box("BookCover", (BW, 0.7, BD), (BX, BH - 0.35, BZ), color=WHITE, bevel=0.2)
b.box("BookCover", (BW, 0.7, BD), (BX, 0.35, BZ), color=WHITE, bevel=0.2)
b.box("BookCover", (1.6, BH, BD), (BX - BW / 2 + 0.6, BH / 2, BZ), color=WHITE, bevel=0.6, segs=3)
for z in (-BD / 2 + 3, BD / 2 - 3):
    b.box("BookCover", (1.7, BH * 0.9, 0.5), (BX - BW / 2 + 0.6, BH / 2, BZ + z), color=TINT_DARK, bevel=0.1)
b.box("BookPages", (BW - 1.4, BH - 1.2, BD - 1.0), (BX + 0.4, BH / 2, BZ), color=PAPER, bevel=0.12)
note("BookCover", (BW, BH, BD), (BX, BH / 2, BZ))
note("BookPages", (BW - 1.4, BH - 1.2, BD - 1.0), (BX + 0.4, BH / 2, BZ))

# ---------------------------------------------------------------- spiral notebook, spine along -X
NX, NZ, NW, NH, ND = 80, 30, 34, 1.6, 46
b.box("Notebook", (NW, NH - 0.3, ND), (NX, (NH - 0.3) / 2, NZ), color=PAPER, bevel=0.1)
b.box("Notebook", (NW, 0.3, ND), (NX, NH - 0.15, NZ), color=BLUE, bevel=0.1)
b.box("Notebook", (12, 0.06, 6), (NX + 4, NH + 0.02, NZ - 12), color=WHITE, bevel=0)
for i in range(3):
    b.box("Notebook", (9, 0.07, 0.25), (NX + 4, NH + 0.03, NZ - 13.5 + i * 1.5), color=LINE, bevel=0)
for i in range(14):
    z = NZ - ND / 2 + 2.5 + i * (ND - 5) / 13
    b.torus("Notebook", 1.0, 0.16, (NX - NW / 2 + 0.6, NH / 2 + 0.1, z), (90, 0, 0), color=METAL, segs=10,
            rsegs=4)
note("Notebook", (NW + 1, NH + 0.4, ND), (NX, NH / 2, NZ))

# ---------------------------------------------------------------- pencil cup (open top shell)
PX, PZ = 80, -10
cup = [(0, 0.0), (4.6, 0.0), (5.0, 0.4), (5.0, 11.0), (4.4, 11.0), (4.4, 1.0), (0, 1.0)]
b.lathe("PencilCup", cup, (PX, 0, PZ), segs=20, colors=[BLUE, BLUE, BLUE, YELLOW, YELLOW2, YELLOW2])
b.torus("PencilCup", 5.02, 0.35, (PX, 4.0, PZ), color=YELLOW, segs=20, rsegs=6)
b.torus("PencilCup", 5.02, 0.35, (PX, 7.5, PZ), color=RED, segs=20, rsegs=6)
note("PencilCup", (10, 11, 10), (PX, 5.5, PZ))

# ---------------------------------------------------------------- center star (tinted), flat
SX, SZ, SR, SI, ST = -60, -30, 7.0, 2.9, 0.25
inner = []
for k in range(5):
    a = math.radians(90 + 72 * k + 36)
    inner.append((SI * math.cos(a), SI * math.sin(a)))
for k in range(5):
    a = math.radians(90 + 72 * k)
    tip = (SR * math.cos(a), SR * math.sin(a))
    i0, i1 = inner[k - 1], inner[k]
    pts = []
    for (px, pz) in (tip, i0, i1, (0, 0)):
        pts += [(SX + px, 0, SZ - pz), (SX + px, ST, SZ - pz)]
    b.hull("Star", pts, color=WHITE)
note("Star", (SR * 2, ST, SR * 2), (SX, ST / 2, SZ))

if __name__ == "__main__":
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "export")
    b.meta["sizes"] = sizes
    finish(b, outdir, focus_y=-2, spacing=190, views=((180, 65),), size=(1600, 1000))
