"""Compare final physical colliders to the untouched v21 inventory and summarize native shots."""
import json
from pathlib import Path
from run_playtests import Studio
s=Studio();assert s.mode()[0]=='Edit'
code='''local r={}for _,p in workspace.CourseSugarloaf:GetDescendants() do if p:IsA('BasePart') and p.CanCollide then local q=p.CurrentPhysicalProperties table.insert(r,{path=p:GetFullName(),cf={p.CFrame:GetComponents()},size={p.Size.X,p.Size.Y,p.Size.Z},collide=p.CanCollide,query=p.CanQuery,touch=p.CanTouch,physics={q.Density,q.Friction,q.Elasticity,q.FrictionWeight,q.ElasticityWeight}}) end end _G.ZF1Colliders=game.HttpService:JSONEncode(r); return #_G.ZF1Colliders'''
n=int(s.luau(code));raw=''.join(json.loads(s.luau('return game.HttpService:JSONEncode(_G.ZF1Colliders:sub(%d,%d))'%(i+1,i+40000))) for i in range(0,n,40000))
after=json.loads(raw)
keys=('path','cf','size','collide','query','touch','physics')
before=[{k:p[k] for k in keys} for p in json.load(open('playtests/stage-zf1/inventory-before.json'))['parts'] if p['collide'] and p['path'].startswith('Workspace.CourseSugarloaf.')]
canonical=lambda rows: sorted(json.dumps(p,sort_keys=True) for p in rows)
assert canonical(before)==canonical(after),'Collider mismatch against untouched v21'
Path('playtests/stage-zf1/colliders-after.json').write_text(raw+'\n')
r=json.load(open('playtests/stage-zf1/sweep/results.json'));rows=[]
for n in range(1,19):
 d=r['h'+str(n)]['default'];f=d['fuzz'];cups=d['cupdrop'];shots=f['allShots']
 assert d['course']=='sugarloaf_canyon' and cups['sunk']==3 and cups['pass'] and sum(t['outcome']=='cup' for t in cups['tries'])==3
 assert len(shots)==2 and f['shots']==2 and all(x['outcome']!='refused' for x in shots)
 rows.append({'hole':n,'cups':cups['sunk'],'cupAttempts':len(cups['tries']),'refusedCupSetups':sum(t['outcome']=='refused' for t in cups['tries']),'completedRandomShots':len(shots),'stuck':f.get('stuck',0),'escapes':f.get('escapes',0),'timeouts':f.get('timeouts',0),'outcomes':[x['outcome'] for x in shots]})
console=json.load(open('playtests/stage-zf1/sweep/console.json'));assert console=={'Server':[],'Client':[]}
summary={'exactOriginalColliders':len(after),'colliderGeometryAndPropertiesUnchanged':True,'holes':rows,'console':console,'allCupDrops':54,'completedRandomShots':36}
Path('playtests/stage-zf1/verification-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
