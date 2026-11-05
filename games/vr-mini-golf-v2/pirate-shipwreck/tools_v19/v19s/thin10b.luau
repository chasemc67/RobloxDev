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
local POS, LOOK = Vector3.new(421.4,18.5,158.0), Vector3.new(521.0,16.5,148.6)
local L1, L2, ALL = {}, {}, {}
for x = 350, 1300, 70 do for y = 140, 440, 50 do
  local _, hits = PROBE(POS, LOOK, x, y, 1)
  local k = 0
  for _, h in ipairs(hits) do
    local p = h.p
    if p.Name == "canopy_wall" or p.Name == "leafclump" then
      k += 1
      local L = (k == 1) and L1 or L2
      L[p] = (L[p] or 0) + 1
      if k >= 2 then break end
    elseif not p.Name:find("palm") and not p.Name:find("torch") and p.Name ~= "rock_l" and p.Name ~= "BackFill_Pad10" then break end
  end
end end
local function list(tag, L) for p, c in pairs(L) do table.insert(OUT, string.format("%s %s pos=(%.1f,%.1f,%.1f) size=(%.1f,%.1f,%.1f) hits=%d", tag, p:GetFullName(), p.Position.X, p.Position.Y, p.Position.Z, p.Size.X, p.Size.Y, p.Size.Z, c)) end end
list("L1", L1) list("L2", L2)
local function hide(L) for p in pairs(L) do p.LocalTransparencyModifier = 1; ALL[p] = true end end
function CLEANUP() for p in pairs(ALL) do p.LocalTransparencyModifier = 0 end local n = 0 for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("BasePart") and d.LocalTransparencyModifier ~= 0 then n += 1 end end table.insert(OUT, "LTM reset; nonzero=" .. n) end
return RUN({ {function() hide(L1) end}, {"cam_bf10", "pad_10_back_thinL1_v19.png"}, {function() hide(L2) end, "pad_10_back_thinL12_v19.png"} })
