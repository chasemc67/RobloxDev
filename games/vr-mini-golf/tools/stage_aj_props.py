"""Import only approved h08_ground and h09_water_tank at manifest transforms."""
import json
from pathlib import Path
from holes_to_lua import REPO,to_lua
from fbx_bounds import mesh_bounds
from run_playtests import Studio
root=Path(REPO)/'assets/vr-mini-golf/sugarloaf-canyon/models'
records=[]
m=json.loads((root/'manifest.json').read_text());p=next(x for x in m['pieces'] if x['id']=='h08_ground')
meshes=mesh_bounds(root/'fbx/h08_ground.fbx')
for mat in p['parts'][0]['meshes']:
 bounds=meshes[mat['mesh']].copy(); meshes[mat['mesh']].update(mat); meshes[mat['mesh']].update(bounds)
records.append({'id':'h08_ground','meshes':meshes,'instances':[{'world_pos':x['pos'],'yaw':x['yaw'],'hole':'h08'} for x in p['instances']]})
p=next(x for x in json.loads((root/'props_h09h14_manifest.json').read_text())['parts'] if x['id']=='h09_water_tank')
meshes=mesh_bounds(root/p['fbx'])
for mat in p['report']['meshes']: meshes[mat['mesh']].update(mat)
records.append({'id':p['id'],'meshes':meshes,'instances':[{'world_pos':p['pivot_world'],'yaw':p['yaw_deg'],'hole':p['hole']}]})
code='local specs='+to_lua(records)+'''
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"),"LOCAL ONLY")
local imported=assert(workspace:FindFirstChild("stage_aj_props"),"missing imported stage_aj_props")
local ss=game.ServerStorage
local off=Vector3.new(unpack(require(ss.CourseData.SugarloafLayout:Clone()).offset))
local course=workspace.CourseSugarloaf
local lib=Instance.new("Folder") lib.Name="StageAJProps" lib.Parent=ss
local report={}
for _,spec in specs do
 local model=Instance.new("Model") model.Name=spec.id
 local found={}
 for _,part in imported:GetDescendants() do
  local s=spec.meshes[part.Name]
  if part:IsA("MeshPart") and s then
   part=part:Clone() part.Parent=model
   part.Size=Vector3.new(unpack(s.size))
   part.CFrame=CFrame.new(unpack(s.center))*CFrame.Angles(0,math.pi,0)
   part.Anchored=true part.CanCollide=false part.CanQuery=false part.CanTouch=false part:SetAttribute("VisualQueryDisabled",true)
   if s.color then part.Color=Color3.fromHex(s.color:gsub("#","")) end
   if s.roblox_material then part.Material=Enum.Material[s.roblox_material] end
   part.CastShadow=s.cast_shadow~=false and s.roblox_material~="Neon"
   found[part.Name]=true
  end
 end
 for name in spec.meshes do assert(found[name],"missing mesh "..name) end
 model.WorldPivot=CFrame.identity model.Parent=lib
 for _,inst in spec.instances do
  local n=tonumber(inst.hole:match("%d+")) local hole=course["Hole"..n]
  local cf=CFrame.new(Vector3.new(unpack(inst.world_pos))+off)*CFrame.Angles(0,math.rad(inst.yaw),0)
  local target=hole:FindFirstChild("StageAJVisuals")
  if not target then target=Instance.new("Folder") target.Name="StageAJVisuals" target.Parent=hole end
  local mover=spec.mover and hole.Movers:FindFirstChild("Mover_"..spec.mover)
  if spec.mover then assert(mover and mover:FindFirstChild("MoverRoot"),"missing mover "..spec.mover) end
  -- Replace corresponding old visual models without touching exact collision proxies.
  local names={[spec.id]=true}
  if spec.id=="h09_windpump_rotor" then names.h09_windpump_vanes=true names.h09_windpump_hub=true end
  for _,d in course:GetDescendants() do
   if d:IsA("Model") and names[d.Name]  then
    local physical=false
    for _,p in d:GetDescendants() do if p:IsA("BasePart") and p.CanCollide then physical=true end end
    if not physical then d:Destroy() end
   end
  end
  local m=model:Clone() m:PivotTo(cf) m.Parent=mover or target
  m:SetAttribute("StageAJVisual",true)
  if mover then
   for _,p in m:GetDescendants() do if p:IsA("BasePart") then
    p.Anchored=false p.Massless=true p.CollisionGroup="GolfMover"
    local w=Instance.new("WeldConstraint") w.Part0=mover.MoverRoot w.Part1=p w.Parent=p
   end end
   for _,p in mover:GetDescendants() do if p.Name=="BlockerVisual" and p:IsA("BasePart") then p.Transparency=1 end end
  end
  table.insert(report,{id=spec.id,hole=n,pivot=m:GetPivot().Position,parts=#m:GetDescendants(),mover=spec.mover})
 end
end
imported:Destroy()
return report
'''
if __name__=='__main__':
 r=Studio().luau(code,timeout=300);print(r)
 json.loads(r)
 Path('playtests/stage-aj/props-placement.json').write_text(r+'\n')
