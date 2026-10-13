"""Hide superseded blockout render skins; preserve every geometry collider and felt."""
import json
from pathlib import Path
from run_playtests import Studio
CODE='''
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"))
local course=workspace.CourseAurora
local all={[9]="h09_reef_wall_skins",[10]="h10_snow_wall_skins",[11]="h11_snowbank_skins",[16]="h16_moonstone_coping"}
local some={[1]={boulder=true},[3]={bridge_rail6=true,bridge_rail7=true},[8]={coral1=true,coral2=true,coral3=true,coral4=true,coral5=true,coral6=true,coral7=true},[17]={pier_s_rail6=true,pier_s_rail7=true,pier_n_rail8=true,pier_n_rail9=true,bridge_rail10=true,bridge_rail11=true}}
local out={}
for n=1,18 do
 local h=course["Hole"..n]
 if all[n] then assert(h.Decor:FindFirstChild(all[n]),"missing replacement skin") end
 local touched=false
 for _,p in h.Rails:GetDescendants() do
  if p:IsA("BasePart") then
   local id=p:GetAttribute("WallId")
   if all[n] or (some[n] and some[n][id]) or (n==13 and id and id:sub(1,11)=="hub_plinth_") then
    assert(not p.CanCollide and not p.CanQuery and not p.CanTouch)
    p.Transparency=1 p:SetAttribute("StageAIReplaced",true) touched=true table.insert(out,p:GetFullName())
   end
  end
 end
 if touched then
  local b=course.Blockout:FindFirstChild(string.format("h%02d_rail",n))
  if b then assert(not b.CanCollide) b.Transparency=1 b:SetAttribute("StageAIReplaced",true) table.insert(out,b:GetFullName()) end
 end
end
local toggle=course.Hole17.Movers.Mover_aurora_span
assert(toggle:FindFirstChild("h17_aurora_span"))
for _,ref in toggle:GetChildren() do
 if ref:IsA("ObjectValue") and ref.Name=="TogglePart" and ref.Value then
  ref.Value.Transparency=1 ref.Value:SetAttribute("StageAIRenderCovered",true) table.insert(out,ref.Value:GetFullName())
 end
end
return game.HttpService:JSONEncode(out)
'''
if __name__=='__main__':
 s=Studio();assert s.mode()[0]=='Edit';r=json.loads(s.luau(CODE));Path('playtests/stage-ai/hidden-render-skins.json').write_text(json.dumps(r,indent=2)+'\n');print('hidden',len(r))
