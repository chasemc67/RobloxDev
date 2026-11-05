# Blender: -- outdir fbx...  Workbench texture previews (3/4 and top-down) + dump of re-imported stats
import bpy,sys,mathutils,os,json
a=sys.argv[sys.argv.index('--')+1:];outdir=a[0];rep={}
for f in a[1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;bpy.ops.import_scene.fbx(filepath=f)
    M=[o for o in sc.objects if o.type=='MESH'];co=[o.matrix_world@v.co for o in M for v in o.data.vertices]
    lo=mathutils.Vector([min(c[i] for c in co) for i in range(3)]);hi=mathutils.Vector([max(c[i] for c in co) for i in range(3)])
    nm=os.path.basename(f)[:-4]
    rep[nm]=dict(objects=[o.name for o in M],tris=sum(len(o.data.loop_triangles) or (o.data.calc_loop_triangles() or len(o.data.loop_triangles)) for o in M),
      bmin_blender=list(map(lambda x:round(x,3),lo)),bmax_blender=list(map(lambda x:round(x,3),hi)),uv=all(o.data.uv_layers for o in M),
      images=[i.name for i in bpy.data.images])
    bpy.ops.mesh.primitive_plane_add(size=14,location=(0,0,-0.002));g=bpy.context.active_object;gm=bpy.data.materials.new('g');gm.diffuse_color=(0.45,0.72,0.35,1);g.data.materials.append(gm)
    sc.render.engine='BLENDER_WORKBENCH';s=sc.display.shading;s.light='STUDIO';s.color_type='TEXTURE';s.show_cavity=True;s.show_shadows=True
    sc.world=bpy.data.worlds.new('w');sc.world.color=(0.85,0.9,1.0)
    cam=bpy.data.objects.new('c',bpy.data.cameras.new('c'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO'
    h=hi.z;ext=max(hi.x-lo.x,hi.y-lo.y,h)
    for tag,loc in(('persp',(ext*1.4,ext*2.2,h*0.5+ext*1.6)),('top',(0.0001,0,h+10))):
        sc.render.resolution_x=sc.render.resolution_y=640;cam.data.ortho_scale=ext*1.35
        tg=mathutils.Vector((0,0,h*0.45));cam.location=loc;cam.rotation_euler=(tg-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler()
        sc.render.filepath=os.path.join(outdir,f'{nm}_{tag}.png');bpy.ops.render.render(write_still=True)
json.dump(rep,open(os.path.join(outdir,'dump.json'),'w'),indent=1);print('DONE_RENDER')
