-- v19 ruin_wall close-up: pad 17's placed ruin_wall (406.0,80.7,-313.1), camera ~22 studs out toward the pad 17 tee side, FOV 60
local cam = workspace.CurrentCamera
cam.CameraType = Enum.CameraType.Scriptable
cam.FieldOfView = 60
local w = Vector3.new(406.0, 80.7, -313.1)
local dir = Vector3.new(-0.707, 0, -0.707)
cam.CFrame = CFrame.lookAt(w + dir * 22 + Vector3.new(0, 3, 0), w)
print("CAM set rw19")
