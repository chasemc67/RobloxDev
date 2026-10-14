"""Stage sc9: offline plan for look7 v49fix_thin60 (LOD choice + felt / rail rules), from true mesh footprints.
Inputs: the layout, sc9_mesh_geom.py output (per-slot XZ hulls, Roblox axes from the FBX pivot) and a place inventory
(sc5_stage INV: every BasePart CFrame/size/tags).
  * instance frame (models/manifest.json rule): root = CFrame.new(pos + offset) * Angles(0, rad(yaw), 0), per-axis scale.
  * felt = every GolfSurface-tagged part (Geometry.Felt, CupPlate, the H7 island stone collider, mover decks at their
    edit pose); rails = every Geometry.Wall part. Each part's OBB is projected to XZ (convex hull of its 8 corners).
  * (a) felt: any slot hull of the piece overlaps any felt polygon in plan (SAT, touching counts as overlap).
  * (b) rail: min plan distance between any slot hull and any rail polygon < 1.0.
  * LOD: the nearest hole = the hole whose felt is nearest in plan; LOD when the plan distance from the instance pivot
    to THAT hole's tee (= hole origin) > 60 and a *_lod mesh exists. Also records min tee distance and the H1 tee distance.
  python3 tools/sc9_plan.py LAYOUT GEOM INVENTORY OUT.json
"""
import json, math, sys
LAYOUT, GEOM, INVF, OUTF = sys.argv[1:5]
OFF = (0, 0, -5000)
TEES = [(60, -4530), (100, -4590), (-95, -4670), (200, -4670), (280, -4674), (280, -4745), (340, -4850), (360, -4945),
        (330, -5110), (290, -5300), (150, -5252), (-200, -5270), (-300, -5290), (-300, -5200), (-300, -5115), (-300, -4888),
        (-345, -4768), (-420, -4764)]
LOD_DIST = 60.0
L = json.load(open(LAYOUT)); G = json.load(open(GEOM)); INV = json.load(open(INVF))


def hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3: return pts
    cr = lambda o, a, b: (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cr(hi[-2], hi[-1], p) <= 0: hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def obb_xz(p):
    c = p['cf']; x, y, z = c[0:3]; R = [c[3:6], c[6:9], c[9:12]]; s = p['size']
    pts = []
    for i in (-.5, .5):
        for j in (-.5, .5):
            for k in (-.5, .5):
                l = (i*s[0], j*s[1], k*s[2])
                pts.append((x + R[0][0]*l[0] + R[0][1]*l[1] + R[0][2]*l[2], z + R[2][0]*l[0] + R[2][1]*l[1] + R[2][2]*l[2]))
    return hull(pts)


def circle(poly):
    cx = sum(p[0] for p in poly)/len(poly); cz = sum(p[1] for p in poly)/len(poly)
    return cx, cz, max(math.hypot(p[0]-cx, p[1]-cz) for p in poly)


def overlap(A, B):
    for P in (A, B):
        for i in range(len(P)):
            a, b = P[i], P[(i+1) % len(P)]; n = (a[1]-b[1], b[0]-a[0])
            pa = [n[0]*q[0]+n[1]*q[1] for q in A]; pb = [n[0]*q[0]+n[1]*q[1] for q in B]
            if max(pa) < min(pb) or max(pb) < min(pa): return False
    return True


def pseg(p, a, b):
    dx, dz = b[0]-a[0], b[1]-a[1]; L2 = dx*dx+dz*dz
    t = 0 if L2 == 0 else max(0, min(1, ((p[0]-a[0])*dx+(p[1]-a[1])*dz)/L2))
    return math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dz)


def dist(A, B):
    if overlap(A, B): return 0.0
    return min(min(pseg(p, Q[i], Q[(i+1) % len(Q)]) for p in P for i in range(len(Q))) for P, Q in ((A, B), (B, A)))


def hole_of(path):
    seg = [s for s in path.split('.') if s.startswith('Hole')]
    return int(seg[0][4:]) if seg else None


felt, rails = [], []
for p in INV['parts']:
    if not (p['collide'] or p['query'] or p['touch'] or any(t.startswith('Golf') for t in p['tags'])): continue
    if 'GolfSurface' in p['tags']:
        poly = obb_xz(p); felt.append((p['path'], hole_of(p['path']), poly, circle(poly), p['cf'][1] + 0))
    elif p['path'].endswith('Geometry.Wall'):
        poly = obb_xz(p); rails.append((p['path'], hole_of(p['path']), poly, circle(poly)))

out = []
for i, e in enumerate(L['instances']):
    k = i + 1; sc = e.get('scale', [1, 1, 1]); yaw = math.radians(e['yaw']); co, si = math.cos(yaw), math.sin(yaw)
    px, pz = e['pos'][0] + OFF[0], e['pos'][2] + OFF[2]
    def world(lp): x, z = lp[0]*sc[0], lp[1]*sc[2]; return (px + x*co + z*si, pz - x*si + z*co)
    # nearest hole by felt plan distance (pivot point)
    best = (1e9, None)
    for f in felt:
        if f[1] is None: continue
        d = dist([(px, pz)], f[2]) if len(f[2]) >= 3 else 1e9
        if d < best[0]: best = (d, f[1])
    nh = best[1]
    tee = TEES[nh-1]; dtee = math.hypot(px - tee[0], pz - tee[1])
    dmin = min(math.hypot(px - t[0], pz - t[1]) for t in TEES); dh1 = math.hypot(px - TEES[0][0], pz - TEES[0][1])
    lod = dtee > LOD_DIST and (e['piece'] + '_lod') in G
    stem = e['piece'] + '_lod' if lod else e['piece']
    polys = [[world(q) for q in s['hull']] for s in G[stem]['slots'].values()]
    feltHits, railMin, railPart = [], 1e9, None
    for P in polys:
        cx, cz, r = circle(P)
        for f in felt:
            if math.hypot(cx-f[3][0], cz-f[3][1]) > r + f[3][2]: continue
            if overlap(P, f[2]) and f[0] + '@%d' % f[1] not in feltHits: feltHits.append(f[0] + '@%s' % f[1])
        for w in rails:
            if math.hypot(cx-w[3][0], cz-w[3][1]) > r + w[3][2] + 1.0 + railMin * 0: continue
            d = dist(P, w[2])
            if d < railMin: railMin, railPart = d, '%s@%s' % (w[0], w[1])
    out.append(dict(i=k, piece=e['piece'], stem=stem, lod=lod, pos=e['pos'], yaw=e['yaw'], scale=sc, src=e.get('src', ''),
                    nearestHole=nh, nearestHoleFeltDist=round(best[0], 3), teeDist=round(dtee, 2), minTeeDist=round(dmin, 2),
                    h1TeeDist=round(dh1, 2), felt=feltHits, railMin=round(railMin, 3) if railMin < 1e8 else None, railPart=railPart,
                    failFelt=bool(feltHits), failRail=railMin < 1.0))
json.dump({'lodDist': LOD_DIST, 'felt': len(felt), 'rails': len(rails), 'instances': out}, open(OUTF, 'w'), indent=0)
print('instances', len(out), 'felt', len(felt), 'rails', len(rails), 'lod', sum(o['lod'] for o in out),
      'failFelt', sum(o['failFelt'] for o in out), 'failRail', sum(o['failRail'] for o in out),
      'failEither', sum(o['failFelt'] or o['failRail'] for o in out))
