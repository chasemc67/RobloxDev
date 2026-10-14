-- Injected only during local Play. Uses the existing client controller and server scoring.
-- __PLAN__ is replaced with one JSON plan by stage_am_h17.py.
local H=game:GetService("HttpService")
local RS=game:GetService("RunService")
local player=game.Players.LocalPlayer
local B=require(player.PlayerScripts.GolfClient.BallController)
local api=game.ReplicatedStorage.GolfTestAPI
local plan=H:JSONDecode(__PLAN__)
local hole=workspace.CourseAurora.Hole17
local mover=hole.Movers.Mover_aurora_span
local span=mover.TogglePart.Value
local period=mover:GetAttribute("Period") or 9
local phaseOffset=mover:GetAttribute("Phase") or 0
local function phase() return (workspace:GetServerTimeNow()+phaseOffset)%period end
local function vec(v) return {v.X,v.Y,v.Z} end
local hazard
for _,v in hole:GetDescendants() do
 if v:GetAttribute("HazardId")=="aurora_gap" and typeof(v:GetAttribute("RespawnWorld"))=="Vector3" then hazard=v break end
end
assert(hazard,"Missing authored aurora_gap RespawnWorld")
assert(api:Invoke("place",17,"0,-23")=="ok","Cannot place on south pier")
local ball=B.ball
local start=ball.Position
-- Local H17 -Z direction and exact light-span edges, independent of world translation.
local direction=Vector3.new(0,0,-1)
local near=span.Position.Z+span.Size.Z/2
local far=span.Position.Z-span.Size.Z/2
local deadline=os.clock()+period+2
repeat RS.Heartbeat:Wait() until ((phase()-plan.phase)%period)<0.05 or os.clock()>deadline
assert(os.clock()<=deadline,"Missed requested launch phase")
local row={plan=plan,launch_phase=phase(),start=vec(start),strokes_before=player:GetAttribute("Strokes"),
 oob_before=ball:GetAttribute("LastOOB"),respawn_expected=vec(hazard:GetAttribute("RespawnWorld")),trace={},events={},
 method="Existing client BallController.hit test path; real server stroke/hazard/respawn flow",entered=false,crossed=false,fell=false}
local connections={}
for _,name in {"ForcedRest","AutoReset","Unstuck","OffSurface"} do
 table.insert(connections,B[name].Event:Connect(function(a,b)
  table.insert(row.events,{kind=name,a=tostring(a),b=tostring(b)})
 end))
end
local t0=os.clock()
row.launched=B.hit(direction*plan.speed,"test")
local nextSample=0
while row.launched and os.clock()-t0<22 do
 RS.Heartbeat:Wait()
 local elapsed=os.clock()-t0 local p=ball.Position local v=ball.AssemblyLinearVelocity.Magnitude
 local cycle=phase() local oob=ball:GetAttribute("LastOOB")
 if p.Z<near and not row.entered then row.entered=true row.enter_phase=cycle row.enter_collide=span.CanCollide end
 if p.Z<far-0.2 and p.Y>start.Y-0.3 and not row.crossed then
  row.crossed=true row.cross_phase=cycle row.cross_collide=span.CanCollide row.cross_position=vec(p)
 end
 if p.Y<start.Y-0.5 then row.fell=true end
 if elapsed>=nextSample then
  table.insert(row.trace,{t=elapsed,phase=cycle,p=vec(p),speed=v,state=B.state,collide=span.CanCollide,
   query=span.CanQuery,touch=span.CanTouch,strokes=player:GetAttribute("Strokes"),oob=oob})
  nextSample=elapsed+0.05
 end
 if oob and oob~=row.oob_before and not row.hazard_time then
  row.hazard_time=elapsed row.hazard_oob=oob row.strokes_after_hazard=player:GetAttribute("Strokes")
 end
 if elapsed>0.3 and B.state=="ready" then
  if row.hazard_time or row.crossed or elapsed>3 then row.outcome="rest" break end
 end
end
for _,c in connections do c:Disconnect() end
-- Allow the authoritative stroke attribute to finish replicating.
task.wait(0.25)
row.elapsed=os.clock()-t0 row.state=B.state row.finish=vec(ball.Position)
row.strokes_after=player:GetAttribute("Strokes") row.speed_after=ball.AssemblyLinearVelocity.Magnitude
row.last_oob=ball:GetAttribute("LastOOB")
local expected=hazard:GetAttribute("RespawnWorld")
row.respawn_horizontal_error=Vector3.new(ball.Position.X-expected.X,0,ball.Position.Z-expected.Z).Magnitude
row.respawn_vertical_error=math.abs(ball.Position.Y-expected.Y)
if plan.kind=="timed" then
 row.pass=row.launched and row.crossed and row.enter_collide and row.cross_collide and not row.fell
  and row.enter_phase>=0.6 and row.enter_phase<6.6 and row.cross_phase>=0.6 and row.cross_phase<6.6
  and row.strokes_after-row.strokes_before==1
else
 row.pass=row.launched and row.fell and not row.crossed and row.hazard_oob~=nil
  and string.find(row.hazard_oob,"hazard:aurora_gap",1,true)~=nil
  and row.strokes_after-row.strokes_before==2 and B.state=="ready" and row.speed_after<0.2
  and row.respawn_horizontal_error<0.1 and row.respawn_vertical_error<0.2
end
return H:JSONEncode(row)
