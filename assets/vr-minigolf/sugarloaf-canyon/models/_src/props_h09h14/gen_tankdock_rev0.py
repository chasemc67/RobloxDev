"""Static tank and dock; Roblox Y-up, vertices relative to holes.json anchors."""
import json, math, os
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
with (D / 'holes.json').open(encoding='utf-8') as f:
    H = {h['id']: h for h in json.load(f)['holes']}
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


def hoop(p, material, center, radius, thickness, y0, y1, axis='y'):
    # Closed annulus: outer/inner walls and two annular faces, no solid caps.
    n = 16
    rings = []
    for t, rr in ((y0, radius), (y1, radius), (y0, radius-thickness), (y1, radius-thickness)):
        ring = []
        for i in range(n):
            a = 2*math.pi*i/n
            u, v = rr*math.cos(a), rr*math.sin(a)
            ring.append([center[0]+u, t, center[2]+v] if axis == 'y'
                        else [center[0]+u, center[1]+v, t])
        rings.extend(ring)
    faces = []
    for i in range(n):
        j = (i+1)%n
        faces.extend([[i,j,n+j,n+i], [2*n+j,2*n+i,3*n+i,3*n+j],
                      [j,i,2*n+i,2*n+j], [n+i,n+j,3*n+j,3*n+i]])
    p.add(material, rings, faces)

p, A = mk('h09', 'water_tank')
p.env_boxes = [[[-13.6,0,-41.95],[-9.7,8,-38.05]]]
# Square horizontal end sections keep the splayed legs exactly above ground.
for sx in (-1,1):
    for sz in (-1,1):
        rings = []
        for y, spread in ((0.06,1.75),(3.2,1.45)):
            cx, cz = sx*spread, sz*spread
            rings.extend([[cx+dx,y,cz+dz] for dx,dz in
                          ((-.175,-.175),(.175,-.175),(.175,.175),(-.175,.175))])
        p.hexa('TimberWeathered', rings)
        p.box('Iron', [sx*1.75,.03,sz*1.75], [.39,.06,.39])
# X braces on all four faces, inset from the outer edges.
for side in (-1,1):
    for reverse in (-1,1):
        p.bar('Timber', [reverse*1.69,.65,side*1.69],
              [-reverse*1.49,2.95,side*1.49], .18)
        p.bar('Timber', [side*1.69,.65,reverse*1.69],
              [side*1.49,2.95,-reverse*1.49], .18)
for k in range(5):
    p.box('Timber', [-1.44+k*.72,3.325,0], [.69,.25,3.6])
p.loft('Timber', [circ([0,0,0],rr,y,16) for rr,y in
                      ((1.55,3.45),(1.7,5.6),(1.55,7.6))])
def tank_radius(y):
    return 1.55+.15*(y-3.45)/2.15 if y <= 5.6 else 1.7-.15*(y-5.6)/2
for y in (3.9,5.6,7.2):
    hoop(p,'Iron',[0,0,0], max(tank_radius(y-.09),tank_radius(y+.09))+.04,
         .065,y-.09,y+.09)
p.loft('TimberWeathered',[circ([0,0,0],1.75,7.6,16),circ([0,0,0],.12,7.94,16)])
p.cyl('Iron',[0,0,0],.1,7.94,8.0,12)
# The 0.6-stud outlet starts inside the barrel and points +Z.
p.cyl('Iron',[0,4,0],.12,1.15,1.75,12,'z')
p.cyl('Iron',[0,0,1.75],.12,3.6,4.0,12)
p.cyl('Brass',[0,4.17,0],.045,1.56,1.78,12,'z')
hoop(p,'Brass',[0,4.17,0],.16,.035,1.78,1.82,'z')
for angle in (0,60,120):
    a = math.radians(angle)
    p.bar('Brass',[-.14*math.cos(a),4.17-.14*math.sin(a),1.8],
          [.14*math.cos(a),4.17+.14*math.sin(a),1.8],.025)
p.notes.append('Splayed tank tower inside the specified box; nearest geometry is 0.205 studs west of rail7. Outlet points +Z and remains inside the box; roof covers the tank.')
P.append(p)

p, A = mk('h14','loading_dock'); r = p.rel
p.env_boxes = [[[-9.6,0,-35.35],[-4.65,2.6,-25.2]]]
# Deck occupies x -8.7..-4.7; outer steps use the remaining west strip.
for k in range(10):
    p.box('Timber',r(-6.7,.875,-34.85+k*.95),[4,.15,.9])
for x in (-8.35,-5.05):
    p.box('TimberWeathered',r(x,.69,-30.575),[.22,.22,9.55])
    for z in (-34.75,-30.5,-25.7):
        p.box('TimberWeathered',r(x,.4,z),[.35,.8,.35])
        p.box('Iron',r(x,.03,z),[.43,.06,.43])
        p.box('Iron',r(x,.785,z),[.39,.03,.39])
for z in (-34.85,-30.575,-26.3):
    p.box('TimberWeathered',r(-6.7,.69,z),[3.65,.22,.2])
p.box('Iron',r(-4.76,.965,-30.575),[.08,.03,9.45])
for x,y,width in ((-8.925,.6,.45),(-9.375,.3,.45)):
    p.box('Timber',r(x,y/2,-28),[width,y,1.8])
for index,(x,z) in enumerate(((-7.65,-33.8),(-6.3,-31.8),(-7.65,-29.8))):
    assert x + .65 <= -5.6, 'crate must stay away from rail'
    p.box('Timber',r(x,1.55,z),[1.2,1.2,1.2])
    for dx in (-.55,.55):
        for dz in (-.55,.55):
            p.box('TimberWeathered',r(x+dx,1.55,z+dz),[.14,1.22,.14])
            for y in (1.08,2.03):
                p.box('Iron',r(x+dx,y,z+dz),[.16,.12,.16])
    for y in (1.02,2.12):
        for dz in (-.59,.59):
            p.box('TimberWeathered',r(x,y,z+dz),[1.2,.12,.1])
        for dx in (-.59,.59):
            p.box('TimberWeathered',r(x+dx,y,z),[.1,.12,1.2])
    if index == 0:
        # Small uneven lilac ore heap rises above the crate rim.
        for dx,dz,e in ((-.27,-.22,.22),(.25,-.2,.24),(-.22,.25,.23),(.23,.22,.21),(0,0,.28)):
            p.octa('RockCandyLilac',r(x+dx,2.18,z+dz),e,1.3)
p.box('Iron',r(-6.2,1.04,-26.1),[.8,.18,.25])
p.notes.append('Dock shifted west of the ramp: at least 0.20 studs outside rail2, 0.20 south of rail3, and 1.7 south of the trestle footprint. Three crates stay west of x -5.65; lilac ore tops at 2.544.')
P.append(p)

ALLOWED = {'Timber','TimberWeathered','Iron','Brass','Rope','Water','RockCandyLilac'}
def self_check(p):
    assert set(p.g) <= ALLOWED, (p.name,'material')
    world = np.array([v for verts,faces in p.g.values() for v in verts])+np.array(p.anchor)
    inside = np.zeros(len(world),dtype=bool)
    for lo,hi in p.env_boxes:
        inside |= ((world >= np.array(lo)-1e-6)&(world <= np.array(hi)+1e-6)).all(axis=1)
    assert inside.all(), (p.name,'outside envelope',world[~inside].tolist())
    for verts,faces in p.g.values():
        assert np.isfinite(verts).all()
        for face in faces:
            assert len(face)>=3 and len(set(face))==len(face)
            assert all(0 <= i < len(verts) for i in face)
    tris = sum(len(f)-2 for v,faces in p.g.values() for f in faces)
    assert tris < 3000, (p.name,tris)
    if p.hole == 'h09':
        assert world[:,0].min() >= -13.65 and world[:,0].max() <= -9.65
    else:
        assert world[:,0].max() <= -4.65
        assert world[:,2].max() <= -25.2 and world[:,2].min() >= -35.35
    print(f'{p.name}: {tris} tris; self-checks PASS; bounds {world.min(axis=0).tolist()} .. {world.max(axis=0).tolist()}')

for p in P:
    self_check(p)
out = []
for p in P:
    out.append(dict(id=p.name, hole=p.hole, anchor=p.anchor, notes=p.notes, envelope=anchor(p.hole, p.name.split('_', 1)[1])['approx_size'],
                    env_boxes=getattr(p, 'env_boxes', None), collider_ids=getattr(p, 'collider_ids', None), rotor=getattr(p, 'rotor', None),
                    felt_exempt_kinds=getattr(p, 'felt_exempt_kinds', []), sweep_boxes=getattr(p, 'sweep_boxes', []),
                    overhead_exempt_boxes=getattr(p, 'overhead_exempt_boxes', []), unreachable_discs=getattr(p, 'unreachable_discs', []),
                    annulus=getattr(p, 'annulus', None),
                    groups={m: dict(verts=v, faces=f) for m, (v, f) in p.g.items()}))
with (D / 'parts.json').open('w',encoding='utf-8') as f:
    json.dump(out,f)
