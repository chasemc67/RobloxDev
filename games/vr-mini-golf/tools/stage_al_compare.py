"""Verify final collider geometry and non-test physics match the preflight snapshot."""
import json
from pathlib import Path
out=Path('playtests/stage-al')
a=json.loads((out/'before-colliders.json').read_text());b=json.loads((out/'final-colliders.json').read_text())
assert len(a)==len(b)
changes=[]
for old,new in zip(a,b):
 if old['physics']!=new['physics']:
  assert '.Hole15.' in old['path'] and old.get('wall'), (old,new)
  assert all(old['physics'][i]==new['physics'][i] for i in (0,2,4))
  assert abs(new['physics'][1]-.1)<1e-6 and new['physics'][3]==100
  changes.append(old['wall'])
 assert {k:v for k,v in old.items() if k!='physics'}=={k:v for k,v in new.items() if k!='physics'}, (old,new)
assert len(changes)==12
report={'colliders':len(a),'geometry_unchanged':True,'only_h15_friction_changed':changes,'density_elasticity_preserved':True}
(out/'collider-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
