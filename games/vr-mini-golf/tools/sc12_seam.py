"""Stage sc12 item 1: H15 low-side dune wall test, 80 fixed native shots (GolfTest `seamshots`, seed 20261014).
Built from the live v79 collider frames (playtests/stage-sc11/h15-colliders.json; rail2 / lean3 / dune unchanged in v79):
  r2across (20) rail2 pocket side: start 0.6-4 studs in from the rail2 inner face (inside the rail2/lean3 pocket), aimed at
                the rail +-60 deg, 1-7 studs/s, spread over the whole 30-stud wall
  r2along  (12) 0.2-0.6 from the face, along the rail either way, 0-15 deg into it, 1-6 studs/s
  r2park    (8) 0.3-0.8 from the face, a 0.4-1.2 studs/s push straight at the rail
  corner   (12) within 3 studs of the north corner (rail2 / dune_lean3 / the 0.6 dune->tier drop), both sides of lean3,
                aimed at the apex +-45 deg, 0.5-5 studs/s
  l3across (12) lean3 dune (main) side: 0.8-4 from the lean3 face, aimed at it +-60 deg, 1-7 studs/s
  l3along   (8) 0.2-0.6 from the lean3 face, along it either way, 0.5-5 studs/s
  crawl     (8) within 1.5 studs of the sweep's lean3 crawl spot (-307.2, -5087.9), main side, any direction, 0.4-6 studs/s
Wedged = a forcedrest (seam hops that end wedged); non-rest = timeout / 20 s autoreset / stuck-3s / offsurface / crawl
(< 0.3 studs/s while moving) > 2 s anywhere.
  PYTHONPATH=tools python3 tools/sc12_seam.py manifest
  PYTHONPATH=tools python3 tools/sc12_seam.py run NAME [SHOTS] [trace]   (-> playtests/stage-sc12/seam-NAME.json; SHOTS = 1-based
                                                                       comma list for a subset, trace = per-shot 0.1 s trace)
"""
import json, math, random, sys, time, os
from pathlib import Path
os.environ.setdefault('GOLF_STUDIO', '124440050576723')
from run_playtests import Studio, set_edit_attrs, clear_test_attrs, wait_api, GAME_DIR

OUT = Path(GAME_DIR) / 'playtests/stage-sc12'
SRC = Path(GAME_DIR) / 'playtests/stage-sc11/h15-colliders.json'
CRAWL = (-307.2, -5087.9)


def frames():
    r = json.loads(SRC.read_text())
    P = {(p.get('wall') or p['path'].split('.')[-1] + ':' + str(p.get('piece'))): p for p in r['parts']}
    def F(p):
        c = p['cf']; return (c[0], c[1], c[2]), (c[3], c[6], c[9]), (c[5], c[8], c[11]), p['size']
    return F(P['dune_rail2']), F(P['dune_lean3']), F(P['Felt:dune'])


def add(a, b, k=1.0): return (a[0] + b[0] * k, a[1] + b[1] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1]
def rot(v, deg):
    a = math.radians(deg); return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))
def unit(v): m = math.hypot(*v); return (v[0] / m, v[1] / m)


def geometry():
    (rp, rX, rZ, rs), (lp, lX, lZ, ls), (dp, dX, dZ, ds) = frames()
    r_in = (-rX[0], -rX[2])                    # rail2 inner normal (toward the pocket / dune)
    r_face = add((rp[0], rp[2]), r_in, rs[0] / 2)
    r_al = (rZ[0], rZ[2]); r_half = rs[2] / 2
    l_main = (-lX[0], -lX[2])                  # lean3 normal toward the main dune (same side as rail2's inner normal)
    l_c = (lp[0], lp[2]); l_al = (lZ[0], lZ[2]); l_half = ls[2] / 2
    l_mainface = add(l_c, l_main, ls[0] / 2); l_pocketface = add(l_c, l_main, -ls[0] / 2)
    # dune north (local -z) edge
    nc = (dp[0] - dZ[0] * ds[2] / 2, dp[2] - dZ[2] * ds[2] / 2); nx = (dX[0], dX[2]); nh = ds[0] / 2
    north = [add(nc, nx, nh), add(nc, nx, -nh)]
    # apex: where the rail2 and lean3 centre lines cross
    a = (rp[0], rp[2]); b = l_c
    det = r_al[0] * (-l_al[1]) - r_al[1] * (-l_al[0])
    t = ((b[0] - a[0]) * (-l_al[1]) - (b[1] - a[1]) * (-l_al[0])) / det
    apex = add(a, r_al, t)
    return dict(r_in=r_in, r_face=r_face, r_al=r_al, r_half=r_half, y=rp[1], l_main=l_main, l_c=l_c, l_al=l_al, l_half=l_half,
                l_mainface=l_mainface, l_pocketface=l_pocketface, north=north, apex=apex)


def pocket_width(g, t):
    """distance from the rail2 inner face point at t to the lean3 pocket face, along the rail2 inner normal"""
    p = add(g['r_face'], g['r_al'], t); n = g['r_in']
    # lean3 pocket face line: l_pocketface + s*l_al ; normal l_main. solve dot(p + n*d - lpf, l_main) = 0
    den = dot(n, g['l_main'])
    d = dot((g['l_pocketface'][0] - p[0], g['l_pocketface'][1] - p[1]), g['l_main']) / den
    return d


def manifest():
    g = geometry(); rng = random.Random(20261014); shots = []
    y = g['y'] + 0.5
    def P(q, yy=None): return [round(q[0], 4), yy if yy is not None else y + 0.6, round(q[1], 4)]
    def r2pt(t, d): return add(add(g['r_face'], g['r_al'], t), g['r_in'], d)
    def l3pt(t, d): return add(add(g['l_mainface'], g['l_al'], t), g['l_main'], d)
    def tpick_r2():
        while True:
            t = rng.uniform(-g['r_half'] + 0.5, g['r_half'] - 0.5)
            if pocket_width(g, t) > 1.0: return t
    # rail2 pocket side
    for k in range(20):
        t = tpick_r2(); w = pocket_width(g, t); d = rng.uniform(0.6, min(4.0, w - 0.35))
        shots.append({'group': 'r2across', 'start': P(r2pt(t, d)), 'dir': list(rot((-g['r_in'][0], -g['r_in'][1]), rng.uniform(-60, 60))), 'speed': round(rng.uniform(1, 7), 3)})
    for k in range(12):
        t = tpick_r2(); w = pocket_width(g, t); d = rng.uniform(0.2, min(0.6, w - 0.35)); sgn = 1 if k % 2 == 0 else -1
        v = (g['r_al'][0] * sgn, g['r_al'][1] * sgn); tow = rng.uniform(0, 15)
        dv = min([rot(v, tow), rot(v, -tow)], key=lambda q: dot(q, g['r_in']))
        shots.append({'group': 'r2along', 'start': P(r2pt(t, d)), 'dir': list(dv), 'speed': round(rng.uniform(1, 6), 3)})
    for k in range(8):
        t = tpick_r2(); w = pocket_width(g, t); d = rng.uniform(0.3, min(0.8, w - 0.35))
        shots.append({'group': 'r2park', 'start': P(r2pt(t, d)), 'dir': [-g['r_in'][0], -g['r_in'][1]], 'speed': round(rng.uniform(0.4, 1.2), 3)})
    # north corner: points within 3 studs of the apex, south of the north edge (on dune felt), either side of lean3
    ap = g['apex']; ne = g['north']; nn = unit((-(ne[1][1] - ne[0][1]), ne[1][0] - ne[0][0]))
    if dot((g['l_c'][0] - ne[0][0], g['l_c'][1] - ne[0][1]), nn) < 0: nn = (-nn[0], -nn[1])   # normal into the dune
    k = 0
    while k < 12:
        q = add(ap, (rng.uniform(-3, 3), rng.uniform(-3, 3)))
        if math.dist(q, ap) > 3 or dot((q[0] - ne[0][0], q[1] - ne[0][1]), nn) < 0.3: continue
        # keep off the wall bodies (>= 0.35 from rail2 inner face plane / lean3 centre line +- 0.25)
        dr = dot((q[0] - g['r_face'][0], q[1] - g['r_face'][1]), g['r_in'])
        dl = abs(dot((q[0] - g['l_c'][0], q[1] - g['l_c'][1]), g['l_main']))
        if dr < 0.35 or dl < 0.6: continue
        dv = rot(unit((ap[0] - q[0], ap[1] - q[1])), rng.uniform(-45, 45))
        shots.append({'group': 'corner', 'start': P(q, y + 1.0), 'dir': list(dv), 'speed': round(rng.uniform(0.5, 5), 3)}); k += 1
    # lean3 main side
    for k in range(12):
        t = rng.uniform(-g['l_half'] + 2.5, g['l_half'] - 1.0); d = rng.uniform(0.8, 4.0)
        shots.append({'group': 'l3across', 'start': P(l3pt(t, d), y + 1.2), 'dir': list(rot((-g['l_main'][0], -g['l_main'][1]), rng.uniform(-60, 60))), 'speed': round(rng.uniform(1, 7), 3)})
    for k in range(8):
        t = rng.uniform(-g['l_half'] + 2.5, g['l_half'] - 1.0); d = rng.uniform(0.2, 0.6); sgn = 1 if k % 2 == 0 else -1
        shots.append({'group': 'l3along', 'start': P(l3pt(t, d), y + 1.2), 'dir': [g['l_al'][0] * sgn, g['l_al'][1] * sgn], 'speed': round(rng.uniform(0.5, 5), 3)})
    k = 0
    while k < 8:
        q = add(CRAWL, (rng.uniform(-1.5, 1.5), rng.uniform(-1.5, 1.5)))
        if dot((q[0] - g['l_mainface'][0], q[1] - g['l_mainface'][1]), g['l_main']) < 0.12: continue
        a = rng.uniform(0, 360)
        shots.append({'group': 'crawl', 'start': P(q, y + 1.2), 'dir': [math.cos(math.radians(a)), math.sin(math.radians(a))], 'speed': round(rng.uniform(0.4, 6), 3)}); k += 1
    A = [*add(g['r_face'], g['r_al'], -g['r_half'])]; B = [*add(g['r_face'], g['r_al'], g['r_half'])]
    seams = [{'name': 'rail2_face', 'A': [A[0], g['y'], A[1]], 'B': [B[0], g['y'], B[1]]}]
    for nm, f in (('lean3_main', g['l_mainface']), ('lean3_pocket', g['l_pocketface'])):
        a = add(f, g['l_al'], -g['l_half']); b = add(f, g['l_al'], g['l_half'])
        seams.append({'name': nm, 'A': [a[0], g['y'], a[1]], 'B': [b[0], g['y'], b[1]]})
    seams.append({'name': 'dune_north_edge', 'A': [ne[0][0], g['y'], ne[0][1]], 'B': [ne[1][0], g['y'], ne[1][1]]})
    m = {'seed': 20261014, 'hole': 15, 'seamA': seams[0]['A'], 'seamB': seams[0]['B'], 'seams': seams, 'apex': ap,
         'pocketWidthByT': {str(t): round(pocket_width(g, t), 3) for t in range(-15, 16, 3)}, 'shots': shots}
    (OUT / 'seam-manifest.json').write_text(json.dumps(m, indent=1) + '\n')
    from collections import Counter
    print('shots', len(shots), Counter(s['group'] for s in shots), 'apex', [round(x, 3) for x in ap], 'pocket w', m['pocketWidthByT'])
    return m


def run(name, only=None, trace=False):
    m = json.loads((OUT / 'seam-manifest.json').read_text())
    st = Studio(); st.stop_play()
    shots = m['shots'] if not only else [m['shots'][i - 1] for i in only]
    opts = {'course': 'sugarloaf_canyon', 'hole': 15, 'seamA': m['seamA'], 'seamB': m['seamB'], 'seams': m['seams'], 'shots': shots, 'radius': 0.6, 'trace': trace}
    set_edit_attrs(st, {'GolfTestMode': True, 'SimulateVR': False, 'GolfTestOpts': json.dumps(opts)})
    try:
        st.start_play(); wait_api(st)
        assert st.api('start', 'seamshots', '') == 'started'
        t = time.monotonic()
        while json.loads(st.api('status')).get('running'):
            time.sleep(5)
            if time.monotonic() - t > 3600: raise TimeoutError('seamshots')
        n = int(st.luau("_G.SC12Seam=game.ReplicatedStorage.GolfTestAPI:Invoke('result','seamshots') return #_G.SC12Seam", 'Client'))
        raw = ''.join(st.luau('return _G.SC12Seam:sub(%d,%d)' % (i + 1, i + 45000), 'Client') for i in range(0, n, 45000))
        res = json.loads(raw)
        res['problems'] = {'server': st.problems('Server'), 'client': st.problems('Client')}
        (OUT / ('seam-%s.json' % name)).write_text(json.dumps(res, indent=1) + '\n')
        summary(name)
    finally:
        st.stop_play(); clear_test_attrs(st)


def summary(name):
    res = json.loads((OUT / ('seam-%s.json' % name)).read_text()); rows = res.get('rows', [])
    from collections import Counter
    by = {}
    for r in rows:
        g = by.setdefault(r.get('group'), Counter()); g['n'] += 1
        g['wedged'] += bool(r.get('wedged')); g['nonrest'] += bool(r.get('nonrest')); g['hops'] += r.get('seamHops', 0)
    print(name, 'shots', res.get('shots'), 'wedged', res.get('wedged'), 'nonrest', res.get('nonrest'), 'stuck(sc11 def)', res.get('stuck'),
          'hops', sum(r.get('seamHops', 0) for r in rows), 'outcomes', dict(Counter(r.get('outcome') for r in rows)), 'err', res.get('error'))
    print('  by group', {k: dict(v) for k, v in by.items()})
    for r in rows:
        if r.get('wedged') or r.get('nonrest') or r.get('outcome') in ('nofelt', 'placefail'):
            print('  ', r.get('shot'), r.get('group'), r.get('outcome'), r.get('flagPos') or r.get('flags'), 'crawl', r.get('crawlAnyS'), r.get('crawlPos'), 'last', r.get('lastMoving'))


if __name__ == '__main__':
    {'manifest': lambda: manifest(), 'run': lambda: run(sys.argv[2], [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 and sys.argv[3] != 'all' else None, 'trace' in sys.argv[4:]), 'summary': lambda: summary(sys.argv[2])}[sys.argv[1]]()
