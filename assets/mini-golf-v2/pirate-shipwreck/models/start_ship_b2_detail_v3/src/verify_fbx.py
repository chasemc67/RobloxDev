# blender -b --factory-startup --python verify_fbx.py -- <fbx_dir> <out_json> : re-import each exported FBX into an empty scene and record names/tris/materials/origins/images
import bpy, sys, os, json
A = sys.argv[sys.argv.index('--') + 1:]; D = A[0]; res = {}
for f in sorted(os.listdir(D)):
    if not f.endswith('.fbx'): continue
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=os.path.join(D, f)); objs = {}
    for o in bpy.data.objects:
        e = dict(type=o.type, loc=[round(v, 4) for v in o.matrix_world.translation], scale=[round(v, 5) for v in o.matrix_world.to_scale()])
        if o.type == 'MESH': e.update(tris=sum(len(p.vertices) - 2 for p in o.data.polygons), mats=[m.name for m in o.data.materials])
        objs[o.name] = e
    res[f] = dict(objects=len(objs), meshes=sum(1 for v in objs.values() if v['type'] == 'MESH'), empties=sorted(n for n, v in objs.items() if v['type'] == 'EMPTY'),
                  tris_total=sum(v.get('tris', 0) for v in objs.values()), images=[(i.name, list(i.size), bool(i.packed_file)) for i in bpy.data.images],
                  size_bytes=os.path.getsize(os.path.join(D, f)), objs=objs if not f.endswith('_col.fbx') else {k: objs[k] for k in sorted(objs)[:3]})
json.dump(res, open(A[1], 'w'), indent=1); print('VERIFY_OK', {k: (v['objects'], v['tris_total']) for k, v in res.items()})
