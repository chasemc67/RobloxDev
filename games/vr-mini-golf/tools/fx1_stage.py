"""Stage fx1 (felt seams near the cup, all three courses): stage commands for the ONE open course place.
  FX1_ROLE=lantern_grove|sugarloaf_canyon|aurora_archipelago (picks the Studio, the course root and the output dir)
  PYTHONPATH=tools python3 tools/fx1_stage.py preflight
  PYTHONPATH=tools python3 tools/fx1_stage.py inventory NAME                    (BaseParts + colour/appearance children)
  PYTHONPATH=tools python3 tools/fx1_stage.py compare A.json B.json OUT.json    (full part diff on the common keys)
  PYTHONPATH=tools python3 tools/fx1_stage.py verify A.json B.json OUT.json     (colliders + placeholders, sc12 rules)
  PYTHONPATH=tools python3 tools/fx1_stage.py scripts NAME                      (export place scripts to /tmp/fx1-<role>-NAME, diff vs exports)
  PYTHONPATH=tools python3 tools/fx1_stage.py seams NAME                        (fx1_seams.luau -> <role>-seams-NAME.json)
  PYTHONPATH=tools python3 tools/fx1_stage.py scan NAME                         (zf1_zscan.luau)
  PYTHONPATH=tools python3 tools/fx1_stage.py apply                             (CourseBuilder.ApplyVisualSeparation(course root))
  PYTHONPATH=tools python3 tools/fx1_stage.py run file.luau [out.json]          (Luau that sets _G.FX1Out, returns its length)
  PYTHONPATH=tools python3 tools/fx1_stage.py shot NAME x,y,z x,y,z             (MCP screen capture -> logs/stages/NAME.png)
"""
import base64, io, json, os, subprocess, sys
from pathlib import Path

ROLES = {
    'lantern_grove': dict(studio='91438142503824', root='Course', version=25, base='playtests/stage-lg14/inventory-reopened.json'),
    'sugarloaf_canyon': dict(studio='124440050576723', root='CourseSugarloaf', version=103, base='playtests/stage-sc12/inventory-final.json'),
    'aurora_archipelago': dict(studio='79649062523043', root='CourseAurora', version=13, base='playtests/stage-au7/inventory-final.json'),
}
ROLE = os.environ.get('FX1_ROLE', 'lantern_grove')
R = ROLES[ROLE]
os.environ.setdefault('GOLF_STUDIO', R['studio'])
import sc5_util
from sc5_util import fetch, GAME
import sc5_stage, sc12_stage

OUT = GAME / 'playtests/stage-fx1'
TOOLS = GAME / 'tools'

INV = sc5_stage.INV.replace("material=p.Material.Name,", "material=p.Material.Name,color=p.Color:ToHex(),variant=p.MaterialVariant,"
                            "union=p:IsA('PartOperation') and p.UsePartColor or nil,"
                            "kids=(function() local k={} for _,d in p:GetChildren() do if d:IsA('Decal') or d:IsA('Texture') then "
                            "table.insert(k,d.ClassName..'|'..d.Name..'|'..d.Texture..'|'..d.Face.Name..'|'..d.Transparency..'|'..d.Color3:ToHex()) "
                            "elseif d:IsA('SurfaceAppearance') then table.insert(k,'SA|'..d.ColorMap) end end table.sort(k) return k end)(),")
CMP_KEYS = ('class', 'cf', 'size', 'transparency', 'collide', 'query', 'touch', 'material', 'group', 'anchored', 'customPhysics', 'physics', 'tags')


def studio():
    from run_playtests import Studio
    s = Studio(); assert s.mode()[0] == 'Edit', 'not in Edit'
    assert s.luau('return workspace:GetAttribute("PlaceRole")') == ROLE, 'wrong place'
    return s


def rounded(v):
    if isinstance(v, float): return round(v, 4) + 0.0
    if isinstance(v, list): return [rounded(x) for x in v]
    return v


def compare(a, b, out, keys=CMP_KEYS):
    x = json.loads(Path(a).read_text()); y = json.loads(Path(b).read_text())
    def rows(d):
        m = {}
        for p in d['parts']:
            k = json.dumps({q: rounded(p.get(q)) for q in keys}, sort_keys=True)
            m.setdefault(p['path'], []).append(k)
        return m
    mx, my = rows(x), rows(y)
    only_a = sorted(set(mx) - set(my)); only_b = sorted(set(my) - set(mx))
    changed = [p for p in sorted(set(mx) & set(my)) if sorted(mx[p]) != sorted(my[p])]
    r = {'a': str(a), 'b': str(b), 'partsA': len(x['parts']), 'partsB': len(y['parts']), 'onlyA': only_a[:200], 'onlyB': only_b[:200],
         'onlyACount': len(only_a), 'onlyBCount': len(only_b), 'changedCount': len(changed),
         'changed': [{'path': p, 'a': mx[p], 'b': my[p]} for p in changed[:100]], 'identical': not (only_a or only_b or changed)}
    Path(out).write_text(json.dumps(r, indent=1) + '\n')
    print({k: v for k, v in r.items() if k.endswith('Count') or k in ('partsA', 'partsB', 'identical')})
    for p in changed[:10]: print('CHANGED', p)
    return r


def main():
    a = sys.argv[1]
    OUT.mkdir(parents=True, exist_ok=True)
    sc5_stage.OUT = OUT
    if a == 'compare':
        compare(sys.argv[2], sys.argv[3], sys.argv[4]); return
    if a == 'verify':
        sc12_stage.verify(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])); return
    if a == 'scripts':
        d = Path('/tmp/fx1-%s-%s' % (ROLE, sys.argv[2]))
        subprocess.run(['rm', '-rf', str(d)]); d.mkdir(parents=True)
        env = dict(os.environ, GOLF_EXPORT_DIR=str(d))
        subprocess.run([sys.executable, str(TOOLS / 'run_playtests.py'), 'export'], env=env, check=True, cwd=GAME)
        ref = GAME / 'exports' / ('%s-v%d' % (ROLE, R['version'])) / 'src'
        r = subprocess.run(['diff', '-rq', str(ref), str(d)], capture_output=True, text=True)
        o = {'export': str(d), 'reference': str(ref), 'identical': r.returncode == 0, 'diff': r.stdout.splitlines()}
        (OUT / ('%s-scripts-%s.json' % (ROLE, sys.argv[2]))).write_text(json.dumps(o, indent=1) + '\n')
        print(json.dumps(o, indent=1)); return
    s = studio()
    root = 'workspace.' + R['root']
    if a == 'preflight':
        raw = s.luau('''local ss=game:GetService("StudioService") local c=%s local h={}
for _,x in c:GetChildren() do if x.Name:match("^Hole%%d+$") then table.insert(h,x.Name) end end table.sort(h,function(a,b) return tonumber(a:sub(5))<tonumber(b:sub(5)) end)
local k={} for _,x in workspace:GetChildren() do table.insert(k,x.Name) end
return game.HttpService:JSONEncode({user=ss:GetUserId(),placeId=game.PlaceId,placeVersion=game.PlaceVersion,role=workspace:GetAttribute("PlaceRole"),holes=h,workspace=k})''' % root)
        (OUT / ('%s-preflight.json' % ROLE)).write_text(raw + '\n'); print(raw)
    elif a == 'inventory':
        raw = fetch(s, '_G.SC5Inv', INV); p = OUT / ('%s-inventory-%s.json' % (ROLE, sys.argv[2])); p.write_text(raw + '\n')
        r = json.loads(raw)
        print(p.name, 'parts', len(r['parts']), 'gameplay', sum(sc5_stage.gameplay(q) for q in r['parts']), 'collide', sum(q['collide'] for q in r['parts']),
              'placeholders', len(r['placeholders']), 'visible', sum(x['transparency'] < 1 for x in r['placeholders']))
    elif a == 'seams':
        code = (TOOLS / 'fx1_seams.luau').read_text().replace('__ROOT__', root)
        raw = fetch(s, '_G.FX1Seams', code); p = OUT / ('%s-seams-%s.json' % (ROLE, sys.argv[2])); p.write_text(raw + '\n')
        r = json.loads(raw); print(p.name, json.dumps(r['summary']))
    elif a == 'scan':
        raw = fetch(s, '_G.ZF1ScanJSON', (TOOLS / 'zf1_zscan.luau').read_text()); r = json.loads(raw)
        (OUT / ('%s-zscan-%s.json' % (ROLE, sys.argv[2]))).write_text(raw + '\n')
        exp = sum(1 for h in r['hits'].get('coplanarFaces', []) if h.get('reviewClass') == 'exposed-planar-candidate')
        print(r['counts']); print(r.get('reviewCounts')); print('exposed planar', exp)
    elif a == 'apply':
        raw = fetch(s, '_G.FX1Fix', 'local r=require(game.ServerStorage.CourseBuilder:Clone()).ApplyVisualSeparation(%s) '
                                    '_G.FX1Fix=game.HttpService:JSONEncode(r) return #_G.FX1Fix' % root)
        (OUT / ('%s-fixes.json' % ROLE)).write_text(raw + '\n'); r = json.loads(raw)
        print({k: len(v) if isinstance(v, list) else v for k, v in r.items()})
    elif a == 'run':
        raw = fetch(s, '_G.FX1Out', Path(sys.argv[2]).read_text().replace('__ROOT__', root))
        if len(sys.argv) > 3: Path(sys.argv[3]).write_text(raw + '\n')
        print(raw[:4000])
    elif a == 'shot':
        from PIL import Image
        pos = [float(x) for x in sys.argv[3].split(',')]; tgt = [float(x) for x in sys.argv[4].split(',')]
        r = s.m.req('tools/call', {'name': 'screen_capture', 'arguments': {'studio_id': s.id, 'capture_id': 'fx1-' + sys.argv[2],
                                                                          'camera_position': pos, 'look_at_position': tgt}})
        img = next(c for c in r['result']['content'] if c.get('type') == 'image')
        Image.open(io.BytesIO(base64.b64decode(img['data']))).save(GAME / 'logs/stages' / (sys.argv[2] + '.png'))
        print('saved', sys.argv[2])


if __name__ == '__main__':
    main()
