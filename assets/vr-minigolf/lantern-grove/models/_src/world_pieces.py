"""Pass 3: world-scale background pieces for the continuous Lantern Grove world (world/world.json).

Every piece is built in its own local frame (1 unit = 1 stud, Blender Z-up, same FBX axes as the props), with the
origin at the piece's world.json `pos` (base centre) unless the piece says otherwise. Roblox placement:
    Model:PivotTo(CFrame.new(pos) * CFrame.Angles(0, math.rad(yaw), 0))
Large pieces are split into several FBX parts (< 20k tris each) that all share the same origin.

Registry: WPIECES (list of dicts). build(ctx) returns [(part_suffix, WPB), ...]; a WPB may carry .post (callable
(root, objs) run after finalize, e.g. booleans). Placement data (instances) comes from world_layout.py.
"""
import math, random
import bmesh
import numpy as np
from mathutils import Vector, Matrix, noise
import lglib
from lglib import M, TAU
import world_fit as WF

# ----------------------------------------------------------------------------- world-only materials
lglib.MATS.update({
    "Heartwood": ("#B9783F", "Wood", 0, 0, "warm heartwood interior of the hero tree (world pass)"),
    # pass 4 (art director): hazy peach + mauve with snowcaps, the foot fading into the horizon sky colour
    "MountainFoot": ("#EDC6A8", "SmoothPlastic", 0, 0, "mountain foot, = horizon sky haze (fades into the sky)"),
    "MountainPeach": ("#D8A38E", "SmoothPlastic", 0, 0, "mountain lower slopes, hazy peach"),
    "MountainMauve": ("#AE8890", "SmoothPlastic", 0, 0, "mountain upper slopes / ridges, dusty mauve"),
    "MountainSnow": ("#F8EDE6", "SmoothPlastic", 0, 0, "snowcaps (warm white, sunset tinted)"),
    "SkyPaper": ("#F6A04A", "SmoothPlastic", 0.7, 0, "sky lantern paper: glowing washi texture (paper_glow.png)"),
    "Cloud": ("#FFE6BE", "SmoothPlastic", 0.35, 0, "golden cumulus card, sunlit tops"),
    "CloudShade": ("#E9B7A4", "SmoothPlastic", 0.2, 0, "cumulus underside (peach shade)"),
    "Mist": ("#F3F7F8", "SmoothPlastic", 0, 0.45, "waterfall mist puffs"),
})
lglib.TEX["Heartwood"] = ("heartwood", 4.0)
lglib.TEX["SkyPaper"] = ("paper_glow", 1.3)
lglib.EMIT_TEX.add("SkyPaper")

WORLD = WF.load_world()
TREE = WORLD["hollow_tree"]
T_O = np.array(TREE["center"], float)            # trunk base centre, world (Roblox)
R_OUT, R_IN = TREE["trunk_outer_radius"], TREE["trunk_inner_radius"]
T_H, HOLLOW_H = TREE["trunk_height"], TREE["hollow_height"]
OCULUS_R = TREE["oculus"]["radius"]
FLARE_R = TREE["root_flare_radius"]
DOOR = TREE["doorway"]
DOOR_A = -math.radians(DOOR["angle_deg"])        # Blender angle (Blender +Y = Roblox -Z)
DOOR_W, DOOR_H = DOOR["width"], DOOR["height"]


class WPB(lglib.PB):
    """PB with a texture tile multiplier (world pieces are 5-50x prop size; tile_scale keeps texel density sane)."""

    def __init__(self, name, tile_scale=1.0):
        super().__init__(name)
        self.tile_scale = tile_scale
        self.post = None

    def finalize(self, collection, smooth_angle=40.0):
        old = lglib.TEX
        lglib.TEX = {k: (v[0], v[1] * self.tile_scale) for k, v in old.items()}
        try:
            return super().finalize(collection, smooth_angle)
        finally:
            lglib.TEX = old


def blw(p_bl, origin=T_O):
    """Blender-local point of a piece at world origin (yaw 0) -> Roblox world."""
    return np.array([origin[0] + p_bl[0], origin[1] + p_bl[2], origin[2] - p_bl[1]])


def wbl(p_w, origin=T_O):
    return Vector((p_w[0] - origin[0], -(p_w[2] - origin[2]), p_w[1] - origin[1]))


def pol(a, r, z=0.0):
    return Vector((math.cos(a) * r, math.sin(a) * r, z))


def all_bms(pbs):
    for pb in pbs:
        for b in pb.bms.values():
            yield b


def bms_bbox(pbs):
    mn = Vector((1e9, 1e9, 1e9))
    mx = -mn
    for b in all_bms(pbs):
        for v in b.verts:
            mn = Vector(map(min, mn, v.co))
            mx = Vector(map(max, mx, v.co))
    return mn, mx


def fit_bms(pbs, size_xyz_roblox, base_z=0.0):
    """Scale every PB about the vertical axis so the bbox is size (Roblox x, y, z), base kept at base_z,
    and centre the xz footprint on the origin."""
    mn, mx = bms_bbox(pbs)
    sx = size_xyz_roblox[0] / (mx.x - mn.x)
    sy = size_xyz_roblox[2] / (mx.y - mn.y)
    sz = size_xyz_roblox[1] / (mx.z - mn.z)
    c = (mn + mx) / 2
    for b in all_bms(pbs):
        for v in b.verts:
            v.co = Vector(((v.co.x - c.x) * sx, (v.co.y - c.y) * sy, base_z + (v.co.z - mn.z) * sz))
    return (sx, sz, sy)


def merge_into(dst, src, remap=None, matrix=None):
    """Append all geometry of PB src into PB dst (material remap dict, optional Blender matrix)."""
    me = lglib._scratch_mesh()
    for mat, b in src.bms.items():
        if matrix is not None:
            bmesh.ops.transform(b, matrix=matrix, verts=b.verts)
        b.to_mesh(me)
        dst.bm((remap or {}).get(mat, mat)).from_mesh(me)
        b.free()
    src.bms = {}


# ----------------------------------------------------------------------------- generic surfaces of revolution
def revolve_bm(profile, segs, disp=None, closed=False, mat_of_seg=None, phase=0.0):
    """profile: list of (r, z, kind). r <= 0 -> pole. disp(a, z, kind, r) -> (r', z').
    closed=True joins the last profile point back to the first (solid ring like the trunk shell).
    mat_of_seg(i) -> material index for the band between profile i and i+1. Returns a bmesh."""
    t = bmesh.new()
    rings = []
    for (r, z, kind) in profile:
        if r <= 1e-6:
            rings.append([t.verts.new((0, 0, z))])
            continue
        ring = []
        for k in range(segs):
            a = TAU * k / segs + phase
            rr, zz = disp(a, z, kind, r) if disp else (r, z)
            ring.append(t.verts.new((rr * math.cos(a), rr * math.sin(a), zz)))
        rings.append(ring)
    n = len(rings)
    pairs = list(zip(range(n), range(1, n))) + ([(n - 1, 0)] if closed else [])
    for i, j in pairs:
        A, B = rings[i], rings[j]
        mi = mat_of_seg(i) if mat_of_seg else 0
        if len(A) == 1 and len(B) == 1:
            continue
        if len(A) == 1:
            fs = [t.faces.new((A[0], B[k], B[(k + 1) % segs])) for k in range(segs)]
        elif len(B) == 1:
            fs = [t.faces.new((A[k], B[0], A[(k + 1) % segs])) for k in range(segs)]
        else:
            fs = [t.faces.new((A[k], A[(k + 1) % segs], B[(k + 1) % segs], B[k])) for k in range(segs)]
        for f in fs:
            f.material_index = mi
    if not closed:
        if len(rings[0]) > 1:
            t.faces.new(list(reversed(rings[0])))
        if len(rings[-1]) > 1:
            t.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(t, faces=t.faces)
    return t


def bark_disp(seed, furrows=18, lump=0.03, furrow=0.022, twist=0.004, buttress=0.0):
    """Outer bark: big lumps + vertical furrows (slight spiral). Inner/dome: outward-only, small."""
    off = Vector((seed * 1.3, seed * 2.1, seed * 0.7))

    def f(a, z, kind, r):
        aa = a + z * twist
        n1 = noise.noise(Vector((math.cos(a) * 1.7, math.sin(a) * 1.7, z * 0.022)) + off)
        n2 = noise.noise(Vector((math.cos(aa) * 3.0, math.sin(aa) * 3.0, z * 0.05)) + off * 2)
        rid = abs(math.sin(furrows * aa + 1.6 * n2))
        rid = 1 - rid ** 0.45            # 1 in the furrow, 0 on the plate
        if kind == "o":
            sw = ((math.degrees(-a) + 180) % 360) - 180     # signed world map angle
            hug = max(0.0, min(1.0, (12 - z) / 6)) * max(0.0, min(1.0, min(sw + 8, 50 - sw) / 8))
            if hug > 0:
                rr = r * (1 + lump * n1 * 2 - furrow * rid)
                return min(rr, (R_OUT - 1.2) * hug + rr * (1 - hug)), z
            base_boost = 0.05 * max(0.0, 1 - max(z, 0) / 10.0) * (0.6 + 0.4 * math.sin(7 * a + 1.3 * n1))
            if z < 36 and buttress:
                door_fade = min(1.0, max(0.0, (math.degrees(ang_dist(a, DOOR_A)) - 14) / 10))
                b = max(0.0, math.cos(7 * (a - DOOR_A) + 0.6 * n1)) ** 3
                base_boost += buttress * (1 - max(z, 0) / 36) ** 1.6 * b * door_fade
            return r * (1 + lump * n1 * 2 - furrow * rid + base_boost), z
        if kind == "c":   # top cap: lumpy in height
            return r * (1 + 0.02 * n2), z + 1.4 * n1
        if kind in ("i", "d"):
            return r * (1 + 0.010 + 0.010 * n1 + 0.012 * (1 - rid)), z
        return r, z
    return f


# ============================================================================ HERO: hollow tree world shell
def shell_profile():
    """(r, z, kind) closed loop around the wall cross-section: outer up, over the top cap, down the oculus shaft,
    under the dome, down the inner wall, back out under the ground. o=outer c=cap s=shaft d=dome i=inner b=bottom"""
    P = []
    for r, z in ((R_OUT + 1.8, -4.0), (R_OUT + 1.4, 0.0), (R_OUT + 0.8, 2.0), (R_OUT + 0.25, 5.0), (R_OUT, 9.0),
                 (R_OUT - 0.2, 14.0), (R_OUT - 0.45, 20.0), (R_OUT - 0.8, 27.0), (R_OUT - 1.15, 34.0),
                 (R_OUT - 1.5, 41.0), (R_OUT - 1.85, 48.0), (R_OUT - 2.2, 55.0), (R_OUT - 2.6, 62.0),
                 (R_OUT - 3.0, 69.0), (R_OUT - 3.4, 76.0), (R_OUT - 3.8, 83.0), (R_OUT - 4.2, 90.0),
                 (R_OUT - 4.5, 95.0), (R_OUT - 4.9, 98.3)):
        P.append((r, z, "o"))
    for r, z in ((R_OUT - 6.5, 99.8), (34.0, 100.6), (28.0, 101.0), (22.0, 100.8), (17.5, 100.2)):
        P.append((r, z, "c"))
    for r, z in ((OCULUS_R + 1.2, 99.6), (OCULUS_R + 0.2, 98.4), (OCULUS_R, 95.0), (OCULUS_R, 89.0),
                 (OCULUS_R + 0.1, 83.0), (OCULUS_R + 0.4, 79.2)):
        P.append((r, z, "s"))
    hz = HOLLOW_H
    for r, z in ((OCULUS_R + 1.5, hz - 0.4), (19.5, hz - 1.4), (24.0, hz - 3.0), (28.5, hz - 5.6), (32.4, hz - 9.2),
                 (35.4, hz - 13.6), (37.4, hz - 18.6), (38.5, hz - 23.6), (R_IN, hz - 28.5)):
        P.append((r, z, "d"))
    for z in (42.0, 35.0, 28.0, 21.0, 14.0, 8.0, 3.0, 0.0, -3.0):
        P.append((R_IN, z, "i"))
    P.append((R_IN + 3.0, -4.6, "b"))
    return P


def door_cutter_bm():
    """Splayed arch bore: 14 wide x 20 high at the outer face (r >= 46.5), 17.5 wide inside (r 33)."""
    def arch(w, h_wall, h_top, bottom, n=14):
        pts = [(-w / 2, bottom), (-w / 2, h_wall)]
        for i in range(1, n):
            a = math.pi - math.pi * i / n
            pts.append((w / 2 * math.cos(a), h_wall + (h_top - h_wall) * math.sin(a)))
        pts += [(w / 2, h_wall), (w / 2, bottom)]
        return pts
    d = Vector((math.cos(DOOR_A), math.sin(DOOR_A), 0))
    tv = Vector((-d.y, d.x, 0))
    secs = []
    for r, w, hw, ht in ((31.0, 17.5, 13.5, 21.6), (37.0, 16.6, 13.4, 21.2), (46.6, DOOR_W, DOOR_H - DOOR_W / 2, DOOR_H),
                         (54.0, DOOR_W, DOOR_H - DOOR_W / 2, DOOR_H)):
        secs.append([d * r + tv * u + Vector((0, 0, v)) for (u, v) in arch(w, hw, ht, -7.0)])
    t = bmesh.new()
    rings = [[t.verts.new(p) for p in s] for s in secs]
    n = len(secs[0])
    for a, b in zip(rings, rings[1:]):
        for k in range(n):
            t.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    t.faces.new(list(reversed(rings[0])))
    t.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(t, faces=t.faces)
    return t


def bm_boolean(target_bm, cutter_bm, op="DIFFERENCE"):
    import bpy
    me_t = bpy.data.meshes.new("_bt")
    target_bm.to_mesh(me_t)
    me_c = bpy.data.meshes.new("_bc")
    cutter_bm.to_mesh(me_c)
    for m in (me_t, me_c):
        m.materials.append(lglib.get_mat("RootBark"))
        m.materials.append(lglib.get_mat("Heartwood"))
    ot = bpy.data.objects.new("_bt", me_t)
    oc = bpy.data.objects.new("_bc", me_c)
    bpy.context.scene.collection.objects.link(ot)
    bpy.context.scene.collection.objects.link(oc)
    mod = ot.modifiers.new("b", "BOOLEAN")
    mod.operation = op
    mod.object = oc
    mod.solver = "EXACT"
    dg = bpy.context.evaluated_depsgraph_get()
    res = bmesh.new()
    res.from_object(ot.evaluated_get(dg), dg)
    bpy.data.objects.remove(ot)
    bpy.data.objects.remove(oc)
    bpy.data.meshes.remove(me_t)
    bpy.data.meshes.remove(me_c)
    return res


def sector_split(b, a0, a1):
    """Copy of bmesh b keeping the wedge a0..a1 (Blender angles, a1 - a0 <= 180 deg)."""
    c = b.copy()
    n0 = Vector((-math.sin(a0), math.cos(a0), 0))
    n1 = Vector((-math.sin(a1), math.cos(a1), 0))
    bmesh.ops.bisect_plane(c, geom=c.verts[:] + c.edges[:] + c.faces[:], plane_co=(0, 0, 0), plane_no=-n0,
                           clear_outer=True)
    bmesh.ops.bisect_plane(c, geom=c.verts[:] + c.edges[:] + c.faces[:], plane_co=(0, 0, 0), plane_no=n1,
                           clear_outer=True)
    return c


def add_bm_by_material(pb, b, mats):
    """Split bmesh faces by material_index into PB material buckets."""
    for mi, mat in enumerate(mats):
        c = b.copy()
        bmesh.ops.delete(c, geom=[f for f in c.faces if f.material_index != mi], context="FACES")
        if len(c.faces):
            pb.add(mat, c)
        else:
            c.free()


def r_out_at(z):
    P = [(r, zz) for r, zz, k in shell_profile() if k == "o"]
    for (r1, z1), (r2, z2) in zip(P, P[1:]):
        if z1 <= z <= z2:
            return r1 + (r2 - r1) * (z - z1) / (z2 - z1)
    return P[-1][0]


def ang_dist(a, b):
    return abs((a - b + math.pi) % TAU - math.pi)


def hero_shell_parts():
    """4 bark sectors (door sector first) + roots + outer details + interior lanterns. Origin = trunk base centre."""
    prof = shell_profile()
    kinds = [k for _, _, k in prof]
    heart = lambda i: 1 if (kinds[i] in ("d", "i") and kinds[(i + 1) % len(kinds)] in ("d", "i", "b")) else 0
    solid = revolve_bm(prof, 320, bark_disp(3, lump=0.045, buttress=0.26), closed=True, mat_of_seg=heart, phase=DOOR_A)
    cut = door_cutter_bm()
    solid2 = bm_boolean(solid, cut)
    solid.free()
    cut.free()
    parts = []
    names = ["door", "north", "back", "south"]
    for k in range(4):
        a0 = DOOR_A - math.pi / 4 + k * math.pi / 2
        pb = WPB(f"hollow_tree_world_shell_part{k + 1}", tile_scale=3.0)
        sec = sector_split(solid2, a0, a0 + math.pi / 2)
        add_bm_by_material(pb, sec, ["RootBark", "Heartwood"])
        sec.free()
        pb.role = f"trunk wall sector {k + 1} ({names[k]}: Blender angles {math.degrees(a0):.0f}..{math.degrees(a0) + 90:.0f})"
        parts.append(pb)
    solid2.free()
    parts.append(hero_roots())
    parts.append(hero_outer_details())
    parts += hero_interior()
    return parts


# ----------------------------------------------------------------------------- roots (kept off the course)
_KEEP = None


def keepouts():
    global _KEEP
    if _KEEP is None:
        H = WF.holes_world(WORLD)
        _KEEP = (WF.hole_obbs(H) + WF.path_obbs(WORLD, door_center=T_O) + WF.lantern_obbs(WORLD))
    return _KEEP


_TERR = None


def terrain():
    global _TERR
    if _TERR is None:
        _TERR = WF.Terrain()
    return _TERR


def ground_z(bx, by, origin=T_O):
    """Terrain height (Blender local z) under a local point of a piece at origin."""
    w = blw((bx, by, 0), origin)
    return float(terrain().height(w[0], w[2])) - origin[1]


def root_path(a, r_end, h_start, arch=0.0, bend=0.0, seed=0):
    """Points + radii of a buttress root leaving the trunk at angle a. arch > 0 lifts the middle (arching root)."""
    rnd = random.Random(seed)
    pts, rad = [], []
    n = 12
    r0 = R_OUT - 3.0
    for i in range(n + 1):
        u = i / n
        r = r0 + (r_end - r0) * u
        aa = a + bend * u * u + 0.03 * math.sin(u * 7 + seed)
        x, y = math.cos(aa) * r, math.sin(aa) * r
        g = ground_z(x, y)
        thick = (8.0 - 6.6 * u ** 0.7) * (1 + 0.15 * rnd.uniform(-1, 1) * u)
        zc = g + thick * 0.12 + h_start * (1 - u) ** 2.0 + arch * math.sin(math.pi * min(u * 1.15, 1.0)) - 1.2 * u ** 3
        pts.append(Vector((x, y, zc)))
        rad.append(max(thick, 0.5))
    return pts, rad


def root_clear(pts, rad):
    P = np.array([blw(p) for p in pts])
    for p, r in zip(P, rad):
        if not WF.points_clear(p[None, :], keepouts(), grow=r + 0.6)[0]:
            return False
    # sample between control points too
    for (p, q), r in zip(zip(P, P[1:]), rad):
        m = (p + q) / 2
        if not WF.points_clear(m[None, :], keepouts(), grow=r + 0.6)[0]:
            return False
    return True


def hero_roots():
    pb = WPB("hollow_tree_world_shell_part5", tile_scale=2.0)
    pb.role = "buttress roots (flare to r 65.8; trimmed by fit rules so they stay off H8/H9 felt, walls and walkways)"
    rnd = random.Random(41)
    placed = []
    k = 0
    a_deg = -180.0
    while a_deg < 180.0:
        a = math.radians(a_deg) + rnd.uniform(-0.05, 0.05)
        a_deg += rnd.uniform(13, 19)
        if ang_dist(a, DOOR_A) < math.radians(17):
            continue
        h0 = rnd.uniform(13, 22)
        bend = rnd.uniform(-0.12, 0.12)
        best = None
        for r_end in np.arange(FLARE_R - rnd.uniform(0, 7), 49.0, -1.5):
            pts, rad = root_path(a, r_end, h0, bend=bend, seed=k)
            if root_clear(pts, rad):
                best = (pts, rad, r_end)
                break
        if best is None:
            continue
        pts, rad, r_end = best
        pb.tube("RootBark", pts, rad, 12, wobble=0.12, seed=k)
        placed.append((math.degrees(a), r_end))
        # side rootlet
        if r_end > 55 and rnd.random() < 0.7:
            s = rnd.choice((-1, 1))
            base = pts[6]
            d = Vector((math.cos(a + s * 0.5), math.sin(a + s * 0.5), 0))
            q = [base, base + d * 5 + Vector((0, 0, -0.8)), base + d * 10 + Vector((0, 0, -1.6))]
            for p in q[1:]:
                p.z = min(p.z, ground_z(p.x, p.y) + 0.4)
            qr = [rad[6] * 0.55, rad[6] * 0.35, 0.3]
            if root_clear(q, qr):
                pb.tube("RootBark", q, qr, 8, wobble=0.1, seed=k + 50)
        # moss saddle on the root
        m = pts[4]
        pb.rock("Moss", (rad[4] * 2.6, rad[4] * 2.0, rad[4] * 0.7), loc=(m.x, m.y, m.z + rad[4] * 0.62),
                rot=(0, 0, math.degrees(a)), seed=k + 7, amp=0.1)
        k += 1
    pb.root_angles = placed
    return pb


# ----------------------------------------------------------------------------- outer details: door frame, fungi,
#                                                                                windows, lanterns, moss
def on_outer(a, z, inset=0.6):
    return pol(a, r_out_at(z) - inset, z)


def hero_outer_details():
    from props_hero import window, arch_band, FRAME_Y
    pb = WPB("hollow_tree_world_shell_part6", tile_scale=1.5)
    pb.role = "outer details: Heartwood Door frame + lanterns, glowing windows, bracket fungi, moss, lantern hooks"
    d = Vector((math.cos(DOOR_A), math.sin(DOOR_A), 0))
    tv = Vector((-d.y, d.x, 0))
    # door frame: oak arch band standing in the door mouth at r 46.3 (inner edge = the 14 x 20 opening)
    rot = Matrix.Rotation(DOOR_A + math.pi / 2, 4, "Z")
    mt = Matrix.Translation(d * (R_OUT + 1.0)) @ rot @ FRAME_Y
    pb.prism("Oak", arch_band(DOOR_W, DOOR_H - DOOR_W / 2, DOOR_H, 1.3, bottom=-0.5, n=16), 2.4, matrix=mt)
    # keystone + lantern brackets
    pb.box("Oak", (2.6, 2.8, 3.2), loc=d * (R_OUT + 1.1) + Vector((0, 0, DOOR_H + 1.75)), rot=(0, 0, math.degrees(DOOR_A)))
    for s in (-1, 1):
        base = d * (R_OUT + 1.6) + tv * s * (DOOR_W / 2 + 2.6)
        pb.box("Iron", (0.35, 0.35, 0.35), loc=base + Vector((0, 0, 17.6)))
        pb.tube("Iron", [base + Vector((0, 0, 17.6)), base + d * 2.2 + Vector((0, 0, 18.0)),
                         base + d * 2.8 + Vector((0, 0, 17.4))], 0.18, 5, smooth=False)
        pb.lantern(3.2, loc=base + d * 2.8 + Vector((0, 0, 13.7)), paper="Paper" if s > 0 else "PaperOrange")
    rnd = random.Random(7)
    # glowing windows (high, unreachable) - knot windows with oak frames
    for a_deg, z, r in ((25, 34, 2.2), (95, 52, 2.6), (160, 41, 2.0), (215, 63, 2.4), (290, 47, 2.2), (330, 70, 1.8),
                        (60, 72, 2.0), (-20, 28, 1.6)):
        a = DOOR_A + math.radians(a_deg)
        n = Vector((math.cos(a), math.sin(a), 0))
        window(pb, on_outer(a, z, inset=0.2) + n * 0.4, n, r=r)
        pb.torus("RootBark", r + 0.55, 0.5, 14, 6, loc=on_outer(a, z, 0.0), rot=(90, 0, math.degrees(a) + 90))
    # bracket fungi shelves, in little stacks
    for j in range(13):
        a = DOOR_A + math.radians(rnd.uniform(25, 335))
        z0 = rnd.uniform(6, 60)
        for i in range(rnd.randint(1, 3)):
            z = z0 + i * rnd.uniform(2.5, 3.5)
            s = rnd.uniform(2.2, 4.2) * (1 - 0.18 * i)
            p = on_outer(a + i * 0.02, z, inset=0.8)
            n = Vector((math.cos(a), math.sin(a), 0))
            pb.sphere(rnd.choice(("CapOrange", "CapGold", "CapOrange")), s, loc=p + n * s * 0.35,
                      scale=(1.0, 1.0, 0.28), segs=12, rings=5, rot=(0, 0, 0))
    # moss cushions around the foot of the trunk and on the top rim
    for j in range(22):
        a = DOOR_A + math.radians(rnd.uniform(20, 340))
        z = rnd.uniform(-0.5, 2.5)
        s = rnd.uniform(5, 9)
        pb.rock("Moss", (s, s * 0.6, s * 0.28), loc=on_outer(a, max(z, 0), inset=1.4) + Vector((0, 0, z - max(z, 0))),
                rot=(0, 0, math.degrees(a) + 90), seed=100 + j, amp=0.12)
    for j in range(14):
        a = TAU * j / 14 + rnd.uniform(-0.1, 0.1)
        s = rnd.uniform(7, 11)
        pb.rock("Moss", (s, s * 0.7, 1.8), loc=pol(a, R_OUT - 6.5, 99.2), rot=(0, 0, math.degrees(a) + 90),
                seed=200 + j, amp=0.15)
    # lanterns on iron hooks around the front of the trunk (h ~ 22-26), away from the door bore
    for j, off in enumerate((-58, -44, -30, 30, 44, 58, 75, -75)):
        a = DOOR_A + math.radians(off)
        n = Vector((math.cos(a), math.sin(a), 0))
        z = 24.0 + 2.0 * math.sin(j * 1.7)
        p = on_outer(a, z, inset=0.3)
        pb.tube("Iron", [p, p + n * 1.8 + Vector((0, 0, 0.4)), p + n * 2.3 + Vector((0, 0, -0.2))], 0.13, 5,
                smooth=False)
        pb.lantern(2.4, loc=p + n * 2.3 + Vector((0, 0, -2.9)), lod=1, paper="Paper" if j % 2 else "PaperOrange")
    return pb


def catenary(p0, p1, sag, n):
    out = []
    for i in range(n + 1):
        u = i / n
        p = p0.lerp(p1, u)
        p.z -= sag * 4 * u * (1 - u)
        out.append(p)
    return out


def hero_interior():
    pb = WPB("hollow_tree_world_shell_part7", tile_scale=1.0)
    pb.role = ("interior: lantern strings across the hollow (local y 26-50, far above H9), wall lanterns, glowing "
               "mushrooms and gold fungi on the inner wall")
    rnd = random.Random(19)
    rin = R_IN + 0.3
    for j, (a_deg, z0, z1, sag, n) in enumerate(((10, 40, 37, 6, 8), (70, 46, 44, 7, 9), (125, 31, 34, 5, 7),
                                                 (165, 50, 47, 6, 8), (35, 28, 30, 4, 6))):
        a = DOOR_A + math.radians(a_deg)
        p0, p1 = pol(a, rin, z0), pol(a + math.pi + rnd.uniform(-0.5, 0.5), rin, z1)
        pts = catenary(p0, p1, sag, 24)
        pb.tube("RootBark", pts, 0.18, 4, smooth=False)
        for i in range(1, n):
            q = pts[round(i * 24 / n)]
            L = rnd.uniform(1.0, 4.0)
            pb.tube("RootBark", [q, q + Vector((0, 0, -L))], 0.07, 3, smooth=False)
            h = rnd.choice((2.0, 2.4, 3.0))
            pb.lantern(h, loc=q + Vector((0, 0, -L - h)), lod=1, paper=rnd.choice(("Paper", "Paper", "PaperOrange")))
    # wall lanterns on brackets, spiralling up
    for j in range(14):
        a = DOOR_A + math.radians(25 + j * 25.0)
        if ang_dist(a, DOOR_A) < math.radians(20):
            continue
        z = 9 + j * 3.6
        n = Vector((math.cos(a), math.sin(a), 0))
        p = pol(a, rin, z)
        pb.tube("Iron", [p, p - n * 1.6 + Vector((0, 0, 0.5)), p - n * 2.0], 0.12, 5, smooth=False)
        pb.lantern(2.2, loc=p - n * 2.0 + Vector((0, 0, -2.7)), lod=1, paper="Paper")
    # glowing mushroom clumps at the foot of the inner wall (protrude <= 1.3 inward), away from the door bore
    for j in range(16):
        a = DOOR_A + math.radians(rnd.uniform(24, 336))
        for i in range(rnd.randint(2, 3)):
            aa = a + rnd.uniform(-0.04, 0.04)
            rr = R_IN + 0.2 - rnd.uniform(0.2, 1.0)
            h = rnd.uniform(0.6, 1.6)
            c = pol(aa, rr, ground_z(*pol(aa, rr)[:2]) - 0.15)
            pb.cyl("Cream", 0.12, 0.16, h, 6, loc=c + Vector((0, 0, h / 2)), smooth=False)
            pb.sphere("ShroomGlow", 0.32 + h * 0.15, loc=c + Vector((0, 0, h)), scale=(1, 1, 0.5), segs=8, rings=4)
    # gold fungi shelves on the inner wall
    for j in range(16):
        a = DOOR_A + math.radians(rnd.uniform(20, 340))
        z = rnd.uniform(8, 50)
        s = rnd.uniform(1.6, 3.2)
        n = Vector((math.cos(a), math.sin(a), 0))
        pb.sphere("CapGold", s, loc=pol(a, R_IN + 0.2, z) - n * s * 0.3, scale=(1, 1, 0.26), segs=10, rings=5)
    # pass 4 (art director: "H9 interior too dark"): low lantern clusters on iron brackets along the inner wall
    # (glow at eye level, 5-9 above the floor, protruding <= 2.3 inward) + extra big glowing mushroom clumps at the
    # wall foot. H9's keep-outs (felt + 1.25 up to felt top + 6.5) end >= 3.7 inside the wall; world_fitcheck
    # verifies every triangle. Glow centres are recorded in pb.lights (world coords) for PointLights.
    pb8 = WPB("hollow_tree_world_shell_part8", tile_scale=1.0)
    pb8.role = ("pass 4 interior glow: 18 low lantern clusters (3 lanterns each, glow 5-9 above the floor) on iron "
                "brackets along the inner wall + 24 big glowing-mushroom clumps at the wall foot; lights_world = "
                "PointLight positions")
    lights = []
    rnd2 = random.Random(77)
    for j in range(18):
        a = DOOR_A + math.radians(18 + j * 324 / 17)
        if ang_dist(a, DOOR_A) < math.radians(17):
            continue
        n = Vector((math.cos(a), math.sin(a), 0))
        g = ground_z(*pol(a, R_IN - 1.0)[:2])
        z = g + rnd2.uniform(8.5, 10.0)
        p = pol(a, R_IN + 0.3, z)
        t = Vector((-n.y, n.x, 0))
        pb8.tube("Iron", [p, p - n * 1.3 + Vector((0, 0, 0.35)), p - n * 1.9 + Vector((0, 0, 0.2))], 0.1, 5, smooth=False)
        pb8.tube("Iron", [p - n * 1.3 + Vector((0, 0, 0.35)) - t * 0.9, p - n * 1.3 + Vector((0, 0, 0.35)) + t * 0.9],
                0.06, 4, smooth=False)
        for (dt, dn, hgt, drop) in ((0.0, 1.9, 1.7, 0.6), (-0.9, 1.3, 1.3, 1.3), (0.9, 1.3, 1.2, 0.9)):
            q = p - n * dn + t * dt + Vector((0, 0, 0.3))
            pb8.tube("RootBark", [q, q - Vector((0, 0, drop))], 0.04, 3, smooth=False)
            c = q - Vector((0, 0, drop + hgt))
            pb8.lantern(hgt, loc=c, lod=1, paper=rnd2.choice(("Paper", "PaperOrange")))
        lights.append(("wall_lantern_cluster", p - n * 1.5 + Vector((0, 0, -1.6))))   # one light per cluster
    for j in range(24):
        a = DOOR_A + math.radians(22 + j * 316 / 23 + rnd2.uniform(-4, 4))
        cl = []
        for i in range(rnd2.randint(3, 5)):
            aa = a + rnd2.uniform(-0.035, 0.035)
            rr = R_IN + 0.1 - rnd2.uniform(0.3, 1.4)
            h = rnd2.uniform(0.8, 2.2)
            c = pol(aa, rr, ground_z(*pol(aa, rr)[:2]) - 0.15)
            pb8.cyl("Cream", 0.14, 0.2, h, 6, loc=c + Vector((0, 0, h / 2)), smooth=False)
            pb8.sphere("ShroomGlow", 0.38 + h * 0.2, loc=c + Vector((0, 0, h)), scale=(1, 1, 0.5), segs=8, rings=4)
            cl.append(c + Vector((0, 0, h)))
        if j % 2 == 0:                       # one light per two clumps (Quest: keep PointLights few)
            lights.append(("wall_mushroom_clump", sum(cl, Vector()) / len(cl)))
    pb8.lights = [dict(kind=k, pos=[round(float(v), 2) for v in blw(tuple(c))]) for k, c in lights]
    return [pb, pb8]


# ============================================================================ HERO: crown
CROWN_POS = None   # set from world.json backdrop piece


def lumpy_mass(pb, c, size, mats, seed, bumps=8, ico=3):
    """Big leaf mass: displaced ellipsoid + bumps on its upper/outer surface."""
    rnd = random.Random(seed)
    sx, sy, sz = size
    pb.rock(mats[0], (sx, sy, sz), loc=c - Vector((0, 0, sz * 0.5 * 0.0)), seed=seed, amp=0.11, ico=ico,
            flat_bottom=False, smooth=True)
    for i in range(bumps):
        th = rnd.uniform(0, TAU)
        ph = rnd.uniform(0.15, 1.25)
        dirv = Vector((math.cos(th) * math.sin(ph), math.sin(th) * math.sin(ph), math.cos(ph)))
        p = c + Vector((dirv.x * sx * 0.42, dirv.y * sy * 0.42, dirv.z * sz * 0.38))
        s = rnd.uniform(0.32, 0.48)
        pb.rock(mats[1 + i % (len(mats) - 1)], (sx * s, sy * s, sz * s * 0.85), loc=p, seed=seed * 10 + i, amp=0.14,
                ico=max(ico - 2, 2), flat_bottom=False, smooth=True)


def crown_parts():
    """Crown: origin = crown base centre (world.json pos, y = trunk base + 100). Limbs start just below it."""
    rnd = random.Random(5)
    limbs = WPB("hollow_tree_crown_part1", tile_scale=3.0)
    limbs.role = "limbs from the trunk top into each leaf mass + 12 big hanging lanterns under the crown"
    masses = [WPB(f"hollow_tree_crown_part{k + 2}", tile_scale=4.0) for k in range(5)]
    for k, m in enumerate(masses):
        m.role = "leaf masses " + ("1-2 (lower ring)", "3-4 (lower ring)", "5-6 (lower ring)", "7-8 (upper tier)", "9 (upper tier)")[k]
    ring = []
    for k in range(6):   # lower outer tier, drooping
        a = DOOR_A + math.radians(30 + k * 60 + rnd.uniform(-8, 8))
        ring.append((a, rnd.uniform(52, 58), rnd.uniform(24, 30), (rnd.uniform(60, 70), rnd.uniform(56, 66), rnd.uniform(44, 52))))
    for k in range(3):   # upper tier: domes the crown, leaves a small light gap over the oculus
        a = DOOR_A + math.radians(k * 120 + rnd.uniform(-10, 10))
        ring.append((a, rnd.uniform(28, 34), rnd.uniform(48, 54), (rnd.uniform(64, 72), rnd.uniform(60, 68), rnd.uniform(40, 46))))
    pal = [("Gold", "Pumpkin", "Gold", "MapleRed"), ("Pumpkin", "Gold", "Pumpkin", "MapleRed"),
           ("Gold", "Gold", "Pumpkin", "Pumpkin")]
    for k, (a, r, z, size) in enumerate(ring):
        c = pol(a, r, z)
        tgt = masses[k // 2]
        lumpy_mass(tgt, c, size, pal[k % 3], seed=300 + k, bumps=10, ico=5 if k < 6 else 4)
        # limb from the trunk top rim into the mass
        a0 = a + rnd.uniform(-0.1, 0.1)
        p0 = pol(a0, 30.0 if k < 6 else 22.0, -3.0)
        p1 = pol(a0, 36.0 if k < 6 else 25.0, 6.0)
        p2 = pol(a, r * 0.75, z * 0.55)
        p3 = pol(a, r * 0.95, z * 0.85)
        limbs.tube("RootBark", [p0, p1, p2, p3], [9.0, 7.2, 5.0, 3.0], 12, wobble=0.12, seed=k)
        for s in (-1, 1):   # side branches
            q0 = p2
            q1 = pol(a + s * 0.35, r * 1.05, z * 0.75)
            limbs.tube("RootBark", [q0, (q0 + q1) / 2 + Vector((0, 0, 2.5)), q1], [3.2, 2.2, 1.0], 8, wobble=0.1)
    # hanging lanterns under the outer crown (Glow cores = PointLights)
    for j in range(12):
        a = DOOR_A + math.radians(j * 30 + rnd.uniform(-8, 8))
        r = rnd.uniform(56, 76)
        top = 13.0
        L = rnd.uniform(4, 11)
        p = pol(a, r, top)
        limbs.tube("RootBark", [p, p - Vector((0, 0, L))], 0.2, 4, smooth=False)
        limbs.lantern(4.0, loc=p - Vector((0, 0, L + 4.0)), paper=("Paper", "PaperOrange")[j % 2])
    fit_bms([limbs] + masses, (176.0, 81.0, 176.0), base_z=-3.0)
    return [limbs] + masses


# ============================================================================ sister trees (variants of hollow_tree)
def giant_tree(name, size, canopy_pal, trunk_r, trunk_h, seed, masses=7, door=False, lanterns=3, squat=1.0,
               roots=7, hollow_door=False):
    """Background giant: furrowed lathe trunk (same bark recipe as the hero), buttress roots, limbs and lumpy
    canopy masses in the hollow_tree look; scaled to `size` (Roblox x, y, z)."""
    rnd = random.Random(seed)
    pb = WPB(name, tile_scale=2.0)
    prof = [(trunk_r * 1.45, -2.0, "o"), (trunk_r * 1.25, 0.5, "o"), (trunk_r * 1.08, 2.5, "o"), (trunk_r, 6.0, "o")]
    for i in range(1, 8):
        z = 6 + (trunk_h - 6) * i / 7
        prof.append((trunk_r * (1 - 0.32 * i / 7), z, "o"))
    prof.append((0.0, trunk_h + 0.5, "o"))
    pb.add("RootBark", revolve_bm(prof, 40, bark_disp(seed, furrows=11, lump=0.05, furrow=0.03)))
    for k in range(roots):
        a = TAU * k / roots + rnd.uniform(-0.25, 0.25)
        L = trunk_r * rnd.uniform(1.4, 2.1)
        pts = []
        for i in range(8):
            u = i / 7
            r = trunk_r * 0.8 + L * u
            pts.append(pol(a + 0.1 * u * u, r, trunk_r * 0.9 * (1 - u) ** 2 + trunk_r * 0.12 * (1 - u) - 0.4 * u))
        pb.tube("RootBark", pts, [trunk_r * (0.42 - 0.34 * i / 7) for i in range(8)], 8, wobble=0.12, seed=seed + k)
    # limbs + canopy
    blobs = []
    W = 1.0
    for k in range(masses - 1):
        a = TAU * k / (masses - 1) + rnd.uniform(-0.2, 0.2)
        r = trunk_r * 2.2
        z = trunk_h + trunk_r * rnd.uniform(0.6, 1.4) * squat
        p0 = pol(a, trunk_r * 0.4, trunk_h * 0.72)
        p1 = pol(a, r * 0.6, trunk_h + trunk_r * 0.2)
        p2 = pol(a, r * 0.95, z - trunk_r * 0.2)
        pb.tube("RootBark", [p0, p1, p2], [trunk_r * 0.45, trunk_r * 0.3, trunk_r * 0.12], 8, wobble=0.1, seed=seed + 20 + k)
        blobs.append((pol(a, r, z), trunk_r * rnd.uniform(1.7, 2.1)))
    blobs.append((Vector((0, 0, trunk_h + trunk_r * 2.0 * squat)), trunk_r * 2.2))
    for k, (c, rr) in enumerate(blobs):
        lumpy_mass(pb, c, (rr * 2, rr * 2, rr * 1.5 * squat), canopy_pal[k % len(canopy_pal):] + canopy_pal[:k % len(canopy_pal)],
                   seed=seed * 10 + k, bumps=7, ico=4)
    # lanterns on cords under the canopy
    for j in range(lanterns):
        a = rnd.uniform(0, TAU)
        p = pol(a, trunk_r * rnd.uniform(1.8, 2.6), trunk_h - trunk_r * 0.1)
        L = trunk_r * 0.4
        pb.tube("RootBark", [p, p - Vector((0, 0, L))], 0.12, 4, smooth=False)
        pb.lantern(trunk_r * 0.28, loc=p - Vector((0, 0, L + trunk_r * 0.28)), paper=("Paper", "PaperOrange")[j % 2])
    if door:
        from props_hero import window, arch_poly, FRAME_Y
        a = -math.pi / 2   # faces Roblox +Z (south)
        n = Vector((math.cos(a), math.sin(a), 0))
        rot = Matrix.Rotation(a + math.pi / 2, 4, "Z")
        mt = Matrix.Translation(n * (trunk_r * 1.08)) @ rot @ FRAME_Y
        w = trunk_r * 0.7
        pb.prism("Oak", arch_poly(w + 0.8, w * 0.8, w * 1.45 + 0.4, 0.0, 12), 0.6, matrix=mt)
        pb.prism("Glow", arch_poly(w, w * 0.8, w * 1.45, 0.0, 12), 0.6, matrix=mt @ Matrix.Translation((0, 0, 0.15)))
        for deg, z in ((40, trunk_h * 0.45), (-35, trunk_h * 0.62), (150, trunk_h * 0.5)):
            aw = a + math.radians(deg)
            nn = Vector((math.cos(aw), math.sin(aw), 0))
            rz = trunk_r * (1 - 0.32 * (z - 6) / (trunk_h - 6))
            window(pb, nn * (rz * 0.98) + Vector((0, 0, z)), nn, r=trunk_r * 0.12)
    for j in range(6):
        a = rnd.uniform(0, TAU)
        z = rnd.uniform(trunk_h * 0.2, trunk_h * 0.7)
        rz = trunk_r * (1 - 0.32 * (z - 6) / (trunk_h - 6))
        s = trunk_r * rnd.uniform(0.18, 0.3)
        pb.sphere(rnd.choice(("CapOrange", "CapGold")), s, loc=pol(a, rz + s * 0.2, z), scale=(1, 1, 0.3), segs=10, rings=4)
    fit_bms([pb], size)
    return pb


# ============================================================================ waterfalls
def wf_local(top_w, bot_w, pos, yaw):
    """World top/bottom -> Blender-local points for a piece at pos with yaw (deg)."""
    a = math.radians(yaw)
    c, s = math.cos(a), math.sin(a)

    def L(p):
        dx, dz = p[0] - pos[0], p[2] - pos[2]
        lx = dx * c - dz * s           # inverse of x' = lx c + lz s ; z' = -lx s + lz c
        lz = dx * s + dz * c
        return Vector((lx, -lz, p[1] - pos[1]))
    return L(top_w), L(bot_w)


def sheet(pb, top, bot, w, seed, ribbons=4, segs=16, across=6, thick=0.5, mat="Water", foam=True):
    """Falling curtain from lip `top` to plunge `bot` (Blender local). Parabolic fall, slight forward bulge."""
    rnd = random.Random(seed)
    d = bot - top
    hd = Vector((d.x, d.y, 0))
    fwd = hd.normalized() if hd.length > 1e-6 else Vector((0, -1, 0))
    side = Vector((-fwd.y, fwd.x, 0))
    secs = []
    centre = []
    for i in range(segs + 1):
        u = i / segs
        p = top + hd * (u ** 0.5) + Vector((0, 0, d.z * u))
        ww = w * (1 + 0.22 * u)
        sec = []
        for j in range(across + 1):
            v = j / across - 0.5
            bulge = 0.35 * w / 9 * math.cos(v * math.pi) * (0.4 + u)
            q = p + side * v * ww + fwd * (bulge + 0.15 * noise.noise(Vector((v * 3, u * 4, seed))))
            sec.append(q)
        back = [q - fwd * thick for q in reversed(sec)]
        secs.append(sec + back)
        centre.append(p)
    pb.loft(mat, secs, smooth=True)
    if foam:
        for k in range(ribbons):
            v = (k + 0.5) / ribbons - 0.5 + rnd.uniform(-0.06, 0.06)
            pts, rad = [], []
            for i in range(segs + 1):
                u = i / segs
                ww = w * (1 + 0.22 * u)
                bulge = 0.35 * w / 9 * math.cos(v * math.pi) * (0.4 + u)
                pts.append(centre[i] + side * v * ww + fwd * (bulge + 0.2))
                rad.append(w / ribbons * rnd.uniform(0.12, 0.22) * (0.6 + 0.8 * u))
            pb.tube("Foam", pts, rad, 5, flatten=0.45)
    # plunge splash + mist
    for k in range(9):
        p = bot + side * rnd.uniform(-w * 0.6, w * 0.6) + fwd * rnd.uniform(-0.5, w * 0.25)
        s = w * rnd.uniform(0.12, 0.22)
        pb.sphere("Foam", s, loc=p + Vector((0, 0, s * 0.1)), scale=(1.4, 1.0, 0.45), segs=8, rings=5)
    for k in range(5):
        p = bot + side * rnd.uniform(-w * 0.5, w * 0.5) + fwd * rnd.uniform(0, w * 0.4)
        s = w * rnd.uniform(0.25, 0.4)
        pb.sphere("Mist", s, loc=p + Vector((0, 0, s * 0.6)), scale=(1.3, 1.0, 0.8), segs=10, rings=6)
    return fwd, side


def falls_rocks(pb, top, bot, w, fwd, side, seed, n_lip=6, n_base=7, tight=False):
    rnd = random.Random(seed)
    h = top.z - bot.z
    # backing slab behind the curtain (hides terrain voxel steps)
    for i in range(max(2, int(h / 6))):
        u = (i + 0.5) / max(2, int(h / 6))
        p = top.lerp(bot, u * 0.9) - fwd * ((0.9 if tight else 1.6) + 0.6 * rnd.random()) + Vector((0, 0, 0))
        p.z = top.z - h * u - (1.0 if tight else 0.0)
        sz = h / max(2, int(h / 6)) * (1.2 if tight else 1.5)
        lglib_rock_slab(pb, p, (w * 1.35, 1.6 if tight else 3.0, sz), seed + i)
    for s in (-1, 1):
        for i in range(n_lip // 2):
            p = top + side * s * (w * 0.55 + i * 1.6 + rnd.uniform(0, 1.2)) + fwd * (rnd.uniform(0.8, 2.0) if tight else -rnd.uniform(0.5, 2.5))
            sz = rnd.uniform(2.2, 3.8) * max(1.0, w / 9)
            pb.rock("Slate", (sz, sz * 0.9, sz * 0.8), loc=p - Vector((0, 0, sz * 0.4)), seed=seed * 3 + i + s * 10, amp=0.15)
            if rnd.random() < 0.6:
                pb.rock("Moss", (sz * 0.8, sz * 0.7, sz * 0.25), loc=p + Vector((0, 0, sz * 0.3)), seed=seed * 5 + i, amp=0.1)
        for i in range(n_base // 2):
            p = bot + side * s * (w * 0.6 + i * 2.0 + rnd.uniform(0, 1.5)) + fwd * rnd.uniform(-1.0, 1.5)
            sz = rnd.uniform(2.0, 3.6) * max(1.0, w / 9)
            pb.rock("Slate", (sz, sz * 0.9, sz * 0.7), loc=p - Vector((0, 0, sz * 0.3)), seed=seed * 7 + i + s * 20, amp=0.15)


def lglib_rock_slab(pb, c, size, seed):
    pb.rock("Slate", size, loc=c - Vector((0, 0, size[2] * 0.5)), seed=seed, amp=0.1, ico=2, flat_bottom=False)


def waterfall(name, wf, pos, yaw, strands=1, lanterns=False, seed=0, tight=False):
    pb = WPB(name, tile_scale=1.5)
    top, bot = wf_local(wf["top"], wf["bottom"], pos, yaw)
    w = wf["width"]
    if strands == 1:
        fwd, side = sheet(pb, top, bot, w * 0.8, seed, ribbons=max(3, int(w / 2)), segs=max(10, int((top.z - bot.z) / 2.2)))
    else:
        hd = Vector(((bot - top).x, (bot - top).y, 0)).normalized()
        sd = Vector((-hd.y, hd.x, 0))
        for s in (-1, 1):
            o = sd * s * w * 0.27
            fwd, side = sheet(pb, top + o, bot + o, w * 0.36, seed + s, ribbons=2, segs=8)
        p = top - fwd * 0.5
        pb.rock("Slate", (w * 0.2, 3.0, top.z - bot.z + 1.5), loc=(top + bot) / 2 - fwd * 0.9 - Vector((0, 0, (top.z - bot.z) / 2 + 0.6)),
                seed=seed + 5, amp=0.12, ico=2)
        pb.rock("Moss", (w * 0.24, 3.0, 0.7), loc=p + Vector((0, 0, 0.3)), seed=seed + 6)
    falls_rocks(pb, top, bot, w, fwd, side, seed + 30, tight=tight)
    # lip water surface
    if not tight:
        pb.plane("Water", w * 0.8, 3.0, loc=top - fwd * 1.5 + Vector((0, 0, 0.05)), rot=(0, 0, math.degrees(math.atan2(fwd.y, fwd.x)) + 90))
    if lanterns:
        for s in (-1, 1):
            base = top + side * s * (w * 0.62 + 1.8) - fwd * 1.2
            pb.cyl("Oak", 0.25, 0.25, 6.0, 8, loc=base + Vector((0, 0, 2.0)), smooth=False)
            pb.box("Oak", (0.3, 0.3, 2.0), loc=base + Vector((0, 0, 4.9)) + fwd * 0.9, rot=(90, 0, math.degrees(math.atan2(fwd.y, fwd.x)) + 90))
            pb.lantern(1.6, loc=base + fwd * 1.8 + Vector((0, 0, 3.0)), paper="Paper" if s > 0 else "PaperOrange")
        for k, s in enumerate((-1, 1, -1)):
            base = bot + side * s * (w * 0.75 + 1.5 + k) + fwd * 1.0
            pb.lantern(1.0, loc=base + Vector((0, 0, 0.6)), hook=False, paper="PaperOrange")
    return pb


# ============================================================================ rock kits
def strata_block(pb, mat, size, loc, seed, cube=0.72, amp=0.07, tilt=0.0):
    """Boxy slate block (cube/sphere blend, light noise), size Blender (x, y, z), loc = centre."""
    t = bmesh.new()
    bmesh.ops.create_icosphere(t, subdivisions=2, radius=0.5)
    off = Vector((seed * 3.1, seed * 1.3, seed * 2.7))
    for v in t.verts:
        c = v.co / (2 * max(abs(v.co.x), abs(v.co.y), abs(v.co.z)))
        v.co = v.co.lerp(c, cube)
        k = amp * 2 * noise.noise(v.co * 2.3 + off)
        v.co *= 1 + k
    bmesh.ops.scale(t, vec=Vector(size), verts=t.verts)
    if tilt:
        bmesh.ops.rotate(t, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(tilt), 3, "Y"), verts=t.verts)
    bmesh.ops.translate(t, vec=Vector(loc), verts=t.verts)
    pb.add(mat, t, None, False)


def cliff_face(name, W, H, D, style, seed, tile=2.0):
    """Modular cliff face, front = Roblox local +Z (Blender -Y), base centre origin, back at Blender +Y = D/2.
    style: strata | columns | overhang | corner."""
    rnd = random.Random(seed)
    pb = WPB(name, tile_scale=tile)
    lean = 0.12   # face leans back a little
    if style == "corner":
        # quarter-round convex corner: blocks around an arc, front faces sweep from -Y to +X
        z = 0.0
        while z < H - 0.5:
            hh = rnd.uniform(H / 5, H / 3.5)
            n = 4
            for i in range(n):
                a = -math.pi / 2 + (math.pi / 2) * (i + 0.5) / n + rnd.uniform(-0.05, 0.05)
                R = W * 0.42 - z * lean + rnd.uniform(-0.8, 0.8)
                c = Vector((math.cos(a) * R - W * 0.12, math.sin(a) * R + D * 0.1, z + hh / 2))
                bw = W * 0.55 / n * 2.2
                blk = WPB("_t")
                strata_block(blk, "Slate", (bw * rnd.uniform(0.9, 1.2), D * 0.5, hh * rnd.uniform(1.0, 1.15)), (0, 0, 0), seed * 50 + i + int(z * 10),
                             cube=0.8, amp=0.1, tilt=rnd.uniform(-5, 5))
                merge_into(pb, blk, matrix=Matrix.Translation(c) @ Matrix.Rotation(a + math.pi / 2, 4, "Z"))
            z += hh * 0.92
    else:
        z = 0.0
        layer = 0
        while z < H - 0.4:
            if style == "columns":
                hh = H
            else:
                hh = rnd.uniform(H / 7, H / 4)
            x = -W / 2
            while x < W / 2:
                bw = rnd.uniform(W / 3.2, W / 1.7) if style != "columns" else rnd.uniform(W / 12, W / 8)
                bw = min(bw, W / 2 - x + 0.5)
                depth_off = rnd.uniform(-2.2, 2.2) * D / 14 + z * lean
                if style == "overhang" and z > H * 0.55:
                    depth_off -= (z - H * 0.55) * 0.35
                hcol = hh * rnd.uniform(0.82, 1.0) if style == "columns" else hh * rnd.uniform(1.0, 1.12)
                c = (x + bw / 2, depth_off + D * 0.12, z + hcol / 2)
                strata_block(pb, "Slate", (bw * 1.06, D * rnd.uniform(0.7, 0.85), hcol), c, seed * 100 + layer * 17 + int(x),
                             cube=0.8 if style != "columns" else 0.72, amp=0.09 if style != "columns" else 0.07,
                             tilt=rnd.uniform(-5, 5) if style != "columns" else 0.0)
                # moss on ledge tops
                if style != "columns" and rnd.random() < 0.35:
                    pb.rock("Moss", (bw * 0.8, D * 0.35, 0.6), loc=(c[0], c[1] - D * 0.22, z + hcol - 0.25), seed=seed + layer * 7 + int(x),
                            amp=0.1)
                x += bw
            z += hh * (0.94 if style != "columns" else 1.0)
            layer += 1
    # grassy / leafy lip on top
    for i in range(int(W / 5)):
        x = -W / 2 + (i + 0.5) * W / int(W / 5) + rnd.uniform(-1, 1)
        top = H + rnd.uniform(-0.4, 0.3)
        y = D * 0.1 + H * lean * 0.5
        if style == "corner":
            a = -math.pi / 2 + math.pi / 2 * (i + 0.5) / int(W / 5)
            x, y = math.cos(a) * W * 0.32 - W * 0.12, math.sin(a) * W * 0.32 + D * 0.1
        pb.rock("Moss", (rnd.uniform(4, 7), rnd.uniform(4, 6), 1.4), loc=(x, y, top - 0.6), seed=seed * 7 + i, amp=0.15)
        if rnd.random() < 0.45:
            s = rnd.uniform(2.0, 3.6)
            pb.rock(rnd.choice(("MapleRed", "Pumpkin", "Gold")), (s * 1.3, s * 1.2, s), loc=(x + rnd.uniform(-1, 1), y + 1.0, top + s * 0.1),
                    seed=seed * 11 + i, amp=0.18, flat_bottom=False, smooth=True)
    if style == "overhang":
        for i in range(6):   # hanging moss / ferns under the overhang
            x = rnd.uniform(-W * 0.4, W * 0.4)
            z = H * rnd.uniform(0.45, 0.6)
            pb.tube("Moss", [(x, -D * 0.1 - 2, z), (x + 0.3, -D * 0.1 - 2.4, z - 2.5), (x, -D * 0.1 - 2.6, z - 4.5)],
                    [0.7, 0.5, 0.15], 5)
    return pb


# ============================================================================ tower, village, mere, sky
def lantern_tower(name="old_lantern_tower"):
    rnd = random.Random(61)
    pb = WPB(name, tile_scale=1.0)
    H, R0, R1 = 30.0, 5.6, 4.6
    course = 1.6
    n = 10
    z = 0.0
    i = 0
    while z < H:
        r = R0 + (R1 - R0) * z / H
        for k in range(n):
            a = TAU * (k + 0.5 * (i % 2)) / n
            # ruin: the north-east side is broken away above ~20
            broken = z > 19 + 9 * (0.5 + 0.5 * math.cos(a - 0.6)) + rnd.uniform(-1.5, 1.5)
            if broken:
                continue
            w = TAU * r / n * 1.02
            pb.box(rnd.choice(("Slate", "Slate", "Limestone")), (w, 1.5, course * 0.96), loc=pol(a, r, z + course / 2),
                   rot=(0, 0, math.degrees(a) + 90), bevel=0.12)
        z += course
        i += 1
    pb.cyl("Slate", R0 - 0.8, R1 - 0.8, H - 2, 10, loc=(0, 0, (H - 2) / 2), smooth=False)   # inner fill
    pb.cyl("Slate", R0 + 1.2, R0 + 0.4, 1.4, 12, loc=(0, 0, 0.3), smooth=False)          # plinth
    # door + slit windows (glow)
    from props_hero import arch_poly, FRAME_Y
    a = -math.pi / 2
    rot = Matrix.Rotation(a + math.pi / 2, 4, "Z")
    mt = Matrix.Translation(pol(a, R0 + 0.55, 0.6)) @ rot @ FRAME_Y
    pb.prism("Oak", arch_poly(2.4, 2.2, 3.6, 0.0, 10), 0.4, matrix=mt)
    for k, (deg, z) in enumerate(((-90, 9), (30, 13), (150, 7), (-40, 17), (100, 15))):
        aa = math.radians(deg)
        r = R0 + (R1 - R0) * z / H + 0.5
        pb.box("Glow", (0.5, 0.25, 1.8), loc=pol(aa, r, z), rot=(0, 0, deg + 90))
    # timber lantern loft on the remaining wall + big lantern
    top = 25.5
    for k in range(4):
        aa = TAU * k / 4 + math.pi / 4
        pb.cyl("Oak", 0.35, 0.35, 9.0, 8, loc=pol(aa, 3.3, top + 4.5), smooth=False)
    pb.box("Oak", (8.0, 8.0, 0.6), loc=(0, 0, top), bevel=0.15)
    pb.cyl("Shingle", 6.4, 0.3, 4.0, 4, loc=(0, 0, top + 10.4), rot=(0, 0, 45), smooth=False)
    pb.lantern(5.5, loc=(0, 0, top + 2.6), paper="PaperOrange")
    pb.sphere("Glow", 1.4, loc=(0, 0, top + 4.6), segs=10, rings=6)
    # ivy / moss and rubble
    for k in range(10):
        aa = rnd.uniform(0, TAU)
        z = rnd.uniform(1, 20)
        r = R0 + (R1 - R0) * z / H + 0.6
        pb.rock("Moss", (rnd.uniform(2, 4), 1.0, rnd.uniform(2, 5)), loc=pol(aa, r, z), rot=(0, 0, math.degrees(aa) + 90),
                seed=600 + k, amp=0.2)
    for k in range(9):
        aa = rnd.uniform(0, TAU)
        s = rnd.uniform(1.0, 2.2)
        pb.rock(rnd.choice(("Slate", "Limestone")), (s, s * 0.9, s * 0.7), loc=pol(aa, R0 + rnd.uniform(1.5, 4), 0), seed=620 + k)
    return pb


def mushroom_village(name="hill_mushroom_houses"):
    import props_hero
    from props_p2p3 import mushroom
    pb = WPB(name, tile_scale=1.0)
    houses = [((-5.5, 3.5), 2.2, 20, {}), ((7.5, 5.0), 1.75, -40, {"ToadRed": "CapOrange"}),
              ((3.0, -8.0), 1.5, 160, {}), ((-9.0, -7.0), 1.25, 110, {"ToadRed": "CapGold"})]
    for (x, y), s, yaw, remap in houses:
        h = WPB("_h")
        props_hero.mushroom_house_medium(h)
        merge_into(pb, h, remap, Matrix.Translation((x, y, 0)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Scale(s, 4))
    rnd = random.Random(3)
    for k in range(9):
        a = rnd.uniform(0, TAU)
        r = rnd.uniform(9, 14)
        mushroom(pb, rnd.uniform(1.2, 2.6), rnd.uniform(0.6, 1.1), (math.cos(a) * r, math.sin(a) * r, 0),
                 cap=rnd.choice(("ToadRed", "CapOrange")), seed=k)
    # lantern string between the two big houses
    p0, p1 = Vector((-5.5, 3.5, 13.0)), Vector((7.5, 5.0, 11.0))
    pts = catenary(p0, p1, 2.0, 12)
    pb.tube("RootBark", pts, 0.08, 4, smooth=False)
    for i in range(2, 11, 2):
        pb.lantern(1.0, loc=pts[i] - Vector((0, 0, 1.1)), lod=1)
    # path stones + moss ground pads
    for k in range(12):
        a = rnd.uniform(0, TAU)
        r = rnd.uniform(0, 12)
        pb.rock("Slate", (1.6, 1.3, 0.4), loc=(math.cos(a) * r, math.sin(a) * r, -0.1), seed=700 + k, amp=0.1)
    return pb


def mere_dock(name="mere_dock"):
    """Long axis local X (14), shore end at +X, water end at -X; origin = deck-level reference (pos y 8.5)."""
    pb = WPB(name, tile_scale=1.0)
    deck_z = 0.75
    for i in range(14):
        x = -6.5 + i
        pb.box("Oak", (0.92, 4.4 + 0.2 * math.sin(i * 1.7), 0.22), loc=(x, 0, deck_z), rot=(0, 0, 0.8 * math.sin(i * 2.3)), bevel=0.04)
    for x in (-6.6, -2.2, 2.2, 6.0):
        for y in (-2.1, 2.1):
            pb.cyl("RootBark", 0.28, 0.32, 4.2, 8, loc=(x, y, deck_z - 1.6), smooth=False)
    for y in (-2.0, 2.0):
        pb.box("Oak", (14.0, 0.25, 0.3), loc=(0, y, deck_z - 0.3))
    for y in (-2.1, 2.1):   # end lantern posts
        pb.cyl("Oak", 0.18, 0.18, 2.6, 8, loc=(-6.6, y, deck_z + 1.3), smooth=False)
        pb.box("Oak", (0.9, 0.16, 0.16), loc=(-6.95, y, deck_z + 2.5))
        pb.lantern(0.9, loc=(-7.3, y, deck_z + 1.45), paper="PaperOrange" if y > 0 else "Paper")
    pb.torus("Oak", 0.45, 0.12, 12, 5, loc=(-4.8, 1.2, deck_z + 0.2))      # rope coil
    pb.box("Oak", (0.9, 0.9, 0.8), loc=(4.6, -1.2, deck_z + 0.5), bevel=0.06)   # crate
    return pb


def lantern_boat(name="mere_lantern_boat"):
    """Tiny paper boat with a lantern; origin = waterline centre. Bow = local -Z."""
    pb = WPB(name, tile_scale=1.0)
    secs = []
    for i in range(9):
        u = i / 8
        y = -3.0 + 6.0 * u
        w = 1.4 * math.sin(math.pi * (0.08 + 0.84 * u)) + 0.05
        lift = 0.5 * (abs(u - 0.5) * 2) ** 3
        secs.append([Vector((-w, y, 0.7 + lift)), Vector((-w * 0.75, y, -0.15 + lift * 0.5)),
                     Vector((w * 0.75, y, -0.15 + lift * 0.5)), Vector((w, y, 0.7 + lift))])
    pb.loft("Cream", secs, smooth=False)
    pb.box("Oak", (1.0, 1.0, 0.15), loc=(0, 0, 0.05))
    pb.lantern(1.6, loc=(0, 0, 0.12), hook=False, paper="PaperOrange")
    return pb


def sky_lantern(name="sky_lantern"):
    """Pass 4: smaller, rounder floating paper sky lantern 1.1 x 1.35 x 1.1 (was 1.5 x 2 x 1.5), glowing washi paper
    texture (SkyPaper, paper_glow.png, self-lit), thin rim and a flame (Glow) at the open bottom.
    Origin = bottom centre."""
    pb = WPB(name, tile_scale=1.0)
    pb.lathe("SkyPaper", [(0.36, 0.0), (0.47, 0.18), (0.55, 0.5), (0.55, 0.85), (0.46, 1.12), (0.27, 1.3),
                          (0.0, 1.35)], 12, smooth=True)
    pb.torus("RootBark", 0.36, 0.03, 12, 3, loc=(0, 0, 0.01))
    pb.sphere("Glow", 0.13, loc=(0, 0, 0.18), segs=6, rings=4)
    return pb


def cloud_card(name, seed, size=(600, 120, 200)):
    rnd = random.Random(seed)
    pb = WPB(name, tile_scale=1.0)
    W, H, D = size
    for k in range(13):
        u = (k + 0.5) / 13 - 0.5
        x = u * W * 0.8 + rnd.uniform(-20, 20)
        r = (0.55 - abs(u)) * H * rnd.uniform(1.1, 1.6) + 18
        z = r * 0.55 + rnd.uniform(-5, 10)
        pb.sphere("Cloud", r, loc=(x, rnd.uniform(-D * 0.2, D * 0.2), z), scale=(1.5, 0.9, 0.75), segs=14, rings=8)
    for k in range(7):
        x = rnd.uniform(-W * 0.42, W * 0.42)
        r = rnd.uniform(35, 60)
        pb.sphere("CloudShade", r, loc=(x, rnd.uniform(-D * 0.1, D * 0.15), r * 0.3), scale=(1.8, 1.0, 0.45), segs=12, rings=6)
    fit_bms([pb], size)
    return pb


# ============================================================================ tree line, far hills, mountains
TREELINE_MIXES = {
    "gold_orange": ("Gold", "Pumpkin", "Gold"),
    "red_orange": ("MapleRed", "Pumpkin", "MapleRed"),
    "red_gold": ("MapleRed", "Gold", "MapleRed"),
    "gold_green": ("Gold", "Moss", "Gold"),
}


def treeline_clump(name, variant, mix, size=(40, 45, 40)):
    rnd = random.Random({"a": 11, "b": 22, "c": 33}[variant])
    pals = TREELINE_MIXES[mix]
    pb = WPB(name, tile_scale=3.0)
    if variant == "a":      # 4 round crowns
        trees = [(-9, 4, 26, 3.0, 11), (8, -3, 30, 3.4, 12), (-1, 10, 22, 2.6, 10), (4, 8, 18, 2.2, 9)]
    elif variant == "b":    # 6 mixed, one tall spire
        trees = [(-12, 0, 24, 2.6, 9), (-4, -6, 34, 3.0, 9), (6, -2, 28, 3.0, 10), (12, 6, 20, 2.4, 9),
                 (-6, 9, 20, 2.4, 8.5), (2, 10, 40, 2.2, 6.5)]
    else:                   # 5 tall layered
        trees = [(-10, -2, 32, 2.6, 8), (-2, 4, 38, 2.8, 8.5), (8, -5, 30, 2.6, 8), (12, 7, 24, 2.2, 7.5),
                 (-6, 10, 26, 2.4, 8)]
    for k, (x, y, h, r, cr) in enumerate(trees):
        pb.tube("RootBark", [(x, y, -3), (x + 0.3, y, h * 0.5), (x, y + 0.3, h * 0.82)], [r * 1.25, r * 0.8, r * 0.45], 7,
                wobble=0.1, seed=k)
        layered = variant == "c" or (variant == "b" and k == 5)
        if layered:
            for t in range(4):
                z = h * 0.55 + t * h * 0.13
                rr = cr * (1.15 - t * 0.2)
                pb.rock(pals[(k + t) % 3], (rr * 2, rr * 2, rr * 1.1), loc=(x, y, z), seed=k * 10 + t, amp=0.16, ico=2,
                        flat_bottom=False, smooth=True)
        else:
            for t in range(4):
                a = TAU * t / 4 + k
                c = (x + math.cos(a) * cr * 0.55, y + math.sin(a) * cr * 0.55, h * 0.78 + (t == 0) * cr * 0.4)
                pb.rock(pals[(k + t) % 3], (cr * 1.4, cr * 1.4, cr * 1.15), loc=c, seed=k * 10 + t, amp=0.17, ico=2,
                        flat_bottom=False, smooth=True)
            pb.rock(pals[k % 3], (cr * 1.9, cr * 1.9, cr * 1.5), loc=(x, y, h * 0.86), seed=k * 10 + 9, amp=0.15, ico=3,
                    flat_bottom=False, smooth=True)
    # undergrowth
    for k in range(5):
        a = rnd.uniform(0, TAU)
        r = rnd.uniform(4, 14)
        s = rnd.uniform(4, 7)
        pb.rock(pals[k % 3], (s * 1.4, s * 1.2, s * 0.8), loc=(math.cos(a) * r, math.sin(a) * r, -0.5), seed=90 + k, amp=0.18,
                flat_bottom=True, smooth=True)
    fit_bms([pb], (size[0], size[1] + 3, size[2]), base_z=-3.0)
    return pb


def far_hill(name, variant, size=(280, 100, 160)):
    """Impostor hill shell: open-bottom dome (Moss/Pumpkin patches) studded with low-poly canopy bumps."""
    rnd = random.Random({"a": 5, "b": 9}[variant])
    pb = WPB(name, tile_scale=8.0)
    nx, ny = 36, 14
    W, D = 1.0, 1.0

    def hgt(u, v):
        if variant == "a":
            h = max(0.0, 1 - u * u) ** 0.8 * max(0.0, 1 - v * v) ** 0.6
        else:
            h = (0.75 * math.exp(-((u + 0.35) / 0.4) ** 2) + 1.0 * math.exp(-((u - 0.3) / 0.38) ** 2)) * max(0.0, 1 - u * u) ** 0.5
            h *= max(0.0, 1 - v * v) ** 0.6
        return h * (1 + 0.08 * noise.noise(Vector((u * 4, v * 4, rnd.random()))))
    grid = [[Vector((u * 0.5, v * 0.5, hgt(u, v))) for u in [-1 + 2 * i / nx for i in range(nx + 1)]]
            for v in [-1 + 2 * j / ny for j in range(ny + 1)]]
    mats = ("Pumpkin", "MapleRed", "Gold", "Moss")
    for j in range(ny):
        for i in range(nx):
            q = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
            n = noise.noise(Vector((i * 0.07, j * 0.12, 7.7)))
            mat = "Pumpkin" if n < 0.25 else "MapleRed"
            t = bmesh.new()
            vs = [t.verts.new(p) for p in q]
            t.faces.new(vs)
            pb.add(mat, t)
    # canopy bumps on the slopes
    for k in range(150):
        u, v = rnd.uniform(-0.92, 0.92), rnd.uniform(-0.85, 0.7)
        h = hgt(u, v)
        if h < 0.08:
            continue
        s = rnd.uniform(0.04, 0.07)
        pb.rock(rnd.choice(("MapleRed", "Gold", "Pumpkin", "Gold", "Moss")), (s, s * 1.6, s * 1.3 / 0.6), loc=(u * 0.5, v * 0.5, h - 0.015), seed=k, amp=0.2, ico=2,
                flat_bottom=False, smooth=False)
    fit_bms([pb], size)
    return pb


def mountain(name, variant, size=(500, 320, 300)):
    """Low-poly silhouette: jittered ridge heightfield. Pass 4 colours: foot = horizon haze (fades into the sky),
    hazy peach lower slopes, dusty mauve upper slopes, warm-white snowcaps on the peaks and up-facing high faces."""
    rnd = random.Random({"a": 1, "b": 2, "c": 3}[variant])
    pb = WPB(name, tile_scale=1.0)
    nx, ny = 22, 10
    peaks = {"a": [(-0.2, 1.0, 0.35), (0.35, 0.7, 0.3)], "b": [(0.0, 1.0, 0.25), (-0.5, 0.55, 0.3), (0.5, 0.6, 0.25)],
             "c": [(-0.35, 0.8, 0.3), (0.15, 1.0, 0.22), (0.6, 0.5, 0.25)]}[variant]

    def hgt(u, v):
        h = 0.0
        for (pu, ph, pw) in peaks:
            h = max(h, ph * max(0.0, 1 - abs(u - pu) / (pw * 2.2)) ** 1.3)
        h *= max(0.0, 1 - (abs(v) / 0.95) ** 2) ** 0.7
        return max(0.0, h * (1 + 0.12 * noise.noise(Vector((u * 5, v * 5, 3.3 + rnd.random())))))
    G = []
    for j in range(ny + 1):
        v = -1 + 2 * j / ny
        row = []
        for i in range(nx + 1):
            u = -1 + 2 * i / nx
            ju = rnd.uniform(-0.3, 0.3) / nx if 0 < i < nx else 0
            jv = rnd.uniform(-0.3, 0.3) / ny if 0 < j < ny else 0
            row.append(Vector(((u + ju) * 0.5, (v + jv) * 0.5, hgt(u + ju, v + jv))))
        G.append(row)
    for j in range(ny):
        for i in range(nx):
            q = [G[j][i], G[j][i + 1], G[j + 1][i + 1], G[j + 1][i]]
            for tri in ((q[0], q[1], q[2]), (q[0], q[2], q[3])):
                zc = sum(p.z for p in tri) / 3
                nrm = (tri[1] - tri[0]).cross(tri[2] - tri[0])
                facing_up = nrm.normalized().z if nrm.length > 0 else 0
                nz = 0.08 * noise.noise(Vector((sum(p.x for p in tri) * 9, sum(p.y for p in tri) * 9, 1.7)))
                z_ = zc + nz
                if z_ > 0.74 or (z_ > 0.58 and facing_up > 0.72):
                    mat = "MountainSnow"
                elif z_ > 0.42:
                    mat = "MountainMauve"
                elif z_ > 0.17:
                    mat = "MountainPeach"
                else:
                    mat = "MountainFoot"
                t = bmesh.new()
                vs = [t.verts.new(p) for p in tri]
                t.faces.new(vs)
                pb.add(mat, t)
    fit_bms([pb], size)
    return pb
