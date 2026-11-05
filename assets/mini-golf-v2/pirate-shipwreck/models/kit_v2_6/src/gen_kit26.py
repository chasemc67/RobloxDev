# Pirate Shipwreck kit_v2 generator (Look B). Run: /workspace/.geo/bin/python gen_kit2.py <outdir>
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
# ================= kit_v2_6: stylised, rounded ruin wall (replaces the blocky kit_v2 version; same footprint/bounds/pivot)
def rstone(sx,sy,sz,b=0.3,seed=0,noise=0.06):
    """bevelled / rounded stone: a 5x5-per-face cube grid pushed onto a rounded box, low-frequency noise + tiny per-vertex jitter (192 tris)"""
    g=[-1,-0.8,0,0.8,1];idx={};V=[];F=[]
    def vid(q):
        k=tuple(q)
        if k not in idx: idx[k]=len(V);V.append(q)
        return idx[k]
    for a in range(3):
        for s in(-1,1):
            for i in range(4):
                for j in range(4):
                    quad=[]
                    for di,dj in((0,0),(1,0),(1,1),(0,1)):
                        q=[0,0,0];q[a]=s;q[(a+1)%3]=g[i+di];q[(a+2)%3]=g[j+dj];quad.append(vid(tuple(q)))
                    F+=[[quad[0],quad[1],quad[2]],[quad[0],quad[2],quad[3]]]
    V=np.array(V,float);inner=np.clip(V,-(1-b),1-b);d=V-inner;n=np.linalg.norm(d,axis=1,keepdims=True)
    V=np.where(n>1e-9,inner+d/np.maximum(n,1e-9)*b,V)
    rg=np.random.default_rng(seed+7)
    u=V/np.linalg.norm(V,axis=1,keepdims=True)
    V=V*np.array([1+noise*nz(x,seed*0.7) for x in u])[:,None]
    V=V*np.array([sx/2,sy/2,sz/2])+rg.uniform(-0.03,0.03,V.shape)*min(sx,sy,sz)*0.3
    m=trimesh.Trimesh(V,np.array(F),process=False)
    c=m.vertices.mean(0);fl=[k for k,t in enumerate(m.faces) if np.dot(np.cross(V[t[1]]-V[t[0]],V[t[2]]-V[t[0]]),V[t].mean(0)-c)<0]
    for k in fl: m.faces[k]=m.faces[k][::-1]
    return m
def place(m,pos,rx=0.0,ry=0.0,rz=0.0):
    m=m.copy()
    for ax,a in(((0,0,1),rz),((1,0,0),rx),((0,1,0),ry)):
        if a: m.apply_transform(Rm(ax,a))
    m.apply_translation(pos);return m
def rock_col(rg,x,y,k):
    v=0.55*math.sin(0.33*x+1.3)*math.cos(0.41*y+0.4)+rg.uniform(-0.45,0.45)
    return 'RockDk' if v<-0.42 else ('RockLt' if v>0.46 else 'Rock')
def rcourse(P,rg,x0,x1,y0,h,cz,depth,wmin,wmax,row,hj=0.08):
    x=x0;k=0;prev=[]
    while x<x1-0.2:
        w=min(rg.uniform(wmin,wmax),x1-x)
        if x1-(x+w)<1.6: w=x1-x
        hh=h*rg.uniform(1-hj,1+hj);col=rock_col(rg,x+w/2,y0,k)
        if len(prev)>=2 and prev[-1]!=prev[-2] and col==prev[-2]: col='Rock' if col!='Rock' else prev[-1]   # no ABAB checker
        prev.append(col)
        m=rstone(w+0.35,hh+0.18,depth*rg.uniform(0.92,1.04),b=rg.uniform(0.2,0.34),seed=row*40+k)
        m=place(m,(x+w/2+rg.uniform(-0.12,0.12),y0+(hh+0.18)/2-0.12+rg.uniform(-0.1,0.1),cz+rg.uniform(-0.18,0.18)),rx=rg.uniform(-1.6,1.6),ry=rg.uniform(-4.5,4.5),rz=rg.uniform(-2.8,2.8))
        P.add(m,col,True);x+=w;k+=1
def mosscap(P,rg,pos,rx,rz,ry,seed):
    cols=['LeafLt','LeafGreen','LeafLt']
    for q in range(3):
        a=rg.uniform(0,6.28);off=(math.cos(a)*rx*0.35*(q>0),0.05*q,math.sin(a)*rz*0.35*(q>0));s=1.0 if q==0 else rg.uniform(0.5,0.7)
        m=dome(rx*s,ry*s*1.35,rz*s,(0,0,0),10,3);jitter(m,(0,0,0),0.16,seed+q);put(P,m,cols[q],(pos[0]+off[0],pos[1]+off[1]-0.15*q+0.0,pos[2]+off[2]),yaw=rg.uniform(0,360))
        P.items[-1]=(P.items[-1][0],P.items[-1][1],True)
def ruin_wall():
    rg=np.random.default_rng(603);P=newp('kit_ruin_wall','bbox','Separate broken wall chunk (about 20 wide, 16 tall) with a window gap, stepped broken top, moss caps; scatter along the jungle trail or beside the arch. v2_6: stylised rounded/bevelled stones.')
    D=4.2;H=[3.1,2.9,3.1,2.9,3.0,2.8]
    rows=[(-10,10),(-10,10),(-10,10),(-10,5.5),(-10,-1.5),(-10,-6.5)]
    y=0.0
    for r,(xa,xb) in enumerate(rows):
        h=H[r]
        segs=[(xa,1.2),(5.0,xb)] if r in(1,2) else [(xa,xb)]
        for si,(a,b_) in enumerate(segs):   # dark core behind the stones: crevices read as shadow, no see-through
            P.add(place(rstone(b_-a-0.7,h*0.9,D-1.3,b=0.15,seed=900+r*3+si,noise=0.02),((a+b_)/2,y+h*0.5,0)),'RockDk',True)
            rcourse(P,rg,a,b_,y,h,0,D,2.2,3.9,r*2+si)
        y+=h
    # window sill + lintel (bigger, lighter), buttress (two stacked stones)
    P.add(place(rstone(4.9,1.0,D*1.12,b=0.3,seed=71),(3.1,3.2,0.25),ry=-3,rz=1.0),'RockLt',True)
    P.add(place(rstone(2.3,3.2,D*1.45,b=0.3,seed=72),(-10.9,1.55,0),ry=4,rz=-1.5),'RockDk',True)
    P.add(place(rstone(2.1,2.3,D*1.35,b=0.32,seed=73),(-10.8,4.25,0.1),ry=-6,rz=2.5),'Rock',True)
    # rubble: rounded chunks + three tilted slabs
    for k in range(8):
        r=rg.uniform(0.8,1.8);m=rstone(r*2*rg.uniform(0.9,1.3),r*2*rg.uniform(0.6,0.95),r*2*rg.uniform(0.85,1.2),b=rg.uniform(0.38,0.5),seed=500+k,noise=0.1)
        P.add(place(m,(rg.uniform(6.0,12.3),r*0.55,rg.uniform(-3.4,4.5)),ry=rg.uniform(0,360),rx=rg.uniform(-12,12),rz=rg.uniform(-12,12)),ROCKS[(k+1)%3] if k%4 else 'Rock',True)
    for k,(x,z,yw) in enumerate(((7.5,3.4,25),(10.5,-1.0,-35),(4.0,4.4,70))):
        m=rstone(rg.uniform(2.6,3.6),1.3,rg.uniform(2.0,2.8),b=0.42,seed=600+k)
        P.add(place(m,(x,0.9+0.2*k,z),ry=yw,rz=rg.uniform(-12,12),rx=rg.uniform(-6,6)),ROCKS[(k+2)%3],True)
    # moss caps on the stepped tops (light moss like the boulder/cliff kit) + a few tufts spilling over the front edge
    mosscap(P,rg,(-8.0,sum(H[:6])-0.05,0),3.7,2.9,1.0,11);mosscap(P,rg,(-3.5,sum(H[:5])-0.05,0.2),3.1,2.9,0.9,21)
    mosscap(P,rg,(2.0,sum(H[:4])-0.05,0),3.3,2.8,0.9,31);mosscap(P,rg,(8.5,sum(H[:3])-0.05,0),3.4,2.8,0.9,41)
    for k,(x,yy) in enumerate(((-6.6,sum(H[:6])-0.2),(-1.0,sum(H[:5])-0.2),(4.3,sum(H[:4])-0.2))):
        m=dome(1.2,0.5,0.9,(0,0,0),8,2);jitter(m,(0,0,0),0.15,50+k);put(P,m,'LeafLt',(x,yy,D/2+0.1),yaw=rg.uniform(0,360));P.items[-1]=(P.items[-1][0],P.items[-1][1],True)
    for k,x in enumerate((-9.2,-5.0)):
        vine(P,V3(x,sum(H[:6])+0.2 if k==0 else sum(H[:5])+0.2,D/2+0.3),rg.uniform(5,8.5),90+k,leaves=3)
    tuft(P,(-4.0,0.3,3.6),6,3.0,15,('FernLt','Fern'),0.7);tuft(P,(5.0,0.3,3.8),5,2.6,16,('Fern','FernDk'),0.7);tuft(P,(-9.5,0.3,-3.0),5,2.6,17,('Fern','FernDk'),0.7)
    scaleP(P,0.88);settle(P,'bbox')
    # fit to the v2 ruin_wall footprint: bbox size 23.09 x 16.56 x 11.09 (per-axis, must stay within 5%)
    mn,mx=bounds(P);tgt=np.array([23.09,16.56,11.09]);k=tgt/(mx-mn);print('fit factors',k)
    assert (abs(k-1)<0.05).all(),k
    for i,(m,c,sm) in enumerate(P.items): m=m.copy();m.vertices=m.vertices*k;P.items[i]=(m,c,sm)
    settle(P,'bbox')
ruin_wall()
# ====================================================================== EXPORT
os.makedirs(os.path.join(OUT,'geom'),exist_ok=True);report={}
for k,p in props.items():
    g=p.merged();V=np.array(g['verts']);g['verts']=np.round(V,4).tolist()
    objs=[dict(name=k,mat='main',verts=g['verts'],tris=g['tris'],uvs=g['uvs'],smooth=g['smooth'])]
    json.dump({k:dict(objects=objs,empties=[])},open(os.path.join(OUT,'geom',k+'.json'),'w'))
    report[k]=dict(tris=len(g['tris']),bbox=dict(min=np.round(V.min(0),2).tolist(),max=np.round(V.max(0),2).tolist()),size=np.round(V.max(0)-V.min(0),2).tolist())
    print(k,report[k])
json.dump(report,open(os.path.join(OUT,'box_report.json'),'w'),indent=1)
palette_png(os.path.join(OUT,'kit_palette.png'));json.dump(PAL,open(os.path.join(OUT,'palette.json'),'w'))
import collections;print(collections.Counter(c for _,c,_ in props['kit_ruin_wall'].items))
