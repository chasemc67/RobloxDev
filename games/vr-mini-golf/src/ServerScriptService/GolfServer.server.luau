-- GolfServer: authoritative rules for the mini golf course.
-- The ball itself is simulated by its owner's client (network ownership) so putts feel instant,
-- while the server tracks strokes, out-of-bounds, sinking and hole progression.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local HttpService = game:GetService("HttpService")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Config = require(Golf:WaitForChild("Config"))
local Remotes = Golf:WaitForChild("Remotes")

local course = workspace:WaitForChild("Course")
local holes = {}
for _, model in course:GetChildren() do
	local n = model:GetAttribute("HoleNumber")
	if n then
		holes[n] = model
	end
end

local ballsFolder = workspace:FindFirstChild("Balls")
if not ballsFolder then
	ballsFolder = Instance.new("Folder")
	ballsFolder.Name = "Balls"
	ballsFolder.Parent = workspace
end

local BALL_COLORS = {
	Color3.fromRGB(255, 255, 255),
	Color3.fromRGB(255, 200, 40),
	Color3.fromRGB(255, 90, 150),
	Color3.fromRGB(80, 200, 255),
	Color3.fromRGB(255, 130, 40),
	Color3.fromRGB(170, 110, 255),
}
local colorIndex = 0

local states = {} -- [Player] = state

-- st.testHole is only set by the Studio test harness (GolfServer.GolfTestServer).
local function holeOf(st)
	return st.testHole or holes[st.hole]
end

local function teePosition(hole)
	local tee = hole:FindFirstChild("Tee")
	local surfaceY = tee.Position.Y - tee.Size.Y / 2
	return Vector3.new(tee.Position.X, surfaceY + Config.BallRadius + 0.03, tee.Position.Z)
end

local function inBounds(hole, pos)
	local bounds = hole:FindFirstChild("Bounds")
	if not bounds then
		return true
	end
	local lp = bounds.CFrame:PointToObjectSpace(pos)
	local half = bounds.Size / 2
	return math.abs(lp.X) <= half.X and math.abs(lp.Y) <= half.Y and math.abs(lp.Z) <= half.Z
end

local function publish(player, st)
	player:SetAttribute("Hole", st.hole)
	player:SetAttribute("Strokes", st.strokes[st.hole] or 0)
	player:SetAttribute("Scores", HttpService:JSONEncode(st.strokes))
end

local function placeBall(player, st, pos, reason)
	local ball = st.ball
	st.resetting = false
	st.lastPos = pos
	ball.Anchored = true
	ball.AssemblyLinearVelocity = Vector3.zero
	ball.AssemblyAngularVelocity = Vector3.zero
	ball.CFrame = CFrame.new(pos)
	ball.Anchored = false
	if player.Parent then
		ball:SetNetworkOwner(player)
	end
	Remotes.BallPlaced:FireClient(player, pos, reason, st.testHole and 0 or st.hole)
end

local function startHole(player, st, index)
	st.hole = index
	st.strokes[index] = 0
	st.sunk = false
	st.finished = false
	publish(player, st)
	placeBall(player, st, teePosition(holes[index]), "hole")
end

local function finishHole(player, st, maxed)
	st.sunk = true
	local hole = holeOf(st)
	local strokes = st.strokes[st.hole]
	if maxed then
		strokes = Config.MaxStrokes
		st.strokes[st.hole] = strokes
	else
		-- settle the ball at the bottom of the cup
		local cup = hole:FindFirstChild("Cup")
		st.ball.Anchored = true
		st.ball.CFrame = CFrame.new(cup.Position - Vector3.new(0, Config.CupDepth - Config.BallRadius, 0))
	end
	publish(player, st)
	Remotes.HoleComplete:FireAllClients(player, st.hole, strokes, hole:GetAttribute("Par"), maxed == true)

	local token = {}
	st.transitionToken = token
	task.delay(Config.HoleTransitionTime, function()
		if states[player] ~= st or st.transitionToken ~= token then
			return
		end
		if st.hole < #holes then
			startHole(player, st, st.hole + 1)
		else
			st.finished = true
			Remotes.CourseComplete:FireClient(player, st.strokes)
		end
	end)
end

local function outOfBounds(player, st)
	st.resetting = true
	st.strokes[st.hole] += Config.PenaltyStrokes
	publish(player, st)
	Remotes.Notice:FireClient(player, "Out of bounds!  +" .. Config.PenaltyStrokes, "bad")
	task.delay(1, function()
		if states[player] == st and st.resetting and not st.sunk then
			placeBall(player, st, st.lastPos, "oob")
		end
	end)
end

local function setupCharacter(character)
	local function apply(part)
		if part:IsA("BasePart") then
			part.CollisionGroup = "GolfPlayer"
		end
	end
	for _, d in character:GetDescendants() do
		apply(d)
	end
	character.DescendantAdded:Connect(apply)
end

local function onPlayerAdded(player)
	colorIndex += 1
	local ball = Golf.BallTemplate:Clone()
	ball.Name = tostring(player.UserId)
	ball.Color = BALL_COLORS[(colorIndex - 1) % #BALL_COLORS + 1]
	ball:SetAttribute("OwnerId", player.UserId)
	ball.NameTag.Label.Text = player.DisplayName
	ball.Trail.Color = ColorSequence.new(ball.Color)
	ball.Anchored = true
	ball.CFrame = CFrame.new(teePosition(holes[1]))
	ball.Parent = ballsFolder

	states[player] = {
		ball = ball,
		hole = 1,
		strokes = {},
		lastPos = ball.Position,
		sunk = false,
		resetting = false,
		finished = false,
		started = false,
		lastStroke = 0,
		lastReset = 0,
	}
	player:SetAttribute("Hole", 1)
	player:SetAttribute("Strokes", 0)
	player:SetAttribute("Scores", "[]")

	player.CharacterAdded:Connect(setupCharacter)
	if player.Character then
		setupCharacter(player.Character)
	end
end

Players.PlayerAdded:Connect(onPlayerAdded)
for _, p in Players:GetPlayers() do
	onPlayerAdded(p)
end

Players.PlayerRemoving:Connect(function(player)
	local st = states[player]
	states[player] = nil
	if st and st.ball then
		st.ball:Destroy()
	end
end)

Remotes.Ready.OnServerEvent:Connect(function(player)
	local st = states[player]
	if not st then
		return
	end
	if not st.started then
		st.started = true
		-- Studio testing aid: set workspace attribute DebugStartHole to begin on a later hole
		local first = math.clamp(workspace:GetAttribute("DebugStartHole") or 1, 1, #holes)
		startHole(player, st, first)
	elseif not st.sunk then
		placeBall(player, st, st.lastPos, "hole")
	end
end)

Remotes.Stroke.OnServerEvent:Connect(function(player, startPos)
	local st = states[player]
	if not st or not st.started or st.sunk or st.resetting or st.finished then
		return
	end
	local now = os.clock()
	if now - st.lastStroke < 0.3 then
		return
	end
	st.lastStroke = now
	if typeof(startPos) ~= "Vector3" or (startPos - st.ball.Position).Magnitude > 4 or not inBounds(holeOf(st), startPos) then
		startPos = st.ball.Position
	end
	st.lastPos = startPos
	st.strokes[st.hole] = (st.strokes[st.hole] or 0) + 1
	publish(player, st)
end)

Remotes.BallRest.OnServerEvent:Connect(function(player)
	local st = states[player]
	if not st or st.sunk or st.resetting or st.finished then
		return
	end
	if (st.strokes[st.hole] or 0) >= Config.MaxStrokes then
		Remotes.Notice:FireClient(player, "Max strokes reached", "bad")
		finishHole(player, st, true)
	end
end)

Remotes.RequestReset.OnServerEvent:Connect(function(player)
	local st = states[player]
	if not st or st.sunk or st.resetting or st.finished then
		return
	end
	local now = os.clock()
	if now - st.lastReset < 1 then
		return
	end
	st.lastReset = now
	placeBall(player, st, st.lastPos, "reset")
end)

Remotes.PlayAgain.OnServerEvent:Connect(function(player)
	local st = states[player]
	if not st or not st.finished then
		return
	end
	st.strokes = {}
	startHole(player, st, 1)
end)

-- Studio-only playtest harness: off unless workspace.GolfTestMode is set before pressing Play.
if RunService:IsStudio() and workspace:GetAttribute("GolfTestMode") == true then
	require(script:WaitForChild("GolfTestServer")).init({
		states = states,
		holes = holes,
		publish = publish,
		placeBall = placeBall,
	})
end

-- Watch every ball for sinking / leaving the course.
RunService.Heartbeat:Connect(function()
	for player, st in states do
		if not st.started or st.sunk or st.resetting or st.finished or st.ball.Anchored then
			continue
		end
		local hole = holeOf(st)
		local pos = st.ball.Position
		local cup = hole:FindFirstChild("Cup")
		local flat = Vector3.new(pos.X - cup.Position.X, 0, pos.Z - cup.Position.Z).Magnitude
		-- sunk once the whole ball has dropped below the rim
		if flat < cup:GetAttribute("Radius") and pos.Y < cup.Position.Y - Config.BallRadius then
			finishHole(player, st, false)
		elseif pos.Y < hole:GetAttribute("KillY") or not inBounds(hole, pos) then
			outOfBounds(player, st)
		end
	end
end)
