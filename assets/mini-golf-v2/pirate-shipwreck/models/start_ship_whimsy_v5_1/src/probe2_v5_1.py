# read-only probe 2: per-component detail of the tee-area props + deck edges (nothing saved)
import bpy, sys, os, json, bmesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import Binv, deck_edges
import numpy as np
A = sys.argv[sys.argv.index('--') + 1:]
out = {}
def comps(o):
    me = o.data; bm = bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); bm.faces.ensure_lookup_table(); seen = set(); res = []
    for f in bm.faces:
        if f in seen: continue
        st = [f]; c = []; seen.add(f)
        while st:
            a = st.pop(); c.append(a)
            for e in a.edges:
                for g in e.link_faces:
                    if g not in seen: seen.add(g); st.append(g)
        P = np.array([Binv(v.co) for g in c for v in g.verts]); mats = sorted(set(me.materials[g.material_index].name for g in c))
        res.append(dict(faces=len(c), min=list(np.round(P.min(0), 2)), max=list(np.round(P.max(0), 2)), mats=mats))
    bm.free(); return res
for n in ['Prop_CargoCluster', 'Prop_TreasureChest', 'Prop_SternWheel', 'Prop_RopeCoils', 'Prop_Crab', 'Dressing']:
    o = bpy.data.objects[n]; out[n] = [c for c in comps(o) if n != 'Dressing' or (c['max'][0] > -112 and c['min'][0] < -40)]
out['deck_edges'] = {str(x): deck_edges(float(x)) for x in range(-130, -30, 5)}
json.dump(out, open(A[0], 'w'), indent=1, default=float); print('PROBE2_OK')
