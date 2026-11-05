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
  local ok, r = GET("http://localhost:8770/shoot?name=" .. name)
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
return RUN({{"v21s/cam_exit1","exit_markers_1_v22.png"},{"v21s/cam_exit1b","exit_markers_1b_v22.png"},{"v21s/cam_exit2","exit_markers_2_v22.png"},{"v21s/cam_exit4","exit_markers_4_v22.png"},{"v21s/cam_exit5","exit_markers_5_v22.png"},{"v21s/cam_exit7","exit_markers_7_v22.png"},{"v21s/cam_exit8","exit_markers_8_v22.png"},{"v21s/cam_exit9","exit_markers_9_v22.png"},{"v21s/cam_exit11","exit_markers_11_v22.png"},{"v22s/cam_gp_tee2","gangplank_v22.png"},{"v22s/cam_gp_beach2","gangplank_beach_v22.png"},{"cam_bf12","pad_12_back_v22.png"}})
