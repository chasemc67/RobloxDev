"""Replace only changed H8 felt/base/wall pieces from the supplied spec."""
import json
from pathlib import Path
from holes_to_lua import REPO, to_lua
from run_playtests import Studio
root=Path(REPO)/'assets/vr-mini-golf/sugarloaf-canyon'
old=json.loads((root/'holes.pre-ae.json').read_text())['holes'][7]
new=json.loads((root/'holes.json').read_text())['holes'][7]
changed={}
for key,attr in [('felt','PieceId'),('walls','WallId')]:
 a={x['id']:x for x in old[key]};b={x['id']:x for x in new[key]}
 changed[attr]={k:True for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
code='local changed='+to_lua(changed)+'''
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"),"LOCAL ONLY")
local ss=game.ServerStorage
local data=require(ss.CourseData.SugarloafCanyon:Clone())
local only=table.clone(data) only.holes={data.holes[8]}
local cb=require(ss.CourseBuilder:Clone())
cb.Build(only,require(ss.CourseData.SugarloafLayout:Clone()),{folder="StageAEH8",courseId="sugarloaf_canyon",palette="sugarloaf"})
local src=workspace.StageAEH8.Hole8 local dst=workspace.CourseSugarloaf.Hole8
local function affected(p)
 for attr,ids in changed do if ids[p:GetAttribute(attr)] then return true end end
 return false
end
local removed,added=0,0
for _,name in {"Geometry","Rails"} do
 for _,p in dst[name]:GetChildren() do if affected(p) then p:Destroy() removed+=1 end end
 for _,p in src[name]:GetChildren() do if affected(p) then p.Parent=dst[name] added+=1 end end
end
workspace.StageAEH8:Destroy()
require(ss.WorldBuilder:Clone()).CapUnderCup(dst,nil,6)
task.wait()
return {removed=removed,added=added,changed=changed,cup=dst.Cup.Position}
'''
r=Studio().luau(code,timeout=300)
print(r)
Path('playtests/stage-ae/h8-rebuild.json').write_text(r+'\n')
