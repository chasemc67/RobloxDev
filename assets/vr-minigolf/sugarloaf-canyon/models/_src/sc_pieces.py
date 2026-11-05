"""Sugarloaf Canyon world-piece generators (Blender 4.5, bpy/bmesh). Imported by sc_build.py.

Every builder returns a list of Part builders (PB subclasses with .y0 = world y of the pivot for the strata UVs and
.role). Coordinates are Blender (x east, y north = Roblox -Z, z up), pivot at the piece base centre, front = +Y.
Member placement inside clusters uses Roblox yaw = Blender rotation about +Z by the same angle.
"""
import math, random
import bmesh
from mathutils import Vector, Matrix
import sclib as L
from sclib import PB, M, R, TAU, ledge, band_rows, nz, smooth01, grid_bm

WALL = "Strata"


class Part(PB):
    def __init__(self, name, y0=0.0, role="whole piece"):
        super().__init__(name)
        self.y0 = y0
        self.role = role


def rim_silhouette():
    pb = Part('rim_silhouette', role='low-poly striped silhouette blade, CastShadow off')
    xs = [-32,-24,-12,0,12,24,32]
    tops = [20,24,23,28,25,24,20]
    verts = [(x,0,0) for x in xs] + [(x,0,h) for x,h in zip(xs,tops)]
    faces = [(i,i+1,i+8,i+7) for i in range(6)]
    add_faces_bm(pb, 'Strata', verts, faces)
    return [pb]


def T(x=0, y=0, z=0):
    return Matrix.Translation(Vector((x, y, z)))


def Rz(deg):
    return Matrix.Rotation(math.radians(deg), 4, "Z")


def S(sx, sy, sz):
    return Matrix.Diagonal((sx, sy, sz, 1))


def add_faces_bm(pb, mat, verts, faces, matrix=None, smooth=False, uvs=None):
    t = bmesh.new()
    V = [t.verts.new(Vector(v)) for v in verts]
    F = []
    for f in faces:
        try:
            F.append(t.faces.new([V[i] for i in f]))
        except ValueError:
            pass
    if uvs is not None:
        lay = t.loops.layers.uv.new("UVMap")
        for f, face in zip(F, faces):
            for l, i in zip(f.loops, face):
                l[lay].uv = uvs[i]
    pb.add(mat, t, matrix, smooth)


def beam(pb, mat, a, b, w, h=None, segs=0):
    """Square timber/iron beam from a to b (Blender points), cross-section w x h."""
    a, b = Vector(a), Vector(b)
    d = b - a
    L_ = d.length
    if L_ < 1e-4:
        return
    h = h or w
    q = d.to_track_quat("Z", "Y")
    m = T(*((a + b) / 2)) @ q.to_matrix().to_4x4()
    pb.box(mat, (w, h, L_), matrix=m)


def rod(pb, mat, a, b, r, segs=6):
    a, b = Vector(a), Vector(b)
    d = b - a
    L_ = d.length
    if L_ < 1e-4:
        return
    q = d.to_track_quat("Z", "Y")
    m = T(*((a + b) / 2)) @ q.to_matrix().to_4x4()
    pb.cyl(mat, r, r, L_, segs, matrix=m, smooth=False, caps=False)


def catenary(a, b, sag, n):
    a, b = Vector(a), Vector(b)
    return [a.lerp(b, i / n) - Vector((0, 0, sag * 4 * (i / n) * (1 - i / n))) for i in range(n + 1)]


def rope(pb, a, b, sag, r=0.09, n=8, mat="Rope"):
    pts = catenary(a, b, sag, n)
    pb.tube(mat, pts, r, segs=4, smooth=True, caps=False)


def stripes_cyl(pb, mats, r, z0, z1, n_staves=16, segs_per=1, vertical=True, band=3.0, r_top=None, m=None):
    """Cylinder whose staves (vertical) or bands (horizontal) alternate between materials."""
    r_top = r if r_top is None else r_top
    if vertical:
        for i in range(n_staves):
            a0, a1 = TAU * i / n_staves, TAU * (i + 1) / n_staves
            v = [(r * math.cos(a0), r * math.sin(a0), z0), (r * math.cos(a1), r * math.sin(a1), z0),
                 (r_top * math.cos(a1), r_top * math.sin(a1), z1), (r_top * math.cos(a0), r_top * math.sin(a0), z1)]
            add_faces_bm(pb, mats[i % len(mats)], v, [(0, 1, 2, 3)], matrix=m)
    else:
        n = max(1, int(round((z1 - z0) / band)))
        for k in range(n):
            za, zb = z0 + (z1 - z0) * k / n, z0 + (z1 - z0) * (k + 1) / n
            ra, rb = r + (r_top - r) * k / n, r + (r_top - r) * (k + 1) / n
            pb.cyl(mats[k % len(mats)], ra, rb, zb - za, n_staves, loc=(0, 0, (za + zb) / 2), smooth=True, caps=False,
                   matrix=m)


# ============================================================================= cliff + slot kit
def cliff_panel(name, h, phase, slot=False, w=24.0, seed=0):
    y0 = phase * 6.0
    pb = Part(name, y0=y0, role=f"{'slot wall' if slot else 'cliff'} panel {w:.0f} x {h} (phase {phase})")
    rnd = random.Random(seed * 31 + h * 7 + phase + (100 if slot else 0))
    so = rnd.uniform(0, 50)
    xs = [-w / 2 + w * i / 8 for i in range(9)]
    zs = band_rows(0.0, float(h), y0, per_band=(0.0, 0.6, 0.9))

    def front(x, z):
        edge = smooth01((w / 2 - abs(x)) / 2.5)
        top = smooth01((h - z) / 1.5) if h > 6 else 1.0
        rel = ledge(z + y0, 1.1) + 0.9 * nz(x, so, z, 0.09, seed) + 0.35 * math.sin(x * 0.9 + so)
        return Vector((x, (rel * edge * top) - 0.5 * (1 - edge), z))
    t, V = grid_bm(len(xs), len(zs), lambda i, j: front(xs[i], zs[j]))
    # top lip back into the rock, side flaps
    back = 8.0
    top_row = V[-1]
    tb = [t.verts.new(Vector((v.co.x, -back, h))) for v in top_row]
    for i in range(len(xs) - 1):
        t.faces.new((top_row[i], tb[i], tb[i + 1], top_row[i + 1]))
    for side in (0, -1):
        col = [V[j][side] for j in range(len(zs))]
        bk = [t.verts.new(Vector((c.co.x, -4.0, c.co.z))) for c in col]
        for j in range(len(zs) - 1):
            q = (col[j], col[j + 1], bk[j + 1], bk[j])
            t.faces.new(q if side == -1 else tuple(reversed(q)))
    bmesh.ops.recalc_face_normals(t, faces=t.faces)
    # make sure the front faces +Y
    t.normal_update()
    fy = sum(f.normal.y for f in t.faces if abs(f.normal.z) < 0.5)
    if fy < 0:
        bmesh.ops.reverse_faces(t, faces=t.faces)
    pb.add(WALL, t)
    if slot:
        n = 2 if h <= 24 else 4
        for k in range(n):
            x = rnd.uniform(-8, 8)
            z = rnd.uniform(3, h - 4)
            crystal_cluster(pb, T(x, 0.4, z) @ Rz(0) @ Matrix.Rotation(math.radians(-62), 4, "X"),
                            size=rnd.uniform(2.2, 3.4), seed=seed + k * 13 + h, flat=True)
    return [pb]


# ============================================================================= small scenery
def crystal(pb, m, length, r, mat, core=True):
    prof = [(r * 0.85, 0), (r, length * 0.15), (r * 0.9, length * 0.72), (0, length)]
    pb.lathe(mat, prof, 6, matrix=m, smooth=False)
    if core and length > 1.8:
        pb.lathe("CandyCore", [(r * 0.35, 0), (r * 0.35, length * 0.6), (0, length * 0.75)], 4, matrix=m, smooth=False)


def crystal_cluster(pb, m, size=4.0, seed=0, flat=False, n=None):
    """Rock-candy cluster, base on z=0 of m, growing up (+z). size ~ cluster height."""
    rnd = random.Random(seed)
    n = n or rnd.randint(5, 7)
    for i in range(n):
        a = TAU * i / n + rnd.uniform(-0.4, 0.4)
        tilt = 0 if i == 0 else rnd.uniform(18, 38)
        if flat:
            tilt *= 0.7
        L_ = size * (1.0 if i == 0 else rnd.uniform(0.45, 0.8))
        r = size * rnd.uniform(0.11, 0.16)
        off = 0 if i == 0 else size * 0.14
        mm = m @ T(math.cos(a) * off, math.sin(a) * off, -0.2) @ Rz(math.degrees(a)) @ \
            Matrix.Rotation(math.radians(tilt), 4, "Y") @ Rz(rnd.uniform(0, 60))
        crystal(pb, mm, L_, r, "CandyPink" if (i + seed) % 3 else "CandyAmber", core=(i == 0))
    if not flat:
        pb.rock(WALL, (size * 0.7, size * 0.6, size * 0.3), loc=(0, 0, -0.1), seed=seed, amp=0.25, matrix=m)


def lolli(pb, m, R_, thick=0.35, seed=0):
    """Swirl lollipop disc of radius R_ in the XZ plane (faces +-Y) centred at m's origin; stick down -z."""
    rings, sect = 2, 10
    for side in (1, -1):
        y = side * thick / 2
        for k in range(rings):
            r0, r1 = R_ * k / rings, R_ * (k + 1) / rings
            for i in range(sect):
                tw = k * 0.9
                a0, a1 = TAU * i / sect + tw, TAU * (i + 1) / sect + tw
                v = [(r0 * math.cos(a0), y, r0 * math.sin(a0)), (r1 * math.cos(a0), y, r1 * math.sin(a0)),
                     (r1 * math.cos(a1), y, r1 * math.sin(a1)), (r0 * math.cos(a1), y, r0 * math.sin(a1))]
                f = [(0, 1, 2, 3)] if side < 0 else [(3, 2, 1, 0)]
                add_faces_bm(pb, "Bubblegum" if (i % 2) else "MintWhite", v, f, matrix=m)
    pb.cyl("Bubblegum", R_, R_, thick, sect, matrix=m @ Matrix.Rotation(math.radians(90), 4, "X"), caps=False,
           smooth=True)
    pb.cyl("MintWhite", 0.09 * R_ + 0.05, 0.09 * R_ + 0.05, R_ * 1.4, 5, loc=(0, 0, -R_ - R_ * 0.6), matrix=m,
           smooth=False)


GUMS = ("GumLemon", "GumLime", "GumCherry")


def lollipop_cactus(pb, m, w, h, seed=0):
    """Saguaro with swirl lollipops on the trunk and arm tips, gumball fruit. Base at z=0, height h, width ~w."""
    rnd = random.Random(seed)
    tr = max(0.35, w * 0.13)
    top = h * 0.70
    pb.tube("Cactus", [Vector((0, 0, -0.4)), Vector((0, 0, top * 0.5)), Vector((0, 0, top))], [tr * 1.05, tr, tr * 0.92],
            segs=7, matrix=m, smooth=True, caps=False)
    pb.sphere("Cactus", tr * 0.92, loc=(0, 0, top), segs=7, rings=3, matrix=m)
    tips = [Vector((0, 0, top + tr * 0.6))]
    narm = 2 if seed % 3 else 1
    for k in range(narm):
        side = 1 if k == 0 else -1
        az = rnd.uniform(-25, 25)
        z0 = top * rnd.uniform(0.35, 0.55)
        reach = w * 0.42
        up = rnd.uniform(0.18, 0.3) * h
        pts = [Vector((0, 0, z0)), Vector((side * reach * 0.6, 0, z0 + 0.1)), Vector((side * reach, 0, z0 + up * 0.3)),
               Vector((side * reach, 0, z0 + up))]
        mm = m @ Rz(az)
        pb.tube("Cactus", pts, tr * 0.7, segs=5, matrix=mm, smooth=True, caps=False)
        pb.sphere("Cactus", tr * 0.7, loc=pts[-1], segs=5, rings=3, matrix=mm)
        tips.append(mm.to_3x3() @ (pts[-1] + Vector((0, 0, tr * 0.4))) + mm.translation - m.translation)
        for g in range(2):
            p = pts[1].lerp(pts[2], 0.3 + 0.4 * g) + Vector((0, -tr * 0.7, 0))
            pb.sphere(GUMS[(seed + g + k) % 3], tr * 0.42, loc=p, segs=5, rings=3, matrix=mm)
    # lollipop on the trunk top (largest), smaller on arm tips
    LR = h - top - tr * 0.6
    LR = max(0.8, min(LR * 0.44, w * 0.45))
    for i, tp in enumerate(tips):
        rr = LR if i == 0 else LR * 0.62
        mm = m @ T(tp.x, tp.y, tp.z + rr * 1.15 + 0.15) @ Rz(rnd.uniform(-40, 40))
        lolli(pb, mm, rr, thick=max(0.25, rr * 0.22), seed=seed + i)
        pb.cyl("MintWhite", 0.12, 0.12, rr * 1.2, 5, loc=(0, 0, -rr * 0.6), matrix=mm, smooth=False)


def hoodoo(pb, m, w, h, ybase, seed=0, gum=None):
    """Striped hoodoo spire with a capstone and a gumdrop cap. Base z=0 at WORLD y ybase."""
    rnd = random.Random(seed)
    cap_h = h * 0.12
    stone_h = h * 0.09
    shaft = h - cap_h - stone_h
    prof = []
    for z in band_rows(-1.0, shaft, ybase, per_band=(0.0, 0.55, 0.9)):
        u = max(z, 0) / shaft
        r = w / 2 * (0.66 + 0.22 * (1 - smooth01(u / 0.12)) - 0.30 * smooth01((u - 0.72) / 0.28)
                     + 0.07 * math.sin(u * 9 + seed))
        r = r * (1 + 0.16 * ledge(z + ybase, 1.0)) if z >= 0 else w / 2
        prof.append((r, z))
    pb.lathe(WALL, prof, 10, matrix=m, smooth=False, wobble=0.1, seed=seed)
    rs = w * 0.42
    pb.lathe(WALL, [(w * 0.16, shaft - 0.3), (rs * 0.9, shaft + stone_h * 0.25), (rs, shaft + stone_h * 0.7),
                    (rs * 0.85, shaft + stone_h)], 10, matrix=m, smooth=False, wobble=0.14, seed=seed + 1)
    rs *= 0.92
    gum = gum or GUMS[seed % 3]
    z0 = shaft + stone_h
    cp = [(rs * 0.95, z0 - 0.1), (rs * 0.98, z0 + cap_h * 0.35), (rs * 0.75, z0 + cap_h * 0.75), (rs * 0.35, z0 + cap_h * 0.96),
          (0, z0 + cap_h)]
    pb.lathe(gum, cp, 12, matrix=m, smooth=True)


def gumdrop(pb, m, r, h, mat):
    pb.lathe(mat, [(r, -0.3), (r * 0.98, h * 0.25), (r * 0.8, h * 0.62), (r * 0.42, h * 0.92), (0, h)], 12, matrix=m,
             smooth=True)


def scrub(pb, m, r, seed=0):
    rnd = random.Random(seed)
    for i in range(5):
        a = TAU * i / 5 + rnd.uniform(-0.3, 0.3)
        d = r * rnd.uniform(0.2, 0.55)
        s = r * rnd.uniform(0.45, 0.65)
        pb.rock("Scrub", (s * 1.4, s * 1.4, s * 1.1), loc=(math.cos(a) * d, math.sin(a) * d, -0.1), seed=seed + i,
                amp=0.3, ico=1, matrix=m)


def small_rock(pb, m, r, seed=0):
    pb.rock(WALL, (r * 2, r * 1.6, r * 1.1), loc=(0, 0, -0.2), seed=seed, amp=0.22, ico=2, matrix=m)


SCATTER_FN = {
    "scrub_a": lambda pb, m, s, seed: scrub(pb, m, 1.6 * s, seed),
    "scrub_b": lambda pb, m, s, seed: scrub(pb, m, 1.3 * s, seed + 50),
    "rock_a": lambda pb, m, s, seed: small_rock(pb, m, 1.6 * s, seed),
    "rock_b": lambda pb, m, s, seed: (small_rock(pb, m, 2.3 * s, seed + 3),
                                      small_rock(pb, m @ T(1.8 * s, 0.6 * s, 0), 1.0 * s, seed + 4)),
    "gumdrop_boulder_a": lambda pb, m, s, seed: gumdrop(pb, m, 2.4 * s, 3.4 * s, GUMS[seed % 3]),
    "gumdrop_boulder_b": lambda pb, m, s, seed: (gumdrop(pb, m, 3.0 * s, 4.2 * s, ("GumCherry", "Bubblegum", "GumLime")[seed % 3]),
                                                 gumdrop(pb, m @ T(3.0 * s, -1.2 * s, 0), 1.4 * s, 2.0 * s, GUMS[(seed + 1) % 3])),
}


def variant(name, fn, y0=0.0, role="variant"):
    pb = Part(name, y0=y0, role=role)
    fn(pb)
    return [pb]


def hoodoo_variant(key):
    w, h, seed = {"a": (8, 24, 3), "b": (10, 32, 5), "c": (7, 20, 8), "d": (12, 40, 13)}[key]
    return variant(f"hoodoo_spire_{key}", lambda pb: hoodoo(pb, Matrix.Identity(4), w, h, 150.0, seed,
                                                                "GumCherry GumLime GumLemon Bubblegum".split()[ord(key) - 97]),
                   y0=150.0, role=f"hoodoo {w} x {h} (strata phased for base y 150)")


def crystal_variant(key):
    size, seed = {"a": (4.5, 2), "b": (6.5, 7), "c": (10.0, 11)}[key]
    return variant(f"crystal_cluster_{key}", lambda pb: crystal_cluster(pb, Matrix.Identity(4), size, seed), y0=18.0,
                   role=f"rock-candy cluster ~{size} tall")


def cactus_variant(key):
    w, h, seed = {"a": (4.2, 9.5, 1), "b": (5.0, 12.5, 4), "c": (6.0, 16.0, 6)}[key]
    return variant(f"lollipop_cactus_{key}", lambda pb: lollipop_cactus(pb, Matrix.Identity(4), w, h, seed),
                   role=f"lollipop cactus {w} x {h}")


def scatter_variant(key):
    return variant(key, lambda pb: SCATTER_FN[key](pb, Matrix.Identity(4), 1.0, 5), y0=18.0, role="scatter variant")


def dune_cap(key):
    sx, sz, h = {"a": (24, 16, 5), "b": (32, 18, 6.5)}[key]

    def fn(pb):
        pb.sphere("PowderSugar", 0.5, loc=(0, 0, -h * 0.25), scale=(sx, sz, h * 2.5), segs=16, rings=8)
        pb.sphere("PowderSugar", 0.5, loc=(sx * 0.25, sz * 0.12, -h * 0.3), scale=(sx * 0.55, sz * 0.6, h * 2.0), segs=12,
                  rings=6)
    return variant(f"sugar_dune_cap_{key}", fn, role=f"powdered-sugar dune cap {sx} x {h} x {sz}")


# ============================================================================= clusters (world.json members)
def cluster(name, cl):
    piv = cl["pivot"]
    pb = Part(name, y0=piv[1], role=f"merged {cl['kind']} cluster ({len(cl['members'])} members)")
    for k, mem in enumerate(cl["members"]):
        p = mem["pos"]
        loc = R(p[0] - piv[0], p[1] - piv[1], p[2] - piv[2])
        m = T(*loc) @ Rz(mem.get("yaw", 0.0))
        seed = mem.get('seed', k * 17 + 3)
        kind = cl["kind"]
        if kind == "hoodoo":
            w, h = mem["size"][0], mem["size"][1]
            hoodoo(pb, m, w, h, p[1], seed=seed, gum=("GumCherry", "GumLime", "GumLemon", "Bubblegum")[k % 4])
        elif kind == "crystal":
            crystal_cluster(pb, m, size=mem["size"][1], seed=seed)
        elif kind == "cactus":
            lollipop_cactus(pb, m, mem["size"][0], mem["size"][1], seed=seed)
        elif kind == "scatter":
            SCATTER_FN[mem["variant"]](pb, m, mem.get("scale", 1.0), seed)
    return [pb]


# ============================================================================= hero landmarks
def old_sugarloaf():
    """Rounded shell over terrain h=18+110*sqrt(1-q^4), r72, flattened top. 4 sector parts + summit cactus part."""
    y0 = 18.0
    peak, rad = 110.0, 72.0
    segs = 72

    def rq(y):            # radius of the terrain dome at world y
        t = max(0.0, min(1.0, (y - 18.0) / peak))
        return rad * max(0.0, 1-t*t)**0.25
    zs = [z for z in band_rows(0.0, 109.9, y0, per_band=(0.0, 0.5, 0.85))]
    rows = []
    for z in zs:
        yw = z + y0
        r = rq(yw)
        dr = (rq(yw + 0.5) - rq(yw - 0.5))
        nr, nzv = 1.0, -dr
        ln = math.hypot(nr, nzv)
        nr, nzv = nr / ln, nzv / ln
        rows.append((z, r, nr, nzv))
    parts = []
    for s in range(4):
        pb = Part(f"old_sugarloaf_shell_part{s + 1}", y0=y0, role=f"dome shell sector {s * 90}-{s * 90 + 90} deg")
        t = bmesh.new()
        n_i = segs // 4
        grid = []
        for j, (z, r, nr, nzv) in enumerate(rows):
            row = []
            for i in range(n_i + 1):
                a = TAU * (s * n_i + i) / segs
                rel = 0.6 + ledge(z + y0, 1.3) + 1.1 * nz(math.cos(a) * 9, math.sin(a) * 9, z * 0.08, 1.0, 5)
                if j == 0:
                    rel = -0.6
                rr = r + rel * nr
                row.append(t.verts.new(Vector((rr * math.cos(a), rr * math.sin(a), z + rel * nzv))))
            grid.append(row)
        for j in range(len(grid) - 1):
            for i in range(n_i):
                t.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
        pole = t.verts.new(Vector((0, 0, 110.6)))
        for i in range(n_i):
            t.faces.new((grid[-1][i], grid[-1][i + 1], pole))
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        t.normal_update()
        if sum(f.normal.z for f in t.faces) < 0:
            bmesh.ops.reverse_faces(t, faces=t.faces)
        pb.add(WALL, t)
        parts.append(pb)
    top = Part("old_sugarloaf_shell_part5", y0=y0, role="summit lollipop cactus (24 tall)")
    lollipop_cactus(top, T(0, 0, 109.8), 10.0, 24.0, seed=4)
    parts.append(top)
    return parts


def sunset_arch():
    y0 = 190.4
    pb = Part("sunset_arch", y0=y0, role="natural arch, opening 30 x 34")
    steps = 44
    sections = []
    nsec = 6

    def sec_pts(c, tang, hw, hx, tt):
        n = Vector((0, -tang.z, tang.y)).normalized()      # in-plane normal (YZ), points away from the opening
        if n.dot(Vector((0, c.y, c.z - 0))) < 0:
            n = -n
        pts = []
        # rectangle around: corners (x=+-hx, n=+-hw), walk perimeter
        loop = []
        for k in range(nsec):
            loop.append((hx, -hw + 2 * hw * k / nsec))
        for k in range(nsec):
            loop.append((hx - 2 * hx * k / nsec, hw))
        for k in range(nsec):
            loop.append((-hx, hw - 2 * hw * k / nsec))
        for k in range(nsec):
            loop.append((-hx + 2 * hx * k / nsec, -hw))
        for (x, v) in loop:
            p = Vector((x, 0, 0)) + c + n * v
            out = Vector((x / hx * 0.7, 0, 0)) + n * (v / hw)
            out.normalize()
            rel = ledge(p.z + y0, 0.9) + 0.9 * nz(p.x, p.y, p.z, 0.15, 21) * (1 - 0.5 * tt)
            pts.append(p + out * rel)
        return pts
    for i in range(-2, steps + 3):
        tt = max(0.0, min(1.0, i / steps))
        t = math.pi * tt
        c = Vector((0, -20 * math.cos(t), 40 * math.sin(t)))
        if i < 0:
            c = Vector((0, -20, 1.2 * i))
        elif i > steps:
            c = Vector((0, 20, -1.2 * (i - steps)))
        tang = Vector((0, 20 * math.sin(t), 40 * math.cos(t))).normalized() if 0 <= i <= steps else \
            Vector((0, 0, 1 if i < 0 else -1))
        hw = 5 + 1 * math.sin(t)
        hx = 8 - 2 * math.sin(t)
        sections.append(sec_pts(c, tang, hw, hx, math.sin(t)))
    pb.loft(WALL, sections, smooth=False, caps=True)
    rnd = random.Random(4)
    for k in range(9):
        side = 1 if k % 2 else -1
        pb.rock(WALL, (rnd.uniform(3, 6), rnd.uniform(3, 6), rnd.uniform(2, 4)),
                loc=(rnd.uniform(-6, 6), side * rnd.uniform(21, 23.5), -0.6), seed=k + 40, amp=0.25, ico=1)
    return [pb]


def peppermint_dam():
    y0 = 17.0
    body = Part("peppermint_dam_part1", y0=y0, role="dam body (peppermint bands), spillway notch")
    top = Part("peppermint_dam_part2", y0=y0, role="crest deck, parapets, railings, arched relief, spillway bridge")
    band = 8.0
    deck = 99.0
    lip = 91.0
    hw = 44.0
    # body bands: full width below the lip, two blocks above it
    z = 0.0
    k = 0
    while z < deck - 2.0 - 1e-6:
        z1 = min(z + band, deck - 2.0)
        mat = "PepRed" if k % 2 == 0 else "MintWhite"
        if z1 <= lip:
            body.box(mat, (2 * hw, 8.0, z1 - z), loc=(0, 0, (z + z1) / 2))
        else:
            if z < lip:
                body.box(mat, (2 * hw, 8.0, lip - z), loc=(0, 0, (z + lip) / 2))
            za = max(z, lip)
            for sx in (-1, 1):
                body.box(mat, (hw - 10, 8.0, z1 - za), loc=(sx * (10 + (hw - 10) / 2), 0, (za + z1) / 2))
        z = z1
        k += 1
    # cornice (full 10 thick) under the deck, except the spillway (bridge deck instead)
    for sx in (-1, 1):
        top.box("MintWhite", (hw - 10, 10.0, 2.0), loc=(sx * (10 + (hw - 10) / 2), 0, deck - 1.0))
    top.box("MintWhite", (20.0, 7.2, 1.5), loc=(0, 0, deck - 0.75))          # spillway footbridge deck
    for sx in (-1, 1):                                                         # bridge beams
        top.box("Iron", (20.0, 0.5, 1.2), loc=(0, sx * 3.3, deck - 2.1))
    top.box("MintWhite", (20.0, 9.0, 0.8), loc=(0, 0.5, lip - 0.4))          # spillway lip sill
    # parapets + railings
    for sy in (-1, 1):
        top.box("PepRed", (2 * hw, 1.4, 2.0), loc=(0, sy * 4.3, deck + 1.0))
        for i in range(23):
            x = -hw + 2 + i * (2 * hw - 4) / 22
            top.box("Iron", (0.25, 0.25, 1.5), loc=(x, sy * 4.3, deck + 2.75))
        top.box("Iron", (2 * hw - 2, 0.3, 0.3), loc=(0, sy * 4.3, deck + 3.5))
    # downstream (south = -Y) pilasters + arched relief bays
    pil = [-hw + 1.5, -27.0, -10.5, 10.5, 27.0, hw - 1.5]
    for x in pil:
        top.box("MintWhite", (3.0, 1.0, deck - 2.0), loc=(x, -4.5, (deck - 2.0) / 2))
    for xa, xb in zip(pil, pil[1:]):
        if xa == -10.5:
            continue                                                            # spillway bay is open
        cx, r = (xa + xb) / 2, (xb - xa) / 2 - 1.5
        pts = [Vector((cx + r * math.cos(a), -4.3, 76 + r * 0.9 * math.sin(a))) for a in
               [math.pi * i / 12 for i in range(13)]]
        top.tube("PepRed", pts, 0.7, segs=6, smooth=True)
        top.box("PepRed", (1.4, 0.8, 76.0), loc=(cx - r, -4.3, 38.0))
        top.box("PepRed", (1.4, 0.8, 76.0), loc=(cx + r, -4.3, 38.0))
    # upstream face trim + footing
    top.box("SandBlock", (2 * hw, 10.0, 3.0), loc=(0, 0, -0.5))
    return [body, top]


def intake_tower():
    y0 = 100.0
    pb = Part("intake_tower", y0=y0, role="domed intake tower, base 8 below water")
    stripes_cyl(pb, ("PepRed", "MintWhite"), 6.0, 0.0, 18.0, n_staves=16, vertical=False, band=3.0)
    pb.cyl("MintWhite", 7.0, 7.0, 0.6, 20, loc=(0, 0, 18.3))
    for i in range(16):
        a = TAU * i / 16
        pb.box("Iron", (0.2, 0.2, 1.4), loc=(6.7 * math.cos(a), 6.7 * math.sin(a), 19.3))
    pb.torus("Iron", 6.7, 0.1, 24, 4, loc=(0, 0, 20.0))
    stripes_cyl(pb, ("MintWhite",), 5.0, 18.6, 21.0, n_staves=16, vertical=False, band=3)
    for i in range(6):
        a = TAU * (i + 0.5) / 6
        m = T(5.75 * math.cos(a), 5.75 * math.sin(a), 6.5) @ Rz(math.degrees(a) + 90)
        pb.box("Iron", (2.4, 0.6, 3.0), matrix=m)
        pb.box("Window", (1.6, 0.5, 1.6), matrix=T(5.05 * math.cos(a), 5.05 * math.sin(a), 19.8) @ Rz(math.degrees(a) + 90))
    gores = 12
    for i in range(gores):
        verts = []
        rings = 6
        faces = []
        for j in range(rings + 1):
            u = j / rings
            rr = 5.0 * math.cos(u * math.pi / 2)
            zz = 21.0 + 4.2 * math.sin(u * math.pi / 2)
            for a in (TAU * i / gores, TAU * (i + 1) / gores):
                verts.append((rr * math.cos(a), rr * math.sin(a), zz))
        for j in range(rings):
            faces.append((2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2))
        add_faces_bm(pb, "PepRed" if i % 2 else "MintWhite", verts, faces, smooth=True)
    pb.cyl("Iron", 0.15, 0.15, 1.2, 5, loc=(0, 0, 25.5))
    pb.sphere("GumCherry", 0.45, loc=(0, 0, 25.6), segs=8, rings=5)
    return [pb]


# ============================================================================= buildings
def sign_text(pb, text, size, m, mat="Licorice"):
    b = L.lglib.text_bm(text, size=size, extrude=0.06)
    pb.add(mat, b, m)


def gable_roof(pb, mat, w, d, z0, rise, over=0.6, m=None, ridge_x=True):
    m = m or Matrix.Identity(4)
    hw, hd = w / 2 + over, d / 2 + over
    if ridge_x:
        v = [(-hw, -hd, z0), (hw, -hd, z0), (hw, 0, z0 + rise), (-hw, 0, z0 + rise), (-hw, hd, z0), (hw, hd, z0)]
        f = [(0, 1, 2, 3), (3, 2, 5, 4)]
    else:
        v = [(-hw, -hd, z0), (0, -hd, z0 + rise), (0, hd, z0 + rise), (-hw, hd, z0), (hw, -hd, z0), (hw, hd, z0)]
        f = [(0, 1, 2, 3), (1, 4, 5, 2)]
    add_faces_bm(pb, mat, v, f, matrix=m)
    # thickness: underside copy
    add_faces_bm(pb, mat, [(x, y, z - 0.25) for x, y, z in v], [tuple(reversed(q)) for q in f], matrix=m)
    # gable ends
    if ridge_x:
        for sx in (-1, 1):
            add_faces_bm(pb, "Timber", [(sx * w / 2, -d / 2, z0), (sx * w / 2, d / 2, z0), (sx * w / 2, 0, z0 + rise - 0.2)],
                         [(0, 1, 2) if sx > 0 else (2, 1, 0)], matrix=m)


def ranger_station():
    pb = Part("ranger_station", y0=18.4, role="timber ranger station with lookout cupola")
    W_, D = 12.0, 11.0
    pb.box("SandBlock", (14.0, 18.0, 1.0), loc=(0, 0, 0.0))
    cy = -3.0
    pb.box("Timber", (W_, D, 7.5), loc=(0, cy, 0.5 + 3.75))
    for x in (-3.5, 3.5):
        pb.box("Window", (2.2, 0.2, 1.8), loc=(x, cy + D / 2 + 0.05, 4.5))
        pb.box("MintWhite", (2.6, 0.25, 0.25), loc=(x, cy + D / 2 + 0.1, 5.5))
    pb.box("Licorice", (2.0, 0.2, 3.6), loc=(0, cy + D / 2 + 0.05, 2.3))
    for y in (-6, 0):
        pb.box("Window", (0.2, 2.0, 1.8), loc=(W_ / 2 + 0.05, cy + y + 2.5, 4.5))
        pb.box("Window", (0.2, 2.0, 1.8), loc=(-W_ / 2 - 0.05, cy + y + 2.5, 4.5))
    gable_roof(pb, "PepRed", W_, D, 8.0, 3.2, m=T(0, cy, 0))
    # porch
    pb.box("Timber", (13.0, 5.5, 0.4), loc=(0, cy + D / 2 + 2.75, 0.7))
    for x in (-6.0, -2.0, 2.0, 6.0):
        pb.box("Timber", (0.4, 0.4, 7.0), loc=(x, cy + D / 2 + 5.2, 0.9 + 3.5))
    pb.box("PepRed", (13.6, 6.0, 0.3), loc=(0, cy + D / 2 + 2.9, 8.0), rot=(-8, 0, 0))
    pb.box("Timber", (12.4, 0.3, 0.3), loc=(0, cy + D / 2 + 5.2, 1.9))
    # lookout cupola
    pb.box("Timber", (4.6, 4.6, 0.4), loc=(0, cy, 11.0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            pb.box("Timber", (0.35, 0.35, 2.6), loc=(sx * 2.1, cy + sy * 2.1, 12.5))
    pb.box("Timber", (4.6, 4.6, 0.8), loc=(0, cy, 11.6))
    pb.box("Window", (4.0, 4.0, 1.6), loc=(0, cy, 12.8))
    add_faces_bm(pb, "PepRed", [(-2.8, -2.8, 13.8), (2.8, -2.8, 13.8), (2.8, 2.8, 13.8), (-2.8, 2.8, 13.8), (0, 0, 15.6)],
                 [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)], matrix=T(0, cy, 0))
    # flagpole + peppermint flag
    fx, fy = -6.5, 8.6
    pb.cyl("MintWhite", 0.12, 0.1, 15.6, 6, loc=(fx, fy, 0.4), base_at_zero=True)
    for k in range(4):
        pb.box("PepRed" if k % 2 == 0 else "MintWhite", (0.7, 0.06, 1.8), loc=(fx + 0.35 + 0.7 * k, fy, 14.6))
    sign_text(pb, "RANGER STATION", 0.75, T(0, cy + D / 2 + 5.45, 7.0) @ Matrix.Rotation(math.pi, 4, "Z"))
    pb.box("MintWhite", (9.5, 0.15, 1.2), loc=(0, cy + D / 2 + 5.35, 7.35))
    return [pb]


SHOPS = [("CANDY CO.", 15.0, ("PepRed", "MintWhite"), "stripes"),
         ("SALOON", 17.5, ("Apricot", "Timber"), "step"),
         ("ASSAY", 13.5, ("MintWhite", "Timber"), "flat"),
         ("GENERAL STORE", 18.0, ("Bubblegum", "MintWhite"), "arch"),
         ("TAFFY PULL", 14.0, ("GumLemon", "MintWhite"), "step")]


def junction_town():
    pb = Part("junction_town", y0=17.8, role="row of 5 false-front shops + boardwalk (front = local -Z)")
    total = sum(s[1] for s in SHOPS) + 0.5 * (len(SHOPS) - 1)
    x = -total / 2
    front_y = 7.0
    for i, (name, w, (paint, trim), style) in enumerate(SHOPS):
        cx = x + w / 2
        bh = 8.5 + (i % 2) * 1.5
        pb.box("Timber", (w - 0.4, 21.0, bh), loc=(cx, front_y - 10.5, bh / 2))
        gable_roof(pb, "Timber", w - 0.4, 21.0, bh, 2.2, over=0.3, m=T(cx, front_y - 10.5, 0), ridge_x=False)
        fh = 12.0 + (i % 3) * 0.8
        if style == "stripes":
            n = 7
            for k in range(n):
                pb.box(paint if k % 2 == 0 else trim, (w / n, 0.5, fh), loc=(cx - w / 2 + w / n * (k + 0.5), front_y, fh / 2))
        else:
            pb.box(paint, (w, 0.5, fh), loc=(cx, front_y, fh / 2))
        if style == "step":
            pb.box(paint, (w * 0.5, 0.5, 1.2), loc=(cx, front_y, fh + 0.6))
            pb.box(trim, (w * 0.5 + 0.3, 0.6, 0.25), loc=(cx, front_y, fh + 1.25))
        elif style == "arch":
            pts = [Vector((cx + w * 0.3 * math.cos(a), front_y, fh - 0.4 + 1.4 * math.sin(a))) for a in
                   [math.pi * k / 8 for k in range(9)]]
            pb.tube(trim, pts, 0.3, segs=5)
            pb.box(paint, (w * 0.6, 0.45, 1.0), loc=(cx, front_y, fh + 0.4))
        pb.box(trim, (w + 0.3, 0.7, 0.35), loc=(cx, front_y + 0.1, fh))
        # sign board + lettering
        pb.box("MintWhite" if paint != "MintWhite" else "Apricot", (w * 0.8, 0.3, 2.0), loc=(cx, front_y + 0.35, fh - 2.0))
        sz = min(1.3, w * 0.8 / (0.62 * len(name)))
        sign_text(pb, name, sz, T(cx, front_y + 0.5, fh - 2.6) @ Matrix.Rotation(math.pi, 4, "Z"))
        # door + windows
        pb.box("Window", (2.4, 0.3, 4.2), loc=(cx, front_y + 0.2, 2.6))
        for sx in (-1, 1):
            pb.box("Window", (w * 0.22, 0.3, 2.6), loc=(cx + sx * w * 0.3, front_y + 0.2, 3.8))
            pb.box(trim, (w * 0.22 + 0.5, 0.4, 0.3), loc=(cx + sx * w * 0.3, front_y + 0.25, 5.2))
        # awning (peppermint slats) over the boardwalk, posts
        for k in range(6):
            pb.box("PepRed" if (k + i) % 2 == 0 else "MintWhite", (w / 6, 6.0, 0.25),
                   loc=(cx - w / 2 + w / 6 * (k + 0.5), front_y + 3.6, 8.9), rot=(-10, 0, 0))
        for sx in (-1, 1):
            pb.box("Timber", (0.4, 0.4, 8.6), loc=(cx + sx * (w / 2 - 0.6), front_y + 6.4, 4.4))
        x += w + 0.5
    pb.box("Timber", (total, 8.0, 0.5), loc=(0, front_y + 4.0, 0.25))
    for k in range(int(total // 6) + 1):
        pb.box("Timber", (0.3, 0.3, 1.1), loc=(-total / 2 + k * 6, front_y + 7.7, 1.0))
    pb.box("Timber", (total, 0.25, 0.25), loc=(0, front_y + 7.7, 1.5))
    # candy barrels on the boardwalk
    for k in range(6):
        bx = -total / 2 + 4 + k * (total - 8) / 5
        stripes_cyl(pb, ("PepRed", "MintWhite"), 0.7, 0.5, 1.9, n_staves=8, vertical=True, m=T(bx, front_y + 6.6, 0))
        pb.cyl("Timber", 0.72, 0.72, 0.15, 8, loc=(bx, front_y + 6.6, 1.95), smooth=False)
    return [pb]


def water_tower():
    pb = Part("water_tower", y0=17.7, role="candy-striped water tower")
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam(pb, "Timber", (sx * 3.9, sy * 3.9, -0.3), (sx * 3.0, sy * 3.0, 18.0), 0.6)
    for z0, z1 in ((1.5, 9.5), (9.5, 17.0)):
        for (ax, ay), (bx, by) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
            k0 = 3.9 - 0.9 * z0 / 18
            k1 = 3.9 - 0.9 * z1 / 18
            beam(pb, "Timber", (ax * k0, ay * k0, z0), (bx * k1, by * k1, z1), 0.25)
    pb.cyl("Timber", 4.9, 4.9, 0.5, 16, loc=(0, 0, 18.25), smooth=False)
    stripes_cyl(pb, ("PepRed", "MintWhite"), 4.5, 18.5, 26.5, n_staves=16, vertical=True)
    for z in (19.5, 25.5):
        pb.torus("Iron", 4.55, 0.12, 24, 4, loc=(0, 0, z))
    pb.cyl("PepRed", 4.8, 0.3, 2.8, 16, loc=(0, 0, 26.5 + 1.4), smooth=False)
    pb.sphere("GumCherry", 0.6, loc=(0, 0, 29.4), segs=8, rings=5)
    beam(pb, "Iron", (4.6, 0, 18.5), (4.6, 0, 26.0), 0.15)
    sign_text(pb, "SUGARLOAF", 1.1, T(0, -4.62, 22.0) @ Matrix.Rotation(0, 4, "Z"), mat="MintWhite")
    return [pb]


def mine_head():
    pb = Part("mine_head", y0=18.0, role="candy-striped headframe, sheave wheel, portal mound")
    # rock mound with a timber portal (behind, -Y)
    pb.rock(WALL, (16.0, 10.0, 9.0), loc=(0, -6.0, -1.0), seed=12, amp=0.2, ico=2)
    pb.box("Licorice", (4.8, 1.0, 5.6), loc=(0, -0.9, 2.8))
    for sx in (-1, 1):
        pb.box("Timber", (0.8, 0.8, 6.4), loc=(sx * 2.8, -0.6, 3.2))
    pb.box("Timber", (7.0, 0.9, 0.9), loc=(0, -0.6, 6.6))
    sign_text(pb, "SUGARLOAF MINE", 0.55, T(0, 0.0, 6.4) @ Matrix.Rotation(math.pi, 4, "Z"), mat="MintWhite")
    # headframe: two striped legs + backstays, in front of the portal (+Y)
    hy = 4.5
    H_ = 20.0
    for sx in (-1, 1):
        n = 10
        for k in range(n):
            a = Vector((sx * 3.2 * (1 - 0.35 * k / n), hy, H_ * k / n))
            b = Vector((sx * 3.2 * (1 - 0.35 * (k + 1) / n), hy, H_ * (k + 1) / n))
            beam(pb, "PepRed" if k % 2 == 0 else "MintWhite", a, b, 0.7)
        beam(pb, "Timber", (sx * 3.0, hy + 9.0, -0.3), (sx * 2.2, hy + 0.2, H_ - 1.0), 0.55)
    for z in (6.0, 12.0, 18.0):
        k = z / H_
        beam(pb, "Timber", (-3.2 * (1 - 0.35 * k), hy, z), (3.2 * (1 - 0.35 * k), hy, z), 0.4)
    pb.box("Timber", (5.2, 2.0, 0.6), loc=(0, hy, H_ + 0.3))
    m = T(0, hy, H_ + 2.6) @ Matrix.Rotation(math.radians(90), 4, "Y")
    pb.torus("Iron", 2.0, 0.18, 20, 4, matrix=m)
    for k in range(6):
        a = math.pi * k / 6
        beam(pb, "Iron", (0, hy + 2.0 * math.cos(a), H_ + 2.6 + 2.0 * math.sin(a)),
             (0, hy - 2.0 * math.cos(a), H_ + 2.6 - 2.0 * math.sin(a)), 0.12)
    rope(pb, (0, hy - 1.8, H_ + 2.6), (0, -0.5, 5.0), 0.2, r=0.07, mat="Iron")
    # little ore cart (static) at the portal
    pb.box("Iron", (2.2, 3.0, 1.6), loc=(0, 2.2, 1.3))
    pb.box("GumLemon", (1.9, 2.6, 0.5), loc=(0, 2.2, 2.2))
    for sx in (-1, 1):
        for sy in (-1, 1):
            pb.cyl("Licorice", 0.4, 0.4, 0.25, 8, loc=(sx * 1.2, 2.2 + sy * 1.0, 0.45), rot=(0, 90, 0))
    return [pb]


def gondola_station(raise_=0.0, name="gondola_station"):
    """raise_ = 0: the pass-1 station (top + bottom until pass 5). raise_ > 0 (pass 6, gondola_station_bottom): the same
    station lifted raise_ studs onto a timber/sandstone undercroft with a 10-riser side stair, same footprint centre."""
    pb = Part(name, y0=18.0, role="gondola station: platform, posts, peppermint roof, bull wheel"
              + (f", raised {raise_} on an undercroft with a side stair" if raise_ else ""))
    pb.frame = T(0, 0, raise_)
    pb.box("SandBlock", (16.0, 12.0, 1.0), loc=(0, 0, 0.3))
    pb.box("Timber", (16.0, 0.4, 1.0), loc=(0, -5.8, 1.3))
    for x in (-7.4, 0.0, 7.4):
        for y in (-5.4, 5.4):
            pb.box("Timber", (0.6, 0.6, 9.6), loc=(x, y, 0.8 + 4.8))
    pb.box("Timber", (16.0, 0.6, 0.6), loc=(0, -5.4, 10.2))
    pb.box("Timber", (16.0, 0.6, 0.6), loc=(0, 5.4, 10.2))
    for k in range(8):
        mat = "PepRed" if k % 2 == 0 else "MintWhite"
        x0 = -8.2 + k * 16.4 / 8
        gable_roof(pb, mat, 16.4 / 8, 12.0, 10.5, 3.2, over=0.0, m=T(x0 + 16.4 / 16, 0, 0), ridge_x=True)
    # bull wheel at the open (+Y) end
    pb.torus("Iron", 3.8, 0.25, 28, 5, loc=(0, 2.0, 7.6))
    pb.cyl("Iron", 0.4, 0.4, 2.6, 8, loc=(0, 2.0, 8.6))
    for k in range(6):
        a = math.pi * k / 6
        beam(pb, "Iron", (3.8 * math.cos(a), 2.0 + 3.8 * math.sin(a), 7.6), (-3.8 * math.cos(a), 2.0 - 3.8 * math.sin(a), 7.6), 0.15)
    pb.box("MintWhite", (10.0, 0.3, 1.4), loc=(0, -5.9, 8.6))
    sign_text(pb, "SUNSET GONDOLA", 0.9, T(0, -6.1, 8.15), mat="PepRed")
    # boarding rails (raised variant: the +X rail stops short of the back so the side stair can reach the deck)
    for x in (-7.6, 7.6):
        if raise_ and x > 0:
            pb.box("Timber", (0.25, 7.0, 0.25), loc=(x, 1.5, 4.4))
        else:
            pb.box("Timber", (0.25, 10.0, 0.25), loc=(x, 0, 4.4))
    pb.frame = Matrix.Identity(4)
    if raise_:
        station_undercroft(pb, raise_)
    return [pb]


def station_undercroft(pb, R_):
    """Open timber trestle under the raised deck (deck slab bottom at R_ - 0.2) + a sandstone side stair on +X.
    Blender station-local: +Y = open (cable) end. The ground boarding point (Roblox local (2, -4) = Blender (2, 4)) stays
    clear: no post on the front centre line, >= 4.9 studs headroom under the joists. The stair (10 x 0.8 risers, 1.5
    treads, 5.8 wide) climbs from the front (y 9) to the back corner of the deck (y -6), where the deck is clear of the
    cabin loop (cabins only use y > -1 around the bull wheel)."""
    zt = R_ - 0.2                                        # underside of the deck slab
    posts = [(-7.4, -5.4), (0.0, -5.4), (7.4, -5.4), (-7.4, 5.4), (7.4, 5.4)]
    for x, y in posts:
        pb.box("SandBlock", (1.6, 1.6, 0.9), loc=(x, y, 0.15))
        pb.box("Timber", (0.7, 0.7, zt - 0.6), loc=(x, y, 0.6 + (zt - 0.6) / 2))
        for sx in (-1, 1):                               # brass bolt heads on the iron post caps
            pb.box("Iron", (0.9, 0.9, 0.3), loc=(x, y, zt - 1.0))
            pb.cyl("Brass", 0.12, 0.12, 0.12, 6, loc=(x + sx * 0.38, y - 0.46, zt - 1.0), rot=(90, 0, 0), smooth=False)
    for y in (-5.4, 5.4):
        pb.box("Timber", (16.4, 0.7, 0.8), loc=(0, y, zt - 0.4))
    for x in (-7.4, 0.0, 7.4):
        pb.box("Timber", (0.6, 11.4, 0.6), loc=(x, 0, zt - 0.3))
    # cross bracing: back row and both sides (front stays open for the walk-in)
    for (xa, ya), (xb, yb) in (((-7.4, -5.4), (0.0, -5.4)), ((0.0, -5.4), (7.4, -5.4)), ((-7.4, -5.4), (-7.4, 5.4)),
                               ((7.4, -5.4), (7.4, 5.4))):
        beam(pb, "TimberWeathered", (xa, ya, 0.7), (xb, yb, zt - 0.9), 0.35)
        beam(pb, "TimberWeathered", (xa, ya, zt - 0.9), (xb, yb, 0.7), 0.35)
    # side stair: 10 risers up to the deck top (R_ + 0.8)
    n = int(round((R_ + 0.8) / 0.8))
    cx, w, y0 = 10.9, 5.8, 9.0
    for k in range(n):
        z = (k + 1) * (R_ + 0.8) / n
        ya = y0 - 1.5 * k
        pb.box("SandBlock", (w, 1.5, z + 0.3), loc=(cx, ya - 0.75, (z - 0.3) / 2))
        pb.box("Timber", (w, 0.25, 0.16), loc=(cx, ya - 0.125, z - 0.06))
    top = R_ + 0.8
    for side in (-1, 1):                 # handrails: outer side full flight, inner side stops at riser 7 (deck entry)
        x = cx + side * (w / 2 - 0.2)
        pts = []
        for k in ((0, 3, 6, 9) if side > 0 else (0, 3, 6)):
            yy = y0 - 1.5 * k - 0.75
            zz = (k + 1) * top / n
            pb.box("Timber", (0.3, 0.3, 3.4), loc=(x, yy, zz + 1.7))
            pts.append(Vector((x, yy, zz + 3.3)))
        beam(pb, "Timber", pts[0], pts[-1], 0.25)


def cableway_trestle():
    pb = Part("cableway_trestle", y0=150.0, role="old ore-cableway trestle, crossarm along local X")
    H_ = 28.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam(pb, "Timber", (sx * 2.6, sy * 2.6, -0.4), (sx * 0.8, sy * 0.8, H_), 0.45)
    for z0, z1 in ((0.5, 9.0), (9.0, 18.0), (18.0, 27.0)):
        for sx in (-1, 1):
            k0 = 2.6 - 1.8 * z0 / H_
            k1 = 2.6 - 1.8 * z1 / H_
            beam(pb, "Timber", (sx * k0, -k0, z0), (sx * k1, k1, z1), 0.22)
            beam(pb, "Timber", (-k0, sx * k0, z0), (k1, sx * k1, z1), 0.22)
    pb.box("Timber", (6.0, 0.8, 0.8), loc=(0, 0, H_ + 0.2))
    for sx in (-1, 1):
        m = T(sx * 2.4, 0, H_ + 1.0) @ Matrix.Rotation(math.radians(90), 4, "Y")
        pb.torus("Iron", 0.55, 0.12, 12, 4, matrix=m)
        pb.box("PepRed", (0.6, 0.6, 0.6), loc=(sx * 2.4, 0, H_ + 0.4))
    pb.box("PepRed", (1.4, 0.2, 1.0), loc=(0, -2.0, 6.0))
    return [pb]


# ============================================================================= lifts, bridges, walkways
LIFTS = {}          # filled by sc_build from sc_specs.lift_params(world.json)
SH = 5.6            # shaft half size (posts at +-SH)


def railing_run(pb, a, b, h=3.4, post_step=3.0, rope_mat="Rope", post_mat="Timber", sag=0.18):
    a, b = Vector(a), Vector(b)
    L_ = (b - a).length
    n = max(1, int(round(L_ / post_step)))
    pts = [a.lerp(b, i / n) for i in range(n + 1)]
    for p in pts:
        pb.box(post_mat, (0.3, 0.3, h + 0.2), loc=(p.x, p.y, p.z + h / 2 - 0.1))
    for p0, p1 in zip(pts, pts[1:]):
        for z in (h * 0.5, h * 0.92):
            rope(pb, p0 + Vector((0, 0, z)), p1 + Vector((0, 0, z)), sag, r=0.08, n=4, mat=rope_mat)


def lift_frame(key):
    lp = LIFTS[key]
    rise, D, gang = lp["rise"], lp["D"], lp["gang"]
    pb = Part(f"lift_frame_{key}", y0=0.0, role=f"lift shaft (rise {rise:.0f}) + top gangway to the top point ({D:.1f} away)")
    top = rise + 11.5
    for sx in (-1, 1):
        for sy in (-1, 1):
            pb.box("Iron", (0.6, 0.6, top + 0.5), loc=(sx * SH, sy * SH, (top + 0.5) / 2 - 0.5))
    # side bracing on the +-X faces only, and only between the boarding levels (all faces open 0..9.5 and rise..rise+9.5)
    z = 10.0
    while z < rise - 1.0:
        z1 = min(z + 6.0, rise - 0.5)
        for sx in (-1, 1):
            beam(pb, "Iron", (sx * SH, -SH, z), (sx * SH, SH, z1), 0.22)
            beam(pb, "Iron", (sx * SH, -SH, z1), (sx * SH, SH, z1), 0.25)
        z = z1
    for sx in (-1, 1):
        beam(pb, "Iron", (sx * SH, -SH, 10.0), (sx * SH, SH, 10.0), 0.25)
    for sy in (-1, 1):
        pb.box("PepRed", (2 * SH + 0.6, 0.7, 0.7), loc=(0, sy * SH, top))
    for sx in (-1, 1):
        pb.box("PepRed", (0.7, 2 * SH + 0.6, 0.7), loc=(sx * SH, 0, top))
    m = T(0, 0, top + 1.6) @ Matrix.Rotation(math.radians(90), 4, "Y")
    pb.torus("Iron", 1.5, 0.15, 16, 4, matrix=m)
    pb.box("Iron", (1.0, 3.6, 0.4), loc=(0, 0, top + 0.5))
    pb.box("SandBlock", (2 * SH + 1.0, 2 * SH + 1.0, 0.6), loc=(0, 0, -0.3))
    # top gangway, rotated by `gang` about the shaft axis, from the shaft edge to 1 past the top point
    g = Rz(gang)
    y0g, y1g = 4.2, D + 1.0
    pb.box("Timber", (6.0, y1g - y0g, 0.5), loc=(0, (y0g + y1g) / 2, rise - 0.25), matrix=g)
    rail_end = max(y0g + 3.0, D - BOARD)
    for sx in (-1, 1):
        pb.box("Iron", (0.3, y1g - y0g, 0.8), loc=(sx * 2.9, (y0g + y1g) / 2, rise - 0.9), matrix=g)
        a = g @ Vector((sx * 3.4, SH + 0.8, rise))
        b = g @ Vector((sx * 3.4, rail_end, rise))
        railing_run(pb, a, b, post_mat="Iron", rope_mat="Rope")
    pb.box("MintWhite", (0.2, 3.0, 1.2), loc=(SH + 0.15, 0, 4.0))
    return [pb]


BOARD = 6.0


def lift_cage():
    pb = Part("lift_cage", y0=0.0, role="static lift cage frame (animate +Y by the lift rise)")
    pb.box("Timber", (7.6, 7.6, 0.35), loc=(0, 0, -0.18))
    pb.box("Iron", (8.0, 8.0, 0.3), loc=(0, 0, -0.5))
    for sx in (-1, 1):
        for sy in (-1, 1):
            pb.box("Iron", (0.35, 0.35, 9.8), loc=(sx * 3.9, sy * 3.9, 4.6))
    for sx in (-1, 1):
        for z in (1.2, 2.4, 3.5):
            pb.box("Iron" if z < 3 else "PepRed", (0.2, 7.8, 0.2), loc=(sx * 3.9, 0, z))
        for k in range(5):
            pb.box("Iron", (0.12, 0.12, 3.5), loc=(sx * 3.9, -3.0 + 1.5 * k, 1.75))
    for sx in (-1, 1):
        pb.box("Iron", (0.3, 8.1, 0.3), loc=(sx * 3.9, 0, 9.5))
        pb.box("Iron", (8.1, 0.3, 0.3), loc=(0, sx * 3.9, 9.5))
    beam(pb, "Iron", (-3.9, -3.9, 9.5), (3.9, 3.9, 9.5), 0.2)
    beam(pb, "Iron", (3.9, -3.9, 9.5), (-3.9, 3.9, 9.5), 0.2)
    pb.box("Iron", (0.8, 0.8, 0.8), loc=(0, 0, 9.9))
    return [pb]


def ranger_footbridge():
    pb = Part("ranger_footbridge", y0=18.0, role="timber plank footbridge 54 x 6 with rope railings, deck top = 0")
    Lh = 27.0
    pb.box("Timber", (6.0, 2 * Lh, 0.45), loc=(0, 0, -0.225))
    for sx in (-1, 1):
        pb.box("Timber", (0.5, 2 * Lh, 1.1), loc=(sx * 2.6, 0, -1.0))
        railing_run(pb, (sx * 3.4, -Lh, 0), (sx * 3.4, Lh, 0), h=3.5, post_step=4.5)
    for yb in (-9.0, 9.0):                                    # trestle bents into the river bed
        for sx in (-1, 1):
            beam(pb, "Timber", (sx * 2.6, yb, -1.5), (sx * 3.2, yb, -7.5), 0.6)
        beam(pb, "Timber", (-2.6, yb, -1.6), (2.6, yb, -1.6), 0.4)
        beam(pb, "Timber", (-2.9, yb, -2.0), (3.1, yb, -6.5), 0.25)
    for sy in (-1, 1):
        for sx in (-1, 1):
            pb.box("Timber", (0.7, 0.7, 4.6), loc=(sx * 3.75, sy * (Lh - 0.4), 2.0))
            pb.sphere("GumCherry", 0.35, loc=(sx * 3.75, sy * (Lh - 0.4), 4.5), segs=8, rings=5)
    return [pb]


def licorice_rope_bridge():
    pb = Part("licorice_rope_bridge", y0=70.0, role="suspension rope bridge 54 x 6, licorice ropes, deck top = 0")
    Lh = 27.0
    n = 36
    for i in range(n):
        y = -Lh + (i + 0.5) * 2 * Lh / n
        pb.box("Timber", (6.0, 2 * Lh / n - 0.12, 0.4), loc=(0, y, -0.2))
    for sx in (-1, 1):
        pb.box("Licorice", (0.35, 2 * Lh, 0.35), loc=(sx * 2.7, 0, -0.55))
        pb.box("Licorice", (0.3, 2 * Lh, 0.3), loc=(sx * 3.1, 0, -0.2))
        pts = catenary((sx * 3.3, -Lh, 4.8), (sx * 3.3, Lh, 4.8), 1.6, 18)
        pb.tube("PepRed", pts, 0.14, segs=5, caps=False)
        pts2 = catenary((sx * 3.3, -Lh, 2.4), (sx * 3.3, Lh, 2.4), 0.6, 18)
        pb.tube("Licorice", pts2, 0.1, segs=4, caps=False)
        for k in range(1, 18):
            p = pts[k]
            rod(pb, "Licorice", (p.x, p.y, -0.2), (p.x, p.y, p.z), 0.05, segs=4)
    for sy in (-1, 1):
        for sx in (-1, 1):
            pb.box("Timber", (0.8, 0.8, 10.5), loc=(sx * 3.6, sy * (Lh + 0.4), 4.75))
            beam(pb, "Licorice", (sx * 3.6, sy * (Lh + 0.4), 9.0), (sx * 7.5, sy * (Lh + 2.2), -0.5), 0.12)
        pb.box("Timber", (8.0, 0.7, 0.7), loc=(0, sy * (Lh + 0.4), 9.6))
        pb.box("MintWhite", (6.4, 0.3, 1.4), loc=(0, sy * (Lh + 0.4), 10.6))
        sign_text(pb, "LICORICE BRIDGE", 0.62, T(0, sy * (Lh + 0.6), 10.2) @ Rz(0 if sy < 0 else 180), mat="PepRed")
    return [pb]


def walk_boardwalk(w=6.0, length=12.0):
    pb = Part(f"walk_boardwalk_{int(w)}x{int(length)}", y0=18.0, role=f"timber boardwalk {w} x {length}, top = 0")
    n = int(length / 1.0)
    for i in range(n):
        pb.box("Timber", (w, 0.9, 0.4), loc=(0, -length / 2 + (i + 0.5) * length / n, -0.2))
    for sx in (-1, 1):
        pb.box("Timber", (0.4, length, 0.6), loc=(sx * (w / 2 - 0.2), 0, -0.5))
    return [pb]


def stair_flight(steps=5, rise=0.8, tread=1.5, w=5.8):
    pb = Part(f"stair_flight_{steps}", y0=18.0, role=f"{steps} steps x {rise} rise x {tread} tread, {w} wide; climbs local -Z")
    for i in range(steps):
        top = (i + 1) * rise
        pb.box("SandBlock", (w, tread, top + 0.6), loc=(0, (i + 0.5) * tread, (top - 0.6) / 2))
        pb.box("Timber", (w, 0.3, 0.2), loc=(0, i * tread + 0.15, top - 0.1))
    for sx in (-1, 1):
        add_faces_bm(pb, "SandBlock", [(sx * w / 2, 0, -0.6), (sx * w / 2, steps * tread, -0.6),
                                       (sx * w / 2, steps * tread, steps * rise), (sx * w / 2, 0, rise)],
                     [(0, 1, 2, 3) if sx > 0 else (3, 2, 1, 0)])
    return [pb]


def landing():
    pb = Part("landing_6x4", y0=18.0, role="sandstone landing 5.8 wide x 4 long, top = 0")
    pb.box("SandBlock", (5.8, 4.0, 0.7), loc=(0, 0, -0.35))
    return [pb]


def railing_12():
    pb = Part("railing_12", y0=18.0, role="railing 12 long (local Z), timber posts + rope rails, 3.4 tall")
    railing_run(pb, (0, -6.0, 0), (0, 6.0, 0), h=3.4, post_step=4.0)
    pb.box("Timber", (0.3, 12.0, 0.25), loc=(0, 0, 3.45))
    return [pb]


# ============================================================================= far cards + sky
def bent_card(pb, mat, w, h, nseg, bend, z0=0.0, centre=False):
    verts, faces, uvs = [], [], []
    for i in range(nseg + 1):
        u = i / nseg
        x = -w / 2 + w * u
        y = bend * (2 * u - 1) ** 2
        for k in (0, 1):
            verts.append((x, y, z0 + (h * k) - (h / 2 if centre else 0)))
            uvs.append((u, float(k)))
    for i in range(nseg):
        a = 2 * i
        faces.append((a, a + 1, a + 3, a + 2))          # normal toward +Y (front)
    add_faces_bm(pb, mat, verts, faces, uvs=uvs)


def card_piece(name, mat, w, h, nseg, bend, role):
    pb = Part(name, role=role)
    bent_card(pb, mat, w, h, nseg, bend, z0=-2.0)
    return [pb]


def sun_disc():
    pb = Part("sun_disc", role="sun disc card 260 x 260, pivot = centre")
    bent_card(pb, "SunGold", 260.0, 260.0, 1, 0.0, centre=True)
    return [pb]


def cloud_streak():
    pb = Part("cloud_streak", role="cloud streak card 700 x 70, pivot = centre")
    bent_card(pb, "CardCloud", 700.0, 70.0, 3, 40.0, centre=True)
    return [pb]


BALLOONS = {"a": ("PepRed", "MintWhite"), "b": ("Bubblegum", "MintWhite"), "c": ("GumLemon", "GumLime")}


def balloon(key):
    ma, mb = BALLOONS[key]
    pb = Part(f"balloon_{key}", role="candy-striped hot-air balloon 24 x 30 x 24, pivot = basket bottom")
    gores = 12
    prof = [(1.2, 8.0), (3.8, 10.0), (8.5, 14.0), (11.4, 19.0), (12.0, 23.0), (10.6, 27.0), (6.6, 29.4), (0.0, 30.0)]
    for i in range(gores):
        verts, faces = [], []
        for j, (r, z) in enumerate(prof):
            for a in (TAU * i / gores, TAU * (i + 1) / gores):
                verts.append((r * math.cos(a), r * math.sin(a), z))
        for j in range(len(prof) - 1):
            faces.append((2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2))
        add_faces_bm(pb, ma if i % 2 else mb, verts, faces, smooth=True)
    pb.box("Timber", (2.4, 2.4, 2.0), loc=(0, 0, 1.0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            rod(pb, "Rope", (sx * 1.1, sy * 1.1, 2.0), (sx * 1.0, sy * 1.0, 8.0), 0.06, segs=4)
    pb.cyl("Iron", 0.5, 0.5, 0.8, 8, loc=(0, 0, 6.0))
    return [pb]
