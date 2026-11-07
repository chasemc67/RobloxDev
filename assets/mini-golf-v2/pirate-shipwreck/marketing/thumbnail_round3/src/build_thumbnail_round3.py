# build_thumbnail_round3.py - Pirate ship thumbnail ROUND 3 (sketch follow-up): single lead scene Thumbnail_B_Lead_R3, built on
# round-2 scene A's camera/frame (per Chase's annotation inputs/chase_green_placement.png), with a RENDER_ONLY right-beach putting green.
#
#   blender -b --factory-startup --python-exit-code 1 --python out/src/build_thumbnail_round3.py -- \
#       --source inputs/pirate_thumbnail_round2.blend --approved inputs/start_ship_whimsy_v5_1.blend \
#       --output out/pirate_thumbnail_round3.blend [--config out/src/round3_config.json] [--report out/logs/build_report_r3.json]
#
# All changes are RENDER-ONLY staging; the authentic ship objects/meshes/materials/transforms are never edited.
#  * Opens the round-2 file (input never written; save_as copy to --output). SHA-256 of --source/--approved recorded before+after.
#  * Removes round-2 scene B (camera, lights, dressing, collections) and ALL round-2 giant balls / putters / sandbar (A and B).
#  * Renames round-2 scene A -> Thumbnail_B_Lead_R3 (camera too; deliverable stays named B_round3 = the single lead). The A camera is
#    kept exactly (camera.mode keep_base) unless config gives a small tweak. Splits the key light so the octopus figurehead gets a
#    softer linked key (local coral softening, as in the first round-3 pass; no exposure / material change).
#  * Adds new RENDER_ONLY golf cluster on the right beach near the bow: chunky low-poly putting green (turf top, raised rolled rim,
#    skirt) whose outline is the sketch's screen-space oval ray-cast onto the staged sand, dark cup, slender white pole (height
#    clamped so its top stays below the octopus), red triangular cloth flag, modest white ball on the green.
import bpy, bmesh, math, os, sys, json, argparse, hashlib, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view as w2c

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(OUTDIR, '..'))


def parse_args():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--source', default=os.path.join(ROOT, 'inputs', 'pirate_thumbnail_round2.blend'))
    p.add_argument('--approved', default=os.path.join(ROOT, 'inputs', 'start_ship_whimsy_v5_1.blend'))
    p.add_argument('--output', default=os.path.join(OUTDIR, 'pirate_thumbnail_round3.blend'))
    p.add_argument('--config', default=os.path.join(HERE, 'round3_config.json'))
    p.add_argument('--report', default=os.path.join(OUTDIR, 'logs', 'build_report_r3.json'))
    p.add_argument('--samples', type=int, default=64)
    return p.parse_args(argv)


A = parse_args()
for _k in ('source', 'approved', 'output', 'config', 'report'):
    setattr(A, _k, os.path.abspath(getattr(A, _k)))
CFG = json.load(open(A.config))


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def lin(rgb, a=1.0):
    f = lambda c: (c / 255.0) / 12.92 if c / 255.0 <= 0.04045 else ((c / 255.0 + 0.055) / 1.055) ** 2.4
    return tuple(f(c) for c in rgb) + (a,)


def mat(name, rgb, rough=0.8, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    bs = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value = lin(rgb); bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    m.diffuse_color = lin(rgb)
    return m


def set_camera(ob, sp):
    t = Vector(sp['target']); az = math.radians(sp['az'])
    loc = Vector((t.x + math.cos(az) * sp['dist'], t.y + math.sin(az) * sp['dist'], sp['cam_z']))
    hd = Vector((t.x - loc.x, t.y - loc.y, 0)).normalized()
    hd = Matrix.Rotation(math.radians(sp.get('yaw_offset', 0.0)), 3, 'Z') @ hd
    tgt = loc + hd + Vector((0, 0, math.tan(math.radians(sp['pitch']))))
    cd = ob.data; cd.lens = sp['lens']; cd.sensor_fit = 'HORIZONTAL'; cd.sensor_width = 36.0
    cd.shift_x = sp.get('shift_x', 0.0); cd.shift_y = sp.get('shift_y', 0.0)
    ob.matrix_world = Matrix.LocRotScale(loc, (tgt - loc).to_track_quat('-Z', 'Y'), Vector((1, 1, 1)))


def cam_ray(sc, cam, u, v):
    fr = [cam.matrix_world @ c for c in cam.data.view_frame(scene=sc)]   # tr, br, bl, tl
    p = fr[2].lerp(fr[1], u).lerp(fr[3].lerp(fr[0], u), v)
    o = cam.matrix_world.translation
    return o, (p - o).normalized()


def uv_ext(sc, cam, objs, pred=None):
    us, vs = [], []
    for o in objs:
        if o.type != 'MESH': continue
        M = o.matrix_basis if o.parent is None else o.matrix_world   # unevaluated file: basis is current for unparented staging
        for vt in o.data.vertices:
            w = M @ vt.co
            if pred and not pred(w): continue
            q = w2c(sc, cam, w)
            if q.z > 0: us.append(q.x); vs.append(q.y)
    if not us: return None
    return dict(u=[round(min(us), 4), round(max(us), 4)], v=[round(min(vs), 4), round(max(vs), 4)])


# ------------------------------------------------------------------------------------------------ golf cluster (render-only)
def build_green(sc, cam, BVH, g, coll):
    def ground(x, y):
        loc, *_ = BVH.ray_cast(Vector((x, y, 500.0)), Vector((0, 0, -1)))
        return loc.z if loc else -99.0
    gcu, gcv = g['uv']; rad_u, rad_v = g['radius_uv']
    O = cam.matrix_world.translation

    def hit_uv(u, v):
        o, d = cam_ray(sc, cam, u, v)
        loc, *_ = BVH.ray_cast(o, d)
        if loc is None: raise RuntimeError('green uv (%.3f, %.3f) misses the terrain' % (u, v))
        return loc
    hit = hit_uv(gcu, gcv)
    fwd = (hit - O); fwd.z = 0; fwd.normalize()
    right = fwd.cross(Vector((0, 0, 1))).normalized()
    C = Vector((hit.x, hit.y, 0))
    wob = g.get('wobble', 0.0)

    def outline(th, s):   # screen-space oval (sketch), slightly irregular, scaled by s, returned as world xy via the sand ray-cast
        r = 1.0 + wob * math.sin(3 * th + 0.7)
        p = hit_uv(gcu + rad_u * s * r * math.cos(th), gcv + rad_v * s * r * math.sin(th))
        return p.x, p.y

    def to_w(x, y):
        return Vector((x, y, 0))

    # fit a plane to the sand under the footprint (keeps the green sitting on the slope, not floating)
    samp = []
    for k in range(24):
        th = 2 * math.pi * k / 24
        for s in (0.0, 0.5, 1.0):
            p = to_w(*outline(th, s)); z = ground(p.x, p.y)
            if z < 1.6: raise RuntimeError('green footprint leaves dry sand at %s (z=%.2f)' % (tuple(round(c, 1) for c in p), z))
            samp.append((p.x, p.y, z))
    n = len(samp); mx = sum(s[0] for s in samp) / n; my = sum(s[1] for s in samp) / n; mz = sum(s[2] for s in samp) / n
    sxx = sum((s[0] - mx) ** 2 for s in samp); syy = sum((s[1] - my) ** 2 for s in samp); sxy = sum((s[0] - mx) * (s[1] - my) for s in samp)
    sxz = sum((s[0] - mx) * (s[2] - mz) for s in samp); syz = sum((s[1] - my) * (s[2] - mz) for s in samp)
    det = sxx * syy - sxy * sxy
    a = (sxz * syy - syz * sxy) / det; b = (syz * sxx - sxz * sxy) / det
    plane = lambda x, y: mz + a * (x - mx) + b * (y - my)
    h, rim = g['height'], g['rim']
    # rings: (scale, dz above plane, material)  0 turf top, 1 rolled rim, 2 skirt
    rings = [(0.80, h, 0), (0.90, h + 0.55 * rim, 1), (0.955, h + rim, 1), (1.0, h + 0.55 * rim, 1), (1.03, 0.45 * h, 2), (1.055, -0.7, 2)]
    seg = 30
    bm = bmesh.new()
    cv = bm.verts.new((C.x, C.y, plane(C.x, C.y) + h))
    ring_v = []
    for s, dz, _m in rings:
        rv = []
        for k in range(seg):
            p = to_w(*outline(2 * math.pi * k / seg, s))
            rv.append(bm.verts.new((p.x, p.y, plane(p.x, p.y) + dz)))
        ring_v.append(rv)
    for k in range(seg):
        f = bm.faces.new((cv, ring_v[0][k], ring_v[0][(k + 1) % seg])); f.material_index = 0
    for r in range(len(rings) - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            f = bm.faces.new((ring_v[r][k], ring_v[r + 1][k], ring_v[r + 1][k2], ring_v[r][k2]))
            f.material_index = 0 if r == 0 else (1 if r < 3 else 2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('RO3_PuttingGreen'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    for m in (mat('RO3_Turf', (78, 168, 70), 0.9), mat('RO3_TurfRim', (104, 186, 84), 0.85), mat('RO3_TurfSkirt', (54, 120, 52), 0.9)):
        me.materials.append(m)
    green = bpy.data.objects.new('RO3_RenderOnly_PuttingGreen', me); coll.objects.link(green)

    def on_top(fx, fy):
        p = hit_uv(gcu + rad_u * 0.8 * fx, gcv + rad_v * 0.8 * fy); return Vector((p.x, p.y, plane(p.x, p.y) + h))

    # cup: dark low-poly cylinder sunk into the turf (top 0.03 above the turf so it reads as a hole)
    cupc = on_top(*g['cup_offset'])
    bm = bmesh.new()
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=g['cup_r'], radius2=g['cup_r'], depth=1.2)
    bmesh.ops.translate(bm, verts=r['verts'], vec=Vector((0, 0, -0.57)))
    cme = bpy.data.meshes.new('RO3_Cup'); bm.to_mesh(cme); bm.free()
    cme.materials.append(mat('RO3_CupDark', (18, 20, 18), 0.95))
    cup = bpy.data.objects.new('RO3_RenderOnly_Cup', cme); cup.location = cupc; coll.objects.link(cup)
    # pole: slender white cylinder standing in the cup; height clamped so the top projects at or below pole_top_v_max (below the face)
    lo, hi = 2.0, g['pole_h']
    if w2c(sc, cam, cupc + Vector((0, 0, hi))).y > g['pole_top_v_max']:
        for _ in range(40):
            mid = (lo + hi) / 2
            if w2c(sc, cam, cupc + Vector((0, 0, mid))).y > g['pole_top_v_max']: hi = mid
            else: lo = mid
        pole_h = round(lo, 2)
    else:
        pole_h = g['pole_h']
    bm = bmesh.new()
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=g['pole_r'], radius2=g['pole_r'], depth=pole_h + 0.9)
    bmesh.ops.translate(bm, verts=r['verts'], vec=Vector((0, 0, (pole_h + 0.9) / 2 - 0.9)))
    pme = bpy.data.meshes.new('RO3_FlagPole'); bm.to_mesh(pme); bm.free()
    pme.materials.append(mat('RO3_PoleWhite', (240, 238, 230), 0.45))
    pole = bpy.data.objects.new('RO3_RenderOnly_FlagPole', pme); pole.location = cupc; coll.objects.link(pole)
    # flag: red triangular cloth (subdivided, gentle wave), flying toward camera-right and slightly away (never toward the face)
    fl, fh = g['flag_len'], g['flag_h']
    fdir = (right * math.cos(math.radians(25)) + fwd * math.sin(math.radians(25))).normalized()
    side = Vector((0, 0, 1)).cross(fdir).normalized()
    top = cupc + Vector((0, 0, pole_h - 0.15))
    nu, nv = 7, 4
    verts, faces = [], []
    idx = {}
    for i in range(nu + 1):
        t = i / nu
        col = []
        for j in range(nv + 1):
            if i == nu and j > 0: break
            s = j / nv
            zz = -fh * (1 - t) * s - fh * 0.5 * t      # triangle: hoist edge full height, tapering to the tip at mid-height
            wav = 0.35 * math.sin(t * math.pi * 1.6) * t
            p = top + fdir * (fl * t + g['pole_r']) + side * wav + Vector((0, 0, zz))
            idx[(i, j)] = len(verts); verts.append(tuple(p))
    for i in range(nu):
        for j in range(nv):
            a_ = idx[(i, j)]; b_ = idx[(i, j + 1)]
            if i + 1 == nu:
                faces.append((a_, idx[(nu, 0)], b_))
            else:
                faces.append((a_, idx[(i + 1, j)], idx[(i + 1, j + 1)], b_))
    fme = bpy.data.meshes.new('RO3_FlagCloth'); fme.from_pydata(verts, [], faces); fme.validate(); fme.update()
    fme.materials.append(mat('RO3_FlagRed', (214, 36, 32), 0.7))
    flag = bpy.data.objects.new('RO3_RenderOnly_FlagCloth', fme); coll.objects.link(flag)
    # ball: modest chunky white ball resting on the turf, short of the cup (no gameplay claim)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=g['ball_r'])
    bme = bpy.data.meshes.new('RO3_GolfBall_LowPoly'); bm.to_mesh(bme); bm.free()
    for p in bme.polygons: p.use_smooth = True
    bme.materials.append(mat('RO3_BallWhite', (246, 246, 240), 0.4))
    ballp = on_top(*g['ball_offset']) + Vector((0, 0, g['ball_r'] * 0.96))
    ball = bpy.data.objects.new('RO3_RenderOnly_GolfBall', bme); ball.location = ballp; coll.objects.link(ball)
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]
    info = dict(center=[round(c, 2) for c in (C.x, C.y, plane(C.x, C.y))], plane_slope=[round(a, 4), round(b, 4)],
                outline='screen-space oval uv %s radius_uv %s ray-cast onto the staged sand' % (g['uv'], g['radius_uv']),
                world_extent_xy=[round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1)], rim_height=rim, cup=[round(c, 2) for c in cupc], cup_radius=g['cup_r'],
                ball=[round(c, 2) for c in ballp], ball_radius=g['ball_r'], pole_height=pole_h, flag=[fl, fh],
                tris=sum(sum(len(p.vertices) - 2 for p in ob.data.polygons) for ob in (green, cup, pole, flag, ball)))
    return [green, cup, pole, flag, ball], info


# ------------------------------------------------------------------------------------------------ main
def main():
    rep = dict(source=dict(path=A.source, sha256_before=sha(A.source)), approved=dict(path=A.approved, sha256_before=sha(A.approved)),
               output=A.output, config=CFG)
    bpy.ops.wm.open_mainfile(filepath=A.source, load_ui=False)
    T = bpy.data.objects['RO_CoveTerrain']; Mt = T.matrix_world
    BVH = BVHTree.FromPolygons([Mt @ v.co for v in T.data.vertices], [tuple(p.vertices) for p in T.data.polygons])

    # 1) drop round-2 scene B (the sketch uses the A frame) and its staging; drop ALL round-2 giant balls / putters / sandbar
    removed = []
    base, drop = CFG['scene_in'], CFG['scene_drop']
    if drop in bpy.data.scenes:
        bpy.data.scenes.remove(bpy.data.scenes[drop]); removed.append('scene ' + drop)
    for o in list(bpy.data.objects):
        if o.name.startswith(('RO2_B_', 'B_R2_', drop)) or o.name in ('RO2_A_GolfBall', 'RO2_A_Putter', 'RO2_A_Sandbar'):
            removed.append(o.name); bpy.data.objects.remove(o)
    for c in list(bpy.data.collections):
        if c.name.startswith('RO2_B_') or c.name == 'RO2_A_GolfProps_RenderOnly':
            removed.append('collection ' + c.name); bpy.data.collections.remove(c)
    for blk, names in ((bpy.data.meshes, ('RO2_GolfBall', 'RO2_Putter', 'RO2_B_Sandbar', 'RO2_A_Sandbar')),
                       (bpy.data.materials, ('RO2_GolfBall_White', 'RO2_Putter_Head', 'RO2_Putter_Shaft', 'RO2_Putter_Grip', 'RO2_Putter_Accent'))):
        for nm in names:
            d = blk.get(nm)
            if d is not None and d.users == 0: blk.remove(d); removed.append('datablock ' + nm)
    for blk in (bpy.data.cameras, bpy.data.lights, bpy.data.meshes):
        for d in list(blk):
            if d.users == 0: blk.remove(d)
    rep['removed'] = removed

    # 2) round-2 scene A -> the single round-3 lead (named B_Lead so the one deliverable stays B_round3)
    sc = bpy.data.scenes[base]; sc.name = CFG['scene_out']
    cam = sc.camera; cam.name = CFG['scene_out']; cam.data.name = CFG['scene_out']
    sc.view_layers[0].update()
    cam.matrix_world = cam.matrix_basis.copy()
    base_cam = dict(location=[round(c, 3) for c in cam.matrix_world.translation], rotation_deg=[round(math.degrees(c), 3) for c in cam.matrix_world.to_euler()],
                    lens=cam.data.lens, shift=[cam.data.shift_x, cam.data.shift_y])
    if CFG['camera'].get('mode', 'keep_base') != 'keep_base':
        set_camera(cam, CFG['camera'])
    else:
        tw = CFG['camera'].get('tweak', {})
        if tw:
            cam.location.z += tw.get('dz', 0.0); cam.rotation_euler.x += math.radians(tw.get('dpitch_deg', 0.0))
            cam.data.shift_y += tw.get('dshift_y', 0.0); cam.matrix_world = cam.matrix_basis.copy()
    rep['camera_base_round2_A'] = base_cam
    sc.cycles.samples = A.samples; sc.cycles.device = 'CPU'
    for k in list(sc.keys()):
        if k.startswith('round2'): del sc[k]
    sc['round3_note'] = 'RENDER_ONLY staged cove + putting green/flag/ball - not the game layout, no live or playable hole implied. Frame = round-2 scene A camera (sketch follow-up).'
    for o in sc.objects:
        if o.name.startswith('A_R2_'): o.name = 'R3_' + o.name[5:]
        if o.name.startswith('RO2_A_'): o.name = 'RO3_' + o.name[6:]
    for c in bpy.data.collections:
        if c.name.startswith('RO2_A_'): c.name = 'RO3_' + c.name[6:]

    # 3) local coral softening: main key excludes the octopus; a face-only key at reduced strength replaces it (same direction)
    fig = bpy.data.objects['Prop_Figurehead']
    key = next(o for o in sc.objects if o.type == 'LIGHT' and o.name.endswith('Sun_Key'))
    ex = bpy.data.collections.new('RO3_B_LightLink_KeyExcludeOctopus'); ex.objects.link(fig)
    key.light_linking.receiver_collection = ex
    ex.collection_objects[0].light_linking.link_state = 'EXCLUDE'
    fk = key.copy(); fk.data = key.data.copy(); fk.name = 'R3_FaceKey_Soft_Linked'; fk.data.name = fk.name
    fk.data.energy = key.data.energy * CFG['lights']['key_face_scale']
    inc = bpy.data.collections.new('RO3_B_LightLink_FaceKeyOctopusOnly'); inc.objects.link(fig)
    fk.light_linking.receiver_collection = inc
    sc.collection.objects.link(fk)
    rep['lights'] = dict(key=key.name, key_energy=key.data.energy, key_excludes=fig.name, face_key=fk.name, face_key_energy=round(fk.data.energy, 3))

    # 4) dressing moves (render-only palms/rocks)
    moved = {}
    for nm, xy in CFG.get('dressing_moves', {}).items():
        ob = bpy.data.objects[nm]
        if xy is None:
            for c in list(ob.users_collection): c.objects.unlink(ob)
            bpy.data.objects.remove(ob); moved[nm] = 'removed'; continue
        loc, *_ = BVH.ray_cast(Vector((xy[0], xy[1], 500)), Vector((0, 0, -1)))
        ob.location = (xy[0], xy[1], loc.z); moved[nm] = [round(c, 2) for c in ob.location]
    rep['dressing_moves'] = moved

    # 5) golf cluster
    gc = bpy.data.collections.new('RO3_B_GolfGreen_RenderOnly')
    env = bpy.data.collections.get('RENDER_ONLY_Environment_R2')
    (env.children if env else bpy.data.scenes[sc.name].collection.children).link(gc)
    if gc not in sc.collection.children_recursive: sc.collection.children.link(gc)
    golf, ginfo = build_green(sc, cam, BVH, CFG['green'], gc)
    for o in golf: o['RENDER_ONLY'] = 'thumbnail staging - not a live playable asset'

    # 6) projections (whole-green-in-frame, face separation, title zone)
    face = uv_ext(sc, cam, [fig])
    gr = uv_ext(sc, cam, [golf[0]]); fl = uv_ext(sc, cam, golf[1:4]); ba = uv_ext(sc, cam, [golf[4]])
    ship = uv_ext(sc, cam, [o for o in sc.objects if o.type == 'MESH' and any(c.name in ('Visual', 'Props', 'Ramps', 'RO2_ShipVisual_NoPier') for c in o.users_collection)])
    eyes = uv_ext(sc, cam, [bpy.data.objects['ShipV5_BowEyes']])
    overlap = lambda p, q: not (p['u'][1] < q['u'][0] or q['u'][1] < p['u'][0] or p['v'][1] < q['v'][0] or q['v'][1] < p['v'][0])
    rep['projection'] = dict(green=gr, flag_pole_cup=fl, ball=ba, figurehead=face, ship=ship, bow_eyes=eyes,
                             green_margin=dict(left=gr['u'][0], right=round(1 - gr['u'][1], 4), bottom=gr['v'][0], top=round(1 - gr['v'][1], 4)),
                             flag_overlaps_figurehead_bbox=overlap(fl, face), green_overlaps_figurehead_bbox=overlap(gr, face))
    rep['golf'] = ginfo
    rep['camera'] = dict(name=cam.name, spec=CFG['camera'], base='round-2 scene A camera (Thumbnail_A_Hero_R2)', location=[round(c, 2) for c in cam.matrix_world.translation],
                         rotation_deg=[round(math.degrees(c), 2) for c in cam.matrix_world.to_euler()], lens=cam.data.lens)
    rep['scenes'] = [s.name for s in bpy.data.scenes]
    print('PROJ', json.dumps(rep['projection']))

    bpy.ops.file.pack_all()
    if A.output in (A.source, A.approved): raise SystemExit('refusing to overwrite an input')
    os.makedirs(os.path.dirname(A.output), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=A.output, copy=True, compress=True)
    rep['source']['sha256_after'] = sha(A.source); rep['approved']['sha256_after'] = sha(A.approved)
    os.makedirs(os.path.dirname(A.report), exist_ok=True)
    json.dump(rep, open(A.report, 'w'), indent=1, default=list)
    print('BUILD_ROUND3_OK', A.output)


try:
    main()
except SystemExit:
    raise
except Exception:
    import traceback; traceback.print_exc(); sys.exit(1)
