-- Read-only capture. Bounds are MeshPart OBBs, not a claim about hollow rendered mesh occupancy.
assert(game.PlaceId == 0 and not game:FindFirstChildOfClass("NetworkClient"), "local Edit place required")
local C = workspace.CourseSugarloaf
local function vec(v) return {v.X,v.Y,v.Z} end
local function record(p)
 local cf=p.CFrame
 return {path=p:GetFullName(),name=p.Name,class=p.ClassName,size=vec(p.Size),center=vec(p.Position),axes={vec(cf.RightVector),vec(cf.UpVector),vec(-cf.LookVector)},
 collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,transparency=p.Transparency,group=p.CollisionGroup,
 wall=p:GetAttribute("WallId"),piece=p:GetAttribute("PieceId"),raised=p:GetAttribute("StageAjRaised"),proxy=p:GetAttribute("StageAjObstacle"),
 skipQuery=p:GetAttribute("VisualQueryDisabled"),surface=p:HasTag("GolfSurface"),mesh=p:IsA("MeshPart") and p.MeshId or nil}
end
local out={layoutOffset=require(game.ServerStorage.CourseData.SugarloafLayout:Clone()).offset,placeId=game.PlaceId,networkClient=false,parts={},holes={},placeholders={},importModels={}}
for _,h in C:GetChildren() do
 local n=tonumber(h.Name:match("^Hole(%d+)$"))
 if n then out.holes[tostring(n)]={origin=vec(h:GetAttribute("HoleOrigin")),yaw=h:GetAttribute("HoleYaw") or 0} end
end
for _,p in C:GetDescendants() do
 if p:IsA("BasePart") then table.insert(out.parts,record(p)) end
 if p.Name=="Placeholder" and p.Parent and (p.Parent.Name=="loading_dock" or p.Parent.Name=="water_tank") then table.insert(out.placeholders,p:GetFullName()) end
 if p:IsA("Model") and (p.Name=="h08_ground" or p.Name=="h09_water_tank") then
  local cf,size=p:GetBoundingBox()
  table.insert(out.importModels,{path=p:GetFullName(),pivot={p:GetPivot():GetComponents()},boundsCenter=vec(cf.Position),boundsSize=vec(size)})
 end
end
-- Fresh data-built reference exists only during this audit; never opens/saves another place.
local ss=game.ServerStorage
local spec=require(ss.CourseData.SugarloafCanyon:Clone())
local selected=table.clone(spec)
selected.holes={}
for _,h in spec.holes do if h.number==8 or h.number==15 then table.insert(selected.holes,h) end end
assert(not workspace:FindFirstChild("StageAJAuditReference"),"stale audit reference exists")
local ok,err=pcall(function()
 require(ss.CourseBuilder:Clone()).Build(selected,require(ss.CourseData.SugarloafLayout:Clone()),{folder="StageAJAuditReference",courseId="sugarloaf_canyon",palette="sugarloaf"})
 out.geometryEquality={}
 local function key(p) return p.Name.."|"..tostring(p:GetAttribute("PieceId") or p:GetAttribute("WallId") or "") end
 local function same(a,b)
  return key(a)==key(b) and a.ClassName==b.ClassName and (a.Size-b.Size).Magnitude<.0001 and (a.Position-b.Position).Magnitude<.0001
   and a.CFrame.RightVector:Dot(b.CFrame.RightVector)>.999999 and a.CFrame.UpVector:Dot(b.CFrame.UpVector)>.999999
   and a.CanCollide==b.CanCollide and a.CanQuery==b.CanQuery and a.CanTouch==b.CanTouch
   and a.CollisionGroup==b.CollisionGroup and a.CustomPhysicalProperties==b.CustomPhysicalProperties
   and a:GetAttribute("Zone")==b:GetAttribute("Zone") and a:GetAttribute("decel_scale")==b:GetAttribute("decel_scale")
 end
 for _,n in {8,15} do
  local result={hole=n,matched=0,unmatchedBuilt={},unmatchedReference={}}
  for _,folder in {"Geometry","Rails"} do
   local fresh={}
   for _,p in workspace.StageAJAuditReference["Hole"..n][folder]:GetChildren() do
    if p:IsA("BasePart") and (p:GetAttribute("PieceId") or p:GetAttribute("WallId")) then table.insert(fresh,p) end
   end
   for _,p in C["Hole"..n][folder]:GetChildren() do
    if not p:IsA("BasePart") or not(p:GetAttribute("PieceId") or p:GetAttribute("WallId")) then continue end
    local found
    for i,q in fresh do if same(p,q) then found=i;break end end
    if found then table.remove(fresh,found);result.matched+=1 else table.insert(result.unmatchedBuilt,folder.."/"..key(p)) end
   end
   for _,p in fresh do table.insert(result.unmatchedReference,folder.."/"..key(p)) end
  end
  result.pass=#result.unmatchedBuilt==0 and #result.unmatchedReference==0
  local capCount=0
  for _,p in C["Hole"..n]:GetDescendants() do if p.Name=="CapUnderCup" then capCount+=1 end end
  result.capUnderCupCount=capCount
  table.insert(out.geometryEquality,result)
 end
end)
local reference=workspace:FindFirstChild("StageAJAuditReference")
if reference then reference:Destroy() end
assert(ok,err)
_G.StageAJAuditJSON=game:GetService("HttpService"):JSONEncode(out)
return #_G.StageAJAuditJSON
