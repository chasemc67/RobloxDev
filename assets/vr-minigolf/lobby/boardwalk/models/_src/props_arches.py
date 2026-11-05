"""Arches group: three portal arches, 16 W x 18 H x 4 D, clear opening >= 10 W x 12 H centred at X=0.
Collision: 3 boxes (2 legs + lintel). Portal surface plane is RobloxDevBot's (not modelled)."""
import math, random
from mathutils import Vector
import bwlib as L
from registry import prop, FRONT_SOUTH

HALF_W, OPEN_H = 5.0, 12.0
MARGIN = 0.04
ARCH_COLL = [dict(name="leg_west", center=[-6.5, 9.0, 0.0], size=[3.0, 18.0, 4.0]),
             dict(name="leg_east", center=[6.5, 9.0, 0.0], size=[3.0, 18.0, 4.0]),
             dict(name="lintel", center=[0.0, 14.0, 0.0], size=[10.0, 4.0, 4.0])]


# ----------------------------------------------------------------------------- shared helpers
def catmull(points, n_per=4):
    P = [Vector(p) for p in points]
    P = [P[0] + (P[0] - P[1])] + P + [P[-1] + (P[-1] - P[-2])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n_per):
            t = k / n_per
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2])
    return out


def resample(vals, n):
    """Linearly resample a list of floats to n entries."""
    out = []
    for i in range(n):
        u = i / (n - 1) * (len(vals) - 1)
        a = int(math.floor(u))
        b = min(a + 1, len(vals) - 1)
        out.append(vals[a] + (vals[b] - vals[a]) * (u - a))
    return out


def enforce_envelope(pb, half_x=8.0, half_y=2.0, top=18.0):
    """Safety net: keep every vertex inside the 16x18x4 box and out of the 10x12 opening."""
    for P in pb.parts.values():
        for v in P.verts:
            v.x = max(-half_x, min(half_x, v.x))
            v.y = max(-half_y, min(half_y, v.y))
            v.z = max(0.0, min(top, v.z))
            if abs(v.x) < HALF_W + MARGIN and v.z < OPEN_H + MARGIN:
                dx = HALF_W + MARGIN - abs(v.x)
                dz = OPEN_H + MARGIN - v.z
                if dx <= dz:
                    v.x = math.copysign(HALF_W + MARGIN, v.x if v.x != 0 else 1)
                else:
                    v.z = OPEN_H + MARGIN

    # Whole-face corner guard: a diagonal may cross the rectangle even if vertices do not.
    from pass2_checks import intersects
    for P in pb.parts.values():
        for face in P.faces:
            pts=[P.verts[k] for k in face]
            if intersects(pts,(-4.999,-2.001,.001),(4.999,2.001,11.999)):
                if min(v.z for v in pts)>9.5:
                    for v in pts:v.z=max(v.z,12.04)
                else:
                    sign=1 if sum(v.x for v in pts)>=0 else -1
                    for v in pts:v.x=sign*max(abs(v.x),5.04)


def opening_extras(objs):
    """Measure the clear opening from the final geometry (vertices + edge samples)."""
    half = 99.0
    height = 99.0
    for o in objs:
        me = o.data
        pts = [v.co.copy() for v in me.vertices]
        for e in me.edges:
            a, b = me.vertices[e.vertices[0]].co, me.vertices[e.vertices[1]].co
            for t in (0.25, 0.5, 0.75):
                pts.append(a.lerp(b, t))
        for p in pts:
            if p.z < OPEN_H - 1e-3:
                half = min(half, abs(p.x))
            if abs(p.x) < HALF_W - 1e-3:
                height = min(height, p.z)
    return {"opening_clear": dict(width=round(2 * half, 3), height=round(height, 3), required=[10, 12],
                                  note="clear rectangle centred on X=0 from the deck up, full depth"),
            "portal_plane": dict(center=[0, 6.0, 0], size=[10, 12], note="RobloxDevBot's portal quad goes here"),
            "nameplate_mount": dict(center=[0, 14.0, 2.3], note="builder: nameplate base at Y 14, Z +2.3; arch front "
                                                                 "face at local Z <= +2.0 behind it")}


# ----------------------------------------------------------------------------- Lantern Grove
@prop("bw_arch_lantern_grove", "arches", target=[16, 18, 4], tris_max=15000, front=FRONT_SOUTH, pivot="local",
      collision=ARCH_COLL,
      notes="Gnarled twin-trunk tree arch, chunky autumn leaf blobs (orange/red/yellow atlas cells), 6 hanging "
            "Neon lanterns kept outside the 10x12 opening.")
def lantern_grove(pb):
    rnd = random.Random(8)
    for s in (-1, 1):
        ctrl = [(-6.6, 0.0, 0.0), (-6.5, 0.15, 3.0), (-6.45, -0.1, 6.0), (-6.35, 0.05, 9.0), (-6.25, 0.0, 11.0),
                (-5.9, 0.0, 12.9), (-4.7, 0.0, 14.3), (-2.6, 0.0, 15.25), (-0.2, 0.0, 15.6)]
        pts = [Vector((s * p.x, p.y, p.z)) for p in catmull(ctrl, 4)]
        radii = resample([1.35, 1.15, 1.05, 1.0, 0.97, 0.93, 0.9, 0.86, 0.84], len(pts))
        pb.tube(pts, radii, segs=12, mapping=("trim", "bark", 6.0), smooth=True)
        # twisted secondary strands (gnarl)
        for k, ph0 in enumerate((0.0, math.pi)):
            spts, srad = [], []
            for i, p in enumerate(pts):
                a = pts[max(i - 1, 0)]
                b = pts[min(i + 1, len(pts) - 1)]
                tg = (b - a).normalized()
                nrm = tg.cross(Vector((0, 1, 0))).normalized()
                ph = ph0 + i / len(pts) * math.tau * 1.6 * s
                off = (nrm * math.cos(ph) + Vector((0, 1, 0)) * math.sin(ph)) * radii[i] * 0.62
                spts.append(p + off)
                srad.append(radii[i] * 0.5)
            pb.tube(spts, srad, segs=8, mapping=("trim", "bark", 5.0), smooth=True)
        # root flares
        for dx, dy in ((1.5, 0.0), (0.5, -1.45), (0.4, 1.45), (-0.85, 0.75), (-0.8, -0.8)):
            base = Vector((s * 6.6, 0, 1.6))
            end = Vector((s * (6.6 + dx), dy, 0.18))
            mid = base.lerp(end, 0.55) + Vector((0, 0, -0.35))
            pb.tube(catmull([base, mid, end], 2), resample([0.75, 0.5, 0.22], 5), segs=7,
                    mapping=("trim", "bark", 3.0))
        # branches up into the canopy
        for (bx, by, bz), (ex, ey, ez) in (((-3.6, 0.0, 14.8), (-5.4, 0.9, 16.9)), ((-2.0, 0.0, 15.4),
                                                                                 (-2.6, -0.8, 17.2)),
                                           ((-6.0, 0.0, 12.8), (-7.4, -0.5, 14.6))):
            a, b = Vector((s * bx, by, bz)), Vector((s * ex, ey, ez))
            pb.tube(catmull([a, a.lerp(b, 0.5) + Vector((0, 0, 0.2)), b], 2), resample([0.5, 0.36, 0.25], 5),
                    segs=7, mapping=("trim", "bark", 3.0))
    # leaf blobs: (x, y, z, sx, sy, sz, cell)
    blobs = [(0.0, 0.3, 16.75, 6.4, 3.0, 2.3, "leaf_orange"), (-3.7, -0.2, 16.6, 4.8, 3.0, 2.6, "leaf_red"),
             (3.7, 0.2, 16.6, 4.8, 3.0, 2.6, "leaf_yellow"), (-6.3, 0.1, 15.4, 2.9, 3.0, 2.8, "leaf_orange"),
             (6.3, -0.1, 15.4, 2.9, 3.0, 2.8, "leaf_red"), (-1.6, 1.0, 15.9, 3.6, 2.0, 2.0, "leaf_yellow"),
             (1.9, -0.9, 15.8, 3.2, 2.0, 2.0, "leaf_orange"), (-5.2, -1.0, 17.0, 2.4, 1.8, 1.6, "leaf_yellow"),
             (5.0, 0.9, 17.0, 2.4, 1.8, 1.6, "leaf_orange"), (-7.0, 0.6, 13.9, 1.7, 2.0, 1.6, "leaf_red"),
             (7.0, -0.6, 13.9, 1.7, 2.0, 1.6, "leaf_yellow"), (0.6, 1.2, 17.3, 2.6, 1.4, 1.2, "leaf_red")]
    for i, (x, y, z, sx, sy, sz, cell) in enumerate(blobs):
        pb.blob((sx, sy, sz), loc=(x, y, z), seed=i * 3 + 1, amp=0.11, ico=2, freq=1.3,
                mapping=("fit", cell), smooth=True)
    # Root moss and chunky flowers stay on the legs.
    for side in (-1,1):
        pb.blob((1.5,1.0,0.6),loc=(side*6.5,-1.1,0.4),ico=2,part="backdrop",color="#4F9A43")
        for j in range(3):
            pb.sphere(.3,loc=(side*(6.1+j*.5),-1.3,.8+j*.15),ico=1,part="backdrop",color="#E8C24C")
    enforce_envelope(pb)
    return opening_extras


def _lantern(pb, x, y, ztop, twig, r=0.42, h=1.0):
    pb.cyl(0.15, 0.15, twig, segs=5, loc=(x, y, ztop + twig / 2), mapping=("flat", "rope"))
    pb.cyl(0.18, r * 0.85, 0.28, segs=8, loc=(x, y, ztop - 0.14), mapping=("flat", "bark"), smooth=False)
    zb = ztop - 0.28 - h
    prof = [(r * 0.7, 0.0), (r * 0.95, h * 0.2), (r, h * 0.5), (r * 0.95, h * 0.8), (r * 0.7, h)]
    pb.lathe(prof, segs=8, loc=(x, y, zb), part="neon")
    pb.cyl(r * 0.75, 0.14, 0.25, segs=8, loc=(x, y, zb - 0.125), rot=(180, 0, 0), mapping=("flat", "bark"),
           smooth=False)
    return zb - 0.25


# ----------------------------------------------------------------------------- Sugarloaf Canyon
def _tower(pb, s, seed, band):
    """Chunky tapered sugarloaf tower: squarish faceted sections (concept_arches.png), flat-shaded."""
    segs = 12
    cx = s * 6.5
    zs = [0.0, 1.6, 3.3, 5.0, 6.7, 8.4, 10.1, 11.8, 13.5, 15.0, 16.3, 17.2, 17.75]
    rings = []
    for j, z in enumerate(zs):
        u = z / 17.75
        rx = 1.6 - 0.45 * u ** 1.5
        ry = 1.4 - 0.35 * u ** 1.5
        if z > 16.0:                       # rounded sugarloaf crown
            k = math.sqrt(max(0.0, 1 - ((z - 16.0) / 2.0) ** 2))
            rx, ry = rx * (0.45 + 0.55 * k), ry * (0.45 + 0.55 * k)
        ring = L.superellipse_ring(rx, ry, 3.6, segs, z,
                                   wob=lambda a_, zz, sd=seed: 1 + 0.06 * L.noise.noise(
                                       Vector((math.cos(a_) * 2.0, math.sin(a_) * 2.0, zz * 0.45 + sd))))
        rings.append([Vector((p.x + cx, p.y, p.z)) for p in ring])
    t = L.bmesh.new()
    R = [[t.verts.new(p) for p in r] for r in rings]
    for ra, rb in zip(R, R[1:]):
        for k in range(segs):
            t.faces.new((ra[k], ra[(k + 1) % segs], rb[(k + 1) % segs], rb[k]))
    pv = t.verts.new(Vector((cx, 0, 18.0)))
    for k in range(segs):
        t.faces.new((R[-1][k], R[-1][(k + 1) % segs], pv))
    t.faces.new(list(reversed(R[0])))
    L.bmesh.ops.recalc_face_normals(t, faces=t.faces)
    pb.add(t, band, smooth=False)


@prop("bw_arch_sugarloaf_canyon", "arches", target=[16, 18, 4], tris_max=8000, front=FRONT_SOUTH, pivot="local",
      collision=ARCH_COLL,
      notes="Two chunky tapered sugarloaf towers of banded red sandstone (#D9714A / #F0C9A0 bands follow height via "
            "the atlas sandstone strip), faceted flat-shaded stone, joined by a crenellated block lintel.")
def sugarloaf(pb):
    band = ("hband", "sandstone", 34.0, 0.08)
    for s, seed in ((-1, 3), (1, 7)):
        _tower(pb, s, seed, band)
    # block lintel wall + crenellations
    pb.box_minmax((-5.6, -1.35, 12.2), (5.6, 1.35, 15.3), mapping=band, bevel=0.3, segs=2)
    for i, x in enumerate((-3.4, 0.0, 3.4)):
        pb.box((2.0, 2.3, 1.1), loc=(x, 0.05 * (i - 1), 15.85), rot=(0, 0, 2 * (i - 1)), mapping=band,
               bevel=0.25, segs=2)
    # foot boulders (outside the opening)
    for i, (x, y, sz) in enumerate(((-7.4, -1.6, 1.3), (7.3, 1.5, 1.5), (-7.5, 1.6, 1.0), (7.5, -1.7, 1.1))):
        pb.blob((1.4, 1.2, sz), loc=(x, y, 0.0), seed=20 + i, amp=0.1, ico=2, flat_bottom=0.0,
                mapping=("flat", "sand_red"), smooth=False)
    pb.neon_hex="#F6A6C8"
    for side in (-1,1):
        for j in range(3):
            crystal(pb,(side*(5.8+j*.65),-1.5,15.8),(side*.12,0,1),1.5+j*.2,.38,color="#FFE08A")
    cactus(pb,(-6.6,-1.65,0.1),scale=.75)
    enforce_envelope(pb)
    return opening_extras


# ----------------------------------------------------------------------------- Aurora Archipelago
def crystal(pb, base, direction, length, radius, sides=6, twist=0.0, color=None):
    d = Vector(direction).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    w = d.cross(u).normalized()
    base = Vector(base)
    ring0, ring1 = [], []
    for k in range(sides):
        a = math.tau * k / sides + twist
        off = u * math.cos(a) + w * math.sin(a)
        ring0.append(base + off * radius)
        ring1.append(base + d * (length * 0.74) + off * radius * 0.92)
    apex = base + d * length
    # body (atlas crystal cell)
    verts = ring0 + ring1
    faces = [[k, (k + 1) % sides, sides + (k + 1) % sides, sides + k] for k in range(sides)]
    faces.append(list(reversed(range(sides))))
    pb.custom(verts, faces, part="backdrop",color=color or "#7B5BD6")
    # glowing tip (Neon #9FE6F2)
    tverts = ring1 + [apex]
    tfaces = [[k, (k + 1) % sides, sides] for k in range(sides)]
    pb.custom(tverts, tfaces, part="neon")


@prop("bw_arch_aurora_archipelago", "arches", target=[16, 18, 4], tris_max=10000, front=FRONT_SOUTH, pivot="local",
      collision=ARCH_COLL,
      notes="Stacked purple crystal arch on dark rock feet; crystal tips are a separate BW_Neon mesh in #9FE6F2.")
def aurora(pb):
    pb.neon_hex = L.NEON_CRYSTAL
    rnd = random.Random(21)
    # rock feet
    for s in (-1, 1):
        pb.blob((2.9, 3.7, 2.4), loc=(s * 6.55, 0, 0.0), seed=31 + s, amp=0.1, ico=3, flat_bottom=0.0,
                part="backdrop", color="#3A3550", smooth=True)
        pb.blob((1.6, 1.8, 1.2), loc=(s * 7.3, -1.3, 0.0), seed=41 + s, amp=0.1, ico=2, flat_bottom=0.0,
                mapping=("flat", "stone"), smooth=True)
    # leg crystal bundles
    for s in (-1, 1):
        legs = [((6.4, 0.0), 11.6, 0.95, 0.06), ((7.1, -0.8), 8.6, 0.7, 0.12), ((7.0, 0.9), 9.6, 0.72, 0.1),
                ((5.95, -1.1), 7.2, 0.6, 0.05), ((6.0, 1.15), 6.4, 0.58, 0.07), ((7.45, 0.1), 5.6, 0.5, 0.2)]
        for (x, y), ln, r, lean in legs:
            d = Vector((s * lean, y * 0.06, 1.0))
            crystal(pb, (s * x, y, 0.6), d, ln, r, twist=rnd.uniform(0, 1))
    # arch band: hexagonal tube along an arc, centre (0, 8.5), radius 7.05
    arc = []
    n = 18
    for i in range(n + 1):
        th = math.radians(22 + (158 - 22) * i / n)
        arc.append(Vector((7.05 * math.cos(th), 0, 8.5 + 7.05 * math.sin(th))))
    pb.tube(arc, 0.9, segs=6, part="backdrop",color="#7B5BD6", smooth=False)
    # radial crystals on the arch
    for i in range(13):
        th = math.radians(30 + 120 * i / 12 + rnd.uniform(-3, 3))
        dirv = Vector((math.cos(th), 0, math.sin(th)))
        base_r = 6.9
        lmax = min(7.9 / max(abs(dirv.x), 1e-3) - base_r, 9.4 / max(dirv.z, 1e-3) - base_r)
        ln = min(rnd.uniform(1.8, 2.8), lmax)
        y = rnd.uniform(-0.7, 0.7)
        d = (dirv + Vector((0, y * 0.4, 0))).normalized()
        crystal(pb, (base_r * dirv.x, y, 8.5 + base_r * dirv.z), d, ln, rnd.uniform(0.42, 0.62),
                twist=rnd.uniform(0, 1))
    # a few sideways crystals (front/back) for depth
    for th, yd in ((60, -1), (120, 1), (90, -1), (75, 1), (105, -1)):
        t = math.radians(th)
        b = Vector((7.0 * math.cos(t), 0, 8.5 + 7.0 * math.sin(t)))
        crystal(pb, b, (math.cos(t) * 0.4, yd * 1.0, math.sin(t) * 0.5), 1.6, 0.36, twist=0.3)
    for side in (-1,1):
        for z in (1.5,6.0,12.8):
            pb.blob((2.2,2.8,.6),loc=(side*6.6,0,z),ico=2,part="backdrop",color="#EEF3F7")
        pb.box((2.1,1.5,.3),loc=(side*6.6,-1.1,.2),bevel=.15,part="backdrop",color="#36997A")
    enforce_envelope(pb)
    return opening_extras

# Pass2 separate runtime assets. All coordinates below are Blender X,Y,Z.
def cactus(pb,loc,scale=1):
    x,y,z=loc
    pb.cyl(.4*scale,.35*scale,3*scale,loc=(x,y,z+1.5*scale),part="backdrop",color="#6FBF5A")
    for side in (-1,1):
        pb.tube([(x,y,z+scale),(x+side*.8*scale,y,z+scale),(x+side*.8*scale,y,z+2*scale)],.25*scale,part="backdrop",color="#6FBF5A")
        pb.cyl(.5*scale,.5*scale,.3,loc=(x+side*.8*scale,y,z+2.2*scale),rot=(90,0,0),mapping=("flat","awn_red"))
    pb.cyl(.65*scale,.65*scale,.3,loc=(x,y,z+3.2*scale),rot=(90,0,0),mapping=("flat","awn_cream"))
    pb.torus(.4*scale,.15,loc=(x,y-.18,z+3.2*scale),rot=(90,0,0),mapping=("flat","awn_red"))

def brass_lantern(pb,x,y,z):
    pb.cyl(.15,.15,.6,loc=(x,y,z+.3),mapping=("flat","rope"))
    pb.cyl(.5,.35,.3,loc=(x,y,z-.15),mapping=("flat","brass"))
    pb.cyl(.38,.38,1,loc=(x,y,z-.8),part="neon")
    pb.cyl(.45,.45,.3,loc=(x,y,z-1.45),mapping=("flat","brass"))

for course,budget in (("lantern_grove",15000),("sugarloaf_canyon",8000),("aurora_archipelago",10000)):
    def surface(pb):
        pb.quad([(-5,-1.5,0),(5,-1.5,0),(5,-1.5,12),(-5,-1.5,12)])
        P=pb.parts["atlas"]
        P.uvs=[[(0,0),(1,0),(1,1),(0,1)]]
    prop("bw_portal_surface_"+course,"arches",target=[10,12,0],tris_max=2,front=FRONT_SOUTH,pivot="local",collision=[],notes="Intentional portal quad; exempt from decorative opening/trigger clearance. UV 0-1; runtime animated texture.")(surface)

@prop("bw_portal_apron","arches",target=[12,.1,4],tris_max=100,front=FRONT_SOUTH,pivot="local",collision=[],notes="Place at (0,0,4) in arch-local Roblox axes. Top Y=0, no step; separate floor exempt from envelope and opening volume.")
def apron(pb):
    pb.box((12,4,.1),loc=(0,0,-.05),mapping=("deck","a"))

@prop("bw_arch_aurora_archipelago_snowpuff","arches",target=[3,3,2],tris_max=1500,front=FRONT_SOUTH,pivot="local",collision=[],motion="Arch base pivot; idle body bob <=0.1 studs, no locomotion.",notes="Snowpuff on left leg, all geometry outside opening.")
def snowpuff(pb):
    pb.sphere(1,loc=(-6.5,-.6,1.4),scale=(.85,.7,1.2),ico=2,part="backdrop",color="#3A3550")
    pb.sphere(.7,loc=(-6.5,-1.1,1.3),scale=(.85,.35,1),ico=2,part="backdrop",color="#EEF3F7")
    pb.sphere(.6,loc=(-6.5,-.6,2.4),ico=2,part="backdrop",color="#EEF3F7")
    pb.cyl(.3,0,.6,loc=(-6.5,-1.2,2.3),rot=(90,0,0),part="backdrop",color="#E58A3A")
    for x in (-6.8,-6.2):
        pb.sphere(.15,loc=(x,-1.05,2.55),ico=1,part="backdrop",color="#3A3550")
        pb.box((.4,.7,.3),loc=(x,-.6,.15),bevel=.12,part="backdrop",color="#E58A3A")
    for P in pb.parts.values():
        for v in P.verts:v.y=max(-2,v.y-.65)

# Pass 3: dense toy-scale layered silhouettes; all solid additions >= .3 studs.
def rich_grove(pb):
    lantern_grove(pb)
    rng=random.Random(303)
    for side in (-1,1):
        for j in range(7):
            z=2+j*1.65
            pb.torus(.45,.18,segs=12,rsegs=5,loc=(side*(6.4+.18*math.sin(j)),-1.05,z),rot=(90,0,j*13),mapping=("flat","bark"))
        for j in range(4):
            x=side*(5.8+j*.45)
            pb.blob((1.0,1.2,.85),loc=(x,-.7+j*.35,.4),seed=80+j,ico=2,part="backdrop",color="#4A2F1A",smooth=False)
        # Forks in front of the trunk and a braided knotted lintel.
        for j in range(3):
            pb.tube(catmull([(side*6.8,-.85,7+j),(side*5.9,-1.15,11+j*.5),(side*(3.5-j),-.8,14.7+j*.5)],5),resample([.48,.4,.3],11),segs=9,mapping=("trim","bark",4))
        for j in range(15):
            x=side*rng.uniform(5.65,7.35);z=rng.uniform(.45,2.2)
            pb.blob((.65,.65,.5),loc=(x,rng.uniform(-1.5,-.8),z),seed=100+j,ico=1,part="backdrop",color=('#C9473A','#E58A3A','#E8C24C')[j%3])
    # Many overlapping chunky leaf masses, rather than one smooth crown.
    for j in range(40):
        x=rng.uniform(-7.2,7.2);z=16.1+rng.uniform(-.4,1.1)
        if j<18:x=(-1 if j%2 else 1)*rng.uniform(6,7.3);z=rng.uniform(8.8,16.2)
        pb.blob((rng.uniform(1.6,2.5),rng.uniform(1.2,1.8),rng.uniform(1.2,2.0)),loc=(x,-1.3,z),seed=300+j,amp=.18,ico=2,part="backdrop",color=('#C9473A','#E58A3A','#E8C24C')[j%3],smooth=False)
    enforce_envelope(pb);return opening_extras

def rich_canyon(pb):
    pb.neon_hex='#F6A6C8';rng=random.Random(403)
    for side in (-1,1):
        # Independently chipped courses with offsets and alternating strata.
        for j in range(10):
            z=.85+j*1.68;w=2.7-rng.uniform(0,.55)
            pb.box((w,2.9-rng.uniform(0,.6),1.95),loc=(side*(6.5+rng.uniform(-.12,.12)),0,z),rot=(0,0,rng.uniform(-7,7)),bevel=.3,segs=2,part='backdrop',color='#D9714A' if j%3 else '#F0C9A0')
            pb.box((w,2.65,.45),loc=(side*6.5,.05,z-.6),bevel=.18,segs=2,part='backdrop',color='#F0C9A0' if j%2 else '#D9714A')
        for j in range(5):
            pb.blob((1.3,1.4,.9),loc=(side*(5.7+j*.42),-.8,.45+j%2*.4),seed=480+j,ico=2,part='backdrop',color='#D9714A',smooth=False)
        for height in (.5,7.4,16.8):
            for j in range(5):
                crystal(pb,(side*(5.65+j*.42),-1.55+(j%2)*.15,height),(side*.12,-.06,1),1.15+(j%3)*.45,.32+(j%2)*.15,sides=8,color='#FFE08A' if j%2 else '#F6A6C8')
    pb.box((11.1,2.8,2.2),loc=(0,0,13.5),bevel=.3,segs=2,part='backdrop',color='#D9714A')
    for j in range(7):
        pb.blob((1.7,2.8,1.0),loc=(-4.5+j*1.5,0,14.6),seed=500+j,ico=2,part='backdrop',color='#F0C9A0' if j%2 else '#D9714A',smooth=False)
    cactus(pb,(-6.4,-1.3,.2),scale=1)
    enforce_envelope(pb);return opening_extras

def rich_aurora(pb):
    aurora(pb);rng=random.Random(503)
    for side in (-1,1):
        for j in range(8):
            x=side*rng.uniform(5.65,7.35);y=-1.25;z=.6+(j//4)*1.0
            pb.blob((1.8,2.0,1.5),loc=(x,y,z),seed=600+j,ico=2,part='backdrop',color='#3A3550',smooth=False)
            pb.blob((1.7,1.8,.5),loc=(x,y,z+.6),seed=650+j,ico=2,part='backdrop',color='#EEF3F7',smooth=False)
        for j in range(9):
            z=3+j*1.25
            crystal(pb,(side*(6.2+(j%2)*.7),(-1 if j%2 else 1)*.65,z),(side*.12,0,1),2.2+(j%3)*.45,.55,sides=8,twist=j*.2)
        pb.box((.45,.45,3),loc=(side*6.8,-1.25,4.7),mapping=('flat','post'),bevel=.15,segs=2)
    for j in range(13):
        x=-4.5+j*.75
        pb.blob((1.2,2.4,.8),loc=(x,0,15.3+1.2*(1-abs(x)/5)),seed=700+j,ico=2,part='backdrop',color='#3A3550',smooth=False)
        pb.blob((1.15,2.3,.4),loc=(x,0,15.75+1.2*(1-abs(x)/5)),seed=720+j,ico=2,part='backdrop',color='#EEF3F7')
        pb.cyl(.22,0,.65+(j%3)*.2,segs=6,loc=(x,-1.1,12.65+(j%3)*.15),rot=(180,0,0),part='backdrop',color='#EEF3F7')
    for j in range(9):
        crystal(pb,(-3.6+j*.9,.15,16.0),(0,.05,1),1.3+1.2*(1-abs(j-4)/5),.5,sides=8)
    enforce_envelope(pb);return opening_extras

import registry as _reg
for _p in _reg.PROPS:
    if _p['name'] in ('bw_arch_lantern_grove','bw_arch_sugarloaf_canyon','bw_arch_aurora_archipelago'):
        _p['fn']={'bw_arch_lantern_grove':rich_grove,'bw_arch_sugarloaf_canyon':rich_canyon,'bw_arch_aurora_archipelago':rich_aurora}[_p['name']]
        _p['notes']='Pass3 layered concept-directed portal; fixed base frame and collision, clear opening. Separate hinge-pivot lantern exports.'

LANTERN_ANCHORS={
'lantern_grove':[[-6.5,11.5,1.3],[6.5,11.5,1.3],[-6.5,7.5,1.3],[6.5,7.5,1.3],[-3.5,14.5,1.3],[3.5,14.5,1.3]],
'sugarloaf_canyon':[[-6.5,12.6,1.6],[6.5,12.6,1.6]],
'aurora_archipelago':[[-6.8,6.2,1.25],[6.8,6.2,1.25]]}
for _course,_anchors in LANTERN_ANCHORS.items():
    for _idx,_anchor in enumerate(_anchors,1):
        def _single(pb,c=_course,anchor=_anchor):
            if c=='lantern_grove':_lantern(pb,0,0,-.5,.5,r=.45,h=1)
            else:
                brass_lantern(pb,0,0,-.6)
                for P in pb.parts.values():
                    for v in P.verts:v.y*=.78
            return lambda objs:dict(pivot='cord anchor / swing hinge at local origin',anchor_position_arch_local=anchor,swing_axis=[0,0,1],suggested_motion='Sway +/-3 degrees about local Z; phase offset per lantern; Neon pulse +/-15% at 0.5Hz.')
        prop('bw_arch_'+_course+'_lantern_'+str(_idx).zfill(2),'arches',target=[1,2.3,1],tris_max=1500,front=FRONT_SOUTH,pivot='local',collision=[],motion='Independent hinge sway +/-3deg around local Z',notes='Place origin at anchor_position_arch_local in parent arch frame.')(_single)
