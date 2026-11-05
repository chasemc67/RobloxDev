"""Jungle side-view metrics (v10): from each jungle pad's back edge (eye 5.5 above the felt), rays across a 120 deg arc toward the next pad and -12..+12 deg elevation.
fill%  = rays that hit terrain or a dressing item (cylinder approximation) within 200-400 studs.
green% = the first thing a ray hits is green: LeafyGrass/Grass terrain, leaf/fern/vine items, or the crown of a palm (upper 45% of its height).
The pad and its 8-stud clearance are not scored. Sea (below the shoreline) is neither. Rocks, palm trunks and Ground/Sand/Rock terrain count as filled but not green."""
import json, math, os, sys, runpy
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
g = runpy.run_path(f'{ROOT}/source/make_dressing.py')
land = g['land']; sd_pad = g['sd_pad']
ITEMS, KIT, COVER, h2r, ij, pw, PAD_TOP, mat2 = g['ITEMS'], g['KIT'], g['COVER'], g['h2r'], g['ij'], g['pw'], g['PAD_TOP'], g['mat2']
GREEN = ('leafclump', 'fernclump', 'vine_arch', 'vine_strip')
def cyl(it):
    m = it['mesh']; s = it['scale']; H = KIT[m]['size'][1] * s
    if m.startswith('palm'): r = 2.4 * s
    elif m in ('leafclump', 'fernclump'): r = COVER[m] * s * 0.8
    elif m.startswith('rock'): r = COVER[m] * s * 0.9
    elif m in ('vine_arch', 'vine_strip'): r = 6
    else: r = COVER.get(m, 3) * s
    kind = 2 if m.startswith('palm') else 1 if m in GREEN else 0
    return it['x'], it['z'], r, H, kind
C = np.array([cyl(i) for i in ITEMS if i['layer'] != 'Backdrop'])
res = {}; resg = {}; CAT = {}
for n in (10, 11, 12, 13, 14):
    x, z, yw = pw[n]; th = math.radians(yw)
    ex, ez = x - 32 * math.sin(th), z - 32 * math.cos(th)
    ey = PAD_TOP[n] + 5.5
    tot = hit = grn = 0
    near = C[np.hypot(C[:, 0] - ex, C[:, 1] - ez) < 420]
    gh = np.array([h2r[ij(c[0], c[1])] for c in near])
    for da in np.arange(-60, 60.1, 2):
        a = math.radians(yw + da); dx, dz = math.sin(a), math.cos(a)
        for el in np.arange(-12, 12.1, 3):
            te = math.tan(math.radians(el)); t_terr = None; green_t = False
            for t in np.arange(4, 400, 4.0):
                px, pz = ex + dx * t, ez + dz * t; py = ey + te * t
                ii, jj = ij(px, pz)
                if not (0 <= ii < h2r.shape[0] and 0 <= jj < h2r.shape[1]): break
                if py < h2r[ii, jj] and sd_pad[ii, jj] < 8 and t < 60: t_terr = -1; break      # the pad itself and its clearance: not scored
                if py < h2r[ii, jj] and land[ii, jj]: t_terr = t; green_t = int(mat2[ii, jj]) in (2, 6); break
            if t_terr == -1: continue
            tot += 1
            t_item = None; green_i = False
            if len(near):
                rx, rz = near[:, 0] - ex, near[:, 1] - ez
                tproj = rx * dx + rz * dz; perp = np.abs(rx * dz - rz * dx)
                m = (tproj > 2) & (perp < near[:, 2]) & (tproj < (t_terr if t_terr else 220))
                if m.any():
                    idx = np.where(m)[0]; order = idx[np.argsort(tproj[idx])]
                    for q in order:
                        yy = ey + te * tproj[q]; H = near[q, 3]
                        if (yy < gh[q] + H) and (yy > gh[q] - 2):
                            if near[q, 4] == 2 and yy < gh[q] + 0.55 * H: continue      # trunk: filled, handled below
                            t_item = tproj[q]; green_i = near[q, 4] >= 1; break
                    if t_item is None:   # trunks / low hits count as filled, not green
                        for q in order:
                            yy = ey + te * tproj[q]
                            if (yy < gh[q] + near[q, 3]) and (yy > gh[q] - 2): t_item = tproj[q]; green_i = False; break
            if t_item is not None and (t_terr is None or t_item < t_terr): hit += 1; grn += int(green_i); CAT['item_green' if green_i else 'item_other'] = CAT.get('item_green' if green_i else 'item_other', 0) + 1
            elif t_terr is not None: hit += 1; grn += int(green_t); CAT['terr_green' if green_t else 'terr_other'] = CAT.get('terr_green' if green_t else 'terr_other', 0) + 1
            else: CAT['sky'] = CAT.get('sky', 0) + 1
    res[n] = round(100 * hit / tot, 1); resg[n] = round(100 * grn / tot, 1)
print('fill', json.dumps(res), 'mean', round(float(np.mean(list(res.values()))), 1))
print('green', json.dumps(resg), 'mean', round(float(np.mean(list(resg.values()))), 1))
print('categories', {k: round(100 * v / (5 * 61 * 9), 1) for k, v in CAT.items()})
