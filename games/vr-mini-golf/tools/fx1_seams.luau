-- Stage fx1: visible felt seam scan for one course root (__ROOT__ is replaced by tools/fx1_stage.py).
-- Samples every edge of every visible playing-surface collider top (GolfSurface parts that render, directly or
-- through a ZF1 visual copy) and asks, a hair inside the collider edge, whether a visible felt top covers it.
--   interior seam  = uncovered, and another surface collider continues past the edge (felt-felt / felt-cup joint)
--   colliderGap    = interior-looking edge where the next collider starts 0.005-0.25 away (gap in the collider itself)
--   perimeter      = uncovered outer edge (no surface beyond), reported separately
--   hiddenNeighbor = beyond the edge is a collider with no felt skin (rendered by an imported mesh): felt meets non-felt
-- Points under a visible non-felt part (rail, decor) are occluded and not counted. Cup circles are excluded.
-- Also reports, per cup, the appearance of each visible cup-area felt piece vs the hole's main felt.
local course = __ROOT__
local CS = game:GetService("CollectionService")
local STEP, INSIDE, OUT = 0.1, 0.006, 0.03
local function holeOf(p)
	local n = p
	while n and n ~= workspace do
		local h = n.Name:match("^Hole(%d+)$")
		if h then return tonumber(h) end
		n = n.Parent
	end
	return 0
end
local function rel(p) return (p:GetFullName():gsub("^Workspace%.", "")) end
local surfaces, visuals, others, cups = {}, {}, {}, {}
local feltVisual = {}
local visibleSurface = {}
for _, p in course:GetDescendants() do
	if p:IsA("BasePart") and CS:HasTag(p, "GolfSurface") then
		local ref = p:FindFirstChild("ZF1VisualReference")
		local v = ref and ref.Value
		local visible = (v and v.Transparency < 1) or p.Transparency < 1
		table.insert(surfaces, { part = p, visible = visible })
		visibleSurface[p] = visible
		if v then feltVisual[v] = p end
		if p.Transparency < 1 then feltVisual[p] = p end
	elseif p:IsA("BasePart") and p.Name == "Cup" and p:GetAttribute("Radius") then
		table.insert(cups, { pos = p.Position, r = p:GetAttribute("Radius"), hole = holeOf(p) })
	end
end
for _, p in course:GetDescendants() do
	if p:IsA("BasePart") and p.Transparency < 1 then
		if feltVisual[p] then table.insert(visuals, p)
		-- occluders: exact block Parts only (rails, caps, boards). Mesh/CSG bounding boxes are not surfaces;
		-- one dressing MeshPart's box can span a whole hole.
		elseif p:IsA("Part") and p.Shape == Enum.PartType.Block and p.Name ~= "CupBottom" and p.Name ~= "Flag" then table.insert(others, p) end
	end
end
-- plan buckets
local CELL = 4
local function bucketize(list)
	local g = {}
	for _, p in list do
		local cf, s = p.CFrame, p.Size / 2
		local ex = math.abs(cf.RightVector.X) * s.X + math.abs(cf.UpVector.X) * s.Y + math.abs(cf.LookVector.X) * s.Z
		local ez = math.abs(cf.RightVector.Z) * s.X + math.abs(cf.UpVector.Z) * s.Y + math.abs(cf.LookVector.Z) * s.Z
		for i = math.floor((cf.X - ex) / CELL), math.floor((cf.X + ex) / CELL) do
			for j = math.floor((cf.Z - ez) / CELL), math.floor((cf.Z + ez) / CELL) do
				local k = i .. "," .. j
				g[k] = g[k] or {}
				table.insert(g[k], p)
			end
		end
	end
	return g
end
local surfaceParts = {}
for _, s in surfaces do table.insert(surfaceParts, s.part) end
local GV, GO, GS = bucketize(visuals), bucketize(others), bucketize(surfaceParts)
local function near(g, pt) return g[math.floor(pt.X / CELL) .. "," .. math.floor(pt.Z / CELL)] or {} end
-- is pt on/near the top face of p (plan inside, height within tol of the top plane)?
local function onTop(p, pt, tol)
	local l = p.CFrame:PointToObjectSpace(pt)
	local s = p.Size / 2
	return math.abs(l.X) <= s.X + 1e-4 and math.abs(l.Z) <= s.Z + 1e-4 and math.abs(l.Y - s.Y) <= tol
end
local function covered(pt)
	for _, v in near(GV, pt) do
		if onTop(v, pt, 0.03) then return v end
	end
	return nil
end
local function occluded(pt)
	for _, o in near(GO, pt) do
		local l = o.CFrame:PointToObjectSpace(pt)
		local s = o.Size / 2
		if math.abs(l.X) <= s.X and math.abs(l.Z) <= s.Z and l.Y <= s.Y + 0.01 and l.Y >= -s.Y - 0.5 then return o end
	end
	return nil
end
local function surfaceAt(pt, except)
	for _, c in near(GS, pt) do
		if c ~= except and onTop(c, pt, 0.06) then return c end
	end
	return nil
end
local function inCup(pt)
	for _, c in cups do
		if (Vector3.new(pt.X - c.pos.X, 0, pt.Z - c.pos.Z)).Magnitude < c.r + 0.03 then return true end
	end
	return false
end
local holes, segs = {}, {}
local function H(h)
	holes[h] = holes[h] or { interior = 0, perimeter = 0, colliderGap = 0, hiddenNeighbor = 0, samples = 0, maxWidth = 0, pairs = {} }
	return holes[h]
end
local n = 0
for _, s in surfaces do
	if not s.visible then continue end
	local c = s.part
	local cf, sz = c.CFrame, c.Size / 2
	local h = holeOf(c)
	for _, e in { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } } do
		local len = e[1] ~= 0 and sz.Z or sz.X
		local half = e[1] ~= 0 and sz.X or sz.Z
		local count = math.max(1, math.floor(2 * len / STEP))
		local run = nil
		for i = 0, count - 1 do
			local t = -len + 0.02 + (2 * len - 0.04) * (i + 0.5) / count
			local function at(d)
				local x = e[1] ~= 0 and e[1] * (half - d) or t
				local z = e[2] ~= 0 and e[2] * (half - d) or t
				return cf:PointToWorldSpace(Vector3.new(x, sz.Y, z))
			end
			local pin = at(INSIDE)
			n += 1
			if n % 4000 == 0 then task.wait() end
			if inCup(pin) then continue end
			H(h).samples += 1
			local kind, other, width = nil, nil, 0
			if not covered(pin) and not occluded(pin) then
				other = surfaceAt(at(-OUT), c)
				-- beyond the edge is a collider that renders through an imported mesh (no felt skin): felt meets non-felt
				if other and not visibleSurface[other] then kind = "hiddenNeighbor"
				elseif other then kind = "interior"
				else
					for _, d in { 0.06, 0.1, 0.15, 0.2, 0.25 } do
						other = surfaceAt(at(-d), c)
						if other then kind = "colliderGap" break end
					end
					kind = kind or "perimeter"
				end
				-- a corner sample in the outer 0.08 inset band (the felt boundary is within 0.1) is perimeter, not a seam
				if kind == "interior" then
					for _, o in { cf.RightVector, -cf.RightVector, cf.LookVector, -cf.LookVector } do
						local q = pin + o * 0.1
						if not surfaceAt(q, nil) then kind = "perimeter" break end
					end
				end
				width = INSIDE
				for _, d in { 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.16, 0.2, 0.3 } do
					if covered(at(d)) then break end
					width = d
				end
			end
			if kind then
				H(h)[kind] += 1
				if kind == "interior" or kind == "colliderGap" then H(h).maxWidth = math.max(H(h).maxWidth, width) end
				local key = kind .. "|" .. rel(c) .. "|" .. (other and rel(other) or "-")
				if run and run.key == key then
					run.to = { pin.X, pin.Y, pin.Z }; run.n += 1; run.width = math.max(run.width, width)
				else
					run = { key = key, kind = kind, hole = h, a = rel(c), b = other and rel(other) or nil, from = { pin.X, pin.Y, pin.Z }, to = { pin.X, pin.Y, pin.Z }, n = 1, width = width,
						edge = e[1] ~= 0 and (e[1] > 0 and "+X" or "-X") or (e[2] > 0 and "+Z" or "-Z") }
					table.insert(segs, run)
					if kind ~= "perimeter" then H(h).pairs[rel(c):match("[^%.]+%.[^%.]+$") .. " / " .. (other and rel(other):match("[^%.]+%.[^%.]+$") or "-")] = true end
				end
			else
				run = nil
			end
		end
	end
end
-- cup-area appearance vs the hole's main (largest visible flat) felt
local function look(p)
	local k = {}
	for _, d in p:GetChildren() do
		if (d:IsA("Texture") or d:IsA("Decal")) and d.Transparency < 1 then
			table.insert(k, d.ClassName .. "|" .. d.Texture .. "|" .. d.Face.Name .. "|" .. string.format("%.2f", d.Transparency) .. "|" .. d.Color3:ToHex()
				.. (d:IsA("Texture") and ("|" .. d.StudsPerTileU .. "x" .. d.StudsPerTileV) or ""))
		elseif d:IsA("SurfaceAppearance") then table.insert(k, "SA|" .. d.ColorMap) end
	end
	table.sort(k)
	local lv = p.CFrame.RightVector
	local grain = math.floor(math.deg(math.atan2(lv.Z, lv.X)) % 180 + 0.5) % 180
	return { color = p.Color:ToHex(), material = p.Material.Name, variant = p.MaterialVariant, tex = table.concat(k, ";"), grain = grain, class = p.ClassName }
end
local cupLooks = {}
for _, cup in cups do
	local main, mainArea
	for _, v in visuals do
		local src = feltVisual[v]
		local l = src.CFrame:PointToObjectSpace(cup.pos)
		local dx, dz = math.max(0, math.abs(l.X) - src.Size.X / 2), math.max(0, math.abs(l.Z) - src.Size.Z / 2)
		-- the adjoining main felt: the largest flat Part whose collider reaches within 2 studs of the cup
		if holeOf(v) == cup.hole and v.CFrame.UpVector.Y > 0.9995 and v:IsA("Part") and math.abs(v.Position.Y + v.Size.Y / 2 - cup.pos.Y) < 0.05
			and math.sqrt(dx * dx + dz * dz) < 2 then
			local a = v.Size.X * v.Size.Z
			if not mainArea or a > mainArea then main, mainArea = v, a end
		end
	end
	local entry = { hole = cup.hole, main = main and rel(main), mainLook = main and look(main), pieces = {} }
	if main then
		local ml = look(main)
		for _, v in visuals do
			if v ~= main and holeOf(v) == cup.hole then
				local d = Vector3.new(v.Position.X - cup.pos.X, 0, v.Position.Z - cup.pos.Z).Magnitude
				local src = feltVisual[v]
				if (d < 2.5 or src.Name == "CupPlate" or src:GetAttribute("CupCut")) and math.abs(v.Position.Y + v.Size.Y / 2 - cup.pos.Y) < 0.6 then
					local l = look(v)
					local ml = ml
					-- a tilted cup piece (a cut into a sloped piece) is compared with the felt of the same tilt
					if v.CFrame.UpVector:Dot(main.CFrame.UpVector) < 0.9999 then
						local best, ba
						for _, w in visuals do
							if w ~= v and holeOf(w) == cup.hole and w:IsA("Part") and w.CFrame.UpVector:Dot(v.CFrame.UpVector) > 0.9999
								and feltVisual[w]:GetAttribute("PieceId") == src:GetAttribute("PieceId") and (not ba or w.Size.X * w.Size.Z > ba) then
								best, ba = w, w.Size.X * w.Size.Z
							end
						end
						if best then ml = look(best) end
					end
					local diff = {}
					for _, k in { "color", "material", "variant", "tex" } do if l[k] ~= ml[k] then table.insert(diff, k) end end
					if l.class == "Part" and l.grain % 90 ~= ml.grain % 90 then table.insert(diff, "grain") end
					if l.class == "Part" and l.grain ~= ml.grain and (l.grain - ml.grain) % 90 == 0 and (l.grain - ml.grain) % 180 ~= 0 then table.insert(diff, "grain90") end
					table.insert(entry.pieces, { path = rel(v), source = rel(src), look = l, differs = diff })
				end
			end
		end
	end
	table.insert(cupLooks, entry)
end
local summary = { interior = 0, perimeter = 0, colliderGap = 0, hiddenNeighbor = 0, affectedHoles = {}, colliderGapHoles = {}, cupPiecesDiffering = 0, cupPieces = 0 }
for h, x in holes do
	summary.interior += x.interior; summary.perimeter += x.perimeter; summary.colliderGap += x.colliderGap; summary.hiddenNeighbor += x.hiddenNeighbor
	local ps = {}
	for k in x.pairs do table.insert(ps, k) end
	table.sort(ps)
	x.pairs = ps
	x.interiorLength = x.interior * STEP
	if x.interior > 0 then table.insert(summary.affectedHoles, h) end
	if x.colliderGap > 0 then table.insert(summary.colliderGapHoles, h) end
end
for _, e in cupLooks do for _, p in e.pieces do summary.cupPieces += 1 if #p.differs > 0 then summary.cupPiecesDiffering += 1 end end end
table.sort(summary.affectedHoles); table.sort(summary.colliderGapHoles)
summary.seamSegments = 0
for _, s in segs do if s.kind == "interior" then summary.seamSegments += 1 end end
local hs = {}
for h, x in holes do hs[tostring(h)] = x end
local keep = {}
for _, s in segs do if s.kind ~= "perimeter" or s.n >= 3 then table.insert(keep, s) end end
_G.FX1Seams = game.HttpService:JSONEncode({ root = course:GetFullName(), step = STEP, inside = INSIDE, summary = summary, holes = hs, segments = keep, cups = cupLooks })
return #_G.FX1Seams
