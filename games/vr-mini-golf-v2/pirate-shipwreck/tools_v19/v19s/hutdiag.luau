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

local hut=Vector3.new(460.1,23.2,428.9)
local L={}
for _,d in ipairs(workspace.World.Dressing.Set2:GetDescendants()) do
 if d:IsA("PointLight") and d.Parent:IsA("Attachment") and (d.Parent.WorldPosition-hut).Magnitude<20 and d.Enabled then table.insert(L,d) end
end
function CLEANUP() for _,l in ipairs(L) do l.Enabled=true end local n=0 for _,l in ipairs(L) do if l.Enabled then n+=1 end end table.insert(OUT,"lanterns re-enabled "..n.."/"..#L) end
return RUN({ {"cam_hut"}, {function() for _,l in ipairs(L) do l.Enabled=false end table.insert(OUT,"disabled "..#L) end, "hut_diag_nolantern_v19.png"} })
