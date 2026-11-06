# Start ship whimsy v5 -> v5_1 ART CORRECTIONS (visual-only pass, Nov 5 2026).
# "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup <abs>\source_v5.blend --python build_v5_1.py -- <abs out_blend> <abs out_dir>
# Opens source_v5.blend (NEVER saved over: save_as copy to a different path, asserted) and edits in memory. Every existing object keeps its
# NAME and ORIGIN (matrix_world asserted identical at save); only mesh vertices / rebuilt mesh data change.
#   1a Hull belly: extra smooth horizontal "roundness" bulge about the heeled centreline (sin^2 hump, peak world Y3, 0 at Y-8 and >=Y14), same x-taper
#      as v5; applied to Hull + the same hull-hugging meshes v5 warped. Deck (Y24) / DeckCabin / ramps untouched.
#   1b ShipV5_SheerRise rebuilt (same object/origin): bow rise 4 -> 7 studs at the stem; transom crest corners 1.6 -> 4.6, centre 4 -> 7;
#      NEW stern side rise boards on the stern-castle tops (0 -> 4.6 toward the transom). Exterior only.
#   1c ShipV5_SternCurl: vertices scaled 1.8x about its own crest base, lifted +3 with the crest (same object/origin/topology).
#   2  ShipV5_BowEyes rebuilt (same object/origin): ~2x eyes, higher on the bow flanks, cream sclera + big dark pupils + thick droopy lid plank.
#   3  Prop_Figurehead rebuilt (same object/origin): octopus ~1.6x, Coral (230,120,100) top + CoralDk (180,80,70) underside, big eyes + grin.
#   4  ShipV5_Patches rebuilt (same object/origin): 4 large (~2.7x linear) blue/teal patches high on the visible low (+Z) side, chunky brass nails.
#   5  Tee visual read: Prop_SternWheel, Prop_TreasureChest, Prop_RopeCoils (tee coil only), Prop_CargoCluster (barrels only; crab crate stays)
#      -> MESH vertices moved/rotated in world space and written back in local space; object origins untouched.
#   Collision collection: NOT touched (asserted). DeckCabin + 3 ramps: asserted byte-identical. Sails/emblem/flag/zigzag mast/crab/lantern untouched.
import bpy, bmesh, sys, os, json, math, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import *
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

A = sys.argv[sys.argv.index('--') + 1:]; OUT_BLEND = os.path.abspath(A[0]); OUT_DIR = os.path.abspath(A[1])
SRC_PATH = os.path.abspath(bpy.data.filepath)
assert OUT_BLEND != SRC_PATH and os.path.basename(OUT_BLEND) != 'source_v5.blend', 'refusing to overwrite source'
os.makedirs(os.path.join(OUT_DIR, 'logs'), exist_ok=True)
sc = bpy.context.scene; LOG = {'notes': [], 'changes': {}, 'skipped': []}
def note(*a):
    s = ' '.join(str(x) for x in a); print('NOTE', s); LOG['notes'].append(s)
def smooth(t): t = min(1.0, max(0.0, t)); return t * t * (3 - 2 * t)

# ------------------------------------------------------------------ fingerprints (collision + locked + untouched + origins)
def mesh_hash(o, world=False):
    h = hashlib.sha256(); me = o.data; n = len(me.vertices); co = np.zeros(n * 3, np.float32); me.vertices.foreach_get('co', co); h.update(co.tobytes())
    lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv); h.update(lv.tobytes())
    if me.uv_layers:
        uv = np.zeros(len(me.loops) * 2, np.float32); me.uv_layers[0].data.foreach_get('uv', uv); h.update(uv.tobytes())
    mi = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi); h.update(mi.tobytes())
    h.update(('|'.join(m.name for m in me.materials if m)).encode())
    h.update(np.array([v for r in o.matrix_world for v in r], np.float64).tobytes()); return h.hexdigest()
def col_hash():
    h = hashlib.sha256()
    for o in sorted(bpy.data.collections['Collision'].objects, key=lambda o: o.name): h.update(o.name.encode()); h.update(mesh_hash(o).encode())
    return h.hexdigest()
COL0 = col_hash()
LOCKED = ['DeckCabin', 'RampFlight1', 'RampLanding', 'RampFlight2']
KEEP = ['ShipV5_SailEmblem', 'Prop_Flag', 'ShipV5_MastZigzag', 'Prop_Crab', 'Prop_DoorLantern', 'Prop_DoorLantern_Glow', 'ShipV5_SailPatches', 'Prop_SternCurl',
        'Pier', 'RockBumper', 'Dressing', 'Dressing_Glow']
H0 = {n: mesh_hash(bpy.data.objects[n]) for n in LOCKED + KEEP}
MW0 = {o.name: [list(r) for r in o.matrix_world] for o in bpy.data.objects}
MESHNAME0 = {o.name: o.data.name for o in bpy.data.objects if o.type == 'MESH'}

# ------------------------------------------------------------------ palette (8x8 cells of 32 px, discovered from UVs as in build_v5)
img = bpy.data.images['start_ship_palette.png']; IW, IH = img.size
pix = np.array(img.pixels[:], dtype=np.float32).reshape(IH, IW, 4)
CS = IW // 8
def cell_of_uv(u, v): return int(u * 8) + 8 * int((1 - v) * 8)
def cell_uv(i): return ((i % 8 + 0.5) / 8, 1 - (i // 8 + 0.5) / 8)
CELL = {}
for ob in bpy.data.objects:
    if ob.type != 'MESH' or ob.name.startswith('COL'): continue
    me = ob.data; uvl = me.uv_layers.get('UVMap')
    for p in me.polygons:
        mn = me.materials[p.material_index].name; u, v = uvl.data[p.loop_start].uv; c = cell_of_uv(u, v)
        if mn in CELL and CELL[mn] != c: raise RuntimeError('inconsistent palette cell for ' + mn)
        CELL[mn] = c
def s2l(c):
    c = c / 255; return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def paint(i, rgb):
    x0 = (i % 8) * CS; y1 = IH - (i // 8) * CS; y0 = y1 - CS
    for k in range(3): pix[y0:y1, x0:x0 + CS, k] = rgb[k] / 255
    pix[y0:y1, x0:x0 + CS, 3] = 1
MATS = {m.name: m for m in bpy.data.materials}
def set_mat_rgb(m, rgb):
    m['rgb'] = list(rgb); lin = (s2l(rgb[0]), s2l(rgb[1]), s2l(rgb[2]), 1.0); m.diffuse_color = lin
    bs = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'); bs.inputs['Base Color'].default_value = lin
NEWMATS = {'CoralDk': (180, 80, 70)}
free = [i for i in range(64) if i not in set(CELL.values())]
for (nm, rgb), ci in zip(NEWMATS.items(), free):
    m = MATS['Coral'].copy(); m.name = nm; set_mat_rgb(m, rgb); MATS[nm] = m; CELL[nm] = ci; paint(ci, rgb)
    note('new material', nm, rgb, 'palette cell', ci)
for k, rgb in (('Coral', [230, 120, 100]), ('PatchBlue', [90, 130, 170]), ('PatchTeal', [70, 150, 140]), ('Brass', [200, 160, 70])):
    assert list(MATS[k]['rgb']) == rgb, k
tex_dir = os.path.join(OUT_DIR, 'textures'); os.makedirs(tex_dir, exist_ok=True); tex_path = os.path.join(tex_dir, 'start_ship_palette.png')
_ni = bpy.data.images.new('_pal_new', IW, IH, alpha=False); _ni.pixels[:] = pix.ravel().tolist()
_ni.filepath_raw = tex_path; _ni.file_format = 'PNG'; _ni.save(); bpy.data.images.remove(_ni)
_new = bpy.data.images.load(tex_path); img.user_remap(_new); bpy.data.images.remove(img); _new.name = 'start_ship_palette.png'; _new.pack(); img = _new
_chk = np.array(img.pixels[:]).reshape(IH, IW, 4); bad = []
for n_, c_ in CELL.items():
    cx = (c_ % 8) * CS + CS // 2; cy = IH - ((c_ // 8) * CS + CS // 2) - 1; got = [int(round(v * 255)) for v in _chk[cy, cx, :3]]
    if got != list(MATS[n_]['rgb']): bad.append((n_, got, list(MATS[n_]['rgb'])))
note('palette verify mismatches', bad); assert not bad
PALETTE = {n: dict(cell=CELL[n], rgb=list(MATS[n]['rgb'])) for n in CELL}

# ------------------------------------------------------------------ mesh helpers (from build_v5)
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
def tris_of(me): return sum(len(p.vertices) - 2 for p in me.polygons)
def replace_prop_mesh(name, mb, note_txt):
    """rebuild an EXISTING prop's mesh in place: same object, same mesh datablock, same origin/matrix (mb in Blender world coords)."""
    ob = bpy.data.objects[name]; me = ob.data; mw0 = [list(r) for r in ob.matrix_world]; t0 = tris_of(me)
    inv = ob.matrix_world.inverted(); mb.V = [tuple(inv @ Vector(v)) for v in mb.V]
    bm = bmesh.new(); bm.to_mesh(me); bm.free(); me.materials.clear(); sk = mb_to_mesh(mb, me)
    assert [list(r) for r in ob.matrix_world] == mw0
    old = ob.get('note', ''); ob['note'] = note_txt; ob['note_v5'] = old
    LOG['changes'][name] = dict(kind='REBUILT in place (vertices rebuilt, same object/mesh datablock/origin)', tris_before=t0, tris_after=tris_of(me), note=note_txt, skipped_faces=sk)
    note('REBUILT', name, t0, '->', tris_of(me))
def world_bm(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bm.faces.ensure_lookup_table(); return bm
class SBVH:
    def __init__(s, names):
        V = []; P = []; s.own = []
        for n in names:
            o = bpy.data.objects[n]; mw = o.matrix_world; o0 = len(V)
            V += [tuple(mw @ v.co) for v in o.data.vertices]
            for p in o.data.polygons: P.append([o0 + i for i in p.vertices]); s.own.append(n)
        s.T = BVHTree.FromPolygons(V, P)
    def ray(s, o, d, dist=400.0):
        loc, nor, idx, dd = s.T.ray_cast(Vector(B(o)), Vector(B(nrm(d))), dist)
        if loc is None: return None
        return Binv(loc), nrm(Binv(nor)), dd, s.own[idx]
def sframe(n, along=(1, 0, 0)):
    R = frame_from(n, along)
    if R[1, 1] < 0: R = frame_from(n, -np.asarray(along, float))
    return R
def slab_profile(mb, top, bot, x0, x1, mat):
    n = len(top); P = lambda x, zy: (x, zy[1], zy[0])
    for k in range(n - 1):
        for x in (x0, x1):
            q = [P(x, top[k]), P(x, top[k + 1]), P(x, bot[k + 1]), P(x, bot[k])]; mb._add(q, [(0, 1, 2, 3)], [mat])
        mb._add([P(x0, top[k]), P(x0, top[k + 1]), P(x1, top[k + 1]), P(x1, top[k])], [(0, 1, 2, 3)], [mat])
        mb._add([P(x0, bot[k]), P(x0, bot[k + 1]), P(x1, bot[k + 1]), P(x1, bot[k])], [(0, 1, 2, 3)], [mat])
    for k in (0, n - 1):
        mb._add([P(x0, top[k]), P(x1, top[k]), P(x1, bot[k]), P(x0, bot[k])], [(0, 1, 2, 3)], [mat])
def mb_bvh(mb): return BVHTree.FromPolygons([tuple(v) for v in mb.V], [list(f) for f in mb.F])
VIS_NAMES = [o.name for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith('COL')]
def obj_bvh(n):
    bm = world_bm(bpy.data.objects[n]); T = BVHTree.FromBMesh(bm); bm.free(); return T
def overlaps(mb, names):
    T = mb_bvh(mb); out = {}
    for n in names:
        k = len(T.overlap(obj_bvh(n)))
        if k: out[n] = k
    return out
def ov_count(a, b): return len(obj_bvh(a).overlap(obj_bvh(b)))
def rail_tops(objs, x, z0=-45.0, z1=72.0, dz=0.35):
    T = SBVH(objs); hits = []
    for z in np.arange(z0, z1, dz):
        r = T.ray(np.array((x, 140.0, z)), (0, -1, 0), 200)
        if r is not None and r[1][1] > 0.7: hits.append((z, r[0][1]))
    if len(hits) < 2: return None
    H = np.array(hits); zm = (H[:, 0].min() + H[:, 0].max()) / 2; out = []
    for side in (H[H[:, 0] < zm], H[H[:, 0] >= zm]):
        if not len(side): return None
        k = int(np.argmax(side[:, 1])); top = side[k, 1]; flat = side[side[:, 1] > top - 0.06]
        out.append((float(flat[:, 0].mean()), float(top), float(flat[:, 0].max() - flat[:, 0].min() + dz)))
    return out

# ------------------------------------------------------------------ measurements (before/after)
def section_width(x, Y, T):
    a = T.ray(np.array((x, Y, -300.0)), (0, 0, 1), 700); b = T.ray(np.array((x, Y, 300.0)), (0, 0, -1), 700)
    if a is None or b is None: return None
    return dict(z_high=round(float(a[0][2]), 3), z_low=round(float(b[0][2]), 3), width=round(float(b[0][2] - a[0][2]), 3))
STATIONS = [-140.0, -100.0, -60.0, -20.0, 20.0, 60.0, 100.0, 130.0]
LEVELS = [-2.0, -0.6, 1.5, 3.0, 6.0, 9.0, 12.0, 18.0, 23.0]
def widths():
    T = SBVH(['Hull']); return {'Y%.1f' % Y: {'x%d' % x: section_width(x, Y, T) for x in STATIONS} for Y in LEVELS}
def obb_list():
    out = []
    for o in bpy.data.collections['Collision'].objects:
        if not o.name.startswith('COL_HullExt'): continue
        W = np.array([Binv(o.matrix_world @ v.co) for v in o.data.vertices]); c = W.mean(0)
        d = sorted([W[i] - W[0] for i in range(1, len(W))], key=lambda v: np.linalg.norm(v))[:3]
        out.append((o.name, c, np.array([nrm(v) for v in d]), np.array([np.linalg.norm(v) / 2 for v in d])))
    return out
def hull_outer_samples():
    T = SBVH(['Hull']); P = []
    for x in np.arange(-158.0, 150.0, 4.0):
        for Y in np.arange(-0.5, 18.01, 1.5):
            for z0, dz in ((-300.0, 1), (300.0, -1)):
                r = T.ray(np.array((x, Y, z0)), (0, 0, dz), 700)
                if r is not None: P.append(r[0])
    return np.array(P)
OBB = obb_list()
def hullext_report():
    P = hull_outer_samples(); best = np.full(len(P), 1e9)
    for n, c, ax, hs in OBB:
        q = (P - c) @ ax.T; best = np.minimum(best, np.linalg.norm(np.maximum(np.abs(q) - hs, 0), axis=1))
    return dict(samples=int(len(P)), max_outside=round(float(best.max()), 3), p95_outside=round(float(np.percentile(best, 95)), 3),
                n_over_0_5=int((best > 0.5).sum()), n_over_1=int((best > 1.0).sum()), n_over_2=int((best > 2.0).sum()))
W_BEFORE = widths(); HX_BEFORE = hullext_report()
OV_BEFORE = {n: ov_count('Hull', n) for n in LOCKED + ['Pier', 'RockBumper', 'Dressing']}
note('hull overlaps before', OV_BEFORE, 'hullext outside before', HX_BEFORE)

# ================================================================== 1a  HULL BELLY ROUNDNESS (additional to v5)
KB = 0.16; YL, YH = -8.0, 14.0; TAN = math.tan(PHI)
def wB(Y):
    t = np.clip((np.asarray(Y, float) - YL) / (YH - YL), 0, 1); return np.sin(math.pi * t) ** 2
def gX(x, stern_lo=0.35):
    x = np.asarray(x, float)
    st = stern_lo + (1 - stern_lo) * np.vectorize(smooth)((x + 160.0) / 30.0)
    bw = 1.0 - np.vectorize(smooth)((x - 105.0) / 45.0)
    return np.minimum(st, bw)
def warp(P, stern_lo):
    P = np.array(P, float); zc = P[:, 1] * TAN; f = 1.0 + KB * wB(P[:, 1]) * gX(P[:, 0], stern_lo)
    Q = P.copy(); Q[:, 2] = zc + (P[:, 2] - zc) * f; return Q
NO_WARP = set(LOCKED + ['Pier', 'RockBumper', 'Dressing', 'Dressing_Glow'])
ORIG_CO = {}
def apply_warp(stern_lo):
    moved = {}
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.startswith('COL') or o.name in NO_WARP or o.name.startswith('ShipV5_'): continue
        me = o.data; n = len(me.vertices)
        if o.name not in ORIG_CO:
            co = np.zeros(n * 3, np.float32); me.vertices.foreach_get('co', co); ORIG_CO[o.name] = co.reshape(n, 3).astype(np.float64)
        L = ORIG_CO[o.name]; t = np.array(o.matrix_world.translation)
        Wb = L + t; R = np.column_stack([Wb[:, 0], Wb[:, 2], -Wb[:, 1]]); Q = warp(R, stern_lo)
        act = (wB(R[:, 1]) * gX(R[:, 0], stern_lo)) > 0      # only vertices the warp actually acts on are rewritten (others stay bit-identical)
        Wn = np.column_stack([Q[:, 0], -Q[:, 2], Q[:, 1]]); Ln = L.copy(); Ln[act] = (Wn - t)[act]
        dmax = float(np.max(np.abs(Ln - L))) if n else 0.0
        me.vertices.foreach_set('co', Ln.astype(np.float32).ravel()); me.update()
        if dmax > 1e-6: moved[o.name] = round(dmax, 4)
    return moved
STERN_LO = 0.35
moved = apply_warp(STERN_LO)
OV_AFTER = {n: ov_count('Hull', n) for n in OV_BEFORE}
if any(OV_AFTER[n] > OV_BEFORE[n] for n in OV_AFTER):
    note('belly warp created new overlaps', OV_AFTER, '-> retry with stern taper 0.0')
    STERN_LO = 0.0; moved = apply_warp(STERN_LO); OV_AFTER = {n: ov_count('Hull', n) for n in OV_BEFORE}
# restore untouched objects exactly (objects that the warp did not move were re-written with identical float32 values; re-assert)
for n in list(ORIG_CO):
    if n not in moved:
        bpy.data.objects[n].data.vertices.foreach_set('co', ORIG_CO[n].astype(np.float32).ravel()); bpy.data.objects[n].data.update()
W_AFTER = widths(); HX_AFTER = hullext_report()
LOG['hull_belly'] = dict(k=KB, profile='f = 1 + %.2f * sin^2(pi*(Y-(%.0f))/(%.0f)) * gX(x); peak at world Y%.1f; 0 at/below Y%.0f and at/above Y%.0f (deck Y24 untouched)' % (KB, YL, YH - YL, (YL + YH) / 2, YL, YH),
    centreline='z = Y*tan(15deg) (heeled hull frame z=0)', x_taper='same as v5: 1.0 for x in [-130,105]; stern end %.2f at x-160; bow fades to 0 by x150' % STERN_LO,
    moved_objects_max_disp=moved, overlaps_before=OV_BEFORE, overlaps_after=OV_AFTER, widths_before=W_BEFORE, widths_after=W_AFTER,
    hullext_outside_before=HX_BEFORE, hullext_outside_after=HX_AFTER)
note('belly moved', moved, 'overlaps', OV_AFTER, 'hullext after', HX_AFTER)
for o in bpy.data.objects:
    if o.name in moved: o['note_v5_1'] = 'v5_1: vertices moved by the belly-roundness warp (same origin/topology/UV/materials)'

VIS = SBVH(VIS_NAMES)
TEE = Binv(bpy.data.objects['Tee1'].matrix_world.translation); TEE_EYE = TEE + np.array((0, 5.0, 0))

# ================================================================== 1b  SHEER: ShipV5_SheerRise rebuilt (+3 everywhere, stern side boards added)
RISE_BOW = 7.0; CREST_CORNER = 4.6; CREST_MID = 7.0; STERN_SIDE = 4.6
SHEER = {}
sr = MB('sheer'); bow_lines = {0: [], 1: []}
for x in np.arange(90.0, 154.1, 4.0):
    t = rail_tops(['Prop_CapRails'], x)
    if t is None: continue
    for i in (0, 1): bow_lines[i].append((x, t[i][0], t[i][1], t[i][2]))
def bow_h(x): return RISE_BOW * smooth((x - 82.0) / 68.0)
for i in (0, 1):
    L_ = bow_lines[i]
    if len(L_) < 4: LOG['skipped'].append('bow sheer side %d: cap rail not found' % i); continue
    path = []; rects = []; caps = []; crects = []
    for (x, z, y, w) in L_:
        h = bow_h(x); hw = max(0.45, min(0.8, 0.45 * w))
        path.append((x, y + (h - 0.4) / 2, z)); rects.append((hw, (h + 0.4) / 2))
        caps.append((x, y + h + 0.1, z)); crects.append((hw + 0.3, 0.3))
    sr.tube(path, 0, 'HullWood', rect=rects, up=(0, 1, 0))
    sr.tube(caps, 0, 'WoodDk', rect=crects, up=(0, 1, 0))
    SHEER['bow_side%d' % i] = dict(x0=L_[0][0], x1=L_[-1][0], cap_rail_top_y=[round(a[2], 2) for a in L_], new_top_y=[round(a[2] + bow_h(a[0]) + 0.4, 2) for a in L_],
                                   rise_v5=[round(4.0 * smooth((a[0] - 86.0) / 64.0), 2) for a in L_], rise_v5_1=[round(bow_h(a[0]), 2) for a in L_])
XT = -160.6
prof = []; Tst = SBVH(['Prop_SternCastle', 'Hull'])
for z in np.arange(-40.0, 72.0, 0.5):
    r = Tst.ray(np.array((-159.2, 140.0, z)), (0, -1, 0), 200)
    if r is not None: prof.append((z, r[0][1]))
STERN = None
if len(prof) > 20:
    Pz = np.array(prof); zlo, zhi = Pz[:, 0].min() + 1.5, Pz[:, 0].max() - 1.5
    zz = np.linspace(zlo, zhi, 25)
    env = np.array([Pz[np.abs(Pz[:, 0] - z) < 4.0][:, 1].max() for z in zz])
    top = []; bot = []
    for k, z in enumerate(zz):
        t = (z - zlo) / (zhi - zlo); top.append((z, env[k] + CREST_CORNER + (CREST_MID - CREST_CORNER) * math.sin(math.pi * t))); bot.append((z, env[k] - 1.2))
    slab_profile(sr, top, bot, XT - 0.7, XT + 0.7, 'HullWood')
    sr.tube([(XT, y + 0.2, z) for z, y in top], 0, 'WoodDk', rect=[(1.0, 0.4)] * len(top), up=(0, 1, 0))
    zc = (zlo + zhi) / 2; kc = int(np.argmin(np.abs(zz - zc)))
    STERN = dict(z_lo=zlo, z_hi=zhi, z_mid=float(zc), crest_top_mid=float(top[kc][1]), env_mid=float(env[kc]), corner_tops=[float(top[0][1]), float(top[-1][1])])
    SHEER['stern_crest'] = dict(x=XT, z_range=[round(zlo, 2), round(zhi, 2)], castle_top_mid=round(float(env[kc]), 2), crest_top_mid=round(float(top[kc][1]), 2),
                                rise_mid_v5=4.0, rise_mid_v5_1=CREST_MID, rise_corner_v5=1.6, rise_corner_v5_1=CREST_CORNER)
else:
    LOG['skipped'].append('stern crest: stern castle top not found')
# stern side rise boards on the stern-castle tops (outboard edge), rising 0 -> STERN_SIDE toward the transom. Low side kept aft of x-136 (gangplank notch).
for side in (0, 1):
    xs0 = -122.0 if side == 0 else -136.0; L_ = []
    for x in np.arange(xs0, -157.9, -3.0):
        t = rail_tops(['Prop_SternCastle'], x)
        if t is None: continue
        z, y, w = t[side]
        if y < 45.0: continue
        L_.append((x, z, y, w))
    if len(L_) < 4: LOG['skipped'].append('stern side rise %d: castle top not found' % side); continue
    L_ = L_[::-1]; xa = L_[-1][0]
    path = []; rects = []; caps = []; crects = []
    for (x, z, y, w) in L_:
        h = 0.35 + STERN_SIDE * smooth((xa - x) / (xa + 158.5)); hw = max(0.45, min(0.8, 0.45 * w))
        path.append((x, y + (h - 0.4) / 2, z)); rects.append((hw, (h + 0.4) / 2)); caps.append((x, y + h + 0.1, z)); crects.append((hw + 0.3, 0.3))
    sr.tube(path, 0, 'HullWood', rect=rects, up=(0, 1, 0)); sr.tube(caps, 0, 'WoodDk', rect=crects, up=(0, 1, 0))
    SHEER['stern_side%d' % side] = dict(x_range=[L_[0][0], L_[-1][0]], castle_top_y=[round(a[2], 2) for a in L_], rise_max=STERN_SIDE)
ovs = overlaps(sr, ['DeckCabin'] + LOCKED[1:])
note('sheer overlaps with locked', ovs); assert not ovs
replace_prop_mesh('ShipV5_SheerRise', sr, 'v5_1 banana sheer +3: bow cap-rail rise board (0 at x82 -> +7 at the stem, both sides) + arched transom crest (+4.6 corners, +7 centre) + stern-castle side rise boards (0 -> +4.6 toward the transom). Exterior trim only; walk surfaces untouched.')
LOG['sheer'] = SHEER

# ================================================================== 1c  ShipV5_SternCurl: 1.8x vertex scale about its crest base, +3 lift with the crest
CURL_S = 1.8
co_ = bpy.data.objects['ShipV5_SternCurl']; me = co_.data; n = len(me.vertices); L0 = np.zeros(n * 3, np.float32); me.vertices.foreach_get('co', L0); L0 = L0.reshape(n, 3).astype(np.float64)
t = np.array(co_.matrix_world.translation); Wb = L0 + t; R = np.column_stack([Wb[:, 0], Wb[:, 2], -Wb[:, 1]])
base_v5 = np.array((-160.6, 66.08, 13.75))   # v5 build log stern_curl.base_roblox (crest_top_mid - 1 at the transom centre)
if STERN is not None:
    base_new = np.array((XT, STERN['crest_top_mid'] - 1.0, STERN['z_mid']))
else:
    base_new = base_v5 + np.array((0, 3.0, 0))
Rn = base_new + (R - base_v5) * CURL_S
Wn = np.column_stack([Rn[:, 0], -Rn[:, 2], Rn[:, 1]]); me.vertices.foreach_set('co', (Wn - t).astype(np.float32).ravel()); me.update()
LOG['changes']['ShipV5_SternCurl'] = dict(kind='EDITED: vertices scaled %.1fx about the crest base and lifted with the +3 crest (same object/origin/topology/UV/materials)' % CURL_S,
    base_v5=list(base_v5), base_v5_1=list(np.round(base_new, 3)), height_before=round(float(R[:, 1].max() - base_v5[1]), 2), height_after=round(float(Rn[:, 1].max() - base_new[1]), 2),
    top_y_before=round(float(R[:, 1].max()), 2), top_y_after=round(float(Rn[:, 1].max()), 2), aft_most_x_before=round(float(R[:, 0].min()), 2), aft_most_x_after=round(float(Rn[:, 0].min()), 2), tris=tris_of(me))
co_['note_v5_1'] = 'v5_1: scaled 1.8x about its crest base, lifted with the +3 transom crest'
note('stern curl', LOG['changes']['ShipV5_SternCurl'])

# ================================================================== 3  Prop_Figurehead -> 1.6x coral octopus, coral top / CoralDk underside
S = 1.6
hv = np.array([Binv(v.co) for v in bpy.data.objects['Hull'].data.vertices]); hvh = np.array([untilt(p) for p in hv])
bs_d = nrm(np.array(BS1) - np.array(BS0)); AX = []
for xs in np.arange(158.0, 200.0, 3.0):
    q = hvh[np.abs(hvh[:, 0] - xs) < 1.6]
    if not len(q): continue
    tt = (q - np.array(BS0)) @ bs_d; foot = np.array(BS0) + np.outer(tt, bs_d); d = np.linalg.norm(q - foot, axis=1)
    sel = q[d < 6.0]
    if len(sel) < 6: continue
    c = sel.mean(0); r = float(np.median(np.linalg.norm(sel - c, axis=1))); AX.append((c, r))
oc = MB('octo')
fh = bpy.data.objects['Prop_Figurehead']; FH0 = Binv(fh.matrix_world.translation); FHh = untilt(FH0)
old_fh = np.array([Binv(fh.matrix_world @ v.co) for v in fh.data.vertices])
HC = np.array((FHh[0] + 8.0 + 3.4, FHh[1] + 4.0 - 4.2, 0.0))       # moved forward so the 1.6x mantle back stays at the v5 stem contact, lowered under the bowsprit
def sv(v): return np.array(v, float) * S
oc.ellipsoid(HC + sv((-1.0, 2.6, 0)), tuple(sv((5.6, 6.6, 5.4))), 'Coral', R=Rz(math.radians(-28)), nu=14, nv=9)        # bulbous mantle
oc.ellipsoid(HC + sv((1.2, -2.4, 0)), tuple(sv((4.8, 3.6, 4.9))), 'Coral', nu=14, nv=7)                                 # face / lower head
EYE_K = 1.2
for sz in (-1, 1):
    ec = HC + sv((5.0, -0.4, 2.35 * sz))
    oc.ellipsoid(ec, tuple(sv((1.25, 1.5, 1.25)) * EYE_K), 'Canvas', nu=10, nv=6)                                          # big cream eye
    pc = ec + sv((1.2, -0.15, 0.08 * sz)) * EYE_K
    oc.ellipsoid(pc, tuple(sv((0.5, 0.85, 0.68)) * EYE_K), 'Shadow', nu=8, nv=5)                                           # dark pupil
    oc.ellipsoid(pc + sv((0.42, 0.38, -0.12 * sz)) * EYE_K, tuple(sv((0.16, 0.2, 0.2)) * EYE_K), 'Canvas', nu=6, nv=4)       # sparkle
    oc.box(ec + sv((0.5, 1.95, 0)) * np.array((1, EYE_K, 1)), tuple(sv((1.8, 0.55, 2.6))), 'CoralDk', R=Rx(math.radians(-14 * sz)))   # brow
grin = [HC + sv((4.25 + 1.5 * math.cos(a) ** 2, -3.55 + 1.25 * abs(math.sin(a)), 3.5 * math.sin(a))) for a in np.linspace(-1.3, 1.3, 11)]
oc.tube(grin, 0.62 * S, 'Shadow', sec=6)
for zt in (-1.35, 0.0, 1.35):
    oc.box(HC + sv((5.75, -3.3, zt)), tuple(sv((0.7, 0.85, 0.8))), 'Canvas')
for sz in (-1, 1):   # cheeks
    oc.ellipsoid(HC + sv((4.3, -2.2, 3.9 * sz)), tuple(sv((0.9, 0.7, 0.9))), 'CoralDk', nu=8, nv=4)
if len(AX) >= 4:
    AXc = np.array([c for c, r in AX]); AXr = np.array([r for c, r in AX])
    def ax_at(x): return np.array([np.interp(x, AXc[:, 0], AXc[:, k]) for k in range(3)]), float(np.interp(x, AXc[:, 0], AXr))
    for k in range(3):
        ph = 2 * math.pi * k / 3 + 0.4; pts = []; rad = []
        x_start = HC[0] + 2.0; x_end = min(AXc[-1, 0], 158.0 + 30.0 + 5.0 * k)
        root = HC + sv((0.5, -3.8, (k - 1) * 2.8)); nN = 32
        for i in range(nN + 1):
            tt = i / nN; x = x_start + (x_end - x_start) * tt; c, rr = ax_at(x)
            a = ph + tt * 2 * math.pi * 1.35; tr = 1.55 * S * (1 - 0.68 * tt)
            ring = c + (rr + tr * 0.8) * np.array((0, math.cos(a), math.sin(a)))
            if tt < 0.2: ring = root + (ring - root) * smooth(tt / 0.2)
            pts.append(ring); rad.append(tr)
        tipd = nrm(pts[-1] - pts[-2]); curl_c = pts[-1]
        for j in range(1, 5):
            a = j * 0.9; pts.append(curl_c + tipd * 1.0 * math.sin(a) + np.array((0, 1.0 * (1 - math.cos(a)), 0))); rad.append(rad[-1] * 0.85)
        oc.tube(pts, rad, 'Coral', sec=8, up=(0, 0, 1))
    for k, zz_ in enumerate((-3.2, 0.0, 3.2)):
        root = HC + sv((-0.5, -4.0, zz_)); pts = []; rad = []
        for i in range(12):
            tt = i / 11; a = tt * 1.7 * math.pi
            pts.append(root + sv((1.5 * math.sin(a) * (1 - 0.5 * tt) + 0.8 * tt, -6.0 * tt + 1.4 * (1 - math.cos(a)) * tt, zz_ * 0.45 * tt))); rad.append(1.35 * S * (1 - 0.7 * tt))
        oc.tube(pts, rad, 'Coral', sec=8, up=(0, 0, 1))
else:
    LOG['skipped'].append('octopus bowsprit tentacles: bowsprit axis not found')
oc.V = [B(tilt(Binv(v))) for v in oc.V]
# recalc_face_normals in mb_to_mesh makes normals consistent; the underside test above uses the MB winding (outward for ellipsoid/tube/box primitives)
ov = overlaps(oc, ['DeckCabin'] + LOCKED[1:]); assert not ov, ov
replace_prop_mesh('Prop_Figurehead', oc, 'v5_1: 1.6x chunky grinning coral octopus, Coral (230,120,100) top + CoralDk (180,80,70) underside/brows/cheeks, big cream eyes with dark pupils + sparkle, thick dark grin + 3 teeth; 3 tentacles spiralling the bowsprit + 3 curled under the head; same object/origin')
# darker warm underside on the BUILT mesh (normals made consistent/outward by recalc_face_normals): Coral faces facing down -> CoralDk
me = fh.data; slot = {m.name: i for i, m in enumerate(me.materials)}; uvl = me.uv_layers['UVMap']; ndk = 0; dk_uv = cell_uv(CELL['CoralDk'])
for p in me.polygons:
    if p.material_index == slot['Coral'] and p.normal.z < -0.35:
        p.material_index = slot['CoralDk']; ndk += 1
        for li in p.loop_indices: uvl.data[li].uv = dk_uv
me.update()
new_fh = np.array([Binv(fh.matrix_world @ v.co) for v in fh.data.vertices])
LOG['octopus'] = dict(scale=S, head_centre_hull=list(np.round(HC, 2)), coraldk_faces=ndk, bowsprit_samples=len(AX),
                      bbox_before=[list(np.round(old_fh.min(0), 2)), list(np.round(old_fh.max(0), 2))], bbox_after=[list(np.round(new_fh.min(0), 2)), list(np.round(new_fh.max(0), 2))],
                      head_height_before=round(float(old_fh[:, 1].max() - old_fh[:, 1].min()), 2), head_height_after=round(float(new_fh[:, 1].max() - new_fh[:, 1].min()), 2))
VIS = SBVH(VIS_NAMES)

# ================================================================== 2  ShipV5_BowEyes rebuilt: ~2x, higher, dark pupils, thick lid plank
EYE_OK = ('Hull', 'Prop_BowRaise', 'Prop_SheerWale')
ER = 5.1   # brass rim radius (v5 2.55)
ey = MB('eyes'); EYES = []; dbg = {}
VIS = SBVH([n for n in VIS_NAMES if n != 'ShipV5_BowEyes'])
def eye_fit(x, Y, side):
    r = VIS.ray(np.array((x, Y, 300.0 * side)), (0, 0, -side), 600)
    if r is None or r[3] not in EYE_OK: return None, 'centre %s' % (None if r is None else r[3])
    p, n = r[0], r[1]
    if n[2] * side < 0: n = -n
    R = sframe(n, (1, 0, 0)); u, v = R[:, 0], R[:, 1]
    if v[1] < 0: v = -v
    u = np.cross(v, n); worst = 0.0
    for k in range(16):
        a = 2 * math.pi * k / 16
        for rr in (ER + 0.9, ER * 0.6):
            q = p + rr * (math.cos(a) * u + math.sin(a) * v)
            h = VIS.ray(q + n * 5.0, -n, 12.0)
            if h is None or h[3] not in EYE_OK: return None, 'rim miss %s' % (None if h is None else h[3])
            s = float(np.dot(h[0] - p, n))
            if s > 1.15 or s < -2.2: return None, 'rim s=%.2f' % s
            worst = min(worst, s)
    return (p, n, u, v, worst), 'ok'
for side in (-1, 1):
    best = None
    for x in (152.0, 150.0, 148.0, 146.0, 144.0, 142.0, 140.0, 138.0, 136.0, 134.0, 130.0, 126.0, 122.0, 118.0):
        t = rail_tops(['Prop_CapRails'], x)
        if t is None: continue
        z_r, y_r, _ = t[0 if side < 0 else 1]
        for dy in np.arange(ER + 1.3, ER + 12.0, 0.25):
            Y = y_r - dy; f, why = eye_fit(x, Y, side)
            dbg.setdefault(side, []).append((x, round(Y, 1), why))
            if f is None: continue
            if best is None or Y > best[1]: best = (x, Y, f, y_r)
            break
    if best is None: LOG['skipped'].append('bow eye side %d: no clear spot' % side); continue
    x, Y, (p, n, u, v, worst), y_r = best
    p = p + n * 0.8; back = -3.2      # eye built 0.8 proud of the sampled surface (rim test allows the surface up to +1.15 / down to -2.2 under the disc)
    ey.torus(p + n * 0.45, n, ER, 1.05, 'Brass', nu=16, nv=6)                                               # chunky brass rim
    ey.frustum(p + n * back, p + n * 0.55, ER - 0.3, ER - 0.3, 'Canvas', sec=16, up=tuple(v))               # cream sclera disc (embedded back to -2.4)
    look = -u * 0.7 * side * 0 + (-v * 0.9)                                                                   # pupils look slightly down (sleepy)
    pc = p + look
    ey.frustum(pc + n * 0.5, pc + n * 1.05, 2.45, 2.45, 'Shadow', sec=12, up=tuple(v))                      # big dark pupil
    ey.frustum(pc + n * 1.0 - v * 1.2 + u * 1.0, pc + n * 1.25 - v * 1.2 + u * 1.0, 0.6, 0.6, 'Canvas', sec=8, up=tuple(v))   # sparkle
    droop = Raxis(n, math.radians(-9 * side))
    lid0 = []; lid1 = []
    for a in np.linspace(0, math.pi, 13):
        q = droop @ (u * (ER + 0.35) * math.cos(a) + v * ((ER + 0.35) * math.sin(a) * 0.98)) + droop @ (v * 0.25)
        lid0.append(p + q * 0.98 + n * 0.5); lid1.append(p + q * 0.9 + n * 2.1)
    ey.loft([lid0, lid1], 'WoodDk')                                                                          # thick dark lid shell
    lc = p + n * 1.55 + droop @ (v * 0.25)
    ey.box(lc, (2 * ER + 2.6, 1.15, 1.9), 'PostLt', R=droop @ np.column_stack([u, v, n]))                    # chunky lid plank (lighter wood edge)
    for e in (-1, 1): ey.frustum(lc + droop @ (u * e * (ER + 0.4)) + n * 0.9, lc + droop @ (u * e * (ER + 0.4)) + n * 1.35, 0.5, 0.35, 'Brass', sec=6)   # lid nails
    EYES.append(dict(side='low(+Z)' if side > 0 else 'high(-Z)', x=x, centre=list(np.round(p, 2)), normal=list(np.round(n, 3)), below_cap_top=round(float(y_r - Y), 2), rim_radius=ER,
                     rim_min_surface_offset=round(worst, 2)))
v5eyes = [dict(side='high(-Z)', centre=[136.0, 53.78, -2.56], rim_radius=2.55), dict(side='low(+Z)', centre=[136.0, 46.53, 28.74], rim_radius=2.55)]
if EYES:
    ov = overlaps(ey, ['Prop_Figurehead', 'ShipV5_SheerRise', 'Prop_CapRails', 'Prop_Seaweed', 'Prop_Portholes', 'Rigging'])
    note('eye overlaps', ov)
    replace_prop_mesh('ShipV5_BowEyes', ey, 'v5_1 sleepy bow face ~2x: brass rim r%.1f, cream sclera, big dark pupils looking down + sparkle, thick dark droopy lid with a light lid plank + brass nails, high on the bow flanks' % ER)
LOG['bow_eyes'] = dict(v5=v5eyes, v5_1=EYES, overlaps=ov if EYES else None, search_debug={str(k): v[:40] for k, v in dbg.items()})
VIS = SBVH(VIS_NAMES)

# ================================================================== 4  ShipV5_Patches rebuilt: 4 LARGE patches high on the low (+Z) side
pa = MB('patches'); PATCHES = []
VIS = SBVH([n for n in VIS_NAMES if n != 'ShipV5_Patches'])
PW_, PH_ = 20.0, 14.0
OTH_P = [n for n in VIS_NAMES if n not in ('Hull', 'ShipV5_Patches')]
def try_patch(x, Y, rot, side=1):
    ru = np.array((math.cos(math.radians(rot)), math.sin(math.radians(rot)))); grid = {}
    NI, NJ = 7, 5
    for i in range(NI):
        for j in range(NJ):
            a = (i / (NI - 1) - 0.5) * PW_; b = (j / (NJ - 1) - 0.5) * PH_
            dx = a * ru[0] - b * ru[1]; dy = a * ru[1] + b * ru[0]
            r = VIS.ray(np.array((x + dx, Y + dy, 300.0 * side)), (0, 0, -side), 600)
            if r is None or r[3] != 'Hull' or r[0][1] < WATER_Y + 2.0: return None
            n = r[1] if r[1][2] * side > 0 else -r[1]
            if n[2] * side < 0.25: return None
            grid[(i, j)] = (r[0], n)
    def fn(uu, vv, off=0.0):
        i = min(NI - 2, int(uu * (NI - 1))); j = min(NJ - 2, int(vv * (NJ - 1))); fu = uu * (NI - 1) - i; fv = vv * (NJ - 1) - j
        P00, N00 = grid[(i, j)]; P10, N10 = grid[(i + 1, j)]; P01, N01 = grid[(i, j + 1)]; P11, N11 = grid[(i + 1, j + 1)]
        P = (1 - fu) * (1 - fv) * P00 + fu * (1 - fv) * P10 + (1 - fu) * fv * P01 + fu * fv * P11
        N = nrm((1 - fu) * (1 - fv) * N00 + fu * (1 - fv) * N10 + (1 - fu) * fv * N01 + fu * fv * N11)
        return P + N * off, N
    return fn
CAND = [(x, Y) for Y in np.arange(33.0, 14.9, -2.0) for x in np.arange(-95.0, 116.0, 5.0)]
REJ = {'rays': 0, 'overlap': 0}
for (x, Y) in CAND:
    if len(PATCHES) >= 4: break
    aft = sum(1 for p_ in PATCHES if p_['x'] < 0); fore = len(PATCHES) - aft
    if x < 0 and aft >= 2: continue
    if x >= 0 and fore >= 2: continue
    if any(abs(x - p_['x']) < PW_ + 6 for p_ in PATCHES): continue
    k = len(PATCHES); rot = (7, -9, -6, 10)[k]; mat = ('PatchBlue', 'PatchTeal', 'PatchTeal', 'PatchBlue')[k]
    fn = try_patch(x, Y, rot)
    if fn is None: REJ['rays'] += 1; continue
    one = MB('p'); one.thick_surface(lambda uu, vv: fn(uu, vv, 0.2), 8, 6, 0.8, mat, side_mat=mat)       # slab -0.2..+0.6 about the hull surface
    NAILS = [(u_, v_) for u_ in (0.05, 0.36, 0.64, 0.95) for v_ in (0.07, 0.93)] + [(0.05, 0.5), (0.95, 0.5)]
    for uu, vv in NAILS:
        P, N = fn(uu, vv, 0.0); one.frustum(P + N * 0.3, P + N * 1.15, 1.0, 0.85, 'Brass', sec=8); one.frustum(P + N * 1.15, P + N * 1.5, 0.85, 0.3, 'Brass', sec=8)
    for (u0, u1) in ((0.33, 0.33), (0.67, 0.67)):   # two dark plank seams across the patch
        pts = [fn(u0, vv, 0.62)[0] for vv in np.linspace(0.08, 0.92, 6)]; one.tube(pts, 0, 'WoodDk', rect=(0.18, 0.12), up=tuple(fn(u0, 0.5)[1]))
    ov = overlaps(one, OTH_P)
    if ov: REJ['overlap'] += 1; continue
    pa.extend(one); PATCHES.append(dict(side='low(+Z)', x=x, Y=Y, mat=mat, size=[PW_, PH_], rot_deg=rot, nails=len(NAILS)))
note('patch candidates rejected', REJ, 'placed', [(p_['x'], p_['Y']) for p_ in PATCHES])
LOG['patches'] = dict(rejected_candidates=REJ, v5=dict(count=5, size=[7.5, 5.5], centre_Y=[11, 13, 9, 16, 12, 14]), v5_1=PATCHES, linear_scale_vs_v5=round(PW_ / 7.5, 2), area_scale_vs_v5=round(PW_ * PH_ / (7.5 * 5.5), 2))
if len(PATCHES) < 4: LOG['skipped'].append('hull patches: only %d placed' % len(PATCHES))
replace_prop_mesh('ShipV5_Patches', pa, 'v5_1: %d LARGE hull patches %gx%g (blue 90,130,170 / teal 70,150,140) high on the low (+Z) side, slab -0.2..+0.6 about the hull, 10 chunky brass nails + 2 dark seams each' % (len(PATCHES), PW_, PH_))
VIS = SBVH(VIS_NAMES)

# ================================================================== 5  TEE VISUAL READ: move prop MESH vertices (origins fixed)
def comps_of(o):
    me = o.data; nv = len(me.vertices); adj = [[] for _ in range(nv)]
    for e in me.edges: a, b = e.vertices; adj[a].append(b); adj[b].append(a)
    lab = -np.ones(nv, int); k = 0
    for s in range(nv):
        if lab[s] >= 0: continue
        st = [s]; lab[s] = k
        while st:
            a = st.pop()
            for b in adj[a]:
                if lab[b] < 0: lab[b] = k; st.append(b)
        k += 1
    return lab, k
def world_R(o):
    n = len(o.data.vertices); L = np.zeros(n * 3, np.float32); o.data.vertices.foreach_get('co', L); L = L.reshape(n, 3).astype(np.float64)
    W = L + np.array(o.matrix_world.translation); return np.column_stack([W[:, 0], W[:, 2], -W[:, 1]]), L
def faces_of(o, vsel):
    return [list(p.vertices) for p in o.data.polygons if all(vsel[i] for i in p.vertices)]
CAM_AX = math.degrees(math.atan2(-0.25, 0.93))   # ship_tee camera axis azimuth (x->z) = -15.05 deg
WEDGE = 20.0                                      # protected tee sightline wedge: +-20 deg about the tee camera axis (central ~45% of the 90 deg view)
def azim(P): return np.degrees(np.arctan2(P[:, 2] - TEE_EYE[2], P[:, 0] - TEE_EYE[0]))
def route_clear(P):
    """horizontal distance of points to the cabin->door->tee->gangplank centreline x=-120 (z -17..62.5), only points in the walk band Y 23..34"""
    zc = np.clip(P[:, 2], -17.0, 62.5); d = np.hypot(P[:, 0] + 120.0, P[:, 2] - zc); band = (P[:, 1] >= 23.0) & (P[:, 1] <= 34.0)
    return float(d[band].min()) if band.any() else 1e9
MOVES = {}
OBST_CACHE = {}
def obst_tree(names, extra=None):
    V = []; P = []
    for n in names:
        o = bpy.data.objects[n]; mw = o.matrix_world; o0 = len(V); V += [tuple(mw @ v.co) for v in o.data.vertices]
        P += [[o0 + i for i in p.vertices] for p in o.data.polygons]
    if extra:
        for (Vb, Fb) in extra: o0 = len(V); V += Vb; P += [[o0 + i for i in f] for f in Fb]
    return BVHTree.FromPolygons(V, P)
def move_group(name, vsel, cands, label):
    """vsel: bool mask of the object's vertices to move. cands: list of (x, z, yaw_deg) target base centres. First candidate that passes wins."""
    o = bpy.data.objects[name]; R, L = world_R(o); sel = R[vsel]
    base = sel[sel[:, 1] < sel[:, 1].min() + 0.8]; piv = np.array(((base[:, 0].min() + base[:, 0].max()) / 2, sel[:, 1].min(), (base[:, 2].min() + base[:, 2].max()) / 2))
    F = faces_of(o, vsel); idx = np.where(vsel)[0]; remap = {int(i): k for k, i in enumerate(idx)}; Fl = [[remap[i] for i in f] for f in F]
    others = [n for n in VIS_NAMES if n not in (name, 'DeckCabin')]
    rest = ~vsel; Fr = faces_of(o, rest)
    rest_extra = [([tuple(o.matrix_world @ Vector(o.data.vertices[i].co)) for i in range(len(o.data.vertices))], Fr)] if Fr else None
    T_oth = obst_tree(others, rest_extra); T_cab = obst_tree(['DeckCabin'])
    tried = []
    for (x, z, yaw) in cands:
        a = math.radians(yaw); Ry_ = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
        tgt = np.array((x, piv[1], z)); Q = tgt + (sel - piv) @ Ry_.T
        VB = [B(q) for q in Q]; T_me = BVHTree.FromPolygons(VB, Fl); T_up = BVHTree.FromPolygons([B(q + np.array((0, 0.35, 0))) for q in Q], Fl)
        ov_o = len(T_me.overlap(T_oth)); ov_c = len(T_up.overlap(T_cab))
        if len(tried) > 400 and not (ov_o == 0 and ov_c == 0): tried.append(dict(x=x, z=z, yaw=yaw, ok=False, overlaps_other=ov_o)); continue
        he, le = deck_edges(x - 4.0) if deck_edges(x - 4.0) else (-1e9, 1e9); he2, le2 = deck_edges(x + 4.0) if deck_edges(x + 4.0) else (-1e9, 1e9)
        in_deck = Q[:, 2].min() > max(he, he2) + 0.8 and Q[:, 2].max() < min(le, le2) - 0.8
        az = azim(Q); off = np.abs(((az - CAM_AX) + 180) % 360 - 180); in_wedge = int((off < WEDGE).sum())
        rc = route_clear(Q)
        ok = ov_o == 0 and ov_c == 0 and in_deck and in_wedge == 0 and rc >= 2.0 + 6.0
        tried.append(dict(x=round(float(x), 2), z=round(float(z), 2), yaw=yaw, overlaps_other=ov_o, overlaps_cabin_walls=ov_c, on_deck=bool(in_deck), verts_in_tee_wedge=in_wedge, route_centreline_dist=round(rc, 2), ok=ok))
        if ok:
            Rn = R.copy(); Rn[vsel] = Q; Wn = np.column_stack([Rn[:, 0], -Rn[:, 2], Rn[:, 1]]); Ln = Wn - np.array(o.matrix_world.translation)
            o.data.vertices.foreach_set('co', Ln.astype(np.float32).ravel()); o.data.update()
            azb = azim(sel); offb = np.abs(((azb - CAM_AX) + 180) % 360 - 180)
            MOVES[label] = dict(object=name, verts_moved=int(vsel.sum()), from_base=list(np.round(piv, 2)), to_base=list(np.round(tgt, 2)), yaw_deg=yaw,
                                bbox_before=[list(np.round(sel.min(0), 2)), list(np.round(sel.max(0), 2))], bbox_after=[list(np.round(Q.min(0), 2)), list(np.round(Q.max(0), 2))],
                                tee_axis_offset_deg_before=[round(float(offb.min()), 1), round(float(offb.max()), 1)], tee_axis_offset_deg_after=[round(float(off.min()), 1), round(float(off.max()), 1)],
                                route_centreline_dist_before=round(route_clear(sel), 2), route_centreline_dist_after=round(rc, 2), n_candidates_tried=len(tried), candidates_tried=tried[-12:])
            note('MOVED', label, name, 'to', (x, z, yaw)); return True
    MOVES[label] = dict(object=name, moved=False, candidates_tried=tried); LOG['skipped'].append('move %s: no candidate passed' % label); note('MOVE FAILED', label, tried); return False
# wheel: off-axis toward the stern end of the open deck / high side, in the lee of the cabin's bow-end wall; face turned to +Z (low side / 3q camera)
o = bpy.data.objects['Prop_SternWheel']; R, _ = world_R(o)
PREF_W = np.array((-78.0, 0.0))
GW = sorted([(float(x), float(z), yw) for x in np.arange(-88.0, -55.9, 2.0) for z in np.arange(-16.0, 8.1, 2.0) for yw in (90, 60, 120, 0)],
            key=lambda c: ((c[0] - PREF_W[0]) ** 2 + (c[1] - PREF_W[1]) ** 2) + {90: 0, 60: 30, 120: 30, 0: 60}[c[2]])
move_group('Prop_SternWheel', np.ones(len(R), bool), GW, 'wheel')
# chest: outboard against the high-side (-Z) bulwark, opening toward the deck (+Z)
o = bpy.data.objects['Prop_TreasureChest']; R, _ = world_R(o)
he = deck_edges(-72.0)[0]
move_group('Prop_TreasureChest', np.ones(len(R), bool), [(-72.0, he + 6.5, 90), (-74.0, he + 6.5, 90), (-70.0, he + 7.0, 90), (-76.0, he + 7.0, 90), (-68.0, he + 7.5, 90), (-72.0, he + 8.5, 90), (-66.0, he + 8.0, 90), (-78.0, he + 8.0, 90)], 'chest')
# tee rope coil (x-90 component only): outboard to the low-side (+Z) bulwark under the hung life ring
o = bpy.data.objects['Prop_RopeCoils']; R, _ = world_R(o); lab, k = comps_of(o)
csel = np.zeros(len(R), bool)
for c in range(k):
    m = lab == c
    if R[m, 0].mean() < -60: csel |= m
le = deck_edges(-100.0)[1]
move_group('Prop_RopeCoils', csel, [(-102.0, le - 3.4, 0), (-104.0, le - 3.4, 0), (-100.0, le - 3.4, 0), (-98.0, le - 3.4, 0), (-96.0, le - 3.4, 0), (-102.0, le - 3.8, 0), (-100.0, le - 4.0, 0), (-96.0, le - 4.0, 0)], 'tee_rope_coil')
# barrels (CargoCluster components west of x-99; the crab's crate stack stays): outboard to the low-side bulwark aft of the gangplank notch
o = bpy.data.objects['Prop_CargoCluster']; R, _ = world_R(o); lab, k = comps_of(o)
bsel = np.zeros(len(R), bool)
for c in range(k):
    m = lab == c
    if R[m, 0].mean() < -99.0: bsel |= m
le = deck_edges(-140.0)[1]
move_group('Prop_CargoCluster', bsel, [(-140.0, le - 6.0, 0), (-142.0, le - 6.0, 0), (-138.0, le - 6.0, 0), (-144.0, le - 6.5, 0), (-140.0, le - 7.5, 0), (-136.0, le - 6.5, 0), (-146.0, le - 7.0, 0), (-140.0, 30.0, 0)], 'barrels')
LOG['tee_moves'] = dict(method='mesh vertices transformed in world space (yaw about the base centre + translation) and written back in object-local space; object origins unchanged',
                        tee_eye=list(np.round(TEE_EYE, 2)), tee_camera_axis_azimuth_deg=round(CAM_AX, 2), protected_wedge_deg=WEDGE,
                        acceptance='no triangle overlap with any other visual mesh (DeckCabin tested with the group lifted 0.35 so only walls count), inside the deck edges, 0 verts inside the +-20 deg tee wedge, >= 8 studs from the route centreline (player r2 + 6)',
                        moves=MOVES)
for lbl, m in MOVES.items():
    if m.get('moved', True): bpy.data.objects[m['object']]['note_v5_1'] = 'v5_1: %s mesh moved out of the tee sightline (origin unchanged)' % lbl

# ------------------------------------------------------------------ final asserts + save
assert col_hash() == COL0, 'collision changed!'
for n in LOCKED + KEEP: assert mesh_hash(bpy.data.objects[n]) == H0[n], 'locked/kept mesh changed: ' + n
for o in bpy.data.objects:
    assert [list(r) for r in o.matrix_world] == MW0[o.name], 'origin moved: ' + o.name
    if o.type == 'MESH': assert o.data.name == MESHNAME0[o.name], 'mesh datablock renamed: ' + o.name
assert set(o.name for o in bpy.data.objects) == set(MW0), 'object set changed'
LOG['palette'] = PALETTE; LOG['source'] = SRC_PATH; LOG['blender'] = bpy.app.version_string
LOG['tris'] = {o.name: tris_of(o.data) for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith('COL')}
LOG['tris_total_visual'] = sum(LOG['tris'].values())
sc['start_ship_version'] = 'start_ship_whimsy_v5_1'; sc['source_blend'] = SRC_PATH
json.dump(LOG, open(os.path.join(OUT_DIR, 'logs', 'build_log.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=True, copy=True)
print('BUILD_OK', OUT_BLEND, 'skipped', LOG['skipped'])
