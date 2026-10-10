-- BallController: owns the local player's ball on the client.
-- Applies rolling resistance, decides when the ball is at rest, and exposes Ball.hit(), the one function
-- every shot goes through (VR putter contact, phone/mouse pull-back, and the Studio test harness).
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Config = require(Golf:WaitForChild("Config"))
local Remotes = Golf:WaitForChild("Remotes")

local player = Players.LocalPlayer
local R = Config.BallRadius

local Ball = {}
Ball.ball = nil :: BasePart?
Ball.state = "waiting" -- waiting | ready | moving | locked
Ball.holeIndex = 1
Ball.StateChanged = Instance.new("BindableEvent")
Ball.Placed = Instance.new("BindableEvent") -- (pos, reason)
Ball.Stroked = Instance.new("BindableEvent") -- (velocity, source)
Ball.Teleported = Instance.new("BindableEvent") -- (teleportId, speedIn, speedOut)
Ball.Unstuck = Instance.new("BindableEvent") -- (reason, fromPos, toPos): pinned by / riding a moving part
Ball.OffSurface = Instance.new("BindableEvent") -- (pos, partName): came to rest somewhere that isn't felt
Ball.ForcedRest = Instance.new("BindableEvent") -- (pos, reason): "maxtime" | "wedged"
Ball.AutoReset = Instance.new("BindableEvent") -- (pos, reason): stuck for the hole's AutoResetStill seconds -> free reset

local slowTime = 0
local rollTime = 0
-- skid after an obstacle hit: the (flat) velocity the ball's spin would roll at, or nil while rolling cleanly
local rollVel: Vector3? = nil
local lastVel: Vector3? = nil -- flat velocity we left the ball with last step
local placeToken = 0
local readyRing: BasePart
local stillTime = 0 -- seconds below StopSpeed whatever the slope (a ball wedged on a bank)
local pinTime = 0 -- seconds pinned against / riding on a moving part
local seamHops = 0 -- seam hops used this stroke (see step)
local parkTime = 0 -- seconds with the ball practically motionless (< 0.05 studs/s) on a slope
local teleportCooldown = 0
local stuckTime = 0 -- seconds the ball has made no progress (see checkAutoReset)
local stuckAnchor: Vector3? = nil
local strokeTime = 0 -- seconds the ball has been moving since it was hit or last came to rest (see Config.StrokeTimeout)

local rayParams = RaycastParams.new()
rayParams.CollisionGroup = "GolfBall"
rayParams.FilterType = Enum.RaycastFilterType.Exclude
rayParams.IgnoreWater = true

local hitSound = Instance.new("Sound")
hitSound.SoundId = "rbxasset://sounds/clickfast.wav"
hitSound.Volume = 0.8
hitSound.Parent = script

function Ball.setState(s)
	if Ball.state ~= s then
		Ball.state = s
		Ball.StateChanged:Fire(s)
	end
end

function Ball.getHole()
	if Ball.holeIndex == 0 then
		return workspace:FindFirstChild("GolfTestLane") -- Studio test harness only
	end
	return workspace.Course:FindFirstChild("Hole" .. Ball.holeIndex)
end

-- Where the player should be aiming from the ball's current spot (handles doglegs).
function Ball.getAimPoint(fromPos: Vector3?)
	local hole = Ball.getHole()
	local cup = hole.Cup.Position
	local aim = hole:FindFirstChild("AimTarget")
	local p = fromPos or (Ball.ball and Ball.ball.Position)
	if not p or not aim then
		return cup
	end
	local function flat(v)
		return Vector3.new(v.X, 0, v.Z)
	end
	if (flat(p) - flat(aim.Position)).Magnitude < 6 or (flat(p) - flat(cup)).Magnitude < (flat(aim.Position) - flat(cup)).Magnitude then
		return cup
	end
	return aim.Position
end

function Ball.isOwner()
	return Ball.ball ~= nil and Ball.ball.ReceiveAge == 0
end

function Ball.canHit()
	return Ball.state == "ready" and Ball.ball ~= nil and not Ball.ball.Anchored
end

-- Ball velocity from a putter contact: face normal `n` (flat, unit) and putter head velocity `clubVel`.
function Ball.clubImpulse(n: Vector3, clubVel: Vector3): Vector3?
	local u = clubVel:Dot(n)
	if u < Config.VRMinHitSpeed then
		return nil
	end
	local t = clubVel - n * u
	local tangential = Vector3.new(t.X, 0, t.Z)
	return n * u * Config.VRHitMultiplier + tangential * Config.VRTangentialTransfer
end

-- source: "vr" | "touch" | "test"
function Ball.hit(velocity: Vector3, source: string?)
	if not Ball.canHit() then
		return false
	end
	local b = Ball.ball
	velocity = Vector3.new(velocity.X, math.max(velocity.Y, 0), velocity.Z)
	if velocity.Magnitude > Config.MaxBallSpeed then
		velocity = velocity.Unit * Config.MaxBallSpeed
	end
	local startPos = b.Position
	b.AssemblyLinearVelocity = velocity
	-- start it already rolling (a putt imparts roll almost immediately); otherwise the ball skids
	-- and loses ~30% of its speed converting to spin
	b.AssemblyAngularVelocity = Vector3.yAxis:Cross(Vector3.new(velocity.X, 0, velocity.Z)) / R
	slowTime = 0
	rollTime = 0
	stillTime = 0
	pinTime = 0
	seamHops = 0
	parkTime = 0
	strokeTime = 0
	rollVel = nil
	lastVel = nil
	Ball.setState("moving")
	Remotes.Stroke:FireServer(startPos)
	hitSound.PlaybackSpeed = 0.8 + math.clamp(velocity.Magnitude / 40, 0, 0.6)
	hitSound.Volume = 0.3 + math.clamp(velocity.Magnitude / 30, 0, 0.7)
	hitSound:Play()
	Ball.Stroked:Fire(velocity, source or "unknown")
	return true
end

function Ball.requestReset()
	Remotes.RequestReset:FireServer()
end

local function groundInfo(b)
	local hit = workspace:Raycast(b.Position, Vector3.new(0, -(R + 0.15), 0), rayParams)
	if not hit then
		return nil, 0
	end
	local n = hit.Normal
	local slopeAccel = workspace.Gravity * math.sqrt(math.max(0, 1 - n.Y * n.Y))
	return hit, slopeAccel
end

-- Sit the ball exactly on the surface (contact slop otherwise leaves a small ball visibly sunk in).
local function settleOnGround(b)
	local hit = workspace:Raycast(b.Position + Vector3.new(0, 0.3, 0), Vector3.new(0, -0.3 - R - 0.2, 0), rayParams)
	if hit and hit.Normal.Y > 0.97 then
		local p = b.Position
		b.CFrame = CFrame.new(p.X, hit.Position.Y + R + 0.001, p.Z)
	end
end

local function flat(v: Vector3)
	return Vector3.new(v.X, 0, v.Z)
end

local function rest(b)
	strokeTime = 0
	rollVel = nil
	lastVel = nil
	b.AssemblyLinearVelocity = Vector3.zero
	b.AssemblyAngularVelocity = Vector3.zero
	settleOnGround(b)
	Ball.setState("ready")
	Remotes.BallRest:FireServer(b.Position)
	-- resting somewhere that isn't felt (on a rail top, a base, a moving part): free reset to the stroke start
	local hit = workspace:Raycast(b.Position + Vector3.new(0, 0.05, 0), Vector3.new(0, -(R + 0.3), 0), rayParams)
	local hole = Ball.getHole()
	local cup = hole and hole:FindFirstChild("Cup")
	local inCup = cup and flat(b.Position - cup.Position).Magnitude < (cup:GetAttribute("Radius") or 0.5)
	if not inCup and not (hit and CollectionService:HasTag(hit.Instance, "GolfSurface")) then
		Ball.OffSurface:Fire(b.Position, hit and hit.Instance.Name or "nothing")
		Remotes.RequestReset:FireServer()
	end
end

-- Distance from `pos` to an oriented box part's surface (0 inside).
local function boxDistance(part: BasePart, pos: Vector3)
	local lp = part.CFrame:PointToObjectSpace(pos)
	local h = part.Size / 2
	local c = Vector3.new(math.clamp(lp.X, -h.X, h.X), math.clamp(lp.Y, -h.Y, h.Y), math.clamp(lp.Z, -h.Z, h.Z))
	return (lp - c).Magnitude
end

local function holeParts(hole, filter)
	local out = {}
	for _, d in hole:GetDescendants() do
		if d:IsA("BasePart") and filter(d) then
			table.insert(out, d)
		end
	end
	return out
end

-- Rail rub: a slow ball that reaches a static rail just as it tops out on a slope stays sunk ~0.002 studs into
-- the rail. The solver's push-out times the rail friction then holds it to a crawl down the slope instead of
-- rolling back. Sit it just clear of any rail it overlaps and drop the velocity into the rail.
local function unsinkFromRails(b: BasePart, obstacles)
	local pos = b.Position
	for _, part in obstacles do
		local lp = part.CFrame:PointToObjectSpace(pos)
		local h = part.Size / 2
		local d = lp - Vector3.new(math.clamp(lp.X, -h.X, h.X), math.clamp(lp.Y, -h.Y, h.Y), math.clamp(lp.Z, -h.Z, h.Z))
		local dist = d.Magnitude
		if dist > 1e-4 and dist < R - 0.0005 then
			local n = part.CFrame:VectorToWorldSpace(d / dist)
			n = Vector3.new(n.X, 0, n.Z)
			if n.Magnitude > 0.5 then
				n = n.Unit
				b.CFrame += n * (R - dist + 0.002)
				local v = b.AssemblyLinearVelocity
				local vn = v:Dot(n)
				if vn < 0 then
					b.AssemblyLinearVelocity = v - n * vn
				end
				return true
			end
		end
	end
	return false
end

-- per-hole caches: moving blockers, collision obstacles, teleports
local cacheHole, cacheBlockers, cacheObstacles, cacheTeleports = nil, {}, {}, {}
local function refreshCache(hole)
	if hole == cacheHole then
		return
	end
	cacheHole = hole
	if not hole then
		cacheBlockers, cacheObstacles, cacheTeleports = {}, {}, {}
		return
	end
	cacheBlockers = holeParts(hole, function(d)
		return CollectionService:HasTag(d, "GolfMoverPart")
	end)
	cacheObstacles = holeParts(hole, function(d)
		return d.CanCollide and (d.Name == "Wall" or d.Name == "Bumper")
	end)
	local tp = hole:FindFirstChild("Teleports")
	cacheTeleports = {}
	if tp then
		for _, m in tp:GetChildren() do
			if m.Name == "Teleport" then
				table.insert(cacheTeleports, m)
			end
		end
	end
end

-- ~0.3 s exit effect for teleports: a chime, a burst of fireflies and a flash at the exit (local only, no collision).
local function teleportFx(pos: Vector3, color: Color3)
	local p = Instance.new("Part")
	p.Name = "TeleportFx"
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Shape = Enum.PartType.Ball
	p.Material = Enum.Material.Neon
	p.Color = color
	p.Transparency = 0.3
	p.Size = Vector3.one * 0.3
	p.CFrame = CFrame.new(pos)
	local light = Instance.new("PointLight")
	light.Color = color
	light.Range = 10
	light.Brightness = 6
	light.Parent = p
	local fx = Instance.new("ParticleEmitter")
	fx.Color = ColorSequence.new(color)
	fx.LightEmission = 1
	fx.Size = NumberSequence.new(0.1, 0)
	fx.Lifetime = NumberRange.new(0.3, 0.6)
	fx.Speed = NumberRange.new(2, 5)
	fx.SpreadAngle = Vector2.new(180, 180)
	fx.Drag = 3
	fx.Rate = 0
	fx.Parent = p
	local snd = Instance.new("Sound")
	snd.SoundId = "rbxasset://sounds/electronicpingshort.wav"
	snd.Volume = 0.6
	snd.PlaybackSpeed = 1.4
	snd.Parent = p
	p.Parent = workspace.CurrentCamera
	fx:Emit(30)
	snd:Play()
	TweenService:Create(p, TweenInfo.new(0.3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Size = Vector3.one * 1.6, Transparency = 1 }):Play()
	TweenService:Create(light, TweenInfo.new(0.3), { Brightness = 0 }):Play()
	Debris:AddItem(p, 1)
end

-- Teleport rings: a ball whose centre enters the entry radius (same level) reappears at the exit, moving along
-- the exit direction at clamp(speed * SpeedFactor, MinSpeed, MaxSpeed) (spec `teleports`).
local function checkTeleports(b: BasePart)
	if os.clock() < teleportCooldown then
		return false
	end
	local pos = b.Position
	for _, m in cacheTeleports do
		local off = pos - m.Position
		if Vector3.new(off.X, 0, off.Z).Magnitude < m:GetAttribute("Radius") and math.abs(off.Y - R) < 0.5 then
			local v = b.AssemblyLinearVelocity
			local speedIn = Vector3.new(v.X, 0, v.Z).Magnitude
			local speedOut = math.clamp(speedIn * m:GetAttribute("SpeedFactor"), m:GetAttribute("MinSpeed"), m:GetAttribute("MaxSpeed"))
			local dir = m:GetAttribute("ExitDir")
			b.CFrame = CFrame.new(m:GetAttribute("ExitPos") + Vector3.new(0, R + 0.01, 0))
			b.AssemblyLinearVelocity = dir * speedOut
			b.AssemblyAngularVelocity = Vector3.yAxis:Cross(dir * speedOut) / R
			teleportCooldown = os.clock() + 0.5
			rollVel, lastVel = nil, nil
			slowTime, stillTime, pinTime = 0, 0, 0
			stuckTime, stuckAnchor = 0, nil
			task.spawn(teleportFx, b.Position, m:GetAttribute("FxColor") or Color3.fromRGB(255, 226, 140))
			Ball.Teleported:Fire(m:GetAttribute("TeleportId"), speedIn, speedOut)
			return true
		end
	end
	return false
end

-- A free spot on the felt next to `pos`, clear of walls and moving parts (for the pin/unstick nudge).
local function freeSpotNear(pos: Vector3, away: Vector3)
	local perp = Vector3.new(-away.Z, 0, away.X)
	for _, d in { 0.6, 1.0, 1.5, 2.2, 3.0 } do
		for _, dir in { perp, -perp, away, -away } do
			local c = pos + dir * d
			local hit = workspace:Raycast(c + Vector3.new(0, 0.7, 0), Vector3.new(0, -2.2, 0), rayParams)
			if hit and CollectionService:HasTag(hit.Instance, "GolfSurface") and math.abs(hit.Position.Y - (pos.Y - R)) < 0.8 then
				local np = hit.Position + Vector3.new(0, R + 0.01, 0)
				local clear = true
				for _, list in { cacheObstacles, cacheBlockers } do
					for _, part in list do
						if boxDistance(part, np) < R + 0.15 then
							clear = false
							break
						end
					end
					if not clear then
						break
					end
				end
				if clear then
					return np
				end
			end
		end
	end
	return nil
end

-- Pinned against a rail by a moving part for > Config.PinNudgeTime (or riding on top of one for > 0.5 s): hop the
-- ball out sideways.
local function checkPinned(b: BasePart, dt: number, ground)
	if #cacheBlockers == 0 then
		pinTime = 0
		return false
	end
	local pos = b.Position
	local touching
	for _, blk in cacheBlockers do
		if boxDistance(blk, pos) < R + 0.05 then
			touching = blk
			break
		end
	end
	local riding = ground and CollectionService:HasTag(ground.Instance, "GolfMoverPart") and ground.Instance
	if Ball.state == "ready" and not touching and not riding then
		pinTime = 0
		return false
	end
	local v = b.AssemblyLinearVelocity
	local speed = Vector3.new(v.X, 0, v.Z).Magnitude
	if riding or (touching and speed < 0.5) then
		pinTime += dt
	else
		pinTime = 0
		return false
	end
	if pinTime < (riding and 0.5 or Config.PinNudgeTime) then
		return false
	end
	pinTime = 0
	local blk = riding or touching
	local mv = blk:GetVelocityAtPosition(pos)
	local away = flat(mv)
	if away.Magnitude < 0.05 then
		away = flat(pos - blk.Position)
	end
	away = away.Magnitude > 1e-3 and away.Unit or Vector3.new(1, 0, 0)
	local np = freeSpotNear(pos, away)
	if not np then
		return false
	end
	b.CFrame = CFrame.new(np)
	b.AssemblyLinearVelocity = Vector3.zero
	b.AssemblyAngularVelocity = Vector3.zero
	rollVel, lastVel = nil, nil
	Ball.Unstuck:Fire(riding and "riding" or "pinned", pos, np)
	return true
end

-- A moving part coming DOWN onto the ball (the H9 root gate closing): push the ball out from under it along the
-- part's thin axis before it lands, so it is moved aside instead of pinned.
local function pushFromDescending(b: BasePart)
	local pos = b.Position
	for _, blk in cacheBlockers do
		local vy = blk:GetVelocityAtPosition(pos).Y
		if vy < -0.05 then
			local lp = blk.CFrame:PointToObjectSpace(pos)
			local h = blk.Size / 2
			local below = -h.Y - lp.Y -- gap from the part's bottom face down to the ball centre
			if math.abs(lp.X) < h.X + R and math.abs(lp.Z) < h.Z + R and below > -R and below < R + 0.35 then
				local axis = h.X <= h.Z and blk.CFrame.RightVector or blk.CFrame.LookVector
				local side = h.X <= h.Z and lp.X or -lp.Z
				axis = flat(axis)
				if axis.Magnitude < 1e-3 then
					continue
				end
				local dir = axis.Unit * (side >= 0 and 1 or -1)
				local v = b.AssemblyLinearVelocity
				if flat(v):Dot(dir) < 2 then
					b.AssemblyLinearVelocity = Vector3.new(0, v.Y, 0) + dir * 2.5
					b.AssemblyAngularVelocity = Vector3.yAxis:Cross(dir * 2.5) / R
					rollVel, lastVel = nil, nil
				end
				return true
			end
		end
	end
	return false
end

-- A sliding part's END closing on a ball (the H8 root door, which slides through the alcove rails into pockets):
-- against a wall, push the ball sideways off the end face (along the part's thin axis) before it pinches; on open
-- felt, bump it ahead like a real end-on hit.
local function pushFromSliding(b: BasePart)
	local pos = b.Position
	for _, blk in cacheBlockers do
		local mv = flat(blk:GetVelocityAtPosition(pos))
		if mv.Magnitude < 0.05 then
			continue
		end
		local dir = mv.Unit
		local h = blk.Size / 2
		local lp = blk.CFrame:PointToObjectSpace(pos)
		local ld = blk.CFrame:VectorToObjectSpace(dir)
		-- moving along its long horizontal axis only (end-on); the thin axis is the other one
		local alongZ = h.Z >= h.X
		local a = alongZ and ld.Z or ld.X
		if math.abs(a) < 0.9 then
			continue
		end
		local alongP, alongH = alongZ and lp.Z or lp.X, alongZ and h.Z or h.X
		local crossP, crossH = alongZ and lp.X or lp.Z, alongZ and h.X or h.Z
		local ahead = alongP * (a > 0 and 1 or -1) - alongH -- gap from the end face to the ball centre
		if math.abs(crossP) < crossH + R and math.abs(lp.Y) < h.Y + R and ahead > -R and ahead < R + 0.35 then
			-- a wall close ahead (within 1.5 studs): sideways, so the ball is never driven into it and pinched
			local hit = workspace:Raycast(pos, dir * 1.5, rayParams)
			local v = b.AssemblyLinearVelocity
			if not (hit and table.find(cacheObstacles, hit.Instance)) then
				-- open felt ahead: the end face bumps a ball it catches up with (a resting client-owned ball does
				-- not always get the contact from the server-driven part, which then slides through it)
				if ahead < R + 0.06 and flat(v):Dot(dir) < mv.Magnitude then
					local nv = flat(v) - dir * flat(v):Dot(dir) + dir * mv.Magnitude * 1.6
					b.AssemblyLinearVelocity = Vector3.new(nv.X, v.Y, nv.Z)
					b.AssemblyAngularVelocity = Vector3.yAxis:Cross(nv) / R
					rollVel, lastVel = nil, nil
					return true
				end
			else
				local axis = flat(alongZ and blk.CFrame.RightVector or blk.CFrame.LookVector)
				if axis.Magnitude < 1e-3 then
					continue
				end
				local side = (alongZ and 1 or -1) * crossP
				local pdir = axis.Unit * (side >= 0 and 1 or -1)
				if flat(v):Dot(pdir) < 2.5 then
					local nv = pdir * 3 + dir * math.min(flat(v):Dot(dir), mv.Magnitude)
					b.AssemblyLinearVelocity = Vector3.new(nv.X, v.Y, nv.Z)
					b.AssemblyAngularVelocity = Vector3.yAxis:Cross(Vector3.new(nv.X, 0, nv.Z)) / R
					rollVel, lastVel = nil, nil
				end
				return true
			end
		end
	end
	return false
end

-- Valley: the bottom of a dip between two sloped felt pieces (H9's rolling tunnel dip). On either plane the slope
-- beats rolling resistance, so the ball would rock in the crease forever; returns the crease point (ball centre) if
-- the felt within `reach` downhill slopes back toward the ball.
local function valleyPoint(pos: Vector3, down: Vector3, reach: number): Vector3?
	local prev
	for t = 0.02, reach, 0.02 do
		local c = pos + down * t
		local hit = workspace:Raycast(c + Vector3.new(0, 0.3, 0), Vector3.new(0, -0.8, 0), rayParams)
		if not hit or not CollectionService:HasTag(hit.Instance, "GolfSurface") then
			return nil
		end
		if flat(hit.Normal):Dot(down) < -0.01 then
			local p0 = prev or hit.Position
			return (p0 + hit.Position) / 2 + Vector3.new(0, R + 0.005, 0)
		end
		prev = hit.Position
	end
	return nil
end

-- Auto-reset (holes with an AutoResetStill attribute, i.e. holes with moving parts or teleports): a moving ball
-- that makes no progress, or a resting ball still held by a moving part, for that many seconds goes back to the
-- stroke start for free.
local function checkAutoReset(b: BasePart, dt: number, hole, cup, cupR)
	local limit = hole and hole:GetAttribute("AutoResetStill")
	if not limit then
		stuckTime, stuckAnchor = 0, nil
		return false
	end
	local pos = b.Position
	if Ball.state == "ready" then
		stuckTime = pinTime > 0 and stuckTime + dt or 0
	elseif cupR and flat(pos - cup.Position).Magnitude < cupR + 0.3 then
		stuckTime, stuckAnchor = 0, nil
	elseif not stuckAnchor or (pos - stuckAnchor).Magnitude > 0.3 then
		stuckTime, stuckAnchor = 0, pos
	else
		stuckTime += dt
	end
	if stuckTime < limit then
		return false
	end
	stuckTime, stuckAnchor = 0, nil
	Ball.AutoReset:Fire(pos, Ball.state == "ready" and "held" or "still")
	Ball.setState("locked")
	Remotes.RequestReset:FireServer()
	return true
end

local function step(dt)
	local b = Ball.ball
	if not b or b.Anchored or not Ball.isOwner() then
		return
	end
	local v = b.AssemblyLinearVelocity
	local speed = v.Magnitude
	local ground, slopeAccel = groundInfo(b)

	if Ball.state == "ready" then
		-- a resting ball that a moving part keeps touching (rubbing past it, or about to squeeze it) for > 0.5 s
		-- is hopped clear, like a pinned rolling ball
		local hole = Ball.getHole()
		refreshCache(hole)
		if pushFromDescending(b) or pushFromSliding(b) then
			slowTime, rollTime, stillTime, pinTime = 0, 0, 0, 0
			stuckTime, stuckAnchor = 0, nil
			Ball.setState("moving")
			return
		end
		if checkPinned(b, dt, ground) or checkAutoReset(b, dt, hole) then
			return
		end
		-- static friction: hold the ball still on gentle slopes; let it go if something pushes it
		if ground and slopeAccel < Config.RollDecel and speed < 1.5 then
			-- cancel sideways creep only: zeroing the vertical velocity too fights the contact solver
			-- and the ball slowly sinks into the felt
			if Vector3.new(v.X, 0, v.Z).Magnitude > 0.005 then
				b.AssemblyLinearVelocity = Vector3.new(0, v.Y, 0)
				b.AssemblyAngularVelocity = Vector3.zero
			end
		elseif speed > 1.5 or not ground then
			slowTime = 0
			rollTime = 0
			stillTime = 0
			pinTime = 0
			stuckTime, stuckAnchor = 0, nil
			Ball.setState("moving")
		end
		return
	end
	if Ball.state ~= "moving" then
		return
	end

	rollTime += dt
	strokeTime += dt
	-- safety net on every hole: a stroke that is still going after StrokeTimeout s (a ball circling a bank, ridden
	-- around by a mover, ...) goes back to its last rest point (the stroke start) for free
	if strokeTime > Config.StrokeTimeout then
		strokeTime = 0
		stuckTime, stuckAnchor = 0, nil
		Ball.AutoReset:Fire(b.Position, "timeout")
		Ball.setState("locked")
		Remotes.RequestReset:FireServer()
		return
	end
	local hole = Ball.getHole()
	refreshCache(hole)
	if checkTeleports(b) then
		return
	end
	if not pushFromDescending(b) then
		pushFromSliding(b)
	end
	if checkPinned(b, dt, ground) then
		return
	end
	-- cup capture: a slow ball over the hole drops in (fast ones skim across or lip out on the far rim)
	local cup = hole and hole:FindFirstChild("Cup")
	local cupR = cup and cup:GetAttribute("Radius")
	if checkAutoReset(b, dt, hole, cup, cupR) then
		return
	end
	if cupR then
		local off = b.Position - cup.Position
		local flatOff = Vector3.new(off.X, 0, off.Z)
		if flatOff.Magnitude < cupR - R * 0.5 and off.Y < R + 0.05 and flat(v).Magnitude < Config.CupCaptureSpeed then
			b.AssemblyLinearVelocity = Vector3.new(-flatOff.X * 8, math.min(v.Y, -4), -flatOff.Z * 8)
			b.AssemblyAngularVelocity = Vector3.zero
			slowTime = 0
			lastVel = nil
			return
		end
	end
	if ground then
		-- felt sink: contact slop can leave a slow ball ~0.01 studs sunk into the felt. The engine then rolls it on
		-- a smaller radius than the spin set below assumes, and the felt's friction brakes it every frame (a ball
		-- crawling down a slope at constant speed). Sit it back on the felt plane. Slow balls only, and never at the
		-- cup, where riding down over the lip is real.
		local sink = R - (b.Position - ground.Position):Dot(ground.Normal)
		local nearCup = cupR and flat(b.Position - cup.Position).Magnitude < cupR + R + 0.1
		if sink > 0.003 and ground.Normal.Y > 0.9 and speed < 2 and not nearCup then
			b.CFrame += ground.Normal * sink
			local vn = v:Dot(ground.Normal)
			if vn < 0 then
				v -= ground.Normal * vn
				b.AssemblyLinearVelocity = v
				speed = v.Magnitude
			end
		end
		if speed < 1.5 and unsinkFromRails(b, cacheObstacles) then
			v = b.AssemblyLinearVelocity
			speed = v.Magnitude
		end
		local hv = flat(v)
		-- obstacle contact (the engine bounced the ball off a wall/post/blade since last step): the bounce
		-- itself comes from the wall's Elasticity; the ball's spin carries over, so it now skids
		if lastVel and (hv - lastVel).Magnitude > math.max(0.6, 0.2 * lastVel.Magnitude) then
			rollVel = (rollVel or lastVel) * Config.SpinKeep + hv * (1 - Config.SpinKeep)
		end
		local newVel = v
		local slip = rollVel and hv - rollVel
		if slip and slip.Magnitude > 0.05 then
			-- sliding friction on the ball; the same friction spins the ball up toward rolling (solid sphere:
			-- spin's rolling speed changes 2.5x as fast as the ball's), so the slip closes at 3.5 mu g
			local mug = Config.SlideFriction * workspace.Gravity
			local dir = slip.Unit
			if slip.Magnitude <= 3.5 * mug * dt then
				newVel = v - slip * (1 / 3.5)
				rollVel = nil
			else
				newVel = v - dir * mug * dt
				rollVel += dir * 2.5 * mug * dt
			end
		elseif speed > 0 then
			rollVel = nil
			local decel = math.max(0, Config.RollDecel - Config.EngineRollLoss) + Config.RollDrag * speed
			local newSpeed = math.max(0, speed - decel * dt)
			if newSpeed > Config.MaxBallSpeed then
				newSpeed = Config.MaxBallSpeed
			end
			newVel = v * (newSpeed / speed)
		end
		b.AssemblyLinearVelocity = newVel
		lastVel = flat(newVel)
		-- the engine always sees pure roll (the skid lives in rollVel above): otherwise the felt's own friction
		-- would brake the same slip a second time
		local n = ground.Normal
		local along = newVel - n * newVel:Dot(n)
		b.AssemblyAngularVelocity = n:Cross(along) / R
		if speed < Config.StopSpeed and slopeAccel < Config.RollDecel then
			slowTime += dt
			if slowTime >= Config.RestTime then
				rest(b)
				return
			end
		else
			slowTime = 0
		end
		-- wedged (e.g. in the corner of a steep bank and its backing rail): not moving, but the slope says it should
		if speed < Config.StopSpeed then
			stillTime += dt
			parkTime = speed < 0.05 and parkTime + dt or 0
			-- seam lip: a slow ball sunk ~0.01 studs into the felt (contact slop) parks against the edge of the
			-- next felt piece at the foot of a slope. Hop it over the lip, downhill, a few times before giving up.
			-- (parked = practically motionless: a ball turning round at the top of its climb is not hopped)
			local downhill = flat(ground.Normal)
			if slopeAccel >= Config.RollDecel and downhill.Magnitude > 1e-3 then
				local vp = valleyPoint(b.Position, downhill.Unit, 0.15)
				if vp then
					b.CFrame = CFrame.new(vp)
					rest(b)
					return
				end
			end
			if slopeAccel >= Config.RollDecel and parkTime >= 0.3 and seamHops < 3 and downhill.Magnitude > 1e-3 then
				seamHops += 1
				stillTime = 0
				parkTime = 0
				b.CFrame = b.CFrame + Vector3.new(0, 0.03, 0)
				b.AssemblyLinearVelocity = downhill.Unit * 0.8
				b.AssemblyAngularVelocity = Vector3.zero
				rollVel, lastVel = nil, nil
				Ball.Unstuck:Fire("seam", b.Position, b.Position)
				return
			end
			-- (holes with AutoResetStill reset a stuck ball to the stroke start instead, see checkAutoReset)
			if stillTime >= 2 and not (hole and hole:GetAttribute("AutoResetStill")) then
				stillTime = 0
				Ball.ForcedRest:Fire(b.Position, "wedged")
				rest(b)
				return
			end
		else
			stillTime = 0
			parkTime = 0
		end
	else
		slowTime = 0
		lastVel = nil
	end
	if rollTime > Config.MaxRollTime then
		Ball.ForcedRest:Fire(b.Position, "maxtime")
		rest(b)
	end
end

local function updateRing()
	local b = Ball.ball
	if not b or not readyRing then
		return
	end
	local show = Ball.state == "ready"
	readyRing.Transparency = show and 0.35 or 1
	if show then
		local t = os.clock()
		local s = R * (4.4 + math.sin(t * 4) * 0.35)
		readyRing.Size = Vector3.new(0.008, s, s)
		readyRing.CFrame = CFrame.new(b.Position - Vector3.new(0, R - 0.006, 0)) * CFrame.Angles(0, 0, math.rad(90))
	end
end

function Ball.init()
	local balls = workspace:WaitForChild("Balls")
	Ball.ball = balls:WaitForChild(tostring(player.UserId))
	local b = Ball.ball
	rayParams.FilterDescendantsInstances = { balls }

	-- hide our own name tag
	local tag = b:FindFirstChild("NameTag")
	if tag then
		tag.Enabled = false
	end

	readyRing = Instance.new("Part")
	readyRing.Name = "BallReadyRing"
	readyRing.Shape = Enum.PartType.Cylinder
	readyRing.Anchored = true
	readyRing.CanCollide = false
	readyRing.CanQuery = false
	readyRing.CanTouch = false
	readyRing.CastShadow = false
	readyRing.Material = Enum.Material.Neon
	readyRing.Color = Color3.fromRGB(255, 255, 255)
	readyRing.Transparency = 1
	readyRing.Parent = workspace.CurrentCamera

	b:GetPropertyChangedSignal("Anchored"):Connect(function()
		if b.Anchored then
			Ball.setState("locked")
		end
	end)

	Remotes.BallPlaced.OnClientEvent:Connect(function(pos, reason, holeIndex)
		Ball.holeIndex = holeIndex
		Ball.setState("locked")
		strokeTime = 0
		placeToken += 1
		local token = placeToken
		Ball.Placed:Fire(pos, reason)
		-- give network ownership a moment to settle before allowing a putt
		local t0 = os.clock()
		while os.clock() - t0 < 3 and (b.Anchored or not Ball.isOwner()) do
			task.wait()
		end
		task.wait(0.15)
		if token ~= placeToken or b.Anchored then
			return
		end
		if (b.Position - pos).Magnitude > 0.5 then
			b.CFrame = CFrame.new(pos)
		end
		b.AssemblyLinearVelocity = Vector3.zero
		b.AssemblyAngularVelocity = Vector3.zero
		settleOnGround(b)
		slowTime = 0
		stuckTime, stuckAnchor = 0, nil
		Ball.setState("ready")
	end)

	RunService.PreSimulation:Connect(step)
	RunService.RenderStepped:Connect(updateRing)
end

return Ball
