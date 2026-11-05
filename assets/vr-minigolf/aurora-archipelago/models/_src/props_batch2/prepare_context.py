from pathlib import Path
import shutil
S=Path(__file__).resolve().parent;D=S.parents[2];bk=S/'_backup_context';bk.mkdir(exist_ok=True)
shutil.copy2(S/'props_batch2.blend',bk/'props_batch2.blend')
for p in (D/'models/previews/props_batch2').glob('h??_34.png'):shutil.copy2(p,bk/p.name)
p=S/'build_batch2.py';t=p.read_text();old="    for w in H[n]['walls']:context_box(n,";new="    for w in H[n]['walls']:\n        if any(w['id'] in p['skin_ids'] for p in P if p['hole']==n):continue\n        context_box(n,";assert old in t;t=t.replace(old,new);p.write_text(t)
render=t[t.index('def render(path,objs):'):t.index('allmesh=[o for o in sc.objects')]
script='''import bpy,json,math
from pathlib import Path
from mathutils import Vector
S=Path(__file__).resolve().parent;D=S.parents[2];PV=D/'models/previews/props_batch2';P=json.loads((S/'parts.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(S/'props_batch2.blend'));sc=bpy.context.scene;cam=sc.camera
for p in P:
 for wid in p['skin_ids']:
  o=bpy.data.objects.get('context_h%02d_'%p['hole']+wid)
  if o:bpy.data.objects.remove(o,do_unlink=True)
'''+render+'''allmesh=[o for o in sc.objects if o.type=='MESH']
for n in [9,10,11,12,13,15,16,17]:
 ids={p['id'] for p in P if p['hole']==n}
 visible=[o for o in allmesh if o.name.startswith('context_h%02d_'%n) or (o.parent and o.parent.name in ids)]
 for o in allmesh:o.hide_render=o not in visible
 render(PV/f'h{n:02d}_34.png',visible)
for o in allmesh:o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(S/'props_batch2.blend'))
print('DONE_CONTEXT_REVIEW',flush=True)
'''
(S/'render_batch2.py').write_text(script)
