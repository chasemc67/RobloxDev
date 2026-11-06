# check() for whimsy v5, exec'd inside fitcheck_v5.py (shares its helpers: mesh_arrays, sha, mw_list, probes, CORR, f2_dist, floater_scan, coplanar_scan ...).
# Baseline = dump of source_v3_2.blend. Rules:
#   LOCKED (DeckCabin + 3 ramps): geometry, UV, material assignment, world matrix exact.  Anchors (4 empties) exact.  All 190 colliders byte-identical.
#   Every source mesh: name, origin matrix, mesh datablock name, collections identical.
#   Only EXPECTED_CHANGED may differ: hull-belly-warped meshes (vertex positions only; topology/UV/materials must stay), Prop_Figurehead + Prop_Stovepipe
#   (rebuilt in place), Rigging (crow's nest vertices rotated + warp of its low anchor-line verts). New meshes must be ShipV5_* in Props.
from mathutils import Vector
LOCKED = ['DeckCabin', 'RampFlight1', 'RampLanding', 'RampFlight2']
REBUILT = ['Prop_Figurehead', 'Prop_Stovepipe']
TAN15 = math.tan(math.radians(15))
# zone trees copied verbatim from prior_scripts/fitcheck_v32_check.py
def _box_tree(lo, hi):
    V = [B((x, y, z)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    P = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return BVHTree.FromPolygons(V, P)
def _f2_tree(F2, yawed):
    d2 = np.array((-0.5, 0, math.sqrt(3) / 2)) if yawed else np.array((0, 0, 1.0)); n2 = np.array((d2[2], 0, -d2[0])); up = np.array((0, 1.0, 0))
    V = [B(F2 + a * d2 + l * n2 + y * up) for a in (-1.0, 72.0) for y in (-13.0, 7.0) for l in (-9.0, 9.0)]
    P = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return BVHTree.FromPolygons(V, P)
def _cyl_tree(c, r, n=64):
    R = r / math.cos(math.pi / n); V = []
    for y in (-60.0, 400.0):
        for k in range(n): a = 2 * math.pi * k / n; V.append(B((c[0] + R * math.cos(a), y, c[2] + R * math.sin(a))))
    P = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    return BVHTree.FromPolygons(V, P)


def _widths():
    trees = scene_trees(['Hull']); T = trees['Hull'][0]; out = {}
    for Y in (-0.6, 6.0, 12.0, 18.0, 23.0):
        row = {}
        for x in (-140.0, -100.0, -60.0, -20.0, 20.0, 60.0, 100.0, 130.0):
            a = T.ray_cast(Vector(B((x, Y, -300.0))), Vector(B((0, 0, 1))), 700); b = T.ray_cast(Vector(B((x, Y, 300.0))), Vector(B((0, 0, -1))), 700)
            row['x%d' % x] = None if a[0] is None or b[0] is None else round(float(Binv(b[0])[2] - Binv(a[0])[2]), 3)
        out['Y%.1f' % Y] = row
    return out
def _hull_samples():
    T = scene_trees(['Hull'])['Hull'][0]; P = []; key = []
    for x in np.arange(-158.0, 150.0, 4.0):
        for Y in np.arange(-0.5, 18.01, 1.5):
            for z0, dz in ((-300.0, 1), (300.0, -1)):
                r = T.ray_cast(Vector(B((x, Y, z0))), Vector(B((0, 0, dz))), 700)
                if r[0] is not None: P.append(list(Binv(r[0]))); key.append((float(x), float(Y), dz))
    return P, key
def _obbs():
    out = []
    for o in bpy.data.collections['Collision'].objects:
        if not o.name.startswith('COL_HullExt'): continue
        W = np.array([Binv(o.matrix_world @ v.co) for v in o.data.vertices]); c = W.mean(0)
        d = sorted([W[i] - W[0] for i in range(1, len(W))], key=lambda v: np.linalg.norm(v))[:3]
        out.append((o.name, c, np.array([nrm(v) for v in d]), np.array([np.linalg.norm(v) / 2 for v in d])))
    return out
def _outside(P, obbs):
    P = np.asarray(P); best = np.full(len(P), 1e9); who = [''] * len(P)
    for n, c, ax, hs in obbs:
        q = (P - c) @ ax.T; d = np.linalg.norm(np.maximum(np.abs(q) - hs, 0), axis=1)
        for i in np.where(d < best)[0]: who[i] = n
        best = np.minimum(best, d)
    return best, who
def _curl_components(name):
    o = bpy.data.objects[name]; bm = world_bm(o); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-3); seen = set(); out = []
    for f in bm.faces:
        if f in seen: continue
        st = [f]; comp = []; seen.add(f)
        while st:
            a = st.pop(); comp.append(a)
            for e in a.edges:
                for g in e.link_faces:
                    if g not in seen: seen.add(g); st.append(g)
        co = np.array([Binv(v.co) for g in comp for v in g.verts]); out.append(dict(faces=len(comp), y=[round(float(co[:, 1].min()), 2), round(float(co[:, 1].max()), 2)],
                                                                                 height=round(float(co[:, 1].max() - co[:, 1].min()), 2), x=[round(float(co[:, 0].min()), 2), round(float(co[:, 0].max()), 2)]))
    bm.free(); return sorted(out, key=lambda d: -d['faces'])
def v5_extra():
    P, key = _hull_samples()
    F2 = Binv(bpy.data.objects['RampFlight2'].matrix_world.translation); CUP = Binv(bpy.data.objects['CupRef'].matrix_world.translation)
    ZT = {k: _box_tree(lo, hi) for k, (lo, hi) in CORR.items()}
    ZT['flight2_apron_yawed'] = _f2_tree(F2, True); ZT['flight2_apron_unyawed'] = _f2_tree(F2, False); ZT['cup_clear_r12'] = _cyl_tree(CUP, 12.0)
    SEG = corridor_segments(F2, True) + corridor_segments(F2, False)[-1:]; corr = {}
    for o in [o for o in bpy.data.collections['Props'].objects if o.type == 'MESH'] + [bpy.data.objects['Rigging'], bpy.data.objects['Hull']]:
        bm = world_bm(o); T = BVHTree.FromBMesh(bm); bm.free()
        corr[o.name] = dict(continuous=corridor_clear(sample_points(o), SEG), zone_tris={k: len(T.overlap(Z)) for k, Z in ZT.items() if T.overlap(Z)})
    return dict(widths=_widths(), hull_samples=P, hull_sample_keys=key, stern_curl_components=_curl_components('Prop_SternCurl'), corridor_source=corr)

# continuous corridor (route_qa style): cabin->door->tee->gangplank 8 wide (half 4), flights/landing 12 wide (half 6); walk-height band -1 .. +10
def corridor_segments(F2, yawed):
    d2 = np.array((-0.5, 0, math.sqrt(3) / 2)) if yawed else np.array((0, 0, 1.0))
    segs = [((-120.0, 24.0, -17.0), (-120.0, 24.0, 62.5), 4.0, 'cabin_door_tee_gangplank'),
            ((-120.0, 24.0, 62.5), (-120.0, 12.0, 113.5), 6.0, 'flight1'),
            ((-120.0, 12.0, 113.5), (-120.0, 12.0, 131.0), 6.27, 'landing (Studio v30 exit 12.54 wide)'),
            (tuple(F2), tuple(F2 + d2 * 72.0 + np.array((0, -12.0, 0))), 6.0, 'flight2_' + ('yawed' if yawed else 'unyawed'))]
    return segs
def corridor_clear(P, segs):
    res = {}
    for a, b, hw, nm in segs:
        a = np.array(a); b = np.array(b); ab = b - a; abxz = np.array((ab[0], ab[2])); L2 = float(abxz @ abxz)
        Q = np.column_stack([P[:, 0] - a[0], P[:, 2] - a[2]]); t = np.clip(Q @ abxz / L2, 0, 1)
        dxz = np.linalg.norm(Q - np.outer(t, abxz), axis=1); yw = a[1] + t * ab[1]
        dy = np.maximum(np.maximum((yw - 1.0) - P[:, 1], 0), P[:, 1] - (yw + 10.0))
        d = np.sqrt(np.maximum(dxz - hw, 0) ** 2 + dy ** 2); inside = (dxz <= hw) & (dy <= 0)
        res[nm] = dict(min_clear=round(float(d.min()), 3), inside_points=int(inside.sum()))
    return res

def check(dump_path, out_dir, src_path, build_log_path):
    S = json.load(open(dump_path)); BL = json.load(open(build_log_path)); FAIL = []; WARN = []; FLAG = []
    R = dict(source=src_path, source_dump_blend=S['blend'], v5_blend=bpy.data.filepath, blender=bpy.app.version_string)
    WARPED = sorted(BL['hull_warp']['moved_objects_max_disp']); EXPECTED = sorted(set(WARPED) | set(REBUILT) | {'Rigging'})
    R['expected_changed'] = dict(hull_warp=WARPED, rebuilt_in_place=REBUILT, rigging='crow\'s nest vertices rotated (+ warp of low anchor-line verts)')
    # ---------------- anchors
    an = {}
    for n in EMPTIES:
        o = bpy.data.objects.get(n); s = S['empties'][n]
        if o is None: an[n] = dict(present=False); FAIL.append('anchor missing ' + n); continue
        cur = dict(loc=list(o.location), rot=list(o.rotation_euler), scale=list(o.scale), mw=mw_list(o), parent=o.parent.name if o.parent else None)
        eq = all(cur[k] == s[k] for k in ('loc', 'rot', 'scale', 'mw', 'parent'))
        an[n] = dict(exact_equal=eq, roblox=list(np.round(Binv(o.location), 4)))
        if not eq: FAIL.append('anchor changed ' + n)
    R['anchors'] = an
    emp_cur = set(o.name for o in bpy.data.objects if o.type == 'EMPTY'); R['empties_identical_set'] = emp_cur == set(S['empties'])
    if not R['empties_identical_set']: FAIL.append('empty set changed')
    # ---------------- collision: byte-identical to source (NOT verified vs Studio v30)
    cols = {o.name: o for o in bpy.data.collections['Collision'].objects}
    names_eq = sorted(cols) == sorted(S['collision']); byte_eq = 0; diff = []; mx = 0.0
    for n, s in S['collision'].items():
        o = cols.get(n)
        if o is None: diff.append(n + ' (missing)'); continue
        co, lv, ps, mi, uv = mesh_arrays(o.data); W = np.array([o.matrix_world @ v.co for v in o.data.vertices], dtype=np.float64)
        same = (sha(co) == s['co_sha'] and sha(lv) == s['loops_sha'] and sha(ps) == s['polys_sha'] and sha(mi) == s['mi_sha'] and sha(uv) == s['uv_sha']
                and mw_list(o) == s['mw'] and sha(W) == s['world_sha'] and [m.name for m in o.data.materials] == s['mats'] and o.data.name == s['mesh_name']
                and [c.name for c in o.users_collection] == s['coll'])
        byte_eq += int(same); mx = max(mx, float(np.max(np.abs(W - np.array(s['world_verts']))))) if W.shape == np.array(s['world_verts']).shape else mx
        if not same: diff.append(n)
    R['collision'] = dict(count_source=len(S['collision']), count_v5=len(cols), names_identical=names_eq, byte_identical_to_source=byte_eq, max_abs_world_vertex_diff=mx, differing=diff,
                          studio_v30_sync='NOT VERIFIED. These are the stale v3_2 Blender colliders. Studio v30 colliders (landing exit 12.54, HullExt disabled at notch, hull-side refit) are authoritative; '
                                          'no collision FBX is handed off (see out/fbx/UNSYNCED_keep_studio_v30_colliders.txt).')
    if not (names_eq and len(cols) == 190 and byte_eq == 190 and mx == 0.0): FAIL.append('collision not byte-identical to source ' + str(diff))
    # ---------------- source meshes
    ms = {}
    for n, s in S['objects'].items():
        o = bpy.data.objects.get(n)
        if o is None or o.type != 'MESH': ms[n] = dict(present=False); FAIL.append('source mesh missing ' + n); continue
        co, lv, ps, mi, uv = mesh_arrays(o.data)
        e = dict(present=True, verts_identical=sha(co) == s['co_sha'], topology_identical=(sha(lv) == s['loops_sha'] and sha(ps) == s['polys_sha']),
                 material_assignment_identical=(sha(mi) == s['mi_sha'] and [m.name for m in o.data.materials] == s['mats']), uv_identical=sha(uv) == s['uv_sha'],
                 origin_matrix_identical=mw_list(o) == s['mw'], mesh_datablock_name_identical=o.data.name == s['mesh_name'],
                 collections_identical=[c.name for c in o.users_collection] == s['coll'], tris_source=s['tris'], tris_v5=tris(o.data))
        e['category'] = 'LOCKED' if n in LOCKED else 'rebuilt_in_place' if n in REBUILT else 'hull_warp' if n in WARPED else 'rigging_nest' if n == 'Rigging' else 'must_unchanged'
        if n in LOCKED and 'world_verts' in s:
            W = np.array([o.matrix_world @ v.co for v in o.data.vertices], dtype=np.float64); e['world_verts_max_abs_diff'] = float(np.max(np.abs(W - np.array(s['world_verts']))))
        exact = e['verts_identical'] and e['topology_identical'] and e['material_assignment_identical'] and e['uv_identical']
        e['changed_vs_source'] = not exact
        if not (e['origin_matrix_identical'] and e['mesh_datablock_name_identical'] and e['collections_identical']): FAIL.append('origin/datablock/collection changed ' + n)
        if n not in EXPECTED and not exact: FAIL.append(e['category'] + ' mesh changed ' + n)
        if (n in WARPED or n == 'Rigging') and not (e['topology_identical'] and e['material_assignment_identical'] and e['uv_identical']): FAIL.append('warped/rigging topology/UV/material changed ' + n)
        if n in LOCKED and (not exact or e.get('world_verts_max_abs_diff', 0) != 0.0): FAIL.append('LOCKED changed ' + n)
        ms[n] = e
    R['meshes_vs_source'] = ms
    R['changed_meshes'] = sorted(n for n, e in ms.items() if e.get('changed_vs_source'))
    new_objs = sorted(o.name for o in bpy.data.objects if o.name not in S['objects'] and o.name not in S['collision'] and o.name not in S['empties'])
    bad_new = [n for n in new_objs if not n.startswith('ShipV5_') or [c.name for c in bpy.data.objects[n].users_collection] != ['Props']]
    R['new_objects'] = new_objs; R['new_objects_bad'] = bad_new
    if bad_new: FAIL.append('new objects not ShipV5_* in Props ' + str(bad_new))
    # ---------------- walk / probes
    R['walk_surfaces'] = dict(source=S['walk'], v5=deck_walk_surfaces()); R['walk_surfaces']['identical'] = R['walk_surfaces']['source'] == R['walk_surfaces']['v5']
    if not R['walk_surfaces']['identical']: FAIL.append('walk surfaces changed')
    trees = scene_trees(); pv = probes(trees); ps_ = S['probes']
    R['spawn_headroom'] = dict(source=ps_['spawn_headroom'], v5=pv['spawn_headroom'], identical=ps_['spawn_headroom'] == pv['spawn_headroom'])
    if not R['spawn_headroom']['identical']: WARN.append('spawn headroom first hit differs')
    door_same = all((a['hit'] is None) == (b['hit'] is None) and (a['hit'] is None or a['hit'][0] == b['hit'][0]) for a, b in zip(ps_['door_rays'], pv['door_rays']))
    R['door_clearance'] = dict(rays=len(pv['door_rays']), blocked_source=sum(r['hit'] is not None for r in ps_['door_rays']), blocked_v5=sum(r['hit'] is not None for r in pv['door_rays']), identical=door_same)
    if not door_same: FAIL.append('door clearance rays changed')
    R['tee_sightlines'] = dict(eye_roblox=pv['tee_eye'], source=ps_['tee_sightlines'], v5=pv['tee_sightlines'],
                               identical=all(ps_['tee_sightlines'][k]['first_hit'] == pv['tee_sightlines'][k]['first_hit'] for k in pv['tee_sightlines']))
    if not R['tee_sightlines']['identical']: FAIL.append('tee sightline first hits changed')
    # ---------------- bow eyes outside tee view
    eye = np.array(pv['tee_eye']); ev = []
    def first(o, d, L):
        best = None
        for n, (T, bm) in trees.items():
            loc, nor, idx, dist = T.ray_cast(Vector(B(o)), Vector(B(nrm(d))), L)
            if loc is not None and (best is None or dist < best[1]): best = (n, dist)
        return best
    cam_d = nrm(np.array((0.93, 0.29, -0.25)))
    for e in BL.get('bow_eyes', []):
        c = np.array(e['centre']) + np.array(e['normal']) * 0.9; L_ = float(np.linalg.norm(c - eye)); h = first(eye, c - eye, L_ - 0.05)
        ang = math.degrees(math.acos(float(np.dot(nrm(c - eye), cam_d))))
        ev.append(dict(side=e['side'], centre=e['centre'], dist_from_tee=round(L_, 1), first_hit_on_ray=None if h is None else [h[0], round(h[1], 2)], occluded=h is not None,
                       angle_from_tee_cam_axis_deg=round(ang, 1), facing_away_from_tee=bool(np.dot(np.array(e['normal']), nrm(eye - np.array(e['centre']))) < 0)))
    R['bow_eyes_tee_view'] = ev
    if any(not x['occluded'] and not x['facing_away_from_tee'] for x in ev): FAIL.append('bow eye visible from tee')
    # ---------------- route corridor: prior zones (same method) + continuous corridor
    F2 = Binv(bpy.data.objects['RampFlight2'].matrix_world.translation); CUP = Binv(bpy.data.objects['CupRef'].matrix_world.translation)
    groups = [o for o in bpy.data.collections['Props'].objects if o.type == 'MESH'] + [bpy.data.objects['Rigging'], bpy.data.objects['Hull']]
    ZT = {k: _box_tree(lo, hi) for k, (lo, hi) in CORR.items()}
    ZT['flight2_apron_yawed'] = _f2_tree(F2, True); ZT['flight2_apron_unyawed'] = _f2_tree(F2, False); ZT['cup_clear_r12'] = _cyl_tree(CUP, 12.0)
    SEG = corridor_segments(F2, True) + corridor_segments(F2, False)[-1:]
    per_obj = {}; tri_hits = {}; cont = {}
    for o in groups:
        P = sample_points(o); dd = {}
        for k, (lo, hi) in CORR.items(): dd[k] = float(aabb_dist(P, lo, hi).min())
        dd['flight2_apron_yawed'] = float(f2_dist(P, F2, True).min()); dd['flight2_apron_unyawed'] = float(f2_dist(P, F2, False).min())
        dd['cup_clear_r12'] = float(max(0.0, (np.sqrt((P[:, 0] - CUP[0]) ** 2 + (P[:, 2] - CUP[2]) ** 2) - 12.0).min()))
        per_obj[o.name] = {k: round(v, 3) for k, v in dd.items()}
        cont[o.name] = corridor_clear(P, SEG)
        bm = world_bm(o); T = BVHTree.FromBMesh(bm); bm.free()
        for k, Z in ZT.items():
            ov = T.overlap(Z)
            if ov: tri_hits.setdefault(o.name, {})[k] = len(ov)
    focus = set(new_objs) | set(R['changed_meshes'])
    zmin = {k: min(((v[k], n) for n, v in per_obj.items() if n in focus), default=(None, None)) for k in ZT}
    cmin = {}
    for n in focus:
        if n not in cont: continue
        for k, v in cont[n].items():
            if k not in cmin or v['min_clear'] < cmin[k][0]: cmin[k] = (v['min_clear'], n)
    CS = S['v5_extra']['corridor_source']
    intr_zone = {n: {k: c for k, c in v.items() if c > CS.get(n, {}).get('zone_tris', {}).get(k, 0)} for n, v in tri_hits.items() if n in focus}
    intr_zone = {n: v for n, v in intr_zone.items() if v}
    intr_cont = {n: {k: v['inside_points'] for k, v in c.items() if v['inside_points'] > CS.get(n, {}).get('continuous', {}).get(k, {}).get('inside_points', 0)} for n, c in cont.items() if n in focus}
    intr_cont = {n: v for n, v in intr_cont.items() if v}
    preexisting = {n: dict(zone_tris=CS[n]['zone_tris'], continuous_inside={k: v['inside_points'] for k, v in CS[n]['continuous'].items() if v['inside_points']}) for n in CS
                   if CS[n]['zone_tris'] or any(v['inside_points'] for v in CS[n]['continuous'].values())}
    R['route_corridor'] = dict(zones_roblox=CORR, per_zone_min_new_or_changed={k: dict(min_dist=v[0], closest=v[1]) for k, v in zmin.items()},
                               continuous_corridor=dict(segments=[dict(a=list(np.round(a, 2)), b=list(np.round(b, 2)), half_width=hw, name=nm) for a, b, hw, nm in SEG],
                                                        band='walk height -1 .. +10 (linear along each flight)', per_segment_min_new_or_changed={k: dict(min_clear=v[0], closest=v[1]) for k, v in cmin.items()}),
                               per_object_zones=per_obj, per_object_continuous=cont, triangle_intersections_all=tri_hits, preexisting_in_source_unchanged=preexisting,
                               intrusions_new_or_changed_vs_source=dict(zone_triangles=intr_zone, continuous_points=intr_cont),
                               method='(a) prior v3_2 zone boxes: min distance of every vertex + face centre, plus BVH triangle overlap against the zone boundaries; (b) continuous corridor capsules along the x=-120 route (half-width 4 cabin->gangplank, 6 flights, 6.27 landing for the Studio v30 12.54 exit), flight2 both yawed -30 and unyawed.')
    if intr_zone or intr_cont: FAIL.append('route corridor intrusion by new/changed mesh ' + json.dumps(dict(z=intr_zone, c=intr_cont)))
    if 'ShipV5_Hammock' in per_obj:
        R['hammock'] = dict(included=True, zones=per_obj['ShipV5_Hammock'], continuous=cont['ShipV5_Hammock'], min_zone=min(per_obj['ShipV5_Hammock'].values()),
                            min_continuous=min(v['min_clear'] for v in cont['ShipV5_Hammock'].values()))
    else: R['hammock'] = dict(included=False)
    # ---------------- coplanarity (same method/tolerances as v3_1/v3_2) on every new/changed mesh, plus the source scan of the same source objects
    names = sorted(set(COPL_V5_SOURCE) | focus)
    cp = coplanar_scan(names, trees)
    src_keys = set((p['obj'], p['other'], tuple(p['at'])) for p in S['coplanar']['pairs'])
    newp = [p for p in cp['pairs'] if (p['obj'], p['other'], tuple(p['at'])) not in src_keys]
    pairs_by = {}
    for p in cp['pairs']: pairs_by.setdefault(p['obj'] + '|' + p['other'], 0); pairs_by[p['obj'] + '|' + p['other']] += 1
    R['coplanarity'] = dict(objects_checked=names, faces_checked=cp['faces_checked'], source_pairs_same_scan=len(S['coplanar']['pairs']), source_faces_checked=S['coplanar']['faces_checked'],
                            v5_pairs=len(cp['pairs']), v5_pairs_not_in_source=len(newp), new_examples=newp[:30], v5_pairs_by_object=pairs_by,
                            source_pairs_by_object={}, method='each face centre: nearest surface of every other visual mesh within 0.03, |dot|>0.995, plane gap <0.02 (unchanged from v3_1/v3_2). '
                            'Scan list now also includes Hull/Rigging and all warped/new meshes; the same list was scanned on the source for a like-for-like count.')
    for p in S['coplanar']['pairs']: R['coplanarity']['source_pairs_by_object'].setdefault(p['obj'] + '|' + p['other'], 0); R['coplanarity']['source_pairs_by_object'][p['obj'] + '|' + p['other']] += 1
    newp_v5 = [p for p in newp if p['obj'].startswith('ShipV5_') or p['other'].startswith('ShipV5_') or p['obj'] in REBUILT or p['other'] in REBUILT]
    if newp_v5: FAIL.append('coplanar faces introduced by new/rebuilt meshes: %d' % len(newp_v5))
    elif newp: WARN.append('coplanar pairs not in source (warp-related): %d' % len(newp))
    # ---------------- hull widening + hull-side collider mismatch
    wb = S['v5_extra']['widths']; wa = _widths()
    R['hull_widths'] = dict(before=wb, after=wa, ratio={Y: {x: (round(wa[Y][x] / wb[Y][x], 4) if wb[Y][x] and wa[Y][x] else None) for x in wb[Y]} for Y in wb},
                            note='horizontal hull width (world Z) at world Y levels; water = -0.6 local. Warp: x1.15 about z=Y*tan15 for Y<=6, smooth to x1.0 at Y18; ' + BL['hull_warp']['x_taper'])
    for Y in ('Y18.0', 'Y23.0'):
        for x, v in wb[Y].items():
            if v and wa[Y][x] and abs(wa[Y][x] - v) > (0.6 if Y == 'Y18.0' else 0.01): FAIL.append('hull width changed near deck %s %s' % (Y, x))
    obbs = _obbs(); P0 = np.array(S['v5_extra']['hull_samples']); key0 = [tuple(k) for k in S['v5_extra']['hull_sample_keys']]
    P1, key1 = _hull_samples(); P1 = np.array(P1); key1 = [tuple(k) for k in key1]
    m1 = {k: i for i, k in enumerate(key1)}; common = [(i, m1[k]) for i, k in enumerate(key0) if k in m1]
    d0, _ = _outside(P0[[i for i, j in common]], obbs); d1, who = _outside(P1[[j for i, j in common]], obbs); inc = d1 - d0
    worst = np.argsort(-inc)[:10]
    per_box = {}
    for k_, (i, j) in enumerate(common):
        if inc[k_] > 0.5: per_box[who[k_]] = max(per_box.get(who[k_], 0.0), round(float(inc[k_]), 3))
    R['hullext_collider_mismatch'] = dict(samples=len(common), source_max_outside=round(float(d0.max()), 3), v5_max_outside=round(float(d1.max()), 3),
        source_p95_outside=round(float(np.percentile(d0, 95)), 3), v5_p95_outside=round(float(np.percentile(d1, 95)), 3),
        increase_max=round(float(inc.max()), 3), increase_p95=round(float(np.percentile(inc, 95)), 3), samples_increase_over_0_5=int((inc > 0.5).sum()), samples_increase_over_1=int((inc > 1.0).sum()),
        boxes_with_increase_over_0_5=dict(sorted(per_box.items())),
        worst=[dict(at=list(np.round(P1[common[w][1]], 2)), outside_before=round(float(d0[w]), 3), outside_after=round(float(d1[w]), 3), box=who[w]) for w in worst],
        method='outer Hull surface sampled by horizontal rays (x-158..146 step 4, Y-0.5..18 step 1.5, both sides); distance outside the nearest COL_HullExt oriented box, source vs v5 at the same ray',
        verdict='FLAG for builder: the widened visual belly sits outside the OLD v3_2 COL_HullExt volumes by up to the increase above. Colliders were NOT modified here; Studio v30 hull-side refit is authoritative and must be re-checked against this visual hull.')
    if inc.max() > 0.25: FLAG.append('hull-side collider mismatch: widened visual hull extends up to %.2f studs further outside the (stale v3_2) COL_HullExt boxes (%d samples >0.5); builder must re-fit/verify against Studio v30' % (inc.max(), int((inc > 0.5).sum())))
    hb = hull_bottom_profile(); sub = []
    for a, b in zip(S['hull_bottom'], hb):
        sub.append(dict(x=a['x'], source_bottom_y=a['bottom_y'], v5_bottom_y=b['bottom_y'], delta=None if a['bottom_y'] is None or b['bottom_y'] is None else round(b['bottom_y'] - a['bottom_y'], 4)))
    R['hull_bottom'] = dict(stations=sub, max_abs_delta=max(abs(s_['delta']) for s_ in sub if s_['delta'] is not None), note='warp is horizontal: keel depth/submersion essentially unchanged')
    # ---------------- stern curl comparison
    old = S['v5_extra']['stern_curl_components']; nc = roblox_bbox(bpy.data.objects['ShipV5_SternCurl']) if 'ShipV5_SternCurl' in bpy.data.objects else None
    R['stern_curl'] = dict(prop_sterncurl_components_source=old[:6], shipv5_sterncurl_bbox=nc, build=BL.get('stern_curl'))
    # ---------------- floaters (isolated components) - informational
    fl = floater_scan(); new_iso = [x for x in fl['isolated'] if x not in S['floaters']['isolated']]
    R['floaters'] = dict(source_isolated=len(S['floaters']['isolated']), v5_isolated=len(fl['isolated']), new_isolated=new_iso)
    if new_iso: WARN.append('isolated components not in source: %d (see floaters)' % len(new_iso))
    # ---------------- tris
    allm = {}; tot = 0
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.startswith('COL'): continue
        mn, mx_ = roblox_bbox(o); t = tris(o.data); tot += t
        allm[o.name] = dict(collection=[c.name for c in o.users_collection][0], tris=t, materials=[m.name for m in o.data.materials], origin_roblox=list(np.round(Binv(o.location), 3)),
                            bbox_min_roblox=mn, bbox_max_roblox=mx_, under_20k=t < 20000, status='NEW' if o.name in new_objs else ms.get(o.name, {}).get('category', '?') + ('_changed' if ms.get(o.name, {}).get('changed_vs_source') else '_unchanged'),
                            tris_source=S['objects'].get(o.name, {}).get('tris'))
    R['tris'] = dict(per_mesh={k: v['tris'] for k, v in allm.items()}, total_visual=tot, total_source_visual=sum(v['tris'] for v in S['objects'].values()),
                     new_shipv5_tris=sum(v['tris'] for k, v in allm.items() if k.startswith('ShipV5_')), collision_tris=sum(tris(o.data) for o in cols.values()),
                     max_mesh=max(allm, key=lambda k: allm[k]['tris']), all_under_20k=all(v['under_20k'] for v in allm.values()))
    if not R['tris']['all_under_20k']: FAIL.append('mesh over 20k')
    if tot > 40000: WARN.append('total visual tris %d above ~40k near-field target (source %d)' % (tot, R['tris']['total_source_visual']))
    R['images'] = {i.name: dict(packed=i.packed_file is not None, size=list(i.size)) for i in bpy.data.images if i.type == 'IMAGE'}
    if not all(v['packed'] for v in R['images'].values()): FAIL.append('unpacked image')
    R['palette'] = BL.get('palette')
    R['not_checked'] = ['collision NOT verified against Studio v30 (no Studio in this job); Blender colliders are stale v3_2', 'no runtime/playtest validation',
                        'props are visual-only (no colliders); ball/player pass through them', 'watertightness of the warped Hull not re-proved (topology unchanged, vertices moved only)']
    R['fail'] = FAIL; R['warn'] = WARN; R['flags_for_builder'] = FLAG; R['pass_hard_checks'] = not FAIL
    json.dump(R, open(os.path.join(out_dir, 'fitcheck.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    json.dump(dict(allm=allm), open(os.path.join(out_dir, 'logs', 'mesh_stats.json'), 'w'), indent=1)
    print('FITCHECK_DONE pass_hard=', not FAIL, 'FAIL', FAIL, 'WARN', WARN, 'FLAG', FLAG)
