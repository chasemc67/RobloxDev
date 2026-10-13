-- LobbyBuilder: the Golden Hour Boardwalk lobby (SRV-137/138) from 3D Model Bot's meshes. Run in Edit (MCP / command bar):
--   local LB = require(game.ServerStorage.LobbyBuilder:Clone())
--   LB.PrepareLibrary()    -- once, after importing assets/vr-mini-golf/lobby/boardwalk/models/fbx/bw_*.fbx with the 3D
--                          -- Importer (one Model per file in Workspace): moves each into ServerStorage.LobbyLibrary.<asset>
--                          -- with its pivot at the prop pivot (base centre; windmill blades: the hub), undoes the
--                          -- importer's turn about Y, applies the Neon colours and makes every part pure decoration
--   LB.Build()             -- (re)builds workspace.Lobby at the layout origin
--   LB.MeasureClearance()  -- moving parts vs every static part, at 36 phases (stage t: >= 0.15 studs)
--   LB.BuildPortals()      -- (stage z; Build calls it) Lobby.Portals.Portal_<courseId>: 10x10x3 walk-in triggers inside
--                          -- each playable course's arch (ServerScriptService.LobbyServer teleports on touch)
--   LB.BuildLeaderboard()  -- (stage z; Build calls it) Lobby.Leaderboard: the board on leaderboard_wall (LobbyServer fills it)
-- Data: ServerStorage.CourseData.LobbyLayout (tools/lobby_to_lua.py; fixes in tools/lobby_overrides.json). Positions
-- are lobby-frame studs (X east, Z south, deck top Y 0); `origin` puts the lobby frame in the world, away from the
-- course. Meshes never collide: walking uses invisible box colliders (walkways, railings, manifest collision boxes).
-- Players spawn here (stage x: workspace.SpawnLocation under LobbySpawn). Stage z: the lobby is its own place; the menu's
-- course cards and the arch portals teleport to each course's place. Stage ab: the pass 10 portal kit (arches, lanterns,
-- portal quads, aprons, per-course scenery) is imported from fbx_merged/lobby_portals_pass10.fbx (tools/merge_fbx_for_import.py).
local ServerStorage = game:GetService("ServerStorage")
local HttpService = game:GetService("HttpService")
local CollectionService = game:GetService("CollectionService")

local LobbyBuilder = {}

local LIB_NAME = "LobbyLibrary"
LobbyBuilder.SPIN_TAG = "LobbySpinner" -- client GolfClient/LobbySpin turns these (attributes SpinAxis, SpinRPM)

local function data()
	return require(ServerStorage.CourseData.LobbyLayout:Clone())
end

local function v3(t)
	return Vector3.new(t[1], t[2], t[3])
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
	return (string.gsub(name, "%.%d+$", ""))
end

local function partsOf(root)
	local out = {}
	if root:IsA("BasePart") then
		table.insert(out, root)
	end
	for _, d in root:GetDescendants() do
		if d:IsA("BasePart") then
			table.insert(out, d)
		end
	end
	return out
end

-- best yaw (0/90/180/270) and translation mapping the manifest's per-mesh centres onto the imported parts
local function fit(parts, spec)
	local centres = {}
	for _, ps in spec.parts do
		centres[ps.mesh] = v3(ps.center)
	end
	local best, bestYaw, bestT, n = math.huge, 0, Vector3.zero, 0
	for _, yaw in { 0, 180, 90, 270 } do
		local rot = CFrame.Angles(0, math.rad(yaw), 0)
		local sum, k = Vector3.zero, 0
		for _, p in parts do
			local c = centres[meshKey(p.Name)]
			if c then
				sum += p.Position - rot * c
				k += 1
			end
		end
		if k > 0 then
			local t = sum / k
			local err = 0
			for _, p in parts do
				local c = centres[meshKey(p.Name)]
				if c then
					err += (p.Position - (t + rot * c)).Magnitude
				end
			end
			if err / k < best - 1e-4 then
				best, bestYaw, bestT, n = err / k, yaw, t, k
			end
		end
	end
	-- a prop can only show its turn if two of its mesh centres differ in XZ (stage ab: a single-mesh prop, or one whose
	-- meshes share an XZ centre, fits every yaw with error 0, and yaw 0 used to win; they now take the common turn)
	local decisive = false
	local first = spec.parts[1]
	for _, ps in spec.parts do
		if math.abs(ps.center[1] - first.center[1]) > 0.05 or math.abs(ps.center[3] - first.center[3]) > 0.05 then
			decisive = true
		end
	end
	return best, bestYaw, bestT, n, decisive
end

function LobbyBuilder.PrepareLibrary()
	local d = data()
	local lib = ServerStorage:FindFirstChild(LIB_NAME) or Instance.new("Folder")
	lib.Name = LIB_NAME
	lib.Parent = ServerStorage
	local report = { prepared = {}, missing = {}, turned = {}, unknownMeshes = {}, scale = {}, fitErr = {} }
	local found = {}
	for name in d.assets do
		local src = workspace:FindFirstChild(name)
		if src and src:IsA("Model") then
			found[name] = src
		elseif not lib:FindFirstChild(name) then
			table.insert(report.missing, name)
		end
	end
	-- the importer's turn is the same for every single-file import: take it from the props that can show it
	local votes = {}
	for name, src in found do
		local _, yaw, _, _, decisive = fit(partsOf(src), d.assets[name])
		if decisive then
			votes[yaw] = (votes[yaw] or 0) + 1
		end
	end
	local common, most = 180, -1
	for yaw, c in votes do
		if c > most then
			common, most = yaw, c
		end
	end
	report.commonTurn = common
	for name, src in found do
		local spec = d.assets[name]
		local parts = partsOf(src)
		local err, yaw, t, _, decisive = fit(parts, spec)
		if not decisive then
			-- recompute the translation for the common turn
			local rot = CFrame.Angles(0, math.rad(common), 0)
			local sum, k = Vector3.zero, 0
			for _, ps in spec.parts do
				for _, p in parts do
					if meshKey(p.Name) == ps.mesh then
						sum += p.Position - rot * v3(ps.center)
						k += 1
					end
				end
			end
			yaw, t = common, k > 0 and sum / k or t
		end
		report.turned[name] = yaw
		report.fitErr[name] = math.floor(err * 1000 + 0.5) / 1000
		local toLocal = (CFrame.new(t) * CFrame.Angles(0, math.rad(yaw), 0)):Inverse()
		local model = Instance.new("Model")
		model.Name = name
		local colours = {}
		for _, ps in spec.parts do
			colours[ps.mesh] = ps
		end
		for _, p in parts do
			p.CFrame = toLocal * p.CFrame
			p.Parent = model
			local ps = colours[meshKey(p.Name)]
			if ps then
				if ps.material == "Neon" then
					p.Material = Enum.Material.Neon
					if p:IsA("MeshPart") then
						p.TextureID = ""
					end
				end
				if ps.color then
					p.Color = Color3.fromHex(ps.color)
				end
				p.CastShadow = ps.material ~= "Neon"
				-- (stage ab, pass 10 portal kit) the Sugarloaf candy crystals: a low glow, not full Neon (their pink /
				-- yellow is vertex colour; Neon would wash it white): plastic plus one dim pink light per cluster
				if ps.mesh:find("__Glow_Crystal") then
					p.Material = Enum.Material.SmoothPlastic
					p.Color = Color3.new(1, 1, 1)
					p.CastShadow = false
					local light = Instance.new("PointLight")
					light.Color, light.Brightness, light.Range, light.Shadows = Color3.fromHex("F59AC8"), 0.5, 7, false
					light.Parent = p
				end
			else
				table.insert(report.unknownMeshes, p:GetFullName())
			end
			decorate(p)
		end
		-- (stage ab) the arch lanterns hang in the arch: no shadows from them (Game Art Bot)
		if string.find(name, "_lantern_%d+$") then
			for _, p in parts do
				p.CastShadow = false
			end
		end
		model.WorldPivot = CFrame.new()
		local _, size = model:GetBoundingBox()
		local want = v3(spec.bbox)
		if want.Y > 0.3 and math.abs(size.Y / want.Y - 1) > 0.05 then
			table.insert(report.scale, string.format("%s %.3f vs %.3f", name, size.Y, want.Y))
		end
		local old = lib:FindFirstChild(name)
		if old then
			old:Destroy()
		end
		model.Parent = lib
		src:Destroy()
		table.insert(report.prepared, name)
	end
	return HttpService:JSONEncode(report)
end

-- non-uniform scale in the prop's own frame (props are axis-aligned around their pivot)
local function scaleModel(model: Model, s: Vector3)
	local pivot = model:GetPivot()
	for _, p in model:GetDescendants() do
		if p:IsA("BasePart") then
			local lp = pivot:ToObjectSpace(p.CFrame)
			local rot = lp - lp.Position
			local function f(a)
				return math.abs(a.X) * s.X + math.abs(a.Y) * s.Y + math.abs(a.Z) * s.Z
			end
			p.Size = p.Size * Vector3.new(f(rot.XVector), f(rot.YVector), f(rot.ZVector))
			p.CFrame = pivot * (CFrame.new(lp.Position * s) * rot)
		end
	end
end

local function box(name, cf, size, parent, props)
	local p = Instance.new("Part")
	p.Name = name
	p.Anchored = true
	p.CanTouch = false
	p.CanQuery = false
	p.CastShadow = false
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	p.Size = size
	p.CFrame = cf
	for k, v in props or {} do
		p[k] = v
	end
	p.Parent = parent
	return p
end

local function collider(name, cf, size, parent)
	return box(name, cf, size, parent, { Transparency = 1, CanCollide = true })
end

function LobbyBuilder.Build()
	local d = data()
	local lib = ServerStorage:FindFirstChild(LIB_NAME)
	assert(lib, "run LobbyBuilder.PrepareLibrary() first")
	local origin = CFrame.new(v3(d.origin))
	local old = workspace:FindFirstChild("Lobby")
	if old then
		old:Destroy()
	end
	local lobby = Instance.new("Model")
	lobby.Name = "Lobby"
	lobby:SetAttribute("LobbyOrigin", v3(d.origin))
	local decor = Instance.new("Folder")
	decor.Name = "Decor"
	decor.Parent = lobby
	local colliders = Instance.new("Folder")
	colliders.Name = "Colliders"
	colliders.Parent = lobby
	local report = { instances = 0, missing = {}, colliders = 0, spinners = 0 }
	local batch = 0
	for _, inst in d.instances do
		local spec = d.assets[inst.asset]
		local src = lib:FindFirstChild(inst.asset)
		local cf = origin * CFrame.new(v3(inst.position)) * CFrame.Angles(0, math.rad(inst.yaw or 0), 0)
		if not src then
			report.missing[inst.asset] = true
		else
			local m = src:Clone()
			m.Name = inst.id
			m:PivotTo(CFrame.new())
			if inst.scale then
				scaleModel(m, v3(inst.scale))
			end
			m:PivotTo(cf)
			m:SetAttribute("Asset", inst.asset)
			if spec.motion then
				m:SetAttribute("SpinAxis", v3(spec.motion.axis))
				m:SetAttribute("SpinRPM", spec.motion.rpm)
				m:SetAttribute("SpinPivot", cf)
				CollectionService:AddTag(m, LobbyBuilder.SPIN_TAG)
				report.spinners += 1
			end
			m.Parent = decor
			report.instances += 1
		end
		if inst.solid then
			local s = inst.scale and v3(inst.scale) or Vector3.one
			for i, c in spec.collision do
				collider(inst.id .. "_col" .. i, cf * CFrame.new(v3(c.center) * s), v3(c.size) * s, colliders)
				report.colliders += 1
			end
		end
		batch += 1
		if batch % 40 == 0 then
			task.wait()
		end
	end
	for _, w in d.walkways do
		collider(w.id, origin * CFrame.new(v3(w.position)) * CFrame.Angles(0, math.rad(w.yaw or 0), 0), v3(w.size), colliders)
	end
	for _, r in d.railings do
		collider(r.id, origin * CFrame.new(v3(r.position)) * CFrame.Angles(0, math.rad(r.yaw or 0), 0), v3(r.size), colliders)
	end
	-- sand behind the arches (walkway "sand_strip" is its collider) and the ocean plane at Y -4
	for _, w in d.walkways do
		if w.id == "sand_strip" then
			box("Sand", origin * CFrame.new(v3(w.position)), v3(w.size), decor, { Color = Color3.fromHex("E3C99A"), Material = Enum.Material.Sand, CanCollide = false })
		end
	end
	local bmin, bmax = v3(d.bounds.min), v3(d.bounds.max)
	local mid = (bmin + bmax) / 2
	box("Ocean", origin * CFrame.new(mid.X, -4.5, mid.Z), Vector3.new(1400, 1, 1400), decor, { Color = Color3.fromHex("3E8FB0"), Material = Enum.Material.Glass, Transparency = 0.15, CanCollide = false })
	-- invisible walls along the bounds (lobby.json: 40 tall)
	local h = 40
	for i, w in {
		{ Vector3.new(bmin.X - 1, h / 2, mid.Z), Vector3.new(2, h, bmax.Z - bmin.Z) },
		{ Vector3.new(bmax.X + 1, h / 2, mid.Z), Vector3.new(2, h, bmax.Z - bmin.Z) },
		{ Vector3.new(mid.X, h / 2, bmin.Z - 1), Vector3.new(bmax.X - bmin.X, h, 2) },
		{ Vector3.new(mid.X, h / 2, bmax.Z + 1), Vector3.new(bmax.X - bmin.X, h, 2) },
	} do
		collider("BoundsWall" .. i, origin * CFrame.new(w[1]), w[2], colliders)
	end
	local sp = v3(d.spawn.position)
	local spawnMarker = box("LobbySpawn", origin * CFrame.new(sp + Vector3.new(0, 0.05, 0)) * CFrame.Angles(0, math.rad(d.spawn.yaw or 0), 0), Vector3.new(4, 0.1, 4), lobby, { Transparency = 1, CanCollide = false })
	spawnMarker:SetAttribute("Note", "lobby spawn (100,0,100), facing north; workspace.SpawnLocation sits under it (stage x)")
	for _, p in lobby:GetDescendants() do
		if p:IsA("BasePart") and p.Parent == colliders then
			p.CollisionGroup = "Default"
		end
	end
	lobby.WorldPivot = origin
	lobby.Parent = workspace
	LobbyBuilder.BuildPortals()
	LobbyBuilder.BuildLeaderboard()
	report.missing = (function()
		local t = {}
		for k in report.missing do
			table.insert(t, k)
		end
		return t
	end)()
	return HttpService:JSONEncode(report)
end

-- (stage z) Walk-in portals: a 10x10x3 trigger standing in each playable course's arch opening (the arch's legs are
-- 10 studs apart, its crossbeam 12 up). Stage ab: the trigger is invisible and the pass 10 portal quad
-- (bw_portal_surface_<course>, 10x12 in the opening, placed by Build) is the glowing surface, in the course colour;
-- Aurora (not playable yet) gets a dim icy sheet and no trigger.
local PORTALS = {
	lantern_grove = { arch = "arch_lantern_grove", color = Color3.fromRGB(255, 190, 90) },
	sugarloaf_canyon = { arch = "arch_sugarloaf_canyon", color = Color3.fromRGB(255, 120, 150) },
}
local PORTAL_SURFACES = {
	lantern_grove = { color = Color3.fromRGB(255, 190, 90), transparency = 0.35 },
	sugarloaf_canyon = { color = Color3.fromRGB(255, 120, 150), transparency = 0.35 },
	aurora_archipelago = { color = Color3.fromHex("9FE6F2"), transparency = 0.7 },
}

function LobbyBuilder.BuildPortals()
	local lobby = workspace:FindFirstChild("Lobby")
	assert(lobby, "no workspace.Lobby")
	local old = lobby:FindFirstChild("Portals")
	if old then
		old:Destroy()
	end
	local folder = Instance.new("Folder")
	folder.Name = "Portals"
	local out = {}
	for courseId, look in PORTAL_SURFACES do
		local surface = lobby.Decor:FindFirstChild("arch_" .. courseId .. "__bw_portal_surface_" .. courseId)
		for _, part in surface and surface:GetDescendants() or {} do
			if part:IsA("BasePart") then
				part.Material = Enum.Material.Neon
				part.Color = look.color
				part.Transparency = look.transparency
				part.CastShadow = false
				if part:IsA("MeshPart") then
					part.TextureID = ""
				end
				local sa = part:FindFirstChildOfClass("SurfaceAppearance")
				if sa then
					sa:Destroy()
				end
			end
		end
	end
	for courseId, p in PORTALS do
		local arch = lobby.Decor:FindFirstChild(p.arch)
		if arch then
			local pivot = arch:GetPivot()
			local t = box("Portal_" .. courseId, pivot * CFrame.new(0, 5, 0), Vector3.new(10, 10, 3), folder, {
				CanCollide = false,
				CanTouch = true,
				Material = Enum.Material.Neon,
				Color = p.color,
				Transparency = lobby.Decor:FindFirstChild(p.arch .. "__bw_portal_surface_" .. courseId) and 1 or 0.72,
				CastShadow = false,
			})
			t:SetAttribute("CourseId", courseId)
			t.CollisionGroup = "Default"
			table.insert(out, courseId .. "@" .. tostring(t.Position))
		end
	end
	folder.Parent = lobby
	return table.concat(out, ", ")
end

-- (stage z) Leaderboard: an invisible part flush with leaderboard_wall's lobby-side face, with a SurfaceGui of one
-- column per playable course (Col_<courseId>: Header, Note, Row1..Row8 with Rank / Player / Total). LobbyServer
-- writes the rows every 60 s from the OrderedDataStores (ServerScriptService.Leaderboard).
local BOARD_ROWS = 8
function LobbyBuilder.BuildLeaderboard()
	local lobby = workspace:FindFirstChild("Lobby")
	assert(lobby, "no workspace.Lobby")
	local old = lobby:FindFirstChild("Leaderboard")
	if old then
		old:Destroy()
	end
	local wall = lobby.Decor:FindFirstChild("leaderboard_wall")
	assert(wall, "no leaderboard_wall")
	local cf, size = wall:GetBoundingBox()
	-- the wall's thin axis is its local Z; the lobby side is the one facing the spawn
	local spawn = lobby:FindFirstChild("LobbySpawn")
	local toSpawn = (spawn and spawn.Position or Vector3.new(0, 0, 6100)) - cf.Position
	local normal = cf.LookVector
	if normal:Dot(toSpawn) < 0 then
		normal = -normal
	end
	local face = cf.Position + normal * (size.Z / 2 + 0.06)
	local w, h = size.X - 1.2, size.Y - 1.4
	local part = box("Leaderboard", CFrame.lookAt(face, face + normal), Vector3.new(w, h, 0.05), lobby, { Transparency = 1, CanCollide = false })
	local gui = Instance.new("SurfaceGui")
	gui.Name = "Board"
	gui.Face = Enum.NormalId.Front
	gui.SizingMode = Enum.SurfaceGuiSizingMode.FixedSize
	gui.CanvasSize = Vector2.new(math.floor(w * 80), math.floor(h * 80))
	gui.LightInfluence = 0
	gui.Brightness = 1.4
	gui.Parent = part
	local bg = Instance.new("Frame")
	bg.Size = UDim2.fromScale(1, 1)
	bg.BackgroundColor3 = Color3.fromRGB(14, 22, 38)
	bg.BackgroundTransparency = 0.15
	bg.Parent = gui
	local function text(name, parent, props)
		local l = Instance.new("TextLabel")
		l.Name = name
		l.BackgroundTransparency = 1
		l.Font = Enum.Font.FredokaOne
		l.TextScaled = true
		l.TextColor3 = Color3.fromRGB(255, 238, 206)
		l.Text = ""
		for k, v in props do
			l[k] = v
		end
		l.Parent = parent
		return l
	end
	text("Title", bg, { Text = "Best Rounds", TextColor3 = Color3.fromRGB(255, 179, 71), Position = UDim2.fromScale(0.05, 0.02), Size = UDim2.fromScale(0.9, 0.13) })
	local courses = { "lantern_grove", "sugarloaf_canyon" }
	local namesById = { lantern_grove = "Lantern Grove", sugarloaf_canyon = "Sugarloaf Canyon" }
	for i, id in courses do
		local col = Instance.new("Frame")
		col.Name = "Col_" .. id
		col.BackgroundTransparency = 1
		col.Position = UDim2.fromScale(0.03 + (i - 1) * 0.49, 0.17)
		col.Size = UDim2.fromScale(0.45, 0.8)
		col.Parent = bg
		text("Header", col, { Text = namesById[id], TextColor3 = Color3.fromRGB(255, 179, 71), Size = UDim2.fromScale(1, 0.12) })
		text("Note", col, { Font = Enum.Font.GothamMedium, TextColor3 = Color3.fromRGB(184, 196, 186), Position = UDim2.fromScale(0, 0.4), Size = UDim2.fromScale(1, 0.08), Text = "Loading scores..." })
		for r = 1, BOARD_ROWS do
			local row = Instance.new("Frame")
			row.Name = "Row" .. r
			row.BackgroundTransparency = r % 2 == 0 and 1 or 0.85
			row.BackgroundColor3 = Color3.fromRGB(30, 46, 70)
			row.BorderSizePixel = 0
			row.Position = UDim2.fromScale(0, 0.14 + (r - 1) * 0.107)
			row.Size = UDim2.fromScale(1, 0.1)
			row.Parent = col
			text("Rank", row, { Size = UDim2.fromScale(0.14, 0.8), Position = UDim2.fromScale(0, 0.1), TextColor3 = Color3.fromRGB(184, 196, 186) })
			text("Player", row, { Font = Enum.Font.GothamMedium, Size = UDim2.fromScale(0.64, 0.8), Position = UDim2.fromScale(0.16, 0.1), TextXAlignment = Enum.TextXAlignment.Left })
			text("Total", row, { Size = UDim2.fromScale(0.18, 0.8), Position = UDim2.fromScale(0.82, 0.1), TextColor3 = Color3.fromRGB(130, 235, 150) })
		end
	end
	return tostring(part.CFrame)
end

-- Clearance of every spinning part from every static lobby part, over a full turn (36 phases). Uses temporary
-- clones with PreciseConvexDecomposition collision (hulls enclose the mesh, so a reported clearance is a lower
-- bound): the spinner is pushed `margin` studs in each of the 6 axis directions and must not touch anything.
function LobbyBuilder.MeasureClearance(margin: number?)
	margin = margin or 0.15
	local lobby = workspace:FindFirstChild("Lobby")
	assert(lobby, "build first")
	local tmp = Instance.new("Folder")
	tmp.Name = "_ClearanceProbe"
	tmp.Parent = workspace
	local out = { margin = margin, spinners = {} }
	local ok, err = pcall(function()
		for _, spinner in CollectionService:GetTagged(LobbyBuilder.SPIN_TAG) do
			if not spinner:IsDescendantOf(lobby) then
				continue
			end
			local pivot = spinner:GetAttribute("SpinPivot")
			local axis = spinner:GetAttribute("SpinAxis")
			local _, sz = spinner:GetBoundingBox()
			local reach = sz.Magnitude + 4
			-- static neighbours within reach (precise clones)
			local statics = {}
			for _, m in lobby.Decor:GetChildren() do
				if m ~= spinner and m:IsA("Model") then
					local mcf, msz = m:GetBoundingBox()
					if (mcf.Position - pivot.Position).Magnitude < reach + msz.Magnitude / 2 then
						for _, p in partsOf(m) do
							local c = p:Clone()
							c.CanQuery, c.CanCollide = true, true
							c.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition
							c.Parent = tmp
							table.insert(statics, c)
						end
					end
				end
			end
			local moving = {}
			for _, p in partsOf(spinner) do
				local c = p:Clone()
				c.CanQuery, c.CanCollide = true, true
				c.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition
				c.Parent = tmp
				table.insert(moving, { part = c, rel = pivot:ToObjectSpace(p.CFrame) })
			end
			task.wait(0.5) -- let the decompositions build
			local params = OverlapParams.new()
			params.FilterType = Enum.RaycastFilterType.Include
			params.FilterDescendantsInstances = statics
			local hits, worst = {}, nil
			for step = 0, 35 do
				local rot = CFrame.fromAxisAngle(axis, math.rad(step * 10))
				for _, dir in { Vector3.xAxis, -Vector3.xAxis, Vector3.yAxis, -Vector3.yAxis, Vector3.zAxis, -Vector3.zAxis } do
					for _, mv in moving do
						mv.part.CFrame = CFrame.new(dir * margin) * pivot * rot * mv.rel
						for _, h in workspace:GetPartsInPart(mv.part, params) do
							local key = h.Name
							hits[key] = (hits[key] or 0) + 1
							worst = worst or string.format("phase %d deg, push %s", step * 10, tostring(dir))
						end
					end
				end
			end
			table.insert(out.spinners, { name = spinner.Name, statics = #statics, hits = hits, firstHit = worst, pass = next(hits) == nil })
		end
	end)
	tmp:Destroy()
	if not ok then
		out.error = tostring(err)
	end
	return HttpService:JSONEncode(out)
end

return LobbyBuilder
