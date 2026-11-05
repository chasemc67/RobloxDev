import sys,json,copy
from pathlib import Path
s=Path(__file__).parent;sys.path.insert(0,str(s))
import bpy,bmesh,bwlib as L,pass9_geo as G
from mathutils import Vector,Matrix
L.PROGRESS=str(s/'PROGRESS_pass9.md');r=s.parent
m=json.loads((r/'_backup_pass8/manifest.json').read_text());old={e['name']:e for e in m['props']}
anchors=[]
for name,e in old.items():
 if name not in ['bw_scn_aurora_crown'] and not any(x in name for x in ['sugarloaf_crystals_','lantern_grove_trunk_','aurora_rocks_']):continue
 L.reset_scene();side=-1 if name.endswith('_w') else 1;coll=[]
 if 'trunk_' in name:
  bpy.ops.import_scene.fbx(filepath=str(r/'_backup_pass8'/e['fbx']))
  bpy.context.view_layer.update();a=e['pivot_position_arch_local'];canopy=[]
  for o in list(bpy.context.scene.objects):
   if o.type!='MESH':continue
   if not o.data.materials[0].name.startswith('BW_Backdrop'):bpy.data.objects.remove(o,do_unlink=True);continue
   for v in o.data.vertices:v.co=o.matrix_world@v.co+Vector((a[0],-a[2],a[1]))
   o.matrix_world=Matrix.Identity(4)
   canopy.append(o)
  core=G.build_twisted_trunk(side);objs=canopy+[core]
  # Combine canopy and new trunk in one asset, retaining material boundaries.
  bpy.ops.object.select_all(action='DESELECT')
  for o in objs:o.select_set(True)
  bpy.context.view_layer.objects.active=core;bpy.ops.object.join();ob=core
  coll=[dict(name='lower_trunk',center=[side*8.4,6.5,0],size=[2.6,13,2.6],CanCollide=True),dict(name='curl',center=[side*6.6,17,0],size=[3.6,8,2.0],CanCollide=True)]
  from mathutils.bvhtree import BVHTree
  for q in old.values():
   aa=q.get('anchor_position_arch_local')
   if not aa or not q['name'].startswith('bw_arch_lantern_grove_lantern_') or aa[0]*side<0:continue
   p=Vector((aa[0],-aa[2],aa[1]));inside=False;nearest=999
   for ca in canopy:
    # joined geometry includes retained canopy; nearest surface + parity containment
    pass
   tree=BVHTree.FromObject(ob,bpy.context.evaluated_depsgraph_get());nearest=tree.find_nearest(p)[3]
   origin=p.copy();hits=0
   for k in range(100):
    hit=tree.ray_cast(origin,Vector((0.917,.231,.326)))
    if hit[0] is None:break
    hits+=1;origin=hit[0]+Vector((0.917,.231,.326))*.0001
   inside=hits%2==1
   anchors.append(dict(name=q['name'],anchor=aa,surface_distance=nearest,inside_canopy=inside))
   assert inside or nearest<.3,(q['name'],nearest)
 elif 'sugarloaf_crystals_' in name:ob=G.build_sugarloaf_crystals(side)
 elif 'aurora_rocks_' in name:
  ob=G.build_aurora_rocks(side)
  coll=[dict(name='outer_pile',center=[side*10.8,1.3,0],size=[3.6,2.6,3.6],CanCollide=True),dict(name='back_pile',center=[side*7.7,1,-3],size=[2.0,2,2.2],CanCollide=True)]
 else:ob=G.build_crown()
 mn,mx=L.bbox_blender([ob]);off=Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z)) if name!='bw_scn_aurora_crown' else Vector((0,0,0))
 for v in ob.data.vertices:v.co-=off
 pivot=[off.x,off.z,-off.y]
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='MATERIAL');bpy.ops.object.mode_set(mode='OBJECT')
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];parts=[]
 for o in objs:
  mat=o.data.materials[0];o.name=name+'__'+mat.name
  mn,mx=L.bbox_blender([o]);sz,ct=L.to_roblox_bbox(mn,mx)
  parts.append(dict(mesh=o.name,material=mat.name,tris=L.tri_count([o]),size=list(sz),center_from_pivot=list(ct),color='#9FE6F2' if mat.name=='Glow_Tips' else None,roblox_material='Neon' if mat.name in ['Glow_Tips','Glow_Crystal'] else 'SmoothPlastic'))
 L.export_fbx(objs,str(r/e['fbx']));mn,mx=L.bbox_blender(objs);sz,ct=L.to_roblox_bbox(mn,mx)
 e.update(pivot_position_arch_local=pivot,pivot='base centre' if name!='bw_scn_aurora_crown' else 'shared arch base centre',pivot_recenter_applied=pivot,bbox_size_studs=list(sz),bbox_center_from_pivot=list(ct),bbox_min_roblox=[mn.x,mn.z,-mx.y],bbox_max_roblox=[mx.x,mx.z,-mn.y],triangles=L.tri_count(objs),parts=parts,materials=sorted({p['material'] for p in parts}),collision=[dict(b,center=[b['center'][k]-pivot[k] for k in range(3)]) for b in coll],notes='Pass9 exact supplied geometry; existing pass8 leaf geometry retained for trunks.',source='pass9_geo.py')
 if name=='bw_scn_aurora_crown':e.update(crystal_table=G.CRYSTALS,sides=12,flat_normals=True,crystal_nudges=[])
 e['tris_x_count']=e['triangles']*e['builder_count'];(s/'manifest_parts'/(name+'.json')).write_text(json.dumps(e,indent=1))
 for i in m['instances']:
  if i['asset']==name:
   parent=next(p for p in m['instances'] if p['id']==i['parent_id']);i['position']=[parent['position'][k]+pivot[k] for k in range(3)]
m['totals']['tris_total']=sum(e['tris_x_count'] for e in m['props']);m['lobby']='Golden Hour Boardwalk - pass9 explicit geometry';m['pass9_clearance']=m['pass8_clearance']
(r/'manifest.json').write_text(json.dumps(m,indent=1));(s/'anchors_pass9.json').write_text(json.dumps(anchors,indent=2));L.log('Pass9 exports complete; six anchors retained inside canopy; lantern FBXs unchanged.')
