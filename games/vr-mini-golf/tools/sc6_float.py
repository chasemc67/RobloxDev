"""Stage sc6 float check: every visual unit that rests on the (new fit030) ground tiles, signed gap from each part's
bottom to the ground below (25 samples per part). A unit hovers if no sample touches (min gap > 0.05) and the nearest
ground is within 1 stud. Ground tiles are made queryable only for the rays and restored.
  PYTHONPATH=tools python3 tools/sc6_float.py
"""
import json
import sc5_ground
from sc5_util import studio, fetch, GAME

LUA = sc5_ground.COMMON + r'''
local isTile={} for _,p in tiles do isTile[p]=true end
local units={}
local function add(name,parts) if #parts>0 then table.insert(units,{name=name,parts=parts}) end end
for _,m in dressing:GetChildren() do if not m.Name:match('_ground$') then local ps={} for _,p in m:GetDescendants() do if p:IsA('BasePart') and not isTile[p] and p.Transparency<1 then table.insert(ps,p) end end add(m.Name,ps) end end
for _,m in course.Kit.cluster:GetChildren() do local ps={} for _,p in m:GetDescendants() do if p:IsA('BasePart') and p.Transparency<1 then table.insert(ps,p) end end add('cluster/'..m.Name,ps) end
for _,f in {'scenery','walkway','building','bridge','structure','lift'} do local k=course.Kit:FindFirstChild(f)
 for _,m in k and k:GetChildren() or {} do local ps={} for _,p in m:GetDescendants() do if p:IsA('BasePart') and p.Transparency<1 then table.insert(ps,p) end end add(f..'/'..m.Name,ps) end end
for n=1,18 do local h=course['Hole'..n]
 for _,fn in {'StageAEVisuals','StageAFVisuals','StageAJVisuals'} do local f=h:FindFirstChild(fn)
  for _,m in f and f:GetChildren() or {} do local ps={} for _,p in m:GetDescendants() do if p:IsA('BasePart') and not isTile[p] and p.Transparency<1 and not (p.CanCollide or p.CanQuery or p.CanTouch) then table.insert(ps,p) end end add('Hole'..n..'.'..fn..'.'..m.Name,ps) end end end
local out={units=0,resting=0,hover={},sample=0}
local ok,err=pcall(function()
for i,u in units do
 local minGap,contacts=math.huge,0
 for _,p in u.parts do local c,s=p.CFrame,p.Size local e=(c.RightVector*s.X/2):Abs()+(c.UpVector*s.Y/2):Abs()+(c.LookVector*s.Z/2):Abs()
  local lo,hi=c.Position-e,c.Position+e
  for ix=0,4 do for iz=0,4 do local x=lo.X+(hi.X-lo.X)*(ix+0.5)/5 local z=lo.Z+(hi.Z-lo.Z)*(iz+0.5)/5
   local h=ray(Vector3.new(x,lo.Y+0.3,z),Vector3.new(0,-1.3,0),tiles)
   if h then contacts+=1 local g=lo.Y-h.Position.Y if g<minGap then minGap=g end end end end end
 if contacts>0 then out.resting+=1 if minGap>0.05 then table.insert(out.hover,{name=u.name,minGap=minGap,contacts=contacts}) end end
 out.units+=1 if i%30==0 then task.wait() end
end end)
restore() assert(ok,err)
_G.SC5Out=game.HttpService:JSONEncode(out) return #_G.SC5Out
'''

# --old: the same rays against temporary clones of the replaced fix_zfight3 tiles (ServerStorage.SC6Backup, Workspace
# copies only), destroyed right after; the live fit030 tiles are left out of the ray list
OLD = LUA.replace("local isTile={}", '''local tmp=Instance.new('Folder') tmp.Name='SC6TmpOldTiles' tmp.Parent=workspace
local live={} for _,p in tiles do live[p]=true end
tiles={} tileHole={}
for _,f in game.ServerStorage.SC6Backup:GetChildren() do if f:GetAttribute('OrigPath'):match('^Workspace') then
 for _,p in f:GetChildren() do local n=tonumber(p.Name:match('^h(%d+)_ground_s%d+__')) if n then local q=p:Clone() q.CanQuery=true q.Parent=tmp table.insert(tiles,q) tileHole[q]=n end end end end
local isTile=live''',1).replace("restore() assert(ok,err)","restore() tmp:Destroy() assert(ok,err)")

if __name__ == '__main__':
    import sys
    old = '--old' in sys.argv
    s = studio()
    raw = fetch(s, '_G.SC5Out', OLD if old else LUA, timeout=900)
    (GAME / ('playtests/stage-sc6/float-gaps%s.json' % ('-oldtiles' if old else ''))).write_text(raw + '\n')
    r = json.loads(raw); print('units', r['units'], 'resting on ground', r['resting'], 'hovering', len(r['hover']))
    for h in r['hover']: print('  HOVER', h)
