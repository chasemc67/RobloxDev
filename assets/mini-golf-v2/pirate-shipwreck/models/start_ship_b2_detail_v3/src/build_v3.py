# Start ship v3 detail pass (start_ship_b2_detail_v3).
# blender.exe -b --factory-startup source.blend --python build_v3.py -- <out_blend> <out_dir>
# Reads the approved v2_3 source.blend (NEVER saved over), edits Hull (bowsprit swap + hull plank recolour),
# rebuilds Rigging (broken main mast, crow's nest, torn sails), adds named Props, updates the packed palette,
# and saves out/start_ship_v3.blend. Collision, Ramps, empties, DeckCabin, Pier, RockBumper, Dressing(_Glow) untouched.
import bpy, bmesh, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import *
from mathutils import Vector
from mathutils.bvhtree import BVHTree

A = sys.argv[sys.argv.index('--') + 1:]; OUT_BLEND = A[0]; OUT_DIR = A[1]
SRC_PATH = bpy.data.filepath
assert os.path.abspath(OUT_BLEND) != os.path.abspath(SRC_PATH), 'refusing to overwrite source'
sc = bpy.context.scene; LOG = {'notes': []}
def note(*a):
    s = ' '.join(str(x) for x in a); print('NOTE', s); LOG['notes'].append(s)
rng = np.random.RandomState(1105)

# ------------------------------------------------------------------ palette: discover existing cells from UVs
img = bpy.data.images['start_ship_palette.png']; IW, IH = img.size
pix = np.array(img.pixels[:], dtype=np.float32).reshape(IH, IW, 4)
def cell_of_uv(u, v): return int(u * 8) + 8 * int((1 - v) * 8)
def cell_uv(i): return ((i % 8 + 0.5) / 8, 1 - (i // 8 + 0.5) / 8)
def cell_rgb(i):
    cx = (i % 8) * 32 + 16; cy = IH - ((i // 8) * 32 + 16) - 1; return [int(round(c * 255)) for c in pix[cy, cx, :3]]
CELL = {}
for ob in bpy.data.objects:
    if ob.type != 'MESH' or ob.name.startswith('COL'): continue
    me = ob.data; uvl = me.uv_layers.get('UVMap')
    for p in me.polygons:
        mn = me.materials[p.material_index].name; u, v = uvl.data[p.loop_start].uv; c = cell_of_uv(u, v)
        if mn in CELL and CELL[mn] != c: raise RuntimeError('inconsistent palette cell for ' + mn)
        CELL[mn] = c
for mn, c in CELL.items():
    rgb = list(bpy.data.materials[mn].get('rgb', [])); px = cell_rgb(c)
    if rgb != px: note('palette cell mismatch', mn, rgb, px)
note('existing cells', CELL)
NEW = dict(HullWood=(130, 90, 55), RopeLt=(190, 160, 110), Brass=(200, 160, 70), Barnacle=(115, 100, 92), Seaweed=(78, 118, 60),
           Gold=(236, 190, 72), Crab=(222, 98, 62), FishTeal=(72, 150, 146), Shadow=(42, 30, 22))
RECOLOR = dict(Canvas=(225, 210, 175), Red=(170, 60, 50))   # only used by Rigging / flag (not by ramps)
used = set(CELL.values()); free = [i for i in range(64) if i not in used]
def s2l(c):
    c = c / 255; return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def paint(i, rgb):
    x0 = (i % 8) * 32; y1 = IH - (i // 8) * 32; y0 = y1 - 32
    pix[y0:y1, x0:x0 + 32, 0] = rgb[0] / 255; pix[y0:y1, x0:x0 + 32, 1] = rgb[1] / 255; pix[y0:y1, x0:x0 + 32, 2] = rgb[2] / 255; pix[y0:y1, x0:x0 + 32, 3] = 1
MATS = {m.name: m for m in bpy.data.materials}
def set_mat_rgb(m, rgb):
    m['rgb'] = list(rgb); lin = (s2l(rgb[0]), s2l(rgb[1]), s2l(rgb[2]), 1.0); m.diffuse_color = lin
    bs = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'); bs.inputs['Base Color'].default_value = lin
for n, rgb in RECOLOR.items():
    old = list(MATS[n]['rgb']); set_mat_rgb(MATS[n], rgb); paint(CELL[n], rgb); note('recolour', n, old, '->', rgb)
for n, rgb in NEW.items():
    m = MATS['Wood'].copy(); m.name = n; set_mat_rgb(m, rgb); MATS[n] = m; CELL[n] = free.pop(0); paint(CELL[n], rgb)
tex_dir = os.path.join(OUT_DIR, 'textures'); os.makedirs(tex_dir, exist_ok=True)
tex_path = os.path.join(tex_dir, 'start_ship_palette.png')
_ni = bpy.data.images.new('_pal_new', IW, IH, alpha=False); _ni.pixels[:] = pix.ravel().tolist()
_ni.filepath_raw = tex_path; _ni.file_format = 'PNG'; _ni.save(); bpy.data.images.remove(_ni)
_new = bpy.data.images.load(tex_path); img.user_remap(_new); bpy.data.images.remove(img); _new.name = 'start_ship_palette.png'; _new.pack(); img = _new
_chk = np.array(img.pixels[:]).reshape(IH, IW, 4)
for n_, c_ in CELL.items():
    cx = (c_ % 8) * 32 + 16; cy = IH - ((c_ // 8) * 32 + 16) - 1; got = [int(round(v * 255)) for v in _chk[cy, cx, :3]]
    if got != list(MATS[n_]['rgb']): note('PALETTE VERIFY FAIL', n_, got, list(MATS[n_]['rgb']))
note('palette written + packed', tex_path)
PALETTE = {n: dict(cell=CELL[n], rgb=list(MATS[n]['rgb'])) for n in CELL}

# ------------------------------------------------------------------ mesh helpers
def mb_to_mesh(mb, me, recalc=True):
    slot = {m.name: i for i, m in enumerate(me.materials) if m}
    for n in mb.M:
        if n not in slot: me.materials.append(MATS[n]); slot[n] = len(me.materials) - 1
    bm = bmesh.new(); bm.from_mesh(me)
    uvl = bm.loops.layers.uv.get('UVMap') or bm.loops.layers.uv.new('UVMap')
    vs = [bm.verts.new(v) for v in mb.V]; newf = []; skipped = 0
    for f, m in zip(mb.F, mb.M):
        if len(set(f)) < 3: skipped += 1; continue
        try: face = bm.faces.new([vs[i] for i in f])
        except ValueError: skipped += 1; continue
        face.material_index = slot[m]; face.smooth = False; uv = cell_uv(CELL[m])
        for l in face.loops: l[uvl].uv = uv
        newf.append(face)
    bmesh.ops.remove_doubles(bm, verts=vs, dist=1e-5)
    newf = [f for f in newf if f.is_valid]
    if recalc and newf: bmesh.ops.recalc_face_normals(bm, faces=newf)
    bm.to_mesh(me); bm.free(); me.update()
    return skipped

def mesh_to_mb(me):
    out = MB(); out.V = [tuple(v.co) for v in me.vertices]; out.F = [list(p.vertices) for p in me.polygons]
    out.M = [me.materials[p.material_index].name for p in me.polygons]; return out

def solver_enum():
    return [i.identifier for i in bpy.types.BooleanModifier.bl_rna.properties['solver'].enum_items]

def mb_process(mb, bevel=None, cutters=(), force_mat=None, segs=2):
    me = bpy.data.meshes.new('_tmp'); mb_to_mesh(mb, me); ob = bpy.data.objects.new('_tmp', me); sc.collection.objects.link(ob); temps = []
    for i, cmb in enumerate(cutters):
        cme = bpy.data.meshes.new('_cut'); cmb2 = MB(); cmb2.V, cmb2.F, cmb2.M = cmb.V, cmb.F, ['Wood'] * len(cmb.F); mb_to_mesh(cmb2, cme)
        co = bpy.data.objects.new('_cut', cme); sc.collection.objects.link(co); co.hide_render = True; temps.append(co)
        md = ob.modifiers.new('cut%d' % i, 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = co
        sv = solver_enum(); md.solver = 'EXACT' if 'EXACT' in sv else sv[0]
    if bevel:
        md = ob.modifiers.new('bev', 'BEVEL'); md.width = bevel; md.segments = segs; md.limit_method = 'ANGLE'
        md.angle_limit = math.radians(35); md.use_clamp_overlap = True
    dg = bpy.context.evaluated_depsgraph_get(); m2 = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    out = mesh_to_mb(m2)
    if force_mat: out.M = [force_mat] * len(out.F)
    for o in temps + [ob]: d = o.data; bpy.data.objects.remove(o, do_unlink=True); bpy.data.meshes.remove(d)
    bpy.data.meshes.remove(m2); return out

COLL = bpy.data.collections.get('Props') or bpy.data.collections.new('Props')
if COLL.name not in sc.collection.children: sc.collection.children.link(COLL)
PROPS = {}
def make_prop(name, mb, pivot='base', bevel=None, note_txt='', segs=2):
    if bevel: mb = mb_process(mb, bevel=bevel, segs=segs)
    V = np.array(mb.V)
    if pivot == 'base': pv = np.array(((V[:, 0].min() + V[:, 0].max()) / 2, (V[:, 1].min() + V[:, 1].max()) / 2, V[:, 2].min()))
    elif pivot == 'origin': pv = np.zeros(3)
    else: pv = np.array(B(pivot))
    mb.V = [tuple(np.array(v) - pv) for v in mb.V]
    me = bpy.data.meshes.new(name); sk = mb_to_mesh(mb, me); ob = bpy.data.objects.new(name, me); ob.location = Vector(pv)
    COLL.objects.link(ob); ob['note'] = note_txt; PROPS[name] = ob
    note('PROP', name, 'tris', sum(len(p.vertices) - 2 for p in me.polygons), 'skipped', sk, 'pivot', [round(v, 2) for v in pv])
    return ob

# ------------------------------------------------------------------ HULL: remove straight bowsprit, recolour outer planks
hull = bpy.data.objects['Hull']; hme = hull.data
bm = bmesh.new(); bm.from_mesh(hme); bm.faces.ensure_lookup_table()
mi = {m.name: i for i, m in enumerate(hme.materials)}
b0 = np.array(BS0); b1 = np.array(BS1); bd = b1 - b0; bl = np.linalg.norm(bd); bdn = bd / bl
def hf(v): return untilt(Binv(v.co))
kill = []
for f in bm.faces:
    ok = True
    for v in f.verts:
        q = hf(v) - b0; t = np.dot(q, bdn)
        if t < -0.5 or t > bl + 0.5 or np.linalg.norm(q - t * bdn) > 1.95: ok = False; break
    if ok: kill.append(f)
note('bowsprit faces found', len(kill), [hme.materials[f.material_index].name for f in kill][:3])
assert len(kill) == 12, 'bowsprit face detection failed'
kv = set(v for f in kill for v in f.verts)
bmesh.ops.delete(bm, geom=kill, context='FACES_ONLY')
bmesh.ops.delete(bm, geom=[v for v in kv if v.is_valid and not v.link_faces], context='VERTS')
if 'HullWood' not in mi: hme.materials.append(MATS['HullWood']); mi['HullWood'] = len(hme.materials) - 1
uvl = bm.loops.layers.uv['UVMap']; rec = 0; X_BOW = X0 + 0.99 * L
for f in bm.faces:
    if hme.materials[f.material_index].name != 'Wood': continue
    c = untilt(Binv(f.calc_center_median())); x, y, z = c; outer = False
    if x < X0 + 0.3 or x > X_BOW - 0.5: outer = True
    else:
        b = bprof(x); h = hgt(x); tw = twf(x); bi = b - tw
        if y > h - 1.05: outer = abs(z) > b - 0.3          # stern-castle prisms: outer side face at |z| = b
        elif abs(z) > bi + 0.05: outer = True
        else:
            so = min(1, abs(z) / b); yo = y0skirt(x) + (h - y0skirt(x)) * so ** PW
            si = min(1, abs(z) / bi); yi = y0f(x) + tw + (h - y0f(x) - tw) * si ** PW
            outer = abs(y - yo) < abs(y - yi)
    if outer:
        f.material_index = mi['HullWood']; uv = cell_uv(CELL['HullWood'])
        for l in f.loops: l[uvl].uv = uv
        rec += 1
bm.to_mesh(hme); bm.free(); hme.update()
note('hull faces recoloured Wood->HullWood', rec)
LOG['hull'] = dict(bowsprit_tris_removed=12, recoloured_faces=rec)
# BVH of the hull skin (for placing hull-attached details)
bmh = bmesh.new(); bmh.from_mesh(hme); HBVH = BVHTree.FromBMesh(bmh); bmh.free()

def ray(o, d, dist=30.0):
    loc, nor, idx, dd = HBVH.ray_cast(Vector(B(o)), Vector(B(nrm(d))), dist)
    if loc is None: return None
    return Binv(loc), nrm(Binv(nor)), dd

def hull_hit(x, s):
    P = hull_outer_w(x, s); n = hull_normal_w(x, s); r = ray(P + n * 4, -n, 12)
    if r is None: note('hull_hit miss', x, s); return P, n
    p, fn, _ = r
    if np.dot(fn, n) < 0: fn = -fn
    return p, fn

def sframe(n, along=(1, 0, 0)):
    R = frame_from(n, along)
    if R[1, 1] < 0: R = frame_from(n, -np.asarray(along, float))
    return R

def offsets(p, n, R, pts2):
    out = []
    for a, b in pts2:
        q = p + R[:, 0] * a + R[:, 1] * b; r = ray(q + n * 4, -n, 12)
        out.append(4 - r[2] if r else None)
    return [o for o in out if o is not None]

def s_for_y(x, yt, side):
    ss = np.linspace(-1, 1, 4001); b = bprof(x); h = hgt(x); y0 = y0skirt(x)
    y = y0 + (h - y0) * np.abs(ss) ** PW; z = ss * b; yw = y * CP - z * SP; im = int(np.argmin(yw))
    if yw[im] > yt: return None
    if side > 0:
        k = im + int(np.argmax(yw[im:] >= yt)); return float(ss[k])
    seg = yw[:im + 1][::-1]; k = im - int(np.argmax(seg >= yt)); return float(ss[k])

# ------------------------------------------------------------------ HULL addition: upcurled bowsprit (hull frame)
bsp = MB('bowsprit')
d0 = nrm(np.array(BS1) - np.array(BS0)); Q = np.array(BS0) + d0 * (bl * 0.80)
left = np.array((-d0[1], d0[0], 0)); r0c = 7.0; Cc = Q + left * r0c; a0 = math.atan2(*(Q - Cc)[[1, 0]])
straight = [np.array(BS0) - d0 * 1.5 + d0 * (bl * 0.80 + 1.5) * t for t in np.linspace(0, 1, 7)]
curl = arc_path(Cc, r0c, 2.0, a0, a0 + math.radians(320), 16, (1, 0, 0), (0, 1, 0))[1:]
path = straight + curl
rad = list(np.linspace(1.8, 1.3, len(straight))) + list(np.linspace(1.3, 0.75, len(curl)))
bsp.tube(path, rad, 'Wood', sec=8, tf=tilt)
for xx in (150.0, 178.0):
    t = (xx - BS0[0]) / (d0[0]); pc = np.array(BS0) + d0 * t; rr = 1.8 - 0.5 * (t + 1.5) / (bl * 0.8 + 1.5)
    bsp.torus(pc, d0, rr + 0.05, 0.45, 'RopeLt', nu=10, nv=5, tf=tilt)
bsp.ellipsoid(curl[-1], (1.15, 1.15, 1.15), 'Brass', nu=8, nv=5, tf=tilt)
BS_ATTACH = tilt(Q); BS_MID = tilt(np.array(BS0) + d0 * 45)
note('bowsprit tris', bsp.tris(), 'attach', BS_ATTACH.round(2))
mb_to_mesh(mb_process(bsp, bevel=None), hme)

# ------------------------------------------------------------------ RIGGING rebuild (18 deg roll frame), same object/origin/name
rig = bpy.data.objects['Rigging']; rme = rig.data
bm = bmesh.new(); bm.to_mesh(rme); bm.free(); rme.materials.clear()
R_ = MB('rig')
def rotabout(p, c, Rm): return np.asarray(c) + Rm @ (np.asarray(p) - np.asarray(c))

def sail(x0, yy, ln, sh, rips=(), patches=(), tfx=None, nu=18, nv=12, bulge_k=0.13):
    tf = tfx or tiltR; bulge = bulge_k * sh
    def S(u, v):
        z = (u - 0.5) * ln * 0.88 * (1 - 0.06 * v); y = yy - 0.9 - v * sh
        x = x0 + 1.4 + bulge * math.sin(math.pi * u) * math.sin(math.pi * (0.1 + 0.85 * v)); return np.array((x, y, z))
    def fn(u, v, off=0.0):
        e = 1e-3; p = S(u, v); du = S(min(1, u + e), v) - S(max(0, u - e), v); dv = S(u, min(1, v + e)) - S(u, max(0, v - e))
        n = nrm(np.cross(dv, du));
        if n[0] < 0: n = -n
        return p + n * off, n
    sm = MB(); sm.thick_surface(lambda u, v: fn(u, v), nu, nv, 0.4, 'Canvas', tf=tf)
    cut = []
    for (u, v, r) in rips:
        p = S(u, v); c = MB(); c.frustum(p - np.array((8, 0, 0)), p + np.array((12, 0, 0)), r, r, 'Wood', sec=14, tf=tf, up=(0, 0, 1)); cut.append(c)
    sm = mb_process(sm, cutters=cut, force_mat='Canvas') if cut else sm
    for (ua, ub, va, vb) in patches:   # CanvasDk patch: 0.22 thick, back 0.1 inside the front face (+0.2) -> 0.12 proud
        pm = MB(); pm.thick_surface(lambda u, v: fn(ua + (ub - ua) * u, va + (vb - va) * v, 0.2 + 0.01), 4, 4, 0.22, 'CanvasDk', tf=tf); sm.extend(pm)
        pm = MB(); pm.thick_surface(lambda u, v: fn(ua + (ub - ua) * u, va + (vb - va) * v, -0.2 - 0.01), 4, 4, 0.22, 'CanvasDk', tf=tf); sm.extend(pm)
    return sm

def yard(x0, yy, ln, tf):
    R_.tube([(x0, yy, -ln / 2), (x0, yy, -ln * 0.3), (x0, yy, ln * 0.3), (x0, yy, ln / 2)], [0.5, 0.8, 0.8, 0.5], 'Post', sec=8, up=(1, 0, 0), tf=tf)
    for zz in (-ln / 2 + 0.6, ln / 2 - 0.6): R_.frustum((x0, yy, zz - 0.35), (x0, yy, zz + 0.35), 0.72, 0.72, 'Iron', sec=8, tf=tf, up=(1, 0, 0))

def nest(x0, yc, rr, wall_h, tf):
    R_.frustum((x0, yc - 0.9, 0), (x0, yc, 0), rr + 0.3, rr + 0.3, 'PostLt', sec=8, tf=tf, phase=math.pi / 8)
    side = 2 * rr * math.tan(math.pi / 8) + 0.5
    for k in range(8):
        a = 2 * math.pi * k / 8; c = np.array((x0 + rr * math.cos(a), yc + wall_h / 2 - 0.2, rr * math.sin(a)))
        Rm = Ry(-a)   # local x tangent, local z radial
        R_.box(c, (0.7, wall_h, side), 'Wood', R=Rm, tf=tf)
        R_.box(c + np.array((0, wall_h / 2 + 0.15, 0)), (1.2, 0.6, side + 0.2), 'WoodDk', R=Rm, tf=tf)
    for k in range(4):
        a = 2 * math.pi * k / 4 + math.pi / 4
        R_.tube([(x0 + 1.0 * math.cos(a), yc - 6.5, 1.0 * math.sin(a)), (x0 + (rr - 0.6) * math.cos(a), yc - 0.6, (rr - 0.6) * math.sin(a))], 0.4, 'WoodDk', sec=6, tf=tf)

# --- MAIN mast: snapped at ~2/3 (stump top y 106 of the original 165), tilted crow's nest, torn sails
MX = MAIN_X; TOPM = 106.0; r_top = 3.4 - 1.8 * (TOPM - 8) / 157
R_.frustum((MX, 8, 0), (MX, TOPM, 0), 3.4, r_top, 'Post', sec=10, tf=tiltR)
for yh in (40.0, 74.0):
    rh = 3.4 - 1.8 * (yh - 8) / 157 + 0.22; R_.frustum((MX, yh - 0.6, 0), (MX, yh + 0.6, 0), rh, rh, 'Iron', sec=10, tf=tiltR)
R_.frustum((MX, TOPM - 0.3, 0), (MX, TOPM + 0.3, 0), r_top - 0.25, r_top - 0.25, 'PostLt', sec=10, tf=tiltR)
for k, hgt_s in enumerate((5.5, 2.4, 4.2, 1.8, 6.8, 3.0, 2.2)):   # chunky splinter crown (pale fresh wood)
    a = 2 * math.pi * k / 7 + 0.3; rr = r_top * 0.55
    base = np.array((MX + rr * math.cos(a), TOPM - 1.0, rr * math.sin(a))); tip = base + np.array((0.5 * math.cos(a), hgt_s + 1.0, 0.5 * math.sin(a)))
    R_.frustum(base, tip, 1.05, 0.15, 'PostLt', sec=4, tf=tiltR)
NEST_Y = 96.0; NEST_TILT = Rz(math.radians(-11))     # tipped toward the bow (+X)
tf_nest = lambda p: tiltR(rotabout(p, (MX, NEST_Y, 0), NEST_TILT))
nest(MX, NEST_Y, 5.2, 3.8, tf_nest)
tf_main = tiltR
yard(MX, 62, 58, tf_main)
R_.extend(sail(MX, 62, 58, 30, rips=[(0.30, 0.45, 4.0), (0.34, 0.57, 3.1), (0.26, 0.35, 2.5), (0.38, 0.47, 2.3),
                                       (0.62, 1.03, 4.4), (0.71, 0.98, 3.1), (0.54, 1.01, 2.8),
                                       (0.83, 0.37, 2.8), (0.87, 0.45, 2.1), (0.80, 0.29, 1.7)],
               patches=[(0.56, 0.70, 0.14, 0.30)], tfx=tf_main))
SAG = Raxis((1, 0, 0), math.radians(-9)); tf_sag = lambda p: tiltR(rotabout(p, (MX, 86, 0), SAG))
yard(MX, 86, 44, tf_sag)
R_.extend(sail(MX, 86, 44, 20, rips=[(0.24, 1.02, 3.3), (0.40, 1.05, 2.6), (0.73, 1.0, 3.7), (0.60, 0.42, 2.4), (0.64, 0.50, 1.7)], tfx=tf_sag, nu=16, nv=10))
# --- FORE mast (intact, original height 126 so COL_Mast_Fore still matches)
FX = FORE_X
R_.frustum((FX, 8, 0), (FX, 126, 0), 2.8, 1.4, 'Post', sec=10, tf=tiltR)
for yh in (36.0, 70.0):
    rh = 2.8 - 1.4 * (yh - 8) / 118 + 0.22; R_.frustum((FX, yh - 0.6, 0), (FX, yh + 0.6, 0), rh, rh, 'Iron', sec=10, tf=tiltR)
R_.ellipsoid((FX, 126.6, 0), (1.7, 1.5, 1.7), 'Brass', nu=10, nv=6, tf=tiltR)
nest(FX, 100.8, 3.8, 2.6, tiltR)
yard(FX, 52, 46, tiltR); yard(FX, 84, 38, tiltR); yard(FX, 108, 28, tiltR)
R_.extend(sail(FX, 52, 46, 26, rips=[(0.66, 0.55, 3.2), (0.61, 0.63, 2.2), (0.70, 0.47, 1.8)], patches=[(0.22, 0.38, 0.24, 0.42)]))
R_.extend(sail(FX, 84, 38, 22, rips=[(0.30, 1.04, 2.4)], patches=[(0.58, 0.76, 0.48, 0.68)], nu=16, nv=10))
furl = [(FX + 1.0, 106.3, z) for z in np.linspace(-11.8, 11.8, 7)]
R_.tube(furl, [1.1, 1.5, 1.35, 1.6, 1.35, 1.5, 1.1], 'Canvas', sec=8, up=(1, 0, 0), tf=tiltR)
for zz in (-7.0, 0.0, 7.0): R_.torus((FX + 1.0, 106.3, zz), (0, 0, 1), 1.62, 0.35, 'RopeLt', nu=10, nv=5, tf=tiltR)
# --- ropes (RopeLt, 0.55 square-ish 6-sided lines)
def rope(p, q, r=0.3): R_.frustum(p, q, r, r, 'RopeLt', sec=6)
rope(tiltR((FX, 125, 0)), BS_ATTACH); rope(tiltR((FX, 110, 0)), BS_MID)
rope(tiltR((MX, 104, 0)), tiltR((FX, 118, 0))); rope(tiltR((MX, 104, 0)), tiltR((-150, 70, 0)))
for mx, yy in ((MX, 92.0), (FX, 84.0)):
    for sgn in (-1, 1):
        for dxx in (-6, 6):
            rope(tiltR((mx, yy, 0)), tilt((mx + dxx, hgt(mx + dxx) - 1, sgn * (bprof(mx + dxx) - 1.2))))
# a slack rope dangling from the broken nest (whimsy, hangs over the high side, well above the deck)
dang = [tf_nest((MX - 1.0 - 0.35 * k, NEST_Y - 0.5 - 2.6 * k + 0.12 * k * k, -5.6 - 0.25 * k)) for k in range(8)]
R_.tube(dang, 0.3, 'RopeLt', sec=6)
note('rigging tris', R_.tris())
mb_to_mesh(R_, rme)

# ------------------------------------------------------------------ PROP: flag (faded red, cream crossed-golf-clubs + ball emblem, no skull)
fl = MB('flag'); FY0, FY1 = 116.0, 125.0; FZ0, FZ1 = -1.0, -17.0
def flag_S(u, v):
    w = max(0.0, (u - 0.62) / 0.38); A_ = 1.5 * w * w * (3 - 2 * w)
    return np.array((FX + A_ * math.sin(2 * math.pi * (1.3 * u) + 0.6 + 0.8 * v), FY1 - v * (FY1 - FY0), FZ0 + u * (FZ1 - FZ0)))
def flag_fn(u, v):
    e = 1e-3; p = flag_S(u, v); du = flag_S(min(1, u + e), v) - flag_S(max(0, u - e), v); dv = flag_S(u, min(1, v + e)) - flag_S(u, max(0, v - e))
    n = nrm(np.cross(du, dv)); n = -n if n[0] < 0 else n; return p, n
fl.thick_surface(flag_fn, 16, 6, 0.4, 'Red', tf=tiltR)
notch = MB(); tri2 = [(FZ1 - 1.0, FY0 - 0.6), (FZ1 - 1.0, FY1 + 0.6), (FZ1 + 3.6, (FY0 + FY1) / 2)]
notch.loft([[np.array((FX - 4, y, z)) for z, y in tri2], [np.array((FX + 4, y, z)) for z, y in tri2]], 'Wood', tf=tiltR)
fl = mb_process(fl, cutters=[notch], force_mat='Red')
EC = np.array((FX, 120.8, -6.8))   # emblem centre (flat hoist half of the flag)
for sx in (-1, 1):
    px_ = 0.2 - 0.1 + 0.11   # emblem piece centre offset from flag mid-plane (0.22 thick: back 0.1 inside, 0.12 proud)
    for sgn in (-1, 1):
        a = math.radians(34) * sgn; dvec = np.array((0, math.cos(a), math.sin(a)))
        Rm = np.column_stack([(1, 0, 0), dvec, np.cross((1, 0, 0), dvec)])
        c0 = EC + np.array((sx * px_, 0.3, 0))
        fl.box(c0, (0.22, 6.2, 0.6), 'Canvas', R=Rm, tf=tiltR)                                # shaft
        fl.box(c0 + dvec * 3.0, (0.22, 1.3, 0.95), 'Canvas', R=Rm, tf=tiltR)                   # grip (top)
        bot = c0 - dvec * 3.1; fl.box(bot + np.array((0, -0.25, -sgn * 0.75)), (0.22, 0.95, 2.2), 'Canvas', tf=tiltR)   # club head (bottom, toe outward)
    fl.frustum(EC + np.array((sx * 0.1, -3.55, 0)), EC + np.array((sx * 0.32, -3.55, 0)), 1.05, 1.05, 'Canvas', sec=12, tf=tiltR, up=(0, 1, 0))   # golf ball between the heads
    fl.box(EC + np.array((sx * px_, -4.75, 0)), (0.22, 0.9, 0.5), 'Canvas', tf=tiltR)        # tee peg
make_prop('Prop_Flag', fl, pivot=tuple(tiltR((FX, FY0, FZ0))), note_txt='fore-mast flag, faded red; original emblem: two crossed golf clubs (grips up) over a golf ball on a tee (no skull)')

# ------------------------------------------------------------------ PROP: stern curl (taller curled stern; hull frame)
st = MB('stern'); h0 = hgt(X0); topT = h0 + CASTLE_H
S0 = np.array((X0 + 1.3, topT - 3.5, 0)); S1 = np.array((X0 + 0.2, topT + 12.0, 0))
lower = [S0 + (S1 - S0) * t for t in np.linspace(0, 1, 5)]
Csp = S1 + np.array((-8.0, 0, 0)); sp = arc_path(Csp, 8.0, 2.0, 0.0, math.radians(400), 26, (1, 0, 0), (0, 1, 0))[1:]
pth = lower + sp; n_ = len(pth)
rect = [(1.6 - 0.8 * i / (n_ - 1), 3.0 - 1.4 * i / (n_ - 1)) for i in range(n_)]
st.tube(pth, None, 'WoodDk', up=(0, 0, 1), rect=rect, tf=tilt)
st.ellipsoid(sp[-1], (1.9, 1.9, 2.0), 'Brass', nu=10, nv=6, tf=tilt)
for sgn in (-1, 1):   # corner volutes curling outboard
    zc = sgn * (bprof(X0) - 1.6); a = np.array((X0 + 1.0, topT - 2.5, zc)); b = np.array((X0 + 0.6, topT + 4.5, zc))
    low2 = [a + (b - a) * t for t in np.linspace(0, 1, 4)]
    cc = b + np.array((0, 0, sgn * 4.5)); ang0 = math.pi if sgn > 0 else 0.0
    sp2 = arc_path(cc, 4.5, 1.2, ang0, ang0 - sgn * math.radians(380), 16, (0, 0, 1), (0, 1, 0))[1:]
    p2 = low2 + sp2; m2 = len(p2)
    st.tube(p2, None, 'WoodDk', up=(1, 0, 0), rect=[(1.1 - 0.45 * i / (m2 - 1), 1.5 - 0.6 * i / (m2 - 1)) for i in range(m2)], tf=tilt)
    st.ellipsoid(sp2[-1], (1.0, 1.0, 1.0), 'Brass', nu=8, nv=5, tf=tilt)
# v3 artifact fix: the source DeckCabin deck-slab stern end face (x=-160, Y 22..24) is coplanar with the Hull stern cap and faces inward
# (renders as a black band on the transom). DeckCabin is a walking-surface mesh and is NOT edited; instead a proud WoodDk deck-line trim
# plank covers it on the outside of the transom (0.5 proud, 0.1 into the cap), matching the stern plank lines.
_he, _le = deck_edges(X0 + 2.0)
st.box((X0 - 0.2, DECK - 1.0, (_he + _le) / 2), (0.6, 2.9, (_le - _he) + 2.4), 'WoodDk')
note('stern deck-line trim covers z', round(_he - 1.2, 2), round(_le + 1.2, 2), 'Y', DECK - 2.45, DECK + 0.45)
make_prop('Prop_SternCurl', st, pivot=tuple(tilt((X0, topT - 3.5, 0))), bevel=0.18, note_txt='curled stern scroll + corner volutes on the transom top (hull 15 deg frame)')

# ------------------------------------------------------------------ PROP: grinning fish figurehead (hull frame)
fh = MB('fish'); T0 = np.array((153.0, 39.0, 0.0)); NZ = np.array((171.5, 45.8, 0.0)); ax = nrm(NZ - T0); flen = np.linalg.norm(NZ - T0)
eup = nrm(np.array((0, 1, 0)) - np.dot((0, 1, 0), ax) * ax); esd = np.cross(ax, eup)   # esd ~ +z
prof = [(0.0, 2.6, 2.0), (0.15, 3.6, 2.8), (0.35, 4.4, 3.4), (0.55, 4.6, 3.5), (0.75, 4.2, 3.2), (0.88, 3.3, 2.5), (0.96, 2.0, 1.5), (1.0, 0.8, 0.7)]
NS = 12
def fpt(t, th, out=0.0):
    tt = [p[0] for p in prof]; hv = np.interp(t, tt, [p[1] for p in prof]); hw = np.interp(t, tt, [p[2] for p in prof])
    return T0 + ax * flen * t + (hv + out) * math.sin(th) * eup + (hw + out) * math.cos(th) * esd
rings = [[fpt(t, 2 * math.pi * k / NS) for k in range(NS)] for t in [p[0] for p in prof]]
fh.loft(rings, lambda n: 'Canvas' if np.dot(n, eup) < -0.45 else 'FishTeal', tf=tilt)
for side in (1, -1):   # grin (Shadow lip tube) + cream teeth + eyes; mirrored
    def F(t, thd, out=0.0):
        th = math.radians(thd); th = th if side > 0 else math.pi - th; return fpt(t, th, out)
    mouth = [F(t, th, 0.05) for t, th in ((0.975, -78), (0.95, -60), (0.92, -44), (0.89, -30), (0.86, -16), (0.83, -4), (0.81, 6))]
    if side < 0: mouth = mouth[::-1]
    fh.tube(mouth, [0.42, 0.5, 0.52, 0.52, 0.5, 0.46, 0.4] if side > 0 else [0.4, 0.46, 0.5, 0.52, 0.52, 0.5, 0.42], 'Shadow', sec=6, tf=tilt)
    for t, th in ((0.935, -50), (0.895, -33), (0.855, -15)):
        p = F(t, th + 9, 0.25); nn = nrm(F(t, th + 9, 1.0) - F(t, th + 9, 0.0)); Rm = frame_from(nn, ax)
        fh.box(p, (0.8, 0.9, 0.7), 'Canvas', R=Rm, tf=tilt)
    pe = F(0.80, 38, 0.0); ne = nrm(F(0.80, 38, 1.0) - pe); Rm = frame_from(ne, ax)
    fh.ellipsoid(pe + ne * 0.25, (1.25, 0.9, 1.25), 'Canvas', R=Rm @ Rx(math.pi / 2), nu=10, nv=6, tf=tilt)
    fh.ellipsoid(pe + ne * 0.95 + ax * 0.25, (0.6, 0.4, 0.6), 'Iron', R=Rm @ Rx(math.pi / 2), nu=8, nv=5, tf=tilt)
    pf = F(0.6, -25, -0.3); nf = nrm(F(0.6, -25, 1.0) - F(0.6, -25, 0.0))   # pectoral fin (Brass)
    tri_ = [pf - ax * 0.4, pf - ax * 3.4 + nf * 2.2 - eup * 0.6, pf + ax * 0.9 + nf * 1.0]
    nn2 = nrm(np.cross(tri_[1] - tri_[0], tri_[2] - tri_[0])); fh.loft([[q - nn2 * 0.22 for q in tri_], [q + nn2 * 0.22 for q in tri_]], 'Brass', tf=tilt)
dor = [fpt(0.32, math.pi / 2, -0.5), fpt(0.42, math.pi / 2, 3.4) - ax * 1.6, fpt(0.70, math.pi / 2, -0.5)]
fh.loft([[q - esd * 0.3 for q in dor], [q + esd * 0.3 for q in dor]], 'Brass', tf=tilt)
make_prop('Prop_Figurehead', fh, pivot=tuple(tilt(T0)), bevel=0.12, note_txt='original grinning fish figurehead on the bow stem')

# ------------------------------------------------------------------ PROP: portholes (brass rims, dark glass) + transom windows
ph = MB('port'); PH_LIST = []
def porthole(p, n, R):
    ring = [(1.75 * math.cos(a), 1.75 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]] + [(0, 0)]
    of = offsets(p, n, R, ring); mx_, mn_ = max(of), min(of)
    ph.torus(p + n * (mx_ + 0.15), n, 1.75, 0.55, 'Brass', nu=12, nv=6)
    ph.frustum(p + n * (mn_ - 0.3), p + n * (mx_ + 0.14), 1.4, 1.4, 'Shadow', sec=12, up=tuple(R[:, 1]))
    PH_LIST.append(dict(at=list(np.round(p, 2)), surface_dev=round(mx_ - mn_, 3)))
for x in (-80.0, -40.0, 0.0, 40.0, 72.0):
    p, n = hull_hit(x, 0.865); porthole(p, n, sframe(n))
for zz in (-13.0, 13.0):
    o = tilt((X0 - 8, h0 + 3.0, zz)); r = ray(o, (1, 0, 0), 20); p, n = r[0], r[1]
    if n[0] > 0: n = -n
    porthole(p, n, sframe(n, tilt((0, 0, 1))))
make_prop('Prop_Portholes', ph, pivot='origin', note_txt='5 low-side brass portholes + 2 transom windows; proud relief, no openings')

# ------------------------------------------------------------------ PROP: cannons in decorative side ports (no hull opening)
cn = MB('cannon'); CN_LIST = []
for x in (-60.0, -20.0, 20.0):
    p, n = hull_hit(x, 0.64); R = sframe(n); u, v = R[:, 0], R[:, 1]
    of = offsets(p, n, R, [(a, b) for a in (-3.3, 0, 3.3) for b in (-3.3, 0, 3.3)]); back = min(of) - 0.15
    inner = offsets(p, n, R, [(a, b) for a in (-2.3, 0, 2.3) for b in (-2.3, 0, 2.3)])
    fd = max(1.1, max(of) + 0.6 - back)
    for c_, sz in ((v * 2.75, (6.6, 1.1)), (-v * 2.75, (6.6, 1.1)), (u * 2.75, (1.1, 4.4)), (-u * 2.75, (1.1, 4.4))):
        cn.box(p + c_ + n * (back + fd / 2), (sz[0], sz[1], fd), 'WoodDk', R=R)
    pt = max(0.5, max(inner) + 0.12 - back); cn.box(p + n * (back + pt / 2), (4.5, 4.5, pt), 'Shadow', R=R)
    hinge = p + v * 3.3 + n * (back + fd); aa = math.radians(58); dl = math.cos(aa) * v + math.sin(aa) * n; ln_ = -math.sin(aa) * v + math.cos(aa) * n
    Rl = np.column_stack([u, dl, ln_]); cn.box(hinge + dl * 2.6 + ln_ * 0.3, (5.8, 5.2, 0.6), 'Wood', R=Rl)
    for sx in (-1.6, 1.6): cn.box(hinge + dl * 2.6 + ln_ * 0.62 + u * sx, (0.6, 4.6, 0.3), 'Iron', R=Rl)
    d = nrm(np.array((n[0], 0.06, n[2]))); s0 = p + n * (back + 0.15)
    cn.tube([s0, s0 + d * 5.4, s0 + d * 6.6], [1.15, 0.92, 0.92], 'Iron', sec=10)
    cn.frustum(s0 + d * 5.3, s0 + d * 6.5, 1.3, 1.3, 'Iron', sec=10); cn.frustum(s0 + d * 6.45, s0 + d * 6.62, 0.62, 0.62, 'Shadow', sec=8)
    cn.frustum(s0 + d * 6.5, s0 + d * 6.7, 0.62, 0.62, 'Shadow', sec=8)
    CN_LIST.append(dict(x=x, port_centre=list(np.round(p, 2)), surface_dev=round(max(of) - min(of), 3), frame_depth=round(fd, 2)))
make_prop('Prop_Cannons', cn, pivot='origin', bevel=0.12, segs=1, note_txt='3 cannons in decorative proud port frames on the low side; the hull is NOT cut')

# ------------------------------------------------------------------ PROP: patch planks + oversized nails
pp = MB('patch')
for (x, s, k) in ((-40.0, 0.60, 3), (2.0, 0.58, 2), (58.0, 0.62, 3), (-30.0, -0.55, 3)):
    p, n = hull_hit(x, s); R = sframe(n)
    for i in range(k):
        L_ = 7.0 + rng.uniform(0, 2.2); off_u = rng.uniform(-0.8, 0.8); rot = math.radians(rng.uniform(-5, 5)); dv = (i - (k - 1) / 2) * 1.8
        Rr = R @ Rz(rot); c0 = p + R[:, 1] * dv + R[:, 0] * off_u
        of = offsets(c0, n, Rr, [(a, b) for a in (-L_ / 2, 0, L_ / 2) for b in (-0.75, 0.75)])
        back = min(of) - 0.15; th = max(0.55, max(of) + 0.2 - back)
        pp.box(c0 + n * (back + th / 2), (L_, 1.5, th), 'Wood', R=Rr)
        for e in (-1, 1):
            for b2 in (-0.38, 0.38):
                q = c0 + Rr[:, 0] * (e * (L_ / 2 - 0.7)) + Rr[:, 1] * b2
                pp.box(q + n * (back + th + 0.05), (0.75, 0.75, 0.6), 'Iron', R=Rr)
make_prop('Prop_PatchPlanks', pp, pivot='origin', bevel=0.1, segs=1, note_txt='patch planks with oversized nails on the hull sides')

# ------------------------------------------------------------------ PROP: chunky cap rails on the sheer (midships -> bow, both sides)
cr = MB('cap')
for sgn in (-1, 1):
    xs_ = list(np.arange(-64.0, 148.1, 4.0)); pts = []; rc = []
    for x in xs_:
        b = bprof(x); tw = twf(x); pts.append(np.array((x, hgt(x) + 0.35, sgn * (b - tw / 2)))); rc.append((tw / 2 + 0.5, 0.6))
    cr.tube(pts, None, 'Wood', up=(0, 1, 0), rect=rc, tf=tilt)
make_prop('Prop_CapRails', cr, pivot='origin', bevel=0.15, note_txt='rounded cap rail on the hull sheer, x -64..148 both sides')

# ------------------------------------------------------------------ PROP: barnacles + seaweed at the waterline
ba = MB('barn'); sw = MB('weed'); WL = []
for (x, side) in ((-152, 1), (-122, 1), (-96, 1), (-62, 1), (-28, 1), (8, 1), (38, 1), (66, 1), (-140, -1), (-78, -1), (-18, -1), (44, -1)):
    sv = s_for_y(x, WATER_Y + 0.9, side)
    if sv is None: continue
    p, n = hull_hit(x, sv); R = sframe(n); WL.append(dict(x=x, side=side, s=round(sv, 3), at=list(np.round(p, 2))))
    for j in range(int(rng.randint(4, 7))):
        a = rng.uniform(-2.6, 2.6); b = rng.uniform(-0.6, 1.6); q = p + R[:, 0] * a + R[:, 1] * b
        r = ray(q + n * 4, -n, 12)
        if r is None: continue
        q, nq, _ = r; nq = nq if np.dot(nq, n) > 0 else -nq; hh = rng.uniform(0.7, 1.15); r0_ = rng.uniform(0.7, 1.05)
        ba.frustum(q - nq * 0.35, q + nq * hh, r0_, r0_ * 0.45, 'Barnacle', sec=7)
        ba.frustum(q + nq * (hh - 0.12), q + nq * (hh + 0.1), r0_ * 0.28, r0_ * 0.28, 'Shadow', sec=6)
    if side > 0 or x < -100:
        for k in range(2):
            pts = []; x1 = x + 3.5 + 2.2 * k
            for j in range(6):
                yt = WATER_Y + 2.2 - j * 0.75; s2 = s_for_y(x1 + 0.6 * math.sin(j * 1.3 + k), yt, side)
                if s2 is None: break
                q, nq = hull_hit(x1 + 0.6 * math.sin(j * 1.3 + k), s2); pts.append(q + nq * 0.03)
            if len(pts) >= 3: sw.tube(pts, None, 'Seaweed', up=tuple(n), rect=(0.55, 0.14))
make_prop('Prop_Barnacles', ba, pivot='origin', note_txt='barnacle clusters along the waterline (world Y0 = local -0.6)')
make_prop('Prop_Seaweed', sw, pivot='origin', note_txt='seaweed ribbons crossing the waterline')

# ------------------------------------------------------------------ deck props (all bottoms 0.1 below the deck top Y=24 -> no coplanar faces)
DB = DECK - 0.1
def barrel(mb, c, r, h, axis_y=True, R=None):
    c = np.asarray(c, float); R = np.eye(3) if R is None else R
    P = lambda y: c + R @ np.array((0, y, 0))
    mb.tube([P(0), P(h * 0.5), P(h)], [r * 0.86, r, r * 0.86], 'Wood', sec=10, up=tuple(R @ np.array((1, 0, 0))))
    for yy in (0.18, 0.82):
        rr = r * (0.86 + 0.14 * (1 - abs(2 * yy - 1))) + 0.04; rh = max(r * (0.86 + 0.14 * (1 - abs(2 * (yy - 0.05) - 1))), r * (0.86 + 0.14 * (1 - abs(2 * (yy + 0.05) - 1)))) + 0.14
        mb.frustum(P(h * yy - 0.25), P(h * yy + 0.25), rh, rh, 'Iron', sec=10, up=tuple(R @ np.array((1, 0, 0))))
    mb.frustum(P(h - 0.15), P(h + 0.15), r * 0.62, r * 0.62, 'WoodDk', sec=10, up=tuple(R @ np.array((1, 0, 0))))
def crate(mb, c, s, yaw):
    c = np.asarray(c, float); R = Ry(math.radians(yaw)); hs = s / 2
    mb.box(c, (s, s, s), 'PostLt', R=R)
    for sx in (-1, 1):
        for sz in (-1, 1): mb.box(c + R @ np.array((sx * (hs - 0.3), 0, sz * (hs - 0.3))), (0.9, s + 0.1, 0.9), 'WoodDk', R=R)
    mb.box(c, (s + 0.3, 0.8, s + 0.3), 'WoodDk', R=R)
    for fz in (-1, 1):
        mb.box(c + R @ np.array((0, 0, fz * (hs + 0.05))), (s * 1.1, 0.7, 0.4), 'WoodDk', R=R @ Rz(math.radians(45 * fz)))
cg = MB('cargo')
barrel(cg, (-104.6, DB, 27.4), 2.3, 5.0); barrel(cg, (-100.0, DB, 28.0), 2.15, 4.6)
barrel(cg, (-101.3, DB + 1.95, 31.9), 1.95, 4.4, R=Rz(math.radians(90)) @ Ry(math.radians(8)))
crate(cg, (-96.4, DB + 2.3, 27.9), 4.6, 8); CRATE2_TOP = DB + 4.6 - 0.1 + 3.2
crate(cg, (-96.6, DB + 4.6 - 0.1 + 1.6, 27.7), 3.2, -14)
make_prop('Prop_CargoCluster', cg, bevel=0.14, segs=1, note_txt='barrels + crates against the cabin front wall, east of the door (out of the door/tee corridor)')
# crab on the top crate (gag)
cb = MB('crab'); CC0 = np.array((-96.6, CRATE2_TOP - 0.15, 27.7))
cb.ellipsoid(CC0 + np.array((0, 0.75, 0)), (1.8, 0.95, 1.4), 'Crab', nu=12, nv=6)
for sz in (-1, 1):
    st0 = CC0 + np.array((1.0, 1.4, sz * 0.5)); cb.frustum(st0, st0 + np.array((0.25, 1.0, 0)), 0.16, 0.16, 'Crab', sec=6)
    e = st0 + np.array((0.3, 1.25, 0)); cb.ellipsoid(e, (0.42, 0.42, 0.42), 'Canvas', nu=8, nv=5); cb.ellipsoid(e + np.array((0.33, 0.05, 0)), (0.2, 0.22, 0.22), 'Iron', nu=6, nv=4)
    for k in range(3):
        xk = -0.9 + 0.8 * k; a = CC0 + np.array((xk, 0.6, sz * 1.1)); b = CC0 + np.array((xk - 0.2, 0.75, sz * 2.1)); c_ = CC0 + np.array((xk - 0.35, 0.05, sz * 2.5))
        cb.tube([a, b, c_], 0.15, 'Crab', sec=5)
    raised = sz > 0
    sh_ = CC0 + np.array((1.2, 0.9, sz * 1.0)); el = sh_ + (np.array((0.9, 1.6, sz * 1.0)) if raised else np.array((1.3, 0.1, sz * 0.7)))
    cl = el + (np.array((0.5, 1.3, sz * 0.3)) if raised else np.array((1.0, 0.2, sz * 0.2)))
    cb.tube([sh_, el, cl], 0.26, 'Crab', sec=6)
    Rm = frame_from(cl - el, (0, 1, 0)); cb.ellipsoid(cl + nrm(cl - el) * 0.55, (0.55, 0.42, 0.75), 'Crab', R=Rm, nu=8, nv=5)
    cb.ellipsoid(cl + nrm(cl - el) * 0.75 + Rm[:, 0] * 0.55, (0.3, 0.3, 0.6), 'Crab', R=Rm, nu=6, nv=4)
make_prop('Prop_Crab', cb, note_txt='tiny crab waving one claw on the cargo crates')

# door lantern (kit style: Iron caps, Brass posts, Glow core) on the cabin front wall EAST of the door, above head height
LX = -107.5; LZ_W = CAB['z1']; LY = DECK + 9.0
ln = MB('lantern'); lg = MB('lantern_glow')
ln.box((LX, LY + 3.4, LZ_W + 0.1), (1.8, 2.4, 0.6), 'WoodDk')                       # wall back plate (0.4 proud)
ln.tube([(LX, LY + 3.4, LZ_W + 0.2), (LX, LY + 3.4, LZ_W + 2.6), (LX, LY + 2.6, LZ_W + 2.9)], 0.22, 'Iron', sec=6)
ln.box((LX, LY - 0.2, LZ_W + 2.9), (2.4, 0.5, 2.4), 'Iron'); ln.box((LX, LY + 2.25, LZ_W + 2.9), (2.6, 0.5, 2.6), 'Iron')
ln.frustum((LX, LY + 2.45, LZ_W + 2.9), (LX, LY + 3.1, LZ_W + 2.9), 1.3, 0.35, 'Iron', sec=4, phase=math.pi / 4)
for sx in (-1, 1):
    for sz in (-1, 1): ln.box((LX + sx * 0.95, LY + 1.0, LZ_W + 2.9 + sz * 0.95), (0.35, 2.3, 0.35), 'Brass')
lg.box((LX, LY + 1.0, LZ_W + 2.9), (1.7, 2.1, 1.7), 'Glow')
make_prop('Prop_DoorLantern', ln, bevel=0.06, segs=1, note_txt='kit lantern on the cabin front wall, 12.5 studs east of the door centre, bottom 8.6 above the deck')
make_prop('Prop_DoorLantern_Glow', lg, note_txt='lantern glow core (same convention as Dressing_Glow)')

# stern wheel (helm) on deck just forward of the cabin's +X wall
wh = MB('wheel'); WX, WZ, WY = -80.5, 10.5, DECK + 7.0
wh.box((WX + 1.2, DB + 3.4, WZ), (1.8, 6.8, 2.4), 'WoodDk'); wh.box((WX + 1.2, DB + 0.35, WZ), (3.2, 0.7, 3.6), 'WoodDk')
wh.frustum((WX - 0.9, WY, WZ), (WX + 1.0, WY, WZ), 0.45, 0.45, 'Iron', sec=8, up=(0, 1, 0))
wh.frustum((WX - 0.9, WY, WZ), (WX - 0.1, WY, WZ), 1.0, 1.0, 'Brass', sec=10, up=(0, 1, 0))
rim = [np.array((WX - 0.5, WY + 4.2 * math.cos(a), WZ + 4.2 * math.sin(a))) for a in np.linspace(0, 2 * math.pi, 17)]
wh.tube(rim, None, 'Wood', up=(1, 0, 0), rect=(0.42, 0.45), caps=False)
for k in range(8):
    a = 2 * math.pi * k / 8 + math.pi / 8; d_ = np.array((0, math.cos(a), math.sin(a)))
    c0 = np.array((WX - 0.5, WY, WZ)); wh.frustum(c0 + d_ * 0.8, c0 + d_ * 4.4, 0.3, 0.3, 'Wood', sec=6)
    wh.frustum(c0 + d_ * 4.4, c0 + d_ * 6.0, 0.42, 0.3, 'WoodDk', sec=6)
make_prop('Prop_SternWheel', wh, bevel=0.08, segs=1, note_txt="ship's wheel on a pedestal, deck forward of the cabin")

# treasure chest peeking open with gold, on the high side of the deck
HI_, LO_ = deck_edges(-48.0); CX, CZ = -48.0, HI_ + 7.5; yaw = math.radians(18); Rc = Ry(yaw)
ch = MB('chest'); cw, chh, cd = 6.4, 3.4, 4.0
def cp(lx, ly, lz): return np.array((CX, DB, CZ)) + Rc @ np.array((lx, ly, lz))
ch.box(cp(0, chh / 2, 0), (cw, chh, cd), 'Wood', R=Rc)
for bx in (-2.4, 0.0, 2.4): ch.box(cp(bx, (chh - 0.4) / 2 - 0.05, 0), (0.6, chh - 0.4, cd + 0.3), 'Brass', R=Rc)
ch.box(cp(0, chh - 0.9, cd / 2 + 0.1), (1.2, 1.4, 0.5), 'Brass', R=Rc)
hinge = np.array((0, chh, -cd / 2)); Rlid = Rx(math.radians(-42))   # opened about the back-top hinge
def lid_ring(xx, sc_=1.0):
    pts = []
    for a in np.linspace(0, math.pi, 7):
        lz = -cd / 2 * math.cos(a) * sc_; ly = (cd / 2) * 0.8 * math.sin(a) * sc_
        pts.append(np.array((xx, ly, lz)))
    return pts
def lid_xf(q):
    q = np.asarray(q, float) + np.array((0, chh, 0)); return cp(*(hinge + Rlid @ (q - hinge)))
ch.loft([[lid_xf(q) for q in lid_ring(-cw / 2)], [lid_xf(q) for q in lid_ring(cw / 2)]], 'Wood')
for bx in (-2.4, 0.0, 2.4):
    ch.loft([[lid_xf(q) for q in lid_ring(bx - 0.3, 1.06)], [lid_xf(q) for q in lid_ring(bx + 0.3, 1.06)]], 'Brass')
ch.ellipsoid(cp(0, chh - 0.1, 0.2), (2.7, 1.3, 1.6), 'Gold', R=Rc, nu=12, nv=6)
for (lx, lz, tl) in ((2.5, 3.2, 12), (-1.0, 3.6, -8), (0.8, 4.4, 5), (3.6, 2.6, 15)):
    q = cp(lx, 0, lz); ch.frustum(q + np.array((0, 0.0, 0)), q + np.array((0, 0.32, 0)), 0.7, 0.7, 'Gold', sec=10)
make_prop('Prop_TreasureChest', ch, bevel=0.1, note_txt='treasure chest, lid ajar, gold peeking; on the high side of the main deck')

# rope coils
rc_ = MB('coils')
def coil(c, R0=2.0, n=3):
    c = np.asarray(c, float)
    rc_.frustum(c + np.array((0, -0.1, 0)), c + np.array((0, 0.55, 0)), R0 - 0.2, R0 - 0.2, 'RopeLt', sec=12)
    for k in range(n): rc_.torus(c + np.array((0.1 * k, 0.45 + 0.78 * k, -0.08 * k)), (0, 1, 0), R0 - 0.12 * k, 0.45, 'RopeLt', nu=14, nv=6)
    e0 = c + np.array((R0 + 0.1, 0.45, 0)); rc_.tube([e0, e0 + np.array((1.4, -0.05, 0.9)), e0 + np.array((2.6, -0.06, 0.4)), e0 + np.array((3.4, -0.07, 1.4))], 0.42, 'RopeLt', sec=6)
coil((-90.0, DB, 36.0)); coil((20.0, DB, 19.0), 2.3)
FCXX = 140.0
while deck_edges(FCXX) is None or (deck_edges(FCXX)[1] - deck_edges(FCXX)[0]) < 16: FCXX -= 2.0
FCH, FCL = deck_edges(FCXX); FCZ = (FCH + FCL) / 2 - 4.0; coil((FCXX, FT - 0.1, FCZ), 1.8, 2)
note('forecastle coil', FCXX, FCZ, 'deck edges', FCH, FCL, 'bitt z', tilt((132.0, 45 + 14 * 0.2577, 0))[2])
note('deck edges at -90', deck_edges(-90.0), 'at 20', deck_edges(20.0), 'at -100', deck_edges(-100.0))
make_prop('Prop_RopeCoils', rc_, pivot='origin', note_txt='three chunky rope coils (deck x-90 / mast base / forecastle)')


# ------------------------------------------------------------------ PROP: inner bulwark frames (ribs) + high-side stringers (scenery walls only, not walk surfaces)
bf = MB('frames'); FR = []
def inner_hit(x, y, side):
    he, le = deck_edges(x); zm = (he + le) / 2; r = ray(np.array((x, y, zm)), (0, 0, side), 80)
    if r is None: return None
    p, n, _ = r
    if n[2] * side > 0: n = -n          # face the ship centre
    return p, n
for side, xr in ((-1, np.arange(-84.0, 113.0, 14.0)), (1, np.arange(-84.0, 113.0, 14.0))):
    for x in xr:
        pts = []
        for y in np.arange(23.5, 70.0, 2.5):
            h_ = inner_hit(x, y, side)
            if h_ is None: break
            p, n = h_; pts.append(p + n * 0.2)
        if len(pts) >= 3:
            bf.tube(pts, None, 'WoodDk', up=(1, 0, 0), rect=(0.55, 0.4)); FR.append(dict(x=float(x), side=side, top=round(float(pts[-1][1]), 2)))
for yy in (33.0, 41.0):
    pts = []
    for x in np.arange(-86.0, 110.1, 4.0):
        h_ = inner_hit(x, yy, -1)
        if h_ is not None: p, n = h_; pts.append(p + n * 0.42)
    if len(pts) > 3: bf.tube(pts, None, 'Wood', up=(0, 1, 0), rect=(0.4, 0.5))
make_prop('Prop_BulwarkFrames', bf, pivot='origin', note_txt='dark wood ribs on the inner bulwarks (both sides) + two stringers on the high side; deck surface untouched')
# ------------------------------------------------------------------ PROP: cabin round windows (brass rims, dark glass, mullions)
cwn = MB('cabwin'); ZF = CAB['z1']; XE = CAB['x1']
def cab_window(c, n, up):
    c = np.asarray(c, float); n = nrm(n); R = frame_from(n, np.cross(up, n))
    cwn.torus(c + n * 0.3, n, 2.0, 0.5, 'Brass', nu=14, nv=6)
    cwn.frustum(c - n * 0.3, c + n * 0.15, 1.7, 1.7, 'Shadow', sec=14, up=tuple(up))
    for k in (0, 1): cwn.box(c + n * 0.25, (3.5, 0.4, 0.3) if k == 0 else (0.4, 3.5, 0.3), 'WoodDk', R=R)
for (x, y) in ((-139.0, 32.0), (-93.0, 35.0)): cab_window((x, y, ZF), (0, 0, 1), np.array((0, 1.0, 0)))
for (z, y) in ((-6.0, 31.5), (11.0, 31.5)): cab_window((XE, y, z), (1, 0, 0), np.array((0, 1.0, 0)))
make_prop('Prop_CabinWindows', cwn, pivot='origin', note_txt='round cabin windows (front wall + bow-facing end wall), proud relief, wall not cut')

LOG['placements'] = dict(frames=FR, portholes=PH_LIST, cannons=CN_LIST, waterline=WL, chest=[CX, DECK, CZ], deck_edges_at_chest=[HI_, LO_],
                         forecastle_coil=[FCXX, FT, FCZ], lantern=[LX, LY, LZ_W], wheel=[WX, WY, WZ], bowsprit_attach=list(BS_ATTACH))
LOG['palette'] = PALETTE
sc['start_ship_version'] = 'start_ship_b2_detail_v3'; sc['source_blend'] = SRC_PATH
json.dump(LOG, open(os.path.join(OUT_DIR, 'logs', 'build_log.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=True, copy=True)
print('BUILD_OK', OUT_BLEND)
