# render_round3_1.py - render the R3.1 lead thumbnail once (Cycles, CPU by default since Roblox Studio may hold the GPU). File not saved.
#   blender -b <out/pirate_thumbnail_round3_1.blend> --python-exit-code 1 --python render_round3_1.py -- \
#       --source <out/pirate_thumbnail_round3_1.blend> --output <out/previews/B_round3_1_1920x1080.png> [--samples 128] [--width 1920 --height 1080]
# Resolution/samples/denoise are set for this render only (the saved .blend keeps the R3 render settings); camera untouched (16:9 frame).
import bpy, os, sys, argparse
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument('--source', help='blend to render (if Blender was started without it)'); p.add_argument('--output', required=True)
p.add_argument('--scene', default='Thumbnail_B_Lead_R3'); p.add_argument('--samples', type=int, default=128)
p.add_argument('--width', type=int, default=1920); p.add_argument('--height', type=int, default=1080)
a = p.parse_args(argv)
try:
    if a.source and os.path.abspath(bpy.data.filepath or '') != os.path.abspath(a.source):
        bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.source), load_ui=False)
    sc = bpy.data.scenes[a.scene]
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = a.samples; sc.cycles.use_denoising = True
    sc.render.resolution_x = a.width; sc.render.resolution_y = a.height; sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
    out = os.path.abspath(a.output); os.makedirs(os.path.dirname(out), exist_ok=True)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print('RENDERED', sc.name, sc.camera.name, out)
except Exception:
    import traceback; traceback.print_exc(); sys.exit(1)
