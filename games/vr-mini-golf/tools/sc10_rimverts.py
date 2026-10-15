"""Stage sc10: dump an FBX's mesh vertices (Roblox axes, FBX pivot frame), connected components and triangles.
  Blender -b --factory-startup --python tools/sc10_rimverts.py -- <in.fbx> <out.json>
(the factory scene's default Cube is ignored by its users)
"""
import bpy, sys, json, bmesh
a=sys.argv[sys.argv.index('--')+1:]
bpy.ops.import_scene.fbx(filepath=a[0], axis_forward='-Z', axis_up='Y', global_scale=1.0)
out={}
for o in bpy.data.objects:
    if o.type!='MESH': continue
    me=o.data
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    # connected components
    seen=set(); comps=[]
    for v in bm.verts:
        if v.index in seen: continue
        st=[v]; comp=[]; seen.add(v.index)
        while st:
            x=st.pop(); comp.append(x.index)
            for e in x.link_edges:
                y=e.other_vert(x)
                if y.index not in seen: seen.add(y.index); st.append(y)
        comps.append(comp)
    W=[o.matrix_world @ v.co for v in me.vertices]
    R=[(w.x,w.z,-w.y) for w in W]
    tris=[]
    for f in bm.faces:
        idx=[v.index for v in f.verts]
        for i in range(1,len(idx)-1): tris.append((idx[0],idx[i],idx[i+1]))
    out[o.name]={'verts':R,'comps':comps,'tris':tris}
json.dump(out, open(a[1],'w'))
print('RIMVERTS',{k:len(v['comps']) for k,v in out.items()})
