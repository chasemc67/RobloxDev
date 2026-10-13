"""Fit the one approved Aurora FBX import to the supplied manifests. Local place only."""
import json, re, shutil
from pathlib import Path
from holes_to_lua import to_lua
from fbx_bounds import mesh_bounds
from run_playtests import Studio
GAME=Path(__file__).resolve().parents[1]
ROOT=GAME.parents[1]/'assets/vr-mini-golf/aurora-archipelago/models'
OUT=GAME/'playtests/stage-ai'
records=[]
for batch in (1,2):
 for p in json.loads((ROOT/f'props_batch{batch}_manifest.json').read_text())['parts']:
  assert p['can_collide'] is False
  bounds=mesh_bounds(ROOT/p['fbx'])
  assert set(bounds)=={m['mesh'] for m in p['meshes']}
  for m in p['meshes']: bounds[m['mesh']].update(m)
  revisions=[int(v) for v in re.findall(r'rev\s*(\d+)',json.dumps(p),re.I)]
  records.append(dict(id=p['id'],hole=p['hole'],meshes=bounds,pivot=p['pivot_world'],yaw=p['placement_yaw'],motion=p['motion'],lights=p.get('lights',[]),revision=max(revisions) if revisions else None,tris=p['tris']))
(OUT/'import-specs.json').write_text(json.dumps(records,indent=2)+'\n')
code='local specs='+to_lua(records)+'''
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"),"LOCAL ONLY")
local imported=assert(workspace:FindFirstChild("stage_ai_props"))
local course=workspace.CourseAurora
local rows={}
for _,spec in specs do
 local hole=course["Hole"..spec.hole]
 local m=Instance.new("Model") m.Name=spec.id
 m:SetAttribute("StageAIVisual",true) m:SetAttribute("Revision",spec.revision)
 local found={}
 for _,src in imported:GetDescendants() do
  local s=spec.meshes[src.Name]
  if src:IsA("MeshPart") and s then
   local p=src:Clone() p.Size=Vector3.new(unpack(s.size))
   p.CFrame=CFrame.new(unpack(s.center))*CFrame.Angles(0,math.pi,0)
   p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false
   p.Color=Color3.fromHex(s.color:gsub("#","")) p.Material=Enum.Material[s.roblox_material]
   p.Transparency=s.transparency or 0 p.CastShadow=s.roblox_material~="Neon"
   p:SetAttribute("VisualQueryDisabled",true)
   p:SetAttribute("ManifestTransparency",p.Transparency)
   p.Parent=m found[p.Name]=true
  end
 end
 for name in spec.meshes do assert(found[name],"missing mesh "..name) end
 m.WorldPivot=CFrame.identity
 for _,light in spec.lights do
  local a=Instance.new("Part") a.Name="LightMount" a.Size=Vector3.one*0.05 a.Transparency=1
  a.CFrame=CFrame.new(unpack(light.position_asset_local)) a.Anchored=true
  a.CanCollide=false a.CanQuery=false a.CanTouch=false a.Parent=m
  local l=Instance.new(light.type) l.Color=Color3.fromHex(light.colour:gsub("#","")) l.Range=light.range l.Brightness=light.brightness l.Parent=a
 end
 local cf=CFrame.new(unpack(spec.pivot))*CFrame.Angles(0,math.rad(spec.yaw),0)
 m:PivotTo(cf)
 local mover=spec.motion and assert(hole.Movers:FindFirstChild("Mover_"..spec.motion.id),"missing mover "..spec.id)
 m.Parent=mover or hole.Decor
 if mover and spec.motion.type~="toggle" then
  local root=assert(mover:FindFirstChild("MoverRoot"))
  for _,p in m:GetDescendants() do if p:IsA("BasePart") then
   p.Anchored=false p.Massless=true p.CollisionGroup="GolfMover"
   local w=Instance.new("WeldConstraint") w.Part0=root w.Part1=p w.Parent=p
  end end
  for _,p in mover:GetDescendants() do
   if p:IsA("BasePart") and not p:IsDescendantOf(m) and (p.Name=="BlockerVisual" or p.Name=="FeltSkin") then p.Transparency=1 end
  end
 elseif mover then
  for _,ref in mover:GetChildren() do if ref:IsA("ObjectValue") and ref.Name=="TogglePart" and ref.Value then ref.Value.Transparency=1 end end
  for _,p in m:GetDescendants() do if p:IsA("MeshPart") then p:SetAttribute("ToggleVisual",true) end end
 end
 local anchor=hole.Decor:FindFirstChild(spec.id:sub(5))
 if anchor and anchor~=m then
  local ph=anchor:FindFirstChild("Placeholder")
  if ph then ph:Destroy() end
 end
 table.insert(rows,{id=spec.id,hole=spec.hole,revision=spec.revision,tris=spec.tris,meshes=(function() local n=0 for _ in found do n+=1 end return n end)(),mover=spec.motion and spec.motion.id})
 task.wait()
end
-- Imported skins replace the matching primitive/blockout presentation; collision remains from the data.
local covered={h01_obstacle=true,h08_obstacle=true,h13_obstacle=true,h09_hazard_reef_lagoon=true}
for _,p in course.Blockout:GetDescendants() do
 if p:IsA("BasePart") and (covered[p.Name] or ({h05_moving_geyser_column=true,h11_moving_ice_floe=true,h12_moving_paddle_wheel=true,h13_moving_carousel_arms=true})[p.Name] or p.Name=="h17_toggle" or p.Name=="h15_player_guards" or p.Name=="h17_player_guards") then p.Transparency=1 end
end
imported:Destroy()
return game.HttpService:JSONEncode(rows)
'''
if __name__=='__main__':
 s=Studio(); assert s.mode()[0]=='Edit'
 r=s.luau(code,timeout=300); rows=json.loads(r)
 (OUT/'props-placement.json').write_text(json.dumps(rows,indent=2)+'\n')
 shutil.copy('/tmp/stage_ai_props_merge_report.json',OUT/'merge-report.json')
 print('placed',len(rows),'props',sum(r['meshes'] for r in rows),'meshes')
