"""Lobby-only release gate using existing SimulateVR input hooks."""
import json
import time
from pathlib import Path
from run_playtests import Studio, set_edit_attrs, mcp_grab
from menu_shots import menu, pointer

s = Studio()
assert s.mode()[0] == 'Edit'
assert s.luau('return game.PlaceId==87725688219952 and workspace:GetAttribute("PlaceRole")=="lobby"') == 'true'
out = {}
dest = Path('playtests/stage-ak')
set_edit_attrs(s, {'SimulateVR': True, 'GolfTestMode': False})
try:
    s.start_play()
    time.sleep(5)
    menu(s, 'close')
    s.luau('local d=game.ReplicatedStorage.VRDebug local _,y=d.Head.Value:ToOrientation() d.Head.Value=CFrame.new(d.Head.Value.Position)*CFrame.Angles(0,y,0) return "ok"', 'Client')
    pointer(s, 'wrist', True)
    time.sleep(1.2)
    out['wrist'] = pointer(s, 'state')['wrist']
    assert out['wrist']['shown'], out['wrist']
    mcp_grab(s, str(dest / 'vr-wrist.png'))
    pointer(s, 'wrist', 'down')
    out['putter'] = s.luau('return workspace:FindFirstChild("VRPutter",true)~=nil', 'Client')
    assert out['putter'] == 'true'
    out['sticks'] = json.loads(s.luau('''local d=game.ReplicatedStorage.VRDebug
local root=game.Players.LocalPlayer.Character.HumanoidRootPart
local p0=root.Position
d.Stick:Fire(Enum.KeyCode.Thumbstick1,Vector2.new(0,0.8)) task.wait(0.6)
d.Stick:Fire(Enum.KeyCode.Thumbstick1,Vector2.zero) task.wait(0.2)
local moved=(root.Position-p0).Magnitude
local c0=workspace.CurrentCamera.CFrame.LookVector
d.Stick:Fire(Enum.KeyCode.Thumbstick2,Vector2.new(0.8,0)) task.wait(0.3)
d.Stick:Fire(Enum.KeyCode.Thumbstick2,Vector2.zero) task.wait(0.3)
local angle=math.deg(math.acos(math.clamp(c0:Dot(workspace.CurrentCamera.CFrame.LookVector),-1,1)))
return game.HttpService:JSONEncode({moved=moved,turnDegrees=angle})''', 'Client'))
    assert out['sticks']['moved'] > 1 and out['sticks']['turnDegrees'] > 5, out['sticks']
    def button(key):
        s.luau('local b=game.ReplicatedStorage.VRDebug.Button b:Fire(Enum.KeyCode.'+key+',false) b:Fire(Enum.KeyCode.'+key+',true) task.wait(0.7) return "ok"', 'Client')
    for key in ['ButtonB', 'ButtonY']:
        button(key)
        assert pointer(s, 'state')['scorecard']
        out[key] = json.loads(s.luau(Path('tools/stage_ag_layout.luau').read_text(), 'Client'))
        assert all(out[key][n] == 0 for n in ['titleClose', 'titleGear', 'closeGear']), out[key]
        mcp_grab(s, str(dest / ('vr-' + key + '.png')))
        button(key)
        assert not pointer(s, 'state')['scorecard']
    button('ButtonB')
    target = next(t for t in pointer(s, 'targets') if t['name'] == 'SettingsButton')
    pointer(s, 'aim', {'hand': 'RightHand', 'point': target['world']})
    time.sleep(0.5)
    out['gearHover'] = pointer(s, 'state')['pointer']
    assert out['gearHover']['button'] == 'SettingsButton'
    pointer(s, 'trigger', 'RightHand')
    time.sleep(0.8)
    out['settings'] = json.loads(menu(s, 'state'))
    assert out['settings']['page'] == 'settings'
    mcp_grab(s, str(dest / 'vr-settings.png'))
    out['console'] = {dm: s.problems(dm) for dm in ['Server', 'Client']}
    assert not any(out['console'].values()), out['console']
    out['pass'] = True
finally:
    s.stop_play()
    set_edit_attrs(s, {'SimulateVR': False, 'GolfTestMode': False})
    dest.joinpath('vr-results.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
