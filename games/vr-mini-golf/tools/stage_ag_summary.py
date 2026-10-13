"""Summarize native Studio evidence; missing runs remain unknown."""
import json
from pathlib import Path
root=Path('playtests/stage-ag')
def schedule(name='h17-schedule-final'):
 d=json.loads((root/(name+'.json')).read_text());rows=d['samples']
 edges=[dict(elapsed=r['elapsed'],phase=r['phase'],solid=r['collide']) for i,r in enumerate(rows) if i==0 or r['collide']!=rows[i-1]['collide']]
 bad=[r for r in rows if r['collide']!=(.6<=r['phase']<6.6) or r['query']!=r['collide'] or r['touch']!=r['collide']]
 return dict(samples=len(rows),duration=rows[-1]['elapsed'],mismatches=len(bad),transitions=edges)
if __name__=='__main__':
 print(json.dumps(schedule(),indent=2))
 p=root/'h4/results.json'
 if p.exists():
  r=json.loads(p.read_text())['h4']['default'];shots=r['fuzz']['allShots']+r['biased']
  lines=['| Shot | Time to rest (s) | Outcome | Speed at 15 s | Moving at 15 s | Flags |','|---|---:|---|---:|---|---|']
  for s in shots:
   a=s.get('at15') or {};flags=','.join(f['kind']+':'+f.get('reason','') for f in s.get('flags',[])) or '—'
   lines.append(f"| {s['label']} | {s.get('tRest','—')} | {s['outcome']} | {a.get('speed','ended earlier')} | {a.get('moving',False)} | {flags} |")
  (root/'h4-shots.md').write_text('\n'.join(lines)+'\n')
  print('H4',len(shots),'over15',sum(bool((s.get('at15') or {}).get('moving')) for s in shots))
