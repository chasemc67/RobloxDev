"""Stage sc5 recovery: rebuild Workspace visual MeshParts that a first replacement pass destroyed.
Template = same-named part in the v23 ServerStorage libraries (game:GetObjects of place version 23, held in
_G.SC5SS23), pose/size/material/transparency/flags/group = playtests/stage-sc5/inventory-before.json (v23 baseline).
  PYTHONPATH=tools python3 tools/sc5_restore.py /tmp/sc5/missing.json
"""
import json, sys
from sc5_util import studio, fetch, OUT
from holes_to_lua import to_lua
LUA = r'''
local rows=__ROWS__
local ss=assert(_G.SC5SS23,'v23 ServerStorage copy missing')
local rep={restored=0,noParent={},noTemplate={},templateFrom={}}
local function findPath(path)
 local x=game for seg in path:gmatch('[^%.]+') do x=x and x:FindFirstChild(seg) end return x
end
local libs={Kit={'SugarloafKit'},StageAEVisuals={'StageAEProps','SugarloafMovers','StageAFProps'},StageAFVisuals={'StageAFProps','StageAEProps','SugarloafMovers'},
 StageAJVisuals={'StageAJProps','StageAFProps'},default={'SugarloafMovers','StageAEProps','StageAFProps','StageAJProps','SugarloafKit'}}
for i,r in rows do
 local segs=r.path:split('.')
 local name=segs[#segs]
 local parent=findPath(table.concat(segs,'.',1,#segs-1))
 if not parent then table.insert(rep.noParent,r.path) continue end
 local stem=name:match('^(.-)__')
 local order=libs.default
 if r.path:find('%.Kit%.') then order=libs.Kit elseif r.path:find('StageAEVisuals') then order=libs.StageAEVisuals
 elseif r.path:find('StageAFVisuals') then order=libs.StageAFVisuals elseif r.path:find('StageAJVisuals') then order=libs.StageAJVisuals end
 local t
 for _,fn in order do local lm=ss[fn]:FindFirstChild(stem) if lm then t=lm:FindFirstChild(name) if t then rep.templateFrom[fn]=(rep.templateFrom[fn] or 0)+1 break end end end
 if not t then table.insert(rep.noTemplate,r.path) continue end
 local p=t:Clone()
 for _,c in p:GetChildren() do if c:IsA('WeldConstraint') or c:IsA('Weld') then c:Destroy() end end
 for k in p:GetAttributes() do if k:sub(1,3)=='ZF1' then p:SetAttribute(k,nil) end end
 p.Size=Vector3.new(table.unpack(r.size)) p.CFrame=CFrame.new(table.unpack(r.cf))
 p.Transparency=r.transparency p.Material=Enum.Material[r.material]
 p.CanCollide=r.collide p.CanQuery=r.query p.CanTouch=r.touch p.Anchored=r.anchored p.CollisionGroup=r.group
 local mover=parent:FindFirstAncestorWhichIsA('Model')
 local mv=parent while mv and not mv.Name:match('^Mover_') do mv=mv.Parent end
 if mv and not r.anchored then
  p.Massless=true
  local root=mv:FindFirstChild('MoverRoot')
  if root then local w=Instance.new('WeldConstraint') w.Part0=root w.Part1=p w.Parent=p else table.insert(rep.noParent,'no MoverRoot '..r.path) end
 end
 p:SetAttribute('SC5Restored',true)
 p.Parent=parent rep.restored+=1
 if i%100==0 then task.wait() end
end
_G.SC5Out=game.HttpService:JSONEncode(rep) return #_G.SC5Out
'''
if __name__ == '__main__':
    rows = json.load(open(sys.argv[1]))
    keep = ('path', 'cf', 'size', 'transparency', 'material', 'collide', 'query', 'touch', 'anchored', 'group')
    rows = [{k: r[k] for k in keep} for r in rows]
    s = studio()
    raw = fetch(s, '_G.SC5Out', LUA.replace('__ROWS__', to_lua(rows)), timeout=900)
    (OUT / 'recovery-restore.json').write_text(raw + '\n')
    r = json.loads(raw); print({k: (len(v) if isinstance(v, list) else v) for k, v in r.items()}, r['noParent'][:5], r['noTemplate'][:5])
