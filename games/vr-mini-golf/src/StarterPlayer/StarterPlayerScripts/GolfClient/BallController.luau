-- BallController: owns the local player's ball on the client.
-- Applies rolling resistance, decides when the ball is at rest, and exposes Ball.hit().
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
Ball.Stroked = Instance.new("BindableEvent") -- (velocity)

local slowTime = 0
local rollTime = 0
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

function Ball.hit(velocity: Vector3)
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
	Ball.setState("moving")
	Remotes.Stroke:FireServer(startPos)
	hitSound.PlaybackSpeed = 0.8 + math.clamp(velocity.Magnitude / 40, 0, 0.6)
	hitSound.Volume = 0.3 + math.clamp(velocity.Magnitude / 30, 0, 0.7)
	hitSound:Play()
	Ball.Stroked:Fire(velocity)
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

local function rest(b)
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
	if ground then
		if speed > 0 then
			local newSpeed = math.max(0, speed - Config.RollDecel * dt)
			if newSpeed > Config.MaxBallSpeed then
				newSpeed = Config.MaxBallSpeed
			end
			local newVel = v * (newSpeed / speed)
			b.AssemblyLinearVelocity = newVel
			-- keep the ball in pure roll: no leftover spin fighting the floor after banks/bumps
			local n = ground.Normal
			local along = newVel - n * newVel:Dot(n)
			b.AssemblyAngularVelocity = n:Cross(along) / R
		end
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
