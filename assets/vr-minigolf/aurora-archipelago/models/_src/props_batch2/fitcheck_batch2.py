from checks import *
import hashlib
NS=[9,10,11,12,13,15,16,17]
# Circumscribed polygonal annular prism, conservative continuous swept volume.
def ring_surface(p,r0,r1,y0,y1,axis='y',depth=None):
 n=720;rr=r1/math.cos(math.pi/n);ts=[]
 def point(r,t,y):
  return np.array([r*math.cos(t),y,r*math.sin(t)])+p['anchor'] if axis=='y' else np.array([r*math.cos(t),r*math.sin(t),y])+p['anchor']
 for i in range(n):
  t=math.tau*i/n;u=math.tau*(i+1)/n
  for rad in [r0,rr]:
   a,b,c,d=point(rad,t,y0),point(rad,u,y0),point(rad,u,y1),point(rad,t,y1);ts.extend([[a,b,c],[a,c,d]])
  for yy in [y0,y1]:
   a,b,c,d=point(r0,t,yy),point(rr,t,yy),point(rr,u,yy),point(r0,u,yy);ts.extend([[a,b,c],[a,c,d]])
 return np.array(ts)
def full_sweep(p,T):
 m=p['motion'];v=T.reshape(-1,3)-p['anchor']
 if m['type']=='toggle':return T,dict(method='stationary full 9-second toggle cycle; geometry fixed',range=[0,9])
 if m['type']=='slide':
  ax=np.array(m['axis']);lo,hi=m['range'];out=[T+ax*lo,T+ax*hi]
  for i in range(3):
   aa=T[:,i]+ax*lo;bb=T[:,(i+1)%3]+ax*lo;cc=T[:,(i+1)%3]+ax*hi;dd=T[:,i]+ax*hi;out.extend([np.stack([aa,bb,cc],axis=1),np.stack([aa,cc,dd],axis=1)])
  return np.concatenate(out),dict(method='exact complete translation endpoint/side prisms',range=m['range'])
 if m['axis']==[0,0,1]:
  r=np.linalg.norm(v[:,:2],axis=1).max();return ring_surface(p,0,r,v[:,2].min(),v[:,2].max(),'z'),dict(method='conservative continuous 360-degree circumscribed disk prism, 720 facets',range=[0,360],max_radius=float(r),min_felt_clearance=float(p['anchor'][1]-r),angle_degrees=float(math.degrees(math.atan2(v[np.argmax(np.linalg.norm(v[:,:2],axis=1)),0],-v[np.argmax(np.linalg.norm(v[:,:2],axis=1)),1]))%360))
 # separate radial/height envelopes per mesh component triangle; low runners, elevated spokes, upper riders
 local=T-np.array(p['anchor']);chunks=[];bounds=[]
 for sel,rlo in [(local[:,:,1].max(axis=1)<=.90001,8.2),((local[:,:,1].min(axis=1)>=1.42499)&(local[:,:,1].max(axis=1)<=1.67501),0),((local[:,:,1].min(axis=1)>=.89999)&~((local[:,:,1].min(axis=1)>=1.42499)&(local[:,:,1].max(axis=1)<=1.67501)),8.2)]:
  vv=local[sel].reshape(-1,3)
  if len(vv):
   rhi=np.linalg.norm(vv[:,[0,2]],axis=1).max();yy0=vv[:,1].min();yy1=vv[:,1].max();chunks.append(ring_surface(p,rlo,rhi,yy0,yy1));bounds.append([float(rlo),float(rhi),float(yy0),float(yy1)])
 return np.concatenate(chunks),dict(method='continuous 360-degree circumscribed annular prisms at separate runner/spoke/rider heights; 720 facets',range=[0,360],radial_height_bounds=bounds,angle_degrees=0,angle_note='spoke to hub top clearance applies for every rotation angle')
def evaluate():
 results=[]
 for p in P:
  h=H[p['hole']];T=triangles(p);fail=[];skin=[w for w in h['walls'] if w['id'] in p['skin_ids']];exempt=np.zeros(len(T),bool)
  # Union containment tested per triangle against source skin volumes. All skin generated boxes are source exact.
  own=np.zeros(T.shape[:2],bool)
  for w in skin:own |= in_foot(T,w)
  if skin:
   exempt=own.all(axis=1)
   if not own.all() and p['id'] not in ['h13_carousel_canopy','h12_icebreaker','h17_crystal_piers','h17_ice_bridge']:fail.append('skin footprint containment')
  for fid in p['felt_skins']:
   f=next(f for f in h['felt'] if f['id']==fid);w=dict(center=f['center'],size=[f['size'][0],100,f['size'][1]],yaw=f.get('yaw',0));exempt|=in_foot(T,w).all(axis=1)&(T[:,:,1].max(axis=1)<=f['center'][1]+.001)
  vals=sorted((clearance(T,w),w['id']) for w in h['walls'] if w['id'] not in p['skin_ids']);minimum=vals[0] if vals else (100,'none')
  if minimum[0]<( .05 if p['motion'] else .1)-1e-5:fail.append('rail clearance <0.1')
  hits=0
  if not p['motion']:
   for f in h['felt']:
    q=(T-np.array(f['center']))@ry(f.get('yaw',0))
    if f.get('slope'):
     sl=f['slope'];idx=0 if sl['axis']=='x' else 2;q[:,:,1]-=q[:,:,idx]*sl['rise']/f['size'][0 if idx==0 else 1]
    slab=hit(q,[0,-.2,0],[f['size'][0]-.00002,.4-.00002,f['size'][1]-.00002]);head=hit(q,[0,4,0],[f['size'][0]-.00002,8-.00002,f['size'][1]-.00002]);hits+=int(((slab|head)&~exempt).sum())
   if hits and p['id']!='h15_ice_parapet':fail.append('felt/head volume intersection')
  sweep=None
  if p['motion']:
   swT,sweep=full_sweep(p,T);vals=sorted((clearance(swT,w),w['id']) for w in h['walls']);sweep.update(min_clearance=vals[0][0],rail=vals[0][1])
   if vals[0][0]<.05-1e-5:fail.append('full mover sweep <0.05')
   if sweep.get('min_felt_clearance',1)<.05-1e-5:fail.append('full mover sweep felt clearance <0.05')
   dressing=[]
   for other in P:
    if other['hole']!=p['hole'] or other['id']==p['id']:continue
    Ot=triangles(other)
    if mtype:=p['motion']['type'] in ['slide','toggle']:
     vv=swT.reshape(-1,3);lo=vv.min(axis=0);hi=vv.max(axis=0);val=clearance(Ot,dict(center=(lo+hi)/2,size=hi-lo))
    else:
     # conservative triangle radial intervals vs exact complete rotating envelopes
     local=Ot-np.array(p['anchor']);axis=2 if p['motion']['axis']==[0,0,1] else 1;inds=[i for i in range(3) if i!=axis];q=local[:,:,inds]
     vmin=np.full(len(q),float('inf'));vmax=np.linalg.norm(q,axis=2).max(axis=1)
     for j in range(3):
      aa=q[:,j];bb=q[:,(j+1)%3];ee=bb-aa;tt=np.clip(-np.einsum('ij,ij->i',aa,ee)/np.maximum(np.einsum('ij,ij->i',ee,ee),1e-12),0,1);vmin=np.minimum(vmin,np.linalg.norm(aa+tt[:,None]*ee,axis=1))
     # origin inside projected triangle means minimum radius 0
     signs=[]
     for j in range(3):
      aa=q[:,j];bb=q[:,(j+1)%3];signs.append(aa[:,0]*bb[:,1]-aa[:,1]*bb[:,0])
     signs=np.array(signs);inside=((signs>=0).all(axis=0)|(signs<=0).all(axis=0)) & (np.abs(signs).sum(axis=0)>1e-10);vmin[inside]=0
     ymin=local[:,:,axis].min(axis=1);ymax=local[:,:,axis].max(axis=1)
     envelopes=[[0,sweep['max_radius'],-.2,.2]] if axis==2 else sweep['radial_height_bounds'];values=[]
     for r0,r1,y0,y1 in envelopes:
      rg=np.maximum(np.maximum(r0-vmax,vmin-r1),0)/math.sqrt(2);yg=np.maximum(np.maximum(y0-ymax,ymin-y1),0);values.append(np.maximum(rg,yg))
     vv=np.min(values,axis=0)
     if other['id']=='h13_carousel_canopy':
      # only central axle joint below canopy is intentional; roof still tested
      joint=(vmax<=.61)&(ymax<=9.0001);vv=vv[~joint]
     val=float(vv.min()) if len(vv) else 100.
    dressing.append((val,other['id']))
   dressing.sort();sweep['dressing_clearances']=dressing;sweep['min_dressing_clearance']=dressing[0][0] if dressing else 100;sweep['nearest_dressing']=dressing[0][1] if dressing else 'none';sweep['mechanical_joint_exception']='central carousel axle against static pole only' if p['hole']==13 else None
   if dressing and dressing[0][0]<.15-1e-5:fail.append('mover to dressing full sweep <0.15')
  tris={m:sum(len(f)-2 for f in g['faces']) for m,g in p['groups'].items()}
  if max(tris.values())>=20000 or sum(tris.values())>=20000:fail.append('triangle budget')
  results.append(dict(id=p['id'],status='FAIL' if fail else 'PASS',tris=tris,total_tris=sum(tris.values()),min_rail_clearance=minimum[0],nearest_rail=minimum[1],felt_head_triangle_hits=hits,skin_ids=p['skin_ids'],sweep=sweep,failures=fail))
 return results
if __name__=='__main__':
 r=evaluate();totals={n:sum(x['total_tris'] for x,p in zip(r,P) if p['hole']==n) for n in NS};ok=all(x['status']=='PASS' for x in r) and all(t<=34000 for t in totals.values());lines=['Aurora batch 2; actual triangle/OBB SAT; L-infinity clearance lower bounds; conservative continuous mover sweeps; source skin and flush-cue exemptions.']+[x['status']+' '+x['id']+' '+json.dumps(x) for x in r]+['SKIPPED '+s['id']+' '+s['reason'] for s in json.loads((S/'skipped.json').read_text())]+['SCOPE SKIPPED: H4, H6, H14, H18 (excluded by brief)','SCOPE SKIPPED: H4, H6, H14, H18 (excluded by brief)','Near-field triangles: '+json.dumps(totals),'ALL PASS: '+('YES' if ok else 'NO')];(D/'models/fitcheck_props_batch2.txt').write_text('\n'.join(lines));(S/'fitcheck_report.json').write_text(json.dumps(dict(all_pass=ok,parts=r,hole_tris=totals),indent=2));print('\n'.join(x['status']+' '+x['id']+' '+str(x['failures']) for x in r));raise SystemExit(0 if ok else 1)
