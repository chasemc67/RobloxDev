-- v14 pad 5 tee, VR eye height, looking at the pad 5 rim torch (daylight check)
local cam = workspace.CurrentCamera
cam.CameraType = Enum.CameraType.Scriptable
cam.FieldOfView = 70
local tm = workspace:FindFirstChild("Torch_Pad05", true)
local tgt = tm and tm:GetPivot().Position or Vector3.new(513,10,426)
if tm then local g = tm:FindFirstChildWhichIsA("MeshPart"); print("TORCH05 at", tostring(tgt)) end
cam.CFrame = CFrame.lookAt(Vector3.new(424.7,16.0,379.3), tgt)
print("CAM set tgt5d " .. tostring(cam.CFrame.Position))
