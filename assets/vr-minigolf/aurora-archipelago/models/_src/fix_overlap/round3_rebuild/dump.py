# Blender: import each FBX, dump mesh data in Roblox prop-local coords (Y up). args: -- out.json id=path ...
import bpy,sys,json
args=sys.argv[sys.argv.index('--')+1:]
out=args[0];res={}
def R(v): return [v.x,v.z,-v.y]
for a in args[1:]:
    id,path=a.split('=',1)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path,use_anim=False)
    objs=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH': continue
        m=o.data;m.calc_loop_triangles()
        objs.append(dict(name=o.name,mesh=m.name,mats=[s.material.name if s.material else None for s in o.material_slots],
          verts=[R(o.matrix_world@v.co) for v in m.vertices],tris=[list(t.vertices) for t in m.loop_triangles]))
    roots=[dict(name=o.name,t=R(o.matrix_world.translation)) for o in bpy.context.scene.objects if o.type=='EMPTY' and o.parent is None]
    res[id]=dict(path=path,objects=objs,roots=roots)
    print('DUMP',id,[(o['name'],len(o['verts']),len(o['tris'])) for o in objs])
json.dump(res,open(out,'w'))
