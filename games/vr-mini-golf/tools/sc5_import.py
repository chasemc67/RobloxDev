"""Stage sc5: replace Sugarloaf visuals with the approved fix_zfight / fix_zfight2/3/4/6 meshes, once each.
Input: an imported bundle workspace.<bundle> (3D Importer, merged FBX from sc5_merge_fbx.py) and the merge report
(<bundle>_report.json: per-mesh Roblox-axis bounds relative to the source pivot).

Old parts are moved to ServerStorage.SC5Backup (not destroyed) so the pass can be reverted until verified.
The live copy may come from another export of the prop (props_batchN vs movers): the bound set with the smallest
spread is used. Frame = per-axis median scale, largest part's rotation, median position; when parts were nudged
one by one (spread > 0.02) and the model pivot agrees within 0.15, the builder-set pivot is the frame.
For every old prop stem P (fbx 'replaces' path), every Model in CourseSugarloaf / the ServerStorage libraries whose
direct BasePart children are named P__* is a copy. Its FBX-origin frame F is solved from the old parts' pre-separation
pose and the old FBX bounds: oldCF = F * (c*S) * Ry(pi).
New parts go to F * (c'*S) * Ry(pi) with size' * S (importer scale and half-turn undone from the FBX bounds), take
appearance from the old part with the same material suffix (else any part in the place with that suffix), keep
anchoring / mover welds / collision group, move lights and other children, and the old parts are destroyed.

  PYTHONPATH=tools python3 tools/sc5_import.py <bundle> <report.json> [group ...]
"""
import json, os, sys
from pathlib import Path
from sc5_util import studio, fetch, OUT
from holes_to_lua import to_lua

SRC = json.load(open('/tmp/sc5/sources2.json'))
OLD = json.load(open('/tmp/sc5/old_bounds.json'))
ALTS = json.load(open('/tmp/sc5/old_bounds_alts.json'))

LUA = r'''
local specs=__SPECS__
local bundleName=__BUNDLE__
assert(workspace:GetAttribute('PlaceRole')=='sugarloaf_canyon')
local bundle=assert(workspace:FindFirstChild(bundleName),'bundle missing')
local course=workspace.CourseSugarloaf
local roots={course}
for _,n in {'SugarloafKit','SugarloafMovers','StageAEProps','StageAFProps','StageAJProps'} do local f=game.ServerStorage:FindFirstChild(n) if f then table.insert(roots,f) end end
local imported={}
for _,d in bundle:GetDescendants() do if d:IsA('MeshPart') then
 local n=d.Name:gsub('%.%d+$','') if imported[n] then error('duplicate import '..n) end imported[n]=d end end
local RY=CFrame.Angles(0,math.pi,0)
local report={copies={},skipped={},flagged={},importCheck={},appearanceFallback={},lightsMoved=0,weldsRetargeted=0,oldPartsRemoved=0,newParts=0}
local backup=game.ServerStorage:FindFirstChild('SC5Backup') or Instance.new('Folder') backup.Name='SC5Backup' backup.Parent=game.ServerStorage
-- importer check: scale k and half-turn per mesh
local ks={}
for _,sp in specs do for _,n in sp.new do local ip=imported[n.name]
 if not ip then table.insert(report.skipped,'not imported '..n.name) else
  local k=n.size[1]>0.05 and ip.Size.X/n.size[1] or (n.size[3]>0.05 and ip.Size.Z/n.size[3] or ip.Size.Y/n.size[2]) table.insert(ks,k) end end end
table.sort(ks) report.importCheck.kMin=ks[1] report.importCheck.kMax=ks[#ks] report.importCheck.n=#ks
-- appearance by suffix from every MeshPart in the place
local global={}
for _,r in roots do for _,p in r:GetDescendants() do if p:IsA('MeshPart') then local suf=p.Name:match('__(.+)$')
 if suf and not global[suf] then global[suf]=p end end end end
local function suffix(n) return n:match('__(.+)$') end
local function copyLook(p,o)
 p.Color=o.Color p.Material=o.Material p.MaterialVariant=o.MaterialVariant p.Transparency=o.Transparency p.Reflectance=o.Reflectance
 p.CastShadow=o.CastShadow p.TextureID=o.TextureID
 for _,c in o:GetChildren() do if c:IsA('SurfaceAppearance') then c:Clone().Parent=p end end
end
local function median(t) table.sort(t) local n=#t if n==0 then return nil end if n%2==1 then return t[(n+1)/2] end return (t[n/2]+t[n/2+1])/2 end
-- robust frame of one copy: per-axis scale = median size ratio, rotation of the largest old part, position = median
local function solve(olds,bounds)
 local rx,ry,rz={},{},{}
 local big,bigV
 for _,o in olds do local b=bounds[o.Name] if b then
  if b.size[1]>0.3 then table.insert(rx,o.Size.X/b.size[1]) end
  if b.size[2]>0.3 then table.insert(ry,o.Size.Y/b.size[2]) end
  if b.size[3]>0.3 then table.insert(rz,o.Size.Z/b.size[3]) end
  local v=b.size[1]*b.size[2]*b.size[3] if not bigV or v>bigV then big,bigV=o,v end end end
 if not big then return nil end
 local sx,sy,sz=median(rx),median(ry),median(rz)
 local any=sx or sy or sz or 1
 local function snap(v) return math.abs(v-1)<0.02 and 1 or v end
 local S=Vector3.new(snap(sx or any),snap(sy or any),snap(sz or any))
 local R=(big.CFrame*RY:Inverse()).Rotation
 local px,py,pz,pts={}, {}, {}, {}
 for _,o in olds do local b=bounds[o.Name] if b then
  local c=Vector3.new(table.unpack(b.center))*S
  local fp=o.Position-R:VectorToWorldSpace(c)
  table.insert(px,fp.X) table.insert(py,fp.Y) table.insert(pz,fp.Z) table.insert(pts,{o.Name,fp}) end end
 local P=Vector3.new(median(px),median(py),median(pz))
 local spread,worst=0,nil
 for _,q in pts do local d=(q[2]-P).Magnitude if d>spread then spread,worst=d,q[1] end end
 return CFrame.new(P)*R,S,spread,worst
end
local DRY=__DRY__
local done=0
for _,sp in specs do
 local P=sp.old
 local copies={}
 for _,r in roots do for _,m in r:GetDescendants() do
  if (m:IsA('Model') or m:IsA('Folder')) and m~=bundle and not m:IsDescendantOf(bundle) then
   for _,c in m:GetChildren() do if c:IsA('BasePart') and c.Name:sub(1,#P+2)==P..'__' and not c:GetAttribute('SC5New') then table.insert(copies,m) break end end
  end end end
 if #copies==0 then table.insert(report.skipped,'no copies of '..P) end
 for _,m in copies do
  local olds={}
  for _,c in m:GetChildren() do if c:IsA('BasePart') and c.Name:sub(1,#P+2)==P..'__' and not c:GetAttribute('SC5New') then table.insert(olds,c) end end
  -- the live copy may come from another export of the same prop: pick the bound set with the smallest spread
  local F,S,spread,worst,boundsFbx
  local best
  for _,alt in sp.altBounds do local f,s2,sp2,w2=solve(olds,alt.parts)
   -- ties (several exports fit) go to the one that needs the least scaling
   local score=f and sp2+0.5*math.max(math.abs(s2.X-1),math.abs(s2.Y-1),math.abs(s2.Z-1))
   if f and (not best or score<best) then best=score F,S,spread,worst,boundsFbx=f,s2,sp2,w2,alt.fbx end end
  if not F then table.insert(report.skipped,'no frame '..m:GetFullName()) continue end
  -- parts nudged one by one (zf1 separation): the builder-set model pivot is the FBX origin when it agrees
  local frameFrom='parts'
  if spread>0.02 and m:IsA('Model') then
   local pv=m:GetPivot()
   if (pv.Position-F.Position).Magnitude<=0.2 and pv.Rotation:FuzzyEq(F.Rotation,1e-3) then F=pv frameFrom='pivot' end
  end
  if spread>0.15 and frameFrom~='pivot' then table.insert(report.flagged,{path=m:GetFullName(),spread=spread,worst=worst}) end
  if DRY then table.insert(report.copies,{path=m:GetFullName(),old=P,scale={S.X,S.Y,S.Z},spread=spread,worst=worst,oldParts=#olds,
    frameFrom=frameFrom,boundsFbx=boundsFbx,pivotDelta=m:IsA('Model') and (m:GetPivot().Position-F.Position).Magnitude or -1}) continue end
  local byS={} for _,o in olds do byS[suffix(o.Name)]=o end
  local anyOld=olds[1]
  local weldTo
  for _,o in olds do for _,w in o:GetChildren() do if w:IsA('WeldConstraint') and w.Part0 and w.Part0~=o and not table.find(olds,w.Part0) then weldTo=w.Part0 end end end
  local news={}
  for _,n in sp.new do
   local ip=imported[n.name] if not ip then continue end
   local p=ip:Clone()
   for _,c in p:GetChildren() do c:Destroy() end
   p.Name=n.name
   p.Size=Vector3.new(table.unpack(n.size))*S
   p.CFrame=F*CFrame.new(Vector3.new(table.unpack(n.center))*S)*RY
   local suf=suffix(n.name)
   local o=byS[suf] or (sp.lookFrom and sp.lookFrom[suf] and byS[sp.lookFrom[suf]])
   if o then copyLook(p,o) elseif global[suf] then copyLook(p,global[suf]) table.insert(report.appearanceFallback,n.name..' <- '..global[suf]:GetFullName())
   else table.insert(report.appearanceFallback,n.name..' <- importer default') end
   if suf:match('^Neon') then p.Material=Enum.Material.Neon p.CastShadow=false end
   p.Anchored=anyOld.Anchored p.Massless=anyOld.Massless p.CollisionGroup=anyOld.CollisionGroup
   p.CanCollide=false p.CanQuery=false p.CanTouch=false
   pcall(function() p.CollisionFidelity=Enum.CollisionFidelity.Box end)
   for k,v in anyOld:GetAttributes() do if k:sub(1,3)~='ZF1' then p:SetAttribute(k,v) end end
   p:SetAttribute('SC5New',true) p:SetAttribute('SC5Source',sp.src[n.stem] or n.stem)
   if weldTo then local w=Instance.new('WeldConstraint') w.Part0=weldTo w.Part1=p w.Parent=p end
   p.Parent=m news[suf]=news[suf] or p table.insert(news,p) report.newParts+=1
  end
  -- children of old parts (lights, attachments, emitters) -> same suffix, else first Neon, else largest
  local largest for _,p in ipairs(news) do if not largest or p.Size.Magnitude>largest.Size.Magnitude then largest=p end end
  for _,o in olds do for _,c in o:GetChildren() do
   if not c:IsA('WeldConstraint') and not c:IsA('SurfaceAppearance') then
    local t=news[suffix(o.Name)] if not t then for _,q in ipairs(news) do if q.Material==Enum.Material.Neon then t=q break end end end
    t=t or largest if t then c.Parent=t report.lightsMoved+=1 end
   end end end
  -- constraints elsewhere that point at an old part
  for _,o in olds do for _,w in m:GetDescendants() do
   if (w:IsA('WeldConstraint') or w:IsA('Weld')) and not table.find(olds,w.Parent) then
    if w.Part0==o then w.Part0=largest report.weldsRetargeted+=1 end
    if w.Part1==o then w.Part1=largest report.weldsRetargeted+=1 end
   end end end
  -- old parts go to ServerStorage.SC5Backup (deleted only after verification), not destroyed
  local bk=Instance.new('Folder') bk.Name=tostring(#report.copies+1) bk:SetAttribute('OrigPath',m:GetFullName())
  local oldNames={} for _,o in olds do table.insert(oldNames,o.Name) o.Parent=bk report.oldPartsRemoved+=1 end
  bk.Parent=backup
  m:SetAttribute('SC5Replaced',P)
  table.insert(report.copies,{path=m:GetFullName(),old=P,scale={S.X,S.Y,S.Z},spread=spread,worst=worst,frameFrom=frameFrom,boundsFbx=boundsFbx,oldParts=#oldNames,newParts=#news,
   frame={F:GetComponents()},pivotDelta=m:IsA('Model') and (m:GetPivot().Position-F.Position).Magnitude or -1})
  done+=1 if done%10==0 then task.wait() end
 end
end
for _,p in workspace:GetDescendants() do if p:GetAttribute('SC5New') then p:SetAttribute('SC5New',nil) end end
for _,r in roots do for _,p in r:GetDescendants() do if p:GetAttribute('SC5New') then p:SetAttribute('SC5New',nil) end end end
_G.SC5Out=game.HttpService:JSONEncode(report) return #_G.SC5Out
'''


def specs_for(report, groups):
    info = json.load(open(report))['mesh_info']
    by_old = {}
    for s in SRC:
        if s['group'] not in groups or not s.get('oldStem'):
            continue
        P = s['oldStem']
        sp = by_old.setdefault(P, dict(old=P, altBounds=ALTS[P], new=[], src={}))
        sp['src'][s['stem']] = s['fbx']
        for name, m in info.items():
            if m['stem'] == s['stem']:
                sp['new'].append(dict(name=name, stem=s['stem'], center=m['center'], size=m['size']))
    return list(by_old.values())


if __name__ == '__main__':
    bundle, report = sys.argv[1], sys.argv[2]
    dry = '--dry' in sys.argv
    groups = ''.join(a for a in sys.argv[3:] if not a.startswith('--')) or 'ABC'
    specs = specs_for(report, groups)
    s = studio()
    code = LUA.replace('__SPECS__', to_lua(specs)).replace('__BUNDLE__', json.dumps(bundle)).replace('__DRY__', 'true' if dry else 'false')
    raw = fetch(s, '_G.SC5Out', code, timeout=1200)
    out = OUT / ('import-' + bundle + ('-dry' if dry else '') + '.json'); out.write_text(raw + '\n')
    r = json.loads(raw)
    print({k: (len(v) if isinstance(v, list) else v) for k, v in r.items()})
    print('skipped', r['skipped'][:30])
    print('flagged', r['flagged'])
    print('frameFrom', {k: sum(1 for c in r['copies'] if c.get('frameFrom') == k) for k in ('parts', 'pivot')})
