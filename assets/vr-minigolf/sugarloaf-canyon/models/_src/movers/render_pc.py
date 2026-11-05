"""blender -b -P out/src/render_pc.py -- --input FILE.blend|fbx
--id h11_lock_lift --output out/previews/cycles [--allow-draft]
blender -b -P out/src/render_pc.py -- --hole h09 --output out/previews/cycles/pass4   (pass 4: VR tee view, eye 5 studs)
Strict default requires passing fitcheck certificate (pass 4). Cycles OptiX only: no fallback.
"""
import bpy,sys,argparse,math,json
from pathlib import Path
from mathutils import Vector,Matrix
SRC=Path(__file__).resolve().parent;sys.path.insert(0,str(SRC))
from registry_movers import REG,motion
def main():
    p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--id');p.add_argument('--hole');p.add_argument('--output',required=True);p.add_argument('--allow-draft',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    cert=SRC/'fitcheck_movers_pass4_validated.txt'
    if not a.allow_draft and (not cert.exists() or 'ALL PASS: YES' not in cert.read_text()):raise RuntimeError('Final renders blocked: fitcheck has not passed')
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    if a.hole:
        bpy.ops.wm.read_factory_settings(use_empty=True);sc=setup_cycles(sun=True);hole_view(a.hole,out,sc);return
    src=Path(a.input)
    if src.suffix.lower()=='.blend':bpy.ops.wm.open_mainfile(filepath=str(src))
    else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(src))
    sc=setup_cycles(sun=a.id in P4IDS)
    root=bpy.data.objects.get(a.id)
    if a.id in P4IDS:p4_states(a,root,out,sc);return
    if root is None:raise RuntimeError('Missing prop root '+a.id)
    e=next(x for x in REG if x['id']==a.id);base=root.matrix_world.copy()
    states=[('rest',-1.3 if a.id=='h11_lock_gate' else 0,0),
            ('max',-7 if a.id=='h06_sluice_gate' else -1 if a.id=='h11_quay_lip' else 4 if 'lift' in a.id else 0,0)]  # p8: deck stays level
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
    for state,t in [('rest',0),('max',8.1)]:  # p8: level top dwell 7.1-9.1, lip flush
        d,tilt=motion(e['id'],t);root.matrix_world=base@Matrix.Translation((0,0,d))@Matrix.Rotation(-math.radians(tilt),4,'X')
        for name,(r,b) in companions.items():
            d,_=motion(name,t);r.matrix_world=b@Matrix.Translation((0,0,d))
        cam.location=(0,-25,5);target=Vector((0,0,2.5));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48
        sc.render.filepath=str(out/('h11_tee_'+state+'_eye.png'));bpy.ops.render.render(write_still=True)

# ---------------- pass 4
P4IDS={e['id'] for e in REG if e['id'].startswith(('h07_','h09_','h14_','h17_','dam_'))}
P4STATES={'h09_windpump_vanes':[('rest',0),('rot45',45)],'h14_ore_bucket':[('minus9',-9),('rest',0),('plus9',9)],'h17_shadow_arms':[('rest',0),('rot45',45)],**{f'h17_shadow_arm_head_{y}':[('rest',0),('rot45',45)] for y in (0,90,180,270)}}
def rb2bl(v):return Vector((v[0],-v[2],v[1]))
def setup_cycles(sun=False):
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    devices=[d for d in prefs.devices if d.type=='OPTIX']
    if not devices:raise RuntimeError('No Cycles OptiX GPU available')
    for d in prefs.devices:d.use=d.type=='OPTIX'
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='GPU';sc.cycles.samples=64;sc.cycles.use_denoising=True
    sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100
    sc.world=bpy.data.worlds.new('Sunset');sc.world.use_nodes=True;bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.22,.14,.19,1);bg.inputs[1].default_value=.6
    for name,loc,power,size in [('Key',(-7,-8,12),1500,8),('Fill',(6,-2,8),900,7),('Rim',(0,7,10),1200,6)]:
        light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;o=bpy.data.objects.new(name,light);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    if sun:
        # Game sun bearing 277 deg / elevation 25 deg (course.md); Blender +Y = north (Roblox -Z).
        l=bpy.data.lights.new('Sun','SUN');l.energy=3.0;l.color=(1,.86,.72);l.angle=math.radians(2);o=bpy.data.objects.new('Sun',l);sc.collection.objects.link(o)
        b=math.radians(277);el=math.radians(25);d=Vector((math.sin(b)*math.cos(el),math.cos(b)*math.cos(el),math.sin(el)))
        o.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
    return sc
def frame_cam(sc,cam,objs,view,eye_z):
    bpy.context.view_layer.update();points=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box]
    lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)]);target=(lo+hi)/2;span=max(hi-lo)
    cam.location=(target.x+span*.95,target.y-span*1.6,eye_z if view=='eye' else target.z+span*.9);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
def p4_states(a,root,out,sc):
    e=next(x for x in REG if x['id']==a.id);base=root.matrix_world.copy()
    cam=bpy.data.objects.get('Camera') or bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'))
    if cam.name not in sc.collection.objects:sc.collection.objects.link(cam)
    sc.camera=cam;cam.data.lens=42;cam.data.clip_end=2000
    # Eye height: 5 studs above the felt (hole y 0) / above the dam deck top (y 116).
    eye_z=(116.0+5-e['pivot'][1]) if e.get('world') else 5-e['pivot'][1]
    for state,ang in P4STATES.get(a.id,[('rest',0)]):
        if 'axis' in e:root.matrix_world=base@Matrix.Rotation(math.radians(ang),4,rb2bl(e['axis']))
        objs=[o for o in sc.objects if o.type=='MESH']
        for view in ('eye','34'):
            frame_cam(sc,cam,objs,view,eye_z);sc.render.filepath=str(out/(a.id+'_'+state+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
    if a.id=='h17_shadow_arms':
        # Pass 4b: assembly views = arms + the four separate head FBXs (same pivot), turned together.
        root.matrix_world=base;bpy.context.view_layer.update()
        for y in (0,90,180,270):
            before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(SRC.parent/'fbx'/f'h17_shadow_arm_head_{y}.fbx'))
            for o in [o for o in bpy.data.objects if o not in before and o.parent is None]:o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted()
        for state,ang in P4STATES[a.id]:
            root.matrix_world=base@Matrix.Rotation(math.radians(ang),4,rb2bl(e['axis']))
            objs=[o for o in sc.objects if o.type=='MESH']
            for view in ('eye','34'):
                frame_cam(sc,cam,objs,view,eye_z);sc.render.filepath=str(out/(a.id+'_assembly_'+state+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
HOLE_IDX={'h07':6,'h09':8,'h14':13,'h17':16}
HOLE_LOOK={'h07':(0,1.0,-36),'h09':(0,3.0,-18.5),'h14':(0,4.0,-24),'h17':(0,1.5,-36)}
def hole_view(hid,out,sc):
    from registry_movers import HOLES
    hi=HOLE_IDX[hid];h=HOLES[hi]
    def mat(name,hexc):
        m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
        b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=tuple((int(hexc[i:i+2],16)/255)**2.2 for i in (0,2,4))+(1,);b.inputs['Roughness'].default_value=.9
        return m
    def solid(name,c,size,yaw,m):
        bpy.ops.mesh.primitive_cube_add(size=1,location=rb2bl(c));o=bpy.context.object;o.name='context_'+name;o.scale=(size[0],size[2],size[1]);o.rotation_euler.z=math.radians(yaw);o.data.materials.append(m)
    felt=mat('context_felt','4F8A45');wall=mat('context_wall','D9A28C');env=mat('context_unbuilt_envelope','A79BB3')
    covered=set()
    for e in REG:
        if e['hole']==hi:covered|=set(e.get('realizes',[]))
    for f in h['felt']:
        c=list(f['center']);c[1]-=.05;solid('felt_'+f['id'],c,[f['size'][0],.1,f['size'][1]],f.get('yaw',0),felt)
    for w in h['walls']:
        if w['id'] not in covered:solid(w['id'],w['center'],w['size'],w.get('yaw',0),wall)
    built={e.get('realizes_anchor') for e in REG if e['hole']==hi}
    for an in h.get('decoration_anchors',[]):
        if an['name'] in built:continue
        for j,o in enumerate(an.get('occluders',[])):solid(an['name']+str(j),o['center'],o['size'],o.get('yaw',0),env)
    for e in REG:
        if e['hole']!=hi:continue
        for inst in e.get('instances') or [dict(pivot=e['pivot'])]:
            before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(SRC.parent/'fbx'/(e['id']+'.fbx')))
            new=[o for o in bpy.data.objects if o not in before];r=next(o for o in new if o.parent is None)
            r.location=rb2bl(inst['pivot'])
            for o in new:
                if o.type=='MESH' and o.data.materials and o.data.materials[0].name.startswith('Mist'):
                    b=next(n for n in o.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Alpha'].default_value=.5;o.visible_shadow=False
    cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.lens=24;cam.data.clip_end=1000
    tee=h['tee']['position'];cam.location=rb2bl([tee[0],tee[1]+5,tee[2]]);cam.rotation_euler=(rb2bl(HOLE_LOOK[hid])-cam.location).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=str(out/(hid+'_tee_eye.png'));bpy.ops.render.render(write_still=True)

if __name__=='__main__':main()
