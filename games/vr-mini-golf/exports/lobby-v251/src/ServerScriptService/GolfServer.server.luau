-- GolfServer: authoritative rules for the mini golf course.
-- The ball itself is simulated by its owner's client (network ownership) so putts feel instant,
-- while the server tracks strokes, out-of-bounds, sinking and hole progression.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local HttpService = game:GetService("HttpService")

local Golf = ReplicatedStorage:WaitForChild("Golf")
-- (stage z) one place per course: the lobby place has no golf (ServerScriptService.LobbyServer runs it), and a course
-- place only hosts its own course (ReplicatedStorage.Golf.Places)
local Places = require(Golf:WaitForChild("Places"))
if Places.isLobby() then
	return
end
local PLACE_COURSE = Places.course() or "lantern_grove"
local Config = require(Golf:WaitForChild("Config"))
local Remotes = Golf:WaitForChild("Remotes")
local PersonalBest = require(script:WaitForChild("PersonalBest"))
local PlaceTeleport = require(script.Parent:WaitForChild("PlaceTeleport"))
local Leaderboard = require(script.Parent:WaitForChild("Leaderboard"))
-- course modes: Peaceful balls pass through each other, PVP balls collide (register before anything walks the groups)
local BallGroups = require(Golf:WaitForChild("BallGroups"))
BallGroups.setup()
require(script:WaitForChild("ClubSetup")).init(Remotes)

-- Remotes added with the front end (created here; clients WaitForChild them)
local function remote(name)
	local r = Remotes:FindFirstChild(name)
	if not r then
		r = Instance.new("RemoteEvent")
		r.Name = name
		r.Parent = Remotes
	end
	return r
end
local SaveSettings = remote("SaveSettings") -- client -> server: settings table (PersonalBest.setSettings)

-- Studio harness rounds never count toward a personal best
local TEST_MODE = RunService:IsStudio() and workspace:GetAttribute("GolfTestMode") == true

-- Each course is its own workspace folder (ReplicatedStorage.Golf.Courses: Lantern Grove workspace.Course, Sugarloaf
-- Canyon workspace.CourseSugarloaf). Stage z: each place builds only its own course (PLACE_COURSE), and every player
-- in it plays that course (st.course, player attribute "Course").
local Courses = require(Golf:WaitForChild("Courses"))
local course = workspace:WaitForChild(Courses.folderName(PLACE_COURSE))
local courseHoles = {}
for id in Courses.FOLDERS do
	local list = Courses.holes(id)
	if next(list) then
		courseHoles[id] = list
	end
end
local holes = courseHoles[PLACE_COURSE]
local function holesOf(st)
	return courseHoles[st and st.course or PLACE_COURSE] or holes
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

-- Every player plays the course at their own pace: no groups, shot timer, idle skip, spectating or replay vote.
-- Sinking moves that player (only) to the next hole; a late joiner starts on hole 1 straight away.
-- The Studio harness can add simulated players (GolfTestServer.addSimPlayer): Folders standing in for a Player,
-- with a server-owned ball. Nothing is sent to them over the network.
local function isReal(player)
	return typeof(player) == "Instance" and player:IsA("Player")
end

local function sendTo(remote, player, ...)
	if isReal(player) then
		remote:FireClient(player, ...)
	end
end

local function applyCourseMode(player, st)
	st.ball.CollisionGroup = BallGroups.groupFor(player:GetAttribute("CourseMode"))
end

-- st.testHole is only set by the Studio test harness (GolfServer.GolfTestServer).
local function holeOf(st)
	return st.testHole or holesOf(st)[st.hole]
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
	player:SetAttribute("HoleHoled", st.sunk == true)
	player:SetAttribute("Strokes", st.strokes[st.hole] or 0)
	player:SetAttribute("Scores", HttpService:JSONEncode(st.strokes))
end

local function placeBall(player, st, pos, reason)
	local ball = st.ball
	st.resetting = false
	st.lastPos = pos
	if st.exploring then
		-- Explore mode: park the ball where play will resume ("Back to golf" places it for real)
		st.resumePos = pos
		ball.Anchored = true
		ball.CFrame = CFrame.new(pos)
		sendTo(Remotes.BallPlaced, player, pos, reason, st.testHole and 0 or st.hole)
		return
	end
	-- the owning client may still send a stale position or two from before the move (e.g. a rewind while the
	-- ball was rolling): don't judge out-of-bounds until those have flushed
	st.placedAt = os.clock()
	ball.Anchored = true
	ball.AssemblyLinearVelocity = Vector3.zero
	ball.AssemblyAngularVelocity = Vector3.zero
	ball.CFrame = CFrame.new(pos)
	ball.Anchored = false
	if isReal(player) and player.Parent then
		ball:SetNetworkOwner(player)
	else
		ball:SetNetworkOwner(nil)
	end
	sendTo(Remotes.BallPlaced, player, pos, reason, st.testHole and 0 or st.hole)
end

local function startHole(player, st, index)
	st.hole = index
	st.strokes[index] = 0
	st.sunk = false
	st.finished = false
	publish(player, st)
	placeBall(player, st, teePosition(holesOf(st)[index]), "hole")
end

-- Course complete: totals, and the personal best (only full 9-hole rounds started on hole 1 outside the test
-- harness count). Sent to the client as the 2nd CourseComplete argument.
local function roundResult(player, st)
	local courseId = st.course or Courses.DEFAULT
	local total, parTotal, complete = 0, 0, true
	for i, h in holesOf(st) do
		parTotal += h:GetAttribute("Par") or 0
		local s = st.strokes[i]
		if type(s) == "number" and s > 0 then
			total += s
		else
			complete = false
		end
	end
	local counted = st.roundValid == true and complete and not TEST_MODE
	local result = { course = courseId, total = total, par = parTotal, counted = counted, newBest = false }
	if counted then
		result.best, result.newBest, result.previousBest = PersonalBest.recordRound(player, courseId, total)
		-- (stage z) the lobby's leaderboard wall reads these
		Leaderboard.submit(player.UserId, courseId, result.best or total)
	else
		result.best = PersonalBest.get(player, courseId)
		result.previousBest = result.best
	end
	-- (stage z) back to the lobby after the results, unless they play again (not in the Studio harness)
	if not TEST_MODE then
		result.returnIn = Config.ReturnToLobbyAfter
	end
	return result
end

-- Course finished: teleport back to the lobby after Config.ReturnToLobbyAfter seconds unless a new round started
-- (Play again) or they already left. Not in the Studio harness (TEST_MODE); in a Studio playtest PlaceTeleport only
-- records the request.
local function scheduleReturn(player, st)
	if TEST_MODE or not isReal(player) then
		return
	end
	local token = {}
	st.returnToken = token
	task.delay(Config.ReturnToLobbyAfter, function()
		if states[player] == st and st.finished and st.returnToken == token then
			PlaceTeleport.send(player, "lobby", "finished")
		end
	end)
end

local function finishHole(player, st, maxed)
	st.sunk = true
	if st.testHole then
		st.roundValid = false
	end
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
	if isReal(player) then
		Remotes.HoleComplete:FireAllClients(player, st.hole, strokes, hole:GetAttribute("Par"), maxed == true)
	end

	local token = {}
	st.transitionToken = token
	task.delay(Config.HoleTransitionTime, function()
		if states[player] ~= st or st.transitionToken ~= token then
			return
		end
		if st.hole < #holesOf(st) then
			startHole(player, st, st.hole + 1)
		else
			st.finished = true
			sendTo(Remotes.CourseComplete, player, st.strokes, isReal(player) and roundResult(player, st) or nil)
			scheduleReturn(player, st)
		end
	end)
end

-- The hazard (water / pit) footprint the ball dropped into, if any (CourseBuilder: Hazards/Hazard parts).
local function hazardAt(hole, pos)
	local folder = hole:FindFirstChild("Hazards")
	if not folder then
		return nil
	end
	for _, h in folder:GetChildren() do
		if h.Name == "Hazard" then
			local lp = h.CFrame:PointToObjectSpace(pos)
			if math.abs(lp.X) <= h.Size.X / 2 + 0.3 and math.abs(lp.Z) <= h.Size.Z / 2 + 0.3 then
				return h
			end
		end
	end
	return nil
end

local function outOfBounds(player, st)
	st.resetting = true
	st.strokes[st.hole] = (st.strokes[st.hole] or 0) + Config.PenaltyStrokes
	publish(player, st)
	-- the ball's last airborne position tells a hazard (water, rabbit hole) from a ball that escaped the course
	local hz = hazardAt(holeOf(st), st.ball.Position)
	local kind = hz and hz:GetAttribute("HazardType") or "escape"
	-- (a running count makes every value new, so it replicates even when the same hazard is hit twice in a row)
	st.oobCount = (st.oobCount or 0) + 1
	st.ball:SetAttribute("LastOOB", (hz and ("hazard:" .. hz:GetAttribute("HazardId")) or "escape") .. "#" .. st.oobCount)
	local text = kind == "water" and "Splash!  Water hazard  +" or (kind == "pit" and "Down the rabbit hole!  +" or "Out of bounds!  +")
	sendTo(Remotes.Notice, player, text .. Config.PenaltyStrokes, "bad", kind)
	-- spec hazard reset = 'respawn': back at a set felt point (H5: the root-bridge entry), else the stroke start
	local respawn = hz and hz:GetAttribute("RespawnWorld")
	task.delay(1, function()
		if states[player] == st and st.resetting and not st.sunk then
			placeBall(player, st, respawn or st.lastPos, "oob")
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

-- (stage z) the lobby is its own place now (no ball there): arriving in a course place starts its hole 1 on Ready.
local function onPlayerAdded(player)
	local real = isReal(player)
	local userId = real and player.UserId or player:GetAttribute("UserId")
	colorIndex += 1
	local ball = Golf.BallTemplate:Clone()
	ball.Name = tostring(userId)
	ball.Color = BALL_COLORS[(colorIndex - 1) % #BALL_COLORS + 1]
	ball:SetAttribute("OwnerId", userId)
	ball.NameTag.Label.Text = real and player.DisplayName or player.Name
	ball.Trail.Color = ColorSequence.new(ball.Color)
	ball.Anchored = true
	ball.CFrame = CFrame.new(teePosition(holes[1]))
	ball.Parent = ballsFolder

	states[player] = {
		ball = ball,
		course = PLACE_COURSE,
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
	player:SetAttribute("Course", states[player].course)
	player:SetAttribute("Hole", 1)
	player:SetAttribute("Strokes", 0)
	player:SetAttribute("Scores", "[]")
	applyCourseMode(player, states[player])
	player:GetAttributeChangedSignal("CourseMode"):Connect(function()
		local st = states[player]
		if st then
			applyCourseMode(player, st)
		end
	end)

	if real then
		player.CharacterAdded:Connect(setupCharacter)
		if player.Character then
			setupCharacter(player.Character)
		end
		PersonalBest.load(player)
	end
	return states[player]
end

local function removePlayer(player)
	local st = states[player]
	states[player] = nil
	if st and st.ball then
		st.ball:Destroy()
	end
end

Players.PlayerAdded:Connect(onPlayerAdded)
for _, p in Players:GetPlayers() do
	onPlayerAdded(p)
end

Players.PlayerRemoving:Connect(function(player)
	removePlayer(player)
	PersonalBest.unload(player)
end)

game:BindToClose(function()
	PersonalBest.flushAll()
end)

SaveSettings.OnServerEvent:Connect(function(player, settings)
	if type(settings) == "table" then
		PersonalBest.setSettings(player, settings)
	end
end)

local function onReady(player)
	local st = states[player]
	if not st then
		return
	end
	if not st.started then
		st.started = true
		-- Studio testing aid: set workspace attribute DebugStartHole to begin on a later hole
		local first = math.clamp(workspace:GetAttribute("DebugStartHole") or 1, 1, #holesOf(st))
		st.roundValid = first == 1
		startHole(player, st, first)
	elseif not st.sunk then
		placeBall(player, st, st.lastPos, "hole")
	end
end
Remotes.Ready.OnServerEvent:Connect(onReady)

local function onStroke(player, startPos)
	local st = states[player]
	if not st or not st.started or st.sunk or st.resetting or st.finished or st.exploring then
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
end
Remotes.Stroke.OnServerEvent:Connect(onStroke)

Remotes.BallRest.OnServerEvent:Connect(function(player)
	local st = states[player]
	if not st or st.sunk or st.resetting or st.finished or st.exploring then
		return
	end
	if (st.strokes[st.hole] or 0) >= Config.MaxStrokes then
		sendTo(Remotes.Notice, player, "Max strokes reached", "bad")
		finishHole(player, st, true)
	end
end)

Remotes.RequestReset.OnServerEvent:Connect(function(player)
	local st = states[player]
	if not st or not st.started or st.sunk or st.resetting or st.finished or st.exploring then
		return
	end
	local now = os.clock()
	if now - st.lastReset < 1 then
		return
	end
	st.lastReset = now
	placeBall(player, st, st.lastPos, "reset")
end)

-- Play again after the round, or (restart == true, from the front-end course picker) restart mid-round.
Remotes.PlayAgain.OnServerEvent:Connect(function(player, restart)
	local st = states[player]
	if not st or not st.started or not (st.finished or restart == true) then
		return
	end
	local now = os.clock()
	if now - (st.lastPlayAgain or 0) < 1 then
		return
	end
	st.lastPlayAgain = now
	st.transitionToken = nil -- cancel a pending "next hole"
	st.returnToken = nil -- and the trip back to the lobby
	st.strokes = {}
	st.roundValid = true
	startHole(player, st, 1)
end)

-- Course picker (stage w): this place's course restarts at hole 1 (a fresh round). Stage z: another course is
-- another place, so picking it teleports there (PlaceTeleport).
local SelectCourse = remote("SelectCourse")
SelectCourse.OnServerEvent:Connect(function(player, courseId)
	local st = states[player]
	if not st or typeof(courseId) ~= "string" then
		return
	end
	if courseId ~= PLACE_COURSE and not courseHoles[courseId] then
		if isReal(player) and Courses.playable(courseId) then
			PlaceTeleport.send(player, courseId, "menu")
		end
		return
	end
	if not courseHoles[courseId] or not Courses.playable(courseId) then
		return
	end
	local now = os.clock()
	if now - (st.lastSelect or 0) < 1 then
		return
	end
	st.lastSelect = now
	st.transitionToken = nil
	st.returnToken = nil
	st.course = courseId
	player:SetAttribute("Course", courseId)
	st.strokes = {}
	st.roundValid = true
	if st.started then
		startHole(player, st, 1)
	elseif st.ready then
		st.started = true
		st.ball.Transparency = 0
		startHole(player, st, 1)
	end
end)

-- Explore mode (per player): walk/fly around the world with no ball and no scoring. The ball is parked (anchored)
-- at its resting spot, or the stroke start if it was still rolling; "Back to golf" puts it back there. A hole
-- transition or out-of-bounds reset that lands meanwhile just moves the parked spot (placeBall).
local SetExplore = Remotes:FindFirstChild("SetExplore") or Instance.new("RemoteEvent")
SetExplore.Name = "SetExplore"
SetExplore.Parent = Remotes
SetExplore.OnServerEvent:Connect(function(player, on)
	local st = states[player]
	if not st or not st.started or typeof(on) ~= "boolean" or st.exploring == on then
		return
	end
	if on then
		local ball = st.ball
		local pos = st.lastPos
		if not st.sunk and not st.resetting and not ball.Anchored and ball.AssemblyLinearVelocity.Magnitude < Config.StopSpeed * 2 and inBounds(holeOf(st), ball.Position) then
			pos = ball.Position
		end
		st.exploring = true
		st.resumePos = pos
		ball.Anchored = true
		ball.AssemblyLinearVelocity = Vector3.zero
		player:SetAttribute("Exploring", true)
	else
		st.exploring = false
		player:SetAttribute("Exploring", false)
		if not st.sunk and not st.finished then
			placeBall(player, st, st.resumePos or st.lastPos, "resume")
		end
	end
end)

-- Explore data for the clients (ServerStorage isn't replicated): scenic viewpoints, walkway points for the fall
-- respawn, and the world bounds. Invisible walls just inside the terrain edge stop players (only) leaving the world.
do
	local ok, layout = pcall(function()
		return require(game:GetService("ServerStorage"):WaitForChild("CourseData"):WaitForChild("WorldLayout"))
	end)
	-- (WorldLayout is Lantern Grove's world; Sugarloaf has no Explore viewpoints/walls yet)
	if ok and layout and layout.enabled and PLACE_COURSE == "lantern_grove" and workspace:FindFirstChild("World") then
		local data = { views = {}, paths = {}, bounds = layout.bounds }
		local poi = {}
		for _, p in layout.pois or {} do
			poi[p.id] = p.pos
		end
		local function view(name, pos, look)
			if pos then
				table.insert(data.views, { name = name, pos = { pos[1], pos[3] }, look = look })
			end
		end
		-- stand spots picked from Edit-mode captures (2026-10-10): each has a clear look at its subject
		view("Welcome Plaza", layout.spawn and layout.spawn.pos, layout.spawn and layout.spawn.look_at)
		view("Grand Falls", { 96, 0, -150 }, { 113, 56, -203 })
		view("Hollow Tree", { -36, 0, 60 }, { -70, 70, 6 })
		view("Lantern Mere", poi.mere_view, { 14, 10, 146 })
		view("Lookout Rock", poi.lookout_rock, { 113, 56, -203 })
		for _, path in layout.paths or {} do
			for _, seg in path.segments do
				local a = Vector3.new(seg.start[1], seg.start[2], seg.start[3])
				local b = Vector3.new(seg["end"][1], seg["end"][2], seg["end"][3])
				local n = math.max(1, math.ceil((b - a).Magnitude / 4))
				for i = 0, n do
					local q = a:Lerp(b, i / n)
					table.insert(data.paths, { math.floor(q.X * 10) / 10, math.floor(q.Y * 10) / 10, math.floor(q.Z * 10) / 10 })
				end
			end
		end
		local value = Golf:FindFirstChild("ExploreData") or Instance.new("StringValue")
		value.Name = "ExploreData"
		value.Value = HttpService:JSONEncode(data)
		value.Parent = Golf

		local PhysicsService = game:GetService("PhysicsService")
		if not PhysicsService:IsCollisionGroupRegistered("ExploreBounds") then
			PhysicsService:RegisterCollisionGroup("ExploreBounds")
		end
		for _, g in PhysicsService:GetRegisteredCollisionGroups() do
			PhysicsService:CollisionGroupSetCollidable("ExploreBounds", g.name, g.name == "GolfPlayer")
		end
		local folder = Instance.new("Folder")
		folder.Name = "ExploreBounds"
		local b = layout.bounds
		local x0, x1, z0, z1 = b.x[1] + 12, b.x[2] - 12, b.z[1] + 12, b.z[2] - 12
		local cx, cz, h = (x0 + x1) / 2, (z0 + z1) / 2, 600
		for _, w in {
			{ Vector3.new(x0 - 2, 200, cz), Vector3.new(4, h, z1 - z0 + 8) },
			{ Vector3.new(x1 + 2, 200, cz), Vector3.new(4, h, z1 - z0 + 8) },
			{ Vector3.new(cx, 200, z0 - 2), Vector3.new(x1 - x0 + 8, h, 4) },
			{ Vector3.new(cx, 200, z1 + 2), Vector3.new(x1 - x0 + 8, h, 4) },
		} do
			local part = Instance.new("Part")
			part.Name = "Wall"
			part.Anchored = true
			part.Transparency = 1
			part.CanQuery = false
			part.CanTouch = false
			part.CastShadow = false
			part.CollisionGroup = "ExploreBounds"
			part.Position, part.Size = w[1], w[2]
			part.Parent = folder
		end
		folder.Parent = workspace
	end
end

-- Camera occlusion (round 2): visible decor blocks the follow cameras' casts and nothing else
-- (ReplicatedStorage.Golf.CameraOcclusion).
do
	local CameraOcclusion = require(Golf:WaitForChild("CameraOcclusion"))
	CameraOcclusion.setupGroups()
	local roots = { course }
	for _, r in { workspace:FindFirstChild("World"), Courses.folder("sugarloaf_canyon") } do
		if r ~= course then
			table.insert(roots, r)
		end
	end
	CameraOcclusion.tagDecor(roots)
end

-- Moving parts (spinner, mill wheel, log, door, gate, lantern bar): server physics, phase-locked to server time.
local Movers = require(script:WaitForChild("Movers"))
Movers.start()

-- Studio-only playtest harness: off unless workspace.GolfTestMode is set before pressing Play.
if RunService:IsStudio() and workspace:GetAttribute("GolfTestMode") == true then
	require(script:WaitForChild("GolfTestServer")).init({
		states = states,
		holes = holes,
		holesOf = holesOf,
		courseHoles = courseHoles,
		publish = publish,
		placeBall = placeBall,
		movers = Movers,
		addPlayer = onPlayerAdded,
		removePlayer = removePlayer,
		onReady = onReady,
		onStroke = onStroke,
	})
end

-- (stage z) Studio-only hook for tools/place_smoke.py (normal playtests, not the harness): finish this player's round
-- now with the strokes so far and run the real results -> back-to-lobby path with a short delay.
if RunService:IsStudio() and not TEST_MODE then
	local hook = Instance.new("BindableFunction")
	hook.Name = "GolfFinishDebug"
	hook.OnInvoke = function(player, returnAfter)
		local st = states[player]
		if not st then
			return "no state"
		end
		st.transitionToken = nil
		st.finished = true
		local result = roundResult(player, st)
		result.returnIn = returnAfter
		sendTo(Remotes.CourseComplete, player, st.strokes, result)
		local token = {}
		st.returnToken = token
		task.delay(returnAfter, function()
			if states[player] == st and st.finished and st.returnToken == token then
				PlaceTeleport.send(player, "lobby", "finished")
			end
		end)
		return "ok"
	end
	hook.Parent = script
end

-- Watch every ball for sinking / leaving the course.
RunService.Heartbeat:Connect(function()
	for player, st in states do
		if not st.started or st.sunk or st.resetting or st.finished or st.exploring or st.ball.Anchored then
			continue
		end
		local hole = holeOf(st)
		local pos = st.ball.Position
		local cup = hole:FindFirstChild("Cup")
		local flat = Vector3.new(pos.X - cup.Position.X, 0, pos.Z - cup.Position.Z).Magnitude
		-- sunk once the whole ball has dropped below the rim
		if flat < cup:GetAttribute("Radius") and pos.Y < cup.Position.Y - Config.BallRadius then
			finishHole(player, st, false)
		elseif os.clock() - (st.placedAt or 0) > 0.75 then
			if pos.Y < hole:GetAttribute("KillY") or not inBounds(hole, pos) then
				outOfBounds(player, st)
			else
				-- water hazards are Terrain water in the world layout: the ball floats, so judge it at the surface
				local hz = hazardAt(hole, pos)
				if hz and hz:GetAttribute("HazardType") == "water" and pos.Y < (hz:GetAttribute("SurfaceY") or -math.huge) + Config.BallRadius then
					outOfBounds(player, st)
				end
			end
		end
	end
end)
