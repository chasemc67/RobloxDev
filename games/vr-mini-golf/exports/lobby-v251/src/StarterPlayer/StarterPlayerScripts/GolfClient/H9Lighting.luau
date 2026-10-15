-- Local zone treatment: capture the exact exposure/bloom state on each entry.
-- Uses generated H9 Bounds and VR eye / flat playing position, including room-scale movement.
-- Bounds span feltMin-8 to feltMax+30, leaving ample headroom above H9 felt.
local Lighting = game:GetService("Lighting")
local RunService = game:GetService("RunService")
local H9Lighting = {}
local active = false
local exposure
local blooms = {}
local connection

function H9Lighting.setInside(inside)
	if inside == active then return end
	active = inside
	if inside then
		exposure = Lighting.ExposureCompensation
		Lighting.ExposureCompensation = exposure - 0.3
		for _, effect in Lighting:GetChildren() do
			if effect:IsA("BloomEffect") then
				blooms[effect] = effect.Intensity
				effect.Intensity *= 0.5
			end
		end
	else
		if exposure ~= nil then Lighting.ExposureCompensation = exposure end
		for effect, intensity in blooms do
			if effect.Parent then effect.Intensity = intensity end
		end
		table.clear(blooms)
		exposure = nil
	end
	workspace:SetAttribute("H9LightingActive", active)
end

function H9Lighting.stop()
	if connection then connection:Disconnect(); connection = nil end
	H9Lighting.setInside(false)
end

function H9Lighting.start(getEye)
	H9Lighting.stop()
	local elapsed = 0
	connection = RunService.RenderStepped:Connect(function(dt)
		elapsed += dt
		if elapsed < 0.1 then return end
		elapsed = 0
		local course = workspace:FindFirstChild("Course")
		local hole = course and course:FindFirstChild("Hole9")
		local bounds = hole and hole:FindFirstChild("Bounds")
		local eye = getEye()
		local inside = false
		if bounds and eye then
			local p = bounds.CFrame:PointToObjectSpace(eye)
			local half = bounds.Size / 2
			inside = math.abs(p.X) <= half.X and math.abs(p.Y) <= half.Y and math.abs(p.Z) <= half.Z
		end
		H9Lighting.setInside(inside)
	end)
end

return H9Lighting
