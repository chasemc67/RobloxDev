"""Pass-5 generators (holes.json p9b). Coordinates are Roblox studs relative to the export pivot.
Every primitive is convex so the fitcheck can use exact convex parts. Red/cream bands only on moving parts."""
import math
import sclib as L
from registry_movers import HOLES,REG
from gen_pass4 import box,ext,h07_teleport_pads,BAND

def _mp(h,i):return next(m for m in HOLES[h]['moving_parts'] if m['id']==i)

# ---------------- H7: exit pad (p9: moved east, clear of the cup -> plain pad, notch removed) + island respawn stone
def h07_teleport_pad_exit(p):h07_teleport_pads(p)
def _oct(h,c):return [(-h+c,-h),(h-c,-h),(h,-h+c),(h,h-c),(h-c,h),(-h+c,h),(-h,h-c),(-h,-h+c)]
def h07_island_respawn_stone(p):
    """Flush marker stone, holes.json approx_size .8 x .02 x .8, pivot = base centre on the island felt (y 0).
    Low-poly chamfered sandstone slab with a glowing octagonal core, framed like the teleport pads (no red/cream)."""
    sx,sy,sz=next(e for e in REG if e['id']=='h07_island_respawn_stone')['size']
    h=sx/2;outer=_oct(h,.12);inner=_oct(.22,.07);base=sy*.6
    ext(p,'SandBlock',outer,'y',0,base)
    for i in range(8):
        j=(i+1)%8;ext(p,'SandBlock',[outer[i],outer[j],inner[j],inner[i]],'y',base,sy)
    ext(p,'RespawnGlow',inner,'y',base,sy)

# ---------------- H9: vane collision mesh = the 48 holes.json strips exactly (collision-only)
def h09_windpump_vanes_collision(p):
    for b in _mp(8,'windpump')['blockers']:
        a=math.radians(b.get('roll',0));x,y,z=b['center']
        box(p,'Collider',(x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a),z),b['size'],roll=b.get('roll',0))

# ---------------- H14: bucket with a skid that follows the 14 foot strips; foot collision mesh
import gen_p5_profile as GP
SKID_TOP=-9.95;SKID_HALF_D=.075
def foot_strips():return _mp(13,'ore_bucket')['blockers'][1:]
def skid_profile():return GP.skid_profile(foot_strips())
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
    # Pass 5 skid: one convex trapezoid per strip column, underside through skid_profile(); depth = collider depth .15.
    pr=skid_profile()
    for (x0,y0),(x1,y1) in zip(pr,pr[1:]):
        ext(p,'Iron',[(x0,SKID_TOP),(x1,SKID_TOP),(x1,y1),(x0,y0)],'z',-SKID_HALF_D,SKID_HALF_D)
    for x in (-.8,-.4,0,.4,.8):
        for z in (-.085,.085):p.cyl('Iron',.045,.045,.02,8,loc=L.R(x,-10.05,z),rot=(90,0,0),smooth=False)
def h14_ore_bucket_foot_collision(p):
    for b in foot_strips():box(p,'Collider',b['center'],b['size'],yaw=b.get('yaw',0))

# ---------------- H17 hour stones: carved sandstone block + raised roman numeral on top
HOUR_INDEX={'XII':0,'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7,'VIII':8,'IX':9,'X':10,'XI':11}
NUMERAL_MATS=('Bubblegum','GumLemon','GumLime')
GH=.5;GW=.08;VW=.32;GAP=.05;BAR=.06;RELIEF=.02
def _glyph_quads(text):
    """2D quads (u right, v up) for a clock-style numeral: strokes + top/bottom serif bars, centred on (0,0)."""
    adv=lambda ch:GW if ch=='I' else VW
    width=sum(adv(c) for c in text)+GAP*(len(text)-1);x=-width/2;q=[]
    def para(xt,xb):return [(xb-GW/2,-GH/2),(xb+GW/2,-GH/2),(xt+GW/2,GH/2),(xt-GW/2,GH/2)]
    for ch in text:
        if ch=='I':q.append([(x,-GH/2),(x+GW,-GH/2),(x+GW,GH/2),(x,GH/2)])
        elif ch=='V':q+=[para(x+GW/2,x+VW/2),para(x+VW-GW/2,x+VW/2)]
        elif ch=='X':q+=[para(x+GW/2,x+VW-GW/2),para(x+VW-GW/2,x+GW/2)]
        x+=adv(ch)+GAP
    w=width/2+.04
    for v in (GH/2+BAR/2,-GH/2-BAR/2):q.append([(-w,v-BAR/2),(w,v-BAR/2),(w,v+BAR/2),(-w,v+BAR/2)])
    return q
def h17_hour_stone(p,hour):
    e=next(x for x in REG if x['id']=='h17_hour_stone_'+hour);sx,sy,sz=e['box']['size']
    if e['collidable']:
        box(p,'SandBlock',(0,(sy-RELIEF)/2,0),(sx,sy-RELIEF,sz))
    else:
        # Only the inward vertical corner is chamfered; the other corners retain the exact box.
        ix=-1 if e['pivot'][0]>0 else 1
        iz=-1 if e['pivot'][2]>-36 else 1
        ring=[(-sx/2,-sz/2),(sx/2,-sz/2),(sx/2,sz/2),(-sx/2,sz/2)]
        poly=[]
        for j,v in enumerate(ring):
            if v==(ix*sx/2,iz*sz/2):
                prev=ring[j-1];nxt=ring[(j+1)%4]
                for q in (prev,nxt):
                    dx=q[0]-v[0];dz=q[1]-v[1];d=math.hypot(dx,dz)
                    poly.append((v[0]+.48*dx/d,v[1]+.48*dz/d))
            else:poly.append(v)
        ext(p,'SandBlock',poly,'y',0,sy-RELIEF)
    k=HOUR_INDEX[hour];a=math.radians(30*k);D=(math.sin(a),-math.cos(a));U=(-D[1],D[0])  # glyph up = radially outward
    mat=NUMERAL_MATS[sorted(HOUR_INDEX,key=HOUR_INDEX.get).index(hour)%3]
    for quad in _glyph_quads(hour):
        ext(p,mat,[(u*U[0]+v*D[0],u*U[1]+v*D[1]) for u,v in quad],'y',sy-RELIEF,sy)

GEN={'h07_teleport_pad_exit':h07_teleport_pad_exit,'h07_island_respawn_stone':h07_island_respawn_stone,'h09_windpump_vanes_collision':h09_windpump_vanes_collision,
     'h14_ore_bucket':h14_ore_bucket,'h14_ore_bucket_foot_collision':h14_ore_bucket_foot_collision}
GEN.update({'h17_hour_stone_'+h:(lambda p,h=h:h17_hour_stone(p,h)) for h in HOUR_INDEX})
