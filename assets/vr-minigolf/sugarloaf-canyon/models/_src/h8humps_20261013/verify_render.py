import bpy, json, os, math, bmesh
from mathutils import Vector, Matrix
D = r'C:\Users\chase\3dmb_sugar_world\h08'
LOG = open(os.path.join(D, 'verify.log'), 'w')
def log(*a): LOG.write(' '.join(str(x) for x in a) + '\n'); LOG.flush()
def B2R(v): return [v[0], v[2], -v[1]]
def R2B(p): return Vector((p[0], -p[2], p[1]))
def dump(fbx, tag):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx, use_anim=False)
    res = {}
    for o in bpy.data.objects:
        log(tag, 'OBJ', o.name, o.type, o.parent.name if o.parent else None, tuple(round(x,4) for x in o.matrix_world.translation), [s.material.name for s in o.material_slots if s.material] if o.type=='MESH' else '')
        if o.type != 'MESH': continue
        me = o.data; me.calc_loop_triangles(); M = o.matrix_world
        res[o.name] = [[B2R(M @ me.vertices[i].co) for i in t.vertices] for t in me.loop_triangles]
    json.dump(res, open(os.path.join(D, 'out', tag + '_tris.json'), 'w'))
    return res
dump(os.path.join(D, 'h15_sugar_dune.fbx'), 'h15')
S = json.load(open(os.path.join(D, 'h15_stage.json'))); A = S['anchor']
for r in [o for o in bpy.data.objects if o.parent is None]: r.location = R2B(A)   # pivot = anchor
def ry(p, d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a); return [p[0]*c + p[2]*s, p[1], -p[0]*s + p[2]*c]
def box(name, c, size, yaw, col):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    hx, hy, hz = [x/2 for x in size]
    vs = [bm.verts.new(R2B([a+b for a, b in zip(ry(p, yaw), c)])) for p in [[-hx,-hy,-hz],[hx,-hy,-hz],[hx,-hy,hz],[-hx,-hy,hz],[-hx,hy,-hz],[hx,hy,-hz],[hx,hy,hz],[-hx,hy,hz]]]
    for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]: bm.faces.new([vs[i] for i in f])
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    m = bpy.data.materials.new(name); m.diffuse_color = col; me.materials.append(m); return o
for w in S['walls']:
    box('rail_' + w['id'], w['center'], w['size'], w.get('yaw', 0), (0.95, 0.75, 0.1, 1) if w['id'] == 'dune_lean3' else (0.35, 0.22, 0.12, 1))
for f in []:
    o = box('felt_' + f['id'], f['center'], [f['size'][0], 0.05, f['size'][1]], f.get('yaw', 0), (0.05, 0.35, 0.12, 1))
    if f.get('slope'):
        s = f['slope']; ang = math.atan2(s['rise'], f['size'][0] if s['axis'] == 'x' else f['size'][1])
        # tilt about the felt's local axis (render-only approximation)
        o.data.transform(Matrix.Translation(-R2B(f['center'])))
        rot = Matrix.Rotation(-math.radians(f.get('yaw', 0)), 4, 'Z')
        tilt = Matrix.Rotation(ang if s['axis'] == 'x' else -ang, 4, 'Y' if s['axis'] == 'x' else 'X')
        o.data.transform(rot.inverted() @ tilt @ rot) if False else o.data.transform(Matrix.Rotation(math.radians(f.get('yaw',0)),4,'Z') @ tilt @ Matrix.Rotation(-math.radians(f.get('yaw',0)),4,'Z'))
        o.data.transform(Matrix.Translation(R2B(f['center'])))
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL'; sc.display.shading.show_shadows = True
sc.render.resolution_x, sc.render.resolution_y = 1400, 1400
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
def shot(fn, eye, tgt, lens=35, ortho=None):
    cam.location = R2B(eye); cam.rotation_euler = (R2B(tgt) - R2B(eye)).to_track_quat('-Z', 'Y').to_euler()
    if ortho: cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho
    else: cam.data.type = 'PERSP'; cam.data.lens = lens
    cam.data.clip_end = 1000
    sc.render.filepath = os.path.join(D, 'out', fn); bpy.ops.render.render(write_still=True); log('RENDER', fn)
cam.location=R2B((0,60,-24)); cam.rotation_euler=(0,0,0); cam.data.type='ORTHO'; cam.data.ortho_scale=44; cam.data.clip_end=1000; sc.render.filepath=os.path.join(D,'out','h15_sugar_dune_top.png'); bpy.ops.render.render(write_still=True); log('RENDER top')
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
shot('h15_sugar_dune_34.png', (26, 14, -2), (4, -2.5, -26), 28)
log('DONE'); LOG.close()
