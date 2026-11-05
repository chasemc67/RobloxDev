# Scan Hull for degenerate / near-degenerate faces and render-ray hits from the stern preview camera that land on odd faces.
import bpy, bmesh, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import *
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out = sys.argv[sys.argv.index('--') + 1]
ob = bpy.data.objects['Hull']; me = ob.data; bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
small = []
for f in bm.faces:
    a = f.calc_area(); e = [l.calc_length() for l in f.edges]
    if a < 0.05 or (max(e) > 0 and a / max(e) ** 2 < 1e-3):
        small.append(dict(i=f.index, area=a, longest=max(e), mat=me.materials[f.material_index].name, c=[round(v, 2) for v in untilt(Binv(f.calc_center_median()))], n=list(f.normal)))
# rays from the stern camera
T = BVHTree.FromBMesh(bm); eye = np.array((-330.0, 60.0, 160.0)); tgt = np.array((-120.0, 40.0, 10.0))
fw = nrm(tgt - eye); rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw); hits = {}
for i in range(-160, 161, 1):
    for j in range(-100, 101, 1):
        d = nrm(fw + rt * i / 160 * math.tan(math.radians(21)) + up * j / 160 * math.tan(math.radians(21)))
        loc, nor, idx, dist = T.ray_cast(Vector(B(eye)), Vector(B(d)), 2000)
        if loc is None: continue
        f = bm.faces[idx]; back = nor.dot(Vector(B(d))) > 0
        k = hits.setdefault(idx, dict(n=0, back=0, area=f.calc_area(), mat=me.materials[f.material_index].name, c=[round(v, 2) for v in untilt(Binv(f.calc_center_median()))]))
        k['n'] += 1; k['back'] += int(back)
backs = {i: v for i, v in hits.items() if v['back'] > 0}
json.dump(dict(n_faces=len(bm.faces), small=small, backfacing_from_stern_cam=backs), open(out, 'w'), indent=1)
print('SCAN', len(bm.faces), 'small', len(small), 'back', len(backs))
