# Cave Cliff hero mesh generator (Look B). Run: /workspace/.geo/bin/python gen_cave.py <outdir>
# Frame: Roblox frame, +Y up, front (cave mouth, stairs) = +Z (south), +X east, origin = footprint centre at the base (placements.json centre 563.5,66,-606.5).
# Footprint x +-120, z +-70, y 0..150. Parts: cave_cliff_lower, cave_cliff_upper, cave_stairs, cave_water, cave_glow, cave_foliage.
import sys,os,json,math,pickle
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import wreck_lib as L
from wreck_lib import *
CAVEPAL=dict(Rock=(110,92,120),RockDk=(84,70,96),RockLt=(132,114,142),Slate=(70,76,92),RockDeep=(52,44,62),Stone=(150,130,120),StoneDk=(120,102,96),
 Moss=(70,120,70),Vine=(30,100,60),Leaf=(90,170,70),LeafDk=(52,128,62),Amber=(255,190,80),AmberDim=(214,140,50),Iron=(58,56,64),DarkWood=(84,52,34),Plank=(140,90,55),
 Rope=(176,140,86),Water=(30,120,140),WaterLt=(140,210,225),Foam=(230,245,245),Sand=(226,184,128),Trunk=(120,84,56),TrunkDk=(92,62,40),Flower=(235,55,55),Brass=(204,152,62),Cream=(238,222,190))
L.PAL.clear();L.PAL.update(CAVEPAL);L.NAMES[:]=list(L.PAL)
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
rng=np.random.default_rng(77)
# ---------------- layout constants (local frame) ----------------
YC=64.0                      # lower/upper split height
MOUTH=dict(cx=20.0,w=40.0,floor=28.0,h=36.0,z0=-12.0,z1=34.0)      # mouth centre x=+20 (placements: centreX 583.5), floor y=28 (world 94), 40x36
POOL=dict(cx=-80.0,cz=44.0,r=19.0,rim=27.0,floor=44.0,surf=48.4)
WF=dict(x=-80.0,w=13.0,z=8.0,top=103.0,bot=48.4)
def nz(x,z,s=1.0):
    return (math.sin(x*0.071*s+1.3)*math.cos(z*0.083*s+0.4)+0.6*math.sin(x*0.19*s+z*0.11*s+2.0)+0.4*math.cos(x*0.037*s-z*0.17*s+5.0))/2.0
def box_in(x,z,x0,x1,z0,z1,wob=3.0,n=1.0):
    return min(x-x0,x1-x,z-z0,z1-z)+wob*nz(x+11*n,z-7*n,1.3)>0
def Hfun(x,z):
    """cliff height at (x,z) in local frame; 0 = no rock. returns (h,tier)"""
    h=0;t=0
    if box_in(x,z,-112,112,-62,60,3.5,0): h=30+2.5*nz(x,z,2.1);t=0
    if box_in(x,z,-98,100,-58,34,3.5,1) : h=max(h,64+2.5*nz(x,z,2.3));t=1
    if box_in(x,z,70,113,-56,44,3,2): h=max(h,52+2*nz(x,z,2.0))
    if box_in(x,z,-94,90,-54,8,3.5,3): 
        if 104+3*nz(x,z,2.2)>h: h=104+3*nz(x,z,2.2);t=2
    if box_in(x,z,-14,62,-54,34,2.0,4):
        if 98+3*nz(x,z,2.2)>h: h=98+3*nz(x,z,2.2);t=2
    if box_in(x,z,-46,60,-50,-6,3,5):
        if 139+3*nz(x,z,1.9)>h: h=139+3*nz(x,z,1.9);t=3
    if box_in(x,z,-4,44,-46,-18,2.5,6):
        if 147+2*nz(x,z,2.4)>h: h=147+2*nz(x,z,2.4);t=3
    if box_in(x,z,-72,-40,-54,-22,2.5,7):
        if 126+3*nz(x,z,2.0)>h: h=126+3*nz(x,z,2.0);t=3
    # stairs corridor (no rock under the front flight: stairs part fills it)
    if 3<=x<=37 and 30<=z<=70: h=0
    # pool tub in front of the west waterfall wall
    if -112<=x<=-50 and 14<=z<=70:
        d=math.hypot(x-POOL['cx'],z-POOL['cz'])
        if d<POOL['r']: h=POOL['floor']-0.5;t=0
        elif d<POOL['rim']: h=POOL['floor']+7+2*nz(x,z,3.0);t=0
        else: h=30+2.5*nz(x,z,2.1) if box_in(x,z,-112,112,-62,60,3.5,0) else 0;t=0
    return min(h,148.5),t
def in_tunnel(x,z): return MOUTH['cx']-MOUTH['w']/2<=x<=MOUTH['cx']+MOUTH['w']/2 and MOUTH['z0']<=z<=MOUTH['z1']
def arch_top(x):
    u=(x-MOUTH['cx'])/(MOUTH['w']/2+0.5)
    return MOUTH['floor']+24+12*math.sqrt(max(0.0,1-u*u))
# ---------------- prism column builder (closed convex solid, split into side/top/bottom meshes) ----------------
def split_solid(m):
    n=m.face_normals;out=[]
    for sel in(n[:,1]>0.55,n[:,1]<-0.55,np.abs(n[:,1])<=0.55):
        if sel.any():
            s=trimesh.Trimesh(m.vertices,m.faces[sel],process=False);s.remove_unreferenced_vertices();out.append(s)
        else: out.append(None)
    return out   # top, bottom, side
def column(xc,zc,r,y0,y1,nsides=6,taper=0.88,tilt=0.15,seed=0,yclip=None):
    r_=np.random.default_rng(seed);k=nsides;ang0=r_.uniform(0,2*math.pi)
    a=[ang0+2*math.pi*(i+r_.uniform(-0.2,0.2))/k for i in range(k)];rad=[r*r_.uniform(0.85,1.1) for _ in a]
    tx,tz=r_.uniform(-tilt,tilt,2)
    bot=[[xc+ra*math.cos(t),y0,zc+ra*math.sin(t)] for ra,t in zip(rad,a)]
    top=[[xc+ra*taper*math.cos(t),y1+tx*ra*math.cos(t)+tz*ra*math.sin(t)+r_.uniform(-0.6,0.6),zc+ra*taper*math.sin(t)] for ra,t in zip(rad,a)]
    rings=[bot,top]
    if yclip is not None:
        f=(yclip-y0)/(y1-y0);mid=[[b[0]+(t[0]-b[0])*f,yclip,b[2]+(t[2]-b[2])*f] for b,t in zip(bot,top)]
        return ring_solid([bot,mid]),ring_solid([mid,top])
    return ring_solid(rings)
def boulder(c,rad,seed,sub=1,flat=0.75):
    r_=np.random.default_rng(seed);m=icosphere(subdivisions=sub)
    v=m.vertices*np.array(rad)*r_.uniform(0.82,1.14,(len(m.vertices),1))
    v[:,1]*=flat;m=trimesh.Trimesh(v+np.array(c),m.faces,process=False);m.fix_normals();return m
def pick(cols,p,seed=None): return cols[int(rng.choice(len(cols),p=p))]
SIDEC=['Rock','RockDk','RockLt','Slate'];SIDEP=[0.42,0.38,0.10,0.10]
TOPC=['RockLt','Rock','Moss','Slate'];TOPP=[0.42,0.28,0.18,0.12]
DEEPC=['RockDk','RockDeep','Slate'];DEEPP=[0.4,0.35,0.25]
lower=Part('lower');upper=Part('upper');stairs=Part('stairs');water=Part('water');glow=Part('glow');foli=Part('foliage')
def put(part,m,inner=False,tier=0,cut_top=False,cut_bot=False):
    top,bot,side=split_solid(m)
    sc,sp=(DEEPC,DEEPP) if inner else (SIDEC,SIDEP)
    if side is not None: part.add(side,sc[int(rng.choice(len(sc),p=sp))])
    if top is not None and not cut_top:
        tc=TOPC[int(rng.choice(4,p=TOPP))] if tier>=0 else 'Rock';part.add(top,tc)
    if bot is not None and not cut_bot: part.add(bot,'RockDeep')
# ---------------- columns ----------------
cols=[];seed=0
def spawn(x,z,r,fine=False):
    global seed
    h,t=Hfun(x,z)
    if h<=1: return
    seed+=1;y0=0.0;inner=False
    if in_tunnel(x,z): y0=arch_top(x)
    if (MOUTH['cx']-MOUTH['w']/2-7<=x<=MOUTH['cx']+MOUTH['w']/2+7) and MOUTH['z0']-7<=z<=MOUTH['z1']+1 and y0==0: inner=True
    if y0>=h-2: return
    cols.append(dict(x=x,z=z,r=r,y0=y0,h=h,t=t,seed=seed,inner=inner or y0>0))
CELL=8.0
for i in range(-16,17):
    for j in range(-10,10):
        x=i*CELL+rng.uniform(-1.6,1.6);z=j*CELL+rng.uniform(-1.6,1.6)
        if -9<=x<=49 and -17<=z<=39: continue
        spawn(x,z,rng.uniform(5.4,6.6))
FC=4.0
for i in range(-3,14):
    for j in range(-5,11):
        x=i*FC+rng.uniform(-0.8,0.8);z=j*FC+rng.uniform(-0.8,0.8)
        if -9<=x<=49 and -17<=z<=39: spawn(x,z,rng.uniform(2.9,3.5))
for c in cols:
    y0,h=c['y0'],c['h'];tier=c['t']
    m_n=6 if c['r']>4 else 5
    if y0>=YC: m=column(c['x'],c['z'],c['r'],y0,h,m_n,seed=c['seed']);put(upper,m,c['inner'],tier)
    elif h<=YC+4: m=column(c['x'],c['z'],c['r'],y0,h,m_n,seed=c['seed']);put(lower,m,c['inner'],tier)
    else:
        a,b=column(c['x'],c['z'],c['r'],y0,h,m_n,seed=c['seed'],yclip=YC)
        put(lower,a,c['inner'],tier,cut_top=True);put(upper,b,c['inner'],tier,cut_bot=True)
# tunnel floor + back wall (lower part), flat stone floor
lower.add(box(MOUTH['w']+1,MOUTH['floor'],MOUTH['z1']-MOUTH['z0']+2,(MOUTH['cx'],MOUTH['floor']/2,(MOUTH['z0']+MOUTH['z1'])/2)),'StoneDk')
lower.add(box(MOUTH['w']+0.5,36,3.0,(MOUTH['cx'],MOUTH['floor']+18,MOUTH['z0']-1.3)),'RockDeep')
# perimeter foot boulders (break the straight base edge)
for k in range(46):
    t=2*math.pi*k/46+rng.uniform(-.05,.05)
    x=106*math.cos(t);z=56*math.sin(t)
    if 3<=x<=37 and z>25: continue
    if -112<=x<=-50 and z>14: continue
    lower.add(boulder((x+rng.uniform(-3,3),13,z+rng.uniform(-3,3)),(rng.uniform(8,11),rng.uniform(11,14),rng.uniform(8,11)),900+k,1,0.9),['Rock','RockDk','RockLt'][k%3])
# backing wall for the waterfall + lip boulder (upper part)
upper.add(box(WF['w']+6,WF['top']-POOL['floor']+2,5.0,(WF['x'],(WF['top']+POOL['floor']-2)/2+1,WF['z']-2.0)),'RockDk')
upper.add(boulder((WF['x'],WF['top']+1.5,WF['z']+0.5),(11,5,7),77,1,1.0),'RockLt')
for sx in(-1,1): upper.add(boulder((WF['x']+sx*9.5,WF['top']-6,WF['z']+0.2),(4.2,12,4.6),70+sx,1,1.0),'RockDk')
# arch ring (cut-stone voussoirs) + jambs, protruding from the face z=34
ring=[]
for k in range(13):
    t=math.pi*k/12;ex,ey=(MOUTH['w']/2+2.4)*math.cos(t),(12+2.4)*math.sin(t)
    ring.append((MOUTH['cx']+ex,52+ey,t))
for k,(x,y,t) in enumerate(ring):
    a=math.degrees(t)
    upper.add(box(5.4,4.6,6.2,(x,y,MOUTH['z1']+0.5),(( 0,0,1),a-90)),['Stone','StoneDk','Stone','RockLt'][k%4])
for sx in(-1,1):
    for k in range(4):
        upper.add(box(4.6,6.0,6.2,(MOUTH['cx']+sx*(MOUTH['w']/2+2.3),MOUTH['floor']+3+k*6.2,MOUTH['z1']+0.5)),['StoneDk','Stone'][(k+(sx>0))%2])
upper.add(box(MOUTH['w']+14,3.0,6.4,(MOUTH['cx'],52+14.8+3.0,MOUTH['z1']+0.5)),'StoneDk')      # keystone lintel band
# ---------------- stairs + rails + lantern posts ----------------
NS=20;RUN=2.0;RISE=0.88;SX0,SX1=5.0,35.0
for i in range(NS):
    top=10+RISE*(i+1);z1=70-RUN*i;z0=z1-RUN-0.4
    stairs.add(box(SX1-SX0,top,z1-z0,((SX0+SX1)/2,top/2,(z0+z1)/2)),['Stone','StoneDk','Stone','Stone'][i%4] if i%5 else 'StoneDk')
for sx,xs in((-1,SX0-1.1),(1,SX1+1.1)):
    for k in range(7):
        z=68-k*6.2;yb=10+RISE*((70-z)/RUN)+0.9
        stairs.add(box(1.0,4.0,1.0,(xs,yb+2.0,z)),'DarkWood')
    pts=[(xs,10+RISE*((70-z)/RUN)+3.6,z) for z in(68,68-6.2*6)]
    stairs.add(beam(pts[0],pts[1],0.6,0.6),'Plank')
    stairs.add(beam((xs,pts[0][1]-1.7,pts[0][2]),(xs,pts[1][1]-1.7,pts[1][2]),0.5,0.5),'Rope')
LAN=[]
for sx,xs in((-1,SX0-3.6),(1,SX1+3.6)):
    for z in(64,50,36):
        yb=10+RISE*((70-z)/RUN)+0.2
        stairs.add(box(1.2,6.8,1.2,(xs,yb+3.4,z)),'DarkWood');stairs.add(box(2.2,0.5,2.2,(xs,yb+6.9,z)),'Iron')
        for a,b in((-1,-1),(-1,1),(1,-1),(1,1)): stairs.add(box(0.35,2.6,0.35,(xs+a*0.9,yb+8.4,z+b*0.9)),'Iron')
        stairs.add(frustum(1.5,0.25,(xs,yb+9.8,z),(xs,yb+10.8,z),4),'Iron');LAN.append((xs,yb+8.4,z))
for (x,y,z) in LAN: glow.add(uvsphere(1.15,(x,y,z),8,6),'Amber')
# cave interior glow cards (flush behind the tunnel mouth, above the floor)
gx,gz=MOUTH['cx'],MOUTH['z0']+0.4
for k,(w,y0,y1,c) in enumerate(((30,29.5,50,'AmberDim'),(22,29.5,44,'Amber'),(11,29.5,36,'Amber'))): glow.add(box(w,y1-y0,0.5,(gx,(y0+y1)/2,gz+0.3*k)),c)
glow.add(box(18,0.5,20,(gx,MOUTH['floor']+0.3,gz+12)),'AmberDim')
# ---------------- water: waterfall sheet + pool ----------------
wz=WF['z']+0.9
for k,(dx,w,c,dz) in enumerate(((-4.5,4.0,'Water',0),(0,5.0,'WaterLt',0.35),(4.5,4.0,'Water',0.1))):
    water.add(box(w,WF['top']-WF['bot']+1.0,0.8,(WF['x']+dx,(WF['top']+WF['bot'])/2,wz+dz)),c)
for k in range(5):  # white streaks
    water.add(box(0.9,rng.uniform(10,22),0.5,(WF['x']+rng.uniform(-5,5),rng.uniform(62,94),wz+0.8)),'Foam')
water.add(frustum(POOL['r'],POOL['r'],(POOL['cx'],POOL['surf']-1.2,POOL['cz']),(POOL['cx'],POOL['surf'],POOL['cz']),20),'Water')
water.add(frustum(7.5,7.5,(POOL['cx'],POOL['surf']-0.3,POOL['cz']-POOL['r']+8),(POOL['cx'],POOL['surf']+0.25,POOL['cz']-POOL['r']+8),12),'WaterLt')
for k in range(14):
    t=2*math.pi*k/14;water.add(box(3.4,0.6,1.5,(POOL['cx']+(POOL['r']-0.8)*math.cos(t),POOL['surf']+0.1,POOL['cz']+(POOL['r']-0.8)*math.sin(t)),((0,1,0),-math.degrees(t)+90)),'Foam')
for k in range(6): water.add(box(2.6,0.6,2.0,(WF['x']-6+k*2.4,POOL['surf']+0.3,WF['z']+4.2+rng.uniform(0,1.4)),((0,1,0),rng.uniform(0,60))),'Foam')
# ---------------- foliage: palms, bushes, vine curtains ----------------
def palm(x,z,hgt,lean,seed):
    r_=np.random.default_rng(seed);y=Hfun(x,z)[0]-0.8
    ang=r_.uniform(0,2*math.pi);d=np.array([math.cos(ang)*lean,0,math.sin(ang)*lean])
    pts=[np.array([x,y,z])+d*(t**2)*hgt*0.5+np.array([0,hgt*t,0]) for t in np.linspace(0,1,5)]
    foli.add(tube(pts,2.1,5,1.2),'Trunk',True)
    for k in range(4): foli.add(box(4.2,0.8,4.2,pts[0]+np.array([0,1.2+k*3.0,0]),((0,1,0),k*30)),'TrunkDk')
    cr=pts[-1]
    for k in range(8):
        a=2*math.pi*k/8+r_.uniform(-.2,.2);dd=np.array([math.cos(a),0,math.sin(a)])
        path=[cr+dd*s*15+np.array([0,2.0*math.sin(s*2.2)-s*s*9.5,0]) for s in np.linspace(0,1,5)]
        rg=[]
        for i,p in enumerate(path):
            w=(2.6*math.sin(math.pi*(0.25+0.75*i/4)))*1.0+0.4;side=np.cross(dd,(0,1,0))
            rg.append([p+side*w,p+np.array([0,0.25,0]),p-side*w,p-np.array([0,0.25,0])])
        foli.add(ring_solid(rg),['Leaf','LeafDk'][k%2])
    for k in range(3): foli.add(uvsphere(1.5,cr+np.array([0.8*math.cos(k*2.1),-1.8,0.8*math.sin(k*2.1)]),6,5),'DarkWood')
PALMS=[(-100,18,26,.5),(-100,-26,30,.4),(94,20,28,.5),(-80,-30,30,.4),(-86,-6,28,.3),(80,10,28,.4),(96,-30,28,.4),(75,44,24,.3),(-40,52,22,.3),(50,52,22,.3)]
sx_=[(x,z) for (x,z,_,_) in PALMS]
for k,(x,z,hg,ln) in enumerate(PALMS): 
    if 1<Hfun(x,z)[0]<110: palm(x,z,hg,ln,300+k)
for k in range(70):
    x=rng.uniform(-112,112);z=rng.uniform(-60,62);h,t=Hfun(x,z)
    if h<10 or in_tunnel(x,z) or (0<x<40 and z>26) or (-112<x<-50 and 14<z<70): continue
    if h>110: continue
    foli.add(uvsphere((rng.uniform(3,5.5),rng.uniform(2,3.5),rng.uniform(3,5.5)),(x,h+0.3,z),8,6),['Leaf','LeafDk','Moss'][k%3],True)
VG=[c for c in cols if c['y0']==0 and c['h']>40]
for k in range(40):
    c=VG[int(rng.integers(len(VG)))];x=c['x']+rng.uniform(-2,2);z=c['z']+c['r']*0.9;ln=rng.uniform(8,22);y1=c['h']-0.8
    if z>60 or in_tunnel(x,z+3) or (-100<x<-60 and z>12 and z<24): continue
    foli.add(box(1.6,ln,0.6,(x,y1-ln/2,z)),'Vine')
    for q in range(int(ln//5)+1):
        foli.add(box(rng.uniform(2.4,3.8),rng.uniform(2.2,3.2),0.6,(x+rng.uniform(-1.2,1.2),y1-q*5-1.5,z+0.3),((0,0,1),rng.uniform(-30,30))),['Leaf','LeafDk'][q%2])
    if rng.random()<0.5: foli.add(uvsphere(0.9,(x+1.4,y1-ln*rng.uniform(.2,.8),z+0.7),5,4),'Flower')
# ---------------- export ----------------
parts={'cave_cliff_lower':lower,'cave_cliff_upper':upper,'cave_stairs':stairs,'cave_water':water,'cave_glow':glow,'cave_foliage':foli}
geomdir=os.path.join(OUT,'geom');os.makedirs(geomdir,exist_ok=True);report={};allV={}
for k,p in parts.items():
    g=p.merged();V=np.array(g['verts']);allV[k]=V
    g['verts']=np.round(V,4).tolist()
    json.dump({k:dict(objects=[dict(name=k,verts=g['verts'],tris=g['tris'],uvs=g['uvs'],smooth=g['smooth'])])},open(os.path.join(geomdir,k+'.json'),'w'))
    report[k]=dict(tris=len(g['tris']),bbox=dict(min=np.round(V.min(0),2).tolist(),max=np.round(V.max(0),2).tolist()))
    print(k,len(g['tris']),report[k]['bbox'])
allv=np.concatenate(list(allV.values()));report['_all_bbox']=dict(min=np.round(allv.min(0),2).tolist(),max=np.round(allv.max(0),2).tolist())
report['_columns']=len(cols)
json.dump(report,open(os.path.join(OUT,'box_report.json'),'w'),indent=1)
palette_png(os.path.join(OUT,'cave_palette.png'));json.dump(CAVEPAL,open(os.path.join(OUT,'palette.json'),'w'))
pickle.dump({k:p.merged() for k,p in parts.items()},open(os.path.join(OUT,'assembled_preview.pkl'),'wb'))
print('ALL',report['_all_bbox'],'cols',len(cols))
