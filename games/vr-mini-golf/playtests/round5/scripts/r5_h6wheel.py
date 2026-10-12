#!/usr/bin/env python3
"""Round 5: H6 mill wheel ball X-ray in VR with the truth ray to the ball's LIVE position (the wheel moves the ball)."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "tools")))
from run_playtests import Studio, set_edit_attrs  # noqa: E402
import r5_xray as X  # noqa: E402
out = sys.argv[1]
POSE = "return game:GetService('HttpService'):JSONEncode(game.Players.LocalPlayer.PlayerScripts:WaitForChild('GolfPointerDebug', 10):Invoke('pose', game:GetService('HttpService'):JSONDecode(%s)))"
LIVE = r"""
local head = Vector3.new(%f, %f, %f)
local CO = require(game.ReplicatedStorage.Golf.CameraOcclusion)
local rp = RaycastParams.new() rp.FilterType = Enum.RaycastFilterType.Exclude rp.CollisionGroup = CO.CAMERA_GROUP rp.IgnoreWater = true
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
local res = {}
local x = game.Players.LocalPlayer.PlayerScripts:FindFirstChild('GolfXRayDebug')
for i = 1, 60 do
  local b = workspace.Balls:GetChildren()[1].Position
  local s = x:Invoke()
  table.insert(res, {truth = blocked(head, b), on = s.ball.on, moved = (b - Vector3.new(%f, %f, %f)).Magnitude})
  task.wait(0.15)
end
return game:GetService('HttpService'):JSONEncode(res)
"""
st = Studio(); st.stop_play()
set_edit_attrs(st, {"GolfTestMode": True, "SimulateVR": True})
try:
    st.start_play(); time.sleep(12)
    X.place(st, 6, (37.5, 30.0, -63.2))
    f = json.loads(st.luau(X.FIND_HEAD % json.dumps("mill"), "Client"))
    head, look, club = f["head"], f["ball"], f["club"]
    st.luau(POSE % json.dumps(json.dumps({"head": head, "look": look, "club": [club[0], look[1] - 0.015, club[2]], "face": [club[0] - look[0], 0, club[2] - look[2]]})), "Client")
    time.sleep(0.5)
    rows = json.loads(st.luau(LIVE % tuple(head + look), "Client", timeout=60))
    agree = sum(1 for r in rows if bool(r["on"]) == r["truth"])
    # allow the 0.25 s fade: count disagreements right after a truth change as transitions
    trans = sum(1 for i, r in enumerate(rows) if bool(r["on"]) != r["truth"] and i > 0 and rows[i - 1]["truth"] != r["truth"])
    res = {"samples": len(rows), "blocked": sum(r["truth"] for r in rows), "agree": agree, "disagree_at_transition": trans, "maxBallMove": max(r["moved"] for r in rows), "rows": rows,
           "console": {"server": st.problems("Server"), "client": st.problems("Client")}}
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}))
    json.dump(res, open(os.path.join(out, "h6_wheel_live.json"), "w"), indent=1)
finally:
    st.stop_play(); set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False})
