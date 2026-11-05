"""Windows/portable assembled Cycles OptiX hero stills. Run through run_blender.ps1.
All placed FBX instances, 16-bit terrain, source water levels. Hardcoded dusk sun.
--preview produces 640x360 composition checks; --reuse uses saved scene; --shots comma list.
"""
import bpy, json, math, os, sys, time
from pathlib import Path
import numpy as np
from mathutils import Vector
SRC=Path(__file__).resolve().parent; MODELS=SRC.parent; COURSE=MODELS.parent
sys.path.insert(0,str(SRC))
import sclib as L
LAY=json.loads((MODELS/'layout.json').read_text()); MAN=json.loads((MODELS/'manifest.json').read_text())
W=json.loads((COURSE/'world'/'world.json').read_text())
OUT=MODELS/'previews'/'hero'; OUT.mkdir(parents=True,exist_ok=True)
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
PREVIEW='--preview' in ARGS
SHOTS=ARGS[ARGS.index('--shots')+1].split(',') if '--shots' in ARGS else None
BLEND=OUT/'sugarloaf_canyon_hero.blend'

def log(s):
    line=time.strftime('%Y-%m-%d %H:%M:%S')+' '+s
    print(line,flush=True)
    with (SRC/'PROGRESS.md').open('a') as f: f.write(line+'\n')

def rb(p): return Vector((p[0],-p[2],p[1]))

def mesh(name,verts,faces,mat):
    me=bpy.data.meshes.new(name); me.from_pydata([rb(v) for v in verts],[],faces); me.update()
    me.materials.append(mat); ob=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(ob)
    return ob

def material(name,hexv,rough=.8,emission=0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    rgb=tuple(L.lglib.srgb_to_lin(c) for c in L.lglib.hex_rgb(hexv))
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*rgb,1)
    b.inputs['Roughness'].default_value=rough
    if emission:
        b.inputs['Emission Color'].default_value=(*rgb,1); b.inputs['Emission Strength'].default_value=emission
    return m

def terrain():
    image=bpy.data.images.load(str(COURSE/'world'/'heightmap.png')); image.colorspace_settings.name='Non-Color'
    width,height=image.size; px=np.empty(width*height*4,np.float32); image.pixels.foreach_get(px)
    hm=px.reshape(height,width,4)[::-1,:,0]*260
    # 2-stud sampling plus exact map boundaries; coordinates use documented pixel centres.
    core=np.unique(np.r_[np.arange(0,1280,2),1279])
    idx=np.r_[0,core,1279]; coords=np.r_[-640,-640+core+.5,640]
    heights=hm[np.ix_(idx,idx)]; n=len(idx); X,Z=np.meshgrid(coords,coords)
    q=np.hypot(X-80,Z+130)/72
    heights=np.where(q<1,18+110*np.sqrt(np.maximum(0,1-q**4)),heights)
    verts=np.stack([X,heights,Z],-1).reshape(-1,3)
    ids=np.arange(n*n).reshape(n,n); a,b,c,d=ids[:-1,:-1],ids[:-1,1:],ids[1:,1:],ids[1:,:-1]
    faces=np.stack([a,d,c,b],-1).reshape(-1,4)
    m=material('Terrain: brown sugar / peach sand / six-band sandstone','#D88E5C')
    nt=m.node_tree; nodes=nt.nodes; links=nt.links; bs=nodes.get('Principled BSDF')
    geom=nodes.new('ShaderNodeNewGeometry'); sep=nodes.new('ShaderNodeSeparateXYZ'); links.new(geom.outputs['Position'],sep.inputs[0])
    div=nodes.new('ShaderNodeMath'); div.operation='DIVIDE'; div.inputs[1].default_value=36; links.new(sep.outputs['Z'],div.inputs[0])
    mod=nodes.new('ShaderNodeMath'); mod.operation='FRACT'; links.new(div.outputs[0],mod.inputs[0])
    ramp=nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation='CONSTANT'
    colors=['#E8C9A1','#C68C59','#CC8D91','#AF7061']
    ramp.color_ramp.interpolation='LINEAR'
    stops=[(0,0),(.105,0),(.117,1),(.382,1),(.394,2),(.549,2),(.561,3),(.99,3),(1,0)]
    for i,(pos,k) in enumerate(stops):
        e=ramp.color_ramp.elements[i] if i<2 else ramp.color_ramp.elements.new(pos)
        e.position=pos;e.color=(*[L.lglib.srgb_to_lin(c) for c in L.lglib.hex_rgb(colors[k])],1)
    links.new(mod.outputs[0],ramp.inputs[0])
    normal=nodes.new('ShaderNodeSeparateXYZ'); links.new(geom.outputs['Normal'],normal.inputs[0])
    cliff=nodes.new('ShaderNodeMath'); cliff.operation='LESS_THAN'; cliff.inputs[1].default_value=.85; links.new(normal.outputs['Z'],cliff.inputs[0])
    sand=nodes.new('ShaderNodeMixRGB'); links.new(sep.outputs['Z'],sand.inputs[0])
    # Explicit height threshold for peach mesa tops.
    high=nodes.new('ShaderNodeMath'); high.operation='GREATER_THAN'; high.inputs[1].default_value=40; links.new(sep.outputs['Z'],high.inputs[0]); links.new(high.outputs[0],sand.inputs[0])
    for socket,h in [(sand.inputs[1],'#D88E5C'),(sand.inputs[2],'#E59C7C')]: socket.default_value=(*[L.lglib.srgb_to_lin(c) for c in L.lglib.hex_rgb(h)],1)
    mix=nodes.new('ShaderNodeMixRGB'); links.new(cliff.outputs[0],mix.inputs[0]); links.new(sand.outputs[0],mix.inputs[1]); links.new(ramp.outputs[0],mix.inputs[2]); links.new(mix.outputs[0],bs.inputs['Base Color'])
    mesh('Heightmap terrain 1280x260x1280',verts,faces,m)

def water():
    m=material('Canyon turquoise water','#3FB7C9',.18)
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Metallic'].default_value=.2
    foam=material('Foam spillway','#E6FAFF',.3)
    for lake in W['lakes']:
        x,z=lake['center']; rx,rz=lake['radii']; y=lake['level']+.05
        verts=[[x,y,z]]+[[x+rx*math.cos(a),y,z+rz*math.sin(a)] for a in np.linspace(0,2*math.pi,129)[:-1]]
        mesh(lake['name'],verts,[(0,i+1,(i+1)%128+1) for i in range(128)],m)
    for stream in W['streams']:
        for k,(a,b) in enumerate(zip(stream['points'],stream['points'][1:])):
            d=np.array([b['x']-a['x'],b['z']-a['z']]); norm=np.linalg.norm(d)
            if norm<1e-6: continue
            off=np.array([-d[1],d[0]])/norm
            verts=[]
            for p in (a,b):
                for sign in (-1,1):
                    q=np.array([p['x'],p['z']])+off*p['width']/2*sign
                    verts.append([q[0],p['level']+.08,q[1]])
            mesh(stream['name']+str(k),verts,[(0,2,3,1)],m)
    for fall in W['waterfalls']:
        a,b=np.array(fall['top'],float),np.array(fall['bottom'],float)
        off=np.array([fall['width']/2,0,0])
        mesh(fall['name'],[a-off,a+off,b+off,b-off],[(0,1,2,3)],foam)

    mesh('Pass3 render-only downstream spillway', [[-10,108,-289.7],[10,108,-289.7],[10,19,-286],[-10,19,-286]],[(0,1,2,3)],foam)

def assets():
    templates={}
    for p in MAN['pieces']:
        if not p['instances'] or p['id']=='sun_disc': continue
        collection=bpy.data.collections.new('asset_'+p['id'])
        objects=[]
        for file in p['files']:
            before=set(bpy.data.objects)
            bpy.ops.import_scene.fbx(filepath=str(MODELS/file),use_anim=False)
            objects+=list(set(bpy.data.objects)-before)
        for obj in objects:
            for col in list(obj.users_collection): col.objects.unlink(obj)
            collection.objects.link(obj)
            if p['group'] in ('far_card','sky') or p['id']=='rim_silhouette': obj.visible_shadow=False
            if obj.type=='MESH':
                for slot in obj.material_slots:
                    # Normalize imported FBX material names to original palette.
                    name=obj.name.split('__')[-1].split('.')[0] if '__' in obj.name else (slot.material.name.split('.')[0] if slot.material else '')
                    if name in L.MATS: slot.material=L.lglib.get_mat(name)
                if name in L.CARDS:
                    # Geometric alpha cutout for reliable horizon silhouettes in reusable scenes.
                    image=bpy.data.images.load(str(MODELS/'textures'/(L.TEX[name][0]+'.png')),check_existing=False)
                    image.alpha_mode='STRAIGHT'; iw,ih=image.size
                    pixels=np.array(image.pixels[:]).reshape(ih,iw,4)
                    log(f'Cutout {name}: alpha {pixels[:,:,3].min()}..{pixels[:,:,3].max()}')
                    co=np.array([v.co[:] for v in obj.data.vertices]); lo,hi=co.min(0),co.max(0)
                    verts=[]; faces=[]; uvs=[]; n=64
                    for yy in range(n):
                        for xx in range(n):
                            u,v=(xx+.5)/n,(yy+.5)/n
                            if pixels[min(ih-1,int(v*ih)),min(iw-1,int(u*iw)),3]<.5: continue
                            q=len(verts)
                            for du,dv in ((0,0),(1,0),(1,1),(0,1)):
                                uu,vv=(xx+du)/n,(yy+dv)/n
                                verts.append((lo[0]+uu*(hi[0]-lo[0]),lo[1]+(hi[1]-lo[1])*(2*uu-1)**2,lo[2]+vv*(hi[2]-lo[2])))
                                uvs.append((uu,vv))
                            faces.append((q,q+1,q+2,q+3))
                    me=bpy.data.meshes.new(obj.name+'_cutout'); me.from_pydata(verts,[],faces); me.update()
                    uv=me.uv_layers.new(name='UVMap')
                    for loop in me.loops: uv.data[loop.index].uv=uvs[loop.vertex_index]
                    me.materials.append(L.lglib.get_mat(name)); obj.data=me
                if p['group']=='far_card':
                    log(f"Card material {obj.name}: {[s.material.name for s in obj.material_slots]}; UV range {[(min(x.uv[0] for x in layer.data),max(x.uv[0] for x in layer.data),min(x.uv[1] for x in layer.data),max(x.uv[1] for x in layer.data)) for layer in obj.data.uv_layers]}")
        templates[p['id']]=collection
    for k,i in enumerate(LAY['instances']):
        if i['piece'] not in templates: continue
        obj=bpy.data.objects.new(i['piece']+'_'+str(k),None); obj.instance_type='COLLECTION'; obj.instance_collection=templates[i['piece']]
        obj.location=rb(i['pos']); obj.rotation_euler.z=math.radians(i['yaw'])
        s=i.get('scale',[1,1,1]); obj.scale=(s[0],s[2],s[1]); bpy.context.scene.collection.objects.link(obj)
    # FBX importer marks shared colour images alpha_mode=NONE. Restore source PNG alpha.
    for name in L.CARDS:
        mat=L.lglib.get_mat(name)
        for node in mat.node_tree.nodes:
            if node.type=='TEX_IMAGE' and node.image:
                # Load a fresh image datablock: imported embedded images can retain packed opaque pixels.
                node.image=bpy.data.images.load(str(MODELS/'textures'/(L.TEX[name][0]+'.png')),check_existing=False)
                node.image.alpha_mode='STRAIGHT'
                nt=mat.node_tree
                uv=nt.nodes.new('ShaderNodeUVMap'); uv.uv_map='UVMap'; nt.links.new(uv.outputs['UV'],node.inputs['Vector'])
                transparent=nt.nodes.new('ShaderNodeBsdfTransparent')
                mix=nt.nodes.new('ShaderNodeMixShader')
                bs=nt.nodes.get('Principled BSDF'); bs.inputs['Alpha'].default_value=1
                for link in list(bs.inputs['Alpha'].links): nt.links.remove(link)
                nt.links.new(node.outputs['Alpha'],mix.inputs[0]); nt.links.new(transparent.outputs[0],mix.inputs[1]); nt.links.new(bs.outputs[0],mix.inputs[2])
                output=nt.nodes.get('Material Output'); nt.links.new(mix.outputs[0],output.inputs['Surface'])
                log(f'Alpha restored {name}: {node.image.alpha_mode}; explicit UVMap and transparent mix')
    # Sun-disc centre lies on the exact compass bearing/elevation from the Crown.
    bearing,elevation=math.radians(270),math.radians(25)
    direction=Vector((math.sin(bearing)*math.cos(elevation),math.cos(bearing)*math.cos(elevation),math.sin(elevation)))
    pos=rb((-370,196,165))+direction*2500
    bpy.ops.mesh.primitive_plane_add(size=120,location=pos)
    disc=bpy.context.object; disc.name='Sun disc: bearing 277 elevation -3'; disc.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
    disc.data.materials.append(L.lglib.get_mat('SunGold')); disc.visible_shadow=False
    uv=disc.data.uv_layers.active
    # Plane already carries full 0..1 texture UVs.
    light=bpy.data.lights.new('Dusk sun 277 -3','SUN'); light.energy=3; light.color=(1,.66,.47); light.angle=math.radians(5)
    sun=bpy.data.objects.new(light.name,light); bpy.context.scene.collection.objects.link(sun)
    sun.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    # Soft warm sky is essential with the physical sun below the horizon.
    world=bpy.data.worlds.new('Warm rose dusk'); world.use_nodes=True
    nt=world.node_tree; bg=nt.nodes['Background']
    coord=nt.nodes.new('ShaderNodeTexCoord'); sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(coord.outputs['Normal'],sep.inputs[0])
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=0
    ramp.color_ramp.elements[0].color=(1,.38,.10,1); ramp.color_ramp.elements[1].position=.8; ramp.color_ramp.elements[1].color=(.36,.13,.38,1)
    mapping=nt.nodes.new('ShaderNodeMapRange');mapping.inputs['From Min'].default_value=-.45;mapping.inputs['From Max'].default_value=.45;nt.links.new(sep.outputs['Z'],mapping.inputs['Value']);nt.links.new(mapping.outputs[0],ramp.inputs[0]); nt.links.new(ramp.outputs[0],bg.inputs['Color']); bg.inputs['Strength'].default_value=.35
    path=nt.nodes.new('ShaderNodeLightPath');ambient=nt.nodes.new('ShaderNodeBackground');ambient.inputs['Color'].default_value=(.38,.28,.6,1);ambient.inputs['Strength'].default_value=.25;mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(ambient.outputs[0],mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],nt.nodes['World Output'].inputs['Surface']);bpy.context.scene.world=world
    fill=bpy.data.lights.new('Sky bounce','AREA'); fill.energy=350000; fill.shape='DISK'; fill.size=1100; fill.color=(.63,.57,1)
    obj=bpy.data.objects.new(fill.name,fill); obj.location=(0,0,650); bpy.context.scene.collection.objects.link(obj)

def configure():
    sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=128; sc.cycles.use_denoising=True
    sc.cycles.adaptive_threshold=.02; sc.cycles.device='GPU'
    prefs=bpy.context.preferences.addons['cycles'].preferences; prefs.compute_device_type='OPTIX'; prefs.get_devices()
    gpu=[]
    for device in prefs.devices:
        device.use=device.type=='OPTIX'
        if device.use: gpu.append(device.name)
    if not gpu: raise RuntimeError('OptiX GPU unavailable; hero specification requires GPU')
    sc.cycles.max_bounces=6; sc.cycles.transparent_max_bounces=8
    sc.render.resolution_x,sc.render.resolution_y=(640,360) if PREVIEW else (1920,1080)
    sc.render.resolution_percentage=100; sc.render.image_settings.file_format='PNG'
    sc.view_settings.view_transform='AgX'; sc.view_settings.exposure=.35
    log('Cycles OptiX devices: '+', '.join(gpu)+'; 128 samples; denoise; hardcoded sun 277/-3')

def main():
    start=time.time()
    if '--reuse' in ARGS: bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        log('Hero scene: importing all placed FBX assets, 2-stud heightmap terrain, source-level water/falls')
        # Build native node materials first: FBX alpha/emission translation is lossy.
        for name in L.MATS: L.lglib.get_mat(name)
        terrain(); water(); assets()
        # Rose-band sheen, shared by every imported strata mesh.
        mat=L.lglib.get_mat('Strata');nt=mat.node_tree
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(MODELS/'textures/strata_roughness.png'));tex.image.colorspace_settings.name='Non-Color'
        nt.links.new(tex.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Roughness'])
        cam=bpy.data.objects.new('Hero camera',bpy.data.cameras.new('Hero camera')); bpy.context.scene.collection.objects.link(cam); bpy.context.scene.camera=cam
        cam.data.clip_start=.1; cam.data.clip_end=15000
    configure(); sc=bpy.context.scene; cam=sc.camera
    shots=[
      ('old_sugarloaf_skyline',W['spawn']['pos'][:],(80,88,-130),58),
      ('dam_crest_walk',(80,185,-240),(0,80,-299),65),
      ('narrows_crystal_walls',(280,27,310),(280,31,240),75),
      ('junction_town',(115,55,560),(30,20,440),92),
      ('world_vista',(1000,1080,1000),(0,70,0),58),
      ('sunset_arch_from_crown',(-370,170,165),(-1250,155,60),52),
    ]
    shots[0]=(shots[0][0],np.array(shots[0][1])+[0,5,0],shots[0][2],shots[0][3])
    shots[3]=(shots[3][0],np.array(shots[3][1])+[0,5,0],shots[3][2],shots[3][3])
    records=[]
    if not PREVIEW:
        sc['hero_shots']=json.dumps([(n,list(map(float,e)),t,f) for n,e,t,f in shots])
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    for name,eye,target,fov in shots:
        if SHOTS and name not in SHOTS: continue
        for obj in sc.objects:
            if obj.instance_type=='COLLECTION' and obj.instance_collection:
                pid=obj.instance_collection.name.removeprefix('asset_')
                obj.hide_render=(name in ('world_vista','sunset_arch_from_crown') and pid in ('distant_mesa_card','butte_spire_card','far_butte_card'))
                if name=='world_vista' and pid in ('far_arch_card','cloud_streak'): obj.hide_render=True
        bearing,elevation=(277,2) if name=='sunset_arch_from_crown' else (270,25)
        br,el=math.radians(bearing),math.radians(elevation)
        direction=Vector((math.sin(br)*math.cos(el),math.cos(br)*math.cos(el),math.sin(el)))
        sun=next(o for o in sc.objects if o.type=='LIGHT' and o.data.type=='SUN')
        sun.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
        disc=next(o for o in sc.objects if o.name.startswith('Sun disc:'))
        disc.location=rb(eye)+direction*2500;disc.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
        if name=='sunset_arch_from_crown':
            for obj in sc.objects:
                if obj.name.startswith('Heightmap terrain') or obj.name.startswith('rim_silhouette_') or (obj.instance_type=='COLLECTION' and obj.instance_collection.name!='asset_far_arch_card'):obj.hide_render=True
            log('Crown render-only exclusions: heightmap terrain, rim silhouettes, near sunset_arch; reveal far arch without moving world pieces')
        cam.location=rb(eye); cam.rotation_euler=(rb(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.angle=math.radians(fov)
        sc.render.filepath=str(OUT/(name+('_draft' if PREVIEW else '')+'.png'))
        t=time.time(); log('Render start '+name+' engine='+sc.render.engine+' context='+bpy.context.scene.render.engine)
        bpy.ops.render.render(write_still=True)
        elapsed=time.time()-t; log(f'Render complete {name}: {elapsed:.1f}s')
        records.append({'shot':name,'path':str(Path(sc.render.filepath).relative_to(MODELS)).replace('\\','/'),'samples':128,'seconds':round(elapsed,2),'eye':list(map(float,eye)),'target':list(map(float,target)),'fov':fov})
    if not PREVIEW: bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    report={'engine':'Cycles','device':'OptiX GPU','gpu':'NVIDIA GeForce RTX 4090','denoise':True,'resolution':[sc.render.resolution_x,sc.render.resolution_y], 'sun':{'bearing':270,'elevation':25,'arch_bearing':277,'arch_elevation':2},'blend':str(BLEND.relative_to(MODELS)).replace('\\','/'),'scene_and_render_seconds':round(time.time()-start,2),'renders':records}
    (OUT/('draft_report.json' if PREVIEW else 'render_report.json')).write_text(json.dumps(report,indent=2))
    log(f'Hero run finished in {time.time()-start:.1f}s; '+('draft composition checks only' if PREVIEW else f'scene saved {BLEND}'))

if __name__=='__main__': main()
