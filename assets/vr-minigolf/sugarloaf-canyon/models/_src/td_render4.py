import bpy,json,sys,math
a=sys.argv[sys.argv.index('--')+1:];G=json.load(open(a[0]));OUT=a[1]
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
def mk(name,d,col):
    if not d: return None
    me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y) for x,y,z in d['verts']],[],d['tris']);me.update()
    o=bpy.data.objects.new(name,me);sc.collection.objects.link(o);o.color=col;return o
K=mk('kept',G['kept'],(0.62,0.6,0.58,1));Dd=mk('drop',G['drop'],(0.95,0.6,0.15,1));F=mk('fill',G['fill'],(0.62,0.6,0.58,1));F.hide_render=True
sc.render.engine='BLENDER_WORKBENCH';sh=sc.display.shading;sh.light='STUDIO';sh.color_type='OBJECT';sh.show_cavity=True;sh.show_object_outline=True
sc.world=bpy.data.worlds.new('w');sc.world.color=(0.12,0.12,0.14)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=5000
sc.render.resolution_x=sc.render.resolution_y=360
for k,(x,y,z) in enumerate(G['drop_pts']):
    cam.location=(x,-z,y+400);cam.rotation_euler=(0,0,0);cam.data.ortho_scale=40
    for tag,vis in (('edgefix3',(1,0,0)),('edgefix4',(1,1,0))):
        K.hide_render=not vis[0];Dd.hide_render=not vis[1];F.hide_render=not vis[2]
        sc.render.filepath=f'{OUT}/site{k:02d}_{tag}.png';bpy.ops.render.render(write_still=True)
print('TD done',len(G['drop_pts']))
