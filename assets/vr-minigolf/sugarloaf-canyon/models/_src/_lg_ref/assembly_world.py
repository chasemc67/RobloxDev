"""Pass 4 hole previews over the REAL world placement (preview only).

  blender -b -P models/_src/assembly_world.py [-- --holes 3,4,6,8,9] [--views tee,top] [--samples 32] [--spot-w 700]
  (--holes renders only those holes; --spot-w = preview watts per unit of spot_lights Brightness)
One world scene (world_scene.py: terrain-4stud.json terrain, world pieces incl. the hollow tree, every hole at its
world.json placement with heroes + rails, all pass-4 dressing, PointLights), then per hole:
  previews/assembly_hNN_tee.png  VR eye view from the tee (eye 5 above the tee, 1 behind, 72 deg FOV, 1280x720)
  previews/assembly_hNN_top.png  ortho cutaway in the hole frame (play direction up), clipped 6 above the highest
                                 felt, collision walls shown, 1024x1024
"""
import sys, os, math
SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
HOLES = [int(x) for x in argv[argv.index("--holes") + 1].split(",")] if "--holes" in argv else None
VIEWS = argv[argv.index("--views") + 1].split(",") if "--views" in argv else ["tee", "top"]
SCENE_OPTS = dict(samples=int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 32, res=1280,
                  dressing=True, lights=True,
                  spot_w=float(argv[argv.index("--spot-w") + 1]) if "--spot-w" in argv else 700.0)
import world_scene as S
import bpy
import numpy as np
import dressing_lib as DL
from mathutils import Vector

sc, cam = S.sc, S.cam
OUT = S.MODELS
mist = sc.world.mist_settings
for h in S.H:
    n = h["number"]
    if HOLES and n not in HOLES:
        continue
    if "tee" in VIEWS:
        for o in S.COLL:
            o.hide_render = True
        mist.start, mist.depth = 30, 700
        tee = DL.to_world(h, h["tee"]["position"])
        Rw = DL.hole_xf(h)[0]
        a = Rw @ np.array([h["tee"]["aim_hint"][0], 0, h["tee"]["aim_hint"][1]], float)
        a /= np.linalg.norm(a)
        cam.data.type = "PERSP"
        cam.data.angle = math.radians(72)
        cam.data.clip_start = 0.1
        cam.location = S.BL(tee - a + np.array([0, 5.0, 0]))
        look = S.BL(tee + a * 20 + np.array([0, 1.5, 0]))
        cam.rotation_euler = (look - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.resolution_x, sc.render.resolution_y = 1280, 720
        sc.render.filepath = os.path.join(OUT, "previews", f"assembly_h{n:02d}_tee.png")
        bpy.ops.render.render(write_still=True)
    if "top" in VIEWS:
        for o in S.COLL:
            o.hide_render = False
        mist.start, mist.depth = 2000, 4000
        pts = []
        for f in h["felt"]:
            for ux in (-1, 1):
                for uz in (-1, 1):
                    lp = np.array(f["center"], float) + DL.yaw_mat(f.get("yaw", 0)) @ np.array([ux * f["size"][0] / 2, 0, uz * f["size"][1] / 2])
                    pts.append(lp)
        pts = np.array(pts)
        c_l = (pts.min(0) + pts.max(0)) / 2
        ext = float(max(pts[:, 0].ptp(), pts[:, 2].ptp()))
        top_y = max(f["center"][1] for f in h["felt"]) + 6.0
        cw = DL.to_world(h, [c_l[0], top_y, c_l[2]])
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ext + 30
        cam.data.clip_start = 0.01
        cam.location = S.BL(cw)
        cam.rotation_euler = (0, 0, math.radians(h["world_yaw"]))
        sc.render.resolution_x, sc.render.resolution_y = 1024, 1024
        sc.render.filepath = os.path.join(OUT, "previews", f"assembly_h{n:02d}_top.png")
        bpy.ops.render.render(write_still=True)
    print(f"[assembly] h{n:02d}")
