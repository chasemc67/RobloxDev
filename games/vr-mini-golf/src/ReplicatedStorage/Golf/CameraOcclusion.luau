-- CameraOcclusion: keeps a follow camera in front of whatever sits between it and the ball (round 2, H8 beams).
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

return CameraOcclusion
