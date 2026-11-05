# Pirate Shipwreck hero WRECK generator (Look B, Golden Hour Hideaway). Run: /workspace/.geo/bin/python gen_wreck.py <outdir>
# Ship-local frame L (untilted): +Y up, bow -Z, stern +Z, keel y=0, x across. Final frame W = Rx(+15deg) * L + (0,SHIFT,0)
# (bow up). Origin = hull midship; y=0 is the "waterline" (sand level) and the pad-1 deck top is at y=+10.
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from wreck_lib import *
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
rng=np.random.default_rng(31)
ROLL=15.0                      # list (roll) about the long axis, replaces the sheet's bow-up pitch (bow must sit in the lagoon)
SX,SY,SZ=90/70,60/45,320/220   # art-director size: 90 wide x 320 long x 60 tall hull (built at 70x220x45, scaled per axis)
ZB,ZS=-110.0,110.0;BEAM=35.0;DECK=37.0;PLANK_T=1.0
SCL=np.diag([SX,SY,SZ,1.0]);FIN=Rm((0,1,0),180)      # FIN: bow to +Z (RobloxDevBot placements convention), stern to -Z
ROT_M=FIN@Rm((0,0,1),-ROLL);ROLL_M=Tm((0,DECK*SY,0))@Rm((0,0,1),-ROLL)@Tm((0,-DECK*SY,0));CR,TR=math.cos(math.radians(ROLL)),math.tan(math.radians(ROLL))

# --- pad-1 deck (world frame, level): x +-27 (54 wide), z -152..-68 (84 long, centre 50 studs from the stern end), top y=24
PAD=dict(x0=-27.0,x1=27.0,z0=-152.0,z1=-68.0,top=24.0)
DSC=DECK*SY
SHIFT=(PAD['top']-0.3)-DSC-TR*28.0        # world y shift: tilted deck plane is 0.3 below the pad top at world x=+28 (high side)
def deck_world_y(xw): return SHIFT+DSC+TR*xw      # listed main-deck plane in the world frame (y at world x)
SHIP_M=Tm((0,SHIFT,0))@FIN@ROLL_M@SCL
_t=trimesh.transformations.transform_points([[10.0,DECK,5.0]],SHIP_M)[0];assert abs(_t[1]-deck_world_y(_t[0]))<1e-6
def sstep(t): t=min(max(t,0),1);return t*t*(3-2*t)
def hw(z):
    u=(z-ZB)/(ZS-ZB);b=min(u/0.46,1);w=5+(BEAM-5)*(1-(1-b)**2.2)
    if u>0.72: w-=9*((u-0.72)/0.28)**2
    return w
def yk(z): return 14*max(0,(-40-z)/70)**2
def ysh(z): return 45+3*sstep((-60-z)/50)
def prof(h): return 0.2+0.8*math.sin(h*math.pi/2)**0.7
def S(z,h,side=1):
    y=yk(z)+h*(ysh(z)-yk(z));return np.array([side*hw(z)*prof(h),y,z])
def N(z,h,side=1):
    e=1e-3;dz=(S(z+e,h,side)-S(z-e,h,side));dh=(S(z,min(h+e,1.0005),side)-S(z,max(h-e,0),side))
    n=np.cross(dz,dh);n/=np.linalg.norm(n)
    if n[0]*side<0: n=-n
    return n
Zst=np.linspace(ZB,ZS,29)
hull=Part('wreck_hull')
# ---------------- hull skin: 12 strakes per side, planks with butt joints, 3 broken holes ----------------
NS=13;HB=np.linspace(0,1,NS+1)
HOLES=[(-1,-34,13,0.22,0.58),(1,-62,10,0.30,0.66),(1,8,9,0.18,0.50),(-1,52,8,0.42,0.76)]  # side,zc,halfLen,h_lo,h_hi (L-frame z)
def pieces_for(k,side):
    z=ZB;out=[]
    while z<ZS-1:
        L=rng.uniform(34,62);z1=min(z+L,ZS);
        if ZS-z1<14: z1=ZS
        out.append([z,z1]);z=z1+0.16
    for (s,zc,hl,lo,hi) in HOLES:
        if s!=side: continue
        hm=(HB[k]+HB[k+1])/2
        if not(lo-0.04<=hm<=hi+0.04): continue
        a=zc-hl+rng.uniform(-4,4);b=zc+hl+rng.uniform(-4,4);new=[]
        for p0,p1 in out:
            if p1<=a or p0>=b: new.append([p0,p1]);continue
            if a-p0>3: new.append([p0,a])
            if p1-b>3: new.append([b,p1])
        out=new
    return out
def plank_mesh(z0,z1,h0,h1,side,off,th):
    zs=[z0]+[z for z in Zst if z0+0.5<z<z1-0.5]+[z1];rings=[]
    for z in zs:
        n=N(z,(h0+h1)/2,side);A=S(z,h0,side)+n*off;B=S(z,h1,side)+n*off
        rings.append([A,B,B-n*th,A-n*th])
    return ring_solid(rings)
for side in(-1,1):
    for k in range(NS):
        wale=k in(4,9)
        for (z0,z1) in pieces_for(k,side):
            off=0.55 if wale else (0.18 if k%2 else -0.12)+rng.uniform(-0.06,0.06)
            g=0.006
            m=plank_mesh(z0,z1,HB[k]+g,HB[k+1]-g,side,off,PLANK_T+(0.6 if wale else 0))
            col='DarkWood' if wale else ['Plank','PlankLt','PlankDk','Plank'][int(rng.integers(4))]
            hull.add(m,col)
def strap(z,side,off=0.95,th=0.9,w=0.9):
    rings=[]
    for h in np.linspace(0.04,1.0,9):
        n=N(z,h,side);a=S(z-w,h,side)+n*off;b=S(z+w,h,side)+n*off;rings.append([a,b,b-n*th,a-n*th])
    return ring_solid(rings)
for side in(-1,1):
    for z in np.arange(-84,100,26)+rng.uniform(-2,2):
        hull.add(strap(float(z),side),'DarkWood')
# keel timber
rings=[]
for z in Zst:
    xk=hw(z)*prof(0)*1.02;y=yk(z);rings.append([(-xk,y-0.6,z),(xk,y-0.6,z),(xk,y+1.0,z),(-xk,y+1.0,z)])
hull.add(ring_solid(rings),'DarkWood')
for (sd,zc,hl,lo,hi) in HOLES:
    hull.add(plank_mesh(zc-hl-5,zc+hl+5,lo-0.02,hi+0.02,sd,-(PLANK_T+0.25),0.4),'WoodDeep')
# ribs (inner frames) with stanchion posts rising above the sheer
for zr in np.arange(-98,104,13.5):
    pts=[];
    for side in(1,-1):
        hs=np.linspace(1,0,6) if side==1 else np.linspace(0,1,6)
        for h in hs:
            n=N(zr,h,side);pts.append((S(zr,h,side)-n*(PLANK_T+0.35),n))
    pts=[(p,n) for p,n in pts]
    top=[]
    for idx in(0,-1):
        p,n=pts[idx];top.append(p+np.array([0,1.0+rng.uniform(0,4.5)*(1 if rng.random()<0.75 else 0.2),0]))
    rings=[]
    seq=[top[0]]+[p for p,_ in pts]+[top[1]]
    nrm=[pts[0][1]]+[n for _,n in pts]+[pts[-1][1]]
    for p,n in zip(seq,nrm):
        t=np.array([0,0,1.0]);rings.append([p+t*0.8-n*1.5,p+t*0.8,p-t*0.8,p-t*0.8-n*1.5])
    hull.add(ring_solid(rings),'DarkWood')
# top rails (broken)
for side in(-1,1):
    z=ZB+8
    while z<ZS-8:
        L=rng.uniform(16,38);z1=min(z+L,ZS-6)
        if rng.random()<0.72:
            zs=np.linspace(z,z1,max(3,int((z1-z)/8)+1));rings=[]
            for zz in zs:
                n=N(zz,1.0,side);o=S(zz,1.0,side)+n*0.45+np.array([0,0.12,0]);i=o-n*2.1
                rings.append([o,o+[0,0.9,0],i+[0,0.9,0],i])
            hull.add(ring_solid(rings),'DarkWood')
        z=z1+rng.uniform(6,14)
# ---------------- main deck boards ----------------
def deck_board_set(zlo,zhi,y,ymaxw,colset=('Plank','PlankLt','PlankDk'),miss=0.10,holes_z=(),bw=5.2,margin=1.6,thick=1.0,name='deck'):
    n=int(2*ymaxw/bw)+1;xe=np.linspace(-n*bw/2,n*bw/2,n+1);cnt=0
    for ci in range(n):
        z=zlo+rng.uniform(0,6)
        while z<zhi-1.5:
            z1=min(z+rng.uniform(9,19),zhi)
            if zhi-z1<6: z1=zhi
            zm=(z+z1)/2;h_d=(DECK-yk(zm))/(ysh(zm)-yk(zm));Wd=hw(zm)*prof(min(h_d,1))-margin
            a=max(xe[ci],-Wd);b=min(xe[ci+1],Wd);p=miss
            for hz,hr in holes_z:
                if abs(zm-hz)<hr: p=0.6
            if b-a>1.4 and rng.random()>p:
                hull.add(box(b-a-0.14,thick,z1-z-0.14,((a+b)/2,y-thick/2+rng.uniform(-0.12,0.1),(z+z1)/2)),colset[int(rng.integers(len(colset)))])
            z=z1+0.14
deck_board_set(-84,109,DECK,BEAM,holes_z=[(-34,14),(-62,12),(8,10),(-20,6)])
# forecastle (raised bow deck), fascia and posts
deck_board_set(-101,-85,DECK+5.0,18,miss=0.04,margin=2.2,thick=1.1)
for i in range(3):
    zc=-85.2;hull.add(box(2*(hw(zc)*prof(0.5)-1.9),1.3,0.9,(0,DECK+0.9+i*1.45,zc+0.2)),'Plank' if i%2 else 'PlankDk')
for x in(-15,-7,0,7,15):
    hull.add(box(1.5,5.4,1.5,(x,DECK+2.4,-85.8)),'DarkWood')
# cargo hatch with grate
hz=10.0
for sx,sz,cx,cz in((11,1.2,0,hz-5.1),(11,1.2,0,hz+5.1),(1.2,9,-5.1,hz),(1.2,9,5.1,hz)):
    hull.add(box(sx,1.5,sz,(cx,DECK+0.75,cz)),'DarkWood')
for x in(-3.6,-1.2,1.2,3.6): hull.add(box(0.5,0.5,9.2,(x,DECK+1.1,hz)),'Iron')
# ---------------- stern cabin (z 96..109.6, 36 wide, 17 tall) ----------------
CZ0,CZ1,CX,CH=22.0,38.0,17.0,17.0;RH=2.8
def wall(kind,fixed,a,b,ybase,rows,openings,t=0.9,skip=0.0):
    for r in range(rows):
        y=ybase+r*RH+RH/2;segs=[(a,b)]
        for (o0,o1,r0,r1) in openings:
            if r0<=r<=r1:
                new=[]
                for s0,s1 in segs:
                    if o1<=s0 or o0>=s1: new.append((s0,s1));continue
                    if o0-s0>0.4: new.append((s0,o0))
                    if s1-o1>0.4: new.append((o1,s1))
                segs=new
        for s0,s1 in segs:
            if s1-s0>9 and rng.random()<0.6:
                m=s0+(s1-s0)*rng.uniform(0.35,0.65);pcs=[(s0,m-0.07),(m+0.07,s1)]
            else: pcs=[(s0,s1)]
            for p0,p1 in pcs:
                if rng.random()<skip: continue
                col=['Plank','PlankLt','PlankDk'][int(rng.integers(3))];h=RH-0.14
                if kind=='z': hull.add(box(p1-p0,h,t,((p0+p1)/2,y,fixed)),col)
                else: hull.add(box(t,h,p1-p0,(fixed,y,(p0+p1)/2)),col)
NR=6
win_back=[(-12.5,-7.5,2,3),(-2.5,2.5,2,3),(7.5,12.5,2,3)]
wall('z',CZ1-0.5,-CX,CX,DECK,NR,win_back)
wall('z',CZ0+0.5,-CX,CX,DECK,NR,[(-3,3,0,3)],skip=0.05)
wall('x',-CX+0.5,CZ0,CZ1,DECK,NR,[(CZ0+5.5,CZ0+9.5,2,3)],skip=0.08)
wall('x',CX-0.5,CZ0,CZ1,DECK,NR,[(CZ0+5.5,CZ0+9.5,2,3)],skip=0.0)
for sx in(-1,1):
    for zc in(CZ0+0.5,CZ1-0.5): hull.add(box(1.7,NR*RH+0.4,1.7,(sx*CX,DECK+NR*RH/2,zc)),'DarkWood')
# roof: boards across x, a couple broken/tilted
rz=CZ0-0.8;k=0
while rz<CZ1+0.4:
    w=3.3;col=['PlankDk','Plank','PlankDk'][k%3]
    if k==1: pass  # missing roof board (hole)
    else:
        rots=[((1,0,0),rng.uniform(-6,6))] if k==3 else []
        hull.add(box(2*CX+2.2,0.9,w-0.12,(0,DECK+NR*RH+0.9+(0.3 if k==3 else 0),rz+w/2),*rots),col)
    rz+=w;k+=1
hull.add(box(2*CX+2.6,0.9,1.0,(0,DECK+NR*RH+0.35,CZ0-1.2)),'DarkWood');hull.add(box(2*CX+2.6,0.9,1.0,(0,DECK+NR*RH+0.35,CZ1+0.4)),'DarkWood')
CABIN_TOP=DECK+NR*RH+1.35
# ---------------- bow stem post ----------------
stem=[(0,yk(-110)-1,-109.5),(0,10,-111.5),(0,24,-112.2),(0,ysh(-110)+6,-111.0)]
hull.add(tube(stem,2.6,6,2.1),'DarkWood',smooth=True)
# ---------------- lantern housings (cage), glow globes go in the glow part ----------------
LANT=[(-14,DECK+11.6,-90),(14,DECK+11.6,-90),(-33.4,ysh(-5)+4.0,-5),(33.4,ysh(-5)+4.0,-5),(-18.8,DECK+NR*RH+0.4,CZ0-1.4),(18.8,DECK+NR*RH+0.4,CZ0-1.4),(-18.8,DECK+NR*RH-3.0,CZ1+0.8),(18.8,DECK+NR*RH-3.0,CZ1+0.8)]
for (x,y,z) in LANT:
    hull.add(box(2.2,0.5,2.2,(x,y-1.45,z)),'Iron');hull.add(frustum(1.5,0.25,(x,y+1.55,z),(x,y+2.5,z),4),'Iron')
    for sx in(-1,1):
        for sz in(-1,1): hull.add(box(0.35,2.6,0.35,(x+sx*0.95,y,z+sz*0.95)),'Iron')
    hull.add(box(0.28,1.2,0.28,(x,y+3.0,z)),'Iron')
# lantern support posts / brackets
for (x,y,z) in LANT[:2]: hull.add(box(1.2,y-DECK-2.6,1.2,(x,(y-2.6+DECK)/2,z)),'DarkWood')
for (x,y,z) in LANT[2:4]: hull.add(box(1.2,5.2,1.2,(x*0.97,y-3.5,z)),'DarkWood')
for (x,y,z) in LANT[4:6]: hull.add(box(1.4,y-DECK-2.0,1.4,(x,(y-2.0+DECK)/2+0.0,z)),'DarkWood')
for (x,y,z) in LANT[6:]: hull.add(beam((x*0.9,y-1.6,z-0.4),(x,y-1.6,z),0.6),'DarkWood')
# ---------------- world-frame extras: pad-1 deck (level, flat, empty) ----------------
extra=Part('extra')
px0,px1,pz0,pz1,pt=PAD['x0'],PAD['x1'],PAD['z0'],PAD['z1'],PAD['top']
TH=1.4;NB=11;xs=np.linspace(px0,px1,NB+1)
for i in range(NB):
    brk=pz0+rng.uniform(26,56)           # one staggered seam per board
    for (a,b) in((pz0,brk-0.07),(brk+0.07,pz1)):
        extra.add(box(xs[i+1]-xs[i]-0.16,TH,b-a,((xs[i]+xs[i+1])/2,pt-TH/2,(a+b)/2)),['Plank','PlankLt','Plank','PlankLt'][(i+int(a))%4])
BY=pt-TH-0.9-0.05
for zc in np.linspace(pz0+3,pz1-3,7): extra.add(box(px1-px0+1.6,1.8,1.8,(0,BY,zc)),'DarkWood')
for sx in(px0-0.2,0.0,px1+0.2): extra.add(box(1.8,1.8,pz1-pz0+0.6,(sx,BY,(pz0+pz1)/2)),'DarkWood')
for sx in(px0+2,0,px1-2):
    for zc in np.linspace(pz0+4,pz1-4,5):
        yb=deck_world_y(sx)-0.6
        if BY-0.9-yb>1.5: extra.add(box(2.4,BY-0.9-yb,2.4,(sx,(yb+BY-0.9)/2,zc)),'DarkWood')
yl=deck_world_y(px0)-0.6                                        # low-side skirt + end skirts close the gap under the deck
extra.add(box(0.8,pt-TH-yl,pz1-pz0,(px0-0.2,(yl+pt-TH)/2,(pz0+pz1)/2)),'PlankDk')
for zz in(pz0-0.2,pz1+0.2): extra.add(box(px1-px0,pt-TH-yl,0.8,(0,(yl+pt-TH)/2,zz)),'PlankDk')
PAD_RECT=dict(x=[px0,px1],z=[pz0,pz1],top_y=pt)
# ======================= masts + sails + rigging (ship-local frame) =======================
rig=Part('wreck_rig')
def unit(v): v=np.array(v,float);return v/np.linalg.norm(v)
def mast(p0,d,Lm,r0,r1,sec=8):
    p0=np.array(p0,float);d=unit(d);pts=[p0,p0+d*Lm/2,p0+d*Lm];rig.add(tube(pts,r0,sec,r1),'Plank',smooth=False);return p0,d
def band(p,d,r,w=1.2): rig.add(frustum(r+0.55,r+0.55,p-d*w/2,p+d*w/2,8),'Iron')
def splinters(p,d,r,n=5,seed=0,col='PlankLt'):
    rr=np.random.default_rng(seed);d=unit(d);a=np.cross(d,(0,0,1.0));a=unit(a) if np.linalg.norm(a)>1e-6 else np.array([1.0,0,0]);b=np.cross(d,a)
    for k in range(n):
        t=2*math.pi*k/n+rr.uniform(-.3,.3);off=a*math.cos(t)+b*math.sin(t);base=p+off*r*0.55;ln=rr.uniform(3.5,9.0)
        tip=base+d*ln+off*rr.uniform(-0.6,1.2);rig.add(frustum(r*0.42,0.12,base-d*0.5,tip,4),col)
def yard(c,u,half,r=0.9,col='Plank'):
    u=unit(u);rig.add(tube([c-u*half,c,c+u*half],r,6,r*0.7),col);
    for s in(-1,1): rig.add(frustum(r*0.75,r*0.75,c+u*s*(half*0.55),c+u*s*(half*0.55+0.9),6),'Iron')
def sail(origin,u,v,w,h,seed,cols=4,rows=3,billow=2.2,nrm=None,tear=0.18):
    """patchwork sail: origin = top-left, u across (w), v down (h); patches are thin skewed slabs"""
    rr=np.random.default_rng(seed);u=unit(u);v=unit(v);n=unit(np.cross(u,v)) if nrm is None else unit(nrm)
    g=0.14;th=0.32
    def P(a,b): # a,b in [0,1]
        return origin+u*a*w+v*b*h+n*billow*math.sin(math.pi*a)*math.sin(math.pi*min(b*0.9+0.1,1))
    pat=None
    for r in range(rows):
        for c in range(cols):
            if r>0 and rr.random()<tear: continue
            a0=c/cols+g/w;a1=(c+1)/cols-g/w;b0=r/rows+0.005;b1=(r+1)/rows-0.01
            if r==rows-1: b1=b0+(b1-b0)*rr.uniform(0.35,1.15)
            col=['SailRed','SailCream'][(c+(seed%2))%2]
            if rr.random()<0.22: col={'SailRed':'SailRedDk','SailCream':'SailCreamDk'}[col]
            tp=(a1-a0)*rr.uniform(0.05,0.5) if r==rows-1 else 0.0
            q=[P(a0,b0),P(a1,b0),P(a1-tp,b1),P(a0+tp,b1)]
            top=[x+n*th/2 for x in q];bot=[x-n*th/2 for x in q]
            rig.add(ring_solid([bot,top]),col)
def pennant(p,d,L=14,H=4.5,col='FlagRed'):
    d=unit(d);up=np.array([0,1.0,0]);n=unit(np.cross(d,up));th=0.3
    pa=[p+up*H/2,p+d*L*0.95+up*H*0.9,p+d*L*0.62,p+d*L*0.95-up*H*0.9,p-up*H/2]
    rig.add(ring_solid([[x-n*th/2 for x in pa],[x+n*th/2 for x in pa]]),col)
def rope(pts,r=0.32,sec=4,col='Rope'): rig.add(tube(pts,r,sec),col)
def sag(a,b,s=1.2,n=5):
    a=np.array(a,float);b=np.array(b,float);return [a+(b-a)*t+np.array([0,-s*4*t*(1-t),0]) for t in np.linspace(0,1,n)]
# --- main mast (the landmark): snapped stump + leaning upper section hinged on the break
MAIN_Z=-28.0;ST_LEN=72.0;UP_LEN=66.0
p0,d0=mast((0,DECK+0.4,MAIN_Z),(0,math.cos(math.radians(7)),-math.sin(math.radians(7))),ST_LEN,3.0,2.5,10)
P1=p0+d0*ST_LEN;band(p0+d0*8,d0,3.0);band(P1-d0*6,d0,2.5)
splinters(P1,d0,2.5,6,seed=3)
d2=unit((0.16,0.64,-0.75));b2=P1+np.array([0.6,0.0,-0.5])
mast(b2,d2,UP_LEN,2.3,1.35,10);P2=b2+d2*UP_LEN

def at(p,d,t): return p+unit(d)*t
# main upper section: yards + sails hanging down the lean
for (t,half,sw,sh,sd) in((38,24,48,32,11),(52,15,30,18,12)):
    c=at(b2,d2,t);u=unit(np.cross(d2,(0,0,1.0)));yard(c,u,half)
    sail(c-u*sw/2+(-d2)*0.4,u,-d2,sw,sh,sd,billow=2.8)
band(at(b2,d2,24),d2,2.0);band(at(b2,d2,46),d2,1.7)
# the stump keeps one ragged yard + sail remnant
c=at(p0,d0,38);yard(c,(1,0,0),20);sail(c+np.array([-19,-0.4,0.0]),(1,0,0),(0,-1,0.12),38,24,13,billow=2.0,nrm=(0,0.1,-1))
# main mast stays: from the stump to the bow side rails + loose lines dangling off the break
for sx in(-1,1):
    for dz in(-6,6):
        rope(sag(at(p0,d0,44),(sx*32.5,ysh(MAIN_Z+dz)+0.6,MAIN_Z+dz-3),1.0,6),0.3)
for k,(sx,off) in enumerate(((1,2.5),(-1,-3.0),(1,-5.0))):
    base=at(b2,d2,UP_LEN-6-4*k);end=np.array([sx*(6+8*k),DECK+3+4*k,MAIN_Z-40-8*k])
    rope([base,(base+end)/2+np.array([sx*2,-6,0]),end],0.3)
for sx in(-1,1):
    top=at(p0,d0,50)+np.array([sx*0.8,0,0]);foot=np.array([sx*33.2,ysh(MAIN_Z)+0.4,MAIN_Z])
    for dz in(-5,5): rope([top,(top+foot)/2,foot+np.array([0,0,dz])],0.3)
    for k in range(1,6):
        t=k/6.5;a=top*(1-t)+(foot+np.array([0,0,-5]))*t;b=top*(1-t)+(foot+np.array([0,0,5]))*t;rig.add(beam(a,b,0.45),'RopeDk')
bs0=np.array([0,DECK+17,-92.0]);bsd=unit((0,0.34,-0.94))
# --- foremast (shorter, upright-ish, bare yards + sails)
FZ=-66.0;FL=74.0
f0,fd=mast((0,DECK+0.4,FZ),(0,math.cos(math.radians(3)),-math.sin(math.radians(3))),FL,2.4,1.5,8)
band(at(f0,fd,10),fd,2.4);band(at(f0,fd,36),fd,2.0);band(at(f0,fd,58),fd,1.7)
rig.add(box(4.6,1.4,4.6,at(f0,fd,FL)+np.array([0,0.6,0])),'DarkWood')       # mast cap
for x in(-12,0,12): rope(sag(at(f0,fd,37.0)+np.array([x,-0.6,0]),at(f0,fd,37.0)+np.array([x+3,-9,0.5]),1.0,4),0.3)
for (t,half,sw,sh,sd) in((38,26,52,28,21),(58,17,34,18,22)):
    c=at(f0,fd,t);yard(c,(1,0,0),half);sail(c+np.array([-sw/2,-0.4,0.3]),(1,0,0),(0,-1,0.05),sw,sh,sd,billow=2.8,nrm=(0,0.05,-1))
# crow's nest: ring of little posts + floor
cn=at(f0,fd,50);rig.add(frustum(4.6,4.6,cn-np.array([0,0.7,0]),cn+np.array([0,0.0,0]),8),'DarkWood')
for k in range(8):
    a=2*math.pi*k/8;rig.add(box(0.5,2.6,0.5,cn+np.array([4.4*math.cos(a),1.3,4.4*math.sin(a)])),'DarkWood')
rig.add(frustum(4.7,4.7,cn+np.array([0,2.4,0]),cn+np.array([0,3.0,0]),8),'DarkWood')
# fore shrouds + ratlines
for sx in(-1,1):
    for dz in(-4,4):
        top=at(f0,fd,46)+np.array([sx*0.8,0,dz*0.25]);foot=np.array([sx*33.2,ysh(FZ+dz)+0.4,FZ+dz])
        rope([top,(top+foot)/2+np.array([0,0.2,0]),foot],0.3)
    for k in range(1,7):
        t=k/7;a=at(f0,fd,46)*(1-t)+np.array([sx*33.2,ysh(FZ)+0.4,FZ-4])*t;b=at(f0,fd,46)*(1-t)+np.array([sx*33.2,ysh(FZ)+0.4,FZ+4])*t
        rig.add(beam(a+[sx*0.8,0,0.5*-1],b+[sx*0.8,0,0.5],0.45),'RopeDk')
rope(sag(at(f0,fd,FL-4),bs0+bsd*46,0.8,6),0.3)
for sx in(-1,1): rig.add(box(1.6,12.5,1.6,(sx*2.6,DECK+5+6.2,-92.5)),'DarkWood')           # forestay to bowsprit tip
rope(sag(at(f0,fd,FL-8),(-14,DECK+4,-96),0.6,5),0.3);rope(sag(at(f0,fd,FL-8),(14,DECK+4,-96),0.6,5),0.3)
pennant(at(f0,fd,FL)+np.array([0,2.0,0]),(0.35,0.1,-1.0),L=15,H=5.0,col='FlagRed')
# bowsprit
rig.add(tube([bs0,bs0+bsd*24,bs0+bsd*48],1.8,8,1.0),'Plank')
band(bs0+bsd*14,bsd,1.7);band(bs0+bsd*34,bsd,1.3)
# --- mizzen: short upright stump with torn yard + sail, plain cream pennant
MZ=np.array([0,CABIN_TOP+0.1,(CZ0+CZ1)/2]);m0,md=mast(MZ,(0,1,0.0),44,1.9,1.2,8)
band(at(m0,md,10),md,1.9);splinters(at(m0,md,44),md,1.3,4,seed=7)
c=at(m0,md,30);yard(c,(1,0,0),15,0.8);sail(c+np.array([-14,-0.4,0.0]),(1,0,0),(0,-1,0.0),28,19,31,billow=1.8,nrm=(0,0,1))
pennant(at(m0,md,40)+np.array([0,0.0,0]),(0,0.15,1.0),L=12,H=4.0,col='SailCream')
for sx in(-1,1):
    rope([at(m0,md,36),np.array([sx*8,CABIN_TOP+6,(CZ0+CZ1)/2-1]),np.array([sx*17.6,CABIN_TOP+0.9,CZ0+2.0])],0.3)
# ======================= glow part: lantern globes + cabin window panes =======================
glow=Part('wreck_glow')
for (x,y,z) in LANT: glow.add(uvsphere(1.15,(x,y,z),8,5),'Amber')
for (cx,cy,cz,sx,sz) in [(-10,DECK+RH*2.5+0.1,CZ1-0.9,5.0,0.4),(0,DECK+RH*2.5+0.1,CZ1-0.9,5.0,0.4),(10,DECK+RH*2.5+0.1,CZ1-0.9,5.0,0.4),
                         (-CX+0.9,DECK+RH*2.5+0.1,CZ0+7.5,0.4,4.0),(CX-0.9,DECK+RH*2.5+0.1,CZ0+7.5,0.4,4.0)]:
    glow.add(box(sx,RH*1.7,sz,(cx,cy+0.2,cz)),'Amber')
# ======================= duck figurehead (own pivot: base-centre of the chest, upright, faces -Z) =======================
duck=Part('wreck_duck');DS=1.0
def D(m): return m
dk=[]
def dadd(m,col,sm=True): duck.add(xf(m,Tm((0,0,0))),col,sm)
dadd(uvsphere((8.6,8.8,8.2),(0,8.4,2.0),14,10),'DuckYellow')                       # chest
for k in range(5):                                                                 # jagged feather tufts under the chest
    a=math.radians(-56+28*k);dadd(frustum(2.2,0.25,(7.2*math.sin(a),5.2,2.0-7.4*math.cos(a)),(8.0*math.sin(a),-0.6,2.0-8.2*math.cos(a)),5),'DuckDk',False)
dadd(uvsphere(9.1,(0,20.0,-3.2),18,12),'DuckYellow')                               # head
dadd(uvsphere((5.6,1.9,5.6),(0,17.4,-12.4),12,7),'Beak')                           # upper bill
dadd(uvsphere((4.7,1.2,4.6),(0,15.4,-11.6),10,6),'BeakDk')                         # lower bill
dadd(uvsphere((2.3,2.8,1.4),(4.3,21.6,-11.3),8,6),'EyeWhite');dadd(uvsphere((1.0,1.3,0.7),(4.0,21.2,-12.5),6,4),'Black')
dadd(xf(trimesh.creation.cylinder(3.3,1.0,sections=12),Tm((-4.3,21.2,-11.4))),'Black',False)  # eye patch
duck.add(tube([(-7.2,21.6,-9.6),(-9.2,22.4,-5.0),(-9.3,24.6,-0.5),(-5,28.0,3.2),(3,28.2,3.6),(8.8,25.2,-0.5),(9.0,22.8,-6.0),(7.0,22.0,-9.4)],0.5,4),'Black')   # eye-patch strap around the head
duck.add(box(5.4,1.5,1.6,(-4.4,25.0,-10.6),((0,0,1),-24)),'DarkWood');duck.add(box(4.8,1.4,1.5,(4.4,25.7,-10.4),((0,0,1),20)),'DarkWood')  # grumpy brows
duck.add(frustum(4.3,4.5,(0,28.6,-4.6),(0,31.9,-4.6),10),'Navy');duck.add(frustum(4.8,4.8,(0,31.5,-4.6),(0,32.1,-4.6),10),'Navy')
duck.add(frustum(4.6,4.6,(0,28.9,-4.6),(0,29.9,-4.6),10),'Cream');duck.add(box(5.2,0.5,3.4,(0,28.8,-9.4),((1,0,0),-12)),'Navy')
duck.add(uvsphere(0.8,(0,30.2,-9.5),6,4),'Brass')
for off,rx,sg in((12.2,8.6,0.9),(10.4,8.5,1.3)):                                    # neck rope (2 loops, sagging at the front)
    ang=np.linspace(0,2*math.pi,17);duck.add(tube([(rx*math.sin(a),off-sg*max(0,-math.cos(a)),1.8-8.4*math.cos(a)) for a in ang],0.8,4),'Rope')
DUCK_PIVOT_L=np.array([0.0,DECK-9.0,-111.5])      # ship-local mount point (chest base) of the duck

# ======================= assemble + export =======================
BIN=os.path.join(OUT,'geom');os.makedirs(BIN,exist_ok=True)
SC=np.diag([DS,DS,DS,1.0])
parts={}
h=hull.merged(SHIP_M);e=extra.merged()
off=len(h['verts']);hh=dict(verts=h['verts']+e['verts'],tris=h['tris']+[[a+off,b+off,c+off] for a,b,c in e['tris']],uvs=h['uvs']+e['uvs'],smooth=h['smooth']+[True]*len(e['tris']),face_mat=h['face_mat']+e['face_mat'])
parts['wreck_hull']=dict(g=hh,pivot=[0,0,0],kind='hull+deck+cabin+pad deck+rock mound',budget=18000)
parts['wreck_rig']=dict(g=rig.merged(SHIP_M),pivot=[0,0,0],kind='masts+sails+rigging',budget=12000)
parts['wreck_glow']=dict(g=glow.merged(SHIP_M),pivot=[0,0,0],kind='lantern globes + window panes (glow: Neon or PointLight)',budget=2000)
dm=duck.merged(SC);dpiv=SHIP_M@np.append(DUCK_PIVOT_L,1.0)
parts['wreck_duck']=dict(g=dm,pivot=dpiv[:3].tolist(),kind='rubber-duck figurehead (own pivot: chest base)',budget=3000,rot_deg=[0,180,-ROLL])
# duck preview copy in wreck frame
dprev=duck.merged(Tm(dpiv[:3])@ROT_M@SC)
import pickle
pickle.dump(dict(hull=parts['wreck_hull']['g'],rig=parts['wreck_rig']['g'],glow=parts['wreck_glow']['g'],duck=dprev),open(os.path.join(OUT,'assembled_preview.pkl'),'wb'))
report={}
allV={}
for k,p in parts.items():
    g=p['g'];V=np.array(g['verts']);
    if k=='wreck_duck': Vw=np.array(dprev['verts'])
    else: Vw=V
    bb=dict(min=np.round(Vw.min(0),2).tolist(),max=np.round(Vw.max(0),2).tolist());allV[k]=Vw
    report[k]=dict(tris=len(g['tris']),verts=len(g['verts']),bbox_wreck_frame=bb,size=np.round(Vw.max(0)-Vw.min(0),2).tolist(),pivot_wreck_frame=p['pivot'],kind=p['kind'],budget=p['budget'])
# clearance check: nothing taller than 3 studs above the pad top within 25 studs (plan) of the pad centre, except the pad deck + its supports
cx,cz=(PAD['x0']+PAD['x1'])/2,(PAD['z0']+PAD['z1'])/2;viol={}
for k in('wreck_hull','wreck_rig','wreck_glow'):
    V=allV[k];m=(np.hypot(V[:,0]-cx,V[:,2]-cz)<=25);viol[k]=round(float(V[m,1].max()-PAD['top']),2) if m.any() else None
report['_pad1_clearance_max_height_above_pad_within_25']=viol
tip=allV['wreck_rig'][:,1].max();_V=allV['wreck_hull'];_bowk=_V[_V[:,2]>140][:,1].min();_m=(np.hypot(_V[:,0]-cx,_V[:,2]-cz)<=25)&(_V[:,1]>PAD['top']+3);print('DBG',_V[_m][:8].round(1).tolist(),int(_m.sum()))
report['_main_mast_tip_y']=round(float(tip),1)
report['_bow_end_lowest_hull_y']=round(float(_bowk),1);report['_hull_min_y']=round(float(allV['wreck_hull'][:,1].min()),1);report['_pad_top']=PAD['top']
json.dump(dict(parts=report,pad=PAD_RECT,list_deg=ROLL,shift_y=SHIFT,duck_assembly=dict(position=np.round(dpiv[:3],3).tolist(),rotation3x3=np.round(ROT_M[:3,:3],6).tolist(),scale_baked=DS)),open(os.path.join(OUT,'box_report.json'),'w'),indent=1)
for k,p in parts.items():
    g=p['g'];V=np.array(g['verts'])
    if k=='wreck_duck': pass
    else: V=V-np.array(p['pivot'])
    json.dump({k:dict(objects=[dict(name=k,verts=V.round(4).tolist(),tris=g['tris'],uvs=g['uvs'],smooth=g['smooth'])])},open(os.path.join(BIN,k+'.json'),'w'))
palette_png(os.path.join(OUT,'wreck_palette.png'))
print(json.dumps(report,indent=1))
