-- v16 hut close-up: pad 5 hut (460.1, 23.2, 428.9), camera ~15 studs out from its tee-facing side, looking at thatch roof + posts, FOV 70
local cam = workspace.CurrentCamera
cam.CameraType = Enum.CameraType.Scriptable
cam.FieldOfView = 70
local hut = Vector3.new(460.1, 23.2, 428.9)
local tee = Vector3.new(424.7, 0, 379.3)
local dir = Vector3.new(tee.X - hut.X, 0, tee.Z - hut.Z).Unit
local from = Vector3.new(hut.X + dir.X * 30, 24, hut.Z + dir.Z * 30)
cam.CFrame = CFrame.lookAt(from, hut + Vector3.new(0, 1, 0))
print("CAM set hut from", tostring(from))
