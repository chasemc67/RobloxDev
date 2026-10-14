"""Capture actual Studio mesh/primitive bounds in hole coordinates for clearance audit."""
import json
from pathlib import Path
from run_playtests import Studio
OUT=Path(__file__).resolve().parents[1]/'playtests/stage-am'
CODE='''
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"))
local cs=game:GetService("CollectionService")
local function isVisual(m)
 return m:GetAttribute("StageAIVisual") or m:GetAttribute("StageAMVisual") or m:GetAttribute("AuroraVisual") or cs:HasTag(m,"StageAIVisual") or cs:HasTag(m,"StageAMVisual") or cs:HasTag(m,"AuroraVisual")
end
local function vec(v) return {v.X,v.Y,v.Z} end
local out={holes={},visualFlags={},weldErrors={},surfaceFields={}}
for n=1,18 do
 local h=workspace.CourseAurora["Hole"..n]
 local cf=CFrame.new(h:GetAttribute("HoleOrigin"))*CFrame.Angles(0,math.rad(h:GetAttribute("HoleYaw")),0)
 local function record(p)
  local pts={}
  for _,x in {-1,1} do for _,y in {-1,1} do for _,z in {-1,1} do
   table.insert(pts,vec(cf:PointToObjectSpace(p.CFrame:PointToWorldSpace(p.Size*Vector3.new(x,y,z)/2))))
  end end end
  return {name=p.Name,path=p:GetFullName(),corners=pts,transparency=p.Transparency,material=p.Material.Name,
   collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,mesh=p:IsA("MeshPart") and p.MeshId or nil,
   piece=p:GetAttribute("PieceId"),wall=p:GetAttribute("WallId"),surface=cs:HasTag(p,"GolfSurface")}
 end
 local row={n=n,props={},anchors={},geometry={},rails={}}
 for _,m in h:GetDescendants() do
  if m:IsA("Model") and isVisual(m) then
   local parts={}
   local mover=m.Parent.Name:sub(1,6)=="Mover_" and m.Parent or nil
   for _,p in m:GetDescendants() do if p:IsA("BasePart") then
    if p:IsA("MeshPart") then table.insert(parts,record(p)) end
    if p.CanCollide or p.CanQuery or p.CanTouch or not p:GetAttribute("VisualQueryDisabled") then table.insert(out.visualFlags,p:GetFullName()) end
    if mover and mover:GetAttribute("Type")~="toggle" then
     local w=p:FindFirstChildOfClass("WeldConstraint")
     if p.Anchored or not w or w.Part0~=mover.MoverRoot or w.Part1~=p then table.insert(out.weldErrors,p:GetFullName()) end
    end
   end end
   table.insert(row.props,{id=m.Name,parts=parts,revision=m:GetAttribute("Revision")})
  end
 end
 for _,a in h.Decor:GetChildren() do
  if not isVisual(a) then
   local parts={}
   for _,p in a:GetDescendants() do if p:IsA("BasePart") and p.Name~="Anchor" and p.Transparency<1 then table.insert(parts,record(p)) end end
   table.insert(row.anchors,{id=a.Name,parts=parts})
  end
 end
 for _,p in h.Geometry:GetDescendants() do if p:IsA("BasePart") then
  table.insert(row.geometry,record(p))
  if p:GetAttribute("decel_scale") then table.insert(out.surfaceFields,{hole=n,piece=p:GetAttribute("PieceId"),scale=p:GetAttribute("decel_scale")}) end
 end end
 for _,p in h.Rails:GetDescendants() do if p:IsA("BasePart") then table.insert(row.rails,record(p)) end end
 out.holes[n]=row task.wait()
end
_G.StageAMJSON=game.HttpService:JSONEncode(out)
return #_G.StageAMJSON
'''
if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True)
 s=Studio();assert s.mode()[0]=='Edit'
 length=int(s.luau(CODE))
 chunks=[s.luau(f'return string.sub(_G.StageAMJSON,{i+1},{i+45000})') for i in range(0,length,45000)]
 d=json.loads(''.join(chunks));(OUT/'built-bounds.json').write_text(json.dumps(d,separators=(',',':'))+'\n')
 s.luau('_G.StageAMJSON=nil return true')
 print('captured',len(d['holes']),'holes; flags',d['visualFlags'],'welds',d['weldErrors'])
