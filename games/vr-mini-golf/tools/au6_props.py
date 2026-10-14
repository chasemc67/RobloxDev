"""Stage au6: replace only the two approved noncolliding H18 banks."""
import json, hashlib, shutil
from pathlib import Path
from run_playtests import Studio
from fbx_bounds import mesh_bounds
from holes_to_lua import to_lua
GAME=Path(__file__).resolve().parents[1]
ROOT=GAME.parents[1]/'assets/vr-mini-golf/aurora-archipelago/models'
OUT=GAME/'playtests/stage-au6'
manifest=json.loads((ROOT/'fbx/props_fix_overlap2/fix_overlap2_manifest.json').read_text())
merge=json.loads(Path('/tmp/stage_au6_props_merge_report.json').read_text())
assert merge['result']=='PASS' and merge['source_files']==2
specs=[]
for entry in manifest['props'].values():
 p=dict(entry['approved_entry']);p.update(fbx=entry['fbx'],sha256=entry['sha256'])
 f=ROOT/p['fbx']; bounds=mesh_bounds(f)
 if p.get('sha256'): assert hashlib.sha256(f.read_bytes()).hexdigest()==p['sha256']
 assert set(bounds)=={m['mesh'] for m in p['meshes']}
 assert not p['can_collide'] and not p['can_query'] and not p['can_touch'] and not p['motion']
 for m in p['meshes']:
  m=dict(m);m['tris']=next(x['tris'] for x in entry['parts'] if x['object']==m['mesh'])
  bounds[m['mesh']].update(m)
 specs.append(dict(id=p['id'],hole=p['hole'],meshes=bounds,pivot=p['pivot_world'],yaw=p['world_yaw'],sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
assert len(specs)==2
code='local specs='+to_lua(specs)+'''
assert(game.PlaceId==0 and workspace:GetAttribute('PlaceRole')=='aurora_archipelago')
local course=workspace.CourseAurora
local imported=assert(workspace:FindFirstChild('stage_au6_props'))
local originals={}
for _,spec in specs do
 local found={}
 for _,v in course:GetDescendants() do if v.Name==spec.id then table.insert(found,v) end end
 assert(#found==1,'expected exactly one original '..spec.id)
 local old=found[1]
 for _,p in old:GetDescendants() do
  assert(not p:IsA('BasePart') or not p.CanCollide,'colliding prop')
  assert(p.Name~='Placeholder','placeholder within prop')
 end
 for name in spec.meshes do
  local n=0 for _,p in imported:GetDescendants() do if p:IsA('MeshPart') and p.Name==name then n+=1 end end
  assert(n==1,'import mesh count '..name..' '..n)
 end
 originals[spec.id]=old
end
local rows={}
for _,spec in specs do
 local old=originals[spec.id]
 local m=Instance.new('Model');m.Name=spec.id
 for k,v in old:GetAttributes() do m:SetAttribute(k,v) end
 m:SetAttribute('AU6OverlapProps',true)
 m.ModelStreamingMode=old.ModelStreamingMode
 local found={}
 for _,p in imported:GetDescendants() do
  local b=spec.meshes[p.Name]
  if p:IsA('MeshPart') and b then
   local q=p:Clone();q.Size=Vector3.new(unpack(b.size));q.CFrame=CFrame.new(unpack(b.center))*CFrame.Angles(0,math.pi,0)
   q.Anchored=true;q.CanCollide=false;q.CanQuery=false;q.CanTouch=false
   q.Color=Color3.fromHex(b.color:gsub('#',''));q.Material=Enum.Material[b.roblox_material]
   q.Transparency=b.transparency or 0;q.CastShadow=b.roblox_material~='Neon'
   q:SetAttribute('VisualQueryDisabled',true);q:SetAttribute('ManifestTransparency',q.Transparency);q.Parent=m
   found[p.Name]=q.MeshId
  end
 end
 m.WorldPivot=CFrame.identity
 local kit=game.ServerStorage:FindFirstChild('AuroraBatch3Kit')
 if kit and kit:FindFirstChild(spec.id) then kit[spec.id]:Destroy();m:Clone().Parent=kit end
 m:PivotTo(CFrame.new(unpack(spec.pivot))*CFrame.Angles(0,math.rad(spec.yaw),0))
 local path=old:GetFullName();m.Parent=old.Parent;old:Destroy()
 table.insert(rows,{id=spec.id,replacedPath=path,pivot={m:GetPivot():GetComponents()},meshes=found})
 task.wait()
end
imported:Destroy()
return game.HttpService:JSONEncode(rows)
'''
if __name__=='__main__':
 s=Studio();assert s.mode()[0]=='Edit'
 rows=json.loads(s.luau(code,timeout=300))
 (OUT/'props-imported.json').write_text(json.dumps(rows,indent=2)+'\n')
 (OUT/'import-specs.json').write_text(json.dumps(specs,indent=2)+'\n')
 shutil.copy('/tmp/stage_au6_props_merge_report.json',OUT/'merge-report.json')
 # Keep batch-three's future normalization aligned with the corrected FBXs.
 records=json.loads((GAME/'playtests/stage-am/import-specs.json').read_text())
 for old in json.loads((GAME/'playtests/stage-au5/import-specs.json').read_text()):
  for r in records:
   if r['id']==old['id']: r.update(meshes=old['meshes'],pivot=old['pivot'],yaw=old['yaw'],tris=json.loads((GAME/'playtests/stage-au5/merge-report.json').read_text())['files'][r['id']]['tris'])
 for r in records:
  for s in specs:
   if r['id']==s['id']:
    r.update(meshes=s['meshes'],pivot=s['pivot'],yaw=s['yaw'],tris=merge['files'][r['id']]['tris'])
 (GAME/'src/ServerStorage/CourseData/AuroraBatch3.luau').write_text('-- Generated batch-three specs; stage-au6 corrected FBX bounds.\nreturn '+to_lua(records)+'\n')
 print('replaced',len(rows),'props')
