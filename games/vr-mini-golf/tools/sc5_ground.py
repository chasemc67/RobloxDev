"""Stage sc5 step 4: drop even-hole ground visuals 0.08 studs plus what rests only on them.
  PYTHONPATH=tools python3 tools/sc5_ground.py seams before|after   (probe the 9 coplanar inter-hole tile pairs)
  PYTHONPATH=tools python3 tools/sc5_ground.py plan                 (decide units, no change)
  PYTHONPATH=tools python3 tools/sc5_ground.py drop                 (apply the plan)
Ground tiles are CanQuery off; they are made queryable only for the probe rays and restored right after.
A unit (ground set, dress set, cluster stem group, scenery model, even-hole visual model) drops if its ground
contacts are all on even-hole tiles and it is not within 0.1 studs of any collider (felt, rails, walls).
Anything moved has its ZF1 base poses rebased by the same offset. Colliders are never touched.
"""
import json, sys
from pathlib import Path
from sc5_util import studio, fetch, OUT, GAME
from holes_to_lua import to_lua

DROP = 0.08
COMMON = r'''
local course=workspace.CourseSugarloaf
local dressing=course.Kit.hole_dressing
local lay=require(game.ServerStorage.CourseData.SugarloafLayout:Clone())
local off=Vector3.new(table.unpack(lay.offset))
local tiles={} local tileHole={} local tileStem={}
-- ground tiles anywhere in the course (H8's ground lives in Hole8.StageAJVisuals), by part name hNN_ground_sXX__*
for _,p in course:GetDescendants() do if p:IsA('BasePart') then local n=tonumber(p.Name:match('^h(%d+)_ground_s%d+__')) if n then
 table.insert(tiles,p) tileHole[p]=n tileStem[p]=p.Name:match('^(.-)__') end end end
local saved={} for _,p in tiles do saved[p]=p.CanQuery p.CanQuery=true end
local function restore() for p,v in saved do p.CanQuery=v end end
local function ray(o,d,list) local rp=RaycastParams.new() rp.FilterType=Enum.RaycastFilterType.Include rp.FilterDescendantsInstances=list
 return workspace:Raycast(o,d,rp) end
'''

SEAMS = COMMON + r'''
local pairs_=__PAIRS__
local out={}
local ok,err=pcall(function()
for _,pr in pairs_ do
 local la,lb={},{} for _,p in tiles do if tileStem[p]==pr.a then table.insert(la,p) elseif tileStem[p]==pr.b then table.insert(lb,p) end end
 -- dense grid over the pair's overlap box (layout coords + offset): top surface of each tile on its own
 local lo=Vector3.new(table.unpack(pr.box[1]))+off local hi=Vector3.new(table.unpack(pr.box[2]))+off
 local step=0.25 local both,cop,minGap,gaps=0,0,nil,{}
 for x=lo.X+step/2,hi.X,step do for z=lo.Z+step/2,hi.Z,step do
  local o=Vector3.new(x,hi.Y+2,z) local d=Vector3.new(0,-(hi.Y-lo.Y)-4,0)
  local ha,hb=ray(o,d,la),ray(o,d,lb)
  if ha and hb then both+=1 local g=math.abs(ha.Position.Y-hb.Position.Y)
   if g<0.02 then cop+=1 end if not minGap or g<minGap then minGap=g end table.insert(gaps,g) end
 end end
 -- the analysis' own sample points as a cross-check
 local pts={}
 for _,at in pr.at do local w=Vector3.new(at[1],at[2],at[3])+off
  local function near(list) local best for _,dd in {Vector3.new(0,-1,0),Vector3.new(0,1,0)} do
   local h=ray(w-dd*0.6,dd*1.2,list) if h and (not best or math.abs(h.Position.Y-w.Y)<math.abs(best-w.Y)) then best=h.Position.Y end end return best end
  local ya,yb=near(la),near(lb) table.insert(pts,{at=at,ya=ya,yb=yb}) end
 table.sort(gaps)
 table.insert(out,{a=pr.a,b=pr.b,partsA=#la,partsB=#lb,samplesBoth=both,coplanarSamples=cop,minGap=minGap,medianGap=gaps[math.max(1,#gaps//2)],points=pts})
 task.wait()
end end)
restore() assert(ok,err)
_G.SC5Out=game.HttpService:JSONEncode(out) return #_G.SC5Out
'''

PLAN = COMMON + r'''
local DROP=__DROP__
local apply=__APPLY__
local units={}
local function addUnit(kind,name,parts,forced) if #parts>0 then table.insert(units,{kind=kind,name=name,parts=parts,forced=forced}) end end
-- even ground sets and even dress sets: forced (they belong to the even hole)
local isTile={} for _,p in tiles do isTile[p]=true end
for n=2,18,2 do local ps={} for _,p in tiles do if tileHole[p]==n then table.insert(ps,p) end end addUnit('ground','h'..string.format('%02d',n)..'_ground',ps,true) end
for _,m in dressing:GetChildren() do
 local n=tonumber(m.Name:match('^h(%d+)_')) local ps={} for _,p in m:GetDescendants() do if p:IsA('BasePart') and not isTile[p] then table.insert(ps,p) end end
 if n and n%2==0 and m.Name:match('_dress_') then addUnit('dress',m.Name,ps,false)
 elseif not m.Name:match('_ground$') then addUnit('dressing',m.Name,ps,false) end
end
-- clusters: per stem group (cacti_*_gNN, scatter_*, hoodoos_*, narrows_crystals); scenery: per model
for _,m in course.Kit.cluster:GetChildren() do
 local g={} for _,p in m:GetDescendants() do if p:IsA('BasePart') then local s=p.Name:match('^(.-)__') or p.Name g[s]=g[s] or {} table.insert(g[s],p) end end
 for s,ps in g do addUnit('cluster',m.Name..'/'..s,ps,false) end
end
for _,f in {'scenery','walkway','building','bridge','structure','lift'} do local k=course.Kit:FindFirstChild(f)
 for _,m in k and k:GetChildren() or {} do local ps={} for _,p in m:GetDescendants() do if p:IsA('BasePart') then table.insert(ps,p) end end addUnit(f,m.Name,ps,false) end end
-- visual models inside even holes (decor meshes, stage visuals, placeholder meshes)
for n=2,18,2 do local h=course:FindFirstChild('Hole'..n)
 for _,fn in {'StageAEVisuals','StageAFVisuals','StageAJVisuals'} do local f=h:FindFirstChild(fn)
  for _,m in f and f:GetChildren() or {} do local ps={} for _,p in m:GetDescendants() do if p:IsA('BasePart') and not isTile[p] then table.insert(ps,p) end end addUnit('holeVisual','Hole'..n..'.'..fn..'.'..m.Name,ps,false) end end
 local d=h:FindFirstChild('Decor')
 for _,m in d and d:GetDescendants() or {} do if m.Name=='SC5Mesh' or (m:IsA('Model') and m.Parent.Name=='Meshes') then
  local ps={} for _,p in m:GetDescendants() do if p:IsA('BasePart') and p.Transparency<1 then table.insert(ps,p) end end addUnit('holeVisual',m:GetFullName(),ps,false) end end
end
local ovp=OverlapParams.new()
local result={drop={},keep={},floatRisk={},moved=0,rebased=0}
local ok,err=pcall(function()
for i,u in units do
 local lo,hi=Vector3.new(math.huge,math.huge,math.huge),Vector3.new(-math.huge,-math.huge,-math.huge)
 local gameplay=false
 for _,p in u.parts do if p.CanCollide or p.CanQuery or p.CanTouch or #p:GetTags()>0 then gameplay=true end
  local c,s=p.CFrame,p.Size local e=(c.RightVector*s.X/2):Abs()+(c.UpVector*s.Y/2):Abs()+(c.LookVector*s.Z/2):Abs()
  lo=lo:Min(c.Position-e) hi=hi:Max(c.Position+e) end
 local even,odd,contacts,flush=0,0,0,0
 for _,p in u.parts do
  local c,s=p.CFrame,p.Size local e=(c.RightVector*s.X/2):Abs()+(c.UpVector*s.Y/2):Abs()+(c.LookVector*s.Z/2):Abs()
  local plo,phi=c.Position-e,c.Position+e
  for ix=0,4 do for iz=0,4 do
   local x=plo.X+(phi.X-plo.X)*(ix+0.5)/5 local z=plo.Z+(phi.Z-plo.Z)*(iz+0.5)/5
   local h=ray(Vector3.new(x,phi.Y+0.5,z),Vector3.new(0,-(phi.Y-plo.Y)-2,0),tiles)
   if h and h.Position.Y>=plo.Y-1.0 and h.Position.Y<=plo.Y+0.3 then
    contacts+=1 if tileHole[h.Instance]%2==0 then even+=1 else odd+=1 end
    if math.abs(h.Position.Y-plo.Y)<0.15 and tileHole[h.Instance]%2==0 then flush+=1 end
   end end end
 end
 -- collider proximity (felt, rails, walls, anything collidable) within 0.1 studs of the unit's parts
 -- sc5 meshes carry the art bot's vertex-level fitcheck (felt/rail clearance >= 0.156, none touching); merged
 -- dress/cluster MeshParts have boxes spanning whole holes, so the box test only applies to other units
 local near
 local fit=true for _,p in u.parts do if not p:GetAttribute('SC5Source') then fit=false end end
 if not fit then
  for _,p in u.parts do for _,q in workspace:GetPartBoundsInBox(p.CFrame,p.Size+Vector3.new(0.2,0.2,0.2),ovp) do
   if q.CanCollide and not table.find(u.parts,q) then near=q:GetFullName() break end end if near then break end end
 end
 local decide=u.kind=='ground' or (u.kind=='dress' and not gameplay and not near) or (not gameplay and not near and even>0 and odd==0)
 local row={kind=u.kind,name=u.name,parts=#u.parts,fitcheck=fit,contacts=contacts,even=even,odd=odd,flush=flush,nearCollider=near,gameplay=gameplay,bottom=lo.Y}
 if decide then table.insert(result.drop,row) else table.insert(result.keep,row) if flush>0 then table.insert(result.floatRisk,row) end end
 if decide and apply then
  for _,p in u.parts do
   p.CFrame=p.CFrame-Vector3.new(0,DROP,0)
   for _,a in {'ZF1BaseCF','ZF1MeshTerrainBaseCF','StageZf1OriginalCFrame'} do local v=p:GetAttribute(a) if typeof(v)=='CFrame' then p:SetAttribute(a,v-Vector3.new(0,DROP,0)) result.rebased+=1 end end
   p:SetAttribute('SC5GroundDrop',DROP) result.moved+=1
  end
 end
 if i%40==0 then task.wait() end
end end)
restore() assert(ok,err)
_G.SC5Out=game.HttpService:JSONEncode(result) return #_G.SC5Out
'''


def seam_pairs():
    d = json.loads((GAME / 'playtests/stage-sc5-inputs/seams.json').read_text())
    return [dict(a=c['a'], b=c['b'], box=c['overlap_box'], at=[e['at'] for e in c['coplanar_ex']]) for c in d['cross'] if c['coplanar'] > 0]


if __name__ == '__main__':
    a = sys.argv[1]
    s = studio()
    if a == 'seams':
        pr = seam_pairs(); assert len(pr) == 9, len(pr)
        raw = fetch(s, '_G.SC5Out', SEAMS.replace('__PAIRS__', to_lua(pr)))
        (OUT / ('seams-' + sys.argv[2] + '.json')).write_text(raw + '\n')
        for r in json.loads(raw):
            print(r['a'], r['b'], 'both-hit samples', r['samplesBoth'], 'coplanar(<0.02)', r['coplanarSamples'],
                  'minGap', r['minGap'] and round(r['minGap'], 4), 'medianGap', r['medianGap'] and round(r['medianGap'], 4))
    elif a in ('plan', 'drop'):
        code = PLAN.replace('__DROP__', str(DROP)).replace('__APPLY__', 'true' if a == 'drop' else 'false')
        raw = fetch(s, '_G.SC5Out', code, timeout=900)
        (OUT / ('ground-' + a + '.json')).write_text(raw + '\n')
        r = json.loads(raw)
        print('drop', len(r['drop']), 'keep', len(r['keep']), 'floatRisk', len(r['floatRisk']), 'moved', r['moved'], 'rebased', r['rebased'])
        for x in r['drop']: print('  DROP', x['kind'], x['name'], x['contacts'], x['even'], x['odd'])
        for x in r['floatRisk']: print('  FLOATRISK', x)
