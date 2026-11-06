# check() for v3_2, exec'd inside fitcheck_v32.py (shares its helpers: mesh_arrays, sha, mw_list, probes, CORR, f2_dist, ...).
# blender -b --factory-startup out/start_ship_v3_2.blend --python fitcheck_v32.py -- check <v3_1_dump.json> <out_dir> <source_v3_1.blend> <repair_log.json>
# Adapted from fitcheck_v31_check.py: baseline is source_v3_1; ONLY PERMITTED meshes may differ (geometry/UV/material assignment);
# every other mesh, all 190 colliders (incl. the already-shortened COL_Mast_Main), anchors, names, origins must be exact v3_1.
# Corridor, probes, hull submersion and the coplanarity test (same 14 objects, same 0.03 / 0.995 / 0.02 tolerances) are unchanged.
PERMITTED = ['Prop_BowRaise', 'Prop_CapRails', 'Prop_SternCastle']
COPL_OBJECTS = ['Prop_Barnacles', 'Prop_BowRaise', 'Prop_BulwarkGear', 'Prop_Cannons', 'Prop_CapRails', 'Prop_Figurehead', 'Prop_RoofTrim', 'Prop_Seaweed',
                'Prop_SheerWale', 'Prop_SternCastle', 'Prop_SternWheel', 'Prop_Stovepipe', 'Prop_TreasureChest', 'Rigging']   # = v3_1 fitcheck objects_checked
LOCKED = ['DeckCabin', 'RampFlight1', 'RampLanding', 'RampFlight2']
MUST_UNCHANGED = ['Hull', 'Pier', 'RockBumper', 'Dressing', 'Dressing_Glow']

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

def check(dump_path, out_dir, src_path, build_log_path):
    S = json.load(open(dump_path)); BL = json.load(open(build_log_path)); FAIL = []; WARN = []
    R = dict(source=src_path, source_dump_blend=S['blend'], v3_2_blend=bpy.data.filepath, blender=bpy.app.version_string, permitted_to_change=PERMITTED)
    changed_by_build = list(PERMITTED)
    # ---------------- anchors
    an = {}
    for n in EMPTIES:
        o = bpy.data.objects.get(n); s = S['empties'][n]
        if o is None: an[n] = dict(present=False); FAIL.append('anchor missing ' + n); continue
        cur = dict(loc=list(o.location), rot=list(o.rotation_euler), scale=list(o.scale), mw=mw_list(o), parent=o.parent.name if o.parent else None)
        eq = all(cur[k] == s[k] for k in ('loc', 'rot', 'scale', 'mw', 'parent'))
        an[n] = dict(exact_equal=eq, loc_blender=cur['loc'], roblox=list(np.round(Binv(o.location), 4)), max_abs_diff=float(np.max(np.abs(np.array(cur['mw']) - np.array(s['mw'])))))
        if not eq: FAIL.append('anchor changed ' + n)
    R['anchors'] = an
    emp_src = set(S['empties']); emp_cur = set(o.name for o in bpy.data.objects if o.type == 'EMPTY')
    R['empties_all'] = dict(source=sorted(emp_src), v3_2=sorted(emp_cur), identical_set=emp_src == emp_cur,
                            all_matrix_identical=all(bpy.data.objects.get(n) is not None and mw_list(bpy.data.objects[n]) == S['empties'][n]['mw'] for n in emp_src))
    # ---------------- collision
    cols = {o.name: o for o in bpy.data.collections['Collision'].objects}
    names_eq = sorted(cols) == sorted(S['collision']); cres = dict(count_source=len(S['collision']), count_v3_2=len(cols), names_identical=names_eq)
    byte_eq = 0; diff = []; mx = 0.0
    for n, s in S['collision'].items():
        o = cols.get(n)
        if o is None: diff.append(n + ' (missing)'); continue
        co, lv, ps, mi, uv = mesh_arrays(o.data); W = np.array([o.matrix_world @ v.co for v in o.data.vertices], dtype=np.float64)
        same = (sha(co) == s['co_sha'] and sha(lv) == s['loops_sha'] and sha(ps) == s['polys_sha'] and sha(mi) == s['mi_sha'] and sha(uv) == s['uv_sha']
                and mw_list(o) == s['mw'] and sha(W) == s['world_sha'] and [m.name for m in o.data.materials] == s['mats'])
        byte_eq += int(same)
        if W.shape == np.array(s['world_verts']).shape: mx = max(mx, float(np.max(np.abs(W - np.array(s['world_verts'])))))
        if not same: diff.append(n)
    cres.update(all_190_byte_identical=byte_eq, max_abs_world_vertex_diff=mx, differing=diff,
                collection_membership_identical=sorted(cols) == S['collections']['Collision'])
    if not (names_eq and len(S['collision']) == 190 and byte_eq == 190 and not diff and mx == 0.0): FAIL.append('collision: 190 not all exact v3_1 ' + str(diff))
    # COL_Mast_Main: already shortened in v3_1 (axis 157 -> 98.3). v3_2 must keep it EXACTLY as v3_1; re-measure its along-axis height.
    s = S['collision']['COL_Mast_Main']; o = cols['COL_Mast_Main']
    W0 = np.array(s['world_verts']); W1 = np.array([o.matrix_world @ v.co for v in o.data.vertices], dtype=np.float64)
    L1 = np.array([tuple(v.co) for v in o.data.vertices]); co, lv, ps, mi, uv = mesh_arrays(o.data)
    order = np.argsort(W1[:, 2]); bot = sorted(order[:4].tolist()); top = sorted(order[4:].tolist())
    ax = L1[top].mean(0) - L1[bot].mean(0); h = float(np.linalg.norm(ax)); ax = ax / h
    wdir = np.array(o.matrix_world.to_3x3() @ Vector(ax)); wdir = wdir / np.linalg.norm(wdir)
    mast = dict(exact_vs_v3_1=('COL_Mast_Main' not in diff), world_verts_max_abs_diff_vs_v3_1=float(np.max(np.abs(W0 - W1))),
                origin_matrix_identical=mw_list(o) == s['mw'], co_sha_identical=sha(co) == s['co_sha'], topology_identical=(sha(lv) == s['loops_sha'] and sha(ps) == s['polys_sha']),
                uv_identical=sha(uv) == s['uv_sha'], materials_identical=[m.name for m in o.data.materials] == s['mats'],
                height_along_axis_v3_2=round(h, 4), axis_tilt_from_vertical_deg=round(math.degrees(math.acos(min(1, abs(wdir[2])))), 3),
                bottom_centre_roblox=list(np.round(Binv(W1[bot].mean(0)), 4)), top_centre_roblox=list(np.round(Binv(W1[top].mean(0)), 4)),
                history='shortened in v3_1 from 157.0 to 98.3 studs along its axis (bottom fixed); source_v3_1 unchanged; not touched in v3_2')
    mast['pass'] = bool(mast['exact_vs_v3_1'] and mast['world_verts_max_abs_diff_vs_v3_1'] == 0.0 and abs(h - 98.3) < 1e-3)
    if not mast['pass']: FAIL.append('COL_Mast_Main not exact v3_1 (98.3 along axis)')
    cres['COL_Mast_Main'] = mast; R['collision'] = cres
    # ---------------- every source mesh object: present, name, origin, datablock; geometry per category
    ms = {}
    for n, s in S['objects'].items():
        o = bpy.data.objects.get(n)
        if o is None or o.type != 'MESH': ms[n] = dict(present=False); FAIL.append('source mesh missing ' + n); continue
        co, lv, ps, mi, uv = mesh_arrays(o.data)
        e = dict(present=True, geometry_identical=(sha(co) == s['co_sha'] and sha(lv) == s['loops_sha'] and sha(ps) == s['polys_sha']),
                 material_assignment_identical=(sha(mi) == s['mi_sha'] and [m.name for m in o.data.materials] == s['mats']), uv_identical=sha(uv) == s['uv_sha'],
                 origin_matrix_identical=mw_list(o) == s['mw'], mesh_datablock_name_identical=o.data.name == s['mesh_name'],
                 collections_identical=[c.name for c in o.users_collection] == s['coll'], tris_v3_1=s['tris'], tris_v3_2=tris(o.data))
        e['category'] = 'LOCKED' if n in LOCKED else 'must_unchanged' if n in MUST_UNCHANGED else 'permitted_repair' if n in PERMITTED else 'must_unchanged_v3_1'
        if n in LOCKED:
            e['dimensions_v3_2'] = list(np.round(o.dimensions, 4))
            if 'world_verts' in s:
                W = np.array([o.matrix_world @ v.co for v in o.data.vertices], dtype=np.float64); e['world_verts_max_abs_diff'] = float(np.max(np.abs(W - np.array(s['world_verts']))))
        all_same = e['geometry_identical'] and e['material_assignment_identical'] and e['uv_identical']
        e['changed_vs_v3_1'] = not all_same
        if not (e['origin_matrix_identical'] and e['mesh_datablock_name_identical'] and e['collections_identical']): FAIL.append('origin/datablock/collection changed ' + n)
        if n not in PERMITTED and not all_same: FAIL.append(e['category'] + ' mesh changed vs v3_1 ' + n)
        if n in PERMITTED and [m.name for m in o.data.materials] != s['mats']: FAIL.append('material slots changed ' + n)
        ms[n] = e
    R['meshes_vs_source'] = ms
    new_objs = sorted(o.name for o in bpy.data.objects if o.type == 'MESH' and o.name not in S['objects'] and o.name not in S['collision'])
    R['new_objects'] = new_objs
    if new_objs: FAIL.append('new mesh objects vs v3_1 ' + str(new_objs))
    R['changed_meshes_vs_v3_1'] = sorted(n for n, e in ms.items() if e.get('changed_vs_v3_1'))
    R['repair_log_changed'] = BL.get('changed_meshes')
    # floating parts: isolated-component scan (same method as the v3_1 dump) must equal v3_1
    fl = floater_scan(); R['floaters'] = dict(v3_1=S['floaters'], v3_2=fl, identical_isolated=fl['isolated'] == S['floaters']['isolated'])
    if not R['floaters']['identical_isolated']: FAIL.append('isolated (floating) components differ from v3_1')
    # ---------------- hull: identical + submersion
    bm = world_bm(bpy.data.objects['Hull'])
    cur = set(tuple(sorted(tuple(round(c, 4) for c in v.co) for v in f.verts)) for f in bm.faces); bm.free()
    src = [tuple(map(tuple, t)) for t in S['hull_tris']]; missing = [t for t in src if t not in cur]
    R['hull_retained'] = dict(source_faces=len(src), v3_2_faces=len(cur), missing=len(missing), hull_geometry_identical=ms['Hull'].get('geometry_identical'))
    hb = hull_bottom_profile(); sub = []
    for a, b in zip(S['hull_bottom'], hb):
        sub.append(dict(x=a['x'], v3_1_bottom_y=a['bottom_y'], v3_2_bottom_y=b['bottom_y'], identical=a['bottom_y'] == b['bottom_y'],
                        submerged_below_water_studs=None if b['bottom_y'] is None else round(WATER_Y - b['bottom_y'], 3)))
    R['hull_submersion'] = dict(water_level_local=WATER_Y, all_identical=all(x['identical'] for x in sub), stations=sub)
    if not R['hull_submersion']['all_identical']: FAIL.append('hull bottom/skirt profile changed')
    # ---------------- walk surfaces / probes
    R['walk_surfaces'] = dict(v3_1=S['walk'], v3_2=deck_walk_surfaces()); R['walk_surfaces']['identical'] = R['walk_surfaces']['v3_1'] == R['walk_surfaces']['v3_2']
    if not R['walk_surfaces']['identical']: FAIL.append('walk surfaces changed')
    pv = probes(scene_trees()); ps_ = S['probes']
    R['spawn_headroom'] = dict(v3_1=ps_['spawn_headroom'], v3_2=pv['spawn_headroom'], identical=ps_['spawn_headroom'] == pv['spawn_headroom'])
    if not R['spawn_headroom']['identical']: WARN.append('spawn headroom first hit differs (see spawn_headroom)')
    door_same = all((a['hit'] is None) == (b['hit'] is None) and (a['hit'] is None or a['hit'][0] == b['hit'][0]) for a, b in zip(ps_['door_rays'], pv['door_rays']))
    R['door_clearance'] = dict(rays=len(pv['door_rays']), rays_blocked_v3_1=sum(r['hit'] is not None for r in ps_['door_rays']), rays_blocked_v3_2=sum(r['hit'] is not None for r in pv['door_rays']),
                               identical=door_same, blocked_v3_2=[r for r in pv['door_rays'] if r['hit'] is not None][:10])
    if not door_same: FAIL.append('door clearance rays changed')
    R['tee_sightlines'] = dict(eye_roblox=pv['tee_eye'], v3_1=ps_['tee_sightlines'], v3_2=pv['tee_sightlines'],
                               identical=all(ps_['tee_sightlines'][k]['first_hit'] == pv['tee_sightlines'][k]['first_hit'] for k in pv['tee_sightlines']))
    if not R['tee_sightlines']['identical']: WARN.append('tee sightline first hits differ (see tee_sightlines)')
    # ---------------- route corridor: vertices + face centres (distance) AND actual triangle intersection (BVH overlap)
    F2 = Binv(bpy.data.objects['RampFlight2'].matrix_world.translation); CUP = Binv(bpy.data.objects['CupRef'].matrix_world.translation)
    props = [o for o in bpy.data.collections['Props'].objects if o.type == 'MESH']
    groups = [(o.name, o) for o in props] + [('Rigging', bpy.data.objects['Rigging'])]
    for n in PERMITTED:
        if n not in [g[0] for g in groups]: groups.append((n, bpy.data.objects[n]))
    ZT = {k: _box_tree(lo, hi) for k, (lo, hi) in CORR.items()}
    ZT['flight2_apron_yawed'] = _f2_tree(F2, True); ZT['flight2_apron_unyawed'] = _f2_tree(F2, False); ZT['cup_clear_r12'] = _cyl_tree(CUP, 12.0)
    corr = {k: dict(min_dist=1e9, closest=None) for k in ZT}; per_obj = {}; tri_hits = {}
    for n, o in groups:
        P = sample_points(o); dd = {}
        for k, (lo, hi) in CORR.items(): dd[k] = float(aabb_dist(P, lo, hi).min())
        dd['flight2_apron_yawed'] = float(f2_dist(P, F2, True).min()); dd['flight2_apron_unyawed'] = float(f2_dist(P, F2, False).min())
        dd['cup_clear_r12'] = float(max(0.0, (np.sqrt((P[:, 0] - CUP[0]) ** 2 + (P[:, 2] - CUP[2]) ** 2) - 12.0).min()))
        per_obj[n] = {k: round(v, 3) for k, v in dd.items()}
        bm = world_bm(o); T = BVHTree.FromBMesh(bm); bm.free()
        for k, Z in ZT.items():
            ov = T.overlap(Z)
            if ov: tri_hits.setdefault(n, {})[k] = len(ov)
        for k, v in dd.items():
            if v < corr[k]['min_dist']: corr[k] = dict(min_dist=round(v, 3), closest=n)
    gk = min(corr, key=lambda k: corr[k]['min_dist'])
    edited = set(PERMITTED)
    per_obj_changed = {k: v for k, v in per_obj.items() if k in edited}
    ck = {z: min(((v[z], n) for n, v in per_obj_changed.items()), default=(None, None)) for z in ZT}
    R['route_corridor'] = dict(boxes_roblox=CORR, flight2_box='flight2 local frame: along -1..72, lateral +-9, height -13..+7 (yawed -30 deg as built in Studio, and unyawed as exported)',
                               cup='12-stud clear radius around CupRef (triangle test uses a circumscribed 64-gon prism, Roblox Y -60..400)',
                               per_zone_all_props=corr, per_zone_repaired_only={z: dict(min_dist=v[0], closest=v[1]) for z, v in ck.items()},
                               per_object=per_obj, min_clearance=dict(studs=corr[gk]['min_dist'], zone=gk, object=corr[gk]['closest']),
                               any_vertex_or_centre_inside=any(v['min_dist'] <= 0 for v in corr.values()),
                               triangle_intersections=tri_hits, any_triangle_intersection=bool(tri_hits),
                               method='(a) min distance from every vertex and face centre of every Props mesh + Rigging + new meshes to each zone volume (Roblox coords); (b) BVH overlap of the actual mesh triangles against the zone boundary surfaces. (a)+(b) together catch triangles fully inside or crossing a zone.')
    if R['route_corridor']['any_vertex_or_centre_inside'] or tri_hits: FAIL.append('route corridor intrusion ' + json.dumps(tri_hits))
    # ---------------- coplanarity (changed + new objects vs every other visual mesh)
    trees = scene_trees(); copl = []; checked = 0
    assert set(PERMITTED) <= set(COPL_OBJECTS)
    for n in COPL_OBJECTS:
        o = bpy.data.objects.get(n)
        if o is None or o.type != 'MESH' or n.startswith('COL'): continue
        bm = world_bm(o)
        for f in bm.faces:
            c = f.calc_center_median(); n0 = f.normal; checked += 1
            for nme, (T, bm2) in trees.items():
                if nme == o.name: continue
                loc, nor, idx, dist = T.find_nearest(c, 0.03)
                if loc is not None and abs(nor.dot(n0)) > 0.995 and abs((c - loc).dot(nor)) < 0.02:
                    copl.append(dict(obj=o.name, other=nme, at=list(np.round(Binv(c), 2)), dist=round(dist, 4)))
        bm.free()
    R['coplanarity'] = dict(objects_checked=COPL_OBJECTS, v3_1_detections=4, faces_checked=checked, coplanar_pairs=len(copl), examples=copl[:20],
                            method='(unchanged from v3_1) each changed/new face centre: nearest surface of every other visual mesh within 0.03 with parallel normal (|dot|>0.995) and plane gap <0.02')
    if copl: FAIL.append('coplanar faces %d' % len(copl))
    # ---------------- tris
    allm = {}; tot = 0
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.startswith('COL'): continue
        mn, mx_ = roblox_bbox(o); t = tris(o.data); tot += t
        allm[o.name] = dict(collection=[c.name for c in o.users_collection][0], tris=t, materials=[m.name for m in o.data.materials],
                            origin_roblox=list(np.round(Binv(o.location), 3)), bbox_min_roblox=mn, bbox_max_roblox=mx_, under_20k=t < 20000,
                            status='repaired_v3_2' if ms.get(o.name, {}).get('changed_vs_v3_1') else 'unchanged_vs_v3_1')
    col_tris = sum(tris(o.data) for o in cols.values())
    R['tris'] = dict(per_mesh={k: v['tris'] for k, v in allm.items()}, total_visual=tot, total_v3_1_visual=sum(v['tris'] for v in S['objects'].values()),
                     collision_tris=col_tris, max_mesh=max(allm, key=lambda k: allm[k]['tris']), all_under_20k=all(v['under_20k'] for v in allm.values()),
                     target_note='brief target ~40k near-field; total_visual counts everything incl. pier/rocks/rigging')
    if not R['tris']['all_under_20k']: FAIL.append('mesh over 20k')
    if tot > 40000: WARN.append('total visual tris %d above ~40k target' % tot)
    # ---------------- images packed
    R['images'] = {i.name: dict(packed=i.packed_file is not None, size=list(i.size), filepath=i.filepath) for i in bpy.data.images if i.type == 'IMAGE'}
    if not all(v['packed'] for v in R['images'].values()): FAIL.append('unpacked image')
    R['not_checked'] = ['no runtime/Studio validation (no Studio in this job)', 'gaps/embeds of the repaired geometry are measured in repair_log.json, not here','proud relief >0.08 and plate thickness >=0.2 are build-script parameters (see build_log notes), not re-measured here',
                        'watertightness: Hull geometry is byte-identical to source, so no new cutout; new props are not required to be closed',
                        'deck props (wheel, chest, cargo, crab, rope coils, gear) have no collider; ball/player pass through']
    R['fail'] = FAIL; R['warn'] = WARN; R['pass_hard_checks'] = not FAIL
    json.dump(R, open(os.path.join(out_dir, 'fitcheck.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    json.dump(dict(allm=allm), open(os.path.join(out_dir, 'logs', 'mesh_stats.json'), 'w'), indent=1)
    print('FITCHECK_DONE pass_hard=', not FAIL, 'FAIL', FAIL, 'WARN', WARN)
