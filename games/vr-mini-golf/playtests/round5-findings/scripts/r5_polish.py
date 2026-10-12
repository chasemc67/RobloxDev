#!/usr/bin/env python3
"""Round 5: (a) H6 mill wheel X-ray in VR, polled until the wheel really blocks the sight line; (b) H9 pendulum near the
VR lens: head 0.8-1.5 studs from the lantern looking at a ball beyond -> glow parts within 3 studs must be hidden
(LTM 1) and their lights off; then 6 studs away -> restored. GolfTestMode + SimulateVR, temp only."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "tools")))
from run_playtests import Studio, set_edit_attrs  # noqa: E402
from ui_shots import capture  # noqa: E402
import r5_xray as X  # noqa: E402

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
POSE = "return game:GetService('HttpService'):JSONEncode(game.Players.LocalPlayer.PlayerScripts:WaitForChild('GolfPointerDebug', 10):Invoke('pose', game:GetService('HttpService'):JSONDecode(%s)))"
PEND = r"""
local m
for _, d in workspace.Course.Hole9:GetDescendants() do if d:IsA('Model') and d.Name == 'Mover_lantern_pendulum' then m = d end end
local glow = {}
for _, d in m:GetDescendants() do
  if d:IsA('BasePart') then
    local lights = 0
    for _, c in d:GetChildren() do if c:IsA('Light') then lights += 1 end end
    if d.Material == Enum.Material.Neon or lights > 0 then table.insert(glow, d) end
  end
end
local c = Vector3.zero
for _, g in glow do c += g.Position end
c /= math.max(#glow, 1)
local info = {}
for _, g in glow do
  local on = 0
  for _, l in g:GetChildren() do if l:IsA('Light') and l.Enabled then on += 1 end end
  table.insert(info, {name = g.Name, ltm = g.LocalTransparencyModifier, lightsOn = on, pos = {g.Position.X, g.Position.Y, g.Position.Z}})
end
local blk
for _, d in m:GetDescendants() do if d:IsA('BasePart') and d.Name == 'Blocker' then blk = d end end
return game:GetService('HttpService'):JSONEncode({centre = {c.X, c.Y, c.Z}, glow = info, n = #glow, cam = {workspace.CurrentCamera.CFrame.X, workspace.CurrentCamera.CFrame.Y, workspace.CurrentCamera.CFrame.Z}})
"""
st = Studio()
st.stop_play()
set_edit_attrs(st, {"GolfTestMode": True, "SimulateVR": True})
res = {}
try:
    st.start_play(); time.sleep(12)
    # (a) H6 mill wheel
    X.place(st, 6, (37.5, 30.0, -63.2))
    found = json.loads(st.luau(X.FIND_HEAD % json.dumps("mill"), "Client"))
    head, look, club = found["head"], found["ball"], found["club"]
    away = [club[0] - look[0], 0, club[2] - look[2]]
    st.luau(POSE % json.dumps(json.dumps({"head": head, "look": look, "club": [club[0], look[1] - 0.015, club[2]], "face": away})), "Client")
    rows = []
    for i in range(40):
        time.sleep(0.25)
        s = json.loads(st.luau(X.STATE % tuple(head + look + club), "Client"))
        rows.append({"truth": s["truth"], "xray": s["xray"], "occ": s["occluders"], "occFaded": s["occludersFaded"]})
        if s["truth"]["ball"] and s["truth"]["club"] and not res.get("h6_blocked_shot"):
            capture(st, os.path.join(out, "h6_mill_wheel_vr_blocked.png"))
            res["h6_blocked_shot"] = s
    agree = sum(1 for r in rows if bool(r["xray"]["ball"]["on"]) == r["truth"]["ball"] and bool(r["xray"]["club"]["on"]) == r["truth"]["club"])
    res["h6_mill_wheel_vr"] = {"samples": len(rows), "blocked_samples": sum(r["truth"]["ball"] for r in rows), "outline_agrees": agree, "rows": rows}
    print("h6", agree, "/", len(rows), "blocked", res["h6_mill_wheel_vr"]["blocked_samples"])
    # (b) H9 pendulum near the lens
    p = json.loads(st.luau(PEND, "Client"))
    c = p["centre"]
    # a ball on the felt 5 studs from the pendulum (search the felt around it)
    spot = st.luau("""local c = Vector3.new(%f, %f, %f)
local CS = game:GetService('CollectionService')
local rp = RaycastParams.new() rp.FilterType = Enum.RaycastFilterType.Include rp.FilterDescendantsInstances = CS:GetTagged('GolfSurface')
for _, r in {5, 4, 6, 3} do for k = 0, 11 do
  local a = math.rad(k * 30)
  local o = c + Vector3.new(math.cos(a) * r, 6, math.sin(a) * r)
  local h = workspace:Raycast(o, Vector3.new(0, -20, 0), rp)
  if h and h.Instance:IsDescendantOf(workspace.Course.Hole9) and h.Normal.Y > 0.99 then return string.format('%%.3f,%%.3f,%%.3f', h.Position.X, h.Position.Y, h.Position.Z) end
end end
return 'none'""" % tuple(c), "Client")
    print("pend spot", spot)
    bx, by, bz = [float(v) for v in spot.split(",")]
    st.api("hitat", 9, spot, "0.01,0", timeout=60); time.sleep(1.0)
    ball = json.loads(st.luau("local b = workspace.Balls:GetChildren()[1].Position return game:GetService('HttpService'):JSONEncode({b.X, b.Y, b.Z})", "Client"))
    res["pendulum"] = []
    for dist in (0.8, 1.5, 6.0):
        p = json.loads(st.luau(PEND, "Client"))
        c = p["centre"]
        d = [c[0] - ball[0], 0, c[2] - ball[2]]
        n = (d[0] ** 2 + d[2] ** 2) ** 0.5
        h = [c[0] + d[0] / n * dist, c[1], c[2] + d[2] / n * dist]
        st.luau(POSE % json.dumps(json.dumps({"head": h, "look": ball})), "Client")
        time.sleep(0.25)
        p = json.loads(st.luau(PEND, "Client"))
        shot = "h9_pendulum_vr_head_%.1fstuds.png" % dist
        capture(st, os.path.join(out, shot))
        g = p["glow"]
        r = {"dist": dist, "glowParts": len(g), "hidden": sum(1 for x in g if x["ltm"] >= 0.99), "lightsOn": sum(x["lightsOn"] for x in g), "glow": g, "shot": shot, "head": h}
        res["pendulum"].append(r)
        print("pend", dist, r["glowParts"], "hidden", r["hidden"], "lightsOn", r["lightsOn"])
    res["console"] = {"server": st.problems("Server"), "client": st.problems("Client")}
    print(json.dumps(res["console"]))
finally:
    json.dump(res, open(os.path.join(out, "polish.json"), "w"), indent=1)
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": False})
