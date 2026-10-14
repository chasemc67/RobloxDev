"""Stage sc9: per-mesh footprint geometry for the look7 kit (sources + LODs), in Roblox axes relative to the FBX pivot.
For each FBX (stem) and each mesh slot (<stem>__<Material>, as sc5_merge_fbx --split-materials names them):
  hull  = XZ convex hull of the slot's vertices, minY = lowest vertex, bottom = up to 16 well-spread vertices within 0.05
  of the stem's lowest point (the contact ring used by the float check). Roblox = (bx, bz, -by), as the merge reports.
  Blender -b --factory-startup --python sc9_mesh_geom.py -- <list.json> <out.json>
"""
import bpy, json, sys
from pathlib import Path
args = sys.argv[sys.argv.index('--') + 1:]
SOURCES = json.loads(Path(args[0]).read_text())


def hull2(pts):
    pts = sorted(set(pts))
    if len(pts) < 3: return pts
    def cr(o, a, b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cr(hi[-2], hi[-1], p) <= 0: hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def spread(pts, k=16):
    if len(pts) <= k: return pts
    out = [pts[0]]
    while len(out) < k:
        out.append(max(pts, key=lambda p: min((p[0]-q[0])**2+(p[2]-q[2])**2 for q in out)))
    return out


res = {}
for s in SOURCES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=s['fbx'], axis_forward='-Z', axis_up='Y', global_scale=1.0)
    dg = bpy.context.evaluated_depsgraph_get()
    slots, allv = {}, []
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH': continue
        me = ob.evaluated_get(dg).to_mesh()
        mats = [m.name.split('.')[0] if m else 'None' for m in ob.data.materials] or ['None']
        for poly in me.polygons:
            slot = mats[poly.material_index] if poly.material_index < len(mats) else mats[0]
            for vi in poly.vertices:
                w = ob.matrix_world @ me.vertices[vi].co
                v = (round(w.x, 4), round(w.z, 4), round(-w.y, 4))
                slots.setdefault(slot, set()).add(v); allv.append(v)
        ob.evaluated_get(dg).to_mesh_clear()
    miny = min(v[1] for v in allv)
    out = {}
    for slot, vs in slots.items():
        vs = list(vs)
        out[s['stem'] + '__' + slot] = {'hull': hull2([(v[0], v[2]) for v in vs]), 'minY': min(v[1] for v in vs),
                                        'maxY': max(v[1] for v in vs)}
    res[s['stem']] = {'slots': out, 'minY': miny, 'bottom': spread(sorted({v for v in allv if v[1] <= miny + 0.05}))}
Path(args[1]).write_text(json.dumps(res))
print('SC9_GEOM', len(res), sum(len(r['slots']) for r in res.values()))
