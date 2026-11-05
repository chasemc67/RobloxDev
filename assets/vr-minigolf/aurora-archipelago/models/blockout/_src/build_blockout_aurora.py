# Aurora Archipelago blockout from holes.json only (skill §3). Run: blender -b -P this.py -- <holes.json> <outdir>
import bpy, bmesh, json, math, sys, os
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index('--')+1:]
HOLES, OUT = argv[0], argv[1]
RENDER = '--norender' not in argv
D = json.load(open(HOLES))
os.makedirs(os.path.join(OUT, 'previews', 'blockout'), exist_ok=True)

def R(p):  # Roblox (x,y,z) -> Blender (x,-z,y)
    return Vector((p[0], -p[2], p[1]))
def roty(p, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [p[0]*c + p[2]*s, p[1], -p[0]*s + p[2]*c]
def add(a, b): return [a[i]+b[i] for i in range(3)]
def rot_axis(p, axis, deg):  # right-hand rot about axis (Roblox coords)
    m = Matrix.Rotation(math.radians(deg), 3, Vector(axis).normalized())
    return list(m @ Vector(p))
def to_world(h, p): return add(roty(p, h['world_yaw']), h['world_offset'])

COL = {'felt': (0.20, 0.62, 0.25, 1), 'ice': (0.55, 0.85, 0.95, 1), 'bank': (0.12, 0.45, 0.18, 1),
       'rail': (0.85, 0.85, 0.80, 1), 'obstacle': (0.95, 0.55, 0.10, 1), 'moving': (0.90, 0.10, 0.10, 1),
       'toggle': (0.85, 0.20, 0.75, 1), 'cup': (0.02, 0.02, 0.02, 1), 'flag': (0.88, 0.24, 0.19, 1),
       'tee': (0.98, 0.85, 0.10, 1), 'teleport': (0.50, 0.20, 0.90, 0.6), 'water': (0.10, 0.35, 0.90, 0.45),
       'pit': (0.10, 0.10, 0.15, 0.35), 'clearance': (1.0, 0.25, 0.85, 0.22), 'guard': (1, 1, 1, 0.18),
       'cupclear': (1.0, 0.95, 0.2, 0.25)}
MATS = {}
def mat(k):
    if k in MATS: return MATS[k]
    m = bpy.data.materials.new('bo_' + k); c = COL[k]
    m.diffuse_color = c; m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = c; b.inputs['Roughness'].default_value = 0.8
    if c[3] < 1:
        b.inputs['Alpha'].default_value = c[3]
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    MATS[k] = m; return m

BOX_F = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
def box_corners(center, size, yaw=0.0, post=None):
    sx, sy, sz = [s/2 for s in size]; out = []
    for (x, y, z) in [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,-sy,sz),(-sx,-sy,sz),(-sx,sy,-sz),(sx,sy,-sz),(sx,sy,sz),(-sx,sy,sz)]:
        p = roty([x, y, z], yaw)
        if post: p = post(p)
        out.append(p)
    return [add(p, center) for p in out]

def cyl(center, r, h, n=16, ybase=None):
    yb = center[1] if ybase is None else ybase; v = []; f = []
    for i in range(n):
        a = 2*math.pi*i/n; v.append([center[0]+r*math.cos(a), yb, center[2]+r*math.sin(a)])
    for i in range(n):
        a = 2*math.pi*i/n; v.append([center[0]+r*math.cos(a), yb+h, center[2]+r*math.sin(a)])
    f.append(tuple(range(n-1, -1, -1))); f.append(tuple(range(n, 2*n)))
    for i in range(n): j = (i+1) % n; f.append((i, j, n+j, n+i))
    return v, f

class Acc:
    def __init__(self): self.v = []; self.f = []
    def add(self, verts, faces):
        o = len(self.v); self.v += verts; self.f += [tuple(i+o for i in fc) for fc in faces]
    def boxp(self, corners): self.add(corners, BOX_F)

OBJS = []; MAN = {'course': D['course'], 'source': os.path.basename(HOLES), 'units': '1 Blender unit = 1 stud, Z-up in Blender; FBX axis_forward -Z, axis_up Y, scale 1.0 (Roblox Y-up). Blender +Y = Roblox -Z.',
       'placement': 'All meshes are in WORLD coordinates (hole frame already applied). Place the FBX root at CFrame.new(0,0,0). Hole root CFrame = CFrame.new(world_offset) * CFrame.Angles(0, rad(world_yaw), 0).',
       'colour_key': {k: [round(x, 3) for x in c] for k, c in COL.items()}, 'holes': []}
COLL = bpy.data.collections.new('blockout'); bpy.context.scene.collection.children.link(COLL)

def mkobj(name, acc, matkey, hole_coll, origin_world=None, worldfn=None):
    if not acc.v: return None
    org = Vector((0, 0, 0)) if origin_world is None else R(origin_world)
    me = bpy.data.meshes.new(name)
    me.from_pydata([R(p) - org for p in acc.v], [], acc.f); me.validate(); me.update()
    me.materials.append(mat(matkey))
    ob = bpy.data.objects.new(name, me); ob.location = org; hole_coll.objects.link(ob)
    bm = bmesh.new(); bm.from_mesh(me); bm.normal_update()
    # fix winding consistently
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); 
    tris = sum(len(f.verts) - 2 for f in bm.faces); bm.free()
    ws = [R(p) for p in acc.v]
    bb = [[min(p[i] for p in acc.v) for i in range(3)], [max(p[i] for p in acc.v) for i in range(3)]]
    OBJS.append(ob); ob['tris'] = tris
    return {'name': name, 'category': matkey, 'tris': tris, 'bbox_roblox_world': [[round(x, 3) for x in b] for b in bb],
            'pivot_roblox_world': [round(x, 4) for x in (origin_world or [0, 0, 0])]}

def hull_obj(name, pts, matkey, hole_coll):
    bm = bmesh.new(); vs = [bm.verts.new(R(p)) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs)
    dv = list({g for g in res.get('geom_interior', []) + res.get('geom_unused', []) if isinstance(g, bmesh.types.BMVert)})
    if dv: bmesh.ops.delete(bm, geom=dv, context='VERTS')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose: bmesh.ops.delete(bm, geom=loose, context='VERTS')
    me = bpy.data.meshes.new(name); bm.to_mesh(me)
    tris = sum(len(f.verts) - 2 for f in bm.faces); bm.free()
    me.materials.append(mat(matkey)); ob = bpy.data.objects.new(name, me); hole_coll.objects.link(ob); OBJS.append(ob); ob['tris'] = tris
    return {'name': name, 'category': matkey, 'tris': tris}

def felt_corners(f):
    cx, cy, cz = f['center']; sx, sz = f['size']; sl = f.get('slope'); th = f.get('thickness', 0.4)
    def top(lx, lz):
        if not sl: return cy
        if sl['axis'] == 'x': return cy + sl['rise'] * (lx / sx)
        return cy + sl['rise'] * (lz / sz)
    pts = []
    for dy in (1, 0):
        for (lx, lz) in [(-sx/2, -sz/2), (sx/2, -sz/2), (sx/2, sz/2), (-sx/2, sz/2)]:
            y = top(lx, lz) - (0 if dy else th)
            p = roty([lx, 0, lz], f.get('yaw', 0)); pts.append([cx + p[0], y, cz + p[2]])
    return pts[4:] + pts[:4]  # bottom first, then top -> matches BOX_F ordering

notes = []
for h in D['holes']:
    hid = h['id']; hc = bpy.data.collections.new(hid); COLL.children.link(hc)
    W = lambda p, h=h: to_world(h, p)
    hm = {'id': hid, 'name': h['name'], 'par': h['par'], 'gimmick': h['gimmick'], 'world_offset': h['world_offset'], 'world_yaw': h['world_yaw'],
          'hole_root_cframe': 'CFrame.new(%g, %g, %g) * CFrame.Angles(0, math.rad(%g), 0)' % (*h['world_offset'], h['world_yaw']),
          'tee_world': [round(x, 3) for x in W(h['tee']['position'])], 'cup_world': [round(x, 3) for x in W(h['cup']['position'])], 'objects': [], 'moving_parts': []}
    timed_ids = set(); 
    for mp in h['moving_parts']:
        if mp['type'] == 'toggle': timed_ids |= set(mp.get('felt_ids', []))
    groups = {'felt': Acc(), 'ice': Acc(), 'bank': Acc(), 'toggle': Acc()}
    for f in h['felt']:
        k = 'toggle' if (f['id'] in timed_ids or f.get('timed')) else 'ice' if f.get('surface') == 'ice' else 'bank' if (f.get('overlay') or f.get('kind') == 'bank') else 'felt'
        groups[k].boxp([W(p) for p in felt_corners(f)])
        if f['size'][0] <= 0 or f['size'][1] <= 0: notes.append(f'{hid} felt {f["id"]} has non-positive size')
    rails, obst = Acc(), Acc()
    for w in h['walls']:
        if min(w['size']) <= 0: notes.append(f'{hid} wall {w["id"]} non-positive size {w["size"]}')
        (obst if w.get('kind') == 'bumper' else rails).boxp([W(p) for p in box_corners(w['center'], w['size'], w.get('yaw', 0))])
    for k, a in list(groups.items()) + [('rail', rails), ('obstacle', obst)]:
        o = mkobj(f'{hid}_{k}', a, k, hc)
        if o: hm['objects'].append(o)
    # hazards
    for z in h['hazards']:
        a = Acc(); c = z['center']; a.boxp([W(p) for p in box_corners([c[0], c[1]-0.05, c[2]], [z['size'][0], 0.1, z['size'][1]], z.get('yaw', 0))])
        o = mkobj(f'{hid}_hazard_{z["id"]}', a, 'water' if z['type'] == 'water' else 'pit', hc); hm['objects'].append(o)
    # cup, flag, tee
    cp = h['cup']['position']; a = Acc(); a.add(*cyl(W(cp), h['cup']['radius'], 0.03, 24, ybase=W(cp)[1] + 0.005)); hm['objects'].append(mkobj(f'{hid}_cup', a, 'cup', hc))
    fl = h['cup'].get('flag', {}); ph = fl.get('pole_height', 7.5)
    a = Acc(); a.add(*cyl(W(cp), fl.get('pole_diameter', 0.15)/2, ph, 8, ybase=W(cp)[1]))
    bs = fl.get('banner_size', [2, 1.2, 0.05]); a.boxp([W(p) for p in box_corners([cp[0]+bs[0]/2, cp[1]+ph-bs[1]/2, cp[2]], bs, 0)])
    hm['objects'].append(mkobj(f'{hid}_flag', a, 'flag', hc))
    a = Acc(); a.add(*cyl(W(cp), 2.2, 0.02, 32, ybase=W(cp)[1] + 0.04)); hm['objects'].append(mkobj(f'{hid}_cup_clearance', a, 'cupclear', hc))
    tp = h['tee']['position']; a = Acc(); a.boxp([W(p) for p in box_corners([tp[0], tp[1]+0.02, tp[2]], [1.5, 0.04, 1.5], 0)]); hm['objects'].append(mkobj(f'{hid}_tee', a, 'tee', hc))
    # teleports
    for t in h['teleports']:
        a = Acc(); e = t['entry']
        if e.get('half_size'): a.boxp([W(p) for p in box_corners([e['center'][0], e['center'][1]+0.06, e['center'][2]], [2*e['half_size'][0], 0.1, 2*e['half_size'][1]], 0)])
        else: a.add(*cyl(W(e['center']), max(e['radius'], 0.3), 0.1, 16, ybase=W(e['center'])[1] + 0.02))
        x = t['exit']; a.add(*cyl(W(x['center']), 0.4, 0.1, 12, ybase=W(x['center'])[1] + 0.02))
        hm['objects'].append(mkobj(f'{hid}_teleport_{t["id"]}', a, 'teleport', hc))
    # player guards (vr_comfort)
    vc = h.get('vr_comfort') or {}
    if vc.get('player_guards'):
        a = Acc()
        for g in vc['player_guards']: a.boxp([W(p) for p in box_corners(g['center'], g['size'], g.get('yaw', 0))])
        hm['objects'].append(mkobj(f'{hid}_player_guards', a, 'guard', hc))
    # moving parts + sweep clearance volumes
    for mp in h['moving_parts']:
        if mp['type'] == 'toggle':
            hm['moving_parts'].append({'id': mp['id'], 'type': 'toggle', 'felt_ids': mp.get('felt_ids'), 'period_s': mp.get('period_s'), 'solid_window': mp.get('solid_window'),
                                       'note': f'felt piece(s) {mp.get("felt_ids")} are in mesh {hid}_toggle (magenta); no separate blockers'})
            continue
        piv = mp['pivot']; axis = mp['axis']
        def pose(b, ang=0.0, off=0.0):
            roll = b.get('roll', 0.0)
            post = (lambda p: rot_axis(p, axis, roll)) if roll else None
            cs = box_corners([0, 0, 0], b['size'], b.get('yaw', 0), post)
            c = rot_axis(b['center'], axis, roll) if roll else list(b['center'])
            pts = [add(c, p) for p in cs]
            if mp['type'] in ('rotate', 'swing'): pts = [rot_axis(p, axis, ang) for p in pts]
            else: pts = [add(p, [axis[i]*off for i in range(3)]) for p in pts]
            return [add(p, piv) for p in pts]
        ph0 = mp.get('phase', 0.0) or 0.0
        if mp['type'] == 'swing': a0 = mp['amplitude_deg'] * math.sin(math.radians(ph0))
        else: a0 = ph0
        a = Acc()
        for b in mp['blockers']:
            a.boxp([W(p) for p in (pose(b, ang=a0) if mp['type'] != 'slide' else pose(b, off=a0))])
        o = mkobj(f'{hid}_moving_{mp["id"]}', a, 'moving', hc, origin_world=W(piv)); hm['objects'].append(o)
        # sweep
        if mp['type'] == 'rotate' and mp.get('range') is None: samples = [i * 5.0 for i in range(72)]
        else:
            lo, hi = (mp['range'] if mp.get('range') else [-mp['amplitude_deg'], mp['amplitude_deg']]); n = 24
            samples = [lo + (hi - lo) * i / n for i in range(n + 1)]
        pts = []
        for s in samples:
            for b in mp['blockers']: pts += [W(p) for p in (pose(b, off=s) if mp['type'] == 'slide' else pose(b, ang=s))]
        so = hull_obj(f'{hid}_clearance_{mp["id"]}', pts, 'clearance', hc); hm['objects'].append(so)
        wax = roty(axis, h['world_yaw'])
        hm['moving_parts'].append({'id': mp['id'], 'type': mp['type'], 'mesh': f'{hid}_moving_{mp["id"]}', 'sweep_volume': so['name'],
            'pivot_local': piv, 'pivot_world': [round(x, 4) for x in W(piv)], 'axis_local': axis, 'axis_world': [round(x, 4) for x in wax],
            'pivot_cframe': 'CFrame.new(%g, %g, %g) * CFrame.Angles(0, math.rad(%g), 0)' % (*[round(x, 4) for x in W(piv)], h['world_yaw']),
            'speed': mp.get('speed'), 'speed_units': mp.get('speed_units'), 'range': mp.get('range'), 'amplitude_deg': mp.get('amplitude_deg'),
            'phase': mp.get('phase'), 'period_s': mp.get('period_s'), 'dwell': mp.get('dwell'),
            'mesh_pose': 'blockers at t=0 pose (phase); mesh origin = pivot; motion per holes.json',
            'sweep_note': 'convex hull of sampled blocker poses over the full range (swing/rotate hulls overstate the true swept band slightly)'})
    hm['tris_total'] = sum(o['tris'] for o in hm['objects'] if o)
    MAN['holes'].append(hm)

MAN['tris_total'] = sum(hh['tris_total'] for hh in MAN['holes'])
MAN['max_mesh_tris'] = max(ob['tris'] for ob in OBJS)
MAN['meshes'] = len(OBJS); MAN['oddities'] = notes
bad = [ob.name for ob in OBJS if ob['tris'] >= 20000]; MAN['over_20k'] = bad

# export
for ob in bpy.context.scene.objects: ob.select_set(False)
for ob in OBJS: ob.select_set(True)
bpy.context.view_layer.objects.active = OBJS[0]
fbx = os.path.join(OUT, 'blockout_aurora.fbx')
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, object_types={'MESH'}, axis_forward='-Z', axis_up='Y', global_scale=1.0,
                         apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', path_mode='COPY', embed_textures=True, mesh_smooth_type='FACE', add_leaf_bones=False)
MAN['fbx'] = 'blockout_aurora.fbx'
json.dump(MAN, open(os.path.join(OUT, 'blockout_aurora_manifest.json'), 'w'), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'blockout_aurora.blend'))
print('EXPORTED', fbx, MAN['tris_total'], MAN['max_mesh_tris'], bad, notes, flush=True)
if not RENDER: sys.exit(0)

# renders: Cycles CPU (Studio has the GPU), one at a time
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24
try: sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
sc.view_settings.view_transform = 'Standard'
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.55, 0.65, 0.85, 1); world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.8
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = 3.0; sun.rotation_euler = (math.radians(40), math.radians(15), math.radians(30)); sc.collection.objects.link(sun)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
pv = os.path.join(OUT, 'previews', 'blockout')
def look(cam, eye, tgt):
    d = tgt - eye; cam.location = eye; cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
for hm, h in zip(MAN['holes'], D['holes']):
    hid = hm['id']
    for c in COLL.children: c.hide_render = False
    # tee view: eye 5 studs above tee, aim at flag mid-height
    tee = R(hm['tee_world']); cupw = R(hm['cup_world'])
    cam.data.type = 'PERSP'; cam.data.lens_unit = 'FOV'; cam.data.angle = math.radians(75); cam.data.clip_end = 3000
    look(cam, tee + Vector((0, 0, 5)), cupw + Vector((0, 0, 1.0)))
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.render.filepath = os.path.join(pv, f'{hid}_tee.png'); bpy.ops.render.render(write_still=True); print('R', hid, 'tee', flush=True)
    # top-down, this hole only
    for c in COLL.children: c.hide_render = (c.name != hid)
    hc = bpy.data.collections[hid]; xs = []; ys = []; zs = []
    for ob in hc.objects:
        for v in ob.data.vertices:
            w = ob.matrix_world @ v.co
            if ob.name.endswith('_hazard_glimmer_gap') or '_hazard_' in ob.name and abs(w.z) > 20: continue
            xs.append(w.x); ys.append(w.y); zs.append(w.z)
    cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2; ext = max(max(xs)-min(xs), max(ys)-min(ys)) * 1.1 + 2
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = ext; cam.location = (cx, cy, max(zs) + 60); cam.rotation_euler = (0, 0, math.radians(h['world_yaw']))  # local -Z (north in layouts) up
    sc.render.resolution_x = sc.render.resolution_y = 1024
    sc.render.filepath = os.path.join(pv, f'{hid}_top.png'); bpy.ops.render.render(write_still=True); print('R', hid, 'top', flush=True)
print('DONE_ALL', flush=True)
