# build_thumbnail_round2.py - Pirate ship thumbnail ROUND 2 (revised A hero / B octopus) from the preserved round-1 file.
#
#   blender -b --factory-startup --python-exit-code 1 --python out/src/build_thumbnail_round2.py -- \
#       --source inputs/pirate_thumbnail_round1.blend --approved inputs/start_ship_whimsy_v5_1.blend \
#       --output out/pirate_thumbnail_round2.blend [--config out/src/round2_config.json] [--report out/build/build_report_r2.json]
#
# What it does (all changes are RENDER-ONLY staging; the authentic ship is never edited):
#  * Opens the round-1 file read-only (save_as copy to --output, the input is never written). Records SHA-256 of --source
#    and --approved before and after.
#  * Drops round-1 scene C (+ its camera/lights/dressing) and rebuilds scenes A and B with new saved cameras
#    (Thumbnail_A_Hero_R2 / Thumbnail_B_Octopus_R2), new light rigs, curated per-scene kit dressing (3-5 palms each,
#    reusing the ORIGINAL kit_v1 / kit_v22 mesh datablocks already in the round-1 file) and render-only golf props.
#  * Scene A links a new collection RO2_ShipVisual_NoPier that holds the original Visual objects except "Pier"
#    (object links only - the Pier object/mesh stays in the file untouched and is still used by the original Scene and B).
#  * Ship objects (Visual / Props / Ramps collections): no mesh, material, modifier, transform or origin edits.
#    Only additions: the ship collections are linked as children of a light-linking receiver collection.
#  * New render-only golf props: dimpled white ball (real displaced dimple geometry: 162 spherical-cap dimples on a 10,242-vertex sphere) and a
#    simple low-poly putter. One ball+putter per scene, placed from image-space targets by ray-casting the staged terrain.
import bpy, bmesh, math, os, sys, json, argparse, hashlib
from mathutils import Vector, Matrix, Euler
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view as w2c

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(OUTDIR, '..'))


def parse_args():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--source', default=os.path.join(ROOT, 'inputs', 'pirate_thumbnail_round1.blend'))
    p.add_argument('--approved', default=os.path.join(ROOT, 'inputs', 'start_ship_whimsy_v5_1.blend'))
    p.add_argument('--output', default=os.path.join(OUTDIR, 'pirate_thumbnail_round2.blend'))
    p.add_argument('--config', default=os.path.join(HERE, 'round2_config.json'))
    p.add_argument('--report', default=os.path.join(OUTDIR, 'build', 'build_report_r2.json'))
    p.add_argument('--res', default='1280x720')
    p.add_argument('--samples', type=int, default=64)
    return p.parse_args(argv)


ARGS = parse_args()
for _k in ('source', 'approved', 'output', 'config', 'report'):
    setattr(ARGS, _k, os.path.abspath(getattr(ARGS, _k)))
RES = tuple(int(v) for v in ARGS.res.lower().split('x'))
CFG = json.load(open(ARGS.config))


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def srgb_to_lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin(rgb, a=None):
    t = tuple(srgb_to_lin(c) for c in rgb)
    return t + ((a,) if a is not None else ())


SHIP_COLS = ('Visual', 'Props', 'Ramps')
TERRAIN = None


BVH = None


def terrain_ray(origin, d):
    """ray-cast the staged terrain mesh (world space; BVH built from its world-space vertices)"""
    loc, nrm, idx, dist = BVH.ray_cast(Vector(origin), Vector(d))
    return (loc is not None), loc, nrm, idx


def ground_z(x, y):
    ok, loc, nrm, idx = terrain_ray((x, y, 500.0), (0, 0, -1))
    return loc.z if ok else 0.0


def new_coll(name, parent=None):
    c = bpy.data.collections.new(name)
    if parent is not None:
        parent.children.link(c)
    return c


# ------------------------------------------------------------------------------------------------ golf props (render-only)
def make_ball_mesh(name='RO2_GolfBall'):
    """unit-radius golf ball: bmesh icosphere(subdivisions=6 -> 10,242 verts) radially displaced by 162 spherical-cap dimples
    centred on the vertices of a bmesh icosphere(subdivisions=3 -> 162 verts)"""
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    centers = [v.co.normalized() for v in bm.verts]; bm.free()
    kd = KDTree(len(centers))
    for i, c in enumerate(centers): kd.insert(c, i)
    kd.balance()
    spacing = min((centers[0] - c).length for c in centers[1:])          # chord to nearest neighbouring dimple centre
    rd = 0.46 * spacing                                                   # dimple radius (chord)
    depth = 0.022
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=6, radius=1.0)
    for v in bm.verts:
        n = v.co.normalized()
        _, _, d = kd.find(n)
        r = 1.0
        if d < rd:
            t = d / rd
            r -= depth * (1.0 - t * t)          # spherical-cap profile, smooth rim
        v.co = n * r
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    m = bpy.data.materials.new('RO2_GolfBall_White'); m.use_nodes = True
    bs = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value = lin((236, 236, 230), 1.0)
    bs.inputs['Roughness'].default_value = 0.38
    try:
        bs.inputs['Coat Weight'].default_value = 0.25; bs.inputs['Coat Roughness'].default_value = 0.12
    except KeyError:
        pass
    me.materials.append(m)
    return me, len(centers)


def box(bm, c, s, rot=None):
    r = bmesh.ops.create_cube(bm, size=1.0)
    M = Matrix.Translation(Vector(c)) @ (rot.to_4x4() if rot else Matrix()) @ Matrix.Diagonal((s[0], s[1], s[2], 1))
    bmesh.ops.transform(bm, matrix=M, verts=r['verts'])
    return r['verts']


def cyl(bm, a, b, r, seg=10):
    a, b = Vector(a), Vector(b); d = b - a
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
    q = d.normalized().to_track_quat('Z', 'Y')
    M = Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=M, verts=res['verts'])
    return res['verts']


def make_putter_mesh(name='RO2_Putter'):
    """unit = ball radius. Local frame: mallet head centred at origin, sole on z=0, toe-heel axis along X (heel at -X).
    The shaft leaves the heel through a short hosel and runs toward -X sloping down to rest its grip on the sand
    (a putter lying on the beach - no swing / action implied)."""
    mats = {}
    def mat(key, rgb, rough, metal):
        m = bpy.data.materials.new('RO2_Putter_' + key); m.use_nodes = True
        bs = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        bs.inputs['Base Color'].default_value = lin(rgb, 1.0); bs.inputs['Roughness'].default_value = rough
        bs.inputs['Metallic'].default_value = metal
        mats[key] = m
    mat('Head', (58, 66, 84), 0.34, 0.8)       # gunmetal-navy mallet
    mat('Shaft', (150, 156, 166), 0.32, 1.0)   # satin steel
    mat('Grip', (28, 26, 30), 0.7, 0.0)        # black rubber grip
    mat('Accent', (168, 174, 184), 0.3, 1.0)   # steel face insert + sight line
    order = ['Head', 'Accent', 'Shaft', 'Grip']
    parts = []
    bm = bmesh.new()
    box(bm, (0, 0, 0.45), (3.8, 1.7, 0.9))
    bmesh.ops.bevel(bm, geom=[e for e in bm.edges], offset=0.3, segments=3, affect='EDGES')
    parts.append(('Head', bm))
    bm2 = bmesh.new()
    box(bm2, (0, -0.86, 0.45), (3.0, 0.05, 0.55))          # face insert (toward -Y)
    box(bm2, (0.0, 0.0, 0.915), (0.14, 1.1, 0.04))          # sight line on top
    parts.append(('Accent', bm2))
    heel = Vector((-1.55, 0.0, 0.85))
    neck = heel + Vector((-0.45, 0.0, 0.75))
    L_shaft, L_grip, r_grip = 24.0, 8.0, 0.36
    drop = neck.z - r_grip
    ang = math.asin(min(0.9, drop / (L_shaft + L_grip)))
    d = Vector((-math.cos(ang), 0.0, -math.sin(ang)))
    shaft_end = neck + d * L_shaft
    grip_end = shaft_end + d * L_grip
    bm3 = bmesh.new()
    cyl(bm3, heel, neck, 0.24)
    cyl(bm3, neck, shaft_end, 0.24, seg=12)
    parts.append(('Shaft', bm3))
    bm4 = bmesh.new()
    cyl(bm4, shaft_end, grip_end, r_grip, seg=12)
    parts.append(('Grip', bm4))
    me = bpy.data.meshes.new(name)
    full = bmesh.new()
    for key, b in parts:
        tmp = bpy.data.meshes.new('tmp'); b.to_mesh(tmp); b.free()
        for p in tmp.polygons: p.material_index = order.index(key)
        full.from_mesh(tmp); bpy.data.meshes.remove(tmp)
    full.to_mesh(me); full.free()
    for p in me.polygons: p.use_smooth = False
    for k in order: me.materials.append(mats[k])
    return me


# ------------------------------------------------------------------------------------------------ cameras / lights
def cam_from_spec(name, sp):
    """orbit camera: horizontal azimuth `az` (deg, from +X) and distance `dist` around target xy, absolute height `cam_z`,
    looking at (target.x, target.y, look_z) - or level+`pitch` deg; lens shift moves the frame without converging verticals any further."""
    t = Vector(sp['target'])
    az = math.radians(sp['az'])
    loc = Vector((t.x + math.cos(az) * sp['dist'], t.y + math.sin(az) * sp['dist'], sp['cam_z']))
    if 'pitch' in sp:   # level-ish view: look away from the target xy direction, pitched up by `pitch` deg
        hd = Vector((t.x - loc.x, t.y - loc.y, 0)).normalized()
        hd = Matrix.Rotation(math.radians(sp.get('yaw_offset', 0.0)), 3, 'Z') @ hd      # + turns the view left
        tgt = loc + hd + Vector((0, 0, math.tan(math.radians(sp['pitch']))))
    else:
        tgt = Vector((t.x, t.y, sp['look_z']))
    cd = bpy.data.cameras.new(name); cd.lens = sp['lens']; cd.sensor_fit = 'HORIZONTAL'; cd.sensor_width = 36.0
    cd.clip_start = 0.5; cd.clip_end = 30000.0
    cd.shift_x = sp.get('shift_x', 0.0); cd.shift_y = sp.get('shift_y', 0.0)
    ob = bpy.data.objects.new(name, cd)
    q = (tgt - loc).to_track_quat('-Z', 'Y')
    ob.matrix_world = Matrix.LocRotScale(loc, q, Vector((1, 1, 1)))
    return ob


def sun(name, az_from, elev, strength, rgb, angle=2.0, shadow=True, glossy=True):
    sd = bpy.data.lights.new(name, 'SUN'); sd.energy = strength; sd.color = lin(rgb); sd.angle = math.radians(angle)
    sd.use_shadow = shadow
    ob = bpy.data.objects.new(name, sd)
    ob.visible_glossy = glossy
    el, az = math.radians(elev), math.radians(az_from)
    to_sun = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    ob.rotation_euler = (-to_sun).to_track_quat('-Z', 'Y').to_euler()
    return ob


def setup_render(sc, cam, samples):
    sc.camera = cam
    sc.render.engine = 'CYCLES'
    cy = sc.cycles
    cy.device = 'CPU'
    cy.samples = samples; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02
    cy.use_denoising = True
    try: cy.denoiser = 'OPENIMAGEDENOISE'
    except TypeError: pass
    cy.max_bounces = 8; cy.diffuse_bounces = 3; cy.glossy_bounces = 2; cy.transmission_bounces = 4; cy.transparent_max_bounces = 16
    cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 1.0
    sc.render.resolution_x, sc.render.resolution_y = RES; sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    vs = sc.view_settings; vs.view_transform = 'Standard'; vs.look = 'None'; vs.gamma = 1.0
    sc.display_settings.display_device = 'sRGB'
    im = sc.render.image_settings; im.file_format = 'PNG'; im.color_mode = 'RGB'; im.color_depth = '8'


# ------------------------------------------------------------------------------------------------ projections
def proj(sc, cam, p):
    v = w2c(sc, cam, Vector(p)); return v


def mesh_uv(sc, cam, names, pred=None, step=1):
    pts = []
    for nm in names:
        o = bpy.data.objects[nm]
        if o.type != 'MESH': continue
        M = o.matrix_world; vs = o.data.vertices
        for i in range(0, len(vs), step):
            w = M @ vs[i].co
            if pred and not pred(w): continue
            u = w2c(sc, cam, w)
            if u.z > 0: pts.append((u.x, u.y))
    return pts


def ext(pts):
    if not pts: return None
    return dict(u=[round(min(p[0] for p in pts), 4), round(max(p[0] for p in pts), 4)],
                v=[round(min(p[1] for p in pts), 4), round(max(p[1] for p in pts), 4)])


def place_ball(sc, cam, ball_me, putter_me, sp, coll, tag):
    """solve ball radius/position so its projected height = sp['ball_frac'] at image point (u, v_center)"""
    u, v, frac = sp['ball_uv'][0], sp['ball_uv'][1], sp['ball_frac']
    cd = cam.data
    M = cam.matrix_world
    origin = M.translation
    # view ray through (u, v) using the camera frame
    fr = [M @ c for c in cd.view_frame(scene=sc)]   # tr, br, bl, tl (world)
    def ray(uu, vv):
        top = fr[3].lerp(fr[0], uu); bot = fr[2].lerp(fr[1], uu)
        p = bot.lerp(top, vv); return (p - origin).normalized()
    R = 2.0
    for _ in range(8):
        # bottom contact point lies on the ray through (u, v - frac/2)
        d = ray(u, v - frac / 2.0)
        if sp.get('sandbar_z') is not None:      # staged render-only sandbar: contact point on plane z = sandbar_z
            tz = sp['sandbar_z']; k = (tz - origin.z) / d.z
            hit = origin + d * k; ok = k > 0
        else:
            ok, hit, n, idx = terrain_ray(origin, d)
        if not ok: raise RuntimeError('ball ray missed terrain')
        c = hit + Vector((0, 0, R * 0.92))        # slightly sunk into sand
        pts = []
        for i in range(48):
            a = 2 * math.pi * i / 48
            # silhouette-ish sample: points on sphere in camera-perpendicular circle
            cz = (c - origin).normalized()
            ax = cz.cross(Vector((0, 0, 1))).normalized(); ay = ax.cross(cz)
            pts.append(w2c(sc, cam, c + (ax * math.cos(a) + ay * math.sin(a)) * R))
        h = max(p.y for p in pts) - min(p.y for p in pts)
        R *= frac / h
    ball = bpy.data.objects.new('RO2_%s_GolfBall' % tag, ball_me)
    ball.location = c; ball.scale = (R, R, R)
    ball.rotation_euler = (0.3, 0.2, 0.5)
    coll.objects.link(ball)
    # putter: head alongside (left of) and slightly behind the ball; shaft points toward frame-left, lying on the sand
    fwd = (c - origin); fwd.z = 0; fwd.normalize()
    right = fwd.cross(Vector((0, 0, 1))).normalized()
    po = sp.get('putter_offset', [-3.0, 0.8])        # (right, forward) in ball radii
    hp = c + right * (po[0] * R) + fwd * (po[1] * R)
    hz = sp['sandbar_z'] if sp.get('sandbar_z') is not None else ground_z(hp.x, hp.y)
    t = math.radians(sp.get('putter_yaw', 0.0))      # + turns the shaft toward the camera
    sdir = -right * math.cos(t) - fwd * math.sin(t)  # world direction of local -X (shaft)
    yaw = math.atan2(-sdir.y, -sdir.x)
    putter = bpy.data.objects.new('RO2_%s_Putter' % tag, putter_me)
    putter.location = (hp.x, hp.y, hz - 0.04 * R)
    putter.rotation_euler = (0, 0, yaw)
    putter.scale = (R, R, R)
    coll.objects.link(putter)
    bar = None
    if sp.get('sandbar_z') is not None:
        bar = make_sandbar('RO2_%s_Sandbar' % tag, c, hp, sdir, R, sp['sandbar_z'], coll)
    return ball, putter, R, bar


def make_sandbar(name, ball_c, head_p, sdir, R, top_z, coll):
    """faceted low sand mound (render-only staging) under ball + putter, elongated along the putter shaft"""
    import random
    rnd = random.Random(11)
    ctr = (ball_c + head_p) / 2 + sdir * (10.0 * R); ctr.z = 0
    ax = sdir.copy(); ax.z = 0; ax.normalize(); ay = Vector((0, 0, 1)).cross(ax)
    a_len, b_len = 24.0 * R, 7.0 * R
    rings, segs = 7, 28
    verts = [Vector((ctr.x, ctr.y, top_z + 0.15 * R))]
    for r in range(1, rings + 1):
        f = r / rings
        for k in range(segs):
            th = 2 * math.pi * (k + 0.5 * (r % 2)) / segs
            jit = 1.0 + rnd.uniform(-0.06, 0.06)
            p = ctr + ax * (math.cos(th) * a_len * f * jit) + ay * (math.sin(th) * b_len * f * jit)
            # flat top to 55% radius, then falls below the water line (z=1) to -3
            h = top_z if f <= 0.55 else top_z - (top_z + 3.0) * ((f - 0.55) / 0.45) ** 1.4
            verts.append(Vector((p.x, p.y, h + rnd.uniform(-0.12, 0.12) * R * (1 - f))))
    faces = []
    for k in range(segs):
        faces.append((0, 1 + k, 1 + (k + 1) % segs))
    for r in range(1, rings):
        o0 = 1 + (r - 1) * segs; o1 = 1 + r * segs
        for k in range(segs):
            a, b = o0 + k, o0 + (k + 1) % segs
            c2, d2 = o1 + k, o1 + (k + 1) % segs
            faces.append((a, c2, d2)); faces.append((a, d2, b))
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], faces); me.validate(); me.update()
    for p in me.polygons: p.use_smooth = False
    me.materials.append(bpy.data.materials['RO_Sand_Seabed'])
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    return ob


# ------------------------------------------------------------------------------------------------ main
def main():
    global TERRAIN
    sha_src_before = sha(ARGS.source); sha_app_before = sha(ARGS.approved)
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(ARGS.source), load_ui=False)
    global BVH
    TERRAIN = bpy.data.objects['RO_CoveTerrain']
    Mt = TERRAIN.matrix_world
    BVH = BVHTree.FromPolygons([Mt @ v.co for v in TERRAIN.data.vertices], [tuple(p.vertices) for p in TERRAIN.data.polygons])
    water = bpy.data.objects['RO_WaterSurface']; floor = bpy.data.objects['RO_SeaFloorFar']
    world = bpy.data.worlds['RO_TropicalSky']

    # ---- remove round-1 thumbnail scenes, their cameras/lights and round-1 kit placements (render-only staging) -----------
    removed = dict(scenes=[], objects=[], collections=[])
    for nm in ('Thumbnail_A_Hero', 'Thumbnail_B_Octopus', 'Thumbnail_C_Adventure'):
        sc = bpy.data.scenes.get(nm)
        if sc:
            bpy.data.scenes.remove(sc); removed['scenes'].append(nm)
    for o in list(bpy.data.objects):
        if o.type in ('CAMERA', 'LIGHT') and o.name[:2] in ('A_', 'B_', 'C_') or o.name.startswith('Thumbnail_') or \
                (o.name.startswith('RO_kit_') and o.type == 'MESH'):
            removed['objects'].append(o.name); bpy.data.objects.remove(o)
    for nm in ('RO_Env_A_only', 'RO_Env_B_only', 'RO_Env_C_only', 'RO_Env_Common'):
        c = bpy.data.collections.get(nm)
        if c: removed['collections'].append(nm); bpy.data.collections.remove(c)
    old_env = bpy.data.collections.get('RENDER_ONLY_Environment')
    if old_env: bpy.data.collections.remove(old_env)
    for blk in (bpy.data.cameras, bpy.data.lights):
        for d in list(blk):
            if d.users == 0: blk.remove(d)

    env = new_coll('RENDER_ONLY_Environment_R2')
    base = new_coll('RO2_Env_Base', env)
    for o in (TERRAIN, water, floor): base.objects.link(o)
    ship_cols = [bpy.data.collections[n] for n in SHIP_COLS]
    ship_vis = [o.name for c in ship_cols for o in c.objects if o.type == 'MESH']
    # Visual minus the separate left Pier (object links only) - used by scenes with hide_pier
    a_vis = new_coll('RO2_ShipVisual_NoPier')
    for o in bpy.data.collections['Visual'].objects:
        if o.name != 'Pier': a_vis.objects.link(o)
    # light-linking receiver: the authentic ship collections (+ golf props are added per scene below)
    recv = {}

    ball_me, n_dimples = make_ball_mesh(); putter_me = make_putter_mesh()
    figure = bpy.data.objects['Prop_Figurehead']
    report = dict(source=dict(path=ARGS.source, sha256_before=sha_src_before), approved=dict(path=ARGS.approved, sha256_before=sha_app_before),
                  output=ARGS.output, removed_round1_staging=removed, ship_objects=ship_vis, scenes={}, placed=[],
                  golf_ball=dict(mesh=ball_me.name, dimples=n_dimples, tris=len(ball_me.polygons) * 1, geometry='bmesh icosphere subdivisions=6 (10,242 verts) radially displaced by spherical-cap dimples (real geometry, no texture)'),
                  putter=dict(mesh=putter_me.name, tris=sum(len(p.vertices) - 2 for p in putter_me.polygons)))

    for key, sp in CFG['scenes'].items():
        scn_name = sp['scene']
        sc = bpy.data.scenes.new(scn_name)
        vis_coll = a_vis if sp.get('hide_pier') else bpy.data.collections['Visual']
        sc.collection.children.link(vis_coll)
        for n in ('Props', 'Ramps'): sc.collection.children.link(bpy.data.collections[n])
        sc.collection.children.link(base)
        dress = new_coll('RO2_%s_Dressing' % key, env); sc.collection.children.link(dress)
        golf = new_coll('RO2_%s_GolfProps_RenderOnly' % key, env); sc.collection.children.link(golf)
        sc.world = world
        cam = cam_from_spec(sp['camera_name'], sp['camera']); sc.collection.objects.link(cam)
        setup_render(sc, cam, ARGS.samples)
        sc.view_settings.exposure = sp.get('exposure', -0.15)
        sc['round2_note'] = 'RENDER_ONLY staged cove + golf identity props - not the game layout, no playable hole implied'
        # kit dressing
        for it in sp['dressing']:
            if it[0] == '@uv':      # image-space placement: ray from this camera through (u, v) onto the staged terrain
                _, pid, uu, vv, s, yaw = it[:6]
                fr = [cam.matrix_world @ cc for cc in cam.data.view_frame(scene=sc)]
                pt = fr[2].lerp(fr[1], uu).lerp(fr[3].lerp(fr[0], uu), vv)
                ok, hit, _n, _i = terrain_ray(cam.matrix_world.translation, (pt - cam.matrix_world.translation).normalized())
                if not ok or hit.z < 1.6:
                    raise RuntimeError('dressing %s at uv %s does not land on dry sand' % (pid, (uu, vv)))
                x, y, sink = hit.x, hit.y, 0.0
            else:
                pid, x, y, s, yaw = it[:5]
                sink = it[5] if len(it) > 5 else 0.0
            me = bpy.data.meshes['KIT_' + pid]
            ob = bpy.data.objects.new('RO2_%s_%s_%02d' % (key, pid, len(report['placed'])), me)
            gz = ground_z(x, y)
            ob.location = (x, y, gz - sink); ob.rotation_euler = (0, 0, math.radians(yaw)); ob.scale = (s, s, s)
            dress.objects.link(ob)
            report['placed'].append(dict(scene=scn_name, object=ob.name, prop=pid, mesh=me.name, kit='kit_v22' if pid in ('kit_boulder_pile', 'kit_canopy_wall') else 'kit_v1',
                                         loc=[round(x, 1), round(y, 1), round(gz - sink, 2)], scale=s, yaw=yaw, tris=len(me.polygons)))
        # lights
        L = sp['lights']; lights = []
        az, el, st = L['key']; lights.append(sun('%s_R2_Sun_Key' % key, az, el, st, tuple(L.get('key_rgb', (255, 238, 214))), angle=2.5))
        az, el, st = L['fill']; lights.append(sun('%s_R2_Fill_NoShadow' % key, az, el, st, tuple(L.get('fill_rgb', (255, 232, 206))), shadow=False, glossy=False))
        az, el, st = L['rim']; lights.append(sun('%s_R2_Rim_Cool' % key, az, el, st, tuple(L.get('rim_rgb', (200, 222, 255))), angle=4.0, glossy=False))
        az, el, st = L['ship_fill']
        sf = sun('%s_R2_ShipFaceFill_Linked' % key, az, el, st, tuple(L.get('ship_fill_rgb', (255, 224, 198))), shadow=False, glossy=False)
        # receivers: every authentic ship mesh shown in this scene EXCEPT 'Rigging' (masts/sails/ropes), so hull + octopus face
        # get the extra warm fill without pushing the cream sails toward clipping (object links only)
        rc = new_coll('RO2_%s_LightLink_HullFace' % key)
        for c in (vis_coll, bpy.data.collections['Props'], bpy.data.collections['Ramps']):
            for o in c.objects:
                if o.type == 'MESH' and o.name != 'Rigging' and o.name not in rc.objects: rc.objects.link(o)
        sf.light_linking.receiver_collection = rc
        lights.append(sf)
        if 'hull_bounce' in L:   # warm upward 'sand bounce' on the hull only (counters the turquoise lagoon bounce = olive cast)
            rh = new_coll('RO2_%s_LightLink_HullOnly' % key)
            for o in rc.objects:
                if o.name != 'Prop_Figurehead': rh.objects.link(o)
            az, el, st = L['hull_bounce']
            hb = sun('%s_R2_HullBounce_Linked' % key, az, el, st, tuple(L.get('hull_bounce_rgb', (255, 214, 170))), shadow=False, glossy=False)
            hb.light_linking.receiver_collection = rh
            lights.append(hb)
        if 'face_bounce' in L:   # same warm upward bounce on the octopus only (lifts the CoralDk underside toward 180,80,70)
            rf = new_coll('RO2_%s_LightLink_OctopusOnly' % key); rf.objects.link(bpy.data.objects['Prop_Figurehead'])
            az, el, st = L['face_bounce']
            fb = sun('%s_R2_FaceBounce_Linked' % key, az, el, st, tuple(L.get('hull_bounce_rgb', (255, 214, 170))), shadow=False, glossy=False)
            fb.light_linking.receiver_collection = rf
            lights.append(fb)
        if 'sail_fill' in L:     # soft cream fill on the sails/masts only ('Rigging'), keeps sail faces broad without lifting the face
            rr = new_coll('RO2_%s_LightLink_SailsOnly' % key); rr.objects.link(bpy.data.objects['Rigging'])
            az, el, st = L['sail_fill']
            sl = sun('%s_R2_SailFill_Linked' % key, az, el, st, tuple(L.get('sail_fill_rgb', (255, 244, 228))), shadow=False, glossy=False)
            sl.light_linking.receiver_collection = rr
            lights.append(sl)
        for lo in lights: sc.collection.objects.link(lo)
        # golf props
        bpy.context.window_manager  # noqa
        ball, putter, R, bar = place_ball(sc, cam, ball_me, putter_me, sp, golf, key)
        report['scenes'][scn_name] = dict(key=key, camera=dict(name=cam.name, spec=sp['camera'], location=[round(x, 2) for x in cam.matrix_world.translation],
                                                                rotation_deg=[round(math.degrees(a), 2) for a in cam.matrix_world.to_euler()]),
                                          lights=[dict(name=lo.name, energy=lo.data.energy, color_linear=list(lo.data.color), shadow=lo.data.use_shadow,
                                                       linked_receivers=(lo.light_linking.receiver_collection.name if lo.light_linking.receiver_collection else None)) for lo in lights],
                                          exposure=sc.view_settings.exposure, view_transform='Standard', samples=ARGS.samples, resolution=list(RES),
                                          collections=[c.name for c in sc.collection.children], pier_hidden=bool(sp.get('hide_pier')),
                                          golf=dict(ball=ball.name, ball_radius=round(R, 3), ball_center=[round(x, 2) for x in ball.location],
                                                    sandbar=(bar.name if bar else None), sandbar_top_z=sp.get('sandbar_z'), putter=putter.name, putter_loc=[round(x, 2) for x in putter.location], putter_yaw_deg=round(math.degrees(putter.rotation_euler.z), 1),
                                                    water_z=water.location.z))
        print('SCENE', key, cam.name, 'ball R', round(R, 2), 'at', tuple(round(x, 1) for x in ball.location))

    # tidy: keep the original 'Scene' (untouched) as the window scene fallback; leave the ship data as loaded.
    for blk in (bpy.data.meshes,):
        pass
    bpy.ops.file.pack_all()
    os.makedirs(os.path.dirname(os.path.abspath(ARGS.output)), exist_ok=True)
    if os.path.abspath(ARGS.output) in (os.path.abspath(ARGS.source), os.path.abspath(ARGS.approved)):
        raise SystemExit('refusing to overwrite an input')
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(ARGS.output), copy=True, compress=True)
    report['source']['sha256_after'] = sha(ARGS.source); report['approved']['sha256_after'] = sha(ARGS.approved)
    os.makedirs(os.path.dirname(os.path.abspath(ARGS.report)), exist_ok=True)
    json.dump(report, open(ARGS.report, 'w'), indent=1, default=lambda o: list(o))
    print('SAVED', ARGS.output)
    print('BUILD_ROUND2_OK')


try:
    main()
except SystemExit:
    raise
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
