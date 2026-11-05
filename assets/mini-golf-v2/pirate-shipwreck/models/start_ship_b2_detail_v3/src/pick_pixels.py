# pick which object/face a preview pixel shows (camera given in Roblox coords), against all visual meshes
import bpy, bmesh, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import *
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index('--') + 1:]; eye = np.array(json.loads(A[0])); tgt = np.array(json.loads(A[1])); fov = float(A[2]); pixels = json.loads(A[3])
W, H = 1600, 1000
trees = {}
for ob in bpy.data.objects:
    if ob.type != 'MESH' or ob.name.startswith('COL'): continue
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world); bm.faces.ensure_lookup_table(); trees[ob.name] = (BVHTree.FromBMesh(bm), bm, ob)
fw = nrm(tgt - eye); rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw); t = math.tan(math.radians(fov) / 2)
for px, py in pixels:
    sx = (px + 0.5) / W * 2 - 1; sy = -((py + 0.5) / H * 2 - 1) * H / W
    d = nrm(fw + rt * sx * t + up * sy * t); best = None
    for n, (T, bm, ob) in trees.items():
        loc, nor, idx, dist = T.ray_cast(Vector(B(eye)), Vector(B(d)), 5000)
        if loc is not None and (best is None or dist < best[0]): best = (dist, n, idx, nor, loc)
    if best:
        dist, n, idx, nor, loc = best; T, bm, ob = trees[n]; f = bm.faces[idx]
        vs = [list(np.round(untilt(Binv(v.co)), 2)) for v in f.verts]
        print('PICK', (px, py), n, idx, ob.data.materials[f.material_index].name, 'area', round(f.calc_area(), 3), 'facing', round(float(nor.dot(Vector(B(d)))), 3), 'hullframe verts', vs)
