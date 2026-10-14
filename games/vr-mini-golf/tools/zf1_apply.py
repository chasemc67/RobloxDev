"""Apply zf1 visual passes to the sole Sugarloaf local snapshot and save evidence."""
import json
from pathlib import Path
from run_playtests import Studio
s=Studio(); assert s.mode()[0]=='Edit'
assert s.luau('return game.PlaceId==0 and workspace:GetAttribute("PlaceRole")=="sugarloaf_canyon"')=='true'
code='''
local course=workspace.CourseSugarloaf
local baseline={}
local placeholders={}
for _,p in course:GetDescendants() do
 if p:IsA('BasePart') then
  if p.CanCollide then table.insert(baseline,{p=p,cf=p.CFrame,size=p.Size,query=p.CanQuery,touch=p.CanTouch,group=p.CollisionGroup,phys=p.CustomPhysicalProperties}) end
  if p:FindFirstAncestor('Placeholder') then table.insert(placeholders,p) end
 end
end
local decals=require(game.ServerStorage.SugarloafDecals:Clone()).Apply(course)
local fixes=require(game.ServerStorage.VisualSeparation:Clone()).Apply(course)
local changed={}
for _,o in baseline do local p=o.p
 if p.CFrame~=o.cf or p.Size~=o.size or not p.CanCollide or p.CanQuery~=o.query or p.CanTouch~=o.touch or p.CollisionGroup~=o.group or p.CustomPhysicalProperties~=o.phys then table.insert(changed,p:GetFullName()) end
end
local count,visible=0,0
for _,p in placeholders do assert(p.Parent,'Placeholder removed');count+=1;if p.Transparency<1 then visible+=1 end end
_G.ZF1FixJSON=game.HttpService:JSONEncode({decals=decals,fixes=fixes,colliderCount=#baseline,changedColliders=changed,placeholderCount=count,visiblePlaceholders=visible})
return #_G.ZF1FixJSON
'''
result=s.luau(code,timeout=300)
try:n=int(result)
except ValueError:raise RuntimeError(result)
raw=''.join(json.loads(s.luau('return game.HttpService:JSONEncode(_G.ZF1FixJSON:sub(%d,%d))'%(i+1,i+40000))) for i in range(0,n,40000))
Path('playtests/stage-zf1/fixes.json').write_text(raw+'\n')
r=json.loads(raw);print(json.dumps({k:v for k,v in r.items() if k not in ['fixes','decals']},indent=2));print('decals',len(r['decals']['placed']),'missing',r['decals']['missing']);print('fix summary',{k:len(v) if isinstance(v,list) else v for k,v in r['fixes'].items()})
assert not r['changedColliders'] and r['placeholderCount']==175
assert len(r['decals']['placed'])==29
