-- Explore: free-roam mode for phone/desktop (Chase, 2026-10-10). Toggled from the HUD's Explore button.
--   * No ball and no scoring: the server parks your ball (GolfServer SetExplore) and "Back to golf" puts it back.
--   * Walk/run/jump with the normal Roblox controls (touch thumbstick + jump button), Sprint toggle (Shift),
--     Fly toggle (F; Space/E up, Q/Ctrl down, or the on-screen Up/Down buttons) so ledges and cliffs never trap you.
--   * Teleport menu: every hole's tee view plus the scenic viewpoints from ReplicatedStorage.Golf.ExploreData.
--   * Falling out of the world (or under it) puts you back on the nearest walkway point. The server's invisible
--     ExploreBounds walls (players only) keep you inside the terrain.
-- Everything here is local to this player; other players' rounds never see it.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local GuiService = game:GetService("GuiService")
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Remotes = Golf:WaitForChild("Remotes")

local player = Players.LocalPlayer

local Explore = {}
Explore.active = false
Explore.Changed = Instance.new("BindableEvent") -- (active)

local WALK_SPEED, SPRINT_SPEED = 16, 30
local FLY_SPEED, FLY_SPRINT_SPEED = 30, 70
local JUMP_POWER = 38
local REAL_GRAVITY = 196.2 -- the course runs at 32.7 (life-size ball); walking feels floaty at that, so a local
-- downward force tops the character up to Roblox's usual gravity while exploring
local FALL_Y = -4 -- below the lowest terrain (y 0): respawn on a walkway
local CEILING_Y = 320

local Ball, HUD, controls
local data = { views = {}, paths = {} }
local sprint, flying = false, false
local flyUp, flyDown = 0, 0
local lastSafe: Vector3? = nil
local savedCamera = nil

local function character()
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	local hrp = char and char:FindFirstChild("HumanoidRootPart")
	return char, hum, hrp
end

local function loadData()
	local v = Golf:FindFirstChild("ExploreData") or Golf:WaitForChild("ExploreData", 5)
	if v then
		local ok, d = pcall(HttpService.JSONDecode, HttpService, v.Value)
		if ok then
			data = d
		end
	end
end

local groundRay = RaycastParams.new()
groundRay.CollisionGroup = "GolfPlayer"
groundRay.FilterType = Enum.RaycastFilterType.Exclude
groundRay.IgnoreWater = false

-- the first solid (or water) surface under (x, z), from high above
local function groundAt(x, z, fromY)
	local char = player.Character
	groundRay.FilterDescendantsInstances = { char, workspace:FindFirstChild("Balls"), workspace.CurrentCamera }
	local hit = workspace:Raycast(Vector3.new(x, fromY or 400, z), Vector3.new(0, -(fromY or 400) - 50, 0), groundRay)
	return hit and hit.Position or Vector3.new(x, 40, z)
end

local function forces(hrp)
	local att = hrp:FindFirstChild("RootAttachment") or hrp:FindFirstChildOfClass("Attachment")
	local g = hrp:FindFirstChild("ExploreGravity")
	if not g then
		g = Instance.new("VectorForce")
		g.Name = "ExploreGravity"
		g.RelativeTo = Enum.ActuatorRelativeTo.World
		g.ApplyAtCenterOfMass = true
		g.Attachment0 = att
		g.Parent = hrp
	end
	local lv = hrp:FindFirstChild("ExploreFly")
	if not lv then
		lv = Instance.new("LinearVelocity")
		lv.Name = "ExploreFly"
		lv.Attachment0 = att
		lv.MaxForce = math.huge
		lv.RelativeTo = Enum.ActuatorRelativeTo.World
		lv.Enabled = false
		lv.Parent = hrp
	end
	local ao = hrp:FindFirstChild("ExploreFlyTurn")
	if not ao then
		ao = Instance.new("AlignOrientation")
		ao.Name = "ExploreFlyTurn"
		ao.Mode = Enum.OrientationAlignmentMode.OneAttachment
		ao.Attachment0 = att
		ao.RigidityEnabled = true
		ao.Enabled = false
		ao.Parent = hrp
	end
	return g, lv, ao
end

local function clearForces(char)
	local hrp = char and char:FindFirstChild("HumanoidRootPart")
	if hrp then
		for _, n in { "ExploreGravity", "ExploreFly", "ExploreFlyTurn" } do
			local f = hrp:FindFirstChild(n)
			if f then
				f:Destroy()
			end
		end
	end
end

local function applySpeed()
	local _, hum = character()
	if hum then
		hum.WalkSpeed = sprint and SPRINT_SPEED or WALK_SPEED
	end
end

function Explore.setSprint(on)
	sprint = on
	applySpeed()
	Explore.Changed:Fire(Explore.active)
end

function Explore.setFly(on)
	flying = on and Explore.active
	local _, hum, hrp = character()
	if hum and hrp then
		local _, lv, ao = forces(hrp)
		lv.Enabled = flying
		ao.Enabled = flying
		hum.PlatformStand = flying
		if not flying then
			hum:ChangeState(Enum.HumanoidStateType.Freefall)
		end
	end
	flyUp, flyDown = 0, 0
	Explore.Changed:Fire(Explore.active)
end

function Explore.isSprinting()
	return sprint
end

function Explore.isFlying()
	return flying
end

function Explore.setFlyVertical(up, down)
	flyUp, flyDown = up and 1 or 0, down and 1 or 0
end

-- Put the character (standing) at a spot, facing `look`.
local function placeCharacter(pos: Vector3, look: Vector3?)
	local char, hum, hrp = character()
	if not (char and hum and hrp) then
		return
	end
	local y = pos.Y + hum.HipHeight + hrp.Size.Y / 2 + 0.2
	local p = Vector3.new(pos.X, y, pos.Z)
	local dir = look and Vector3.new(look.X - p.X, 0, look.Z - p.Z) or Vector3.new(0, 0, -1)
	if dir.Magnitude < 0.1 then
		dir = Vector3.new(0, 0, -1)
	end
	char:PivotTo(CFrame.lookAt(p, p + dir.Unit))
	hrp.AssemblyLinearVelocity = Vector3.zero
	lastSafe = p
	-- camera behind the character, looking where it faces (or up at the subject for the scenic views)
	local cam = workspace.CurrentCamera
	if cam.CameraType == Enum.CameraType.Custom then
		local target = look or (p + dir.Unit * 10)
		-- (high enough to clear the meadow's tall Terrain grass blades)
		cam.CFrame = CFrame.lookAt(p - dir.Unit * 9 + Vector3.new(0, 6.5, 0), target)
	end
end

-- Teleport destinations: hole tees (standing a few studs behind the tee, looking down the hole) + scenic views.
function Explore.destinations()
	local list = {}
	local holes = {}
	for _, h in workspace.Course:GetChildren() do
		local n = h:GetAttribute("HoleNumber")
		if n then
			holes[n] = h
		end
	end
	for n = 1, #holes do
		local h = holes[n]
		local tee = h:FindFirstChild("Tee")
		if tee then
			local aim = h:FindFirstChild("AimTarget") or h:FindFirstChild("Cup")
			table.insert(list, {
				kind = "hole",
				name = "H" .. n,
				title = string.format("Hole %d - %s", n, h:GetAttribute("HoleName") or ""),
				tee = tee,
				aim = aim,
			})
		end
	end
	for _, v in data.views or {} do
		table.insert(list, { kind = "view", name = v.name, title = v.name, xz = v.pos, look = v.look })
	end
	return list
end

function Explore.teleport(dest)
	if not Explore.active then
		return
	end
	if dest.kind == "hole" then
		local tee = dest.tee
		local aimPos = dest.aim and dest.aim.Position or (tee.Position + tee.CFrame.LookVector * 10)
		local d = Vector3.new(aimPos.X - tee.Position.X, 0, aimPos.Z - tee.Position.Z)
		d = d.Magnitude > 0.1 and d.Unit or Vector3.new(0, 0, -1)
		local spot = tee.Position - d * 4
		local g = groundAt(spot.X, spot.Z, tee.Position.Y + 30)
		-- inside the hollow tree (H9) a high ray hits the canopy/roof: start just above the tee instead
		if g.Y > tee.Position.Y + 6 then
			g = groundAt(spot.X, spot.Z, tee.Position.Y + 4)
		end
		placeCharacter(g, aimPos)
	else
		local g = groundAt(dest.xz[1], dest.xz[2])
		local look = dest.look and Vector3.new(dest.look[1], dest.look[2], dest.look[3])
		placeCharacter(g, look)
	end
	HUD.toast(dest.title)
end

-- Nearest walkway point (spawn plaza -> H9 paths) to where we fell from.
local function respawnNearPath(from: Vector3)
	local best, bestD = nil, math.huge
	for _, p in data.paths or {} do
		local d = (Vector3.new(p[1], 0, p[3]) - Vector3.new(from.X, 0, from.Z)).Magnitude
		if d < bestD then
			best, bestD = p, d
		end
	end
	if best then
		local g = groundAt(best[1], best[3], best[2] + 8)
		placeCharacter(g, nil)
	elseif lastSafe then
		placeCharacter(lastSafe - Vector3.new(0, 3, 0), nil)
	end
	HUD.toast("Back on the path")
end

local function inWorld(p: Vector3)
	local b = data.bounds
	if not b then
		return true
	end
	return p.X > b.x[1] and p.X < b.x[2] and p.Z > b.z[1] and p.Z < b.z[2]
end

-- Character setup for each mode. Golf: frozen in place (GolfMain/TouchControls stand it beside the ball).
local function applyCharacter()
	local char, hum, hrp = character()
	if not (char and hum) then
		return
	end
	if Explore.active then
		if controls then
			controls:Enable()
		end
		hum.UseJumpPower = true
		hum.JumpPower = JUMP_POWER
		hum.AutoRotate = true
		hum.PlatformStand = false
		applySpeed()
		if hrp then
			local g = forces(hrp)
			g.Force = Vector3.new(0, -hrp.AssemblyMass * (REAL_GRAVITY - workspace.Gravity), 0)
		end
		for _, d in char:GetDescendants() do
			if d:IsA("BasePart") or d:IsA("Decal") then
				d.LocalTransparencyModifier = 0
			end
		end
	else
		clearForces(char)
		hum.PlatformStand = false
		if controls then
			controls:Disable()
		end
		hum.WalkSpeed = 0
		hum.JumpPower = 0
		hum.JumpHeight = 0
		hum.AutoRotate = false
	end
end

function Explore.applyCharacter()
	applyCharacter()
end

function Explore.setActive(on)
	if on == Explore.active or HUD.isVR then
		return
	end
	Explore.active = on
	Ball.exploreActive = on
	local cam = workspace.CurrentCamera
	local _, hum = character()
	if on then
		Remotes.SetExplore:FireServer(true)
		sprint, flying = false, false
		savedCamera = cam.CFrame
		pcall(function()
			GuiService.TouchControlsEnabled = true
		end)
		applyCharacter()
		cam.CameraType = Enum.CameraType.Custom
		if hum then
			cam.CameraSubject = hum
		end
		HUD.message("Explore!  No ball, no score.  Back to golf any time", Color3.fromRGB(150, 220, 255), 2.5)
	else
		Explore.setFly(false)
		sprint = false
		pcall(function()
			GuiService.TouchControlsEnabled = false
		end)
		applyCharacter()
		cam.CameraType = Enum.CameraType.Scriptable
		Remotes.SetExplore:FireServer(false)
	end
	Explore.Changed:Fire(on)
end

function Explore.toggle()
	Explore.setActive(not Explore.active)
end

function Explore.start(ballController, hud, controlModule)
	Ball, HUD, controls = ballController, hud, controlModule
	task.spawn(loadData)

	player.CharacterAdded:Connect(function(char)
		char:WaitForChild("Humanoid", 10)
		char:WaitForChild("HumanoidRootPart", 10)
		flying = false
		applyCharacter()
		if Explore.active then
			local hum = char:FindFirstChildOfClass("Humanoid")
			if hum then
				workspace.CurrentCamera.CameraSubject = hum
			end
			Explore.Changed:Fire(true)
		end
	end)

	-- (not gameProcessed: the control scripts' own Space/Shift bindings mark those keys processed; only skip typing)
	UserInputService.InputBegan:Connect(function(input)
		if not Explore.active or UserInputService:GetFocusedTextBox() then
			return
		end
		local k = input.KeyCode
		if k == Enum.KeyCode.LeftShift or k == Enum.KeyCode.RightShift then
			Explore.setSprint(true)
		elseif k == Enum.KeyCode.F then
			Explore.setFly(not flying)
		elseif k == Enum.KeyCode.Space or k == Enum.KeyCode.E then
			flyUp = 1
		elseif k == Enum.KeyCode.Q or k == Enum.KeyCode.LeftControl then
			flyDown = 1
		elseif k == Enum.KeyCode.T then
			HUD.toggleTeleportMenu()
		end
	end)
	UserInputService.InputEnded:Connect(function(input)
		local k = input.KeyCode
		if k == Enum.KeyCode.LeftShift or k == Enum.KeyCode.RightShift then
			if Explore.active and sprint and not UserInputService.TouchEnabled then
				Explore.setSprint(false)
			end
		elseif k == Enum.KeyCode.Space or k == Enum.KeyCode.E then
			flyUp = 0
		elseif k == Enum.KeyCode.Q or k == Enum.KeyCode.LeftControl then
			flyDown = 0
		end
	end)

	-- Studio-only hook for the playtest runner (an MCP require() gets its own module copy, so it drives this one)
	if RunService:IsStudio() then
		local hook = Instance.new("BindableFunction")
		hook.Name = "GolfExploreDebug"
		hook.OnInvoke = function(cmd, arg)
			if cmd == "on" or cmd == "off" then
				-- (deferred: the MCP execute_luau tool puts back any CameraType change made during its call)
				task.delay(0.5, Explore.setActive, cmd == "on")
			elseif cmd == "fly" then
				Explore.setFly(arg == true)
			elseif cmd == "sprint" then
				Explore.setSprint(arg == true)
			elseif cmd == "vertical" then
				Explore.setFlyVertical(arg == 1, arg == -1)
			elseif cmd == "teleport" then
				for _, d in Explore.destinations() do
					if d.name == arg then
						Explore.teleport(d)
						break
					end
				end
			elseif cmd == "menu" then
				HUD.toggleTeleportMenu()
			elseif cmd == "scorecard" then
				HUD.toggleScorecard()
			end
			local _, hum, hrp = character()
			return {
				active = Explore.active,
				flying = flying,
				sprint = sprint,
				walkSpeed = hum and hum.WalkSpeed,
				pos = hrp and { hrp.Position.X, hrp.Position.Y, hrp.Position.Z },
				floor = hum and tostring(hum.FloorMaterial),
				camType = tostring(workspace.CurrentCamera.CameraType),
				dests = #Explore.destinations(),
			}
		end
		hook.Parent = player:WaitForChild("PlayerScripts")
	end

	local checkT = 0
	RunService.Heartbeat:Connect(function(dt)
		if not Explore.active then
			return
		end
		local _, hum, hrp = character()
		if not (hum and hrp) or hum.Health <= 0 then
			return
		end
		if flying then
			local cam = workspace.CurrentCamera
			local mv = controls and controls:GetMoveVector() or Vector3.zero
			-- camera-relative: look up and push forward to climb
			local dir = cam.CFrame:VectorToWorldSpace(mv)
			if dir.Magnitude > 1 then
				dir = dir.Unit
			end
			local speed = sprint and FLY_SPRINT_SPEED or FLY_SPEED
			local vel = dir * speed + Vector3.new(0, (flyUp - flyDown) * speed * 0.7, 0)
			if hrp.Position.Y > CEILING_Y and vel.Y > 0 then
				vel = Vector3.new(vel.X, 0, vel.Z)
			end
			local _, lv, ao = forces(hrp)
			lv.VectorVelocity = vel
			local flatLook = Vector3.new(cam.CFrame.LookVector.X, 0, cam.CFrame.LookVector.Z)
			if flatLook.Magnitude > 0.1 then
				ao.CFrame = CFrame.lookAt(Vector3.zero, flatLook.Unit)
			end
		end
		checkT += dt
		if checkT < 0.25 then
			return
		end
		checkT = 0
		local p = hrp.Position
		if p.Y < FALL_Y or not inWorld(p) then
			Explore.setFly(false)
			respawnNearPath(lastSafe or p)
		elseif hum.FloorMaterial ~= Enum.Material.Air and hum.FloorMaterial ~= Enum.Material.Water then
			lastSafe = p
		end
	end)
end

return Explore
