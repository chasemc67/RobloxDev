# Blender (Windows PC, background): -- workdir  (workdir/geom.json, workdir/palette.png) -> workdir/out/*.fbx
# Roblox frame (+Y up, front +Z, studs). Blender mapping B(v)=(x,-z,y). FBX axes -Z forward / Y up, scale 1 (same as the kit pipeline).
import bpy,sys,json,os,shutil,math
from mathutils import Vector
W=sys.argv[sys.argv.index('--')+1];OUT=os.path.join(W,'out');os.makedirs(OUT,exist_ok=True)
G=json.load(open(os.path.join(W,'geom.json')))
def B(v): return Vector((v[0],-v[2],v[1]))
bpy.ops.wm.read_factory_settings(use_empty=True)
tp=os.path.join(OUT,'start_ship_palette.png');shutil.copy(os.path.join(W,'palette.png'),tp);img=bpy.data.images.load(tp)
m=bpy.data.materials.new('start_ship_pal');m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=0.6
ti=nt.nodes.new('ShaderNodeTexImage');ti.image=img;ti.interpolation='Closest';nt.links.new(ti.outputs['Color'],bs.inputs['Base Color'])
colm=bpy.data.materials.new('col_mat');colm.diffuse_color=(0.9,0.3,0.3,1)
vis=[];
for o in G['objects']:
    me=bpy.data.meshes.new(o['name']);me.from_pydata([B(v) for v in o['verts']],[],[tuple(t) for t in o['tris']]);me.validate();me.update()
    uv=me.uv_layers.new(name='UVMap')
    for l in me.loops: uv.data[l.index].uv=o['uvs'][l.vertex_index]
    me.materials.append(m)
    for p in me.polygons: p.use_smooth=False
    ob=bpy.data.objects.new(o['name'],me);ob.location=B(o['origin']);bpy.context.scene.collection.objects.link(ob);vis.append(ob)
    print('BUILD',o['name'],len(me.polygons))
emp=[]
for e in G['empties']:
    eo=bpy.data.objects.new(e['name'],None);eo.empty_display_type='SPHERE';eo.empty_display_size=0.8;eo.location=B(e['pos']);bpy.context.scene.collection.objects.link(eo);emp.append(eo);print('EMPTY',e['name'],e['pos'])
import numpy as np
cob=[]
for c in G['cols']:
    R=np.array(c['R']);s=np.array(c['size'])/2;ctr=np.array(c['centre']);piv=np.array(c['pivot'])
    corners=[(sx*s[0],sy*s[1],sz*s[2]) for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)]
    local=[R@np.array(k) for k in corners]
    if not piv.any(): loc=ctr;verts=local
    else: loc=piv;verts=[ctr+k for k in local]
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    me=bpy.data.meshes.new(c['name']);me.from_pydata([B(v) for v in verts],[],faces);me.validate();me.update();me.materials.append(colm)
    # make winding outward
    me.polygons.foreach_set('use_smooth',[False]*len(me.polygons));bpy.context.view_layer.update()
    ob=bpy.data.objects.new(c['name'],me);ob.location=B(loc);bpy.context.scene.collection.objects.link(ob);cob.append(ob)
    import bmesh
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
print('COL objects',len(cob))
def export(path,objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.export_scene.fbx(filepath=path,use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',path_mode='COPY',embed_textures=True,mesh_smooth_type='FACE',add_leaf_bones=False)
    print('EXPORTED',path)
export(os.path.join(OUT,'start_ship_b2_visual.fbx'),vis+emp)
export(os.path.join(OUT,'start_ship_b2_col.fbx'),cob)
for ob in vis:
    if ob.name.startswith('Ramp'):
        loc=ob.location.copy();ob.location=(0,0,0);export(os.path.join(OUT,ob.name+'_own_origin.fbx'),[ob]);ob.location=loc
