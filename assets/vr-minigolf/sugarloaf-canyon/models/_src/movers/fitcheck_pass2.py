"""Pass 2 raw-source and spatially cut residual checks; no blanket hole exemptions."""
import json, math, datetime
import numpy as np
from registry_movers import REG,HOLES,motion
from fitcheck_movers import SRC,sat,transformed

# Hole-local cut bounds. Collision cuts are handoff requirements, not source edits.
CUTS={
 ('h06_sluice_gate','rail5'):([-10.56,-.04,-28.38],[3.56,1.08,-27.62]),
 ('h11_lock_gate','rail4'):([-1.86,-1.36,-21.58],[1.86,1.26,-20.92]),
 ('h11_lock_gate','rail8'):([-1.86,-1.36,-21.58],[1.86,1.26,-20.92]),
 ('h11_lock_gate','felt_lock'):([-1.86,-1.36,-21.58],[1.86,1.26,-20.92]),
 ('h11_lock_lift','felt_lock'):([-1.66,-.21,-25.06],[1.66,4.36,-20.94]),
 ('h11_lock_lift','rail6'):([-1.66,-.21,-25.06],[1.66,4.36,-24.44]),
 ('h11_lock_lift','quay_rail20'):([-1.66,-.21,-25.06],[1.66,4.36,-24.44]),
 ('h11_lock_lift','felt_quay'):([-1.66,3.79,-25.06],[1.66,4.36,-24.94]),
}
def residual(c,s,yaw,cut):
 a=math.radians(yaw);ext=np.array([abs(math.cos(a))*s[0]+abs(math.sin(a))*s[2],s[1],abs(math.sin(a))*s[0]+abs(math.cos(a))*s[2]])/2
 lo=np.array(c)-ext;hi=np.array(c)+ext;cl=np.maximum(lo,cut[0]);ch=np.minimum(hi,cut[1])
 if np.any(ch<=cl):return [(c,s,yaw)]
 pieces=[]
 for axis in range(3):
  for low in (True,False):
   l=lo.copy();h=hi.copy()
   if low:h[axis]=cl[axis]
   else:l[axis]=ch[axis]
   if np.all(h-l>1e-8):pieces.append(((l+h)/2,h-l,0))
  lo[axis]=cl[axis];hi[axis]=ch[axis]
 return pieces
def main(proposed=False):
 results={};lines=['SRV-132 PASS 2: source raw overlaps and required Studio/holes-collision cuts',
 'SAT signed lower bounds, triangle versus OBB; primitive static AABBs conservative.',
 'dt <= .005 s, translation <= .015 stud; tilt <= .134 degree; explicit top sweep <= .25 degree.',
 'WHITELIST: exact pairs and cut volumes below. Residual obstacle geometry must clear >=.05.',
 'CONTACT exceptions: static felt contact overlap <=.001; H6 gate lifted .02 (felt epsilon .0005).']
 for (prop,ob),cut in CUTS.items():lines.append(f'REQUIRED CUT {prop} / {ob}: min={cut[0]} max={cut[1]}')
 ok=True;minimum=(float('inf'),None)
 for e in REG:
  h=HOLES[e['hole']];obs=[]
  for w in h.get('walls',[])+h.get('rails',[]):obs.append((w['id'],w['center'],w['size'],w.get('yaw',0),'rail/wall'))
  for f in h['felt']:
   rise=(f.get('slope') or {}).get('rise',0);obs.append(('felt_'+f['id'],f['center'],[f['size'][0],max(.001,rise),f['size'][1]],f.get('yaw',0),'felt'))
  cup=h['cup'];obs.append(('cup',cup['position'],[cup['radius']*2,.001,cup['radius']*2],0,'cup'));obs.append(('tee',h['tee']['position'],[2,.001,2],0,'tee'))
  if e['moving']:
   for base in REG:
    if base['hole']==e['hole'] and not base['moving']:
     for j,comp in enumerate(json.loads((SRC/(base['id']+'_components.json')).read_text())):obs.append((base['id']+'_'+str(j),np.array(comp['center'])+base['pivot'],comp['size'],0,'static base'))
  tri=np.array(json.loads((SRC/(e['id']+'_triangles.json')).read_text()));period=7.866666666666667 if e['hole']==5 else 9.6
  times=np.linspace(0,period,math.ceil(period/.005)+1) if e['moving'] else [0]
  states=[(t,None) for t in times]
  if 'lift' in e['id']:states.extend((7.5,float(a)) for a in np.linspace(0,4,17))
  best={};raw={};seen=set()
  for t,angle in states:
   v,d,ang=transformed(e,t,tri,angle);key=(round(d,10),round(ang,10))
   if key in seen:continue
   seen.add(key)
   lo=v.min(axis=(0,1));hi=v.max(axis=(0,1))
   for name,c,s,yaw,kind in obs:
    cut=CUTS.get((e['id'],name));pieces=residual(c,s,yaw,cut) if cut else [(c,s,yaw)]
    if cut:
     g,loc=sat(v,c,s,yaw)
     if g<raw.get(name,{}).get('clearance',float('inf')):raw[name]=dict(clearance=g,time=float(t),offset=d,tilt=ang,location=loc)
    for pc,ps,py in pieces:
     # Cheap conservative bound, used only to skip states unable to improve pair minimum.
     lower=np.linalg.norm(np.maximum(np.maximum(lo-np.array(pc),np.array(pc)-hi),0))-np.linalg.norm(ps)/2
     if lower>best.get(name,{}).get('clearance',float('inf')):continue
     g,loc=sat(v,pc,ps,py)
     if g<best.get(name,{}).get('clearance',float('inf')):best[name]=dict(clearance=g,time=float(t),offset=d,tilt=ang,location=loc,kind=kind,residual_cut=bool(cut))
  lines.append('\n'+e['id'])
  for name,b in best.items():
   g=b['clearance'];contact=b['kind']=='felt' and ((not e['moving'] and g>=-.001) or (e['id']=='h06_sluice_gate' and g>=.0194))
   passed=g>=.05-1e-6 or contact
   b['status']='CONTACT APPROVED' if contact and g<.05 else 'PASS' if passed else 'FAIL'
   ok &= passed
   if not contact and g<minimum[0]:minimum=(g,dict(prop=e['id'],obstacle=name,**b))
   lines.append(b['status']+' '+name+' '+json.dumps(b))
  for name,b in raw.items():lines.append('DESIGNED APERTURE / REPLACEMENT '+name+' raw='+json.dumps(b))
  results[e['id']]=dict(pairs=best,raw_whitelist=raw)
  ent=next(x for x in json.loads((SRC/'movers_manifest.json').read_text())['movers'] if x['id']==e['id']);budget=all(x['tris']<20000 for x in ent['meshes']);ok &= budget;lines.append('Mesh budget '+('PASS' if budget else 'FAIL'))
 timing=(motion('h11_lock_lift',9.15)==(0,0) and motion('h11_lock_gate',5.5)[0]==-1.3);ok &= timing
 lines+=['\nTIMING '+('PASS' if timing else 'FAIL')+': rise 5.50–7.50; tilt/release 7.50–7.65; return 7.65–9.15; gate fully down at 9.60; .45 s margin.',
 'MIN NON-EXEMPT '+json.dumps(minimum[1]),'ALL PASS: '+('YES' if ok else 'NO'),
 'Validation is conditional on implementing the listed Studio/holes collision cuts and removing static lock felt. Uncut source still has the raw intersections listed above.']
 prefix='fitcheck_movers_pass2_proposed' if proposed else 'fitcheck_movers_pass2'
 (SRC/(prefix+'_'+('validated' if ok else 'failed')+'.txt')).write_text('\n'.join(lines),encoding='utf-8')
 (SRC/('fitcheck_results_pass2'+('_proposed' if proposed else '')+'.json')).write_text(json.dumps(dict(all_pass=bool(ok),minimum=minimum[1],cuts=[dict(prop=p,obstacle=o,min=c[0],max=c[1]) for (p,o),c in CUTS.items()],results=results),indent=2))
 with (SRC/'PROGRESS.md').open('a') as f:f.write('\n- '+datetime.datetime.now().astimezone().isoformat()+' Pass 2 sweep completed: ALL PASS '+str(ok)+'; minimum '+str(minimum)+'\n')
 print('\n'.join(lines))
if __name__=='__main__':main()
