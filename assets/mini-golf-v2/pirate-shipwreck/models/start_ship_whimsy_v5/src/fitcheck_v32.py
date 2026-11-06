# Fitcheck for start ship v3_2 (helpers byte-identical to prior_scripts/fitcheck_v31.py; check() from fitcheck_v32_check.py, baseline = dump of source_v3_1.blend).
#  1) blender -b --factory-startup source.blend --python fitcheck_v3.py -- dump <dump.json>
#  2) blender -b --factory-startup out/start_ship_v3.blend --python fitcheck_v3.py -- check <dump.json> <out_dir> <source.blend path>
# 'check' compares v3 against the source dump and writes out_dir/fitcheck.json, fitcheck.md, manifest.json.
import bpy, bmesh, sys, os, json, math, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import *
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index('--') + 1:]; MODE = A[0]
ORIG = ['Hull', 'DeckCabin', 'Rigging', 'Pier', 'RockBumper', 'Dressing', 'Dressing_Glow', 'RampFlight1', 'RampLanding', 'RampFlight2']
EMPTIES = ['Spawn', 'Tee1', 'RampStart', 'CupRef']

def sha(a): return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def mesh_arrays(me):
    n = len(me.vertices); co = np.zeros(n * 3, np.float32); me.vertices.foreach_get('co', co)
    lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
    ps = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('loop_start', ps)
    mi = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
    uv = np.zeros(len(me.loops) * 2, np.float32)
    if me.uv_layers: me.uv_layers[0].data.foreach_get('uv', uv)
    return co, lv, ps, mi, uv
def mw_list(o): return [float(v) for row in o.matrix_world for v in row]
def roblox_bbox(o):
    co = np.array([o.matrix_world @ v.co for v in o.data.vertices]); R = np.column_stack([co[:, 0], co[:, 2], -co[:, 1]])
    return R.min(0).round(3).tolist(), R.max(0).round(3).tolist()
def tris(me): return int(sum(len(p.vertices) - 2 for p in me.polygons))
def world_bm(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bm.faces.ensure_lookup_table(); return bm

def hull_bottom_profile():
    ob = bpy.data.objects['Hull']; bm = world_bm(ob); T = BVHTree.FromBMesh(bm); res = []
    for x in np.arange(-158.0, 157.0, 10.0):
        best = None
        for by in np.arange(-60.0, 60.0, 0.25):
            loc, nor, idx, d = T.ray_cast(Vector((x, by, -40.0)), Vector((0, 0, 1)), 200)
            if loc is not None and (best is None or loc.z < best[0]): best = (loc.z, by)
        res.append(dict(x=float(x), bottom_y=None if best is None else round(float(best[0]), 4), at_roblox_z=None if best is None else round(float(-best[1]), 2)))
    bm.free(); return res

def scene_trees(names=None, exclude=()):
    out = {}
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.startswith('COL') or o.name in exclude: continue
        if names is not None and o.name not in names: continue
        bm = world_bm(o); out[o.name] = (BVHTree.FromBMesh(bm), bm)
    return out

def probes(trees):
    """spawn headroom, door clearance, tee sightlines: first hits against all visual meshes"""
    def first(o, d, L):
        best = None
        for n, (T, bm) in trees.items():
            loc, nor, idx, dist = T.ray_cast(Vector(B(o)), Vector(B(nrm(d))), L)
            if loc is not None and (best is None or dist < best[1]): best = (n, dist)
        return best
    E = {n: Binv(bpy.data.objects[n].matrix_world.translation) for n in EMPTIES}
    sp = E['Spawn']; hr = first(sp + np.array((0, 0.05, 0)), (0, 1, 0), 100)
    door = []
    for x in np.arange(-123.5, -116.4, 1.0):
        for y in np.arange(24.5, 33.6, 1.0):
            h = first(np.array((x, y, 18.0)), (0, 0, 1), 12.0)   # from inside the cabin, out through the door to z=30
            door.append(dict(x=float(x), y=float(y), hit=None if h is None else [h[0], round(h[1], 3)]))
    eye = E['Tee1'] + np.array((0, 5.0, 0)); F2 = Binv(bpy.data.objects['RampFlight2'].matrix_world.translation)
    targets = {'RampStart+1': E['RampStart'] + np.array((0, 1, 0)), 'Landing_centre+1': np.array((-120.0, 13.0, 122.5)), 'Flight2_mouth+1': F2 + np.array((0, 1, 0)),
               'Flight1_mid+1': np.array((-120.0, 19.0, 88.5))}
    sl = {}
    for k, t in targets.items():
        L = float(np.linalg.norm(t - eye)); h = first(eye, t - eye, L)
        sl[k] = dict(target=list(np.round(t, 2)), dist=round(L, 3), first_hit=None if h is None else [h[0], round(h[1], 3)])
    return dict(spawn_headroom=None if hr is None else [hr[0], round(hr[1], 4)], door_rays=door, tee_eye=list(np.round(eye, 3)), tee_sightlines=sl)

def deck_walk_surfaces():
    o = bpy.data.objects['DeckCabin']; me = o.data; area = 0.0; n = 0; area30 = 0.0
    for p in me.polygons:
        c = o.matrix_world @ p.center; nn = p.normal
        if nn.z > 0.999 and abs(c.z - 24.0) < 1e-3: area += p.area; n += 1
        if nn.z > 0.999 and abs(c.z - 30.0) < 1e-3: area30 += p.area
    return dict(deck_top_Y24_faces=n, deck_top_Y24_area=round(area, 3), forecastle_top_Y30_area=round(area30, 3))

def dump():
    D = dict(objects={}, empties={}, collision={}, collections={c.name: sorted(o.name for o in c.objects) for c in bpy.data.collections})
    for o in bpy.data.objects:
        if o.type == 'EMPTY': D['empties'][o.name] = dict(loc=list(o.location), rot=list(o.rotation_euler), scale=list(o.scale), mw=mw_list(o), parent=o.parent.name if o.parent else None, coll=[c.name for c in o.users_collection])
        elif o.type == 'MESH':
            co, lv, ps, mi, uv = mesh_arrays(o.data)
            e = dict(mw=mw_list(o), co_sha=sha(co), loops_sha=sha(lv), polys_sha=sha(ps), mi_sha=sha(mi), uv_sha=sha(uv), mats=[m.name for m in o.data.materials], tris=tris(o.data),
                     verts=len(o.data.vertices), coll=[c.name for c in o.users_collection], mesh_name=o.data.name)
            if o.name.startswith('COL') or o.name.startswith('Ramp'):
                W = np.array([o.matrix_world @ v.co for v in o.data.vertices], dtype=np.float64); e['world_verts'] = W.tolist(); e['world_sha'] = sha(W)
            if o.name.startswith('COL'): D['collision'][o.name] = e
            else: D['objects'][o.name] = e
    D['hull_bottom'] = hull_bottom_profile(); D['probes'] = probes(scene_trees()); D['walk'] = deck_walk_surfaces()
    # source hull triangles (rounded) for "everything except the bowsprit is still there"
    bm = world_bm(bpy.data.objects['Hull'])
    D['hull_tris'] = sorted([tuple(sorted(tuple(round(c, 4) for c in v.co) for v in f.verts)) for f in bm.faces]); bm.free()
    # source visual floater scan (merged by position; components whose bbox touches no other component)
    D['floaters'] = floater_scan()
    D['blend'] = bpy.data.filepath
    return D

def floater_scan():
    out = []
    boxes = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.startswith('COL') or o.name.startswith('_'): continue
        bm = world_bm(o); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-3); seen = set()
        for f in bm.faces:
            if f in seen: continue
            st = [f]; comp = []; seen.add(f)
            while st:
                a = st.pop(); comp.append(a)
                for e in a.edges:
                    for g in e.link_faces:
                        if g not in seen: seen.add(g); st.append(g)
            co = np.array([v.co for g in comp for v in g.verts]); boxes.append((o.name, co.min(0), co.max(0), len(comp)))
        bm.free()
    mn = np.array([b[1] for b in boxes]); mx = np.array([b[2] for b in boxes]); eps = 0.05
    for i, (n, a, b, k) in enumerate(boxes):
        ov = np.all((mn <= b + eps) & (mx >= a - eps), axis=1); ov[i] = False
        if not ov.any() and n not in ('RockBumper', 'Pier'):
            out.append(dict(obj=n, faces=k, bbmin=list(np.round(a, 2)), bbmax=list(np.round(b, 2))))
    return dict(components=len(boxes), isolated=out)

# ------------------------------------------------------------------ corridor (Roblox coords)
CORR = {
    'cabin_interior_spawn': ((-148.0, 24.0, -17.0), (-92.0, 40.0, 22.0)),
    'door_approach': ((-126.0, 24.0, 18.0), (-114.0, 35.0, 30.0)),
    'tee_pad_stance': ((-128.0, 24.0, 28.0), (-112.0, 31.0, 46.0)),
    'outrigger': ((-131.0, 24.0, 43.0), (-109.0, 31.0, 63.0)),
    'flight1': ((-128.0, 11.0, 62.0), (-112.0, 31.0, 116.0)),
    'landing': ((-129.0, 10.0, 113.0), (-111.0, 20.0, 132.0)),
}
def aabb_dist(P, lo, hi):
    lo = np.array(lo); hi = np.array(hi); d = np.maximum(np.maximum(lo - P, 0), P - hi); return np.linalg.norm(d, axis=1)
def f2_dist(P, F2, yawed=True):
    d2 = np.array((-0.5, 0, math.sqrt(3) / 2)) if yawed else np.array((0, 0, 1.0)); n2 = np.array((d2[2], 0, -d2[0]))
    Q = P - F2; a = Q @ d2; l = Q @ n2; y = Q[:, 1]
    da = np.maximum(np.maximum(-1.0 - a, 0), a - 72.0); dl = np.maximum(np.abs(l) - 9.0, 0); dy = np.maximum(np.maximum(-13.0 - y, 0), y - 7.0)
    return np.sqrt(da ** 2 + dl ** 2 + dy ** 2)
def sample_points(o, only_new=None, centres=True):
    me = o.data; mw = o.matrix_world; P = [mw @ v.co for v in me.vertices] + ([mw @ p.center for p in me.polygons] if centres else [])
    P = np.array([Binv(p) for p in P])
    if only_new is not None: P = P[only_new(P)]
    return P

def _bs_dist(c):
    q = untilt(Binv(np.array(c))) - np.array(BS0); d = nrm(np.array(BS1) - np.array(BS0)); t = np.dot(q, d); return float(np.linalg.norm(q - t * d))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fitcheck_v32_check.py')).read())

if MODE == 'dump':
    json.dump(dump(), open(A[1], 'w')); print('DUMP_OK', A[1])
else:
    check(A[1], A[2], A[3], A[4])
