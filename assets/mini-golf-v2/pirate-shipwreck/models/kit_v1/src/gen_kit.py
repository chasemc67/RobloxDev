# Pirate Shipwreck dressing kit wave 1 generator (Look B). Run: /workspace/.geo/bin/python gen_kit.py <outdir>
# Roblox frame: +Y up, FRONT = +Z, studs. One merged mesh per FBX, palette-texture colour. Scenery only.
import sys,os,json,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kit_lib import *
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
props={};META={}
def newp(i,mode,use,**kw): P=Part(i);props[i]=P;META[i]=dict(mode=mode,use=use,**kw);return P
def shift(P,dx,dy,dz):
    for i,(m,c,sm) in enumerate(P.items): m=m.copy();m.apply_translation((dx,dy,dz));P.items[i]=(m,c,sm)
def bounds(P):
    V=np.concatenate([m.vertices for m,_,_ in P.items]);return V.min(0),V.max(0)
def settle(P,mode):
    mn,mx=bounds(P)
    if mode=='bbox': shift(P,-(mn[0]+mx[0])/2,-mn[1],-(mn[2]+mx[2])/2)      # base centre = bbox centre, min y = 0
    elif mode=='base': shift(P,0,-mn[1],0)                                    # trunk base stays on x=z=0
    elif mode=='buried': shift(P,-(mn[0]+mx[0])/2,0,-(mn[2]+mx[2])/2)         # y=0 is the ground line; lower part is meant to be sunk
def nz(u,s): return 0.5*math.sin(2.7*u[0]+s)+0.3*math.sin(3.9*u[2]+2*s)+0.2*math.sin(5.1*u[1]+1.7*s)
def jitter(m,c,jit,s):
    V=m.vertices.copy();d=V-np.array(c,float);u=d/(np.linalg.norm(d,axis=1,keepdims=True)+1e-9)
    k=np.array([1+jit*nz(x,s) for x in u])[:,None];m.vertices=np.array(c,float)+d*k;return m
def capdome(rx,ry,rz,tmax,lon,lat):
    rings=[]
    for t in np.linspace(0.04,tmax,lat+1):
        rr=math.sin(t);rings.append([(rx*rr*math.cos(2*math.pi*k/lon),ry*math.cos(t),rz*rr*math.sin(2*math.pi*k/lon)) for k in range(lon)])
    return ring_solid(rings)
def yawm(m,deg,pos): m=m.copy();m.apply_transform(Rm((0,1,0),deg));m.apply_translation(pos);return m
def blades(P,specs,cols):
    for i,(p0,c,p1,w,t,n) in enumerate(specs): P.add(blade(p0,c,p1,w,t,n),cols[i%len(cols)])
# ---------------------------------------------------------------- PALMS
def palm(i,h,lean,seed,br,nfr,use,mode='bbox',bow=(0.0,0.0)):
    rg=np.random.default_rng(seed);P=newp(i,mode,use,height_target=h+4)
    top=V3(lean[0],h,lean[1])
    tp=lambda s:V3(lean[0]*s**1.7+bow[0]*math.sin(math.pi*s),h*s,lean[1]*s**1.7+bow[1]*math.sin(math.pi*s))
    P.add(tube([tp(s) for s in np.linspace(0,1,14)],br,8,br*0.55),'Trunk')
    P.add(frustum(br*1.55,br*1.0,(0,0,0),(0,h*0.05+0.8,0),8),'TrunkDk')
    for k in range(1,int(h/3.4)):
        s=k/int(h/3.4);p=tp(s);T=tp(min(s+.02,1))-tp(max(s-.02,0));T/=np.linalg.norm(T);r=br*(1-0.45*s)+0.3
        P.add(frustum(r,r,p-T*0.4,p+T*0.4,8),'TrunkLt' if k%2 else 'TrunkDk')
    L=4.0+0.14*h
    for k in range(nfr):
        a=math.radians(k*360/nfr+rg.uniform(-9,9));dd=V3(math.cos(a),0,math.sin(a));LL=L*(1 if k%2==0 else 0.85)
        P.add(blade(top+V3(0,0.3,0),top+dd*LL*0.5+V3(0,0.48*LL,0),top+dd*LL+V3(0,-0.43*LL+rg.uniform(-0.6,0.6),0),LL*0.17,0.3,7),['PalmGreen','PalmGreenDk','PalmGreenLt'][k%3])
    for k in range(4):
        a=math.radians(k*90+30);dd=V3(math.cos(a),0,math.sin(a))
        P.add(blade(top+V3(0,0.5,0),top+dd*0.15*L+V3(0,0.28*L,0),top+dd*0.38*L+V3(0,0.42*L,0),0.13*L,0.28,6),'PalmGreenLt')
    for dx,dy,dz in((-1.0,-1.0,0.8),(1.0,-1.1,0.9),(0.1,-1.2,-1.1)): P.add(ell(0.85+h/90,top+V3(dx,dy,dz),8,5),'Coconut' if dx>0 else 'CoconutDk')
    R=6+0.12*h;ns=15+int(h/12)
    for k in range(ns):
        a=math.radians(k*360/ns+rg.uniform(-8,8));dd=V3(math.cos(a),0,math.sin(a));LL=R*rg.uniform(0.85,1.1)
        P.add(blade(dd*1.6+V3(0,0.5,0),dd*LL*0.5+V3(0,0.55*LL,0),dd*LL+V3(0,0.45,0),0.95,0.3,6),['Fern','FernDk','FernLt'][k%3])
    for k in range(6):
        a=math.radians(k*60+20);dd=V3(math.cos(a),0,math.sin(a));LL=R*0.55
        P.add(blade(dd*1.0+V3(0,0.5,0),dd*LL*0.4+V3(0,0.75*LL,0),dd*LL+V3(0,0.9,0),0.8,0.28,5),'FernLt')
    settle(P,mode);return P
palm('kit_palm_s',21,(0.6,0.4),11,1.15,8,'Short palm for beach pads (target ~25 high).',bow=(0.8,0.0))
palm('kit_palm_m',36,(1.2,0.7),12,1.5,9,'Medium palm, shoulders the pad palms (target ~40 high).',bow=(1.2,0.5))
palm('kit_palm_l',56,(1.8,0.9),13,1.9,10,'Tall palm for skyline and jungle edges (target ~60 high).',bow=(1.6,0.6))
palm('kit_palm_lean_a',40,(0.0,15.0),14,1.6,9,'Leaning palm: crown leans toward +Z (front). Origin is the trunk base.',mode='base',bow=(1.0,0.0))
palm('kit_palm_lean_b',32,(13.0,2.5),15,1.4,9,'Leaning palm: crown leans toward +X. Origin is the trunk base.',mode='base',bow=(0.0,1.2))
# ---------------------------------------------------------------- ROCKS (half-buried, bottom is below y=0 on purpose)
def rockset(i,R,n,rx0,seed,use,lon,lat):
    rg=np.random.default_rng(seed);P=newp(i,'buried',use)
    mo=dome(R*1.08,0.55+R*0.07,R*1.02,(0,0,0),14,3);jitter(mo,(0,0,0),0.12,seed);P.add(yawm(mo,rg.uniform(0,90),(0,-0.45,0)),'SandTop')
    for k in range(n):
        rx=rx0*(1-0.72*k/n)*rg.uniform(0.9,1.1);ry=rx*rg.uniform(0.8,1.25);rz=rx*rg.uniform(0.8,1.1)
        a=k*2.4;rr=0 if k==0 else R*rg.uniform(0.35,0.85)-rx*0.2;pos=(rr*math.cos(a),-ry*0.3,rr*math.sin(a));yaw=rg.uniform(0,360);sd=seed+k*1.3
        lo,la=(lon,lat) if k<3 else (8,3)
        b=dome(rx,ry,rz,(0,0,0),lo,la);jitter(b,(0,0,0),0.16,sd);P.add(yawm(b,yaw,pos),['Rock','RockDk','RockLt'][k%3])
        c=capdome(rx*1.05,ry*1.05,rz*1.05,0.95,lo,max(la-1,2));jitter(c,(0,0,0),0.16,sd);P.add(yawm(c,yaw,pos),'SandTopLt' if k%2 else 'SandTop')
    settle(P,'buried')
rockset('kit_rock_s',6.5,5,3.4,21,'Small half-buried rock cluster for pad corners and waterline.',10,4)
rockset('kit_rock_m',11,8,5.6,22,'Medium half-buried rock cluster for the beach and jungle banks.',12,4)
rockset('kit_rock_l',19,11,9.6,23,'Large half-buried rock cluster for headlands and cave approach.',14,5)
# ---------------------------------------------------------------- UNDERGROWTH
P=newp('kit_leafclump','bbox','Big-leaf jungle plant (taro/banana style) for the jungle trail and pad corners.');rg=np.random.default_rng(31)
for k in range(10):
    a=math.radians(k*137.5);dd=V3(math.cos(a),0,math.sin(a));L=rg.uniform(9,13);p0=dd*0.9+V3(0,0.4,0)
    P.add(blade(p0,p0+dd*L*0.3+V3(0,L*0.95,0),p0+dd*L*0.9+V3(0,L*0.5+rg.uniform(-2,1),0),L*0.24,0.3,8),['LeafGreen','LeafLt','LeafDk','LeafYellow'][k%4])
for k in range(6):
    a=math.radians(k*60+15);dd=V3(math.cos(a),0,math.sin(a));L=rg.uniform(5,7);p0=dd*0.6+V3(0,0.4,0)
    P.add(blade(p0,p0+dd*L*0.25+V3(0,L*0.9,0),p0+dd*L*0.7+V3(0,L*0.6,0),L*0.26,0.28,7),['LeafLt','LeafGreen'][k%2])
P.add(dome(2.4,0.9,2.4,(0,-0.2,0),8,2),'SandTop'); settle(P,'bbox')
P=newp('kit_fernclump','bbox','Low fern clump to break up bare ground; scatter 3-5 per pad corner.');rg=np.random.default_rng(32)
for k in range(24):
    a=math.radians(k*137.5);dd=V3(math.cos(a),0,math.sin(a));L=rg.uniform(6.5,9.5);p0=dd*0.6+V3(0,0.4,0)
    P.add(blade(p0,p0+dd*L*0.4+V3(0,L*0.9,0),p0+dd*L*0.95+V3(0,0.7+rg.uniform(0,0.8),0),0.9,0.26,6),['Fern','FernDk','FernLt'][k%3])
for k in range(8):
    a=math.radians(k*45+10);dd=V3(math.cos(a),0,math.sin(a));L=rg.uniform(4,5.5);p0=dd*0.4+V3(0,0.4,0)
    P.add(blade(p0,p0+dd*L*0.2+V3(0,L*0.95,0),p0+dd*L*0.55+V3(0,L*0.8,0),0.8,0.26,5),'FernLt')
settle(P,'bbox')
def vine(P,top,length,seed,leaves=4,r0=0.3):
    rg=np.random.default_rng(seed);pts=[];n=9
    for q in range(n):
        s=q/(n-1);pts.append(top+V3(0.7*math.sin(5*s+seed),-length*s,0.6*math.sin(3*s+seed*2)))
    P.add(tube(pts,r0,5,0.2),'Vine')
    for q in range(leaves):
        s=(q+1.2)/(leaves+1.2);p=top+V3(0.7*math.sin(5*s+seed),-length*s,0.6*math.sin(3*s+seed*2));sd=1 if q%2==0 else -1;o=V3(sd,0,rg.uniform(-0.3,0.3))
        P.add(blade(p,p+o*1.3+V3(0,0.9,0),p+o*2.8+V3(0,-0.8,0),0.9,0.22,4),['VineLt','Vine','VineDk'][q%3])
P=newp('kit_vine_strip','bbox','Hanging vine curtain (about 22 wide, 25 tall) for jungle canopy edges; hang from a branch or canopy mass.');rg=np.random.default_rng(33)
H=26.0;P.add(tube([V3(-12+24*s,H+0.6*math.sin(3*s),0.0) for s in np.linspace(0,1,10)],0.8,6,0.6),'TrunkDk')
for k,x in enumerate(np.linspace(-11,11,9)): vine(P,V3(x,H,rg.uniform(-0.6,0.6)),rg.uniform(11,25.5),40+k,leaves=5)
for k in range(7): a=-11+3.6*k;P.add(blade(V3(a,H+0.2,0),V3(a+1.6,H+2.6,0.4),V3(a+3.6,H+0.6,0.2),1.3,0.25,5),['LeafGreen','LeafLt','LeafDk'][k%3])
settle(P,'bbox')
P=newp('kit_vine_arch','bbox','Vine arch spanning a path (about 36 wide, 16 high). Path runs along Z; arch spans X. One every ~40 studs on the jungle trail.');rg=np.random.default_rng(34)
RX=17.0;HY=15.0
for z0,ph in((-0.9,0.0),(0.9,2.0)):
    pts=[V3(-RX*math.cos(th),HY*math.sin(th)*1.0,z0*math.cos(3*th+ph)) for th in np.linspace(0.0,math.pi,18)]
    P.add(tube(pts,0.95,6,0.8),'Trunk' if z0<0 else 'TrunkDk')
for k in range(22):
    th=0.15+k*(math.pi-0.3)/21;p=V3(-RX*math.cos(th),HY*math.sin(th),0);sd=1 if k%2 else -1;o=V3(0,0,sd*1.0)+V3(0,1,0)*0.2
    P.add(blade(p,p+V3(0,1.5,0)+o*1.5+V3(sd*0.6,0,0),p+V3(sd*3.0,0.2,sd*0.6)+V3(0,-0.6,0)*1,1.25,0.25,5),['LeafGreen','LeafLt','LeafDk','VineLt'][k%4])
for k,th in enumerate(np.linspace(0.3*math.pi,0.7*math.pi,7)):
    p=V3(-RX*math.cos(th),HY*math.sin(th)-0.4,0.0);vine(P,p,rg.uniform(5,8.5),60+k,leaves=3)
for sx in(-1,1):
    for k in range(7):
        a=math.radians(k*52+10);dd=V3(math.cos(a),0,math.sin(a));L=rg.uniform(4.5,6.5);base=V3(sx*RX,0,0)
        P.add(blade(base+dd*0.8+V3(0,0.4,0),base+dd*L*0.45+V3(0,L*0.8,0),base+dd*L+V3(0,0.6,0),0.9,0.28,5),['Fern','FernDk','FernLt'][k%3])
settle(P,'bbox')
# ---------------------------------------------------------------- WRECK DEBRIS
def plank(P,c,L,w,t,yaw,tilt=0,col='Plank',roll=0):
    m=box(L,t,w,(0,0,0));sp=box(1.5,t*0.8,w*0.45,(L/2+0.6,0,w*0.2),((0,1,0),14));sp2=box(1.1,t*0.7,w*0.3,(-L/2-0.4,0,-w*0.15),((0,1,0),-12))
    for q,cc in((m,col),(sp,'PlankDk'),(sp2,'PlankDk')):
        q=q.copy();q.apply_transform(Rm((0,0,1),tilt));q.apply_transform(Rm((1,0,0),roll));q.apply_transform(Rm((0,1,0),yaw));q.apply_translation(c);P.add(q,cc)
P=newp('kit_planks','bbox','Broken plank pile for the beach debris trail from the wreck.')
for c,L,w,t,yaw,tilt,col,roll in(((0,0.2,0),11,1.8,0.4,10,0,'Plank',0),((1.6,0.2,3.0),8.5,1.6,0.4,-28,0,'PlankDk',0),((-2.0,0.2,-3.1),9.5,1.7,0.4,72,0,'PlankLt',0),((0.5,0.78,0.8),9.0,1.6,0.4,-12,3,'PlankDk',0),((-1.5,1.4,-1.0),7.0,1.5,0.4,40,6,'Plank',0),((5.5,0.6,-2.2),6.5,1.5,0.4,-60,0,'PlankLt',20),((-5.2,0.2,2.6),5.5,1.4,0.4,25,0,'PlankDk',0)):
    plank(P,(c[0],c[1]+t/2,c[2]),L,w,t,yaw,tilt,col,roll)
settle(P,'bbox')
P=newp('kit_barrel','bbox','Barrel for the beach, pad 1 and the wreck deck.')
ys=[0,0.8,1.8,2.6,3.4,4.4,5.2];rs=[1.9,2.2,2.45,2.55,2.45,2.2,1.9]
P.add(lathe(list(zip(rs,ys)),12),'Plank')
for y in(0.9,2.0,3.2,4.3):
    r=float(np.interp(y,ys,rs))+0.14;P.add(frustum(r,r,(0,y-0.18,0),(0,y+0.18,0),12),'Iron')
P.add(lathe([(0.05,5.05),(2.0,5.05),(2.0,5.4),(0.05,5.4)],12),'PlankLt');settle(P,'bbox')
def crate(P,c,s,yaw):
    h=s/2;q=Part('c');q.add(box(s,s,s,(0,h,0)),'DarkWood')
    for sx in(-1,1):
        for sz in(-1,1): q.add(box(s*0.2,s*1.08,s*0.2,(sx*(h-0.0),h,sz*(h-0.0))),'DarkWood' )
    for f in range(4):
        for k in(-1,0,1):
            w=s*0.24;pos=[0,0,0]
            if f==0: pos=(k*s*0.3,h,h+s*0.04);ex=(w,s*0.9,s*0.1)
            elif f==1: pos=(k*s*0.3,h,-h-s*0.04);ex=(w,s*0.9,s*0.1)
            elif f==2: pos=(h+s*0.04,h,k*s*0.3);ex=(s*0.1,s*0.9,w)
            else: pos=(-h-s*0.04,h,k*s*0.3);ex=(s*0.1,s*0.9,w)
            q.add(box(*ex,pos),'Plank' if k!=0 else 'PlankLt')
    for k in(-1,0,1): q.add(box(s*0.24,s*0.1,s*0.9,(k*s*0.3,s+s*0.03,0)),'Plank')
    M=Tm(c)@Rm((0,1,0),yaw)
    for m,col,sm in q.items: P.add(xf(m,M),col)
P=newp('kit_crate','bbox','Wooden crate pair for the beach and wreck deck.')
crate(P,(0,0,0),4.2,12);crate(P,(4.6,0,1.8),2.8,-30);settle(P,'bbox')
P=newp('kit_rope_coil','bbox','Coiled rope for the wreck deck and beach.')
pts=[]
for q in range(64):
    s=q/63;turns=3.0;th=s*turns*2*math.pi;r=2.5-1.2*s;pts.append(V3(r*math.cos(th),0.5+0.85*s*turns*0.4+0.0,r*math.sin(th)))
P.add(tube(pts,0.5,6,0.5),'Rope')
P.add(tube([pts[-1],pts[-1]+V3(0.6,0.0,0.5),V3(2.6,0.5,2.2),V3(3.8,0.45,3.1)],0.45,6,0.4),'RopeDk');settle(P,'bbox')
P=newp('kit_spar_snapped','bbox','Snapped mast spar resting on a rock, with a lashed yard piece, for the beach and wreck.')
rg=np.random.default_rng(35);p0=V3(-10,1.1,0);p1=V3(8,5.4,0);d=(p1-p0)/np.linalg.norm(p1-p0)
P.add(frustum(1.1,0.82,p0,p1,10),'PlankLt')
for q in range(6):
    a=q*math.pi/3+0.4;off=V3(0,math.cos(a),math.sin(a))*0.6;L=rg.uniform(1.4,3.0)
    P.add(beam(p1+off,p1+off+d*L+V3(0,rg.uniform(-0.6,0.6),rg.uniform(-0.6,0.6)),0.45,0.6),'PlankDk')
for s in(0.18,0.28): c=p0+(p1-p0)*s;P.add(frustum(1.28,1.28,c-d*0.18,c+d*0.18,10),'Rope')
c=p0+(p1-p0)*0.23;P.add(frustum(0.6,0.5,c+V3(0,0,-5.5),c+V3(0,0,5.5),8),'Plank')
rk=dome(3.2,4.1,2.8,(0,0,0),9,3);jitter(rk,(0,0,0),0.12,5);P.add(yawm(rk,30,(6.2,0.0,0.3)),'RockDk')
settle(P,'bbox')
def sweep_rect(pts,w,t):
    rings=[]
    for i,p in enumerate(pts):
        T=pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)];T/=np.linalg.norm(T);N=V3(-T[1],T[0],0);Z=V3(0,0,1)
        rings.append([p+N*t/2+Z*w/2,p+N*t/2-Z*w/2,p-N*t/2-Z*w/2,p-N*t/2+Z*w/2])
    return ring_solid(rings)
P=newp('kit_hull_rib','buried','Half-buried hull ribs arching out of sand (bottom 2 studs are meant to sink below the ground line).')
RX_,RY_=10.0,12.0
for zc,t0,t1,col in((-6.5,0,180,'PlankDk'),(0,0,160,'Plank'),(6.5,12,180,'PlankDk')):
    pts=[V3(RX_*math.cos(math.radians(a)),-2.0+RY_*math.sin(math.radians(a)),zc) for a in np.linspace(t0,t1,13)];m=sweep_rect(pts,1.5,1.2)
    P.add(m,col)
for a in(55,125):
    p=V3(RX_*math.cos(math.radians(a)),-2.0+RY_*math.sin(math.radians(a)),0);T=V3(-math.sin(math.radians(a))*RX_,math.cos(math.radians(a))*RY_,0);T/=np.linalg.norm(T);N=V3(-T[1],T[0],0)
    m=box(0.5,1.5,15.0,(0,0,0));R=np.eye(4);R[:3,0]=-N;R[:3,1]=T;R[:3,2]=(0,0,1);m.apply_transform(R);m.apply_translation(p+N*0.8);P.add(m,'PlankLt')
settle(P,'buried')
# ---------------------------------------------------------------- BACKDROP
def spire(P,pos,r,h,lon,rings,pw,seed,lean=(0.0,0.0),mesa=0.0,cap0=None,cap_col='HazeGreen',col='HazeRock',cols2=None):
    R_=[];Rc=[]
    for i in range(rings+1):
        s=i/rings;y=h*s;base=(1-s)**pw*0.88+0.12*(1-s)
        if mesa: base=(1-mesa*s) if s<0.82 else (1-mesa*0.82)*(1-(s-0.82)/0.18*0.75)
        ox=pos[0]+lean[0]*s*s;oz=pos[1]+lean[1]*s*s;ring=[];rc=[]
        for k in range(lon):
            a=2*math.pi*k/lon;f=1+0.14*math.sin(3*a+7*s+seed)+0.08*math.sin(5*a-3*s+2*seed)+(0.05 if i%3==0 else 0)
            rr=r*base*f;ring.append((ox+rr*math.cos(a),y,oz+rr*math.sin(a)));rr2=rr*1.035+1.4;rc.append((ox+rr2*math.cos(a),y,oz+rr2*math.sin(a)))
        R_.append(ring);Rc.append(rc)
    P.add(ring_solid(R_),col)
    if cap0 is not None:
        i0=int(cap0*rings);P.add(ring_solid(Rc[i0:]),cap_col)
def stack(i,use,mains,boulders,seed,lon=18,rings=20):
    rg=np.random.default_rng(seed);P=newp(i,'bbox',use)
    for q,(x,z,r,h,pw,lean,mesa,cap0,col,cc) in enumerate(mains): spire(P,(x,z),r,h,lon,rings,pw,seed+q,lean,mesa,cap0,cc,col)
    x0,z0,r0=mains[0][0],mains[0][1],mains[0][2]
    for q in range(boulders):
        a=q*2.4;rr=r0*rg.uniform(1.0,1.5);spire(P,(x0+rr*math.cos(a),z0+rr*math.sin(a)),r0*rg.uniform(0.18,0.3),mains[0][3]*rg.uniform(0.07,0.14),10,4,0.9,seed+9+q,col=['HazeRock','HazeRockDk','HazeRockLt'][q%3])
    sk=dome(r0*2.0,6.0,r0*1.7,(x0,0,z0),16,3);jitter(sk,(x0,0,z0),0.12,seed);P.add(sk,'HazeSand')
    settle(P,'bbox')
stack('kit_stack_a','Tall hazy sea-stack spire group for the skyline (about 320 high). Place 400-900 studs out; fog friendly.',
 [(0,0,46,320,0.75,(18,0),0,0.8,'HazeRock','HazeGreenDk'),(66,-12,25,175,0.8,(-8,4),0,0.78,'HazeRockDk','HazeGreen'),(-52,16,18,96,0.8,(6,0),0,0.7,'HazeRockLt','HazeGreenLt')],7,101)
stack('kit_stack_b','Broad hazy mesa island with twin tops for the skyline (about 190 high).',
 [(0,0,105,190,1.0,(0,0),0.45,0.7,'HazeRockDk','HazeGreen'),(120,-40,58,125,1.0,(0,0),0.4,0.65,'HazeRock','HazeGreenLt'),(-110,50,42,70,1.0,(0,0),0.35,0.5,'HazeRockLt','HazeGreenDk')],8,202,lon=18,rings=18)
stack('kit_stack_c','Tall leaning twin-fin sea stack (about 390 high) for the horizon.',
 [(0,0,34,390,0.85,(48,10),0,0.86,'HazeRock','HazeGreenDk'),(48,-6,26,255,0.8,(-26,6),0,0.82,'HazeRockLt','HazeGreen'),(-40,26,20,150,0.85,(14,-6),0,0.75,'HazeRockDk','HazeGreenLt'),(26,38,14,80,0.8,(0,0),0,0.6,'HazeRock','HazeGreen')],9,303)
def torus(R0,prof,N,seed,wj=0.0,hj=0.0):
    V=[];F=[];m=len(prof)
    for i in range(N):
        a=2*math.pi*i/N;sw=1+wj*math.sin(5*a+seed)+wj*0.6*math.sin(11*a+2*seed);sh=1+hj*math.sin(7*a+seed*1.3)+hj*0.5*math.sin(13*a+seed)
        for dr,y in prof: r=R0+dr*sw;V.append((r*math.cos(a),y*(sh if y>0.6 else 1),r*math.sin(a)))
    for i in range(N):
        j=(i+1)%N
        for k in range(m):
            l=(k+1)%m;F+=[[i*m+k,j*m+k,j*m+l],[i*m+k,j*m+l,i*m+l]]
    t=trimesh.Trimesh(np.array(V),F,process=False);t.fix_normals();return t
P=newp('kit_reef_ring','bbox','Offshore reef ring (about 260 across) to break up the empty horizon; sits on the water surface, y=0 is the water line.');rg=np.random.default_rng(404)
P.add(torus(95,[(-30,0),(-27,0.5),(27,0.5),(30,0),(0,-0.4)],48,3,0.08,0),'ReefTealLt')
P.add(torus(95,[(-9,0),(-7,2.2),(-3,3.6),(3,3.2),(7,2.0),(9,0)],48,5,0.18,0.35),'ReefRock')
P.add(torus(125,[(-2.5,0.7),(-1.5,1.0),(1.5,1.0),(2.5,0.7),(0,0.55)],48,11,0.1,0),'HazeFoam')
for k in range(18):
    a=math.radians(k*20+rg.uniform(-4,4));r=95+rg.uniform(-6,6);rx=rg.uniform(4,9);ry=rx*rg.uniform(0.6,1.1)
    b=dome(rx,ry,rx*0.9,(0,0,0),9,3);jitter(b,(0,0,0),0.16,k);P.add(yawm(b,rg.uniform(0,360),(r*math.cos(a),0.4,r*math.sin(a))),['ReefRock','ReefRockDk','ReefRock'][k%3])
    if k%3==0: c=capdome(rx*1.05,ry*1.05,rx*0.95,0.85,9,2);jitter(c,(0,0,0),0.16,k);P.add(yawm(c,0,(r*math.cos(a),0.4,r*math.sin(a))),'ReefSand')
for k,(a,r,rr) in enumerate(((0.9,92,11),(3.6,98,9))):
    P.add(dome(rr,2.2,rr*0.85,(r*math.cos(a),0.45,r*math.sin(a)),12,3),'ReefSand')
settle(P,'bbox')
# ---------------------------------------------------------------- export
os.makedirs(os.path.join(OUT,'geom'),exist_ok=True);report={}
for k,p in props.items():
    g=p.merged();V=np.array(g['verts']);g['verts']=np.round(V,4).tolist()
    json.dump({k:dict(objects=[dict(name=k,verts=g['verts'],tris=g['tris'],uvs=g['uvs'],smooth=g['smooth'])])},open(os.path.join(OUT,'geom',k+'.json'),'w'))
    report[k]=dict(tris=len(g['tris']),bbox=dict(min=np.round(V.min(0),2).tolist(),max=np.round(V.max(0),2).tolist()),size=np.round(V.max(0)-V.min(0),2).tolist(),mode=META[k]['mode'],use=META[k]['use'])
    print(k,len(g['tris']),report[k]['size'],report[k]['bbox']['min'][1])
json.dump(report,open(os.path.join(OUT,'box_report.json'),'w'),indent=1)
palette_png(os.path.join(OUT,'kit_palette.png'));json.dump(PAL,open(os.path.join(OUT,'palette.json'),'w'))
