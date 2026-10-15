"""Stage sc11 item 3: placeholder inventory + decal mapping -> playtests/stage-sc11/placeholders.json.
Inputs: placeholders-raw.json (sc11_place.py placeholders), /tmp/sc11/decornotes.json (each HoleN.Decor item's Anchor Notes and
every Decal/Texture under it), decal-asset-match.json (uploaded image vs local PNG, pixel sampled).
  python3 tools/sc11_placeholders.py
"""
import json, collections
from pathlib import Path

G = Path(__file__).resolve().parents[1] / 'playtests/stage-sc11'
DEC = Path('/Users/chase-mini/src/RobloxDev/assets/vr-mini-golf/sugarloaf-canyon/decals')
# PNGs outside manifest.json, by the Decor item they were made for (sc5 / al2 placements)
EXTRA = {'sign_bypass': 'h09_sign_bypass.png', 'felt_arrow_bypass': 'h09_felt_arrow_bypass.png', 'safe_bank_sign': 'h14_safe_bank_sign.png',
         'safe_bank_arrow': 'h14_safe_bank_arrow.png', 'timing_arrow': 'h14_timing_arrow.png', 'plank_respawn_stone': 'plank_respawn_stone_decal.png',
         'player_tp_bridge1_entry': 'h07_teleport_pad_decal.png', 'player_tp_bridge1_island': 'h07_teleport_pad_decal.png',
         'player_tp_bridge2_island': 'h07_teleport_pad_decal.png', 'player_tp_bridge2_exit': 'h07_teleport_pad_exit_decal.png'}

raw = json.loads((G / 'placeholders-raw.json').read_text()); N = json.load(open('/tmp/sc11/decornotes.json'))
match = json.loads((G / 'decal-asset-match.json').read_text()); byasset = {v['asset']: f for f, v in match.items()}
man = json.loads((DEC / 'manifest.json').read_text())['decals']
rows = []
for x in raw:
    if x.get('container'): continue
    p = x['path'].replace('Workspace.CourseSugarloaf.', '').split('.'); hole, item = p[0], p[2]
    n = N.get(hole + '.' + item, {}); attrs = x['attrs'] if isinstance(x['attrs'], dict) else {}
    want = (man.get(item) or {}).get('file') or EXTRA.get(item)
    decs = n.get('decals', [])
    applied = [{'file': byasset.get(d['tex']), 'tex': d['tex'], 'face': d['face'], 'on': d['path'].replace('Workspace.CourseSugarloaf.', '')} for d in decs]
    on_this = [d['face'] for d in decs if d['path'].startswith(x['path'] + '.')]
    status = ('no decal in the folder for this item' if not want else
              'already applied (asset pixel-identical to the PNG)' if any(a['file'] == want for a in applied) else 'mapped, NOT applied')
    rows.append({'name': item, 'part': x['name'], 'path': x['path'], 'hole': x['hole'], 'visible': x['visible'], 'transparency': x['transparency'],
                 'size': [round(s, 3) for s in x['size']], 'material': x['material'], 'collide': x['collide'], 'represents': n.get('notes'),
                 'decalFile': want, 'decalStatus': status, 'decalsOnItem': applied, 'decalFacesOnThisPart': on_this,
                 'replacedBy': attrs.get('SC5ReplacedBy')})
vis = [r for r in rows if r['visible']]
out = {'method': 'every BasePart under Workspace.CourseSugarloaf with an ancestor named Placeholder, or "placeholder" in its name, tags or '
                  'attribute names (175 parts, all via a Placeholder ancestor; 0 extra by name/tag/attribute)',
       'total': len(rows), 'visible': len(vis), 'decalFolder': 'assets/vr-mini-golf/sugarloaf-canyon/decals (29 in manifest.json + 8 other PNGs)',
       'newDecalsApplied': 0, 'newUploads': 0,
       'visibleSummary': collections.Counter(r['decalStatus'] for r in vis), 'allSummary': collections.Counter(r['decalStatus'] for r in rows),
       'rows': rows}
(G / 'placeholders.json').write_text(json.dumps(out, indent=1) + '\n')
print(out['total'], out['visible'], dict(out['visibleSummary']), dict(out['allSummary']))
for r in vis:
    print(r['hole'], r['name'], r['part'], r['size'], r['decalFile'], r['decalStatus'], r['decalFacesOnThisPart'], (r['represents'] or '')[:70])
