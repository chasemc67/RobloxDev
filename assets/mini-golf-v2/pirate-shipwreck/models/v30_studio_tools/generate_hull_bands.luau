-- v27 generator: hull-side collider + sand-bank profile data from the v2_2 Hull mesh (ship-local coordinates).
-- Output: Luau source text for HULLCOLS / BANKPROF tables (pasted into ship_v2_build.luau).
local AS = game:GetService("AssetService")
local em = AS:CreateEditableMeshAsync(Content.fromUri("rbxassetid://140183409961532"), { FixedSize = true })
local C = Vector3.new(20.280494689941406,36.28750133514404,13.720499038696289)
local MCF = CFrame.new(C) * CFrame.Angles(0, math.pi, 0) -- mesh frame in ship space (importer 180 deg flip)
local function hit(o, d)
	local r = { em:RaycastLocal(MCF:PointToObjectSpace(o), MCF:VectorToObjectSpace(d)) }
	for _, x in r do
		if typeof(x) == "Vector3" then return MCF:PointToWorldSpace(x) end
	end
	return nil
end
-- outermost hull z at height y over x samples; side +1 (port, +z) / -1 (starboard)
local function outer(xs, y, side)
	local best
	for _, x in xs do
		local h = hit(Vector3.new(x, y, side * 140 + 13), Vector3.new(0, 0, -side * 300))
		-- reject far-side hits (ray passed through an opening): must be on our side of the centre line
		if h and (h.Z - 12) * side > 0 then
			if not best or (h.Z - best) * side > 0 then best = h.Z end
		end
	end
	return best
end
local function keelAt(x)
	local lo
	for z = -6, 30, 1 do
		local h = hit(Vector3.new(x, -30, z), Vector3.new(0, 120, 0))
		if h and (not lo or h.Y < lo) then lo = h.Y end
	end
	return lo
end
local TOP = 22 -- bands stop 2 below the deck top (24): nothing pokes into the deck / outrigger / tee
_G.V30HullBands = {}
local out = { "local HULLCOLS = {" }
local nparts = 0
local function f(v) return string.format("%.3f", v) end
local function emit(name, cf, size)
	table.insert(_G.V30HullBands,{n=name,cf=cf,s=size})
 local p = cf.Position
	local r = { cf:GetComponents() }
	table.insert(out, string.format('  {n="%s", p={%s,%s,%s}, R={%s,%s,%s,%s,%s,%s,%s,%s,%s}, s={%s,%s,%s}},', name,
		f(p.X), f(p.Y), f(p.Z), f(r[4]), f(r[5]), f(r[6]), f(r[7]), f(r[8]), f(r[9]), f(r[10]), f(r[11]), f(r[12]), f(size.X), f(size.Y), f(size.Z)))
	nparts += 1
end
local STEP = 4
local prof = {}
for xc = -158, 158, STEP do
 task.wait()
	-- bow: past the forecastle (ends x 136.2) the bands go up the stem to 44; from x 88 the bow dune gets within a jump
	-- of 22, so the outer-skin bands go up to 36 (outside the bulwarks; the outrigger exit is far aft at x -131..-108)
	local TOP = if xc >= 140 then 44 elseif xc >= 92 then 36 else 22
	local xs = {}
	for dx = -2, 2, 1 do
		local x = math.clamp(xc + dx, -160.2, 157.5)
		table.insert(xs, x)
	end
	local keel = math.huge
	for _, x in xs do local k = keelAt(x); if k and k < keel then keel = k end end
	if keel == math.huge then continue end
	-- lowest level (2-stud grid, >= keel + 1) with hits on both sides
	local yk
	local y = math.max(0, math.ceil((keel + 1) / 2) * 2)
	while y <= TOP do
		if outer(xs, y, 1) and outer(xs, y, -1) then yk = y; break end
		y += 2
	end
	if not yk then
		-- bow: keel above the band top. Block from below the seabed up to TOP, as wide as the hull's lowest full section
		local yy = math.ceil(keel + 0.5)
		local zp0, zm0
		while yy <= 44 do
			zp0, zm0 = outer(xs, yy, 1), outer(xs, yy, -1)
			if zp0 and zm0 then break end
			yy += 1
		end
		if zp0 and zm0 then
			table.insert(prof, string.format("{%d,%s,%s,%s,%s}", xc, f(keel), f(yy), f(zm0), f(zp0)))
			emit(string.format("COL_HullUnder_%d", xc), CFrame.new(xc, (-24 + TOP) / 2, (zp0 + zm0) / 2), Vector3.new(STEP + 0.6, TOP + 24, zp0 - zm0))
		end
		continue
	end
	local levels = { yk }
	local l = yk + 4
	while l < TOP - 1 do table.insert(levels, l); l += 4 end
	table.insert(levels, TOP)
	local zp, zm = outer(xs, yk, 1), outer(xs, yk, -1)
	table.insert(prof, string.format("{%d,%s,%s,%s,%s}", xc, f(keel), f(yk), f(zm), f(zp)))
	-- block under the hull: skirt-to-skirt, from below the seabed up to yk
	local len = STEP + 0.6
	local bot = -24
	emit(string.format("COL_HullUnder_%d", xc), CFrame.new(xc, (bot + yk) / 2, (zp + zm) / 2), Vector3.new(len, yk - bot, zp - zm))
	for _, side in { 1, -1 } do
		for i = 1, #levels - 1 do
			local ya, yb = levels[i], levels[i + 1]
			local za, zb = outer(xs, ya, side), outer(xs, yb, side)
			if not (za and zb) or yb <= ya then continue end
			local dz, dy = zb - za, yb - ya
			local L = math.sqrt(dz * dz + dy * dy)
			local T = 1.2
			-- band frame: Y axis along the surface line (a -> b), Z axis = outward normal (side)
			local up = Vector3.new(0, dy, dz).Unit
			local nOut = Vector3.new(0, -dz, dy).Unit * side -- perpendicular in the y-z plane
			if nOut.Z * side < 0 then nOut = -nOut end
			local mid = Vector3.new(xc, (ya + yb) / 2, (za + zb) / 2) - nOut * (T / 2)
			local cf = CFrame.fromMatrix(mid, Vector3.xAxis, up, Vector3.xAxis:Cross(up))
			local Lc = L -- inner top corner is at most T above TOP (23.2 < deck top 24)
			emit(string.format("COL_HullSide%s_%d_%d", side > 0 and "P" or "S", xc, i), cf, Vector3.new(len, Lc, T))
		end
	end
end
table.insert(out, "}")
return {bands=#_G.V30HullBands}
