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
local POS, LOOK = Vector3.new(421.4,18.5,158.0), Vector3.new(521.0,16.5,148.6)
local function collect()
  local cnt = {}
  for x = 350, 1300, 70 do for y = 140, 440, 50 do
    local _, hits = PROBE(POS, LOOK, x, y, 1)
    for _, h in ipairs(hits) do
      local p = h.p
      local nm = p.Parent:IsA("Model") and p.Parent.Name or p.Name
      if nm == "canopy_wall" or nm == "leafclump" then cnt[p] = (cnt[p] or 0) + 1; break end
      if nm ~= "palm_l" and nm ~= "palm_m" and nm ~= "palm_s" and not nm:find("palm") then break end
    end
  end end
  for p, c in pairs(cnt) do table.insert(HID, p); table.insert(OUT, string.format("CAND %s pos=(%.1f,%.1f,%.1f) size=(%.1f,%.1f,%.1f) hits=%d dist=%.1f", p:GetFullName(), p.Position.X, p.Position.Y, p.Position.Z, p.Size.X, p.Size.Y, p.Size.Z, c, (p.Position - POS).Magnitude)) end
  for _, p in ipairs(HID) do p.LocalTransparencyModifier = 1 end
end
function CLEANUP() for _, p in ipairs(HID) do p.LocalTransparencyModifier = 0 end local n = 0 for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("BasePart") and d.LocalTransparencyModifier ~= 0 then n += 1 end end table.insert(OUT, "LTM reset; nonzero=" .. n) end
return RUN({ {function() collect() end}, {"cam_bf10", "pad_10_back_thintest_v19.png"} })
