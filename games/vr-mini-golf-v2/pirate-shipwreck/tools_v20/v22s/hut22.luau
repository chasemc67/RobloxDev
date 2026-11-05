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
-- v20 hut-lantern helpers: the lantern_hanging PointLights within 26 studs (xz) of a hut
local function HUTLIGHTS()
  local huts, out = {}, {}
  for _, d in ipairs(workspace.World.Dressing:GetDescendants()) do if d:IsA("MeshPart") and d.Name == "hut_leanto" then table.insert(huts, d.Position) end end
  for _, d in ipairs(workspace.World.Dressing:GetDescendants()) do
    if d:IsA("PointLight") and d:FindFirstAncestor("lantern_hanging") then
      local p = d.Parent.WorldPosition
      for _, h in ipairs(huts) do if (Vector3.new(p.X,0,p.Z) - Vector3.new(h.X,0,h.Z)).Magnitude < 26 then table.insert(out, d); break end end
    end
  end
  return out
end
function SETB(b, r) return function() local n = 0 for _, l in ipairs(HUTLIGHTS()) do l.Brightness = b; if r then l.Range = r end; n += 1 end; table.insert(OUT, "SETB " .. b .. " r " .. tostring(r) .. " n " .. n) end end
function SETEN(en) return function() local n = 0 for _, l in ipairs(HUTLIGHTS()) do l.Enabled = en; n += 1 end; table.insert(OUT, "SETEN " .. tostring(en) .. " n " .. n) end end
function READL() local t = {} for _, l in ipairs(HUTLIGHTS()) do table.insert(t, string.format("%.2f/%d/%s/sh=%s/%s", l.Brightness, l.Range, tostring(l.Enabled), tostring(l.Shadows), tostring(l.Color))) end; table.insert(OUT, "LIGHTS " .. table.concat(t, " ")) end
CLEANUP = function() for _, l in ipairs(HUTLIGHTS()) do l.Enabled = true; l.Color = Color3.fromRGB(255,235,200) end; READL(); READT() end
function SETC(r, g, b) return function() for _, l in ipairs(HUTLIGHTS()) do l.Color = Color3.fromRGB(r, g, b) end; table.insert(OUT, "SETC " .. r .. "," .. g .. "," .. b) end end
function HUTS() local t = {} for _, d in ipairs(workspace.World.Dressing:GetDescendants()) do if d:IsA("MeshPart") and d.Name == "hut_leanto" then table.insert(t, d) end end return t end
function SETTEX(id) return function() local n = 0 for _, h in ipairs(HUTS()) do h.TextureID = "rbxassetid://" .. id; n += 1 end; task.wait(4); table.insert(OUT, "SETTEX " .. id .. " n " .. n) end end
function READT() local t = {} for _, h in ipairs(HUTS()) do table.insert(t, h.TextureID) end; table.insert(OUT, "TEX " .. table.concat(t, " ")) end
return RUN({{SETTEX("86926769188910")},{"cam_hut","hut_k271_lit_v22.png"},{SETEN(false)},{"cam_hut","hut_k271_off_v22.png"},{SETEN(true)},{SETTEX("118487047899591")},{"cam_hut","hut_closeup_v22.png"},{SETEN(false)},{"cam_hut","hut_posts_lightsoff_v22.png"},{SETEN(true)},{READL},{"cam_lantern","lantern_v22.png"}})
