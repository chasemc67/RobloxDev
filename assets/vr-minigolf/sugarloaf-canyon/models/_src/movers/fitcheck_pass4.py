"""SRV-132 pass 4 fitcheck against in/holes.json (p8) incl. approved collision_cuts.
Separation = SAT lower bound (triangle vs convex part); negative = penetration. Static props are their exact
recorded convex parts (no AABB inflation). Sweeps: rotors 0.5 deg over 360; bucket 0.25 deg over +-9 plus
period sampling dt .01 s; H6/H11 dt .0025 s plus schedule breakpoints. Thresholds: >=.05 general,
>=.15 mover-to-static-prop and to approved cut residuals (holes.json clearance .15)."""
import json,math,datetime,sys
from pathlib import Path
import numpy as np
from registry_movers import REG,HOLES,motion,period,H11_CYCLE,H6_PERIOD,DAM
from fitcheck_pass3 import residual,CUTS,CUT_THRESH
SRC=Path(__file__).resolve().parent;TOL=1e-6
# ---------------------------------------------------------------- geometry
def Ry(a):a=math.radians(a);return np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
def Rz(a):a=math.radians(a);return np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
def Raxis(axis,deg):
    k=np.array(axis,float);k/=np.linalg.norm(k);a=math.radians(deg);K=np.array([[0,-k[2],k[1]],[k[2],0,-k[0]],[-k[1],k[0],0]])
    return np.eye(3)+math.sin(a)*K+(1-math.cos(a))*K@K
def canon(v):
    v=np.asarray(v,float);n=np.linalg.norm(v,axis=1);v=v[n>1e-9]/n[n>1e-9,None]
    k=np.argmax(np.abs(v),axis=1);v=v*np.sign(v[np.arange(len(v)),k])[:,None]
    return np.unique(np.round(v,7),axis=0)
def mkpoly(V,N,D,E,name='',kind=''):
    V=np.asarray(V,float);N=np.asarray(N,float);D=np.asarray(D,float)
    A=canon(np.vstack([N,np.eye(3)]));E=canon(E)
    return dict(V=V,N=N,D=D,A=A,E=E,lo=V.min(0),hi=V.max(0),name=name,kind=kind)
def box_poly(c,s,yaw=0,roll=0,name='',kind=''):
    R=Ry(yaw)@Rz(roll);h=np.array(s,float)/2
    V=np.array([np.array(c)+R@(h*np.array(sg)) for sg in np.array(np.meshgrid([-1,1],[-1,1],[-1,1])).T.reshape(-1,3)])
    N=np.vstack([R.T,-R.T]);D=np.concatenate([R.T@np.array(c)+h,-(R.T@np.array(c))+h])
    P=mkpoly(V,N,D,R.T,name,kind);P['box']=(list(c),list(s),yaw);return P
def disk_poly(c,r,h,name='',kind='',n=32):
    """Vertical n-gon prism circumscribing a disk of radius r (top at c[1]), conservative for round cups."""
    R=r/math.cos(math.pi/n);a=np.arange(n)*2*math.pi/n;c=np.array(c,float)
    ring=np.stack([R*np.cos(a),np.zeros(n),R*np.sin(a)],1)
    V=np.vstack([ring+c+[0,-h,0],ring+c]);mid=a+math.pi/n
    N=np.vstack([np.stack([np.cos(mid),np.zeros(n),np.sin(mid)],1),[[0,1,0],[0,-1,0]]])
    D=np.concatenate([r+N[:n]@c,[c[1],-(c[1]-h)]])
    E=np.vstack([np.roll(ring,-1,0)-ring,[[0,1,0]]])
    return mkpoly(V,N,D,E,name,kind)
def comp_poly(comp,offset,name,kind,R=None):
    R=np.eye(3) if R is None else R;off=np.array(offset,float)
    V=np.array(comp['verts'])@R.T+off;P=np.array(comp['planes']);N=P[:,:3]@R.T;D=P[:,3]+N@off
    return mkpoly(V,N,D,np.array(comp['edges'])@R.T,name,kind)
def translate(P,d):
    d=np.asarray(d,float);Q=dict(P);Q['V']=P['V']+d;Q['D']=P['D']+P['N']@d;Q['lo']=P['lo']+d;Q['hi']=P['hi']+d;return Q
def sat_cheap(T,P):
    pt=T@P['A'].T;pv=P['V']@P['A'].T
    g=np.maximum(pt.min(1)-pv.max(0),pv.min(0)-pt.max(1)).max(1)
    e=np.roll(T,-1,axis=1)-T;n=np.cross(e[:,0],e[:,1]);nn=np.linalg.norm(n,axis=1);ok=nn>1e-12;n=n/np.maximum(nn,1e-12)[:,None]
    a=np.einsum('nvi,ni->nv',T,n);b=P['V']@n.T
    g2=np.maximum(a.min(1)-b.max(0),b.min(0)-a.max(1));g2[~ok]=-np.inf
    return np.maximum(g,g2)
def sat_cross(T,P):
    e=np.roll(T,-1,axis=1)-T;C=np.cross(e[:,:,None,:],P['E'][None,None,:,:]).reshape(len(T),-1,3)
    cn=np.linalg.norm(C,axis=2);ok=cn>1e-9;C=C/np.maximum(cn,1e-12)[:,:,None]
    a=np.einsum('nvi,nji->nvj',T,C);b=np.einsum('mi,nji->nmj',P['V'],C)
    g=np.maximum(a.min(1)-b.max(1),b.min(1)-a.max(1));g[~ok]=-np.inf
    return g.max(1)
def gap(T,P,best=np.inf):
    """min over triangles of SAT separation lower bound; skips triangles that cannot beat `best`."""
    lo=T.min(1);hi=T.max(1);sep=np.maximum(P['lo']-hi,lo-P['hi']).max(1)
    idx=np.nonzero(sep<best)[0]
    if len(idx)==0:return np.inf,None
    Ts=T[idx];c=sat_cheap(Ts,P);order=np.argsort(c);res=np.inf;arg=None
    for k in range(0,len(order),48):
        sel=order[k:k+48];sel=sel[c[sel]<min(res,best)]
        if len(sel)==0:break
        f=np.maximum(c[sel],sat_cross(Ts[sel],P));j=int(np.argmin(f))
        if f[j]<res:res=float(f[j]);arg=Ts[sel[j]].mean(0).tolist()
    return res,arg
def inside(pts,parts,tol=1e-4):
    ok=np.zeros(len(pts),bool)
    for P in parts:ok|=np.all(pts@P['N'].T-P['D']<=tol,axis=1)
    return ok
def box_samples(c,s,yaw=0,roll=0,n=(5,5,5),ymin=None):
    R=Ry(yaw)@Rz(roll);g=[np.linspace(-.5,.5,k) for k in n];pts=np.array(np.meshgrid(*g)).T.reshape(-1,3)*np.array(s)
    pts=pts@R.T+np.array(c)
    return pts if ymin is None else pts[pts[:,1]>=ymin-1e-9]
# ---------------------------------------------------------------- data
MAN={m['id']:m for m in json.loads((SRC/'movers_manifest.json').read_text())['movers']}
TRI={e['id']:np.array(json.loads((SRC/(e['id']+'_triangles.json')).read_text())) for e in REG}
COMP={e['id']:json.loads((SRC/(e['id']+'_components.json')).read_text()) for e in REG}
def parts_of(e,offset=None,R=None):
    off=e['pivot'] if offset is None else offset
    return [comp_poly(c,off,e['id']+'_'+str(j),'static prop',R) for j,c in enumerate(COMP[e['id']])]
def felt_poly(f):
    rise=(f.get('slope') or {}).get('rise',0);th=f.get('thickness')
    if rise:return box_poly(f['center'],[f['size'][0],max(.001,abs(rise)),f['size'][1]],f.get('yaw',0),name='felt_'+f['id'],kind='felt')
    if th:c=list(f['center']);c[1]-=th/2;return box_poly(c,[f['size'][0],th,f['size'][1]],f.get('yaw',0),name='felt_'+f['id'],kind='felt')
    c=list(f['center']);c[1]-=.0005  # felt centre is its TOP: .001 slab just below the playing surface
    return box_poly(c,[f['size'][0],.001,f['size'][1]],f.get('yaw',0),name='felt_'+f['id'],kind='felt')
def hole_obstacles(e,skip_anchor=()):
    h=HOLES[e['hole']];obs=[]
    for w in h.get('walls',[]):obs.append(box_poly(w['center'],w['size'],w.get('yaw',0),name=w['id'],kind='rail/wall'))
    for f in h['felt']:obs.append(felt_poly(f))
    cup=h['cup'];obs.append(disk_poly(cup['position'],cup['radius'],.001,name='cup',kind='cup'))
    obs.append(box_poly(h['tee']['position'],[2,.001,2],name='tee',kind='tee'))
    for a in h.get('decoration_anchors',[]):
        if a['name'] in skip_anchor:continue
        for j,o in enumerate(a.get('occluders',[])):obs.append(box_poly(o['center'],o['size'],o.get('yaw',0),name='anchor_'+a['name']+'_'+str(j),kind='anchor envelope'))
    return obs
def realized_anchors(hole):return {e.get('realizes_anchor') for e in REG if e['hole']==hole and e.get('realizes_anchor')}
def threshold(e,P):
    if P['kind']=='static prop':return .15
    if (e['id'],P['name']) in CUT_THRESH:return CUT_THRESH[(e['id'],P['name'])]
    if e['id']=='h09_windpump_vanes' and P['kind']=='felt':return .02
    return .05
def contact_ok(e,P,g):
    if P['kind']!='felt':return False
    if not e['moving']:return g>=-.001
    return e['id']=='h06_sluice_gate' and g>=.0194
# ---------------------------------------------------------------- mover states
def states(e):
    n=e['id']
    if e['kind']=='rotate':return [(a/e['speed'],0.0,float(a)) for a in np.arange(0,360,.5)]
    if e['kind']=='swing':
        out=[(None,0.0,float(a)) for a in np.arange(-9,9.0001,.25)]
        out+=[(float(t),0.0,motion(n,float(t))[1]) for t in np.arange(0,e['period']+1e-9,.01)]
        return out
    if e['moving']:
        T=period(n);dt=.0025;ts=set(np.round(np.arange(0,T+1e-9,dt),6))
        ts|={0,5.5,5.8,6.1,6.9,7.0,7.1,9.1,9.2,9.3,10.1,10.4,10.7,1.2,1.2+7/3,3.2+7/3}
        out=[];seen=set()
        for t in sorted(ts):
            if t>T:continue
            d,a=motion(n,t);k=round(d,9)
            if k in seen:continue
            seen.add(k);out.append((float(t),d,a))
        return out
    return [(0.0,0.0,0.0)]
def place(e,tri,d,a):
    piv=np.array(e['pivot'],float)
    if e['kind'] in ('rotate','swing'):return tri@Raxis(e['axis'],a).T+piv
    if e['moving']:return tri+piv+np.array(e['axis'])*d
    return tri+piv
# ---------------------------------------------------------------- checks
def check_prop(e):
    tri=TRI[e['id']];h=HOLES[e['hole']];skip=realized_anchors(e['hole']) if e['moving'] else ({e.get('realizes_anchor')}-{None})
    obs=hole_obstacles(e,skip)
    if e['moving']:
        for b in REG:
            if b['hole']==e['hole'] and not b['moving']:obs+=parts_of(b)
    realized={w['id'] for w in h['walls'] if w['id'] in e.get('realizes',[])}
    vrbox={b['id']:b for b in h.get('vr_comfort',{}).get('boxes',[])}
    if h.get('vr_comfort',{}).get('mist'):vrbox['gap_mist']=h['vr_comfort']['mist']
    own=[box_poly(w['center'],w['size'],w.get('yaw',0)) for w in h['walls'] if w['id'] in realized]+[box_poly(vrbox[i]['center'],vrbox[i]['size'],vrbox[i].get('yaw',0)) for i in e.get('realizes_vr',[])]
    best={};insts=e.get('instances') or [dict(id=None,pivot=e['pivot'])]
    prepared=[]
    for P in obs:
        if P['name'] in realized:continue
        cut=CUTS.get((e['id'],P['name']))
        pieces=[box_poly(c,s,y,name=P['name'],kind=P['kind']) for c,s,y in residual(*P['box'],cut)] if cut else [P]
        prepared.append((P,cut,pieces))
    for t,d,a in states(e):
        for inst in insts:
            T=place(dict(e,pivot=inst['pivot']),tri,d,a)
            for P,cut,pieces in prepared:
                key=P['name']+('' if inst['id'] is None else '@'+inst['id'])
                cur=best.get(key,{}).get('clearance',np.inf)
                for Q in pieces:
                    g,loc=gap(T,Q,cur)
                    if g<cur:
                        cur=g;best[key]=dict(clearance=g,time=t,offset=d,angle=a,location=loc,kind=P['kind'],residual_cut=cut is not None,instance=inst['id'])
                if cut:
                    raw,loc=gap(T,P)
                    if key in best and raw<best[key].get('raw',np.inf):best[key]['raw']=raw;best[key]['raw_location']=loc
    out={}
    for name,b in best.items():
        P=next(p for p in obs if p['name']==name.split('@')[0])
        thr=threshold(e,P);g=b['clearance']
        status='PASS' if g>=thr-TOL else 'CONTACT APPROVED' if contact_ok(e,P,g) else None
        if status is None and not e['moving'] and P['kind']=='rail/wall':
            inh=min(poly_gap(q,P) for q in own) if own else np.inf
            if g>=min(inh,thr)-TOL and inh<thr:status='JUNCTION INHERITED';b['inherited_from_holes_json']=inh
        if status is None and not e['moving'] and P['kind']=='static prop':status='PASS' if g>=-.001 else None
        if status is None and not e['moving'] and P['kind']=='anchor envelope':status='INFO (unbuilt landmark envelope)'
        b.update(threshold=thr,status=status or 'FAIL');out[name]=b
    return out
def poly_gap(P,Q):
    """Separation lower bound between two convex parts (SAT on face normals and edge-edge axes)."""
    ax=[P['A'],Q['A']]
    C=np.cross(P['E'][:,None,:],Q['E'][None,:,:]).reshape(-1,3);n=np.linalg.norm(C,axis=1);ax.append(C[n>1e-9]/n[n>1e-9,None])
    A=np.vstack(ax);a=P['V']@A.T;b=Q['V']@A.T
    return float(np.maximum(a.min(0)-b.max(0),b.min(0)-a.max(0)).max())
def moving_pairs():
    res={}
    for first,second in [('h11_lock_gate','h11_lock_lift'),('h11_quay_lip','h11_lock_lift'),('h11_quay_lip','h11_lock_gate')]:
        e=next(x for x in REG if x['id']==first);o=next(x for x in REG if x['id']==second);base=parts_of(o)
        best=dict(clearance=np.inf);seen=set()
        for t in sorted(set(np.round(np.arange(0,H11_CYCLE+1e-9,.0025),6))|{5.5,5.8,6.1,6.9,7.0,7.1,9.1,9.2,9.3,10.1,10.4}):
            d1,_=motion(first,t);d2,_=motion(second,t);k=(round(d1,9),round(d2,9))
            if k in seen:continue
            seen.add(k);T=place(e,TRI[first],d1,0)
            for P in base:
                g,loc=gap(T,translate(P,np.array(o['axis'])*d2),best['clearance'])
                if g<best['clearance']:best=dict(clearance=g,time=float(t),offset=d1,other_offset=d2,component=P['name'],location=loc,kind='moving pair')
        best['threshold']=.05;best['status']='PASS' if best['clearance']>=.05-TOL else 'FAIL';res[(first,second)]=best
    return res
def coverage():
    """Visual vs gameplay collision: blockers must be covered by the visual meshes (designed exceptions listed)."""
    rep={}
    def parts_rest(i):e=next(x for x in REG if x['id']==i);return [comp_poly(c,[0,0,0],i,'') for c in COMP[i]]
    mp=lambda h,i:next(m for m in HOLES[h]['moving_parts'] if m['id']==i)
    vp=parts_rest('h09_windpump_vanes');pts=np.vstack([box_samples(b['center'],b['size'],0,0,(5,9,3))@Rz(b.get('roll',0)).T for b in mp(8,'windpump')['blockers']])  # roll turns the strip about the hub
    rv=max(np.hypot(*np.array(c['verts'])[:,:2].T).max() for c in COMP['h09_windpump_vanes'] if c['material'].startswith('Lip'))
    rep['h09_windpump_vanes']=dict(strip_samples=len(pts),covered=int(inside(pts,vp).sum()),visual_tip_radius=float(rv),note='24 holes.json strips inside the vane visual; tip arc vertices include every strip corner on r 4.1')
    bp=parts_rest('h14_ore_bucket');b0,b1=mp(13,'ore_bucket')['blockers']
    p0=box_samples(b0['center'],b0['size'],n=(7,7,7));p1=box_samples(b1['center'],b1['size'],n=(15,9,3))
    miss=p1[~inside(p1,bp)];dev=float(max((math.hypot(x,y)-0 for x,y,z in miss),default=0))
    skid=[c for c in COMP['h14_ore_bucket'] if c['material']=='Iron' and abs(c['center'][1]+10.075)<.2 and c['size'][0]>2]
    rep['h14_ore_bucket']=dict(body_samples=len(p0),body_covered=int(inside(p0,bp).sum()),foot_samples=len(p1),foot_covered=int(inside(p1,bp).sum()),
        foot_uncovered_max_radius_from_hinge=dev,skid_bbox=[skid[0]['size'],skid[0]['center']] if skid else None,
        note='Foot shown as Iron skid (Game Art Bot): envelope 2.1 x .4 x .15 (plate .11 + rivet heads to .15); bottom is an arc r 10.275 about the hinge, so only the two lower collider corners (<=.054 tall) lie outside the visual')
    # Pass 4b: arms (r 8.2..split) + four separate heads (r split..11.5) must together cover the blockers; each head stays inside its own blocker.
    heads=[e['id'] for e in REG if e['id'].startswith('h17_shadow_arm_head_')];blk=mp(16,'shadow_arm')['blockers']
    ap=parts_rest('h17_shadow_arms')+[q for h_ in heads for q in parts_rest(h_)];pts=np.vstack([box_samples(b['center'],b['size'],b['yaw'],n=(7,5,7),ymin=0.051+1e-6) for b in blk])
    allv=np.vstack([c['verts'] for pid in ['h17_shadow_arms']+heads for c in COMP[pid]]);inbox=inside(allv,[box_poly(b['center'],b['size'],b['yaw']) for b in blk],1e-5)
    own={}
    for h_ in heads:
        b=next(x for x in blk if round(x['yaw'])==next(e for e in REG if e['id']==h_)['head_yaw'])
        own[h_]=bool(inside(np.vstack([c['verts'] for c in COMP[h_]]),[box_poly(b['center'],b['size'],b['yaw'])],1e-5).all())
    # arms/heads are axis-aligned at yaw 0/90/180/270: radial extent = max(|x|,|z|)
    arm_rmax=float(max(abs(np.vstack([c['verts'] for c in COMP['h17_shadow_arms']])[:,i]).max() for i in (0,2)))
    head_rmin=float(min(min(abs(v[0]) if abs(v[0])>abs(v[2]) else abs(v[2]) for c in COMP[h_] for v in c['verts']) for h_ in heads))
    rep['h17_shadow_arms']=dict(samples_above_y051=len(pts),covered=int(inside(pts,ap).sum()),visual_within_blockers=bool(inbox.all()),heads_within_own_blocker=own,
        arm_outer_radial=arm_rmax,head_inner_radial=head_rmin,split_radius=arm_rmax,split_seamless=abs(arm_rmax-head_rmin)<1e-5,
        note='arms (h17_shadow_arms, r 8.2..split) + heads (h17_shadow_arm_head_0/90/180/270, r split..11.5) = blocker boxes except a .051 underside gap above the felt')
    pp=[comp_poly(c,[0,0,0],'p','') for c in COMP['h17_plinth'][:2]]
    strips=[w for w in HOLES[16]['walls'] if w['id'].startswith('gnomon_plinth_')]
    pts=np.vstack([box_samples([w['center'][0],.6,w['center'][2]+36],[w['size'][0],1.2,w['size'][2]],n=(9,4,3)) for w in strips])
    hullv=np.array(COMP['h17_plinth'][0]['verts']);rmax=float(np.hypot(hullv[:,0],hullv[:,2]).max());rmin=float(min(abs(P_) for P_ in np.array(COMP['h17_plinth'][0]['planes'])[:,3][np.abs(np.array(COMP['h17_plinth'][0]['planes'])[:,1])<.5]))
    rep['h17_plinth']=dict(strip_samples_y0_1_2=len(pts),covered=int(inside(pts,pp).sum()),hull_max_radius=rmax,hull_min_apothem=rmin,arm_inner_radius=8.2,radial_gap_to_arms=8.2-rmax,note='convex shell enclosing all 48 gnomon_plinth_* strips (collision not enlarged)')
    def boxcov(pid,boxes,piv,ymax=None):
        pr=parts_rest(pid);tot=cov=0;ok=True
        for b in boxes:
            c=[b['center'][i]-piv[i] for i in range(3)];s=list(b['size'])
            if ymax is not None and c[1]+s[1]/2>ymax:top=ymax;bot=c[1]-s[1]/2;c[1]=(top+bot)/2;s[1]=top-bot
            pts=box_samples(c,s,b.get('yaw',0),n=(3,9,15));tot+=len(pts);cov+=int(inside(pts,pr).sum())
        allv=np.vstack([x['verts'] for x in COMP[pid]])
        within=inside(allv,[box_poly([b['center'][i]-piv[i] for i in range(3)],b['size'],b.get('yaw',0)) for b in boxes],1e-5).all()
        return dict(samples=tot,covered=cov,visual_within_exact_boxes=bool(within))
    vb={b['id']:b for b in HOLES[6]['vr_comfort']['boxes']};vb['gap_mist']=HOLES[6]['vr_comfort']['mist']
    rep['h07_bridge_parapets']=boxcov('h07_bridge_parapets',[vb[i] for i in ('rope_rail6','rope_rail7','rope_rail12','rope_rail13')],[0,0,-42])
    rep['h07_bridge_skirts']=dict(boxcov('h07_bridge_skirts',[vb[i] for i in ('bridge1_skirt_west','bridge1_skirt_east','bridge2_skirt_west','bridge2_skirt_east')],[0,0,-42],ymax=-.5),note='exact skirt boxes overlap the parapets at y -.5..0; skirt mesh stops at y -.5 (parapet mesh covers the overlap; avoids coplanar z-fighting)')
    rep['h07_gap_floor_mist']=boxcov('h07_gap_floor_mist',[vb['gap_comfort_floor'],vb['gap_mist']],[0,-4.25,-42])
    s=HOLES[6]['player_teleport_points'][0]['size'];rep['h07_teleport_pads']=dict(boxcov('h07_teleport_pads',[dict(center=[0,s[1]/2,0],size=s)],[0,0,0]),note='pad base on felt (y 0), top y .02')
    pt=next(q for q in HOLES[6]['player_teleport_points'] if q['id']=='bridge2_exit');cup=HOLES[6]['cup'];cc=np.array(cup['position'])-np.array(pt['position'])
    pr=parts_rest('h07_teleport_pad_exit');pts=box_samples([0,pt['size'][1]/2,0],pt['size'],n=(31,3,21));far=np.hypot(pts[:,0]-cc[0],pts[:,2]-cc[2])>cup['radius']+.15+.06
    allv=np.vstack([x['verts'] for x in COMP['h07_teleport_pad_exit']]);dmin=float(np.hypot(allv[:,0]-cc[0],allv[:,2]-cc[2]).min())
    within=inside(allv,[box_poly([0,pt['size'][1]/2,0],pt['size'])],1e-5).all()
    rep['h07_teleport_pad_exit']=dict(samples=int(far.sum()),covered=int(inside(pts[far],pr).sum()),visual_within_exact_boxes=bool(within),min_distance_to_cup_centre=dmin,cup_radius=cup['radius'],cup_edge_clearance=dmin-cup['radius'],
        note='holes.json bridge2_exit pad box overlaps the cup disk; visual notched r .65 round the cup (spec question raised)')
    rep['dam_crest_parapets']=boxcov('dam_crest_parapets',[DAM['deck']]+DAM['parapets']+DAM['skirts'],DAM['deck']['center'])
    for pid,hm,i in (('h11_lock_gate',10,'lock_gate'),('h11_lock_lift',10,'lock_lift_deck'),('h11_quay_lip',10,'quay_lip'),('h06_sluice_gate',5,'sluice_gate')):
        e=next(x for x in REG if x['id']==pid);m=mp(hm,i);pr=parts_rest(pid);off=np.array(m['pivot'])-np.array(e['pivot'])
        pts=np.vstack([box_samples(np.array(b['center'])+off,b['size'],b.get('yaw',0),n=(9,5,5)) for b in m['blockers']])
        if pid=='h06_sluice_gate':pts=pts[pts[:,1]>=.02-1e-9]
        rep[pid]=dict(samples=len(pts),covered=int(inside(pts,pr).sum()))
    for k,v in rep.items():
        c=v.get('covered',v.get('body_covered'));n=v.get('samples',v.get('strip_samples',v.get('body_samples',v.get('samples_above_y051',v.get('strip_samples_y0_1_2')))))
        v['status']='PASS' if c==n and v.get('visual_within_exact_boxes',True) and v.get('visual_within_blockers',True) and all(v.get('heads_within_own_blocker',{}).values()) and v.get('split_seamless',True) else 'FAIL'
    return rep
def main():
    t0=datetime.datetime.now();results={};ok=True
    for e in REG:
        if e.get('world'):continue
        print('checking',e['id'],flush=True);results[e['id']]=check_prop(e)
    pairs=moving_pairs();cov=coverage()
    lines=['SRV-132 PASS 4 FITCHECK vs in/holes.json (p8) incl. approved collision_cuts. Generated '+t0.astimezone().isoformat(),
    'Method: triangle vs exact convex part SAT separation lower bound (negative = penetration). Static props use their recorded convex parts; walls/felt/cups/tee/anchor occluders are holes.json boxes.',
    'Sweeps: rotors 0.5 deg over 360 deg (720 states); ore bucket 0.25 deg over -9..+9 plus period sampling dt .01 s; H6/H11 dt .0025 s plus schedule breakpoints (lip <=.025 stud/step, gate <=.011, deck .01).',
    'Thresholds: >=.05 general; >=.15 mover vs static props and vs approved cut residuals (holes.json collision_cuts clearance .15); H9 vanes vs felt >=.02 (holes.json windpump visual "clearance .02").',
    'Exceptions (explicit): static props resting on felt (contact >=-.001); H6 gate on supporting neck felt (lifted .02, >=.0194, holes.json p7/p8 support contact);',
    '  static exact-box visuals adjacent to holes.json walls they meet (JUNCTION INHERITED: the holes.json boxes themselves touch/overlap there); unbuilt landmark envelopes vs static props = INFO.',
    'Approved cuts: '+'; '.join(f'{p}/{o} min={c[0]} max={c[1]}' for (p,o),c in CUTS.items())]
    overall=(np.inf,None);overall_strict=(np.inf,None);per_prop={}
    for pid,res in results.items():
        lines.append('\n'+pid);pm=(np.inf,None)
        for name,b in sorted(res.items(),key=lambda kv:kv[1]['clearance']):
            if b['status']=='FAIL':ok=False
            lines.append(f"{b['status']} {name} "+json.dumps({k:(round(v,9) if isinstance(v,float) else v) for k,v in b.items() if k!='status'}))
            if b['status'] in ('PASS',) and b['clearance']<pm[0]:pm=(b['clearance'],dict(obstacle=name,**b))
        for (a,c),b in pairs.items():
            if pid in (a,c):
                lines.append(f"{b['status']} MOVING PAIR {a} / {c} "+json.dumps({k:v for k,v in b.items() if k!='status'}))
                if b['status']=='FAIL':ok=False
                if b['clearance']<pm[0]:pm=(b['clearance'],dict(obstacle=(c if pid==a else a),**b))
        budget=all(m['tris']<20000 for m in MAN[pid]['meshes']);ok&=budget;lines.append('Mesh budget '+('PASS' if budget else 'FAIL')+f" (max mesh {max(m['tris'] for m in MAN[pid]['meshes'])} tris)")
        per_prop[pid]=pm[1]
        if pm[1]:
            lines.append('PROP MIN '+pid+' '+json.dumps(pm[1]))
            if pm[0]<overall[0]:overall=pm
            if not (pid=='h09_windpump_vanes' and pm[1]['kind']=='felt') and pm[0]<overall_strict[0]:overall_strict=pm
    lines.append('\nCOVERAGE (visual vs gameplay collision)')
    for k,v in cov.items():
        lines.append(f"{v['status']} {k} "+json.dumps(v));ok&=v['status']=='PASS'
    # H11 p8 timing interlocks
    q=lambda n,t:motion(n,t)[0]
    tchk=dict(gate_closed_before_rise=all(q('h11_lock_gate',t)==0 for t in np.arange(5.8,10.4,.01)),
        deck_bottom_while_gate_moving=all(q('h11_lock_lift',t)==0 for t in list(np.arange(5.5,5.8,.01))+list(np.arange(10.4,10.7,.01))),
        lip_flush_whole_top_dwell=all(q('h11_quay_lip',t)==-1 for t in np.arange(7.0,9.2,.01)),
        deck_level_top=all(q('h11_lock_lift',t)==4 for t in np.arange(7.1,9.1,.01)),cycle=H11_CYCLE==10.7)
    tok=all(tchk.values());ok&=tok
    lines.append('\nH11 p8 TIMING '+('PASS' if tok else 'FAIL')+' '+json.dumps(tchk)+' : gate open 0-5.5, rise 5.5-5.8, closed 5.8-10.4, lower 10.4-10.7; deck rise 6.1-7.1, level top 7.1-9.1, down 9.1-10.1; lip sink 6.9-7.0, flush 7.0-9.2, rise 9.2-9.3.')
    lines.append('\nOVERALL MIN (all PASS pairs) '+json.dumps(overall[1]))
    lines.append('OVERALL MIN excluding the holes.json-specified H9 felt clearance '+json.dumps(overall_strict[1]))
    lines.append('ALL PASS: '+('YES' if ok else 'NO'))
    name='fitcheck_movers_pass4_'+('validated' if ok else 'failed')+'.txt'
    for old in ('fitcheck_movers_pass4_validated.txt','fitcheck_movers_pass4_failed.txt'):
        if (SRC/old).exists() and old!=name:(SRC/old).rename(SRC/(old.replace('.txt','_superseded_'+t0.strftime('%H%M%S')+'.txt')))
    (SRC/name).write_text('\n'.join(lines),encoding='utf-8')
    (SRC/'fitcheck_results_pass4.json').write_text(json.dumps(dict(all_pass=bool(ok),overall_min=overall[1],overall_min_strict=overall_strict[1],per_prop_minima=per_prop,results=results,
        moving_pairs={f'{a}/{c}':b for (a,c),b in pairs.items()},coverage=cov,h11_timing=tchk,cuts=[dict(prop=p,obstacle=o,min=c[0],max=c[1]) for (p,o),c in CUTS.items()]),indent=1,default=float))
    with (SRC/'PROGRESS.md').open('a') as f:f.write(f"\n- {datetime.datetime.now().astimezone().isoformat()} fitcheck_pass4: ALL PASS {ok}; overall min {overall[0]:.6f} ({overall[1]['obstacle'] if overall[1] else ''}); {name}\n")
    print('\n'.join(l for l in lines if not l.startswith(('PASS','CONTACT','JUNCTION','INFO'))))
    return ok
if __name__=='__main__':sys.exit(0 if main() else 1)
