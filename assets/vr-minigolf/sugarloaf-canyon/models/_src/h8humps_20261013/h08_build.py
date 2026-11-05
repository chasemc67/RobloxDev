import bpy, json, os, math, bmesh
from mathutils import Vector, Matrix
D = r'C:\Users\chase\3dmb_sugar_world\h08'
LOG = open(os.path.join(D, 'h08_build.log'), 'w')
def log(*a): LOG.write(' '.join(str(x) for x in a) + '\n'); LOG.flush()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(D, 'h08_ground.fbx'), use_anim=False)
objs = list(bpy.data.objects)
for o in objs: log('OBJ', o.name, o.type, o.parent.name if o.parent else None, tuple(round(v,4) for v in o.location), tuple(round(v,4) for v in o.rotation_euler), tuple(round(v,4) for v in o.scale), [s.material.name for s in o.material_slots if s.material] if o.type=='MESH' else '')
root = [o for o in objs if o.parent is None][0]
G = json.load(open(os.path.join(D, 'h08_geom.json')))
def R2B(p): return Vector((p[0], -p[2], p[1]))   # roblox hole-local -> blender world
def fill(obj, tris, tile):
    inv = obj.matrix_world.inverted()
    me = obj.data; bm = bmesh.new()
    uvl = bm.loops.layers.uv.new('UVMap')
    for t in tris:
        vs = [bm.verts.new(inv @ R2B(p)) for p in t]
        f = bm.faces.new(vs)
        n = (R2B(t[1]) - R2B(t[0])).cross(R2B(t[2]) - R2B(t[0]))
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l, p in zip(f.loops, t):
            w = R2B(p); uv = [w[i] for i in range(3) if i != ax]
            l[uvl].uv = (uv[0] / tile, uv[1] / tile)
    bm.normal_update(); bm.to_mesh(me); bm.free()
    if me.uv_layers: me.uv_layers.active = me.uv_layers[0]
brick = bpy.data.objects['h08_ground__ClayBrick']
log('brick before', len(brick.data.polygons), 'uv layers', [u.name for u in brick.data.uv_layers])
mat = brick.material_slots[0].material
me_old = brick.data
brick.data = bpy.data.meshes.new('h08_ground__ClayBrick')
brick.data.materials.append(mat)
fill(brick, [t for b in G['bricks'] for t in b], 2.0)
log('brick after', len(brick.data.polygons))
COL = {'PepRed': (0xD9/255, 0x34/255, 0x3A/255), 'MintWhite': (1.0, 0xF8/255, 0xF0/255)}
for m, tris in G['trim'].items():
    name = 'h08_ground__' + m
    me = bpy.data.meshes.new(name); ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = root; ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.matrix_world = brick.matrix_world.copy()
    mt = bpy.data.materials.get(m) or bpy.data.materials.new(m)
    mt.use_nodes = True; bsdf = mt.node_tree.nodes.get('Principled BSDF')
    c = COL[m]
    def lin(x): return x/12.92 if x <= 0.04045 else ((x+0.055)/1.055)**2.4
    bsdf.inputs['Base Color'].default_value = (lin(c[0]), lin(c[1]), lin(c[2]), 1); bsdf.inputs['Roughness'].default_value = 0.5
    mt.diffuse_color = (lin(c[0]), lin(c[1]), lin(c[2]), 1)
    me.materials.append(mt)
    fill(ob, tris, 1.0)
    log('trim', name, len(me.polygons))
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
tot = 0
for o in meshes:
    o.data.calc_loop_triangles(); n = len(o.data.loop_triangles); tot += n; log('TRIS', o.name, n)
log('TOTAL', tot)
out = os.path.join(D, 'out'); os.makedirs(out, exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
for o in [root] + meshes: o.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.fbx(filepath=os.path.join(out, 'h08_ground.fbx'), use_selection=True, apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0,
    axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True, add_leaf_bones=False, bake_anim=False,
    mesh_smooth_type="FACE", use_mesh_modifiers=True, object_types={"EMPTY", "MESH"}, use_custom_props=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'h08_ground_src.blend'))
log('EXPORTED')
# ---- previews (render-only staging: felt profile strip + rails from spec), Workbench on CPU-friendly engine
starts = [-8, -18.467, -28.933, -39.4]
def prof(z):
    for s in starts:
        if s - 0.3 <= z <= s: return 0.12 * (s - z) / 0.3
        if s - 0.6 <= z < s - 0.3: return 0.12 * (z - (s - 0.6)) / 0.3
    return 0.0
zs = sorted({round(2 - 0.25 * i, 4) for i in range(0, 241)} | {s for s in starts} | {round(s - .3, 4) for s in starts} | {round(s - .6, 4) for s in starts}, reverse=True)
fm = bpy.data.meshes.new('stage_felt'); bm = bmesh.new()
rows = []
for z in zs:
    hw = 4.0 if z > -44 else 9.0
    rows.append((bm.verts.new(R2B((-hw, prof(z), z))), bm.verts.new(R2B((hw, prof(z), z)))))
for a, b in zip(rows, rows[1:]): bm.faces.new((a[0], a[1], b[1], b[0]))
bm.to_mesh(fm); bm.free()
fo = bpy.data.objects.new('stage_felt', fm); bpy.context.scene.collection.objects.link(fo)
fmat = bpy.data.materials.new('stage_felt'); fmat.diffuse_color = (0.05, 0.35, 0.12, 1); fm.materials.append(fmat)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL'
sc.display.shading.show_shadows = True
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
def shot(fn, eye, tgt, lens=35, ortho=None):
    cam.location = R2B(eye); cam.rotation_euler = (R2B(tgt) - R2B(eye)).to_track_quat('-Z', 'Y').to_euler()
    if ortho: cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho
    else: cam.data.type = 'PERSP'; cam.data.lens = lens
    sc.render.filepath = os.path.join(out, fn); bpy.ops.render.render(write_still=True); log('RENDER', fn)
shot('h08_ground_34.png', (16, 9, 8), (0, 0, -24), 28)
# side profile: ortho from -X looking +X at hump 2 region, vertical exaggeration via scale of whole scene
for o in list(sc.objects):
    if o.type == 'MESH' and o.parent is None: pass
shot('h08_ground_side_full.png', (-30, 0.4, -24), (0, 0.4, -24), ortho=66)
sc.render.resolution_x, sc.render.resolution_y = 1600, 600
shot('h08_ground_side_hump2.png', (-30, 0.3, -18.77), (0, 0.3, -18.77), ortho=3.0)
log('DONE')
LOG.close()
