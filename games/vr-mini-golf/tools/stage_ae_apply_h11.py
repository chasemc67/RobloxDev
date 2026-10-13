"""Apply generated H11 motion settings without rebuilding its geometry or visuals."""
from pathlib import Path
from run_playtests import Studio
code='''
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"),"LOCAL ONLY")
local data=require(game.ServerStorage.CourseData.SugarloafCanyon:Clone())
local math=require(game.ReplicatedStorage.Golf.MoverMath:Clone())
local m=workspace.CourseSugarloaf.Hole11.Movers.Mover_lock_gate
local before={phase=m:GetAttribute("Phase"),dwell=m:GetAttribute("Dwell")}
for _,d in data.holes[11].moving_parts do if d.id=="lock_gate" then
 m:SetAttribute("Phase",d.phase) m:SetAttribute("Dwell",math.encodeDwell(d.dwell))
 m:SetAttribute("Speed",d.speed) m:SetAttribute("Period",d.period_s)
end end
return {before=before,after={phase=m:GetAttribute("Phase"),dwell=m:GetAttribute("Dwell")}}
'''
r=Studio().luau(code);print(r);Path('playtests/stage-ae/h11-config-change.json').write_text(r+'\n')
