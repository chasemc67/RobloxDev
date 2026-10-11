#!/usr/bin/env python3
"""Screenshots of the front end (title, course picker, settings, how to play, results) in a normal playtest.

  python3 tools/menu_shots.py --out playtests/stage-m/ui                          # desktop
  python3 tools/menu_shots.py --device iphone_17_pro --out playtests/stage-m/ui   # Studio phone emulator
  python3 tools/menu_shots.py --vr --out playtests/stage-m/ui                     # SimulateVR: world-space panel
  python3 tools/menu_shots.py --vr --pointer --out playtests/stage-p/vr-pointer   # laser pointer walk-through
  python3 tools/menu_shots.py --vr --wrist --out playtests/stage-p/wrist          # wrist card up / down

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


def pointer(st, cmd, arg=None):
    a = "nil" if arg is None else ("game:GetService('HttpService'):JSONDecode(%s)" % json.dumps(json.dumps(arg)) if isinstance(arg, (dict, list)) else json.dumps(arg))
    return json.loads(st.luau("return game:GetService('HttpService'):JSONEncode(game.Players.LocalPlayer.PlayerScripts:WaitForChild('GolfPointerDebug', 10):Invoke(%s, %s))"
                              % (json.dumps(cmd), a), "Client"))


# (button to aim at, hand, page expected after the trigger; None = menu closed, "scorecard" = the VR scorecard is up)
POINTER_STEPS = [
    ("WristMenu", "RightHand", "title"),
    ("Settings", "RightHand", "settings"),
    ("Back", "RightHand", "title"),
    ("HowToPlay", "RightHand", "howto"),
    ("TabPhone", "RightHand", "howto"),
    ("Back", "LeftHand", "title"),          # the other hand takes over
    ("Play", "RightHand", "courses"),
    ("Back", "RightHand", "title"),
    ("Play", "RightHand", "courses"),
    ("PlayCourse", "RightHand", None),       # menu closes: pointer hidden in play
    ("WristScores", "RightHand", "scorecard"),
    ("Close", "RightHand", None),
    ("@results", None, "results"),
    ("BackToMenu", "RightHand", "title"),
    ("@results", None, "results"),
    ("PlayAgain", "LeftHand", None),
]


def pointer_walk(st, out):
    """Aim the simulated controller at each button, check the hover, pull the trigger, check the page."""
    rows, ok = [], True
    for i, (name, hand, expect) in enumerate(POINTER_STEPS):
        if name == "@results":
            menu(st, "results", RESULT)
            time.sleep(1.2)
            continue
        if name.startswith("Wrist"):
            pointer(st, "wrist", True)
            time.sleep(1.0)
        targets = pointer(st, "targets") or []
        t = next((t for t in targets if t["name"] == name), None)
        if not t:
            rows.append({"step": i, "button": name, "error": "not on any open panel", "targets": [x["name"] for x in targets]})
            ok = False
            continue
        pointer(st, "aim", {"hand": hand, "point": t["world"]})
        time.sleep(0.4)
        hover = pointer(st, "state")["pointer"]
        shot = "%02d_%s_%s.png" % (i, name, hand)
        capture(st, os.path.join(out, shot))
        pointer(st, "trigger", hand)
        time.sleep(0.8)
        if name.startswith("Wrist"):
            pointer(st, "wrist", False)
            time.sleep(0.6)
        m = menu(st, "state")
        after = json.loads(m) if isinstance(m, str) else m
        card = st.luau("local g = game.Players.LocalPlayer.PlayerGui:FindFirstChild('VRScorecard') return g and g.Enabled or false", "Client")
        page = "scorecard" if card in (True, "true") else after.get("page")
        beam = pointer(st, "state")["pointer"]["beam"]
        good = hover.get("button") == name and page == expect and (expect is not None or not beam)
        ok = ok and good
        rows.append({"step": i, "button": name, "hand": hand, "hovered": hover.get("button"), "hand_used": hover.get("hand"),
                     "page_after": page, "expected": expect, "beam_after": beam, "pass": good, "shot": shot})
        print("pointer", rows[-1])
    with open(os.path.join(out, "pointer_walk.json"), "w") as fh:
        json.dump({"pass": ok, "steps": rows}, fh, indent=1)
    print("POINTER WALK", "PASS" if ok else "FAIL")
    return ok


def wrist_shots(st, out):
    res = {}
    pointer(st, "wrist", False)
    time.sleep(1.0)
    res["down"] = pointer(st, "state")["wrist"]
    capture(st, os.path.join(out, "wrist_down.png"))
    pointer(st, "wrist", True)
    time.sleep(0.12)
    res["fading_in"] = pointer(st, "state")["wrist"]
    time.sleep(1.0)
    res["up"] = pointer(st, "state")["wrist"]
    capture(st, os.path.join(out, "wrist_up.png"))
    # a zoomed still to judge legibility: look straight at the card, FOV 30
    st.luau("""local h = game.ReplicatedStorage.VRDebug.Head
local card = workspace.CurrentCamera:FindFirstChild('VRWrist')
local d = game.ReplicatedStorage.VRDebug
d:SetAttribute('HeadBefore', h.Value)
local head = workspace.CurrentCamera.CFrame
local lp = (head * h.Value:Inverse()):PointToObjectSpace(card.Position)
h.Value = CFrame.lookAt(h.Value.Position, lp)
workspace.CurrentCamera.FieldOfView = 25
return 'ok'""", "Client")
    time.sleep(0.5)
    res["zoom"] = pointer(st, "state")["wrist"]
    capture(st, os.path.join(out, "wrist_up_zoom_fov25.png"))
    st.luau("""local d = game.ReplicatedStorage.VRDebug
d.Head.Value = d:GetAttribute('HeadBefore')
workspace.CurrentCamera.FieldOfView = 70
return 'ok'""", "Client")
    time.sleep(0.5)
    targets = pointer(st, "targets") or []
    t = next((t for t in targets if t["name"] == "WristMenu"), None)
    if t:
        pointer(st, "aim", {"hand": "RightHand", "point": t["world"]})
        time.sleep(0.4)
        res["hover"] = pointer(st, "state")["pointer"]
        capture(st, os.path.join(out, "wrist_up_pointer_menu.png"))
    pointer(st, "wrist", False)
    time.sleep(0.12)
    res["fading_out"] = pointer(st, "state")["wrist"]
    time.sleep(1.0)
    res["down_again"] = pointer(st, "state")["wrist"]
    ok = (not res["down"]["shown"] and res["up"]["shown"] and res["up"]["alpha"] == 1 and 0 < res["fading_in"]["alpha"] < 1
          and not res["down_again"]["shown"] and res["down_again"]["alpha"] == 0)
    res["pass"] = ok
    with open(os.path.join(out, "wrist.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print("WRIST", json.dumps(res))
    print("WRIST", "PASS" if ok else "FAIL")
    return ok


def panel_pos(st):
    return json.loads(st.luau("local p = workspace.CurrentCamera:FindFirstChild('GolfMenuPanel') "
                              "return game:GetService('HttpService'):JSONEncode(p and {p.Position.X, p.Position.Y, p.Position.Z} or {0, 0, 0})", "Client"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(GAME_DIR, "playtests", "stage-m", "ui"))
    ap.add_argument("--device")
    ap.add_argument("--wait", type=float, default=12)
    ap.add_argument("--vr", action="store_true", help="SimulateVR: the world-space menu panel")
    ap.add_argument("--pointer", action="store_true", help="(--vr) laser pointer walk-through: aim, hover, trigger, page")
    ap.add_argument("--wrist", action="store_true", help="(--vr) wrist card shots: down, up, pointer on MENU")
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
            if args.pointer or args.wrist:
                ok = True
                if args.wrist:
                    ok = wrist_shots(st, args.out) and ok
                if args.pointer:
                    ok = pointer_walk(st, args.out) and ok
                print(json.dumps({"server": st.problems("Server"), "client": st.problems("Client")}))
                return
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
