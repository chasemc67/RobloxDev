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
