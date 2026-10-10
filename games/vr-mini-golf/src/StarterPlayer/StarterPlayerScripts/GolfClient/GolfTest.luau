-- GolfTest: client half of the Studio playtest harness (see games/vr-mini-golf/playtesting.md).
-- Only started by GolfMain when RunService:IsStudio() and workspace.GolfTestMode == true.
--
-- Scenarios run here because the ball is simulated by its owner's client. Every shot goes through
-- Ball.hit(), the same function the VR putter and the phone pull-back use. The runner
-- (tools/run_playtests.py) drives everything through the client-local BindableFunction
-- ReplicatedStorage.GolfTestAPI:
--   Invoke("list")                 -> JSON [{name, desc, vr, seconds}]
--   Invoke("start", name, cam)     -> "started" | "error: ..."   (cam: "fixed" | "topdown" | "follow" | "")
--   Invoke("status")               -> JSON {running, name, cam, elapsed, lines, error}
--   Invoke("log", fromLine, chars) -> "<nextLine>\n<jsonl lines>"
--   Invoke("result", name)         -> JSON result of the last run of that scenario
--   Invoke("clubpose", legacy, view) -> JSON club geometry: holds the club hand in a putting grip next to the ball
--                                      (Config.VRClubLegacyAim = legacy) with the club debug overlay on and the
--                                      camera on "side" | "front" | "top" of the stance (for screenshots)
-- Compact event lines are also printed with the prefix "GOLFTEST|".
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local HttpService = game:GetService("HttpService")

local Golf = ReplicatedStorage:WaitForChild("Golf")
local Config = require(Golf:WaitForChild("Config"))
local Remotes = Golf:WaitForChild("Remotes")

local player = Players.LocalPlayer
local R = Config.BallRadius
local STUD = 0.3 -- metres per stud
local SAMPLE_DT = 1 / 30

local GolfTest = {}

local function mps(m: number)
	return m / STUD
end
local function flat(v: Vector3)
	return Vector3.new(v.X, 0, v.Z)
end
local function round(x: number, d: number?)
	local m = 10 ^ (d or 3)
	return math.floor(x * m + 0.5) / m
end
local function vec(v: Vector3)
	return { round(v.X, 4), round(v.Y, 4), round(v.Z, 4) }
end

-- Ideal flat rollout for Config's rolling model dv/dt = -(RollDecel + RollDrag * v): distance (studs), time (s).
local function idealRollout(v0: number)
	local a, k = Config.RollDecel, Config.RollDrag or 0
	if k < 1e-6 then
		return v0 * v0 / (2 * a), v0 / a
	end
	return (v0 - (a / k) * math.log(1 + k * v0 / a)) / k, math.log(1 + k * v0 / a) / k
end

------------------------------------------------------------------------ run state + logging
local lines = {} -- encoded JSONL for the current run
local results = {} -- [scenario] = result table
local run = { running = false, name = "", cam = "", t0 = 0, err = nil }
local shot = nil -- data for the shot in flight (or nil)
local shotLabel = nil

local function now()
	return os.clock() - run.t0
end

local function record(entry)
	entry.t = round(now(), 4)
	entry.shot = entry.shot or shotLabel
	table.insert(lines, HttpService:JSONEncode(entry))
end

local function event(kind: string, data)
	data = data or {}
	data.type = "event"
	data.event = kind
	record(data)
	local copy = table.clone(data)
	copy.type, copy.event = nil, nil
	print("GOLFTEST|" .. run.name .. "|" .. kind .. "|" .. HttpService:JSONEncode(copy))
end

local function physicsOf(name: string)
	for _, d in workspace.Course:GetDescendants() do
		if d:IsA("BasePart") and d.Name == name then
			local p = d.CustomPhysicalProperties
			return p and {
				density = round(p.Density),
				friction = round(p.Friction),
				elasticity = round(p.Elasticity),
				frictionWeight = round(p.FrictionWeight),
				elasticityWeight = round(p.ElasticityWeight),
				group = d.CollisionGroup,
			} or { group = d.CollisionGroup }
		end
	end
	return nil
end

------------------------------------------------------------------------ module refs (set in start)
local Ball, VR, simVR
local debugFolder

------------------------------------------------------------------------ outcome tracking
local outcome = nil -- "rest" | "cup" | "oob"
local placedCount = 0

local contactParams = RaycastParams.new()
contactParams.FilterType = Enum.RaycastFilterType.Exclude

local surfaceParams = RaycastParams.new()
surfaceParams.FilterType = Enum.RaycastFilterType.Exclude

local function partLabel(p: Instance?)
	if not p then
		return "?"
	end
	local anc = p.Parent
	while anc and anc ~= workspace and anc:GetAttribute("HoleNumber") == nil do
		anc = anc.Parent
	end
	return ((anc and anc ~= workspace) and anc.Name .. "/" or "") .. p.Name
end

-- contact detection state
local prevVel, prevPos = nil, nil
local pending = nil
local lastSample = -1

local function finishContact(c, vOut: Vector3)
	local n
	if c.hit then
		n = flat(c.hit.Normal)
	end
	if not n or n.Magnitude < 0.3 then
		n = flat(vOut - c.vIn)
	end
	if n.Magnitude < 1e-4 then
		return
	end
	n = n.Unit
	local vin, vout = flat(c.vIn), flat(vOut)
	local tan = Vector3.yAxis:Cross(n)
	local inN, outN = vin:Dot(n), vout:Dot(n)
	local inT, outT = vin:Dot(tan), vout:Dot(tan)
	local info = {
		part = partLabel(c.hit and c.hit.Instance),
		normal = vec(n),
		vIn = vec(c.vIn),
		vOut = vec(vOut),
		speedIn = round(vin.Magnitude),
		speedOut = round(vout.Magnitude),
		vnIn = round(inN),
		vnOut = round(outN),
		vtIn = round(inT),
		vtOut = round(outT),
		angleIn = round(math.deg(math.atan2(math.abs(inT), math.abs(inN))), 1),
		angleOut = round(math.deg(math.atan2(math.abs(outT), math.abs(outN))), 1),
		pos = vec(c.pos),
	}
	if math.abs(inN) > 0.05 then
		info.restitution = round(math.abs(outN) / math.abs(inN))
	end
	if math.abs(inT) > 0.3 then
		info.tangentialRetention = round(outT / inT)
	end
	info.speedRetention = round(vout.Magnitude / math.max(vin.Magnitude, 1e-3))
	info.tContact = round(now(), 4)
	-- Walkabout reference: ~0.6 right after a head-on hit, ~1/3 of the incoming speed 0.3 s later (skid)
	local b = Ball.ball
	task.delay(0.3, function()
		if b then
			info.speedAfter300ms = round(flat(b.AssemblyLinearVelocity).Magnitude)
			info.retentionAfter300ms = round(info.speedAfter300ms / math.max(vin.Magnitude, 1e-3))
		end
	end)
	event("contact", info)
	if shot then
		table.insert(shot.contacts, info)
	end
end

local function onPostSimulation(dt)
	if not run.running then
		return
	end
	local b = Ball.ball
	if not b then
		return
	end
	local t = now()
	local v = b.AssemblyLinearVelocity
	local p = b.Position
	if t - lastSample >= SAMPLE_DT - 1e-3 then
		lastSample = t
		record({ type = "sample", p = vec(p), v = vec(v), s = Ball.state })
	end
	if shot then
		local speed = v.Magnitude
		shot.maxY = math.max(shot.maxY, p.Y)
		shot.maxAlong = math.max(shot.maxAlong, (p - shot.start):Dot(shot.dir))
		if not shot.tStop and Ball.state == "moving" and t - shot.t0 > 0.05 and speed < Config.StopSpeed then
			shot.tStop = t - shot.t0
		end
		if shot.cup and not shot.rimSpeed then
			local d = flat(p - shot.cup.Position).Magnitude
			if d < shot.cup:GetAttribute("Radius") then
				shot.rimSpeed = round(flat(v).Magnitude)
				shot.rimTime = round(t - shot.t0)
			end
		end
	end
	-- wall / obstacle contacts: a sudden change in horizontal velocity while rolling
	if pending then
		pending.frames += 1
		if pending.frames >= 2 then
			finishContact(pending, v)
			pending = nil
		end
	elseif prevVel and Ball.state == "moving" and not b.Anchored then
		local a, c = flat(prevVel), flat(v)
		local dv = (c - a).Magnitude
		if a.Magnitude > 0.3 and dv > math.max(0.4, Config.RollDecel * dt + 0.08 * a.Magnitude) then
			contactParams.FilterDescendantsInstances = { workspace:FindFirstChild("Balls"), player.Character, workspace.CurrentCamera }
			local hit = workspace:Spherecast(prevPos, R * 0.95, a.Unit * (a.Magnitude * dt * 1.5 + 0.25), contactParams)
			pending = { frames = 0, vIn = prevVel, pos = p, hit = hit }
		end
	end
	prevVel, prevPos = v, p
end

------------------------------------------------------------------------ scenario helpers
local function setFrame(focus: Vector3, size: number, viewDir: Vector3?)
	workspace:SetAttribute("GolfTestFocus", focus)
	workspace:SetAttribute("GolfTestFrameSize", size)
	workspace:SetAttribute("GolfTestViewDir", viewDir or Vector3.new(0, 0, 1))
end

local testRemote

-- Places the ball on `hole` (0 = test lane) at (x, surfaceY + R, z) through the server, then waits until it's
-- puttable (same BallPlaced flow as a new hole).
local function place(hole: number, x: number, z: number, surfaceY: number)
	local pos = Vector3.new(x, surfaceY + R + 0.03, z)
	local before = placedCount
	outcome = nil
	shot = nil
	local ok, err = testRemote:InvokeServer("place", { hole = hole, pos = pos })
	if not ok then
		error("place failed: " .. tostring(err))
	end
	local t0 = os.clock()
	while (placedCount == before or Ball.state ~= "ready") and os.clock() - t0 < 6 do
		task.wait()
	end
	if Ball.state ~= "ready" then
		error("ball not ready after place (state " .. Ball.state .. ")")
	end
	task.wait(0.25)
	event("placed", { hole = hole, pos = vec(Ball.ball.Position) })
end

local function waitOutcome(timeout: number)
	local t0 = os.clock()
	while not outcome and os.clock() - t0 < timeout do
		task.wait()
	end
	return outcome or "timeout"
end

-- One scripted shot: ball velocity `dir * speed` through Ball.hit (the VR/touch code path).
local function shoot(label: string, dir: Vector3, speedMps: number, opts)
	opts = opts or {}
	shotLabel = label
	dir = flat(dir).Unit
	local b = Ball.ball
	local start = b.Position
	shot = {
		label = label,
		start = start,
		dir = dir,
		t0 = now(),
		contacts = {},
		maxY = start.Y,
		maxAlong = 0,
		cup = opts.cup,
	}
	outcome = nil
	local okHit = Ball.hit(dir * mps(speedMps), "test")
	if not okHit then
		event("error", { msg = "hit refused", state = Ball.state })
		shot = nil
		return { label = label, outcome = "refused" }
	end
	local res = waitOutcome(opts.timeout or 20)
	local s = shot
	shot = nil
	task.wait(0.05)
	local finish = b.Position
	local flatDist = flat(finish - start).Magnitude
	local out = {
		label = label,
		speedMps = speedMps,
		v0 = round(mps(speedMps)),
		outcome = res,
		start = vec(start),
		finish = vec(finish),
		distStuds = round(flatDist),
		distM = round(flatDist * STUD),
		tStop = s.tStop and round(s.tStop),
		tEnd = round(now() - s.t0),
		maxY = round(s.maxY),
		maxAlong = round(s.maxAlong),
		contacts = s.contacts,
		rimSpeed = s.rimSpeed,
		rimSpeedMps = s.rimSpeed and round(s.rimSpeed * STUD),
		rimTime = s.rimTime,
	}
	event("shot", {
		label = label,
		outcome = res,
		distM = out.distM,
		tStop = out.tStop,
		contacts = #s.contacts,
		rimSpeedMps = out.rimSpeedMps,
	})
	shotLabel = nil
	return out
end

local function hole(n)
	return workspace.Course:FindFirstChild("Hole" .. n)
end

local function ballPlaneY()
	return Ball.ball.Position.Y - R
end

------------------------------------------------------------------------ simulated VR hand driving
local poseFn = nil -- function(t) -> world CFrame for the club hand, or nil
local lastPoseClock = 0 -- os.clock() the current hand pose was computed for
local PARKED = CFrame.new(0.4, 6.5, -0.3) * CFrame.Angles(math.rad(90), 0, 0) -- club pointing straight up

local function parkHand()
	poseFn = nil
	if debugFolder then
		-- PARKED is the club's rotation; turn it into the hand rotation for the current club mount
		local _, clubOffset = VR.test.getClubMount()
		debugFolder.RightHand.Value = PARKED * clubOffset.Rotation:Inverse()
	end
end

local function driveHand()
	if not (poseFn and VR and VR.test) then
		return
	end
	lastPoseClock = os.clock()
	local cf = poseFn(lastPoseClock)
	if cf then
		debugFolder.RightHand.Value = VR.test.toLocal(cf)
	end
end

local function headPart()
	return VR.test.putter:FindFirstChild("Head")
end

local function vrRequired()
	if not (simVR and VR and VR.test) then
		return { skipped = "needs SimulateVR (set workspace.SimulateVR = true before Play)" }
	end
	return nil
end

------------------------------------------------------------------------ scenarios
local S = 1 -- felt surface height on holes 1, 2, 4 and the test lane
local HILL_LOW, HILL_HIGH = 1, 2.2
local SCENARIOS = {}

local function scenario(def)
	table.insert(SCENARIOS, def)
end

scenario({
	name = "rollout",
	desc = "Straight putts at 2/4/6 m/s on the flat test lane: rollout distance and time",
	seconds = 30,
	run = function()
		local shots = {}
		for _, speed in { 2, 4, 6 } do
			place(0, -40, -6, S)
			local d, t = idealRollout(mps(speed))
			setFrame(Vector3.new(-40, S, -6 + d / 2), math.max(8, d + 4), Vector3.new(1, 0, 0))
			local r = shoot(speed .. "mps", Vector3.new(0, 0, 1), speed, { timeout = t + 6 })
			r.idealM = round(d * STUD)
			r.idealT = round(t)
			table.insert(shots, r)
		end
		return { shots = shots }
	end,
})

scenario({
	name = "bank",
	desc = "Hole 2 Dogleg 45-degree bank wall at 4 and 6 m/s: speed and angle in/out",
	seconds = 13,
	run = function()
		local shots = {}
		setFrame(Vector3.new(31, S, 15), 14, Vector3.new(1, 0, 1))
		for _, speed in { 4, 6 } do
			place(2, 30, 2, S)
			table.insert(shots, shoot("bank-" .. speed .. "mps", Vector3.new(0, 0, 1), speed, { timeout = 6 }))
		end
		return { shots = shots }
	end,
})

scenario({
	name = "walls",
	desc = "Restitution: straight wall head-on (3 and 6 m/s) and at 45 degrees, bumper post head-on and at 45 degrees",
	seconds = 15,
	run = function()
		local shots = {}
		-- hole 1 end wall (inner face z = 32), head-on
		setFrame(Vector3.new(-1, S, 27), 10, Vector3.new(1, 0, 0))
		for _, speed in { 3, 6 } do
			place(1, -2.5, 24, S)
			table.insert(shots, shoot("wall-straight-" .. speed .. "mps", Vector3.new(0, 0, 1), speed, { timeout = 3 }))
		end
		-- hole 1 right wall (inner face x = 4) at 45 degrees
		place(1, 1, 22, S)
		table.insert(shots, shoot("wall-45deg-5mps", Vector3.new(1, 0, 1), 5, { timeout = 3 }))
		-- hole 2 bumper post (44, 20), r 0.6: head-on, then offset so the contact normal is 45 degrees
		setFrame(Vector3.new(42, S, 20), 8, Vector3.new(0, 0, 1))
		place(2, 40, 20, S)
		table.insert(shots, shoot("post-straight-6mps", Vector3.new(1, 0, 0), 6, { timeout = 3 }))
		place(2, 40, 20 + (0.6 + R) * math.sin(math.rad(45)), S)
		table.insert(shots, shoot("post-45deg-5mps", Vector3.new(1, 0, 0), 5, { timeout = 3 }))
		return { shots = shots }
	end,
})

scenario({
	name = "windmill",
	desc = "Hole 4: putt through the windmill tunnel at 4 m/s, timed to two blade phases",
	seconds = 20,
	run = function()
		local shots = {}
		local mill = hole(4):FindFirstChild("Windmill")
		local omega = (mill:GetAttribute("RPS") or 0.25) * math.pi * 2
		setFrame(Vector3.new(115, S, 20), 26, Vector3.new(1, 0, 0))
		for _, phase in { 0, 45 } do
			place(4, 115, -1, S)
			-- wait for a fixed blade phase (4 blades -> the pattern repeats every 90 degrees)
			local period = (math.pi / 2) / omega
			local t0 = os.clock()
			while os.clock() - t0 < period + 0.1 do
				local a = math.deg((workspace:GetServerTimeNow() * omega) % (math.pi / 2))
				if math.abs(a - phase) < 2 then
					break
				end
				task.wait()
			end
			table.insert(shots, shoot("mill-phase" .. phase, Vector3.new(0, 0, 1), 4, { cup = hole(4).Cup, timeout = 14 }))
		end
		return { shots = shots }
	end,
})

scenario({
	name = "hill",
	desc = "Hole 3 The Hill: 5 m/s climbs to the green, 2 m/s rolls back",
	seconds = 22,
	run = function()
		local shots = {}
		local dir = Vector3.new(77 - 75, 0, 25 - 0)
		setFrame(Vector3.new(75, 1.6, 12), 22, Vector3.new(1, 0, 0))
		for _, def in { { "hill-strong-5mps", 5 }, { "hill-weak-2mps", 2 } } do
			place(3, 75, 0, HILL_LOW)
			local r = shoot(def[1], dir, def[2], { cup = hole(3).Cup, timeout = 14 })
			r.madeGreen = r.maxY > HILL_HIGH + R - 0.05
			r.endedOnGreen = r.finish[2] > HILL_HIGH + R - 0.05
			r.rolledBack = r.finish[3] < 6
			table.insert(shots, r)
		end
		return { shots = shots }
	end,
})

scenario({
	name = "cup",
	desc = "Hole 1 cup from 60 cm at 1.3 to 4 m/s: holed or lip-out, speed at the rim",
	seconds = 16,
	run = function()
		local shots = {}
		local cup = hole(1).Cup
		setFrame(Vector3.new(0, S, 27), 6, Vector3.new(1, 0, 0))
		for _, speed in { 1.3, 1.6, 2.0, 2.5, 3.0, 4.0 } do
			place(1, 0, 25, S)
			local r = shoot("cup-" .. speed .. "mps", Vector3.new(0, 0, 1), speed, { cup = cup, timeout = 6 })
			r.holed = r.outcome == "cup"
			r.cupPos = vec(cup.Position)
			-- first pass: holed without touching anything away from the cup (the drop itself bumps the cup's
			-- rim/liner, which the contact detector also logs, so contacts inside the cup don't count)
			local away = 0
			for _, c in r.contacts do
				if flat(Vector3.new(c.pos[1], c.pos[2], c.pos[3]) - cup.Position).Magnitude > cup:GetAttribute("Radius") + 2 * R then
					away += 1
				end
			end
			r.holedFirstPass = r.holed and away == 0
			table.insert(shots, r)
		end
		return { shots = shots }
	end,
})

-- Measures, relative to the plane the ball rests on: the VR rig floor, the character's feet, and the putter
-- head bottom with the (simulated) club held over the neighbouring ledge.
local function measureLedge(label, holeN, ballX, ballZ, surfaceY, clubX, clubZ, teleportHead)
	place(holeN, ballX, ballZ, surfaceY)
	local ballStart = Ball.ball.Position
	if teleportHead then
		VR.test.placeHead(teleportHead, Vector3.new(1, 0, 0), nil)
	end
	local half = VR.test.headSize / 2
	local plane = ballPlaneY()
	-- hold the putter head over the ledge, a few mm below the ball's plane (so any floor clamp engages)
	local target = Vector3.new(clubX, plane + half.Y + 0.01 - 0.03, clubZ)
	poseFn = function()
		return VR.test.handCFrameFor(target, Vector3.new(0, 0, 1))
	end
	task.wait(1.0)
	local head = headPart()
	local char = player.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart")
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	local headBottom = head.Position.Y - half.Y
	local res = {
		label = label,
		ballPlaneY = round(plane, 4),
		rigFloorY = round(VR.test.getOrigin().Y, 4),
		headBottomY = round(headBottom, 4),
		headPos = vec(head.Position),
		headTarget = vec(target),
		ballMoved = round((Ball.ball.Position - ballStart).Magnitude, 4),
	}
	res.rigDelta = round(res.rigFloorY - plane, 4)
	res.headDelta = round(headBottom - plane, 4)
	if hrp and hum then
		local feet = hrp.Position.Y - hum.HipHeight - hrp.Size.Y / 2
		res.charFeetY = round(feet, 4)
		res.charDelta = round(feet - plane, 4)
	end
	local wall = hole(holeN).Geometry:FindFirstChild("Wall")
	res.wallGroup = wall and wall.CollisionGroup
	res.playerCollidesWithWall = wall and game:GetService("PhysicsService"):CollisionGroupsAreCollidable(wall.CollisionGroup, "GolfPlayer")
	res.ok = math.abs(res.rigDelta) < 0.05 and math.abs(res.headDelta) < 0.05 and (res.charDelta == nil or math.abs(res.charDelta) < 0.1)
	event("ledge", res)
	parkHand()
	return res
end

scenario({
	name = "ledge",
	desc = "VR plane snap: ball beside a rail/ledge; putter head, VR rig floor and character must stay on the ball's plane",
	vr = true,
	seconds = 14,
	run = function()
		local skip = vrRequired()
		if skip then
			return skip
		end
		local cases = {}
		setFrame(Vector3.new(4, S, 8), 6, Vector3.new(0, 0, 1))
		-- ball touching hole 1's right wall (inner face x = 4); the warp stance lands outside the wall
		table.insert(cases, measureLedge("h1-ball-at-wall", 1, 4 - R - 0.01, 8, S, 4.35, 8))
		-- ball 1 stud from the wall: the warp stance lands on top of the wall
		table.insert(cases, measureLedge("h1-stance-on-wall", 1, 3, 8, S, 4.3, 8.2))
		-- The Hill's raised green, ball at the left wall (inner face x = 69), head teleported over the wall
		setFrame(Vector3.new(69, HILL_HIGH, 22), 6, Vector3.new(0, 0, 1))
		table.insert(cases, measureLedge("h3-green-edge", 3, 69 + R + 0.01, 22, HILL_HIGH, 68.6, 22.3, Vector3.new(68.5, HILL_HIGH, 22)))
		local ok = true
		for _, c in cases do
			ok = ok and c.ok
		end
		return { cases = cases, ok = ok }
	end,
})

-- Sweeps the simulated putter head along a straight line at the ball's plane height and checks that it
-- follows the hand exactly (no collision pushback, no climbing) and never moves the ball.
local function sweep(label, from: Vector3, to: Vector3, seconds: number)
	local half = VR.test.headSize / 2
	local plane = ballPlaneY()
	local y = plane + half.Y + 0.01
	local a = Vector3.new(from.X, y, from.Z)
	local b = Vector3.new(to.X, y, to.Z)
	local dir = flat(b - a).Unit
	local ballStart = Ball.ball.Position
	local hitsBefore = GolfTest.hitCount
	local t0 = os.clock() + 0.4
	poseFn = function(t)
		local f = math.clamp((t - t0) / seconds, 0, 1)
		return VR.test.handCFrameFor(a:Lerp(b, f), dir)
	end
	local maxErr, maxLift = 0, 0
	local head = headPart()
	-- the 0.4 s lead-in moves the club from its parked pose to the start of the sweep; measure after that
	while os.clock() < t0 do
		RunService.PostSimulation:Wait()
	end
	while os.clock() < t0 + seconds + 0.2 do
		RunService.PostSimulation:Wait()
		-- compare with the hand pose this frame's putter was built from (not "now": Studio may run at 20 fps)
		local f = math.clamp((lastPoseClock - t0) / seconds, 0, 1)
		local want = a:Lerp(b, f)
		maxErr = math.max(maxErr, flat(head.Position - want).Magnitude)
		maxLift = math.max(maxLift, head.Position.Y - y)
	end
	local props = {}
	local allGhost = true
	for _, p in VR.test.putter:GetDescendants() do
		if p:IsA("BasePart") then
			props[p.Name] = { canCollide = p.CanCollide, canTouch = p.CanTouch, canQuery = p.CanQuery, anchored = p.Anchored }
			allGhost = allGhost and not p.CanCollide and not p.CanTouch and p.Anchored
		end
	end
	local res = {
		label = label,
		maxFollowError = round(maxErr, 4),
		maxLift = round(maxLift, 4),
		ballMoved = round((Ball.ball.Position - ballStart).Magnitude, 4),
		hits = GolfTest.hitCount - hitsBefore,
		clubParts = props,
		clubPartsGhost = allGhost,
	}
	-- the face was 5 mm below the wall top at most if it "climbed"; anything over 2 cm means it rode up
	res.ok = allGhost and res.maxFollowError < 0.02 and res.maxLift < 0.07 and res.ballMoved < 0.01 and res.hits == 0
	event("sweep", res)
	parkHand()
	task.wait(0.2)
	return res
end

scenario({
	name = "ghost",
	desc = "VR club ghosting: sweep the putter head through a wall and a bumper post, then a real VR swing hit",
	vr = true,
	seconds = 15,
	run = function()
		local skip = vrRequired()
		if skip then
			return skip
		end
		local out = {}
		-- through hole 1's right wall (x 4..5) with the ball well away
		setFrame(Vector3.new(4, S, 18), 8, Vector3.new(0, 0, 1))
		place(1, 0, 18, S)
		out.wall = sweep("through-wall", Vector3.new(2.6, 0, 20), Vector3.new(6.2, 0, 20), 1.0)
		-- through hole 2's first bumper post (44, 20)
		setFrame(Vector3.new(43, S, 20), 8, Vector3.new(0, 0, 1))
		place(2, 39, 20, S)
		out.post = sweep("through-post", Vector3.new(42.4, 0, 20.1), Vector3.new(45.6, 0, 20.1), 1.0)
		-- a real swing through the ball: putter face speed 4 studs/s (1.2 m/s) along +Z
		setFrame(Vector3.new(0, S, 9), 8, Vector3.new(1, 0, 0))
		place(1, 0, 6, S)
		local half = VR.test.headSize / 2
		local y = ballPlaneY() + half.Y + 0.01
		local clubSpeed = 4
		local a = Vector3.new(0, y, 6 - R - half.X - 0.5)
		local t0 = os.clock() + 0.5
		local strokesBefore = GolfTest.hitCount
		outcome = nil
		shot = { label = "vr-swing", start = Ball.ball.Position, dir = Vector3.new(0, 0, 1), t0 = now(), contacts = {}, maxY = 0, maxAlong = 0 }
		shotLabel = "vr-swing"
		poseFn = function(t)
			local d = math.max(0, t - t0) * clubSpeed
			return VR.test.handCFrameFor(a + Vector3.new(0, 0, math.min(d, 1.4)), Vector3.new(0, 0, 1))
		end
		local tWait = os.clock()
		while GolfTest.hitCount == strokesBefore and os.clock() - tWait < 3 do
			task.wait()
		end
		parkHand()
		local res = waitOutcome(10)
		shot = nil
		shotLabel = nil
		local expected = clubSpeed * Config.VRHitMultiplier
		out.swing = {
			hit = GolfTest.hitCount > strokesBefore,
			source = GolfTest.lastHitSource,
			ballSpeed = GolfTest.lastHitVelocity and round(GolfTest.lastHitVelocity.Magnitude),
			expectedSpeed = round(expected),
			outcome = res,
			distM = round(flat(Ball.ball.Position - Vector3.new(0, 0, 6)).Magnitude * STUD),
		}
		out.swing.ok = out.swing.hit and out.swing.source == "vr" and math.abs((out.swing.ballSpeed or 0) - expected) < 0.25 * expected
		event("swing", out.swing)
		out.ok = out.wall.ok and out.post.ok and out.swing.ok
		return out
	end,
})

------------------------------------------------------------------------ club debug overlay (GolfTestClubDebug)
-- A part-built Quest Touch proxy at the simulated club-hand CFrame, plus axis gizmos (X red, Y green, Z blue;
-- thick = hand, thin = club mount at the shaft start), the aim ray (-Z, yellow) and a marker for the head.
-- The proxy is the PHYSICAL controller (handle along Config.VRClubGripPitch), whatever mount the code uses, so
-- with VRClubLegacyAim the screenshots show where the old club came out relative to the real handle.
local clubDebug = nil
local function dbgPart(name, size, color, material, shape)
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	if shape then
		p.Shape = shape
	end
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = true, false, false, false, false
	p.Parent = clubDebug
	return p
end
local function physicalGripDir()
	-- handle bottom direction in hand space: -Y raked VRClubGripPitch toward +Z
	return CFrame.Angles(math.rad(-90 - (Config.VRClubGripPitch or 35)), 0, 0).LookVector
end
local function buildClubDebug()
	clubDebug = Instance.new("Folder")
	clubDebug.Name = "GolfTestClubDebug"
	local dark, grey = Color3.fromRGB(35, 35, 40), Color3.fromRGB(200, 200, 205)
	dbgPart("Handle", Vector3.new(0.3, 0.12, 0.12), dark, nil, Enum.PartType.Cylinder)
	dbgPart("Top", Vector3.new(0.17, 0.035, 0.2), dark)
	dbgPart("Stick", Vector3.new(0.03, 0.05, 0.05), grey, nil, Enum.PartType.Cylinder)
	dbgPart("Ring", Vector3.new(0.03, 0.34, 0.34), grey, nil, Enum.PartType.Cylinder).Transparency = 0.25
	dbgPart("Trigger", Vector3.new(0.05, 0.09, 0.04), Color3.fromRGB(230, 80, 60))
	dbgPart("ButtCap", Vector3.new(0.025, 0.13, 0.13), Color3.fromRGB(255, 170, 0), Enum.Material.Neon, Enum.PartType.Cylinder)
	for _, set in { { "Hand", 0.03, 0.65 }, { "Club", 0.016, 0.45 } } do
		for _, ax in { { "X", Color3.fromRGB(255, 40, 40) }, { "Y", Color3.fromRGB(40, 230, 40) }, { "Z", Color3.fromRGB(50, 90, 255) } } do
			dbgPart(set[1] .. ax[1], Vector3.new(set[2], set[2], set[3]), ax[2], Enum.Material.Neon)
		end
	end
	dbgPart("AimRay", Vector3.new(0.012, 0.012, 1.4), Color3.fromRGB(255, 230, 40), Enum.Material.Neon).Transparency = 0.2
	dbgPart("PlayerHead", Vector3.new(0.7, 0.85, 0.75), Color3.fromRGB(240, 200, 170), nil, Enum.PartType.Ball).Transparency = 0.35
	dbgPart("Nose", Vector3.new(0.08, 0.08, 0.25), Color3.fromRGB(240, 200, 170)).Transparency = 0.35
	clubDebug.Parent = workspace
end
local function segment(part, a: Vector3, b: Vector3)
	part.Size = Vector3.new(part.Size.X, part.Size.Y, math.max((b - a).Magnitude, 0.01))
	part.CFrame = CFrame.lookAt((a + b) / 2, b)
end
local function updateClubDebug()
	local on = workspace:GetAttribute("GolfTestClubDebug") == true and VR and VR.test
	if not on then
		if clubDebug then
			clubDebug:Destroy()
			clubDebug = nil
		end
		return
	end
	if not clubDebug then
		buildClubDebug()
	end
	local hand = VR.getState().hand
	local g = hand:VectorToWorldSpace(physicalGripDir())
	local butt = hand.Position + g * (Config.VRClubButtOffset or 0.25)
	local top = hand.Position - g * 0.05
	local cyl = CFrame.Angles(0, math.rad(90), 0) -- cylinder axis (X) along a lookAt's LookVector
	clubDebug.Handle.Size = Vector3.new((butt - top).Magnitude, 0.12, 0.12)
	clubDebug.Handle.CFrame = CFrame.lookAt((butt + top) / 2, butt) * cyl
	clubDebug.ButtCap.CFrame = CFrame.lookAt(butt, butt + g) * cyl
	clubDebug.Top.CFrame = hand * CFrame.new(0, 0.03, -0.03)
	clubDebug.Stick.CFrame = hand * CFrame.new(0, 0.06, 0.0) * CFrame.Angles(0, 0, math.rad(90))
	-- tracking ring: a halo over the top front of the controller
	clubDebug.Ring.CFrame = hand * CFrame.new(0, 0.1, -0.12) * CFrame.Angles(math.rad(-45), 0, 0) * CFrame.Angles(0, 0, math.rad(90))
	clubDebug.Trigger.CFrame = hand * CFrame.new(0, -0.03, -0.1) * CFrame.Angles(math.rad(-(Config.VRClubGripPitch or 35)), 0, 0)
	local _, _, clubCF = VR.test.getClubMount()
	for _, set in { { "Hand", hand }, { "Club", clubCF } } do
		local cf, len = set[2], clubDebug[set[1] .. "X"].Size.Z
		segment(clubDebug[set[1] .. "X"], cf.Position, cf.Position + cf.RightVector * len)
		segment(clubDebug[set[1] .. "Y"], cf.Position, cf.Position + cf.UpVector * len)
		segment(clubDebug[set[1] .. "Z"], cf.Position, cf.Position - cf.LookVector * len) -- +Z
	end
	segment(clubDebug.AimRay, hand.Position, hand.Position + hand.LookVector * 1.4)
	local headCF = VR.test.getOrigin() * debugFolder.Head.Value
	clubDebug.PlayerHead.CFrame = headCF
	clubDebug.Nose.CFrame = headCF * CFrame.new(0, 0, -0.42)
end

-- Holds the simulated club hand in a typical putting grip next to a ball on hole 1 and measures the club.
-- Hand ~3 ft (3.05 studs) above the floor, ~0.9 studs in front of the eyes, handle (grip axis) aimed at the spot
-- behind the ball where the putter head should sit; controller X = the golfer's right, so the aim ray points
-- forward-up away from the body (a relaxed pistol-style hold).
local HAND_HEIGHT = 0.9144 / STUD
local function deg(a: Vector3, b: Vector3)
	return math.deg(math.acos(math.clamp(a.Unit:Dot(b.Unit), -1, 1)))
end
local function clubPose(legacy: boolean, view: string?)
	Config.VRClubLegacyAim = legacy == true
	VR.test.resetClubMount()
	if not GolfTest.vizBall then
		place(1, 0, 10, S)
		VR.warpToBall(Ball.ball.Position)
		GolfTest.vizBall = Ball.ball.Position
		task.wait(0.3)
	end
	-- park the off hand (and its wrist HUD) out of the shots
	debugFolder.LeftHand.Value = CFrame.new(-0.6, 3, 2)
	local ballPos = GolfTest.vizBall
	local half = VR.test.headSize / 2
	local plane = ballPos.Y - R
	local headCF = VR.test.getOrigin() * debugFolder.Head.Value
	local F = flat(headCF.LookVector).Unit -- golfer facing: toward the ball
	local Rt = F:Cross(Vector3.yAxis) -- golfer's right
	-- warpToBall faces you so the target is on your lead (left) side: the putter face points along -Rt
	local headTarget = ballPos - (-Rt) * (R + half.X + 0.06)
	headTarget = Vector3.new(headTarget.X, plane + half.Y + 0.01, headTarget.Z)
	local floorY = VR.test.getOrigin().Y
	local handPos = Vector3.new(headCF.X, floorY + HAND_HEIGHT, headCF.Z) + F * (flat(headTarget - headCF.Position):Dot(F) - 0.6)
	handPos = Vector3.new(handPos.X, handPos.Y, handPos.Z) + Rt:Dot(headTarget - handPos) * Rt
	-- the physical handle points at the head target: build the hand from the physical grip axis (not the code's
	-- mount, which differs in legacy mode)
	local gripDir = (headTarget - handPos).Unit
	local back = -gripDir
	local right = (Rt - back * Rt:Dot(back)).Unit
	local handleRot = CFrame.fromMatrix(Vector3.zero, right, back:Cross(right), back)
	local physicalRot = CFrame.Angles(math.rad(-90 - (Config.VRClubGripPitch or 35)), 0, 0)
	local handCF = CFrame.new(handPos) * handleRot * physicalRot:Inverse()
	poseFn = function()
		return handCF
	end
	workspace:SetAttribute("GolfTestClubDebug", true)
	if view then
		-- full views frame the whole stance (player head to ball, same for both mounts); "*_close" views centre
		-- on the controller. FOV 40.
		local close = string.find(view, "_close") ~= nil
		local center = close and handPos + gripDir * 0.3 or (headCF.Position + ballPos) / 2
		local dist = close and 2.6 or 11
		local camPos, up = nil, Vector3.yAxis
		local base = string.gsub(view, "_close", "")
		if base == "side" then
			-- down the line: from the target side, looking back along the target line (stance in profile)
			camPos = center - Rt * dist + Vector3.new(0, dist * 0.08, 0)
		elseif base == "front" then
			-- face-on: from beyond the ball looking back at the golfer, slightly raised to clear the course wall
			camPos = center + F * dist + Vector3.new(0, dist * 0.15, 0)
		elseif base == "top" then
			camPos, up = center + Vector3.new(0, dist, 0), F
		end
		workspace:SetAttribute("GolfTestFocus", center)
		workspace:SetAttribute("GolfTestCamPos", camPos)
		workspace:SetAttribute("GolfTestCamUp", up)
		workspace:SetAttribute("GolfTestCamera", "look")
	end
	task.wait(0.6)
	local head = headPart()
	local _, _, clubCF = VR.test.getClubMount()
	local handNow = VR.getState().hand
	local handleWorld = handNow:VectorToWorldSpace(physicalRot.LookVector)
	local buttWorld = handNow.Position + handleWorld * (Config.VRClubButtOffset or 0.25)
	local shaftVis = VR.test.putter.Shaft.CFrame.LookVector
	local res = {
		legacy = legacy == true,
		view = view,
		handHeightM = round((handNow.Position.Y - floorY) * STUD),
		handleLeanDeg = round(deg(handleWorld, -Vector3.yAxis), 1),
		shaftVsHandleDeg = round(deg(clubCF.LookVector, handleWorld), 1),
		shaftVisualVsHandleDeg = round(deg(shaftVis, handleWorld), 1),
		shaftStartGap = round((clubCF.Position - buttWorld).Magnitude, 3),
		shaftLeanDeg = round(deg(clubCF.LookVector, -Vector3.yAxis), 1),
		aimRayElevationDeg = round(math.deg(math.asin(math.clamp(handNow.LookVector.Y, -1, 1))), 1),
		aimRayForward = round(handNow.LookVector:Dot(F), 3),
		headBottomAbovePlane = round(head.Position.Y - half.Y - plane, 3),
		headToTarget = round((head.Position - headTarget).Magnitude, 3),
		headToBallFlat = round(flat(head.Position - ballPos).Magnitude, 3),
		clubLength = round(VR.test.clubLength(), 3),
		headPos = vec(head.Position),
		handPos = vec(handNow.Position),
	}
	event("clubpose", res)
	return res
end

scenario({
	name = "clubviz",
	desc = "VR club mount: putting-grip hand pose, shaft along the handle out of its bottom (vs legacy aim-ray mount)",
	vr = true,
	seconds = 6,
	run = function()
		local skip = vrRequired()
		if skip then
			return skip
		end
		GolfTest.vizBall = nil
		local out = { legacy = clubPose(true, "side"), grip = clubPose(false, "side") }
		-- A-button re-fit from the grip pose: the shaft should go straight down from the handle bottom, with the
		-- head on the ball's plane
		local lengthBefore = VR.test.clubLength()
		debugFolder.Button:Fire(Enum.KeyCode.ButtonA, false)
		debugFolder.Button:Fire(Enum.KeyCode.ButtonA, true)
		task.wait(0.4)
		local butt, _, clubCF = VR.test.getClubMount()
		local hand = VR.getState().hand
		local head = headPart()
		out.fit = {
			shaftLeanDeg = round(deg(clubCF.LookVector, -Vector3.yAxis), 2),
			shaftStartGap = round((clubCF.Position - hand:PointToWorldSpace(butt)).Magnitude, 4),
			headBottomAbovePlane = round(head.Position.Y - VR.test.headSize.Y / 2 - (GolfTest.vizBall.Y - R), 3),
			clubLength = round(VR.test.clubLength(), 3),
			clubLengthBefore = round(lengthBefore, 3),
		}
		out.fit.ok = out.fit.shaftLeanDeg < 1 and out.fit.shaftStartGap < 0.01 and math.abs(out.fit.headBottomAbovePlane - 0.01) < 0.05
		event("fit", out.fit)
		Config.VRClubLegacyAim = false
		VR.test.resetClubMount()
		workspace:SetAttribute("GolfTestClubDebug", false)
		workspace:SetAttribute("GolfTestCamera", "")
		GolfTest.vizBall = nil
		local g = out.grip
		-- shaft continues the handle (< 2 deg), starts at its bottom (< 1 cm), head on the ball's plane (3 mm
		-- clearance, < 1.5 cm error) right behind the ball (within ~3 cm of the intended spot)
		out.ok = g.shaftVsHandleDeg < 2 and g.shaftStartGap < 0.03 and math.abs(g.headBottomAbovePlane - 0.01) < 0.05
			and g.headToTarget < 0.1 and out.fit.ok
		return out
	end,
})

local byName = {}
for _, s in SCENARIOS do
	byName[s.name] = s
end

------------------------------------------------------------------------ runner API
local function runScenario(name, cam)
	local sc = byName[name]
	table.clear(lines)
	run = { running = true, name = name, cam = cam or "", t0 = os.clock(), err = nil }
	lastSample = -1
	prevVel, prevPos, pending = nil, nil, nil
	workspace:SetAttribute("GolfTestCamera", cam or "")
	record({
		type = "header",
		scenario = name,
		cam = cam or "",
		simulateVR = simVR == true,
		config = {
			BallRadius = Config.BallRadius,
			RollDecel = Config.RollDecel,
			RollDrag = Config.RollDrag,
			SpinKeep = Config.SpinKeep,
			SlideFriction = Config.SlideFriction,
			CupCaptureSpeed = Config.CupCaptureSpeed,
			StopSpeed = Config.StopSpeed,
			VRHitMultiplier = Config.VRHitMultiplier,
			VRClubLegacyAim = Config.VRClubLegacyAim,
			VRClubGripPitch = Config.VRClubGripPitch,
			VRClubGripYaw = Config.VRClubGripYaw,
			VRClubGripRoll = Config.VRClubGripRoll,
			VRClubButtOffset = Config.VRClubButtOffset,
			VRClubAngle = Config.VRClubAngle,
			VRClubTipOffset = Config.VRClubTipOffset,
			Gravity = workspace.Gravity,
		},
		physics = {
			ball = (function()
				local p = Ball.ball.CustomPhysicalProperties
				return p and { friction = p.Friction, elasticity = p.Elasticity, frictionWeight = p.FrictionWeight, elasticityWeight = p.ElasticityWeight }
			end)(),
			wall = physicsOf("Wall"),
			bumper = physicsOf("Bumper"),
			felt = physicsOf("Felt"),
		},
	})
	print("GOLFTEST|" .. name .. "|start|cam=" .. (cam or ""))
	parkHand()
	local ok, res = xpcall(sc.run, debug.traceback)
	parkHand()
	if not ok then
		run.err = tostring(res)
		res = { error = run.err }
		warn("GOLFTEST|" .. name .. "|error|" .. run.err)
	end
	res.scenario = name
	res.cam = cam or ""
	res.seconds = round(now(), 2)
	results[name] = res
	record({ type = "result", result = res })
	print("GOLFTEST|" .. name .. "|done|" .. res.seconds .. "s")
	run.running = false
end

local function api(cmd, a, b)
	if cmd == "list" then
		local out = {}
		for _, s in SCENARIOS do
			table.insert(out, { name = s.name, desc = s.desc, vr = s.vr == true, seconds = s.seconds })
		end
		return HttpService:JSONEncode(out)
	elseif cmd == "start" then
		if run.running then
			return "error: busy with " .. run.name
		end
		if not byName[a] then
			return "error: unknown scenario " .. tostring(a)
		end
		run.running = true
		task.spawn(runScenario, a, b)
		return "started"
	elseif cmd == "status" then
		return HttpService:JSONEncode({
			running = run.running,
			name = run.name,
			cam = run.cam,
			elapsed = run.running and round(now(), 2) or nil,
			lines = #lines,
			error = run.err,
			simulateVR = simVR == true,
			ballState = Ball.state,
		})
	elseif cmd == "log" then
		local from = a or 1
		local budget = b or 60000
		local out, used, i = {}, 0, from
		while i <= #lines and used + #lines[i] + 1 <= budget do
			table.insert(out, lines[i])
			used += #lines[i] + 1
			i += 1
		end
		return tostring(i) .. "\n" .. table.concat(out, "\n")
	elseif cmd == "result" then
		return HttpService:JSONEncode(results[a] or {})
	elseif cmd == "clubpose" then
		if not (simVR and VR and VR.test) then
			return "error: needs SimulateVR"
		end
		local ok, res = pcall(clubPose, a == true, b)
		return ok and HttpService:JSONEncode(res) or ("error: " .. tostring(res))
	elseif cmd == "camera" then
		workspace:SetAttribute("GolfTestCamera", a or "")
		return "ok"
	end
	return "error: unknown command " .. tostring(cmd)
end

------------------------------------------------------------------------ recording cameras
local followDir = Vector3.new(0, 0, 1)
local followPos = nil

local function updateCamera(dt)
	local mode = workspace:GetAttribute("GolfTestCamera")
	if mode == nil or mode == "" then
		followPos = nil
		return
	end
	local camera = workspace.CurrentCamera
	camera.CameraType = Enum.CameraType.Scriptable
	local focus = workspace:GetAttribute("GolfTestFocus")
	local size = workspace:GetAttribute("GolfTestFrameSize") or 10
	local view = workspace:GetAttribute("GolfTestViewDir") or Vector3.new(0, 0, 1)
	view = flat(view).Magnitude > 1e-3 and flat(view).Unit or Vector3.new(0, 0, 1)
	local b = Ball.ball
	if typeof(focus) ~= "Vector3" then
		focus = b and b.Position or Vector3.zero
	end
	if mode == "look" then
		-- explicit camera: GolfTestCamPos looking at GolfTestFocus (screenshots)
		camera.FieldOfView = workspace:GetAttribute("GolfTestFOV") or 40
		local up = workspace:GetAttribute("GolfTestCamUp") or Vector3.yAxis
		camera.CFrame = CFrame.lookAt(workspace:GetAttribute("GolfTestCamPos") or focus + Vector3.new(0, 0, 8), focus, up)
	elseif mode == "fixed" then
		camera.FieldOfView = 50
		local pos = focus - view * size * 0.75 + Vector3.new(0, size * 0.6, 0)
		camera.CFrame = CFrame.lookAt(pos, focus)
	elseif mode == "topdown" then
		camera.FieldOfView = 50
		local h = (size / 2) / math.tan(math.rad(25)) * 1.1
		camera.CFrame = CFrame.lookAt(focus + Vector3.new(0, h, 0), focus, view)
	elseif mode == "follow" and b then
		camera.FieldOfView = 60
		local v = flat(b.AssemblyLinearVelocity)
		if v.Magnitude > 0.5 then
			followDir = followDir:Lerp(v.Unit, 1 - math.exp(-dt * 4))
			if followDir.Magnitude > 1e-3 then
				followDir = followDir.Unit
			end
		end
		local want = b.Position - followDir * 4 + Vector3.new(0, 2.2, 0)
		followPos = followPos and followPos:Lerp(want, 1 - math.exp(-dt * 6)) or want
		camera.CFrame = CFrame.lookAt(followPos, b.Position + followDir * 1.5)
	end
end

------------------------------------------------------------------------ start
function GolfTest.start(ballController, _hud, vrModule, simulate)
	Ball = ballController
	VR = vrModule
	simVR = simulate
	debugFolder = simulate and ReplicatedStorage:FindFirstChild("VRDebug")
	GolfTest.hitCount = 0
	testRemote = Golf:WaitForChild("GolfTestRemote", 15)
	if not testRemote then
		warn("GOLFTEST|client|no GolfTestRemote (server test mode off?)")
		return
	end

	Ball.Stroked.Event:Connect(function(velocity, source)
		GolfTest.hitCount += 1
		GolfTest.lastHitSource = source
		GolfTest.lastHitVelocity = velocity
		if run.running then
			event("hit", { source = source, velocity = vec(velocity), speed = round(velocity.Magnitude), pos = vec(Ball.ball.Position) })
		end
	end)
	Ball.StateChanged.Event:Connect(function(s)
		if s == "ready" and shot and not outcome then
			outcome = "rest"
			if run.running then
				event("rest", { pos = vec(Ball.ball.Position) })
			end
		end
	end)
	Ball.Placed.Event:Connect(function(_, reason)
		placedCount += 1
		if reason == "oob" and shot and not outcome then
			outcome = "oob"
		end
	end)
	Remotes.HoleComplete.OnClientEvent:Connect(function(who, holeNum, strokes, _, maxed)
		if who == player and shot and not outcome and not maxed then
			outcome = "cup"
			if run.running then
				event("cup", { hole = holeNum, strokes = strokes })
			end
		end
	end)
	Remotes.Notice.OnClientEvent:Connect(function(text)
		if string.find(text, "Out of bounds") and shot and not outcome then
			outcome = "oob"
			if run.running then
				event("oob", { pos = vec(Ball.ball.Position) })
			end
		end
	end)

	RunService.PostSimulation:Connect(onPostSimulation)
	RunService:BindToRenderStep("GolfTestHand", Enum.RenderPriority.Camera.Value - 50, driveHand)
	RunService:BindToRenderStep("GolfTestCamera", Enum.RenderPriority.Camera.Value + 10, updateCamera)
	RunService:BindToRenderStep("GolfTestClubDebug", Enum.RenderPriority.Camera.Value + 11, updateClubDebug)
	parkHand()

	local fn = Instance.new("BindableFunction")
	fn.Name = "GolfTestAPI"
	fn.OnInvoke = api
	fn.Parent = ReplicatedStorage
	print("GOLFTEST|client|ready|simulateVR=" .. tostring(simulate == true))
end

return GolfTest
