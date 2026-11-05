"""Round 4 walls: per-FBX geometry comparison (per material, world-space vertices, 4 dp).
  blender -b --factory-startup -P walls_compare.py -- <dirA> <dirB> [<dirC>] <out.json>
For every FBX name in dirA: A vs B (and A vs C if given). Reports which files / materials differ and the max vertex move."""
import bpy, sys, os, json
import numpy as np

args = sys.argv[sys.argv.index('--') + 1:]
dirs, out = args[:-1], args[-1]


def snap(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    V, T = {}, {}
    for o in bpy.context.scene.objects:
        if o.type != 'MESH':
            continue
        o.data.calc_loop_triangles()
        k = o.name.split('.')[0].split('__')[-1]
        T[k] = T.get(k, 0) + len(o.data.loop_triangles)
        V.setdefault(k, []).extend(tuple(round(c, 4) for c in (o.matrix_world @ v.co)) for v in o.data.vertices)
    return {k: np.array(sorted(v)) for k, v in V.items()}, T


def cmp(a, b):
    (Va, Ta), (Vb, Tb) = a, b
    res = {}
    for k in sorted(set(Va) | set(Vb)):
        if k not in Va or k not in Vb:
            res[k] = 'missing in ' + ('A' if k not in Va else 'B')
        elif Va[k].shape != Vb[k].shape:
            res[k] = f'vertex count {len(Va[k])} vs {len(Vb[k])}'
        elif not np.array_equal(Va[k], Vb[k]):
            res[k] = f'moved (sorted max |d| {np.abs(Va[k] - Vb[k]).max():.4f}, {int((np.abs(Va[k] - Vb[k]).max(1) > 1e-4).sum())} verts)'
        if Ta.get(k) != Tb.get(k):
            res[k] = res.get(k, '') + f' tris {Ta.get(k)} vs {Tb.get(k)}'
    return res


R = {}
for f in sorted(os.listdir(dirs[0])):
    if not f.endswith('.fbx'):
        continue
    S = [snap(os.path.join(d, f)) if os.path.exists(os.path.join(d, f)) else None for d in dirs]
    r = {}
    for j in range(1, len(dirs)):
        r[f'vs{j}'] = 'missing' if S[j] is None else cmp(S[0], S[j])
    R[f] = r
json.dump(R, open(out, 'w'), indent=1)
for f, r in R.items():
    if any(v for v in r.values()):
        print('DIFF', f, json.dumps(r))
print('compared', len(R))
