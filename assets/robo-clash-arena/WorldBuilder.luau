-- Robo Clash Arena: builds the holo-arena template, the lobby showcase and lighting.
-- Run in Studio edit mode: require(this).BuildArena(Config) -> Model (floor top at y = 0).
-- Arena layout (110 x 110): perimeter glass walls, 4 tall pillars, 2 low cover walls,
-- 4 raised corner blocks, 2 pits at (+-34, 0). Geometry folder = solid + blocks shots.

local World = {}

local FLOOR = Color3.fromRGB(18, 22, 38)
local GRID = Color3.fromRGB(0, 160, 255)
local WALL = Color3.fromRGB(60, 140, 255)
local TRIM = Color3.fromRGB(80, 230, 255)
local PILLAR = Color3.fromRGB(34, 38, 58)
local BAND = Color3.fromRGB(190, 80, 255)
local DANGER = Color3.fromRGB(255, 50, 80)

local function part(parent, name, size, cf, color, material, props)
	local p = Instance.new("Part")
	p.Name = name
	p.Anchored = true
	p.Size = size
	p.CFrame = cf
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	if props then
		for k, v in pairs(props) do
			p[k] = v
		end
	end
	p.Parent = parent
	return p
end

local DECOR = { CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false }

-- Split rect [x0,x1]x[z0,z1] minus axis-aligned holes into rectangles.
local function subtractHoles(x0, x1, z0, z1, holes)
	local xs = { x0, x1 }
	for _, h in ipairs(holes) do
		table.insert(xs, math.clamp(h[1], x0, x1))
		table.insert(xs, math.clamp(h[2], x0, x1))
	end
	table.sort(xs)
	local rects = {}
	for i = 1, #xs - 1 do
		local a, b = xs[i], xs[i + 1]
		if b - a > 0.01 then
			local cuts = {}
			for _, h in ipairs(holes) do
				if h[1] < b - 0.01 and h[2] > a + 0.01 then
					table.insert(cuts, { h[3], h[4] })
				end
			end
			table.sort(cuts, function(u, v)
				return u[1] < v[1]
			end)
			local z = z0
			for _, c in ipairs(cuts) do
				if c[1] > z then
					table.insert(rects, { a, b, z, c[1] })
				end
				z = math.max(z, c[2])
			end
			if z < z1 then
				table.insert(rects, { a, b, z, z1 })
			end
		end
	end
	return rects
end

function World.BuildArena(Config)
	local H = Config.Arena.Half
	local WH = Config.Arena.WallHeight
	local model = Instance.new("Model")
	model.Name = "ArenaTemplate"
	local geo = Instance.new("Folder")
	geo.Name = "Geometry"
	geo.Parent = model
	local decor = Instance.new("Folder")
	decor.Name = "Decor"
	decor.Parent = model
	local spawns = Instance.new("Folder")
	spawns.Name = "Spawns"
	spawns.Parent = model

	local holes = {
		{ -40, -28, -6, 6 },
		{ 28, 40, -6, 6 },
	}
	local floorThick = 3
	for i, r in ipairs(subtractHoles(-H, H, -H, H, holes)) do
		local sx, sz = r[2] - r[1], r[4] - r[3]
		local cx, cz = (r[1] + r[2]) / 2, (r[3] + r[4]) / 2
		part(geo, "Floor" .. i, Vector3.new(sx, floorThick, sz), CFrame.new(cx, -floorThick / 2, cz), FLOOR, Enum.Material.SmoothPlastic, { Reflectance = 0.08 })
		-- grid lines clipped to this rect
		local step = 10
		for gx = -H + step, H - step, step do
			if gx > r[1] + 0.05 and gx < r[2] - 0.05 then
				part(decor, "GridX", Vector3.new(0.18, 0.05, sz), CFrame.new(gx, 0.03, cz), GRID, Enum.Material.Neon, { Transparency = 0.45, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false })
			end
		end
		for gz = -H + step, H - step, step do
			if gz > r[3] + 0.05 and gz < r[4] - 0.05 then
				part(decor, "GridZ", Vector3.new(sx, 0.05, 0.18), CFrame.new(cx, 0.03, gz), GRID, Enum.Material.Neon, { Transparency = 0.45, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false })
			end
		end
	end

	-- Pit warning borders + glowing void inside
	for _, h in ipairs(holes) do
		local cx, cz = (h[1] + h[2]) / 2, (h[3] + h[4]) / 2
		local sx, sz = h[2] - h[1], h[4] - h[3]
		part(decor, "PitEdge", Vector3.new(sx + 0.8, 0.12, 0.4), CFrame.new(cx, 0.06, h[3] - 0.2), DANGER, Enum.Material.Neon, DECOR)
		part(decor, "PitEdge", Vector3.new(sx + 0.8, 0.12, 0.4), CFrame.new(cx, 0.06, h[4] + 0.2), DANGER, Enum.Material.Neon, DECOR)
		part(decor, "PitEdge", Vector3.new(0.4, 0.12, sz), CFrame.new(h[1] - 0.2, 0.06, cz), DANGER, Enum.Material.Neon, DECOR)
		part(decor, "PitEdge", Vector3.new(0.4, 0.12, sz), CFrame.new(h[2] + 0.2, 0.06, cz), DANGER, Enum.Material.Neon, DECOR)
		part(decor, "PitGlow", Vector3.new(sx, 0.2, sz), CFrame.new(cx, -14, cz), DANGER, Enum.Material.Neon, { Transparency = 0.55, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false })
	end

	-- Underside rim so the platform reads as floating
	part(decor, "Underside", Vector3.new(2 * H - 6, 4, 2 * H - 6), CFrame.new(0, -floorThick - 2, 0), Color3.fromRGB(12, 14, 26), Enum.Material.Metal, DECOR)
	for _, s in ipairs({ 1, -1 }) do
		part(decor, "RimGlow", Vector3.new(2 * H + 4, 0.4, 0.4), CFrame.new(0, -floorThick, s * (H + 2)), TRIM, Enum.Material.Neon, DECOR)
		part(decor, "RimGlow", Vector3.new(0.4, 0.4, 2 * H + 4), CFrame.new(s * (H + 2), -floorThick, 0), TRIM, Enum.Material.Neon, DECOR)
	end

	-- Perimeter: visible glass walls + invisible tall barriers
	local barrierH = Config.Arena.BarrierHeight
	for _, s in ipairs({ 1, -1 }) do
		part(geo, "Wall", Vector3.new(2 * H + 4, WH, 2), CFrame.new(0, WH / 2, s * (H + 1)), WALL, Enum.Material.Glass, { Transparency = 0.55 })
		part(geo, "Wall", Vector3.new(2, WH, 2 * H + 4), CFrame.new(s * (H + 1), WH / 2, 0), WALL, Enum.Material.Glass, { Transparency = 0.55 })
		part(decor, "WallTrim", Vector3.new(2 * H + 4.2, 0.35, 2.2), CFrame.new(0, WH + 0.1, s * (H + 1)), TRIM, Enum.Material.Neon, DECOR)
		part(decor, "WallTrim", Vector3.new(2.2, 0.35, 2 * H + 4.2), CFrame.new(s * (H + 1), WH + 0.1, 0), TRIM, Enum.Material.Neon, DECOR)
		part(decor, "WallBase", Vector3.new(2 * H + 4.2, 0.3, 2.2), CFrame.new(0, 0.2, s * (H + 1)), TRIM, Enum.Material.Neon, DECOR)
		part(decor, "WallBase", Vector3.new(2.2, 0.3, 2 * H + 4.2), CFrame.new(s * (H + 1), 0.2, 0), TRIM, Enum.Material.Neon, DECOR)
		local barrierProps = { Transparency = 1, CanQuery = false, CastShadow = false }
		part(model, "Barrier", Vector3.new(2 * H + 4, barrierH, 2), CFrame.new(0, WH + barrierH / 2, s * (H + 1)), WALL, nil, barrierProps)
		part(model, "Barrier", Vector3.new(2, barrierH, 2 * H + 4), CFrame.new(s * (H + 1), WH + barrierH / 2, 0), WALL, nil, barrierProps)
	end
	part(model, "Ceiling", Vector3.new(2 * H + 4, 2, 2 * H + 4), CFrame.new(0, WH + barrierH, 0), WALL, nil, { Transparency = 1, CanQuery = false, CastShadow = false })

	-- Tall pillars
	for _, p in ipairs({ { -20, -18 }, { 20, -18 }, { -20, 18 }, { 20, 18 } }) do
		local h = 16
		part(geo, "Pillar", Vector3.new(7, h, 7), CFrame.new(p[1], h / 2, p[2]), PILLAR, Enum.Material.Metal)
		for _, y in ipairs({ 3.5, 11 }) do
			part(decor, "PillarBand", Vector3.new(7.3, 0.6, 7.3), CFrame.new(p[1], y, p[2]), BAND, Enum.Material.Neon, DECOR)
		end
		part(decor, "PillarCap", Vector3.new(7.4, 0.4, 7.4), CFrame.new(p[1], h + 0.2, p[2]), TRIM, Enum.Material.Neon, DECOR)
	end

	-- Low cover walls (jumpable, block gun fire)
	for _, z in ipairs({ -15, 15 }) do
		part(geo, "Cover", Vector3.new(14, 5, 2.5), CFrame.new(0, 2.5, z), Color3.fromRGB(40, 60, 110), Enum.Material.Glass, { Transparency = 0.25 })
		part(decor, "CoverTrim", Vector3.new(14.2, 0.3, 2.7), CFrame.new(0, 5.1, z), TRIM, Enum.Material.Neon, DECOR)
	end

	-- Raised corner blocks
	for _, c in ipairs({ { -1, -1 }, { 1, -1 }, { -1, 1 }, { 1, 1 } }) do
		local cx, cz = c[1] * 44, c[2] * 44
		part(geo, "CornerBlock", Vector3.new(11, 4, 11), CFrame.new(cx, 2, cz), PILLAR, Enum.Material.Metal)
		part(decor, "CornerTrim", Vector3.new(11.2, 0.25, 11.2), CFrame.new(cx, 4.1, cz), BAND, Enum.Material.Neon, DECOR)
	end

	-- Center emblem
	local ring = part(decor, "CenterRing", Vector3.new(0.1, 16, 16), CFrame.new(0, 0.04, 0) * CFrame.Angles(0, 0, math.rad(90)), TRIM, Enum.Material.Neon, DECOR)
	ring.Shape = Enum.PartType.Cylinder
	ring.Transparency = 0.6
	local inner = part(decor, "CenterDisc", Vector3.new(0.12, 14.6, 14.6), CFrame.new(0, 0.05, 0) * CFrame.Angles(0, 0, math.rad(90)), FLOOR, Enum.Material.SmoothPlastic, DECOR)
	inner.Shape = Enum.PartType.Cylinder

	-- Lights
	for _, c in ipairs({ { -1, -1, BAND }, { 1, -1, TRIM }, { -1, 1, TRIM }, { 1, 1, BAND } }) do
		local holder = part(decor, "LightHolder", Vector3.new(1, 1, 1), CFrame.new(c[1] * 30, 26, c[2] * 30), c[3], Enum.Material.Neon, { Transparency = 1, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false })
		local l = Instance.new("PointLight")
		l.Range = 60
		l.Brightness = 1.4
		l.Color = c[3]
		l.Shadows = false
		l.Parent = holder
	end

	-- Spawns (facing the center)
	local spawnPos = { Vector3.new(0, 0, 40), Vector3.new(0, 0, -40), Vector3.new(-46, 0, 14), Vector3.new(46, 0, -14) }
	for i, pos in ipairs(spawnPos) do
		local look = CFrame.lookAt(pos, Vector3.new(0, 0, 0))
		part(spawns, "Spawn" .. i, Vector3.new(4, 0.2, 4), look, TRIM, Enum.Material.Neon, { Transparency = 1, CanCollide = false, CanQuery = false, CanTouch = false })
		part(decor, "SpawnPad", Vector3.new(6, 0.08, 6), CFrame.new(pos + Vector3.new(0, 0.05, 0)), Config.TeamColors[i], Enum.Material.Neon, { Transparency = 0.85, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false })
	end

	local pivot = part(model, "Pivot", Vector3.new(1, 1, 1), CFrame.new(0, 0, 0), TRIM, nil, { Transparency = 1, CanCollide = false, CanQuery = false, CanTouch = false })
	model.PrimaryPart = pivot
	return model
end

-- Lobby showcase at the origin: platform + 3 robot statues on pedestals (facing +Z).
function World.BuildLobby(Config, robotFolder)
	local lobby = Instance.new("Model")
	lobby.Name = "Lobby"
	local disc = part(lobby, "Platform", Vector3.new(3, 70, 70), CFrame.new(0, -1.5, 0) * CFrame.Angles(0, 0, math.rad(90)), FLOOR, Enum.Material.SmoothPlastic, { Reflectance = 0.1 })
	disc.Shape = Enum.PartType.Cylinder
	for i, r in ipairs({ 35.2, 22 }) do
		local ring = part(lobby, "Ring" .. i, Vector3.new(0.2, r * 2, r * 2), CFrame.new(0, 0.02 * i, 0) * CFrame.Angles(0, 0, math.rad(90)), TRIM, Enum.Material.Neon, DECOR)
		ring.Shape = Enum.PartType.Cylinder
		ring.Transparency = 0.5
		local cover = part(lobby, "RingCover" .. i, Vector3.new(0.22, r * 2 - 0.8, r * 2 - 0.8), CFrame.new(0, 0.02 * i + 0.01, 0) * CFrame.Angles(0, 0, math.rad(90)), FLOOR, Enum.Material.SmoothPlastic, DECOR)
		cover.Shape = Enum.PartType.Cylinder
	end
	for i = 0, 11 do
		local a = i / 12 * math.pi * 2
		local pos = Vector3.new(math.cos(a) * 33, 0, math.sin(a) * 33)
		part(lobby, "Post", Vector3.new(1.2, 12, 1.2), CFrame.new(pos + Vector3.new(0, 6, 0)), PILLAR, Enum.Material.Metal)
		part(lobby, "PostGlow", Vector3.new(1.3, 1.5, 1.3), CFrame.new(pos + Vector3.new(0, 12.5, 0)), i % 2 == 0 and TRIM or BAND, Enum.Material.Neon, DECOR)
	end
	local stands = Instance.new("Folder")
	stands.Name = "Stands"
	stands.Parent = lobby
	for i, def in ipairs(Config.Robots) do
		local x = (i - 2) * 14
		local ped = part(stands, "Pedestal" .. def.Id, Vector3.new(2, 9, 9), CFrame.new(x, 1, 0) * CFrame.Angles(0, 0, math.rad(90)), PILLAR, Enum.Material.Metal)
		ped.Shape = Enum.PartType.Cylinder
		local glow = part(stands, "PedGlow" .. def.Id, Vector3.new(0.3, 9.5, 9.5), CFrame.new(x, 1.75, 0) * CFrame.Angles(0, 0, math.rad(90)), def.Neon, Enum.Material.Neon, DECOR)
		glow.Shape = Enum.PartType.Cylinder
		local src = robotFolder:FindFirstChild(def.Id)
		if src then
			local statue = src:Clone()
			statue.Name = "Statue" .. def.Id
			local rootY = statue.Humanoid.HipHeight + statue.HumanoidRootPart.Size.Y / 2
			for _, d in ipairs(statue:GetDescendants()) do
				if d:IsA("Humanoid") or d:IsA("AlignOrientation") then
					d:Destroy()
				elseif d:IsA("BasePart") then
					d.Anchored = true
					d.CanCollide = false
					d.CanQuery = false
				end
			end
			statue:PivotTo(CFrame.new(x, 2 + rootY, 0) * CFrame.Angles(0, math.pi, 0))
			statue.Parent = stands
		end
	end
	local holder = part(lobby, "LobbyLight", Vector3.new(1, 1, 1), CFrame.new(0, 18, 14), TRIM, Enum.Material.Neon, { Transparency = 1, CanCollide = false, CanQuery = false, CanTouch = false })
	local l = Instance.new("PointLight")
	l.Range = 45
	l.Brightness = 2
	l.Color = Color3.fromRGB(180, 210, 255)
	l.Parent = holder
	return lobby
end

function World.SetupLighting()
	local Lighting = game:GetService("Lighting")
	Lighting.ClockTime = 0.5
	Lighting.Brightness = 2
	Lighting.Ambient = Color3.fromRGB(95, 95, 125)
	Lighting.OutdoorAmbient = Color3.fromRGB(120, 125, 165)
	Lighting.ExposureCompensation = 0.25
	Lighting.EnvironmentDiffuseScale = 0.5
	Lighting.EnvironmentSpecularScale = 0.6
	Lighting.GlobalShadows = true
	pcall(function()
		Lighting.Technology = Enum.Technology.Future
	end)
	for _, c in ipairs(Lighting:GetChildren()) do
		if c:IsA("PostEffect") or c:IsA("Atmosphere") or c:IsA("Sky") then
			c:Destroy()
		end
	end
	local bloom = Instance.new("BloomEffect")
	bloom.Intensity = 0.7
	bloom.Size = 28
	bloom.Threshold = 1.4
	bloom.Parent = Lighting
	local cc = Instance.new("ColorCorrectionEffect")
	cc.Contrast = 0.12
	cc.Saturation = 0.15
	cc.TintColor = Color3.fromRGB(235, 240, 255)
	cc.Parent = Lighting
	local atm = Instance.new("Atmosphere")
	atm.Density = 0.28
	atm.Offset = 0.1
	atm.Color = Color3.fromRGB(50, 60, 110)
	atm.Decay = Color3.fromRGB(40, 20, 90)
	atm.Glare = 0
	atm.Haze = 1.2
	atm.Parent = Lighting
	local sky = Instance.new("Sky")
	sky.StarCount = 3000
	sky.CelestialBodiesShown = false
	sky.Parent = Lighting
end

return World
