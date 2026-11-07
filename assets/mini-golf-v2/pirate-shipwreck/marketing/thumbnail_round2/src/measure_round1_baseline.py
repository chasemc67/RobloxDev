# measure_round1_baseline.py - re-render round-1 scenes A/B from the preserved round-1 file (half res, quick) and sample the
# same visible-material pixel medians as validate_round2.py, so round-2 lighting changes can be compared numerically.
#   blender -b inputs/pirate_thumbnail_round1.blend --python-exit-code 1 --python out/src/measure_round1_baseline.py -- --outdir out/build/r1_baseline
# The input file is opened read-only and never saved.
import bpy, os, sys, json, argparse
import numpy as np
from bpy_extras.object_utils import world_to_camera_view as w2c
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser(); p.add_argument('--outdir', required=True); p.add_argument('--samples', type=int, default=24)
a = p.parse_args(argv); a.outdir = os.path.abspath(a.outdir); os.makedirs(a.outdir, exist_ok=True)
res = {}
try:
    for k, nm in (('A', 'Thumbnail_A_Hero'), ('B', 'Thumbnail_B_Octopus')):
        sc = bpy.data.scenes[nm]; cam = sc.camera
        vl = sc.view_layers[0]; vl.update(); dg = vl.depsgraph
        sc.cycles.device = 'CPU'; sc.cycles.samples = a.samples; sc.render.resolution_percentage = 50
        fp = os.path.join(a.outdir, '%s_round1_half.png' % k); sc.render.filepath = fp
        bpy.ops.render.render(write_still=True, scene=sc.name)
        im = bpy.data.images.load(fp); w, h = im.size
        px = np.array(im.pixels[:], np.float32).reshape(h, w, im.channels)[::-1]
        org = cam.matrix_world.translation; out = {}
        for obn, keys in (('Prop_Figurehead', ('Coral', 'CoralDk')), ('Hull', ('HullWood',)), ('Rigging', ('Canvas',))):
            ob = bpy.data.objects[obn]; M = ob.matrix_world; mats = [m.name for m in ob.data.materials]
            for poly in ob.data.polygons:
                mn = mats[poly.material_index]
                if mn not in keys: continue
                c = M @ poly.center
                if mn == 'HullWood' and c.z < 4.0: continue
                d = c - org; dist = d.length; d.normalize()
                ok, loc, nrm, idx, hob, _ = sc.ray_cast(dg, org, d, distance=dist + 0.5)
                if not ok or hob.name != ob.name or (loc - c).length > 1.0: continue
                q = w2c(sc, cam, c)
                if 0 < q.x < 1 and 0 < q.y < 1:
                    x = min(w - 1, int(q.x * w)); y = min(h - 1, int((1 - q.y) * h))
                    out.setdefault('Canvas_sails' if mn == 'Canvas' else mn, []).append(px[y, x, :3] * 255)
        res[k] = {kk: dict(median=[int(x) for x in np.median(np.array(v), 0)], n=len(v), clipped_frac=round(float(np.mean(np.max(np.array(v), 1) >= 254)), 3)) for kk, v in out.items()}
    json.dump(res, open(os.path.join(a.outdir, 'round1_pixel_baseline.json'), 'w'), indent=1)
    print('BASELINE', json.dumps(res))
except Exception:
    import traceback; traceback.print_exc(); sys.exit(1)
