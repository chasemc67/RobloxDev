# render_round2.py - render ONE round-2 scene from the packed file (CPU Cycles; one Blender job at a time).
#   blender -b out/pirate_thumbnail_round2.blend --python-exit-code 1 --python out/src/render_round2.py -- --scene A
# Output: out/previews/<A|B>_round2.png (1280x720, no text). --out / --samples / --percent for quick proofs. File not saved.
import bpy, os, sys, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); OUTDIR = os.path.abspath(os.path.join(HERE, '..'))
SCENES = {'A': 'Thumbnail_A_Hero_R2', 'B': 'Thumbnail_B_Octopus_R2'}
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser(); p.add_argument('--scene', required=True, choices=list(SCENES)); p.add_argument('--out')
p.add_argument('--samples', type=int); p.add_argument('--percent', type=int)
a = p.parse_args(argv)
try:
    sc = bpy.data.scenes[SCENES[a.scene]]
    sc.cycles.device = 'CPU'
    if a.samples: sc.cycles.samples = a.samples
    if a.percent: sc.render.resolution_percentage = a.percent
    out = a.out or os.path.join(OUTDIR, 'previews', '%s_round2.png' % a.scene)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    sc.render.filepath = os.path.abspath(out)
    if bpy.context.window: bpy.context.window.scene = sc
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print('RENDERED', sc.name, sc.camera.name, out)
except Exception:
    import traceback; traceback.print_exc(); sys.exit(1)
