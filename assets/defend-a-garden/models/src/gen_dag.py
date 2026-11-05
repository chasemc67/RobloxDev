# Defend a Garden low-poly generator (box). Roblox frame: +Y up, front = -Z, pivot base centre at origin.
# Writes geom JSON (build_dag.py format) + one palette texture. Run with /workspace/.geo/bin/python
import numpy as np, trimesh, json, math, sys, os
from trimesh.creation import icosphere, cylinder, cone
from trimesh.geometry import align_vectors
from PIL import Image
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
PAL=dict(  # name: rgb 0-255 ; laid out on an 8x8 grid of 32px cells
 LeafGreen=(76,175,80),LeafDark=(46,125,50),Thorn=(104,140,40),Pink=(244,143,177),Yellow=(255,214,0),
 Terracotta=(205,98,52),TerracottaDark=(150,66,34),Soil=(84,56,36),PodBrown=(141,90,52),PodTan=(196,146,92),
 White=(250,250,250),Black=(25,25,30),VineGreen=(110,190,60),Petal=(255,200,20),DiscBrown=(110,70,30),
 Gold=(230,170,40),Lens=(255,245,170),BaseDark=(40,60,40),Lime=(170,220,60),LimeDark=(120,170,40),
 SnailShell=(150,90,210),SnailSwirl=(205,165,240),SnailSkin=(245,225,190),BeetleBlue=(30,80,220),
 BeetleDark=(15,40,130),MoleBrown=(110,70,50),MoleBelly=(200,160,120),NosePink=(240,120,140),
 Claw=(240,230,205),Helmet=(250,190,30),Crown=(255,200,50),Ruby=(210,30,50),Cape=(120,40,170))
NAMES=list(PAL);CELL=32
def uv_of(c):
    i=NAMES.index(c);x,y=i%8,i//8
    return [(x+0.5)/8,1-(y+0.5)/8]
def palette_png(p):
    im=Image.new('RGB',(256,256),(128,128,128))
    for n,c in PAL.items():
        i=NAMES.index(n);x,y=i%8,i//8;im.paste(c,(x*CELL,y*CELL,(x+1)*CELL,(y+1)*CELL))
    im.save(p)
def tf(m,pos=(0,0,0),scale=(1,1,1),d=None,rot=None):
    m=m.copy();m.apply_scale(scale) if np.ndim(scale) else m.apply_scale(scale)
    if rot is not None:
        for ax,a in rot: m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(a),ax))
    if d is not None: m.apply_transform(align_vectors([0,0,1],np.array(d,float)/np.linalg.norm(d)))
    m.apply_translation(pos);return m
def sph(r,pos,sc=(1,1,1),sub=1,**k): return tf(icosphere(sub,r),pos,sc,**k)
def cyl(r,h,pos,d=(0,1,0),sec=12,**k): return tf(cylinder(r,h,sections=sec),pos,d=d,**k)
def cn(r,h,pos,d,sec=8):  # base at pos, tip along d
    d=np.array(d,float);d/=np.linalg.norm(d);return tf(cone(r,h,sections=sec),pos,d=d)
def frustum(r0,r1,y0,y1,sec=16):
    a=np.linspace(0,2*np.pi,sec,endpoint=False);v=[]
    for r,y in((r0,y0),(r1,y1)): v+=[[r*math.cos(t),y,r*math.sin(t)] for t in a]
    v+=[[0,y0,0],[0,y1,0]];f=[]
    for i in range(sec):
        j=(i+1)%sec;f+=[[i,sec+i,sec+j],[i,sec+j,j],[2*sec,i,j],[2*sec+1,sec+j,sec+i]]
    m=trimesh.Trimesh(v,f);m.fix_normals();return m
def tube(pts,r,sec=8,r1=None):
    pts=np.array(pts,float);n=len(pts);r1=r if r1 is None else r1;V=[];F=[]
    T=np.gradient(pts,axis=0);T/=np.linalg.norm(T,axis=1)[:,None]
    u=np.cross(T[0],[0,1,0] if abs(T[0][1])<.9 else [1,0,0]);u/=np.linalg.norm(u)
    for i in range(n):
        if i: u=u-np.dot(u,T[i])*T[i];u/=np.linalg.norm(u)
        w=np.cross(T[i],u);rr=r+(r1-r)*i/(n-1)
        for k in range(sec):
            t=2*np.pi*k/sec;V.append(pts[i]+rr*(math.cos(t)*u+math.sin(t)*w))
    for i in range(n-1):
        for k in range(sec):
            a,b=i*sec+k,i*sec+(k+1)%sec;F+=[[a,b,b+sec],[a,b+sec,a+sec]]
    V+=[pts[0],pts[-1]];c0,c1=len(V)-2,len(V)-1
    for k in range(sec):
        F+=[[c0,(k+1)%sec,k],[c1,(n-1)*sec+k,(n-1)*sec+(k+1)%sec]]
    m=trimesh.Trimesh(np.array(V),F,process=True);m.fix_normals();return m
def obj(name,items):
    V=[];T=[];U=[];MI=[];mats=[]
    for m,c in items:
        if c not in mats: mats.append(c)
        o=len(V);V+=m.vertices.tolist();T+=(m.faces+o).tolist();U+=[uv_of(c)]*len(m.vertices);MI+=[mats.index(c)]*len(m.faces)
    return dict(name=name,verts=V,tris=T,uvs=U,mats=mats,mat_index=MI)
def ring_pts(R,y,n=24,z0=0): return [[R*math.cos(t),y,R*math.sin(t)] for t in np.linspace(0,2*np.pi,n)]
# ---------------- items
def thorn_hedge():
    b=[(sph(1.35,(0,1.45,0),(1,0.95,1),2),'LeafGreen')]
    for k in range(7):
        a=2*np.pi*k/7;b.append((sph(0.75,(1.15*math.cos(a),0.85+0.25*(k%2),1.15*math.sin(a)),sub=1),'LeafGreen' if k%2 else 'LeafDark'))
    b.append((sph(0.7,(0,2.35,0),sub=1),'LeafDark'))
    sp=[];rng=np.random.default_rng(3)
    dirs=[(math.cos(a)*math.cos(e),math.sin(e),math.sin(a)*math.cos(e)) for e,n in((0.15,8),(0.75,5)) for a in np.linspace(0,2*np.pi,n,endpoint=False)+e]+[(0,1,0)]
    for d in dirs:
        d=np.array(d);p=np.array([0,1.4,0])+d*np.array([1.75,1.05,1.75]);sp.append((cn(0.22,0.7,p,d),'Thorn'))
    fl=[]
    for k,(a,e) in enumerate([(0.4,0.3),(1.3,0.6),(2.2,0.2),(3.1,0.55),(4.0,0.25),(4.9,0.6),(5.7,0.35),(0.9,1.1)]):
        d=np.array([math.cos(a)*math.cos(e),math.sin(e),math.sin(a)*math.cos(e)]);p=np.array([0,1.4,0])+d*np.array([1.62,1.08,1.62])
        fl.append((tf(cylinder(0.26,0.12,sections=10),p,d=d),'Pink'));fl.append((sph(0.1,p+d*0.08,sub=0),'Yellow'))
    o=[obj('Bush',b),obj('Thorns',sp),obj('Flowers',fl)]
    for x in o: x['verts']=(np.array(x['verts'])*[0.835,1,0.835]).tolist()  # PROPS.md 4x4 footprint
    return o
def pea_shooter():
    pot=[(frustum(0.62,0.82,0,1.15),'Terracotta'),(frustum(0.92,0.92,1.08,1.38,16),'TerracottaDark'),(cyl(0.84,0.1,(0,1.31,0),sec=16),'Soil')]
    for k in range(4):
        a=np.pi/4+k*np.pi/2;pot.append((sph(0.45,(0.75*math.cos(a),1.45,0.75*math.sin(a)),(1.5,0.35,0.8),sub=1,rot=[((0,1,0),-math.degrees(a))]),'LeafGreen'))
    head=[(sph(0.72,(0,2.05,0),(1,0.92,1),2),'PodBrown'),(sph(0.5,(0,2.45,0.05),(1,0.45,1),1),'PodTan')]
    for x in(-0.27,0.27):
        head+=[(sph(0.2,(x,2.1,-0.6),(1,1.15,0.6),1),'White'),(sph(0.11,(x,2.08,-0.71),(1,1.1,0.5),1),'Black')]
    pts=[(0,2.6,0.1)]+[(0.32*math.sin(t*2.2),2.6+0.25*t+0.25*math.sin(t*1.6),0.1-0.32*math.cos(t*2.2)+0.32) for t in np.linspace(0.2,2.9,14)]
    end=np.array(pts[-1]);pts+= [tuple(end+np.array([0,0.05*i,-0.17*i])) for i in(1,2,3)]
    e=np.array(pts[-1]);bar=[(tube(pts,0.13,8,0.16),'VineGreen'),(cyl(0.24,0.3,tuple(e+[0,0,-0.1]),d=(0,0,1),sec=12),'VineGreen'),
         (cyl(0.15,0.06,tuple(e+[0,0,-0.27]),d=(0,0,1),sec=10),'LeafDark'),(sph(0.2,tuple(e+[0.15,0.25,0.2]),(1.4,0.3,0.7),sub=1),'LeafGreen')]
    return [obj('Pot',pot),obj('Head',head),obj('Barrel',bar)]
def sunflower_beam():
    base=[(cyl(0.9,0.3,(0,0.15,0),sec=16),'BaseDark'),(cyl(0.96,0.12,(0,0.16,0),sec=16),'Gold'),(cyl(0.45,0.3,(0,0.42,0),sec=12),'Gold'),
          (cyl(0.13,2.2,(0,1.6,0),sec=8),'LeafDark')]
    for s in(-1,1): base.append((sph(0.5,(0.42*s,1.3+0.2*(s>0),0),(1.3,0.25,0.6),1,rot=[((0,0,1),25*s)]),'LeafGreen'))
    hc=np.array([0,2.85,0]);tilt=35;H=[]
    def rt(m): return tf(m,rot=[((1,0,0),-tilt)])  # tilt face up so it reads from above
    for k in range(12):
        a=2*np.pi*k/12;p=np.array([0.78*math.cos(a),0.78*math.sin(a),0.02*(k%2)])
        H.append((tf(sph(0.32,p,(1.45,0.75,0.28),1,rot=[((0,0,1),math.degrees(a))]),rot=[((1,0,0),-tilt)]),'Petal'))
    H+=[(rt(cyl(0.6,0.32,(0,0,0),d=(0,0,1),sec=16)),'DiscBrown'),(rt(cyl(0.45,0.16,(0,0,-0.2),d=(0,0,1),sec=16)),'Gold'),(rt(cyl(0.32,0.14,(0,0,-0.3),d=(0,0,1),sec=16)),'Lens')]
    H=[(m.apply_translation(hc) or m,c) for m,c in H]
    return [obj('Base',base),obj('Head',H)]
# ---------------- pests
def legs(pairs,y,col,span,r=0.05,foot=0.0):
    L=[];R=[]
    for z in pairs:
        for s,lst in((1,R),(-1,L)):
            p=[(s*span*0.35,y,z),(s*span*0.8,y+0.18,z),(s*span,foot,z-0.05)];lst.append((tube(p,r,6),col))
    return L,R
def aphid():
    body=[(sph(0.62,(0,0.78,0.15),(0.95,0.85,1.25),2),'Lime'),(sph(0.25,(0,1.18,0.55),(1,0.6,1),0),'LimeDark')]
    head=[(sph(0.38,(0,0.85,-0.65),sub=1),'Lime')]
    for x in(-0.16,0.16): head+=[(sph(0.11,(x,0.95,-0.97),(1,1,0.6),1),'White'),(sph(0.065,(x,0.94,-1.03),(1,1,0.5),0),'Black')]
    ant=[(tube([(s*0.12,1.15,-0.8),(s*0.3,1.45,-0.95),(s*0.55,1.6,-0.7)],0.035,5),'LimeDark') for s in(-1,1)]
    L,R=legs((-0.35,0.15,0.55),0.55,'LimeDark',0.85)
    return [obj('Body',body),obj('Head',head),obj('Antennae',ant),obj('LegsL',L),obj('LegsR',R)]
def snail():
    foot=[(sph(0.5,(0,0.32,0.15),(1.1,0.64,2.6),2),'SnailSkin'),(tube([(0,0.4,-0.7),(0,0.9,-0.95),(0,1.2,-1.05)],0.33,10,0.3),'SnailSkin')]
    head=[(sph(0.38,(0,1.35,-1.08),sub=1),'SnailSkin')]
    for s in(-1,1):
        tip=(s*0.32,2.05,-1.15);head+=[(tube([(s*0.12,1.55,-1.08),(s*0.25,1.8,-1.12),tip],0.06,6),'SnailSkin'),(sph(0.17,tip,sub=1),'White'),(sph(0.09,(tip[0],tip[1],tip[2]-0.13),(1,1,0.5),0),'Black')]
    shell=[(sph(0.9,(0,1.25,0.45),(0.85,1,1),2),'SnailShell')]
    for s in(-1,1):
        sw=[(s*0.77,1.25+0.55*(1-t)*math.sin(t*9),0.45+0.55*(1-t)*math.cos(t*9)) for t in np.linspace(0,0.85,22)]
        shell.append((tube(sw,0.07,6),'SnailSwirl'))
    return [obj('Foot',foot),obj('Head',head),obj('Shell',shell)]
def beetle():
    shell=[(sph(0.8,(0,0.85,0.25),(1,0.75,1.25),2),'BeetleBlue'),(tube([(0,1.43,-0.6),(0,1.47,0.25),(0,1.2,1.15)],0.04,5),'BeetleDark')]
    head=[(sph(0.42,(0,0.75,-0.8),(1.1,0.85,1),1),'BeetleDark'),
          (tube([(0,0.95,-1.0),(0,1.2,-1.3),(0,1.65,-1.35),(0,1.9,-1.1)],0.17,8,0.05),'BeetleBlue')]
    for x in(-0.22,0.22): head+=[(sph(0.11,(x,0.85,-1.15),(1,1,0.6),1),'White'),(sph(0.06,(x,0.84,-1.21),(1,1,0.5),0),'Black')]
    L,R=legs((-0.45,0.2,0.75),0.55,'BeetleDark',1.05,0.07)
    return [obj('Shell',shell),obj('Head',head),obj('LegsL',L),obj('LegsR',R)]
def mole_parts():
    body=[(sph(0.9,(0,1.05,0),(1,1.05,0.85),2),'MoleBrown'),(sph(0.65,(0,0.95,-0.38),(1,1.1,0.6),1),'MoleBelly')]
    head=[(sph(0.62,(0,1.95,-0.12),(1.05,0.95,0.95),2),'MoleBrown'),(sph(0.25,(0,1.8,-0.68),(1.1,0.8,1),1),'MoleBelly'),(sph(0.12,(0,1.86,-0.9),sub=1),'NosePink'),
          (sph(0.62,(0,2.18,-0.08),(1.12,0.62,1.12),2),'Helmet'),(cyl(0.78,0.08,(0,2.08,-0.08),sec=16),'Helmet'),
          (cyl(0.17,0.16,(0,2.3,-0.72),d=(0,0,1),sec=12),'Gold'),(cyl(0.12,0.06,(0,2.3,-0.82),d=(0,0,1),sec=12),'Lens')]
    for x in(-0.22,0.22): head+=[(sph(0.08,(x,2.0,-0.66),(1,1,0.5),0),'Black'),(cyl(0.07,0.12,(x*1.1,1.6,-0.7),d=(0,1,0),sec=6),'White')]
    arms={}
    for s,n in((-1,'ArmL'),(1,'ArmR')):
        a=[(tube([(s*0.7,1.3,-0.2),(s*1.0,1.0,-0.45),(s*0.85,0.85,-0.75)],0.2,8),'MoleBrown'),(sph(0.25,(s*0.85,0.85,-0.8),sub=1),'MoleBrown')]
        for k in(-1,0,1): a.append((cn(0.07,0.38,(s*0.85+k*0.12,0.8,-0.95),(k*0.2,-0.4,-1)),'Claw'))
        arms[n]=a
    feet=[(sph(0.3,(s*0.45,0.17,-0.25),(1,0.55,1.4),1),'MoleBrown') for s in(-1,1)]
    return body,head,arms,feet
def mole():
    b,h,a,f=mole_parts();return [obj('Body',b),obj('Head',h),obj('ArmL',a['ArmL']),obj('ArmR',a['ArmR']),obj('Feet',f)]
def mole_king():
    b,h,a,f=mole_parts();cr=[(frustum(0.5,0.58,2.5,2.82,16),'Crown')]
    for k in range(5):
        t=2*np.pi*k/5-np.pi/2;p=(0.5*math.cos(t),2.78,-0.08+0.5*math.sin(t));cr.append((cn(0.14,0.38,p,(0,1,0),6),'Crown'));cr.append((sph(0.07,(p[0],p[1]+0.42,p[2]),sub=0),'Ruby'))
    cr.append((sph(0.1,(0,2.66,-0.63),(1,1,0.5),0),'Ruby'))
    cape=[(tube([(0,0.35,0.95-0.05*abs(x)) for x in [0]]+[(0,2.0,0.72)],0.01,4),'Cape')] if False else []
    cp=frustum(1.0,0.75,0.25,1.85,16);cp.vertices[:,2]+=0.25;cp=cp.slice_plane([0,0,0.25],[0,0,1],cap=True)
    cape=[(cp,'Cape'),(cyl(0.12,0.9,(0,1.82,-0.62),d=(1,0,0),sec=8),'Gold')]
    parts=[obj('Body',b),obj('Head',h),obj('Crown',cr),obj('Cape',cape),obj('ArmL',a['ArmL']),obj('ArmR',a['ArmR']),obj('Feet',f)]
    S=1.535  # PROPS.md: 4x4 footprint, 5 tall
    for o in parts: o['verts']=(np.array(o['verts'])*S).tolist()
    return parts
G={'thorn_hedge':thorn_hedge(),'pea_shooter':pea_shooter(),'sunflower_beam':sunflower_beam(),'aphid':aphid(),'snail':snail(),'beetle':beetle(),'mole':mole(),'mole_king':mole_king()}
rep={}
for k,objs in G.items():
    allv=np.vstack([o['verts'] for o in objs]);lo=allv.min(0);hi=allv.max(0);sh=np.array([-(lo[0]+hi[0])/2,-lo[1],-(lo[2]+hi[2])/2])
    for o in objs: o['verts']=(np.array(o['verts'])+sh).round(5).tolist()
    allv=allv+sh;rep[k]=dict(tris=sum(len(o['tris']) for o in objs),size_xyz=(allv.max(0)-allv.min(0)).round(3).tolist(),parts={o['name']:len(o['tris']) for o in objs})
json.dump({k:{'objects':v} for k,v in G.items()},open(os.path.join(OUT,'dag_geom.json'),'w'))
palette_png(os.path.join(OUT,'dag_palette.png'));json.dump(rep,open(os.path.join(OUT,'dag_box_report.json'),'w'),indent=1)
for k,v in rep.items(): print(k,v)
