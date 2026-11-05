from pathlib import Path
S=Path(__file__).resolve().parent;p=S/'fitcheck_batch2.py';t=p.read_text();a=t.index('   dressing=[]');b=t.index('  tris=',a)
t=t[:a]+'''   dressing=[]
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
   if dressing and dressing[0][0]<.05-1e-5:fail.append('mover to dressing full sweep <0.05')
''' +t[b:];p.write_text(t)
