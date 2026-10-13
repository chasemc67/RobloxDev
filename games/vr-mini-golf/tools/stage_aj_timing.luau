local root=game.ServerStorage.QA_SC
local Config=require(game.ReplicatedStorage.Golf.Config)
local holeNumber=root:GetAttribute("Hole") or 8
local approach=root:GetAttribute("Approach")==true
local H=game:GetService("HttpService") local CS=game:GetService("CollectionService") local RS=game:GetService("RunService")
local function vec(p) return {p.X,p.Y,p.Z} end
local function flat(p) return Vector3.new(p.X,0,p.Z) end
local hole=workspace.CourseSugarloaf["Hole"..holeNumber]
local rp=RaycastParams.new() rp.FilterType=Enum.RaycastFilterType.Include rp.FilterDescendantsInstances={hole} rp.RespectCanCollide=true rp.CollisionGroup="GolfBall"
local function ground(x,z)
 if holeNumber==8 then return workspace:Raycast(Vector3.new(x,80,z),Vector3.new(0,-20,0),rp) end
 return workspace:Raycast(Vector3.new(x,hole.Tee.Position.Y+30,z),Vector3.new(0,-90,0),rp)
end
local plans={}
local seed=holeNumber==8 and 2026101208 or (approach and 2026101316 or 2026101315)
if holeNumber==8 then
local rng=Random.new(2026101208)
local bd=hole.Bounds
for i=1,80 do
 local p=hole.Tee.Position
 if i>40 then
  for attempt=1,1000 do
   local q=bd.CFrame:PointToWorldSpace(Vector3.new(rng:NextNumber(-0.48,0.48)*bd.Size.X,0,rng:NextNumber(-0.48,0.48)*bd.Size.Z))
   local hit=ground(q.X,q.Z)
   if hit and CS:HasTag(hit.Instance,"GolfSurface") and flat(hit.Position-hole.Cup.Position).Magnitude>0.8 then p=hit.Position break end
  end
 end
 local hit=ground(p.X,p.Z) p=hit.Position+Vector3.new(0,0.081,0)
 local dir=flat(hole.Cup.Position-p).Unit
 dir=CFrame.Angles(0,math.rad(rng:NextNumber(-100,100)),0):VectorToWorldSpace(dir)
 local speed=rng:NextNumber(i%5==0 and 0.5 or 2,i%5==0 and 3 or 19.78)
 plans[i]={index=i,start=vec(p),velocity=vec(dir*speed),kind=i<=40 and "tee" or "felt"}
end

else
 local rng=Random.new(seed)
 local rail
 for _,p in hole.Geometry:GetDescendants() do if p:IsA("BasePart") and p:GetAttribute("WallId")=="dune_rail2" then rail=p break end end
 assert(rail,"missing dune_rail2")
 local lean
 if approach then
  for _,p in hole.Geometry:GetDescendants() do if p:IsA("BasePart") and p:GetAttribute("WallId")=="dune_lean3" then lean=p break end end
  assert(lean,"missing dune_lean3")
 end
 local longX=rail.Size.X>rail.Size.Z
 for i=1,80 do
  local chosen,aim
  for attempt=1,200 do
   if approach then
    local railSide=lean.CFrame:PointToObjectSpace(rail.Position).X>=0 and 1 or -1
    local along=rng:NextNumber(-0.42,0.42)*lean.Size.Z
    local q=lean.CFrame:PointToWorldSpace(Vector3.new(-railSide*(lean.Size.X/2+rng:NextNumber(0.5,4)),0,along))
    local hit=ground(q.X,q.Z)
    if hit and CS:HasTag(hit.Instance,"GolfSurface") and hit.Instance:GetAttribute("PieceId")=="dune" then
     chosen=hit.Position+Vector3.new(0,Config.BallRadius+0.001,0)
     local inRail=rail.CFrame:PointToObjectSpace(chosen)
     aim=rail.CFrame:PointToWorldSpace(longX and Vector3.new(math.clamp(inRail.X,-rail.Size.X*.45,rail.Size.X*.45),0,0) or Vector3.new(0,0,math.clamp(inRail.Z,-rail.Size.Z*.45,rail.Size.Z*.45)))
    end
   else
   local along=rng:NextNumber(-0.44,0.44)*(longX and rail.Size.X or rail.Size.Z)
   local inset=rng:NextNumber(0.18,1.4)+(longX and rail.Size.Z or rail.Size.X)/2
   for _,sign in {1,-1} do
    local q=rail.CFrame:PointToWorldSpace(longX and Vector3.new(along,0,sign*inset) or Vector3.new(sign*inset,0,along))
    local hit=ground(q.X,q.Z)
    if hit and CS:HasTag(hit.Instance,"GolfSurface") and hit.Instance:GetAttribute("PieceId")=="dune" then
     chosen=hit.Position+Vector3.new(0,Config.BallRadius+0.001,0)
     aim=rail.CFrame:PointToWorldSpace(longX and Vector3.new(along,0,0) or Vector3.new(0,0,along))
     break
    end
   end
   end
   if chosen then break end
  end
  assert(chosen,"could not place seam plan "..i)
  local dir=flat(aim-chosen).Unit
  dir=CFrame.Angles(0,math.rad(rng:NextNumber(approach and -20 or -50,approach and 20 or 50)),0):VectorToWorldSpace(dir)
  plans[i]={index=i,start=vec(chosen),velocity=vec(dir*rng:NextNumber(approach and 2 or 0.5,approach and 12 or 5)),kind=approach and "dune_lean3_approach" or "dune_rail2_seam"}
 end
end
if root:FindFirstChild("Replay") then plans=H:JSONDecode(root.Replay.Value) end
local out=Instance.new("StringValue") out.Name="Results" out.Parent=root
local result={seed=seed,hole=holeNumber,approach=approach,ball_ball_collidable=game:GetService("PhysicsService"):CollisionGroupsAreCollidable("GolfBall","GolfBall"),stop_definition="last sample speed > Config.StopSpeed to native ready/rest",plans=plans,shots={},errors={},done=0,total=80,method="Current-build BallController physics cloned server-side; only ownership, hole routing, placement and remote reporting adapted. 4 independent noncolliding balls."}
local function save() out.Value=H:JSONEncode(result) end
game:GetService("ScriptContext").Error:Connect(function(msg,stack,src) if #result.errors<30 then table.insert(result.errors,{message=msg,stack=stack,source=src and src:GetFullName()}) end end)
for worker=1,4 do task.spawn(function()
 local m=root.ControllerTemplate:Clone() m.Name="Controller"..worker m:SetAttribute("Hole",holeNumber) m.Parent=root
 local B=require(m)
 local ball=game.ReplicatedStorage.Golf.BallTemplate:Clone() ball.Name="QA_SC_Ball"..worker ball.Anchored=true ball.CollisionGroup="GolfBall" ball.Parent=workspace.Balls B.init(ball)
 local active
 local function event(kind,p,r) if active then table.insert(active.events,{kind=kind,pos=typeof(p)=="Vector3" and vec(p) or nil,detail=tostring(r or p)}) end end
 B.ForcedRest.Event:Connect(function(p,r) event("forced_rest",p,r) end)
 B.AutoReset.Event:Connect(function(p,r) event("auto_reset",p,r) end)
 B.Unstuck.Event:Connect(function(r,p) event("unstuck",p,r) end)
 B.OffSurface.Event:Connect(function(p,r) event("off_surface",p,r) end)
 for i=worker,#plans,4 do
 local ok,err=xpcall(function()
 local plan=plans[i] local pos=Vector3.new(unpack(plan.start)) local hit=ground(pos.X,pos.Z)
 if hit and CS:HasTag(hit.Instance,"GolfSurface") then pos=hit.Position+Vector3.new(0,0.081,0) end
 B.qaPlace(pos) task.wait(0.2) B.setState("ready")
 local row={index=i,kind=plan.kind,start=vec(ball.Position),velocity=plan.velocity,events={},trace={}}
 active=row
 local t=os.clock() local sim=0 local belowSince=nil local first=nil local nextTrace=0 local lastAbove=0
 row.launched=B.hit(Vector3.new(unpack(plan.velocity)),"test")
 while row.launched do
 local dt=RS.Heartbeat:Wait() sim+=dt local elapsed=os.clock()-t
 local p=ball.Position local v=ball.AssemblyLinearVelocity.Magnitude
 if elapsed>=nextTrace then table.insert(row.trace,{t=elapsed,p=vec(p),v=v,state=B.state}); nextTrace=elapsed+0.2 end
 row.finish=vec(p)
 if v>Config.StopSpeed then lastAbove=elapsed end
 if v<Config.StopSpeed then
  if not first then first=elapsed row.first_below_pos=vec(p) end
  belowSince=belowSince or elapsed
 else belowSince=nil end
 if B.state=="ready" then row.outcome="stopped" row.rest_seconds=elapsed row.stop_seconds=elapsed-lastAbove row.last_above_seconds=lastAbove row.tail_seconds=first and elapsed-first row.sim_seconds=sim break end
 if flat(p-hole.Cup.Position).Magnitude<(hole.Cup:GetAttribute("Radius") or 0.21) and p.Y<hole.Cup.Position.Y-0.08 then row.outcome="cup" break end
 if m:GetAttribute("ResetRequested") then row.outcome="reset_requested" break end
 if p.Y<hole.Cup.Position.Y-15 then row.outcome="escape" break end
 if elapsed>25 then row.outcome="timeout" break end
 end
 row.elapsed=os.clock()-t row.first_below_seconds=first
 local hit=workspace:Raycast(ball.Position+Vector3.new(0,0.1,0),Vector3.new(0,-1,0),rp)
 row.ground=hit and hit.Instance:GetFullName() row.groundZone=hit and hit.Instance:GetAttribute("Zone")
 active=nil ball.Anchored=true local tr=Instance.new("StringValue") tr.Name="Trace"..i tr.Value=H:JSONEncode(row.trace) tr.Parent=root row.trace=nil table.insert(result.shots,row) save()
 end,debug.traceback)
 if not ok then table.insert(result.errors,{worker=worker,index=i,error=err}) save() end
 end
 B.connection:Disconnect() ball:Destroy() m:Destroy() result.done+=1 save()
end) end
save() return "started 80 shots / 4 workers (native ready timing)"