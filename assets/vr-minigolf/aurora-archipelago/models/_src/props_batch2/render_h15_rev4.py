import bpy,math
from pathlib import Path
from mathutils import Vector
S=Path(__file__).resolve().parent;D=S.parents[2];PV=D/'models/previews/props_batch2'
bpy.ops.wm.open_mainfile(filepath=str(S/'props_batch2_rev4.blend'));sc=bpy.context.scene;cam=sc.camera
meshes=[o for o in sc.objects if o.type=='MESH'];visible=[o for o in meshes if o.name.startswith('context_h15_') or (o.parent and o.parent.name.startswith('h15_'))]
for o in meshes:o.hide_render=o not in visible
def render(name,objects):
 bpy.context.view_layer.update();pts=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box];lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)]);center=(lo+hi)/2
 cam.location=center+Vector((.8,-1.3,1.2)).normalized()*400;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[cam.matrix_world.inverted()@v for v in pts];xmin,xmax=min(v.x for v in q),max(v.x for v in q);ymin,ymax=min(v.y for v in q),max(v.y for v in q)
 cam.location+=cam.rotation_euler.to_matrix()@Vector(((xmin+xmax)/2,(ymin+ymax)/2,0));cam.data.ortho_scale=max(xmax-xmin,(ymax-ymin)*1280/960)*1.16;sc.render.filepath=str(PV/name);bpy.ops.render.render(write_still=True)
render('h15_34.png',visible)
detail=[o for o in visible if not(o.parent and o.parent.name=='h15_great_frozen_falls')]
for o in meshes:o.hide_render=o not in detail
# Existing detail preview is outside rev4 output scope.
print('DONE_H15_FRAME')
