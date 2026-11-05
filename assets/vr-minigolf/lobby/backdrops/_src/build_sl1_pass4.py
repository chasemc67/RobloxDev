"""SL1 pass 4. Blender 5.2 headless; approved inputs are SHA256 guarded."""
import sys, os, json, math, random, hashlib, atexit
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
OUT=str(Path(args[0]).resolve()); RENDER='--render' in args
ROOT=Path(OUT)
def approved_snapshot():
    paths=sorted(list(ROOT.glob('fbx/*.fbx'))+[ROOT/'manifest.json',ROOT/'_src/build_backdrops.py']+[p for p in ROOT.glob('previews/*') if p.is_file()])
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
APPROVED=approved_snapshot()
EXPECTED=json.loads((ROOT/'_src/sl1_pass4_approved_sha256.json').read_text())
def guard():
    if approved_snapshot()!=APPROVED or APPROVED!=EXPECTED:
        print('ERROR: approved files changed',flush=True); os._exit(1)
guard(); atexit.register(guard)
import bpy,bmesh
from mathutils import Vector,Matrix,noise
bpy.ops.wm.read_factory_settings(use_empty=True)
for d in ('fbx_pass4','previews_pass4'): (ROOT/d).mkdir(exist_ok=True)
PYLON_HEIGHTS=[]
# Behind the cable and between the broad mesas; +Y is away from boardwalk.
SPIRES=[(-98,48,3.5,45),(-48,58,3.5,55),(14,64,3.5,60),(44,62,3,48),(94,62,3.5,42)]
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


VC=mat_vc('BD_VC')
const=lambda h: (lambda c, v=hx(h): v)
def grad(h0,h1,z0,z1):
    a,b=hx(h0),hx(h1)
    return lambda c: a.lerp(b, max(0,min(1,(c.z-z0)/(z1-z0))))
zones_objs={}
meta={}

def build_SL1(coll, by):
    NE=mat_neon('BD_Neon_Crystal','#F59AC8',2.5)
    mes=Mesh('SL1_mesas', VC); rig=Mesh('SL1_cable_pylons', VC)
    cab=Mesh('SL1_gondola_cabin', VC); wf=Mesh('SL1_cascade', VC); cry=Mesh('SL1_crystals_neon', NE, '#F59AC8'); flo=Mesh('SL1_shore', VC)
    # pass 3: true mesas - flared talus base, uneven sloped sides, flat tops, uneven strata
    def rnoise(a, z, sd):
        return 1+0.17*noise.noise(Vector((math.cos(a)*1.3+sd, math.sin(a)*1.3, z*0.015)))+0.07*noise.noise(Vector((math.cos(a)*4+sd, math.sin(a)*4, z*0.05)))
    PROF=[(1.8,0.0),(1.5,0.10),(1.28,0.24),(1.15,0.38),(1.06,0.5),(0.98,0.62),(0.92,0.74),(0.86,0.86),(0.81,0.95),(0.78,1.0)]
    def mesa(cx,cy,R,top,sd,segs=22, target=None):
        target = mes if target is None else target
        sh=top/9.5
        # Isolines follow the original warped strata phase, so rims remain narrow.
        def warp(x,y):
            return 4.0*noise.noise(Vector((x*0.035+sd,y*0.035,sd)))+0.07*(x-cx)-0.04*(y-cy)
        levels=[('profile',top*t) for _,t in PROF]
        for j in range(2,10):
            for off in (-0.8,0.0,0.8): levels.append(('band',j*sh+off))
        levels += [('profile',top-0.85),('profile',top-0.25)]
        levels.sort(key=lambda v:v[1])
        levels=[('profile',-3)]+[v for v in levels if v[1]<top-1.0]+[('profile',top-0.85),('profile',top-0.25),('profile',top)]
        def profile(z):
            if z<0:return 1.9
            t=min(1,z/top)
            for (r0,t0),(r1,t1) in zip(PROF,PROF[1:]):
                if t<=t1:return r0+(r1-r0)*(t-t0)/(t1-t0)
            return PROF[-1][0]
        def wobble(x,y):
            d=math.hypot(x-cx,y-cy)
            fade=0.0 if top in (47.4,55.4) and d<=4 else (min(1,(d-4)/3) if top in (47.4,55.4) else 1)
            return fade*(0.8*math.sin(x*0.13+sd)*math.cos(y*0.11)+0.3*noise.noise(Vector((x*0.07,y*0.07,sd))))
        rings=[]
        for kind,level in levels:
            ring=[]
            for k in range(segs):
                a=2*math.pi*k/segs; z=level
                for _ in range(5):
                    r=R*profile(z)*rnoise(a,z,sd)
                    x,y=cx+r*math.cos(a),cy+r*math.sin(a)
                    if kind=='band':z=level-warp(x,y)
                # Avoid crossing at the base/top while retaining warped boundaries.
                z=max(0.02,min(top-1.1,z)) if kind=='band' else z
                if level>=top-0.85:
                    r*=1+0.018*math.sin(a*5+sd)+0.012*math.sin(a*9-sd)
                    if level==top-0.25:r*=1.025
                    x,y=cx+r*math.cos(a),cy+r*math.sin(a)
                    z+=wobble(x,y)
                ring.append(target.bm.verts.new((x,y,z)))
            rings.append(ring)
        # Sort angular columns to prevent warped strata crossing profile samples.
        for k in range(segs):
            coords=sorted((ring[k].co.copy() for ring in rings),key=lambda v:v.z)
            for ring,co in zip(rings,coords):ring[k].co=co
        def colour(c):
            if c.z>=top-1.05:return hx('#6E9A4A')*0.82
            if c.z<top*0.13:return hx('#C9774E').lerp(hx('#D99A6A'),0.5+0.5*noise.noise(c*0.08))
            phase=c.z+warp(c.x,c.y); band=math.floor(phase/sh)
            col=hx('#D9483B') if band%2==0 else hx('#F6E3C8')
            if min(phase%sh,sh-phase%sh)<=0.81:col*=0.82
            return col
        for i in range(len(rings)-1):
            for k in range(segs):
                f=target.bm.faces.new((rings[i][k],rings[i][(k+1)%segs],rings[i+1][(k+1)%segs],rings[i+1][k]))
                target.paint([f],colour,by)
        # Two inner rings plus a central fan give the top real interior relief.
        outer=rings[-1]
        for fraction in (0.66,0.33,0.12):
            inner=[]
            for v in rings[-1]:
                f=fraction
                if fraction==0.12 and top in (47.4,55.4):
                    f=3.0/math.hypot(v.co.x-cx,v.co.y-cy)
                x=cx+(v.co.x-cx)*f; y=cy+(v.co.y-cy)*f
                inner.append(target.bm.verts.new((x,y,top+wobble(x,y))))
            for k in range(segs):
                f=target.bm.faces.new((outer[k],outer[(k+1)%segs],inner[(k+1)%segs],inner[k]))
                target.paint([f],const('#6E9A4A'),by)
            outer=inner
        centre=target.bm.verts.new((cx,cy,top+wobble(cx,cy)))
        for k in range(segs):target.paint([target.bm.faces.new((outer[k],outer[(k+1)%segs],centre))],const('#6E9A4A'),by)
        if top in (47.4,55.4): PYLON_HEIGHTS.append(dict(centre=[cx,cy],before=top,after=centre.co.z))
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
    sp=Mesh('SL1_spires',VC)
    for i,(x,y,r,h) in enumerate(SPIRES):
        mesa(x,y,r,h,30+i*3.7,segs=8,target=sp)
    objs=[m.finish(coll) for m in (mes,flo,rig,wf,cab,cry,sp)]
    return objs, dict(neon={'SL1_crystals_neon':'#F59AC8'}, cable_local_unscaled=dict(a=list(CA),b=list(CB)), cabin_centre_local_unscaled=list(cabc))


def tris(o): o.data.calc_loop_triangles(); return len(o.data.loop_triangles)
def rb_bbox(objs):
    vs=[v.co for o in objs for v in o.data.vertices]
    mn=Vector([min(v[i] for v in vs) for i in range(3)]); mx=Vector([max(v[i] for v in vs) for i in range(3)])
    # roblox: X=x, Y=z, Z=-y
    return dict(min=[round(mn.x,2),round(mn.z,2),round(-mx.y,2)], max=[round(mx.x,2),round(mx.z,2),round(-mn.y,2)],
                size=[round(mx.x-mn.x,2),round(mx.z-mn.z,2),round(mx.y-mn.y,2)])


def main():
    global S
    baseline=json.loads((ROOT/'manifest.json').read_text())
    old=baseline['zones']['SL1']
    coll=bpy.data.collections.new('SL1'); bpy.context.scene.collection.children.link(coll)
    S=3.0
    objs,extra=build_SL1(coll,-4)
    S=1.0
    rt=Mesh('SL1_root',VC);box(rt,(0,0,0),(1,1,1),const('#FFFFFF'),-999)
    objs.insert(0,rt.finish(coll))
    result=json.loads(json.dumps(old))
    result['fbx']='fbx_pass4/bd_sl1_sugarloaf_canyon_pass4.fbx'
    result['meshes']=[dict(name=o.name,tris=tris(o),material=o.data.materials[0].name,neon_hex=o.data.materials[0].get('neon_hex'),bbox=rb_bbox([o])) for o in objs]
    result['tris']=sum(m['tris'] for m in result['meshes']);result['bbox']=rb_bbox(objs)
    result['pass']='pass 4: organic mesa caps, darker strata rims, five backdrop hoodoos'
    result['decoration']=dict(Anchored=True,CanCollide=False,CanQuery=False,CanTouch=False)
    from mathutils.bvhtree import BVHTree
    mesa_object=next(o for o in objs if o.name=='SL1_mesas')
    tree=BVHTree.FromObject(mesa_object,bpy.context.evaluated_depsgraph_get())
    for record in PYLON_HEIGHTS:
        cx,cy=record['centre'];samples=[]
        for dx,dy in ((0,0),(-1.2,-1.2),(-1.2,1.2),(1.2,-1.2),(1.2,1.2)):
            hit=tree.ray_cast(Vector(((cx+dx)*3,(cy+dy)*3,400)),Vector((0,0,-1)))
            if hit[0] is None:raise RuntimeError('Missing pylon footprint surface')
            samples.append(hit[0].z/3)
        record['footprint_samples']=samples
    result['pylon_top_heights_unscaled']=PYLON_HEIGHTS
    result['spires_local_unscaled']=[dict(centre=[x,y],radius=r,height=h) for x,y,r,h in SPIRES]
    # Store actual scaled mesh vertices for independent corridor checks (not centre-only).
    result['spires_vertices_local_scaled']=[list(v.co) for v in objs[-1].data.vertices]
    for m in result['meshes']:print('MESH',m['name'],m['tris'])
    if result['tris']>15000:raise RuntimeError('SL1 triangle budget exceeded: '+str(result['tris']))
    for m in result['meshes']:
        if m['name'] not in ('SL1_mesas','SL1_spires'):
            approved=next(v for v in old['meshes'] if v['name']==m['name'])
            if m!=approved:raise RuntimeError('Fixed mesh changed: '+m['name'])
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    path=str(ROOT/result['fbx'])
    bpy.ops.export_scene.fbx(filepath=path,use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',global_scale=1.0,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=True,mesh_smooth_type='FACE',colors_type='SRGB',path_mode='COPY',embed_textures=False,use_mesh_modifiers=True)
    (ROOT/'manifest_sl1_pass4.json').write_text(json.dumps(result,indent=2)+'\n')
    if RENDER:render_comparison(objs,old)
    # Fresh scene import validates the delivered FBX, not the source meshes.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path)
    imported=[o for o in bpy.context.scene.objects if o.type=='MESH']
    for o in imported:
        bpy.context.view_layer.objects.active=o;o.select_set(True)
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.select_set(False)
    checks=[]
    for o in imported:
        want=next((m for m in result['meshes'] if m['name']==o.name),None)
        bbox=rb_bbox([o]);count=tris(o)
        ok=want is not None and count==want['tris'] and all(abs(bbox[k][i]-want['bbox'][k][i])<=0.03 for k in ('min','max','size') for i in range(3))
        checks.append(dict(name=o.name,tris=count,bbox=bbox,pass_check=ok))
    all_pass=len(checks)==len(result['meshes']) and all(c['pass_check'] for c in checks)
    (ROOT/'_src/reimport_sl1_pass4.json').write_text(json.dumps(dict(meshes=checks,bbox=rb_bbox(imported),all_pass=all_pass),indent=2)+'\n')
    if not all_pass:raise RuntimeError('FBX reimport validation failed')
    guard();print('DONE SL1 pass 4')

def render_comparison(after,old):
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32
    sc.cycles.device='CPU';sc.cycles.use_denoising=True
    sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
    sc.view_settings.view_transform='Standard'
    x,y,z=old['position'];yaw=ZONES['SL1']['yaw']
    def place(objects):
        for o in objects:o.location=(x,-z,y);o.rotation_euler=(0,0,yaw)
    place(after)
    # Import the approved pass-3 FBX for all before images.
    existing=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(ROOT/old['fbx']))
    before=[o for o in set(bpy.data.objects)-existing if o.type=='MESH']
    for o in before:
        o.name='BEFORE_'+o.name
        if 'crystals_neon' in o.name:
            o.data.materials.clear();o.data.materials.append(next(o2.data.materials[0] for o2 in after if o2.name=='SL1_crystals_neon'))
        else:
            o.data.materials.clear();o.data.materials.append(VC)
        bpy.context.view_layer.objects.active=o;o.select_set(True)
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.select_set(False)
    place(before)
    world=bpy.data.worlds.new('Pass4World');sc.world=world;world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(*hx('#F4CFC4'),1)
    world.node_tree.nodes['Background'].inputs[1].default_value=1.1
    sun=bpy.data.lights.new('sun','SUN');sun.energy=2.6;sun.color=hx('#FFCFA8');sun.angle=0.05
    so=bpy.data.objects.new('sun',sun);sc.collection.objects.link(so);so.rotation_euler=(math.radians(55),0,math.radians(20))
    context=[]
    for name,verts,col in [('sea',[(-3000,-3000,-4),(3000,-3000,-4),(3000,3000,-4),(-3000,3000,-4)],'#6A4E86'),('deck',[(-50,-140,0),(260,-140,0),(260,-36,0),(-50,-36,0)],'#9A6A44')]:
        me=bpy.data.meshes.new(name);me.from_pydata(verts,[],[(0,1,2,3)])
        o=bpy.data.objects.new(name,me);sc.collection.objects.link(o)
        m=bpy.data.materials.new(name+'M');m.diffuse_color=(*hx(col),1);me.materials.append(m);context.append(o)
    for course,ax in [('lantern_grove',45),('sugarloaf_canyon',110),('aurora_archipelago',175)]:
        path=ROOT/('_ctx/bw_arch_'+course+'.fbx')
        if path.exists():
            existing=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(path))
            added=list(set(bpy.data.objects)-existing);context+=added
            for o in added:
                if o.parent is None:o.location=(ax,-32,0)
    cam=bpy.data.cameras.new('cam');cam.lens_unit='FOV';cam.sensor_fit='HORIZONTAL';cam.clip_end=6000
    co=bpy.data.objects.new('cam',cam);sc.collection.objects.link(co);sc.camera=co
    # Exact pass-3 boardwalk camera formula and target.
    fov=2*math.atan(0.85*110*3/math.hypot(x-100,z-100))*1.25
    views=[('boardwalk_eye',(100,-100,5),(x,-z,118),fov),('34',(x+640,-z-640,430),(x,-z,105),math.radians(52))]
    black=bpy.data.materials.new('SilhouetteBlack');black.use_nodes=True
    nt=black.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(0,0,0,1);nt.links.new(em.outputs[0],out.inputs[0])
    for label,objects,other in [('before',before,after),('after',after,before)]:
        for o in other:o.hide_render=True
        for o in objects:o.hide_render=o.name.endswith('_root')
        for view,eye,target,angle in views:
            co.location=eye;co.rotation_euler=(Vector(target)-co.location).to_track_quat('-Z','Y').to_euler();cam.angle=angle
            sc.view_layers[0].material_override=None
            for o in context:o.hide_render=False
            world.node_tree.nodes['Background'].inputs[0].default_value=(*hx('#F4CFC4'),1)
            name=('SL1_'+view+'.png') if label=='after' else ('SL1_before_'+view+'.png')
            sc.render.filepath=str(ROOT/'previews_pass4'/name);bpy.ops.render.render(write_still=True)
            sc.view_layers[0].material_override=black
            for o in context:o.hide_render=True
            world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1)
            world.node_tree.nodes['Background'].inputs[1].default_value=1.0
            sc.render.film_transparent=False
            sc.render.filepath=str(ROOT/'previews_pass4'/('SL1_'+label+'_'+view+'_silhouette.png'));bpy.ops.render.render(write_still=True)
            # Threshold antialiased edges to produce literal black on white PNGs.
            image=bpy.data.images.load(sc.render.filepath,check_existing=False)
            pixels=list(image.pixels[:])
            for i in range(0,len(pixels),4):
                val=1.0 if pixels[i]>=0.5 else 0.0;pixels[i:i+4]=[val,val,val,1.0]
            image.pixels[:]=pixels;image.filepath_raw=sc.render.filepath;image.file_format='PNG';image.save();bpy.data.images.remove(image)
            world.node_tree.nodes['Background'].inputs[1].default_value=1.1
    sc.view_layers[0].material_override=None

if __name__=='__main__':
    try:main()
    except Exception:
        import traceback
        traceback.print_exc();guard();sys.exit(1)
