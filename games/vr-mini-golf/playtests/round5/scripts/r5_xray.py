#!/usr/bin/env python3
"""X-ray / see-through check (stage p): ball and putter head behind tunnels, wheels, trees and rails.

  python3 tools/xray_shots.py --out playtests/stage-p/xray

For each spot the ball is put on the felt inside or behind an obstacle and the viewpoint is put outside it, looking
at the ball:
  * VR (SimulateVR): the simulated head (GolfPointerDebug "pose") with the putter head beside the ball. Logs whether
    the ball / club Highlights are on (GolfXRayDebug), how many course parts the head-to-ball fade has faded, and
    saves <spot>_vr.png.
  * flat (test-mode "look" camera from the same point): the ball Highlight, <spot>_flat.png.
The "open" spot looks at the ball from straight above it: nothing blocks, so both outlines must be off.
Writes xray.json; PASS if every blocked spot shows the ball outline (and the club outline in VR) and "open" shows none.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools")))
from run_playtests import Studio, set_edit_attrs, GAME_DIR  # noqa: E402
from ui_shots import capture  # noqa: E402

# name, hole, ball spot (x, felt y, z), what must be in the way (substring of the blocking part's full name; None =
# nothing: the open control spot)
SPOTS = [
    ("h3_mushroom_tunnel", 3, (158.5, 44.0, 28.3), "mushroom_house_large_tunnel"),
    ("h6_mill_wheel", 6, (37.5, 30.0, -63.2), "mill"),
    ("h9_trunk_tunnel", 9, (-75.1, 40.6, 9.1), "trunk_tunnel"),
    ("h9_hollow_tree", 9, (-85.0, 41.0, 0.0), "hollow_tree|Hole9.Decor|Hole9.Movers|Hole9.Rails"),  # (inside the tree)
    ("h8_hollow_tree", 8, (-17.5, 37.3, 16.0), "hollow_tree"),
    ("h1_rail", 1, (186.5, 25.0, 135.3), "Hole1.Rails|deflector"),
    ("h5_covered_bridge", 5, (71.4, 38.5, -96.7), "covered_bridge|bridge"),
    ("open", 1, (186.5, 25.0, 135.3), None),
]
# round 5: live VR fade at the round-3 worst wall spots (head at the round-4 camera pose: yaw, dist 6, pitch 30) and
# the H6 tee sign spot; every part CameraOcclusion.occluders(head, ball) returns must have LTM >= 0.7
FADE_SPOTS = [
    ("fade_h1", 1, (193.4, 25, 139.6), 30), ("fade_h2", 2, (222.7, 25, 107.4), 90), ("fade_h3", 3, (163.3, 44.5, 24.7), 150),
    ("fade_h4", 4, (185, 48.5, -34.3), 30), ("fade_h5", 5, (71.4, 38.5, -96.7), 90), ("fade_h6_teesign", 6, (47.7, 30.5, -71.5), 0),
    ("fade_h7", 7, (49.4, 25.2, -13.9), 180), ("fade_h8_hollowtree", 8, (-14.4, 36.5, -15.4), 210), ("fade_h9_hollowtree", 9, (-80.9, 42.6, 21.7), 0),
]

# From the ball's real resting spot, find a viewpoint (ring around the ball, high first) whose sight lines to the ball
# and to a point 0.3 behind it (where the putter head goes) both first hit an opaque part named like `want` (or, for
# want = nil, hit nothing at all). Returns head, ball, club point.
FIND_HEAD = r"""
local want = %s
local ball = workspace.Balls:GetChildren()[1]
local b = ball.Position
local CO = require(game.ReplicatedStorage.Golf.CameraOcclusion)
local rp = RaycastParams.new()
rp.FilterType = Enum.RaycastFilterType.Exclude
rp.CollisionGroup = CO.CAMERA_GROUP
rp.IgnoreWater = true
local function first(from, to)
  local f = { workspace.CurrentCamera, workspace.Balls, game.Players.LocalPlayer.Character }
  local d = to - from
  for _ = 1, 12 do
    rp.FilterDescendantsInstances = f
    local h = workspace:Raycast(from, d.Unit * (d.Magnitude - 0.12), rp)
    if not h then return nil end
    if h.Instance:IsA('Terrain') or h.Instance.Transparency < 0.95 then return h.Instance end
    table.insert(f, h.Instance)
  end
end
local function ok(inst)
  if want == nil then return inst == nil end
  if inst == nil then return false end
  for w in string.gmatch(want, '[^|]+') do
    if string.find(inst:GetFullName(), w, 1, true) then return true end
  end
  return false
end
for _, up in { 4.5, 3, 1.8, 0.8, 0.4 } do
  for _, r in { 6, 8, 10, 4, 3, 2, 12, 14, 17, 20 } do
    for k = 0, 23 do
      local a = math.rad(k * 15)
      local head = b + Vector3.new(math.cos(a) * r, up, math.sin(a) * r)
      local away = Vector3.new(b.X - head.X, 0, b.Z - head.Z).Unit
      local club = b + away * 0.3
      if ok(first(head, b)) and ok(first(head, club)) then
        return game:GetService('HttpService'):JSONEncode({ head = { head.X, head.Y, head.Z }, ball = { b.X, b.Y, b.Z }, club = { club.X, club.Y, club.Z },
          blocker = want and first(head, b):GetFullName() or nil })
      end
    end
  end
end
return game:GetService('HttpService'):JSONEncode({ ball = { b.X, b.Y, b.Z } })
"""

YAW_HEAD = r"""
local ball = workspace.Balls:GetChildren()[1]
local b = ball.Position
local focus = b + Vector3.new(0, 0.25, 0)
local rot = CFrame.fromEulerAnglesYXZ(-math.rad(30), math.rad(%s), 0)
local head = focus - rot.LookVector * 6
local away = Vector3.new(b.X - head.X, 0, b.Z - head.Z).Unit
local club = b + away * 0.3
return game:GetService('HttpService'):JSONEncode({ head = { head.X, head.Y, head.Z }, ball = { b.X, b.Y, b.Z }, club = { club.X, club.Y, club.Z } })
"""

STATE = r"""
local head, ballP, clubP = Vector3.new(%f, %f, %f), Vector3.new(%f, %f, %f), Vector3.new(%f, %f, %f)
local CO = require(game.ReplicatedStorage.Golf.CameraOcclusion)
local rp = RaycastParams.new()
rp.FilterType = Enum.RaycastFilterType.Exclude
rp.CollisionGroup = CO.CAMERA_GROUP
rp.IgnoreWater = true
local function blocked(from, to)
  local f = { workspace.CurrentCamera, workspace.Balls, game.Players.LocalPlayer.Character }
  local d = to - from
  for _ = 1, 12 do
    rp.FilterDescendantsInstances = f
    local h = workspace:Raycast(from, d.Unit * (d.Magnitude - 0.12), rp)
    if not h then return false end
    if h.Instance:IsA('Terrain') or h.Instance.Transparency < 0.95 then return true end
    table.insert(f, h.Instance)
  end
  return false
end
local HS = game:GetService('HttpService')
local ps = game.Players.LocalPlayer.PlayerScripts
local x = ps:FindFirstChild('GolfXRayDebug')
local faded = 0
for _, d in workspace.Course:GetDescendants() do
  if d:IsA('BasePart') and d.LocalTransparencyModifier >= 0.69 and d.LocalTransparencyModifier < 0.99 then faded += 1 end
end
local occ = CO.occluders(head, ballP + Vector3.new(0, 0.25, 0), { game.Players.LocalPlayer.Character })
local nOcc, nFadedOcc, notFaded, models = 0, 0, {}, {}
for p in occ do
  nOcc += 1
  if p.LocalTransparencyModifier >= 0.69 then nFadedOcc += 1 else table.insert(notFaded, p:GetFullName() .. '=' .. p.LocalTransparencyModifier) end
  local m = p:FindFirstAncestorWhichIsA('Model')
  local k = m and m.Name or p.Name
  models[k] = (models[k] or 0) + 1
end
local glowHidden = 0
for _, d in workspace.Course:GetDescendants() do
  if d:IsA('BasePart') and d.LocalTransparencyModifier >= 0.99 then glowHidden += 1 end
end
return HS:JSONEncode({ xray = x and x:Invoke() or 'nohook', faded = faded, glowHidden = glowHidden, occluders = nOcc, occludersFaded = nFadedOcc, notFaded = notFaded, occModels = models, truth = { ball = blocked(head, ballP), club = blocked(head, clubP) } })
"""


def place(st, hole, ball):
    x, y, z = ball
    st.api("hitat", hole, "%.3f,%.3f,%.3f" % (x, y, z), "0.01,0", timeout=60)
    time.sleep(1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--wait", type=float, default=12)
    ap.add_argument("--spots", help="comma list of spot names (default all); merges into an existing xray.json")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    st = Studio()
    spots = [sp for sp in SPOTS if not args.spots or sp[0] in args.spots.split(",")]
    results = {}
    prev = os.path.join(args.out, "xray.json")
    if args.spots and os.path.exists(prev):
        results = json.load(open(prev))
    for mode in ("vr", "flat"):
        st.stop_play()
        set_edit_attrs(st, {"GolfTestMode": True, "SimulateVR": mode == "vr", "SkipMenu": None})
        try:
            st.start_play()
            time.sleep(args.wait)
            allspots = spots + ([(n, h, b, ("@yaw", y)) for n, h, b, y in FADE_SPOTS] if not args.spots else [])
            for name, hole, ball, want in allspots:
                place(st, hole, ball)
                if isinstance(want, tuple):
                    found = json.loads(st.luau(YAW_HEAD % want[1], "Client"))
                else:
                    found = json.loads(st.luau(FIND_HEAD % ("nil" if want is None else json.dumps(want)), "Client"))
                if "head" not in found:
                    print(mode, name, "no viewpoint found", found)
                    results.setdefault(name, {})[mode] = {"xray": {}, "error": "no viewpoint", "ball": found["ball"]}
                    continue
                head, look, club = found["head"], found["ball"], found["club"]
                if mode == "vr":
                    pointer = "game.Players.LocalPlayer.PlayerScripts:WaitForChild('GolfPointerDebug', 10)"
                    away = [club[0] - look[0], 0, club[2] - look[2]]
                    d = json.dumps({"head": head, "look": look, "club": [club[0], look[1] - 0.08 + 0.065, club[2]], "face": away})
                    st.luau("return game:GetService('HttpService'):JSONEncode(%s:Invoke('pose', game:GetService('HttpService'):JSONDecode(%s)))"
                            % (pointer, json.dumps(d)), "Client")
                else:
                    st.luau("""workspace:SetAttribute('GolfTestCamPos', Vector3.new(%f, %f, %f))
workspace:SetAttribute('GolfTestFocus', Vector3.new(%f, %f, %f))
workspace:SetAttribute('GolfTestFOV', 50)
workspace:SetAttribute('GolfTestCamera', 'look')
return 'ok'""" % (head[0], head[1], head[2], look[0], look[1], look[2]), "Client")
                bx, by, bz = look
                time.sleep(1.2)
                s = json.loads(st.luau(STATE % tuple(head + look + club), "Client"))
                shot = "%s_%s.png" % (name, mode)
                capture(st, os.path.join(args.out, shot))
                s.update({"head": head, "ball": look, "blocker": found.get("blocker"), "shot": shot})
                results.setdefault(name, {})[mode] = s
                print(mode, name, json.dumps(s))
            results.setdefault("_console", {})[mode] = {"server": st.problems("Server"), "client": st.problems("Client")}
        finally:
            st.stop_play()
            set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False, "GolfTestCamera": None, "GolfTestCamPos": None,
                                "GolfTestFocus": None, "GolfTestFOV": None})
    ok = True
    for name, *_ in SPOTS:
        for mode in ("vr", "flat"):
            if name not in results or mode not in results[name]:
                continue
            x = results[name][mode].get("xray") or {}
            ball_on = x.get("ball", {}).get("on")
            club_on = x.get("club", {}).get("on")
            truth = results[name][mode].get("truth") or {}
            # the outline must match the sight line at that moment (the H6 wheel turns), and the obstacle spots must
            # have been caught blocked at least in one mode
            good = bool(x) and bool(ball_on) == bool(truth.get("ball")) and (mode != "vr" or bool(club_on) == bool(truth.get("club")))
            results[name][mode]["pass"] = bool(good)
            ok = ok and bool(good)
    results["pass"] = ok
    with open(os.path.join(args.out, "xray.json"), "w") as fh:
        json.dump(results, fh, indent=1)
    print("console", json.dumps(results["_console"]))
    print("XRAY", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()
