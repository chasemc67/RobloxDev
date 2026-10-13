-- Stage aj: repeatable local build repairs. Applies after geometry and after each visual import.
-- Visual changes never change course collision. The seven explicit obstacle proxies are Parts.
local ServerStorage = game:GetService("ServerStorage")
local Overrides = {}
-- Approved manifest pivots; mesh library is populated by tools/stage_aj_props.py.
local APPROVED_VISUALS = {
 {id="h08_ground",hole=8,position={360,70,55},yaw=0},
 {id="h09_water_tank",hole=9,position={370,70,-121.65},yaw=-90},
}

local function restoreApprovedVisuals(course)
 local library=ServerStorage:FindFirstChild("StageAJProps")
 if not library then return {} end
 local layout=require(ServerStorage.CourseData.SugarloafLayout:Clone())
 local offset=Vector3.new(unpack(layout.offset))
 local restored={}
 for _,spec in APPROVED_VISUALS do
  local source=library:FindFirstChild(spec.id)
  local hole=course:FindFirstChild("Hole"..spec.hole)
  if not source or not hole then continue end
  local target=hole:FindFirstChild("StageAJVisuals")
  if not target then target=Instance.new("Folder");target.Name="StageAJVisuals";target.Parent=hole end
  local approved=target:FindFirstChild(spec.id)
  for _,d in course:GetDescendants() do
   if d:IsA("Model") and d.Name==spec.id and d~=approved then
    local physical=false
    for _,p in d:GetDescendants() do if p:IsA("BasePart") and p.CanCollide then physical=true end end
    if not physical then d:Destroy() end
   end
  end
  if not approved then approved=source:Clone();approved.Parent=target end
  approved:PivotTo(CFrame.new(Vector3.new(unpack(spec.position))+offset)*CFrame.Angles(0,math.rad(spec.yaw),0))
  approved:SetAttribute("StageAJVisual",true)
  for _,p in approved:GetDescendants() do
   if p:IsA("BasePart") then
    p.Anchored=true;p.CanCollide=false;p.CanQuery=false;p.CanTouch=false
    p:SetAttribute("VisualQueryDisabled",true)
   end
  end
  table.insert(restored,approved:GetFullName())
 end
 return restored
end

local function isTradingPost(p)
	local node = p
	while node do
		local name = string.lower(node.Name):gsub("[^%w]", "")
		if string.find(name, "tradingpost", 1, true) then return true end
		node = node.Parent
	end
	return false
end

function Overrides.Apply(course)
	course = course or workspace:FindFirstChild("CourseSugarloaf")
	assert(course, "CourseSugarloaf missing")
	local data = require(ServerStorage.CourseData.SugarloafCanyon:Clone())
	local cfg = require(game.ReplicatedStorage.Golf.Config)
	local report = { cameraParts = {}, removedPlaceholders = {}, raisedVisuals = {}, colliders = {}, railcapsByHole = {} }
	report.approvedVisuals = restoreApprovedVisuals(course)
	local physics = game:GetService("PhysicsService")
	if not physics:IsCollisionGroupRegistered("GolfWall") then physics:RegisterCollisionGroup("GolfWall") end
	for _, d in course:GetDescendants() do
		if d:IsA("BasePart") and isTradingPost(d) then
			d.CanCollide, d.CanQuery, d.CanTouch = false, false, false
			d:SetAttribute("VisualQueryDisabled", true)
			table.insert(report.cameraParts, d:GetFullName())
		end
	end
	for _, h in data.holes do
		local hole = course:FindFirstChild("Hole" .. h.number)
		if not hole then continue end
		local cf = CFrame.new(hole:GetAttribute("HoleOrigin")) * CFrame.Angles(0, math.rad(hole:GetAttribute("HoleYaw") or 0), 0)
		local decor = hole:FindFirstChild("Decor")
		local rails = hole:FindFirstChild("Rails")
		local count = 0
		if h.number == 8 and rails then
			for _,p in rails:GetChildren() do
				if p:IsA("BasePart") and not p.CanCollide and (p.Name=="Bumper_gumdrop1" or p.Name=="Bumper_gumdrop2") then
					p.Transparency=1
					p.CanQuery,p.CanTouch=false,false
					p:SetAttribute("VisualQueryDisabled",true)
					p:SetAttribute("ReplacedBy","approved gumdrop mesh")
				end
			end
		end
		for _, p in rails and rails:GetDescendants() or {} do
			if p:IsA("BasePart") and not p.CanCollide and string.sub(p.Name, 1, 8) == "RailCap_" then
				if not p:GetAttribute("StageAjRaised") then
					p.CFrame += Vector3.new(0, 0.02, 0)
					p:SetAttribute("StageAjRaised", true)
					table.insert(report.raisedVisuals, p:GetFullName())
				end
				count += 1
			end
		end
		report.railcapsByHole[tostring(h.number)] = count
		if decor then
			local name = h.number == 14 and "loading_dock" or h.number == 9 and "water_tank" or nil
			local anchor = name and decor:FindFirstChild(name)
			-- Water-tank placeholder is suppressed permanently: the approved imported mesh is the visual.
			local ph = anchor and anchor:FindFirstChild("Placeholder")
			if ph then table.insert(report.removedPlaceholders, ph:GetFullName()); ph:Destroy() end
		end
		local geometry = hole:FindFirstChild("Geometry")
		if not geometry then continue end
		for _, a in h.decoration_anchors or {} do
			local boxes = {}
			if h.number == 7 and a.name == "island_hoodoo" then
				boxes = a.occluders or {}
			elseif h.number == 17 and string.match(a.name, "^hour_stone_") and a.exact_box and not a.exact_box.collidable then
				boxes = { a.exact_box }
			end
			for index, box in boxes do
				local id = a.name .. "_proxy_" .. index
				local p
				for _, old in geometry:GetChildren() do
					if old:GetAttribute("StageAjObstacle") == id then p = old; break end
				end
				p = p or Instance.new("Part")
				p.Name = "Wall"
				p.Anchored = true
				p.Size = Vector3.new(unpack(box.size))
				p.CFrame = cf * CFrame.new(unpack(box.center)) * CFrame.Angles(0, math.rad(box.yaw or 0), 0)
				p.Transparency, p.CastShadow = 1, false
				p.CanCollide, p.CanQuery, p.CanTouch = true, true, false
				p.CollisionGroup = "GolfWall"
				p.CustomPhysicalProperties = PhysicalProperties.new(1, cfg.WallFriction, cfg.WallElasticity, 100, 100)
				p:SetAttribute("StageAjObstacle", id)
				p:SetAttribute("WallId", id)
				p:SetAttribute("PrimitiveBoundsSource", "holes.json decoration_anchors")
				p.Parent = geometry
				table.insert(report.colliders, { id = id, hole = h.number, size = box.size, center = box.center })
			end
		end
	end
	return report
end

return Overrides
