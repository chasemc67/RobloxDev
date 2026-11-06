# read-only probe of source_v3_2.blend: objects, collections, bboxes (Roblox coords), materials, tris. Nothing saved.
import bpy, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import Binv
import numpy as np
A = sys.argv[sys.argv.index('--') + 1:]
out = dict(collections={c.name: [o.name for o in c.objects] for c in bpy.data.collections if c.name != 'Collision'}, objects={},
           materials={m.name: [round(x, 4) for x in next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value] if m.use_nodes and any(n.type == 'BSDF_PRINCIPLED' for n in m.node_tree.nodes) else None for m in bpy.data.materials},
           images=[(i.name, list(i.size), i.packed_file is not None) for i in bpy.data.images], ncol=len(bpy.data.collections['Collision'].objects))
for o in bpy.data.objects:
    if o.type == 'MESH':
        co = np.array([o.matrix_world @ v.co for v in o.data.vertices]); R = np.column_stack([co[:, 0], co[:, 2], -co[:, 1]])
        e = dict(loc_roblox=list(np.round(Binv(o.location), 3)), rot=list(np.round(o.rotation_euler, 4)), scale=list(o.scale), bbmin=list(R.min(0).round(2)), bbmax=list(R.max(0).round(2)),
                 tris=sum(len(p.vertices) - 2 for p in o.data.polygons), mats=[m.name for m in o.data.materials], uv=[u.name for u in o.data.uv_layers])
        if o.name.startswith('COL'):
            if 'Hull' in o.name or 'hull' in o.name.lower(): out.setdefault('col_hull', {})[o.name] = e
            continue
        out['objects'][o.name] = e
    else:
        out['objects'][o.name] = dict(type=o.type, loc_roblox=list(np.round(Binv(o.location), 3)), parent=o.parent.name if o.parent else None)
out['col_names'] = [o.name for o in bpy.data.collections['Collision'].objects]
json.dump(out, open(A[0], 'w'), indent=1, default=float); print('PROBE_OK')
