# Blender: -- W  -> W/start_ship_v2_3.blend   (same geometry/origins/axes as src/build_ship.py; adds collections + per-colour materials)
import bpy,sys,json,os,shutil,bmesh
import numpy as np
from mathutils import Vector
W=sys.argv[sys.argv.index('--')+1]
G=json.load(open(os.path.join(W,'geom.json')));P=json.load(open(os.path.join(W,'pal.json')));PAL,NAMES=P['PAL'],P['NAMES']
def B(v): return Vector((v[0],-v[2],v[1]))
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
tp=os.path.join(W,'start_ship_palette.png');shutil.copy(os.path.join(W,'palette.png'),tp);img=bpy.data.images.load(tp);img.pack()
def s2l(c):
    c=c/255;return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
MAT={}
for n,c in PAL.items():   # one material per palette colour (Wood, WoodDk, ...); texture = shared palette PNG so the FBX look is unchanged
    m=bpy.data.materials.new(n);m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF')
    m.diffuse_color=(s2l(c[0]),s2l(c[1]),s2l(c[2]),1);bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=0.6
    ti=nt.nodes.new('ShaderNodeTexImage');ti.image=img;ti.interpolation='Closest';nt.links.new(ti.outputs['Color'],bs.inputs['Base Color'])
    m['rgb']=list(c);MAT[n]=m
colm=bpy.data.materials.new('Collision');colm.diffuse_color=(0.9,0.3,0.3,0.35)
def coll(n):
    c=bpy.data.collections.new(n);sc.collection.children.link(c);return c
CV,CR,CC=coll('Visual'),coll('Ramps'),coll('Collision')
def cell(u,v): return int(u*8)+8*int((1-v)*8)
for o in G['objects']:
    me=bpy.data.meshes.new(o['name']);me.from_pydata([B(v) for v in o['verts']],[],[tuple(t) for t in o['tris']]);me.validate();me.update()
    uv=me.uv_layers.new(name='UVMap')
    for l in me.loops: uv.data[l.index].uv=o['uvs'][l.vertex_index]
    used=[]
    for p in me.polygons:
        u,v=o['uvs'][me.loops[p.loop_start].vertex_index];n=NAMES[cell(u,v)]
        if n not in used: used.append(n);me.materials.append(MAT[n])
        p.material_index=used.index(n);p.use_smooth=False
    ob=bpy.data.objects.new(o['name'],me);ob.location=B(o['origin'])
    (CR if o['name'].startswith('Ramp') else CV).objects.link(ob);print('BUILD',o['name'],len(me.polygons),used)
for e in G['empties']:
    eo=bpy.data.objects.new(e['name'],None);eo.empty_display_type='SPHERE';eo.empty_display_size=0.8;eo.location=B(e['pos']);CV.objects.link(eo)
for c in G['cols']:
    R=np.array(c['R']);s=np.array(c['size'])/2;ctr=np.array(c['centre']);piv=np.array(c['pivot'])
    local=[R@np.array((sx*s[0],sy*s[1],sz*s[2])) for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)]
    if not piv.any(): loc=ctr;verts=local
    else: loc=piv;verts=[ctr+k for k in local]
    me=bpy.data.meshes.new(c['name']);me.from_pydata([B(v) for v in verts],[],[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]);me.validate();me.update();me.materials.append(colm)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(c['name'],me);ob.location=B(loc);ob.display_type='WIRE';CC.objects.link(ob)
print('COUNTS',len(CV.objects),len(CR.objects),len(CC.objects))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(W,'start_ship_v2_3.blend'),compress=True);print('SAVED')
