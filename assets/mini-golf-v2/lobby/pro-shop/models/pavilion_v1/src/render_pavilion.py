"""Render review previews for pro_shop_pavilion_v1 (one Blender process, cameras in sequence).

Usage:
  blender -b <pro_shop_pavilion_v1.blend> --python render_pavilion.py -- --outdir <dir>
          [--cams CAM_Front34 CAM_Eye_Counter ...] [--device CPU|GPU] [--samples 64] [--percent 100]
Writes <outdir>/<camera name minus CAM_>.png. Collision proxies, editable-text source and anchors
never render. Each camera stores its resolution (ps_res) and sun direction (ps_sun_dir).
"""
import argparse
import os
import sys
import time

import bpy
from mathutils import Vector

DEFAULT = ["CAM_Front34", "CAM_Eye_Counter", "CAM_Eye_BallTray", "CAM_Eye_ClubRack", "CAM_Rear34"]


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--cams", nargs="*", default=DEFAULT)
    ap.add_argument("--device", default="CPU")
    ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--percent", type=int, default=100)
    a = ap.parse_args(argv)
    os.makedirs(a.outdir, exist_ok=True)
    sc = bpy.context.scene
    sc.cycles.device = a.device
    sc.cycles.samples = a.samples
    sc.cycles.use_denoising = True
    sc.render.resolution_percentage = a.percent
    sc.render.image_settings.file_format = "PNG"
    for c in bpy.data.collections:
        if c.name in ("PS_Collision_Proxy", "PS_Source_EditableText"):
            c.hide_render = True
    sun = bpy.data.objects["ENV_Sun"]
    for name in a.cams:
        cam = bpy.data.objects[name]
        sc.camera = cam
        rx, ry = cam.get("ps_res", (1600, 1000))
        sc.render.resolution_x, sc.render.resolution_y = int(rx), int(ry)
        d = Vector(cam.get("ps_sun_dir", (0.55, 0.62, -0.75)))
        sun.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(os.path.abspath(a.outdir), name.replace("CAM_", "") + ".png")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"RENDERED {sc.render.filepath} {rx}x{ry} in {time.time() - t:.1f}s", flush=True)


if __name__ == "__main__":
    main()
