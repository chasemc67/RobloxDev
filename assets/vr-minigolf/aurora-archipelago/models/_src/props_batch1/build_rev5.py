"""Blender 5.2 only: parts -> FBX, actual triangles, manifest, CPU context previews."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
S=Path(__file__).resolve().parent;D=S.parents[2]
P=json.loads((S/'parts.json').read_text());PAL=json.loads((S/'palette.json').read_text())
H={h['number']:h for h in json.loads((D/'holes.json').read_text())['holes']}
FBX=D/'models/fbx/props_batch1';PV=D/'models/previews/props_batch1'
FBX.mkdir(parents=True,exist_ok=True);PV.mkdir(parents=True,exist_ok=True)
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
sc=bpy.context.scene;sc.unit_settings.system='NONE'
def B(p):return Vector((p[0],-p[2],p[1]))
def lin(h):
    rgb=[int(h[i:i+2],16)/255 for i in [1,3,5]];return [v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]+[1]
def mat(k):
    m=bpy.data.materials.get(k)
    if m:return m
    m=bpy.data.materials.new(k);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];color,rbx,emission,alpha,_=PAL[k]
    b.inputs['Base Color'].default_value=lin(color);m.diffuse_color=lin(color);b.inputs['Roughness'].default_value=.25 if k in ['Brass','Ice'] else .72
    b.inputs['Metallic'].default_value=.6 if k=='Brass' else 0
    if emission:b.inputs['Emission Color'].default_value=lin(color);b.inputs['Emission Strength'].default_value=emission*.45
    if k=='Ice':b.inputs['Transmission Weight'].default_value=.3;b.inputs['IOR'].default_value=1.31
    return m
def mesh(name,g,m):
    me=bpy.data.meshes.new(name);me.from_pydata([B(v) for v in g['verts']],[],g['faces']);me.validate();me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();me.materials.append(mat(m))
    o=bpy.data.objects.new(name,me);sc.collection.objects.link(o);return o
CHANGED=set(json.loads((S/'rev5_ids.json').read_text())); OLD=json.loads((D/'models/props_batch1_manifest.json').read_text()); OLDREP={p['id']:p for p in OLD['parts']}; ROOTS={};TRI={};rep=[]
for p in P:
    root=bpy.data.objects.new(p['id'],None);sc.collection.objects.link(root);objs=[];ms=[];ts=[]
    for k,g in p['groups'].items():
        o=mesh(p['id']+'__'+k,g,k);o.parent=root;objs.append(o);o.data.calc_loop_triangles()
        ms.append(dict(mesh=o.name,material=k,colour=PAL[k][0],color=PAL[k][0],roblox_material=PAL[k][1],transparency=PAL[k][3],tris=len(o.data.loop_triangles)))
        for t in o.data.loop_triangles:ts.append([[o.data.vertices[i].co.x,o.data.vertices[i].co.z,-o.data.vertices[i].co.y] for i in t.vertices])
    TRI[p['id']]=ts
    for o in sc.objects:o.select_set(False)
    root.select_set(True)
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    if p['id'] in CHANGED:
        bpy.ops.export_scene.fbx(filepath=str(FBX/(p['id']+'.fbx')),use_selection=True,object_types={'EMPTY','MESH'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',path_mode='COPY',embed_textures=True,mesh_smooth_type='FACE',add_leaf_bones=False)
    h=H[p['hole']];a=p['anchor'];ang=math.radians(h['world_yaw']);off=h['world_offset'];world=[a[0]*math.cos(ang)+a[2]*math.sin(ang)+off[0],a[1]+off[1],-a[0]*math.sin(ang)+a[2]*math.cos(ang)+off[2]]
    r=dict(id=p['id'],hole=p['hole'],fbx='fbx/props_batch1/'+p['id']+'.fbx',tris=sum(m['tris'] for m in ms),max_mesh_tris=max(m['tris'] for m in ms),meshes=ms,pivot_hole_local=a,anchor_local=a,yaw_local=p['yaw_local'],world_offset=off,world_yaw=h['world_yaw'],pivot_world=world,placement_yaw=h['world_yaw']+p['yaw_local'],motion=p['motion'],notes=p['notes'],can_collide=False)
    vs=[v for g in p['groups'].values() for v in g['verts']];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
    r['bbox_asset_local']=[lo,hi];r['bbox_hole_local']=[[lo[i]+a[i] for i in range(3)],[hi[i]+a[i] for i in range(3)]];r['bbox']=r['bbox_asset_local'];r['dimensions']=[hi[i]-lo[i] for i in range(3)]
    r['lights']=[]
    if p['id'] in ['h01_harbour_lantern','h02_lantern_cue']:
        r['lights']=[dict(type='PointLight',colour='#FFB861',range=14,brightness=.8,position_asset_local=([-.65,8.14,0] if p['hole']==1 else [0,.54,0]))]
    if p['id']=='h05_signal_lamp':r['runtime_signal']=dict(controller='geyser_lift',flush_colour='#5CFFB0',moving_colour='#FFB861',lens_material='AuroraMint')
    if p['id']=='h05_steamwhistle_geyser':r['runtime_effect']=dict(type='steam_puff',height=60,period_seconds=20,collision=False,origin_asset_local=[0,7,0])
    rep.append(r if p['id'] in CHANGED else OLDREP[p['id']]);ROOTS[p['id']]=(root,objs);root.location=B(a)
(S/'triangles.json').write_text(json.dumps(TRI));(S/'build_report.json').write_text(json.dumps(dict(blender_version=bpy.app.version_string,parts=rep),indent=2))
(D/'models/props_batch1_manifest.json').write_text(json.dumps(dict(course='aurora-archipelago',batch=1,parts=rep,skipped=json.loads((S/'skipped.json').read_text()),axes=dict(forward='-Z',up='Y',scale=1)),indent=2))
# Exact source blockout context (felt, slopes, rails) in each hole's local frame.
CONTEXT={}
def context_box(n,name,c,size,yaw,k,slope=None):
    sx,sy,sz=[v/2 for v in size];vs=[]
    for x,y,z in [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,-sy,sz),(-sx,-sy,sz),(-sx,sy,-sz),(sx,sy,-sz),(sx,sy,sz),(-sx,sy,sz)]:
        if slope:y+=(x/size[0] if slope['axis']=='x' else z/size[2])*slope['rise']
        an=math.radians(yaw);vs.append([c[0]+x*math.cos(an)+z*math.sin(an),c[1]+y,c[2]-x*math.sin(an)+z*math.cos(an)])
    o=mesh(name,dict(verts=vs,faces=[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]]),k);CONTEXT.setdefault(n,[]).append(o)
for n in [1,2,3,5,7,8]:
    for f in H[n]['felt']:context_box(n,'context_h%02d_'%n+f['id'],[f['center'][0],f['center'][1]-.2,f['center'][2]],[f['size'][0],.4,f['size'][1]],f.get('yaw',0),'Felt',f.get('slope'))
    for w in H[n]['walls']:context_box(n,'context_h%02d_'%n+w['id'],w['center'],w['size'],w.get('yaw',0),'SnowShadow' if n==2 else 'Timber')
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=12;sc.cycles.use_denoising=True
sc.render.resolution_x=1280;sc.render.resolution_y=960;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('Aurora twilight');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.16,.32,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sun=bpy.data.objects.new('Moon',bpy.data.lights.new('Moon','SUN'));sc.collection.objects.link(sun);sun.data.energy=2;sun.rotation_euler=(math.radians(35),math.radians(-20),math.radians(-35))
area=bpy.data.objects.new('Soft key',bpy.data.lights.new('Soft key','AREA'));sc.collection.objects.link(area);area.data.energy=2200;area.data.shape='DISK';area.data.size=40;area.location=(0,30,55)
cam=bpy.data.objects.new('Preview camera',bpy.data.cameras.new('Preview camera'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=1000
def render(path,objs):
    bpy.context.view_layer.update();pts=[o.matrix_world@Vector(v) for o in objs for v in o.bound_box];lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)]);center=(lo+hi)/2
    cam.location=center+Vector((.8,-1.3,1.2)).normalized()*150;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
    # Fit in camera coordinates with 15% margin.
    inv=cam.matrix_world.inverted();cs=[inv@v for v in pts];ww=max(v.x for v in cs)-min(v.x for v in cs);hh=max(v.y for v in cs)-min(v.y for v in cs);cam.data.ortho_scale=max(ww,hh*1280/960)*1.16
    sc.render.filepath=str(path);bpy.ops.render.render(write_still=True);print('RENDERED',path.name,flush=True)
allmesh=[o for o in sc.objects if o.type=='MESH']
for n in [7,8]:
    visible=CONTEXT[n]+[o for p in P if p['hole']==n for o in ROOTS[p['id']][1]]
    for o in allmesh:o.hide_render=o not in visible
    render(PV/f'h{n:02d}_34.png',visible)
for p in P:
    if p['id'] not in CHANGED:continue
    visible=ROOTS[p['id']][1]
    for o in allmesh:o.hide_render=o not in visible
    render(PV/(p['id']+'_34.png'),visible)

for id in ['h07_coral_w2','h08_coral_1']:
    p=next(p for p in P if p['id']==id);visible=ROOTS[id][1]
    for o in allmesh:o.hide_render=o not in visible
    # Undo skin yaw only for a local front view; camera follows rotated front.
    a=B(p['anchor']);ang=math.radians(next(w['yaw'] for w in H[8]['walls'] if w['id']==p['skin_ids'][0]) if p['skin_ids'] else 0);direction=Vector((math.sin(ang),-math.cos(ang),0))
    center=a+Vector((0,0,3 if p['hole']==7 else 2));cam.location=center+direction*100
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=8
    sc.render.resolution_x=800;sc.render.resolution_y=800;sc.render.film_transparent=True
    sc.render.filepath=str(PV/(id+'_front.png'));bpy.ops.render.render(write_still=True)
for o in allmesh:o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(S/'props_batch1_rev5.blend'))
print('DONE_ALL',flush=True)
