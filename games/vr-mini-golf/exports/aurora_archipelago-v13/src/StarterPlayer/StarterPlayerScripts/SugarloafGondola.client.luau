-- SugarloafGondola (stage ab): moves the Sunset Gondola cabin (SugarloafBuilder.PlaceKit tags it SugarloafGondola and
-- stores the ride as attributes) locally on every client, in step with server time so everyone sees the same cabin.
-- Ride (kit manifest gondola_cabin.motion): up line A -> T -> B, dwell, down line B -> T -> A, dwell. Each span is a
-- parabola P(w) = P + (Q - P) w - (0, 4 sag w (1 - w), 0), with w ~ arc length along the span / span length; the cabin
-- stays level at the line's constant yaw.
local CollectionService = game:GetService("CollectionService")
local RunService = game:GetService("RunService")

local function span(P: Vector3, Q: Vector3, sag: number, w: number)
	return P + (Q - P) * w - Vector3.new(0, 4 * sag * w * (1 - w), 0)
end

local function start(cabin: Model)
	local speed = cabin:GetAttribute("Speed") or 6
	local dwell = cabin:GetAttribute("Dwell") or 8
	local lines = {}
	for _, dir in { "up", "down" } do
		local arcs, sags = cabin:GetAttribute(dir .. "Arcs"), cabin:GetAttribute(dir .. "Sags")
		lines[dir] = { A = cabin:GetAttribute(dir .. "A"), T = cabin:GetAttribute(dir .. "T"), B = cabin:GetAttribute(dir .. "B"),
			L1 = arcs.X, L2 = arcs.Y, s1 = sags.X, s2 = sags.Y }
	end
	local up, down = lines.up, lines.down
	local upTime, downTime = (up.L1 + up.L2) / speed, (down.L1 + down.L2) / speed
	local cycle = upTime + dwell + downTime + dwell
	local upRot = CFrame.Angles(0, math.rad(cabin:GetAttribute("UpYaw") or 0), 0)
	local downRot = CFrame.Angles(0, math.rad(cabin:GetAttribute("DownYaw") or 180), 0)
	-- position at distance s along a line from A (0) to B (L1 + L2)
	local function along(l, s)
		if s <= l.L1 then
			return span(l.A, l.T, l.s1, math.clamp(s / l.L1, 0, 1))
		end
		return span(l.T, l.B, l.s2, math.clamp((s - l.L1) / l.L2, 0, 1))
	end
	local conn
	conn = RunService.RenderStepped:Connect(function()
		if not cabin.Parent then
			conn:Disconnect()
			return
		end
		local t = workspace:GetServerTimeNow() % cycle
		local cf
		if t < upTime then
			cf = CFrame.new(along(up, t * speed)) * upRot
		elseif t < upTime + dwell then
			cf = CFrame.new(up.B) * upRot
		elseif t < upTime + dwell + downTime then
			-- down line: from B back to A
			local s = (down.L1 + down.L2) - (t - upTime - dwell) * speed
			cf = CFrame.new(along(down, s)) * downRot
		else
			cf = CFrame.new(down.A) * downRot
		end
		cabin:PivotTo(cf)
	end)
end

for _, c in CollectionService:GetTagged("SugarloafGondola") do
	start(c)
end
CollectionService:GetInstanceAddedSignal("SugarloafGondola"):Connect(start)
