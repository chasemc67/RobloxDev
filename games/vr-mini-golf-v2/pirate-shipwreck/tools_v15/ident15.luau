-- v15 identification of (a) near-camera see-through panels on pads 6, 13, 18 and (b) halo trees. Prints candidates; does not modify anything.
local cams = {
  [6]  = { Vector3.new(712.6,14.0,417.9),  Vector3.new(812.2,8.0,409.0) },
  [13] = { Vector3.new(-344.2,28.5,-161.9), Vector3.new(-430.5,22.5,-212.4) },
  [18] = { Vector3.new(561.8,99.0,-465.4), Vector3.new(642.1,93.0,-525.0) },
}
local cam = workspace.CurrentCamera
local function obbDist(part, p)
  local lp = part.CFrame:PointToObjectSpace(p); local h = part.Size / 2
  local c = Vector3.new(math.clamp(lp.X, -h.X, h.X), math.clamp(lp.Y, -h.Y, h.Y), math.clamp(lp.Z, -h.Z, h.Z))
  return (lp - c).Magnitude, (math.abs(lp.X) <= h.X and math.abs(lp.Y) <= h.Y and math.abs(lp.Z) <= h.Z)
end
for n, c in pairs(cams) do
  cam.CameraType = Enum.CameraType.Scriptable; cam.FieldOfView = 70; cam.CFrame = CFrame.lookAt(c[1], c[2])
  task.wait(0.5)
  local vs = cam.ViewportSize
  local res = {}
  for _, d in ipairs(workspace:GetDescendants()) do
    if d:IsA("BasePart") and d ~= workspace.Terrain and not d:IsDescendantOf(cam) then
      local dist, inside = obbDist(d, c[1])
      if dist < 60 then
        local sp, on = cam:WorldToViewportPoint(d.Position)
        table.insert(res, { d = d, dist = dist, inside = inside, sx = sp.X / vs.X, sy = sp.Y / vs.Y, on = on })
      end
    end
  end
  table.sort(res, function(a, b) return a.dist < b.dist end)
  print("IDENT15 pad", n, "candidates within 60 studs (OBB distance):", #res)
  for i = 1, math.min(14, #res) do
    local r = res[i]; local d = r.d
    local mid = d:IsA("MeshPart") and d.MeshId or ""
    print(string.format("IDENT15 pad %d #%d %s | %s | dist %.1f inside=%s | size %.0f,%.0f,%.0f | transp %.2f | mat %s | color %s | mesh %s | tex %s | screen %.2f,%.2f on=%s", n, i, d:GetFullName(), d.ClassName, r.dist, tostring(r.inside), d.Size.X, d.Size.Y, d.Size.Z, d.Transparency, d.Material.Name, tostring(d.Color), mid, d:IsA("MeshPart") and d.TextureID or "", r.sx, r.sy, tostring(r.on)))
  end
end
cam.CameraType = Enum.CameraType.Custom
