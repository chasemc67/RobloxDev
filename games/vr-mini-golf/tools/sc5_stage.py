"""Stage sc5 (Sugarloaf Canyon) evidence helpers.
  PYTHONPATH=tools python3 tools/sc5_stage.py inventory before|after
  PYTHONPATH=tools python3 tools/sc5_stage.py scan before|after
  PYTHONPATH=tools python3 tools/sc5_stage.py verify            (colliders/gameplay parts + placeholders, before vs after)
  PYTHONPATH=tools python3 tools/sc5_stage.py apply             (CourseBuilder.ApplyVisualSeparation on CourseSugarloaf)
  PYTHONPATH=tools python3 tools/sc5_stage.py shot NAME x,y,z x,y,z   (MCP screen capture -> logs/stages/NAME.png)
"""
import base64, io, json, sys
from pathlib import Path
from sc5_util import studio, fetch, OUT, GAME

INV = '''local r={parts={},placeholders={}} local n=0
for _,p in workspace:GetDescendants() do if p:IsA('BasePart') then
 local v={path=p:GetFullName(),class=p.ClassName,cf={p.CFrame:GetComponents()},size={p.Size.X,p.Size.Y,p.Size.Z},transparency=p.Transparency,
  collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,material=p.Material.Name,tags=p:GetTags(),group=p.CollisionGroup,anchored=p.Anchored,
  customPhysics=p.CustomPhysicalProperties and {p.CustomPhysicalProperties.Density,p.CustomPhysicalProperties.Friction,p.CustomPhysicalProperties.Elasticity,p.CustomPhysicalProperties.FrictionWeight,p.CustomPhysicalProperties.ElasticityWeight} or false}
 if p.CanCollide or p.CanQuery or p.CanTouch then local q=p.CurrentPhysicalProperties v.physics={q.Density,q.Friction,q.Elasticity,q.FrictionWeight,q.ElasticityWeight} end
 table.insert(r.parts,v) if p:FindFirstAncestor('Placeholder') then table.insert(r.placeholders,v) end
 n+=1 if n%3000==0 then task.wait() end
end end
_G.SC5Inv=game.HttpService:JSONEncode(r) return #_G.SC5Inv'''

KEYS = ('path', 'cf', 'size', 'collide', 'query', 'touch', 'physics', 'group', 'anchored', 'customPhysics')


def gameplay(p):
    return p['collide'] or p['query'] or p['touch'] or any(t.startswith('Golf') for t in p.get('tags', []))


def canon(rows, exempt=()):
    return sorted(json.dumps({k: p.get(k) for k in KEYS}, sort_keys=True) for p in rows
                  if gameplay(p) and not any(p['path'].startswith(e) for e in exempt))


def main():
    a = sys.argv[1]
    OUT.mkdir(parents=True, exist_ok=True)
    if a == 'verify':
        b = json.loads((OUT / 'inventory-before.json').read_text()); c = json.loads((OUT / 'inventory-after.json').read_text())
        # the only allowed gameplay-flag change: the h16_sinkhole_rim visual (old copy had collide/query/touch on, if any)
        ex = ('Workspace.CourseSugarloaf.Hole16.StageAFVisuals.h16_sinkhole_rim',)
        cb, ca = canon(b['parts'], ex), canon(c['parts'], ex)
        missing = sorted(set(cb) - set(ca)); added = sorted(set(ca) - set(cb))
        ph_b = sorted(x['path'] for x in b['placeholders']); ph_a = sorted(x['path'] for x in c['placeholders'])
        r = {'colliders': 'same' if not missing and not added else 'changed',
             'gameplayPartsBefore': len(cb), 'gameplayPartsAfter': len(ca),
             'canCollideBefore': sum(p['collide'] for p in b['parts']), 'canCollideAfter': sum(p['collide'] for p in c['parts']),
             'missing': missing[:50], 'added': added[:50],
             'placeholderPartsBefore': len(ph_b), 'placeholderPartsAfter': len(ph_a),
             'placeholderVisibleBefore': sum(x['transparency'] < 1 for x in b['placeholders']),
             'placeholderVisibleAfter': sum(x['transparency'] < 1 for x in c['placeholders']),
             'placeholderPathsSame': ph_b == ph_a,
             'partsBefore': len(b['parts']), 'partsAfter': len(c['parts'])}
        (OUT / 'collider-verification.json').write_text(json.dumps(r, indent=2) + '\n')
        print(json.dumps({k: v for k, v in r.items() if k not in ('missing', 'added')}, indent=1), len(missing), len(added))
        return
    s = studio()
    if a == 'inventory':
        raw = fetch(s, '_G.SC5Inv', INV); (OUT / ('inventory-' + sys.argv[2] + '.json')).write_text(raw + '\n')
        r = json.loads(raw)
        print('parts', len(r['parts']), 'gameplay', sum(gameplay(p) for p in r['parts']), 'collide', sum(p['collide'] for p in r['parts']),
              'placeholders', len(r['placeholders']), 'visible', sum(x['transparency'] < 1 for x in r['placeholders']))
    elif a == 'scan':
        raw = fetch(s, '_G.ZF1ScanJSON', (GAME / 'tools/zf1_zscan.luau').read_text()); r = json.loads(raw)
        (OUT / ('zscan-' + sys.argv[2] + '.json')).write_text(raw + '\n')
        hits = OUT / 'model-bot-mesh-hits.json'; prior = json.loads(hits.read_text()) if hits.exists() else {}
        prior[sys.argv[2]] = r['modelBotMeshHits']; hits.write_text(json.dumps(prior) + '\n')
        exp = sum(1 for h in r['hits'].get('coplanarFaces', []) if h.get('reviewClass') == 'exposed-planar-candidate')
        print(r['counts']); print(r.get('reviewCounts')); print('exposed planar', exp)
    elif a == 'apply':
        raw = fetch(s, '_G.SC5Fix', 'local r=require(game.ServerStorage.CourseBuilder:Clone()).ApplyVisualSeparation(workspace.CourseSugarloaf) '
                                    '_G.SC5Fix=game.HttpService:JSONEncode(r) return #_G.SC5Fix')
        (OUT / 'fixes.json').write_text(raw + '\n'); r = json.loads(raw)
        print({k: len(v) if isinstance(v, list) else v for k, v in r.items()})
    elif a == 'views':
        from PIL import Image, ImageDraw
        views = [('H1 trading post deck', (66, 30, -4512), (48.4, 20, -4531)),
                 ('H7 teleport pads', (362, 82, -4872), (343, 70, -4893)),
                 ('H13-H15 ground seams', (-262, 172, -5178), (-299, 150, -5178)),
                 ('H16 sinkhole rim', (-292, 197, -4864), (-300, 189.8, -4874))]
        tiles = []
        for i, (label, pos, tgt) in enumerate(views):
            r = s.m.req('tools/call', {'name': 'screen_capture', 'arguments': {'studio_id': s.id, 'capture_id': 'sc5-%s-%d' % (sys.argv[2], i),
                                                                              'camera_position': list(pos), 'look_at_position': list(tgt)}})
            img = next(c for c in r['result']['content'] if c.get('type') == 'image')
            im = Image.open(io.BytesIO(base64.b64decode(img['data']))).convert('RGB')
            im = im.resize((960, int(960 * im.height / im.width)))
            ImageDraw.Draw(im).text((10, 10), label + ' (' + sys.argv[2] + ')', fill=(255, 255, 0))
            tiles.append(im)
        h = max(t.height for t in tiles)
        grid = Image.new('RGB', (1920, 2 * h))
        for i, t in enumerate(tiles):
            grid.paste(t, ((i % 2) * 960, (i // 2) * h))
        grid.save(GAME / 'logs/stages' / ('sc5-' + sys.argv[2] + '.png')); print('saved sc5-' + sys.argv[2])
    elif a == 'shot':
        from PIL import Image
        pos = [float(x) for x in sys.argv[3].split(',')]; tgt = [float(x) for x in sys.argv[4].split(',')]
        r = s.m.req('tools/call', {'name': 'screen_capture', 'arguments': {'studio_id': s.id, 'capture_id': 'sc5-' + sys.argv[2],
                                                                          'camera_position': pos, 'look_at_position': tgt}})
        img = next(c for c in r['result']['content'] if c.get('type') == 'image')
        Image.open(io.BytesIO(base64.b64decode(img['data']))).save(GAME / 'logs/stages' / (sys.argv[2] + '.png'))
        print('saved', sys.argv[2])


if __name__ == '__main__':
    main()
