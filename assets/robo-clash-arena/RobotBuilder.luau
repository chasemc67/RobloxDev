-- Robo Clash Arena: assembles robot rigs from the Blender meshes imported into
-- ServerStorage.RoboClashAssets.Meshes.<Id> (3D Importer, scene position, pivot at origin) and the
-- rig table in RobotRigs (generated from export/*_rig.json by blender/gen_rigs.py).
-- Run in Studio edit mode: require(this).BuildAll(Config.Robots, folder).
-- Rig: invisible HumanoidRootPart (fixed hitbox size) -RootJoint-> Torso pivot -> Neck/RShoulder/LShoulder/
-- RHip/LHip/PodJoint (+ extra anim joints: Fan*/Tail/Wisp). Every limb is an invisible pivot Part driven by a
-- Motor6D; the visual MeshParts (<Limb>Mesh, <Limb>Glow) are WeldConstraint'ed to their pivot and never collide.
-- Forward is -Z. Attachments: GunTip (+GunTip2), BombTip, PodTip.

local ServerStorage = game:GetService("ServerStorage")

local Builder = {}

local function rigs()
	-- not script.Parent: Rebuild requires a temporary clone of this module
	local m = ServerStorage.RoboClashTools:FindFirstChild("RobotRigs")
	assert(m, "RobotRigs module missing")
	local c = m:Clone()
	c.Parent = m.Parent
	local r = (require :: any)(c)
	c:Destroy()
	return r
end

local function pivotPart(parent, name, cf)
	local p = Instance.new("Part")
	p.Name = name
	p.Size = Vector3.new(0.4, 0.4, 0.4)
	p.CFrame = cf
	p.Transparency = 1
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Massless = true
	p.CastShadow = false
	p.Parent = parent
	return p
end

local function rotCF(r: Vector3)
	return CFrame.Angles(math.rad(r.X), math.rad(r.Y), math.rad(r.Z))
end

function Builder.Build(def, rig)
	rig = rig or rigs()[def.Id]
	assert(rig, "no rig for " .. tostring(def.Id))
	local src = ServerStorage:FindFirstChild("RoboClashAssets")
	src = src and src:FindFirstChild("Meshes") and src.Meshes:FindFirstChild(def.Id)
	assert(src, "missing imported meshes ServerStorage.RoboClashAssets.Meshes." .. def.Id)

	local model = Instance.new("Model")
	model.Name = def.Id
	model:SetAttribute("RobotId", def.Id)
	model:SetAttribute("HitRadius", rig.Hitbox.Radius)
	model:SetAttribute("CapDown", rig.Hitbox.Down)
	model:SetAttribute("CapUp", rig.Hitbox.Up)
	model:SetAttribute("Tris", rig.Tris)

	local root = Instance.new("Part")
	root.Name = "HumanoidRootPart"
	root.Size = rig.Root
	root.Transparency = 1
	root.CanCollide = true
	root.CanQuery = false
	root.CanTouch = true
	root.CFrame = CFrame.new(0, rig.HipHeight + rig.Root.Y / 2, 0)
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
	for _, j in ipairs(rig.Joints) do
		local parent = parts[j.Parent]
		assert(parent, j.Name .. ": parent " .. j.Parent .. " not built yet")
		local cf = CFrame.new(j.Pivot) * rotCF(j.Rot)
		local limb = pivotPart(model, j.Part, cf)
		parts[j.Part] = limb
		local m = Instance.new("Motor6D")
		m.Name = j.Name
		m.Part0 = parent
		m.Part1 = limb
		m.C0 = parent.CFrame:ToObjectSpace(cf)
		m.C1 = CFrame.identity
		if j.Anim then
			m:SetAttribute("Anim", j.Anim)
		end
		m.Parent = parent
	end

	for key, info in pairs(rig.Meshes) do
		local mp = src:FindFirstChild(key, true)
		assert(mp and mp:IsA("MeshPart"), "missing mesh " .. def.Id .. "." .. key)
		local limb = parts[info.Limb]
		local v = mp:Clone()
		for _, c in ipairs(v:GetChildren()) do
			c:Destroy()
		end
		v.Name = info.Glow and key or (key .. "Mesh")
		v.Anchored = false
		v.Massless = true
		v.CanCollide = false
		v.CanQuery = false
		v.CanTouch = false
		v.CollisionFidelity = Enum.CollisionFidelity.Box
		-- Neon blooms pale vertex colours to white; GlowTint (Color3 or {Default=, <Limb>=}) keeps them saturated.
		local tint = info.Glow and def.GlowTint or nil
		if typeof(tint) == "table" then
			tint = tint[info.Limb] or tint.Default
		end
		v.Color = tint or Color3.new(1, 1, 1)
		v.Material = info.Glow and Enum.Material.Neon or Enum.Material.SmoothPlastic
		v.CastShadow = not info.Glow
		v.Transparency = 0
		v.CFrame = mp.CFrame
		v:SetAttribute("Glow", info.Glow or nil)
		v.Parent = model
		local w = Instance.new("WeldConstraint")
		w.Part0 = limb
		w.Part1 = v
		w.Parent = v
	end

	for name, a in pairs(rig.Attachments) do
		local limb = parts[a.Part]
		local at = Instance.new("Attachment")
		at.Name = name
		at.CFrame = limb.CFrame:ToObjectSpace(CFrame.new(a.Pos))
		at.Parent = limb
	end

	local hum = Instance.new("Humanoid")
	hum.RigType = Enum.HumanoidRigType.R15
	hum.HipHeight = rig.HipHeight
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
	local all = rigs()
	for _, def in ipairs(robots) do
		local old = folder:FindFirstChild(def.Id)
		if old then
			old:Destroy()
		end
		Builder.Build(def, all[def.Id]).Parent = folder
	end
end

return Builder
