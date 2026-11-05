"""LOOK8 (2026-10-14, Game Art Bot): look7 + trading-post foreground props (render-only), sun low IN frame, orange-to-pink sky, far cliffs lowered and broken into separate varied hoodoo spires (render-only).
LOOK7 (2026-10-14): pass-6 scene + latest approved FBX (fix_zfight*, fit030), look7 dressing (path edging, dirt, denser props, stepped cliff bases), golden-hour relight (sun 25 deg #FFC890, exposure 0.65, orange horizon, deeper turquoise sky, lifted floor fill).
Pass 6 staged hero still (copy of render_hero_pass5.py). Run through run_blender.ps1.
All placed FBX instances (incl. the pass-6 dressing, trading post, tower cliffs, raised gondola station), 16-bit
terrain, source water levels, plus RENDER-SCENE-ONLY hole staging from holes.json: felt lanes, ROUNDED CLAY-BRICK
CURBS in place of the pass-5 candy-striped rails, cups + flags. Low orange sun 277/4 rim-lighting the cliff tops,
second orange rim sun 300/4, peach-to-gold camera sky behind the far mesas.
Shot: V1-hub-tee1 (-> previews/hero/V1-hub-tee1_pass6.png). --preview: 640x360, 16 samples, *_pass6_draft.png.
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
BUNDLE=Path(os.environ.get('LOOK7_BUNDLE',r'C:\Users\chase\sc_look7'))
PMAP=json.loads((BUNDLE/'piece_files.json').read_text())
DRESS=json.loads((BUNDLE/'layout_look7_dressing.json').read_text())
OUT=MODELS/'previews'/'hero'; OUT.mkdir(parents=True,exist_ok=True)
ARGS=[a for x in (sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []) for a in x.split()]
PREVIEW='--preview' in ARGS
SHOTS=ARGS[ARGS.index('--shots')+1].split(',') if '--shots' in ARGS else None
HOLES=json.loads((COURSE/'holes.json').read_text())['holes']
SUN_BEARING,SUN_ELEV=float(os.environ.get('L7_SUN_BEARING','18')),float(os.environ.get('L7_SUN_ELEV','6'))

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

    # A render-only sheet hugs the downstream face; source waterfall remains intact.
    foam=material('Pass4 luminous streak foam','#FFFFFF',.38,.45)
    nt=foam.node_tree; tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=1.8
    coord=nt.nodes.new('ShaderNodeTexCoord'); mapping=nt.nodes.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=(80,2.8,.6)
    nt.links.new(coord.outputs['Generated'],mapping.inputs[0]);nt.links.new(mapping.outputs[0],tex.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.28,.62,.72,1);ramp.color_ramp.elements[1].color=(1,1,1,1)
    nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],nt.nodes.get('Principled BSDF').inputs['Base Color'])
    mesh('Pass4 downstream spillway sheet', [[-10,108,-299.6],[10,108,-299.6],[10,16.8,-297.7],[-10,16.8,-297.7]],[(0,1,2,3)],foam)
    streak=material('Pass4 waterfall blue-white grooves','#C8E7EC',.5,.08)
    for i in range(27):
        x=-9.6+i*.73;w=.10+.07*(i%3)
        mesh('Pass4 vertical water streak',[(x,107.5,-299.4),(x+w,107.5,-299.4),(x+w+.12,18,-297.5),(x+.12,18,-297.5)],[(0,1,2,3)],streak)
    ring=material('Pass4 plunge foam' ,'#FFFFFF',.65,.3)
    verts=[]
    for i in range(96):
        a=i*2*math.pi/96
        for r in (12,15): verts.append((r*math.cos(a),17.25,-288+r*.65*math.sin(a)))
    mesh('Pass4 plunge pool foam ring',verts,[(2*i,2*i+1,(2*i+3)%192,(2*i+2)%192) for i in range(96)],ring)
    mist=bpy.data.materials.new('Pass4 base spray volume');mist.use_nodes=True
    nt=mist.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');vol=nt.nodes.new('ShaderNodeVolumePrincipled');vol.inputs['Density'].default_value=.035;vol.inputs['Color'].default_value=(.85,.94,1,1);nt.links.new(vol.outputs['Volume'],out.inputs['Volume'])
    for x in (-9,0,9):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=rb((x,21,-290)))
        ob=bpy.context.object;ob.name='Pass4 base spray';ob.scale=(8,7,5);ob.data.materials.append(mist)

def assets():
    templates={}
    GROUP={p['id']:p['group'] for p in MAN['pieces']}
    plist=[dict(id=k,files=v,group=GROUP.get(k,'look7_dressing'),instances=[1]) for k,v in PMAP.items()]
    for p in plist:
        if not p['instances'] or p['id']=='sun_disc': continue
        collection=bpy.data.collections.new('asset_'+p['id'])
        objects=[]
        for file in p['files']:
            before=set(bpy.data.objects)
            bpy.ops.import_scene.fbx(filepath=str(BUNDLE/file) if (BUNDLE/file).exists() else str(MODELS/file),use_anim=False)
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
    log(f"Look7 templates {len(templates)}; layout {len(LAY['instances'])} + dressing {len(DRESS['instances'])} instances")
    for k,i in enumerate(LAY['instances']+DRESS['instances']):
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
    disc=bpy.context.object; disc.name='Sun disc: pass4 west'; disc.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
    disc.data.materials.append(L.lglib.get_mat('SunGold')); disc.visible_shadow=False
    uv=disc.data.uv_layers.active
    # Plane already carries full 0..1 texture UVs.
    light=bpy.data.lights.new('Golden-hour west key','SUN'); light.energy=3.8; light.color=(1,.57,.28); light.angle=math.radians(5)
    sun=bpy.data.objects.new(light.name,light); bpy.context.scene.collection.objects.link(sun)
    sun.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    # Soft warm sky is essential with the physical sun below the horizon.
    world=bpy.data.worlds.new('Pass4 peach turquoise sky / lavender ambient'); world.use_nodes=True
    nt=world.node_tree; bg=nt.nodes['Background']
    coord=nt.nodes.new('ShaderNodeTexCoord'); sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(coord.outputs['Normal'],sep.inputs[0])
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=0
    ramp.color_ramp.elements[0].color=(.999,.485,.254,1); ramp.color_ramp.elements[1].position=.8; ramp.color_ramp.elements[1].color=(.078,.578,.687,1)
    mapping=nt.nodes.new('ShaderNodeMapRange');mapping.inputs['From Min'].default_value=0;mapping.inputs['From Max'].default_value=-.5;nt.links.new(sep.outputs['Z'],mapping.inputs['Value']);nt.links.new(mapping.outputs[0],ramp.inputs[0]); nt.links.new(ramp.outputs[0],bg.inputs['Color']); bg.inputs['Strength'].default_value=.65
    path=nt.nodes.new('ShaderNodeLightPath');ambient=nt.nodes.new('ShaderNodeBackground');ambient.inputs['Color'].default_value=(.38,.28,.6,1);ambient.inputs['Strength'].default_value=.65;mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(ambient.outputs[0],mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],nt.nodes['World Output'].inputs['Surface']);bpy.context.scene.world=world
    fill=bpy.data.lights.new('Sky bounce','AREA'); fill.energy=650000; fill.shape='DISK'; fill.size=1100; fill.color=(.63,.57,1)
    obj=bpy.data.objects.new(fill.name,fill); obj.location=(0,0,650); bpy.context.scene.collection.objects.link(obj)

def pass4_clouds():
    cloud=material('Pass4 warm cumulus','#FFE3CD',.95,.15)
    for x,y,z,s in [(-1100,480,-600,100),(-1450,530,350,130),(400,600,-1100,100)]:
        for dx,dy,dz,r in [(-.7,0,0,.65),(0,.25,0,.85),(.7,0,0,.6),(0,0,.35,.6)]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=rb((x+dx*s,y+dy*s,z+dz*s)))
            ob=bpy.context.object;ob.name='Pass4 lit cumulus';ob.scale=(s*r,s*r*.7,s*r*.45);ob.data.materials.append(cloud)
            for poly in ob.data.polygons: poly.use_smooth=True

def sundir(bearing,elevation):
    br,el=math.radians(bearing),math.radians(elevation)
    return Vector((math.sin(br)*math.cos(el),math.cos(br)*math.cos(el),math.sin(el)))

def rot(yaw,x,z):
    # holes.json: x' = x cos + z sin; z' = -x sin + z cos (positive yaw = CCW in map view).
    c,s=math.cos(math.radians(yaw)),math.sin(math.radians(yaw)); return x*c+z*s,-x*s+z*c

def felt_height(h,lx,lz,margin):
    """Felt top (hole-local y) at a hole-local point, or None. Planar slopes per holes.json schema."""
    best=None
    for f in h['felt']:
        cx,cy,cz=f['center']; sx,sz=f['size']; px,pz=rot(-f['yaw'],lx-cx,lz-cz)
        if abs(px)>sx/2+margin or abs(pz)>sz/2+margin: continue
        y=cy; sl=f.get('slope')
        if sl:
            u,n=(px,sx) if sl['axis']=='x' else (pz,sz); y+=sl['rise']*max(-.5,min(.5,u/n))
        best=y if best is None else max(best,y)
    return best

def stage_holes():
    """Render-scene-only staging of every hole in holes.json: felt slabs, rails, cups, flags, H1 ball."""
    felt=material('Pass5b staged putting felt','#3E9A45',.95)
    nt=felt.node_tree; bs=nt.nodes.get('Principled BSDF')
    geom=nt.nodes.new('ShaderNodeNewGeometry'); noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=9; noise.inputs['Detail'].default_value=6
    nt.links.new(geom.outputs['Position'],noise.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB'); lin=lambda hx:(*[L.lglib.srgb_to_lin(c) for c in L.lglib.hex_rgb(hx)],1)
    ramp.color_ramp.elements[0].position=.35; ramp.color_ramp.elements[0].color=lin('#23962F'); ramp.color_ramp.elements[1].position=.65; ramp.color_ramp.elements[1].color=lin('#52C24A')
    nt.links.new(noise.outputs['Fac'],ramp.inputs[0]); nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
    fine=nt.nodes.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value=60; nt.links.new(geom.outputs['Position'],fine.inputs['Vector'])
    bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.18; bump.inputs['Distance'].default_value=.02
    nt.links.new(fine.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    if 'Sheen Weight' in bs.inputs: bs.inputs['Sheen Weight'].default_value=.4
    stripe=material('Pass5b candy rail cap','#D9343A',.5)
    nt=stripe.node_tree; geom=nt.nodes.new('ShaderNodeNewGeometry'); sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geom.outputs['Position'],sep.inputs[0])
    add=nt.nodes.new('ShaderNodeMath'); add.operation='ADD'; nt.links.new(sep.outputs['X'],add.inputs[0]); nt.links.new(sep.outputs['Y'],add.inputs[1])
    div=nt.nodes.new('ShaderNodeMath'); div.operation='DIVIDE'; div.inputs[1].default_value=3; nt.links.new(add.outputs[0],div.inputs[0])
    fr=nt.nodes.new('ShaderNodeMath'); fr.operation='FRACT'; nt.links.new(div.outputs[0],fr.inputs[0])
    gt=nt.nodes.new('ShaderNodeMath'); gt.operation='GREATER_THAN'; gt.inputs[1].default_value=.5; nt.links.new(fr.outputs[0],gt.inputs[0])
    mix=nt.nodes.new('ShaderNodeMixRGB'); mix.inputs[1].default_value=lin('#D9343A'); mix.inputs[2].default_value=lin('#FFF8F0')
    nt.links.new(gt.outputs[0],mix.inputs[0]); nt.links.new(mix.outputs[0],nt.nodes.get('Principled BSDF').inputs['Base Color'])
    timber=L.lglib.get_mat('Timber'); white=L.lglib.get_mat('MintWhite'); cupm=material('Pass5b cup liner','#1C1416',.6)
    acc={'felt':([],[]),'curb':([],[])}
    # Pass 6: rounded clay-brick curb material (per-brick tint from a brick_id attribute, soft noise, faint bump)
    brick=material('Pass6 rounded clay-brick curb','#B65C3E',.82)
    bnt=brick.node_tree; bbs=bnt.nodes.get('Principled BSDF')
    attr=bnt.nodes.new('ShaderNodeAttribute'); attr.attribute_name='brick_id'
    wn=bnt.nodes.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions='1D'; bnt.links.new(attr.outputs['Fac'],wn.inputs['W'])
    br=bnt.nodes.new('ShaderNodeValToRGB'); br.color_ramp.elements[0].color=lin('#A24C2C'); br.color_ramp.elements[1].color=lin('#CF7A52')
    bnt.links.new(wn.outputs['Value'],br.inputs[0])
    bg=bnt.nodes.new('ShaderNodeNewGeometry'); bn=bnt.nodes.new('ShaderNodeTexNoise'); bn.inputs['Scale'].default_value=3.5
    bnt.links.new(bg.outputs['Position'],bn.inputs['Vector'])
    mixb=bnt.nodes.new('ShaderNodeMixRGB'); mixb.blend_type='MULTIPLY'; mixb.inputs[0].default_value=.3
    bnt.links.new(br.outputs['Color'],mixb.inputs[1]); bnt.links.new(bn.outputs['Color'],mixb.inputs[2]); bnt.links.new(mixb.outputs[0],bbs.inputs['Base Color'])
    bump2=bnt.nodes.new('ShaderNodeBump'); bump2.inputs['Strength'].default_value=.25; bnt.links.new(bn.outputs['Fac'],bump2.inputs['Height']); bnt.links.new(bump2.outputs['Normal'],bbs.inputs['Normal'])
    brick_ids=[]
    PROF=[(-1,0.0),(1,0.0),(1,.55),(.92,.74),(.72,.9),(.4,.99),(0,1.0),(-.4,.99),(-.72,.9),(-.92,.74),(-1,.55)]
    def curb(cx,cz,w,ends,W_):
        """Row of rounded clay bricks along a holes.json wall (render-only): bricks ~1.5 long with 0.12 joints, rounded
        top profile, 0.08 wider than the rail each side; heights follow the staged rail ends (felt + 1.0)."""
        sx,sy,sz=w['size']; L_=sz; n=max(1,int(round(L_/1.5))); seg=L_/n
        hw=sx/2+.08
        m=len(PROF)
        for k in range(n):
            za,zb=-L_/2+k*seg+.06,-L_/2+(k+1)*seg-.06
            v,f=acc['curb']; q=len(v)
            for zz in (za,zb):
                t=(zz+L_/2)/L_; top=ends[0][0]+(ends[1][0]-ends[0][0])*t; bot=ends[0][1]+(ends[1][1]-ends[0][1])*t
                hh=top-bot
                for px,py in PROF:
                    dx,dz=rot(w['yaw'],px*hw,zz); v.append(W_(cx+dx,bot+py*hh,cz+dz))
            for i in range(m): f.append((q+i,q+(i+1)%m,q+m+(i+1)%m,q+m+i))
            f.append(tuple(range(q+m-1,q-1,-1))); f.append(tuple(range(q+m,q+2*m)))
            brick_ids.extend([(hash((round(cx,2),round(cz,2),k))%997)/997.0]*(2*m))
    def box(key,corners):
        """corners: 8 world points, bottom ring then top ring (same winding)."""
        v,f=acc[key]; q=len(v); v.extend(corners)
        f.extend([(q,q+3,q+2,q+1),(q+4,q+5,q+6,q+7)]+[(q+i,q+(i+1)%4,q+4+(i+1)%4,q+4+i) for i in range(4)])
    nfelt=nrail=0
    for h in [h for h in HOLES if h['world_offset'][1]<40]:  # look8: upper-tier holes sit on lowered terrain, not staged
        ox,oy,oz=h['world_offset']; yaw=h['world_yaw']
        W_=lambda lx,ly,lz:(ox+rot(yaw,lx,lz)[0],oy+ly,oz+rot(yaw,lx,lz)[1])
        for f in h['felt']:
            cx,cy,cz=f['center']; sx,sz=f['size']; sl=f.get('slope'); top=[]
            for px,pz in ((-sx/2,-sz/2),(sx/2,-sz/2),(sx/2,sz/2),(-sx/2,sz/2)):
                y=cy
                if sl: y+=sl['rise']*((px/sx) if sl['axis']=='x' else (pz/sz))
                dx,dz=rot(f['yaw'],px,pz); top.append((cx+dx,y+.03,cz+dz))
            thick=f.get('thickness',.5) if f.get('solid',True) is False else .6
            box('felt',[W_(x,y-thick,z) for x,y,z in top]+[W_(x,y,z) for x,y,z in top]); nfelt+=1
        for w in h['walls']:
            if w.get('kind')=='bumper': continue  # bumpers are boulders/hoodoos dressed by kit props
            cx,cy,cz=w['center']; sx,sy,sz=w['size']; ends=[]
            for e in (-1,1):
                dx,dz=rot(w['yaw'],0,e*sz/2); hy=felt_height(h,cx+dx,cz+dz,.9) if sy>1.6 else None
                ends.append((hy+1.0,hy-.35) if hy is not None else (cy+sy/2,cy-sy/2))
            def ring(dw,which,lift=0):
                pts=[]
                for (ex,ez),k in (((-1,-1),0),((1,-1),0),((1,1),1),((-1,1),1)):
                    px,pz=rot(w['yaw'],ex*(sx/2+dw),ez*sz/2); t,b=ends[k]
                    y={'top':t,'bot':b,'captop':t+.06,'capbot':t-.22}[which]+lift
                    pts.append(W_(cx+px,y,cz+pz))
                return pts
            curb(cx,cz,w,ends,W_); nrail+=1
        # Cup liner + rim, flag pole and banner (pole height/banner from holes.json flag spec).
        c=h['cup']; fl=c['flag']; cx,cy,cz=c['position']; cyw=(felt_height(h,cx,cz,0) or cy)+.04
        r=c['radius']; base=W_(cx,cyw,cz)
        verts=[base]+[(base[0]+r*math.cos(a),base[1],base[2]+r*math.sin(a)) for a in np.linspace(0,2*math.pi,25)[:-1]]
        mesh(h['id']+' cup',verts,[(0,i+1,(i+1)%24+1) for i in range(24)],cupm)
        verts=[(base[0]+rr*math.cos(a),base[1]+.005,base[2]+rr*math.sin(a)) for a in np.linspace(0,2*math.pi,25)[:-1] for rr in (r,r+.12)]
        mesh(h['id']+' cup rim',verts,[(2*i,(2*i+2)%48,(2*i+3)%48,2*i+1) for i in range(24)],white)
        pr=fl['pole_diameter']/2; ph=fl['pole_height']; ring8=[(pr*math.cos(a),pr*math.sin(a)) for a in np.linspace(0,2*math.pi,9)[:-1]]
        verts=[(base[0]+a,base[1]+yy,base[2]+b) for yy in (0,ph) for a,b in ring8]
        mesh(h['id']+' flag pole',verts,[(i,(i+1)%8,8+(i+1)%8,8+i) for i in range(8)]+[tuple(range(15,7,-1))],white)
        bw,bh,bd=fl['banner_size']; bm=material(h['id']+' banner',fl['banner_color'],.7,.15)
        pts=[]
        for yy in (ph-bh,ph):
            for lx,lz in ((0,-bd/2),(bw,-bd/2),(bw,bd/2),(0,bd/2)):
                dx,dz=rot(yaw,lx,lz); pts.append((base[0]+dx,base[1]+yy,base[2]+dz))
        mesh(h['id']+' flag banner',pts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],bm)
    for key,m in (('felt',felt),('curb',brick)):
        v,f=acc[key]; ob=mesh('Pass6 staged '+key,v,f,m)
        if key=='curb':
            at=ob.data.attributes.new('brick_id','FLOAT','POINT'); at.data.foreach_set('value',brick_ids)
            for poly in ob.data.polygons: poly.use_smooth=True
    h=HOLES[0]; t=h['tee']['position']; ox,oy,oz=h['world_offset']; br=.24
    bpy.ops.mesh.primitive_uv_sphere_add(radius=br,segments=24,ring_count=12,location=rb((ox+t[0],oy+t[1]+.03+br,oz+t[2])))
    ball=bpy.context.object; ball.name='Pass5b H1 ball (x3 scale for legibility)'; ball.data.materials.append(white)
    for p in ball.data.polygons: p.use_smooth=True
    log(f'Pass6 staging (render-only, holes.json): {nfelt} felt slabs, {nrail} rounded clay-brick curbs (bumpers skipped), {len(HOLES)} cups+flags, H1 ball')


EYE8=(60.0,25.5,482.0)
def imp(path):
    before=set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=str(path),use_anim=False); objs=list(set(bpy.data.objects)-before)
    col=bpy.data.collections.new('l8_'+Path(path).stem)
    for o in objs:
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o)
        if o.type=='MESH':
            for slot in o.material_slots:
                n=o.name.split('__')[-1].split('.')[0]
                if n in L.MATS: slot.material=L.lglib.get_mat(n)
    return col
def inst(col,pos,yaw,s=(1,1,1),name='l8'):
    ob=bpy.data.objects.new(name,None); ob.instance_type='COLLECTION'; ob.instance_collection=col
    ob.location=rb(pos); ob.rotation_euler.z=math.radians(yaw); ob.scale=(s[0],s[2],s[1]); bpy.context.scene.collection.objects.link(ob); return ob
def look8_mods():
    rng=np.random.default_rng(8); ex=np.array(EYE8)
    # 1. far cliffs (render-only): hide cliff/slot/rim instances > 220 studs ahead in the view cone; replace with separate varied hoodoo spires, lower
    sp=[imp(MODELS/'fbx'/f'hoodoo_spire_{c}.fbx') for c in 'abcd']
    hidden=[];spires=0
    for ob in list(bpy.context.scene.objects):
        if ob.instance_type!='COLLECTION' or not ob.instance_collection: continue
        n=ob.instance_collection.name.removeprefix('asset_')
        if n in ('distant_mesa_card','far_butte_card','butte_spire_card','far_arch_card'):
            ob.scale=(ob.scale[0],ob.scale[1],ob.scale[2]*0.35);hidden.append('card '+n);continue
        if not n.startswith(('cliff','slot','rim_silhouette')): continue
        g=np.array([ob.location.x,ob.location.z,-ob.location.y]);d=g-ex
        if -d[2]<60 or abs(d[0])>-d[2]*2.5+40: continue
        ob.hide_render=True;ob['l8_hidden']=1;hidden.append(n)
        if n.startswith('rim'): continue
        if rng.random()<0.3:   # sparse: gaps between spires so the horizon glow shows through
            dist=float(np.hypot(d[0],d[2]));sc=float(rng.uniform(0.9,1.6));sy=min(sc*float(rng.uniform(0.9,1.6)),dist*0.15/32)
            inst(sp[rng.integers(4)],(g[0]+rng.uniform(-6,6),18.0,g[2]+rng.uniform(-6,6)),float(rng.uniform(0,360)),(sc,sy,sc),'l8 hoodoo');spires+=1
    # look8: everything on the upper tiers (base y>40) would float over the lowered terrain -> hidden in this shot
    up=0
    for ob in bpy.context.scene.objects:
        if ob.instance_type=='COLLECTION' and ob.instance_collection and ob.location.z>40 and not ob.name.startswith('l8') and ob.instance_collection.name.removeprefix('asset_') not in ('cloud_streak','distant_mesa_card','far_butte_card','butte_spire_card','far_arch_card'):
            ob.hide_render=True;ob['l8_hidden']=1;up+=1
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH' and ob.name in ('Sugarloaf Reservoir',) or ob.name.startswith(('Pass4','Spillway')): ob.hide_render=True
    log(f'Look8 hid {up} upper-tier instances + reservoir/spillway')
    # lower the far terrain rim so the glow reads (render-only)
    t=next((o for o in bpy.data.objects if o.name.startswith('Heightmap terrain')),None)
    log(f'Look8 terrain object: {t.name if t else None}');t.hide_render=os.environ.get('L8DBG','0')=='1'
    if t:
        me=t.data;co=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',co);co=co.reshape(-1,3)
        gz=-co[:,1];far=(ex[2]-gz)>260;co[far,2]=np.minimum(co[far,2],18+(co[far,2]-18)*0.12)
        me.vertices.foreach_set('co',co.ravel());me.update()
    # 2. trading-post foreground (render-only kit props)
    P={k:imp(MODELS/'fbx'/f'{k}.fbx') for k in ('barrel_a','barrel_b','lantern_post','crystal_cluster_a','crystal_cluster_b','crystal_cluster_c','rock_candy_cluster','lollipop_cactus_a','railing_12')}
    FG=[('barrel_b',(52.6,18,475.6),20),('barrel_a',(51.2,18,473.8),75),('barrel_b',(53.4,18,472.9),140),('lantern_post',(54.4,18,470.5),90),('crystal_cluster_b',(48.8,18,466.5),30),('lollipop_cactus_a',(49.5,18,465.5),0),
        ('barrel_b',(67.4,18,475.4),200),('lantern_post',(66.0,18,470.6),-90),('crystal_cluster_a',(70.5,18,467.5),210),('rock_candy_cluster',(67.8,18,467.2),60),('rock_candy_cluster',(70.5,18,474.5),120)]
    for k,pos,yaw in FG: inst(P[k],pos,yaw,name='l8 fg '+k)
    # rope posts: timber posts + sagging licorice rope lining the tee walk both sides
    tim=L.lglib.get_mat('Timber') if 'Timber' in L.MATS else material('l8 post','#7A5230');rope=material('l8 rope','#C9A46A',.9)
    for x in (55.6,64.4):
        zs=[478.5,474.5,470.5];prev=None
        for z in zs:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.22,depth=2.2,location=rb((x,19.1,z)));o=bpy.context.object;o.data.materials.append(tim)
            if prev is not None:
                pts=[(x,20.0-0.35*math.sin(math.pi*u),prev+(z-prev)*u) for u in np.linspace(0,1,9)]
                cu=bpy.data.curves.new('l8rope','CURVE');cu.dimensions='3D';cu.bevel_depth=.07;spl=cu.splines.new('POLY');spl.points.add(len(pts)-1)
                for q,pt in zip(spl.points,pts): q.co=(*rb(pt),1)
                ro=bpy.data.objects.new('l8 rope',cu);ro.data.materials.append(rope);bpy.context.scene.collection.objects.link(ro)
            prev=z
    import collections;vis=collections.Counter()
    for ob in bpy.context.scene.objects:
        if ob.hide_render: continue
        if ob.instance_type=='COLLECTION' and ob.instance_collection:
            g=np.array([ob.location.x,ob.location.z,-ob.location.y]);d=g-ex
            if -d[2]>100 and abs(d[0])<-d[2]: vis[ob.instance_collection.name]+=1
        elif ob.type=='MESH':
            bb=[ob.matrix_world@Vector(c) for c in ob.bound_box];zmax=max(v.z for v in bb)
            if zmax>60: vis['MESH '+ob.name[:40]]+=1
    tall=collections.Counter()
    for ob in bpy.context.scene.objects:
        if ob.hide_render or ob.instance_type!='COLLECTION' or not ob.instance_collection: continue
        for o in ob.instance_collection.objects:
            if o.type!='MESH': continue
            bb=[ob.matrix_world@o.matrix_world@Vector(c) for c in o.bound_box]
            if max(v.z for v in bb)>45 and max(v.y for v in bb)>-ex[2]+40: tall[ob.instance_collection.name]+=1;break
    if os.environ.get('L8DBG2','0')=='1':
        for ob in bpy.context.scene.objects:
            if ob.instance_type=='COLLECTION': ob.hide_render=True
        log('DBG2 all instances hidden')
    log('Look8 tall visible: '+str(tall.most_common(30)))
    log('Look8 visible far: '+str(vis.most_common(40)))
    log(f'Look8 mods: hid {len(hidden)} far cliff/rim instances, {spires} separate hoodoo spires (scale 1.0-2.4, gaps), far terrain lowered x0.2 beyond 70 studs, {len(FG)} foreground props + rope posts')

GRADE=dict(exposure=float(os.environ.get('L7_EXPOSURE','0.65')),look='AgX - Punchy',sky_strength=float(os.environ.get('L7_SKY','1.0')))
KEY=dict(energy=float(os.environ.get('L7_KEY','7.0')),hex='#FFC890'); RIM=dict(bearing=285,elev=6,energy=float(os.environ.get('L7_RIM','2.5')),color=(1,.45,.15),shadow=False); FILL=dict(bounce=float(os.environ.get('L7_BOUNCE','480000')),ambient=float(os.environ.get('L7_AMB','0.62')))
SKY=[(0,'#FF7A1E'),(.08,'#FF9A3C'),(.2,'#FFA868'),(.34,'#FF8FA0'),(.55,'#E77FB8'),(.9,'#9A6FC0')]
def relight():
    """Pass 6 light: low orange key 277/4 (rakes the floor, rim-lights the cliff tops), second strong orange rim sun
    300/4 behind the left rim, peach-to-gold camera sky (gold at the horizon behind the far mesas)."""
    sc=bpy.context.scene
    sun=next(o for o in sc.objects if o.type=='LIGHT' and o.data.type=='SUN')
    sun.data.energy=KEY['energy']; sun.data.color=tuple(L.lglib.srgb_to_lin(c) for c in L.lglib.hex_rgb(KEY['hex'])); sun.data.angle=math.radians(2.5)
    rim=bpy.data.lights.new('Orange rim','SUN'); rim.energy=RIM['energy']; rim.color=RIM['color']; rim.angle=math.radians(3)
    rim.use_shadow=RIM['shadow']   # render-only rim: at 3-4 deg the real sun is blocked by the west mesas, so the orange rim on the cliff tops is a no-shadow fill from the same bearing
    ob=bpy.data.objects.new(rim.name,rim); sc.collection.objects.link(ob)
    nt=sc.world.node_tree; ramp=next(n for n in nt.nodes if n.type=='VALTORGB')
    lin=lambda hx:(*[L.lglib.srgb_to_lin(c) for c in L.lglib.hex_rgb(hx)],1)
    els=ramp.color_ramp.elements; els[0].position=SKY[0][0]; els[0].color=lin(SKY[0][1]); els[1].position=SKY[-1][0]; els[1].color=lin(SKY[-1][1])
    for pos,hx in SKY[1:-1]:
        e=els.new(pos); e.color=lin(hx)
    fill=next(o for o in sc.objects if o.name.startswith('Sky bounce')); fill.data.energy=FILL['bounce']
    nt.nodes['Background'].inputs['Strength'].default_value=GRADE['sky_strength']
    amb=next(n for n in nt.nodes if n.type=='BACKGROUND' and n.name!='Background'); amb.inputs['Strength'].default_value=FILL['ambient']
    log(f'Look7 relight: key sun {SUN_BEARING}/{SUN_ELEV} {KEY}; rim sun {RIM}; fill {FILL}; grade {GRADE}; sky '+'>'.join(h for _,h in SKY))

def measure_arch():
    col=bpy.data.collections['asset_sunset_arch'];points=[]
    for ob in col.objects:
        if ob.type=='MESH': points.extend([ob.matrix_world @ v.co for v in ob.data.vertices])
    coords=np.array([[v.x,v.z,-v.y] for v in points]);lo=coords.min(0);hi=coords.max(0)
    # Inner lintel at centre of opening, measured on the imported vertices.
    centre=coords[np.abs(coords[:,2])<3]
    lintel=float(centre[:,1].min())+190.4
    log(f'Pass4 imported arch bounds local game: {lo.tolist()}..{hi.tolist()}; central inner lintel world y={lintel:.3f}; opening centre z=205, base y=190.4')
    bpy.context.scene['pass4_arch_bounds']=json.dumps({'local_min':lo.tolist(),'local_max':hi.tolist(),'inner_lintel_y':lintel})

def configure():
    sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=16 if PREVIEW else 128; sc.cycles.use_denoising=True
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
    sc.view_settings.view_transform='AgX'; sc.view_settings.exposure=GRADE['exposure']
    try:
        sc.view_settings.look=GRADE['look']
    except TypeError as e:
        log(f'look {GRADE["look"]} unavailable: {e}')
    log('Cycles OptiX devices: '+', '.join(gpu)+f'; {sc.cycles.samples} samples; denoise; pass6 key {SUN_BEARING}/{SUN_ELEV}')

def main():
    start=time.time()
    from bpy_extras.object_utils import world_to_camera_view
    bpy.ops.wm.read_factory_settings(use_empty=True)
    log('Pass6 hero scene: importing all placed FBX assets (incl. pass-6 dressing + tower cliffs), 2-stud heightmap terrain, source-level water/falls, staged holes with clay-brick curbs')
    for name in L.MATS: L.lglib.get_mat(name)
    terrain(); water(); assets(); look8_mods(); pass4_clouds(); stage_holes(); relight()
    mat=L.lglib.get_mat('Strata');nt=mat.node_tree
    tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(MODELS/'textures/strata_roughness.png'));tex.image.colorspace_settings.name='Non-Color'
    nt.links.new(tex.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Roughness'])
    cam=bpy.data.objects.new('Hero camera',bpy.data.cameras.new('Hero camera')); bpy.context.scene.collection.objects.link(cam); bpy.context.scene.camera=cam
    cam.data.clip_start=.1; cam.data.clip_end=15000
    configure(); sc=bpy.context.scene
    lay={i['piece']:i for i in LAY['instances'] if i['piece'].startswith('gondola')}
    stations=[i['pos'] for i in LAY['instances'] if i['piece']=='gondola_station']
    tower=next(p for p in MAN['pieces'] if p['id']=='gondola_cable')['line']['tower']['centre_world']
    V1_EYE=(60.0,25.5,482.0); V1_TARGET=(80.0,-49.6,-130.0)
    # name, eye, target, horizontal FOV, key (bearing, elevation), rim bearing, output
    shots=[
      ('V1-hub-tee1',V1_EYE,V1_TARGET,78,(SUN_BEARING,SUN_ELEV),RIM['bearing'],OUT/'V1-hub-tee1_look8.png'),
    ]
    rim=next(o for o in sc.objects if o.name.startswith('Orange rim'))
    sun=next(o for o in sc.objects if o.type=='LIGHT' and o.data.type=='SUN' and o is not rim)
    disc=next(o for o in sc.objects if o.name.startswith('Sun disc:'))
    records=[]
    for name,eye,target,fov,(bearing,elevation),rimb,out in shots:
        if SHOTS and name not in SHOTS: continue
        direction=sundir(bearing,elevation)
        sun.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
        rim.rotation_euler=(-sundir(rimb,RIM['elev'])).to_track_quat('-Z','Y').to_euler()
        disc.location=rb(eye)+direction*2500;disc.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
        cam.location=rb(eye); cam.rotation_euler=(rb(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.angle=math.radians(fov)
        sc.render.filepath=str(out.with_name(out.stem+'_draft.png') if PREVIEW else out)
        if PREVIEW: sc.render.filepath=str(OUT/(name+'_look8_draft.png'))
        for obj in sc.objects:
            if obj.instance_type=='COLLECTION' and obj.instance_collection:
                # pass4 world_vista rule: giant far cards read as flat slabs from high aerial views.
                obj.hide_render=bool(obj.get('l8_hidden')) or name=='gondola_span' and obj.instance_collection.name.removeprefix('asset_') in ('distant_mesa_card','butte_spire_card','far_butte_card','far_arch_card','cloud_streak')
        bpy.context.view_layer.update()
        marks={}
        if name=='gondola_span':
            for label,p in (('bottom station',stations[1]),('top station',stations[0]),('support tower',tower),('cabin (boarding)',lay['gondola_cabin']['pos'])):
                v=world_to_camera_view(sc,cam,rb(p)); marks[label]=[round(v.x,4),round(1-v.y,4),round(v.z,1)]
        t=time.time(); log(f'Render start {name} eye={list(eye)} target={list(target)} fov={fov} key={bearing}/{elevation} rim={rimb}/'+str(RIM['elev']))
        bpy.ops.render.render(write_still=True)
        elapsed=time.time()-t; log(f'Render complete {name}: {elapsed:.1f}s -> {sc.render.filepath}')
        records.append({'shot':name,'path':str(Path(sc.render.filepath).relative_to(MODELS)).replace(chr(92),'/'),'samples':sc.cycles.samples,'seconds':round(elapsed,2),'eye':list(map(float,eye)),'target':list(map(float,target)),'fov_horizontal':fov,'key_sun':[bearing,elevation],'rim':[rimb,RIM['elev']],'label_uv':marks})
    report={'engine':'Cycles','device':'OptiX GPU','denoise':True,'resolution':[sc.render.resolution_x,sc.render.resolution_y],'exposure':GRADE['exposure'],'staging':'render-scene-only from holes.json','renders':records}
    report['sky']=SKY; report['key']=KEY; report['rim_light']=RIM; report['curbs']='rounded clay-brick curbs replace the pass-5 candy rails (render-only)'
    (OUT/('look8_draft_report.json' if PREVIEW else 'look8_render_report.json')).write_text(json.dumps(report,indent=2))
    log(f'Pass6 hero run finished in {time.time()-start:.1f}s'+(' (preview)' if PREVIEW else ''))

if __name__=='__main__': main()
