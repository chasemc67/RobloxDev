-- GolfTestServer: server half of the Studio playtest harness. Only required by GolfServer when
-- RunService:IsStudio() and workspace.GolfTestMode == true. The client half (GolfClient.GolfTest) runs the
-- scenarios, because the ball is simulated by its owner's client; this module only places the ball
-- deterministically and keeps the round logic (strokes, transitions) out of the way.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Config = require(Golf:WaitForChild("Config"))

local GolfTestServer = {}

-- A long, flat, wall-less felt strip off to the side of the course for rollout tests. The felt is a clone
-- of hole 1's felt so it has the same material, physical properties and tags.
local LANE_X, LANE_Z0, LANE_Z1, LANE_W, SURFACE_Y = -40, -10, 80, 10, 1

local function buildLane()
	local old = workspace:FindFirstChild("GolfTestLane")
	if old then
		old:Destroy()
	end
	local lane = Instance.new("Model")
	lane.Name = "GolfTestLane"
	lane:SetAttribute("HoleNumber", 0)
	lane:SetAttribute("HoleName", "Test Lane")
	lane:SetAttribute("Par", 0)
	lane:SetAttribute("KillY", SURFACE_Y - 0.5)
	local geo = Instance.new("Folder")
	geo.Name = "Geometry"
	geo.Parent = lane

	-- (stage ab) since the place split a course place may hold only Sugarloaf: take hole 1's felt of whichever is here
	local course = workspace:FindFirstChild("Course") or workspace:FindFirstChild("CourseSugarloaf") or workspace:FindFirstChild("CourseAurora")
	local source = course.Hole1.Geometry:FindFirstChild("Felt")
	local felt = source:Clone()
	felt.Size = Vector3.new(LANE_W, 1, LANE_Z1 - LANE_Z0)
	felt.CFrame = CFrame.new(LANE_X, SURFACE_Y - 0.5, (LANE_Z0 + LANE_Z1) / 2)
	felt.Parent = geo

	local function marker(name, cf, size)
		local p = Instance.new("Part")
		p.Name = name
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.Transparency = 1
		p.Size = size or Vector3.new(0.2, 0.2, 0.2)
		p.CFrame = cf
		p.Parent = lane
		return p
	end
	-- the cup is far past the end of the lane, so nothing ever sinks here
	marker("Cup", CFrame.new(LANE_X, SURFACE_Y, LANE_Z1 + 500)):SetAttribute("Radius", 0.21)
	marker("AimTarget", CFrame.new(LANE_X, SURFACE_Y, LANE_Z1))
	marker("Tee", CFrame.new(LANE_X, SURFACE_Y + 0.011, LANE_Z0 + 2))
	marker("Bounds", CFrame.new(LANE_X, SURFACE_Y + 10, (LANE_Z0 + LANE_Z1) / 2), Vector3.new(LANE_W + 4, 30, LANE_Z1 - LANE_Z0 + 6))
	lane.Parent = workspace
	return lane
end

function GolfTestServer.init(ctx)
	local lane = buildLane()

	local remote = Instance.new("RemoteFunction")
	remote.Name = "GolfTestRemote"
	remote.Parent = Golf

	remote.OnServerInvoke = function(player, cmd, args)
		local st = ctx.states[player]
		if not st then
			return false, "no state"
		end
		if cmd == "place" then
			-- args: { hole = 0 (test lane) | 1..9, pos = Vector3 }
			if args.hole == 0 then
				st.testHole = lane
			else
				st.testHole = nil
				-- (stage w) args.course: play a hole of another course (Sugarloaf Canyon sweeps)
				if args.course and ctx.courseHoles[args.course] then
					st.course = args.course
					player:SetAttribute("Course", args.course)
				end
				st.hole = math.clamp(args.hole, 1, #ctx.holesOf(st))
			end
			st.started = true
			st.sunk = false
			st.finished = false
			st.resetting = false
			st.transitionToken = {} -- cancels any pending "next hole" after a test sink
			st.strokes[st.hole] = 0
			ctx.publish(player, st)
			ctx.placeBall(player, st, args.pos, "test")
			return true
		elseif cmd == "ballRadius" then
			return Config.BallRadius
		elseif cmd == "spec" then
			-- the hole's spec (tee, cup, cup_from, waypoints, HIO line, movers, teleports) for the client scenarios
			local data = require(game:GetService("ServerStorage").CourseData[args.course == "aurora_archipelago" and "AuroraArchipelago" or args.course == "sugarloaf_canyon" and "SugarloafCanyon" or "LanternGrove"])
			local h = data.holes[args.hole]
			if not h then
				return false, "no hole " .. tostring(args.hole)
			end
			return game:GetService("HttpService"):JSONEncode({
				number = h.number,
				name = h.name,
				par = h.par,
				tee = h.tee,
				cup = h.cup,
				cup_from = h.cup_from,
				ai_waypoints = h.ai_waypoints,
				hio = h.hio,
				moving_parts = h.moving_parts,
				teleports = h.teleports,
				hazards = h.hazards,
				felt = h.felt,
				walls = h.walls,
				max_putt = data.physics.max_putt_speed_studs_s,
			})
		elseif cmd == "movers" then
			-- every mover's constraint value vs the spec at server time, and each blocker's world position vs the
			-- spec formula (pivot + Rot(axis, angle) * centre / pivot + centre + axis * offset), studs
			local t = workspace:GetServerTimeNow()
			local out = {}
			for model, s in ctx.movers.active do
				local cur, err, rate = ctx.movers.state(model, t)
				local want = ctx.movers.value(model, t)
				local pivot = model:GetAttribute("PivotWorld")
				local axis = model:GetAttribute("AxisWorld")
				local base = model:FindFirstChild("MoverBase")
				local maxPosErr = 0
				for _, blk in model:GetChildren() do
					if blk.Name == "Blocker" then
						local rest = blk:GetAttribute("RestCFrame")
						if rest then
							local expect
							if s.rotate then
								expect = (CFrame.new(pivot) * CFrame.fromAxisAngle(axis, math.rad(want)) * CFrame.new(-pivot) * rest).Position
							else
								expect = rest.Position + axis * want
							end
							maxPosErr = math.max(maxPosErr, (blk.Position - expect).Magnitude)
						end
					end
				end
				table.insert(out, {
					id = model:GetAttribute("MoverId"),
					hole = model.Parent and model.Parent.Parent and model.Parent.Parent.Name,
					type = model:GetAttribute("Type"),
					value = cur,
					want = want,
					err = err,
					rate = rate,
					blockerPosErr = maxPosErr,
					networkOwnerServer = s.root:GetNetworkOwner() == nil,
					anchored = s.root.Anchored,
					baseOk = base ~= nil,
				})
			end
			return game:GetService("HttpService"):JSONEncode({ t = t, movers = out })
		end
		return false, "unknown command " .. tostring(cmd)
	end

	-- Server-only entry for multi-player checks (no client needed): ServerStorage.GolfTestBindable:Invoke(cmd, args)
	local bindable = game:GetService("ServerStorage"):FindFirstChild("GolfTestBindable") or Instance.new("BindableFunction")
	bindable.Name = "GolfTestBindable"
	bindable.OnInvoke = function(cmd, args)
		if cmd == "modes" then
			------------------------------------------------------------------------------------------------ course modes
-- Simulated players: a Folder per player (attributes UserId, CourseMode) with a server-owned ball.
local simCount = 0
local function addSim(ctx, name, mode)
	local folder = game:GetService("ServerStorage"):FindFirstChild("SimPlayers") or Instance.new("Folder")
	folder.Name = "SimPlayers"
	folder.Parent = game:GetService("ServerStorage")
	simCount += 1
	local p = Instance.new("Folder")
	p.Name = name
	p:SetAttribute("UserId", -simCount)
	p:SetAttribute("CourseMode", mode)
	p.Parent = folder
	return p, ctx.addPlayer(p)
end

local function onLane(ctx, lane, p, pos)
	local st = ctx.states[p]
	st.testHole = lane
	st.started = true
	st.sunk, st.finished, st.resetting = false, false, false
	st.transitionToken = {}
	ctx.placeBall(p, st, pos, "test")
	return st
end

-- Two balls rolled head-on along the flat test lane: do they bounce off each other or pass through?
-- Returns true when they collided (each ends up on its own starting side).
local function headOn(ctx, lane, a, b, z)
	local x = lane.Tee.Position.X
	local y = lane.Tee.Position.Y + Config.BallRadius + 0.02
	local sa = onLane(ctx, lane, a, Vector3.new(x, y, z))
	local sb = onLane(ctx, lane, b, Vector3.new(x, y, z + 4))
	task.wait(0.2)
	sa.ball.AssemblyLinearVelocity = Vector3.new(0, 0, 6)
	sb.ball.AssemblyLinearVelocity = Vector3.new(0, 0, -6)
	task.wait(1.2)
	local za, zb = sa.ball.Position.Z, sb.ball.Position.Z
	sa.ball.Anchored, sb.ball.Anchored = true, true -- parked (the test lane has open ends)
	return za < zb, { za = za, zb = zb, groupA = sa.ball.CollisionGroup, groupB = sb.ball.CollisionGroup }
end

local function sink(ctx, p)
	local st = ctx.states[p]
	local cup = ctx.holesOf(st)[st.hole]:FindFirstChild("Cup")
	ctx.onStroke(p, st.ball.Position)
	ctx.placeBall(p, st, cup.Position - Vector3.new(0, Config.CupDepth - Config.BallRadius, 0), "test")
end

local function waitFor(fn, seconds)
	local t0 = os.clock()
	while os.clock() - t0 < seconds do
		if fn() then
			return true
		end
		task.wait(0.1)
	end
	return fn()
end

-- SRV-139 checks with 3 simulated players. Returns { pass = bool, checks = { {name, ok, detail} } }.
function GolfTestServer.modesTest(ctx, lane, opts)
	local checks, pass = {}, true
	local function check(name, ok, detail)
		pass = pass and ok == true
		table.insert(checks, { name = name, ok = ok == true, detail = detail })
	end
	local A = addSim(ctx, "SimPeacefulA", "Peaceful")
	local B = addSim(ctx, "SimPeacefulB", "Peaceful")
	local P1 = addSim(ctx, "SimPVP1", "PVP")
	local P2 = addSim(ctx, "SimPVP2", "PVP")
	local ok, err = pcall(function()
		local hit, d = headOn(ctx, lane, A, B, 10)
		check("peaceful balls pass through each other", not hit, d)
		hit, d = headOn(ctx, lane, P1, P2, 30)
		check("PVP balls collide", hit, d)
		hit, d = headOn(ctx, lane, P1, A, 50)
		check("PVP ball passes through a Peaceful ball", not hit, d)
		-- switching mode mid-round moves the ball to the other group straight away
		P2:SetAttribute("CourseMode", "Peaceful")
		task.wait(0.1) -- (attribute signals are deferred)
		check("mode switch regroups the ball", ctx.states[P2].ball.CollisionGroup == "GolfBall", ctx.states[P2].ball.CollisionGroup)
		P2:SetAttribute("CourseMode", "PVP")

		-- independent progression: A and P1 start the course; only A sinks
		for _, p in { A, P1 } do
			local st = ctx.states[p]
			st.testHole = nil
			st.started = false
			ctx.onReady(p)
		end
		check("both start on H1", ctx.states[A].hole == 1 and ctx.states[P1].hole == 1)
		sink(ctx, A)
		local wait = Config.HoleTransitionTime + 1.5
		check("A advances to H2 after sinking H1", waitFor(function()
			return ctx.states[A].hole == 2 and not ctx.states[A].sunk
		end, wait), { hole = ctx.states[A].hole })
		check("P1 stays on H1 (A passes P1)", ctx.states[P1].hole == 1 and not ctx.states[P1].sunk, { hole = ctx.states[P1].hole })
		sink(ctx, A)
		check("A advances only to the NEXT hole (H3)", waitFor(function()
			return ctx.states[A].hole == 3 and not ctx.states[A].sunk
		end, wait), { hole = ctx.states[A].hole })
		-- nobody is timed out, skipped or forced to spectate while idle
		task.wait(opts.idle or 4)
		local s1 = ctx.states[P1]
		check("idle P1 is not skipped/spectating", s1.hole == 1 and s1.started and not s1.sunk and not s1.finished and not s1.ball.Anchored, { hole = s1.hole })
		check("A still on H3 (no group sync)", ctx.states[A].hole == 3)

		-- late joiner: starts on H1 and can play immediately, while the others are on H3 / H1
		local L = addSim(ctx, "SimLateJoiner", "Peaceful")
		ctx.onReady(L)
		local sl = ctx.states[L]
		local tee = ctx.holes[1]:FindFirstChild("Tee").Position
		check("late joiner starts on H1", sl.hole == 1 and sl.started and not sl.ball.Anchored and (Vector3.new(sl.ball.Position.X, 0, sl.ball.Position.Z) - Vector3.new(tee.X, 0, tee.Z)).Magnitude < 1, { hole = sl.hole })
		ctx.onStroke(L, sl.ball.Position)
		check("late joiner can stroke immediately", sl.strokes[1] == 1, { strokes = sl.strokes[1] })
		check("late joiner did not move the others", ctx.states[A].hole == 3 and ctx.states[P1].hole == 1)
	end)
	if not ok then
		check("no errors", false, tostring(err))
	end
	for p in ctx.states do
		if typeof(p) == "Instance" and not p:IsA("Player") then
			ctx.removePlayer(p)
			p:Destroy()
		end
	end
	return game:GetService("HttpService"):JSONEncode({ pass = pass, checks = checks })
end

return GolfTestServer.modesTest(ctx, lane, args or {})
		end
		return false, "unknown command " .. tostring(cmd)
	end
	bindable.Parent = game:GetService("ServerStorage")

	print("GOLFTEST|server|ready")
end

------------------------------------------------------------------------------------------------ course modes
-- Simulated players: a Folder per player (attributes UserId, CourseMode) with a server-owned ball.
local simCount = 0
local function addSim(ctx, name, mode)
	local folder = game:GetService("ServerStorage"):FindFirstChild("SimPlayers") or Instance.new("Folder")
	folder.Name = "SimPlayers"
	folder.Parent = game:GetService("ServerStorage")
	simCount += 1
	local p = Instance.new("Folder")
	p.Name = name
	p:SetAttribute("UserId", -simCount)
	p:SetAttribute("CourseMode", mode)
	p.Parent = folder
	return p, ctx.addPlayer(p)
end

local function onLane(ctx, lane, p, pos)
	local st = ctx.states[p]
	st.testHole = lane
	st.started = true
	st.sunk, st.finished, st.resetting = false, false, false
	st.transitionToken = {}
	ctx.placeBall(p, st, pos, "test")
	return st
end

-- Two balls rolled head-on along the flat test lane: do they bounce off each other or pass through?
-- Returns true when they collided (each ends up on its own starting side).
local function headOn(ctx, lane, a, b, z)
	local x = lane.Tee.Position.X
	local y = lane.Tee.Position.Y + Config.BallRadius + 0.02
	local sa = onLane(ctx, lane, a, Vector3.new(x, y, z))
	local sb = onLane(ctx, lane, b, Vector3.new(x, y, z + 4))
	task.wait(0.2)
	sa.ball.AssemblyLinearVelocity = Vector3.new(0, 0, 6)
	sb.ball.AssemblyLinearVelocity = Vector3.new(0, 0, -6)
	task.wait(1.2)
	local za, zb = sa.ball.Position.Z, sb.ball.Position.Z
	sa.ball.Anchored, sb.ball.Anchored = true, true -- parked (the test lane has open ends)
	return za < zb, { za = za, zb = zb, groupA = sa.ball.CollisionGroup, groupB = sb.ball.CollisionGroup }
end

local function sink(ctx, p)
	local st = ctx.states[p]
	local cup = ctx.holesOf(st)[st.hole]:FindFirstChild("Cup")
	ctx.onStroke(p, st.ball.Position)
	ctx.placeBall(p, st, cup.Position - Vector3.new(0, Config.CupDepth - Config.BallRadius, 0), "test")
end

local function waitFor(fn, seconds)
	local t0 = os.clock()
	while os.clock() - t0 < seconds do
		if fn() then
			return true
		end
		task.wait(0.1)
	end
	return fn()
end

-- SRV-139 checks with 3 simulated players. Returns { pass = bool, checks = { {name, ok, detail} } }.
function GolfTestServer.modesTest(ctx, lane, opts)
	local checks, pass = {}, true
	local function check(name, ok, detail)
		pass = pass and ok == true
		table.insert(checks, { name = name, ok = ok == true, detail = detail })
	end
	local A = addSim(ctx, "SimPeacefulA", "Peaceful")
	local B = addSim(ctx, "SimPeacefulB", "Peaceful")
	local P1 = addSim(ctx, "SimPVP1", "PVP")
	local P2 = addSim(ctx, "SimPVP2", "PVP")
	local ok, err = pcall(function()
		local hit, d = headOn(ctx, lane, A, B, 10)
		check("peaceful balls pass through each other", not hit, d)
		hit, d = headOn(ctx, lane, P1, P2, 30)
		check("PVP balls collide", hit, d)
		hit, d = headOn(ctx, lane, P1, A, 50)
		check("PVP ball passes through a Peaceful ball", not hit, d)
		-- switching mode mid-round moves the ball to the other group straight away
		P2:SetAttribute("CourseMode", "Peaceful")
		task.wait(0.1) -- (attribute signals are deferred)
		check("mode switch regroups the ball", ctx.states[P2].ball.CollisionGroup == "GolfBall", ctx.states[P2].ball.CollisionGroup)
		P2:SetAttribute("CourseMode", "PVP")

		-- independent progression: A and P1 start the course; only A sinks
		for _, p in { A, P1 } do
			local st = ctx.states[p]
			st.testHole = nil
			st.started = false
			ctx.onReady(p)
		end
		check("both start on H1", ctx.states[A].hole == 1 and ctx.states[P1].hole == 1)
		sink(ctx, A)
		local wait = Config.HoleTransitionTime + 1.5
		check("A advances to H2 after sinking H1", waitFor(function()
			return ctx.states[A].hole == 2 and not ctx.states[A].sunk
		end, wait), { hole = ctx.states[A].hole })
		check("P1 stays on H1 (A passes P1)", ctx.states[P1].hole == 1 and not ctx.states[P1].sunk, { hole = ctx.states[P1].hole })
		sink(ctx, A)
		check("A advances only to the NEXT hole (H3)", waitFor(function()
			return ctx.states[A].hole == 3 and not ctx.states[A].sunk
		end, wait), { hole = ctx.states[A].hole })
		-- nobody is timed out, skipped or forced to spectate while idle
		task.wait(opts.idle or 4)
		local s1 = ctx.states[P1]
		check("idle P1 is not skipped/spectating", s1.hole == 1 and s1.started and not s1.sunk and not s1.finished and not s1.ball.Anchored, { hole = s1.hole })
		check("A still on H3 (no group sync)", ctx.states[A].hole == 3)

		-- late joiner: starts on H1 and can play immediately, while the others are on H3 / H1
		local L = addSim(ctx, "SimLateJoiner", "Peaceful")
		ctx.onReady(L)
		local sl = ctx.states[L]
		local tee = ctx.holes[1]:FindFirstChild("Tee").Position
		check("late joiner starts on H1", sl.hole == 1 and sl.started and not sl.ball.Anchored and (Vector3.new(sl.ball.Position.X, 0, sl.ball.Position.Z) - Vector3.new(tee.X, 0, tee.Z)).Magnitude < 1, { hole = sl.hole })
		ctx.onStroke(L, sl.ball.Position)
		check("late joiner can stroke immediately", sl.strokes[1] == 1, { strokes = sl.strokes[1] })
		check("late joiner did not move the others", ctx.states[A].hole == 3 and ctx.states[P1].hole == 1)
	end)
	if not ok then
		check("no errors", false, tostring(err))
	end
	for p in ctx.states do
		if typeof(p) == "Instance" and not p:IsA("Player") then
			ctx.removePlayer(p)
			p:Destroy()
		end
	end
	return game:GetService("HttpService"):JSONEncode({ pass = pass, checks = checks })
end

return GolfTestServer
