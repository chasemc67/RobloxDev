# blender.exe -b --factory-startup <blend> --python render_v31.py -- <previews_dir> [shot ...]
# v3_1: identical to previous_scripts/render_v3.py (same CAMS for ship_3q / ship_tee, same env) except brighter daylight
# (sun 3.6->4.6, sky 1.1->1.35, exposure 0.35->0.6) and extra detail cameras. Env var SHIP_SAMPLES overrides 64 samples.
# Cycles CPU (Studio may be using the GPU). Adds render-only water (world Y0 = local -0.6), sand beach + bow dune,
# a cup marker, daylight; applies flight2's 30 deg yaw like the source preview. NOTHING is saved back to the blend.
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import B, Binv, WATER_Y, nrm
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import bmesh
A = sys.argv[sys.argv.index('--') + 1:]; PV = A[0]; SHOTS = A[1:] or ['ship_3q', 'ship_tee', 'ship_route']
os.makedirs(PV, exist_ok=True); sc = bpy.context.scene
def s2l(c): c = c / 255; return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def flat_mat(n, rgb, rough=0.8, emit=0.0):
    m = bpy.data.materials.new(n); m.use_nodes = True; bs = next(x for x in m.node_tree.nodes if x.type == 'BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value = (*[s2l(c) for c in rgb], 1); bs.inputs['Roughness'].default_value = rough; return m
# flight 2 yaw (preview only, as in source render_ship.py)
f2 = bpy.data.objects['RampFlight2']; piv = f2.matrix_world.translation.copy()
f2.matrix_world = Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-30), 4, 'Z') @ Matrix.Translation(-piv) @ f2.matrix_world
# glow emission (render only)
g = bpy.data.materials['Glow']; bs = next(x for x in g.node_tree.nodes if x.type == 'BSDF_PRINCIPLED')
bs.inputs['Emission Color'].default_value = (1.0, 0.55, 0.2, 1); bs.inputs['Emission Strength'].default_value = 6.0
# hull bvh for the bow dune
hull = bpy.data.objects['Hull']; bm = bmesh.new(); bm.from_mesh(hull.data); bm.transform(hull.matrix_world); HB = BVHTree.FromBMesh(bm); bm.free()
from shiplib import hull_outer_w
import functools
@functools.lru_cache(maxsize=None)
def KEEL(x):
    ss = np.linspace(-1, 1, 401); P = [hull_outer_w(min(x, 156.0), q) for q in ss]; k = int(np.argmin([p[1] for p in P])); return P[k][2], P[k][1]
def sand_h(x, z):
    zs = 58.0 + max(0.0, -170.0 - x) * 1.3 + 5.0 * math.sin(x / 37.0) + 2.5 * math.sin(x / 11.0 + 1.0); xs = 100.0 + max(0.0, -z - 20.0) * 0.9 + 6.0 * math.sin(z / 29.0)
    m = max(z - zs, x - xs)
    y = -0.05 if m > 6 else -0.05 - (6 - m) * 0.3
    y = max(y, -7.0)
    if x > 60:   # bow resting on the beach: smooth dune rising to just under the keel line (render only)
        kz, ky = KEEL(x); w = min(1.0, (x - 60) / 35.0); dune = (ky - 0.4) * w * math.exp(-((z - kz) / 26.0) ** 2) + (-0.05) * (1 - w)
        y = max(y, min(dune, ky - 0.4))
    return y
xs = np.arange(-460, 420.1, 4.0); zs = np.arange(-300, 380.1, 4.0); V = []; F = []
for i, x in enumerate(xs):
    for j, z in enumerate(zs): V.append(B((x, sand_h(x, z), z)))
nz = len(zs)
for i in range(len(xs) - 1):
    for j in range(nz - 1): F.append((i * nz + j, (i + 1) * nz + j, (i + 1) * nz + j + 1, i * nz + j + 1))
me = bpy.data.meshes.new('ENV_Sand'); me.from_pydata(V, [], F); me.update(); sand = bpy.data.objects.new('ENV_Sand', me); sc.collection.objects.link(sand)
me.materials.append(flat_mat('ENV_SandMat', (226, 184, 128), 0.95))
for p in me.polygons: p.use_smooth = True
bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, WATER_Y)); wat = bpy.context.active_object; wat.name = 'ENV_Water'
wm = flat_mat('ENV_WaterMat', (52, 150, 165), 0.12); wat.data.materials.append(wm)
wb = next(x for x in wm.node_tree.nodes if x.type == 'BSDF_PRINCIPLED'); wb.inputs['Alpha'].default_value = 0.86
cup = bpy.data.objects['CupRef'].matrix_world.translation
bpy.ops.mesh.primitive_cylinder_add(radius=7, depth=0.3, vertices=24, location=(cup.x, cup.y, 0.0)); o = bpy.context.active_object; o.name = 'ENV_CupGreen'; o.data.materials.append(flat_mat('ENV_Felt', (105, 185, 98)))
bpy.ops.mesh.primitive_cylinder_add(radius=0.7, depth=0.34, vertices=16, location=(cup.x, cup.y, 0.02)); o = bpy.context.active_object; o.name = 'ENV_CupHole'; o.data.materials.append(flat_mat('ENV_Hole', (20, 20, 20)))
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=8, vertices=8, location=(cup.x, cup.y, 4.0)); o = bpy.context.active_object; o.name = 'ENV_Pin'; o.data.materials.append(flat_mat('ENV_PinM', (240, 240, 240)))
bpy.ops.mesh.primitive_cube_add(size=1, location=(cup.x + 1.3, cup.y, 7.2)); o = bpy.context.active_object; o.name = 'ENV_PinFlag'; o.scale = (2.4, 0.1, 1.4); o.data.materials.append(flat_mat('ENV_PinFlagM', (220, 50, 40)))
for o in bpy.data.objects:
    if o.name.startswith('COL'): o.hide_render = True
# light + world
sun = bpy.data.objects.new('ENV_Sun', bpy.data.lights.new('ENV_Sun', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 4.6; sun.data.angle = math.radians(6); sun.data.color = (1.0, 0.97, 0.92)
d = nrm(np.array(B((0.35, 0.85, 0.55)))); sun.rotation_euler = Vector(-d).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new('ENV_World'); sc.world = w; w.use_nodes = True; bg = next(x for x in w.node_tree.nodes if x.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.42, 0.62, 0.95, 1); bg.inputs['Strength'].default_value = 1.35
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(os.environ.get('SHIP_SAMPLES', '64')); sc.cycles.use_denoising = True
try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
sc.cycles.max_bounces = 4; sc.render.resolution_x, sc.render.resolution_y = 1600, 1000; sc.render.resolution_percentage = 100
try: sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Base Contrast'
except Exception: pass
sc.view_settings.exposure = 0.6
cam = bpy.data.objects.new('ENV_Cam', bpy.data.cameras.new('ENV_Cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.sensor_fit = 'HORIZONTAL'; cam.data.clip_start = 0.2; cam.data.clip_end = 6000
def shoot(name, eye_r, tgt_r, fov):
    eye = Vector(B(eye_r)); tgt = Vector(B(tgt_r)); cam.location = eye; cam.rotation_euler = (tgt - eye).to_track_quat('-Z', 'Y').to_euler()
    cam.data.angle = math.radians(fov); sc.render.filepath = os.path.join(PV, name + '.png'); bpy.ops.render.render(write_still=True); print('RENDERED', name, eye_r, tgt_r, fov)
tee = Binv(bpy.data.objects['Tee1'].matrix_world.translation); eye_tee = tee + np.array((0, 5.0, 0))
CAMS = {
 'ship_3q': ((330.0, 205.0, 420.0), (10.0, 42.0, 15.0), 46),
 'ship_tee': (tuple(eye_tee), tuple(eye_tee + np.array((0.93, 0.29, -0.25)) * 50), 90),
 'ship_route': ((-10.0, 160.0, 285.0), (-125.0, 8.0, 110.0), 58),
 'ship_stern': ((-330.0, 60.0, 160.0), (-120.0, 40.0, 10.0), 42),
 'ship_bow': ((300.0, 30.0, 120.0), (150.0, 40.0, 10.0), 40),
 'ship_beach': ((-25.0, 5.0, 105.0), (-25.0, 11.0, 30.0), 62),
 # v3_1 extra detail cameras (not used for the 3q/tee comparison)
 'det_bow': ((215.0, 22.0, 75.0), (150.0, 36.0, 12.0), 40),
 'det_deck': ((-40.0, 62.0, 40.0), (-100.0, 30.0, 0.0), 55),
 'det_roof': ((-60.0, 75.0, 60.0), (-120.0, 52.0, 0.0), 45),
 'det_sail': ((120.0, 80.0, 160.0), (10.0, 80.0, 0.0), 45),
 'det_mast': ((90.0, 120.0, 120.0), (-5.0, 95.0, -25.0), 40),
 'det_sails': ((200.0, 60.0, 125.0), (55.0, 45.0, 5.0), 52),
 'det_fore': ((175.0, 72.0, 115.0), (97.0, 42.0, 10.0), 45),
 'det_side': ((70.0, 42.0, 175.0), (45.0, 20.0, 30.0), 58),
 'det_stern3q': ((-235.0, 95.0, 140.0), (-130.0, 50.0, 10.0), 45),
}
for s in SHOTS:
    e, t, f = CAMS[s]; shoot(s, e, t, f)
print('RENDER_OK')
