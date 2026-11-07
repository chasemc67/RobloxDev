# build_thumbnail_C_v1.py - Thumbnail proof C (deck/cabin adventure toward the patched sails).
# INCOMPLETE ENVIRONMENT: v31 free roam, no verified environment export. Ship-only scene, plain neutral sky.
#
# Run (from the workdir, one Blender process at a time):
#   blender -b inputs/start_ship_whimsy_v5_1.blend --python-exit-code 1 --python out/src/build_thumbnail_C_v1.py
# The source .blend is opened read-only and never saved. The script ADDS only a camera, 2 lights and a world;
# it does not touch geometry, materials, modifiers or object transforms. It hides Collision objects and empties
# (helpers) at render time. Then it packs everything, saves out/pirate_thumbnail_C_v1_INCOMPLETE_ENVIRONMENT.blend
# and renders out/previews/C_INCOMPLETE_ENVIRONMENT_960x540.png (no text).
import bpy, math, os, sys
from mathutils import Vector

WORK = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT_BLEND = os.path.join(WORK, 'out', 'pirate_thumbnail_C_v1_INCOMPLETE_ENVIRONMENT.blend')
OUT_PNG = os.path.join(WORK, 'out', 'previews', 'C_INCOMPLETE_ENVIRONMENT_960x540.png')

# ---- camera (Blender Z-up ship frame; deck top Z=24; bow +X; cabin x-150..-90 y-25..20; open walkway y-30..-40; hull heeled, bulwark ~y-45) ----
# v1 note: first trial at (-135,-55,31) sat inside the port bulwark; corrected once after a deck raycast probe (out/src/probe_deck_C.py).
CAM_NAME = 'Thumbnail_C_DeckAdventure'
CAM_LOC = Vector((-148.0, -40.0, 33.0))     # aft end of the open -Y walkway beside the cabin (deck Z=24), ~9 studs eye height
CAM_TARGET = Vector((30.0, -24.0, 55.0))     # patched main/fore sails ahead, cabin roof along the left
CAM_LENS = 22.0                             # mm, 36 mm sensor width (horizontal fit)

# ---- light (LookB approximation; Roblox values in inputs/lighting_lookB.json are not 1:1) ----
SUN_ELEV = 35.0          # deg; LookB note ~33 deg elevation
SUN_AZ_FROM = 235.0      # deg, direction the light COMES FROM (0=+X, 90=+Y): behind-right of camera = front/side key
SUN_RGB = (255, 236, 212)  # warm, from ColorShift_Top 255,245,230 / Atmosphere 255,235,210
SUN_STRENGTH = 4.6       # as approved v5_1 preview look
SUN_ANGLE = 2.0          # deg soft-ish shadows (ShadowSoftness 0.35)
FILL_RGB = (255, 228, 200) # warm bounce to lift wood shadows, no shadows cast
FILL_STRENGTH = 0.9
SKY_RGB = (196, 202, 210)  # plain neutral sky (no clouds/gradient/scenery)
SKY_STRENGTH = 1.2
EXPOSURE = -0.35
SAMPLES = 64


def srgb_to_lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin(rgb):
    return tuple(srgb_to_lin(c) for c in rgb)


def main():
    src = bpy.data.filepath
    scene = bpy.context.scene

    # hide Collision objects and helpers (empties) - render-time visibility only, nothing moved or edited
    hidden = []
    for o in scene.objects:
        is_col = o.name.startswith('COL_') or any(c.name == 'Collision' for c in o.users_collection)
        if is_col or o.type == 'EMPTY':
            o.hide_render = True
            o.hide_viewport = True
            hidden.append(o.name)
    col = bpy.data.collections.get('Collision')
    if col:
        col.hide_render = True
        col.hide_viewport = True

    # camera
    cd = bpy.data.cameras.new(CAM_NAME)
    cd.lens = CAM_LENS
    cd.sensor_fit = 'HORIZONTAL'
    cd.sensor_width = 36.0
    cd.clip_start = 0.5
    cd.clip_end = 5000.0
    cam = bpy.data.objects.new(CAM_NAME, cd)
    scene.collection.objects.link(cam)
    cam.location = CAM_LOC
    cam.rotation_euler = (CAM_TARGET - CAM_LOC).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam

    # sun (key)
    sd = bpy.data.lights.new('Thumbnail_C_Sun', 'SUN')
    sd.energy = SUN_STRENGTH
    sd.color = lin(SUN_RGB)
    sd.angle = math.radians(SUN_ANGLE)
    sun = bpy.data.objects.new('Thumbnail_C_Sun', sd)
    scene.collection.objects.link(sun)
    el, az = math.radians(SUN_ELEV), math.radians(SUN_AZ_FROM)
    to_sun = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    sun.rotation_euler = (-to_sun).to_track_quat('-Z', 'Y').to_euler()

    # fill (no shadows) from the opposite low side to lift wood shadows
    fd = bpy.data.lights.new('Thumbnail_C_Fill', 'SUN')
    fd.energy = FILL_STRENGTH
    fd.color = lin(FILL_RGB)
    fd.use_shadow = False
    fill = bpy.data.objects.new('Thumbnail_C_Fill', fd)
    scene.collection.objects.link(fill)
    faz, fel = az + math.pi * 0.8, math.radians(20.0)
    to_fill = Vector((math.cos(fel) * math.cos(faz), math.cos(fel) * math.sin(faz), math.sin(fel)))
    fill.rotation_euler = (-to_fill).to_track_quat('-Z', 'Y').to_euler()

    # world: plain neutral sky
    w = bpy.data.worlds.new('Thumbnail_C_NeutralSky')
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (*lin(SKY_RGB), 1.0)
    bg.inputs[1].default_value = SKY_STRENGTH
    scene.world = w

    # render
    try:
        scene.render.engine = 'CYCLES'
    except TypeError as e:
        raise SystemExit('Cycles unavailable: %s' % e)
    scene.cycles.device = 'CPU'   # Roblox Studio is open on this PC -> CPU only
    scene.cycles.samples = SAMPLES
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    vs = scene.view_settings
    vs.view_transform = 'Standard'
    vs.look = 'None'
    vs.exposure = EXPOSURE
    vs.gamma = 1.0
    scene.display_settings.display_device = 'sRGB'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'
    scene.render.filepath = OUT_PNG
    scene['thumbnail_C_version'] = 'pirate_thumbnail_C_v1_INCOMPLETE_ENVIRONMENT'
    scene['thumbnail_C_note'] = 'INCOMPLETE ENVIRONMENT: v31 free roam, no verified environment export; ship-only, neutral sky; proof not final'
    scene['thumbnail_C_source'] = src

    # pack + save new file (source never saved)
    bpy.ops.file.pack_all()
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, copy=True, compress=True)
    print('SAVED', OUT_BLEND)
    print('HIDDEN', len(hidden))
    print('CAM', tuple(round(x, 3) for x in cam.location), tuple(round(math.degrees(a), 3) for a in cam.rotation_euler), CAM_LENS)
    print('SUN_ROT', tuple(round(math.degrees(a), 3) for a in sun.rotation_euler),
          'FILL_ROT', tuple(round(math.degrees(a), 3) for a in fill.rotation_euler))

    bpy.ops.render.render(write_still=True)
    print('RENDERED', OUT_PNG)
    print('BUILD_C_OK')


try:
    main()
except Exception:
    import traceback
    traceback.print_exc()
    sys.exit(1)
