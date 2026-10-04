-- TouchControls: 2D controls for phones/tablets (and mouse on desktop).
--   * Press near the ball and pull back: distance = power, sideways = angle. Release to putt.
--   * Drag anywhere else to orbit the camera, pinch (or mouse wheel) to zoom.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage:WaitForChild("Golf"):WaitForChild("Config"))

local player = Players.LocalPlayer
local R = Config.BallRadius

local Touch = {}

local DOTS = 12
local MIN_PITCH, MAX_PITCH = math.rad(12), math.rad(80)
local MIN_DIST, MAX_DIST = 2, 30

local function flat(v: Vector3)
	return Vector3.new(v.X, 0, v.Z)
end

local function yawToward(dir: Vector3)
	return math.atan2(-dir.X, -dir.Z)
end

function Touch.start(Ball, HUD)
	local camera = workspace.CurrentCamera
	camera.CameraType = Enum.CameraType.Scriptable
	camera:GetPropertyChangedSignal("CameraType"):Connect(function()
		if camera.CameraType ~= Enum.CameraType.Scriptable then
			camera.CameraType = Enum.CameraType.Scriptable
		end
	end)

	local yaw, pitch, dist = math.pi, math.rad(30), 6
	local focus: Vector3? = nil

	local camRay = RaycastParams.new()
	camRay.CollisionGroup = "GolfClub" -- ignores balls and players
	camRay.FilterType = Enum.RaycastFilterType.Exclude

	---------------------------------------------------------------- aim visuals
	local aimFolder = Instance.new("Folder")
	aimFolder.Name = "AimDots"
	aimFolder.Parent = camera
	local dots = {}
	for i = 1, DOTS do
		local d = Instance.new("Part")
		d.Shape = Enum.PartType.Ball
		d.Size = Vector3.one * 0.2
		d.Anchored = true
		d.CanCollide = false
		d.CanQuery = false
		d.CanTouch = false
		d.CastShadow = false
		d.Material = Enum.Material.Neon
		d.Transparency = 1
		d.Parent = aimFolder
		dots[i] = d
	end

	local function hideAim()
		for _, d in dots do
			d.Transparency = 1
		end
		HUD.hidePower()
	end

	local function powerColor(p)
		if p < 0.5 then
			return Color3.fromRGB(90, 230, 90):Lerp(Color3.fromRGB(255, 220, 60), p * 2)
		end
		return Color3.fromRGB(255, 220, 60):Lerp(Color3.fromRGB(255, 70, 60), (p - 0.5) * 2)
	end

	---------------------------------------------------------------- character placement (cosmetic stance)
	local standRay = RaycastParams.new()
	standRay.CollisionGroup = "GolfClub"
	standRay.FilterType = Enum.RaycastFilterType.Exclude

	local function standBesideBall(shotDir: Vector3)
		local char = player.Character
		local hrp = char and char:FindFirstChild("HumanoidRootPart")
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		if not (hrp and hum and Ball.ball) or shotDir.Magnitude < 1e-3 then
			return
		end
		shotDir = flat(shotDir).Unit
		local right = Vector3.new(-shotDir.Z, 0, shotDir.X)
		local spot = Ball.ball.Position - right * 1.7
		standRay.FilterDescendantsInstances = { char }
		local hit = workspace:Raycast(spot + Vector3.new(0, 4, 0), Vector3.new(0, -12, 0), standRay)
		local groundY = hit and hit.Position.Y or (Ball.ball.Position.Y - R)
		local y = groundY + hum.HipHeight + hrp.Size.Y / 2
		local p = Vector3.new(spot.X, y, spot.Z)
		char:PivotTo(CFrame.lookAt(p, p + right))
		hrp.AssemblyLinearVelocity = Vector3.zero
		-- keep our own avatar from blocking the view of the ball (others still see it normally)
		for _, d in char:GetDescendants() do
			if d:IsA("BasePart") or d:IsA("Decal") then
				d.LocalTransparencyModifier = 0.75
			end
		end
	end

	---------------------------------------------------------------- input
	local touches = {} -- [InputObject] = Vector2
	local mode: string? = nil -- "aim" | "orbit" | "pinch"
	local aimInput: InputObject? = nil
	local aimStart = Vector2.zero
	local aimCurrent = Vector2.zero
	local lastOrbit = Vector2.zero
	local pinchDist0, dist0 = 0, dist
	local mouseDown = false

	local function countTouches()
		local n = 0
		for _ in touches do
			n += 1
		end
		return n
	end

	local function ballScreenPos()
		local p, onScreen = camera:WorldToScreenPoint(Ball.ball.Position)
		return Vector2.new(p.X, p.Y), onScreen
	end

	local function nearBall(pos: Vector2)
		if not Ball.ball then
			return false
		end
		local sp, onScreen = ballScreenPos()
		if not onScreen then
			return false
		end
		local vp = camera.ViewportSize
		local radius = math.max(70, math.min(vp.X, vp.Y) * 0.2)
		return (pos - sp).Magnitude <= radius
	end

	-- screen drag -> world shot direction + power (0..1)
	local function computeShot()
		local d = aimCurrent - aimStart
		local vp = camera.ViewportSize
		local scale = math.min(vp.X, vp.Y) * 0.42
		local power = math.clamp(d.Magnitude / scale, 0, 1)
		local f = flat(camera.CFrame.LookVector)
		local r = flat(camera.CFrame.RightVector)
		if f.Magnitude < 1e-3 or r.Magnitude < 1e-3 then
			return nil, 0
		end
		-- pulling down/back shoots forward, pulling left shoots right (slingshot)
		local dir = f.Unit * d.Y + r.Unit * -d.X
		if dir.Magnitude < 1e-3 then
			return nil, 0
		end
		return dir.Unit, power
	end

	local function updateAim()
		local dir, power = computeShot()
		if not dir or power < 0.03 then
			for _, d in dots do
				d.Transparency = 1
			end
			HUD.showPower(0, aimStart, aimCurrent)
			return
		end
		local color = powerColor(power)
		local origin = Ball.ball.Position - Vector3.new(0, R * 0.5, 0)
		local spacing = 0.18 + power * 0.7
		for i, d in dots do
			d.Color = color
			d.Transparency = 0.1 + (i / DOTS) * 0.6
			local s = (0.09 - (i / DOTS) * 0.04) * math.clamp(dist / 6, 0.8, 3)
			d.Size = Vector3.one * s
			d.CFrame = CFrame.new(origin + dir * (0.2 + spacing * i))
		end
		HUD.showPower(power, aimStart, aimCurrent, color)
		standBesideBall(dir)
	end

	local function beginAim(input, pos)
		mode = "aim"
		aimInput = input
		aimStart = pos
		aimCurrent = pos
		updateAim()
	end

	local function cancelAim()
		if mode == "aim" then
			mode = nil
		end
		aimInput = nil
		hideAim()
	end

	local function releaseAim()
		local dir, power = computeShot()
		cancelAim()
		if dir and power >= 0.03 and Ball.canHit() then
			local speed = Config.TouchMaxSpeed * power ^ Config.TouchPowerCurve
			Ball.hit(dir * math.max(speed, 0.8))
		end
	end

	local function pinchDistance()
		local a, b
		for _, p in touches do
			if not a then
				a = p
			elseif not b then
				b = p
			end
		end
		return (a and b) and (a - b).Magnitude or 0
	end

	UserInputService.InputBegan:Connect(function(input, gameProcessed)
		if gameProcessed then
			return
		end
		local pos = Vector2.new(input.Position.X, input.Position.Y)
		if input.UserInputType == Enum.UserInputType.Touch then
			touches[input] = pos
			local n = countTouches()
			if n == 1 then
				if Ball.canHit() and nearBall(pos) then
					beginAim(input, pos)
				else
					mode = "orbit"
					lastOrbit = pos
				end
			elseif n == 2 then
				cancelAim()
				mode = "pinch"
				pinchDist0 = pinchDistance()
				dist0 = dist
			end
		elseif input.UserInputType == Enum.UserInputType.MouseButton1 then
			mouseDown = true
			if Ball.canHit() and nearBall(pos) then
				beginAim(input, pos)
			else
				mode = "orbit"
				lastOrbit = pos
			end
		elseif input.UserInputType == Enum.UserInputType.MouseButton2 then
			cancelAim()
			mode = "orbit"
			lastOrbit = pos
			mouseDown = true
		elseif input.KeyCode == Enum.KeyCode.R then
			Ball.requestReset()
		end
	end)

	local function orbitBy(delta: Vector2)
		yaw -= delta.X * 0.008
		pitch = math.clamp(pitch + delta.Y * 0.006, MIN_PITCH, MAX_PITCH)
	end

	UserInputService.InputChanged:Connect(function(input)
		local pos = Vector2.new(input.Position.X, input.Position.Y)
		if input.UserInputType == Enum.UserInputType.Touch then
			if touches[input] == nil then
				return
			end
			touches[input] = pos
			if mode == "aim" and input == aimInput then
				aimCurrent = pos
				updateAim()
			elseif mode == "orbit" then
				orbitBy(pos - lastOrbit)
				lastOrbit = pos
			elseif mode == "pinch" then
				local pd = pinchDistance()
				if pinchDist0 > 10 and pd > 10 then
					dist = math.clamp(dist0 * pinchDist0 / pd, MIN_DIST, MAX_DIST)
				end
			end
		elseif input.UserInputType == Enum.UserInputType.MouseMovement and mouseDown then
			if mode == "aim" then
				aimCurrent = pos
				updateAim()
			elseif mode == "orbit" then
				orbitBy(pos - lastOrbit)
				lastOrbit = pos
			end
		elseif input.UserInputType == Enum.UserInputType.MouseWheel then
			dist = math.clamp(dist * (1 - input.Position.Z * 0.12), MIN_DIST, MAX_DIST)
		end
	end)

	UserInputService.InputEnded:Connect(function(input)
		if input.UserInputType == Enum.UserInputType.Touch then
			if mode == "aim" and input == aimInput then
				releaseAim()
			end
			touches[input] = nil
			local n = countTouches()
			if n == 0 then
				mode = nil
			elseif n == 1 and mode == "pinch" then
				mode = "orbit"
				for _, p in touches do
					lastOrbit = p
				end
			end
		elseif input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.MouseButton2 then
			if mode == "aim" and input.UserInputType == Enum.UserInputType.MouseButton1 then
				releaseAim()
			end
			mouseDown = false
			mode = nil
		end
	end)

	-- cancel aiming if the ball stops being hittable mid-drag
	Ball.StateChanged.Event:Connect(function(state)
		if state ~= "ready" and mode == "aim" then
			cancelAim()
		end
		if state == "ready" and Ball.ball then
			local toTarget = flat(Ball.getAimPoint() - Ball.ball.Position)
			standBesideBall(toTarget.Magnitude > 0.1 and toTarget or flat(camera.CFrame.LookVector))
		end
	end)

	-- new hole / reset: point the camera at the target
	Ball.Placed.Event:Connect(function(pos, reason)
		focus = pos
		if reason == "hole" then
			local hole = Ball.getHole()
			local aim = hole:FindFirstChild("AimTarget") or hole.Cup
			local dir = flat(aim.Position - pos)
			if dir.Magnitude > 0.1 then
				yaw = yawToward(dir)
			end
			pitch = math.rad(30)
			dist = 6
		end
	end)

	---------------------------------------------------------------- camera
	RunService:BindToRenderStep("GolfCamera", Enum.RenderPriority.Camera.Value + 1, function(dt)
		local b = Ball.ball
		if not b then
			return
		end
		local target = b.Position + Vector3.new(0, 0.25, 0)
		if not focus then
			focus = target
		end
		focus = focus:Lerp(target, 1 - math.exp(-dt * 7))
		local rot = CFrame.fromEulerAnglesYXZ(-pitch, yaw, 0)
		local desired = focus - rot.LookVector * dist
		camRay.FilterDescendantsInstances = { player.Character, camera }
		local hit = workspace:Raycast(focus, desired - focus, camRay)
		if hit then
			desired = hit.Position + hit.Normal * 0.4
		end
		camera.CFrame = CFrame.lookAt(desired, focus)
		if mode == "aim" then
			updateAim()
		end
	end)
end

return Touch
