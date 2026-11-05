"""Pass-4 generators (H7/H9/H14/H17 + dam crest). Coordinates are Roblox studs relative to the export pivot.
Every primitive is convex so fitcheck_pass4 can use exact convex parts. Red/cream bands only on moving parts."""
import math
import bmesh
import sclib as L
from registry_movers import HOLES,DAM

def box(p,m,c,s,yaw=0,roll=0):
    # Roblox yaw about +Y = Blender +Z; Roblox roll about +Z = Blender -Y.
    p.box(m,(s[0],s[2],s[1]),loc=L.R(*c),rot=(0,-roll,yaw))
def ext(p,mat,poly,axis,lo,hi):
    """Convex prism: poly 2D in the plane normal to `axis` ('x': (z,y), 'y': (x,z), 'z': (x,y)), spanning lo..hi on axis."""
    def P(u,v,w):
        if axis=='z':return L.R(u,v,w)
        if axis=='y':return L.R(u,w,v)
        return L.R(w,v,u)
    t=bmesh.new();bot=[t.verts.new(P(u,v,lo)) for u,v in poly];top=[t.verts.new(P(u,v,hi)) for u,v in poly];n=len(poly)
    t.faces.new(bot);t.faces.new(list(reversed(top)))
    for i in range(n):t.faces.new((bot[i],top[i],top[(i+1)%n],bot[(i+1)%n]))
    bmesh.ops.recalc_face_normals(t,faces=t.faces);p.add(mat,t)
def hull2d(pts):
    pts=sorted(set((round(x,9),round(y,9)) for x,y in pts))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];hi=[]
    for q in pts:
        while len(lo)>=2 and cross(lo[-2],lo[-1],q)<=1e-12:lo.pop()
        lo.append(q)
    for q in reversed(pts):
        while len(hi)>=2 and cross(hi[-2],hi[-1],q)<=1e-12:hi.pop()
        hi.append(q)
    return lo[:-1]+hi[:-1]
BAND=('LipRed','LipCream')

# ---------------- H9 windpump
VANE_W=2.4;VANE_TIP=4.1;VANE_D=0.4;HUB_HALF=1.2
def vane_polys():
    """Per vane (pointing -Y at roll 0): radial bands of .6 from the hub square edge (1.2) to the circular tip r 4.1.
    Tip arc vertices every .2 in x, so every blocker strip corner on the r 4.1 circle is a polygon vertex."""
    c=lambda t:math.sqrt(VANE_TIP**2-t*t);edges=[1.2,1.8,2.4,3.0,3.6];out=[]
    for i,(a,b) in enumerate(zip(edges,edges[1:])):out.append((BAND[i%2],[(-1.2,-a),(1.2,-a),(1.2,-b),(-1.2,-b)]))
    tipn=[(-1.2,-3.6),(1.2,-3.6)]+[(t/10,-c(t/10)) for t in range(12,-13,-2)]
    out.append((BAND[(len(edges)-1)%2],tipn))
    return out
def h09_windpump_vanes(p):
    box(p,'Brass',(0,0,0),(2*HUB_HALF,2*HUB_HALF,VANE_D))
    p.cyl('Iron',.45,.36,.3,24,loc=L.R(0,0,.35),rot=(90,0,0),smooth=False)
    for k in range(4):
        a=math.radians(90*k);ca,sa=math.cos(a),math.sin(a)
        for mat,poly in vane_polys():
            ext(p,mat,[(x*ca-y*sa,x*sa+y*ca) for x,y in poly],'z',-VANE_D/2,VANE_D/2)
def h09_windpump_hub(p):
    # Static bearing housing behind the rotor (front face .17 behind the vane back face), mast and roof tower.
    p.cyl('Iron',.45,.45,.88,24,loc=L.R(0,0,-.81),rot=(90,0,0),smooth=False)
    box(p,'Timber',(0,(.45+3.88)/2,-.81),(.4,3.88-.45,.4))
    for x in (-.9,.9):
        for z in (-.85,-2.65):box(p,'Timber',(x,3.88+1.5,z),(.25,3.0,.25))
    for z in (-.85,-2.65):box(p,'Timber',(0,3.88+1.5,z),(3.3,.18,.18),roll=-59);box(p,'Timber',(0,3.88+1.5,z),(3.3,.18,.18),roll=59)
    box(p,'Timber',(0,3.88+3.1,-1.75),(2.3,.2,2.3))
    p.cyl('Brass',.12,.12,1.0,12,loc=L.R(0,3.88+3.7,-1.75),smooth=False)
    box(p,'MintWhite',(0,3.88+4.0,-2.9),(.08,.9,1.9))
    box(p,'Timber',(0,3.88+4.0,-2.0),(.12,.12,1.6))

# ---------------- H14 ore bucket + trestle
SKID_R=10.275
def h14_ore_bucket(p):
    p.cyl('Iron',.28,.28,.09,20,loc=L.R(0,0,0),rot=(90,0,0),smooth=False)
    box(p,'Iron',(0,-.3,0),(.14,.5,.09))
    box(p,'Iron',(0,-3.5,0),(.16,6.1,.16))
    box(p,'Iron',(0,-6.6,0),(2.4,.16,.16))
    for x in (-1.11,1.11):box(p,'Iron',(x,-7.6,0),(.12,2.1,.16))
    for y,m in ((-9.7,'LipRed'),(-9.1,'LipCream'),(-8.5,'LipRed')):box(p,m,(0,y,0),(2.1,.6,1.8))
    box(p,'Iron',(0,-8.1,0),(2.1,.2,1.8))
    for i,(x,z,h,m) in enumerate([(-.55,-.4,.7,'CandyPink'),(.1,.25,.85,'CandyAmber'),(.6,-.35,.6,'CandyPink'),(-.2,.5,.55,'CandyAmber'),(.55,.45,.5,'CandyPink'),(-.65,.35,.45,'CandyAmber')]):
        p.cyl(m,.2,0,h,6,loc=L.R(x,-8.0+h/2,z),rot=(0,(-1)**i*12,0),smooth=False)
    # Skid: 2.1 x .4 x .15 collider envelope; bottom arc r 10.275 about the hinge keeps .075 felt gap in all swing angles.
    xs=[1.05-i*.15 for i in range(15)]
    ext(p,'Iron',[(-1.05,-9.95),(1.05,-9.95)]+[(x,-math.sqrt(SKID_R**2-x*x)) for x in xs],'z',-.055,.055)
    for x in (-.8,-.4,0,.4,.8):
        for z in (-.065,.065):p.cyl('Iron',.045,.045,.02,8,loc=L.R(x,-10.08,z),rot=(90,0,0),smooth=False)
def h14_cableway_trestle(p):
    for x in (-5.1,5.1):box(p,'SandBlock',(x,.15,0),(1.0,.3,1.2))
    for x in (-5,5):box(p,'Timber',(x,(.3+10.35)/2,0),(.8,10.05,.8))
    # Twin cap beams with a .4 slot: the moving hanger eye (|z|<=.045) turns between them.
    for z in (-.35,.35):box(p,'Timber',(0,10.85,z),(10.8,1.0,.3))
    box(p,'Timber',(0,11.075,0),(10.8,.55,.4))
    for s in (-1,1):
        for z in (-.35,.35):box(p,'Timber',(s*4.0,9.675,z),(1.9,.3,.3),roll=180-48.4 if s>0 else 48.4)
    for z in (-.52,.52):
        box(p,'Iron',(0,10.68,z),(.9,.6,.04))
        for x in (-.3,.3):
            for y in (10.48,10.88):p.cyl('Brass',.05,.05,.03,8,loc=L.R(x,y,z+(.035 if z>0 else -.035)),rot=(90,0,0),smooth=False)

# ---------------- H17 sundial
ARM_BOTTOM=0.051
# Pass 4b: each arm's leading end (head, r ARM_SPLIT..11.5) is its own FBX (h17_shadow_arm_head_<yaw>), same pivot/motion.
# Split on a .6 band edge so the red/cream sequence runs on unbroken across arm + head; heads are plain boxes (squared, no rounding).
ARM_SPLIT=10.0
def _h17_blockers():return next(m for m in HOLES[16]['moving_parts'] if m['id']=='shadow_arm')['blockers']
def _h17_arm(p,b,rlo,rhi):
    """Arm segment r rlo..rhi of blocker b (clamped to the blocker): Slate core + .15 red/cream bands on both sweep faces."""
    a=math.radians(b['yaw']);ca,sa=math.cos(a),math.sin(a)
    r0=math.hypot(b['center'][0],b['center'][2])
    L0=r0-b['size'][0]/2;L1=r0+b['size'][0]/2;W=b['size'][2]/2;top=b['center'][1]+b['size'][1]/2
    lo=max(L0,rlo);hi=min(L1,rhi)
    def put(m,rc,tc,rs,ts):
        # local radial rc (+x before yaw), tangential tc (+z before yaw); Roblox yaw rotation.
        box(p,m,(rc*ca+tc*sa,(ARM_BOTTOM+top)/2,-rc*sa+tc*ca),(rs,top-ARM_BOTTOM,ts),yaw=b['yaw'])
    put('Slate',(lo+hi)/2,0,hi-lo,2*(W-.15))
    e=[L0+.6*i for i in range(int((L1-L0)/.6)+1)]+[L1]
    e=sorted(set(round(x,6) for x in e))
    for i,(u,v) in enumerate(zip(e,e[1:])):
        u,v=max(u,lo),min(v,hi)
        if v-u<1e-6:continue
        for s in (-1,1):put(BAND[i%2],(u+v)/2,s*(W-.075),v-u,.15)
def h17_shadow_arms(p):
    for b in _h17_blockers():_h17_arm(p,b,0,ARM_SPLIT)
def h17_shadow_arm_head(p,yaw):
    _h17_arm(p,next(b for b in _h17_blockers() if round(b['yaw'])==yaw),ARM_SPLIT,1e9)
def h17_plinth(p):
    pts=[]
    for w in HOLES[16]['walls']:
        if w['id'].startswith('gnomon_plinth_'):
            cz=w['center'][2]+36;hx=w['size'][0]/2;hz=w['size'][2]/2
            pts+=[(sx*hx,cz+sz*hz) for sx in (-1,1) for sz in (-1,1)]
    hull=hull2d(pts)
    ext(p,'SandBlock',hull,'y',0,1.1);ext(p,'MintWhite',hull,'y',1.1,1.2)
    for k in range(12):
        a=math.radians(30*k);box(p,'Licorice',(6.2*math.cos(a),1.21,-6.2*math.sin(a)),(1.2,.02,.12),yaw=30*k)
    box(p,'Brass',(0,1.3,0),(1.6,.2,6.0))
    for i in range(7):box(p,'Bubblegum' if i%2==0 else 'MintWhite',(0,1.4+.8*i+.4,0),(1.2,.8,1.2))
    ext(p,'Bubblegum',[(-3,1.4),(3,1.4),(0,9.0)],'x',-.2,.2)
    return hull

# ---------------- H7 comfort pieces (pivot [0,0,-42] / [0,-4.25,-42] / pad base)
def _vr(i):return next(b for b in HOLES[6]['vr_comfort']['boxes'] if b['id']==i)
def h07_bridge_parapets(p,piv=(0,0,-42)):
    for rid in ('rope_rail6','rope_rail7','rope_rail12','rope_rail13'):
        b=_vr(rid);cx,cy,cz=[b['center'][i]-piv[i] for i in range(3)];sx,sy,sz=b['size'];y0=cy-sy/2;y1=cy+sy/2
        n=round(sz/2.75);post=.4;panel=(sz-(n+1)*post)/n;z=cz-sz/2
        for k in range(n+1):
            box(p,'Timber',(cx,cy,z+post/2),(sx,sy,post));z+=post
            if k<n:
                zc=z+panel/2
                box(p,'SandBlock',(cx,(y0+y1-.6)/2,zc),(sx,sy-.6,panel))
                box(p,'Rope',(cx,y1-.45,zc),(sx,.3,panel))
                box(p,'Timber',(cx,y1-.15,zc),(sx,.3,panel));z+=panel
def h07_bridge_skirts(p,piv=(0,0,-42)):
    for rid in ('bridge1_skirt_west','bridge1_skirt_east','bridge2_skirt_west','bridge2_skirt_east'):
        b=_vr(rid);cx,cy,cz=[b['center'][i]-piv[i] for i in range(3)];sx,sy,sz=b['size']
        top=-0.5-piv[1]  # parapet bottom; exact skirt box overlaps parapet y -.5..0 (parapet mesh covers it)
        box(p,'SandBlock',(cx,(cy-sy/2+top)/2,cz),(sx,top-(cy-sy/2),sz))
def h07_gap_floor_mist(p,piv=(0,-4.25,-42)):
    f=_vr('gap_comfort_floor');m=HOLES[6]['vr_comfort']['mist']
    box(p,'FloorSand',[f['center'][i]-piv[i] for i in range(3)],f['size'])
    box(p,'Mist',[m['center'][i]-piv[i] for i in range(3)],m['size'])
def h07_teleport_pads(p):
    s=HOLES[6]['player_teleport_points'][0]['size'];w,h,d=s;b=.25
    for z in (-(d-b)/2,(d-b)/2):box(p,'PadLime',(0,h/2,z),(w,h,b))
    for x in (-(w-b)/2,(w-b)/2):box(p,'PadLime',(x,h/2,0),(b,h,d-2*b))
    box(p,'PadCore',(0,h/2,0),(w-2*b,h,d-2*b))

def _pad_tiles(w,d,b):
    return [('PadLime',-w/2,w/2,-d/2,-d/2+b),('PadLime',-w/2,w/2,d/2-b,d/2),('PadLime',-w/2,-w/2+b,-d/2+b,d/2-b),('PadLime',w/2-b,w/2,-d/2+b,d/2-b),('PadCore',-w/2+b,w/2-b,-d/2+b,d/2-b)]
def h07_teleport_pad_exit(p):
    """bridge2_exit pad at its exact holes.json box, minus a r .65 notch round the cup (cup r .5 + .15).
    Stair-stepped x-slices (<=.05) give convex boxes; every slice excludes the disk's widest chord."""
    pt=next(q for q in HOLES[6]['player_teleport_points'] if q['id']=='bridge2_exit');cup=HOLES[6]['cup']
    w,h,d=pt['size'];cx=cup['position'][0]-pt['position'][0];cz=cup['position'][2]-pt['position'][2];r=cup['radius']+.15
    for m,x0,x1,z0,z1 in _pad_tiles(w,d,.25):
        xs=sorted({x0,x1}|{x for x in [cx-r+i*.05 for i in range(int(2*r/.05)+2)] if x0<x<x1}|({max(x0,cx-r),min(x1,cx+r)} if cx-r<x1 and cx+r>x0 else set()))
        for xa,xb in zip(xs,xs[1:]):
            xn=min(max(cx,xa),xb);hh=math.sqrt(max(r*r-(xn-cx)**2,0)) if (xa<cx+r and xb>cx-r) else -1
            spans=[(z0,z1)] if hh<0 else [(z0,min(z1,cz-hh)),(max(z0,cz+hh),z1)]
            for za,zb in spans:
                if zb-za>1e-6:box(p,m,((xa+xb)/2,h/2,(za+zb)/2),(xb-xa,h,zb-za))
# ---------------- world dam crest (pivot = deck centre, world coords)
def dam_crest_parapets(p):
    o=DAM['deck']['center'];rel=lambda c:[c[i]-o[i] for i in range(3)]
    box(p,'MintWhite',rel(DAM['deck']['center']),DAM['deck']['size'])
    for q in DAM['parapets']:
        c=rel(q['center']);s=q['size']
        box(p,'MintWhite',(c[0],c[1]-.15,c[2]),(s[0],s[1]-.3,s[2]));box(p,'PepRed',(c[0],c[1]+s[1]/2-.15,c[2]),(s[0],.3,s[2]))
    for q in DAM['skirts']:box(p,'MintWhite',rel(q['center']),q['size'])
GEN={k:v for k,v in globals().items() if k.startswith(('h07_','h09_','h14_','h17_','dam_')) and k!='h17_shadow_arm_head'}
GEN.update({f'h17_shadow_arm_head_{y}':(lambda p,y=y:h17_shadow_arm_head(p,y)) for y in (0,90,180,270)})
