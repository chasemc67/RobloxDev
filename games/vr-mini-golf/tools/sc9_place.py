"""Stage sc9: Sugarloaf Canyon look7 dressing edgefix4 -> v49fix_thin60 + LODs.
  PYTHONPATH=tools python3 tools/sc9_place.py probe                 (Look7Dressing / SC7Kit / tee markers / view settings)
  PYTHONPATH=tools python3 tools/sc9_place.py remove                (delete Look7Dressing + SC7Kit templates the new layout doesn't use)
  PYTHONPATH=tools python3 tools/sc9_place.py lodtemplates <bundle> (one template per LOD mesh -> ServerStorage.SC9LODKit)
  PYTHONPATH=tools python3 tools/sc9_place.py dressing              (plan.json -> Workspace.CourseSugarloaf.Look7Dressing)
  PYTHONPATH=tools python3 tools/sc9_place.py float                 (rule c, per piece -> float.json)
  PYTHONPATH=tools python3 tools/sc9_place.py delete                (delete every piece that failed a rule -> dressing-check.json)
Placement (models/manifest.json, as sc7): root = CFrame.new(pos + SugarloafLayout.offset) * Angles(0, rad(yaw), 0); `scale`
per local axis on every MeshPart Size and its offset from the pivot. Mesh centres/sizes come from the merge reports (Roblox axes,
relative to the FBX pivot); the 3D Importer bakes a Y half-turn (undone with RY). Source meshes reuse the SC7Kit templates (the
21 source FBX files are byte-identical to the ones sc7 imported); LOD meshes come from one new import (SC9LODKit).
The LOD choice and the felt / rail rules come from tools/sc9_plan.py (true mesh footprints, offline).
"""
import json, sys
from pathlib import Path
from sc5_util import studio, fetch, GAME
from holes_to_lua import to_lua

OUT = GAME / 'playtests/stage-sc9'
FBX = Path('/Users/chase-mini/src/RobloxDev/assets/vr-mini-golf/sugarloaf-canyon/models/fbx')
LAYOUT = FBX / 'look7_dressing/layout_look7_dressing_v49fix_thin60.json'
REPORTS = ['/tmp/sc7/sc7_K_report.json', '/Users/chase-mini/sc9imp/sc9_LOD_report.json']
PLAN = Path('/tmp/sc9/plan.json')
GEOM = Path('/tmp/sc9/geom.json')

PROBE = r'''
local course=workspace.CourseSugarloaf
local r={look7={models=0,parts=0,byPiece={}},kit={},tees={},view={}}
local f=course:FindFirstChild('Look7Dressing')
if f then for _,d in f:GetDescendants() do if d:IsA('Model') then r.look7.models+=1 local n=d.Name:gsub('_%d+$','') r.look7.byPiece[n]=(r.look7.byPiece[n] or 0)+1
 elseif d:IsA('BasePart') then r.look7.parts+=1 end end end
local kit=game.ServerStorage:FindFirstChild('SC7Kit')
if kit then for _,c in kit:GetChildren() do table.insert(r.kit,c.Name) end end
for i=1,18 do local h=course:FindFirstChild('Hole'..i) local t=h and (h:FindFirstChild('Tee',true) or h:FindFirstChild('TeePad',true))
 table.insert(r.tees,{hole=i,tee=t and t:GetFullName() or false,pos=t and t:IsA('BasePart') and {t.Position.X,t.Position.Y,t.Position.Z} or false,
  pivot=h and {h:GetPivot().X,h:GetPivot().Y,h:GetPivot().Z} or false}) end
local L=game.Lighting local atm=L:FindFirstChildOfClass('Atmosphere')
r.view={streaming=workspace.StreamingEnabled,fogEnd=L.FogEnd,fogStart=L.FogStart,atmosphere=atm and {density=atm.Density,haze=atm.Haze,offset=atm.Offset} or false}
_G.SC5Out=game.HttpService:JSONEncode(r) return #_G.SC5Out
'''

REMOVE = r'''
local keep=__KEEP__
local course=workspace.CourseSugarloaf
local r={look7Models=0,look7Parts=0,look7Folders=0,kitRemoved={},kitKept={}}
local f=course:FindFirstChild('Look7Dressing')
if f then
 for _,d in f:GetDescendants() do if d:IsA('Model') then r.look7Models+=1 elseif d:IsA('BasePart') then r.look7Parts+=1 end end
 r.look7Folders=#f:GetChildren()
 for _,sub in f:GetChildren() do sub:Destroy() task.wait() end
 f:Destroy()
end
local kit=game.ServerStorage.SC7Kit
local want={} for _,n in keep do want[n]=true end
-- a template is "used" if the new layout needs it, or anything else references its Name as a piece outside the kit
for _,c in kit:GetChildren() do if want[c.Name] then table.insert(r.kitKept,c.Name) else table.insert(r.kitRemoved,c.Name) c:Destroy() end end
_G.SC5Out=game.HttpService:JSONEncode(r) return #_G.SC5Out
'''

LODTEMPLATES = r'''
local meshes=__MESHES__
local bundle=assert(workspace:FindFirstChild(__BUNDLE__),'bundle missing')
local src=game.ServerStorage.SC7Kit
local RY=CFrame.Angles(0,math.pi,0)
local imported={}
for _,d in bundle:GetDescendants() do if d:IsA('MeshPart') then local n=d.Name:gsub('%.%d+$','')
 if imported[n] then error('duplicate import '..n) end imported[n]=d end end
local kit=game.ServerStorage:FindFirstChild('SC9LODKit') if kit then kit:Destroy() end
kit=Instance.new('Folder') kit.Name='SC9LODKit'
local rep={templates={},missing={},kScale={}}
for _,n in meshes do
 local ip=imported[n.name]
 local sname=n.name:gsub('_lod__','__')
 local o=src:FindFirstChild(sname)
 if not ip or not o then table.insert(rep.missing,n.name..(ip and '' or ' (not imported)')..(o and '' or ' (no source template)')) continue end
 table.insert(rep.kScale,n.size[1]>0.05 and ip.Size.X/n.size[1] or ip.Size.Z/n.size[3])
 local p=ip:Clone() for _,c in p:GetChildren() do c:Destroy() end
 p.Name=n.name p.Size=Vector3.new(table.unpack(n.size)) p.CFrame=CFrame.new(Vector3.new(table.unpack(n.center)))*RY
 -- same slot appearance as the source template; texture: the LOD's own importer texture (matches its UVs) when it has one,
 -- else the source template's (e.g. the shared Strata texture) -- the sc7 rule
 p.Color=o.Color p.Material=o.Material p.MaterialVariant=o.MaterialVariant p.Transparency=o.Transparency p.Reflectance=o.Reflectance
 p.CastShadow=o.CastShadow
 local own=ip.TextureID if own=='' then p.TextureID=o.TextureID end
 for _,c in o:GetChildren() do if c:IsA('SurfaceAppearance') then c:Clone().Parent=p end end
 for k,v in o:GetAttributes() do if k~='SC7Source' then p:SetAttribute(k,v) end end
 p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false p.Massless=true
 p:SetAttribute('VisualQueryDisabled',true) p:SetAttribute('SC9Source',n.src) p:SetAttribute('SC9LODOf',sname)
 p.Parent=kit
 table.insert(rep.templates,{name=n.name,source=sname,material=p.Material.Name,color={p.Color.R,p.Color.G,p.Color.B},transparency=p.Transparency,
  castShadow=p.CastShadow,texture=p.TextureID,textureFrom=own~='' and 'lod importer' or 'source template',sourceTexture=o.TextureID,meshId=p.MeshId})
end
kit.Parent=game.ServerStorage
table.sort(rep.kScale) rep.kMin=rep.kScale[1] rep.kMax=rep.kScale[#rep.kScale] rep.kScale=nil
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''

DRESSING = r'''
local pieces=__PIECES__
local inst=__INST__
local course=workspace.CourseSugarloaf
local lay=require(game.ServerStorage.CourseData.SugarloafLayout:Clone())
local off=Vector3.new(table.unpack(lay.offset))
local RY=CFrame.Angles(0,math.pi,0)
local kits={game.ServerStorage.SC7Kit,game.ServerStorage.SC9LODKit}
local function tmpl(n) for _,k in kits do local t=k:FindFirstChild(n) if t then return t end end error('template '..n) end
assert(not course:FindFirstChild('Look7Dressing'),'remove first')
local folder=Instance.new('Folder') folder.Name='Look7Dressing'
folder:SetAttribute('SC9Layout','look7_dressing/layout_look7_dressing_v49fix_thin60.json')
folder.Parent=course
local rep={placed=0,parts=0,lod=0,byStem={},fidelity={}}
local sub={}
local batch={}
local function flush() for _,m in batch do m[1].Parent=m[2] end batch={} task.wait() end
for i,e in inst do
 local f=sub[e.piece] if not f then f=Instance.new('Folder') f.Name=e.piece f.Parent=folder sub[e.piece]=f end
 local m=Instance.new('Model') m.Name=e.piece..'_'..e.i
 local root=CFrame.new(Vector3.new(table.unpack(e.pos))+off)*CFrame.Angles(0,math.rad(e.yaw),0)
 local s=Vector3.new(table.unpack(e.scale))
 for _,n in assert(pieces[e.stem],'stem '..e.stem) do
  local p=tmpl(n.name):Clone()
  p.Size=Vector3.new(table.unpack(n.size))*s
  p.CFrame=root*CFrame.new(Vector3.new(table.unpack(n.center))*s)*RY
  p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false p.Massless=true
  pcall(function() p.CollisionFidelity=Enum.CollisionFidelity.Box end)
  local ok=pcall(function() p.RenderFidelity=Enum.RenderFidelity.Automatic end)
  rep.fidelity[ok and 'set' or 'failed']=(rep.fidelity[ok and 'set' or 'failed'] or 0)+1
  p:SetAttribute('VisualQueryDisabled',true)
  p.Parent=m
 end
 m.WorldPivot=root
 m:SetAttribute('SC9LayoutIndex',e.i) m:SetAttribute('SC9Src',e.src) m:SetAttribute('SC9Stem',e.stem)
 m:SetAttribute('SC9LOD',e.lod) m:SetAttribute('SC9TeeDist',e.teeDist) m:SetAttribute('SC9NearestHole',e.nearestHole)
 table.insert(batch,{m,f})
 rep.placed+=1 rep.parts+=#m:GetChildren() if e.lod then rep.lod+=1 end
 rep.byStem[e.stem]=(rep.byStem[e.stem] or 0)+1
 if #batch>=60 then flush() end
end
flush()
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''

# Rule (c): for each piece, its contact ring = the stem's lowest vertices (sc9_mesh_geom.py `bottom`, within 0.05 of the
# lowest point), transformed with the instance frame. Ground = Terrain + every visible (Transparency < 1) BasePart that is
# not Look7 dressing. Visual ground tiles have CanQuery off, so CanQuery is turned on for those parts for the duration of
# the check (same call, no yield) and restored exactly. Ray from 5 above the lowest point straight down 200.
# gap = lowest point - ground hit; the piece floats when EVERY ring point's gap > 0.1 (no hit = floating).
FLOAT = r'''
local rings=__RINGS__
local course=workspace.CourseSugarloaf
local dress=course.Look7Dressing
local lay=require(game.ServerStorage.CourseData.SugarloafLayout:Clone())
local off=Vector3.new(table.unpack(lay.offset))
local saved={} local ground={workspace.Terrain}
for _,p in workspace:GetDescendants() do if p:IsA('BasePart') and not p:IsDescendantOf(dress) and p.Transparency<1 then
 table.insert(ground,p) if not p.CanQuery then saved[p]=true p.CanQuery=true end end end
local rp=RaycastParams.new() rp.FilterType=Enum.RaycastFilterType.Include rp.FilterDescendantsInstances=ground
local rep={pieces={},toggled=0}
for _ in saved do rep.toggled+=1 end
local ok,err=pcall(function()
 for _,f in dress:GetChildren() do for _,m in f:GetChildren() do
  local stem=m:GetAttribute('SC9Stem') local ring=rings[stem]
  local root=m.WorldPivot local sc=Vector3.new(1,1,1)
  local i=m:GetAttribute('SC9LayoutIndex')
  local e=rings.__scale[tostring(i)] if e then sc=Vector3.new(table.unpack(e)) end
  local lowY=(root*Vector3.new(0,ring.minY*sc.Y,0)).Y
  local best,bestPart,hits,n=math.huge,false,0,0
  for _,b in ring.bottom do
   local w=root*Vector3.new(b[1]*sc.X,b[2]*sc.Y,b[3]*sc.Z)
   local h=workspace:Raycast(Vector3.new(w.X,lowY+5,w.Z),Vector3.new(0,-200,0),rp) n+=1
   if h then hits+=1 local g=lowY-h.Position.Y if g<best then best=g bestPart=h.Instance==workspace.Terrain and 'Terrain' or h.Instance:GetFullName() end end
  end
  table.insert(rep.pieces,{i=i,name=m.Name,lowY=lowY,gap=best<math.huge and best or false,ground=bestPart,samples=n,hits=hits})
 end end
end)
for p in saved do p.CanQuery=false end
assert(ok,err)
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''

DELETE = r'''
local ids=__IDS__
local dress=workspace.CourseSugarloaf.Look7Dressing
local want={} for _,i in ids do want[i]=true end
local rep={deleted={},parts=0}
for _,f in dress:GetChildren() do for _,m in f:GetChildren() do
 local i=m:GetAttribute('SC9LayoutIndex') if want[i] then rep.parts+=#m:GetChildren() table.insert(rep.deleted,m.Name) m:Destroy() end end
 if #f:GetChildren()==0 then f:Destroy() end end
local left,lp=0,0 for _,d in dress:GetDescendants() do if d:IsA('Model') then left+=1 elseif d:IsA('BasePart') then lp+=1 end end
rep.left=left rep.leftParts=lp
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''


def meshes_by_stem():
    by = {}
    for r in REPORTS:
        for name, m in json.load(open(r))['mesh_info'].items():
            by.setdefault(m['stem'], []).append(dict(name=name, center=m['center'], size=m['size'], tris=m['tris']))
    return by


if __name__ == '__main__':
    a = sys.argv[1]
    s = studio()
    if a == 'probe':
        raw = fetch(s, '_G.SC5Out', PROBE); (OUT / 'probe.json').write_text(raw + '\n'); print(json.dumps(json.loads(raw))[:4000])
    elif a == 'remove':
        L = json.loads(LAYOUT.read_text()); by = meshes_by_stem()
        keep = sorted(m['name'] for p in {e['piece'] for e in L['instances']} for m in by[p])
        raw = fetch(s, '_G.SC5Out', REMOVE.replace('__KEEP__', to_lua(keep)), timeout=1800)
        (OUT / 'remove.json').write_text(raw + '\n'); r = json.loads(raw)
        print({k: (len(v) if isinstance(v, list) else v) for k, v in r.items()}); print('removed', r['kitRemoved'])
    elif a == 'lodtemplates':
        by = meshes_by_stem()
        srcs = {x['stem']: x['fbx'].split('/models/fbx/')[1] for x in json.load(open('/tmp/sc9/list.json'))}
        meshes = [dict(m, src=srcs[k]) for k, v in by.items() if k.endswith('_lod') for m in v]
        raw = fetch(s, '_G.SC5Out', LODTEMPLATES.replace('__MESHES__', to_lua(meshes)).replace('__BUNDLE__', json.dumps(sys.argv[2])))
        (OUT / 'lod-templates.json').write_text(raw + '\n'); r = json.loads(raw)
        print('templates', len(r['templates']), 'missing', r['missing'], 'k', r['kMin'], r['kMax'])
        for t in r['templates']: print(t['name'], t['material'], t['textureFrom'], t['texture'][-16:], t['castShadow'])
    elif a == 'dressing':
        by = meshes_by_stem(); P = json.loads(PLAN.read_text())['instances']
        inst = [dict(i=e['i'], piece=e['piece'], stem=e['stem'], lod=e['lod'], pos=e['pos'], yaw=e['yaw'], scale=e['scale'], src=e['src'],
                     teeDist=e['teeDist'], nearestHole=e['nearestHole']) for e in P]
        pieces = {k: [dict(name=m['name'], center=m['center'], size=m['size']) for m in by[k]] for k in {e['stem'] for e in inst}}
        raw = fetch(s, '_G.SC5Out', DRESSING.replace('__PIECES__', to_lua(pieces)).replace('__INST__', to_lua(inst)), timeout=1800)
        (OUT / 'dressing.json').write_text(raw + '\n'); print(json.loads(raw))
    elif a == 'float':
        G = json.loads(GEOM.read_text()); P = json.loads(PLAN.read_text())['instances']
        rings = {k: dict(minY=v['minY'], bottom=v['bottom']) for k, v in G.items()}
        rings['__scale'] = {str(e['i']): e['scale'] for e in P if e['scale'] != [1, 1, 1]}
        raw = fetch(s, '_G.SC5Out', FLOAT.replace('__RINGS__', to_lua(rings)), timeout=1800)
        (OUT / 'float.json').write_text(raw + '\n'); r = json.loads(raw)
        fl = [p for p in r['pieces'] if p['gap'] is False or p['gap'] > 0.1]
        print('pieces', len(r['pieces']), 'toggled', r['toggled'], 'float', len(fl))
        for p in sorted(fl, key=lambda p: -(p['gap'] or 99))[:40]: print(' ', p)
    elif a == 'delete':
        ids = json.loads(sys.argv[2])
        raw = fetch(s, '_G.SC5Out', DELETE.replace('__IDS__', to_lua(ids)))
        (OUT / 'delete.json').write_text(raw + '\n'); r = json.loads(raw); print(len(r['deleted']), r['parts'], r['left'], r['leftParts'])
