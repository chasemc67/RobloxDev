"""Collect stage-ae evidence, preserving unknown/unrun counts as null."""
import json,hashlib,re,statistics
from pathlib import Path
OUT=Path('playtests/stage-ae')
SC=[1,2,3,4,5,6,8,9,11,14,17]
MOVERS={6,9,11,14,17}
def read(p,default=None):
 return json.loads(p.read_text()) if p.exists() else default
def result(folder,n):
 p=OUT/folder/f'h{n}.jsonl'
 if p.exists():
  for line in reversed(p.read_text().splitlines()):
   d=json.loads(line)
   if d.get('type')=='result':return d['result']
 return {}
def row(course,n,cup,sweep,expected):
 c=cup.get('cupdrop',{});f=sweep.get('fuzz',{});s=sweep.get('slow',{})
 complete=f.get('shots')==8 and s.get('shots',0)==expected and not sweep.get('error')
 ntime=sum(x.get('timeouts',0) for x in [f,s]);issues=sweep.get('issues',[])
 r={'course':course,'hole':n,'cupdrop_sunk':c.get('sunk'),'cupdrop_total':c.get('n'),'cupdrop_pass':c.get('n')==3 and c.get('sunk')==3,
 'random_shots':f.get('shots'),'slow_rollers':s.get('shots',0) if sweep else None,'sweep_required':course=='sugarloaf' or n==2,
 'sweep_complete':complete,'escapes':sum(x.get('escapes',0) for x in [f,s]) if complete else None,
 'stuck_shots':sum(x.get('stuck',0) for x in [f,s]) if complete else None,
 'hazard_returns':sum(x.get('hazards',0) for x in [f,s]) if complete else None,
 'lost_balls':0 if complete and ntime==0 else None,'timeouts':ntime if complete else None,'issues':issues,'error':sweep.get('error') or cup.get('error')}
 p=OUT/course/f'h{n:02}';p.mkdir(parents=True,exist_ok=True);(p/'result.json').write_text(json.dumps(r,indent=2)+'\n');return r
def main():
 rows=[]
 for n in range(1,19):rows.append(row('aurora',n,result('aurora/cupdrop',n),result('aurora/sweep',n),0))
 for n in SC:
  d=result('sugarloaf/sweep',n)
  if n==17:
   retry=result('sugarloaf/h17-slow-recheck',n)
   if retry:
    d=dict(d);d['slow']=retry.get('slow',{});d['issues']=d.get('issues',[])+retry.get('issues',[])
  rows.append(row('sugarloaf',n,d,d,6 if n in MOVERS else 0))
 floor=result('sugarloaf/h8-timing',8).get('floorstop',[])
 values=[r['stopInterval'] for r in floor if r.get('stopInterval') is not None]
 timing={'definition':'Seconds from last PostSimulation speed > Config.StopSpeed (0.2 studs/s) while moving to first ready/rest sample.',
 'shots':floor,'measured':len(values),'median':statistics.median(values) if values else None,'flags_over_1_5':[r['label'] for r in floor if r.get('over15')],
 'complete':len(values)>=12 and all(r.get('outcome')=='rest' for r in floor),
 'stuck_flags':[{'label':r['label'],'flag':f} for r in floor for f in r.get('flags',[]) if f.get('kind') in ['forcedrest','offsurface','stuck-3s','stuck-timeout']]}
 (OUT/'h8-timing.json').write_text(json.dumps(timing,indent=2)+'\n')
 for r in rows:
  if r['course']=='sugarloaf' and r['hole']==8:
   r['floor_timing']=timing
   (OUT/'sugarloaf/h08/result.json').write_text(json.dumps(r,indent=2)+'\n')
 console={}
 for phase in ['aurora/cupdrop','aurora/sweep','sugarloaf/sweep','sugarloaf/h8-timing','sugarloaf/h17-slow-recheck']:
  p=OUT/phase/'summary.md';s=p.read_text() if p.exists() else ''
  console[phase]={side.lower():int(count) for side,count in re.findall(r'(Server|Client) warnings/errors: (\d+)',s)}
 copies={}
 for name in ['playtest-aurora-v2.rbxl','playtest/playtest-sc-batch12.rbxl']:
  p=Path(name)
  if p.exists():copies[name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 complete=all(r['cupdrop_pass'] and (not r['sweep_required'] or r['sweep_complete']) for r in rows) and timing['complete']
 escapes=sum(r['escapes'] or 0 for r in rows);stuck=sum(r['stuck_shots'] or 0 for r in rows)
 clean=all(v.get('server')==0 and v.get('client')==0 for v in console.values())
 out={'stage':'ae','result':'PASS' if complete and clean and not escapes and not stuck and not timing['flags_over_1_5'] and not timing['stuck_flags'] else 'PARTIAL',
 'complete':complete,'console':console,'local_files':copies,'cupdrop_aurora':sum(r['cupdrop_sunk'] or 0 for r in rows if r['course']=='aurora'),
 'cupdrop_sc':sum(r['cupdrop_sunk'] or 0 for r in rows if r['course']=='sugarloaf'),'escapes':escapes,'stuck_shots':stuck,
 'h8':timing,'h11':read(OUT/'h11-after-summary.json'),'aurora_h2':read(OUT/'aurora-h2-clearance.json'),'holes':rows,
 'limits':['Importer Upload to Roblox was unchecked; meshes carry rbxassetid references. Importer-internal upload/cache behavior and cross-machine portability are unverified.','Aurora inherited H4 wedge finding and H17 static-toggle fallback from ac2 were not retested in this scope.'],
 'lost_definition':'No unrecovered/missing ball observed when every requested shot completed without errors/timeouts; unknown is null. Hazards and escapes are separate.',
 'shutdown':read(OUT/'shutdown.json')}
 (OUT/'result.json').write_text(json.dumps(out,indent=2)+'\n')
 lines=['| Course | Hole | Cupdrop | Random / slow | Escapes | Lost | Stuck | Reasons |','|---|---|---|---|---|---|---|---|']
 for r in rows:
  reason=', '.join(sorted({i.get('reason',i['kind']) for i in r['issues']})) or '—'
  def val(x):return 'unrun' if x is None else str(x)
  lines.append(f"| {r['course']} | H{r['hole']:02} | {val(r['cupdrop_sunk'])}/{val(r['cupdrop_total'])} | {val(r['random_shots'])} / {val(r['slow_rollers'])} | {val(r['escapes'])} | {val(r['lost_balls'])} | {val(r['stuck_shots'])} | {reason} |")
 (OUT/'per-hole.md').write_text('\n'.join(lines)+'\n')
 print({k:v for k,v in out.items() if k in ['result','complete','cupdrop_aurora','cupdrop_sc','escapes','stuck_shots']})
if __name__=='__main__':main()
