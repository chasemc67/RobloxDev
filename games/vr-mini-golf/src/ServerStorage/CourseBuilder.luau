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

local GeometryService = game:GetService("GeometryService")
local CollectionService = game:GetService("CollectionService")
local PhysicsService = game:GetService("PhysicsService")
local Lighting = game:GetService("Lighting")
local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Golf"):WaitForChild("Config"))

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
		bridge = def.kind == "bridge",
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
	CollectionService:AddTag(p, SURFACE_TAG)
	return p
end

-- A plain felt slab (sloped pieces are boxes tilted about the axis perpendicular to `slope.axis`).
function Hole:buildPiece(pc)
	local color = self:feltColor(pc)
	local sx, sz = pc.def.size[1], pc.def.size[2]
	if pc.axis == "x" then
		sx = math.sqrt(sx * sx + pc.rise * pc.rise)
	elseif pc.axis == "z" then
		sz = math.sqrt(sz * sz + pc.rise * pc.rise)
	end
	-- sloped (non-overlay) slabs are thicker so they reach down to the flat base below their low end
	local t = FELT_T
	if pc.axis and not pc.overlay and not pc.bridge then
		t = FELT_T + math.abs(pc.rise)
	end
	local top = self.cf * pc.base * pc.tilt
	self:feltPart("Felt", top * CFrame.new(0, -t / 2, 0), Vector3.new(sx, t, sz), color, pc)
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
	CollectionService:AddTag(cup, SURFACE_TAG)
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

	-- flag on a pole standing in the cup
	local poleH = 5
	local poleBase = cupWorld.Y - CUP_DEPTH
	vis("FlagPole", CFrame.new(cupWorld.X, poleBase + poleH / 2, cupWorld.Z) * CFrame.Angles(0, 0, math.rad(90)),
		Vector3.new(poleH, 0.06, 0.06), Color3.fromRGB(245, 245, 245), M.SmoothPlastic, self.model, Enum.PartType.Cylinder)
	local flag = vis("Flag", CFrame.new(cupWorld.X + 0.72, poleBase + poleH - 0.5, cupWorld.Z), Vector3.new(1.4, 0.9, 0.03), P.amber, M.SmoothPlastic, self.model)
	for _, face in { Enum.NormalId.Front, Enum.NormalId.Back } do
		local gui = new("SurfaceGui", { Face = face, CanvasSize = Vector2.new(140, 90), LightInfluence = 0 }, flag)
		new("TextLabel", {
			Size = UDim2.fromScale(1, 1),
			BackgroundTransparency = 1,
			Text = tostring(self.def.number),
			TextScaled = true,
			Font = Enum.Font.FredokaOne,
			TextColor3 = P.bark,
		}, gui)
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
local RAIL_NOTCHES = {
	[6] = { rail5 = { axis = "x", from = 5, to = 10 } },
}
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
		return P.bark, M.Wood
	end
	return P.limestone, M.Limestone
end

function Hole:buildWall(w)
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
	local notch = RAIL_NOTCHES[self.def.number] and RAIL_NOTCHES[self.def.number][w.id]
	if notch then
		local function sAt(v)
			local probe = notch.axis == "x" and Vector3.new(v, c.Y, c.Z) or Vector3.new(c.X, c.Y, v)
			return cf:PointToObjectSpace(probe).Z
		end
		local n0, n1 = sAt(notch.from), sAt(notch.to)
		n0, n1 = math.min(n0, n1), math.max(n0, n1)
		pieces = {}
		if n0 > -len / 2 + 0.05 then
			table.insert(pieces, { -len / 2, n0 })
		end
		if n1 < len / 2 - 0.05 then
			table.insert(pieces, { n1, len / 2 })
		end
	end
	local capped = not string.find(w.id, "deflector") and not string.find(w.id, "board")
	for _, pc in pieces do
		local mid, l = (pc[1] + pc[2]) / 2, pc[2] - pc[1]
		local body = vis("Rail_" .. w.id, self.cf * tilt * CFrame.new(0, -capT - bodyH / 2, mid), Vector3.new(thick, bodyH, l), color, material, self.rails)
		body:SetAttribute("WallId", w.id)
		if capped then
			vis("RailCap_" .. w.id, self.cf * tilt * CFrame.new(0, -capT / 2, mid), Vector3.new(thick + 0.08, capT, l + 0.04), P.oak, M.Wood, self.rails)
		end
	end
end

------------------------------------------------------------------------------------------------ moving parts
local function moverValue(m, t)
	-- same as the designer's sim (tools/sim.py part_state): returns value (deg or studs) and rate (per s)
	local sp = m.speed
	if not m.range then
		return (m.phase or 0) + sp * t, sp
	end
	local a, b = m.range[1], m.range[2]
	local span = b - a
	if span <= 0 then
		return a, 0
	end
	local per = 2 * span
	local u = ((m.phase or 0) - a) + math.abs(sp) * t
	u = u - per * math.floor(u / per)
	if u < span then
		return a + u, math.abs(sp)
	end
	return b - (u - span), -math.abs(sp)
end
CourseBuilder.moverValue = moverValue

local function moverPeriod(m)
	if m.range then
		return 2 * (m.range[2] - m.range[1]) / math.abs(m.speed)
	end
	return 360 / math.abs(m.speed)
end

local function axisFrame(pos, axis)
	axis = axis.Unit
	local ref = math.abs(axis.Y) < 0.9 and Vector3.yAxis or Vector3.xAxis
	local y = (ref - axis * ref:Dot(axis)).Unit
	return CFrame.fromMatrix(pos, axis, y)
end

local MOVER_STYLE = {
	spinner = { P.cream, M.SmoothPlastic },
	millwheel = { P.oak, M.WoodPlanks },
	log = { P.bark, M.Wood },
	root_door = { P.bark, M.Wood },
	root_gate = { P.bark, M.Wood },
	lantern_bar = { P.oak, M.Wood },
}

-- Clearance gap: a sliding blocker must stop SLIDE_CLEARANCE short of any rail/bumper ahead of it (more than a ball
-- diameter), so a ball can never be squeezed between the two (the spec's H8 root door slid 0.6 studs into the alcove
-- rails and crushed balls parked against them). Walls the blocker already overlaps at offset 0 are ignored (e.g. the
-- H9 root gate's ends sit inside the corridor rails and slide vertically along them).
local SLIDE_CLEARANCE = 0.22
function Hole:clampSlideRange(m, blockers, axis)
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
			for _, p in pts(b.cf + axis * (off + sign * SLIDE_CLEARANCE), b.size) do
				local lp = wall.CFrame:PointToObjectSpace(p)
				local h = wall.Size / 2
				if math.abs(lp.X) < h.X and math.abs(lp.Y) < h.Y and math.abs(lp.Z) < h.Z then
					return true
				end
			end
		end
		return false
	end
	local lo, hi = m.range[1], m.range[2]
	local out = { lo, hi }
	for idx, sign in { [1] = -1, [2] = 1 } do
		local ahead = {}
		for _, w in walls do
			if not hits(0, sign, w) then
				table.insert(ahead, w)
			end
		end
		local target = sign > 0 and hi or lo
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

function Hole:buildMover(m)
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
	if m.type == "slide" and m.range then
		local bl = {}
		for _, b in m.blockers do
			local rollRot = b.roll and CFrame.fromAxisAngle(axisLocal, math.rad(b.roll)) or CFrame.new()
			table.insert(bl, { cf = self.cf * CFrame.new(pivotLocal) * rollRot * CFrame.new(v3(b.center)) * CFrame.Angles(0, math.rad(b.yaw or 0), 0), size = v3(b.size) })
		end
		local r = self:clampSlideRange(m, bl, axis)
		if math.abs(r[1] - m.range[1]) > 1e-3 or math.abs(r[2] - m.range[2]) > 1e-3 then
			model:SetAttribute("SpecRange", Vector2.new(m.range[1], m.range[2]))
			print(string.format("CourseBuilder: hole %d %s range [%g, %g] -> [%g, %g] (clearance %.2f to the rails)",
				self.def.number, m.id, m.range[1], m.range[2], r[1], r[2], SLIDE_CLEARANCE))
			m = table.clone(m)
			m.range = r
		end
	end
	local a0 = new("Attachment", { Name = "A0" }, base)
	local a1 = new("Attachment", { Name = "A1" }, root)
	local constraint
	if m.type == "rotate" then
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
		local vp = vis("BlockerVisual", cf, size, style[1], style[2], model)
		vp.Anchored = false
		vp.Massless = true
		new("WeldConstraint", { Part0 = blk, Part1 = vp }, vp)
	end
	self:moverExtras(m, model, root, pivotLocal, axisLocal)

	model:SetAttribute("MoverId", m.id)
	model:SetAttribute("Type", m.type)
	model:SetAttribute("Speed", m.speed)
	model:SetAttribute("Phase", m.phase or 0)
	model:SetAttribute("HasRange", m.range ~= nil)
	model:SetAttribute("RangeMin", m.range and m.range[1] or 0)
	model:SetAttribute("RangeMax", m.range and m.range[2] or 0)
	model:SetAttribute("Period", moverPeriod(m))
	model:SetAttribute("PivotWorld", pivot)
	model:SetAttribute("AxisWorld", axis)
	model:SetAttribute("Visual", m.visual)
	CollectionService:AddTag(model, MOVER_TAG)
	return model
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
		for _, s in { -1, 1 } do
			ride("Puffball", CFrame.new(s * 4.1, 0.85, 0), Vector3.one * 1.2, P.cream, M.SmoothPlastic, Enum.PartType.Ball)
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
	elseif m.id == "lantern_bar" then
		for _, s in { -1, 1 } do
			local l = ride("Lantern", CFrame.new(s * 2.9, 0.1, 0), Vector3.new(0.6, 0.8, 0.6), P.paper, M.SmoothPlastic)
			new("PointLight", { Color = P.amber, Range = 6, Brightness = 0.8 }, l)
		end
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
	local secret = tp.entry.radius < 0.32
	local col = secret and P.amber or P.firefly
	-- entry: glowing ring flat on the felt, exactly the trigger radius
	local entryRing = new("Model", { Name = "EntryRing" }, self.teleports)
	ring(entryRing, CFrame.new(entryW + Vector3.new(0, 0.012, 0)), tp.entry.radius + 0.03, 0.04, col, 16)
	local glow = vis("Glow", CFrame.new(entryW + Vector3.new(0, 0.006, 0)) * CFrame.Angles(0, 0, math.rad(90)),
		Vector3.new(0.01, tp.entry.radius * 2, tp.entry.radius * 2), col, M.Neon, entryRing, Enum.PartType.Cylinder)
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
		self:placeholder(a, ph)
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
	local spot
	for _, o in { { -5.4, -1 }, { 5.4, -1 }, { -5.4, 2.5 }, { 5.4, 2.5 }, { -2.5, 4.5 }, { 2.5, 4.5 }, { -9, 0 }, { 9, 0 }, { 0, 6 } } do
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
	local signParent = self.model
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
	model:SetAttribute("Par", def.par)
	model:SetAttribute("HoleName", def.name)
	model:SetAttribute("Zone", def.zone)
	model:SetAttribute("Gimmick", def.gimmick)
	model:SetAttribute("SpecId", def.id)
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
	for _, f in def.felt do
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
	self:buildTee()
	self:buildDecor()
	if not inWorld then
		self:buildGround()
	end
	self:finish()
	model.Parent = course
	return model
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
			d.CustomPhysicalProperties = d.Name == "Bumper" and bumper or wall
			counts.obstacle += 1
		elseif CollectionService:HasTag(d, MOVER_PART_TAG) then
			d.CollisionGroup = MOVER_GROUP
			d.CustomPhysicalProperties = wall
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
function CourseBuilder.Build(data, layout)
	local courseData = game:GetService("ServerStorage"):WaitForChild("CourseData")
	data = data or require(courseData:WaitForChild("LanternGrove"))
	if layout == nil and courseData:FindFirstChild("WorldLayout") then
		layout = require(courseData.WorldLayout:Clone())
	end
	if layout and layout.enabled == false then
		layout = nil
	end
	local old = workspace:FindFirstChild("Course")
	if old then
		old:Destroy()
	end
	local course = new("Folder", { Name = "Course" })
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
	local counts = CourseBuilder.ApplyPhysics(course)
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
	if spawn and layout and layout.spawn then
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
