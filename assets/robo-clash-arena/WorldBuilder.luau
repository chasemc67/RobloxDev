-- Robo Clash Arena: builds the Homework Desk arena template (S04), the desk lobby showcase and lighting.
-- Run in Studio edit mode: require(this).BuildArena(Config) -> Model (floor top at y = 0).
-- Arena layout (110 x 110, unchanged from the holo arena): perimeter walls, 4 tall pillars, 2 low cover
-- walls, 4 raised corner blocks, 2 pits at (+-34, 0). Geometry folder = solid + blocks shots.
-- Every Geometry part keeps its gameplay size and is invisible; the desk props that dress it are parented
-- under it (no collide/query) so the camera occlusion fade reaches them. Props are MeshParts cloned from
-- ServerStorage.RoboClashAssets.Meshes.DeskProps (blender/make_props.py, imported with the 3D Importer).
-- Tall props only sit on the +-X sides: players spawn at +-Z, so the camera always looks from a Z side.

local ServerStorage = game:GetService("ServerStorage")

local World = {}

local WOOD = Color3.fromRGB(196, 142, 92)
local WOOD_DARK = Color3.fromRGB(150, 100, 62)
local FLOOR_WOOD = Color3.fromRGB(150, 104, 70)
local WALLPAPER = Color3.fromRGB(240, 226, 200)
local TRIM = Color3.fromRGB(250, 248, 240)
local HAZARD_Y = Color3.fromRGB(255, 205, 40)
local HAZARD_K = Color3.fromRGB(40, 36, 40)
local DANGER = Color3.fromRGB(255, 70, 50)
local WARM = Color3.fromRGB(255, 214, 160)
local WHITE = Color3.new(1, 1, 1)

local RED = Color3.fromRGB(230, 62, 58)
local BLUE = Color3.fromRGB(60, 120, 230)
local GREEN = Color3.fromRGB(70, 190, 92)
local YELLOW = Color3.fromRGB(250, 200, 40)
local ORANGE = Color3.fromRGB(255, 140, 40)
local PURPLE = Color3.fromRGB(150, 92, 220)

-- S04 palette (concepts/s04-palette.md)
local S_MAT = Color3.fromHex("8BAE7A")
local S_YELLOW = Color3.fromHex("FED960")
local S_RED = Color3.fromHex("E45D51")
local S_BLUE = Color3.fromHex("4359AF")
local S_PINK = Color3.fromHex("F98E98")
local S_ORANGE = Color3.fromHex("F79E5C")
local S_DESK = Color3.fromHex("FAD3B0")
local S_GREEN = Color3.fromRGB(96, 178, 92)

-- Tileable textures from concepts/textures (uploaded image assets)
local TEX_WOOD = "rbxassetid://78503721249412"
local TEX_MAT = "rbxassetid://94217611860656"
local MAT_TILE = 60
local MAT_TINT = Color3.fromRGB(165, 192, 132)

local DESK_Y = -0.3 -- desk top; the cutting mat (floor) sits 0.3 above it
local ROOM_Y = -62 -- room floor under the desk

local DECOR = { CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false }
local SOLID_DECOR = { CanCollide = false, CanQuery = false, CanTouch = false }
local HIDDEN = { Transparency = 1, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false }

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

local function texture(p: BasePart, id: string, tile: number, tint: Color3?, face: Enum.NormalId?, offU: number?, offV: number?)
	local t = Instance.new("Texture")
	t.Texture = id
	t.Face = face or Enum.NormalId.Top
	t.StudsPerTileU = tile
	t.StudsPerTileV = tile
	t.OffsetStudsU = offU or 0
	t.OffsetStudsV = offV or 0
	t.Color3 = tint or Color3.new(1, 1, 1)
	t.Parent = p
	return t
end

local function cylY(parent, name, diameter, height, cf, color, material, props)
	local c = part(parent, name, Vector3.new(height, diameter, diameter), cf * CFrame.Angles(0, 0, math.rad(90)), color, material, props)
	c.Shape = Enum.PartType.Cylinder
	return c
end

----------------------------------------------------------------------------------------------
-- Desk props (MeshParts). ORIGIN = the base point each prop was modeled around in make_props.py,
-- so `anchor` is where that base point goes (on the surface, y = bottom of the prop).
----------------------------------------------------------------------------------------------
local ORIGIN = {
	PencilLong = Vector3.new(0, 0, 0),
	PencilShort = Vector3.new(-30, 0, 24),
	PencilRed = Vector3.new(20, 0, 24),
	Crayon = Vector3.new(-40, 0, 46),
	Ruler = Vector3.new(0, 0, -26),
	Brick2x2 = Vector3.new(40, 0, -46),
	Brick2x4 = Vector3.new(60, 0, -46),
	Eraser = Vector3.new(-10, 0, -46),
	DeskLamp = Vector3.new(-80, 0, 0),
	DeskLampGlow = Vector3.new(-80, 0, 0),
	BookCover = Vector3.new(40, 0, 30),
	BookPages = Vector3.new(40, 0, 30),
	Notebook = Vector3.new(80, 0, 30),
	PencilCup = Vector3.new(80, 0, -10),
	Star = Vector3.new(-60, 0, -30),
}

local propsFolder
local function props()
	if not propsFolder then
		local a = ServerStorage:FindFirstChild("RoboClashAssets")
		propsFolder = a and a:FindFirstChild("Meshes") and a.Meshes:FindFirstChild("DeskProps")
		assert(propsFolder, "missing ServerStorage.RoboClashAssets.Meshes.DeskProps (import export/deskprops.fbx)")
	end
	return propsFolder
end

-- opts: color, scale (number | Vector3), name, glow, solid (cast shadow), props (extra properties)
local function prop(parent, name, anchor: CFrame, opts)
	opts = opts or {}
	local src = props():FindFirstChild(name, true) :: MeshPart
	assert(src, "missing desk prop " .. name)
	local scale = opts.scale or 1
	if typeof(scale) == "number" then
		scale = Vector3.one * scale
	end
	local p = src:Clone()
	p:ClearAllChildren()
	p.Name = opts.name or name
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CollisionFidelity = Enum.CollisionFidelity.Box
	p.Material = opts.glow and Enum.Material.Neon or Enum.Material.SmoothPlastic
	p.CastShadow = opts.shadow ~= false and not opts.glow
	p.Color = opts.color or WHITE
	p.Size = src.Size * scale
	p.CFrame = anchor * CFrame.new((src.Position - ORIGIN[name]) * scale)
	if opts.props then
		for k, v in pairs(opts.props) do
			(p :: any)[k] = v
		end
	end
	p.Parent = parent
	return p
end

local function book(parent, anchor: CFrame, color: Color3, scale, name: string?)
	prop(parent, "BookCover", anchor, { color = color, scale = scale, name = name })
	prop(parent, "BookPages", anchor, { scale = scale, name = name })
end

local function bookStack(parent, base: CFrame, colors, scale)
	scale = scale or 1
	local s = typeof(scale) == "number" and Vector3.one * scale or scale
	local y = 0
	for i, c in ipairs(colors) do
		local yaw = math.rad(((i * 37) % 23) - 11)
		book(parent, base * CFrame.new(0, y, 0) * CFrame.Angles(0, yaw, 0), c, s)
		y += 5 * s.Y
	end
	return y
end

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

-- Intervals of [a, b] along one axis not covered by holes that span `at` on the other axis.
local function freeSpans(a, b, at, holes, axis)
	local cuts = {}
	for _, h in ipairs(holes) do
		local lo, hi, olo, ohi
		if axis == "x" then
			lo, hi, olo, ohi = h[1], h[2], h[3], h[4]
		else
			lo, hi, olo, ohi = h[3], h[4], h[1], h[2]
		end
		if at > olo - 0.01 and at < ohi + 0.01 then
			table.insert(cuts, { lo, hi })
		end
	end
	table.sort(cuts, function(u, v)
		return u[1] < v[1]
	end)
	local out, cur = {}, a
	for _, c in ipairs(cuts) do
		if c[1] > cur then
			table.insert(out, { cur, math.min(c[1], b) })
		end
		cur = math.max(cur, c[2])
	end
	if cur < b then
		table.insert(out, { cur, b })
	end
	return out
end

----------------------------------------------------------------------------------------------
-- Room + desk (shared by arena and lobby)
----------------------------------------------------------------------------------------------
local function buildDesk(parent, x0, x1, z0, z1, holes)
	local thick = 4
	for i, r in ipairs(subtractHoles(x0, x1, z0, z1, holes or {})) do
		local sx, sz = r[2] - r[1], r[4] - r[3]
		local d = part(parent, "Desk" .. i, Vector3.new(sx, thick, sz), CFrame.new((r[1] + r[2]) / 2, DESK_Y - thick / 2, (r[3] + r[4]) / 2), S_DESK, Enum.Material.SmoothPlastic, SOLID_DECOR)
		texture(d, TEX_WOOD, 48, nil, Enum.NormalId.Top, (r[1] - x0) % 48, (r[3] - z0) % 48)
	end
	-- rounded front/back lip + legs
	for _, z in ipairs({ z0, z1 }) do
		part(parent, "DeskLip", Vector3.new(x1 - x0, thick + 0.6, 1.2), CFrame.new((x0 + x1) / 2, DESK_Y - thick / 2, z), WOOD_DARK, Enum.Material.Wood, SOLID_DECOR)
	end
	local legH = DESK_Y - thick - ROOM_Y
	for _, x in ipairs({ x0 + 8, x1 - 8 }) do
		for _, z in ipairs({ z0 + 8, z1 - 8 }) do
			part(parent, "DeskLeg", Vector3.new(8, legH, 8), CFrame.new(x, ROOM_Y + legH / 2, z), WOOD_DARK, Enum.Material.Wood, SOLID_DECOR)
		end
	end
end

local function buildRoom(parent, halfX, halfZ, windowsZ)
	local h = 210
	part(parent, "RoomFloor", Vector3.new(halfX * 2, 2, halfZ * 2), CFrame.new(0, ROOM_Y - 1, 0), FLOOR_WOOD, Enum.Material.WoodPlanks, SOLID_DECOR)
	part(parent, "Rug", Vector3.new(halfX * 1.1, 0.3, halfZ * 1.0), CFrame.new(0, ROOM_Y + 0.15, 0), Color3.fromRGB(120, 170, 200), Enum.Material.Fabric, SOLID_DECOR)
	for _, s in ipairs({ -1, 1 }) do
		part(parent, "RoomWall", Vector3.new(halfX * 2, h, 2), CFrame.new(0, ROOM_Y + h / 2, s * halfZ), WALLPAPER, Enum.Material.SmoothPlastic, SOLID_DECOR)
		part(parent, "RoomWall", Vector3.new(2, h, halfZ * 2), CFrame.new(s * halfX, ROOM_Y + h / 2, 0), WALLPAPER, Enum.Material.SmoothPlastic, SOLID_DECOR)
		part(parent, "Baseboard", Vector3.new(halfX * 2, 6, 3), CFrame.new(0, ROOM_Y + 3, s * (halfZ - 0.5)), TRIM, nil, SOLID_DECOR)
		part(parent, "Baseboard", Vector3.new(3, 6, halfZ * 2), CFrame.new(s * (halfX - 0.5), ROOM_Y + 3, 0), TRIM, nil, SOLID_DECOR)
	end
	-- windows (bright sky panes) on the Z walls, the ones the battle camera faces
	for _, s in ipairs(windowsZ or { -1, 1 }) do
		local z = s * (halfZ - 1.2)
		local cy = ROOM_Y + 120
		for _, x in ipairs({ -70, 70 }) do
			part(parent, "WindowPane", Vector3.new(60, 70, 0.4), CFrame.new(x, cy, z), Color3.fromRGB(176, 222, 255), Enum.Material.Neon, DECOR)
			part(parent, "WindowFrame", Vector3.new(64, 4, 1.6), CFrame.new(x, cy + 36, z), TRIM, nil, DECOR)
			part(parent, "WindowFrame", Vector3.new(64, 4, 1.6), CFrame.new(x, cy - 36, z), TRIM, nil, DECOR)
			part(parent, "WindowFrame", Vector3.new(4, 76, 1.6), CFrame.new(x - 32, cy, z), TRIM, nil, DECOR)
			part(parent, "WindowFrame", Vector3.new(4, 76, 1.6), CFrame.new(x + 32, cy, z), TRIM, nil, DECOR)
			part(parent, "WindowFrame", Vector3.new(2.5, 70, 1.4), CFrame.new(x, cy, z), TRIM, nil, DECOR)
			part(parent, "WindowFrame", Vector3.new(60, 2.5, 1.4), CFrame.new(x, cy, z), TRIM, nil, DECOR)
		end
		-- corkboard with pinned notes between the windows
		local cork = part(parent, "Corkboard", Vector3.new(50, 40, 1), CFrame.new(0, cy - 5, z), Color3.fromRGB(196, 150, 100), Enum.Material.Fabric, DECOR)
		local notes = { YELLOW, Color3.fromRGB(255, 160, 200), Color3.fromRGB(150, 220, 255), Color3.fromRGB(180, 240, 150), WHITE }
		for i = 1, 7 do
			local nx = -18 + ((i * 13) % 36)
			local ny = -12 + ((i * 7) % 24)
			part(parent, "Note", Vector3.new(9, 9, 0.2), cork.CFrame * CFrame.new(nx, ny, -s * 0.6) * CFrame.Angles(0, 0, math.rad(((i * 17) % 20) - 10)), notes[(i - 1) % #notes + 1], nil, DECOR)
		end
	end
end

----------------------------------------------------------------------------------------------
-- Arena
----------------------------------------------------------------------------------------------
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
	local room = Instance.new("Folder")
	room.Name = "Room"
	room.Parent = model

	local holes = {
		{ -40, -28, -6, 6 },
		{ 28, 40, -6, 6 },
	}

	-- Play mat (the playable floor): mint grid texture tinted toward the S04 sage, aligned across the pit cut-outs
	local floorThick = 3
	for i, r in ipairs(subtractHoles(-H, H, -H, H, holes)) do
		local sx, sz = r[2] - r[1], r[4] - r[3]
		local cx, cz = (r[1] + r[2]) / 2, (r[3] + r[4]) / 2
		local fl = part(geo, "Floor" .. i, Vector3.new(sx, floorThick, sz), CFrame.new(cx, -floorThick / 2, cz), S_MAT, Enum.Material.SmoothPlastic)
		texture(fl, TEX_MAT, MAT_TILE, MAT_TINT, Enum.NormalId.Top, (r[1] + H) % MAT_TILE, (r[3] + H) % MAT_TILE)
	end
	-- a few brighter guide lines so distances still read from the battle camera
	for _, g in ipairs({ -30, 0, 30 }) do
		for _, sp in ipairs(freeSpans(-H, H, g, holes, "z")) do
			part(decor, "GridX", Vector3.new(0.3, 0.04, sp[2] - sp[1]), CFrame.new(g, 0.03, (sp[1] + sp[2]) / 2), WHITE, nil, { Transparency = 0.45, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false })
		end
		for _, sp in ipairs(freeSpans(-H, H, g, holes, "x")) do
			part(decor, "GridZ", Vector3.new(sp[2] - sp[1], 0.04, 0.3), CFrame.new((sp[1] + sp[2]) / 2, 0.03, g), WHITE, nil, { Transparency = 0.45, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false })
		end
	end

	-- Pits: holes cut through mat and desk, hazard-tape border, dark liner and a red glow below
	for _, h in ipairs(holes) do
		local cx, cz = (h[1] + h[2]) / 2, (h[3] + h[4]) / 2
		local sx, sz = h[2] - h[1], h[4] - h[3]
		local seg = 1.5
		local k = 0
		local function tape(x0, z0, dx, dz, n, alongX)
			for i = 0, n - 1 do
				k += 1
				local pos = Vector3.new(x0 + dx * (i + 0.5), 0.07, z0 + dz * (i + 0.5))
				local size = alongX and Vector3.new(seg, 0.12, 1.1) or Vector3.new(1.1, 0.12, seg)
				part(decor, "PitEdge", size, CFrame.new(pos), k % 2 == 0 and HAZARD_Y or HAZARD_K, nil, DECOR)
			end
		end
		local nx, nz = math.floor((sx + 2.2) / seg + 0.5), math.floor((sz + 2.2) / seg + 0.5)
		tape(h[1] - 1.1, h[3] - 0.55, (sx + 2.2) / nx, 0, nx, true)
		tape(h[1] - 1.1, h[4] + 0.55, (sx + 2.2) / nx, 0, nx, true)
		tape(h[1] - 0.55, h[3], 0, sz / nz, nz, false)
		tape(h[2] + 0.55, h[3], 0, sz / nz, nz, false)
		local depth = 4.6
		part(decor, "PitLiner", Vector3.new(sx, depth, 0.3), CFrame.new(cx, -depth / 2, h[3] + 0.15), Color3.fromRGB(70, 46, 32), nil, DECOR)
		part(decor, "PitLiner", Vector3.new(sx, depth, 0.3), CFrame.new(cx, -depth / 2, h[4] - 0.15), Color3.fromRGB(70, 46, 32), nil, DECOR)
		part(decor, "PitLiner", Vector3.new(0.3, depth, sz), CFrame.new(h[1] + 0.15, -depth / 2, cz), Color3.fromRGB(70, 46, 32), nil, DECOR)
		part(decor, "PitLiner", Vector3.new(0.3, depth, sz), CFrame.new(h[2] - 0.15, -depth / 2, cz), Color3.fromRGB(70, 46, 32), nil, DECOR)
		part(decor, "PitGlow", Vector3.new(sx, 0.2, sz), CFrame.new(cx, -14, cz), DANGER, Enum.Material.Neon, { Transparency = 0.45, CanCollide = false, CanQuery = false, CanTouch = false, CastShadow = false })
	end

	-- Desk under the mat (with the same holes) and the room around it
	buildDesk(room, -165, 165, -125, 125, holes)
	buildRoom(room, 240, 215)

	-- Perimeter: invisible collision walls (unchanged) dressed as the S04 playset fence: knee-high toy blocks
	-- in red/blue/yellow/green with contrasting connector pegs, round posts at the corners.
	local barrierH = Config.Arena.BarrierHeight
	local FENCE_H = 4
	local segs = 8
	local segLen = (2 * H + 2) / segs
	local fenceCols = { S_RED, S_BLUE, S_YELLOW, S_GREEN }
	for si, s in ipairs({ 1, -1 }) do
		local wz = part(geo, "Wall", Vector3.new(2 * H + 4, WH, 2), CFrame.new(0, WH / 2, s * (H + 1)), WHITE, nil, { Transparency = 1 })
		local wx = part(geo, "Wall", Vector3.new(2, WH, 2 * H + 4), CFrame.new(s * (H + 1), WH / 2, 0), WHITE, nil, { Transparency = 1 })
		for i = 1, segs do
			local t = -H - 1 + (i - 0.5) * segLen
			local cA = fenceCols[(i + si * 2 - 1) % 4 + 1]
			local cB = fenceCols[(i + si * 2) % 4 + 1]
			local bscale = Vector3.new((segLen - 1.4) / 14, FENCE_H / 5.33, 2.2 / 7)
			prop(wz, "Brick2x4", CFrame.new(t, 0, s * (H + 1)), { scale = bscale, color = cA, name = "Fence" })
			prop(wx, "Brick2x4", CFrame.new(s * (H + 1), 0, t) * CFrame.Angles(0, math.rad(90), 0), { scale = bscale, color = cB, name = "Fence" })
			if i < segs then
				local e = -H - 1 + i * segLen
				local peg = i % 2 == 0 and S_YELLOW or S_BLUE
				part(wz, "Fence", Vector3.new(1.4, FENCE_H + 0.6, 2.8), CFrame.new(e, (FENCE_H + 0.6) / 2, s * (H + 1)), peg, nil, SOLID_DECOR)
				part(wx, "Fence", Vector3.new(2.8, FENCE_H + 0.6, 1.4), CFrame.new(s * (H + 1), (FENCE_H + 0.6) / 2, e), peg, nil, SOLID_DECOR)
			end
		end
		local barrierProps = { Transparency = 1, CanQuery = false, CastShadow = false }
		part(model, "Barrier", Vector3.new(2 * H + 4, barrierH, 2), CFrame.new(0, WH + barrierH / 2, s * (H + 1)), WHITE, nil, barrierProps)
		part(model, "Barrier", Vector3.new(2, barrierH, 2 * H + 4), CFrame.new(s * (H + 1), WH + barrierH / 2, 0), WHITE, nil, barrierProps)
	end
	part(model, "Ceiling", Vector3.new(2 * H + 4, 2, 2 * H + 4), CFrame.new(0, WH + barrierH, 0), WHITE, nil, { Transparency = 1, CanQuery = false, CastShadow = false })
	-- round corner posts (the far pair carry orange pennants)
	for i, c in ipairs({ { -1, -1 }, { 1, -1 }, { 1, 1 }, { -1, 1 } }) do
		local pc = CFrame.new(c[1] * (H + 1), 0, c[2] * (H + 1))
		local body = i % 2 == 0 and S_BLUE or S_RED
		cylY(decor, "WallTrim", 5, 5.4, pc * CFrame.new(0, 2.7, 0), body, nil, SOLID_DECOR)
		cylY(decor, "WallTrim", 5.3, 0.8, pc * CFrame.new(0, 4.2, 0), S_YELLOW, nil, SOLID_DECOR)
		cylY(decor, "WallTrim", 3.6, 0.7, pc * CFrame.new(0, 5.75, 0), i % 2 == 0 and S_YELLOW or S_ORANGE, nil, SOLID_DECOR)
		if c[2] < 0 then
			cylY(decor, "Pennant", 0.4, 8, pc * CFrame.new(0, 10, 0), S_YELLOW, nil, SOLID_DECOR)
			local flag = Instance.new("WedgePart")
			flag.Name = "Pennant"
			flag.Anchored = true
			flag.Size = Vector3.new(0.2, 2.4, 4)
			flag.CFrame = pc * CFrame.new(0, 12.6, -c[1] * 2.1) * CFrame.Angles(0, c[1] > 0 and math.pi or 0, math.rad(180))
			flag.Color = S_ORANGE
			flag.Material = Enum.Material.SmoothPlastic
			flag.CanCollide, flag.CanQuery, flag.CanTouch = false, false, false
			flag.Parent = decor
		end
	end

	-- Tall pillars (2 robots tall): -X pair = the blue tunnel building, +X pair = the red fort.
	-- Collision boxes are unchanged; the toy dressing is parented to them so the occlusion fade covers it.
	for pi, p in ipairs({ { -20, -18 }, { 20, -18 }, { -20, 18 }, { 20, 18 } }) do
		local h = 16
		local pillar = part(geo, "Pillar", Vector3.new(7, h, 7), CFrame.new(p[1], h / 2, p[2]), WHITE, nil, { Transparency = 1 })
		local blue = p[1] < 0
		local body = blue and S_BLUE or S_RED
		for i = 0, 2 do
			local shade = i == 1 and body:Lerp(WHITE, 0.08) or body
			prop(pillar, "Brick2x2", CFrame.new(p[1], i * 16 / 3, p[2]), { name = "Block", color = shade })
		end
		-- tunnel arch on the faces toward +-Z: yellow ring with a dark opening, sunk into the floor
		for _, fz in ipairs({ 1, -1 }) do
			-- local +X of `face` points to world -Z, so "outward" is -fz along local X
			local face = CFrame.new(p[1], 0.5, p[2] + fz * 3.52) * CFrame.Angles(0, math.rad(90), 0)
			local ring = part(pillar, "Arch", Vector3.new(0.12, 5.2, 5.2), face, S_YELLOW, nil, SOLID_DECOR)
			ring.Shape = Enum.PartType.Cylinder
			local holeP = part(pillar, "Arch", Vector3.new(0.12, 3.8, 3.8), face * CFrame.new(-fz * 0.06, 0, 0), Color3.fromRGB(40, 34, 40), nil, DECOR)
			holeP.Shape = Enum.PartType.Cylinder
		end
		-- roof toppers: trees on the blue building, crayons and a pennant on the red fort
		local top = CFrame.new(p[1], h + 0.6, p[2])
		if blue then
			cylY(pillar, "Tree", 1, 1.8, top * CFrame.new(0, 0.9, 0), Color3.fromRGB(150, 96, 60), nil, SOLID_DECOR)
			local leaf = Color3.fromRGB(86, 176, 90)
			for k, o in ipairs({ { 0, 2.6, 0, 3.6 }, { 0, 4.3, 0, 2.7 }, { 0, 5.6, 0, 1.7 } }) do
				local b = part(pillar, "Tree", Vector3.new(o[4], o[4] * 0.75, o[4]), top * CFrame.new(o[1], o[2], o[3]), leaf:Lerp(WHITE, k * 0.04), nil, SOLID_DECOR)
				b.Shape = Enum.PartType.Ball
			end
		else
			for k, c in ipairs({ S_RED, S_GREEN, S_GREEN }) do
				local a = math.rad(k * 120 + pi * 20)
				prop(pillar, "Crayon", top * CFrame.new(math.cos(a) * 1.3, 4.1, math.sin(a) * 1.3) * CFrame.Angles(0, 0, math.rad(90)), { scale = 0.3, color = c, name = "Crayon" })
			end
		end
	end

	-- Low cover walls = pink erasers (jumpable, block gun fire)
	for i, z in ipairs({ -15, 15 }) do
		local cover = part(geo, "Cover", Vector3.new(14, 5, 2.5), CFrame.new(0, 2.5, z), WHITE, nil, { Transparency = 1 })
		prop(cover, "Eraser", CFrame.new(0, 0, z) * CFrame.Angles(0, i == 1 and 0 or math.pi, 0), { name = "Eraser", color = S_PINK:Lerp(WHITE, 0.35) })
	end

	-- Raised corner blocks (same footprint/height): sticky-note cubes, grey toy crates with blue panels, a blue block
	local kinds = { "Sticky", "Crate", "Crate", "Block" }
	for i, c in ipairs({ { -1, -1 }, { 1, -1 }, { -1, 1 }, { 1, 1 } }) do
		local cx, cz = c[1] * 44, c[2] * 44
		local blockPart = part(geo, "CornerBlock", Vector3.new(11, 4, 11), CFrame.new(cx, 2, cz), WHITE, nil, { Transparency = 1 })
		local kind = kinds[i]
		if kind == "Sticky" then
			local layers = { S_GREEN, S_BLUE, S_PINK, S_YELLOW }
			for k, col in ipairs(layers) do
				local lh = k == #layers and 1.6 or 0.8
				local y0 = (k - 1) * 0.8
				part(blockPart, "Pad", Vector3.new(11, lh, 11), CFrame.new(cx, y0 + lh / 2, cz) * CFrame.Angles(0, math.rad((k % 2) * 2 - 1), 0), col, nil, SOLID_DECOR)
			end
		elseif kind == "Crate" then
			local grey = Color3.fromRGB(128, 132, 140)
			part(blockPart, "Crate", Vector3.new(11, 4, 11), CFrame.new(cx, 2, cz), grey, nil, SOLID_DECOR)
			for _, f in ipairs({ { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } }) do
				local pos = Vector3.new(cx + f[1] * 5.52, 2, cz + f[2] * 5.52)
				local size = f[1] ~= 0 and Vector3.new(0.1, 2.6, 8.6) or Vector3.new(8.6, 2.6, 0.1)
				part(blockPart, "CratePanel", size, CFrame.new(pos), S_BLUE, nil, DECOR)
			end
			part(blockPart, "CratePanel", Vector3.new(8.6, 0.1, 8.6), CFrame.new(cx, 4.02, cz), grey:Lerp(Color3.new(0, 0, 0), 0.15), nil, DECOR)
		else
			part(blockPart, "Block", Vector3.new(11, 4, 11), CFrame.new(cx, 2, cz), S_BLUE, nil, SOLID_DECOR)
			for _, sx in ipairs({ -2.6, 2.6 }) do
				for _, sz in ipairs({ -2.6, 2.6 }) do
					cylY(blockPart, "Stud", 3, 0.7, CFrame.new(cx + sx, 4.35, cz + sz), S_BLUE:Lerp(WHITE, 0.06), nil, SOLID_DECOR)
				end
			end
		end
	end

	-- Center emblem: blue disc in a yellow ring with a gold star
	local ring = cylY(decor, "CenterRing", 20, 0.1, CFrame.new(0, 0.05, 0), S_YELLOW, nil, DECOR)
	ring.Transparency = 0
	local disc = cylY(decor, "CenterRingInner", 18.4, 0.1, CFrame.new(0, 0.08, 0), S_BLUE, nil, DECOR)
	disc.Transparency = 0
	prop(decor, "Star", CFrame.new(0, 0.12, 0), { name = "CenterDisc", color = S_YELLOW, shadow = false })

	-- Desk dressing outside the walls. -X: lamp + book stack + pencil cup. +X: notebook, books, toy bricks.
	-- +-Z (camera sides): only flat things.
	local lampBase = CFrame.new(-H - 30, DESK_Y, -26)
	prop(decor, "DeskLamp", lampBase, { name = "Lamp" })
	local bulb = prop(decor, "DeskLampGlow", lampBase, { name = "LampBulb", glow = true })
	local tilt = math.rad(28.8)
	local spotHolder = part(decor, "LampSpot", Vector3.new(1, 1, 1), CFrame.lookAt(bulb.Position, bulb.Position + Vector3.new(math.sin(tilt), -math.cos(tilt), 0)), WARM, nil, HIDDEN)
	local spot = Instance.new("SpotLight")
	spot.Face = Enum.NormalId.Front
	spot.Angle = 75
	spot.Range = 60
	spot.Brightness = 2.2
	spot.Color = WARM
	spot.Shadows = true
	spot.Parent = spotHolder
	local glowL = Instance.new("PointLight")
	glowL.Color = WARM
	glowL.Range = 18
	glowL.Brightness = 1.2
	glowL.Parent = bulb

	bookStack(decor, CFrame.new(-H - 34, DESK_Y, 34), { RED, BLUE, GREEN, YELLOW })
	bookStack(decor, CFrame.new(-H - 30, DESK_Y, 80) * CFrame.Angles(0, math.rad(20), 0), { PURPLE, ORANGE })
	local cup = CFrame.new(-H - 18, DESK_Y, 64)
	prop(decor, "PencilCup", cup)
	for i, n in ipairs({ "PencilShort", "PencilRed", "PencilShort" }) do
		local a = math.rad(i * 120)
		-- standing tip-up in the cup: local +X (tip) -> up, base point at the pencil's middle
		prop(decor, n, cup * CFrame.new(math.cos(a) * 1.6, 20, math.sin(a) * 1.6) * CFrame.Angles(math.sin(a) * 0.15, 0, math.rad(90) + math.cos(a) * 0.15))
	end
	prop(decor, "Notebook", CFrame.new(H + 30, DESK_Y, -30) * CFrame.Angles(0, math.rad(-12), 0))
	bookStack(decor, CFrame.new(H + 34, DESK_Y, 38) * CFrame.Angles(0, math.rad(-8), 0), { BLUE, YELLOW, RED })
	prop(decor, "Brick2x4", CFrame.new(H + 18, DESK_Y, 78) * CFrame.Angles(0, math.rad(30), 0), { color = BLUE })
	prop(decor, "Brick2x2", CFrame.new(H + 26, DESK_Y, 88) * CFrame.Angles(0, math.rad(-15), 0), { color = RED })
	prop(decor, "Brick2x2", CFrame.new(H + 26, DESK_Y + 6.2 - 0.9, 88) * CFrame.Angles(0, math.rad(5), 0), { color = YELLOW })
	-- camera sides: flat stuff only
	prop(decor, "PencilShort", CFrame.new(30, DESK_Y, H + 16) * CFrame.Angles(0, math.rad(18), 0))
	prop(decor, "Crayon", CFrame.new(-34, DESK_Y, H + 14) * CFrame.Angles(0, math.rad(-25), 0), { color = GREEN })
	prop(decor, "Crayon", CFrame.new(-22, DESK_Y, H + 22) * CFrame.Angles(0, math.rad(-8), 0), { color = ORANGE })
	-- lying on its side: 5-stud height -> along Z, 2.7 thickness -> up
	prop(decor, "Eraser", CFrame.new(60, DESK_Y + 1.35, -H - 16) * CFrame.Angles(math.rad(90), 0, 0) * CFrame.new(0, -2.55, 0))
	prop(decor, "PencilRed", CFrame.new(-36, DESK_Y, -H - 18) * CFrame.Angles(0, math.rad(-30), 0))
	for i, c in ipairs({ YELLOW, Color3.fromRGB(255, 160, 200), Color3.fromRGB(150, 220, 255) }) do
		part(decor, "StickyNote", Vector3.new(9, 0.12, 9), CFrame.new(-8 + i * 11, DESK_Y + 0.06 + i * 0.02, H + 16 + (i % 2) * 6) * CFrame.Angles(0, math.rad(i * 14 - 20), 0), c, nil, DECOR)
	end
	part(decor, "Paper", Vector3.new(34, 0.08, 44), CFrame.new(10, DESK_Y + 0.04, -H - 26) * CFrame.Angles(0, math.rad(6), 0), Color3.fromRGB(252, 250, 244), nil, DECOR)

	-- Soft warm fill from above so the mat reads bright from the battle camera
	for _, c in ipairs({ { -1, 0 }, { 1, 0 } }) do
		local holder = part(decor, "LightHolder", Vector3.new(1, 1, 1), CFrame.new(c[1] * 28, 34, c[2]), WARM, nil, HIDDEN)
		local l = Instance.new("PointLight")
		l.Range = 60
		l.Brightness = 0.7
		l.Color = WARM
		l.Shadows = false
		l.Parent = holder
	end

	-- Spawns (facing the center)
	local spawnPos = { Vector3.new(0, 0, 40), Vector3.new(0, 0, -40), Vector3.new(-46, 0, 14), Vector3.new(46, 0, -14) }
	for i, pos in ipairs(spawnPos) do
		local look = CFrame.lookAt(pos, Vector3.new(0, 0, 0))
		part(spawns, "Spawn" .. i, Vector3.new(4, 0.2, 4), look, WHITE, Enum.Material.Neon, { Transparency = 1, CanCollide = false, CanQuery = false, CanTouch = false })
		local pad = cylY(decor, "SpawnPad", 6.5, 0.06, CFrame.new(pos + Vector3.new(0, 0.04, 0)), Config.TeamColors[i], nil, DECOR)
		pad.Transparency = 0.35
	end

	local pivot = part(model, "Pivot", Vector3.new(1, 1, 1), CFrame.new(0, 0, 0), WHITE, nil, { Transparency = 1, CanCollide = false, CanQuery = false, CanTouch = false })
	model.PrimaryPart = pivot
	return model
end

----------------------------------------------------------------------------------------------
-- Lobby: the three robots on book pedestals on a desk, in a sunny bedroom (statues face +Z).
----------------------------------------------------------------------------------------------
function World.BuildLobby(Config, robotFolder)
	local lobby = Instance.new("Model")
	lobby.Name = "Lobby"
	local room = Instance.new("Folder")
	room.Name = "Room"
	room.Parent = lobby
	buildDesk(room, -80, 80, -55, 55)
	part(lobby, "Platform", Vector3.new(160, 0.4, 110), CFrame.new(0, DESK_Y - 0.2, 0), WOOD, Enum.Material.WoodPlanks, { Transparency = 1, CanQuery = false })
	buildRoom(room, 150, 130)
	-- cutting mat under the statues
	local mat = part(lobby, "Mat", Vector3.new(60, 0.3, 30), CFrame.new(0, DESK_Y + 0.15, 1), S_MAT, nil, SOLID_DECOR)
	texture(mat, TEX_MAT, 30, MAT_TINT)

	local stands = Instance.new("Folder")
	stands.Name = "Stands"
	stands.Parent = lobby
	local pedScale = Vector3.new(0.4, 0.4, 0.31)
	for i, def in ipairs(Config.Robots) do
		local x = (i - 2) * 14
		-- pedestal: a book in the robot's colour, top at y = 2
		local base = CFrame.new(x, DESK_Y + 0.3, 0)
		prop(stands, "BookCover", base, { scale = pedScale, color = def.Secondary, name = "Pedestal" .. def.Id })
		prop(stands, "BookPages", base, { scale = pedScale, name = "PedestalPages" .. def.Id })
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

	-- desk dressing behind/around the statues (kept inside the title camera orbit, below its height)
	local lampBase = CFrame.new(-36, DESK_Y, -18) * CFrame.Angles(0, math.rad(-20), 0)
	prop(lobby, "DeskLamp", lampBase, { name = "Lamp" })
	local bulb = prop(lobby, "DeskLampGlow", lampBase, { name = "LampBulb", glow = true })
	local glowL = Instance.new("PointLight")
	glowL.Color = WARM
	glowL.Range = 30
	glowL.Brightness = 1.5
	glowL.Parent = bulb
	-- standing books along the back: thickness along X, height up, spine facing the camera (+Z)
	local stand = CFrame.fromMatrix(Vector3.zero, Vector3.new(0, 0, -1), Vector3.new(-1, 0, 0))
	local bs = 0.55
	for i, c in ipairs({ RED, BLUE, YELLOW, GREEN, PURPLE, ORANGE, BLUE }) do
		local center = Vector3.new(-2 + i * 5.4 * bs * 1.05, DESK_Y + 17 * bs, -19)
		book(lobby, CFrame.new(center) * stand * CFrame.new(0, -2.5 * bs, 0), c, bs)
	end
	local cup = CFrame.new(-22, DESK_Y, -16)
	prop(lobby, "PencilCup", cup)
	prop(lobby, "Brick2x4", CFrame.new(30, DESK_Y, 14) * CFrame.Angles(0, math.rad(25), 0), { color = RED })
	prop(lobby, "Brick2x2", CFrame.new(36, DESK_Y, 8) * CFrame.Angles(0, math.rad(-10), 0), { color = YELLOW })
	prop(lobby, "Crayon", CFrame.new(-30, DESK_Y, 16) * CFrame.Angles(0, math.rad(30), 0), { color = BLUE })
	prop(lobby, "PencilShort", CFrame.new(40, DESK_Y, -12) * CFrame.Angles(0, math.rad(-70), 0))
	prop(lobby, "Notebook", CFrame.new(-60, DESK_Y, 26) * CFrame.Angles(0, math.rad(15), 0))

	local holder = part(lobby, "LobbyLight", Vector3.new(1, 1, 1), CFrame.new(0, 18, 14), WARM, nil, HIDDEN)
	local l = Instance.new("PointLight")
	l.Range = 45
	l.Brightness = 0.6
	l.Color = WARM
	l.Parent = holder
	World.LightStatues(lobby, Config)
	return lobby
end

-- Showcase lighting for the select screen: warm key spotlight from the camera side, a soft rim light
-- in the robot's neon colour and a round paper-sticker backdrop so silhouettes read against the room.
-- Safe to re-run: replaces the previous StatueLights folder.
function World.LightStatues(lobby, Config)
	local old = lobby:FindFirstChild("StatueLights")
	if old then
		old:Destroy()
	end
	local folder = Instance.new("Folder")
	folder.Name = "StatueLights"
	folder.Parent = lobby
	for i, def in ipairs(Config.Robots) do
		local x = (i - 2) * 14
		local keyPos = Vector3.new(x, 15, 11)
		local key = part(folder, "Key" .. def.Id, Vector3.new(1, 1, 1), CFrame.lookAt(keyPos, Vector3.new(x, 5, 0)), WARM, nil, HIDDEN)
		local spot = Instance.new("SpotLight")
		spot.Face = Enum.NormalId.Front
		spot.Angle = 50
		spot.Range = 24
		spot.Brightness = 0.9
		spot.Color = Color3.fromRGB(255, 236, 210)
		spot.Shadows = false
		spot.Parent = key
		local rimPos = Vector3.new(x, 9, -4.5)
		local rim = part(folder, "Rim" .. def.Id, Vector3.new(1, 1, 1), CFrame.lookAt(rimPos, Vector3.new(x, 6, 2)), def.Neon, nil, HIDDEN)
		local rl = Instance.new("SpotLight")
		rl.Face = Enum.NormalId.Front
		rl.Angle = 80
		rl.Range = 14
		rl.Brightness = 1.4
		rl.Color = def.Neon
		rl.Shadows = false
		rl.Parent = rim
		-- Backdrop: round sticker with a white border, standing behind the statue.
		local haloCF = CFrame.new(x, 7.4, -7) * CFrame.Angles(0, math.rad(90), 0)
		-- Backdrop: round sticker (white border, darker robot-colour face) so light shells read against it
		local back = def.Backdrop or def.Secondary:Lerp(Color3.new(0, 0, 0), 0.4)
		local hoop = part(folder, "Halo" .. def.Id, Vector3.new(0.2, 10, 10), haloCF, Color3.fromRGB(250, 246, 238), Enum.Material.SmoothPlastic, DECOR)
		hoop.Shape = Enum.PartType.Cylinder
		local face = part(folder, "HaloFace" .. def.Id, Vector3.new(0.25, 9.3, 9.3), haloCF, back, Enum.Material.SmoothPlastic, DECOR)
		face.Shape = Enum.PartType.Cylinder
		local inner = part(folder, "HaloRing" .. def.Id, Vector3.new(0.3, 7.9, 7.9), haloCF, back:Lerp(WHITE, 0.25), Enum.Material.SmoothPlastic, DECOR)
		inner.Shape = Enum.PartType.Cylinder
		local innerFace = part(folder, "HaloInner" .. def.Id, Vector3.new(0.35, 7.5, 7.5), haloCF, back, Enum.Material.SmoothPlastic, DECOR)
		innerFace.Shape = Enum.PartType.Cylinder
	end
end

function World.SetupLighting()
	local Lighting = game:GetService("Lighting")
	Lighting.ClockTime = 14.2
	Lighting.GeographicLatitude = 35
	Lighting.Brightness = 1.9
	Lighting.Ambient = Color3.fromRGB(140, 122, 104)
	Lighting.OutdoorAmbient = Color3.fromRGB(170, 152, 128)
	Lighting.ColorShift_Top = Color3.fromRGB(255, 226, 186)
	Lighting.ColorShift_Bottom = Color3.fromRGB(120, 90, 60)
	Lighting.ExposureCompensation = -0.2
	Lighting.EnvironmentDiffuseScale = 0.6
	Lighting.EnvironmentSpecularScale = 0.4
	Lighting.GlobalShadows = true
	Lighting.ShadowSoftness = 0.35
	pcall(function()
		Lighting.Technology = Enum.Technology.Future
	end)
	for _, c in ipairs(Lighting:GetChildren()) do
		if c:IsA("PostEffect") or c:IsA("Atmosphere") or c:IsA("Sky") then
			c:Destroy()
		end
	end
	local bloom = Instance.new("BloomEffect")
	bloom.Intensity = 0.45
	bloom.Size = 24
	bloom.Threshold = 1.6
	bloom.Parent = Lighting
	local cc = Instance.new("ColorCorrectionEffect")
	cc.Contrast = 0.08
	cc.Saturation = 0.04
	cc.TintColor = Color3.fromRGB(255, 246, 234)
	cc.Parent = Lighting
	local atm = Instance.new("Atmosphere")
	atm.Density = 0.18
	atm.Offset = 0
	atm.Color = Color3.fromRGB(255, 236, 210)
	atm.Decay = Color3.fromRGB(240, 210, 170)
	atm.Glare = 0
	atm.Haze = 0.6
	atm.Parent = Lighting
	local sky = Instance.new("Sky")
	sky.CelestialBodiesShown = false
	sky.StarCount = 0
	sky.Parent = Lighting
end

return World
