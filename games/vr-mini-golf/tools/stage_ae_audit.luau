assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"),"LOCAL ONLY")
local ss=game.ServerStorage local data=require(ss.CourseData.SugarloafCanyon:Clone())
local course=workspace.CourseSugarloaf local h=course.Hole8
local cf=CFrame.new(h:GetAttribute("HoleOrigin"))*CFrame.Angles(0,math.rad(h:GetAttribute("HoleYaw")),0)
local r={placeId=game.PlaceId,role=workspace:GetAttribute("PlaceRole"),felt={},walls={},visualParts=0,physicalVisuals={},unweldedVisuals={},meshIds={}}
for _,f in data.holes[8].felt do
 local found={}
 for _,p in h.Geometry:GetChildren() do if p:GetAttribute("PieceId")==f.id and p.Name=="Felt" then table.insert(found,p) end end
 local row={id=f.id,count=#found}
 if #found==1 then
  local p=found[1] local top=p.CFrame*Vector3.new(0,p.Size.Y/2,0)
  row.topError=(top-cf*Vector3.new(unpack(f.center))).Magnitude
  row.projectedX=p.Size.X
  row.projectedZ=p.Size.Z*p.CFrame.UpVector.Y
  row.collides=p.CanCollide
  row.pass=row.topError<.001 and p.CanCollide
 else row.cupSplit=f.id=="green" row.pass=f.id=="green" end
 table.insert(r.felt,row)
end
for _,w in data.holes[8].walls do
 local found
 for _,p in h.Geometry:GetChildren() do if p:GetAttribute("WallId")==w.id then found=p break end end
 table.insert(r.walls,{id=w.id,positionError=found and (found.Position-cf*Vector3.new(unpack(w.center))).Magnitude or -1,
 sizeError=found and (found.Size-Vector3.new(unpack(w.size))).Magnitude or -1})
end
for _,model in course:GetDescendants() do if model:GetAttribute("StageAEVisual") then
 for _,p in model:GetDescendants() do if p:IsA("BasePart") then
  r.visualParts+=1
  if p.CanCollide or p.CanQuery or p.CanTouch then table.insert(r.physicalVisuals,p:GetFullName()) end
  if model.Parent.Name:find("Mover_") and (p.Anchored or not p:FindFirstChildOfClass("WeldConstraint")) then table.insert(r.unweldedVisuals,p:GetFullName()) end
  if p:IsA("MeshPart") then r.meshIds[p.MeshId]=true end
 end end
end end
local params=RaycastParams.new() params.FilterType=Enum.RaycastFilterType.Include params.FilterDescendantsInstances={workspace.Terrain}
local hit=workspace:Raycast(h.Cup.Position+Vector3.new(0,2,0),Vector3.new(0,-12,0),params)
r.h8TerrainDepth=hit and h.Cup.Position.Y-hit.Position.Y or 12
return game.HttpService:JSONEncode(r)
