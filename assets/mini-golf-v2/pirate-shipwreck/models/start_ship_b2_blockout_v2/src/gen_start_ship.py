# Start ship B2/B3 blockout generator (box, numpy/trimesh/shapely). Roblox frame: +Y up, front +Z, studs.
# Ship long axis = X (stern -X, bow +X). Low (sand) side = +Z. v2: hull listing 15 deg, masts/sails/rigging roll 18 deg; hull/masts/sails/rigging roll toward +Z; deck, cabin, platform, ramp are LEVEL / fixed grade.
# Writes work/geom.json (objects with own origins, empties, COL boxes, preview-only extras) and work/palette.png
import numpy as np, trimesh, math, json, os, sys
from shapely.geometry import Polygon, box as sbox
from shapely import affinity
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','work');os.makedirs(OUT,exist_ok=True)
PAL=dict(Wood=(110,70,40),WoodDk=(80,50,30),Post=(100,72,50),PostLt=(122,90,64),Thatch=(200,165,90),Rock=(115,100,92),RockDk=(94,82,76),RockLt=(135,119,110),
 Sand=(226,184,128),Felt=(105,185,98),Flame=(240,110,30),Canvas=(225,205,165),CanvasDk=(198,176,136),Red=(200,50,40),Rope=(176,140,86),Iron=(70,66,64),Glow=(255,190,110))
NAMES=list(PAL)
def uv_of(c):
    i=NAMES.index(c);return [(i%8+0.5)/8,1-(i//8+0.5)/8]
def palette_png(p):
    from PIL import Image
    im=Image.new('RGB',(256,256),(128,128,128))
    for n,c in PAL.items():
        i=NAMES.index(n);im.paste(c,((i%8)*32,(i//8)*32,(i%8)*32+32,(i//8)*32+32))
    im.save(p)
PHI=math.radians(15);CP,SP=math.cos(PHI),math.sin(PHI)   # HULL list (kept at 15 so the level-deck cut / cabin / tee / ramp origins do not move)
PHIR=math.radians(18);CPR,SPR=math.cos(PHIR),math.sin(PHIR)   # masts, sails, rigging roll
def tilt(p):
    x,y,z=p;return (x,y*CP-z*SP,y*SP+z*CP)
def tiltR(p):
    x,y,z=p;return (x,y*CPR-z*SPR,y*SPR+z*CPR)
def Rx(a):
    c,s=math.cos(a),math.sin(a);return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a):
    c,s=math.cos(a),math.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
class Part:
    def __init__(s,name,origin=(0,0,0)):
        s.name=name;s.origin=np.array(origin,float);s.T=[];s.C=[]   # T: list of (3,3) triangles in LOCAL coords, C colour name per tri
    def tri(s,a,b,c,col,want=None):
        a,b,c=[np.array(v,float) for v in(a,b,c)]
        n=np.cross(b-a,c-a)
        if np.linalg.norm(n)<1e-9: return
        if want is not None and np.dot(n,want)<0: b,c=c,b
        s.T.append(np.array([a,b,c]));s.C.append(col)
    def mesh(s,m,col,R=None,t=(0,0,0),tf=None):
        V=np.array(m.vertices);F=np.array(m.faces)
        for f in F:
            tri=V[f];n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);n=n/(np.linalg.norm(n)+1e-12)
            cn=col(n) if callable(col) else col
            P=tri@R.T+np.array(t) if R is not None else tri+np.array(t)
            if tf: P=np.array([tf(p) for p in P])
            s.tri(P[0],P[1],P[2],cn)
    def box(s,c,size,col,R=None):
        m=trimesh.creation.box(extents=size);s.mesh(m,col,R,c)
    def beam(s,p0,p1,w,col,h=None,up=(0,1,0),tf=None):
        p0=np.array(p0,float);p1=np.array(p1,float);h=w if h is None else h;d=p1-p0;L=np.linalg.norm(d);d/=L
        a=np.cross(d,up)
        if np.linalg.norm(a)<1e-6:a=np.cross(d,(1,0,0))
        a/=np.linalg.norm(a);b=np.cross(d,a);R=np.eye(3);R[:,0]=a;R[:,1]=b;R[:,2]=d
        m=trimesh.creation.box(extents=(w,h,L));s.mesh(m,col,R,(p0+p1)/2,tf=tf)
    def frustum(s,r0,r1,p0,p1,col,sec=8,tf=None):
        p0=np.array(p0,float);p1=np.array(p1,float);d=p1-p0;L=np.linalg.norm(d);d/=L
        a=np.cross(d,(0,1,0))
        if np.linalg.norm(a)<1e-6:a=np.cross(d,(1,0,0))
        a/=np.linalg.norm(a);b=np.cross(d,a);ring=[]
        for r,p in((r0,p0),(r1,p1)):
            ring.append([p+r*(math.cos(2*math.pi*k/sec)*a+math.sin(2*math.pi*k/sec)*b) for k in range(sec)])
        for k in range(sec):
            j=(k+1)%sec;ctr=(ring[0][k]+ring[0][j]+ring[1][k]+ring[1][j])/4-(p0+p1)/2
            s.tri(ring[0][k],ring[1][k],ring[1][j],col,want=ctr);s.tri(ring[0][k],ring[1][j],ring[0][j],col,want=ctr)
            s.tri(p0,ring[0][j],ring[0][k],col,want=-d);s.tri(p1,ring[1][k],ring[1][j],col,want=d)
    def poly_slab(s,poly,y0,y1,top,side,bottom=None):
        """extrude shapely polygon given in (x,z) between world/local heights y0<y1. Faces oriented outward."""
        V,F=trimesh.creation.triangulate_polygon(poly,engine='earcut')
        for f in F:
            a,b,c=[np.array([V[i][0],y1,V[i][1]]) for i in f];s.tri(a,b,c,top,want=(0,1,0))
            a,b,c=[np.array([V[i][0],y0,V[i][1]]) for i in f];s.tri(a,b,c,bottom or side,want=(0,-1,0))
        rings=[poly.exterior]+list(poly.interiors)
        for r in rings:
            pts=list(r.coords)[:-1]
            for i in range(len(pts)):
                p,q=pts[i],pts[(i+1)%len(pts)]
                if math.dist(p,q)<1e-9: continue
                A=np.array([p[0],y0,p[1]]);B=np.array([q[0],y0,q[1]]);C=np.array([q[0],y1,q[1]]);D=np.array([p[0],y1,p[1]])
                mid=(A+C)/2;cen=np.array([np.mean([pp[0] for pp in pts]),mid[1],np.mean([pp[1] for pp in pts])])
                # outward = away from polygon interior (for holes: toward the hole centre, handled by sign of orientation)
                nrm=np.cross(B-A,D-A)
                inside=r is poly.exterior
                want=(mid-cen) if inside else (cen-mid)
                s.tri(A,B,C,side,want=want);s.tri(A,C,D,side,want=want)
    def out(s):
        V=[];U=[];F=[]
        for t,c in zip(s.T,s.C):
            i=len(V);V+=[list(map(float,p)) for p in t];U+=[uv_of(c)]*3;F.append([i,i+1,i+2])
        return dict(name=s.name,origin=list(map(float,s.origin)),verts=V,tris=F,uvs=U,smooth=[0]*len(F))
    def tf_apply(s,fn):
        s.T=[np.array([fn(p) for p in t]) for t in s.T]
objs={};cols=[];empties=[];prev={}
def COL(name,centre,size,R=None,pivot=(0,0,0),note=''):
    cols.append(dict(name=name,centre=list(map(float,centre)),size=list(map(float,size)),R=(np.eye(3) if R is None else R).tolist(),pivot=list(map(float,pivot)),note=note))
Pv=np.array
# ------------------------------------------------------------------ layout constants
DECK=24.0;SAND=0.0
L=320.0;X0=-160.0;BEAM=45.0;PW=2.2;HG=45.2
def tpar(x): return (x-X0)/L
def bprof(x): return BEAM*max(0.0,1-tpar(x)**3.5)**0.75
def hgt(x): t=tpar(x);return HG*(1+0.15*t**4+0.07*(1-t)**3)
def y0f(x): return 26*tpar(x)**4
def twf(x): return min(2.5,0.45*bprof(x))
GAP=(-130.0,-110.0);NOTCH_W=23.0     # bulwark notch, world height of notch floor
CAB=dict(x0=-150.0,x1=-90.0,z0=-19.0,z1=24.0,wt=2.0,wall_h=16.0,peak=30.0)   # cabin outer footprint 60 x 43; walls 16 -> interior 16 at eaves
DOORX=-120.0;DOOR_W=8.0;DOOR_H=10.0
def outer_pts(x,n=23,clamp=False):
    b=bprof(x);h=hgt(x);y0=y0f(x);P=[]
    for s in np.linspace(-1,1,n):
        z=s*b;y=y0+(h-y0)*abs(s)**PW
        if clamp and s>0: y=min(y,(NOTCH_W+z*SP)/CP)
        P.append((z,y))
    return P
def inner_pts(x,n=23,clamp=False):
    b=bprof(x);h=hgt(x);y0=y0f(x);tw=twf(x);bi=b-tw;P=[]
    for s in np.linspace(1,-1,n):
        z=s*bi;y=y0+tw+(h-y0-tw)*abs(s)**PW
        if clamp and s>0: y=min(y,(NOTCH_W+z*SP)/CP)
        P.append((z,y))
    return P
# ------------------------------------------------------------------ HULL (tilted)
hull=Part('Hull')
xs=sorted(set([round(v,3) for v in np.linspace(X0,X0+0.99*L,34)]+[GAP[0]-0.02,GAP[0],GAP[1],GAP[1]+0.02]))
def clampflag(x): return GAP[0]-0.03<x<GAP[1]+0.03
NOUT=23
rings=[]
for x in xs:
    cl=clampflag(x)
    O=outer_pts(x,NOUT,cl);I=inner_pts(x,NOUT,cl);rings.append((x,O+I))
WALES={0,21,2,19,5,16,10,11}   # outer strip indices: sheer strake 0/21, upper wale 2/19, lower wale 5/16, keel 10/11
def pt3(x,zy): return np.array(tilt((x,zy[1],zy[0])))
def ring_edges():
    E=[]
    for i in range(NOUT-1):E.append((i,i+1,'o',i))
    E.append((NOUT-1,NOUT,'r',0))
    for k in range(NOUT-1):E.append((NOUT+k,NOUT+k+1,'i',k))
    E.append((2*NOUT-1,0,'r',1));return E
for (xa,Ra),(xb,Rb) in zip(rings[:-1],rings[1:]):
    h=hgt((xa+xb)/2);cen=np.array(tilt(((xa+xb)/2,h*0.55,0)))
    for u,v,kind,idx in ring_edges():
        A=pt3(xa,Ra[u]);B=pt3(xa,Ra[v]);C=pt3(xb,Rb[v]);D=pt3(xb,Rb[u])
        mid=(A+B+C+D)/4
        if kind=='o':
            want=mid-cen;col='WoodDk' if idx in WALES else 'Wood'   # planks (110,70,40); sheer strake + two wales + keel strip (80,50,30)
        elif kind=='i': want=cen-mid;col='Wood'
        else: want=np.array([0,1,0.0]);col='WoodDk'
        hull.tri(A,B,C,col,want=want);hull.tri(A,C,D,col,want=want)
def fan(P3,ctr,col,want):
    for i in range(len(P3)-1): hull.tri(ctr,P3[i],P3[i+1],col,want=want)
xS,RS=rings[0];xB,RB=rings[-1]
sil=lambda x:[pt3(x,p) for p in outer_pts(x,NOUT)]
Ps=sil(xS);fan(Ps+[Ps[0]],np.mean(Ps,axis=0),'Wood',(-1,0,0))
Pb=sil(xB);fan(Pb+[Pb[0]],np.mean(Pb,axis=0),'Wood',(1,0,0))
xt=X0+twf(X0);Pi=[pt3(xt,p) for p in inner_pts(xt,NOUT)[::-1]];Pi3=[np.array([xt,p[1],p[2]]) for p in Pi]
fan(Pi3+[Pi3[0]],np.mean(Pi3,axis=0),'Post',(1,0,0))
# ---- v2: STERN CASTLE (raised bulwark walls around the cabin, tilts with the hull) + BOWSPRIT (hull frame)
CASTLE_H=10.0;CAS_X0,CAS_X1=-95.0,-65.0;GAPC=(GAP[0]-3.0,GAP[1]+3.0)
def cas_d(x): return CASTLE_H*min(1.0,max(0.0,(CAS_X1-x)/(CAS_X1-CAS_X0)))
CASTLE_RUNS=[]   # (xa,xb,sign) for COL
def cas_prism(xa,xb,sg,cap_a=False,cap_b=False):
    def sec(x):
        b=bprof(x);bi=b-twf(x);h=hgt(x);d=cas_d(x)
        return [np.array(tilt((x,y,sg*z))) for (z,y) in((b,h-1.0),(b,h+d),(bi,h+d),(bi,h-1.0))]
    pa,pb=sec(xa),sec(xb);cen=np.mean(pa+pb,axis=0)
    for k,col in((0,'Wood'),(1,'WoodDk'),(2,'Wood')):
        A,B,C,D=pa[k],pa[k+1],pb[k+1],pb[k];mid=(A+B+C+D)/4;w=mid-cen
        if k==0: w=np.array(tilt((0,0,sg)))
        if k==2: w=-np.array(tilt((0,0,sg)))
        if k==1: w=np.array(tilt((0,1,0)))
        hull.tri(A,B,C,col,want=w);hull.tri(A,C,D,col,want=w)
    for cap,p,sgn in((cap_a,pa,-1),(cap_b,pb,1)):
        if cap:
            hull.tri(p[0],p[1],p[2],'Wood',want=(sgn,0,0));hull.tri(p[0],p[2],p[3],'Wood',want=(sgn,0,0))
    CASTLE_RUNS.append((xa,xb,sg))
xc=[-160.0,-140.0,-133.0]+[-107.0,-95.0,-85.0,-75.0,-65.0]
for sg in(-1,1):
    if sg<0:
        for xa,xb in zip([-160.0,-145.0,-130.0,-115.0,-100.0,-95.0,-85.0,-75.0],[-145.0,-130.0,-115.0,-100.0,-95.0,-85.0,-75.0,-65.0]): cas_prism(xa,xb,sg)
    else:
        for xa,xb,ca,cb in((-160.0,-145.0,0,0),(-145.0,-133.0,0,1),(-107.0,-95.0,1,0),(-95.0,-85.0,0,0),(-85.0,-75.0,0,0),(-75.0,-65.0,0,0)): cas_prism(xa,xb,sg,ca,cb)
_b=bprof(X0);_h=hgt(X0)
hull.box(tilt((X0+0.2+1.15,_h+(CASTLE_H-1.0)/2,0)),(2.3,CASTLE_H+1.0,2*_b),lambda n:'Wood' if n[0]<-0.5 else 'WoodDk',R=Rx(PHI))   # transom plate (stern castle back wall)
# bowsprit: from the forecastle, in the hull's 15 deg frame
BS0=(118.0,45.0,0.0);BS1=(215.0,70.0,0.0)
hull.beam(tilt(BS0),tilt(BS1),2.6,'Wood')
hull.beam(tilt((150.0,45.0+32*0.2577-1.5,0.0)),tilt((178.0,45.0+60*0.2577-1.5,0.0)),0.0001,'Rope') if False else None
BS_TIP=np.array(tilt(BS1))
objs['Hull']=hull
# ------------------------------------------------------------------ deck polygon (level at Y=24) from inner hull cross-section
def inner_cross(x,level=DECK):
    n=801;b=bprof(x);h=hgt(x);y0=y0f(x);tw=twf(x);bi=b-tw
    s=np.linspace(-1,1,n);z=s*bi;y=y0+tw+(h-y0-tw)*np.abs(s)**PW
    yw=y*CP-z*SP;zw=z*CP+y*SP
    d=yw-level;idx=np.where(np.diff(np.sign(d)))[0]
    if len(idx)<2:return None
    def interp(i):
        t=d[i]/(d[i]-d[i+1]);return zw[i]+t*(zw[i+1]-zw[i])
    return interp(idx[0]),interp(idx[-1])
xd=np.linspace(X0+2.0,X0+L*0.995,200);edge=[]
for x in xd:
    r=inner_cross(x)
    if r is None or r[1]-r[0]<10: break
    edge.append((x,r[0],r[1]))
edge=np.array(edge);X_DECK_END=float(edge[-1,0])
HI=lambda x:float(np.interp(x,edge[:,0],edge[:,1]));LO=lambda x:float(np.interp(x,edge[:,0],edge[:,2]))
EXP=0.6
dx=[X0+2.0-2.0]+[e[0] for e in edge]
top=[(edge[0,0]-2.0,edge[0,1]-EXP)]+[(e[0],e[1]-EXP) for e in edge]+[(edge[-1,0]+0.0,edge[-1,1]-EXP)]
bot=[(edge[0,0]-2.0,edge[0,2]+EXP)]+[(e[0],e[2]+EXP) for e in edge]
deck_poly=Polygon(top+bot[::-1]).buffer(0)
# ------------------------------------------------------------------ DECK + CABIN + OUTRIGGER (level)
dc=Part('DeckCabin')
CI=sbox(CAB['x0']+CAB['wt'],CAB['z0']+CAB['wt'],CAB['x1']-CAB['wt'],CAB['z1']-CAB['wt'])
deck_h=deck_poly.difference(CI)
dc.poly_slab(deck_h,DECK-2.0,DECK,'PostLt','Wood')
dc.poly_slab(CI,DECK-2.0,DECK,'PostLt','Wood')   # cabin floor slab (abuts the deck slab, same top Y=24)
wt=CAB['wt'];x0,x1,z0,z1=CAB['x0'],CAB['x1'],CAB['z0'],CAB['z1'];wh=CAB['wall_h'];yb=DECK-0.3;ytop=DECK+wh
def wallbox(xa,xb,za,zb,ya,yb2):
    dc.box(((xa+xb)/2,(ya+yb2)/2,(za+zb)/2),(xb-xa,yb2-ya,zb-za),lambda n:'Wood')
wallbox(x0,x1,z0,z0+wt,yb,ytop)                 # back (-Z)
wallbox(x0,x0+wt,z0+wt-0.0,z1-wt,yb,ytop)       # -X end  (small overlap into corners avoided: abuts)
wallbox(x1-wt,x1,z0+wt,z1-wt,yb,ytop)           # +X end
wallbox(x0,DOORX-DOOR_W/2,z1-wt,z1,yb,ytop)     # front left of door
wallbox(DOORX+DOOR_W/2,x1,z1-wt,z1,yb,ytop)     # front right of door
wallbox(DOORX-DOOR_W/2,DOORX+DOOR_W/2,z1-wt,z1,DECK+DOOR_H,ytop)   # lintel
# door frame trim (dark wood, proud of the wall by 0.3)
dc.box((DOORX-DOOR_W/2-0.4,DECK+DOOR_H/2+0.3,z1+0.15),(0.8,DOOR_H+0.6,0.7),lambda n:'WoodDk')
dc.box((DOORX+DOOR_W/2+0.4,DECK+DOOR_H/2+0.3,z1+0.15),(0.8,DOOR_H+0.6,0.7),lambda n:'WoodDk')
dc.box((DOORX,DECK+DOOR_H+0.4,z1+0.15),(DOOR_W+1.6,0.8,0.7),lambda n:'WoodDk')
# gable roof (ridge along X); gable infill triangles poke 0.6 into the roof slabs
zc=(z0+z1)/2;half=(z1-z0)/2;rise=CAB['peak']-wh;ang=math.atan2(rise,half)
for xe0,xe1 in((x0,x0+wt),(x1-wt,x1)):
    pts=[(z0,ytop),(z1,ytop),(zc,ytop+rise+0.9)]
    for k in range(3):
        a,b=pts[k],pts[(k+1)%3]
    A=[(xe0,p[1],p[0]) for p in pts];B=[(xe1,p[1],p[0]) for p in pts]
    dc.tri(A[0],A[2],A[1],'Wood',want=(-1,0,0));dc.tri(B[0],B[1],B[2],'Wood',want=(1,0,0))
    for k in range(3):
        a0,a1=A[k],A[(k+1)%3];b0,b1=B[k],B[(k+1)%3];mid=(np.array(a0)+np.array(b1))/2;cen=(np.mean([p[0] for p in A+B]),np.mean([p[1] for p in A+B]),np.mean([p[2] for p in A+B]))
        dc.tri(a0,b0,b1,'Wood',want=mid-np.array(cen));dc.tri(a0,b1,a1,'Wood',want=mid-np.array(cen))
ov=2.5;slope_len=half/math.cos(ang)+ov/math.cos(ang)+0.5;thick=1.6
for side in(-1,1):
    # panel centre line from apex down to eave
    apex=np.array([0,ytop+rise+0.2,zc]);dirv=np.array([0,-math.sin(ang),side*math.cos(ang)])
    c=apex+dirv*(slope_len/2-0.4);R=Rx(-side*ang) if side>0 else Rx(-side*ang)
    # build in local frame: box (len X, thick, slope_len) -> rotate so local z maps onto dirv
    m=trimesh.creation.box(extents=(CAB['x1']-CAB['x0']+2*ov,thick,slope_len))
    a=math.atan2(-dirv[1],dirv[2]);R=Rx(a)    # R_x(a) maps z-axis to (0,-sin a,cos a) = dirv
    dc.mesh(m,lambda n:'WoodDk' if n[1]>0.5 else 'Wood',R,c)
dc.box(((x0+x1)/2,ytop+rise+1.3,zc),(CAB['x1']-CAB['x0']+2*ov,0.8,1.6),lambda n:'Wood')
# tee pad (felt, on deck), 12 x 14, 6 studs from the door face
TEE_Z0=z1+6.0;TEE_Z1=TEE_Z0+14.0
dc.box((DOORX,DECK+0.2,(TEE_Z0+TEE_Z1)/2),(12,0.4,14),lambda n:'Felt' if n[1]>0.5 else 'WoodDk')
# outrigger platform (level, Y=24 top): 22 wide (gap 20 + 1 each side), z 43..63
PX0,PX1,PZ0,PZ1=DOORX-11.0,DOORX+11.0,43.0,63.0
dc.box(((PX0+PX1)/2,DECK-1.0,(PZ0+PZ1)/2),(PX1-PX0,2.0,PZ1-PZ0),lambda n:'PostLt' if n[1]>0.5 else 'Wood')
for px in(PX0+3.0,DOORX,PX1-3.0): dc.box((px,(DECK-1.5-1.0)/2,PZ1-2.0),(2.4,DECK-1.5+1.0,2.4),lambda n:'Post')
def rail_box(part,xa,xb,za,zb,h,inner_dir=None,base=DECK):
    part.box(((xa+xb)/2,base+h/2-0.1,(za+zb)/2),(xb-xa,h+0.2,zb-za),lambda n:'Post' if n[1]>0.5 else 'Wood')
RH=4.0
rail_box(dc,PX0,PX0+1.6,48.0,PZ1,RH);rail_box(dc,PX1-1.6,PX1,48.0,PZ1,RH)
MW=7.6    # half width of flight1 slab+rails
rail_box(dc,PX0,DOORX-MW,PZ1-1.6,PZ1,RH);rail_box(dc,DOORX+MW,PX1,PZ1-1.6,PZ1,RH)
# ---- v2: RAILED FORECASTLE STEP at the bow (level, +6 over the deck) with a 10-wide stair and rails
FC_X0=112.0;FC_H=6.0;FT=DECK+FC_H
fc_poly=deck_poly.intersection(sbox(FC_X0,-200.0,400.0,200.0)).buffer(-0.3,join_style=2)
dc.poly_slab(fc_poly,DECK-0.5,FT,'PostLt','Wood')
FZC=(HI(FC_X0+0.3)+LO(FC_X0+0.3))/2
dc.box((FC_X0-3.75,DECK-0.5+(2.0+0.5)/2,FZC),(7.5,2.5,10.0),lambda n:'PostLt' if n[1]>0.5 else 'Wood')       # tread 1: top DECK+2
dc.box((FC_X0-1.25,DECK-0.5+(4.0+0.5)/2,FZC),(2.5+0.3,4.5,10.0),lambda n:'PostLt' if n[1]>0.5 else 'Wood')    # tread 2: top DECK+4
def fc_rail():
    pin=fc_poly.buffer(-1.4,join_style=2);pts=[np.array(p) for p in pin.exterior.coords]
    xmin=pin.bounds[0];segs=[]
    for p,q in zip(pts[:-1],pts[1:]):
        ln=np.linalg.norm(q-p)
        if ln<0.5: continue
        if abs(p[0]-xmin)<0.05 and abs(q[0]-xmin)<0.05:
            za,zb=p[1],q[1];lo,hi=sorted((za,zb));gz=(FZC-5.8,FZC+5.8);brk=sorted(set([za,zb]+[g for g in gz if lo<g<hi]),reverse=(za>zb))
            for u,v in zip(brk[:-1],brk[1:]):
                m=(u+v)/2
                if gz[0]<m<gz[1]: continue
                segs.append((np.array([xmin,u]),np.array([xmin,v])))
        else: segs.append((p,q))
    posts=[]
    for p,q in segs:
        n=max(1,int(math.ceil(np.linalg.norm(q-p)/8.0)))
        for k in range(n):
            a=p+(q-p)*k/n;b=p+(q-p)*(k+1)/n
            dc.beam((a[0],FT+3.2,a[1]),(b[0],FT+3.2,b[1]),0.9,'Post')
            dc.beam((a[0],FT+1.5,a[1]),(b[0],FT+1.5,b[1]),0.5,'Rope')
            posts+=[a,b]
    seen=[]
    for a in posts:
        if any(np.linalg.norm(a-s_)<0.3 for s_ in seen): continue
        seen.append(a);dc.box((a[0],FT+1.7,a[1]),(1.5,4.0,1.5),lambda n:'Post')
    return segs
FC_SEGS=fc_rail()
# bowsprit bitts: two posts from the forecastle top up to the bowsprit underside
for bx in(122.0,132.0):
    bp=np.array(tilt((bx,BS0[1]+(bx-BS0[0])*(BS1[1]-BS0[1])/(BS1[0]-BS0[0]),0.0)))
    hh=bp[1]-1.5-FT+0.4;dc.box((bx,FT-0.4+hh/2,bp[2]),(2.4,hh,2.4),lambda n:'Post')
objs['DeckCabin']=dc
SPAWN=(DOORX,DECK,(z0+z1)/2);TEE1=(DOORX,DECK+0.4,(TEE_Z0+TEE_Z1)/2);RAMPSTART=(DOORX,DECK,PZ1-0.5)
F1_ORG=np.array(RAMPSTART)
# ------------------------------------------------------------------ MASTS + SAILS + RIGGING (tilted)
rg=Part('Rigging');TF=tiltR
def tp(p): return np.array(tiltR(p))
def mast(x,ybase,ytip,r0,r1,yards,sails_h,flag=True):
    rg.frustum(r0,r1,tp((x,ybase,0)),tp((x,ytip,0)),'Post',8)
    # crow's nest
    yc=ytip*0.80
    rg.box(tp((x,yc,0)),(7,0.8,7),lambda n:'PostLt',R=Rx(PHIR)@np.eye(3)) if False else None
    nest=trimesh.creation.box(extents=(7,0.8,7));rg.mesh(nest,lambda n:'PostLt',Rx(PHIR),tp((x,yc,0)))
    for (yy,ln,sh) in yards:
        rg.beam(tp((x,yy,-ln/2)),tp((x,yy,ln/2)),1.3,'Post')
        rg.box(tp((x+0.9,yy-sh/2-0.7,0)),(0.5,sh,ln*0.88),lambda n:'Canvas' if abs(n[0])>0.5 else 'CanvasDk',R=Rx(PHIR))
    if flag:
        rg.box(tp((x+0.2,ytip+0.0-4.5,0)),(0.4,0,0),lambda n:'Red') if False else None
        fl=trimesh.creation.box(extents=(0.4,6.0,15.0));rg.mesh(fl,lambda n:'Red',Rx(PHIR),tp((x+0.2,ytip-4.0,-8.0)))
MAIN_X,FORE_X=10.0,95.0
mast(MAIN_X,8,165,3.4,1.6,[(62,58,30),(100,48,28),(133,36,24)],0)
mast(FORE_X,8,126,2.8,1.4,[(52,46,26),(84,38,26),(108,28,20)],0)
# bowsprit + stays (thin beams) + shrouds
rg.beam(tp((MAIN_X,165,0)),BS_TIP,0.6,'Rope');rg.beam(tp((FORE_X,126,0)),BS_TIP,0.6,'Rope')   # stays run to the (hull-frame) bowsprit tip
rg.beam(tp((MAIN_X,165,0)),tp((FORE_X,126,0)),0.6,'Rope');rg.beam(tp((MAIN_X,165,0)),tp((-150,70,0)),0.6,'Rope')
for mx,yy in((MAIN_X,100),(FORE_X,84)):
    for sgn in(-1,1):
        for dxx in(-6,6): rg.beam(tp((mx,yy,0)),np.array(tilt((mx+dxx,hgt(mx+dxx)-1,sgn*(bprof(mx+dxx)-1.2)))),0.5,'Rope')
objs['Rigging']=rg
# ------------------------------------------------------------------ RAMP pieces
def flight(name,origin,run,drop,apron=False,end_y_local=None):
    P=Part(name,origin);th=math.atan2(drop,run);Ls=run/math.cos(th);n=np.array([0,math.cos(th),math.sin(th)]);R=Rx(th)
    mid=np.array([0,-drop/2,run/2]);gl=-origin[1]-1.0    # local y of sand-1
    P.mesh(trimesh.creation.box(extents=(15.0,2.0,Ls)),lambda n_:'Felt' if n_[1]>0.5 else 'Wood',R,mid-n*1.0)
    for sx in(-1,1):
        P.mesh(trimesh.creation.box(extents=(1.6,3.7,Ls)),lambda n_,sx=sx:('Felt' if n_[0]*sx<-0.5 else ('Post' if n_[1]>0.5 else 'Wood')),R,mid+n*(3.5/2-0.2)+np.array([sx*6.8,0,0]))
        P.mesh(trimesh.creation.box(extents=(1.4,1.6,Ls)),lambda n_:'WoodDk',R,mid-n*2.8+np.array([sx*5.0,0,0]))   # stringers
        zs=[1.0,17.0,33.0,49.0]
        for z in zs:
            if z>run-0.5: continue
            yt=-z*drop/run
            P.box((sx*6.8,yt-0.5+3.25,z),(2.4,6.5,2.4),lambda n_:'Post')
            if z>=16:
                hh=(yt-1.5)-gl
                if hh>0.5: P.box((sx*6.0,gl+hh/2,z),(2.4,hh,2.4),lambda n_:'Post')
        for z0_,z1_ in zip(zs[:-1],zs[1:]):
            if z1_>run-0.5: continue
            P.beam((sx*6.8,-z0_*drop/run+5.0-1.2,z0_),(sx*6.8,-z1_*drop/run+5.0-1.2,z1_),0.5,'Rope')
    if apron:
        ay=end_y_local;P.box((0,ay-0.6+0.0,run+8.0-0.25),(14.0,1.2,16.5),lambda n_:'Felt' if n_[1]>0.5 else 'Wood')
    return P
def flight_cols(prefix,P,run,drop,apron=False,ay=None):
    th=math.atan2(drop,run);Ls=run/math.cos(th);n=np.array([0,math.cos(th),math.sin(th)]);R=Rx(th);mid=np.array([0,-drop/2,run/2])
    COL(prefix+'_Surface',mid-n*1.0,(15.0,2.0,Ls),R,P.origin,'felt surface (ball friction/bounce); walkable')
    for sx,nm in((-1,'RailW'),(1,'RailE')): COL(prefix+'_'+nm,mid+n*(3.5/2-0.2)+np.array([sx*6.8,0,0]),(1.6,3.7,Ls),R,P.origin,'rail 3.5 high')
    if apron: COL(prefix+'_Apron',(0,ay-0.6,run+8.0-0.25),(14.0,1.2,16.5),None,P.origin,'flat felt apron')
F1_RUN,F1_DROP=52.0,12.0
f1=flight('RampFlight1',F1_ORG,F1_RUN,F1_DROP);objs['RampFlight1']=f1
flight_cols('COL_Flight1',f1,F1_RUN,F1_DROP)
LAND_ORG=F1_ORG+np.array([0,-F1_DROP,F1_RUN])
# landing (local origin = centre of north edge, local y=0 is the landing top, world Y=12)
Mloc=np.array([-6.7,13.0]);dloc=np.array([-0.5,math.sqrt(3)/2])
lp=Part('RampLanding',LAND_ORG)
sq=sbox(-8.0,-0.5,8.0,16.0)
nrm=dloc;tang=np.array([-nrm[1],nrm[0]]);base=Mloc+0.5*nrm
big=Polygon([tuple(base+200*tang),tuple(base-200*tang),tuple(base-200*tang-300*nrm),tuple(base+200*tang-300*nrm)])
land_poly=sq.intersection(big).buffer(0)
lp.poly_slab(land_poly,-2.0,0.0,'Felt','Wood')
def lrail(xa,xb,za,zb,h):
    lp.box(((xa+xb)/2,h/2-0.2,(za+zb)/2),(xb-xa,h+0.4,zb-za),lambda n:'Post' if n[1]>0.5 else ('Felt' if False else 'Wood'))
    return ((xa+xb)/2,h/2-0.2,(za+zb)/2),(xb-xa,h+0.4,zb-za)
LRAILS={}
LRAILS['RailE']=lrail(6.5,8.1,-0.5,16.1,3.5)
LRAILS['RailS']=lrail(-1.5,8.1,14.5,16.1,5.5)
LRAILS['RailW']=lrail(-8.1,-6.5,-0.5,12.4,3.5)
LRAILS['RailN_W']=lrail(-8.1,-6.0,-0.5,1.1,3.5)
LRAILS['RailN_E']=lrail(6.0,8.1,-0.5,1.1,3.5)
for (px,pz) in((7.3,-0.5+0.8),(-7.3,0.3),(7.3,15.3),(-1.6+0.0,15.3),(-7.3,11.5)):
    lp.box((px,3.0-0.2,pz),(2.4,6.4,2.4),lambda n:'Post')
for (px,pz) in((-6.2,2.0),(6.2,2.0),(6.2,13.5),(-6.2,8.0)):
    lp.box((px,(-1.0-13.0)/2,pz),(2.4,12.0+1.0+1.0,2.4),lambda n:'Post')
objs['RampLanding']=lp
COL('COL_Landing_FloorA',(0,-1.0,5.85),(16.0,2.0,12.7),None,LAND_ORG,'flat felt, top at world Y=12')
COL('COL_Landing_FloorB',(3.25,-1.0,14.0),(9.5,2.0,4.0),None,LAND_ORG,'flat felt SE part (corner cut for flight2 mouth)')
for k,(c,s) in LRAILS.items(): COL('COL_Landing_'+k,c,s,None,LAND_ORG,'outer south rail 5.5 high' if k=='RailS' else 'rail')
F2_ORG=np.array([LAND_ORG[0]+Mloc[0],12.0,LAND_ORG[2]+Mloc[1]])
F2_RUN=52.0;F2_DROP=11.8
f2=flight('RampFlight2',F2_ORG,F2_RUN,F2_DROP,apron=True,end_y_local=-F2_DROP);objs['RampFlight2']=f2
flight_cols('COL_Flight2',f2,F2_RUN,F2_DROP,apron=True,ay=-F2_DROP)
d2=np.array([-0.5,0,math.sqrt(3)/2]);n2=np.array([math.sqrt(3)/2,0,0.5])
CUP=F2_ORG+d2*98.0;CUP[1]=0.0
# ------------------------------------------------------------------ PIER (own origin at its centre)
PIER_O=np.array([-215.0,0.0,125.0]);pier=Part('Pier',PIER_O);PL=190.0
pier.box((0,3.5,0),(10.0,1.0,PL),lambda n:'PostLt' if n[1]>0.5 else 'Wood')
for sx in(-1,1):
    pier.box((sx*4.4,2.2,0),(1.2,1.4,PL),lambda n:'WoodDk')
    for z in np.arange(-PL/2+5,PL/2,15.0):
        pier.box((sx*4.2,0.0,z),(2.0,7.0,2.0),lambda n:'Post')
        pier.box((sx*4.4,6.6,z),(1.8,5.0,1.8),lambda n:'Post')
    zs=list(np.arange(-PL/2+5,PL/2,15.0))
    for a,b in zip(zs[:-1],zs[1:]): pier.beam((sx*4.4,8.5,a),(sx*4.4,8.5,b),0.5,'Rope')
objs['Pier']=pier
# ------------------------------------------------------------------ ROCK BUMPER (own origin at base centre)
BUMP_LAT=21.0;BUMP_ALONG=60.0
BUMP_O=np.array([*(F2_ORG[[0,2]]+d2[[0,2]]*BUMP_ALONG+n2[[0,2]]*BUMP_LAT)]);BUMP_O=np.array([BUMP_O[0],0.0,BUMP_O[1]])
rb=Part('RockBumper',BUMP_O);rng=np.random.RandomState(7)
ico=trimesh.creation.icosphere(subdivisions=1,radius=1.0);V=np.array(ico.vertices)*np.array([9.0,8.0,8.0]);V=V*(1+rng.uniform(-0.12,0.12,(len(V),1)));V[:,1]+=1.0
ico=trimesh.Trimesh(V,ico.faces,process=False)
rb.mesh(ico,lambda n:'RockLt' if n[1]>0.6 else ('RockDk' if n[1]<-0.2 else 'Rock'))
objs['RockBumper']=rb
# ------------------------------------------------------------------ DRESSING (world frame) + GLOW lanterns
dr=Part('Dressing');gl=Part('Dressing_Glow')
for (bx,bz) in((-82,-12),(-76,-6),(-80,-1)):
    dr.frustum(2.0,1.9,(bx,DECK,bz),(bx,DECK+4.5,bz),'Wood',8)
    dr.frustum(2.2,2.2,(bx,DECK+1.0,bz),(bx,DECK+1.5,bz),'Iron',8);dr.frustum(2.2,2.2,(bx,DECK+3.2,bz),(bx,DECK+3.7,bz),'Iron',8)
for (cx,cz,s) in((-70,-14,3.6),(-66.0,-8,3.6)):
    dr.box((cx,DECK+s/2,cz),(s,s,s),lambda n:'Post');dr.box((cx+0.2,DECK+s+1.5,cz),(2.6,3.0,2.6),lambda n:'PostLt')
dr.frustum(0.4,0.4,(40,DECK,30),(40,DECK+9,30),'Iron',6);dr.beam((37,DECK+7.5,30),(43,DECK+7.5,30),0.6,'Iron');dr.frustum(2.0,2.0,(40,DECK+0.0,24),(40,DECK+0.5,24),'Rope',8)
dr.frustum(2.2,2.2,(-100,DECK,-10),(-100,DECK+1.2,-10),'Rope',10)
for lx in(PX0+2.2,PX1-2.2):
    dr.box((lx,DECK+4.0,PZ1-2.2),(2.4,8.0,2.4),lambda n:'Post');dr.box((lx,DECK+8.6,PZ1-2.2),(3.4,1.0,3.4),lambda n:'Iron')
    gl.box((lx,DECK+10.3,PZ1-2.2),(2.2,2.4,2.2),lambda n:'Glow');dr.box((lx,DECK+11.8,PZ1-2.2),(3.0,0.6,3.0),lambda n:'Iron')
for z in(-PL/2+2,PL/2-2):
    pier.box((0,0,0),(0.0,0.0,0.0),lambda n:'Post') if False else None
objs['Dressing']=dr;objs['Dressing_Glow']=gl
# ------------------------------------------------------------------ COLLISION boxes (world; deck/cabin/platform at Y=24)
# level deck: segments of the inner hull cross-section
cuts=list(np.arange(float(edge[0,0]-1.0),X_DECK_END,16.0))+[X_DECK_END]
for k,(a,b) in enumerate(zip(cuts[:-1],cuts[1:])):
    seg=[e for e in edge if a<=e[0]<=b] or [edge[0]]
    zh=max(HI(a),HI(b),min(e[1] for e in seg)*0+max(e[1] for e in seg)) if False else max(max(HI(a),HI(b)),max(e[1] for e in seg))
    zl=min(min(LO(a),LO(b)),min(e[2] for e in seg))
    COL('COL_Deck_%02d'%k,((a+b)/2,DECK-1.0,(zh+zl)/2),(b-a+0.4,2.0,zl-zh+0.4),None,(0,0,0),'level deck, top Y=24')
COL('COL_CabinFloor',((x0+x1)/2,DECK-1.0,zc),(x1-x0-2*wt+0.4,2.0,z1-z0-2*wt+0.4),None,(0,0,0),'cabin floor, top Y=24')
COL('COL_Outrigger',((PX0+PX1)/2,DECK-1.0,(PZ0+PZ1)/2),(PX1-PX0,2.0,PZ1-PZ0),None,(0,0,0),'outrigger platform, top Y=24')
cw=lambda n,xa,xb,za,zb,ya,yb2:COL(n,((xa+xb)/2,(ya+yb2)/2,(za+zb)/2),(xb-xa,yb2-ya,zb-za),None,(0,0,0),'cabin wall')
cw('COL_CabinWall_Back',x0,x1,z0,z0+wt,DECK,ytop);cw('COL_CabinWall_W',x0,x0+wt,z0,z1,DECK,ytop);cw('COL_CabinWall_E',x1-wt,x1,z0,z1,DECK,ytop)
cw('COL_CabinWall_FrontL',x0,DOORX-DOOR_W/2,z1-wt,z1,DECK,ytop);cw('COL_CabinWall_FrontR',DOORX+DOOR_W/2,x1,z1-wt,z1,DECK,ytop)
cw('COL_CabinWall_Lintel',DOORX-DOOR_W/2,DOORX+DOOR_W/2,z1-wt,z1,DECK+DOOR_H,ytop)
for side in(-1,1):
    a=math.atan2(-(-math.sin(ang)),side*math.cos(ang)) if False else math.atan2(math.sin(ang),side*math.cos(ang))
    dirv=np.array([0,-math.sin(ang),side*math.cos(ang)]);apex=np.array([0,ytop+rise+0.2,zc]);c=apex+dirv*(slope_len/2-0.4)
    COL('COL_CabinRoof_%s'%('S' if side>0 else 'N'),((x0+x1)/2,c[1],c[2]),(x1-x0+2*ov,thick,slope_len),Rx(math.atan2(-dirv[1],dirv[2])),(0,0,0),'roof panel')
# deck-edge walls (invisible, 4+ high -> 22 so players/balls stay on the deck): high side, low side (with the ramp gap), stern, bow
ys0,ys1=DECK-2.0,DECK+16.0
ecut=list(np.arange(float(edge[0,0]-1.0),X_DECK_END,12.0))+[X_DECK_END]
for k,(a,b) in enumerate(zip(ecut[:-1],ecut[1:])):
    pts=[e for e in edge if a<=e[0]<=b]+[(a,HI(a),LO(a)),(b,HI(b),LO(b))]
    zh=max(p[1] for p in pts);zl=min(p[2] for p in pts)
    COL('COL_Bulwark_Hi_%02d'%k,((a+b)/2,(ys0+ys1)/2,zh-1.5),(b-a+0.2,ys1-ys0,3.0),None,(0,0,0),'high-side bulwark')
    if not (b<=GAP[0]+1 or a>=GAP[1]-1) :
        pass
    if b<=GAP[0]+0.01 or a>=GAP[1]-0.01 or True:
        # split around the ramp gap
        segs=[(a,b)]
        if b>GAP[0] and a<GAP[1]:
            segs=[]
            if a<GAP[0]: segs.append((a,GAP[0]))
            if b>GAP[1]: segs.append((GAP[1],b))
        for j,(sa,sb) in enumerate(segs):
            COL('COL_Bulwark_Lo_%02d_%d'%(k,j),((sa+sb)/2,(ys0+ys1)/2,zl+1.5),(sb-sa+0.2,ys1-ys0,3.0),None,(0,0,0),'low-side bulwark (gap for the ramp)')
COL('COL_Bulwark_Stern',(edge[0,0]-1.0,(ys0+ys1)/2,(HI(edge[0,0])+LO(edge[0,0]))/2),(3.0,ys1-ys0,LO(edge[0,0])-HI(edge[0,0])+4.0),None,(0,0,0),'stern wall')
COL('COL_Bulwark_Bow',(X_DECK_END+1.0,(ys0+ys1)/2,(HI(X_DECK_END)+LO(X_DECK_END))/2),(3.0,ys1-ys0,LO(X_DECK_END)-HI(X_DECK_END)+4.0),None,(0,0,0),'bow wall')
cr=lambda n,xa,xb,za,zb:COL(n,((xa+xb)/2,DECK+RH/2,(za+zb)/2),(xb-xa,RH,zb-za),None,(0,0,0),'platform edge rail 4 high')
cr('COL_PlatRail_W',PX0,PX0+1.6,48.0,PZ1);cr('COL_PlatRail_E',PX1-1.6,PX1,48.0,PZ1)
cr('COL_PlatRail_SW',PX0,DOORX-MW,PZ1-1.6,PZ1);cr('COL_PlatRail_SE',DOORX+MW,PX1,PZ1-1.6,PZ1)
# hull exterior (keep players out; scenery): tilted chord boxes hugging the outer skin
hs=np.linspace(X0,X0+0.99*L,9)
for k,(a,b) in enumerate(zip(hs[:-1],hs[1:])):
    xm=(a+b)/2;O=[np.array(tilt((xm,p[1],p[0])))[1:] for p in outer_pts(xm,9)]   # (y,z) world
    for i,(p,q) in enumerate(zip(O[:-1],O[1:])):
        dy,dz=q[0]-p[0],q[1]-p[1];ln=math.hypot(dy,dz)
        if ln<0.5: continue
        al=math.atan2(-dy,dz);R=Rx(al);nrm=R@np.array([0,1,0]);mid=(p+q)/2
        # outward normal: away from the hull axis (0, h*0.5 world) ; push box so its inner face lies on the skin
        axis=np.array(tilt((xm,hgt(xm)*0.5,0)))[1:];out=mid-axis;nv=np.array([nrm[1],nrm[2]])
        sgn=1.0 if np.dot(nv,out)>0 else -1.0
        cy,cz=mid+sgn*nv*1.25
        COL('COL_HullExt_%d_%02d'%(k,i),(xm,cy,cz),(b-a+0.2,2.5,ln+0.3),R,(0,0,0),'hull exterior (tilted 15 deg), scenery collision')
COL('COL_HullExt_Stern',(X0+1.0,tilt((X0,hgt(X0)*0.45,0))[1],tilt((X0,hgt(X0)*0.45,0))[2]),(2.0,hgt(X0)*0.9,2*BEAM*0.9),Rx(PHI),(0,0,0),'stern transom')

# v2 COLs: stern castle walls (tilted with the hull), forecastle step, stair, riser rails
for k,(xa,xb,sg) in enumerate(CASTLE_RUNS):
    xm=(xa+xb)/2;dm=(cas_d(xa)+cas_d(xb))/2
    if dm<1.0: continue
    b=bprof(xm);tw_=twf(xm);hh=hgt(xm)
    c=tilt((xm,hh+(dm-1.0)/2,sg*(b-tw_/2)))
    COL('COL_Castle_%s_%02d'%('Lo' if sg>0 else 'Hi',k),c,(xb-xa+0.1,dm+1.0,tw_),Rx(PHI),(0,0,0),'stern castle wall (tilted 15 deg with the hull), scenery collision')
COL('COL_Castle_Transom',tilt((X0+0.2+1.15,hgt(X0)+(CASTLE_H-1.0)/2,0)),(2.3,CASTLE_H+1.0,2*bprof(X0)),Rx(PHI),(0,0,0),'stern castle back wall')
fcut=list(np.arange(FC_X0,X_DECK_END,8.0))+[X_DECK_END]
for k,(a,b) in enumerate(zip(fcut[:-1],fcut[1:])):
    a2=max(a,FC_X0+0.3);zh=max(HI(a2),HI(b));zl=min(LO(a2),LO(b))
    COL('COL_Forecastle_%02d'%k,((a+b)/2,DECK+FC_H/2,(zh+zl)/2),(b-a+0.2,FC_H,zl-zh+0.4),None,(0,0,0),'forecastle step, top Y=%.0f'%(DECK+FC_H))
COL('COL_ForecastleStair_1',(FC_X0-3.75,DECK+1.0,FZC),(7.5,2.0,10.0),None,(0,0,0),'stair tread 1, top Y=26')
COL('COL_ForecastleStair_2',(FC_X0-1.25,DECK+2.0,FZC),(2.8,4.0,10.0),None,(0,0,0),'stair tread 2, top Y=28')
for k,(p,q) in enumerate(FC_SEGS):
    if abs(p[0]-q[0])<0.05 and abs(p[0]-(FC_X0+1.7))<0.8:
        lo,hi=sorted((p[1],q[1]));COL('COL_ForecastleRail_%d'%k,(p[0],FT+1.75,(lo+hi)/2),(1.0,3.5,hi-lo),None,(0,0,0),'forecastle riser rail 3.5 high')
COL('COL_RockBumper',(0,4.0,0),(15.0,8.0,13.0),None,BUMP_O,'rock bumper collider')
COL('COL_PierDeck',(0,3.5,0),(10.0,1.0,PL),None,PIER_O,'pier deck')
for m in('COL_Mast_Main','COL_Mast_Fore'):
    mx,yt=(MAIN_X,165) if 'Main' in m else (FORE_X,126)
    p0=np.array(tiltR((mx,8,0)));p1=np.array(tiltR((mx,yt,0)));d=p1-p0;Lm=np.linalg.norm(d);al=math.atan2(-d[1],d[2])
    COL(m,(mx,(p0[1]+p1[1])/2,(p0[2]+p1[2])/2),(5.0,5.0,Lm),Rx(al),(0,0,0),'mast (optional)')
# ------------------------------------------------------------------ preview-only: sand mound under the hull's high side
mound=Part('PreviewSandMound');MX=list(np.linspace(-150,125,24))
mrings=[];N=None
for x in MX:
    O=[(pt[1:]) for pt in [np.array(tilt((x,p[1],p[0]))) for p in outer_pts(x,201)]]  # (y,z)
    arr=np.array(O);imin=int(np.argmin(arr[:,0]));seq=[arr[i] for i in range(imin,-1,-1) if arr[i][0]<=20]
    seq=seq[::max(1,len(seq)//8)]
    taper=min(1.0,min((x+150)/30.0,(125-x)/30.0)+0.05)
    ring=[(s[1],max(0.0,s[0]*taper)) for s in seq]
    ring.append((ring[-1][0]-26.0,0.0));ring.append((ring[0][0],0.0))
    mrings.append(ring)
Nr=min(len(r) for r in mrings)
def resamp(r,n):
    a=np.array(r);idx=np.linspace(0,len(r)-1,n);return [tuple(a[int(round(i))]) for i in idx]
mrings=[r if len(r)==Nr else resamp(r,Nr) for r in mrings]
for xa,ra,xb,rb_ in zip(MX[:-1],mrings[:-1],MX[1:],mrings[1:]):
    for i in range(Nr):
        j=(i+1)%Nr;A=(xa,ra[i][1]-0.0,ra[i][0]);B=(xa,ra[j][1],ra[j][0]);C=(xb,rb_[j][1],rb_[j][0]);D=(xb,rb_[i][1],rb_[i][0])
        mid=(np.array(A)+np.array(C))/2;cen=np.array([xa,np.mean([p[1] for p in ra]),np.mean([p[0] for p in ra])])
        mound.tri(A,B,C,'Sand',want=mid-np.array([mid[0],cen[1],cen[2]]));mound.tri(A,C,D,'Sand',want=mid-np.array([mid[0],cen[1],cen[2]]))
prev['PreviewSandMound']=mound
for n,p in prev.items(): pass
# ------------------------------------------------------------------ write
EMP=[('Spawn',SPAWN),('Tee1',TEE1),('RampStart',RAMPSTART),('CupRef',tuple(CUP))]
geom=dict(objects=[o.out() for o in objs.values()],empties=[dict(name=n,pos=list(map(float,p))) for n,p in EMP],
 cols=cols,preview=[o.out() for o in prev.values()],
 info=dict(deck_end_x=X_DECK_END,deck_edge_hi_at_cabin=HI(-120),deck_edge_lo_at_cabin=LO(-120),f1_origin=list(map(float,F1_ORG)),landing_origin=list(map(float,LAND_ORG)),
  f2_origin=list(map(float,F2_ORG)),f2_yaw_deg=-30.0,f2_heading=[-0.5,0,math.sqrt(3)/2],pier_origin=list(map(float,PIER_O)),bumper_origin=list(map(float,BUMP_O)),
  cabin=dict(outer_x=[x0,x1],outer_z=[z0,z1],wall=wt,wall_h=wh,peak_h=CAB['peak'],interior_h_eaves=wh,door=dict(x=DOORX,w=DOOR_W,h=DOOR_H)),
  platform=dict(x=[PX0,PX1],z=[PZ0,PZ1]),castle=dict(raise_studs=CASTLE_H,full_height_x=[X0,CAS_X0],taper_to_x=CAS_X1,low_side_open_x=list(GAPC)),forecastle=dict(x0=FC_X0,x1=X_DECK_END,top_y=FT,height=FC_H,stair_z=FZC,stair_w=10.0,rail_h=3.5),bowsprit=dict(root_hull_local=list(BS0),tip_hull_local=list(BS1),tip_world=list(map(float,BS_TIP))),bumper=dict(lateral=BUMP_LAT,along=BUMP_ALONG),tilt=dict(hull_deg=15,rigging_deg=18),tee_pad=dict(x=[DOORX-6,DOORX+6],z=[TEE_Z0,TEE_Z1])))
json.dump(geom,open(os.path.join(OUT,'geom.json'),'w'))
palette_png(os.path.join(OUT,'palette.png'))
for o in objs.values(): print(o.name,len(o.T),'tris')
print('cols',len(cols),'deck end x',X_DECK_END,'edge at cabin',HI(-120),LO(-120),'f2',F2_ORG,'cup',CUP,'bumper',BUMP_O)
