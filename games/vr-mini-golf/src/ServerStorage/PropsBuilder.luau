-- PropsBuilder: puts 3D Model Bot's Lantern Grove meshes on the course. Run in Edit (command bar / MCP):
--   local PB = require(game.ServerStorage.PropsBuilder:Clone())
--   PB.PrepareLibrary()   -- once, after importing models/library/lg_lib_*.fbx with the 3D Importer: moves every prop
--                         -- into ServerStorage.LanternGroveProps.<prop> (Model, pivot = the prop's origin at 0,0,0),
--                         -- applies the manifest materials and makes every part pure decoration
--   PB.Place()            -- (re)places all props on workspace.Course: HoleN/Decor/Props (static) and, for moving
--                         -- parts, a visual welded to the mover's physics root (HoleN/Movers/Mover_<id>/PropVisual)
-- Data: ServerStorage.CourseData.PropPlacements (tools/props_to_lua.py from models/manifest.json). Positions are
-- hole-local; each hole's frame is its HoleOrigin/HoleYaw (world layout or flat), so props follow the holes.
-- Decoration never touches ball play: Anchored (or massless + welded), CanCollide/CanTouch/CanQuery false.
local PropsBuilder = {}

local ServerStorage = game:GetService("ServerStorage")
local HttpService = game:GetService("HttpService")
local Terrain = workspace.Terrain

local LIB_NAME = "LanternGroveProps"
local MAX_DRESSING_LIGHTS = 6 -- per hole, on top of the hero lanterns (phone performance)
local SKIP_PROPS = {
	-- the hole's tee sign (part-built, shows number + name + par) stays; the mesh sign only shows the number
	tee_sign_h01 = true, tee_sign_h02 = true, tee_sign_h03 = true, tee_sign_h04 = true, tee_sign_h05 = true,
	tee_sign_h06 = true, tee_sign_h07 = true, tee_sign_h08 = true, tee_sign_h09 = true,
	-- the H9 hollow tree is the world-scale tree now; this smaller one becomes a background tree (world layout)
	hollow_tree = true,
	-- water: Terrain water in the world layout
	water_surface = true,
}

-- Treeline cards: the 3D Importer flattens their PNG alpha, so the alpha-cut texture (models/textures/card_*.png,
-- uploaded 2026-10-10 with the Studio MCP upload_image) goes on as a SurfaceAppearance with AlphaMode Transparency.
local CARD_TEXTURES = {
	treeline_card_red = "rbxassetid://79137228052052",
	treeline_card_gold = "rbxassetid://119241826373121",
}

-- hero meshes that stand in for part-built CourseBuilder visuals (hidden, not deleted: a rebuild recreates them)
local REPLACES = {
	["^cup_flag_h"] = { "Flag", "FlagPole" },
	["^h5_respawn_stone$"] = { "RespawnStone" },
}

local function data()
	return require(ServerStorage.CourseData.PropPlacements:Clone())
end

local function decorate(p: BasePart)
	p.Anchored = true
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Massless = true
	pcall(function()
		p.CollisionFidelity = Enum.CollisionFidelity.Box
	end)
end

local function meshKey(name)
	-- importer/Blender suffixes: "<prop>__<Material>", "<prop>__<Material>_tag", ".001"
	name = string.gsub(name, "%.%d+$", "")
	return name
end

-- Moves the imported library models into ServerStorage.LanternGroveProps, one Model per prop, pivot at its origin.
-- The origin is recovered from the manifest (bbox centre relative to the origin), so it doesn't matter where the
-- importer put the bundle. Also checks the import scale (lantern_large must be ~2.12 studs tall).
function PropsBuilder.PrepareLibrary(sources)
	local d = data()
	local lib = ServerStorage:FindFirstChild(LIB_NAME) or Instance.new("Folder")
	lib.Name = LIB_NAME
	lib.Parent = ServerStorage
	sources = sources or {}
	if #sources == 0 then
		for bundle in d.library do
			local m = workspace:FindFirstChild(bundle, true) or ServerStorage:FindFirstChild(bundle, true)
			if m then
				table.insert(sources, m)
			end
		end
	end
	local report = { props = 0, parts = 0, missing = {}, scale = {}, unknownMeshes = 0, turned = {} }
	-- The importer may turn the whole bundle about Y (Studio's "Front" vs the FBX's -Z forward: the 2026-10-10 import
	-- came in rotated 180 degrees). Detect it from one prop's grid cell and undo it about the bundle's origin.
	for _, src in sources do
		local offsets = d.library[src.Name]
		if not offsets then
			continue
		end
		for name, off in offsets do
			local m = src:FindFirstChild(name, true)
			local info = d.props[name]
			if m and info then
				local cf = m:GetBoundingBox()
				local want = Vector3.new(off[1], 0, off[3]) + Vector3.new(table.unpack(info.center))
				local best, bestYaw = math.huge, 0
				for _, yaw in { 0, 90, 180, 270 } do
					local got = CFrame.Angles(0, math.rad(yaw), 0) * cf.Position
					local e = (Vector3.new(got.X, 0, got.Z) - Vector3.new(want.X, 0, want.Z)).Magnitude
					if e < best then
						best, bestYaw = e, yaw
					end
				end
				if bestYaw ~= 0 then
					src:PivotTo(CFrame.Angles(0, math.rad(bestYaw), 0) * src:GetPivot())
				end
				report.turned[src.Name] = bestYaw
				break
			end
		end
	end
	for name, info in d.props do
		-- find the prop's root anywhere in the imported bundles
		local root
		for _, src in sources do
			-- a bundle holds many props; a single-prop FBX import is a Model named after the prop itself
			root = src.Name == name and src or src:FindFirstChild(name, true)
			if root then
				break
			end
		end
		if not root then
			if not lib:FindFirstChild(name) then
				table.insert(report.missing, name)
			end
			continue
		end
		local parts = {}
		if root:IsA("BasePart") then
			table.insert(parts, root)
		end
		for _, x in root:GetDescendants() do
			if x:IsA("BasePart") then
				table.insert(parts, x)
			end
		end
		if #parts == 0 then
			table.insert(report.missing, name)
			continue
		end
		local old = lib:FindFirstChild(name)
		if old then
			old:Destroy()
		end
		local model = Instance.new("Model")
		model.Name = name
		for _, p in parts do
			p.Parent = model
			local key = meshKey(p.Name)
			-- flat manifest colours everywhere, except the treeline cards: their alpha-cut texture IS the shape
			local card = string.find(key, "__Card") ~= nil
			if p:IsA("MeshPart") and not card then
				for _, sa in p:GetChildren() do
					if sa:IsA("SurfaceAppearance") then
						sa:Destroy()
					end
				end
				p.TextureID = ""
			elseif card then
				for _, sa in p:GetChildren() do
					if sa:IsA("SurfaceAppearance") then
						sa:Destroy()
					end
				end
				if p:IsA("MeshPart") and CARD_TEXTURES[name] then
					p.TextureID = ""
					local sa = Instance.new("SurfaceAppearance")
					sa.ColorMap = CARD_TEXTURES[name]
					sa.AlphaMode = Enum.AlphaMode.Transparency
					sa.Parent = p
				end
				report.cards = (report.cards or 0) + 1
			end
			local spec = d.parts[key] or d.parts[(string.gsub(key, "_[%a]+$", ""))]
			if spec and card then
				-- textured: keep the texture's own colours (Color tints a MeshPart texture)
				p.Color = Color3.new(1, 1, 1)
				p.CastShadow = false
			elseif spec then
				p.Color = Color3.fromHex(spec.color)
				p.Material = Enum.Material[spec.material] or Enum.Material.SmoothPlastic
				p.Transparency = spec.transparency or 0
			else
				report.unknownMeshes += 1
			end
			decorate(p)
			report.parts += 1
		end
		-- measured bbox vs manifest -> scale check + origin
		local cf, size = model:GetBoundingBox()
		local want = Vector3.new(table.unpack(info.bbox))
		local k = size.Y / math.max(want.Y, 1e-3)
		-- (flat props, e.g. decals 0.01 thick, come in at Studio's minimum part thickness: no height check)
		if want.Y > 0.3 and math.abs(k - 1) > 0.05 then
			-- importer unit mismatch (FBX header says metres): undo it
			model:ScaleTo(1 / k)
			cf, size = model:GetBoundingBox()
			table.insert(report.scale, string.format("%s x%.3f", name, k))
		end
		-- single-file imports (no library grid): fit the importer's turn about Y + the origin from the per-mesh centres
		-- (the 3D Importer turns these 180 degrees too); bundles: origin from the whole-prop bbox centre
		local fitted = false
		if not root:FindFirstAncestorWhichIsA("Model") or not d.library[(root:FindFirstAncestorWhichIsA("Model") :: Model).Name] then
			local best, bestYaw, bestT = math.huge, 0, Vector3.zero
			for _, yaw in { 0, 90, 180, 270 } do
				local rot = CFrame.Angles(0, math.rad(yaw), 0)
				local sum, n = Vector3.zero, 0
				for _, p in parts do
					local ps = d.parts[meshKey(p.Name)]
					if ps and ps.center then
						sum += p.Position - rot * Vector3.new(table.unpack(ps.center))
						n += 1
					end
				end
				if n >= 2 then
					local t = sum / n
					local err = 0
					for _, p in parts do
						local ps = d.parts[meshKey(p.Name)]
						if ps and ps.center then
							err += (p.Position - (t + rot * Vector3.new(table.unpack(ps.center)))).Magnitude
						end
					end
					if err / n < best then
						best, bestYaw, bestT = err / n, yaw, t
					end
				end
			end
			if best < 0.05 then
				local toLocal = (CFrame.new(bestT) * CFrame.Angles(0, math.rad(bestYaw), 0)):Inverse()
				for _, p in parts do
					p.CFrame = toLocal * p.CFrame
				end
				model.WorldPivot = CFrame.new()
				report.turned[name] = bestYaw
				fitted = true
			end
		end
		if not fitted then
			local origin = cf.Position - Vector3.new(table.unpack(info.center))
			model.WorldPivot = CFrame.new(origin)
			model:PivotTo(CFrame.new())
		end
		model:SetAttribute("Tris", info.tris)
		model:SetAttribute("Kind", info.kind)
		model.Parent = lib
		report.props += 1
	end
	for _, src in sources do
		if #src:GetDescendants() == 0 or not src:FindFirstChildWhichIsA("BasePart", true) then
			src:Destroy()
		end
	end
	local ll = lib:FindFirstChild("lantern_large")
	if ll then
		local _, s = ll:GetBoundingBox()
		report.lanternLargeHeight = math.floor(s.Y * 1000 + 0.5) / 1000
	end
	return HttpService:JSONEncode(report)
end

------------------------------------------------------------------------------------------------ placing
local function holeCF(hole)
	return CFrame.new(hole:GetAttribute("HoleOrigin")) * CFrame.Angles(0, math.rad(hole:GetAttribute("HoleYaw") or 0), 0)
end

-- non-uniform scale in the prop's own frame (props are built axis-aligned around their origin)
local function scaleModel(model: Model, s: Vector3)
	local pivot = model:GetPivot()
	for _, p in model:GetDescendants() do
		if p:IsA("BasePart") then
			local lp = pivot:ToObjectSpace(p.CFrame)
			local pos = lp.Position * s
			local rot = lp - lp.Position
			-- size scales along the part's own axes mapped from the model axes (exact for axis-aligned parts)
			local ax = rot:VectorToWorldSpace(Vector3.xAxis)
			local ay = rot:VectorToWorldSpace(Vector3.yAxis)
			local az = rot:VectorToWorldSpace(Vector3.zAxis)
			local function f(a)
				return math.abs(a.X) * s.X + math.abs(a.Y) * s.Y + math.abs(a.Z) * s.Z
			end
			p.Size = p.Size * Vector3.new(f(ax), f(ay), f(az))
			p.CFrame = pivot * (CFrame.new(pos) * rot)
		end
	end
end

local function instance(lib, name, cf, scale, scaleZTo, bbox)
	local src = lib:FindFirstChild(name)
	if not src then
		return nil
	end
	local m = src:Clone()
	m:PivotTo(CFrame.new())
	if type(scale) == "number" and math.abs(scale - 1) > 1e-3 then
		m:ScaleTo(scale)
	elseif type(scale) == "table" then
		scaleModel(m, Vector3.new(scale[1], scale[2], scale[3]))
	end
	if scaleZTo and bbox then
		scaleModel(m, Vector3.new(1, 1, scaleZTo / bbox[3]))
	end
	m:PivotTo(cf)
	return m
end

local function addGlow(model, range, brightness)
	for _, p in model:GetDescendants() do
		if p:IsA("BasePart") and p.Material == Enum.Material.Neon and not p:FindFirstChildOfClass("PointLight") then
			local l = Instance.new("PointLight")
			l.Color = Color3.fromHex("FFB347")
			l.Range = range or 8
			l.Brightness = brightness or 0.9
			l.Shadows = false
			l.Parent = p
			return true
		end
	end
	return false
end

-- PointLight with the given {range, brightness, color3} on the model's first Neon part (or existing PointLight)
local function setLight(model, spec)
	local light = model:FindFirstChildWhichIsA("PointLight", true)
	if not light then
		for _, p in model:GetDescendants() do
			if p:IsA("BasePart") and p.Material == Enum.Material.Neon then
				light = Instance.new("PointLight")
				light.Parent = p
				break
			end
		end
	end
	if not light then
		return false
	end
	light.Color = spec.color3 and Color3.fromRGB(table.unpack(spec.color3)) or Color3.fromHex("FFA957")
	light.Range = spec.range or 16
	light.Brightness = spec.brightness or 2
	light.Shadows = false
	return true
end

-- world-layout keep-outs for the set dressing (it was authored around each hole on its own)
local function worldKeepouts(course)
	local wl = ServerStorage.CourseData:FindFirstChild("WorldLayout")
	if not (course:GetAttribute("WorldLayout") and wl) then
		return nil
	end
	local layout = require(wl:Clone())
	local segs = {}
	for _, path in layout.paths do
		for _, s in path.segments do
			if s.type ~= "on_hole" then
				table.insert(segs, { Vector3.new(s.start[1], 0, s.start[3]), Vector3.new(s["end"][1], 0, s["end"][3]), (path.width or 6) / 2 })
			end
		end
	end
	local t = layout.hollow_tree
	return {
		segs = segs,
		tree = Vector3.new(t.center[1], 0, t.center[3]),
		treeIn = t.trunk_inner_radius,
		treeOut = t.trunk_outer_radius,
		spawn = Vector3.new(layout.spawn.pos[1], 0, layout.spawn.pos[3]),
	}
end

-- is any felt piece of `hole` within r (flat distance) of p?
local function overFelt(hole, p: Vector3, r)
	for _, f in hole.Geometry:GetChildren() do
		if f:IsA("BasePart") and (f.Name == "Felt" or f.Name == "CupPlate") then
			local lp = f.CFrame:PointToObjectSpace(Vector3.new(p.X, f.Position.Y, p.Z))
			local dx = math.max(math.abs(lp.X) - f.Size.X / 2, 0)
			local dz = math.max(math.abs(lp.Z) - f.Size.Z / 2, 0)
			if dx * dx + dz * dz < r * r then
				return true
			end
		end
	end
	return false
end

local groundParams = RaycastParams.new()
groundParams.FilterType = Enum.RaycastFilterType.Include
groundParams.FilterDescendantsInstances = { Terrain }
groundParams.IgnoreWater = false

-- Places everything. Returns per-hole counts (placed / skipped by reason).
function PropsBuilder.Place(course)
	course = course or workspace.Course
	local d = data()
	local lib = ServerStorage:FindFirstChild(LIB_NAME)
	assert(lib, "run PropsBuilder.PrepareLibrary() first")
	local ko = worldKeepouts(course)
	local report = {}
	local holes = {}
	for _, h in course:GetChildren() do
		local n = h:GetAttribute("HoleNumber")
		if n then
			holes[n] = h
		end
	end

	-- clear the previous run + the part placeholders
	for _, h in holes do
		local decor = h:FindFirstChild("Decor")
		for _, a in decor and decor:GetChildren() or {} do
			if a.Name == "Props" then
				a:Destroy()
			else
				local ph = a:FindFirstChild("Placeholder")
				if ph then
					ph:Destroy()
				end
			end
		end
		for _, mv in h.Movers:GetChildren() do
			local pv = mv:FindFirstChild("PropVisual")
			if pv then
				pv:Destroy()
			end
		end
	end

	local function otherHoleNear(n, p: Vector3, r)
		for m, h in holes do
			if m ~= n then
				local b = h:FindFirstChild("Bounds")
				if b then
					local lp = b.CFrame:PointToObjectSpace(p)
					local hs = b.Size / 2
					if math.abs(lp.X) < hs.X + r and math.abs(lp.Z) < hs.Z + r then
						return true
					end
				end
			end
		end
		return false
	end
	local function nearPath(p: Vector3, r)
		for _, s in ko.segs do
			local a, b = s[1], s[2]
			local ab = b - a
			local q = Vector3.new(p.X, 0, p.Z)
			local t = math.clamp((q - a):Dot(ab) / math.max(ab:Dot(ab), 1e-6), 0, 1)
			if (a + ab * t - q).Magnitude < s[3] + r + 0.3 then
				return true
			end
		end
		return false
	end

	for n, h in holes do
		local cfH = holeCF(h)
		local rep = { hero = 0, moving = 0, dressing = 0, skipped = {} }
		report["Hole" .. n] = rep
		local function skip(why)
			rep.skipped[why] = (rep.skipped[why] or 0) + 1
		end
		local folder = Instance.new("Folder")
		folder.Name = "Props"
		folder.Parent = h.Decor

		-- hero / structure / moving placements
		for _, pl in d.placements do
			if pl.hole ~= n or SKIP_PROPS[pl.prop] then
				continue
			end
			local info = d.props[pl.prop]
			local cf = cfH * CFrame.new(table.unpack(pl.pos)) * CFrame.Angles(0, math.rad(pl.yaw or 0), 0)
			local m = instance(lib, pl.prop, cf, pl.scale, pl.scale_z_to, info and info.bbox)
			if not m then
				skip("missing:" .. pl.prop)
				continue
			end
			local motion = pl.motion or (info and info.motion)
			if motion then
				-- ride on the physics mover (phase-locked to the spec on the server): weld, massless, no collision
				local mover
				for _, mv in h.Movers:GetChildren() do
					if mv:GetAttribute("MoverId") == motion.id then
						mover = mv
					end
				end
				if not mover then
					skip("nomover:" .. pl.prop)
					m:Destroy()
					continue
				end
				m.Name = "PropVisual"
				local root = mover:FindFirstChild("MoverRoot")
				for _, p in m:GetDescendants() do
					if p:IsA("BasePart") then
						p.Anchored = false
						local w = Instance.new("WeldConstraint")
						w.Part0 = root
						w.Part1 = p
						w.Parent = p
					end
				end
				m.Parent = mover
				-- the mesh replaces the part-built visual (the invisible Blocker parts still do the colliding)
				for _, v in mover:GetChildren() do
					if v:IsA("BasePart") and v.Name ~= "Blocker" and v.Name ~= "MoverRoot" and v.Name ~= "MoverBase" then
						v.Transparency = 1
					end
				end
				addGlow(m, 8, 0.9)
				rep.moving += 1
			else
				m.Parent = folder
				-- a mesh that replaces a part-built stand-in (CourseBuilder's flag, the H5 respawn stone)
				for pat, standIns in REPLACES do
					if string.find(pl.prop, pat) then
						for _, sn in standIns do
							for _, x in h:GetDescendants() do
								if x.Name == sn and x:IsA("BasePart") then
									x.Transparency = 1
									for _, g in x:GetChildren() do
										if g:IsA("SurfaceGui") then
											g.Enabled = false
										end
									end
								end
							end
						end
					end
				end
				if pl.light then
					-- props_overrides.json lantern with its own light (H9 amber lanterns over the green)
					setLight(m, pl.light)
				elseif string.find(pl.prop, "lantern") or string.find(pl.prop, "torii") or string.find(pl.prop, "mushroom") or string.find(pl.prop, "ring") then
					addGlow(m, 10, 1)
				end
				if pl.chain_top then
					-- hanging chain from the lantern top up into the canopy
					local top = m:GetBoundingBox().Position + Vector3.new(0, m:GetExtentsSize().Y / 2, 0)
					local len = cfH.Position.Y + pl.chain_top - top.Y
					if len > 0.1 then
						local c = Instance.new("Part")
						c.Name = "Chain"
						c.Shape = Enum.PartType.Cylinder
						c.Size = Vector3.new(len, 0.08, 0.08)
						c.CFrame = CFrame.new(top + Vector3.new(0, len / 2, 0)) * CFrame.Angles(0, 0, math.rad(90))
						c.Color = Color3.fromHex("3B3A3F")
						c.Material = Enum.Material.Metal
						c.CastShadow = false
						decorate(c)
						c.Parent = m
					end
				end
				rep.hero += 1
			end
		end

		-- set dressing
		local lights = 0
		local dfolder = Instance.new("Folder")
		dfolder.Name = "Dressing"
		dfolder.Parent = folder
		for _, it in d.dressing[n] or {} do
			if SKIP_PROPS[it.prop] then
				continue
			end
			local info = d.props[it.prop]
			if not info then
				skip("unknown")
				continue
			end
			local sc = it.scale or 1
			local r = math.max(info.bbox[1], info.bbox[3]) * sc / 2
			local lp = Vector3.new(table.unpack(it.pos))
			local wp = cfH:PointToWorldSpace(lp)
			local y = wp.Y
			if ko then
				if otherHoleNear(n, wp, r * 0.6) then
					skip("otherHole")
					continue
				end
				if nearPath(wp, it.role == "tree" and r * 0.5 or r * 0.7) then
					skip("path")
					continue
				end
				local dt = (Vector3.new(wp.X, 0, wp.Z) - ko.tree).Magnitude
				if n == 9 then
					-- inside the giant trunk: only small things on the floor, clear of the wall
					if it.role == "tree" or info.bbox[2] * sc > 4.5 or dt > ko.treeIn - r - 1 then
						skip("trunk")
						continue
					end
				elseif dt < ko.treeOut + r + 2 then
					skip("trunk")
					continue
				end
				if (Vector3.new(wp.X, 0, wp.Z) - ko.spawn).Magnitude < 12 + r then
					skip("plaza")
					continue
				end
				local hit = workspace:Raycast(Vector3.new(wp.X, wp.Y + 40, wp.Z), Vector3.new(0, -90, 0), groundParams)
				if not hit then
					skip("noground")
					continue
				end
				if hit.Material == Enum.Material.Water and not string.find(it.prop, "stone") and not string.find(it.prop, "rock") then
					skip("water")
					continue
				end
				y = hit.Position.Y - 0.15
			end
			-- keep tree canopies off the hole's own felt (they hide the green from the tee and in the overview), and
			-- everything else off it too (the dressing was fitted to the pre-v2 holes: H8's upper level moved 9 studs)
			if it.role == "tree" and overFelt(h, wp, r * 0.85) then
				skip("canopy")
				continue
			elseif it.role ~= "tree" and overFelt(h, wp, math.min(r, 1.5) + 0.3) then
				skip("felt")
				continue
			end
			local cf = CFrame.new(wp.X, y, wp.Z) * (cfH - cfH.Position) * CFrame.Angles(0, math.rad(it.yaw or 0), 0)
			local m = instance(lib, it.prop, cf, sc)
			if not m then
				skip("missing:" .. it.prop)
				continue
			end
			m.Parent = dfolder
			-- small stuff casts no shadow (cheaper on phones)
			if info.bbox[2] * sc < 3 then
				for _, p in m:GetDescendants() do
					if p:IsA("BasePart") then
						p.CastShadow = false
					end
				end
			end
			if lights < MAX_DRESSING_LIGHTS and (string.find(it.prop, "lantern") or string.find(it.prop, "glowing")) then
				if addGlow(m, 8, 0.8) then
					lights += 1
				end
			end
			rep.dressing += 1
		end
		rep.lights = lights

		-- pass-8 PointLights (manifest lights[]): amber rail lanterns (H7 lower tiers, H8) and the H8 mushroom /
		-- firefly glow. The rail_lantern_* meshes aren't imported yet, so each rail light gets a small stand-in
		-- (stake + lantern_small, or a primitive lantern); glow lights hang on an invisible point over their cluster.
		local lfolder = Instance.new("Folder")
		lfolder.Name = "Lights"
		lfolder.Parent = folder
		for _, l in d.pointLights or {} do
			if l.hole ~= n then
				continue
			end
			local wp = cfH:PointToWorldSpace(Vector3.new(table.unpack(l.pos)))
			local spec = { range = l.range, brightness = l.brightness, color3 = l.color3 }
			local m = Instance.new("Model")
			m.Name = "Light_" .. l.id
			if l.kind == "rail_lantern" then
				-- l.base / l.yaw: the post's foot (hole-local) and yaw (local +X points at the rail), l.pos: the glow core
				local baseW = l.base and cfH:PointToWorldSpace(Vector3.new(table.unpack(l.base))) or wp - Vector3.new(0, 1.5, 0)
				local rot = (cfH - cfH.Position) * CFrame.Angles(0, math.rad(l.yaw or 0), 0)
				local hit = workspace:Raycast(baseW + Vector3.new(0, 3, 0), Vector3.new(0, -8, 0), groundParams)
				local footY = hit and hit.Position.Y - 0.1 or baseW.Y
				local mesh = lib:FindFirstChild(l.prop or "") and instance(lib, l.prop, CFrame.new(baseW.X, footY, baseW.Z) * rot, 1)
				if mesh then
					mesh.Parent = m
				else
					-- stand-in until rail_lantern_stake / rail_lantern_crook are imported: lantern_small with its glow on
					-- the light point, on a stake (1.9 tall) or hanging from a crook post (6.5 tall, arm out to the lantern)
					local crook = l.prop == "rail_lantern_crook"
					local s = crook and 1.25 or 1
					local function post(name, a, b, thick)
						local p = Instance.new("Part")
						p.Name = name
						p.Size = Vector3.new(thick, thick, (b - a).Magnitude)
						p.CFrame = CFrame.lookAt((a + b) / 2, b)
						p.Color = Color3.fromHex("8A5A33")
						p.Material = Enum.Material.Wood
						p.Parent = m
					end
					local lan = instance(lib, "lantern_small", CFrame.new(wp - Vector3.new(0, 0.36 * s, 0)) * rot, s)
					local lanTop = wp.Y + 0.4 * s
					if lan then
						lan.Parent = m
					else
						local core = Instance.new("Part")
						core.Name = "Glow"
						core.Shape = Enum.PartType.Ball
						core.Size = Vector3.new(0.35, 0.35, 0.35)
						core.CFrame = CFrame.new(wp)
						core.Color = Color3.fromRGB(table.unpack(l.color3))
						core.Material = Enum.Material.Neon
						core.Parent = m
					end
					if crook then
						local foot = Vector3.new(baseW.X, footY, baseW.Z)
						local topY = math.max(footY + 6.5, lanTop + 0.3)
						post("Post", foot, Vector3.new(foot.X, topY, foot.Z), 0.22)
						post("Arm", Vector3.new(foot.X, topY - 0.1, foot.Z), Vector3.new(wp.X, topY - 0.1, wp.Z), 0.14)
						post("Hanger", Vector3.new(wp.X, topY - 0.1, wp.Z), Vector3.new(wp.X, lanTop, wp.Z), 0.05)
					else
						post("Stake", Vector3.new(wp.X, footY, wp.Z), Vector3.new(wp.X, wp.Y - 0.36 * s + 0.02, wp.Z), 0.14)
					end
				end
			else
				local pt = Instance.new("Part")
				pt.Name = "GlowPoint"
				pt.Size = Vector3.new(0.2, 0.2, 0.2)
				pt.CFrame = CFrame.new(wp + Vector3.new(0, 0.3, 0))
				pt.Transparency = 1
				pt.Parent = m
				local light = Instance.new("PointLight")
				light.Parent = pt
			end
			for _, p in m:GetDescendants() do
				if p:IsA("BasePart") then
					decorate(p)
					p.CastShadow = false
				end
			end
			setLight(m, spec)
			m.Parent = lfolder
			rep.pointLights = (rep.pointLights or 0) + 1
		end
	end

	-- the old H9 hollow tree mesh stands in the NW forest as a sister tree (world layout)
	local worldLib = ServerStorage:FindFirstChild("LanternGroveWorld")
	if ko and lib:FindFirstChild("hollow_tree") and not (worldLib and worldLib:FindFirstChild("sister_tree_nw")) then
		local bg = workspace:FindFirstChild("World") and workspace.World:FindFirstChild("Backdrop")
		if bg then
			local old = bg:FindFirstChild("sister_tree_nw_mesh")
			if old then
				old:Destroy()
			end
			local hit = workspace:Raycast(Vector3.new(-190, 200, -110), Vector3.new(0, -300, 0), groundParams)
			local m = instance(lib, "hollow_tree", CFrame.new(-190, hit and hit.Position.Y - 0.5 or 32, -110) * CFrame.Angles(0, math.rad(140), 0), 1.4)
			m.Name = "sister_tree_nw_mesh"
			m.Parent = bg
			local clump = bg:FindFirstChild("sister_tree_nw")
			if clump then
				clump:Destroy()
			end
		end
	end

	local parts, tris = 0, 0
	for _, h in holes do
		for _, x in h.Decor:GetDescendants() do
			if x:IsA("BasePart") then
				parts += 1
			elseif x:IsA("Model") and x:GetAttribute("Tris") then
				tris += x:GetAttribute("Tris")
			end
		end
	end
	report.totalDecorParts = parts
	report.totalDecorTris = tris
	return HttpService:JSONEncode(report)
end

return PropsBuilder
