-- MoverMath: the spec motion profile of a course moving part (holes.json moving_parts), shared by the server
-- driver (GolfServer.Movers), CourseBuilder and the test harness so they all agree on where a part is at time t.
--   swing:  angle = amplitude * sin(360 t / period + phase)
--   rotate: angle = phase + speed * t (no range) / ping-pong like slide (range)
--   slide:  ping-pong range[1] -> range[2] -> range[1] at |speed|, with optional dwell stops
--           (dwell = {{at, s}}: a stop at a range end pauses once per visit, an interior stop on both passes;
--           phase = offset at t=0 on the forward pass, and if a stop sits there t=0 is the start of its pause).
--   keys:   piecewise-linear offset over one `period` from keyframes {{t, v}} (Sugarloaf H11 lift deck and quay lip,
--           whose holes.json `schedule` is a timetable rather than a speed; stage w)
-- Same as the designer's sim (tools/sim.py part_state / slide_dwell_state).
local MoverMath = {}

local EPS = 1e-6

-- Dwell stops as "at:s;at:s" (Model attribute form) <-> {{at=, s=}}
function MoverMath.encodeDwell(dwell)
	local parts = {}
	for _, d in dwell or {} do
		table.insert(parts, string.format("%g:%g", d.at, d.s))
	end
	return table.concat(parts, ";")
end

-- Keyframes as "t:v;t:v" (Model attribute form) <-> {{t=, v=}}
function MoverMath.encodeKeys(keys)
	local parts = {}
	for _, k in keys or {} do
		table.insert(parts, string.format("%g:%g", k.t, k.v))
	end
	return table.concat(parts, ";")
end

function MoverMath.decodeKeys(str)
	local out = {}
	for t, v in string.gmatch(str or "", "([%-%d%.e]+):([%-%d%.e]+)") do
		table.insert(out, { t = tonumber(t), v = tonumber(v) })
	end
	return out
end

function MoverMath.decodeDwell(str)
	local out = {}
	for at, s in string.gmatch(str or "", "([%-%d%.e]+):([%-%d%.e]+)") do
		table.insert(out, { at = tonumber(at), s = tonumber(s) })
	end
	return out
end

-- Legs of one ping-pong cycle starting at range min: {x0, x1, dur} (x0 == x1 for a pause), plus the cycle length
-- and the time the forward pass reaches `phase` (start of its pause if a stop sits there).
local function legs(a, b, speed, dwell, phase)
	local sp = math.abs(speed)
	local out = {}
	local stops = {}
	for _, d in dwell or {} do
		if d.s > 0 and d.at >= a - EPS and d.at <= b + EPS then
			table.insert(stops, { at = math.clamp(d.at, a, b), s = d.s })
		end
	end
	table.sort(stops, function(p, q)
		return p.at < q.at
	end)
	local t, x, t0 = 0, a, nil
	local function pause(at, s)
		if t0 == nil and math.abs(at - phase) < EPS then
			t0 = t
		end
		table.insert(out, { x, x, s })
		t += s
	end
	local function move(to)
		if t0 == nil and phase > x - EPS and phase < to + EPS and to > x then
			t0 = t + (phase - x) / sp
		end
		local dur = math.abs(to - x) / sp
		if dur > 0 then
			table.insert(out, { x, to, dur })
			t += dur
		end
		x = to
	end
	-- forward pass a -> b (a stop at a pauses at the start of the cycle)
	for _, st in stops do
		if math.abs(st.at - a) < EPS then
			pause(a, st.s)
		end
	end
	for _, st in stops do
		if st.at > a + EPS and st.at < b - EPS then
			move(st.at)
			pause(st.at, st.s)
		end
	end
	move(b)
	for _, st in stops do
		if math.abs(st.at - b) < EPS then
			pause(b, st.s)
		end
	end
	-- back b -> a
	for i = #stops, 1, -1 do
		local st = stops[i]
		if st.at > a + EPS and st.at < b - EPS then
			local dur = math.abs(x - st.at) / sp
			table.insert(out, { x, st.at, dur })
			t += dur
			x = st.at
			table.insert(out, { x, x, st.s })
			t += st.s
		end
	end
	local dur = math.abs(x - a) / sp
	if dur > 0 then
		table.insert(out, { x, a, dur })
		t += dur
	end
	return out, t, t0 or 0
end

-- p: {type, speed, phase, range = {min, max} | nil, period (swing), amplitude (swing), dwell}
-- Returns value (deg or studs) and rate (per s) at time t.
function MoverMath.value(p, t)
	local phase = p.phase or 0
	if p.type == "toggle" then
		local clock = t + phase
		local cycleStart = math.floor(clock / p.period) * p.period
		return (clock >= cycleStart + p.solidStart and clock < cycleStart + p.solidEnd) and 1 or 0, 0
	end
	if p.type == "keys" then
		local keys = p.keys
		local tau = (t + phase) % p.period
		for i = 1, #keys - 1 do
			local a, b = keys[i], keys[i + 1]
			if tau >= a.t and tau <= b.t then
				if b.t - a.t < 1e-9 then
					return b.v, 0
				end
				local rate = (b.v - a.v) / (b.t - a.t)
				return a.v + rate * (tau - a.t), rate
			end
		end
		return keys[#keys] and keys[#keys].v or 0, 0
	end
	if p.type == "swing" then
		local w = 2 * math.pi / p.period
		local a = w * (t % p.period) + math.rad(phase)
		return p.amplitude * math.sin(a), p.amplitude * w * math.cos(a)
	end
	local sp = p.speed
	if not p.range then
		-- reduce t first: server time is ~1.7e9 and deg/s * that loses precision
		return phase + sp * (t % (360 / math.abs(sp))), sp
	end
	local a, b = p.range[1], p.range[2]
	if b - a <= 0 or sp == 0 then
		return a, 0
	end
	local L, period, t0 = legs(a, b, sp, p.dwell, phase)
	local tau = (t % period + t0) % period
	for _, leg in L do
		if tau <= leg[3] then
			if leg[1] == leg[2] then
				return leg[1], 0
			end
			local f = tau / leg[3]
			return leg[1] + (leg[2] - leg[1]) * f, (leg[2] > leg[1] and 1 or -1) * math.abs(sp)
		end
		tau -= leg[3]
	end
	return a, 0
end

-- Full cycle length in s (incl. pauses).
function MoverMath.period(p)
	if p.type == "swing" or p.type == "keys" or p.type == "toggle" then
		return p.period
	end
	if not p.range then
		return 360 / math.abs(p.speed)
	end
	local _, period = legs(p.range[1], p.range[2], p.speed, p.dwell, p.phase or 0)
	return period
end

-- Profile from a built mover Model's attributes (CourseBuilder:buildMover).
function MoverMath.fromModel(model)
	return {
		type = model:GetAttribute("Type"),
		speed = model:GetAttribute("Speed"),
		phase = model:GetAttribute("Phase") or 0,
		range = model:GetAttribute("HasRange") and { model:GetAttribute("RangeMin"), model:GetAttribute("RangeMax") } or nil,
		period = model:GetAttribute("Period"),
		solidStart = model:GetAttribute("SolidStart"),
		solidEnd = model:GetAttribute("SolidEnd"),
		amplitude = model:GetAttribute("Amplitude"),
		dwell = MoverMath.decodeDwell(model:GetAttribute("Dwell")),
		keys = MoverMath.decodeKeys(model:GetAttribute("Keys")),
	}
end

return MoverMath
