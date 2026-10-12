#!/usr/bin/env python3
"""VR wrist trigger check (stage q): scripted SimulateVR motion through VRControls' GolfPointerDebug "wristSim" hook.

  python3 tools/wrist_sim.py --out playtests/stage-q/wrist-sim [--seeds 7,8]

Scenarios (see VRControls wristSim): watch (3 deliberate looks: expect 3 shows), glance (0.15 s flicks), swings
(practice swings, off hand on the grip then IN the watch pose), stance (address waggles behind a hittable ball),
head (25 s looking around / walking / pointing / near-watch poses). Glance/swing/stance shows are false shows. Relaxed Stage s gaze deliberately accepts near-watch head poses.
Also saves shots of the wrist up (bracer + card) and the pointer on the wrist MENU button.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_playtests import Studio, set_edit_attrs, GAME_DIR  # noqa: E402
from ui_shots import capture  # noqa: E402
from menu_shots import menu, pointer  # noqa: E402

LOOK_AT_CARD = """local h = game.ReplicatedStorage:WaitForChild('VRDebug'):WaitForChild('Head')
local card = workspace.CurrentCamera:FindFirstChild('VRWrist')
if not card then
  local gui = game.Players.LocalPlayer.PlayerGui:FindFirstChild('VRWrist')
  card = gui and gui.Adornee
end
local cam = workspace.CurrentCamera
local o = cam.CFrame * h.Value:Inverse() -- sim camera = origin * head
local headW = o * h.Value
h.Value = o:Inverse() * CFrame.lookAt(headW.Position, card.Position)
return 'ok'"""

LEVEL_HEAD = """local h = game.ReplicatedStorage:WaitForChild('VRDebug'):WaitForChild('Head')
local before = h.Value
local look = Vector3.new(before.LookVector.X, 0, before.LookVector.Z)
look = look.Magnitude > 0.01 and look.Unit or Vector3.new(0, 0, -1)
h.Value = CFrame.lookAt(before.Position, before.Position + look)
return 'ok'"""


def shots(st, out):
    pointer(st, "wrist", True)
    time.sleep(1.2)
    up = pointer(st, "state")["wrist"]
    capture(st, os.path.join(out, "wrist_up.png"))
    # zoom: head turned to the card (still in its gaze cone), narrow FOV
    st.luau(LOOK_AT_CARD, "Client")
    time.sleep(0.3)
    st.luau("workspace.CurrentCamera.FieldOfView = 22 return 'ok'", "Client")
    time.sleep(0.4)
    capture(st, os.path.join(out, "wrist_up_zoom_fov22.png"))
    st.luau("workspace.CurrentCamera.FieldOfView = 70 return 'ok'", "Client")
    targets = pointer(st, "targets") or []
    t = next((t for t in targets if t["name"] == "WristMenu"), None)
    hover = None
    if t:
        pointer(st, "aim", {"hand": "RightHand", "point": t["world"]})
        time.sleep(0.5)
        hover = pointer(st, "state")["pointer"]
        capture(st, os.path.join(out, "wrist_pointer_menu.png"))
        st.luau(LOOK_AT_CARD, "Client")
        time.sleep(0.3)
        st.luau("workspace.CurrentCamera.FieldOfView = 30 return 'ok'", "Client")
        time.sleep(0.4)
        capture(st, os.path.join(out, "wrist_pointer_menu_zoom_fov30.png"))
        st.luau("workspace.CurrentCamera.FieldOfView = 70 return 'ok'", "Client")
    pointer(st, "wrist", False)
    time.sleep(1.0)
    down = pointer(st, "state")["wrist"]
    return {"up": up, "hover": hover, "down_after": down}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(GAME_DIR, "playtests", "stage-q", "wrist-sim"))
    ap.add_argument("--seeds", default="7")
    ap.add_argument("--wait", type=float, default=12)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": True, "SkipMenu": None})
    res = {"runs": []}
    try:
        st.start_play()
        time.sleep(args.wait)
        st.luau(LEVEL_HEAD, "Client")
        print("close", menu(st, "close"))
        time.sleep(1.5)
        res["shots"] = shots(st, args.out)
        print("SHOTS", json.dumps(res["shots"])[:600])
        false_shows = 0
        for seed in [int(s) for s in args.seeds.split(",")]:
            for sc in ["watch", "glance", "swings", "stance", "head"]:
                st.luau(LEVEL_HEAD, "Client")
                r = pointer(st, "wristSim", {"scenario": sc, "seed": seed})
                r["seed"] = seed
                res["runs"].append(r)
                if sc in ("glance", "swings", "stance"):
                    false_shows += r["shows"]
                print("%-6s seed %d: shows %d hides %d frames %d lookFrames %d by %s latency %s" % (
                    sc, seed, r["shows"], r["hides"], r["frames"], r["lookFrames"], r.get("lookFramesBy"), r.get("latencyMs")))
        watch = [r for r in res["runs"] if r["scenario"] == "watch"]
        res["false_shows"] = false_shows
        res["watch_ok"] = all(r["shows"] == 3 and r["hides"] == 3 for r in watch)
        res["problems"] = {"server": st.problems("Server"), "client": st.problems("Client")}
        res["pass"] = false_shows == 0 and res["watch_ok"]
        print("FALSE SHOWS", false_shows, "WATCH", "OK" if res["watch_ok"] else "BAD", "->", "PASS" if res["pass"] else "FAIL")
        print(json.dumps(res["problems"]))
    finally:
        with open(os.path.join(args.out, "wrist_sim.json"), "w") as fh:
            json.dump(res, fh, indent=1)
        st.stop_play()
        set_edit_attrs(st, {"SimulateVR": False})


if __name__ == "__main__":
    main()
