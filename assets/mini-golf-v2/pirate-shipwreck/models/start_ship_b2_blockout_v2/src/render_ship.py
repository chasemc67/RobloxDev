# Blender (Windows PC, background, Workbench): -- workdir (workdir/out/start_ship_b2_visual.fbx, geom.json) -> workdir/prev/*.png, dump.json, plan_meta.json
import bpy,sys,json,os,math,mathutils,bmesh
from mathutils import Vector,Matrix
W=sys.argv[sys.argv.index('--')+1];PV=os.path.join(W,'prev');os.makedirs(PV,exist_ok=True)
G=json.load(open(os.path.join(W,'geom.json')))
def B(x,y,z): return Vector((x,-z,y))
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=os.path.join(W,'out','start_ship_b2_visual.fbx'))
new=[o for o in bpy.data.objects if o not in before];meshes={o.name.split('.')[0]:o for o in new if o.type=='MESH'};empt={o.name:o for o in new if o.type=='EMPTY'}
dump={'objects':{},'empties':{}}
allmn=[1e9]*3;allmx=[-1e9]*3
for n,o in meshes.items():
    co=[o.matrix_world@v.co for v in o.data.vertices];mn=[min(c[i] for c in co) for i in range(3)];mx=[max(c[i] for c in co) for i in range(3)]
    rmn=[mn[0],mn[2],-mx[1]];rmx=[mx[0],mx[2],-mn[1]]
    org=o.matrix_world.translation
    dump['objects'][n]=dict(tris=len(o.data.polygons),roblox_min=[round(v,2) for v in rmn],roblox_max=[round(v,2) for v in rmx],size=[round(rmx[i]-rmn[i],2) for i in range(3)],origin_roblox=[round(org[0],3),round(org[2],3),round(-org[1],3)],materials=[m.name for m in o.data.materials],uv=bool(o.data.uv_layers))
for n,e in empt.items():
    t=e.matrix_world.translation;dump['empties'][n]=[round(t[0],3),round(t[2],3),round(-t[1],3)]
json.dump(dump,open(os.path.join(PV,'dump.json'),'w'),indent=1)
# ---- preview-only scene dressing
def mat(n,c):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*[(v/255) for v in c],1);return m
def rbox(n,center,size,c):
    bpy.ops.mesh.primitive_cube_add(size=1,location=B(*center));o=bpy.context.active_object;o.name=n;o.scale=(size[0],size[2],size[1]);o.data.materials.append(mat(n,c));return o
def cyl(n,center,r,h,c):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=h,vertices=10,location=B(*center));o=bpy.context.active_object;o.name=n;o.data.materials.append(mat(n,c));return o
def sph(n,center,r,c):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r,segments=10,ring_count=6,location=B(*center));o=bpy.context.active_object;o.name=n;o.data.materials.append(mat(n,c));return o
def figure(x,y,z,tag,s=1.0):   # 5-stud Roblox character
    cyl('fl'+tag,(x-0.35*s,y+1.0*s,z),0.3*s,2.0*s,(60,70,110));cyl('fr'+tag,(x+0.35*s,y+1.0*s,z),0.3*s,2.0*s,(60,70,110))
    rbox('ft'+tag,(x,y+2.9*s,z),(1.5*s,1.8*s,0.8*s),(230,70,60));cyl('fa'+tag,(x-1.0*s,y+2.9*s,z),0.22*s,1.7*s,(230,70,60));cyl('fb'+tag,(x+1.0*s,y+2.9*s,z),0.22*s,1.7*s,(230,70,60))
    sph('fh'+tag,(x,y+4.3*s,z),0.7*s,(240,200,160))
SANDC=(226,184,128)
rbox('sand1',(150,-3,50),(700,6,900),SANDC)
rbox('sand2',(-450,-3,325),(500,6,350),SANDC)
water=rbox('water',(-450,-3.6,-25),(500,6,400),(60,150,170))
pm=G['preview'][0];me=bpy.data.meshes.new('mound');me.from_pydata([B(*v) for v in pm['verts']],[],[tuple(t) for t in pm['tris']]);me.validate();me.update();mo=bpy.data.objects.new('mound',me);sc.collection.objects.link(mo);me.materials.append(mat('mound',SANDC))
for p in me.polygons:p.use_smooth=False
# flight 2 is built straight; apply the 30 deg turn (heading toward -X) for the assembled preview only
f2=meshes['RampFlight2'];piv=f2.matrix_world.translation.copy();f2.matrix_world=Matrix.Translation(piv)@Matrix.Rotation(math.radians(-30),4,'Z')@Matrix.Translation(-piv)@f2.matrix_world
tee=G['empties'][1]['pos'];spn=G['empties'][0]['pos']
figure(tee[0]+3.0,tee[1],tee[2]+2.0,'a');figure(-136.0,24.0,6.0,'b')
sc.render.engine='BLENDER_WORKBENCH';s=sc.display.shading;s.light='STUDIO';s.color_type='TEXTURE';s.show_cavity=False;s.show_shadows=True
sc.world=bpy.data.worlds.get('w') or bpy.data.worlds.new('w');sc.world.color=(0.55,0.68,0.80)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.sensor_fit='HORIZONTAL'
def shoot(name,loc,tgt,rx,ry,fov=None,ortho=None,rot=None):
    sc.render.resolution_x,sc.render.resolution_y=rx,ry;cam.data.clip_start=0.3;cam.data.clip_end=9000
    if ortho: cam.data.type='ORTHO';cam.data.ortho_scale=ortho
    else: cam.data.type='PERSP';cam.data.angle_x=math.radians(fov)
    cam.location=loc
    cam.rotation_euler=rot if rot is not None else (tgt-loc).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=os.path.join(PV,name);bpy.ops.render.render(write_still=True);print('RENDER',name)
def cut_copies(names,co,no,which='world'):
    out=[]
    for n,o in list(meshes.items())+[('mound',mo)]:
        if n not in names: continue
        bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world)
        bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],plane_co=co,plane_no=no,clear_outer=True)
        me=bpy.data.meshes.new(n+'_cut');bm.to_mesh(me);bm.free()
        for m in o.data.materials: me.materials.append(m)
        c=bpy.data.objects.new(n+'_cut',me);sc.collection.objects.link(c);out.append((o,c))
    return out
def restore(pairs):
    for o,c in pairs:
        o.hide_render=False;bpy.data.objects.remove(c,do_unlink=True)
# 1. hero 3/4
tgt=B(5,28,55);dirv=B(0.50,0.36,0.80).normalized() if False else Vector((0.55,-0.72,0.62)).normalized()
shoot('hero_3q.png',tgt+dirv*740,tgt,1600,1200,fov=34)
# 2. side section: everything with x < -120 kept (cut through the door centre line), seen from +X; flipped on the box so the sand side is on the right
pairs=cut_copies(list(meshes.keys())+['mound'],Vector((-120,0,0)),Vector((1,0,0)))
for o,c in pairs:o.hide_render=True
for f in [o for o in bpy.data.objects if o.name.startswith(('fl','fr','ft','fa','fb','fh'))]:pass
shoot('side_section_raw.png',B(700,60,95),B(-120,60,95),1600,1200,ortho=330)
restore(pairs)
# 3. plan: roof cut off DeckCabin, Rigging hidden
meshes['Rigging'].hide_render=True
pairs=cut_copies(['DeckCabin'],Vector((0,0,40.6)),Vector((0,0,1)))
for o,c in pairs:o.hide_render=True
cx,cz,sc_w=-20.0,95.0,500.0
shoot('plan_raw.png',Vector((cx,-cz,600)),Vector((cx,-cz,0)),1600,1200,ortho=sc_w,rot=(0,0,0))
json.dump(dict(cx=cx,cz=cz,scale=sc_w,w=1600,h=1200),open(os.path.join(PV,'plan_meta.json'),'w'))
restore(pairs);meshes['Rigging'].hide_render=False
# 4. cabin door view (eye 4.4 studs above the cabin floor)
eye=B(-120,24+4.4,8.0);shoot('door_view.png',eye,B(-120,21.0,140.0),1600,1200,fov=88)
print('ALLDONE')
