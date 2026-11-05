# Blender: -- dag_geom.json outdir palette.png   -> outdir/<id>/<id>.fbx + <id>.png (palette texture)
import bpy,sys,json,os,shutil
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:];g=json.load(open(a[0]));outdir=a[1];tex=a[2]
def B(v): return Vector((v[0],-v[2],v[1]))
for id,spec in g.items():
    bpy.ops.wm.read_factory_settings(use_empty=True);d=os.path.join(outdir,id);os.makedirs(d,exist_ok=True)
    tp=os.path.join(d,id+'.png');shutil.copy(tex,tp);img=bpy.data.images.load(tp)
    m=bpy.data.materials.new(id+'_mat');m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF')
    ti=nt.nodes.new('ShaderNodeTexImage');ti.image=img;ti.interpolation='Closest';nt.links.new(ti.outputs['Color'],bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value=0.45
    for o in spec['objects']:
        me=bpy.data.meshes.new(o['name']);me.from_pydata([B(v) for v in o['verts']],[],[tuple(t) for t in o['tris']]);me.validate();me.update()
        uv=me.uv_layers.new(name='UVMap')
        for l in me.loops: uv.data[l.index].uv=o['uvs'][l.vertex_index]
        me.materials.append(m)
        for p in me.polygons: p.use_smooth=True
        ob=bpy.data.objects.new(o['name'],me);bpy.context.scene.collection.objects.link(ob)
        print('BUILD',id,o['name'],len(me.polygons))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=os.path.join(d,id+'.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',path_mode='COPY',embed_textures=True,mesh_smooth_type='FACE',add_leaf_bones=False)
    print('EXPORTED',id)
