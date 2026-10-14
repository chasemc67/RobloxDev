import bpy, sys, json
args=sys.argv[sys.argv.index('--')+1:]
out={}
for f in args[1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=f, axis_forward='-Z', axis_up='Y', global_scale=1.0)
    stem=f.split('/')[-1][:-4]
    for o in bpy.data.objects:
        if o.type!='MESH': continue
        me=o.data; me.calc_loop_triangles()
        M=o.matrix_world
        V=[M @ v.co for v in me.vertices]
        R=[(v.x,v.z,-v.y) for v in V]
        # material split names like the importer: stem__Material
        mats=[m.name if m else 'None' for m in me.materials]
        for t in me.loop_triangles:
            mn=mats[t.material_index] if mats else o.name
            key=stem+'__'+mn.split('.')[0]
            out.setdefault(key,[]).append([R[i] for i in t.vertices])
json.dump(out,open(args[0],'w'))
