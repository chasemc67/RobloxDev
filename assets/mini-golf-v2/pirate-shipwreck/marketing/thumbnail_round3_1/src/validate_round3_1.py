# validate_round3_1.py - checks + manifest for the R3.1 polish (run in Blender, factory startup). Exit 1 if any check fails.
#   blender -b --factory-startup --python-exit-code 1 --python validate_round3_1.py -- --source <inputs/pirate_thumbnail_round3.blend> \
#     --output <out/pirate_thumbnail_round3_1.blend> --previews <out/previews> --polish-report <out/logs/polish_report.json> --manifest <out/manifest.json>
# Compares EVERY object/material/light/world/camera/render setting of the source vs output; only the five golf render-only objects may differ,
# and only in the documented way (green: vertex Z only; cup/pole/ball: location Z only; cloth: vertex positions only).
import bpy, os, sys, json, hashlib, argparse
import numpy as np
from bpy_extras.object_utils import world_to_camera_view as w2c

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser()
for k in ('source', 'output', 'previews', 'polish_report', 'manifest'):
    p.add_argument('--' + k.replace('_', '-'), dest=k, required=True)
p.add_argument('--expected-source-sha', default='308623f2bae9139693273b487f7013da04db707985e2618040140f614f249085')
p.add_argument('--scene', default='Thumbnail_B_Lead_R3')
a = p.parse_args(argv)
for k in ('source', 'output', 'previews', 'polish_report', 'manifest'):
    setattr(a, k, os.path.abspath(getattr(a, k)))
STEM = 'B_round3_1'
SIZES = {}
for w, h in ((1920, 1080), (1280, 720), (320, 180), (160, 90)):
    SIZES['%s_%dx%d.png' % (STEM, w, h)] = (w, h); SIZES['%s_%dx%d_gray.png' % (STEM, w, h)] = (w, h)
GREEN, CUP, POLE, CLOTH, BALL = ('RO3_RenderOnly_PuttingGreen', 'RO3_RenderOnly_Cup', 'RO3_RenderOnly_FlagPole', 'RO3_RenderOnly_FlagCloth', 'RO3_RenderOnly_GolfBall')
GOLF = (GREEN, CUP, POLE, CLOTH, BALL)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def h_arr(x):
    return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()[:16]


def rnas(idb, skip=()):
    d = {}
    for pr in idb.bl_rna.properties:
        if pr.identifier in skip or pr.identifier in ('rna_type', 'session_uid', 'is_evaluated', 'original', 'users', 'is_runtime_data',
                                                       'tag', 'is_missing', 'is_embedded_data', 'is_library_indirect', 'name_full', 'id_type'):
            continue
        try:
            v = getattr(idb, pr.identifier)
        except Exception:
            continue
        if pr.type in ('BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'):
            try:
                v = [round(x, 6) if isinstance(x, float) else x for x in v] if getattr(pr, 'array_length', 0) else (round(v, 6) if isinstance(v, float) else v)
            except TypeError:
                v = str(v)
            d[pr.identifier] = v if not isinstance(v, set) else sorted(v)
        elif pr.type == 'POINTER' and v is not None and hasattr(v, 'name'):
            d[pr.identifier] = v.name
    return d


def node_sig(nt):
    if nt is None:
        return None
    d = []
    for n in sorted(nt.nodes, key=lambda n: n.name):
        d.append((n.type, n.name))
        for i in n.inputs:
            if hasattr(i, 'default_value'):
                v = i.default_value
                try:
                    v = [round(float(x), 6) for x in v]
                except TypeError:
                    v = round(float(v), 6) if isinstance(v, (int, float)) else str(v)
                d.append((i.identifier, v))
        if n.type == 'TEX_IMAGE' and n.image:
            d.append(('img', n.image.name))
    d += sorted((l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier) for l in nt.links)
    return hashlib.sha256(json.dumps(d, default=str).encode()).hexdigest()[:16]


def snapshot():
    S = dict(objects={}, materials={}, lights={}, worlds={}, cameras={}, images={}, scenes={})
    for o in bpy.data.objects:
        s = dict(type=o.type, location=[round(x, 6) for x in o.location], rot=[round(x, 6) for x in o.rotation_euler],
                 rot_mode=o.rotation_mode, quat=[round(x, 6) for x in o.rotation_quaternion], scale=[round(x, 6) for x in o.scale],
                 deltas=[round(x, 6) for x in (*o.delta_location, *o.delta_rotation_euler, *o.delta_scale)],
                 parent=o.parent.name if o.parent else None, mpi=[round(x, 6) for r in o.matrix_parent_inverse for x in r],
                 modifiers=[(m.type, m.name) for m in o.modifiers], data=o.data.name if o.data else None,
                 collections=sorted(c.name for c in o.users_collection), hide_render=o.hide_render, visible_camera=o.visible_camera,
                 visible_shadow=o.visible_shadow, mats=[(sl.link, sl.material.name if sl.material else None) for sl in o.material_slots])
        if o.type == 'MESH':
            me = o.data
            co = np.zeros(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co)
            lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
            mi = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
            s.update(verts=len(me.vertices), polys=len(me.polygons), co=h_arr(co), xy=h_arr(co.reshape(-1, 3)[:, :2]), z=h_arr(co.reshape(-1, 3)[:, 2]),
                     loops=h_arr(lv), mat_index=h_arr(mi), mesh_mats=[m.name if m else None for m in me.materials])
        S['objects'][o.name] = s
    for m in bpy.data.materials:
        S['materials'][m.name] = dict(nodes=node_sig(m.node_tree), **{k: v for k, v in rnas(m).items() if k in ('diffuse_color', 'blend_method', 'use_nodes')})
    for l in bpy.data.lights:
        S['lights'][l.name] = dict(rnas(l), nodes=node_sig(l.node_tree) if getattr(l, 'node_tree', None) else None)
    for w in bpy.data.worlds:
        S['worlds'][w.name] = dict(nodes=node_sig(w.node_tree))
    for c in bpy.data.cameras:
        S['cameras'][c.name] = rnas(c)
    for i in bpy.data.images:
        S['images'][i.name] = dict(source=i.source, packed=i.packed_file is not None, size=list(i.size))
    for sc in bpy.data.scenes:
        S['scenes'][sc.name] = dict(camera=sc.camera.name if sc.camera else None, frame=sc.frame_current, world=sc.world.name if sc.world else None,
                                    render=rnas(sc.render, skip=('filepath',)), cycles=rnas(sc.cycles), view=rnas(sc.view_settings),
                                    objects=sorted(o.name for o in sc.objects), collections=sorted(c.name for c in sc.collection.children_recursive),
                                    props={k: str(sc[k]) for k in sc.keys()})
    return S


def diff(A, B, path=''):
    out = []
    if isinstance(A, dict) and isinstance(B, dict):
        for k in sorted(set(A) | set(B)):
            if k not in A or k not in B:
                out.append((path + '/' + k, 'only in ' + ('output' if k not in A else 'source')))
            else:
                out += diff(A[k], B[k], path + '/' + k)
    elif A != B:
        out.append((path, A, B))
    return out


def main():
    C = {}
    rep = json.load(open(a.polish_report))
    src_now = sha(a.source)
    C['source_sha256_unchanged'] = dict(ok=src_now == rep['source_sha256_before'] == rep['source_sha256_after'] == a.expected_source_sha,
                                        now=src_now, expected=a.expected_source_sha)
    bpy.ops.wm.open_mainfile(filepath=a.source, load_ui=False)
    S0 = snapshot()
    sc0 = bpy.data.scenes[a.scene]; cam0 = sc0.camera
    sc0.view_layers[0].update()   # stored matrix_world can be stale (R3 saved unevaluated); compare evaluated matrices
    cam0_mw = [x for r in cam0.matrix_world for x in r]
    g0 = bpy.data.objects[GREEN].data
    co0 = np.zeros(len(g0.vertices) * 3, np.float64); g0.vertices.foreach_get('co', co0); co0 = co0.reshape(-1, 3)
    cl0 = np.zeros(len(bpy.data.objects[CLOTH].data.vertices) * 3); bpy.data.objects[CLOTH].data.vertices.foreach_get('co', cl0); cl0 = cl0.reshape(-1, 3)
    bpy.ops.wm.open_mainfile(filepath=a.output, load_ui=False)
    S1 = snapshot()
    sc = bpy.data.scenes[a.scene]; cam = sc.camera
    sc.view_layers[0].update()
    d = diff(S0, S1)
    allowed = {('/objects/%s/%s' % (GREEN, k)) for k in ('co', 'z')} | {('/objects/%s/%s' % (CLOTH, k)) for k in ('co', 'xy', 'z')} | \
              {('/objects/%s/location' % n) for n in (CUP, POLE, BALL)}
    unexpected = [x for x in d if x[0] not in allowed]
    C['only_golf_polish_changed'] = dict(ok=not unexpected, all_diffs=[x[0] for x in d], unexpected=unexpected[:40],
                                         compared='all objects (transforms, deltas, parent, modifiers, collections, visibility, material slots, mesh co/xy/z/loops/material-index hashes), '
                                                  'all materials (node/link values), lights, worlds, cameras, images, scenes (render/cycles/view settings, membership, props)')
    for n in (CUP, POLE, BALL):
        l0, l1 = S0['objects'][n]['location'], S1['objects'][n]['location']
        C['%s_xy_kept_z_only' % n] = dict(ok=l0[:2] == l1[:2] and abs((l1[2] - l0[2]) + rep['params']['turf_drop']) < 1e-4, before=l0, after=l1)
    C['camera_exact_r3'] = dict(ok=(S0['cameras'] == S1['cameras'] and S0['objects'][cam.name] == S1['objects'][cam.name]
                                    and cam0_mw == [x for r in cam.matrix_world for x in r] and S0['scenes'][a.scene]['render'] == S1['scenes'][a.scene]['render']
                                    and S0['scenes'][a.scene]['frame'] == S1['scenes'][a.scene]['frame']),
                                camera=cam.name, lens=cam.data.lens, sensor=[cam.data.sensor_fit, cam.data.sensor_width], shift=[cam.data.shift_x, cam.data.shift_y],
                                clip=[cam.data.clip_start, cam.data.clip_end], location=list(cam.matrix_world.translation), rotation_euler=list(cam.matrix_world.to_euler()),
                                frame=sc.frame_current, resolution_in_file=[sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage])
    g1 = bpy.data.objects[GREEN].data
    co1 = np.zeros(len(g1.vertices) * 3, np.float64); g1.vertices.foreach_get('co', co1); co1 = co1.reshape(-1, 3)
    dz = co1[:, 2] - co0[:, 2]
    C['green_footprint_xy_unchanged'] = dict(ok=co0.shape == co1.shape and bool(np.array_equal(co0[:, :2], co1[:, :2])),
                                             verts=len(co1), max_abs_dxy=float(np.abs(co1[:, :2] - co0[:, :2]).max()),
                                             xy_extent=[round(float(co1[:, 0].min()), 3), round(float(co1[:, 0].max()), 3), round(float(co1[:, 1].min()), 3), round(float(co1[:, 1].max()), 3)],
                                             dz_min=round(float(dz.min()), 4), dz_max=round(float(dz.max()), 4), verts_z_changed=int((dz != 0).sum()))
    imgs = [i for i in bpy.data.images if i.source == 'FILE']
    unpacked = [i.name for i in imgs if i.packed_file is None]
    C['images_packed'] = dict(ok=not unpacked, file_images=[i.name for i in imgs], unpacked=unpacked)
    sc.view_layers[0].update()
    def uv_ext(names):
        us, vs = [], []
        for n in names:
            o = bpy.data.objects[n]
            for vt in o.data.vertices:
                q = w2c(sc, cam, o.matrix_world @ vt.co); us.append(q.x); vs.append(q.y)
        return dict(u=[round(min(us), 4), round(max(us), 4)], v=[round(min(vs), 4), round(max(vs), 4)])
    fig = uv_ext(['Prop_Figurehead']); fl = uv_ext([POLE, CLOTH]); gr = uv_ext([GREEN])
    C['flag_below_face'] = dict(ok=fl['v'][1] < fig['v'][0], flag_pole_uv=fl, figurehead_uv=fig, vertical_gap_frac=round(fig['v'][0] - fl['v'][1], 4))
    C['green_in_frame'] = dict(ok=min(gr['u'][0], 1 - gr['u'][1], gr['v'][0], 1 - gr['v'][1]) > 0.02, green_uv=gr)
    cl1 = np.zeros(len(bpy.data.objects[CLOTH].data.vertices) * 3); bpy.data.objects[CLOTH].data.vertices.foreach_get('co', cl1); cl1 = cl1.reshape(-1, 3)
    sizes = {}
    for fn in SIZES:
        fp = os.path.join(a.previews, fn)
        if not os.path.exists(fp):
            sizes[fn] = None; continue
        im = bpy.data.images.load(fp); sizes[fn] = [list(im.size), im.channels]; bpy.data.images.remove(im)
    C['preview_sizes'] = dict(ok=all(sizes[fn] and sizes[fn][0] == list(wh) for fn, wh in SIZES.items()), sizes=sizes)
    ok = all(v['ok'] for v in C.values())
    G = rep['green']; M = rep['moves']
    manifest = dict(
        deliverable='Pirate Shipwreck thumbnail ROUND 3.1 tiny base polish of the R3 lead (B_round3): green lip sunk into sand + flag cloth offset from the right rock edge. Full-res NOT Art approved yet.',
        files=dict(blend=dict(path='pirate_thumbnail_round3_1.blend', sha256=sha(a.output), note='compressed, all file images packed'),
                   previews={fn: dict(size=list(wh), sha256=sha(os.path.join(a.previews, fn)) if sizes.get(fn) else None) for fn, wh in SIZES.items()},
                   scripts=sorted(os.listdir(os.path.dirname(os.path.abspath(__file__))))),
        input=dict(path='inputs/pirate_thumbnail_round3.blend', commit='7c3b54b', sha256=src_now),
        scene=a.scene, camera=C['camera_exact_r3'],
        render=dict(engine='CYCLES', device='CPU (Roblox Studio open: GPU left alone)', samples=128, denoise=True, resolution=[1920, 1080],
                    note='resolution/samples set at render time only by render_round3_1.py; the .blend keeps the R3 render settings (1280x720, 64 spp)'),
        changes=dict(
            green=dict(object=GREEN, what='vertex Z only; X/Y identical (footprint unchanged); topology/materials unchanged',
                       verts_total=G['verts'], verts_z_changed=G['verts_z_changed'], turf_drop=G['turf_drop'],
                       rings='centre + 6 rings x 30 (ring scale 0.80 turf, 0.90/0.955/1.0 rolled rim, 1.03/1.055 dark skirt)',
                       new_profile=dict(turf='old planar turf -%.2f' % G['turf_drop'], rim_0p90='turf plane +%.2f' % rep['params']['rim1'],
                                        rim_crest_0p955='turf plane +%.2f (was +0.55)' % rep['params']['rim2'], rim_shoulder_1p0='turf plane +%.2f (was +0.30)' % rep['params']['rim3'],
                                        skirt_1p03='sand under vertex -%.2f (was plane +0.225 - turf)' % rep['params']['foot'], skirt_1p055='sand under vertex -%.2f' % rep['params']['toe']),
                       lip_height_before_after=dict(rim_crest_above_sand_at_skirt_foot=G['rim_crest_above_sand_foot'], exposed_dark_skirt_height=G['exposed_skirt_height'],
                                                    rim_crest_above_turf_ring0=G['rim_crest_above_turf'], turf_edge_ring0_above_sand=G['turf_edge_above_sand'],
                                                    units='studs (Blender units)'),
                       dz_range=[C['green_footprint_xy_unchanged']['dz_min'], C['green_footprint_xy_unchanged']['dz_max']]),
            cup=M[CUP], pole=M[POLE], ball=M[BALL], flag_cloth=M[CLOTH],
            id_props_added={n: 'RENDER_ONLY_round3_1' for n in GOLF}),
        caveats=[
            'Sand under the green is uneven and the turf top stays planar (shape preserved). Turf could only drop 0.12 before interior sand (min clearance 0.226) would poke through, '
            'so on the low (sand falls away) side a dark skirt of up to ~%.2f studs remains exposed (was %.2f); mean %.2f (was %.2f). Fixing that fully would need tilting/reshaping the turf or a sand mound = redesign, not done.'
            % (G['exposed_skirt_height']['after']['max'], G['exposed_skirt_height']['before']['max'], G['exposed_skirt_height']['after']['mean'], G['exposed_skirt_height']['before']['mean']),
            'Flag: swinging the cloth toward the camera (negative yaw) barely moves its tip (max reach ~281px vs 261px at 1920 along the rock top); yaws +10..+30 slide the tip along the rock diagonal edge (tangent). '
            'The first clean gap is ~+34..37 deg, so +36 deg about the pole was used: tip moves %.1f px left at 1920, clear of the rock edge (~10px). The cloth is the same mesh but more foreshortened, so its projected red area is ~half of R3; check the 160x90 golf cue.' % M[CLOTH]['tip_dx_px_1920']],
        checks=C, all_checks_ok=ok)
    json.dump(manifest, open(a.manifest, 'w'), indent=1, default=str)
    for k, v in C.items():
        print('CHECK', k, 'OK' if v['ok'] else 'FAIL')
    print('VALIDATE_ROUND3_1_' + ('OK' if ok else 'FAIL'))
    return ok


try:
    ok = main()
except Exception:
    import traceback; traceback.print_exc(); sys.exit(1)
sys.exit(0 if ok else 1)
