# validate_round3.py - checks + manifest for the round-3 B lead thumbnail (run in Blender, factory startup).
#   blender -b --factory-startup --python-exit-code 1 --python out/src/validate_round3.py -- --source inputs/pirate_thumbnail_round2.blend \
#     --approved inputs/start_ship_whimsy_v5_1.blend --output out/pirate_thumbnail_round3.blend --previews out/previews \
#     --report out/logs/build_report_r3.json --manifest out/manifest.json
# Exit code 1 if any check fails.
import bpy, os, sys, json, hashlib, argparse
import numpy as np
from bpy_extras.object_utils import world_to_camera_view as w2c

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser()
for k in ('source', 'approved', 'output', 'previews', 'report', 'manifest'):
    p.add_argument('--' + k, required=True)
p.add_argument('--expected-source-sha', default='3837fadb44409dc64d9b7a20ea07aa7bc3fb502c58001853141eaa14edee9d43')
p.add_argument('--expected-approved-sha', default='fd7798af4ca9bd107dba927bdf663e7017c04f8c4c7649b518b5c78c8d4bcacd')
p.add_argument('--scene', default='Thumbnail_B_Lead_R3')
a = p.parse_args(argv)
for k in ('source', 'approved', 'output', 'previews', 'report', 'manifest'):
    setattr(a, k, os.path.abspath(getattr(a, k)))
SHIP_COLS = ('Visual', 'Props', 'Ramps')
SIZES = {'B_round3.png': (1280, 720), 'B_round3_320x180.png': (320, 180), 'B_round3_160x90.png': (160, 90),
         'B_round3_gray.png': (1280, 720), 'B_round3_320x180_gray.png': (320, 180), 'B_round3_160x90_gray.png': (160, 90),
         'round2_vs_round3_small_comparison.png': None}
GOLF = ('RO3_RenderOnly_PuttingGreen', 'RO3_RenderOnly_Cup', 'RO3_RenderOnly_FlagPole', 'RO3_RenderOnly_FlagCloth', 'RO3_RenderOnly_GolfBall')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def h_arr(x):
    return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()[:16]


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
                 matrix_parent_inverse=[round(x, 5) for r in o.matrix_parent_inverse for x in r],
                 matrix=None if is_col else [round(x, 5) for r in o.matrix_world for x in r],
                 parent=o.parent.name if o.parent else None, modifiers=[(m.type, m.name) for m in o.modifiers])
        if o.type == 'MESH':
            me = o.data
            co = np.zeros(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co)
            lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
            mi = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
            s.update(verts=len(me.vertices), polys=len(me.polygons), co=h_arr(co), loops=h_arr(lv), mat_index=h_arr(mi),
                     materials=[mat_sig(m) for m in me.materials])
        out[o.name] = s
    return out


def uv_ext(sc, cam, objs):
    us, vs = [], []
    for o in objs:
        M = o.matrix_basis if o.parent is None else o.matrix_world   # unparented staging: basis is current in an unevaluated file
        for vt in o.data.vertices:
            q = w2c(sc, cam, M @ vt.co)
            if q.z > 0:
                us.append(q.x); vs.append(q.y)
    return dict(u=[round(min(us), 4), round(max(us), 4)], v=[round(min(vs), 4), round(max(vs), 4)])


def main():
    C = {}
    rep = json.load(open(a.report))
    src_now, app_now = sha(a.source), sha(a.approved)
    C['source_sha256_unchanged'] = dict(ok=src_now == rep['source']['sha256_before'] == rep['source']['sha256_after'] == a.expected_source_sha,
                                        now=src_now, expected=a.expected_source_sha)
    C['approved_sha256_unchanged'] = dict(ok=app_now == rep['approved']['sha256_before'] == rep['approved']['sha256_after'] == a.expected_approved_sha,
                                          now=app_now, expected=a.expected_approved_sha)

    bpy.ops.wm.open_mainfile(filepath=a.approved, load_ui=False)
    app_sig = signature()
    ship_names = sorted({o.name for c in SHIP_COLS if c in bpy.data.collections for o in bpy.data.collections[c].objects})
    bpy.ops.wm.open_mainfile(filepath=a.output, load_ui=False)
    out_sig = signature(set(app_sig))
    diffs = [(n, 'missing') for n in app_sig if n not in out_sig]
    diffs += [(n, k) for n, s in app_sig.items() if n in out_sig for k, v in s.items() if out_sig[n].get(k) != v]
    C['authentic_ship_unchanged_vs_approved'] = dict(ok=not diffs, compared_objects=len(app_sig), diffs=diffs[:40],
        compared='mesh co/loop/material-index hashes, basis transforms + deltas + parent inverse, matrix_world (non-Collision), parent, modifiers, material node values')

    imgs = [i for i in bpy.data.images if i.source == 'FILE']
    unpacked = [i.name for i in imgs if i.packed_file is None]
    C['images_packed'] = dict(ok=not unpacked, file_images=len(imgs), unpacked=unpacked)

    thumbs = [s.name for s in bpy.data.scenes if s.name.startswith('Thumbnail_')]
    sc = bpy.data.scenes.get(a.scene)
    C['single_thumbnail_scene'] = dict(ok=(thumbs == [a.scene] and sc is not None and sc.camera is not None and sc.camera.name == a.scene),
                                       scenes=[s.name for s in bpy.data.scenes], thumbnail_scenes=thumbs, camera=sc.camera.name if sc and sc.camera else None,
                                       note="'Scene' = untouched original scene carried from the approved ship file; not a thumbnail")
    vis = set(o.name for o in sc.objects)
    left = [n for n in vis if any(t in n for t in ('GolfBall', 'Putter', 'Sandbar')) and not n.startswith('RO3_RenderOnly_')]
    gone = not any(n in bpy.data.objects for n in ('RO2_B_GolfBall', 'RO2_B_Putter', 'RO2_B_Sandbar', 'RO2_A_GolfBall', 'RO2_A_Putter'))
    C['round2_giant_ball_putter_removed'] = dict(ok=(not left) and gone, leftovers=left)
    C['collision_not_in_scene'] = dict(ok=not any(c.name == 'Collision' for c in sc.collection.children_recursive))

    cam = sc.camera
    cam.matrix_world = cam.matrix_basis.copy()   # unevaluated file (thumbnail scene is not the window scene): refresh the unparented camera
    golf =[bpy.data.objects[n] for n in GOLF]
    gr = uv_ext(sc, cam, golf[:1])
    fig = uv_ext(sc, cam, [bpy.data.objects['Prop_Figurehead']])
    flag = uv_ext(sc, cam, golf[2:4])
    margin = min(gr['u'][0], 1 - gr['u'][1], gr['v'][0], 1 - gr['v'][1])
    C['whole_green_in_frame'] = dict(ok=margin >= 0.04, green_uv=gr, min_margin_frac=round(margin, 4), required_margin_frac=0.04,
                                     margin_px_1280x720=dict(left=round(gr['u'][0] * 1280), right=round((1 - gr['u'][1]) * 1280),
                                                             bottom=round(gr['v'][0] * 720), top=round((1 - gr['v'][1]) * 720)))
    hit = not (flag['u'][1] < fig['u'][0] or fig['u'][1] < flag['u'][0] or flag['v'][1] < fig['v'][0] or fig['v'][1] < flag['v'][0])
    C['flag_clear_of_figurehead'] = dict(ok=not hit, flag_pole_uv=flag, figurehead_uv=fig, vertical_gap_frac=round(fig['v'][0] - flag['v'][1], 4))

    sizes = {}
    for fn in SIZES:
        im = bpy.data.images.load(os.path.join(a.previews, fn)); sizes[fn] = list(im.size)
        if fn == 'B_round3.png':
            px = np.array(im.pixels[:], np.float32).reshape(im.size[1], im.size[0], im.channels)[::-1]
            x0, x1 = int(gr['u'][0] * 1280), int(gr['u'][1] * 1280); y0, y1 = int((1 - gr['v'][1]) * 720), int((1 - gr['v'][0]) * 720)
            box = px[y0:y1, x0:x1, :3]
            turf = (box[..., 1] > box[..., 0] * 1.3) & (box[..., 1] > box[..., 2] * 1.3) & (box[..., 1] > 0.3)
            C['green_rendered_pixels'] = dict(ok=int(turf.sum()) > 5000, turf_pixels_in_green_bbox=int(turf.sum()), bbox_px=[x0, y0, x1, y1],
                                              bbox_area_px=int((x1 - x0) * (y1 - y0)))
        bpy.data.images.remove(im)
    C['output_sizes'] = dict(ok=all(wh is None or sizes[fn] == list(wh) for fn, wh in SIZES.items()), sizes=sizes)

    staged = {}
    for o in sc.objects:
        if o.name in ship_names:
            continue
        kind = ('golf_render_only' if o.name.startswith('RO3_RenderOnly_') else 'dressing_render_only' if '_kit_' in o.name
                else 'environment_render_only' if o.name.startswith('RO_') else o.type.lower())
        staged.setdefault(kind, []).append(o.name)
    ok = all(v['ok'] for v in C.values())
    tris = lambda o: sum(len(q.vertices) - 2 for q in o.data.polygons)
    authentic = [n for n in ship_names if n in vis]
    manifest = dict(
        deliverable='Pirate Shipwreck marketing thumbnail ROUND 3 sketch follow-up - single lead image B_round3 on the round-2 A frame, for independent Art + Playtest critique (not approved)',
        files=dict(blend='pirate_thumbnail_round3.blend (compressed, all file images packed)', previews=sorted(os.listdir(a.previews))),
        inputs=dict(round2_blend=dict(path='inputs/pirate_thumbnail_round2.blend', commit='d0dd39a', sha256=src_now),
                    approved_ship=dict(path='inputs/start_ship_whimsy_v5_1.blend', sha256=app_now),
                    scene_export_manifest=dict(path='inputs/scene_export_manifest.json',
                                               use='read only; not used for reconstruction. Edit-session export Nov 7 2:51 PM PT, PlaceVersion 0 - not a certified published version or live mesh equality')),
        scene=a.scene,
        camera=dict(rep['camera'], round2_A_base=rep.get('camera_base_round2_A'), change='sketch follow-up: round-2 scene A camera kept exactly (no tweak); the first round-3 pass used a raised round-2 B camera, now dropped'),
        sketch=dict(path='inputs/chase_green_placement.png', use='visual reference only (red annotation not reproduced): A frame, green oval lower-right u~0.70-0.96 v~0.05-0.25, flag rising beside bow, face clear'),
        render=dict(engine=sc.render.engine, device=sc.cycles.device, samples=sc.cycles.samples, resolution=[sc.render.resolution_x, sc.render.resolution_y],
                    view_transform=sc.view_settings.view_transform, exposure=round(sc.view_settings.exposure, 3)),
        lights=[dict(name=o.name, energy=round(o.data.energy, 3), receivers=(o.light_linking.receiver_collection.name if o.light_linking.receiver_collection else None))
                for o in sc.objects if o.type == 'LIGHT'],
        authentic=dict(note='approved ship objects, unchanged (see checks). Collision collection is in the file but not linked into the thumbnail scene.',
                       objects=authentic, count=len(authentic)),
        staged_render_only=dict(note='RENDER_ONLY thumbnail staging: cove terrain/water, palms/rocks dressing, light rig and the golf cluster. NOT game assets, NOT a live or playable hole.',
                                counts={k: len(v) for k, v in staged.items()}, groups={k: sorted(v) for k, v in staged.items()},
                                golf=dict(rep['golf'], object_tris={o.name: tris(o) for o in golf}), dressing_moves=rep.get('dressing_moves')),
        removed_from_round2=rep['removed'], build_projection=rep['projection'], checks=C, all_checks_ok=ok)
    json.dump(manifest, open(a.manifest, 'w'), indent=1, default=list)
    for k, v in C.items():
        print('CHECK', k, 'OK' if v['ok'] else 'FAIL')
    print('VALIDATE_ROUND3_' + ('OK' if ok else 'FAIL'))
    return ok


try:
    ok = main()
except Exception:
    import traceback; traceback.print_exc(); sys.exit(1)
sys.exit(0 if ok else 1)
