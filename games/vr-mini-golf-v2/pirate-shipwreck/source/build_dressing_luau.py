"""Builds import/dressing_place.luau (embeds data/dressing data + kit bbox centres). Run after make_dressing.py."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(f'{ROOT}/data/kit_manifest_v1_1.json'))['meshes']
M2 = json.load(open(f'{ROOT}/data/kit_manifest_v2.json'))
for _k, _v in M2['meshes'].items(): M.setdefault(_k, _v)
M21 = json.load(open(f'{ROOT}/data/kit_manifest_v2_1.json'))      # v13: kit_v2_1 (canopy_wall, both tiki torches, cliff_ridge) overrides kit_v2
for _k, _v in M21['meshes'].items(): M[_k] = _v
M22 = json.load(open(f'{ROOT}/data/kit_manifest_v2_2.json'))      # v14: kit_v2_2 torches only (separate untextured _Flame and _Core parts); the other 10 meshes are identical to kit_v2_1
for _k, _v in M22['meshes'].items():
    if 'torch' in _k: M[_k] = _v
# v16 hook: kit_v2_4 hut meshes (3D Model Bot palette fix; kit_v2_3 is NOT used, Game Art Bot wants the v2_2 hut kept). Active only if data/kit_manifest_v2_4.json exists (copied from models/kit_v2_4/manifest.json); overrides the hut mesh entries only.
_p24 = f'{ROOT}/data/kit_manifest_v2_4.json'
M24 = json.load(open(_p24)) if os.path.exists(_p24) else {'meshes': {}}
for _k, _v in M24['meshes'].items():
    if 'hut' in _k: M[_k] = _v
LA = {k.replace('kit_', ''): v['LightAttach_pos_roblox_studs'] for k, v in M2['meshes'].items() if 'LightAttach_pos_roblox_studs' in v}
for k, v in M21['meshes'].items():
    if 'LightAttach_pos_roblox_studs' in v: LA[k.replace('kit_', '')] = v['LightAttach_pos_roblox_studs']
for k, v in M22['meshes'].items():
    if 'torch' in k and 'LightAttach_pos_roblox_studs' in v: LA[k.replace('kit_', '')] = v['LightAttach_pos_roblox_studs']
cen = {k.replace('kit_', ''): [round((v['bbox_min'][i] + v['bbox_max'][i]) / 2, 4) for i in range(3)] for k, v in M.items()}
data = open(f'{ROOT}/import/dressing_data.json').read()
body = r'''
local HttpService = game:GetService("HttpService")
local SS = game:GetService("ServerStorage")
local DATA = HttpService:JSONDecode(DATAJ)
local CEN = HttpService:JSONDecode(CENJ)
local out = function(s) print("DR " .. s) end
-- 1. templates -> ServerStorage.KitV1
local kit = SS:FindFirstChild("KitV1")
if not kit then kit = Instance.new("Folder"); kit.Name = "KitV1"; kit.Parent = SS end
-- v12: every imported kit_* model sitting in Workspace (kit_v1_2 rocks, kit_v2 set pieces) becomes / replaces a template; two-part lights (main + _Glow) become a Model template
local function prep(t) t.PivotOffset = CFrame.new(); t.Anchored = true; t.CanCollide = false; t.CanTouch = false; t.CanQuery = false; t.CollisionFidelity = Enum.CollisionFidelity.Box; t.RenderFidelity = Enum.RenderFidelity.Automatic end
local converted = {}
for _, m in ipairs(workspace:GetChildren()) do
	if m:IsA("Model") and m.Name:sub(1, 4) == "kit_" then
		local nm = m.Name:sub(5)
		local mps = {}; for _, d in ipairs(m:GetDescendants()) do if d:IsA("MeshPart") then table.insert(mps, d) end end
		local main = m:FindFirstChild(m.Name, true)
		local old = kit:FindFirstChild(nm); if old then old:Destroy() end
		if #mps == 1 then
			local t = mps[1]:Clone(); t.Name = nm; prep(t); t.CFrame = CFrame.new(0, -500, 0); t.Parent = kit
		else
			local md = Instance.new("Model"); md.Name = nm
			for _, mp in ipairs(mps) do
				local t = mp:Clone(); prep(t); t.CFrame = CFrame.new(0, -500, 0) + (mp.Position - main.Position); t.Parent = md
				if mp == main then md.PrimaryPart = t end
			end
			md.Parent = kit
		end
		table.insert(converted, nm); m:Destroy()
	end
end
if #converted > 0 then out("converted templates: " .. table.concat(converted, ",")) end
out("templates " .. #kit:GetChildren())
-- 2. fresh Dressing folders
local W = workspace.World
local old = W:FindFirstChild("Dressing"); if old then old:Destroy() end
local root = Instance.new("Folder"); root.Name = "Dressing"; root.Parent = W
local folders = {}
local function folder(n) if not folders[n] then local f = Instance.new("Folder"); f.Name = n; f.Parent = root; folders[n] = f end return folders[n] end
-- v11: backdrop / skyline stacks and the reef ring live in a Persistent model so StreamingEnabled never drops the far silhouettes
local persist = Instance.new("Model"); persist.Name = "BackdropPersistent"; persist.ModelStreamingMode = Enum.ModelStreamingMode.Persistent; persist.Parent = root
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = { workspace.Terrain }
local function ground(x, z)
	local r = workspace:Raycast(Vector3.new(x, 500, z), Vector3.new(0, -1000, 0), rp)
	return r and r.Position.Y or nil
end
local TINT = { [1] = Color3.fromRGB(238, 226, 170), [2] = Color3.fromRGB(205, 215, 150), [3] = Color3.fromRGB(226, 214, 160), [4] = Color3.fromRGB(226, 214, 160), [5] = Color3.fromRGB(232, 214, 160), [6] = Color3.fromRGB(205, 215, 150), [7] = Color3.fromRGB(215, 200, 150) }
local ROCK = { rock_s = true, rock_m = true, rock_l = true }
local SHADOW = { palm_s = true, palm_m = true, palm_l = true, palm_lean_a = true, palm_lean_b = true, rock_s = true, rock_m = true, rock_l = true, rock_l2 = true, stack_a = true, stack_b = true, stack_c = true, reef_ring = true, vine_arch = true, hull_rib = true }
local LA = HttpService:JSONDecode(LAJ)
local SHADOW2 = { hut_leanto = true, ruin_arch = true, ruin_wall = true, boulder_pile = true, cliff_ridge = true, canopy_wall = true, torch_tiki = true, torch_tiki_short = true }
-- v13: flame / glass parts are Neon in a bright warm colour, point lights 4 bright with shadows off (daylight-visible glow)
local GLOW, FLAME = Color3.fromRGB(255, 170, 90), Color3.fromRGB(255, 170, 90)
local LIGHT_BRIGHT, LIGHT_RANGE = 4, 18
-- v14 torches
local TCORE_SCALE, TCORE_TRANSP, TCORE_MAT = 0.6, 0.3, Enum.Material.Neon   -- v21: core about 60% size and Transparency 0.3 (it rendered white); if it still renders white switch TCORE_MAT to SmoothPlastic and keep the colour
local TFLAME, TCORE = Color3.fromRGB(240, 110, 30), Color3.fromRGB(255, 190, 110)   -- v20: core (255,190,110) per Game Art Bot (was 255,220,150; an interim (255,200,130) was used before Game Art Bot accepted 255,190,110)
local TLIGHT_RANGE, TLIGHT_BRIGHT = 14, 1.5   -- v14 daylight check; v15 fallback if the flame still renders lemon: TFLAME (240,110,30), TLIGHT_BRIGHT 1.5
-- v14 huts: kit palette already holds Wood1 (110,70,40) / Wood2 (140,95,55) / Straw (200,165,90); no boost, optional darkening multiplier only (HUT_MUL, tuned in Studio from rendered pixels)
local BACKFILL_RANGE, BACKFILL_BRIGHT = 40, 1.5   -- v16 warm fill light behind the tee, pads 10-12
local BACKFILL_PAD = { [10] = { 20, 1.5 }, [11] = { 40, 0.8 }, [12] = { 20, 1.5 } }   -- v21 final (Studio): pad 10 / 12 at range 20 stay off their felt   -- v21: pad 11's light now sits at the hub (hub sand about +16 bright at 1.5); pad 12 felt rendered lime (178,224,119) under 3 / 55   -- v16 Studio tune: pads 11/12 back views lifted; pad 10 keeps 40 / 1.5
local HUT_LANTERN_BRIGHT, HUT_LANTERN_DIST, HUT_LANTERN_RANGE = 1.0, 26, 16   -- v21 Game Art Bot: 1.0 / range 16, shadows on (0.9 if the thatch reads R > 210; v20 had 0.4 / 6, which left the thatch at the lights-off (87,64,24))   -- v20: lantern_hanging PointLights within 26 studs of a hut (they drove the thatch to (251,201,54)); first value 1.5 (was 4), tuned in Studio to a thatch near (200,165,90)
local HUT_MUL = nil   -- nil = keep the template's own Color (never brighten)
local SKYROCK = Color3.fromRGB(140, 138, 140)
local MESHCOL = { hut_leanto = HUT_MUL }   -- optional per-mesh Color tint (wood / thatch pieces), none unless set below
local nlights = 0
local function place(mesh, x, y0, z, yawDeg, scale, layer, tint)
	local t = kit[mesh]; local c = CEN[mesh]
	local base = CFrame.new(x, y0, z) * CFrame.Angles(0, math.rad(yawDeg), 0)
	if t:IsA("Model") then
		local md = Instance.new("Model"); md.Name = mesh
		-- v13: centre every part on the manifest bbox centre via the union AABB of the template (the main part alone is not the whole bbox: tiki torches)
		local mn, mx
		for _, tp in ipairs(t:GetChildren()) do
			local lo, hi = tp.Position - tp.Size / 2, tp.Position + tp.Size / 2
			mn = mn and Vector3.new(math.min(mn.X, lo.X), math.min(mn.Y, lo.Y), math.min(mn.Z, lo.Z)) or lo
			mx = mx and Vector3.new(math.max(mx.X, hi.X), math.max(mx.Y, hi.Y), math.max(mx.Z, hi.Z)) or hi
		end
		local Bc = (mn + mx) / 2
		for _, tp in ipairs(t:GetChildren()) do
			local p = tp:Clone()
			local cc = Vector3.new(c[1], c[2], c[3]) + (tp.Position - Bc)
			p.Size = tp.Size * scale
			p.CFrame = base * CFrame.new(cc * scale)
			p.Anchored = true; p.CanCollide = false; p.CanTouch = false; p.CanQuery = false; p.CastShadow = false
			if MESHCOL[mesh] and p.Name:sub(-5) ~= "_Glow" and p.Name:sub(-6) ~= "_Flame" and p.Name:sub(-5) ~= "_Core" then p.Color = MESHCOL[mesh] end
			local isFlame, isCore = p.Name:sub(-6) == "_Flame", p.Name:sub(-5) == "_Core"
			if isFlame or isCore then
				-- v14 (kit_v2_2): untextured Neon parts; flame 255,140,50, core 255,220,150; light + embers on the flame part's LightAttach
				p.TextureID = ""; p.Material = Enum.Material.Neon
				if isCore then p.Color = TCORE; p.Size = p.Size * TCORE_SCALE; p.Transparency = TCORE_TRANSP; p.Material = TCORE_MAT else
					p.Color = TFLAME
					local la = LA[mesh]
					local att = Instance.new("Attachment"); att.Name = "LightAttach"
					att.Position = (Vector3.new(la[1], la[2], la[3]) - cc) * scale; att.Parent = p
					local li = Instance.new("PointLight"); li.Color = TFLAME; li.Range = TLIGHT_RANGE; li.Brightness = TLIGHT_BRIGHT; li.Shadows = false; li.Parent = att
					local em = Instance.new("ParticleEmitter"); em.Name = "Embers"; em.Rate = 3.5; em.Lifetime = NumberRange.new(1.2, 2.0); em.Speed = NumberRange.new(2, 4); em.SpreadAngle = Vector2.new(25, 25)
					em.Acceleration = Vector3.new(0, 1.5, 0); em.LightEmission = 1; em.Color = ColorSequence.new(Color3.fromRGB(255, 150, 60)); em.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.14), NumberSequenceKeypoint.new(1, 0) }); em.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(1, 1) }); em.Parent = att
					nlights += 1
				end
			elseif p.Name:sub(-5) == "_Glow" then
				local la = LA[mesh]
				local att = Instance.new("Attachment"); att.Name = "LightAttach"
				att.Position = (Vector3.new(la[1], la[2], la[3]) - cc) * scale; att.Parent = p
				p.Material = Enum.Material.Neon; p.Color = GLOW
				local li = Instance.new("PointLight"); li.Color = FLAME; li.Range = LIGHT_RANGE; li.Brightness = LIGHT_BRIGHT; li.Shadows = false; li.Parent = att
				nlights += 1
			end
			p.Parent = md
		end
		md.Parent = folder(layer)
		return md
	end
	local p = t:Clone()
	p.Size = t.Size * scale
	p.CFrame = base * CFrame.new(c[1] * scale, c[2] * scale, c[3] * scale)
	p.Anchored = true; p.CanCollide = false; p.CanTouch = false; p.CanQuery = false
	p.CastShadow = SHADOW[mesh] == true or SHADOW2[mesh] == true
	if MESHCOL[mesh] then p.Color = MESHCOL[mesh] end
	-- v12: kit_v1_2 rocks already carry the (115,100,92) palette; no Studio tint
	if layer == "Backdrop" and mesh:sub(1, 5) == "stack" then p.Color = Color3.fromRGB(238, 232, 180) end
	if layer == "Skyline" then   -- v11: dark silhouettes
		if mesh:sub(1, 5) == "stack" then p.Color = Color3.fromRGB(108, 112, 92)
		elseif ROCK[mesh] then p.Color = SKYROCK   -- v13: darker (was 205,200,195)
		elseif mesh == "cliff_ridge" or mesh == "canopy_wall" then -- kit_v2_1 ridge / canopy colours kept as modelled (no tint)
		else p.Color = Color3.fromRGB(150, 160, 120) end
	end
	p.Name = mesh
	if mesh:sub(1, 5) == "stack" or mesh == "reef_ring" or mesh == "cliff_ridge" or mesh == "canopy_wall" then p.Parent = persist else p.Parent = folder(layer) end
	return p
end
local counts, wet, n = {}, 0, 0
for _, it in ipairs(DATA.items) do
	local mesh, x, z, yaw, sc, layer, tint, dy = it[1], it[2], it[3], it[4], it[5], it[6], it[7], (it[8] or 0)
	local gp = it[9]
	local gy = gp and ground(gp[1], gp[2]) or ground(x, z)
	local y0
	if layer == "Backdrop" or (layer == "Skyline" and (mesh:sub(1, 5) == "stack" or mesh == "cliff_ridge" or mesh == "canopy_wall")) then
		if mesh == "reef_ring" then y0 = (gy and gy > -6) and gy or -6
		elseif mesh == "canopy_wall" then y0 = (gy and gy > 0.2) and (gy - 2) or -8
		else y0 = -12 end
	elseif not gy or gy < 0.2 then
		y0 = nil
	else
		if mesh == "hull_rib" then y0 = gy - 4.2 * sc
		elseif ROCK[mesh] then y0 = gy - 0.15
		elseif mesh == "vine_strip" then y0 = (layer == "Hang") and (gy - 20.0) or (gy - 1.0)
		elseif mesh == "vine_arch" then y0 = gy - 0.4
		elseif mesh == "lantern_hanging" then y0 = gy + dy
		else y0 = gy - 0.3 + dy end
	end
	if y0 then place(mesh, x, y0, z, yaw, sc, layer, tint); counts[mesh] = (counts[mesh] or 0) + 1; n += 1 else wet += 1 end
end
-- 3. cave face vine strips: rays along -Z against the cave parts (CanQuery switched on for the probe only)
local cave = workspace.World.Meshes.CaveV2
local saved = {}
for _, d in ipairs(cave:GetDescendants()) do if d:IsA("BasePart") then saved[d] = d.CanQuery; d.CanQuery = true end end
local rp2 = RaycastParams.new(); rp2.FilterType = Enum.RaycastFilterType.Include; rp2.FilterDescendantsInstances = { cave }
local cv = 0
for _, pr in ipairs(DATA.probes) do
	local r = workspace:Raycast(Vector3.new(pr.x, pr.y, pr.z), Vector3.new(0, 0, -160), rp2)
	if r and r.Normal.Z > 0.5 and r.Position.Z > pr.faceZ - 45 and r.Position.Z < pr.faceZ + 6 and r.Instance.Name:sub(1, 10) == "cave_cliff" then
		local sc = 1.0
		local yaw = math.deg(math.atan2(r.Normal.X, r.Normal.Z))
		place("vine_strip", r.Position.X + r.Normal.X * 0.8, r.Position.Y - 21, r.Position.Z + r.Normal.Z * 0.8, yaw, sc, "Vines", 0)
		cv += 1
	end
end
for d, q in pairs(saved) do d.CanQuery = q end

-- 4. v11: boardwalk planks, stepping stones (Parts, collisions off, no scripts) and placeholder lanterns (Neon part + PointLight)
local wf = folder("Walkways")
local nbw, nst = 0, 0
local WOOD1, WOOD2 = Color3.fromRGB(84, 52, 34), Color3.fromRGB(94, 60, 40)
for k, w in ipairs(DATA.walk) do
	local kind, x, z, yaw = w[1], w[2], w[3], math.rad(w[4])
	if kind == "bw" then
		local len, wid = w[5], w[6]
		local dx, dz = math.sin(yaw) * len / 2, math.cos(yaw) * len / 2
		local gf, gb = ground(x + dx, z + dz), ground(x - dx, z - dz)
		if gf and gb and gf > 0.2 and gb > 0.2 then
			local a, b = Vector3.new(x - dx, gb + 0.15, z - dz), Vector3.new(x + dx, gf + 0.15, z + dz)
			local part = Instance.new("Part"); part.Name = "Boardwalk"; part.Anchored = true; part.CanCollide = false; part.CanTouch = false; part.CanQuery = false; part.CastShadow = false
			part.Material = Enum.Material.WoodPlanks; part.Color = (k % 2 == 0) and WOOD1 or WOOD2
			part.Size = Vector3.new(wid, 0.5, (b - a).Magnitude + 0.15); part.CFrame = CFrame.lookAt((a + b) / 2, b); part.Parent = wf; nbw += 1
		end
	elseif kind == "gp" then
		-- v22: pad 1 gangplank at the wreck rail gap: a plank from the deck (felt top + 5.9) down to the ground, rope posts at both ends and a rope along each side
		local pad1 = workspace.World.Blockout.Pads:FindFirstChild("Pad01")
		local ft = pad1 and pad1:GetAttribute("FeltTopY")
		local len, wid = w[5], w[6]
		local dx, dz = math.sin(yaw) * len / 2, math.cos(yaw) * len / 2
		local gf = ground(x + dx, z + dz)
		if ft and gf then
			local a, b = Vector3.new(x - dx, ft + 5.9, z - dz), Vector3.new(x + dx, gf + 0.2, z + dz)
			local part = Instance.new("Part"); part.Name = "Gangplank"; part.Anchored = true; part.CanCollide = false; part.CanTouch = false; part.CanQuery = false; part.CastShadow = false
			part.Material = Enum.Material.WoodPlanks; part.Color = WOOD2; part.Size = Vector3.new(wid, 0.4, (b - a).Magnitude); part.CFrame = CFrame.lookAt((a + b) / 2, b); part.Parent = wf
			local right = part.CFrame.RightVector
			for _, sd in ipairs({ -1, 1 }) do
				local tops = {}
				for _, f in ipairs({ 0.04, 0.96 }) do
					local c = a:Lerp(b, f) + right * sd * (wid / 2 + 0.3)
					local post = Instance.new("Part"); post.Name = "GangplankPost"; post.Shape = Enum.PartType.Cylinder; post.Anchored = true; post.CanCollide = false; post.CanTouch = false; post.CanQuery = false
					post.Material = Enum.Material.Wood; post.Color = Color3.fromRGB(110, 70, 40); post.Size = Vector3.new(3.4, 0.7, 0.7); post.CFrame = CFrame.new(c + Vector3.new(0, 1.2, 0)) * CFrame.Angles(0, yaw, math.pi / 2); post.Parent = wf
					table.insert(tops, c + Vector3.new(0, 2.4, 0))
				end
				local rp = Instance.new("Part"); rp.Name = "GangplankRope"; rp.Anchored = true; rp.CanCollide = false; rp.CanTouch = false; rp.CanQuery = false; rp.CastShadow = false
				rp.Material = Enum.Material.Fabric; rp.Color = Color3.fromRGB(190, 160, 105); rp.Size = Vector3.new(0.25, 0.25, (tops[2] - tops[1]).Magnitude); rp.CFrame = CFrame.lookAt((tops[1] + tops[2]) / 2, tops[2]); rp.Parent = wf
			end
			nst += 1
		else out("gangplank: no ground / FeltTopY") end
	elseif kind == "mk" then
		-- v21: tee-exit marker, a short rope-wrapped wooden post (3 studs, wood (110,70,40)); no light
		local gy = ground(x, z)
		if gy and gy > 0.2 then
			local hgt = w[5]
			local post = Instance.new("Part"); post.Name = "TeeExitPost"; post.Shape = Enum.PartType.Cylinder; post.Anchored = true; post.CanCollide = false; post.CanTouch = false; post.CanQuery = false
			post.Material = Enum.Material.Wood; post.Color = Color3.fromRGB(110, 70, 40); post.Size = Vector3.new(hgt, 0.7, 0.7)
			post.CFrame = CFrame.new(x, gy + hgt / 2 - 0.15, z) * CFrame.Angles(0, yaw, math.pi / 2); post.Parent = wf
			for _, fy in ipairs({ 0.9, 1.6, 2.3 }) do
				local rp = Instance.new("Part"); rp.Name = "TeeExitRope"; rp.Shape = Enum.PartType.Cylinder; rp.Anchored = true; rp.CanCollide = false; rp.CanTouch = false; rp.CanQuery = false; rp.CastShadow = false
				rp.Material = Enum.Material.Fabric; rp.Color = Color3.fromRGB(190, 160, 105); rp.Size = Vector3.new(0.3, 0.86, 0.86)
				rp.CFrame = CFrame.new(x, gy + fy - 0.15, z) * CFrame.Angles(0, yaw, math.pi / 2); rp.Parent = wf
			end
			nst += 1
		end
	else
		local gy = ground(x, z)
		if gy and gy > 0.2 then
			local d = w[5]
			local part = Instance.new("Part"); part.Name = "StepStone"; part.Shape = Enum.PartType.Cylinder; part.Anchored = true; part.CanCollide = false; part.CanTouch = false; part.CanQuery = false; part.CastShadow = false
			part.Material = Enum.Material.Slate; part.Color = Color3.fromRGB(132, 128, 106)
			part.Size = Vector3.new(0.55, d, d * 0.9); part.CFrame = CFrame.new(x, gy + 0.1, z) * CFrame.Angles(0, yaw, math.pi / 2); part.Parent = wf; nst += 1
		end
	end
end
out(string.format("walkways: %d boardwalk planks, %d stepping stones", nbw, nst))
local nl = 0
local caveF = workspace.World.Meshes:FindFirstChild("CaveV2")
for _, l in ipairs(DATA.lanterns) do
	if l.kind == "rim" then
		local pad = workspace.World.Blockout.Pads:FindFirstChild(string.format("Pad%02d", l.pad))
		local ft = pad and pad:GetAttribute("FeltTopY")
		-- v20: rim torches snap to the terrain (ground ray, -0.1 like the back torches); pad 1 stands on the wreck deck (no terrain there) so it keeps felt top + 0.5
		local gy = (l.pad ~= 1) and ground(l.x, l.z) or nil
		local y0 = gy and (gy - 0.1) or (ft and ft + 5.9)   -- v20 Studio finding: the wreck deck plate sits above the felt top; FeltTopY + 5.9 stands on it
		if y0 then local md = place(l.mesh, l.x, y0, l.z, 0, l.scale, "Set2", 0); md.Name = string.format("Torch_Pad%02d", l.pad); nl += 1 end
	elseif l.kind == "hub" then
		-- v20: second tiki torch at the jungle hub clearing (the pad 11 back torch + lantern post also stand there)
		local gy = ground(l.x, l.z)
		if gy then local md = place(l.mesh, l.x, gy - 0.1, l.z, 0, l.scale, "Set2", 0); md.Name = "Torch_Hub02"; nl += 1 else out("hub torch: no ground") end
	elseif l.kind == "back" then
		-- v16: warm torch + invisible warm fill light 18-25 studs behind the tee of pads 10-12 (back-view canopy edges were near-black)
		local gy = ground(l.x, l.z)
		if gy then
			local md = place(l.mesh, l.x, gy - 0.1, l.z, 0, l.scale, "Set2", 0); md.Name = string.format("Torch_BackPad%02d", l.pad); nl += 1
			local fp = Instance.new("Part"); fp.Name = string.format("BackFill_Pad%02d", l.pad); fp.Anchored = true; fp.CanCollide = false; fp.CanTouch = false; fp.CanQuery = false; fp.CastShadow = false
			fp.Transparency = 1; fp.Size = Vector3.new(1, 1, 1); fp.CFrame = CFrame.new(l.x, gy + 11, l.z); fp.Parent = folder("Set2")
			local li = Instance.new("PointLight"); li.Color = Color3.fromRGB(255, 190, 120); li.Range = BACKFILL_PAD[l.pad] and BACKFILL_PAD[l.pad][1] or BACKFILL_RANGE; li.Brightness = BACKFILL_PAD[l.pad] and BACKFILL_PAD[l.pad][2] or BACKFILL_BRIGHT; li.Shadows = false; li.Parent = fp
		else out("back torch: no ground pad " .. l.pad) end
	else
		local saved2 = {}
		for _, d in ipairs(caveF:GetDescendants()) do if d:IsA("BasePart") then saved2[d] = d.CanQuery; d.CanQuery = true end end
		local rp3 = RaycastParams.new(); rp3.FilterType = Enum.RaycastFilterType.Include; rp3.FilterDescendantsInstances = { caveF, workspace.Terrain }
		local r = workspace:Raycast(Vector3.new(l.x, 130, l.z), Vector3.new(0, -100, 0), rp3)
		for d, q in pairs(saved2) do d.CanQuery = q end
		if r then out(string.format("mouth torch ground %.1f on %s", r.Position.Y, r.Instance.Name)); local md = place(l.mesh, l.x, r.Position.Y - 1.0, l.z, 0, l.scale, "Set2", 0); md.Name = "Torch_CaveMouth"; nl += 1 else out("mouth torch: no ground") end
	end
end
out("torches " .. nl)
-- v22: cut the palm shadows on the felt: palms within 48 studs of the pad 14 tee and the v21 shadow list stop casting shadows
do
	-- v22 Studio final: the 4 Mid palms over pads 2 / 4, and the 4 palm_l@Skyline (about 125 studs south of pad 14) that shaded the pad 14 felt; palms are MeshParts (single-mesh kit templates), not Models
	local NOSH = { {-394.8, 294.7}, {150.6, 397.8}, {161.0, 407.4}, {164.7, 403.9}, {-602.1, -245.4}, {-622.5, -252.7}, {-572.2, -241.5}, {-554.7, -251.9} }
	local p14 = workspace.World.Blockout.Pads:FindFirstChild("Pad14")
	local c14 = p14 and p14:GetPivot().Position
	local nns = 0
	for _, m in ipairs(root:GetDescendants()) do
		if (m:IsA("Model") or m:IsA("BasePart")) and string.sub(m.Name, 1, 4) == "palm" then
			local pp = m:IsA("Model") and m:GetPivot().Position or m.Position
			local hit = c14 and ((pp.X - c14.X) ^ 2 + (pp.Z - c14.Z) ^ 2) < 48 ^ 2
			for _, q in ipairs(NOSH) do if (pp.X - q[1]) ^ 2 + (pp.Z - q[2]) ^ 2 < 6 ^ 2 then hit = true end end
			if hit then
				if m:IsA("BasePart") then m.CastShadow = false end
				for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.CastShadow = false end end; nns += 1
			end
		end
	end
	out("palm shadows off: " .. nns)
end
-- v21: new hut texture (kit_v2_7_1, uploaded Image 86926769188910; kit_v2_7 = 125695280272501) on every hut; the FBX / MeshId are unchanged
-- v22: kit_v2_7_2 (brighter thatch): the uploaded Image id is set as workspace attribute HutTextureId by the build job (the id is only known after the upload; the generator constant is HUT_TEXTURE_ID below once uploaded)
local HUT_TEXTURE_ID = workspace:GetAttribute("HutTextureId") or "rbxassetid://118487047899591"  -- v22 final: kit_v2_7_2 (uploaded Image 118487047899591); v21 was 86926769188910 (kit_v2_7_1)
for _, d in ipairs(root:GetDescendants()) do if d:IsA("MeshPart") and d.Name == "hut_leanto" and HUT_TEXTURE_ID then d.TextureID = HUT_TEXTURE_ID end end
-- v20: lower the lantern lights near huts
do
	local huts = {}
	for _, d in ipairs(root:GetDescendants()) do if d:IsA("MeshPart") and d.Name == "hut_leanto" then table.insert(huts, d.Position) end end
	local nlow = 0
	for _, m in ipairs(root:GetDescendants()) do
		if m:IsA("Model") and m.Name == "lantern_hanging" then
			local pp = nil; for _, c in ipairs(m:GetChildren()) do if c:IsA("BasePart") then pp = c.Position; break end end
			if pp then
				for _, hp in ipairs(huts) do
					if (Vector3.new(pp.X, 0, pp.Z) - Vector3.new(hp.X, 0, hp.Z)).Magnitude < HUT_LANTERN_DIST then
						for _, li in ipairs(m:GetDescendants()) do if li:IsA("PointLight") then li.Brightness = HUT_LANTERN_BRIGHT; li.Range = HUT_LANTERN_RANGE; li.Shadows = true; li.Color = Color3.fromRGB(255, 235, 200) end end   -- v20 Studio tuning: 1.2 and the whiter (255,235,200) light colour put the thatch at (207,167,66)
						nlow += 1; break
					end
				end
			end
		end
	end
	-- v20 Studio finding: the pad 5 rim torch light (range 14) added about +47 R to the hut posts; torch lights within 34 studs of a hut centre get range 12
	for _, md in ipairs(root:GetDescendants()) do
		if md:IsA("Model") and md.Name:sub(1, 6) == "Torch_" then
			local pp = md:FindFirstChildWhichIsA("BasePart", true)
			if pp then for _, hp in ipairs(huts) do
				if (Vector3.new(pp.Position.X, 0, pp.Position.Z) - Vector3.new(hp.X, 0, hp.Z)).Magnitude < 34 then
					for _, li in ipairs(md:GetDescendants()) do if li:IsA("PointLight") then li.Range = 12 end end; break
				end
			end end
		end
	end
	out("hut lanterns lowered " .. nlow .. " (brightness " .. HUT_LANTERN_BRIGHT .. ")")
end
-- v23: COLLISION. Everything a player can stand on or run into collides (Chase: the explore player fell through the scenery); small foliage stays non-colliding.
--   rocks (rock_s only when its largest side >= 2.5 studs) -> Hull; concave / walkable pieces -> Default (precise); crates / barrels / planks / spars -> Box (planks, spars only when >= 3);
--   palms are one mesh with the fronds, so a box on the mesh would wall off the crown: each palm gets a few invisible TrunkCollider blocks along the real trunk (TRUNK, measured on the FBX);
--   ferns, leaves, vines, canopy_wall, torches, lanterns, the sea stacks / reef ring stay non-colliding. CanQuery is on for colliding parts (ball raycasts, the VR floor ray); CanTouch off.
do
	local TRUNK = HttpService:JSONDecode(TRUNKJ)
	local HULL = { rock_l = true, rock_m = true, rock_s = true }
	local PRECISE = { boulder_pile = true, ruin_arch = true, ruin_wall = true, hut_leanto = true, hull_rib = true, cliff_ridge = true, rowboat_broken = true }
	local BOXED = { crate = true, crate_stack = true, barrel = true, planks = true, spar_snapped = true }
	local ncol, ntrunk = {}, 0
	local function solid(p, fid) p.CanCollide = true; p.CanQuery = true; p.CanTouch = false; p.CollisionFidelity = fid end
	for _, p in ipairs(root:GetDescendants()) do
		if p:IsA("MeshPart") then
			local nm = p.Name
			local big = math.max(p.Size.X, p.Size.Y, p.Size.Z)
			local k
			if HULL[nm] and (nm ~= "rock_s" or big >= 2.5) then solid(p, Enum.CollisionFidelity.Hull); k = "hull"
			elseif PRECISE[nm] then solid(p, Enum.CollisionFidelity.Default); k = "precise"
			elseif BOXED[nm] and ((nm ~= "planks" and nm ~= "spar_snapped") or big >= 3) then solid(p, Enum.CollisionFidelity.Box); k = "box"
			elseif TRUNK[nm] then
				local layer = p.Parent and p.Parent.Name or ""
				local pts = TRUNK[nm]
				local c = CEN[nm]
				local sc = p.Size.Y / (c[2] * 2)   -- the template bbox is centred on c (base at y = 0 for upright palms), so Size.Y = bbox height * scale
				local cf, ctr = p.CFrame, Vector3.new(c[1], c[2], c[3])
				local last = (layer == "Skyline") and 3 or #pts
				for i = 1, last - 1 do
					local a = cf * CFrame.new((Vector3.new(pts[i][1], pts[i][2], pts[i][3]) - ctr) * sc)
					local b = cf * CFrame.new((Vector3.new(pts[i + 1][1], pts[i + 1][2], pts[i + 1][3]) - ctr) * sc)
					local len = (b.Position - a.Position).Magnitude
					if len > 0.1 then
						local w = 2 * pts[i + 1][4] * sc * 0.9
						local cp = Instance.new("Part"); cp.Name = "TrunkCollider"; cp.Anchored = true; cp.Transparency = 1; cp.CastShadow = false
						cp.Size = Vector3.new(w, w, len + 0.4); cp.CFrame = CFrame.lookAt((a.Position + b.Position) / 2, b.Position)
						cp.CanCollide = true; cp.CanQuery = true; cp.CanTouch = false; cp.Parent = p; ntrunk += 1
					end
				end
				k = "trunk"
			end
			if k then ncol[k] = (ncol[k] or 0) + 1 end
		end
	end
	-- walkways: boardwalk / gangplank / stepping stones are walkable
	local wf = root:FindFirstChild("Walkways")
	if wf then for _, p in ipairs(wf:GetChildren()) do
		if p:IsA("BasePart") and (p.Name == "Boardwalk" or p.Name == "Gangplank" or p.Name == "StepStone") then p.CanCollide = true; p.CanQuery = true; ncol.walk = (ncol.walk or 0) + 1 end
	end end
	-- the imported world: pad felts / bases / rims (the player stood on the plinth, knee deep in the felt), the hero meshes (wreck, cave)
	local B = workspace.World:FindFirstChild("Blockout")
	local pads = B and B:FindFirstChild("Pads")
	if pads then for _, p in ipairs(pads:GetDescendants()) do if p:IsA("BasePart") and p.Transparency < 1 then p.CanCollide = true; p.CanQuery = true; ncol.pad = (ncol.pad or 0) + 1 end end end
	local M = workspace.World:FindFirstChild("Meshes")
	if M then for _, p in ipairs(M:GetDescendants()) do if p:IsA("MeshPart") and p.Transparency < 1 and not (p.Name:find("_water") or p.Name:find("_glow") or p.Name:find("_foliage")) then solid(p, Enum.CollisionFidelity.Default); ncol.hero = (ncol.hero or 0) + 1 end end end
	local ks = {}; for k, v in pairs(ncol) do table.insert(ks, k .. "=" .. v) end; table.sort(ks)
	out("collision: " .. table.concat(ks, " ") .. " trunkColliders=" .. ntrunk)
end
-- 5. streaming
local function trySet(k, v) local ok, e = pcall(function() workspace[k] = v end); local ok2, cur = pcall(function() return workspace[k] end); return k .. " set=" .. tostring(ok) .. " readable=" .. tostring(ok2) .. " val=" .. tostring(ok2 and cur or "n/a") end
out("streaming " .. trySet("StreamingEnabled", true) .. " | " .. trySet("StreamingMinRadius", 128) .. " | " .. trySet("StreamingTargetRadius", 800))

out("kit_v2 point lights " .. nlights)
out(string.format("placed %d (skipped wet/no-ground %d), cave vine strips %d", n, wet, cv))
local keys = {}; for k, v in pairs(counts) do table.insert(keys, k .. "=" .. v) end; table.sort(keys)
out("counts " .. table.concat(keys, " "))
local inst = 0; for _, d in ipairs(root:GetDescendants()) do inst += 1 end
out("DONE instances " .. inst)
'''
open(f'{ROOT}/import/dressing_place.luau', 'w').write('local DATAJ = [==[' + data + ']==]\nlocal CENJ = [==[' + json.dumps(cen) + ']==]\nlocal LAJ = [==[' + json.dumps(LA) + ']==]\nlocal TRUNKJ = [==[' + open(f'{ROOT}/data/palm_trunks_v23.json').read() + ']==]\n' + body)
print(os.path.getsize(f'{ROOT}/import/dressing_place.luau'))
