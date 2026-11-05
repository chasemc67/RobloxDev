# Blender (Windows PC): -- workdir  (workdir/fbx/prop_*.fbx) -> workdir/prev/3q_<prop>.png, lineup.png, dump.json   (Workbench)
import bpy,sys,json,os,math,mathutils
W=sys.argv[sys.argv.index('--')+1];PV=os.path.join(W,'prev');os.makedirs(PV,exist_ok=True)
NAMES=['prop_cannon','prop_coconut','prop_flytrap','prop_croc','prop_captain']
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
def B(x,y,z): return mathutils.Vector((x,-z,y))
def mat(n,c):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*[(v/255) for v in c],1);return m
def rbox(n,center,size,c):
    bpy.ops.mesh.primitive_cube_add(size=1,location=B(*center));o=bpy.context.active_object;o.name=n;o.scale=(size[0],size[2],size[1]);o.data.materials.append(mat(n,c));return o
def cyl(n,center,r,h,c):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=h,vertices=10,location=B(*center));o=bpy.context.active_object;o.name=n;o.data.materials.append(mat(n,c));return o
def sph(n,center,r,c):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r,segments=10,ring_count=6,location=B(*center));o=bpy.context.active_object;o.name=n;o.data.materials.append(mat(n,c));return o
def figure(x,z,tag):
    # 5-stud scale figure: legs 0..2, torso 2..3.8, head sphere to 5.0
    cyl('fl'+tag,(x-0.35,1.0,z),0.3,2.0,(60,70,110));cyl('fr'+tag,(x+0.35,1.0,z),0.3,2.0,(60,70,110))
    rbox('ft'+tag,(x,2.9,z),(1.5,1.8,0.8),(230,70,60));cyl('fa'+tag,(x-1.0,2.9,z),0.22,1.7,(230,70,60));cyl('fb'+tag,(x+1.0,2.9,z),0.22,1.7,(230,70,60))
    sph('fh'+tag,(x,4.3,z),0.7,(240,200,160))
dump={};objs={}
for n in NAMES:
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=os.path.join(W,'fbx',n+'.fbx'))
    obs=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];objs[n]=obs
    co=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    mn=[min(c[i] for c in co) for i in range(3)];mx=[max(c[i] for c in co) for i in range(3)]
    # blender -> roblox: x=bx, y=bz, z=-by
    dump[n]=dict(tris=sum(len(o.data.polygons) for o in obs),objects=[o.name for o in obs],uv=all(o.data.uv_layers for o in obs),
      roblox_min=[round(mn[0],3),round(mn[2],3),round(-mx[1],3)],roblox_max=[round(mx[0],3),round(mx[2],3),round(-mn[1],3)])
    for o in obs: o.hide_render=True
json.dump(dump,open(os.path.join(PV,'dump.json'),'w'),indent=1)
sc.render.engine='BLENDER_WORKBENCH';s=sc.display.shading;s.light='STUDIO';s.color_type='TEXTURE';s.show_cavity=False;s.show_shadows=True
sc.world=bpy.data.worlds.get('w') or bpy.data.worlds.new('w');sc.world.color=(0.55,0.68,0.80)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
def shoot(name,loc,tgt,rx,ry,fov):
    sc.render.resolution_x,sc.render.resolution_y=rx,ry;cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.angle_y=math.radians(fov);cam.data.clip_end=6000
    cam.location=loc;cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler();sc.render.filepath=os.path.join(PV,name);bpy.ops.render.render(write_still=True);print('RENDER',name)
# per-prop 3q: front (+Z) toward the camera, from the front-right and above
for n in NAMES:
    for m in NAMES:
        for o in objs[m]: o.hide_render=(m!=n)
    d=dump[n];mn,mx=d['roblox_min'],d['roblox_max'];c=[(mn[i]+mx[i])/2 for i in range(3)];ext=max(mx[0]-mn[0],mx[1]-mn[1],mx[2]-mn[2])
    g=rbox('Ground',(0,-3.3,0),(ext*3,6,ext*3),(226,184,128))
    dist=ext*1.75;dirv=mathutils.Vector((0.72,0.55,1.0)).normalized()
    shoot('3q_'+n+'.png',B(c[0]+dirv.x*dist,c[1]+dirv.y*dist,c[2]+dirv.z*dist),B(c[0],c[1]*0.9,c[2]),1100,1100,38)
    bpy.data.objects.remove(g,do_unlink=True)
# lineup: all five in a row (front toward camera) with a 5-stud figure beside each
order=['prop_cannon','prop_flytrap','prop_croc','prop_captain','prop_coconut'];x=0;pos={}
for n in order:
    d=dump[n];w=d['roblox_max'][0]-d['roblox_min'][0];x+=w/2;pos[n]=x;x+=w/2+10
tot=x-10
for m in NAMES:
    for o in objs[m]: o.hide_render=False;o.location=o.location+B(pos[m]-tot/2,0,0)
rbox('Ground',(0,-3.3,0),(tot+60,6,120),(226,184,128))
for i,n in enumerate(order):
    d=dump[n];figure(pos[n]-tot/2-(d['roblox_max'][0]-d['roblox_min'][0])/2-2.2,max(d['roblox_max'][2],8)-2,str(i))
shoot('lineup.png',B(0,32,tot*0.7),B(0,25,0),2400,1000,46)
print('DONE_RENDER')
