"""Verify final local Edit state, collision invariance, and completed test counts."""
import json
from pathlib import Path
from run_playtests import Studio
from stage_al_summary import shot_counts
out=Path('playtests/stage-al2');s=Studio();assert s.mode()[0]=='Edit'
state=json.loads(s.luau('return game.HttpService:JSONEncode({placeId=game.PlaceId,gameId=game.GameId,networkClient=game:FindService("NetworkClient")~=nil,role=workspace:GetAttribute("PlaceRole"),testMode=workspace:GetAttribute("GolfTestMode"),simulateVR=workspace:GetAttribute("SimulateVR")})'))
assert state['placeId']==0 and not state['networkClient'] and not state['testMode'] and not state['simulateVR']
source={}
for name in ['SugarloafHints','SugarloafOverrides']:
 source[name]=s.luau('return game.HttpService:JSONEncode(game.ServerStorage.'+name+'.Source)')
 assert json.loads(source[name])==Path('src/ServerStorage/'+name+'.luau').read_text()
state['changedSourceEquality']=list(source)
code='''local r={} for _,p in workspace.CourseSugarloaf:GetDescendants() do if p:IsA('BasePart') and p.CanCollide then local ph=p.CurrentPhysicalProperties table.insert(r,{path=p:GetFullName(),cf={p.CFrame:GetComponents()},size={p.Size.X,p.Size.Y,p.Size.Z},physics={ph.Density,ph.Friction,ph.Elasticity,ph.FrictionWeight,ph.ElasticityWeight}}) end end _G.AL2After=game.HttpService:JSONEncode(r) return #_G.AL2After'''
n=int(s.luau(code));raw=''.join(json.loads(s.luau('return game.HttpService:JSONEncode(_G.AL2After:sub(%d,%d))'%(a+1,a+45000))) for a in range(0,n,45000))
after=json.loads(raw);before=json.loads((out/'before-colliders.json').read_text())
assert sorted(before,key=lambda x:x['path'])==sorted(after,key=lambda x:x['path'])
state['unchangedPhysicalColliders']=len(after)
(out/'after-colliders.json').write_text(raw+'\n')
s.luau('_G.AL2Before=nil _G.AL2After=nil return true')
results=json.loads((out/'sweep/results.json').read_text());rows=[]
for n in [9,14]:
 r=results['h'+str(n)]['default'];assert r['course']=='sugarloaf_canyon' and not r.get('error')
 cups=r['cupdrop'];shots=r['fuzz']['allShots']
 assert cups['n']==3 and cups['sunk']==3 and len(cups['tries'])==3
 assert len(shots)==8 and r['fuzz']['shots']==8 and all(x['outcome']!='refused' for x in shots)
 counts=shot_counts(shots)
 for metric in ['stuck','escapes','timeouts']:counts[metric]=max(counts[metric],r['fuzz'].get(metric,0),r.get(metric,0))
 rows.append(dict(hole=n,cups=3,attempts=3,random=len(shots),**counts))
console=json.loads((out/'console.json').read_text());assert console=={'Server':[],'Client':[]}
state['holes']=rows;state['consoleErrors']=0;state['consoleWarnings']=0
state['result']='PASS' if all(not any(r[k] for k in ['stuck','escapes','timeouts']) for r in rows) else 'PARTIAL'
(out/'verification-summary.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(state,indent=2))
