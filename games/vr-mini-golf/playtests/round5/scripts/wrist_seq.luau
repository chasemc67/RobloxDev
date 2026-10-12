-- Round 5 extra wrist sequences (SimulateVR client). Drives VRDebug Head / hands frame by frame (world poses converted
-- with the sim origin = camera * Head:Inverse()), polls GolfPointerDebug "state" every frame and logs show events per
-- labelled segment. SEGMENTS (JSON) is substituted by the runner.
local HS = game:GetService('HttpService')
local RunService = game:GetService('RunService')
local RS = game:GetService('ReplicatedStorage')
local dbg = RS:WaitForChild('VRDebug')
local hook = game.Players.LocalPlayer.PlayerScripts:WaitForChild('GolfPointerDebug')
local cam = workspace.CurrentCamera
local segs = HS:JSONDecode(SEGMENTS)
local OFF = OFFHAND -- "LeftHand" / "RightHand"
local CLUB = OFF == 'LeftHand' and 'RightHand' or 'LeftHand'
local left = OFF == 'LeftHand'
local side = left and -1 or 1

local function flat(v) return Vector3.new(v.X, 0, v.Z) end
local function base()
  return cam.CFrame * dbg.Head.Value:Inverse()
end
local B = base()
local function setW(name, cf) dbg[name].Value = B:Inverse() * cf end

local ballPart
for _, b in (workspace:FindFirstChild('Balls') or workspace):GetChildren() do
  if b:IsA('BasePart') then ballPart = b end
end
local ballPos = ballPart and ballPart.Position or cam.CFrame.Position - Vector3.new(0, 5, 0)
local groundY = ballPos.Y - (ballPart and ballPart.Size.Y / 2 or 0)
local h0 = cam.CFrame
local baseLook = flat(h0.LookVector).Unit
local baseRight = baseLook:Cross(Vector3.yAxis)
-- stand 4 studs from the ball for non-stance segments
local eye = Vector3.new(ballPos.X, groundY + 5.4, ballPos.Z) - baseLook * 4.5 + baseRight * 1.5

local function headLook(pos, yaw, pitch)
  local d = CFrame.fromAxisAngle(Vector3.yAxis, math.rad(yaw)):VectorToWorldSpace(baseLook)
  d = d * math.cos(math.rad(pitch)) + Vector3.yAxis * math.sin(math.rad(pitch))
  local cf = CFrame.lookAt(pos, pos + d)
  setW('Head', cf)
  return cf
end
-- same watch pose as VRControls (forearm across the body, back of the wrist up at the eyes)
local function watchPose(headW, yawDeg, tiltDeg)
  local flatLook = flat(headW.LookVector)
  flatLook = flatLook.Magnitude > 1e-3 and flatLook.Unit or Vector3.new(0, 0, -1)
  flatLook = CFrame.fromAxisAngle(Vector3.yAxis, math.rad(yawDeg or 0)):VectorToWorldSpace(flatLook)
  local flatRight = flatLook:Cross(Vector3.yAxis)
  local wristPos = headW.Position + flatLook * 1.4 - Vector3.new(0, 0.55, 0) + flatRight * (0.15 * side)
  local back = (headW.Position - wristPos).Unit
  if tiltDeg and tiltDeg ~= 0 then
    back = CFrame.fromAxisAngle(flatRight, math.rad(tiltDeg)):VectorToWorldSpace(back)
  end
  local right = back * (left and -1 or 1)
  local look = flatRight * -side
  look = (look - right * look:Dot(right)).Unit
  local up = right:Cross(look)
  local rot = CFrame.fromMatrix(Vector3.zero, right, up)
  local handPos = wristPos - rot:VectorToWorldSpace(Vector3.new(0, -0.12, 0.33))
  return CFrame.new(handPos) * rot, wristPos
end
local function hang(headW, which)
  local sd = which == 'RightHand' and 1 or -1
  local fl = flat(headW.LookVector).Unit
  local fr = fl:Cross(Vector3.yAxis)
  local rest = headW.Position + fr * (0.6 * sd) - Vector3.new(0, 2.6, 0)
  return CFrame.lookAt(rest, rest + fl)
end
local function club(p, face)
  hook:Invoke('pose', { club = { p.X, p.Y, p.Z }, face = { face.X, face.Y, face.Z } })
end
local function clubAtSide(hw)
  local fl = flat(hw.LookVector).Unit
  local p = Vector3.new(hw.X, groundY + 0.3, hw.Z) + fl:Cross(Vector3.yAxis) * (1.0 * -side) + fl * 0.3
  club(p, fl)
end

local results = {}
local wasShown = hook:Invoke('state').wrist.shown
for i, s in segs do
  local t0 = os.clock()
  local shows, firstShow, frames, maxBlocked = 0, nil, 0, {}
  local minFace, minGaze = 999, 999
  local wristPt
  while os.clock() - t0 < s.dur do
    local t = os.clock() - t0
    local hw
    if s.kind == 'down' then
      hw = headLook(eye, s.yaw or 0, s.pitch or -10)
      clubAtSide(hw)
      setW(OFF, hang(hw, OFF))
    elseif s.kind == 'watch' then
      hw = headLook(eye, s.yaw or 0, s.pitch or -18)
      clubAtSide(hw)
      setW(OFF, (watchPose(hw, s.wristYaw, s.tilt)))
    elseif s.kind == 'lookat' then
      -- head turned so the wrist sits gazeOff deg off the gaze centre (horizontal)
      local hw0 = headLook(eye, 0, -18)
      local cf, wp = watchPose(hw0, 0, s.tilt)
      local dir = (wp - eye).Unit
      dir = CFrame.fromAxisAngle(Vector3.yAxis, math.rad(s.gazeOff or 0)):VectorToWorldSpace(dir)
      hw = CFrame.lookAt(eye, eye + dir)
      setW('Head', hw)
      clubAtSide(hw)
      setW(OFF, cf)
    elseif s.kind == 'swing' then
      -- practice swing beside the head with the wrist raised and looked at (worst case); speed s.speed studs/s peak
      hw = headLook(eye, 0, -18)
      local spot = Vector3.new(eye.X, groundY + 0.3, eye.Z) + baseLook * 1.3
      local amp = s.amp or 1.2
      local w = (s.speed or 6) / amp
      club(spot + baseRight * (amp * math.sin(w * t)), baseRight)
      setW(OFF, (watchPose(hw)))
    elseif s.kind == 'stance' then
      -- lining up a putt: standing over the ball, putter head s.back studs behind it, small waggle, looking at the wrist
      local stand = Vector3.new(ballPos.X, groundY + 5.1, ballPos.Z) - baseLook * 1.6
      hw = headLook(stand, 0, s.lookWrist and -20 or -60)
      local back = (s.back or 0.6) + (s.waggle or 0.1) * math.sin(t * 3)
      club(Vector3.new(ballPos.X, groundY + 0.3, ballPos.Z) - baseRight * back, baseRight)
      setW(OFF, (watchPose(hw)))
    end
    RunService.RenderStepped:Wait()
    frames += 1
    local st = hook:Invoke('state').wrist
    if st.faceDeg then
      minFace = math.min(minFace, st.faceDeg)
      minGaze = math.min(minGaze, st.gazeDeg)
    end
    if st.blocked then maxBlocked[st.blocked] = (maxBlocked[st.blocked] or 0) + 1 end
    if st.shown and not wasShown then
      shows += 1
      firstShow = firstShow or math.floor((os.clock() - t0) * 1000)
    end
    wasShown = st.shown
  end
  table.insert(results, { i = i, name = s.name, kind = s.kind, expect = s.expect, dur = s.dur, frames = frames, shows = shows, firstShowMs = firstShow, minFaceDeg = math.floor(minFace + 0.5), minGazeDeg = math.floor(minGaze + 0.5), blocked = maxBlocked, shownAtEnd = wasShown })
end
return HS:JSONEncode(results)
