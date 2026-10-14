"""Stage au7: replace the H7 mogul trim (props_fix_overlap3) and H18 ramp lanterns (props_fix_overlap4) visuals.
Imported bundle: workspace.stage_au7_props (3D Importer, merged /tmp/au7/stage_au7_props.fbx). Each mesh is rebuilt
from the true FBX bounds (fbx_bounds.py) with the importer Y half-turn undone, placed at the prop's manifest
pivot_world/world_yaw (asserted equal to the live model pivot), and keeps the live part's colour/material/transparency.
Visual only: CanCollide/CanQuery/CanTouch off. Any ServerStorage kit copy of the prop is replaced too.
  python3 tools/au7_props.py
"""
import hashlib, json, shutil
from pathlib import Path
from run_playtests import Studio
from fbx_bounds import mesh_bounds
from holes_to_lua import to_lua
GAME = Path(__file__).resolve().parents[1]
MODELS = GAME.parents[1] / 'assets/vr-mini-golf/aurora-archipelago/models'
OUT = GAME / 'playtests/stage-au7'
MERGE = Path('/tmp/au7/stage_au7_props_merge_report.json')
# id -> (new manifest, approved placement record carrying pivot_world/world_yaw)
SOURCES = {
    'h07_mogul_trim': ('fbx/props_fix_overlap3/props_fix_overlap3_manifest.json', 'props_batch1_manifest.json'),
    'h18_ramp_lanterns': ('fbx/props_fix_overlap4/props_fix_overlap4_manifest.json', 'props_batch3_manifest.json'),
}
FITCHECK = {'h07_mogul_trim': 'fbx/props_fix_overlap3/props_fix_overlap3_fitcheck.json',
            'h18_ramp_lanterns': 'fbx/props_fix_overlap4/props_fix_overlap4_fitcheck.json'}
merge = json.loads(MERGE.read_text())
assert merge['result'] == 'PASS' and merge['source_files'] == 2
specs = []
for pid, (man, placed) in SOURCES.items():
    entry = json.loads((MODELS / man).read_text())['props'][pid]
    f = MODELS / entry['fbx']
    assert hashlib.sha256(f.read_bytes()).hexdigest() == entry['sha256'], pid
    assert not entry['collision'] and not entry['query'] and not entry['touch']
    fit = json.loads((MODELS / FITCHECK[pid]).read_text())[pid]
    fit = fit.get('after', fit)
    assert fit['intersecting_pairs'] == 0 and fit['coplanar_tri_pairs'] == 0 and fit['thin_parts'] == 0, pid
    pm = json.loads((MODELS / placed).read_text())
    rec = next(p for p in (pm['parts'] if 'parts' in pm else pm['props']) if p['id'] == pid)
    b = mesh_bounds(f)
    assert set(b) == {p['object'] for p in entry['parts']}, pid
    for p in entry['parts']:
        b[p['object']]['tris'] = p['tris']
    specs.append(dict(id=pid, hole=rec['hole'], fbx=entry['fbx'], sha256=entry['sha256'], tris=entry['tris'],
                      meshes=b, pivot=rec['pivot_world'], yaw=rec['world_yaw']))

code = 'local specs=' + to_lua(specs) + r'''
assert(game.PlaceId==79649062523043 and workspace:GetAttribute('PlaceRole')=='aurora_archipelago')
local course=workspace.CourseAurora
local imported=assert(workspace:FindFirstChild('stage_au7_props'),'no import')
local function near(a,b) for i=1,12 do if math.abs(a[i]-b[i])>1e-3 then return false end end return true end
local rows={}
for _,spec in specs do
 local found={}
 for _,v in course:GetDescendants() do if v.Name==spec.id then table.insert(found,v) end end
 assert(#found==1,'expected exactly one original '..spec.id..' got '..#found)
 local old=found[1]
 assert(old:IsA('Model'))
 local want=CFrame.new(unpack(spec.pivot))*CFrame.Angles(0,math.rad(spec.yaw),0)
 assert(near({old:GetPivot():GetComponents()},{want:GetComponents()}),'live pivot differs from manifest '..spec.id)
 local olds={}
 for _,p in old:GetDescendants() do
  if p:IsA('BasePart') then
   assert(not p.CanCollide and not p.CanQuery and not p.CanTouch,'gameplay part in prop '..p:GetFullName())
   assert(#game.CollectionService:GetTags(p)==0,'tagged part in prop '..p:GetFullName())
   olds[p.Name]=p
  end
 end
 -- build at identity
 local m=Instance.new('Model');m.Name=spec.id
 for k,v in old:GetAttributes() do m:SetAttribute(k,v) end
 m:SetAttribute('AU7Source',spec.fbx);m:SetAttribute('AU7Sha256',spec.sha256);m:SetAttribute('Tris',spec.tris)
 m.ModelStreamingMode=old.ModelStreamingMode
 local meshes={}
 for name,b in spec.meshes do
  local src={} for _,p in imported:GetDescendants() do if p:IsA('MeshPart') and p.Name==name then table.insert(src,p) end end
  assert(#src==1,'import mesh count '..name..' '..#src)
  local ref=assert(olds[name],'no live part '..name)
  local q=src[1]:Clone()
  for _,c in q:GetChildren() do c:Destroy() end
  q.TextureID=''
  q.Size=Vector3.new(unpack(b.size));q.CFrame=CFrame.new(unpack(b.center))*CFrame.Angles(0,math.pi,0)
  q.Anchored=true;q.CanCollide=false;q.CanQuery=false;q.CanTouch=false;q.Massless=true
  pcall(function() q.CollisionFidelity=Enum.CollisionFidelity.Box end)
  q.Color=ref.Color;q.Material=ref.Material;q.Transparency=ref.Transparency;q.CastShadow=ref.CastShadow
  q.Reflectance=ref.Reflectance
  for k,v in ref:GetAttributes() do if k:sub(1,3)~='ZF1' then q:SetAttribute(k,v) end end
  q:SetAttribute('VisualQueryDisabled',true)
  for _,c in ref:GetChildren() do if not c:IsA('JointInstance') and not c:IsA('WeldConstraint') then c:Clone().Parent=q end end
  q.Parent=m
  meshes[name]=q.MeshId
 end
 m.WorldPivot=CFrame.identity
 local kits={}
 for _,v in game.ServerStorage:GetDescendants() do
  if v.Name==spec.id and v:IsA('Model') then
   local k=m:Clone();k:PivotTo(v:GetPivot());local par=v.Parent;local path=v:GetFullName();v:Destroy();k.Parent=par
   table.insert(kits,path)
  end
 end
 m:PivotTo(want)
 local path=old:GetFullName();local parent=old.Parent;old:Destroy();m.Parent=parent
 local n=0 for _,v in course:GetDescendants() do if v.Name==spec.id then n+=1 end end
 assert(n==1,'duplicate '..spec.id)
 table.insert(rows,{id=spec.id,replacedPath=path,newPath=m:GetFullName(),pivot={m:GetPivot():GetComponents()},meshes=meshes,
  oldParts=(function() local t={} for k in olds do table.insert(t,k) end table.sort(t) return t end)(),kitsReplaced=kits})
 task.wait()
end
imported:Destroy()
return game.HttpService:JSONEncode(rows)
'''

if __name__ == '__main__':
    s = Studio(); assert s.mode()[0] == 'Edit'
    OUT.mkdir(parents=True, exist_ok=True)
    rows = json.loads(s.luau(code, timeout=300))
    (OUT / 'imported.json').write_text(json.dumps({'imported': rows, 'specs': specs}, indent=2) + '\n')
    shutil.copy(MERGE, OUT / 'merge-report.json')
    print({r['id']: r['replacedPath'] for r in rows})
