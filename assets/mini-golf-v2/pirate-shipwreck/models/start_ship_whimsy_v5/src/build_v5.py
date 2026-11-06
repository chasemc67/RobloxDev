# Start ship v3_2 -> whimsy v5 (visual-only pass, Nov 5 2026).
# "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup <abs>\source_v3_2.blend --python build_v5.py -- <abs out_blend> <abs out_dir>
# Opens source_v3_2.blend (NEVER saved over: save_as copy to a different path, asserted) and edits in memory:
#   * Hull belly: horizontal widening (world Z, about the heeled centreline z = Y*tan15) of 15% at/below world Y6 (waterline -0.6 inside),
#     smooth to 0% at world Y18 (6 below the Y24 deck) -> deck footprint / walk surfaces untouched. Same space-warp applied to every
#     existing hull-hugging visual mesh (Prop_* + Rigging) so their contact is preserved. DeckCabin, Ramps, Pier, RockBumper, Dressing NOT touched.
#   * Prop_Figurehead: vertices rebuilt (same object/mesh/origin) -> chunky grinning coral octopus, 3 tentacles wrapping the bowsprit.
#   * Prop_Stovepipe: vertices rebuilt (same origin) -> lopsided double-elbow pipe with a tilted hat.
#   * Rigging: only the main crow's nest components rotated to a 12 deg tilt (same object/origin).
#   * NEW visual-only meshes in Props: ShipV5_SheerRise, ShipV5_SternCurl, ShipV5_MastZigzag, ShipV5_Telescope, ShipV5_BowEyes, ShipV5_Patches,
#     ShipV5_SailPatches, ShipV5_SailEmblem, ShipV5_YardNest, ShipV5_Bottle, ShipV5_Hammock.
#   * Collision collection: NOT touched (asserted: every collider's mesh hash unchanged at save time).
import bpy, bmesh, sys, os, json, math, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import *
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

A = sys.argv[sys.argv.index('--') + 1:]; OUT_BLEND = os.path.abspath(A[0]); OUT_DIR = os.path.abspath(A[1])
SRC_PATH = os.path.abspath(bpy.data.filepath)
assert OUT_BLEND != SRC_PATH and os.path.basename(OUT_BLEND) != 'source_v3_2.blend', 'refusing to overwrite source'
os.makedirs(os.path.join(OUT_DIR, 'logs'), exist_ok=True)
sc = bpy.context.scene; LOG = {'notes': [], 'changes': {}, 'skipped': []}
def note(*a):
    s = ' '.join(str(x) for x in a); print('NOTE', s); LOG['notes'].append(s)
rng = np.random.RandomState(5005)
def smooth(t): t = min(1.0, max(0.0, t)); return t * t * (3 - 2 * t)

# ------------------------------------------------------------------ collision fingerprint (must be identical at save)
def col_hash():
    h = hashlib.sha256()
    for o in sorted(bpy.data.collections['Collision'].objects, key=lambda o: o.name):
        n = len(o.data.vertices); co = np.zeros(n * 3, np.float32); o.data.vertices.foreach_get('co', co)
        h.update(o.name.encode()); h.update(co.tobytes()); h.update(np.array([v for r in o.matrix_world for v in r], np.float64).tobytes())
    return h.hexdigest()
COL0 = col_hash()

# ------------------------------------------------------------------ palette (8x8 cells of 32 px, discovered from UVs as in build_v3/v3_1)
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
NEWMATS = {'Coral': (230, 120, 100), 'PatchBlue': (90, 130, 170), 'PatchTeal': (70, 150, 140)}
free = [i for i in range(64) if i not in set(CELL.values())]
for (nm, rgb), ci in zip(NEWMATS.items(), free):
    m = MATS['Wood'].copy(); m.name = nm; set_mat_rgb(m, rgb); MATS[nm] = m; CELL[nm] = ci; paint(ci, rgb)
    note('new material', nm, rgb, 'palette cell', ci)
assert list(MATS['Brass']['rgb']) == [200, 160, 70] and list(MATS['WoodDk']['rgb']) == [80, 50, 30] and list(MATS['HullWood']['rgb']) == [130, 90, 55]
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

# ------------------------------------------------------------------ mesh helpers (from build_v31)
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
COLL = bpy.data.collections['Props']
def tris_of(me): return sum(len(p.vertices) - 2 for p in me.polygons)
def make_prop(name, mb, note_txt=''):
    assert name.startswith('ShipV5_') and name not in bpy.data.objects, name
    V = np.array(mb.V); pv = np.array(((V[:, 0].min() + V[:, 0].max()) / 2, (V[:, 1].min() + V[:, 1].max()) / 2, V[:, 2].min()))
    mb.V = [tuple(np.array(v) - pv) for v in mb.V]
    me = bpy.data.meshes.new(name); sk = mb_to_mesh(mb, me); ob = bpy.data.objects.new(name, me); ob.location = Vector(pv)
    COLL.objects.link(ob); ob['note'] = note_txt; ob['visual_only'] = True
    LOG['changes'][name] = dict(kind='NEW visual-only prop', tris=tris_of(me), pivot_roblox=list(np.round(Binv(pv), 3)), note=note_txt, skipped_faces=sk)
    note('NEW', name, 'tris', tris_of(me), 'skipped', sk); return ob
def replace_prop_mesh(name, mb, note_txt):
    """rebuild an EXISTING prop's mesh in place: same object, same mesh datablock, same origin/matrix (mb in Blender world coords)."""
    ob = bpy.data.objects[name]; me = ob.data; mw0 = [list(r) for r in ob.matrix_world]; t0 = tris_of(me)
    inv = ob.matrix_world.inverted(); mb.V = [tuple(inv @ Vector(v)) for v in mb.V]
    bm = bmesh.new(); bm.to_mesh(me); bm.free(); me.materials.clear(); sk = mb_to_mesh(mb, me)
    assert [list(r) for r in ob.matrix_world] == mw0
    old = ob.get('note', ''); ob['note'] = note_txt
    LOG['changes'][name] = dict(kind='EDITED existing prop (vertices rebuilt, same object/mesh/origin)', tris_before=t0, tris_after=tris_of(me), note=note_txt, prev_note=old, skipped_faces=sk)
    note('EDIT', name, t0, '->', tris_of(me))

# ------------------------------------------------------------------ scene BVH helpers (Roblox coords in/out)
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
    """closed slab between profile curves top/bot [(z,y)] extruded x0..x1, all quads (no concave ngons)"""
    n = len(top); P = lambda x, zy: (x, zy[1], zy[0])
    for k in range(n - 1):
        for x in (x0, x1):
            q = [P(x, top[k]), P(x, top[k + 1]), P(x, bot[k + 1]), P(x, bot[k])]; mb._add(q, [(0, 1, 2, 3)], [mat])
        mb._add([P(x0, top[k]), P(x0, top[k + 1]), P(x1, top[k + 1]), P(x1, top[k])], [(0, 1, 2, 3)], [mat])
        mb._add([P(x0, bot[k]), P(x0, bot[k + 1]), P(x1, bot[k + 1]), P(x1, bot[k])], [(0, 1, 2, 3)], [mat])
    for k in (0, n - 1):
        mb._add([P(x0, top[k]), P(x1, top[k]), P(x1, bot[k]), P(x0, bot[k])], [(0, 1, 2, 3)], [mat])
def mb_bvh(mb):
    return BVHTree.FromPolygons([tuple(v) for v in mb.V], [list(f) for f in mb.F])
VIS_NAMES = [o.name for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith('COL')]
def obj_bvh(n):
    bm = world_bm(bpy.data.objects[n]); T = BVHTree.FromBMesh(bm); bm.free(); return T
def overlaps(mb, names):
    T = mb_bvh(mb); out = {}
    for n in names:
        k = len(T.overlap(obj_bvh(n)))
        if k: out[n] = k
    return out

# ------------------------------------------------------------------ measurements reused before/after the hull warp
def section_width(x, Y, T):
    a = T.ray(np.array((x, Y, -300.0)), (0, 0, 1), 700); b = T.ray(np.array((x, Y, 300.0)), (0, 0, -1), 700)
    if a is None or b is None: return None
    return dict(z_high=round(float(a[0][2]), 3), z_low=round(float(b[0][2]), 3), width=round(float(b[0][2] - a[0][2]), 3))
STATIONS = [-140.0, -100.0, -60.0, -20.0, 20.0, 60.0, 100.0, 130.0]
LEVELS = [-0.6, 6.0, 12.0, 18.0, 23.0]
def widths():
    T = SBVH(['Hull']); return {'Y%.1f' % Y: {'x%d' % x: section_width(x, Y, T) for x in STATIONS} for Y in LEVELS}
def obb_list():
    out = []
    for o in bpy.data.collections['Collision'].objects:
        if not o.name.startswith('COL_HullExt'): continue
        W = np.array([Binv(o.matrix_world @ v.co) for v in o.data.vertices]); c = W.mean(0)
        d = sorted([W[i] - W[0] for i in range(1, len(W))], key=lambda v: np.linalg.norm(v))[:3]
        ax = [nrm(v) for v in d]; hs = [np.linalg.norm(v) / 2 for v in d]; out.append((o.name, c, np.array(ax), np.array(hs)))
    return out
def outside_hullext(P, obbs):
    best = np.full(len(P), 1e9)
    for n, c, ax, hs in obbs:
        q = (P - c) @ ax.T; d = np.maximum(np.abs(q) - hs, 0); best = np.minimum(best, np.linalg.norm(d, axis=1))
    return best
def hull_outer_samples():
    """outer hull surface samples below Y18 (where the warp acts): horizontal rays from both sides"""
    T = SBVH(['Hull']); P = []
    for x in np.arange(-158.0, 150.0, 4.0):
        for Y in np.arange(-0.5, 18.01, 1.5):
            for z0, dz in ((-300.0, 1), (300.0, -1)):
                r = T.ray(np.array((x, Y, z0)), (0, 0, dz), 700)
                if r is not None: P.append(r[0])
    return np.array(P)
OBB = obb_list()
def hullext_report():
    P = hull_outer_samples(); d = outside_hullext(P, OBB)
    return dict(samples=int(len(P)), max_outside=round(float(d.max()), 3), p95_outside=round(float(np.percentile(d, 95)), 3),
                mean_outside=round(float(d.mean()), 3), n_over_1_stud=int((d > 1.0).sum()), n_over_2_studs=int((d > 2.0).sum()),
                worst=[list(np.round(P[i], 2)) + [round(float(d[i]), 3)] for i in np.argsort(-d)[:8]])
def ov_count(a, b): return len(obj_bvh(a).overlap(obj_bvh(b)))
LOCKED = ['DeckCabin', 'RampFlight1', 'RampLanding', 'RampFlight2']
W_BEFORE = widths(); HX_BEFORE = hullext_report()
OV_BEFORE = {n: ov_count('Hull', n) for n in LOCKED + ['Pier', 'RockBumper', 'Dressing']}
note('hull overlaps with locked/static before', OV_BEFORE, 'hullext outside before', HX_BEFORE['max_outside'])

# ================================================================== 1a  HULL BELLY WARP
KW = 0.15; YA, YB = 6.0, 18.0; TAN = math.tan(PHI)
def wY(Y): return np.where(Y <= YA, 1.0, np.where(Y >= YB, 0.0, 1.0 - np.vectorize(smooth)((Y - YA) / (YB - YA))))
def gX(x, stern_lo=0.35):
    x = np.asarray(x, float)
    st = stern_lo + (1 - stern_lo) * np.vectorize(smooth)((x + 160.0) / 30.0)
    bw = 1.0 - np.vectorize(smooth)((x - 105.0) / 45.0)
    return np.minimum(st, bw)
def warp(P, stern_lo=0.35):
    P = np.array(P, float); zc = P[:, 1] * TAN; f = 1.0 + KW * wY(P[:, 1]) * gX(P[:, 0], stern_lo)
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
        assert np.allclose(np.array(o.matrix_world.to_3x3()), np.eye(3)), o.name
        Wb = L + t; R = np.column_stack([Wb[:, 0], Wb[:, 2], -Wb[:, 1]]); Q = warp(R, stern_lo)
        Wn = np.column_stack([Q[:, 0], -Q[:, 2], Q[:, 1]]); Ln = Wn - t
        dmax = float(np.max(np.abs(Ln - L))) if n else 0.0
        if dmax > 1e-6:
            me.vertices.foreach_set('co', Ln.astype(np.float32).ravel()); me.update(); moved[o.name] = round(dmax, 4)
    return moved
STERN_LO = 0.35
moved = apply_warp(STERN_LO)
OV_AFTER = {n: ov_count('Hull', n) for n in OV_BEFORE}
if any(OV_AFTER[n] > OV_BEFORE[n] for n in OV_AFTER):
    note('warp created new overlaps', OV_AFTER, '-> retry with stern taper 0.0')
    STERN_LO = 0.0; moved = apply_warp(STERN_LO); OV_AFTER = {n: ov_count('Hull', n) for n in OV_BEFORE}
W_AFTER = widths(); HX_AFTER = hullext_report()
LOG['hull_warp'] = dict(k=KW, full_below_world_Y=YA, zero_above_world_Y=YB, centreline='z = Y*tan(15deg) (heeled hull frame z=0)',
    x_taper='1.0 for x in [-130,105]; stern end factor %.2f at x-160; bow fades to 0 by x150 (stem/bowsprit/figurehead untouched)' % STERN_LO,
    moved_objects_max_disp=moved, overlaps_before=OV_BEFORE, overlaps_after=OV_AFTER, widths_before=W_BEFORE, widths_after=W_AFTER,
    hullext_outside_before=HX_BEFORE, hullext_outside_after=HX_AFTER)
note('warp moved', moved, 'overlaps after', OV_AFTER, 'hullext outside after', HX_AFTER['max_outside'])
for o in bpy.data.objects:
    if o.name in moved: o['note_v5'] = 'v5: vertices moved by the hull-belly widening warp (same origin/topology/UV/materials)'

# visual BVH of the warped scene (for placement)
VIS = SBVH(VIS_NAMES)
TEE = Binv(bpy.data.objects['Tee1'].matrix_world.translation); TEE_EYE = TEE + np.array((0, 5.0, 0))

# ================================================================== 1b  BANANA SHEER: ShipV5_SheerRise (bow cap-rail rise + stern transom crest)
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
RISE = 4.0
sr = MB('sheer'); BOWX = np.arange(94.0, 154.1, 4.0); bow_lines = {0: [], 1: []}
for x in BOWX:
    t = rail_tops(['Prop_CapRails'], x)
    if t is None: continue
    for i in (0, 1): bow_lines[i].append((x, t[i][0], t[i][1], t[i][2]))
for i in (0, 1):
    L_ = bow_lines[i]
    if len(L_) < 4: LOG['skipped'].append('bow sheer side %d: cap rail not found' % i); continue
    path = []; rects = []; caps = []; crects = []
    for (x, z, y, w) in L_:
        h = RISE * smooth((x - 86.0) / 64.0); hw = max(0.3, min(0.55, 0.35 * w))
        path.append((x, y + (h - 0.35) / 2, z)); rects.append((hw, (h + 0.35) / 2))
        caps.append((x, y + h + 0.05, z)); crects.append((hw + 0.22, 0.22))
    sr.tube(path, 0, 'HullWood', rect=rects, up=(0, 1, 0))
    sr.tube(caps, 0, 'WoodDk', rect=crects, up=(0, 1, 0))
    LOG.setdefault('sheer', {})['bow_side%d' % i] = dict(x0=L_[0][0], x1=L_[-1][0], cap_top_y=[round(a[2], 2) for a in L_], rise_at_end=round(RISE * smooth((L_[-1][0] - 86) / 64), 2))
# stern: transom crest board across the top of the stern castle + rising side strakes
XT = -160.6
prof = []
Tst = SBVH(['Prop_SternCastle', 'Hull'])
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
        t = (z - zlo) / (zhi - zlo); top.append((z, env[k] + 1.6 + (RISE - 1.6) * math.sin(math.pi * t))); bot.append((z, env[k] - 1.2))
    poly = top + bot[::-1]
    slab_profile(sr, top, bot, XT - 0.6, XT + 0.6, 'HullWood')
    sr.tube([(XT, y + 0.15, z) for z, y in top], 0, 'WoodDk', rect=[(0.85, 0.3)] * len(top), up=(0, 1, 0))
    zc = (zlo + zhi) / 2; kc = int(np.argmin(np.abs(zz - zc))); STERN = dict(z_lo=zlo, z_hi=zhi, z_mid=float(zc), crest_top_mid=float(top[kc][1]), env_mid=float(env[kc]))
    LOG.setdefault('sheer', {})['stern_crest'] = dict(x=XT, z_range=[round(zlo, 2), round(zhi, 2)], rise_mid=RISE, castle_top_mid=round(float(env[kc]), 2), crest_top_mid=round(float(top[kc][1]), 2))
else:
    LOG['skipped'].append('stern crest: stern castle top not found')
make_prop('ShipV5_SheerRise', sr, 'banana sheer: bow cap-rail rise board (0 at x86 -> +4 at the stem, both sides) + arched transom crest (+1.6 corners, +4 centre). Exterior trim only; walk surfaces untouched.')

# ================================================================== 1c  ShipV5_SternCurl (tall spiral, leaning outboard/aft)
def tall_curl():
    cu = MB('curl')
    if STERN is None: return None
    zc = STERN['z_mid']; base = np.array((XT, STERN['crest_top_mid'] - 1.0, zc))
    up = nrm(tilt((0, 1, 0))); aft = np.array((-1.0, 0, 0))
    H0 = 15.0; LEAN = 4.0; R0 = 7.5; turns = 1.45
    def m2(d, h): return base + d * aft + h * up
    pts = [m2(LEAN * (h / H0) ** 1.3, h) for h in np.linspace(0, H0, 6)]
    Cc = np.array((LEAN + R0, H0)); n = 40
    for i in range(1, n + 1):
        t = i / n; a = math.pi - 2 * math.pi * turns * t; r = R0 * (1 - 0.78 * t)
        pts.append(m2(Cc[0] + r * math.cos(a), Cc[1] + r * math.sin(a)))
    rad = list(np.linspace(2.2, 1.7, 6)) + list(np.linspace(1.7, 0.75, n))
    cu.tube(pts, rad, 'WoodDk', sec=8, up=tuple(np.cross(up, aft)))
    knob_c = m2(Cc[0] + R0 * 0.1, Cc[1] - R0 * 0.05)
    cu.ellipsoid(pts[-1], (1.15, 1.15, 1.15), 'Brass', nu=8, nv=5)
    cu.torus(pts[3], up, 2.25, 0.4, 'Brass', nu=10, nv=4)
    Y = np.array([p[1] for p in pts]); X = np.array([p[0] for p in pts])
    LOG['stern_curl'] = dict(base_roblox=list(np.round(base, 2)), top_y=round(float(Y.max() + 1.7), 2), height_above_base=round(float(Y.max() + 1.7 - base[1]), 2),
                             aft_most_x=round(float(X.min() - 1.7), 2), spiral_outer_diameter=2 * R0, lean='stem leans %.1f studs aft over %.0f; spiral curls aft/down (outboard)' % (LEAN, H0))
    return cu
cu = tall_curl()
if cu is not None: make_prop('ShipV5_SternCurl', cu, 'tall spiral stern curl on the transom crest centre, curling aft (outboard); Prop_SternCurl corner scrolls kept unchanged')
else: LOG['skipped'].append('ShipV5_SternCurl (no stern crest)')

# ================================================================== 1d  Prop_Figurehead -> coral octopus (vertices rebuilt; same object/origin)
hv = np.array([Binv(v.co) for v in bpy.data.objects['Hull'].data.vertices])     # Hull origin at 0 (asserted by warp)
hvh = np.array([untilt(p) for p in hv])
bs_d = nrm(np.array(BS1) - np.array(BS0)); AX = []
for xs in np.arange(158.0, 196.0, 3.0):
    q = hvh[np.abs(hvh[:, 0] - xs) < 1.6]
    if not len(q): continue
    t = (q - np.array(BS0)) @ bs_d; foot = np.array(BS0) + np.outer(t, bs_d); d = np.linalg.norm(q - foot, axis=1)
    sel = q[d < 6.0]
    if len(sel) < 6: continue
    c = sel.mean(0); r = float(np.median(np.linalg.norm(sel - c, axis=1)))
    AX.append((c, r))
note('bowsprit axis samples', [(list(np.round(c, 1)), round(r, 2)) for c, r in AX])
oc = MB('octo')
fh = bpy.data.objects['Prop_Figurehead']; FH0 = Binv(fh.matrix_world.translation); FHh = untilt(FH0)
old_fh = np.array([untilt(Binv(fh.matrix_world @ v.co)) for v in fh.data.vertices])
# head (mantle) in the hull frame, nose under the bowsprit, tucked against the stem
HC = np.array((FHh[0] + 8.0, FHh[1] + 4.0, 0.0))
oc.ellipsoid(HC + np.array((-1.0, 2.6, 0)), (5.6, 6.6, 5.4), 'Coral', R=Rz(math.radians(-28)), nu=12, nv=8)      # bulbous mantle, leaning back
oc.ellipsoid(HC + np.array((1.2, -2.4, 0)), (4.8, 3.6, 4.9), 'Coral', nu=12, nv=6)                                # face / lower head
for sz in (-1, 1):   # big round eyes, white + dark pupil looking forward
    ec = HC + np.array((5.0, -0.6, 2.2 * sz))
    oc.ellipsoid(ec, (1.25, 1.5, 1.25), 'Canvas', nu=8, nv=5)
    oc.ellipsoid(ec + np.array((0.95, -0.1, 0.05 * sz)), (0.5, 0.75, 0.6), 'Shadow', nu=6, nv=4)
    oc.box(ec + np.array((0.6, 1.75, 0)), (1.6, 0.45, 2.4), 'Coral', R=Rx(math.radians(-14 * sz)))              # brow
# grin: thick dark crescent + 3 cream teeth
grin = [HC + np.array((4.1 + 1.6 * math.cos(a) ** 2, -3.6 + 1.1 * (1 - math.cos(a)) * -0.2 + 1.3 * abs(math.sin(a)), 3.4 * math.sin(a))) for a in np.linspace(-1.25, 1.25, 9)]
oc.tube(grin, 0.55, 'Shadow', sec=6)
for zt in (-1.3, 0.0, 1.3):
    oc.box(HC + np.array((5.55, -3.35, zt)), (0.6, 0.75, 0.75), 'Canvas')
# 3 tentacles: from the head base, spiralling forward around the bowsprit (8 sides, tapering)
if len(AX) >= 4:
    AXc = np.array([c for c, r in AX]); AXr = np.array([r for c, r in AX])
    def ax_at(x):
        return np.array([np.interp(x, AXc[:, 0], AXc[:, k]) for k in range(3)]), float(np.interp(x, AXc[:, 0], AXr))
    for k in range(3):
        ph = 2 * math.pi * k / 3 + 0.4; pts = []; rad = []
        x_start = HC[0] + 2.0; x_end = min(AXc[-1, 0], 158.0 + 26.0 + 5.0 * k)
        root = HC + np.array((0.5, -3.8, (k - 1) * 2.8))
        nN = 30
        for i in range(nN + 1):
            t = i / nN; x = x_start + (x_end - x_start) * t; c, rr = ax_at(x)
            a = ph + t * 2 * math.pi * 1.35; tr = 1.55 * (1 - 0.7 * t)
            ring = c + (rr + tr * 0.75) * np.array((0, math.cos(a), math.sin(a)))
            if t < 0.18: ring = root + (ring - root) * smooth(t / 0.18)
            pts.append(ring); rad.append(tr)
        tipd = nrm(pts[-1] - pts[-2]); curl_c = pts[-1]
        for j in range(1, 5):   # little curled tip
            a = j * 0.9; pts.append(curl_c + tipd * 0.7 * math.sin(a) + np.array((0, 0.7 * (1 - math.cos(a)), 0))); rad.append(rad[-1] * 0.85)
        oc.tube(pts, rad, 'Coral', sec=8, up=(0, 0, 1))
    # 3 short hanging/curling tentacles under the head against the stem
    for k, zz in enumerate((-3.2, 0.0, 3.2)):
        root = HC + np.array((-0.5, -4.0, zz)); pts = []; rad = []
        for i in range(12):
            t = i / 11; a = t * 1.7 * math.pi
            pts.append(root + np.array((1.5 * math.sin(a) * (1 - 0.5 * t) + 0.8 * t, -6.0 * t + 1.4 * (1 - math.cos(a)) * t, zz * 0.45 * t))); rad.append(1.35 * (1 - 0.72 * t))
        oc.tube(pts, rad, 'Coral', sec=8, up=(0, 0, 1))
else:
    LOG['skipped'].append('octopus bowsprit tentacles: bowsprit axis not found')
oc.V = [B(tilt(Binv(v))) for v in oc.V]   # MB stores Blender coords of the hull-frame build -> tilt into the world
replace_prop_mesh('Prop_Figurehead', oc, 'v5: original chunky grinning coral octopus (230,120,100), 3 tentacles spiralling forward around the bowsprit (8 sides), 3 curled tentacles under the head; same object/origin')
LOG['octopus'] = dict(head_centre_hull=list(np.round(HC, 2)), bowsprit_samples=len(AX), bowsprit_radius_median=round(float(np.median([r for c, r in AX])), 2) if AX else None,
                      old_bbox_hull=[list(np.round(old_fh.min(0), 2)), list(np.round(old_fh.max(0), 2))])

# ================================================================== 2  Mast: tilt the crow's nest to 12 deg, zigzag topmast, bent brass telescope
rig = bpy.data.objects['Rigging']; rme = rig.data
bm = bmesh.new(); bm.from_mesh(rme); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table(); mnames = [m.name for m in rme.materials]
seen = set(); comps = []
for f in bm.faces:
    if f in seen: continue
    st = [f]; c = []; seen.add(f)
    while st:
        a = st.pop(); c.append(a)
        for e in a.edges:
            for g in e.link_faces:
                if g not in seen: seen.add(g); st.append(g)
    comps.append(c)
nest = []; stump_post = None; spl = None
for c in comps:
    vi = sorted(set(v.index for g in c for v in g.verts)); P = np.array([untiltR(Binv(bm.verts[i].co)) for i in vi])
    rad = np.hypot(P[:, 0] - MAIN_X, P[:, 2]); mats = set(mnames[g.material_index] for g in c)
    if P[:, 1].min() >= 84 and P[:, 1].max() <= 104 and rad.max() <= 9.5 and rad.max() > 3.6 and not (mats & {'Canvas', 'CanvasDk'}): nest.append((c, vi, P))
for p in rme.polygons:
    mn = rme.materials[p.material_index].name
    for vi in p.vertices:
        q = untiltR(Binv(rme.vertices[vi].co))
        if abs(q[0] - MAIN_X) < 4.2 and abs(q[2]) < 4.2 and q[1] > 90:
            if mn == 'Post': stump_post = max(stump_post or -1e9, q[1])
            if mn == 'PostLt': spl = max(spl or -1e9, q[1])
note('nest comps', len(nest), [ (list(np.round(P.min(0), 1)), list(np.round(P.max(0), 1))) for c, vi, P in nest], 'stump post top', stump_post, 'splinters', spl)
NEST = None
if nest:
    allP = np.vstack([P for c, vi, P in nest]); piv = np.array(((allP[:, 0].min() + allP[:, 0].max()) / 2, allP[:, 1].min(), (allP[:, 2].min() + allP[:, 2].max()) / 2))
    ns = np.zeros(3); ar = 0.0
    for c, vi, P in nest:
        for g in c:
            n_ = untiltR(Binv(g.normal)); a_ = g.calc_area()
            if abs(n_[1]) > 0.8: ns += np.sign(n_[1]) * n_ * a_; ar += a_
    a0 = nrm(ns) if ar > 0 else np.array((0, 1.0, 0)); th0 = math.degrees(math.acos(min(1.0, abs(a0[1]))))
    up = np.array((0, 1.0, 0)); delta = 12.0 - th0
    k_ = np.cross(up, a0)
    if np.linalg.norm(k_) < 1e-3 or th0 < 0.5: k_ = np.array((0, 0, -1.0))   # lean the top toward +X (bow)
    Rn = Raxis(k_, math.radians(delta))
    for c, vi, P in nest:
        for i in vi:
            q = untiltR(Binv(bm.verts[i].co)); q2 = piv + Rn @ (q - piv); bm.verts[i].co = Vector(B(tiltR(q2)))
    bm.to_mesh(rme); rme.update()
    tubP = max((P for c, vi, P in nest), key=lambda P: (np.hypot(P[:, 0] - MAIN_X, P[:, 2]).max(), len(P)))   # main tub (widest component)
    a1 = Rn @ a0; th1 = math.degrees(math.acos(min(1.0, abs(a1[1]))))
    NEST = dict(components=len(nest), verts=int(sum(len(vi) for c, vi, P in nest)), pivot_rig=list(np.round(piv, 3)), tilt_before_deg=round(th0, 2), tilt_after_deg=round(th1, 2),
                axis=list(np.round(nrm(k_), 3)), R=Rn, rim_r=float(np.hypot(tubP[:, 0] - MAIN_X, tubP[:, 2]).max()), rim_h=float(tubP[:, 1].max() - piv[1]))
    LOG['changes']['Rigging'] = dict(kind='EDITED existing mesh: main crow\'s nest components rotated about their base centre (same object/origin/topology/UV/materials)',
                                     nest={k: v for k, v in NEST.items() if k != 'R'}, tris=tris_of(rme))
    note('nest tilt', th0, '->', th1)
else:
    LOG['skipped'].append('crow\'s nest tilt: nest components not found in Rigging')
bm.free()
# zigzag jury topmast out of the splinter crown (rig frame, tiltR)
mz = MB('mast')
if stump_post is not None:
    b0 = np.array((MAIN_X, stump_post - 3.0, 0.0)); segs = [(13.0, -15.0, 1.75, 1.45), (11.5, 21.0, 1.45, 1.15), (9.0, -9.0, 1.15, 0.9)]
    p = b0; joints = []
    for L_, ang, r0, r1 in segs:
        d = np.array((math.sin(math.radians(-ang)), math.cos(math.radians(ang)), 0.0)); q = p + d * L_
        mz.frustum(p - d * 0.6, q + d * 0.6, r0, r1, 'Post', sec=8, tf=tiltR, up=(0, 0, 1)); joints.append((q, d, r1)); p = q
    for q, d, r in joints[:-1]:
        for o_ in (-0.9, 0.9): mz.torus(q + d * o_, d, r + 0.35, 0.35, 'RopeLt', nu=10, nv=4, tf=tiltR)
        mz.frustum(q - d * 0.25, q + d * 0.25, r + 0.42, r + 0.42, 'Iron', sec=8, tf=tiltR, up=(0, 0, 1))
    mz.frustum(b0 + np.array((0, 1.2, 0)), b0 + np.array((0, 2.4, 0)), 2.45, 2.45, 'Iron', sec=8, tf=tiltR, up=(0, 0, 1))
    top = joints[-1][0]; mz.ellipsoid(top + np.array((0, 0.8, 0)), (1.25, 1.1, 1.25), 'Brass', nu=8, nv=5, tf=tiltR)
    make_prop('ShipV5_MastZigzag', mz, 'jury-rigged zigzag topmast out of the main-mast splinter crown: 3 Post segments, 2 zigzag bends (rope lashings + iron bands), brass truck knob')
    LOG['mast_zigzag'] = dict(base_rig=list(np.round(b0, 2)), top_rig=list(np.round(top, 2)), bends=2, top_world_y=round(float(tiltR(top)[1]), 2))
else:
    LOG['skipped'].append('ShipV5_MastZigzag: stump top not found')
# bent brass telescope resting on the tilted nest rim, pointing to the bow
if NEST is not None:
    piv = np.array(NEST['pivot_rig']); R = NEST['R']; rr = NEST['rim_r'] - MAIN_X * 0 ; rh = NEST['rim_h']
    def nl(v): return piv + R @ np.asarray(v, float)
    p0 = nl((rr - 2.6 - (piv[0] - MAIN_X), rh + 0.2, 1.6)); p1 = nl((rr + 0.8 - (piv[0] - MAIN_X), rh + 0.9, 1.9))
    d1 = nrm(p1 - p0); kink = Raxis((0, 0, 1), math.radians(-24)) @ d1; p2 = p1 + kink * 3.4
    te = MB('scope')
    te.tube([p0, p1], [0.45, 0.5], 'Brass', sec=8, tf=tiltR)
    te.tube([p1 - d1 * 0.3, p2], [0.62, 0.72], 'Brass', sec=8, tf=tiltR)
    te.torus(p1, d1, 0.62, 0.22, 'Iron', nu=8, nv=4, tf=tiltR)
    te.frustum(p2 - kink * 0.05, p2 + kink * 0.18, 0.6, 0.6, 'Shadow', sec=8, tf=tiltR)
    te.torus(p2, kink, 0.75, 0.2, 'Brass', nu=8, nv=4, tf=tiltR)
    make_prop('ShipV5_Telescope', te, 'bent brass telescope (24 deg kink) resting on the 12-deg-tilted crow\'s nest rim, pointing to the bow')

# ================================================================== 3  Bow sleepy face: ShipV5_BowEyes
ey = MB('eyes'); EYES = []; EYE_OK = ('Hull', 'Prop_BowRaise', 'Prop_SheerWale')
for side in (-1, 1):
    best = None
    dbg = []
    for x in (136.0, 132.0, 140.0, 128.0, 124.0, 144.0, 120.0):
        t = rail_tops(['Prop_CapRails'], x)
        if t is None: continue
        z_r, y_r, _ = t[0 if side < 0 else 1]
        for dy in (5.8, 6.6, 7.4, 5.0, 8.4, 9.4):
            Y = y_r - dy; r = VIS.ray(np.array((x, Y, 300.0 * side)), (0, 0, -side), 600)
            if r is None or r[3] not in EYE_OK: dbg.append((x, round(Y, 1), None if r is None else r[3])); continue
            ok = True
            for du, dv in ((2.9, 0), (-2.9, 0), (0, 2.9), (0, -2.9)):
                r2 = VIS.ray(np.array((x + du, Y + dv, 300.0 * side)), (0, 0, -side), 600)
                if r2 is None or r2[3] not in EYE_OK or abs(r2[0][2] - r[0][2]) > 2.4: ok = False; dbg.append((x, round(Y, 1), 'corner', None if r2 is None else r2[3], None if r2 is None else round(float(r2[0][2] - r[0][2]), 2)))
            if ok: best = (x, Y, r); break
        if best: break
    if best is None: LOG['skipped'].append('bow eye side %d: no clear spot' % side); LOG.setdefault('bow_eye_dbg', {})[side] = dbg[:60]; continue
    x, Y, r = best; p, n = r[0], r[1]
    if n[2] * side < 0: n = -n
    R = sframe(n, (1, 0, 0)); u, v = R[:, 0], R[:, 1]
    if v[1] < 0: v = -v
    u = np.cross(v, n)
    ey.torus(p + n * 0.35, n, 2.55, 0.6, 'Brass', nu=12, nv=5)
    ey.frustum(p - n * 0.6, p + n * 0.45, 2.15, 2.15, 'Shadow', sec=12, up=tuple(v))
    ey.frustum(p + n * 0.4 - v * 1.05 - u * 0.75 * side, p + n * 0.62 - v * 1.05 - u * 0.75 * side, 0.45, 0.45, 'Canvas', sec=6, up=tuple(v))
    droop = Raxis(n, math.radians(-9 * side))
    lid0 = []; lid1 = []
    for a in np.linspace(0, math.pi, 9):
        q = droop @ (u * 2.75 * math.cos(a) + v * (2.75 * math.sin(a) * 0.98)) - droop @ (v * 0.35)
        lid0.append(p + q + n * 0.55); lid1.append(p + q * 0.93 + n * 1.35)
    ey.loft([lid0, lid1], 'Wood')
    ec = p + n * 1.15 - droop @ (v * 0.35)
    ey.box(ec, (5.9, 0.55, 0.75), 'WoodDk', R=droop @ np.column_stack([u, v, n]))
    EYES.append(dict(side='low(+Z)' if side > 0 else 'high(-Z)', centre=list(np.round(p, 2)), normal=list(np.round(n, 3)), below_cap_top=round(float(t[0 if side < 0 else 1][1] - Y), 2)))
if EYES: make_prop('ShipV5_BowEyes', ey, 'sleepy bow face: 2 round brass porthole eyes (dark glass + highlight) with droopy half-lid planks, high on the bow flanks')
LOG['bow_eyes'] = EYES

# ================================================================== 4  ShipV5_Patches: blue/teal hull patches with oversized brass nails
pa = MB('patches'); PATCHES = []
CANDS = [(1, -82.0, 11.0, 'PatchBlue', 8), (1, 84.0, 13.0, 'PatchTeal', -10), (1, -110.0, 9.0, 'PatchTeal', 6), (1, 104.0, 16.0, 'PatchBlue', 12),
         (-1, -66.0, 12.0, 'PatchTeal', -7), (-1, 86.0, 14.0, 'PatchBlue', 9), (1, -10.0, 2.5, 'PatchBlue', 5), (-1, 110.0, 18.0, 'PatchTeal', -6),
         (1, 70.0, 6.0, 'PatchTeal', 10), (-1, -100.0, 9.0, 'PatchBlue', -9)]
for side, x, Y, mat, rot in CANDS:
    if len(PATCHES) >= 5: break
    W_, H_ = 7.5, 5.5
    ru = np.array((math.cos(math.radians(rot)), math.sin(math.radians(rot))))
    grid = {}; ok = True
    for i in range(4):
        for j in range(3):
            a = (i / 3 - 0.5) * W_; b = (j / 2 - 0.5) * H_
            dx = a * ru[0] - b * ru[1]; dy = a * ru[1] + b * ru[0]
            r = VIS.ray(np.array((x + dx, Y + dy, 300.0 * side)), (0, 0, -side), 600)
            if r is None or r[3] != 'Hull' or r[0][1] < WATER_Y + 1.0: ok = False; break
            n = r[1] if r[1][2] * side > 0 else -r[1]; grid[(i, j)] = (r[0], n)
        if not ok: break
    if not ok: continue
    def fn(uu, vv, off=0.0):
        i = min(2, int(uu * 3)); j = min(1, int(vv * 2)); fu = uu * 3 - i; fv = vv * 2 - j
        P00, N00 = grid[(i, j)]; P10, N10 = grid[(i + 1, j)]; P01, N01 = grid[(i, j + 1)]; P11, N11 = grid[(i + 1, j + 1)]
        P = (1 - fu) * (1 - fv) * P00 + fu * (1 - fv) * P10 + (1 - fu) * fv * P01 + fu * fv * P11
        N = nrm((1 - fu) * (1 - fv) * N00 + fu * (1 - fv) * N10 + (1 - fu) * fv * N01 + fu * fv * N11)
        return P + N * off, N
    pa.thick_surface(lambda uu, vv: fn(uu, vv, 0.15), 3, 2, 0.7, mat, side_mat=mat)
    for uu, vv in ((0.07, 0.1), (0.93, 0.1), (0.07, 0.9), (0.93, 0.9), (0.5, 0.08), (0.5, 0.92)):
        P, N = fn(uu, vv, 0.0); pa.frustum(P + N * 0.3, P + N * 0.85, 0.62, 0.52, 'Brass', sec=6); pa.frustum(P + N * 0.85, P + N * 1.08, 0.52, 0.22, 'Brass', sec=6)
    PATCHES.append(dict(side='low(+Z)' if side > 0 else 'high(-Z)', x=x, Y=Y, mat=mat, size=[W_, H_], rot_deg=rot))
make_prop('ShipV5_Patches', pa, '%d hull patches (blue 90,130,170 / teal 70,150,140), 0.7 slab (-0.2..+0.5 about the hull surface) of the widened hull, 6 oversized brass nails each' % len(PATCHES))
LOG['patches'] = PATCHES
if len(PATCHES) < 4: LOG['skipped'].append('hull patches: only %d placed' % len(PATCHES))

# ================================================================== 5  sails: big square patches + original skull & crossbones (rig frame surfaces from build_v31)
SAG = Raxis((1, 0, 0), math.radians(-9))
def tf_sag(p): return tiltR(np.asarray((MAIN_X, 86.0, 0.0)) + SAG @ (np.asarray(p, float) - np.asarray((MAIN_X, 86.0, 0.0))))
def sail_S(x0, yy, ln, sh, bulge_k=0.13):
    bulge = bulge_k * sh
    def S(u, v):
        z = (u - 0.5) * ln * 0.88 * (1 - 0.06 * v); y = yy - 0.9 - v * sh
        x = x0 + 1.4 + bulge * math.sin(math.pi * u) * math.sin(math.pi * (0.1 + 0.85 * v)); return np.array((x, y, z))
    return S
def sail_fn(S):
    def fn(u, v, off=0.0):
        e = 1e-3; p = S(u, v); du = S(min(1, u + e), v) - S(max(0, u - e), v); dv = S(u, min(1, v + e)) - S(u, max(0, v - e))
        n = nrm(np.cross(dv, du))
        if n[0] < 0: n = -n
        return p + n * off, n
    return fn
SAILDEF = {'main_lower': ((MAIN_X, 62.0, 58.0, 30.0), tiltR), 'fore_lower': ((FORE_X, 52.0, 46.0, 26.0), tiltR), 'main_upper': ((MAIN_X, 86.0, 44.0, 20.0), tf_sag)}
RIGT = SBVH(['Rigging'])
def on_sail(key, uv_pts):
    (x0, yy, ln, sh), tf = SAILDEF[key]; fn = sail_fn(sail_S(x0, yy, ln, sh)); miss = 0
    for u, v in uv_pts:
        p, n = fn(u, v, 0.0); pw = tf(p); nw = nrm(tf(p + n) - pw)
        r = RIGT.ray(pw + nw * 3.0, -nw, 6.0)
        if r is None or abs(r[2] - 2.8) > 0.06: miss += 1
    return miss
sp = MB('sailpatch'); SP = []
for key, (ua, ub, va, vb), mat in (('main_upper', (0.12, 0.30, 0.20, 0.55), 'PatchBlue'), ('main_lower', (0.585, 0.715, 0.34, 0.56), 'PatchTeal'), ('fore_lower', (0.20, 0.36, 0.58, 0.86), 'CanvasDk')):
    (x0, yy, ln, sh), tf = SAILDEF[key]; fn = sail_fn(sail_S(x0, yy, ln, sh))
    pts = [(ua + (ub - ua) * i / 4, va + (vb - va) * j / 4) for i in range(5) for j in range(5)]; miss = on_sail(key, pts)
    if miss: LOG['skipped'].append('sail patch %s: %d/25 samples off-sail -> skipped' % (key, miss)); continue
    for sg in (1, -1):
        sp.thick_surface(lambda u, v: fn(ua + (ub - ua) * u, va + (vb - va) * v, sg * 0.22), 4, 4, 0.28, mat, tf=tf)
        for (u, v) in ((ua + 0.012, va + 0.03), (ub - 0.012, va + 0.03), (ua + 0.012, vb - 0.03), (ub - 0.012, vb - 0.03)):   # dark stitch crosses
            p, n = fn(u, v, sg * 0.40)
            for a in (45, -45):
                Rr = frame_from(n, (0, math.cos(math.radians(a)), math.sin(math.radians(a))))
                sp.box(p, (1.2, 0.28, 0.12), 'WoodDk', R=Rr, tf=tf)
    SP.append(dict(sail=key, uv=[ua, ub, va, vb], size_studs=[round((ub - ua) * ln * 0.88, 1), round((vb - va) * sh, 1)], mat=mat))
make_prop('ShipV5_SailPatches', sp, 'large square sail patches (both faces, slab 0.08-0.36 from the sail mid-surface = embedded through the 0.2 sail face) with dark stitch crosses')
LOG['sail_patches'] = SP
# skull & crossbones (original simple emblem) on the bare top band of the main lower sail (visible above the bulwark in 3q and from the tee), both faces
EMB_SAIL = 'main_lower'; em = MB('emblem'); (x0, yy, ln, sh), tf = SAILDEF[EMB_SAIL]; S = sail_S(x0, yy, ln, sh); fn = sail_fn(S)
UC, VC = 0.485, 0.195; ES = 0.64; EMB_CHK = []
def to_uv(zl, yl):
    v = VC - yl / sh; return (UC + zl / (ln * 0.88 * (1 - 0.06 * v)), v)
def slab2d(poly, off0, off1, mat, sg, emax=2.0, nr=2):
    """convex 2D shape -> slab that follows the curved sail: boundary edges subdivided to <=emax, radial fan with nr rings (no large flat faces)"""
    bd = []
    for k in range(len(poly)):
        a_ = np.array(poly[k]); b_ = np.array(poly[(k + 1) % len(poly)]); m = max(1, int(math.ceil(np.linalg.norm(b_ - a_) / emax)))
        bd += [a_ + (b_ - a_) * i / m for i in range(m)]
    EMB_CHK.extend(to_uv(q[0], q[1]) for q in bd)
    cen = np.mean(np.array(poly), axis=0); nb = len(bd)
    def P(q, off): u, v = to_uv(q[0], q[1]); return fn(u, v, sg * off)[0]
    for off, flip in ((off1, False), (off0, True)):
        rings = [[cen + (q - cen) * (j / nr) for q in bd] for j in range(1, nr + 1)]
        V = [P(cen, off)] + [P(q, off) for r in rings for q in r]; F = []
        for k in range(nb): F.append((0, 1 + k, 1 + (k + 1) % nb))
        for j in range(nr - 1):
            for k in range(nb):
                a0 = 1 + j * nb + k; a1 = 1 + j * nb + (k + 1) % nb; F.append((a0, a0 + nb, a1 + nb, a1))
        if flip: F = [f[::-1] for f in F]
        em._add(V, F, [mat] * len(F), tf)
    V = [P(q, off0) for q in bd] + [P(q, off1) for q in bd]
    em._add(V, [(k, (k + 1) % nb, nb + (k + 1) % nb, nb + k) for k in range(nb)], [mat] * nb, tf)
def circ(cz, cy, r, n=12, sy=1.0): return [(ES * (cz + r * math.cos(2 * math.pi * k / n)), ES * (cy + sy * r * math.sin(2 * math.pi * k / n))) for k in range(n)]
def bar(cz, cy, L_, w, ang):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang)); hl, hw = L_ / 2, w / 2
    return [(ES * (cz + a * c - b * s), ES * (cy + a * s + b * c)) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))]
if True:
    for sg in (1, -1):
        for ang in (34, -34):
            slab2d(bar(0, -0.6, 10.5, 1.15, ang), 0.10 if ang > 0 else 0.11, 0.34 if ang > 0 else 0.35, 'WoodDk', sg)
            ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            for e in (-1, 1):
                ex, eyy = e * 5.25 * ca, -0.6 + e * 5.25 * sa
                for o in (-1, 1): slab2d(circ(ex - sa * 0.55 * o, eyy + ca * 0.55 * o, 0.8, 8), 0.12 + 0.005 * o, 0.37 + 0.005 * o, 'WoodDk', sg)
        slab2d(circ(0, 1.2, 3.1, 14, 0.95), 0.14, 0.42, 'WoodDk', sg)                         # cranium
        slab2d([(ES * a_, ES * b_) for a_, b_ in ((-1.75, -2.9), (1.75, -2.9), (1.95, -0.6), (-1.95, -0.6))], 0.15, 0.41, 'WoodDk', sg)   # jaw
        for ez in (-1.2, 1.2): slab2d(circ(ez, 1.0, 0.85, 8), 0.38, 0.50, 'Canvas', sg)           # eye sockets (cream)
        slab2d([(ES * a_, ES * b_) for a_, b_ in ((0, 0.0), (0.42, -0.85), (-0.42, -0.85))], 0.38, 0.50, 'Canvas', sg)               # nose
        for tz in (-1.05, -0.35, 0.35, 1.05): slab2d(bar(tz, -2.3, 0.12, 1.0, 90), 0.37, 0.49, 'Canvas', sg)   # teeth gaps
    miss = on_sail(EMB_SAIL, EMB_CHK)    # every emblem boundary vertex must sit on bare sail (no tear hole, not on the old v3_1 patch: hit distance 2.8 +-0.06)
    if miss == 0:
        make_prop('ShipV5_SailEmblem', em, 'original simple skull & crossbones (darkwood 80,50,30, cream eye/nose/teeth inlays) on the top band of the main lower sail, both faces')
        LOG['emblem'] = dict(sail=EMB_SAIL, uv_centre=[UC, VC], scale=ES, size_studs=[round(11.5 * ES, 1), round(9.0 * ES, 1)], boundary_points_checked=len(EMB_CHK), off_bare_sail=0)
    else:
        LOG['skipped'].append('sail emblem: %d/%d boundary points not on bare sail' % (miss, len(EMB_CHK)))

# ================================================================== 7a  nest + eggs on the fore lower yardarm (+Z end)
yn = MB('yardnest'); YN = None
upw = nrm(tiltR((0, 1, 0)))
for zr in (13.0, 15.0, 11.0, -13.0):
    for xr in np.arange(FORE_X - 1.0, FORE_X + 4.01, 0.5):
        pw = tiltR(np.array((xr, 62.0, zr))); r = RIGT.ray(pw, -upw, 14.0)
        if r is None: continue
        q = untiltR(r[0])
        if 50.0 < q[1] < 55.5 and np.dot(r[1], upw) > 0.6:
            YN = (q, xr, zr); break
    if YN: break
if YN:
    q = YN[0]; c = q + np.array((0, -0.25, 0))
    yn.frustum(c, c + np.array((0, 1.3, 0)), 1.8, 2.7, 'Rope', sec=10, tf=tiltR, up=(0, 0, 1))
    yn.torus(c + np.array((0, 1.35, 0)), (0, 1, 0), 2.55, 0.62, 'Rope', nu=10, nv=5, tf=tiltR)
    for k in range(7):
        a = 2 * math.pi * k / 7 + 0.3; d = np.array((math.cos(a), 0.25, math.sin(a)))
        yn.box(c + np.array((0, 1.1, 0)) + d * 2.4, (3.2, 0.28, 0.28), 'Post', R=frame_from(nrm(np.cross(d, (0, 1, 0))), d), tf=tiltR)
    for k, (dx, dz, ry) in enumerate(((-0.6, -0.5, 0.0), (0.7, 0.1, 15.0), (-0.1, 0.8, -12.0))):
        yn.ellipsoid(c + np.array((dx, 2.05, dz)), (0.72, 0.98, 0.72), 'Canvas' if k != 1 else 'PatchBlue', R=Rz(math.radians(ry)), nu=8, nv=5, tf=tiltR)
    make_prop('ShipV5_YardNest', yn, 'twig nest with 3 eggs (2 cream, 1 pale blue) sitting on the fore lower yard near its +Z arm')
    LOG['yard_nest'] = dict(rig=list(np.round(q, 2)), world=list(np.round(tiltR(q), 2)))
else:
    LOG['skipped'].append('yard nest: fore yard top not found')

# ================================================================== 7b/c  bottle by the rail + hammock (outside the protected walkway), overlap-tested
OTHERS = [n for n in VIS_NAMES if n != 'DeckCabin']
def bottle_at(x, side):
    he, le = deck_edges(x); z = (he + 2.0) if side < 0 else (le - 2.0)
    bo = MB('bottle'); c = np.array((x, DECK + 1.12, z)); ax = nrm(np.array((math.cos(0.5), 0, math.sin(0.5) * side * -1)))
    bo.tube([c - ax * 1.6, c + ax * 1.0, c + ax * 1.6, c + ax * 2.6], [1.15, 1.15, 0.5, 0.45], 'FishTeal', sec=8, up=(0, 1, 0))
    bo.tube([c + ax * 2.5, c + ax * 3.2], [0.48, 0.42], 'PostLt', sec=6, up=(0, 1, 0))
    bo.tube([c - ax * 0.6, c + ax * 0.4], [1.2, 1.2], 'Canvas', sec=8, up=(0, 1, 0), caps=True)
    return bo
BOTTLE = None
for x, side in ((64.0, -1), (58.0, -1), (70.0, -1), (30.0, -1), (64.0, 1), (26.0, 1)):
    bo = bottle_at(x, side)
    ov = overlaps(bo, OTHERS)
    if not ov: BOTTLE = (x, side, bo); break
if BOTTLE:
    make_prop('ShipV5_Bottle', BOTTLE[2], 'teal glass message bottle with cork and cream label band, lying on deck beside the %s bulwark at x%.0f' % ('high' if BOTTLE[1] < 0 else 'low', BOTTLE[0]))
    LOG['bottle'] = dict(x=BOTTLE[0], side=BOTTLE[1], overlaps_other_meshes=0)
else:
    LOG['skipped'].append('bottle: no overlap-free spot')
def hammock_at(x0, side):
    he, le = deck_edges(x0 + 8.0); z = (he + 4.2) if side < 0 else (le - 4.2)
    L_ = 16.0; Wd = 3.6; YE = 32.6; SAGH = 2.8; xa, xb = x0, x0 + L_
    posts = MB('posts'); bed = MB('bed')
    for xp in (xa - 2.2, xb + 2.2):
        posts.frustum((xp, DECK - 0.25, z), (xp, 36.6, z), 0.75, 0.6, 'Post', sec=8)
        posts.ellipsoid((xp, 36.7, z), (0.75, 0.55, 0.75), 'PostLt', nu=8, nv=4)
    def S(u, v):
        x = xa + L_ * u; y = YE - SAGH * math.sin(math.pi * u) + 0.9 * ((2 * v - 1) ** 2) * math.sin(math.pi * u) ** 0.5
        zz = z + (v - 0.5) * Wd * (0.82 + 0.18 * math.sin(math.pi * u)); return np.array((x, y, zz))
    def fn(u, v):
        e = 1e-3; p = S(u, v); du = S(min(1, u + e), v) - S(max(0, u - e), v); dv = S(u, min(1, v + e)) - S(u, max(0, v - e)); n = nrm(np.cross(du, dv))
        if n[1] < 0: n = -n
        return p, n
    bed.thick_surface(fn, 10, 4, 0.3, 'CanvasDk')
    for u in (0.0, 1.0):
        xs = xa + L_ * u; bed.box((xs, YE + 0.15, z), (0.6, 0.6, Wd + 0.9), 'Wood')
        xp = (xa - 2.2) if u == 0 else (xb + 2.2)
        for dz in (-Wd / 2, Wd / 2):
            bed.tube([(xs, YE + 0.2, z + dz * 0.9), (xp, 35.2, z)], 0.18, 'RopeLt', sec=6)
        bed.tube([(xs + (0.3 if u == 0 else -0.3), YE + 0.2, z), (xp, 35.2, z)], 0.18, 'RopeLt', sec=6)
    pu = 0.16; pp, pn = fn(pu, 0.5)
    bed.ellipsoid(pp + pn * 0.75, (1.55, 0.62, 1.35), 'Canvas', nu=10, nv=5)
    return posts, bed, z
HAM = None
for x0, side in ((34.0, -1), (40.0, -1), (28.0, -1), (46.0, -1), (34.0, 1), (40.0, 1)):
    posts, bed, z = hammock_at(x0, side)
    full = MB('ham'); full.extend(posts); full.extend(bed)
    ov = overlaps(full, OTHERS); ovd = overlaps(bed, ['DeckCabin'])
    if not ov and not ovd: HAM = (x0, side, full, z); break
    note('hammock candidate', x0, side, 'overlaps', ov, ovd)
if HAM:
    make_prop('ShipV5_Hammock', HAM[2], 'canvas hammock with skeleton-free cream pillow, slung between two free-standing posts on the %s side deck (x%.0f-%.0f); visual only' % ('high' if HAM[1] < 0 else 'low', HAM[0] - 2.2, HAM[0] + 18.2))
    LOG['hammock'] = dict(included=True, x_range=[HAM[0] - 2.2, HAM[0] + 18.2], z=round(HAM[3], 2), side=HAM[1], overlaps_other_meshes=0)
else:
    LOG['hammock'] = dict(included=False, reason='no overlap-free candidate'); LOG['skipped'].append('hammock: no clear spot')

# ================================================================== 6  Prop_Stovepipe: lopsided double-elbow pipe (vertices rebuilt, origin kept)
st_o = bpy.data.objects['Prop_Stovepipe']; SP0 = np.array([Binv(st_o.matrix_world @ v.co) for v in st_o.data.vertices])
ylo = SP0[:, 1].min(); bsel = SP0[SP0[:, 1] < ylo + 0.6]; bc = bsel.mean(0); br = float(np.median(np.hypot(bsel[:, 0] - bc[0], bsel[:, 2] - bc[2])))
pr = max(0.9, min(1.5, br * 0.8)); base = np.array((bc[0], ylo - 0.3, bc[2])); stp = MB('stove')
pts = [base, base + np.array((0, 4.2, 0)), base + np.array((-1.9, 7.2, 0.5)), base + np.array((-2.1, 9.6, 0.6)), base + np.array((-0.3, 12.4, 0.2)), base + np.array((0.2, 14.4, 0.0))]
stp.tube(pts, [pr * 1.05, pr, pr, pr * 0.95, pr * 0.95, pr * 0.9], 'Iron', sec=8)
stp.frustum(base + np.array((0, 0.25, 0)), base + np.array((0, 1.1, 0)), pr + 0.55, pr + 0.3, 'Brass', sec=8)
for k in (1, 3):
    d = nrm(pts[k + 1] - pts[k - 1]); stp.torus(pts[k], d, pr + 0.15, 0.25, 'Brass', nu=8, nv=4)
hat_c = pts[-1] + np.array((0, 0.9, 0)); hR = Rz(math.radians(-17)) @ Rx(math.radians(9))
stp.frustum(hat_c - hR @ np.array((0, 0.5, 0)), hat_c + hR @ np.array((0, 0.6, 0)), pr * 2.1, pr * 0.5, 'Iron', sec=8, up=(1, 0, 0))
stp.box(pts[-1] + np.array((0, 0.55, 0)), (0.35, 1.3, pr * 1.6), 'Iron')
replace_prop_mesh('Prop_Stovepipe', stp, 'v5: lopsided stovepipe: two crooked elbows (brass bands), brass roof flange, tilted coolie hat; same object/origin; base sits in the old roof footprint')
LOG['stovepipe'] = dict(old_base_centre=list(np.round(bc, 2)), old_base_radius=round(br, 2), pipe_radius=round(pr, 2), old_top=round(float(SP0[:, 1].max()), 2), new_top=round(float(hat_c[1] + 0.6), 2))

# ------------------------------------------------------------------ final asserts + save
assert col_hash() == COL0, 'collision changed!'
for n in LOCKED: assert n not in moved
LOG['palette'] = PALETTE; LOG['source'] = SRC_PATH; LOG['blender'] = bpy.app.version_string
sc['start_ship_version'] = 'start_ship_whimsy_v5'; sc['source_blend'] = SRC_PATH
json.dump(LOG, open(os.path.join(OUT_DIR, 'logs', 'build_log.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=True, copy=True)
print('BUILD_OK', OUT_BLEND, 'skipped', LOG['skipped'])
