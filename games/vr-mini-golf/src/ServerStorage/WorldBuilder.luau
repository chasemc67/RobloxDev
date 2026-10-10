-- WorldBuilder: the Lantern Grove world around the holes (world layout only). Run in Edit, after CourseBuilder.Build:
--   tools/world_terrain.py           writes the Terrain from the world map (terrain-4stud.json) via WriteTerrainRows,
--                                    then runs CarveHoles + CheckClearance
--   WorldBuilder.BuildScenery()      workspace.World: walkways/stairs, lantern posts, waterfalls, stream flow, the
--                                    hollow tree stand-in, backdrop (tree line, far hills, mountains), spawn plaza
--   WorldBuilder.ApplyLighting()     warm autumn evening (course.md + world.json sky)
-- Everything in workspace.World is scenery: Anchored, CanCollide/CanTouch false. Walkway/stair/plaza tops keep
-- CanQuery (tag GolfWalkable) so the VR floor and teleport arc can stand on them; nothing else is queryable.
-- Ball play never touches any of it: CarveHoles clears the Terrain over every felt piece and fills the water hazards.
local WorldBuilder = {}

local CollectionService = game:GetService("CollectionService")
local Lighting = game:GetService("Lighting")
local ServerStorage = game:GetService("ServerStorage")
local Terrain = workspace.Terrain
local M = Enum.Material

local function hex(s)
	return Color3.fromHex(s)
end
local P = {
	oak = hex("8A5A33"),
	bark = hex("5B3A22"),
	ember = hex("D2452A"),
	pumpkin = hex("E8862E"),
	gold = hex("F2B632"),
	amber = hex("FFB347"),
	paper = hex("F7C873"),
	moss = hex("7A9A3A"),
	slate = hex("6E7480"),
	foam = hex("E6F6FF"),
	water = hex("4AA3DF"),
	cream = hex("F4E9D2"),
	toadstool = hex("D8392B"),
}

local function layoutModule()
	return require(ServerStorage.CourseData.WorldLayout:Clone())
end

local function new(className, props, parent)
	local inst = Instance.new(className)
	for k, v in props do
		inst[k] = v
	end
	if parent then
		inst.Parent = parent
	end
	return inst
end

-- scenery part: anchored, no collision/touch/query, no shadow for big far pieces
local function vis(name, cf, size, color, material, parent, shape)
	local p = new("Part", {
		Name = name,
		Anchored = true,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Size = size,
		CFrame = cf,
		Color = color,
		Material = material or M.SmoothPlastic,
		TopSurface = Enum.SurfaceType.Smooth,
		BottomSurface = Enum.SurfaceType.Smooth,
	})
	if shape then
		p.Shape = shape
	end
	p.Parent = parent
	return p
end

-- a box between two points (top surface along the line), e.g. walkway boards and handrails
local function span(name, a: Vector3, b: Vector3, width, thick, color, material, parent)
	local mid = (a + b) / 2
	local len = (b - a).Magnitude
	if len < 0.05 then
		return nil
	end
	local cf = CFrame.lookAt(mid, b) * CFrame.new(0, -thick / 2, 0)
	return vis(name, cf, Vector3.new(width, thick, len), color, material, parent)
end

local function walkable(p)
	p.CanQuery = true
	CollectionService:AddTag(p, "GolfWalkable")
	return p
end

------------------------------------------------------------------------------------------------ terrain
-- Writes rows j0 .. j0+n-1 of the world map's 4-stud grid (terrain-4stud.json): heights/water/material indices as
-- comma-separated strings, row-major. Each column is solid up to `height` (top two voxels in the surface material,
-- Rock below so cliffs read as rock), Mud under water, Water from the bed up to the water surface.
local MATS = { [0] = M.Grass, [1] = M.LeafyGrass, [2] = M.Rock, [3] = M.Ground, [4] = M.Water, [5] = M.Sand }
WorldBuilder.Y0 = -12
WorldBuilder.NY = 44 -- y -12 .. 164
function WorldBuilder.WriteTerrainRows(meta, j0, n, hs, ws, ms)
	local cols, cell = meta.cols, meta.cell
	local function nums(s, conv)
		local out = {}
		for v in string.gmatch(s, "[^,]+") do
			table.insert(out, conv(v))
		end
		return out
	end
	local H = nums(hs, tonumber)
	local W = nums(ws, function(v)
		return v ~= "_" and tonumber(v) or false
	end)
	local MI = nums(ms, tonumber)
	local NY, Y0 = WorldBuilder.NY, WorldBuilder.Y0
	local mats, occs = {}, {}
	for i = 1, cols do
		local mx, ox = {}, {}
		mats[i], occs[i] = mx, ox
		for y = 1, NY do
			mx[y], ox[y] = {}, {}
		end
	end
	for j = 1, n do
		for i = 1, cols do
			local k = (j - 1) * cols + i
			local h, w, mi = H[k], W[k], MI[k]
			local surf = MATS[mi] or M.Grass
			local wet = w and w > h + 0.05
			if surf == M.Water then
				surf = M.Mud
			end
			if wet then
				surf = (surf == M.Sand) and M.Sand or M.Mud
			end
			for y = 1, NY do
				local ybot = Y0 + (y - 1) * cell
				-- smooth terrain puts the surface at about (voxel centre + occupancy * cell), so a column's surface
				-- lands at h when occupancy = (h - centre) / cell (measured: bottom-based occupancy sat 2 studs high)
				local centre = ybot + cell / 2
				local occ = math.clamp((h - centre) / cell, 0, 1)
				local mat, o = M.Air, 0
				if occ > 0 then
					mat, o = (h - ybot) <= 2 * cell and surf or M.Rock, occ
					if wet and occ < 0.5 then
						-- the voxel holding the bed surface: water reads better than a half-empty mud cell
						mat, o = M.Water, math.clamp((w - centre) / cell, occ, 1)
					end
				elseif wet and centre < w then
					mat, o = M.Water, math.clamp((w - centre) / cell, 0, 1)
				end
				mats[i][y][j], occs[i][y][j] = mat, o
			end
		end
	end
	local x0, z0 = meta.x0, meta.z0 + (j0 - 1) * cell
	local region = Region3.new(Vector3.new(x0, Y0, z0), Vector3.new(x0 + cols * cell, Y0 + NY * cell, z0 + n * cell))
	Terrain:WriteVoxels(region, cell, mats, occs)
	return "ok"
end

-- Clears the Terrain off every felt piece (+0.6 around, from the felt bottom to 6.5 above), so smoothed voxels
-- never poke through the felt, then fills each water hazard with Terrain water from its bed to its surface.
function WorldBuilder.CarveHoles(course)
	course = course or workspace.Course
	local n = 0
	for _, hole in course:GetChildren() do
		local geo = hole:FindFirstChild("Geometry")
		if not geo then
			continue
		end
		for _, p in geo:GetChildren() do
			if p:IsA("BasePart") and (p.Name == "Felt" or p.Name == "CupPlate") then
				local t = p.Size.Y
				Terrain:FillBlock(p.CFrame * CFrame.new(0, 3.25, 0), Vector3.new(p.Size.X + 1.2, t + 6.5, p.Size.Z + 1.2), M.Air)
				-- wider, from just under the felt top: neighbouring (higher) pads bleed in at the 4-stud voxel scale
				Terrain:FillBlock(p.CFrame * CFrame.new(0, t / 2 - 0.1 + 3.5, 0), Vector3.new(p.Size.X + 4, 7, p.Size.Z + 4), M.Air)
				n += 1
			end
		end
		-- FillBlock(Air) only partly empties voxels that straddle the felt top, and smoothing lets a neighbouring higher
		-- pad bleed over a lower piece (H2 ledge base, H7 slope foot). Cap every voxel near each piece directly so the
		-- terrain surface (about centre + occupancy * 4) stays 0.1 under the piece's lowest top, 2 studs around it.
		for _, p in geo:GetChildren() do
			if p:IsA("BasePart") and (p.Name == "Felt" or p.Name == "CupPlate") then
				WorldBuilder.CapUnder(p, 2, 0.1)
			end
		end
		local hz = hole:FindFirstChild("Hazards")
		for _, h in hz and hz:GetChildren() or {} do
			if h.Name == "Hazard" and h:GetAttribute("HazardType") == "water" then
				local top = h:GetAttribute("SurfaceY")
				local flat = h.CFrame - h.CFrame.Position
				local c = Vector3.new(h.Position.X, top, h.Position.Z)
				Terrain:FillBlock(CFrame.new(c + Vector3.new(0, 3, 0)) * flat, Vector3.new(h.Size.X, 6, h.Size.Z), M.Air)
				Terrain:FillBlock(CFrame.new(c - Vector3.new(0, 1, 0)) * flat, Vector3.new(h.Size.X + 0.4, 2, h.Size.Z + 0.4), M.Water)
				Terrain:FillBlock(CFrame.new(c - Vector3.new(0, 2.5, 0)) * flat, Vector3.new(h.Size.X + 0.4, 1, h.Size.Z + 0.4), M.Mud)
			end
		end
	end
	return n
end

function WorldBuilder.CapUnder(p: BasePart, margin, clearance)
	local cell = 4
	-- lowest point of the top face (sloped pieces: the low end)
	local top = math.huge
	for _, sx in { -1, 1 } do
		for _, sz in { -1, 1 } do
			top = math.min(top, p.CFrame:PointToWorldSpace(Vector3.new(sx * p.Size.X / 2, p.Size.Y / 2, sz * p.Size.Z / 2)).Y)
		end
	end
	local flat = CFrame.new(p.Position) * CFrame.Angles(0, select(2, p.CFrame:ToEulerAnglesYXZ()), 0)
	local r = math.sqrt((p.Size.X / 2 + margin) ^ 2 + (p.Size.Z / 2 + margin) ^ 2)
	local function snap(v, up)
		return (up and math.ceil(v / cell) or math.floor(v / cell)) * cell
	end
	local lo = Vector3.new(snap(p.Position.X - r), snap(top - 12), snap(p.Position.Z - r))
	local hi = Vector3.new(snap(p.Position.X + r, true), snap(top + 12, true), snap(p.Position.Z + r, true))
	local region = Region3.new(lo, hi)
	local mats, occs = Terrain:ReadVoxels(region, cell)
	local size = mats.Size
	local changed = false
	for i = 1, size.X do
		for k = 1, size.Z do
			local cx, cz = lo.X + (i - 0.5) * cell, lo.Z + (k - 0.5) * cell
			local lp = flat:PointToObjectSpace(Vector3.new(cx, p.Position.Y, cz))
			if math.abs(lp.X) <= p.Size.X / 2 + margin and math.abs(lp.Z) <= p.Size.Z / 2 + margin then
				for j = 1, size.Y do
					local cy = lo.Y + (j - 0.5) * cell
					local cap = math.clamp((top - clearance - cy) / cell, 0, 1)
					-- no grass blades (Terrain decoration) poking up through the felt
					if mats[i][j][k] == Enum.Material.Grass then
						mats[i][j][k] = Enum.Material.LeafyGrass
						changed = true
					end
					if occs[i][j][k] > cap then
						occs[i][j][k] = cap
						if cap <= 0 then
							mats[i][j][k] = Enum.Material.Air
						end
						changed = true
					end
				end
			end
		end
	end
	if changed then
		Terrain:WriteVoxels(region, cell, mats, occs)
	end
end

-- Terrain intrusion check: casts down onto every felt piece on a 0.5-stud grid; a Terrain hit above the felt top
-- (minus 0.02) is an intrusion. Also checks the ball corridor inside each hole's Bounds for any solid voxel above
-- the felt (raycasts from 3 studs over the felt down to it).
function WorldBuilder.CheckClearance(course)
	course = course or workspace.Course
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Include
	params.FilterDescendantsInstances = { Terrain }
	params.IgnoreWater = true
	local out = {}
	for _, hole in course:GetChildren() do
		local geo = hole:FindFirstChild("Geometry")
		if not geo then
			continue
		end
		local bad, samples, worst = 0, 0, 0
		for _, p in geo:GetChildren() do
			if p:IsA("BasePart") and (p.Name == "Felt" or p.Name == "CupPlate") then
				local hx, hz = p.Size.X / 2, p.Size.Z / 2
				for x = -hx + 0.1, hx - 0.1, 0.5 do
					for z = -hz + 0.1, hz - 0.1, 0.5 do
						local top = p.CFrame:PointToWorldSpace(Vector3.new(x, p.Size.Y / 2, z))
						samples += 1
						local hit = workspace:Raycast(top + Vector3.new(0, 3, 0), Vector3.new(0, -3.02, 0), params)
						if hit then
							bad += 1
							worst = math.max(worst, hit.Position.Y - top.Y)
						end
					end
				end
			end
		end
		out[hole.Name] = { samples = samples, intrusions = bad, worst = math.floor(worst * 1000) / 1000 }
	end
	return game:GetService("HttpService"):JSONEncode(out)
end

------------------------------------------------------------------------------------------------ props (optional)
-- Imported 3D Model Bot meshes live in ServerStorage.LanternGroveProps.<name> (Model, pivot = prop origin).
local function prop(name)
	local lib = ServerStorage:FindFirstChild("LanternGroveProps")
	local m = lib and lib:FindFirstChild(name)
	return m and m:Clone() or nil
end
WorldBuilder.prop = prop

local function glow(part, range, brightness)
	new("PointLight", { Color = P.amber, Range = range or 8, Brightness = brightness or 0.9, Shadows = false }, part)
end

local function lanternPost(parent, pos: Vector3, faceDir: Vector3?)
	local cf = CFrame.new(pos)
	if faceDir and faceDir.Magnitude > 1e-3 then
		cf = CFrame.lookAt(pos, pos + Vector3.new(faceDir.X, 0, faceDir.Z))
	end
	local m = prop("lantern_post")
	if m then
		m:PivotTo(cf)
		m.Parent = parent
		local g = m:FindFirstChild("lantern_post__Glow", true)
		if g then
			glow(g, 8, 0.9)
		end
		return m
	end
	local post = new("Model", { Name = "LanternPost" }, parent)
	vis("Post", cf * CFrame.new(0, 1.6, 0), Vector3.new(0.35, 3.2, 0.35), P.oak, M.Wood, post)
	vis("Arm", cf * CFrame.new(0, 3.05, -0.4), Vector3.new(0.15, 0.15, 0.9), P.oak, M.Wood, post)
	local paper = vis("Paper", cf * CFrame.new(0, 2.5, -0.75), Vector3.new(0.75, 0.95, 0.75), P.paper, M.SmoothPlastic, post, Enum.PartType.Ball)
	paper.Transparency = 0.1
	local core = vis("Glow", cf * CFrame.new(0, 2.5, -0.75), Vector3.new(0.35, 0.45, 0.35), P.amber, M.Neon, post, Enum.PartType.Ball)
	glow(core, 8, 0.9)
	return post
end

------------------------------------------------------------------------------------------------ walkways
local function buildPaths(layout, folder)
	local f = new("Folder", { Name = "Walkways" }, folder)
	local plank, edge = hex("9C6B3F"), P.bark
	for _, path in layout.paths do
		local m = new("Model", { Name = path.id }, f)
		m:SetAttribute("PathName", path.name)
		local w = path.width or 6
		local handrails = path.id == "p_h2_h3" or path.id == "p_h7_h8"
		for si, seg in path.segments do
			local a, b = Vector3.new(table.unpack(seg.start)), Vector3.new(table.unpack(seg["end"]))
			if seg.type == "on_hole" then
				continue
			end
			local flatDir = Vector3.new(b.X - a.X, 0, b.Z - a.Z)
			if flatDir.Magnitude < 0.05 then
				continue
			end
			flatDir = flatDir.Unit
			local side = Vector3.new(-flatDir.Z, 0, flatDir.X)
			if seg.type == "stairs" then
				-- one block per step: tread `tread`, rising `rise`, down into the graded ground
				local steps, rise, tread = seg.steps, seg.rise, seg.tread or 1.5
				for k = 1, steps do
					local topY = a.Y + k * rise
					local c = a + flatDir * ((k - 0.5) * tread)
					local h = rise + 1.2
					local s = vis("Step", CFrame.lookAt(Vector3.new(c.X, topY - h / 2, c.Z), Vector3.new(c.X, topY - h / 2, c.Z) + flatDir),
						Vector3.new(w, h, tread + 0.05), plank, M.WoodPlanks, m)
					walkable(s)
				end
				if handrails then
					for _, sgn in { -1, 1 } do
						local o = side * sgn * (w / 2 - 0.2)
						span("Handrail", a + o + Vector3.new(0, 3.2, 0), b + o + Vector3.new(0, 3.2, 0), 0.25, 0.25, P.oak, M.Wood, m)
						for k = 0, steps, 3 do
							local c = a + flatDir * (k * tread) + o
							vis("Baluster", CFrame.new(c + Vector3.new(0, a.Y + k * rise - c.Y + 1.6, 0)), Vector3.new(0.25, 3.2, 0.25), P.oak, M.Wood, m)
						end
					end
				end
			elseif seg.type == "landing" then
				local s = span("Landing", a + Vector3.new(0, 0.08, 0), b + Vector3.new(0, 0.08, 0), w, 0.6, plank, M.WoodPlanks, m)
				if s then
					s.Size = Vector3.new(w, 0.6, math.max(s.Size.Z, w * 0.6))
					walkable(s)
				end
			else
				-- walk / ramp: the ground is graded and painted (Ground); edge it with low log kerbs, and lay a thin
				-- board path on top so the route reads from the tees
				local s = span("Path", a + Vector3.new(0, 0.06, 0), b + Vector3.new(0, 0.06, 0), w - 1, 0.3, hex("8C6A45"), M.Ground, m)
				if s then
					walkable(s)
				end
				for _, sgn in { -1, 1 } do
					local o = side * sgn * (w / 2 - 0.25)
					span("Kerb", a + o + Vector3.new(0, 0.3, 0), b + o + Vector3.new(0, 0.3, 0), 0.4, 0.4, edge, M.Wood, m)
				end
			end
		end
	end
	return f
end

------------------------------------------------------------------------------------------------ water
local FOAM_TEX = "rbxasset://textures/particles/smoke_main.dds"

local function beam(parent, a: Vector3, b: Vector3, width, color, transparency, speed, name)
	local holder = vis(name or "BeamHolder", CFrame.new(a), Vector3.new(0.2, 0.2, 0.2), color, M.SmoothPlastic, parent)
	holder.Transparency = 1
	local a0 = new("Attachment", { Position = Vector3.zero }, holder)
	local a1 = new("Attachment", {}, holder)
	a1.WorldPosition = b -- (only once parented: WorldPosition set before that is taken as a local offset)
	return new("Beam", {
		Attachment0 = a0,
		Attachment1 = a1,
		Width0 = width,
		Width1 = width,
		Color = ColorSequence.new(color),
		Transparency = NumberSequence.new(transparency),
		Texture = FOAM_TEX,
		TextureMode = Enum.TextureMode.Wrap,
		TextureLength = 6,
		TextureSpeed = speed,
		LightEmission = 0.35,
		LightInfluence = 0.6,
		FaceCamera = false,
		Segments = 4,
	}, holder)
end

local function buildWater(layout, folder)
	local f = new("Folder", { Name = "Water" }, folder)
	-- waterfalls: two crossing curtains (so they read from any side) + mist at the foot
	for _, wf in layout.waterfalls do
		if string.find(wf.name, "decor") then
			continue -- drawn by a prop on the hole (H6's waterfall_small)
		end
		local m = new("Model", { Name = wf.name }, f)
		local top, bot = Vector3.new(table.unpack(wf.top)), Vector3.new(table.unpack(wf.bottom))
		-- camera-facing ribbons: a blue body and a foam layer streaming down
		local b1 = beam(m, top, bot, wf.width * 0.9, hex("7FC4E8"), 0.2, 4, "Curtain")
		b1.Width1 = wf.width
		b1.FaceCamera = true
		b1.LightEmission = 0.1
		local b2 = beam(m, top, bot, wf.width * 0.7, P.foam, 0.35, 6, "Foam")
		b2.Width1 = wf.width * 0.85
		b2.FaceCamera = true
		b2.LightEmission = 0.25
		local mist = vis("Mist", CFrame.new(bot + Vector3.new(0, 0.5, 0)), Vector3.new(wf.width, 0.5, 2), P.foam, M.SmoothPlastic, m)
		mist.Transparency = 1
		new("ParticleEmitter", {
			Texture = FOAM_TEX,
			Color = ColorSequence.new(P.foam),
			LightEmission = 0.2,
			-- subtle: the falls sit right beside H5 and H7, so the mist must not drift over the greens
			Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, wf.width * 0.12), NumberSequenceKeypoint.new(1, wf.width * 0.3) }),
			Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.75), NumberSequenceKeypoint.new(1, 1) }),
			Lifetime = NumberRange.new(0.8, 1.4),
			Rate = math.clamp(wf.drop * 0.4, 3, 10),
			Speed = NumberRange.new(0.5, 1.5),
			SpreadAngle = Vector2.new(35, 35),
			Acceleration = Vector3.new(0, 0.4, 0),
		}, mist)
	end
	-- stream flow: foam streaks drifting downstream just above the Terrain water surface
	local pts = layout.stream.points
	for k = 1, #pts - 1 do
		local p0, p1 = pts[k], pts[k + 1]
		if math.abs(p1.level - p0.level) > 1.5 then
			continue -- a waterfall: the curtains cover it
		end
		local a = Vector3.new(p0.x, p0.level + 0.08, p0.z)
		local b = Vector3.new(p1.x, p1.level + 0.08, p1.z)
		local bm = beam(f, a, b, math.min(p0.width, p1.width) * 0.5, P.foam, 0.82, 2.2 + (p0.level - p1.level), "Flow")
		bm.LightEmission = 0.1
		local dir = (b - a).Unit
		for _, at in { bm.Attachment0, bm.Attachment1 } do
			-- lie flat on the water
			at.WorldCFrame = CFrame.fromMatrix(at.WorldPosition, dir, Vector3.new(-dir.Z, 0, dir.X))
		end
	end
	-- mill flume: a timber trough with a water strip in it
	local fl = layout.mill_flume
	local fm = new("Model", { Name = "MillFlume" }, f)
	for k = 1, #fl.points - 1 do
		local a, b = Vector3.new(table.unpack(fl.points[k])), Vector3.new(table.unpack(fl.points[k + 1]))
		span("Trough", a + Vector3.new(0, 0.1, 0), b + Vector3.new(0, 0.1, 0), fl.width + 0.6, 0.9, P.oak, M.WoodPlanks, fm)
		local wtr = span("FlumeWater", a + Vector3.new(0, 0.12, 0), b + Vector3.new(0, 0.12, 0), fl.width, 0.1, P.water, M.Glass, fm)
		if wtr then
			wtr.Transparency = 0.25
		end
	end
	return f
end

------------------------------------------------------------------------------------------------ hollow tree
-- Stand-in for 3D Model Bot's world-scale shell (replace by dropping ServerStorage.LanternGroveProps.hollow_tree_world
-- in and rebuilding). Trunk wall annulus with the Heartwood Door, root flare, crown masses around an open oculus.
-- The interior (radius < inner radius, above the floor) stays empty: H9 is played there.
local function buildTree(layout, folder)
	local t = layout.hollow_tree
	local f = new("Model", { Name = "HollowTree" }, folder)
	local c = Vector3.new(t.center[1], t.base_y, t.center[3])
	local shell = prop("hollow_tree_world")
	if shell then
		shell:PivotTo(CFrame.new(c))
		shell.Parent = f
		return f
	end
	f:SetAttribute("StandIn", true)
	local rin, rout, h = t.trunk_inner_radius, t.trunk_outer_radius, t.trunk_height
	local rmid, thick = (rin + rout) / 2, rout - rin
	local N = 44
	local doorA = math.rad(t.doorway.angle_deg)
	local doorHalf = (t.doorway.width / 2) / rmid
	local barkA, barkB = hex("6B4426"), hex("7C5230")
	for k = 0, N - 1 do
		local a = (k + 0.5) * 2 * math.pi / N
		local d = math.abs(((a - doorA + math.pi) % (2 * math.pi)) - math.pi)
		local chord = 2 * math.pi * rmid / N * 1.12
		local dir = Vector3.new(math.cos(a), 0, math.sin(a))
		local p = c + dir * rmid
		local cf = CFrame.lookAt(p, p + dir)
		local col = k % 2 == 0 and barkA or barkB
		local wobble = 1 + 0.08 * math.sin(k * 2.3)
		if d < doorHalf + 0.02 then
			-- doorway: wall only above the arch
			local y0 = t.doorway.height
			vis("Trunk", cf * CFrame.new(0, y0 + (h - y0) / 2, 0), Vector3.new(chord, h - y0, thick * wobble), col, M.Wood, f)
		else
			vis("Trunk", cf * CFrame.new(0, h / 2, 0), Vector3.new(chord, h, thick * wobble), col, M.Wood, f)
		end
		-- bark ridges outside
		if k % 2 == 1 then
			vis("Ridge", cf * CFrame.new(0, h * 0.45, -thick / 2 - 0.8), Vector3.new(2.2, h * 0.9, 2), barkA, M.Wood, f)
		end
	end
	-- door arch trim + lanterns
	local dd = Vector3.new(math.cos(doorA), 0, math.sin(doorA))
	local dp = c + dd * (rout + 0.3)
	local dcf = CFrame.lookAt(dp, dp + dd)
	vis("DoorArch", dcf * CFrame.new(0, t.doorway.height + 0.8, 0), Vector3.new(t.doorway.width + 3, 1.6, 2), P.oak, M.Wood, f)
	for _, s in { -1, 1 } do
		vis("DoorPost", dcf * CFrame.new(s * (t.doorway.width / 2 + 0.9), t.doorway.height / 2, 0), Vector3.new(1.6, t.doorway.height + 1.6, 2), P.oak, M.Wood, f)
		local l = vis("DoorLantern", dcf * CFrame.new(s * (t.doorway.width / 2 + 0.9), 10, -1.6), Vector3.new(1.2, 1.6, 1.2), P.paper, M.Neon, f, Enum.PartType.Ball)
		glow(l, 14, 1.4)
	end
	-- root flare: big roots radiating from the base (skip the door and H8's side, which has its own spec roots)
	for k = 0, 13 do
		local a = k * 2 * math.pi / 14 + 0.11
		local d = math.abs(((a - doorA + math.pi) % (2 * math.pi)) - math.pi)
		if d < 0.45 then
			continue
		end
		local dir = Vector3.new(math.cos(a), 0, math.sin(a))
		local len = t.root_flare_radius - rout + 8
		local p = c + dir * (rout + len / 2 - 4)
		vis("Root", CFrame.lookAt(p, p + dir) * CFrame.new(0, 1.5, 0) * CFrame.Angles(math.rad(-9), 0, 0), Vector3.new(6, 6, len), barkB, M.Wood, f)
	end
	-- crown: big leaf masses on a ring over the trunk top + a high centre mass, leaving the oculus open
	local crownY = c.Y + h
	local cols = { P.gold, P.pumpkin, hex("F2A03A"), P.ember, P.gold, P.pumpkin, hex("E9B949") }
	for k = 0, 6 do
		local a = k * 2 * math.pi / 7 + 0.3
		local r = t.crown.radius_xz * 0.55
		local s = 52 + 10 * math.sin(k * 1.7)
		vis("Crown", CFrame.new(c + Vector3.new(math.cos(a) * r, h + 22 + 8 * math.cos(k * 2.1), math.sin(a) * r)), Vector3.one * s, cols[k + 1], M.Grass, f, Enum.PartType.Ball)
	end
	vis("Crown", CFrame.new(c + Vector3.new(0, h + 62, 0)), Vector3.one * 64, P.gold, M.Grass, f, Enum.PartType.Ball)
	-- light shaft through the oculus onto the heart
	local shaft = vis("Oculus", CFrame.new(c + Vector3.new(0, t.oculus.y - c.Y, 0)), Vector3.new(4, 1, 4), P.amber, M.SmoothPlastic, f)
	shaft.Transparency = 1
	new("SpotLight", { Face = Enum.NormalId.Bottom, Angle = 35, Range = 60, Brightness = 3, Color = hex("FFD9A0"), Shadows = false }, shaft)
	-- warm interior fill (the trunk blocks the sun)
	for k = 0, 3 do
		local a = k * math.pi / 2 + 0.4
		local l = vis("Fill", CFrame.new(c + Vector3.new(math.cos(a) * rin * 0.85, 14, math.sin(a) * rin * 0.85)), Vector3.new(1.4, 1.8, 1.4), P.paper, M.Neon, f, Enum.PartType.Ball)
		glow(l, 40, 1.2)
	end
	return f
end

------------------------------------------------------------------------------------------------ backdrop
local function treeClump(parent, base: Vector3, size: Vector3, colors, seed)
	local rng = Random.new(seed)
	local m = new("Model", { Name = "TreeClump" }, parent)
	local n = 5
	for k = 1, n do
		local off = Vector3.new(rng:NextNumber(-0.32, 0.32) * size.X, 0, rng:NextNumber(-0.32, 0.32) * size.Z)
		local th = size.Y * rng:NextNumber(0.55, 1)
		local cr = size.X * rng:NextNumber(0.32, 0.45)
		local p = base + off
		vis("Trunk", CFrame.new(p + Vector3.new(0, th * 0.3, 0)), Vector3.new(cr * 0.18, th * 0.6, cr * 0.18), P.bark, M.Wood, m).CastShadow = false
		local leaf = vis("Leaves", CFrame.new(p + Vector3.new(0, th - cr * 0.6, 0)), Vector3.one * cr * 2, colors[(k + seed) % #colors + 1], M.Grass, m, Enum.PartType.Ball)
		leaf.CastShadow = false
	end
	return m
end

local function ellipsoid(name, cf, size, color, material, parent)
	-- a block part with a sphere mesh renders as the ellipsoid that fits the part (keeps the real bounds for culling)
	local p = vis(name, cf, Vector3.new(math.min(size.X, 2048), math.min(size.Y, 2048), math.min(size.Z, 2048)), color, material, parent)
	p.CastShadow = false
	new("SpecialMesh", { MeshType = Enum.MeshType.Sphere }, p)
	return p
end

local function mountain(parent, base: Vector3, size: Vector3, yaw, color)
	-- four corner wedges = a pyramid, plus a rounded shoulder; atmosphere does the rest
	local m = new("Model", { Name = "Mountain" }, parent)
	local cf = CFrame.new(base) * CFrame.Angles(0, math.rad(yaw or 0), 0)
	local hx, hz, h = size.X / 2, size.Z / 2, math.min(size.Y, 2000)
	for k = 0, 3 do
		local w = new("CornerWedgePart", {
			Anchored = true,
			CanCollide = false,
			CanQuery = false,
			CanTouch = false,
			CastShadow = false,
			Color = color,
			Material = M.Rock,
			Size = Vector3.new(math.min(hx, 2000), h, math.min(hz, 2000)),
		})
		-- CornerWedge apex is at its -X/+Z top corner... place each quarter so the apexes meet at the centre
		w.CFrame = cf * CFrame.Angles(0, k * math.pi / 2, 0) * CFrame.new(hx / 2, h / 2, -hz / 2) * CFrame.Angles(0, math.pi / 2, 0)
		w.Parent = m
	end
	return m
end

local function buildBackdrop(layout, folder)
	local f = new("Folder", { Name = "Backdrop" }, folder)
	local tl = new("Folder", { Name = "TreeLine" }, f)
	local colorSets = {
		["gold+orange"] = { P.gold, P.pumpkin, hex("F2A03A") },
		["red+orange"] = { P.ember, P.pumpkin, hex("B83A24") },
		["green+gold"] = { P.moss, P.gold, hex("8FA23F") },
		["red+gold"] = { P.ember, P.gold, P.pumpkin },
	}
	local fallback = { P.gold, P.pumpkin, P.ember, P.moss }
	for idx, pc in layout.backdrop.pieces do
		local pos = Vector3.new(table.unpack(pc.pos))
		local size = Vector3.new(table.unpack(pc.size))
		if pc.kind == "tree_line_cluster" then
			local m = treeClump(tl, pos, size, colorSets[pc.colors] or fallback, idx)
			m.Name = pc.id
		elseif pc.kind == "far_forest_hill" then
			local cf = CFrame.new(pos) * CFrame.Angles(0, math.rad(pc.yaw_deg or 0), 0)
			-- muted, darker than the near forest: the atmosphere lightens them into distant autumn hills
			local hill = ellipsoid(pc.id, cf, Vector3.new(size.X, size.Y * 2, size.Z), hex("5E5A2C"), M.Grass, f)
			hill.Color = (idx % 3 == 0) and hex("6A5228") or ((idx % 3 == 1) and hex("525A2A") or hex("704428"))
		elseif pc.kind == "distant_mountain" then
			local m = mountain(f, pos, size, pc.yaw_deg, (idx % 2 == 0) and hex("7C7FA8") or hex("8E8AB4"))
			m.Name = pc.id
		elseif pc.id == "old_lantern_tower" then
			local m = new("Model", { Name = pc.id }, f)
			vis("Tower", CFrame.new(pos + Vector3.new(0, size.Y / 2, 0)), Vector3.new(size.X * 0.7, size.Y, size.Z * 0.7), P.slate, M.Cobblestone, m)
			local l = vis("Lantern", CFrame.new(pos + Vector3.new(0, size.Y + 2.5, 0)), Vector3.new(5, 6, 5), P.amber, M.Neon, m, Enum.PartType.Ball)
			glow(l, 40, 2)
		elseif pc.kind == "background" and string.find(pc.id, "sister_tree") then
			local m = treeClump(f, pos, size, string.find(pc.id, "sw") and colorSets["red+orange"] or colorSets["gold+orange"], idx)
			m.Name = pc.id
		elseif pc.id == "hill_mushroom_houses" then
			local m = new("Model", { Name = pc.id }, f)
			for k = 0, 2 do
				local p = pos + Vector3.new((k - 1) * 9, 0, (k % 2) * 6)
				local s = 7 + k * 2
				vis("Stem", CFrame.new(p + Vector3.new(0, s * 0.35, 0)), Vector3.new(s * 0.6, s * 0.7, s * 0.6), P.cream, M.SmoothPlastic, m)
				vis("Cap", CFrame.new(p + Vector3.new(0, s * 0.85, 0)), Vector3.one * s * 1.2, k == 1 and P.pumpkin or P.toadstool, M.SmoothPlastic, m, Enum.PartType.Ball)
				local win = vis("Window", CFrame.new(p + Vector3.new(0, s * 0.4, s * 0.31)), Vector3.new(1.2, 1.2, 0.2), P.amber, M.Neon, m)
				if k == 1 then
					glow(win, 16, 1)
				end
			end
		elseif pc.id == "mere_dock" then
			local m = new("Model", { Name = pc.id }, f)
			vis("Deck", CFrame.new(pos + Vector3.new(0, 0.6, 0)), Vector3.new(size.Z, 0.5, size.X), hex("9C6B3F"), M.WoodPlanks, m)
			local l = vis("Lantern", CFrame.new(pos + Vector3.new(0, 3, size.X / 2 - 1)), Vector3.new(0.9, 1.2, 0.9), P.paper, M.Neon, m, Enum.PartType.Ball)
			glow(l, 12, 1)
		elseif pc.id == "mere_lantern_boats" then
			local lake = layout.lakes[1]
			local rng = Random.new(7)
			local m = new("Model", { Name = pc.id }, f)
			for k = 1, 8 do
				local a = rng:NextNumber(0, 2 * math.pi)
				local rr = rng:NextNumber(0.2, 0.75)
				local p = Vector3.new(lake.center[1] + math.cos(a) * lake.radii[1] * rr, lake.level + 0.3, lake.center[2] + math.sin(a) * lake.radii[2] * rr)
				vis("Boat", CFrame.new(p) * CFrame.Angles(0, a, 0), Vector3.new(1.2, 0.4, 2.4), P.cream, M.SmoothPlastic, m)
				local l = vis("BoatLantern", CFrame.new(p + Vector3.new(0, 0.8, 0)), Vector3.new(0.7, 0.9, 0.7), P.amber, M.Neon, m, Enum.PartType.Ball)
				if k % 3 == 0 then
					glow(l, 10, 0.8)
				end
			end
		elseif pc.id == "sky_lanterns" then
			local rng = Random.new(11)
			local m = new("Model", { Name = pc.id }, f)
			for k = 1, 24 do
				local a = rng:NextNumber(0, 2 * math.pi)
				local r = rng:NextNumber(60, 120)
				vis("SkyLantern", CFrame.new(pos.X + math.cos(a) * r, rng:NextNumber(150, 280), pos.Z + math.sin(a) * r), Vector3.new(2, 2.6, 2), P.amber, M.Neon, m, Enum.PartType.Ball).CastShadow = false
			end
		end
	end
	return f
end

------------------------------------------------------------------------------------------------ lanterns + plaza
local function buildLanterns(layout, folder)
	local f = new("Folder", { Name = "Lanterns" }, folder)
	-- face each post's lantern toward its walkway: the nearest path segment
	local segs = {}
	for _, path in layout.paths do
		for _, s in path.segments do
			table.insert(segs, { Vector3.new(table.unpack(s.start)), Vector3.new(table.unpack(s["end"])) })
		end
	end
	for _, lp in layout.lanterns.points do
		local pos = Vector3.new(table.unpack(lp.pos))
		local best, bd = nil, math.huge
		for _, s in segs do
			local ab = s[2] - s[1]
			local t = math.clamp((pos - s[1]):Dot(ab) / math.max(ab:Dot(ab), 1e-6), 0, 1)
			local q = s[1] + ab * t
			local d = (Vector3.new(q.X, 0, q.Z) - Vector3.new(pos.X, 0, pos.Z)).Magnitude
			if d < bd then
				best, bd = q, d
			end
		end
		local ground = pos.Y
		local hit = workspace:Raycast(pos + Vector3.new(0, 30, 0), Vector3.new(0, -60, 0), (function()
			local rp = RaycastParams.new()
			rp.FilterType = Enum.RaycastFilterType.Include
			rp.FilterDescendantsInstances = { Terrain }
			rp.IgnoreWater = true
			return rp
		end)())
		if hit then
			ground = hit.Position.Y
		end
		lanternPost(f, Vector3.new(pos.X, ground, pos.Z), best and (best - pos) or nil)
	end
	return f
end

local function buildPlaza(layout, folder)
	local f = new("Model", { Name = "WelcomePlaza" }, folder)
	local sp = layout.spawn.pos
	local c = Vector3.new(sp[1], sp[2], sp[3])
	local pad = vis("Plaza", CFrame.new(c + Vector3.new(0, -0.25, 0)) * CFrame.Angles(0, 0, math.rad(90)), Vector3.new(0.6, 22, 22), hex("B8AFA0"), M.Cobblestone, f, Enum.PartType.Cylinder)
	walkable(pad)
	-- course board facing hole 1
	local look = Vector3.new(layout.spawn.look_at[1], c.Y, layout.spawn.look_at[3])
	local dir = (look - c).Unit
	local bp = c + dir * 7 + Vector3.new(dir.Z, 0, -dir.X) * 6
	local bcf = CFrame.lookAt(bp, bp - dir)
	for _, s in { -1, 1 } do
		vis("BoardPost", bcf * CFrame.new(s * 2.4, 2.2, 0), Vector3.new(0.4, 4.4, 0.4), P.oak, M.Wood, f)
	end
	local board = vis("Board", bcf * CFrame.new(0, 3.6, 0), Vector3.new(5.4, 2.8, 0.3), P.bark, M.WoodPlanks, f)
	local gui = new("SurfaceGui", { Face = Enum.NormalId.Back, CanvasSize = Vector2.new(540, 280), LightInfluence = 0 }, board)
	new("TextLabel", { Size = UDim2.fromScale(1, 0.5), BackgroundTransparency = 1, Text = "Lantern Grove", TextScaled = true, Font = Enum.Font.FredokaOne, TextColor3 = P.paper }, gui)
	new("TextLabel", { Size = UDim2.fromScale(1, 0.4), Position = UDim2.fromScale(0, 0.55), BackgroundTransparency = 1, Text = "9 holes  -  Par 27", TextScaled = true, Font = Enum.Font.FredokaOne, TextColor3 = Color3.new(1, 1, 1) }, gui)
	return f
end

------------------------------------------------------------------------------------------------ build
function WorldBuilder.BuildScenery(layout)
	layout = layout or layoutModule()
	local old = workspace:FindFirstChild("World")
	if old then
		old:Destroy()
	end
	local world = new("Folder", { Name = "World" })
	world.Parent = workspace
	local stats = {}
	stats.paths = #buildPaths(layout, world):GetDescendants()
	stats.water = #buildWater(layout, world):GetDescendants()
	stats.tree = #buildTree(layout, world):GetDescendants()
	stats.backdrop = #buildBackdrop(layout, world):GetDescendants()
	stats.lanterns = #buildLanterns(layout, world):GetChildren()
	buildPlaza(layout, world)
	local lights = 0
	for _, d in workspace:GetDescendants() do
		if d:IsA("Light") then
			lights += 1
		end
	end
	stats.lightsInWorkspace = lights
	stats.parts = #world:GetDescendants()
	return game:GetService("HttpService"):JSONEncode(stats)
end

-- Warm autumn evening (course.md palette; world.json sky: golden-hour sun from the WSW behind the tree).
function WorldBuilder.ApplyLighting()
	pcall(function()
		Lighting.Technology = Enum.Technology.Future
	end)
	Lighting.ClockTime = 17.1
	Lighting.GeographicLatitude = 23
	Lighting.Brightness = 2.4
	Lighting.Ambient = hex("5E4A3A")
	Lighting.OutdoorAmbient = hex("9A7A5A")
	Lighting.ColorShift_Top = hex("FFC27A")
	Lighting.ColorShift_Bottom = hex("3A2A20")
	Lighting.EnvironmentDiffuseScale = 0.7
	Lighting.EnvironmentSpecularScale = 0.5
	Lighting.ShadowSoftness = 0.3
	Lighting.FogColor = hex("E8B27A")
	Lighting.FogStart = 0
	Lighting.FogEnd = 100000 -- Atmosphere does the haze
	local atm = Lighting:FindFirstChildOfClass("Atmosphere") or new("Atmosphere", {}, Lighting)
	atm.Density = 0.32
	atm.Offset = 0.15
	atm.Color = hex("F3C98B")
	atm.Decay = hex("A9645A")
	atm.Glare = 0.4
	atm.Haze = 1.8
	local bloom = Lighting:FindFirstChildOfClass("BloomEffect") or new("BloomEffect", {}, Lighting)
	bloom.Intensity = 0.5
	bloom.Size = 30
	bloom.Threshold = 1.6
	local rays = Lighting:FindFirstChildOfClass("SunRaysEffect") or new("SunRaysEffect", {}, Lighting)
	rays.Intensity = 0.06
	rays.Spread = 0.6
	local cc = Lighting:FindFirstChild("GroveGrade") or new("ColorCorrectionEffect", { Name = "GroveGrade" }, Lighting)
	cc.Saturation = 0.12
	cc.Contrast = 0.06
	cc.TintColor = hex("FFF4E6")
	Terrain.WaterColor = hex("3E8FA8")
	Terrain.WaterTransparency = 0.55
	Terrain.WaterReflectance = 0.6
	Terrain.WaterWaveSize = 0.12
	Terrain.WaterWaveSpeed = 9
	return "ok"
end

return WorldBuilder
