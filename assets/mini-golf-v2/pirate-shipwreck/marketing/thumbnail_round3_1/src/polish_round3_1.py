# polish_round3_1.py - round 3.1 render-only polish of the R3 lead thumbnail (2 asset corrections, nothing else).
#   blender -b --factory-startup --python-exit-code 1 --python polish_round3_1.py -- --source <pirate_thumbnail_round3.blend> \
#       --output <out/pirate_thumbnail_round3_1.blend> [--report <json>] [--turf-drop 0.12] [--flag-yaw-deg D] [--probe a,b,c]
# 1) RO3_RenderOnly_PuttingGreen: vertex Z only (X/Y untouched = identical footprint). Turf top lowered uniformly by --turf-drop
#    (planar shape kept); rolled rim softened to a minimal lip just above the turf; skirt shoulder/foot sunk to the sand under
#    each boundary vertex (sand is uneven, sampled per vertex). Cup, pole, flag cloth and ball move down by the same turf drop.
# 2) RO3_RenderOnly_FlagCloth: rotated by --flag-yaw-deg about the pole axis (world Z through the cup/pole x/y). Pole/cup x/y unchanged.
# The source is opened read-only and saved as a packed copy to --output; SHA-256 of the source recorded before/after.
import bpy, sys, os, json, math, hashlib, argparse
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view as w2c

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument('--source', required=True); p.add_argument('--output', required=True); p.add_argument('--report')
p.add_argument('--scene', default='Thumbnail_B_Lead_R3')
p.add_argument('--turf-drop', type=float, default=0.12)
p.add_argument('--rim1', type=float, default=0.06, help='ring 0.90 above new turf')
p.add_argument('--rim2', type=float, default=0.09, help='rim crest (ring 0.955) above new turf = lip over turf')
p.add_argument('--rim3', type=float, default=0.02, help='rim outer shoulder (ring 1.0) above new turf')
p.add_argument('--foot', type=float, default=0.03, help='skirt ring 1.03 sunk this far below sand')
p.add_argument('--toe', type=float, default=0.40, help='skirt ring 1.055 sunk this far below sand')
p.add_argument('--flag-yaw-deg', type=float, default=0.0)
p.add_argument('--probe', default='', help='comma list of yaw angles: dump cloth screen polygons only, no save')
A = p.parse_args(argv)
A.source = os.path.abspath(A.source); A.output = os.path.abspath(A.output)
A.report = os.path.abspath(A.report) if A.report else os.path.splitext(A.output)[0] + '_polish_report.json'
SEG, NR = 30, 6
OFF = [0.5, 0.5 + 0.3025, 0.5 + 0.55, 0.5 + 0.3025, 0.225, -0.7]   # R3 ring dz above the fitted sand plane (height 0.5, rim 0.55)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def stats(xs):
    return dict(min=round(min(xs), 3), mean=round(sum(xs) / len(xs), 3), max=round(max(xs), 3))


def main():
    rep = dict(source=A.source, source_sha256_before=sha(A.source), params=vars(A).copy())
    bpy.ops.wm.open_mainfile(filepath=A.source, load_ui=False)
    sc = bpy.data.scenes[A.scene]
    sc.view_layers[0].update(); cam = sc.camera
    T = bpy.data.objects['RO_CoveTerrain']; Mt = T.matrix_world
    BVH = BVHTree.FromPolygons([Mt @ v.co for v in T.data.vertices], [tuple(q.vertices) for q in T.data.polygons])

    def sand(x, y):
        l, *_ = BVH.ray_cast(Vector((x, y, 500.0)), Vector((0, 0, -1)))
        if l is None: raise RuntimeError('no sand under %.2f %.2f' % (x, y))
        return l.z
    G = bpy.data.objects['RO3_RenderOnly_PuttingGreen']; cup = bpy.data.objects['RO3_RenderOnly_Cup']
    pole = bpy.data.objects['RO3_RenderOnly_FlagPole']; cloth = bpy.data.objects['RO3_RenderOnly_FlagCloth']; ball = bpy.data.objects['RO3_RenderOnly_GolfBall']
    for o in (G, cloth):
        assert o.parent is None and o.matrix_world == Matrix.Identity(4), o.name + ' expected identity transform'
    assert len(G.data.vertices) == 1 + SEG * NR
    dz = A.turf_drop
    axis = Vector((pole.location.x, pole.location.y, 0))

    def rot(yaw):
        return Matrix.Translation(axis) @ Matrix.Rotation(math.radians(yaw), 4, 'Z') @ Matrix.Translation(-axis)

    if A.probe:
        out = {}
        for a in A.probe.split(','):
            R = rot(float(a))
            out[a] = dict(uv=[list(w2c(sc, cam, R @ (v.co - Vector((0, 0, dz)))))[:2] for v in cloth.data.vertices],
                          faces=[list(f.vertices) for f in cloth.data.polygons])
        out['pole_uv'] = [list(w2c(sc, cam, pole.location + Vector((0, 0, z - dz))))[:2] for z in (0.0, 4.0, 8.0, 12.0)]
        os.makedirs(os.path.dirname(A.report), exist_ok=True)
        json.dump(out, open(A.report, 'w')); print('PROBE_OK'); return

    me = G.data
    before = [v.co.copy() for v in me.vertices]
    ring = lambda r, k: 1 + r * SEG + k
    lip_b, lip_a, skirt_b, skirt_a, rimturf_b, rimturf_a, turf_b, turf_a = [], [], [], [], [], [], [], []
    me.vertices[0].co.z -= dz
    for k in range(SEG):
        s = [sand(before[ring(r, k)].x, before[ring(r, k)].y) for r in range(NR)]
        Tn = [before[ring(r, k)].z - OFF[r] + 0.5 - dz for r in range(NR)]          # new planar turf level at each ring's x/y
        new = [Tn[0], Tn[1] + A.rim1, Tn[2] + A.rim2, Tn[3] + A.rim3, s[4] - A.foot, s[5] - A.toe]
        new[3] = min(new[3], new[2] - 0.02)
        new[4] = min(new[4], new[3] - 0.01)
        new[5] = min(new[5], new[4] - 0.05)
        for r in range(NR): me.vertices[ring(r, k)].co.z = new[r]
        ob = [before[ring(r, k)].z for r in range(NR)]
        lip_b.append(ob[2] - s[4]); lip_a.append(new[2] - s[4])                     # rim crest above the sand at the skirt foot
        skirt_b.append(max(0.0, ob[3] - s[4])); skirt_a.append(max(0.0, new[3] - s[4]))   # exposed dark skirt (rim shoulder -> sand)
        rimturf_b.append(ob[2] - ob[0]); rimturf_a.append(new[2] - new[0])
        turf_b.append(ob[0] - s[0]); turf_a.append(new[0] - s[0])
    me.update()
    for v0, v1 in zip(before, me.vertices):
        assert v0.x == v1.co.x and v0.y == v1.co.y, 'footprint x/y changed'
    changed = [i for i, (v0, v1) in enumerate(zip(before, me.vertices)) if v0.z != v1.co.z]
    rep['green'] = dict(object=G.name, verts=len(me.vertices), verts_z_changed=len(changed), xy_changed=0, turf_drop=dz,
                        rim_crest_above_sand_foot=dict(before=stats(lip_b), after=stats(lip_a)),
                        exposed_skirt_height=dict(before=stats(skirt_b), after=stats(skirt_a)),
                        rim_crest_above_turf=dict(before=stats(rimturf_b), after=stats(rimturf_a)),
                        turf_edge_above_sand=dict(before=stats(turf_b), after=stats(turf_a)),
                        per_vertex_z=dict(before=[round(v.z, 4) for v in before], after=[round(v.co.z, 4) for v in me.vertices]))
    moves = {}
    for o in (cup, pole, ball):
        b = list(o.location); o.location.z -= dz
        moves[o.name] = dict(before=[round(c, 4) for c in b], after=[round(c, 4) for c in o.location], delta=[0.0, 0.0, -dz])
    cb = [v.co.copy() for v in cloth.data.vertices]
    uvb = [w2c(sc, cam, c) for c in cb]
    R = rot(A.flag_yaw_deg)
    for v in cloth.data.vertices: v.co = R @ (v.co - Vector((0, 0, dz)))
    cloth.data.update()
    uva = [w2c(sc, cam, v.co) for v in cloth.data.vertices]
    tip = max(range(len(uvb)), key=lambda i: (uvb[i] - uvb[0]).length)
    moves[cloth.name] = dict(yaw_deg_about_pole=A.flag_yaw_deg, pole_axis_xy=[round(axis.x, 4), round(axis.y, 4)], z_drop=dz, verts=len(cb),
                             max_vertex_move=round(max((v.co - c).length for v, c in zip(cloth.data.vertices, cb)), 4),
                             tip_vertex=tip,
                             tip_world=dict(before=[round(c, 3) for c in cb[tip]], after=[round(c, 3) for c in cloth.data.vertices[tip].co]),
                             tip_uv=dict(before=[round(uvb[tip].x, 4), round(uvb[tip].y, 4)], after=[round(uva[tip].x, 4), round(uva[tip].y, 4)]),
                             tip_dx_px_1920=round((uva[tip].x - uvb[tip].x) * 1920, 1), tip_dy_px_1080=round((uva[tip].y - uvb[tip].y) * 1080, 1),
                             u_range=dict(before=[round(min(q.x for q in uvb), 4), round(max(q.x for q in uvb), 4)], after=[round(min(q.x for q in uva), 4), round(max(q.x for q in uva), 4)]),
                             v_range=dict(before=[round(min(q.y for q in uvb), 4), round(max(q.y for q in uvb), 4)], after=[round(min(q.y for q in uva), 4), round(max(q.y for q in uva), 4)]))
    rep['moves'] = moves
    for o in (G, cup, pole, cloth, ball):
        o['RENDER_ONLY_round3_1'] = 'R3.1 polish: green lip sunk into sand / flag cloth yaw (render-only staging)'
    # keep zero-user images (e.g. an unused packed kit palette) so the save does not drop any datablock that the source carries
    rep['fake_user_kept'] = []
    for im in bpy.data.images:
        if im.users == 0 and not im.use_fake_user:
            im.use_fake_user = True; rep['fake_user_kept'].append(im.name)
    bpy.ops.file.pack_all()
    if A.output == A.source: raise SystemExit('refusing to overwrite the source')
    os.makedirs(os.path.dirname(A.output), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=A.output, copy=True, compress=True)
    if os.path.exists(A.output + '1'): os.remove(A.output + '1')
    rep['source_sha256_after'] = sha(A.source); rep['output_sha256'] = sha(A.output)
    assert rep['source_sha256_after'] == rep['source_sha256_before']
    os.makedirs(os.path.dirname(A.report), exist_ok=True)
    json.dump(rep, open(A.report, 'w'), indent=1)
    print('POLISH_R3_1_OK', A.output)


try:
    main()
except SystemExit:
    raise
except Exception:
    import traceback; traceback.print_exc(); sys.exit(1)
