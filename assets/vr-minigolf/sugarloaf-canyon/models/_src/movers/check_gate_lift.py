import json,math
import numpy as np
from fitcheck_movers import SRC,sat,transformed
from registry_movers import REG,motion
e=REG[2];gate=np.array(json.loads((SRC/'h11_lock_gate_triangles.json').read_text()))
comps=json.loads((SRC/'h11_lock_lift_components.json').read_text());best=dict(clearance=float('inf'))
seen=set()
for t in np.linspace(0,9.6,1921):
 g,gd,_=transformed(e,float(t),gate);d,tilt=motion('h11_lock_lift',float(t));key=(round(gd,8),round(d,8),round(tilt,8))
 if key in seen:continue
 seen.add(key)
 v=g-np.array(REG[3]['pivot']);a=math.radians(tilt);y=(v[:,:,1]-d).copy();z=(v[:,:,2]+2).copy()
 v[:,:,1]=y*math.cos(a)-z*math.sin(a);v[:,:,2]=y*math.sin(a)+z*math.cos(a)-2
 lo=v.min((0,1));hi=v.max((0,1))
 for i,c in enumerate(comps):
  c0=np.array(c['center']);s=np.array(c['size']);sep=np.maximum(np.maximum(lo-c0-s/2,c0-s/2-hi),0)
  if max(sep)>best['clearance']:continue
  distance,location=sat(v,c0,s,0)
  if distance<best['clearance']:best=dict(clearance=distance,time=float(t),gate_offset=gd,lift_offset=d,tilt=tilt,platform_component=i,location_platform_local=location)
best['pass']=best['clearance']>=.05-1e-6
(SRC/'gate_lift_pair_pass2.json').write_text(json.dumps(best,indent=2));print(json.dumps(best))
if not best['pass']:raise RuntimeError('gate/lift pair fails')
