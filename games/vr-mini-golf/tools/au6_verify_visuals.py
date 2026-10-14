import json,sys
from pathlib import Path
from run_playtests import Studio
s=Studio();assert s.mode()[0]=='Edit'
code="""
local c=workspace.CourseAurora local h=c.Hole6
local layers={h.Hazards.RespawnStone,h.Decor.h06_respawn_stone.h06_respawn_stone__Lime}
local r={layers={},thin={},props={},placeholders={}}
local function halfY(p) return (math.abs(p.CFrame.RightVector.Y)*p.Size.X+math.abs(p.CFrame.UpVector.Y)*p.Size.Y+math.abs(p.CFrame.ZVector.Y)*p.Size.Z)/2 end
for _,p in c:GetDescendants() do
 if p:IsA('BasePart') and p.Transparency<1 and math.min(p.Size.X,p.Size.Y,p.Size.Z)<.19999 then table.insert(r.thin,p:GetFullName()) end
end
local minGap=math.huge
for _,p in layers do
 local row={path=p:GetFullName(),size={p.Size.X,p.Size.Y,p.Size.Z},cf={p.CFrame:GetComponents()},bottom=p.Position.Y-halfY(p),top=p.Position.Y+halfY(p),supports={}}
 local minimum=math.huge
 for _,q in h:GetDescendants() do
  if q:IsA('BasePart') and (q.CanCollide or (q.Transparency<1 and q.Name=='Visual_Felt')) then
   local n=q.CFrame.UpVector
   if math.abs(n.Y)>.9 then
    local top=-math.huge
    for _,x in {-1,1} do for _,z in {-1,1} do
     local wx=p.Position.X+x*.4 local wz=p.Position.Z+z*.4
     local plane=q.Position+n*q.Size.Y/2
     local y=plane.Y-(n.X*(wx-plane.X)+n.Z*(wz-plane.Z))/n.Y
     local localP=q.CFrame:PointToObjectSpace(Vector3.new(wx,y,wz))
     if math.abs(localP.X)<=q.Size.X/2+.001 and math.abs(localP.Z)<=q.Size.Z/2+.001 then top=math.max(top,y) end
    end end
    if top>-math.huge then
     local gap=(row.bottom-top)*math.abs(n.Y)
     table.insert(row.supports,{path=q:GetFullName(),gap=gap,collider=q.CanCollide})
     minimum=math.min(minimum,gap)
    end
   end
  end
 end
 row.minimumSupportGap=minimum
 if p==layers[2] then row.previousLayerGap=row.bottom-(layers[1].Position.Y+halfY(layers[1]));minimum=math.min(minimum,row.previousLayerGap) end
 row.cacheMatches=p:GetAttribute('ZF1BaseCF')==p.CFrame and p:GetAttribute('ZF1BaseSize')==p.Size
 assert(not p.CanCollide and not p.CanQuery and not p.CanTouch)
 minGap=math.min(minGap,minimum);table.insert(r.layers,row)
end
r.minimumGap=minGap
for _,id in {'h18_crystal_bank_ne_deco','h18_crystal_bank_sw_deco'} do
 local found={} for _,m in c:GetDescendants() do if m.Name==id then table.insert(found,m) end end
 assert(#found==1,'duplicate '..id)
 local meshes={}
 for _,p in found[1]:GetDescendants() do if p:IsA('BasePart') then
  assert(not p.CanCollide and not p.CanQuery and not p.CanTouch)
  table.insert(meshes,{name=p.Name,mesh=p.MeshId,size={p.Size.X,p.Size.Y,p.Size.Z}})
 end end
 table.insert(r.props,{path=found[1]:GetFullName(),meshes=meshes})
end
return game.HttpService:JSONEncode(r)
"""
r=json.loads(s.luau(code));phase=sys.argv[1] if len(sys.argv)>1 else 'after'
Path('playtests/stage-au6/visual-'+phase+'.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
if phase=='after':
 assert r['minimumGap']>=.08 and not r['thin']
 assert all(x['cacheMatches'] for x in r['layers'])
