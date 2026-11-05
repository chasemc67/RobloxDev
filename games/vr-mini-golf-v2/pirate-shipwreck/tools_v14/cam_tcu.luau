-- v14 torch close-up: ~10 studs from the pad 5 torch, ground + 6
local cam = workspace.CurrentCamera
cam.CameraType = Enum.CameraType.Scriptable
cam.FieldOfView = 50
local tm = workspace:FindFirstChild("Torch_Pad05", true)
assert(tm, "Torch_Pad05 missing")
local p = tm:GetPivot().Position
local fl; for _, c in ipairs(tm:GetChildren()) do if c.Name:sub(-5) == "_Glow" or c.Name:sub(-6) == "_Flame" then fl = c end end
local look = fl and fl.Position or p
local tee = Vector3.new(424.7, 0, 379.3)
local dir = Vector3.new(tee.X - look.X, 0, tee.Z - look.Z).Unit
local from = Vector3.new(look.X + dir.X * 10, look.Y - 1.5, look.Z + dir.Z * 10)
cam.CFrame = CFrame.lookAt(from, look)
print("CAM set tcu from", tostring(from), "to", tostring(look))
