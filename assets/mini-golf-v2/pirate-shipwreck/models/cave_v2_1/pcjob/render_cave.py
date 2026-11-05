# Blender (Windows PC): -- workdir   (workdir/fbx/cave_*.fbx, workdir/overlay.json) -> workdir/prev/*.png + dump.json
import bpy,sys,json,os,math,mathutils
W=sys.argv[sys.argv.index('--')+1];ONLY=sys.argv[sys.argv.index('--')+2].split(',') if len(sys.argv)>sys.argv.index('--')+2 else None;PV=os.path.join(W,'prev');os.makedirs(PV,exist_ok=True)
ov=json.load(open(os.path.join(W,'overlay.json')))
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
def B(x,y,z): return mathutils.Vector((x,-z,y))
PARTS=['cave_cliff_lower','cave_cliff_upper','cave_stairs','cave_water','cave_glow','cave_foliage'];objs={};dump={}
for p in PARTS:
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=os.path.join(W,'fbx',p+'.fbx'))
    obs=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];objs[p]=obs
    co=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    dump[p]=dict(tris=sum(len(o.data.polygons) for o in obs),objects=[o.name for o in obs],uv=all(o.data.uv_layers for o in obs),
      min_blender=[round(min(c[i] for c in co),3) for i in range(3)],max_blender=[round(max(c[i] for c in co),3) for i in range(3)])
json.dump(dump,open(os.path.join(PV,'dump.json'),'w'),indent=1)
def mat(n,c):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*[(v/255)**2.2 for v in c],1);return m
def rbox(n,center,size,c,yaw=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=B(*center));o=bpy.context.active_object;o.name=n;o.scale=(size[0],size[2],size[1]);o.rotation_euler[2]=math.radians(yaw);o.data.materials.append(mat(n,c));return o
sc.render.engine='BLENDER_WORKBENCH';s=sc.display.shading;s.light='STUDIO';s.color_type='TEXTURE';s.show_cavity=False;s.show_shadows=True
sc.world=bpy.data.worlds.get('w') or bpy.data.worlds.new('w');sc.world.color=(0.55,0.68,0.80)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
def shoot(name,loc,tgt,rx,ry,fov=None,ortho=None):
    if ONLY and name[:-4] not in ONLY: return
    sc.render.resolution_x,sc.render.resolution_y=rx,ry
    if ortho: cam.data.type='ORTHO';cam.data.ortho_scale=ortho
    else: cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.angle_y=math.radians(fov)
    cam.data.clip_end=6000;cam.location=loc;cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=os.path.join(PV,name);bpy.ops.render.render(write_still=True);print('RENDER',name)
# --- local-frame views on a plain ground slab (top at y=-0.3)
g=rbox('Ground',(0,-3.3,0),(420,6,320),(120,100,70))
shoot('3q.png',B(-250,190,330),B(0,62,0),1800,1100,fov=45)
shoot('3q_east.png',B(260,170,300),B(0,62,0),1800,1100,fov=45)
shoot('front.png',B(0,75,600),B(0,70,0),1800,1100,fov=38)
shoot('top.png',mathutils.Vector((0,0,700)),mathutils.Vector((0,0,-1)),1600,1200,ortho=300)
shoot('side_west.png',B(-560,75,0),B(0,72,0),1800,1000,ortho=300)
shoot('mouth_closeup.png',B(20,52,200),B(20,52,20),1400,1000,fov=42)
shoot('tunnel_depth.png',B(20,40,120),B(20,44,-25),1400,1000,fov=28)
shoot('waterfall_closeup.png',B(-80,70,190),B(-80,70,20),1400,1000,fov=45)
bpy.data.objects.remove(g,do_unlink=True)
if ONLY: print('DONE_RENDER');sys.exit(0)
# --- world overlay: terrain from heightmap + pads (felt, rim, art-clear outline) with the cave at its placement
C=ov['cave_centre']
for p in PARTS:
    for o in objs[p]: o.location=o.location+B(*C)
me=bpy.data.meshes.new('terrain');me.from_pydata([B(*v) for v in ov['verts']],[],[tuple(t) for t in ov['tris']]);me.validate();me.update()
me.materials.append(mat('terrain',(176,150,100)));t=bpy.data.objects.new('terrain',me);sc.collection.objects.link(t)
for pd in ov['pads']:
    x,y,z=pd['pos'];yaw=pd['yaw']
    rbox('rim%d'%pd['n'],(x,y-1.0,z),(pd['outer'][0],1.2,pd['outer'][1]),(70,76,92),yaw)
    rbox('felt%d'%pd['n'],(x,y-0.35,z),(pd['felt'][0],0.8,pd['felt'][1]),(100,230,135),yaw)
    ax,az=pd['clear'];th=math.radians(yaw);X=mathutils.Vector((math.cos(th),0,-math.sin(th)));Z=mathutils.Vector((math.sin(th),0,math.cos(th)))
    for (cx,cz,sx,sz) in((0,az/2,ax,1.2),(0,-az/2,ax,1.2),(ax/2,0,1.2,az),(-ax/2,0,1.2,az)):
        c=mathutils.Vector((x,y+0.4,z))+X*cx+Z*cz;rbox('clr',(c.x,c.y,c.z),(sx,0.6,sz),(255,60,200),yaw)
cx,cy,cz=C
shoot('overlay_top_wide.png',mathutils.Vector((250,520,800)),mathutils.Vector((250,520,-1)),1800,1000,ortho=1400)  # Blender y = -Roblox z -> centre z=-520
shoot('overlay_top_close.png',B(563,900,-560),B(563,0,-560),1600,1200,ortho=430)
shoot('overlay_3q.png',B(330,330,-250),B(540,110,-560),1800,1100,fov=42)
shoot('overlay_front.png',B(580,140,-300),B(570,110,-560),1800,1100,fov=40)
print('DONE_RENDER')
