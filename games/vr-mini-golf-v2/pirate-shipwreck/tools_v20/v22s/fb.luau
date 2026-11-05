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
return RUN({{"cam_tf1","pad_1_v22.png"},{"cam_bf1","pad_1_back_v22.png"},{"cam_tf2","pad_2_v22.png"},{"cam_bf2","pad_2_back_v22.png"},{"cam_tf3","pad_3_v22.png"},{"cam_bf3","pad_3_back_v22.png"},{"cam_tf4","pad_4_v22.png"},{"cam_bf4","pad_4_back_v22.png"},{"cam_tf5","pad_5_v22.png"},{"cam_bf5","pad_5_back_v22.png"},{"cam_tf6","pad_6_v22.png"},{"cam_bf6","pad_6_back_v22.png"},{"cam_tf7","pad_7_v22.png"},{"cam_bf7","pad_7_back_v22.png"},{"cam_tf8","pad_8_v22.png"},{"cam_bf8","pad_8_back_v22.png"},{"cam_tf9","pad_9_v22.png"},{"cam_bf9","pad_9_back_v22.png"},{"cam_tf10","pad_10_v22.png"},{"cam_bf10","pad_10_back_v22.png"},{"cam_tf11","pad_11_v22.png"},{"cam_bf11","pad_11_back_v22.png"},{"cam_tf12","pad_12_v22.png"},{"cam_bf12","pad_12_back_v22.png"},{"cam_tf13","pad_13_v22.png"},{"cam_bf13","pad_13_back_v22.png"},{"cam_tf14","pad_14_v22.png"},{"cam_bf14","pad_14_back_v22.png"},{"cam_tf15","pad_15_v22.png"},{"cam_bf15","pad_15_back_v22.png"},{"cam_tf16","pad_16_v22.png"},{"cam_bf16","pad_16_back_v22.png"},{"cam_tf17","pad_17_v22.png"},{"cam_bf17","pad_17_back_v22.png"},{"cam_tf18","pad_18_v22.png"},{"cam_bf18","pad_18_back_v22.png"},})
