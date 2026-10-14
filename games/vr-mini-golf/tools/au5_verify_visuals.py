import json
from pathlib import Path
from run_playtests import Studio
s=Studio();assert s.mode()[0]=='Edit'
code='''
local c=workspace.CourseAurora local r={blockoutParts=0,blockoutVisible=0,baseVisuals={},sign={},props={},thin={}}
for _,p in c.Blockout:GetDescendants() do if p:IsA('BasePart') then
 r.blockoutParts+=1;if p.Transparency<1 then r.blockoutVisible+=1 end
 assert(not p.CanCollide and not p.CanQuery and not p.CanTouch)
end end
for _,p in c:GetDescendants() do
 if p:IsA('BasePart') and p.Transparency<1 and math.min(p.Size.X,p.Size.Y,p.Size.Z)<.19999 then table.insert(r.thin,p:GetFullName()) end
 if p:IsA('Model') and p:GetAttribute('AU5OverlapProps') then
  local n=0 for _,q in p:GetDescendants() do if q:IsA('BasePart') then n+=1;assert(not q.CanCollide and not q.CanQuery and not q.CanTouch) end end
  table.insert(r.props,{path=p:GetFullName(),parts=n})
 end
end
local stone=c.Hole6:FindFirstChild('h06_respawn_stone',true):FindFirstChildWhichIsA('BasePart',true)
local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Include;local colliders={}
for _,p in c.Hole6:GetDescendants() do if p:IsA('BasePart') and p.CanCollide then table.insert(colliders,p) end end
params.FilterDescendantsInstances=colliders
local gap=math.huge
for _,x in {-1,1} do for _,z in {-1,1} do
 local v=stone.CFrame:PointToWorldSpace(Vector3.new(x*stone.Size.X/2,-stone.Size.Y/2,z*stone.Size.Z/2))
 local hit=assert(workspace:Raycast(v+Vector3.new(0,10,0),Vector3.new(0,-20,0),params))
 gap=math.min(gap,v.Y-hit.Position.Y)
end end
r.stone={minimumGap=gap,size={stone.Size.X,stone.Size.Y,stone.Size.Z},position={stone.Position.X,stone.Position.Y,stone.Position.Z}}
assert(gap>=.079)
local col=c.Hole5:FindFirstChild('h05_geyser_column__Basalt',true)
for _,p in c.Hole5.Geometry:GetChildren() do if p.Name:find('AU5BaseVisual',1,true) then
 local minimumGap=math.huge
 for _,col in c.Hole5:FindFirstChild('h05_geyser_column',true):GetDescendants() do if col:IsA('BasePart') and col.Transparency<1 then
 local q=col.CFrame:ToObjectSpace(p.CFrame)
 local hx=math.abs(q.RightVector.X)*p.Size.X/2+math.abs(q.UpVector.X)*p.Size.Y/2+math.abs(q.ZVector.X)*p.Size.Z/2
 local hz=math.abs(q.RightVector.Z)*p.Size.X/2+math.abs(q.UpVector.Z)*p.Size.Y/2+math.abs(q.ZVector.Z)*p.Size.Z/2
 local g=math.max(math.abs(q.X)-hx-col.Size.X/2,math.abs(q.Z)-hz-col.Size.Z/2)
 minimumGap=math.min(minimumGap,g);assert(g>=.079,'base gap '..g..' against '..col.Name)
 end end
 table.insert(r.baseVisuals,{path=p:GetFullName(),gap=minimumGap})
end end
local sign=c.Hole14:FindFirstChild('h14_safe_side_sign',true)
local post=sign.h14_safe_side_sign__Timber local face=sign.h14_safe_side_sign__AuroraTeal
r.sign.facePostGap=math.abs((face.Position-post.Position):Dot(face.CFrame.ZVector))-(face.Size.Z+post.Size.Z)/2
local prev=face
for _,p in {sign.h14_safe_side_sign__Brass,sign.h14_safe_side_sign__Glow,sign.h14_safe_side_sign__Snow} do
 local g=p.Position.Y-p.Size.Y/2-(prev.Position.Y+prev.Size.Y/2)
 r.sign[p.Name]=g;assert(g>=.079);prev=p
end
assert(r.sign.facePostGap>=.079 and #r.props==12 and #r.thin==0)
return game.HttpService:JSONEncode(r)
'''
raw=s.luau(code);
if not raw.startswith('{'): raise RuntimeError(raw)
r=json.loads(raw);Path('playtests/stage-au5/visual-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
