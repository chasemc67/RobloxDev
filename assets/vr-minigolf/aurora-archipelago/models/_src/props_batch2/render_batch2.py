import bpy,json,math
from pathlib import Path
from mathutils import Vector
S=Path(__file__).resolve().parent;D=S.parents[2];PV=D/'models/previews/props_batch2';P=json.loads((S/'parts.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(S/'props_batch2.blend'));sc=bpy.context.scene;cam=sc.camera
for p in P:
 for wid in p['skin_ids']:
  o=bpy.data.objects.get('context_h%02d_'%p['hole']+wid)
  if o:bpy.data.objects.remove(o,do_unlink=True)
def render(path,objs):
    bpy.context.view_layer.update();pts=[o.matrix_world@Vector(v) for o in objs for v in o.bound_box];lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)]);center=(lo+hi)/2
    cam.location=center+Vector((.8,-1.3,1.2)).normalized()*150;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
    # Fit in camera coordinates with 15% margin.
    inv=cam.matrix_world.inverted();cs=[inv@v for v in pts];ww=max(v.x for v in cs)-min(v.x for v in cs);hh=max(v.y for v in cs)-min(v.y for v in cs);cam.data.ortho_scale=max(ww,hh*1280/960)*1.16
    sc.render.filepath=str(path);bpy.ops.render.render(write_still=True);print('RENDERED',path.name,flush=True)
allmesh=[o for o in sc.objects if o.type=='MESH']
for n in [9,10,11,12,13,15,16,17]:
 ids={p['id'] for p in P if p['hole']==n}
 visible=[o for o in allmesh if o.name.startswith('context_h%02d_'%n) or (o.parent and o.parent.name in ids)]
 for o in allmesh:o.hide_render=o not in visible
 render(PV/f'h{n:02d}_34.png',visible)
for o in allmesh:o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(S/'props_batch2.blend'))
print('DONE_CONTEXT_REVIEW',flush=True)
