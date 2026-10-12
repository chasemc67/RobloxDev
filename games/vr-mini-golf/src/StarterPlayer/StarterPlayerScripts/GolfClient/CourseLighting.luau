-- CourseLighting (stage w): each course has its own sky. Lantern Grove's is whatever the place's Lighting holds
-- (WorldBuilder.ApplyLighting, warm autumn evening); Sugarloaf Canyon's golden-hour sunset is applied locally while
-- the camera is inside Sugarloaf's world box (workspace.CourseSugarloaf WorldMin/WorldMax, 5000 studs north) and the
-- captured Lantern Grove values come back when it leaves. Same idea as H9Lighting (which only acts inside LG's H9).
-- Sugarloaf values: assets/vr-mini-golf/sugarloaf-canyon/course.md "Lighting (sunset, launch)": the game sun at
-- bearing 277, elevation 25 (GeographicLatitude 17 + ClockTime 16.3 measure 277.2 / 25.3 in Studio).
local Lighting = game:GetService("Lighting")
local RunService = game:GetService("RunService")

local CourseLighting = {}

local function hex(s)
	return Color3.fromHex(s)
end

local SUGARLOAF = {
	lighting = {
		ClockTime = 16.3,
		GeographicLatitude = 17,
		Ambient = hex("7A4A50"),
		OutdoorAmbient = hex("C9806A"),
		Brightness = 2.0,
		ColorShift_Top = hex("FFC38A"),
		ColorShift_Bottom = hex("B45A7A"),
	},
	Atmosphere = { Density = 0.35, Offset = 0.1, Color = hex("F7B48E"), Decay = hex("B4699A"), Glare = 0.6, Haze = 2.0 },
	BloomEffect = { Intensity = 0.7, Threshold = 1.3 },
	SunRaysEffect = { Intensity = 0.12 },
	terrain = { WaterColor = hex("3FB7C9"), WaterTransparency = 0.6 },
}

local saved = nil
local active = false

local function capture()
	local s = { lighting = {}, effects = {}, terrain = {} }
	for k in SUGARLOAF.lighting do
		s.lighting[k] = Lighting[k]
	end
	for class, props in SUGARLOAF do
		if class ~= "lighting" and class ~= "terrain" then
			local inst = Lighting:FindFirstChildOfClass(class)
			if inst then
				local t = {}
				for k in props do
					t[k] = inst[k]
				end
				s.effects[class] = t
			end
		end
	end
	for k in SUGARLOAF.terrain do
		s.terrain[k] = workspace.Terrain[k]
	end
	return s
end

local function apply(set, effects)
	for k, v in set.lighting do
		Lighting[k] = v
	end
	for class, props in effects do
		local inst = Lighting:FindFirstChildOfClass(class)
		if inst then
			for k, v in props do
				inst[k] = v
			end
		end
	end
	for k, v in set.terrain do
		workspace.Terrain[k] = v
	end
end

function CourseLighting.setSugarloaf(on: boolean)
	if on == active then
		return
	end
	active = on
	if on then
		saved = capture()
		local effects = {}
		for class, props in SUGARLOAF do
			if class ~= "lighting" and class ~= "terrain" then
				effects[class] = props
			end
		end
		apply(SUGARLOAF, effects)
	elseif saved then
		apply(saved, saved.effects)
		saved = nil
	end
	workspace:SetAttribute("SugarloafLightingActive", active)
end

function CourseLighting.start(getEye)
	local elapsed = 0
	RunService.RenderStepped:Connect(function(dt)
		elapsed += dt
		if elapsed < 0.25 then
			return
		end
		elapsed = 0
		local sc = workspace:FindFirstChild("CourseSugarloaf")
		local mn, mx = sc and sc:GetAttribute("WorldMin"), sc and sc:GetAttribute("WorldMax")
		local eye = getEye and getEye() or workspace.CurrentCamera.CFrame.Position
		local inside = mn ~= nil and eye ~= nil and eye.X > mn.X - 400 and eye.X < mx.X + 400 and eye.Z > mn.Z - 400 and eye.Z < mx.Z + 400
		CourseLighting.setSugarloaf(inside)
	end)
end

return CourseLighting
