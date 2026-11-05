-- v19 ruin_wall close-up, SUNLIT side: pad 17's ruin_wall (406.0,80.7,-313.1), camera ~24 studs out on the +Z (sun) side, FOV 60
local cam = workspace.CurrentCamera
cam.CameraType = Enum.CameraType.Scriptable
cam.FieldOfView = 60
local w = Vector3.new(406.0, 80.7, -313.1)
cam.CFrame = CFrame.lookAt(w + Vector3.new(6, 5, 23), w)
print("CAM set rw19b")
