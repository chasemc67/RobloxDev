"""Sugarloaf world props: mine-head, lift cage, gondola cabin, scatter set. Pure python -> <set>/parts.json (Roblox coords, pivot-relative).
relative to the landmark anchor = base-centre pivot). Built inside each props.md envelope; sheets = direction."""
import json, math, os
D = '/workspace/RobloxDev/assets/vr-minigolf/sugarloaf-canyon/'
H = {h['id']: h for h in json.load(open(D + 'holes.json'))['holes']}
def roty(p, d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a); return [p[0]*c + p[2]*s, p[1], -p[0]*s + p[2]*c]
class Part:
    def __init__(s, name, hole, anchor): s.name = name; s.hole = hole; s.anchor = anchor; s.g = {}; s.notes = []
    def add(s, m, v, f):
        V, F = s.g.setdefault(m, ([], [])); o = len(V); V += [[round(x, 5) for x in p] for p in v]; F += [[i+o for i in fc] for fc in f]
    def box(s, m, c, size, yaw=0):
        hx, hy, hz = [x/2 for x in size]
        vs = [[-hx,-hy,-hz],[hx,-hy,-hz],[hx,-hy,hz],[-hx,-hy,hz],[-hx,hy,-hz],[hx,hy,-hz],[hx,hy,hz],[-hx,hy,hz]]
        s.add(m, [[a+b for a, b in zip(roty(p, yaw), c)] for p in vs], [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
    def bar(s, m, a, b, t):  # square bar from point a to b (thickness t)
        import numpy as np
        a = np.array(a, float); b = np.array(b, float); d = b - a; L = np.linalg.norm(d); d /= L
        up = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0])
        u = np.cross(d, up); u /= np.linalg.norm(u); w = np.cross(d, u); h = t/2
        ring = [u*h + w*h, -u*h + w*h, -u*h - w*h, u*h - w*h]
        vs = [list(a + r) for r in ring] + [list(b + r) for r in ring]
        s.add(m, vs, [(3,2,1,0), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)])
    def prism_xz(s, m, poly, y0, y1):
        n = len(poly); vs = [[x, y0, z] for x, z in poly] + [[x, y1, z] for x, z in poly]
        s.add(m, vs, [list(range(n-1, -1, -1)), list(range(n, 2*n))] + [[i, (i+1) % n, n+(i+1) % n, n+i] for i in range(n)])
    def prism_zy(s, m, poly, x0, x1):  # poly in (z, y), extruded along x
        n = len(poly); vs = [[x0, y, z] for z, y in poly] + [[x1, y, z] for z, y in poly]
        s.add(m, vs, [list(range(n-1, -1, -1)), list(range(n, 2*n))] + [[i, (i+1) % n, n+(i+1) % n, n+i] for i in range(n)])
    def cyl(s, m, c, r, a0, a1, n=16, axis='y'):
        pts = [(r*math.cos(2*math.pi*i/n), r*math.sin(2*math.pi*i/n)) for i in range(n)]
        if axis == 'y': vs = [[c[0]+p, t, c[2]+q] for t in (a0, a1) for p, q in pts]
        elif axis == 'z': vs = [[c[0]+p, c[1]+q, t] for t in (a0, a1) for p, q in pts]
        else: vs = [[t, c[1]+p, c[2]+q] for t in (a0, a1) for p, q in pts]
        s.add(m, vs, [list(range(n-1, -1, -1)), list(range(n, 2*n))] + [[i, (i+1) % n, n+(i+1) % n, n+i] for i in range(n)])
def anchor(hid, name): return next(a for a in H[hid]['decoration_anchors'] if a['name'] == name)
P = []
def loft(s, m, rings, cap0=True, cap1=True):
    """rings: list of equal-length vertex rings (CCW seen from +y). A ring of one point = apex."""
    V = []; idx = []
    for r in rings: idx.append(list(range(len(V), len(V)+len(r)))); V += r
    F = []
    for a, b in zip(idx, idx[1:]):
        n = max(len(a), len(b))
        for i in range(n):
            if len(b) == 1: F.append([a[i], a[(i+1) % n], b[0]])
            elif len(a) == 1: F.append([a[0], b[(i+1) % n], b[i]])
            else: F.append([a[i], a[(i+1) % n], b[(i+1) % n], b[i]])
    if cap0 and len(idx[0]) > 2: F.append(idx[0][::-1])
    if cap1 and len(idx[-1]) > 2: F.append(idx[-1])
    s.add(m, V, F)
Part.loft = loft
def circ(c, r, y, n=24, a0=0.0, a1=2*math.pi, closed=True):
    k = n if closed else n + 1
    return [[c[0] + r*math.cos(a0 + (a1-a0)*i/n), y, c[2] - r*math.sin(a0 + (a1-a0)*i/n)] for i in range(k)]

import numpy as np
def hexa(s, m, v8):  # bottom ring 0-3, top ring 4-7 (same winding)
    s.add(m, v8, [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
Part.hexa = hexa
def prism_xy(s, m, poly, z0, z1):  # poly in (x, y), extruded along z
    n = len(poly); vs = [[x, y, z0] for x, y in poly] + [[x, y, z1] for x, y in poly]
    s.add(m, vs, [list(range(n-1, -1, -1)), list(range(n, 2*n))] + [[i, (i+1) % n, n+(i+1) % n, n+i] for i in range(n)])
Part.prism_xy = prism_xy
def octa(s, m, c, e, hy=1.4):
    cx, cy, cz = c
    s.add(m, [[cx+e, cy, cz], [cx-e, cy, cz], [cx, cy, cz+e], [cx, cy, cz-e], [cx, cy+e*hy, cz], [cx, cy-e, cz]],
          [(0,2,4), (2,1,4), (1,3,4), (3,0,4), (2,0,5), (1,2,5), (3,1,5), (0,3,5)])
Part.octa = octa
def mk(hid, name):
    a = anchor(hid, name); A = a['position']; p = Part(hid + '_' + name, hid, A)
    p.rel = lambda x, y, z: [x - A[0], y - A[1], z - A[2]]
    return p, A

import random
HERE = os.path.dirname(os.path.abspath(__file__))
SETS = {}
def new(setname, pid, env, notes, pivot_desc):
    p = Part(pid, setname, [0, 0, 0]); p.env = env; p.notes.append(notes); p.pivot_desc = pivot_desc; SETS.setdefault(setname, []).append(p); return p
def xform(s, m, verts, faces, R=None, t=(0, 0, 0)):
    R = np.eye(3) if R is None else np.array(R); s.add(m, [list(R @ np.array(v) + np.array(t)) for v in verts], faces)
Part.xform = xform
def Rxyz(ax, ay, az):
    a, b, c = [math.radians(x) for x in (ax, ay, az)]
    X = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Y = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Z = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Y @ X @ Z
def ngon(cx, cz, r, y, n, ph=0.0, rr=None):
    return [[cx + (rr[k] if rr else r)*math.cos(2*math.pi*k/n + ph), y, cz - (rr[k] if rr else r)*math.sin(2*math.pi*k/n + ph)] for k in range(n)]
def tri(p): return sum(sum(len(f)-2 for f in g[1]) for g in p.g.values())

# ======================= MINE-HEAD  world [134,18.3,392], envelope 14x18x12 (x +-7, y 0..18, z +-6), yaw 0, pivot base centre.
p = new('mine_head', 'mine_head', [14, 18, 12], 'Candy-striped headframe with sheave wheel over a timber shaft collar (west), winding house with drum, chimney and gable roof (east), ore cart heaped with rock candy on a short track between them.', 'base centre (world [134,18.3,392], yaw 0)')
# shaft collar + headframe (west half, centre x -3.8)
hx = -3.8
p.box('Timber', [hx, 0.4, 0], [4.6, 0.8, 4.6]); p.box('Iron', [hx, 0.82, 0], [3.0, 0.05, 3.0])
for sx in (-1, 1):
    for sz in (-1, 1):
        a = [hx + sx*2.0, 0.8, sz*2.0]; b = [hx + sx*0.75, 14.6, sz*0.75]
        q = [a[i] + (b[i]-a[i])*k/7 for i in range(3) for k in range(8)]
        for k in range(7):                                   # striped legs: 7 alternating segments
            a0 = [a[i] + (b[i]-a[i])*k/7 for i in range(3)]; a1 = [a[i] + (b[i]-a[i])*(k+1)/7 for i in range(3)]
            p.bar('PepRed' if k % 2 == 0 else 'MintWhite', a0, a1, 0.42)
for y, h in ((4.5, 1.73), (9.0, 1.31)):                     # horizontal girts (legs at that height)
    for sz in (-1, 1): p.bar('Timber', [hx - h, y, sz*h], [hx + h, y, sz*h], 0.22)
    for sx in (-1, 1): p.bar('Timber', [hx + sx*h, y, -h], [hx + sx*h, y, h], 0.22)
p.box('Timber', [hx, 14.75, 0], [2.2, 0.3, 2.2])           # sheave deck
for sz in (-0.95, 0.95): p.box('Iron', [hx, 15.4, sz], [0.5, 1.0, 0.12])
R0, cy = 1.7, 16.2                                          # sheave wheel (axis z), top 17.9
rim_o = [[hx + R0*math.cos(2*math.pi*k/16), cy + R0*math.sin(2*math.pi*k/16)] for k in range(16)]
for k in range(16):
    a0, a1 = 2*math.pi*k/16, 2*math.pi*(k+1)/16
    pts = [[hx + r*math.cos(a), cy + r*math.sin(a)] for r, a in ((R0, a0), (R0, a1), (R0-0.3, a1), (R0-0.3, a0))]
    p.add('Brass', [[x, y, -0.15] for x, y in pts] + [[x, y, 0.15] for x, y in pts], [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
for k in range(4):
    a = math.pi*k/4; p.bar('Iron', [hx - (R0-0.3)*math.cos(a), cy - (R0-0.3)*math.sin(a), 0], [hx + (R0-0.3)*math.cos(a), cy + (R0-0.3)*math.sin(a), 0], 0.12)
p.cyl('Iron', [hx, cy, 0], 0.25, -0.9, 0.9, 8, 'z')
# back-stays from the headframe top down to the winding-house side
for sz in (-1, 1): p.bar('Timber', [hx + 0.75, 14.3, sz*0.75], [1.2, 0.8, sz*2.2], 0.3)
# winding house (east): x 1.0..6.6, z -4..4
p.box('Brick', [3.8, 0.25, 0], [5.8, 0.5, 8.2]); p.box('CreamTaffy', [3.8, 3.25, 0], [5.4, 5.5, 7.8])
for x0, x1 in ((1.0, 3.8), (6.6, 3.8)):
    vs = [[x0, 6.0, -4.3], [x1, 8.6, -4.3], [x1, 8.6, 4.3], [x0, 6.0, 4.3]]; vs += [[v[0], v[1] + 0.25, v[2]] for v in vs]
    p.add('PepRed', vs, [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
for zf in (-3.9, 3.9): p.add('CreamTaffy', [[1.1, 6.0, zf], [6.5, 6.0, zf], [3.8, 8.5, zf]], [(0, 1, 2)])
p.box('Brick', [5.6, 8.6, 2.6], [0.9, 4.0, 0.9]); p.box('Iron', [5.6, 10.65, 2.6], [1.1, 0.12, 1.1])   # chimney to 10.7
for z in (-2.5, 0.0, 2.5): p.box('Window', [6.52, 3.8, z], [0.06, 1.2, 1.0]); p.box('MintWhite', [6.55, 3.1, z], [0.06, 0.15, 1.3])
p.box('Timber', [3.8, 2.0, -3.92], [1.4, 3.0, 0.06]); p.box('MintWhite', [3.8, 3.6, -3.94], [1.8, 0.2, 0.06])     # door (north)
p.cyl('Licorice', [1.0, 4.2, 0], 0.7, -1.2, 1.2, 12, 'z')      # winding drum poking out of the west wall
p.bar('Iron', [1.0, 4.9, 0], [hx + R0, cy, 0], 0.08)             # hoist cable drum -> sheave
p.bar('Iron', [hx - R0, cy, 0], [hx - R0, 1.0, 0], 0.08)           # cable down the shaft
# track + ore cart (south side between, x -1..1? keep under the back-stays): rails along x at z 4.6..5.6
for z in (4.55, 5.45): p.box('Iron', [-0.5, 0.06, z], [7.0, 0.12, 0.1])
for x in (-3.5, -2.0, -0.5, 1.0, 2.5): p.box('Timber', [x, 0.03, 5.0], [0.3, 0.06, 1.6])
p.box('Iron', [-0.5, 1.0, 5.0], [2.2, 1.4, 1.4]); p.box('PepRed', [-0.5, 1.75, 5.0], [2.3, 0.15, 1.5])
for x in (-1.2, 0.2):
    for z in (4.3, 5.7): p.cyl('Licorice', [x, 0.32, 0], 0.3, z - 0.07, z + 0.07, 10, 'z')
rnd = random.Random(7)
for k in range(9):
    p.octa(['CrystalGlow', 'Bubblegum', 'Lemon'][k % 3], [-0.5 + rnd.uniform(-0.8, 0.8), 1.85, 5.0 + rnd.uniform(-0.45, 0.45)], rnd.uniform(0.25, 0.4), 1.5)
p.ground_note = 'Base y 0 = world 18.3 (world.json POI, ground sampled from terrain). The brick/timber plinths are 0.5-0.8 tall so small terrain undulation stays hidden; sink the model if the sampled ground is lower.'

# ======================= LIFT CAGE: outer 7x7x9.5, floor 6x6 clear 8, posts 0.4, lattice 0.15 @1.0, waist rail 3.5, 4-wide opening on -Z (landing side). Pivot floor centre (floor top y 0).
p = new('lift_cage', 'lift_cage', [7, 9.5, 7], 'Shared mesh for all 4 lift routes. Floor slab y -0.5..0, roof frame y 8..9 (clear 8), candy-striped 0.4 corner posts, 0.15 lattice bars at 1.0 on three sides and beside the 4-wide opening on -Z (turn the cage so -Z faces the landing), brass waist rail at 3.5, hoist eye on the roof.', 'floor centre (top of the floor slab); -Z = opening, faces the landing')
p.box('Iron', [0, -0.25, 0], [7.0, 0.5, 7.0]); p.box('Timber', [0, 0.02, 0], [6.0, 0.04, 6.0])
for sx in (-1, 1):
    for sz in (-1, 1):
        for k in range(9): p.box('PepRed' if k % 2 == 0 else 'MintWhite', [sx*3.3, -0.5 + 9.5*(k+0.5)/9, sz*3.3], [0.4, 9.5/9, 0.4])
p.box('Iron', [0, 8.25, 0], [7.0, 0.5, 7.0]) if False else None
for sx in (-1, 1): p.box('Iron', [sx*3.3, 8.5, 0], [0.4, 1.0, 6.2]); p.box('Iron', [0, 8.5, sx*3.3], [6.2, 1.0, 0.4])
p.box('PepRed', [0, 8.9, 0], [6.2, 0.2, 6.2])
p.box('Iron', [0, 9.0, 0], [0.8, 0.0, 0.8]) if False else None
def wall(axis, sgn, ranges):
    for lo, hi in ranges:                                             # vertical bars at 1.0 inside [lo, hi]
        u = lo
        while u <= hi + 1e-6:
            c = [u, 4.0, sgn*3.25] if axis == 'z' else [sgn*3.25, 4.0, u]
            p.box('Iron', c, [0.15, 8.0, 0.15]); u += 1.0
        for y in (1.0, 2.0, 5.0, 6.0, 7.0):                              # horizontals (waist rail at 3.5 separately)
            c = [(lo+hi)/2, y, sgn*3.25] if axis == 'z' else [sgn*3.25, y, (lo+hi)/2]
            s_ = [hi - lo + 0.15, 0.15, 0.15] if axis == 'z' else [0.15, 0.15, hi - lo + 0.15]
            p.box('Iron', c, s_)
        c = [(lo+hi)/2, 3.5, sgn*3.25] if axis == 'z' else [sgn*3.25, 3.5, (lo+hi)/2]
        p.box('Brass', c, [hi - lo + 0.15, 0.22, 0.22] if axis == 'z' else [0.22, 0.22, hi - lo + 0.15])
wall('z', 1, [(-2.5, 2.5)]); wall('x', 1, [(-2.5, 2.5)]); wall('x', -1, [(-2.5, 2.5)])
wall('z', -1, [(-2.9, -2.1), (2.1, 2.9)])                              # opening x -2..2 on -Z
p.box('PepRed', [0, 8.0 - 0.15, -3.3], [4.0, 0.3, 0.3])                 # opening header (clear 8 kept: underside 7.7?) 
p.notes.append('Opening header sits in the roof band (y 7.7..8.0 under the roof frame) -> clear height in the doorway is 7.7; the 8 clear height holds inside the cage.')
p.cyl('Brass', [0, 0, 0], 0.35, 9.0, 9.0 + 0.0001, 8, 'y') if False else None
p.box('Iron', [0, 9.0 - 0.001 + 0.0, 0], [0.01, 0.01, 0.01]) if False else None

# ======================= GONDOLA CABIN: outer 8W x 6D x 8H, inner 7x5 clear 7, benches 1.5 deep seat 1.8, windows 3.2..6.5, hanger 0.5 sq rising 4 to the grip. Pivot = grip.
p = new('gondola', 'gondola_cabin', [8, 12, 6], 'Enclosed seated cabin (x = width 8, z = depth 6); cabin base 12 below the grip, roof 4 below it; inner 7x5 with clear height 7 (floor top 0.5, ceiling 7.5 above the base); two facing benches 1.5 deep (seat 1.8) along the long walls; glazing 3.2..6.5 on all four sides with candy-striped corner posts; door on +X end; hanger arm 0.5 square from the roof to the grip clamp.', 'cable grip (cabin base at y -12); cable runs along +-Z')
B = -12.0
def gb(m, c, s): p.box(m, [c[0], c[1] + B, c[2]], s)
gb('Iron', [0, 0.25, 0], [8, 0.5, 6])
for (cx, cz, sx_, sz_) in ((0, 2.75, 7.0, 0.5), (0, -2.75, 7.0, 0.5), (3.75, 0, 0.5, 6.0), (-3.75, 0, 0.5, 6.0)):
    gb('CreamTaffy', [cx, 1.85, cz], [sx_, 2.7, sz_]); gb('PepRed', [cx, 7.0, cz], [sx_, 1.0, sz_])
    gb('Window', [cx, 4.85, cz], [sx_ - 0.6 if sx_ > 1 else 0.12, 3.3, 0.12 if sz_ < 1 else sz_ - 0.6])
for sx in (-1, 1):
    for sz in (-1, 1):
        for k in range(4): gb('PepRed' if k % 2 else 'MintWhite', [sx*3.75, 3.2 + 3.3*(k+0.5)/4, sz*2.75], [0.5, 3.3/4, 0.5])
gb('MintWhite', [0, 3.15, 2.75], [7.0, 0.12, 0.52]); gb('MintWhite', [0, 3.15, -2.75], [7.0, 0.12, 0.52])
gb('PepRed', [0, 7.75, 0], [8, 0.5, 6]); gb('MintWhite', [0, 8.0 - 0.02, 0], [6.0, 0.04, 4.0]) if False else None
for sz in (-1, 1):                                               # benches
    gb('Timber', [0, 1.6, sz*1.75], [6.6, 0.4, 1.5]); gb('Timber', [0, 1.05, sz*1.75], [6.6, 1.1, 1.2])
    gb('Bubblegum', [0, 2.6, sz*2.35], [6.6, 1.4, 0.3])
gb('Timber', [4.02, 3.4, 0], [0.04, 5.0, 1.6]) if False else gb('Brass', [3.98, 2.0, 0.6], [0.04, 0.15, 0.4])
p.box('Iron', [0, -4.0 + 2.0 - 0.0, 0][:1] + [-2.0, 0], [0.5, 4.0, 0.5])        # hanger arm y -4..0
p.box('Iron', [0, 0.0, 0], [1.4, 0.7, 1.6]); p.cyl('Brass', [0, 0, 0], 0.18, -1.0, 1.0, 10, 'z')                # grip clamp + cable pin (pin along cable, Z)
p.box('Brass', [0, -3.8, 0], [1.2, 0.3, 1.2])

# ======================= SCATTER (pivot base, designed at mid size so 0.8-1.25 scale covers the props.md ranges)
def cactus(pid, H, rdisk, mats, side):
    p = new('scatter', pid, None, f'Lollipop cactus, H {H} (x0.8..1.25 -> {H*0.8:.1f}..{H*1.25:.1f}; spec 6-10), disc {2*rdisk} dia', 'base centre')
    cy = H - rdisk
    p.loft('Lime', [ngon(0, 0, 0.32, 0, 8), ngon(0, 0, 0.26, cy, 8)])
    for k in range(12):
        a0, a1 = 2*math.pi*k/12, 2*math.pi*(k+1)/12
        pts = [[0, cy], [rdisk*math.cos(a0), cy + rdisk*math.sin(a0)], [rdisk*math.cos(a1), cy + rdisk*math.sin(a1)]]
        p.add(mats[k % 2], [[x, y, -0.25] for x, y in pts] + [[x, y, 0.25] for x, y in pts], [(2,1,0),(3,4,5),(1,2,5,4),(0,1,4,3),(2,0,3,5)])
    if side:
        sy = cy*0.5; p.bar('Lime', [0, sy, 0], [1.1, sy + 0.9, 0], 0.3); p.bar('Lime', [1.1, sy + 0.9, 0], [1.1, sy + 1.9, 0], 0.26)
        p.cyl(mats[0], [1.1, sy + 2.5, 0], 0.65, -0.18, 0.18, 12, 'z'); p.cyl('MintWhite', [1.1, sy + 2.5, 0], 0.3, -0.2, 0.2, 8, 'z')
    p.loft('Strata', [ngon(0, 0, 0.6, 0, 8), ngon(0, 0, 0.4, 0.35, 8)])
    return p
cactus('cactus_a', 8.0, 1.5, ['PepRed', 'MintWhite'], False)
cactus('cactus_b', 7.6, 1.5, ['Bubblegum', 'MintWhite'], True)
cactus('cactus_c', 8.0, 1.5, ['Lemon', 'PepRed'], True)
def gumdrop(pid, D, mat, seed):
    p = new('scatter', pid, None, f'Gumdrop, {D} dia (x0.8..1.25 -> {D*0.8:.2f}..{D*1.25:.2f}; spec 1.5-3)', 'base centre')
    r = D/2; rings = [ngon(0, 0, r, 0, 12), ngon(0, 0, r*1.02, r*0.35, 12)]
    for k in range(1, 5):
        t = k/5*math.pi/2; rings.append(ngon(0, 0, r*1.02*math.cos(t), r*0.35 + r*0.75*math.sin(t), 12))
    rings.append([[0, r*1.1, 0]]); p.loft(mat, rings)
    rnd = random.Random(seed)
    for k in range(8):
        a = rnd.uniform(0, 2*math.pi); t = rnd.uniform(0.2, 1.1)
        p.octa('Sugar', [r*0.95*math.cos(t)*math.cos(a)*0.95, r*0.35 + r*0.75*math.sin(t), r*0.95*math.cos(t)*math.sin(a)*0.95], 0.06*D, 1.3)
    return p
gumdrop('gumdrop_a', 2.0, 'Cherry', 1); gumdrop('gumdrop_b', 2.2, 'Lime', 2); gumdrop('gumdrop_c', 2.3, 'Lemon', 3)
def chunk(p, m, c, s, R):
    vs = [[-1,-1,-1],[1,-1,-1],[1,-1,1],[-1,-1,1],[-0.7,1,-0.7],[0.7,1,-0.7],[0.7,1,0.7],[-0.7,1,0.7]]
    p.xform(m, [[v[0]*s[0]/2, v[1]*s[1]/2, v[2]*s[2]/2] for v in vs], [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)], R, c)
def ore(pid, W, gem, seed):
    p = new('scatter', pid, None, f'Ore cluster, {W} wide (x0.8..1.25 -> {W*0.8:.2f}..{W*1.25:.2f}; spec 2-4)', 'base centre')
    rnd = random.Random(seed); half = W/2
    for k in range(9):
        s = rnd.uniform(0.35, 0.6)*W*0.5; a = rnd.uniform(0, 2*math.pi); d = rnd.uniform(0, half - s*0.75)
        chunk(p, 'Strata' if k % 3 else 'Iron', [d*math.cos(a), s*0.35, d*math.sin(a)], [s, s*0.8, s*0.9], Rxyz(rnd.uniform(-12, 12), rnd.uniform(0, 90), rnd.uniform(-12, 12)))
    for k in range(10):
        a = rnd.uniform(0, 2*math.pi); d = rnd.uniform(0, half*0.6)
        p.octa(gem, [d*math.cos(a), W*0.22 + rnd.uniform(0, 0.25)*W, d*math.sin(a)], rnd.uniform(0.09, 0.15)*W, 1.6)
    p.norm = ('W', W); return p
ore('ore_a', 2.6, 'CrystalGlow', 11); ore('ore_b', 3.0, 'Lemon', 12); ore('ore_c', 3.2, 'Violet', 13)
def spire(p, m, base, h, r, R):
    ring0 = ngon(0, 0, r, 0, 6); ring1 = ngon(0, 0, r*0.9, h*0.78, 6); tip = [[0, h, 0]]
    V = ring0 + ring1 + tip; F = [list(range(5, -1, -1))] + [[i, (i+1) % 6, 6 + (i+1) % 6, 6 + i] for i in range(6)] + [[6 + i, 6 + (i+1) % 6, 12] for i in range(6)]
    p.xform(m, V, F, R, base)
def crystal(pid, H, mat, seed):
    p = new('scatter', pid, None, f'Rock-candy crystal spire cluster, tallest {H} (x0.8..1.25 -> {H*0.8:.2f}..{H*1.25:.2f}; spec 2-5)', 'base centre')
    rnd = random.Random(seed)
    spire(p, mat, [0, -0.05, 0], H, 0.32*H/3.4, np.eye(3))
    for k in range(5):
        a = 2*math.pi*k/5 + rnd.uniform(-0.3, 0.3); h = H*rnd.uniform(0.4, 0.7)
        spire(p, mat if k % 2 else 'MintWhite', [0.35*H/3.4*math.cos(a), -0.05, 0.35*H/3.4*math.sin(a)], h, 0.22*H/3.4, Rxyz(rnd.uniform(14, 26)*math.sin(a), 0, -rnd.uniform(14, 26)*math.cos(a)))
    chunk(p, 'Strata', [0, 0.1, 0], [1.4*H/3.4, 0.45*H/3.4, 1.3*H/3.4], Rxyz(0, 20, 0))
    p.norm = ('H', H); return p
crystal('crystal_a', 2.6, 'CrystalGlow', 21); crystal('crystal_b', 3.4, 'Violet', 22); crystal('crystal_c', 4.0, 'CrystalGlow', 23)
def hoodoo(pid, H, W, seed, cap):
    p = new('scatter', pid, None, f'Striped hoodoo, H {H} x W {W} (x0.8..1.25 -> H {H*0.8:.1f}..{H*1.25:.1f}, W {W*0.8:.2f}..{W*1.25:.2f}; spec 8-20 x 3-6)', 'base centre')
    rnd = random.Random(seed); n = 10; ys = [0] + sorted(rnd.uniform(0.08, 0.86) for _ in range(6)) + [0.88]
    prof = lambda t: W/2*(1.0 - 0.38*math.sin(math.pi*min(t/0.85, 1)) ** 0.8 + 0.05*math.sin(t*23))
    for i, (t0, t1) in enumerate(zip(ys, ys[1:])):
        rr0 = [prof(t0)*(1 + 0.06*math.sin(k*1.7 + i)) for k in range(n)]; rr1 = [prof(t1)*(1 + 0.06*math.sin(k*1.7 + i + 1)) for k in range(n)]
        p.loft('Watermelon' if i % 2 == 0 else 'CreamTaffy', [ngon(0, 0, 0, t0*H, n, 0, rr0), ngon(0, 0, 0, t1*H, n, 0, rr1)], cap0=(i == 0), cap1=False)
    ytop = 0.88*H; rc = W*0.36
    p.loft('Strata', [ngon(0, 0, prof(0.88), ytop, n), ngon(0, 0, rc, ytop + 0.02*H, n), ngon(0, 0, rc*0.95, ytop + 0.05*H, n)], cap0=True, cap1=True)
    rings = [ngon(0, 0, rc*math.cos(t), ytop + 0.05*H + (H*0.07)*math.sin(t), n) for t in [k/4*math.pi/2 for k in range(4)]] + [[[0, H, 0]]]
    p.loft(cap, rings)
    p.norm = ('WXZ', W); return p
hoodoo('hoodoo_a', 10.0, 3.8, 31, 'Cherry'); hoodoo('hoodoo_b', 13.0, 4.2, 32, 'Lime'); hoodoo('hoodoo_c', 16.0, 4.6, 33, 'Bubblegum')

def normalize(p):
    if not hasattr(p, 'norm'): return
    V = np.array([v for vs, f in p.g.values() for v in vs]); lo, hi = V.min(0), V.max(0); kind, val = p.norm
    if kind == 'H': k = val/(hi[1] - lo[1]); kx = k; ky = k
    elif kind == 'W': k = val/max(hi[0]-lo[0], hi[2]-lo[2]); kx = k; ky = k
    else: kx = val/max(hi[0]-lo[0], hi[2]-lo[2]); ky = 1.0
    for m, (vs, f) in p.g.items():
        for v in vs: v[0] = round(v[0]*kx, 5); v[2] = round(v[2]*kx, 5); v[1] = round((v[1] - lo[1])*ky, 5)
for parts in SETS.values():
    for p in parts: normalize(p)
for name, parts in SETS.items():
    os.makedirs(os.path.join(HERE, name), exist_ok=True); out = []
    for p in parts:
        out.append(dict(id=p.name, hole=name, anchor=[0, 0, 0], notes=p.notes + ([p.ground_note] if hasattr(p, 'ground_note') else []), envelope=p.env, pivot=p.pivot_desc,
                        groups={m: dict(verts=v, faces=f) for m, (v, f) in p.g.items()}))
    json.dump(out, open(os.path.join(HERE, name, 'parts.json'), 'w'))
    print(name, [(p.name, tri(p)) for p in parts])
