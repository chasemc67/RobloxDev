# args: -- outdir id ... ; renders approved (in/appr_id.fbx) and fixed (out/id.fbx) per asset
import bpy,sys,os,math
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];outdir=args[0];W='C:\\Users\\chase\\aa_fix3\\'
COL={'Ice':(0.56,0.89,1,1),'IceCore':(0.75,0.96,1,1),'Snow':(0.96,0.96,1,1),'SnowShadow':(0.79,0.76,0.93,1),'Basalt':(0.25,0.25,0.3,1),'Canvas':(0.48,0.36,0.78,1),
     'Brass':(0.79,0.63,0.29,1),'Glow':(1,0.85,0.4,1),'HullTeal':(0.2,0.6,0.6,1),'Timber':(0.54,0.35,0.24,1)}
for id in args[1:]:
  for tag,path in (('before',W+'in\\appr_'+id+'.fbx'),('after',W+'out\\'+id+'.fbx')):
    bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
    bpy.ops.import_scene.fbx(filepath=path,use_anim=False)
    ms=[o for o in sc.objects if o.type=='MESH']
    for o in ms:
        o.color=COL.get(o.name.split('__')[-1].split('.')[0],(0.8,0.8,0.8,1))
    pts=[o.matrix_world@Vector(c) for o in ms for c in o.bound_box]
    lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)));hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    c=(lo+hi)/2;r=max((hi-lo).length/2,0.5)
    cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
    cam.data.type='ORTHO';cam.data.ortho_scale=r*2.2
    d=Vector((math.cos(math.radians(-60)),math.sin(math.radians(-60)),0.45)).normalized()
    cam.location=c+d*r*4;cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.clip_end=r*20
    sc.render.engine='BLENDER_WORKBENCH';sh=sc.display.shading;sh.color_type='OBJECT';sh.light='STUDIO';sh.show_cavity=True;sh.show_object_outline=True
    sc.render.resolution_x=sc.render.resolution_y=420;sc.render.film_transparent=False
    sc.world=bpy.data.worlds.new('w') if not sc.world else sc.world
    sc.render.filepath=os.path.join(outdir,f'{id}_{tag}.png');bpy.ops.render.render(write_still=True);print('RENDER',id,tag)
