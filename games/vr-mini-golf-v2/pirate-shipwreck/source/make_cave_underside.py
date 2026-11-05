"""Rasterise the cave v2.2 rock mesh (lower + upper) into per-stud 'lowest surface seen from below' and 'floor top' maps.
Input: assets/.../cave_v2_2/work/geom/*.json (Roblox frame (x, y_up, z), origin at cave base centre).
Output: data/cave_underside.npz  (grid origin = cave local x -120, z -72, 1 stud per sample)
  under[z, x]  lowest y (local, 0 = world 66) of any rock triangle above this column, nan = none
"""
import json, os, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEOM = '/workspace/RobloxDev/assets/mini-golf-v2/pirate-shipwreck/models/cave_v2_2/work/geom'
X0, Z0, NX, NZ = -120, -72, 241, 145
under = np.full((NZ, NX), np.inf)
for name in ('cave_cliff_lower', 'cave_cliff_upper'):
    o = json.load(open(f'{GEOM}/{name}.json'))[name]['objects'][0]
    V = np.array(o['verts'], float); T = np.array(o['tris'], int)
    P = np.stack([V[:, 0], V[:, 2], V[:, 1]], 1)          # verts are already Roblox-frame (x, y_up, z): columns (x, z, y)
    for a, b, c in T:
        A, B, C = P[a], P[b], P[c]
        xmin, xmax = int(np.floor(min(A[0], B[0], C[0]))), int(np.ceil(max(A[0], B[0], C[0])))
        zmin, zmax = int(np.floor(min(A[1], B[1], C[1]))), int(np.ceil(max(A[1], B[1], C[1])))
        xs = np.arange(max(xmin, X0), min(xmax, X0 + NX - 1) + 1); zs = np.arange(max(zmin, Z0), min(zmax, Z0 + NZ - 1) + 1)
        if len(xs) == 0 or len(zs) == 0: continue
        gx, gz = np.meshgrid(xs, zs)
        d = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1])
        if abs(d) < 1e-9: continue
        l1 = ((B[1] - C[1]) * (gx - C[0]) + (C[0] - B[0]) * (gz - C[1])) / d
        l2 = ((C[1] - A[1]) * (gx - C[0]) + (A[0] - C[0]) * (gz - C[1])) / d
        l3 = 1 - l1 - l2
        m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not m.any(): continue
        y = l1 * A[2] + l2 * B[2] + l3 * C[2]
        ii, jj = gx[m] - X0, gz[m] - Z0
        np.minimum.at(under, (jj, ii), y[m])
under[np.isinf(under)] = np.nan
np.savez_compressed(f'{ROOT}/data/cave_underside.npz', under=under, x0=X0, z0=Z0)
print('covered columns', int(np.isfinite(under).sum()), 'of', under.size, 'min', np.nanmin(under), 'max', np.nanmax(under))
