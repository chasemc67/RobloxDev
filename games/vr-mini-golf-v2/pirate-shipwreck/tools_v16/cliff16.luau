-- v16 pad 18 tan cliff: the tan faces in the left half of cam_tf18 are Workspace.World.Meshes.CaveV2.cave_cliff_lower
-- (MeshPart, MeshId rbxassetid://78593172579470, TextureID rbxassetid://99336401497933 palette PNG, Plastic, Color was 163,162,165).
-- Color does not tint a textured MeshPart (rendered pixels identical), so this only records the rock colour; the visible fix needs the palette PNG tan cells changed.
-- Terrain is NOT changed (the lower-left mound is terrain Slate, colour left as is). A SurfaceAppearance tint was tested and not kept.
local p = workspace.World.Meshes.CaveV2.cave_cliff_lower
print("CLIFF16", p:GetFullName(), "was", tostring(p.Color))
p.Color = Color3.fromRGB(115, 100, 92)
for _, c in ipairs(p:GetChildren()) do if c.Name == "TEST16_SA" then c:Destroy() end end
print("CLIFF16 now", tostring(p.Color), "SA", tostring(p:FindFirstChildOfClass("SurfaceAppearance") ~= nil), "tex", p.TextureID)
