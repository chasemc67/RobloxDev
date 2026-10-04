-- CourseBuilder: procedurally builds the mini golf course into workspace.Course.
-- Run from the command bar:  require(game.ServerStorage.CourseBuilder).Build()
-- Re-apply tags, collision groups and wall physics (from Config) to the existing course without rebuilding it:
--   require(game.ServerStorage.CourseBuilder).ApplyPhysics()
-- (the command bar caches required modules; pass a fresh Config to pick up edits:
--   ApplyPhysics(nil, require(game.ReplicatedStorage.Golf.Config:Clone())) )
local CourseBuilder = {}

local GeometryService = game:GetService("GeometryService")
local CollectionService = game:GetService("CollectionService")
local PhysicsService = game:GetService("PhysicsService")
local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Golf"):WaitForChild("Config"))

-- life size at 1 stud = 0.3 m
local SURFACE_THICK = 1
local WALL_H = 0.5 -- 15 cm bumpers
local CUP_RADIUS = 0.21 -- 12.6 cm cup (regulation is 10.8 cm)
local CUP_DEPTH = 0.35 -- 10.5 cm deep
local CUP_PLATE = 1.6

local FELT_PHYS = PhysicalProperties.new(1, 0.35, 0, 1, 100)
-- walls: the high weights make these values win over the ball's own (Config.Wall*/BumperElasticity)
local function wallPhys(cfg, elasticity)
	return PhysicalProperties.new(1, cfg.WallFriction, elasticity, 100, 100)
end
local WALL_PHYS = wallPhys(Config, Config.WallElasticity)

-- Playable felt (the ball's plane). VR uses only these for the putter head and the player's floor.
local SURFACE_TAG = "GolfSurface"
local SURFACE_NAMES = { Felt = true, CupPlate = true, Ramp = true }
-- Walls, rails, bumpers and obstacles: collide with the ball, but players walk/stand through them.
local OBSTACLE_GROUP = "GolfWall"
local OBSTACLE_NAMES = { Wall = true, Bumper = true, House = true, Roof = true, Blade = true }

local WALL_COLOR = Color3.fromRGB(240, 236, 222)
local BASE_COLOR = Color3.fromRGB(150, 112, 78)
local BUMPER_COLOR = Color3.fromRGB(220, 60, 60)
local SMOOTH = Enum.SurfaceType.Smooth

local function new(className, props, parent)
	local inst = Instance.new(className)
	for k, v in props do
		inst[k] = v
	end
	inst.Parent = parent
	return inst
end

local Hole = {}
Hole.__index = Hole

local function newHole(course, number, def)
	local model = new("Model", { Name = "Hole" .. number }, course)
	model:SetAttribute("HoleNumber", number)
	model:SetAttribute("Par", def.par)
	model:SetAttribute("HoleName", def.name)
	local self = setmetatable({
		model = model,
		feltColor = def.felt,
		min = Vector3.new(math.huge, math.huge, math.huge),
		max = Vector3.new(-math.huge, -math.huge, -math.huge),
		minSurface = math.huge,
	}, Hole)
	self.geo = new("Folder", { Name = "Geometry" }, model)
	return self
end

function Hole:track(a, b)
	self.min = self.min:Min(a):Min(b)
	self.max = self.max:Max(a):Max(b)
end

function Hole:part(name, cf, size, color, material, phys, className)
	local p = new(className or "Part", {
		Name = name,
		Anchored = true,
		Size = size,
		CFrame = cf,
		Color = color,
		Material = material,
		CustomPhysicalProperties = phys,
		TopSurface = SMOOTH,
		BottomSurface = SMOOTH,
	}, self.geo)
	local half = size / 2
	self:track(cf.Position - Vector3.new(1, 0, 1) * half.Magnitude, cf.Position + Vector3.new(1, 0, 1) * half.Magnitude)
	return p
end

function Hole:box(name, a, b, color, material, phys)
	local p = self:part(name, CFrame.new((a + b) / 2), b - a, color, material, phys)
	self:track(a, b)
	return p
end

function Hole:felt(x0, x1, z0, z1, surfaceY)
	self.minSurface = math.min(self.minSurface, surfaceY)
	local y0 = surfaceY - SURFACE_THICK
	if y0 > 0.01 then
		self:box("Base", Vector3.new(x0, 0, z0), Vector3.new(x1, y0, z1), BASE_COLOR, Enum.Material.WoodPlanks, WALL_PHYS)
	end
	return self:box("Felt", Vector3.new(x0, y0, z0), Vector3.new(x1, surfaceY, z1), self.feltColor, Enum.Material.Fabric, FELT_PHYS)
end

-- Felt rectangle with a real cup cut into it (CSG plate around the cup, plain parts elsewhere).
function Hole:feltWithCup(x0, x1, z0, z1, surfaceY, cx, cz)
	self.minSurface = math.min(self.minSurface, surfaceY)
	local y0 = surfaceY - SURFACE_THICK
	if y0 > 0.01 then
		self:box("Base", Vector3.new(x0, 0, z0), Vector3.new(x1, y0, z1), BASE_COLOR, Enum.Material.WoodPlanks, WALL_PHYS)
	end
	local h = CUP_PLATE / 2
	local px0, px1, pz0, pz1 = cx - h, cx + h, cz - h, cz + h
	local function strip(a0, a1, b0, b1)
		if a1 - a0 > 0.01 and b1 - b0 > 0.01 then
			self:box("Felt", Vector3.new(a0, y0, b0), Vector3.new(a1, surfaceY, b1), self.feltColor, Enum.Material.Fabric, FELT_PHYS)
		end
	end
	strip(x0, px0, z0, z1)
	strip(px1, x1, z0, z1)
	strip(px0, px1, z0, pz0)
	strip(px0, px1, pz1, z1)

	local plateCF = CFrame.new(cx, surfaceY - SURFACE_THICK / 2, cz)
	local plate = new("Part", {
		Anchored = true,
		Size = Vector3.new(CUP_PLATE, SURFACE_THICK, CUP_PLATE),
		CFrame = plateCF,
		Color = self.feltColor,
		Material = Enum.Material.Fabric,
		CustomPhysicalProperties = FELT_PHYS,
	}, workspace)
	-- the cup is a blind hole CUP_DEPTH deep (the plate keeps its bottom)
	local cutterH = CUP_DEPTH + 0.2
	local cupMidCF = CFrame.new(cx, surfaceY - CUP_DEPTH + cutterH / 2, cz)
	local cutter = new("Part", {
		Anchored = true,
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(cutterH, CUP_RADIUS * 2, CUP_RADIUS * 2),
		CFrame = cupMidCF * CFrame.Angles(0, 0, math.rad(90)),
	}, workspace)
	local results = GeometryService:SubtractAsync(plate, { cutter }, {
		CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition,
		RenderFidelity = Enum.RenderFidelity.Precise,
		SplitApart = false,
	})
	local cup = results[1]
	cup.Name = "CupPlate"
	cup.Anchored = true
	cup.UsePartColor = true
	cup.Color = self.feltColor
	cup.Material = Enum.Material.Fabric
	cup.CustomPhysicalProperties = FELT_PHYS
	cup.Parent = self.geo
	plate:Destroy()
	cutter:Destroy()

	-- white cup liner (hollow, visual only) + bottom
	local linerH = CUP_DEPTH - 0.03
	local linerCF = CFrame.new(cx, surfaceY - 0.015 - linerH / 2, cz) * CFrame.Angles(0, 0, math.rad(90))
	local outer = new("Part", {
		Anchored = true,
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(linerH, CUP_RADIUS * 2 - 0.004, CUP_RADIUS * 2 - 0.004),
		CFrame = linerCF,
		Color = Color3.fromRGB(250, 250, 250),
		Material = Enum.Material.SmoothPlastic,
	}, workspace)
	local inner = new("Part", {
		Anchored = true,
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(linerH + 0.2, CUP_RADIUS * 2 - 0.03, CUP_RADIUS * 2 - 0.03),
		CFrame = linerCF,
	}, workspace)
	local liner = GeometryService:SubtractAsync(outer, { inner }, { CollisionFidelity = Enum.CollisionFidelity.Box, SplitApart = false })[1]
	liner.Name = "CupLiner"
	liner.Anchored = true
	liner.CanCollide = false
	liner.CanQuery = false
	liner.CanTouch = false
	liner.UsePartColor = true
	liner.Color = Color3.fromRGB(250, 250, 250)
	liner.Parent = self.geo
	outer:Destroy()
	inner:Destroy()
	new("Part", {
		Name = "CupBottom",
		Anchored = true,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(0.01, CUP_RADIUS * 2 - 0.01, CUP_RADIUS * 2 - 0.01),
		CFrame = CFrame.new(cx, surfaceY - CUP_DEPTH + 0.006, cz) * CFrame.Angles(0, 0, math.rad(90)),
		Color = Color3.fromRGB(45, 45, 45),
		Material = Enum.Material.SmoothPlastic,
	}, self.geo)

	local marker = new("Part", {
		Name = "Cup",
		Anchored = true,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Transparency = 1,
		Size = Vector3.new(0.2, 0.2, 0.2),
		CFrame = CFrame.new(cx, surfaceY, cz),
	}, self.model)
	marker:SetAttribute("Radius", CUP_RADIUS)

	-- flag (non-colliding)
	local poleH = 5
	local poleBase = surfaceY - CUP_DEPTH
	new("Part", {
		Name = "FlagPole",
		Anchored = true,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(poleH, 0.05, 0.05),
		CFrame = CFrame.new(cx, poleBase + poleH / 2, cz) * CFrame.Angles(0, 0, math.rad(90)),
		Color = Color3.fromRGB(245, 245, 245),
		Material = Enum.Material.SmoothPlastic,
	}, self.model)
	local flag = new("Part", {
		Name = "Flag",
		Anchored = true,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Size = Vector3.new(1.4, 0.9, 0.03),
		CFrame = CFrame.new(cx + 0.72, poleBase + poleH - 0.5, cz),
		Color = Color3.fromRGB(235, 50, 50),
		Material = Enum.Material.SmoothPlastic,
	}, self.model)
	for _, face in { Enum.NormalId.Front, Enum.NormalId.Back } do
		local gui = new("SurfaceGui", { Face = face, CanvasSize = Vector2.new(140, 90), LightInfluence = 0 }, flag)
		new("TextLabel", {
			Size = UDim2.fromScale(1, 1),
			BackgroundTransparency = 1,
			Text = tostring(self.model:GetAttribute("HoleNumber")),
			TextScaled = true,
			Font = Enum.Font.FredokaOne,
			TextColor3 = Color3.new(1, 1, 1),
		}, gui)
	end
	return cup
end

function Hole:wall(x0, z0, x1, z1, surfaceY, color)
	return self:box("Wall", Vector3.new(x0, surfaceY - SURFACE_THICK, z0), Vector3.new(x1, surfaceY + WALL_H, z1), color or WALL_COLOR, Enum.Material.Wood, WALL_PHYS)
end

-- Wall between two XZ points (any angle).
function Hole:wallLine(ax, az, bx, bz, surfaceY, thickness)
	local a = Vector3.new(ax, 0, az)
	local b = Vector3.new(bx, 0, bz)
	local len = (b - a).Magnitude
	local height = SURFACE_THICK + WALL_H
	local mid = (a + b) / 2 + Vector3.new(0, surfaceY - SURFACE_THICK + height / 2, 0)
	local cf = CFrame.lookAt(mid, mid + (b - a))
	local p = self:part("Wall", cf, Vector3.new(thickness or 0.8, height, len), WALL_COLOR, Enum.Material.Wood, WALL_PHYS)
	return p
end

function Hole:post(x, z, surfaceY, radius)
	local height = SURFACE_THICK + WALL_H + 0.25
	local p = self:part(
		"Bumper",
		CFrame.new(x, surfaceY - SURFACE_THICK + height / 2, z) * CFrame.Angles(0, 0, math.rad(90)),
		Vector3.new(height, radius * 2, radius * 2),
		BUMPER_COLOR,
		Enum.Material.SmoothPlastic,
		wallPhys(Config, Config.BumperElasticity),
		"Part"
	)
	p.Shape = Enum.PartType.Cylinder
	return p
end

function Hole:tee(x, z, surfaceY)
	local tee = new("Part", {
		Name = "Tee",
		Anchored = true,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Size = Vector3.new(2.2, 0.02, 2.2),
		CFrame = CFrame.new(x, surfaceY + 0.011, z),
		Color = Color3.fromRGB(250, 250, 250),
		Material = Enum.Material.SmoothPlastic,
		Transparency = 0.55,
	}, self.model)
	return tee
end

function Hole:aim(x, z, y)
	new("Part", {
		Name = "AimTarget",
		Anchored = true,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Transparency = 1,
		Size = Vector3.new(0.2, 0.2, 0.2),
		CFrame = CFrame.new(x, y, z),
	}, self.model)
end

function Hole:sign(x, z, faceDir)
	local post = CFrame.lookAt(Vector3.new(x, 0, z), Vector3.new(x, 0, z) + faceDir)
	new("Part", {
		Name = "SignPost",
		Anchored = true,
		Size = Vector3.new(0.4, 3, 0.4),
		CFrame = post * CFrame.new(0, 1.5, 0),
		Color = BASE_COLOR,
		Material = Enum.Material.Wood,
	}, self.model)
	local board = new("Part", {
		Name = "Sign",
		Anchored = true,
		Size = Vector3.new(4.5, 2.6, 0.25),
		CFrame = post * CFrame.new(0, 3.6, 0),
		Color = Color3.fromRGB(35, 70, 50),
		Material = Enum.Material.SmoothPlastic,
	}, self.model)
	local gui = new("SurfaceGui", { Face = Enum.NormalId.Front, CanvasSize = Vector2.new(450, 260), LightInfluence = 0 }, board)
	local holeNum = self.model:GetAttribute("HoleNumber")
	new("TextLabel", {
		Size = UDim2.new(1, 0, 0.42, 0),
		BackgroundTransparency = 1,
		Text = "HOLE " .. holeNum,
		TextScaled = true,
		Font = Enum.Font.FredokaOne,
		TextColor3 = Color3.fromRGB(255, 230, 120),
	}, gui)
	new("TextLabel", {
		Size = UDim2.new(1, 0, 0.28, 0),
		Position = UDim2.fromScale(0, 0.42),
		BackgroundTransparency = 1,
		Text = self.model:GetAttribute("HoleName"),
		TextScaled = true,
		Font = Enum.Font.FredokaOne,
		TextColor3 = Color3.new(1, 1, 1),
	}, gui)
	new("TextLabel", {
		Size = UDim2.new(1, 0, 0.26, 0),
		Position = UDim2.fromScale(0, 0.72),
		BackgroundTransparency = 1,
		Text = "PAR " .. self.model:GetAttribute("Par"),
		TextScaled = true,
		Font = Enum.Font.FredokaOne,
		TextColor3 = Color3.fromRGB(200, 240, 200),
	}, gui)
end

function Hole:finish()
	local a = Vector3.new(self.min.X - 1, -5, self.min.Z - 1)
	local b = Vector3.new(self.max.X + 1, self.max.Y + 25, self.max.Z + 1)
	new("Part", {
		Name = "Bounds",
		Anchored = true,
		CanCollide = false,
		CanQuery = false,
		CanTouch = false,
		Transparency = 1,
		Size = b - a,
		CFrame = CFrame.new((a + b) / 2),
	}, self.model)
	self.model:SetAttribute("KillY", self.minSurface - 0.5)
	self.model.PrimaryPart = self.model:FindFirstChild("Tee")
end

local function tree(parent, x, z, scale)
	scale = scale or 1
	local m = new("Model", { Name = "Tree" }, parent)
	new("Part", {
		Name = "Trunk",
		Anchored = true,
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(6 * scale, 1.2 * scale, 1.2 * scale),
		CFrame = CFrame.new(x, 3 * scale, z) * CFrame.Angles(0, 0, math.rad(90)),
		Color = Color3.fromRGB(110, 75, 45),
		Material = Enum.Material.Wood,
	}, m)
	for i, off in { Vector3.new(0, 7, 0), Vector3.new(1.6, 6, 0.6), Vector3.new(-1.4, 6.2, -0.8), Vector3.new(0.2, 8.6, 0.3) } do
		new("Part", {
			Name = "Leaves",
			Anchored = true,
			Shape = Enum.PartType.Ball,
			Size = Vector3.one * (i == 1 and 5.5 or 4) * scale,
			CFrame = CFrame.new(x, 0, z) + off * scale,
			Color = Color3.fromRGB(50 + i * 8, 125 + i * 6, 55),
			Material = Enum.Material.Grass,
		}, m)
	end
end

local function setGroupCollides(a, b, collides)
	if PhysicsService:IsCollisionGroupRegistered(a) and PhysicsService:IsCollisionGroupRegistered(b) then
		PhysicsService:CollisionGroupSetCollidable(a, b, collides)
	end
end

-- Tags the playable surfaces, puts obstacles in their own collision group and applies the wall physics.
function CourseBuilder.ApplyPhysics(course, cfg)
	course = course or workspace:FindFirstChild("Course")
	cfg = cfg or Config
	local wall, bumper = wallPhys(cfg, cfg.WallElasticity), wallPhys(cfg, cfg.BumperElasticity)
	for _, g in { OBSTACLE_GROUP, "GolfBall", "GolfPlayer", "GolfClub" } do
		if not PhysicsService:IsCollisionGroupRegistered(g) then
			PhysicsService:RegisterCollisionGroup(g)
		end
	end
	setGroupCollides(OBSTACLE_GROUP, "GolfBall", true)
	setGroupCollides(OBSTACLE_GROUP, "GolfPlayer", false)
	setGroupCollides(OBSTACLE_GROUP, "GolfClub", false)
	setGroupCollides(OBSTACLE_GROUP, OBSTACLE_GROUP, true)
	local counts = { surface = 0, obstacle = 0 }
	for _, d in course:GetDescendants() do
		if not d:IsA("BasePart") then
			continue
		end
		if SURFACE_NAMES[d.Name] then
			CollectionService:AddTag(d, SURFACE_TAG)
			counts.surface += 1
		elseif OBSTACLE_NAMES[d.Name] then
			d.CollisionGroup = OBSTACLE_GROUP
			d.CustomPhysicalProperties = d.Name == "Bumper" and bumper or wall
			counts.obstacle += 1
		end
	end
	return counts
end

local HOLES = {
	{ name = "Warm Up", par = 2, felt = Color3.fromRGB(46, 160, 72) },
	{ name = "Dogleg", par = 3, felt = Color3.fromRGB(40, 140, 150) },
	{ name = "The Hill", par = 3, felt = Color3.fromRGB(70, 155, 60) },
	{ name = "Windmill", par = 3, felt = Color3.fromRGB(150, 70, 140) },
}

function CourseBuilder.Build()
	local old = workspace:FindFirstChild("Course")
	if old then
		old:Destroy()
	end
	local course = new("Folder", { Name = "Course" }, workspace)
	local decor = new("Folder", { Name = "Decor" }, course)

	------------------------------------------------------------------ Hole 1: straight warm up
	do
		local h = newHole(course, 1, HOLES[1])
		local s = 1
		h:feltWithCup(-4, 4, -4, 32, s, 0, 27)
		h:wall(-5, -5, -4, 33, s)
		h:wall(4, -5, 5, 33, s)
		h:wall(-4, -5, 4, -4, s)
		h:wall(-4, 32, 4, 33, s)
		-- gentle chicane bumpers
		h:wallLine(-4, 12, -1.5, 14, s, 0.8)
		h:wallLine(4, 17, 1.5, 19, s, 0.8)
		h:tee(0, -1, s)
		h:aim(0, 27, s)
		h:sign(-7.5, 1, Vector3.new(1, 0, -0.4))
		h:finish()
	end

	------------------------------------------------------------------ Hole 2: dogleg right
	do
		local h = newHole(course, 2, HOLES[2])
		local s = 1
		h:felt(26, 34, -4, 24, s)
		h:feltWithCup(34, 58, 16, 24, s, 53, 20)
		h:wall(25, -5, 26, 25, s) -- left of leg A
		h:wall(34, -5, 35, 15, s) -- right of leg A
		h:wall(34, 15, 59, 16, s) -- bottom of leg B (inner corner)
		h:wall(26, -5, 34, -4, s) -- back
		h:wall(25, 24, 59, 25, s) -- top
		h:wall(58, 15, 59, 25, s) -- end of leg B
		h:wallLine(25.6, 15.6, 34.4, 24.4, s, 1) -- 45 degree bank across the whole corner
		h:post(44, 20, s, 0.6)
		h:post(48.5, 17.6, s, 0.6)
		h:post(48.5, 22.4, s, 0.6)
		h:tee(30, -1, s)
		h:aim(30, 20, s)
		h:sign(22.5, 1, Vector3.new(1, 0, -0.4))
		h:finish()
	end

	------------------------------------------------------------------ Hole 3: up the hill
	do
		local h = newHole(course, 3, HOLES[3])
		-- a short, gentle ramp (36 cm rise over 2.4 m, ~8.5 degrees) up to a raised green
		local low, high = 1, 2.2
		local rampZ, run = 6, 8
		local topZ = rampZ + run
		h:felt(71, 79, -4, rampZ, low)
		h:box("Base", Vector3.new(71, 0, rampZ), Vector3.new(79, low, topZ), BASE_COLOR, Enum.Material.WoodPlanks, WALL_PHYS)
		-- ramp (wedge rises toward +Z)
		local rise = high - low
		local ramp = h:part("Ramp", CFrame.new(75, low + rise / 2, rampZ + run / 2), Vector3.new(8, rise, run), h.feltColor, Enum.Material.Fabric, FELT_PHYS, "WedgePart")
		ramp:SetAttribute("Felt", true)
		h:feltWithCup(69, 81, topZ, topZ + 16, high, 77, topZ + 11)
		h:wall(70, -5, 71, rampZ, low)
		h:wall(79, -5, 80, rampZ, low)
		h:wall(71, -5, 79, -4, low)
		-- ramp side walls follow the slope
		local angle = math.atan2(rise, run)
		local slopeLen = math.sqrt(rise * rise + run * run)
		local rampCF = CFrame.new(75, low + rise / 2, rampZ + run / 2) * CFrame.Angles(-angle, 0, 0)
		for _, side in { -1, 1 } do
			h:part("Wall", rampCF * CFrame.new(side * 4.5, WALL_H - 1, 0), Vector3.new(1, 2, slopeLen + 0.8), WALL_COLOR, Enum.Material.Wood, WALL_PHYS)
		end
		local top = high + WALL_H
		h:box("Wall", Vector3.new(68, 0, topZ + 16), Vector3.new(82, top, topZ + 17), WALL_COLOR, Enum.Material.Wood, WALL_PHYS)
		h:box("Wall", Vector3.new(68, 0, topZ), Vector3.new(69, top, topZ + 16), WALL_COLOR, Enum.Material.Wood, WALL_PHYS)
		h:box("Wall", Vector3.new(81, 0, topZ), Vector3.new(82, top, topZ + 16), WALL_COLOR, Enum.Material.Wood, WALL_PHYS)
		h:box("Wall", Vector3.new(68, 0, topZ - 1), Vector3.new(71, top, topZ), WALL_COLOR, Enum.Material.Wood, WALL_PHYS)
		h:box("Wall", Vector3.new(79, 0, topZ - 1), Vector3.new(82, top, topZ), WALL_COLOR, Enum.Material.Wood, WALL_PHYS)
		h:post(73.5, topZ + 7, high, 0.6)
		h:tee(75, 0, low)
		h:aim(75, topZ, high)
		h:sign(67.5, 1, Vector3.new(1, 0, -0.4))
		h:finish()
	end

	------------------------------------------------------------------ Hole 4: windmill
	do
		local h = newHole(course, 4, HOLES[4])
		local s = 1
		h:feltWithCup(110, 120, -4, 44, s, 115, 38)
		h:wall(109, -5, 110, 45, s)
		h:wall(120, -5, 121, 45, s)
		h:wall(110, -5, 120, -4, s)
		h:wall(110, 44, 120, 45, s)
		-- funnel toward the tunnel
		h:wallLine(110, 14, 113.2, 18.6, s, 0.8)
		h:wallLine(120, 14, 116.8, 18.6, s, 0.8)
		-- windmill house with tunnel
		local houseColor = Color3.fromRGB(235, 225, 200)
		h:box("House", Vector3.new(110, s, 19), Vector3.new(113.75, 7, 23), houseColor, Enum.Material.WoodPlanks, WALL_PHYS)
		h:box("House", Vector3.new(116.25, s, 19), Vector3.new(120, 7, 23), houseColor, Enum.Material.WoodPlanks, WALL_PHYS)
		h:box("House", Vector3.new(113.75, s + 1.6, 19), Vector3.new(116.25, 7, 23), houseColor, Enum.Material.WoodPlanks, WALL_PHYS)
		local roofColor = Color3.fromRGB(170, 60, 50)
		h:part("Roof", CFrame.new(115, 8.5, 19.75), Vector3.new(11, 3, 2.5), roofColor, Enum.Material.Slate, WALL_PHYS, "WedgePart")
		h:part("Roof", CFrame.new(115, 8.5, 22.25) * CFrame.Angles(0, math.pi, 0), Vector3.new(11, 3, 2.5), roofColor, Enum.Material.Slate, WALL_PHYS, "WedgePart")
		-- spinning blades (animated on each client)
		local mill = new("Model", { Name = "Windmill" }, h.model)
		-- blade tips sweep 1 cm above the felt so they block the ball
		local hubCF = CFrame.new(115, s + 0.03 + 4.6, 18.6)
		local hub = new("Part", {
			Name = "Hub",
			Anchored = true,
			CanCollide = false,
			Shape = Enum.PartType.Cylinder,
			Size = Vector3.new(0.6, 1.2, 1.2),
			CFrame = hubCF * CFrame.Angles(0, math.rad(90), 0),
			Color = Color3.fromRGB(90, 60, 40),
			Material = Enum.Material.Wood,
		}, mill)
		mill.PrimaryPart = hub
		for i = 0, 3 do
			local rot = CFrame.Angles(0, 0, i * math.pi / 2 + math.pi / 4)
			new("Part", {
				Name = "Blade",
				Anchored = true,
				Size = Vector3.new(1.4, 4.2, 0.3),
				CFrame = hubCF * rot * CFrame.new(0, -2.5, 0.15),
				Color = Color3.fromRGB(250, 250, 245),
				Material = Enum.Material.WoodPlanks,
				CustomPhysicalProperties = WALL_PHYS,
				TopSurface = SMOOTH,
				BottomSurface = SMOOTH,
			}, mill)
		end
		mill:SetAttribute("PivotCFrame", hubCF)
		mill:SetAttribute("RPS", 0.25)
		CollectionService:AddTag(mill, "Spinner")
		h:tee(115, -1, s)
		h:aim(115, 19, s)
		h:sign(106.5, 1, Vector3.new(1, 0, -0.4))
		h:finish()
	end

	------------------------------------------------------------------ decor
	local trees = {
		{ -12, 8 }, { -14, 26, 1.2 }, { 14, 30 }, { 15, 4, 0.9 }, { 20, 36, 1.1 }, { 40, 34 }, { 64, 32, 1.2 },
		{ 64, 6 }, { 88, 8, 1.1 }, { 90, 30 }, { 100, 40, 1.3 }, { 102, 12 }, { 128, 10 }, { 130, 32, 1.2 },
		{ 45, 4, 0.9 }, { 52, -8 }, { 95, -10, 1.1 }, { -6, -16 }, { 128, 50 }, { 75, 48, 1.3 },
	}
	for _, t in trees do
		tree(decor, t[1], t[2], t[3])
	end

	CourseBuilder.ApplyPhysics(course)
	return course
end

return CourseBuilder
