"""Stage sc7 (Sugarloaf Canyon) evidence helpers: the sc5_stage commands, writing to playtests/stage-sc7.
  PYTHONPATH=tools python3 tools/sc7_stage.py inventory before|after|<name>
  PYTHONPATH=tools python3 tools/sc7_stage.py scan before|after
  PYTHONPATH=tools python3 tools/sc7_stage.py verify [before after]   (colliders + placeholders)
  PYTHONPATH=tools python3 tools/sc7_stage.py apply                   (CourseBuilder.ApplyVisualSeparation)
  PYTHONPATH=tools python3 tools/sc7_stage.py shot NAME x,y,z x,y,z
"""
import json, sys
import sc5_util, sc5_stage
from sc5_stage import canon

OUT = sc5_util.GAME / 'playtests/stage-sc7'
sc5_stage.OUT = OUT


def verify(a, b, out):
    x = json.loads(a.read_text()); y = json.loads(b.read_text())
    cx, cy = canon(x['parts']), canon(y['parts'])
    missing = sorted(set(cx) - set(cy)); added = sorted(set(cy) - set(cx))
    pa = sorted(p['path'] for p in x['placeholders']); pb = sorted(p['path'] for p in y['placeholders'])
    r = {'colliders': 'same' if not missing and not added else 'changed', 'gameplayPartsA': len(cx), 'gameplayPartsB': len(cy),
         'missing': missing[:50], 'added': added[:50], 'placeholderPartsA': len(pa), 'placeholderPartsB': len(pb),
         'placeholderVisibleA': sum(p['transparency'] < 1 for p in x['placeholders']),
         'placeholderVisibleB': sum(p['transparency'] < 1 for p in y['placeholders']),
         'placeholderPathsSame': pa == pb, 'partsA': len(x['parts']), 'partsB': len(y['parts']), 'a': str(a.name), 'b': str(b.name)}
    out.write_text(json.dumps(r, indent=2) + '\n')
    print(json.dumps({k: v for k, v in r.items() if k not in ('missing', 'added')}), len(missing), len(added))
    for m in missing[:5]: print('MISSING', m[:300])
    for m in added[:5]: print('ADDED', m[:300])
    return r


VIEWS = [('H2 right tunnel lanterns', (104, 30, -4600), (109, 22, -4626)),
         ('H1 tee dressing', (80, 30, -4495), (62, 18, -4520)),
         ('West cliff stack site 1 (fillers buried in terrain)', (-118, 30, -5145), (-140, 15, -5131)),
         ('H2 tunnel lanterns close (Neon)', (114, 23, -4604), (110, 22, -4625))]


def views(tag):
    import base64, io
    from PIL import Image, ImageDraw
    s = sc5_util.studio(); tiles = []
    for i, (label, pos, tgt) in enumerate(VIEWS):
        r = s.m.req('tools/call', {'name': 'screen_capture', 'arguments': {'studio_id': s.id, 'capture_id': 'sc7-%s-%d' % (tag, i),
                                                                          'camera_position': list(pos), 'look_at_position': list(tgt)}})
        img = next(c for c in r['result']['content'] if c.get('type') == 'image')
        im = Image.open(io.BytesIO(base64.b64decode(img['data']))).convert('RGB')
        im.save(OUT / ('view%d-%s.png' % (i, tag)))
        im = im.resize((960, int(960 * im.height / im.width)))
        ImageDraw.Draw(im).text((10, 10), label + ' (' + tag + ')', fill=(255, 255, 0))
        tiles.append(im)
    h = max(t.height for t in tiles)
    grid = Image.new('RGB', (1920, 2 * h))
    for i, t in enumerate(tiles):
        grid.paste(t, ((i % 2) * 960, (i // 2) * h))
    grid.save(sc5_util.GAME / 'logs/stages' / ('sc7-' + tag + '.png')); print('saved sc7-' + tag)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == 'verify':
        a = sys.argv[2] if len(sys.argv) > 2 else str(OUT / 'inventory-before.json')
        b = sys.argv[3] if len(sys.argv) > 3 else str(OUT / 'inventory-after.json')
        from pathlib import Path
        verify(Path(a), Path(b), OUT / (sys.argv[4] if len(sys.argv) > 4 else 'collider-verification.json'))
    elif sys.argv[1] == 'views':
        views(sys.argv[2])
    else:
        sc5_stage.main()
