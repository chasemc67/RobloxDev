local W = workspace
local found
for _, m in W:GetChildren() do
  if m:IsA("Model") then print("FOL top-level model " .. m.Name) end
end
local holder = W:FindFirstChild("cave_foliage")
local mp = holder and holder:FindFirstChildWhichIsA("MeshPart", true)
if not mp then print("FOL missing") return end
local o = mp.PivotOffset.Position
local c = Vector3.new(o.X, -o.Y, o.Z)
local caveCF = CFrame.new(563.5, 66, -606.5)
mp.Parent = W.World.Meshes.CaveV1
mp.Anchored = true; mp.CanCollide = false; mp.CanTouch = false; mp.CanQuery = false; mp.CastShadow = true
mp.PivotOffset = CFrame.new()
mp.CFrame = caveCF * CFrame.new(c)
holder:Destroy()
print(("FOL ok size=%s pos=%s tex=%s mesh=%s"):format(tostring(mp.Size), tostring(mp.Position), mp.TextureID, mp.MeshId))
