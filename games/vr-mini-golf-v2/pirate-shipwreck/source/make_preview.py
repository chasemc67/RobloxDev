import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from layout import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
st = np.load('/tmp/ps_state.npz'); h = st['h']; mat = st['mat']
P = json.load(open(f'{ROOT}/data/placements.json')); geo = json.load(open('/tmp/ps_geo.json'))
MAT_RGB = {1:(226,184,128), 2:(30,100,60), 3:(120,105,95), 4:(120,105,95), 5:(150,105,70), 6:(90,170,70), 7:(110,80,55)}
Z = 2   # preview px per grid cell
rgb = np.zeros((GH, GW, 3), float)
for k, c in MAT_RGB.items(): rgb[mat == k] = c
water = h < 0
depth = np.clip(-h / 26, 0, 1)[..., None]
wcol = np.array([30,120,140]) * (1 - 0.55*depth) + np.array([10,50,80]) * 0.55*depth
rgb = np.where(water[..., None], wcol, rgb)
# hillshade, sun from the west-south-west low
gy, gx = np.gradient(h * 2.0, CELL)
az = math.radians(250); alt = math.radians(25)
nx, ny, nz = -gx, -gy, np.ones_like(h)
nl = np.sqrt(nx*nx + ny*ny + nz*nz); nx, ny, nz = nx/nl, ny/nl, nz/nl
lx, ly, lz = math.sin(az)*math.cos(alt)*-1, math.cos(az)*math.cos(alt)*-1, math.sin(alt)
shade = np.clip(nx*lx + ny*ly + nz*lz, 0, 1)
shade = 0.55 + 0.6 * shade
# contour-ish elevation tint
rgb = np.clip(rgb * shade[..., None], 0, 255)
img = Image.fromarray(rgb.astype(np.uint8)).resize((GW*Z, GH*Z), Image.BICUBIC)
d = ImageDraw.Draw(img, 'RGBA')
try:
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20); fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
except Exception: f = fs = ImageFont.load_default()
def tp(X, Zw): return ((X - X0) / CELL * Z, (Zw - Z0) / CELL * Z)
def poly(c, fill=None, outline=None, w=2):
    d.polygon([tp(*p) for p in c], fill=fill, outline=outline, width=w)
# trail
pts = [tp(*p) for p in P['trail']['pointsXZ']]; d.line(pts, fill=(255,255,255,120), width=3)
# hero footprints
wr = P['heroMeshes'][0]; cf = P['heroMeshes'][1]
poly(rect_corners(wr['geometricCentre'][0], wr['geometricCentre'][1], WRECK_WID, WRECK_LEN, wr['yawDeg']), fill=(140,90,55,200), outline=(255,255,255,255))
poly(rect_corners(cf['centre'][0], cf['centre'][2], CLIFF_W, CLIFF_D, 0), fill=(110,92,120,120), outline=(255,255,255,255))
# mouth, waterfall, pool
mx = cf['mouth']['centreX']; fz = cf['frontFaceZ']
d.line([tp(mx - 20, fz), tp(mx + 20, fz)], fill=(255,190,80,255), width=6)
d.ellipse([*(np.array(tp(*(geo['pool'][0:1] + [geo['pool'][1]]))) - 22/CELL*Z), *(np.array(tp(geo['pool'][0], geo['pool'][1])) + 22/CELL*Z)], fill=(60,150,190,230), outline=(255,255,255,200))
d.line([tp(geo['falls_x'], geo['cliff_front_z'] - 100), tp(geo['falls_x'], geo['cliff_front_z'])], fill=(170,220,255,255), width=5)
# rest stops
for r in P['restStops']:
    poly(rect_corners(r['pos'][0], r['pos'][2], REST_SIZE, REST_SIZE, 0), fill=(255,255,255,90), outline=(255,220,90,255))
    x, y = tp(r['pos'][0], r['pos'][2]); d.text((x - 14, y - 10), f"R{r['n']}", fill=(255,240,160,255), font=f, stroke_width=2, stroke_fill=(0,0,0,255))
# props
for pr in P['heroProps']:
    x, y = tp(pr['anchor'][0], pr['anchor'][2]); fp = pr['footprint']
    poly(rect_corners(pr['anchor'][0], pr['anchor'][2], fp['x'], fp['z'], pr['yawDeg']), fill=(255,120,200,150), outline=(255,255,255,200), w=1)
# pads
for p in P['pads']:
    X, Zw = p['pos'][0], p['pos'][2]; yaw = p['yawDeg']
    poly(rect_corners(X, Zw, *p['artClearSize'], yaw), fill=None, outline=(255,255,255,70), w=1)
    wood = p['rim'] == 'dark_wood'
    poly(rect_corners(X, Zw, *p['outerSize'], yaw), fill=(84,52,34,255) if wood else (50,54,66,255))
    poly(rect_corners(X, Zw, *p['feltSize'], yaw), fill=(100,230,135,255))
    x, y = tp(X, Zw); d.text((x - 10, y - 12), str(p['n']), fill=(0,40,10,255), font=f)
# labels
def lab(X, Zw, t): 
    x, y = tp(X, Zw); d.text((x, y), t, fill=(255,255,255,255), font=f, stroke_width=3, stroke_fill=(0,0,0,255))
lab(wr['geometricCentre'][0] - 120, wr['geometricCentre'][1] - 110, 'WRECK 320x90 (wreck_v2), bow W, stern on sand')
lab(cf['centre'][0] - 90, cf['centre'][2] - 20, 'CAVE 240x140 (cave_v1)')
lab(geo['pool'][0] - 90, geo['pool'][1] + 30, 'pool / waterfall')
lab(-1150, 800, 'Pirate Shipwreck - blockout2 layout (look B), world only')
d.text(tp(-1150, 840), 'grid 1 cell = 4 studs, preview 2px/cell. Green = felt 30x60, outline = rim 4, faint box = 8-stud art-clear. Pink = hero props', fill=(255,255,255,255), font=fs, stroke_width=2, stroke_fill=(0,0,0,255))
# scale bar 200 studs
x, y = tp(-1150, 900); d.rectangle([x, y, x + 200/CELL*Z, y + 8], fill=(255,255,255,255)); d.text((x, y + 10), '200 studs', fill=(255,255,255,255), font=fs, stroke_width=2, stroke_fill=(0,0,0,255))
os.makedirs(f'{ROOT}/preview', exist_ok=True)
img.convert('RGB').save(f'{ROOT}/preview/layout-topdown-full.png')
img.crop((400,250,1700,1000)).convert('RGB').save(f'{ROOT}/preview/layout-topdown.png')
print(img.size)
# heightmap preview
hp = np.clip((h - HMIN) / (HMAX - HMIN), 0, 1)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(16, 5.2))
ax[0].imshow(h, cmap='terrain', extent=[X0, X0 + GW*CELL, Z0 + GH*CELL, Z0], vmin=-30, vmax=120); ax[0].set_title('heightmap (studs, water 0)')
ax[0].contour(np.linspace(X0, X0 + GW*CELL, GW), np.linspace(Z0, Z0 + GH*CELL, GH), h, levels=[0], colors='k', linewidths=0.6)
for p in P['pads']: ax[0].text(p['pos'][0], p['pos'][2], str(p['n']), fontsize=7, ha='center', color='w')
ax[1].plot(range(1, 19), [p['pos'][1] for p in P['pads']], 'o-'); ax[1].set_title('felt-top elevation per pad (studs above water)'); ax[1].set_xlabel('pad'); ax[1].grid(True)
plt.tight_layout(); plt.savefig(f'{ROOT}/preview/heightmap-preview.png', dpi=80)
