"""Stage lg14 (Lantern Grove) evidence helpers: the sc5/sc12 stage commands for workspace.Course, writing to playtests/stage-lg14.
  PYTHONPATH=tools python3 tools/lg14_stage.py preflight
  PYTHONPATH=tools python3 tools/lg14_stage.py inventory before|after|<name>
  PYTHONPATH=tools python3 tools/lg14_stage.py scan before|after
  PYTHONPATH=tools python3 tools/lg14_stage.py verify A.json B.json OUT.json   (colliders + placeholders)
  PYTHONPATH=tools python3 tools/lg14_stage.py apply                           (CourseBuilder.ApplyVisualSeparation(workspace.Course))
  PYTHONPATH=tools python3 tools/lg14_stage.py run file.luau [out.json]        (Luau that sets _G.LG14Out, returns its length)
  PYTHONPATH=tools python3 tools/lg14_stage.py shot NAME x,y,z x,y,z           (MCP screen capture -> logs/stages/NAME.png)
  PYTHONPATH=tools python3 tools/lg14_stage.py summary DIR [BEFORE_DIR OUT.json] (zf2_sweep results, holes present only)
"""
import base64, io, json, os, sys
from pathlib import Path
os.environ.setdefault('GOLF_STUDIO', '91438142503824')
import sc5_util
from sc5_util import fetch, GAME
import sc5_stage, sc12_stage

OUT = GAME / 'playtests/stage-lg14'


def studio():
    from run_playtests import Studio
    s = Studio(); assert s.mode()[0] == 'Edit', 'not in Edit'
    assert s.luau('return workspace:GetAttribute("PlaceRole")') == 'lantern_grove'
    return s


def summ(d):
    r = json.loads((Path(d) / 'results.json').read_text()); con = json.loads((Path(d) / 'console.json').read_text())
    holes = []
    for k in sorted(r, key=lambda k: int(k[1:])):
        h = r[k]['default']; fz = h.get('fuzz') or {}; cd = h.get('cupdrop') or {}
        holes.append({'hole': int(k[1:]), 'cups': cd.get('sunk', 0), 'cupAttempts': cd.get('n', 0), 'completedShots': fz.get('shots', 0),
                      'stuck': fz.get('stuck', 0), 'escapes': fz.get('escapes', 0), 'timeouts': fz.get('timeouts', 0),
                      'outcomes': [s.get('outcome') for s in fz.get('allShots', [])]})
    tot = {k: sum(x[k] for x in holes) for k in ('cups', 'cupAttempts', 'completedShots', 'stuck', 'escapes', 'timeouts')}
    return {'holes': holes, 'total': tot, 'console': con}


def main():
    a = sys.argv[1]
    OUT.mkdir(parents=True, exist_ok=True)
    sc5_stage.OUT = OUT
    if a == 'verify':
        sc12_stage.verify(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])); return
    if a == 'summary':
        x = summ(sys.argv[2]); (Path(sys.argv[2]) / 'summary.json').write_text(json.dumps(x, indent=1) + '\n')
        print(x['total'], 'console', {k: len(v) for k, v in x['console'].items()})
        if len(sys.argv) > 4:
            y = summ(sys.argv[3]); keys = ('cups', 'completedShots', 'stuck', 'escapes', 'timeouts')
            diff = [{'hole': p['hole'], 'before': {k: q[k] for k in keys}, 'after': {k: p[k] for k in keys}} for p, q in zip(x['holes'], y['holes'])]
            o = {'seed': 20261014, 'before': y['total'], 'after': x['total'], 'consoleBefore': y['console'], 'consoleAfter': x['console'],
                 'differingHoles': [d for d in diff if d['before'] != d['after']], 'holes': diff}
            Path(sys.argv[4]).write_text(json.dumps(o, indent=1) + '\n'); print('differing', o['differingHoles'])
        return
    s = studio()
    if a == 'preflight':
        print(s.luau('''local ss=game:GetService("StudioService") local c=workspace:FindFirstChild("Course") local h={}
if c then for _,x in c:GetChildren() do if x.Name:match("^Hole%d+$") then table.insert(h,x.Name) end end end table.sort(h,function(a,b) return tonumber(a:sub(5))<tonumber(b:sub(5)) end)
return game.HttpService:JSONEncode({user=ss:GetUserId(),placeId=game.PlaceId,placeVersion=game.PlaceVersion,role=workspace:GetAttribute("PlaceRole"),holes=h})'''))
    elif a == 'inventory':
        raw = fetch(s, '_G.SC5Inv', sc5_stage.INV); (OUT / ('inventory-' + sys.argv[2] + '.json')).write_text(raw + '\n')
        r = json.loads(raw)
        print('parts', len(r['parts']), 'gameplay', sum(sc5_stage.gameplay(p) for p in r['parts']), 'collide', sum(p['collide'] for p in r['parts']),
              'placeholders', len(r['placeholders']), 'visible', sum(x['transparency'] < 1 for x in r['placeholders']))
    elif a == 'scan':
        raw = fetch(s, '_G.ZF1ScanJSON', (GAME / 'tools/zf1_zscan.luau').read_text()); r = json.loads(raw)
        (OUT / ('zscan-' + sys.argv[2] + '.json')).write_text(raw + '\n')
        exp = sum(1 for h in r['hits'].get('coplanarFaces', []) if h.get('reviewClass') == 'exposed-planar-candidate')
        print(r['counts']); print(r.get('reviewCounts')); print('exposed planar', exp)
    elif a == 'apply':
        raw = fetch(s, '_G.LG14Fix', 'local r=require(game.ServerStorage.CourseBuilder:Clone()).ApplyVisualSeparation(workspace.Course) '
                                     '_G.LG14Fix=game.HttpService:JSONEncode(r) return #_G.LG14Fix')
        (OUT / 'fixes.json').write_text(raw + '\n'); r = json.loads(raw)
        print({k: len(v) if isinstance(v, list) else v for k, v in r.items()})
    elif a == 'run':
        raw = fetch(s, '_G.LG14Out', Path(sys.argv[2]).read_text())
        if len(sys.argv) > 3: Path(sys.argv[3]).write_text(raw + '\n')
        print(raw[:4000])
    elif a == 'shot':
        from PIL import Image
        pos = [float(x) for x in sys.argv[3].split(',')]; tgt = [float(x) for x in sys.argv[4].split(',')]
        r = s.m.req('tools/call', {'name': 'screen_capture', 'arguments': {'studio_id': s.id, 'capture_id': 'lg14-' + sys.argv[2],
                                                                          'camera_position': pos, 'look_at_position': tgt}})
        img = next(c for c in r['result']['content'] if c.get('type') == 'image')
        Image.open(io.BytesIO(base64.b64decode(img['data']))).save(GAME / 'logs/stages' / (sys.argv[2] + '.png'))
        print('saved', sys.argv[2])


if __name__ == '__main__':
    main()
