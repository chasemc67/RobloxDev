# blender.exe -b --factory-startup out/start_ship_v3_2.blend --python export_v32.py -- <fbx_dir> <verify_json> <v3_1_dump.json>
# v3_2: identical to prior_scripts/export_v31.py + reimported collider world-vertex comparison against the v3_1 dump.
# Same conventions as previous_scripts/export_v3.py: FBX axis_forward -Z, axis_up Y, scale 1, embedded textures, face smoothing.
# start_ship_b2_visual.fbx = Visual meshes + Ramps + Props + anchor empties; start_ship_b2_col.fbx = 190 COL boxes; 3 ramp FBXs on their own origin.
# The blend is NOT saved. After export, the scene is reset and every FBX re-imported to verify names / tris / origins.
import bpy, sys, os, json
A = sys.argv[sys.argv.index('--') + 1:]; OUT = A[0]; VJ = A[1]; DUMP = json.load(open(A[2])); os.makedirs(OUT, exist_ok=True)
import numpy as np
C = bpy.data.collections
order = ['Hull', 'DeckCabin', 'Rigging', 'RampFlight1', 'RampLanding', 'RampFlight2', 'Pier', 'RockBumper', 'Dressing', 'Dressing_Glow']
vis = [o for o in C['Visual'].objects if o.type == 'MESH'] + [o for o in C['Ramps'].objects]
vis.sort(key=lambda o: order.index(o.name))
props = sorted([o for o in C['Props'].objects if o.type == 'MESH'], key=lambda o: o.name)
emp = [o for o in C['Visual'].objects if o.type == 'EMPTY']
cob = list(C['Collision'].objects)
allmesh = set(o.name for o in bpy.data.objects if o.type == 'MESH')
assert allmesh == set(o.name for o in vis + props + cob), sorted(allmesh ^ set(o.name for o in vis + props + cob))
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons) if o.type == 'MESH' else 0
def rec(o, loc=None): return dict(type=o.type, tris=tris(o), loc=[round(c, 4) for c in (loc if loc is not None else o.matrix_world.translation)])
EXP = {}
def export(path, objs, override_loc=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH', 'EMPTY'}, axis_forward='-Z', axis_up='Y', global_scale=1,
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', path_mode='COPY', embed_textures=True,
                             mesh_smooth_type='FACE', add_leaf_bones=False)
    EXP[os.path.basename(path)] = {o.name: rec(o, override_loc) for o in objs}
    print('EXPORTED', path, len(objs))
export(os.path.join(OUT, 'start_ship_b2_visual.fbx'), vis + props + emp)
export(os.path.join(OUT, 'start_ship_b2_col.fbx'), cob)
for ob in vis:
    if ob.name.startswith('Ramp'):
        loc = ob.location.copy(); ob.location = (0, 0, 0); bpy.context.view_layer.update()
        export(os.path.join(OUT, ob.name + '_own_origin.fbx'), [ob], override_loc=(0.0, 0.0, 0.0)); ob.location = loc
print('EXPORT_OK')
# ---------------- reimport verify
V = dict(files={}, all_ok=True)
for fn, exp in EXP.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(OUT, fn))
    got = {o.name: rec(o) for o in bpy.data.objects}
    names_ok = set(got) == set(exp)
    tri_bad = [n for n in exp if n in got and got[n]['tris'] != exp[n]['tris']]
    loc_bad = [(n, exp[n]['loc'], got[n]['loc']) for n in exp if n in got and max(abs(a - b) for a, b in zip(exp[n]['loc'], got[n]['loc'])) > 1e-3]
    imgs = [dict(name=i.name, packed=i.packed_file is not None, size=list(i.size)) for i in bpy.data.images if i.type == 'IMAGE']
    colcmp = None
    if fn == 'start_ship_b2_col.fbx':
        mxd = 0.0; bad = []
        for n, sd in DUMP['collision'].items():
            o = bpy.data.objects.get(n)
            if o is None: bad.append(n); continue
            Wv = np.array([o.matrix_world @ v.co for v in o.data.vertices], dtype=np.float64); S0 = np.array(sd['world_verts'])
            if Wv.shape != S0.shape: bad.append(n); continue
            d = float(np.max(np.abs(Wv - S0))); mxd = max(mxd, d)
            if d > 1e-3: bad.append(n)
        colcmp = dict(colliders_compared=len(DUMP['collision']), max_abs_world_vertex_diff_vs_v3_1=mxd, over_tol_1e_3=bad, ok=not bad)
    ok = names_ok and not tri_bad and not loc_bad and (colcmp is None or colcmp['ok'])
    V['files'][fn] = dict(bytes=os.path.getsize(os.path.join(OUT, fn)), objects_exported=len(exp), objects_reimported=len(got), names_ok=names_ok,
                          missing=sorted(set(exp) - set(got)), extra=sorted(set(got) - set(exp)), tris_exported=sum(v['tris'] for v in exp.values()),
                          tris_reimported=sum(v['tris'] for v in got.values()), tri_mismatch=tri_bad, origin_mismatch=loc_bad[:10], images_after_import=imgs, collision_vs_v3_1=colcmp, ok=ok,
                          per_object={n: dict(tris=exp[n]['tris'], origin_blender=exp[n]['loc'], reimported_origin=got.get(n, {}).get('loc')) for n in exp})
    V['all_ok'] &= ok
    print('VERIFY', fn, ok, len(exp), len(got))
json.dump(V, open(VJ, 'w'), indent=1)
print('VERIFY_DONE all_ok=', V['all_ok'])
