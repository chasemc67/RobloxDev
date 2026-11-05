"""Backdrop group: sea stacks + rock arch (vertex colour only, far in the ocean), lantern-tree canopy cluster (NW)."""
import math, random
from mathutils import Vector
import bwlib as L
from registry import prop, FRONT_SOUTH, FRONT_NONE
from props_arches import catmull, resample, _lantern


def _rgb(name):
    import atlas_def as A
    return tuple(c / 255 for c in A.hex_rgb255(A.PAL[name]))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def section_sweep(pb, centres, half_w, half_d, segs, color, n=2.4, seed=0, wob=0.04, caps=(True, True)):
    """Sweep a superellipse section along a centreline lying in the Blender XZ plane.
    half_w = in-plane half width (along the in-plane normal), half_d = half depth (Y)."""
    t = L.bmesh.new()
    rings = []
    for i, c in enumerate(centres):
        a = centres[max(i - 1, 0)]
        b = centres[min(i + 1, len(centres) - 1)]
        tg = (b - a).normalized()
        nrm = Vector((-tg.z, 0.0, tg.x))
        ring = []
        for k in range(segs):
            ang = math.tau * k / segs
            ca, sa = math.cos(ang), math.sin(ang)
            u = math.copysign(abs(ca) ** (2 / n), ca)
            v = math.copysign(abs(sa) ** (2 / n), sa)
            w = 1 + wob * L.noise.noise(Vector((ca * 1.2, sa * 1.2, i * 0.35 + seed)))
            ring.append(t.verts.new(c + nrm * (u * half_w[i] * w) + Vector((0, v * half_d[i] * w, 0))))
        rings.append(ring)
    for ra, rb in zip(rings, rings[1:]):
        for k in range(segs):
            t.faces.new((ra[k], ra[(k + 1) % segs], rb[(k + 1) % segs], rb[k]))
    if caps[0]:
        t.faces.new(list(reversed(rings[0])))
    if caps[1]:
        t.faces.new(rings[-1])
    L.bmesh.ops.recalc_face_normals(t, faces=t.faces)
    pb.add(t, part="backdrop", smooth=True, color=color)


def _rock_colour(z, top):
    z = max(z, 0.0)
    wet, red, light = _rgb("bark"), _rgb("sand_red"), _rgb("sand_light")
    w = math.sin(z * 0.62 + 0.4 * math.sin(z * 0.23))
    band = 1.0 / (1.0 + math.exp(-6.0 * w))            # crisp-but-soft alternating bands
    c = _mix(red, light, 0.1 + 0.75 * band)
    c = _mix(c, light, max(0.0, (z - top * 0.8) / (top * 0.2)) * 0.35)   # sun-bleached crown
    return _mix(wet, c, z / 2.4)


# ----------------------------------------------------------------------------- rock arch (backdrop hero)
@prop("bw_rock_arch", "backdrop", target=[30, 24, 10], tris_max=1200, front=FRONT_SOUTH,
      notes="Backdrop hero: one clean, chunky sandstone arch (clear ~12.6 x 15 opening), smooth superellipse "
            "section swept along an elliptical centreline, warm vertex-colour bands. Base at the waterline.")
def rock_arch(pb):
    n = 28
    cs, hw, hd = [], [], []
    for i in range(n + 1):
        t = math.pi * (1 - i / n)
        x, z = 10.6 * math.cos(t), 19.6 * math.sin(t)
        cs.append(Vector((x, 0, z)))
        s = math.sin(t)
        hw.append(4.35 - 0.2 * s + 0.9 * (1 - s) ** 5)
        hd.append(5.0 - 0.9 * s)
    section_sweep(pb, cs, hw, hd, 16, lambda co: _rock_colour(co.z, 24.0), n=2.6, seed=3, wob=0.035)
    for i, (x, y, sx, sz) in enumerate(((-13.2, -2.8, 3.2, 2.4), (12.8, 3.0, 3.4, 2.6), (-8.6, 3.6, 2.4, 1.6))):
        pb.blob((sx, sx * 0.9, sz), loc=(x, y, 0.0), seed=50 + i, amp=0.08, ico=2, flat_bottom=0.0,
                part="backdrop", color=lambda co: _rock_colour(co.z, 24.0))
    for P in pb.parts.values():
        for v in P.verts:
            v.z = max(0.0, v.z)


# ----------------------------------------------------------------------------- sea stacks
@prop("bw_sea_stacks", "backdrop", target=[30, 22, 12], tris_max=1800, front=FRONT_SOUTH,
      notes="Four simple weathered stacks (grey stone, warm tops), vertex colour only; deliberately plainer than "
            "bw_rock_arch.")
def sea_stacks(pb):
    stacks = [(-11.6, 1.2, 22.0, 3.3, 3.6, 1), (-3.2, -2.0, 14.5, 2.8, 3.1, 2), (5.0, 2.0, 17.5, 3.0, 3.3, 3),
              (12.5, -1.6, 8.5, 2.3, 2.6, 4)]
    stone, light, wet = _rgb("stone"), _rgb("sand_light"), _rgb("bark")

    def col(co, top):
        z = max(co.z, 0.0)
        c = _mix(stone, light, (z / top) ** 1.6 * 0.65 + 0.08 * math.sin(z * 0.8))
        return _mix(wet, c, z / 1.8)

    for (x, y, h, rx, ry, seed) in stacks:
        zs = [h * u for u in (0.0, 0.14, 0.3, 0.46, 0.62, 0.76, 0.87, 0.95, 1.0)]
        cs = [Vector((x + 0.25 * math.sin(z * 0.3 + seed), y, z)) for z in zs]
        taper = [1.08, 1.0, 0.96, 0.93, 0.88, 0.82, 0.7, 0.5, 0.18]
        section_sweep(pb, cs, [rx * k for k in taper], [ry * k for k in taper], 12,
                      lambda co, h=h: col(co, h), n=2.3, seed=seed, wob=0.06, caps=(True, True))
    for i, (x, y, s) in enumerate(((-7.8, 3.0, 2.0), (1.0, 3.4, 1.6), (9.4, 3.0, 1.8))):
        pb.blob((s * 1.4, s, s), loc=(x, y, 0.0), seed=70 + i, amp=0.08, ico=2, flat_bottom=0.0, part="backdrop",
                color=lambda co: col(co, 8.0))
    for P in pb.parts.values():
        for v in P.verts:
            v.z = max(0.0, v.z)


# ----------------------------------------------------------------------------- lantern-tree canopy
@prop("bw_lantern_tree_canopy", "backdrop", target=[24, 16, 20], tris_max=6000, front=FRONT_SOUTH,
      notes="Three chunky autumn lantern trees (trunks included, base at Y 0) with 8 Neon lanterns. Builder places "
            "it at Y 10 (base) which floats it: see README spec question (should be Y 0 / sand).")
def canopy(pb):
    trees = [((-6.0, 2.0), (-5.4, 2.6, 8.2), 1.1), ((5.0, -4.0), (4.4, -4.6, 7.2), 1.0), ((6.4, 5.2), (6.9, 5.8, 9.0), 0.95)]
    for (bx, by), (tx, ty, tz), r in trees:
        a = Vector((bx, by, 0.0))
        b = Vector((tx, ty, tz))
        mid = a.lerp(b, 0.5) + Vector((0.5, -0.3, 0.0))
        pts = catmull([a, a.lerp(mid, 0.5), mid, b], 3)
        pb.tube(pts, resample([r * 1.3, r, r * 0.85, r * 0.7], len(pts)), segs=9, mapping=("trim", "bark", 5.0))
        for dx, dy, dz in ((2.6, 0.8, 2.0), (-2.4, -0.9, 2.4), (0.4, 2.4, 2.8)):
            c = b + Vector((dx, dy, dz))
            pb.tube(catmull([b - Vector((0, 0, 1.0)), b.lerp(c, 0.5) + Vector((0, 0, 0.4)), c], 2),
                    resample([r * 0.6, r * 0.42, r * 0.3], 5), segs=6, mapping=("trim", "bark", 3.0))
        for dx, dy in ((1.0, 0.0), (-0.7, 0.8), (-0.3, -1.0)):
            e = a + Vector((dx * 1.8, dy * 1.8, 0.15))
            pb.tube(catmull([a + Vector((0, 0, 1.4)), a.lerp(e, 0.6) + Vector((0, 0, 0.3)), e], 2),
                    resample([r * 0.8, r * 0.5, r * 0.25], 5), segs=6, mapping=("trim", "bark", 3.0))
    blobs = [(-6.0, 2.2, 11.4, 9.0, 8.0, 5.4, "leaf_orange"), (-8.6, -1.6, 9.6, 5.0, 5.0, 3.8, "leaf_red"),
             (-3.4, 5.4, 12.6, 6.0, 5.6, 4.0, "leaf_yellow"), (5.0, -4.6, 10.0, 8.0, 7.6, 5.0, "leaf_red"),
             (8.6, -7.0, 8.6, 5.0, 4.6, 3.4, "leaf_orange"), (1.8, -7.0, 12.0, 5.0, 4.6, 3.4, "leaf_yellow"),
             (6.6, 6.0, 12.4, 8.0, 7.0, 5.0, "leaf_yellow"), (9.6, 2.8, 10.4, 4.6, 4.6, 3.8, "leaf_orange"),
             (2.8, 7.6, 13.4, 4.6, 3.8, 3.2, "leaf_red")]
    for i, (x, y, z, sx, sy, sz, cell) in enumerate(blobs):
        pb.blob((sx, sy, sz), loc=(x, y, z), seed=80 + i, amp=0.11, ico=3, freq=1.2, mapping=("fit", cell))
    for (x, y, zt) in ((-9.6, -3.4, 8.0), (-2.2, 0.6, 9.0), (-6.4, 6.4, 10.4), (1.6, -3.0, 8.0), (8.8, -8.6, 7.0),
                       (10.2, 0.4, 8.6), (4.4, 2.6, 9.6), (-1.0, 8.0, 11.6)):
        _lantern(pb, x, y, zt, 1.0, r=0.5, h=1.15)
    for P in pb.parts.values():
        for v in P.verts:
            v.x = max(-12.0, min(12.0, v.x))
            v.y = max(-10.0, min(10.0, v.y))
            v.z = max(0.0, min(16.0, v.z))
