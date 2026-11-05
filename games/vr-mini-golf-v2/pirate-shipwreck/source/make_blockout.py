#!/usr/bin/env python3
"""Generate the Pirate Shipwreck blockout data (world only, no holes).

Outputs (relative to the course folder):
  data/heightmap.png        16-bit grayscale, 1 px = 4 studs, 1024x640. stud = HMIN + v/65535*(HMAX-HMIN)
  data/materialmap.png      8-bit palette PNG, same grid. ids: see MATERIALS
  data/placements.json      pads, rest stops, wreck / cave stand-ins, hero footprints, prop anchors
  data/lighting.json        look B lighting / atmosphere / post values
  data/world.json           grid + transform constants
  data/blockout-report.json automatic checks (pad clearances, overlaps, slopes)
  preview/layout-topdown.png, preview/heightmap-preview.png, preview/trail-profile.png
  import/import_world.luau  Studio import script with the data embedded (see make_import.py)
Re-run: python3 source/make_blockout.py
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(__file__))
from layout import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = '/workspace/gameart/pirate-shipwreck/r1/raw/map_base1.png'
rng = np.random.default_rng(1031)

MATERIALS = {0: 'Air', 1: 'Sand', 2: 'LeafyGrass', 3: 'Rock', 4: 'Slate', 5: 'Ground', 6: 'Grass', 7: 'Mud', 8: 'Sandstone', 9: 'Limestone'}
MAT_RGB = {1:(226,184,128), 2:(106,150,62), 3:(158,148,116), 4:(132,128,110), 5:(172,142,88), 6:(120,156,60), 7:(110,80,55), 8:(236,200,150), 9:(140,125,112)}

def smooth(t):
    t = np.clip(t, 0, 1); return t*t*(3-2*t)

# ---------------------------------------------------------------- land mask from the map
im = Image.open(BASE).convert('RGB').resize((MAP_W, MAP_H), Image.LANCZOS)
A = np.asarray(im).astype(int); R, G, B = A[...,0], A[...,1], A[...,2]
water = (B > R + 45) & (B >= G - 10)
lab, n = ndi.label(ndi.binary_opening(water, iterations=3))
border = set(np.unique(np.r_[lab[0], lab[-1], lab[:,0], lab[:,-1]])) - {0}
sea = np.isin(lab, list(border)); sea = (ndi.binary_dilation(sea, iterations=2) & water) | sea
land = ~sea
ship = Image.new('L', (MAP_W, MAP_H), 0)
SHIP_POLY = [(5,285),(55,232),(120,224),(200,250),(250,290),(255,330),(235,352),(150,352),(60,345),(5,320)]
ImageDraw.Draw(ship).polygon(SHIP_POLY, fill=255)      # the concept map's (oversized) ship: this is water in the blockout
land &= ~(np.asarray(ship) > 0)
land = ndi.binary_fill_holes(ndi.binary_closing(land, iterations=3))
lab, n = ndi.label(land); sizes = ndi.sum(land, lab, range(1, n + 1)); land = lab == (1 + int(np.argmax(sizes)))
# the island is cut by the top edge of the concept map: pad it upward with a rounded cap
PADN = 40
land = np.pad(land, ((PADN, 0), (0, 0)), mode='edge')
land[:PADN, :] &= True
cap = np.zeros_like(land); yy, xx = np.mgrid[0:land.shape[0], 0:land.shape[1]]
land_f = ndi.gaussian_filter(land.astype(float), 3) > 0.5
# fade the cap: shrink land in the padded strip toward its middle
strip = np.arange(land.shape[0])[:, None] < PADN
shrink = np.clip((PADN - np.arange(land.shape[0])[:, None]) / PADN, 0, 1) * 70      # px inset at the very top
r0 = int(np.nonzero(land.any(axis=1))[0][0]); cxm = np.nonzero(land[r0])[0]; midx = (cxm.min() + cxm.max()) / 2
half = (cxm.max() - cxm.min()) / 2
inset_ok = np.abs(xx - midx) < (half - shrink)
land_cap = np.where(strip, land & inset_ok, land)
land = ndi.binary_closing(land_cap, iterations=2)
Y_OFF = PADN                     # land image rows are offset by PADN px (map y = row - PADN)

def land_sample_field():
    d_in = ndi.distance_transform_edt(land)
    d_out = ndi.distance_transform_edt(~land)
    sd = (d_in - d_out) * S                                     # signed distance, studs (positive inland)
    return ndi.gaussian_filter(sd, 2.0)
SD_PX = land_sample_field()                                   # on the padded px grid

# grid cell centres -> map px (padded rows)
ii, jj = np.meshgrid(np.arange(GW), np.arange(GH))            # ii = x index, jj = z index
WX = X0 + ii * CELL + CELL / 2; WZ = Z0 + jj * CELL + CELL / 2
PXX = WX / S + CX; PXY = WZ / S + CZ + Y_OFF
def sample(field, order=1, mode='nearest'):
    return ndi.map_coordinates(field, [PXY, PXX], order=order, mode=mode)
SD = sample(SD_PX)
# beyond the padded map the sea continues: distance keeps growing negative
outside = (PXX < 0) | (PXX > MAP_W - 1) | (PXY < 0) | (PXY > land.shape[0] - 1)
cl_x = np.clip(PXX, 0, MAP_W - 1); cl_y = np.clip(PXY, 0, land.shape[0] - 1)
edge_d = np.hypot(PXX - cl_x, PXY - cl_y) * S
SD = np.where(outside, np.minimum(SD, -edge_d - 60), SD)

# ---------------------------------------------------------------- layout geometry (world studs)
pads_w = pad_pos_w()
cl = catmull([px2w(x, y) for _, _, x, y in PADS_PX], per=40)         # trail polyline (world)
cl = np.array(cl)
# cumulative arc length and elevations along the trail
seg = np.r_[0, np.cumsum(np.hypot(*np.diff(cl, axis=0).T))]
pad_s = []
for n_, z, x, y in PADS_PX:
    p = np.array(px2w(x, y)); k = int(np.argmin(np.hypot(*(cl - p).T))); pad_s.append(seg[k])
pad_s = np.array(pad_s); pad_e = np.array([PAD_ELEV[n_] for n_, *_ in PADS_PX])
def trail_elev(s):
    # flat at each pad, smoothstep between neighbours
    out = np.empty_like(s, dtype=float)
    for i, v in enumerate(s):
        if v <= pad_s[0]: out[i] = pad_e[0]; continue
        if v >= pad_s[-1]: out[i] = pad_e[-1]; continue
        k = int(np.searchsorted(pad_s, v) - 1)
        t = (v - pad_s[k]) / (pad_s[k+1] - pad_s[k])
        flat = 0.18                                        # keep the first / last 18% of each leg level
        t = smooth((t - flat) / (1 - 2*flat))
        out[i] = pad_e[k] + (pad_e[k+1] - pad_e[k]) * t
    return out
cl_e = trail_elev(seg)
# v9: terrace the climb to the cave (legs 15->16, 16->17, 17->18): level treads with short risers about 3 studs high
def terrace(e_arr):
    out = e_arr.copy()
    for k in (14, 15, 16):
        a, b = pad_s[k], pad_s[k+1]; m = (seg >= a) & (seg <= b)
        dh = pad_e[k+1] - pad_e[k]; n_st = max(2, int(round(dh / 3.0)))
        t = (seg[m] - a) / (b - a); t = np.clip((t - 0.18) / 0.64, 0, 1) * n_st
        fl = np.floor(np.minimum(t, n_st - 1e-9)); fr = t - fl
        st = (fl + smooth((fr - 0.86) / 0.14)) / n_st
        out[m] = pad_e[k] + dh * st
    return out
cl_e = terrace(cl_e)
# trail starts at pad 2 for terrain purposes (pad 1 -> 2 is a gangway across the surf, no causeway)
i2 = int(np.argmin(np.abs(seg - pad_s[1])))
corr_pts = cl[i2:]; corr_e = cl_e[i2:]

# pad orientation: along the trail (direction of play)
tang = np.gradient(cl, axis=0)
pad_yaw = {}
for (n_, z, x, y), s in zip(PADS_PX, pad_s):
    k = int(np.argmin(np.abs(seg - s))); t = tang[k]; t = t / np.hypot(*t)
    pad_yaw[n_] = math.degrees(math.atan2(t[0], t[1]))
    if n_ == 18:   # last pad: keep the previous tangent (trail ends here)
        pass
# rest stops
rest_w = []
for n_, x, y in REST_PX:
    p = np.array(px2w(x, y)); k = int(np.argmin(np.hypot(*(corr_pts - p).T)))
    rest_w.append((n_, p, corr_pts[k], float(corr_e[k])))

# wreck placement (room decision: wreck v2 mesh, 320 x 90 x 60). Local frame: Y 0 = water line, X 0 = centreline, Z 0 = midship,
# +Z = bow (lagoon), -Z = stern (beach). The stern end touches the sand; the rest of the hull is in the lagoon.
def sd_at(X, Z):
    return float(SD[int(np.clip((Z - Z0) // CELL, 0, GH-1)), int(np.clip((X - X0) // CELL, 0, GW-1))])
ax = WRECK_AXIS                                  # bow -> stern, world (X,Z)
p1_old = np.array(pads_w[1])                     # old pad 1 map position (only used to pick the line the ship lies on)
line_pts = [p1_old + ax * t for t in np.arange(-200, 400, 2.0)]
# stern end: first point (walking from the lagoon toward the beach) where the signed shore distance reaches +STERN_INLAND
STERN_INLAND = 6.0
stern_end = next(q for q in line_pts if sd_at(*q) >= STERN_INLAND)
bow_end = stern_end - ax * WRECK_LEN
wreck_c = stern_end - ax * (WRECK_LEN / 2)       # geometric centre (stern/bow midpoint)
wreck_origin = stern_end - ax * WRECK_STERN_Z    # local origin = midship (hull z range is about -160 .. +166)
ship_yaw_bow = math.degrees(math.atan2(-ax[0], -ax[1]))          # local +Z points to the bow
bowdir = -ax
pad1_xz = wreck_origin + bowdir * PAD1_LOCAL_Z   # pad 1 deck centre, local (0, 24, -110)
pads_w[1] = (float(pad1_xz[0]), float(pad1_xz[1]))
pad_yaw[1] = math.degrees(math.atan2(ax[0], ax[1]))              # pad 1 plays toward the stern/beach
p1 = np.array(pads_w[1])
hull_rect = rect_corners(*wreck_c, WRECK_WID, WRECK_LEN, ship_yaw_bow)
wreck_sd = {}
for nm, s_ in (('stern_end', 0), ('stern+30', 30), ('stern+60', 60), ('midship', 160), ('bow', 300)):
    q = stern_end - ax * s_
    perp = np.array([ax[1], -ax[0]])
    wreck_sd[nm] = [round(sd_at(*(q + perp * o)), 1) for o in (-45, 0, 45)]
# cave cliff: front face CLIFF_FRONT_GAP north of pad 18, mouth centred on pad 18's X
p18 = np.array(pads_w[18])
cliff_front_z = p18[1] - CLIFF_FRONT_GAP
cliff_center = np.array([p18[0] - 20.0, cliff_front_z - CLIFF_D / 2])
mouth_x = p18[0]
falls_x = cliff_center[0] - 80.0
pool_c = np.array([falls_x, cliff_center[1] + 44.0])      # cave v1 mesh: pool tub at local (-80, 48.4, 44)

# ---------------------------------------------------------------- natural terrain
def fbm(shape, scales, amps):
    out = np.zeros(shape)
    for s, a in zip(scales, amps):
        f = ndi.gaussian_filter(rng.standard_normal(shape), s); f /= f.std() + 1e-9; out += f * a
    return out
noise = fbm((GH, GW), (6, 14, 30), (1.0, 1.6, 2.4))                 # smooth, compresses well

d = SD
below = d < 0
h_sea = -26.0 * (1 - np.exp(np.minimum(d, 0) / 140.0))
h_beach = 3.0 * smooth(np.maximum(d, 0) / 45.0)
base = np.where(below, h_sea, h_beach)

# trail elevation diffused over the land (normalised convolution) -> natural inland height
def gridix(P):
    return (np.clip(((P[:,0] - X0) / CELL).astype(int), 0, GW-1), np.clip(((P[:,1] - Z0) / CELL).astype(int), 0, GH-1))
Em = np.zeros((GH, GW)); Mm = np.zeros((GH, GW))
gx, gz = gridix(corr_pts); Em[gz, gx] = corr_e; Mm[gz, gx] = 1
sig = 150 / CELL
Hfill = ndi.gaussian_filter(Em, sig) / np.maximum(ndi.gaussian_filter(Mm, sig), 1e-6)
wl = smooth((d - 30) / 160.0)
# jungle floor sits a little above the trail so the trail reads as cut through it
jung_up = 5.5 * wl * smooth((d - 80) / 120.0)
# cliff massif dome (north-east), elliptical
dx = (WX - (cliff_center[0] - 10)) / 330.0; dz = (WZ - (cliff_center[1] + 40)) / 230.0
dome = 38.0 * np.exp(-(dx**2 + dz**2) * 1.3) * smooth((d - 20) / 80.0)
h = base + wl * (np.maximum(Hfill, 3.0) - 3.0) + jung_up * 0 + wl * noise * 1.6 + jung_up + dome

# trail corridor (full flat <= 14 studs, blends to 0 at 46)
def nearest(P, E, pts_x, pts_z):
    from scipy.spatial import cKDTree
    tree = cKDTree(P)
    dist, idx = tree.query(np.c_[pts_x.ravel(), pts_z.ravel()])
    return dist.reshape(pts_x.shape), E[idx].reshape(pts_x.shape)
fine = []
fe = []
for a_, b_, ea, eb in zip(corr_pts[:-1], corr_pts[1:], corr_e[:-1], corr_e[1:]):
    L = np.hypot(*(b_ - a_)); m = max(2, int(L / 4))
    for t in np.linspace(0, 1, m, endpoint=False):
        fine.append(a_ + (b_ - a_) * t); fe.append(ea + (eb - ea) * t)
fine = np.array(fine); fe = np.array(fe)
# spurs to rest stops (straight, level with the point they leave the trail)
spur_pts, spur_e = [], []
for n_, p, q, e in rest_w:
    L = np.hypot(*(p - q)); m = max(2, int(L / 4))
    for t in np.linspace(0, 1, m):
        spur_pts.append(q + (p - q) * t); spur_e.append(e)
all_pts = np.vstack([fine, np.array(spur_pts)]); all_e = np.r_[fe, np.array(spur_e)]
cdist, celev = nearest(all_pts, all_e, WX, WZ)
wt = 1 - smooth((cdist - 14) / 32.0)
wt *= (d > 8)                                # never carve the trail into open sea
h = h * (1 - wt) + (celev - 1.0) * wt

def rect_sdf(cx, cz, w, l, yaw):
    th = math.radians(yaw); axx = np.array([math.cos(th), -math.sin(th)]); azz = np.array([math.sin(th), math.cos(th)])
    rx = WX - cx; rz = WZ - cz
    u = rx * axx[0] + rz * axx[1]; v = rx * azz[0] + rz * azz[1]
    qx = np.abs(u) - w / 2; qz = np.abs(v) - l / 2
    return np.hypot(np.maximum(qx, 0), np.maximum(qz, 0)) + np.minimum(np.maximum(qx, qz), 0)
def pad_uv(cx, cz, yaw):
    th = math.radians(yaw); axx = np.array([math.cos(th), -math.sin(th)]); azz = np.array([math.sin(th), math.cos(th)])
    rx = WX - cx; rz = WZ - cz
    return rx * axx[0] + rz * axx[1], rx * azz[0] + rz * azz[1]

# ---- v9 terrain: dunes, shelves, jungle banks (all seeded by rng9, independent of the v8 noise so the v8 terrain is reproduced elsewhere)
rng9 = np.random.default_rng(9009)
def nrm(f): return (f - f.mean()) / (f.std() + 1e-9)
land_c9 = d > 0
# trail frame: nearest corridor point, signed lateral offset u (+ = left of travel), arc length s
from scipy.spatial import cKDTree
_tree = cKDTree(corr_pts); _dist, _idx = _tree.query(np.c_[WX.ravel(), WZ.ravel()])
_idx = _idx.reshape(WX.shape); _dist = _dist.reshape(WX.shape)
_tg = np.gradient(corr_pts, axis=0); _tg /= np.hypot(*_tg.T)[:, None]
_off = np.stack([WX - corr_pts[_idx, 0], WZ - corr_pts[_idx, 1]], -1)
U_lat = _tg[_idx, 0] * _off[..., 1] - _tg[_idx, 1] * _off[..., 0]        # cross(t, off) > 0: left (map frame, Z down)
S_arc = seg[i2:][_idx]
# (a) beach: rock/sand shelves stepping down to the water, replacing the smooth beach ramp (same 3-4.5 stud height inland)
shelf = 0.8 * smooth(np.maximum(d, 0) / 6.0) + 1.2 * (smooth((d - 10) / 4.5) + smooth((d - 24) / 4.5) + smooth((d - 38) / 4.5))
h_beach9 = np.where(below, h_sea, np.maximum(shelf, h_beach))
h = h + (h_beach9 - base) * (1 - smooth((d - 70) / 40.0))
# (b) dunes: soft ridges on the beach band away from the trail
dn = nrm(ndi.gaussian_filter(rng9.standard_normal((GH, GW)), 4.5)) + 0.5 * nrm(ndi.gaussian_filter(rng9.standard_normal((GH, GW)), 2.0))
dunes = 5.0 * smooth(dn * 0.9 - 0.15) * smooth((d - 14) / 22.0) * (1 - smooth((d - 100) / 50.0)) * smooth((_dist - 28) / 22.0)
h = h + dunes
# (c) jungle trail banks: the trail is cut into a slope. Pads 10-14: a 8-15 stud bank on one side (side alternates per leg), the other side drops away a little
legs9 = [(9, +1), (10, -1), (11, +1), (12, -1), (13, +1)]       # leg k = pad (k+1) -> pad (k+2); side +1 = left of travel
bank = np.zeros((GH, GW)); fall = np.zeros((GH, GW))
bn = nrm(ndi.gaussian_filter(rng9.standard_normal((GH, GW)), 7.0))
for k, sd_ in legs9:
    a_, b_ = pad_s[k], pad_s[k+1]
    inleg = smooth((S_arc - (a_ + 20)) / 40.0) * (1 - smooth((S_arc - (b_ - 60)) / 40.0))
    au = np.abs(U_lat); onside = smooth((U_lat * sd_) / 8.0 + 0.5); offside = 1 - onside
    Bk = 11.5 + 3.5 * np.clip(bn, -1, 1)                                             # 8..15
    prof = smooth((au - 16) / 12.0) * (1 - smooth((au - 36) / 45.0))
    bank = np.maximum(bank, inleg * onside * Bk * prof)
    fall = np.maximum(fall, inleg * offside * 4.0 * smooth((au - 18) / 14.0) * (1 - smooth((au - 40) / 50.0)))
bank *= smooth((d - 90) / 40.0); fall *= smooth((d - 90) / 40.0)
h = h + bank - fall
bank_mask = bank > 3.0
# (c2) v11 terraces: flat treads with short rock risers on the jungle/cave hillsides so cliffs show from above (not near the trail, rest stops or pads, which are written after)
_tz = smooth((d - 110) / 30.0) * (1 - wt) * smooth((h - 14) / 6.0) * (1 - smooth((h - 78) / 8.0)) * smooth((_dist - 40) / 20.0)
_st = 7.0; _fl = np.floor(h / _st); _fr = h / _st - _fl
_ht = (_fl + smooth((_fr - 0.8) / 0.14)) * _st
h = h * (1 - 0.65 * _tz) + _ht * 0.65 * _tz
# (d) pads: raised plinth (+2..6 studs) with a steep drop-off on one lateral side and a shallow ramp (24 studs) on the others
pad_mask = np.zeros((GH, GW)); pad_zone_mask = {}
dropwall = np.zeros((GH, GW), bool); DROP = {}
h_pre = h.copy()
def hsample(X, Z):
    return float(h_pre[int(np.clip((Z - Z0) // CELL, 0, GH-1)), int(np.clip((X - X0) // CELL, 0, GW-1))])
for n_, zname, x, y in PADS_PX:
    if n_ == 1: continue
    cx, cz = pads_w[n_]; yaw_ = pad_yaw[n_]; q = rect_sdf(cx, cz, CLEAR[0], CLEAR[1], yaw_)
    top = PAD_TOP[n_] - PLATEAU_BELOW
    if PAD_RAISE[n_] > 0:
        th = math.radians(yaw_); axx = np.array([math.cos(th), -math.sin(th)])
        hp = hsample(cx + axx[0] * 42, cz + axx[1] * 42); hm = hsample(cx - axx[0] * 42, cz - axx[1] * 42)
        sgn = 1 if hp <= hm else -1
        sgn = {13: -1}.get(n_, sgn)                       # pad 13: the flytrap hero prop stands on the +X side, so the drop-off goes to the other side
        DROP[n_] = sgn
        u, v = pad_uv(cx, cz, yaw_)
        f = smooth((u * sgn + 10) / 20.0)                    # 1 on the drop-off side
        rw = 24.0 - 18.0 * f
        wp = 1 - smooth(q / rw)
        # carve the outside of the drop-off side down so the wall is real (at least 3.2 below the plateau), fading out 30-50 studs away
        dw = f * (1 - smooth((q - 26) / 22.0)) * (q > 0)
        h = np.where(dw > 0, h * (1 - dw) + np.minimum(h, top - 3.2) * dw, h)
        dropwall |= (f > 0.45) & (q > -2) & (q < rw + 4)
    else:
        wp = 1 - smooth(q / 24.0)
    h = h * (1 - wp) + top * wp
    pad_mask = np.maximum(pad_mask, wp)
# rest stop clearings (flat disks)
rs_mask = np.zeros((GH, GW))
for n_, p, q, e in rest_w:
    r = np.hypot(WX - p[0], WZ - p[1]); wr = 1 - smooth((r - REST_SIZE * 0.62) / 22.0)
    h = h * (1 - wr) + (e - 1.0) * wr; rs_mask = np.maximum(rs_mask, wr)
# cave v1 (3D Model Bot) terrain fit. The cave mesh sits at (563.5, 66, -606.5), yaw 0; footprint x +-120, z +-70.
# 1) fill under and behind it: inside the footprint (plus a 36-stud skirt on the sides and the back, none at the front) terrain is raised to
#    at least CAVE_FILL_Y so the base is buried and the back no longer floats (it was up to about 60 studs above the hill).
# 2) mouth: the tunnel floor is Y 94 (local 28), the stairs drop from it to Y 76 at the front face. Terrain in the mouth corridor is set to
#    that profile (1 stud below the walking surface), cutting the hill (96-108 there) down so it lines up with the cave floor.
# The waterfall pool is now part of the mesh (a tub inside the footprint, surface Y 114.4), so the old terrain pool basin is gone.
CAVE_FILL_Y = CLIFF_BASE_Y + 2.0
SKIRT = 36.0
cx0, cz0 = cliff_center
fx0, fx1, fz0, fz1 = cx0 - CLIFF_W / 2, cx0 + CLIFF_W / 2, cz0 - CLIFF_D / 2, cz0 + CLIFF_D / 2     # footprint
dxo = np.maximum(np.maximum(fx0 - WX, WX - fx1), 0.0)                          # distance outside in x
dzo = np.maximum(fz0 - WZ, 0.0)                                                # outside at the back (north); front (south) has no skirt
inside_front = WZ <= fz1 + 0.0
dist_out = np.hypot(dxo, dzo)
wf = np.where(WZ > fz1, 0.0, 1 - smooth(dist_out / SKIRT))
h_before_cave = h.copy()
h = np.maximum(h, CAVE_FILL_Y * wf + h * (1 - wf))
h = np.where(wf > 0, np.maximum(h, h_before_cave), h)
# mouth corridor (widened for the bigger cave v2 mouth, same floor): x = mouth centre +-33, z from the back of the tunnel to 13 studs south of the face
mx0 = mouth_x - 33.0; mx1 = mouth_x + 33.0
cz_face = fz1                                                                  # front face z
PAD18_PLATEAU = PAD_ELEV[18] - 1.0                                             # pad 18 plateau height (88)
# v6: Roblox renders the voxel terrain surface about 2-3 studs ABOVE the heightmap value (partial-occupancy voxels), so the cut profile sits
# CUT_BELOW studs under the mesh walking surface to make the rendered terrain land about 0.8 under the floor / stair treads, never over them.
CUT_BELOW = 3.5
def mouth_profile(Z):
    stair_top_z = cz0 + 29.6                                                   # local z where the stairs start dropping from the mouth floor
    floor = CAVE_MOUTH_FLOOR_Y - CUT_BELOW
    stair_bot = 76.0 - 2.0                                                     # gentler at the very front so the ramp to the pad 18 plateau is not steeper than before
    p = np.where(Z <= stair_top_z, floor, floor + (stair_bot - floor) * np.clip((Z - stair_top_z) / (cz_face - stair_top_z), 0, 1))
    # in front of the face: a short ramp up to pad 18's plateau edge (its art-clear rect starts 13 studs in front of the face)
    return np.where(Z > cz_face, stair_bot + (PAD18_PLATEAU - stair_bot) * np.clip((Z - cz_face) / 13.0, 0, 1), p)
lat = np.maximum(np.maximum(mx0 - WX, WX - mx1), 0.0)
lon_back = np.maximum((cz0 - 12.0 - 6.0) - WZ, 0.0)
lon_front = np.maximum(WZ - (cz_face + 13.0), 0.0)
dm = np.hypot(lat, np.maximum(lon_back, lon_front))
wm = 1 - smooth(dm / 10.0)
prof = mouth_profile(WZ)
cut_zone = (wm > 0) & (WZ > cz0 - 20)
h = np.where(cut_zone, h * (1 - wm) + prof * wm, h)
# v6: fill under overhangs. data/cave_underside.npz (make_cave_underside.py) = lowest rock-mesh height above each column (local, 0 = world 66).
# Wherever the rock base is higher than the hill (back, flanks, feet), raise the terrain to just inside the rock (-1.5; the render adds ~2).
# Not applied inside the mouth corridor box (the tunnel floor / stairs are handled by the cut above).
CAVE_FILL_MASK = np.zeros((GH, GW), bool)
_u = np.load(f'{ROOT}/data/cave_underside.npz'); _U, _ux0, _uz0 = _u['under'], int(_u['x0']), int(_u['z0'])
_best = np.full((GH, GW), np.inf); _cnt = np.zeros((GH, GW), int)
for _dx in (-1.0, 1.0):
    for _dz in (-1.0, 1.0):
        _lx = np.round(WX - cx0 + _dx).astype(int) - _ux0; _lz = np.round(WZ - cz0 + _dz).astype(int) - _uz0
        _ok = (_lx >= 0) & (_lx < _U.shape[1]) & (_lz >= 0) & (_lz < _U.shape[0])
        _v = np.full((GH, GW), np.nan); _v[_ok] = _U[_lz[_ok], _lx[_ok]]
        _fin = np.isfinite(_v); _best = np.where(_fin, np.minimum(_best, np.where(_fin, _v, np.inf)), _best); _cnt += _fin
_llx, _llz = WX - cx0, WZ - cz0
_corr = (_llx > -12) & (_llx < 52) & (_llz > -32) & (_llz < 72)
_fill = (_cnt >= 2) & (_best < 46.0) & ~_corr
_target = np.where(_fill, CLIFF_BASE_Y + _best - 1.5, -1e9)
CAVE_FILL_MASK = _fill & (_target > h + 0.5)
h = np.maximum(h, _target)
basin = np.zeros_like(h)
pool_surf = float(CLIFF_BASE_Y + 48.4)
# v9: a level ledge for the Captain's last nap (hero prop 24x24 on the cave side of pad 18). Rendered ground ends up ~100.4 (= heightmap 98.43 + 1.97 bias).
_rc = np.hypot(WX - 556.65, WZ - (-517.61)); _wc = 1 - smooth((_rc - 17.0) / 16.0)
h = h * (1 - _wc) + 98.43 * _wc
# v12: the big hillside face beside pad 18's tee (u +30..+70, v -100..-30) is pushed back 22 studs: the heightfield there is re-sampled 22 studs toward the pad
_cx18, _cz18 = pads_w[18]; _yaw18 = pad_yaw[18]; _th18 = math.radians(_yaw18)
_u18, _v18 = pad_uv(_cx18, _cz18, _yaw18)
_w18 = smooth((_u18 - 24.0) / 8.0) * smooth((-_v18 - 26.0) / 14.0) * (1 - smooth((-_v18 - 100.0) / 20.0))
_xs = (WX - 22.0 * math.cos(_th18) - X0) / CELL - 0.5; _zs = (WZ + 22.0 * math.sin(_th18) - Z0) / CELL - 0.5
_hs = ndi.map_coordinates(h, [_zs, _xs], order=1, mode='nearest')
h = np.where(_w18 > 0, h * (1 - _w18) + np.minimum(h, _hs) * _w18, h)
# v19: the pad 17 grass hump (LeafyGrass shelf 105-150 studs ahead of the tee, x 460..516, z -392..-320) is lowered to the surrounding ground (render y 78 = heightmap 76.03),
# ramping back to the original surface between x 492 and 512 and 8 studs outside the z range. Lowers only. This is the v16 Studio carve (hump16.luau) moved into the heightmap source so a regeneration keeps it.
HUMP19_TARGET = 78.0 - 1.97
_wx = smooth((WX - 452.0) / 8.0) * (1 - smooth((WX - 492.0) / 20.0)); _wz = smooth((WZ + 400.0) / 8.0) * (1 - smooth((WZ + 312.0) / 8.0))
_wh = _wx * _wz
HUMP19_DROP = float(np.max(np.where(_wh > 0, h - (h * (1 - _wh) + np.minimum(h, HUMP19_TARGET) * _wh), 0)))
h = h * (1 - _wh) + np.minimum(h, HUMP19_TARGET) * _wh
h = np.clip(h, HMIN + 1, HMAX - 1)

# ---------------------------------------------------------------- materials
gy, gx_ = np.gradient(h, CELL)
slope = np.hypot(gx_, gy)
# colour classes from the concept map
sandc = (R > 150) & (G > 120) & (B < 150) & (R - B > 35)
greenc = (G > R + 6) & (G > B)
rockc = ~(sandc | greenc | water)
def cls_field(m):
    f = ndi.gaussian_filter(m.astype(float), 1.5)
    return np.pad(f, ((PADN, 0), (0, 0)), mode='edge')
cs, cg, cr = cls_field(sandc), cls_field(greenc), cls_field(rockc)
S_, G_, R_ = sample(cs), sample(cg), sample(cr)
mat = np.full((GH, GW), 1, dtype=np.uint8)
jungle = (G_ > S_) & (G_ > R_)
rocky = (R_ > S_) & (R_ > G_)
land_c = d > 0
mat = np.where(land_c & jungle, 2, mat)
mat = np.where(land_c & rocky & (d > 60), 3, mat)
mat = np.where(land_c & (d <= 45), 1, mat)                     # beach rim is always sand
mat = np.where(land_c & (slope > 0.55) & (d > 60), 3, mat)
mat = np.where(land_c & (h > 55) & (d > 60) & (slope > 0.3), 3, mat)
# trail surfaces
trail_zone = (cdist < 12)               # v11: only the 24-wide lane is trail material (was the whole 60-wide graded corridor = the brown bands)
jung_trail = trail_zone & land_c & (celev > 6)
mat = np.where(jung_trail, 5, mat)                              # dirt trail in the jungle / cliff
mat = np.where(trail_zone & land_c & (celev <= 6), 1, mat)      # sand trail on the beach
mat = np.where((cdist >= 12) & (wt > 0.5) & land_c & (celev > 6) & (d > 45), 2, mat)   # v11: the graded corridor beside the lane is leaf-green
# cave-zone slate around pads 15-18
for n_, zname, x, y in PADS_PX:
    if n_ == 1: continue
    cx, cz = pads_w[n_]; r = np.hypot(WX - cx, WZ - cz)
    # v10: no dirt (Ground) between pads. Pad surrounds are LeafyGrass; sand stays only on the beach rim/dunes and the trail; the jungle/cliff trail keeps Ground.
    if zname == 'cave' and n_ == 18:
        mat = np.where(r < 75, 4, mat)
    elif zname == 'cave':   # pads 15-17: LeafyGrass right around the pad, rock stays natural on the faces
        mat = np.where((rect_sdf(cx, cz, OUTER[0], OUTER[1], pad_yaw[n_]) < 14) & ~trail_zone & (slope < 0.7), 2, mat)
    elif zname == 'jungle':
        mat = np.where((r < 62) & ~trail_zone, 2, mat)
        mat = np.where((r < 175) & ~trail_zone & (d > 45) & (slope < 0.9) & ((mat == 3) | (mat == 1)), 2, mat)   # v10: the jungle floor is leaf-green, rock only on real cliffs
    else:   # beach / wreck cove: green ring right around the pad (no pale sand within 6 studs of the felt edge, and the ring props sit on it)
        mat = np.where((rect_sdf(cx, cz, OUTER[0], OUTER[1], pad_yaw[n_]) < 14) & ~trail_zone, 2, mat)
for n_, p, q, e in rest_w:
    r = np.hypot(WX - p[0], WZ - p[1]); mat = np.where(r < 30, 4 if e > 30 else 2, mat)
# v10: any Ground left outside the trail becomes LeafyGrass
mat = np.where((mat == 5) & ~trail_zone, 2, mat)
mat = np.where(dropwall & (d > 4), 3, mat)
mat = np.where(bank_mask & (slope > 0.5) & (d > 60), 3, mat)
mat = np.where(basin > 0.3, 7, mat)
# v11: gentle ground that the map classes as rock (the brown ring around the island) becomes leaf-green; rock stays on cliffs, drop walls and the cave plateau
_cave_r = np.hypot(WX - 563, WZ + 606)
mat = np.where((mat == 3) & (slope < 0.5) & (d > 45) & (_cave_r > 240) & ~dropwall, 2, mat)
# v11: tee side of every pad (u +-42, 80 studs back from the pad edge) is grass, outside the lane
for n_, zname, x, y in PADS_PX:
    if n_ == 1: continue
    cx, cz = pads_w[n_]; _u, _v = pad_uv(cx, cz, pad_yaw[n_])
    tee = (np.abs(_u) < 42) & (_v < -OUTER[1] / 2 + 6) & (_v > -OUTER[1] / 2 - 80) & ~trail_zone & (d > 4) & (slope < 0.8)
    mat = np.where(tee, 6, mat)
mat = np.where(d <= 0, 1, mat).astype(np.uint8)
# v11: mode filter (removes speckle and hard dark seams between materials)
_ids = [1, 2, 3, 4, 5, 6, 7]
_sc = np.stack([ndi.gaussian_filter((mat == k).astype(np.float32), 1.3) + (0.06 if k in (2, 6) else 0.0) for k in _ids])
_mf = np.array(_ids, dtype=np.uint8)[np.argmax(_sc, 0)]
mat = np.where((d > 3) & (basin <= 0.3), _mf, mat).astype(np.uint8)
# a little grass (lit) variety in the jungle away from the trail
lit = (ndi.gaussian_filter(rng.standard_normal((GH, GW)), 5) > 0.35) & (mat == 2) & (cdist > 40)
mat = np.where(lit, 6, mat).astype(np.uint8)
# v19: the slope under the pad 17 boulder_pile (x 488..536, z -388..-320) is Rock instead of LeafyGrass, as in the v16 Studio retexture (a green swell under boulders reads as a hump)
_rk = (WX >= 488) & (WX <= 536) & (WZ >= -388) & (WZ <= -320) & ((mat == 2) | (mat == 6)) & (d > 4)
mat = np.where(_rk, 3, mat).astype(np.uint8)

# v20 (Game Art Bot path spec): ONE continuous Sand trail in pad order 1 -> 18: wreck stern/dock, up the beach (pads 2-5), into the jungle hub, through the jungle pads,
# past the ruin arches and the cave mouth, and back down to the beach (rest stop 3 / pad 9). Gently curving (no straight run over ~40 studs), 6-10 studs wide, ~2 stud
# dithered blend into the surrounding grass/ground. Each tee sits OFF to one side of the trail (the trail passes at |u| 32 beside the tee, joined by a 12 stud apron).
# Clearings: 30 stud hub, 15 stud at the ruin arches and the cave mouth, 12 stud apron at each tee. Material only: heights are not touched.
# The route is also written to data/route_v20.json for make_dressing (plant-free margin, stones, hub props) and the placer.
from scipy.spatial import cKDTree
_rp = np.random.default_rng(20261120)
def _tw(n_, u_, v_):
    cx, cz = pads_w[n_]; th = math.radians(pad_yaw[n_])
    return np.array([cx + u_ * math.cos(th) + v_ * math.sin(th), cz - u_ * math.sin(th) + v_ * math.cos(th)])
TRAIL_U = 32.0          # trail centre beside the tee (clear edge is |u| 27)
APRON_U, APRON_R = 24.0, 6.0
SIDE_END_V = 52.0       # the trail stays beside the pad until past its far end (clear edge v = +42)
def _pad_pts(n_, s_):
    return (_tw(n_, s_ * TRAIL_U, -27.0), _tw(n_, s_ * TRAIL_U, 8.0), _tw(n_, s_ * TRAIL_U, SIDE_END_V))
# DP over the side of each pad (2..18): cost = path length of the connection from the previous pad's far end to this pad's tee
_sides = (-1, 1); _best = {}
_prev_cost = {s_: 0.0 for s_ in _sides}; _prev_choice = {}
_start = _tw(1, 0.0, 62.0)                                      # wreck stern end / dock foot (pad 1 plays toward the beach)
_last = {s_: _start for s_ in _sides}
_choice = {}
_cost = {s_: float(np.linalg.norm(_pad_pts(2, s_)[0] - _start)) for s_ in _sides}; _hist = {2: {s_: None for s_ in _sides}}
for n_ in range(3, 19):
    _new = {}; _hist[n_] = {}
    for s_ in _sides:
        cand = [(_cost[sp] + float(np.linalg.norm(_pad_pts(n_ - 1, sp)[2] - _pad_pts(n_, s_)[0])), sp) for sp in _sides]
        _new[s_], _hist[n_][s_] = min(cand)
    _cost = _new
_sd = {}; _s_cur = min(_cost, key=_cost.get)
for n_ in range(18, 1, -1):
    _sd[n_] = _s_cur; _s_cur = _hist[n_][_s_cur]
RTE = {1: _start}
_wps = [(_start, 'start')]
for n_ in range(2, 19):
    t0, t1, t2 = _pad_pts(n_, _sd[n_]); _wps += [(t0, f'tee{n_}'), (t1, f'mid{n_}'), (t2, f'end{n_}')]
CAVE_M = np.array([583.5, -522.0]); RS3 = np.array([705.6, -51.6])
_wps += [(CAVE_M, 'cave'), (np.array([660.0, -330.0]), 'descent'), (RS3, 'beach')]
# smooth: uniform Catmull-Rom through the waypoints, sampled every 2 studs
_P = np.array([w[0] for w in _wps]); _P = np.vstack([_P[0] * 2 - _P[1], _P, _P[-1] * 2 - _P[-2]])
_pts = []
for i_ in range(1, len(_P) - 2):
    p0, p1, p2, p3 = _P[i_ - 1], _P[i_], _P[i_ + 1], _P[i_ + 2]
    L_ = float(np.linalg.norm(p2 - p1)); m_ = max(int(L_ / 2.0), 2)
    for t in np.linspace(0, 1, m_, endpoint=False):
        _pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
_pts.append(_P[-2]); RT = np.array(_pts)
_seg_ = np.r_[0, np.cumsum(np.hypot(*np.diff(RT, axis=0).T))]
# gentle meander (wavelength about 64 studs, amplitude 5), faded to 0 within 18 studs of each pad waypoint so tees and aprons stay put
_tn = np.gradient(RT, axis=0); _tn /= (np.hypot(*_tn.T)[:, None] + 1e-9); _nr = np.c_[-_tn[:, 1], _tn[:, 0]]
_fade = np.ones(len(RT))
for w_, nm_ in _wps:
    if nm_.startswith(('tee', 'start', 'beach')): _fade = np.minimum(_fade, np.clip((np.hypot(*(RT - w_).T) - 6.0) / 18.0, 0, 1))
_mea = 5.0 * np.sin(_seg_ / 10.5 + 0.9) * _fade
RT = RT + _nr * _mea[:, None]
_seg_ = np.r_[0, np.cumsum(np.hypot(*np.diff(RT, axis=0).T))]
# longest straight run: window over which no point is more than 0.8 stud off the chord
_run = 0.0; _j0 = 0
for i_ in range(0, len(RT), 3):
    j_ = i_
    while j_ + 1 < len(RT) and (_seg_[j_ + 1] - _seg_[i_]) < 120:
        j_ += 1
        c0, c1 = RT[i_], RT[j_]; ch = c1 - c0; cn = np.hypot(*ch)
        if cn < 1: continue
        off_ = np.abs((RT[i_:j_ + 1, 0] - c0[0]) * ch[1] - (RT[i_:j_ + 1, 1] - c0[1]) * ch[0]) / cn
        if off_.max() > 0.8: break
    _run = max(_run, float(_seg_[j_] - _seg_[i_]))
# ruin arches (pads 10, 13, 16): 15 stud clearings; spur path if the arch is more than 14 studs from the trail
ARCHES = [(10, 359.21, 127.19), (13, -361.18, -214.06), (16, 101.8, -478.78)]
_tr0 = cKDTree(RT); SPURS = []
for n_, ax_, az_ in ARCHES:
    dd0, ii0 = _tr0.query([ax_, az_])
    if dd0 > 14:
        a0 = RT[ii0]; a1 = np.array([ax_, az_]); k = int(np.hypot(*(a1 - a0)) / 2) + 2
        sp = np.array([a0 + (a1 - a0) * t for t in np.linspace(0, 1, k)]); SPURS.append(sp)
# v21 (Game Art Bot / Playtest Bot): pads 2-9 could not see the trail from the tee at eye height; a spur leaves the trail near the cup end and crosses ahead of the tee
# (to |u| 6 at v 74) so a sand band sits in the tee view past the cup end
N_ARCH_SPURS = len(SPURS)
for n_ in range(2, 10):
    s_ = _sd[n_]
    ahead = np.array([_tw(n_, s_ * 32.0, 44.0), _tw(n_, s_ * 20.0, 58.0), _tw(n_, s_ * 8.0, 70.0), _tw(n_, s_ * 0.0, 74.0)])
    k_ = int(sum(np.hypot(*(ahead[i + 1] - ahead[i])) for i in range(3)) / 2) + 2
    # Catmull-Rom-free: piecewise linear is fine at 2 stud sampling
    sp = np.vstack([np.array([ahead[i] + (ahead[i + 1] - ahead[i]) * t for t in np.linspace(0, 1, max(int(np.hypot(*(ahead[i + 1] - ahead[i])) / 2), 2), endpoint=False)]) for i in range(3)] + [ahead[3:4]])
    SPURS.append(sp)
# hub: on leg pad 10 -> pad 11, 50 studs of trail BEFORE pad 11's tee (pad 11's back view looks at it)
_k11 = int(np.argmin(np.hypot(*(RT - [w for w, nm in _wps if nm == 'tee11'][0]).T)))
_kh = int(np.argmin(np.abs(_seg_ - (_seg_[_k11] - 52.0)))); HUB = (float(RT[_kh, 0]), float(RT[_kh, 1])); HUB_R = 15.0
CLEARINGS = [dict(kind='hub', x=HUB[0], z=HUB[1], r=HUB_R)]
for n_, ax_, az_ in ARCHES: CLEARINGS.append(dict(kind=f'arch{n_}', x=ax_, z=az_, r=7.5))
CLEARINGS.append(dict(kind='cave', x=float(CAVE_M[0]), z=float(CAVE_M[1]), r=7.5))
for n_ in range(2, 19):
    ap = _tw(n_, _sd[n_] * APRON_U, -27.0); CLEARINGS.append(dict(kind=f'apron{n_}', x=float(ap[0]), z=float(ap[1]), r=APRON_R))
# path field: distance to the (meandered) trail centreline + spurs; half width 3..5 (6-10 wide) varying along the trail
_allp = np.vstack([RT] + SPURS); _allseg = np.r_[_seg_, np.concatenate([np.full(len(sp), 0.0) for sp in SPURS])] if SPURS else _seg_
_tree = cKDTree(_allp)
_dd, _ii = _tree.query(np.c_[WX.ravel(), WZ.ravel()]); _dd = _dd.reshape(WX.shape); _ii = _ii.reshape(WX.shape)
_s_ = _allseg[_ii]
_hw = 4.4 + 0.5 * np.sin(_s_ / 47.0 + 0.7) + 0.1 * np.sin(_s_ / 19.0)
# v21: pads 11-14 legs 10 studs wide (half width 5.0), the 17 -> 18 leg at least 9 (4.6); smooth ramps of 12 studs
def _wp_s(nm_):
    w_ = [w for w, nn in _wps if nn == nm_][0]; return float(_seg_[int(np.argmin(np.hypot(*(RT - w_).T)))])
def _ramp(s_arr, a_, b_, r_=12.0): return np.clip(np.minimum((s_arr - (a_ - r_)) / r_, ((b_ + r_) - s_arr) / r_), 0.0, 1.0)
_sRT = _seg_
_hwb = 4.4 + 0.5 * np.sin(_sRT / 47.0 + 0.7) + 0.1 * np.sin(_sRT / 19.0)
_hwb = np.maximum(_hwb, _hwb + (5.0 - _hwb) * _ramp(_sRT, _wp_s('tee11') - 30.0, _wp_s('end14') + 30.0))
_hwb = np.maximum(_hwb, _hwb + (5.4 - _hwb) * _ramp(_sRT, _wp_s('end14') - 40.0, _wp_s('end14') + 60.0))      # v22: ~30 % sand from above at the pad 14 trail start
_hwb = np.maximum(_hwb, _hwb + (4.6 - _hwb) * _ramp(_sRT, _wp_s('mid17'), _wp_s('tee18') + 10.0))
_hwb = np.maximum(_hwb, 4.3)      # v22: trail at least 8 studs wide along its full length
_HW_RT = _hwb
_jz = _ramp(_sRT, _wp_s('tee11') - 30.0, _wp_s('end14') + 30.0) > 0.5       # jungle trail under the canopy (pads 11-14): lighter Sandstone
_spur_hw = np.concatenate([np.full(len(sp), 4.0 if k >= N_ARCH_SPURS else 2.6) for k, sp in enumerate(SPURS)]) if SPURS else np.zeros(0)
_hw = np.where(_ii >= len(RT), _spur_hw[np.clip(_ii - len(RT), 0, max(len(_spur_hw) - 1, 0))] if len(_spur_hw) else 2.6, _hwb[np.clip(_ii, 0, len(RT) - 1)])
_noise = ndi.gaussian_filter(_rp.standard_normal((GH, GW)), 1.0); _noise = (_noise - _noise.min()) / (_noise.max() - _noise.min())
_edge = 2.0
_pcov = np.clip(1.0 - (_dd - _hw) / _edge, 0.0, 1.0)
_ppath = (_pcov >= 1.0) | ((_pcov > 0) & (_noise < _pcov))
_pad_block = np.zeros(WX.shape, bool)
for n_, zname, x, y in PADS_PX:
    cx, cz = pads_w[n_]; _pad_block |= rect_sdf(cx, cz, OUTER[0], OUTER[1], pad_yaw[n_]) < 2.0
_pclr = np.zeros(WX.shape, bool)
for c_ in CLEARINGS:
    _r = np.hypot(WX - c_['x'], WZ - c_['z']); _cv = np.clip(1.0 - (_r - c_['r'] + 2.0) / 2.0, 0.0, 1.0)
    _pclr |= (_cv >= 1.0) | ((_cv > 0) & (_noise < _cv))
_lane_ok = land_c & (d > 3) & (basin <= 0.3) & (mat != 7)
_want = (_ppath | _pclr) & ~_pad_block
# rock / steep crossings stay as they are (no sand painted on rock): stepping stones are placed there by make_dressing
_rock_cross = _want & _lane_ok & ((mat == 3) | (slope >= 1.2))
PATH_MASK = _want & _lane_ok & (mat != 3) & (slope < 1.2)
# v22 Studio final: 29 neck cells (grid x,z) where the painted trail was under 8 studs with planting on both sides; painted Sandstone in place in v22
_V22_WIDEN = '367,235;368,235;369,235;389,203;390,203;391,202;392,205;396,201;396,202;406,194;407,194;409,196;410,196;494,289;494,290;495,290;577,341;578,341;578,342;580,338;581,339;630,340;631,339;633,342;634,342;636,219;637,219;639,221;640,221'
for _c in _V22_WIDEN.split(';'):
    _gx, _gz = map(int, _c.split(','))
    if mat[_gz, _gx] != 3: PATH_MASK[_gz, _gx] = True
_beach_before = int(((mat == 1) & PATH_MASK).sum())
# the old jungle dirt lane / beach lane through the pad centres is not the trail any more: Ground becomes LeafyGrass
mat = np.where((mat == 5) & ~PATH_MASK, 2, mat)
mat = np.where(PATH_MASK, 1, mat)
_jzc = PATH_MASK & ~_pclr     # v22: the whole trail (and the spurs) is Sandstone (236,200,150); clearings keep Sand           # v21: the pads 11-14 trail under the canopy is lighter Sandstone (Terrain colour (236,200,150))
mat = np.where(_jzc, 8, mat).astype(np.uint8)
# v22 (Game Art Bot): the dark backlit slope in the pad 14 view (Rock / Grass about 80 studs ahead of the tee, around (-586,-290)) is recoloured to the light rock colour (140,125,112) = Terrain Limestone
_lsr = (np.hypot(WX - (-586.0), WZ - (-290.0)) < 55.0) & (WZ > -330.0)
mat = np.where(_lsr & ((mat == 3) | (mat == 6)) & ~PATH_MASK, 9, mat).astype(np.uint8)
print('Limestone slope cells', int(((mat == 9)).sum()))
np.save('/tmp/ps_pathmask.npy', PATH_MASK); Image.fromarray((PATH_MASK * 255).astype(np.uint8)).save(f'{ROOT}/data/pathmask_v20.png')
Image.fromarray((_rock_cross * 255).astype(np.uint8)).save(f'{ROOT}/data/pathrock_v20.png')
# stepping-stone sites: centreline points where the trail crosses rock / steep ground (2-3 flat stones per crossing, spaced 3.5 studs)
_ST = []; _runs = []; _cur = []
for i_, p_ in enumerate(RT):
    gi = int((p_[1] - Z0) / 4); gj = int((p_[0] - X0) / 4)
    inr = 0 <= gi < GH and 0 <= gj < GW and bool(_rock_cross[gi, gj])
    if inr: _cur.append(i_)
    elif _cur:
        if len(_cur) >= 2: _runs.append(_cur)
        _cur = []
if _cur and len(_cur) >= 2: _runs.append(_cur)
for r_ in _runs:                                              # 2-3 flat stones per crossing (3 when longer than ~16 studs)
    k_ = 3 if len(r_) > 8 else 2
    for t_ in np.linspace(0.2, 0.8, k_):
        p_ = RT[r_[int(t_ * (len(r_) - 1))]]; _ST.append([round(float(p_[0]), 2), round(float(p_[1]), 2)])
ROUTE = dict(hwPts=[round(float(v), 3) for v in _HW_RT[::2]], spurHw=[4.0 if k >= N_ARCH_SPURS else 2.6 for k in range(len(SPURS))], pointsXZ=[[round(float(x), 2), round(float(z), 2)] for x, z in RT[::2]], spurs=[[[round(float(x), 2), round(float(z), 2)] for x, z in sp] for sp in SPURS],
             sides={str(k): int(v) for k, v in _sd.items()}, clearings=[{k: (round(v, 2) if isinstance(v, float) else v) for k, v in c_.items()} for c_ in CLEARINGS],
             stones=_ST, halfWidthRange=[3.8, 5.0], plantMargin=1.5, trailU=TRAIL_U, lengthStuds=round(float(_seg_[-1]), 1), longestStraightStuds=round(_run, 1))
json.dump(ROUTE, open(f'{ROOT}/data/route_v20.json', 'w'))
PATH_INFO = dict(hub=[round(HUB[0], 1), round(HUB[1], 1)], hubRadius=HUB_R, halfWidthRange=[3.8, 5.0], edgeBand=_edge, cells=int(PATH_MASK.sum()), lengthStuds=ROUTE['lengthStuds'],
                 longestStraightStuds=ROUTE['longestStraightStuds'], stepSites=len(_ST), sides=ROUTE['sides'])
print('v20 route:', PATH_INFO)

# ---------------------------------------------------------------- write maps
os.makedirs(f'{ROOT}/data', exist_ok=True)
hv = np.round((h - HMIN) / (HMAX - HMIN) * 65535).astype(np.uint16)
Image.fromarray(hv).save(f'{ROOT}/data/heightmap.png')              # mode I;16
pm = Image.fromarray(mat, mode='P'); pal = []
for i in range(256): pal += list(MAT_RGB.get(i, (0, 0, 0)))
pm.putpalette(pal); pm.save(f'{ROOT}/data/materialmap.png')
np.save('/tmp/ps_h.npy', h); np.save('/tmp/ps_mat.npy', mat)

# ---------------------------------------------------------------- placements
def hat(X, Z):
    return float(h[int(np.clip((Z - Z0) // CELL, 0, GH-1)), int(np.clip((X - X0) // CELL, 0, GW-1))])
pads_out = []
for n_, zname, x, y in PADS_PX:
    X, Z = pads_w[n_]; e = PAD_TOP[n_]; yaw = pad_yaw[n_]
    pads_out.append(dict(
        n=n_, id=f'Pad{n_:02d}', zone={'wreck':'wreck_cove','beach':'beach','jungle':'jungle','cave':'cave_cliff'}[zname],
        pos=[round(X, 2), e, round(Z, 2)], yawDeg=round(yaw, 1), mapPx=[x, y],
        feltSize=[FELT[0], FELT[1]], rimWidth=RIM, outerSize=list(OUTER), artClearSize=list(CLEAR),
        rim='dark_wood' if n_ <= 9 else 'slate', surfaceUnder='wreck_deck_hull' if n_ == 1 else MATERIALS[int(mat[int((Z-Z0)//CELL), int((X-X0)//CELL)])],
        terrainTopUnderPad=None if n_ == 1 else round(hat(X, Z), 2),
        note='elevation = felt top Y. +Z local runs along the trail (direction of play). pos is the felt centre on the felt top.'
             + (' Flat stern deck of the wreck: sits on the hull stand-in, not on terrain; plays toward the stern/beach.' if n_ == 1 else '')))
rest_out = [dict(n=n_, id=f'RestStop{n_}', pos=[round(p[0], 2), round(e, 2), round(p[1], 2)], size=[REST_SIZE, REST_SIZE],
                 mapPx=[x, y], yawDeg=0.0, joinsTrailAt=[round(q[0], 2), round(q[1], 2)],
                 gag=('croc nap (gag 11, hero) near pad 14' if n_ == 1 else 'dressing gags TBD (Game Art Bot)'),
                 note='flat clearing, no hole, no felt; gag props sit here')
            for (n_, x, y), (_, p, q, e) in zip(REST_PX, rest_w)]
def yawrot(vec, yaw):  # local (x,z) -> world
    th = math.radians(yaw); return (vec[0]*math.cos(th) + vec[1]*math.sin(th), -vec[0]*math.sin(th) + vec[1]*math.cos(th))
wreck = dict(
    id='wreck', mesh='wreck_v2 (3D Model Bot, models/wreck_v2/: wreck_hull, wreck_rig, wreck_glow, wreck_duck, all at this origin, identity rotation)',
    centre=[round(wreck_origin[0], 2), 0.0, round(wreck_origin[1], 2)], yawDeg=round(ship_yaw_bow, 1),
    yawNote='centre = the mesh origin: Y 0 = water line, X 0 = centreline, Z 0 = midship. Local +Z points to the bow (duck, lagoon); stern (local Z -160) faces the beach and pad 1. Hull lists 15 deg (roll, high side +X).',
    footprint=dict(length=WRECK_LEN, width=WRECK_WID, hullHeight=HULL_H, mastTipAboveWaterline=MAST_H, mastTipWreckV2=MAST_H_V2, units='studs',
                   source='room decision (Game Art Bot / RobloxDevBot): about 320 long, 90 wide, 60 tall, mast tip about Y 161; wreck_v2 final mast tip is Y 138.8'),
    waterline=WATER_Y, deckTopY=PAD_ELEV[1], sternLocalZ=-WRECK_STERN_Z, geometricCentre=[round(wreck_c[0], 2), round(wreck_c[1], 2)],
    sternEnd=[round(stern_end[0], 2), round(stern_end[1], 2)], bowEnd=[round(bow_end[0], 2), round(bow_end[1], 2)],
    pad1CentreFromStern=PAD1_FROM_STERN, pad1Local=[0.0, PAD_ELEV[1], PAD1_LOCAL_Z], pad1DeckSize=[54, 84],
    shoreDistanceAlongHull=wreck_sd, shoreNote='signed distance to shore in studs (positive = inland), sampled at -45 / 0 / +45 studs across the hull, at hull stations measured from the stern end. Only the stern end is on sand.',
    tiltDeg='15 roll (list) in the mesh; pad 1 is a level plank deck on posts (top exactly Y 24)',
    keepClear='nothing taller than 3 studs within 25 studs of pad 1 centre; flat empty deck at the stern side (handoff)',
    meshes=['wreck_hull 13.8k tris', 'wreck_rig 3.2k', 'wreck_glow 0.6k', 'wreck_duck 1.7k'],
    standIn=dict(hull='box 90x60x320 (top = Y 24 deck, hull bottom sunk in the sea floor); removed when the real mesh is imported', mainMast='cylinder, base on the deck, tip at Y 161',
                 mainSail='50x38x1 cream + 18x14 red patch', foreMast='snapped', cabin='40x22x23 forward of the pad deck', duck='22 stud yellow cube at the bow'))
cliff = dict(
    id='cave_cliff', mesh='3D Model Bot hero 2', centre=[round(cliff_center[0], 2), CLIFF_BASE_Y, round(cliff_center[1], 2)], yawDeg=0.0,
    yawNote='front face (cave mouth, stairs) faces +Z (south), toward pad 18 and the trail.',
    footprint=dict(width=CLIFF_W, depth=CLIFF_D, height=CLIFF_H, units='studs',
                   source='3d-2-cave-cliff-sheet.png (about 240 wide, 150 tall, 140 deep; mouth about 40 wide and 36 tall)'),
    baseY=CLIFF_BASE_Y, topY=CLIFF_BASE_Y + CLIFF_H, frontFaceZ=round(cliff_front_z, 2),
    mouth=dict(width=MOUTH_W, height=MOUTH_H, centreX=round(mouth_x, 2), floorY=CAVE_MOUTH_FLOOR_Y),
    waterfall=dict(x=round(falls_x, 2), poolCentre=[round(pool_c[0], 2), round(pool_surf, 2), round(pool_c[1], 2)], poolRadius=22,
                   note='moved onto the cliff flank (the concept map has it ~300 studs west of the mouth; the 3D sheet puts it on the cliff)'),
    keepClear='pads 17 and 18 flank the front face; 8 studs of empty space around each pad, no mesh part on a pad',
    meshes=['cliff lower half <= 16k tris', 'cliff upper half + cave arch <= 16k tris', 'stairs + railings <= 4k tris'])
PROP_DEFS = [  # id, name, pad/rest anchor, footprint [x,z] (estimated unless stated), height, source
    ('gag01_duck_figurehead', 'Duck figurehead', 'wreck bow', [22, 22], 22, 'sheet: about 22 studs tall, 3k tris; part of the wreck mesh or its own piece'),
    ('gag02_backward_cannon', 'Backward cannon', 'wreck deck beside pad 1-2', [14, 7], 7, 'sheet: about 14 long, 2.5k tris + 6 cannonballs (200 tris each); width/height estimated'),
    ('gag07_coconut_casualty', 'Coconut casualty', 'jungle entry, beside pad 10', [16, 16], 55, 'sheet: palm 55 tall (3k tris) + flat skeleton 14 long (1.5k tris); footprint estimated'),
    ('gag10_flytrap_burp', 'Flytrap burp', 'jungle, pads 13-14 (beside pad 13)', [20, 20], 30, 'sheet: about 30 tall, 4k tris; footprint estimated'),
    ('gag11_croc_nap', 'Croc nap', 'rest stop near pad 14 (RestStop1)', [40, 16], 12, 'sheet: about 40 long, 4k tris; width/height estimated'),
    ('gag13_captains_last_nap', "Captain's last nap", 'cave, beside pad 18', [24, 24], 30, 'sheet: throne + gold pile about 30 tall, 6k tris; footprint estimated')]
props = []
def side_pos(n_, half, side=-1):
    X, Z = pads_w[n_]; yaw = pad_yaw[n_]; off = CLEAR[0] / 2 + half + 2
    vx, vz = yawrot((side * off, 0), yaw); return [round(X + vx, 2), round(Z + vz, 2)]
for pid, name, where, fp, ht, src in PROP_DEFS:
    if pid.startswith('gag01'):
        continue        # the duck figurehead is part of the wreck_v2 mesh (wreck_duck.fbx)
    elif pid.startswith('gag02'):
        along = 200.0   # studs from the stern end toward the bow (local z +40), on the listed main deck, forward of the pad deck and the cabin
        q = stern_end - ax * along; pos = [round(q[0], 2), 17.0, round(q[1], 2)]; yaw = pad_yaw[1] + 180
    elif pid.startswith('gag07'):
        xz = side_pos(10, 12, -1); pos = [xz[0], round(hat(*xz) + 1, 2), xz[1]]; yaw = pad_yaw[10]
    elif pid.startswith('gag10'):
        xz = side_pos(13, 14, 1); pos = [xz[0], round(hat(*xz) + 1, 2), xz[1]]; yaw = pad_yaw[13]
    elif pid.startswith('gag11'):
        r = rest_out[0]; pos = [r['pos'][0], r['pos'][1], r['pos'][2]]; yaw = 0.0
    else:
        xz = side_pos(18, 14, 1); pos = [xz[0], round(hat(*xz) + 1, 2), xz[1]]; yaw = pad_yaw[18]
    props.append(dict(id=pid, name=name, where=where, anchor=pos, yawDeg=round(yaw, 1),
                      footprint=dict(x=fp[0], z=fp[1], height=ht, units='studs'), source=src, hero=True))
# v7: the five gag props as placed in Studio (props_v1 / props_v1_1 meshes, origin = base centre, front = +Z).
# anchor = base centre (Y = ground or deck under the base, measured in Studio). Coconut moved 11 studs, flytrap and
# captain 2 studs away from their pads (out of the art-clear rectangle); cannon +Z points at the wreck centre.
V7_PLACED = {
    'gag02_backward_cannon':   dict(anchor=[-656.24, 40.15, 206.53], yaw=74.8, mesh='props_v1_1/prop_cannon.fbx', size=[23.45, 9.7, 26.3],
                                    note='on the wreck deck (stern castle top, hull top Y about 40 here); +Z (muzzle) aims at the wreck centre (-617.64, 217.01)'),
    'gag07_coconut_casualty':  dict(anchor=[389.62, 6.72, 108.73], yaw=95.4, mesh='props_v1_1/prop_coconut.fbx', size=[22.47, 55.41, 26.69],
                                    note='moved 11.0 studs from (390.66, 119.68) along (-0.094, -0.996), away from Pad10; clears the art-clear rectangle by 7.6 studs; v8: yawed 180 deg about its own centre (yaw -84.6 -> 95.4) so the skeleton and coconut face the trail, anchor unchanged (gap +7.56)'),
    'gag10_flytrap_burp':      dict(anchor=[-390.20, 24.72, -136.64], yaw=-120.3, mesh='props_v1/prop_flytrap.fbx', size=[20.43, 30.6, 26.63],
                                    note='moved 2.0 studs from (-389.19, -138.37) away from Pad13; clears the art-clear rectangle by 1.2 studs'),
    'gag11_croc_nap':          dict(anchor=[-631.5, 27.58, -556.5], yaw=0.0, mesh='props_v1/prop_croc.fbx', size=[27.0, 10.91, 40.0],
                                    note='RestStop1; Y is the terrain surface under it'),
    'gag13_captains_last_nap': dict(anchor=[556.65, 100.94, -517.61], yaw=126.6, mesh='props_v1/prop_captain.fbx', size=[24.7, 31.68, 23.27],
                                    note='moved 2.0 studs from (557.84, -516.0) away from Pad18; clears the art-clear rectangle by 1.0 studs; on a steep slope, Y is the mean of 5 terrain samples (90.5 to 113.9)'),
}
for _pr in props:
    _v = V7_PLACED.get(_pr['id'])
    if _v:
        _pr['anchorPlannedV6'] = _pr['anchor']; _pr['yawDegPlannedV6'] = _pr['yawDeg']
        _pr['anchor'] = _v['anchor']; _pr['yawDeg'] = _v['yaw']
        _pr['placed'] = dict(version=('v8' if _pr['id']=='gag07_coconut_casualty' else 'v7'), mesh=_v['mesh'], sizeStuds=_v['size'], anchored=True, canCollide=False, canTouch=False, canQuery=False, note=_v['note'])

placements = dict(
    format=1, course='Pirate Shipwreck', look='B Golden Hour Hideaway', status='blockout1, world only, no holes',
    coords='studs; X east, Y up, Z south; origin = centre of map-overhead.png frame (819x461 px at 3 studs per px)',
    waterLevelY=WATER_Y, pads=pads_out, restStops=rest_out, heroMeshes=[wreck, cliff], heroProps=props,
    padRules=dict(feltColor=[87, 147, 79], feltHex='#579353', felt='Plastic, Reflectance 0, no texture',
                  rimWidthStuds=RIM, rimWood=[84, 52, 34], rimSlate=[70, 76, 92],
                  extraSoftLights=dict(pads=[16], range=30, brightness=0.3, enabled=False,   # v20: pads 15 and 17 soft lights removed (made pad 17 render (151,218,128) vs (105,186,103) on pads 5/18); pad 16 keeps a weak one
                          color=[255, 225, 190], shadows=False, height=14,
                                       note='Look B room decision: pads 15-17 must not sit in dark shadow. Two extra soft warm PointLights each, further up and wider than the standard pad light. Slate discs around pads 15-17 removed from the material map.'),
                  feltNeverTouchesSand=True, lightThingsMinDistanceFromFelt=6, emptySpaceAroundPad=ART_CLEAR,
                  padLight=dict(range=16, brightness=1.0, color=[255, 245, 225], shadows=False, countPerPad=2,
                                note='handoff says one light; 2 per 60-stud pad so the far end is lit (range 16)'),
                  cup='dark ring + red flag (235,55,55) on a cream pole, >= 14 studs tall, visible from the tee (holes step, not here)'),
    paths20=PATH_INFO,
    trail=dict(widthStuds=28, pointsXZ=[[round(a, 1), round(b, 1)] for a, b in cl[::6]]),
    sunNote='sunset sun is low in the west; the wreck (west) can shade pad 1-2. Check Lighting:GetSunDirection() printed by the import script and tune.')
placements['footprintSummary'] = (
    [dict(id='wreck', sizeStuds=dict(width=WRECK_WID, height=MAST_H + HULL_H - PAD_ELEV[1] + 0, length=WRECK_LEN), note='hull 60 tall at midships, mast tip about Y 161 (wreck_v2 final: 138.8), pad 1 deck top Y 24 (flat, 54 x 84, centre local (0,24,-110))') ] +
    [dict(id='cave_cliff', sizeStuds=dict(width=CLIFF_W, height=CLIFF_H, depth=CLIFF_D), note='base Y 66, mouth 40 wide on the +Z face, mouth floor Y 94; cave v2 (same footprint) coming')] +
    [dict(id=p['id'], sizeStuds=dict(x=p['footprint']['x'], z=p['footprint']['z'], height=p['footprint']['height']), note=p['source']) for p in props])
json.dump(placements, open(f'{ROOT}/data/placements.json', 'w'), indent=1)

lighting = json.load(open(os.path.join(os.path.dirname(__file__), 'lighting_lookB.json')))
json.dump(lighting, open(f'{ROOT}/data/lighting.json', 'w'), indent=1)
world = dict(format=1, studsPerMapPx=S, mapSizePx=[MAP_W, MAP_H], originMapPx=[CX, CZ], gridCellStuds=CELL, gridSize=[GW, GH],
             gridCornerXZ=[X0, Z0], minY=MINY, voxelLayers=LAYERS, topY=MINY + 4 * LAYERS,
             height=dict(file='heightmap.png', bits=16, minStuds=HMIN, maxStuds=HMAX, formula='stud = min + v/65535*(max-min)', rows='z, north to south', cols='x, west to east'),
             material=dict(file='materialmap.png', ids={str(k): v for k, v in MATERIALS.items()}),
             terrainSource='generated only (no hand edits yet)', waterLevelY=WATER_Y,
             materialColors={MATERIALS[k]: list(v) for k, v in MAT_RGB.items()})
json.dump(world, open(f'{ROOT}/data/world.json', 'w'), indent=1)

# ---------------------------------------------------------------- checks
checks = []
def rect_cells(cx, cz, w, l, yaw):
    q = rect_sdf(cx, cz, w, l, yaw); return q <= 0
for p in pads_out:
    n_ = p['n']
    if n_ == 1: continue
    X, Z = p['pos'][0], p['pos'][2]; m = rect_cells(X, Z, OUTER[0], OUTER[1], p['yawDeg'])
    hh = h[m]; ms = mat[m]
    m2 = rect_cells(X, Z, CLEAR[0], CLEAR[1], p['yawDeg'])
    checks.append(dict(pad=n_, terrainMin=round(float(hh.min()), 2), terrainMax=round(float(hh.max()), 2), flatSpread=round(float(hh.max() - hh.min()), 2),
                       minSurfaceAboveWater=bool(hh.min() > 0.5), maxSlopeInClear=round(float(slope[m2].max()), 3),
                       underPadMaterials=sorted({MATERIALS[int(v)] for v in np.unique(ms)}), shoreDistanceStuds=round(float(SD[int((Z-Z0)//CELL), int((X-X0)//CELL)]), 1)))
# overlaps of clear rects and hero footprints
rects = {f'pad{p["n"]}': rect_corners(p['pos'][0], p['pos'][2], CLEAR[0], CLEAR[1], p['yawDeg']) for p in pads_out}
for r_ in rest_out:
    rects[f'rest{r_["n"]}'] = rect_corners(r_['pos'][0], r_['pos'][2], REST_SIZE, REST_SIZE, 0)
rects['wreck'] = rect_corners(*wreck_c, WRECK_WID, WRECK_LEN, ship_yaw_bow)
rects['cliff'] = rect_corners(*cliff_center, CLIFF_W, CLIFF_D, 0)
ov = []
keys = list(rects)
for i, a_ in enumerate(keys):
    for b_ in keys[i+1:]:
        if sat_overlap(rects[a_], rects[b_]): ov.append([a_, b_])
# pad 1 sits on the wreck deck on purpose; mast distance from pad 1
mast_main = stern_end - ax * 210.0; fore = stern_end - ax * 250.0   # stand-in positions; real rig (wreck_v2 manifest): nearest rig point is 50 studs from the pad 1 centre
d_mast = float(np.hypot(*(mast_main - p1)))
report = dict(padChecks=checks, overlaps=ov, overlapNote='pad1 / wreck overlap is intended (pad 1 is the wreck stern deck)',
              mainMastDistanceFromPad1=round(d_mast, 1), keepClear25OK=d_mast >= 25,
              pad1Elevation=PAD_ELEV[1], gangwayRunStuds=round(float(np.hypot(*(np.array(pads_w[2]) - p1))), 1),
              minPadToPadCentreDistance=round(min(float(np.hypot(*(np.array(pads_w[a]) - np.array(pads_w[b])))) for a in range(1, 19) for b in range(a+1, 19)), 1),
              maxTerrainHeight=round(float(h.max()), 1), minTerrainHeight=round(float(h.min()), 1),
              trailLengthStuds=round(float(seg[-1] - pad_s[0]), 0))
json.dump(report, open(f'{ROOT}/data/blockout-report.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in report.items() if k != 'padChecks'}, indent=1))
for c in checks: print(c)

# keep in memory for the preview step
np.savez('/tmp/ps_state.npz', h=h, mat=mat)
json.dump(dict(wreck_c=list(map(float, wreck_c)), stern=list(map(float, stern_end)), bow=list(map(float, bow_end)), ax=list(map(float, ax)),
               cliff_c=list(map(float, cliff_center)), pool=list(map(float, pool_c)), falls_x=float(falls_x), cliff_front_z=float(cliff_front_z),
               mouth_x=float(mouth_x), ship_yaw=ship_yaw_bow, pool_surf=float(pool_surf)), open('/tmp/ps_geo.json', 'w'))
