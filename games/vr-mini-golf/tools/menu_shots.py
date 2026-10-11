#!/usr/bin/env python3
"""Screenshots of the front end (title, course picker, settings, how to play, results) in a normal playtest.

  python3 tools/menu_shots.py --out playtests/stage-m/ui                          # desktop
  python3 tools/menu_shots.py --device iphone_17_pro --out playtests/stage-m/ui   # Studio phone emulator
  python3 tools/menu_shots.py --vr --out playtests/stage-m/ui                     # SimulateVR: world-space panel

Drives GolfClient.FrontEnd through its Studio-only GolfMenuDebug hook and saves Studio MCP screen captures
(<prefix>_menu_<page>.png), then the golf view with the menu closed. Stops play and the emulator when done.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_playtests import Studio, set_edit_attrs, GAME_DIR  # noqa: E402
from ui_shots import capture  # noqa: E402

# a finished round for the results page (par 27): 25 strokes, a new best over 28
RESULT = {"scores": [2, 3, 2, 4, 3, 2, 3, 3, 3],
          "result": {"course": "lantern_grove", "total": 25, "par": 27, "best": 25, "previousBest": 28, "newBest": True, "counted": True}}


def menu(st, cmd, arg=None):
    return st.luau("return game:GetService('HttpService'):JSONEncode(game.Players.LocalPlayer.PlayerScripts:WaitForChild('GolfMenuDebug', 10):Invoke(%s, %s))"
                   % (json.dumps(cmd), "nil" if arg is None else "game:GetService('HttpService'):JSONDecode(%s)" % json.dumps(json.dumps(arg))
                      if isinstance(arg, dict) else json.dumps(arg)), "Client")


def panel_pos(st):
    return json.loads(st.luau("local p = workspace.CurrentCamera:FindFirstChild('GolfMenuPanel') "
                              "return game:GetService('HttpService'):JSONEncode(p and {p.Position.X, p.Position.Y, p.Position.Z} or {0, 0, 0})", "Client"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(GAME_DIR, "playtests", "stage-m", "ui"))
    ap.add_argument("--device")
    ap.add_argument("--wait", type=float, default=12)
    ap.add_argument("--vr", action="store_true", help="SimulateVR: the world-space menu panel")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    prefix = "vr" if args.vr else "phone" if args.device else "desktop"
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": args.vr, "SkipMenu": None})
    if args.device:
        st.luau("game:GetService('StudioDeviceSimulatorService'):SetDeviceAsync(%s) return 'ok'" % json.dumps(args.device), "Edit")
    try:
        st.start_play()
        time.sleep(args.wait)
        if args.vr:
            # the simulated head starts pitched ~60 deg down at the tee; level it (keep position and yaw) and reopen
            # the menu so its panel is anchored in front of a level head
            print("head", st.luau("""local h = game.ReplicatedStorage:WaitForChild('VRDebug'):WaitForChild('Head')
local before = h.Value
local look = Vector3.new(before.LookVector.X, 0, before.LookVector.Z)
look = look.Magnitude > 0.01 and look.Unit or Vector3.new(0, 0, -1)
h.Value = CFrame.lookAt(before.Position, before.Position + look)
return tostring(before) .. ' -> ' .. tostring(h.Value)""", "Client"))
            print("close", menu(st, "close"))
            time.sleep(1.0)
        panels = []
        for page in ["title", "courses", "settings", "howto"]:
            print(page, menu(st, "open", page))
            time.sleep(1.5)
            capture(st, os.path.join(args.out, "%s_menu_%s.png" % (prefix, page)))
            if args.vr:
                panels.append(panel_pos(st))
            if page == "howto":
                print("text", st.luau("""local out = {}
    for _, g in game.Players.LocalPlayer.PlayerGui:GetChildren() do
      if g.Name == 'GolfMenu' then
        local scale = 1
        for _, d in g:GetDescendants() do if d:IsA('UIScale') then scale = d.Scale end end
        for _, d in g:GetDescendants() do
          if d:IsA('TextLabel') and d.Name == 'Text' and d.Parent.Name == 'HowToBody' then
            table.insert(out, string.format('%s TextSize %d x scale %.2f = %.1f px, fits %s', g.ClassName, d.TextSize, scale, d.TextSize * scale, tostring(d.TextFits)))
          end
        end
      end
    end
    return table.concat(out, '; ')""", "Client"))
        print("results", menu(st, "results", RESULT))
        time.sleep(1.5)
        capture(st, os.path.join(args.out, "%s_menu_results.png" % prefix))
        if args.vr:
            panels.append(panel_pos(st))
            spread = max(max(abs(a[i] - b[i]) for i in range(3)) for a in panels for b in panels)
            print("vr panel positions", panels, "max jump %.3f studs" % spread, "PASS" if spread < 0.01 else "FAIL")

        print("close", menu(st, "close"))
        time.sleep(1.5)
        capture(st, os.path.join(args.out, "%s_golf_hud.png" % prefix))
        problems = {"server": st.problems("Server"), "client": st.problems("Client")}
        print(json.dumps(problems))
    finally:
        st.stop_play()
        if args.vr:
            set_edit_attrs(st, {"SimulateVR": False})
        if args.device:
            st.luau("pcall(function() game:GetService('StudioDeviceSimulatorService'):StopSimulationAsync() end) return 'ok'", "Edit")


if __name__ == "__main__":
    main()
