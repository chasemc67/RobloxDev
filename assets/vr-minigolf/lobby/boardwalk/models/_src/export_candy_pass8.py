import bpy
from mathutils import Vector
from rock_candy import make_cluster
for side,suffix in ((-1,'w'),(1,'e')):
 L.reset_scene();objs=[]
 for j,(x,y,z,n,size) in enumerate(((9.5,-.8,15.0,8,2.0),(10.1,-.5,.65,6,1.0),(8.8,1,.65,5,1.0))):
  o=make_cluster('cluster_'+str(j),n,size,810+j)
  for v in o.data.vertices:v.co.x=side*(v.co.x+x);v.co.y+=y;v.co.z+=z
  objs.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();ob=objs[0]
 mn,mx=L.bbox_blender([ob]);off=Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z))
 for v in ob.data.vertices:v.co-=off
 name='bw_scn_sugarloaf_crystals_'+suffix;ob.name=name+'__Glow_Crystal'
 L.export_fbx([ob],str(SRC.parent/'fbx'/ (name+'.fbx')))
 mn,mx=L.bbox_blender([ob]);sz,ct=L.to_roblox_bbox(mn,mx)
 e=dict(name=name,group='scenery',fbx='fbx/'+name+'.fbx',front='south (+Z)',notes='Supplied rock_candy make_cluster: 8 crystals size2 at joint, two base clusters n6/n5 size1; mirrored.',pivot='base centre',pivot_position_arch_local=[off.x,off.z,-off.y],bbox_size_studs=build_all.r3(sz),bbox_center_from_pivot=build_all.r3(ct),bbox_min_roblox=build_all.r3([mn.x,mn.z,-mx.y]),bbox_max_roblox=build_all.r3([mx.x,mx.z,-mn.y]),target_size_studs=[0,0,0],triangles=L.tri_count([ob]),tris_max=19999,materials=['Glow_Crystal'],parts=[dict(mesh=ob.name,material='Glow_Crystal',roblox_material='Neon',vertex_colour_attribute='Col',tris=L.tri_count([ob]),size=build_all.r3(sz),center_from_pivot=build_all.r3(ct))],collision=[],motion=None,scalable=None,can_collide=False,foliage_can_collide=False,crystals_can_collide=False,course='sugarloaf_canyon',decoration_only=True,cluster_recipe=[{'n':8,'size':2.0},{'n':6,'size':1.0},{'n':5,'size':1.0}])
 (SRC/'manifest_parts'/(name+'.json')).write_text(json.dumps(e,indent=1))
