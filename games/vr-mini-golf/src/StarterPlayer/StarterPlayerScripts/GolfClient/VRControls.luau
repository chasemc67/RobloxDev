-- VRControls: Walkabout-style VR putting at real-world scale (1 stud = 0.3 m, HeadScale 1).
--   * Room-scale: the camera is a floor-level playspace origin; your real head/hands are tracked on top of it.
--   * The putter shaft runs parallel to the club-hand controller's handle and comes out of its TOP end
--     (Config.VRClubFlip, VRClubGripPitch/Yaw/Roll, VRClubButtOffset; v80, Chase's VR playtest of v79 found the
--     out-of-the-bottom mount pointing the wrong way). Length auto-fits your height and stretches a few cm to
--     reach the ground.
--   * Hole plane: near the ball, the putter head and your floor sit on the plane of the felt the ball is on
--     (parts tagged GolfSurface, slopes included). Walls, rails and posts are never ground: the club ghosts
--     through them and you can't stand on them. The ball is only moved by the swing-hit logic below.
--   * The putter face velocity at contact becomes the ball velocity.
--
-- Controls (modelled on Walkabout Mini Golf):
--   Trigger (either hand) ...... warp to your ball; on a menu / wrist button: click (GolfClient.VRPointer)
--   Right stick left/right ..... snap turn
--   Right stick forward ........ aim teleport arc, release to teleport
--   Right stick back ........... rewind ball to where your last shot started
--   Left stick ................. walk
--   Grip (club hand) ........... hold to make the putter solid (only when Config.VRGripToPutt = true)
--   B / Y ...................... scorecard
--   Off-hand X / A .............. toggle wrist. Hand and grip fit are chosen in Settings only.
--   Look at either wrist ....... bracer + wrist card: hole, par, stroke, total, best (HUD; no buttons)
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
local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage:WaitForChild("Golf"):WaitForChild("Config"))
local CameraOcclusion = require(ReplicatedStorage:WaitForChild("Golf"):WaitForChild("CameraOcclusion"))
local VRPointer = require(script.Parent:WaitForChild("VRPointer"))
local ClubSetup = require(script.Parent:WaitForChild("ClubSetup"))

local player = Players.LocalPlayer
local R = Config.BallRadius

local VR = {}

-- real-ish blade putter: 3.3 cm thick, 3.3 cm tall, 12.6 cm toe-to-heel
local HEAD_SIZE = Vector3.new(0.11, 0.11, 0.42) -- X = face thickness, Y = height, Z = toe-to-heel
local HIT_COOLDOWN = 0.6
local REACH_EXTRA = 0.5 -- the shaft may stretch this much (15 cm) to keep the head on the ground
local TELEPORT_SPEED = 22 -- ~6.5 m max reach
-- (stage ab, Chase) the head is level with the ground only while on / near it; lifted, it moves rigidly with the club.
-- Blend by the head's height over its resting height: level up to HEAD_LEVEL_NEAR, rigid from HEAD_LEVEL_FAR.
local HEAD_LEVEL_NEAR = 0.15 -- 4.5 cm
local HEAD_LEVEL_FAR = 0.6 -- 18 cm
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

-- Default club mount for `hand`, in hand space: the butt point (where the shaft starts) and the club rotation
-- (LookVector = shaft direction, RightVector = putter face normal, UpVector ~ toe side).
-- Grip mount: the shaft runs along the handle axis. Unflipped (VRClubFlip false, v12-v79) it leaves the bottom:
-- from the hand frame a -90 deg pitch turns LookVector from -Z (aim ray) to -Y (down the handle) and a further
-- -VRClubGripPitch rakes it toward +Z. Flipped (default) adds 180 deg about X, so it leaves the TOP: +Y raked
-- toward -Z, the exact negation of the unflipped shaft (yaw is negated too so a non-zero yaw also negates
-- exactly). RightVector (the putter face normal) stays hand +X either way, so the face still points the same
-- way; only UpVector (toe side, unused by the head) flips. The butt point is VRClubButtOffset along the shaft,
-- i.e. on the top side when flipped. Rotations about X are unchanged by the left/right mirror (hand YZ plane);
-- yaw and roll flip sign.
-- Legacy mount (VRClubLegacyAim): from the controller tip along the aim ray, pitched by VRClubAngle.
local function defaultClubMount(hand: Enum.UserCFrame): (Vector3, CFrame)
	if Config.VRClubLegacyAim then
		return Vector3.new(0, 0, -(Config.VRClubTipOffset or 0)), CFrame.Angles(math.rad(Config.VRClubAngle or 0), 0, 0)
	end
	local mirror = hand == Enum.UserCFrame.LeftHand and -1 or 1
	local flip = Config.VRClubFlip ~= false
	local rot = CFrame.Angles(math.rad((flip and 90 or -90) - (Config.VRClubGripPitch or 35)), 0, 0)
		* CFrame.Angles(0, math.rad((Config.VRClubGripYaw or 0) * mirror * (flip and -1 or 1)), 0)
		* CFrame.Angles(0, 0, math.rad((Config.VRClubGripRoll or 0) * mirror))
	return rot.LookVector * (Config.VRClubButtOffset or 0.25), rot
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
	if Ball.lobbyRoam then
		local char = player.Character or player.CharacterAdded:Wait()
		local root = char:WaitForChild("HumanoidRootPart", 10)
		local hum = char:WaitForChild("Humanoid", 10)
		if root and hum then
			origin = CFrame.new(root.Position - Vector3.new(0, hum.HipHeight + root.Size.Y / 2, 0)) * yawOnly(root.CFrame)
			hum.WalkSpeed, hum.JumpPower, hum.JumpHeight = 0, 0, 0
			hum.AutoRotate = false
		end
	end
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

	-- Playable felt (CourseBuilder tags it GolfSurface). Only these define the ball's plane.
	local surfaceRay = RaycastParams.new()
	surfaceRay.FilterType = Enum.RaycastFilterType.Include
	local function refreshSurfaces()
		surfaceRay.FilterDescendantsInstances = CollectionService:GetTagged("GolfSurface")
	end
	refreshSurfaces()
	CollectionService:GetInstanceAddedSignal("GolfSurface"):Connect(refreshSurfaces)
	CollectionService:GetInstanceRemovedSignal("GolfSurface"):Connect(refreshSurfaces)
	local function surfaceHit(pos: Vector3, fromAbove: number)
		return workspace:Raycast(pos + Vector3.new(0, fromAbove, 0), Vector3.new(0, -(fromAbove + 30), 0), surfaceRay)
	end

	-- The plane of the felt under the ball (point + normal). Kept while the ball is in the air or in the cup.
	local planePoint: Vector3? = nil
	local planeNormal = Vector3.yAxis
	local function updateBallPlane(ballPos: Vector3?)
		if not ballPos and (not Ball.ball or Ball.ball.Anchored) then
			return -- sunk / being placed: keep the last plane (don't drop into the cup)
		end
		local p = ballPos or Ball.ball.Position
		local hit = workspace:Raycast(p + Vector3.new(0, 0.05, 0), Vector3.new(0, -(R + 0.4), 0), surfaceRay)
		if hit and hit.Normal.Y > 0.7 then
			planePoint, planeNormal = hit.Position, hit.Normal
		elseif ballPos or not planePoint then
			planePoint, planeNormal = p - Vector3.new(0, R, 0), Vector3.yAxis
		end
	end
	-- Height of the ball's plane at `pos`'s XZ, or nil when `pos` is out of VRPlaneRange of the ball.
	local function ballPlaneY(pos: Vector3): number?
		if not planePoint or flat(pos - planePoint).Magnitude > Config.VRPlaneRange then
			return nil
		end
		local n = planeNormal
		return planePoint.Y - (n.X * (pos.X - planePoint.X) + n.Z * (pos.Z - planePoint.Z)) / n.Y
	end
	-- Ground for the putter head: the ball's plane near the ball, otherwise the felt underneath (never walls).
	local function groundY(pos: Vector3, fromAbove: number)
		local y = ballPlaneY(pos)
		if y then
			return y
		end
		local hit = surfaceHit(pos, fromAbove)
		return hit and hit.Position.Y
	end

	-- Away from the ball the player's floor follows walkable surfaces (felt, ramps, grass) - stepping
	-- over a wall shouldn't bump your view up and down.
	local floorRay = RaycastParams.new()
	floorRay.FilterType = Enum.RaycastFilterType.Include
	local walkable = {}
	-- (world layout: the Terrain and the walkway/stair/plaza parts, which WorldBuilder tags GolfWalkable)
	local WALKABLE_NAMES = { Felt = true, CupPlate = true, Ramp = true, Base = true, Lawn = true, Baseplate = true, SpawnLocation = true }
	for _, d in workspace:GetDescendants() do
		if d:IsA("BasePart") and (WALKABLE_NAMES[d.Name] or CollectionService:HasTag(d, "GolfWalkable")) then
			table.insert(walkable, d)
		end
	end
	table.insert(walkable, workspace.Terrain)
	floorRay.FilterDescendantsInstances = walkable
	local walkableSet = {}
	for _, p in walkable do
		walkableSet[p] = true
	end
	local function floorY(pos: Vector3, fromAbove: number)
		-- near the ball: stand on the ball's plane (flat, at the ball's contact height), whatever is underfoot
		if ballPlaneY(pos) then
			return planePoint.Y
		end
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
	local grip = piece("Grip", Vector3.new(0.07, 0.07, 0.3), Color3.fromRGB(30, 30, 30), Enum.Material.Rubber)
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

	local dominant = Enum.UserCFrame.RightHand
	local clubButt, clubOffset = defaultClubMount(dominant) -- hand-space shaft start and club rotation
	local clubLength = 2.6 -- replaced by the height-based fit below
	local clubFitted = false
	local clubHeadYaw = 0 -- degrees about the shaft (club setup, stick left/right; saved with the fit)
	local headRel: CFrame? = nil -- head rotation in the club frame, from the last frame the head was level on the ground

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
		updateBallPlane(bp)
		placeHead(stand, facing, planePoint and planePoint.Y or bp.Y - R)
		if not clubFitted then
			autoFitClub()
		end
	end

	local setup
	setup = ClubSetup.new({
		eye = function() return worldPose(Enum.UserCFrame.Head) end,
		pose = function() return worldPose(dominant) end,
		hand = function() return dominant.Name end,
		headPosition = function() return head.Position end,
		ground = function(pos) return groundY(pos, 3) or origin.Y end,
		butt = function() return clubButt end,
		rotation = function() return clubOffset end,
		active = function(on) player:SetAttribute("ClubSetupActive",on) end,
		apply = function(rotation,length,headYaw)
			clubOffset,clubLength,clubFitted = rotation,length,true
			clubHeadYaw = headYaw or 0
			headRel = nil
			teleportedThisFrame = true
		end,
		defaults = function()
			clubButt,clubOffset = defaultClubMount(dominant)
			clubHeadYaw = 0
			headRel = nil
			autoFitClub()
			teleportedThisFrame = true
		end,
	}, Config, HUD)
	VR.beginClubSetup = function() setup:begin() end
	VR.resetClubSetup = function() setup:save(true) end
	VR.cancelClubSetup = function() if setup.active then setup:cancel() end end

	local function switchHands()
		dominant = dominant == Enum.UserCFrame.RightHand and Enum.UserCFrame.LeftHand or Enum.UserCFrame.RightHand
		clubButt, clubOffset = defaultClubMount(dominant)
		setup:applySaved()
		teleportedThisFrame = true
		HUD.message(dominant == Enum.UserCFrame.RightHand and "Right-handed" or "Left-handed", Color3.new(1, 1, 1), 1.5)
	end
	-- Handedness is changed only through Settings (or the Studio-only test hook).
	VR.setLeftHanded = function(left: boolean)
		if (dominant == Enum.UserCFrame.LeftHand) ~= left then
			switchHands()
		end
	end
	VR.isLeftHanded = function()
		return dominant == Enum.UserCFrame.LeftHand
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
		if setup.active then
			local clubTrigger = dominant == Enum.UserCFrame.RightHand and Enum.KeyCode.ButtonR2 or Enum.KeyCode.ButtonL2
			if keyCode == clubTrigger then setup:save(false)
			elseif keyCode == Enum.KeyCode.ButtonB or keyCode == Enum.KeyCode.ButtonY then setup:save(true) end
			return
		end
		-- trigger: the laser pointer's click first (menus, scorecard, wrist card buttons)
		if keyCode == Enum.KeyCode.ButtonR2 or keyCode == Enum.KeyCode.ButtonL2 then
			if VRPointer.press(keyCode == Enum.KeyCode.ButtonR2 and Enum.UserCFrame.RightHand or Enum.UserCFrame.LeftHand) then
				return
			end
		end
		if Ball.menuOpen then
			return -- the front-end menu is up (GolfClient.FrontEnd)
		end
		if keyCode == Enum.KeyCode.ButtonR2 or keyCode == Enum.KeyCode.ButtonL2 then
			if player:GetAttribute("Course") ~= nil then
				warpToBall(nil) -- (stage y: not in the lobby, where the hidden ball is just parked on the spawn deck)
			end
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
		elseif (dominant == Enum.UserCFrame.RightHand and keyCode == Enum.KeyCode.ButtonX)
			or (dominant == Enum.UserCFrame.LeftHand and keyCode == Enum.KeyCode.ButtonA) then
			if HUD.toggleWrist then HUD.toggleWrist() end
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
		if setup.active then setup.stick = pos; moveStick, actionStick = Vector2.zero, Vector2.zero; return end
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
		-- hold the body exactly where we put it each frame: cancel gravity locally (the character stands on
		-- the ball's plane even where there's no felt under it, e.g. outside a wall)
		local hover = hrp:FindFirstChild("GolfVRHover")
		if not hover then
			local att = Instance.new("Attachment")
			att.Name = "GolfVRHoverAttachment"
			att.Parent = hrp
			hover = Instance.new("VectorForce")
			hover.Name = "GolfVRHover"
			hover.RelativeTo = Enum.ActuatorRelativeTo.World
			hover.ApplyAtCenterOfMass = true
			hover.Attachment0 = att
			hover.Parent = hrp
		end
		hover.Force = Vector3.new(0, hrp.AssemblyMass * workspace.Gravity, 0)
		-- and stop the Humanoid's hip spring pulling it down to whatever is under it (a lower floor past a wall)
		hum.PlatformStand = true
		local y = origin.Y + hum.HipHeight + hrp.Size.Y / 2
		local pos = Vector3.new(headWorld.X, y, headWorld.Z)
		char:PivotTo(CFrame.new(pos) * yawOnly(headWorld))
		hrp.AssemblyLinearVelocity = Vector3.zero
		hrp.AssemblyAngularVelocity = Vector3.zero
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

	local lastClubCF = CFrame.new()
	local function updatePutter(handCF: CFrame)
		-- shaft starts at the handle end (clubButt: top when VRClubFlip) and runs along the grip axis (or the A-button fit)
		local clubCF = handCF * CFrame.new(clubButt) * clubOffset
		local gripPos = clubCF.Position
		local shaftDir = clubCF.LookVector
		local headPos = gripPos + shaftDir * clubLength
		lastClubCF = clubCF

		local floor = groundY(headPos, 1.5)
		local level = 0 -- 1: on / near the ground (head level), 0: lifted (rigid with the club)
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
			local k = math.clamp((headPos.Y - restY - HEAD_LEVEL_NEAR) / (HEAD_LEVEL_FAR - HEAD_LEVEL_NEAR), 0, 1)
			level = 1 - k * k * (3 - 2 * k)
		end

		-- face normal: the club's face direction turned by the saved head yaw about the shaft
		local faceRaw = clubCF.RightVector
		if clubHeadYaw ~= 0 then
			faceRaw = CFrame.fromAxisAngle(shaftDir, math.rad(clubHeadYaw)):VectorToWorldSpace(faceRaw)
		end
		local faceN = flat(faceRaw)
		if faceN.Magnitude < 0.2 then
			faceN = flat(clubCF.UpVector:Cross(shaftDir))
		end
		faceN = faceN.Magnitude > 1e-3 and faceN.Unit or Vector3.xAxis
		local levelRot = CFrame.fromMatrix(Vector3.zero, faceN, Vector3.yAxis)
		if level >= 0.999 or not headRel then
			headRel = clubCF.Rotation:Inverse() * levelRot
		end
		local headRot = level >= 0.999 and levelRot or (clubCF.Rotation * headRel):Lerp(levelRot, level)
		local headCF = CFrame.new(headPos) * headRot

		-- visuals: a short ferrule at the shaft start (handle end), then the shaft down to the hosel
		grip.CFrame = CFrame.lookAt(gripPos + shaftDir * (grip.Size.Z / 2), gripPos + shaftDir * grip.Size.Z)
		local toeDir = headCF.LookVector
		if toeDir:Dot(flat(clubCF.UpVector)) < 0 then
			toeDir = -toeDir
		end
		local hosel = headPos + Vector3.new(0, half.Y * 0.5, 0) - toeDir * (half.Z * 0.75)
		local shaftStart = gripPos + shaftDir * (grip.Size.Z * 0.8)
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
		local solid = not setup.active and not aimingTeleport and (not Config.VRGripToPutt or gripHeld[dominant])
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
					local ballVel = Ball.clubImpulse(n, headVelocity())
					if ballVel and Ball.hit(ballVel, "vr") then
						cooldownUntil = now + HIT_COOLDOWN
						haptic(math.clamp(0.25 + ballVel.Magnitude / 20, 0.25, 1), 0.08)
					end
					break
				end
			end
		end
		wasTouching = touchingNow
		prevHeadCF = headCF
	end

	------------------------------------------------------------ see-through (stage m/n occluder fade, from the head)
	-- The same fade the phone/desktop camera does (CameraOcclusion.fade: LocalTransparencyModifier 0.7, thick sweep,
	-- near-lens glow hide), from the VR head (camera CFrame * head UserCFrame) to the ball, at ~30 Hz.
	local lastHeadWorld = CFrame.new()
	local fadeAt, fading = 0, false
	local function updateSeeThrough(eye: Vector3)
		local now = os.clock()
		local b = Ball.ball
		local focus = b and b.Position + Vector3.new(0, 0.25, 0)
		local nearClub = b and (head.Position - b.Position).Magnitude <= Config.WristStanceRange + 1
		local eligible = focus and Ball.canHit() and b.AssemblyLinearVelocity.Magnitude < 0.15 and not setup.active and nearClub and (focus - eye).Magnitude <= Config.VRFadeRange
		Ball.seeThrough = eligible == true
		if not eligible then
			if fading then CameraOcclusion.clearFade(); fading = false end
			return
		end
		if now - fadeAt < 1 / 30 then return end
		fadeAt = now
		if eligible then
			CameraOcclusion.fade(eye, focus, { player.Character })
			fading = true
		elseif fading then
			CameraOcclusion.clearFade()
			fading = false
		end
	end

	------------------------------------------------------------ frame update
	local wristHand: Enum.UserCFrame? = nil
	RunService:BindToRenderStep("GolfVR", Enum.RenderPriority.Camera.Value + 1, function(dt)
		camera.HeadScale = 1 -- life size: 1 stud = 0.3 m, regardless of avatar size
		updateBallPlane()
		if not setup.active then handleActionStick() end

		-- smooth locomotion relative to where you're looking
		if not setup.active and not Ball.menuOpen and moveStick.Magnitude > 0.2 then
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
		setup:update(dt)
		local headCF = updatePutter(worldPose(dominant))
		detectHit(headCF)
		teleportedThisFrame = false

		-- the wrist card goes on whichever wrist you look at (stage ab, Chase: either wrist). It only changes wrists
		-- while hidden; the off hand wins ties, so nothing changes for players who check the off hand.
		local offHand = dominant == Enum.UserCFrame.RightHand and Enum.UserCFrame.LeftHand or Enum.UserCFrame.RightHand
		if not wristHand or not HUD.isWristShown() then
			local offScore = HUD.wristLookScore(worldPose(offHand), headWorld, offHand == Enum.UserCFrame.LeftHand)
			local clubScore = HUD.wristLookScore(worldPose(dominant), headWorld, dominant == Enum.UserCFrame.LeftHand)
			wristHand = clubScore < offScore - 0.05 and dominant or offHand
		end
		-- the wrist stays down mid-swing (putter head speed) and in a putting stance (head low beside a hittable ball)
		local b = Ball.ball
		local toBall = b and (headCF.Position - b.Position)
		local stance = toBall ~= nil and Ball.canHit() and Vector3.new(toBall.X, 0, toBall.Z).Magnitude < Config.WristStanceRange and math.abs(toBall.Y) < 0.8
		-- (the club hand raised to look at its wrist isn't putting, even with the putter dangling by the ball)
		stance = stance and wristHand ~= dominant
		HUD.placeVRWrist(worldPose(wristHand), headWorld, wristHand == Enum.UserCFrame.LeftHand, { clubSpeed = headVelocity().Magnitude, stance = stance or setup.active })
		HUD.placeVRMessage(headWorld)
		VRPointer.update({
			[Enum.UserCFrame.RightHand] = worldPose(Enum.UserCFrame.RightHand),
			[Enum.UserCFrame.LeftHand] = worldPose(Enum.UserCFrame.LeftHand),
		}, dominant)
		lastHeadWorld = headWorld
		updateCharacter(headWorld)
		updateSeeThrough(headWorld.Position)
	end)

	-- new hole / reset: put the player next to the ball
	local prompted = false
	Ball.Placed.Event:Connect(function(pos)
		warpToBall(pos)
		if not prompted then
			prompted = true
			task.delay(2.4, function()
				HUD.message("Hold your controller like a putter grip, handle down.  Trigger: warp to ball", Color3.fromRGB(180, 230, 255), 6)
			end)
		end
	end)

	VR.warpToBall = warpToBall
	VR.putterHead = head
	-- the viewpoint for XRay (the VR head; the camera CFrame is the floor origin on a real headset)
	VR.getEye = function()
		return lastHeadWorld.Position
	end
	VRPointer.start(simulate)

	-- Studio + SimulateVR only: drive the laser pointer and the wrist card (tools/menu_shots.py --vr, --wrist).
	--   Invoke("targets") -> clickable buttons on the open panels with their world points
	--   Invoke("aim", { hand = "RightHand", point = {x, y, z} }) -> puts that hand below/beside the head aiming at it
	--   Invoke("trigger", "RightHand") -> trigger down + up on that hand
	--   Invoke("wrist", true / false) -> off hand in a watch pose (back of the wrist to the eyes) / lowered
	--   Invoke("state") -> pointer + wrist card state
	--   Invoke("wristSim", { scenario = "watch" | "glance" | "swings" | "stance" | "head", seed = n }) -> wrist events
	if simulate and RunService:IsStudio() then
		local hook = Instance.new("BindableFunction")
		hook.Name = "GolfPointerDebug"
		local function setHand(which: Enum.UserCFrame, worldCF: CFrame)
			local v = debugFolder:FindFirstChild(which.Name)
			if v then
				v.Value = (origin * CFrame.new(0, -floorOffsetY, 0)):Inverse() * worldCF
			end
		end
		-- off hand in a watch pose: forearm across the body, wrist ~42 cm in front and 16 cm below the eyes, back of the
		-- wrist up at them (yawDeg turns the wrist spot about the head, tiltDeg tips the back of the wrist off the eyes)
		local function watchPose(headW: CFrame, left: boolean, yawDeg: number?, tiltDeg: number?)
			local side = left and -1 or 1
			local flatLook = flat(headW.LookVector)
			flatLook = flatLook.Magnitude > 1e-3 and flatLook.Unit or Vector3.new(0, 0, -1)
			flatLook = CFrame.fromAxisAngle(Vector3.yAxis, math.rad(yawDeg or 0)):VectorToWorldSpace(flatLook)
			local flatRight = flatLook:Cross(Vector3.yAxis)
			local wristPos = headW.Position + flatLook * 1.4 - Vector3.new(0, 0.55, 0) + flatRight * (0.15 * side)
			local back = (headW.Position - wristPos).Unit
			if tiltDeg and tiltDeg ~= 0 then
				back = CFrame.fromAxisAngle(flatRight, math.rad(tiltDeg)):VectorToWorldSpace(back)
			end
			local right = back * (left and -1 or 1) -- left hand: back of the hand is -X
			local look = flatRight * -side -- aim ray across the body, toward the midline
			look = (look - right * look:Dot(right)).Unit
			local up = right:Cross(look)
			local rot = CFrame.fromMatrix(Vector3.zero, right, up)
			-- the controller origin sits WRIST_OFFSET-ish ahead of the wrist along its own axes
			local handPos = wristPos - rot:VectorToWorldSpace(Vector3.new(0, -0.12, 0.33))
			return CFrame.new(handPos) * rot
		end

		-- Scripted VR-sim motion for the wrist trigger (tools/wrist_sim.py): drives head + both hands frame by frame
		-- and returns the wrist show/hide events, plus how many frames met the look test while a gate held it down.
		--   "watch"  3x deliberate look at the wrist (1.2 s) then lower it: expect 3 shows / 3 hides
		--   "glance" 6x the wrist flicks through the watch pose for 0.15 s: expect 0 shows
		--   "swings" 10 practice swings away from the ball, off hand on the grip / then IN the watch pose: expect 0
		--   "stance" 8 address waggles behind a hittable ball (slow), off hand on the grip / in the watch pose: expect 0
		--   "head"   25 s of looking around, walking, pointing, hands by your sides / near-watch poses: expect 0
		local function wristSim(name: string, seed: number?)
			local rng = Random.new(seed or 7)
			local off = dominant == Enum.UserCFrame.RightHand and Enum.UserCFrame.LeftHand or Enum.UserCFrame.RightHand
			local left = off == Enum.UserCFrame.LeftHand
			local side = left and -1 or 1
			local h0 = worldPose(Enum.UserCFrame.Head)
			local baseLook = flat(h0.LookVector)
			baseLook = baseLook.Magnitude > 1e-3 and baseLook.Unit or Vector3.new(0, 0, -1)
			local baseRight = baseLook:Cross(Vector3.yAxis)
			local b = Ball.ball
			local ballPos = b and b.Position or (h0.Position + baseLook * 4 - Vector3.new(0, 5.2, 0))
			local groundY = ballPos.Y
			local eye = Vector3.new(h0.X, groundY + 5.4, h0.Z)
			-- away from the ball for the non-stance scenarios
			local away = Vector3.new(eye.X - ballPos.X, 0, eye.Z - ballPos.Z)
			if away.Magnitude < 4 then
				eye += (away.Magnitude > 1e-3 and away.Unit or -baseLook) * (4 - away.Magnitude)
			end
			local function headLook(pos: Vector3, yaw: number, pitch: number)
				local d = CFrame.fromAxisAngle(Vector3.yAxis, math.rad(yaw)):VectorToWorldSpace(baseLook)
				d = d * math.cos(math.rad(pitch)) + Vector3.yAxis * math.sin(math.rad(pitch))
				local cf = CFrame.lookAt(pos, pos + d)
				setHand(Enum.UserCFrame.Head, cf)
				return cf
			end
			local function headAt(pos: Vector3, target: Vector3)
				local cf = CFrame.lookAt(pos, target)
				setHand(Enum.UserCFrame.Head, cf)
				return cf
			end
			local function hang(headW: CFrame, h: Enum.UserCFrame, swingDeg: number?)
				local sd = h == Enum.UserCFrame.RightHand and 1 or -1
				local fl = flat(headW.LookVector)
				fl = fl.Magnitude > 1e-3 and fl.Unit or baseLook
				local fr = fl:Cross(Vector3.yAxis)
				local rest = headW.Position + fr * (0.6 * sd) - Vector3.new(0, 2.6, 0)
				local dir = CFrame.fromAxisAngle(fr, math.rad(swingDeg or 0)):VectorToWorldSpace(fl)
				return CFrame.lookAt(rest, rest + dir)
			end
			local function clubAtSide(headW: CFrame)
				local fl = flat(headW.LookVector)
				fl = fl.Magnitude > 1e-3 and fl.Unit or baseLook
				local p = Vector3.new(headW.X, groundY + 0.3, headW.Z) + fl:Cross(Vector3.yAxis) * (1.0 * (left and 1 or -1)) + fl * 0.3
				setHand(dominant, VR.test.handCFrameFor(p, fl))
			end
			local function grip(): CFrame
				return worldPose(dominant) * CFrame.new(0, -0.1, 0.3)
			end
			local t0 = os.clock()
			local frames, condFrames, gated = 0, 0, {}
			local function frame()
				RunService.RenderStepped:Wait()
				frames += 1
				local st = HUD.wristState()
				if st and st.faceDeg and st.faceDeg <= Config.WristShowDeg and st.gazeDeg <= Config.WristGazeDeg then
					condFrames += 1
					local why = st.blocked or "none"
					gated[why] = (gated[why] or 0) + 1
				end
			end
			local function run(seconds: number, step: (t: number) -> ())
				local s0 = os.clock()
				while true do
					local t = os.clock() - s0
					if t > seconds then
						break
					end
					step(t)
					frame()
				end
			end
			local function lower(seconds)
				run(seconds, function()
					local hw = headLook(eye, 0, -10)
					clubAtSide(hw)
					setHand(off, hang(hw, off))
				end)
			end
			local latency = {}
			lower(0.8)
			if name == "watch" then
				for i = 1, 3 do
					local tShow = os.clock()
					run(1.2, function()
						local hw = headLook(eye, 0, -18)
						clubAtSide(hw)
						setHand(off, watchPose(hw, left))
					end)
					for _, e in HUD.wristEvents(tShow) do
						if e.event == "show" then
							table.insert(latency, math.floor((e.t - tShow) * 1000))
							break
						end
					end
					lower(1.2)
				end
			elseif name == "glance" then
				for i = 1, 6 do
					run(0.15, function()
						local hw = headLook(eye, 0, -18)
						clubAtSide(hw)
						setHand(off, watchPose(hw, left))
					end)
					lower(0.7)
				end
			elseif name == "swings" then
				-- practice swings 2+ studs from the ball: target line along baseRight, putter head through a spot in front of
				-- the feet; head looking at that spot. Peak head speed 3.5..9 studs/s.
				local spot = Vector3.new(eye.X, groundY + 0.3, eye.Z) + baseLook * 1.3
				for i = 1, 10 do
					local amp = rng:NextNumber(0.9, 1.8)
					local period = rng:NextNumber(0.9, 1.6)
					local watch = i > 5
					run(period, function(t)
						-- off hand on the grip looking at the swing, or (worst case) looking right at the raised wrist
						local hw = watch and headLook(eye, 0, -20) or headAt(eye + Vector3.new(0, -0.3, 0), spot)
						local p = spot + baseRight * (amp * math.sin(2 * math.pi * t / period))
						setHand(dominant, VR.test.handCFrameFor(p, baseRight))
						setHand(off, watch and watchPose(hw, left) or grip())
					end)
				end
				lower(0.5)
			elseif name == "stance" then
				-- standing beside the ball, putter head waggling 0.6..1.4 studs behind it (never reaching it), slow
				local stand = Vector3.new(ballPos.X, groundY + 5.1, ballPos.Z) - baseLook * 1.6
				for i = 1, 8 do
					local period = rng:NextNumber(1.6, 2.6)
					local watch = i % 2 == 0
					run(period, function(t)
						local hw = headAt(stand, ballPos)
						local back = 0.6 + 0.8 * (1 - math.cos(2 * math.pi * t / period)) / 2
						local p = Vector3.new(ballPos.X, groundY + 0.3, ballPos.Z) - baseRight * back
						setHand(dominant, VR.test.handCFrameFor(p, baseRight))
						-- in the watch pose the head looks at the wrist (worst case)
						if watch then
							setHand(off, watchPose(headLook(stand, 0, -20), left))
						else
							setHand(off, grip())
						end
					end)
				end
				lower(0.5)
			elseif name == "head" then
				-- 25 s: smooth random yaw/pitch targets (+-80 deg, -60..+25), walking bob + arm swing, now and then
				-- pointing the off hand forward, or holding it near the watch pose while looking 35-60 deg away
				local yaw, pitch = 0, -10
				local seg = 0
				while seg < 25 do
					local dur = rng:NextNumber(0.8, 2.0)
					local y1, p1 = rng:NextNumber(-80, 80), rng:NextNumber(-60, 25)
					local y0, p0 = yaw, pitch
					local mode = rng:NextInteger(1, 4)
					local awayYaw = (rng:NextNumber() < 0.5 and -1 or 1) * rng:NextNumber(35, 60)
					local walk = rng:NextNumber() < 0.5
					run(dur, function(t)
						local k = (1 - math.cos(math.pi * math.min(t / dur, 1))) / 2
						yaw, pitch = y0 + (y1 - y0) * k, p0 + (p1 - p0) * k
						local bob = walk and Vector3.new(0, 0.06 * math.sin(t * 11), 0) + baseLook * (t * 1.2) or Vector3.zero
						local hw = headLook(eye + bob, yaw, pitch)
						clubAtSide(hw)
						if mode == 1 then
							setHand(off, hang(hw, off, walk and 25 * math.sin(t * 5.5) or 0))
						elseif mode == 2 then
							local from = hw.Position + hw.RightVector * (0.5 * side) - Vector3.new(0, 1.1, 0) + flat(hw.LookVector) * 0.8
							setHand(off, CFrame.lookAt(from, from + hw.LookVector * 10 + Vector3.new(0, 1, 0)))
						elseif mode == 3 then
							-- wrist in the watch pose for a spot 35-60 deg away from where you look
							setHand(off, watchPose(hw, left, awayYaw))
						else
							-- wrist up toward the eyes, back of it tipped 40-70 deg off them (looking at the palm side)
							setHand(off, watchPose(hw, left, 0, (rng:NextNumber() < 0.5 and -1 or 1) * 55))
						end
					end)
					seg += dur
				end
				lower(0.5)
			end
			lower(0.6)
			local ev = HUD.wristEvents(t0)
			local shows, hides = 0, 0
			for _, e in ev do
				if e.event == "show" then
					shows += 1
				else
					hides += 1
				end
			end
			return { scenario = name, seconds = os.clock() - t0, frames = frames, lookFrames = condFrames, lookFramesBy = gated, shows = shows, hides = hides, latencyMs = latency, events = ev }
		end

		hook.OnInvoke = function(cmd, arg)
			local headW = worldPose(Enum.UserCFrame.Head)
			if cmd == "targets" then
				local out = {}
				for _, t in VRPointer.targets() do
					table.insert(out, { panel = t.panel, name = t.name, text = t.text, world = { t.world.X, t.world.Y, t.world.Z } })
				end
				return out
			elseif cmd == "aim" then
				local hand = Enum.UserCFrame[arg.hand or "RightHand"]
				local side = hand == Enum.UserCFrame.RightHand and 1 or -1
				local from = headW.Position + headW.RightVector * (0.6 * side) - Vector3.new(0, 1.1, 0) + headW.LookVector * 0.8
				local p = Vector3.new(arg.point[1], arg.point[2], arg.point[3])
				setHand(hand, CFrame.lookAt(from, p))
				-- in a menu the idle hand hangs down by your side, pointing at the floor (not when it's the wrist-up hand)
				if VRPointer.modalOpen() then
					local other = hand == Enum.UserCFrame.RightHand and Enum.UserCFrame.LeftHand or Enum.UserCFrame.RightHand
					local rest = headW.Position - headW.RightVector * (0.6 * side) - Vector3.new(0, 2.6, 0)
					setHand(other, CFrame.lookAt(rest, rest + Vector3.new(0, -1, 0) + flat(headW.LookVector) * 0.3))
				end
				return { hand = hand.Name }
			elseif cmd == "trigger" then
				local key = arg == "LeftHand" and Enum.KeyCode.ButtonL2 or Enum.KeyCode.ButtonR2
				onButtonDown(key)
				onButtonUp(key)
				return VRPointer.state()
			elseif cmd == "wrist" then
				local off = dominant == Enum.UserCFrame.RightHand and Enum.UserCFrame.LeftHand or Enum.UserCFrame.RightHand
				-- (stage ab) "club": the club hand's wrist in the watch pose instead (the card works on either wrist)
				if arg == "club" then
					off = dominant
				elseif arg == "down" then
					-- both hands well below the head (out of the 4-stud look range): the card hides
					for _, h in { Enum.UserCFrame.LeftHand, Enum.UserCFrame.RightHand } do
						local side = h == Enum.UserCFrame.RightHand and 1 or -1
						local rest = headW.Position + headW.RightVector * (0.7 * side) - Vector3.new(0, 4.4, 0)
						setHand(h, CFrame.lookAt(rest, rest + flat(headW.LookVector) + Vector3.new(0, -1, 0)))
					end
					return { hand = "both" }
				end
				local left = off == Enum.UserCFrame.LeftHand
				local side = left and -1 or 1
				local flatLook = flat(headW.LookVector)
				flatLook = flatLook.Magnitude > 1e-3 and flatLook.Unit or Vector3.new(0, 0, -1)
				local flatRight = flatLook:Cross(Vector3.yAxis)
				if arg then
					setHand(off, watchPose(headW, left))
				else
					setHand(off, CFrame.lookAt(headW.Position + flatRight * (0.6 * side) - Vector3.new(0, 2.6, 0), headW.Position + flatRight * (0.6 * side) - Vector3.new(0, 2.6, 0) + flatLook))
				end
				return { hand = off.Name }
			elseif cmd == "pose" then
				-- { head = {x, y, z}, look = {x, y, z}, club = {x, y, z}?, face = {x, y, z}? } in world space
				local function v3(t)
					return Vector3.new(t[1], t[2], t[3])
				end
				if arg.head then
					setHand(Enum.UserCFrame.Head, CFrame.lookAt(v3(arg.head), v3(arg.look)))
				end
				if arg.club then
					setHand(dominant, VR.test.handCFrameFor(v3(arg.club), v3(arg.face or { 1, 0, 0 })))
				end
				return { origin = { origin.X, origin.Y, origin.Z } }
			elseif cmd == "headBlend" then
				-- (stage ab) the putter head: level on / near the ground, rigid with the club when lifted (smooth blend).
				-- Club hand placed so the head rests on the felt beside the ball, then raised 0.35 (in the blend) and
				-- 2 studs (rigid) with the wrist rolled 30 deg about the aim axis. Reports the head's tilt from level.
				local b = Ball.ball and Ball.ball.Position
				if not b then
					return { error = "no ball" }
				end
				local fl = flat(headW.LookVector)
				fl = fl.Magnitude > 1e-3 and fl.Unit or Vector3.new(0, 0, -1)
				local spot = Vector3.new(b.X, b.Y - R + half.Y + 0.01, b.Z) + fl:Cross(Vector3.yAxis) * 1.5
				local base = VR.test.handCFrameFor(spot, fl)
				local function settle()
					for _ = 1, 6 do
						RunService.RenderStepped:Wait()
					end
					return math.deg(math.acos(math.clamp(head.CFrame.UpVector.Y, -1, 1))), head.Position.Y - spot.Y
				end
				local res = {}
				if setup.active then
					setup:cancel()
				end
				setHand(dominant, base)
				res.groundTilt, res.groundLift = settle()
				local roll = CFrame.fromAxisAngle(base.LookVector, math.rad(30))
				local function lifted(h)
					return CFrame.new(base.Position + Vector3.new(0, h, 0)) * roll * base.Rotation
				end
				setHand(dominant, lifted(0.55)) -- (the shaft stretches to keep the head down, so 0.55 lifts it ~0.3)
				res.midTilt, res.midLift = settle()
				setHand(dominant, lifted(2))
				res.liftedTilt, res.liftedLift = settle()
				-- rigid: the head keeps its club-frame relation as the hand rolls further while lifted
				local rel1 = (lastClubCF.Rotation:Inverse() * head.CFrame.Rotation)
				setHand(dominant, CFrame.new(base.Position + Vector3.new(0, 2, 0)) * CFrame.fromAxisAngle(base.LookVector, math.rad(50)) * base.Rotation)
				settle()
				local rel2 = (lastClubCF.Rotation:Inverse() * head.CFrame.Rotation)
				local d = rel1:Inverse() * rel2
				local _, ang = d:ToAxisAngle()
				res.rigidDriftDeg = math.deg(ang)
				setHand(dominant, base)
				res.backTilt = settle()
				res.headYaw = clubHeadYaw
				res.pass = res.groundTilt < 1 and res.midTilt > 1 and res.midTilt < res.liftedTilt and res.liftedTilt > 15
					and res.rigidDriftDeg < 1 and res.backTilt < 1
				return res
			elseif cmd == "offHandToggle" then
				onButtonDown(dominant == Enum.UserCFrame.RightHand and Enum.KeyCode.ButtonX or Enum.KeyCode.ButtonA)
				return HUD.wristState()
			elseif cmd == "clubAway" then
				local pos = headW.Position + headW.RightVector * 3 - Vector3.new(0,4,0)
				setHand(dominant,VR.test.handCFrameFor(pos,headW.RightVector))
				return true
			elseif cmd == "wristPalm" then
				local off = dominant == Enum.UserCFrame.RightHand and Enum.UserCFrame.LeftHand or Enum.UserCFrame.RightHand
				local pose = watchPose(headW,off == Enum.UserCFrame.LeftHand)
				local pivot = pose:PointToWorldSpace(Vector3.new(0,-0.12,0.33))
				local rot = pose.Rotation * CFrame.Angles(0,0,math.pi)
				setHand(off,CFrame.new(pivot-rot:VectorToWorldSpace(Vector3.new(0,-0.12,0.33)))*rot)
				return {hand=off.Name}
			elseif cmd == "randomStroke" then
				local rng = Random.new(tonumber(arg) or 617)
				local angle = rng:NextNumber(0,math.pi*2)
				local speed = rng:NextNumber(1.5,3)
				return {hit=Ball.hit(Vector3.new(math.cos(angle),0,math.sin(angle))*speed,"test"),angle=angle,speed=speed}
			elseif cmd == "regressionState" then
				local n=0
				for _,d in workspace:GetDescendants() do
					if d:IsA("BasePart") and d.LocalTransparencyModifier>0.01 and not d:IsDescendantOf(camera) and not (player.Character and d:IsDescendantOf(player.Character)) then n+=1 end
				end
				return {ballState=Ball.state,hole=player:GetAttribute("Hole"),strokes=player:GetAttribute("Strokes"),holed=player:GetAttribute("HoleHoled"),wrist=HUD.wristState(),fadeActive=fading,fadedParts=n}
			elseif cmd == "fadeGateTest" then
				if not Ball.ball then return {pass=false,error="no ball"} end
				local savedState,savedHead,savedAnchored=Ball.state,head.CFrame,Ball.ball.Anchored
				local states={}
				head.CFrame=CFrame.new(Ball.ball.Position+Vector3.new(0,0.1,0.5))
				for _,case in {{"aim","ready",false},{"rolling","moving",false},{"sunk","locked",true}} do
					Ball.state,Ball.ball.Anchored=case[2],case[3]
					fadeAt=0
					updateSeeThrough(headW.Position)
					states[case[1]]=fading
				end
				Ball.state,head.CFrame,Ball.ball.Anchored=savedState,savedHead,savedAnchored
				fadeAt=0;updateSeeThrough(headW.Position)
				return {pass=states.aim and not states.rolling and not states.sunk,states=states,fixture="synchronous local gate states; no shot"}
			elseif cmd == "clubSetup" then
				local action = type(arg) == "table" and arg.action or arg
				if action == "begin" then setup:begin()
				elseif action == "cancel" then setup:cancel()
				elseif action == "save" then onButtonDown(dominant == Enum.UserCFrame.RightHand and Enum.KeyCode.ButtonR2 or Enum.KeyCode.ButtonL2)
				elseif action == "reset" then setup:save(true)
				elseif action == "stick" then onStick(Enum.KeyCode.Thumbstick2,Vector2.new(arg.x or 0,arg.y or 0)) end
				local fit = setup.active and setup:solve() or nil
				return { active=setup.active, saving=setup.saving, hand=dominant.Name, fit=fit,
					target=setup.target and {setup.target.X,setup.target.Y,setup.target.Z}, saved=setup.fits[dominant.Name] }
			elseif cmd == "clubSetupTest" then
				local before = dominant
				onButtonDown(before == Enum.UserCFrame.RightHand and Enum.KeyCode.ButtonA or Enum.KeyCode.ButtonX)
				local noSwap = dominant == before
				-- (stage ab) start from a putting pose: the head on the felt beside the ball
				if Ball.ball then
					local bp = Ball.ball.Position
					local fl = flat(headW.LookVector)
					fl = fl.Magnitude > 1e-3 and fl.Unit or Vector3.new(0, 0, -1)
					setHand(dominant, VR.test.handCFrameFor(Vector3.new(bp.X, bp.Y - R + half.Y + 0.01, bp.Z) + fl:Cross(Vector3.yAxis) * 1.5, fl))
					for _ = 1, 4 do RunService.RenderStepped:Wait() end
				end
				setup:begin()
				local p0, yaw0 = setup.target, setup.headYaw
				onStick(Enum.KeyCode.Thumbstick2,Vector2.new(0.8,0.4))
				for _ = 1,20 do RunService.RenderStepped:Wait() end
				onStick(Enum.KeyCode.Thumbstick2,Vector2.zero)
				local fit = setup:solve()
				-- (stage ab) the stick turns the head (yaw) and no longer moves the ground target
				local moved = (setup.target-p0).Magnitude
				local yawTurned = setup.headYaw - yaw0
				local hand = worldPose(dominant)
				local solvedHead = hand:PointToWorldSpace(clubButt) + (hand.Rotation * clubOffset).LookVector * clubLength
				local err = (solvedHead-setup.target).Magnitude
				onButtonDown(dominant == Enum.UserCFrame.RightHand and Enum.KeyCode.ButtonR2 or Enum.KeyCode.ButtonL2)
				local t0 = os.clock()
				while setup.saving and os.clock()-t0<15 do task.wait(0.05) end
				local saved = setup.fits[dominant.Name] ~= nil and not setup.active
				local savedYaw = setup.fits[dominant.Name] and setup.fits[dominant.Name].headYaw
				return { noButtonHandChange=noSwap, targetMoved=moved, headYaw=yawTurned, savedHeadYaw=savedYaw, liveHeadYaw=clubHeadYaw, solveError=err,
					saved=saved, fit=fit, pass=noSwap and moved<0.02 and yawTurned>0.5 and savedYaw ~= nil and math.abs(savedYaw-clubHeadYaw)<1e-3 and err<0.02 and saved }
			elseif cmd == "state" then
				return { pointer = VRPointer.state(), wrist = HUD.wristState(), scorecard = HUD.isScorecardOpen(), menuOpen = Ball.menuOpen == true }
			elseif cmd == "wristSim" then
				HUD.wristEvents(nil, true) -- print show/hide events to the output from now on
				return wristSim(arg.scenario, arg.seed)
			end
			return nil
		end
		hook.Parent = player:WaitForChild("PlayerScripts")
	end
	VR.getState = function()
		return {
			origin = origin,
			clubLength = clubLength,
			head = head.CFrame,
			hand = worldPose(dominant),
			headVel = headVelocity(),
		}
	end

	-- Hooks for the Studio test harness (GolfClient.GolfTest, SimulateVR only).
	VR.test = {
		putter = putter,
		headSize = HEAD_SIZE,
		getOrigin = function()
			return origin
		end,
		ballPlaneY = ballPlaneY,
		placeHead = placeHead,
		-- Club-hand world CFrame that puts the putter head centre at `headPos` with the shaft straight down
		-- and the face pointing along `faceDir` (flat).
		handCFrameFor = function(headPos: Vector3, faceDir: Vector3)
			local right = flat(faceDir).Unit
			local back = Vector3.yAxis
			local clubRot = CFrame.fromMatrix(Vector3.zero, right, back:Cross(right), back)
			local handRot = clubRot * clubOffset.Rotation:Inverse()
			local butt = handRot:VectorToWorldSpace(clubButt)
			return CFrame.new(headPos - butt - clubRot.LookVector * clubLength) * handRot
		end,
		-- Club-hand world CFrame at `handPos` whose club shaft points along `shaftDir`, face normal ~ `faceDir`.
		handCFrameAlong = function(handPos: Vector3, shaftDir: Vector3, faceDir: Vector3)
			local back = -shaftDir.Unit
			local right = (faceDir - back * faceDir:Dot(back)).Unit
			local clubRot = CFrame.fromMatrix(Vector3.zero, right, back:Cross(right), back)
			return CFrame.new(handPos) * (clubRot * clubOffset.Rotation:Inverse())
		end,
		-- Club rotation that the club-hand pose maps to (hand space), the hand-space butt point, last club CFrame.
		getClubMount = function()
			return clubButt, clubOffset, lastClubCF
		end,
		-- Re-reads the default mount from Config (e.g. after toggling Config.VRClubLegacyAim) and unfits the club.
		resetClubMount = function()
			clubButt, clubOffset = defaultClubMount(dominant)
			teleportedThisFrame = true
		end,
		-- Club hand for test shots: Enum.UserCFrame.RightHand / LeftHand (re-reads the mirrored default mount).
		setDominant = function(hand: Enum.UserCFrame)
			dominant = hand
			clubButt, clubOffset = defaultClubMount(dominant)
			teleportedThisFrame = true
		end,
		getDominant = function()
			return dominant
		end,
		clubLength = function()
			return clubLength
		end,
		toLocal = function(worldCF: CFrame)
			return (origin * CFrame.new(0, -floorOffsetY, 0)):Inverse() * worldCF
		end,
	}
end

return VR
