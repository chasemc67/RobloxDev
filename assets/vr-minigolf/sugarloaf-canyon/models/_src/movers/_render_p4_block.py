# ---------------- pass 4
P4IDS={e['id'] for e in REG if e['id'].startswith(('h07_','h09_','h14_','h17_','dam_'))}
P4STATES={'h09_windpump_vanes':[('rest',0),('rot45',45)],'h14_ore_bucket':[('minus9',-9),('rest',0),('plus9',9)],'h17_shadow_arms':[('rest',0),('rot45',45)]}
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
