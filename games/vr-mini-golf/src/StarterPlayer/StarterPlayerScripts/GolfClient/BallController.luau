-- BallController: owns the local player's ball on the client.
-- Applies rolling resistance, decides when the ball is at rest, and exposes Ball.hit(), the one function
-- every shot goes through (VR putter contact, phone/mouse pull-back, and the Studio test harness).
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

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

local slowTime = 0
local rollTime = 0
-- skid after an obstacle hit: the (flat) velocity the ball's spin would roll at, or nil while rolling cleanly
local rollVel: Vector3? = nil
local lastVel: Vector3? = nil -- flat velocity we left the ball with last step
local placeToken = 0
local readyRing: BasePart

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
	rollVel = nil
	lastVel = nil
	b.AssemblyLinearVelocity = Vector3.zero
	b.AssemblyAngularVelocity = Vector3.zero
	settleOnGround(b)
	Ball.setState("ready")
	Remotes.BallRest:FireServer(b.Position)
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
			Ball.setState("moving")
		end
		return
	end
	if Ball.state ~= "moving" then
		return
	end

	rollTime += dt
	-- cup capture: a slow ball over the hole drops in (fast ones skim across or lip out on the far rim)
	local hole = Ball.getHole()
	local cup = hole and hole:FindFirstChild("Cup")
	local cupR = cup and cup:GetAttribute("Radius")
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
			end
		else
			slowTime = 0
		end
	else
		slowTime = 0
		lastVel = nil
	end
	if rollTime > Config.MaxRollTime then
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
		Ball.setState("ready")
	end)

	RunService.PreSimulation:Connect(step)
	RunService.RenderStepped:Connect(updateRing)
end

return Ball
