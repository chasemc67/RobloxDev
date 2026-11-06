# read-only probe of source_v5.blend (nothing saved). blender -b --factory-startup source_v5.blend --python probe_v5_1.py -- <out.json>
import bpy, sys, os, json, bmesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import Binv
import numpy as np
A = sys.argv[sys.argv.index('--') + 1:]
out = dict(blender=bpy.app.version_string, file=bpy.data.filepath, objects={}, materials={}, images=[],
           view=dict(vt=bpy.context.scene.view_settings.view_transform, look=bpy.context.scene.view_settings.look))
for m in bpy.data.materials:
    if not m.use_nodes: out['materials'][m.name] = None; continue
    nodes = [(n.type, n.name, getattr(getattr(n, 'image', None), 'name', None), getattr(getattr(n, 'image', None), 'colorspace_settings', None) and n.image.colorspace_settings.name) for n in m.node_tree.nodes]
    bs = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    links = [(l.from_node.type, l.from_socket.name, l.to_node.type, l.to_socket.name) for l in m.node_tree.links]
    out['materials'][m.name] = dict(rgb=list(m.get('rgb', [])), nodes=nodes, links=links, base=[round(x, 4) for x in bs.inputs['Base Color'].default_value] if bs else None, users=m.users)
out['images'] = [(i.name, list(i.size), i.packed_file is not None, i.colorspace_settings.name, i.filepath) for i in bpy.data.images]
for o in bpy.data.objects:
    if o.name.startswith('COL'): continue
    e = dict(type=o.type, coll=[c.name for c in o.users_collection], loc_roblox=list(np.round(Binv(o.matrix_world.translation), 3)), mw_identity_rot=bool(np.allclose(np.array(o.matrix_world.to_3x3()), np.eye(3))),
             note=str(o.get('note', '')), note_v5=str(o.get('note_v5', '')))
    if o.type == 'MESH':
        co = np.array([o.matrix_world @ v.co for v in o.data.vertices]); R = np.column_stack([co[:, 0], co[:, 2], -co[:, 1]])
        e.update(bbmin=list(R.min(0).round(2)), bbmax=list(R.max(0).round(2)), tris=sum(len(p.vertices) - 2 for p in o.data.polygons), mats=[m.name for m in o.data.materials], mesh=o.data.name)
        # connected components summary (for props near the tee)
        if o.name.startswith('Prop_') or o.name.startswith('ShipV5_'):
            bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bm.verts.ensure_lookup_table(); seen = set(); comps = []
            for v in bm.verts:
                if v in seen: continue
                st = [v]; c = []; seen.add(v)
                while st:
                    a = st.pop(); c.append(a)
                    for ed in a.link_edges:
                        w = ed.other_vert(a)
                        if w not in seen: seen.add(w); st.append(w)
                P = np.array([Binv(x.co) for x in c]); comps.append((P.min(0), P.max(0), len(c)))
            bm.free()
            # merge overlapping comps' boxes into clusters
            cl = []
            for a, b, n in comps:
                for k in cl:
                    if np.all(a <= k[1] + 0.3) and np.all(b >= k[0] - 0.3): k[0] = np.minimum(k[0], a); k[1] = np.maximum(k[1], b); k[2] += n; break
                else: cl.append([a.copy(), b.copy(), n])
            e['n_components'] = len(comps)
            e['clusters'] = [dict(min=list(np.round(a, 1)), max=list(np.round(b, 1)), verts=n) for a, b, n in sorted(cl, key=lambda k: -k[2])[:40]]
    out['objects'][o.name] = e
out['ncol'] = len(bpy.data.collections['Collision'].objects)
out['collections'] = {c.name: len(c.objects) for c in bpy.data.collections}
out['scene_props'] = {k: str(v) for k, v in bpy.context.scene.items()}
json.dump(out, open(A[0], 'w'), indent=1, default=float); print('PROBE_OK')
