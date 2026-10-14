"""Stage sc5: placeholders_ph1 meshes, H7 pad / plank stone decals.
  PYTHONPATH=tools python3 tools/sc5_place.py placeholders <bundle>
  PYTHONPATH=tools python3 tools/sc5_place.py decals '<json {name: assetId}>'
Placement = placeholders_ph1/manifest.json placement (layout coords) + SugarloafLayout.offset; FBX pivot at the
placement, mesh centres from the merge report. Placeholder parts are kept (hidden, ReplacedBy attribute), not deleted.
"""
import json, sys
from pathlib import Path
from sc5_util import studio, fetch, OUT
from holes_to_lua import to_lua

FBX = Path('/Users/chase-mini/src/RobloxDev/assets/vr-mini-golf/sugarloaf-canyon/models/fbx')
COLORS = json.load(open('/tmp/sc5/inspect_ph.json'))

PH = r'''
local specs=__SPECS__
local bundle=assert(workspace:FindFirstChild(__BUNDLE__))
local course=workspace.CourseSugarloaf
local lay=require(game.ServerStorage.CourseData.SugarloafLayout:Clone())
local off=Vector3.new(table.unpack(lay.offset))
local RY=CFrame.Angles(0,math.pi,0)
local imported={} for _,d in bundle:GetDescendants() do if d:IsA('MeshPart') then imported[d.Name]=d end end
local global={}
for _,p in course:GetDescendants() do if p:IsA('MeshPart') then local suf=p.Name:match('__(.+)$') if suf and not global[suf] then global[suf]=p end end end
local MAT={Iron=Enum.Material.Metal,RustIron=Enum.Material.CorrodedMetal,RivetIron=Enum.Material.DiamondPlate,Brass=Enum.Material.Metal,
 Timber=Enum.Material.WoodPlanks,TimberWeathered=Enum.Material.WoodPlanks,Rope=Enum.Material.Fabric,Water=Enum.Material.Glass,
 RiverStone=Enum.Material.Slate,RiverStoneMoss=Enum.Material.Slate,SandstoneRed=Enum.Material.Sandstone}
local report={placed={},hidden={},appearance={}}
for _,sp in specs do
 local hole=course:FindFirstChild(sp.hole) local decor=hole and hole:FindFirstChild('Decor')
 local holder=decor and decor:FindFirstChild(sp.name)
 if not holder then table.insert(report.placed,{name=sp.name,error='holder missing'}) continue end
 local old=holder:FindFirstChild('SC5Mesh') if old then old:Destroy() end
 local model=Instance.new('Model') model.Name='SC5Mesh'
 for i,pos in sp.positions do
  local root=CFrame.new(Vector3.new(table.unpack(pos))+off)*CFrame.Angles(0,math.rad(sp.yaw),0)
  for _,n in sp.meshes do
   local ip=assert(imported[n.name],'import '..n.name)
   local p=ip:Clone() for _,c in p:GetChildren() do c:Destroy() end
   p.Name=n.name..(#sp.positions>1 and ('_'..i) or '')
   p.Size=Vector3.new(table.unpack(n.size)) p.CFrame=root*CFrame.new(Vector3.new(table.unpack(n.center)))*RY
   local suf=n.name:match('__(.+)$')
   local g=global[suf]
   if g and not g:IsDescendantOf(holder) then p.Color=g.Color p.Material=g.Material p.TextureID=g.TextureID p.MaterialVariant=g.MaterialVariant
    if i==1 then table.insert(report.appearance,n.name..' <- '..g:GetFullName()) end
   else p.Color=Color3.new(table.unpack(n.color)) p.Material=MAT[suf] or Enum.Material.SmoothPlastic p.TextureID=''
    if i==1 then table.insert(report.appearance,n.name..' <- blender colour') end end
   if suf:match('^Neon') then p.Material=Enum.Material.Neon p.CastShadow=false p.Color=Color3.new(table.unpack(n.color)) else p.CastShadow=true end
   p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false p.Massless=true
   pcall(function() p.CollisionFidelity=Enum.CollisionFidelity.Box end)
   p:SetAttribute('SC5Source','placeholders_ph1/'..sp.name..'.fbx')
   p.Parent=model
  end
 end
 model.WorldPivot=CFrame.new(Vector3.new(table.unpack(sp.positions[1]))+off)*CFrame.Angles(0,math.rad(sp.yaw),0)
 model.Parent=holder
 local ph=holder:FindFirstChild('Placeholder')
 local phc
 if ph then for _,p in ph:GetDescendants() do if p:IsA('BasePart') then
   assert(not p.CanCollide,'placeholder collidable '..p:GetFullName())
   if p.Transparency<1 then table.insert(report.hidden,p:GetFullName()) end
   p:SetAttribute('SC5ReplacedBy','placeholders_ph1/'..sp.name..'.fbx') p:SetAttribute('SC5PrevTransparency',p.Transparency) p.Transparency=1
   for _,c in p:GetDescendants() do if c:IsA('Light') then c.Enabled=false elseif c:IsA('SurfaceGui') or c:IsA('BillboardGui') then c.Enabled=false end end
 end end phc=ph:GetBoundingBox().Position end
 local mc,ms=model:GetBoundingBox()
 table.insert(report.placed,{name=sp.name,path=model:GetFullName(),parts=#model:GetChildren(),copies=#sp.positions,
  bboxMin={(mc.Position-ms/2).X,(mc.Position-ms/2).Y,(mc.Position-ms/2).Z},bboxMax={(mc.Position+ms/2).X,(mc.Position+ms/2).Y,(mc.Position+ms/2).Z},
  placeholderCenterDelta=phc and {(mc.Position-phc).X,(mc.Position-phc).Y,(mc.Position-phc).Z} or nil})
end
_G.SC5Out=game.HttpService:JSONEncode(report) return #_G.SC5Out
'''


DECALS = r'''
local ids=__IDS__
local course=workspace.CourseSugarloaf
local lay=require(game.ServerStorage.CourseData.SugarloafLayout:Clone())
local off=Vector3.new(table.unpack(lay.offset))
local GAP=0.08
local report={decals={},removed={}}
-- the collidable surface under a point (skip noncolliding parts)
local function surface(pos)
 local ex={} local rp=RaycastParams.new() rp.FilterType=Enum.RaycastFilterType.Exclude
 for _=1,40 do rp.FilterDescendantsInstances=ex
  local h=workspace:Raycast(pos+Vector3.new(0,3,0),Vector3.new(0,-8,0),rp)
  if not h then return nil end
  if h.Instance.CanCollide then return h end
  table.insert(ex,h.Instance) end
end
local function carrier(parent,name,center,sizeX,sizeZ,look,asset)
 local h=assert(surface(center),'no surface under '..name)
 local n=h.Normal
 local top=(look-n*look:Dot(n)).Unit
 local p=parent:FindFirstChild(name) or Instance.new('Part')
 p.Name=name p.Size=Vector3.new(math.max(0.2,sizeX),0.2,math.max(0.2,sizeZ))
 p.CFrame=CFrame.fromMatrix(h.Position+n*(GAP-0.1),n:Cross(top).Unit,n,top)
 p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false p.CastShadow=false p.Transparency=1
 p:SetAttribute('FeltLift',GAP) p:SetAttribute('VisualQueryDisabled',true) p:SetAttribute('SC5DecalCarrier',true)
 local d=p:FindFirstChildOfClass('Decal') or Instance.new('Decal') d.Texture=asset d.Face=Enum.NormalId.Top d.Parent=p
 p.Parent=parent
 table.insert(report.decals,{path=p:GetFullName(),asset=asset,size={p.Size.X,p.Size.Z},surface=h.Instance:GetFullName(),surfaceY=h.Position.Y,topY=p.Position.Y+0.1*n.Y,lift=GAP})
 return p
end
-- H7 pads: one decal per pad mesh, footprint = pad bounding box, then the pad mesh (visual only) is removed
local h7=course.Hole7 local meshes=h7.Decor.Meshes
local folder=h7.Decor:FindFirstChild('SC5Decals') or Instance.new('Folder') folder.Name='SC5Decals' folder.Parent=h7.Decor
for _,m in meshes:GetChildren() do if m.Name:match('^h07_teleport_pad') then
 for _,p in m:GetDescendants() do if p:IsA('BasePart') then assert(not(p.CanCollide or p.CanQuery or p.CanTouch) and #p:GetTags()==0,'pad part is gameplay '..p:GetFullName()) end end
 local cf,sz=m:GetBoundingBox()
 local exit=m.Name:match('^h07_teleport_pad_exit')~=nil
 carrier(folder,'decal_'..m.Name,cf.Position,sz.X,sz.Z,cf.LookVector,exit and ids.exit or ids.entry)
 table.insert(report.removed,{path=m:GetFullName(),bboxSize={sz.X,sz.Y,sz.Z},parts=#m:GetChildren()})
 m:Destroy()
end end
-- plank respawn stone: flat decal at the placeholders_ph1 placement, no mesh; stand-in stays hidden as a placeholder
local h3=course.Hole3 local holder=h3.Decor.plank_respawn_stone
local pos=Vector3.new(__PLANK__)+off
local yaw=math.rad(__PLANKYAW__)
local ph=holder:FindFirstChild('Placeholder')
local _,phs=ph:GetBoundingBox()
local w=math.max(phs.X,phs.Z) local sx,sz=w,w/1.6
local look=(CFrame.Angles(0,yaw,0)).LookVector
carrier(holder,'SC5Decal',pos,sx,sz,look,ids.plank)
for _,p in ph:GetDescendants() do if p:IsA('BasePart') then assert(not p.CanCollide,'placeholder collidable')
 if p.Transparency<1 then p:SetAttribute('SC5PrevTransparency',p.Transparency) p.Transparency=1 end p:SetAttribute('SC5ReplacedBy','decals/plank_respawn_stone_decal.png') end end
report.plankStandIn={size={phs.X,phs.Y,phs.Z}}
_G.SC5Out=game.HttpService:JSONEncode(report) return #_G.SC5Out
'''


def ph_specs(report):
    man = json.loads((FBX / 'placeholders_ph1/manifest.json').read_text())
    info = json.load(open(report))['mesh_info']
    specs = []
    for name, v in man.items():
        if name == 'plank_respawn_stone':
            continue
        hole = v['instance_paths'][0].split('.')[2]
        pos = v['placement']['pos']
        positions = [pos]
        if name == 'tunnel_lanterns':
            # anchor = right tunnel, hole-local (9, 8, -32); tunnel felt spans local z -16..-42 -> every 6 studs
            positions = [[pos[0], pos[1], pos[2] + dz] for dz in (12, 6, 0, -6)]
        cols = {m['name']: m['cols'][0] for m in COLORS[name]['meshes']}
        meshes = [dict(name=k, center=m['center'], size=m['size'], color=cols[k]) for k, m in info.items() if m['stem'] == name]
        specs.append(dict(name=name, hole=hole, yaw=v['placement']['yaw'], positions=positions, meshes=meshes))
    return specs


if __name__ == '__main__':
    a = sys.argv[1]
    s = studio()
    if a == 'placeholders':
        bundle = sys.argv[2]
        specs = ph_specs('/tmp/sc5/sc5_A_report.json')
        code = PH.replace('__SPECS__', to_lua(specs)).replace('__BUNDLE__', json.dumps(bundle))
        raw = fetch(s, '_G.SC5Out', code); (OUT / 'placeholders.json').write_text(raw + '\n')
        r = json.loads(raw); print(json.dumps(r, indent=1)[:4000])
    elif a == 'decals':
        ids = json.loads(sys.argv[2])
        man = json.loads((FBX / 'placeholders_ph1/manifest.json').read_text())['plank_respawn_stone']['placement']
        code = (DECALS.replace('__IDS__', to_lua(ids)).replace('__PLANK__', ','.join(str(v) for v in man['pos']))
                .replace('__PLANKYAW__', str(man['yaw'])))
        raw = fetch(s, '_G.SC5Out', code); (OUT / 'decals.json').write_text(raw + '\n')
        print(json.dumps(json.loads(raw), indent=1))
