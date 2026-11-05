# Pirate Shipwreck hero GAG PROPS v1 generator (Look B). Run: /workspace/.geo/bin/python gen_props.py <outdir>
# Roblox frame: +Y up, FRONT = +Z, studs. Each prop: base-centre origin at ground (min y = 0, bbox centre x/z = 0). One merged mesh per FBX, palette-texture colour.
import sys,os,json,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from props_lib import *
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
rng=np.random.default_rng(2026)
V3=lambda *a:np.array(a,float)
def lathe(prof,sec=10,rot0=0.0):
    """revolve [(r,y),...] about the y axis -> closed solid (tiny radius instead of 0)"""
    rings=[]
    for r,y in prof:
        r=max(r,0.04);rings.append([(r*math.cos(2*math.pi*k/sec+rot0),y,r*math.sin(2*math.pi*k/sec+rot0)) for k in range(sec)])
    return ring_solid(rings)
def orient_y(m,d,at=(0,0,0)):
    """rotate a y-axis solid so +y points along d, then translate"""
    d=np.array(d,float);d/=np.linalg.norm(d);R=align_vectors([0,1,0],d);m=m.copy();m.apply_transform(R);m.apply_translation(at);return m
def ell(r,c=(0,0,0),lon=10,lat=6): return uvsphere(r,c,lon,lat)
def dome(rx,ry,rz,c=(0,0,0),lon=10,lat=4,up=True):
    th=np.linspace(0.05,math.pi/2,lat+1);rings=[]
    for t in th:
        y=ry*math.cos(t)*(1 if up else -1);rr=math.sin(t)
        rings.append([(rx*rr*math.cos(2*math.pi*k/lon),y,rz*rr*math.sin(2*math.pi*k/lon)) for k in range(lon)])
    if not up: rings=rings[::-1]
    m=ring_solid(rings);m.apply_translation(c);return m
def bez(p0,c,p1,n):
    p0,c,p1=map(lambda a:np.array(a,float),(p0,c,p1));return [(1-s)**2*p0+2*s*(1-s)*c+s*s*p1 for s in np.linspace(0,1,n)]
def blade(p0,c,p1,w,t,n=7):
    """leaf blade: lens/diamond cross-section loft along a quadratic curve"""
    pts=bez(p0,c,p1,n);rings=[]
    for i,p in enumerate(pts):
        s=i/(n-1);T=pts[min(i+1,n-1)]-pts[max(i-1,0)];T/=np.linalg.norm(T)
        side=np.cross(T,(0,1,0))
        if np.linalg.norm(side)<1e-3: side=np.array([1.0,0,0])
        side/=np.linalg.norm(side);nr=np.cross(side,T)
        ww=max(w*(math.sin(math.pi*min(1.0,0.12+0.88*s))**0.75),0.06);tt=max(t*(1-0.6*s),0.05)
        rings.append([p+side*ww,p+nr*tt,p-side*ww,p-nr*tt])
    return ring_solid(rings)
def bone(p0,p1,r,P,col='Bone',knob=True):
    P.add(frustum(r,r,p0,p1,6),col)
    if knob:
        for p in (p0,p1): P.add(ell(r*1.55,p,6,4),col)
def hat(P,c=(0,0,0),size=1.0,yaw=0,pitch=0,roll=0,band='Brass',body='HatDark'):
    """plain tricorn pirate hat (NO emblem). radius 3.2*size"""
    q=Part('h')
    q.add(lathe([(0.05,0),(3.0,0),(3.0,0.35),(0.05,0.35)],12),body)
    for k in range(3):
        a=90+120*k;m=box(2.4,0.32,2.7,(0,0.0,0));m.apply_transform(Rm((1,0,0),-48));m.apply_translation((0,0.95,2.55));m.apply_transform(Rm((0,1,0),a));q.add(m,'HatDarkLt' if k==1 else body)
    q.add(frustum(2.1,1.85,(0,0.2,0),(0,1.8,0),10),body)
    q.add(lathe([(0.05,1.8),(1.85,1.8),(1.85,2.0),(0.05,2.0)],10),'HatDarkLt')
    q.add(frustum(2.2,2.05,(0,0.5,0),(0,1.1,0),10),band)
    M=Tm(c)@Rm((0,1,0),yaw)@Rm((1,0,0),pitch)@Rm((0,0,1),roll)@np.diag([size,size,size,1.0])
    for m,col,sm in q.items: P.add(xf(m,M),col)
def skull(P,c,R,s=1.0,asleep=False,col='Bone'):
    q=Part('s')
    q.add(ell((1.5,1.45,1.5),(0,0.2,0),10,6),col)
    q.add(box(1.9,0.8,1.9,(0,-1.3,0.3)),'BoneDk')
    for i in range(4): q.add(box(0.36,0.5,0.2,(-0.66+0.44*i,-1.5,1.3)),'Tooth')
    if asleep:
        for sx in(-1,1): q.add(box(0.8,0.2,0.2,(sx*0.62,0.28,1.42),((0,0,1),-sx*12)),'Black')
    else:
        for sx in(-1,1): q.add(ell((0.42,0.5,0.25),(sx*0.62,0.3,1.3),6,4),'Black')
    q.add(box(0.3,0.4,0.2,(0,-0.3,1.44)),'Black')
    M=Tm(c)@R@np.diag([s,s,s,1.0])
    for m,cc,sm in q.items: P.add(xf(m,M),cc)
def boot(P,base,d,fwd,s=1.0):
    """boot whose shaft top is at `base`, shaft pointing along d (up the leg), foot toward fwd"""
    d=np.array(d,float);d/=np.linalg.norm(d);fwd=np.array(fwd,float);fwd-=d*np.dot(fwd,d);fwd/=np.linalg.norm(fwd)
    side=np.cross(d,fwd);R=np.eye(4);R[:3,0]=side;R[:3,1]=d;R[:3,2]=fwd
    q=Part('b')
    q.add(frustum(1.15,1.0,(0,-0.1,0),(0,-2.0,0),8),'BootBrown')
    q.add(box(1.9,1.3,3.4,(0,-2.5,0.8)),'BootBrown')
    q.add(box(2.0,0.45,3.6,(0,-3.35,0.85)),'BootSole')
    q.add(box(2.1,0.4,0.75,(0,-0.1,0)),'BootSole')    # turned cuff band
    M=Tm(base)@R@np.diag([s,s,s,1.0])
    for m,cc,sm in q.items: P.add(xf(m,M),cc)
def recentre(P,keep=None):
    """shift so min y=0 and bbox centre x/z=0; returns shift"""
    V=np.concatenate([m.vertices for m,_,_ in P.items]);mn,mx=V.min(0),V.max(0);sh=np.array([-(mn[0]+mx[0])/2,-mn[1],-(mn[2]+mx[2])/2])
    for i,(m,c,sm) in enumerate(P.items): m=m.copy();m.apply_translation(sh);P.items[i]=(m,c,sm)
    return sh
props={}
# =============================================================== 1. BACKWARD CANNON (muzzle +Z = front, points back at the ship)
P=Part('prop_cannon');props['prop_cannon']=P
PIT=6.0;d=V3(0,math.sin(math.radians(PIT)),math.cos(math.radians(PIT)));B0=V3(0,3.3,-3.6)
prof=[(0.3,-1.95),(0.7,-1.8),(0.85,-1.35),(0.5,-0.95),(0.55,-0.7),(1.55,-0.55),(1.72,0.1),(1.62,1.0),(1.48,2.6),(1.35,4.8),(1.2,7.0),(1.1,8.8),(1.12,9.7),(1.32,10.0),(1.34,10.9),(0.72,11.0)]
P.add(orient_y(lathe(prof,14),d,B0),'Bronze')
for a0,a1,rr in((0.25,0.7,1.78),(5.0,5.45,1.4),(9.7,10.1,1.36)):
    P.add(orient_y(frustum(rr,rr,(0,a0,0),(0,a1,0),14),d,B0),'BronzeLt')
P.add(orient_y(frustum(0.8,0.8,(0,10.9,0),(0,11.18,0),12),d,B0),'Black')       # bore
for sx in(-1,1):
    P.add(beam((sx*2.2,1.0,-5.7),(sx*2.2,2.9,3.9),0.9,2.0),'Plank')                # cheek planks (outside barrel radius)
    ax=B0+d*3.9;P.add(frustum(0.55,0.55,(sx*1.5,ax[1],ax[2]),(sx*3.0,ax[1],ax[2]),8),'BronzeDk')   # trunnions
    x=sx*3.6;P.add(frustum(2.4,2.4,(x-0.45,2.4,1.4),(x+0.45,2.4,1.4),14),'DarkWood')    # wheel rim
    P.add(frustum(1.85,1.85,(x-0.55,2.4,1.4),(x+0.55,2.4,1.4),14),'PlankDk')           # wheel face
    for k in range(3): m=box(1.3,0.5,3.6,(x,2.4,1.4),((1,0,0),60*k));P.add(m,'DarkWood')  # spokes
    P.add(frustum(0.85,0.85,(x-0.75,2.4,1.4),(x+0.75,2.4,1.4),8),'Bronze')              # hub
P.add(frustum(0.5,0.5,(-3.8,2.4,1.4),(3.8,2.4,1.4),8),'DarkWood')                       # axle
P.add(box(4.0,1.3,1.1,(0,1.1,-4.6)),'PlankDk')                                          # rear cross-beam
for (z,y,x) in[(-0.3,0.7,6.7),(1.15,0.7,6.7),(2.6,0.7,6.7),(0.43,1.95,6.7),(1.88,1.95,6.7),(1.15,3.2,6.7)]:
    P.add(ell(0.72,(x,y,z),8,5),'Iron')                                                   # 6 cannonballs (3+2+1 stack)
P.add(frustum(0.24,0.24,(-6.5,0.26,-4.2),(-6.5,0.26,5.0),6),'Plank');P.add(frustum(0.55,0.55,(-6.5,0.55,5.0),(-6.5,0.55,6.3),8),'HatDark')   # ramrod
hat(P,(5.6,0.0,6.4),0.9,yaw=35,pitch=6,roll=14)                                         # blown-off plain hat
m=lathe([(0.05,0.0),(2.3,0.0),(2.3,0.2),(0.05,0.2)],12);mz=B0+d*11.0;m.apply_translation((mz[0],0,mz[2]+2.0));P.add(m,'MudDk')   # scorch mark in front of the muzzle
for i,(m,c,sm) in enumerate(P.items): P.items[i]=(xf(m,np.diag([1.5,1.5,1.5,1.0])),c,sm)   # v1.1: whole prop x1.5
recentre(P)
# =============================================================== 2. COCONUT CASUALTY (palm + flat skeleton + coconut + plain hat)
P=Part('prop_coconut');props['prop_coconut']=P
base=V3(-4.5,0,-3.8);top=V3(0.3,50.4,-2.6)
def trunk_pt(s): return base+(top-base)*V3(s**1.9,s,s**1.2)+V3(0,0,1.8*math.sin(math.pi*s))
pts=[trunk_pt(s) for s in np.linspace(0,1,14)]
P.add(tube(pts,1.9,8,0.95),'Trunk')
P.add(frustum(2.9,1.9,(base[0],0,base[2]),(base[0],2.2,base[2]),8),'Trunk')
for k in range(1,16):
    s=k/16;p=trunk_pt(s);T=trunk_pt(min(s+.02,1))-trunk_pt(max(s-.02,0));T/=np.linalg.norm(T);r=1.9-0.95*s+0.28
    P.add(frustum(r,r,p-T*0.4,p+T*0.4,8),'TrunkDk')
for i in range(9):
    a=math.radians(i*40+rng.uniform(-8,8));dd=V3(math.cos(a),0,math.sin(a));L=10.8 if i%2==0 else 9.2
    P.add(blade(top+V3(0,0.4,0),top+dd*(L*0.5)+V3(0,5.2,0),top+dd*L+V3(0,-4.6+rng.uniform(-1,1),0),1.75,0.3),['PalmGreen','PalmGreenDk','PalmGreenLt'][i%3])
for i in range(4):
    a=math.radians(i*90+30);dd=V3(math.cos(a),0,math.sin(a))
    P.add(blade(top+V3(0,0.6,0),top+dd*1.6+V3(0,3.2,0),top+dd*4.2+V3(0,4.6,0),1.3,0.28,6),'PalmGreenLt')
for dx,dy,dz in((-1.5,-1.4,1.2),(1.4,-1.5,1.3),(0.1,-1.6,-1.7),(0.0,-0.6,0.2)): P.add(ell((1.2,1.3,1.2),top+V3(dx,dy,dz),8,5),'Coconut')
SX=4.2   # skeleton lies along z, face up, head toward +Z (front)
N0=len(P.items)
Rup=Rm((1,0,0),-90)
skull(P,(SX,1.55,5.2),Rup,1.0,asleep=True)
P.add(ell((2.3,1.2,2.2),(SX,1.25,1.4),10,6),'BoneDk')
for z in(0.4,1.1,1.8,2.5): P.add(box(2.6,0.34,0.38,(SX,2.3,z)),'Bone')
P.add(ell((1.9,0.8,1.3),(SX,0.9,-1.6),8,5),'BoneDk')
bone((SX,1.0,2.9),(SX,0.9,4.1),0.28,P,'Bone',False)
for sx in(-1,1):
    bone((SX+sx*1.9,1.0,2.7),(SX+sx*4.5,0.7,2.0),0.3,P);bone((SX+sx*4.5,0.7,2.0),(SX+sx*6.6,0.6,3.4),0.28,P);P.add(ell((0.55,0.3,0.7),(SX+sx*6.9,0.45,3.7),6,4),'Bone')
    bone((SX+sx*0.9,0.9,-2.0),(SX+sx*1.2,0.65,-4.6),0.34,P);bone((SX+sx*1.2,0.65,-4.6),(SX+sx*1.0,0.6,-6.9),0.3,P);P.add(box(1.2,0.55,1.5,(SX+sx*1.0,0.45,-7.5)),'Bone')
# v1.1: skeleton x1.5 about (SX,0,0), then shifted toward the palm so the footprint stays tight
SKM=Tm((-3.0,0,0))@Tm((SX,0,0))@np.diag([1.5,1.5,1.5,1.0])@Tm((-SX,0,0))
for i in range(N0,len(P.items)): m,c,sm=P.items[i];P.items[i]=(xf(m,SKM),c,sm)
KX=SX-3.0;KZ=5.2*1.5;KY=1.55*1.5
# big dented coconut resting on the skull (+ a small cartoon star painted on its front)
CR=2.9;cc=V3(KX,KY+1.6+CR-0.7,KZ-0.2)
cm=uvsphere(CR,(0,0,0),16,11);V=cm.vertices.copy()
n1=V3(0.55,0.80,0.25);n1/=np.linalg.norm(n1)
for k in range(len(V)):
    u=V[k]/np.linalg.norm(V[k]);ang=math.acos(max(-1,min(1,float(u@n1))));V[k]=V[k]*(1-0.36*math.exp(-(ang/0.5)**2))
cm.vertices=V+cc;P.add(cm,'Coconut')
n2=V3(0.28,-0.05,0.96);n2/=np.linalg.norm(n2)
def star(R0,R1,t,col):
    pts=[]
    for k in range(10):
        r=R0 if k%2==0 else R1;a=math.pi/2+k*math.pi/5;pts.append((r*math.cos(a),r*math.sin(a)))
    Vv=[(0,0,t/2)]+[(x,y,t/2) for x,y in pts]+[(0,0,-t/2)]+[(x,y,-t/2) for x,y in pts];F=[]
    for k in range(10):
        a=1+k;b=1+(k+1)%10;F+=[[0,a,b],[11,11+b,11+a],[a,11+a,11+b],[a,11+b,b]]
    m=trimesh.Trimesh(np.array(Vv),F,process=False);m.fix_normals();return m
st=star(1.15,0.5,0.45,'GoldLt');st.apply_transform(align_vectors([0,0,1],n2));st.apply_translation(cc+n2*(CR*0.93))
P.add(st,'GoldLt')
hat(P,(KX+7.2,0.15,KZ+3.6),0.95,yaw=-30,pitch=4,roll=-8)     # plain hat on the ground beside the skull
for (x,z,r) in((-6.8,0.5,1.5),(-1.5,-7.0,1.1)): P.add(dome(r*1.4,r,r*1.2,(x,0,z),8,3),'Rock')
recentre(P)
# =============================================================== 3. FLYTRAP BURP (boots sticking out of the mouth, +Z)
P=Part('prop_flytrap');props['prop_flytrap']=P
P.add(tube([V3(0,0,-3),V3(0,6,-4.2),V3(0,12,-4.0),V3(0,17.5,-2.2)],2.3,8,1.7),'PlantGreen')
P.add(frustum(3.4,2.3,(0,0,-3),(0,1.8,-3),8),'PlantGreenDk')
HY=V3(0,18.0,-2.6)
lower=dome(6.4,3.8,7.0,V3(0,0,3.5),12,4,up=False);P.add(xf(lower,Tm(HY)),'PlantGreen')
lc=lathe([(0.05,0.0),(5.9,0.0),(5.9,0.12),(0.05,0.12)],12);lc.apply_transform(np.diag([1,1,1.15,1.0]));P.add(xf(lc,Tm(HY+V3(0,0.12,3.5))),'JawRed')
JR=Rm((1,0,0),-36)
upper=dome(6.4,3.8,7.0,V3(0,0,3.5),12,4,up=True);P.add(xf(upper,Tm(HY)@JR),'PlantGreenLt')
uc=lathe([(0.05,0.0),(5.9,0.0),(5.9,0.12),(0.05,0.12)],12);uc.apply_transform(np.diag([1,1,1.15,1.0]));P.add(xf(uc,Tm(HY)@JR@Tm((0,-0.24,3.5))),'JawRedDk')
for i,t in enumerate(np.linspace(-115,115,9)):
    a=math.radians(t);x=5.7*math.sin(a);z=3.5+6.3*math.cos(a)
    tooth=frustum(0.5,0.05,(x,0.1,z),(x*0.97,1.7,z),5)
    P.add(xf(tooth,Tm(HY)),'Tooth')
    a2=math.radians(t+12.8);x2=5.7*math.sin(a2);z2=3.5+6.3*math.cos(a2)
    tt=frustum(0.5,0.05,(x2,-0.1,z2),(x2*0.97,-1.7,z2),5);P.add(xf(tt,Tm(HY)@JR),'Tooth')
for sx in(-1,1):
    for (px,pz,rr,col) in((sx*2.9,3.6,1.15,'EyeWhite'),):
        n=V3(px/6.4**2,0,0);pc=V3(px,0,pz-3.5);y=3.8*math.sqrt(max(1-(px/6.4)**2-((pz-3.5)/7)**2,0.05))
        e=V3(px,y,pz)+V3(0,0.15,0.25);P.add(xf(ell(rr,e,8,5),Tm(HY)@JR),'EyeWhite');P.add(xf(ell(0.55,e+V3(0,0.35,0.85),6,4),Tm(HY)@JR),'Black')
# legs: striped socks, boots at the ends, poking out of the mouth and kicking
for sx,(p0,d_,fw,L) in{-1:(V3(-1.7,19.0,4.0),V3(-0.18,1.0,0.55),V3(-0.3,0.2,1),8.5),1:(V3(2.0,19.0,4.4),V3(0.30,0.9,0.75),V3(0.5,0.1,1),7.6)}.items():
    d_=d_/np.linalg.norm(d_);p1=p0+d_*L
    P.add(frustum(0.82,0.82,p0,p1,8),'SockCream')
    for k in range(3):
        a=p0+d_*(0.9+k*2.5);b=a+d_*1.3;P.add(frustum(0.93,0.93,a,b,8),'SockRed')
    boot(P,p1+d_*0.3,-d_,fw,0.95)
hat(P,(7.4,0.0,9.2),1.0,yaw=-25,pitch=5,roll=10)
for k in range(6):
    a=math.radians(k*60+20+rng.uniform(-8,8));dd=V3(math.cos(a),0,math.sin(a))
    P.add(blade(V3(0,1.0,-3)+dd*1.4,V3(0,1.0,-3)+dd*5.0+V3(0,4.2,0),V3(0,1.0,-3)+dd*10.2+V3(0,-0.2,0),2.0,0.3,7),['PlantGreenDk','PlantGreen','PlantGreenLt'][k%3])
for (x,z,r) in((-6.5,5.5,1.6),(-8.0,3.2,1.1),(5.0,-7.2,1.3)): P.add(dome(r*1.4,r,r*1.2,(x,0,z),8,3),'Rock')
recentre(P)
# =============================================================== 4. CROC NAP (head +Z)
P=Part('prop_croc');props['prop_croc']=P
def cz_prof(z):
    # (centre x, half width, half height) along z (-20 tail tip .. +20 snout tip)
    ks=[(-20,0.3,0.25),(-16,0.9,0.7),(-11,2.0,1.4),(-6,3.9,2.6),(-1,5.6,3.2),(5,5.7,3.1),(9,4.7,3.0),(12,5.0,3.6),(15,3.7,2.4),(18,3.1,1.9),(20,1.4,1.1)]
    zs=[k[0] for k in ks];w=float(np.interp(z,zs,[k[1] for k in ks]));h=float(np.interp(z,zs,[k[2] for k in ks]))
    xo=5.5*math.sin(math.pi*min(1,max(0,(-z-2)/20))*0.9)*(1 if z<-2 else 0)
    return xo,w,h
rings=[]
zs=[-20,-17.5,-15,-12,-9,-6,-3,0,3,6,8.5,10.5,12.5,14.5,16.5,18.5,19.7,20]
for z in zs:
    xo,w,h=cz_prof(z);rings.append([(xo+w*math.cos(2*math.pi*k/12+math.pi/12),h+h*math.sin(2*math.pi*k/12+math.pi/12),z) for k in range(12)])
P.add(ring_solid(rings),'CrocGreen')
# pale belly strip peeking at the throat/snout underside (below the lip line) and lip line
for z0,z1 in((10.0,19.2),):
    for sx in(-1,1):
        xa,wa,ha=cz_prof(z0);xb,wb,hb=cz_prof(z1)
        P.add(beam((sx*(wa+0.06),ha*0.78,z0),(sx*(wb+0.06),hb*0.78,z1),0.22,0.45,up=(0,1,0)),'CrocBelly')   # lip stripe
for k in range(6):
    z=11.4+k*1.4;xo,w,h=cz_prof(z)
    for sx in(-1,1): P.add(frustum(0.28,0.04,(sx*(w+0.02),h*0.78,z),(sx*(w+0.02),h*0.78-0.9,z),4),'Tooth')
for z in np.arange(-17,10,2.4):
    xo,w,h=cz_prof(z);P.add(frustum(0.9,0.05,(xo,2*h-0.35,z),(xo,2*h+1.1,z),4),'CrocDk')
for sx in(-1,1):
    xo,w,h=cz_prof(19.7);P.add(ell((0.42,0.3,0.4),(sx*0.75,2*h+0.05,19.1),5,4),'Black')
    for z in(5.5,-8.0):
        xo,w,h=cz_prof(z);foot=V3(xo+sx*(w+2.2),0,z+1.0)
        P.add(frustum(1.7,1.25,(xo+sx*(w-0.9),h*1.0,z),(foot[0],0.7,foot[2]),6),'CrocGreen')
        for q in(-1,0,1): P.add(box(0.7,0.55,1.6,(foot[0]+sx*0.35,0.28,foot[2]+1.4+0.0),((0,1,0),q*18)),'CrocLt')
hat(P,(0.0,6.6,12.0),1.45,yaw=0,pitch=-14,roll=6,band='Brass')       # captain's plain hat tipped over the eyes
# cutlass lying beside
P.add(box(0.8,0.25,7.0,(10.6,0.3,3.4),((0,1,0),-4)),'Steel');P.add(box(0.8,0.25,2.5,(10.3,0.3,-1.6)),'Steel')
P.add(box(2.4,0.35,0.4,(10.45,0.35,-3.1)),'Brass');P.add(box(0.5,0.45,1.9,(10.45,0.35,-4.3)),'DarkWood')
m=dome(13.5,0.5,20.0,(0,0,0),16,3);P.add(m,'Mud')
for (x,z,r) in((11.5,10,1.4),(-11,9,1.2),(-9,-14,1.4),(8.5,-12,1.0)): P.add(dome(r*1.2,r*0.6,r*1.2,(x,0.0,z),8,3),'MudLt')
recentre(P)
# =============================================================== 5. CAPTAIN'S LAST NAP (skeleton captain on his gold, bone throne)
P=Part('prop_captain');props['prop_captain']=P
TZ=-5.0
# gold heap
P.add(dome(11.5,5.6,10.5,(0,0,3.0),16,5),'GoldDk')
for (x,y,z,rx,ry,rz,c) in[(-6.5,0,6,5.0,3.2,4.5,'Gold'),(6.0,0,7.5,4.6,3.0,4.2,'GoldDk'),(0,0,10.5,5.2,2.6,3.5,'Gold'),(-8,0,-2.5,4.2,3.4,4.8,'GoldDk'),(8.5,0,-3,4.0,3.2,4.4,'Gold')]:
    P.add(dome(rx,ry,rz,(x,y,z),10,4),c)
for i in range(46):
    a=rng.uniform(0,2*math.pi);rr=rng.uniform(0.15,0.95);x=rr*11*math.cos(a);z=3.0+rr*10*math.sin(a)
    if abs(x)<4.0 and z<0: continue
    y=5.6*math.sqrt(max(1-(x/11.5)**2-((z-3)/10.5)**2,0.02))
    m=frustum(1.0,1.0,(0,-0.14,0),(0,0.14,0),8);m=xf(m,Rm((1,0,0),rng.uniform(-35,35)),Rm((0,0,1),rng.uniform(-35,35)),Tm((x,y-0.05,z)))
    P.add(m,['GoldLt','Gold','GoldLt'][i%3])
for (x,z,c) in((-3.5,7.5,'GemBlue'),(4.5,9,'GemRed'),(2.0,5.4,'GemBlue'),(-7.5,9.5,'GemRed'),(8.5,3.8,'GemBlue')):
    y=5.6*math.sqrt(max(1-(x/11.5)**2-((z-3)/10.5)**2,0.02));P.add(ell(0.62,(x,y+0.35,z),5,3),c)
# treasure chest, lid open, spilling coins
cx,cz=9.0,8.5
P.add(box(5.2,2.6,3.4,(cx,2.55,cz),((0,1,0),-18)),'Plank')
for sx in(-1.6,1.6): P.add(box(0.5,2.7,3.5,(cx+sx*math.cos(math.radians(-18)),2.6,cz-sx*math.sin(math.radians(-18))*-1),((0,1,0),-18)),'Brass')
P.add(frustum(1.75,1.75,(cx-2.6*math.cos(0.31),4.35,cz),(cx+2.6*math.cos(0.31),4.35,cz),8),'PlankDk')
# bone throne
for sx in(-1,1):
    bone((sx*5.2,2.5,TZ-1.6),(sx*5.2,25.5,TZ-1.6),0.95,P)
    bone((sx*5.2,10.0,TZ-1.6),(sx*5.2,10.0,TZ+3.0),0.55,P)          # arm rests
    P.add(ell(0.95,(sx*5.2,10.0,TZ+3.4),6,4),'Bone')
for y in(13.2,16.8,20.4,23.6):
    P.add(frustum(0.5,0.5,(-5.2,y,TZ-1.9),(5.2,y,TZ-1.9),6),'BoneDk')  # rib bars
P.add(box(9.4,1.5,8.0,(0,5.6,TZ+0.8)),'Bone')
P.add(box(9.9,0.6,8.4,(0,4.7,TZ+0.8)),'BoneShade')
P.add(ell((1.4,1.5,1.4),(-5.2,26.4,TZ-1.6),8,5),'Bone');P.add(ell((1.4,1.5,1.4),(5.2,26.4,TZ-1.6),8,5),'Bone')
# skeleton captain, asleep, head drooping
pelv=V3(0,7.4,TZ-0.2);neck=V3(0,15.2,TZ-1.5)
torso=ring_solid([[(-3.5,0,-1.7),(3.5,0,-1.7),(3.5,0,1.7),(-3.5,0,1.7)],[(-3.8,2.4,-1.9),(3.8,2.4,-1.9),(3.8,2.4,1.9),(-3.8,2.4,1.9)],[(-4.2,5.0,-1.9),(4.2,5.0,-1.9),(4.2,5.0,1.9),(-4.2,5.0,1.9)],[(-4.3,7.6,-1.8),(4.3,7.6,-1.8),(4.3,7.6,1.5),(-4.3,7.6,1.5)]])
# reorder quads so rings are closed loops (cw/ccw consistent)
P.add(xf(torso,Tm((0,7.7,TZ-0.9))),'CoatRed')
P.add(box(7.6,0.55,3.7,(0,7.6,TZ+0.1)),'DarkWood');P.add(box(1.3,0.8,0.3,(0,7.6,TZ+2.1)),'Brass')    # belt + buckle
for i in range(3): P.add(ell(0.28,(0,9.6+i*1.6,TZ+1.85),5,3),'Brass')                                # coat buttons
P.add(box(2.4,0.9,2.2,(0,15.3,TZ-0.9)),'CoatRedDk')                                                    # collar
skull(P,(0,17.4,TZ+0.8),Rm((1,0,0),28),1.55,asleep=True)
hat(P,(0,19.4,TZ+0.5),1.05,yaw=0,pitch=26,roll=0,band='Brass')                                        # plain captain's hat tilted over the eyes
for sx in(-1,1):
    sh_=V3(sx*4.6,13.4,TZ-0.9);el=V3(sx*5.4,10.2,TZ+0.6);ha=V3(sx*1.5,9.4,TZ+2.6)
    P.add(frustum(1.0,0.9,sh_,el,8),'CoatRed');P.add(ell(1.15,sh_,8,5),'CoatRedDk');P.add(frustum(0.9,0.85,el,ha,8),'CoatRed');P.add(ell(0.85,ha,6,4),'Bone')
    th=V3(sx*1.9,7.2,TZ+0.4);kn=V3(sx*2.0,7.8,TZ+5.8);an=V3(sx*2.1,3.4,TZ+7.4)
    P.add(frustum(1.05,0.95,th,kn,8),'Black');P.add(frustum(0.85,0.75,kn,an,8),'Black');P.add(ell(1.0,kn,6,4),'Black')
    boot(P,an+V3(0,0.4,0),(0,1,-0.1),(0,0.15,1),1.05)
# parrot on the right throne post
pp=V3(5.2,28.4,TZ-1.6)
P.add(ell((1.3,1.7,1.2),pp+V3(0,0.4,0),8,5),'CoatRed');P.add(ell(0.85,pp+V3(0,2.4,0.4),7,4),'CoatRed');P.add(frustum(0.45,0.08,pp+V3(0,2.4,1.1),pp+V3(0,2.1,2.0),5),'Beak')
for sx in(-1,1): P.add(ell(0.2,pp+V3(sx*0.5,2.6,1.0),4,3),'Black')
P.add(box(0.9,0.3,2.6,pp+V3(0,-1.0,-1.6),((1,0,0),-25)),'GemBlue')
recentre(P)
# =============================================================== export
os.makedirs(os.path.join(OUT,'geom'),exist_ok=True);report={}
for k,p in props.items():
    g=p.merged();V=np.array(g['verts']);g['verts']=np.round(V,4).tolist()
    json.dump({k:dict(objects=[dict(name=k,verts=g['verts'],tris=g['tris'],uvs=g['uvs'],smooth=g['smooth'])])},open(os.path.join(OUT,'geom',k+'.json'),'w'))
    report[k]=dict(tris=len(g['tris']),bbox=dict(min=np.round(V.min(0),2).tolist(),max=np.round(V.max(0),2).tolist()),size=np.round(V.max(0)-V.min(0),2).tolist())
    print(k,len(g['tris']),report[k]['size'],report[k]['bbox'])
json.dump(report,open(os.path.join(OUT,'box_report.json'),'w'),indent=1)
palette_png(os.path.join(OUT,'props_palette.png'));json.dump(PAL,open(os.path.join(OUT,'palette.json'),'w'))
import pickle;pickle.dump({k:p.merged() for k,p in props.items()},open(os.path.join(OUT,'assembled_preview.pkl'),'wb'))
