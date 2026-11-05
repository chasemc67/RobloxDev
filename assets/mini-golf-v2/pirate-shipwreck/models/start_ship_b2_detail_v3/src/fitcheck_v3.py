# Fitcheck for start ship v3.
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
def check(dump_path, out_dir, src_path):
    S = json.load(open(dump_path)); R = dict(source=src_path, source_dump_blend=S['blend'], v3_blend=bpy.data.filepath); ok_all = True
    # anchors
    an = {}
    for n in EMPTIES:
        o = bpy.data.objects.get(n); s = S['empties'][n]
        cur = dict(loc=list(o.location), rot=list(o.rotation_euler), scale=list(o.scale), mw=mw_list(o), parent=o.parent.name if o.parent else None)
        eq = all(cur[k] == s[k] for k in ('loc', 'rot', 'scale', 'mw', 'parent'))
        an[n] = dict(exact_equal=eq, loc_blender=cur['loc'], roblox=list(np.round(Binv(o.location), 4)), max_abs_diff=float(np.max(np.abs(np.array(cur['mw']) - np.array(s['mw'])))))
        ok_all &= eq
    R['anchors'] = an
    # collision
    cols = {o.name: o for o in bpy.data.collections['Collision'].objects}
    names_eq = sorted(cols) == sorted(S['collision']); cres = dict(count_source=len(S['collision']), count_v3=len(cols), names_identical=names_eq)
    mx = 0.0; byte_eq = 0; diff = []
    for n, o in cols.items():
        s = S['collision'].get(n)
        if s is None: diff.append(n); continue
        co, lv, ps, mi, uv = mesh_arrays(o.data); W = np.array([o.matrix_world @ v.co for v in o.data.vertices], dtype=np.float64)
        same = (sha(co) == s['co_sha'] and sha(lv) == s['loops_sha'] and sha(ps) == s['polys_sha'] and mw_list(o) == s['mw'] and sha(W) == s['world_sha'])
        byte_eq += int(same); mx = max(mx, float(np.max(np.abs(W - np.array(s['world_verts'])))))
        if not same: diff.append(n)
    cres.update(byte_identical=byte_eq, max_abs_world_vertex_diff=mx, differing=diff,
                collection_membership_identical=sorted(o.name for o in bpy.data.collections['Collision'].objects) == S['collections']['Collision'])
    R['collision'] = cres; ok_all &= (names_eq and byte_eq == len(S['collision']) == 190 and mx == 0.0)
    # meshes: unchanged / changed
    ms = {}
    for n in ORIG:
        o = bpy.data.objects[n]; s = S['objects'][n]; co, lv, ps, mi, uv = mesh_arrays(o.data)
        e = dict(geometry_identical=(sha(co) == s['co_sha'] and sha(lv) == s['loops_sha'] and sha(ps) == s['polys_sha']),
                 materials_identical=(sha(mi) == s['mi_sha'] and [m.name for m in o.data.materials] == s['mats']), uv_identical=sha(uv) == s['uv_sha'],
                 origin_matrix_identical=mw_list(o) == s['mw'], name_identical=True, mesh_datablock_name_identical=o.data.name == s['mesh_name'],
                 tris_source=s['tris'], tris_v3=tris(o.data), mats_source=s['mats'], mats_v3=[m.name for m in o.data.materials])
        if n.startswith('Ramp'):
            W = np.array([o.matrix_world @ v.co for v in o.data.vertices], dtype=np.float64); e['world_verts_max_abs_diff'] = float(np.max(np.abs(W - np.array(s['world_verts']))))
            ok_all &= e['geometry_identical'] and e['materials_identical'] and e['uv_identical'] and e['origin_matrix_identical'] and e['world_verts_max_abs_diff'] == 0.0
        ms[n] = e
    R['meshes_vs_source'] = ms
    # hull: all source triangles except the 12 bowsprit tris still present (positions), the rest is additive
    bm = world_bm(bpy.data.objects['Hull'])
    cur = set(tuple(sorted(tuple(round(c, 4) for c in v.co) for v in f.verts)) for f in bm.faces); src = [tuple(map(tuple, t)) for t in S['hull_tris']]
    missing = [t for t in src if t not in cur]; bm.free()
    R['hull_retained'] = dict(source_tris=len(src), source_tris_still_present=len(src) - len(missing), missing=len(missing),
                              missing_are_bowsprit=all(all(_bs_dist(c) < 1.95 for c in t) for t in missing), bowsprit_def='within 1.95 studs of the source bowsprit beam axis (hull frame 118,45 -> 215,70)')
    # hull bottom / submersion
    hb = hull_bottom_profile(); sub = []
    for a, b in zip(S['hull_bottom'], hb):
        sub.append(dict(x=a['x'], source_bottom_y=a['bottom_y'], v3_bottom_y=b['bottom_y'], identical=a['bottom_y'] == b['bottom_y'],
                        submerged_below_water_studs=None if b['bottom_y'] is None else round(WATER_Y - b['bottom_y'], 3)))
    R['hull_submersion'] = dict(water_level_local=WATER_Y, stations=sub, note='bottom = lowest Hull point at each x station (rays every 0.25 studs across the beam); water world Y0 = local -0.6')
    # walking surfaces
    R['walk_surfaces'] = dict(source=S['walk'], v3=deck_walk_surfaces()); R['walk_surfaces']['identical'] = R['walk_surfaces']['source'] == R['walk_surfaces']['v3']
    # probes
    pv = probes(scene_trees()); ps_ = S['probes']
    door_same = all((a['hit'] is None) == (b['hit'] is None) and (a['hit'] is None or a['hit'][0] == b['hit'][0]) for a, b in zip(ps_['door_rays'], pv['door_rays']))
    R['spawn_headroom'] = dict(source=ps_['spawn_headroom'], v3=pv['spawn_headroom'], identical=ps_['spawn_headroom'] == pv['spawn_headroom'])
    R['door_clearance'] = dict(rays=len(pv['door_rays']), rays_blocked_source=sum(r['hit'] is not None for r in ps_['door_rays']), rays_blocked_v3=sum(r['hit'] is not None for r in pv['door_rays']),
                               identical=door_same, blocked_v3=[r for r in pv['door_rays'] if r['hit'] is not None][:10])
    R['tee_sightlines'] = dict(eye_roblox=pv['tee_eye'], source=ps_['tee_sightlines'], v3=pv['tee_sightlines'],
                               identical=all(ps_['tee_sightlines'][k]['first_hit'] == pv['tee_sightlines'][k]['first_hit'] for k in pv['tee_sightlines']))
    # corridor clearance of new / rebuilt geometry
    F2 = Binv(bpy.data.objects['RampFlight2'].matrix_world.translation); CUP = Binv(bpy.data.objects['CupRef'].matrix_world.translation)
    props = [o for o in bpy.data.collections['Props'].objects if o.type == 'MESH']
    src_hull = set(tuple(round(c, 4) for c in v) for t in S['hull_tris'] for v in t)
    groups = [(o.name, sample_points(o)) for o in props] + [('Rigging(rebuilt)', sample_points(bpy.data.objects['Rigging']))]
    hp = sample_points(bpy.data.objects['Hull'], centres=False); hv = np.array([tuple(round(c, 4) for c in B(p)) for p in hp])
    newmask = np.array([tuple(r) not in src_hull for r in hv]); groups.append(('Hull(new bowsprit)', hp[newmask]))
    corr = {k: dict(min_dist=1e9, closest=None) for k in list(CORR) + ['flight2_apron_yawed', 'flight2_apron_unyawed', 'cup_clear_r12']}
    per_obj = {}
    for n, P in groups:
        if len(P) == 0: continue
        dd = {}
        for k, (lo, hi) in CORR.items(): dd[k] = float(aabb_dist(P, lo, hi).min())
        dd['flight2_apron_yawed'] = float(f2_dist(P, F2, True).min()); dd['flight2_apron_unyawed'] = float(f2_dist(P, F2, False).min())
        dd['cup_clear_r12'] = float(max(0.0, (np.sqrt((P[:, 0] - CUP[0]) ** 2 + (P[:, 2] - CUP[2]) ** 2) - 12.0).min()))
        per_obj[n] = {k: round(v, 3) for k, v in dd.items()}
        for k, v in dd.items():
            if v < corr[k]['min_dist']: corr[k] = dict(min_dist=round(v, 3), closest=n)
    gmin = min(v['min_dist'] for v in corr.values()); gk = min(corr, key=lambda k: corr[k]['min_dist'])
    R['route_corridor'] = dict(boxes_roblox=CORR, flight2_box='flight2 local frame: along -1..72, lateral +-9, height -13..+7 (yawed -30 deg as built in Studio, and unyawed as exported)',
                               cup='12-stud clear radius around CupRef', per_zone=corr, per_object=per_obj, min_clearance=dict(studs=gmin, zone=gk, object=corr[gk]['closest']),
                               any_inside=any(v['min_dist'] <= 0 for v in corr.values()),
                               method='min distance from every vertex and face centre of each new/rebuilt mesh to each corridor volume (Roblox coords)')
    ok_all &= not R['route_corridor']['any_inside']
    # coplanarity: new faces vs every other visual mesh
    trees = scene_trees(); copl = []; checked = 0
    for o in props + [bpy.data.objects['Rigging']]:
        bm = world_bm(o)
        for f in bm.faces:
            c = f.calc_center_median(); n0 = f.normal; checked += 1
            for nme, (T, bm2) in trees.items():
                if nme == o.name: continue
                loc, nor, idx, dist = T.find_nearest(c, 0.03)
                if loc is not None and abs(nor.dot(n0)) > 0.995 and abs((c - loc).dot(nor)) < 0.02:
                    copl.append(dict(obj=o.name, other=nme, at=list(np.round(Binv(c), 2)), dist=round(dist, 4)))
        bm.free()
    R['coplanarity'] = dict(faces_checked=checked, coplanar_pairs=len(copl), examples=copl[:20],
                            method='each new/rebuilt face centre: nearest surface of every other visual mesh within 0.03 with parallel normal (|dot|>0.995) and plane gap <0.02')
    # mesh stats + envelope flags
    allm = {}
    tot = 0
    src_union = None
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.startswith('COL'): continue
        mn, mx_ = roblox_bbox(o); t = tris(o.data); tot += t
        allm[o.name] = dict(collection=[c.name for c in o.users_collection][0], tris=t, materials=[m.name for m in o.data.materials],
                            origin_roblox=list(np.round(Binv(o.location), 3)), bbox_min_roblox=mn, bbox_max_roblox=mx_, under_20k=t < 20000)
    R['tris'] = dict(per_mesh={k: v['tris'] for k, v in allm.items()}, total=tot, max_mesh=max(allm, key=lambda k: allm[k]['tris']), all_under_20k=all(v['under_20k'] for v in allm.values()))
    ok_all &= R['tris']['all_under_20k']
    # envelope: compare each new prop bbox to the source visual + collider union bbox
    cmn = np.array([1e9] * 3); cmx = -cmn
    for n in ORIG + list(cols):
        o = bpy.data.objects[n]
        if n == 'Rigging': continue
        a, b = roblox_bbox(o); cmn = np.minimum(cmn, a); cmx = np.maximum(cmx, b)
    srcrig = S['objects']['Rigging']
    flags = []
    for o in props + [bpy.data.objects['Rigging']]:
        a, b = roblox_bbox(o); out_ = [k for k, ax in enumerate('xyz') if a[k] < cmn[k] - 0.01 or b[k] > cmx[k] + 0.01]
        if out_: flags.append(dict(obj=o.name, axes_outside=['xyz'[k] for k in out_], bbox_min=a, bbox_max=b))
    walk_props = ['Prop_CargoCluster', 'Prop_Crab', 'Prop_TreasureChest', 'Prop_SternWheel', 'Prop_RopeCoils']
    R['envelope'] = dict(source_union_bbox_roblox=[cmn.round(2).tolist(), cmx.round(2).tolist()], props_outside_union=flags,
                         visual_only_on_walkable_deck=walk_props,
                         notes=['Deck props (cargo, crab, chest, wheel, rope coils) stand on the walkable deck with NO collider: players/balls pass through them unless the build bot adds simple CanCollide boxes. They are all outside the route corridor.',
                                'COL_Mast_Main (unchanged) still spans the original 8..165 mast; the visual main mast is now snapped at ~106 (+ splinters to ~113) -> the collider sticks ~50 studs above the visible stump (it is the optional mast collider; consider disabling or shortening it in Studio).',
                                'Stern curl, figurehead, curled bowsprit, cap rails and hull dressing are scenery with no collider (same as the source hull/rigging scenery).'])
    R['pass_hard_checks'] = bool(ok_all)
    R['floaters_source'] = S['floaters']
    json.dump(R, open(os.path.join(out_dir, 'fitcheck.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    json.dump(dict(allm=allm), open(os.path.join(out_dir, 'logs', 'mesh_stats.json'), 'w'), indent=1)
    print('FITCHECK_DONE pass_hard=', ok_all, 'min clearance', R['route_corridor']['min_clearance'], 'coplanar', len(copl))

if MODE == 'dump':
    json.dump(dump(), open(A[1], 'w')); print('DUMP_OK', A[1])
else:
    check(A[1], A[2], A[3])
