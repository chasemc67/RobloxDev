"""Summarize actual completed native tests; never count setup attempts as shots."""
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);r=json.loads((p/'results.json').read_text());rows=[]
for n in sorted(int(k[1:]) for k in r if k.startswith('h')):
 d=r['h'+str(n)]['default'];f=d['fuzz'];c=d['cupdrop'];shots=f.get('allShots')
 if shots is None:
  events=[json.loads(line) for line in (p/('h'+str(n)+'.jsonl')).read_text().splitlines()]
  shots=[e for e in events if e.get('event')=='shot' and '-fuzz-' in e.get('label','')]
 rows.append({'hole':n,'course':d['course'],'cups':c['sunk'],'cupPass':c['pass'],'cupAttempts':len(c['tries']),'completedShots':len(shots),'stuck':f.get('stuck',0),'escapes':f.get('escapes',0),'timeouts':f.get('timeouts',0),'outcomes':[x['outcome'] for x in shots]})
assert [x['hole'] for x in rows]==list(range(1,10 if rows[0]['course']=='lantern_grove' else 19)), 'incomplete course sweep'
console=json.loads((p/'console.json').read_text())
summary={'holes':rows,'console':console,'cups':sum(r['cups'] for r in rows),'shots':sum(r['completedShots'] for r in rows),'timeouts':sum(r['timeouts'] for r in rows),'stuck':sum(r['stuck'] for r in rows),'escapes':sum(r['escapes'] for r in rows)}
(p/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
assert all(r['cups']==3 and r['cupPass'] and r['completedShots']==2 and 'refused' not in r['outcomes'] for r in rows)
assert console=={'Server':[],'Client':[]}
assert summary['stuck']==0 and summary['escapes']==0
