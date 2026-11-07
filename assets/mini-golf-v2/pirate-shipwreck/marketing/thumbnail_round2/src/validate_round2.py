# validate_round2.py - checks + measurements + manifest for round 2. Run AFTER build, both renders and make_downsamples.py:
#   blender -b --factory-startup --python-exit-code 1 --python out/src/validate_round2.py -- \
#       --source inputs/pirate_thumbnail_round1.blend --approved inputs/start_ship_whimsy_v5_1.blend \
#       --output out/pirate_thumbnail_round2.blend
# * authentic ship: every object of the APPROVED ship file is compared with the same-named object in the output (mesh vertex
#   coordinate / loop / material-index hashes, basis transforms + parent inverse, matrix_world (non-Collision), parent,
#   modifiers, material node values). Input SHA-256s are checked against the build-time values and the expected approved SHA.
# * scenes / saved cameras / Collision not linked / Pier hidden in A only via collection links / packed images / PNG sizes.
# * projected measurements per scene (0..1 image coords, y up): ship extents, octopus heights, bowsprit-curl in-frame margin,
#   golf ball projected height, title-zone intrusions (geometry), title-zone pixel calm, coral + hull pixel medians.
import bpy, os, sys, json, hashlib, argparse, math
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view as w2c

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(OUTDIR, '..'))
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument('--source', default=os.path.join(ROOT, 'inputs', 'pirate_thumbnail_round1.blend'))
p.add_argument('--approved', default=os.path.join(ROOT, 'inputs', 'start_ship_whimsy_v5_1.blend'))
p.add_argument('--output', default=os.path.join(OUTDIR, 'pirate_thumbnail_round2.blend'))
p.add_argument('--report', default=os.path.join(OUTDIR, 'build', 'build_report_r2.json'))
p.add_argument('--previews', default=os.path.join(OUTDIR, 'previews'))
p.add_argument('--manifest', default=os.path.join(OUTDIR, 'manifest.json'))
p.add_argument('--expected-approved-sha', default='fd7798af4ca9bd107dba927bdf663e7017c04f8c4c7649b518b5c78c8d4bcacd')
p.add_argument('--expected-source-sha', default='411e594f2bcd55c5c05a25cbd15cbdd8bcba98f10ca65e50bb4224c91e6c12ce')
p.add_argument('--measure-only', action='store_true', help='skip PNG checks (quick proofs)')
a = p.parse_args(argv)
for _k in ('source', 'approved', 'output', 'report', 'previews', 'manifest'):
    setattr(a, _k, os.path.abspath(getattr(a, _k)))

SCN = {'A': 'Thumbnail_A_Hero_R2', 'B': 'Thumbnail_B_Octopus_R2'}
TITLE = dict(u=[0.05, 0.40], v=[0.65, 0.95])     # upper-left title area, 5% margins (y up)
SIZES = {'': (1280, 720), '_320x180': (320, 180), '_160x90': (160, 90)}


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def h_arr(arr):
    return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()[:16]


def mat_sig(m):
    if m is None:
        return None
    d = [m.name]
    if m.node_tree:
        for n in sorted(m.node_tree.nodes, key=lambda n: n.name):
            for i in n.inputs:
                if hasattr(i, 'default_value'):
                    v = i.default_value
                    try:
                        v = [round(float(x), 5) for x in v]
                    except TypeError:
                        v = round(float(v), 5) if isinstance(v, (int, float)) else str(v)
                    d.append((n.type, n.name, i.identifier, v))
            if n.type == 'TEX_IMAGE' and n.image:
                d.append(('img', n.image.name, n.interpolation))
    return hashlib.sha256(json.dumps(d, default=str).encode()).hexdigest()[:16]


def signature(names=None):
    out = {}
    for o in bpy.data.objects:
        if names is not None and o.name not in names:
            continue
        is_col = o.name.startswith('COL_') or any(c.name == 'Collision' for c in o.users_collection)
        s = dict(type=o.type, basis=[round(x, 5) for x in (*o.location, *o.rotation_euler, *o.scale, *o.delta_location, *o.delta_rotation_euler, *o.delta_scale)],
                 rotation_mode=o.rotation_mode, matrix_parent_inverse=[round(x, 5) for r in o.matrix_parent_inverse for x in r],
                 matrix=None if is_col else [round(x, 5) for r in o.matrix_world for x in r],
                 parent=o.parent.name if o.parent else None, modifiers=[(m.type, m.name) for m in o.modifiers])
        if o.type == 'MESH':
            me = o.data
            co = np.zeros(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co)
            lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
            mi = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
            s.update(verts=len(me.vertices), polys=len(me.polygons), tris=int(sum(len(q.vertices) - 2 for q in me.polygons)),
                     co=h_arr(co), loops=h_arr(lv), mat_index=h_arr(mi), materials=[mat_sig(m) for m in me.materials])
        out[o.name] = s
    return out


def load_png(path):
    im = bpy.data.images.load(path)
    w, h = im.size
    px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, im.channels)[::-1]   # top-down rows, stored values 0..1
    ch = im.channels
    bpy.data.images.remove(im)
    return px, (w, h), ch


def uv_pts(sc, cam, objs, pred=None, step=1):
    pts = []
    for o in objs:
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
    us = [q[0] for q in pts]; vs = [q[1] for q in pts]
    return dict(u=[round(min(us), 4), round(max(us), 4)], v=[round(min(vs), 4), round(max(vs), 4)],
                width=round(max(us) - min(us), 4), height=round(max(vs) - min(vs), 4))


def in_title(q):
    return TITLE['u'][0] <= q[0] <= TITLE['u'][1] and TITLE['v'][0] <= q[1] <= TITLE['v'][1]


R = dict(checks={}, measurements={})
try:
    rep = json.load(open(a.report))
    src_before, app_before = rep['source']['sha256_before'], rep['approved']['sha256_before']
    src_now, app_now = sha(a.source), sha(a.approved)
    R['checks']['approved_sha256'] = dict(ok=(app_before == app_now == a.expected_approved_sha), expected=a.expected_approved_sha,
                                          before_build=app_before, after_build=rep['approved']['sha256_after'], now=app_now)
    R['checks']['round1_source_sha256'] = dict(ok=(src_before == src_now == rep['source']['sha256_after'] == a.expected_source_sha),
                                               expected=a.expected_source_sha, before_build=src_before, after_build=rep['source']['sha256_after'], now=src_now)

    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.approved), load_ui=False)
    app_sig = signature()
    app_cols = {c.name: len(c.objects) for c in bpy.data.collections}
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.output), load_ui=False)
    out_sig = signature(set(app_sig))
    diffs = []
    for nm, s in app_sig.items():
        if nm not in out_sig:
            diffs.append((nm, 'missing')); continue
        for k, v in s.items():
            if out_sig[nm].get(k) != v:
                diffs.append((nm, k))
    R['checks']['authentic_ship_unchanged_vs_approved'] = dict(
        ok=not diffs, compared_objects=len(app_sig),
        compared='mesh vertex-coordinate/loop/material-index hashes, basis transforms (loc/rot/scale/deltas/parent inverse), matrix_world (non-Collision), parent, modifiers, material node values',
        note='Collision objects: stored matrix_world cache is stale in the source (never evaluated); their basis transforms are compared',
        diffs=diffs[:50])

    # scenes / cameras
    cams = {}
    for k, nm in SCN.items():
        sc = bpy.data.scenes.get(nm)
        cams[nm] = dict(scene=bool(sc), camera=sc.camera.name if sc and sc.camera else None,
                        camera_saved=bool(sc and sc.camera and sc.camera.name in sc.objects),
                        collision_linked=bool(sc and any(c.name == 'Collision' for c in sc.collection.children_recursive)),
                        pier_in_scene=bool(sc and 'Pier' in sc.objects),
                        view_transform=sc.view_settings.view_transform if sc else None, look=sc.view_settings.look if sc else None,
                        exposure=round(sc.view_settings.exposure, 3) if sc else None, engine=sc.render.engine if sc else None,
                        device=sc.cycles.device if sc else None, samples=sc.cycles.samples if sc else None,
                        resolution=[sc.render.resolution_x, sc.render.resolution_y] if sc else None)
    other = [s.name for s in bpy.data.scenes if s.name not in SCN.values()]
    R['checks']['scenes_and_cameras'] = dict(
        ok=all(v['camera'] == nm and v['camera_saved'] and not v['collision_linked'] for nm, v in cams.items())
           and not cams[SCN['A']]['pier_in_scene'] and 'Thumbnail_C_Adventure' not in [s.name for s in bpy.data.scenes],
        scenes=cams, other_scenes=other, note="'Scene' = untouched original scene from the approved ship file (not a thumbnail)")
    R['checks']['helpers_render_hidden'] = dict(ok=all(o.hide_render for o in bpy.data.objects if o.type == 'EMPTY'))
    imgs = [(i.name, i.packed_file is not None) for i in bpy.data.images if i.source == 'FILE']
    R['checks']['images_packed'] = dict(ok=all(pk for _, pk in imgs), images=imgs)

    fig = bpy.data.objects['Prop_Figurehead']; hull = bpy.data.objects['Hull']
    ship_main = [bpy.data.objects[n] for n in ('Hull', 'DeckCabin', 'Rigging')] + list(bpy.data.collections['Props'].objects)
    curl_pred = lambda w: w.x > 177 and w.z > 56
    meas = {}
    for k, nm in SCN.items():
        sc = bpy.data.scenes[nm]; cam = sc.camera
        vl = sc.view_layers[0]; vl.update(); dg = vl.depsgraph
        m = {}
        m['ship_hull_rig_props'] = ext(uv_pts(sc, cam, ship_main, step=3))
        m['ramps'] = ext(uv_pts(sc, cam, list(bpy.data.collections['Ramps'].objects)))
        m['octopus_full'] = ext(uv_pts(sc, cam, [fig]))
        m['octopus_head_mantle_face_z27_52'] = ext(uv_pts(sc, cam, [fig], pred=lambda w: 27 <= w.z < 52))
        m['octopus_body_below_curl_z_lt52'] = ext(uv_pts(sc, cam, [fig], pred=lambda w: w.z < 52))
        cu = ext(uv_pts(sc, cam, [hull, fig, bpy.data.objects['Rigging']], pred=curl_pred))
        cu['min_margin'] = round(min(cu['u'][0], cu['v'][0], 1 - cu['u'][1], 1 - cu['v'][1]), 4)
        cu['inside_frame'] = cu['min_margin'] > 0
        m['bowsprit_curl_tip'] = cu
        golf = [o for o in sc.objects if o.name.startswith('RO2_%s_' % k) and ('GolfBall' in o.name or 'Putter' in o.name)]
        ball = next(o for o in golf if 'GolfBall' in o.name); putter = next(o for o in golf if 'Putter' in o.name)
        m['golf_ball'] = ext(uv_pts(sc, cam, [ball], step=7)); m['golf_ball']['radius_studs'] = round(ball.scale.x, 3)
        m['golf_ball']['center_world'] = [round(x, 2) for x in ball.location]
        m['golf_ball']['bottom_z_vs_water_z1'] = round(ball.location.z - ball.scale.x, 2)
        m['putter'] = ext(uv_pts(sc, cam, [putter], step=1))
        # title-zone intrusions by any rendered geometry (vertices; thin ropes are cylinders so their vertices are caught)
        allobj = [o for o in sc.objects if o.type == 'MESH' and not o.hide_render and o.name not in ('RO_CoveTerrain', 'RO_WaterSurface', 'RO_SeaFloorFar')]
        hits = {}
        for o in allobj:
            n_in = sum(1 for q in uv_pts(sc, cam, [o], step=1 if len(o.data.vertices) < 20000 else 5) if in_title(q))
            if n_in: hits[o.name] = n_in
        m['title_zone_geometry_intrusions'] = hits
        # camera
        m['camera'] = dict(name=cam.name, location=[round(x, 2) for x in cam.matrix_world.translation], lens=cam.data.lens,
                           shift=[cam.data.shift_x, cam.data.shift_y], rotation_deg=[round(math.degrees(x), 2) for x in cam.matrix_world.to_euler()])
        # visible coral samples (ray-cast from the camera; first hit must be the figurehead)
        org = cam.matrix_world.translation
        samp = {'Coral': [], 'CoralDk': [], 'HullWood': [], 'Canvas_sails': []}
        targets = [(fig, ('Coral', 'CoralDk')), (hull, ('HullWood',)), (bpy.data.objects['Rigging'], ('Canvas',))]
        for ob, keys in targets:
            M = ob.matrix_world; mats = [mm.name for mm in ob.data.materials]
            for poly in ob.data.polygons:
                mn = mats[poly.material_index]
                if mn not in keys: continue
                c = M @ poly.center
                if mn == 'HullWood' and c.z < 4.0: continue      # below/at the waterline: seen through tinted water
                d = (c - org); dist = d.length; d.normalize()
                ok, loc, nrm, idx, hob, _ = sc.ray_cast(dg, org, d, distance=dist + 0.5)
                if not ok or hob.name != ob.name or (loc - c).length > 1.0: continue
                q = w2c(sc, cam, c)
                if 0 < q.x < 1 and 0 < q.y < 1:
                    samp['Canvas_sails' if mn == 'Canvas' else mn].append((q.x, q.y))
        m['_samples'] = samp
        meas[k] = m
    R['measurements'] = meas

    if not a.measure_only:
        pngs = {}
        for k in SCN:
            for suf, size in SIZES.items():
                for g in ('', '_gray'):
                    fn = '%s_round2%s%s.png' % (k, suf, g)
                    fp = os.path.join(a.previews, fn)
                    if os.path.exists(fp):
                        px, wh, ch = load_png(fp)
                        pngs[fn] = dict(size=list(wh), channels=ch, ok=list(wh) == list(size), sha256=sha(fp))
                    else:
                        pngs[fn] = dict(ok=False, missing=True)
        R['checks']['previews'] = dict(ok=all(v['ok'] for v in pngs.values()), files=pngs)
        for k in SCN:
            px, (w, h), ch = load_png(os.path.join(a.previews, '%s_round2.png' % k))
            m = meas[k]
            def pix(q):
                x = min(w - 1, max(0, int(q[0] * w))); y = min(h - 1, max(0, int((1 - q[1]) * h)))
                return px[y, x, :3] * 255.0
            for key, pts in m['_samples'].items():
                if pts:
                    arr = np.array([pix(q) for q in pts])
                    m['pixel_srgb_' + key] = dict(median=[int(x) for x in np.median(arr, 0)], p90=[int(x) for x in np.percentile(arr, 90, 0)], n=len(pts),
                                                  clipped_frac=round(float(np.mean(np.max(arr, 1) >= 254)), 3))
            x0, x1 = int(TITLE['u'][0] * w), int(TITLE['u'][1] * w); y0, y1 = int((1 - TITLE['v'][1]) * h), int((1 - TITLE['v'][0]) * h)
            zone = px[y0:y1, x0:x1, :3] * 255.0
            lum = zone @ np.array([0.2126, 0.7152, 0.0722])
            gy, gx = np.gradient(lum)
            m['title_zone_pixels'] = dict(mean_srgb=[int(x) for x in zone.reshape(-1, 3).mean(0)], lum_std=round(float(lum.std()), 2),
                                          max_local_gradient=round(float(np.max(np.hypot(gx, gy))), 2))
            m['frame_clipped_frac'] = round(float(np.mean(np.max(px[..., :3], 2) >= 254 / 255.0)), 4)
    for m in meas.values():
        m.pop('_samples', None)

    # summary checks on measurements
    R['checks']['b_curl_tip_inside_frame'] = dict(ok=meas['B']['bowsprit_curl_tip']['inside_frame'], margin=meas['B']['bowsprit_curl_tip']['min_margin'])
    R['checks']['ball_size_A_12_15pct'] = dict(ok=0.12 <= meas['A']['golf_ball']['height'] <= 0.15, measured=meas['A']['golf_ball']['height'])
    R['checks']['ball_size_B_15_18pct'] = dict(ok=0.15 <= meas['B']['golf_ball']['height'] <= 0.18, measured=meas['B']['golf_ball']['height'])
    R['checks']['ball_above_water'] = dict(ok=all(meas[k]['golf_ball']['bottom_z_vs_water_z1'] > 1.0 for k in SCN))
    R['checks']['title_zone_geometry_clear'] = dict(ok=all(not meas[k]['title_zone_geometry_intrusions'] for k in SCN),
                                                    zone='u %.2f-%.2f, v %.2f-%.2f (y up)' % (TITLE['u'][0], TITLE['u'][1], TITLE['v'][0], TITLE['v'][1]))
    R['ok'] = all(c['ok'] for c in R['checks'].values())
    print('MEASURE', json.dumps(meas, indent=1))
    print('VALIDATION', json.dumps({k: v['ok'] for k, v in R['checks'].items()}), 'ALL_OK' if R['ok'] else 'FAILED')

    if not a.measure_only:
        man = dict(job='Pirate ship thumbnails ROUND 2 (revised A hero / B octopus) after round-1 Art+Playtest critique; proofs for an independent second critique, not final',
                   status='round2 delivered (A/B only, C dropped); STOP - waiting for independent second critique',
                   inputs=dict(approved_ship=dict(path='inputs/start_ship_whimsy_v5_1.blend', sha256_before=app_before, sha256_after=app_now,
                                                  objects=len(app_sig), collections=app_cols),
                               round1_source=dict(path='inputs/pirate_thumbnail_round1.blend', sha256_before=src_before, sha256_after=src_now)),
                   output=dict(path='out/pirate_thumbnail_round2.blend', sha256=sha(a.output), bytes=os.path.getsize(a.output), packed=True,
                               scenes=list(SCN.values()), other_scenes=other),
                   authentic_vs_staged=dict(
                       authentic=dict(collections=['Visual', 'Props', 'Ramps'], objects=len(app_sig),
                                      note='approved ship objects, unchanged (see validation). Collision collection present in the file but not linked into thumbnail scenes. Pier object/mesh kept; only not linked into scene A or B.'),
                       staged_render_only=dict(collection='RENDER_ONLY_Environment_R2',
                                               items=['RO_CoveTerrain / RO_WaterSurface / RO_SeaFloorFar / RO_TropicalSky world (round-1 staged cove, unchanged)',
                                                      'per-scene kit dressing (original kit_v1 / kit_v22 meshes, new placements)',
                                                      'RO2_<A|B>_GolfBall + RO2_<A|B>_Putter (+ RO2_B_Sandbar) render-only identity props',
                                                      'per-scene sun key / shadowless fill / cool rim / ship-linked warm fill lights'],
                                               placed_kit_instances=rep['placed'],
                                               counts=dict(A=sum(1 for q in rep['placed'] if q['scene'] == SCN['A']), B=sum(1 for q in rep['placed'] if q['scene'] == SCN['B']),
                                                           palms_A=sum(1 for q in rep['placed'] if q['scene'] == SCN['A'] and 'palm' in q['prop']),
                                                           palms_B=sum(1 for q in rep['placed'] if q['scene'] == SCN['B'] and 'palm' in q['prop'])),
                                               golf_ball=rep['golf_ball'], putter=rep['putter'],
                                               honesty='No cup, flag, hole, shot trail, avatar, score or playable-course claim. Environment is staged, not the v31 game layout.')),
                   scenes=rep['scenes'], removed_round1_staging=rep['removed_round1_staging'],
                   measurements=meas, validation=R)
        json.dump(man, open(a.manifest, 'w'), indent=1, default=lambda o: list(o) if hasattr(o, '__iter__') else str(o))
    sys.exit(0 if R['ok'] else 1)
except SystemExit:
    raise
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
