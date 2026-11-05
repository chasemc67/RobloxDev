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

local _ok, _src = GET("http://localhost:8765/ident15_ray.luau?t=" .. os.clock()); local PROBE = loadstring(_src)()
local HID = {}
local function hideFirst(pos, look, pts)
  for _, px in ipairs(pts) do
    local _, hits = PROBE(pos, look, px[1], px[2], 1)
    local p = hits[1] and hits[1].p
    if p and not table.find(HID, p) then table.insert(HID, p) end
  end
  for _, p in ipairs(HID) do p.LocalTransparencyModifier = 1; table.insert(OUT, string.format("LTM-hide %s pos=(%.1f,%.1f,%.1f) size=(%.1f,%.1f,%.1f)", p:GetFullName(), p.Position.X, p.Position.Y, p.Position.Z, p.Size.X, p.Size.Y, p.Size.Z)) end
end
function CLEANUP() for _, p in ipairs(HID) do p.LocalTransparencyModifier = 0 end local n = 0 for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("BasePart") and d.LocalTransparencyModifier ~= 0 then n += 1 end end table.insert(OUT, "LTM reset; nonzero=" .. n) end
return RUN({ {function() hideFirst(Vector3.new(205.7,20.5,1.5), Vector3.new(295.2,18.5,46.1), {{653,163},{450,250},{1000,250}}) end},
  {"cam_bf11", "pad_11_back_hidecw_v19.png"} })
