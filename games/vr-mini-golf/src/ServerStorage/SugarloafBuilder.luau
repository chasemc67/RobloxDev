-- SugarloafBuilder (stage w): dresses workspace.CourseSugarloaf (built by CourseBuilder.Build(..., {folder =
-- "CourseSugarloaf", palette = "sugarloaf"})) with the pass 5 mover meshes in ServerStorage.SugarloafMovers
-- (assets/vr-mini-golf/sugarloaf-canyon/models/fbx/movers/, merged into one FBX for the 3D Importer).
--   require(game.ServerStorage.SugarloafBuilder:Clone()).PlaceMeshes()
-- Each library Model has its pivot at the piece's spec pivot (hole-local, models/_src/movers/movers_pass5_summary.md).
--   moving pieces: welded to their mover's MoverRoot at the rest pose (massless, no collision); the stand-in
--                  BlockerVisual boxes are hidden
--   *_collision:   collision proxies (Transparency 1, CanCollide on, CastShadow off): H9 vanes and H14 bucket foot ride
--                  their mover in the GolfMover group as its blockers (the holes.json strip boxes they were cut from are
--                  kept as non-colliding references); H7's flush respawn tile is static felt
--   static pieces: anchored at hole frame * pivot (frames, chamber, trestle, plinth, hour stones, bridge parapets...)
-- Visual meshes never collide or take queries (the holes.json walls/blockers are the collision).
local CollectionService = game:GetService("CollectionService")
local ServerStorage = game:GetService("ServerStorage")

local SugarloafBuilder = {}

local MOVER_PART_TAG = "GolfMoverPart"
local SURFACE_TAG = "GolfSurface"
local BUMPER_PHYS = PhysicalProperties.new(1, 0.05, 0.65, 100, 100) -- spec: moving colliders use bumper restitution 0.65
local FELT_PHYS = PhysicalProperties.new(1, 0.35, 0, 1, 100)

-- piece -> { hole, mover id (moving) | pivot (static), collision? }
local PIECES = {
	h06_sluice_gate = { hole = 6, mover = "sluice_gate" },
	h06_sluice_frame = { hole = 6, pivot = { 0, 0, -28 } },
	h07_bridge_parapets = { hole = 7, pivot = { 0, 0, -42 } },
	h07_bridge_skirts = { hole = 7, pivot = { 0, 0, -42 } },
	h07_gap_floor_mist = { hole = 7, pivot = { 0, -4.25, -42 } },
	h07_island_respawn_stone = { hole = 7, pivot = { 0, 0, -38.5 } },
	h07_island_respawn_stone_collision = { hole = 7, pivot = { 0, 0, -38.5 }, collision = "felt" },
	h07_teleport_pads = { hole = 7, pads = { "bridge1_entry", "bridge1_island", "bridge2_island" } },
	h07_teleport_pad_exit = { hole = 7, pads = { "bridge2_exit" } },
	h09_windpump_vanes = { hole = 9, mover = "windpump" },
	h09_windpump_vanes_collision = { hole = 9, mover = "windpump", collision = "mover" },
	h09_windpump_hub = { hole = 9, pivot = { 0, 4.12, -17.75 } },
	h11_lock_gate = { hole = 11, mover = "lock_gate" },
	h11_lock_lift = { hole = 11, mover = "lock_lift_deck" },
	h11_quay_lip = { hole = 11, mover = "quay_lip" },
	h11_lock_chamber = { hole = 11, pivot = { 0, 0, -23 } },
	h14_ore_bucket = { hole = 14, mover = "ore_bucket" },
	h14_ore_bucket_foot_collision = { hole = 14, mover = "ore_bucket", collision = "mover" },
	h14_cableway_trestle = { hole = 14, pivot = { 0, 0, -24 } },
	h17_shadow_arms = { hole = 17, mover = "shadow_arm" },
	h17_shadow_arm_head_0 = { hole = 17, mover = "shadow_arm" },
	h17_shadow_arm_head_90 = { hole = 17, mover = "shadow_arm" },
	h17_shadow_arm_head_180 = { hole = 17, mover = "shadow_arm" },
	h17_shadow_arm_head_270 = { hole = 17, mover = "shadow_arm" },
	h17_plinth = { hole = 17, pivot = { 0, 0, -36 } },
	h17_hour_stone_XII = { hole = 17, pivot = { 0, 0, -48.5 } },
	h17_hour_stone_I = { hole = 17, pivot = { 6.25, 0, -46.8253 } },
	h17_hour_stone_III = { hole = 17, pivot = { 12.5, 0, -36 } },
	h17_hour_stone_IV = { hole = 17, pivot = { 10.8253, 0, -29.75 } },
	h17_hour_stone_VII = { hole = 17, pivot = { -6.25, 0, -25.1747 } },
	h17_hour_stone_VIII = { hole = 17, pivot = { -10.8253, 0, -29.75 } },
	h17_hour_stone_IX = { hole = 17, pivot = { -12.5, 0, -36 } },
	h17_hour_stone_X = { hole = 17, pivot = { -10.8253, 0, -42.25 } },
	h17_hour_stone_XI = { hole = 17, pivot = { -6.25, 0, -46.8253 } },
	-- world piece (dam crest walk, world.json dam.crest_walk): course-local [0, 115.7, -305] + the layout offset
	dam_crest_parapets = { world = { 0, 115.7, -305 } },
}
SugarloafBuilder.PIECES = PIECES

-- Material colours from models/_src/movers/movers_manifest.json (the importer kept only embedded textures, so the
-- untextured meshes came in near-white). Mesh names are <piece>__<Material>.
local MATERIALS = {
	Brass = { "C9973A", "Metal" }, Bubblegum = { "F78FB3", "SmoothPlastic" }, CandyAmber = { "FFB347", "Glass", 0.25 },
	CandyPink = { "FF6FA8", "Glass", 0.25 }, Collider = { "FF00FF", "SmoothPlastic", 1 }, FloorSand = { "D88E5C", "Sand" },
	GumLemon = { "FFD84A", "SmoothPlastic" }, GumLime = { "9BDB4D", "SmoothPlastic" }, Iron = { "3B3A3F", "Metal" },
	Licorice = { "2B1D20", "SmoothPlastic" }, LipCream = { "FFF0C9", "SmoothPlastic" }, LipRed = { "B83A35", "SmoothPlastic" },
	MintWhite = { "FFF8F0", "SmoothPlastic" }, Mist = { "F6D3E1", "SmoothPlastic", 0.5 }, PadCore = { "2F5D3A", "SmoothPlastic" },
	PadLime = { "D8FF6A", "Neon" }, PepRed = { "D9343A", "SmoothPlastic" }, RespawnGlow = { "7FE7FF", "Neon" },
	Rope = { "C9A46A", "Fabric" }, SandBlock = { "E39A82", "Sandstone" }, SignalGreen = { "63FF67", "Neon" },
	SignalRed = { "FF3028", "Neon" }, Slate = { "5E6670", "Slate" }, Timber = { "8A5A33", "WoodPlanks" },
}
local function applyMaterial(p: BasePart)
	local key = string.match(p.Name, "__(%w+)$")
	local m = key and MATERIALS[key]
	if m then
		p.Color = Color3.fromHex(m[1])
		p.Material = Enum.Material[m[2]]
		p.Transparency = m[3] or 0
		if m[2] == "Neon" or m[2] == "Glass" or (m[3] or 0) > 0 then
			p.CastShadow = false
		end
	end
end

local function holeCF(hole: Model): CFrame
	return CFrame.new(hole:GetAttribute("HoleOrigin")) * CFrame.Angles(0, math.rad(hole:GetAttribute("HoleYaw") or 0), 0)
end

local function setVisual(p: BasePart)
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
end

local function findMover(hole: Model, id: string)
	local movers = hole:FindFirstChild("Movers")
	return movers and movers:FindFirstChild("Mover_" .. id)
end

local function holeDef(data, n)
	for _, h in data.holes do
		if h.number == n then
			return h
		end
	end
end

function SugarloafBuilder.PlaceMeshes(course: Folder?)
	course = course or workspace:FindFirstChild("CourseSugarloaf")
	assert(course, "build CourseSugarloaf first")
	local lib = ServerStorage:FindFirstChild("SugarloafMovers")
	assert(lib, "ServerStorage.SugarloafMovers missing (import the merged pass 5 FBX)")
	local data = require(ServerStorage.CourseData.SugarloafCanyon:Clone())
	local layout = require(ServerStorage.CourseData.SugarloafLayout:Clone())
	local off = layout.offset
	local report = {}
	-- clear an earlier placement
	for _, d in course:GetDescendants() do
		if d:GetAttribute("SugarloafMesh") then
			d:Destroy()
		end
	end
	local world = course:FindFirstChild("WorldMeshes") or Instance.new("Folder")
	world.Name = "WorldMeshes"
	world.Parent = course
	for _, src in lib:GetChildren() do
		local spec = PIECES[src.Name]
		if not spec then
			table.insert(report, src.Name .. ": no placement rule")
			continue
		end
		local function place(target: CFrame, parent: Instance, nameSuffix: string?)
			local m = src:Clone()
			m.Name = src.Name .. (nameSuffix or "")
			m:SetAttribute("SugarloafMesh", true)
			m:PivotTo(target)
			for _, p in m:GetDescendants() do
				if p:IsA("BasePart") then
					p.Anchored = true
					setVisual(p)
					applyMaterial(p)
				end
			end
			m.Parent = parent
			return m
		end
		if spec.world then
			place(CFrame.new(spec.world[1] + off[1], spec.world[2] + off[2], spec.world[3] + off[3]), world)
			table.insert(report, src.Name .. ": world")
			continue
		end
		local hole = course:FindFirstChild("Hole" .. spec.hole)
		local cf = holeCF(hole)
		local decor = hole:FindFirstChild("Decor")
		local meshes = decor:FindFirstChild("Meshes") or Instance.new("Folder")
		meshes.Name = "Meshes"
		meshes.Parent = decor
		if spec.pads then
			local def = holeDef(data, spec.hole)
			local n = 0
			for _, tp in def.player_teleport_points or {} do
				if table.find(spec.pads, tp.id) then
					place(cf * CFrame.new(tp.position[1], tp.position[2], tp.position[3]) * CFrame.Angles(0, math.rad(tp.yaw or 0), 0), meshes, "_" .. tp.id)
					n += 1
				end
			end
			table.insert(report, string.format("%s: %d pads", src.Name, n))
			continue
		end
		if spec.mover then
			local mover = findMover(hole, spec.mover)
			local root = mover and mover:FindFirstChild("MoverRoot")
			if not root then
				table.insert(report, src.Name .. ": mover " .. spec.mover .. " missing")
				continue
			end
			-- the library pivot is the spec pivot; the mover is at its rest pose in Edit (angle/offset 0)
			local pivot = mover:GetAttribute("PivotWorld")
			local rest = CFrame.new(pivot) * (cf - cf.Position)
			local m = place(rest, mover)
			for _, p in m:GetDescendants() do
				if p:IsA("BasePart") then
					p.Anchored = false
					p.Massless = true
					p.CollisionGroup = "GolfMover"
					local w = Instance.new("WeldConstraint")
					w.Part0, w.Part1 = root, p
					w.Parent = p
					if spec.collision == "mover" then
						-- collision proxy: the blocker the ball meets
						p.Transparency = 1
						p.CastShadow = false
						p.CanCollide = true
						p.CanQuery = true
						p.Massless = false
						p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition
						p.CustomPhysicalProperties = BUMPER_PHYS
						p:SetAttribute("RestCFrame", p.CFrame)
						p:SetAttribute("CollisionProxy", src.Name)
						p.Name = "Blocker"
						CollectionService:AddTag(p, MOVER_PART_TAG)
					end
				end
			end
			if spec.collision == "mover" then
				-- the proxy replaces the holes.json strips it was built from (H9: all 48 vane strips; H14: the 14 foot
				-- strips, blockers 2..15): they stay as non-colliding references at the same pose
				for _, b in mover:GetChildren() do
					if b.Name == "Blocker" and not b:GetAttribute("CollisionProxy") then
						local i = b:GetAttribute("BlockerIndex") or 0
						if spec.mover == "windpump" or (spec.mover == "ore_bucket" and i > 1) then
							b.CanCollide = false
							b.CanQuery = false
							b:SetAttribute("ReplacedBy", src.Name)
							CollectionService:RemoveTag(b, MOVER_PART_TAG)
						end
					end
				end
			else
				for _, v in mover:GetChildren() do
					if v.Name == "BlockerVisual" or v.Name == "MoverFeltTop" then
						v.Transparency = 1
					end
				end
			end
			table.insert(report, src.Name .. ": on Mover_" .. spec.mover .. (spec.collision and " (collision proxy)" or ""))
			continue
		end
		local m = place(cf * CFrame.new(spec.pivot[1], spec.pivot[2], spec.pivot[3]), meshes)
		if spec.collision == "felt" then
			for _, p in m:GetDescendants() do
				if p:IsA("BasePart") then
					p.Transparency = 1
					p.CastShadow = false
					p.CanCollide = true
					p.CanQuery = true
					p.CustomPhysicalProperties = FELT_PHYS
					p:SetAttribute("CollisionProxy", src.Name)
					CollectionService:AddTag(p, SURFACE_TAG)
				end
			end
		end
		table.insert(report, src.Name .. ": static H" .. spec.hole .. (spec.collision and " (collision)" or ""))
	end
	-- the hour-stone, plinth and parapet stand-in boxes are replaced by their meshes (their collision boxes stay)
	local h17 = course:FindFirstChild("Hole17")
	for _, r in h17 and h17.Rails:GetChildren() or {} do
		local id = r:GetAttribute("WallId") or ""
		if string.find(id, "hour_stone") or string.find(id, "gnomon_plinth") then
			r.Transparency = 1
		end
	end
	local h7 = course:FindFirstChild("Hole7")
	for _, r in h7 and h7.Rails:GetChildren() or {} do
		local id = r:GetAttribute("WallId") or ""
		if string.find(id, "rope_rail") then
			r.Transparency = 1
		end
	end
	return table.concat(report, "\n")
end

-- Mover clearance over a full cycle (stage w rule: 0.15 studs, 0.06 for the H9 and H14 blockers). Each mover is
-- stepped through `n` poses of its spec profile in Edit (MoverRoot moved, welded blockers follow; restored after) and
-- every collision blocker's surface (0.25 grid) is measured against the hole's colliding static boxes: walls/bumpers/
-- bases, and felt reported separately (several movers ride on the felt by design: H6 gate board, H17 arms).
function SugarloafBuilder.CheckClearance(course: Folder?, n: number?)
	course = course or workspace:FindFirstChild("CourseSugarloaf")
	n = n or 90
	local MoverMath = require(game:GetService("ReplicatedStorage").Golf.MoverMath:Clone())
	local function surfacePoints(cf, size, step)
		local pts, h = {}, size / 2
		local function rng(a)
			local k, t = math.max(1, math.ceil(2 * a / step)), {}
			for i = 0, k do
				table.insert(t, -a + 2 * a * i / k)
			end
			return t
		end
		for _, x in rng(h.X) do
			for _, y in rng(h.Y) do
				for _, z in rng(h.Z) do
					if math.abs(x) >= h.X - 1e-6 or math.abs(y) >= h.Y - 1e-6 or math.abs(z) >= h.Z - 1e-6 then
						table.insert(pts, cf:PointToWorldSpace(Vector3.new(x, y, z)))
					end
				end
			end
		end
		return pts
	end
	local function obbDist(p, part)
		local l = part.CFrame:PointToObjectSpace(p)
		local h = part.Size / 2
		local dx, dy, dz = math.max(math.abs(l.X) - h.X, 0), math.max(math.abs(l.Y) - h.Y, 0), math.max(math.abs(l.Z) - h.Z, 0)
		return math.sqrt(dx * dx + dy * dy + dz * dz)
	end
	local out = {}
	for _, hole in course:GetChildren() do
		local movers = hole:FindFirstChild("Movers")
		for _, mover in movers and movers:GetChildren() or {} do
			local root, base = mover.MoverRoot, mover.MoverBase
			local p = MoverMath.fromModel(mover)
			local period = MoverMath.period(p)
			local rotate = mover.Drive:IsA("HingeConstraint")
			local walls, felts = {}, {}
			for _, d in hole.Geometry:GetChildren() do
				if d:IsA("Part") and d.CanCollide then
					table.insert((d.Name == "Felt" or d.Name == "CupPlate") and felts or walls, d)
				end
			end
			local blockers = {}
			for _, b in mover:GetChildren() do
				if b:IsA("Part") and b.Name == "Blocker" then
					table.insert(blockers, b) -- (collision proxies are measured through the strip boxes they match)
				end
			end
			local rule = (mover.Name == "Mover_windpump" or mover.Name == "Mover_ore_bucket") and 0.06 or 0.15
			local rest = root.CFrame
			local minW, whereW, minF, whereF = math.huge, "", math.huge, ""
			for i = 0, n - 1 do
				local t = period * i / n
				local v = MoverMath.value(p, t)
				if rotate then
					root.CFrame = base.CFrame * CFrame.fromAxisAngle(Vector3.xAxis, math.rad(v)) * base.CFrame:ToObjectSpace(rest)
				else
					root.CFrame = rest + base.CFrame.XVector * v
				end
				for _, b in blockers do
					local pts = surfacePoints(b.CFrame, b.Size, 0.25)
					for _, list in { walls, felts } do
						for _, st in list do
							if (st.Position - b.Position).Magnitude < (st.Size.Magnitude + b.Size.Magnitude) / 2 + 0.5 then
								for _, q in pts do
									local d = obbDist(q, st)
									local tag = string.format("%s vs %s t=%.2f", b:GetAttribute("MoverFelt") or ("b" .. tostring(b:GetAttribute("BlockerIndex"))),
										tostring(st:GetAttribute("WallId") or st:GetAttribute("PieceId") or st.Name), t)
									if list == walls and d < minW then
										minW, whereW = d, tag
									elseif list == felts and d < minF then
										minF, whereF = d, tag
									end
								end
							end
						end
					end
				end
				if i % 10 == 0 then
					task.wait()
				end
			end
			root.CFrame = rest
			table.insert(out, string.format("H%s %s rule %.2f: walls %.3f %s (%s) | felt %.3f (%s)", tostring(hole:GetAttribute("HoleNumber")), mover.Name,
				rule, minW, minW >= rule - 1e-3 and "PASS" or "FAIL", whereW, minF, whereF))
		end
	end
	return table.concat(out, "\n")
end

return SugarloafBuilder
