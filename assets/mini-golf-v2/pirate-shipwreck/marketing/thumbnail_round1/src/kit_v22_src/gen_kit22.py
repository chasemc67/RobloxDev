# Pirate Shipwreck kit_v2_1 generator (torches, canopy_wall, cliff_ridge revised) (Look B). Run: /workspace/.geo/bin/python gen_kit2.py <outdir>
# Roblox frame: +Y up, FRONT = +Z, studs. Scenery only (CanCollide off). Glow parts are their own object; LightAttach empties exported.
import sys,os,json,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kit_lib import *
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
props={};META={}
def newp(i,mode,use,**kw): P=Part(i);P.att={};props[i]=P;META[i]=dict(mode=mode,use=use,**kw);return P
def shift(P,dx,dy,dz):
    for i,(m,c,sm) in enumerate(P.items): m=m.copy();m.apply_translation((dx,dy,dz));P.items[i]=(m,c,sm)
    for k,v in P.att.items(): P.att[k]=(v[0]+dx,v[1]+dy,v[2]+dz)
def bounds(P):
    V=np.concatenate([m.vertices for m,_,_ in P.items]);return V.min(0),V.max(0)
def settle(P,mode):
    mn,mx=bounds(P)
    if mode=='bbox': shift(P,-(mn[0]+mx[0])/2,-mn[1],-(mn[2]+mx[2])/2)
    elif mode=='base': shift(P,0,-mn[1],0)
    elif mode=='sunk2': shift(P,-(mn[0]+mx[0])/2,-2.0-mn[1],-(mn[2]+mx[2])/2)
    elif mode=='ringtop': pass
def nz(u,s): return 0.5*math.sin(2.7*u[0]+s)+0.3*math.sin(3.9*u[2]+2*s)+0.2*math.sin(5.1*u[1]+1.7*s)
def jitter(m,c,jit,s):
    V=m.vertices.copy();d=V-np.array(c,float);u=d/(np.linalg.norm(d,axis=1,keepdims=True)+1e-9)
    k=np.array([1+jit*nz(x,s) for x in u])[:,None];m.vertices=np.array(c,float)+d*k;return m
def capdome(rx,ry,rz,tmax,lon,lat):
    rings=[]
    for t in np.linspace(0.04,tmax,lat+1):
        rr=math.sin(t);rings.append([(rx*rr*math.cos(2*math.pi*k/lon),ry*math.cos(t),rz*rr*math.sin(2*math.pi*k/lon)) for k in range(lon)])
    return ring_solid(rings)
def put(P,m,col,o=(0,0,0),s=1.0,yaw=0.0,rot=None):
    m=m.copy()
    if s!=1.0: m.apply_scale(s)
    if rot is not None: m.apply_transform(Rm(*rot))
    if yaw: m.apply_transform(Rm((0,1,0),yaw))
    m.apply_translation(o);P.add(m,col)
def scaleP(P,k):
    for i,(m,c,sm) in enumerate(P.items): m=m.copy();m.apply_scale(k);P.items[i]=(m,c,sm)
    for a,v in P.att.items(): P.att[a]=tuple(x*k for x in v)
def ribbon(pts,w,t,wave=0.0):
    """sheet of width w (across X) and thickness t following a path in the YZ plane"""
    rings=[]
    for i,p in enumerate(pts):
        p=np.array(p,float);T=np.array(pts[min(i+1,len(pts)-1)],float)-np.array(pts[max(i-1,0)],float);T/=np.linalg.norm(T)
        X=V3(1,0,0);N=np.cross(X,T);N/=np.linalg.norm(N);ww=w/2*(1+wave*math.sin(2.1*i))
        rings.append([p-X*ww+N*t/2,p+X*ww+N*t/2,p+X*ww-N*t/2,p-X*ww-N*t/2])
    return ring_solid(rings)
def tuft(P,pos,n,L,seed,cols=('Fern','FernDk','FernLt'),w=0.8,seg=4):
    rg=np.random.default_rng(seed)
    for k in range(n):
        a=math.radians(k*360/n+rg.uniform(-18,18));dd=V3(math.cos(a),0,math.sin(a));l=L*rg.uniform(0.8,1.15);p0=V3(*pos)+dd*0.3
        P.add(blade(p0,p0+dd*l*0.35+V3(0,l*0.9,0),p0+dd*l*0.95+V3(0,l*rg.uniform(0.1,0.5),0),w,0.22,seg),cols[k%len(cols)])
def vine(P,top,length,seed,leaves=4,r0=0.3):
    rg=np.random.default_rng(seed);pts=[];n=9
    for q in range(n):
        s=q/(n-1);pts.append(top+V3(0.7*math.sin(5*s+seed),-length*s,0.6*math.sin(3*s+seed*2)))
    P.add(tube(pts,r0,5,0.2),'Vine')
    for q in range(leaves):
        s=(q+1.2)/(leaves+1.2);p=top+V3(0.7*math.sin(5*s+seed),-length*s,0.6*math.sin(3*s+seed*2));sd=1 if q%2==0 else -1;o=V3(sd,0,rg.uniform(-0.3,0.3))
        P.add(blade(p,p+o*1.3+V3(0,0.9,0),p+o*2.8+V3(0,-0.8,0),0.9,0.22,4),['VineLt','Vine','VineDk'][q%3])
ROCKS=['Rock','RockDk','RockLt']
def blk(P,rg,cx,y0,cz,sx,sy,sz,col,yawj=4.0):
    """stone block, sunk 0.12 into what is below, depth jittered so no faces coincide"""
    sy2=sy+0.12;sz2=sz*rg.uniform(0.93,1.05)
    m=box(sx,sy2,sz2,(0,0,0),((0,1,0),rg.uniform(-yawj,yawj)),((0,0,1),rg.uniform(-1.5,1.5)))
    m.apply_translation((cx,y0-0.12+sy2/2,cz+rg.uniform(-0.2,0.2)));P.add(m,col)
def course(P,rg,x0,x1,y0,h,cz,depth,wmin=2.6,wmax=4.4,k0=0):
    x=x0;k=k0
    while x<x1-0.2:
        w=min(rg.uniform(wmin,wmax),x1-x)
        if x1-(x+w)<1.4: w=x1-x
        blk(P,rg,x+w/2,y0,cz,w+0.2,h*rg.uniform(0.94,1.04),depth,ROCKS[k%3]);x+=w;k+=1
def chunk(P,rg,pos,r,col,jit=0.2):
    ry=r*rg.uniform(0.6,0.95);m=dome(r*rg.uniform(0.9,1.1),ry,r*rg.uniform(0.85,1.1),(0,0,0),7,2);jitter(m,(0,0,0),jit,rg.uniform(0,9))
    put(P,m,col,pos,yaw=rg.uniform(0,360))
def moss(P,rg,pos,rx,rz,ry=1.1,col='LeafGreen'):
    m=dome(rx,ry,rz,(0,0,0),8,2);jitter(m,(0,0,0),0.12,rg.uniform(0,9));put(P,m,col,pos,yaw=rg.uniform(0,360))
# ====================================================================== SET PIECES
# ---- hut (lean-to): back posts 24 tall, front posts 17, roof slopes down toward +Z (open front and sides)
def hut():
    rg=np.random.default_rng(501);P=newp('kit_hut_leanto','bbox','Open-sided palm-thatch lean-to for the beach camp / jungle trail: 4 crooked posts, thatch roof, hammock, plank shelf with 2 bottles. Open front faces +Z. About 30 wide x 25 tall x 22 deep.')
    posts=[((-13.5,-8.0),24.2,(1.2,0.8)),((13.5,-8.3),23.0,(-0.9,1.0)),((-13.0,8.0),16.8,(0.7,-0.9)),((13.4,7.7),17.4,(-1.1,-0.6))]
    for k,((x,z),h,(bx,bz)) in enumerate(posts):
        pts=[V3(x+bx*math.sin(math.pi*s)+0.5*s*s,h*s,z+bz*math.sin(math.pi*s)) for s in np.linspace(0,1,10)]
        P.add(tube(pts,0.95,6,0.7),'Wood1' if k%2==0 else 'Wood2')
        P.add(frustum(1.5,1.1,(pts[0][0],0,pts[0][2]),(pts[0][0],1.6,pts[0][2]),6),'WoodDk')
        top=pts[-1];P.add(frustum(1.15,1.15,top-V3(0,2.0,0),top-V3(0,1.2,0),8),'RopeK');P.add(frustum(1.1,1.1,top-V3(0,3.0,0),top-V3(0,2.4,0),8),'RopeKDk')
    # floor boards
    for k in range(6):
        z=-8.6+k*3.15;P.add(box(29.0+rg.uniform(-0.4,0.4),0.6,2.9,(0,0.32+0.04*(k%2),z),((0,1,0),rg.uniform(-1.2,1.2))),'Wood2' if k%2 else 'Wood1')
    # roof: slab along the slope + rafters + thatch fronds
    A=V3(0,24.9,-10.6);Bp=V3(0,17.0,11.6)
    sl=lambda s:A+(Bp-A)*s
    P.add(ribbon([sl(s) for s in np.linspace(0,1,5)],32.0,0.7),'StrawDk')
    d=(Bp-A)/np.linalg.norm(Bp-A);N=V3(0,d[2],-d[1])
    if N[1]<0: N=-N
    for x in(-15.0,-5.0,5.0,15.0): P.add(tube([sl(0.0)+V3(x,-0.7,0),sl(1.0)+V3(x,-0.7,0)],0.5,5,0.5),'Wood1')
    cols=['Straw','StrawLt','PalmGreenDk','Straw','StrawDk','StrawLt']
    for r,s in enumerate((0.1,0.36,0.62,0.9)):
        for q,x in enumerate(np.linspace(-14.4,14.4,9)):
            x+=rg.uniform(-0.5,0.5);p0=sl(s)+N*0.45+V3(x,0,0);c=p0+d*3.6+N*1.9;p1=p0+d*7.4+N*(-0.4-0.15*r)
            P.add(blade(p0,c,p1,1.55,0.2,5),cols[(q+r*2)%6])
    for q,x in enumerate(np.linspace(-13.0,13.0,6)): # ridge cap fronds sticking over the top edge
        p0=sl(0.0)+N*0.4+V3(x,0,0);P.add(blade(p0,p0+V3(0,2.4,-1.2),p0+V3(0.0,0.9,-3.4),1.3,0.18,5),['PalmGreenDk','PalmGreen','Straw'][q%3])
    # hammock (along Z, left side) + ropes
    hp=[V3(-11.6,11.4-3.0*math.sin(math.pi*s)**1.2,-7.0+14.0*s) for s in np.linspace(0,1,9)]
    P.add(ribbon(hp,4.2,0.4,0.05),'Canvas');P.add(ribbon([hp[0]+V3(0,0.2,0),hp[1]+V3(0,0.0,0)],4.2,0.2),'CanvasDk')
    for z,pi_ in((-7.0,0),(7.0,8)):
        for sx in(-1.6,1.6):
            P.add(tube([V3(-13.3,12.8,z*1.0+(0.3 if z<0 else -0.2)),V3(-11.6+sx,11.5,z)],0.13,4,0.13),'RopeK')
    P.add(box(2.6,0.5,1.6,(-11.6,hp[3][1]+0.45,-2.8),((0,1,0),10)),'CanvasDk')
    # shelf on the back: crossbeam, plank, brackets, bottles
    P.add(beam((-13.5,13.2,-8.9),(13.5,13.4,-9.0),0.9,0.9),'Wood2')
    P.add(box(11.5,0.6,2.5,(5.0,14.0,-8.8)),'Plank')
    for x in(0.5,9.5): P.add(box(0.5,1.6,1.6,(x,13.2,-8.5),((0,0,1),0)),'PlankDk')
    for x,s,tl in((3.2,1.0,0),(6.4,0.9,12)):
        bt=lathe([(0.04,0.0),(0.6,0.0),(0.62,1.7),(0.45,2.2),(0.27,2.6),(0.27,3.3),(0.04,3.3)],8);put(P,bt,'Bottle' if s>0.95 else 'BottleDk',(x,14.3,-8.8),s,rot=((0,0,1),tl))
        put(P,frustum(0.3,0.3,(0,3.3,0),(0,3.75,0),8),'Plank',(x,14.3,-8.8),s,rot=((0,0,1),tl))
    tuft(P,(-6,0.5,3),6,3.0,11,('FernLt','Fern'),0.7);tuft(P,(9,0.5,-3),5,2.8,12,('Fern','FernDk'),0.7)
    settle(P,'bbox')
hut()
# ---- ruin arch
def ruin_arch():
    rg=np.random.default_rng(502);P=newp('kit_ruin_arch','bbox','Broken stone arch with one side collapsed into rubble, moss caps and a vine strip draped over the crown. Place over the jungle trail. About 35 wide x 30 tall.')
    D=6.0
    hs=[2.9,2.6,3.0,2.7,2.8];y=0.0
    for k,h in enumerate(hs):
        course(P,rg,-16.5+0.15*(k%2),-11.5,y,h,0,D,2.4,3.0,k);y+=h   # left pillar (to ~14)
    yL=y
    y=0.0
    for k,h in enumerate((2.9,2.7,2.6)):
        course(P,rg,11.5,16.5-1.2*(k==2),y,h,0,D,2.4,3.0,k+1);y+=h    # right pillar, broken at ~8
    blk(P,rg,13.0,y,0.2,2.2,1.5,D*0.7,'RockLt',10);blk(P,rg,15.4,y,-0.4,1.7,1.0,D*0.6,'Rock',20)
    cx,cy,Ri,T=0.0,yL,11.5,3.2
    angs=np.linspace(180,80,10)
    for k,th in enumerate(angs):
        r=Ri+T/2;t=math.radians(th);L=r*math.radians(11.5)*1.04
        m=box(L,T*(1.25 if abs(th-90)<6 else 1.0),D*rg.uniform(0.93,1.05),(0,0,0),((0,0,1),th-90));m.apply_translation((cx+r*math.cos(t),cy+r*math.sin(t),rg.uniform(-0.15,0.15)));P.add(m,ROCKS[k%3])
    # one overhanging stone past the crown, tilted
    t=math.radians(69);r=Ri+T/2;m=box(3.2,T*0.95,D*0.9,(0,0,0),((0,0,1),69-90+9));m.apply_translation((cx+r*math.cos(t)+0.6,cy+r*math.sin(t)-0.4,0.3));P.add(m,'RockLt')
    # rubble pile (right side, under the missing half of the arch)
    for k in range(13):
        a=rg.uniform(0,2*math.pi);rr=rg.uniform(0,7.5);pos=(7.5+rr*math.cos(a)*1.05,0.0,rr*math.sin(a)*0.8+1.2);chunk(P,rg,pos,rg.uniform(1.2,2.8)*(1.2-0.6*rr/7.5)+0.8,ROCKS[k%3])
    for k,(x,z,yw) in enumerate(((5.5,-2.5,30),(9.0,3.8,-20),(12.5,-3.5,60))):
        m=box(rg.uniform(3.0,4.2),1.5,rg.uniform(2.2,3.0),(0,0,0),((0,0,1),rg.uniform(-18,18)),((0,1,0),yw));m.apply_translation((x,1.2+0.3*k,z));P.add(m,ROCKS[(k+1)%3])
    # moss caps
    for th in(100,114,128,146,163):
        t=math.radians(th);r=Ri+T+0.05;m=dome(2.7,0.95,3.2,(0,0,0),8,2);jitter(m,(0,0,0),0.1,th);m.apply_transform(Rm((0,0,1),th-90));m.apply_translation((cx+r*math.cos(t),cy+r*math.sin(t),0));P.add(m,['LeafGreen','LeafDk','LeafLt'][th%3])
    moss(P,rg,(-14.0,yL-0.2,0),3.4,3.6,1.1)
    ytop_r=2.9+2.7+2.6
    moss(P,rg,(13.0,ytop_r+1.6,0.2),2.0,2.6,0.9,'LeafDk');moss(P,rg,(9.0,3.4,3.6),2.2,2.2,0.8,'LeafLt');moss(P,rg,(7.0,4.2,-1.5),2.4,2.4,0.9)
    # vine strip draped over the crown (front face) + leaf blades over the arch top
    for k,th in enumerate(np.linspace(168,92,9)):
        t=math.radians(th);r=Ri+T-0.2;top=V3(cx+r*math.cos(t),cy+r*math.sin(t),D/2+0.35)
        vine(P,top,rg.uniform(5.5,11.0)*(1.0 if th>120 else 0.8),70+k,leaves=3)
    for k,th in enumerate(np.linspace(100,170,10)):
        t=math.radians(th);r=Ri+T;p=V3(cx+r*math.cos(t),cy+r*math.sin(t),(1.2 if k%2 else -1.2));sd=1 if k%2 else -1
        P.add(blade(p,p+V3(-math.cos(t)*0.5,1.4,sd*1.2),p+V3(sd*0.3,0.9,sd*3.6),1.1,0.2,4),['LeafGreen','LeafLt','LeafDk'][k%3])
    tuft(P,(-9.5,0.3,3.9),5,2.8,13,('FernLt','Fern'),0.7);tuft(P,(2.0,0.3,-3.5),5,2.8,14,('Fern','FernDk'),0.7)
    settle(P,'bbox')
ruin_arch()
# ---- ruin wall chunk (~20 wide), window gap, stepped broken top
def ruin_wall():
    rg=np.random.default_rng(503);P=newp('kit_ruin_wall','bbox','Separate broken wall chunk (about 20 wide, 16 tall) with a window gap, stepped broken top, moss caps; scatter along the jungle trail or beside the arch.')
    D=4.2;H=[3.1,2.9,3.1,2.9,3.0,2.8]
    rows=[(-10,10),(-10,10),(-10,10),(-10,5.5),(-10,-1.5),(-10,-6.5)]
    y=0.0
    for r,(xa,xb) in enumerate(rows):
        h=H[r]
        if r in(1,2): # window gap x in (1.2, 5.0): skip
            course(P,rg,xa,1.2,y,h,0,D,2.4,3.4,r);course(P,rg,5.0,xb,y,h,0,D,2.4,3.4,r+2)
        else: course(P,rg,xa,xb,y,h,0,D,2.4,3.6,r)
        y+=h
    # lintel stone over the window (row 3 covers it already); sill and buttress
    blk(P,rg,3.1,2.9,0.3,4.6,0.9,D*1.15,'RockLt',2)
    blk(P,rg,-10.9,0.0,0.0,2.0,5.2,D*1.5,'RockDk',3)
    for k in range(7):
        a=rg.uniform(0,2*math.pi);chunk(P,rg,(rg.uniform(6.0,12.5),0.0,rg.uniform(-3.4,4.5)),rg.uniform(1.0,2.4),ROCKS[k%3])
    for k,(x,z,yw) in enumerate(((7.5,3.4,25),(10.5,-1.0,-35),(4.0,4.4,70))):
        m=box(rg.uniform(2.6,3.6),1.4,rg.uniform(2.0,2.8),(0,0,0),((0,0,1),rg.uniform(-14,14)),((0,1,0),yw));m.apply_translation((x,1.0+0.2*k,z));P.add(m,ROCKS[(k+2)%3])
    tops=[(-8.4,sum(H[:6]),1.0),(-3.6,sum(H[:5]),0.8),(2.4,sum(H[:4]),0.5)]
    moss(P,rg,(-8.0,sum(H[:6])-0.1,0),3.6,2.8,1.0);moss(P,rg,(-3.5,sum(H[:5])-0.1,0.2),3.0,2.8,0.9,'LeafDk');moss(P,rg,(2.0,sum(H[:4])-0.1,0),3.2,2.7,0.9,'LeafLt');moss(P,rg,(8.5,sum(H[:3])-0.1,0),3.3,2.7,0.9)
    for k,x in enumerate((-9.2,-5.0)):
        vine(P,V3(x,sum(H[:6])+0.2 if k==0 else sum(H[:5])+0.2,D/2+0.3),rg.uniform(5,8.5),90+k,leaves=3)
    tuft(P,(-4.0,0.3,3.6),6,3.0,15,('FernLt','Fern'),0.7);tuft(P,(5.0,0.3,3.8),5,2.6,16,('Fern','FernDk'),0.7);tuft(P,(-9.5,0.3,-3.0),5,2.6,17,('Fern','FernDk'),0.7)
    scaleP(P,0.88);settle(P,'bbox')
ruin_wall()
# ---- boulder pile (3-4 stacked rounded boulders, one leaning), ferns in the cracks, base sunk 2 studs below y=0
def boulder_pile():
    rg=np.random.default_rng(504);P=newp('kit_boulder_pile','sunk2','Big rounded boulder pile (3 stacked + 1 leaning), mossy tops, ferns in the cracks. Base is meant to be sunk: lowest point is exactly 2 studs below y=0. About 30 wide x 20 tall above ground.')
    def bo(c,r,col,seed,tilt=0.0,jit=0.1):
        m=uvsphere(r,(0,0,0),12,8);jitter(m,(0,0,0),jit,seed)
        cap=capdome(r[0]*1.04,r[1]*1.04,r[2]*1.04,0.92,10,3);jitter(cap,(0,0,0),jit,seed)
        for q,cc in((m,col),(cap,'LeafGreen' if seed%2 else 'LeafLt')):
            q=q.copy();q.apply_transform(Rm((0,0,1),tilt));q.apply_translation(c);P.add(q,cc)
    bo((-3.5,6.0,0.0),(10.5,8.0,9.8),'Rock',1);bo((9.5,3.6,3.2),(8.8,6.6,8.0),'RockDk',2);bo((-3.0,14.0,-0.8),(6.8,5.8,6.3),'RockLt',3)
    bo((-14.6,5.6,4.5),(4.2,8.4,4.6),'Rock',4,tilt=-20,jit=0.12)
    tuft(P,(3.8,9.6,3.8),6,3.4,21,('FernLt','Fern'),0.8);tuft(P,(-11.2,3.8,6.2),5,3.0,22,('Fern','FernDk'),0.8);tuft(P,(-0.5,7.8,5.5),5,3.0,23,('FernLt','FernDk'),0.8)
    tuft(P,(14.0,0.5,0.5),5,3.0,24,('Fern','FernLt'),0.8);tuft(P,(-3.5,0.2,10.6),6,3.4,25,('FernLt','Fern'),0.8)
    scaleP(P,0.84);settle(P,'sunk2')
boulder_pile()
# ---- crate stack
def crate(P,c,s,yaw,open_side=False):
    h=s/2;q=Part('c');q.add(box(s,s*0.08,s,(0,s*0.04,0)),'WoodDk')
    for sx in(-1,1):
        for sz in(-1,1): q.add(box(s*0.2,s*1.08,s*0.2,(sx*h,h,sz*h)),'WoodDk')
    for f in range(4):
        for k in(-1,0,1):
            w=s*0.24
            if f==0: pos=(k*s*0.3,h,h+s*0.04);ex=(w,s*0.9,s*0.1)
            elif f==1: pos=(k*s*0.3,h,-h-s*0.04);ex=(w,s*0.9,s*0.1)
            elif f==2: pos=(h+s*0.04,h,k*s*0.3);ex=(s*0.1,s*0.9,w)
            else: pos=(-h-s*0.04,h,k*s*0.3);ex=(s*0.1,s*0.9,w)
            q.add(box(*ex,pos),'Wood2' if k!=0 else 'Wood1')
    if not open_side:
        for k in(-1,0,1): q.add(box(s*0.24,s*0.1,s*0.9,(k*s*0.3,s+s*0.03,0)),'Wood2')
    else: # lid planks hanging off one side
        q.add(box(s*0.24,s*0.1,s*0.8,(0.3*s,s+s*0.03,0),((0,0,1),-25)),'Wood2')
    M=Tm(c)@Rm((0,1,0),yaw)
    for m,col,sm in q.items:
        P.add(xf(m,M),col)
def barrel(P,c,s=1.0):
    ys=[0,0.8,1.8,2.6,3.4,4.4,5.2];rs=[1.9,2.2,2.45,2.55,2.45,2.2,1.9];Q=Part('b')
    Q.add(lathe(list(zip(rs,ys)),12),'Wood2')
    for y in(0.9,2.0,3.2,4.3):
        r=float(np.interp(y,ys,rs))+0.14;Q.add(frustum(r,r,(0,y-0.18,0),(0,y+0.18,0),12),'Iron')
    Q.add(lathe([(0.05,5.05),(2.0,5.05),(2.0,5.4),(0.05,5.4)],12),'Plank')
    for m,col,sm in Q.items: put(P,m,col,c,s)
def crate_stack():
    rg=np.random.default_rng(505);P=newp('kit_crate_stack','bbox','Cargo pile for the beach and wreck deck: 2 stacked crates with a canvas tarp half pulled off, one open crate spilling coconuts, 2 barrels, a rope coil. About 19 wide x 12 tall.')
    crate(P,(-4.0,0,-1.5),6.2,8);crate(P,(-4.3,6.2,-1.7),5.2,-16)
    path=[(11.85,-1.9),(11.85,0.4),(11.25,1.4),(9.6,2.2),(7.0,2.55),(4.0,2.8),(1.5,3.3),(0.42,4.5),(0.38,6.5),(0.38,8.2)]
    P.add(ribbon([V3(-4.2,y,z) for y,z in path],5.6,0.3,0.06),'Canvas')
    P.add(ribbon([V3(-4.2,11.5,-1.9),V3(-4.2,11.5,-0.6)],5.9,0.12),'CanvasDk')
    # open crate lying on its side, opening faces +Z
    Q=Part('o');crate(Q,(0,0,0),4.6,0,True)
    for m,col,sm in Q.items:
        m=m.copy();m.apply_transform(Rm((1,0,0),90));m.apply_transform(Rm((0,1,0),12));m.apply_translation((3.6,2.3,-1.5));P.add(m,col)
    for k,(x,z) in enumerate(((3.9,2.4),(5.4,3.0),(2.6,4.6),(4.6,5.8),(6.3,6.0),(1.6,7.0),(3.5,7.9))):
        r=0.95 if k%3 else 1.05;put(P,uvsphere(r,(0,0,0),8,5),'Coconut' if k%2 else 'CoconutDk',(x,r*0.98,z),yaw=rg.uniform(0,90))
    put(P,uvsphere(0.95,(0,0,0),8,5),'Coconut',(3.2,1.7,3.1));put(P,uvsphere(0.95,(0,0,0),8,5),'CoconutDk',(4.4,2.7,1.8))
    barrel(P,(8.6,0,-3.2));barrel(P,(9.4,0,2.8),0.92)
    pts=[]
    for q in range(48):
        s=q/47;th=s*3.0*2*math.pi;r=2.5-1.2*s;pts.append(V3(r*math.cos(th),0.5+0.34*s*3.0,r*math.sin(th)))
    cp=Part('coil');cp.add(tube(pts,0.5,6,0.5),'RopeK');cp.add(tube([pts[-1],pts[-1]+V3(0.6,0.0,0.5),V3(2.6,0.5,2.2),V3(3.8,0.45,3.1)],0.45,6,0.4),'RopeKDk')
    for m,col,sm in cp.items: put(P,m,col,(4.5,0,-6.8),0.8)
    settle(P,'bbox')
crate_stack()
# ---- broken rowboat on its side
def rowboat():
    rg=np.random.default_rng(506);P=newp('kit_rowboat_broken','bbox','Split rowboat tipped on its side in the sand with faded teal paint, one oar stuck upright, the other cracked on the ground. About 20 long; open side faces +Z.')
    H=Part('h');xs=np.linspace(-10,10,11)
    def b(x): return 3.3*max(1-(x/10)**2,0.0)**0.6+0.25
    def yt(x): return 1.5+0.9*(x/10)**2
    def dh(x): return 2.4*(1-0.5*(x/10)**2)
    def sec(x,phi,th=0.0,sgn=1):
        return V3(x,yt(x)-(dh(x)-th)*math.cos(phi),sgn*(b(x)-th)*math.sin(phi))
    phis=[0.0,0.3,0.62,0.95,1.28,1.5708]
    pcols=['Paint','PaintDk','PaintLt','Paint','PaintDk']
    for sgn in(1,-1):
        for k in range(5):
            segs=[(-10.0,10.0)]
            if sgn==-1 and k in(2,3): segs=[(-10.0,-2.4+0.9*(k-2)),(3.4+1.2*(k-2),10.0)]
            for (xa,xb) in segs:
                n=max(int((xb-xa)/2.0)+1,2);rings=[]
                for x in np.linspace(xa,xb,n+1):
                    th=0.5;o1=sec(x,phis[k],0,sgn);o2=sec(x,phis[k+1],0,sgn);i2=sec(x,phis[k+1],th,sgn);i1=sec(x,phis[k],th,sgn)
                    rings.append([o1,o2,i2,i1])
                H.add(ring_solid(rings),pcols[(k+(0 if sgn==1 else 1))%5])
    # keel, rails, ribs, thwarts
    H.add(tube([sec(x,0,-0.25,1) for x in xs],0.42,4,0.42),'Wood2')
    for sgn in(1,-1): H.add(tube([V3(x,yt(x)+0.12,sgn*(b(x)-0.05)) for x in xs],0.26,4,0.26),'Wood2')
    for x in(-7.0,-3.5,0.0,3.5,7.0):
        pts=[sec(x,p,0.62,sg) for sg,p in [(-1,1.45),(-1,1.1),(-1,0.75),(-1,0.38),(1,0.0),(1,0.38),(1,0.75),(1,1.1),(1,1.45)]]
        H.add(tube(pts,0.3,4,0.3),'Wood1')
    H.add(box(1.5,0.4,2*b(-3.0)-0.9,(-3.0,yt(-3.0)-0.8,0)),'Wood2')
    H.add(box(1.4,0.4,2*b(3.4)*0.55,(3.4,yt(3.4)-0.8,-b(3.4)*0.42),((0,1,0),6)),'Wood1')   # broken thwart (half missing)
    for q,(x,zz,yw) in enumerate(((0.6,-2.6,20),(1.6,-2.9,-30))):
        H.add(box(rg.uniform(1.8,2.4),0.35,0.6,(x,yt(x)-1.05+0.2*q,zz),((0,1,0),yw),((0,0,1),12)),'WoodDk')
    roll=72.0
    for m,col,sm in H.items:
        m=m.copy();m.apply_transform(Rm((1,0,0),roll));P.add(m,col)
    mn,mx=bounds(P);shift(P,0,-mn[1],0)
    mn,mx=bounds(P);zf=mx[2]
    # oars
    def oar(base,tip,blade,col_sh='Wood2',L=None):
        d=np.array(tip,float)-np.array(base,float);d/=np.linalg.norm(d)
        P.add(frustum(0.28,0.22,base,np.array(base)+d*(L or 10.5),6),col_sh)
        bs=np.array(base)+d*(L or 10.5);m=box(1.5,3.4,0.22);m.apply_transform(align_vectors([0,1,0],d));m.apply_translation(bs+d*1.6);P.add(m,blade)
    oar(V3(-6.6,0,zf+1.6),V3(-6.9,10.5,zf+1.9),'PaintLt')
    # cracked oar lying on the sand: handle half, jagged break, loose blade half
    base=V3(-7.5,0.3,zf+3.6);d=V3(0.97,0.0,0.24);d/=np.linalg.norm(d)
    P.add(frustum(0.28,0.24,base,base+d*5.6,6),'Wood2')
    for q,(off,L) in enumerate(((0.0,1.0),(0.3,1.5),(-0.3,0.8))):
        P.add(beam(base+d*5.5+V3(0,0.1,off),base+d*(5.5+L)+V3(0,0.1,off),0.28,0.3),'WoodDk')
    b2=base+d*8.2+V3(0.4,0,-0.9)
    P.add(frustum(0.24,0.22,b2,b2+d*3.2,6),'Wood1');m=box(3.4,0.22,1.5);m.apply_transform(Rm((0,1,0),-14));m.apply_translation(b2+d*4.9+V3(0,0.05,0));P.add(m,'PaintLt')
    # small sand drifts against the hull
    for x,z,r in((-7.0,mn[2]+1.0,3.2),(6.0,mn[2]+0.6,3.8)):
        m=dome(r,0.95,r*0.8,(0,0,0),8,2);jitter(m,(0,0,0),0.1,x);put(P,m,'SandTop',(x,0,z))
    settle(P,'bbox')
rowboat()
# ====================================================================== LIGHTS
def tongue(P,col,r,h,base,lean_dir,lean_deg):
    prof=[(0.05,0.0),(r*0.62,0.05*h),(r*0.95,0.2*h),(r,0.36*h),(r*0.82,0.55*h),(r*0.5,0.76*h),(r*0.2,0.92*h),(0.04,h)]
    m=lathe(prof,8)
    if lean_deg:
        ax=(lean_dir[1],0,-lean_dir[0]);m=m.copy();m.apply_transform(Rm(ax,lean_deg))
        # make sure it leans toward lean_dir (tip x/z has positive projection)
        tip=m.vertices[m.vertices[:,1].argmax()]
        if tip[0]*lean_dir[0]+tip[2]*lean_dir[1]<0: m=lathe(prof,8);m.apply_transform(Rm(ax,-lean_deg))
    m.apply_translation(base);P.add(m,col)
def torch(i,H,fh,use):
    P=newp(i,'bbox',use);yt=H-0.35-(fh-0.3)*0.915;Hp=yt
    n=max(int(Hp/1.55),2);ys=np.linspace(0,Hp,n+1)
    for k in range(n): P.add(frustum(0.52-0.03*k/n,0.5-0.03*(k+1)/n,(0,ys[k],0),(0,ys[k+1]-0.06,0),7),'Bamboo' if k%2==0 else 'BambooDk')
    for y in ys[1:-1]: P.add(frustum(0.66,0.66,(0,y-0.14,0),(0,y+0.14,0),7),'BambooDk')
    for y in(yt-0.9,yt-1.4,1.2): P.add(frustum(0.62,0.62,(0,y-0.1,0),(0,y+0.1,0),8),'RopeK')
    # low bowl: rim only 0.55 above the pole top, flame pokes well above it
    P.add(lathe([(0.3,yt-0.7),(1.0,yt-0.4),(1.7,yt+0.1),(1.95,yt+0.5),(1.95,yt+0.62),(1.5,yt+0.62),(1.25,yt+0.34),(0.05,yt+0.2)],8,0.2),'Wood1')
    P.add(frustum(1.15,1.15,(0,yt-0.15,0),(0,yt+0.25,0),8),'RopeKDk')
    yb=yt+0.3;F=fh-0.3
    # three orange tongues around a taller bright core
    for q,(ang,hh,rr) in enumerate(((20,0.93,0.62),(140,0.72,0.55),(260,0.6,0.5))):
        a_=math.radians(ang);d=(math.cos(a_),math.sin(a_));tongue(P,'Flame',rr*(fh/3.75)**0.5*1.0,F*hh,(0.5*d[0]*(fh/3.75)**0.5,yb,0.5*d[1]*(fh/3.75)**0.5),d,14)
    tongue(P,'FlameCore',0.78*(fh/3.75)**0.5,F*0.84,(0,yb+0.05,0),(1,0),0)
    gy=[V[1] for m,c,_ in P.items if c in('Flame','FlameCore') for V in m.vertices];P.att['LightAttach']=(0.0,round((min(gy)+max(gy))/2,4),0.0);settle(P,'base')
torch('kit_torch_tiki',9.0,3.75,'Tiki torch (about 9 tall) for pad edges and the beach: bamboo pole, rope wraps, low bowl head with a teardrop flame (3 tongues + brighter core). Flame is a separate _Glow object; LightAttach at the flame centre.')
torch('kit_torch_tiki_short',6.0,3.1,'Short tiki torch (6 tall) for path edges. Low bowl, teardrop flame (3 tongues + core) as a separate _Glow object; LightAttach at the flame centre.')
def lantern(P,o=(0,0,0)):
    pts=[V3(0.42*math.sin(a),-0.5+0.42*math.cos(a),0) for a in np.linspace(0,2*math.pi,11)]
    put(P,tube(pts,0.08,4,0.08),'LanternIron',o)
    put(P,frustum(0.2,0.64,(0,-1.0,0),(0,-1.45,0),6),'LanternIron',o);put(P,frustum(0.7,0.7,(0,-1.45,0),(0,-1.62,0),6),'LanternIronLt',o)
    for k in range(4):
        a=math.radians(45+90*k);put(P,box(0.14,1.3,0.14,(0.6*math.cos(a),-2.3,0.6*math.sin(a))),'LanternIron',o)
    put(P,frustum(0.5,0.5,(0,-1.62,0),(0,-2.72,0),6),'Glow',o)
    put(P,frustum(0.7,0.7,(0,-2.72,0),(0,-2.9,0),6),'LanternIronLt',o);put(P,frustum(0.5,0.12,(0,-2.9,0),(0,-3.2,0),6),'LanternIron',o)
    return (o[0],o[1]-2.1,o[2])
P=newp('kit_lantern_hanging','ringtop','Hanging lantern (about 3.2 tall): iron frame, amber glass (separate Glow object), ring top. PIVOT IS THE TOP OF THE RING (y=0); the lantern hangs below it. LightAttach at the glass.')
P.att['LightAttach']=lantern(P)
def lantern_post():
    rg=np.random.default_rng(607);P=newp('kit_lantern_post','base','Crooked wooden lantern post (about 10 tall) with a crossbar and a hanging lantern; origin is the post base, lantern hangs 3.4 studs to +X. Lantern glass is a separate Glow object; LightAttach at the glass.')
    pts=[V3(0.55*math.sin(2.0*s),10.0*s,0.45*math.sin(3.0*s)) for s in np.linspace(0,1,10)]
    P.add(tube(pts,0.62,6,0.42),'Wood1');P.add(frustum(1.1,0.8,(0,0,0),(0,1.2,0),6),'WoodDk')
    P.add(beam((-0.4,9.35,0.2),(4.2,9.05,0.0),0.55,0.55),'Wood2')
    P.add(beam((0.3,7.2,0.3),(2.8,9.1,0.0),0.4,0.4),'Wood1')
    P.add(frustum(0.72,0.72,(0.5,8.1,0.37),(0.5,8.45,0.37),8),'RopeK')
    P.add(frustum(0.4,0.4,(3.4,8.78,0),(3.4,9.12,0),6),'RopeK')
    P.add(tube([V3(3.4,8.9,0),V3(3.4,8.4,0)],0.07,4,0.07),'RopeKDk')
    P.att['LightAttach']=lantern(P,(3.4,8.4,0.0))
    for k,(x,z,r) in enumerate(((0.9,0.8,1.0),(-0.9,0.4,0.8),(0.2,-1.0,0.9))): chunk(P,rg,(x*1.1,0.0,z),r,ROCKS[k%3],0.15)
    settle(P,'base')
lantern_post()
# ====================================================================== SKYLINE
def canopy_wall():
    rg=np.random.default_rng(711);P=newp('kit_canopy_wall','bbox','Dark treetop curtain for the far skyline (about 200 wide x 60 tall). Uneven top line with 4 taller palm-crown bumps, scalloped tapered bottom. Closed solid (front, back, top all modelled = double sided). Place 300+ studs behind the course, fog friendly; tile end to end or scale.')
    xs=np.linspace(-100,100,101)
    hf=lambda x:30+7*math.sin(x*0.063+0.5)+5*math.sin(x*0.17+1)+3*math.sin(x*0.39+2)+2.0*math.sin(x*0.83)
    bot=lambda x:max(0.0,9*(math.sin(x*0.11+1.0)+0.7*math.sin(x*0.29+0.4)-0.25))
    rings=[]
    for x in xs:
        h=hf(x)-5;b0=bot(x);b0=min(b0,h*0.6);H_=h-b0
        rings.append([(x,b0,1.6),(x,b0+0.4*H_,5),(x,b0+0.85*H_,5),(x,h,0),(x,b0+0.85*H_,-5),(x,b0+0.4*H_,-5),(x,b0,-1.6)])
    P.add(ring_solid(rings),'CanopyA')
    crowns=[-72,-28,22,66]
    x=-92.0;k=0
    while x<93:
        r=rg.uniform(9.0,13.5);ry=rg.uniform(7.0,13.0);y=hf(x)-9.0
        m=dome(r,ry,rg.uniform(6.0,7.5),(0,0,0),9,3);jitter(m,(0,0,0),0.14,k);put(P,m,['CanopyA','CanopyC','CanopyA','CanopyB'][k%4],(x,y,rg.uniform(-0.8,0.8)),yaw=rg.uniform(-8,8))
        x+=r*rg.uniform(0.85,1.15);k+=1
    # palm-crown bumps: a tall narrow dome with drooping fan domes at the top, poking above the line (~1.5x local height)
    for j,cx in enumerate(crowns):
        cx+=rg.uniform(-5,5);y0=hf(cx)-8.0;top=[55.0,60.0,57.0,52.0][j]-y0
        put(P,jitter(dome(6.2,top*0.9,5.5,(0,0,0),9,4),(0,0,0),0.1,40+j),['CanopyB','CanopyC'][j%2],(cx,y0,0))
        for q,(dx,dyf,tilt) in enumerate(((-7.5,0.82,28),(7.5,0.86,-28),(0.0,0.97,0))):
            f=dome(7.5,3.6,6.0,(0,0,0),9,3);jitter(f,(0,0,0),0.12,50+j*3+q)
            put(P,f,['CanopyC','CanopyA','CanopyB'][(q+j)%3],(cx+dx,y0+top*dyf-1.2,0),rot=((0,0,1),tilt))
    settle(P,'bbox')
canopy_wall()
def cliff_ridge():
    rg=np.random.default_rng(702);P=newp('kit_cliff_ridge','bbox','Jagged dark rock ridge with green tops for the far skyline (about 300 wide x 120 tall x 60 deep). Place 300+ studs behind the course, fog friendly.')
    nx,nz=120,10;X=np.linspace(-150,150,nx+1);Z=np.linspace(-30,30,nz+1)
    pk=[(-142+k*21.5+rg.uniform(-5,5),rg.uniform(62,112),rg.uniform(15,26)) for k in range(14)];pk=[(x,h,w*1.9) for x,h,w in pk];pk[5]=(pk[5][0],120.0,26.0)
    def prof(x): return max(40+10*math.sin(x*0.09),max(h*(0.5+0.5*math.cos(math.pi*min(1.0,abs(x-xk)/w)))**0.85 for xk,h,w in pk))
    Hm=np.zeros((nz+1,nx+1))
    for j,z in enumerate(Z):
        f=max(0.0,1-abs(z/30.0)**1.5)**0.9
        for i,x in enumerate(X): Hm[j,i]=8.0+(prof(x)-8.0)*f+2.0*math.sin(x*0.31+z*0.2)*f+rg.uniform(-1.0,1.0)*f
    Hm*=120.0/Hm.max()
    V=[(X[i],Hm[j,i],Z[j]) for j in range(nz+1) for i in range(nx+1)];idx=lambda i,j:j*(nx+1)+i;F=[]
    for j in range(nz):
        for i in range(nx):
            a,b,c,d=idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1)
            F+=[[a,d,c],[a,c,b]] if (i+j)%2==0 else [[a,d,b],[b,d,c]]
    n0=len(V)
    # skirts down to y=0 around the border
    def skirt(cells):
        nonlocal V,F
        base={}
        for (i,j) in cells:
            base[(i,j)]=len(V);V.append((X[i],0.0,Z[j]))
        for p,q in zip(cells[:-1],cells[1:]):
            a,b=idx(*p),idx(*q);a0,b0=base[p],base[q];F+=[[a,a0,b0],[a,b0,b]]
    skirt([(i,nz) for i in range(nx+1)]);skirt([(i,0) for i in range(nx+1)][::-1]);skirt([(0,j) for j in range(nz+1)][::-1]);skirt([(nx,j) for j in range(nz+1)])
    m=trimesh.Trimesh(np.array(V),np.array(F),process=False);m.fix_normals()
    nrm=m.face_normals;cen=m.triangles_center
    gsel=((nrm[:,1]>0.30)&(cen[:,1]>10))|(cen[:,1]>82);col=np.where(gsel,0,1+((np.floor(cen[:,1]/9.0).astype(int)+np.floor(cen[:,0]/17.0).astype(int))%3))
    for c,name in enumerate(['RidgeGreen','Rock','RockDk','RockLt']):
        sel=np.where(col==c)[0]
        if len(sel): P.add(m.submesh([sel],append=True),name)
    settle(P,'bbox')
cliff_ridge()
# ====================================================================== EXPORT
os.makedirs(os.path.join(OUT,'geom'),exist_ok=True);report={}
for k,p in props.items():
    main=Part(k);glow=Part(k);fl=Part(k);co=Part(k)
    for m,c,sm in p.items: (glow if c=='Glow' else fl if c=='Flame' else co if c=='FlameCore' else main).add(m,c,sm)
    objs=[];tris=0
    for nm,pp,mt in((k,main,'main'),(k+'_Glow',glow,'glow'),(k+'_Flame',fl,'flame'),(k+'_Core',co,'core')):
        if not pp.items: continue
        g=pp.merged();V=np.array(g['verts']);g['verts']=np.round(V,4).tolist()
        objs.append(dict(name=nm,mat=mt,verts=g['verts'],tris=g['tris'],uvs=g['uvs'],smooth=g['smooth']));tris+=len(g['tris'])
    emp=[dict(name=n,pos=[round(float(x),4) for x in v]) for n,v in p.att.items()]
    json.dump({k:dict(objects=objs,empties=emp)},open(os.path.join(OUT,'geom',k+'.json'),'w'))
    V=np.concatenate([m.vertices for m,_,_ in p.items])
    report[k]=dict(tris=tris,bbox=dict(min=np.round(V.min(0),2).tolist(),max=np.round(V.max(0),2).tolist()),size=np.round(V.max(0)-V.min(0),2).tolist(),mode=META[k]['mode'],use=META[k]['use'],
        objects=[o['name'] for o in objs],attach={a:[round(float(x),3) for x in v] for a,v in p.att.items()})
    print(k,tris,report[k]['size'],'minY',report[k]['bbox']['min'][1],report[k]['attach'])
json.dump(report,open(os.path.join(OUT,'box_report.json'),'w'),indent=1)
palette_png(os.path.join(OUT,'kit_palette.png'));json.dump(PAL,open(os.path.join(OUT,'palette.json'),'w'))
