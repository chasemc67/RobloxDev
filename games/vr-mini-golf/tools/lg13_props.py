"""Stage lg13: replace the Lantern Grove kit + placed copies of the approved fix_zfight props.
Imported bundle: workspace.lg13_props (3D Importer, merged /tmp/lg13/lg13_props.fbx). Importer x99.4 auto-scale and
Y half-turn are undone from the true FBX bounds (fbx_bounds.py). Placed copies keep their pivot, ScaleTo factor,
colour/material (H9 dim, rail dims), lights, emissive appearances and mover welds; only the mesh parts change.
  PYTHONPATH=tools python3 tools/lg13_props.py
"""
import hashlib, json
from pathlib import Path
from run_playtests import Studio
from fbx_bounds import mesh_bounds
from holes_to_lua import to_lua
GAME = Path(__file__).resolve().parents[1]
FBX = GAME.parents[1] / 'assets/vr-mini-golf/lantern-grove/models/fbx'
OUT = GAME / 'playtests/stage-lg13-claude'
SOURCES = {
    'h5_respawn_stone': ('fix_zfight4/h5_respawn_stone.fbx', 'fix_zfight4/fix_zfight4_manifest.json'),
    'gold_leaf_bush': ('fix_zfight/gold_leaf_bush.fbx', 'fix_zfight/fix_zfight_manifest.json'),
    'grass_tuft': ('fix_zfight/grass_tuft.fbx', 'fix_zfight/fix_zfight_manifest.json'),
    'lantern_span_20': ('fix_zfight/lantern_span_20.fbx', 'fix_zfight/fix_zfight_manifest.json'),
    'h9_lantern_pendulum': ('fix_zfight/h9_lantern_pendulum.fbx', 'fix_zfight/fix_zfight_manifest.json'),
    'h9_lantern_pendulum_h9dim': ('fix_zfight/h9_lantern_pendulum_h9dim.fbx', 'fix_zfight/fix_zfight_manifest.json'),
}
specs = []
for prop, (fbx, man) in SOURCES.items():
    entry = json.loads((FBX / man).read_text())['props'][prop]
    data = (FBX / fbx).read_bytes()
    assert hashlib.sha256(data).hexdigest() == entry['sha256'], prop
    b = mesh_bounds(FBX / fbx)
    specs.append(dict(prop=prop, tris=entry['tris'], sha256=entry['sha256'], fbx=fbx,
                      meshes={k: dict(center=v['center'], size=v['size']) for k, v in b.items()}))

code = 'local specs=' + to_lua(specs) + r'''
assert(workspace:GetAttribute('PlaceRole')=='lantern_grove')
local imported=assert(workspace:FindFirstChild('lg13_props'))
local lib=game.ServerStorage.LanternGroveProps
local course=workspace.Course
local report={kit={},placed={},lightsMoved=0}
local function decorate(p) p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.Massless=true
 pcall(function() p.CollisionFidelity=Enum.CollisionFidelity.Box end) end
local function isCopy(m,P)
 for _,c in m:GetChildren() do if c:IsA('BasePart') and c.Name:sub(1,#P+2)==P..'__' then return true end end
 return false
end
-- placed copies first (before the kit changes), longest prop names first so h9dim doesn't match the plain pendulum
table.sort(specs,function(a,b) return #a.prop>#b.prop end)
local claimed={}
local copies={}
for _,spec in specs do
 copies[spec.prop]={}
 for _,m in course:GetDescendants() do
  if m:IsA('Model') and not claimed[m] and isCopy(m,spec.prop) then claimed[m]=true;table.insert(copies[spec.prop],m) end
 end
end
for _,spec in specs do
 local P=spec.prop
 local oldKit=assert(lib:FindFirstChild(P),'kit '..P)
 local src=assert(imported:FindFirstChild(P),'import '..P)
 -- new kit model at the origin
 local kit=Instance.new('Model');kit.Name=P
 for k,v in oldKit:GetAttributes() do kit:SetAttribute(k,v) end
 kit:SetAttribute('Tris',spec.tris);kit:SetAttribute('LG13Source',spec.fbx);kit:SetAttribute('LG13Sha256',spec.sha256)
 for name,b in spec.meshes do
  local p=assert(src:FindFirstChild(name),'mesh '..name):Clone()
  for _,c in p:GetChildren() do c:Destroy() end
  p.TextureID=''
  p.Size=Vector3.new(table.unpack(b.size))
  p.CFrame=CFrame.new(table.unpack(b.center))*CFrame.Angles(0,math.pi,0)
  local ref=oldKit:FindFirstChild(name)
  if ref then p.Color=ref.Color;p.Material=ref.Material;p.Transparency=ref.Transparency;p.CastShadow=ref.CastShadow end
  decorate(p);p.Parent=kit
 end
 kit.WorldPivot=CFrame.new()
 table.insert(report.kit,{prop=P,oldMeshes=#oldKit:GetChildren(),newMeshes=#kit:GetChildren()})
 -- placed copies
 for _,m in copies[P] do
  local pivot,s=m:GetPivot(),m:GetScale()
  local olds={}
  for _,c in m:GetChildren() do if c:IsA('BasePart') and c.Name:sub(1,#P+2)==P..'__' then olds[c.Name]=c end end
  local anyOld=next(olds) and olds[next(olds)]
  local news={}
  local weldTo
  for _,o in olds do for _,w in o:GetChildren() do if w:IsA('WeldConstraint') and w.Part0 and w.Part0~=o then weldTo=w.Part0 end end end
  for _,kp in kit:GetChildren() do
   local p=kp:Clone()
   local lp=kp.CFrame
   p.Size=kp.Size*s
   p.CFrame=pivot*CFrame.new(lp.Position*s)*(lp-lp.Position)
   local o=olds[kp.Name] or anyOld
   if olds[kp.Name] then p.Color=o.Color;p.Material=o.Material;p.Transparency=o.Transparency end
   p.CastShadow=o.CastShadow
   for k,v in o:GetAttributes() do if k:sub(1,3)~='ZF1' then p:SetAttribute(k,v) end end
   if olds[kp.Name] then
    for _,c in o:GetChildren() do if c:IsA('SurfaceAppearance') then c:Clone().Parent=p end end
   end
   p.Anchored=o.Anchored
   if weldTo then local w=Instance.new('WeldConstraint');w.Part0=weldTo;w.Part1=p;w.Parent=p end
   p.Parent=m
   news[kp.Name]=p
  end
  -- lights: same-named part, else the first Neon part, else the largest part
  for _,o in olds do
   for _,c in o:GetChildren() do
    if c:IsA('Light') then
     local t=news[o.Name]
     if not t then for _,q in news do if q.Material==Enum.Material.Neon then t=q break end end end
     if not t then t=next(news) and news[next(news)] end
     c.Parent=t;report.lightsMoved+=1
    end
   end
  end
  for _,o in olds do o:Destroy() end
  table.insert(report.placed,{prop=P,path=m:GetFullName(),scale=s,old=(function() local n=0 for _ in olds do n+=1 end return n end)(),new=#kit:GetChildren()})
 end
 oldKit:Destroy();kit.Parent=lib
 task.wait()
end
imported:Destroy()
return game.HttpService:JSONEncode(report)
'''
if __name__ == '__main__':
    s = Studio(); assert s.mode()[0] == 'Edit'
    OUT.mkdir(parents=True, exist_ok=True)
    rep = json.loads(s.luau(code, timeout=300))
    (OUT / 'props-imported.json').write_text(json.dumps(rep, indent=2) + '\n')
    (OUT / 'import-specs.json').write_text(json.dumps(specs, indent=2) + '\n')
    print({'kit': rep['kit'], 'placed': len(rep['placed']), 'lightsMoved': rep['lightsMoved']})
