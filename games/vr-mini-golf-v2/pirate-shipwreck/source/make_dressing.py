"""v9 dressing generator (seeded, deterministic).
Reads  data/heightmap.png, materialmap.png, placements.json, kit_manifest_v1_1.json
Writes data/dressing.json  (item list + metrics)  and  import/dressing_data.json (compact list for the Luau placer)
Run after make_blockout.py.  python3 source/make_dressing.py
"""
import json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'source'))
from layout import CELL, GW, GH, X0, Z0, HMIN, HMAX, CLEAR, REST_SIZE
rng = np.random.default_rng(20261031)
RES = 2.0
NX, NZ = int(GW * CELL / RES), int(GH * CELL / RES)
def cx_(i): return X0 + (i + 0.5) * RES
def ij(x, z): return int((z - Z0) // RES), int((x - X0) // RES)
II, JJ = np.meshgrid(np.arange(NX), np.arange(NZ))
WX = X0 + (II + 0.5) * RES; WZ = Z0 + (JJ + 0.5) * RES

hm = np.asarray(Image.open(f'{ROOT}/data/heightmap.png')).astype(np.float64)
h = HMIN + hm / 65535.0 * (HMAX - HMIN)
h2 = ndi.zoom(h, 2, order=1)              # world-grid heights (heightmap units)
h2r = h2 + 1.97                           # rendered surface bias
mat = np.asarray(Image.open(f'{ROOT}/data/materialmap.png'))
mat2 = np.kron(mat, np.ones((2, 2), dtype=mat.dtype))
land = h2 > 0.8
sd_in = ndi.distance_transform_edt(land) * RES          # distance inland from the shore
sd_out = ndi.distance_transform_edt(~land) * RES        # distance out to sea from land
gz, gx = np.gradient(ndi.gaussian_filter(h2r, 2.0)); slope = np.hypot(gx, gz) / RES

P = json.load(open(f'{ROOT}/data/placements.json'))
M = json.load(open(f'{ROOT}/data/kit_manifest_v1_1.json'))
for _k, _v in json.load(open(f'{ROOT}/data/kit_manifest_v2.json'))['meshes'].items(): M['meshes'].setdefault(_k, _v)   # v12: kit_v2 pieces
for _k, _v in json.load(open(f'{ROOT}/data/kit_manifest_v2_1.json'))['meshes'].items(): M['meshes'][_k] = _v   # v13: kit_v2_1 (canopy_wall, both tiki torches, cliff_ridge) overrides kit_v2
pads = {q['n']: q for q in P['pads']}
ZONE = lambda n: 'wreckcove' if n <= 4 else 'beach' if n <= 9 else 'jungle' if n <= 14 else 'cave'

def rect_sdf(cx, cz, w, l, yaw):
    th = math.radians(yaw); ax = (math.cos(th), -math.sin(th)); az = (math.sin(th), math.cos(th))
    rx = WX - cx; rz = WZ - cz
    u = rx * ax[0] + rz * ax[1]; v = rx * az[0] + rz * az[1]
    qx = np.abs(u) - w / 2; qz = np.abs(v) - l / 2
    return np.hypot(np.maximum(qx, 0), np.maximum(qz, 0)) + np.minimum(np.maximum(qx, qz), 0)

# ---------------------------------------------------------------- kit table
KIT = {}
for k, v in M['meshes'].items():
    if not (isinstance(v, dict) and 'bbox_min' in v): continue
    nm = k.replace('kit_', '')
    bmin = np.array(v['bbox_min']); bmax = np.array(v['bbox_max'])
    KIT[nm] = dict(size=(bmax - bmin), cen=(bmin + bmax) / 2, bmin=bmin, tris=v.get('tris', 0))
def half(n): s = KIT[n]['size']; return max(s[0], s[2]) / 2
HEIGHT = {n: float(KIT[n]['size'][1]) for n in KIT}
LOWMAX = 5.5
# cover radius (what counts as "covered ground") and separation radius per kind
COVER = {'palm_s': 7, 'palm_m': 8, 'palm_l': 9, 'palm_lean_a': 8, 'palm_lean_b': 8, 'rock_s': 5, 'rock_m': 8.5, 'rock_l': 14,
         'leafclump': 11, 'fernclump': 8.5, 'vine_strip': 4, 'planks': 6, 'barrel': 3, 'crate': 4.5, 'rope_coil': 3, 'spar_snapped': 8, 'hull_rib': 9}
SEP = {'palm_s': 4.5, 'palm_m': 5, 'palm_l': 5.5, 'palm_lean_a': 5, 'palm_lean_b': 5, 'rock_s': 4.5, 'rock_m': 7.5, 'rock_l': 13,
       'leafclump': 7, 'fernclump': 5.5, 'planks': 5, 'barrel': 2.6, 'crate': 4, 'rope_coil': 3, 'spar_snapped': 6, 'hull_rib': 7, 'vine_strip': 3}
TALL = lambda n: HEIGHT[n] > LOWMAX

# ---------------------------------------------------------------- exclusion rasters
pw = {n: (pads[n]['pos'][0], pads[n]['pos'][2], pads[n]['yawDeg']) for n in pads}
sd_pad = np.full((NZ, NX), 1e9); pad_id = np.zeros((NZ, NX), dtype=np.int16)
for n, (x, z, yw) in pw.items():
    q = rect_sdf(x, z, CLEAR[0], CLEAR[1], yw)
    m = q < sd_pad; sd_pad[m] = q[m]; pad_id[m] = n
hard = sd_pad <= 0
ho = np.zeros((NZ, NX), bool)      # v11: hard cells that are NOT the pad clearance rect (rest stops, hero props, wreck, cave)
for rs in P['restStops']:
    x, z = rs['pos'][0], rs['pos'][2]
    hard |= (np.abs(WX - x) <= REST_SIZE / 2 + 8) & (np.abs(WZ - z) <= REST_SIZE / 2 + 8)
    ho |= (np.abs(WX - x) <= REST_SIZE / 2 + 8) & (np.abs(WZ - z) <= REST_SIZE / 2 + 8)
HERO_DISC = []
for hp in P['heroProps']:
    x, z = hp['anchor'][0], hp['anchor'][2]; r = max(hp['footprint']['x'], hp['footprint']['z']) / 2 + 8
    HERO_DISC.append((x, z, r)); hard |= np.hypot(WX - x, WZ - z) <= r; ho |= np.hypot(WX - x, WZ - z) <= r
wk = P['heroMeshes'][0]; cv = P['heroMeshes'][1]
wc = np.array([wk['centre'][0], wk['centre'][2]]); sternE = np.array(wk['sternEnd']); bowE = np.array(wk['bowEnd'])
axis = (sternE - bowE) / np.linalg.norm(sternE - bowE)
u_w = (WX - wc[0]) * axis[0] + (WZ - wc[1]) * axis[1]; v_w = -(WX - wc[0]) * axis[1] + (WZ - wc[1]) * axis[0]
wreck_zone = (np.abs(u_w) <= 175) & (np.abs(v_w) <= 48)          # hull footprint + margin
hard |= wreck_zone
ho |= wreck_zone
cave_c = (cv['centre'][0], cv['centre'][2])
hard |= (np.abs(WX - cave_c[0]) <= 135) & (WZ >= cave_c[1] - 80) & (WZ <= cv['frontFaceZ'] + 10)
ho |= (np.abs(WX - cave_c[0]) <= 135) & (WZ >= cave_c[1] - 80) & (WZ <= cv['frontFaceZ'] + 10)
mouthx = cv['mouth']['centreX']
hard |= (np.abs(WX - mouthx) <= 34) & (WZ >= cv['frontFaceZ'] - 5) & (WZ <= cv['frontFaceZ'] + 70)
ho |= (np.abs(WX - mouthx) <= 34) & (WZ >= cv['frontFaceZ'] - 5) & (WZ <= cv['frontFaceZ'] + 70)
# trail lane
tp = np.array(P['trail']['pointsXZ'], float)
dense = []
for a, b in zip(tp[:-1], tp[1:]):
    L = np.linalg.norm(b - a); k = max(1, int(L / 2)); dense += [a + (b - a) * t / k for t in range(k)]
dense.append(tp[-1]); dense = np.array(dense)
for rs in P['restStops']:
    c = np.array([rs['pos'][0], rs['pos'][2]]); j = np.array(rs['joinsTrailAt'])
    L = np.linalg.norm(c - j); k = max(1, int(L / 2)); dense = np.vstack([dense, [j + (c - j) * t / k for t in range(k + 1)]])
# chords pad -> next pad along the course
order = sorted(pads); chord = []
for a, b in zip(order[1:-1], order[2:]):
    A = np.array(pw[a][:2]); B = np.array(pw[b][:2]); L = np.linalg.norm(B - A); k = max(1, int(L / 2))
    chord += [A + (B - A) * t / k for t in range(k + 1)]
chord = np.array(chord)
q = np.stack([WX.ravel(), WZ.ravel()], 1)
dlane = cKDTree(dense).query(q, workers=-1)[0].reshape(NZ, NX)
dchord = cKDTree(chord).query(q, workers=-1)[0].reshape(NZ, NX)
# vine-arch slots: every ~40 studs of arc length along the jungle trail (pads 10..14)
def nearest_idx(p): return int(np.argmin(np.hypot(*(tp - np.array(p)).T)))
ARCHES = []
i10, i14 = nearest_idx(pw[10][:2]), nearest_idx(pw[14][:2])
seg = tp[min(i10, i14):max(i10, i14) + 1]
cum = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(seg, axis=0).T))])
s = 52.0
while s < cum[-1] - 45:
    k = int(np.searchsorted(cum, s)); t = (s - cum[k - 1]) / max(1e-6, cum[k] - cum[k - 1]); p = seg[k - 1] + (seg[k] - seg[k - 1]) * t
    tg = seg[min(k, len(seg) - 1)] - seg[max(k - 2, 0)]; tg = tg / np.linalg.norm(tg)
    ok = all(rect_sd_pt < 1 for rect_sd_pt in [0])
    ARCHES.append((float(p[0]), float(p[1]), float(math.degrees(math.atan2(tg[0], tg[1]))))); s += 20.0
def arch_ok(a):
    x, z, yw = a; i, j = ij(x, z)
    if sd_pad[i, j] < 14 or not land[i, j]: return False
    for r in P['restStops']:
        if math.hypot(x - r['pos'][0], z - r['pos'][2]) < 40: return False
    return True
ARCHES = [a for a in ARCHES if arch_ok(a)]
arch_mask = np.zeros((NZ, NX), bool)
for x, z, yw in ARCHES:
    th = math.radians(yw); tg = (math.sin(th), math.cos(th)); lt = (math.cos(th), -math.sin(th))
    u = (WX - x) * lt[0] + (WZ - z) * lt[1]; v = (WX - x) * tg[0] + (WZ - z) * tg[1]
    arch_mask |= (np.abs(u) <= 23.5) & (np.abs(v) <= 7)
hard_all = hard | arch_mask
ho_all = ho | arch_mask
inner_lane = dlane < 8
no_place = hard_all | inner_lane | ~land            # nothing at all
low_only = (dlane < 16) | (dchord < 12)             # only items <= LOWMAX high
d_none = ndi.distance_transform_edt(~no_place) * RES
d_low = ndi.distance_transform_edt(~(no_place | low_only)) * RES    # distance to nearest cell where tall items are not allowed

# ---------------------------------------------------------------- item store
ITEMS = []          # dict(mesh,x,z,yaw,scale,layer,pad)
IX = np.zeros(0); IZ = np.zeros(0); IR = np.zeros(0); IP = np.zeros(0, bool)
cover = np.zeros((NZ, NX), bool)
def paint(x, z, r):
    i, j = ij(x, z); R = int(r / RES) + 1
    i0, i1, j0, j1 = max(i - R, 0), min(i + R + 1, NZ), max(j - R, 0), min(j + R + 1, NX)
    cover[i0:i1, j0:j1] |= (np.hypot(WX[i0:i1, j0:j1] - x, WZ[i0:i1, j0:j1] - z) <= r)
def free(x, z, r, mesh):
    i, j = ij(x, z)
    if not (0 <= i < NZ and 0 <= j < NX): return False
    if not land[i, j] or no_place[i, j]: return False
    # footprint must not enter forbidden cells (soft: foliage may overlap 25% of radius)
    soft = 0.75 if mesh in ('leafclump', 'fernclump', 'vine_strip') else 0.9
    if d_none[i, j] < r * soft: return False
    if TALL(mesh) and d_low[i, j] < r * 0.8: return False
    if IX.size:
        dd = np.hypot(IX - x, IZ - z)
        lim = (IR + SEP[mesh]) * (np.where(IP, 0.52, 1.0) if mesh.startswith('palm') else 1.0)     # palms in a clump stand close (crowns overlap)
        if np.any(dd < lim): return False
    return True
def add(mesh, x, z, yaw, scale, layer, force=False):
    global IX, IZ, IR, IP
    r = SEP[mesh] * scale
    if not force and not free(x, z, r, mesh): return False
    ITEMS.append(dict(mesh=mesh, x=round(float(x), 2), z=round(float(z), 2), yaw=round(float(yaw), 1), scale=round(float(scale), 3), layer=layer,
                      pad=int(pad_id[ij(x, z)]) if (0 <= ij(x, z)[0] < NZ and 0 <= ij(x, z)[1] < NX) else 0))
    IX = np.append(IX, x); IZ = np.append(IZ, z); IR = np.append(IR, r); IP = np.append(IP, mesh.startswith('palm'))
    paint(x, z, COVER[mesh] * scale * (0.9 if mesh not in ('barrel',) else 1)); return True
def ang(): return float(rng.uniform(0, 360))
def tint_of(x, z):
    i, j = ij(x, z); return int(mat2[i, j])
def inb(i, j): return 0 <= i < NZ and 0 <= j < NX

# ---------------------------------------------------------------- 0. arches (reserved first)   (v10: one slot every ~26 studs instead of 40)
LAYER_ARCH = 'Arches'
for x, z, yw in ARCHES:
    ITEMS.append(dict(mesh='vine_arch', x=round(x, 2), z=round(z, 2), yaw=round(yw, 1), scale=1.0, layer=LAYER_ARCH, pad=int(pad_id[ij(x, z)])))

# ---------------------------------------------------------------- helpers: field directions
gl_z, gl_x = np.gradient(ndi.gaussian_filter(dlane, 3.0))
gs_z, gs_x = np.gradient(ndi.gaussian_filter(sd_in, 3.0))
def dir_to_lane(x, z):
    i, j = ij(x, z); v = np.array([-gl_x[i, j], -gl_z[i, j]]); n = np.linalg.norm(v); return v / n if n > 1e-6 else None
def dir_to_sea(x, z):
    i, j = ij(x, z); v = np.array([-gs_x[i, j], -gs_z[i, j]]); n = np.linalg.norm(v); return v / n if n > 1e-6 else None
def sdpad_at(x, z): i, j = ij(x, z); return sd_pad[i, j]
def crown_ok(cx, cz, rc):
    i, j = ij(cx, cz)
    if not inb(i, j): return False
    return sd_pad[i, j] >= rc * 0.95 and dlane[i, j] >= 9 and dchord[i, j] >= 6 and not hard_all[i, j]
def lean_palm(x, z, sc, layer):
    """one leaning palm: leans over the trail or the water, never across a putting line (crown must clear every pad rect, the lane and the chords)"""
    i, j = ij(x, z); dirs = []
    if dlane[i, j] < 70:
        d = dir_to_lane(x, z)
        if d is not None: dirs.append(d)
    if sd_in[i, j] < 90:
        d = dir_to_sea(x, z)
        if d is not None: dirs.append(d)
    pid = int(pad_id[i, j])
    if pid:
        a = np.array([x - pw[pid][0], z - pw[pid][1]]); n_ = np.linalg.norm(a)
        if n_ > 1e-6: dirs.append(a / n_)
    for d in dirs:
        for _t in range(3):
            dd = d + rng.normal(0, 0.15, 2); dd /= np.linalg.norm(dd)
            if rng.random() < 0.5: nm, yw, reach = 'palm_lean_a', math.degrees(math.atan2(dd[0], dd[1])), 17.0 * sc
            else: nm, yw, reach = 'palm_lean_b', math.degrees(math.atan2(-dd[1], dd[0])), 15.0 * sc
            if crown_ok(x + dd[0] * reach, z + dd[1] * reach, 8.0 * sc) and add(nm, x, z, yw, sc, layer): return nm
    return None
def upright_palm(x, z, size, layer):
    sc = float(rng.uniform(0.85, 1.2)); nm = {'s': 'palm_s', 'm': 'palm_m', 'l': 'palm_l'}[size]
    if size == 'l': sc = float(rng.uniform(1.0, 1.25))
    if crown_ok(x, z, COVER[nm] * 0.8) and add(nm, x, z, ang(), sc, layer): return nm
    return None
def rock_at(x, z, layer, size=None):
    nm = size or ('rock_s' if rng.random() < 0.55 else 'rock_m'); sc = float(rng.uniform(0.8, 1.3))
    return add(nm, x, z, ang(), sc, layer)
PALMS = []          # (x, z, n palms) per clump
CLUMPS = []         # centres of every palm clump (open gaps between them)
def palm_clump(cx0, cz0, layer, big=False, k=None):
    """tight clump: 3-5 palms = one leaning palm + mixed s/m/l (big=True: mostly l and m), a rock and a clump of leaves at the foot"""
    k = int(k or rng.integers(3, 5))
    sizes = list(rng.permutation(['l', 'm', 'l', 'm'] if big else ['l', 'm', 's', 'm']))[:k - 1]
    if not big and 's' not in sizes and k >= 4: sizes[-1] = 's'
    placed = 0
    for _t in range(8):
        a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(0, 3.5)
        if lean_palm(cx0 + rr * math.cos(a), cz0 + rr * math.sin(a), float(rng.uniform(0.9, 1.2)), layer): placed += 1; break
    a0 = rng.uniform(0, 2 * math.pi)
    for q_, sz in enumerate(sizes):
        for _t in range(10):
            a = a0 + q_ * 2 * math.pi / max(len(sizes), 1) + rng.uniform(-0.5, 0.5); rr = rng.uniform(4.5, 9.0)
            if upright_palm(cx0 + rr * math.cos(a), cz0 + rr * math.sin(a), sz, layer): placed += 1; break
    if placed == 0: return 0
    CLUMPS.append((cx0, cz0)); PALMS.append((cx0, cz0, placed))
    a = rng.uniform(0, 2 * math.pi)
    for _t in range(8):
        rr = rng.uniform(6, 13); a += 0.8
        if rock_at(cx0 + rr * math.cos(a), cz0 + rr * math.sin(a), layer, 'rock_m' if rng.random() < .5 else 'rock_s'): break
    for _t in range(6):
        rr = rng.uniform(7, 14); a += 1.3
        if add('leafclump' if rng.random() < .6 else 'fernclump', cx0 + rr * math.cos(a), cz0 + rr * math.sin(a), ang(), 1.0, layer): break
    return placed
def centre_ok(x, z, rmin=11.0, gap=0.0):
    i, j = ij(x, z)
    if not inb(i, j) or not land[i, j] or no_place[i, j] or d_none[i, j] < rmin or d_low[i, j] < rmin: return False
    if gap and CLUMPS and min(math.hypot(x - a, z - b) for a, b in CLUMPS) < gap: return False
    return True

# per zone fill weights (no palms: palms only come in clumps) and per mesh scale ranges (jungle leaves are big: 1.5-2x)
ZW = {'wreckcove': [('fernclump', .32), ('leafclump', .30), ('rock_s', .20), ('rock_m', .18)],
      'beach':     [('fernclump', .32), ('leafclump', .30), ('rock_s', .20), ('rock_m', .18)],
      'jungle':    [('leafclump', .80), ('fernclump', .06), ('rock_m', .08), ('rock_s', .06)],
      'cave':      [('rock_m', .28), ('rock_l', .10), ('rock_s', .14), ('fernclump', .20), ('leafclump', .28)]}
SCALE_R = {'jungle': {'leafclump': (1.5, 2.0), 'fernclump': (1.1, 1.5), 'rock_m': (0.9, 1.4), 'rock_s': (0.9, 1.3)},
           'cave': {'leafclump': (1.1, 1.6), 'fernclump': (1.0, 1.4)}, 'beach': {'leafclump': (1.0, 1.5), 'fernclump': (1.0, 1.4)},
           'wreckcove': {'leafclump': (1.0, 1.5), 'fernclump': (1.0, 1.4)}}
def pick(zone, lowonly=False, big=False):
    ops = [(k, w) for k, w in ZW[zone] if (not lowonly or not TALL(k)) and (not big or k in ('rock_l', 'rock_m', 'leafclump'))]
    if not ops: ops = [('rock_m', .5), ('fernclump', .5)]
    ks = [k for k, _ in ops]; ws = np.array([w for _, w in ops]); return ks[int(rng.choice(len(ks), p=ws / ws.sum()))]
def fscale(zone, nm, lowonly=False):
    lo, hi = SCALE_R.get(zone, {}).get(nm, (0.85, 1.3))
    if lowonly and nm in ('fernclump', 'leafclump'): lo, hi = 0.85, 1.05
    return float(rng.uniform(lo, hi))

# ---------------------------------------------------------------- 1. per pad set pieces
RIM_TORCH_U_PAD = {1: 21.0}   # v20: pad 1 stands on the wreck deck; |u| 24 is outside the hull (torch sunk into the hull side). 21.0 is a first value, verified / tuned in Studio
RIM_TORCH_U = 24.0   # v19: rim torches stand 5 studs outside the rim's outer edge (|u| 19), clear of the rail (v16-v18 had them at 15.8 = on the rail)
def to_world(n, u, v):
    x, z, yw = pw[n]; th = math.radians(yw)
    return (x + u * math.cos(th) + v * math.sin(th), z - u * math.sin(th) + v * math.cos(th))
DROP = {}   # pad -> sign of lateral drop side (lower ground)
for n in range(2, 19):
    vals = []
    for sgn in (-1, 1):
        px, pz = to_world(n, sgn * 46, 0); i, j = ij(px, pz); vals.append(h2[i, j])
    DROP[n] = -1 if vals[0] < vals[1] else 1
DROP[13] = -1

# ================================================================ v11 helpers
ridge = h2r - ndi.gaussian_filter(h2r, 22)            # local high ground: tree-line clumps sit on these
WALK = []                                             # boardwalk planks ['bw', x, z, yaw, length, width] and stepping stones ['st', x, z, yaw, diameter, 0] (Parts, no scripts)
LANT = []                                             # lantern placeholders (pad rim corners and the cave mouth)
SET_PIECES = {}
def pad_uv_arr(n):
    x, z, yw = pw[n]; th = math.radians(yw); rx = WX - x; rz = WZ - z
    return rx * math.cos(th) - rz * math.sin(th), rx * math.sin(th) + rz * math.cos(th)
def ok_hero(x, z):
    return all(math.hypot(x - hx, z - hz) >= hr for hx, hz, hr in HERO_DISC)
def fadd(mesh, x, z, yaw, sc, layer, minlane=8.5, sepk=0.5):
    """forced add (may sit inside the pad clearance ring) with its own checks: land, not wreck/cave/rest/hero, out of the lane, tall items not on the chord"""
    i, j = ij(x, z)
    if not inb(i, j) or not land[i, j] or ho_all[i, j] or dlane[i, j] < minlane or not ok_hero(x, z): return False
    if TALL(mesh) and low_only[i, j] and dlane[i, j] < 16: return False
    if IX.size:
        dd = np.hypot(IX - x, IZ - z)
        if np.any(dd < (IR + SEP[mesh] * sc) * sepk): return False
    return add(mesh, x, z, yaw, sc, layer, force=True)
def tee_approach(n):
    """short boardwalk (3 x 8.2 studs) then 5 stepping stones from the pad's tee rim, ferns and small rocks on both sides"""
    OL = 68.0; yw = pw[n][2]; nb = 0
    for k in range(3):
        v = -OL / 2 - 1.0 - 4.1 - k * 8.4; x, z = to_world(n, 0, v); i, j = ij(x, z)
        if inb(i, j) and land[i, j] and not ho_all[i, j]: WALK.append(['bw', round(x, 2), round(z, 2), round(yw, 1), 8.2, 6.5]); nb += 1
    for k in range(5):
        v = -OL / 2 - 1.0 - 3 * 8.4 - 3.5 - k * 5.4; x, z = to_world(n, float(rng.uniform(-1.3, 1.3)), v); i, j = ij(x, z)
        if inb(i, j) and land[i, j] and not ho_all[i, j]: WALK.append(['st', round(x, 2), round(z, 2), round(ang(), 1), round(float(rng.uniform(3.6, 4.8)), 2), 0]); nb += 1
    v = -OL / 2 - 3.0; nf = 0
    while v > -OL / 2 - 82:
        for sgn in (-1, 1):
            x, z = to_world(n, sgn * float(rng.uniform(8.8, 10.6)), v + float(rng.uniform(-1.5, 1.5)))
            nm = 'fernclump' if rng.random() < 0.55 else 'rock_s'
            if fadd(nm, x, z, ang(), float(rng.uniform(0.85, 1.15)), 'Front', 8.4, 0.5): nf += 1
            if rng.random() < 0.6:
                x, z = to_world(n, sgn * float(rng.uniform(15.5, 19.0)), v + float(rng.uniform(-2, 2)))
                nm = 'fernclump' if rng.random() < 0.5 else 'rock_s'
                if fadd(nm, x, z, ang(), float(rng.uniform(0.9, 1.2)), 'Front', 8.4, 0.5): nf += 1
        v -= float(rng.uniform(5.0, 6.5))
    return nb, nf
def overhead_jungle(n):
    """pads 10-14: 3 tall palms lean in from both sides so the fronds overlap above the pad, plus one vine arch spanning the pad"""
    W, L = CLEAR; th = math.radians(pw[n][2]); got = 0
    for sgn, v0 in ((-1, 8), (1, 18), (int(rng.choice([-1, 1])), 34)):
        for _t in range(10):
            u = sgn * (W / 2 + float(rng.uniform(1.5, 5.5))); x, z = to_world(n, u, v0 + float(rng.uniform(-5, 5))); sc = float(rng.uniform(1.4, 1.6))
            dd = np.array([-sgn * math.cos(th), sgn * math.sin(th)])
            if fadd('palm_lean_a', x, z, math.degrees(math.atan2(dd[0], dd[1])), sc, 'Front', 10.0, 0.5): got += 1; break
    ax, az = to_world(n, 0, -8)
    ITEMS.append(dict(mesh='vine_arch', x=round(ax, 2), z=round(az, 2), yaw=round(pw[n][2], 1), scale=1.1, layer='Arches', pad=n))
    return got
def pad_lantern(n):
    sg = -DROP.get(n, -1); x, z = to_world(n, sg * 17.0, -31.0)
    LANT.append(dict(kind='rim', pad=n, x=round(x, 2), z=round(z, 2)))
RING_N = {}
def pad_ring(n, zone):
    """v10: a fern or leaf clump plus a rock every 6-8 studs, centred just outside the 8-stud clearance edge (nearest part touches the edge).
    Stations stay out of the trail lane and the pad-to-pad chord, so the tee-to-cup line and the pad-to-pad view stay open."""
    W, L = CLEAR; jung = zone == 'jungle'; cnt = 0
    sides = [((-W / 2, -L / 2), (1, 0), (0, -1), W), ((W / 2, -L / 2), (0, 1), (1, 0), L), ((W / 2, L / 2), (-1, 0), (0, 1), W), ((-W / 2, L / 2), (0, -1), (-1, 0), L)]
    def station(u, v, nrm_, kind, along):
        nonlocal cnt
        wx, wz = to_world(n, u, v); i, j = ij(wx, wz)
        if not inb(i, j) or not land[i, j] or no_place[i, j] or dlane[i, j] < 10 or dchord[i, j] < 9: return
        lowo = bool(low_only[i, j])
        if kind == 'clump':
            nm = 'leafclump' if (jung or rng.random() < .5) else 'fernclump'
            if lowo and nm == 'leafclump': nm = 'fernclump'
            sc = float(rng.uniform(0.8, 1.15)) if not lowo else float(rng.uniform(0.8, 1.0))
        else:
            nm = ('rock_s' if rng.random() < (0.7 if jung else 0.5) else 'rock_m')
            if lowo: nm = 'rock_s'
            sc = float(rng.uniform(0.8, 1.2))
        e = 0.5 * max(KIT[nm]['size'][0], KIT[nm]['size'][2]) * sc * 0.8
        wx, wz = to_world(n, u + nrm_[0] * e, v + nrm_[1] * e)
        if add(nm, wx, wz, ang(), sc, 'Front', force=True): cnt += 1
    for (su, sv), (du, dv), nrm_, Ls in sides:
        t = float(rng.uniform(0, 3))
        while t < Ls:
            station(su + du * t, sv + dv * t, nrm_, 'clump', t)
            station(su + du * (t + 3.5 + rng.uniform(-0.6, 0.6)), sv + dv * (t + 3.5 + rng.uniform(-0.6, 0.6)), nrm_, 'rock', t)
            t += float(rng.uniform(6, 8))
    return cnt
V11 = dict(tee={}, overhead={})
for n in range(2, 19):
    V11['tee'][n] = tee_approach(n)
    if 10 <= n <= 14: V11['overhead'][n] = overhead_jungle(n)
for n in (1, 5, 10, 15, 18): pad_lantern(n)
LANT.append(dict(kind='mouth', pad=0, x=round(mouthx + 17.0, 2), z=round(cv['frontFaceZ'] + 9.0, 2)))
for n in range(2, 19):
    RING_N[n] = pad_ring(n, ZONE(n))
for n in range(2, 19):
    zone = ZONE(n); lay = 'Front'; sg = DROP[n]
    # (a) rocks at the drop-off edge (second row, just outside the ring)
    for v in (-34, -12, 12, 34):
        r = float(rng.uniform(0.9, 1.4)); nm = 'rock_m' if rng.random() < 0.6 else 'rock_s'
        off = CLEAR[0] / 2 + 14 + SEP[nm] * r * 0.6
        wx, wz = to_world(n, off * sg, v + rng.uniform(-4, 4)); add(nm, wx, wz, ang(), r, lay)
    # (b) palm clumps right behind the pad as a backdrop: big palms, far end (+Z) left and right of the trail lane, the tee end, and one on the side
    W, L = CLEAR
    slots = [(-1, 'far'), (1, 'far'), (rng.choice([-1, 1]), 'side')]      # v11: no big palms at the tee end (the camera stands there; foreground clutter instead)
    for sgn, kind in slots:
        for _t in range(18):
            if kind == 'far': u = sgn * rng.uniform(24, 36); v = L / 2 + rng.uniform(12, 30) + _t * 1.5
            elif kind == 'tee': u = sgn * rng.uniform(24, 36); v = -L / 2 - rng.uniform(12, 28) - _t * 1.5
            else: u = sgn * (W / 2 + rng.uniform(16, 26) + _t); v = rng.uniform(-14, 26)
            wx, wz = to_world(n, u, v)
            if centre_ok(wx, wz, 11.0, gap=30.0):
                if palm_clump(wx, wz, 'Mid', big=True): break
    # (c) v11 tree line: clumps chained off the existing clumps (26-42 studs apart) on ridges, so the far palms read as a continuous tree line, not a sprinkle
    nextra = {'wreckcove': 2, 'beach': 2, 'jungle': 3, 'cave': 1}[zone]
    for _ in range(nextra):
        best = None
        for relax in (0.8, -0.5, -99):
            for _t in range(300):
                a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(45, 150)
                px, pz = pw[n][0] + math.cos(a) * rr, pw[n][1] + math.sin(a) * rr
                i, j = ij(px, pz)
                if not inb(i, j) or ridge[i, j] < relax or not centre_ok(px, pz, 11.0): continue
                dm = min([math.hypot(px - cx2, pz - cz2) for cx2, cz2 in CLUMPS] + [999])
                if 26 <= dm <= 42: best = (px, pz); break
            if best: break
        if best: palm_clump(best[0], best[1], 'Mid')


# ---------------------------------------------------------------- 1b. v11 set pieces (placeholders for kit_v2), skyline silhouettes
def rock_pile(n, cu, cv_):
    got = 0
    for nm, du, dv, sc in (('rock_l', 0, 0, 1.9), ('rock_l', -24, 10, 1.35), ('rock_l', 22, -8, 1.45), ('rock_m', -8, -22, 1.7), ('rock_m', 12, 24, 1.6)):
        x, z = to_world(n, cu + du, cv_ + dv)
        if fadd(nm, x, z, ang(), sc * float(rng.uniform(0.92, 1.08)), 'Set', 12.0, 0.4): got += 1
    for k in range(3):
        a = rng.uniform(0, 2 * math.pi); rr = float(rng.uniform(26, 36)); x, z = to_world(n, cu + rr * math.cos(a), cv_ + rr * math.sin(a))
        if fadd('palm_m' if k < 2 else 'palm_l', x, z, ang(), float(rng.uniform(1.1, 1.35)), 'Set', 14.0, 0.45): got += 1
    for k in range(3):
        a = rng.uniform(0, 2 * math.pi); rr = float(rng.uniform(20, 34)); x, z = to_world(n, cu + rr * math.cos(a), cv_ + rr * math.sin(a))
        if fadd('leafclump', x, z, ang(), float(rng.uniform(1.5, 1.9)), 'Set', 12.0, 0.45): got += 1
    return got
def debris_stack(n, cu, cv_):
    got = 0
    for nm, du, dv, sc in (('hull_rib', 0, 0, 2.3), ('hull_rib', 15, 7, 1.9), ('planks', -12, 4, 2.6), ('planks', 9, -12, 2.2), ('spar_snapped', -18, -6, 2.4), ('spar_snapped', 20, -10, 2.0),
                           ('barrel', -5, 10, 2.0), ('barrel', 6, 14, 1.8), ('crate', -14, -14, 2.2), ('crate', 2, -6, 2.0), ('rope_coil', 8, 5, 2.2), ('barrel', -2, -16, 1.9)):
        x, z = to_world(n, cu + du, cv_ + dv)
        if fadd(nm, x, z, ang() if nm != 'hull_rib' else pw[n][2] + 90 + float(rng.uniform(-20, 20)), sc * float(rng.uniform(0.94, 1.06)), 'Set', 12.0, 0.3): got += 1
    for k in range(3):
        a = rng.uniform(0, 2 * math.pi); rr = float(rng.uniform(16, 26)); x, z = to_world(n, cu + rr * math.cos(a), cv_ + rr * math.sin(a))
        if fadd('fernclump', x, z, ang(), float(rng.uniform(1.3, 1.6)), 'Set', 12.0, 0.4): got += 1
    return got
for n in range(2, 19):
    sgn = -DROP[n]; got = 0; kind = 'debris' if (n <= 9 and n % 2 == 1) else 'rocks'
    for sg2 in (sgn, -sgn):
        for _t in range(8):
            cu = sg2 * float(rng.uniform(76, 90)); cv_ = float(rng.uniform(-12, 24))
            x, z = to_world(n, cu, cv_); i, j = ij(x, z)
            if not inb(i, j) or not land[i, j] or ho_all[i, j] or dlane[i, j] < 30: continue
            got = (debris_stack if kind == 'debris' else rock_pile)(n, cu, cv_)
            if got >= 4: break
        if got >= 4: break
    SET_PIECES[n] = (kind, got)

def out_dist_at(x, z):
    i, j = ij(x, z)
    if not (0 <= i < NZ and 0 <= j < NX): return -1
    return float(sd_out[i, j]) if not land[i, j] else -1
SKY_STACKS = []
BACK = []
def sky_stack(n, offs):
    x0, z0, yw = pw[n]; th0 = math.radians(yw); a_f = math.atan2(math.cos(th0), math.sin(th0)); ng = 0
    for off in offs:
        a = a_f + math.radians(off)
        for dist in np.arange(420, 1000, 20):
            x, z = x0 + math.cos(a) * dist, z0 + math.sin(a) * dist
            if abs(x) > 2048 - 200 or abs(z) > 1280 - 200: break
            if out_dist_at(x, z) < 140: continue
            nm = ('stack_a', 'stack_b', 'stack_c')[int(rng.integers(3))]
            if min([math.hypot(x - q[0], z - q[1]) for q in SKY_STACKS] + [999]) >= 170 and min([math.hypot(x - q[1], z - q[2]) for q in BACK] + [999]) >= 260:
                sc = float(np.clip(math.tan(math.radians(rng.uniform(9, 15))) * dist / HEIGHT[nm], 0.22, 0.9))
                SKY_STACKS.append((x, z)); ng += 1
                ITEMS.append(dict(mesh=nm, x=round(x, 1), z=round(z, 1), yaw=round(ang(), 1), scale=round(sc, 3), layer='Skyline', pad=n))
            break
    return ng
def sky_rocks(n, cnt, vmin, vmax, scl, umax=110):
    L = CLEAR[1]; got = 0
    for _ in range(cnt):
        for _t in range(60):
            u = float(rng.uniform(-umax, umax)); v = float(rng.uniform(vmin, vmax)); x, z = to_world(n, u, v); i, j = ij(x, z)
            if not inb(i, j) or not land[i, j] or ho_all[i, j] or dlane[i, j] < 28 or dchord[i, j] < 20 or sd_pad[i, j] < 30: continue
            if fadd('rock_l', x, z, ang(), float(rng.uniform(*scl)), 'Skyline', 28.0, 0.45): got += 1; break
    return got
def canopy_wall(n, back=False):
    """tall palm_l (1.5-1.9x) and 2.5-3.2x leaf clumps in a band 35-95 studs behind the pad (or behind the tee for the back view)"""
    L = CLEAR[1]; sv = -1 if back else 1; got = 0
    for nm, cnt, lo, hi in (('palm_l', 6 if not back else 4, 1.5, 1.9), ('leafclump', 8 if not back else 5, 2.5, 3.2)):
        for _ in range(cnt):
            for _t in range(40):
                u = float(rng.uniform(-70, 70)); v = sv * (L / 2 + float(rng.uniform(35, 95))); x, z = to_world(n, u, v)
                if add(nm, x, z, ang(), float(rng.uniform(lo, hi)), 'Skyline'): got += 1; break
    return got
SKY = {}
for n in range(2, 19):
    z_ = ZONE(n)
    if z_ in ('wreckcove', 'beach'):
        SKY[n] = dict(rocks=sky_rocks(n, 2, CLEAR[1] / 2 + 60, CLEAR[1] / 2 + 200, (3.2, 4.4)) + sky_rocks(n, 1, -CLEAR[1] / 2 - 200, -CLEAR[1] / 2 - 60, (3.2, 4.4)))
    elif z_ == 'jungle':
        SKY[n] = dict(canopy=canopy_wall(n) + canopy_wall(n, True))
    else:
        SKY[n] = dict(rocks=sky_rocks(n, 3, CLEAR[1] / 2 + 50, CLEAR[1] / 2 + 170, (3.5, 5.2)) + sky_rocks(n, 2, -CLEAR[1] / 2 - 170, -CLEAR[1] / 2 - 50, (3.5, 5.2)))
# pad 15: cave rock pulled in as a backdrop (rock_l 5-6x behind the far end), rocks and plants over the cliff edge, hanging vines and a big rock on the drop side
SKY[15]['caveRocks'] = sky_rocks(15, 3, CLEAR[1] / 2 + 70, CLEAR[1] / 2 + 150, (5.0, 6.2), 90)
P15V11 = dict(edge=0, vines=0, bigRock=False)
sg15 = DROP[15]; th15 = math.radians(pw[15][2])
for k, v in enumerate(range(-36, 37, 6)):
    nm = ('leafclump', 'fernclump', 'rock_s', 'fernclump', 'rock_m', 'leafclump')[k % 6]
    x, z = to_world(15, sg15 * (19.5 + float(rng.uniform(2.0, 5.0))), v + float(rng.uniform(-1.5, 1.5)))
    if fadd(nm, x, z, ang(), float(rng.uniform(0.95, 1.25)), 'Front', 6.0, 0.4): P15V11['edge'] += 1
for v in (-22, 6, 30):
    nx, nz = sg15 * math.cos(th15), -sg15 * math.sin(th15); x, z = to_world(15, sg15 * 21.0, v)
    ITEMS.append(dict(mesh='vine_strip', x=round(x, 2), z=round(z, 2), yaw=round(math.degrees(math.atan2(nx, nz)), 1), scale=1.15, layer='Hang', pad=15)); P15V11['vines'] += 1
for off in (44, 52, 60):
    x, z = to_world(15, sg15 * off, -4)
    if fadd('rock_l', x, z, ang(), 1.5, 'Front', 12.0, 0.35): P15V11['bigRock'] = True; break

# ---------------------------------------------------------------- 2. gap fill (farthest-point), per pad
def zone_need(n, reach):
    return (sd_pad <= reach) & (pad_id == n) & land & ~(hard | wreck_zone)
def fill(n, reach, target, layer, big=False, lanes_low=True, maxit=500, need=None, low=False):
    need0 = zone_need(n, reach) if need is None else need
    x, z, _ = pw[n]
    i0, j0 = ij(x, z); R = int((reach + 60) / RES)
    sl = (slice(max(i0 - R, 0), min(i0 + R, NZ)), slice(max(j0 - R, 0), min(j0 + R, NX)))
    bad = np.zeros_like(need0[sl]); added = 0
    for it in range(maxit):
        nd = need0[sl] & ~bad[...]
        E = ndi.distance_transform_edt(nd & ~cover[sl]) * RES
        k = int(np.argmax(E)); iy, ix = divmod(k, E.shape[1])
        if E[iy, ix] <= target: break
        gi, gj = iy + sl[0].start, ix + sl[1].start
        px, pz = cx_(gj), Z0 + (gi + 0.5) * RES
        zone = ZONE(n); ok = False
        lowonly = bool(low_only[gi, gj])
        for _t in range(7):
            if low:
                nm = 'fernclump' if rng.random() < 0.55 else 'rock_s'; ok = add(nm, px, pz, ang(), float(rng.uniform(0.9, 1.25)), layer)
            else:
                nm = pick(zone, lowonly, big)
                ok = add(nm, px, pz, ang(), fscale(zone, nm, lowonly), layer)
            if ok: added += 1; break
        if not ok:
            bad[max(iy - 3, 0):iy + 4, max(ix - 3, 0):ix + 4] = True
    return added
FILL_LOG = {}
T_NEAR = {'jungle': 7.5, 'cave': 10, 'beach': 10, 'wreckcove': 10}
T_FAR = {'jungle': 16.0, 'cave': 24, 'beach': 24, 'wreckcove': 24}
FG_T = {'jungle': 7.0, 'cave': 7.0, 'beach': 7.0, 'wreckcove': 7.0}
def fg_need(n):
    """foreground: 26 studs round the pad clearance rect on all four sides plus the tee side 78 studs back (what the VR camera sees first)"""
    W, L = CLEAR; u, v = pad_uv_arr(n)
    reg = (sd_pad <= 26) | ((np.abs(u) < 46) & (v < -L / 2) & (v > -L / 2 - 78))
    return reg & (sd_pad > 0) & land & ~ho_all & (np.hypot(WX - pw[n][0], WZ - pw[n][1]) < 140)
def edge_need(n):
    """trail edges: the 8-16 stud band beside the lane within 105 studs of the pad (the lane itself stays empty)"""
    return (dlane >= 8) & (dlane <= 15.5) & land & ~ho_all & (sd_pad > 0) & (np.hypot(WX - pw[n][0], WZ - pw[n][1]) < 105)
FG_LOG = {}
for n in range(2, 19):
    z = ZONE(n)
    f1 = fill(n, 100, FG_T[z], 'Front', need=fg_need(n), low=True)
    f2 = fill(n, 100, 2.4, 'Front', need=edge_need(n), low=True)
    a1 = fill(n, 90, T_NEAR[z], 'Fill')
    a2 = fill(n, 190, T_FAR[z], 'Far', big=True)
    FILL_LOG[n] = (a1, a2); FG_LOG[n] = (f1, f2)

# ---------------------------------------------------------------- 2b. bare patches: a rock cluster and two palm clumps in every patch wider than 30 studs (trail lane excluded)
PATCHES = []
need_all = np.zeros((NZ, NX), bool)
for n in range(2, 19): need_all |= zone_need(n, 100)
need_all &= ~inner_lane
bad_p = np.zeros((NZ, NX), bool)
for _it in range(120):
    E = ndi.distance_transform_edt(need_all & ~cover & ~bad_p) * RES
    k = int(np.argmax(E)); iy, ix = divmod(k, NX)
    if E[iy, ix] <= 15.0: break
    px, pz = cx_(ix), Z0 + (iy + 0.5) * RES; diam = 2 * float(E[iy, ix])
    got = 0
    if add('rock_l', px, pz, ang(), float(rng.uniform(0.9, 1.2)), 'Fill'): got += 1
    else: got += int(add('rock_m', px, pz, ang(), float(rng.uniform(1.0, 1.3)), 'Fill'))
    a0 = rng.uniform(0, 2 * math.pi)
    for q_ in range(3):
        for _t in range(6):
            a = a0 + q_ * 2.1 + _t * 0.4; rr = rng.uniform(10, 16)
            if add('rock_m' if q_ < 2 else 'rock_s', px + rr * math.cos(a), pz + rr * math.sin(a), ang(), float(rng.uniform(0.9, 1.3)), 'Fill'): got += 1; break
    npc = 0
    for q_ in range(1):
        for _t in range(10):
            a = a0 + math.pi * q_ + rng.uniform(-0.4, 0.4); rr = rng.uniform(13 + _t, 19 + _t)
            cxp, czp = px + rr * math.cos(a), pz + rr * math.sin(a)
            if centre_ok(cxp, czp, 9.0, gap=22.0) and palm_clump(cxp, czp, 'Mid'): npc += 1; break
    PATCHES.append(dict(x=round(px, 1), z=round(pz, 1), diameter=round(diam, 1), rocks=got, palmClumps=npc))
    if got + npc == 0: bad_p[max(iy - 4, 0):iy + 5, max(ix - 4, 0):ix + 5] = True
    elif not cover[iy, ix]: bad_p[max(iy - 3, 0):iy + 4, max(ix - 3, 0):ix + 4] = True

# ---------------------------------------------------------------- 2c. v11: bare / brown ground (rock or dirt material, or still uncovered) gets 2x leaf clumps
BROWN = 0
brown_m = land & ~ho_all & ~inner_lane & (dlane > 14) & (slope < 0.8) & np.isin(mat2, (2, 3, 5, 6)) & (sd_in > 10) & ~hard_all
for _it in range(160):
    E = ndi.distance_transform_edt(brown_m & ~cover) * RES
    k = int(np.argmax(E)); iy, ix = divmod(k, NX)
    if E[iy, ix] <= 24.0: break
    px, pz = cx_(ix), Z0 + (iy + 0.5) * RES
    if add('leafclump', px, pz, ang(), float(rng.uniform(1.9, 2.1)), 'Far'): BROWN += 1
    else:
        brown_m[max(iy - 4, 0):iy + 5, max(ix - 4, 0):ix + 5] = False

# ---------------------------------------------------------------- 3. debris groups (tide line + near the wreck) and hull ribs
tide = land & (sd_in > 2) & (sd_in < 14) & ~hard_all & ~inner_lane & (dlane > 14)
def debris_group(cx0, cz0, layer='Debris'):
    k = int(rng.integers(3, 6)); names = ['planks', 'barrel', 'crate', 'rope_coil', 'spar_snapped', 'planks', 'barrel']
    ok = 0
    for _ in range(k):
        for _t in range(14):
            a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(2, 11)
            nm = names[int(rng.integers(len(names)))]
            if add(nm, cx0 + rr * math.cos(a), cz0 + rr * math.sin(a), ang(), float(rng.uniform(0.9, 1.3)), layer): ok += 1; break
    return ok
def tide_pts(cen, rad, cnt, sep=40):
    d = np.hypot(WX - cen[0], WZ - cen[1]); idx = np.argwhere(tide & (d < rad)); out = []
    if len(idx) == 0: return out
    for _ in range(cnt):
        best, bd = None, -1
        for _t in range(60):
            i, j = idx[int(rng.integers(len(idx)))]; p = (cx_(j), Z0 + (i + .5) * RES)
            dm = min([math.hypot(p[0] - q[0], p[1] - q[1]) for q in out] + [99]) if out else 99
            if dm > bd: bd, best = dm, p
        if best and bd >= sep: out.append(best)
    return out
DEBRIS_G = 0
for p in tide_pts(sternE, 120, 4, 35) + tide_pts(wc, 260, 6, 45):
    if debris_group(*p): DEBRIS_G += 1
for n in range(2, 10):
    for p in tide_pts(pw[n][:2], 170, 1, 0):
        if debris_group(*p): DEBRIS_G += 1
# hull ribs: half-buried in the sand west of the wreck
RIBS = 0
west = tide & (WX < wc[0] - 60) & (np.hypot(WX - wc[0], WZ - wc[1]) < 520)
idx = np.argwhere(west)
if len(idx) == 0:
    west = tide & (np.hypot(WX - bowE[0], WZ - bowE[1]) < 420); idx = np.argwhere(west)
rib_pts = []
if len(idx):
    for _ in range(5):
        best, bd = None, -1
        for _t in range(80):
            i, j = idx[int(rng.integers(len(idx)))]; p = (cx_(j), Z0 + (i + .5) * RES)
            dm = min([math.hypot(p[0] - q[0], p[1] - q[1]) for q in rib_pts] + [999])
            if dm > bd: bd, best = dm, p
        if best and bd >= 24:
            rib_pts.append(best)
for (x, z) in rib_pts[:4]:
    d = dir_to_sea(x, z); yaw = math.degrees(math.atan2(-d[1], d[0])) + 90 if d is not None else ang()
    # ribs stand perpendicular to the shore; sunk so about half is buried
    if add('hull_rib', x, z, yaw + float(rng.uniform(-15, 15)), float(rng.uniform(1.0, 1.4)), 'Debris'): RIBS += 1

# v10 wreck: planks, a barrel and a hull rib on the sand at the waterline below pad 1's deck (the wreck itself is untouched)
p1 = np.array(pw[1][:2]); d_p1 = np.hypot(WX - p1[0], WZ - p1[1])
wl = land & (sd_in > 1.5) & (sd_in < 9) & (h2r > 0.8) & (h2r < 4.5) & (d_p1 < 160) & (dlane > 10) & (sd_pad > 8)
WRECK_EXTRA = []
idx = np.argwhere(wl)
if len(idx):
    k = int(np.argmin(d_p1[wl])); i, j = idx[k]; wp = (cx_(j), Z0 + (i + .5) * RES)
    ds = dir_to_sea(*wp); ds = ds if ds is not None else np.array([0.0, -1.0]); perp = np.array([-ds[1], ds[0]])
    yaw_sea = math.degrees(math.atan2(ds[0], ds[1]))
    spec = [('planks', 0, 0, ang(), 1.2), ('barrel', 5.5, 3.0, ang(), 1.2), ('hull_rib', -9, 2.0, yaw_sea + 90 + float(rng.uniform(-12, 12)), 1.2), ('planks', 11, -4.0, ang(), 1.0)]
    for nm, al, ac, yw, sc in spec:
        x = wp[0] + perp[0] * al + ds[0] * ac * -1; z = wp[1] + perp[1] * al + ds[1] * ac * -1
        ITEMS.append(dict(mesh=nm, x=round(float(x), 2), z=round(float(z), 2), yaw=round(float(yw), 1), scale=sc, layer='Debris', pad=1))
        WRECK_EXTRA.append((nm, round(float(x), 1), round(float(z), 1)))

# ---------------------------------------------------------------- 4. vine strips on cliff faces + cave probes
VINE_T = 0
steep = (slope > 0.85) & land & ~hard_all & ~inner_lane & (dlane > 20) & (sd_pad > 12) & (mat2 == 3)
idx = np.argwhere(steep); chosen = []
for _ in range(60):
    if len(idx) == 0: break
    i, j = idx[int(rng.integers(len(idx)))]; p = (cx_(j), Z0 + (i + .5) * RES)
    if min([math.hypot(p[0] - q[0], p[1] - q[1]) for q in chosen] + [99]) < 30: continue
    # face normal points downhill
    d = np.array([-gx[i, j], -gz[i, j]]); nn = np.linalg.norm(d)
    if nn < 1e-6: continue
    d /= nn; yaw = math.degrees(math.atan2(d[0], d[1]))
    sc = float(rng.uniform(0.9, 1.3))
    ITEMS.append(dict(mesh='vine_strip', x=round(p[0], 2), z=round(p[1], 2), yaw=round(yaw, 1), scale=round(sc, 3), layer='Vines', pad=int(pad_id[i, j]))); chosen.append(p); VINE_T += 1
    if VINE_T >= 14: break
# v10 pad 15: vine strips on the cliff faces around the pad, a medium or large rock at the base of each
P15 = []
p15 = np.array(pw[15][:2]); near15 = np.hypot(WX - p15[0], WZ - p15[1]) < 170
steep15 = (slope > 0.55) & land & ~hard_all & ~inner_lane & (sd_pad > 10) & near15
idx = np.argwhere(steep15); ch15 = []
for _ in range(400):
    if len(idx) == 0 or len(ch15) >= 12: break
    i, j = idx[int(rng.integers(len(idx)))]; p = (cx_(j), Z0 + (i + .5) * RES)
    if min([math.hypot(p[0] - q[0], p[1] - q[1]) for q in ch15] + [99]) < 15: continue
    d = np.array([-gx[i, j], -gz[i, j]]); nn = np.linalg.norm(d)
    if nn < 1e-6: continue
    d /= nn; yaw = math.degrees(math.atan2(d[0], d[1])); sc = float(rng.uniform(1.0, 1.35))
    ITEMS.append(dict(mesh='vine_strip', x=round(p[0], 2), z=round(p[1], 2), yaw=round(yaw, 1), scale=round(sc, 3), layer='Vines', pad=15)); VINE_T += 1
    # walk downhill to the foot of the face, then a medium or large rock
    bx, bz = p
    for _s in range(25):
        ii, jj = ij(bx, bz)
        if not inb(ii, jj) or slope[ii, jj] < 0.4: break
        dd = np.array([-gx[ii, jj], -gz[ii, jj]]); n2 = np.linalg.norm(dd)
        if n2 < 1e-6: break
        bx += dd[0] / n2 * 2.0; bz += dd[1] / n2 * 2.0
    ch15.append(p); okr = False
    for nm in (('rock_l', 'rock_m') if rng.random() < 0.5 else ('rock_m', 'rock_l')):
        for off in (0, 6, -6, 12, -12):
            if add(nm, bx + off * d[1], bz - off * d[0], ang(), float(rng.uniform(1.0, 1.3)), 'Fill'): okr = True; break
        if okr: break
    if not okr:
        ii, jj = ij(bx, bz)
        if inb(ii, jj) and land[ii, jj] and not no_place[ii, jj]: okr = add('rock_m', bx, bz, ang(), float(rng.uniform(1.0, 1.3)), 'Fill', force=True)
    P15.append((round(p[0], 1), round(p[1], 1), okr))
CAVE_PROBES = []
fz = cv['frontFaceZ']
for k, x in enumerate(np.arange(cave_c[0] - 105, cave_c[0] + 106, 30)):
    if abs(x - mouthx) < 40: continue
    for y in (125, 150, 175):
        if rng.random() < 0.8: CAVE_PROBES.append(dict(x=float(x + rng.uniform(-6, 6)), y=float(y + rng.uniform(-8, 8)), z=float(fz + 60), faceZ=float(fz)))

# ---------------------------------------------------------------- 4b. v11 jungle trail: boardwalk runs (3 x 8.2 studs) and stepping stones along the lane (sand stays only on the beach)
JW = dict(bw=0, st=0)
i9, i15 = nearest_idx(pw[9][:2]), nearest_idx(pw[15][:2])
seg2 = tp[min(i9, i15):max(i9, i15) + 1]
cum2 = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(seg2, axis=0).T))])
def seg_at(sv):
    k = int(np.searchsorted(cum2, sv)); k = min(max(k, 1), len(seg2) - 1)
    t = (sv - cum2[k - 1]) / max(1e-6, cum2[k] - cum2[k - 1]); p_ = seg2[k - 1] + (seg2[k] - seg2[k - 1]) * t
    tg = seg2[k] - seg2[k - 1]; tg = tg / np.linalg.norm(tg); return p_, tg
sv = 30.0; phase = 0
while sv < cum2[-1] - 30:
    run = 25.2 if phase % 2 == 0 else 38.0
    t0 = sv
    if phase % 2 == 0:
        for k in range(3):
            p_, tg = seg_at(sv + 4.1 + k * 8.4); i, j = ij(p_[0], p_[1])
            if inb(i, j) and land[i, j] and sd_in[i, j] > 45 and sd_pad[i, j] > 4 and not ho[i, j]:
                WALK.append(['bw', round(float(p_[0]), 2), round(float(p_[1]), 2), round(math.degrees(math.atan2(tg[0], tg[1])), 1), 8.2, 6.0]); JW['bw'] += 1
    else:
        q = 3.0
        while q < run:
            p_, tg = seg_at(sv + q); nx_, nz_ = -tg[1], tg[0]; lat = float(rng.uniform(-1.4, 1.4)); i, j = ij(p_[0] + nx_ * lat, p_[1] + nz_ * lat)
            if inb(i, j) and land[i, j] and sd_in[i, j] > 45 and sd_pad[i, j] > 4 and not ho[i, j]:
                WALK.append(['st', round(float(p_[0] + nx_ * lat), 2), round(float(p_[1] + nz_ * lat), 2), round(ang(), 1), round(float(rng.uniform(3.6, 4.8)), 2), 0]); JW['st'] += 1
            q += 6.2
    sv += run + 6.0; phase += 1

# ---------------------------------------------------------------- 5. backdrop: stacks + reef ring
def stack_ok(x, z, nm, rot):
    sz = KIT[nm]['size']; r = 0.5 * max(sz[0], sz[2]) * 0.8
    d = out_dist_at(x, z)
    return d - r >= 400 and abs(x) < 2048 - 140 and abs(z) < 1280 - 140, d
stack_cands = {'stack_a': None, 'stack_c': None, 'stack_b': None}
b1 = bowE; axd = (bowE - sternE) / np.linalg.norm(bowE - sternE)   # stern -> bow (west)
def search(nm, centre_dir, ang_off, lo=500, hi=1500, target_pt=None):
    th = math.atan2(centre_dir[1], centre_dir[0]) + math.radians(ang_off)
    for dist in np.arange(lo, hi, 20):
        x, z = pw[1][0] + math.cos(th) * dist, pw[1][1] + math.sin(th) * dist
        ok, d = stack_ok(x, z, nm, 0)
        if ok: return (x, z)
    return None
for nm, off in (('stack_c', -12), ('stack_a', 16)):
    pt = search(nm, axd, off)
    if pt: BACK.append((nm, pt[0], pt[1], float(rng.uniform(0, 360)), 1.0))
# stack_b off the south beach side: scan the southern sea
best = None
for x in np.arange(-1100, 700, 40):
    for z in np.arange(700, 1140, 40):
        ok, d = stack_ok(x, z, 'stack_b', 0)
        if ok: 
            sc = -abs(x + 250) - 0.3 * abs(z - 1000)
            if best is None or sc > best[0]: best = (sc, x, z)
if best: BACK.append(('stack_b', best[1], best[2], float(rng.uniform(0, 360)), 1.0))
# reef ring round the bow
bow_c = bowE + axd * 20
BACK.append(('reef_ring', float(bow_c[0]), float(bow_c[1]), math.degrees(math.atan2(axd[0], axd[1])), 1.0))
for nm, x, z, yw, sc in BACK:
    ITEMS.append(dict(mesh=nm, x=round(x, 1), z=round(z, 1), yaw=round(yw, 1), scale=sc, layer='Backdrop', pad=0))

# v11 skyline stacks (dark silhouettes in the sea behind each pad, in view and behind the tee), after the v10 backdrop so they keep clear of it
for n in range(2, 19):
    z_ = ZONE(n)
    if z_ in ('wreckcove', 'beach'): SKY[n]['stacks'] = sky_stack(n, (-60, -25, 10, 45, 150, 210))
    elif z_ == 'cave': SKY[n]['stacks'] = sky_stack(n, (-45, 30, 160))

# ---------------------------------------------------------------- 5b. v12 post pass (Game Art Bot v11 notes + Playtest Bot v11 critique). Own RNG, so the v11 layout is kept except for these edits.
rng2 = np.random.default_rng(20261101)
V12 = {}
def uvp(n, x, z):
    th = math.radians(pw[n][2]); dx, dz = x - pw[n][0], z - pw[n][1]
    return dx * math.cos(th) - dz * math.sin(th), dx * math.sin(th) + dz * math.cos(th)
# 1. arches on only 3 of jungle pads 10-14 (10, 12, 14), at the cup end, 0.7x; pads 11 and 13 keep the leaning-palm canopy
ARCH_KEEP = (10, 12, 14)
new_items = []; rm_arch = 0
for it in ITEMS:
    if it['mesh'] == 'vine_arch' and it['layer'] == 'Arches' and it['scale'] == 1.1 and 10 <= it['pad'] <= 14:
        if it['pad'] not in ARCH_KEEP: rm_arch += 1; continue
        ax, az = to_world(it['pad'], 0, 37.0); it = dict(it, x=round(ax, 2), z=round(az, 2), scale=0.7)
    new_items.append(it)
ITEMS[:] = new_items
# arch pads lose one canopy palm (the farthest along the pad) so the two kinds read differently
palm_rm = 0
for n in ARCH_KEEP:
    cand = [(uvp(n, it['x'], it['z'])[1], k) for k, it in enumerate(ITEMS) if it['mesh'] == 'palm_lean_a' and it['layer'] == 'Front' and it['pad'] == n and abs(uvp(n, it['x'], it['z'])[0]) < 45 and -35 < uvp(n, it['x'], it['z'])[1] < 60]
    if len(cand) >= 3: ITEMS.pop(max(cand)[1]); palm_rm += 1
V12['arches'] = dict(kept=list(ARCH_KEEP), removed=rm_arch, palmsRemoved=palm_rm)
# 4a. delete the pad 17 floating vine strip ("trellis")
n0 = len(ITEMS); ITEMS[:] = [it for it in ITEMS if not (it['mesh'] == 'vine_strip' and it['layer'] == 'Vines' and it['pad'] == 17)]
V12['trellisRemoved'] = n0 - len(ITEMS)
# 5. beach pads 2-8: cut every second far palm
fp = sorted([k for k, it in enumerate(ITEMS) if it['mesh'].startswith('palm') and it['layer'] == 'Mid' and 2 <= it['pad'] <= 8 and math.hypot(it['x'] - pw[it['pad']][0], it['z'] - pw[it['pad']][1]) > 60], key=lambda k: (ITEMS[k]['pad'], ITEMS[k]['x'], ITEMS[k]['z']))
drop = set(fp[1::2]); V12['farPalmsCut'] = [len(drop), len(fp)]
ITEMS[:] = [it for k, it in enumerate(ITEMS) if k not in drop]
# (d) beach / wreck cove skyline rocks (pads 2-9): nothing closer than 140 studs, then keep every second one
sk = {}
for k, it in enumerate(ITEMS):
    if it['mesh'] == 'rock_l' and it['layer'] == 'Skyline' and 2 <= it['pad'] <= 9: sk.setdefault(it['pad'], []).append(k)
drop = set(); nsky0 = sum(len(v) for v in sk.values())
for n, ks in sk.items():
    ks.sort(key=lambda k: math.hypot(ITEMS[k]['x'] - pw[n][0], ITEMS[k]['z'] - pw[n][1]))
    far = [k for k in ks if math.hypot(ITEMS[k]['x'] - pw[n][0], ITEMS[k]['z'] - pw[n][1]) >= 140]
    drop |= set(ks) - set(far[::2])
ITEMS[:] = [it for k, it in enumerate(ITEMS) if k not in drop]
V12['beachSkylineRocks'] = [nsky0, nsky0 - len(drop)]
# pad 3 back view: the big skyline rock_l face behind the tee goes 30 studs further back, with a row of big leaf/fern clumps along its near edge to break it up
V12['pad3Face'] = []
_p3 = []
for it in ITEMS:
    if it['mesh'] == 'rock_l' and it['layer'] == 'Skyline' and math.hypot(it['x'] - pw[3][0], it['z'] - pw[3][1]) < 260:
        u_, v_ = uvp(3, it['x'], it['z'])
        if -220 < v_ < -90 and abs(u_) < 100:
            x2, z2 = to_world(3, u_, v_ - 30.0); V12['pad3Face'].append((round(u_), round(v_), round(it['scale'], 2))); it['x'] = round(float(x2), 2); it['z'] = round(float(z2), 2)
            _p3.append((u_, v_ - 30.0, it['scale']))
for u_, v_, sc_ in _p3:
    r_ = 0.5 * KIT['rock_l']['size'][0] * sc_
    for q in range(8):
        a_ = float(rng2.uniform(-0.9, 0.9)); uu = u_ + 0.9 * r_ * math.sin(a_); vv = v_ + 0.9 * r_ * math.cos(a_) + 0.0
        x2, z2 = to_world(3, uu, vv)
        ITEMS.append(dict(mesh='leafclump' if q % 2 == 0 else 'fernclump', x=round(float(x2), 2), z=round(float(z2), 2), yaw=round(float(rng2.uniform(0, 360)), 1), scale=round(float(rng2.uniform(1.8, 2.6)), 3), layer='Far', pad=3))
# (a) plants near each tee stay waist-high or lower: nothing but low clumps within 4 studs of the tee point, at most 3.5 tall within 6; tall plants start 6+ out
tee_rm = tee_cap = 0; new_items = []
for it in ITEMS:
    n = it['pad']
    if 2 <= n <= 18 and it['layer'] not in ('Skyline', 'Backdrop', 'Hang', 'Arches', 'Vines', 'Set'):
        tx, tz = to_world(n, 0, -CLEAR[1] / 2 + 12 - 0.0)  # tee point: 30 studs behind the pad centre
        tx, tz = to_world(n, 0, -30.0); d = math.hypot(it['x'] - tx, it['z'] - tz); nm = it['mesh']
        h = HEIGHT[nm] * it['scale']
        if d < 4 and (nm.startswith('palm') or nm in ('leafclump', 'fernclump')): tee_rm += 1; continue
        if d < 4 and nm.startswith('rock') and h > 2.6: it = dict(it, scale=round(2.6 / HEIGHT[nm], 3)); tee_cap += 1
        elif 4 <= d < 6 and nm == 'leafclump': tee_rm += 1; continue
        elif 4 <= d < 6 and nm == 'fernclump' and h > 3.5: it = dict(it, scale=round(3.5 / HEIGHT[nm], 3)); tee_cap += 1
        elif d < 6 and nm.startswith('palm'): tee_rm += 1; continue
    new_items.append(it)
ITEMS[:] = new_items; V12['teePlants'] = dict(removed=tee_rm, capped=tee_cap)
# 4b. backdrop stack behind pads 16 and 17 (dark sea stacks straight down the line, 9-16 deg elevation)
def sky_stack2(n, offs, lo=420, hi=1300):
    x0, z0, yw = pw[n]; th0 = math.radians(yw); a_f = math.atan2(math.cos(th0), math.sin(th0)); ng = 0
    for off in offs:
        a = a_f + math.radians(off)
        for dist in np.arange(lo, hi, 20):
            x, z = x0 + math.cos(a) * dist, z0 + math.sin(a) * dist
            if abs(x) > 2048 - 200 or abs(z) > 1280 - 200: break
            if out_dist_at(x, z) < 140: continue
            if min([math.hypot(x - q[0], z - q[1]) for q in SKY_STACKS] + [999]) < 150: continue
            nm = ('stack_a', 'stack_b', 'stack_c')[int(rng2.integers(3))]
            sc = float(np.clip(math.tan(math.radians(rng2.uniform(11, 16))) * dist / HEIGHT[nm], 0.22, 0.9))
            SKY_STACKS.append((x, z)); ng += 1
            ITEMS.append(dict(mesh=nm, x=round(x, 1), z=round(z, 1), yaw=round(float(rng2.uniform(0, 360)), 1), scale=round(sc, 3), layer='Skyline', pad=n)); break
    return ng
V12['stack1617'] = {str(n): sky_stack2(n, (0, -9, 9)) for n in (16, 17)}
# 2. moss and ferns dotted on rock tops (dy = height above ground): fern/leaf clumps at 0.4-0.6x sitting on rock_l and every third rock_m near a pad
moss = 0; add_items = []
for it in ITEMS:
    if it['mesh'] in ('rock_l', 'rock_m') and it['layer'] in ('Front', 'Mid', 'Set', 'Fill') and it['scale'] < 3 and 2 <= it['pad'] <= 18:
        if it['mesh'] == 'rock_m' and int(rng2.integers(3)) != 0: continue
        top = HEIGHT[it['mesh']] * it['scale'] * 0.72
        for q in range(2 if it['mesh'] == 'rock_l' else 1):
            nm = 'fernclump' if rng2.random() < 0.55 else 'leafclump'
            r_ = float(rng2.uniform(0, 0.28)) * 0.5 * max(KIT[it['mesh']]['size'][0], KIT[it['mesh']]['size'][2]) * it['scale']; a_ = float(rng2.uniform(0, 2 * math.pi))
            sc_ = float(rng2.uniform(0.42, 0.6)) * (1.0 if nm == 'fernclump' else 0.75)
            add_items.append(dict(mesh=nm, x=round(it['x'] + r_ * math.cos(a_), 2), z=round(it['z'] + r_ * math.sin(a_), 2), yaw=round(float(rng2.uniform(0, 360)), 1), scale=round(sc_, 3), layer='Moss', pad=it['pad'], dy=round(top, 2)))
            moss += 1
ITEMS.extend(add_items); V12['mossOnRocks'] = moss
# (b) lanterns: on the non-drop rim at u=16.5, 21 studs behind the pad centre (about 18 from the VR camera, ahead and to the side); bigger lamp and light set in the placer
for l in LANT:
    if l['kind'] == 'rim':
        sg = -DROP.get(l['pad'], -1); x, z = to_world(l['pad'], sg * RIM_TORCH_U_PAD.get(l['pad'], RIM_TORCH_U), -10.0); l['x'] = round(x, 2); l['z'] = round(z, 2)
V12['lanterns'] = [(l['pad'], l['x'], l['z']) for l in LANT if l['kind'] == 'rim']

# ---------------------------------------------------------------- 5c. v12 kit_v2 set pieces (Game Art Bot approved): one per pad, nearest edge ~30 studs off the play line (outside the 27-stud art clearance), lanterns hung on the hut eaves and the ruin arch, lantern posts, cliff ridges on the far beach skylines
PIECE = {1: 'rowboat_broken', 2: 'rowboat_broken', 3: 'hut_leanto', 4: 'crate_stack', 5: 'hut_leanto', 6: 'rowboat_broken', 7: 'crate_stack', 8: 'hut_leanto', 9: 'ruin_wall',
         10: 'ruin_arch', 11: 'ruin_wall', 12: 'hut_leanto', 13: 'ruin_arch', 14: 'boulder_pile', 15: 'boulder_pile', 16: 'ruin_arch', 17: 'ruin_wall', 18: 'crate_stack'}
POSTS = (1, 7, 11, 14)          # lantern_post beside the piece on these pads
HUT_LANT = ((-11.0, 18.0, 14.0), (11.0, 18.0, 14.0))     # hanging-lantern pivots (local x, y, z) under the hut's front eaves
ARCH_LANT = ((-8.5, 27.0, 0.5),)                          # under the arch curve
V12['setPieces'] = {}; V12['setPiecesSkipped'] = []; V12['hangingLanterns'] = 0; V12['lanternPosts'] = 0
def piece_ok(n, u, v, mesh, sc=1.0):
    sx, sy, sz = KIT[mesh]['size']; x, z = to_world(n, u, v); i, j = ij(x, z)
    if not (0 <= i < NZ and 0 <= j < NX) or not land[i, j] or no_place[i, j] or slope[i, j] > 0.5 or sd_in[i, j] < 6: return None
    r = 0.5 * max(sx, sz) * 0.8
    if d_none[i, j] < r * 0.5: return None
    zs = []
    for du, dv in ((-sz / 2, -sx / 2), (sz / 2, -sx / 2), (-sz / 2, sx / 2), (sz / 2, sx / 2)):
        qx, qz = to_world(n, u + math.copysign(1, u) * 0 + du, v + dv); qi, qj = ij(qx, qz)
        if not (0 <= qi < NZ and 0 <= qj < NX) or not land[qi, qj] or no_place[qi, qj]: return None
        zs.append(h2r[qi, qj])
    if max(zs) - min(zs) > 4.0: return None
    return x, z, r
for n in range(1, 19):
    done = False
    sides = (-1, 1) if n == 1 else ((-DROP[n], DROP[n]) if n != 18 else (-1,))
    cands = [(PIECE[n], 0.0)] + [(m_, e_) for e_ in (6.0, 14.0) for m_ in (PIECE[n], 'ruin_wall', 'boulder_pile', 'crate_stack')]
    for mesh, extra in cands:
      sx, sy, sz = KIT[mesh]['size']
      for side in sides:
        for v in (14.0, 8.0, 20.0, 26.0, 2.0, -4.0, 32.0, 38.0):
            u = side * (30.0 + extra + sz / 2)
            res = piece_ok(n, u, v, mesh)
            if res is None: continue
            x, z, r = res
            px, pz, yw = pw[n]; fx, fz = pw[n][0] - x, pw[n][1] - z
            yaw = math.degrees(math.atan2(fx, fz))
            ITEMS[:] = [it for it in ITEMS if not (it['layer'] not in ('Skyline', 'Backdrop') and math.hypot(it['x'] - x, it['z'] - z) < r)]
            ITEMS.append(dict(mesh=mesh, x=round(float(x), 2), z=round(float(z), 2), yaw=round(yaw, 1), scale=1.0, layer='Set2', pad=n))
            V12['setPieces'][str(n)] = [mesh, round(u, 1), v, side]
            th = math.radians(yaw)
            def loc(lx, lz): return (x + lx * math.cos(th) + lz * math.sin(th), z - lx * math.sin(th) + lz * math.cos(th))
            lants = HUT_LANT if mesh == 'hut_leanto' else ARCH_LANT if mesh == 'ruin_arch' else ()
            for lx, ly, lz in lants:
                qx, qz = loc(lx, lz)
                ITEMS.append(dict(mesh='lantern_hanging', x=round(float(qx), 2), z=round(float(qz), 2), yaw=round(yaw, 1), scale=1.5, layer='Set2', pad=n, dy=round(ly, 2), gp=[round(float(x), 2), round(float(z), 2)])); V12['hangingLanterns'] += 1
            if n in POSTS:
                pu = side * (28.5); pv = v - (sx / 2 + 3.0) if v > 0 else v + sx / 2 + 3.0
                qx, qz = to_world(n, pu, pv); qi, qj = ij(qx, qz)
                if land[qi, qj] and not no_place[qi, qj] and slope[qi, qj] < 0.5:
                    pyaw = pw[n][2] + (0 if side == -1 else 180)
                    ITEMS.append(dict(mesh='lantern_post', x=round(float(qx), 2), z=round(float(qz), 2), yaw=round(float(pyaw), 1), scale=1.4, layer='Set2', pad=n)); V12['lanternPosts'] += 1
            done = True; break
        if done: break
      if done: break
    if not done: V12['setPiecesSkipped'].append(n)
# cliff ridges on the far beach skylines (pads 2-9): placed like the sea stacks, 11-16 degrees of elevation, away from the island
ridges = []
for n in (3, 5, 7, 9):
    x0, z0, yw = pw[n]; th0 = math.radians(yw); a_f = math.atan2(math.cos(th0), math.sin(th0)) + math.pi    # straight back from the tee
    for off in (-14, 14):
        a = a_f + math.radians(off); placed = False
        for dist in np.arange(480, 1300, 20):
            x, z = x0 + math.cos(a) * dist, z0 + math.sin(a) * dist
            if abs(x) > 2048 - 250 or abs(z) > 1280 - 250: break
            if out_dist_at(x, z) < 160: continue
            if min([math.hypot(x - q[0], z - q[1]) for q in SKY_STACKS + ridges] + [999]) < 200: continue
            sc = float(np.clip(math.tan(math.radians(rng2.uniform(9, 13))) * dist / HEIGHT['cliff_ridge'], 0.5, 2.2))
            ridges.append((x, z)); ITEMS.append(dict(mesh='cliff_ridge', x=round(x, 1), z=round(z, 1), yaw=round(math.degrees(math.atan2(x0 - x, z0 - z)) + 90, 1), scale=round(sc, 3), layer='Skyline', pad=n)); placed = True; break
V12['cliffRidges'] = len(ridges)

# ---------------------------------------------------------------- 5d. v13 post pass (Playtest Bot v12 critique + Game Art Bot v12 notes; Game Art wins where they overlap). Own RNG; v12 layout kept except for these edits.
rng3 = np.random.default_rng(20261102)
V13 = {}
def az_to_pad(n, x, z):                               # bearing (rad) from the pad centre to a world point, same convention as the v12 ridge code
    return math.atan2(z - pw[n][1], x - pw[n][0])
def angdiff(a, b): return abs((a - b + math.pi) % (2 * math.pi) - math.pi)
def pad_az(n, back=False):
    th0 = math.radians(pw[n][2]); return math.atan2(math.cos(th0), math.sin(th0)) + (math.pi if back else 0.0)
# -- 1. beach skylines (pads 2-9): sharp Skyline spike stacks out, kit_v2_1 cliff ridges in, kit_v2_1 canopy walls in front of every ridge so the skyline reads in layers
def is_stack_sky(it): return it['layer'] == 'Skyline' and it['mesh'].startswith('stack')
rm_st = []
for it in ITEMS:
    if not is_stack_sky(it): continue
    if 2 <= it['pad'] <= 9: rm_st.append(it); continue
    for n in (7, 9):                                  # any other stack that stands in the forward or back arc of pads 7 and 9
        a = az_to_pad(n, it['x'], it['z'])
        if min(angdiff(a, pad_az(n)), angdiff(a, pad_az(n, True))) < math.radians(38): rm_st.append(it); break
rm_ids = {id(i) for i in rm_st}
ITEMS[:] = [it for it in ITEMS if id(it) not in rm_ids]
SKY_STACKS[:] = [q for q in SKY_STACKS if min([math.hypot(q[0] - it['x'], q[1] - it['z']) for it in rm_st] + [999]) > 1.0]
ridge_its = [it for it in ITEMS if it['mesh'] == 'cliff_ridge']
def view_yaw(n, x, z):
    dx, dz = pw[n][0] - x, pw[n][1] - z; return math.degrees(math.atan2(dx, dz)) % 360        # long (x) axis perpendicular to the line of sight
def new_ridge(n, x, z, layer_pad):
    d = math.hypot(x - pw[n][0], z - pw[n][1])
    sc = float(np.clip(math.tan(math.radians(rng3.uniform(9, 13))) * d / HEIGHT['cliff_ridge'], 0.5, 2.2))
    ITEMS.append(dict(mesh='cliff_ridge', x=round(x, 1), z=round(z, 1), yaw=round(view_yaw(n, x, z), 1), scale=round(sc, 3), layer='Skyline', pad=layer_pad))
    return ITEMS[-1]
# existing 5 ridges: face the pad properly (v12 had the 300-stud axis along the line of sight)
for it in ridge_its:
    n = it['pad']; it['yaw'] = round(view_yaw(n, it['x'], it['z']), 1)
# one ridge per removed stack spot (same bearing and distance, re-scaled), then make sure pads 7 and 9 have ridges in both arcs
nr = 0
for it in rm_st:
    n = it['pad'] if 2 <= it['pad'] <= 9 else min((7, 9), key=lambda q: math.hypot(it['x'] - pw[q][0], it['z'] - pw[q][1]))
    if min([math.hypot(it['x'] - r['x'], it['z'] - r['z']) for r in ITEMS if r['mesh'] == 'cliff_ridge'] + [999]) < 230: continue
    new_ridge(n, it['x'], it['z'], n); nr += 1
for n in (7, 9):
    for back in (False, True):
        have = [r for r in ITEMS if r['mesh'] == 'cliff_ridge' and angdiff(az_to_pad(n, r['x'], r['z']), pad_az(n, back)) < math.radians(30)]
        if have: continue
        a_c = pad_az(n, back); x0, z0 = pw[n][0], pw[n][1]
        for off in (-12, 12, 0, -22, 22):
            ok = False
            for dist in np.arange(480, 1300, 20):
                a = a_c + math.radians(off); x, z = x0 + math.cos(a) * dist, z0 + math.sin(a) * dist
                if abs(x) > 2048 - 250 or abs(z) > 1280 - 250: break
                if out_dist_at(x, z) < 160: continue
                if min([math.hypot(x - q['x'], z - q['z']) for q in ITEMS if q['mesh'] == 'cliff_ridge'] + [999]) < 230: continue
                new_ridge(n, x, z, n); nr += 1; ok = True; break
            if ok: break
# canopy walls in front of each ridge: 50-55% of the way from the pad, 6 degrees of elevation (below the 9-13 deg ridge), 1-3 side by side across the ridge width
nw = 0
walls_on_land = 0
for r in [q for q in ITEMS if q['mesh'] == 'cliff_ridge']:
    n = r['pad']; x0, z0 = pw[n][0], pw[n][1]; d = math.hypot(r['x'] - x0, r['z'] - z0); dw = d * 0.52
    ux, uz = (r['x'] - x0) / d, (r['z'] - z0) / d; px_, pz_ = -uz, ux            # unit along the sight line and across it
    Hw = math.tan(math.radians(6.0)) * dw; scw = float(np.clip(Hw / HEIGHT['canopy_wall'], 0.35, 1.2)); ww = KIT['canopy_wall']['size'][0] * scw * 0.92
    rw = KIT['cliff_ridge']['size'][0] * r['scale'] * 0.9
    k = int(np.clip(math.ceil(rw / ww), 1, 3))
    for q in range(k):
        off = (q - (k - 1) / 2) * ww
        x, z = x0 + ux * dw + px_ * off, z0 + uz * dw + pz_ * off
        if abs(x) > 2048 - 150 or abs(z) > 1280 - 150: continue
        i, j = ij(x, z)
        if land[i, j] and h2r[i, j] > 0.55 * HEIGHT['canopy_wall'] * scw: continue        # buried in a hill
        if min([math.hypot(x - pw[m][0], z - pw[m][1]) for m in pw]) < 120: continue
        walls_on_land += int(land[i, j])
        ITEMS.append(dict(mesh='canopy_wall', x=round(x, 1), z=round(z, 1), yaw=round(view_yaw(n, x, z), 1), scale=round(scw, 3), layer='Skyline', pad=n)); nw += 1
V13['skyline'] = dict(stacksRemoved=len(rm_st), ridgesAdded=nr, ridgesTotal=sum(1 for q in ITEMS if q['mesh'] == 'cliff_ridge'), canopyWalls=nw, wallsOnLand=walls_on_land)
# -- 2. pale domes: pad 16 forward domes pushed back 55 studs, pad 17 mound/face pushed back 45 and 0.85x, pad 2 mid-distance rock pushed back 30 (Skyline rocks are darkened in the placer)
moved = {}
for it in ITEMS:
    if it['mesh'] != 'rock_l' or it['layer'] != 'Skyline': continue
    n = it['pad']
    if n not in (2, 16, 17): continue
    u, v = uvp(n, it['x'], it['z'])
    if 40 < v < 220 and abs(u) < 130:
        push, k = {2: (30.0, 1.0), 16: (55.0, 1.0), 17: (45.0, 0.85)}[n]
        nx_, nz_ = to_world(n, u, v + push); it['x'] = round(nx_, 2); it['z'] = round(nz_, 2); it['scale'] = round(it['scale'] * k, 3); moved.setdefault(str(n), []).append((round(u), round(v)))
V13['domesPushed'] = moved
# -- 3. rim torches (kit_v2_1 tiki torches) replace the yellow lantern placeholders on pads 1, 4, 5, 10, 15, 17, 18 (~24 studs from the tee); the cave-mouth lantern becomes a torch too
TORCH_PADS = (1, 4, 5, 6, 10, 15, 17, 18)   # v16: pad 6 gets a torch too
if os.environ.get('TORCH_ONLY'): TORCH_PADS = tuple(int(q) for q in os.environ['TORCH_ONLY'].split(','))
LANT[:] = [l for l in LANT if l['kind'] != 'rim']
tr = {}
for n in TORCH_PADS:
    sg = -DROP.get(n, -1); x, z = to_world(n, sg * RIM_TORCH_U_PAD.get(n, RIM_TORCH_U), -2.0)      # v16: every rim torch on pads 1, 4, 5, 6, 10, 15, 17, 18 sits at v -2 (v15: 5, 17, 18): torches on pads 5, 17, 18 moved 6.4 studs further from the tee (v -10 to -2) (Game Art Bot)
    mesh, sc = ('torch_tiki_short', 1.7) if n in (4, 17) else ('torch_tiki', 1.25)
    LANT.append(dict(kind='rim', pad=n, x=round(x, 2), z=round(z, 2), mesh=mesh, scale=sc))
    tx_, tz_ = to_world(n, 0, -27.0); tr[str(n)] = [mesh, round(math.hypot(x - tx_, z - tz_), 1)]
    ITEMS[:] = [it for it in ITEMS if not (it['layer'] not in ('Skyline', 'Backdrop') and math.hypot(it['x'] - x, it['z'] - z) < 4.5 and it['mesh'] != 'vine_arch')]
for l in LANT:
    if l['kind'] == 'mouth': l['mesh'] = 'torch_tiki'; l['scale'] = 1.4
V13['torches'] = dict(pads=tr, caveMouth='torch_tiki')
# -- 4. beach pads 2-8: low edge dressing along the rails (pebbles and shell-sized rocks, short fern and leaf clumps) at u = 18-23, v = -20..28
ed = 0
for n in range(2, 9):
    for sgn in (-1, 1):
        v = -19.0
        while v < 28.0:
            x, z = to_world(n, sgn * float(rng3.uniform(18.0, 23.0)), v + float(rng3.uniform(-1.2, 1.2)))
            r_ = rng3.random()
            nm, sc = (('rock_s', float(rng3.uniform(0.16, 0.32))) if r_ < 0.4 else ('rock_s', float(rng3.uniform(0.35, 0.55))) if r_ < 0.6 else ('fernclump', float(rng3.uniform(0.3, 0.42))) if r_ < 0.85 else ('leafclump', float(rng3.uniform(0.18, 0.26))))
            if fadd(nm, x, z, ang(), sc, 'Edge', 3.0, 0.25): ed += 1
            v += float(rng3.uniform(2.6, 4.4))
V13['edgeDressing'] = ed
# -- 5. tee and back-shot clearance, measured from the VR camera point (tee, 5 studs above the felt): plants and rocks within 6 studs, and in the 120-degree cone behind the tee out to 35 studs, are capped
#      (2.5 studs up to 8 away, rising 0.15 per stud). Capped = scaled down (counts and tris unchanged). Jungle pads 10-14 are never thinned: everything there is shrunk, nothing is removed.
def cap_h(d): return 2.5 if d <= 8 else min(2.5 + 0.15 * (d - 8), 6.6)
PLANTS = ('fernclump', 'leafclump'); ROCKS = ('rock_s', 'rock_m', 'rock_l')
stat = dict(shrunk=0, removed=0, palmsRemoved=0, rocksRemoved=0, rocksShrunk=0)
removed_rocks = []; shrunk_rocks = []; keep = []
for it in ITEMS:
    n = it['pad']; nm = it['mesh']
    if not (2 <= n <= 18) or it['layer'] in ('Skyline', 'Backdrop', 'Hang', 'Arches', 'Vines', 'Set', 'Set2', 'Moss', 'Debris', 'Walkways', 'Lanterns') or (nm not in PLANTS + ROCKS and not nm.startswith('palm')): keep.append(it); continue
    u, v = uvp(n, it['x'], it['z']); uT, vT = u, v + 27.0; d = math.hypot(uT, vT)
    in_cone = vT < 0 and abs(uT) <= math.tan(math.radians(60)) * -vT and d <= 35
    if not (d <= 6 or in_cone): keep.append(it); continue
    jungle = 10 <= n <= 14
    if nm.startswith('palm'):
        if d <= 6 or (in_cone and d <= 12 and not jungle): stat['palmsRemoved'] += 1; continue
        keep.append(it); continue
    h = HEIGHT[nm] * it['scale']; cap = cap_h(d)
    if h <= cap: keep.append(it); continue
    ratio = cap / h
    if nm in ROCKS:
        if ratio < 0.55 and not jungle: stat['rocksRemoved'] += 1; removed_rocks.append((it['x'], it['z'], 0.5 * KIT[nm]['size'][0] * it['scale'] + 3)); continue
        ratio = max(ratio, 0.55); stat['rocksShrunk'] += 1; shrunk_rocks.append((it['x'], it['z'], 0.5 * KIT[nm]['size'][0] * it['scale'] + 3, ratio))
        keep.append(dict(it, scale=round(it['scale'] * ratio, 3))); continue
    stat['shrunk'] += 1; keep.append(dict(it, scale=round(it['scale'] * ratio, 3)))
final = []
for it in keep:                                       # moss on removed / shrunk rocks follows its rock
    if it['layer'] == 'Moss':
        if any(math.hypot(it['x'] - a, it['z'] - b) < r for a, b, r in removed_rocks): continue
        for a, b, r, k in shrunk_rocks:
            if math.hypot(it['x'] - a, it['z'] - b) < r: it = dict(it, dy=round(it.get('dy', 0) * k, 2), scale=round(it['scale'] * k, 3)); break
    final.append(it)
ITEMS[:] = final
V13['teeClearance'] = stat
V13['rule'] = 'cap 2.5 studs within 8 of the VR camera point (tee), +0.15 per stud to 6.6 at 35 studs, in the 120-degree back cone and within 6 studs of the tee; rocks below 55% scale are removed (not on pads 10-14); palms within 6 (and within 12 in the back cone, not on pads 10-14) are removed'

# ---------------------------------------------------------------- 5e. v14 post pass (Playtest Bot + Game Art Bot v13 critique; Game Art wins on overlap). Own RNG; v13 layout kept except for these edits.
from layout import PAD_TOP as _PT14
rng4 = np.random.default_rng(20261103)
V14 = {}
def gy14(x, z):
    i, j = ij(x, z); return float(h2r[i, j]) if inb(i, j) else 0.0
def bearing(n, x, z): return math.atan2(z - pw[n][1], x - pw[n][0])
# -- 1. big tan rock faces behind / ahead of pads 2, 16, 17, 18: every large Skyline rock_l within 260 studs of the play axis (+-55 deg) is swapped for two boulder piles (kit_v2, rock tint 115,100,92) at least 110 studs out
rm14 = []; add14 = []
for it in ITEMS:
    if it['mesh'] != 'rock_l' or it['layer'] != 'Skyline' or it['scale'] <= 1.5: continue
    for n in (2, 16, 17, 18):
        if it['scale'] <= 3.0 and n != 17: continue
        d = math.hypot(it['x'] - pw[n][0], it['z'] - pw[n][1])
        if d > 260: continue
        a = bearing(n, it['x'], it['z'])
        if min(angdiff(a, pad_az(n)), angdiff(a, pad_az(n, True))) > math.radians(55): continue
        rm14.append((id(it), n, round(d))); break
rm_ids14 = {r[0] for r in rm14}
for it in list(ITEMS):
    if id(it) not in rm_ids14: continue
    n = [r for r in rm14 if r[0] == id(it)][0][1]
    d = max(math.hypot(it['x'] - pw[n][0], it['z'] - pw[n][1]), 110.0); a = bearing(n, it['x'], it['z'])
    for off in (-22.0, 22.0):
        x = pw[n][0] + math.cos(a) * d - math.sin(a) * off; z = pw[n][1] + math.sin(a) * d + math.cos(a) * off
        add14.append(dict(mesh='boulder_pile', x=round(x, 2), z=round(z, 2), yaw=round(float(rng4.uniform(0, 360)), 1), scale=2.3, layer='Set2', pad=n))
ITEMS[:] = [it for it in ITEMS if id(it) not in rm_ids14] + add14
V14['tanRocksSwapped'] = [(r[1], r[2]) for r in rm14]; V14['boulderPilesAdded'] = len(add14)
# -- 2. rock spikes on pads 7 and 9: no sea stack (any layer) within 50 deg of the forward or back axis
rm_sp = [it for it in ITEMS if it['mesh'].startswith('stack') and any(min(angdiff(bearing(n, it['x'], it['z']), pad_az(n)), angdiff(bearing(n, it['x'], it['z']), pad_az(n, True))) < math.radians(50) for n in (7, 9))]
rm_sp_ids = {id(i) for i in rm_sp}; ITEMS[:] = [it for it in ITEMS if id(it) not in rm_sp_ids]
V14['spikeStacksRemoved'] = len(rm_sp)
# -- 3. torches also on pads 8 and 12 (the yellow lantern blocks / hut glare pads)
for n in (8, 12):
    sg = -DROP.get(n, -1); x, z = to_world(n, sg * RIM_TORCH_U_PAD.get(n, RIM_TORCH_U), -2.0 if n == 12 else -10.0)      # v16: pad 12 torch to v -2 like the others
    LANT.append(dict(kind='rim', pad=n, x=round(x, 2), z=round(z, 2), mesh='torch_tiki', scale=1.25))
    ITEMS[:] = [it for it in ITEMS if not (it['layer'] not in ('Skyline', 'Backdrop') and math.hypot(it['x'] - x, it['z'] - z) < 4.5 and it['mesh'] != 'vine_arch')]
V14['torchPads'] = sorted(l['pad'] for l in LANT if l['kind'] == 'rim')
# -- 4. eye-height plants in the back view: fern / leaf clumps in the 130-degree cone behind each tee (out to 90 studs) must top out 1.5 studs under the VR eye (felt top + 5), measured on the rendered ground (jungle pads 10-14: shrunk to 0.3x at most, never removed)
PL14 = ('fernclump', 'leafclump'); st14 = dict(shrunk=0, removed=0, jungleFloor=0); keep14 = []
for it in ITEMS:
    n = it['pad']; nm = it['mesh']
    if not (2 <= n <= 18) or nm not in PL14 or it['layer'] in ('Skyline', 'Backdrop', 'Hang', 'Vines', 'Arches'): keep14.append(it); continue
    best = None
    for m in range(max(2, n - 1), min(18, n + 1) + 1):          # neighbouring pads' back cones can reach too
        u, v = uvp(m, it['x'], it['z']); du, dv = u, v + 27.0; d = math.hypot(du, dv)
        if dv < 0 and d <= 90 and abs(du) <= math.tan(math.radians(65)) * -dv:
            best = (m, d); break
    if best is None: keep14.append(it); continue
    m = best[0]; eye = _PT14[m] + 5.0; g = gy14(it['x'], it['z']) + it.get('dy', 0)
    hh = HEIGHT[nm] * it['scale']; allow = eye - 1.5 - g
    if hh <= allow: keep14.append(it); continue
    ratio = allow / hh
    if ratio < 0.3:
        if 10 <= m <= 14: st14['jungleFloor'] += 1; keep14.append(dict(it, scale=round(it['scale'] * 0.3, 3))); continue
        st14['removed'] += 1; continue
    st14['shrunk'] += 1; keep14.append(dict(it, scale=round(it['scale'] * ratio, 3)))
ITEMS[:] = keep14; V14['eyeHeightPlants'] = st14
# -- 5. beach pads 2-8: heavier low edge dressing along both rails (pebble rocks, short ferns, leaf tufts), second pass on top of the v13 edge items
ed2 = 0
for n in range(2, 9):
    for sgn in (-1, 1):
        v = -22.0
        while v < 30.0:
            x, z = to_world(n, sgn * float(rng4.uniform(19.4, 23.0)), v + float(rng4.uniform(-0.8, 0.8)))
            r_ = rng4.random()
            nm, sc = (('rock_s', float(rng4.uniform(0.55, 0.95))) if r_ < 0.45 else ('fernclump', float(rng4.uniform(0.55, 0.8))) if r_ < 0.8 else ('leafclump', float(rng4.uniform(0.4, 0.55))))
            if fadd(nm, x, z, ang(), sc, 'Edge', 3.0, 0.2): ed2 += 1
            v += float(rng4.uniform(1.9, 3.2))
V14['edgeDressing2'] = ed2
# -- 6. jungle backdrop step / ramp (Game Art Bot: required): behind and ahead of pads 10-14, three staggered canopy_wall tiers whose tops climb 6, 9.5, 13 deg (200, 290, 380 studs out)
walls14 = 0; skipped14 = 0
for n in range(10, 15):
    for back in (False, True):
        a_c = pad_az(n, back)
        for (dist, elev, offs) in ((200.0, 6.0, (0.0,)), (290.0, 9.5, (-9.0, 9.0)), (380.0, 13.0, (-18.0, 0.0, 18.0))):
            for off in offs:
                a = a_c + math.radians(off); x, z = pw[n][0] + math.cos(a) * dist, pw[n][1] + math.sin(a) * dist
                if abs(x) > 2048 - 150 or abs(z) > 1280 - 150: skipped14 += 1; continue
                scw = float(np.clip(math.tan(math.radians(elev)) * dist / HEIGHT['canopy_wall'], 0.5, 2.0))
                i, j = ij(x, z)
                if land[i, j] and h2r[i, j] > 0.55 * HEIGHT['canopy_wall'] * scw: skipped14 += 1; continue
                if min([math.hypot(x - pw[m][0], z - pw[m][1]) for m in pw]) < 120: skipped14 += 1; continue
                ITEMS.append(dict(mesh='canopy_wall', x=round(x, 1), z=round(z, 1), yaw=round(view_yaw(n, x, z), 1), scale=round(scw, 3), layer='Skyline', pad=n)); walls14 += 1
V14['jungleBackdropTiers'] = dict(walls=walls14, skippedBuried=skipped14)
metrics_v14 = V14

# ---------------------------------------------------------------- 5f. v16 post pass (Game Art Bot + Playtest Bot v15). Own RNG.
rng5 = np.random.default_rng(20261104)
V16 = {}
# -- 1. pad 6 end cap: the pad 10 tier-1 canopy_wall at (765.3, 243.4) ends 38 studs from the pad 6 tee. Smaller (1.2x) and slid 35 studs along its axis away from the tee: its near end is >100 studs out.
for it in ITEMS:
    if it['mesh'] == 'canopy_wall' and abs(it['x'] - 765.3) < 0.5 and abs(it['z'] - 243.4) < 0.5:
        th = math.radians(it['yaw']); ax = np.array([math.cos(th), -math.sin(th)]); tee6 = np.array(to_world(6, 0, -27.0))
        cen = np.array([it['x'], it['z']])
        if np.dot(cen - tee6, ax) < 0: ax = -ax                          # ax points away from the tee along the wall
        old_end = float(np.linalg.norm(cen - ax * 146.7 * (it['scale'] / 1.444) - tee6)); sc_new = 1.2
        half = 146.7 * sc_new / 1.444; cen2 = cen + ax * 35.0
        near = cen2 - ax * half
        it['x'], it['z'], it['scale'] = round(float(cen2[0]), 1), round(float(cen2[1]), 1), sc_new
        V16['pad6WallEnd'] = dict(oldNearEndDist=round(old_end, 1), newNearEndDist=round(float(np.linalg.norm(near - tee6)), 1), center=[it['x'], it['z']], scale=sc_new)
# -- 2. plants: every palm / fern clump / leaf clump jittered +-3 studs, +-20% scale, random yaw (lean palms: yaw +-20 deg and scale never up, so crowns still clear the putting lines). Rejected if the move would touch a pad's rails/felt, the lane, water, or a torch.
PLANT = lambda nm: nm.startswith('palm') or nm in ('fernclump', 'leafclump')
tee_pts = {m: to_world(m, 0, -27.0) for m in pw}
torch_xy = [(l['x'], l['z']) for l in LANT if l['kind'] in ('rim', 'back')]
def jit_ok(it, x, z):
    i, j = ij(x, z)
    if not inb(i, j) or not land[i, j]: return False
    if dlane[i, j] < 8 and not (dlane[ij(it['x'], it['z'])] < 8): return False
    for m in pw:
        u0, v0 = uvp(m, it['x'], it['z']); u1, v1 = uvp(m, x, z)
        if abs(v1) < 36 and abs(u0) < 32 and abs(u1) < min(abs(u0), 19.5) - 1e-9: return False      # never closer to the felt than it was (and never inside the 19.5 rail line)
        if abs(v1) < 36 and abs(u1) < 19.0: return False
    for tx_, tz_ in torch_xy:
        if math.hypot(x - tx_, z - tz_) < 4.0: return False
    return True
nj = nrej = 0
for it in ITEMS:
    nm = it['mesh']
    if not PLANT(nm): continue
    lean = nm.startswith('palm_lean')
    for _try in range(12):
        x = it['x'] + float(rng5.uniform(-3, 3)); z = it['z'] + float(rng5.uniform(-3, 3))
        if jit_ok(it, x, z): it['x'], it['z'] = round(x, 2), round(z, 2); nj += 1; break
    else: nrej += 1
    f = float(rng5.uniform(0.8, 1.2))
    if lean: f = min(f, 1.0)
    it['scale'] = round(it['scale'] * f, 3)
    it['yaw'] = round((it['yaw'] + float(rng5.uniform(-20, 20))) % 360 if lean else float(rng5.uniform(0, 360)), 1)
V16['plantJitter'] = dict(plants=sum(1 for it in ITEMS if PLANT(it['mesh'])), moved=nj, notMoved=nrej)
# -- 3. eye-height plants in the back views of pads 10, 11, 12: the v14 cap re-run on the jittered scales, with the jungle floor lowered from 0.3x to 0.15x (v15 pads 10 / 11 back still showed big leaf plants over the eye line). Shrinks only, nothing removed.
st16 = dict(shrunk=0, floorHit=0); keep16 = []
for it in ITEMS:
    nm = it['mesh']
    if nm not in PL14 or it['layer'] in ('Skyline', 'Backdrop', 'Hang', 'Vines', 'Arches'): keep16.append(it); continue
    hit = None
    for m in (10, 11, 12):
        u, v = uvp(m, it['x'], it['z']); du, dv = u, v + 27.0; d = math.hypot(du, dv)
        if dv < 0 and d <= 90 and abs(du) <= math.tan(math.radians(65)) * -dv: hit = m; break
    if hit is None: keep16.append(it); continue
    eye = _PT14[hit] + 5.0; g = gy14(it['x'], it['z']) + it.get('dy', 0); hh = HEIGHT[nm] * it['scale']; allow = eye - 1.5 - g
    if hh <= allow: keep16.append(it); continue
    r_ = max(0.15, allow / hh) if allow > 0 else 0.15
    if allow / hh < 0.15: st16['floorHit'] += 1
    st16['shrunk'] += 1; keep16.append(dict(it, scale=round(it['scale'] * r_, 3)))
ITEMS[:] = keep16; V16['eyeHeightPlants'] = st16
# -- 4. a warm light source in each back view of pads 10, 11, 12: a tiki torch (v15 look) 18-25 studs behind the tee off the lane, plus an invisible warm fill light above it (placer: kind 'back')
back_l = {}
for n in (10, 11, 12):
    for (u, v) in ((15, -48), (-15, -48), (17, -44), (-17, -44), (14, -54), (-14, -54)):
        x, z = to_world(n, u, v); i, j = ij(x, z)
        if inb(i, j) and land[i, j] and dlane[i, j] >= 10 and h2r[i, j] > 1.0: break
    else: raise SystemExit('no back torch spot pad %d' % n)
    LANT.append(dict(kind='back', pad=n, x=round(x, 2), z=round(z, 2), mesh='torch_tiki', scale=1.25))
    ITEMS[:] = [it for it in ITEMS if not (it['layer'] not in ('Skyline', 'Backdrop') and math.hypot(it['x'] - x, it['z'] - z) < 4.5 and it['mesh'] != 'vine_arch')]
    back_l[str(n)] = [round(x, 1), round(z, 1), u, v]
V16['backTorches'] = back_l
V16['torchPads'] = sorted((l['kind'], l['pad']) for l in LANT if l['kind'] in ('rim', 'back'))
metrics_v16 = V16

# ---------------------------------------------------------------- 5g. v19 (Playtest Bot v16): the eye-height cap reaches the Skyline layer behind pads 10, 11, 12
# v14/v16 skipped layer 'Skyline', so the big Skyline.leafclump (about 70 x 24 x 64 studs, 13-20 studs from the bf11 / bf12 cameras) still reached over the eye line.
# Rule: every Skyline fern / leaf clump in the 130-degree back cone of pad 10, 11 or 12 (out to 120 studs) must top out 1.5 studs under the VR eye (felt top + 5), measured on the rendered ground.
# Shrunk to fit; where that would need less than 0.15x (or the ground there is above the eye) the clump is removed (Skyline filler only; the ground plants are untouched).
V19 = {}; st19 = dict(shrunk=0, removed=0, checked=0, rows=[]); keep19 = []
for it in ITEMS:
    nm = it['mesh']
    if nm not in PL14 or it['layer'] in ('Backdrop', 'Hang', 'Vines', 'Arches'): keep19.append(it); continue
    sky19 = it['layer'] == 'Skyline'
    hit = None
    for m in (10, 11, 12, 13, 14):
        u, v = uvp(m, it['x'], it['z']); du, dv = u, v + 27.0; d_ = math.hypot(du, dv)
        if dv < 0 and d_ <= 160 and abs(du) <= math.tan(math.radians(80)) * -dv: hit = (m, d_); break
    if hit is None: keep19.append(it); continue
    st19['checked'] += 1
    m = hit[0]; eye = _PT14[m] + 5.0; g = gy14(it['x'], it['z']) + it.get('dy', 0); hh = HEIGHT[nm] * it['scale']; allow = eye - (2.5 if sky19 else 3.0) - g      # v21: ground plants capped 3 studs under the eye (ferns at chest-to-eye height were still standing behind the tee)
    if hh <= allow: keep19.append(it); continue      # (ground plants already shrunk below 0.3x by an earlier cap stay as they are)
    r_ = allow / hh if allow > 0 else 0.0
    if r_ < 0.15 and not sky19 and d_ > 90: r_ = 0.15            # v21: ground plants far out keep the 0.15x floor; within 90 studs of the tee they are removed when they still cannot fit
    if r_ < 0.15:
        st19['removed'] += 1; st19['rows'].append([m, nm, round(hit[1], 1), it['scale'], 'removed']); continue
    st19['shrunk'] += 1; st19['rows'].append([m, nm, round(hit[1], 1), it['scale'], round(it['scale'] * r_, 3)]); keep19.append(dict(it, scale=round(it['scale'] * r_, 3)))
# v19 (pad 10 back view): the two Skyline canopy_walls that made the dark far mass were hidden in the place (Transparency 1); the generator now drops them
_cw19 = [(521.6, 159.1), (557.3, 45.7)]
_n_cw = len(keep19)
keep19 = [it for it in keep19 if not (it['mesh'] == 'canopy_wall' and any(abs(it['x'] - cx) < 3 and abs(it['z'] - cz) < 3 for cx, cz in _cw19))]
st19['canopyWallsDropped'] = _n_cw - len(keep19)
ITEMS[:] = keep19; st19['rows'] = st19['rows'][:60]; V19['skylineEyeCap'] = st19; V19['rimTorchU'] = RIM_TORCH_U; V19['rimTorchUPad'] = RIM_TORCH_U_PAD
metrics_v19 = V19
# 5i. v21 Studio finals (hidden / moved in place in the published v21; the generator now matches)
_V21_DROP = [('boulder_pile', 311.9, -456.8)] + [('leafclump', x, z) for x, z in [(492.3, 213.3), (476.1, 186.4), (224.4, 89.1), (-35.6, -114.1), (-75.3, -77.7), (-76.0, -71.1), (-66.3, -61.2), (-66.8, -10.0), (-28.7, -49.1)]] \
    + [('fernclump', x, z) for x, z in [(-398.7, 263.1), (164.7, 327.9), (166.9, 326.5), (161.6, 326.2)]] + [('rock_s', 437.8, 360.6), ('rock_s', 440.6, 358.7)]
_V21_MOVE = [('ruin_arch', -361.2, -214.1, -383.9, -229.3), ('lantern_hanging', -369.6, -214.9, -392.3, -230.2), ('rock_m', -374.1, -571.4, -374.9, -575.3)]
# v22 Studio finals (hidden in place in v22): hedge items that blocked the far tee-exit posts on pads 2 / 4 / 5 / 7, 10 leafclump@Far above the pad 12 felt cone, 2 ferns on widened trail cells
_V22_DROP = [(m_, x_, z_) for m_, x_, z_ in [
    ('fernclump', -367.4, 269.8), ('fernclump', -355.9, 269.7), ('rock_s', -359.7, 269.3), ('rock_s', -363.0, 270.4), ('rock_s', -370.3, 266.7), ('fernclump', -351.7, 284.8), ('fernclump', -341.4, 297.0), ('leafclump', -379.7, 268.0), ('leafclump', -359.2, 270.2),
    ('fernclump', 188.1, 329.4), ('fernclump', 209.1, 332.8), ('fernclump', 191.8, 331.3), ('rock_s', 204.6, 332.8), ('rock_s', 206.2, 333.5), ('rock_s', 198.1, 329.9), ('rock_s', 196.3, 331.6), ('rock_s', 204.1, 330.8), ('fernclump', 208.1, 321.2),
    ('leafclump', 480.2, 363.2), ('fernclump', 474.8, 364.6), ('fernclump', 480.3, 365.6), ('rock_s', 476.3, 365.8), ('rock_s', 465.9, 364.4), ('rock_s', 471.2, 364.0),
    ('rock_s', 931.6, 299.9), ('rock_s', 929.6, 301.7), ('rock_s', 931.0, 275.0), ('fernclump', 929.2, 307.4),
    ('leafclump', -75.3, -77.7), ('leafclump', -76.0, -71.1), ('leafclump', -64.0, -68.7), ('leafclump', -67.3, -62.4), ('leafclump', -48.5, -71.7), ('leafclump', -52.0, -63.5), ('leafclump', -67.7, -12.0), ('leafclump', -42.3, -58.1), ('leafclump', -52.1, -12.6), ('leafclump', -28.9, -50.0),
    ('fernclump', -420.0, -501.1), ('fernclump', -462.3, -471.2)]]
_n21d = _n21m = 0; _k21 = []
for it in ITEMS:
    if any(it['mesh'] == nm and abs(it['x'] - x) < 1.5 and abs(it['z'] - z) < 1.5 for nm, x, z in _V21_DROP): _n21d += 1; continue
    if any(it['mesh'] == nm and abs(it['x'] - x) < 0.2 and abs(it['z'] - z) < 0.2 for nm, x, z in _V22_DROP): _n21d += 1; continue
    for nm, x, z, nx, nz in _V21_MOVE:
        if it['mesh'] == nm and abs(it['x'] - x) < 1.5 and abs(it['z'] - z) < 1.5: it['x'], it['z'] = nx, nz; _n21m += 1; break
    _k21.append(it)
ITEMS[:] = _k21; V19['v21StudioDropped'] = _n21d; V19['v21StudioMoved'] = _n21m

# 5h. v20 (Game Art Bot path spec + Playtest Bot): everything below is generated from data/route_v20.json (written by make_blockout.py)
#  a) 1.5 stud plant-free margin along the trail (path half width 3..5 + 1.5), clearings (hub 15, arches / cave mouth 7.5, tee aprons 6, all + 1.5): ferns and rock_s may line the
#     edges (they are only removed from the path itself)
#  b) 2-3 flat stepping stones where the trail crosses rock; hub props (pad 11 back torch, a second tiki torch, the pad 11 lantern post) moved to the 30 stud hub
#  c) pad 11 back view: canopy_wall hidden (dropped), leaf/fern clumps above the eye line removed; pad 12 back view: near-black canopy gaps filled
#  d) pads 16-18: boulder_piles get random yaw and +-25% scale; every other one is swapped for a kit_v1_2 rock (rock_l / rock_m templates are already kit_v1_2)
from scipy.spatial import cKDTree as _KD
_R20 = json.load(open(f'{ROOT}/data/route_v20.json'))
_rp_ = np.array(_R20['pointsXZ']); _rs_ = np.r_[0, np.cumsum(np.hypot(*np.diff(_rp_, axis=0).T))]
_sp_ = [np.array(sp) for sp in _R20['spurs']]
_all_ = np.vstack([_rp_] + _sp_) if _sp_ else _rp_
_isp_ = np.r_[np.zeros(len(_rp_), bool), np.ones(len(_all_) - len(_rp_), bool)]
_ss_ = np.r_[_rs_, np.zeros(len(_all_) - len(_rp_))]
_kd = _KD(_all_)
_hwpts_ = np.array(_R20['hwPts']); _spurhw_ = []
for k_, sp_ in enumerate(_sp_): _spurhw_ += [_R20['spurHw'][k_]] * len(sp_)
_hwall_ = np.r_[_hwpts_, np.array(_spurhw_)] if _spurhw_ else _hwpts_
def _hw20(i):
    return float(_hwall_[i])
_PM = np.array(Image.open(f'{ROOT}/data/pathmask_v20.png')) > 127; X0_, Z0_ = -2048, -1280
keep20, n20, h20 = [], 0, 0
SMALL20 = ('fernclump', 'rock_s')
for it in ITEMS:
    if it['layer'] in ('Backdrop', 'Skyline', 'Hang', 'Vines', 'Arches'): keep20.append(it); continue
    if it['mesh'] == 'ruin_arch': keep20.append(it); continue                    # run-2 bug: the arch clearings are centred on the arches, so the arches were being removed
    if it['mesh'] == 'lantern_hanging' and 'gp' in it and any(math.hypot(it['gp'][0] - c['x'], it['gp'][1] - c['z']) < 3.0 for c in _R20['clearings'] if c['kind'].startswith('arch')): keep20.append(it); continue
    dd_, ii_ = _kd.query([it['x'], it['z']]); hw_ = _hw20(int(ii_))
    inclr = any(math.hypot(it['x'] - c['x'], it['z'] - c['z']) < c['r'] + 1.5 for c in _R20['clearings'])
    marg = (hw_ + (3.0 if (it['mesh'] == 'fernclump' and hw_ >= 4.9) else 0.0)) if it['mesh'] in SMALL20 else hw_ + 1.5       # v21: ferns pulled back 3 studs on the pads 11-14 trail
    if it['mesh'] in ('leafclump', 'vine_strip', 'fernclump') or it['mesh'].startswith('palm'):
        gi_ = int((it['z'] - Z0_) / 4); gj_ = int((it['x'] - X0_) / 4)
        if 1 <= gi_ < _PM.shape[0] - 1 and 1 <= gj_ < _PM.shape[1] - 1 and _PM[gi_ - 1:gi_ + 2, gj_ - 1:gj_ + 2].any() and not (it['mesh'] == 'fernclump' and not _PM[gi_, gj_]): n20 += 1; continue     # v21: no leaf/fern/palm on any sand cell (2 leafclumps by pad 8)
    if dd_ < marg or inclr: n20 += 1; h20 += int(inclr and dd_ >= marg); continue
    keep20.append(it)
ITEMS[:] = keep20
# a2) overhead read of the trail (overview_v20): palms whose fronds overhang the trail and the vine strips / hangs above it are cleared along the trail
keep20b, nov = [], 0
npalm_tee = {}
def _palm_in_tee_cone(it):
    # v20 critic: palms out of the tee cone on pads 10-14 (the v13 rule exempted these pads): within 16 studs of the tee any direction, or in the 140-degree back cone out to 50 studs, or the 100-degree forward cone out to 40 studs
    for m in (10, 11, 12, 13, 14):
        u, v = uvp(m, it['x'], it['z']); du, dv = u, v + 27.0; d_ = math.hypot(du, dv)
        if m == 13 and dv >= 0 and d_ <= 160 and abs(du) <= math.tan(math.radians(45)) * dv: return m      # v22: a palm trunk still crossed the pad 13 tee view: no palm in the 90-degree forward cone to 160 studs
        if d_ <= 16 or (dv < 0 and d_ <= 90 and abs(du) <= math.tan(math.radians(70)) * -dv) or (dv >= 0 and d_ <= 90 and abs(du) <= math.tan(math.radians(62)) * dv):
            return m
    return None
_hub0 = [c for c in _R20['clearings'] if c['kind'] == 'hub'][0]
_CW_DROP = [(3.8, -94.5), (2.5, -99.7), (64.3, -37.7), (-39.4, 16.2)]     # run-2: the near-black Persistent canopy_walls of the pad 12 back view (x, z)
ncw_drop = nsky_drop = 0
keep20d = []
for it in ITEMS:
    if it['mesh'] == 'canopy_wall':
        dd_, ii_ = _kd.query([it['x'], it['z']]); rad_ = 0.35 * max(KIT['canopy_wall']['size'][0], KIT['canopy_wall']['size'][2]) * it['scale']
        if dd_ < rad_ or any(math.hypot(it['x'] - cx_, it['z'] - cz_) < 8.0 for cx_, cz_ in _CW_DROP): ncw_drop += 1; continue
    elif it['layer'] == 'Skyline' and it['mesh'] in ('leafclump', 'rock_l', 'palm_l', 'palm_m', 'fernclump'):
        dd_, ii_ = _kd.query([it['x'], it['z']]); rad_ = 0.4 * max(KIT[it['mesh']]['size'][0], KIT[it['mesh']]['size'][2]) * it['scale']
        if dd_ < rad_ and it['scale'] > 0.2: nsky_drop += 1; continue
    keep20d.append(it)
ITEMS[:] = keep20d; V19['canopyWallsDropped20'] = ncw_drop; V19['skylineOverTrailDropped'] = nsky_drop
for it in ITEMS:
    if it['mesh'].startswith('palm') or it['layer'] in ('Hang', 'Vines') or it['mesh'] in ('vine_strip', 'canopy_wall'):
        dd_, ii_ = _kd.query([it['x'], it['z']]); hw_ = _hw20(int(ii_))
        _hubd = math.hypot(it['x'] - _hub0['x'], it['z'] - _hub0['z'])
        _jz_ = hw_ >= 4.9      # v21: jungle trail zone (pads 11-14 legs + pad 14 start): clear the overhead much wider so the sand reads from above
        if _jz_ and it['layer'] == 'Skyline' and it['mesh'] in ('leafclump', 'palm_l', 'palm_m', 'palm_s', 'fernclump') and dd_ < hw_ + 7.0: nov += 1; continue
        if (dd_ < hw_ + ((9.0 if _jz_ else 4.5) if it['mesh'].startswith('palm') else (4.5 if _jz_ else 2.0)) or _hubd < _hub0['r'] + 6.0) and not (it['mesh'] == 'vine_arch'):
            nov += 1; continue
    if it['mesh'].startswith('palm'):
        _m = _palm_in_tee_cone(it)
        if _m: npalm_tee[_m] = npalm_tee.get(_m, 0) + 1; nov += 1; continue
    keep20b.append(it)
ITEMS[:] = keep20b
# a3) tee views at eye height (run 2: 9 pads could not see the trail): open the Edge hedge between each tee and its apron, and keep the first 40 studs of the trail near each tee low
_ap20 = {c['kind']: c for c in _R20['clearings']}
keep20e, nopen = [], 0
_tees20 = {}
for n_ in range(1, 19):
    tx_, tz_ = to_world(n_, 0.0, -27.0); _tees20[n_] = (tx_, tz_)
def _seg_d(px, pz, ax, az, bx, bz):
    vx, vz = bx - ax, bz - az; L2 = vx * vx + vz * vz or 1.0; t = max(0.0, min(1.0, ((px - ax) * vx + (pz - az) * vz) / L2)); return math.hypot(px - (ax + t * vx), pz - (az + t * vz))
for it in ITEMS:
    if it['mesh'] in ('leafclump', 'fernclump') and it['layer'] in ('Edge', 'Front', 'Mid', 'Fill', 'Moss'):
        drop_ = False
        for n_, (tx_, tz_) in _tees20.items():
            a_ = _ap20.get(f'apron{n_}')
            if a_ is not None and _seg_d(it['x'], it['z'], tx_, tz_, a_['x'], a_['z']) < 6.0: drop_ = True; break
            if math.hypot(it['x'] - tx_, it['z'] - tz_) < 45.0:
                dd_, ii_ = _kd.query([it['x'], it['z']])
                if dd_ < _hw20(int(ii_)) + 4.5: drop_ = True; break
        if drop_: nopen += 1; continue
    keep20e.append(it)
ITEMS[:] = keep20e; V19['teeTrailOpened'] = nopen
# a4) v22: the pad 16 ruin_arch re-seated across the 16 -> 17 exit trail (verified in Studio in v21: pillars off the sand, centre on it, 9 studs of sand under the span): arch (140,-472) with RightVector (0.200,-0.980) = yaw 78.5, lantern (138.8,-463.6)
for it in ITEMS:
    if it['mesh'] == 'ruin_arch' and it['pad'] == 16: it['x'], it['z'], it['yaw'] = 140.0, -472.0, 78.5; V19['arch16Yaw'] = 78.5
    elif it['mesh'] == 'lantern_hanging' and 'gp' in it and math.hypot(it['gp'][0] - 101.8, it['gp'][1] + 478.8) < 3.0: it['x'], it['z'], it['yaw'] = 138.8, -463.6, 78.5
# a4b) v24 Studio finals (published in Pirate Shipwreck v24): vine_arches of pads 10 / 12 / 14 moved to pad-local |Z| 40.23 (off the rim), pad 13 ruin_arch span perpendicular to the trail
_V24_VINE = {10: (354.45, 164.28), 12: (-166.07, -105.93), 14: (-594.79, -410.72)}
for it in ITEMS:
    if it['mesh'] == 'vine_arch' and it['layer'] == 'Arches' and it['scale'] == 0.7 and it['pad'] in _V24_VINE: it['x'], it['z'] = _V24_VINE[it['pad']]; V19['v24VineMoved'] = V19.get('v24VineMoved', 0) + 1
    elif it['mesh'] == 'ruin_arch' and abs(it['x'] + 383.9) < 0.3 and abs(it['z'] + 229.3) < 0.3: it['yaw'] = 80.7; V19['v24Arch13Yaw'] = 80.7
    elif it['mesh'] == 'lantern_hanging' and abs(it['x'] + 392.3) < 0.3 and abs(it['z'] + 230.2) < 0.3: it['x'], it['z'], it['yaw'] = -384.8, -220.9, 80.7
# a5) v21: a few edge stones along the trail beside the tees of pads 1, 2, 4, 5 (rock_s, 6 studs apart, alternating sides, within 36 studs of the tee)
rg5 = np.random.default_rng(2026112); nst5 = 0
for n_ in (1, 2, 4, 5):
    tx_, tz_ = _tees20[n_]
    idx_ = [i for i in range(len(_rp_)) if math.hypot(_rp_[i][0] - tx_, _rp_[i][1] - tz_) < 36.0]
    last_s = -99.0; side_ = 1
    for i in idx_[::1]:
        if _rs_[i] - last_s < 6.0 or i == 0 or i >= len(_rp_) - 1: continue
        t_ = _rp_[i + 1] - _rp_[i - 1]; t_ = t_ / (np.hypot(*t_) + 1e-9); nr_ = np.array([-t_[1], t_[0]]) * side_
        px_, pz_ = _rp_[i] + nr_ * (_hw20(i) + 0.9)
        ITEMS.append(dict(mesh='rock_s', x=round(float(px_), 2), z=round(float(pz_), 2), yaw=round(float(rg5.uniform(0, 360)), 1), scale=round(float(rg5.uniform(0.8, 1.1)), 3), layer='Edge', pad=n_)); nst5 += 1
        last_s = _rs_[i]; side_ = -side_
V19['edgeStonesPads1245'] = nst5
# a6) v21 tee-exit markers (no lights): a pair of short rope-wrapped wooden posts (3 studs, wood (110,70,40)) straddling the trail just ahead of the tee on pads 1, 2, 4, 5, 7, 8, 9, 11,
#     with a kit_v1_2 rock_s at the foot of each post
nmk = 0; _MKPOS = []
for n_ in (1, 2, 4, 5, 7, 8, 9, 11):
    best_ = None
    for sg_ in (1, -1):
        ex_, ez_ = to_world(n_, sg_ * 32.0, -18.0); dd_, ii_ = _kd.query([ex_, ez_])
        if best_ is None or dd_ < best_[0]: best_ = (dd_, int(ii_))
    ii_ = min(max(best_[1], 1), len(_rp_) - 2)
    t_ = _rp_[ii_ + 1] - _rp_[ii_ - 1]; t_ = t_ / (np.hypot(*t_) + 1e-9); nr_ = np.array([-t_[1], t_[0]]); yw_ = math.degrees(math.atan2(t_[0], t_[1]))
    for sd_ in (1, -1):
        px_, pz_ = _rp_[ii_] + nr_ * sd_ * (_hw20(ii_) + 0.9)
        WALK.append(['mk', round(float(px_), 2), round(float(pz_), 2), round(yw_, 1), 3.0, 0]); nmk += 1
        rx_, rz_ = _rp_[ii_] + nr_ * sd_ * (_hw20(ii_) + 1.9) + t_ * 0.4
        ITEMS.append(dict(mesh='rock_s', x=round(float(rx_), 2), z=round(float(rz_), 2), yaw=round(float(rg5.uniform(0, 360)), 1), scale=0.34, layer='Edge', pad=n_))     # v22: foot rock top <= post base + 1 (rock_s 2.7 high x 0.34 = 0.9)
        _MKPOS.append((float(px_), float(pz_)))
# v22: no hedge rock / fern on a post (Studio v21: 3 posts stood on 4-stud Edge rocks and ferns hid the shafts): drop the Edge plants and rocks within 3.5 studs of a post, except the foot rocks themselves
_k22 = []; _nrm = 0
for it in ITEMS:
    if it['layer'] == 'Edge' and it['mesh'] in ('rock_s', 'fernclump', 'leafclump') and not (it['mesh'] == 'rock_s' and it['scale'] == 0.34) and any(math.hypot(it['x'] - px, it['z'] - pz) < 3.5 for px, pz in _MKPOS): _nrm += 1; continue
    _k22.append(it)
ITEMS[:] = _k22; # a7) v22 (Game Art Bot): pad 1 sits behind the wreck rail, so the tee exit was not visible. A short gangplank with rope posts is built at the rail gap in the pad 1 frame
#     (WALK 'gp': x, z, yaw, length, width; the placer sets the near end on the deck (felt top + 5.9) and the far end on the ground; rope posts at both ends, a rope along each side). Position tuned / verified in Studio.
WALK.append(['gp', -462.5, 257.1, 77.2, 29.74, 4.0])   # v22 Studio final: centre xz, yaw (deg), horizontal length, width: deck top (-477.0, 32.9, 253.8) in the bow gap down to the trail head (-448.0, 4.2, 260.4)
# a8) v22: pads 6-9 each get a 10-stud-wide sightline gap through the planting from the tee to the trail (segment tee -> the trail point ahead on the exit side, about 67 studs out); low plants (under 2 studs) stay at the sides
_n_gap = 0; _gap_seg = {}
for n_ in (6, 7, 8, 9):
    tx_, tz_ = to_world(n_, 0.0, -27.0); best_ = None
    for sg_ in (1, -1):
        ex_, ez_ = to_world(n_, sg_ * 32.0, 40.0); dd_, ii_ = _kd.query([ex_, ez_])
        if best_ is None or dd_ < best_[0]: best_ = (dd_, int(ii_))
    px_, pz_ = _all_[best_[1]]; _gap_seg[n_] = (tx_, tz_, float(px_), float(pz_))
_k23 = []
for it in ITEMS:
    drop_ = False
    if it['mesh'] in ('fernclump', 'leafclump', 'vine_strip', 'palm_s', 'palm_m', 'palm_l', 'palm_lean_a', 'palm_lean_b', 'rock_m', 'rock_l') and it['layer'] not in ('Backdrop', 'Skyline', 'Hang', 'Vines', 'Arches') and HEIGHT[it['mesh']] * it['scale'] >= 2.0:
        for n_, (ax_, az_, bx_, bz_) in _gap_seg.items():
            if _seg_d(it['x'], it['z'], ax_, az_, bx_, bz_) < 5.0 and math.hypot(it['x'] - ax_, it['z'] - az_) > 14.0: drop_ = True; break
    if drop_: _n_gap += 1
    else: _k23.append(it)
ITEMS[:] = _k23; V19['sightlineGapDropped'] = _n_gap; V19['sightlineGapSegments'] = {str(k): [round(x, 1) for x in v] for k, v in _gap_seg.items()}
# a6b) v22: a second marker pair on the ahead spur of pads 2-9 (about 60 studs ahead of the tee in the pad frame) so the posts are inside the plain tee view; 4.5 studs tall
for n_ in range(2, 10):
    k_ = len(_sp_) - 8 + (n_ - 2)
    if k_ >= len(_sp_): continue
    sp_ = _sp_[k_]; vv_ = [uvp(n_, p[0], p[1])[1] + 27.0 for p in sp_]; j_ = int(np.argmin([abs(v - 62.0) for v in vv_]))
    j_ = min(max(j_, 1), len(sp_) - 2); t_ = sp_[j_ + 1] - sp_[j_ - 1]; t_ = t_ / (np.hypot(*t_) + 1e-9); nr_ = np.array([-t_[1], t_[0]]); yw_ = math.degrees(math.atan2(t_[0], t_[1]))
    for sd_ in (1, -1):
        px_, pz_ = sp_[j_] + nr_ * sd_ * (4.0 + 0.9)
        WALK.append(['mk', round(float(px_), 2), round(float(pz_), 2), round(yw_, 1), 4.5, 0]); nmk += 1
        ITEMS.append(dict(mesh='rock_s', x=round(float(sp_[j_][0] + nr_[0] * sd_ * 5.9), 2), z=round(float(sp_[j_][1] + nr_[1] * sd_ * 5.9), 2), yaw=round(float(rg5.uniform(0, 360)), 1), scale=0.34, layer='Edge', pad=n_)); _MKPOS.append((float(px_), float(pz_)))
# a9) v22 Studio final: the big dark rock left of the pad 14 tee view is boulder_pile@Set2 at (-635.0, -385.2): scaled to 0.55 (31.4 x 19.3 x 19.6 -> 17.3 x 10.6 x 10.8), base on the ground
_n14r = 0
for it in ITEMS:
    if it['mesh'] == 'boulder_pile' and abs(it['x'] + 635.0) < 1.0 and abs(it['z'] + 385.2) < 1.0: it['scale'] = round(it['scale'] * 0.55, 3); _n14r += 1
V19['pad14RocksShrunk'] = _n14r
V19['teeExitMarkers'] = nmk; V19['markerClearedEdge'] = _nrm
V19['overheadCleared'] = nov; V19['palmsTeeCone'] = npalm_tee
V19['pathsRemoved'] = n20; V19['pathsRemovedClearingOnly'] = h20
# b) stepping stones where the trail crosses rock
WALK_ST = 0
rst = np.random.default_rng(20261121)
for (sx, sz) in _R20['stones']:
    WALK.append(['st', float(sx), float(sz), float(rst.uniform(0, 360)), float(rst.uniform(2.6, 3.6))]); WALK_ST += 1
V19['trailStones'] = WALK_ST
# b) hub props
_hub = [c for c in _R20['clearings'] if c['kind'] == 'hub'][0]
_k = int(np.argmin(np.hypot(*(_rp_ - [_hub['x'], _hub['z']]).T))); _tg = _rp_[min(_k + 1, len(_rp_) - 1)] - _rp_[max(_k - 1, 0)]; _tg = _tg / (np.hypot(*_tg) + 1e-9); _nm = np.array([-_tg[1], _tg[0]])
def _hubp(off_n, off_t=0.0): return (round(float(_hub['x'] + _nm[0] * off_n + _tg[0] * off_t), 2), round(float(_hub['z'] + _nm[1] * off_n + _tg[1] * off_t), 2))
moved20 = []
for l in LANT:
    if l['kind'] == 'back' and l['pad'] == 11:
        l['x'], l['z'] = _hubp(10.0, 0.0); moved20.append('back torch pad 11')
LANT.append(dict(kind='hub', pad=11, x=_hubp(-10.0, 0.0)[0], z=_hubp(-10.0, 0.0)[1], mesh='torch_tiki', scale=1.25)); moved20.append('second tiki torch (new)')
for it in ITEMS:
    if it['mesh'] == 'lantern_post' and it['pad'] == 11:
        it['x'], it['z'] = _hubp(9.0, 11.0); moved20.append('lantern_post pad 11')
V19['hubProps'] = moved20; V19['hub'] = [_hub['x'], _hub['z']]
# c) pad 11 back view
_uv = lambda m_, x_, z_: uvp(m_, x_, z_)
keep20c, rows20 = [], []
for it in ITEMS:
    if it['layer'] == 'Backdrop': keep20c.append(it); continue
    u, v = _uv(11, it['x'], it['z']); du, dv = u, v + 27.0; d_ = math.hypot(du, dv)
    inbk = dv < 0 and abs(du) <= math.tan(math.radians(70)) * -dv
    if dv < 0 and it['mesh'] == 'canopy_wall' and d_ <= 130: rows20.append(['canopy_wall', round(d_, 1), it['x'], it['z']]); continue
    if inbk and d_ <= 110 and it['mesh'] in ('leafclump', 'fernclump'):
        eye = _PT14[11] + 5.0; g = gy14(it['x'], it['z']) + it.get('dy', 0); top = g + HEIGHT[it['mesh']] * it['scale']
        if top > eye - 0.5: rows20.append([it['mesh'], round(d_, 1), it['x'], it['z'], round(top - eye, 1), it['layer']]); continue
    keep20c.append(it)
ITEMS[:] = keep20c; V19['pad11BackRemoved'] = rows20[:40]
# c) pad 12 back view: fill near-black gaps (no canopy item within 16 studs, 28..110 studs out, +-50 deg) with eye-capped leaf clumps
rg = np.random.default_rng(20261122); fill12 = []
cands12 = [it for it in ITEMS if it['layer'] != 'Backdrop' and it['mesh'] in ('leafclump', 'canopy_wall', 'palm_l', 'palm_m', 'palm_lean_a', 'palm_lean_b')]
ctree = _KD([[it['x'], it['z']] for it in cands12]) if cands12 else None
eye12 = _PT14[12] + 5.0
for d_ in np.arange(30.0, 110.0, 12.0):
    for a_ in np.arange(-50.0, 51.0, 10.0):
        u = math.tan(math.radians(a_)) * d_; x_, z_ = to_world(12, u, -27.0 - d_)
        i_, j_ = ij(x_, z_)
        if not inb(i_, j_): continue
        if ctree is not None and ctree.query([x_, z_])[0] < 16.0: continue
        if h2[ij(x_, z_)] < 1.0: continue
        _dt, _it_ = _kd.query([x_, z_])
        if _dt < _hw20(int(_it_)) + 9.0: continue                      # run-2: gap fill must stay off the trail (leafclumps are 21-24 wide)
        g = gy14(x_, z_); allow = eye12 - 1.5 - g
        sc = min(1.0, allow / HEIGHT['leafclump'])
        if sc < 0.45: continue
        fill12.append(dict(mesh='leafclump', x=round(float(x_ + rg.uniform(-3, 3)), 2), z=round(float(z_ + rg.uniform(-3, 3)), 2), yaw=round(float(rg.uniform(0, 360)), 1), scale=round(float(sc * rg.uniform(0.85, 1.0)), 3), layer='Far', pad=12))
ITEMS.extend(fill12); V19['pad12GapFill'] = len(fill12)
# d) pads 16-18 boulders
rbo = np.random.default_rng(20261123); nb = 0; nsw = 0; seq = 0
for it in ITEMS:
    if it['mesh'] == 'boulder_pile' and it['pad'] in (16, 17, 18):
        seq += 1; fp = max(KIT['boulder_pile']['size'][0], KIT['boulder_pile']['size'][2]) / 2 * it['scale']
        if seq % 2 == 0:
            nm_ = 'rock_l' if seq % 4 == 0 else 'rock_m'
            it['mesh'] = nm_; it['scale'] = round(float(min(max(fp / (max(KIT[nm_]['size'][0], KIT[nm_]['size'][2]) / 2) * rbo.uniform(0.9, 1.15), 0.6), 4.0)), 3); it['layer'] = it['layer']; nsw += 1
        else:
            it['scale'] = round(float(it['scale'] * rbo.uniform(0.75, 1.25)), 3)
        it['yaw'] = round(float(rbo.uniform(0, 360)), 1); nb += 1
keepb, seen_b, nb_drop = [], [], 0
for it in ITEMS:
    if it['mesh'] in ('boulder_pile', 'rock_m', 'rock_l') and it['layer'] == 'Set2' and it.get('pad') in (16, 17, 18):
        it['scale'] = round(min(it['scale'], 2.4), 3) if it['mesh'] != 'boulder_pile' else it['scale']
        dd_, ii_ = _kd.query([it['x'], it['z']]); fpb = max(KIT[it['mesh']]['size'][0], KIT[it['mesh']]['size'][2]) / 2 * it['scale'] * 0.8
        if dd_ < fpb + 1.0 or any(math.hypot(it['x'] - a_, it['z'] - b_) < 2.5 for a_, b_ in seen_b): nb_drop += 1; continue
        seen_b.append((it['x'], it['z']))
    keepb.append(it)
ITEMS[:] = keepb
V19['boulders1618'] = dict(varied=nb, swappedToRocks=nsw, droppedOnTrailOrDuplicate=nb_drop)
# ---------------------------------------------------------------- 6. metrics
need_m = np.zeros((NZ, NX), bool)
for n in range(2, 19): need_m |= zone_need(n, 100)
E = ndi.distance_transform_edt(need_m & ~cover) * RES
Ej = {}
for n in range(2, 19):
    m = zone_need(n, 100); Ej[n] = round(float(2 * (ndi.distance_transform_edt(m & ~cover) * RES)[m].max()), 1) if m.any() else 0
E2 = ndi.distance_transform_edt(need_m & ~cover & ~inner_lane) * RES
Ek = {n: round(float(2 * (ndi.distance_transform_edt(zone_need(n, 100) & ~cover & ~inner_lane) * RES).max()), 1) for n in range(2, 19)}
metrics = dict(maxBareDiameterIncludingTrail=round(float(2 * E.max()), 1), maxBareDiameterExcludingTrail=round(float(2 * E2.max()), 1),
               perPadMaxBareDiameterExcludingTrail=Ek, perPadMaxBareDiameterIncludingTrail=Ej)
cnt = {}; tris = 0
for it in ITEMS:
    cnt[it['mesh']] = cnt.get(it['mesh'], 0) + 1; tris += KIT[it['mesh']]['tris']
metrics.update(counts=cnt, total=len(ITEMS), trisTotal=int(tris), fillLog={str(k): v for k, v in FILL_LOG.items()},
               debrisGroups=DEBRIS_G, hullRibs=RIBS, palms=sum(v for k, v in cnt.items() if k.startswith('palm')), palmClumps=len(PALMS), palmsPerClump=[p[2] for p in PALMS], ringStations=RING_N, barePatches=PATCHES, pad15Vines=P15, wreckExtra=WRECK_EXTRA, arches=len(ARCHES), vineStripsTerrain=VINE_T, caveProbes=len(CAVE_PROBES), v11=dict(teeApproach={str(k): v for k, v in V11['tee'].items()}, overheadPalms={str(k): v for k, v in V11['overhead'].items()}, setPieces={str(k): v for k, v in SET_PIECES.items()}, skyline={str(k): v for k, v in SKY.items()}, pad15=P15V11, fgLog={str(k): v for k, v in FG_LOG.items()}, brownClumps=BROWN, jungleWalk=JW, walkParts=len(WALK), lanterns=len(LANT), skyStacks=len(SKY_STACKS)))
metrics['v12'] = V12
metrics['v13'] = V13; metrics['v14'] = V14; metrics['v16'] = V16; metrics['v19'] = V19
metrics['layers'] = {l: sum(1 for it in ITEMS if it['layer'] == l) for l in sorted({it['layer'] for it in ITEMS})}
# per-pad tris within 120 studs of the pad centre (visible budget estimate)
vis = {}
for n in range(1, 19):
    t = 0
    for it in ITEMS:
        if it['layer'] == 'Backdrop': continue
        if math.hypot(it['x'] - pw[n][0], it['z'] - pw[n][1]) < 140: t += KIT[it['mesh']]['tris']
    vis[n] = t
metrics['trisWithin140OfPad'] = vis
out = dict(seed=20261031, kit='kit_v1_1 for stack_a, stack_c, reef_ring, vine_arch, rock_s, rock_m, rock_l; kit_v1 for the rest', items=ITEMS, arches=ARCHES,
           caveProbes=CAVE_PROBES, walk=WALK, lanterns=LANT, dropSide={str(k): v for k, v in DROP.items()}, metrics=metrics)
json.dump(out, open(f'{ROOT}/data/dressing.json', 'w'), default=lambda o: o.item() if hasattr(o, 'item') else str(o))
os.makedirs(f'{ROOT}/import', exist_ok=True)
# v22 Studio final: the 10 pad 12 leafclump@Far items (tops 2.5-3.8 over the felt on slopes, missed by the eye cap, which reads the centre ground) are dropped; they are made after the a-rules, so the drop is here
_FAR12 = [(-75.3, -77.7), (-76.0, -71.1), (-64.0, -68.7), (-67.3, -62.4), (-48.5, -71.7), (-52.0, -63.5), (-67.7, -12.0), (-42.3, -58.1), (-52.1, -12.6), (-28.9, -50.0)]
_n12 = len(ITEMS); ITEMS[:] = [it for it in ITEMS if not (it['mesh'] == 'leafclump' and any(abs(it['x'] - x) < 0.2 and abs(it['z'] - z) < 0.2 for x, z in _FAR12))]
V19['pad12FarLeafDropped'] = _n12 - len(ITEMS)
compact = dict(items=[[it['mesh'], it['x'], it['z'], it['yaw'], it['scale'], it['layer'], tint_of(it['x'], it['z']) if it['layer'] not in ('Backdrop', 'Skyline') else 0, it.get('dy', 0)] + ([it['gp']] if 'gp' in it else []) for it in ITEMS], probes=CAVE_PROBES, walk=WALK, lanterns=LANT)
json.dump(compact, open(f'{ROOT}/import/dressing_data.json', 'w'), separators=(',', ':'), default=lambda o: o.item())
print(json.dumps(metrics, indent=None, default=lambda o: o.item())); print('stacks', BACK[:3], 'ribs', rib_pts[:4])

# ---------------------------------------------------------------- summary into placements.json (make_blockout rewrites that file, so this runs after it)
from layout import PAD_RAISE, PAD_TOP, PLATEAU_BELOW
PJ = json.load(open(f'{ROOT}/data/placements.json'))
PJ['dressing'] = dict(
    version='v14', seed=20261031, generator='source/make_dressing.py -> data/dressing.json, import/dressing_data.json; source/build_dressing_luau.py -> import/dressing_place.luau',
    kitSource=dict(kit_v1_1=['stack_a', 'stack_c', 'reef_ring', 'vine_arch', 'rock_s', 'rock_m', 'rock_l'],
                   kit_v1='all other kit meshes', note='the 7 kit_v1_1 meshes are still in Game Art Bot review'),
    kitAssets='data/kit_assets_v9.json (MeshId/TextureID per mesh, uploaded by Studio Asset Manager import into the private place)',
    padRaise={str(k): v for k, v in PAD_RAISE.items()}, padTop={str(k): v for k, v in PAD_TOP.items()}, plateauBelow=PLATEAU_BELOW,
    terrainBiasNote='Roblox renders flat voxel terrain ~1.97 studs above the heightmap value; pad plateaus are written 2.5 below the felt top so rendered ground sits ~0.5 under it.',
    vineArchSlots=[dict(x=round(a[0], 1), z=round(a[1], 1), yawDeg=round(a[2], 1)) for a in ARCHES],
    captainLedge='flat ledge radius 17 + 16 blend at (556.65,-517.61), heightmap 98.43 (renders ~100.4)',
    metrics=metrics)
json.dump(PJ, open(f'{ROOT}/data/placements.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
