-- v14 read-back: torches (Torch_ models), flame/core/light/emitter spec, neon audit, grey parts, lighting, counts
local grey = Color3.fromRGB(105,103,108)
local ng = 0
for _, d in ipairs(workspace:GetDescendants()) do
  if d:IsA("BasePart") and d.Color == grey then ng += 1; if ng <= 5 then print("CHK16 GREY", d:GetFullName()) end end
end
print("CHK16 grey parts", ng)
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
    if not core or core.Material ~= Enum.Material.Neon or core.Color ~= Color3.fromRGB(255,220,150) or core.TextureID ~= "" then coreBad += 1 end
    local att = fl and fl:FindFirstChild("LightAttach")
    local li = att and att:FindFirstChildOfClass("PointLight")
    local em = att and att:FindFirstChildOfClass("ParticleEmitter")
    if not li or li.Range ~= 14 or math.abs(li.Brightness - 1.5) > 1e-4 then lightBad += 1 end
    if not em or em.Rate < 3 or em.Rate > 4 then emBad += 1 end
  end
end
table.sort(names)
print("CHK16 torches", torches, "flameBad", flameBad, "coreBad", coreBad, "lightBad", lightBad, "emitterBad", emBad)
local fc = nil; for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("Model") and d.Name == "Torch_Pad05" then for _, p in ipairs(d:GetChildren()) do if p.Name:sub(-6) == "_Flame" then fc = p end end end end
print("CHK16 flame colour", fc and tostring(fc.Color), "light", fc and tostring(fc:FindFirstChild("LightAttach"):FindFirstChildOfClass("PointLight").Brightness))
print("CHK16 torch names", table.concat(names, ","))
-- neon audit: only torch flames/cores and lantern glass may be Neon
local badNeon = {}
for _, d in ipairs(workspace:GetDescendants()) do
  if d:IsA("BasePart") and d.Material == Enum.Material.Neon then
    local n = d.Name; local pn = d.Parent and d.Parent.Name or ""
    local ok = (n:sub(-5) == "_Glow") or n:sub(-6) == "_Flame" or n:sub(-5) == "_Core" or pn:find("lantern") or pn:find("Lantern") or pn:find("Torch_") or n:lower():find("lantern") or n:lower():find("flame")
    if not ok then table.insert(badNeon, d:GetFullName()) end
  end
end
print("CHK16 other neon parts", #badNeon, badNeon[1] or "")
print("CHK16 meshparts", mp, "instances", ins, "pointlights", pl)
local L = game.Lighting; local a = L:FindFirstChildOfClass("Atmosphere")
print(string.format("CHK16 light clock=%.2f lat=%.1f bright=%.2f exp=%.2f dens=%.3f offset=%.2f haze=%.2f glare=%.2f", L.ClockTime, L.GeographicLatitude, L.Brightness, L.ExposureCompensation, a.Density, a.Offset, a.Haze, a.Glare))
local cc = L:FindFirstChildOfClass("ColorCorrectionEffect"); print("CHK16 colorcorrection", cc and string.format("sat=%.2f contrast=%.2f tint=%s", cc.Saturation, cc.Contrast, tostring(cc.TintColor)))
local bl = L:FindFirstChildOfClass("BloomEffect"); print("CHK16 bloom threshold", bl and bl.Threshold, "intensity", bl and bl.Intensity)
print("CHK16 templates", #game.ServerStorage.KitV1:GetChildren(), "http", tostring(game:GetService("HttpService").HttpEnabled), "placeId", game.PlaceId)
local stray = {} for _, c in ipairs(workspace:GetChildren()) do if c.Name:sub(1,4) == "kit_" then table.insert(stray, c.Name) end end
print("CHK16 stray kit_ models in Workspace:", table.concat(stray, ","))
local bi = game.ReplicatedStorage:FindFirstChild("Shared") and game.ReplicatedStorage.Shared:FindFirstChild("BuildInfo")
print("CHK16 sha", bi and bi.Source:match('sha = "(%w+)"'), "dirty", bi and bi.Source:match('dirty = (%w+)'))
print("CHK16 streaming", tostring(workspace.StreamingEnabled))
local sd = L:GetSunDirection(); print(string.format("CHK16 sun dir %.3f %.3f %.3f elevDeg %.1f", sd.X, sd.Y, sd.Z, math.deg(math.asin(sd.Y))))

-- v16 additions
local a2 = L:FindFirstChildOfClass("Atmosphere")
print("CHK16 atmosphere color", tostring(a2.Color), "decay", tostring(a2.Decay))
local fcnt, fbad, fcol = 0, 0, ""
for _, d in ipairs(workspace.World.Blockout:GetDescendants()) do
  if d:IsA("BasePart") and d.Name:lower():find("felt") then fcnt += 1; fcol = tostring(d.Color); if d.Color ~= Color3.fromRGB(120,190,110) then fbad += 1 end end
end
print("CHK16 felt parts", fcnt, "notExpectedColour", fbad, "last", fcol)
local fp = workspace.World.Blockout:FindFirstChild("HeroPropFootprints"); local fpv, fpn = 0, 0
if fp then for _, d in ipairs(fp:GetChildren()) do if d:IsA("BasePart") then fpn += 1; if d.Transparency < 1 or d.CanCollide then fpv += 1 end end end end
print("CHK16 footprints", fpn, "stillVisibleOrColliding", fpv)
for _, nm in ipairs({"wreck_glow", "cave_glow"}) do
  local f = workspace:FindFirstChild(nm, true)
  print("CHK16", nm, f and f.ClassName, f and tostring(f.Material) or "NOT FOUND")
end
local fills = 0; for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("Part") and d.Name:sub(1, 9) == "BackFill_" then fills += 1 end end
print("CHK16 backfill lights", fills)
-- huts: every hut_leanto MeshPart (placed and template) must be Color white, plain material, no SurfaceAppearance, TextureID set
local hb, hn = 0, 0
for _, d in ipairs(workspace.World.Dressing:GetDescendants()) do
  if d:IsA("MeshPart") and d.Name == "hut_leanto" then hn += 1; if d.Color ~= Color3.fromRGB(255,255,255) or d.Material ~= Enum.Material.Plastic or d.TextureID == "" or d:FindFirstChildOfClass("SurfaceAppearance") then hb += 1 end end
end
print("CHK16 huts", hn, "notWhite/plastic/textured", hb)
