import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector,Matrix
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S))
import render_pc_pass5 as R
from registry_movers import REG
O=S.parent/'previews/cycles/pass5';O.mkdir(parents=True,exist_ok=True)
assert 'ALL PASS: YES' in (S/'fitcheck_movers_pass5_validated.txt').read_text()
def shot(sc,name,pos,target,ortho=None):
    cam=sc.camera;cam.location=R.rb2bl(pos);cam.rotation_euler=(R.rb2bl(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if ortho else 'PERSP';cam.data.lens=42
    if ortho:cam.data.ortho_scale=ortho
    sc.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
for h in ('h07','h09','h14','h17'):
    bpy.ops.wm.read_factory_settings(use_empty=True);sc=R.setup_cycles(sun=True);R.hole_view(h,O,sc)
    if h=='h07':
        shot(sc,'h07_respawn_pads_eye',[8,5,-30],[1.5,0,-39]);shot(sc,'h07_respawn_pads_34',[10,9,-30],[1.5,0,-39])
        shot(sc,'h07_exit_pad_34',[10,5,-53],[5.15,0,-59])
    if h=='h17':
        shot(sc,'h17_ring_eye',[22,5,-12],[0,.5,-36]);shot(sc,'h17_ring_top',[0,38,-36],[0,0,-36],30)
        shot(sc,'h17_decorative_chamfer_34',[9,4,-43],[6.25,.4,-46.8253])
def load(pid):
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(S.parent/'fbx'/(pid+'.fbx')))
    new=[o for o in bpy.data.objects if o not in before];return next(o for o in new if o.parent is None),new
for pid,angles in [('h09_windpump_vanes',[0,45]),('h14_ore_bucket',[-9,0,9])]:
    for a in angles:
        bpy.ops.wm.read_factory_settings(use_empty=True);sc=R.setup_cycles(sun=True)
        root,objs=load(pid);e=next(e for e in REG if e['id']==pid)
        root.location=R.rb2bl(e['pivot']);root.rotation_euler=Matrix.Rotation(math.radians(a),4,R.rb2bl(e['axis'])).to_euler()
        cid='h09_windpump_vanes_collision' if pid.startswith('h09') else 'h14_ore_bucket_foot_collision'
        cr,co=load(cid);cr.location=root.location;cr.rotation_euler=root.rotation_euler
        mat=bpy.data.materials.new('collision_overlay');mat.diffuse_color=(0.02,1,.8,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.02,1,.8,1);bs.inputs['Emission Color'].default_value=(.02,1,.8,1);bs.inputs['Emission Strength'].default_value=.6
        for o in co:
            if o.type=='MESH':
                o.data.materials.clear();o.data.materials.append(mat);mod=o.modifiers.new('Collider wire overlay','WIREFRAME');mod.thickness=.009
        cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));sc.collection.objects.link(cam);sc.camera=cam
        if pid.startswith('h09'):shot(sc,f'h09_vanes_{a}_overlay',[7,5,-8],[0,4.12,-17.75])
        else:
            shot(sc,f'h14_bucket_{a}_foot_close',[3,1.6,-20],[0,.25,-24])
            shot(sc,f'h14_bucket_{a}_34',[8,7,-12],[0,5,-24])
print('PASS5 Cycles OptiX batch complete')
