-- v16 hut audit (read-only): template + every placed hut_leanto MeshPart: Color, Material, TextureID, SurfaceAppearance, children
local function desc(p)
  local sa = p:FindFirstChildOfClass("SurfaceAppearance")
  local kids = {}; for _, c in ipairs(p:GetChildren()) do table.insert(kids, c.ClassName .. ":" .. c.Name) end
  return string.format("%s class=%s color=%s mat=%s tex=%s meshId=%s SA=%s kids=[%s] colorMap=%s trans=%.2f", p:GetFullName(), p.ClassName, tostring(p.Color), tostring(p.Material), p.TextureID, p.MeshId, tostring(sa ~= nil), table.concat(kids, ","), sa and sa.ColorMap or "-", p.Transparency)
end
local t = game.ServerStorage.KitV1:FindFirstChild("hut_leanto")
print("HUT16 template", t and t.ClassName, t and (t:IsA("MeshPart") and desc(t) or "model"))
for _, d in ipairs(workspace.World.Dressing:GetDescendants()) do
  if d:IsA("MeshPart") and d.Name == "hut_leanto" then print("HUT16 placed", desc(d), string.format("pos=(%.1f,%.1f,%.1f)", d.Position.X, d.Position.Y, d.Position.Z)) end
end
local L = game.Lighting
print(string.format("HUT16 lighting bright=%.2f exp=%.2f ambient=%s outdoor=%s envDiffuse=%.2f envSpec=%.2f", L.Brightness, L.ExposureCompensation, tostring(L.Ambient), tostring(L.OutdoorAmbient), L.EnvironmentDiffuseScale, L.EnvironmentSpecularScale))
