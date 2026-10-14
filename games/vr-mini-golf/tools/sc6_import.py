"""Stage sc6: swap in fit030 (Sugarloaf ground tile sets, h02/h09/h11/h13 dress props), whole sets, once each.
Input: imported bundles workspace.<bundle> (3D Importer, merged FBX from sc5_merge_fbx.py --split-materials) and
their merge reports (per-mesh Roblox-axis bounds relative to the FBX pivot).

Frame per copy, from fit030/kit_fitcheck_030.json (no guessing): Workspace copies sit at the fitcheck pos +
SugarloafLayout.offset, identity rotation, minus 0.08 on even holes (the sc5 ground drop); ServerStorage library
copies sit at the origin. Before replacing, the frame is checked against the old parts (old FBX bounds from the
sc5 merge reports, oldCF = F * c * Ry(pi)); a copy whose old parts do not fit within 0.05 (median) is skipped.
A ground set replaces EVERY hNN_ground_sXX__* part of the copy (no mixing); a dress set every hNN_dress_props__*.
Appearance comes from the old part with the same name/suffix. Old parts go to ServerStorage.SC6Backup.

  PYTHONPATH=tools python3 tools/sc6_import.py <bundle> <report.json> [--dry]
"""
import json, sys
from pathlib import Path
from sc5_util import studio, fetch, GAME
from holes_to_lua import to_lua

OUT = GAME / 'playtests/stage-sc6'
FIT = Path('/Users/chase-mini/src/RobloxDev/assets/vr-mini-golf/sugarloaf-canyon/models/fbx/fit030')
OLD_REPORTS = ['/tmp/sc5/sc5_A_report.json', '/tmp/sc5/sc5_B1_report.json', '/tmp/sc5/sc5_B2_report.json']
DROP = 0.08

LUA = r'''
local specs=__SPECS__
local bundleName=__BUNDLE__
local DRY=__DRY__
local DROP=__DROPV__
assert(workspace:GetAttribute('PlaceRole')=='sugarloaf_canyon')
local bundle=assert(workspace:FindFirstChild(bundleName),'bundle missing')
local course=workspace.CourseSugarloaf
local lay=require(game.ServerStorage.CourseData.SugarloafLayout:Clone())
local off=Vector3.new(table.unpack(lay.offset))
local roots={course}
for _,n in {'SugarloafKit','SugarloafMovers','StageAEProps','StageAFProps','StageAJProps'} do local f=game.ServerStorage:FindFirstChild(n) if f then table.insert(roots,f) end end
local imported={}
for _,d in bundle:GetDescendants() do if d:IsA('MeshPart') then
 local n=d.Name:gsub('%.%d+$','') if imported[n] then error('duplicate import '..n) end imported[n]=d end end
local RY=CFrame.Angles(0,math.pi,0)
local report={copies={},skipped={},importCheck={},appearanceFallback={},lightsMoved=0,oldPartsRemoved=0,newParts=0}
local backup=game.ServerStorage:FindFirstChild('SC6Backup') or Instance.new('Folder') backup.Name='SC6Backup' backup.Parent=game.ServerStorage
local ks={}
for _,sp in specs do for _,n in sp.new do local ip=imported[n.name]
 if not ip then table.insert(report.skipped,'not imported '..n.name) else
  local k=n.size[1]>0.05 and ip.Size.X/n.size[1] or ip.Size.Z/n.size[3] table.insert(ks,k) end end end
table.sort(ks) report.importCheck.kMin=ks[1] report.importCheck.kMax=ks[#ks] report.importCheck.n=#ks
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
local function isOld(c,sp) return c:IsA('BasePart') and c.Name:match(sp.pattern)~=nil and not c:GetAttribute('SC6New') end
for _,sp in specs do
 local copies={}
 for _,r in roots do for _,m in r:GetDescendants() do
  if (m:IsA('Model') or m:IsA('Folder')) and not m:IsDescendantOf(bundle) and not m:IsDescendantOf(backup) then
   for _,c in m:GetChildren() do if isOld(c,sp) then table.insert(copies,m) break end end
  end end end
 if #copies==0 then table.insert(report.skipped,'no copies of '..sp.name) end
 for _,m in copies do
  local olds={} for _,c in m:GetChildren() do if isOld(c,sp) then table.insert(olds,c) end end
  local ws=m:IsDescendantOf(workspace)
  local F=ws and CFrame.new(Vector3.new(table.unpack(sp.pos))+off-Vector3.new(0,sp.even and DROP or 0,0)) or CFrame.new()
  -- verify the frame against the old parts (old FBX bounds)
  local dev,devY,rotBad,matched={}, {}, 0, 0
  for _,o in olds do local b=sp.oldBounds[o.Name] if b then matched+=1
   local want=F*CFrame.new(Vector3.new(table.unpack(b.center)))*RY
   table.insert(dev,(o.Position-want.Position).Magnitude) table.insert(devY,o.Position.Y-want.Position.Y)
   if not o.CFrame.Rotation:FuzzyEq(want.Rotation,1e-3) then rotBad+=1 end end end
  local med=median(dev) or 99
  local row={path=m:GetFullName(),spec=sp.name,workspace=ws,frame={F:GetComponents()},oldParts=#olds,matched=matched,
   medianDev=med,maxDev=dev[#dev],medianDevY=median(devY),rotMismatch=rotBad}
  if med>0.05 or rotBad>0 then row.error='frame does not fit old parts' table.insert(report.skipped,row) continue end
  if DRY then table.insert(report.copies,row) continue end
  local byName,byS={},{} for _,o in olds do byName[o.Name]=o byS[suffix(o.Name)]=byS[suffix(o.Name)] or o end
  local anyOld=olds[1]
  local news={}
  for _,n in sp.new do
   local ip=imported[n.name] if not ip then continue end
   local p=ip:Clone() for _,c in p:GetChildren() do c:Destroy() end
   p.Name=n.name p.Size=Vector3.new(table.unpack(n.size))
   p.CFrame=F*CFrame.new(Vector3.new(table.unpack(n.center)))*RY
   local suf=suffix(n.name)
   local o=byName[n.name] or byS[suf]
   if o then copyLook(p,o) elseif global[suf] then copyLook(p,global[suf]) table.insert(report.appearanceFallback,n.name..' <- '..global[suf]:GetFullName())
   else table.insert(report.appearanceFallback,n.name..' <- importer default') end
   if suf:match('^Neon') then p.Material=Enum.Material.Neon p.CastShadow=false end
   p.Anchored=anyOld.Anchored p.Massless=anyOld.Massless p.CollisionGroup=anyOld.CollisionGroup
   p.CanCollide=false p.CanQuery=false p.CanTouch=false
   pcall(function() p.CollisionFidelity=Enum.CollisionFidelity.Box end)
   for k,v in anyOld:GetAttributes() do if k:sub(1,3)~='ZF1' and k~='SC5Source' and k~='SC5GroundDrop' then p:SetAttribute(k,v) end end
   p:SetAttribute('SC6New',true) p:SetAttribute('SC6Source','fit030/'..n.stem..'.fbx')
   if ws and sp.even then p:SetAttribute('SC6GroundDrop',DROP) end
   p.Parent=m table.insert(news,p) report.newParts+=1
  end
  local largest for _,p in news do if not largest or p.Size.Magnitude>largest.Size.Magnitude then largest=p end end
  for _,o in olds do for _,c in o:GetChildren() do
   if not c:IsA('SurfaceAppearance') then local t=nil for _,q in news do if q.Name==o.Name then t=q break end end
    t=t or largest if t then c.Parent=t report.lightsMoved+=1 end end end end
  local bk=Instance.new('Folder') bk.Name=tostring(#report.copies+1) bk:SetAttribute('OrigPath',m:GetFullName())
  for _,o in olds do o.Parent=bk report.oldPartsRemoved+=1 end
  bk.Parent=backup
  m:SetAttribute('SC6Replaced',sp.name)
  row.newParts=#news table.insert(report.copies,row)
  task.wait()
 end
end
for _,r in roots do for _,p in r:GetDescendants() do if p:GetAttribute('SC6New') then p:SetAttribute('SC6New',nil) end end end
_G.SC5Out=game.HttpService:JSONEncode(report) return #_G.SC5Out
'''


def specs_for(report):
    info = json.load(open(report))['mesh_info']
    fc = {p['piece']: p for p in json.loads((FIT / 'kit_fitcheck_030.json').read_text())['per_instance']}
    old = {}
    for r in OLD_REPORTS:
        old.update(json.load(open(r))['mesh_info'])
    sets = {}
    for name, m in info.items():
        stem = m['stem']
        key = stem.rsplit('_s', 1)[0] if '_ground_s' in stem else stem   # h01_ground / h02_dress_props
        sets.setdefault(key, []).append(dict(name=name, stem=stem, center=m['center'], size=m['size']))
    specs = []
    for key, new in sorted(sets.items()):
        hole = int(key[1:3])
        pattern = '^%s_s%%d+__' % key if key.endswith('_ground') else '^%s__' % key
        ob = {k: dict(center=v['center']) for k, v in old.items()
              if (k.startswith(key + '_s') if key.endswith('_ground') else k.startswith(key + '__'))}
        specs.append(dict(name=key, pattern=pattern, pos=fc[key]['pos'], even=hole % 2 == 0, new=new, oldBounds=ob))
    return specs


if __name__ == '__main__':
    bundle, report = sys.argv[1], sys.argv[2]
    dry = '--dry' in sys.argv
    specs = specs_for(report)
    s = studio()
    code = (LUA.replace('__SPECS__', to_lua(specs)).replace('__BUNDLE__', json.dumps(bundle))
            .replace('__DRY__', 'true' if dry else 'false').replace('__DROPV__', str(DROP)))
    raw = fetch(s, '_G.SC5Out', code, timeout=1200)
    out = OUT / ('import-' + bundle + ('-dry' if dry else '') + '.json'); out.write_text(raw + '\n')
    r = json.loads(raw)
    print({k: (len(v) if isinstance(v, list) else v) for k, v in r.items()})
    for x in r['skipped']: print('SKIP', x)
    for c in r['copies']:
        print(c['spec'], c['path'][-60:], 'old', c['oldParts'], 'matched', c['matched'], 'dev', round(c['medianDev'], 4),
              round(c['maxDev'] or 0, 4), 'devY', c['medianDevY'] and round(c['medianDevY'], 4), 'new', c.get('newParts'))
