"""Lobby far-backdrop zones LG2 / SL1 / AU2. Blender 5.2, headless.
blender -b --factory-startup -P build_backdrops.py -- <outdir> [--render]
Built Z-up, 1 unit = 1 stud, Blender +Y = Roblox -Z (north). Each zone built around its pivot
(base centre at sea level), exported with identity transforms, Y-up FBX."""
import bpy, bmesh, sys, os, json, math, random
from mathutils import Vector, Matrix, noise
args = sys.argv[sys.argv.index('--')+1:]
OUT = args[0]; RENDER = '--render' in args
os.makedirs(os.path.join(OUT,'fbx'), exist_ok=True); os.makedirs(os.path.join(OUT,'previews'), exist_ok=True)
random.seed(7)
def hx(h, a=1.0):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return Vector([ (x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4) for x in c])  # linear
HAZE = hx('#F2A57E')
# Zone pivots in Roblox world (x, y, z). Arches: LG (45,0,32) SL (110,0,32) AU (175,0,32); sea level -4.
SPAWN=(100.0,100.0)
S=1.0
def far(ax, rng):
    dx,dz=ax-SPAWN[0],32-SPAWN[1]; L=math.hypot(dx,dz); x=SPAWN[0]+dx/L*rng; z=SPAWN[1]+dz/L*rng
    return (round(x,1),-4,round(z,1)), math.atan2(SPAWN[0]-x, SPAWN[1]-z)
ZONES={}
for zid,c,ax,rng,sc in (('LG2','lantern_grove',45,820,3.2),('SL1','sugarloaf_canyon',110,860,3.0),('AU2','aurora_archipelago',175,820,3.2)):
    p,yaw=far(ax,rng); ZONES[zid]=dict(course=c,pos=p,yaw=yaw,scale=sc,arch=(ax,0,32),range_from_spawn=rng)
class Mesh:
    def __init__(s, name, mat, neon=None):
        s.name=name; s.mat=mat; s.neon=neon; s.bm=bmesh.new(); s.col=s.bm.loops.layers.color.new('Col')
    def faces_of(s, verts): return list({f for v in verts for f in v.link_faces})
    def paint(s, faces, fn, base_y):
        for f in faces:
            c=f.calc_center_median(); col=fn(c)
            wy=c.z*S+base_y
            if wy>30: col=col.lerp(HAZE, min(0.10,(wy-30)/300))  # light tint only; lobby Atmosphere adds the haze
            for l in f.loops: l[s.col]=(col.x,col.y,col.z,1.0)
    def finish(s, coll):
        bmesh.ops.scale(s.bm, vec=Vector((S,S,S)), verts=s.bm.verts)
        me=bpy.data.meshes.new(s.name); s.bm.normal_update(); s.bm.to_mesh(me); s.bm.free()
        o=bpy.data.objects.new(s.name, me); coll.objects.link(o); me.materials.append(s.mat); return o

def jitter(verts, amp, freq, seed=0.0):
    for v in verts:
        n=v.co.normalized() if v.co.length>1e-6 else Vector((0,0,1))
        v.co += v.normal*amp*noise.noise(v.co*freq+Vector((seed,seed*1.3,seed*0.7)))

def ico(M, c, r, sub, fn, base_y, amp=0, freq=0.1, seed=0):
    g=bmesh.ops.create_icosphere(M.bm, subdivisions=sub, radius=1.0); vs=g['verts']
    bmesh.ops.scale(M.bm, vec=Vector(r), verts=vs); bmesh.ops.translate(M.bm, vec=Vector(c), verts=vs)
    M.bm.normal_update()
    if amp: jitter(vs, amp, freq, seed)
    M.paint(M.faces_of(vs), fn, base_y); return vs

def lathe(M, profile, segs, fn, base_y, center=(0,0), amp=0, freq=0.1, seed=0, twist=0, cap_top=True, cap_bot=True):
    rings=[]
    for i,(r,z) in enumerate(profile):
        ring=[]
        for k in range(segs):
            a=2*math.pi*k/segs + twist*i
            ring.append(M.bm.verts.new((center[0]+r*math.cos(a), center[1]+r*math.sin(a), z)))
        rings.append(ring)
    faces=[]
    for i in range(len(rings)-1):
        for k in range(segs):
            a,b=rings[i][k],rings[i][(k+1)%segs]; c,d=rings[i+1][(k+1)%segs],rings[i+1][k]
            faces.append(M.bm.faces.new((a,b,c,d)))
    if cap_bot and profile[0][0]>0.01: faces.append(M.bm.faces.new(list(reversed(rings[0]))))
    if cap_top and profile[-1][0]>0.01: faces.append(M.bm.faces.new(rings[-1]))
    vs=[v for r in rings for v in r]
    M.bm.normal_update()
    if amp: jitter(vs, amp, freq, seed)
    M.paint(faces, fn, base_y); return vs

def tube(M, p0, p1, r0, r1, segs, fn, base_y, rings=2):
    p0=Vector(p0); p1=Vector(p1); d=p1-p0; L=d.length
    prof=[(r0+(r1-r0)*t/(rings-1), L*t/(rings-1)) for t in range(rings)]
    vs=lathe(M, prof, segs, fn, base_y)
    q=Vector((0,0,1)).rotation_difference(d.normalized())
    bmesh.ops.rotate(M.bm, verts=vs, cent=Vector((0,0,0)), matrix=q.to_matrix())
    bmesh.ops.translate(M.bm, vec=p0, verts=vs)
    M.bm.normal_update(); M.paint(M.faces_of(vs), fn, base_y); return vs

def box(M, c, size, fn, base_y, rotz=0):
    g=bmesh.ops.create_cube(M.bm, size=1.0); vs=g['verts']
    bmesh.ops.scale(M.bm, vec=Vector(size), verts=vs)
    if rotz: bmesh.ops.rotate(M.bm, verts=vs, cent=Vector(), matrix=Matrix.Rotation(rotz,3,'Z'))
    bmesh.ops.translate(M.bm, vec=Vector(c), verts=vs); M.paint(M.faces_of(vs), fn, base_y); return vs

def mat_vc(name):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
    a=nt.nodes.new('ShaderNodeVertexColor'); a.layer_name='Col'; nt.links.new(a.outputs[0], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value=0.85; return m
def mat_neon(name, h, strength=3.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    c=hx(h); b.inputs['Base Color'].default_value=(*c,1); b.inputs['Emission Color'].default_value=(*c,1)
    b.inputs['Emission Strength'].default_value=strength; m['neon_hex']=h; return m

bpy.ops.wm.read_factory_settings(use_empty=True)
VC=mat_vc('BD_VC')
const=lambda h: (lambda c, v=hx(h): v)
def grad(h0,h1,z0,z1):
    a,b=hx(h0),hx(h1)
    return lambda c: a.lerp(b, max(0,min(1,(c.z-z0)/(z1-z0))))
zones_objs={}
meta={}

# ---------------- LG2 colossal lantern tree (pass 2) ----------------
def build_LG2(coll, by):
    NE=mat_neon('BD_Neon_Lantern','#FFC867',6)
    isl=Mesh('LG2_island', VC); tree=Mesh('LG2_tree_trunk', VC); can=Mesh('LG2_tree_canopy', VC)
    fill=Mesh('LG2_filler_trees', VC); lan=Mesh('LG2_lanterns_neon', NE, '#FFC867'); caps=Mesh('LG2_lantern_caps', VC)
    def rock(c):
        if c.z>7.2: return hx('#7E8A3C')
        return hx('#4E4664').lerp(hx('#8A7A96'), max(0,min(1,(c.z+3)/10)))
    lathe(isl, [(26,-3),(33,0),(32,3),(30,6),(27,7.6),(14,8.2)], 36, rock, by, amp=2.0, freq=0.11, seed=1)
    for i,(c,r) in enumerate([((-26,-16,1),(9,7,7)),((24,-18,1),(8,7,6)),((30,10,1),(9,8,8)),((-30,12,1),(8,8,7))]):
        ico(isl, c, r, 3, rock, by, amp=1.0, freq=0.15, seed=10+i)
    bark=grad('#4A2F1A','#80583A',8,40)
    prof=[(9,7.5),(7,12),(5.5,18),(5,24),(4.8,30),(5.4,35),(7,39),(6,42)]
    lathe(tree, prof, 24, bark, by, twist=0.32, amp=0.9, freq=0.2, seed=4)
    for k in range(3):   # twisted strands spiralling up the trunk
        pts=[]
        for j in range(9):
            t=j/8; a=k*2.094+t*4.2; r=7.5-3*t+ (1.5 if j in (0,8) else 0)
            pts.append(Vector((r*math.cos(a), r*math.sin(a), 7.5+33*t)))
        for j in range(8): tube(tree, pts[j], pts[j+1], 2.2, 2.0, 8, bark, by)
    for k in range(6):
        a=k*math.pi/3+0.3; tube(tree, (5*math.cos(a),5*math.sin(a),11), (16*math.cos(a),16*math.sin(a),7.4), 2.8, 1.2, 8, bark, by, rings=3)
    for k,(a,el) in enumerate([(0.4,34),(1.9,36),(3.3,33),(4.6,35),(5.6,34)]):
        tube(tree,(0,0,el),(24*math.cos(a),21*math.sin(a),el+9),2.6,1.4,8,bark,by,rings=3)
    cor=lambda c: hx('#F790AC').lerp(hx('#FFD0D4'), max(0,min(1,(c.z-42)/16)))
    blobs=[((0,0,50),(38,33,9)),((-14,6,56),(22,18,7)),((15,-5,56),(22,18,7)),((0,4,61),(16,13,5)),((-26,-8,47),(14,12,6)),((26,8,47),(14,12,6))]
    for i,(c,r) in enumerate(blobs): ico(can, c, r, 4 if i==0 else 3, cor, by, amp=1.5, freq=0.09, seed=20+i)
    rng=random.Random(5)
    for k in range(10):
        a=k*2*math.pi/10+0.2; rr=31+rng.uniform(-2,2); x,y=rr*math.cos(a),rr*math.sin(a)*0.86
        zt=44.5; zl=zt-8-rng.uniform(0,3)
        box(caps,(x,y,(zt+zl+3)/2),(1.0,1.0,zt-zl-3),const('#3A2416'),by)
        lathe(caps,[(3.0,zl+2.4),(1.6,zl+3.6)],8,const('#3A2416'),by,center=(x,y))
        lathe(caps,[(1.6,zl-3.6),(3.0,zl-2.4)],8,const('#3A2416'),by,center=(x,y))
        lathe(lan,[(3.0,zl-2.4),(3.5,zl),(3.0,zl+2.4)],10,const('#FFC867'),by,center=(x,y))
    fc=lambda c: hx('#F48C9E').lerp(hx('#FFC0BC'), max(0,min(1,(c.z-14)/10)))
    for i,(cx,cy) in enumerate([(-30,12),(30,10)]):
        tube(fill,(cx,cy,7),(cx,cy,16),1.8,1.2,8,bark,by)
        ico(fill,(cx,cy,19),(9,8,4.5),3,fc,by,amp=0.6,freq=0.2,seed=30+i)
    return [m.finish(coll) for m in (isl,tree,can,fill,caps,lan)], dict(neon={'LG2_lanterns_neon':'#FFC867'})

# ---------------- SL1 mesas + gondola (pass 2) ----------------
def build_SL1(coll, by):
    NE=mat_neon('BD_Neon_Crystal','#F59AC8',2.5)
    mes=Mesh('SL1_mesas', VC); rig=Mesh('SL1_cable_pylons', VC)
    cab=Mesh('SL1_gondola_cabin', VC); wf=Mesh('SL1_cascade', VC); cry=Mesh('SL1_crystals_neon', NE, '#F59AC8'); flo=Mesh('SL1_shore', VC)
    # pass 3: true mesas - flared talus base, uneven sloped sides, flat tops, uneven strata
    def rnoise(a, z, sd):
        return 1+0.17*noise.noise(Vector((math.cos(a)*1.3+sd, math.sin(a)*1.3, z*0.015)))+0.07*noise.noise(Vector((math.cos(a)*4+sd, math.sin(a)*4, z*0.05)))
    PROF=[(1.8,0.0),(1.5,0.10),(1.28,0.24),(1.15,0.38),(1.06,0.5),(0.98,0.62),(0.92,0.74),(0.86,0.86),(0.81,0.95),(0.78,1.0)]
    def strata(cx,cy,top,sh,sd):
        def f(c):
            if c.z>top-0.05: return hx('#6E9A4A')
            if c.z<top*0.13: return hx('#C9774E').lerp(hx('#D99A6A'),0.5+0.5*noise.noise(c*0.08))
            w=c.z+4.0*noise.noise(Vector((c.x*0.035+sd,c.y*0.035,sd)))+0.07*(c.x-cx)-0.04*(c.y-cy)
            return hx('#D9483B') if int(math.floor(w/sh))%2==0 else hx('#F6E3C8')
        return f
    def mesa(cx,cy,R,top,sd,segs=44):
        rings=[]
        sub=[]
        for i in range(len(PROF)-1):  # densify for strata resolution
            (r0,t0),(r1,t1)=PROF[i],PROF[i+1]
            for k in range(2): sub.append((r0+(r1-r0)*k/2, t0+(t1-t0)*k/2))
        sub.append(PROF[-1])
        for (rf,tf) in [(1.9,-0.06)]+sub:
            z=-3 if tf<0 else top*tf; ring=[]
            for k in range(segs):
                a=2*math.pi*k/segs; r=R*rf*rnoise(a,z,sd)
                ring.append(mes.bm.verts.new((cx+r*math.cos(a),cy+r*math.sin(a),z)))
            rings.append(ring)
        fs=[]
        for i in range(len(rings)-1):
            for k in range(segs):
                fs.append(mes.bm.faces.new((rings[i][k],rings[i][(k+1)%segs],rings[i+1][(k+1)%segs],rings[i+1][k])))
        fs.append(mes.bm.faces.new(rings[-1]))
        mes.bm.normal_update(); mes.paint(fs, strata(cx,cy,top,top/9.5,sd), by)
        return lambda a,z: R*rnoise(a,z,sd)
    # (cx,cy,R,top): A and B tops carry the unchanged gondola pylons (z 47.4 / 55.4); hero mesa off-centre right
    M=[(-30,0,22,47.4),(26,4,19,55.4),(68,18,23,90.0),(-74,28,14,26.0),(-6,42,17,34.0),(-54,-26,8,13.0)]
    rad={}
    for i,(x,y,R,top) in enumerate(M): rad[i]=mesa(x,y,R,top,3.7*i+1)
    lathe(flo,[(40,-3),(66,-0.5),(62,1.2),(40,1.8)],36,grad('#B8664A','#D99A6A',-1,1.8),by,center=(14,12),amp=1.4,freq=0.08,seed=70)
    A=Vector((-30,0,46+1.4)); B=Vector((26,4,54+1.4))
    for p in (A,B):
        box(rig,(p.x,p.y,p.z+5),(2.4,2.4,10),const('#4A2E22'),by); box(rig,(p.x,p.y,p.z+10),(7,2.4,1.8),const('#4A2E22'),by)
    CA=Vector((A.x,A.y,A.z+10)); CB=Vector((B.x,B.y,B.z+10))
    tube(rig,CA,CB,0.9,0.9,8,const('#2E2230'),by)
    mid=CA.lerp(CB,0.5); cabc=Vector((mid.x,mid.y,mid.z-6.5))
    box(cab,cabc,(8,6,6),const('#D02A26'),by)
    box(cab,cabc+Vector((0,0,0.6)),(8.3,6.3,1.8),const('#FFF1DC'),by)
    box(cab,cabc+Vector((0,0,3.4)),(9,7,1.0),const('#7A1E1C'),by)
    box(cab,cabc+Vector((0,0,5.3)),(1.0,1.0,3.0),const('#2E2230'),by)
    # pale cascade down the west-front flank of the hero mesa (clear of the portal pillar from the boardwalk)
    hx_,hy_,HR,HT=M[2]; rf=rad[2]; a=math.radians(-118)
    d=Vector((math.cos(a),math.sin(a),0)); tg=Vector((-d.y,d.x,0))
    rows=[]
    for (pf,tf) in [(0.785,0.985),(0.81,0.95),(0.86,0.86),(0.92,0.74),(0.98,0.62),(1.06,0.5),(1.15,0.38),(1.28,0.24),(1.5,0.10),(1.8,0.0)]:
        z=HT*tf; r=rf(a,z)*pf+1.5; p=Vector((hx_,hy_,z))+d*r; w=4.5+3*(1-tf)
        rows.append([wf.bm.verts.new(p-tg*w),wf.bm.verts.new(p+tg*w)])
    fs=[wf.bm.faces.new((rows[i][0],rows[i][1],rows[i+1][1],rows[i+1][0])) for i in range(len(rows)-1)]
    wf.paint(fs,grad('#F7D6E4','#FFF4F8',0,HT),by); wf.bm.normal_update()
    foot=Vector((hx_,hy_,0))+d*(rf(a,0)*1.8+4)
    ico(wf,(foot.x,foot.y,0.5),(11,8,2.2),2,const('#FFF4F8'),by)
    rng=random.Random(9)
    for (cx,cy) in [(-48,-26),(52,-20),(-4,-34)]:
        for j in range(4):
            a=rng.uniform(0,6.28); h=rng.uniform(6,11); bx,byy=cx+3*math.cos(a),cy+3*math.sin(a)
            tube(cry,(bx,byy,0.5),(bx+rng.uniform(-2,2),byy+rng.uniform(-2,2),1+h),2.0,0.1,6,const('#F59AC8'),by)
    objs=[m.finish(coll) for m in (mes,flo,rig,wf,cab,cry)]
    return objs, dict(neon={'SL1_crystals_neon':'#F59AC8'}, cable_local_unscaled=dict(a=list(CA),b=list(CB)), cabin_centre_local_unscaled=list(cabc))

# ---------------- AU2 floating islands (pass 2) ----------------
def build_AU2(coll, by):
    NC=mat_neon('BD_Neon_Ice','#9FE6F2',1.2); NP=mat_neon('BD_Neon_Amethyst','#B07CF0',2.5)
    ISL=[('main',(0,0),50,20),('left',(-40,12),36,12),('right',(38,-2),40,13)]
    objs=[]; extra={'islands':{}}
    rockf=lambda c: hx('#B0A4D8').lerp(hx('#DCD3F4'), 0.5+0.5*noise.noise(c*0.15))
    for k,(nm,(x,y),top,R) in enumerate(ISL):
        I=Mesh('AU2_island_'+nm, VC); C=Mesh('AU2_crystals_'+nm+'_neon', NC, '#9FE6F2')
        prof=[(0.6,top-2.0*R),(R*0.35,top-1.55*R),(R*0.7,top-1.0*R),(R*0.95,top-0.45*R),(R*1.05,top-0.1*R),(R*0.98,top+0.2)]
        lathe(I,prof,32,rockf,by,center=(x,y),amp=R*0.08,freq=0.18,seed=80+k,twist=0.12)
        ico(I,(x,y,top+0.4),(R*1.03,R*0.98,R*0.34),4 if nm=='main' else 3,const('#FFFFFF'),by,amp=R*0.04,freq=0.2,seed=90+k)
        for j,dx in enumerate((-R*0.4, R*0.32) if nm=='main' else (R*0.1,)):
            L=R*1.5 if nm=='main' else R*1.2
            tube(C,(x+dx,y-R*0.9,top+0.3),(x+dx*1.05,y-R*0.6,top-L),4.5 if nm=='main' else 3.0,1.5,8,const('#BFEFFF'),by,rings=4)  # frozen fall, Neon pale blue
        rng=random.Random(100+k)
        if nm=='main':
            tube(C,(x,y,top+R*0.2),(x+1,y,top+R*0.2+34),6.0,0.2,8,const('#9FE6F2'),by)  # hero ice spire
            for j in range(5):
                a=j*1.256+0.3; bx,byy=x+5*math.cos(a),y+5*math.sin(a)
                tube(C,(bx,byy,top+R*0.2),(bx+2.5*math.cos(a),byy+2.5*math.sin(a),top+R*0.2+rng.uniform(12,20)),3.0,0.15,6,const('#9FE6F2'),by)
        else:
            for j in range(4):
                a=rng.uniform(0,6.28); rr=rng.uniform(0,R*0.4)
                bx,byy=x+rr*math.cos(a),y+rr*math.sin(a)
                tube(C,(bx,byy,top+R*0.2),(bx,byy,top+R*0.2+(10 if j==0 else rng.uniform(4,7))),2.4 if j==0 else 1.5,0.1,6,const('#9FE6F2'),by)
        objs+= [I.finish(coll), C.finish(coll)]
        extra['islands'][nm]=dict(centre_local_unscaled=[x,y,top])
    P=Mesh('AU2_crystals_amethyst_neon', NP, '#B07CF0')
    for (x,y,top,R) in [(0,0,50,20),(38,-2,40,13)]:
        for j in range(3):
            a=j*2.1+0.4; bx,byy=x+R*0.6*math.cos(a),y+R*0.6*math.sin(a)
            tube(P,(bx,byy,top+R*0.15),(bx,byy,top+R*0.15+5),1.6,0.1,6,const('#B07CF0'),by)
    objs.append(P.finish(coll))
    S_=Mesh('AU2_drift_rocks', VC)
    for i,(c,r) in enumerate([((-18,-12,24),3.5),((20,8,20),3),((-58,0,20),3),((60,14,26),3.2)]):
        ico(S_,c,(r,r,r*1.3),2,rockf,by,amp=0.4,freq=0.4,seed=120+i)
    objs.append(S_.finish(coll))
    extra['neon']={'AU2_crystals_main_neon':'#9FE6F2','AU2_crystals_left_neon':'#9FE6F2','AU2_crystals_right_neon':'#9FE6F2','AU2_crystals_amethyst_neon':'#B07CF0'}
    return objs, extra

def tris(o): o.data.calc_loop_triangles(); return len(o.data.loop_triangles)
def rb_bbox(objs):
    vs=[v.co for o in objs for v in o.data.vertices]
    mn=Vector([min(v[i] for v in vs) for i in range(3)]); mx=Vector([max(v[i] for v in vs) for i in range(3)])
    # roblox: X=x, Y=z, Z=-y
    return dict(min=[round(mn.x,2),round(mn.z,2),round(-mx.y,2)], max=[round(mx.x,2),round(mx.z,2),round(-mn.y,2)],
                size=[round(mx.x-mn.x,2),round(mx.z-mn.z,2),round(mx.y-mn.y,2)])

stats={}
ONLY=args[args.index('--only')+1].split(',') if '--only' in args else ['LG2','SL1','AU2']
for zid,fn in [z for z in (('LG2',build_LG2),('SL1',build_SL1),('AU2',build_AU2)) if z[0] in ONLY]:
    coll=bpy.data.collections.new(zid); bpy.context.scene.collection.children.link(coll)
    by=ZONES[zid]['pos'][1]; S=ZONES[zid]['scale']
    objs,extra=fn(coll,by)
    S=1.0; RT=Mesh(zid+'_root', VC); box(RT,(0,0,0),(1,1,1),const('#FFFFFF'),-999); objs.insert(0,RT.finish(coll))  # PrimaryPart, invisible
    zones_objs[zid]=objs
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    path=os.path.join(OUT,'fbx','bd_%s_%s.fbx'%(zid.lower(),ZONES[zid]['course']))
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'}, axis_forward='-Z', axis_up='Y',
        global_scale=1.0, apply_scale_options='FBX_SCALE_UNITS', bake_space_transform=True, mesh_smooth_type='FACE',
        colors_type='SRGB', path_mode='COPY', embed_textures=False, use_mesh_modifiers=True)
    stats[zid]=dict(fbx=os.path.relpath(path,OUT).replace('\\','/'), extra=extra, zone_bbox=rb_bbox(objs),
        meshes=[dict(name=o.name, tris=tris(o), material=o.data.materials[0].name, neon_hex=o.data.materials[0].get('neon_hex'), bbox=rb_bbox([o])) for o in objs])
    stats[zid]['tris']=sum(m['tris'] for m in stats[zid]['meshes'])
    print('ZONE',zid,stats[zid]['tris'])
json.dump(stats, open(os.path.join(OUT,'_src','build_stats%s.json'%('' if len(ONLY)==3 else '_'+'_'.join(ONLY))),'w'), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'_src','backdrops%s.blend'%('' if len(ONLY)==3 else '_'+'_'.join(ONLY))))

if RENDER:
    sc=bpy.context.scene
    sc.render.engine='CYCLES'
    try:
        pr=bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type='OPTIX'; pr.get_devices()
        for d in pr.devices: d.use=True
        sc.cycles.device='GPU'
    except Exception as e: print('gpu',e)
    sc.cycles.samples=32
    if '--cpu' in args: sc.cycles.device='CPU'; print('CPU render'); sc.cycles.use_denoising=True
    sc.render.resolution_x=1280; sc.render.resolution_y=720
    sc.view_settings.view_transform='Standard'
    for zid,objs in zones_objs.items():
        x,y,z=ZONES[zid]['pos']
        for o in objs: o.location=(x,-z,y); o.rotation_euler=(0,0,ZONES[zid]['yaw'])
    w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True; nt=w.node_tree; N=nt.nodes; Lk=nt.links
    bg=N['Background']; tc=N.new('ShaderNodeTexCoord'); sep=N.new('ShaderNodeSeparateXYZ'); ramp=N.new('ShaderNodeValToRGB')
    Lk.new(tc.outputs['Window'],sep.inputs[0]); Lk.new(sep.outputs['Y'],ramp.inputs[0])
    ramp.color_ramp.elements[0].position=0.45; ramp.color_ramp.elements[0].color=(*hx('#F7B27A'),1)
    ramp.color_ramp.elements[1].position=1.0; ramp.color_ramp.elements[1].color=(*hx('#7E4C8E'),1)
    e=ramp.color_ramp.elements.new(0.68); e.color=(*hx('#E8706A'),1)
    amb=N.new('ShaderNodeBackground'); amb.inputs[0].default_value=(*hx('#F4CFC4'),1); amb.inputs[1].default_value=1.1
    bg.inputs[1].default_value=1.0; lp=N.new('ShaderNodeLightPath'); mix=N.new('ShaderNodeMixShader')
    Lk.new(ramp.outputs[0],bg.inputs[0]); Lk.new(lp.outputs['Is Camera Ray'],mix.inputs[0])
    Lk.new(amb.outputs[0],mix.inputs[1]); Lk.new(bg.outputs[0],mix.inputs[2]); Lk.new(mix.outputs[0],N['World Output'].inputs[0])
    sun=bpy.data.lights.new('sun','SUN'); sun.energy=2.6; sun.color=hx('#FFCFA8'); sun.angle=0.05
    so=bpy.data.objects.new('sun',sun); sc.collection.objects.link(so); so.rotation_euler=(math.radians(55),0,math.radians(20))
    sea=bpy.data.meshes.new('sea'); sea.from_pydata([(-3000,-3000,-4),(3000,-3000,-4),(3000,3000,-4),(-3000,3000,-4)],[],[(0,1,2,3)])
    so2=bpy.data.objects.new('sea',sea); sc.collection.objects.link(so2)
    sm=bpy.data.materials.new('seaM'); sm.use_nodes=True; b=sm.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*hx('#6A4E86'),1); b.inputs['Roughness'].default_value=0.25; sea.materials.append(sm)
    deck=bpy.data.meshes.new('deck'); deck.from_pydata([(-50,-140,0),(260,-140,0),(260,-36,0),(-50,-36,0)],[],[(0,1,2,3)])
    do=bpy.data.objects.new('deck',deck); sc.collection.objects.link(do); dm=bpy.data.materials.new('deckM'); dm.use_nodes=True
    dm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*hx('#9A6A44'),1); deck.materials.append(dm)
    # context arches from the lobby kit (if copied alongside)
    for c,(ax,ay,az) in (('lantern_grove',(45,0,32)),('sugarloaf_canyon',(110,0,32)),('aurora_archipelago',(175,0,32))):
        p=os.path.join(OUT,'_ctx','bw_arch_%s.fbx'%c)
        if os.path.exists(p):
            before=set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=p)
            for o in set(bpy.data.objects)-before:
                if o.parent is None: o.location=(ax,-az,ay)
    cam=bpy.data.cameras.new('cam'); cam.lens_unit='FOV'; cam.sensor_fit='HORIZONTAL'; cam.angle=math.radians(62); cam.clip_end=6000
    co=bpy.data.objects.new('cam',cam); sc.collection.objects.link(co); sc.camera=co
    def look(o,t):
        d=Vector(t)-o.location; o.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    def vfov(zid):
        x,_,z=ZONES[zid]['pos']; d=math.hypot(x-SPAWN[0],z-SPAWN[1]); w=110*ZONES[zid]['scale']
        return 2*math.degrees(math.atan(0.85*w/d))
    views={}
    for zid in ONLY:
        x,_,z=ZONES[zid]['pos']; views[zid]=((100,5,100),(x,(118 if zid=='SL1' else 95),z),(vfov(zid)*1.25 if zid=='SL1' else vfov(zid)),zid+'_boardwalk_eye.png')
    if len(ONLY)==3: views['ALL']=((100,5,100),(110,40,-700),100,'all_zones_from_spawn.png')
    for name,(p,t,fov,fn_) in views.items():
        co.location=(p[0],-p[2],p[1]); look(co,(t[0],-t[2],t[1])); cam.angle=math.radians(fov)
        sc.render.filepath=os.path.join(OUT,'previews',fn_)
        bpy.ops.render.render(write_still=True); print('RENDERED',name,round(fov,1))
print('DONE')
