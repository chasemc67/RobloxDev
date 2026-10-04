-- Spinners: animates tagged obstacles (the windmill) on each client using server time,
-- so every client sees the same blade position and the locally simulated ball collides with it.
local CollectionService = game:GetService("CollectionService")
local RunService = game:GetService("RunService")

local Spinners = {}

local active = {}

local function add(model)
	local pivot = model:GetAttribute("PivotCFrame")
	local rps = model:GetAttribute("RPS") or 0.25
	if typeof(pivot) ~= "CFrame" then
		return
	end
	local parts = {}
	for _, p in model:GetDescendants() do
		if p:IsA("BasePart") then
			parts[p] = pivot:ToObjectSpace(p.CFrame)
		end
	end
	active[model] = { pivot = pivot, omega = rps * math.pi * 2, parts = parts }
end

local function step()
	local t = workspace:GetServerTimeNow()
	for _, s in active do
		local angle = (t * s.omega) % (math.pi * 2)
		local rot = s.pivot * CFrame.Angles(0, 0, -angle)
		local axis = s.pivot.LookVector -- rotation axis (blades spin in the pivot's XY plane)
		local angVel = axis * s.omega -- CFrame.Angles(0,0,-a) about local Z == +a about LookVector
		for part, offset in s.parts do
			local cf = rot * offset
			part.CFrame = cf
			-- give contacts the correct surface velocity
			part.AssemblyAngularVelocity = angVel
			part.AssemblyLinearVelocity = angVel:Cross(cf.Position - s.pivot.Position)
		end
	end
end

function Spinners.start()
	for _, m in CollectionService:GetTagged("Spinner") do
		add(m)
	end
	CollectionService:GetInstanceAddedSignal("Spinner"):Connect(add)
	RunService.PreSimulation:Connect(step)
end

return Spinners
