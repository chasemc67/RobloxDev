"""blender -b -P out/src/render_pc.py -- --input FILE.blend|fbx
--id h11_lock_lift --output out/previews/cycles [--allow-draft]
Strict default requires passing fitcheck certificate. Cycles OptiX only: no fallback.
"""
import bpy,sys,argparse,math,json
from pathlib import Path
from mathutils import Vector,Matrix
SRC=Path(__file__).resolve().parent;sys.path.insert(0,str(SRC))
from registry_movers import REG,motion
def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--id',required=True);p.add_argument('--output',required=True);p.add_argument('--allow-draft',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    cert=SRC/'fitcheck_movers_pass3_validated.txt'
    if not a.allow_draft and (not cert.exists() or 'ALL PASS: YES' not in cert.read_text()):raise RuntimeError('Final renders blocked: fitcheck has not passed')
    src=Path(a.input);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    if src.suffix.lower()=='.blend':bpy.ops.wm.open_mainfile(filepath=str(src))
    else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(src))
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    devices=[d for d in prefs.devices if d.type=='OPTIX']
    if not devices:raise RuntimeError('No Cycles OptiX GPU available')
    for d in prefs.devices:d.use=d.type=='OPTIX'
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='GPU';sc.cycles.samples=64;sc.cycles.use_denoising=True
    sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100
    sc.world=bpy.data.worlds.new('Sunset');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.14,.19,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.6
    for name,loc,power,size in [('Key',(-7,-8,12),1500,8),('Fill',(6,-2,8),900,7),('Rim',(0,7,10),1200,6)]:
        light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;o=bpy.data.objects.new(name,light);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    root=bpy.data.objects.get(a.id)
    if root is None:raise RuntimeError('Missing prop root '+a.id)
    e=next(x for x in REG if x['id']==a.id);base=root.matrix_world.copy()
    states=[('rest',-1.3 if a.id=='h11_lock_gate' else 0,0),
            ('max',-7 if a.id=='h06_sluice_gate' else -1 if a.id=='h11_quay_lip' else 4 if 'lift' in a.id else 0,4 if 'lift' in a.id else 0)]
    cam=bpy.data.objects.get('Camera')
    if cam is None:cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));sc.collection.objects.link(cam)
    sc.camera=cam;cam.data.lens=42
    for state,offset,tilt in states:
        if 'lift' in a.id:
            # Roblox north-edge hinge z=-25 -> Blender y=+2.
            root.matrix_world=base@Matrix.Translation((0,0,offset))@Matrix.Rotation(-math.radians(tilt),4,'X')
        else:root.matrix_world=base@Matrix.Translation((offset if e['hole']==5 else 0,0,offset if e['hole']==10 else 0))
        bpy.context.view_layer.update();objs=[o for o in sc.objects if o.type=='MESH'];points=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box]
        lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)]);target=(lo+hi)/2;span=max(hi-lo)
        for view in ('eye','34'):
            cam.location=(target.x+span*.95,target.y-span*1.6,5-e['pivot'][1] if view=='eye' else target.z+span*.9);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
            sc.render.filepath=str(out/(a.id+'_'+state+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
    if a.id=='h11_lock_lift':tee_views(e,root,base,out,sc,cam)

def tee_views(e,root,base,out,sc,cam):
    # Actual hole tee (0,0,0), eye y=5, context transformed into lift pivot frame.
    from registry_movers import HOLES,LIP_PARAMS
    from fitcheck_pass3 import residual,CUTS
    import numpy as np
    h=HOLES[10];pivot=e['pivot'];companions={}
    for name in ('h11_lock_chamber','h11_lock_gate','h11_quay_lip'):
        bpy.ops.import_scene.fbx(filepath=str(SRC.parent/'fbx'/(name+'.fbx')))
        r=bpy.data.objects.get(name);reg=next(x for x in REG if x['id']==name)
        delta=[reg['pivot'][i]-pivot[i] for i in range(3)];r.location=(delta[0],-delta[2],delta[1]);companions[name]=(r,r.matrix_world.copy())
    def solid(name,c,size,yaw,color):
        bpy.ops.mesh.primitive_cube_add(size=1,location=(c[0]-pivot[0],-(c[2]-pivot[2]),c[1]-pivot[1]))
        o=bpy.context.object;o.name='context_'+name;o.scale=(size[0],size[2],size[1]);o.rotation_euler.z=-math.radians(yaw)
        mat=bpy.data.materials.get('context_'+color)
        if mat is None:
            mat=bpy.data.materials.new('context_'+color);mat.diffuse_color=tuple(int(color[i:i+2],16)/255 for i in (0,2,4))+(1,)
        o.data.materials.append(mat)
    for f in h['felt']:
        if f['id']=='lock':continue
        pieces=[(f['center'],[f['size'][0],.001,f['size'][1]],f.get('yaw',0))]
        for (_,ob),cut in CUTS.items():
            if ob=='felt_'+f['id']:pieces=[p for c,z,y in pieces for p in residual(c,z,y,cut)]
        for c,z,y in pieces:solid('felt_'+f['id'],c,z,y,'597A50')
    for w in h.get('walls',[])+h.get('rails',[]):
        pieces=[(w['center'],w['size'],w.get('yaw',0))]
        for (_,ob),cut in CUTS.items():
            if ob==w['id']:pieces=[p for c,z,y in pieces for p in residual(c,z,y,cut)]
        for c,z,y in pieces:solid(w['id'],c,z,y,'BCA283')
    for state,t in [('rest',0),('max',7.6)]:
        d,tilt=motion(e['id'],t);root.matrix_world=base@Matrix.Translation((0,0,d))@Matrix.Rotation(-math.radians(tilt),4,'X')
        for name,(r,b) in companions.items():
            d,_=motion(name,t);r.matrix_world=b@Matrix.Translation((0,0,d))
        cam.location=(0,-25,5);target=Vector((0,0,2.5));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48
        sc.render.filepath=str(out/('h11_tee_'+state+'_eye.png'));bpy.ops.render.render(write_still=True)

if __name__=='__main__':main()
