-- v14 read-back: torches (Torch_ models), flame/core/light/emitter spec, neon audit, grey parts, lighting, counts
local grey = Color3.fromRGB(105,103,108)
local ng = 0
for _, d in ipairs(workspace:GetDescendants()) do
  if d:IsA("BasePart") and d.Color == grey then ng += 1; if ng <= 5 then print("CHK14 GREY", d:GetFullName()) end end
end
print("CHK14 grey parts", ng)
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
    if not fl or fl.Material ~= Enum.Material.Neon or fl.Color ~= Color3.fromRGB(255,140,50) or fl.TextureID ~= "" then flameBad += 1 end
    if not core or core.Material ~= Enum.Material.Neon or core.Color ~= Color3.fromRGB(255,220,150) or core.TextureID ~= "" then coreBad += 1 end
    local att = fl and fl:FindFirstChild("LightAttach")
    local li = att and att:FindFirstChildOfClass("PointLight")
    local em = att and att:FindFirstChildOfClass("ParticleEmitter")
    if not li or li.Range ~= 14 or math.abs(li.Brightness - 2.0) > 1e-4 then lightBad += 1 end  -- v14 step 6 tuned (was 10 / 1.2)
    if not em or em.Rate < 3 or em.Rate > 4 then emBad += 1 end
  end
end
table.sort(names)
print("CHK14 torches", torches, "flameBad", flameBad, "coreBad", coreBad, "lightBad", lightBad, "emitterBad", emBad)
print("CHK14 torch names", table.concat(names, ","))
-- neon audit: only torch flames/cores and lantern glass may be Neon
local badNeon = {}
for _, d in ipairs(workspace:GetDescendants()) do
  if d:IsA("BasePart") and d.Material == Enum.Material.Neon then
    local n = d.Name; local pn = d.Parent and d.Parent.Name or ""
    local ok = (n:sub(-5) == "_Glow") or n:sub(-6) == "_Flame" or n:sub(-5) == "_Core" or pn:find("lantern") or pn:find("Lantern") or pn:find("Torch_") or n:lower():find("lantern") or n:lower():find("flame")
    if not ok then table.insert(badNeon, d:GetFullName()) end
  end
end
print("CHK14 other neon parts", #badNeon, badNeon[1] or "")
print("CHK14 meshparts", mp, "instances", ins, "pointlights", pl)
local L = game.Lighting; local a = L:FindFirstChildOfClass("Atmosphere")
print(string.format("CHK14 light clock=%.2f lat=%.1f bright=%.2f exp=%.2f dens=%.3f offset=%.2f haze=%.2f glare=%.2f", L.ClockTime, L.GeographicLatitude, L.Brightness, L.ExposureCompensation, a.Density, a.Offset, a.Haze, a.Glare))
local bl = L:FindFirstChildOfClass("BloomEffect"); print("CHK14 bloom threshold", bl and bl.Threshold, "intensity", bl and bl.Intensity)
print("CHK14 templates", #game.ServerStorage.KitV1:GetChildren(), "http", tostring(game:GetService("HttpService").HttpEnabled), "placeId", game.PlaceId)
local stray = {} for _, c in ipairs(workspace:GetChildren()) do if c.Name:sub(1,4) == "kit_" then table.insert(stray, c.Name) end end
print("CHK14 stray kit_ models in Workspace:", table.concat(stray, ","))
local bi = game.ReplicatedStorage:FindFirstChild("Shared") and game.ReplicatedStorage.Shared:FindFirstChild("BuildInfo")
print("CHK14 sha", bi and bi.Source:match('sha = "(%w+)"'), "dirty", bi and bi.Source:match('dirty = (%w+)'))
print("CHK14 streaming", tostring(workspace.StreamingEnabled))
local sd = L:GetSunDirection(); print(string.format("CHK14 sun dir %.3f %.3f %.3f elevDeg %.1f", sd.X, sd.Y, sd.Z, math.deg(math.asin(sd.Y))))
