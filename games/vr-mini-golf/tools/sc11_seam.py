"""Stage sc11 item 4: H15 dune-felt / dune_rail2 seam test (native client harness scenario `seamshots`, GolfTest.luau).
Fixed manifest (seed 20261014), built from the live rail2 collider frame (playtests/stage-sc11/h15-colliders.json):
  across (24): start 1.0-4.0 studs in from the rail2 inner face, aimed at the rail +-60 deg off the perpendicular, 1-7 studs/s
  along  (16): start 0.25-0.7 from the face, aimed along the rail (either way) 0-15 deg toward it, 1-6 studs/s
  park    (8): start 0.3-0.8 from the face, a gentle 0.4-1.2 studs/s push straight at the rail
Half the shots sit within 4 studs (along the rail) of the reported spot (-313.7, y 146.7 -> rail2 at z -5091.5).
  PYTHONPATH=tools python3 tools/sc11_seam.py manifest
  PYTHONPATH=tools python3 tools/sc11_seam.py run NAME          (-> playtests/stage-sc11/seam-NAME.json)
"""
import json, math, random, sys, time, os
from pathlib import Path
os.environ.setdefault('GOLF_STUDIO', '124440050576723')
from run_playtests import Studio, set_edit_attrs, clear_test_attrs, wait_api, GAME_DIR

OUT = Path(GAME_DIR) / 'playtests/stage-sc11'
REPORTED = (-313.7, 146.7)


def rail2():
    r = json.loads((OUT / 'h15-colliders.json').read_text())
    p = next(x for x in r['parts'] if x.get('wall') == 'dune_rail2')
    c = p['cf']; pos = c[0:3]; X = (c[3], c[6], c[9]); Z = (c[5], c[8], c[11]); s = p['size']
    inner = (-X[0], -X[2])  # inner face normal (toward the dune centre)
    face = (pos[0] + inner[0] * s[0] / 2, pos[2] + inner[1] * s[0] / 2)
    along = (Z[0], Z[2]); half = s[2] / 2
    return face, inner, along, half, pos[1]


def manifest():
    face, inner, along, half, y = rail2()
    t0 = (REPORTED[0] - face[0]) / along[0]  # along-rail coordinate of the reported spot
    rng = random.Random(20261014)
    shots = []
    def pt(t, d): return [face[0] + along[0] * t + inner[0] * d, y + 0.5, face[1] + along[1] * t + inner[1] * d]
    def rot(v, deg):
        a = math.radians(deg); return [v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a)]
    def tpick(k): return max(-half + 1, min(half - 1, t0 + rng.uniform(-4, 4))) if k % 2 == 0 else rng.uniform(-half + 1.5, half - 1.5)
    for k in range(24):
        t = tpick(k); d = rng.uniform(1.0, 4.0)
        shots.append({'group': 'across', 'start': pt(t, d), 'dir': rot([-inner[0], -inner[1]], rng.uniform(-60, 60)), 'speed': round(rng.uniform(1, 7), 3)})
    for k in range(16):
        t = tpick(k); d = rng.uniform(0.25, 0.7); sgn = 1 if k % 2 == 0 else -1
        v = [along[0] * sgn, along[1] * sgn]; tow = rng.uniform(0, 15) * (1 if sgn > 0 else -1)
        # rotate the along vector toward the rail by `tow` degrees (sign picked so it turns into the face)
        cand = [rot(v, tow), rot(v, -tow)]
        dv = min(cand, key=lambda q: q[0] * inner[0] + q[1] * inner[1])
        shots.append({'group': 'along', 'start': pt(t, d), 'dir': dv, 'speed': round(rng.uniform(1, 6), 3)})
    for k in range(8):
        t = tpick(k); d = rng.uniform(0.3, 0.8)
        shots.append({'group': 'park', 'start': pt(t, d), 'dir': [-inner[0], -inner[1]], 'speed': round(rng.uniform(0.4, 1.2), 3)})
    A = [face[0] - along[0] * half, y, face[1] - along[1] * half]; B = [face[0] + along[0] * half, y, face[1] + along[1] * half]
    m = {'seed': 20261014, 'hole': 15, 'seamA': A, 'seamB': B, 'reportedAlongT': t0, 'railFace': face, 'innerNormal': inner, 'shots': shots}
    (OUT / 'seam-manifest.json').write_text(json.dumps(m, indent=1) + '\n')
    print('shots', len(shots), 'reported t', round(t0, 2), 'seam', [round(x, 2) for x in A], [round(x, 2) for x in B])
    return m


def run(name):
    m = json.loads((OUT / 'seam-manifest.json').read_text())
    st = Studio(); st.stop_play()
    opts = {'course': 'sugarloaf_canyon', 'hole': 15, 'seamA': m['seamA'], 'seamB': m['seamB'], 'shots': m['shots'], 'radius': 0.6}
    set_edit_attrs(st, {'GolfTestMode': True, 'SimulateVR': False, 'GolfTestOpts': json.dumps(opts)})
    try:
        st.start_play(); wait_api(st)
        assert st.api('start', 'seamshots', '') == 'started'
        t = time.monotonic()
        while json.loads(st.api('status')).get('running'):
            time.sleep(5)
            if time.monotonic() - t > 3000: raise TimeoutError('seamshots')
        n = int(st.luau("_G.SC11Seam=game.ReplicatedStorage.GolfTestAPI:Invoke('result','seamshots') return #_G.SC11Seam", 'Client'))
        raw = ''.join(st.luau('return _G.SC11Seam:sub(%d,%d)' % (i + 1, i + 45000), 'Client') for i in range(0, n, 45000))
        res = json.loads(raw)
        res['problems'] = {'server': st.problems('Server'), 'client': st.problems('Client')}
        (OUT / ('seam-%s.json' % name)).write_text(json.dumps(res, indent=1) + '\n')
        rows = res.get('rows', [])
        print(name, 'shots', res.get('shots'), 'stuck', res.get('stuck'), 'hops', sum(r.get('seamHops', 0) for r in rows),
              'outcomes', {o: sum(r.get('outcome') == o for r in rows) for o in {r.get('outcome') for r in rows}}, 'err', res.get('error'))
        for r in rows:
            if r.get('stuck') or r.get('outcome') in ('nofelt', 'placefail'): print('  ', r.get('shot'), r.get('group'), r.get('outcome'), r.get('flags'), r.get('finish'))
    finally:
        st.stop_play(); clear_test_attrs(st)


if __name__ == '__main__':
    {'manifest': lambda: manifest(), 'run': lambda: run(sys.argv[2])}[sys.argv[1]]()
