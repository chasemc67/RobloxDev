"""Stage sc12 item 3: H3 pebble component 26 onto the h03_ground_s22 strip. Only that component's vertices change.
Source: fix_v42_item5c/h03_dress_props.fbx (the sc8 import). Keeps the Pebble object only; component 26 = the connected
component whose Roblox-axis centroid is at hole-local (53.655, 0.211, 9.209) (H3 root (-95, 18, -4670), identity rotation).
Transform (Roblox axes, hole-local = world offsets): yaw YAW deg about the vertical axis through CENTRE (the Studio vertex
mean of the component), then dz. Roblox = (bx, bz, -by).
  Blender -b --factory-startup --python tools/sc12_pebble_fbx.py -- <in.fbx> <out.fbx> <yaw> <dz>
"""
import bpy, bmesh, sys, math, json
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT, YAW, DZ = a[0], a[1], math.radians(float(a[2])), float(a[3])
CENTRE = (-41.34480285644531 + 95, 18.210725784301758 - 18, -4660.79052734375 + 4670)
TARGET = (53.655, 0.211, 9.209)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.fbx(filepath=SRC, axis_forward='-Z', axis_up='Y', global_scale=1.0)
names = [o.name for o in bpy.data.objects]
peb = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.split('.')[0].endswith('Pebble')]
assert len(peb) == 1, names
peb = peb[0]
for o in list(bpy.data.objects):
    if o is not peb and o.type == 'MESH': bpy.data.objects.remove(o, do_unlink=True)
me = peb.data; M = peb.matrix_world; Mi = M.inverted()
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
seen = set(); comps = []
for v in bm.verts:
    if v.index in seen: continue
    st = [v]; comp = []; seen.add(v.index)
    while st:
        x = st.pop(); comp.append(x.index)
        for e in x.link_edges:
            y = e.other_vert(x)
            if y.index not in seen: seen.add(y.index); st.append(y)
    comps.append(comp)
def rbx(co): w = M @ co; return (w.x, w.z, -w.y)
def cen(c): P = [rbx(bm.verts[i].co) for i in c]; return tuple(sum(p[k] for p in P) / len(P) for k in range(3))
best = min(comps, key=lambda c: sum((x - y) ** 2 for x, y in zip(cen(c), TARGET)))
d = math.dist(cen(best), TARGET)
assert d < 0.05 and len(best) == 12, (d, len(best))
lo_before = [min(rbx(v.co)[k] for v in bm.verts) for k in range(3)]; hi_before = [max(rbx(v.co)[k] for v in bm.verts) for k in range(3)]
rep = {'objects': names, 'pebble': peb.name, 'components': len(comps), 'comp26': {'verts': len(best), 'centroidDist': d}, 'moves': []}
for i in best:
    x, y, z = rbx(bm.verts[i].co)
    dx, dz = x - CENTRE[0], z - CENTRE[2]
    nx = CENTRE[0] + dx * math.cos(YAW) - dz * math.sin(YAW)
    nz = CENTRE[2] + dx * math.sin(YAW) + dz * math.cos(YAW) + DZ
    w = Vector((nx, -nz, y))                        # back to Blender world axes
    bm.verts[i].co = Mi @ w
    rep['moves'].append([[x, y, z], [nx, y, nz]])
lo = [min(rbx(v.co)[k] for v in bm.verts) for k in range(3)]; hi = [max(rbx(v.co)[k] for v in bm.verts) for k in range(3)]
rep['boundsBefore'] = [lo_before, hi_before]; rep['boundsAfter'] = [lo, hi]
bm.to_mesh(me); me.update(); bm.free()
bpy.ops.export_scene.fbx(filepath=OUT, axis_forward='-Z', axis_up='Y', global_scale=1, path_mode='COPY', embed_textures=True,
                         add_leaf_bones=False, bake_anim=False)
json.dump(rep, open(OUT.replace('.fbx', '_pebble.json'), 'w'), indent=1)
print('PEBBLE', json.dumps({k: v for k, v in rep.items() if k != 'moves'}))
