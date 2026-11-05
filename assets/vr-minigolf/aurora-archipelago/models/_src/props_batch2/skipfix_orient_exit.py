import json
from pathlib import Path
S=Path(__file__).resolve().parent
f=S/'parts.json';P=json.loads(f.read_text());p=next(p for p in P if p['id']=='h09_conch_exit')
for g in p['groups'].values():
 for v in g['verts']:v[0],v[2]=-v[2],v[0]
p['notes'].append('Mouth rotated west toward teleport exit and cup; rotation baked into mesh, pivot unchanged.')
f.write_text(json.dumps(P))
build=(S/'build_skipfix_guard.py').read_text().replace("CHANGED={'h15_ice_parapet'}","CHANGED={'h09_conch_exit'}").replace('for n in [15]:\n    visible=','for n in [9]:\n    visible=')
(S/'build_skipfix_exit.py').write_text(build)
