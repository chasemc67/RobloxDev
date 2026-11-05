# Blender -b source.blend --python inspect_source.py -- out_json
import bpy,sys,json
from mathutils import Vector
out=sys.argv[sys.argv.index('--')+1]
R={'collections':{},'objects':{},'materials':{},'images':[]}
for c in bpy.data.collections: R['collections'][c.name]=[o.name for o in c.objects]
for o in bpy.data.objects:
    e=dict(type=o.type,loc=list(o.location),rot=list(o.rotation_euler),scale=list(o.scale),parent=o.parent.name if o.parent else None,coll=[c.name for c in o.users_collection])
    if o.type=='MESH':
        me=o.data;mw=o.matrix_world;co=[mw@v.co for v in me.vertices]
        e.update(tris=sum(len(p.vertices)-2 for p in me.polygons),verts=len(me.vertices),mats=[m.name if m else None for m in me.materials],
          bbmin=[min(c[i] for c in co) for i in range(3)],bbmax=[max(c[i] for c in co) for i in range(3)],uv=[u.name for u in me.uv_layers],mesh=me.name)
        if o.name in('Hull','DeckCabin','Rigging','Dressing','Dressing_Glow','Pier','RockBumper') or o.name.startswith('Ramp'):
            cnt={}
            for p in me.polygons:
                n=me.materials[p.material_index].name;cnt[n]=cnt.get(n,0)+1
            e['mat_tris']=cnt
    R['objects'][o.name]=e
for m in bpy.data.materials:
    nodes=[n.type for n in m.node_tree.nodes] if m.use_nodes and m.node_tree else []
    R['materials'][m.name]=dict(diffuse=list(m.diffuse_color),rgb=list(m.get('rgb',[])),nodes=nodes,users=m.users)
for i in bpy.data.images: R['images'].append(dict(name=i.name,packed=bool(i.packed_file),size=list(i.size),fp=i.filepath))
R['scene']=dict(name=bpy.context.scene.name,unit=bpy.context.scene.unit_settings.scale_length,engine=bpy.context.scene.render.engine)
json.dump(R,open(out,'w'),indent=1);print('INSPECT_OK')
