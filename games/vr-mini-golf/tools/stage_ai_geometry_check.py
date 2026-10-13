"""Compare built native wall boxes with authored boxes, without touching the place."""
import json,math
from pathlib import Path
OUT=Path('playtests/stage-ai')
spec=json.loads(Path('../../assets/vr-mini-golf/aurora-archipelago/holes.json').read_text())
built=json.loads((OUT/'built-bounds.json').read_text())
rows=[]
for h,b in zip(spec['holes'],built['holes']):
 for w in h['walls']:
  found=[p for p in b['geometry'] if p.get('wall')==w['id']]
  errors=[]
  for p in found:
   a=math.radians(w.get('yaw',0));c,s=math.cos(a),math.sin(a)
   local=[]
   for v in p['corners']:
    x,y,z=[v[i]-w['center'][i] for i in range(3)]
    local.append([c*x-s*z,y,s*x+c*z])
   errors.append(max(abs(min(v[i] for v in local)+w['size'][i]/2) for i in range(3)))
   errors.append(max(abs(max(v[i] for v in local)-w['size'][i]/2) for i in range(3)))
  rows.append({'hole':h['number'],'wall':w['id'],'parts':len(found),'max_bound_error':max(errors) if errors else None,'pass':len(found)==1 and max(errors)<0.001})
r={'walls':len(rows),'pass':sum(x['pass'] for x in rows),'failures':[x for x in rows if not x['pass']],'max_error':max(x['max_bound_error'] or 0 for x in rows),'rows':rows}
(OUT/'wall-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n')
print({k:v for k,v in r.items() if k!='rows'})
felts=[]
for h,b in zip(spec['holes'],built['holes']):
 for f in h['felt']:
  parts=[p for p in b['geometry'] if p.get('piece')==f['id'] and p['surface']]
  top=[p['corners'][i] for p in parts for i in (2,3,6,7)]
  a=math.radians(f.get('yaw',0));c,s=math.cos(a),math.sin(a)
  slope=f.get('slope') or {};axis=slope.get('axis');rise=slope.get('rise',0)
  coords=[];errors=[]
  for v in top:
   x,y,z=[v[i]-f['center'][i] for i in range(3)]
   xx,zz=c*x-s*z,s*x+c*z
   yy=(xx/f['size'][0] if axis=='x' else zz/f['size'][1] if axis=='z' else 0)*rise
   errors.append(abs(y-yy));coords.append((xx,zz))
  extent_error=max(abs(min(v[i] for v in coords)+f['size'][i]/2) for i in range(2)) if coords else None
  if coords:extent_error=max(extent_error,max(abs(max(v[i] for v in coords)-f['size'][i]/2) for i in range(2)))
  felts.append({'hole':h['number'],'piece':f['id'],'parts':len(parts),'plane_error':max(errors) if errors else None,'extent_error':extent_error,'pass':bool(parts) and max(errors)<0.001 and extent_error<0.001})
fr={'pieces':len(felts),'pass':sum(x['pass'] for x in felts),'failures':[x for x in felts if not x['pass']],'rows':felts}
(OUT/'felt-geometry-check.json').write_text(json.dumps(fr,indent=2)+'\n')
print({k:v for k,v in fr.items() if k!='rows'})
