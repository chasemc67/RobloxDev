"""Read-only post-import verification of approved source hashes and manifest transforms."""
import hashlib,json
from pathlib import Path
from run_playtests import Studio
from holes_to_lua import to_lua
GAME=Path(__file__).resolve().parents[1]; ROOT=GAME.parents[1]; OUT=GAME/'playtests/stage-am'
CODE='''
assert(game.PlaceId==0 and not game:FindFirstChildOfClass("NetworkClient"))
local records=__SPECS__ local rows={} local errors={}
for _,r in records do
 local m=assert(workspace.CourseAurora["Hole"..r.hole]:FindFirstChild(r.id,true),r.id)
 local expected=CFrame.new(unpack(r.pivot))*CFrame.Angles(0,math.rad(r.yaw),0)
 local row={id=r.id,revision=m:GetAttribute("Revision"),parts={}}
 if m:GetAttribute("Revision")~=r.revision then table.insert(errors,r.id..":revision") end
 for name,s in r.meshes do
  local p=assert(m:FindFirstChild(name),name)
  local cf=expected*CFrame.new(unpack(s.center))*CFrame.Angles(0,math.pi,0)
  local pos=(p.Position-cf.Position).Magnitude
  local size=(p.Size-Vector3.new(unpack(s.size))).Magnitude
  local rotation=(p.CFrame.LookVector-cf.LookVector).Magnitude+(p.CFrame.UpVector-cf.UpVector).Magnitude
  local color=Color3.fromHex(s.color:gsub("#",""))
  local colorError=math.abs(p.Color.R-color.R)+math.abs(p.Color.G-color.G)+math.abs(p.Color.B-color.B)
  local ok=pos<0.001 and size<0.001 and rotation<0.001 and colorError<0.001 and p.Material.Name==s.roblox_material
   and math.abs(p.Transparency-(s.transparency or 0))<0.0001 and not p.CanCollide and not p.CanQuery and not p.CanTouch and p:GetAttribute("VisualQueryDisabled")==true
  if not ok then table.insert(errors,name) end
  table.insert(row.parts,{name=name,meshId=p.MeshId,positionError=pos,sizeError=size,rotationError=rotation,pass=ok})
 end
 assert(not (r.id=="h06_kettle_pool" and m:FindFirstChild("h06_kettle_pool__Steam")),"unapproved kettle steam mesh")
 table.insert(rows,row)
end
return game.HttpService:JSONEncode({props=rows,errors=errors})
'''
if __name__=='__main__':
 hashes=json.loads((OUT/'import-hashes.json').read_text())
 for h in hashes:
  h['unchanged']=hashlib.sha1((ROOT/h['file']).read_bytes()).hexdigest()==h['sha1']
 assert all(h['unchanged'] for h in hashes)
 s=Studio();assert s.mode()[0]=='Edit'
 specs=json.loads((OUT/'import-specs.json').read_text())
 r=json.loads(s.luau(CODE.replace('__SPECS__',to_lua(specs))))
 r['hashes_unchanged']=True;r['fbx_files']=len(hashes)
 (OUT/'asset-check.json').write_text(json.dumps(r,indent=2)+'\n')
 print('asset check',len(r['props']),'props; errors',r['errors'])
