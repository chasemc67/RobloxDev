-- v20 grade20: applies the SAME values the generator now writes (data/lighting.json + padRules.feltColor + make_import) to an already-imported place,
-- so the Studio-side v16..v19 grade patches are no longer needed. Idempotent; prints before/after.
local L = game.Lighting
local function C(r,g,b) return Color3.fromRGB(r,g,b) end
print(string.format("GRADE20 before bright=%.2f top=%s amb=%s out=%s exp=%.2f", L.Brightness, tostring(L.ColorShift_Top), tostring(L.Ambient), tostring(L.OutdoorAmbient), L.ExposureCompensation))
L.Brightness = 1.6; L.ColorShift_Top = C(255,245,230); L.ColorShift_Bottom = C(0,0,0); L.Ambient = C(110,110,115); L.OutdoorAmbient = C(135,135,140); L.ExposureCompensation = -0.3
local a = L:FindFirstChildOfClass("Atmosphere")
a.Density = 0.2; a.Offset = 0.05; a.Haze = 0; a.Glare = 0.3; a.Color = C(255,235,210); a.Decay = C(190,150,110)
local cc = L:FindFirstChildOfClass("ColorCorrectionEffect"); cc.Saturation = 0; cc.Contrast = 0.05; cc.TintColor = C(255,255,255)
local B = workspace.World.Blockout
local n = 0
for _, d in ipairs(B:GetDescendants()) do
  if d:IsA("BasePart") and d.Name:lower():find("felt") then d.Color = C(87,147,79); n += 1 end
end
local fp = B:FindFirstChild("HeroPropFootprints")
if fp then for _, d in ipairs(fp:GetChildren()) do if d:IsA("BasePart") then d.Transparency = 1; d.CanCollide = false; d.CanQuery = false; d.CastShadow = false end end end
for _, nm in ipairs({"wreck_glow", "cave_glow"}) do
  for _, d in ipairs(workspace:GetDescendants()) do if d.Name == nm and d:IsA("BasePart") then d.Material = Enum.Material.SmoothPlastic end end
end
print(string.format("GRADE20 after bright=%.2f haze=%.2f felt parts=%d", L.Brightness, a.Haze, n))
