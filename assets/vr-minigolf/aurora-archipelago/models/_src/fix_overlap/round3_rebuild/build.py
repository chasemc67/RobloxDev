# Blender: args: -- geom.json outdir ; geom[id]={src, objects:{objname:{verts,tris}}}
import bpy,sys,json,os
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:]
g=json.load(open(args[0]));outdir=args[1]
def B(v): return Vector((v[0],-v[2],v[1]))
for id,spec in g.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=spec['src'],use_anim=False)
    for o in [o for o in bpy.context.scene.objects if o.type=='MESH']:
        if o.name not in spec['objects']: bpy.data.objects.remove(o); continue
        d=spec['objects'][o.name];inv=o.matrix_world.inverted()
        mats=list(o.data.materials)
        me=bpy.data.meshes.new(o.data.name+'_fix')
        me.from_pydata([inv@B(v) for v in d['verts']],[],[tuple(t) for t in d['tris']]);me.validate();me.update()
        for m in mats: me.materials.append(m)
        old=o.data;o.data=me;nm=old.name;bpy.data.meshes.remove(old);me.name=nm
        for p in me.polygons: p.use_smooth=False
        print('BUILD',id,o.name,len(me.vertices),len(me.polygons))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=os.path.join(outdir,id+'.fbx'),use_selection=True,object_types={'EMPTY','MESH'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',path_mode='COPY',embed_textures=True,mesh_smooth_type='FACE',add_leaf_bones=False)
    print('EXPORTED',id)
