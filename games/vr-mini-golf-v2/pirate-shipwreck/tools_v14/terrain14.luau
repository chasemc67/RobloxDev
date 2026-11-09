-- v14: terrain rock faces in the kit rock tint (Rock 115,100,92 per Game Art; Slate a step darker)
local T = workspace.Terrain
T:SetMaterialColor(Enum.Material.Rock, Color3.fromRGB(115,100,92))
T:SetMaterialColor(Enum.Material.Slate, Color3.fromRGB(105,95,88))
print("TERRAIN14 rock", tostring(T:GetMaterialColor(Enum.Material.Rock)), "slate", tostring(T:GetMaterialColor(Enum.Material.Slate)))
