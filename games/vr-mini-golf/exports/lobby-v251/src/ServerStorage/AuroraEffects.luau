-- Stage am: reproducible visual-only effects, applied after manifest prop placement.
local Effects = {}
local CollectionService = game:GetService("CollectionService")
local MoverMath = require(game.ReplicatedStorage.Golf.MoverMath)
local function v3(v) return Vector3.new(v[1], v[2], v[3]) end
local function holeCF(hole)
	return CFrame.new(hole:GetAttribute("HoleOrigin")) * CFrame.Angles(0, math.rad(hole:GetAttribute("HoleYaw") or 0), 0)
end
local function visual(parent, name, cf, size)
	local p = Instance.new("Part")
	p.Name, p.CFrame, p.Size = name, cf, size
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch = true, false, false, false
	p.Transparency = 1
	p:SetAttribute("VisualQueryDisabled", true)
	CollectionService:AddTag(p, "VisualQueryDisabled")
	p.Parent = parent
	return p
end
local function eachPart(root, fn)
	if root:IsA("BasePart") then fn(root) end
	for _, p in root:GetDescendants() do if p:IsA("BasePart") then fn(p) end end
end
local function ref(mover, name, value)
	local r = Instance.new("ObjectValue")
	r.Name, r.Value, r.Parent = name, value, mover
end
local function anchor(def, id)
	for _, a in def.decoration_anchors or {} do if (a.id or a.name) == id then return a end end
end

function Effects.Apply(course, data)
	local result = { steam = false, ribbonParts = 0, lampParts = 0 }
	local h6 = course:FindFirstChild("Hole6")
	local pool = h6 and h6:FindFirstChild("h06_kettle_pool", true)
	if pool then
		local old = pool:FindFirstChild("KettleSteamSource", true)
		if old then old:Destroy() end
		local hazard
		for _, h in data.holes[6].hazards or {} do if h.id == "kettle_pool" then hazard = h end end
		assert(hazard, "Kettle steam requires the authored pool hazard")
		local cf = holeCF(h6)
		-- At water level: maximum rise <0.9 studs plus 0.3 radius. Never rises to a 5-stud tee eye.
		local source = visual(pool, "KettleSteamSource", cf * CFrame.new(v3(hazard.center) + Vector3.new(0, 0.12, 0)), Vector3.new(0.1, 0.1, 0.1))
		local at = Instance.new("Attachment")
		at.Name, at.Parent = "LowSteam", source
		local steam = Instance.new("ParticleEmitter")
		steam.Name = "KettleSteam"
		steam.Texture = "rbxasset://textures/particles/smoke_main.dds"
		steam.Color = ColorSequence.new(Color3.new(1, 1, 1))
		steam.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.2, 0.86), NumberSequenceKeypoint.new(0.7, 0.92), NumberSequenceKeypoint.new(1, 1)})
		steam.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.18), NumberSequenceKeypoint.new(1, 0.6)})
		steam.Speed, steam.Lifetime, steam.Rate = NumberRange.new(0.22, 0.4), NumberRange.new(1.2, 1.8), 5
		steam.Acceleration, steam.SpreadAngle, steam.Drag = Vector3.new(0, 0.03, 0), Vector2.new(8, 8), 0.1
		steam.Rotation, steam.RotSpeed = NumberRange.new(0, 360), NumberRange.new(-8, 8)
		steam.LightEmission = 0.25
		steam.Parent = at
		source:SetAttribute("MaxRiseStuds", 0.9)
		source:SetAttribute("EyeHeightStuds", 5)
		result.steam = true
	end
	local hole, def = course:FindFirstChild("Hole17"), data.holes[17]
	if not hole then return result end
	local mover = hole:FindFirstChild("Mover_aurora_span", true)
	assert(mover, "Aurora effects require the authored toggle mover")
	for _, child in mover:GetChildren() do
		if child:IsA("ObjectValue") and child.Name ~= "TogglePart" then child:Destroy() end
	end
	local old = hole:FindFirstChild("AuroraEffectSources")
	if old then old:Destroy() end
	local folder = Instance.new("Folder")
	folder.Name, folder.Parent = "AuroraEffectSources", hole
	local cf = holeCF(hole)
	local ribbon = hole:FindFirstChild("h17_aurora_ribbon", true)
	if not ribbon then
		local a = assert(anchor(def, "aurora_ribbon"), "Missing ribbon anchor")
		ribbon = visual(folder, "RibbonFallback", cf * CFrame.new(v3(a.pos or a.position) + Vector3.new(0, 20, 0)), Vector3.new(3, 20, 0.08))
		ribbon.Color, ribbon.Material = Color3.fromRGB(92,255,176), Enum.Material.Neon
	end
	local alpha, phase = MoverMath.toggleVisual(MoverMath.fromModel(mover), workspace:GetServerTimeNow())
	eachPart(ribbon, function(p)
		p.CanCollide, p.CanQuery, p.CanTouch = false, false, false
		p:SetAttribute("VisualQueryDisabled", true)
		ref(mover, "ToggleRibbon", p)
		local base = p:GetAttribute("ManifestTransparency") or 0
		p.Transparency = base + (1-base)*alpha
		result.ribbonParts += 1
	end)
	local lamp = hole:FindFirstChild("h17_span_lamp", true)
	if not lamp then
		local a = assert(anchor(def, "span_lamp"), "Missing lamp anchor")
		lamp = visual(folder, "LampFallback", cf * CFrame.new(v3(a.pos or a.position) + Vector3.new(0, 1.8, 0)), Vector3.new(0.4, 0.8, 0.4))
		lamp.Material = Enum.Material.Neon
	end
	eachPart(lamp, function(p)
		if p.Material ~= Enum.Material.Neon and not string.find(p.Name, "AuroraMint") then return end
		p.CanCollide, p.CanQuery, p.CanTouch = false, false, false
		p:SetAttribute("VisualQueryDisabled", true)
		ref(mover, "ToggleLamp", p)
		p.Color = phase == "solid" and Color3.fromRGB(92,255,176) or Color3.fromRGB(176,124,255)
		p.Transparency = phase == "gone" and 0.65 or 0
		local previous = p:FindFirstChild("SpanTimingLight")
		if previous then previous:Destroy() end
		local light = Instance.new("PointLight")
		light.Name, light.Range, light.Color = "SpanTimingLight", 7, p.Color
		light.Brightness = phase == "solid" and 1.5 or 0
		light.Parent = p
		ref(mover, "ToggleLight", light)
		result.lampParts += 1
	end)
	-- Fray points stay above y=10 along the ribbon, clear of the putt sightline.
	local ribbonAnchor = anchor(def, "aurora_ribbon")
	local pos = ribbonAnchor and (ribbonAnchor.pos or ribbonAnchor.position) or {0, 0, -29}
	for i = 1, 3 do
		local source = visual(folder, "RibbonFray" .. i, cf * CFrame.new(v3(pos) + Vector3.new((i-2)*1.1, 11+(i-1)*7, 0)), Vector3.new(0.1, 0.1, 0.1))
		local sparkles = Instance.new("ParticleEmitter")
		sparkles.Name, sparkles.Texture = "DimmingSparkles", "rbxasset://textures/particles/sparkles_main.dds"
		sparkles.Color = ColorSequence.new(Color3.fromRGB(92,255,176), Color3.fromRGB(176,124,255))
		sparkles.LightEmission, sparkles.Rate = 1, 24
		sparkles.Lifetime, sparkles.Speed = NumberRange.new(0.35,0.8), NumberRange.new(0.5,1.2)
		sparkles.SpreadAngle = Vector2.new(100,100)
		sparkles.Size = NumberSequence.new(0.13,0)
		sparkles.Transparency = NumberSequence.new(0.15,1)
		sparkles.Enabled, sparkles.Parent = phase == "fade_out", source
		ref(mover, "ToggleSparkles", sparkles)
	end
	return result
end
return Effects
