"""Summarize completed native runs; never infer missing tests as passes."""
import json
from pathlib import Path
OUT=Path('playtests/stage-am')
d=json.loads((OUT/'sweep/results.json').read_text())
rows=[];stuck=[];escapes=[];h4=[]
for k,v in sorted(d.items(),key=lambda kv:int(kv[0][1:])):
 r=v['default'];shots=r.get('fuzz',{}).get('allShots',[])+r.get('slow',{}).get('allShots',[])+r.get('biased',[])
 for s in shots:
  flags=s.get('flags',[])
  if s['outcome']=='timeout' or any(f['kind'] in ['offsurface','forcedrest','stuck-3s'] or (f['kind']=='autoreset' and f.get('reason')=='timeout') for f in flags):stuck.append(dict(hole=r['hole'],**s))
  if s['outcome']=='escape' or any(f['kind']=='escape' for f in flags):escapes.append(dict(hole=r['hole'],**s))
 if r['hole']==4:h4=r.get('biased',[])
 rows.append({'hole':r['hole'],'cups_sunk':r.get('cupdrop',{}).get('sunk',0),'cups_attempted':r.get('cupdrop',{}).get('n',0),'random':r.get('fuzz',{}).get('shots',0),'slow':r.get('slow',{}).get('shots',0),'focused':len(r.get('biased',[])),'issue_stuck':r.get('stuck'),'issue_escapes':r.get('escapes')})
schedule=None
summary={'completed_holes':len(rows),'cupdrop_sunk':sum(r['cups_sunk'] for r in rows),'cupdrop_attempted':sum(r['cups_attempted'] for r in rows),'random':sum(r['random'] for r in rows),'slow':sum(r['slow'] for r in rows),'stuck':len(stuck),'escapes':len(escapes),'h4_focused':len(h4),'h4_crawl15':sum(bool((s.get('at15') or {}).get('moving')) for s in h4),'hazard_returns':sum(v['default'].get(g,{}).get('hazards',0) for v in d.values() for g in ['fuzz','slow']),'timeouts':sum(v['default'].get(g,{}).get('timeouts',0) for v in d.values() for g in ['fuzz','slow']),'nudges':sum(v['default'].get(g,{}).get('nudges',0) for v in d.values() for g in ['fuzz','slow']),'h17':schedule,'console':json.loads((OUT/'console.json').read_text()) if (OUT/'console.json').exists() else None}
(OUT/'test-summary.json').write_text(json.dumps({'summary':summary,'holes':rows,'stuck':stuck,'escapes':escapes,'h4':h4},indent=2)+'\n')
lines=['| Hole | Cupdrop | Random | Slow | Focused | Stuck issues | Escape issues |','|---|---|---:|---:|---:|---:|---:|']
for r in rows:lines.append(f"| {r['hole']} | {r['cups_sunk']}/{r['cups_attempted']} | {r['random']} | {r['slow']} | {r['focused']} | {r['issue_stuck']} | {r['issue_escapes']} |")
(OUT/'per-hole.md').write_text('\n'.join(lines)+'\n')
printed=dict(summary)
if printed['h17']: printed['h17']={k:v for k,v in printed['h17'].items() if k!='bad'}
print(json.dumps(printed,indent=2))
