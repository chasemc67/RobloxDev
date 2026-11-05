-- v16 Studio-side edits (plain Parts/properties, no scripts, nothing deleted): felt colour, non-Neon glow parts, footprints hidden. Prints before/after.
local B = workspace.World.Blockout
local n, old = 0, {}
for _, d in ipairs(B:GetDescendants()) do
  if d:IsA("BasePart") and d.Name:lower():find("felt") then old[tostring(d.Color)] = (old[tostring(d.Color)] or 0) + 1; d.Color = Color3.fromRGB(120, 190, 110); n += 1 end
end
local o = {}; for k, v in pairs(old) do table.insert(o, k .. "x" .. v) end
print("WORLD16 felt parts", n, "were", table.concat(o, " | "))
local fp = B:FindFirstChild("HeroPropFootprints")
for _, d in ipairs(fp:GetChildren()) do
  if d:IsA("BasePart") then
    print("WORLD16 footprint", d.Name, "was transparency", d.Transparency)
    d.Transparency = 1; d.CanCollide = false; d.CanQuery = false; d.CastShadow = false
  end
end
for _, nm in ipairs({"wreck_glow", "cave_glow"}) do
  for _, d in ipairs(workspace:GetDescendants()) do
    if d.Name == nm and d:IsA("BasePart") then print("WORLD16", d:GetFullName(), d.ClassName, "was", tostring(d.Material), tostring(d.Color), "textureID", d:IsA("MeshPart") and d.TextureID or "-"); d.Material = Enum.Material.SmoothPlastic end
  end
end
