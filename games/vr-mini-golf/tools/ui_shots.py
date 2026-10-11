#!/usr/bin/env python3
"""UI screenshots of the golf HUD and Explore mode in a normal (non-test) playtest, desktop or Studio phone emulator.

  python3 tools/ui_shots.py --out playtests/lantern-v1/stage-d/ui                 # desktop
  python3 tools/ui_shots.py --device iphone_17_pro --out playtests/lantern-v1/stage-d/ui

Drives the real client through GolfClient.Explore's Studio-only GolfExploreDebug hook and saves Studio MCP
screen captures (<prefix>_<name>.png). Stops play and the emulator when done.
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_playtests import Studio, set_edit_attrs, log, GAME_DIR  # noqa: E402

STEPS = [
    ("golf", None),
    ("golf_scorecard", ["scorecard"]),
    ("explore", ["scorecard", "on", "wait:1.5", "teleport:Hollow Tree"]),
    ("explore_menu", ["menu"]),
    ("explore_fly", ["menu", "fly:true", "vertical:1", "wait:1", "vertical:0"]),
    ("explore_falls", ["fly:false", "teleport:Grand Falls"]),
    ("explore_h5", ["teleport:H5"]),
    ("back_to_golf", ["off", "wait:2.5"]),
]


def hook(st, cmd):
    if cmd.startswith("wait:"):
        time.sleep(float(cmd[5:]))
        return
    name, _, arg = cmd.partition(":")
    lua_arg = {"": "nil", "true": "true", "false": "false"}.get(arg)
    if lua_arg is None:
        lua_arg = arg if arg.lstrip("-").isdigit() else json.dumps(arg)
    st.luau("game.Players.LocalPlayer.PlayerScripts.GolfExploreDebug:Invoke(%s, %s) return 'ok'" % (json.dumps(name), lua_arg),
            "Client")


def capture(st, path):
    r = st.m.req("tools/call", {"name": "screen_capture", "arguments": {"studio_id": st.id, "capture_id": os.path.basename(path)}})
    img = [c for c in r["result"]["content"] if c.get("type") == "image"][0]
    tmp = path + ".jpg"
    with open(tmp, "wb") as fh:
        fh.write(base64.b64decode(img["data"]))
    subprocess.run(["uv", "run", "-q", "--with", "pillow", "python", "-c",
                    "import sys; from PIL import Image; Image.open(sys.argv[1]).save(sys.argv[2])", tmp, path],
                   check=True, timeout=120)
    os.remove(tmp)
    log("shot", os.path.relpath(path, GAME_DIR))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(GAME_DIR, "playtests", "lantern-v1", "stage-d", "ui"))
    ap.add_argument("--device")
    ap.add_argument("--wait", type=float, default=12)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    prefix = "phone" if args.device else "desktop"
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False})
    if args.device:
        st.luau("game:GetService('StudioDeviceSimulatorService'):SetDeviceAsync(%s) return 'ok'" % json.dumps(args.device), "Edit")
    try:
        st.start_play()
        time.sleep(args.wait)
        for name, cmds in STEPS:
            for c in cmds or []:
                hook(st, c)
            time.sleep(1.5)
            capture(st, os.path.join(args.out, "%s_%s.png" % (prefix, name)))
        problems = {"server": st.problems("Server"), "client": st.problems("Client")}
        print(json.dumps(problems))
    finally:
        st.stop_play()
        if args.device:
            st.luau("pcall(function() game:GetService('StudioDeviceSimulatorService'):StopSimulationAsync() end) return 'ok'", "Edit")


if __name__ == "__main__":
    main()
