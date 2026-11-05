-- v16b: Dressing signature (name/position/size/colour per part, sorted, hashed) + counts; hut mesh/tex excluded so old vs new hut compares equal
local D = workspace.World.Dressing
local rows = {}
for _, d in ipairs(D:GetDescendants()) do
  if d:IsA("BasePart") then
    table.insert(rows, string.format("%s|%.2f,%.2f,%.2f|%.2f,%.2f,%.2f|%s", d:GetFullName(), d.Position.X, d.Position.Y, d.Position.Z, d.Size.X, d.Size.Y, d.Size.Z, d.Name == "hut_leanto" and "-" or tostring(d.Color)))
  elseif d:IsA("PointLight") then
    table.insert(rows, string.format("%s|L|%.1f|%.2f", d:GetFullName(), d.Range, d.Brightness))
  end
end
table.sort(rows)
local h = 5381
for _, r in ipairs(rows) do for i = 1, #r do h = (h * 33 + string.byte(r, i)) % 4294967296 end end
local n = 0; for _ in ipairs(D:GetDescendants()) do n += 1 end
print(string.format("SIG16B rows=%d desc=%d hash=%08x", #rows, n, h))
return string.format("rows=%d desc=%d hash=%08x", #rows, n, h)
