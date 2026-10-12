#!/usr/bin/env python3
"""Round 6: H6 mill wheel ball/putter outline in VR, round-5 method (48 MCP-polled time samples, 0.25 s apart) with
two truths per sample: r5's (rays to the fixture positions) and live (rays to the ball's and putter head's live
positions), plus the XRay logical state and the Highlight.Enabled actually set."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "tools")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "round5", "scripts")))
from run_playtests import Studio, set_edit_attrs  # noqa: E402
from ui_shots import capture  # noqa: E402
import r5_xray as X  # noqa: E402

out = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 48
os.makedirs(out, exist_ok=True)
POSE = "return game:GetService('HttpService'):JSONEncode(game.Players.LocalPlayer.PlayerScripts:WaitForChild('GolfPointerDebug', 10):Invoke('pose', game:GetService('HttpService'):JSONDecode(%s)))"
FIND_MIXED = r"""
-- candidate heads around the ball whose sight line hits the mill wheel at least once over 4 s; pick the one
-- blocked closest to half the time (spokes passing), so both misses and false shows can be counted
local ball = workspace.Balls:GetChildren()[1]
local b = ball.Position
local CO = require(game.ReplicatedStorage.Golf.CameraOcclusion)
local rp = RaycastParams.new() rp.FilterType = Enum.RaycastFilterType.Exclude rp.CollisionGroup = CO.CAMERA_GROUP rp.IgnoreWater = true
local function first(from, to)
  local f = { workspace.CurrentCamera, workspace.Balls, game.Players.LocalPlayer.Character }
  local d = to - from
  for _ = 1, 32 do
    rp.FilterDescendantsInstances = f
    local h = workspace:Raycast(from, d.Unit * (d.Magnitude - 0.12), rp)
    if not h then return nil end
    if h.Instance:IsA('Terrain') or h.Instance.Transparency < 0.95 then return h.Instance end
    table.insert(f, h.Instance)
  end
end
local cands = {}
for _, up in { 4.5, 3, 1.8, 0.8 } do
  for _, r in { 4, 6, 8, 10 } do
    for k = 0, 35 do
      local a = math.rad(k * 10)
      table.insert(cands, { head = b + Vector3.new(math.cos(a) * r, up, math.sin(a) * r), hits = 0, mill = 0 })
    end
  end
end
for _ = 1, 40 do
  for _, c in cands do
    local i = first(c.head, b)
    if i then c.hits += 1 if string.find(i:GetFullName(), 'mill', 1, true) then c.mill += 1 end end
  end
  task.wait(0.1)
end
local best, score = nil, 1e9
for _, c in cands do
  if c.mill > 0 and c.mill == c.hits then
    local sc = math.abs(c.hits / 40 - 0.5)
    if sc < score then best, score = c, sc end
  end
end
if not best then return game:GetService('HttpService'):JSONEncode({ ball = { b.X, b.Y, b.Z } }) end
local h = best.head
local away = Vector3.new(b.X - h.X, 0, b.Z - h.Z).Unit
local club = b + away * 0.3
return game:GetService('HttpService'):JSONEncode({ head = { h.X, h.Y, h.Z }, ball = { b.X, b.Y, b.Z }, club = { club.X, club.Y, club.Z }, blockedFrac = best.hits / 40 })
"""
PROBE = r"""
local head, ballP, clubP = Vector3.new(%f, %f, %f), Vector3.new(%f, %f, %f), Vector3.new(%f, %f, %f)
local CO = require(game.ReplicatedStorage.Golf.CameraOcclusion)
local rp = RaycastParams.new() rp.FilterType = Enum.RaycastFilterType.Exclude rp.CollisionGroup = CO.CAMERA_GROUP rp.IgnoreWater = true
local cam = workspace.CurrentCamera
local function blocked(from, to, margin)
  local f = { cam, workspace.Balls, game.Players.LocalPlayer.Character }
  local d = to - from
  for _ = 1, 32 do
    rp.FilterDescendantsInstances = f
    local h = workspace:Raycast(from, d.Unit * (d.Magnitude - margin), rp)
    if not h then return false end
    if h.Instance:IsA('Terrain') or h.Instance.Transparency < 0.95 then return true end
    table.insert(f, h.Instance)
  end
  return false
end
local x = game.Players.LocalPlayer.PlayerScripts:FindFirstChild('GolfXRayDebug'):Invoke()
local eye = cam.CFrame.Position
local ball = workspace.Balls:FindFirstChildWhichIsA('BasePart')
local ph = cam:FindFirstChild('VRPutter') and cam.VRPutter:FindFirstChild('Head')
local bh, ch = cam:FindFirstChild('BallXRay'), cam:FindFirstChild('ClubXRay')
return game:GetService('HttpService'):JSONEncode({
  r5truth = { ball = blocked(head, ballP, 0.12), club = blocked(head, clubP, 0.12) },
  live = { ball = blocked(eye, ball.Position, 0.12), club = ph and blocked(eye, ph.Position, 0.1) or false },
  on = { ball = x.ball.on, club = x.club.on },
  enabled = { ball = bh and bh.Enabled or false, club = ch and ch.Enabled or false },
  eyeErr = (eye - head).Magnitude, ballMove = (ball.Position - ballP).Magnitude })
"""
st = Studio(); st.stop_play()
set_edit_attrs(st, {"GolfTestMode": True, "SimulateVR": True})
rows, res = [], {}
try:
    st.start_play(); time.sleep(12)
    X.place(st, 6, (37.5, 30.0, -63.2))
    f = json.loads(st.luau(FIND_MIXED, "Client", timeout=120)) if "--mixed" in sys.argv else json.loads(st.luau(X.FIND_HEAD % json.dumps("mill"), "Client"))
    head, look, club = f["head"], f["ball"], f["club"]
    st.luau(POSE % json.dumps(json.dumps({"head": head, "look": look, "club": [club[0], look[1] - 0.015, club[2]], "face": [club[0] - look[0], 0, club[2] - look[2]]})), "Client")
    time.sleep(0.5)
    shot_blocked = shot_clear = False
    for i in range(N):
        time.sleep(0.25)
        s = json.loads(st.luau(PROBE % tuple(head + look + club), "Client"))
        rows.append(s)
        if s["live"]["ball"] and not shot_blocked:
            capture(st, os.path.join(out, "h6_wheel_blocked%s.png" % ("_mixed" if "--mixed" in sys.argv else ""))); shot_blocked = True
        if not s["live"]["ball"] and not shot_clear:
            capture(st, os.path.join(out, "h6_wheel_clear%s.png" % ("_mixed" if "--mixed" in sys.argv else ""))); shot_clear = True
    def count(truth, field):
        r = {}
        for k in ("ball", "club"):
            r[k] = {"blocked": sum(1 for s in rows if s[truth][k]),
                    "missing": sum(1 for s in rows if s[truth][k] and not s[field][k]),
                    "false": sum(1 for s in rows if not s[truth][k] and s[field][k])}
        return r
    res = {"samples": len(rows), "fixture": f,
           "r5truth_vs_on": count("r5truth", "on"), "live_vs_on": count("live", "on"), "live_vs_enabled": count("live", "enabled"),
           "anyBlocked_r5": sum(1 for s in rows if s["r5truth"]["ball"] or s["r5truth"]["club"]),
           "maxEyeErr": max(s["eyeErr"] for s in rows), "maxBallMove": max(s["ballMove"] for s in rows),
           "console": {"server": st.problems("Server"), "client": st.problems("Client")}}
    print(json.dumps(res))
finally:
    res["rows"] = rows
    json.dump(res, open(os.path.join(out, "h6_wheel_r6%s.json" % ("_mixed" if "--mixed" in sys.argv else "")), "w"), indent=1)
    st.stop_play(); set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False})
