"""World placement evaluated against every hole, using reused triangle/OBB SAT."""
from checks import *
p=json.loads((S/'h15_part.json').read_text())
actual=S/'h15_triangles.json'
if actual.exists():T=np.array(json.loads(actual.read_text()))+p['anchor']
else:
 ts=[]
 for g in p['groups'].values():
  for f in g['faces']:
   for i in range(1,len(f)-1):ts.append([g['verts'][f[0]],g['verts'][f[i]],g['verts'][f[i+1]]])
 T=np.array(ts)+p['anchor']
W=json.loads((D/'world/world.json').read_text());placements={h['number']:h['placement'] for h in W['holes']}
results=[]
for n,h in H.items():
 pl=placements[n];Q=(T-np.array(pl['origin']))@ry(pl['yaw_deg'])
 # Whole-mesh separating-axis bounds give a conservative rail lower bound;
 # detailed SAT used for every rail within 100 studs.
 rails=[]
 for w in h['walls']:
  q=(Q-np.array(w['center']))@ry(w.get('yaw',0));lo=q.reshape(-1,3).min(0);hi=q.reshape(-1,3).max(0);half=np.array(w['size'])/2
  lower=float(np.maximum(np.maximum(lo-half,-half-hi),0).max())
  val=clearance(Q,w) if lower<100 else lower
  rails.append((val,w['id']))
 hits=0
 for f in h['felt']:
  q=(Q-np.array(f['center']))@ry(f.get('yaw',0))
  if f.get('slope'):
   sl=f['slope'];idx=0 if sl['axis']=='x' else 2;q[:,:,1]-=q[:,:,idx]*sl['rise']/f['size'][0 if idx==0 else 1]
  hits+=int((hit(q,[0,-.2,0],[f['size'][0]-.00002,.4-.00002,f['size'][1]-.00002])|hit(q,[0,4,0],[f['size'][0]-.00002,8-.00002,f['size'][1]-.00002])).sum())
 val,wid=min(rails) if rails else (100,'none')
 results.append(dict(hole=n,min_rail_clearance=val,nearest_rail=wid,felt_head_triangle_hits=hits,status='PASS' if val>=.1-1e-5 and hits==0 else 'FAIL'))
report=dict(all_pass=all(r['status']=='PASS' for r in results),method='All 18 holes transformed through authoritative world placements; triangle/OBB SAT, slope shear, .1 rail and felt +0..8 head gates; conservative L-infinity distances',geometry='FBX triangulation' if actual.exists() else 'generator triangulation',parts=results)
(S/'h15_fitcheck.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
