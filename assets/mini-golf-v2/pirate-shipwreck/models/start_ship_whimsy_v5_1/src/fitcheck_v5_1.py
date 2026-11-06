# Fitcheck for start ship whimsy v5_1 vs source_v5.blend.
# 1) blender -b --factory-startup source_v5.blend --python fitcheck_v5_1.py -- dump <dump.json>
# 2) blender -b --factory-startup out/start_ship_whimsy_v5_1.blend --python fitcheck_v5_1.py -- check <dump.json> <out_dir> <build_log.json>
# 'check' writes out_dir/fitcheck.json + fitcheck.md + manifest.json. Helper methods (probes, corridor segments, coplanar scan) copied from prior_scripts/fitcheck_v5*.py.
import bpy, bmesh, sys, os, json, math, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import *
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index('--') + 1:]; MODE = A[0]
EMPTIES = ['Spawn', 'Tee1', 'RampStart', 'CupRef']
LOCKED = ['DeckCabin', 'RampFlight1', 'RampLanding', 'RampFlight2']
MUST_UNCHANGED = ['ShipV5_SailEmblem', 'Prop_Flag', 'ShipV5_MastZigzag', 'Prop_Crab', 'Prop_DoorLantern', 'Prop_DoorLantern_Glow', 'ShipV5_SailPatches',
                  'Prop_SternCurl', 'Pier', 'RockBumper', 'Dressing', 'Dressing_Glow']
MOVED = {'Prop_SternWheel': 'wheel', 'Prop_TreasureChest': 'chest', 'Prop_RopeCoils': 'tee rope coil', 'Prop_CargoCluster': 'barrels'}
QA_OBJS = ['Prop_SternWheel', 'Prop_TreasureChest', 'Prop_RopeCoils', 'Prop_CargoCluster', 'Prop_Crab', 'Prop_DoorLantern']

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
def tris(me): return int(sum(len(p.vertices) - 2 for p in me.polygons))
def world_bm(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bm.faces.ensure_lookup_table(); return bm
def roblox_verts(o):
    n = len(o.data.vertices); L = np.zeros(n * 3, np.float32); o.data.vertices.foreach_get('co', L); L = L.reshape(n, 3).astype(np.float64)
    M = np.array(o.matrix_world); W = L @ M[:3, :3].T + M[:3, 3]; return np.column_stack([W[:, 0], W[:, 2], -W[:, 1]])
def world_tris(o):
    R = roblox_verts(o); T = []
    for p in o.data.polygons:
        v = list(p.vertices)
        for k in range(1, len(v) - 1): T.append((v[0], v[k], v[k + 1]))
    return R[np.array(T)] if T else np.zeros((0, 3, 3))
def scene_trees(names=None, exclude=()):
    out = {}
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.startswith('COL') or o.name in exclude: continue
        if names is not None and o.name not in names: continue
        bm = world_bm(o); out[o.name] = (BVHTree.FromBMesh(bm), bm)
    return out

# ------------------------------------------------------------------ probes (copied from prior fitcheck_v5.py)
def probes(trees):
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
            h = first(np.array((x, y, 18.0)), (0, 0, 1), 12.0)
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
    o = bpy.data.objects['DeckCabin']; area = 0.0; n = 0; area30 = 0.0
    for p in o.data.polygons:
        c = o.matrix_world @ p.center; nn = p.normal
        if nn.z > 0.999 and abs(c.z - 24.0) < 1e-3: area += p.area; n += 1
        if nn.z > 0.999 and abs(c.z - 30.0) < 1e-3: area30 += p.area
    return dict(deck_top_Y24_faces=n, deck_top_Y24_area=round(area, 3), forecastle_top_Y30_area=round(area30, 3))
def coplanar_scan(names, trees=None, find=0.03, dotmin=0.995, gapmax=0.02):
    trees = trees or scene_trees(); out = []; checked = 0
    for n in names:
        o = bpy.data.objects.get(n)
        if o is None or o.type != 'MESH': continue
        bm = world_bm(o)
        for f in bm.faces:
            c = f.calc_center_median(); n0 = f.normal; checked += 1
            for nme, (T, bm2) in trees.items():
                if nme == o.name: continue
                loc, nor, idx, dist = T.find_nearest(c, find)
                if loc is not None and abs(nor.dot(n0)) > dotmin and abs((c - loc).dot(nor)) < gapmax:
                    out.append(dict(obj=o.name, other=nme, at=[round(float(v), 2) for v in Binv(c)], dist=round(dist, 4)))
        bm.free()
    return dict(objects=names, faces_checked=checked, pairs=out)

# ------------------------------------------------------------------ route corridor (Roblox coords) — segments as prior fitcheck_v5_check.corridor_segments
def corridor_segments(F2, yawed):
    d2 = np.array((-0.5, 0, math.sqrt(3) / 2)) if yawed else np.array((0, 0, 1.0))
    return [((-120.0, 24.0, -17.0), (-120.0, 24.0, 62.5), 4.0, 'cabin_door_tee_gangplank'),
            ((-120.0, 24.0, 62.5), (-120.0, 12.0, 113.5), 6.0, 'flight1'),
            ((-120.0, 12.0, 113.5), (-120.0, 12.0, 131.0), 6.27, 'landing (Studio v30 exit 12.54 wide)'),
            (tuple(F2), tuple(F2 + d2 * 72.0 + np.array((0, -12.0, 0))), 6.0, 'flight2_' + ('yawed' if yawed else 'unyawed'))]
def seg_metrics(P, seg, r=2.0, hplayer=5.5):
    """P: (N,3) Roblox points. Returns (corridor_clear, player_clear, inside_corridor_mask).
    corridor (prior method): horizontal half-width hw about the xz centreline, walk band yw-1 .. yw+10; clearance = distance to that volume.
    player (swept): player capsule r=2.0, 5.5 tall, centre path anywhere within hw-r of the centreline (stays inside the walkway), feet on the walk line;
    clearance = distance to the swept capsule-axis set minus r (0 = touching, <0 = intersecting)."""
    a = np.array(seg[0]); b = np.array(seg[1]); hw = seg[2]; ab = b - a; abxz = np.array((ab[0], ab[2])); L2 = float(abxz @ abxz)
    Q = np.column_stack([P[:, 0] - a[0], P[:, 2] - a[2]]); t = np.clip(Q @ abxz / L2, 0, 1)
    dxz = np.linalg.norm(Q - np.outer(t, abxz), axis=1); yw = a[1] + t * ab[1]
    dy = np.maximum(np.maximum((yw - 1.0) - P[:, 1], 0), P[:, 1] - (yw + 10.0))
    corr = np.sqrt(np.maximum(dxz - hw, 0) ** 2 + dy ** 2); inside = (dxz <= hw) & (dy <= 0)
    lat = np.maximum(dxz - (hw - r), 0); dyp = np.maximum(np.maximum((yw + r) - P[:, 1], 0), P[:, 1] - (yw + hplayer - r))
    play = np.sqrt(lat ** 2 + dyp ** 2) - r
    return corr, play, inside
SPACING = 0.2
def tri_samples(Tr, spacing=SPACING):
    """dense barycentric samples of each triangle (edge subdivisions so that sample spacing <= spacing); exact vertices included."""
    out = []
    for tri in Tr:
        e = max(np.linalg.norm(tri[1] - tri[0]), np.linalg.norm(tri[2] - tri[1]), np.linalg.norm(tri[0] - tri[2])); n = max(1, int(math.ceil(e / spacing)))
        I, J = np.meshgrid(np.arange(n + 1), np.arange(n + 1)); m = (I + J) <= n; u = I[m] / n; v = J[m] / n
        out.append(tri[0] + np.outer(u, tri[1] - tri[0]) + np.outer(v, tri[2] - tri[0]))
    return np.vstack(out) if out else np.zeros((0, 3))
def route_qa(names, prefilter=None):
    F2 = Binv(bpy.data.objects['RampFlight2'].matrix_world.translation)
    SEG = corridor_segments(F2, True) + corridor_segments(F2, False)[-1:]; res = {}
    for n in names:
        o = bpy.data.objects[n]; Tr = world_tris(o); rec = {}
        if prefilter is not None and len(Tr) > 2500:   # only the big meshes (Hull, Rigging...) are prefiltered; every prop is fully sampled
            keep = np.zeros(len(Tr), bool)
            for seg in SEG:
                c, p, _ = seg_metrics(Tr.reshape(-1, 3), seg); dmin = np.minimum(c, p + 2.0).reshape(-1, 3).min(1)
                e = np.max(np.linalg.norm(Tr - np.roll(Tr, 1, axis=1), axis=2), axis=1)
                keep |= dmin - e < prefilter
            Tr_s = Tr[keep]
        else:
            Tr_s = Tr
        P = tri_samples(Tr_s) if len(Tr_s) else np.zeros((0, 3))
        for seg in SEG:
            if not len(P): rec[seg[3]] = dict(corridor_clear=None, player_clear=None, note='no triangle within prefilter %s studs' % prefilter); continue
            c, p, ins = seg_metrics(P, seg); k = int(np.argmin(p))
            rec[seg[3]] = dict(corridor_clear=round(float(c.min()), 3), player_clear=round(float(p.min()), 3), inside_corridor_samples=int(ins.sum()),
                               closest_point=list(np.round(P[k], 2)))
        res[n] = dict(tris=int(len(Tr)), tris_sampled=int(len(Tr_s)), samples=int(len(P)), segments=rec)
    return dict(method='triangle-swept: every triangle densely sampled (barycentric grid, spacing <= %.2f studs, so true clearance >= reported - %.2f) and measured against each walkway segment: '
                       '(a) prior corridor volume (half-width hw about the centreline, walk band -1..+10) and (b) swept player capsule r=2.0, 5.5 tall, centre path within hw-2 of the centreline.' % (SPACING, SPACING * 0.58),
                segments=[dict(name=s[3], a=list(np.round(s[0], 2)), b=list(np.round(s[1], 2)), half_width=s[2]) for s in SEG], objects=res)
def corridor_overlap(names):
    """exact BVH triangle overlap between each object and the prior corridor volumes (prisms)"""
    F2 = Binv(bpy.data.objects['RampFlight2'].matrix_world.translation); SEG = corridor_segments(F2, True) + corridor_segments(F2, False)[-1:]; vols = {}
    for a, b, hw, nm in SEG:
        a = np.array(a); b = np.array(b); d = b - a; dxz = nrm(np.array((d[0], 0, d[2]))); nl = np.array((dxz[2], 0, -dxz[0])); V = []
        for p in (a, b):
            for s in (-hw, hw):
                for yy in (-1.0, 10.0): V.append(B(p + nl * s + np.array((0, yy, 0))))
        F = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        vols[nm] = BVHTree.FromPolygons(V, F)
    out = {}
    for n in names:
        bm = world_bm(bpy.data.objects[n]); T = BVHTree.FromBMesh(bm); bm.free()
        k = {nm: len(T.overlap(Z)) for nm, Z in vols.items()}; out[n] = {kk: v for kk, v in k.items() if v}
    return out

# ------------------------------------------------------------------ tee view visibility of props
CAM_DIR = nrm(np.array((0.93, 0.29, -0.25)))
def tee_visibility(names):
    eye = Binv(bpy.data.objects['Tee1'].matrix_world.translation) + np.array((0, 5.0, 0)); trees = scene_trees(); out = {}
    fw = CAM_DIR; rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw); th = math.tan(math.radians(45)); tv = th * 1000 / 1600
    for n in names:
        R = roblox_verts(bpy.data.objects[n]); k_in = 0; k_vis = 0; offs = []
        step = max(1, len(R) // 400)
        for p in R[::step]:
            d = p - eye; z = d @ fw
            if z <= 0: continue
            if abs(d @ rt) / z > th or abs(d @ up) / z > tv: continue
            k_in += 1; L = float(np.linalg.norm(d)); blocked = False
            for nm, (T, bm) in trees.items():
                if nm == n: continue
                loc, nor, idx, dist = T.ray_cast(Vector(B(eye)), Vector(B(d / L)), L - 0.15)
                if loc is not None: blocked = True; break
            if not blocked: k_vis += 1
        az = np.degrees(np.arctan2(R[:, 2] - eye[2], R[:, 0] - eye[0])); cax = math.degrees(math.atan2(CAM_DIR[2], CAM_DIR[0]))
        off = np.abs(((az - cax) + 180) % 360 - 180)
        out[n] = dict(sampled_verts=int(len(R[::step])), in_tee_frame=k_in, visible_from_tee_eye=k_vis, visible_fraction=round(k_vis / max(1, len(R[::step])), 3),
                      azimuth_offset_from_tee_axis_deg=[round(float(off.min()), 1), round(float(off.max()), 1)])
    return out

# ------------------------------------------------------------------ silhouette measures
def sheer_tops():
    names = ['Prop_CapRails', 'ShipV5_SheerRise', 'Prop_BowRaise', 'Hull', 'Prop_SternCastle']
    P = np.vstack([roblox_verts(bpy.data.objects[n]) for n in names]); zc = P[:, 1] * math.tan(PHI); out = {}
    for x in (-158.0, -150.0, -140.0, -130.0, 90.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 154.0):
        m = np.abs(P[:, 0] - x) < 1.0
        for side, sm in (('high', P[:, 2] < zc), ('low', P[:, 2] >= zc)):
            q = P[m & sm]; out['x%d_%s' % (x, side)] = round(float(q[:, 1].max()), 2) if len(q) else None
    return out
def widths():
    T = scene_trees(['Hull'])['Hull'][0]; out = {}
    for Y in (-2.0, -0.6, 1.5, 3.0, 6.0, 9.0, 12.0, 18.0, 23.0):
        row = {}
        for x in (-140.0, -100.0, -60.0, -20.0, 20.0, 60.0, 100.0):
            a = T.ray_cast(Vector(B((x, Y, -300.0))), Vector(B((0, 0, 1))), 700); b = T.ray_cast(Vector(B((x, Y, 300.0))), Vector(B((0, 0, -1))), 700)
            row['x%d' % x] = None if a[0] is None or b[0] is None else round(float(Binv(b[0])[2] - Binv(a[0])[2]), 3)
        out['Y%.1f' % Y] = row
    return out
def hullext():
    T = scene_trees(['Hull'])['Hull'][0]; P = []
    for x in np.arange(-158.0, 150.0, 4.0):
        for Y in np.arange(-0.5, 18.01, 1.5):
            for z0, dz in ((-300.0, 1), (300.0, -1)):
                r = T.ray_cast(Vector(B((x, Y, z0))), Vector(B((0, 0, dz))), 700)
                if r[0] is not None: P.append(Binv(r[0]))
    P = np.array(P); best = np.full(len(P), 1e9); who = np.array([''] * len(P), dtype=object)
    for o in bpy.data.collections['Collision'].objects:
        if not o.name.startswith('COL_HullExt'): continue
        W = np.array([Binv(o.matrix_world @ v.co) for v in o.data.vertices]); c = W.mean(0)
        d = sorted([W[i] - W[0] for i in range(1, len(W))], key=lambda v: np.linalg.norm(v))[:3]
        ax = np.array([nrm(v) for v in d]); hs = np.array([np.linalg.norm(v) / 2 for v in d])
        dd = np.linalg.norm(np.maximum(np.abs((P - c) @ ax.T) - hs, 0), axis=1); m = dd < best; who[m] = o.name; best = np.minimum(best, dd)
    return P.tolist(), best.tolist(), who.tolist()
def floating_check(names):
    """moved props: every vertex within 0.6 of the lowest Y must have deck (DeckCabin) within 0.25 below it"""
    T = scene_trees(['DeckCabin'])['DeckCabin'][0]; out = {}
    for n in names:
        R = roblox_verts(bpy.data.objects[n]); lo = R[R[:, 1] < R[:, 1].min() + 0.6]; gaps = []
        for p in lo[:: max(1, len(lo) // 60)]:
            r = T.ray_cast(Vector(B(p + np.array((0, 0.5, 0)))), Vector((0, 0, -1)), 5.0); gaps.append(None if r[0] is None else round(r[3] - 0.5, 3))
        g = [x for x in gaps if x is not None]
        out[n] = dict(base_samples=len(gaps), no_deck_below=sum(1 for x in gaps if x is None), max_gap=max(g) if g else None, min_y=round(float(R[:, 1].min()), 3))
    return out

def dump_state():
    D = dict(blend=bpy.data.filepath, blender=bpy.app.version_string, objects={}, empties={}, collision={}, collections={c.name: sorted(o.name for o in c.objects) for c in bpy.data.collections})
    for o in bpy.data.objects:
        if o.type == 'EMPTY': D['empties'][o.name] = dict(mw=mw_list(o), coll=[c.name for c in o.users_collection]); continue
        co, lv, ps, mi, uv = mesh_arrays(o.data)
        e = dict(mw=mw_list(o), co_sha=sha(co), loops_sha=sha(lv), polys_sha=sha(ps), mi_sha=sha(mi), uv_sha=sha(uv), mats=[m.name for m in o.data.materials], tris=tris(o.data),
                 verts=len(o.data.vertices), coll=[c.name for c in o.users_collection], mesh_name=o.data.name)
        if o.name.startswith('COL') or o.name in LOCKED: e['world_sha'] = sha(np.array([o.matrix_world @ v.co for v in o.data.vertices], dtype=np.float64))
        if o.name == 'Rigging': e['roblox_verts'] = roblox_verts(o).tolist()
        (D['collision'] if o.name.startswith('COL') else D['objects'])[o.name] = e
    vis = [o.name for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith('COL')]
    trees = scene_trees()
    D['probes'] = probes(trees); D['walk'] = deck_walk_surfaces()
    D['route_qa'] = route_qa([n for n in vis if n not in LOCKED], prefilter=12.0)
    D['corridor_overlap'] = corridor_overlap([n for n in vis if n not in LOCKED])
    D['tee_visibility'] = tee_visibility(QA_OBJS + ['ShipV5_BowEyes'])
    D['sheer'] = sheer_tops(); D['widths'] = widths(); P, best, who = hullext(); D['hullext'] = dict(P=P, best=best, who=who)
    D['curl'] = dict(bbox=[list(np.round(roblox_verts(bpy.data.objects['ShipV5_SternCurl']).min(0), 2)), list(np.round(roblox_verts(bpy.data.objects['ShipV5_SternCurl']).max(0), 2))])
    D['figurehead_bbox'] = [list(np.round(roblox_verts(bpy.data.objects['Prop_Figurehead']).min(0), 2)), list(np.round(roblox_verts(bpy.data.objects['Prop_Figurehead']).max(0), 2))]
    D['floating'] = floating_check(list(MOVED))
    return D, trees

if MODE == 'dump':
    D, trees = dump_state()
    D['coplanar'] = coplanar_scan(['Hull', 'Prop_Barnacles', 'Prop_PatchPlanks', 'Prop_Seaweed', 'Rigging', 'ShipV5_SheerRise', 'ShipV5_SternCurl', 'ShipV5_BowEyes',
                                   'Prop_Figurehead', 'ShipV5_Patches'] + list(MOVED), trees)
    json.dump(D, open(A[1], 'w')); print('DUMP_OK', A[1]); sys.exit(0)

# ======================================================================================== check
S = json.load(open(A[1])); OUT = A[2]; BL = json.load(open(A[3])); FAIL = []; WARN = []; FLAG = []
D, trees = dump_state()
R = dict(source=S['blend'], v5_1=D['blend'], blender=D['blender'])
# anchors
R['anchors'] = {n: dict(exact=S['empties'][n]['mw'] == D['empties'][n]['mw'], roblox=list(np.round(Binv(bpy.data.objects[n].matrix_world.translation), 3))) for n in EMPTIES}
if not all(v['exact'] for v in R['anchors'].values()): FAIL.append('anchor moved')
# locked
KEYS = ['co_sha', 'loops_sha', 'polys_sha', 'mi_sha', 'uv_sha', 'mats', 'mw', 'world_sha', 'mesh_name', 'coll']
R['locked'] = {n: {k: S['objects'][n][k] == D['objects'][n][k] for k in KEYS} for n in LOCKED}
for n, v in R['locked'].items():
    if not all(v.values()): FAIL.append('locked mesh changed: ' + n)
# collision
cb = [n for n in S['collision'] if n not in D['collision'] or any(S['collision'][n][k] != D['collision'][n][k] for k in KEYS if k in S['collision'][n])]
R['collision'] = dict(count_source=len(S['collision']), count_v5_1=len(D['collision']), byte_identical=len(S['collision']) - len(cb), changed=cb,
                      verified_vs_studio_v30=False, note='Blender colliders are the stale v3_2 set (unchanged). NOT verified against Studio v30; no collision FBX handed off.')
if cb or len(D['collision']) != len(S['collision']): FAIL.append('collision changed')
# names / origins / datablocks / collections
miss = sorted(set(S['objects']) - set(D['objects'])); extra = sorted(set(D['objects']) - set(S['objects']))
org = [n for n in S['objects'] if n in D['objects'] and S['objects'][n]['mw'] != D['objects'][n]['mw']]
dbn = [n for n in S['objects'] if n in D['objects'] and S['objects'][n]['mesh_name'] != D['objects'][n]['mesh_name']]
col_ = [n for n in S['objects'] if n in D['objects'] and S['objects'][n]['coll'] != D['objects'][n]['coll']]
R['names_origins'] = dict(missing=miss, new_objects=extra, origin_changed=org, mesh_datablock_renamed=dbn, collection_changed=col_, all_preserved=not (miss or extra or org or dbn or col_),
                          empties_preserved=sorted(S['empties']) == sorted(D['empties']))
if miss or extra or org or dbn or col_: FAIL.append('names/origins not preserved')
changed = {}
for n in S['objects']:
    s, d = S['objects'][n], D['objects'][n]
    diff = [k for k in ('co_sha', 'loops_sha', 'polys_sha', 'mi_sha', 'uv_sha', 'mats') if s[k] != d[k]]
    if diff: changed[n] = diff
R['changed_meshes'] = {n: dict(fields=v, kind=(BL['changes'].get(n, {}).get('kind') or ('belly warp (vertex positions only)' if n in BL['hull_belly']['moved_objects_max_disp'] else
                        ('prop mesh moved out of the tee sightline (vertex positions only)' if n in MOVED else '?')))) for n, v in changed.items()}
topo_bad = [n for n, v in changed.items() if n not in ('ShipV5_SheerRise', 'Prop_Figurehead', 'ShipV5_BowEyes', 'ShipV5_Patches') and set(v) - {'co_sha'}]
if topo_bad: FAIL.append('topology/UV/material changed on vertex-only edits: %s' % topo_bad)
mu = [n for n in MUST_UNCHANGED if n in changed]; R['must_unchanged'] = dict(names=MUST_UNCHANGED, changed=mu)
if mu: FAIL.append('must-unchanged mesh changed: %s' % mu)
rv0 = np.array(S['objects']['Rigging']['roblox_verts']); rv1 = roblox_verts(bpy.data.objects['Rigging']); dd = np.linalg.norm(rv1 - rv0, axis=1)
R['rigging'] = dict(verts=int(len(dd)), moved=int((dd > 1e-6).sum()), max_disp=round(float(dd.max()), 4), max_disp_above_Y14=round(float(dd[rv0[:, 1] > 14.0].max()), 6),
                    note='only low anchor-line verts below Y14 moved by the belly warp; sails/masts/yards/crow\'s nest untouched')
if R['rigging']['max_disp_above_Y14'] > 0: FAIL.append('Rigging moved above Y14')
# probes
pv, ps_ = D['probes'], S['probes']
R['probes'] = dict(spawn_headroom_identical=pv['spawn_headroom'] == ps_['spawn_headroom'], spawn_headroom=pv['spawn_headroom'],
                   door_rays_identical=pv['door_rays'] == ps_['door_rays'], door_rays=len(pv['door_rays']),
                   tee_sightlines_identical=all(pv['tee_sightlines'][k]['first_hit'] == ps_['tee_sightlines'][k]['first_hit'] for k in pv['tee_sightlines']),
                   tee_sightlines=pv['tee_sightlines'], walk_surfaces_identical=D['walk'] == S['walk'], walk=D['walk'])
for k in ('spawn_headroom_identical', 'door_rays_identical', 'tee_sightlines_identical', 'walk_surfaces_identical'):
    if not R['probes'][k]: FAIL.append('probe changed: ' + k)
# route QA
rq0 = S['route_qa']; rq1 = D['route_qa']; R['route_qa'] = dict(method=rq1['method'], segments=rq1['segments'], player_radius=2.0, objects={})
intr = []
for n in rq1['objects']:
    e1 = rq1['objects'][n]; e0 = rq0['objects'].get(n)
    rec = dict(tris=e1['tris'], tris_sampled=e1['tris_sampled'], samples=e1['samples'], v5_1=e1['segments'], source_v5=e0['segments'] if e0 else None, changed=n in changed)
    R['route_qa']['objects'][n] = rec
    if n in changed:
        for sg, v in e1['segments'].items():
            v0 = e0['segments'].get(sg) if e0 else None
            if v['player_clear'] is None: continue
            new_in = v.get('inside_corridor_samples', 0) - ((v0 or {}).get('inside_corridor_samples') or 0)
            worse = v0 is not None and v0['player_clear'] is not None and v['player_clear'] < v0['player_clear'] - 1e-3
            if (v['player_clear'] < 0 and (v0 is None or v0['player_clear'] is None or v['player_clear'] < v0['player_clear'] - 1e-3)) or new_in > 0:
                intr.append((n, sg, v['player_clear'], new_in))
R['route_qa']['new_intrusions_by_changed_meshes'] = intr
R['corridor_overlap'] = dict(source=S['corridor_overlap'], v5_1=D['corridor_overlap'],
                             new=[(n, k, v) for n, d in D['corridor_overlap'].items() for k, v in d.items() if v > S['corridor_overlap'].get(n, {}).get(k, 0)])
if intr or R['corridor_overlap']['new']: FAIL.append('route corridor intrusion by changed mesh: %s / %s' % (intr, R['corridor_overlap']['new']))
R['moved_props'] = {}
for n, lbl in MOVED.items():
    v1 = rq1['objects'][n]['segments']; v0 = rq0['objects'][n]['segments']; sg = 'cabin_door_tee_gangplank'
    R['moved_props'][lbl] = dict(object=n, build=BL['tee_moves']['moves'].get(lbl if lbl != 'tee rope coil' else 'tee_rope_coil'),
        player_clear_before=v0[sg]['player_clear'], player_clear_after=v1[sg]['player_clear'], corridor_clear_before=v0[sg]['corridor_clear'], corridor_clear_after=v1[sg]['corridor_clear'],
        min_player_clear_all_segments_after=min(v['player_clear'] for v in v1.values() if v['player_clear'] is not None),
        tee_visibility_before=S['tee_visibility'][n], tee_visibility_after=D['tee_visibility'][n], floating=D['floating'][n])
    f0 = S['floating'][n]; f1 = D['floating'][n]; R['moved_props'][lbl]['floating_source'] = f0
    if f1['no_deck_below'] > f0['no_deck_below'] or (f1['max_gap'] or 0) > (f0['max_gap'] or 0) + 0.01 or abs(f1['min_y'] - f0['min_y']) > 1e-3:
        FAIL.append('moved prop sits differently on the deck than in v5: ' + n)   # (curved barrel/coil undersides give the same small gaps as in v5)
R['tee_visibility'] = dict(source=S['tee_visibility'], v5_1=D['tee_visibility'], method='vertices (<=400 per mesh) inside the ship_tee camera frame (90 deg h-fov, 1600x1000) and with an unobstructed ray from the tee eye (Tee1 + 5 up)')
# coplanar
names_c = S['coplanar']['objects']; cn = coplanar_scan(names_c, trees)
key = lambda p: (p['obj'], p['other'], tuple(p['at']))
new_pairs = [p for p in cn['pairs'] if key(p) not in set(key(q) for q in S['coplanar']['pairs'])]
R['coplanar'] = dict(method='face centre within 0.03 of another visual mesh, |dot|>0.995, plane gap <0.02 (prior method)', objects=names_c, faces_checked=cn['faces_checked'],
                     source_pairs=len(S['coplanar']['pairs']), v5_1_pairs=len(cn['pairs']), new_pairs=new_pairs[:40], new_pair_count=len(new_pairs))
if new_pairs: FAIL.append('%d new coplanar pairs' % len(new_pairs))
# tris
tr = {n: dict(source=S['objects'][n]['tris'], v5_1=D['objects'][n]['tris']) for n in S['objects']}
R['tris'] = dict(per_mesh=tr, total_source=sum(v['source'] for v in tr.values()), total_v5_1=sum(v['v5_1'] for v in tr.values()), over_20k=[n for n, v in tr.items() if v['v5_1'] >= 20000])
if R['tris']['over_20k']: FAIL.append('mesh over 20k tris')
if R['tris']['total_v5_1'] > 40000: WARN.append('total visual tris %d above ~40k near-field target (source %d)' % (R['tris']['total_v5_1'], R['tris']['total_source']))
# belly / sheer / curl / figurehead / eyes / patches
R['belly'] = dict(profile=BL['hull_belly']['profile'], x_taper=BL['hull_belly']['x_taper'], widths_source=S['widths'], widths_v5_1=D['widths'],
                  deck_Y23_max_abs_change=max(abs((D['widths']['Y23.0'][k] or 0) - (S['widths']['Y23.0'][k] or 0)) for k in D['widths']['Y23.0']))
if R['belly']['deck_Y23_max_abs_change'] > 0.01: FAIL.append('deck-level width changed')
R['sheer'] = dict(silhouette_top_y_source=S['sheer'], silhouette_top_y_v5_1=D['sheer'], delta={k: (None if S['sheer'][k] is None or D['sheer'][k] is None else round(D['sheer'][k] - S['sheer'][k], 2)) for k in D['sheer']},
                  build=BL['sheer'])
R['stern_curl'] = dict(bbox_source=S['curl']['bbox'], bbox_v5_1=D['curl']['bbox'], build=BL['changes']['ShipV5_SternCurl'])
R['figurehead'] = dict(bbox_source=S['figurehead_bbox'], bbox_v5_1=D['figurehead_bbox'], build=BL['octopus'])
R['bow_eyes'] = dict(build=BL['bow_eyes']['v5_1'], v5=BL['bow_eyes']['v5'], tee_visibility_source=S['tee_visibility']['ShipV5_BowEyes'], tee_visibility_v5_1=D['tee_visibility']['ShipV5_BowEyes'])
R['patches'] = BL['patches']
# hull-side flag
P0 = np.array(S['hullext']['P']); b0 = np.array(S['hullext']['best']); P1 = np.array(D['hullext']['P']); b1 = np.array(D['hullext']['best']); w1 = D['hullext']['who']
n_ = min(len(b0), len(b1)); inc = b1[:n_] - b0[:n_] if len(b0) == len(b1) else None
R['hull_side_flag'] = dict(method='outer Hull sampled by horizontal rays (x-158..146 step 4, Y-0.5..18 step 1.5, both sides); distance outside the nearest STALE v3_2 COL_HullExt oriented box',
    source_v5=dict(max=round(float(b0.max()), 3), p95=round(float(np.percentile(b0, 95)), 3), n_over_0_5=int((b0 > 0.5).sum()), n_over_1=int((b0 > 1).sum())),
    v5_1=dict(max=round(float(b1.max()), 3), p95=round(float(np.percentile(b1, 95)), 3), n_over_0_5=int((b1 > 0.5).sum()), n_over_1=int((b1 > 1).sum()), n_over_2=int((b1 > 2).sum())),
    increase_vs_v5=None if inc is None else dict(max=round(float(inc.max()), 3), n_over_0_5=int((inc > 0.5).sum()), n_over_1=int((inc > 1).sum()),
        boxes_over_1=sorted(set(w1[i] for i in np.where(inc > 1.0)[0]))),
    note='Studio v30 hull-side/under bands (930 COL_HullSide* + 80 COL_HullUnder*) were fitted to the v3_2 hull. The v5_1 belly is rounder (up to ~+15% width at Y1.5-3). Builder must REGENERATE the bands against the new Hull; do not paste v30 band transforms.')
FLAG.append('hull-side colliders: v5_1 visual belly sits up to %.2f studs outside the stale v3_2 COL_HullExt boxes (p95 %.2f, %d samples >1 stud). Studio v30 hull-side/under bands must be REGENERATED against this Hull.' %
            (R['hull_side_flag']['v5_1']['max'], R['hull_side_flag']['v5_1']['p95'], R['hull_side_flag']['v5_1']['n_over_1']))
R['FAIL'] = FAIL; R['WARN'] = WARN; R['FLAG'] = FLAG; R['overall'] = 'PASS' if not FAIL else 'FAIL'
json.dump(R, open(os.path.join(OUT, 'fitcheck.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))

# ------------------------------------------------------------------ manifest
man = dict(asset='start_ship_whimsy_v5_1', blend='out/start_ship_whimsy_v5_1.blend', source='source_v5.blend (sha 8e88f0e97323ffdb..., commit 2e4023b)', blender=D['blender'],
           axes='Blender Z-up, 1 unit = 1 stud; FBX axis_forward -Z, axis_up Y, global_scale 1, FBX_SCALE_UNITS, embedded palette texture',
           placement='CFrame(-690, 0.6, 160) * Angles(0, rad(102), 0) * CFrame(bboxCentre) * Angles(0, pi, 0)  (unchanged)',
           fbx=dict(visual='out/fbx/start_ship_b2_visual.fbx', ramps=['out/fbx/RampFlight1_own_origin.fbx', 'out/fbx/RampLanding_own_origin.fbx', 'out/fbx/RampFlight2_own_origin.fbx'],
                    collision='NOT EXPORTED - see out/fbx/UNSYNCED_keep_studio_v30_colliders.txt'),
           anchors={n: list(np.round(Binv(bpy.data.objects[n].matrix_world.translation), 3)) for n in EMPTIES},
           palette=BL['palette'], texture='out/textures/start_ship_palette.png (256x256, packed in blend, embedded in FBX)', meshes={},
           tris_total_visual=R['tris']['total_v5_1'], collision=R['collision'], changed_vs_v5=sorted(changed))
for o in bpy.data.objects:
    if o.type != 'MESH' or o.name.startswith('COL'): continue
    Rv = roblox_verts(o)
    man['meshes'][o.name] = dict(collection=[c.name for c in o.users_collection][0], tris=tris(o.data), materials=[m.name for m in o.data.materials],
                                 pivot_roblox=list(np.round(Binv(o.matrix_world.translation), 3)), bbox_min=list(np.round(Rv.min(0), 2)), bbox_max=list(np.round(Rv.max(0), 2)),
                                 changed_in_v5_1=o.name in changed, cancollide='visual only (CanCollide off)' if o.name not in LOCKED else 'visual (Studio colliders authoritative)')
json.dump(man, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)

# ------------------------------------------------------------------ markdown
L = []; w = L.append
w('# Fitcheck: start ship whimsy v5_1 (out/start_ship_whimsy_v5_1.blend) vs source_v5.blend\n')
w('**Overall hard checks: %s**\n' % R['overall'])
w('## FAILS'); [w('- ' + f) for f in FAIL] if FAIL else w('- none'); w('')
w('## Warnings'); [w('- ' + f) for f in WARN] if WARN else w('- none'); w('')
w('## FLAGS for the builder'); [w('- **' + f + '**') for f in FLAG]; w('')
w('## Collision: NOT verified vs Studio v30')
w('- %d/%d Blender colliders byte-identical to source_v5 (mesh verts, loops, polys, UV, material slots, matrix_world, world verts). Changed: %s' % (R['collision']['byte_identical'], R['collision']['count_source'], R['collision']['changed'] or 'none'))
w('- NOT VERIFIED against Studio v30. These are the stale v3_2 boxes. No collision FBX exported; see `out/fbx/UNSYNCED_keep_studio_v30_colliders.txt`.\n')
w('## Locks')
for n, v in R['locked'].items(): w('- %s: %s' % (n, 'EXACT (verts, loops, polys, materials, UV, matrix, world verts, datablock, collection)' if all(v.values()) else v))
w('- anchors exact: ' + ', '.join('%s=%s %s' % (n, v['exact'], v['roblox']) for n, v in R['anchors'].items()))
p_ = R['probes']; w('- spawn headroom identical %s; door rays identical %s (%d rays); tee sightlines identical %s; deck walk surfaces identical %s\n' % (p_['spawn_headroom_identical'], p_['door_rays_identical'], p_['door_rays'], p_['tee_sightlines_identical'], p_['walk_surfaces_identical']))
w('## Names / origins')
no = R['names_origins']; w('- every source object present, same name, same origin matrix_world, same mesh datablock, same collection: **%s** (missing %s, new %s, origin changed %s)' % (no['all_preserved'], no['missing'], no['new_objects'], no['origin_changed']))
w('- must-unchanged (sails emblem, flag, zigzag mast, crab, lantern + glow, sail patches, Prop_SternCurl corner scrolls, pier, rock, dressing): changed = %s' % (mu or 'none'))
w('- Rigging: %d of %d verts moved (belly warp of low anchor lines only), max %.3f; max displacement above Y14 = %s (sails/masts untouched)\n' % (R['rigging']['moved'], R['rigging']['verts'], R['rigging']['max_disp'], R['rigging']['max_disp_above_Y14']))
w('## Changed meshes (all keep name + origin)'); w('| mesh | what changed | tris v5 -> v5_1 |'); w('|---|---|---|')
for n, v in R['changed_meshes'].items(): w('| %s | %s | %d -> %d |' % (n, v['kind'], tr[n]['source'], tr[n]['v5_1']))
w('')
w('## Route QA (triangle-swept, player r=2.0)'); w('- ' + R['route_qa']['method'])
w('- segments: ' + '; '.join('%s hw %.2f' % (s['name'], s['half_width']) for s in R['route_qa']['segments']))
w('- new intrusions by changed meshes: %s; new exact BVH corridor-volume overlaps: %s\n' % (R['route_qa']['new_intrusions_by_changed_meshes'] or 'none', R['corridor_overlap']['new'] or 'none'))
w('### Moved tee props: exact measured clearances vs the cabin->door->tee->gangplank walkway (x=-120, z-17..62.5)')
w('| prop | object | player clearance before -> after (studs) | corridor(hw4) clearance before -> after | min player clearance, all segments (after) | tee-frame visible verts before -> after | offset from tee axis after (deg) |')
w('|---|---|---|---|---|---|---|')
for lbl, m in R['moved_props'].items():
    w('| %s | %s | %.3f -> %.3f | %.3f -> %.3f | %.3f | %d/%d -> %d/%d | %s |' % (lbl, m['object'], m['player_clear_before'], m['player_clear_after'], m['corridor_clear_before'], m['corridor_clear_after'], m['min_player_clear_all_segments_after'],
      m['tee_visibility_before']['visible_from_tee_eye'], m['tee_visibility_before']['sampled_verts'], m['tee_visibility_after']['visible_from_tee_eye'], m['tee_visibility_after']['sampled_verts'], m['tee_visibility_after']['azimuth_offset_from_tee_axis_deg']))
w('\n- Prop_RopeCoils and Prop_CargoCluster are multi-part meshes: only the tee coil (x-90) and the 3 barrels moved; their other parts (mast/forecastle coils, the crab\'s crate stack) did not, so the object-level numbers above include the unmoved parts.')
w('- Physical route was already clear in v5 (before values above); this pass is a VISUAL sightline fix, not a physical-obstruction fix.\n')
w('### All meshes: min player clearance per segment (v5 -> v5_1)'); w('| mesh | ' + ' | '.join(s['name'] for s in R['route_qa']['segments']) + ' |'); w('|---|' + '---|' * len(R['route_qa']['segments']))
fmt = lambda v: 'n/a(>12 prefilter)' if v is None or v.get('player_clear') is None else '%.2f' % v['player_clear']
for n, v in sorted(R['route_qa']['objects'].items()):
    w('| %s%s | ' % (n, ' *' if v['changed'] else '') + ' | '.join('%s -> %s' % (fmt((v['source_v5'] or {}).get(s['name'])), fmt(v['v5_1'].get(s['name']))) for s in R['route_qa']['segments']) + ' |')
w('\n(* = changed in v5_1. Negative = pre-existing geometry inside the player envelope, e.g. Hull rail/notch at the gangplank and the pier/ramp-adjacent meshes; identical in v5 and v5_1.)\n')
w('## Tee sightline (art: wheel/chest blocked the tee centreline)')
for n, v in R['tee_visibility']['v5_1'].items():
    s0 = R['tee_visibility']['source'][n]; w('- %s: visible verts from the tee eye %d/%d -> %d/%d; azimuth offset from tee camera axis %s -> %s deg' % (n, s0['visible_from_tee_eye'], s0['sampled_verts'], v['visible_from_tee_eye'], v['sampled_verts'], s0['azimuth_offset_from_tee_axis_deg'], v['azimuth_offset_from_tee_axis_deg']))
w('')
w('## Coplanarity'); w('- %s; %d faces; source pairs %d, v5_1 pairs %d, NEW pairs %d %s\n' % (R['coplanar']['method'], R['coplanar']['faces_checked'], R['coplanar']['source_pairs'], R['coplanar']['v5_1_pairs'], R['coplanar']['new_pair_count'], R['coplanar']['new_pairs'][:5] if new_pairs else ''))
w('## Belly (horizontal Hull width, world Z, studs): v5 -> v5_1'); w('- ' + R['belly']['profile'] + '; ' + R['belly']['x_taper'])
w('| Y | ' + ' | '.join(R['belly']['widths_v5_1']['Y-0.6'].keys()) + ' |'); w('|---|' + '---|' * 7)
for Y in R['belly']['widths_v5_1']:
    w('| %s | ' % Y + ' | '.join('%s -> %s%s' % (S['widths'][Y][k], D['widths'][Y][k], '' if not S['widths'][Y][k] or not D['widths'][Y][k] else ' (x%.3f)' % (D['widths'][Y][k] / S['widths'][Y][k])) for k in D['widths'][Y]) + ' |')
w('- deck level (Y23) max width change %.4f (deck footprint fixed); water = local Y-0.6.\n' % R['belly']['deck_Y23_max_abs_change'])
w('## Sheer (top of exterior silhouette: cap rail / sheer rise / bow raise / hull / stern castle, per station, studs): v5 -> v5_1')
w('| station | v5 | v5_1 | delta |'); w('|---|---|---|---|')
for k in D['sheer']: w('| %s | %s | %s | %s |' % (k, S['sheer'][k], D['sheer'][k], R['sheer']['delta'][k]))
w('- bow rise board: 0 at x82 -> +7.0 at the stem (v5: +4.0); transom crest corners +4.6 / centre +7.0 above the castle top (v5: +1.6 / +4.0); new stern side rise boards 0 -> +4.6 on the stern castle tops. Exterior trim only (no walk surface touched).\n')
c_ = R['stern_curl']['build']; w('## Stern curl'); w('- ShipV5_SternCurl scaled %s about its crest base %s -> %s: height above base %.2f -> %.2f, top Y %.2f -> %.2f, aft-most x %.2f -> %.2f. Prop_SternCurl corner scrolls unchanged.\n' % ('1.8x', c_['base_v5'], c_['base_v5_1'], c_['height_before'], c_['height_after'], c_['top_y_before'], c_['top_y_after'], c_['aft_most_x_before'], c_['aft_most_x_after']))
o_ = R['figurehead']['build']; w('## Octopus figurehead'); w('- Prop_Figurehead rebuilt 1.6x (same origin): bbox %s -> %s; height %.1f -> %.1f; %d CoralDk underside faces.\n' % (R['figurehead']['bbox_source'], R['figurehead']['bbox_v5_1'], o_['head_height_before'], o_['head_height_after'], o_['coraldk_faces']))
w('## Bow eyes'); w('- v5: ' + json.dumps(R['bow_eyes']['v5'])); w('- v5_1: ' + json.dumps(R['bow_eyes']['build']))
w('- tee view: visible verts %d/%d (source %d/%d)\n' % (R['bow_eyes']['tee_visibility_v5_1']['visible_from_tee_eye'], R['bow_eyes']['tee_visibility_v5_1']['sampled_verts'], R['bow_eyes']['tee_visibility_source']['visible_from_tee_eye'], R['bow_eyes']['tee_visibility_source']['sampled_verts']))
w('## Hull patches'); w('- ' + json.dumps(R['patches']['v5_1'])); w('- linear scale vs v5 patch %.2fx, area %.2fx\n' % (R['patches']['linear_scale_vs_v5'], R['patches']['area_scale_vs_v5']))
h_ = R['hull_side_flag']; w('## Hull-side collider FLAG (colliders untouched)'); w('- ' + h_['method']); w('- v5: %s; v5_1: %s; increase vs v5: %s' % (h_['source_v5'], h_['v5_1'], h_['increase_vs_v5'])); w('- ' + h_['note'] + '\n')
w('## Triangles'); w('| mesh | v5 | v5_1 |'); w('|---|---|---|')
for n, v in sorted(tr.items()): w('| %s | %d | %d |' % (n, v['source'], v['v5_1']))
w('| **total visual** | **%d** | **%d** |' % (R['tris']['total_source'], R['tris']['total_v5_1'])); w('- largest mesh: %s (%d); all < 20k: %s' % (max(tr, key=lambda n: tr[n]['v5_1']), max(v['v5_1'] for v in tr.values()), not R['tris']['over_20k']))
open(os.path.join(OUT, 'fitcheck.md'), 'w', encoding='utf-8').write('\n'.join(L))
print('FITCHECK', R['overall'], FAIL, WARN)
