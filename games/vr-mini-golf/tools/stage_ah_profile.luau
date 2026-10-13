-- spec is injected by stage_ah_profile.py. Read-only, Edit mode; no instances created.
assert(game.PlaceId == 0 and not game:FindFirstChildOfClass("NetworkClient"))
local h = workspace.CourseAurora["Hole"..spec.number]
local origin = Vector3.new(unpack(spec.world_offset))
local cf = CFrame.new(origin) * CFrame.Angles(0,math.rad(spec.world_yaw or 0),0)
assert((h:GetAttribute("HoleOrigin")-origin).Magnitude < 0.0001)
local function vec(v) return {v.X,v.Y,v.Z} end
local parts, metadata, byPiece = {}, {}, {}
for _,p in h:GetDescendants() do
 if p:IsA("BasePart") and p:HasTag("GolfSurface") and p.CanCollide then
  table.insert(parts,p)
  local id=p:GetAttribute("PieceId")
  byPiece[id]=byPiece[id] or {} table.insert(byPiece[id],p)
  table.insert(metadata,{id=id,name=p.Name,class=p.ClassName,size=vec(p.Size),
    localCF={cf:ToObjectSpace(p.CFrame):GetComponents()},normal=vec(cf:VectorToObjectSpace(p.CFrame.UpVector)),
    collide=p.CanCollide,query=p.CanQuery,decel_scale=p:GetAttribute("decel_scale") or 1,
    cupCut=p:GetAttribute("CupCut") or false})
 end
end
local function params(list)
 local q=RaycastParams.new() q.FilterType=Enum.RaycastFilterType.Include
 q.FilterDescendantsInstances=list q.RespectCanCollide=true return q
end
local all=params(parts)
local function cast(x,z,q)
 local hit=workspace:Raycast(cf:PointToWorldSpace(Vector3.new(x,10,z)),Vector3.new(0,-30,0),q or all)
 if not hit then return false end
 return {cf:PointToObjectSpace(hit.Position).Y,hit.Instance:GetAttribute("PieceId"),
   vec(cf:VectorToObjectSpace(hit.Normal)),hit.Instance.ClassName}
end
local function grid(x0,x1,z0,z1,step)
 local rows={} local count=0
 for iz=0,math.floor((z1-z0)/step+0.5) do
  for ix=0,math.floor((x1-x0)/step+0.5) do
   local x,z=x0+ix*step,z0+iz*step
   table.insert(rows,{x,z,cast(x,z)}) count+=1
   if count%500==0 then task.wait() end
  end
 end return rows
end
local grids, seams = {}, {}
if spec.number==18 then
 grids.collection_and_foot=grid(-17.4,-9.6,-30,-22,0.1)
 grids.ramp_full=grid(-13.6,-13.4,-38.5,-27.5,0.1)
 -- One-sided joint probes at 0.001 and 0.01 stud; both component planes as well as the visible top.
 for ix=0,78 do
  local x=-17.4+ix*0.1
  for _,d in {-0.1,-0.01,-0.001,0,0.001,0.01,0.1} do
   table.insert(seams,{x=x,z=-28+d,all=cast(x,-28+d),
     ramp=cast(x,-28+d,params(byPiece.ramp)),plaza=cast(x,-28+d,params(byPiece.plaza_w))})
  end
  if ix%10==0 then task.wait() end
 end
else
 grids.cup_joint=grid(-2,2,-56,-52,0.1)
 grids.pool_north=grid(8.3,14.7,-47.5,-45.5,0.1)
 for _,axis in {"x","z"} do
  for _,side in {-1,1} do
   for j=-5,5 do
    for _,d in {-0.01,-0.001,0,0.001,0.01} do
     local x=axis=="x" and side*0.6+d or j*0.1
     local z=-54+(axis=="z" and side*0.6+d or j*0.1)
     table.insert(seams,{x=x,z=z,axis=axis,side=side,all=cast(x,z),
       pad=cast(x,z,params(byPiece.cup_pad)),shelf=cast(x,z,params(byPiece.shelf))})
    end
   end
  end
 end
end
local hazards={}
for _,p in h.Hazards:GetChildren() do
 if p:IsA("BasePart") and p:GetAttribute("HazardId") then
  local corners={}
  for _,x in {-1,1} do for _,z in {-1,1} do
   table.insert(corners,vec(cf:PointToObjectSpace(p.CFrame:PointToWorldSpace(Vector3.new(x*p.Size.X/2,0,z*p.Size.Z/2)))))
  end end
  table.insert(hazards,{id=p:GetAttribute("HazardId"),localCenter=vec(cf:PointToObjectSpace(p.Position)),
    size=vec(p.Size),localCorners=corners,surfaceY=p:GetAttribute("SurfaceY")-origin.Y,
    localRespawn=vec(cf:PointToObjectSpace(p:GetAttribute("RespawnWorld"))),
    collide=p.CanCollide,query=p.CanQuery,penalty=p:GetAttribute("Penalty")})
 end
end
_G.StageAHProfileJSON = game:GetService("HttpService"):JSONEncode({hole=spec.number,spacing=0.1,
  columns={"local_x","local_z","hit_or_false"},hitColumns={"local_y","piece_id","normal","class"},
  parts=metadata,grids=grids,seams=seams,hazards=hazards})
return #_G.StageAHProfileJSON
