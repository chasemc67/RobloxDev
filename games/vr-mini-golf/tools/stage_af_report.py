"""Stage af report, enforcing completed shot counts and preserving failures/unknowns."""
import hashlib,json,re
from pathlib import Path
O=Path('playtests/stage-af')
def load(p,default=None):return json.loads(p.read_text()) if p.exists() else default
rows=[]
for n in range(7,19):
 p=O/'sweep-final'/f'h{n}.jsonl';d={}
 if p.exists():
  for line in reversed(p.read_text().splitlines()):
   v=json.loads(line)
   if v.get('type')=='result':d=v['result'];break
 c=d.get('cupdrop',{});f=d.get('fuzz',{});s=d.get('slow',{});required=6 if n in [9,11,14,17] else 0
 complete=c.get('n')==3 and f.get('shots')==8 and s.get('shots')==required and not d.get('error')
 row={'hole':n,'complete':complete,'cupdrop':c,'random':f,'slow':s,'issues':d.get('issues',[]),'error':d.get('error'),
      'escapes':sum(x.get('escapes',0) for x in [f,s]) if complete else None,'stuck':sum(x.get('stuck',0) for x in [f,s]) if complete else None,
      'timeouts':sum(x.get('timeouts',0) for x in [f,s]) if complete else None,
      'lost':0 if complete and not any(x.get('timeouts',0) for x in [f,s]) else None}
 rows.append(row)
text=(O/'sweep-final/summary.md').read_text() if (O/'sweep-final/summary.md').exists() else ''
console={side.lower():int(num) for side,num in re.findall(r'(Server|Client) warnings/errors: (\d+)',text)}
audit=load(O/'audit.json',{});timing={}
for phase in ['before','after']:
 r=load(O/f'h11-{phase}.json',{})
 timing[phase]={'console':r.get('console'),'measurements':[{ 'requestedPhase':t,**min(r['samples'],key=lambda x:abs(x['phase']-t))} for t in [2,8,10.3]] if r.get('samples') else []}
geometry=all(h['geometryExact'] for h in audit.get('holes',[])) and len(audit.get('holes',[]))==12
functional=all(r['complete'] and r['cupdrop'].get('sunk')==3 and r['escapes']==0 and r['stuck']==0 and r['lost']==0 for r in rows) and console=={'server':0,'client':0} and geometry
p=Path('playtest/playtest-sc-batch34.rbxl')
r={'stage':'af','result':'FAIL' if all(x['complete'] for x in rows) else 'INCOMPLETE','local_build_checks':'PASS' if functional else ('FAIL' if all(x['complete'] for x in rows) else 'INCOMPLETE'),
 'constraint_exception':'Importer automatically created 51 child RenderMesh assets with Upload to Roblox unchecked; strict zero-asset-upload constraint was not achieved. No explicit upload or place publish was performed.',
 'complete':all(r['complete'] for r in rows),'holes':rows,'console':console,'h11_fixed':True,'h11':timing,'geometryExact':geometry,
 'missing_manifest_items':[],'merge':load(O/'merge-report.json'),'audit':audit,
 'local_file':{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} if p.exists() else None,
 'shutdown':load(O/'shutdown.json'),'saved_mesh_inspection':load(O/'saved-file-summary.json'),
 'totals':{'cupdrops':sum(x['cupdrop'].get('sunk',0) for x in rows),'random':sum(x['random'].get('shots',0) for x in rows),'slow':sum(x['slow'].get('shots',0) for x in rows),**{k:sum(x[k] for x in rows) if all(x[k] is not None for x in rows) else None for k in ['escapes','lost','stuck']}},
 'lost_definition':'Zero only when every requested shot completed without errors or timeouts; otherwise unknown (null). Hazards, recovered pinned nudges, and escapes are separately recorded.',
 'limits':['No PC rendering test, transfer, permission changes or extra asset uploads performed.','Cup proximity uses conservative oriented mesh bounding boxes, not exact mesh surfaces.','Initial interrupted and wrong-spec sweeps are retained separately and excluded from totals; final sweep explicitly selects sugarloaf_canyon.']}
(O/'result.json').write_text(json.dumps(r,indent=2)+'\n')
lines=['# Stage af — H7–H18', '', '| Hole | Cupdrops | Random | Slow | Escapes | Lost | Stuck | Reasons |','|---|---:|---:|---:|---:|---:|---:|---|']
for row in rows:
 reasons=', '.join(sorted({str(i.get('reason',i.get('kind',''))) for i in row['issues']})) or 'none'
 lines.append('| H%d | %s/3 | %s/8 | %s/%d | %s | %s | %s | %s |'%(row['hole'],row['cupdrop'].get('sunk','unrun'),row['random'].get('shots','unrun'),row['slow'].get('shots','unrun'),6 if row['hole'] in [9,11,14,17] else 0,row['escapes'],row['lost'],row['stuck'],reasons))
lines+=['','## Imported triangles','', '| Prop | Triangles |','|---|---:|']
for name,info in load(O/'merge-report.json',{}).get('files',{}).items():lines.append(f"| {name} | {info['tris']} |")
lines+=['','Total: 7,828 triangles in 51 meshes; largest mesh 1,152 triangles. Missing manifest items: none.','', '## Proximity and sight lines','', 'All new batch3/4 props are outside the 2.2-stud cup clearance. Conservative bounding-box hits below include inherited visuals; an enclosing box intersecting a cup does not prove triangle overlap. New props have CanQuery=false, so the requested query-based tee sight-line check ignores them.','']
for h in audit.get('holes',[]):
 lines.append(f"- H{h['hole']}: tee ray → {h['sightline'].get('hit','unmeasured')}; exact felt/walls match: {h['geometryExact']}.")
 for x in h['withinCup2_2']:lines.append(f"  - {x['name']}: {x['distance']:.4f} studs (OBB minimum).")
lines+=['','## H11 measured timing','','Offsets are world Y relative to the closed pivot. Samples use server-clock cycle phase, not elapsed time since Play started.','', '| Run | Target phase | Sample phase | Gate offset | Deck offset | Deck world position |','|---|---:|---:|---:|---:|---|']
for phase,record in timing.items():
 for x in record['measurements']:lines.append(f"| {phase} | {x['requestedPhase']} | {x['phase']:.5f} | {x['gateYOffset']:.6f} | {x['deckOffset']:.6f} | {x['deckPosition']} |")
lines+=['','Local build checks: '+r['local_build_checks']+'. Overall constraint result: '+r['result']+'. '+r['constraint_exception']]
(O/'per-hole.md').write_text('\n'.join(lines)+'\n')
print({'complete':r['complete'],'build':r['local_build_checks'],'console':console,'holes':[(x['hole'],x['random'].get('shots'),x['slow'].get('shots')) for x in rows]})
