"""Sugarloaf batch 3: H7-H12 landmarks. Pure python -> parts.json (per part: material -> verts/faces, Roblox coords,
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

# ============ H7 rope_bridges [0,0,-42], env 8x4x32 (x -4..4, z -58..-26, y 0..4).
# Parapets (rope_rail6/7/12/13, 0.5 x 4 tall) and skirts are holes.json walls (rendered by the course build).
# Decks stay flat felt (Game Art Bot): this mesh is only rope-trim posts outside the parapets + sagging hand ropes.
a = anchor('h07', 'rope_bridges'); A = a['position']; p = Part('h07_rope_bridges', 'h07', A)
def rel(x, y, z): return [x - A[0], y - A[1], z - A[2]]
spans = [(-2.75, 2.75, -36.2, -27.0), (1.05, 6.55, -57.1, -45.9)]   # (west x, east x, north z, south z): 0.1 off parapet outer faces
for xw, xe, zn, zs in spans:
    for x in (xw, xe):
        for z in (zn, (zn+zs)/2, zs):
            p.box('Timber', rel(x, 1.8, z), [0.3, 3.6, 0.3])
            p.box('PepRed', rel(x, 3.8, z), [0.34, 0.4, 0.34])
        for ytop, sag in ((3.9, 0.3), (2.3, 0.25)):
            for z0, z1 in ((zn, (zn+zs)/2), ((zn+zs)/2, zs)):
                N = 6; pts = [[x, ytop - sag*4*t*(1-t), z0 + (z1-z0)*t] for t in [i/N for i in range(N+1)]]
                for q0, q1 in zip(pts, pts[1:]): p.bar('Rope', rel(*q0), rel(*q1), 0.12)
p.env_boxes = [[[-4, 0, -58], [4, 4, -26]], [[0.85, 0, -58], [6.75, 4, -45.7]]]
p.notes.append('Decks are the flat holes.json felt (Game Art Bot): sag is only in the visual hand ropes (0.3 / 0.25). Parapets + skirts are holes.json walls; this mesh adds rope posts 0.1 outside the parapet outer faces. Bridge 2 (x 1.3..6.3, holes.json) runs past the centred props.md envelope (x -4..4); its east posts sit at x 6.55, so the envelope is extended to x 6.75 over bridge 2 only.')
P.append(p)

# ============ H8 gumdrops: dress the two holes.json gumdrop bumpers (1.8 square boxes, yaw 22.5, top y 1.5).
# Visual stays inside each collider footprint (inset 0.03) so nothing hangs outside the collision; dome rises to <= 2.4.
a = anchor('h08', 'gumdrops'); A = a['position']; p = Part('h08_gumdrops', 'h08', A)
W8 = {w['id']: w for w in H['h08']['walls']}
def octo(h, ch):
    return [[h, -h+ch], [h, h-ch], [h-ch, h], [-h+ch, h], [-h, h-ch], [-h, -h+ch], [-h+ch, -h], [h-ch, -h]]
for wid, mat in (('gumdrop1', 'Cherry'), ('gumdrop2', 'Lime')):
    w = W8[wid]; c = w['center']; yaw = w['yaw']; base = octo(0.87, 0.22)
    def ring(sc, y): return [[c[0]-A[0]+q[0], y, c[2]-A[2]+q[2]] for q in (roty([x*sc, 0, z*sc], yaw) for x, z in base)]
    rings = [ring(1.0, 0.0), ring(1.0, 0.5), ring(1.0, 0.95)]
    for k in range(1, 6):
        t = k/6*math.pi/2; rings.append(ring(math.cos(t), 0.95 + 1.35*math.sin(t)))
    rings.append([[c[0]-A[0], 2.3, c[2]-A[2]]])
    p.loft(mat, rings)
    for k in range(6):                                     # tiny sugar crystals on the dome
        ang = math.radians(60*k + 15); r = 0.42; cx, cz = c[0]-A[0] + r*math.cos(ang), c[2]-A[2] + r*math.sin(ang); cy = 1.95
        e = 0.07; p.add('MintWhite', [[cx+e, cy, cz], [cx-e, cy, cz], [cx, cy, cz+e], [cx, cy, cz-e], [cx, cy+e*1.4, cz], [cx, cy-e, cz]],
                        [(0,2,4), (2,1,4), (1,3,4), (3,0,4), (2,0,5), (1,2,5), (3,1,5), (0,3,5)])
p.env_boxes = [[[W8[i]['center'][0]-1.2, 0, W8[i]['center'][2]-1.2], [W8[i]['center'][0]+1.2, 2.4, W8[i]['center'][2]+1.2]] for i in ('gumdrop1', 'gumdrop2')]
p.collider_ids = ['gumdrop1', 'gumdrop2']
p.notes.append('props.md envelope 2.4 cube is per gumdrop (the anchor [0,0,-50] sits between the two bumpers): applied around each holes.json gumdrop collider. Two bumpers = cherry + lime (lemon not used: only two colliders). Visual inside the collider footprint; dome above the 1.5 collider top to 2.3.')
P.append(p)

# ============ H9 pump_house: occluders x -6..-1.2 and 1.2..8, z -24..-18, y 0..8. Tunnel x -1.2..1.2 (felt pump_tunnel).
# Low rock walls (rail2/3/4, house13/14/17/18, top y 1.0) are holes.json walls: house body sits on them from y 1.1.
a = anchor('h09', 'pump_house'); A = a['position']; p = Part('h09_pump_house', 'h09', A)
zS, zN = -18.1, -23.95
p.box('Timber', rel(-3.9, 0.55, -21.0), [4.2, 1.1, 4.8])                  # west lower infill x -6..-1.8, z -23.4..-18.6
p.box('Timber', rel(4.6, 0.55, -21.0), [5.6, 1.1, 4.8])                   # east lower infill x 1.75..7.45
def roof_y(z): return 6.0 + (zS - z)/(zS - zN)*2.0 - 0.3                     # lean-to: south eave 6, north 8 (top)
def shed(x0, x1, y0):
    poly = [(zS, y0), (zN, y0), (zN, roof_y(zN)), (zS, roof_y(zS))]
    p.prism_zy('Timber', [(z - A[2], y) for z, y in poly], x0 - A[0], x1 - A[0])
shed(-6.0, -1.25, 1.1); shed(1.25, 7.95, 1.1); shed(-1.25, 1.25, 3.0)          # portal over the tunnel: lintel from y 3
p.prism_zy('PepRed', [(z - A[2], y) for z, y in [(zS, roof_y(zS)), (zN, roof_y(zN)), (zN, roof_y(zN)+0.3), (zS, roof_y(zS)+0.3)]], -6.0 - A[0], 7.95 - A[0])
for x0, x1 in ((-6.0, -1.25), (1.25, 7.95)):                                  # cream trim band + plank seams on the south face
    p.box('MintWhite', rel((x0+x1)/2, 1.25, zS + 0.02), [x1-x0, 0.3, 0.04])
p.box('MintWhite', rel(0, 3.15, zS + 0.02), [2.5, 0.3, 0.04])
for x in (-4.6, -2.6, 3.0, 6.2):                                            # windows (south face)
    p.box('Window', rel(x, 3.6, zS + 0.025), [1.2, 1.2, 0.05]); p.box('MintWhite', rel(x, 2.9, zS + 0.03), [1.5, 0.15, 0.06])
p.cyl('Brass', rel(0, 4.12, 0), 0.55, zS - A[2], -18.05 - A[2], 16, 'z')      # windpump bearing behind the hub (rotor back face -17.96)
p.env_boxes = [[[-6.0, 0, -24], [8.0, 8, -18]]]
# rev1 (Game Art Bot): candy trim along the south roof edge + candy-striped stack and a mushroom vent so it reads as a pump house from the tee.
def rtop(z): return roof_y(z) + 0.3
xs = [-6.0 + 0.5675*k for k in range(25)]
for k, (x0, x1) in enumerate(zip(xs, xs[1:])):
    p.box('MintWhite' if k % 2 == 0 else 'Bubblegum', rel((x0+x1)/2, rtop(-18.35) + 0.1, -18.36), [x1 - x0 - 0.02, 0.24, 0.5])
for i in range(4):
    p.cyl('PepRed' if i % 2 == 0 else 'MintWhite', rel(5.6, 0, -19.2), 0.35, 6.2 + 0.4125*i - A[1], 6.2 + 0.4125*(i+1) - A[1], 12, 'y')
p.cyl('Iron', rel(5.6, 0, -19.2), 0.45, 7.85 - A[1], 7.97 - A[1], 12, 'y')
p.cyl('Iron', rel(-4.0, 0, -20.0), 0.22, 6.5 - A[1], 7.3 - A[1], 10, 'y'); p.cyl('Brass', rel(-4.0, 0, -20.0), 0.38, 7.3 - A[1], 7.42 - A[1], 10, 'y')
p.notes.append('rev1: white/bubblegum candy trim blocks along the south roof eave (on the roof, z -18.11..-18.61, top <= 6.3, behind the rotor sweep), candy-striped stack r 0.35 at x 5.6 to 7.97 with iron cap, iron mushroom vent with brass cap at x -4 to 7.42; all inside the 8-tall occluder envelope.')
p.rotor = dict(center=[0, 4.12, -17.75], r=4.2, zmin=-18.04)
p.felt_exempt_kinds = ['tunnel']
p.notes.append('Built to the two holes.json occluders (x -6..8) rather than the props.md envelope (16 wide centred at x -3 -> -11..5, which would cut the east half that the anchor note and occluder put at x 1.2..8). Tunnel x -1.2..1.2 is covered (portal 3 tall): the 8-overhead rule is waived for the tunnel felt by design. Body sits on the 1.0-tall rock walls from y 1.1; lean-to roof 6 (south) -> 8 (north); bearing stops at z -18.05, behind the rotor sweep.')
P.append(p)

# ============ H10 sluice_flume [0,-1.8,-22] env 5x4x16 (x +-2.5, y -1.8..2.2, z -30..-14). Chute rails rail3/11 x +-1.5..2.0, top y 1.0.
a = anchor('h10', 'sluice_flume'); A = a['position']; p = Part('h10_sluice_flume', 'h10', A)
z0, z1 = -29.95, -14.6
for sx in (-1, 1):
    p.box('Timber', rel(sx*2.25, -0.35, (z0+z1)/2), [0.3, 2.9, z1-z0])             # casing boards x 2.1..2.4, y -1.8..1.1
    for k in range(6): p.box('Iron', rel(sx*2.36, -1.6 + 0.55*k, (z0+z1)/2), [0.02, 0.06, z1-z0]) if False else None
    p.box('Timber', rel(sx*2.025, 1.2, (z0+z1)/2), [0.85, 0.2, z1-z0])              # cap x 1.55..2.45, y 1.1..1.3 (over rail top 1.0)
    p.box('Water', rel(sx*2.0, 1.33, (z0+z1)/2), [0.5, 0.06, z1-z0])            # turquoise runnel on the cap, beside the felt
    for z in (-28.0, -24.0, -20.0, -16.0):                                       # trestle legs every 4
        p.box('Timber', rel(sx*2.42, -0.3, z), [0.16, 3.0, 0.35])
        p.bar('Timber', rel(sx*2.42, -1.7, z - 1.6), rel(sx*2.42, 0.7, z), 0.14)
    for z in (z1 - 0.25, z0 + 0.25):                                              # peppermint gate-frame posts (no lintel)
        for i in range(4): p.box('PepRed' if i % 2 == 0 else 'MintWhite', rel(sx*2.25, -1.8 + 0.25 + 0.5*i + 0.75*0, z), [0.4, 0.5, 0.4]) if False else None
        for i in range(8): p.box('PepRed' if i % 2 == 0 else 'MintWhite', rel(sx*2.27, -1.8 + 0.5*i + 0.25, z), [0.34, 0.5, 0.5])
p.notes.append('Open-top casing outside the holes.json chute rails (x +-2.1..2.45), cap over the 1.0 rail top from y 1.1; nothing spans the chute (8-overhead rule), so the top/bottom gate frames are striped posts without a lintel. Water runnel sits on the caps beside the felt. Casing ends at z -14.6 (rail2/rail12) and -29.95 (basin felt).')
P.append(p)

# ============ H11 lock_keeper_hut [9,0,-10] env 5x7x5 (x 6.5..11.5, z -12.5..-7.5). rail9 outer face x 6.5 (top 2.4).
a = anchor('h11', 'lock_keeper_hut'); A = a['position']; p = Part('h11_lock_keeper_hut', 'h11', A)
p.box('CreamTaffy', rel(9.0, 2.1, -10.0), [4.2, 4.2, 4.2])                      # body x 6.9..11.1
p.box('Timber', rel(9.0, 0.15, -10.0), [4.4, 0.3, 4.4])
gab = [(-12.4, 4.0), (-7.6, 4.0), (-7.6, 4.2), (-12.4, 4.2)]
def roofside(x0, x1):
    # sloped slab from eave (x0, y 4.0) to ridge (x1, y 6.3), along z -12.4..-7.6
    vs = [[x0, 4.0, -12.4], [x1, 6.3, -12.4], [x1, 6.3, -7.6], [x0, 4.0, -7.6]]
    vs += [[v[0], v[1] + 0.25, v[2]] for v in vs]
    p.add('PepRed', [rel(*v) for v in vs], [(0,1,2,3), (7,6,5,4), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)])
roofside(6.55, 9.0); roofside(11.45, 9.0)
for zf in (-12.1, -7.9):
    p.prism_xz if False else None
    p.add('CreamTaffy', [rel(6.9, 4.2, zf), rel(11.1, 4.2, zf), rel(9.0, 6.2, zf)], [(0, 1, 2)] if zf > -10 else [(2, 1, 0)])
p.box('Brick', rel(10.2, 6.0, -9.0), [0.6, 2.0, 0.6]); p.box('Iron', rel(10.2, 6.95, -9.0), [0.7, 0.1, 0.7])
p.box('Timber', rel(9.0, 1.2, -7.88), [1.1, 2.3, 0.06]); p.cyl('Brass', rel(9.35, 1.2, 0), 0.06, -7.85 - A[2], -7.8 - A[2], 8, 'z')
for z in (-11.0, -9.0):
    p.box('Window', rel(11.12, 2.6, z), [0.05, 0.9, 0.9])
p.cyl('Brass', rel(10.3, 1.4, 0), 0.35, -7.88 - A[2], -7.6 - A[2], 12, 'z')     # winch drum on the south face
p.box('Iron', rel(10.3, 1.4, -7.6), [0.9, 0.08, 0.12]) if False else p.bar('Iron', rel(10.3, 1.4, -7.62), rel(10.95, 1.4, -7.62), 0.08)
for i in range(8):                                                              # barber-pole gauge at the SW corner
    p.cyl('PepRed' if i % 2 == 0 else 'MintWhite', rel(7.05, 0.0, -7.75), 0.2, 0.4*i, 0.4*(i+1), 12, 'y')
p.notes.append('Gable ridge along z (front view triangle), overhang 0.35 west / 0.35 east (west eave stays at x 6.55 over rail9 outer face 6.5, 1.6 above its top). Chimney to 7.0, door + winch + barber-pole gauge on the south (tee) face.')
P.append(p)

# ============ H12 intake_tower [6,-1.2,-38] env 7x16x7 (x 2.5..9.5, y -1.2..14.8, z -41.5..-34.5). Stands in the reservoir.
a = anchor('h12', 'intake_tower'); A = a['position']; p = Part('h12_intake_tower', 'h12', A)
C = [0, 0, 0]
def r_at(y): return 3.1 - 0.35*(y/12.5)
bands = [0.0, 1.2, 2.6, 4.0, 5.4, 7.0, 8.6, 10.0, 11.4, 12.5]
for i, (y0, y1) in enumerate(zip(bands, bands[1:])):
    mat = 'Window' if (y0, y1) == (7.0, 8.6) else ('PepRed' if i % 2 == 0 else 'MintWhite')
    if mat == 'Window':                                     # window band: alternating glass / white piers
        for k in range(12):
            a0, a1 = 2*math.pi*k/12, 2*math.pi*(k+1)/12
            m2 = 'Window' if k % 2 == 0 else 'MintWhite'
            p.loft(m2, [circ(C, r_at(y0), y0, 3, a0, a1, False) + circ(C, r_at(y0)-0.15, y0, 3, a1, a0, False),
                        circ(C, r_at(y1), y1, 3, a0, a1, False) + circ(C, r_at(y1)-0.15, y1, 3, a1, a0, False)])
    else:
        p.loft(mat, [circ(C, r_at(y0), y0), circ(C, r_at(y1), y1)], cap0=(i == 0), cap1=False)
p.loft('Iron', [circ(C, 3.3, 12.5), circ(C, 3.3, 13.1), circ(C, 2.6, 13.1)], cap0=True, cap1=True)   # cap ring / cornice
dome = [circ(C, 2.6*math.cos(t), 13.1 + 1.6*math.sin(t), 24) for t in [k/5*math.pi/2 for k in range(5)]] + [[[0, 14.75, 0]]]
for s in range(8):                                                                # peppermint swirl dome (8 gores)
    a0, a1 = 2*math.pi*s/8, 2*math.pi*(s+1)/8
    rings = []
    for k in range(5):
        t = k/5*math.pi/2; tw = 0.35*k
        rings.append(circ(C, 2.6*math.cos(t), 13.1 + 1.6*math.sin(t), 3, a0 + tw, a1 + tw, False) + [[0, 13.1 + 1.6*math.sin(t), 0]])
    rings.append([[0, 14.75, 0]])
    p.loft('PepRed' if s % 2 == 0 else 'MintWhite', rings, cap0=False, cap1=False)
p.notes.append('Round tapered tower r 3.1 -> 2.75 (d 6.2 at base, inside the d7 envelope and the 6x6 occluder footprint corners aside), peppermint bands, one window band (y 7..8.6), iron cornice, low peppermint-swirl dome to 14.75 (no spire). Base at y -1.2 (anchor, under the water surface).')
P.append(p)

out = []
for p in P:
    out.append(dict(id=p.name, hole=p.hole, anchor=p.anchor, notes=p.notes, envelope=anchor(p.hole, p.name.split('_', 1)[1])['approx_size'],
                    env_boxes=getattr(p, 'env_boxes', None), collider_ids=getattr(p, 'collider_ids', None), rotor=getattr(p, 'rotor', None),
                    felt_exempt_kinds=getattr(p, 'felt_exempt_kinds', []),
                    groups={m: dict(verts=v, faces=f) for m, (v, f) in p.g.items()}))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.json'), 'w'))
print([(o['id'], sum(sum(len(f)-2 for f in g['faces']) for g in o['groups'].values())) for o in out])
