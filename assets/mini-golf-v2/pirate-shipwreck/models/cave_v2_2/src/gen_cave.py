# Cave Cliff v2 generator. Run: /workspace/.geo/bin/python gen_cave.py <outdir>
# v2: chunky leaning rock slabs, uneven skyline (low west -> high east), warm slate + sandy sun tops, 1.5x mouth, recessed glow, wide white waterfall.
# Frame: Roblox frame, +Y up, front (cave mouth, stairs) = +Z (south), +X east, origin = footprint centre at the base (placements.json centre 563.5,66,-606.5).
# Footprint x +-120, z +-70, y 0..150. Parts: cave_cliff_lower, cave_cliff_upper, cave_stairs, cave_water, cave_glow, cave_foliage.
import sys,os,json,math,pickle
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import wreck_lib as L
from wreck_lib import *
CAVEPAL=dict(Rock=(115,100,92),RockDk=(94,82,76),RockLt=(135,119,110),Slate=(106,94,88),RockDeep=(68,60,56),Sandy=(190,150,110),SandyDk=(171,133,98),
 Stone=(150,130,120),StoneDk=(120,102,96),
 Moss=(70,120,70),Vine=(30,100,60),Leaf=(90,170,70),LeafDk=(52,128,62),Amber=(255,190,80),AmberDim=(214,140,50),Iron=(58,56,64),DarkWood=(84,52,34),Plank=(140,90,55),
 Rope=(176,140,86),Water=(60,150,170),WaterLt=(170,224,236),WhiteWater=(240,250,252),Foam=(250,253,253),Sand=(226,184,128),Trunk=(120,84,56),TrunkDk=(92,62,40),Flower=(235,55,55),Brass=(204,152,62),Cream=(238,222,190),
 GlowOrange=(255,168,38),GlowHot=(255,214,92),GlowDeep=(255,128,28))   # v2_2: rock re-tinted warm neutral (was purple 95,85,105). v2_1: ~2x brighter / more saturated than v2 (255,140,40)/(255,176,70)/(230,100,30)
L.PAL.clear();L.PAL.update(CAVEPAL);L.NAMES[:]=list(L.PAL)
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
rng=np.random.default_rng(91)
SUN=np.array([-0.45,0.75,0.50]);SUN/=np.linalg.norm(SUN)
YC=64.0
MOUTH=dict(cx=20.0,w=60.0,floor=28.0,h=54.0,z0=-30.0,z1=34.0,spring=58.0,arc=24.0)   # 1.5x: 60 wide x 54 tall (was 40x36), floor y=28 (world 94)
POOL=dict(cx=-80.0,cz=36.0,r=19.0,rim=27.0,floor=44.0,surf=48.4)
WF=dict(x=-80.0,w=22.0,z=9.0,top=95.0,bot=48.4,front=17.0)
BX0,BX1,BZ0,BZ1=-119.4,119.4,-69.6,69.6
def nz(x,z,s=1.0):
    return (math.sin(x*0.071*s+1.3)*math.cos(z*0.083*s+0.4)+0.6*math.sin(x*0.19*s+z*0.11*s+2.0)+0.4*math.cos(x*0.037*s-z*0.17*s+5.0))/2.0
def box_in(x,z,x0,x1,z0,z1,wob=3.0,n=1.0):
    return min(x-x0,x1-x,z-z0,z1-z)+wob*nz(x+11*n,z-7*n,1.3)>0
def Hfun(x,z):
    """cliff height at (x,z) in local frame; 0 = no rock. returns (h,tier). Skyline climbs west (low) -> east (high)."""
    h=0;t=0;r=min(max((x+110)/220.0,0.0),1.0)
    if box_in(x,z,-106,106,-58,54,3,0): h=30+2.5*nz(x,z,2.1);t=0
    if box_in(x,z,-96,98,-56,32,3.5,1) : h=max(h,60+16*r+2.5*nz(x,z,2.3));t=1
    if box_in(x,z,-92,92,-52,6,3.5,3):
        v=100+26*r**1.1+3*nz(x,z,2.2)
        if v>h: h=v;t=2
    if box_in(x,z,-16,56,-50,34,2.0,4):
        v=108+3*nz(x,z,2.2)
        if v>h: h=v;t=2
    if box_in(x,z,-30,96,-50,-6,3,5):
        v=124+24*r**1.3+3*nz(x,z,1.9)-9*math.exp(-((x-10)/12.0)**2)
        if v>h: h=v;t=3
    if box_in(x,z,58,94,-48,-14,2.5,6):
        v=146+2*nz(x,z,2.4)
        if v>h: h=v;t=3
    if -5<=x<=45 and 30<=z<=70: h=0               # stairs corridor
    if -112<=x<=-50 and 12<=z<=70:                  # pool tub in front of the west waterfall wall
        d=math.hypot(x-POOL['cx'],z-POOL['cz'])
        if d<POOL['r']: h=POOL['floor']-0.5;t=0
        elif d<POOL['rim']: h=POOL['floor']+7+2*nz(x,z,3.0);t=0
        else: h=30+2.5*nz(x,z,2.1) if box_in(x,z,-106,106,-58,54,3,0) else 0;t=0
    return min(h,146.0),t
def tz_rect(pad=0.0): return (MOUTH['cx']-MOUTH['w']/2-pad,MOUTH['cx']+MOUTH['w']/2+pad,MOUTH['z0']-pad,MOUTH['z1']+pad)
def in_tunnel(x,z):
    a,b,c,d=tz_rect();return a<=x<=b and c<=z<=d
def arch_top(x):
    u=(x-MOUTH['cx'])/(MOUTH['w']/2)
    return MOUTH['spring']+MOUTH['arc']*math.sqrt(max(0.0,1-min(u*u,1.0)))
def rect_dist(x,z,pad=0.0):
    a,b,c,d=tz_rect(pad);return math.hypot(max(a-x,0,x-b),max(c-z,0,z-d))
# ---------------- leaning slab builder ----------------
def slab_rings(xc,zc,rx,rz,y0,y1,k,ang,lean,tilt,seed,fs):
    r_=np.random.default_rng(seed)
    a=[2*math.pi*(i+r_.uniform(-0.22,0.22))/k for i in range(k)];u=[r_.uniform(0.84,1.12) for _ in a]
    ca,sa=math.cos(ang),math.sin(ang)
    P=[(rx*math.cos(t)*w,rz*math.sin(t)*w) for t,w in zip(a,u)];P=[(px*ca-pz*sa,px*sa+pz*ca) for px,pz in P]
    taper=r_.uniform(0.80,0.93);bulge=r_.uniform(0.0,0.07);noise=r_.uniform(-0.7,0.7,k)
    out=[]
    for f in fs:
        s=1-(1-taper)*f+bulge*math.sin(math.pi*f);lx,lz=lean[0]*f**1.3,lean[1]*f**1.3;ring=[]
        for i,(px,pz) in enumerate(P):
            X=xc+px*s+lx;Z=zc+pz*s+lz;Y=y0+(y1-y0)*f
            if f>=0.999: Y+=tilt[0]*px+tilt[1]*pz+noise[i]
            ring.append([min(max(X,BX0),BX1),min(Y,149.4),min(max(Z,BZ0),BZ1)])
        out.append(ring)
    return out
def make_slab(c,clip=None):
    y0,y1=c['y0'],c['h'];fs_all=[0,0.5,1.0]
    kw=dict(xc=c['x'],zc=c['z'],rx=c['rx'],rz=c['rz'],k=c['k'],ang=c['ang'],lean=c['lean'],tilt=c['tilt'],seed=c['seed'])
    if clip is None: return ring_solid(slab_rings(y0=y0,y1=y1,fs=fs_all,**kw))
    fy=(clip-y0)/(y1-y0)
    lo=ring_solid(slab_rings(y0=y0,y1=y1,fs=[0,fy*0.5,fy],**kw));hi=ring_solid(slab_rings(y0=y0,y1=y1,fs=[fy,(fy+1)/2,1.0],**kw))
    return lo,hi
def face_groups(m,inner,base,sandy,topc):
    """split a solid into per-colour sub-meshes by face normal vs the sun"""
    n=m.face_normals;d=n@SUN;out=[]
    def sub(sel,col):
        if sel.any():
            q=trimesh.Trimesh(m.vertices,m.faces[sel],process=False);q.remove_unreferenced_vertices();out.append((q,col))
    bot=n[:,1]<-0.55;top=n[:,1]>0.5;side=~(bot|top)
    sub(bot,'RockDeep')
    sub(top&(d>0.55),sandy);sub(top&(d<=0.55),topc)
    if inner: sub(side,'RockDeep')
    else:
        sub(side&(d>0.45),'RockLt' if base!='RockLt' else 'Rock');sub(side&(d<=-0.15),'RockDk');sub(side&(d>-0.15)&(d<=0.45),base)
    return out
def boulder(c,rad,seed,sub=1,flat=0.75):
    r_=np.random.default_rng(seed);m=icosphere(subdivisions=sub)
    v=m.vertices*np.array(rad)*r_.uniform(0.82,1.14,(len(m.vertices),1))
    v[:,1]*=flat;m=trimesh.Trimesh(v+np.array(c),m.faces,process=False);m.fix_normals();return m
lower=Part('lower');upper=Part('upper');stairs=Part('stairs');water=Part('water');glow=Part('glow');foli=Part('foliage')
def put(part,m,c,cut_top=False,cut_bot=False):
    for q,col in face_groups(m,c['inner'],c['base'],c['sandy'],c['topc']):
        if cut_top and col in ('Sandy','SandyDk','Moss') : continue
        if cut_top and q.face_normals[:,1].mean()>0.5: continue
        if cut_bot and q.face_normals[:,1].mean()<-0.5: continue
        part.add(q,col)
# ---------------- slabs ----------------
cols=[];seed=0
def spawn(x,z,rmaj,rmin,fine=False,hang=False):
    global seed
    h,t=Hfun(x,z)
    if h<=1: return
    seed+=1;y0=0.0
    R=rmaj*1.25
    if not fine:
        if rect_dist(x,z)<R+0.5:
            if h<112: return
            y0=100.0                      # big slab floating on the small ceiling columns above the tunnel
    else:
        if not in_tunnel(x,z): return
        y0=max(arch_top(x+dx) for dx in(-rmaj,0,rmaj))+0.4
        h=min(h,101.0+rng.uniform(-0.4,0.4))
        if y0>=h-2: return
    if y0>=h-3: return
    big=not fine
    if big and h>40: h=min(h+rng.uniform(-8,2.5),146.0)
    mag=min(rng.uniform(0.09,0.20)*(h-y0),15.0) if big else rng.uniform(0.3,1.2)
    la=rng.uniform(0,2*math.pi);lean=(mag*math.cos(la),mag*math.sin(la))
    ts=rng.uniform(0.25,0.65) if big else rng.uniform(0.05,0.2);tb=rng.uniform(0,2*math.pi);tilt=(ts*math.cos(tb),ts*math.sin(tb))
    cols.append(dict(x=x,z=z,rx=rmaj,rz=rmin,k=6 if big and rng.random()<.6 else 5,ang=rng.uniform(0,math.pi),lean=lean,tilt=tilt,y0=y0,h=h,t=t,seed=seed,
      inner=False,fine=fine,base=['Rock','Rock','Slate','RockLt','RockDk'][int(rng.integers(5))],sandy='Sandy' if rng.random()<.7 else 'SandyDk',
      topc=['RockLt','Rock','Moss','Slate'][int(rng.choice(4,p=[.35,.25,.25,.15]))]))
CELL=14.0
for i in range(-9,10):
    for j in range(-5,6):
        x=i*CELL+rng.uniform(-2.5,2.5)+(CELL/2 if j%2 else 0);z=j*CELL+rng.uniform(-2.5,2.5)+3
        spawn(x,z,rng.uniform(9.0,12.0),rng.uniform(6.5,8.8))
FC=5.0
for i in range(-4,15):
    for j in range(-8,9):
        x=i*FC+rng.uniform(-0.6,0.6);z=j*FC+rng.uniform(-0.6,0.6)
        spawn(x,z,rng.uniform(3.3,3.9),rng.uniform(3.1,3.7),fine=True)
def emit(c):
    y0,h=c['y0'],c['h']
    if y0>=YC: put(upper,make_slab(c),c)
    elif h<=YC+4: put(lower,make_slab(c),c)
    else:
        a,b=make_slab(c,YC);put(lower,a,c,cut_top=True);put(upper,b,c,cut_bot=True)
segn=0
for c in cols:
    H=c['h']-c['y0']
    if c['fine'] or H<48: emit(c);continue
    n=max(2,int(round(H/rng.uniform(30,40))));ys=np.linspace(c['y0'],c['h'],n+1);ox=oz=0.0
    for k in range(n):
        segn+=1;d=dict(c);d['seed']=c['seed']*7+k
        d['y0']=ys[k]-(1.8 if k else 0.0);d['h']=ys[k+1]
        if k:
            ox+=rng.uniform(-3.8,3.8);oz+=rng.uniform(-3.8,3.8);ox=max(min(ox,6),-6);oz=max(min(oz,6),-6)
        d['x']=c['x']+ox;d['z']=c['z']+oz;sc_=0.93**k;d['rx']=c['rx']*sc_;d['rz']=c['rz']*sc_
        la=rng.uniform(0,2*math.pi);mg=min(rng.uniform(0.10,0.22)*(d['h']-d['y0']),8.0);d['lean']=(mg*math.cos(la),mg*math.sin(la))
        ts=rng.uniform(0.25,0.65);tb=rng.uniform(0,2*math.pi);d['tilt']=(ts*math.cos(tb),ts*math.sin(tb))
        if k==0: d['y0']=c['y0']
        emit(d)
def core(x0,x1,z0,z1,yb,yt,col='RockDeep'):
    for (ya,yz,part) in ((yb,min(yt,YC-0.3),lower),(max(yb,YC+0.3),yt,upper)):
        if yz-ya>1: part.add(box(x1-x0,yz-ya,z1-z0,((x0+x1)/2,(ya+yz)/2,(z0+z1)/2)),col)
for a in((-96,-6,-40,44,0,27),(46,96,-40,44,0,27),(-6,46,-40,-34,0,27),(-84,-18,-38,22,0,56),(58,86,-38,22,0,56),(-18,58,-38,-34,0,56),
         (-80,-18,-34,-3,0,96),(58,80,-34,-3,0,96),(-18,58,-38,-34,0,96),(-20,86,-36,-12,92,118)): core(*a)
# tunnel: floor, side jambs, back wall (lower part)
M=MOUTH;TL=M['z1']-M['z0']
lower.add(box(M['w']+1,M['floor'],TL+2,(M['cx'],M['floor']/2,(M['z0']+M['z1'])/2)),'StoneDk')
for sx in(-1,1): lower.add(box(5.0,M['spring']-M['floor']+2,TL+2,(M['cx']+sx*(M['w']/2+2.4),(M['spring']+M['floor'])/2+1,(M['z0']+M['z1'])/2)),'RockDeep')
lower.add(box(M['w']+5,M['spring']-M['floor']+M['arc'],3.0,(M['cx'],M['floor']+(M['spring']-M['floor']+M['arc'])/2,M['z0']-1.3)),'RockDeep')
# perimeter foot boulders (break the straight base edge)
for k in range(40):
    t=2*math.pi*k/40+rng.uniform(-.05,.05)
    x=104*math.cos(t);z=54*math.sin(t)
    if -8<=x<=48 and z>25: continue
    if -112<=x<=-50 and z>14: continue
    lower.add(boulder((x+rng.uniform(-3,3),13,z+rng.uniform(-3,3)),(rng.uniform(8,11),rng.uniform(11,14),rng.uniform(8,11)),900+k,1,0.9),['Rock','RockDk','RockLt'][k%3])
# backing wall for the waterfall (deep enough to hide any slab bulge), lip boulder (upper part)
WZ0,WZ1=WF['z']-7.0,WF['front']-1.0
upper.add(box(WF['w']+8,WF['top']-POOL['floor']-0.5,WZ1-WZ0,(WF['x'],(WF['top']+POOL['floor']+0.5)/2,(WZ0+WZ1)/2)),'RockDk')
upper.add(boulder((WF['x'],WF['top']+0.8,WF['front']-3.0),(WF['w']/2+3,4.2,5.5),77,1,1.0),'RockLt')
for sx in(-1,1): upper.add(boulder((WF['x']+sx*(WF['w']/2+5),WF['top']-9,WF['front']-4.5),(5,14,6),70+sx,1,1.0),'Rock')
# arch ring (cut-stone voussoirs) + jambs, protruding from the face z=34
ring=[]
for k in range(17):
    t=math.pi*k/16;ex,ey=(M['w']/2+2.4)*math.cos(t),(M['arc']+2.4)*math.sin(t)
    ring.append((M['cx']+ex,M['spring']+ey,t))
for k,(x,y,t) in enumerate(ring):
    a=math.degrees(t)
    upper.add(box(6.0,5.0,6.2,(x,y,M['z1']+0.5),((0,0,1),a-90)),['Stone','StoneDk','Stone','RockLt'][k%4])
for sx in(-1,1):
    for k in range(5):
        (lower if M['floor']+3+k*6.4<YC else upper).add(box(5.0,6.2,6.2,(M['cx']+sx*(M['w']/2+2.5),M['floor']+3.1+k*6.4,M['z1']+0.5)),['StoneDk','Stone'][(k+(sx>0))%2])
upper.add(box(M['w']+16,3.2,6.4,(M['cx'],M['spring']+M['arc']+2.4+4.0,M['z1']+0.5)),'StoneDk')      # keystone lintel band
# ---------------- stairs + rails + lantern posts ----------------
NS=20;RUN=2.0;RISE=0.88;SX0,SX1=0.0,40.0
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
# cave interior glow: recessed light cards + a hot floor pool set deep at the back of the 64-stud tunnel (nothing near the mouth, so it never reads as a door)
gx=MOUTH['cx'];gz=MOUTH['z0']
# v2_2 staggered layout: 7 separate cards, clearly different depths (z0+4 .. z0+30 = 26 studs of tunnel), distinct x slots with 2-5 stud gaps so dark rock shows between them,
# NO backdrop panels / big floor slab. Each card floats at y floor+0.9 over its own thin base pad (top floor+0.55, 0.35 gap). Back wall face is z0+0.2 (nearest card 3.7 off it).
glow_cards=[(-21,3.2,14,4,'GlowOrange'),(-12,4.4,22,17,'GlowHot'),(-4.5,2.6,10,9,'GlowDeep'),(4,3.6,18,26,'GlowOrange'),(12,2.8,26,13,'GlowDeep'),(20,4.0,12,21,'GlowHot'),(25.5,3.0,16,7,'GlowOrange')]
for (dx,w,hh,dz,c) in glow_cards:
    glow.add(box(w,hh,0.5,(gx+dx,MOUTH['floor']+0.9+hh/2,gz+dz)),c)
    glow.add(box(w+1.4,0.4,2.0,(gx+dx,MOUTH['floor']+0.35,gz+dz)),'GlowDeep')
for sx in(-1,1): glow.add(uvsphere(1.5,(gx+sx*12,MOUTH['floor']+20,gz+22),8,6),'GlowHot')
# ---------------- water: wide white waterfall sheet + pool ----------------
wz=WF['front']-0.2;th=1.5;wtop=WF['top']+0.5;wh=wtop-WF['bot']
for dx,w,c,dz in((-WF['w']*0.36,WF['w']*0.26,'Foam',0),(0,WF['w']*0.52,'WhiteWater',0.5),(WF['w']*0.36,WF['w']*0.26,'Foam',0.15)):
    water.add(box(w,wh,th,(WF['x']+dx,(wtop+WF['bot'])/2,wz+dz)),c)
for k in range(14):  # bright foam streaks standing proud of the sheet
    ln=rng.uniform(12,30);water.add(box(rng.uniform(1.0,2.2),ln,0.5,(WF['x']+rng.uniform(-WF['w']*0.42,WF['w']*0.42),rng.uniform(WF['bot']+ln/2+4,wtop-ln/2-1),wz+1.3)),'Foam')
for k in range(7): water.add(uvsphere((rng.uniform(2.5,4.2),rng.uniform(1.4,2.2),rng.uniform(2.5,4.0)),(WF['x']+rng.uniform(-WF['w']/2,WF['w']/2),WF['bot']+1.0,WF['front']+1.5+rng.uniform(0,2.6)),8,6),'Foam')
water.add(box(WF['w']+3,0.5,1.7,(WF['x'],POOL['surf']+0.35,WF['front']+0.45)),'Foam')   # v2_2 foam strip where the sheet meets the pool (bottom surf+0.1, 0.1 above pool top)
water.add(frustum(POOL['r'],POOL['r'],(POOL['cx'],POOL['surf']-1.2,POOL['cz']),(POOL['cx'],POOL['surf'],POOL['cz']),20),'Water')
water.add(frustum(8.5,8.5,(POOL['cx'],POOL['surf']-0.3,POOL['cz']-POOL['r']+9),(POOL['cx'],POOL['surf']+0.25,POOL['cz']-POOL['r']+9),12),'WaterLt')
for k in range(14):
    t=2*math.pi*k/14;water.add(box(3.4,0.6,1.5,(POOL['cx']+(POOL['r']-0.8)*math.cos(t),POOL['surf']+0.1,POOL['cz']+(POOL['r']-0.8)*math.sin(t)),((0,1,0),-math.degrees(t)+90)),'Foam')
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
PALMS=[(-96,26,26,.5),(-96,-26,28,.4),(92,24,28,.5),(-82,-20,30,.4),(-60,-8,28,.3),(70,18,26,.4),(98,-30,28,.4),(75,44,24,.3),(-50,50,22,.3),(60,50,22,.3),(-30,-30,30,.4),(40,-34,26,.3)]
sx_=[(x,z) for (x,z,_,_) in PALMS]
for k,(x,z,hg,ln) in enumerate(PALMS): 
    if 1<Hfun(x,z)[0]<118 and Hfun(x,z)[0]+hg+9<147 and rect_dist(x,z,2)>1: palm(x,z,hg,ln,300+k)
for k in range(120):
    x=rng.uniform(-112,112);z=rng.uniform(-60,62);h,t=Hfun(x,z)
    if h<10 or in_tunnel(x,z) or rect_dist(x,z,3)<1 or (-5<x<45 and z>26) or (-112<x<-50 and 12<z<70): continue
    if h>118: continue
    foli.add(uvsphere((rng.uniform(3,5.5),rng.uniform(2,3.5),rng.uniform(3,5.5)),(x,h+0.3,z),8,6),['Leaf','LeafDk','Moss'][k%3],True)
VG=[c for c in cols if c['y0']==0 and c['h']>40 and not c['fine']]
for k in range(34):
    c=VG[int(rng.integers(len(VG)))];x=c['x']+rng.uniform(-3,3);z=c['z']+max(c['rx'],c['rz'])*0.55;ln=rng.uniform(8,22);y1=c['h']-1.0
    if z>58 or rect_dist(x,z,4)<2 or (-100<x<-60 and 12<z<26) or abs(x-WF['x'])<18 and z<24: continue
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
