# Blender (Windows PC): -- workdir (workdir/fbx/kit_*.fbx) -> workdir/prev/3q_<mesh>.png, lineup_*.png, dump.json (Workbench)
import bpy,sys,json,os,math,mathutils,glob
W=sys.argv[sys.argv.index('--')+1];PV=os.path.join(W,'prev');os.makedirs(PV,exist_ok=True)
NAMES=[os.path.basename(f)[:-4] for f in sorted(glob.glob(os.path.join(W,'fbx','kit_*.fbx')))]
GROUPS=[('lineup_set1.png',['kit_hut_leanto','kit_ruin_arch','kit_ruin_wall']),('lineup_set2.png',['kit_boulder_pile','kit_crate_stack','kit_rowboat_broken']),
 ('lineup_lights.png',['kit_torch_tiki','kit_torch_tiki_short','kit_lantern_hanging','kit_lantern_post']),
 ('lineup_skyline.png',['kit_canopy_wall','kit_cliff_ridge']),
 ('lineup_rocks.png',['kit_rock_s','kit_rock_m','kit_rock_l'])]
LIFT={'kit_lantern_hanging':6.0}
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
def figure(x,z,tag,s=1.2):  # NB 5-stud base x1.2  # 6-stud player figure
    cyl('fl'+tag,(x-0.35*s,1.0*s,z),0.3*s,2.0*s,(60,70,110));cyl('fr'+tag,(x+0.35*s,1.0*s,z),0.3*s,2.0*s,(60,70,110))
    rbox('ft'+tag,(x,2.9*s,z),(1.5*s,1.8*s,0.8*s),(230,70,60));cyl('fa'+tag,(x-1.0*s,2.9*s,z),0.22*s,1.7*s,(230,70,60));cyl('fb'+tag,(x+1.0*s,2.9*s,z),0.22*s,1.7*s,(230,70,60))
    sph('fh'+tag,(x,4.3*s,z),0.7*s,(240,200,160))
dump={};objs={};orig={}
for n in NAMES:
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=os.path.join(W,'fbx',n+'.fbx'))
    new=[o for o in bpy.data.objects if o not in before]
    obs=[o for o in new if o.type=='MESH'];emp=[o for o in new if o.type=='EMPTY'];objs[n]=obs;orig[n]=[o.location.copy() for o in obs]
    co=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    mn=[min(c[i] for c in co) for i in range(3)];mx=[max(c[i] for c in co) for i in range(3)]
    dump[n]=dict(tris=sum(len(o.data.polygons) for o in obs),objects=[o.name for o in obs],obj_tris={o.name:len(o.data.polygons) for o in obs},
      materials={o.name:[m.name for m in o.data.materials] for o in obs},uv=all(o.data.uv_layers for o in obs),
      empties={e.name:[round(e.matrix_world.translation[0],3),round(e.matrix_world.translation[2],3),round(-e.matrix_world.translation[1],3)] for e in emp},
      roblox_min=[round(mn[0],3),round(mn[2],3),round(-mx[1],3)],roblox_max=[round(mx[0],3),round(mx[2],3),round(-mn[1],3)])
    for o in obs: o.hide_render=True
    for e in emp: e.hide_render=True
json.dump(dump,open(os.path.join(PV,'dump.json'),'w'),indent=1)
sc.render.engine='BLENDER_WORKBENCH';s=sc.display.shading;s.light='STUDIO';s.color_type='TEXTURE';s.show_cavity=False;s.show_shadows=True
sc.world=bpy.data.worlds.get('w') or bpy.data.worlds.new('w');sc.world.color=(0.55,0.68,0.80)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
def shoot(name,loc,tgt,rx,ry,fov):
    sc.render.resolution_x,sc.render.resolution_y=rx,ry;cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.angle_y=math.radians(fov);cam.data.clip_end=9000
    cam.location=loc;cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler();sc.render.filepath=os.path.join(PV,name);bpy.ops.render.render(write_still=True);print('RENDER',name)
def ground(ext,n,ytop):
    col=(226,184,128)
    return rbox('Ground',(0,ytop-3.0,0),(ext*3,6,ext*3),col)
for n in NAMES:
    for m in NAMES:
        for o in objs[m]: o.hide_render=(m!=n)
    d=dump[n];mn,mx=d['roblox_min'],d['roblox_max'];c=[(mn[i]+mx[i])/2 for i in range(3)];ext=max(mx[0]-mn[0],mx[1]-mn[1],mx[2]-mn[2])
    ytop=-0.02 if mn[1]>-2.5 and n!='kit_lantern_hanging' else (mn[1]-0.05 if n=='kit_lantern_hanging' else -0.02)
    g=ground(ext,n,ytop);dist=ext*2.1;dirv=mathutils.Vector((0.72,0.55,1.0)).normalized()
    shoot('3q_'+n+'.png',B(c[0]+dirv.x*dist,c[1]+dirv.y*dist,c[2]+dirv.z*dist),B(c[0],c[1]*0.9 if n!='kit_lantern_hanging' else c[1],c[2]),1100,1100,38)
    bpy.data.objects.remove(g,do_unlink=True)
def lineup(fname,order,fig=True):
    for m in NAMES:
        for o in objs[m]: o.hide_render=True
    x=0;pos={};maxh=0;maxd=0
    for n in order:
        d=dump[n];w=d['roblox_max'][0]-d['roblox_min'][0];x+=w/2;pos[n]=x;x+=w/2+10;maxh=max(maxh,d['roblox_max'][1]+LIFT.get(n,0));maxd=max(maxd,d['roblox_max'][2]-d['roblox_min'][2])
    tot=x-10
    for n in order:
        for o,l in zip(objs[n],orig[n]): o.hide_render=False;o.location=l+B(pos[n]-tot/2-(dump[n]['roblox_min'][0]+dump[n]['roblox_max'][0])/2,LIFT.get(n,0),0)
    rbox('Ground',(0,-3.02,0),(tot+80,6,maxd*1.8+40),(226,184,128))
    if fig:
        for i,n in enumerate(order):
            d=dump[n];figure(pos[n]-tot/2-(d['roblox_max'][0]-d['roblox_min'][0])/2-2.2,min(d['roblox_max'][2],12)-1,str(i))
    dist=max(0.5*tot,1.5*maxh)+maxd*0.2
    shoot(fname,B(0,maxh*0.55+8,dist),B(0,maxh*0.4,0),2400,1000,46)
    for n in order:
        for o,l in zip(objs[n],orig[n]): o.location=l;o.hide_render=True
    for o in [o for o in bpy.data.objects if o.name=='Ground' or o.name[:2] in('fl','fr','ft','fa','fb','fh')]: bpy.data.objects.remove(o,do_unlink=True)
for fn,order in GROUPS:
    order=[n for n in order if n in dump]
    if order: lineup(fn,order)
