#!/usr/bin/env python3
"""Full-cycle OBB separating-axis lower bounds for colliders, felt, and authored decorative occluder boxes; excludes unmodeled mesh details."""
import argparse,json,os,math
import numpy as np
import sim as S
from numba import njit
@njit(cache=True)
def sat_gap(c,h,r,sc,sh,sr):
 best=0.0
 for n in range(15):
  if n<3: axis=r[:,n].copy()
  elif n<6: axis=sr[:,n-3].copy()
  else: axis=np.cross(r[:,(n-6)//3],sr[:,(n-6)%3])
  norm=np.sqrt(np.sum(axis*axis))
  if norm<1e-9:continue
  axis/=norm
  gap=abs(np.dot(sc-c,axis))-np.sum(np.abs(axis@r)*h)-np.sum(np.abs(axis@sr)*sh)
  best=max(best,gap)
 return best
course=json.load(open(os.path.join(S.HERE,'..','holes.json')))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',default=os.path.join(S.HERE,'out','p7-clearance.json'))
opts=parser.parse_args()
results=[]
for hn in (6,11):
 h=next(h for h in course['holes'] if h['number']==hn);ha=S.HoleArrays(h);statics=[]
 for w in h['walls']:
  c=np.array(w['center']);extent=np.abs(S.yaw_R(w.get('yaw',0))) @ (np.array(w['size'])/2)
  statics.append((w['id'],c,np.array(w['size'])/2,S.yaw_R(w.get('yaw',0))))
 for anchor in h.get('decoration_anchors',[]):
  for oi,box in enumerate(anchor.get('occluders',[])):
   statics.append(('decor:'+anchor['name']+':'+str(oi),np.array(box['center'],float),np.array(box['size'],float)/2,S.yaw_R(box.get('yaw',0))))
 for f in h['felt']:
  thickness=f.get('thickness',.4);r=S.yaw_R(f.get('yaw',0));half=np.array([f['size'][0]/2,thickness/2,f['size'][1]/2]);c=np.array(f['center'],float)
  sl=f.get('slope')
  if sl:
   ax=0 if sl['axis']=='x' else 2;ang=math.atan(sl['rise']/f['size'][0 if ax==0 else 1]);co=math.cos(ang);si=math.sin(ang)
   tilt=np.array([[co,-si,0],[si,co,0],[0,0,1]]) if ax==0 else np.array([[1,0,0],[0,co,si],[0,-si,co]])
   r=r@tilt;half[ax]/=co
  c-=r[:,1]*thickness/2
  statics.append(('felt:'+f['id'],c,half,r))
 Rth=np.empty(9);Rw=np.empty(9);cen=np.empty(3)
 for j,m in enumerate(h['moving_parts']):
  best=(1e9,None,None);exceptions=set();samples=max(1921,math.ceil(S.cycle_period(m)/.005)+1)
  for t in np.linspace(0,S.cycle_period(m),samples,endpoint=False):
   for k in range(ha.nMB):
    if int(ha.MB[k,0])!=j:continue
    S.blocker_pose(ha.MP,ha.MB,k,t,Rth,Rw,cen);ext=np.abs(Rw.reshape(3,3))@ha.MB[k,4:7];lo=cen-ext;hi=cen+ext
    for name,sc,sh,sr in statics:
     if hn==6 and name=='felt:neck':exceptions.add(name);continue # Authored sliding board rests on neck felt; visual bottom is raised .02.
     d=sat_gap(cen,ha.MB[k,4:7],Rw.reshape(3,3),sc,sh,sr)
     if d<best[0]:best=(d,name,float(t))
  results.append(dict(hole=hn,part=m['id'],samples=samples,dt=S.cycle_period(m)/samples,minimum_lower_bound=best[0],obstacle=best[1],time=best[2],support_contact_exceptions=sorted(exceptions),pass_=best[0]>=.15-1e-6))
print(json.dumps(results,indent=2))
os.makedirs(os.path.dirname(os.path.abspath(opts.out)),exist_ok=True)
json.dump(results,open(opts.out,'w'),indent=2)
assert all(r['pass_'] for r in results)
