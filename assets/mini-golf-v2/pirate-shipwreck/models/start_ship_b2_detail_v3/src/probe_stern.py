# Probe the Hull stern cap for see-through slits: rays from astern along +X (hull frame), report where the first hit is NOT on the cap.
# blender -b --factory-startup <blend> --python probe_stern.py -- <out_json>
import bpy, bmesh, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import *
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out = sys.argv[sys.argv.index('--') + 1]
ob = bpy.data.objects['Hull']; bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world); bm.faces.ensure_lookup_table()
T = BVHTree.FromBMesh(bm); bad = []; total = 0; back = []
for y in np.arange(-1.5, 58.0, 0.2):
    for z in np.arange(-44.0, 44.0, 0.5):
        o = tilt((X0 - 10, y, z)); d = tilt((1, 0, 0))
        # only probe inside the stern silhouette
        b = bprof(X0); h = hgt(X0); y0 = y0skirt(X0); s = z / b
        if abs(s) > 0.98 or y < y0 + (h - y0) * abs(s) ** PW + 0.3 or y > h - 0.3: continue
        total += 1
        loc, nor, idx, dist = T.ray_cast(Vector(B(o)), Vector(B(d)), 40)
        hx = untilt(Binv(loc))[0] if loc is not None else None
        if loc is not None and nor.dot(Vector(B(d))) > 0:
            f = bm.faces[idx]; back.append(dict(y=round(float(y), 2), z=round(float(z), 2), face=idx, mat=ob.data.materials[f.material_index].name, c=[round(v, 2) for v in untilt(Binv(f.calc_center_median()))], nv=len(f.verts)))
        if loc is None or hx > X0 + 0.5:
            f = bm.faces[idx] if idx is not None else None
            bad.append(dict(y=round(float(y), 2), z=round(float(z), 2), hit_x=None if hx is None else round(float(hx), 2), mat=None if f is None else ob.data.materials[f.material_index].name))
ys = sorted(set(b_['y'] for b_ in bad))
bf = sorted(set(b_['face'] for b_ in back))
json.dump(dict(backfacing_hits=len(back), backfacing_faces=bf, back_sample=[next(b_ for b_ in back if b_['face'] == f) for f in bf], total=total, bad=len(bad), y_values=ys, sample=bad[:40]), open(out, 'w'), indent=1)
print('PROBE', total, len(bad), 'backfacing', len(back), bf)
