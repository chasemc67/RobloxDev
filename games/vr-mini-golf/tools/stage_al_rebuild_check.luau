-- Temporary reference folder in the one LOCAL place; no second place or save.
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"))
local ss=game.ServerStorage local course=workspace.CourseSugarloaf
local before={} for _,p in course:GetDescendants() do if p:IsA("BasePart") then before[p]={p.CFrame,p.Size,p.CanCollide} end end
local report={}
local override=require(ss.SugarloafOverrides:Clone())
report.repeatApply=override.Apply(course)
report.repeatPoseChanges={}
for p,v in before do if p.Parent and (p.CFrame~=v[1] or p.Size~=v[2] or p.CanCollide~=v[3]) then table.insert(report.repeatPoseChanges,p:GetFullName()) end end
assert(#report.repeatPoseChanges==0,"visual override drift")
local spec=require(ss.CourseData.SugarloafCanyon:Clone())
local subset=table.clone(spec) subset.holes={spec.holes[9],spec.holes[14],spec.holes[15]}
local refName="StageALReference"
assert(not workspace:FindFirstChild(refName))
local ok,err=pcall(function()
 require(ss.CourseBuilder:Clone()).Build(subset,require(ss.CourseData.SugarloafLayout:Clone()),{folder=refName,courseId="sugarloaf_canyon",palette="sugarloaf"})
 local ref=workspace[refName]
 report.rebuiltH15={}
 for _,p in ref.Hole15.Geometry:GetDescendants() do if p:IsA("BasePart") and p:GetAttribute("WallId") then
  local props=p.CurrentPhysicalProperties
  table.insert(report.rebuiltH15,{wall=p:GetAttribute("WallId"),friction=props.Friction,weight=props.FrictionWeight,test=p:GetAttribute("StageAlFrictionTest")})
  assert(math.abs(props.Friction-.1)<1e-6 and props.FrictionWeight==100,"friction did not survive rebuild")
 end end
 report.rebuiltDockParts=0
 for _,p in ref.Hole14.StageAJVisuals.h14_loading_dock:GetDescendants() do if p:IsA("BasePart") then
  assert(not p.CanCollide and not p.CanQuery and not p.CanTouch and p:GetAttribute("VisualQueryDisabled")) report.rebuiltDockParts+=1
 end end
 assert(not ref.Hole9.Decor.pump_house:FindFirstChild("Placeholder"))
 assert(not ref.Hole14.Decor.ore_piles:FindFirstChild("Placeholder"))
 report.rebuiltCoplanar=#require(ss.SugarloafRailTops:Clone()).Scan(ref)
 assert(report.rebuiltCoplanar==0)
 report.rebuiltRail15={}
 for _,p in ref.Hole15.Rails:GetChildren() do if p:IsA("BasePart") then
  local built=course.Hole15.Rails:FindFirstChild(p.Name)
  if built then assert((built.Position-p.Position).Magnitude<.0001 and (built.Size-p.Size).Magnitude<.0001,"rail rebuild mismatch "..p.Name) end
 end end
end)
if workspace:FindFirstChild(refName) then workspace[refName]:Destroy() end
report.referenceSuccess=ok report.referenceError=err
assert(ok,err)
return game.HttpService:JSONEncode(report)
