"""Rebuild H11 gate from generated holes.json data, preserving imported visual welds."""
from pathlib import Path
from run_playtests import Studio
code='''
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"),"LOCAL ONLY")
local ss=game.ServerStorage
local data=require(ss.CourseData.SugarloafCanyon:Clone())
local only=table.clone(data) only.holes={data.holes[11]}
require(ss.CourseBuilder:Clone()).Build(only,require(ss.CourseData.SugarloafLayout:Clone()),{folder="StageAFH11",courseId="sugarloaf_canyon",palette="sugarloaf"})
local dst=workspace.CourseSugarloaf.Hole11.Movers
local old=dst.Mover_lock_gate
local fresh=workspace.StageAFH11.Hole11.Movers.Mover_lock_gate
local before={phase=old:GetAttribute("Phase"),dwell=old:GetAttribute("Dwell")}
local moved=0
for _,m in old:GetChildren() do if m:IsA("Model") and m:GetAttribute("StageAEVisual") then
 for _,p in m:GetDescendants() do
  if p:IsA("WeldConstraint") then
   if p.Part0==old.MoverRoot then p.Part0=fresh.MoverRoot end
   if p.Part1==old.MoverRoot then p.Part1=fresh.MoverRoot end
  end
 end
 m.Parent=fresh moved+=1
end end
assert(moved>0,"Expected ae gate visual")
for _,p in fresh:GetDescendants() do if p.Name=="BlockerVisual" and p:IsA("BasePart") then p.Transparency=1 end end
fresh.Parent=dst old:Destroy() workspace.StageAFH11:Destroy()
return game.HttpService:JSONEncode({before=before,after={phase=fresh:GetAttribute("Phase"),dwell=fresh:GetAttribute("Dwell")},visualModelsPreserved=moved})
'''
r=Studio().luau(code,timeout=300);print(r)
Path('playtests/stage-af/h11-rebuild.json').write_text(r+'\n')
