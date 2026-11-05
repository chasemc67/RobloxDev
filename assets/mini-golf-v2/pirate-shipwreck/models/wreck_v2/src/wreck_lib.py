# Shared helpers for the Pirate Shipwreck wreck generator (box, trimesh). Roblox frame: +Y up, front = -Z, studs.
import numpy as np, trimesh, math, json
from trimesh.creation import icosphere
from trimesh.geometry import align_vectors
PAL=dict(Plank=(140,90,55),PlankLt=(160,108,66),PlankDk=(118,74,45),DarkWood=(84,52,34),WoodDeep=(52,32,22),
 SailCream=(238,222,190),SailCreamDk=(214,196,160),SailRed=(196,60,50),SailRedDk=(168,46,40),
 DuckYellow=(255,205,40),DuckDk=(240,186,30),Beak=(238,128,38),BeakDk=(205,100,30),Black=(30,28,34),EyeWhite=(250,245,235),
 Slate=(70,76,92),Rock=(110,92,120),RockDk=(84,70,96),RockLt=(132,114,142),Rope=(176,140,86),RopeDk=(132,98,60),
 Amber=(255,190,80),Iron=(58,56,64),Brass=(204,152,62),FlagRed=(235,55,55),Navy=(40,44,66),Cream=(238,222,190))
NAMES=list(PAL);CELL=32
def uv_of(c):
    i=NAMES.index(c);x,y=i%8,i//8;return [(x+0.5)/8,1-(y+0.5)/8]
def palette_png(p):
    from PIL import Image
    im=Image.new('RGB',(256,256),(128,128,128))
    for n,c in PAL.items():
        i=NAMES.index(n);x,y=i%8,i//8;im.paste(c,(x*CELL,y*CELL,(x+1)*CELL,(y+1)*CELL))
    im.save(p)
def Rm(axis,deg):
    return trimesh.transformations.rotation_matrix(math.radians(deg),axis)
def Tm(p): return trimesh.transformations.translation_matrix(p)
def xf(m,*mats):
    m=m.copy()
    for M in mats: m.apply_transform(M)
    return m
def box(sx,sy,sz,c=(0,0,0),*rots):
    """box centred at c with optional rotations (applied about its own centre, in order)"""
    m=trimesh.creation.box(extents=(sx,sy,sz))
    for ax,a in rots: m.apply_transform(Rm(ax,a))
    m.apply_translation(c);return m
def beam(p0,p1,w,h=None,up=(0,1,0)):
    """rectangular beam from p0 to p1, cross-section w (across) x h (along up-ish)"""
    p0=np.array(p0,float);p1=np.array(p1,float);h=w if h is None else h
    d=p1-p0;L=np.linalg.norm(d);d/=L
    a=np.cross(d,up);
    if np.linalg.norm(a)<1e-6: a=np.cross(d,(1,0,0))
    a/=np.linalg.norm(a);b=np.cross(d,a)
    R=np.eye(4);R[:3,0]=a;R[:3,1]=b;R[:3,2]=d
    m=trimesh.creation.box(extents=(w,h,L));m.apply_transform(R);m.apply_translation((p0+p1)/2);return m
def uvsphere(r,c=(0,0,0),lon=12,lat=8):
    if np.isscalar(r): r=(r,r,r)
    V=[[0,r[1],0]]
    for i in range(1,lat):
        t=math.pi*i/lat
        for j in range(lon):
            p=2*math.pi*j/lon;V.append([r[0]*math.sin(t)*math.cos(p),r[1]*math.cos(t),r[2]*math.sin(t)*math.sin(p)])
    V.append([0,-r[1],0]);F=[]
    for j in range(lon): F.append([0,1+(j+1)%lon,1+j])
    for i in range(lat-2):
        for j in range(lon):
            a=1+i*lon+j;b=1+i*lon+(j+1)%lon;F+=[[a,b,b+lon],[a,b+lon,a+lon]]
    last=len(V)-1;base=1+(lat-2)*lon
    for j in range(lon): F.append([last,base+j,base+(j+1)%lon])
    m=trimesh.Trimesh(np.array(V)+np.array(c),F,process=False);m.fix_normals();return m
def frustum(r0,r1,p0,p1,sec=8,rot0=0.0):
    """tapered prism from p0 to p1, end caps (no centre verts needed: fan)"""
    p0=np.array(p0,float);p1=np.array(p1,float);d=p1-p0;L=np.linalg.norm(d);d/=L
    a=np.cross(d,(0,1,0))
    if np.linalg.norm(a)<1e-6: a=np.cross(d,(1,0,0))
    a/=np.linalg.norm(a);b=np.cross(d,a);V=[];F=[]
    for r,p in((r0,p0),(r1,p1)):
        for k in range(sec):
            t=2*math.pi*k/sec+rot0;V.append(p+r*(math.cos(t)*a+math.sin(t)*b))
    V+=[p0,p1]
    for k in range(sec):
        j=(k+1)%sec;F+=[[k,sec+k,sec+j],[k,sec+j,j],[2*sec,k,j],[2*sec+1,sec+j,sec+k]]
    m=trimesh.Trimesh(np.array(V),F,process=False);m.fix_normals();return m
def tube(pts,r,sec=4,r1=None):
    pts=np.array(pts,float);n=len(pts);r1=r if r1 is None else r1;V=[];F=[]
    T=np.gradient(pts,axis=0);T/=np.linalg.norm(T,axis=1)[:,None]
    u=np.cross(T[0],[0,1,0] if abs(T[0][1])<.9 else [1,0,0]);u/=np.linalg.norm(u)
    for i in range(n):
        if i: u=u-np.dot(u,T[i])*T[i];u/=np.linalg.norm(u)
        w=np.cross(T[i],u);rr=r+(r1-r)*i/(n-1)
        for k in range(sec):
            t=2*np.pi*k/sec+0.7854;V.append(pts[i]+rr*(math.cos(t)*u+math.sin(t)*w))
    for i in range(n-1):
        for k in range(sec):
            a,b=i*sec+k,i*sec+(k+1)%sec;F+=[[a,b,b+sec],[a,b+sec,a+sec]]
    V+=[pts[0],pts[-1]];c0,c1=len(V)-2,len(V)-1
    for k in range(sec): F+=[[c0,(k+1)%sec,k],[c1,(n-1)*sec+k,(n-1)*sec+(k+1)%sec]]
    m=trimesh.Trimesh(np.array(V),F,process=False);m.fix_normals();return m
def ring_solid(rings):
    """closed solid from a list of equal-length closed polygon rings (convex-ish), fan caps"""
    rings=[np.array(r,float) for r in rings];m=len(rings[0]);V=np.concatenate(rings);F=[]
    for i in range(len(rings)-1):
        for j in range(m):
            a=i*m+j;b=i*m+(j+1)%m;F+=[[a,b,b+m],[a,b+m,a+m]]
    for j in range(1,m-1):
        F.append([0,j+1,j]);o=(len(rings)-1)*m;F.append([o,o+j,o+j+1])
    t=trimesh.Trimesh(V,F,process=False);t.fix_normals();return t
class Part:
    def __init__(s,name): s.name=name;s.items=[]
    def add(s,m,col,smooth=False):
        if isinstance(m,(list,tuple)):
            for x in m: s.add(x,col,smooth)
            return
        s.items.append((m,col,smooth))
    def faces(s): return sum(len(m.faces) for m,_,_ in s.items)
    def merged(s,M=None):
        V=[];T=[];U=[];SM=[];MT=[];n=0
        for m,c,sm in s.items:
            v=m.vertices.copy()
            if M is not None: v=trimesh.transformations.transform_points(v,M)
            V+=v.tolist();T+=(m.faces+n).tolist();U+=[uv_of(c)]*len(v);SM+=[sm]*len(m.faces);MT+=[c]*len(m.faces);n+=len(v)
        return dict(verts=V,tris=T,uvs=U,smooth=SM,face_mat=MT)
