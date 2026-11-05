# Blender (Windows PC): -- geom_dir outdir palette.png -> outdir/<id>.fbx (+<id>.png palette). Roblox frame (+Y up, front +Z). Blender mapping B(v)=(x,-z,y).
# Each json: objects (main mesh + optional <id>_Glow mesh with its own material) and empties (LightAttach).
import bpy,sys,json,os,shutil,glob
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:];gd,outdir,tex=a[0],a[1],a[2]
os.makedirs(outdir,exist_ok=True)
def B(v): return Vector((v[0],-v[2],v[1]))
for jf in sorted(glob.glob(os.path.join(gd,"kit_*.json"))):
    g=json.load(open(jf))
    for id,spec in g.items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        tp=os.path.join(outdir,id+'.png');shutil.copy(tex,tp);img=bpy.data.images.load(tp)
        def mk(name,kind='main'):
            m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF')
            bs.inputs['Roughness'].default_value=0.5
            if kind in('flame','core'):   # plain colour, NO texture node (Studio sets Neon colour, TextureID cleared); UVs are still exported
                c=(1.0,140/255,50/255,1.0) if kind=='flame' else (1.0,220/255,150/255,1.0)
                bs.inputs['Base Color'].default_value=c;m.diffuse_color=c
                try: bs.inputs['Emission Color'].default_value=c;bs.inputs['Emission Strength'].default_value=1.0
                except Exception as ex: print('emission skipped',ex)
                return m
            ti=nt.nodes.new('ShaderNodeTexImage');ti.image=img;ti.interpolation='Closest';nt.links.new(ti.outputs['Color'],bs.inputs['Base Color'])
            if kind=='glow':
                try: bs.inputs['Emission Color'].default_value=(1.0,0.745,0.43,1.0);bs.inputs['Emission Strength'].default_value=1.0
                except Exception as ex: print('emission skipped',ex)
            return m
        mats={'main':mk(id+'_mat'),'glow':mk(id+'_glow_mat','glow'),'flame':mk(id+'_flame_mat','flame'),'core':mk(id+'_core_mat','core')}
        for o in spec['objects']:
            me=bpy.data.meshes.new(o['name']);me.from_pydata([B(v) for v in o['verts']],[],[tuple(t) for t in o['tris']]);me.validate();me.update()
            uv=me.uv_layers.new(name='UVMap')
            for l in me.loops: uv.data[l.index].uv=o['uvs'][l.vertex_index]
            me.materials.append(mats[o.get('mat','main')])
            for p,sm in zip(me.polygons,o['smooth']): p.use_smooth=bool(sm)
            ob=bpy.data.objects.new(o['name'],me);bpy.context.scene.collection.objects.link(ob)
            print('BUILD',id,o['name'],len(me.polygons))
        for e in spec.get('empties',[]):
            eo=bpy.data.objects.new(e['name'],None);eo.empty_display_type='SPHERE';eo.empty_display_size=0.4;eo.location=B(e['pos']);bpy.context.scene.collection.objects.link(eo)
            print('EMPTY',id,e['name'],e['pos'])
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.fbx(filepath=os.path.join(outdir,id+'.fbx'),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',path_mode='COPY',embed_textures=True,mesh_smooth_type='FACE',add_leaf_bones=False)
        print('EXPORTED',id)
