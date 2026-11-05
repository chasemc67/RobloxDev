-- v22: gangplank seen from the beach, 25 studs east of its foot, eye = ground + 5
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = { workspace.Terrain }
local function gy(x, z) local r = workspace:Raycast(Vector3.new(x, 400, z), Vector3.new(0, -600, 0), rp); return r and r.Position.Y or 0 end
local cam = workspace.CurrentCamera
cam.CameraType = Enum.CameraType.Scriptable
cam.FieldOfView = 70
cam.CFrame = CFrame.lookAt(Vector3.new(-430.0, gy(-430.0, 285.0) + 5, 285.0), Vector3.new(-460.0, 14.0, 257.5))
