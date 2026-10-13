"""Read-only progress checkpoint for a running stage-al friction scenario."""
import json,sys
from pathlib import Path
from run_playtests import Studio
out=Path('playtests/stage-al/h15-'+sys.argv[1]);out.mkdir(exist_ok=True)
p=out/'checkpoint.json';checkpoint=json.loads(p.read_text()) if p.exists() else {'next':1,'rows':[]}
s=Studio()
target=json.loads(s.api("status"))["lines"]
while checkpoint["next"]<=target:
 text=s.api('log',checkpoint['next'],60000);head,_,body=text.partition('\n');nxt=int(head)
 if body:
  for line in body.splitlines():
   row=json.loads(line)
   if row.get('event')=='h15-friction-row':checkpoint['rows'].append(row)
 if nxt<=checkpoint['next']:break
 checkpoint['next']=nxt
checkpoint['status']=json.loads(s.api('status'));p.write_text(json.dumps(checkpoint,indent=1))
from collections import Counter
print(json.dumps({'shots':len(checkpoint['rows']),'categories':dict(Counter(r['category'] for r in checkpoint['rows'])),'raw_timeouts':sum(bool(r.get('nativeTimeout')) for r in checkpoint['rows']),'status':checkpoint['status']}))
