-- CourseBuilder: builds workspace.Course from a course spec module (ServerStorage.CourseData.<Course>, generated from
-- the designer's holes.json by games/vr-mini-golf/tools/holes_to_lua.py). Run in Edit from the command bar or the MCP:
--   require(game.ServerStorage.CourseBuilder:Clone()).Build(require(game.ServerStorage.CourseData.LanternGrove:Clone()))
-- (the command bar caches modules, so pass clones). Re-import of an updated spec is one step:
--   python3 tools/holes_to_lua.py --push --build
-- Re-apply tags, collision groups and wall physics (from Config) without rebuilding:
--   require(game.ServerStorage.CourseBuilder:Clone()).ApplyPhysics(nil, require(game.ReplicatedStorage.Golf.Config:Clone()))
--
-- Layout of every hole model (workspace.Course.HoleN):
--   Geometry/   collision: Felt (visible, tagged GolfSurface), CupPlate, invisible Wall/Bumper blocks from the spec, and
--               Base blocks under the felt (cliff faces between levels). Walls/bumpers/bases are in collision group GolfWall.
--   Rails/      visual rails/bumpers (no collision, no queries): swap in meshes freely.
--   Movers/     moving parts: one Model per spec moving part (tag GolfMover), driven by GolfServer.Movers.
--   Hazards/    water/pit visuals + invisible Hazard footprints (used to tell "water hazard" from "escaped").
--   Teleports/  Teleport entry markers (attributes) + ring visuals. The ball's owner client does the teleport.
--   Decor/      one Model per spec decoration anchor: an invisible Anchor part (+ Mount attachment) and a Placeholder.
--   Ground/     the lawn under the hole (flat layout only; in the world layout the Terrain is the ground).
--   Tee, Cup (marker, attribute Radius), AimTarget, Bounds, Sign, FlagPole, Flag.
local CourseBuilder = {}
local BLOCKOUT = false
local BUILD_COURSE_ID = nil

local GeometryService = game:GetService("GeometryService")
local CollectionService = game:GetService("CollectionService")
local PhysicsService = game:GetService("PhysicsService")
local Lighting = game:GetService("Lighting")
local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Golf"):WaitForChild("Config"))
local MoverMath = require(game:GetService("ReplicatedStorage"):WaitForChild("Golf"):WaitForChild("MoverMath"))

-- World placement. Each hole's frame comes from the WorldLayout module (ServerStorage.CourseData.WorldLayout,
-- generated from the world map by tools/world_to_lua.py): holeCF = CFrame.new(origin) * Angles(0, rad(yaw), 0), and
-- every hole element (felt, walls, movers, hazards, teleports, tee, cup, decor anchors) is holeCF * its local CFrame.
-- Changing a hole's placement is a data edit + rebuild; the hole geometry is never touched. Without a layout (or
-- `enabled = false`) the holes sit on the flat greybox plane: holes.json world_offset/world_yaw, lifted COURSE_Y.
local COURSE_Y = 8
local FELT_T = 0.4 -- felt slab thickness (spec suggestion)
local CUP_PLATE = 2.2 -- square felt plate the cup is cut into
local CUP_PLATE_T = 1
local LAWN_DROP = 1.5 -- lawn top below each hole's lowest felt
local RAIL_H = 1 -- visual rails stand 1 stud above the felt they border
local CUP_DEPTH = Config.CupDepth

local FELT_PHYS = PhysicalProperties.new(1, 0.35, 0, 1, 100)
-- walls: the high weights make these values win over the ball's own (Config.Wall*/BumperElasticity)
local function wallPhys(cfg, elasticity)
	return PhysicalProperties.new(1, cfg.WallFriction, elasticity, 100, 100)
end

local SURFACE_TAG = "GolfSurface"
local SURFACE_NAMES = { Felt = true, CupPlate = true, Ramp = true }
-- collide with the ball, but players walk/stand through them and the club ghosts through them
local OBSTACLE_GROUP = "GolfWall"
local OBSTACLE_NAMES = { Wall = true, Bumper = true, Base = true }
-- moving blockers: collide with the ball only (never with felt, walls, players or the club)
local MOVER_GROUP = "GolfMover"
local MOVER_TAG = "GolfMover" -- on the mover Model
local MOVER_PART_TAG = "GolfMoverPart" -- on its colliding blocker parts

local function hex(s)
	return Color3.fromHex(s)
end
-- course.md palette
local P = {
	felt = hex("4F9A3A"),
	feltHi = hex("86C24A"),
	feltLo = hex("2F6B2A"),
	limestone = hex("B8AFA0"),
	oak = hex("8A5A33"),
	bark = hex("5B3A22"),
	ember = hex("D2452A"),
	pumpkin = hex("E8862E"),
	gold = hex("F2B632"),
	toadstool = hex("D8392B"),
	cream = hex("F4E9D2"),
	amber = hex("FFB347"),
	paper = hex("F7C873"),
	water = hex("4AA3DF"),
	foam = hex("E6F6FF"),
	slate = hex("6E7480"),
	moss = hex("7A9A3A"),
	firefly = hex("D8FF6A"),
	lawn = hex("6F8F3A"),
}
-- Sugarloaf Canyon (stage w; assets/vr-mini-golf/sugarloaf-canyon/course.md): Build(..., {palette = "sugarloaf"})
-- swaps these into P for that build (each Build runs on a fresh clone of this module)
local SUGARLOAF_P = {
	felt = hex("4FA83D"),
	feltHi = hex("86C24A"),
	feltLo = hex("3B7F35"),
	limestone = hex("E39A82"), -- pink sandstone rail blocks
	oak = hex("8A5A33"), -- weathered timber caps
	bark = hex("AF7061"), -- muted terracotta (bases / cliff faces under the felt)
	cream = hex("FFF8F0"), -- mint white
	slate = hex("C68C59"), -- ochre strata
	toadstool = hex("D9343A"), -- peppermint red
	firefly = hex("D8FF6A"), -- sour-apple lime (teleports)
	paper = hex("FFD36B"), -- sunset gold (sign text)
	amber = hex("FFB347"),
	water = hex("3FB7C9"),
	moss = hex("3E8E41"), -- saguaro green
	lawn = hex("D88E5C"),
	candy = hex("FF6FA8"), -- rock-candy pink
	rope = hex("C9A46A"),
}
-- Sugarloaf felt: grayscale masters of sugarloaf-canyon/textures (felt.png, slope_felt_C.png; textures/_make_roblox_tints.py)
-- tinted per part with Texture.Color3, so one upload serves every felt tone
local SUGARLOAF_FELT = {
	flat = "rbxassetid://109987285887975", -- felt_gray
	studs = 6,
	slope = {
		["-Z"] = "rbxassetid://109008728097658", -- slope_gray_r0
		["+X"] = "rbxassetid://90010334104026", -- r90
		["+Z"] = "rbxassetid://105111549391714", -- r180
		["-X"] = "rbxassetid://122003802815451", -- r270
	},
	GRAY = 0.86, -- mean of the masters: tint = colour / GRAY
}
local COURSE = nil -- nil = Lantern Grove; "sugarloaf_canyon" while building Sugarloaf (set by Build)
local M = Enum.Material
local SMOOTH = Enum.SurfaceType.Smooth

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

-- visual-only part: no collision, no queries (raycasts), no touches
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
		TopSurface = SMOOTH,
		BottomSurface = SMOOTH,
	}, nil)
	if shape then
		p.Shape = shape
	end
	p.Parent = parent
	return p
end

local function v3(t)
	return Vector3.new(t[1], t[2], t[3])
end

------------------------------------------------------------------------------------------------ felt geometry
-- One spec felt piece in its hole's local frame. `base` = top-surface centre CFrame without the slope tilt.
local function makePiece(def)
	local c = v3(def.center)
	local yaw = math.rad(def.yaw or 0)
	local sl = def.slope
	local pc = {
		def = def,
		c = c,
		base = CFrame.new(c) * CFrame.Angles(0, yaw, 0),
		hx = def.size[1] / 2,
		hz = def.size[2] / 2,
		axis = sl and sl.axis or nil,
		rise = sl and sl.rise or 0,
		overlay = def.overlay == true,
		-- solid = false decks (Sugarloaf H16 upper deck, bridges): a lower level runs underneath, so no base block
		bridge = def.kind == "bridge" or def.solid == false,
		thickness = def.thickness,
	}
	if pc.axis == "x" then
		pc.tilt = CFrame.Angles(0, 0, math.atan2(pc.rise, def.size[1]))
	elseif pc.axis == "z" then
		pc.tilt = CFrame.Angles(-math.atan2(pc.rise, def.size[2]), 0, 0)
	else
		pc.tilt = CFrame.new()
	end
	return pc
end

-- surface height of a piece at hole-local (x, z), or nil when outside its footprint
local function pieceHeight(pc, x, z, eps)
	eps = eps or 1e-3
	local lp = pc.base:PointToObjectSpace(Vector3.new(x, pc.c.Y, z))
	if math.abs(lp.X) > pc.hx + eps or math.abs(lp.Z) > pc.hz + eps then
		return nil
	end
	if pc.axis == "x" then
		return pc.c.Y + pc.rise * lp.X / (2 * pc.hx)
	elseif pc.axis == "z" then
		return pc.c.Y + pc.rise * lp.Z / (2 * pc.hz)
	end
	return pc.c.Y
end

local function pieceMinTop(pc)
	return pc.c.Y - math.abs(pc.rise) / 2
end

------------------------------------------------------------------------------------------------ hole builder
local Hole = {}
Hole.__index = Hole

function Hole:W(x, y, z)
	return self.cf:PointToWorldSpace(Vector3.new(x, y, z))
end

function Hole:WCF(cf)
	return self.cf * cf
end

function Hole:folder(name)
	return new("Folder", { Name = name }, self.model)
end

function Hole:heightAt(x, z, includeOverlay)
	local best
	for _, pc in self.pieces do
		if pc.overlay and not includeOverlay then
			continue
		end
		local h = pieceHeight(pc, x, z)
		if h and (not best or h > best) then
			best = h
		end
	end
	return best
end

function Hole:feltColor(pc)
	local d = pc.def
	if d.color then
		return hex(d.color) -- (stage gg2: per-piece felt tint, used only by the bonus goose hole's zones)
	end
	if pc.overlay then
		return P.feltHi
	elseif d.kind == "tunnel" then
		return P.feltLo
	elseif d.zone == "green" or d.zone == "heart" or d.zone == "north" then
		return P.feltHi
	end
	-- lower levels read darker
	if pieceMinTop(pc) < self.feltMinLocal + 0.01 and self.feltMaxLocal - self.feltMinLocal > 0.9 then
		return P.feltLo
	end
	return P.felt
end

-- A bank meets the playable felt at its low edge. Resolve that adjacent surface
-- geometrically, so a bank's zone label cannot accidentally borrow the cup's tint.
function Hole:adjacentBankColor(pc)
	local sign = pc.rise >= 0 and -1 or 1
	local low = pc.base:PointToWorldSpace(Vector3.new(pc.axis == "x" and sign * pc.hx or 0,
		-math.abs(pc.rise) / 2, pc.axis == "z" and sign * pc.hz or 0))
	local best, bestDistance
	for _, other in self.pieces do
		if other ~= pc and not other.overlay then
			local angle = other.axis and math.deg(math.atan(math.abs(other.rise) /
				(other.axis == "x" and other.hx * 2 or other.hz * 2))) or 0
			if angle < 25 then
				local q = other.base:PointToObjectSpace(low)
				local x, z = math.clamp(q.X, -other.hx, other.hx), math.clamp(q.Z, -other.hz, other.hz)
				local near = other.base:PointToWorldSpace(Vector3.new(x, 0, z))
				near = Vector3.new(near.X, pieceHeight(other, near.X, near.Z) or other.c.Y, near.Z)
				local distance = (near - low).Magnitude
				if not bestDistance or distance < bestDistance then
					best, bestDistance = other, distance
				end
			end
		end
	end
	return self:feltColor(best or pc), best and best.def.id or pc.def.id
end

-- Sloped felt reads as sloped and shows which way is down (Chase, stage m; pattern C, stage n): any felt top tilted
-- between MIN_DEG and 25 degrees gets 3D Model Bot's one-way arrowhead felt (lantern-grove/models/textures/slope_felt_color.png,
-- 8 studs per tile, +V = downhill), baked into each felt tone by art/slope/make_slope_C.py. A Top-face Texture maps +U
-- to part -X and +V to part -Z and can't be turned, so each tone is uploaded in four rotations keyed by the part-local
-- downhill axis; the bright arrow tips point downhill. Plain Parts can't take a SurfaceAppearance, so the nap comes
-- from the Fabric material. Banks at 25 degrees or steeper use plain felt at 0.78x the adjacent felt colour (Game Art
-- Bot, round 7: same hue, darker); a shallower `kind = "bank"` piece keeps its chevrons, tinted 0.78x too.
local SLOPE_FELT = {
	MIN_DEG = 2,
	MAX_CHEVRON_DEG = 25,
	BANK_TINT = 0.78,
	STUDS_PER_TILE = 8,
	textures = {
		felt = {
			["-Z"] = "rbxassetid://73580481363879", -- slope_C_felt_r0
			["+X"] = "rbxassetid://129592782423546", -- slope_C_felt_r90
			["+Z"] = "rbxassetid://113253314312541", -- slope_C_felt_r180
			["-X"] = "rbxassetid://121717075552560", -- slope_C_felt_r270
		},
		feltHi = {
			["-Z"] = "rbxassetid://80509726173823",
			["+X"] = "rbxassetid://81751955839110",
			["+Z"] = "rbxassetid://131309615299067",
			["-X"] = "rbxassetid://117574107082616",
		},
		feltLo = {
			["-Z"] = "rbxassetid://89306582470432",
			["+X"] = "rbxassetid://124677910862174",
			["+Z"] = "rbxassetid://105060035224927",
			["-X"] = "rbxassetid://97307371441525",
		},
	},
}

-- the baked tone closest to a piece colour
local function slopeTone(color: Color3): string
	local best, bestD = "felt", math.huge
	for tone in SLOPE_FELT.textures do
		local c = P[tone]
		local d = (c.R - color.R) ^ 2 + (c.G - color.G) ^ 2 + (c.B - color.B) ^ 2
		if d < bestD then
			best, bestD = tone, d
		end
	end
	return best
end

-- Sugarloaf felt nap: the grayscale master tinted to the part colour (Color3 = colour / GRAY), on the Top face
local function tintedTexture(p: BasePart, id: string, color: Color3, name: string)
	local k = 1 / SUGARLOAF_FELT.GRAY
	return new("Texture", {
		Name = name,
		Face = Enum.NormalId.Top,
		Texture = id,
		StudsPerTileU = SUGARLOAF_FELT.studs,
		StudsPerTileV = SUGARLOAF_FELT.studs,
		Color3 = Color3.new(math.min(1, color.R * k), math.min(1, color.G * k), math.min(1, color.B * k)),
	}, p)
end

function Hole:slopeFelt(p: BasePart, color: Color3, pc)
	local n = p.CFrame.UpVector
	local tilt = math.deg(math.acos(math.clamp(n.Y, -1, 1)))
	if tilt <= SLOPE_FELT.MIN_DEG then
		if COURSE then
			tintedTexture(p, SUGARLOAF_FELT.flat, p.Color, "FeltNap")
		end
		return
	end
	p:SetAttribute("SlopeDeg", math.floor(tilt * 10 + 0.5) / 10)
	if tilt >= SLOPE_FELT.MAX_CHEVRON_DEG then
		local adjacentId
		color, adjacentId = self:adjacentBankColor(pc)
		p:SetAttribute("AdjacentFeltPiece", adjacentId)
		p:SetAttribute("AdjacentFeltColor", color)
		p.Color = Color3.new(color.R * SLOPE_FELT.BANK_TINT, color.G * SLOPE_FELT.BANK_TINT, color.B * SLOPE_FELT.BANK_TINT)
		p:SetAttribute("FeltPattern", "PlainBank")
		if COURSE then
			tintedTexture(p, SUGARLOAF_FELT.flat, p.Color, "FeltNap")
		end
		return
	end
	p:SetAttribute("FeltPattern", "ChevronC")
	-- downhill along the surface, in part space
	local down = p.CFrame:VectorToObjectSpace(Vector3.new(0, -1, 0) + n * n.Y)
	local key
	if math.abs(down.X) > math.abs(down.Z) then
		key = down.X > 0 and "+X" or "-X"
	else
		key = down.Z > 0 and "+Z" or "-Z"
	end
	local tex
	if COURSE then
		tex = tintedTexture(p, SUGARLOAF_FELT.slope[key], color, "SlopeFelt")
		tex.StudsPerTileU, tex.StudsPerTileV = SLOPE_FELT.STUDS_PER_TILE, SLOPE_FELT.STUDS_PER_TILE
	else
		tex = new("Texture", {
			Name = "SlopeFelt",
			Face = Enum.NormalId.Top,
			Texture = SLOPE_FELT.textures[slopeTone(color)][key],
			StudsPerTileU = SLOPE_FELT.STUDS_PER_TILE,
			StudsPerTileV = SLOPE_FELT.STUDS_PER_TILE,
		}, p)
	end
	if pc and pc.def and pc.def.kind == "bank" then
		local k = SLOPE_FELT.BANK_TINT
		tex.Color3 = Color3.new(tex.Color3.R * k, tex.Color3.G * k, tex.Color3.B * k)
		p.Color = Color3.new(color.R * k, color.G * k, color.B * k)
		p:SetAttribute("FeltPattern", "ChevronBank")
		p:SetAttribute("AdjacentFeltColor", color)
		return
	end
	p:SetAttribute("SlopeDeg", math.floor(tilt * 10 + 0.5) / 10)
end

function Hole:feltPart(name, cf, size, color, pc)
	local p = new("Part", {
		Name = name,
		Anchored = true,
		Size = size,
		CFrame = cf,
		Color = color,
		Material = M.Fabric,
		CustomPhysicalProperties = FELT_PHYS,
		TopSurface = SMOOTH,
		BottomSurface = SMOOTH,
	}, self.geo)
	p:SetAttribute("PieceId", pc.def.id)
	p:SetAttribute("Zone", pc.def.zone)
	p:SetAttribute("decel_scale", pc.def.decel_scale)
	CollectionService:AddTag(p, SURFACE_TAG)
	self:slopeFelt(p, color, pc)
	return p
end

-- A plain felt slab (sloped pieces are boxes tilted about the axis perpendicular to `slope.axis`).
function Hole:buildPiece(pc)
	local color = self:feltColor(pc)
	-- stage sc12: an exact hole-local pose for a piece whose tilt a single-axis slope cannot express (H15 lean3 terrace)
	if pc.def.cframe then
		self:feltPart("Felt", self.cf * CFrame.new(table.unpack(pc.def.cframe)), Vector3.new(table.unpack(pc.def.part_size)), color, pc)
		return
	end
	local sx, sz = pc.def.size[1], pc.def.size[2]
	if pc.axis == "x" then
		sx = math.sqrt(sx * sx + pc.rise * pc.rise)
	elseif pc.axis == "z" then
		sz = math.sqrt(sz * sz + pc.rise * pc.rise)
	end
	-- sloped (non-overlay) slabs are thicker so they reach down to the flat base below their low end
	local t = pc.thickness or FELT_T
	if pc.axis and not pc.overlay and not pc.bridge then
		t = t + math.abs(pc.rise)
	end
	local top = self.cf * pc.base * pc.tilt
	local felt = self:feltPart("Felt", top * CFrame.new(0, -t / 2, 0), Vector3.new(sx, t, sz), color, pc)
	if self.def.number == 9 and COURSE == nil and felt:GetAttribute("FeltPattern") == "PlainBank" then
		self:bankLip(felt)
	end
end

-- Lantern Grove H9: a 0.05-stud lip along the top edge of each bank, #6CC79F, no glow (Playtest Bot round 8 #3: bank
-- and felt are both very dark under H9's night lighting; an edge highlight reads better than a darker tint). Visual
-- only (no collision, no queries), plain SmoothPlastic, never Neon, no lights.
local BANK_LIP = { color = Color3.fromHex("6CC79F"), height = 0.05, width = 0.12 }
function Hole:bankLip(p: BasePart)
	local s = p.Size
	local best, bestY
	for _, e in { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } } do
		local y = p.CFrame:PointToWorldSpace(Vector3.new(e[1] * s.X / 2, s.Y / 2, e[2] * s.Z / 2)).Y
		if not bestY or y > bestY then
			best, bestY = e, y
		end
	end
	local W, H = BANK_LIP.width, BANK_LIP.height
	local size, off
	if best[1] ~= 0 then
		size, off = Vector3.new(W, H, s.Z), Vector3.new(best[1] * (s.X / 2 - W / 2), s.Y / 2 + H / 2, 0)
	else
		size, off = Vector3.new(s.X, H, W), Vector3.new(0, s.Y / 2 + H / 2, best[2] * (s.Z / 2 - W / 2))
	end
	local lip = vis("BankLip", p.CFrame * CFrame.new(off), size, BANK_LIP.color, M.SmoothPlastic, self.rails)
	lip.CastShadow = false
	lip:SetAttribute("PieceId", p:GetAttribute("PieceId"))
	return lip
end

-- A flat felt piece with the cup cut into it: four strips around a CSG plate.
function Hole:buildCupPiece(pc, cupLocal)
	local color = self:feltColor(pc)
	local lc = pc.base:PointToObjectSpace(cupLocal)
	local hx, hz = pc.hx, pc.hz
	local h = CUP_PLATE / 2
	local px0, px1 = math.max(-hx, lc.X - h), math.min(hx, lc.X + h)
	local pz0, pz1 = math.max(-hz, lc.Z - h), math.min(hz, lc.Z + h)
	local top = self.cf * pc.base
	local function strip(a0, a1, b0, b1)
		if a1 - a0 > 0.01 and b1 - b0 > 0.01 then
			self:feltPart("Felt", top * CFrame.new((a0 + a1) / 2, -FELT_T / 2, (b0 + b1) / 2), Vector3.new(a1 - a0, FELT_T, b1 - b0), color, pc)
		end
	end
	strip(-hx, px0, -hz, hz)
	strip(px1, hx, -hz, hz)
	strip(px0, px1, -hz, pz0)
	strip(px0, px1, pz1, hz)

	local radius = self.def.cup.radius or 0.5
	local plate = new("Part", {
		Anchored = true,
		Size = Vector3.new(px1 - px0, CUP_PLATE_T, pz1 - pz0),
		CFrame = top * CFrame.new((px0 + px1) / 2, -CUP_PLATE_T / 2, (pz0 + pz1) / 2),
	}, workspace)
	local cupWorld = self.cf:PointToWorldSpace(cupLocal)
	local cutterH = CUP_DEPTH + 0.2
	local cutter = new("Part", {
		Anchored = true,
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(cutterH, radius * 2, radius * 2),
		CFrame = CFrame.new(cupWorld + Vector3.new(0, -CUP_DEPTH + cutterH / 2, 0)) * CFrame.Angles(0, 0, math.rad(90)),
	}, workspace)
	local cup = GeometryService:SubtractAsync(plate, { cutter }, {
		CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition,
		RenderFidelity = Enum.RenderFidelity.Precise,
		SplitApart = false,
	})[1]
	plate:Destroy()
	cutter:Destroy()
	cup.Name = "CupPlate"
	cup.Anchored = true
	cup.UsePartColor = true
	cup.Color = color
	cup.Material = M.Fabric
	cup.CustomPhysicalProperties = FELT_PHYS
	cup:SetAttribute("PieceId", pc.def.id)
	cup:SetAttribute("Zone", pc.def.zone)
	cup:SetAttribute("decel_scale", pc.def.decel_scale)
	CollectionService:AddTag(cup, SURFACE_TAG)
	-- stage fx1: the same felt look as the strips around it (Sugarloaf's tinted FeltNap; CSG drops children)
	self:slopeFelt(cup, color, pc)
	cup.Parent = self.geo

	-- white liner (hollow, visual only) + dark bottom
	local linerH = CUP_DEPTH - 0.03
	local linerCF = CFrame.new(cupWorld + Vector3.new(0, -0.015 - linerH / 2, 0)) * CFrame.Angles(0, 0, math.rad(90))
	local outer = new("Part", {
		Anchored = true,
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(linerH, radius * 2 - 0.004, radius * 2 - 0.004),
		CFrame = linerCF,
	}, workspace)
	local inner = new("Part", {
		Anchored = true,
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(linerH + 0.2, radius * 2 - 0.04, radius * 2 - 0.04),
		CFrame = linerCF,
	}, workspace)
	local liner = GeometryService:SubtractAsync(outer, { inner }, { CollisionFidelity = Enum.CollisionFidelity.Box, SplitApart = false })[1]
	outer:Destroy()
	inner:Destroy()
	liner.Name = "CupLiner"
	liner.Anchored = true
	liner.CanCollide = false
	liner.CanQuery = false
	liner.CanTouch = false
	liner.UsePartColor = true
	liner.Color = Color3.fromRGB(250, 250, 250)
	liner.Parent = self.geo
	vis("CupBottom", CFrame.new(cupWorld + Vector3.new(0, -CUP_DEPTH + 0.006, 0)) * CFrame.Angles(0, 0, math.rad(90)),
		Vector3.new(0.01, radius * 2 - 0.01, radius * 2 - 0.01), Color3.fromRGB(45, 45, 45), M.SmoothPlastic, self.geo, Enum.PartType.Cylinder)

	local marker = vis("Cup", CFrame.new(cupWorld), Vector3.new(0.2, 0.2, 0.2), Color3.new(1, 1, 1), M.SmoothPlastic, self.model)
	marker.Transparency = 1
	marker:SetAttribute("Radius", radius)

	-- flag on a pole standing in the cup (spec cup.flag: pole_height above the cup felt, banner at the top, turned to
	-- face the tee; visual only, like every vis() part: no collision, the ball passes through)
	local fs = self.def.cup.flag or {}
	local poleH = (fs.pole_height or 5) + CUP_DEPTH
	local poleD = fs.pole_diameter or 0.06
	local bs = fs.banner_size or { 1.4, 0.9, 0.03 }
	local poleBase = cupWorld.Y - CUP_DEPTH
	vis("FlagPole", CFrame.new(cupWorld.X, poleBase + poleH / 2, cupWorld.Z) * CFrame.Angles(0, 0, math.rad(90)),
		Vector3.new(poleH, poleD, poleD), Color3.fromRGB(245, 245, 245), M.SmoothPlastic, self.model, Enum.PartType.Cylinder)
	local teeW = self.cf:PointToWorldSpace(v3(self.def.tee.position))
	local toTee = Vector3.new(teeW.X - cupWorld.X, 0, teeW.Z - cupWorld.Z)
	toTee = toTee.Magnitude > 0.1 and toTee.Unit or Vector3.zAxis
	-- banner face toward the tee, flying out to the side of the pole
	local face = CFrame.lookAt(Vector3.zero, -toTee)
	local flagCF = CFrame.new(cupWorld.X, poleBase + poleH - bs[2] / 2 - 0.05, cupWorld.Z) * face * CFrame.new(bs[1] / 2 + poleD / 2, 0, 0)
	local flag = vis("Flag", flagCF, Vector3.new(bs[1], bs[2], bs[3]), fs.banner_color and Color3.fromHex(fs.banner_color) or P.amber, M.SmoothPlastic, self.model)
	for _, face in { Enum.NormalId.Front, Enum.NormalId.Back } do
		local gui = new("SurfaceGui", { Face = face, CanvasSize = Vector2.new(140, 90), LightInfluence = 0 }, flag)
		new("TextLabel", {
			Size = UDim2.fromScale(1, 1),
			BackgroundTransparency = 1,
			Text = tostring(self.def.number),
			TextScaled = true,
			Font = Enum.Font.FredokaOne,
			TextColor3 = fs.banner_color and Color3.new(1, 1, 1) or P.bark,
		}, gui)
	end
end

-- A cup near the edge of its piece also cuts into the neighbouring felt: split that slab along its long axis into the
-- part clear of the cup and a strip around it, and subtract the cup cylinder from the strip (only the strip becomes a
-- CSG part, so the rest keeps its felt texture).
function Hole:cutNeighbourCup(cupLocal)
	local radius = self.def.cup.radius or 0.5
	local cupWorld = self.cf:PointToWorldSpace(cupLocal)
	for _, p in self.geo:GetChildren() do
		if p.Name ~= "Felt" or not p:IsA("Part") then
			continue
		end
		local lp = p.CFrame:PointToObjectSpace(cupWorld)
		local h = p.Size / 2
		local dx = math.max(0, math.abs(lp.X) - h.X)
		local dz = math.max(0, math.abs(lp.Z) - h.Z)
		if dx * dx + dz * dz >= radius * radius or math.abs(lp.Y) > h.Y + 1 then
			continue
		end
		-- strip across the axis the cup is NOT near the edge of
		local alongZ = math.abs(lp.X) > h.X - radius
		local c = alongZ and lp.Z or lp.X
		local half = alongZ and h.Z or h.X
		local a0, a1 = math.max(-half, c - radius - 0.6), math.min(half, c + radius + 0.6)
		local function sub(b0, b1)
			if b1 - b0 < 0.01 then
				return nil
			end
			local q = p:Clone()
			local mid = (b0 + b1) / 2
			q.Size = alongZ and Vector3.new(p.Size.X, p.Size.Y, b1 - b0) or Vector3.new(b1 - b0, p.Size.Y, p.Size.Z)
			q.CFrame = p.CFrame * (alongZ and CFrame.new(0, 0, mid) or CFrame.new(mid, 0, 0))
			q.Parent = self.geo
			return q
		end
		sub(-half, a0)
		sub(a1, half)
		local strip = sub(a0, a1)
		p:Destroy()
		local cutterH = CUP_DEPTH + 2
		local cutter = new("Part", {
			Anchored = true,
			Shape = Enum.PartType.Cylinder,
			Size = Vector3.new(cutterH, radius * 2, radius * 2),
			CFrame = CFrame.new(cupWorld + Vector3.new(0, -CUP_DEPTH + cutterH / 2, 0)) * CFrame.Angles(0, 0, math.rad(90)),
		}, workspace)
		local cut = GeometryService:SubtractAsync(strip, { cutter }, {
			CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition,
			RenderFidelity = Enum.RenderFidelity.Precise,
			SplitApart = false,
		})[1]
		cutter:Destroy()
		cut.Name = "Felt"
		cut.Anchored = true
		cut.UsePartColor = true
		cut.Color = strip.Color
		cut.Material = strip.Material
		cut.CustomPhysicalProperties = FELT_PHYS
		for k, v in strip:GetAttributes() do
			cut:SetAttribute(k, v)
		end
		cut:SetAttribute("CupCut", true)
		-- stage fx1: SubtractAsync drops children; keep the strip's felt textures
		for _, d in strip:GetChildren() do
			if d:IsA("Texture") or d:IsA("Decal") then
				d:Clone().Parent = cut
			end
		end
		CollectionService:AddTag(cut, SURFACE_TAG)
		strip:Destroy()
		cut.Parent = self.geo
	end
end

-- Base blocks under the felt, down to the lawn: they are the cliff faces between levels, so they collide
-- (GolfWall: the ball bounces off them like a rail, players pass through).
function Hole:buildBase(pc)
	local topY = pieceMinTop(pc) - FELT_T
	local bottom = self.lawnTopLocal
	if topY - bottom < 0.05 then
		return
	end
	local h = topY - bottom
	local cf = self.cf * CFrame.new(pc.c.X, bottom + h / 2, pc.c.Z) * CFrame.Angles(0, math.rad(pc.def.yaw or 0), 0)
	local p = new("Part", {
		Name = "Base",
		Anchored = true,
		Size = Vector3.new(pc.def.size[1], h, pc.def.size[2]),
		CFrame = cf,
		Color = P.bark,
		Material = M.WoodPlanks,
		CustomPhysicalProperties = wallPhys(Config, Config.WallElasticity),
		TopSurface = SMOOTH,
		BottomSurface = SMOOTH,
	}, self.geo)
	p:SetAttribute("PieceId", pc.def.id)
end

------------------------------------------------------------------------------------------------ walls + rails
-- Gaps cut into a visual rail (hole-local x or z range along the rail), where a decoration mesh passes through it:
-- the H6 mill wheel's rims and paddles cross the north rail (rail5) at x 5..10 (models/README.md). Collision walls
-- are untouched.
-- H8: the root door's open end slides 2.05 past rail16 into the south door pocket (models pass 8: x 4.2..5.3; stage v
-- widened the west cut to 5.6 so the tilted cut face keeps >= 0.15 studs from the door; the placed h8_door_pocket
-- prop was also widened x1.4, raised 0.17 and moved 0.05 deeper in Studio for the same clearance).
local H9_RAIL_WOOD = Color3.fromHex("7A4E32")
local RAIL_NOTCHES = {
	[6] = { rail5 = { axis = "x", from = 5, to = 10 } },
	[8] = { rail16 = { axis = "x", from = 4.2, to = 5.6 } },
}
-- per-hole rail skins (3D Model Bot manifest hole_skins, via tools/props_to_lua.py into CourseData.PropPlacements)
local RAIL_SKINS = {}
do
	-- (by path, cloned: the build step requires a clone of this module, and the command bar caches modules)
	local ok, pp = pcall(function()
		return require(game:GetService("ServerStorage").CourseData.PropPlacements:Clone())
	end)
	if ok and type(pp) == "table" and pp.skins then
		for k, v in pp.skins do
			RAIL_SKINS[tonumber(k)] = v
		end
	end
end

local function wallStyle(w)
	local id = w.id
	if w.kind == "bumper" then
		if string.find(id, "stump") then
			return P.bark, M.Wood
		elseif string.find(id, "hub") then
			return P.cream, M.SmoothPlastic
		elseif string.find(id, "toadstool") then
			return P.toadstool, M.SmoothPlastic
		elseif string.find(id, "post") then
			return P.oak, M.Wood
		end
		return P.slate, M.Slate
	end
	if string.find(id, "deflector") or string.find(id, "board") then
		return P.oak, M.WoodPlanks
	elseif string.find(id, "backing") then
		-- the bank backing face reads as stone (Playtest Bot round 8 #1, stage w): the bank_backing_stone prop sits
		-- inside this rail, so the rail face itself is limestone; the prop carries the oak cap
		return P.limestone, M.Limestone
	end
	return P.limestone, M.Limestone
end

-- Sugarloaf wall families (holes.json ids, with __cutN suffixes from the mover collision cuts): body colour,
-- material, timber cap?, transparency
local function sugarloafWallStyle(w)
	local id = w.id
	local function has(k)
		return string.find(id, k, 1, true) ~= nil
	end
	if has("crystal") then
		return P.candy, M.Glass, false, 0.25
	elseif has("gumdrop") then
		return hex("F78FB3"), M.SmoothPlastic, false
	elseif has("hoodoo") then
		return hex("CC8D91"), M.Sandstone, false
	elseif has("boulder") then
		return hex("E8736B"), M.Sandstone, false
	elseif has("gnomon_plinth") or has("hour_stone") then
		return hex("E8C9A1"), M.Sandstone, false
	elseif has("rock") or has("pocket") then
		return hex("C68C59"), M.Sandstone, false
	elseif has("rope_rail") or has("bridge_rail") or has("house") then
		return P.oak, M.WoodPlanks, false
	elseif has("quay") or has("gate_approach") then
		return P.cream, M.Concrete, true
	end
	return P.limestone, M.Sandstone, true
end

-- Sugarloaf mover clearance trims (stage w): the H9 pump-house front walls either side of the tunnel (rail2, house13)
-- and the tunnel side walls (rail3, house18) ended at z = -18.0, 0.05 from the windpump vane colliders (z -17.95); the
-- H9/H14 blocker rule is >= 0.06, so those faces move to z = -18.01 (hole-local, axis-aligned walls only).
local SUGARLOAF_TRIMS = {
	[9] = { rail2 = { zmax = -18.01 }, house13 = { zmax = -18.01 }, rail3 = { zmax = -18.01 }, house18 = { zmax = -18.01 } },
}
local function trimWall(w, t)
	local yaw = (w.yaw or 0) % 180
	assert(yaw == 0 or yaw == 90, "trimWall: axis-aligned walls only")
	local ex, ez = w.size[1], w.size[3]
	if yaw == 90 then
		ex, ez = w.size[3], w.size[1]
	end
	local z0, z1 = w.center[3] - ez / 2, w.center[3] + ez / 2
	z1 = t.zmax and math.min(z1, t.zmax) or z1
	z0 = t.zmin and math.max(z0, t.zmin) or z0
	local out = table.clone(w)
	out.center = { w.center[1], w.center[2], (z0 + z1) / 2 }
	out.size = { ex, w.size[2], z1 - z0 }
	out.yaw = 0
	out.trimmed = true
	return out
end

function Hole:buildWall(w)
	local trim = COURSE and SUGARLOAF_TRIMS[self.def.number] and SUGARLOAF_TRIMS[self.def.number][w.id]
	if trim then
		w = trimWall(w, trim)
	end
	local c = v3(w.center)
	local size = v3(w.size)
	local cf = CFrame.new(c) * CFrame.Angles(0, math.rad(w.yaw or 0), 0)
	local bumper = w.kind == "bumper"
	local p = new("Part", {
		Name = bumper and "Bumper" or "Wall",
		Anchored = true,
		Size = size,
		CFrame = self.cf * cf,
		Transparency = 1,
		CanTouch = false,
		CastShadow = false,
		CustomPhysicalProperties = wallPhys(Config, bumper and Config.BumperElasticity or Config.WallElasticity),
		TopSurface = SMOOTH,
		BottomSurface = SMOOTH,
	}, self.geo)
	p:SetAttribute("WallId", w.id)
	if w.hour_stone then
		p:SetAttribute("HourStone", w.hour_stone == true and w.id or tostring(w.hour_stone))
	end

	if BLOCKOUT then
		local body = vis("Rail_" .. w.id, self.cf * cf, size, P.limestone, M.SmoothPlastic, self.rails)
		body:SetAttribute("WallId", w.id)
		return
	end
	if COURSE then
		-- Sugarloaf: the visual is exactly the collision box (its cut pieces included), so what you see is what the
		-- ball hits and the 0.15 mover clearance holds for the visuals too; plain rails get a timber cap inset at the top
		local color, material, cap, transp = sugarloafWallStyle(w)
		local body = vis((bumper and "Bumper_" or "Rail_") .. w.id, self.cf * cf, size, color, material, self.rails)
		body:SetAttribute("WallId", w.id)
		if transp then
			body.Transparency = transp
			body.CastShadow = false
		end
		if cap and size.Y > 0.3 and size.X > 0.1 and size.Z > 0.1 then
			local capT = 0.12
			local capPart = vis("RailCap_" .. w.id, self.cf * cf * CFrame.new(0, size.Y / 2 - capT / 2 + 0.02, 0), Vector3.new(size.X, capT, size.Z), P.oak, M.WoodPlanks, self.rails)
			capPart:SetAttribute("WallId", w.id)
			capPart:SetAttribute("StageAjRaised", true)
		end
		return
	end

	local color, material = wallStyle(w)
	local bottom = self.lawnTopLocal
	if bumper then
		local top = c.Y + size.Y / 2
		local h = top - bottom
		local vp = vis("Bumper_" .. w.id, self.cf * CFrame.new(c.X, bottom + h / 2, c.Z) * CFrame.Angles(0, math.rad(w.yaw or 0), 0),
			Vector3.new(size.X, h, size.Z), color, material, self.rails)
		vp:SetAttribute("WallId", w.id)
		return
	end
	-- visual rail: RAIL_H above the felt it borders (sampled on both sides near each end), following ramps
	local L, thick = size.Z, size.X
	local wallTop = c.Y + size.Y / 2
	local function topAt(s)
		local best
		for _, side in { -1, 1 } do
			for _, d in { thick / 2 + 0.15, thick / 2 + 0.6 } do
				local pt = cf:PointToWorldSpace(Vector3.new(side * d, 0, s))
				local hh = self:heightAt(pt.X, pt.Z, true)
				if hh and (not best or hh > best) then
					best = hh
				end
			end
		end
		return best and math.min(wallTop, best + RAIL_H) or nil
	end
	local s0 = math.max(-L / 2 + 0.3, -L / 2 + L * 0.1)
	local s1 = -s0
	local t0, t1 = topAt(s0), topAt(s1)
	t0 = t0 or t1 or math.min(wallTop, c.Y + RAIL_H)
	t1 = t1 or t0
	-- extrapolate to the ends
	local slope = (s1 - s0) > 1e-3 and (t1 - t0) / (s1 - s0) or 0
	if math.abs(slope) < 0.004 then
		slope = 0
		t0 = math.max(t0, t1)
		t1 = t0
	end
	local tA = t0 + slope * (-L / 2 - s0)
	local tB = t0 + slope * (L / 2 - s0)
	local midTop = (tA + tB) / 2
	local ang = math.atan2(tB - tA, L)
	local len = L / math.cos(ang)
	local capT = 0.12
	local bodyH = midTop - capT - bottom
	local tilt = CFrame.new(c.X, midTop, c.Z) * CFrame.Angles(0, math.rad(w.yaw or 0), 0) * CFrame.Angles(-ang, 0, 0)
	-- pieces along the rail (s = distance along its local Z, from -len/2 to len/2), minus any notch
	local pieces = { { -len / 2, len / 2 } }
	local notch = COURSE == nil and RAIL_NOTCHES[self.def.number] and RAIL_NOTCHES[self.def.number][w.id]
	if notch then
		local function sAt(v)
			local probe = notch.axis == "x" and Vector3.new(v, c.Y, c.Z) or Vector3.new(c.X, c.Y, v)
			return cf:PointToObjectSpace(probe).Z
		end
		-- horizontal distance along the rail -> distance along the tilted rail kit, measured low on the body (where
		-- the crossing mesh passes; the cut faces are square to the tilted rail)
		local h0 = cf:PointToObjectSpace((tilt * CFrame.new(0, -capT - bodyH * 0.8, 0)).Position).Z
		local n0, n1 = (sAt(notch.from) - h0) / math.cos(ang), (sAt(notch.to) - h0) / math.cos(ang)
		n0, n1 = math.min(n0, n1), math.max(n0, n1)
		pieces = {}
		if n0 > -len / 2 + 0.05 then
			table.insert(pieces, { -len / 2, n0 })
		end
		if n1 < len / 2 - 0.05 then
			table.insert(pieces, { n1, len / 2 })
		end
	end
	-- no cap on deflector boards, and none on bank backings: their bank_backing_stone prop has its own oak cap (two
	-- caps 0.15 apart z-fought, round 8 #1)
	local backing = string.find(w.id, "backing") ~= nil
	local capped = not string.find(w.id, "deflector") and not string.find(w.id, "board") and not backing
	-- the hole's rail-kit skin (manifest hole_skins: H8/H9 cream trim) on plain limestone rails
	local skin = COURSE == nil and RAIL_SKINS[self.def.number] or nil
	local plain = color == P.limestone and material == M.Limestone and not backing
	local capColor, capMat = P.oak, M.Wood
	if skin and plain then
		-- (stage ab, Game Art Bot) H8's old cream #DDD3BE block is retired: its plain rails stay limestone like H1-H7
		if self.def.number ~= 8 then
			color = skin.rail_block_color and Color3.fromHex(skin.rail_block_color) or color
			material = skin.rail_block_roblox_material and Enum.Material[skin.rail_block_roblox_material] or material
		end
		capColor = skin.rail_cap_color and Color3.fromHex(skin.rail_cap_color) or capColor
		capMat = skin.rail_cap_roblox_material and Enum.Material[skin.rail_cap_roblox_material] or capMat
	end
	-- H9 (under the heart-well lantern): rail tops and faces are oak #7A4E32, Reflectance 0 (Game Art Bot round 7,
	-- stage v; Playtest Bot round 8 #2, stage w: the cream limestone skin is gone). Limestone stays only on the bank
	-- backing (and posts).
	if self.def.number == 9 and self.course == nil then
		if not backing then
			color, material = H9_RAIL_WOOD, M.WoodPlanks
		end
		capColor, capMat = H9_RAIL_WOOD, M.Wood
		skin = nil
	end
	for _, pc in pieces do
		local mid, l = (pc[1] + pc[2]) / 2, pc[2] - pc[1]
		local body = vis("Rail_" .. w.id, self.cf * tilt * CFrame.new(0, -capT - bodyH / 2, mid), Vector3.new(thick, bodyH, l), color, material, self.rails)
		body:SetAttribute("WallId", w.id)
		if skin and plain then
			-- which rail-kit piece this stands in for (Playtest Bot checks props by manifest name)
			body:SetAttribute("ManifestProp", l >= 3 and skin.rail_straight_4 or skin.rail_straight_2)
		end
		if capped then
			vis("RailCap_" .. w.id, self.cf * tilt * CFrame.new(0, -capT / 2, mid), Vector3.new(thick + 0.08, capT, l + 0.04), capColor, capMat, self.rails)
		end
	end
end

------------------------------------------------------------------------------------------------ moving parts
-- spec value / cycle of a moving part (shared with GolfServer.Movers and the harness): ReplicatedStorage.Golf.MoverMath
local function moverProfile(m)
	return { type = m.type, speed = m.speed, phase = m.phase_s or m.phase or 0, solidStart = m.solid_window and m.solid_window[1], solidEnd = m.solid_window and m.solid_window[2], range = m.range, period = m.period_s, amplitude = m.amplitude_deg, dwell = m.dwell, keys = m.keys }
end

-- Sugarloaf H11's timetable movers (holes.json `schedule`) as keyframed slides along their axis (MoverMath "keys"):
--   lift:     deck down until rise[1], up `height` by rise[2], level until return_[1], down by return_[2]
--   quay_lip: top at 0 except the `flush` interval, where it is sunk 1 stud (top y 5 -> 4), moving at `speed` studs/s
local function normalizeMover(m)
	if m.type == "lift" then
		local sc = m.schedule
		local h = sc.height or 4
		m = table.clone(m)
		m.type = "keys"
		m.keys = { { t = 0, v = 0 }, { t = sc.rise[1], v = 0 }, { t = sc.rise[2], v = h }, { t = sc.return_[1], v = h }, { t = sc.return_[2], v = 0 }, { t = m.period_s, v = 0 } }
		m.range = { 0, h }
		m.speed = m.speed or h / (sc.rise[2] - sc.rise[1])
	elseif m.type == "quay_lip" then
		local f = m.schedule.flush
		local drop, ramp = 1, 1 / (m.speed or 10)
		m = table.clone(m)
		m.type = "keys"
		m.keys = { { t = 0, v = 0 }, { t = f[1] - ramp, v = 0 }, { t = f[1], v = -drop }, { t = f[2], v = -drop }, { t = f[2] + ramp, v = 0 }, { t = m.period_s, v = 0 } }
		m.range = { -drop, 0 }
	end
	return m
end
CourseBuilder.normalizeMover = normalizeMover
local function moverValue(m, t)
	return MoverMath.value(moverProfile(m), t)
end
CourseBuilder.moverValue = moverValue

local function moverPeriod(m)
	return MoverMath.period(moverProfile(m))
end

local function axisFrame(pos, axis)
	axis = axis.Unit
	local ref = math.abs(axis.Y) < 0.9 and Vector3.yAxis or Vector3.xAxis
	local y = (ref - axis * ref:Dot(axis)).Unit
	return CFrame.fromMatrix(pos, axis, y)
end

local MOVER_STYLE = {
	-- Sugarloaf Canyon (stand-ins until the pass 5 mover meshes are welded on; SugarloafMeshes)
	sluice_gate = { Color3.fromHex("8A5A33"), M.WoodPlanks },
	windpump = { Color3.fromHex("F78FB3"), M.SmoothPlastic },
	lock_gate = { Color3.fromHex("8A5A33"), M.WoodPlanks },
	lock_lift_deck = { Color3.fromHex("8A5A33"), M.WoodPlanks },
	quay_lip = { Color3.fromHex("D9343A"), M.SmoothPlastic },
	ore_bucket = { Color3.fromHex("3B3A3F"), M.Metal },
	shadow_arm = { Color3.fromHex("5E6470"), M.Slate },
	spinner = { P.cream, M.SmoothPlastic },
	millwheel = { P.oak, M.WoodPlanks },
	log = { P.bark, M.Wood },
	root_door = { P.bark, M.Wood },
	root_gate = { P.bark, M.Wood },
	lantern_bar = { P.oak, M.Wood },
	lantern_pendulum = { P.paper, M.SmoothPlastic },
}

-- Clearance gap: a sliding blocker must stop SLIDE_CLEARANCE short of any rail/bumper ahead of it (0.5 studs, ~3 ball
-- diameters, per Playtest Bot; a spec mover may set its own `clearance` / `end_clearance`), so a ball can never be squeezed between the
-- two (the spec's H8 root door slid 0.6 studs into the alcove rails and crushed balls parked against them). Walls the blocker already overlaps at offset 0 are ignored (e.g. the
-- H9 root gate's ends sit inside the corridor rails and slide vertically along them).
local SLIDE_CLEARANCE = 0.5
function Hole:clampSlideRange(m, blockers, axis)
	-- (Sugarloaf: the course-wide 0.15 mover clearance; its holes.json already carries the collision cuts for it)
	local clearance = m.clearance or m.end_clearance or (COURSE and 0.15 or SLIDE_CLEARANCE)
	local walls = {}
	for _, d in self.geo:GetChildren() do
		if d:IsA("BasePart") and (d.Name == "Wall" or d.Name == "Bumper") then
			table.insert(walls, d)
		end
	end
	local function pts(cf, size)
		local out = {}
		local f = { -1, -0.5, 0, 0.5, 1 }
		for _, i in f do
			for _, j in f do
				for _, k in f do
					if math.abs(i) == 1 or math.abs(j) == 1 or math.abs(k) == 1 then
						table.insert(out, cf:PointToWorldSpace(Vector3.new(i * size.X / 2, j * size.Y / 2, k * size.Z / 2)))
					end
				end
			end
		end
		return out
	end
	local function hits(off, sign, wall)
		for _, b in blockers do
			for _, p in pts(b.cf + axis * (off + sign * clearance), b.size) do
				local lp = wall.CFrame:PointToObjectSpace(p)
				local h = wall.Size / 2
				if math.abs(lp.X) < h.X and math.abs(lp.Y) < h.Y and math.abs(lp.Z) < h.Z then
					return true
				end
			end
		end
		return false
	end
	-- Pocket: a wall the blocker passes right THROUGH by the spec end of its travel (its leading face ends beyond
	-- the wall's far face, e.g. H8's root door sliding into pockets in the knot walls) cannot pinch the ball against
	-- it, so the travel is not clamped there (movers don't collide with walls; BallController.pushFromSliding moves a
	-- ball out of the way of a blocker end closing on a wall).
	local function lead(off, sign)
		local best = -math.huge
		for _, bb in blockers do
			for _, p in pts(bb.cf + axis * off, bb.size) do
				best = math.max(best, p:Dot(axis) * sign)
			end
		end
		return best
	end
	local function farFace(w, sign)
		local best = -math.huge
		for _, p in pts(w.CFrame, w.Size) do
			best = math.max(best, p:Dot(axis) * sign)
		end
		return best
	end
	local lo, hi = m.range[1], m.range[2]
	local out = { lo, hi }
	for idx, sign in { [1] = -1, [2] = 1 } do
		local target = sign > 0 and hi or lo
		local ahead = {}
		for _, w in walls do
			if not hits(0, sign, w) then
				local crossed = false
				if lead(target, sign) > farFace(w, sign) + 0.05 then
					for o = 0, math.abs(target), 0.05 do
						if hits(sign * o, sign, w) then
							crossed = true
							break
						end
					end
				end
				if crossed then
					print(string.format("CourseBuilder: hole %d %s slides through %s into a pocket (offset %g)", self.def.number, m.id, w:GetAttribute("WallId") or w.Name, target))
				else
					table.insert(ahead, w)
				end
			end
		end
		local o = 0
		while (sign > 0 and o < target) or (sign < 0 and o > target) do
			local nxt = o + sign * 0.02
			if (sign > 0 and nxt > target) or (sign < 0 and nxt < target) then
				nxt = target
			end
			local blocked = false
			for _, w in ahead do
				if hits(nxt, sign, w) then
					blocked = true
					break
				end
			end
			if blocked then
				break
			end
			o = nxt
		end
		out[idx] = math.floor(o * 100 + 0.5) / 100
	end
	return out
end

-- Lantern Grove block-rate tuning (stage w, Playtest Bot round 8 #5: H7 and H8 sat at 50%, the top of the band;
-- target ~44% over 24 shots): shorter dwells where the blocker sits in the intended line, same speeds and travel.
--   H7 log: the +6 end stop (in the ball's path) 1.5 -> 1.025 s; H8 root door: the closed stop 1.8 -> 1.1 s.
--   Measured (blockrate, 24 aimed shots per run; one run varies +-2 with the phase grid): H7 1.0 s 9/11/9,
--   1.025 s 10/11/12 (45.8%), 1.05 s 12/13/9, 1.1 s 10/13; H8 1.1 s 11/24 twice (playtests/stage-w).
-- (dwell `at` values at the spec range ends follow the clearance-clamped ends, see buildMover)
local LG_DWELL = {
	[7] = { log = { { at = -6, s = 1.0 }, { at = 6, s = 1.025 } } },
	[8] = { root_door = { { at = 0, s = 1.1 }, { at = 4, s = 2.2 } } },
}

function Hole:buildMover(m)
	if m.type == "toggle" then
		assert(m.period_s > 0 and m.solid_window, "toggle requires period and solid_window")
		local model = new("Model", { Name = "Mover_" .. m.id }, self.movers)
		model:SetAttribute("MoverId", m.id)
		model:SetAttribute("Type", "toggle")
		model:SetAttribute("Period", m.period_s)
		model:SetAttribute("Phase", m.phase_s or 0)
		model:SetAttribute("SolidStart", m.solid_window[1])
		model:SetAttribute("SolidEnd", m.solid_window[2])
		for _, segment in m.profile or {} do
			model:SetAttribute("Profile_" .. segment.state, segment.s)
		end
		model:SetAttribute("PivotWorld", self.cf:PointToWorldSpace(v3(m.pivot)))
		model:SetAttribute("AxisWorld", self.cf:VectorToWorldSpace(v3(m.axis)))
		local ids = {}
		for _, id in m.felt_ids do ids[id] = true end
		local solid = MoverMath.value(MoverMath.fromModel(model), workspace:GetServerTimeNow()) == 1
		local count = 0
		for _, part in self.geo:GetDescendants() do
			if part:IsA("BasePart") and ids[part:GetAttribute("PieceId")] and CollectionService:HasTag(part, SURFACE_TAG) then
				new("ObjectValue", { Name = "TogglePart", Value = part }, model)
				part.CanCollide, part.CanQuery, part.CanTouch = solid, solid, solid
				count += 1
			end
		end
		assert(count > 0, "toggle has no matching felt")
		CollectionService:AddTag(model, MOVER_TAG)
		return model
	end
	m = normalizeMover(m)
	local tune = COURSE == nil and LG_DWELL[self.def.number] and LG_DWELL[self.def.number][m.id]
	if tune then
		m = table.clone(m)
		m.spec_dwell = m.dwell
		m.dwell = tune
	end
	local model = new("Model", { Name = "Mover_" .. m.id }, self.movers)
	local pivotLocal = v3(m.pivot)
	local axisLocal = v3(m.axis).Unit
	local pivot = self.cf:PointToWorldSpace(pivotLocal)
	local axis = self.cf:VectorToWorldSpace(axisLocal)
	local frame = axisFrame(pivot, axis)

	local base = vis("MoverBase", frame, Vector3.new(0.3, 0.3, 0.3), P.bark, M.SmoothPlastic, model)
	base.Transparency = 1
	local root = new("Part", {
		Name = "MoverRoot",
		Anchored = false,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Transparency = 1,
		Size = Vector3.new(0.4, 0.4, 0.4),
		CFrame = frame,
		CustomPhysicalProperties = PhysicalProperties.new(2, 0.3, 0, 1, 1),
	}, model)
	model.PrimaryPart = root
	if not BLOCKOUT and m.type == "slide" and m.range then
		local bl = {}
		for _, b in m.blockers do
			local rollRot = b.roll and CFrame.fromAxisAngle(axisLocal, math.rad(b.roll)) or CFrame.new()
			table.insert(bl, { cf = self.cf * CFrame.new(pivotLocal) * rollRot * CFrame.new(v3(b.center)) * CFrame.Angles(0, math.rad(b.yaw or 0), 0), size = v3(b.size) })
		end
		local r = self:clampSlideRange(m, bl, axis)
		if math.abs(r[1] - m.range[1]) > 1e-3 or math.abs(r[2] - m.range[2]) > 1e-3 then
			model:SetAttribute("SpecRange", Vector2.new(m.range[1], m.range[2]))
			print(string.format("CourseBuilder: hole %d %s range [%g, %g] -> [%g, %g] (clearance %.2f to the rails)",
				self.def.number, m.id, m.range[1], m.range[2], r[1], r[2], m.clearance or m.end_clearance or (COURSE and 0.15 or SLIDE_CLEARANCE)))
			-- dwell stops at the spec range ends move with the clamped ends
			local dwell = nil
			for _, d in m.dwell or {} do
				local at = d.at
				if math.abs(at - m.range[1]) < 1e-3 then
					at = r[1]
				elseif math.abs(at - m.range[2]) < 1e-3 then
					at = r[2]
				end
				dwell = dwell or {}
				table.insert(dwell, { at = at, s = d.s })
			end
			m = table.clone(m)
			m.range = r
			m.dwell = dwell
		end
	end
	local a0 = new("Attachment", { Name = "A0" }, base)
	local a1 = new("Attachment", { Name = "A1" }, root)
	local constraint
	if m.type == "rotate" or m.type == "swing" then
		constraint = new("HingeConstraint", {
			Name = "Drive",
			Attachment0 = a0,
			Attachment1 = a1,
			ActuatorType = Enum.ActuatorType.Motor,
			MotorMaxTorque = 1e9,
			MotorMaxAcceleration = math.huge,
			AngularVelocity = 0,
		}, model)
	else
		constraint = new("PrismaticConstraint", {
			Name = "Drive",
			Attachment0 = a0,
			Attachment1 = a1,
			ActuatorType = Enum.ActuatorType.Motor,
			MotorMaxForce = 1e9,
			MotorMaxAcceleration = math.huge,
			Velocity = 0,
			LimitsEnabled = m.range ~= nil,
			LowerLimit = m.range and m.range[1] - 0.05 or 0,
			UpperLimit = m.range and m.range[2] + 0.05 or 0,
		}, model)
	end

	local style = MOVER_STYLE[m.id] or { P.oak, M.Wood }
	local phys = wallPhys(Config, Config.WallElasticity)
	for i, b in m.blockers do
		local rollRot = b.roll and CFrame.fromAxisAngle(axisLocal, math.rad(b.roll)) or CFrame.new()
		local rel = rollRot * CFrame.new(v3(b.center)) * CFrame.Angles(0, math.rad(b.yaw or 0), 0)
		local cf = self.cf * CFrame.new(pivotLocal) * rel
		local size = v3(b.size)
		local blk = new("Part", {
			Name = "Blocker",
			Anchored = false,
			Size = size,
			CFrame = cf,
			Transparency = 1,
			CanTouch = false,
			CastShadow = false,
			CustomPhysicalProperties = phys,
			TopSurface = SMOOTH,
			BottomSurface = SMOOTH,
		}, model)
		blk:SetAttribute("BlockerIndex", i)
		blk:SetAttribute("RestCFrame", cf) -- pose at angle/offset 0 (harness checks the live pose against the spec)
		CollectionService:AddTag(blk, MOVER_PART_TAG)
		new("WeldConstraint", { Part0 = root, Part1 = blk }, blk)
		-- a pendulum's extra blockers (Round 8 H9 foot under the lantern) are invisible colliders
		if not (m.type == "swing" and i > 1) then
			local vp = vis("BlockerVisual", cf, size, style[1], style[2], model)
			vp.Anchored = false
			vp.Massless = true
			new("WeldConstraint", { Part0 = blk, Part1 = vp }, vp)
		end
	end
	self:moverFelt(m, model, root)
	self:moverExtras(m, model, root, pivotLocal, axisLocal)

	model:SetAttribute("MoverId", m.id)
	model:SetAttribute("Type", m.type)
	model:SetAttribute("Speed", m.speed)
	model:SetAttribute("Phase", m.phase or 0)
	model:SetAttribute("HasRange", m.range ~= nil)
	model:SetAttribute("RangeMin", m.range and m.range[1] or 0)
	model:SetAttribute("RangeMax", m.range and m.range[2] or 0)
	model:SetAttribute("Period", moverPeriod(m))
	model:SetAttribute("Dwell", MoverMath.encodeDwell(m.dwell))
	if m.keys then
		model:SetAttribute("Keys", MoverMath.encodeKeys(m.keys))
	end
	if m.type == "swing" then
		model:SetAttribute("Amplitude", m.amplitude_deg)
	end
	model:SetAttribute("PivotWorld", pivot)
	model:SetAttribute("AxisWorld", axis)
	model:SetAttribute("Visual", m.visual)
	CollectionService:AddTag(model, MOVER_TAG)
	return model
end

-- A mover's own felt (Sugarloaf H11: gate top, lift deck, quay lip; holes.json moving_parts[].felt, top-surface centre
-- at offset 0). Where the felt box is the same box as a blocker, that blocker IS the felt: it gets the GolfSurface tag
-- (the ball and the VR floor treat it as felt) and felt colour; thin decks (<= 0.2) also get felt physics (the ball
-- rides on them), while thick ones (the gate, the lip) keep wall physics for side hits. Otherwise a welded felt slab.
function Hole:moverFelt(m, model, root)
	for _, f in m.felt or {} do
		local pc = makePiece(f)
		local t = f.thickness or FELT_T
		local top = self.cf * pc.base * pc.tilt
		local cf = top * CFrame.new(0, -t / 2, 0)
		local size = Vector3.new(f.size[1], t, f.size[2])
		local part
		for _, b in model:GetChildren() do
			if b.Name == "Blocker" and (b.Position - cf.Position).Magnitude < 0.02 and (b.Size - size).Magnitude < 0.02 then
				part = b
				break
			end
		end
		if not part then
			part = new("Part", { Name = "Blocker", Anchored = false, Size = size, CFrame = cf, Transparency = 1, CanTouch = false, CastShadow = false, TopSurface = SMOOTH, BottomSurface = SMOOTH }, model)
			part:SetAttribute("RestCFrame", cf)
			CollectionService:AddTag(part, MOVER_PART_TAG)
			new("WeldConstraint", { Part0 = root, Part1 = part }, part)
		end
		part:SetAttribute("MoverFelt", f.id)
		part:SetAttribute("PieceId", f.id)
		part:SetAttribute("Zone", f.zone)
		part:SetAttribute("decel_scale", f.decel_scale)
		if t <= 0.2 then
			part:SetAttribute("FeltPhysics", true)
			part.CustomPhysicalProperties = FELT_PHYS
		end
		CollectionService:AddTag(part, SURFACE_TAG)
		-- visible felt top (a thin skin on the box top, riding with it)
		local skin = vis("MoverFeltTop", cf * CFrame.new(0, t / 2 - 0.005, 0), Vector3.new(size.X, 0.02, size.Z), P.felt, M.Fabric, model)
		skin.Anchored = false
		skin.Massless = true
		skin.CastShadow = false
		new("WeldConstraint", { Part0 = part, Part1 = skin }, skin)
		if COURSE then
			tintedTexture(skin, SUGARLOAF_FELT.flat, P.felt, "FeltNap")
		end
	end
end

-- decorative pieces that ride on a mover (welded, massless, no collision)
function Hole:moverExtras(m, model, root, pivotLocal, axisLocal)
	local function ride(name, relCF, size, color, material, shape)
		local p = vis(name, self.cf * CFrame.new(pivotLocal) * relCF, size, color, material, model, shape)
		p.Anchored = false
		p.Massless = true
		new("WeldConstraint", { Part0 = root, Part1 = p }, p)
		return p
	end
	if m.id == "spinner" then
		-- a puffball near the outer end of each arm (spec blockers; the arms are 2.3 long since spec v2)
		for _, b in m.blockers do
			local c = v3(b.center)
			local reach = math.abs(c.X) + b.size[1] / 2 - 0.4
			ride("Puffball", CFrame.new(math.sign(c.X) * reach, 0.85, 0), Vector3.one * 1.2, P.cream, M.SmoothPlastic, Enum.PartType.Ball)
		end
		ride("HubCap", CFrame.new(0, 2.3, 0) * CFrame.Angles(0, 0, math.rad(90)), Vector3.new(0.5, 2.4, 2.4), P.toadstool, M.SmoothPlastic, Enum.PartType.Cylinder)
	elseif m.id == "millwheel" then
		-- rims either side of the flume + spokes (wheel radius 3.6, axle along local Z)
		for _, zz in { -3.95, 3.95 } do
			for k = 0, 15 do
				local a = k * math.pi / 8
				ride("Rim", CFrame.Angles(0, 0, a) * CFrame.new(0, -3.4, zz), Vector3.new(1.42, 0.3, 0.25), P.bark, M.Wood)
			end
			for k = 0, 3 do
				ride("Spoke", CFrame.new(0, 0, zz) * CFrame.Angles(0, 0, k * math.pi / 4), Vector3.new(0.2, 6.8, 0.2), P.oak, M.Wood)
			end
		end
	elseif m.type == "swing" then
		-- pendulum: a chain from the hinge down to the blocker (the lantern body), glowing
		local b = m.blockers[1]
		local top = v3(b.center) + Vector3.new(0, b.size[2] / 2, 0)
		local len = top.Magnitude
		if len > 0.1 then
			-- cylinder axis is local X: turn it to point from the hinge to the lantern top
			ride("Chain", CFrame.lookAt(top / 2, top) * CFrame.Angles(0, math.rad(90), 0), Vector3.new(len, 0.12, 0.12), P.bark, M.Metal, Enum.PartType.Cylinder)
		end
		-- the root beam it hangs from (static, across the swing plane: spec anchor pendulum_beam, 16 long; hidden with
		-- the rest of the part visuals once the h9_lantern_pendulum mesh rides the mover, h9_pendulum_root_beam replaces it)
		local across = axisLocal:Cross(Vector3.yAxis)
		vis("HingeBeam", self.cf * CFrame.lookAt(pivotLocal, pivotLocal + across) * CFrame.new(0, 0.6, 0), Vector3.new(1.2, 1.2, 16), P.bark, M.Wood, model)
		local glow = ride("LanternGlow", CFrame.new(v3(b.center)), v3(b.size) * 0.7, P.amber, M.Neon)
		glow.Transparency = 0.2
		new("PointLight", { Color = P.amber, Range = 12, Brightness = 1.2, Shadows = false }, glow)
	elseif m.id == "lantern_bar" then
		for _, s in { -1, 1 } do
			local l = ride("Lantern", CFrame.new(s * 2.9, 0.1, 0), Vector3.new(0.6, 0.8, 0.6), P.paper, M.SmoothPlastic)
			new("PointLight", { Color = P.amber, Range = 6, Brightness = 0.8 }, l)
		end
	end
end

------------------------------------------------------------------------------------------------ slot guards
-- Sugarloaf H11 (stage w sweep): the mover collision cuts leave 0.15-stud slots beside the lock gate and the quay lip
-- (the mover clearance), and the 0.16-stud ball squeezed into them in the engine (a slow roll into the lock fell
-- through the gate slot = out of bounds +1; a ball against the lip from the quay wedged 2 studs down). A slot narrower
-- than the ball can't swallow it, so these invisible guards (no collision, no queries) tell BallController to keep a
-- ball over them at the felt's support height (hole-local boxes = the cut boxes; SupportY = the felt top beside them).
local SUGARLOAF_SLOT_GUARDS = {
	[11] = {
		{ id = "gate_slot", min = { -1.95, -1.45, -21.65 }, max = { 1.95, 1.35, -20.85 }, support = 0 },
		{ id = "lip_slot", min = { -1.95, 2.35, -25.7 }, max = { 1.95, 5.15, -25.2 }, support = 4 },
	},
}
function Hole:buildSlotGuards()
	local guards = COURSE and SUGARLOAF_SLOT_GUARDS[self.def.number]
	if not guards then
		return
	end
	local folder = self:folder("SlotGuards")
	for _, g in guards do
		local mn, mx = v3(g.min), v3(g.max)
		local p = vis("SlotGuard", self.cf * CFrame.new((mn + mx) / 2), mx - mn, Color3.new(1, 1, 0), M.SmoothPlastic, folder)
		p.Transparency = 1
		p.CastShadow = false
		p:SetAttribute("GuardId", g.id)
		p:SetAttribute("SupportY", self.cf:PointToWorldSpace(Vector3.new(0, g.support, 0)).Y)
	end
end

------------------------------------------------------------------------------------------------ hazards, teleports
function Hole:buildHazard(hz)
	local c = v3(hz.center)
	local cf = self.cf * CFrame.new(c) * CFrame.Angles(0, math.rad(hz.yaw or 0), 0)
	local sx, sz = hz.size[1], hz.size[2]
	local volume = vis("Hazard", cf * CFrame.new(0, -1, 0), Vector3.new(sx, 6, sz), Color3.new(1, 0, 0), M.SmoothPlastic, self.hazards)
	volume.Transparency = 1
	volume:SetAttribute("HazardId", hz.id)
	volume:SetAttribute("HazardType", hz.type)
	volume:SetAttribute("Penalty", hz.penalty or 1)
	if hz.reset == "respawn" and hz.respawn then
		-- a miss is placed at rest on this felt point (e.g. H5's bridge entry) instead of the stroke start
		volume:SetAttribute("RespawnWorld", self.cf:PointToWorldSpace(v3(hz.respawn)) + Vector3.new(0, Config.BallRadius + 0.03, 0))
		-- glowing mossy marker flush on the felt where the ball comes back (spec anchor bridge_respawn_stone)
		local rs = COURSE == nil and vis("RespawnStone", self.cf * CFrame.new(v3(hz.respawn) + Vector3.new(0, 0.006, 0)) * CFrame.Angles(0, 0, math.rad(90)),
			Vector3.new(0.01, 0.8, 0.8), P.firefly, M.Neon, self.hazards, Enum.PartType.Cylinder)
		if rs then
			-- (Sugarloaf: the pass 5 sandstone respawn marker mesh goes here instead; SugarloafBuilder)
			rs.Transparency = 0.35
			rs.CastShadow = false
		end
	end
	-- water surface (world y): Terrain water is buoyant, so the server calls a ball that reaches it a hazard
	volume:SetAttribute("SurfaceY", (cf * CFrame.new(0, 0, 0)).Y)
	local depth = c.Y - self.lawnTopLocal
	if hz.type == "water" and self.inWorld then
		-- the world's Terrain water fills the hazard (WorldBuilder.CarveHoles); nothing to draw here
	elseif hz.type == "water" then
		local w = vis("Water", cf * CFrame.new(0, -depth / 2, 0), Vector3.new(sx, depth, sz), P.water, M.Glass, self.hazards)
		w.Transparency = 0.4
		w.CastShadow = false
		-- stream bed
		vis("StreamBed", cf * CFrame.new(0, -depth + 0.05, 0), Vector3.new(sx, 0.1, sz), P.slate, M.Pebble, self.hazards)
	elseif depth <= 0.1 or COURSE then
		-- (Sugarloaf H7 Taffy Gap: the canyon itself is the pit; the hazard surface sits 30 below the felt)
	else
		-- a dark rabbit hole: the felt has a gap here; fill the gap's floor with a dark disc
		vis("PitFloor", cf * CFrame.new(0, -depth / 2 + 0.05, 0), Vector3.new(sx, depth, sz), Color3.fromRGB(28, 20, 14), M.Ground, self.hazards)
	end
end

local function ring(parent, cf, radius, thickness, color, segments)
	segments = segments or 16
	local segLen = 2 * math.pi * radius / segments * 1.08
	for k = 0, segments - 1 do
		local a = k * 2 * math.pi / segments
		local p = vis("Ring", cf * CFrame.Angles(0, a, 0) * CFrame.new(0, 0, -radius), Vector3.new(segLen, thickness, thickness), color, M.Neon, parent)
		p.CastShadow = false
	end
end

function Hole:buildTeleport(tp)
	local entry = v3(tp.entry.center)
	local exit = v3(tp.exit.center)
	local dir = Vector3.new(tp.exit.dir[1], 0, tp.exit.dir[2]).Unit
	local entryW = self.cf:PointToWorldSpace(entry)
	local exitW = self.cf:PointToWorldSpace(exit)
	local dirW = self.cf:VectorToWorldSpace(dir)
	local marker = vis("Teleport", CFrame.new(entryW), Vector3.new(0.2, 0.2, 0.2), P.firefly, M.Neon, self.teleports)
	marker.Transparency = 1
	marker:SetAttribute("TeleportId", tp.id)
	marker:SetAttribute("Radius", tp.entry.radius)
	marker:SetAttribute("ExitPos", exitW)
	marker:SetAttribute("ExitDir", dirW)
	marker:SetAttribute("SpeedFactor", tp.speed_factor or 1)
	marker:SetAttribute("MinSpeed", tp.min_speed or 2)
	marker:SetAttribute("MaxSpeed", tp.max_speed or 8)
	if tp.entry.half_size then
		-- rectangle trigger (hole-local axes): centre +- half_size; the marker's CFrame carries the hole yaw
		marker.CFrame = self.cf * CFrame.new(entry)
		marker:SetAttribute("HalfSize", Vector2.new(tp.entry.half_size[1], tp.entry.half_size[2]))
	end
	if tp.kind == "lift" then
		-- Sugarloaf H11: the lock chamber floor is the lift deck. The ball rides the deck (Movers/Mover_<platform>) up
		-- and is pushed out at the exit when the release starts (BallController.checkTeleports)
		marker:SetAttribute("Kind", "lift")
		local deck
		for _, mm in self.def.moving_parts or {} do
			if mm.type == "lift" then
				deck = mm
			end
		end
		if deck then
			marker:SetAttribute("LiftMover", "Mover_" .. deck.id)
			marker:SetAttribute("Release", deck.schedule.release[1])
			marker:SetAttribute("RideStart", deck.schedule.rise[1])
			marker:SetAttribute("Period", deck.period_s)
		end
		return
	end
	local secret = COURSE == nil and tp.entry.radius < 0.32
	local col = secret and P.amber or P.firefly
	marker:SetAttribute("FxColor", col) -- BallController's exit flash
	if secret then
		-- the knot-hole itself (H9 Lantern Knot): a dark hollow ringed by bark, flush with the felt, never colliding
		local knot = new("Model", { Name = "Knot" }, self.teleports)
		local hollow = vis("Hollow", CFrame.new(entryW + Vector3.new(0, 0.004, 0)) * CFrame.Angles(0, 0, math.rad(90)),
			Vector3.new(0.008, tp.entry.radius * 2 + 0.1, tp.entry.radius * 2 + 0.1), Color3.fromRGB(28, 18, 10), M.SmoothPlastic, knot, Enum.PartType.Cylinder)
		hollow.CastShadow = false
		ring(knot, CFrame.new(entryW + Vector3.new(0, 0.03, 0)), tp.entry.radius + 0.16, 0.12, P.bark, 14)
	end
	-- entry: glowing ring just above the felt, exactly the trigger radius. Stage lg13 (VisualSeparation): ring and
	-- glow disc are 0.2 thick, 0.08 clear of the felt, side by side with the disc 0.08 inside the ring's inner face
	-- (the old 0.04 ring over a 0.01 disc got thickened into each other and into the felt).
	local entryRing = new("Model", { Name = "EntryRing" }, self.teleports)
	local ringR, lift = tp.entry.radius + 0.03, 0.08 + 0.1
	ring(entryRing, CFrame.new(entryW + Vector3.new(0, lift, 0)), ringR, 0.2, col, 16)
	local glowR = math.max(ringR - 0.1 - 0.08, 0.1)
	local glow = vis("Glow", CFrame.new(entryW + Vector3.new(0, lift, 0)) * CFrame.Angles(0, 0, math.rad(90)),
		Vector3.new(0.2, glowR * 2, glowR * 2), col, M.Neon, entryRing, Enum.PartType.Cylinder)
	glow.Transparency = 0.45
	new("PointLight", { Color = col, Range = secret and 4 or 7, Brightness = secret and 0.8 or 1.5 }, glow)
	new("ParticleEmitter", {
		Color = ColorSequence.new(col),
		LightEmission = 1,
		Size = NumberSequence.new(0.12),
		Lifetime = NumberRange.new(1, 2),
		Rate = secret and 3 or 10,
		Speed = NumberRange.new(0.3, 0.8),
		SpreadAngle = Vector2.new(40, 40),
		Transparency = NumberSequence.new(0.2, 1),
	}, glow)
	-- exit: a ring of fireflies standing on the felt, facing the exit direction
	local exitRing = new("Model", { Name = "ExitRing" }, self.teleports)
	local exitCF = CFrame.lookAt(exitW + Vector3.new(0, 1.0, 0), exitW + Vector3.new(0, 1.0, 0) + dirW) * CFrame.Angles(math.rad(90), 0, 0)
	ring(exitRing, exitCF, 0.95, 0.08, col, 18)
	local exitGlow = vis("ExitGlow", CFrame.new(exitW + Vector3.new(0, 0.006, 0)) * CFrame.Angles(0, 0, math.rad(90)), Vector3.new(0.01, 0.6, 0.6), col, M.Neon, exitRing, Enum.PartType.Cylinder)
	exitGlow.Transparency = 0.5
	new("PointLight", { Color = col, Range = 6, Brightness = 1 }, exitGlow)
end

------------------------------------------------------------------------------------------------ decor
local function lantern(parent, cf, scale, bright)
	scale = scale or 1
	local shell = vis("LanternPaper", cf, Vector3.new(0.7, 0.9, 0.7) * scale, P.paper, M.SmoothPlastic, parent, Enum.PartType.Ball)
	shell.Transparency = 0.15
	local core = vis("LanternCore", cf, Vector3.new(0.35, 0.45, 0.35) * scale, P.amber, M.Neon, parent, Enum.PartType.Ball)
	new("PointLight", { Color = P.amber, Range = 8, Brightness = bright or 0.6 }, core)
	vis("LanternCap", cf * CFrame.new(0, 0.48 * scale, 0), Vector3.new(0.4, 0.08, 0.4) * scale, P.bark, M.Wood, parent)
end

local function lanternPost(parent, base, h)
	h = h or 3
	vis("Post", base * CFrame.new(0, h / 2, 0), Vector3.new(0.3, h, 0.3), P.oak, M.Wood, parent)
	vis("Arm", base * CFrame.new(0.35, h - 0.1, 0), Vector3.new(0.8, 0.12, 0.12), P.oak, M.Wood, parent)
	lantern(parent, base * CFrame.new(0.65, h - 0.7, 0), 0.9)
end

local function mushroom(parent, base, stemH, stemR, capR, capColor, glow)
	vis("Stem", base * CFrame.new(0, stemH / 2, 0) * CFrame.Angles(0, 0, math.rad(90)), Vector3.new(stemH, stemR * 2, stemR * 2), P.cream, M.SmoothPlastic, parent, Enum.PartType.Cylinder)
	local cap = vis("Cap", base * CFrame.new(0, stemH, 0), Vector3.new(capR * 2, capR * 1.1, capR * 2), capColor or P.toadstool, glow and M.Neon or M.SmoothPlastic, parent, Enum.PartType.Ball)
	if glow then
		cap.Transparency = 0.2
		new("PointLight", { Color = capColor, Range = 5, Brightness = 0.7 }, cap)
	else
		for k = 0, 4 do
			local a = k * 2 * math.pi / 5
			vis("Spot", base * CFrame.new(math.cos(a) * capR * 0.62, stemH + capR * 0.3, math.sin(a) * capR * 0.62), Vector3.one * capR * 0.32, P.cream, M.SmoothPlastic, parent, Enum.PartType.Ball)
		end
	end
	return cap
end

local function house(parent, base, w, h, capColor)
	local stemH = h * 0.55
	vis("Stem", base * CFrame.new(0, stemH / 2, 0) * CFrame.Angles(0, 0, math.rad(90)), Vector3.new(stemH, w * 0.6, w * 0.6), P.cream, M.SmoothPlastic, parent, Enum.PartType.Cylinder)
	vis("Cap", base * CFrame.new(0, stemH + h * 0.15, 0), Vector3.new(w, h * 0.55, w), capColor or P.toadstool, M.SmoothPlastic, parent, Enum.PartType.Ball)
	vis("Door", base * CFrame.new(0, 1.1, -w * 0.3), Vector3.new(1.1, 2.2, 0.2), P.bark, M.Wood, parent)
	local win = vis("Window", base * CFrame.new(0, stemH * 0.7, -w * 0.3), Vector3.new(0.1, 0.9, 0.9), P.amber, M.Neon, parent, Enum.PartType.Cylinder)
	win.CFrame = base * CFrame.new(w * 0.15, stemH * 0.72, -w * 0.29) * CFrame.Angles(0, math.rad(90), 0)
end

local function tree(parent, base, h, w, colors)
	vis("Trunk", base * CFrame.new(0, h * 0.3, 0) * CFrame.Angles(0, 0, math.rad(90)), Vector3.new(h * 0.6, w * 0.12, w * 0.12), P.bark, M.Wood, parent, Enum.PartType.Cylinder)
	local offs = { Vector3.new(0, 0.62, 0), Vector3.new(0.22, 0.5, 0.1), Vector3.new(-0.2, 0.52, -0.12), Vector3.new(0.05, 0.8, 0.05) }
	for i, o in offs do
		vis("Leaves", base * CFrame.new(o.X * w, o.Y * h, o.Z * w), Vector3.one * w * (i == 1 and 0.7 or 0.5), colors[(i - 1) % #colors + 1], M.Grass, parent, Enum.PartType.Ball)
	end
end

local function rock(parent, cf, size)
	vis("Rock", cf, size, P.slate, M.Slate, parent, Enum.PartType.Ball)
	vis("Moss", cf * CFrame.new(0, size.Y * 0.3, 0), Vector3.new(size.X * 0.8, size.Y * 0.4, size.Z * 0.8), P.moss, M.Grass, parent, Enum.PartType.Ball)
end

-- Placeholder primitives for each spec decoration anchor, in palette colours. Everything is no-collision,
-- no-query: the anchor's Mount attachment marks where a real mesh goes.
function Hole:placeholder(a, parent)
	local name = a.name
	local pos = v3(a.position)
	local size = a.approx_size and v3(a.approx_size) or Vector3.new(2, 2, 2)
	-- anchors are authored at felt height; ones beside the felt stand on the (lower) lawn instead
	local drop = 0
	if not self:heightAt(pos.X, pos.Z, true) and pos.Y < self.feltMaxLocal + 0.6 then
		drop = pos.Y - self.lawnTopLocal
		pos -= Vector3.new(0, drop, 0)
	end
	local lawn = self.lawnTopLocal
	local base = self.cf * CFrame.new(pos)
	if self.inWorld and (name == "hollow_tree" or name == "hollow_tree_base") then
		-- the world's giant hollow tree (WorldBuilder) stands here instead
		return
	end
	if name == "lantern_gate" then
		local postH = size.Y + 0.6 + (pos.Y - lawn)
		for _, s in { -1, 1 } do
			vis("Post", self.cf * CFrame.new(pos.X + s * 4.3, lawn + postH / 2, pos.Z), Vector3.new(0.6, postH, 0.6), P.ember, M.Wood, parent)
		end
		vis("Kasagi", base * CFrame.new(0, size.Y + 0.4, 0), Vector3.new(size.X + 1.2, 0.5, 0.9), P.bark, M.Wood, parent)
		vis("Nuki", base * CFrame.new(0, size.Y - 0.6, 0), Vector3.new(size.X, 0.35, 0.5), P.ember, M.Wood, parent)
		for _, s in { -1, 1 } do
			vis("Cord", base * CFrame.new(s * 1.8, size.Y - 1.3, 0), Vector3.new(0.05, 1.1, 0.05), P.bark, M.SmoothPlastic, parent)
			lantern(parent, base * CFrame.new(s * 1.8, size.Y - 2.2, 0), 1.4, 0.9)
		end
	elseif name == "maple_tree" then
		tree(parent, base, size.Y, size.X, { P.ember, P.pumpkin, P.ember, P.gold })
	elseif name == "mossy_boulder" or name == "stream_rocks" then
		rock(parent, base * CFrame.new(0, size.Y * 0.35, 0), size)
	elseif name == "welcome_sign" then
		-- the tee sign (Hole:sign) is the functional one; this is the carved course sign
		vis("Post", base * CFrame.new(0, 1.2, 0), Vector3.new(0.3, 2.4, 0.3), P.oak, M.Wood, parent)
		local board = vis("Board", base * CFrame.new(0, 2.5, 0) * CFrame.Angles(0, math.rad(-60), 0), Vector3.new(2.4, 1, 0.2), P.oak, M.WoodPlanks, parent)
		local gui = new("SurfaceGui", { Face = Enum.NormalId.Front, CanvasSize = Vector2.new(240, 100), LightInfluence = 0 }, board)
		new("TextLabel", { Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, Text = "Lantern Grove", TextScaled = true, Font = Enum.Font.FredokaOne, TextColor3 = P.paper }, gui)
		lantern(parent, base * CFrame.new(0, 3.4, 0), 0.8)
	elseif name == "giant_acorn" then
		vis("Nut", base * CFrame.new(0, 2.5, 0), Vector3.new(2.4, 2.8, 2.4), P.oak, M.SmoothPlastic, parent, Enum.PartType.Ball)
		vis("Cap", base * CFrame.new(0, 3.5, 0), Vector3.new(2.7, 1.3, 2.7), P.bark, M.Wood, parent, Enum.PartType.Ball)
		vis("Stalk", base * CFrame.new(0, 4.3, 0), Vector3.new(0.25, 0.6, 0.25), P.bark, M.Wood, parent)
	elseif name == "rabbit_hole_rim" then
		for k = 0, 7 do
			local ang = k * math.pi / 4
			vis("Root", base * CFrame.new(math.cos(ang) * 1.35, 0.06, math.sin(ang) * 1.35) * CFrame.Angles(0, -ang, 0), Vector3.new(0.3, 0.12, 0.9), P.bark, M.Wood, parent)
		end
	elseif name == "squirrel_hut" then
		vis("Post", base * CFrame.new(0, 1.5, 0), Vector3.new(0.4, 3, 0.4), P.oak, M.Wood, parent)
		vis("Hut", base * CFrame.new(0, 3.6, 0), Vector3.new(2, 1.6, 2), P.oak, M.WoodPlanks, parent)
		vis("Roof", base * CFrame.new(0, 4.6, 0), Vector3.new(2.6, 0.8, 2.6), P.toadstool, M.SmoothPlastic, parent, Enum.PartType.Ball)
	elseif name == "ledge_lanterns" or name == "green_lanterns" or name == "step_lanterns" then
		local xs = name == "step_lanterns" and { 3.2, 7.3 } or { pos.X, -pos.X }
		for _, x in xs do
			local gy = self:heightAt(x, pos.Z, true) or lawn
			lanternPost(parent, self.cf * CFrame.new(x, gy, pos.Z), size.Y + (a.position[2] - gy))
		end
	elseif name == "stem_house" then
		-- the tunnel (felt 5 long, 7 wide) runs through the stem: stem walls outside both rails, a lintel, the cap
		for _, z in { -17.0, -7.0 } do
			vis("StemWall", self.cf * CFrame.new(pos.X, 1.5, z), Vector3.new(6, 3, 1.5), P.cream, M.SmoothPlastic, parent)
		end
		vis("Lintel", self.cf * CFrame.new(pos.X, 3.4, pos.Z), Vector3.new(5.6, 0.8, 11.5), P.cream, M.SmoothPlastic, parent)
		vis("Cap", self.cf * CFrame.new(pos.X, 6.2, pos.Z), Vector3.new(10, 5, 10), P.toadstool, M.SmoothPlastic, parent, Enum.PartType.Ball)
		for k = 0, 5 do
			local ang = k * math.pi / 3
			vis("Spot", self.cf * CFrame.new(pos.X + math.cos(ang) * 3.3, 7.4, pos.Z + math.sin(ang) * 3.3), Vector3.one * 1.3, P.cream, M.SmoothPlastic, parent, Enum.PartType.Ball)
		end
		lantern(parent, self.cf * CFrame.new(pos.X - 3, 2.6, -6.2), 1)
	elseif name == "small_toadstools" or name == "glow_shrooms" or name == "glow_mushrooms" then
		local glow = name ~= "small_toadstools"
		for k, o in { Vector3.new(0, 0, 0), Vector3.new(0.9, 0, 0.7), Vector3.new(-0.8, 0, 0.6) } do
			local sc = k == 1 and 1 or 0.7
			mushroom(parent, base * CFrame.new(o), size.Y * 0.6 * sc, 0.2 * sc, 0.6 * sc, glow and P.firefly or P.toadstool, glow)
		end
	elseif name == "toadstool_stool_deco" then
		-- the bumper visual is the stool itself; add a cap on top
		vis("Cap", base * CFrame.new(0, self:heightAt(pos.X, pos.Z) + 1.6, 0) - Vector3.new(0, pos.Y, 0), Vector3.new(2.2, 0.9, 2.2), P.toadstool, M.SmoothPlastic, parent, Enum.PartType.Ball)
	elseif name == "house_2" or name == "mushroom_house_L" or name == "mushroom_house_R" then
		house(parent, base * CFrame.Angles(0, math.rad(pos.X > 0 and -90 or 90), 0), size.X, size.Y, name == "mushroom_house_R" and P.pumpkin or P.toadstool)
	elseif name == "lantern_string" or name == "heart_lanterns" then
		if name == "lantern_string" then
			vis("Cord", base, Vector3.new(size.X, 0.05, 0.05), P.bark, M.SmoothPlastic, parent)
			for k = 0, 5 do
				lantern(parent, base * CFrame.new(-size.X / 2 + 1 + k * (size.X - 2) / 5, -0.5, 0), 0.8)
			end
		else
			for i = 0, 3 do
				for j = 0, 2 do
					local p = base * CFrame.new(-size.X / 2 + 2 + i * (size.X - 4) / 3, (i + j) % 2 * 1.2, -size.Z / 2 + 2 + j * (size.Z - 4) / 2)
					lantern(parent, p, 1.2, 1)
				end
			end
		end
	elseif name == "puffball_carousel" then
		-- hub cap + arms ride on the mover (Movers/Mover_spinner); nothing static beyond the hub bumper
		vis("HubBase", base * CFrame.new(0, 0.05, 0) * CFrame.Angles(0, 0, math.rad(90)), Vector3.new(0.1, 2, 2), P.moss, M.Grass, parent, Enum.PartType.Cylinder)
	elseif name == "root_bridge" then
		for _, s in { -1, 1 } do
			vis("Root", self.cf * CFrame.new(s * 0.75, -0.45, pos.Z), Vector3.new(0.7, 0.7, size.Z), P.bark, M.Wood, parent)
		end
		for _, z in { -16, -21.5, -27 } do
			vis("Arch", self.cf * CFrame.new(0, -0.7, z), Vector3.new(2.6, 0.6, 0.8), P.bark, M.Wood, parent)
		end
	elseif name == "covered_bridge" then
		for _, x in { -13.5, -7.5 } do
			for _, z in { -15.2, -27.8 } do
				vis("Post", self.cf * CFrame.new(x, 1.6, z), Vector3.new(0.4, 5.2, 0.4), P.oak, M.Wood, parent)
			end
		end
		vis("Roof", self.cf * CFrame.new(pos.X, 4.5, pos.Z), Vector3.new(7.4, 0.5, 13.6), P.toadstool, M.WoodPlanks, parent)
		vis("Ridge", self.cf * CFrame.new(pos.X, 5.0, pos.Z), Vector3.new(4, 0.5, 13.6), P.bark, M.WoodPlanks, parent)
		for _, z in { -15.0, -28.0 } do
			lantern(parent, self.cf * CFrame.new(pos.X, 3.6, z), 1)
		end
	elseif name == "waterfall_bg" or name == "waterfall" or name == "cascade" then
		local steps = name == "cascade" and 3 or 2
		for k = 1, steps do
			local h = size.Y * k / steps
			rock(parent, base * CFrame.new((k - 1) * 0.4, h - size.Y / steps * 0.5, (k - 1) * -size.Z * 0.18), Vector3.new(size.X * (1.1 - k * 0.15), size.Y / steps, size.Z * 0.6))
		end
		local fall = vis("Fall", base * CFrame.new(0, size.Y * 0.45, size.Z * 0.3), Vector3.new(size.X * 0.4, size.Y * 0.9, 0.2), P.water, M.Glass, parent)
		fall.Transparency = 0.3
		vis("Foam", base * CFrame.new(0, 0.2, size.Z * 0.45), Vector3.new(size.X * 0.6, 0.4, 1.2), P.foam, M.SmoothPlastic, parent, Enum.PartType.Ball)
	elseif name == "water_mill" then
		-- south of the mill race (water x 4.5..9.5, z -1..-5); the axle runs from the wheel into the wall
		vis("MillHouse", self.cf * CFrame.new(8, (lawn + 8) / 2, 2.4), Vector3.new(7, 8 - lawn, 3.6), P.cream, M.WoodPlanks, parent)
		vis("Frame", self.cf * CFrame.new(8, (lawn + 8.2) / 2, 0.55), Vector3.new(7.2, 8.2 - lawn, 0.2), P.oak, M.Wood, parent)
		vis("Roof", self.cf * CFrame.new(8, 8.6, 2.4), Vector3.new(8, 1.2, 4.6), P.bark, M.Slate, parent)
		vis("Axle", self.cf * CFrame.new(7.5, 3.6, -4.2) * CFrame.Angles(0, math.rad(90), 0), Vector3.new(9.6, 0.45, 0.45), P.bark, M.Wood, parent, Enum.PartType.Cylinder)
	elseif name == "sacks" then
		for k, o in { Vector3.new(0, 0.5, 0), Vector3.new(0.9, 0.5, 0.3), Vector3.new(0.4, 1.3, 0.1) } do
			vis(k == 3 and "Crate" or "Sack", base * CFrame.new(o), Vector3.new(0.9, 0.9, 0.9), k == 3 and P.oak or P.cream, k == 3 and M.WoodPlanks or M.Fabric, parent)
		end
	elseif name == "ferns" then
		for k, o in { Vector3.new(0, 0.6, 0), Vector3.new(1, 0.5, 0.6), Vector3.new(-0.8, 0.5, 0.7) } do
			vis("Fern", base * CFrame.new(o), Vector3.new(1.6, 1.2, 1.6), k == 2 and P.ember or P.moss, M.Grass, parent, Enum.PartType.Ball)
		end
	elseif name == "root_knot_ring" then
		-- root arch behind the ring (the alcove's back rail is at x = 9.25)
		vis("RootL", self.cf * CFrame.new(9.9, (lawn + 3.2) / 2, -9.2), Vector3.new(0.8, 3.2 - lawn, 0.8), P.bark, M.Wood, parent)
		vis("RootR", self.cf * CFrame.new(9.9, (lawn + 3.2) / 2, -13.8), Vector3.new(0.8, 3.2 - lawn, 0.8), P.bark, M.Wood, parent)
		vis("RootTop", self.cf * CFrame.new(9.9, 3.3, -11.5), Vector3.new(0.9, 0.8, 5.4), P.bark, M.Wood, parent)
	elseif name == "hollow_tree_base" then
		vis("Trunk", base * CFrame.new(0, 13, 0) * CFrame.Angles(0, 0, math.rad(90)), Vector3.new(26, 14, 14), P.oak, M.Wood, parent, Enum.PartType.Cylinder)
		for k = 0, 4 do
			local ang = k * 2 * math.pi / 5
			vis("Root", base * CFrame.new(math.cos(ang) * 8.5, 1.2, math.sin(ang) * 8.5) * CFrame.Angles(0, -ang, math.rad(20)), Vector3.new(6, 2.2, 2.4), P.bark, M.Wood, parent)
		end
		for k, o in { Vector3.new(0, 30, 0), Vector3.new(6, 27, 3), Vector3.new(-5, 28, -4), Vector3.new(2, 33, -6) } do
			vis("Canopy", base * CFrame.new(o), Vector3.one * (k == 1 and 18 or 12), k % 2 == 0 and P.gold or P.pumpkin, M.Grass, parent, Enum.PartType.Ball)
		end
	elseif name == "hollow_tree" then
		-- a partial trunk shell around the chamber + heart, skipping anything near the felt (and the tunnel side)
		local cx, cz, r = 23, -36, 22
		for k = 0, 35 do
			local ang = k * math.pi / 18
			local px, pz = cx + math.cos(ang) * r, cz + math.sin(ang) * r
			local clear = true
			for dx = -2.5, 2.5, 1.25 do
				for dz = -2.5, 2.5, 1.25 do
					if self:heightAt(px + dx, pz + dz, true) then
						clear = false
					end
				end
			end
			if clear and px > 4 then
				-- tall behind the heart (north), root-height toward the tee and tunnel so you can see in
				local h = pz < cz - 4 and 30 or (pz < cz + 6 and 12 or 5)
				vis("Trunk", self.cf * CFrame.new(px, lawn + h / 2, pz) * CFrame.Angles(0, -ang, 0), Vector3.new(3, h, 4.2), P.oak, M.Wood, parent)
			end
		end
	elseif name == "trunk_tunnel" then
		for _, z in { -21.3, -29.7 } do
			vis("Buttress", self.cf * CFrame.new(pos.X, pos.Y + 1.8, z), Vector3.new(size.X, 3.6, 0.9), P.bark, M.Wood, parent)
		end
		vis("Arch", self.cf * CFrame.new(pos.X, pos.Y + 3.9, pos.Z), Vector3.new(size.X, 1.2, size.Z + 1), P.bark, M.Wood, parent)
	elseif name == "well_rim" then
		vis("RimLog", self.cf * CFrame.new(pos.X, pos.Y - 0.45, -40.25) * CFrame.Angles(0, 0, 0), Vector3.new(size.X, 0.5, 0.5), P.bark, M.Wood, parent)
	elseif name == "lantern_knot" or name == "exit_ring" or name == "mill_wheel" or name == "log_rail" then
		-- the functional visuals live in Teleports/ and Movers/; the anchor marks where the mesh goes
	else
		local p = vis("Block", base * CFrame.new(0, size.Y / 2, 0), size, P.slate, M.SmoothPlastic, parent)
		p.Transparency = 0.5
	end
end

------------------------------------------------------------------------------------------------ Sugarloaf decor
-- Part-built stand-ins for Sugarloaf's decoration anchors (props.md P1 landmarks, signs, felt arrows). Visual only.
-- Skipped: anchors whose look comes from elsewhere (the flag, the pass 5 mover meshes and their static frames, the
-- slot-canyon Terrain walls, the bumper/rock collision blocks that already render, teleport rings).
local SC_SKIP = {
	cup_flag = true, sluice_gate = true, gate_frame = true, windpump_wheel = true, ore_bucket = true, cableway_trestle = true,
	shadow_arm = true, hour_stones = true, gnomon_plinth = true, rope_bridges = true, gap_view = true, island_respawn_stone = true,
	island_edge_lip = true, lock_chamber = true, dam_view = true, slot_walls = true, echo_walls = true, geode_entry = true,
	geode_exit = true, intake_grate = true, striped_boulder = true, gumdrops = true, maze_rock = true, rock_face = true,
	hoodoo_deco = true, sugar_dune = true, tier_lip = true, dune_cliff = true, deck_overhang = true, bowl_rim = true,
	cliff_edge = true, dip_trim = true, basin_bank = true, sluice_flume = true, pipe_lip = true, left_open_cut = true,
	log_plank = true, ranger_footbridge = true, safe_east_wait = true, plank_respawn_stone = false,
}
local SIGN_TEXT = {
	sign_left = "Shortcut", sign_mid = "Mine-Cart Junction", sign_right = "Long way", sign_plank = "Log plank", sign_bridge = "Footbridge",
	sign_overflow = "Overflow", sign_bypass = "Round the back - no vanes", sign_pier = "Intake pier", sign_shore = "Shoreline",
	sign_west = "West", sign_centre = "Centre", sign_east = "East", safe_bank_sign = "Bank west - safe", sign_rim = "Rim route",
}

function Hole:sugarloafPlaceholder(a, parent)
	local name = a.name
	if name == "loading_dock" or name == "water_tank" or SC_SKIP[name] or string.find(name, "^hour_stone") or string.find(name, "^player_tp_") or string.find(name, "_skirt_")
		or string.find(name, "^crystal_%d") or string.find(name, "^hoodoo_%d") then
		return
	end
	local pos = v3(a.position)
	local size = a.approx_size and v3(a.approx_size) or Vector3.new(2, 2, 2)
	local base = self.cf * CFrame.new(pos)
	local lawn = math.min(pos.Y, self.lawnTopLocal + 1.5)
	local function box(n, cf, sz, col, mat)
		return vis(n, cf, sz, col, mat or M.SmoothPlastic, parent)
	end
	local function striped(n, cf, sz, cols)
		-- horizontal candy bands every 1 stud
		local bands = math.max(1, math.floor(sz.Y))
		for k = 0, bands - 1 do
			local h = sz.Y / bands
			box(n, cf * CFrame.new(0, -sz.Y / 2 + h * (k + 0.5), 0), Vector3.new(sz.X, h, sz.Z), cols[k % #cols + 1], M.Sandstone)
		end
	end
	local candy = { hex("E8736B"), hex("F6E3C8"), hex("D9534F"), hex("F2B48A") }
	if string.find(name, "arrow") or string.find(name, "chevron") then
		-- glowing lime arrow decal flat on the felt, pointing local -Z (or the anchor's facing)
		local dir = a.facing and Vector3.new(a.facing[1], 0, a.facing[2]) or Vector3.new(0, 0, -1)
		local f = self.cf * CFrame.lookAt(pos + Vector3.new(0, 0.006, 0), pos + Vector3.new(0, 0.006, 0) + dir)
		local L = math.max(size.Z, size.X) * 0.5
		for _, sgn in { -1, 1 } do
			local bar = box("Arrow", f * CFrame.new(sgn * L * 0.22, 0, -L * 0.05) * CFrame.Angles(0, sgn * math.rad(40), 0), Vector3.new(0.18, 0.01, L * 0.75), P.firefly, M.SmoothPlastic)
			bar.CastShadow = false
		end
		return
	end
	if string.find(name, "sign") then
		local face = self.cf:VectorToWorldSpace(Vector3.new(0, 0, 1))
		local post = CFrame.lookAt(base.Position, base.Position + face)
		box("SignPost", post * CFrame.new(0, size.Y / 2, 0), Vector3.new(0.2, size.Y, 0.2), P.oak, M.WoodPlanks)
		local board = box("SignBoard", post * CFrame.new(0, size.Y - 0.5, 0), Vector3.new(math.max(1.6, size.X), 0.8, 0.15), P.toadstool, M.SmoothPlastic)
		local gui = new("SurfaceGui", { Face = Enum.NormalId.Back, CanvasSize = Vector2.new(240, 100), LightInfluence = 0 }, board)
		new("TextLabel", { Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, Text = SIGN_TEXT[name] or name, TextScaled = true, Font = Enum.Font.FredokaOne, TextColor3 = P.cream }, gui)
		return
	end
	if name == "trailhead_arch" or name == "arch_gate" then
		-- candy-striped posts and a lintel; the opening stays >= 8 high (props.md: H18 underside >= 8 over the ramp)
		local w, h = size.X, math.max(size.Y, 9.4)
		for _, sx in { -1, 1 } do
			striped("Post", base * CFrame.new(sx * (w / 2 - 0.6), h / 2, 0), Vector3.new(1.2, h, size.Z), candy)
		end
		box("Lintel", base * CFrame.new(0, h - 0.6, 0), Vector3.new(w, 1.2, size.Z), P.oak, M.WoodPlanks)
		return
	end
	if name == "pump_house" then
		-- timber pump house around the 2.4-wide tunnel (pump_tunnel felt z -24..-18): its front face is at local z = -18
		-- (stage w: the house front stays at z <= -18 (-18.01, with the trimmed rail2/house13), 0.06 behind the windpump
		-- vanes at z -17.95..-17.25)
		local z0, z1, top = -24, -18.01, 8
		for _, xr in { { -8, -1.2 }, { 1.2, 8 } } do
			local cx, w = (xr[1] + xr[2]) / 2, xr[2] - xr[1]
			local hb = top - lawn
			box("PumpHouse", self.cf * CFrame.new(cx, lawn + hb / 2, (z0 + z1) / 2), Vector3.new(w, hb, z1 - z0), hex("FFF8F0"), M.WoodPlanks)
			box("Trim", self.cf * CFrame.new(cx, top - 0.3, z1 - 0.05), Vector3.new(w, 0.6, 0.1), P.toadstool, M.SmoothPlastic)
		end
		box("Roof", self.cf * CFrame.new(0, top + 0.3, (z0 + z1) / 2), Vector3.new(16.4, 0.6, z1 - z0 + 0.4), P.toadstool, M.SmoothPlastic)
		return
	end
	if name == "lollipop_cactus_1" or name == "island_hoodoo" or name == "big_gumdrop_bg" then
		if name == "lollipop_cactus_1" then
			box("Cactus", base * CFrame.new(0, size.Y * 0.35, 0), Vector3.new(1.2, size.Y * 0.7, 1.2), P.moss, M.Grass)
			box("Arm", base * CFrame.new(0.9, size.Y * 0.45, 0), Vector3.new(0.7, 2.4, 0.7), P.moss, M.Grass)
			local pop = vis("Lollipop", base * CFrame.new(0, size.Y * 0.8, 0) * CFrame.Angles(0, 0, math.rad(90)), Vector3.new(0.3, 2.6, 2.6), hex("F78FB3"), M.SmoothPlastic, parent, Enum.PartType.Cylinder)
			pop.Reflectance = 0.05
		elseif name == "island_hoodoo" then
			striped("Hoodoo", base * CFrame.new(0, size.Y / 2, 0), Vector3.new(size.X, size.Y, size.Z), { hex("CC8D91"), hex("E8C9A1") })
			vis("GumdropCap", base * CFrame.new(0, size.Y + 0.6, 0), Vector3.new(size.X + 1, 1.6, size.Z + 1), hex("F78FB3"), M.SmoothPlastic, parent, Enum.PartType.Ball)
		else
			vis("Gumdrop", base * CFrame.new(0, size.Y * 0.45, 0), size, hex("9BDB4D"), M.SmoothPlastic, parent, Enum.PartType.Ball)
		end
		return
	end
	if string.find(name, "lantern") or name == "crystal_cue" or name == "gate_light" then
		local core = vis("Glow", base * CFrame.new(0, size.Y / 2, 0), size, name == "gate_light" and hex("9BDB4D") or P.amber, M.Neon, parent)
		core.Transparency = 0.2
		new("PointLight", { Color = core.Color, Range = 8, Brightness = 0.5, Shadows = false }, core)
		return
	end
	if name == "sinkhole_rim" then
		for k = 0, 11 do
			local ang = k * math.pi / 6
			box("Rim", base * CFrame.new(math.cos(ang) * 1.55, 0.06, math.sin(ang) * 1.55) * CFrame.Angles(0, -ang, 0), Vector3.new(0.3, 0.12, 0.85), hex("E8C9A1"), M.Sandstone)
		end
		return
	end
	if name == "gnomon" then
		box("Gnomon", base * CFrame.new(0, size.Y / 2 + 1.2, 0), Vector3.new(size.X, size.Y, size.Z * 0.6), hex("3B3A3F"), M.Metal)
		return
	end
	if name == "plank_respawn_stone" then
		local d = vis("RespawnStone", base * CFrame.new(0, 0.006, 0) * CFrame.Angles(0, 0, math.rad(90)), Vector3.new(0.01, 0.8, 0.8), hex("E8C9A1"), M.Sandstone, parent, Enum.PartType.Cylinder)
		d.CastShadow = false
		return
	end
	-- buildings and big props: a body + a peppermint roof/band; rocks and piles: sandstone
	local rocky = string.find(name, "rock") or string.find(name, "pile") or string.find(name, "flood") or name == "geode_wall"
	local h = size.Y + (pos.Y - lawn)
	local body = box(rocky and "Rock" or "Body", self.cf * CFrame.new(pos.X, lawn + h / 2, pos.Z), Vector3.new(size.X, h, size.Z),
		rocky and hex("C68C59") or hex("FFF8F0"), rocky and M.Sandstone or M.WoodPlanks)
	if name == "geode_wall" then
		body.Color = hex("CC8D91")
		for k = 0, 5 do
			local g = box("Crystal", self.cf * CFrame.new(pos.X + size.X / 2, lawn + 2 + k * 2, pos.Z - size.Z / 2 + 2 + k * 2.6) * CFrame.Angles(0, 0, math.rad(25 + k * 9)), Vector3.new(0.8, 1.8, 0.8), P.candy, M.Glass)
			g.Transparency = 0.25
		end
	elseif not rocky and size.Y >= 2 then
		box("Roof", self.cf * CFrame.new(pos.X, lawn + h + 0.25, pos.Z), Vector3.new(size.X + 0.6, 0.5, size.Z + 0.6), P.toadstool, M.SmoothPlastic)
	end
end

function Hole:buildDecor()
	for _, a in self.def.decoration_anchors or {} do
		local m = new("Model", { Name = a.name }, self.decor)
		local pos = v3(a.position)
		local size = a.approx_size and v3(a.approx_size) or Vector3.new(1, 1, 1)
		local anchor = vis("Anchor", self.cf * CFrame.new(pos + Vector3.new(0, size.Y / 2, 0)), size, P.firefly, M.ForceField, m)
		anchor.Transparency = 1
		anchor.CastShadow = false
		new("Attachment", { Name = "Mount", Position = Vector3.new(0, -size.Y / 2, 0) }, anchor)
		anchor:SetAttribute("Notes", a.notes)
		anchor:SetAttribute("ApproxSize", size)
		anchor:SetAttribute("Landmark", a.landmark == true)
		m.PrimaryPart = anchor
		local ph = new("Model", { Name = "Placeholder" }, m)
		if COURSE then
			self:sugarloafPlaceholder(a, ph)
		else
			self:placeholder(a, ph)
		end
	end
end

------------------------------------------------------------------------------------------------ tee, sign, ground
function Hole:buildTee()
	local t = self.def.tee
	local pos = v3(t.position)
	local surf = self:heightAt(pos.X, pos.Z) or pos.Y
	local tw = self.cf:PointToWorldSpace(Vector3.new(pos.X, surf, pos.Z))
	local tee = vis("Tee", CFrame.new(tw + Vector3.new(0, 0.011, 0)), Vector3.new(2.2, 0.02, 2.2), Color3.fromRGB(250, 250, 250), M.SmoothPlastic, self.model)
	tee.Transparency = 0.55
	local hint = t.aim_hint or { 0, -1 }
	local aim = self.cf:PointToWorldSpace(Vector3.new(pos.X + hint[1] * 12, surf, pos.Z + hint[2] * 12))
	local at = vis("AimTarget", CFrame.new(aim), Vector3.new(0.2, 0.2, 0.2), Color3.new(1, 1, 1), M.SmoothPlastic, self.model)
	at.Transparency = 1
	-- hole sign beside the tee, on the lawn clear of any felt, facing the tee
	-- (stage gg2: spec tee.sign = {x, z} puts the sign there, e.g. the goose hole, whose tee sits in a 22-wide body)
	local spot = t.sign and Vector3.new(t.sign[1], self.lawnTopLocal, t.sign[2])
	for _, o in t.sign and {} or { { -5.4, -1 }, { 5.4, -1 }, { -5.4, 2.5 }, { 5.4, 2.5 }, { -2.5, 4.5 }, { 2.5, 4.5 }, { -9, 0 }, { 9, 0 }, { 0, 6 } } do
		local x, z = pos.X + o[1], pos.Z + o[2]
		local clear = true
		for dx = -1.2, 1.2, 0.6 do
			for dz = -1.2, 1.2, 0.6 do
				if self:heightAt(x + dx, z + dz, true) then
					clear = false
				end
			end
		end
		if clear then
			spot = Vector3.new(x, self.lawnTopLocal, z)
			break
		end
	end
	spot = spot or Vector3.new(pos.X - 6, self.lawnTopLocal, pos.Z)
	local sp = self.cf:PointToWorldSpace(spot)
	local toTee = Vector3.new(tw.X - sp.X, 0, tw.Z - sp.Z)
	local face = toTee.Magnitude > 0.1 and toTee.Unit or self.cf:VectorToWorldSpace(Vector3.new(0, 0, 1))
	local post = CFrame.lookAt(sp, sp + face)
	-- grouped under the manifest's tee-sign name (tee_sign_hNN; the part-built sign also shows name + par, so it
	-- stands in for the number-only mesh, which PropsBuilder skips)
	local signParent = new("Model", { Name = string.format("tee_sign_h%02d", self.def.number) }, self.model)
	vis("SignPost", post * CFrame.new(0, 2.3, 0), Vector3.new(0.35, 4.6, 0.35), P.oak, M.Wood, signParent)
	local board = vis("Sign", post * CFrame.new(0, 4.6, 0), Vector3.new(4.2, 2.4, 0.25), P.bark, M.WoodPlanks, signParent)
	local gui = new("SurfaceGui", { Face = Enum.NormalId.Front, CanvasSize = Vector2.new(420, 240), LightInfluence = 0 }, board)
	new("TextLabel", { Size = UDim2.new(1, 0, 0.42, 0), BackgroundTransparency = 1, Text = "HOLE " .. self.def.number, TextScaled = true, Font = Enum.Font.FredokaOne, TextColor3 = P.paper }, gui)
	new("TextLabel", { Size = UDim2.new(1, 0, 0.28, 0), Position = UDim2.fromScale(0, 0.42), BackgroundTransparency = 1, Text = self.def.name, TextScaled = true, Font = Enum.Font.FredokaOne, TextColor3 = Color3.new(1, 1, 1) }, gui)
	new("TextLabel", { Size = UDim2.new(1, 0, 0.26, 0), Position = UDim2.fromScale(0, 0.72), BackgroundTransparency = 1, Text = "PAR " .. self.def.par, TextScaled = true, Font = Enum.Font.FredokaOne, TextColor3 = P.firefly }, gui)
	lantern(signParent, post * CFrame.new(0, 6.3, 0), 1)
end

function Hole:buildGround()
	local m = 6
	local x0, x1, z0, z1 = self.bx0 - m, self.bx1 + m, self.bz0 - m, self.bz1 + m
	local topW = self.cf:PointToWorldSpace(Vector3.new(0, self.lawnTopLocal, 0)).Y
	local lawn = new("Part", {
		Name = "Lawn",
		Anchored = true,
		Size = Vector3.new(x1 - x0, topW, z1 - z0),
		CFrame = self.cf * CFrame.new((x0 + x1) / 2, self.lawnTopLocal - topW / 2, (z0 + z1) / 2),
		Color = P.lawn,
		Material = M.Grass,
		TopSurface = SMOOTH,
		BottomSurface = SMOOTH,
	}, self.ground)
	lawn.CanTouch = false
end

function Hole:finish()
	-- bounds: the felt's footprint + 3 studs, from well below the lowest felt to well above
	local a = Vector3.new(self.bx0 - 3, self.feltMinLocal - 8, self.bz0 - 3)
	local b = Vector3.new(self.bx1 + 3, self.feltMaxLocal + 30, self.bz1 + 3)
	local bounds = vis("Bounds", self.cf * CFrame.new((a + b) / 2), b - a, Color3.new(1, 1, 1), M.SmoothPlastic, self.model)
	bounds.Transparency = 1
	self.model:SetAttribute("KillY", self.cf:PointToWorldSpace(Vector3.new(0, self.feltMinLocal - 0.5, 0)).Y)
	self.model.PrimaryPart = self.model:FindFirstChild("Tee")
end

local function lcm(a, b)
	-- periods are multiples of 0.1 s in this spec
	local ia, ib = math.floor(a * 10 + 0.5), math.floor(b * 10 + 0.5)
	local function gcd(x, y)
		while y ~= 0 do
			x, y = y, x % y
		end
		return x
	end
	return ia // gcd(ia, ib) * ib / 10
end

local function holeFrame(def, layout)
	local place = layout and layout.enabled ~= false and layout.holes and layout.holes[def.number]
	if place then
		local o = place.origin
		return CFrame.new(o[1], o[2], o[3]) * CFrame.Angles(0, math.rad(place.yaw or 0), 0), place.yaw or 0, true
	end
	local off = def.world_offset or { 0, 0, 0 }
	return CFrame.new(off[1], off[2] + COURSE_Y, off[3]) * CFrame.Angles(0, math.rad(def.world_yaw or 0), 0), def.world_yaw or 0, false
end
CourseBuilder.holeFrame = holeFrame

local function buildHole(course, def, layout)
	local holeCF, yaw, inWorld = holeFrame(def, layout)
	local model = new("Model", { Name = "Hole" .. def.number })
	model:SetAttribute("HoleNumber", def.number)
	model:SetAttribute("CourseId", BUILD_COURSE_ID or COURSE or "lantern_grove")
	model:SetAttribute("Par", def.par)
	model:SetAttribute("HoleName", def.name)
	model:SetAttribute("Zone", def.zone)
	model:SetAttribute("Gimmick", def.gimmick)
	model:SetAttribute("SpecId", def.id)
	-- auto-reset a stuck ball (BallController.checkAutoReset): spec `auto_reset_still` (seconds, or false), else on
	-- for every hole with moving parts or teleports
	local autoReset = def.auto_reset_still
	if autoReset == nil and (#(def.moving_parts or {}) > 0 or #(def.teleports or {}) > 0) then
		autoReset = Config.AutoResetStill
	end
	if autoReset then
		model:SetAttribute("AutoResetStill", autoReset)
	end
	local self = setmetatable({
		def = def,
		model = model,
		cf = holeCF,
		inWorld = inWorld,
		pieces = {},
	}, Hole)
	model:SetAttribute("HoleOrigin", self.cf.Position)
	model:SetAttribute("HoleYaw", yaw)
	self.geo = self:folder("Geometry")
	self.rails = self:folder("Rails")
	self.movers = self:folder("Movers")
	self.hazards = self:folder("Hazards")
	self.teleports = self:folder("Teleports")
	self.decor = self:folder("Decor")
	self.ground = self:folder("Ground")

	local fmin, fmax = math.huge, -math.huge
	local bx0, bx1, bz0, bz1 = math.huge, -math.huge, math.huge, -math.huge
	local removed = {}
	for _, id in def.removed_static_felt or {} do
		removed[id] = true
	end
	for _, f in def.felt do
		if removed[f.id] then
			continue -- (Sugarloaf H11: the lock floor is the moving lift deck's own felt)
		end
		local pc = makePiece(f)
		table.insert(self.pieces, pc)
		fmin = math.min(fmin, pieceMinTop(pc))
		fmax = math.max(fmax, pc.c.Y + math.abs(pc.rise) / 2)
		for _, sx in { -1, 1 } do
			for _, sz in { -1, 1 } do
				local p = pc.base:PointToWorldSpace(Vector3.new(sx * pc.hx, 0, sz * pc.hz))
				bx0, bx1 = math.min(bx0, p.X), math.max(bx1, p.X)
				bz0, bz1 = math.min(bz0, p.Z), math.max(bz1, p.Z)
			end
		end
	end
	self.feltMinLocal, self.feltMaxLocal = fmin, fmax
	self.bx0, self.bx1, self.bz0, self.bz1 = bx0, bx1, bz0, bz1
	self.lawnTopLocal = fmin - LAWN_DROP
	model:SetAttribute("FeltMinY", self.cf:PointToWorldSpace(Vector3.new(0, fmin, 0)).Y)
	model:SetAttribute("FeltMaxY", self.cf:PointToWorldSpace(Vector3.new(0, fmax, 0)).Y)

	-- felt: the cup goes into the highest flat piece under it
	local cupLocal = v3(def.cup.position)
	local cupPiece
	for _, pc in self.pieces do
		if not pc.overlay and not pc.axis then
			local hh = pieceHeight(pc, cupLocal.X, cupLocal.Z, -0.6)
			if hh and math.abs(hh - cupLocal.Y) < 0.05 then
				cupPiece = pc
			end
		end
	end
	if not cupPiece then
		-- (Sugarloaf H16: the cup is 0.2 from the edge of its flat piece; cutNeighbourCup clears the rest of the hole)
		for _, pc in self.pieces do
			if not pc.overlay and not pc.axis then
				local hh = pieceHeight(pc, cupLocal.X, cupLocal.Z, 0)
				if hh and math.abs(hh - cupLocal.Y) < 0.05 then
					cupPiece = pc
				end
			end
		end
	end
	assert(cupPiece, "hole " .. def.number .. ": no flat felt piece under the cup")
	for _, pc in self.pieces do
		if pc == cupPiece then
			self:buildCupPiece(pc, cupLocal)
		else
			self:buildPiece(pc)
		end
		if not pc.overlay and not pc.bridge then
			self:buildBase(pc)
		end
	end
	self:cutNeighbourCup(cupLocal)
	for _, w in def.walls do
		self:buildWall(w)
	end
	local period = 0
	for _, m in def.moving_parts or {} do
		local mm = self:buildMover(m)
		local pd = mm:GetAttribute("Period")
		period = period == 0 and pd or lcm(period, pd)
	end
	model:SetAttribute("MoverPeriod", period)
	for _, hz in def.hazards or {} do
		self:buildHazard(hz)
	end
	for _, tp in def.teleports or {} do
		self:buildTeleport(tp)
	end
	self:buildSlotGuards()
	self:buildTee()
	if not BLOCKOUT then self:buildDecor() end
	if not inWorld then
		self:buildGround()
	end
	self:finish()
	model.Parent = course
	return model
end

------------------------------------------------------------------------------------------------ bonus hole (stage gg2)
-- A hidden bonus hole (Lantern Grove "Hole 19 - The Golden Goose": ServerStorage.CourseData.LanternGroveBonus, made by
-- tools/gg2_goose.py) built into an existing course folder beside its holes, which are not touched. The model gets
-- attribute Bonus = true, so Courses.holes() leaves it out of the round (scorecard, par total, #holes) and
-- Courses.bonusHole() finds it. GolfServer starts it when a ball on hole 9 reaches the egg (BuildH9Secret).
--   local CB = require(game.ServerStorage.CourseBuilder:Clone())
--   local data = require(game.ServerStorage.CourseData.LanternGroveBonus:Clone())
--   CB.BuildBonus(data); CB.BuildH9Secret(data); CB.ApplyVisualSeparation(workspace.Course)
local function decorPart(parent, cf, d)
	local p = vis(d.name, cf * CFrame.new(v3(d.center)) * CFrame.Angles(0, math.rad(d.yaw or 0), 0), v3(d.size),
		hex(d.color), M[d.material] or M.SmoothPlastic, parent, d.shape == "Ball" and Enum.PartType.Ball or nil)
	p.CastShadow = false
	p:SetAttribute("VisualQueryDisabled", true) -- (CameraOcclusion.tagDecor leaves it alone)
	return p
end

function CourseBuilder.BuildBonus(data, course)
	course = course or workspace:FindFirstChild("Course")
	local def = data.holes[1]
	local old = course:FindFirstChild("Hole" .. def.number)
	if old then
		old:Destroy()
	end
	local layout = { holes = { [def.number] = { origin = data.placement.origin, yaw = data.placement.yaw } } }
	BUILD_COURSE_ID = course:GetAttribute("CourseId")
	local model = buildHole(course, def, layout)
	model:SetAttribute("Bonus", true)
	model:SetAttribute("ZF1DenseFeltJoints", true) -- (VisualSeparation: stair-stepped felt joints, see there)
	local cf = holeFrame(def, layout)
	for _, d in def.decor_parts or {} do
		decorPart(model.Decor, cf, d)
	end
	local counts = CourseBuilder.ApplyPhysics(model)
	counts.parts = #model:GetDescendants()
	return game:GetService("HttpService"):JSONEncode(counts)
end

-- The secret way in (data.secret): golden goose footprints on hole 9's felt leading to a glowing golden egg in a
-- dead-end pocket. Additive and visual only, in Hole<N>/Secret: nothing collides, queries or touches, so no ball path
-- changes. The egg is a trigger the server watches (GolfServer): EggTrigger (Radius, ReturnWorld, BonusHole).
function CourseBuilder.BuildH9Secret(data, course)
	course = course or workspace:FindFirstChild("Course")
	local s = data.secret
	local h = course:FindFirstChild("Hole" .. s.hole)
	local old = h:FindFirstChild("Secret")
	if old then
		old:Destroy()
	end
	local hcf = CFrame.new(h:GetAttribute("HoleOrigin")) * CFrame.Angles(0, math.rad(h:GetAttribute("HoleYaw") or 0), 0)
	local m = new("Model", { Name = "Secret" }, h)
	local feltParams = RaycastParams.new()
	feltParams.FilterType = Enum.RaycastFilterType.Include
	feltParams.FilterDescendantsInstances = { h.Geometry }
	-- the felt top under a hole-local (x, z) (searching down from the spec height + 2)
	local function surface(x, y, z)
		local p = hcf:PointToWorldSpace(Vector3.new(x, y + 2, z))
		local hit = workspace:Raycast(p, Vector3.new(0, -6, 0), feltParams)
		assert(hit and CollectionService:HasTag(hit.Instance, SURFACE_TAG), string.format("no felt under secret spot %.2f, %.2f", x, z))
		return hit.Position, hit.Normal
	end
	local function frame(x, y, z, yaw)
		local pos, n = surface(x, y, z)
		local fwd = hcf:VectorToWorldSpace(Vector3.new(math.sin(math.rad(yaw)), 0, math.cos(math.rad(yaw))))
		local right = fwd:Cross(n).Unit
		return CFrame.fromMatrix(pos, right, n) -- (right-handed; -Z = look = fwd projected on the felt)
	end
	local function mark(p)
		p.CastShadow = false
		p:SetAttribute("VisualQueryDisabled", true)
		return p
	end
	-- footprints: a web 0.09 above the felt (part sunk 0.11 into it), three toes 0.085 above the web (no coplanar tops)
	local prints = new("Folder", { Name = "Footprints" }, m)
	local col = hex(s.print_color)
	for i, fp in s.prints do
		local f = frame(fp[1], fp[2], fp[3], fp[4]) -- fp[4]: walking direction (hole-local yaw, 180 = toward -Z)
		local foot = new("Model", { Name = "Print" .. i }, prints)
		mark(vis("Web", f * CFrame.new(0, 0.09 - 0.1, 0.12), Vector3.new(0.62, 0.2, 0.36), col, M.SmoothPlastic, foot))
		for k, a in { -32, 0, 32 } do
			local base = f * CFrame.new((k - 2) * 0.22, 0.175 - 0.1, -0.02)
			mark(vis("Toe", base * CFrame.Angles(0, math.rad(-a), 0) * CFrame.new(0, 0, -0.3), Vector3.new(0.2, 0.2, 0.62), col, M.SmoothPlastic, foot))
		end
	end
	for i, fe in s.feathers do
		local f = frame(fe[1], fe[2], fe[3], fe[4])
		local feather = new("Model", { Name = "Feather" .. i }, m)
		mark(vis("Vane", f * CFrame.new(0, 0.09 - 0.1, 0), Vector3.new(0.36, 0.2, 1.0), hex(s.feather_color), M.SmoothPlastic, feather))
		mark(vis("Quill", f * CFrame.new(0, 0.175 - 0.1, -0.15), Vector3.new(0.2, 0.2, 1.3), hex(s.print_color), M.SmoothPlastic, feather))
	end
	-- the golden egg in its pocket, a glowing ring at the trigger radius (the teleport entry-ring look) and the trigger
	local e = s.egg
	local trig = surface(e.trigger[1], e.trigger[2], e.trigger[3])
	local eggPos = surface(e.pos[1], e.pos[2], e.pos[3])
	local egg = mark(vis("GoldenEgg", CFrame.new(eggPos + Vector3.new(0, e.size[2] / 2 - 0.03, 0)), v3(e.size), hex(e.color), M.Neon, m))
	new("SpecialMesh", { MeshType = Enum.MeshType.Sphere }, egg)
	local entryRing = new("Model", { Name = "EggRing" }, m)
	local ringR, lift = e.radius + 0.03, 0.22
	ring(entryRing, CFrame.new(trig + Vector3.new(0, lift, 0)), ringR, 0.2, P.gold, 16)
	local glow = mark(vis("Glow", CFrame.new(trig + Vector3.new(0, lift, 0)) * CFrame.Angles(0, 0, math.rad(90)),
		Vector3.new(0.2, math.max(ringR - 0.18, 0.1) * 2, math.max(ringR - 0.18, 0.1) * 2), P.gold, M.Neon, entryRing, Enum.PartType.Cylinder))
	glow.Transparency = 0.55
	new("PointLight", { Color = P.gold, Range = 5, Brightness = 1 }, glow)
	new("ParticleEmitter", {
		Color = ColorSequence.new(P.gold),
		LightEmission = 1,
		Size = NumberSequence.new(0.1),
		Lifetime = NumberRange.new(1, 2),
		Rate = 3,
		Speed = NumberRange.new(0.3, 0.8),
		SpreadAngle = Vector2.new(40, 40),
		Transparency = NumberSequence.new(0.2, 1),
	}, glow)
	local marker = vis("EggTrigger", CFrame.new(trig), Vector3.new(0.2, 0.2, 0.2), P.gold, M.SmoothPlastic, m)
	marker.Transparency = 1
	marker:SetAttribute("Radius", e.radius)
	marker:SetAttribute("BonusHole", data.holes[1].number)
	local back = surface(s.return_pos[1], s.return_pos[2], s.return_pos[3])
	marker:SetAttribute("ReturnWorld", back + Vector3.new(0, Config.BallRadius + 0.03, 0))
	return #m:GetDescendants()
end

------------------------------------------------------------------------------------------------ physics groups
local function setGroupCollides(a, b, collides)
	if PhysicsService:IsCollisionGroupRegistered(a) and PhysicsService:IsCollisionGroupRegistered(b) then
		PhysicsService:CollisionGroupSetCollidable(a, b, collides)
	end
end

-- Tags the playable surfaces, puts obstacles/movers in their collision groups and applies the wall physics.
function CourseBuilder.ApplyPhysics(course, cfg)
	course = course or workspace:FindFirstChild("Course")
	cfg = cfg or Config
	local wall, bumper = wallPhys(cfg, cfg.WallElasticity), wallPhys(cfg, cfg.BumperElasticity)
	for _, g in { OBSTACLE_GROUP, MOVER_GROUP, "GolfBall", "GolfPlayer", "GolfClub" } do
		if not PhysicsService:IsCollisionGroupRegistered(g) then
			PhysicsService:RegisterCollisionGroup(g)
		end
	end
	setGroupCollides(OBSTACLE_GROUP, "GolfBall", true)
	setGroupCollides(OBSTACLE_GROUP, "GolfPlayer", false)
	setGroupCollides(OBSTACLE_GROUP, "GolfClub", false)
	setGroupCollides(OBSTACLE_GROUP, OBSTACLE_GROUP, true)
	for _, g in { "Default", OBSTACLE_GROUP, MOVER_GROUP, "GolfPlayer", "GolfClub" } do
		setGroupCollides(MOVER_GROUP, g, false)
	end
	setGroupCollides(MOVER_GROUP, "GolfBall", true)
	local counts = { surface = 0, obstacle = 0, mover = 0 }
	for _, d in course:GetDescendants() do
		if not d:IsA("BasePart") then
			continue
		end
		if SURFACE_NAMES[d.Name] then
			CollectionService:AddTag(d, SURFACE_TAG)
			counts.surface += 1
		elseif OBSTACLE_NAMES[d.Name] and d.CanCollide then
			d.CollisionGroup = OBSTACLE_GROUP
            local base = d.Name == "Bumper" and bumper or wall
            local friction = d:GetAttribute("WallFrictionOverride")
            if friction ~= nil then
                -- Per-wall test/data override; density and elasticity remain the existing wall values.
                local current = d.CurrentPhysicalProperties
                d.CustomPhysicalProperties = PhysicalProperties.new(current.Density, friction, current.Elasticity,
                    d:GetAttribute("WallFrictionWeightOverride") or current.FrictionWeight, current.ElasticityWeight)
            else
                d.CustomPhysicalProperties = base
            end
			counts.obstacle += 1
		elseif CollectionService:HasTag(d, MOVER_PART_TAG) then
			d.CollisionGroup = MOVER_GROUP
			-- (a mover's thin felt deck, e.g. Sugarloaf H11's lift, keeps felt physics: the ball rides on it)
			d.CustomPhysicalProperties = d:GetAttribute("FeltPhysics") and FELT_PHYS or wall
			counts.mover += 1
		elseif d.Name == "MoverRoot" or d.Name == "BlockerVisual" or (d.Parent and d.Parent:IsA("Model") and CollectionService:HasTag(d.Parent, MOVER_TAG)) then
			d.CollisionGroup = MOVER_GROUP
		end
	end
	return counts
end

------------------------------------------------------------------------------------------------ lighting (course.md, day)
function CourseBuilder.ApplyLighting()
	Lighting.ClockTime = 16.8
	Lighting.GeographicLatitude = 40
	Lighting.Ambient = hex("6B5A48")
	Lighting.OutdoorAmbient = hex("8C7A60")
	Lighting.Brightness = 2.2
	Lighting.ColorShift_Top = hex("FFD9A0")
	Lighting.EnvironmentDiffuseScale = 0.6
	Lighting.EnvironmentSpecularScale = 0.6
	local atm = Lighting:FindFirstChildOfClass("Atmosphere") or new("Atmosphere", {}, Lighting)
	atm.Density = 0.32
	atm.Color = hex("F3C98B")
	atm.Decay = hex("B5683A")
	atm.Glare = 0.3
	atm.Haze = 1.6
	local bloom = Lighting:FindFirstChildOfClass("BloomEffect") or new("BloomEffect", {}, Lighting)
	bloom.Intensity = 0.6
	bloom.Threshold = 1.4
	local rays = Lighting:FindFirstChildOfClass("SunRaysEffect") or new("SunRaysEffect", {}, Lighting)
	rays.Intensity = 0.08
	local dof = Lighting:FindFirstChildOfClass("DepthOfFieldEffect")
	if dof then
		dof.Enabled = false -- blurs the far holes in VR and in overview shots
	end
end

------------------------------------------------------------------------------------------------ build
-- data: the course spec module (default ServerStorage.CourseData.LanternGrove). Yields (CSG).
-- layout: WorldLayout table (default ServerStorage.CourseData.WorldLayout if present), or false for the flat layout.
-- opts (stage w, second course): { folder = "CourseSugarloaf", courseId = "sugarloaf_canyon", palette = "sugarloaf" }
--   builds into workspace[opts.folder] (only that folder is replaced; Lantern Grove's workspace.Course is untouched),
--   with Sugarloaf's palette, felt textures, exact-box rails and props, and leaves Lighting and the spawn alone:
--   require(game.ServerStorage.CourseBuilder:Clone()).Build(require(game.ServerStorage.CourseData.SugarloafCanyon:Clone()),
--     require(game.ServerStorage.CourseData.SugarloafLayout:Clone()), { folder = "CourseSugarloaf", courseId = "sugarloaf_canyon", palette = "sugarloaf" })
-- Reuse the build finalizer on an existing course without rebuilding its colliders.
-- Stage fx1: in-place match for places built before the cup felt fix. A CSG cup piece (CupPlate, CupCut felt) gets
-- the Texture/Decal children of the felt it was cut from (same hole Geometry, same PieceId, same tilt), so the cup area
-- reads as the same felt. A hidden collider keeps its copies hidden; its ZF1 visual copy shows them. Idempotent.
function CourseBuilder.MatchCupFelt(course)
	local report = {}
	for _, cup in course:GetDescendants() do
		if not (cup:IsA("PartOperation") and (cup.Name == "CupPlate" or cup:GetAttribute("CupCut"))) then
			continue
		end
		local ref, area
		for _, p in cup.Parent:GetChildren() do
			if p:IsA("Part") and p.Name == "Felt" and p:GetAttribute("PieceId") == cup:GetAttribute("PieceId")
				and p.CFrame.UpVector:Dot(cup.CFrame.UpVector) > 0.9999 and (not area or p.Size.X * p.Size.Z > area) then
				ref, area = p, p.Size.X * p.Size.Z
			end
		end
		if not ref then
			continue
		end
		local ref2 = cup:FindFirstChild("ZF1VisualReference")
		local visual = ref2 and ref2.Value
		for _, d in ref:GetChildren() do
			if (d:IsA("Texture") or d:IsA("Decal")) and not cup:FindFirstChild(d.Name) then
				local shown = d:GetAttribute("ZF1OriginalTransparency") or d.Transparency
				local c = d:Clone()
				c.Transparency = shown
				c:SetAttribute("ZF1OriginalTransparency", nil)
				if visual then
					c:Clone().Parent = visual
					c:SetAttribute("ZF1OriginalTransparency", shown)
					c.Transparency = 1
				end
				c.Parent = cup
				table.insert(report, { cup = cup:GetFullName(), from = ref:GetFullName(), child = d.Name })
			end
		end
	end
	return report
end

function CourseBuilder.ApplyVisualSeparation(course)
	if course.Name == "CourseAurora" then require(game.ServerStorage.AuroraVisualCleanup:Clone()).Apply(course) end
	local cupFelt = CourseBuilder.MatchCupFelt(course)
	local scenery = course == workspace:FindFirstChild("Course") and workspace:FindFirstChild("World") or nil
	local report = require(game.ServerStorage.VisualSeparation:Clone()).Apply(course, scenery)
	report.cupFelt = cupFelt
	return report
end

function CourseBuilder.Build(data, layout, opts)
	opts = opts or {}
	BLOCKOUT = opts.blockout == true
	BUILD_COURSE_ID = opts.courseId
	local folderName = opts.folder or "Course"
	local primary = folderName == "Course"
	local courseData = game:GetService("ServerStorage"):WaitForChild("CourseData")
	data = data or require(courseData:WaitForChild("LanternGrove"))
	if primary and layout == nil and courseData:FindFirstChild("WorldLayout") then
		layout = require(courseData.WorldLayout:Clone())
	end
	if layout and layout.enabled == false then
		layout = nil
	end
	if opts.palette == "sugarloaf" then
		for k, v in SUGARLOAF_P do
			P[k] = v
		end
		COURSE = opts.courseId or "sugarloaf_canyon"
	end
	local old = workspace:FindFirstChild(folderName)
	if old then
		old:Destroy()
	end
	local course = new("Folder", { Name = folderName })
	course:SetAttribute("CourseId", opts.courseId or "lantern_grove")
	course:SetAttribute("CourseName", data.course)
	course:SetAttribute("TotalPar", data.total_par)
	course:SetAttribute("SpecSha1", data.source and data.source.sha1 or "")
	course:SetAttribute("CourseY", layout and 0 or COURSE_Y)
	course:SetAttribute("WorldLayout", layout ~= nil)
	if layout and layout.bounds then
		local b = layout.bounds
		course:SetAttribute("WorldMin", Vector3.new(b.x[1], b.y_range[1], b.z[1]))
		course:SetAttribute("WorldMax", Vector3.new(b.x[2], b.y_range[2], b.z[2]))
	end
	course.Parent = workspace
	local stats = { holes = 0, world = layout ~= nil }
	for _, h in data.holes do
		buildHole(course, h, layout)
		stats.holes += 1
		task.wait()
	end
	if COURSE == "sugarloaf_canyon" then
		require(game.ServerStorage.SugarloafOverrides:Clone()).Apply(course)
	end
	local counts = CourseBuilder.ApplyPhysics(course)
	-- Stage zf2: preserve authored physics while separating course visuals.
	if course:GetAttribute("CourseId") == "aurora_archipelago" or course:GetAttribute("CourseId") == "lantern_grove" then
		stats.visualSeparation = CourseBuilder.ApplyVisualSeparation(course)
	end
	if not primary then
		stats.surface, stats.obstacle, stats.mover = counts.surface, counts.obstacle, counts.mover
		stats.parts = #course:GetDescendants()
		return game:GetService("HttpService"):JSONEncode(stats)
	end
	local wb = game:GetService("ServerStorage"):FindFirstChild("WorldBuilder")
	if layout and wb then
		require(wb:Clone()).ApplyLighting()
	else
		CourseBuilder.ApplyLighting()
	end
	workspace.Gravity = data.physics and data.physics.gravity_studs_s2 or 32.7
	-- spawn beside hole 1's tee (players are frozen; VR/touch controls move the view)
	local spawn = workspace:FindFirstChildOfClass("SpawnLocation")
	local h1 = course:FindFirstChild("Hole1")
	if spawn then
		-- players are frozen / moved by the controls; the pad itself shouldn't show up on the course
		spawn.Transparency = 1
		local decal = spawn:FindFirstChildOfClass("Decal")
		if decal then
			decal.Transparency = 1
		end
	end
	local lobbySpot = workspace:FindFirstChild("Lobby") and workspace.Lobby:FindFirstChild("LobbySpawn")
	if spawn and lobbySpot then
		-- (stage x) players spawn in the lobby and pick a course there (GolfServer parks the ball on this spot)
		spawn.CFrame = lobbySpot.CFrame * CFrame.new(0, -lobbySpot.Size.Y / 2 - spawn.Size.Y / 2, 0)
	elseif spawn and layout and layout.spawn then
		-- Welcome Plaza, facing hole 1 (the ball starts on its tee; VR warps you to it)
		local p, look = layout.spawn.pos, layout.spawn.look_at
		local pos = Vector3.new(p[1], p[2] + spawn.Size.Y / 2, p[3])
		spawn.CFrame = CFrame.lookAt(pos, Vector3.new(look[1], pos.Y, look[3]))
	elseif spawn and h1 then
		local tee = h1.Tee.Position
		local lawnTop = h1.Ground.Lawn.Position.Y + h1.Ground.Lawn.Size.Y / 2
		spawn.CFrame = CFrame.new(tee.X + 7, lawnTop + spawn.Size.Y / 2, tee.Z + 3)
	end
	stats.surface, stats.obstacle, stats.mover = counts.surface, counts.obstacle, counts.mover
	stats.parts = #course:GetDescendants()
	return game:GetService("HttpService"):JSONEncode(stats)
end

return CourseBuilder
