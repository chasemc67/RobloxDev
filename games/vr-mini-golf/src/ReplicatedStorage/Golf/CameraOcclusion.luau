-- CameraOcclusion: what the cameras do about geometry between them and their subject.
--   * Golf cameras (putting/orbit, test follow): pass through everything (stage m, Chase's feedback) and fade what
--     sits between the camera and the ball: passThrough() + fade(). Only Terrain still pushes the camera in, since
--     it can't be made see-through.
--   * Explore's walking camera: resolve() pulls it in front of decor the Roblox popper can't see (round 2).
-- Decor never collides and is built with CanQuery off, so ordinary casts can't see it. GolfServer puts the visible
-- decor in collision group GolfDecor with CanQuery on; that group only "collides" with GolfCamera, the group these
-- casts use, so balls, players, the club and every other raycast still ignore the decor.
local CollectionService = game:GetService("CollectionService")
local PhysicsService = game:GetService("PhysicsService")

local CameraOcclusion = {}

CameraOcclusion.CAMERA_GROUP = "GolfCamera"
CameraOcclusion.DECOR_GROUP = "GolfDecor"
-- groups the camera is blocked by (ball, players, club and the Explore walls never block it)
CameraOcclusion.BLOCKING_GROUPS = { "Default", "GolfWall", "GolfMover", "GolfDecor" }

local RADIUS = 0.25 -- clearance kept around the camera (near plane + a margin)
local MIN_DIST = 1.5 -- closer than this to the focus, lift the camera over the obstacle instead
local SEE_THROUGH = 0.6 -- parts at least this transparent (invisible walls, glows) don't block

-- Server: register the groups and their collision matrix (idempotent).
function CameraOcclusion.setupGroups()
	for _, g in { CameraOcclusion.CAMERA_GROUP, CameraOcclusion.DECOR_GROUP } do
		if not PhysicsService:IsCollisionGroupRegistered(g) then
			PhysicsService:RegisterCollisionGroup(g)
		end
	end
	local blocking = {}
	for _, g in CameraOcclusion.BLOCKING_GROUPS do
		blocking[g] = true
	end
	for _, g in PhysicsService:GetRegisteredCollisionGroups() do
		PhysicsService:CollisionGroupSetCollidable(CameraOcclusion.DECOR_GROUP, g.name, g.name == CameraOcclusion.CAMERA_GROUP)
		if g.name ~= CameraOcclusion.DECOR_GROUP then
			PhysicsService:CollisionGroupSetCollidable(CameraOcclusion.CAMERA_GROUP, g.name, blocking[g.name] == true)
		end
	end
end

local FAR_PREFIXES = { "mountain_", "far_hill", "cloud_card" }

-- Server: make the visible, non-colliding decor under `roots` visible to camera casts only. Returns the count.
function CameraOcclusion.tagDecor(roots)
	local n = 0
	for _, root in roots do
		for _, d in root:GetDescendants() do
			if not d:IsA("BasePart") or d.CanCollide or d.CanQuery or d.Transparency >= SEE_THROUGH then
				continue
			end
			if math.max(d.Size.X, d.Size.Y, d.Size.Z) < 1 then
				continue -- teleport ring beads, lantern bits, grass tufts: the camera can pass through those
			end
			local far = false
			for _, pre in FAR_PREFIXES do
				if string.sub(d.Name, 1, #pre) == pre then
					far = true
					break
				end
			end
			if far then
				continue
			end
			d.CollisionGroup = CameraOcclusion.DECOR_GROUP
			d.CanQuery = true
			n += 1
		end
	end
	return n
end

local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Exclude
params.CollisionGroup = CameraOcclusion.CAMERA_GROUP
params.IgnoreWater = true

local felt = nil
local function feltParts()
	if not felt then
		felt = CollectionService:GetTagged("GolfSurface")
	end
	return felt
end

-- The first thing a camera-sized sphere hits going from `from` to `to` (felt, balls, characters, the camera's own
-- parts and see-through parts excluded), or nil.
function CameraOcclusion.cast(from: Vector3, to: Vector3, ignore: { Instance }?)
	local filter = { workspace.CurrentCamera, workspace:FindFirstChild("Balls") }
	for _, p in feltParts() do
		table.insert(filter, p)
	end
	for _, i in ignore or {} do
		table.insert(filter, i)
	end
	for _ = 1, 8 do
		params.FilterDescendantsInstances = filter
		local hit = workspace:Spherecast(from, RADIUS, to - from, params)
		if not hit then
			return nil
		end
		if hit.Instance:IsA("BasePart") and not hit.Instance:IsA("Terrain") and hit.Instance.Transparency >= SEE_THROUGH then
			table.insert(filter, hit.Instance)
			continue
		end
		return hit
	end
	return nil
end

-- Camera position for a camera that wants to sit at `desired` looking at `focus`: `desired`, or pulled in front of
-- the first thing in between. When that leaves it closer than MIN_DIST (ball against a rail, under a beam), the camera
-- swings up toward a top-down view instead and takes the direction with the most free room.
function CameraOcclusion.resolve(focus: Vector3, desired: Vector3, ignore: { Instance }?): Vector3
	local offset = desired - focus
	local dist = offset.Magnitude
	if dist < 1e-3 then
		return desired
	end
	local hit = CameraOcclusion.cast(focus, desired, ignore)
	if not hit then
		return desired
	end
	local dir = offset.Unit
	local bestDir, bestFree = dir, hit.Distance
	if bestFree < MIN_DIST then
		for _, t in { 0.35, 0.65, 0.9 } do
			local d = dir:Lerp(Vector3.yAxis, t).Unit
			local h = CameraOcclusion.cast(focus, focus + d * dist, ignore)
			local free = h and h.Distance or dist
			if free > bestFree then
				bestDir, bestFree = d, free
			end
			if free >= MIN_DIST then
				break
			end
		end
	end
	return focus + bestDir * math.clamp(bestFree - 0.05, 0, dist)
end

-------------------------------------------------------------------------- golf cameras: pass-through + see-through
CameraOcclusion.FADE = 0.7 -- LocalTransparencyModifier for parts between the camera and the ball
local FADE_MODEL_MAX = 80 -- a hit on a decor model with at most this many parts fades the whole model...
local FADE_MODEL_EXTENT = 16 -- ...if it's no bigger than this (the hollow tree shell fades part by part)
local FADE_INSIDE_R = 1.5 -- parts within this of the camera (it sits in or right next to them) fade too
local INSIDE_MAX_SIZE = 12 -- that overlap is by bounding box, so huge meshes (the hollow tree shell, 40-128 studs, whose
-- boxes hold the whole H8/H9 play area) are left to the rays and the sphere sweep, which test real geometry
local THICK_R = 1.5 -- radius of the thick sight-line sweep: big decor just off the line (H6 tee sign) fades
local THICK_STOP = 2.5 -- the thick sweep stops this far short of the ball, so rails beside the ball stay
local GLOW_HIDE_R = 3 -- glow/neon parts this close to the camera hide and their lights go off (H9 pendulum)

local terrainParams = RaycastParams.new()
terrainParams.FilterType = Enum.RaycastFilterType.Include
terrainParams.IgnoreWater = true

local fadeRay = RaycastParams.new()
fadeRay.FilterType = Enum.RaycastFilterType.Exclude
fadeRay.CollisionGroup = CameraOcclusion.CAMERA_GROUP
fadeRay.IgnoreWater = true
local fadeOverlap = OverlapParams.new()
fadeOverlap.FilterType = Enum.RaycastFilterType.Exclude
fadeOverlap.CollisionGroup = CameraOcclusion.CAMERA_GROUP

-- Camera position for a golf camera that wants `desired` looking at `focus`: `desired` itself (walls, rails,
-- props and movers never push it), except that Terrain in between pulls it in (lifting it toward a top-down
-- view when that leaves it closer than MIN_DIST).
function CameraOcclusion.passThrough(focus: Vector3, desired: Vector3): Vector3
	local offset = desired - focus
	local dist = offset.Magnitude
	if dist < 1e-3 then
		return desired
	end
	terrainParams.FilterDescendantsInstances = { workspace.Terrain }
	local hit = workspace:Spherecast(focus, RADIUS, offset, terrainParams)
	if not hit then
		return desired
	end
	local dir = offset.Unit
	local bestDir, bestFree = dir, hit.Distance
	if bestFree < MIN_DIST then
		for _, t in { 0.35, 0.65, 0.9 } do
			local d = dir:Lerp(Vector3.yAxis, t).Unit
			local h = workspace:Spherecast(focus, RADIUS, d * dist, terrainParams)
			local free = h and h.Distance or dist
			if free > bestFree then
				bestDir, bestFree = d, free
			end
			if free >= MIN_DIST then
				break
			end
		end
	end
	return focus + bestDir * math.clamp(bestFree - 0.05, 0, dist)
end

local modelParts = setmetatable({}, { __mode = "k" }) -- [Model] = its parts, or false when too big to fade whole

local function fadeGroup(p: BasePart, into)
	into[p] = true
	local m = p:FindFirstAncestorWhichIsA("Model")
	if not m or m:GetAttribute("HoleNumber") or m.Parent == workspace then
		return
	end
	local parts = modelParts[m]
	if parts == nil then
		parts = {}
		local ext = m:GetExtentsSize()
		if math.max(ext.X, ext.Y, ext.Z) > FADE_MODEL_EXTENT then
			parts = false
		end
		for _, d in m:GetDescendants() do
			if parts and d:IsA("BasePart") then
				table.insert(parts, d)
				if #parts > FADE_MODEL_MAX then
					parts = false
					break
				end
			end
		end
		modelParts[m] = parts
	end
	for _, d in parts or {} do
		into[d] = true
	end
end

-- off-centre sight lines (degrees right, up) that also fade: the ball's surroundings, a rail or tunnel wall just
-- beside it (camprobe: the H9 trunk tunnel arch)
local CONE = { { 5, 0 }, { -5, 0 }, { 10, 0 }, { -10, 0 }, { 0, 4 }, { 0, -4 }, { 0, 8 }, { 0, -8 }, { 5, 4 }, { -5, 4 }, { 5, -4 }, { -5, -4 } }

-- The parts a golf camera at `camPos` sees in front of `focus`: everything on the sight line (centre plus four rays
-- 0.3 off it, so a rail edge at the frame centre goes too), on the CONE lines around it (felt excepted, so the green
-- in front of the ball stays), a THICK_R sphere swept along the line (big decor just off it) and whatever sits
-- within FADE_INSIDE_R of the camera. Rails, walls, felt banks, movers and the
-- camera-queryable decor (tagDecor) count; the ball, `ignore` and Terrain don't. Mostly see-through parts are skipped.
-- Returns a set { [BasePart] = true }.
function CameraOcclusion.occluders(camPos: Vector3, focus: Vector3, ignore: { Instance }?)
	local filter = { workspace.CurrentCamera, workspace.Terrain }
	local balls = workspace:FindFirstChild("Balls")
	if balls then
		table.insert(filter, balls)
	end
	for _, i in ignore or {} do
		table.insert(filter, i)
	end
	local found = {}
	local toFocus = focus - camPos
	local len = toFocus.Magnitude
	if len < 0.05 then
		return found
	end
	local look = CFrame.lookAt(camPos, focus)
	local fwd, right, up = look.LookVector, look.RightVector, look.UpVector
	local hits = {}
	-- stop just short of the focus (0.25 over the ball) so the felt under the ball doesn't count
	local reach = math.max(len - 0.1, 0.05)
	local function sweep(from: Vector3, dir: Vector3, skipFelt: boolean)
		local f = table.clone(filter)
		for _ = 1, 16 do
			fadeRay.FilterDescendantsInstances = f
			local hit = workspace:Raycast(from, dir, fadeRay)
			if not hit then
				break
			end
			local p = hit.Instance
			table.insert(f, p)
			if p:IsA("BasePart") and p.Transparency < 0.95 and not (skipFelt and CollectionService:HasTag(p, "GolfSurface")) then
				hits[p] = true
			end
		end
	end
	for _, off in { Vector3.zero, up * 0.3, -up * 0.3, right * 0.3, -right * 0.3 } do
		sweep(camPos + off, fwd * reach, false)
	end
	for _, a in CONE do
		sweep(camPos, (look * CFrame.Angles(math.rad(a[2]), math.rad(-a[1]), 0)).LookVector * reach, true)
	end
	-- thick sweep: a THICK_R sphere along the sight line (felt skipped), stopping THICK_STOP short of the ball
	if len - THICK_STOP > 0.1 then
		local f = table.clone(filter)
		for _, p in feltParts() do
			table.insert(f, p)
		end
		for _ = 1, 16 do
			fadeRay.FilterDescendantsInstances = f
			local hit = workspace:Spherecast(camPos, THICK_R, fwd * (len - THICK_STOP), fadeRay)
			if not hit then
				break
			end
			table.insert(f, hit.Instance)
			if hit.Instance:IsA("BasePart") and hit.Instance.Transparency < 0.95 then
				hits[hit.Instance] = true
			end
		end
	end
	fadeOverlap.FilterDescendantsInstances = filter
	for _, p in workspace:GetPartBoundsInRadius(camPos, FADE_INSIDE_R, fadeOverlap) do
		if p.Transparency < 0.95 and not CollectionService:HasTag(p, "GolfSurface")
			and math.max(p.Size.X, p.Size.Y, p.Size.Z) <= INSIDE_MAX_SIZE then
			hits[p] = true
		end
	end
	for p in hits do
		fadeGroup(p, found)
	end
	return found
end

local faded: { [BasePart]: boolean } = {}

-- Glow parts (Neon, or carrying a light) and their lights, cached on first use. Near the camera they hide and the
-- lights go off, so a lantern swinging past the lens doesn't wash the view (H9 pendulum, round 4). Most of them have
-- CanQuery off, so this is plain box-distance maths instead of a query.
local glow: { { part: BasePart, lights: { Light } } }? = nil
local function glowParts()
	if glow then
		return glow
	end
	local list = {}
	for _, root in { workspace:FindFirstChild("Course"), workspace:FindFirstChild("World"), workspace:FindFirstChild("CourseSugarloaf") } do
		for _, d in root and root:GetDescendants() or {} do
			if d:IsA("BasePart") then
				local lights = {}
				for _, c in d:GetChildren() do
					if c:IsA("Light") then
						table.insert(lights, c)
					end
				end
				-- (lights count on invisible carriers too: the pendulum's LanternGlow point)
				if (d.Material == Enum.Material.Neon and d.Transparency < 0.95) or #lights > 0 then
					table.insert(list, { part = d, lights = lights })
				end
			end
		end
	end
	glow = list
	return list
end

local function boxDistance(p: BasePart, at: Vector3): number
	local l = p.CFrame:PointToObjectSpace(at)
	local h = p.Size / 2
	local c = Vector3.new(math.clamp(l.X, -h.X, h.X), math.clamp(l.Y, -h.Y, h.Y), math.clamp(l.Z, -h.Z, h.Z))
	return (l - c).Magnitude
end

local hiddenGlow: { [BasePart]: { Light } } = {}

local function hideNearGlow(camPos: Vector3?)
	local near = {}
	if camPos then
		for _, g in glowParts() do
			local p = g.part
			if p.Parent and (p.Position - camPos).Magnitude < GLOW_HIDE_R + p.Size.Magnitude / 2
				and boxDistance(p, camPos) < GLOW_HIDE_R then
				near[p] = g.lights
			end
		end
	end
	for p, lights in hiddenGlow do
		if not near[p] then
			p.LocalTransparencyModifier = faded[p] and CameraOcclusion.FADE or 0
			for _, l in lights do
				l.Enabled = true
			end
			hiddenGlow[p] = nil
		end
	end
	for p, lights in near do
		if not hiddenGlow[p] then
			p.LocalTransparencyModifier = 1
			local off = {}
			for _, l in lights do
				if l.Enabled then
					l.Enabled = false
					table.insert(off, l)
				end
			end
			hiddenGlow[p] = off
		end
	end
end

-- Fade (client-side LocalTransparencyModifier) what's between the camera and the ball; restore what's clear again.
function CameraOcclusion.fade(camPos: Vector3, focus: Vector3, ignore: { Instance }?)
	local now = CameraOcclusion.occluders(camPos, focus, ignore)
	for p in faded do
		if not now[p] then
			if not hiddenGlow[p] then
				p.LocalTransparencyModifier = 0
			end
			faded[p] = nil
		end
	end
	for p in now do
		if not faded[p] then
			p.LocalTransparencyModifier = math.max(p.LocalTransparencyModifier, CameraOcclusion.FADE)
			faded[p] = true
		end
	end
	hideNearGlow(camPos)
end

-- Restore everything fade() changed (leaving the golf camera, e.g. into Explore).
function CameraOcclusion.clearFade()
	for p in faded do
		p.LocalTransparencyModifier = 0
	end
	table.clear(faded)
	hideNearGlow(nil)
end

return CameraOcclusion
