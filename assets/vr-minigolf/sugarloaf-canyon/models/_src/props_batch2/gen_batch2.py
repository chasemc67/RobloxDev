"""Sugarloaf batch 2: H1-H6 landmarks. Pure python -> parts.json (per part: material -> verts/faces, Roblox coords,
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

# ---- H1 trailhead_arch: envelope 9.5 x 10 x 1.2. Posts outside rails (rail inner faces +-3.5, outer +-4.0).
a = anchor('h01', 'trailhead_arch'); p = Part('h01_trailhead_arch', 'h01', a['position'])
for sx in (-1, 1):
    x = sx * 4.4                                   # 0.6 posts x 4.1..4.7: 0.1 clear of the rail outer face (4.0)
    for i in range(4):                              # candy stripes: 2-stud bands to y 8
        p.box('PepRed' if i % 2 == 0 else 'MintWhite', [x, 1.0 + 2*i, 0], [0.6, 2.0, 0.6])
    p.box('Timber', [x, 8.75, 0], [0.6, 1.5, 0.6])                     # post top inside the beam zone
p.box('Timber', [0, 9.25, 0], [9.5, 1.5, 1.16])                         # flat-topped crossbeam, bottom y 8.5 (> 8)
p.box('Timber', [0, 8.25, 0], [8.0, 0.5, 0.5])                         # under-rail y 8.0..8.5 (keeps >= 8 overhead)
p.box('MintWhite', [0, 9.25, 0.59], [6.0, 1.1, 0.02])                  # sign face on the beam (south, tee side)
p.box('PepRed', [0, 9.25, 0.62], [5.4, 0.7, 0.02]) if False else None
for k in range(6): p.box('PepRed', [-2.5 + k, 9.25, 0.6], [0.5, 1.1, 0.0]) if False else None
p.cyl('Bubblegum', [-3.6, 9.25, 0], 0.45, 0.58, 0.6, 16, 'z')         # swirl-lollipop badges on the beam face
p.cyl('Bubblegum', [3.6, 9.25, 0], 0.45, 0.58, 0.6, 16, 'z')
p.notes.append('Sign is mounted ON the beam face (y 8.7..9.8), not hung below: props.md needs >= 8 overhead clearance and the beam bottom is the 8-stud line. Posts 0.6 (anchor occluders), not 1.2 (sheet): 1.2 posts cannot fit outside the rails inside the 9.5 envelope.')
P.append(p)

# ---- H2 headframe: envelope 8 x 16 x 6 around [1,0,-22] -> x -3..5, z -25..-19. Middle channel rails x +-2.5 outer faces.
a = anchor('h02', 'headframe'); p = Part('h02_headframe', 'h02', a['position'])
AX = a['position'][0]
xl, xr = -2.8 - AX, 4.6 - AX        # leg centre lines (absolute -2.75 / 4.6): outside the channel (>= 0.1 clear of rails)
t = 0.4; Y8 = 8.8
apex = (1.0 - AX, 14.5)              # sheave axle over the anchor
for z in (-2.6, 2.6):
    # vertical legs to y 8.2 (outside channel), then A-frame members to the sheave above y >= 8
    p.bar('Timber', [xl, 0, z], [xl, Y8, z], t); p.bar('Timber', [xr, 0, z], [xr, Y8, z], t)
    p.bar('PepRed', [xl, Y8, z], [apex[0] - 0.5, apex[1], z*0.35], t); p.bar('PepRed', [xr, Y8, z], [apex[0] + 0.5, apex[1], z*0.35], t)
    for y0 in (0.3, 4.2):                           # lattice X-bracing in the side planes (legs outside the channel)
        p.bar('MintWhite', [xl, y0, z], [xl, y0 + 3.6, -z*0.0 + (z - math.copysign(5.2, z)) ], 0.2) if False else None
for x in (xl, xr):                                   # side-plane lattice: X braces between the two legs of each side
    for y0 in (0.4, 4.3):
        p.bar('MintWhite', [x, y0, -2.6], [x, y0 + 3.7, 2.6], 0.2); p.bar('MintWhite', [x, y0, 2.6], [x, y0 + 3.7, -2.6], 0.2)
    p.bar('Timber', [x, 4.2, -2.6], [x, 4.2, 2.6], 0.3)
for z in (-2.6, 2.6):                                # cross ties over the channel only above y 8
    p.bar('Timber', [xl, Y8 + 0.15, z], [xr, Y8 + 0.15, z], 0.3)
p.bar('Timber', [apex[0], 13.6, -0.95], [apex[0], 13.6, 0.95], 0.35)     # sheave platform beam
p.cyl('Iron', [apex[0], apex[1], 0], 1.5, -0.15, 0.15, 24, 'z')          # sheave wheel r 1.5 -> top y 16
p.cyl('PepRed', [apex[0], apex[1], 0], 0.35, -0.3, 0.3, 12, 'z')
for k in range(6):
    ang = math.pi*k/3; p.bar('Iron', [apex[0], apex[1], 0.17], [apex[0] + 1.35*math.cos(ang), apex[1] + 1.35*math.sin(ang), 0.17], 0.12)
p.bar('Timber', [apex[0], apex[1] - 0.3, -0.9], [apex[0], 0.0, -2.95], 0.35) if False else None
p.bar('Timber', [apex[0] + 0.2, 13.0, -0.6], [apex[0] + 0.2, Y8 + 0.3, -2.7], 0.3)   # back-leg brace (side view), above y 8
p.notes.append('Open lattice (Game Art Bot). Legs are vertical outside the middle channel up to y 8.2, and the A-frame converges above y 8, so no member enters the channel below 8 (the sheet A-frame legs would cross it). Left legs sit 0.05-0.1 off rock16; envelope x -3..5 is off-centre to the channel.')
P.append(p)

# ---- H3 ranger_station: envelope 10 x 18 x 10. Stilts, deck + cabin 8x6x8 at y 8, gable roof (overhang 1), cupola to 18.
a = anchor('h03', 'ranger_station'); p = Part('h03_ranger_station', 'h03', a['position'])
for sx in (-1, 1):
    for sz in (-1, 1):
        p.box('Timber', [sx*3.6, 4.0, sz*3.6], [0.5, 8.0, 0.5])
        p.bar('Timber', [sx*3.6, 0.5, sz*3.6], [sx*3.6, 6.5, -sz*3.6], 0.18) if sx > 0 else p.bar('Timber', [sx*3.6, 0.5, sz*3.6], [-sx*3.6, 6.5, sz*3.6], 0.18)
p.box('Timber', [0, 7.85, 0], [9.6, 0.3, 9.6])                     # deck
for sx in (-1, 1):                                                 # deck railing
    p.box('MintWhite', [sx*4.7, 8.5, 0], [0.12, 1.0, 9.4]); p.box('MintWhite', [0, 8.5, sx*4.7], [9.4, 1.0, 0.12])
p.box('PepRed', [0, 10.5, 0], [7.0, 5.0, 6.0])                     # cabin walls y 8..13 (cabin 8x6x8 incl. roof base)
p.box('MintWhite', [0, 13.2, 0], [7.4, 0.4, 6.4])
for z in (-3.02, 3.02):
    p.box('Window', [-1.8, 10.8, z], [1.6, 1.4, 0.04]); p.box('Window', [1.8, 10.8, z], [1.6, 1.4, 0.04])
p.box('Timber', [0, 9.6, 3.02], [1.2, 2.2, 0.04])                  # door (south)
roof = [(-5.0, 13.4), (5.0, 13.4), (0.0, 16.4)]                     # gable: x span 10 (overhang), ridge y 16.4
p.add('PepRed', [[x, y, -5.0] for x, y in roof] + [[x, y, 5.0] for x, y in roof], [(2,1,0), (3,4,5), (0,1,4,3), (1,2,5,4), (2,0,3,5)])
p.box('Timber', [0, 16.6, 0], [1.6, 0.6, 1.6])                     # cupola
p.box('Window', [0, 17.15, 0], [1.4, 0.5, 1.4])
p.add('PepRed', [[-1.0, 17.4, -1.0], [1.0, 17.4, -1.0], [1.0, 17.4, 1.0], [-1.0, 17.4, 1.0], [0, 18.0, 0]], [(3,2,1,0), (0,1,4), (1,2,4), (2,3,4), (3,0,4)])
for k in range(8):                                                 # ladder on the south side
    p.box('Timber', [4.0, 0.6 + k*0.9, 4.6], [0.9, 0.08, 0.08])
p.box('Timber', [3.6, 3.9, 4.6], [0.08, 7.8, 0.08]); p.box('Timber', [4.4, 3.9, 4.6], [0.08, 7.8, 0.08])
P.append(p)

# ---- H4 geode_wall: envelope 3 x 14 x 18. Thin slab, ragged top <= 14, cracked geode oval (6 wide x 8 tall) on the lane (+x) face.
a = anchor('h04', 'geode_wall'); p = Part('h04_geode_wall', 'h04', a['position'])
top = [(-9.0, 0), (-9.0, 11.0), (-6.5, 13.4), (-3.0, 12.6), (0.5, 12.9), (3.5, 13.9), (6.5, 13.0), (8.0, 11.5), (9.0, 9.5), (9.0, 0)]
ring = [(3.0*math.cos(2*math.pi*i/20), 6.6 + 4.0*math.sin(2*math.pi*i/20)) for i in range(20)]
# slab as two prisms around the cavity: back slab x -1.5..0.2 full outline, front shell x 0.2..1.5 full outline (cavity drawn as crystal face)
p.prism_zy('Watermelon', top, -1.5, 0.4)
p.prism_zy('CreamTaffy', top, 0.4, 0.9)
p.prism_zy('GeodeRim', ring, 0.9, 1.0)                                         # oval rim on the lane face
p.prism_zy('CrystalGlow', [(z*0.86, 6.6 + (y - 6.6)*0.86) for z, y in ring], 1.0, 1.05)
for i in range(14):                                                            # crystal points inside the oval (<= x 1.5)
    ang = 2*math.pi*i/14; r = 0.45 + 0.35*(i % 3)
    zc, yc = 1.8*math.cos(ang)*(0.4 + 0.25*(i % 3)), 6.6 + 2.6*math.sin(ang)*(0.4 + 0.25*(i % 3))
    base = [(zc + 0.25*math.cos(2*math.pi*k/5), yc + 0.25*math.sin(2*math.pi*k/5)) for k in range(5)]
    p.add('CrystalGlow', [[1.05, y, z] for z, y in base] + [[1.05 + r*0.3, yc, zc]], [(4,3,2,1,0)] + [(k, (k+1) % 5, 5) for k in range(5)])
P.append(p)

# ---- H5 echo_walls: envelope 16 x 44 x 46 (x -5..11, z -45..1). Walls on the plate OUTSIDE the pipe rails (channel polygon
# = holes.json plate_visible), 0.15 clear of rail faces, banded pink/cream, rounded lip.
a = anchor('h05', 'echo_walls'); p = Part('h05_echo_walls', 'h05', a['position']); AX, AZ = a['position'][0], a['position'][2]
ch = H['h05']['plate_visible'][0]
W = ch[:6]; E = list(reversed(ch[6:]))          # west chain (north->south), east chain (north->south)
def offset(chain, d):
    out = []
    for i in range(len(chain)):
        segs = []
        for j in (i-1, i):
            if 0 <= j < len(chain)-1:
                (x0, z0), (x1, z1) = chain[j], chain[j+1]; L = math.hypot(x1-x0, z1-z0); segs.append(((x1-x0)/L, (z1-z0)/L))
        nx = sum(-sz for sx, sz in segs); nz = sum(sx for sx, sz in segs)   # left normal of travel direction
        n = math.hypot(nx, nz); nx, nz = nx/n, nz/n
        cosh = (nx*(-segs[0][1]) + nz*segs[0][0]); k = d/max(cosh, 0.3)
        out.append((chain[i][0] + nx*k, chain[i][1] + nz*k))
    return out
def clip_x(poly, x0, keep_ge):     # Sutherland-Hodgman against x = x0
    out = []
    for i in range(len(poly)):
        A, B = poly[i], poly[(i+1) % len(poly)]
        ina, inb = (A[0] >= x0) == keep_ge, (B[0] >= x0) == keep_ge
        if ina: out.append(A)
        if ina != inb:
            t = (x0 - A[0]) / (B[0] - A[0]); out.append((x0, A[1] + t*(B[1]-A[1])))
    return out
def clip_z(poly, z0, keep_ge):
    sw = [(z, x) for x, z in poly]; r = clip_x(sw, z0, keep_ge); return [(x, z) for z, x in r]
d = 0.5 + 0.15
Wo = offset(W, -d)    # travelling south (-z), west side is +left? compute: left of (0,-1) is (-1,0)*-1 ... verified below
if Wo[0][0] > W[0][0]: Wo = offset(W, d)
Eo = offset(E, d)
if Eo[0][0] < E[0][0]: Eo = offset(E, -d)
XW, XE, ZN, ZS = -5.0 + 0.15, 10.0 - 0.15, 1.0, -37.75 + 0.25 + 0.15
west = [(XW - 2.0, ZN + 1)] + [(x, z) for x, z in Wo] + [(XW - 2.0, Wo[-1][1] - 1)]
west = clip_z(clip_z(clip_x(west, XW, True), ZN, False), ZS, True)
east = [(XE + 2.0, ZN + 1)] + [(x, z) for x, z in Eo] + [(XE + 2.0, Eo[-1][1] - 1)]
east = clip_z(clip_z(clip_x(east, XE, False), ZN, False), ZS, True)
def pieces(poly):  # split self-touching clip results into separate loops is not needed for these shapes; drop slivers
    return [poly] if len(poly) >= 3 else []
def area(poly): return 0.5*sum(poly[i][0]*poly[(i+1) % len(poly)][1] - poly[(i+1) % len(poly)][0]*poly[i][1] for i in range(len(poly)))
loops = []
for poly in (west, east):
    # break a loop where it runs along the clip line with zero width (east wall pinches at x = XE)
    cur = []; segs = []
    for q in poly:
        cur.append(q)
    loops.append(cur)
def split_pinch(poly, xline):
    # split at consecutive vertices both on xline whose midpoint is outside: handled by area sign of sub-loops
    idx = [i for i, q in enumerate(poly) if abs(q[0] - xline) < 1e-6]
    return poly, idx
final = []
for poly, xl in ((west, XW), (east, XE)):
    # remove zero-width runs along the clip line: group into sub-polygons separated by on-line vertex pairs
    on = [abs(q[0] - xl) < 1e-6 for q in poly]
    subs, cur = [], []
    n = len(poly)
    start = next((i for i in range(n) if on[i] and on[(i-1) % n]), None)
    if start is None: final.append(poly); continue
    order = [poly[(start + k) % n] for k in range(n)]; onr = [on[(start + k) % n] for k in range(n)]
    for k, q in enumerate(order):
        cur.append(q)
        if onr[k] and k > 0 and len(cur) >= 3 and onr[k-1] is False:
            subs.append(cur); cur = [q]
    if len(cur) >= 3: subs.append(cur)
    for s_ in subs:
        if abs(area(s_)) > 0.5: final.append(s_)
def dedupe_line(poly, xl):
    out = []
    n = len(poly)
    for i, q in enumerate(poly):
        a, b = poly[i-1], poly[(i+1) % n]
        if all(abs(v[0] - xl) < 1e-6 for v in (a, q, b)): continue   # interior vertex of a run along the clip line
        out.append(q)
    return out
final = [dedupe_line(q, XE if q[0][0] > 3 else XW) for q in final]
loc = lambda poly: [(x - AX, z - AZ) for x, z in poly]
for poly in final:
    lp = loc(poly)
    cx = sum(x for x, z in lp)/len(lp); cz = sum(z for x, z in lp)/len(lp)
    ins = [(cx + (x - cx)*0.0 + (x - cx)*1.0 - 0.0, z) for x, z in lp]
    for k in range(10):                                         # bands 0..40 (4-stud), alternating watermelon / cream
        p.prism_xz('Watermelon' if k % 2 == 0 else 'CreamTaffy', lp, 4.0*k, 4.0*k + 4.0)
    # rounded lip 40..44: shrink toward the centroid in two steps (stays inside the footprint)
    for (y0, y1, s_) in ((40.0, 43.0, 1.0), (43.0, 43.6, 0.93), (43.6, 44.0, 0.82)):
        p.prism_xz('CreamTaffy' if y0 < 43 else 'Watermelon', [(cx + (x - cx)*s_, cz + (z - cz)*s_) for x, z in lp], y0, y1)
p.footprints = [loc(q) for q in final]
p.notes.append('Footprint = plate area outside the pipe rails (channel from holes.json plate_visible), 0.15 clear of every rail face, inside the envelope. Wall bases sit on the plate felt (y 0) outside the reachable channel.')
P.append(p)

# ---- H6 bell_tower: envelope 3 x 9 x 3 around [-9,0,-30] -> z -31.5..-28.5; pocket_w21 occupies z -28.97..-28.47, so stay z <= -29.12.
a = anchor('h06', 'bell_tower'); p = Part('h06_bell_tower', 'h06', a['position']); AZ = a['position'][2]
z0, z1 = -31.5 - AZ, -29.12 - AZ                 # local -1.5 .. 0.88
zc = (z0 + z1)/2; dz = (z1 - z0)
for sx in (-1, 1):
    for zz in (z0 + 0.15, z1 - 0.15):
        p.box('Timber', [sx*1.3, 3.5, zz], [0.3, 7.0, 0.3])
    p.bar('MintWhite', [sx*1.3, 0.4, z0 + 0.15], [sx*1.3, 3.6, z1 - 0.15], 0.15)
for i in range(3): p.box('PepRed' if i % 2 == 0 else 'MintWhite', [0, 0.3 + 0.2*i + 0.1 - 0.1, zc], [2.9, 0.2, dz - 0.05]) if False else None
p.box('Timber', [0, 0.15, zc], [2.9, 0.3, dz - 0.02])                           # base sill
p.box('Timber', [0, 7.1, zc], [3.0, 0.2, dz])                                   # roof plate
p.add('PepRed', [[-1.5, 7.2, z0], [1.5, 7.2, z0], [1.5, 7.2, z1], [-1.5, 7.2, z1], [0, 9.0, zc]], [(3,2,1,0), (0,1,4), (1,2,4), (2,3,4), (3,0,4)])
bell = [(0.0, 6.7), (0.35, 6.6), (0.5, 6.1), (0.75, 5.0), (0.0, 5.0)]           # brass bell (lathe), hangs from the roof plate
n = 12; vs = []; fs = []
for ring in range(len(bell)):
    r, y = bell[ring]
    for k in range(n): vs.append([r*math.cos(2*math.pi*k/n), y, zc + r*math.sin(2*math.pi*k/n)])
for ring in range(len(bell)-1):
    for k in range(n): fs.append([ring*n + k, ring*n + (k+1) % n, (ring+1)*n + (k+1) % n, (ring+1)*n + k])
p.add('Brass', vs, fs); p.box('Iron', [0, 6.85, zc], [0.15, 0.3, 0.15])
p.notes.append('Footprint trimmed to z -31.5..-29.12 (2.38 deep): the 3x3 envelope overlaps pocket_w21 (z -28.97..-28.47) by 0.47; kept 0.15 clear.')
P.append(p)

out = []
for p in P:
    out.append(dict(id=p.name, hole=p.hole, anchor=p.anchor, notes=p.notes, envelope=anchor(p.hole, p.name.split('_', 1)[1])['approx_size'],
                    footprints=getattr(p, 'footprints', None), groups={m: dict(verts=v, faces=f) for m, (v, f) in p.g.items()}))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.json'), 'w'))
print([(o['id'], {m: len(g['faces']) for m, g in o['groups'].items()}) for o in out])
print('H5 loops', [len(f) for f in (P[4].footprints or [])])
for f in P[4].footprints: print([(round(x+3,2), round(z-22,2)) for x, z in f])
