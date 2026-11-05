-- v15: list every BasePart whose bounding box the camera ray through a shot pixel crosses (manual slab test; decor has CanQuery off). Read-only.
local cam = workspace.CurrentCamera
local function slab(part, o, d)
  local cf = part.CFrame; local lo = cf:PointToObjectSpace(o); local ld = cf:VectorToObjectSpace(d); local h = part.Size / 2
  local tmin, tmax = 0, 1e9
  for _, ax in ipairs({"X", "Y", "Z"}) do
    local oo, dd, hh = lo[ax], ld[ax], h[ax]
    if math.abs(dd) < 1e-9 then if math.abs(oo) > hh then return nil end
    else local t1, t2 = (-hh - oo) / dd, (hh - oo) / dd; if t1 > t2 then t1, t2 = t2, t1 end; tmin = math.max(tmin, t1); tmax = math.min(tmax, t2); if tmin > tmax then return nil end end
  end
  return tmin
end
local parts = {}
for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("BasePart") and d ~= workspace.Terrain then table.insert(parts, d) end end
return function(pos, look, px, py, maxn)
  cam.CameraType = Enum.CameraType.Scriptable; cam.FieldOfView = 70; cam.CFrame = CFrame.lookAt(pos, look); task.wait(0.2)
  local ray = cam:ViewportPointToRay(277 + px, 2 + py)
  local hits = {}
  for _, p in ipairs(parts) do local t = slab(p, ray.Origin, ray.Direction) if t then table.insert(hits, { p = p, t = t }) end end
  table.sort(hits, function(a, b) return a.t < b.t end)
  local o = {}
  for i = 1, math.min(maxn or 8, #hits) do local p = hits[i].p
    table.insert(o, string.format("  #%d t=%.1f %s | %s | transp %.2f | size %.1f,%.1f,%.1f | mat %s | col %d,%d,%d | mesh %s | tex %s | cq %s dbl %s", i, hits[i].t, p:GetFullName(), p.ClassName, p.Transparency, p.Size.X, p.Size.Y, p.Size.Z, p.Material.Name, p.Color.R*255, p.Color.G*255, p.Color.B*255, p:IsA("MeshPart") and p.MeshId or "", p:IsA("MeshPart") and p.TextureID or "", tostring(p.CanQuery), p:IsA("MeshPart") and tostring(p.DoubleSided) or "-"))
  end
  return table.concat(o, "\n"), hits
end
