# render_round1.py - render ONE thumbnail scene from the packed round-1 file (CPU Cycles; one Blender job at a time).
#   blender -b out/pirate_thumbnail_round1.blend --python-exit-code 1 --python out/src/render_round1.py -- --scene A
# Output: out/previews/<A|B|C>_round1.png (no text). --out overrides the png path. The .blend is not saved.
import bpy, os, sys, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); OUTDIR = os.path.abspath(os.path.join(HERE, '..'))
SCENES = {'A': 'Thumbnail_A_Hero', 'B': 'Thumbnail_B_Octopus', 'C': 'Thumbnail_C_Adventure'}
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser(); p.add_argument('--scene', required=True, choices=list(SCENES)); p.add_argument('--out')
p.add_argument('--samples', type=int); p.add_argument('--percent', type=int)
a = p.parse_args(argv)
try:
    sc = bpy.data.scenes[SCENES[a.scene]]
    sc.cycles.device = 'CPU'
    if a.samples: sc.cycles.samples = a.samples
    if a.percent: sc.render.resolution_percentage = a.percent
    out = a.out or os.path.join(OUTDIR, 'previews', '%s_round1.png' % a.scene)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sc.render.filepath = out
    if bpy.context.window: bpy.context.window.scene = sc
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print('RENDERED', sc.name, sc.camera.name, out)
except Exception:
    import traceback; traceback.print_exc(); sys.exit(1)
