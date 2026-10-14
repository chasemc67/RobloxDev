"""Rebuild local Aurora, preserving approved batch1/2 visuals and reconnecting mover welds."""
import json
from pathlib import Path
from run_playtests import Studio
from aurora_build import CODE
OUT=Path('playtests/stage-am')
SAVE='''
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"))
local lib=Instance.new("Folder") lib.Name="StageAMRetained" lib.Parent=game.ServerStorage
local count=0
for n=1,18 do
 local hole=workspace.CourseAurora["Hole"..n]
 for _,m in hole:GetDescendants() do
  if m:IsA("Model") and m:GetAttribute("StageAIVisual") then
   m:SetAttribute("RetainedHole",n)
   m:SetAttribute("RetainedMover",m.Parent.Name:sub(1,6)=="Mover_" and m.Parent.Name or nil)
   for _,p in m:GetDescendants() do
    if p:IsA("WeldConstraint") then p:Destroy() elseif p:IsA("BasePart") then p.Anchored=true end
   end
   m.Parent=lib count+=1
  end
 end
end
assert(count==74,"expected 74 existing approved props")
return count
'''
RESTORE='''
local lib=game.ServerStorage.StageAMRetained local count=0
for _,m in lib:GetChildren() do
 local hole=workspace.CourseAurora["Hole"..m:GetAttribute("RetainedHole")]
 local moverName=m:GetAttribute("RetainedMover")
 local mover=moverName and assert(hole.Movers:FindFirstChild(moverName))
 m.Parent=mover or hole.Decor
 for _,p in m:GetDescendants() do
  if p:IsA("BasePart") then
   p.CanCollide=false p.CanQuery=false p.CanTouch=false p:SetAttribute("VisualQueryDisabled",true)
   if mover and mover:GetAttribute("Type")~="toggle" then
    p.Anchored=false p.Massless=true
    local w=Instance.new("WeldConstraint") w.Part0=assert(mover:FindFirstChild("MoverRoot")) w.Part1=p w.Parent=p
   end
  end
 end
 if mover then for _,p in mover:GetDescendants() do
  if p:IsA("BasePart") and not p:IsDescendantOf(m) and (p.Name=="BlockerVisual" or p.Name=="FeltSkin") then p.Transparency=1 end
 end end
 count+=1
end
lib:Destroy()
return count
'''
if __name__=='__main__':
 s=Studio();assert s.mode()[0]=='Edit'
 r={'retained':s.luau(SAVE),'build':s.luau(CODE,timeout=600),'restored':s.luau(RESTORE)}
 (OUT/'rebuild.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
