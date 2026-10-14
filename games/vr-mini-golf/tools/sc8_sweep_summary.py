"""Stage sc8: summarize a zf2_sweep.py results.json (cups / shots / stuck / escapes / timeouts per hole), optional compare.
  python3 tools/sc8_sweep_summary.py DIR [BEFORE_DIR OUT.json]
"""
import json, sys
from pathlib import Path


def summ(d):
    r = json.loads((Path(d) / 'results.json').read_text()); con = json.loads((Path(d) / 'console.json').read_text())
    holes = []
    for n in range(1, 19):
        h = r['h%d' % n]['default']; fz = h.get('fuzz') or {}; cd = h.get('cupdrop') or {}
        outs = [s.get('outcome') for s in fz.get('allShots', [])]
        holes.append({'hole': n, 'cups': cd.get('sunk', 0), 'cupAttempts': cd.get('n', 0), 'completedShots': fz.get('shots', 0),
                      'stuck': fz.get('stuck', 0) + h.get('stuck', 0) if isinstance(h.get('stuck'), int) else fz.get('stuck', 0),
                      'escapes': fz.get('escapes', 0), 'timeouts': fz.get('timeouts', 0), 'outcomes': outs})
    tot = {k: sum(x[k] for x in holes) for k in ('cups', 'cupAttempts', 'completedShots', 'stuck', 'escapes', 'timeouts')}
    return {'holes': holes, 'total': tot, 'console': con}


if __name__ == '__main__':
    a = summ(sys.argv[1]); (Path(sys.argv[1]) / 'summary.json').write_text(json.dumps(a, indent=1) + '\n')
    print(a['total'], 'console', {k: len(v) for k, v in a['console'].items()})
    for h in a['holes']:
        if h['cups'] < h['cupAttempts'] or h['stuck'] or h['escapes'] or h['timeouts']: print(' ', h)
    if len(sys.argv) > 3:
        b = summ(sys.argv[2]); diff = [{'hole': x['hole'], 'before': {k: y[k] for k in ('cups', 'completedShots', 'stuck', 'escapes', 'timeouts')},
                                        'after': {k: x[k] for k in ('cups', 'completedShots', 'stuck', 'escapes', 'timeouts')}}
                                       for x, y in zip(a['holes'], b['holes'])]
        out = {'seed': 20261014, 'before': b['total'], 'after': a['total'], 'consoleBefore': b['console'], 'consoleAfter': a['console'],
               'differingHoles': [d for d in diff if d['before'] != d['after']], 'holes': diff}
        Path(sys.argv[3]).write_text(json.dumps(out, indent=1) + '\n'); print('differing', out['differingHoles'])
