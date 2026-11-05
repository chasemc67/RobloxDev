from pathlib import Path
s=Path('out/src');t=(s/'render_batch_pass5.py').read_text();t=t[:t.index("for h in ('h07'")]+t[t.index('def load(pid):'):];t=t.replace("for pid,angles in [('h09_windpump_vanes',[0,45]),('h14_ore_bucket',[-9,0,9])]", "for pid,angles in [('h14_ore_bucket',[-9,0,9])]")
t=t.replace("shot(sc,f'h14_bucket_{a}_foot_close',[3,1.6,-20],[0,.25,-24])", "x=10.25*math.sin(math.radians(a));shot(sc,f'h14_bucket_{a}_foot_close',[x+2,.8,-21],[x,.15,-24],3.2)")
t += """
bpy.ops.wm.read_factory_settings(use_empty=True);sc=R.setup_cycles(sun=True)
for pid in ('h07_island_respawn_stone','h07_teleport_pads','h07_teleport_pad_exit'):
    e=next(e for e in REG if e['id']==pid)
    for inst in e.get('instances') or [dict(pivot=e['pivot'])]:
        root,objs=load(pid);root.location=R.rb2bl(inst['pivot'])
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));sc.collection.objects.link(cam);sc.camera=cam
shot(sc,'h07_respawn_pads_eye',[5,5,-33],[2,0,-38.5])
shot(sc,'h07_respawn_pads_34',[8,8,-33],[2,0,-38.5])
"""
(s/'render_fix_pass5.py').write_text(t)
