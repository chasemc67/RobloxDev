"""Stage sc7: Sugarloaf Canyon tunnel_lanterns_post2 + look7 dressing edgefix4 (incl. cliff filler rocks).
  PYTHONPATH=tools python3 tools/sc7_place.py probe                 (existing look7/lantern/Strata state -> probe.json)
  PYTHONPATH=tools python3 tools/sc7_place.py templates <bundle>     (one template per kit mesh -> ServerStorage.SC7Kit)
  PYTHONPATH=tools python3 tools/sc7_place.py lanterns [--dry]       (H2 right tunnel, every 6 studs; float + clearance)
  PYTHONPATH=tools python3 tools/sc7_place.py dressing               (layout_look7_dressing_edgefix4.json -> Look7Dressing)
  PYTHONPATH=tools python3 tools/sc7_place.py cliffcheck             (cliff base vs ground gaps per edgefix4 filler site)
Placement (models/manifest.json): CFrame.new(pos + SugarloafLayout.offset) * CFrame.Angles(0, rad(yaw), 0); `scale` =
per-axis factors (local X, Y, Z) on every MeshPart Size and its offset from the pivot. Mesh centres/sizes come from the
merge report (Roblox axes, relative to the FBX pivot); the 3D Importer bakes a Y half-turn (undone with RY).
All new parts: anchored, CanCollide/CanQuery/CanTouch off, VisualQueryDisabled (CameraOcclusion leaves them alone).
"""
import json, sys
from pathlib import Path
from sc5_util import studio, fetch, GAME
from holes_to_lua import to_lua

OUT = GAME / 'playtests/stage-sc7'
FBX = Path('/Users/chase-mini/src/RobloxDev/assets/vr-mini-golf/sugarloaf-canyon/models/fbx')
LAYOUT = FBX / 'look7_dressing/layout_look7_dressing_edgefix4.json'
REPORT = '/tmp/sc7/sc7_K_report.json'

PROBE = r'''
local course=workspace.CourseSugarloaf
local r={look7={},lanternHolder={},strata={},variants={},names={},kitLib={}}
local pat={'look7','cliffT_','clay_brick_edging','cliff_filler','gumdrop_shrub','lollipop_cactus','scrub_a','barrel_a','barrel_b','rock_candy_cluster','red_dirt_patch','boulder_scatter','fallen_rock_scatter','gumdrop_boulder','rock_a','rock_b','crystal_cluster'}
local seen={}
for _,root in {workspace,game.ServerStorage} do for _,d in root:GetDescendants() do
 for _,p in pat do if d.Name:sub(1,#p)==p then local key=root.Name..':'..d.ClassName..':'..(d.Parent and d.Parent:GetFullName() or '')
  seen[key]=(seen[key] or 0)+1 break end end end end
for k,v in seen do table.insert(r.look7,{k,v}) end
local h=course.Hole2:FindFirstChild('Decor') and course.Hole2.Decor:FindFirstChild('tunnel_lanterns')
if h then for _,d in h:GetDescendants() do if d:IsA('BasePart') then
 table.insert(r.lanternHolder,{path=d:GetFullName(),pos={d.Position.X,d.Position.Y,d.Position.Z},size={d.Size.X,d.Size.Y,d.Size.Z},transparency=d.Transparency,material=d.Material.Name,color={d.Color.R,d.Color.G,d.Color.B}}) end end end
local strataSeen={}
for _,d in game:GetDescendants() do if d:IsA('MeshPart') then local suf=d.Name:match('__(.+)$')
 if suf then local k=suf..'|'..d.Material.Name..'|'..d.MaterialVariant..'|'..tostring(d:FindFirstChildOfClass('SurfaceAppearance')~=nil)..'|'..d.TextureID
  if not strataSeen[k] then strataSeen[k]=d:GetFullName() end end end end
for k,v in strataSeen do table.insert(r.strata,{k,v}) end
for _,v in game.MaterialService:GetDescendants() do if v:IsA('MaterialVariant') then table.insert(r.variants,{v.Name,v.BaseMaterial.Name,v.ColorMap,v:GetFullName()}) end end
for _,c in course:GetChildren() do table.insert(r.names,c.Name..':'..c.ClassName) end
for _,c in game.ServerStorage:GetChildren() do table.insert(r.kitLib,c.Name..':'..c.ClassName) end
_G.SC5Out=game.HttpService:JSONEncode(r) return #_G.SC5Out
'''

COMMON = r'''
local course=workspace.CourseSugarloaf
local lay=require(game.ServerStorage.CourseData.SugarloafLayout:Clone())
local off=Vector3.new(table.unpack(lay.offset))
local RY=CFrame.Angles(0,math.pi,0)
local kit=assert(game.ServerStorage:FindFirstChild('SC7Kit'),'templates first')
local function visual(p)
 p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false p.Massless=true
 pcall(function() p.CollisionFidelity=Enum.CollisionFidelity.Box end)
 p:SetAttribute('VisualQueryDisabled',true)
end
-- one instance of a kit piece at a layout entry: returns a Model of MeshParts
local function place(piece,meshes,pos,yaw,scale,name)
 local m=Instance.new('Model') m.Name=name
 local root=CFrame.new(Vector3.new(table.unpack(pos))+off)*CFrame.Angles(0,math.rad(yaw),0)
 local s=Vector3.new(table.unpack(scale))
 for _,n in meshes do
  local t=assert(kit:FindFirstChild(n.name),'template '..n.name)
  local p=t:Clone()
  p.Size=Vector3.new(table.unpack(n.size))*s
  p.CFrame=root*CFrame.new(Vector3.new(table.unpack(n.center))*s)*RY
  visual(p) p.Parent=m
 end
 m.WorldPivot=root
 return m
end
'''

TEMPLATES = r'''
local meshes=__MESHES__
local bundle=assert(workspace:FindFirstChild(__BUNDLE__),'bundle missing')
local strata=__STRATA__
local RY=CFrame.Angles(0,math.pi,0)
local imported={}
for _,d in bundle:GetDescendants() do if d:IsA('MeshPart') then local n=d.Name:gsub('%.%d+$','')
 if imported[n] then error('duplicate import '..n) end imported[n]=d end end
-- appearance donors: an existing part with the same material suffix (prefer the same stem)
local byStem,bySuf={},{}
for _,root in {workspace.CourseSugarloaf,game.ServerStorage} do for _,p in root:GetDescendants() do
 if p:IsA('MeshPart') and not p:IsDescendantOf(bundle) and not p:FindFirstAncestor('SC7Kit') and not p:FindFirstAncestor('SC6Backup') then
  local n=p.Name:gsub('_%d+$','') local suf=n:match('__(.+)$')
  if suf then byStem[n]=byStem[n] or p bySuf[suf]=bySuf[suf] or p end end end end
local MAT={Iron=Enum.Material.Metal,Brass=Enum.Material.Metal,Timber=Enum.Material.WoodPlanks,TimberWeathered=Enum.Material.WoodPlanks,
 Scrub=Enum.Material.Grass,RedDirt=Enum.Material.Ground,RedDirtLight=Enum.Material.Ground,Pebble=Enum.Material.Pebble,ClayBrick=Enum.Material.Brick}
local kit=game.ServerStorage:FindFirstChild('SC7Kit') if kit then kit:Destroy() end
kit=Instance.new('Folder') kit.Name='SC7Kit'
local rep={templates={},missing={},kScale={}}
for _,n in meshes do
 local ip=imported[n.name]
 if not ip then table.insert(rep.missing,n.name) continue end
 local k=n.size[1]>0.05 and ip.Size.X/n.size[1] or ip.Size.Z/n.size[3]
 table.insert(rep.kScale,k)
 local p=ip:Clone() for _,c in p:GetChildren() do c:Destroy() end
 p.Name=n.name p.Size=Vector3.new(table.unpack(n.size)) p.CFrame=CFrame.new(Vector3.new(table.unpack(n.center)))*RY
 local suf=n.name:match('__(.+)$')
 local o=byStem[n.name] or bySuf[suf]
 local src
 if o then
  p.Color=o.Color p.Material=o.Material p.MaterialVariant=o.MaterialVariant p.Transparency=o.Transparency p.Reflectance=o.Reflectance
  if byStem[n.name] then -- same mesh: its texture matches these UVs
   p.TextureID=o.TextureID for _,c in o:GetChildren() do if c:IsA('SurfaceAppearance') then c:Clone().Parent=p end end
   src=o:GetFullName()
  else src=o:GetFullName()..' (material+colour; own texture '..ip.TextureID..')' end
 else p.Color=Color3.new(table.unpack(n.color or {0.8,0.8,0.8})) p.Material=MAT[suf] or Enum.Material.SmoothPlastic src='blender colour' end
 if suf=='Strata' then -- the place's Strata look (cliff kit): record Enum material / MaterialVariant
  p.Material=Enum.Material[strata.material] p.MaterialVariant=strata.variant
  if not byStem[n.name] and strata.donor then local d=game:FindFirstChild('Workspace') for seg in strata.donor:gmatch('[^%.]+') do if seg~='Workspace' then d=d[seg] end end
   p.Color=d.Color if ip.TextureID=='' then p.TextureID=d.TextureID end src='strata donor '..strata.donor end
 end
 if suf:match('^Neon') then p.Material=Enum.Material.Neon p.CastShadow=false
  if not o then p.Color=Color3.new(table.unpack(n.color)) end else p.CastShadow=true end -- Neon keeps the donor colour (ph1 NeonAmber 1,0.7,0.25)
 p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false p.Massless=true
 p:SetAttribute('VisualQueryDisabled',true)
 p:SetAttribute('SC7Source',n.src)
 p.Parent=kit
 table.insert(rep.templates,{name=n.name,appearance=src,material=p.Material.Name,variant=p.MaterialVariant,color={p.Color.R,p.Color.G,p.Color.B},
  surfaceAppearance=p:FindFirstChildOfClass('SurfaceAppearance')~=nil,texture=p.TextureID,meshId=p.MeshId})
end
kit.Parent=game.ServerStorage
table.sort(rep.kScale) rep.kMin=rep.kScale[1] rep.kMax=rep.kScale[#rep.kScale] rep.kScale=nil
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''

LANTERNS = r'''
local meshes=__MESHES__
local sites=__SITES__
local DRY=__DRY__
local hole=course.Hole2
local holder=hole.Decor.tunnel_lanterns
local rep={sites={},replaced={},hidden={}}
-- ground under each post (exclude everything that is not hole ground / felt), and nearest gameplay part
local gp={} for _,q in hole:GetDescendants() do if q:IsA('BasePart') and (q.CanCollide or q.CanQuery or q.CanTouch) then table.insert(gp,q) end end
local rp=RaycastParams.new() rp.FilterType=Enum.RaycastFilterType.Include
local grounds={} for _,q in course:GetDescendants() do if q:IsA('MeshPart') and q.Name:match('^h02_ground_s') then table.insert(grounds,q) end end
local function boxDist(pt,q) local l=q.CFrame:PointToObjectSpace(pt) local h=q.Size/2
 return Vector3.new(math.max(math.abs(l.X)-h.X,0),math.max(math.abs(l.Y)-h.Y,0),math.max(math.abs(l.Z)-h.Z,0)).Magnitude end
local model=Instance.new('Model') model.Name='SC7Lanterns'
for i,s in sites do
 local m=place('tunnel_lanterns_post2',meshes,s.pos,s.yaw,{1,1,1},'tunnel_lanterns_post2_'..i)
 local post=m:FindFirstChild('tunnel_lanterns_post2__Iron')
 -- post base: the Iron mesh bottom at the post (local x 2.82..3.03)
 local baseY=post.Position.Y-post.Size.Y/2
 local postXZ=m.WorldPivot*Vector3.new(2.925,0,0)
 -- ground: temporarily query-enable ground tiles (they are visual, CanQuery off)
 local saved={} for _,g in grounds do saved[g]=g.CanQuery g.CanQuery=true end
 rp.FilterDescendantsInstances=grounds
 local hit=workspace:Raycast(Vector3.new(postXZ.X,baseY+3,postXZ.Z),Vector3.new(0,-8,0),rp)
 for g,v in saved do g.CanQuery=v end
 local feltHit
 do local fp=RaycastParams.new() fp.FilterType=Enum.RaycastFilterType.Include fp.FilterDescendantsInstances=gp
  feltHit=workspace:Raycast(Vector3.new(postXZ.X,baseY+3,postXZ.Z),Vector3.new(0,-8,0),fp) end
 -- clearance vs every gameplay part of H2. The Iron mesh is an L (post + crossbar arm), so its bounding box is not
 -- sampled; instead two conservative sub-volumes in pivot space (manifest: post at local x 2.82..3.03, 0.206 x 0.3;
 -- arm + lantern above the lantern bottom y 0 .. Iron top): post column x[2.82,3.03] z[-0.15,0.15] y[base,top],
 -- top volume = the Iron/NeonAmber bbox above local y 0.
 local piv=m.WorldPivot local top=post.Position.Y+post.Size.Y/2
 local vols={{name='post',lo=Vector3.new(2.82,baseY-piv.Y,-0.15),hi=Vector3.new(3.03,top-piv.Y,0.15)},
  {name='arm+lantern',lo=Vector3.new(-0.42,0,-0.42),hi=Vector3.new(3.03,top-piv.Y,0.42)}}
 local best,bq,bv=math.huge,nil,nil
 local per={}
 for _,v in vols do local vb,vq=math.huge,nil
  for ix=0,6 do for iy=0,24 do for iz=0,4 do
   local l=v.lo+(v.hi-v.lo)*Vector3.new(ix/6,iy/24,iz/4) local pt=piv*l
   for _,q in gp do local d=boxDist(pt,q) if d<vb then vb,vq=d,q end end end end end
  per[v.name]={minDist=vb,nearest=vq and vq:GetFullName()}
  if vb<best then best,bq,bv=vb,vq,v.name end end
 table.insert(rep.sites,{i=i,pos=s.pos,postBaseY=baseY,postXZ={postXZ.X,postXZ.Z},ground=hit and hit.Position.Y or false,groundPart=hit and hit.Instance:GetFullName() or false,
  baseMinusGround=hit and (baseY-hit.Position.Y) or false,gameplayBelow=feltHit and feltHit.Instance:GetFullName() or false,
  minDistGameplay=best,nearest=bq and bq:GetFullName() or false,nearestVolume=bv,volumes=per,feltTopBelow=feltHit and feltHit.Position.Y or false})
 m.Parent=model
end
if not DRY then
 local old=holder:FindFirstChild('SC5Mesh') if old then table.insert(rep.replaced,old:GetFullName()..' ('..#old:GetChildren()..' parts)') old.Parent=nil
  local bk=game.ServerStorage:FindFirstChild('SC7Backup') or Instance.new('Folder') bk.Name='SC7Backup' bk.Parent=game.ServerStorage old.Parent=bk end
 for _,c in holder:GetChildren() do if c.Name=='SC7Lanterns' then c:Destroy() end end
 model.Parent=holder
 local ph=holder:FindFirstChild('Placeholder')
 if ph then for _,p in ph:GetDescendants() do if p:IsA('BasePart') then p:SetAttribute('SC7ReplacedBy','placeholders_ph2/tunnel_lanterns_post2.fbx')
  table.insert(rep.hidden,{p:GetFullName(),p.Transparency}) end end end
end
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''

DRESSING = r'''
local pieces=__PIECES__
local inst=__INST__
local folder=course:FindFirstChild('Look7Dressing')
local rep={replacedOld=0,placed=0,parts=0,byPiece={}}
if folder then rep.replacedOld=#folder:GetChildren() folder:Destroy() end
folder=Instance.new('Folder') folder.Name='Look7Dressing'
folder:SetAttribute('SC7Layout','look7_dressing/layout_look7_dressing_edgefix4.json')
local sub={}
for i,e in inst do
 local f=sub[e.piece] if not f then f=Instance.new('Folder') f.Name=e.piece f.Parent=folder sub[e.piece]=f end
 local m=place(e.piece,assert(pieces[e.piece],'piece '..e.piece),e.pos,e.yaw,e.scale,e.piece..'_'..e.i)
 m:SetAttribute('SC7LayoutIndex',e.i) m:SetAttribute('SC7Src',e.src)
 m.Parent=f rep.placed+=1 rep.parts+=#m:GetChildren()
 rep.byPiece[e.piece]=(rep.byPiece[e.piece] or 0)+1
 if i%200==0 then task.wait() end
end
folder.Parent=course
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''

# Cliff base check per edgefix4 filler site (site k = the k-th cliff step dropped by edgefix2, refilled by edgefix3/4).
# (1) openFrac: top-down rays over the dropped panel's footprint; a ray whose first hit is not Look7 dressing sees ground
#     through the cliff stack (the layout's own open_after is the art bot's figure for the same thing).
# (2) base gaps: every cliff/filler part within 3 studs of the footprint is sampled on its footprint perimeter (inset 0.25);
#     the first ground surface (terrain or non-dressing part) from 20 above: gap = base - ground (> 0.15 = visible slit;
#     <= 0 = the base is buried). openFrac counts only ground seen at/below the site's cliff base.
# Visual parts near the site are query-enabled for the duration of the check and restored exactly.
CLIFF = r'''
local sites=__SITES__
local dress=course.Look7Dressing
local rep={sites={}}
local all={} for _,p in workspace:GetDescendants() do if p:IsA('BasePart') and p.Transparency<1 then table.insert(all,p) end end
for _,s in sites do
 local root=CFrame.new(Vector3.new(table.unpack(s.pos))+off)*CFrame.Angles(0,math.rad(s.yaw),0)
 local sc=s.scale
 local hx,z0,z1=12*sc[1],(2.75-5.25)*sc[3],(2.75+5.25)*sc[3]
 local saved={} local near={} local dn={}
 for _,p in all do if (p.Position-root.Position).Magnitude<60 then if not p.CanQuery then saved[p]=true p.CanQuery=true end
  table.insert(near,p) if p:IsDescendantOf(dress) then table.insert(dn,p) end end end
 local rpAll=RaycastParams.new() rpAll.FilterType=Enum.RaycastFilterType.Include local inc={workspace.Terrain} for _,p in near do table.insert(inc,p) end rpAll.FilterDescendantsInstances=inc
 local ground={workspace.Terrain} for _,p in near do if not p:IsDescendantOf(dress) then table.insert(ground,p) end end
 local rpG=RaycastParams.new() rpG.FilterType=Enum.RaycastFilterType.Include rpG.FilterDescendantsInstances=ground
 local n,open=0,0
 for x=-hx,hx,0.5 do for z=z0,z1,0.5 do
  local o=root*Vector3.new(x,0,z)
  local h=workspace:Raycast(o+Vector3.new(0,12,0),Vector3.new(0,-30,0),rpAll) n+=1
  if h and not h.Instance:IsDescendantOf(dress) and h.Position.Y<root.Position.Y+0.3 then open+=1 end -- ground seen at/below the cliff base
 end end
 -- base gaps of dressing parts around the site
 local models={} for _,p in dn do local m=p:FindFirstAncestorOfClass('Model')
  local nm=m and m.Name or '' if m and (nm:match('^cliffT_') or nm:match('^cliff_filler')) then
   local l=root:PointToObjectSpace(m.WorldPivot.Position)
   if math.abs(l.X)<hx+3 and l.Z>z0-3 and l.Z<z1+3 then models[m]=true end end end
 local parts={}
 for m in models do
  local cnt,gapN,maxGap,buriedN=0,0,-99,0
  for _,p in m:GetChildren() do if p:IsA('BasePart') then
   local base=m.WorldPivot.Position.Y
   local sx,sz=p.Size.X/2-0.25,p.Size.Z/2-0.25
   for i=-1,1,0.25 do for j=-1,1,0.25 do
    if math.abs(i)<1 and math.abs(j)<1 then continue end -- footprint perimeter only
    local w=p.CFrame*Vector3.new(i*sx,0,j*sz)
    local h=workspace:Raycast(Vector3.new(w.X,base+400,w.Z),Vector3.new(0,-800,0),rpG) -- ground surface from above
    local g=h and (base-h.Position.Y) or 99
    cnt+=1 if g>0.15 then gapN+=1 end if g>maxGap then maxGap=g end
    if h and h.Position.Y>=base+p.Size.Y then buriedN+=1 end
   end end end end
  table.insert(parts,{model=m.Name,src=m:GetAttribute('SC7Src'),samples=cnt,gapFrac=gapN/math.max(cnt,1),maxGap=maxGap,buriedFrac=buriedN/math.max(cnt,1)})
 end
 for p in saved do p.CanQuery=false end
 table.insert(rep.sites,{site=s.site,pos=s.pos,yaw=s.yaw,openFrac=open/n,layoutOpenAfter=s.open_after,samples=n,parts=parts})
 task.wait()
end
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''


def meshes_by_piece():
    info = json.load(open(REPORT))['mesh_info']
    src = {s['stem']: s['fbx'].split('/models/fbx/')[1] for s in json.load(open('/tmp/sc7/sources.json'))}
    by = {}
    for name, m in info.items():
        by.setdefault(m['stem'], []).append(dict(name=name, center=m['center'], size=m['size'], src=src[m['stem']]))
    return by


def strata_spec():
    return json.loads((OUT / 'strata.json').read_text())


if __name__ == '__main__':
    a = sys.argv[1]
    s = studio()
    if a == 'probe':
        raw = fetch(s, '_G.SC5Out', PROBE)
        (OUT / 'probe.json').write_text(raw + '\n'); print(json.dumps(json.loads(raw), indent=0)[:6000])
    elif a == 'templates':
        by = meshes_by_piece()
        cols = json.load(open('/tmp/sc7/colors.json')) if Path('/tmp/sc7/colors.json').exists() else {}
        meshes = [dict(m, color=cols.get(m['name'])) for v in by.values() for m in v]
        st = strata_spec()
        code = (TEMPLATES.replace('__MESHES__', to_lua(meshes)).replace('__BUNDLE__', json.dumps(sys.argv[2]))
                .replace('__STRATA__', to_lua(st)))
        raw = fetch(s, '_G.SC5Out', code)
        (OUT / 'templates.json').write_text(raw + '\n'); r = json.loads(raw)
        print('templates', len(r['templates']), 'missing', r['missing'], 'k', r['kMin'], r['kMax'])
        for t in r['templates']: print(t['name'], t['material'], t['variant'], t['surfaceAppearance'], '<-', t['appearance'][-70:])
    elif a == 'lanterns':
        by = meshes_by_piece()
        man = json.load(open(FBX / 'placeholders_ph2/manifest.json'))['tunnel_lanterns_post2']['placement']
        p = man['pos']
        # right tunnel felt spans hole-local z -16..-42; anchor local z -32 -> every 6 studs: -20, -26, -32, -38
        sites = [dict(pos=[p[0], p[1], p[2] + dz], yaw=man['yaw']) for dz in (12, 6, 0, -6)]
        dry = '--dry' in sys.argv
        code = (COMMON + LANTERNS).replace('__MESHES__', to_lua(by['tunnel_lanterns_post2'])).replace('__SITES__', to_lua(sites)) \
            .replace('__DRY__', 'true' if dry else 'false')
        raw = fetch(s, '_G.SC5Out', code)
        (OUT / ('lanterns' + ('-dry' if dry else '') + '.json')).write_text(raw + '\n'); print(json.dumps(json.loads(raw), indent=1))
    elif a == 'dressing':
        by = meshes_by_piece()
        L = json.loads(LAYOUT.read_text())
        inst = [dict(i=k + 1, piece=e['piece'], pos=e['pos'], yaw=e['yaw'], scale=e.get('scale', [1, 1, 1]), src=e.get('src', ''))
                for k, e in enumerate(L['instances'])]
        pieces = {k: by[k] for k in {e['piece'] for e in inst}}
        code = (COMMON + DRESSING).replace('__PIECES__', to_lua(pieces)).replace('__INST__', to_lua(inst))
        raw = fetch(s, '_G.SC5Out', code, timeout=1800)
        (OUT / 'dressing.json').write_text(raw + '\n'); print(json.loads(raw))
    elif a == 'cliffcheck':
        sites = json.load(open('/tmp/sc7/sites.json'))
        raw = fetch(s, '_G.SC5Out', (COMMON + CLIFF).replace('__SITES__', to_lua(sites)), timeout=1800)
        (OUT / 'cliff-check.json').write_text(raw + '\n'); r = json.loads(raw)
        for x in r['sites']:
            worst = max(x['parts'], key=lambda p: p['gapFrac'], default=None)
            print(x['site'], 'open', round(x['openFrac'], 3), 'layout', x['layoutOpenAfter'], 'parts', len(x['parts']),
                  'worst', worst and (worst['model'], round(worst['gapFrac'], 2), round(worst['maxGap'], 2)),
                  'fullyBuried', sum(p['buriedFrac'] == 1 for p in x['parts']))
