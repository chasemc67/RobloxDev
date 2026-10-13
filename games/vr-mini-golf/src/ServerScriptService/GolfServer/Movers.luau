-- Movers: drives the course's moving parts on the server (spinner bar, mill wheel, sliding log, root door,
-- root gate, lantern pendulum). Each one is an unanchored assembly built by CourseBuilder: a MoverRoot with the
-- colliding Blocker parts welded to it, held by a HingeConstraint (rotate, swing) or PrismaticConstraint (slide) to an
-- anchored MoverBase at the spec pivot, with a Motor actuator. Every physics step the motor velocity is set to
-- the spec rate plus a small correction toward the spec position at server time t (workspace:GetServerTimeNow()),
-- so the parts are phase-locked to the spec (pivot, axis, speed, range, phase) and every client sees the same
-- timing. Because the parts really move under physics (server network owner), the client-simulated ball gets a
-- proper contact response from their surface velocity.
local RunService = game:GetService("RunService")
local CollectionService = game:GetService("CollectionService")
local MoverMath = require(game:GetService("ReplicatedStorage"):WaitForChild("Golf"):WaitForChild("MoverMath"))

local Movers = {}

local KP = 6 -- 1/s: position correction gain
local MAX_CORRECTION = 2 -- x the spec rate (rad/s or studs/s) at most

-- Spec value (degrees or studs) and rate at time t (ReplicatedStorage.Golf.MoverMath, incl. slide dwell pauses).
local profiles = setmetatable({}, { __mode = "k" })
function Movers.value(model, t)
	local p = profiles[model]
	if not p then
		p = MoverMath.fromModel(model)
		profiles[model] = p
	end
	return MoverMath.value(p, t)
end

local function wrap180(d)
	return (d + 180) % 360 - 180
end

local active = {}

local function add(model)
	if active[model] then return end
	if model:GetAttribute("Type") == "toggle" then
		local parts = {}
		for _, ref in model:GetChildren() do
			if ref:IsA("ObjectValue") and ref.Name == "TogglePart" and ref.Value then
				table.insert(parts, ref.Value)
			end
		end
		local visuals = {}
		for _, part in model:GetDescendants() do
			if part:IsA("BasePart") and part:GetAttribute("ToggleVisual") then
				table.insert(visuals, part)
			end
		end
		active[model] = { toggle = true, parts = parts, visuals = visuals }
		return
	end
	local drive = model:FindFirstChild("Drive")
	local root = model:FindFirstChild("MoverRoot")
	if not drive or not root or active[model] then
		return
	end
	local ok = pcall(function()
		root:SetNetworkOwner(nil)
	end)
	active[model] = { drive = drive, root = root, rotate = drive:IsA("HingeConstraint"), owned = ok }
end

-- Current value of the constraint in spec units (degrees / studs) and the error to the spec at time t.
function Movers.state(model, t)
	local s = active[model]
	if not s then
		return nil
	end
	local want, rate = Movers.value(model, t)
	if s.toggle then return want, 0, 0 end
	if s.rotate then
		local cur = s.drive.CurrentAngle
		return cur, wrap180(want - cur), rate
	end
	local cur = s.drive.CurrentPosition
	return cur, want - cur, rate
end

local function step()
	local t = workspace:GetServerTimeNow()
	for model, s in active do
		if not model.Parent then
			active[model] = nil
			continue
		end
		if s.toggle then
			local solid = Movers.value(model, t) == 1
			for _, part in s.parts do
				part.CanCollide, part.CanQuery, part.CanTouch = solid, solid, solid
			end
			-- Render skins follow the same server-time solid window; they never provide collision.
			for _, part in s.visuals do
				part.Transparency = solid and (part:GetAttribute("ManifestTransparency") or 0) or 1
			end
			continue
		end
		local _, err, rate = Movers.state(model, t)
		local corr = KP * err
		local lim = math.abs(rate) * MAX_CORRECTION + 0.5
		corr = math.clamp(corr, -lim, lim)
		if s.rotate then
			s.drive.AngularVelocity = math.rad(rate + corr)
		else
			s.drive.Velocity = rate + corr
		end
	end
end

function Movers.start()
	for _, m in CollectionService:GetTagged("GolfMover") do
		add(m)
	end
	CollectionService:GetInstanceAddedSignal("GolfMover"):Connect(add)
	RunService.PreSimulation:Connect(step)
end

Movers.active = active

return Movers
