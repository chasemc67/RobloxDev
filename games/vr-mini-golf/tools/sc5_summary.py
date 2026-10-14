"""Stage sc5: merge the import / placeholder / decal reports into playtests/stage-sc5/imported.json."""
import collections, json
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / 'playtests/stage-sc5'
src = json.load(open('/tmp/sc5/sources2.json'))
skipped = json.load(open('/tmp/sc5/sources.json'))['skipped']
rep = {'bundles': {}, 'replaced': [], 'placeholders': None, 'decals': None}
for b in ('sc5_A', 'sc5_B1', 'sc5_B2'):
    p = OUT / ('import-%s.json' % b)
    if not p.exists():
        continue
    r = json.loads(p.read_text())
    rep['bundles'][b] = {k: r[k] for k in ('newParts', 'oldPartsRemoved', 'importCheck', 'lightsMoved', 'weldsRetargeted')}
    rep['bundles'][b]['copies'] = len(r['copies'])
    for c in r['copies']:
        rep['replaced'].append({k: c.get(k) for k in ('path', 'old', 'oldParts', 'newParts', 'scale', 'spread', 'frameFrom', 'boundsFbx')} | {'bundle': b})
rep['placeholders'] = json.loads((OUT / 'placeholders.json').read_text())
rep['decals'] = json.loads((OUT / 'decals.json').read_text())
groups = collections.Counter(s['group'] for s in src)
rep['sources'] = {'fix_zfight (props + cacti groups)': groups['A'], 'fix_zfight3 tiles': groups['D'] + groups['E'],
                  'fix_zfight4/6/2 + placeholders_ph1': groups['C'],
                  'files': [{'stem': s['stem'], 'fbx': s['fbx'], 'sha256': s['sha_actual'], 'replaces': s['replaces']} for s in src]}
rep['notImported'] = skipped
rep['workspaceCopies'] = sum(1 for c in rep['replaced'] if c['path'].startswith('Workspace.'))
rep['libraryCopies'] = sum(1 for c in rep['replaced'] if c['path'].startswith('ServerStorage.'))
(OUT / 'imported.json').write_text(json.dumps(rep, indent=1) + '\n')
print({k: v for k, v in rep['bundles'].items()}, 'workspace', rep['workspaceCopies'], 'library', rep['libraryCopies'])
