# verify.py - measured verification for the start_ship_b2_detail_v3 mast-collider fix. All modes run inside Blender 5.2 headless:
#  dump : blender -b --factory-startup <blend> --python-exit-code 1 --python verify.py -- dump <json>      fingerprint every datablock
#  fbx  : blender -b --factory-startup --python-exit-code 1 --python verify.py -- fbx <fbx_dir> <json>     re-import each FBX: names/origins/tris
#  check: blender -b --factory-startup --python-exit-code 1 --python verify.py -- check <src.json> <donor.json> <fix.json> <fbx.json> <out_dir> <steps.txt>
#         compares and writes out_dir/fitcheck.json, fitcheck.md, manifest.json, README.md, report.txt; exits 1 on any failed hard check.
import bpy, sys, os, json, hashlib, math, platform
import numpy as np
A = sys.argv[sys.argv.index('--') + 1:]; MODE = A[0]
MAST = 'COL_Mast_Main'; EMPTIES = ['Spawn', 'Tee1', 'RampStart', 'CupRef']; BOTTOM = (0, 2, 4, 6); TOP = (1, 3, 5, 7)
SOURCE_SHA256 = '87b319a5b6308c1d7d3deaac91b4b4e16b651572ac569a14606a8446442cc92f'
PLACE_Y = 0.6   # Roblox placement (unchanged): worldY = localY + 0.6


def H(b): return hashlib.sha256(b).hexdigest()
def sha_np(a): return H(np.ascontiguousarray(a).tobytes())
def R(v): return [float(v[0]), float(v[2]), -float(v[1])]       # Blender (x,y,z) -> Roblox local (x, z, -y)
def RW(v): r = R(v); return [r[0], r[1] + PLACE_Y, r[2]]
def mat(m): return [[float(x) for x in r] for r in m]


COMP = {'FLOAT_VECTOR': ('vector', 3, np.float32), 'FLOAT2': ('vector', 2, np.float32), 'FLOAT': ('value', 1, np.float32), 'INT': ('value', 1, np.int32),
        'INT32_2D': ('value', 2, np.int32), 'BOOLEAN': ('value', 1, bool), 'FLOAT_COLOR': ('color', 4, np.float32), 'BYTE_COLOR': ('color', 4, np.float32),
        'QUATERNION': ('value', 4, np.float32), 'FLOAT4X4': ('value', 16, np.float32)}


def attr_sha(a):
    n = len(a.data)
    try:
        k, c, t = COMP[a.data_type]; arr = np.zeros(n * c, t); a.data.foreach_get(k, arr); return sha_np(arr)
    except Exception:
        key = next((k for k in ('value', 'vector', 'color') if n and hasattr(a.data[0], k)), 'value')
        return H(repr([tuple(getattr(d, key)) if hasattr(getattr(d, key), '__len__') else getattr(d, key) for d in a.data]).encode())


def obj_fp(o):
    e = dict(type=o.type, data=o.data.name if o.data else None, parent=o.parent.name if o.parent else None, collections=sorted(c.name for c in o.users_collection),
             matrix_world=mat(o.matrix_world), matrix_basis=mat(o.matrix_basis), matrix_parent_inverse=mat(o.matrix_parent_inverse), rotation_mode=o.rotation_mode,
             modifiers=[m.type for m in o.modifiers], hide_render=o.hide_render, hide_viewport=o.hide_viewport, props=sorted(o.keys()),
             material_slots=[[s.material.name if s.material else None, s.link] for s in o.material_slots])
    if o.type == 'EMPTY': e.update(empty_display_type=o.empty_display_type, empty_display_size=o.empty_display_size)
    if o.type == 'MESH':
        me = o.data
        e.update(verts=len(me.vertices), polys=len(me.polygons), tris=int(sum(len(p.vertices) - 2 for p in me.polygons)), mesh_users=me.users,
                 mesh_materials=[m.name if m else None for m in me.materials], uv_layers=[u.name for u in me.uv_layers],
                 attributes={'%s|%s|%s' % (a.name, a.domain, a.data_type): attr_sha(a) for a in me.attributes})
        ps = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('loop_start', ps); e['poly_offsets'] = sha_np(ps)
        co = np.array([tuple(o.matrix_world @ v.co) for v in me.vertices], np.float64); e['world_vert_sha'] = sha_np(co.astype(np.float32))
        rb = np.column_stack([co[:, 0], co[:, 2], -co[:, 1]]); e['bbox_roblox'] = [rb.min(0).tolist(), rb.max(0).tolist()]
        if o.name == MAST:
            e['local_co'] = [list(v.co) for v in me.vertices]; e['world_co'] = co.tolist(); e['poly_verts'] = [list(p.vertices) for p in me.polygons]
    return e


def node_fp(m):
    if not (m.use_nodes and m.node_tree): return None
    out = []
    for n in m.node_tree.nodes:
        ins = []
        for i in n.inputs:
            dv = getattr(i, 'default_value', None)
            ins.append((i.identifier, repr(tuple(dv)) if hasattr(dv, '__len__') else repr(dv)))
        out.append((n.name, n.type, n.image.name if getattr(n, 'image', None) else None, ins))
    links = sorted((l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier) for l in m.node_tree.links)
    return H(repr((out, links)).encode())


def dump(path):
    D = dict(file=bpy.data.filepath, file_sha256=H(open(bpy.data.filepath, 'rb').read()), blender=bpy.app.version_string, build_hash=bpy.app.build_hash.decode(),
             unit_scale=bpy.context.scene.unit_settings.scale_length, collections={c.name: sorted(o.name for o in c.objects) for c in bpy.data.collections},
             objects={o.name: obj_fp(o) for o in bpy.data.objects},
             materials={m.name: dict(diffuse=list(m.diffuse_color), nodes=node_fp(m), props=sorted(m.keys())) for m in bpy.data.materials},
             images={i.name: dict(size=list(i.size), packed=bool(i.packed_file), packed_sha=H(i.packed_file.data) if i.packed_file else None, filepath=i.filepath) for i in bpy.data.images},
             counts={k: len(getattr(bpy.data, k)) for k in ('objects', 'meshes', 'materials', 'images', 'collections', 'textures', 'node_groups', 'cameras', 'lights', 'worlds', 'scenes')})
    json.dump(D, open(path, 'w'), indent=0); print('DUMP_OK', path, len(D['objects']))


def fbx(d, path):
    res = {}
    for f in sorted(os.listdir(d)):
        if not f.endswith('.fbx'): continue
        bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=os.path.join(d, f)); objs = {}
        for o in bpy.data.objects:
            e = dict(type=o.type, loc=[float(v) for v in o.matrix_world.translation], scale=[float(v) for v in o.matrix_world.to_scale()])
            if o.type == 'MESH':
                e.update(tris=int(sum(len(p.vertices) - 2 for p in o.data.polygons)), mats=[m.name for m in o.data.materials if m])
                if o.name == MAST: e['world_co'] = [list(o.matrix_world @ v.co) for v in o.data.vertices]
            objs[o.name] = e
        res[f] = dict(size_bytes=os.path.getsize(os.path.join(d, f)), objects=objs, images=[[i.name, list(i.size), bool(i.packed_file)] for i in bpy.data.images])
    json.dump(res, open(path, 'w'), indent=0); print('FBX_OK', {k: len(v['objects']) for k, v in res.items()})


def mast_geo(w):
    ax = w[1] - w[0]; L = float(np.linalg.norm(ax)); u = ax / L
    bot = w[list(BOTTOM)].mean(0); top = w[list(TOP)].mean(0)
    e1b, e2b = w[2] - w[0], w[4] - w[0]; e1t, e2t = w[3] - w[1], w[5] - w[1]
    rb = np.array([R(v) for v in w])
    return dict(length_along_axis=L, axis_dir_blender=u.tolist(), axis_tilt_from_vertical_deg=math.degrees(math.acos(abs(u[2]))),
                cross_bottom=[e1b.tolist(), e2b.tolist()], cross_top=[e1t.tolist(), e2t.tolist()], cross_section=[float(np.linalg.norm(e1b)), float(np.linalg.norm(e2b))],
                bottom_center_roblox_local=R(bot), top_center_roblox_local=R(top), top_center_roblox_world=RW(top),
                top_verts_roblox_local=[R(w[i]) for i in TOP], bottom_verts_roblox_local=[R(w[i]) for i in BOTTOM],
                bbox_roblox_local=[rb.min(0).tolist(), rb.max(0).tolist()],
                highest_roblox_local_y=float(w[:, 2].max()), highest_roblox_world_y=float(w[:, 2].max()) + PLACE_Y)


def check(src_p, don_p, fix_p, fbx_p, O, steps_p):
    S, Dn, F, X = (json.load(open(p)) for p in (src_p, don_p, fix_p, fbx_p)); fails = []
    def req(c, msg):
        if not c: fails.append(msg)
    so, fo = S['objects'], F['objects']
    req(S['file_sha256'] == SOURCE_SHA256, 'source sha mismatch')
    req(sorted(so) == sorted(fo), 'object name set differs')
    vis = sorted(n for n, v in so.items() if v['type'] == 'MESH' and not n.startswith('COL'))
    cols = sorted(n for n, v in so.items() if v['type'] == 'MESH' and n.startswith('COL'))
    vis_res = {n: so[n] == fo.get(n) for n in vis}
    req(len(vis) == 28 and all(vis_res.values()), 'visual/ramp/prop meshes not byte-identical: %s' % [n for n, ok in vis_res.items() if not ok])
    vis_tris = sum(fo[n]['tris'] for n in vis); big = max(vis, key=lambda n: fo[n]['tris'])
    req(vis_tris == 49405 and fo[big]['tris'] == 7282, 'visual tris %d / largest %s %d' % (vis_tris, big, fo[big]['tris']))
    req(len(cols) == 190 and MAST in cols and sorted(n for n in fo if n.startswith('COL')) == cols, 'collider names differ')
    col_res = {n: so[n] == fo[n] for n in cols if n != MAST}
    req(len(col_res) == 189 and all(col_res.values()), 'colliders changed: %s' % [n for n, ok in col_res.items() if not ok])
    an = {}
    for n in EMPTIES:
        loc = [r[3] for r in fo[n]['matrix_world'][:3]]
        an[n] = dict(exact=so[n] == fo[n], blender_loc=loc, roblox_local=R(loc), roblox_world=RW(loc))
        req(an[n]['exact'], 'anchor %s changed' % n)
    others = {k: S[k] == F[k] for k in ('materials', 'images', 'collections', 'unit_scale')}
    cnt = {k: [S['counts'][k], F['counts'][k]] for k in S['counts']}
    req(all(others.values()) and all(a == b for a, b in cnt.values()), 'materials/images/collections/counts differ: %s %s' % (others, cnt))
    req(all(v['packed'] for v in F['images'].values()), 'image not packed')
    # ---- mast
    ms, mf, md = so[MAST], fo[MAST], Dn['objects'][MAST]
    GEOM = ('attributes', 'world_vert_sha', 'bbox_roblox', 'local_co', 'world_co')
    nonpos = lambda e: {k: v for k, v in e.items() if k not in GEOM}
    req(nonpos(ms) == nonpos(mf), 'mast non-geometry fields changed (name/datablock/matrix/material/collections/topology)')
    np_attr = lambda e: {k: v for k, v in e['attributes'].items() if not k.startswith('position|')}
    req(np_attr(ms) == np_attr(mf), 'mast non-position attributes changed')
    req(mf['matrix_world'] == ms['matrix_world'] == md['matrix_world'], 'mast origin matrix differs from source/donor')
    req(mf['local_co'] == md['local_co'], 'mast vertices != donor vertices')
    req(mf['poly_verts'] == ms['poly_verts'] == md['poly_verts'], 'mast topology differs')
    req(all(mf['local_co'][i] == ms['local_co'][i] for i in BOTTOM), 'mast bottom vertices changed')
    w0, w1 = np.array(ms['world_co']), np.array(mf['world_co'])
    g0, g1 = mast_geo(w0), mast_geo(w1)
    req(abs(g0['length_along_axis'] - 157.0) < 0.05 and abs(g1['length_along_axis'] - 98.3) < 0.05, 'mast length %.4f -> %.4f' % (g0['length_along_axis'], g1['length_along_axis']))
    req(np.allclose(g0['axis_dir_blender'], g1['axis_dir_blender'], atol=1e-5) and abs(g1['axis_tilt_from_vertical_deg'] - 18) < 0.05, 'mast axis changed')
    req(np.allclose(g1['cross_top'], g1['cross_bottom'], atol=1e-4) and g1['cross_bottom'] == g0['cross_bottom'], 'cross-section changed')
    vd = [dict(index=i, part='bottom' if i in BOTTOM else 'top', old_blender=w0[i].tolist(), new_blender=w1[i].tolist(), old_roblox_local=R(w0[i]), new_roblox_local=R(w1[i]),
               delta_roblox=(np.array(R(w1[i])) - np.array(R(w0[i]))).tolist(), moved=float(np.linalg.norm(w1[i] - w0[i]))) for i in range(8)]
    req(all(abs(d['moved'] - (g0['length_along_axis'] - g1['length_along_axis'])) < 1e-3 for d in vd if d['part'] == 'top'), 'top verts did not all move by the length delta')
    # ---- FBX re-import
    fx = {}
    def near(a, b, t=1e-3): return all(abs(x - y) <= t for x, y in zip(a, b))
    def org(n): return [r[3] for r in fo[n]['matrix_world'][:3]]
    vexp = set(vis) | set(EMPTIES); vf = X.get('start_ship_b2_visual.fbx', {}).get('objects', {})
    fx['start_ship_b2_visual.fbx'] = dict(objects=len(vf), meshes=sum(v['type'] == 'MESH' for v in vf.values()), empties=sorted(n for n, v in vf.items() if v['type'] == 'EMPTY'),
        tris=sum(v.get('tris', 0) for v in vf.values()), names_ok=set(vf) == vexp, origins_ok=bool(vf) and all(n in vf and near(vf[n]['loc'], org(n)) for n in vexp),
        tris_ok=bool(vf) and all(n in vf and vf[n].get('tris') == fo[n]['tris'] for n in vis), images=X.get('start_ship_b2_visual.fbx', {}).get('images'))
    cf = X.get('start_ship_b2_col.fbx', {}).get('objects', {})
    fx['start_ship_b2_col.fbx'] = dict(objects=len(cf), tris=sum(v.get('tris', 0) for v in cf.values()), names_ok=set(cf) == set(cols),
        origins_ok=bool(cf) and all(n in cf and near(cf[n]['loc'], org(n)) for n in cols), tris_ok=bool(cf) and all(n in cf and cf[n].get('tris') == fo[n]['tris'] for n in cols),
        mast_world_verts_match_blend=MAST in cf and bool(np.allclose(cf[MAST]['world_co'], w1, atol=1e-3)),
        mast_max_world_vertex_diff=float(np.abs(np.array(cf[MAST]['world_co']) - w1).max()) if MAST in cf else None)
    for r in ('RampFlight1', 'RampLanding', 'RampFlight2'):
        rf = X.get(r + '_own_origin.fbx', {}).get('objects', {})
        fx[r + '_own_origin.fbx'] = dict(objects=len(rf), names_ok=set(rf) == {r}, origin=rf.get(r, {}).get('loc'), origins_ok=r in rf and near(rf[r]['loc'], [0, 0, 0], 1e-6),
                                         tris=rf.get(r, {}).get('tris'), tris_ok=rf.get(r, {}).get('tris') == fo[r]['tris'])
    for k, v in fx.items(): req(v['names_ok'] and v['origins_ok'] and v['tris_ok'], 'FBX %s re-import mismatch' % k)
    req(sorted(X) == sorted(fx), 'expected exactly the 5 FBX files, got %s' % sorted(X))
    req(fx['start_ship_b2_col.fbx']['mast_world_verts_match_blend'], 'col FBX COL_Mast_Main verts do not match the blend')
    req(any(i[2] for i in (fx['start_ship_b2_visual.fbx']['images'] or [])), 'visual FBX texture not embedded/packed on re-import')
    PASS = not fails
    tdelta = (np.array(g1['top_center_roblox_local']) - np.array(g0['top_center_roblox_local'])).tolist()
    fit = dict(name='start_ship_b2_detail_v3 mastfix', pass_hard_checks=PASS, failures=fails,
               source=dict(file=S['file'], sha256=S['file_sha256'], is_copy_of='start_ship_b2_detail_v3/out/start_ship_v3.blend (original v3 release)'),
               donor=dict(file=Dn['file'], sha256=Dn['file_sha256'], used_for='COL_Mast_Main vertex positions only (embedded in src/mastfix.py)'),
               output=dict(file=F['file'], sha256=F['file_sha256']), blender=F['blender'] + ' ' + F['build_hash'],
               visual_meshes=dict(count=len(vis), byte_identical=sum(vis_res.values()), tris_total=vis_tris, largest=big, largest_tris=fo[big]['tris'],
                                  per_mesh={n: dict(tris=fo[n]['tris'], identical=vis_res[n], collection=fo[n]['collections']) for n in vis}),
               colliders=dict(count=len(cols), names_identical=sorted(n for n in fo if n.startswith('COL')) == cols, other_byte_identical=sum(col_res.values()), other_count=len(col_res), changed=[MAST]),
               anchors=an, materials_images_collections_identical=others, datablock_counts=cnt,
               mast=dict(origin_matrix=mf['matrix_world'], origin_matrix_identical=mf['matrix_world'] == ms['matrix_world'] == md['matrix_world'], mesh_datablock=mf['data'], material=mf['mesh_materials'],
                         vertices_equal_donor=mf['local_co'] == md['local_co'], bottom_identical=all(mf['local_co'][i] == ms['local_co'][i] for i in BOTTOM),
                         non_position_attributes_identical=np_attr(ms) == np_attr(mf), old=g0, new=g1, length_delta=g1['length_along_axis'] - g0['length_along_axis'],
                         top_center_delta_roblox=tdelta, vertices=vd),
               fbx_reimport=fx, frame='Blender Z up; Roblox local (x,y,z) = (bx, bz, -by); placement unchanged: Roblox worldY = localY + 0.6', units='1 Blender unit = 1 stud')
    json.dump(fit, open(os.path.join(O, 'fitcheck.json'), 'w'), indent=1)
    f3 = lambda v: '(%.3f, %.3f, %.3f)' % tuple(v)
    org_m = f3([r[3] for r in mf['matrix_world'][:3]])
    md_ = ['# start_ship_b2_detail_v3 - COL_Mast_Main fix: fitcheck (measured)\n',
           'Source: ORIGINAL v3 release `start_ship_b2_detail_v3/out/start_ship_v3.blend` (local copy `original_v3.blend`, sha256 `%s`). Output `out/start_ship_v3_mastfix.blend` (sha256 `%s`). All values measured by `src/verify.py`.\n' % (S['file_sha256'], F['file_sha256']),
           '**Hard checks: %s**%s\n' % ('PASS' if PASS else 'FAIL', '' if PASS else ' - ' + '; '.join(fails)),
           '## Collision delta (the only change)',
           '- `COL_Mast_Main` (mesh datablock `%s`, material %s): 8 vertex positions replaced by the donor values (4 move, 4 stay). Origin matrix identical (identity rotation, translation %s Blender); faces, edges and all other attributes identical.' % (mf['data'], mf['mesh_materials'], org_m),
           '- Length along the 18 deg mast axis: **%.4f -> %.4f** (delta %.4f). Tilt from vertical %.3f deg (unchanged). Cross-section %.4f x %.4f (unchanged; top = bottom).' % (g0['length_along_axis'], g1['length_along_axis'], g1['length_along_axis'] - g0['length_along_axis'], g1['axis_tilt_from_vertical_deg'], g1['cross_section'][0], g1['cross_section'][1]),
           '- Bottom 4 vertices bit-identical to v3. Bottom centre Roblox local %s.' % f3(g1['bottom_center_roblox_local']),
           '- **Top centre Roblox local: old %s -> new %s** (delta %s); Roblox world (Y + 0.6): old %s -> new %s.' % (f3(g0['top_center_roblox_local']), f3(g1['top_center_roblox_local']), f3(tdelta), f3(g0['top_center_roblox_world']), f3(g1['top_center_roblox_world'])),
           '- Highest collider point Roblox Y: local %.3f -> %.3f (world %.3f -> %.3f).' % (g0['highest_roblox_local_y'], g1['highest_roblox_local_y'], g0['highest_roblox_world_y'], g1['highest_roblox_world_y']),
           '- Roblox local bbox: old %s .. %s -> new %s .. %s\n' % (f3(g0['bbox_roblox_local'][0]), f3(g0['bbox_roblox_local'][1]), f3(g1['bbox_roblox_local'][0]), f3(g1['bbox_roblox_local'][1])),
           '| vertex | part | old Roblox local | new Roblox local | moved (studs) |', '|---|---|---|---|---|']
    md_ += ['| %d | %s | %s | %s | %.4f |' % (d['index'], d['part'], f3(d['old_roblox_local']), f3(d['new_roblox_local']), d['moved']) for d in vd]
    md_ += ['\n## Unchanged (byte-identical: geometry, every mesh attribute incl. UVs and material indices, material slots, world transform, name, datablock, collection)',
            '- Visual + ramps + props meshes: **%d / %d** identical; %d tris total, largest %s %d.' % (sum(vis_res.values()), len(vis), vis_tris, big, fo[big]['tris']),
            '- Colliders: 190 names identical; the other **%d / %d** byte-identical.' % (sum(col_res.values()), len(col_res)),
            '- Materials (node trees), packed palette image, collections, unit scale identical: %s. Datablock counts identical: %s.' % (all(others.values()), all(a == b for a, b in cnt.values())),
            '\n## Anchors (exact)', '| empty | Roblox local | Roblox world (Y + 0.6) | exact |', '|---|---|---|---|']
    md_ += ['| %s | %s | %s | %s |' % (n, f3(v['roblox_local']), f3(v['roblox_world']), v['exact']) for n, v in an.items()]
    md_ += ['\n## FBX re-import (each file imported into an empty scene)', '| file | objects | tris | names | origins | tris match |', '|---|---|---|---|---|---|']
    md_ += ['| %s | %d | %s | %s | %s | %s |' % (k, v['objects'], v['tris'], v['names_ok'], v['origins_ok'], v['tris_ok']) for k, v in fx.items()]
    md_ += ['\n- col FBX `COL_Mast_Main` world vertices match the blend: %s (max diff %s).' % (fx['start_ship_b2_col.fbx']['mast_world_verts_match_blend'], fx['start_ship_b2_col.fbx']['mast_max_world_vertex_diff'])]
    open(os.path.join(O, 'fitcheck.md'), 'w', encoding='utf-8').write('\n'.join(md_) + '\n')
    fbxs = sorted(fx)
    man = dict(name='start_ship_b2_detail_v3_mastfix', based_on='ORIGINAL v3 release start_ship_b2_detail_v3/out/start_ship_v3.blend (NOT the refined ship)',
               source=dict(local_copy='original_v3.blend', sha256=S['file_sha256']), donor=dict(file='mast_donor_v3_2.blend', sha256=Dn['file_sha256'], used='COL_Mast_Main vertex positions only'),
               outputs=dict(blend='start_ship_v3_mastfix.blend', blend_sha256=F['file_sha256'], fbx=['fbx/' + f for f in fbxs],
                            fbx_sha256={f: H(open(os.path.join(O, 'fbx', f), 'rb').read()) for f in fbxs if os.path.exists(os.path.join(O, 'fbx', f))},
                            previews='none new - visuals are byte-identical to v3; use the existing v3 previews'),
               units='1 Blender unit = 1 stud', frame=fit['frame'], textures='start_ship_palette.png packed in the blend and embedded in the visual FBX (unchanged)',
               export=dict(axis_forward='-Z', axis_up='Y', global_scale=1.0, apply_scale_options='FBX_SCALE_UNITS', embed_textures=True, path_mode='COPY', mesh_smooth_type='FACE',
                           visual_fbx='28 meshes (Visual 7 + Ramps 3 + Props 18) + Spawn/Tee1/RampStart/CupRef empties', col_fbx='190 COL boxes',
                           ramps='RampFlight1/RampLanding/RampFlight2 on their own origin (location zeroed for export only)'),
               collections={k: len(v) for k, v in F['collections'].items()},
               meshes={n: dict(tris=fo[n]['tris'], collection=fo[n]['collections'][0], status='byte-identical to v3') for n in vis},
               tris=dict(total_visual=vis_tris, largest=big, largest_tris=fo[big]['tris']),
               anchors={n: dict(roblox_local=v['roblox_local'], roblox_world=v['roblox_world'], exact_equal_to_v3=v['exact']) for n, v in an.items()},
               changes=['COL_Mast_Main: 4 top vertices moved down the 18 deg mast axis; box length 157.0 -> 98.3; bottom, cross-section and origin unchanged. Nothing else changed.'],
               collision_delta=dict(collider=MAST, length_old=g0['length_along_axis'], length_new=g1['length_along_axis'],
                                    top_center_roblox_local_old=g0['top_center_roblox_local'], top_center_roblox_local_new=g1['top_center_roblox_local'],
                                    top_center_roblox_world_old=g0['top_center_roblox_world'], top_center_roblox_world_new=g1['top_center_roblox_world'],
                                    top_verts_roblox_local_old=g0['top_verts_roblox_local'], top_verts_roblox_local_new=g1['top_verts_roblox_local'],
                                    highest_roblox_world_y_old=g0['highest_roblox_world_y'], highest_roblox_world_y_new=g1['highest_roblox_world_y']),
               hard_checks_pass=PASS, fbx_reimport=fx)
    json.dump(man, open(os.path.join(O, 'manifest.json'), 'w'), indent=1)
    rd = ['# start_ship_b2_detail_v3 - mast collider fix', '',
          'Original v3 release ship (`start_ship_b2_detail_v3/out/start_ship_v3.blend`, sha256 `%s`) with ONE change: collider `COL_Mast_Main` shortened from 157.0 to 98.3 studs along its 18 deg axis (bottom fixed). All visuals, ramps, props, materials, textures, anchors and the other 189 colliders are byte-identical to v3, so the existing v3 previews still apply.' % S['file_sha256'], '',
          '## Files', '- `start_ship_v3_mastfix.blend`: full scene (Visual / Ramps / Props / Collision collections, palette packed).',
          '- `fbx/start_ship_b2_visual.fbx` (28 meshes + 4 anchor empties, %d tris), `fbx/start_ship_b2_col.fbx` (190 COL boxes), `fbx/RampFlight1_own_origin.fbx`, `fbx/RampLanding_own_origin.fbx`, `fbx/RampFlight2_own_origin.fbx`. Same names as v3.' % vis_tris,
          '- `manifest.json`, `fitcheck.json`, `fitcheck.md`, `report.txt`; `src/` holds the release scripts (mastfix.py, export.py, verify.py). `logs/` is scratch (ignored).', '',
          '## Axes, pivots, placement (unchanged from v3)',
          '- 1 Blender unit = 1 stud. Blender Z-up; Roblox local (x, y, z) = (bx, bz, -by). FBX: axis_forward -Z, axis_up Y, scale 1, FBX_SCALE_UNITS, embedded textures, face smoothing.',
          '- Pivots/origins unchanged; the ramp own-origin FBXs have origin 0. Placement unchanged: **Roblox worldY = localY + 0.6** (water at world Y 0).', '',
          '## Collision delta',
          '- COL_Mast_Main top centre Roblox local %s -> %s; world %s -> %s. Highest collider point world Y %.3f -> %.3f.' % (f3(g0['top_center_roblox_local']), f3(g1['top_center_roblox_local']), f3(g0['top_center_roblox_world']), f3(g1['top_center_roblox_world']), g0['highest_roblox_world_y'], g1['highest_roblox_world_y']),
          '- Bottom centre %s (unchanged), cross-section %.2f x %.2f (unchanged), origin matrix unchanged. Full per-vertex table in fitcheck.md.' % (f3(g1['bottom_center_roblox_local']), g1['cross_section'][0], g1['cross_section'][1]), '',
          '## Rebuild (from the workdir; one Blender process at a time)', '```', 'B="C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe"',
          '"$B" -b --factory-startup original_v3.blend --python-exit-code 1 --python out/src/mastfix.py -- out/start_ship_v3_mastfix.blend',
          '"$B" -b --factory-startup out/start_ship_v3_mastfix.blend --python-exit-code 1 --python out/src/export.py -- out/fbx',
          '"$B" -b --factory-startup <blend> --python-exit-code 1 --python out/src/verify.py -- dump out/logs/<src|donor|fix>.json',
          '"$B" -b --factory-startup --python-exit-code 1 --python out/src/verify.py -- fbx out/fbx out/logs/fbx.json',
          '"$B" -b --factory-startup --python-exit-code 1 --python out/src/verify.py -- check out/logs/src.json out/logs/donor.json out/logs/fix.json out/logs/fbx.json out out/logs/steps.txt', '```',
          'mastfix.py embeds the measured donor coordinates (no donor file needed) and refuses to run on anything but the v3 source sha256. The donor dump is only used by verify.py as evidence.']
    open(os.path.join(O, 'README.md'), 'w', encoding='utf-8').write('\n'.join(rd) + '\n')
    steps = open(steps_p, encoding='utf-8').read() if os.path.exists(steps_p) else ''
    rep = ['START SHIP v3 MAST-COLLIDER FIX (start_ship_b2_detail_v3_mastfix) - report', 'Date: 2026-11-05',
           'Agent/model: Claude Code, model claude-opus-5-5 (Opus 5.5).',
           'Machine: this Windows PC (%s, node %s). Blender %s (hash %s), headless: "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b --factory-startup --python-exit-code 1, one process at a time.' % (platform.platform(), platform.node(), F['blender'], F['build_hash']),
           'No Studio/node/roblox/git/credentials touched. No art changes, no previews rendered (visuals byte-identical to v3).', '',
           'SOURCE original_v3.blend (= start_ship_b2_detail_v3/out/start_ship_v3.blend) sha256 %s (read-only)' % S['file_sha256'],
           'DONOR  mast_donor_v3_2.blend sha256 %s (COL_Mast_Main vertex positions only; origin matrix identical to source)' % Dn['file_sha256'],
           'OUTPUT start_ship_v3_mastfix.blend sha256 %s' % F['file_sha256'], '', 'HARD CHECKS: %s' % ('PASS' if PASS else 'FAIL: ' + '; '.join(fails)),
           '- Visual/ramp/prop meshes byte-identical %d/%d; %d tris, largest %s %d.' % (sum(vis_res.values()), len(vis), vis_tris, big, fo[big]['tris']),
           '- Colliders: 190 names exact; other 189 byte-identical %d/%d. Anchors exact: %s. Materials/images/collections identical: %s.' % (sum(col_res.values()), len(col_res), all(v['exact'] for v in an.values()), all(others.values())),
           '- COL_Mast_Main: length %.4f -> %.4f; bottom 4 verts identical; cross-section identical; origin matrix identical; vertices == donor: %s.' % (g0['length_along_axis'], g1['length_along_axis'], mf['local_co'] == md['local_co']),
           '  top centre Roblox local %s -> %s ; world %s -> %s' % (f3(g0['top_center_roblox_local']), f3(g1['top_center_roblox_local']), f3(g0['top_center_roblox_world']), f3(g1['top_center_roblox_world'])),
           '- FBX re-import: ' + '; '.join('%s %d obj %s tris ok=%s' % (k, v['objects'], v['tris'], v['names_ok'] and v['origins_ok'] and v['tris_ok']) for k, v in fx.items()), '',
           'STEPS (exit code / seconds):', steps.rstrip()]
    open(os.path.join(O, 'report.txt'), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
    print('CHECK', 'PASS' if PASS else 'FAIL', fails)
    if not PASS: sys.exit(1)


if MODE == 'dump': dump(A[1])
elif MODE == 'fbx': fbx(A[1], A[2])
elif MODE == 'check': check(*A[1:7])
else: sys.exit('unknown mode')
