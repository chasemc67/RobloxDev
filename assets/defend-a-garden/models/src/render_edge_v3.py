# Blender: -- workdir  (workdir/edge_layout_v3.json; instance 'path' relative to workdir) -> workdir/prev2/*.png + dump.json
import bpy,sys,json,os,math,mathutils
W=sys.argv[sys.argv.index('--')+1];OUT=os.path.join(W,'out');PV=os.path.join(W,'prev3');os.makedirs(PV,exist_ok=True)
lay=json.load(open(os.path.join(W,'edge_layout_v3.json')))
PATHS={i['piece']:i['path'] for i in lay['instances']};pieces=sorted(PATHS)
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
lib=bpy.data.collections.new('lib');sc.collection.children.link(lib);SRC={};dump={}
for p in pieces:
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=os.path.join(W,*PATHS[p].split('/')))
    obs=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
    for o in obs:
        for c in o.users_collection: c.objects.unlink(o)
        lib.objects.link(o)
    SRC[p]=obs;dg=bpy.context.evaluated_depsgraph_get()
    co=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    dump[p]=dict(tris=sum(len(o.data.polygons) for o in obs),parts=[o.name for o in obs],uv=all(o.data.uv_layers for o in obs),
      min_blender=[round(min(c[i] for c in co),3) for i in range(3)],max_blender=[round(max(c[i] for c in co),3) for i in range(3)])
lib.hide_render=True
json.dump(dump,open(os.path.join(PV,'dump.json'),'w'),indent=1)
def B(x,y,z): return mathutils.Vector((x,-z,y))
def mat(n,c):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*[ (v/255)**2.2 for v in c],1);return m
def rbox(n,center,size,c):
    bpy.ops.mesh.primitive_cube_add(size=1,location=B(*center));o=bpy.context.active_object;o.name=n;o.scale=(size[0],size[2],size[1]);o.data.materials.append(mat(n,c));return o
def place(coll,p,pos,ry,s):
    M=mathutils.Matrix.Translation(B(*pos))@mathutils.Matrix.Rotation(math.radians(ry),4,'Z')@mathutils.Matrix.Scale(s,4)
    for o in SRC[p]:
        d=o.copy();d.matrix_world=M@o.matrix_world;coll.objects.link(d)
def setup(color_type):
    sc.render.engine='BLENDER_WORKBENCH';s=sc.display.shading;s.light='STUDIO';s.color_type=color_type;s.show_cavity=False;s.show_shadows=True
    sc.world=bpy.data.worlds.get('w') or bpy.data.worlds.new('w');sc.world.color=(0.02,0.02,0.02)  # near-black void so gaps show
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
def shoot(name,loc,tgt,rx,ry,fov=None,ortho=None):
    sc.render.resolution_x,sc.render.resolution_y=rx,ry
    if ortho: cam.data.type='ORTHO';cam.data.ortho_scale=ortho
    else: cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.angle_y=math.radians(fov)
    cam.data.clip_end=3000;cam.location=loc;cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=os.path.join(PV,name);bpy.ops.render.render(write_still=True);print('RENDER',name)
setup('TEXTURE')
# ---- 2) layout around a stand-in garden, from the 4 pan-clamp corners at zoom 218
lc=bpy.data.collections.new('layout');sc.collection.children.link(lc);sb=bpy.data.collections.new('standin');sc.collection.children.link(sb)
bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children['standin']
rbox('Lawn',(-2,-3,2),(184,6,150),(120,200,80));rbox('FarBank',(130,-3,2),(60,6,150),(120,200,80));rbox('Rim',(0,-6,0),(420,4,360),(90,170,70))
rbox('River',(97,-1.6,2),(14,4,150),(70,190,255));rbox('Patch',(0,0.2,-47),(50,0.5,26),(130,84,48));rbox('Shed',(-62,4.5,-48),(16,9,12),(190,120,70));rbox('Roof',(-62,10,-48),(18,2,13),(220,70,60))
paths={'bridge':[(112,22),(80,22),(58,22),(46,0),(24,-4),(16,-22),(8,-34)],'south':[(-30,50),(-30,36),(-56,20),(-52,-6),(-22,-12),(-8,-34)]}
for pts in paths.values():
    for (ax,az),(bx,bz) in zip(pts,pts[1:]):
        L=math.hypot(bx-ax,bz-az);o=rbox('Path',((ax+bx)/2,0.12,(az+bz)/2),(12,0.3,L+12*0.0),(214,160,96));o.rotation_euler[2]=math.atan2(-(bx-ax),-(bz-az))
        o2=rbox('PathJ',(bx,0.12,bz),(12,0.3,12),(214,160,96));o2.rotation_euler[2]=math.atan2(-(bx-ax),-(bz-az))
for i in lay['instances']: place(lc,i['piece'],i['pos'],i['rotY'],i['scale'])
D=mathutils.Vector((0,1.45,1)).normalized()*218
for tag,(tx,tz) in {'NW':(-99,-75),'SW':(-99,73)}.items():
    t=mathutils.Vector((tx,0,tz));c=t+D
    shoot(f'layout_{tag}_zoom218.png',B(c.x,c.y,c.z),B(t.x,t.y,t.z),1600,900,fov=40)
shoot('layout_plan_top.png',mathutils.Vector((20,-10,600)),mathutils.Vector((20,-9.999,0)),1600,1000,ortho=560)
print('DONE_RENDER')
