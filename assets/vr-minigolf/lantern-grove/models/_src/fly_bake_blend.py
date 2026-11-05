"""Preview flythrough (Eevee). blender -b --factory-startup -P _src/flythrough.py -- [--start N --end M --step K]
Renders previews/fly_frames/f_NNNN.png, skipping existing frames (checkpointed)."""
import sys, os, math, json
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d): return int(argv[argv.index(k) + 1]) if k in argv else d
SCENE_OPTS = dict(samples=16, res=1280, dressing=True, lights=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world_scene as S
import bpy
from mathutils import Vector
import numpy as np
FPS = 24
sc = bpy.context.scene
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try: sc.render.engine = eng; break
    except TypeError: pass
ee = sc.eevee
for k, v in dict(taa_render_samples=arg("--taa", 16), use_shadows=True, use_raytracing=False, use_gtao=True, use_bloom=True).items():
    if hasattr(ee, k): setattr(ee, k, v)
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1280, 720, 100
sc.render.image_settings.file_format = "PNG"
sc.render.fps = FPS
T = S.T
W = S.W
def gy(x, z):
    try: return float(T.height(x, z))
    except Exception: return 30.0
keys = []  # (time_s, pos, target) map coords x,y(up),z
t = 0.0
keys.append((t, (330, 230, 330), (60, 40, -10))); t += 5
keys.append((t, (290, 140, 260), (150, 35, 60))); t += 4
for h in W["holes"][:8]:
    tee, cup = np.array(h["tee_world"]), np.array(h["cup_world"])
    d = cup - tee; d[1] = 0; d /= np.linalg.norm(d) + 1e-6
    side = np.array([-d[2], 0, d[0]])
    p = tee - d * 9 + side * 3; p[1] = max(tee[1], gy(p[0], p[2])) + 6
    keys.append((t, tuple(p), tuple(cup + [0, 1, 0]))); t += 2.6
    q = tee + d * 6 - side * 4; q[1] = max(tee[1], gy(q[0], q[2])) + 7
    keys.append((t, tuple(q), tuple(cup + d * 15 + [0, 2, 0]))); t += 3.4
tr = W["hollow_tree"]; c = np.array(tr["center"]); op = np.array(tr["doorway"]["outer_point"])
dr = op - c; dr[1] = 0; dr /= np.linalg.norm(dr)
keys.append((t, tuple(c + dr * 110 + [0, 40, 0]), tuple(c + [0, 60, 0]))); t += 5
keys.append((t, tuple(op + dr * 25 + [0, 10, 0]), tuple(op + [0, 8, 0]))); t += 4
keys.append((t, tuple(op + [0, 8, 0]), tuple(c + [0, 6, 0]))); t += 3
keys.append((t, tuple(c + dr * 18 + [0, 9, 0]), tuple(c - dr * 30 + [0, 4, 0]))); t += 4
keys.append((t, tuple(c + dr * 8 + [0, 10, 0]), tuple(c + [0, 75, 0]))); t += 3
keys.append((t, tuple(c + dr * 8 + [0, 11, 0]), tuple(c + [0, 78, 0])))
DUR = keys[-1][0]; NF = int(DUR * FPS) + 1
def cr(p0, p1, p2, p3, u):
    return 0.5 * (2*p1 + (-p0+p2)*u + (2*p0-5*p1+4*p2-p3)*u*u + (-p0+3*p1-3*p2+p3)*u**3)
def sample(ts, idx):
    for i in range(len(keys) - 1):
        if keys[i][0] <= ts <= keys[i+1][0]: break
    a, b = keys[i][0], keys[i+1][0]; u = (ts - a) / (b - a); u = u*u*(3-2*u)*0.5 + u*0.5
    P = [np.array(keys[max(0, min(len(keys)-1, j))][idx], float) for j in (i-1, i, i+1, i+2)]
    return cr(*P, u)
cam = sc.camera
cam.data.angle = math.radians(70)
start, end, step = arg("--start", 0), arg("--end", NF - 1), arg("--step", 1)
sc.frame_start, sc.frame_end = 0, NF - 1
for f in range(0, NF):
    ts = f / FPS
    p, tg = sample(ts, 1), sample(ts, 2)
    cam.location = S.BL(p)
    cam.rotation_euler = (S.BL(tg) - S.BL(p)).to_track_quat("-Z", "Y").to_euler()
    if f: 
        e = cam.rotation_euler; pe = prev
        for k in range(3):
            while e[k]-pe[k] > math.pi: e[k] -= 2*math.pi
            while e[k]-pe[k] < -math.pi: e[k] += 2*math.pi
    prev = cam.rotation_euler.copy()
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)
ee.taa_render_samples = 24
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = "//frames/f_"
bpy.ops.file.pack_all()
dst = "/workspace/lg_render/lantern_grove_fly.blend"
os.makedirs(os.path.dirname(dst), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True)
print("[bake] saved", dst, NF, flush=True)
