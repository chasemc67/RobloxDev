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
	local name = p.Name
	if p:GetAttribute("WallId") then
		name ..= ":" .. p:GetAttribute("WallId")
	elseif p.Name == "Blocker" and p.Parent then
		name ..= ":" .. tostring(p.Parent:GetAttribute("MoverId"))
	end
	return ((anc and anc ~= workspace) and anc.Name .. "/" or "") .. name
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
	if shot and not shot.fellFlagged then
		local h = Ball.getHole()
		local minY = h and h:GetAttribute("FeltMinY")
		if minY and p.Y < minY - 3 then
			shot.fellFlagged = true
			event("fell", { pos = vec(p) })
		end
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

------------------------------------------------------------------------ course helpers (Lantern Grove)
-- Spec coordinates are per-hole local (studs, Y up, play toward -Z). CourseBuilder stores each hole's frame
-- origin/yaw as attributes, so helpers can take spec coordinates straight from holes.json / hNN-notes.md.
local G = Config.BallRadius
local VMAX = 19.78 -- spec max putt (studs/s): a full putt rolls 60 studs on flat felt
local CollectionService = game:GetService("CollectionService")

local function hole(n)
	return workspace.Course:FindFirstChild("Hole" .. n)
end

local function holeCF(n)
	local h = hole(n)
	return CFrame.new(h:GetAttribute("HoleOrigin")) * CFrame.Angles(0, math.rad(h:GetAttribute("HoleYaw") or 0), 0)
end

local function W(n, x, y, z)
	return holeCF(n):PointToWorldSpace(Vector3.new(x, y or 0, z))
end

local function WD(n, dx, dz)
	return holeCF(n):VectorToWorldSpace(Vector3.new(dx, 0, dz))
end

local function toLocal(n, p: Vector3)
	return holeCF(n):PointToObjectSpace(p)
end

local feltParams = RaycastParams.new()
feltParams.FilterType = Enum.RaycastFilterType.Include
local function refreshFelt()
	feltParams.FilterDescendantsInstances = CollectionService:GetTagged("GolfSurface")
end

-- Felt under a world point (searching down from `fromY`, default 3 studs above it): hit or nil.
local function feltHit(p: Vector3, fromY: number?)
	local top = fromY or (p.Y + 3)
	return workspace:Raycast(Vector3.new(p.X, top, p.Z), Vector3.new(0, -(top - p.Y) - 6, 0), feltParams)
end

local function zoneOf(p: Vector3)
	local hit = workspace:Raycast(p + Vector3.new(0, 0.05, 0), Vector3.new(0, -(R + 0.6), 0), feltParams)
	return hit and hit.Instance:GetAttribute("Zone"), hit and hit.Instance:GetAttribute("PieceId")
end

local function ballPlaneY()
	return Ball.ball.Position.Y - R
end

-- Places the ball at spec-local (x, z) on hole n, on the felt (the highest piece at or below spec height y + 0.5).
local function placeL(n, x, z, y)
	local wp = W(n, x, y or 0, z)
	local hit = feltHit(wp, wp.Y + 0.6)
	if not hit then
		error(string.format("no felt under hole %d (%.2f, %.2f)", n, x, z))
	end
	place(n, hit.Position.X, hit.Position.Z, hit.Position.Y)
	return hit.Position
end

-- Flat-felt rolling model inverse: launch speed (studs/s) that rolls `d` studs.
local function speedFor(d: number)
	local lo, hi = 0, 60
	for _ = 1, 40 do
		local mid = (lo + hi) / 2
		if idealRollout(mid) < d then
			lo = mid
		else
			hi = mid
		end
	end
	return (lo + hi) / 2
end

-- aim = atan2(dz, dx) in degrees, in the hole's local frame (hNN-notes.md convention)
local function aimDir(n, deg)
	local a = math.rad(deg)
	return WD(n, math.cos(a), math.sin(a))
end

local function obstaclesOf(n)
	local out = {}
	for _, d in hole(n).Geometry:GetChildren() do
		if d:IsA("BasePart") and d.CanCollide and (d.Name == "Wall" or d.Name == "Bumper") then
			table.insert(out, d)
		end
	end
	return out
end

-- Line of sight for a rolling ball from a to b (world): follows the felt, blocked by walls/bumpers and steps up.
local losParams = RaycastParams.new()
losParams.FilterType = Enum.RaycastFilterType.Include
local function los(n, a: Vector3, b: Vector3)
	losParams.FilterDescendantsInstances = obstaclesOf(n)
	local d = flat(b - a).Magnitude
	local steps = math.max(1, math.ceil(d / 0.4))
	local prev = a
	local prevH = a.Y - R
	for i = 1, steps do
		local p = a:Lerp(b, i / steps)
		local hit = feltHit(Vector3.new(p.X, prevH, p.Z), prevH + 0.6)
		if not hit then
			return false
		end
		local h = hit.Position.Y
		if h > prevH + 0.25 then
			return false
		end
		local from = Vector3.new(prev.X, prevH + R + 0.03, prev.Z)
		local to = Vector3.new(p.X, h + R + 0.03, p.Z)
		if (to - from).Magnitude > 1e-3 and workspace:Spherecast(from, R * 0.9, to - from, losParams) then
			return false
		end
		prev, prevH = Vector3.new(p.X, h + R, p.Z), h
	end
	return true
end

------------------------------------------------------------------------ moving parts: phase + client lag
local function moversOf(n)
	local out = {}
	local f = hole(n):FindFirstChild("Movers")
	for _, m in f and f:GetChildren() or {} do
		if CollectionService:HasTag(m, "GolfMover") then
			table.insert(out, m)
		end
	end
	return out
end

-- spec value of a mover at server time t (same as GolfServer.Movers.value)
local function moverValue(m, t)
	local sp = m:GetAttribute("Speed")
	local phase = m:GetAttribute("Phase") or 0
	local per = m:GetAttribute("Period")
	if not m:GetAttribute("HasRange") then
		return phase + sp * (t % per)
	end
	local a, b = m:GetAttribute("RangeMin"), m:GetAttribute("RangeMax")
	local span = b - a
	local u = (phase - a) + math.abs(sp) * (t % per)
	u = u - 2 * span * math.floor(u / (2 * span))
	return u < span and a + u or b - (u - span)
end

-- the value this client currently SEES (replicated physics), from the first blocker's pose
local function moverObserved(m)
	local blk = m:FindFirstChild("Blocker")
	local rest = blk and blk:GetAttribute("RestCFrame")
	if not rest then
		return nil
	end
	local axis = m:GetAttribute("AxisWorld")
	if m:GetAttribute("Type") == "slide" then
		return (blk.Position - rest.Position):Dot(axis)
	end
	-- rotation of the blocker's frame about the axis, relative to its rest frame
	local rel = blk.CFrame.Rotation * rest.Rotation:Inverse()
	local ax, ang = rel:ToAxisAngle()
	if ax:Dot(axis) < 0 then
		ang = -ang
	end
	return math.deg(ang)
end

-- How far (s) behind server time this client sees the mover: the lag L minimising |value(now - L) - observed|.
local function moverLag(m)
	local best, bestErr = 0, math.huge
	local obs = moverObserved(m)
	if not obs then
		return 0
	end
	local now = workspace:GetServerTimeNow()
	local rot = m:GetAttribute("Type") == "rotate"
	for L = 0, 0.6, 0.005 do
		local e = moverValue(m, now - L) - obs
		if rot then
			e = (e + 180) % 360 - 180
		end
		if math.abs(e) < bestErr then
			best, bestErr = L, math.abs(e)
		end
	end
	return best, bestErr
end

local lagCache = {}
local function holeLag(n)
	if lagCache[n] then
		return lagCache[n]
	end
	local ms = moversOf(n)
	if #ms == 0 then
		return 0
	end
	local sum, k = 0, 0
	for _ = 1, 5 do
		for _, m in ms do
			sum += moverLag(m)
			k += 1
		end
		task.wait(0.05)
	end
	lagCache[n] = sum / k
	return lagCache[n]
end

-- Wait until the hole's moving parts (as this client sees them) are at spec time `phase` (mod `period`).
local function waitPhase(n, phase, period)
	local ms = moversOf(n)
	if #ms == 0 or not phase then
		return nil
	end
	period = period or hole(n):GetAttribute("MoverPeriod")
	local lag = holeLag(n)
	local t0 = os.clock()
	while os.clock() - t0 < period + 1 do
		local seen = (workspace:GetServerTimeNow() - lag) % period
		local d = (seen - phase) % period
		if d < 0.02 or d > period - 0.005 then
			break
		end
		RunService.Heartbeat:Wait()
	end
	return round((workspace:GetServerTimeNow() - lag) % period, 3)
end

------------------------------------------------------------------------ issue detection (escape / stuck)
-- Every scripted shot also records: teleports, unstick nudges, off-felt rests, forced rests and (via the
-- server's LastOOB attribute) whether an out-of-bounds was a designed hazard or an escape.
local shotFlags = nil -- per-shot list of flags, set by shoot()
local issues = {} -- per-scenario list of {kind, hole, label, pos, detail}

local function flag(kind, data)
	data = data or {}
	data.kind = kind
	data.label = shotLabel
	data.hole = Ball.holeIndex
	if shotFlags then
		table.insert(shotFlags, data)
	end
	if kind ~= "teleport" and kind ~= "hazard" then
		table.insert(issues, data)
	end
	event("flag", data)
end

-- shoot() in studs/s along a world direction, plus phase timing and flag collection
local function shootS(label: string, dir: Vector3, studsPerSec: number, opts)
	opts = opts or {}
	shotFlags = {}
	local before = Ball.ball:GetAttribute("LastOOB")
	Ball.ball:SetAttribute("LastOOB", nil)
	local r = shoot(label, dir, studsPerSec * STUD, opts)
	r.speed = round(studsPerSec)
	r.flags = shotFlags
	shotFlags = nil
	local last = Ball.ball:GetAttribute("LastOOB")
	if r.outcome == "oob" then
		r.outcome = (last and string.sub(last, 1, 7) == "hazard:") and "hazard" or "escape"
		r.oob = last or "unknown"
		if r.outcome == "escape" then
			table.insert(issues, { kind = "escape", label = label, hole = Ball.holeIndex, pos = r.finish, detail = last })
			event("flag", { kind = "escape", label = label, pos = r.finish })
		end
	elseif r.outcome == "timeout" then
		table.insert(issues, { kind = "stuck-timeout", label = label, hole = Ball.holeIndex, pos = r.finish })
		event("flag", { kind = "stuck-timeout", label = label, pos = r.finish })
	end
	local _ = before
	local z, piece = zoneOf(Ball.ball.Position)
	r.zone, r.piece = z, piece
	-- after an OOB the server re-places the ball at the stroke start after 1 s: wait for it
	if r.outcome == "hazard" or r.outcome == "escape" then
		local t0 = os.clock()
		while (Ball.state ~= "ready") and os.clock() - t0 < 5 do
			task.wait()
		end
		task.wait(0.2)
	end
	return r
end

------------------------------------------------------------------------ AI golfer (intended lines)
local specCache = {}
local function spec(n)
	if not specCache[n] then
		local s = testRemote:InvokeServer("spec", { hole = n })
		specCache[n] = HttpService:JSONDecode(s)
	end
	return specCache[n]
end

local function inList(list, v)
	for _, x in list or {} do
		if x == v then
			return true
		end
	end
	return false
end

-- Pick the target like the designer's sim golfer: the cup when allowed from this zone and in sight, else the
-- furthest waypoint (last -> first) for this skill whose `from` includes the current zone and is in sight.
local function chooseTarget(n, skill, zone, pos)
	local sp = spec(n)
	local cupL = sp.cup.position
	local cupW = W(n, cupL[1], cupL[2], cupL[3])
	local cupOk = sp.cup_from == nil or inList(sp.cup_from, zone)
	if cupOk and los(n, pos, cupW + Vector3.new(0, R, 0)) then
		return cupW, 1.0, 1, "cup"
	end
	local wps = {}
	for _, key in { skill, "all" } do
		for _, w in (sp.ai_waypoints or {})[key] or {} do
			table.insert(wps, w)
		end
	end
	for i = #wps, 1, -1 do
		local w = wps[i]
		if inList(w.from, zone) then
			local p = W(n, w.pos[1], w.pos[2], w.pos[3])
			local hit = feltHit(p, p.Y + 0.6)
			local tp = hit and hit.Position + Vector3.new(0, R, 0) or p
			if los(n, pos, tp) or i == 1 then
				return tp, w.carry or 0, w.power_scale or 1, w.id
			end
		end
	end
	return cupW, 1.0, 1, cupOk and "cup-blind" or "cup-fallback"
end

-- Plays the hole from the tee with the intended (spec waypoint) line for `skill` ("good" = aggressive/risk line,
-- "average" = safe line). Returns strokes, holed, per-stroke log.
local function playHole(n, skill, opts)
	opts = opts or {}
	local sp = spec(n)
	local t = sp.tee.position
	placeL(n, t[1], t[3], t[2])
	local strokes, shots = 0, {}
	local holed = false
	while strokes < (opts.cap or Config.MaxStrokes) do
		local pos = Ball.ball.Position
		local zone = zoneOf(pos) or "?"
		local target, carry, pscale, tid = chooseTarget(n, skill, zone, pos)
		local d = flat(target - pos).Magnitude
		local v = speedFor(d + carry) * pscale
		local climb = target.Y - pos.Y
		if climb > 0.05 then
			v += math.sqrt(2 * workspace.Gravity * climb)
		end
		v = math.min(v, VMAX)
		local phase
		if opts.phases and opts.phases[strokes + 1] then
			phase = waitPhase(n, opts.phases[strokes + 1])
		end
		local r = shootS(string.format("h%d-%s-s%d", n, skill, strokes + 1), target - pos, v, { cup = hole(n).Cup, timeout = 22 })
		strokes += 1
		r.fromZone, r.target, r.targetId, r.phase = zone, vec(target), tid, phase
		r.contacts = nil
		table.insert(shots, r)
		if r.outcome == "hazard" or r.outcome == "escape" then
			strokes += Config.PenaltyStrokes
		elseif r.outcome == "cup" then
			holed = true
			break
		end
	end
	return { skill = skill, strokes = strokes, holed = holed, par = sp.par, shots = shots }
end

------------------------------------------------------------------------ per-hole scenario parts
local function opts()
	local raw = workspace:GetAttribute("GolfTestOpts")
	local ok, o = pcall(HttpService.JSONDecode, HttpService, raw or "{}")
	return ok and o or {}
end

local function frameHole(n)
	local b = hole(n).Bounds
	local size = math.max(b.Size.X, b.Size.Z)
	setFrame(Vector3.new(b.Position.X, hole(n):GetAttribute("FeltMaxY"), b.Position.Z), size * 0.9, Vector3.new(0, 0, -1))
end

-- Hole-in-one attempt: the designer's ace line from hNN-notes.md (aim, speed, mover phase) first. If it misses
-- (the in-engine bounces/skid differ a little from the designer's sim), search like a golfer would:
--   1. a coarse aim scan around the spec line (+-1, +-2 ... +-8 deg, nearest first) at the spec speed and 88% of it;
--   2. Newton/Broyden refinement from the closest finish (miss vector in the hole frame vs aim and speed), with a
--      trust region that halves after a worse shot.
-- Stops at the first ace or after `tries` shots.
local function hioAttempt(n, tries)
	local sp = spec(n)
	local line = sp.hio
	if not line then
		return { skipped = "no HIO line in the notes" }
	end
	tries = tries or 30
	local t = sp.tee.position
	local cupL = Vector3.new(sp.cup.position[1], 0, sp.cup.position[3])
	local attempts = {}
	local ace
	local best
	local function try(aim, v, stage)
		v = math.clamp(v, 4, VMAX)
		placeL(n, t[1], t[3], t[2])
		local phase = line.phase and waitPhase(n, line.phase) or nil
		local r = shootS(string.format("h%d-hio-%d", n, #attempts + 1), aimDir(n, aim), v, { cup = hole(n).Cup, timeout = 22 })
		local fl = toLocal(n, Vector3.new(r.finish[1], r.finish[2], r.finish[3]))
		local miss = Vector2.new(fl.X - cupL.X, fl.Z - cupL.Z)
		r.aimDeg, r.phase, r.contacts, r.stage = round(aim, 2), phase, nil, stage
		r.missStuds = round(miss.Magnitude, 2)
		r.miss = { round(miss.X, 2), round(miss.Y, 2) }
		table.insert(attempts, r)
		local valid = r.outcome == "rest" or r.outcome == "cup"
		if r.outcome == "cup" then
			ace = r
		end
		if valid and (not best or miss.Magnitude < best.m.Magnitude) then
			best = { a = aim, v = v, m = miss }
		end
		return miss, valid
	end
	local function done()
		return ace ~= nil or #attempts >= tries
	end
	local a0, v0 = line.aim_deg, math.min(line.speed, VMAX)
	try(a0, v0, "spec")
	-- 0. candidate lines from tools/engine_sim.py (engine-calibrated sim), if the runner passed any
	local cands = (opts().hioLines or {})[tostring(n)] or {}
	for _, c in cands do
		if done() then
			break
		end
		if c[3] and line.phase ~= nil then
			line = table.clone(line)
			line.phase = c[3]
		end
		try(c[1], c[2], "engine-sim")
		if best and best.m.Magnitude < 2 then
			break
		end
	end
	-- 1. coarse scan
	local scan = {}
	for k = 1, 8 do
		table.insert(scan, { a0 + k, v0 })
		table.insert(scan, { a0 - k, v0 })
	end
	for k = 0, 8 do
		table.insert(scan, { a0 + k, v0 * 0.88 })
		if k > 0 then
			table.insert(scan, { a0 - k, v0 * 0.88 })
		end
	end
	local scanBudget = math.max(0, tries - 8 - #attempts)
	for i, c in scan do
		if done() or i > scanBudget or (best and best.m.Magnitude < 2) then
			break
		end
		try(c[1], c[2], "scan")
		-- once something lands within 2 studs, go refine it
		if best and best.m.Magnitude < 2 then
			break
		end
	end
	-- 2. refine from the best finish
	if not done() and best then
		local da, dv = 0.4, best.v >= VMAX - 0.05 and -0.4 or 0.4
		local base = best
		local ma = try(base.a + da, base.v, "refine")
		local mv = (not done()) and try(base.a, base.v + dv, "refine") or base.m
		local J = { (ma - base.m) / da, (mv - base.m) / dv }
		local rA, rV = 2, 2
		while not done() do
			local j1, j2 = J[1], J[2]
			local det = j1.X * j2.Y - j2.X * j1.Y
			local stepA, stepV
			if math.abs(det) < 1e-4 then
				stepA, stepV = (#attempts % 2 == 0) and rA / 2 or -rA / 2, 0
			else
				stepA = (-best.m.X * j2.Y + best.m.Y * j2.X) / det
				stepV = (-j1.X * best.m.Y + j1.Y * best.m.X) / det
			end
			stepA, stepV = math.clamp(stepA, -rA, rA), math.clamp(stepV, -rV, rV)
			local from = best
			local na, nv = from.a + stepA, math.clamp(from.v + stepV, 4, VMAX)
			local m, valid = try(na, nv, "refine")
			if valid then
				local s1, s2 = na - from.a, nv - from.v
				local Js = j1 * s1 + j2 * s2
				local ss = s1 * s1 + s2 * s2
				if ss > 1e-6 then
					local corr = ((m - from.m) - Js) / ss
					J = { j1 + corr * s1, j2 + corr * s2 }
				end
			end
			if not valid or m.Magnitude >= from.m.Magnitude then
				rA, rV = math.max(rA / 2, 0.05), math.max(rV / 2, 0.05)
			end
		end
	end
	return {
		line = line,
		attempts = attempts,
		ace = ace ~= nil,
		aceAim = ace and ace.aimDeg,
		aceSpeed = ace and ace.speed,
		bestMiss = best and round(best.m.Magnitude, 2),
		bestAim = best and round(best.a, 2),
		bestSpeed = best and round(best.v, 2),
	}
end

-- Bank / rail shots (spec-local start, aim point, speed): logs the first contacts (restitution, angles).
local BANKS = {
	[1] = { { "deflector-45", { 0, -26.5 }, { 0, -33 }, 10 }, { "lane-rail-30", { -2, -6 }, { 3.5, -15 }, 9 } },
	[2] = { { "stump-headon", { 0, -14 }, { 0, -19 }, 8 }, { "lane-rail-40", { 2, -4 }, { -4, -11 }, 9 } },
	[3] = { { "bank1-ride", { 0, -3 }, { -1, -11.5 }, 15 }, { "bank2-ride", { 6, -12 }, { 18, -12 }, 12 } },
	[4] = { { "plaza-rail-45", { 0, -15 }, { -7, -22 }, 9 }, { "ramp-rail", { 3, -28.5 }, { 5, -33 }, 9 } },
	[5] = { { "shore-rail-45", { -6, -4 }, { -15, -13 }, 10 }, { "covered-rail", { -10.5, -16 }, { -7.75, -21 }, 8 } },
	[6] = { { "board1", { 0, -2 }, { 0, -8.5 }, 12 }, { "board2", { 9, -8.5 }, { 15, -8 }, 12 } },
	[7] = { { "t2-rail-45", { 4, -16 }, { 10, -22 }, 8 }, { "t3-rail", { -4, -36 }, { -8.25, -38 }, 7 } },
	[8] = { { "bank1-ride", { -8, -11.5 }, { -17, -11.5 }, 12 }, { "bank2-ride", { -16.5, -42 }, { -16.5, -49 }, 10 } },
	[9] = { { "bank1-ride", { 0, -18 }, { -1, -25 }, 12 }, { "root-deflector", { 15, -25.5 }, { 22, -26.5 }, 10 } },
}

local function bankShots(n)
	local out = {}
	for _, b in BANKS[n] or {} do
		local p = placeL(n, b[2][1], b[2][2], 3)
		local tgt = W(n, b[3][1], 0, b[3][2])
		local r = shootS(string.format("h%d-bank-%s", n, b[1]), tgt - p, b[4], { timeout = 14 })
		local c = r.contacts and r.contacts[1]
		r.bank = b[1]
		r.firstContact = c and {
			part = c.part,
			restitution = c.restitution,
			tangentialRetention = c.tangentialRetention,
			angleIn = c.angleIn,
			angleOut = c.angleOut,
			speedIn = c.speedIn,
			speedOut = c.speedOut,
		}
		r.nContacts = r.contacts and #r.contacts or 0
		r.contacts = nil
		table.insert(out, r)
	end
	return out
end

-- Moving-part timing sweep: the intended first shot (tee -> first waypoint) at N evenly spaced phases of each
-- mover's own cycle. Records whether the ball touched a blocker and where it ended up.
local function timingSweep(n, count)
	local ms = moversOf(n)
	if #ms == 0 then
		return nil
	end
	local sp = spec(n)
	local t = sp.tee.position
	local out = {}
	for _, m in ms do
		local per = m:GetAttribute("Period")
		local rows = {}
		for k = 0, count - 1 do
			local ph = per * k / count
			local tee = placeL(n, t[1], t[3], t[2])
			local pos = Ball.ball.Position
			local line = sp.hio
			local dir, v
			if line then
				dir, v = aimDir(n, line.aim_deg), line.speed
			else
				local target = chooseTarget(n, "good", zoneOf(pos) or "?", pos)
				dir, v = target - pos, VMAX * 0.8
			end
			-- wait for this mover's phase (as seen on this client)
			local lag = holeLag(n)
			local t0 = os.clock()
			while os.clock() - t0 < per + 1 do
				local seen = (workspace:GetServerTimeNow() - lag) % per
				local d = (seen - ph) % per
				if d < 0.02 or d > per - 0.005 then
					break
				end
				RunService.Heartbeat:Wait()
			end
			local r = shootS(string.format("h%d-sweep-%s-%d", n, m:GetAttribute("MoverId"), k), dir, v, { cup = hole(n).Cup, timeout = 22 })
			local blocked = false
			for _, c in r.contacts or {} do
				if string.find(c.part or "", "Blocker") then
					blocked = true
				end
			end
			table.insert(rows, { phase = round(ph, 2), outcome = r.outcome, zone = r.zone, blocked = blocked, finish = r.finish, flags = r.flags })
			local _ = tee
		end
		table.insert(out, { mover = m:GetAttribute("MoverId"), period = per, rows = rows })
	end
	return out
end

-- Fuzz: random shots (any direction, 20-100% power) from the tee and from random spots on the felt.
-- Counts escapes (OOB outside any hazard), stuck balls (timeouts, off-felt rests, forced rests) and nudges.
local function fuzz(n, count, seed)
	local rng = Random.new(seed or n * 7919)
	local sp = spec(n)
	local res = { shots = 0, hazards = 0, escapes = 0, stuck = 0, nudges = 0, holed = 0, list = {} }
	for i = 1, count do
		local start
		if i % 3 == 1 then
			local t = sp.tee.position
			start = { t[1], t[3], t[2] }
		else
			local f = sp.felt[rng:NextInteger(1, #sp.felt)]
			if f.overlay then
				f = sp.felt[1]
			end
			local hx, hz = f.size[1] / 2 - 0.4, f.size[2] / 2 - 0.4
			local lx, lz = rng:NextNumber(-hx, hx), rng:NextNumber(-hz, hz)
			local yaw = math.rad(f.yaw or 0)
			start = { f.center[1] + lx * math.cos(yaw) + lz * math.sin(yaw), f.center[3] - lx * math.sin(yaw) + lz * math.cos(yaw), f.center[2] }
		end
		local ok = pcall(placeL, n, start[1], start[2], start[3] + 0.3)
		if ok then
			local ang = rng:NextNumber(0, 360)
			local v = rng:NextNumber(0.2, 1.0) * VMAX
			local r = shootS(string.format("h%d-fuzz-%d", n, i), aimDir(n, ang), v, { cup = hole(n).Cup, timeout = 26 })
			res.shots += 1
			if r.outcome == "hazard" then
				res.hazards += 1
			elseif r.outcome == "escape" then
				res.escapes += 1
			elseif r.outcome == "timeout" then
				res.stuck += 1
			elseif r.outcome == "cup" then
				res.holed += 1
			end
			for _, f in r.flags or {} do
				if f.kind == "unstuck" then
					res.nudges += 1
				elseif f.kind == "offsurface" or f.kind == "forcedrest" then
					res.stuck += 1
				end
			end
			if r.outcome == "escape" or r.outcome == "timeout" or #(r.flags or {}) > 0 then
				table.insert(res.list, { label = r.label, start = start, aim = round(ang, 1), speed = round(v), outcome = r.outcome, finish = r.finish, flags = r.flags })
			end
		end
	end
	return res
end

local function holeScenario(n)
	return function()
		refreshFelt()
		table.clear(issues)
		lagCache[n] = nil
		local o = opts()
		local parts = o.parts or "routes,hio,banks,sweep,fuzz"
		local out = { hole = n, name = hole(n):GetAttribute("HoleName"), par = hole(n):GetAttribute("Par") }
		frameHole(n)
		if #moversOf(n) > 0 then
			out.clientLag = round(holeLag(n), 3)
		end
		if string.find(parts, "routes") then
			out.routes = { playHole(n, "good"), playHole(n, "average") }
		end
		if string.find(parts, "hio") then
			out.hio = hioAttempt(n, o.hioTries)
		end
		if string.find(parts, "banks") then
			out.banks = bankShots(n)
		end
		if string.find(parts, "sweep") then
			out.sweep = timingSweep(n, o.sweep or 6)
		end
		if string.find(parts, "fuzz") then
			out.fuzz = fuzz(n, o.fuzz or 12, o.seed)
		end
		out.issues = table.clone(issues)
		out.escapes, out.stuck = 0, 0
		for _, it in issues do
			if it.kind == "escape" then
				out.escapes += 1
			elseif it.kind ~= "unstuck" then
				out.stuck += 1
			end
		end
		out.nudges = 0
		for _, it in issues do
			if it.kind == "unstuck" then
				out.nudges += 1
			end
		end
		return out
	end
end

------------------------------------------------------------------------ scenarios
local SCENARIOS = {}

local function scenario(def)
	table.insert(SCENARIOS, def)
end

local S = 1 -- test lane felt height

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
	desc = "Hole 1 Lantern Gate 45-degree timber deflector at 4 and 6 m/s: speed and angle in/out",
	seconds = 13,
	run = function()
		refreshFelt()
		local shots = {}
		setFrame(W(1, -1, 0.5, -31), 12, Vector3.new(1, 0, 0))
		for _, speed in { 4, 6 } do
			placeL(1, 0, -27, 1)
			table.insert(shots, shoot("bank-" .. speed .. "mps", WD(1, 0, -1), speed, { timeout = 6 }))
		end
		return { shots = shots }
	end,
})

scenario({
	name = "walls",
	desc = "Restitution: rail head-on (3 and 6 m/s) and at 45 degrees, bumper block head-on and at 45 degrees",
	seconds = 15,
	run = function()
		refreshFelt()
		local shots = {}
		-- hole 1 green's north rail (inner face z = -36), head-on
		setFrame(W(1, -6, 0.5, -34), 8, Vector3.new(1, 0, 0))
		for _, speed in { 3, 6 } do
			placeL(1, -6, -32.5, 1)
			table.insert(shots, shoot("wall-straight-" .. speed .. "mps", WD(1, 0, -1), speed, { timeout = 3 }))
		end
		-- hole 1 lane's east rail (inner face x = 3.5) at 45 degrees
		placeL(1, 1, -8, 1)
		table.insert(shots, shoot("wall-45deg-5mps", WD(1, 1, -1), 5, { timeout = 3 }))
		-- hole 3 toadstool stool bumper (17, -28.8), 1.6 square: head-on, then 45 degrees onto its face
		setFrame(W(3, 17, 0, -27), 8, Vector3.new(0, 0, 1))
		placeL(3, 17, -25, 1)
		table.insert(shots, shoot("bumper-straight-6mps", WD(3, 0, -1), 6, { timeout = 3 }))
		placeL(3, 14.6, -25, 1)
		table.insert(shots, shoot("bumper-45deg-5mps", WD(3, 1, -1), 5, { timeout = 3 }))
		return { shots = shots }
	end,
})

scenario({
	name = "hill",
	desc = "Hole 9 ramp (1 stud rise): 5 m/s climbs to the landing, 2 m/s rolls back",
	seconds = 22,
	run = function()
		refreshFelt()
		local shots = {}
		local low = W(9, 0, 0, -2).Y
		local high = W(9, 0, 1, -25).Y
		setFrame(W(9, 0, 0.5, -14), 24, Vector3.new(1, 0, 0))
		for _, def in { { "hill-strong-5mps", 5 }, { "hill-weak-2mps", 2 } } do
			placeL(9, 0, -2, 1)
			local r = shoot(def[1], WD(9, 0, -1), def[2], { cup = hole(9).Cup, timeout = 14 })
			r.madeGreen = r.maxY > high + R - 0.05
			r.endedOnGreen = r.finish[2] > high + R - 0.05
			r.rolledBack = r.finish[2] < low + R + 0.05
			table.insert(shots, r)
		end
		return { shots = shots }
	end,
})

scenario({
	name = "cup",
	desc = "Hole 1 cup (r 0.5) from 60 cm at 1.3 to 4 m/s: holed or lip-out, speed at the rim",
	seconds = 16,
	run = function()
		refreshFelt()
		local shots = {}
		local cup = hole(1).Cup
		setFrame(cup.Position, 6, Vector3.new(1, 0, 0))
		for _, speed in { 1.3, 1.6, 2.0, 2.5, 3.0, 4.0 } do
			placeL(1, -9.5, -26.5 + 2, 1)
			local r = shoot("cup-" .. speed .. "mps", WD(1, 0, -1), speed, { cup = cup, timeout = 6 })
			r.holed = r.outcome == "cup"
			r.cupPos = vec(cup.Position)
			r.cupRadius = cup:GetAttribute("Radius")
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

scenario({
	name = "movers",
	desc = "Moving parts vs spec: server constraint value and blocker pose error, network owner, client lag",
	seconds = 8,
	run = function()
		refreshFelt()
		local srv = HttpService:JSONDecode(testRemote:InvokeServer("movers", {}))
		local lags = {}
		for n = 1, 9 do
			for _, m in moversOf(n) do
				local lag, err = moverLag(m)
				table.insert(lags, { hole = n, id = m:GetAttribute("MoverId"), lag = round(lag, 3), residual = round(err, 3) })
			end
		end
		local ok = #srv.movers == 6
		for _, m in srv.movers do
			ok = ok and math.abs(m.err) < (m.type == "rotate" and 2 or 0.1) and m.blockerPosErr < 0.1 and m.networkOwnerServer and not m.anchored
		end
		return { server = srv.movers, client = lags, ok = ok }
	end,
})

for n = 1, 9 do
	scenario({
		name = "h" .. n,
		desc = "Hole " .. n .. ": intended lines (good/average), HIO line + sweep, rail banks, mover timing sweep, fuzz (escape/stuck)",
		seconds = 600,
		run = holeScenario(n),
	})
end

-- Hole 7: can the sliding log pin the ball? Balls parked in / beside the log's path near both ends of its
-- travel (next to the side rails and the pool gap) and slow putts into its path; each one records whether the
-- ball ended up stuck against the log (contact + ~0 speed for > 0.5 s), what the unstick nudge did, and where.
scenario({
	name = "h7pin",
	desc = "Hole 7 sliding log: try to pin the ball against a rail (parked balls, slow putts, end-of-travel), unstick nudge",
	seconds = 240,
	run = function()
		refreshFelt()
		table.clear(issues)
		local n = 7
		local log = moversOf(n)[1]
		setFrame(W(n, 0, -1.2, -20.5), 24, Vector3.new(0, 0, -1))
		local cases = {}
		local blk = log:FindFirstChild("Blocker")
		local function watch(label, seconds)
			-- watch the ball for `seconds`: min speed while touching the log, max continuous pinned time, nudges
			local t0 = os.clock()
			local pinned, maxPinned, touched = 0, 0, false
			local nudges0 = #issues
			local lastT = os.clock()
			while os.clock() - t0 < seconds do
				RunService.Heartbeat:Wait()
				local now2 = os.clock()
				local dt = now2 - lastT
				lastT = now2
				local p = Ball.ball.Position
				local lp = blk.CFrame:PointToObjectSpace(p)
				local h = blk.Size / 2
				local c = Vector3.new(math.clamp(lp.X, -h.X, h.X), math.clamp(lp.Y, -h.Y, h.Y), math.clamp(lp.Z, -h.Z, h.Z))
				local touching = (lp - c).Magnitude < R + 0.05
				touched = touched or touching
				local v = flat(Ball.ball.AssemblyLinearVelocity).Magnitude
				if touching and v < 0.5 then
					pinned += dt
					maxPinned = math.max(maxPinned, pinned)
				else
					pinned = 0
				end
			end
			local nudged = {}
			for i = nudges0 + 1, #issues do
				table.insert(nudged, issues[i])
			end
			return { label = label, touchedLog = touched, maxPinnedS = round(maxPinned, 2), nudges = nudged, finish = vec(Ball.ball.Position), zone = zoneOf(Ball.ball.Position), state = Ball.state }
		end
		-- 1) parked balls in the log's path at the ends of its travel (log end reaches x = +-8.5; rails at +-10)
		for _, x in { 8.4, 8.6, 9.0, 9.85, -8.4, -8.6, -9.0, -9.85, 0, 5 } do
			for _, z in { -20.5, -19.98, -21.02 } do
				local ok = pcall(placeL, n, x, z, -0.5)
				if ok then
					shotFlags = {}
					local r = watch(string.format("parked x=%.2f z=%.2f", x, z), 5.2)
					shotFlags = nil
					r.start = { x, z }
					table.insert(cases, r)
				end
			end
		end
		-- 2) slow putts into the log's path from the middle tier, at 4 phases
		for _, ph in { 0, 1.2, 2.4, 3.6 } do
			for _, x in { 7.5, -7.5, 0 } do
				placeL(n, x, -18.5, -0.5)
				waitPhase(n, ph, log:GetAttribute("Period"))
				shotFlags = {}
				Ball.hit(WD(n, 0, -1) * 2.2, "test")
				local r = watch(string.format("putt x=%.1f phase=%.1f", x, ph), 5)
				shotFlags = nil
				r.start = { x, -18.5 }
				table.insert(cases, r)
				local t0 = os.clock()
				while Ball.state ~= "ready" and os.clock() - t0 < 6 do
					task.wait()
				end
			end
		end
		local pins, maxPinned = 0, 0
		for _, c in cases do
			maxPinned = math.max(maxPinned, c.maxPinnedS)
			if c.maxPinnedS > 0.5 or #c.nudges > 0 then
				pins += 1
			end
		end
		return { cases = cases, pinCases = pins, maxPinnedS = maxPinned, issues = table.clone(issues) }
	end,
})

-- Hole 8 root door (slides +-2.5 along z across the alcove mouth; its ends reach into the alcove rails):
-- balls parked against the rails at the door's ends of travel. Does the door crush/launch/pin them?
scenario({
	name = "h8door",
	desc = "Hole 8 sliding root door: balls parked against the alcove rails at the door's end of travel",
	seconds = 120,
	run = function()
		refreshFelt()
		table.clear(issues)
		local n = 8
		local door = moversOf(n)[1]
		local blk = door:FindFirstChild("Blocker")
		setFrame(W(n, 5, 0, -11.5), 10, Vector3.new(0, 0, -1))
		local cases = {}
		for _, c in { { 4.75, -8.1 }, { 4.75, -14.9 }, { 4.5, -8.2 }, { 5.0, -14.8 }, { 4.75, -9.0 }, { 3.9, -8.1 } } do
			local ok = pcall(placeL, n, c[1], c[2], 0.5)
			if ok then
				local start = Ball.ball.Position
				local t0 = os.clock()
				local maxSpeed, maxY, pinned, maxPinned, lastT = 0, start.Y, 0, 0, os.clock()
				shotFlags = {}
				while os.clock() - t0 < 5.5 do
					RunService.Heartbeat:Wait()
					local dt = os.clock() - lastT
					lastT = os.clock()
					local v = Ball.ball.AssemblyLinearVelocity
					maxSpeed = math.max(maxSpeed, v.Magnitude)
					maxY = math.max(maxY, Ball.ball.Position.Y)
					local lp = blk.CFrame:PointToObjectSpace(Ball.ball.Position)
					local h = blk.Size / 2
					local cl = Vector3.new(math.clamp(lp.X, -h.X, h.X), math.clamp(lp.Y, -h.Y, h.Y), math.clamp(lp.Z, -h.Z, h.Z))
					if (lp - cl).Magnitude < R + 0.05 and flat(v).Magnitude < 0.5 then
						pinned += dt
						maxPinned = math.max(maxPinned, pinned)
					else
						pinned = 0
					end
				end
				local fl = shotFlags
				shotFlags = nil
				table.insert(cases, {
					start = c,
					maxSpeed = round(maxSpeed),
					maxRise = round(maxY - start.Y),
					maxPinnedS = round(maxPinned, 2),
					finish = vec(Ball.ball.Position),
					zone = zoneOf(Ball.ball.Position),
					state = Ball.state,
					flags = fl,
				})
				local t1 = os.clock()
				while Ball.state ~= "ready" and os.clock() - t1 < 6 do
					task.wait()
				end
			end
		end
		return { cases = cases, issues = table.clone(issues), range = { door:GetAttribute("RangeMin"), door:GetAttribute("RangeMax") } }
	end,
})

-- Hole-to-hole progression: sink every hole in turn (a gentle putt from 1.5 studs) and check that the server moves
-- the ball to the next tee, the VR rig warps beside it (SimulateVR), the HUD shows the new hole, and after hole 9
-- the final 9-hole scorecard opens.
scenario({
	name = "progress",
	desc = "Hole-to-hole progression 1 -> 9: sink, next tee, VR warp to the tee, HUD, final 9-hole scorecard",
	seconds = 120,
	run = function()
		refreshFelt()
		local rows = {}
		local gui = player.PlayerGui -- screen HUD (GolfHUD) or the VR wrist/card panels
		local completed = false
		local conn = Remotes.CourseComplete.OnClientEvent:Connect(function()
			completed = true
		end)
		local n = 1
		local sp
		-- a spot 1.5 studs from the cup on the cup's own felt level with a clear line to it (any of 8 directions)
		local wallRay = RaycastParams.new()
		wallRay.FilterType = Enum.RaycastFilterType.Exclude
		wallRay.FilterDescendantsInstances = { workspace:FindFirstChild("Balls") }
		local function nearCup(k)
			local c = spec(k).cup.position
			local cupW = hole(k).Cup.Position
			for i = 0, 7 do
				local a = math.rad(90 + i * 45)
				local x, z = c[1] + math.cos(a) * 1.5, c[3] + math.sin(a) * 1.5
				local w = W(k, x, c[2], z)
				local hit = feltHit(w)
				if hit and math.abs(hit.Position.Y - cupW.Y) < 0.05 then
					local from = w + Vector3.new(0, G + 0.02, 0)
					local to = cupW + Vector3.new(0, G + 0.02, 0)
					local block = workspace:Raycast(from, to - from, wallRay)
					if not block or block.Instance.Name == "CupPlate" then
						return x, z
					end
				end
			end
			return c[1], c[3] + 1.5
		end
		sp = spec(1)
		local x0, z0 = nearCup(1)
		placeL(1, x0, z0, sp.cup.position[2])
		while n <= 9 do
			sp = spec(n)
			local cupW = hole(n).Cup.Position
			if n > 1 then
				-- the server already put us on this hole's tee: walk the ball up to its cup
				local x, z = nearCup(n)
				placeL(n, x, z, sp.cup.position[2])
			end
			local placedBefore = placedCount
			local r = shootS("progress-h" .. n, cupW - Ball.ball.Position, speedFor(1.5 + 0.6), { cup = hole(n).Cup, timeout = 8 })
			local row = { hole = n, sunk = r.outcome == "cup" }
			if n < 9 then
				-- wait for the server's next-hole placement (HoleTransitionTime)
				local t0 = os.clock()
				while (placedCount == placedBefore or Ball.holeIndex ~= n + 1 or Ball.state ~= "ready") and os.clock() - t0 < Config.HoleTransitionTime + 6 do
					task.wait()
				end
				task.wait(0.3)
				local tee = hole(n + 1).Tee.Position
				row.nextHole = Ball.holeIndex
				row.ballToTee = round(flat(Ball.ball.Position - tee).Magnitude, 3)
				if VR and VR.test then
					row.vrRigToBall = round(flat(VR.test.getOrigin().Position - Ball.ball.Position).Magnitude, 2)
					row.vrRigFloorDelta = round(VR.test.getOrigin().Y - (Ball.ball.Position.Y - R), 3)
				end
				local title = ""
				for _, d in gui and gui:GetDescendants() or {} do
					if d:IsA("TextLabel") and string.find(d.Text, "^Hole %d") then
						title = d.Text
					end
				end
				row.hudTitle = title
				row.ok = row.sunk and row.nextHole == n + 1 and row.ballToTee < 0.3 and (row.vrRigToBall == nil or row.vrRigToBall < 3)
			else
				local t0 = os.clock()
				while not completed and os.clock() - t0 < Config.HoleTransitionTime + 6 do
					task.wait()
				end
				task.wait(0.5)
				local card = gui and gui:FindFirstChild("Scorecard", true)
				row.courseComplete = completed
				row.scorecard = card ~= nil
				local cells = {}
				for _, d in card and card:GetDescendants() or {} do
					if d:IsA("TextLabel") then
						table.insert(cells, d.Text)
					end
				end
				row.scorecardCells = cells
				row.ok = row.sunk and completed and card ~= nil and table.find(cells, "27") ~= nil and table.find(cells, "9") ~= nil
			end
			table.insert(rows, row)
			n += 1
		end
		conn:Disconnect()
		local ok = true
		for _, r in rows do
			ok = ok and r.ok
		end
		return { rows = rows, ok = ok }
	end,
})

------------------------------------------------------------------------ VR plane snap / ghosting (SimulateVR)
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

local function surfaceAt(n, x, z, y)
	local p = W(n, x, y or 0, z)
	local hit = feltHit(p, p.Y + 0.6)
	return hit.Position
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
		refreshFelt()
		local cases = {}
		-- hole 1 lane, ball touching the east rail (inner face x = 3.5): the warp stance lands outside the rail
		local s1 = surfaceAt(1, 3.5 - R - 0.01, -8)
		local c1 = W(1, 3.85, 0, -8)
		setFrame(s1, 6, Vector3.new(0, 0, 1))
		table.insert(cases, measureLedge("h1-ball-at-rail", 1, s1.X, s1.Z, s1.Y, c1.X, c1.Z))
		-- ball 1 stud from the rail: the warp stance lands on top of the rail
		local s2 = surfaceAt(1, 2.5, -8)
		local c2 = W(1, 3.8, 0, -7.8)
		table.insert(cases, measureLedge("h1-stance-on-rail", 1, s2.X, s2.Z, s2.Y, c2.X, c2.Z))
		-- hole 4's raised green (0.6 up), ball at its west rail (inner face x = -6), head teleported over the rail
		local s3 = surfaceAt(4, -6 + R + 0.01, -41, 0.6)
		local c3 = W(4, -6.4, 0, -40.7)
		setFrame(s3, 6, Vector3.new(0, 0, 1))
		table.insert(cases, measureLedge("h4-green-edge", 4, s3.X, s3.Z, s3.Y, c3.X, c3.Z, Vector3.new(W(4, -6.5, 0, -41).X, s3.Y, W(4, -6.5, 0, -41).Z)))
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
	desc = "VR club ghosting: sweep the putter head through a rail and a bumper block, then a real VR swing hit",
	vr = true,
	seconds = 15,
	run = function()
		local skip = vrRequired()
		if skip then
			return skip
		end
		refreshFelt()
		local out = {}
		-- through hole 1's east lane rail (x 3.5..4.0) with the ball well away
		placeL(1, 0, -12, 1)
		setFrame(W(1, 3.75, 0, -12), 8, Vector3.new(0, 0, 1))
		out.wall = sweep("through-rail", W(1, 2.6, 0, -10), W(1, 6.2, 0, -10), 1.0)
		-- through hole 3's toadstool stool bumper (17, -28.8), 1.6 square
		placeL(3, 13.5, -28.8, 1)
		setFrame(W(3, 17, 0, -28.8), 8, Vector3.new(0, 0, 1))
		out.post = sweep("through-bumper", W(3, 15.4, 0, -28.7), W(3, 18.6, 0, -28.7), 1.0)
		-- a real swing through the ball: putter face speed 4 studs/s (1.2 m/s) along the hole's -Z
		local bp = placeL(1, 0, -6, 1)
		setFrame(W(1, 0, 0, -9), 8, Vector3.new(1, 0, 0))
		local fwd = WD(1, 0, -1)
		local half = VR.test.headSize / 2
		local y = ballPlaneY() + half.Y + 0.01
		local clubSpeed = 4
		local a = Vector3.new(bp.X, y, bp.Z) - fwd * (R + half.X + 0.5)
		local t0 = os.clock() + 0.5
		local strokesBefore = GolfTest.hitCount
		outcome = nil
		shot = { label = "vr-swing", start = Ball.ball.Position, dir = fwd, t0 = now(), contacts = {}, maxY = 0, maxAlong = 0 }
		shotLabel = "vr-swing"
		poseFn = function(t)
			local d = math.max(0, t - t0) * clubSpeed
			return VR.test.handCFrameFor(a + fwd * math.min(d, 1.4), fwd)
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
			distM = round(flat(Ball.ball.Position - bp).Magnitude * STUD),
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
		refreshFelt()
		placeL(1, 0, -4, 1)
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
	elseif cmd == "frame" then
		-- screenshot framing: ("topdown", n) north-up plan of hole n (0 = whole course), ("hole", n) 3/4 view from
		-- behind the tee, ("ball") chase cam on the ball, ("clear") back to normal. Haze is thinned for shots.
		local atm = game:GetService("Lighting"):FindFirstChildOfClass("Atmosphere")
		if a == "clear" then
			workspace:SetAttribute("GolfTestCamera", "")
			if atm and GolfTest.savedHaze then
				atm.Density, atm.Haze = GolfTest.savedHaze[1], GolfTest.savedHaze[2]
			end
			return "ok"
		end
		if a == "ball" then
			workspace:SetAttribute("GolfTestCamera", "follow")
			return "ok"
		end
		if atm and not GolfTest.savedHaze then
			GolfTest.savedHaze = { atm.Density, atm.Haze }
		end
		if atm then
			atm.Density, atm.Haze = 0.12, 0.4
		end
		if atm and b == 0 then
			atm.Density, atm.Haze = 0, 0 -- the world overview is shot from ~1000 studs up
		end
		local box
		-- world layout: CourseBuilder stores the terrain extent; the overview frames the whole world, not just the holes
		local wmin, wmax = workspace.Course:GetAttribute("WorldMin"), workspace.Course:GetAttribute("WorldMax")
		local world = wmin ~= nil and wmax ~= nil
		if b == 0 and world then
			box = { (wmin + wmax) / 2, wmax - wmin }
		elseif b == 0 then
			local lo, hi = Vector3.one * math.huge, -Vector3.one * math.huge
			for _, h in workspace.Course:GetChildren() do
				local bd = h:FindFirstChild("Bounds")
				if bd then
					lo = lo:Min(bd.Position - bd.Size / 2)
					hi = hi:Max(bd.Position + bd.Size / 2)
				end
			end
			box = { (lo + hi) / 2, hi - lo }
		else
			local bd = hole(b).Bounds
			box = { bd.Position, bd.Size }
		end
		local c = Vector3.new(box[1].X, b == 0 and (world and 30 or 8) or hole(b):GetAttribute("FeltMaxY"), box[1].Z)
		if a == "topdown" then
			-- frame size is the larger of the extents, corrected for the viewport aspect
			local vp = workspace.CurrentCamera.ViewportSize
			local aspect = vp.X / math.max(vp.Y, 1)
			-- (the runner crops the CoreGui strip off the top of the capture: leave room for it)
			local size = math.max(box[2].Z, box[2].X / aspect) * (b == 0 and 1.22 or 1.18)
			workspace:SetAttribute("GolfTestTopFOV", (b == 0 and world) and 85 or nil)
			setFrame(c, size, Vector3.new(0, 0, -1))
			workspace:SetAttribute("GolfTestCamera", "topdown")
		elseif a == "hole" then
			local s2 = math.max(box[2].X, box[2].Z)
			-- from behind the tee (south), except where a landmark sits between the camera and the hole
			local VIEW = { [6] = Vector3.new(0.85, 0, -0.35), [9] = Vector3.new(-0.55, 0, 0.75) }
			-- (directions are in the hole's local frame: +Z = behind the tee)
			local d = holeCF(b):VectorToWorldSpace((VIEW[b] or Vector3.new(0.15, 0, 1)).Unit)
			workspace:SetAttribute("GolfTestFocus", c)
			-- (world layout: H9 is inside the hollow tree, so the camera has to stay inside the trunk)
			local back, up = 0.8, 0.62
			if world and b == 9 then
				back, up = 0.3, 0.5
			end
			workspace:SetAttribute("GolfTestCamPos", c + d * s2 * back + Vector3.new(0, s2 * up, 0))
			workspace:SetAttribute("GolfTestCamUp", Vector3.yAxis)
			workspace:SetAttribute("GolfTestFOV", 50)
			workspace:SetAttribute("GolfTestCamera", "look")
		elseif a == "ball" then
			workspace:SetAttribute("GolfTestCamera", "follow")
		end
		return "ok"
	elseif cmd == "putt" then
		-- ("putt", n, "hio"|skill): from where the ball is, fire the HIO line or the intended next shot (async)
		local n = a
		task.spawn(function()
			local sp = spec(n)
			local pos = Ball.ball.Position
			if b == "hio" and sp.hio then
				if sp.hio.phase then
					waitPhase(n, sp.hio.phase)
				end
				Ball.hit(aimDir(n, sp.hio.aim_deg) * sp.hio.speed, "test")
			else
				local target, carry, pscale = chooseTarget(n, b or "good", zoneOf(pos) or "?", pos)
				local v = speedFor(flat(target - pos).Magnitude + carry) * pscale
				if target.Y - pos.Y > 0.05 then
					v += math.sqrt(2 * workspace.Gravity * (target.Y - pos.Y))
				end
				Ball.hit(flat(target - pos).Unit * math.min(v, VMAX), "test")
			end
		end)
		return "ok"
	elseif cmd == "place" then
		-- ("place", n, "x,z") put the ball at spec-local (x, z) on hole n (default: the tee)
		refreshFelt()
		local ok, err = pcall(function()
			local sp = spec(a)
			local x, z = sp.tee.position[1], sp.tee.position[3]
			if b and b ~= "" then
				local xs, zs = string.match(b, "([%-%d%.]+),([%-%d%.]+)")
				x, z = tonumber(xs), tonumber(zs)
			end
			placeL(a, x, z, 3)
		end)
		return ok and "ok" or ("error: " .. tostring(err))
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
		camera.Focus = CFrame.new(focus)
	elseif mode == "fixed" then
		camera.FieldOfView = 50
		local pos = focus - view * size * 0.75 + Vector3.new(0, size * 0.6, 0)
		camera.CFrame = CFrame.lookAt(pos, focus)
	elseif mode == "topdown" then
		-- (the world overview uses a wide lens: the play client stops drawing parts/terrain ~1000 studs out)
		local fov = workspace:GetAttribute("GolfTestTopFOV") or 50
		camera.FieldOfView = fov
		local h = (size / 2) / math.tan(math.rad(fov / 2)) * 1.1
		camera.CFrame = CFrame.lookAt(focus + Vector3.new(0, h, 0), focus, view)
		camera.Focus = CFrame.new(focus) -- render detail/lighting around the framed spot, not ~1000 studs up
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
	Remotes.Notice.OnClientEvent:Connect(function(text, _, oobKind)
		if oobKind and shot and not outcome then
			outcome = "oob"
			if run.running then
				event("oob", { pos = vec(Ball.ball.Position) })
			end
		end
	end)

	-- escape/stuck detection hooks (see flag())
	Ball.Teleported.Event:Connect(function(id, vin, vout)
		if run.running then
			flag("teleport", { id = id, speedIn = round(vin), speedOut = round(vout), pos = vec(Ball.ball.Position) })
		end
	end)
	Ball.Unstuck.Event:Connect(function(reason, from, to)
		if run.running then
			flag("unstuck", { reason = reason, from = vec(from), to = vec(to) })
		end
	end)
	Ball.OffSurface.Event:Connect(function(pos, partName)
		if run.running then
			flag("offsurface", { pos = vec(pos), part = partName })
		end
	end)
	Ball.ForcedRest.Event:Connect(function(pos, reason)
		if run.running then
			flag("forcedrest", { pos = vec(pos), reason = reason })
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
