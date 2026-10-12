#!/usr/bin/env python3
"""Round 6 check 4: the new wrist card (WristFace Top, canvas 1024x784, AlwaysOnTop off) on both wrists.
Measures part size and aspect, every GUI element inside the canvas, TextFits, text height on screen and in angle at the
eye, and whether the bracer mesh hides any part of the card (rays from the eye with the client bracer copy made
queryable for the probe only, plus clearance of the card plane over the bracer along the face normal).
Read-only: SimulateVR Play session, pointer clicks only, attributes restored."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "tools")))
from run_playtests import Studio, set_edit_attrs  # noqa: E402
from menu_shots import pointer, menu  # noqa: E402
from ui_shots import capture  # noqa: E402
from wrist_sim import LEVEL_HEAD  # noqa: E402
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'round5', 'scripts')))
from r5_wrist import SWING  # noqa: E402

MEASURE = r"""
local HS = game:GetService('HttpService')
local pl = game.Players.LocalPlayer
local cam = workspace.CurrentCamera
local gui
for _, g in pl.PlayerGui:GetChildren() do
  if g:IsA('SurfaceGui') and g.Adornee and g.Adornee.Name == 'WristFace' then gui = g end
end
assert(gui, 'wrist SurfaceGui missing')
local p = gui.Adornee
local CW, CH = gui.CanvasSize.X, gui.CanvasSize.Y
local top = gui.Face == Enum.NormalId.Top
local W = top and p.Size.Z or p.Size.X
local H = top and p.Size.X or p.Size.Y
local n = p.CFrame.UpVector
local c = p.Position + n * (p.Size.Y / 2)
local targets = HS:JSONDecode(%s)
assert(#targets == 2, 'need both wrist button targets')
-- pick the canvas->world axes (u along +-Z, v along +-X of the part) that put the buttons where VRPointer says they are
local best, bestErr
for _, su in {1, -1} do for _, sv in {1, -1} do
  local U, V = p.CFrame.LookVector * -su, p.CFrame.RightVector * sv
  local err = 0
  for _, t in targets do
    local w = c + U * (t.u / CW - 0.5) * W + V * (t.v / CH - 0.5) * H
    err += (w - Vector3.new(t.world[1], t.world[2], t.world[3])).Magnitude
  end
  if not bestErr or err < bestErr then best, bestErr = {U = U, V = V}, err end
end end
local function world(u, v) return c + best.U * (u / CW - 0.5) * W + best.V * (v / CH - 0.5) * H end
local eye = cam.CFrame.Position
local vp = cam.ViewportSize
local function px(a, b)
  local A = cam:WorldToViewportPoint(a) local B = cam:WorldToViewportPoint(b)
  return (Vector2.new(A.X, A.Y) - Vector2.new(B.X, B.Y)).Magnitude
end
local function ang(a, b) return math.deg(math.acos(math.clamp((a - eye).Unit:Dot((b - eye).Unit), -1, 1))) end
-- bracer parts (client copy in the camera), made queryable for the probe only
local bracer, saved = {}, {}
for _, m in cam:GetChildren() do
  if m:IsA('Model') then
    for _, d in m:GetDescendants() do
      if d:IsA('BasePart') and d ~= p and p:IsDescendantOf(m) then
        table.insert(bracer, d) saved[d] = d.CanQuery
      end
    end
  end
end
local fid = {}
for _, b in bracer do b.CanQuery = true fid[b.Name] = b:IsA('MeshPart') and b.CollisionFidelity.Name or b.ClassName end
local rp = RaycastParams.new() rp.FilterType = Enum.RaycastFilterType.Include rp.FilterDescendantsInstances = bracer
local function hidden(w)
  local d = w - eye
  local h = workspace:Raycast(eye, d.Unit * (d.Magnitude - 0.0005), rp)
  return h and h.Instance.Name or nil
end
local function clearance(w)
  -- distance from the card plane down to the bracer under (or above) this point, along the face normal
  local from = w + n * 0.2
  local h = workspace:Raycast(from, -n * 0.4, rp)
  return h and (0.2 - h.Distance) or nil  -- > 0: card is above the bracer surface by this much
end
local elems, outside, notFit, occluded = {}, {}, {}, {}
local origin = gui.AbsolutePosition
local probes = 0
for _, d in gui:GetDescendants() do
  if d:IsA('GuiObject') and d.Visible then
    local a = d.AbsolutePosition - origin
    local s = d.AbsoluteSize
    local r = {name = d.Name, class = d.ClassName, x = a.X, y = a.Y, w = s.X, h = s.Y}
    if a.X < -0.5 or a.Y < -0.5 or a.X + s.X > CW + 0.5 or a.Y + s.Y > CH + 0.5 then table.insert(outside, d.Name) end
    if d:IsA('TextLabel') or d:IsA('TextButton') then
      r.text, r.fits, r.textSize, r.bounds = d.Text, d.TextFits, d.TextSize, {d.TextBounds.X, d.TextBounds.Y}
      if d.Text ~= '' and (not d.TextFits or d.TextBounds.X > s.X + 0.5) then table.insert(notFit, d.Name) end
      local cx, cy = a.X + s.X / 2, a.Y + s.Y / 2
      local th = d.TextBounds.Y
      local t0, t1 = world(cx, cy - th / 2), world(cx, cy + th / 2)
      r.screenPx = px(t0, t1)
      r.deg = ang(t0, t1)
      r.mm = (t1 - t0).Magnitude * 300
    end
    local pts = {{a.X + 2, a.Y + 2}, {a.X + s.X - 2, a.Y + 2}, {a.X + 2, a.Y + s.Y - 2}, {a.X + s.X - 2, a.Y + s.Y - 2}, {a.X + s.X / 2, a.Y + s.Y / 2}}
    for _, q in pts do
      probes += 1
      local hit = hidden(world(q[1], q[2]))
      if hit then table.insert(occluded, d.Name .. '@' .. math.floor(q[1]) .. ',' .. math.floor(q[2]) .. ':' .. hit) end
    end
    table.insert(elems, r)
  end
end
-- clearance grid over the whole canvas (17 x 13)
local minClr, minAt, gridHidden, gridN = math.huge, nil, 0, 0
local negClr = {}
for i = 0, 16 do for j = 0, 12 do
  local u, v = i / 16 * CW, j / 12 * CH
  local w = world(u, v)
  local cl = clearance(w)
  if cl and cl < minClr then minClr, minAt = cl, {u, v} end
  if cl and cl < 0 then table.insert(negClr, {u, v, cl}) end
  gridN += 1
  if hidden(w) then gridHidden += 1 end
end end
for b, q in saved do b.CanQuery = q end
local corners = {world(0, 0), world(CW, 0), world(CW, CH), world(0, CH)}
local cpx = {}
for _, w in corners do local s = cam:WorldToViewportPoint(w) table.insert(cpx, {s.X, s.Y}) end
return HS:JSONEncode({
  part = p:GetFullName(), size = {p.Size.X, p.Size.Y, p.Size.Z}, widthStuds = W, heightStuds = H, canvas = {CW, CH},
  partAspect = W / H, canvasAspect = CW / CH, alwaysOnTop = gui.AlwaysOnTop, zOffset = gui.ZOffset, face = gui.Face.Name,
  lightInfluence = gui.LightInfluence, brightness = gui.Brightness, sizingMode = gui.SizingMode.Name,
  axisFitErr = bestErr, eyeDist = (c - eye).Magnitude, faceToEyeDeg = math.deg(math.acos(math.clamp(n:Dot((eye - c).Unit), -1, 1))),
  viewport = {vp.X, vp.Y}, fov = cam.FieldOfView, cardScreenCorners = cpx,
  elements = elems, outside = outside, notFit = notFit, occludedProbes = occluded, probes = probes,
  gridHidden = gridHidden, gridN = gridN, minClearanceStuds = minClr ~= math.huge and minClr or nil, minClearanceAt = minAt, negClearance = negClr,
  bracerParts = #bracer, bracerFidelity = fid, handed = pl:GetAttribute('Handedness')})
"""

LOOK = r"""
local h = game.ReplicatedStorage.VRDebug.Head
local cam = workspace.CurrentCamera
local p
for _, g in game.Players.LocalPlayer.PlayerGui:GetChildren() do
  if g:IsA('SurfaceGui') and g.Adornee and g.Adornee.Name == 'WristFace' then p = g.Adornee end
end
local origin = cam.CFrame * h.Value:Inverse()
h.Value = origin:Inverse() * CFrame.lookAt(cam.CFrame.Position, p.Position)
return 'ok'
"""


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    st = Studio()
    st.stop_play()
    set_edit_attrs(st, {"GolfTestMode": False, "SimulateVR": True, "PBInStudio": False})
    hand = "RightHand"
    res = {}

    def wait_for(fn, label, seconds=6):
        t = time.monotonic() + seconds
        while time.monotonic() < t:
            v = fn()
            if v:
                return v
            time.sleep(0.1)
        raise AssertionError(label)

    def click(name, wrist=False):
        if wrist:
            pointer(st, "wrist", True)
            wait_for(lambda: pointer(st, "state")["wrist"].get("alpha", 0) > 0.6, "wrist up")
        t = wait_for(lambda: next((t for t in pointer(st, "targets") or [] if t["name"] == name), None), "target " + name)
        pointer(st, "aim", {"hand": hand, "point": t["world"]})
        wait_for(lambda: pointer(st, "state")["pointer"].get("button") == name, "hover " + name)
        pointer(st, "trigger", hand)
        time.sleep(0.8)
        m = menu(st, "state")
        print("clicked", name, hand, (json.loads(m) if isinstance(m, str) else m).get("page"), flush=True)
        if wrist:
            pointer(st, "wrist", False)
            time.sleep(0.7)

    def measure(label):
        st.luau(LEVEL_HEAD, "Client")
        pointer(st, "wrist", True)
        wait_for(lambda: pointer(st, "state")["wrist"].get("alpha", 0) > 0.99, "wrist shown")
        time.sleep(0.3)
        print("targets", [t["name"] for t in pointer(st, "targets")], flush=True)
        targets = [{"u": u, "v": 720, "world": t["world"]} for t in pointer(st, "targets") for (nm, u) in (("WristMenu", 296), ("WristScores", 728)) if t["name"] == nm]
        r = {"natural": json.loads(st.luau(MEASURE % json.dumps(json.dumps(targets)), "Client"))}
        capture(st, os.path.join(out, label + "_natural.png"))
        st.luau(LOOK, "Client")
        time.sleep(0.4)
        r["lookedAt"] = json.loads(st.luau(MEASURE % json.dumps(json.dumps(targets)), "Client"))
        capture(st, os.path.join(out, label + "_lookat.png"))
        st.luau("workspace.CurrentCamera.FieldOfView = 22 return true", "Client")
        time.sleep(0.4)
        capture(st, os.path.join(out, label + "_zoom.png"))
        st.luau("workspace.CurrentCamera.FieldOfView = 70 return true", "Client")
        st.luau(LEVEL_HEAD, "Client")
        pointer(st, "wrist", False)
        time.sleep(0.7)
        res[label] = r
        n = r["natural"]
        print(label, json.dumps({k: n.get(k) for k in ("bracerParts", "axisFitErr", "size", "partAspect", "canvasAspect", "alwaysOnTop", "outside", "notFit", "occludedProbes", "gridHidden", "minClearanceStuds", "eyeDist", "faceToEyeDeg")}), flush=True)

    try:
        st.start_play()
        time.sleep(12)
        st.luau(LEVEL_HEAD, "Client")
        click("Play")
        click("PlayCourse")
        time.sleep(1.5)
        res["titleTargetsBeforeStroke"] = None
        res["swing"] = json.loads(st.luau(SWING % ("4.0", "0"), "Client", timeout=90))
        print("swing", res["swing"], flush=True)
        st.luau(LEVEL_HEAD, "Client")
        time.sleep(1.0)
        measure("left_wrist")
        click("WristMenu", True)
        click("Settings")
        click("HandLeft")
        hand = "LeftHand"
        click("Back")
        click("Resume")
        time.sleep(0.8)
        measure("right_wrist")
        res["console"] = {"server": st.problems("Server"), "client": st.problems("Client")}
    finally:
        with open(os.path.join(out, "wristcard.json"), "w") as fh:
            json.dump(res, fh, indent=1)
        st.stop_play()
        set_edit_attrs(st, {"SimulateVR": False, "GolfTestMode": False, "PBInStudio": None})


if __name__ == "__main__":
    main()
