"""Read-only rev1/rev2 geometry audit; never executes generator output writes."""
import json, hashlib
from pathlib import Path
import numpy as np
S=Path(__file__).resolve().parent

def measure():
 source=(S/'gen_batch3_rev1.py').read_text()
 start=source.index("p=make(18,'halo_arch')")
 end=source.index("for name,c in [('crystal_bank",start)
 namespace={}
 exec(source[:source.index('for j in range(2):')],namespace)
 exec(source[start:end],namespace)
 old=namespace['p'];path=namespace['path']
 current=json.loads((S/'parts.json').read_text())
 new=next(p for p in current if p['id']=='h18_halo_arch')
 assert np.array_equal(old.anchor,new['anchor']), 'Arch pivot changed'
 revised_source=(S/'gen_batch3.py').read_text()
 begin=revised_source.index("p=make(18,'halo_arch')")
 stop=revised_source.index("for name,c in [('crystal_bank",begin)
 exec(revised_source[begin:stop],namespace)
 expected=namespace['p']
 for m,(v,f) in expected.g.items():
  assert np.array_equal(v,new['groups'][m]['verts']) and f==new['groups'][m]['faces'], 'Generated mesh mismatch'
 verts=np.concatenate([g['verts'] for g in new['groups'].values()])
 deviations=[];thickness=[];inner_faces=0
 # Every rev1 segment has two ten-vertex rings, derived by executing rev1 code above.
 oldverts=np.array(old.g['Ice'][0])
 newfaces=[np.array(g['verts'])[f] for g in new['groups'].values() for f in g['faces']]
 for i,(aa,bb) in enumerate(zip(path,path[1:])):
  ring=oldverts[i*20:(i+1)*20];base=np.array([aa]*10+[bb]*10)-old.anchor
  d=np.array(bb)-aa;d=d/np.linalg.norm(d);out=np.cross(d,[0,0,1]);out/=np.linalg.norm(out)
  if out@(np.array(aa)+np.array(bb))/2-out@np.array([0,18.6,-52])<0:out=-out
  q=(ring-base)@out
  want=ring+2*np.maximum(q,0)[:,None]*out
  # Verify actual exported-source vertices and complete inward side facets.
  for v in want: assert np.min(np.linalg.norm(verts-v,axis=1))<1e-12
  for v in ring[q<=0]:deviations.append(float(np.min(np.linalg.norm(verts-v,axis=1))))
  for j in range(10):
   ids=[j,(j+1)%10,(j+1)%10+10,j+10]
   face=ring[ids];values=q[ids];clipped=[]
   for k in range(4):
    v0=face[k];v1=face[(k+1)%4];q0=values[k];q1=values[(k+1)%4]
    if q0<=0:clipped.append(v0)
    if q0*q1<0:clipped.append(v0+(v1-v0)*(-q0/(q1-q0)))
   if len(clipped)>=3:
    face=np.array(clipped)
    assert any(f.shape==face.shape and all(np.min(np.linalg.norm(f-v,axis=1))<1e-12 for v in face) for f in newfaces), 'Inner surface portion moved'
    inner_faces+=1
  assert np.all(want[:,1]>=ring[:,1]-1e-12), 'Downward thickening'
  assert np.array_equal(want[:,2],ring[:,2]), 'Depth profile moved'
  thickness.append([float(np.ptp(q[:10])),float(np.ptp((want-base)[:10]@out))])
 assert np.allclose(np.array(thickness)[:,1],2*np.array(thickness)[:,0])
 # Foot positions = source segment base centres; complete inward base half is fixed.
 assert path[0]==[-23,.5,-52] and path[-1]==[23,.5,-52]
 baseline=json.loads((S/'parts_rev1.json').read_text())
 polish_ids=set(json.loads((S/'polish_ids.json').read_text())) if (S/'polish_ids.json').exists() else set()
 if polish_ids:
  prepolish={p['id']:p for p in json.loads((S/'parts_prepolish.json').read_text())}
  for p in current:
   if p['id'] not in polish_ids:assert p==prepolish[p['id']], 'Unexpected polish change: '+p['id']
 for p in current:
  prior=next(v for v in baseline if v['id']==p['id'])
  if p['id']=='h18_halo_arch' or p['id'] in polish_ids:continue
  groups={m:g for m,g in prior['groups'].items() if p['id']!='h06_kettle_pool' or m!='Steam'}
  assert p['groups']==groups, 'Unexpected change: '+p['id']
 result=dict(parts_sha256=hashlib.sha256((S/'parts.json').read_bytes()).hexdigest(),
  crown_thickness_rev1_rev2=thickness[len(thickness)//2],
  legs_thickness_rev1_rev2=[thickness[0],thickness[-1]],
  all_segment_thickness_rev1_rev2=thickness,inner_edge_max_deviation=max(deviations),
  fixed_inner_facets=inner_faces,foot_centres=[path[0],path[-1]],
  all_pass=True,method='Execute rev1 arch block, audit actual rev2 vertices and unchanged inward facets; thickness along each segment outward normal')
 return result
if __name__=='__main__':
 result=measure();(S/'arch_rev2_measurements.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
