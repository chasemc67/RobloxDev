"""Stage fx1: new z-scan coplanar hits after vs before, classified (felt-top overlap = same-normal top faces of two felt visuals)."""
import json, sys
from collections import Counter
def key(h):
    n = lambda x: x['name'] + '|' + ','.join('%.2f' % v for v in x['position'])
    return tuple(sorted([n(h['a']), n(h['b'])])) + (','.join('%.0f' % v for v in h.get('normalA', [])), h.get('reviewClass'))
b = json.load(open(sys.argv[1])); a = json.load(open(sys.argv[2]))
kb = Counter(key(h) for h in b['hits']['coplanarFaces']); ka = Counter(key(h) for h in a['hits']['coplanarFaces'])
new = [h for h in a['hits']['coplanarFaces'] if ka[key(h)] > kb.get(key(h), 0)]
gone = [h for h in b['hits']['coplanarFaces'] if kb[key(h)] > ka.get(key(h), 0)]
felt = lambda x: 'Felt' in x['name'] or 'CupPlate' in x['name']
cls = Counter()
feltTop = []
for h in new:
    nA = h.get('normalA', [0, 0, 0]); nB = h.get('normalB')
    kind = h.get('reviewClass')
    pair = ('felt' if felt(h['a']) else h['a']['name'].split('.')[-1]) + '/' + ('felt' if felt(h['b']) else h['b']['name'].split('.')[-1])
    cls[(kind, pair, 'up' if abs(nA[1]) > 0.9 else 'side')] += 1
    if felt(h['a']) and felt(h['b']) and abs(nA[1]) > 0.9 and kind != 'opposing-interface-review':
        feltTop.append(h)
out = {'new': len(new), 'gone': len(gone), 'newByClass': {' | '.join(k): v for k, v in cls.items()}, 'newFeltTopSameNormal': len(feltTop),
       'feltTopExamples': [{'a': h['a']['name'], 'b': h['b']['name'], 'class': h.get('reviewClass'), 'normalA': h.get('normalA')} for h in feltTop[:20]]}
if len(sys.argv) > 3: open(sys.argv[3], 'w').write(json.dumps(out, indent=1) + '\n')
print(json.dumps(out, indent=1))
