"""Import corrected Aurora visuals using stage-am FBX bounds and existing anchors."""
import json,hashlib,shutil
from pathlib import Path
from run_playtests import Studio
from fbx_bounds import mesh_bounds
from holes_to_lua import to_lua
root=Path('../../assets/vr-mini-golf/aurora-archipelago/models')
out=Path('playtests/stage-zf2/aurora')
manifest=json.loads((root/'props_batch3_manifest.json').read_text())
merge=json.loads(Path('/tmp/stage_zf2_props_merge_report.json').read_text())
specs=[]
for spec in manifest['parts']:
 if spec['id'] not in ('h06_respawn_stone','h18_crystal_chute'):continue
 f=root/'fbx/props_fix_overlap'/(spec['id']+'.fbx');bounds=mesh_bounds(f)
 for m in spec['meshes']:bounds[m['mesh']].update(m)
 for obj in merge['files'][spec['id']]['objects']:bounds[obj['name']]['tris']=obj['tris']
 specs.append({'id':spec['id'],'hole':spec['hole'],'meshes':bounds,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(out/'import-specs.json').write_text(json.dumps(specs,indent=2)+'\n')
shutil.copy('/tmp/stage_zf2_props_merge_report.json',out/'merge-report.json')
records=json.loads(Path('playtests/stage-am/import-specs.json').read_text())
for r in records:
 for f in specs:
  if r['id']==f['id']:
   r['meshes']=f['meshes'];r['tris']=merge['files'][r['id']]['tris']
Path('src/ServerStorage/CourseData/AuroraBatch3.luau').write_text('-- Generated stage-am specs; stage-zf2 corrected h06/h18 source FBX bounds.\nreturn '+to_lua(records)+'\n')
s=Studio();assert s.mode()[0]=='Edit'
code='local specs='+to_lua(specs)+'''
assert(game.PlaceId==0 and workspace:GetAttribute('PlaceRole')=='aurora_archipelago')
local imported=assert(workspace:FindFirstChild('stage_zf2_props'))
local rows={}
for _,spec in specs do
 local old=assert(workspace.CourseAurora['Hole'..spec.hole]:FindFirstChild(spec.id,true))
 local pivot=old:GetPivot()
 for _,p in old:GetDescendants() do if p:IsA('BasePart') then assert(not p.CanCollide,'colliding prop') end assert(p.Name~='Placeholder','placeholder within prop') end
 local m=Instance.new('Model');m.Name=spec.id
 for k,v in old:GetAttributes() do m:SetAttribute(k,v) end
 m:SetAttribute('ZF2OverlapProps',true)
 local found={}
 for _,p in imported:GetDescendants() do
  local b=spec.meshes[p.Name]
  if p:IsA('MeshPart') and b then
   local q=p:Clone();q.Size=Vector3.new(unpack(b.size));q.CFrame=CFrame.new(unpack(b.center))*CFrame.Angles(0,math.pi,0)
   q.Anchored=true;q.CanCollide=false;q.CanQuery=false;q.CanTouch=false
   q.Color=Color3.fromHex(b.color:gsub('#',''));q.Material=Enum.Material[b.roblox_material];q.Transparency=b.transparency or 0;q.CastShadow=b.roblox_material~='Neon'
   q:SetAttribute('VisualQueryDisabled',true);q:SetAttribute('ManifestTransparency',q.Transparency);q.Parent=m
   found[p.Name]=q.MeshId
  end
 end
 for name in spec.meshes do assert(found[name],'missing '..name) end
 m.WorldPivot=CFrame.identity
 local kit=game.ServerStorage:FindFirstChild('AuroraBatch3Kit')
 if kit then local prior=kit:FindFirstChild(spec.id);if prior then prior:Destroy() end m:Clone().Parent=kit end
 m:PivotTo(pivot);m.Parent=old.Parent;old:Destroy()
 table.insert(rows,{id=spec.id,pivot={pivot:GetComponents()},meshes=found})
end
imported:Destroy()
return game.HttpService:JSONEncode(rows)
'''
r=s.luau(code);(out/'props-imported.json').write_text(r+'\n');print(r)
