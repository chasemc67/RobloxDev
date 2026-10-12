#!/usr/bin/env python3
"""Stage s VR-only fitting, persistence roundtrip, reset and explainer screenshots.
Runs one Studio play session, leaves Edit mode. No live DataStore writes by default.
"""
import argparse
import json
import os
import time
from run_playtests import Studio, set_edit_attrs, GAME_DIR
from menu_shots import menu, pointer
from ui_shots import capture


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(GAME_DIR, 'playtests', 'stage-s', 'club-setup'))
    ap.add_argument('--wait', type=float, default=12)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    st = Studio()
    result = {'ui_steps': []}

    def wait_for(fn, description, seconds=8):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            value = fn()
            if value:
                return value
            time.sleep(.15)
        raise AssertionError(description)

    def menu_page():
        value = menu(st, 'state')
        return (json.loads(value) if isinstance(value, str) else value).get('page')

    def click_button(name, expected_page):
        # Use the non-club controller so opening setup preserves the putting-hand pose.
        target = wait_for(lambda: next((t for t in pointer(st, 'targets') or [] if t['name'] == name), None),
                          'Settings target missing: ' + name)
        pointer(st, 'aim', {'hand': 'LeftHand', 'point': target['world']})
        hover = wait_for(lambda: (lambda x: x if x.get('button') == name else None)(pointer(st, 'state')['pointer']),
                         'Controller ray failed to hover: ' + name)
        pointer(st, 'trigger', 'LeftHand')
        wait_for(lambda: menu_page() == expected_page, 'Wrong page after: ' + name)
        row = {'button': name, 'controller': 'LeftHand', 'hover': hover, 'page': menu_page(), 'pass': True}
        result['ui_steps'].append(row)
        print('UI', json.dumps(row), flush=True)

    st.stop_play()
    set_edit_attrs(st, {'GolfTestMode': False, 'SimulateVR': True, 'SkipMenu': None, 'ClubSetupInStudio': False})
    try:
        st.start_play()
        time.sleep(args.wait)
        menu(st, 'open', 'title')
        click_button('Settings', 'settings')
        capture(st, os.path.join(args.out, 'settings_club_setup.png'))
        click_button('ClubSetup', None)
        entry = wait_for(lambda: (lambda x: x if x.get('active') else None)(pointer(st, 'clubSetup', 'state')),
                         'Settings Club setup button did not activate fitting')
        result['settings_entry'] = {'pass': entry['active'] and menu_page() is None, 'state': entry}
        time.sleep(1.2)
        result['explainer'] = json.loads(st.luau("""
local cam=workspace.CurrentCamera
local panel=cam:FindFirstChild('ClubSetupCard')
local gui=game.Players.LocalPlayer.PlayerGui:FindFirstChild('ClubSetupExplainer')
assert(panel and gui,'missing explainer panel/gui')
local screen,visible=cam:WorldToViewportPoint(panel.Position)
local texts,images={},{}
for _,d in gui:GetDescendants() do
 if d:IsA('TextLabel') then table.insert(texts,{name=d.Name,text=d.Text,fits=d.TextFits}) end
 if d:IsA('ImageLabel') then table.insert(images,{name=d.Name,loaded=d.IsLoaded,image=d.Image}) end
end
return game.HttpService:JSONEncode({visible=visible,screen={screen.X,screen.Y,screen.Z},
 enabled=gui.Enabled,adornee=gui.Adornee==panel,face=gui.Face.Name,canvas={gui.CanvasSize.X,gui.CanvasSize.Y},texts=texts,images=images})
""", 'Client'))
        capture(st, os.path.join(args.out, 'club_setup_explainer.png'))
        # Dedicated inspection view: turn the simulated headset toward the actual card,
        # without changing card placement or substituting a screen-space preview.
        st.luau("""
local h=game.ReplicatedStorage.VRDebug.Head
local cam=workspace.CurrentCamera
local panel=cam:FindFirstChild('ClubSetupCard')
local origin=cam.CFrame*h.Value:Inverse()
h.Value=origin:Inverse()*CFrame.lookAt(cam.CFrame.Position,panel.Position)
cam.FieldOfView=45
return true
""", 'Client')
        time.sleep(.5)
        capture(st, os.path.join(args.out, 'club_setup_explainer_close.png'))
        st.luau('workspace.CurrentCamera.FieldOfView=70 return true','Client')
        pointer(st, 'clubSetup', 'cancel')
        result['fit_test'] = pointer(st, 'clubSetupTest')
        result['server_roundtrip'] = json.loads(st.luau("return game.HttpService:JSONEncode(game.ReplicatedStorage.Golf.Remotes.ClubSetup:InvokeServer('load'))", 'Client'))
        time.sleep(1.2)
        menu(st, 'open', 'title')
        click_button('Settings', 'settings')
        before_reset = pointer(st, 'clubSetup', 'state')
        assert before_reset.get('saved'), 'Fit missing before Settings reset'
        click_button('ResetClubSetup', 'settings')
        for _ in range(100):
            state = pointer(st, 'clubSetup', 'state')
            if not state.get('saving') and not state.get('saved'):
                break
            time.sleep(.1)
        result['reset'] = state
        result['reset_server_roundtrip'] = json.loads(st.luau("return game.HttpService:JSONEncode(game.ReplicatedStorage.Golf.Remotes.ClubSetup:InvokeServer('load'))", 'Client'))
        reset_fits = result['reset_server_roundtrip'].get('fits') or {}
        result['reset_via_settings'] = {'pass': bool(before_reset.get('saved') and not state.get('saved')
                                                   and not state.get('saving') and menu_page() == 'settings')}
        menu(st, 'close')
        result['problems'] = {'server': st.problems('Server'), 'client': st.problems('Client')}
        result['pass'] = bool(result['fit_test'].get('pass') and result['server_roundtrip'].get('ok')
                              and result['settings_entry']['pass'] and result['reset_via_settings']['pass']
                              and result['reset_server_roundtrip'].get('ok')
                              and not reset_fits.get(state['hand'])
                              and not state.get('saved') and not state.get('saving')
                              and result['explainer']['visible'] and result['explainer']['enabled'] and result['explainer']['adornee']
                              and all(t['fits'] for t in result['explainer']['texts'])
                              and not result['problems']['server'] and not result['problems']['client'])
        print(json.dumps(result, indent=2), flush=True)
    except Exception as exc:
        result['pass'] = False
        result['error'] = str(exc)
        raise
    finally:
        with open(os.path.join(args.out, 'club_setup_sim.json'), 'w') as fh:
            json.dump(result, fh, indent=2)
        st.stop_play()
        set_edit_attrs(st, {'SimulateVR': False, 'ClubSetupInStudio': None})


if __name__ == '__main__':
    main()
