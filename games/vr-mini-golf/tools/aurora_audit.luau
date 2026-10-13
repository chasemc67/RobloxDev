-- Read-only Edit audit, run with execute_luau after the local build/playtest.
assert(game.PlaceId == 0, "LOCAL ONLY")
local data=require(game.ServerStorage.CourseData.AuroraArchipelago:Clone())
local config=require(game.ReplicatedStorage.Golf.Config:Clone())
local course=workspace.CourseAurora
local function v(t) return Vector3.new(t[1],t[2],t[3]) end
local report={placeId=game.PlaceId,role=workspace:GetAttribute("PlaceRole"),holes={},visualParts=0,visualCollisionFailures=0}
for _,def in data.holes do
 local h=course:FindFirstChild("Hole"..def.number)
 local cf=CFrame.new(v(def.world_offset))*CFrame.Angles(0,math.rad(def.world_yaw or 0),0)
 local row={hole=def.number,wallCount=0,moverBlockers=0,maxWallPositionError=0,maxWallSizeError=0,maxWallAngleError=0,maxMoverPositionError=0,maxMoverSizeError=0,maxMoverAngleError=0,missingWalls={},missingMovers={}}
 row.cupPositionError=(h.Cup.Position-cf:PointToWorldSpace(v(def.cup.position))).Magnitude
 row.configCupDepth=config.CupDepth
 row.visualCupBottomDepth=h.Cup.Position.Y-h.Geometry.CupBottom.Position.Y
 local rp=RaycastParams.new() rp.FilterType=Enum.RaycastFilterType.Include rp.FilterDescendantsInstances={h.Geometry} rp.RespectCanCollide=true
 local hit=workspace:Raycast(h.Cup.Position+Vector3.new(0,0.02,0),Vector3.new(0,-2,0),rp)
 row.collisionCupBottomDepth=hit and h.Cup.Position.Y-hit.Position.Y or -1
 row.autoResetStill=h:GetAttribute("AutoResetStill")
 for _,w in def.walls do
  local found
  for _,p in h.Geometry:GetChildren() do if p:GetAttribute("WallId")==w.id then found=p break end end
  if not found then table.insert(row.missingWalls,w.id) else
   row.wallCount+=1
   row.maxWallPositionError=math.max(row.maxWallPositionError,(found.Position-(cf*CFrame.new(v(w.center))).Position).Magnitude)
   local _,angle=(found.CFrame.Rotation:Inverse()*(cf*CFrame.Angles(0,math.rad(w.yaw or 0),0)).Rotation):ToAxisAngle()
   row.maxWallAngleError=math.max(row.maxWallAngleError,math.abs(angle))
   row.maxWallSizeError=math.max(row.maxWallSizeError,(found.Size-v(w.size)).Magnitude)
  end
 end
 row.movers={}
 for _,m in def.moving_parts do
  local model=h.Movers:FindFirstChild("Mover_"..m.id)
  if not model then table.insert(row.missingMovers,m.id) else
   local mr={id=m.id,staticReason=model:GetAttribute("StaticReason"),type=model:GetAttribute("Type"),range={model:GetAttribute("RangeMin"),model:GetAttribute("RangeMax")},blockers=0}
   for i,b in m.blockers do
    local found
    for _,p in model:GetChildren() do if p:GetAttribute("BlockerIndex")==i then found=p break end end
    if found then
     local expect=cf*CFrame.new(v(m.pivot))*CFrame.fromAxisAngle(v(m.axis),math.rad(b.roll or 0))*CFrame.new(v(b.center))*CFrame.Angles(0,math.rad(b.yaw or 0),0)
     row.maxMoverPositionError=math.max(row.maxMoverPositionError,(found.Position-expect.Position).Magnitude)
     local _,angle=(found.CFrame.Rotation:Inverse()*expect.Rotation):ToAxisAngle()
     row.maxMoverAngleError=math.max(row.maxMoverAngleError,math.abs(angle))
     row.maxMoverSizeError=math.max(row.maxMoverSizeError,(found.Size-v(b.size)).Magnitude)
     row.moverBlockers+=1 mr.blockers+=1
    else table.insert(row.missingMovers,m.id..":"..i) end
   end
   table.insert(row.movers,mr)
  end
 end
 row.pass=#row.missingWalls==0 and #row.missingMovers==0
  and row.maxWallPositionError<0.001 and row.maxWallSizeError<0.001 and row.maxWallAngleError<0.001
  and row.maxMoverPositionError<0.001 and row.maxMoverSizeError<0.001 and row.maxMoverAngleError<0.001
  and row.cupPositionError<0.001 and math.abs(row.collisionCupBottomDepth-config.CupDepth)<0.002
 table.insert(report.holes,row)
end
for _,p in course.Blockout:GetDescendants() do
 if p:IsA("BasePart") then
  report.visualParts+=1
  if p.CanCollide or p.CanQuery or p.CanTouch then report.visualCollisionFailures+=1 end
 end
end
report.noSugarloaf=workspace:FindFirstChild("CourseSugarloaf")==nil
return game:GetService("HttpService"):JSONEncode(report)
