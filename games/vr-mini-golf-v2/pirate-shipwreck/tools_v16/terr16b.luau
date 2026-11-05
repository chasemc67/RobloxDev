-- v16b: confirm v16 edits outside Dressing: pad 17 hump carve (old ray-hit voxels now Air) + Rock retexture, cave_cliff_lower Color
local T = workspace.Terrain
local function vox(p)
  local r = Region3.new(p - Vector3.new(2, 2, 2), p + Vector3.new(2, 2, 2)):ExpandToGrid(4)
  local m, o = T:ReadVoxels(r, 4); return tostring(m[1][1][1]), o[1][1][1]
end
for _, p in ipairs({ Vector3.new(480.6, 84.3, -339.9), Vector3.new(491.8, 81.7, -358.4), Vector3.new(496.8, 87.8, -348.5) }) do
  local m, o = vox(p); print(string.format("TERR16B hump voxel (%.0f,%.0f,%.0f) %s occ=%.2f", p.X, p.Y, p.Z, m, o))
end
local r = Region3.new(Vector3.new(488, 80, -388), Vector3.new(536, 104, -320)):ExpandToGrid(4)
local m = T:ReadVoxels(r, 4); local rock, grass = 0, 0
for x = 1, m.Size.X do for y = 1, m.Size.Y do for z = 1, m.Size.Z do
  local v = m[x][y][z]; if v == Enum.Material.Rock then rock += 1 elseif v == Enum.Material.LeafyGrass then grass += 1 end
end end end
print("TERR16B rock region Rock", rock, "LeafyGrass", grass)
local c = workspace:FindFirstChild("cave_cliff_lower", true)
print("TERR16B cave_cliff_lower", c and tostring(c.Color))
