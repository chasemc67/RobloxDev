"""Per-hole VR tee views (eye 5 studs above the tee, looking at the cup) over the REAL pass-2b world:
opens out_p2b/models/blockout/aurora_blockout.blend, hides the blockout's placeholder rails/flags/tee markers and spire,
IMPORTS the exported P1 FBXs (hole dressing, flags, movers at rest, H5 cone + puff, spire + shards) and places them with
the holes.json world transforms. Cycles OptiX 32 spp, 1280x720, the pass-2b lights/bloom + tee fill.
  blender -b out_p2b/models/blockout/aurora_blockout.blend -P out_props/_src/tee_views.py
"""
import bpy, sys, os, json, math
from mathutils import Vector, Matrix
SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import holesdata as D

man = json.load(open(os.path.join(OUT, "manifest.json")))
PRE = os.path.join(OUT, "previews")
for o in bpy.data.objects:
    if o.name in ("holes__Timber", "holes__Snow", "holes__Brass", "holes__Flag") or o.name.startswith("spire__"):
        o.hide_render = True
col = bpy.data.collections.new("P1 props")
bpy.context.scene.collection.children.link(col)


def cv(p):
    return Vector((p[0], -p[2], p[1]))


def import_fbx(rel):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(OUT, rel))
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
    roots = [o for o in new if o.parent is None]
    return roots, new


def place(roots, M):
    for r in roots:
        r.matrix_world = M @ r.matrix_world


def hole_M(n):
    h = D.H[n]
    return Matrix.Translation(cv(h["world_offset"])) @ Matrix.Rotation(math.radians(h["world_yaw"]), 4, "Z")


def inst_M(pos, yaw=0.0, scale=1.0):
    s = scale if isinstance(scale, (list, tuple)) else [scale] * 3
    return Matrix.Translation(cv(pos)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Diagonal((s[0], s[2], s[1], 1))


nimp = 0
for f in man["hole_dressing_files"]:
    roots, new = import_fbx(f["file"])
    place(roots, hole_M(f["hole"]))
    nimp += 1
for h in man["holes"]:
    for i in h["instances"]:
        if i["merged_into_dressing"]:
            continue
        roots, new = import_fbx(i["fbx"])
        place(roots, hole_M(h["hole"]) @ inst_M(i["pos"], i["yaw"], i["scale"]))
        nimp += 1
for w in man["world_instances"]:
    if w["prop"] in ("aa_world_starfrost_spire", "aa_world_spire_shards", "aa_kit_geyser_cone", "aa_world_geyser_puff60", "aa_world_great_frozen_falls"):
        roots, new = import_fbx(w["fbx"])
        place(roots, inst_M(w["pos"], w["yaw"], w["scale"]))
        nimp += 1
for L in man["lights"]:
    d = bpy.data.lights.new("p1 light", "POINT")
    d.energy = 25 * L["brightness"]
    d.color = tuple(int(L["color"][k:k + 2], 16) / 255 for k in (1, 3, 5))
    d.shadow_soft_size = 0.5
    o = bpy.data.objects.new("p1 light", d)
    col.objects.link(o)
    o.location = cv(L["pos_world"])
print(f"[tee] imported {nimp} FBX instances")

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 32
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1280, 720, 100
cam = bpy.data.objects["Hero Camera"]
sc.camera = cam
fill = bpy.data.objects.get("Tee soft fill")
if fill:
    fill.hide_render = False
done = []
for n in sorted(D.H):
    h = D.H[n]
    tee = D.to_world(n, [h["tee"]["position"][0], h["tee"]["position"][1] + 5.0, h["tee"]["position"][2]])
    cup = D.to_world(n, [h["cup"]["position"][0], h["cup"]["position"][1] + 1.0, h["cup"]["position"][2]])
    cam.location = cv(tee)
    cam.rotation_euler = (cv(cup) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.angle = math.radians(72)
    sc.render.filepath = os.path.join(PRE, f"tee_h{n:02d}.png")
    bpy.ops.render.render(write_still=True)
    done.append(n)
    print(f"[tee] H{n} rendered", flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "aurora_props_p1_in_world.blend"), compress=True)
print("[tee] done", done)
