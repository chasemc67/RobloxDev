"""Build every Lantern Grove prop: FBX export, previews, manifest, combined .blend.

Run (from anywhere):
  blender -b -P models/_src/build_all.py                      # everything
  blender -b -P models/_src/build_all.py -- --only lantern_small,giant_acorn
  blender -b -P models/_src/build_all.py -- --no-render       # FBX + manifest only
Then: python3 models/_src/make_docs.py  (contact sheet + README tables). build.sh does both.
"""
import bpy, sys, os, json, math, time, importlib
from mathutils import Vector, Matrix

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)

import lglib
import registry
for m in ("props_dressing", "props_moving", "props_hero", "props_p2p3", "props_variants", "props_cards", "props_pass6", "props_pass7", "props_pass8", "props_pass10",
          "props_v210b"):
    importlib.import_module(m)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ONLY = None
RENDER = "--no-render" not in argv
if "--only" in argv:
    ONLY = set(argv[argv.index("--only") + 1].split(","))
SAMPLES = 24

FBX_DIR = os.path.join(OUT, "fbx")
PREV_DIR = os.path.join(OUT, "previews")
os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(PREV_DIR, exist_ok=True)


# ----------------------------------------------------------------------------- scene setup
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "NONE"
    sc.unit_settings.scale_length = 1.0
    return sc


def setup_render(sc):
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.render.resolution_x = sc.render.resolution_y = 512
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = -0.1
    world = bpy.data.worlds.new("w")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.62, 0.70, 0.85, 1)
    bg.inputs["Strength"].default_value = 0.9


def make_stage(sc):
    """Ground, sun, reference capsule. Returns dict of helper objects (render only)."""
    col = bpy.data.collections.new("_stage")
    sc.collection.children.link(col)
    me = bpy.data.meshes.new("ground")
    import bmesh
    b = bmesh.new()
    bmesh.ops.create_grid(b, x_segments=1, y_segments=1, size=400)
    b.to_mesh(me)
    g = bpy.data.objects.new("ground", me)
    m = bpy.data.materials.new("ground")
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.32, 0.31, 0.29, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95
    me.materials.append(m)
    col.objects.link(g)
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 2.6
    sun.color = (1.0, 0.9, 0.78)
    sun.angle = math.radians(8)
    so = bpy.data.objects.new("sun", sun)
    so.rotation_euler = (math.radians(50), 0, math.radians(-35))
    col.objects.link(so)
    # 5-stud reference figure: capsule r 0.75
    pb = lglib.PB("_capsule")
    pb.lathe("Cream", [(0, 0)] + [(0.75 * math.sin(a * math.pi / 12), 0.75 - 0.75 * math.cos(a * math.pi / 12))
                                for a in range(1, 7)] +
             [(0.75 * math.sin(a * math.pi / 12), 4.25 - 0.75 * math.cos(a * math.pi / 12)) for a in range(6, 12)] +
             [(0, 5.0)], 16)
    cap_root, cap_objs = pb.finalize(col)
    cm = bpy.data.materials.new("capsule")
    cm.use_nodes = True
    cm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.25, 0.45, 0.85, 1)
    for o in cap_objs:
        o.data.materials[0] = cm
    cam = bpy.data.cameras.new("cam")
    cam.lens_unit = "FOV"
    cam.angle = math.radians(60)
    cam.clip_start = 0.05
    cam.clip_end = 2000
    co = bpy.data.objects.new("cam", cam)
    col.objects.link(co)
    sc.camera = co
    return dict(col=col, ground=g, capsule=cap_root, cam=co)


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def axis_helper(col, origin_bl, axis_bl, length, kind):
    """Red arrow (rotate axis) / blue arrow (slide axis) for previews only."""
    pb = lglib.PB("_axis")
    L = length
    pb.cyl("ToadRed" if kind == "rotate" else "Water", 0.06, 0.06, L, 8, loc=(0, 0, 0))
    pb.cyl("ToadRed" if kind == "rotate" else "Water", 0.2, 0.0, 0.45, 8, loc=(0, 0, L / 2 + 0.2))
    pb.sphere("Firefly", 0.16, segs=10, rings=6)
    root, objs = pb.finalize(col)
    q = Vector((0, 0, 1)).rotation_difference(Vector(axis_bl))
    root.matrix_world = Matrix.Translation(origin_bl) @ q.to_matrix().to_4x4()
    return root, objs


def render_previews(sc, stage, prop, root, objs):
    mn, mx = lglib.bbox_blender(objs)
    lift = -mn.z if mn.z < 0 else 0.0  # moving parts may hang below their pivot
    root.location = (0, 0, lift)
    bpy.context.view_layer.update()
    mn, mx = lglib.bbox_blender(objs)
    helpers = []
    if prop.get("motion"):
        mo = prop["motion"]
        ax = mo["axis_roblox"]
        axb = Vector((ax[0], -ax[2], ax[1]))
        size = max((mx - mn).length * 0.75, 2.0)
        h, ho = axis_helper(stage["col"], Vector((0, 0, lift)), axb, size, mo["type"])
        helpers.append(h)
        helpers += ho
    c = (mn + mx) / 2
    ext = mx - mn
    # --- eye-level view: camera at eye height 5, a few studs in front (south, Blender -Y),
    #     5-stud reference capsule standing beside the prop
    cap = stage["capsule"]
    side = ext.y > ext.x * 1.3  # long along Blender Y: look at its broad side from -X
    if prop.get("view") in ("x", "y"):
        side = prop["view"] == "x"
    f = Vector((1, 0, 0)) if side else Vector((0, 1, 0))
    r = Vector((0, -1, 0)) if side else Vector((1, 0, 0))
    wid = ext.y if side else ext.x
    dep = ext.x if side else ext.y
    fov = math.radians(60)
    cap.location = c + r * (wid / 2 + 1.4)
    cap.location.z = 0
    w = wid + 3.2
    hgt = max(ext.z, 5.4)
    d = max(4.6, (max(w, hgt * 1.05) / 2) / math.tan(fov / 2) * 1.1) + dep / 2
    cam = stage["cam"]
    eye = 5.0
    tz = max(min(hgt * 0.45, eye + (hgt - eye) * 0.5), 1.6)
    mid = c + r * 1.0
    camp = mid - f * d + r * (0.12 * d)
    cam.location = (camp.x, camp.y, eye)
    look_at(cam, (mid.x, mid.y, tz))
    cap.hide_render = False
    for o in cap.children:
        o.hide_render = False
    sc.render.filepath = os.path.join(PREV_DIR, f"{prop['name']}_eye.png")
    bpy.ops.render.render(write_still=True)
    # --- 3/4 elevated view (no capsule)
    cap.hide_render = True
    for o in cap.children:
        o.hide_render = True
    rad = max(ext.length / 2, 1.0)
    d = rad / math.sin(fov / 2) * 1.02
    az, el = math.radians(-125), math.radians(32)
    cam.location = (c.x + d * math.cos(el) * math.cos(az), c.y + d * math.cos(el) * math.sin(az), c.z + d * math.sin(el))
    look_at(cam, c)
    sc.render.filepath = os.path.join(PREV_DIR, f"{prop['name']}_34.png")
    bpy.ops.render.render(write_still=True)
    for h in helpers:
        bpy.data.objects.remove(h, do_unlink=True)
    root.location = (0, 0, 0)
    bpy.context.view_layer.update()


def export_fbx(root, objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0,
        axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True, add_leaf_bones=False,
        bake_anim=False, mesh_smooth_type="FACE", use_mesh_modifiers=True, object_types={"EMPTY", "MESH"},
        use_custom_props=False)


def part_info(objs):
    out = []
    for o in objs:
        mat = o.get("lg_mat") or o.name.split("__", 1)[1].split("_")[0]     # pass 10: renamed parts (WristFace)
        hexv, rbx, emis, transp, note = lglib.MATS[mat]
        mn, mx = lglib.bbox_blender([o])
        size, center = lglib.to_roblox_bbox(mn, mx)
        tex = lglib.TEX.get(mat)
        out.append(dict(mesh=o.name, material=mat, color=hexv, roblox_material=rbx,
                        texture=f"textures/{tex[0]}.png" if tex else None,
                        transparency=transp, tris=lglib.tri_count([o]), note=note,
                        bbox_center_from_origin=[round(v, 3) for v in center],
                        size=[round(v, 3) for v in size]))
        if mat in lglib.REFLECTANCE:        # v210: explicit Roblox MeshPart.Reflectance
            out[-1]["reflectance"] = lglib.REFLECTANCE[mat]
    return out


def main():
    t0 = time.time()
    sc = reset_scene()
    setup_render(sc)
    stage = make_stage(sc)
    manifest_path = os.path.join(OUT, "manifest.json")
    old = {}
    if os.path.exists(manifest_path):
        try:
            old = {p["name"]: p for p in json.load(open(manifest_path)).get("props", [])}
        except Exception:
            old = {}
    entries = {}
    built = []
    for prop in registry.PROPS:
        if ONLY and prop["name"] not in ONLY:
            continue
        name = prop["name"]
        col = bpy.data.collections.new(name)
        sc.collection.children.link(col)
        pb = lglib.PB(name)
        post = prop["fn"](pb)
        root, objs = pb.finalize(col, prop.get("smooth_angle", 40))
        if callable(post):
            post(root, objs)
            lglib.box_uv_objects(objs)
        tris = lglib.tri_count(objs)
        mn, mx = lglib.bbox_blender(objs)
        size, center = lglib.to_roblox_bbox(mn, mx)
        fbx = os.path.join(FBX_DIR, f"{name}.fbx")
        # hide other prop collections for export/render
        for c in sc.collection.children:
            if c.name not in ("_stage",):
                sc.view_layers[0].layer_collection.children[c.name].exclude = (c.name != name)
        export_fbx(root, objs, fbx)
        views = ("eye", "34")
        if RENDER:
            if prop.get("previews_fn"):     # pass 10: small props (VR wrist bracer) render their own views
                views = prop["previews_fn"](sc, stage, root, objs, PREV_DIR, look_at)
            else:
                render_previews(sc, stage, prop, root, objs)
        elif prop.get("previews_fn"):
            views = None                    # --no-render: keep the old preview list
        e = registry.manifest_entry(prop)
        e.update(dict(
            fbx=f"fbx/{name}.fbx",
            previews=[f"previews/{name}_{v}.png" for v in views] if views else old.get(name, {}).get("previews", []),
            bbox_size_studs=[round(v, 3) for v in size],
            bbox_center_from_origin=[round(v, 3) for v in center],
            triangles=tris,
            parts=part_info(objs),
        ))
        tgt = prop.get("target")
        if tgt:
            e["size_ratio_vs_target"] = [round(s / t, 2) if t else None for s, t in zip(size, tgt)]
        entries[name] = e
        built.append((name, tris, [round(v, 2) for v in size], tgt))
        print(f"[built] {name:32s} tris={tris:6d} size={[round(v, 2) for v in size]} target={tgt}")
    # merge manifest
    allp = []
    for prop in registry.PROPS:
        n = prop["name"]
        if n in entries:
            allp.append(entries[n])
        elif n in old:
            allp.append(old[n])
    manifest = registry.manifest_header()
    manifest["props"] = allp
    if os.path.exists(manifest_path):
        try:
            prev = json.load(open(manifest_path))
            for k in ("dressing", "world", "lights", "lights_note", "emissive"):
                if k in prev:
                    manifest[k] = prev[k]
            for k, v in prev.items():       # v210: keep any other top-level block (h9_emissive_dim, notes, ...)
                if k not in manifest:
                    manifest[k] = v
        except Exception:
            pass
    json.dump(manifest, open(manifest_path, "w"), indent=1)
    # combined blend (full builds only): lay props out on a grid, everything visible
    if ONLY is None:
        for c in sc.collection.children:
            sc.view_layers[0].layer_collection.children[c.name].exclude = False
        sc.view_layers[0].layer_collection.children["_stage"].exclude = True
        x = 0.0
        rowz = 0.0
        y = 0.0
        for prop in registry.PROPS:
            root = bpy.data.objects.get(prop["name"])
            if not root:
                continue
            objs = list(root.children)
            mn, mx = lglib.bbox_blender(objs)
            wdt = mx.x - mn.x
            if x + wdt > 120:
                x = 0.0
                y += rowz + 4
                rowz = 0.0
            root.location = (x - mn.x, y - mn.y, 0)
            x += wdt + 4
            rowz = max(rowz, mx.y - mn.y)
        for m in list(bpy.data.meshes):
            if m.users == 0:
                bpy.data.meshes.remove(m)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "lantern_grove_props.blend"), compress=True)
    print(f"[done] {len(built)} props in {time.time() - t0:.0f}s")


main()
