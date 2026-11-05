-- v19 shot driver prefix: SHOTS = { {cam, name}, ... } must be defined after this file is concatenated; call RUN(SHOTS)
local HS = game:GetService("HttpService")
local OUT = {}
function GET(url) HS.HttpEnabled = true; local ok, r = pcall(function() return HS:GetAsync(url) end); HS.HttpEnabled = false; return ok, r end
function CAM(name)
  local ok, src = GET("http://localhost:8765/" .. name .. ".luau?t=" .. os.clock())
  assert(ok, "cam fetch " .. tostring(src)); local f = assert(loadstring(src)); f()
end
function SHOOT(name)
  task.wait(2.5)
  local ok, r = GET("http://localhost:8767/shoot?name=" .. name)
  table.insert(OUT, name .. ": " .. tostring(r):gsub("\n", " | "))
end
function RESTORE()
  local c = workspace.CurrentCamera; c.CameraType = Enum.CameraType.Custom; c.FieldOfView = 70
  HS.HttpEnabled = false
end
function RUN(list)
  local okAll, err = pcall(function()
    for _, s in ipairs(list) do
      if type(s[1]) == "function" then s[1]() else CAM(s[1]) end
      if s[2] then SHOOT(s[2]) end
    end
  end)
  if not okAll then table.insert(OUT, "RUN ERR " .. tostring(err)) end
  if CLEANUP then CLEANUP() end
  RESTORE()
  local c = workspace.CurrentCamera
  table.insert(OUT, "cam " .. c.CameraType.Name .. " fov " .. c.FieldOfView .. " http " .. tostring(HS.HttpEnabled))
  return table.concat(OUT, "\n")
end

local T = {}
for _, d in ipairs(workspace.World.Dressing.BackdropPersistent:GetChildren()) do
  if d.Name == "canopy_wall" and (d.Position - Vector3.new(521.6,52.5,159.1)).Magnitude < 0.5 then table.insert(T, d) end
end
table.insert(OUT, "found " .. #T)
local function hide() for _, p in ipairs(T) do p.LocalTransparencyModifier = 1 end end
function CLEANUP() for _, p in ipairs(T) do p.LocalTransparencyModifier = 0 end local n = 0 for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("BasePart") and d.LocalTransparencyModifier ~= 0 then n += 1 end end table.insert(OUT, "LTM reset; nonzero=" .. n) end
return RUN({ {function() hide() end}, {"cam_bf10", "t1_bf10.png"}, {"cam_tf9", "t1_tf9.png"}, {"cam_tf10", "t1_tf10.png"}, {"cam_tf11", "t1_tf11.png"}, {"cam_bf9", "t1_bf9.png"}, {"cam_bf11", "t1_bf11.png"}, {"cam_ov12", "t1_ov.png"} })
