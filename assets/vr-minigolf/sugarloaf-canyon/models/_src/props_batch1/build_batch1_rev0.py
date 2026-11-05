# Sugarloaf batch 1 final props: timing meshes + flag. Blender 5.2 headless.
# Geometry authored in Roblox hole-local coords RELATIVE TO EACH PIVOT (pivot = origin).
import bpy, bmesh, json, math, sys, os
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index('--')+1:]
OUT = argv[0]; RENDER = '--norender' not in argv
FBX = os.path.join(OUT, 'fbx'); PV = os.path.join(OUT, 'previews'); os.makedirs(FBX, exist_ok=True); os.makedirs(PV, exist_ok=True)
sc = bpy.context.scene; sc.unit_settings.system = 'NONE'
for _o in list(bpy.data.objects): bpy.data.objects.remove(_o, do_unlink=True)

PAL = {'Timber': ('#8A5A33', 'WoodPlanks'), 'Iron': ('#3B3A3F', 'Metal'), 'PepRed': ('#D9343A', 'SmoothPlastic'),
       'MintWhite': ('#FFF8F0', 'SmoothPlastic'), 'Bubblegum': ('#F78FB3', 'SmoothPlastic'), 'Slate': ('#5E5A66', 'Slate'),
       'FlagRed': ('#E03C31', 'Fabric'), 'Brass': ('#FFD36B', 'Metal')}
def srgb(hx):
    c = [int(hx[i:i+2], 16)/255 for i in (1, 3, 5)]
    return [((x+0.055)/1.055)**2.4 if x > 0.04045 else x/12.92 for x in c] + [1]
MATS = {}
def mat(k):
    if k not in MATS:
        m = bpy.data.materials.new(k); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = srgb(PAL[k][0]); m.diffuse_color = srgb(PAL[k][0])
        b.inputs['Roughness'].default_value = 0.35 if k in ('Iron', 'Brass') else 0.75
        b.inputs['Metallic'].default_value = 0.8 if k in ('Iron', 'Brass') else 0.0
        MATS[k] = m
    return MATS[k]
def B(p): return Vector((p[0], -p[2], p[1]))  # Roblox -> Blender
def roty(p, d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a); return [p[0]*c + p[2]*s, p[1], -p[0]*s + p[2]*c]
def rot(p, axis, d): return list(Matrix.Rotation(math.radians(d), 3, Vector(axis)) @ Vector(p))

class Part:
    def __init__(s, name): s.name = name; s.g = {}
    def add(s, matk, verts, faces):
        v, f = s.g.setdefault(matk, ([], [])); o = len(v); v += [list(p) for p in verts]; f += [tuple(i+o for i in fc) for fc in faces]
    def box(s, matk, c, size, yaw=0, post=None):
        hx, hy, hz = [x/2 for x in size]
        vs = [[-hx,-hy,-hz],[hx,-hy,-hz],[hx,-hy,hz],[-hx,-hy,hz],[-hx,hy,-hz],[hx,hy,-hz],[hx,hy,hz],[-hx,hy,hz]]
        vs = [roty(p, yaw) for p in vs]; vs = [[p[i]+c[i] for i in range(3)] for p in vs]
        if post: vs = [post(p) for p in vs]
        s.add(matk, vs, [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
    def prism(s, matk, poly, y0, y1, plane='xz', post=None):
        # extrude polygon; plane 'xz' -> poly in (x,z), extruded along y; 'xy' -> poly in (x,y), extruded along z (y0..y1 are z)
        n = len(poly); vs = []
        for t in (y0, y1):
            for (a, b) in poly: vs.append([a, t, b] if plane == 'xz' else [a, b, t])
        if post: vs = [post(p) for p in vs]
        f = [tuple(range(n-1, -1, -1)), tuple(range(n, 2*n))] + [(i, (i+1) % n, n+(i+1) % n, n+i) for i in range(n)]
        s.add(matk, vs, f)
    def cyl(s, matk, c, r, y0, y1, n=12, axis='y', post=None):
        poly = [(r*math.cos(2*math.pi*i/n), r*math.sin(2*math.pi*i/n)) for i in range(n)]
        if axis == 'y': s.prism(matk, [(c[0]+a, c[2]+b) for a, b in poly], y0, y1, 'xz', post)
        else: s.prism(matk, [(c[0]+a, c[1]+b) for a, b in poly], y0, y1, 'xy', post)

PARTS = []
# ---------- H6 sluice gate: pivot bottom centre [0,0,-28], slides on +x. Board 7 x 1.0 x 0.6, 45-deg points.
p = Part('h06_sluice_gate')
hull = [(-3.5, 0), (-3.2, -0.3), (3.2, -0.3), (3.5, 0), (3.2, 0.3), (-3.2, 0.3)]
inset = [(-3.48, 0), (-3.2, -0.28), (3.2, -0.28), (3.48, 0), (3.2, 0.28), (-3.2, 0.28)]
p.prism('Timber', inset, 0.0, 0.9, 'xz')                     # timber board body (inside the hull by .02)
for i, (y0, y1) in enumerate([(0.9, 0.95), (0.95, 1.0)]):   # red/cream striped top cap = full hull
    pass
# striped cap along x: 0.5-stud bands, full hull profile, y .9..1.0
edges = [-3.5, -3.2] + [-3.2 + 0.5*k for k in range(1, 13)] + [3.2, 3.5]
edges = sorted(set(round(e, 4) for e in edges))
def hull_w(x): return 0.3 if abs(x) <= 3.2 else max(0.0, 0.3 - (abs(x) - 3.2))
for k in range(len(edges)-1):
    a, b = edges[k], edges[k+1]
    poly = [(a, -hull_w(a)), (b, -hull_w(b)), (b, hull_w(b)), (a, hull_w(a))]
    if hull_w(a) == 0: poly = [(a, 0), (b, -hull_w(b)), (b, hull_w(b))]
    if hull_w(b) == 0: poly = [(a, -hull_w(a)), (b, 0), (a, hull_w(a))]
    p.prism('PepRed' if k % 2 == 0 else 'MintWhite', poly, 0.9, 1.0, 'xz')
for x in (-2.4, -0.8, 0.8, 2.4):                               # iron straps on both faces, inside the 0.6 hull
    p.box('Iron', [x, 0.45, -0.29], [0.18, 0.9, 0.02]); p.box('Iron', [x, 0.45, 0.29], [0.18, 0.9, 0.02])
PARTS.append((p, {'hole': 'h06', 'pivot_local': [0, 0.0, -28.0], 'motion': 'slide x, range [-7,0], see holes.json h06.sluice_gate'}))

# ---------- H9 windpump rotor: pivot hub [0,4.12,-17.75], axis +z. 4 lollipop vanes 2.4 wide, r .6..4.1, depth .4.
p = Part('h09_windpump_rotor')
R_TIP = 4.1; N = 16
def vane_poly():
    xs = [-1.2 + 2.4*i/N for i in range(N+1)]
    bottom = [(x, -math.sqrt(R_TIP**2 - x*x)) for x in xs]           # circular clipped tip
    return bottom + [(1.2, -0.6), (-1.2, -0.6)]
for k, roll in enumerate((0, 90, 180, 270)):
    post = (lambda r: (lambda q: rot(q, [0, 0, 1], r)))(roll)
    poly = vane_poly()
    p.prism('PepRed' if k % 2 == 0 else 'MintWhite', poly, -0.19, 0.19, 'xy', post)  # bands fill .19..2 each face
    # bubblegum swirl band: thin ring sector on both faces (inside the .4 depth: faces at +-.2, band .19..2)
    ring = [(x*0.62, y*0.62) for (x, y) in poly[:N+1]]
    band = poly[2:N-1]; band_in = [(x*0.9, y*0.9) for (x, y) in band]
    pb = [(x, y) for (x, y) in band] + list(reversed(band_in))
    p.prism('Bubblegum' if k % 2 == 0 else 'PepRed', pb, 0.19, 0.2, 'xy', post)
    p.prism('Bubblegum' if k % 2 == 0 else 'PepRed', pb, -0.2, -0.19, 'xy', post)
p.cyl('Iron', [0, 0, 0], 0.6, -0.2, 0.2, 16, axis='z')  # hub; vane roots overlap it              # hub disc inside the vane depth
p.cyl('Brass', [0, 0, 0], 0.25, 0.2, 0.2001, 12, axis='z') if False else None
PARTS.append((p, {'hole': 'h09', 'pivot_local': [0, 4.12, -17.75], 'motion': 'rotate about +z at 20 deg/s, continuous (18 s period)'}))

# ---------- H11 lock gate: single flat leaf 3.6 x 1.2 x 0.5, pivot [0,0,-21.25], collider centre y .6, slides on y [-1.3,0].
p = Part('h11_lock_gate')
p.box('Timber', [0, 0.6, 0], [3.56, 1.2, 0.46])                 # body, top flush y 1.2 (gate_top felt)
for x in (-1.2, 0.0, 1.2):
    p.box('Iron', [x, 0.6, -0.24], [0.16, 1.16, 0.02]); p.box('Iron', [x, 0.6, 0.24], [0.16, 1.16, 0.02])
for i in range(6):                                             # red/cream striped end posts (0.02 each end)
    y0 = i*0.2; m = 'PepRed' if i % 2 == 0 else 'MintWhite'
    p.box(m, [-1.79, y0+0.1, 0], [0.02, 0.2, 0.5]); p.box(m, [1.79, y0+0.1, 0], [0.02, 0.2, 0.5])
PARTS.append((p, {'hole': 'h11', 'pivot_local': [0, 0.0, -21.25], 'motion': 'slide y, range [-1.3,0] (single flat leaf per Game Art Bot)'}))

# ---------- H14 ore bucket: hinge [0,10.35,-24], axis +z, swing +-9. Bucket box 2.1x2x1.8 at y -9; skid follows holes.json foot strips.
HJ = json.load(open(os.path.join(OUT, 'holes.json')))
H14 = next(h for h in HJ['holes'] if h['id'] == 'h14'); ob = next(m for m in H14['moving_parts'] if m['id'] == 'ore_bucket')
p = Part('h14_ore_bucket')
# tapered bucket inside the exact 2.1x2x1.8 collider: top 2.1x1.8, bottom 1.9x1.6
top, bot = (1.05, 0.9), (0.95, 0.8)
vs = [[-bot[0], -10, -bot[1]], [bot[0], -10, -bot[1]], [bot[0], -10, bot[1]], [-bot[0], -10, bot[1]],
      [-top[0], -8.15, -top[1]], [top[0], -8.15, -top[1]], [top[0], -8.15, top[1]], [-top[0], -8.15, top[1]]]
p.add('Iron', vs, [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
for i, (y0, y1) in enumerate([(-8.15, -8.075), (-8.075, -8.0)]):   # red/cream rim band (full collider footprint)
    p.box('PepRed' if i == 0 else 'MintWhite', [0, (y0+y1)/2, 0], [2.1, y1-y0, 1.8])
p.box('Timber', [0, -8.6, 0], [2.0, 0.3, 1.72])                   # ore load visible inside rim? (inside taper)
# skid plate: rocker through holes.json foot-strip bottoms (chords lie above the strips -> never lower than collider)
strips = [b for b in ob['blockers'] if abs(b['center'][1] + 9.0) > 0.5]
pts = sorted([(b['center'][0], b['center'][1] - b['size'][1]/2) for b in strips])
x0 = pts[0][0] - 0.075; x1 = pts[-1][0] + 0.075
# vertices at strip edges, each at the HIGHER of the two neighbouring strip bottoms -> the skid never dips below any strip
prof = [(x0, pts[0][1])] + [((pts[i][0] + pts[i+1][0]) / 2, max(pts[i][1], pts[i+1][1])) for i in range(len(pts)-1)] + [(x1, pts[-1][1])]
prof = [(x, y + 0.001) for x, y in prof]
poly = prof + [(x1, -10.0), (x0, -10.0)]
p.prism('Timber', list(reversed(poly)), -0.075, 0.075, 'xy')
# hanger: 9-stud bail from hinge down to the bucket rim
p.cyl('Iron', [0, 0, 0], 0.08, -8.0, 0.0, 8, 'y')
p.box('Iron', [0, -7.95, 0], [2.0, 0.1, 0.12])
p.cyl('Brass', [0, 0, 0], 0.2, -0.2, 0.2, 12, axis='z')            # hinge boss at the pivot
PARTS.append((p, {'hole': 'h14', 'pivot_local': [0.0, 10.35, -24.0], 'motion': 'swing about +z, amplitude 9 deg, period 4 s, sinusoidal'}))

# ---------- H17 shadow arms: pivot [0,0,-36], axis +y, 12 deg/s. 4 slate bars r 8.2..11.5, 3.6 thick, 0.9 tall.
p = Part('h17_shadow_arms')
for yaw in (0, 90, 180, 270):
    post = (lambda r: (lambda q: roty(q, r)))(yaw)
    # bevelled slate bar inside the 3.3x0.9x3.6 box at x 9.85
    lo = [(8.2, -1.8), (11.5, -1.8), (11.5, 1.8), (8.2, 1.8)]
    hi = [(8.28, -1.72), (11.42, -1.72), (11.42, 1.72), (8.28, 1.72)]
    vs = [[a, 0.0, b] for a, b in lo] + [[a, 0.8, b] for a, b in lo] + [[a, 0.88, b] for a, b in hi]
    vs = [post(q) for q in vs]
    f = [(3,2,1,0), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7), (4,5,9,8), (5,6,10,9), (6,7,11,10), (7,4,8,11), (8,9,10,11)]
    p.add('Slate', vs, f)
    # cream sun-line inlay on the top (inside box, y .88..0.9)
    p.add('MintWhite', [post([a, y, b]) for y in (0.88, 0.9) for (a, b) in [(8.5, -0.15), (11.2, -0.15), (11.2, 0.15), (8.5, 0.15)]],
          [(3,2,1,0), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)])
PARTS.append((p, {'hole': 'h17', 'pivot_local': [0.0, 0.0, -36.0], 'motion': 'rotate about +y at 12 deg/s, continuous'}))

# ---------- Flag (all holes): pole 7.5 high, dia .15; banner 2 x 1.2 x .05 #e03c31 at the top. Pivot = pole base at the cup.
p = Part('flag')
p.cyl('MintWhite', [0, 0, 0], 0.075, 0.0, 7.5, 10, 'y')
p.box('FlagRed', [1.0 + 0.075, 6.9, 0], [2.0 - 0.0, 1.2, 0.05])
PARTS.append((p, {'hole': 'all', 'pivot_local': 'cup.flag base (cup position)', 'motion': 'static, visual only, no collision'}))

# ---------- build objects, export
REP = {'parts': []}
def build(p):
    root = bpy.data.objects.new(p.name, None); sc.collection.objects.link(root); objs = []
    for mk, (v, f) in sorted(p.g.items()):
        me = bpy.data.meshes.new(p.name + '__' + mk); me.from_pydata([B(q) for q in v], [], f); me.validate(); me.update()
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
        me.materials.append(mat(mk)); o = bpy.data.objects.new(p.name + '__' + mk, me); sc.collection.objects.link(o); o.parent = root; objs.append(o)
    return root, objs
TRI = {}
for p, meta in PARTS:
    root, objs = build(p); meshes = []; alltris = []
    for o in objs:
        me = o.data; me.calc_loop_triangles(); t = len(me.loop_triangles)
        meshes.append({'mesh': o.name, 'material': o.name.split('__')[1], 'color': PAL[o.name.split('__')[1]][0], 'roblox_material': PAL[o.name.split('__')[1]][1], 'tris': t})
        for lt in me.loop_triangles:
            alltris.append([[me.vertices[i].co.x, me.vertices[i].co.z, -me.vertices[i].co.y] for i in lt.vertices])  # back to Roblox local
    TRI[p.name] = alltris
    for ob in sc.objects: ob.select_set(False)
    root.select_set(True); [o.select_set(True) for o in objs]; bpy.context.view_layer.objects.active = root
    fp = os.path.join(FBX, p.name + '.fbx')
    bpy.ops.export_scene.fbx(filepath=fp, use_selection=True, object_types={'EMPTY', 'MESH'}, axis_forward='-Z', axis_up='Y', global_scale=1.0,
        apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', path_mode='COPY', embed_textures=True, mesh_smooth_type='FACE', add_leaf_bones=False)
    REP['parts'].append(dict(id=p.name, fbx='fbx/' + p.name + '.fbx', tris=sum(m['tris'] for m in meshes), max_mesh_tris=max(m['tris'] for m in meshes), meshes=meshes, **meta))
json.dump(REP, open(os.path.join(OUT, 'build_report.json'), 'w'), indent=1)
json.dump(TRI, open(os.path.join(OUT, 'triangles.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'props_batch1.blend'))
print('EXPORTED', [(r['id'], r['tris']) for r in REP['parts']], flush=True)
if not RENDER: sys.exit(0)

# ---------- previews: Cycles CPU (Studio holds the GPU), one at a time
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 48; sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'Standard'
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.95, 0.75, 0.65, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = 3.5; sun.rotation_euler = (math.radians(50), 0, math.radians(-60)); sc.collection.objects.link(sun)
gm = bpy.data.meshes.new('ground'); gm.from_pydata([(-60,-60,0),(60,-60,0),(60,60,0),(-60,60,0)], [], [(0,1,2,3)])
gmat = bpy.data.materials.new('felt'); gmat.use_nodes = True; gmat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = srgb('#4FA83D')
gm.materials.append(gmat); ground = bpy.data.objects.new('ground', gm); sc.collection.objects.link(ground)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 1280, 960
roots = {o.name: o for o in sc.objects if o.type == 'EMPTY'}
GROUND_Y = {'h06_sluice_gate': 0, 'h09_windpump_rotor': -4.12, 'h11_lock_gate': 0, 'h14_ore_bucket': -10.35, 'h17_shadow_arms': 0, 'flag': 0}
def bounds(r):
    pts = [o.matrix_world @ Vector(c) for o in r.children for c in o.bound_box]
    lo = Vector([min(q[i] for q in pts) for i in range(3)]); hi = Vector([max(q[i] for q in pts) for i in range(3)]); return lo, hi
for name, r in roots.items():
    for n2, r2 in roots.items():
        for o in r2.children: o.hide_render = (n2 != name)
    ground.location = (0, 0, GROUND_Y[name]); lo, hi = bounds(r); c = (lo + hi)/2; size = (hi - lo).length
    for view in ('34', 'eye', 'front'):
        if view == '34': d = Vector((1.0, -1.3, 0.8)).normalized(); cam.data.type = 'PERSP'; cam.data.lens = 50; eye = c + d*size*1.6
        elif view == 'eye': d = Vector((0.25, -1.0, 0.0)).normalized(); cam.data.type = 'PERSP'; cam.data.lens = 35; eye = Vector((c.x, c.y, GROUND_Y[name] + 5.0)) + d*max(size*1.1, 6)
        else: cam.data.type = 'ORTHO'; cam.data.ortho_scale = max(hi.x-lo.x, hi.z-lo.z)*1.25; eye = c + Vector((0, -50, 0))
        cam.location = eye; cam.rotation_euler = (c - eye).to_track_quat('-Z', 'Y').to_euler(); cam.data.clip_end = 500
        sc.render.filepath = os.path.join(PV, f'{name}_{view}.png'); bpy.ops.render.render(write_still=True); print('R', name, view, flush=True)
print('DONE_ALL', flush=True)
