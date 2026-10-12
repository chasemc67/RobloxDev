-- LobbyBuilder: the Golden Hour Boardwalk lobby (SRV-137/138) from 3D Model Bot's meshes. Run in Edit (MCP / command bar):
--   local LB = require(game.ServerStorage.LobbyBuilder:Clone())
--   LB.PrepareLibrary()    -- once, after importing assets/vr-mini-golf/lobby/boardwalk/models/fbx/bw_*.fbx with the 3D
--                          -- Importer (one Model per file in Workspace): moves each into ServerStorage.LobbyLibrary.<asset>
--                          -- with its pivot at the prop pivot (base centre; windmill blades: the hub), undoes the
--                          -- importer's turn about Y, applies the Neon colours and makes every part pure decoration
--   LB.Build()             -- (re)builds workspace.Lobby at the layout origin
--   LB.MeasureClearance()  -- moving parts vs every static part, at 36 phases (stage t: >= 0.15 studs)
-- Data: ServerStorage.CourseData.LobbyLayout (tools/lobby_to_lua.py; fixes in tools/lobby_overrides.json). Positions
-- are lobby-frame studs (X east, Z south, deck top Y 0); `origin` puts the lobby frame in the world, away from the
-- course. Meshes never collide: walking uses invisible box colliders (walkways, railings, manifest collision boxes).
-- The lobby is not the spawn yet (the portals / course board hookup is the lobby integration ticket).
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
	-- a prop whose mesh centres all sit on the Y axis can't tell its turn apart
	local decisive = false
	for _, ps in spec.parts do
		if math.abs(ps.center[1]) > 0.05 or math.abs(ps.center[3]) > 0.05 then
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
			else
				table.insert(report.unknownMeshes, p:GetFullName())
			end
			decorate(p)
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
	spawnMarker:SetAttribute("Note", "lobby spawn (100,0,100), facing north; not a SpawnLocation until the lobby is wired in")
	for _, p in lobby:GetDescendants() do
		if p:IsA("BasePart") and p.Parent == colliders then
			p.CollisionGroup = "Default"
		end
	end
	lobby.WorldPivot = origin
	lobby.Parent = workspace
	report.missing = (function()
		local t = {}
		for k in report.missing do
			table.insert(t, k)
		end
		return t
	end)()
	return HttpService:JSONEncode(report)
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
