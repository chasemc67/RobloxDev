"""Additive H15 export and CPU previews; never export other batch assets."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
S=Path(__file__).resolve().parent;D=S.parents[2];PV=D/'models/previews/props_batch2'
p=json.loads((S/'h15_part.json').read_text());PAL=json.loads((S/'palette.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(S/'props_batch2.blend'));sc=bpy.context.scene
code=(S/'build_batch2.py').read_text();exec(code[code.index('def B(p):'):code.index('ROOTS={}')])
root=bpy.data.objects.new(p['id'],None);sc.collection.objects.link(root);objs=[];ms=[]
for k,g in p['groups'].items():
 o=mesh(p['id']+'__'+k,g,k);o.parent=root;objs.append(o);o.data.calc_loop_triangles()
 ms.append(dict(mesh=o.name,material=k,colour=PAL[k][0],color=PAL[k][0],roblox_material=PAL[k][1],transparency=PAL[k][3],tris=len(o.data.loop_triangles)))
assert all(m['tris']<20000 for m in ms)
for o in sc.objects:o.select_set(False)
root.select_set(True)
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=root
fbx=D/'models/fbx/props_batch2'/ (p['id']+'.fbx')
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'EMPTY','MESH'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',path_mode='COPY',embed_textures=True,mesh_smooth_type='FACE',add_leaf_bones=False)
# Reimport into same scene, verify only newly imported objects, use their actual
# triangulation for final fitcheck. Original meshes stay available for previews.
before=set(sc.objects);bpy.ops.import_scene.fbx(filepath=str(fbx),use_anim=False)
imported=list(set(sc.objects)-before);roots=[o for o in imported if o.type=='EMPTY'];meshes=[o for o in imported if o.type=='MESH']
assert len(roots)==1 and roots[0].location.length<1e-5 and len(meshes)==len(ms)
ts=[];err=0
for m in ms:
 o=next(o for o in meshes if o.name.startswith(m['mesh']));assert o.parent==roots[0] and len(o.data.materials)==1
 o.data.calc_loop_triangles();assert len(o.data.loop_triangles)==m['tris']
 vv=[o.matrix_world@v.co for v in o.data.vertices];rb=[[v.x,v.z,-v.y] for v in vv];sv=p['groups'][m['material']]['verts']
 for axis in range(3):
  err=max(err,abs(min(v[axis] for v in rb)-min(v[axis] for v in sv)),abs(max(v[axis] for v in rb)-max(v[axis] for v in sv)))
 for t in o.data.loop_triangles:ts.append([rb[i] for i in t.vertices])
assert err<1e-4
(S/'h15_triangles.json').write_text(json.dumps(ts))
(S/'h15_fbx_validation.json').write_text(json.dumps(dict(all_pass=True,mesh_count=len(meshes),tris=len(ts),coordinate_error=err,base_pivot_zero=True,one_mesh_per_material=True),indent=2))
for o in imported:bpy.data.objects.remove(o,do_unlink=True)
vs=[v for g in p['groups'].values() for v in g['verts']];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
world=p['anchor'];h=json.loads((D/'holes.json').read_text())['holes'][14];a=[world[i]-h['world_offset'][i] for i in range(3)]
r=dict(id=p['id'],hole=15,fbx='fbx/props_batch2/'+p['id']+'.fbx',tris=sum(m['tris'] for m in ms),max_mesh_tris=max(m['tris'] for m in ms),meshes=ms,pivot_hole_local=a,anchor_local=a,yaw_local=0,world_offset=h['world_offset'],world_yaw=0,pivot_world=world,placement_yaw=0,motion=None,notes=p['notes'],can_collide=False,can_query=False,can_touch=False,streaming='Persistent',primary_part='base-centre root (builder creates PrimaryPart)',bbox_asset_local=[lo,hi],bbox_hole_local=[[lo[i]+a[i] for i in range(3)],[hi[i]+a[i] for i in range(3)]],bbox_world=[[lo[i]+world[i] for i in range(3)],[hi[i]+world[i] for i in range(3)]],dimensions=[hi[i]-lo[i] for i in range(3)],lights=[],placement_source='world/world.json waterfalls: Great Frozen Falls',source_top=[20,182,-398],source_bottom=world)
(S/'h15_build_report.json').write_text(json.dumps(r,indent=2))
cam=sc.camera;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=12;sc.cycles.use_denoising=True
sc.render.resolution_x=1280;sc.render.resolution_y=960;sc.render.resolution_percentage=100
exec(code[code.index('def render(path,objs):'):code.index('allmesh=[o for o in sc.objects')])
# Centre the projected bounds (the long cascade and small lane are asymmetric).
old_render=render
def render(path,objs):
 bpy.context.view_layer.update();pts=[o.matrix_world@Vector(v) for o in objs for v in o.bound_box]
 center=(Vector([min(v[i] for v in pts) for i in range(3)])+Vector([max(v[i] for v in pts) for i in range(3)]))/2
 cam.location=center+Vector((.8,-1.3,1.2)).normalized()*300;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
 cs=[cam.matrix_world.inverted()@v for v in pts];xmin,xmax=min(v.x for v in cs),max(v.x for v in cs);ymin,ymax=min(v.y for v in cs),max(v.y for v in cs)
 cam.location+=cam.rotation_euler.to_matrix()@Vector(((xmin+xmax)/2,(ymin+ymax)/2,0))
 cam.data.ortho_scale=max(xmax-xmin,(ymax-ymin)*1280/960)*1.16
 sc.render.filepath=str(path);bpy.ops.render.render(write_still=True);print('RENDERED',path.name,flush=True)
allmesh=[o for o in sc.objects if o.type=='MESH']
for o in allmesh:o.hide_render=o not in objs
render(PV/(p['id']+'_34.png'),objs)
root.location=B(a)
visible=objs+[o for o in allmesh if o.name.startswith('context_h15_')]
for o in allmesh:o.hide_render=o not in visible
render(PV/'h15_34.png',visible)
bpy.ops.wm.save_as_mainfile(filepath=str(S/'h15_falls.blend'))
print('H15_EXPORT_REIMPORT_RENDER_PASS',flush=True)
