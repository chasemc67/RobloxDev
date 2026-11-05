# Blender 5.2 headless: parts.json -> one FBX per landmark (root empty at the anchor base centre, one mesh per material),
# triangles.json for the fitcheck, Cycles CPU previews (34 / eye / front). Run: blender -b -P build_batch3.py -- <dir>
import bpy, bmesh, json, math, sys, os
from mathutils import Vector
OUT = sys.argv[sys.argv.index('--')+1]
PARTS = json.load(open(os.path.join(OUT, 'parts.json')))
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene; sc.unit_settings.system = 'NONE'
PAL = {'Timber': ('#8A5A33', 'WoodPlanks'), 'Iron': ('#3B3A3F', 'Metal'), 'PepRed': ('#D9343A', 'SmoothPlastic'),
       'MintWhite': ('#FFF8F0', 'SmoothPlastic'), 'Bubblegum': ('#F78FB3', 'SmoothPlastic'), 'Window': ('#9FD8E8', 'Glass'),
       'Watermelon': ('#E8736B', 'Sandstone'), 'CreamTaffy': ('#F6E3C8', 'Sandstone'), 'GeodeRim': ('#C8463F', 'Rock'),
       'CrystalGlow': ('#FF6FA8', 'Neon'), 'Brass': ('#C9973A', 'Metal'), 'Rope': ('#C9A86A', 'Fabric'), 'Cherry': ('#E8304A', 'SmoothPlastic'), 'Lime': ('#7ED957', 'SmoothPlastic'), 'Water': ('#3FD0C9', 'Glass'), 'Brick': ('#A8483A', 'Brick'), 'Sugar': ('#FFF1F4', 'Sand')}
def lin(hx):
    c = [int(hx[i:i+2], 16)/255 for i in (1, 3, 5)]; return [((x+0.055)/1.055)**2.4 if x > 0.04045 else x/12.92 for x in c] + [1]
MATS = {}
def mat(k):
    if k not in MATS:
        m = bpy.data.materials.new(k); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = lin(PAL[k][0]); m.diffuse_color = lin(PAL[k][0])
        b.inputs['Roughness'].default_value = 0.35 if k in ('Iron', 'Brass', 'Window') else 0.8
        b.inputs['Metallic'].default_value = 0.8 if k in ('Iron', 'Brass') else 0.0
        if k == 'CrystalGlow':
            b.inputs['Emission Color'].default_value = lin(PAL[k][0]); b.inputs['Emission Strength'].default_value = 2.0
        MATS[k] = m
    return MATS[k]
B = lambda p: Vector((p[0], -p[2], p[1]))
REP = {'parts': []}; TRI = {}; ROOTS = {}
FBX = os.path.join(OUT, 'fbx'); PV = os.path.join(OUT, 'previews'); os.makedirs(FBX, exist_ok=True); os.makedirs(PV, exist_ok=True)
for P in PARTS:
    root = bpy.data.objects.new(P['id'], None); sc.collection.objects.link(root); objs = []; meshes = []; tris_all = []
    for mk, g in sorted(P['groups'].items()):
        me = bpy.data.meshes.new(P['id'] + '__' + mk); me.from_pydata([B(v) for v in g['verts']], [], [tuple(f) for f in g['faces']]); me.validate(); me.update()
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
        me.materials.append(mat(mk)); o = bpy.data.objects.new(me.name, me); sc.collection.objects.link(o); o.parent = root; objs.append(o)
        me.calc_loop_triangles(); t = len(me.loop_triangles)
        meshes.append({'mesh': o.name, 'material': mk, 'color': PAL[mk][0], 'roblox_material': PAL[mk][1], 'tris': t})
        for lt in me.loop_triangles: tris_all.append([[me.vertices[i].co.x, me.vertices[i].co.z, -me.vertices[i].co.y] for i in lt.vertices])
    TRI[P['id']] = tris_all; ROOTS[P['id']] = (root, objs)
    for ob in sc.objects: ob.select_set(False)
    root.select_set(True); [o.select_set(True) for o in objs]; bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(filepath=os.path.join(FBX, P['id'] + '.fbx'), use_selection=True, object_types={'EMPTY', 'MESH'}, axis_forward='-Z', axis_up='Y',
        global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', path_mode='COPY', embed_textures=True, mesh_smooth_type='FACE', add_leaf_bones=False)
    REP['parts'].append(dict(id=P['id'], hole=P['hole'], fbx='fbx/props_batch4/' + P['id'] + '.fbx', anchor_local=P['anchor'], envelope=P['envelope'],
        tris=sum(m['tris'] for m in meshes), max_mesh_tris=max(m['tris'] for m in meshes), meshes=meshes, notes=P['notes']))
json.dump(REP, open(os.path.join(OUT, 'build_report.json'), 'w'), indent=1); json.dump(TRI, open(os.path.join(OUT, 'triangles.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'props_batch4.blend'))
print('EXPORTED', [(r['id'], r['tris'], r['max_mesh_tris']) for r in REP['parts']], flush=True)
# previews: Cycles CPU
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 48; sc.cycles.use_denoising = True; sc.view_settings.view_transform = 'Standard'
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.95, 0.75, 0.65, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = 3.5; sun.rotation_euler = (math.radians(50), 0, math.radians(-60)); sc.collection.objects.link(sun)
gm = bpy.data.meshes.new('g'); gm.from_pydata([(-80,-80,0),(80,-80,0),(80,80,0),(-80,80,0)], [], [(0,1,2,3)])
gmt = bpy.data.materials.new('sand'); gmt.use_nodes = True; gmt.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = lin('#D88E5C'); gm.materials.append(gmt)
ground = bpy.data.objects.new('ground', gm); sc.collection.objects.link(ground)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 1280, 960
for pid, (root, objs) in ROOTS.items():
    for q, (r2, o2) in ROOTS.items():
        for o in o2: o.hide_render = (q != pid)
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)]); c = (lo + hi)/2; size = (hi - lo).length
    for view in ('34', 'eye', 'front'):
        if view == '34': cam.data.type = 'PERSP'; cam.data.lens = 40; eye = c + Vector((1.0, -1.3, 0.7)).normalized()*size*1.5
        elif view == 'eye': cam.data.type = 'PERSP'; cam.data.lens = 30; eye = Vector((c.x + size*0.3, lo.y - max(size*0.9, 8), 5.0)); 
        else: cam.data.type = 'ORTHO'; cam.data.ortho_scale = max(hi.x - lo.x, hi.z - lo.z)*1.2; eye = Vector((c.x, lo.y - 60, c.z))
        tgt = c if view != 'eye' else Vector((c.x, c.y, min(c.z, 6.0)))
        cam.location = eye; cam.rotation_euler = (tgt - eye).to_track_quat('-Z', 'Y').to_euler(); cam.data.clip_end = 1000
        sc.render.filepath = os.path.join(PV, f'{pid}_{view}.png'); bpy.ops.render.render(write_still=True); print('R', pid, view, flush=True)
print('DONE_ALL', flush=True)
