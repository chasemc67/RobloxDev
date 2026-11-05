# Defend a Garden edge-dressing kit + layout (box). Roblox frame, +Y up, base-centre pivots, studs.
# Map facts (src/shared/Map.luau, src/server/World.luau, CameraRig.luau @950e151): lawn top y0 x-94..90 z-73..77;
# river x90..104 water top 0.4; far bank x100..160 top 0; Rim top y-4 (x+-210, z+-180); shed (-62,-48); patch (0,-47) 50x26;
# camera looks toward -Z (north = -Z, top of screen), tilt 55.4deg, FOV 40, d<=218, pan X-99..99 Z-75..73.
import numpy as np, json, math, os, sys
src=open(os.path.join(os.path.dirname(__file__),'gen_dag.py')).read().split('# ---------------- items')[0]
exec(src.replace("OUT=sys.argv[1] if len(sys.argv)>1 else '.'",""))
import trimesh, shapely.geometry as sg
from trimesh.creation import extrude_polygon, box
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
PAL.clear();PAL.update(G1=(70,170,60),G2=(96,196,72),G3=(58,150,70),Back1=(48,128,52),Back2=(40,112,48),Trunk=(140,92,56),
 Hedge=(62,150,62),HedgeLt=(80,168,66),Wood=(170,112,62),WoodLt=(186,138,96),Rock=(170,176,186),RockDk=(140,146,156),
 Reed=(110,165,62),Cattail=(120,80,45),Water=(70,190,255),Bed=(40,120,190),Ring=(78,150,62),Bush1=(84,176,64),Bush2=(66,158,72))
NAMES[:]=list(PAL)
def superblock(sx,sy,sz,e=0.35,n=14,pos=(0,0,0)):
    # rounded block (superellipsoid), base at pos y
    u=np.linspace(-np.pi/2,np.pi/2,n);v=np.linspace(-np.pi,np.pi,2*n,endpoint=False)
    f=lambda w,p: np.sign(w)*np.abs(w)**p
    V=[];F=[]
    for a in u:
        for b in v: V.append([sx/2*f(np.cos(a),e)*f(np.cos(b),e),sy/2*f(np.sin(a),e),sz/2*f(np.cos(a),e)*f(np.sin(b),e)])
    m2=2*n
    for i in range(n-1):
        for j in range(m2):
            a,b=i*m2+j,i*m2+(j+1)%m2;F+=[[a,b+m2,b],[a,a+m2,b+m2]]
    m=trimesh.Trimesh(V,F);m.merge_vertices();m.update_faces(m.nondegenerate_faces());m.fix_normals()
    m.apply_translation([pos[0],pos[1]+sy/2,pos[2]]);return m
def lumpy(r,pos,sc,seed,sub=1):
    m=icosphere(sub,r);rng=np.random.default_rng(seed);m.vertices*=(1+rng.uniform(-0.12,0.12,(len(m.vertices),1)));return tf(m,pos,sc)
def tree(h,greens,seed,lean=1.0):
    rng=np.random.default_rng(seed);tr=h*0.42;R=h*0.3
    T=[(frustum(h*0.06,h*0.045,0,tr+R*0.4,10),'Trunk')]
    T.append((sph(R,(0,tr+R*0.8,0),(1,0.9,1),2),greens[0]))
    for k in range(2):
        a=rng.uniform(0,6.28)+k*3.1;T.append((sph(R*0.72,(R*0.55*math.cos(a),tr+R*(1.25+0.25*k),R*0.55*math.sin(a)),sub=2),greens[(k+1)%len(greens)]))
    return [obj('Tree',T)]
def backdrop(seed):
    h=20;T=[(frustum(1.1,0.8,0,9,10),'Trunk')]
    for i,(y,r) in enumerate(((9.5,5.2),(13.5,4.6),(17,3.4))): T.append((sph(r,(0.3*(i%2),y,0),(1,0.85,1),2),'Back1' if i%2==0 else 'Back2'))
    return [obj('Tree',T)]
def hedge(L,H,D,cap=False):
    if cap: return [obj('Hedge',[(superblock(D,H,D,0.5),'Hedge')])]
    return [obj('Hedge',[(superblock(L,H,D,0.3,16),'Hedge'),(superblock(L*0.9,H*0.12,D*0.85,0.5,8,(0,H*0.9-0.1,0)),'HedgeLt')])]
def fence_section():
    R=[(box([0.5,0.6,8.2]).apply_translation([0,y,0]) or None,'') for y in ()]
    rails=[]
    for y,dz in((1.3,0.0),(2.5,0.0)):
        b=box([0.5,0.6,8.3]);b.apply_transform(trimesh.transformations.rotation_matrix(math.radians(4 if y>2 else -4),[0,1,0]));b.apply_translation([0,y,0]);rails.append((b,'WoodLt'))
    return [obj('Rails',rails)]
def fence_post(): return [obj('Post',[(frustum(0.5,0.42,0,3.4,8),'Wood'),(cn(0.42,0.35,(0,3.4,0),(0,1,0),8),'Wood')])]
def rock(s,seed):
    m=lumpy(1.0,(0,0,0),(1.4*s,0.8*s,1.15*s),seed);m.apply_translation([0,-m.bounds[0][1]-0.25*s,0])
    k=lumpy(0.5,(0.9*s,0,0.3*s),(s,0.8*s,s),seed+1);k.apply_translation([0,-k.bounds[0][1]-0.1*s,0])
    return [obj('Rock',[(m,'Rock'),(k,'RockDk')])]
def reeds(n,seed):
    rng=np.random.default_rng(seed);P=[]
    for i in range(n):
        a=rng.uniform(0,6.28);r=rng.uniform(0,1.1);x,z=r*math.cos(a),r*math.sin(a);h=rng.uniform(2.6,4.2)
        top=(x+rng.uniform(-0.3,0.3),h,z+rng.uniform(-0.3,0.3));P.append((tube([(x,0,z),((x+top[0])/2,h/2,(z+top[2])/2),top],0.13,5,0.1),'Reed'))
        if i%2==0: P.append((tube([(top[0],h-0.2,top[2]),(top[0],h+0.7,top[2])],0.22,6),'Cattail'))
    return [obj('Reeds',P)]
def bush(seed,k):
    rng=np.random.default_rng(seed);B=[(sph(1.3,(0,1.0,0),(1.2,0.85,1.1),2),'Bush1' if k==0 else 'Bush2')]
    for i in range(2+k):
        a=rng.uniform(0,6.28);B.append((sph(0.9,(1.1*math.cos(a),0.75,1.0*math.sin(a)),sub=2),'Bush2' if k==0 else 'G1'))
    o=obj('Bush',B);v=np.array(o['verts']);v[:,1]-=v[:,1].min()-0.0;o['verts']=v.tolist();return [o]
def river_ext():
    w=box([14,2,40]);w.apply_translation([0,-0.6,0]);b=box([14.4,1,40]);b.apply_translation([0,-2.0,0])  # water top 0.4 like World.luau
    return [obj('Water',[(w,'Water')]),obj('Bed',[(b,'Bed')])]
RING_OUT=(-360,360,-240,180);RING_HOLE=(-94,160,-73,77);RING_Y=-3.9
def ground_ring():
    x0,x1,z0,z1=RING_OUT;h=RING_HOLE
    poly=sg.box(x0,z0,x1,z1).difference(sg.box(h[0],h[2],h[1],h[3]))
    m=extrude_polygon(poly,0.2);v=m.vertices.copy();m.vertices=np.c_[v[:,0],v[:,2],v[:,1]];m.fix_normals()
    return [obj('Ring',[(m,'Ring')])]
KIT={'tree_round_a':tree(8,['G1','G2','G3'],1),'tree_round_b':tree(11,['G2','G3','G1'],2),'tree_round_c':tree(14,['G3','G1','G2'],3),
 'tree_backdrop':backdrop(4),'hedge_tall':hedge(8,5,3.5),'hedge_tall_cap':hedge(0,5,3.5,True),'hedge_low':hedge(8,2.5,2.5),'hedge_low_cap':hedge(0,2.5,2.5,True),
 'fence_section':fence_section(),'fence_post':fence_post(),'rock_s':rock(0.8,5),'rock_m':rock(1.6,6),'rock_l':rock(2.8,7),
 'reeds_a':reeds(9,8),'reeds_b':reeds(14,9),'bush_a':bush(10,0),'bush_b':bush(11,1),'river_ext':river_ext(),'ground_ring':ground_ring()}
rep={}
for k,objs in KIT.items():
    allv=np.vstack([o['verts'] for o in objs])
    if k not in('ground_ring','river_ext'):
        lo,hi=allv.min(0),allv.max(0);sh=np.array([-(lo[0]+hi[0])/2,-lo[1],-(lo[2]+hi[2])/2])
        if k.startswith('fence_section'): sh=np.array([0,0,0.0])
        for o in objs: o['verts']=(np.array(o['verts'])+sh).round(4).tolist()
    allv=np.vstack([o['verts'] for o in objs])
    rep[k]=dict(tris=sum(len(o['tris']) for o in objs),size_xyz=(allv.max(0)-allv.min(0)).round(2).tolist(),miny=round(float(allv[:,1].min()),3),parts=[o['name'] for o in objs])
# ---------------- layout (game coords; y = ground the piece stands on)
L=[];rng=np.random.default_rng(42);RY=RING_Y+0.2  # top of ring slab
def put(p,x,y,z,r=0,s=1): L.append(dict(piece=p,pos=[round(float(x),2),round(float(y),2),round(float(z),2)],rotY=round(float(r),1),scale=round(float(s),3)))
# North: two staggered rows of tall hedges on the lawn behind the patch (patch fence z-60), caps at ends
for row,(z,off) in enumerate(((-66.5,0),(-70.6,5.6))):
    xs=np.arange(-84+off,84.1-11.2+off,11.2) if row else np.arange(-84,84.1,11.2)[:-1]
    for x in xs: put('hedge_tall',x+5.6,0,z,0,1.4)
    put('hedge_tall_cap',xs[0]-0.6,0,z);put('hedge_tall_cap',xs[-1]+11.8,0,z)
# North backdrop: tall trees on the rim, round trees between them
for i,x in enumerate(np.arange(-110,121,22)): put('tree_backdrop',x+rng.uniform(-3,3),RY,-86+rng.uniform(-3,3),rng.uniform(0,360),rng.uniform(1.0,1.2))
for i,x in enumerate(np.arange(-99,110,22)): put(['tree_round_b','tree_round_c'][i%2],x,RY,-79+rng.uniform(-1.5,1.5),rng.uniform(0,360),rng.uniform(1.0,1.15))
# West: split-rail fence on the plateau edge (lawn x-94), posts at joins; clumps on the rim beyond
zs=np.arange(-72,76.1,8.2)
for z in zs[:-1]: put('fence_section',-91.5,0,z+4.1,0)
for z in zs: put('fence_post',-91.5,0,z)
for z in np.arange(-64,76,16):
    put(['tree_round_a','tree_round_b','tree_round_c'][int(rng.integers(3))],-104+rng.uniform(-3,3),RY,z+rng.uniform(-4,4),rng.uniform(0,360),rng.uniform(0.9,1.2))
    put(['bush_a','bush_b'][int(rng.integers(2))],-97.5,RY,z+rng.uniform(4,8),rng.uniform(0,360),rng.uniform(1,1.4))
for z in np.arange(-56,70,28): put('tree_round_c',-120+rng.uniform(-4,4),RY,z,rng.uniform(0,360),1.1)
# South: low hedges near the lawn edge with a gap where the south path (x-30) enters; spawn still reads
gap=(-38,-22)  # 16-stud opening centred on the south path (x -30); path itself starts at the gate z 50
for x0,x1 in((-91,gap[0]),(gap[1],87)):
    n=max(1,round((x1-x0)/11.2));sc=(x1-x0)/n/8
    for k in range(n): put('hedge_low',x0+(k+0.5)*(x1-x0)/n,0,72.5,0,sc)
put('hedge_low_cap',gap[0],0,72.5);put('hedge_low_cap',gap[1],0,72.5)
for x in(-80,-58,-8,18,44,70): put(['tree_round_a','tree_round_b'][int(rng.integers(2))],x+rng.uniform(-4,4),RY,88+rng.uniform(-3,6),rng.uniform(0,360),rng.uniform(0.9,1.1))
for x in(-75,-40,0,35,65): put(['tree_round_b','tree_round_c'][int(rng.integers(2))],x+rng.uniform(-5,5),RY,112+rng.uniform(-6,10),rng.uniform(0,360),1.1)
for x in(-70,-46,-14,6,30,58,80): put(['bush_a','bush_b'][int(rng.integers(2))],x,RY,81+rng.uniform(-1,2),rng.uniform(0,360),1.2)
# East: river extensions both ends at ring level, rocks + reeds on banks, trees on the far bank
for zc in(97,137,177): put('river_ext',97,RY,zc)
for zc in(-93,-133,-173,-213): put('river_ext',97,RY,zc)
for z,lvl in [(-60,0),(-30,0),(10,0),(45,0),(68,0),(90,RY),(-88,RY),(120,RY),(-120,RY)]:
    for side in(-1,1):
        put(['rock_s','rock_m','rock_l'][int(rng.integers(3))],97+side*9.2,lvl,z+rng.uniform(-3,3),rng.uniform(0,360))
for z,lvl in [(-50,0),(-15,0),(55,0),(100,RY),(-100,RY)]:
    put(['reeds_a','reeds_b'][int(rng.integers(2))],97+(-1)**int(z>0)*8.6,lvl,z,rng.uniform(0,360))
for z in np.arange(-64,72,17): put(['tree_round_a','tree_round_b','tree_round_c'][int(rng.integers(3))],118+rng.uniform(-6,10),0,z+rng.uniform(-3,3),rng.uniform(0,360),rng.uniform(0.9,1.2))
for z in(-50,-10,30,62): put('tree_backdrop',150+rng.uniform(-4,4),0,z,rng.uniform(0,360),1.0)
put('ground_ring',0,RING_Y,0)
json.dump({k:{'objects':v} for k,v in KIT.items()},open(os.path.join(OUT,'edge_geom.json'),'w'))
palette_png(os.path.join(OUT,'edge_palette.png'))
cnt={};[cnt.__setitem__(i['piece'],cnt.get(i['piece'],0)+1) for i in L]
lay=dict(coordinate_frame='game studs, Roblox world: +Y up, north=-Z (top of screen); pos = piece pivot (base centre) placed on the ground it stands on',
  source='Map.luau/World.luau/CameraRig.luau @950e151',rim_ring_top_y=round(RY,2),rotY_units='degrees about +Y',counts=cnt,instances=L)
json.dump(lay,open(os.path.join(OUT,'edge_layout.json'),'w'),indent=1)
json.dump(rep,open(os.path.join(OUT,'edge_box_report.json'),'w'),indent=1)
for k,v in rep.items(): print(k,v)
print(cnt,len(L))
