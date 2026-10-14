"""Reapply source effects and visual flags after verification; local Edit only."""
import json
from pathlib import Path
from run_playtests import Studio
s=Studio();assert s.mode()[0]=='Edit'
r=s.luau('''
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"))
local c=workspace.CourseAurora local parts=0
for _,m in c:GetDescendants() do
 if m:IsA("Model") and m:GetAttribute("StageAIVisual") then
  for _,p in m:GetDescendants() do if p:IsA("BasePart") then
   p.CanCollide=false p.CanQuery=false p.CanTouch=false p:SetAttribute("VisualQueryDisabled",true) parts+=1
  end end
 end
end
local effects=require(game.ServerStorage.AuroraEffects:Clone()).Apply(c,require(game.ServerStorage.CourseData.AuroraArchipelago:Clone()))
return game.HttpService:JSONEncode({parts=parts,effects=effects})
''')
Path('playtests/stage-am/final-apply.json').write_text(r+'\n');print(r)
