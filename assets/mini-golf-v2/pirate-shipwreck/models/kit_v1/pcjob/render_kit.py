# Blender (Windows PC): -- workdir  (workdir/fbx/kit_*.fbx) -> workdir/prev/3q_<mesh>.png, lineup_*.png, dump.json   (Workbench)
import bpy,sys,json,os,math,mathutils,glob
W=sys.argv[sys.argv.index('--')+1];PV=os.path.join(W,'prev');os.makedirs(PV,exist_ok=True)
NAMES=[os.path.basename(f)[:-4] for f in sorted(glob.glob(os.path.join(W,'fbx','kit_*.fbx')))]
GRP1=['kit_palm_s','kit_palm_m','kit_palm_l','kit_palm_lean_a','kit_palm_lean_b','kit_rock_s','kit_rock_m','kit_rock_l']
GRP2=['kit_leafclump','kit_fernclump','kit_vine_strip','kit_vine_arch','kit_planks','kit_barrel','kit_crate','kit_rope_coil','kit_spar_snapped','kit_hull_rib']
GRP3=['kit_palm_l','kit_stack_a','kit_stack_b','kit_stack_c','kit_reef_ring']
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
    cyl('fl'+tag,(x-0.35,1.0,z),0.3,2.0,(60,70,110));cyl('fr'+tag,(x+0.35,1.0,z),0.3,2.0,(60,70,110))
    rbox('ft'+tag,(x,2.9,z),(1.5,1.8,0.8),(230,70,60));cyl('fa'+tag,(x-1.0,2.9,z),0.22,1.7,(230,70,60));cyl('fb'+tag,(x+1.0,2.9,z),0.22,1.7,(230,70,60))
    sph('fh'+tag,(x,4.3,z),0.7,(240,200,160))
dump={};objs={};orig={}
for n in NAMES:
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=os.path.join(W,'fbx',n+'.fbx'))
    obs=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];objs[n]=obs;orig[n]=[o.location.copy() for o in obs]
    co=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    mn=[min(c[i] for c in co) for i in range(3)];mx=[max(c[i] for c in co) for i in range(3)]
    dump[n]=dict(tris=sum(len(o.data.polygons) for o in obs),objects=[o.name for o in obs],uv=all(o.data.uv_layers for o in obs),
      roblox_min=[round(mn[0],3),round(mn[2],3),round(-mx[1],3)],roblox_max=[round(mx[0],3),round(mx[2],3),round(-mn[1],3)])
    for o in obs: o.hide_render=True
json.dump(dump,open(os.path.join(PV,'dump.json'),'w'),indent=1)
sc.render.engine='BLENDER_WORKBENCH';s=sc.display.shading;s.light='STUDIO';s.color_type='TEXTURE';s.show_cavity=False;s.show_shadows=True
sc.world=bpy.data.worlds.get('w') or bpy.data.worlds.new('w');sc.world.color=(0.55,0.68,0.80)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
def shoot(name,loc,tgt,rx,ry,fov):
    sc.render.resolution_x,sc.render.resolution_y=rx,ry;cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.angle_y=math.radians(fov);cam.data.clip_end=9000
    cam.location=loc;cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler();sc.render.filepath=os.path.join(PV,name);bpy.ops.render.render(write_still=True);print('RENDER',name)
def ground(ext,n):
    col=(120,172,176) if n.startswith('kit_stack') or n=='kit_reef_ring' else (226,184,128)
    return rbox('Ground',(0,-3.02,0),(ext*3,6,ext*3),col)
for n in NAMES:
    for m in NAMES:
        for o in objs[m]: o.hide_render=(m!=n)
    d=dump[n];mn,mx=d['roblox_min'],d['roblox_max'];c=[(mn[i]+mx[i])/2 for i in range(3)];ext=max(mx[0]-mn[0],mx[1]-mn[1],mx[2]-mn[2])
    g=ground(ext,n);dist=ext*1.75;dirv=mathutils.Vector((0.72,0.55,1.0)).normalized()
    shoot('3q_'+n+'.png',B(c[0]+dirv.x*dist,c[1]+dirv.y*dist,c[2]+dirv.z*dist),B(c[0],c[1]*0.9,c[2]),1100,1100,38)
    bpy.data.objects.remove(g,do_unlink=True)
def lineup(fname,order,fig=True):
    for m in NAMES:
        for o in objs[m]: o.hide_render=True
    x=0;pos={};maxh=0;maxd=0
    for n in order:
        d=dump[n];w=d['roblox_max'][0]-d['roblox_min'][0];x+=w/2;pos[n]=x;x+=w/2+10;maxh=max(maxh,d['roblox_max'][1]);maxd=max(maxd,d['roblox_max'][2]-d['roblox_min'][2])
    tot=x-10
    for n in order:
        for o,l in zip(objs[n],orig[n]): o.hide_render=False;o.location=l+B(pos[n]-tot/2-(dump[n]['roblox_min'][0]+dump[n]['roblox_max'][0])/2,0,0)
    rbox('Ground',(0,-3.02,0),(tot+80,6,maxd*1.8+40),(120,172,176) if 'kit_stack_a' in order else (226,184,128))
    if fig:
        for i,n in enumerate(order):
            d=dump[n];figure(pos[n]-tot/2-(d['roblox_max'][0]-d['roblox_min'][0])/2-2.2,min(d['roblox_max'][2],12)-1,str(i))
    dist=max(0.55*tot,1.6*maxh)+maxd*0.3
    shoot(fname,B(0,maxh*0.55+8,dist),B(0,maxh*0.4,0),2400,1000,46)
    for n in order:
        for o,l in zip(objs[n],orig[n]): o.location=l;o.hide_render=True
    for o in [o for o in bpy.data.objects if o.name=='Ground' or o.name[:2] in('fl','fr','ft','fa','fb','fh')]: bpy.data.objects.remove(o,do_unlink=True)
lineup('lineup_trees.png',GRP1);lineup('lineup_ground.png',GRP2);lineup('lineup_backdrop.png',GRP3)
print('DONE_RENDER')
