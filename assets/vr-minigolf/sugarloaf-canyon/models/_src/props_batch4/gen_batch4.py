"""Sugarloaf batch 4: H13-H18 landmarks. Pure python -> parts.json (per part: material -> verts/faces, Roblox coords,
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

# ============ H13 maze_rock [-5.5,0,-28] env 7x4x24 -> x -9..-2, z -40..-16, y 0..4.
# holes.json rock_w9..w12 (1.0 tall rails) box the island x -9..-2, z -40..-16; inside them x -8.5..-2.5, z -39.5..-16.5 is not felt.
p, A = mk('h13', 'maze_rock'); r = p.rel
xw, xe, zn, zs = -8.4, -2.6, -39.4, -16.6
bands = [(0.0, 1.0, 'Watermelon'), (1.0, 1.6, 'CreamTaffy'), (1.6, 2.2, 'Watermelon')]
for y0, y1, m in bands:
    p.prism_xy(m, [(xw - A[0], y0), (xe - A[0], y0), (xe - A[0], y1), (xw - A[0], y1)], zn - A[2], zs - A[2])
p.prism_xy('CreamTaffy', [(xw - A[0], 2.2), (xe - A[0], 2.2), (xe - 0.5 - A[0], 2.75), (xw + 0.5 - A[0], 2.75)], zn - A[2], zs - A[2])
caps = ['Cherry', 'Lime', 'Bubblegum']
def oct_ring(cx, cz, rr, y): return [[cx + rr*math.cos(2*math.pi*(k+0.5)/8), y, cz - rr*math.sin(2*math.pi*(k+0.5)/8)] for k in range(8)]
for i in range(6):
    z = -18.6 - i*3.76; cx, cz = -5.5 - A[0], z - A[2]; top = 3.0 + 0.125*((i*37) % 3)
    p.loft('Watermelon', [oct_ring(cx, cz, 1.3, 2.7), oct_ring(cx, cz, 1.15, 3.0)], cap0=True, cap1=True)
    p.loft('CreamTaffy', [oct_ring(cx, cz, 1.15, 3.0), oct_ring(cx, cz, 1.0, top)], cap0=False, cap1=True)
    rings = [oct_ring(cx, cz, 1.05*math.cos(t), top + 0.7*math.sin(t)) for t in [k/4*math.pi/2 for k in range(4)]] + [[[cx, top + 0.7, cz]]]
    p.loft(caps[i % 3], rings)
p.notes.append('Banded sandstone spine (watermelon/cream bands, chamfered top to 2.75) filling the holes.json rock island inside rock_w9..w12, 0.1 off their inner faces; six striped hoodoo stubs with gumdrop caps along it, cap tops 3.7..3.95 (inside the 4.0 envelope). Nothing overhangs a corridor; the 1.0-tall collider rails are the course build.')
P.append(p)

# ============ H14 cableway_trestle [0,0,-24] env 10x11.35x1.5 (x +-5, z -24.75..-23.25). Rails rail1/rail9 outer faces x +-4.5 (top 1.0).
p, A = mk('h14', 'cableway_trestle'); r = p.rel
for sx in (-1, 1):
    p.bar('Timber', r(sx*4.81, 0.01, -24.0), r(sx*4.5, 10.35, -24.0), 0.33)          # A-leg, splayed out at the foot
    p.box('Iron', r(sx*4.8, 0.08, -24.0), [0.4, 0.16, 1.2])                         # foot plate x 4.6..5.0
    p.bar('Timber', r(sx*4.55, 8.65, -24.0), r(sx*2.9, 10.3, -24.0), 0.22)           # knee brace (lowest point > 8.4 over the lane felt)
    for zz in (-24.35, -23.65):                                                     # cross-tie bolts
        p.box('Brass', r(sx*4.5, 9.6, zz), [0.2, 0.2, 0.06])
p.box('Timber', r(0, 10.85, -24.0), [10.0, 1.0, 1.0])                               # beam y 10.35..11.35 (= occluder)
for sx in (-1, 1): p.box('PepRed', r(sx*4.75, 10.84, -24.0), [0.5, 1.02, 1.04])     # peppermint end caps
p.box('Iron', r(0, 11.4, -24.0), [10.0, 0.08, 0.3]) if False else None
p.box('Iron', r(0, 10.85, -24.52), [1.2, 0.6, 0.04]); p.box('Iron', r(0, 10.85, -23.48), [1.2, 0.6, 0.04])  # hinge cheek plates on the beam faces
p.cyl('Brass', r(0, 10.85, 0), 0.2, -24.56 - A[2], -23.44 - A[2], 12, 'z')         # hinge pin through the beam (above the hanger)
p.sweep_boxes = [[[-2.7, 0.3, -25.0], [2.7, 10.3, -23.0]]]
p.notes.append('Two splayed timber A-legs (foot centre x +-4.81, top +-4.5) standing 0.11 outside rail1/rail9, beam = the holes.json beam occluder y 10.35..11.35 with peppermint end caps, knee braces above y 8.4, iron hinge cheeks + brass pin on the beam faces. Nothing below the beam inside x +-2.7: the ore-bucket swing (+-9 deg on a 9 hanger, batch 1) stays clear. The overhead main cableway is world kit, not part of this mesh.')
P.append(p)

# ============ H15 sugar_dune [0,-2.2,-24] env 30x6x34 -> x -15..15, y -2.2..3.8, z -41..-7. Dune felt is holes.json (yaw 25 plane).
# Dressing = sugar drifts outside dune_rail1 (west) / dune_rail2 (east), built in dune-local (u across the fall line, v along it).
p, A = mk('h15', 'sugar_dune'); r = p.rel
FD = next(f for f in H['h15']['felt'] if f['id'] == 'dune'); DC = FD['center']; DY = FD['yaw']
def d2w(u, y, v):  # dune local -> hole local
    q = roty([u, 0, v], DY); return [DC[0] + q[0], y, DC[2] + q[2]]
W15 = H['h15']['walls']; F15 = H['h15']['felt']
def Ry(d):
    a = math.radians(d); return np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
def wall_d(P):
    P = np.array(P, float); best = 9e9
    for w in W15:
        q = (P - np.array(w['center'])) @ Ry(w.get('yaw', 0)); d = np.abs(q) - np.array(w['size'])/2
        best = min(best, float((np.linalg.norm(np.maximum(d, 0), axis=1) + np.minimum(d.max(axis=1), 0)).min()))
    return best
def on_felt(P):
    P = np.array(P, float)
    for f in F15:
        q = (P - np.array(f['center'])) @ Ry(f.get('yaw', 0))
        if ((np.abs(q[:, 0]) <= f['size'][0]/2 + 0.05) & (np.abs(q[:, 2]) <= f['size'][1]/2 + 0.05)).any(): return True
    return False
def drift(prof_fn, side, ylo, mats):
    vs = np.arange(-15.0, 15.01, 1.0); keep = []
    for v in vs:
        ring = [d2w(u, y, v) for u, y in prof_fn(v)]; R = np.array(ring)
        ok = (R[:, 0].min() >= -18.5 + 1e-6) and (R[:, 0].max() <= 18.5 - 1e-6) and (R[:, 2].min() >= -41 + 1e-6) and (R[:, 2].max() <= -7 - 1e-6)
        dense = np.vstack([R + (np.roll(R, -1, 0) - R)*t for t in np.linspace(0, 1, 6)])
        ok = ok and wall_d(dense) >= 0.12 and not on_felt(dense)
        keep.append((v, ring if ok else None))
    runs, cur = [], []
    for v, ring in keep:
        if ring is None:
            if cur: runs.append(cur); cur = []
        else: cur.append((v, ring))
    if cur: runs.append(cur)
    run = max(runs, key=len)
    rings = [[[x - A[0], y - A[1], z - A[2]] for x, y, z in ring] for v, ring in run]
    # split rings into a lower and upper band (two materials): profile points 0..k-1 share
    p.loft(mats, rings)
    return run[0][0], run[-1][0]
TAPER = {}
def tap(side, v):
    lo, hi = TAPER.get(side, (-99, 99)); d = min(v - lo, hi - v)
    return 1.0 if d >= 3.0 else max(0.35, 0.35 + 0.65*d/3.0)
def west_prof(v):   # rev1: taller, rounded mound (half-dome section), crest up to ~3.3
    hc = (3.7 + 0.6*math.sin(v*0.45))*tap('w', v); pts = [(-12.62, -1.0)]
    for k in range(1, 10):
        t = math.pi*k/10; u = -14.72 - 2.1*math.cos(t); yb = -1.0 - 0.4*(1 - math.cos(t))/2
        pts.append((u, yb + hc*math.sin(t)**0.75))
    return pts + [(-16.82, -1.4)]
def east_prof(v):
    hc = (2.6 + 0.4*math.sin(v*0.5 + 1.0))*tap('e', v); pts = [(12.62, -3.45)]
    for k in range(1, 10):
        t = math.pi*k/10; u = 14.4 - 1.78*math.cos(t)
        pts.append((u, -3.45 + hc*math.sin(t)**0.75))
    return pts + [(16.18, -3.45)]
_g = dict(p.g); wv = drift(west_prof, -1, -1.0, 'Sugar'); ev = drift(east_prof, 1, -3.45, 'Sugar')
p.g = {}; TAPER['w'] = wv; TAPER['e'] = ev
wv = drift(west_prof, -1, -1.0, 'Sugar'); ev = drift(east_prof, 1, -3.45, 'Sugar')
# ridge stripe of pink sugar along the west crest (thin cap, follows the crest)
vm = (wv[0] + wv[1])/2
# striped sand-sled propped on the west drift, nose up over the crest, at mid run
u0, v0 = -15.8, vm
y0 = -1.0 + 0.0
yc = west_prof(v0)[3][1] - 0.3
for k, mm in enumerate(['PepRed', 'MintWhite', 'PepRed', 'MintWhite']):
    vv = v0 - 0.9 + 0.45*k + 0.225
    c = d2w(u0, yc + 0.2 + 0.18*k, vv); p.box(mm, r(*c), [0.9, 0.12, 0.45], DY)
c = d2w(u0, yc + 0.95, v0 + 1.05); p.box('PepRed', r(*c), [0.9, 0.35, 0.12], DY)
p.ranges = dict(west_v=wv, east_v=ev)
p.env_boxes = [[[-18.5, -2.2, -41], [18.5, 3.8, -7]], [[0, -3.6, -41], [18.5, 3.8, -7]]]
p.notes.append(f'Powdered-sugar drifts outside the holes.json dune rails (felt plane = holes.json): west drift 0.12 outside dune_rail1, rev1: taller rounded half-dome drifts (west crest ~2.4..3.3, east up to ~-0.4 over its -3.45 base), ends tapered over 3 studs, (dune-local v {wv[0]}..{wv[1]}), east drift outside dune_rail2 (v {ev[0]}..{ev[1]}), both trimmed automatically where they would leave the envelope (widened from x +-15 to +-18.5: the 30-wide props.md box centred on the anchor cuts the drifts, while the holes.json dune rails/green run to x +-17.75), touch a rail (<0.12) or reach felt. East drift sits on the low east side (felt edge y -3.4), so its base runs to y -3.45, below the props.md envelope bottom (-2.2): envelope extended to y -3.6 on the east half only. Striped sled (4 stripes + curled nose) propped on the west drift shoulder. Sled tracks / wind ripples are felt decals (slope_arrows anchor), not mesh.')
P.append(p)

# ============ H16 sinkhole_rim [0,0,-16.2] env 3.4x0.3x3.4. Opening = gap in the deck felt x +-1.2, z -15..-17.4 (deck top y 0).
p, A = mk('h16', 'sinkhole_rim'); r = p.rel
o, t = 1.18, 0.12
for (cx, cz, sx, sz) in ((0, -16.2 + (o - t/2), 2*o, t), (0, -16.2 - (o - t/2), 2*o, t), (o - t/2, -16.2, t, 2*o - 2*t), (-(o - t/2), -16.2, t, 2*o - 2*t)):
    p.box('GeodeRim', r(cx, -0.15, cz), [sx, 0.3, sz])
for k in range(12):
    side = k // 3; j = (k % 3 - 1)*0.7
    cx, cz = [(j, -16.2 + o - t - 0.05), (j, -16.2 - o + t + 0.05), (o - t - 0.05, -16.2 + j), (-(o - t - 0.05), -16.2 + j)][side]
    p.octa('CrystalGlow', r(cx, -0.17, cz), 0.1 + 0.03*(k % 2), 1.2)
for sx in (-1, 1):                                                           # low rope railing on posts outside the deck rails, south of the bowl
    zs_ = [-0.8, -5.6, -10.4]
    for z in zs_:
        p.box('Timber', r(sx*4.75, 0.9, z), [0.3, 1.8, 0.3]); p.box('PepRed', r(sx*4.75, 1.9, z), [0.34, 0.2, 0.34])
    for z0_, z1_ in zip(zs_, zs_[1:]):
        for ytop in (1.6, 0.95):
            N = 5; pts = [[sx*4.75, ytop - 0.15*4*q*(1-q), z0_ + (z1_ - z0_)*q] for q in [i/N for i in range(N+1)]]
            for q0, q1 in zip(pts, pts[1:]): p.bar('Rope', r(*q0), r(*q1), 0.1)
p.env_boxes = [[[-1.7, -0.3, -17.9], [1.7, 0.3, -14.5]], [[-4.95, 0, -10.6], [-4.55, 2.0, -0.6]], [[4.55, 0, -10.6], [4.95, 2.0, -0.6]]]
p.overhead_exempt_boxes = [[[-4.25, -0.4, -24.0], [4.25, 0.0, -12.0]]]
p.notes.append('The rim is flush: a 0.12-thick crystal-rock collar lining the 2.4 x 2.4 felt opening, y -0.3..0 (inside the deck slab), with 12 glowing rock-candy crystals on its inner face (visual opening ~1.9). Nothing sits on the deck felt. Collar is over the bowl felt but inside the deck-slab band (the holes.json deck already covers that bowl end), so the 8-overhead rule treats it as deck. Envelope y extended to -0.3 for the flush collar. Rope railing on 3 posts each side, 0.1 outside deck_rail1/3, only south of the bowl (z -0.8..-10.4) so nothing hangs over bowl felt; envelope extended for these.')
P.append(p)

# ============ H17 gnomon [0,0,-36] env 1.6x9x6 (x +-0.8, z -39..-33). Plinth strips (holes.json) top y 1.2.
p, A = mk('h17', 'gnomon'); r = p.rel
yb, yt = 1.5, 9.0
p.box('Brass', r(0, 1.4, -36.0), [1.6, 0.2, 6.0])                               # base plate y 1.3..1.5 (0.1 over the plinth top)
def zh(y): return 3.0 - 6.0*(y - yb)/(yt - yb)                                  # hypotenuse: north edge vertical (z -3), toe at z +3
ys = [yb + (yt - yb)*k/8 for k in range(9)]
for k, (y0, y1) in enumerate(zip(ys, ys[1:])):
    poly = [(-3.0, y0), (zh(y0), y0), (zh(y1), y1), (-3.0, y1)] if k < 7 else [(-3.0, y0), (zh(y0), y0), (-3.0, y1)]
    p.prism_zy('PepRed' if k % 2 == 0 else 'MintWhite', poly, -0.5, 0.5)
p.box('Brass', r(0, 8.94, -38.7), [1.1, 0.12, 0.5])                              # brass tip cap
p.unreachable_discs = [dict(center=[0, -36.0], r=7.5)]
p.annulus = dict(center=[0, -36.0], r0=8.0, r1=11.7, ymax=1.0)
p.notes.append('Right-triangle blade 1.0 thick (vertical edge north at z -39, toe south at z -33), 8 candy stripes, from a brass base plate floating 0.1 over the holes.json plinth top (1.2) to 9.0. Felt under the solid r 7.5 plinth is unreachable, so it is not treated as reachable felt; the shadow-arm annulus r 8.2..11.5 is untouched.')
P.append(p)

# ============ H18 arch_gate [-9,0,-26] env 10x13x4 (x -14..-4, z -28..-24). Rails rail3 (outer face x -12.5) and rail11 (x -5.5), tops y 3.2. Ramp felt x -12..-6.
p, A = mk('h18', 'arch_gate'); r = p.rel
zf, zb = -24.4, -27.6
legy_i = [0, 1.6, 3.2, 4.8, 6.4, 8.6]; legy_o = [y*10.0/8.6 for y in legy_i]
th = [math.pi*(1 - k/12) for k in range(13)]
inner = [(-12.6, y) for y in legy_i] + [(-9 + 3.6*math.cos(a), 8.6 + 2.0*math.sin(a)) for a in th[1:-1]] + [(-5.4, y) for y in legy_i[::-1]]
outer = [(-14.0, y) for y in legy_o] + [(-9 + 5.0*math.cos(a), 10.0 + 3.0*math.sin(a)) for a in th[1:-1]] + [(-4.0, y) for y in legy_o[::-1]]
for i in range(len(inner) - 1):
    (ix0, iy0), (ix1, iy1), (ox0, oy0), (ox1, oy1) = inner[i], inner[i+1], outer[i], outer[i+1]
    v8 = [[ix0, iy0, zf], [ox0, oy0, zf], [ox0, oy0, zb], [ix0, iy0, zb], [ix1, iy1, zf], [ox1, oy1, zf], [ox1, oy1, zb], [ix1, iy1, zb]]
    p.hexa('Watermelon' if i % 2 == 0 else 'CreamTaffy', [r(*v) for v in v8])
p.notes.append('Natural arch, legs x -14..-12.6 and -5.4..-4.0 (0.1 outside rail3 / rail11, 1.4 wide instead of the 2.2 the sheet suggests: the rails leave no more room inside the 10 envelope), depth 3.2 (z -27.6..-24.4). Opening 7.2 wide, straight to 8.6 then elliptical to the crown underside 10.6; underside over the ramp felt (x -12..-6) is >= 9.7, i.e. >= 9.3 above the felt (>= 8 required). Outer crown 13.0. 24 alternating watermelon/cream stripe segments.')
P.append(p)

out = []
for p in P:
    out.append(dict(id=p.name, hole=p.hole, anchor=p.anchor, notes=p.notes, envelope=anchor(p.hole, p.name.split('_', 1)[1])['approx_size'],
                    env_boxes=getattr(p, 'env_boxes', None), collider_ids=getattr(p, 'collider_ids', None), rotor=getattr(p, 'rotor', None),
                    felt_exempt_kinds=getattr(p, 'felt_exempt_kinds', []), sweep_boxes=getattr(p, 'sweep_boxes', []),
                    overhead_exempt_boxes=getattr(p, 'overhead_exempt_boxes', []), unreachable_discs=getattr(p, 'unreachable_discs', []),
                    annulus=getattr(p, 'annulus', None),
                    groups={m: dict(verts=v, faces=f) for m, (v, f) in p.g.items()}))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.json'), 'w'))
print([(o['id'], sum(sum(len(f)-2 for f in g['faces']) for g in o['groups'].values())) for o in out])
