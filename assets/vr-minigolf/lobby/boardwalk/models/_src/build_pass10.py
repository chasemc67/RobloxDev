import sys,json,copy
from pathlib import Path
s=Path(__file__).parent;sys.path.insert(0,str(s))
import bpy,bmesh,bwlib as L,pass10_geo as G
from mathutils import Vector,Matrix
L.PROGRESS=str(s/'PROGRESS_pass10.md');r=s.parent
m=json.loads((r/'_backup_pass9/manifest.json').read_text());old={e['name']:e for e in m['props']}
anchors=json.loads((s/'anchors_pass9.json').read_text())
for name,e in old.items():
 if not any(x in name for x in ['sugarloaf_crystals_','aurora_rocks_']):continue
 L.reset_scene();side=-1 if name.endswith('_w') else 1;coll=[]
 if 'sugarloaf_crystals_' in name:ob=G.build_sugarloaf_crystals(side)
 else:
  ob=G.build_aurora_rocks(side)
  # Two bounding approximations follow the taller mound, keeping the west-front snowpuff clear.
  pts=[Vector((v.co.x,v.co.z,-v.co.y)) for v in ob.data.vertices]
  for label,subset in [('front_outer',[v for v in pts if v.z>=.3]),('rear_mound',[v for v in pts if v.z<.3])]:
   lo=[min(v[k] for v in subset) for k in range(3)];hi=[max(v[k] for v in subset) for k in range(3)]
   if label=='front_outer':
    lo[2]=.3
    if side<0:hi[0]=min(hi[0],-7.61)
    else:lo[0]=max(lo[0],7.61)
   else:hi[2]=.29
   coll.append(dict(name=label,center=[(lo[k]+hi[k])/2 for k in range(3)],size=[hi[k]-lo[k] for k in range(3)],CanCollide=True))
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
 e.update(pivot_position_arch_local=pivot,pivot='base centre' if name!='bw_scn_aurora_crown' else 'shared arch base centre',pivot_recenter_applied=pivot,bbox_size_studs=list(sz),bbox_center_from_pivot=list(ct),bbox_min_roblox=[mn.x,mn.z,-mx.y],bbox_max_roblox=[mx.x,mx.z,-mn.y],triangles=L.tri_count(objs),parts=parts,materials=sorted({p['material'] for p in parts}),collision=[dict(b,center=[b['center'][k]-pivot[k] for k in range(3)]) for b in coll],notes='Pass10 exact supplied geometry; tighter candy bases / taller snowy mounds.',source='pass10_geo.py')
 if name=='bw_scn_aurora_crown':e.update(crystal_table=G.CRYSTALS,sides=12,flat_normals=True,crystal_nudges=[])
 e['tris_x_count']=e['triangles']*e['builder_count'];(s/'manifest_parts'/(name+'.json')).write_text(json.dumps(e,indent=1))
 for i in m['instances']:
  if i['asset']==name:
   parent=next(p for p in m['instances'] if p['id']==i['parent_id']);i['position']=[parent['position'][k]+pivot[k] for k in range(3)]
m['totals']['tris_total']=sum(e['tris_x_count'] for e in m['props']);m['lobby']='Golden Hour Boardwalk - pass10 explicit geometry';m['pass10_clearance']=m['pass9_clearance']
(r/'manifest.json').write_text(json.dumps(m,indent=1));(s/'anchors_pass10.json').write_text(json.dumps(anchors,indent=2));L.log('Pass10 four exports complete; all other FBXs unchanged.')


