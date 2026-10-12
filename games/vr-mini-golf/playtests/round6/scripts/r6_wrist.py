#!/usr/bin/env python3
"""Round 6: stage_r_wrist.py extended: a real VR stroke first (r5 repro), 3x MENU->Resume->SCORES, then hand switch
right->left AND left->right, wrist MENU/SCORES + Best on both wrists. Times to hover recorded (0.5 s swing guard)."""
import argparse
import json
import os
import time
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', '..', 'tools')))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'round5', 'scripts')))

from run_playtests import Studio, set_edit_attrs
from menu_shots import menu, pointer
from ui_shots import capture
from wrist_sim import LEVEL_HEAD
from r5_wrist import SWING


GEOMETRY = r"""
local pl = game.Players.LocalPlayer
local cam = workspace.CurrentCamera
local gui = pl.PlayerGui:FindFirstChild('VRWrist')
if not gui or not gui:IsA('SurfaceGui') then
  for _, g in pl.PlayerGui:GetChildren() do
    if g:IsA('SurfaceGui') and g.Adornee and (g.Adornee.Name == 'VRWrist' or g.Adornee.Name == 'WristFace') then gui = g break end
  end
end
assert(gui and gui.Adornee, 'wrist SurfaceGui missing')
local p = gui.Adornee
local top = gui.Face == Enum.NormalId.Top
local width, height = top and p.Size.Z or p.Size.X, top and p.Size.X or p.Size.Y
local texts = {}
for _, d in gui:GetDescendants() do
  if d:IsA('TextLabel') or d:IsA('TextButton') then texts[d.Name] = {text=d.Text, fits=d.TextFits} end
end
return game:GetService('HttpService'):JSONEncode({adornee=p:GetFullName(), face=gui.Face.Name,
  size={p.Size.X,p.Size.Y,p.Size.Z}, canvas={gui.CanvasSize.X,gui.CanvasSize.Y},
  partAspect=width/height, canvasAspect=gui.CanvasSize.X/gui.CanvasSize.Y, texts=texts,
  bestAttribute=pl:GetAttribute('Best_lantern_grove')})
"""

LOOK = r"""
local h = game.ReplicatedStorage.VRDebug.Head
local cam = workspace.CurrentCamera
local p = cam:FindFirstChild('VRWrist')
if not p then
  for _, g in game.Players.LocalPlayer.PlayerGui:GetChildren() do
    if g:IsA('SurfaceGui') and g.Adornee and g.Adornee.Name == 'WristFace' then p=g.Adornee break end
  end
end
assert(p, 'wrist face missing')
local origin = cam.CFrame * h.Value:Inverse()
h.Value = origin:Inverse() * CFrame.lookAt(cam.CFrame.Position, p.Position)
return 'ok'
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='playtests/round6/wrist-r6')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    st = Studio()
    st.stop_play()
    keys = ('GolfTestMode', 'SimulateVR', 'SkipMenu', 'PBInStudio')
    old = json.loads(st.luau("return game:GetService('HttpService'):JSONEncode(workspace:GetAttributes())"))
    restore = {key: old.get(key) for key in keys}
    result = {'steps': [], 'screenshots': [], 'passed': False}
    hand = 'RightHand'

    def save():
        with open(os.path.join(args.out, 'wrist-regression.json'), 'w') as fh:
            json.dump(result, fh, indent=2)

    def wait_for(fn, label, seconds=5):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            value = fn()
            if value:
                return value
            time.sleep(0.1)
        raise AssertionError(label)

    def page():
        card = st.luau("local g=game.Players.LocalPlayer.PlayerGui:FindFirstChild('VRScorecard') return g and g.Enabled or false", 'Client')
        if card in (True, 'true'):
            return 'scorecard'
        state = menu(st, 'state')
        if isinstance(state, str):
            state = json.loads(state)
        return state.get('page')

    def raise_wrist():
        info = pointer(st, 'wrist', True)
        expected_off = 'LeftHand' if hand == 'RightHand' else 'RightHand'
        assert info['hand'] == expected_off, info
        wait_for(lambda: (lambda s: s['wrist'].get('shown') and s['wrist'].get('alpha', 0) > .6)(pointer(st, 'state')), 'wrist did not appear')

    def click(name, expect, wrist=False):
        if wrist:
            raise_wrist()
        target = wait_for(lambda: next((t for t in pointer(st, 'targets') or [] if t['name'] == name), None), 'missing target ' + name)
        row = {'button': name, 'hand': hand, 'samples': [], 'expected': expect}
        result['steps'].append(row)
        pointer(st, 'aim', {'hand': hand, 'point': target['world']})
        began = time.monotonic()
        for offset in (.1, .4):
            time.sleep(max(0, offset - (time.monotonic() - began)))
            row['samples'].append({'requestedSeconds': offset, 'elapsed': time.monotonic() - began, 'state': pointer(st, 'state')})
        settled = wait_for(lambda: (lambda s: s if s['pointer'].get('button') == name else None)(pointer(st, 'state')), 'hover did not settle: ' + name)
        row['settled'] = {'elapsed': time.monotonic() - began, 'state': settled}
        pointer(st, 'trigger', hand)
        wait_for(lambda: page() == expect, 'wrong page after ' + name)
        row['page'] = page()
        row['passed'] = True
        print(json.dumps(row), flush=True)
        save()
        if wrist:
            pointer(st, 'wrist', False)
            time.sleep(.65)

    def screenshot(label):
        st.luau(LEVEL_HEAD, 'Client')
        raise_wrist()
        time.sleep(.3)
        geometry = json.loads(st.luau(GEOMETRY, 'Client'))
        state = pointer(st, 'state')
        row = {'label': label, 'geometry': geometry, 'state': state}
        result['screenshots'].append(row)
        assert state['wrist']['best'] == '-2', row
        assert geometry['bestAttribute'] == 25, row
        assert geometry['canvas'] == [1024, 784], geometry
        assert abs(geometry['partAspect'] - geometry['canvasAspect']) < .025, geometry
        if geometry['adornee'].endswith('.WristFace'):
            assert geometry['face'] == 'Top', geometry
        capture(st, os.path.join(args.out, label + '.png'))
        st.luau(LOOK, 'Client')
        st.luau('workspace.CurrentCamera.FieldOfView=22 return true', 'Client')
        time.sleep(.5)
        capture(st, os.path.join(args.out, label + '-zoom.png'))
        st.luau('workspace.CurrentCamera.FieldOfView=70 return true', 'Client')
        st.luau(LEVEL_HEAD, 'Client')
        pointer(st, 'wrist', False)
        time.sleep(.65)
        save()

    try:
        set_edit_attrs(st, {'GolfTestMode': False, 'SimulateVR': True, 'SkipMenu': None, 'PBInStudio': False})
        st.start_play()
        time.sleep(12)
        st.luau(LEVEL_HEAD, 'Client')
        click('Play', 'courses')
        click('PlayCourse', None)
        # Seed the authoritative Studio-only in-memory record, not just its replicated
        # attribute: setSettings republishes that record when handedness changes.
        # MCP execute_luau has a separate require cache. An actual temporary server
        # Script must share GolfServer's PersonalBest module instance/record table.
        seed_source = """
assert(game:GetService('RunService'):IsStudio(), 'regression fixture is Studio-only')
local output = script:WaitForChild('Result')
local ok, value = pcall(function()
local PB = require(game:GetService('ServerScriptService'):WaitForChild('GolfServer'):WaitForChild('PersonalBest'))
local seeded = {}
for _,p in game.Players:GetPlayers() do
  p:SetAttribute('Strokes',1)
  local best, isNew, previous = PB.recordRound(p, 'lantern_grove', 25)
  assert(best == 25, 'unexpected existing Studio best; fixture expects fresh in-memory record')
  table.insert(seeded, {userId=p.UserId, best=best, isNew=isNew, previous=previous})
end
return seeded
end)
output.Value = game:GetService('HttpService'):JSONEncode({ok=ok, result=ok and value or nil, error=not ok and tostring(value) or nil})
"""
        seed_name = 'StageRWristBestFixture'
        st.luau("""
local ss = game:GetService('ServerScriptService')
assert(not ss:FindFirstChild(%s), 'fixture already exists')
local s=Instance.new('Script') s.Name=%s s.Source=%s
local v=Instance.new('StringValue') v.Name='Result' v.Parent=s
s.Parent=ss
return true
""" % (json.dumps(seed_name), json.dumps(seed_name), json.dumps(seed_source)), 'Server')
        try:
            seed_reply = wait_for(lambda: st.luau("local s=game:GetService('ServerScriptService'):FindFirstChild(%s) return s and s.Result.Value or ''" % json.dumps(seed_name), 'Server'), 'server fixture did not finish', 10)
            result['bestSeed'] = json.loads(seed_reply)
            assert result['bestSeed']['ok'], result['bestSeed']
        finally:
            st.luau("local s=game:GetService('ServerScriptService'):FindFirstChild(%s) if s then s:Destroy() end return true" % json.dumps(seed_name), 'Server')
        time.sleep(.8)
        try:
            result['swing'] = json.loads(st.luau(SWING % ('4.0', '0'), 'Client', timeout=90))
        except Exception as exc:
            result['swing'] = {'error': str(exc)}
        print('swing', json.dumps(result['swing'])[:400], flush=True)
        st.luau(LEVEL_HEAD, 'Client')
        time.sleep(1.5)
        screenshot('left-wrist')
        for trial in range(3):
            click('WristMenu', 'title', True)
            click('Resume', None)
            click('WristScores', 'scorecard', True)
            click('Close', None)
        def cycle(tag):
            click('WristMenu', 'title', True)
            assert pointer(st, 'state')['wrist']['best'] == '-2', tag
            click('Resume', None)
            click('WristScores', 'scorecard', True)
            click('Close', None)
        # right -> left
        click('WristMenu', 'title', True)
        click('Settings', 'settings')
        click('HandLeft', 'settings')
        hand = 'LeftHand'
        click('Back', 'title')
        click('Resume', None)
        screenshot('right-wrist')
        cycle('after R->L')
        # left -> right
        click('WristMenu', 'title', True)
        click('Settings', 'settings')
        click('HandRight', 'settings')
        hand = 'RightHand'
        click('Back', 'title')
        click('Resume', None)
        screenshot('left-wrist-after-swap-back')
        cycle('after L->R')
        result['console'] = {'server': st.problems('Server'), 'client': st.problems('Client')}
        assert not any(line.startswith('ERROR ') for rows in result['console'].values() for line in rows), result['console']
        result['passed'] = True
    except Exception as exc:
        result['failure'] = str(exc)
        raise
    finally:
        if 'console' not in result:
            try:
                result['console'] = {'server': st.problems('Server'), 'client': st.problems('Client')}
            except Exception as exc:
                result['consoleReadError'] = str(exc)
        save()
        st.stop_play()
        set_edit_attrs(st, restore)
        print(json.dumps({'passed': result['passed'], 'failure': result.get('failure'), 'console': result.get('console')}), flush=True)


if __name__ == '__main__':
    main()
