-- v22: gangplank seen side-on from the north-east, ground + 8
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = { workspace.Terrain }
local function gy(x, z) local r = workspace:Raycast(Vector3.new(x, 400, z), Vector3.new(0, -600, 0), rp); return r and r.Position.Y or 0 end
local cam = workspace.CurrentCamera
cam.CameraType = Enum.CameraType.Scriptable
cam.FieldOfView = 70
cam.CFrame = CFrame.lookAt(Vector3.new(-455.0, 30, 205.0), Vector3.new(-467.1, 18.0, 257.9))
