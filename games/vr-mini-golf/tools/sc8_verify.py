"""Stage sc8: colliders are identical to v49 except the 4 H16 sinkhole-opening felt colliders, which may differ only in
CFrame/size (every other key equal). Placeholders same.
  python3 tools/sc8_verify.py BEFORE.json AFTER.json OUT.json
"""
import json, sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from sc5_stage import gameplay, KEYS
a, b, out = sys.argv[1:4]
A = json.load(open(a)); B = json.load(open(b))
OPEN = {(-297.4, -4871.8): 'deck_e', (-302.6, -4871.8): 'deck_w', (-300.0, -4867.3): 'deck_n', (-300.0, -4874.5): 'deck_m',
        (-297.525, -4871.8): 'deck_e', (-302.475, -4871.8): 'deck_w', (-300.0, -4867.425): 'deck_n', (-300.0, -4874.375): 'deck_m'}
def opening(p):
    if p['path'] != 'Workspace.CourseSugarloaf.Hole16.Geometry.Felt' or abs(p['cf'][1] - 189.8) > 1e-3: return None
    for (x, z), k in OPEN.items():
        if abs(p['cf'][0] - x) < 1e-3 and abs(p['cf'][2] - z) < 1e-3: return k
def canon(p, keys=KEYS): return json.dumps({k: p.get(k) for k in keys}, sort_keys=True)
ga = [p for p in A['parts'] if gameplay(p)]; gb = [p for p in B['parts'] if gameplay(p)]
ra = sorted(canon(p) for p in ga if not opening(p)); rb = sorted(canon(p) for p in gb if not opening(p))
oa = {opening(p): p for p in ga if opening(p)}; ob = {opening(p): p for p in gb if opening(p)}
nongeo = [k for k in KEYS if k not in ('cf', 'size')]
pairs = {k: {'before': {'pos': oa[k]['cf'][:3], 'size': oa[k]['size']}, 'after': {'pos': ob[k]['cf'][:3], 'size': ob[k]['size']},
             'rotationSame': oa[k]['cf'][3:] == ob[k]['cf'][3:], 'otherKeysSame': canon(oa[k], nongeo) == canon(ob[k], nongeo)}
         for k in sorted(oa) if k in ob}
pa = sorted(p['path'] for p in A['placeholders']); pb = sorted(p['path'] for p in B['placeholders'])
r = {'colliders': 'same except H16 opening' if ra == rb and len(pairs) == 4 and all(v['otherKeysSame'] and v['rotationSame'] for v in pairs.values()) else 'changed',
     'gameplayA': len(ga), 'gameplayB': len(gb), 'identicalOutsideOpening': ra == rb, 'outsideOpeningCount': len(ra),
     'missingOutsideOpening': sorted(set(ra) - set(rb))[:20], 'addedOutsideOpening': sorted(set(rb) - set(ra))[:20],
     'h16Opening': pairs, 'placeholderPartsA': len(pa), 'placeholderPartsB': len(pb), 'placeholderPathsSame': pa == pb,
     'placeholderVisibleA': sum(p['transparency'] < 1 for p in A['placeholders']), 'placeholderVisibleB': sum(p['transparency'] < 1 for p in B['placeholders']),
     'partsA': len(A['parts']), 'partsB': len(B['parts']), 'a': a.split('/')[-1], 'b': b.split('/')[-1]}
json.dump(r, open(out, 'w'), indent=1)
print(json.dumps({k: v for k, v in r.items() if k not in ('h16Opening',)}))
for k, v in pairs.items(): print(k, v)
