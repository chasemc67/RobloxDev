-- v16 pad 17 grass hump: lower the LeafyGrass crown ~100-130 studs ahead of the pad 17 tee (x 468-512, z -388..-320, peak y ~88)
-- to the surrounding ground height (y 78) with a ramp back to the original surface at x 492..512 (boulder_pile base starts ~x 495, bottom y 87).
-- Lowers only (never raises), so the felt plateau (x<=425), dirt trail (y 74-80), torches and boulders are untouched. Terrain data in the place only:
-- a heightmap/terrain regeneration would bring the hump back. A TerrainRegion backup of the region is kept in _G.HUMP16_BACKUP for this session.
local T = workspace.Terrain
local R = 4
local x0, x1, z0, z1, y0, y1 = 460, 516, -392, -320, 60, 104
local reg = Region3.new(Vector3.new(x0, y0, z0), Vector3.new(x1, y1, z1)):ExpandToGrid(R)
_G.HUMP16_BACKUP = T:CopyRegion(Region3int16.new(Vector3int16.new(x0/R, y0/R, z0/R), Vector3int16.new(x1/R - 1, y1/R - 1, z1/R - 1)))
local mats, occ = T:ReadVoxels(reg, R)
local sx, sy, sz = mats.Size.X, mats.Size.Y, mats.Size.Z
local base = reg.CFrame.Position - reg.Size / 2
local TARGET, RAMP0, RAMP1 = 78, 492, 512
local changed, maxDrop = 0, 0
local function top(x, z) for y = sy, 1, -1 do if mats[x][y][z] ~= Enum.Material.Air and occ[x][y][z] > 0 then return base.Y + (y - 1) * R + occ[x][y][z] * R end end return nil end
for x = 1, sx do
	local cx = base.X + (x - 0.5) * R
	for z = 1, sz do
		local orig = top(x, z)
		if orig then
			local t = TARGET
			if cx > RAMP0 then local a = math.clamp((cx - RAMP0) / (RAMP1 - RAMP0), 0, 1); t = TARGET + a * (orig - TARGET) end
			if orig > t + 0.5 then
				for y = 1, sy do
					local vb = base.Y + (y - 1) * R
					if mats[x][y][z] ~= Enum.Material.Air then
						if vb >= t then mats[x][y][z] = Enum.Material.Air; occ[x][y][z] = 0
						elseif vb + R > t then occ[x][y][z] = math.min(occ[x][y][z], math.max((t - vb) / R, 0.05)) end
					end
				end
				changed += 1; maxDrop = math.max(maxDrop, orig - t)
			end
		end
	end
end
T:WriteVoxels(reg, R, mats, occ)
print(string.format("HUMP16 region (%d,%d,%d)-(%d,%d,%d) columns lowered %d maxDrop %.1f target %d ramp x %d..%d", x0, y0, z0, x1, y1, z1, changed, maxDrop, TARGET, RAMP0, RAMP1))
-- part 2 (run after the carve): the rest of the swell is the slope under Set2.boulder_pile (531,109,-356; bottom y 87), which cannot be lowered
-- without leaving the boulders floating, so its LeafyGrass above y 80 becomes Rock and reads as the boulders' rocky base (brief's fallback, for that slope only).
-- Backup of that region in _G.HUMP16_BACKUP2.
_G.HUMP16_BACKUP2 = T:CopyRegion(Region3int16.new(Vector3int16.new(488/4, 80/4, -388/4), Vector3int16.new(536/4 - 1, 104/4 - 1, -320/4 - 1)))
T:ReplaceMaterial(Region3.new(Vector3.new(488, 80, -388), Vector3.new(536, 104, -320)), 4, Enum.Material.LeafyGrass, Enum.Material.Rock)
print("HUMP16 part 2: LeafyGrass -> Rock in (488,80,-388)-(536,104,-320)")
