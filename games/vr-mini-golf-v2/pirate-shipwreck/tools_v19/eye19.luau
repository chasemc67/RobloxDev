-- v19 step 4 read-only audit: Dressing items in the back-view cone of pads 10-12 whose top is above the back camera eye, + pixel probes
local PROBE = loadstring(game:GetService("HttpService"):GetAsync("http://localhost:8765/ident15_ray.luau?t=" .. os.clock()))()
local cams = {
  [10] = { Vector3.new(421.4,18.5,158.0), Vector3.new(521.0,16.5,148.6), { {612,245}, {300,150}, {900,200} } },
  [11] = { Vector3.new(205.7,20.5,1.5), Vector3.new(295.2,18.5,46.1), { {653,163}, {450,120}, {850,140} } },
  [12] = { Vector3.new(-101.6,25.5,-86.8), Vector3.new(-5.7,23.5,-58.4), { {184,122}, {600,150}, {1000,180} } },
}
local out = {}
local items = {}
for _, d in ipairs(workspace.World.Dressing:GetDescendants()) do
  if d:IsA("MeshPart") and d.Transparency < 1 then table.insert(items, d) end
end
for _, n in ipairs({10, 11, 12}) do
  local c = cams[n]; local pos, look = c[1], c[2]
  local fwd = Vector3.new(look.X - pos.X, 0, look.Z - pos.Z).Unit
  local list = {}
  for _, p in ipairs(items) do
    local layer = p.Parent and p.Parent.Name or "?"
    if p.Parent and p.Parent:IsA("Model") then layer = p.Parent.Parent.Name end
    local nm = p.Parent:IsA("Model") and p.Parent.Name or p.Name
    local v = Vector3.new(p.Position.X - pos.X, 0, p.Position.Z - pos.Z); local dist = v.Magnitude
    if dist < 160 and dist > 1 then
      local ang = math.deg(math.acos(math.clamp(v.Unit:Dot(fwd), -1, 1)))
      local top = p.Position.Y + p.Size.Y / 2
      if ang < 80 and top > pos.Y and (nm:find("leaf") or nm:find("fern") or nm:find("frond") or layer == "Skyline") then
        table.insert(list, { dist, string.format("  %s/%s pos=(%.1f,%.1f,%.1f) size=(%.1f,%.1f,%.1f) top=%.1f eye=%.1f over=%.1f dist=%.1f ang=%.0f", layer, nm, p.Position.X, p.Position.Y, p.Position.Z, p.Size.X, p.Size.Y, p.Size.Z, top, pos.Y, top - pos.Y, dist, ang) })
      end
    end
  end
  table.sort(list, function(a, b) return a[1] < b[1] end)
  table.insert(out, string.format("EYE19 pad %d: %d leaf/fern/Skyline items above eye in 160deg/160 cone", n, #list))
  for i = 1, math.min(#list, 25) do table.insert(out, list[i][2]) end
  for _, px in ipairs(c[3]) do
    local s = PROBE(pos, look, px[1], px[2], 4)
    table.insert(out, string.format(" PROBE pad %d px (%d,%d):\n%s", n, px[1], px[2], s))
  end
end
local cam = workspace.CurrentCamera; cam.CameraType = Enum.CameraType.Custom; cam.FieldOfView = 70
return table.concat(out, "\n")
