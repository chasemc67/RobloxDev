-- v21: chk20 with the lantern rule scoped (Attachment WorldPosition; shadows rule skips the 3 ruin_arch 4/18 lanterns)
-- v20 read-back (felt 87,147,79; core 255,190,110; v19 lighting; haze 0.5 density 0.2; hut lantern lights): torches (Torch_ models), flame/core/light/emitter spec, neon audit, grey parts, lighting, counts
local grey = Color3.fromRGB(105,103,108)
local ng = 0
for _, d in ipairs(workspace:GetDescendants()) do
  if d:IsA("BasePart") and d.Color == grey then ng += 1; if ng <= 5 then print("CHK20S GREY", d:GetFullName()) end end
end
print("CHK20S grey parts", ng)
local mp, ins, pl = 0, 0, 0
for _, d in ipairs(workspace:GetDescendants()) do
  ins += 1
  if d:IsA("MeshPart") then mp += 1 end
  if d:IsA("PointLight") then pl += 1 end
end
local torches, flameBad, coreBad, lightBad, emBad = 0, 0, 0, 0, 0
local names = {}
for _, d in ipairs(workspace:GetDescendants()) do
  if d:IsA("Model") and d.Name:sub(1, 6) == "Torch_" then
    torches += 1; table.insert(names, d.Name)
    local fl, core = nil, nil
    for _, p in ipairs(d:GetChildren()) do
      if p.Name:sub(-6) == "_Flame" then fl = p elseif p.Name:sub(-5) == "_Core" then core = p end
    end
    if not fl or fl.Material ~= Enum.Material.Neon or (fl.Color ~= Color3.fromRGB(240,110,30)) or fl.TextureID ~= "" then flameBad += 1 end
    if not core or (core.Material ~= Enum.Material.Neon and core.Material ~= Enum.Material.SmoothPlastic) or math.abs(core.Transparency-0.3) > 0.01 or core.Color ~= Color3.fromRGB(255,190,110) or core.TextureID ~= "" then coreBad += 1 end
    local att = fl and fl:FindFirstChild("LightAttach")
    local li = att and att:FindFirstChildOfClass("PointLight")
    local em = att and att:FindFirstChildOfClass("ParticleEmitter")
    if not li or (li.Range ~= 14 and li.Range ~= 12) or math.abs(li.Brightness - 1.5) > 1e-4 then lightBad += 1 end
    if not em or em.Rate < 3 or em.Rate > 4 then emBad += 1 end
  end
end
table.sort(names)
print("CHK20S torches", torches, "flameBad", flameBad, "coreBad", coreBad, "lightBad", lightBad, "emitterBad", emBad)
local fc = nil; for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("Model") and d.Name == "Torch_Pad05" then for _, p in ipairs(d:GetChildren()) do if p.Name:sub(-6) == "_Flame" then fc = p end end end end
print("CHK20S flame colour", fc and tostring(fc.Color), "light", fc and tostring(fc:FindFirstChild("LightAttach"):FindFirstChildOfClass("PointLight").Brightness))
print("CHK20S torch names", table.concat(names, ","))
-- neon audit: only torch flames/cores and lantern glass may be Neon
local badNeon = {}
for _, d in ipairs(workspace:GetDescendants()) do
  if d:IsA("BasePart") and d.Material == Enum.Material.Neon then
    local n = d.Name; local pn = d.Parent and d.Parent.Name or ""
    local ok = (n:sub(-5) == "_Glow") or n:sub(-6) == "_Flame" or n:sub(-5) == "_Core" or pn:find("lantern") or pn:find("Lantern") or pn:find("Torch_") or n:lower():find("lantern") or n:lower():find("flame")
    if not ok then table.insert(badNeon, d:GetFullName()) end
  end
end
print("CHK20S other neon parts", #badNeon, badNeon[1] or "")
print("CHK20S meshparts", mp, "instances", ins, "pointlights", pl)
local L = game.Lighting; local a = L:FindFirstChildOfClass("Atmosphere")
print(string.format("CHK20S light clock=%.2f lat=%.1f bright=%.2f exp=%.2f dens=%.3f offset=%.2f haze=%.2f glare=%.2f", L.ClockTime, L.GeographicLatitude, L.Brightness, L.ExposureCompensation, a.Density, a.Offset, a.Haze, a.Glare))
local cc = L:FindFirstChildOfClass("ColorCorrectionEffect"); print("CHK20S colorcorrection", cc and string.format("sat=%.2f contrast=%.2f tint=%s", cc.Saturation, cc.Contrast, tostring(cc.TintColor)))
local bl = L:FindFirstChildOfClass("BloomEffect"); print("CHK20S bloom threshold", bl and bl.Threshold, "intensity", bl and bl.Intensity)
print("CHK20S templates", #game.ServerStorage.KitV1:GetChildren(), "http", tostring(game:GetService("HttpService").HttpEnabled), "placeId", game.PlaceId)
local stray = {} for _, c in ipairs(workspace:GetChildren()) do if c.Name:sub(1,4) == "kit_" then table.insert(stray, c.Name) end end
print("CHK20S stray kit_ models in Workspace:", table.concat(stray, ","))
local bi = game.ReplicatedStorage:FindFirstChild("Shared") and game.ReplicatedStorage.Shared:FindFirstChild("BuildInfo")
print("CHK20S sha", bi and bi.Source:match('sha = "(%w+)"'), "dirty", bi and bi.Source:match('dirty = (%w+)'))
print("CHK20S streaming", tostring(workspace.StreamingEnabled))
local sd = L:GetSunDirection(); print(string.format("CHK20S sun dir %.3f %.3f %.3f elevDeg %.1f", sd.X, sd.Y, sd.Z, math.deg(math.asin(sd.Y))))

-- v16 additions
local a2 = L:FindFirstChildOfClass("Atmosphere")
print("CHK20S atmosphere color", tostring(a2.Color), "decay", tostring(a2.Decay))
local fcnt, fbad, fcol = 0, 0, ""
for _, d in ipairs(workspace.World.Blockout:GetDescendants()) do
  if d:IsA("BasePart") and d.Name:lower():find("felt") then fcnt += 1; fcol = tostring(d.Color); if d.Color ~= Color3.fromRGB(87,147,79) then fbad += 1 end end
end
print("CHK20S felt parts", fcnt, "notExpectedColour", fbad, "last", fcol)
local fp = workspace.World.Blockout:FindFirstChild("HeroPropFootprints"); local fpv, fpn = 0, 0
if fp then for _, d in ipairs(fp:GetChildren()) do if d:IsA("BasePart") then fpn += 1; if d.Transparency < 1 or d.CanCollide then fpv += 1 end end end end
print("CHK20S footprints", fpn, "stillVisibleOrColliding", fpv)
for _, nm in ipairs({"wreck_glow", "cave_glow"}) do
  local f = workspace:FindFirstChild(nm, true)
  print("CHK20S", nm, f and f.ClassName, f and tostring(f.Material) or "NOT FOUND")
end
local fills = 0; for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("Part") and d.Name:sub(1, 9) == "BackFill_" then fills += 1 end end
print("CHK20S backfill lights", fills)
-- huts: every hut_leanto MeshPart (placed and template) must be Color white, plain material, no SurfaceAppearance, TextureID set
local hb, hn = 0, 0
for _, d in ipairs(workspace.World.Dressing:GetDescendants()) do
  if d:IsA("MeshPart") and d.Name == "hut_leanto" then hn += 1; if d.Color ~= Color3.fromRGB(255,255,255) or d.Material ~= Enum.Material.Plastic or d.TextureID == "" or d:FindFirstChildOfClass("SurfaceAppearance") then hb += 1 end end
end
print("CHK20S huts", hn, "notWhite/plastic/textured", hb)

-- v20 expected-value asserts
local function eq(a, b) return math.abs(a.R-b.R) < 0.003 and math.abs(a.G-b.G) < 0.003 and math.abs(a.B-b.B) < 0.003 end
local function C(r,g,b) return Color3.fromRGB(r,g,b) end
local okAll = true
local function chk(name, cond) if not cond then okAll = false end print("CHK20S EXPECT", name, cond and "ok" or "FAIL") end
local at = L:FindFirstChildOfClass("Atmosphere")
chk("Brightness 1.6", math.abs(L.Brightness - 1.6) < 1e-3)
chk("ColorShift_Top", eq(L.ColorShift_Top, C(255,245,230)))
chk("ColorShift_Bottom", eq(L.ColorShift_Bottom, C(0,0,0)))
chk("Ambient", eq(L.Ambient, C(110,110,115)))
chk("OutdoorAmbient", eq(L.OutdoorAmbient, C(135,135,140)))
chk("Exposure -0.3", math.abs(L.ExposureCompensation + 0.3) < 1e-3)
chk("Atmosphere Haze 0 (v21)", math.abs(at.Haze) < 1e-3)
chk("Atmosphere Density .2 Offset .05 Glare .3", math.abs(at.Density-0.2)<1e-3 and math.abs(at.Offset-0.05)<1e-3 and math.abs(at.Glare-0.3)<1e-3)
chk("Atmosphere Color/Decay", eq(at.Color, C(255,235,210)) and eq(at.Decay, C(190,150,110)))
chk("ColorCorrection sat 0 contrast .05", cc and math.abs(cc.Saturation) < 1e-3 and math.abs(cc.Contrast-0.05) < 1e-3)
chk("Bloom threshold 1.1", bl and math.abs(bl.Threshold-1.1) < 1e-3)
chk("felt parts all (87,147,79)", fcnt == 18 and fbad == 0)
chk("torch core bad 0", coreBad == 0)
chk("footprints hidden", fpv == 0)
local lanB = {}
for _, d in ipairs(workspace.World.Dressing:GetDescendants()) do
  if d:IsA("PointLight") then
    local m = d:FindFirstAncestor("lantern_hanging")
    -- v20c: scope to HUT lanterns (within 26 studs of a hut_leanto); the 3 ruin_arch lanterns keep the generator default 4 / 18
    local near = false
    if m then
      local lp = d.Parent and ((d.Parent:IsA("Attachment") and d.Parent.WorldPosition) or (d.Parent:IsA("BasePart") and d.Parent.Position)) or nil
      for _, h in ipairs(workspace.World.Dressing:GetDescendants()) do
        if h.Name == "hut_leanto" and lp then local hp = h:IsA("Model") and h:GetPivot().Position or (h:IsA("BasePart") and h.Position) or nil; if hp and (Vector3.new(hp.X,0,hp.Z)-Vector3.new(lp.X,0,lp.Z)).Magnitude < 26 then near = true break end end
      end
    end
    if m and near then local k = string.format("%.2f/%d", d.Brightness, d.Range); lanB[k] = (lanB[k] or 0) + 1 end
  end
end
local o = {}; for k, v in pairs(lanB) do table.insert(o, k .. "x" .. v) end
print("CHK20S lantern_hanging PointLights (brightness/range x count):", table.concat(o, " | "))
local onlyOK, nl = true, 0
for k, v in pairs(lanB) do nl += v; if k ~= "1.00/16" and k ~= "0.90/16" then onlyOK = false end end
chk("hut lantern lights 1.0 (or 0.9) / range 16 (v21)", onlyOK and nl > 0)
local shOK, matBad = true, 0
for _, d in ipairs(workspace.World.Dressing:GetDescendants()) do if d:IsA("PointLight") and d:FindFirstAncestor("lantern_hanging") and not d.Shadows and not (d.Brightness == 4 and d.Range == 18) then shOK = false end end
for _, d in ipairs(workspace.World.Blockout:GetDescendants()) do if d:IsA("BasePart") and d.Name:lower():find("felt") and d.Material ~= Enum.Material.Plastic then matBad += 1 end end
chk("hut lantern shadows on", shOK)
chk("felt Material Plastic all 18", matBad == 0)
print("CHK20S ALL EXPECTED", okAll and "GREEN" or "RED")
