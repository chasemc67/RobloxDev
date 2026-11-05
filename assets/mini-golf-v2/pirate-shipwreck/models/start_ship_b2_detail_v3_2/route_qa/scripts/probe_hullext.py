# read-only: are any collider volumes occupying the walk band (y 24.05..29) on the outrigger / notch route section?
import bpy, numpy as np, json, sys
from mathutils import Vector
def Binv(p): return np.array((p[0], p[2], -p[1]))
def B(p): return Vector((p[0], -p[2], p[1]))
out = {}
for n in ('COL_HullExt_0_07', 'COL_HullExt_1_07', 'COL_HullExt_0_06', 'COL_HullExt_1_06', 'COL_Outrigger'):
    o = bpy.data.objects[n]; out[n] = [list(np.round(Binv(o.matrix_world @ v.co), 3)) for v in o.data.vertices]
def inside(o, p):   # convex closed mesh: inside if behind all face planes (world space)
    mw = o.matrix_world; q = B(p); nm = mw.to_3x3().inverted().transposed()
    for f in o.data.polygons:
        c = mw @ f.center; nn = (nm @ f.normal).normalized()
        if (q - c).dot(nn) > 1e-6: return False
    return True
cols = [o for o in bpy.data.objects if o.name.startswith('COL') and o.type == 'MESH']
occ = {}
for x in np.arange(-128.0, -111.9, 1.0):
    for z in np.arange(40.0, 64.1, 0.5):
        for y in (24.1, 24.5, 25.5, 26.5, 28.5, 30.0):
            for o in cols:
                if inside(o, (x, y, z)): occ.setdefault(o.name, []).append((float(x), float(y), float(z)))
summ = {k: dict(n=len(v), x=[min(a[0] for a in v), max(a[0] for a in v)], y=[min(a[1] for a in v), max(a[1] for a in v)], z=[min(a[2] for a in v), max(a[2] for a in v)]) for k, v in occ.items()}
json.dump(dict(verts=out, occupancy=summ, samples=occ), open(sys.argv[-1], 'w'), indent=1)
print('PROBE_OK', json.dumps(summ))
