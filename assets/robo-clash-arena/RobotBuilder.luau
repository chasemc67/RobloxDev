-- Robo Clash Arena: procedural robot rigs built from Parts.
-- Run in Studio edit mode (require this ModuleScript and call Build(id) / BuildAll(folder)).
-- Rig: HumanoidRootPart -RootJoint-> Torso -Neck-> Head, -RShoulder/LShoulder-> arms,
-- -RHip/LHip-> legs. Detail parts are WeldConstraint'ed to their limb. Only the root collides.
-- Forward is -Z. Attachments: GunTip (RArm), BombTip (LArm), PodTip (Torso).

local Builder = {}

local function mk(parent, name, size, cf, color, material, shape)
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.CFrame = cf
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	if shape then
		p.Shape = shape
	end
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Massless = true
	p.CastShadow = true
	p.Parent = parent
	return p
end

local FWD = CFrame.Angles(0, math.rad(90), 0) -- cylinder axis (X) -> pointing forward (-Z)
local UP = CFrame.Angles(0, 0, math.rad(90)) -- cylinder axis (X) -> vertical

local BALL = Enum.PartType.Ball
local CYL = Enum.PartType.Cylinder
local WEDGE = Enum.PartType.Wedge
local NEON = Enum.Material.Neon
local METAL = Enum.Material.Metal

local function specs(c)
	local P, S, N, D = c.Primary, c.Secondary, c.Neon, Color3.fromRGB(45, 48, 58)
	return {
		Bolt = {
			Root = Vector3.new(3, 3, 2.5),
			HipHeight = 2.6,
			Limbs = {
				{ "Torso", "HumanoidRootPart", "RootJoint", CFrame.new(0, 0.7, 0), CFrame.new(), Vector3.new(3.0, 2.4, 2.0), P, {
					{ Vector3.new(2.4, 1.4, 0.4), CFrame.new(0, 0.35, -1.05), S },
					{ Vector3.new(0.9, 0.9, 0.9), CFrame.new(0, 0.3, -1.3), N, NEON, BALL },
					{ Vector3.new(2.0, 0.7, 1.6), CFrame.new(0, -1.45, 0), S },
					{ Vector3.new(1.3, 0.8, 1.6), CFrame.new(1.9, 0.95, 0), P },
					{ Vector3.new(1.3, 0.8, 1.6), CFrame.new(-1.9, 0.95, 0), P },
					{ Vector3.new(1.34, 0.15, 1.64), CFrame.new(1.9, 1.2, 0), N, NEON },
					{ Vector3.new(1.34, 0.15, 1.64), CFrame.new(-1.9, 1.2, 0), N, NEON },
					-- back pack (pod launcher)
					{ Vector3.new(2.0, 1.6, 0.8), CFrame.new(0, 0.3, 1.4), P },
					{ Vector3.new(0.25, 1.3, 1.0), CFrame.new(0.7, 1.3, 1.5), S, nil, WEDGE },
					{ Vector3.new(0.25, 1.3, 1.0), CFrame.new(-0.7, 1.3, 1.5), S, nil, WEDGE },
					{ Vector3.new(0.6, 0.6, 0.6), CFrame.new(0.5, -0.4, 1.85), N, NEON, BALL },
					{ Vector3.new(0.6, 0.6, 0.6), CFrame.new(-0.5, -0.4, 1.85), N, NEON, BALL },
				}, { PodTip = CFrame.new(0, 1.0, 1.9) } },
				{ "Head", "Torso", "Neck", CFrame.new(0, 1.9, 0), CFrame.new(), Vector3.new(1.6, 1.3, 1.5), S, {
					{ Vector3.new(1.4, 0.35, 0.15), CFrame.new(0, 0.1, -0.78), N, NEON },
					{ Vector3.new(0.25, 0.8, 1.2), CFrame.new(0, 0.95, 0.1), P, nil, WEDGE },
					{ Vector3.new(0.3, 0.6, 0.6), CFrame.new(0.9, 0, 0), P },
					{ Vector3.new(0.3, 0.6, 0.6), CFrame.new(-0.9, 0, 0), P },
				} },
				{ "RArm", "Torso", "RShoulder", CFrame.new(1.95, 0.6, 0), CFrame.new(0, 0.9, 0), Vector3.new(0.9, 2.0, 0.9), S, {
					{ Vector3.new(2.6, 0.9, 0.9), CFrame.new(0, -1.1, -0.9) * FWD, P, nil, CYL },
					{ Vector3.new(0.3, 1.0, 1.0), CFrame.new(0, -1.1, -2.25) * FWD, N, NEON, CYL },
				}, { GunTip = CFrame.new(0, -1.1, -2.5) } },
				{ "LArm", "Torso", "LShoulder", CFrame.new(-1.95, 0.6, 0), CFrame.new(0, 0.9, 0), Vector3.new(0.9, 2.0, 0.9), S, {
					{ Vector3.new(1.2, 1.1, 1.4), CFrame.new(0, -1.1, -0.3), P },
					{ Vector3.new(1.24, 0.3, 0.6), CFrame.new(0, -0.85, -0.6), N, NEON },
				}, { BombTip = CFrame.new(0, -0.5, -1.0) } },
				{ "RLeg", "Torso", "RHip", CFrame.new(0.8, -1.3, 0), CFrame.new(0, 1.7, 0), Vector3.new(1.0, 3.0, 1.0), P, {
					{ Vector3.new(1.1, 0.7, 0.4), CFrame.new(0, 0.2, -0.55), S },
					{ Vector3.new(1.2, 0.5, 2.0), CFrame.new(0, -1.55, -0.3), S },
				} },
				{ "LLeg", "Torso", "LHip", CFrame.new(-0.8, -1.3, 0), CFrame.new(0, 1.7, 0), Vector3.new(1.0, 3.0, 1.0), P, {
					{ Vector3.new(1.1, 0.7, 0.4), CFrame.new(0, 0.2, -0.55), S },
					{ Vector3.new(1.2, 0.5, 2.0), CFrame.new(0, -1.55, -0.3), S },
				} },
			},
		},
		Crusher = {
			Root = Vector3.new(3.6, 3, 3),
			HipHeight = 2.2,
			Limbs = {
				{ "Torso", "HumanoidRootPart", "RootJoint", CFrame.new(0, 0.9, 0), CFrame.new(), Vector3.new(4.4, 3.0, 2.8), P, {
					{ Vector3.new(3.6, 1.2, 0.5), CFrame.new(0, -0.8, -1.5), S, METAL },
					{ Vector3.new(3.0, 0.22, 0.12), CFrame.new(0, 0.75, -1.43), N, NEON },
					{ Vector3.new(3.0, 0.22, 0.12), CFrame.new(0, 0.38, -1.43), N, NEON },
					{ Vector3.new(3.0, 0.22, 0.12), CFrame.new(0, 0.01, -1.43), N, NEON },
					{ Vector3.new(1.9, 1.8, 2.5), CFrame.new(2.9, 0.9, 0), P },
					{ Vector3.new(1.9, 1.8, 2.5), CFrame.new(-2.9, 0.9, 0), P },
					{ Vector3.new(2.0, 0.35, 2.6), CFrame.new(2.9, 1.9, 0), S, METAL },
					{ Vector3.new(2.0, 0.35, 2.6), CFrame.new(-2.9, 1.9, 0), S, METAL },
					{ Vector3.new(1.4, 0.55, 0.55), CFrame.new(1.3, 2.1, 1.1) * UP, S, METAL, CYL },
					{ Vector3.new(1.4, 0.55, 0.55), CFrame.new(-1.3, 2.1, 1.1) * UP, S, METAL, CYL },
					{ Vector3.new(0.2, 0.6, 0.6), CFrame.new(1.3, 2.85, 1.1) * UP, N, NEON, CYL },
					{ Vector3.new(0.2, 0.6, 0.6), CFrame.new(-1.3, 2.85, 1.1) * UP, N, NEON, CYL },
					-- generator pack
					{ Vector3.new(3.0, 2.2, 1.2), CFrame.new(0, 0.3, 2.0), S, METAL },
					{ Vector3.new(2.4, 0.3, 0.1), CFrame.new(0, 0.7, 2.62), N, NEON },
					{ Vector3.new(2.4, 0.3, 0.1), CFrame.new(0, 0.1, 2.62), N, NEON },
				}, { PodTip = CFrame.new(0, 0.2, 2.8) } },
				{ "Head", "Torso", "Neck", CFrame.new(0, 1.9, -0.4), CFrame.new(), Vector3.new(1.5, 1.0, 1.3), S, {
					{ Vector3.new(1.1, 0.22, 0.1), CFrame.new(0, 0.05, -0.68), N, NEON },
					{ Vector3.new(1.8, 0.35, 0.5), CFrame.new(0, 0.45, -0.5), P },
				} },
				{ "RArm", "Torso", "RShoulder", CFrame.new(3.0, 0.3, 0), CFrame.new(0, 1.0, 0), Vector3.new(1.5, 2.4, 1.5), S, {
					{ Vector3.new(2.1, 1.7, 2.6), CFrame.new(0, -1.4, -1.0), P },
					{ Vector3.new(0.9, 0.38, 0.38), CFrame.new(-0.7, -1.4, -2.6) * FWD, D, METAL, CYL },
					{ Vector3.new(0.9, 0.38, 0.38), CFrame.new(-0.35, -1.4, -2.6) * FWD, D, METAL, CYL },
					{ Vector3.new(0.9, 0.38, 0.38), CFrame.new(0, -1.4, -2.6) * FWD, D, METAL, CYL },
					{ Vector3.new(0.9, 0.38, 0.38), CFrame.new(0.35, -1.4, -2.6) * FWD, D, METAL, CYL },
					{ Vector3.new(0.9, 0.38, 0.38), CFrame.new(0.7, -1.4, -2.6) * FWD, D, METAL, CYL },
					{ Vector3.new(2.0, 0.3, 0.12), CFrame.new(0, -0.7, -2.32), N, NEON },
				}, { GunTip = CFrame.new(0, -1.4, -3.0) } },
				{ "LArm", "Torso", "LShoulder", CFrame.new(-3.0, 0.3, 0), CFrame.new(0, 1.0, 0), Vector3.new(1.5, 2.4, 1.5), S, {
					{ Vector3.new(1.6, 1.9, 1.9), CFrame.new(0, -1.5, -0.3) * UP, P, nil, CYL },
					{ Vector3.new(0.25, 1.95, 1.95), CFrame.new(0, -0.6, -0.3) * UP, N, NEON, CYL },
				}, { BombTip = CFrame.new(0, -0.4, -0.4) } },
				{ "RLeg", "Torso", "RHip", CFrame.new(1.3, -1.6, 0), CFrame.new(0, 1.3, 0), Vector3.new(1.8, 2.3, 1.9), P, {
					{ Vector3.new(2.3, 0.7, 2.9), CFrame.new(0, -1.15, -0.2), S, METAL },
					{ Vector3.new(2.32, 0.15, 2.92), CFrame.new(0, -0.9, -0.2), N, NEON },
				} },
				{ "LLeg", "Torso", "LHip", CFrame.new(-1.3, -1.6, 0), CFrame.new(0, 1.3, 0), Vector3.new(1.8, 2.3, 1.9), P, {
					{ Vector3.new(2.3, 0.7, 2.9), CFrame.new(0, -1.15, -0.2), S, METAL },
					{ Vector3.new(2.32, 0.15, 2.92), CFrame.new(0, -0.9, -0.2), N, NEON },
				} },
			},
		},
		Lancer = {
			Root = Vector3.new(2.6, 3, 2.2),
			HipHeight = 3.6,
			Limbs = {
				{ "Torso", "HumanoidRootPart", "RootJoint", CFrame.new(0, 0.8, 0), CFrame.new(), Vector3.new(2.3, 2.6, 1.5), P, {
					{ Vector3.new(2.0, 1.0, 0.3), CFrame.new(0, 0.6, -0.85), S },
					{ Vector3.new(0.7, 0.7, 0.7), CFrame.new(0, -0.05, -0.8), N, NEON, BALL },
					{ Vector3.new(1.4, 0.8, 1.0), CFrame.new(0, -1.6, 0), D, METAL },
					{ Vector3.new(1.1, 1.1, 1.1), CFrame.new(1.45, 1.0, 0), S, nil, BALL },
					{ Vector3.new(1.1, 1.1, 1.1), CFrame.new(-1.45, 1.0, 0), S, nil, BALL },
					-- wings
					{ Vector3.new(0.2, 3.2, 1.2), CFrame.new(1.1, 1.3, 1.0) * CFrame.Angles(0, 0, math.rad(-28)), S },
					{ Vector3.new(0.2, 3.2, 1.2), CFrame.new(-1.1, 1.3, 1.0) * CFrame.Angles(0, 0, math.rad(28)), S },
					{ Vector3.new(0.22, 3.2, 0.2), CFrame.new(1.1, 1.3, 1.55) * CFrame.Angles(0, 0, math.rad(-28)), N, NEON },
					{ Vector3.new(0.22, 3.2, 0.2), CFrame.new(-1.1, 1.3, 1.55) * CFrame.Angles(0, 0, math.rad(28)), N, NEON },
					{ Vector3.new(0.8, 1.2, 0.6), CFrame.new(0, 0.2, 1.0), D, METAL },
					{ Vector3.new(0.5, 0.5, 0.5), CFrame.new(0, -0.5, 1.35), N, NEON, BALL },
				}, { PodTip = CFrame.new(0, 0.8, 1.4) } },
				{ "Head", "Torso", "Neck", CFrame.new(0, 2.05, 0), CFrame.new(), Vector3.new(1.2, 1.5, 1.3), S, {
					{ Vector3.new(1.0, 0.25, 0.1), CFrame.new(0, 0.2, -0.68), N, NEON },
					{ Vector3.new(0.25, 1.6, 1.6), CFrame.new(0, 1.2, 0.2), P, nil, WEDGE },
					{ Vector3.new(1.4, 0.15, 0.15), CFrame.new(0.7, 0.9, 0.3) * UP, D, METAL, CYL },
					{ Vector3.new(1.4, 0.15, 0.15), CFrame.new(-0.7, 0.9, 0.3) * UP, D, METAL, CYL },
				} },
				{ "RArm", "Torso", "RShoulder", CFrame.new(1.5, 0.5, 0), CFrame.new(0, 1.1, 0), Vector3.new(0.7, 2.4, 0.7), P, {
					{ Vector3.new(4.6, 0.55, 0.55), CFrame.new(0, -1.2, -2.0) * FWD, D, METAL, CYL },
					{ Vector3.new(0.4, 0.4, 1.2), CFrame.new(0, -0.8, -1.2), S },
					{ Vector3.new(0.3, 0.8, 0.8), CFrame.new(0, -1.2, -4.3) * FWD, N, NEON, CYL },
				}, { GunTip = CFrame.new(0, -1.2, -4.6) } },
				{ "LArm", "Torso", "LShoulder", CFrame.new(-1.5, 0.5, 0), CFrame.new(0, 1.1, 0), Vector3.new(0.7, 2.4, 0.7), P, {
					{ Vector3.new(0.9, 0.9, 1.3), CFrame.new(0, -1.2, -0.3), S },
					{ Vector3.new(0.92, 0.25, 0.5), CFrame.new(0, -0.95, -0.6), N, NEON },
				}, { BombTip = CFrame.new(0, -0.6, -0.9) } },
				{ "RLeg", "Torso", "RHip", CFrame.new(0.6, -1.4, 0), CFrame.new(0, 2.2, 0), Vector3.new(0.8, 4.0, 0.9), P, {
					{ Vector3.new(0.9, 0.8, 0.5), CFrame.new(0, 0.4, -0.5), S },
					{ Vector3.new(0.9, 0.45, 1.8), CFrame.new(0, -2.1, -0.3), S },
				} },
				{ "LLeg", "Torso", "LHip", CFrame.new(-0.6, -1.4, 0), CFrame.new(0, 2.2, 0), Vector3.new(0.8, 4.0, 0.9), P, {
					{ Vector3.new(0.9, 0.8, 0.5), CFrame.new(0, 0.4, -0.5), S },
					{ Vector3.new(0.9, 0.45, 1.8), CFrame.new(0, -2.1, -0.3), S },
				} },
			},
		},
	}
end

function Builder.Build(def)
	local spec = specs(def)[def.Id]
	assert(spec, "no spec for " .. tostring(def.Id))
	local model = Instance.new("Model")
	model.Name = def.Id
	model:SetAttribute("RobotId", def.Id)

	local root = Instance.new("Part")
	root.Name = "HumanoidRootPart"
	root.Size = spec.Root
	root.Transparency = 1
	root.CanCollide = true
	root.CanQuery = false
	root.CanTouch = true
	root.CFrame = CFrame.new(0, spec.HipHeight + spec.Root.Y / 2, 0)
	root.TopSurface = Enum.SurfaceType.Smooth
	root.BottomSurface = Enum.SurfaceType.Smooth
	root.Parent = model
	model.PrimaryPart = root

	local att = Instance.new("Attachment")
	att.Name = "FaceAttachment"
	att.Parent = root
	local align = Instance.new("AlignOrientation")
	align.Name = "FaceAlign"
	align.Mode = Enum.OrientationAlignmentMode.OneAttachment
	align.Attachment0 = att
	align.Responsiveness = 45
	align.MaxTorque = math.huge
	align.MaxAngularVelocity = math.huge
	align.Parent = root

	local parts = { HumanoidRootPart = root }
	for _, L in ipairs(spec.Limbs) do
		local name, parentName, jointName, c0, c1, size, color, details, attachments = table.unpack(L)
		local parent = parts[parentName]
		local base = mk(model, name, size, parent.CFrame * c0 * c1:Inverse(), color)
		parts[name] = base
		local m = Instance.new("Motor6D")
		m.Name = jointName
		m.Part0 = parent
		m.Part1 = base
		m.C0 = c0
		m.C1 = c1
		m.Parent = parent
		for i, d in ipairs(details) do
			local dsize, dcf, dcolor, dmat, dshape = d[1], d[2], d[3], d[4], d[5]
			local p = mk(model, name .. "_" .. i, dsize, base.CFrame * dcf, dcolor, dmat, dshape)
			local w = Instance.new("WeldConstraint")
			w.Part0 = base
			w.Part1 = p
			w.Parent = p
		end
		if attachments then
			for aname, acf in pairs(attachments) do
				local a = Instance.new("Attachment")
				a.Name = aname
				a.CFrame = acf
				a.Parent = base
			end
		end
	end

	local hum = Instance.new("Humanoid")
	hum.RigType = Enum.HumanoidRigType.R15
	hum.HipHeight = spec.HipHeight
	hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	hum.HealthDisplayType = Enum.HumanoidHealthDisplayType.AlwaysOff
	hum.BreakJointsOnDeath = false
	hum.RequiresNeck = false
	hum.AutoRotate = false
	hum.UseJumpPower = true
	hum.Parent = model
	return model
end

function Builder.BuildAll(robots, folder)
	for _, def in ipairs(robots) do
		local old = folder:FindFirstChild(def.Id)
		if old then
			old:Destroy()
		end
		Builder.Build(def).Parent = folder
	end
end

return Builder
