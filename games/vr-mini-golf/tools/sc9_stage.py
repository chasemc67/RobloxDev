"""Stage sc9 (Sugarloaf Canyon) evidence helpers: the sc5_stage commands, writing to playtests/stage-sc9.
  PYTHONPATH=tools python3 tools/sc9_stage.py inventory before|after|<name>
  PYTHONPATH=tools python3 tools/sc9_stage.py scan before|after
  PYTHONPATH=tools python3 tools/sc9_stage.py verify [before after]   (colliders + placeholders)
  PYTHONPATH=tools python3 tools/sc9_stage.py apply                   (CourseBuilder.ApplyVisualSeparation)
  PYTHONPATH=tools python3 tools/sc9_stage.py shot NAME x,y,z x,y,z
"""
import json, sys
import sc5_util, sc5_stage
from sc5_stage import canon

OUT = sc5_util.GAME / 'playtests/stage-sc9'
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


VIEWS = [('H1 tee', (60, 26, -4478), (40, 18, -4540)),
         ('H1 tee wide', (70, 60, -4440), (0, 15, -4600)),
         ('H13 trench', (-262, 172, -5178), (-299, 150, -5178)),
         ('West cliff wall', (-80, 60, -4700), (-140, 20, -4700))]


def views(tag):
    import base64, io
    from PIL import Image, ImageDraw
    s = sc5_util.studio(); tiles = []
    for i, (label, pos, tgt) in enumerate(VIEWS):
        r = s.m.req('tools/call', {'name': 'screen_capture', 'arguments': {'studio_id': s.id, 'capture_id': 'sc9-%s-%d' % (tag, i),
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
    grid.save(sc5_util.GAME / 'logs/stages' / ('sc9-' + tag + '.png')); print('saved sc9-' + tag)


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
