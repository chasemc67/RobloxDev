-- VRControls: Walkabout-style VR putting at real-world scale (1 stud = 0.3 m, HeadScale 1).
--   * Room-scale: the camera is a floor-level playspace origin; your real head/hands are tracked on top of it.
--   * The putter shaft extends out of the FRONT of the club-hand controller (point the controller at the
--     ground like the top of a putter grip). Length auto-fits your height and stretches a few cm to reach
--     the ground. The head slides along the floor instead of passing through it.
--   * The putter face velocity at contact becomes the ball velocity.
--
-- Controls (modelled on Walkabout Mini Golf):
--   Trigger (either hand) ...... warp to your ball
--   Right stick left/right ..... snap turn
--   Right stick forward ........ aim teleport arc, release to teleport
--   Right stick back ........... rewind ball to where your last shot started
--   Left stick ................. walk
--   Grip (club hand) ........... hold to make the putter solid (only when Config.VRGripToPutt = true)
--   B / Y ...................... scorecard     A ... re-fit club (point it straight down first)
--   X .......................... swap hands
--
-- For testing without a headset set workspace attribute "SimulateVR" = true before playing. Poses are then read
-- from CFrameValues in ReplicatedStorage.VRDebug (Head/LeftHand/RightHand, relative to the floor origin),
-- buttons can be pressed by firing ReplicatedStorage.VRDebug.Button (KeyCode) and sticks set with
-- ReplicatedStorage.VRDebug.Stick (KeyCode, Vector2).
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local VRService = game:GetService("VRService")
local HapticService = game:GetService("HapticService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage:WaitForChild("Golf"):WaitForChild("Config"))

local player = Players.LocalPlayer
local R = Config.BallRadius

local VR = {}

-- real-ish blade putter: 3.3 cm thick, 3.3 cm tall, 12.6 cm toe-to-heel
local HEAD_SIZE = Vector3.new(0.11, 0.11, 0.42) -- X = face thickness, Y = height, Z = toe-to-heel
local HIT_COOLDOWN = 0.6
local REACH_EXTRA = 0.5 -- the shaft may stretch this much (15 cm) to keep the head on the ground
local TELEPORT_SPEED = 22 -- ~6.5 m max reach
local TELEPORT_GRAVITY = Vector3.new(0, -22, 0)

local function flat(v: Vector3)
	return Vector3.new(v.X, 0, v.Z)
end

local function yawOnly(cf: CFrame)
	local look = flat(cf.LookVector)
	if look.Magnitude < 1e-3 then
		look = Vector3.new(0, 0, -1)
	end
	return CFrame.lookAt(Vector3.zero, look.Unit)
end

-- Shaft along the controller's pointing direction, face normal = controller right, toe = controller up.
local function defaultClubOffset()
	return CFrame.Angles(math.rad(Config.VRClubAngle or 0), 0, 0)
end

function VR.start(Ball, HUD, simulate)
	local camera = workspace.CurrentCamera
	pcall(function()
		VRService.AutomaticScaling = Enum.VRScaling.Off
	end)
	camera.HeadScale = 1
	camera.HeadLocked = true
	camera.CameraType = Enum.CameraType.Scriptable
	camera:GetPropertyChangedSignal("CameraType"):Connect(function()
		if camera.CameraType ~= Enum.CameraType.Scriptable then
			camera.CameraType = Enum.CameraType.Scriptable
		end
	end)

	------------------------------------------------------------ tracking sources
	local debugFolder = simulate and ReplicatedStorage:WaitForChild("VRDebug")
	local function rawUserCFrame(which: Enum.UserCFrame): CFrame
		if simulate then
			local v = debugFolder:FindFirstChild(which.Name)
			return v and v.Value or CFrame.new()
		end
		return VRService:GetUserCFrame(which)
	end
	local function scaled(cf: CFrame)
		return cf.Rotation + cf.Position * camera.HeadScale
	end

	-- Offset from the tracking origin down to the real floor (studs, already scaled).
	local floorOffsetY = 0
	local function calibrateFloor()
		if simulate then
			floorOffsetY = 0
			return
		end
		if VRService:GetUserCFrameEnabled(Enum.UserCFrame.Floor) then
			floorOffsetY = scaled(VRService:GetUserCFrame(Enum.UserCFrame.Floor)).Position.Y
		else
			-- no floor info: if the head is near the origin height, the origin is probably at eye level
			local headY = scaled(VRService:GetUserCFrame(Enum.UserCFrame.Head)).Position.Y
			floorOffsetY = headY < 2.5 and (headY - 5.4) or 0
		end
	end
	calibrateFloor()
	VRService.UserCFrameEnabled:Connect(function(which)
		if which == Enum.UserCFrame.Floor then
			calibrateFloor()
		end
	end)

	-- origin: world CFrame (position + yaw) of the real-world floor centre
	local origin = CFrame.new(0, 1, -6)
	local teleportedThisFrame = true

	local function localPose(which)
		return CFrame.new(0, -floorOffsetY, 0) * scaled(rawUserCFrame(which))
	end
	local function worldPose(which)
		return origin * localPose(which)
	end

	------------------------------------------------------------ raycasting
	local clubRay = RaycastParams.new()
	clubRay.CollisionGroup = "GolfClub" -- ignores balls and characters
	clubRay.FilterType = Enum.RaycastFilterType.Exclude
	clubRay.FilterDescendantsInstances = { camera }

	local function groundY(pos: Vector3, fromAbove: number)
		local hit = workspace:Raycast(pos + Vector3.new(0, fromAbove, 0), Vector3.new(0, -(fromAbove + 30), 0), clubRay)
		return hit and hit.Position.Y
	end

	-- The player's floor only follows walkable surfaces (felt, ramps, grass) - stepping over a
	-- wall shouldn't bump your view up and down.
	local floorRay = RaycastParams.new()
	floorRay.FilterType = Enum.RaycastFilterType.Include
	local walkable = {}
	local WALKABLE_NAMES = { Felt = true, CupPlate = true, Ramp = true, Base = true, Baseplate = true, SpawnLocation = true }
	for _, d in workspace:GetDescendants() do
		if d:IsA("BasePart") and WALKABLE_NAMES[d.Name] then
			table.insert(walkable, d)
		end
	end
	floorRay.FilterDescendantsInstances = walkable
	local walkableSet = {}
	for _, p in walkable do
		walkableSet[p] = true
	end
	local function floorY(pos: Vector3, fromAbove: number)
		local hit = workspace:Raycast(pos + Vector3.new(0, fromAbove, 0), Vector3.new(0, -(fromAbove + 30), 0), floorRay)
		return hit and hit.Position.Y
	end

	------------------------------------------------------------ putter model
	local putter = Instance.new("Model")
	putter.Name = "VRPutter"
	local function piece(name, size, color, material, shape, parent)
		local p = Instance.new("Part")
		p.Name = name
		p.Size = size
		p.Color = color
		p.Material = material or Enum.Material.Metal
		if shape then
			p.Shape = shape
		end
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.CastShadow = false
		p.Parent = parent or putter
		return p
	end
	local grip = piece("Grip", Vector3.new(0.1, 0.1, 0.75), Color3.fromRGB(30, 30, 30), Enum.Material.Rubber)
	local shaft = piece("Shaft", Vector3.new(0.035, 0.035, 2), Color3.fromRGB(205, 205, 210))
	local head = piece("Head", HEAD_SIZE, Color3.fromRGB(70, 75, 85))
	head.CastShadow = true
	local sight = piece("Sight", Vector3.new(0.012, 0.004, 0.12), Color3.fromRGB(255, 255, 255), Enum.Material.Neon)
	putter.Parent = camera

	-- teleport arc visuals
	local arcFolder = Instance.new("Folder")
	arcFolder.Name = "TeleportArc"
	arcFolder.Parent = camera
	local arcDots = {}
	for i = 1, 24 do
		arcDots[i] = piece("Dot", Vector3.one * 0.08, Color3.fromRGB(120, 220, 255), Enum.Material.Neon, Enum.PartType.Ball, arcFolder)
		arcDots[i].Transparency = 1
	end
	local arcTarget = piece("Target", Vector3.new(0.04, 1.6, 1.6), Color3.fromRGB(120, 220, 255), Enum.Material.Neon, Enum.PartType.Cylinder, arcFolder)
	arcTarget.Transparency = 1

	local clubOffset = defaultClubOffset()
	local clubLength = 2.6 -- replaced by the height-based fit below
	local clubFitted = false
	local dominant = Enum.UserCFrame.RightHand

	------------------------------------------------------------ helpers
	local function motorFor(hand)
		return hand == Enum.UserCFrame.RightHand and Enum.VibrationMotor.RightHand or Enum.VibrationMotor.LeftHand
	end
	local function haptic(strength, duration, hand)
		if simulate then
			return
		end
		local motor = motorFor(hand or dominant)
		pcall(function()
			HapticService:SetMotor(Enum.UserInputType.Gamepad1, motor, strength)
		end)
		task.delay(duration, function()
			pcall(function()
				HapticService:SetMotor(Enum.UserInputType.Gamepad1, motor, 0)
			end)
		end)
	end

	-- Walkabout-style auto fit: club length from the player's eye height (works standing or seated).
	local function autoFitClub()
		local eye = localPose(Enum.UserCFrame.Head).Position.Y
		if eye < 2 then
			return
		end
		clubLength = math.clamp(eye * 0.47, 1.6, 3.3)
		clubFitted = true
	end

	-- Moves the playspace so the real head ends up at `headTarget` (XZ) looking along `facing`.
	local function placeHead(headTarget: Vector3, facing: Vector3?, floorHeight: number?)
		local headLocal = localPose(Enum.UserCFrame.Head)
		local rot = origin.Rotation
		if facing then
			local localYaw = yawOnly(headLocal)
			local wantYaw = CFrame.lookAt(Vector3.zero, flat(facing).Unit)
			rot = wantYaw * localYaw:Inverse()
		end
		local offset = rot * flat(headLocal.Position)
		local y = floorHeight or floorY(headTarget, 3) or origin.Y
		origin = CFrame.new(headTarget.X - offset.X, y, headTarget.Z - offset.Z) * rot
		teleportedThisFrame = true
	end

	-- Walkabout's "warp to ball": stand beside the ball in a putting stance, target on your lead side.
	local function warpToBall(ballPos: Vector3?)
		if not Ball.ball then
			return
		end
		local bp = ballPos or Ball.ball.Position
		local toTarget = flat(Ball.getAimPoint(bp) - bp)
		if toTarget.Magnitude < 0.1 then
			toTarget = Vector3.new(0, 0, 1)
		end
		toTarget = toTarget.Unit
		local facing
		if dominant == Enum.UserCFrame.RightHand then
			facing = Vector3.new(-toTarget.Z, 0, toTarget.X)
		else
			facing = Vector3.new(toTarget.Z, 0, -toTarget.X)
		end
		local stand = bp - facing * Config.VRStanceDistance
		placeHead(stand, facing, bp.Y - R)
		if not clubFitted then
			autoFitClub()
		end
	end

	-- Manual re-fit: point the club straight down at the floor and press A.
	local function fitClub()
		local handCF = worldPose(dominant)
		local headPos = worldPose(Enum.UserCFrame.Head).Position
		local toe = flat(handCF.Position - headPos)
		if toe.Magnitude < 0.2 then
			toe = flat(handCF.UpVector)
		end
		if toe.Magnitude < 1e-3 then
			return
		end
		toe = toe.Unit
		local back = Vector3.yAxis -- shaft points straight down
		local right = toe:Cross(back)
		local desired = CFrame.fromMatrix(Vector3.zero, right, toe, back)
		clubOffset = handCF.Rotation:Inverse() * desired
		local floor = groundY(handCF.Position, 0.5) or origin.Y
		clubLength = math.clamp(handCF.Position.Y - floor - HEAD_SIZE.Y / 2, 1.2, 4)
		clubFitted = true
		teleportedThisFrame = true -- the head jumps; don't treat that as a swing
		haptic(0.4, 0.15)
		HUD.message("Club fitted", Color3.fromRGB(180, 230, 255), 1.5)
	end

	local function switchHands()
		dominant = dominant == Enum.UserCFrame.RightHand and Enum.UserCFrame.LeftHand or Enum.UserCFrame.RightHand
		clubOffset = defaultClubOffset()
		teleportedThisFrame = true
		HUD.message(dominant == Enum.UserCFrame.RightHand and "Right-handed" or "Left-handed", Color3.new(1, 1, 1), 1.5)
	end

	------------------------------------------------------------ input
	local moveStick = Vector2.zero
	local actionStick = Vector2.zero -- right stick: turn / teleport / rewind
	local turnLatched = false
	local rewindLatched = false
	local aimingTeleport = false
	local teleportTarget: Vector3? = nil
	local gripHeld = { [Enum.UserCFrame.RightHand] = false, [Enum.UserCFrame.LeftHand] = false }

	local function onButtonDown(keyCode)
		if keyCode == Enum.KeyCode.ButtonR2 or keyCode == Enum.KeyCode.ButtonL2 then
			warpToBall(nil)
		elseif keyCode == Enum.KeyCode.ButtonR1 then
			gripHeld[Enum.UserCFrame.RightHand] = true
		elseif keyCode == Enum.KeyCode.ButtonL1 then
			gripHeld[Enum.UserCFrame.LeftHand] = true
		elseif keyCode == Enum.KeyCode.ButtonB or keyCode == Enum.KeyCode.ButtonY then
			if HUD.isFinalCardOpen() then
				HUD.playAgain()
			else
				HUD.toggleScorecard()
			end
		elseif keyCode == Enum.KeyCode.ButtonA then
			fitClub()
		elseif keyCode == Enum.KeyCode.ButtonX then
			switchHands()
		end
	end
	local function onButtonUp(keyCode)
		if keyCode == Enum.KeyCode.ButtonR1 then
			gripHeld[Enum.UserCFrame.RightHand] = false
		elseif keyCode == Enum.KeyCode.ButtonL1 then
			gripHeld[Enum.UserCFrame.LeftHand] = false
		end
	end
	local function onStick(keyCode, pos: Vector2)
		if keyCode == Enum.KeyCode.Thumbstick1 then
			moveStick = pos
		elseif keyCode == Enum.KeyCode.Thumbstick2 then
			actionStick = pos
		end
	end

	-- Buttons are handled even if a core script already bound them (e.g. jump on A).
	UserInputService.InputBegan:Connect(function(input)
		onButtonDown(input.KeyCode)
	end)
	UserInputService.InputEnded:Connect(function(input)
		onButtonUp(input.KeyCode)
		if input.KeyCode == Enum.KeyCode.Thumbstick1 or input.KeyCode == Enum.KeyCode.Thumbstick2 then
			onStick(input.KeyCode, Vector2.zero)
		end
	end)
	UserInputService.InputChanged:Connect(function(input)
		if input.KeyCode == Enum.KeyCode.Thumbstick1 or input.KeyCode == Enum.KeyCode.Thumbstick2 then
			onStick(input.KeyCode, Vector2.new(input.Position.X, input.Position.Y))
		end
	end)
	if simulate then
		debugFolder:WaitForChild("Button").Event:Connect(function(keyCode, isUp)
			if isUp then
				onButtonUp(keyCode)
			else
				onButtonDown(keyCode)
			end
		end)
		local stickEvent = debugFolder:FindFirstChild("Stick")
		if stickEvent then
			stickEvent.Event:Connect(onStick)
		end
	end

	------------------------------------------------------------ teleport arc
	local function updateTeleportArc()
		local hand = worldPose(Enum.UserCFrame.RightHand)
		local p = hand.Position
		local v = hand.LookVector * TELEPORT_SPEED
		local dt = 0.05
		local target, n = nil, 0
		for i = 1, 60 do
			local nextP = p + v * dt + TELEPORT_GRAVITY * (0.5 * dt * dt)
			local hit = workspace:Raycast(p, nextP - p, clubRay)
			if i % 2 == 0 and n < #arcDots then
				n += 1
				arcDots[n].CFrame = CFrame.new(p)
			end
			if hit then
				if walkableSet[hit.Instance] and hit.Normal.Y > 0.7 then
					target = hit.Position
				end
				break
			end
			v += TELEPORT_GRAVITY * dt
			p = nextP
		end
		local color = target and Color3.fromRGB(120, 220, 255) or Color3.fromRGB(255, 110, 100)
		for i, d in arcDots do
			d.Transparency = i <= n and 0.2 or 1
			d.Color = color
		end
		if target then
			arcTarget.Transparency = 0.3
			arcTarget.CFrame = CFrame.new(target + Vector3.new(0, 0.03, 0)) * CFrame.Angles(0, 0, math.rad(90))
		else
			arcTarget.Transparency = 1
		end
		return target
	end

	local function hideTeleportArc()
		for _, d in arcDots do
			d.Transparency = 1
		end
		arcTarget.Transparency = 1
	end

	local function handleActionStick()
		local s = actionStick
		-- teleport: push forward to aim, release to go
		if s.Y > 0.6 and math.abs(s.X) < 0.75 then
			aimingTeleport = true
			teleportTarget = updateTeleportArc()
			return
		elseif aimingTeleport then
			aimingTeleport = false
			hideTeleportArc()
			if teleportTarget then
				placeHead(teleportTarget, nil, teleportTarget.Y)
			end
			teleportTarget = nil
		end

		-- rewind the ball: pull back
		if s.Y < -0.7 and math.abs(s.X) < 0.6 then
			if not rewindLatched then
				rewindLatched = true
				Ball.requestReset()
			end
		elseif s.Y > -0.3 then
			rewindLatched = false
		end

		-- snap turn around the head
		if math.abs(s.X) > 0.7 and math.abs(s.Y) < 0.6 then
			if not turnLatched then
				turnLatched = true
				local headWorld = worldPose(Enum.UserCFrame.Head).Position
				local angle = math.rad(Config.VRSnapTurnDegrees) * (s.X > 0 and -1 or 1)
				local pivot = CFrame.new(headWorld.X, origin.Y, headWorld.Z)
				origin = pivot * CFrame.Angles(0, angle, 0) * pivot:Inverse() * origin
				teleportedThisFrame = true
			end
		elseif math.abs(s.X) < 0.3 then
			turnLatched = false
		end
	end

	------------------------------------------------------------ character follows the head (others see you)
	local function hideLocalCharacter(char)
		for _, d in char:GetDescendants() do
			if d:IsA("BasePart") or d:IsA("Decal") then
				d.LocalTransparencyModifier = 1
			end
		end
	end

	local function updateCharacter(headWorld: CFrame)
		local char = player.Character
		local hrp = char and char:FindFirstChild("HumanoidRootPart")
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		if not (hrp and hum) then
			return
		end
		hideLocalCharacter(char)
		local y = origin.Y + hum.HipHeight + hrp.Size.Y / 2
		local pos = Vector3.new(headWorld.X, y, headWorld.Z)
		char:PivotTo(CFrame.new(pos) * yawOnly(headWorld))
		hrp.AssemblyLinearVelocity = Vector3.zero
	end

	------------------------------------------------------------ putter + hit detection
	local prevHeadCF: CFrame? = nil
	local history = {} -- recent {t, pos} of the putter head
	local cooldownUntil = 0
	local wasTouching = false
	local half = HEAD_SIZE / 2

	local function overlap(cf: CFrame, center: Vector3)
		local lp = cf:PointToObjectSpace(center)
		local cp = Vector3.new(math.clamp(lp.X, -half.X, half.X), math.clamp(lp.Y, -half.Y, half.Y), math.clamp(lp.Z, -half.Z, half.Z))
		local delta = lp - cp
		return delta.Magnitude < R, delta, lp
	end

	local function headVelocity()
		local n = #history
		if n < 2 then
			return Vector3.zero
		end
		local newest = history[n]
		-- two frames: enough to smooth tracking jitter without lagging an accelerating swing
		local oldest = history[math.max(1, n - 2)]
		local dt = newest.t - oldest.t
		if dt <= 1e-4 then
			return Vector3.zero
		end
		return (newest.p - oldest.p) / dt
	end

	local function updatePutter(handCF: CFrame)
		local clubCF = handCF * clubOffset
		local gripPos = clubCF.Position
		local shaftDir = clubCF.LookVector
		local headPos = gripPos + shaftDir * clubLength

		local floor = groundY(headPos, 1.5)
		if floor then
			local restY = floor + half.Y + 0.01
			if headPos.Y < restY then
				-- slide along the ground instead of passing through it
				headPos = Vector3.new(headPos.X, restY, headPos.Z)
			elseif shaftDir.Y < -0.3 then
				-- a little too short: stretch (up to REACH_EXTRA) so the head sits on the ground
				local need = (headPos.Y - restY) / -shaftDir.Y
				if need <= REACH_EXTRA then
					headPos += shaftDir * need
				else
					headPos += shaftDir * REACH_EXTRA
				end
			end
		end

		local faceN = flat(clubCF.RightVector)
		if faceN.Magnitude < 0.2 then
			faceN = flat(clubCF.UpVector:Cross(shaftDir))
		end
		faceN = faceN.Magnitude > 1e-3 and faceN.Unit or Vector3.xAxis
		local headCF = CFrame.fromMatrix(headPos, faceN, Vector3.yAxis)

		-- visuals: grip starts at the controller and runs along the pointing direction
		grip.CFrame = CFrame.lookAt(gripPos + shaftDir * 0.3, gripPos + shaftDir * 1)
		local toeDir = headCF.LookVector
		if toeDir:Dot(flat(clubCF.UpVector)) < 0 then
			toeDir = -toeDir
		end
		local hosel = headPos + Vector3.new(0, half.Y * 0.5, 0) - toeDir * (half.Z * 0.75)
		local shaftStart = gripPos + shaftDir * 0.65
		local len = (hosel - shaftStart).Magnitude
		if len > 0.05 then
			shaft.Size = Vector3.new(0.035, 0.035, len)
			shaft.CFrame = CFrame.lookAt((hosel + shaftStart) / 2, hosel)
		end
		head.CFrame = headCF
		sight.CFrame = headCF * CFrame.new(0, half.Y + 0.002, 0)

		return headCF
	end

	local function detectHit(headCF: CFrame)
		local now = os.clock()
		table.insert(history, { t = now, p = headCF.Position })
		if #history > 6 then
			table.remove(history, 1)
		end

		local b = Ball.ball
		local solid = not aimingTeleport and (not Config.VRGripToPutt or gripHeld[dominant])
		local ready = Ball.canHit() and solid
		-- "ghost" the putter while it can't hit the ball
		local ghost = not ready or now < cooldownUntil
		for _, p in putter:GetChildren() do
			p.Transparency = ghost and 0.65 or 0
		end

		-- teleports, snap turns, fitting and tracking glitches make the head jump: never a swing
		-- (a real swing tops out well under 30 studs/s, so scale the limit with frame time)
		local frameDt = #history >= 2 and (now - history[#history - 1].t) or 1 / 60
		local jumped = prevHeadCF ~= nil and (headCF.Position - prevHeadCF.Position).Magnitude > math.max(1.5, 30 * frameDt)
		if not prevHeadCF or teleportedThisFrame or jumped or not b then
			if teleportedThisFrame or jumped then
				table.clear(history)
				table.insert(history, { t = now, p = headCF.Position })
			end
			prevHeadCF = headCF
			wasTouching = b ~= nil and (overlap(headCF, b.Position))
			return
		end
		local center = b.Position
		local touchingNow = overlap(headCF, center)

		if ready and now >= cooldownUntil and not wasTouching then
			local moved = (headCF.Position - prevHeadCF.Position).Magnitude
			local steps = math.clamp(math.ceil(moved / 0.02), 1, 80)
			for i = 1, steps do
				local cf = prevHeadCF:Lerp(headCF, i / steps)
				local hit, delta, lp = overlap(cf, center)
				if hit then
					local n
					if delta.Magnitude > 1e-4 then
						n = cf:VectorToWorldSpace(delta.Unit)
					else
						n = cf.RightVector * (lp.X >= 0 and 1 or -1)
					end
					n = flat(n)
					if n.Magnitude < 1e-3 then
						break
					end
					n = n.Unit
					local v = headVelocity()
					local u = v:Dot(n)
					if u >= Config.VRMinHitSpeed then
						local tangential = flat(v - n * u)
						local ballVel = n * u * Config.VRHitMultiplier + tangential * Config.VRTangentialTransfer
						if Ball.hit(ballVel) then
							cooldownUntil = now + HIT_COOLDOWN
							haptic(math.clamp(0.25 + ballVel.Magnitude / 20, 0.25, 1), 0.08)
						end
					end
					break
				end
			end
		end
		wasTouching = touchingNow
		prevHeadCF = headCF
	end

	------------------------------------------------------------ frame update
	RunService:BindToRenderStep("GolfVR", Enum.RenderPriority.Camera.Value + 1, function(dt)
		camera.HeadScale = 1 -- life size: 1 stud = 0.3 m, regardless of avatar size
		handleActionStick()

		-- smooth locomotion relative to where you're looking
		if moveStick.Magnitude > 0.2 then
			local headWorld = worldPose(Enum.UserCFrame.Head)
			local yaw = yawOnly(headWorld)
			local move = (yaw.LookVector * moveStick.Y + yaw.RightVector * moveStick.X) * Config.VRMoveSpeed * dt
			origin = origin + move
		end

		-- keep the playspace floor on the ground under your head (walk up ramps etc.)
		local headWorld = worldPose(Enum.UserCFrame.Head)
		local g = floorY(Vector3.new(headWorld.X, origin.Y, headWorld.Z), 2.2)
		if g and math.abs(g - origin.Y) > 0.01 then
			local newY = origin.Y + (g - origin.Y) * math.min(1, dt * 10)
			origin = origin + Vector3.new(0, newY - origin.Y, 0)
		end

		headWorld = worldPose(Enum.UserCFrame.Head)
		if simulate then
			camera.CFrame = headWorld -- emulate what the headset would render
		else
			camera.CFrame = origin * CFrame.new(0, -floorOffsetY, 0)
		end

		if not clubFitted then
			autoFitClub()
		end
		local headCF = updatePutter(worldPose(dominant))
		detectHit(headCF)
		teleportedThisFrame = false

		local offHand = dominant == Enum.UserCFrame.RightHand and Enum.UserCFrame.LeftHand or Enum.UserCFrame.RightHand
		HUD.placeVRWrist(worldPose(offHand), headWorld.Position)
		HUD.placeVRMessage(headWorld)
		updateCharacter(headWorld)
	end)

	-- new hole / reset: put the player next to the ball
	local prompted = false
	Ball.Placed.Event:Connect(function(pos)
		warpToBall(pos)
		if not prompted then
			prompted = true
			task.delay(2.4, function()
				HUD.message("Point your controller at the ground like a putter grip.  Trigger: warp to ball", Color3.fromRGB(180, 230, 255), 6)
			end)
		end
	end)

	VR.warpToBall = warpToBall
	VR.getState = function()
		return {
			origin = origin,
			clubLength = clubLength,
			head = head.CFrame,
			hand = worldPose(dominant),
			headVel = headVelocity(),
		}
	end
end

return VR
