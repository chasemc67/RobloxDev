# validate_round1.py - checks + manifest. Run AFTER build + 3 renders (one Blender job):
#   blender -b --factory-startup --python-exit-code 1 --python out/src/validate_round1.py -- \
#       --source inputs/start_ship_whimsy_v5_1.blend --output out/pirate_thumbnail_round1.blend
# Compares every source object (mesh data, transforms, materials+node values, modifiers) between the source .blend and
# the packed output; checks source SHA-256, 3 saved cameras, PNG resolutions, packed images; writes out/manifest.json.
import bpy, os, sys, json, hashlib, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(OUTDIR, '..'))
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument('--source', default=os.path.join(ROOT, 'inputs', 'start_ship_whimsy_v5_1.blend'))
p.add_argument('--output', default=os.path.join(OUTDIR, 'pirate_thumbnail_round1.blend'))
p.add_argument('--expected-sha', default='fd7798af4ca9bd107dba927bdf663e7017c04f8c4c7649b518b5c78c8d4bcacd')
p.add_argument('--hash-before', default=None, help='sha256 recorded before the build (optional)')
p.add_argument('--res', default='1280x720')
a = p.parse_args(argv)
RES = [int(v) for v in a.res.split('x')]


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def h_arr(arr):
    return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()[:16]


def mat_sig(m):
    if m is None:
        return None
    d = [m.name]
    if m.node_tree:
        for n in sorted(m.node_tree.nodes, key=lambda n: n.name):
            for i in n.inputs:
                if hasattr(i, 'default_value'):
                    v = i.default_value
                    try:
                        v = [round(float(x), 5) for x in v]
                    except TypeError:
                        v = round(float(v), 5) if isinstance(v, (int, float)) else str(v)
                    d.append((n.type, n.name, i.identifier, v))
            if n.type == 'TEX_IMAGE' and n.image:
                d.append(('img', n.image.name, n.interpolation))
    return hashlib.sha256(json.dumps(d, default=str).encode()).hexdigest()[:16]


def signature(names=None):
    out = {}
    for o in bpy.data.objects:
        if names is not None and o.name not in names:
            continue
        is_col = o.name.startswith('COL_') or any(c.name == 'Collision' for c in o.users_collection)
        # basis transform = the real object transform. matrix_world is compared too, except for Collision objects whose stored
        # matrix_world cache is stale in the source file (not evaluated there) and gets refreshed when any file is saved.
        s = dict(type=o.type, basis=[round(x, 5) for x in (*o.location, *o.rotation_euler, *o.scale, *o.delta_location, *o.delta_rotation_euler, *o.delta_scale)],
                 rotation_mode=o.rotation_mode, matrix_parent_inverse=[round(x, 5) for r in o.matrix_parent_inverse for x in r],
                 matrix=None if is_col else [round(x, 5) for r in o.matrix_world for x in r],
                 parent=o.parent.name if o.parent else None, modifiers=[(m.type, m.name) for m in o.modifiers])
        if o.type == 'MESH':
            me = o.data
            co = np.zeros(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co)
            lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
            mi = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
            s.update(verts=len(me.vertices), polys=len(me.polygons), tris=int(sum(len(q.vertices) - 2 for q in me.polygons)),
                     co=h_arr(co), loops=h_arr(lv), mat_index=h_arr(mi), materials=[mat_sig(m) for m in me.materials])
        out[o.name] = s
    return out


R = dict(checks={})
try:
    src_sha = sha(a.source)
    bpy.ops.wm.open_mainfile(filepath=a.source, load_ui=False)
    src_sig = signature()
    src_cols = {c.name: len(c.objects) for c in bpy.data.collections}
    bpy.ops.wm.open_mainfile(filepath=a.output, load_ui=False)
    out_sig = signature(set(src_sig))
    diffs = []
    for nm, s in src_sig.items():
        if nm not in out_sig:
            diffs.append((nm, 'missing')); continue
        for k, v in s.items():
            if out_sig[nm].get(k) != v:
                diffs.append((nm, k))
    ship_tris = sum(v.get('tris', 0) for v in src_sig.values())
    R['checks']['ship_objects_identical'] = dict(ok=not diffs, compared_objects=len(src_sig), compared='mesh vertex-coordinate/loop/material_index hashes, basis transforms (loc/rot/scale/deltas/parent inverse), matrix_world (non-Collision), parent, modifiers, material node values', note='Collision objects: stored matrix_world cache stale in source (not evaluated); basis transforms identical', diffs=diffs[:50])
    after = sha(a.source)
    R['checks']['source_sha256'] = dict(ok=(src_sha == a.expected_sha == after), expected=a.expected_sha, before=a.hash_before or src_sha, after=after)
    cams = {}
    for scn in ('Thumbnail_A_Hero', 'Thumbnail_B_Octopus', 'Thumbnail_C_Adventure'):
        sc = bpy.data.scenes.get(scn)
        cams[scn] = dict(scene=bool(sc), camera=sc.camera.name if sc and sc.camera else None,
                         collision_linked=bool(sc and any(c.name == 'Collision' for c in sc.collection.children_recursive)),
                         view_transform=sc.view_settings.view_transform if sc else None, engine=sc.render.engine if sc else None,
                         device=sc.cycles.device if sc else None, samples=sc.cycles.samples if sc else None,
                         resolution=[sc.render.resolution_x, sc.render.resolution_y] if sc else None)
    R['checks']['cameras'] = dict(ok=all(v['camera'] == k for k, v in cams.items()) and not any(v['collision_linked'] for v in cams.values()), scenes=cams)
    R['checks']['helpers_render_hidden'] = dict(ok=all(o.hide_render for o in bpy.data.objects if o.type == 'EMPTY'),
                                               empties=[o.name for o in bpy.data.objects if o.type == 'EMPTY'])
    imgs = [(i.name, i.packed_file is not None) for i in bpy.data.images if i.source == 'FILE']
    R['checks']['images_packed'] = dict(ok=all(pk for _, pk in imgs), images=imgs)
    pngs = {}
    for k in 'ABC':
        fp = os.path.join(OUTDIR, 'previews', '%s_round1.png' % k)
        if os.path.exists(fp):
            im = bpy.data.images.load(fp)
            pngs[k] = dict(path='previews/%s_round1.png' % k, size=list(im.size), sha256=sha(fp))
            bpy.data.images.remove(im)
        else:
            pngs[k] = None
    R['checks']['previews'] = dict(ok=all(v and v['size'] == RES for v in pngs.values()), files=pngs)
    R['ok'] = all(c['ok'] for c in R['checks'].values())

    br = json.load(open(os.path.join(OUTDIR, 'build', 'build_report.json')))
    man = dict(job='Pirate ship thumbnails ROUND 1 (A hero / B octopus / C adventure): proofs for Playtest+Art critique, not final',
               status='round1 delivered; waiting for round2 feedback (no further iterations made)',
               source=dict(path='inputs/start_ship_whimsy_v5_1.blend', commit='0852f9d', sha256_before=a.hash_before or src_sha, sha256_after=after,
                           objects=len(src_sig), tris_all_objects_incl_collision=ship_tris, collections=src_cols),
               output=dict(path='out/pirate_thumbnail_round1.blend', sha256=sha(a.output), bytes=os.path.getsize(a.output), packed=True,
                           scenes=['Thumbnail_A_Hero', 'Thumbnail_B_Octopus', 'Thumbnail_C_Adventure'],
                           note='Original "Scene" from the source file is kept untouched (it still links Collision); use the three Thumbnail_* scenes.'),
               validation=R,
               scenes=br['scenes'], water_z=br['water_z'], key_points_world=br['key_points'],
               tris=dict(original_ship_rendered=br['tris']['ship'], added_terrain=br['tris']['terrain'], added_water=br['tris']['water'],
                         added_kit_props_total_all_scenes=br['tris']['kit_props_total'], added_kit_props_by_collection=br['tris']['kit_props_by_collection']),
               render_only_additions=dict(collection='RENDER_ONLY_Environment',
                                          note='Staged tropical cove for thumbnails only. NOT the game layout and NOT the v30/v31 placement.',
                                          procedural=['RO_CoveTerrain: faceted height-field sand/lagoon seabed (height() in build script), colour by height',
                                                      'RO_SeaFloorFar: deep-sea floor plane', 'RO_WaterSurface: transparent + glossy water, bump waves, z=%.1f' % br['water_z'],
                                                      'RO_TropicalSky: gradient sky world', 'per-scene sun key + shadowless fill'],
                                          kit_instances=br['placed']),
               hidden_helpers=br['hidden_helpers'])
    json.dump(man, open(os.path.join(OUTDIR, 'manifest.json'), 'w'), indent=1)
    print('VALIDATION', json.dumps({k: v['ok'] for k, v in R['checks'].items()}), 'ALL_OK' if R['ok'] else 'FAILED')
    if diffs:
        print('DIFFS', diffs[:20])
    sys.exit(0 if R['ok'] else 1)
except SystemExit:
    raise
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
