"""Pass 2 raw-source and spatially cut residual checks; no blanket hole exemptions."""
import json, math, datetime
import numpy as np
from registry_movers import REG,HOLES,motion
from fitcheck_movers import SRC,sat,transformed
CUTS={};CUT_THRESH={}
for idx in (5,10):
 h=HOLES[idx]
 names={x['id'] for x in h.get('walls',[])+h.get('rails',[])}
 for cut in h['collision_cuts']:
  prop={'sluice_gate':'h06_sluice_gate','lock_gate':'h11_lock_gate','lock_lift_deck':'h11_lock_lift','quay_lip':'h11_quay_lip'}[cut['mover']]
  for target in cut['targets']:
   obstacles=[w['id'] for w in h.get('walls',[])+h.get('rails',[])]+['felt_'+f['id'] for f in h['felt']]
   root=target if target in names or any(n.startswith(target+'__cut') for n in names) else 'felt_'+target
   for ob in [n for n in obstacles if n==root or n.startswith(root+'__cut')]:
    key=(prop,ob)
    if key in CUTS:
     CUTS[key]=(np.minimum(CUTS[key][0],cut['min']).tolist(),np.maximum(CUTS[key][1],cut['max']).tolist())
    else:CUTS[key]=(cut['min'],cut['max'])
    CUT_THRESH[key]=cut['clearance']

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
 results={};lines=['SRV-132 PASS 3: source raw overlaps and required Studio/holes-collision cuts',
 'SAT signed lower bounds, triangle versus OBB; primitive static AABBs conservative.',
 'dt <= .005 s, translation <= .05 stud (lip speed 10), other movers <= .015; tilt <= .134 degree; explicit top sweep <= .25 degree.',
 'holes_rev.json APPROVED COLLISION CUT SET: exact pairs and cut volumes below. Residual obstacle geometry must clear >=.05.',
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
  tri=np.array(json.loads((SRC/(e['id']+'_triangles.json')).read_text()));period=7.866666666666667 if e['hole']==5 else 10.6
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
   threshold=.15 if e['id']=='h06_sluice_gate' and name=='h06_sluice_frame_1' else CUT_THRESH.get((e['id'],name),.05)
   passed=g>=threshold-1e-6 or contact
   b['status']='CONTACT APPROVED' if contact and g<.05 else 'PASS' if passed else 'FAIL'
   ok &= passed
   if not contact and g<minimum[0]:minimum=(g,dict(prop=e['id'],obstacle=name,**b))
   lines.append(b['status']+' '+name+' '+json.dumps(b))
  for name,b in raw.items():lines.append('DESIGNED APERTURE / REPLACEMENT '+name+' raw='+json.dumps(b))
  results[e['id']]=dict(pairs=best,raw_whitelist=raw)
  ent=next(x for x in json.loads((SRC/'movers_manifest.json').read_text())['movers'] if x['id']==e['id']);budget=all(x['tris']<20000 for x in ent['meshes']);ok &= budget;lines.append('Mesh budget '+('PASS' if budget else 'FAIL'))
 # Moving/moving pairs: transform triangle mesh into the other mover's rest frame.
 for first,second in [('h11_lock_gate','h11_lock_lift'),('h11_quay_lip','h11_lock_lift'),('h11_quay_lip','h11_lock_gate')]:
  e=next(x for x in REG if x['id']==first);base=next(x for x in REG if x['id']==second)
  tri=np.array(json.loads((SRC/(first+'_triangles.json')).read_text()));comps=json.loads((SRC/(second+'_components.json')).read_text())
  bestpair=dict(clearance=float('inf'));seen=set()
  for t in np.linspace(0,10.6,2121):
   v,d1,a1=transformed(e,float(t),tri);d2,a2=motion(second,float(t));key=tuple(round(x,9) for x in (d1,a1,d2,a2))
   if key in seen:continue
   seen.add(key);v-=np.array(base['pivot']);v[:,:,1]-=d2
   if second=='h11_lock_lift':
    a=math.radians(a2);y=v[:,:,1].copy();z=v[:,:,2]
    v[:,:,1]=y*math.cos(a)-z*math.sin(a);v[:,:,2]=y*math.sin(a)+z*math.cos(a)
   lo=v.min((0,1));hi=v.max((0,1))
   for j,c in enumerate(comps):
    cc=np.array(c['center']);ss=np.array(c['size']);sep=np.maximum(np.maximum(lo-cc-ss/2,cc-ss/2-hi),0)
    if max(sep)>bestpair['clearance']:continue
    g,loc=sat(v,cc,ss,0)
    if g<bestpair['clearance']:bestpair=dict(clearance=g,time=float(t),offset=d1,tilt=a1,other_offset=d2,other_tilt=a2,component=j,location_other_pivot_local=loc,kind='moving pair',residual_cut=False)
  bestpair['status']='PASS' if bestpair['clearance']>=.05-1e-6 else 'FAIL';ok &= bestpair['status']=='PASS'
  results[first]['pairs'][second]=bestpair
  results[second]['pairs'][first]=dict(bestpair,location_note='location expressed in '+second+' rest frame')
  lines.append('MOVING PAIR '+first+' / '+second+' '+json.dumps(bestpair))
  if bestpair['clearance']<minimum[0]:minimum=(bestpair['clearance'],dict(prop=first,obstacle=second,**bestpair))
 per_prop={p:min((dict(obstacle=n,**b) for n,b in v['pairs'].items() if b['status']!='CONTACT APPROVED'),key=lambda b:b['clearance']) for p,v in results.items()}
 for p,b in per_prop.items():lines.append('PROP MIN '+p+' '+json.dumps(b))
 timing=(motion('h11_lock_lift',9.15)==(0,0) and motion('h11_lock_gate',5.5)[0]==0);ok &= timing
 lines+=['\nTIMING '+('PASS' if timing else 'FAIL')+': rise 5.50–7.50; tilt/release 7.50–7.65; return 7.65–9.15; gate begins lowering 9.95; fully down 10.60; .80 s margin after return.',
 'MIN NON-EXEMPT '+json.dumps(minimum[1]),'ALL PASS: '+('YES' if ok else 'NO'),
 'Validation is conditional on implementing the listed Studio/holes collision cuts and removing static lock felt. Source already contains approved split collision pieces; residual cut volumes checked as specified.']
 prefix='fitcheck_movers_pass3'
 (SRC/(prefix+'_'+('validated' if ok else 'failed')+'.txt')).write_text('\n'.join(lines),encoding='utf-8')
 (SRC/'fitcheck_results_pass3.json').write_text(json.dumps(dict(all_pass=bool(ok),minimum=minimum[1],cuts=[dict(prop=p,obstacle=o,min=c[0],max=c[1]) for (p,o),c in CUTS.items()],results=results,per_prop_minima=per_prop),indent=2))
 with (SRC/'PROGRESS.md').open('a') as f:f.write('\n- '+datetime.datetime.now().astimezone().isoformat()+' Pass 3 sweep completed: ALL PASS '+str(ok)+'; minimum '+str(minimum)+'\n')
 print('\n'.join(lines))
if __name__=='__main__':main()
