"""Stage gg2 (LG hidden goose hole 19) helpers. Only talks to the Lantern Grove Studio (GOLF_STUDIO=91438142503824).
  PYTHONPATH=tools python3 tools/gg2_tool.py push              push the gg2 src files into Studio (Edit)
  PYTHONPATH=tools python3 tools/gg2_tool.py build             CourseBuilder.BuildBonus + BuildH9Secret (Edit)
  PYTHONPATH=tools python3 tools/gg2_tool.py diff A.json B.json OUT.json
        everything outside the new hole 19 / Hole9.Secret must be identical (all parts, every compared key), the
        colliders outside them too; lists the new parts and the new gameplay parts (Hole9.Secret must have none)
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault('GOLF_STUDIO', '91438142503824')
HERE = Path(__file__).resolve().parent
GAME = HERE.parent
sys.path.insert(0, str(HERE))

FILES = [
    'src/ReplicatedStorage/Golf/Courses.luau',
    'src/ServerStorage/CourseBuilder.luau',
    'src/ServerStorage/PropsBuilder.luau',
    'src/ServerStorage/VisualSeparation.luau',
    'src/ServerStorage/CourseData/LanternGroveBonus.luau',
    'src/ServerScriptService/GolfServer.server.luau',
    'src/ServerScriptService/GolfServer/GolfTestServer.luau',
    'src/StarterPlayer/StarterPlayerScripts/GolfClient/HUD.luau',
    'src/StarterPlayer/StarterPlayerScripts/GolfClient/FrontEnd.luau',
    'src/StarterPlayer/StarterPlayerScripts/GolfClient/GolfTest.luau',
]
NEW = ('Workspace.Course.Hole19', 'Workspace.Course.Hole9.Secret')


def studio():
    from run_playtests import Studio
    s = Studio()
    assert s.mode()[0] == 'Edit', 'not in Edit'
    assert s.luau('return workspace:GetAttribute("PlaceRole")') == 'lantern_grove', 'wrong place'
    return s


def is_new(path):
    return any(path == n or path.startswith(n + '.') for n in NEW)


def diff(a, b, out):
    import fx1_stage
    import sc5_stage
    x = json.loads(Path(a).read_text())
    y = json.loads(Path(b).read_text())
    keep = lambda d: {**d, 'parts': [p for p in d['parts'] if not is_new(p['path'])]}
    xa, yb = keep(x), keep(y)
    ta, tb = Path('/tmp/gg2/_a.json'), Path('/tmp/gg2/_b.json')
    ta.parent.mkdir(exist_ok=True)
    ta.write_text(json.dumps(xa))
    tb.write_text(json.dumps(yb))
    r = fx1_stage.compare(ta, tb, '/tmp/gg2/_cmp.json')
    ca, cb = sc5_stage.canon(xa['parts']), sc5_stage.canon(yb['parts'])
    new = [p for p in y['parts'] if is_new(p['path'])]
    new_gp = [p for p in new if sc5_stage.gameplay(p)]
    o = {'a': str(a), 'b': str(b), 'existingIdentical': r['identical'], 'existingChanged': r['changedCount'],
         'existingOnlyA': r['onlyACount'], 'existingOnlyB': r['onlyBCount'], 'changed': r['changed'][:20],
         'collidersExisting': 'same' if ca == cb else 'DIFF', 'collidersExistingCount': len(ca),
         'newParts': len(new), 'newGameplay': len(new_gp),
         'newGameplayByRoot': {n: sum(1 for p in new_gp if p['path'].startswith(n)) for n in NEW},
         'newCollide': sum(1 for p in new if p['collide']),
         'secretParts': sum(1 for p in new if p['path'].startswith(NEW[1]))}
    Path(out).write_text(json.dumps(o, indent=1) + '\n')
    print(json.dumps({k: v for k, v in o.items() if k != 'changed'}))
    return o


def main():
    cmd = sys.argv[1]
    if cmd == 'diff':
        diff(sys.argv[2], sys.argv[3], sys.argv[4])
        return
    s = studio()
    if cmd == 'push':
        import argparse
        from run_playtests import cmd_push
        os.chdir(GAME)
        cmd_push(argparse.Namespace(files=[str(GAME / f) for f in FILES]), s)
    elif cmd == 'build':
        print(s.luau('''local CB = require(game.ServerStorage.CourseBuilder:Clone())
local data = require(game.ServerStorage.CourseData.LanternGroveBonus:Clone())
local a = CB.BuildBonus(data)
local b = CB.BuildH9Secret(data)
return a .. " | secret " .. b''', timeout=600))


if __name__ == '__main__':
    main()
