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

local A = game.Lighting:FindFirstChildOfClass("Atmosphere")
local H0 = A.Haze
table.insert(OUT, string.format("ATM before dens=%.3f offset=%.2f haze=%.2f glare=%.2f color=%s decay=%s", A.Density, A.Offset, A.Haze, A.Glare, tostring(A.Color), tostring(A.Decay)))
local function h(v) A.Haze = v table.insert(OUT, "haze set " .. v) end
function CLEANUP() A.Haze = H0 table.insert(OUT, "haze restored " .. A.Haze) end
return RUN({ {"cam_ov12"}, {function() h(0.10) end, "haze_ov_010.png"}, {function() h(0.05) end, "haze_ov_005.png"}, {function() h(0.0) end, "haze_ov_000.png"} })
