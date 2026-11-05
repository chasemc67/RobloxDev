# Blender (Windows PC): -- workdir   (workdir/fbx/*.fbx, workdir/assembly.json) -> workdir/prev/*.png + dump.json
import bpy,sys,json,os,math,mathutils
W=sys.argv[sys.argv.index('--')+1];PV=os.path.join(W,'prev');os.makedirs(PV,exist_ok=True)
asm=json.load(open(os.path.join(W,'assembly.json')))
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
def B(x,y,z): return mathutils.Vector((x,-z,y))
P=mathutils.Matrix(((1,0,0),(0,0,-1),(0,1,0)))      # Roblox->Blender basis change
dump={};objs={}
for p in ('wreck_hull','wreck_rig','wreck_glow','wreck_duck'):
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=os.path.join(W,'fbx',p+'.fbx'))
    obs=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];objs[p]=obs
    co=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    dump[p]=dict(tris=sum(len(o.data.polygons) for o in obs),objects=[o.name for o in obs],uv=all(o.data.uv_layers for o in obs),
      min_blender=[round(min(c[i] for c in co),3) for i in range(3)],max_blender=[round(max(c[i] for c in co),3) for i in range(3)])
# assemble the duck (own pivot): rotation R (Roblox frame) + position
R=mathutils.Matrix(asm['rotation3x3']);Rb=(P@R@P.inverted()).to_4x4();M=mathutils.Matrix.Translation(B(*asm['position']))@Rb
for o in objs['wreck_duck']:
    o.parent=None;o.matrix_world=M@o.matrix_world
json.dump(dump,open(os.path.join(PV,'dump.json'),'w'),indent=1)
def mat(n,c):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*[(v/255)**2.2 for v in c],1);return m
def rbox(n,center,size,c):
    bpy.ops.mesh.primitive_cube_add(size=1,location=B(*center));o=bpy.context.active_object;o.name=n;o.scale=(size[0],size[2],size[1]);o.data.materials.append(mat(n,c));return o
def setup():
    sc.render.engine='BLENDER_WORKBENCH';s=sc.display.shading;s.light='STUDIO';s.color_type='TEXTURE';s.show_cavity=False;s.show_shadows=True
    sc.world=bpy.data.worlds.get('w') or bpy.data.worlds.new('w');sc.world.color=(0.55,0.68,0.80)
setup()
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
def shoot(name,loc,tgt,rx,ry,fov=None,ortho=None):
    sc.render.resolution_x,sc.render.resolution_y=rx,ry
    if ortho: cam.data.type='ORTHO';cam.data.ortho_scale=ortho
    else: cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.angle_y=math.radians(fov)
    cam.data.clip_end=4000;cam.location=loc;cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=os.path.join(PV,name);bpy.ops.render.render(write_still=True);print('RENDER',name)
# duck centre (world, Blender frame) for the close-up
dco=[o.matrix_world@v.co for o in objs['wreck_duck'] for v in o.data.vertices];dc=sum(dco,mathutils.Vector())/len(dco)
# --- no-water views first (hull draft visible)
shoot('side_nowater.png',B(-560,40,-5),B(0,35,0),1800,900,ortho=380)
shoot('top.png',mathutils.Vector((0,-5,700)),mathutils.Vector((0,-4.999,0)),1000,1400,ortho=400)
shoot('front_bow.png',B(0,60,700),B(0,45,0),1000,1000,fov=40)
# duck close-up (in front of the bow, from the lagoon side)
shoot('duck_closeup.png',dc+B(-22,10,44),dc+B(0,0,0),1200,1200,fov=32)
# --- with a water plane at y=0 (water-line origin) and a sand slab behind the stern
rbox('Water',(0,-6,0),(900,12,1300),(60,150,170));rbox('Sand',(0,-4,-370),(900,18,420),(224,184,120))
shoot('3q.png',B(-330,150,-330),B(0,40,0),1800,1100,fov=45)
shoot('3q_bow.png',B(-300,120,330),B(0,40,0),1800,1100,fov=45)
shoot('side.png',B(-560,40,-5),B(0,35,0),1800,900,ortho=380)
print('DONE_RENDER')
