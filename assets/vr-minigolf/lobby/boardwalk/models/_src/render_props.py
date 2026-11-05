"""Per-prop previews from the exported FBX files: 3/4 view + eye-height (5 studs) view with a 2x5 reference
capsule. Writes previews/props/_views/<name>_34.png and <name>_eye.png; post_previews.py composes
previews/props/<name>.png and previews/contact_sheet.png.
Blender: -P render_props.py [-- --only a,b]"""
import bpy, os, sys, math, json
from mathutils import Vector

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import bwlib as L  # noqa: E402
import render_lib as RL  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
argv = [a for x in argv for a in x.replace("=", " ").split(" ") if a]
ONLY = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
VIEWS = os.path.join(OUT, "previews", "props", "_views")
os.makedirs(VIEWS, exist_ok=True)


def main():
    man = json.load(open(os.path.join(OUT, "manifest.json")))
    sc = L.reset_scene()
    RL.setup_cycles(sc, samples=48, res=(720, 720))
    RL.world(sc, "#E9C9AE", 0.9, zenith_hex="#9DB8D8")
    stage = bpy.data.collections.new("_stage")
    sc.collection.children.link(stage)
    RL.sun(stage, (0.55, 0.75, -0.6), hexv="#FFD2A0", energy=3.2, angle_deg=6)
    RL.plane(stage, "ground", (600, 600), (0, 0, 0), RL.flat_mat("ground", "#A79C8E", 0.95))
    cap = RL.capsule(stage, (0, 0, 0))
    cam = RL.camera(stage, fov_deg=40)
    fov = math.radians(40)
    for p in man["props"]:
        name = p["name"]
        if ONLY and name not in ONLY:
            continue
        col = bpy.data.collections.new(name)
        sc.collection.children.link(col)
        objs = RL.import_fbx(os.path.join(OUT, p["fbx"]), col)
        RL.fix_imported_materials()
        mn, mx = L.bbox_blender(objs)
        lift = -mn.z if mn.z < -1e-3 else 0.0       # blades: pivot at hub, sit them on the ground
        for o in objs:
            o.location.z += lift
        bpy.context.view_layer.update()
        mn, mx = L.bbox_blender(objs)
        c = (mn + mx) / 2
        ext = mx - mn
        front = Vector((0, 1, 0)) if p["front"].startswith("-Z") else Vector((0, -1, 0))
        side = Vector((-front.y, front.x, 0))       # viewer's right when looking at the front
        if side.x < 0:
            side = -side
        rad = max(ext.length / 2, 0.8)
        # --- 3/4 view
        cap.hide_render = True
        d = rad / math.sin(fov / 2) * 1.08
        az = math.radians(35)
        hdir = (front * math.cos(az) - side * math.sin(az)).normalized()
        el = math.radians(28)
        cam.location = c + hdir * d * math.cos(el) + Vector((0, 0, d * math.sin(el)))
        RL.look_at(cam, c)
        sc.render.filepath = os.path.join(VIEWS, f"{name}_34.png")
        bpy.ops.render.render(write_still=True)
        # --- eye height view (5 studs) with capsule beside the prop
        wid = abs(ext.dot(side)) if abs(side.x) > 0.5 else ext.y
        wid = ext.x if abs(side.x) > 0.5 else ext.y
        dep = ext.y if abs(side.x) > 0.5 else ext.x
        cap.location = c + side * (wid / 2 + 1.6)
        cap.location.z = 0
        cap.hide_render = False
        w = wid + 4.4
        hgt = max(ext.z, 5.5)
        d = max(6.0, (max(w * 0.5, hgt * 0.55)) / math.tan(fov / 2) * 1.12) + dep / 2
        mid = c + side * 1.2
        cam.location = Vector((mid.x, mid.y, 0)) + front * d + Vector((0, 0, 5.0))
        tz = max(min(hgt * 0.45, 5.0 + (hgt - 5.0) * 0.45), 1.8)
        RL.look_at(cam, (mid.x, mid.y, tz))
        sc.render.filepath = os.path.join(VIEWS, f"{name}_eye.png")
        bpy.ops.render.render(write_still=True)
        # hide this prop from following renders
        for o in col.objects:
            o.hide_render = True
        print(f"[render] {name}")
    L.log(f"render_props: {len(man['props']) if not ONLY else len(ONLY)} props rendered to previews/props/_views")


try:
    main()
except Exception:
    import traceback
    traceback.print_exc()
