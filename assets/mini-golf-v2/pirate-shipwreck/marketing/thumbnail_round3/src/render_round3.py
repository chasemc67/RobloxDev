# render_round3.py - render the single round-3 thumbnail scene (CPU Cycles; one Blender job at a time). File not saved.
#   blender -b out/pirate_thumbnail_round3.blend --python-exit-code 1 --python out/src/render_round3.py -- --output out/previews/B_round3.png
#   [--scene Thumbnail_B_Lead_R3] [--samples N] [--percent P]
import bpy, os, sys, argparse
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser(); p.add_argument('--output', required=True); p.add_argument('--scene', default='Thumbnail_B_Lead_R3')
p.add_argument('--samples', type=int); p.add_argument('--percent', type=int)
a = p.parse_args(argv)
try:
    sc = bpy.data.scenes[a.scene]
    sc.cycles.device = 'CPU'
    if a.samples: sc.cycles.samples = a.samples
    if a.percent: sc.render.resolution_percentage = a.percent
    out = os.path.abspath(a.output); os.makedirs(os.path.dirname(out), exist_ok=True)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print('RENDERED', sc.name, sc.camera.name, out)
except Exception:
    import traceback; traceback.print_exc(); sys.exit(1)
