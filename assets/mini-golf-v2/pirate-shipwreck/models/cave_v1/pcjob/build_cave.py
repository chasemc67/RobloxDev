# Blender (Windows PC): -- geom_dir outdir palette.png  -> outdir/<part>.fbx (+ <part>.png palette texture embedded)
# geom_dir/<part>.json = {part:{objects:[{name,verts,tris,uvs,smooth}]}} in Roblox frame (+Y up, front -Z, studs). Blender mapping B(v)=(x,-z,y).
import bpy,sys,json,os,shutil,glob
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:];gd,outdir,tex=a[0],a[1],a[2]
os.makedirs(outdir,exist_ok=True)
def B(v): return Vector((v[0],-v[2],v[1]))
for jf in sorted(glob.glob(os.path.join(gd,'cave_*.json'))):
    g=json.load(open(jf))
    for id,spec in g.items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        tp=os.path.join(outdir,id+'.png');shutil.copy(tex,tp);img=bpy.data.images.load(tp)
        m=bpy.data.materials.new(id+'_mat');m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF')
        ti=nt.nodes.new('ShaderNodeTexImage');ti.image=img;ti.interpolation='Closest';nt.links.new(ti.outputs['Color'],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value=0.5
        for o in spec['objects']:
            me=bpy.data.meshes.new(o['name']);me.from_pydata([B(v) for v in o['verts']],[],[tuple(t) for t in o['tris']]);me.validate();me.update()
            uv=me.uv_layers.new(name='UVMap')
            for l in me.loops: uv.data[l.index].uv=o['uvs'][l.vertex_index]
            me.materials.append(m)
            for p,sm in zip(me.polygons,o['smooth']): p.use_smooth=bool(sm)
            ob=bpy.data.objects.new(o['name'],me);bpy.context.scene.collection.objects.link(ob)
            print('BUILD',id,o['name'],len(me.polygons))
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.fbx(filepath=os.path.join(outdir,id+'.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',path_mode='COPY',embed_textures=True,mesh_smooth_type='FACE',add_leaf_bones=False)
        print('EXPORTED',id)
