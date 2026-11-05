-- v19 step 2b read-back: rim torch positions in the pad felt frame + ground gap (read-only)
local out = {}
local pads = workspace.World.Blockout.Pads
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = { workspace.Terrain }
local rp2 = RaycastParams.new(); rp2.FilterType = Enum.RaycastFilterType.Exclude
for _, n in ipairs({1, 4, 5, 6, 8, 10, 12, 15, 17, 18}) do
  local tm = workspace:FindFirstChild(string.format("Torch_Pad%02d", n), true)
  local felt = pads:FindFirstChild(string.format("Pad%02d", n)) and pads[string.format("Pad%02d", n)]:FindFirstChild("Felt")
  if not tm or not felt then table.insert(out, "TORCH19 pad " .. n .. " MISSING torch=" .. tostring(tm) .. " felt=" .. tostring(felt)) continue end
  local cf, size = tm:GetBoundingBox()
  local base = Vector3.new(cf.Position.X, cf.Position.Y - size.Y / 2, cf.Position.Z)
  local l = felt.CFrame:PointToObjectSpace(base)
  local hit = workspace:Raycast(base + Vector3.new(0, 30, 0), Vector3.new(0, -80, 0), rp)
  rp2.FilterDescendantsInstances = { tm, workspace.Terrain }
  local hitAny = workspace:Raycast(base + Vector3.new(0, 30, 0), Vector3.new(0, -80, 0), rp2)
  -- nearest rail/rim part to the torch base (anything in the pad model except Felt)
  local near, nd = nil, 1e9
  for _, d in ipairs(felt.Parent:GetDescendants()) do
    if d:IsA("BasePart") and d ~= felt then
      local lp = d.CFrame:PointToObjectSpace(base); local h = d.Size / 2
      local q = Vector3.new(math.max(math.abs(lp.X) - h.X, 0), math.max(math.abs(lp.Y) - h.Y, 0), math.max(math.abs(lp.Z) - h.Z, 0))
      if q.Magnitude < nd then nd = q.Magnitude; near = d end
    end
  end
  table.insert(out, string.format("TORCH19 pad %d base=(%.1f,%.1f,%.1f) u=%.1f v=%.1f (felt half %.0fx%.0f) terrainY=%s gap=%s otherHit=%s nearestPadPart=%s dist=%.1f",
    n, base.X, base.Y, base.Z, l.X, l.Z, felt.Size.X / 2, felt.Size.Z / 2,
    hit and string.format("%.2f", hit.Position.Y) or "none", hit and string.format("%.2f", base.Y - hit.Position.Y) or "-",
    hitAny and (hitAny.Instance:GetFullName() .. string.format("@%.2f", hitAny.Position.Y)) or "none", near and near.Name or "-", nd))
end
return table.concat(out, "\n")
