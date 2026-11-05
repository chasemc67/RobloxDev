"""Pass5 standalone scenery, generated in arch coordinates then base-centred."""
import math, random
from mathutils import Vector
import bwlib as L
from registry import prop, FRONT_SOUTH
from props_arches import catmull, resample, crystal, cactus

SCENERY=[]
ANCHORS=[[-8.2,21.3,2.3],[8.2,21.3,2.3],[-6,22.3,2.3],[6,22.3,2.3],[-3.5,23.3,2.3],[3.5,23.3,2.3]]

def box(center,size,name):return dict(name=name,center=center,size=size,CanCollide=True)

def register(name,course,fn,coll):
    SCENERY.append(name)
    def generate(pb):
        fn(pb)
        if 'atlas' not in pb.parts:
            # Shared-atlas stone inset, large enough to read at toy scale.
            vs=[v for p in pb.parts.values() for v in p.verts]
            cx=(min(v.x for v in vs)+max(v.x for v in vs))/2
            cy=(min(v.y for v in vs)+max(v.y for v in vs))/2
            pb.box((.8,.8,.5),loc=(cx,cy,.25),mapping=('flat','stone'),bevel=.15)
        # Tight side overlap, with depth bounded behind the Z4 approach plane.
        for part in pb.parts.values():
            for v in part.verts:
                if 'trunk_' in name:
                    v.x *= .51
                    v.y = max(-6.5 if v.z>18 else -3.7, min(9 if v.z>18 else 2.8, v.y))
                elif name=='bw_scn_aurora_crown':
                    v.y+=8.5
                elif 'planter_' in name:
                    v.x = (v.x - (15 if v.x>0 else -15))*.62 + (8.6 if v.x>0 else -8.6)
                    v.y = v.y*.5
                elif 'rocks_' in name:
                    v.x=(v.x-(15 if v.x>0 else -15))*.6+(8.8 if v.x>0 else -8.8)
                    v.y=max(-3.7,min(9 if v.z>12 else 2.8,v.y*.95))
                    if v.z<3.6:v.x=(1 if v.x>0 else -1)*max(7.8,abs(v.x))
                if name != 'bw_scn_aurora_crown' and v.z<12.01:
                    if v.x>0:v.x=max(5.15,v.x)
                    else:v.x=min(-5.15,v.x)
        verts=[v for p in pb.parts.values() for v in p.verts]
        for v in verts:v.z=max(0,v.z)
        mn=Vector(tuple(min(v[k] for v in verts) for k in range(3)))
        mx=Vector(tuple(max(v[k] for v in verts) for k in range(3)))
        off=Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z))
        for v in verts:v-=off
        pivot=[off.x,off.z,-off.y]
        collisions=[dict(b,center=[b['center'][k]-pivot[k] for k in range(3)]) for b in coll]
        def extras(objs):
            for o in objs:
                if o.name.endswith('BW_Neon_Yellow'):
                    m=o.data.materials[0].copy();m.name='BW_Neon_Yellow';m['bw_hex']='#FFE08A'
                    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');rgb=(*L.lin('#FFE08A'),1)
                    bs.inputs['Base Color'].default_value=rgb;bs.inputs['Emission Color'].default_value=rgb
                    o.data.materials.clear();o.data.materials.append(m)
            if name=='bw_scn_aurora_crown':
                for o in objs:
                    if o.data.materials[0].name.startswith('BW_Neon'):
                        o.data.materials[0].name='Glow_Tips'
            return dict(pivot='base centre',pivot_position_arch_local=[round(v,4) for v in pivot],course=course,
                collision=collisions,collision_frame='FBX pivot-local Roblox axes',can_collide=False,
                decoration_only=True,foliage_can_collide=False,crystals_can_collide=False,
                clearance_rule='Zone A X[-5,5] Y[0,12] Z[-12,4]; zone B X[-11,11] Y[0,18] Z[4,34]; no triangle intersection; above Y18 allowed.',
                material_policy='Opaque vertex colour + shared atlas; separate Neon; no real lights')
        return extras
    prop(name,'scenery',target=[0,0,0],tris_max=19999,front=FRONT_SOUTH,pivot='local',collision=[],
         notes='Pass5 standalone toy scenery; place at pivot_position_arch_local relative to parent arch; invisible collision boxes only.')(generate)

def trunk(pb,s):
    def pos(x,y,z):return (x/.51,y,z)
    # Three distinct interwoven strands: 240 degrees over the exposed trunk.
    for strand in range(3):
        path=[];rads=[]
        for i in range(33):
            f=i/32;a=strand*math.tau/3+f*math.radians(240)
            rad=.95-.4*f
            path.append(pos(s*(8.1-.6*f)+math.cos(a)*rad,math.sin(a)*rad,.25+21.3*f))
            rads.append((1.15-.55*f)/.51)
        pb.tube(path,rads,segs=10,mapping=('trim','bark',5+strand),smooth=True)
    for j in range(6):
        a=j*math.tau/6
        pb.tube([pos(s*8.1,0,3),pos(s*8.1+math.cos(a)*1.6,math.sin(a)*1.3,1),pos(s*8.1+math.cos(a)*2.7,math.sin(a)*2.2,.2)],[.9/.51,.6/.51,.18/.51],segs=8,mapping=('trim','bark',4))
    for a in [a for a in ANCHORS if a[0]*s>0]:
        pb.tube([pos(s*7.5,0,20),pos(a[0],-.3,a[1]+1),pos(a[0],-a[2],a[1])],[.65/.51,.4/.51,.2/.51],segs=8,mapping=('trim','bark',3))
    pb.tube([pos(s*7.5,0,18.7),pos(s*4,0,19.2),pos(s*.2,0,19.5)],[.8/.51,.7/.51,.6/.51],segs=10,mapping=('trim','bark',7))
    # Core/top, overlapping middle masses, small outer cascades; no low front foliage.
    blobs=[(1.8,1.0,23.3,4.5),(5.2,1.7,24.7,3.8),(7.8,.6,22.7,3.3),(4.0,-1.8,21.7,3.2),(8.8,1.3,20.1,2.5),(2.2,-1.5,21,2.8),(6.8,-1.7,20.2,2.2),(9.2,.2,17.8,1.8),(9.4,1.1,15.2,1.4),(9.5,.5,13.1,1.2),(8.9,2.0,19.0,1.5),(6.1,2.6,26.3,2.3)]
    for j,(x,y,h,r) in enumerate(blobs):
        pb.blob((2*r/.51,2*r*.85,2*r*.8),loc=pos(s*x,y,h),ico=2,amp=.065,seed=4600+j,part='backdrop',color=('#E58A3A','#C9473A','#E8C24C')[j%3],smooth=True)

def planter(pb,s):
    x=s*15;y=-3
    pb.box((5.4,3.7,1.7),loc=(x,y,.85),bevel=.35,segs=2,part='backdrop',color='#756568')
    pb.box((4.6,3,.35),loc=(x,y,1.7),mapping=('flat','bark'),bevel=.15)
    for j in range(13):
        a=j*2.4;r=.3+(j%4)*.4;cx=x+math.cos(a)*r;cy=y+math.sin(a)*r*.65
        pb.cyl(.15,.15,.85,loc=(cx,cy,2),part='backdrop',color='#4F9A43')
        for k in range(5):
            pb.sphere(.32,loc=(cx+math.cos(k*math.tau/5)*.32,cy+math.sin(k*math.tau/5)*.32,2.5+(j%3)*.16),ico=1,part='backdrop',color=('#E58A3A','#C9473A','#E8C24C')[j%3])
        pb.sphere(.25,loc=(cx,cy,2.6+(j%3)*.16),ico=1,part='backdrop',color='#E8C24C')

def tower(pb,s):
    import bmesh
    from mathutils import Matrix
    for j in range(17):
        h=.82+j*1.6;cx=s*(10.2-h*math.tan(math.radians(10)));radius=2.7-j*.035
        bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=12,radius1=radius,radius2=radius*.98,depth=1.95)
        bmesh.ops.scale(bm,vec=Vector((1,.80,1)),verts=bm.verts)
        bmesh.ops.bevel(bm,geom=list(bm.edges),offset=.3,segments=3,affect='EDGES',clamp_overlap=True)
        mat=Matrix.Translation((cx,0,h))@Matrix.Rotation(math.radians(-s*10),4,'Y')
        pb.add(bm,matrix=mat,part='backdrop',color='#F0C9A0' if j%3==0 else '#D9714A',smooth=True)
    pb.box((1,.8,.5),loc=(s*10.2,0,.25),mapping=('flat','stone'),bevel=.15)

def candies(pb,s):
    # Full Neon candy shards on the front-facing leg/lintel joints and at the base.
    pb.neon_hex='#F6A6C8'
    for j in range(18):
        joint=j<12;k=j%6
        h=(12.7 if j<6 else 16.5) if joint else .45
        x=s*((7.0 if joint else 9.7)+(k%3)*.55)
        y=-2.3-(k//3)*.25
        length=3.0+(j%4)*.9
        n=6;base=Vector((x,y,h));r=.76+(j%2)*.24
        vs=[base+Vector((math.cos(k*math.tau/n)*r,math.sin(k*math.tau/n)*r,0)) for k in range(n)]
        vs += [v+Vector((-s*.25,0,length*.7)) for v in vs]
        vs += [base+Vector((-s*.35,0,length))]
        faces=[list(reversed(range(n)))]+[[k,(k+1)%n,n+(k+1)%n,n+k] for k in range(n)]+[[n+k,n+(k+1)%n,2*n] for k in range(n)]
        key='neon' if j%2==0 else pb.name+'__BW_Neon_Yellow'
        if j%2:pb._part(key).mat='BW_Neon'
        pb.custom(vs,faces,part=key)
    for j in range(3):pb.blob((2,1.8,.8),loc=(s*(9+j*.6),-2,.4),ico=1,seed=700+j,part='backdrop',color='#D9714A',flat_bottom=0)
    pb.box((.8,.8,.5),loc=(s*9.8,-2,.25),mapping=('flat','stone'),bevel=.15)

def large_cactus(pb):
    cactus(pb,(-15,-.7,.1),scale=4.05)
    # Front-facing disc with geometric red/cream spiral bands, 1.5x original height.
    cx=-15;cz=17.2;r=2.35;n=48;rings=24
    for face_y in (-2.48,-1.82):
        for j in range(rings):
            r0=r*j/rings;r1=r*(j+1)/rings
            for k in range(n):
                a=k*math.tau/n;b=(k+1)*math.tau/n;t0=1.35*math.tau*r0/r;t1=1.35*math.tau*r1/r
                vs=[(cx+r0*math.cos(a+t0),face_y,cz+r0*math.sin(a+t0)),(cx+r1*math.cos(a+t1),face_y,cz+r1*math.sin(a+t1)),(cx+r1*math.cos(b+t1),face_y,cz+r1*math.sin(b+t1)),(cx+r0*math.cos(b+t0),face_y,cz+r0*math.sin(b+t0))]
                color='#E2574C' if (k//12)%2==0 else '#F6EBD8'
                pb.custom(vs,[[0,1,2,3]],part='backdrop',color=color)
    pb.cyl(r,r,.6,segs=48,loc=(cx,-2.15,cz),rot=(90,0,0),caps=False,part='backdrop',color='#F6EBD8')
    pb.cyl(.26,.26,5,segs=12,loc=(cx,-2.15,13.7),part='backdrop',color='#F6EBD8')
    pb.box((4.2,2.7,.5),loc=(-15,-.7,.25),part='backdrop',color='#D9714A',bevel=.2)
    # Normalize the full rebuilt assembly to exactly 1.5x the pass5 bbox height.
    import json
    from pathlib import Path
    old=json.loads((Path(__file__).parent.parent/'_backup_pass5/manifest.json').read_text())
    target=1.5*next(e for e in old['props'] if e['name']=='bw_scn_sugarloaf_lollipop_cactus')['bbox_size_studs'][1]
    vv=[v for p in pb.parts.values() for v in p.verts];height=max(v.z for v in vv)-min(v.z for v in vv);f=target/height
    for v in vv:
        v.x=-15+(v.x+15)*f;v.y=-.7+(v.y+.7)*f;v.z*=f

def crown(pb):
    # Exact supplied geometry is exported by build_pass7; no historical crown is generated.
    import aurora_crown_v2 as crown_source
    crown_source.SIDES=16 # allowed: initial12-sided build measured1284 tris (<1500)
    return crown_source.build_crown()

def rocks(pb,s):
    # All snowy rubble grounded tightly at the legs; shoulder debris removed.
    for j in range(7):
        x=s*(15+(j%3)*1.1);y=-.4+(j//3)*.85;h=.7+(j%3)*.27
        pb.blob((3.0,2.1,1.8),loc=(x,y,h),ico=2,seed=800+j,flat_bottom=0,part='backdrop',color='#3A3550')
        pb.blob((2.8,1.95,.55),loc=(x,y,h+.77),ico=2,seed=850+j,part='backdrop',color='#EEF3F7')
    pb.box((.8,.8,.5),loc=(s*15,0,.25),mapping=('flat','stone'),bevel=.15)

for s,suffix in ((-1,'w'),(1,'e')):
    register('bw_scn_lantern_grove_trunk_'+suffix,'lantern_grove',lambda pb,s=s:trunk(pb,s),[box([s*7.7,8,0],[2.5,16,2.6],'trunk'),box([s*7.4,17,0],[2.4,2,2.5],'upper_trunk')])
    register('bw_scn_lantern_grove_planter_'+suffix,'lantern_grove',lambda pb,s=s:planter(pb,s),[box([s*8.6,.8,1.1],[3,1.6,.8],'stone_front'),box([s*8.6,.8,1.9],[3,1.6,.8],'stone_back')])
    register('bw_scn_sugarloaf_tower_'+suffix,'sugarloaf_canyon',lambda pb,s=s:tower(pb,s),[box([s*(10.2-h*.176327),h,0],[2.8,6.5,3.2],'tower_'+str(i)) for i,h in enumerate((3.5,10,16.5,23))])
    register('bw_scn_sugarloaf_crystals_'+suffix,'sugarloaf_canyon',lambda pb,s=s:candies(pb,s),[box([s*8.3,.6,2.4],[1.5,1.2,1.1],'rock_w'),box([s*9.5,.6,2.4],[1.5,1.2,1.1],'rock_e')])
    register('bw_scn_aurora_rocks_'+suffix,'aurora_archipelago',lambda pb,s=s:rocks(pb,s),[box([s*8.5,1.1,0],[2.3,2.2,2.5],'rock_front'),box([s*9.5,1.5,-1.3],[2.5,3,2.5],'rock_back')])
register('bw_scn_sugarloaf_lollipop_cactus','sugarloaf_canyon',large_cactus,[box([-15,6,0],[2.5,12,2.5],'stem'),box([-15,.25,0],[4.8,.5,3],'stone_base')])
register('bw_scn_aurora_crown','aurora_archipelago',crown,[box([-6,19.3,-9],[3,1.4,2],'rock_w'),box([6,19.3,-9],[3,1.4,2],'rock_e')])
