"""Shape helpers used by gen_batch3; pure Python, no Blender dependencies."""
import sys as _guard_sys
from pathlib import Path as _GuardPath
_guard_sys.path.insert(0, str(_GuardPath(__file__).resolve().parent.parent))
from polish_guard import start_guard
_PROTECTED_VERIFY = start_guard()

import sys,math,json
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from polish_geometry import Mesh,count
IDS=['h04_ice_channel_edge','h18_ramp_lanterns','h14_buoy_float','h04_frosted_palm_a','h04_frosted_palm_b','h06_frosted_palms']+[f'h{n:02d}_snowpuffs' for n in [4,6,14,18]]

def merge(p,m):
    for mat,g in m.groups.items():p.add(mat,g['verts'],g['faces'])
def sphere(p,mat,c,size,n=12,steps=4):
    m=Mesh();m.sphere(mat,np.array(c)-p.anchor,size,n,steps);merge(p,m)

def snow_mound(p,mat,c,size,n=16):
    """Lumpy dome with a single planar underside, within the original slab bounds."""
    x,y,z=c;w,h,d=size
    rings=[]
    for yy,scale in [(0,1),(.55,.78),(.86,.42)]:
        ring=[]
        for i in range(n):
            angle=math.tau*i/n
            lump=.94+.06*math.cos(3*angle)
            ring.append([x+w*.5*scale*lump*math.cos(angle)-p.anchor[0],
                         y+h*yy-p.anchor[1],z+d*.5*scale*lump*math.sin(angle)-p.anchor[2]])
        rings.append(ring)
    verts=[v for ring in rings for v in ring]+[[x-p.anchor[0],y+h-p.anchor[1],z-p.anchor[2]]]
    faces=[list(range(n-1,-1,-1))]
    for j in range(2):
        faces += [[j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i] for i in range(n)]
    faces += [[2*n+i,2*n+(i+1)%n,3*n] for i in range(n)]
    p.add(mat,verts,faces)

def puff(p,c,sc=.8,bell=False):
    from geometry import bud,tube
    x,y,z=c
    # Pole triangles close both ends; there is no flat head cap.
    steps=3 if bell else 4
    sphere(p,'Ink',[x,y+sc*.45,z],[sc,sc*.9,sc*.8],16,steps)
    sphere(p,'Ink',[x,y+sc*.96,z],[sc*.66,sc*.58,sc*.64],16,steps)
    sphere(p,'Snow',[x,y+sc*.42,z+sc*.31],[sc*.65,sc*.68,sc*.23],8,3)
    bud(p,'Beak',[x,y+sc*.85,z+sc*.38],[sc*.3,sc*.18,sc*.3])
    sphere(p,'AuroraTeal',[x,y+sc*.75,z],[sc*.88,sc*.16,sc*.78],8,3)
    sphere(p,'AuroraViolet',[x+sc*.22,y+sc*.57,z+sc*.39],[sc*.16,sc*.44,.08],6,3)
    for dx in [-.19,.19]:sphere(p,'Ink',[x+dx*sc,y+sc*.99,z+sc*.3],[.065,.075,.05],6,2)
    for dx in [-.43,.43]:sphere(p,'Ink',[x+dx*sc,y+sc*.4,z],[sc*.28,sc*.42,sc*.25],6,2)
    if bell:
        sphere(p,'Brass',[x+sc*.55,y+sc*.37,z+.15],[.25,.25,.25],6,2)
        tube(p,'Brass',[x+sc*.55,y+sc*.45,z+.15],[x+sc*.55,y+sc*.65,z+.15],.03,n=4)

def palm(p,root,lean,height=11.5,phase=0):
    from geometry import tube
    x,y,z=root;pts=[[x+lean*(j/8)**2,y+height*j/8,z+.14*math.sin(j/8*math.pi)] for j in range(9)]
    for j,(aa,bb) in enumerate(zip(pts,pts[1:])):
        tube(p,'Timber',aa,bb,.22-j*.011,.21-j*.011,n=6)
        tube(p,'SnowShadow',bb,[bb[0],bb[1]+.055,bb[2]],.22-j*.011,n=6)
    crown=np.array(pts[-1])
    for k in range(11):
        theta=phase+k*math.tau/11;direction=np.array([math.cos(theta),0,math.sin(theta)]);side=np.array([-direction[2],0,direction[0]])
        rings=[];snow=[]
        for t,w in [(0,.03),(.25,.35),(.5,.44),(.75,.28),(1,.012)]:
            c=crown+direction*2*t+[0,.65*math.sin(math.pi*t)-.95*t*t,0]
            rings.append([(c-side*w-p.anchor).tolist(),(c+side*w-p.anchor).tolist(),(c+side*w+[0,.035,0]-p.anchor).tolist(),(c-side*w+[0,.035,0]-p.anchor).tolist()])
            snow.append([(c-side*w*.66+[0,.041,0]-p.anchor).tolist(),(c+side*w*.66+[0,.041,0]-p.anchor).tolist()])
        p.loft('AuroraTeal',rings)
        p.add('Snow',[v for r in snow for v in r],[[j*2,j*2+1,j*2+3,j*2+2] for j in range(4)])

def buoy(p):
    from geometry import tube
    x,y,z=p.anchor
    for dx in [-.65,.65]:
        # Twelve-sided bulged barrel, continuous band boundaries with no internal caps.
        profile=[(.08,.34),(.28,.46),(.55,.5),(.85,.46),(1.1,.34)]
        rings=[[[dx+r*math.cos(i*math.tau/12),yy,r*math.sin(i*math.tau/12)] for i in range(12)] for yy,r in profile]
        for j in range(4):p.loft(['AuroraMint','AuroraViolet','Snow','AuroraMint'][j],rings[j:j+2],j==0,j==3)
        sphere(p,'Snow',[x+dx,y+.08,z],[1.1,.16,1.05],12,3)
        for k in range(4):
            a=k*math.tau/4;tube(p,'Brass',[x+dx+.15*math.cos(a),y+1.08,z+.15*math.sin(a)],[x+dx+.15*math.cos(a),y+1.58,z+.15*math.sin(a)],.025,n=4)
        sphere(p,'Glow',[x+dx,y+1.4,z],[.16,.22,.16],6,3)
        sphere(p,'Brass',[x+dx,y+1.64,z],[.35,.16,.35],8,3)
    # A single coil in the existing footprint, with frost on the rope.
    for k in range(12):
        a=k*math.tau/12;b=(k+1)*math.tau/12
        tube(p,'Snow',[x+.4*math.cos(a),y+.08,z+.9+.4*math.sin(a)],[x+.4*math.cos(b),y+.08,z+.9+.4*math.sin(b)],.045,n=4)

def ramp_lanterns(p):
    from geometry import box
    x,y,z=p.anchor
    for dz in [-3.5,0,3.5]:
        box(p,'Brass',[-8.4,y+.25,z+dz],[1.898,.06,.95])
        for side in [-1,1]:box(p,'Brass',[-8.4,y+.20,z+dz+side*.46],[1.898,.10,.03])
        box(p,'Timber',[x,y+2.88,z+dz],[.898,5.26,.898])
        box(p,'Glow',[x,y+6.02,z+dz],[.55,.84,.55])
        for dx in [-1,1]:
            for side in [-1,1]:box(p,'Brass',[x+dx*.378,y+6.02,z+dz+side*.378],[.108,1.1475,.108])
        box(p,'Brass',[x,y+5.5,z+dz],[.898,.15,.898])
        sphere(p,'Brass',[x,y+6.57,z+dz],[.898,.22,.898],8,3)
        sphere(p,'Brass',[x,y+6.74,z+dz],[.12,.12,.12],6,3)

def ice_bank(p,width=.4):
    from geometry import box
    # Rail outer edge 4.5, .15 clearance; retained authorized outer envelope 5.05.
    for sign in [-1,1]:
        inner=4.65;outer=inner+width
        for j in range(12):
            z=-39.15+(j+.5)*30.9/12;h=.82+.09*(j%4);x=sign*(inner+width/2)
            rings=[]
            for yy,sc in [(0.1,.90),(.25,1),(h,.88)]:
                rings.append([[x+dx*width*sc/2-p.anchor[0],yy-p.anchor[1],z+dz*(30.9/12)/2-p.anchor[2]] for dx,dz in [(-1,-1),(1,-1),(1,1),(-1,1)]])
            p.loft('Ice',rings)
            box(p,'IceCore',[sign*(inner+.065),h-.045,z],[.09,.09,30.9/12])

def finish(out,S):
    baseline=json.loads((S/'parts_prepolish.json').read_text());old={p['id']:p for p in baseline};new={p['id']:p for p in out}
    for p in baseline:
        if p['id'] not in IDS:new[p['id']]=p
    out=[new[p['id']] for p in baseline]
    for p in out:
        if p['id'] not in IDS:continue
        original=old[p['id']]
        for key in ['anchor','yaw_local','skin_ids','felt_skins','motion','override_boxes']:p[key]=original[key]
        p.update(can_collide=False,can_query=False,can_touch=False)
        p['notes']=original['notes']+['Polish: rounded organic geometry; original pivot/yaw and clearance envelope retained.']
        tris=count(p['groups']);limit=count(original['groups'])*1.2 if 'snowpuffs' in p['id'] else (2999 if p['id']=='h06_frosted_palms' else 900)
        if 'snowpuffs' in p['id']:limit=min(limit,900 if p['hole']==14 else 1600)
        assert tris<=limit and tris<3000,(p['id'],tris,limit)
    (S/'polish_ids.json').write_text(json.dumps(IDS,indent=2))
    (S/'polish_shapes.json').write_text(json.dumps([dict(id=p['id'],old_tris=count(old[p['id']]['groups']),new_tris=count(p['groups'])) for p in out if p['id'] in IDS],indent=2))
    return out
