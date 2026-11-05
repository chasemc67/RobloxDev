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
-- v19 calibration helpers: own temporary test Part (destroyed after) and one-frame cliff texture blank (restored + verified)
local CLIFF_TEX = "rbxassetid://104642093288682"
local CPOS = Vector3.new(597.9, 97.5, -492.2)
local CAMP = Vector3.new(561.8, 99.0, -465.4)
function CALIB_ON(kind)
  local old = workspace:FindFirstChild("V19_CalibPart"); if old then old:Destroy() end
  local p = Instance.new("Part"); p.Name = "V19_CalibPart"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CastShadow = false
  p.Material = Enum.Material.Plastic; p.Color = Color3.fromRGB(115, 100, 92); p.Size = Vector3.new(12, 12, 0.5)
  p.TopSurface = Enum.SurfaceType.Smooth; p.BottomSurface = Enum.SurfaceType.Smooth
  local n
  if kind == "sun" then n = game.Lighting:GetSunDirection() else local d = CAMP - CPOS; n = Vector3.new(d.X, 0, d.Z).Unit end
  p.CFrame = CFrame.lookAt(CPOS, CPOS + n)
  p.Parent = workspace
  local v = workspace.CurrentCamera:WorldToViewportPoint(CPOS)
  table.insert(OUT, string.format("CALIB %s normal (%.2f,%.2f,%.2f) vp (%.0f,%.0f) vpsize %s", kind, n.X, n.Y, n.Z, v.X, v.Y, tostring(workspace.CurrentCamera.ViewportSize)))
end
function CALIB_OFF() local p = workspace:FindFirstChild("V19_CalibPart"); if p then p:Destroy() end; table.insert(OUT, "CALIB destroyed, left=" .. tostring(workspace:FindFirstChild("V19_CalibPart") ~= nil)) end
function BLANK() workspace.World.Meshes.CaveV2.cave_cliff_lower.TextureID = "" end
function UNBLANK() local c = workspace.World.Meshes.CaveV2.cave_cliff_lower; c.TextureID = CLIFF_TEX; table.insert(OUT, "CLIFF restored tex=" .. c.TextureID .. " ok=" .. tostring(c.TextureID == CLIFF_TEX)) end
function CLEANUP()
  local c = workspace.World.Meshes.CaveV2.cave_cliff_lower
  if c.TextureID ~= CLIFF_TEX then c.TextureID = CLIFF_TEX end
  local p = workspace:FindFirstChild("V19_CalibPart"); if p then p:Destroy() end
  table.insert(OUT, "CLEANUP cliffTex ok=" .. tostring(c.TextureID == CLIFF_TEX) .. " calibLeft=" .. tostring(workspace:FindFirstChild("V19_CalibPart") ~= nil))
end
return RUN({ {"cam_bf10","pad_10_back_after_v19.png"},{"cam_bf11","pad_11_back_after_v19.png"},{"cam_bf12","pad_12_back_after_v19.png"},
 {"cam_tcu","torch_closeup_after_v19.png"},{"cam_ov12","overview_after_v19.png"},
})
