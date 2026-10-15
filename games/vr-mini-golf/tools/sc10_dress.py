"""Stage sc10: Look7Dressing rules on the LIVE place (true mesh footprints from sc9_mesh_geom.py, live Model pivots).
  (a) felt: any slot hull overlaps the plan polygon of any GolfSurface part (SAT, touching counts)            -> 0 allowed
  (b) rail: min plan distance from any slot hull to any Geometry.Wall polygon < 1.0                            -> 0 allowed
  (c) float: contact ring (stem's lowest vertices) rayed down from lowest + 5 onto Terrain + visible non-dressing
      parts; the piece floats when EVERY ring point is > 0.1 above its ground (no hit = floating)              -> 0 allowed
  PYTHONPATH=tools python3 tools/sc10_dress.py check NAME              (live check -> playtests/stage-sc10/NAME.json)
  PYTHONPATH=tools python3 tools/sc10_dress.py trench                  (item 4: analyse + plan -> trench-plan.json)
  PYTHONPATH=tools python3 tools/sc10_dress.py rail                    (item 5: analyse + plan -> rail-plan.json)
Seat rule (items 4/5): keep rotation, translate vertically so the lowest point is 0.05 below the HIGHEST ground under the
contact ring (so at least one ring point is 0.05 into the ground and none floats > 0.1).
"""
import json, math, sys
from pathlib import Path
import sc10_place as P
from sc5_util import studio, fetch, GAME

OUT = GAME / 'playtests/stage-sc10'
SINK = 0.05


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
    c = p['cf']; x, y, z = c[0:3]; R = [c[3:6], c[6:9], c[9:12]]; s = p['size']; pts = []
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
    for Q in (A, B):
        for i in range(len(Q)):
            a, b = Q[i], Q[(i+1) % len(Q)]; n = (a[1]-b[1], b[0]-a[0])
            pa = [n[0]*q[0]+n[1]*q[1] for q in A]; pb = [n[0]*q[0]+n[1]*q[1] for q in B]
            if max(pa) < min(pb) or max(pb) < min(pa): return False
    return True


def pseg(p, a, b):
    dx, dz = b[0]-a[0], b[1]-a[1]; L2 = dx*dx+dz*dz
    t = 0 if L2 == 0 else max(0, min(1, ((p[0]-a[0])*dx+(p[1]-a[1])*dz)/L2))
    q = (a[0]+t*dx, a[1]+t*dz)
    return math.hypot(p[0]-q[0], p[1]-q[1]), q


def dist(A, B):
    """plan distance between convex polygons, and the closest pair (point on A, point on B)."""
    if overlap(A, B): return 0.0, None
    best = (1e9, None)
    for p in A:
        for i in range(len(B)):
            d, q = pseg(p, B[i], B[(i+1) % len(B)])
            if d < best[0]: best = (d, (p, q))
    for p in B:
        for i in range(len(A)):
            d, q = pseg(p, A[i], A[(i+1) % len(A)])
            if d < best[0]: best = (d, (q, p))
    return best


def hole_of(path):
    seg = [s for s in path.split('.') if s.startswith('Hole')]
    return int(seg[0][4:]) if seg else None


def colliders(inv):
    felt, rails = [], []
    for p in inv['parts']:
        if not (p['collide'] or p['query'] or p['touch'] or any(t.startswith('Golf') for t in p['tags'])): continue
        if 'GolfSurface' in p['tags']:
            poly = obb_xz(p); felt.append((p['path'], hole_of(p['path']), poly, circle(poly)))
        elif p['path'].endswith('Geometry.Wall'):
            poly = obb_xz(p); rails.append((p['path'], hole_of(p['path']), poly, circle(poly)))
    return felt, rails


class World:
    def __init__(self, s, inv_name):
        self.s = s; self.G = P.geom(); self.sc = P.scales()
        self.inv = json.loads((OUT / (inv_name + '.json')).read_text())
        self.felt, self.rails = colliders(self.inv)
        self.live = json.loads(fetch(s, '_G.SC5Out', P.LOOK7, timeout=600))

    def piece(self, i, d=(0, 0, 0)):
        pc = dict(self.live[str(i)]); pc['pivot'] = [pc['pivot'][k] + d[k] for k in range(3)]
        return pc

    def fp(self, pc, i):
        return P.footprint(pc, self.sc[int(i)], self.G)

    def felt_hits(self, hulls):
        out = []
        for H in hulls:
            cx, cz, r = circle(H)
            for f in self.felt:
                if math.hypot(cx-f[3][0], cz-f[3][1]) > r + f[3][2]: continue
                if overlap(H, f[2]) and f[0] not in out: out.append(f[0])
        return out

    def rail_min(self, hulls, exclude=None):
        best = (1e9, None, None)
        for H in hulls:
            cx, cz, r = circle(H)
            for k, w in enumerate(self.rails):
                if exclude is not None and k == exclude: continue
                if math.hypot(cx-w[3][0], cz-w[3][1]) > r + w[3][2] + 2.0: continue
                d, pair = dist(H, w[2])
                if d < best[0]: best = (d, k, pair)
        return best

    def ground(self, pts_by_id):
        q = [{'id': k, 'pts': v} for k, v in pts_by_id.items()]
        return P.ground(self.s, q) if q else {}


def gaps(lo, ring_hits):
    """per ring point: lowest - ground (False = no hit)."""
    return [(lo - h[0]) if h else False for h in ring_hits]


def check(W, name):
    rows = []; q = {}
    fps = {}
    for i, pc in W.live.items():
        hulls, lo, hi, ring = W.fp(pc, i); fps[i] = (hulls, lo, hi, ring)
        q[i] = [[x, lo + 5, z] for x, y, z in ring]
    G = W.ground(q)
    for i, pc in W.live.items():
        hulls, lo, hi, ring = fps[i]
        felt = W.felt_hits(hulls); rm, rk, _ = W.rail_min(hulls)
        g = gaps(lo, G[i]); fin = [x for x in g if x is not False]
        gap = min(fin) if fin else None
        rows.append({'i': int(i), 'name': pc['name'], 'stem': pc['stem'], 'pivot': pc['pivot'], 'lowY': lo, 'highY': hi,
                     'felt': felt, 'railMin': round(rm, 3) if rm < 1e8 else None, 'rail': W.rails[rk][0] + '@%d' % W.rails[rk][1] if rk is not None else None,
                     'gap': gap, 'hits': len(fin), 'ring': len(g),
                     'ground': sorted({h[1] for h in G[i] if h}),
                     'failFelt': bool(felt), 'failRail': rm < 1.0, 'failFloat': gap is None or gap > 0.1})
    r = {'pieces': len(rows), 'felt': sum(x['failFelt'] for x in rows), 'railUnder1': sum(x['failRail'] for x in rows),
         'floatOver0.1': sum(x['failFloat'] for x in rows), 'feltPolys': len(W.felt), 'railPolys': len(W.rails),
         'minRail': min(x['railMin'] for x in rows if x['railMin'] is not None), 'rows': rows}
    (OUT / (name + '.json')).write_text(json.dumps(r) + '\n')
    print({k: v for k, v in r.items() if k != 'rows'})
    return r


def seat(W, i, d, keep_rail=None):
    """translate piece i horizontally by d=(dx,dz), then seat. Returns dict with dy, ground info and rule results."""
    pc = W.piece(i, (d[0], 0, d[1]))
    hulls, lo, hi, ring = W.fp(pc, i)
    hits = W.ground({str(i): [[x, lo + 5, z] for x, y, z in ring]})[str(i)]
    if not any(hits):  # nothing under the ring within 205: try from far above (piece may be buried / far above)
        hits = W.ground({str(i): [[x, lo + 40, z] for x, y, z in ring]})[str(i)]
    fin = [h for h in hits if h]
    res = {'i': int(i), 'name': pc['name'], 'd': d, 'lowBefore': lo}
    if not fin:
        res.update(ok=False, reason='no ground under the contact ring'); return res
    gtop = max(h[0] for h in fin); drop = lo - (gtop - SINK)
    res.update(groundTop=gtop, groundParts=sorted({h[1] for h in fin}), groundOnFelt=any(h[2] for h in fin), dy=-drop, drop=drop)
    pc2 = W.piece(i, (d[0], -drop, d[1])); hulls2, lo2, hi2, ring2 = W.fp(pc2, i)
    felt = W.felt_hits(hulls2); rm, rk, _ = W.rail_min(hulls2)
    hits2 = W.ground({str(i): [[x, lo2 + 5, z] for x, y, z in ring2]})[str(i)]
    g = [x for x in gaps(lo2, hits2) if x is not False]; gap = min(g) if g else None
    res.update(lowAfter=lo2, highAfter=hi2, felt=felt, railMin=rm, rail=W.rails[rk][0] if rk is not None else None, gapAfter=gap,
               failFelt=bool(felt) or res['groundOnFelt'], failRail=rm < 1.0, failFloat=gap is None or gap > 0.1)
    res['ok'] = not (res['failFelt'] or res['failRail'] or res['failFloat'])
    return res


if __name__ == '__main__':
    a = sys.argv[1]
    s = studio()
    if a == 'check':
        W = World(s, sys.argv[3] if len(sys.argv) > 3 else 'inventory-before'); check(W, sys.argv[2])


def band_pieces(W, y0=110, y1=122):
    out = []
    for i, pc in W.live.items():
        hulls, lo, hi, ring = W.fp(pc, i)
        if hi >= y0 and lo <= y1: out.append((i, pc, hulls, lo, hi, ring))
    return out


def trench_scan(W, true=False):
    """ground under every footprint point (hull vertices + contact ring) of every piece with any point at y 110-122."""
    B = band_pieces(W); q = {}
    for i, pc, hulls, lo, hi, ring in B:
        q[i] = [[x, lo + 5, z] for H in hulls for x, z in H] + [[x, lo + 5, z] for x, y, z in ring]
    G = (P.trueground(s, [{'id': k, 'pts': v} for k, v in q.items()]) if true else W.ground(q))
    rows = []
    for i, pc, hulls, lo, hi, ring in B:
        h = G[i]; nh = sum(len(H) for H in hulls)
        hull_d = [lo - x[0] if x else None for x in h[:nh]]; ring_d = [lo - x[0] if x else None for x in h[nh:]]
        rows.append({'i': int(i), 'name': pc['name'], 'stem': pc['stem'], 'pivot': pc['pivot'], 'lowY': lo, 'highY': hi,
                     'hullDrop': hull_d, 'ringDrop': ring_d, 'ground': sorted({x[1] for x in h if x}),
                     'maxDrop': max([d for d in hull_d + ring_d if d is not None], default=None),
                     'ringMinGap': min([d for d in ring_d if d is not None], default=None),
                     'misses': sum(x is None for x in hull_d + ring_d)})
    return rows


if __name__ == '__main__' and sys.argv[1] in ('trenchscan', 'trenchscantrue'):
    W = World(s, 'inventory-before')
    rows = trench_scan(W, sys.argv[1] == 'trenchscantrue')
    name = 'trench-scan' + ('-true' if sys.argv[1] == 'trenchscantrue' else '')
    (OUT / (name + '.json')).write_text(json.dumps(rows) + '\n')
    import collections
    print('band pieces', len(rows))
    print('maxDrop bins', collections.Counter(('miss' if r['maxDrop'] is None else '>10' if r['maxDrop'] > 10 else '2-10' if r['maxDrop'] > 2 else '0.5-2' if r['maxDrop'] > 0.5 else '0.1-0.5' if r['maxDrop'] > 0.1 else '<=0.1') for r in rows))
    for r in sorted(rows, key=lambda r: -(r['maxDrop'] if r['maxDrop'] is not None else 999))[:40]:
        print(r['i'], r['name'], [round(x, 1) for x in r['pivot']], 'lo %.2f' % r['lowY'], 'maxDrop', r['maxDrop'] and round(r['maxDrop'], 2), 'ringGap', r['ringMinGap'] and round(r['ringMinGap'], 2), 'miss', r['misses'], [g.split('.')[-1] for g in r['ground']][:4])
