# Shared helpers for the Pirate Shipwreck wreck generator (box, trimesh). Roblox frame: +Y up, front = -Z, studs.
import numpy as np, trimesh, math, json
from trimesh.creation import icosphere
from trimesh.geometry import align_vectors
PAL=dict(
 # wood / rope
 Plank=(140,90,55),PlankDk=(118,74,45),DarkWood=(84,52,34),Trunk=(120,84,56),TrunkDk=(92,62,40),Rope=(176,140,86),
 # palm / plants
 PalmGreen=(60,150,60),PalmGreenDk=(48,124,52),PalmGreenLt=(90,170,70),Coconut=(120,75,40),CoconutDk=(92,56,30),
 PlantGreen=(70,170,70),PlantGreenDk=(52,138,58),PlantGreenLt=(104,190,84),
 # bone / hats / coat
 Bone=(240,232,210),BoneDk=(214,204,178),BoneShade=(188,176,150),HatDark=(58,46,40),HatDarkLt=(78,64,54),Brass=(204,152,62),
 CoatRed=(196,60,50),CoatRedDk=(160,44,40),Black=(40,34,32),EyeWhite=(250,245,235),
 # metal
 Bronze=(150,110,50),BronzeDk=(118,84,38),BronzeLt=(176,134,64),Iron=(70,66,64),IronLt=(98,94,90),Steel=(156,152,146),SteelDk=(120,116,110),
 # flytrap
 JawRed=(200,60,70),JawRedDk=(166,44,52),SockRed=(196,60,50),SockCream=(238,222,190),BootBrown=(92,58,36),BootSole=(52,34,24),Tooth=(238,222,190),
 # croc / mud
 CrocGreen=(80,140,60),CrocDk=(60,112,50),CrocLt=(112,168,76),CrocBelly=(214,200,140),Mud=(110,78,50),MudDk=(86,60,40),MudLt=(132,98,64),
 # treasure
 Gold=(255,200,60),GoldDk=(224,162,34),GoldLt=(255,224,110),GemBlue=(60,130,200),GemRed=(200,50,60),Beak=(238,128,38),
 # ground / rock (warm neutral, matches cave_v2_2)
 Rock=(115,100,92),RockDk=(94,82,76),RockLt=(135,119,110),Sand=(226,184,128),SandDk=(200,160,106))
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
