"""Stage sc8: Sugarloaf Canyon H16 2-slot rim + sinkhole opening, ground seams, TRADING POST board raise,
H3 dress props (fix_v42_item5c), cliff filler deletion.
  PYTHONPATH=tools python3 tools/sc8_place.py probe            (state of everything sc8 touches -> probe.json)
  PYTHONPATH=tools python3 tools/sc8_place.py replace [--dry]  (items 1+5: rim + h03_dress_props from the sc8_K import)
  PYTHONPATH=tools python3 tools/sc8_place.py lua FILE [OUT]    (run a Luau file that sets _G.SC5Out)
Mesh centres/sizes come from the merge report (~/sc8imp/sc8_K_report.json, Roblox axes relative to the FBX pivot); the
3D Importer bakes a Y half-turn (undone with RY). Part CFrame = root * CFrame.new(centre) * RY, root = the model's
frame (Workspace rim: the rim model pivot; Workspace h03: CFrame.new(-95,18,-4670); ServerStorage library copies: identity).
"""
import json, sys
from pathlib import Path
from sc5_util import studio, fetch, GAME

OUT = GAME / 'playtests/stage-sc8'

PROBE = r'''
local course=workspace.CourseSugarloaf
local h16=course.Hole16
local function row(p) return {path=p:GetFullName(),class=p.ClassName,pos={p.Position.X,p.Position.Y,p.Position.Z},size={p.Size.X,p.Size.Y,p.Size.Z},
 rot={p.CFrame:ToOrientation()},collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,transparency=p.Transparency,material=p.Material.Name,
 color={p.Color.R,p.Color.G,p.Color.B},tags=p:GetTags(),attrs=p:GetAttributes()} end
local r={h16={},rim={},rimLib={},seams={},board={},h03={},fillers={},fillerTemplates={},attrs={}}
-- every H16 part within 3 studs (xz) of the sinkhole centre, plus all gameplay parts in H16
local rim=h16.StageAFVisuals.h16_sinkhole_rim
local frame=rim:FindFirstChild('h16_sinkhole_rim__GeodeRim',true)
local c=frame.Position r.centre={c.X,c.Y,c.Z} r.rimPivot={rim:GetPivot():GetComponents()}
for _,p in h16:GetDescendants() do if p:IsA('BasePart') then
 local d=Vector3.new(p.Position.X-c.X,0,p.Position.Z-c.Z).Magnitude
 if d<4 or p.CanCollide or p.CanTouch then table.insert(r.h16,row(p)) end end end
for _,p in rim:GetDescendants() do if p:IsA('BasePart') then table.insert(r.rim,row(p)) end end
for _,p in game.ServerStorage.StageAFProps.h16_sinkhole_rim:GetDescendants() do if p:IsA('BasePart') then table.insert(r.rimLib,row(p)) end end
for k,v in h16:GetAttributes() do r.attrs[k]=v end
for _,p in course:GetDescendants() do if p:IsA('BasePart') and (p.Name:match('^h16_ground_s03') or p.Name:match('^h17_ground_s20') or p.Name:match('^h13_ground_s04')
 or p.Name:match('^h14_ground_s00') or p.Name:match('^h09_ground_s0[01]')) then table.insert(r.seams,row(p)) end end
local tp=course.Kit.hole_dressing.trading_post_deck
for _,p in tp:GetDescendants() do if p:IsA('BasePart') then table.insert(r.board,row(p)) end end
for _,root in {course,game.ServerStorage} do for _,m in root:GetDescendants() do if m.Name=='h03_dress_props' and m:IsA('Model') then
 local parts={} for _,p in m:GetDescendants() do if p:IsA('BasePart') then table.insert(parts,row(p)) end end
 table.insert(r.h03,{path=m:GetFullName(),pivot={m:GetPivot():GetComponents()},parts=parts}) end end end
local l7=course:FindFirstChild('Look7Dressing')
local nf,np=0,0 local fparents={}
if l7 then for _,f in l7:GetChildren() do if f.Name:match('^cliff_filler_rock') then fparents[f.Name]=#f:GetChildren()
 for _,p in f:GetDescendants() do if p:IsA('BasePart') then np+=1 end end end end end
r.fillers={folders=fparents,parts=np}
local kit=game.ServerStorage:FindFirstChild('SC7Kit')
if kit then for _,t in kit:GetChildren() do if t.Name:match('cliff_filler') then table.insert(r.fillerTemplates,t.Name) end end end
_G.SC5Out=game.HttpService:JSONEncode(r) return #_G.SC5Out
'''

REPLACE = r'''
local meshes=__MESHES__
local DRY=__DRY__
local RY=CFrame.Angles(0,math.pi,0)
local bundle=assert(workspace:FindFirstChild('sc8_K'),'import bundle sc8_K missing')
local imported={} for _,d in bundle:GetDescendants() do if d:IsA('MeshPart') then imported[d.Name]=d end end
local course=workspace.CourseSugarloaf
local NEON={h16_sinkhole_rim__CrystalPink=Color3.new(1,0.4,0.75),h16_sinkhole_rim__CrystalAmber=Color3.new(1,0.7,0.25)}
local SRC={h16_sinkhole_rim='h16_rim_2slot_b/h16_sinkhole_rim.fbx',h03_dress_props='fix_v42_item5c/h03_dress_props.fbx'}
local targets={
 {stem='h16_sinkhole_rim',model=course.Hole16.StageAFVisuals.h16_sinkhole_rim,root=course.Hole16.StageAFVisuals.h16_sinkhole_rim:GetPivot(),ws=true},
 {stem='h16_sinkhole_rim',model=game.ServerStorage.StageAFProps.h16_sinkhole_rim,root=CFrame.identity,ws=false},
 {stem='h03_dress_props',model=course.Kit.hole_dressing.h03_dress_props.h03_dress_props,root=CFrame.new(-95,18,-4670),ws=true},
 {stem='h03_dress_props',model=game.ServerStorage.SugarloafKit.h03_dress_props,root=CFrame.identity,ws=false},
}
local rep={copies={},kScale={}}
local bk=game.ServerStorage:FindFirstChild('SC8Backup')
if not DRY then if not bk then bk=Instance.new('Folder') bk.Name='SC8Backup' bk.Parent=game.ServerStorage end end
for _,t in targets do
 local m=t.model
 local old={} for _,p in m:GetChildren() do if p:IsA('BasePart') then old[p.Name]=p end end
 local copy={path=m:GetFullName(),root={t.root:GetComponents()},oldParts={},newParts={},unchangedSlotDelta={}}
 for n,p in old do table.insert(copy.oldParts,{name=n,pos={p.Position.X,p.Position.Y,p.Position.Z},size={p.Size.X,p.Size.Y,p.Size.Z},material=p.Material.Name,color={p.Color.R,p.Color.G,p.Color.B}}) end
 local newParts={}
 for _,n in meshes do if n.stem==t.stem then
  local ip=assert(imported[n.name],'imported '..n.name)
  table.insert(rep.kScale,ip.Size.X/n.size[1])
  local p=ip:Clone() for _,c in p:GetChildren() do c:Destroy() end
  for a in p:GetAttributes() do p:SetAttribute(a,nil) end
  p.Name=n.name p.Size=Vector3.new(table.unpack(n.size)) p.CFrame=t.root*CFrame.new(Vector3.new(table.unpack(n.center)))*RY
  local o=old[n.name] local appearance
  if o then -- same slot: keep the old part's look and flags
   p.Material=o.Material p.MaterialVariant=o.MaterialVariant p.Color=o.Color p.Transparency=o.Transparency p.Reflectance=o.Reflectance
   p.CastShadow=o.CastShadow p.CollisionGroup=o.CollisionGroup p.Anchored=o.Anchored p.Massless=o.Massless
   if p.TextureID=='' then p.TextureID=o.TextureID end
   for _,c in o:GetChildren() do if c:IsA('SurfaceAppearance') then c:Clone().Parent=p end end
   for a,v in o:GetAttributes() do if a:sub(1,3)~='ZF1' and a~='SC5Source' then p:SetAttribute(a,v) end end
   appearance='old '..o:GetFullName()
   local d=(p.Position-o.Position).Magnitude
   if n.name:match('GeodeRim') or n.name:match('PepRed') or n.name:match('Rope') or n.name:match('Timber') or n.name:match('GumLime') then
    table.insert(copy.unchangedSlotDelta,{name=n.name,posDelta=d,sizeDelta=(p.Size-o.Size).Magnitude,rotSame=p.CFrame.Rotation:FuzzyEq(o.CFrame.Rotation,1e-4)}) end
  else
   p.Material=Enum.Material.Neon p.Color=assert(NEON[n.name],'no appearance rule for '..n.name) p.CastShadow=false
   p.Anchored=true p.Massless=true appearance='Neon '..tostring(p.Color)
   local g=old['h16_sinkhole_rim__GeodeRim'] if g then p.CollisionGroup=g.CollisionGroup end
  end
  p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false
  pcall(function() p.CollisionFidelity=Enum.CollisionFidelity.Box end)
  if t.ws then p:SetAttribute('VisualQueryDisabled',true) end
  p:SetAttribute('SC8Source',SRC[t.stem])
  table.insert(newParts,p)
  table.insert(copy.newParts,{name=n.name,appearance=appearance,material=p.Material.Name,color={p.Color.R,p.Color.G,p.Color.B},castShadow=p.CastShadow,
   texture=p.TextureID,mesh=p.MeshId,pos={p.Position.X,p.Position.Y,p.Position.Z},size={p.Size.X,p.Size.Y,p.Size.Z}})
 end end
 if not DRY then
  local b=m:Clone() b.Name=m.Name..'__'..(t.ws and 'Workspace' or 'ServerStorage') b:SetAttribute('SC8BackupOf',m:GetFullName()) b.Parent=bk
  for _,p in old do p:Destroy() end
  for _,p in newParts do p.Parent=m end
  local flags={} for _,q in m:GetDescendants() do if q:IsA('BasePart') then
   assert(not q.CanCollide and not q.CanQuery and not q.CanTouch,'flag on '..q:GetFullName())
   if t.ws then assert(q:GetAttribute('VisualQueryDisabled')==true,'VisualQueryDisabled '..q:GetFullName()) end end end
  copy.backup=b:GetFullName()
 end
 table.insert(rep.copies,copy)
end
table.sort(rep.kScale) rep.kMin=rep.kScale[1] rep.kMax=rep.kScale[#rep.kScale] rep.kScale=nil
if not DRY then bundle:Destroy() rep.bundleRemoved=true end
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''

if __name__ == '__main__':
    a = sys.argv[1]
    s = studio()
    if a == 'probe':
        raw = fetch(s, '_G.SC5Out', PROBE); (OUT / 'probe.json').write_text(raw + '\n'); print(len(raw))
    elif a == 'replace':
        from holes_to_lua import to_lua
        rp = json.load(open('/tmp/sc8/sc8_K_report.json'))['mesh_info']
        meshes = [{'name': k, 'stem': v['stem'], 'center': v['center'], 'size': v['size']} for k, v in rp.items()]
        dry = '--dry' in sys.argv
        raw = fetch(s, '_G.SC5Out', REPLACE.replace('__MESHES__', to_lua(meshes)).replace('__DRY__', 'true' if dry else 'false'))
        (OUT / ('replace-dry.json' if dry else 'replace.json')).write_text(raw + '\n')
        r = json.loads(raw); print('k', r['kMin'], r['kMax'])
        for c in r['copies']:
            print(c['path'], len(c['oldParts']), '->', len(c['newParts']), c.get('backup'))
            for d in c['unchangedSlotDelta']: print('   ', d)
            for n in c['newParts']: print('    ', n['name'], n['material'], [round(x, 3) for x in n['color']], n['castShadow'], n['appearance'][:80])
    elif a == 'lua':
        raw = fetch(s, '_G.SC5Out', Path(sys.argv[2]).read_text(), timeout=900)
        if len(sys.argv) > 3: Path(sys.argv[3]).write_text(raw + '\n')
        print(raw[:6000])
