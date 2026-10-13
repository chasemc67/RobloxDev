assert(game.PlaceId==0 and not game:FindFirstChildOfClass('NetworkClient'),'LOCAL ONLY')
local course=workspace.CourseSugarloaf
local r={placeId=game.PlaceId,role=workspace:GetAttribute('PlaceRole'),holes={},physicalVisuals={},unweldedVisuals={},meshes={}}
local function vec(v) return {v.X,v.Y,v.Z} end
local function dist(p,v)
 local q=p.CFrame:PointToObjectSpace(v) local h=p.Size/2
 return Vector3.new(math.max(math.abs(q.X)-h.X,0),math.max(math.abs(q.Y)-h.Y,0),math.max(math.abs(q.Z)-h.Z,0)).Magnitude
end
for n=7,18 do
 local h=course['Hole'..n] local row={hole=n,props={},withinCup2_2={},sightline={}}
 for _,p in h:GetDescendants() do if p:IsA('BasePart') then
  local af=p:FindFirstAncestor('StageAFVisuals')
  local vis=p:FindFirstAncestorWhichIsA('Model')
  if af then table.insert(row.props,p:GetFullName()) end
  if (af or vis and vis:GetAttribute('StageAEVisual')) then
   if p.CanCollide or p.CanQuery or p.CanTouch then table.insert(r.physicalVisuals,p:GetFullName()) end
   if dist(p,h.Cup.Position)<2.2 then table.insert(row.withinCup2_2,{name=p:GetFullName(),distance=dist(p,h.Cup.Position)}) end
   if vis and vis.Parent.Name:match('^Mover_') then
    local w=p:FindFirstChildOfClass('WeldConstraint')
    if p.Anchored or not w or (w.Part0~=vis.Parent.MoverRoot and w.Part1~=vis.Parent.MoverRoot) then table.insert(r.unweldedVisuals,p:GetFullName()) end
   end
   if p:IsA('MeshPart') then table.insert(r.meshes,{name=p:GetFullName(),MeshId=p.MeshId,MeshContent=tostring(p.MeshContent),sourceType=tostring(p.MeshContent.SourceType),texture=p.TextureID}) end
  end
 end end
 local tee=h:FindFirstChild('Tee')
 if tee then
  local start=tee.Position+Vector3.new(0,5,0)
  local params=RaycastParams.new() params.FilterType=Enum.RaycastFilterType.Exclude params.FilterDescendantsInstances={tee}
  local hit=workspace:Raycast(start,h.Cup.Position+Vector3.new(0,.1,0)-start,params)
  row.sightline={from=vec(start),hit=hit and hit.Instance:GetFullName() or 'clear',newPropHit=hit and hit.Instance:FindFirstAncestor('StageAFVisuals')~=nil or false}
 end
 table.insert(r.holes,row)
end
-- Compare unchanged exact felt/walls against a fresh build from the generated holes.json data.
local ss=game.ServerStorage local data=require(ss.CourseData.SugarloafCanyon:Clone())
local only=table.clone(data) only.holes={}
for n=7,18 do table.insert(only.holes,data.holes[n]) end
require(ss.CourseBuilder:Clone()).Build(only,require(ss.CourseData.SugarloafLayout:Clone()),{folder='StageAFReference',courseId='sugarloaf_canyon',palette='sugarloaf'})
local function signature(h)
 local out={}
 for _,folder in {'Geometry','Rails'} do
  for _,p in h[folder]:GetChildren() do if p:IsA('BasePart') and (p:GetAttribute('PieceId') or p:GetAttribute('WallId')) then
   local a={folder,p.Name,p:GetAttribute('PieceId') or '',p:GetAttribute('WallId') or '',tostring(p.CanCollide)}
   for _,v in {p.CFrame:GetComponents()} do table.insert(a,string.format('%.3f',math.abs(v)<.0005 and 0 or v)) end
   for _,v in vec(p.Size) do table.insert(a,string.format('%.3f',v)) end
   table.insert(out,table.concat(a,'|'))
  end end
 end
 table.sort(out) return out
end
for _,row in r.holes do
 local a=signature(course['Hole'..row.hole]) local b=signature(workspace.StageAFReference['Hole'..row.hole])
 row.geometryCount=#a row.referenceCount=#b row.geometryExact=table.concat(a,'\n')==table.concat(b,'\n')
 if not row.geometryExact then row.actualGeometry=a row.expectedGeometry=b end
end
workspace.StageAFReference:Destroy()
return game.HttpService:JSONEncode(r)
