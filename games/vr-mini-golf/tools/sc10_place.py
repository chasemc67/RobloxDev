"""Stage sc10: Sugarloaf Canyon H16 rim 2slot_d, TRADING POST board +0.3, H3 floating pebbles, H11/H12 trench dressing,
rail-rule push-off for Look7Dressing.
  PYTHONPATH=tools python3 tools/sc10_place.py probe                 (rim / board / H3 pebble state -> probe.json)
  PYTHONPATH=tools python3 tools/sc10_place.py rim [--dry]           (item 1: rim from the sc10_K import, manifest appearance)
  PYTHONPATH=tools python3 tools/sc10_place.py board                 (item 2: both sc6 board parts +0.3, Workspace + library)
  PYTHONPATH=tools python3 tools/sc10_place.py look7 NAME            (live Look7 pivots -> NAME.json)
  PYTHONPATH=tools python3 tools/sc10_place.py move FILE             (apply a move/delete plan: [{i, dx, dy, dz} | {i, delete}])
  PYTHONPATH=tools python3 tools/sc10_place.py lua FILE [OUT]        (run a Luau file that sets _G.SC5Out)
Look7 geometry (true mesh, not bounding boxes) comes from sc9_mesh_geom.py (/tmp/sc9/geom.json: per-slot XZ hulls, minY/maxY,
contact ring). A piece's frame is its Model WorldPivot (= layout pos + offset, yaw) with the layout per-axis scale.
"""
import json, math, sys
from pathlib import Path
from sc5_util import studio, fetch, GAME
from holes_to_lua import to_lua

OUT = GAME / 'playtests/stage-sc10'
GEOM = Path('/tmp/sc9/geom.json')
PLAN = Path('/tmp/sc9/plan.json')
REPORT = Path('/Users/chase-mini/sc10imp/sc10_K_report.json')

PROBE = r'''
local course=workspace.CourseSugarloaf
local function row(p) return {path=p:GetFullName(),class=p.ClassName,pos={p.Position.X,p.Position.Y,p.Position.Z},size={p.Size.X,p.Size.Y,p.Size.Z},
 rot={p.CFrame:ToOrientation()},collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,transparency=p.Transparency,material=p.Material.Name,
 color=p.Color:ToHex(),castShadow=p.CastShadow,texture=p:IsA('MeshPart') and p.TextureID or '',mesh=p:IsA('MeshPart') and p.MeshId or '',attrs=p:GetAttributes()} end
local r={rim={},rimLib={},board={},boardLib={},h03={}}
local rim=course.Hole16.StageAFVisuals.h16_sinkhole_rim
r.rimPivot={rim:GetPivot():GetComponents()}
for _,p in rim:GetDescendants() do if p:IsA('BasePart') then table.insert(r.rim,row(p)) end end
for _,p in game.ServerStorage.StageAFProps.h16_sinkhole_rim:GetDescendants() do if p:IsA('BasePart') then table.insert(r.rimLib,row(p)) end end
for _,p in course.Kit.hole_dressing.trading_post_deck:GetDescendants() do if p:IsA('BasePart') and p:GetAttribute('SC6Source') then table.insert(r.board,row(p)) end end
for _,p in game.ServerStorage.SugarloafKit.trading_post_deck:GetDescendants() do if p:IsA('BasePart') and p:GetAttribute('SC6Source') then table.insert(r.boardLib,row(p)) end end
for _,root in {course,game.ServerStorage} do for _,m in root:GetDescendants() do if m.Name=='h03_dress_props' and m:IsA('Model') then
 local parts={} for _,p in m:GetDescendants() do if p:IsA('BasePart') then table.insert(parts,row(p)) end end
 table.insert(r.h03,{path=m:GetFullName(),pivot={m:GetPivot():GetComponents()},parts=parts}) end end end
_G.SC5Out=game.HttpService:JSONEncode(r) return #_G.SC5Out
'''

# Item 1. Same frame as sc8 (Workspace root = the rim model pivot, library root = identity). Appearance from the d manifest.
RIM = r'''
local meshes=__MESHES__
local DRY=__DRY__
local RY=CFrame.Angles(0,math.pi,0)
local bundle=assert(workspace:FindFirstChild('sc10_K'),'import bundle sc10_K missing')
local imported={} for _,d in bundle:GetDescendants() do if d:IsA('MeshPart') then local n=d.Name:gsub('%.%d+$','') assert(not imported[n],'dup '..n) imported[n]=d end end
local course=workspace.CourseSugarloaf
local LOOK={ -- h16_rim_2slot_d/manifest.json "materials"
 h16_sinkhole_rim__GeodeRim={Enum.Material.Rock,'C8463F'},
 h16_sinkhole_rim__CrystalPink={Enum.Material.Neon,'FF6FA8'},
 h16_sinkhole_rim__CrystalAmber={Enum.Material.Neon,'FFB347'},
 h16_sinkhole_rim__PepRed={Enum.Material.SmoothPlastic,'D9343A'},
 h16_sinkhole_rim__Rope={Enum.Material.Fabric,'C9A86A'},
 h16_sinkhole_rim__Timber={Enum.Material.WoodPlanks,'8A5A33'}}
local targets={
 {model=course.Hole16.StageAFVisuals.h16_sinkhole_rim,root=course.Hole16.StageAFVisuals.h16_sinkhole_rim:GetPivot(),ws=true},
 {model=game.ServerStorage.StageAFProps.h16_sinkhole_rim,root=CFrame.identity,ws=false},
}
local rep={copies={},kScale={}}
local bk=game.ServerStorage:FindFirstChild('SC10Backup')
if not DRY and not bk then bk=Instance.new('Folder') bk.Name='SC10Backup' bk.Parent=game.ServerStorage end
for _,t in targets do
 local m=t.model
 local old={} for _,p in m:GetChildren() do if p:IsA('BasePart') then old[p.Name]=p end end
 local copy={path=m:GetFullName(),root={t.root:GetComponents()},oldParts={},newParts={},slotDelta={}}
 for n,p in old do table.insert(copy.oldParts,{name=n,pos={p.Position.X,p.Position.Y,p.Position.Z},size={p.Size.X,p.Size.Y,p.Size.Z},material=p.Material.Name,color=p.Color:ToHex(),mesh=p.MeshId}) end
 local newParts={}
 for _,n in meshes do
  local ip=assert(imported[n.name],'imported '..n.name)
  table.insert(rep.kScale,ip.Size.X/n.size[1])
  local p=ip:Clone() for _,c in p:GetChildren() do c:Destroy() end
  for a in p:GetAttributes() do p:SetAttribute(a,nil) end
  p.Name=n.name p.Size=Vector3.new(table.unpack(n.size)) p.CFrame=t.root*CFrame.new(Vector3.new(table.unpack(n.center)))*RY
  local look=assert(LOOK[n.name],'no manifest look for '..n.name)
  p.Material=look[1] p.MaterialVariant='' p.Color=Color3.fromHex(look[2]) p.Transparency=0 p.Reflectance=0
  local o=old[n.name]
  if o then
   p.CastShadow=o.CastShadow p.CollisionGroup=o.CollisionGroup
   for a,v in o:GetAttributes() do if a:sub(1,3)~='ZF1' and a:sub(1,2)~='SC' then p:SetAttribute(a,v) end end
   table.insert(copy.slotDelta,{name=n.name,posDelta=(p.Position-o.Position).Magnitude,sizeDelta=(p.Size-o.Size).Magnitude,
    rotSame=p.CFrame.Rotation:FuzzyEq(o.CFrame.Rotation,1e-4),bottomDelta=(p.Position.Y-p.Size.Y/2)-(o.Position.Y-o.Size.Y/2)})
  else p.CastShadow=false end
  if look[1]==Enum.Material.Neon then p.CastShadow=false end
  p.Anchored=true p.Massless=true p.CanCollide=false p.CanQuery=false p.CanTouch=false
  pcall(function() p.CollisionFidelity=Enum.CollisionFidelity.Box end)
  if t.ws then p:SetAttribute('VisualQueryDisabled',true) end
  p:SetAttribute('SC10Source','h16_rim_2slot_d/h16_sinkhole_rim.fbx')
  table.insert(newParts,p)
  table.insert(copy.newParts,{name=n.name,material=p.Material.Name,color=p.Color:ToHex(),castShadow=p.CastShadow,texture=p.TextureID,mesh=p.MeshId,
   pos={p.Position.X,p.Position.Y,p.Position.Z},size={p.Size.X,p.Size.Y,p.Size.Z},bottomY=p.Position.Y-p.Size.Y/2})
 end
 if not DRY then
  local b=m:Clone() b.Name=m.Name..'__'..(t.ws and 'Workspace' or 'ServerStorage') b:SetAttribute('SC10BackupOf',m:GetFullName()) b.Parent=bk
  for _,p in old do p:Destroy() end
  for _,p in newParts do p.Parent=m end
  for _,q in m:GetDescendants() do if q:IsA('BasePart') then
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

# Item 2. Both sc6 board parts (SC6Source attribute), Workspace + SugarloafKit library copy, +0.3. H1 rail1 clearance.
BOARD = r'''
local DY=0.3
local rep={parts={},rail={}}
local ws=workspace.CourseSugarloaf.Kit.hole_dressing.trading_post_deck
local lib=game.ServerStorage.SugarloafKit.trading_post_deck
local wsBoard={}
-- Workspace parts carry SC6Source; the library copies only carry sc8's SC8Raise mark
local function isBoard(root,p) if root==ws then return p:GetAttribute('SC6Source')~=nil end
 return p:GetAttribute('SC8Raise')~=nil and (p.Name:match('__PepRed$') or p.Name:match('__MintWhite$'))~=nil end
for _,root in {ws,lib} do local n=0
 for _,p in root:GetDescendants() do if p:IsA('BasePart') and isBoard(root,p) then n+=1
  local b=p.Position.Y
  p.CFrame=p.CFrame+Vector3.new(0,DY,0)
  if p:GetAttribute('ZF1BaseCF') then p:SetAttribute('ZF1BaseCF',p:GetAttribute('ZF1BaseCF')+Vector3.new(0,DY,0)) end
  p:SetAttribute('SC10Raise',DY)
  if root==ws then table.insert(wsBoard,p) end
  table.insert(rep.parts,{path=p:GetFullName(),name=p.Name,src=p:GetAttribute('SC6Source'),beforeY=b,afterY=p.Position.Y,collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch}) end end
 assert(n==2,'expected 2 sc6 board parts in '..root:GetFullName()..', got '..n)
end
local rails={} for _,q in workspace.CourseSugarloaf.Hole1:GetDescendants() do if q:IsA('BasePart') and q.Name:match('rail1$') then table.insert(rails,q) end end
local function boxDist(pt,q) local l=q.CFrame:PointToObjectSpace(pt) local h=q.Size/2
 return Vector3.new(math.max(math.abs(l.X)-h.X,0),math.max(math.abs(l.Y)-h.Y,0),math.max(math.abs(l.Z)-h.Z,0)).Magnitude end
for _,p in wsBoard do local best,bq=math.huge,nil
 for ix=0,4 do for iy=0,2 do for iz=0,4 do
  local pt=p.CFrame*Vector3.new((ix/4-0.5)*p.Size.X,(iy/2-0.5)*p.Size.Y,(iz/4-0.5)*p.Size.Z)
  for _,q in rails do local d=boxDist(pt,q) if d<best then best,bq=d,q end end end end end
 table.insert(rep.rail,{part=p.Name,minDist=best,rail=bq and bq:GetFullName(),rails=#rails}) end
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''

# Ground under a set of world XZ points: Terrain + every visible (Transparency < 1) BasePart that is not Look7 dressing and not
# the probed thing itself (same ground set as sc9's float rule). CanQuery-off visual parts are query-enabled for the call and
# restored. Each ray goes down from y0 (per point) 200 studs.
GROUND = r'''
local Q=__Q__
local course=workspace.CourseSugarloaf
local skip={course.Look7Dressing} for _,m in __SKIP__ do table.insert(skip,m) end
local function skipped(p) for _,s in skip do if p==s or p:IsDescendantOf(s) then return true end end return false end
local saved={} local ground={workspace.Terrain}
for _,p in workspace:GetDescendants() do if p:IsA('BasePart') and p.Transparency<1 and not skipped(p) then
 table.insert(ground,p) if not p.CanQuery then saved[p]=true p.CanQuery=true end end end
local rp=RaycastParams.new() rp.FilterType=Enum.RaycastFilterType.Include rp.FilterDescendantsInstances=ground
local rep={}
local ok,err=pcall(function()
 for _,q in Q do local hits={}
  for _,pt in q.pts do local h=workspace:Raycast(Vector3.new(pt[1],pt[2],pt[3]),Vector3.new(0,-200,0),rp)
   table.insert(hits,h and {h.Position.Y,h.Instance==workspace.Terrain and 'Terrain' or h.Instance:GetFullName(),h.Instance:HasTag('GolfSurface')} or false) end
  rep[tostring(q.id)]=hits end
end)
for p in saved do p.CanQuery=false end
assert(ok,err)
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''

# True-surface ground: the RENDER mesh, not the collision geometry. Candidates = every visible (Transparency < 1) BasePart
# outside the skip set whose world AABB contains the column; MeshParts are hit with EditableMesh:RaycastLocal on their own
# mesh (vertex bounds -> part Size), block Parts with an exact ray/box slab test, plus Terrain (workspace:Raycast).
# Returns the highest hit below each origin (first surface going down). Nothing in the place is modified.
TRUEGROUND = r'''
local Q=__Q__
local course=workspace.CourseSugarloaf
local skip={course.Look7Dressing} for _,m in __SKIP__ do table.insert(skip,m) end
local function skipped(p) for _,s in skip do if p==s or p:IsDescendantOf(s) then return true end end return false end
local AS=game:GetService('AssetService')
local parts={}
for _,p in workspace:GetDescendants() do if p:IsA('BasePart') and p.Transparency<1 and not skipped(p) and p~=workspace.Terrain then
 local cf,s=p.CFrame,p.Size/2 local R=cf.Rotation
 local e=Vector3.new(math.abs(R.XVector.X)*s.X+math.abs(R.YVector.X)*s.Y+math.abs(R.ZVector.X)*s.Z,
  math.abs(R.XVector.Y)*s.X+math.abs(R.YVector.Y)*s.Y+math.abs(R.ZVector.Y)*s.Z,
  math.abs(R.XVector.Z)*s.X+math.abs(R.YVector.Z)*s.Y+math.abs(R.ZVector.Z)*s.Z)
 table.insert(parts,{p=p,lo=cf.Position-e,hi=cf.Position+e}) end end
local cache={}
local function mesh(p) local id=p.MeshId local c=cache[id]
 if c==nil then local ok,e=pcall(function() return AS:CreateEditableMeshAsync(Content.fromUri(id)) end)
  if ok then local mn,mx=Vector3.one*1e9,-Vector3.one*1e9 for _,v in e:GetVertices() do local q=e:GetPosition(v) mn=mn:Min(q) mx=mx:Max(q) end
   c={e=e,ctr=(mn+mx)/2,size=mx-mn} else c=false end cache[id]=c end
 return c end
local function slab(o,d,h) local t0,t1=-math.huge,math.huge
 for _,ax in {'X','Y','Z'} do local oo,dd,hh=o[ax],d[ax],h[ax]
  if math.abs(dd)<1e-9 then if math.abs(oo)>hh then return nil end else
   local a,b=(-hh-oo)/dd,(hh-oo)/dd if a>b then a,b=b,a end t0=math.max(t0,a) t1=math.min(t1,b) if t0>t1 then return nil end end end
 if t1<0 then return nil end return math.max(t0,0) end
local tp=RaycastParams.new() tp.FilterType=Enum.RaycastFilterType.Include tp.FilterDescendantsInstances={workspace.Terrain}
local rep={meshFail={}}
for _,q in Q do local hits={}
 for _,pt in q.pts do
  local o=Vector3.new(pt[1],pt[2],pt[3]) local dir=Vector3.new(0,-200,0)
  local best,bp,felt=nil,nil,false
  local th=workspace:Raycast(o,dir,tp) if th then best=th.Position.Y bp='Terrain' end
  for _,c in parts do if o.X>=c.lo.X and o.X<=c.hi.X and o.Z>=c.lo.Z and o.Z<=c.hi.Z and c.lo.Y<=o.Y and (not best or c.hi.Y>best) then
   local p=c.p local y
   if p:IsA('MeshPart') then local m=mesh(p)
    if m then local sc=p.Size/m.size
     local lo=p.CFrame:PointToObjectSpace(o)/sc+m.ctr local ld=p.CFrame:VectorToObjectSpace(dir)/sc
     local _,hp=m.e:RaycastLocal(lo,ld) if hp then y=(p.CFrame*((hp-m.ctr)*sc)).Y end
    else rep.meshFail[p.MeshId]=p:GetFullName() end
   else local t=slab(p.CFrame:PointToObjectSpace(o),p.CFrame:VectorToObjectSpace(dir),p.Size/2) if t then y=o.Y-200*t end end
   if y and y<=o.Y and (not best or y>best) then best=y bp=p:GetFullName() felt=p:HasTag('GolfSurface') end end end
  table.insert(hits,best and {best,bp,felt} or false) end
 rep[tostring(q.id)]=hits end
for _,c in cache do if c then c.e:Destroy() end end
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''


def trueground(s, queries, skip='{}'):
    out = {}; fails = {}
    for k in range(0, len(queries), 60):
        raw = fetch(s, '_G.SC5Out', TRUEGROUND.replace('__Q__', to_lua(queries[k:k + 60])).replace('__SKIP__', skip), timeout=1200)
        r = json.loads(raw); fails.update(r.pop('meshFail') or {}); out.update(r)
    if fails: print('TRUEGROUND mesh load failures:', fails)
    return out


LOOK7 = r'''
local rep={}
for _,f in workspace.CourseSugarloaf.Look7Dressing:GetChildren() do for _,m in f:GetChildren() do
 local c=m.WorldPivot local rx,ry,rz=c:ToOrientation()
 rep[tostring(m:GetAttribute('SC9LayoutIndex'))]={name=m.Name,folder=f.Name,stem=m:GetAttribute('SC9Stem'),pivot={c.X,c.Y,c.Z},yaw=math.deg(ry),rx=math.deg(rx),rz=math.deg(rz),parts=#m:GetChildren()} end end
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''

# Apply a plan: translate a piece (all MeshParts + WorldPivot, rotation kept) or delete it.
MOVE = r'''
local plan=__PLAN__
local dress=workspace.CourseSugarloaf.Look7Dressing
local by={} for _,f in dress:GetChildren() do for _,m in f:GetChildren() do by[m:GetAttribute('SC9LayoutIndex')]=m end end
local rep={moved={},deleted={},parts=0}
for _,e in plan do local m=assert(by[e.i],'piece '..e.i)
 if e.delete then rep.parts+=#m:GetChildren() table.insert(rep.deleted,{i=e.i,name=m.Name,reason=e.reason}) local f=m.Parent m:Destroy() if #f:GetChildren()==0 then f:Destroy() end
 else local d=Vector3.new(e.dx,e.dy,e.dz)
  for _,p in m:GetChildren() do if p:IsA('BasePart') then p.CFrame=p.CFrame+d end end
  m.WorldPivot=m.WorldPivot+d m:SetAttribute(e.tag,true)
  table.insert(rep.moved,{i=e.i,name=m.Name,d={e.dx,e.dy,e.dz},pivot={m.WorldPivot.X,m.WorldPivot.Y,m.WorldPivot.Z}}) end end
local left,lp=0,0 for _,d in dress:GetDescendants() do if d:IsA('Model') then left+=1 elseif d:IsA('BasePart') then lp+=1 end end
rep.left=left rep.leftParts=lp
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''


# ---- offline geometry (true mesh footprints) ----
def geom():
    return json.loads(GEOM.read_text())


def scales():
    return {o['i']: o['scale'] for o in json.loads(PLAN.read_text())['instances']}


def frame(piece, sc):
    """world(local xyz) for a piece from its live pivot/yaw and layout scale."""
    px, py, pz = piece['pivot']; a = math.radians(piece['yaw']); co, si = math.cos(a), math.sin(a)
    def w(x, y, z):
        x, y, z = x * sc[0], y * sc[1], z * sc[2]
        return (px + x * co + z * si, py + y, pz - x * si + z * co)
    return w


def footprint(piece, sc, G):
    """slot hulls (world XZ), lowest/highest world y, contact ring (world xyz)."""
    g = G[piece['stem']]; w = frame(piece, sc)
    hulls = [[(lambda q: (q[0], q[2]))(w(x, 0, z)) for x, z in s['hull']] for s in g['slots'].values()]
    lo = piece['pivot'][1] + g['minY'] * sc[1]
    hi = piece['pivot'][1] + max(s['maxY'] for s in g['slots'].values()) * sc[1]
    ring = [w(*b) for b in g['bottom']]
    return hulls, lo, hi, ring


def ground(s, queries, skip='{}'):
    out = {}
    for k in range(0, len(queries), 150):
        raw = fetch(s, '_G.SC5Out', GROUND.replace('__Q__', to_lua(queries[k:k + 150])).replace('__SKIP__', skip), timeout=900)
        out.update(json.loads(raw))
    return out


if __name__ == '__main__':
    a = sys.argv[1]
    s = studio()
    if a == 'probe':
        raw = fetch(s, '_G.SC5Out', PROBE); (OUT / 'probe.json').write_text(raw + '\n'); r = json.loads(raw)
        for k in ('rim', 'rimLib', 'board', 'boardLib'):
            for p in r[k]: print(k, p['path'].split('.')[-1], p['material'], p['color'], [round(x, 3) for x in p['pos']], [round(x, 3) for x in p['size']], p['castShadow'])
    elif a == 'rim':
        rp = json.loads(REPORT.read_text())['mesh_info']
        meshes = [{'name': k, 'center': v['center'], 'size': v['size']} for k, v in rp.items()]
        dry = '--dry' in sys.argv
        raw = fetch(s, '_G.SC5Out', RIM.replace('__MESHES__', to_lua(meshes)).replace('__DRY__', 'true' if dry else 'false'))
        (OUT / ('rim-dry.json' if dry else 'rim.json')).write_text(raw + '\n')
        r = json.loads(raw); print('k', r['kMin'], r['kMax'])
        for c in r['copies']:
            print(c['path'], len(c['oldParts']), '->', len(c['newParts']), c.get('backup'))
            for d in c['slotDelta']: print('   ', d)
            for n in c['newParts']: print('    ', n['name'], n['material'], n['color'], n['castShadow'], round(n['bottomY'], 4), n['texture'][-20:])
    elif a == 'board':
        raw = fetch(s, '_G.SC5Out', BOARD); (OUT / 'board.json').write_text(raw + '\n'); print(raw)
    elif a == 'look7':
        raw = fetch(s, '_G.SC5Out', LOOK7, timeout=600); (OUT / (sys.argv[2] + '.json')).write_text(raw + '\n'); print(len(json.loads(raw)))
    elif a == 'move':
        plan = json.loads(Path(sys.argv[2]).read_text())
        raw = fetch(s, '_G.SC5Out', MOVE.replace('__PLAN__', to_lua(plan)), timeout=900)
        Path(sys.argv[3]).write_text(raw + '\n'); r = json.loads(raw)
        print('moved', len(r['moved']), 'deleted', len(r['deleted']), 'parts', r['parts'], 'left', r['left'], r['leftParts'])
    elif a == 'lua':
        raw = fetch(s, '_G.SC5Out', Path(sys.argv[2]).read_text(), timeout=900)
        if len(sys.argv) > 3: Path(sys.argv[3]).write_text(raw + '\n')
        print(raw[:6000])
