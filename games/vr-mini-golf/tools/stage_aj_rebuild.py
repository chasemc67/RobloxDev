"""Replace only changed H8/H15 generated pieces/walls; preserve cup/CapUnderCup."""
import json
from pathlib import Path
from run_playtests import Studio
code=r'''assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"),"LOCAL ONLY")
local ss=game.ServerStorage
local data=require(ss.CourseData.SugarloafCanyon:Clone())
local only=table.clone(data) only.holes={data.holes[8],data.holes[15]}
require(ss.CourseBuilder:Clone()).Build(only,require(ss.CourseData.SugarloafLayout:Clone()),{folder="StageAJReference",courseId="sugarloaf_canyon",palette="sugarloaf"})
local report={}
local function key(p) return (p:GetAttribute("PieceId") and "PieceId:"..p:GetAttribute("PieceId")) or (p:GetAttribute("WallId") and "WallId:"..p:GetAttribute("WallId")) end
local function same(a,b)
 return a.ClassName==b.ClassName and (a.Size-b.Size).Magnitude<0.0001 and (a.Position-b.Position).Magnitude<0.0001 and a.CFrame.RightVector:Dot(b.CFrame.RightVector)>0.999999 and a.CFrame.UpVector:Dot(b.CFrame.UpVector)>0.999999 and a.CanCollide==b.CanCollide and a.CanQuery==b.CanQuery and a.CanTouch==b.CanTouch and a.CollisionGroup==b.CollisionGroup and a.CustomPhysicalProperties==b.CustomPhysicalProperties and a:GetAttribute("Zone")==b:GetAttribute("Zone") and a:GetAttribute("decel_scale")==b:GetAttribute("decel_scale")
end
for _,n in {8,15} do
 local src=workspace.StageAJReference["Hole"..n] local dst=workspace.CourseSugarloaf["Hole"..n]
 local changed={} local removed={} local added={}
 for _,folder in {"Geometry","Rails"} do
  local fresh={}
  for _,p in src[folder]:GetChildren() do if key(p) then table.insert(fresh,p) end end
  for _,p in dst[folder]:GetChildren() do if key(p) then
   local match
   for i,q in fresh do if key(p)==key(q) and p.Name==q.Name and same(p,q) then match=i break end end
   if match then table.remove(fresh,match) else
    changed[key(p)]=true table.insert(removed,{name=p:GetFullName(),id=key(p)}) p:Destroy()
   end
  end end
  for _,p in fresh do changed[key(p)]=true p.Parent=dst[folder] table.insert(added,{name=p:GetFullName(),id=key(p)}) end
 end
 require(ss.WorldBuilder:Clone()).CapUnderCup(dst,nil,6)
 table.insert(report,{hole=n,changed=changed,removed=removed,added=added})
end
workspace.StageAJReference:Destroy()
return game.HttpService:JSONEncode(report)'''
if __name__=='__main__':
 r=Studio().luau(code,timeout=300);print(r)
 json.loads(r)
 Path('playtests/stage-aj/geometry-rebuild.json').write_text(r+'\n')
