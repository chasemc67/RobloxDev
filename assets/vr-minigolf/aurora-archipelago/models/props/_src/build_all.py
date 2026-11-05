"""Build every Aurora Archipelago P1 prop: FBX per prop, per-hole merged dressing (hole frame, one mesh per material),
previews (eye height 5 + capsule, 3/4), manifest.json and aurora_props_p1.blend.
Adapted from lantern-grove/models/_src/build_all.py.

  blender -b --factory-startup -P out_props/_src/build_all.py [-- --no-render] [-- --only a,b]
"""
import bpy, bmesh, sys, os, json, math, time, importlib
from mathutils import Vector, Matrix

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import aalib, registry, holesdata as D
for m in ("props_kit", "props_movers", "props_holes"):
    importlib.import_module(m)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDER = "--no-render" not in argv
ONLY = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
FBX_DIR, PREV_DIR = os.path.join(OUT, "fbx"), os.path.join(OUT, "previews")
os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(PREV_DIR, exist_ok=True)
LOG = os.path.join(os.path.dirname(OUT), "PROGRESS.md")


def log(s):
    print("[build] " + s, flush=True)
    import datetime
    with open(LOG, "a", encoding="utf8") as f:
        f.write(datetime.datetime.now().isoformat() + " - PROPS " + s + "\n")


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "NONE"
    sc.unit_settings.scale_length = 1.0
    return sc


def setup_render(sc):
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 16
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = d.type == "OPTIX"
        sc.cycles.device = "GPU"
    except Exception as e:
        print("GPU setup failed", e)
    sc.render.resolution_x = sc.render.resolution_y = 512
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.exposure = 0.0
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.36, 0.38, 0.62, 1)
    bg.inputs["Strength"].default_value = 0.8


def make_stage(sc):
    col = bpy.data.collections.new("_stage")
    sc.collection.children.link(col)
    me = bpy.data.meshes.new("ground")
    b = bmesh.new()
    bmesh.ops.create_grid(b, x_segments=1, y_segments=1, size=600)
    b.to_mesh(me)
    g = bpy.data.objects.new("ground", me)
    m = bpy.data.materials.new("ground")
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (0.55, 0.57, 0.68, 1)
    p.inputs["Roughness"].default_value = 0.95
    me.materials.append(m)
    col.objects.link(g)
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.2
    sun.color = (1.0, 0.93, 0.85)
    sun.angle = math.radians(8)
    so = bpy.data.objects.new("sun", sun)
    so.rotation_euler = (math.radians(50), 0, math.radians(-35))
    col.objects.link(so)
    pb = aalib.PB("_capsule")
    pb.lathe("Cream", [(0, 0)] + [(0.75 * math.sin(a * math.pi / 12), 0.75 - 0.75 * math.cos(a * math.pi / 12)) for a in range(1, 7)] +
             [(0.75 * math.sin(a * math.pi / 12), 4.25 - 0.75 * math.cos(a * math.pi / 12)) for a in range(6, 12)] + [(0, 5.0)], 16)
    cap_root, cap_objs = pb.finalize(col)
    cm = bpy.data.materials.new("capsule")
    next(n for n in cm.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.25, 0.45, 0.85, 1)
    for o in cap_objs:
        o.data.materials[0] = cm
    cam = bpy.data.cameras.new("cam")
    cam.lens_unit = "FOV"
    cam.angle = math.radians(60)
    cam.clip_start = 0.05
    cam.clip_end = 3000
    co = bpy.data.objects.new("cam", cam)
    col.objects.link(co)
    sc.camera = co
    return dict(col=col, ground=g, capsule=cap_root, cam=co)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def axis_helper(col, origin_bl, axis_bl, length, kind):
    pb = aalib.PB("_axis")
    pb.cyl("MoveRed" if kind == "rotate" else "Ice", 0.06, 0.06, length, 8)
    pb.cyl("MoveRed" if kind == "rotate" else "Ice", 0.2, 0.0, 0.45, 8, loc=(0, 0, length / 2 + 0.2))
    pb.sphere("Lime", 0.16, segs=10, rings=6)
    root, objs = pb.finalize(col)
    q = Vector((0, 0, 1)).rotation_difference(Vector(axis_bl))
    root.matrix_world = Matrix.Translation(origin_bl) @ q.to_matrix().to_4x4()
    return [root] + objs


def render_previews(sc, stage, prop, root, objs):
    mn, mx = aalib.bbox_blender(objs)
    lift = -mn.z if mn.z < 0 else 0.0
    root.location = (0, 0, lift)
    bpy.context.view_layer.update()
    mn, mx = aalib.bbox_blender(objs)
    helpers = []
    if prop.get("motion") and prop["motion"].get("type") in ("rotate", "slide", "swing"):
        ax = prop["motion"]["axis_roblox"]
        helpers = axis_helper(stage["col"], Vector((0, 0, lift)), Vector((ax[0], -ax[2], ax[1])), max((mx - mn).length * 0.6, 2.0),
                              "rotate" if prop["motion"]["type"] != "slide" else "slide")
    c, ext = (mn + mx) / 2, mx - mn
    cap, cam = stage["capsule"], stage["cam"]
    side = ext.y > ext.x * 1.3
    f = Vector((1, 0, 0)) if side else Vector((0, 1, 0))
    r = Vector((0, -1, 0)) if side else Vector((1, 0, 0))
    wid, dep = (ext.y, ext.x) if side else (ext.x, ext.y)
    fov = math.radians(60)
    cap.location = c + r * (wid / 2 + 1.4)
    cap.location.z = 0
    hgt = max(ext.z, 5.4)
    d = max(4.6, (max(wid + 3.2, hgt * 1.05) / 2) / math.tan(fov / 2) * 1.1) + dep / 2
    tz = max(min(hgt * 0.45, 5.0 + (hgt - 5.0) * 0.5), 1.6)
    mid = c + r * 1.0
    camp = mid - f * d + r * (0.12 * d)
    cam.location = (camp.x, camp.y, 5.0)
    look_at(cam, (mid.x, mid.y, tz))
    for o in [cap] + list(cap.children):
        o.hide_render = False
    sc.render.filepath = os.path.join(PREV_DIR, f"{prop['name']}_eye.png")
    bpy.ops.render.render(write_still=True)
    for o in [cap] + list(cap.children):
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
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0,
                             axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True, add_leaf_bones=False,
                             bake_anim=False, mesh_smooth_type="FACE", use_mesh_modifiers=True, object_types={"EMPTY", "MESH"},
                             use_custom_props=False)


def part_info(objs):
    out = []
    for o in objs:
        mat = aalib.mat_of(o.name)
        hexv, rbx, emis, transp, note = aalib.MATS[mat]
        mn, mx = aalib.bbox_blender([o])
        size, center = aalib.to_roblox_bbox(mn, mx)
        tex = aalib.TEX.get(mat)
        out.append(dict(mesh=o.name, material=mat, color=hexv, roblox_material=rbx, emission=emis,
                        texture=f"textures/{tex[0]}.png" if tex else None, transparency=transp, tris=aalib.tri_count([o]),
                        note=note, bbox_center_from_origin=[round(v, 3) for v in center], size=[round(v, 3) for v in size]))
    return out


def place_matrix(pl):
    s = pl.get("scale", 1.0)
    s = [s, s, s] if not isinstance(s, (list, tuple)) else s
    return Matrix.Translation(aalib.R(*pl["pos"])) @ Matrix.Rotation(math.radians(pl.get("yaw", 0.0)), 4, "Z") @ \
        Matrix.Diagonal((s[0], s[2], s[1], 1.0))


def xform_light(L, pl):
    p = place_matrix(pl) @ aalib.R(*L["pos"])
    return [round(p.x, 3), round(p.z, 3), round(-p.y, 3)]


def main():
    t0 = time.time()
    sc = reset_scene()
    setup_render(sc)
    stage = make_stage(sc)
    built = {}
    entries = []
    for prop in registry.PROPS:
        name = prop["name"]
        if ONLY and name not in ONLY:
            continue
        col = bpy.data.collections.new(name)
        sc.collection.children.link(col)
        pb = aalib.PB(name)
        prop["fn"](pb)
        root, objs = pb.finalize(col, prop.get("smooth_angle", 40))
        tris = aalib.tri_count(objs)
        assert tris < 20000 and all(aalib.tri_count([o]) < 20000 for o in objs), name
        mn, mx = aalib.bbox_blender(objs)
        size, center = aalib.to_roblox_bbox(mn, mx)
        for c in sc.collection.children:
            if c.name != "_stage":
                sc.view_layers[0].layer_collection.children[c.name].exclude = (c.name != name)
        export_fbx(root, objs, os.path.join(FBX_DIR, f"{name}.fbx"))
        if RENDER:
            render_previews(sc, stage, prop, root, objs)
        ex = prop.get("extra") or {}
        e = registry.manifest_entry(prop)
        for k in ("extra",):
            e.pop(k, None)
        e.update(dict(fbx=f"fbx/{name}.fbx", previews=[f"previews/{name}_eye.png", f"previews/{name}_34.png"],
                      bbox_size_studs=[round(v, 3) for v in size], bbox_center_from_origin=[round(v, 3) for v in center],
                      triangles=tris, mesh_parts=len(objs), materials=sorted({aalib.mat_of(o.name) for o in objs}),
                      parts=part_info(objs), pivot=prop["origin"], collision="none (CanCollide false); decoration only"))
        if ex.get("lights"):
            e["lights_local"] = ex["lights"]
        built[name] = (prop, root, objs, tris)
        entries.append(e)
        print(f"[built] {name:34s} tris={tris:6d} size={[round(v, 2) for v in size]}", flush=True)
    log(f"built {len(built)} props, {sum(b[3] for b in built.values())} tris (single copies)")

    # ---------------------------------------------------------------- per-hole merged dressing (hole frame)
    hole_files = []
    if ONLY is None:
        hcol = bpy.data.collections.new("_holes")
        sc.collection.children.link(hcol)
        for n in sorted(D.H):
            bms = {}
            contents = []
            for name, (prop, root, objs, tris) in built.items():
                ex = prop.get("extra") or {}
                if not ex.get("merge"):
                    continue
                for pl in prop["placements"]:
                    if pl["hole"] != n:
                        continue
                    M = place_matrix(pl)
                    contents.append(dict(prop=name, anchor=pl.get("anchor"), pos=pl["pos"], yaw=pl.get("yaw", 0.0), scale=pl.get("scale", 1.0), tris=tris))
                    for o in objs:
                        b = bms.setdefault(aalib.mat_of(o.name), bmesh.new())
                        me = o.data.copy()
                        me.transform(M)
                        b.from_mesh(me)
                        bpy.data.meshes.remove(me)
            if not bms:
                continue
            objs_h = []
            for mat, b in sorted(bms.items()):
                me = bpy.data.meshes.new(f"aa_h{n:02d}_dressing__{mat}")
                b.to_mesh(me)
                b.free()
                me.materials.clear()
                me.materials.append(aalib.get_mat(mat))
                ob = bpy.data.objects.new(me.name, me)
                hcol.objects.link(ob)
                objs_h.append(ob)
            # split into files < 20k tris (whole materials per file; any single material mesh must be < 20k)
            groups, cur, cnt = [], [], 0
            for ob in sorted(objs_h, key=lambda o: -aalib.tri_count([o])):
                t = aalib.tri_count([ob])
                assert t < 20000, ob.name
                placed = False
                for g in groups:
                    if g[1] + t < 19500:
                        g[0].append(ob)
                        g[1] += t
                        placed = True
                        break
                if not placed:
                    groups.append([[ob], t])
            for gi, (obs, t) in enumerate(groups):
                fname = f"aa_h{n:02d}_dressing" + (f"_{'abcdefgh'[gi]}" if len(groups) > 1 else "")
                root = bpy.data.objects.new(fname, None)
                hcol.objects.link(root)
                for ob in obs:
                    ob.parent = root
                    if len(groups) > 1:
                        ob.name = ob.name.replace(f"aa_h{n:02d}_dressing__", fname + "__")
                for c in sc.collection.children:
                    if c.name != "_stage":
                        sc.view_layers[0].layer_collection.children[c.name].exclude = (c.name != "_holes")
                export_fbx(root, obs, os.path.join(FBX_DIR, fname + ".fbx"))
                mn, mx = aalib.bbox_blender(obs)
                size, center = aalib.to_roblox_bbox(mn, mx)
                hole_files.append(dict(file=f"fbx/{fname}.fbx", hole=n, frame="hole frame: origin = holes.json world_offset, rotated by world_yaw (PivotTo(holeRoot))",
                                       triangles=t, mesh_parts=len(obs), materials=sorted(aalib.mat_of(o.name) for o in obs),
                                       bbox_size_studs=[round(v, 3) for v in size], bbox_center_from_origin=[round(v, 3) for v in center],
                                       parts=part_info(obs), contents=contents if gi == 0 else "see first file of this hole"))
            log(f"H{n}: dressing {sum(g[1] for g in groups)} tris in {len(groups)} file(s), {len(contents)} instances")

    # ---------------------------------------------------------------- instances + lights
    holes_block = {}
    lights = []
    for name, (prop, root, objs, tris) in built.items():
        ex = prop.get("extra") or {}
        for pl in prop["placements"]:
            n = pl["hole"]
            h = holes_block.setdefault(n, dict(hole=n, world_offset=D.H[n]["world_offset"], world_yaw=D.H[n]["world_yaw"], instances=[]))
            h["instances"].append(dict(prop=name, fbx=f"fbx/{name}.fbx", merged_into_dressing=bool(ex.get("merge")), anchor=pl.get("anchor"),
                                       pos=pl["pos"], yaw=pl.get("yaw", 0.0), scale=pl.get("scale", 1.0), tris=tris,
                                       world_pos=[round(v, 3) for v in D.to_world(n, pl["pos"])], note=pl.get("note", "")))
            for L in ex.get("lights", []):
                hp_ = xform_light(L, pl)
                lights.append(dict(prop=name, hole=n, pos_hole=hp_, pos_world=[round(v, 3) for v in D.to_world(n, hp_)],
                                   range=L["range"], brightness=L["brightness"], color=L["color"], note=L.get("note", "")))
        for wi in ex.get("world_instances", []):
            for L in ex.get("lights", []):
                pw = place_matrix(wi) @ aalib.R(*L["pos"])
                lights.append(dict(prop=name, hole=None, pos_world=[round(pw.x, 3), round(pw.z, 3), round(-pw.y, 3)],
                                   range=L["range"], brightness=L["brightness"], color=L["color"], note=wi.get("note", "")))
    world_inst = []
    for name, (prop, root, objs, tris) in built.items():
        for wi in (prop.get("extra") or {}).get("world_instances", []):
            world_inst.append(dict(prop=name, fbx=f"fbx/{name}.fbx", pos=wi["pos"], yaw=wi.get("yaw", 0.0), scale=wi.get("scale", 1.0), tris=tris, note=wi.get("note", "")))
    for e in entries:
        ex = next(p for p in registry.PROPS if p["name"] == e["name"]).get("extra") or {}
        e["world_instances"] = ex.get("world_instances", [])
        e["class"] = ex.get("cls")
        e["merged_into_hole_dressing"] = bool(ex.get("merge"))
    manifest = dict(
        course="Aurora Archipelago (VR mini golf) - P1 props",
        pass_="props-p1", units="studs; 1 Blender unit = 1 stud; positions/sizes Roblox Y-up",
        axes="Roblox (x,y,z) = Blender (x,-z,y); FBX axis_forward -Z, axis_up Y, scale 1.0, FBX_SCALE_UNITS, embedded textures",
        coordinate_note="placements are HOLE-LOCAL (holes.json frame): world = R_y(world_yaw)*local + world_offset; pos = where the prop ORIGIN goes; yaw deg about +Y. world_instances are world coordinates.",
        structure="Each FBX = one root empty (<prop>) + one child mesh per material (<prop>__<Material>), all sharing the prop origin. Set MeshPart Color/Material/Transparency from parts[]; Neon parts are glow cores.",
        collision="Decoration only: CanCollide=false, CanQuery=false, CanTouch=false, Anchored=true on every MeshPart. Gameplay collision = holes.json parts.",
        textures=dict(dir="textures/", size="512x512 tiling PNG (8-bit RGB), also embedded in each FBX", materials={m: dict(texture=f"textures/{t}.png", tile_studs=k) for m, (t, k) in aalib.TEX.items()}),
        materials={k: dict(color=v[0], roblox_material=v[1], emission=v[2], transparency=v[3], note=v[4]) for k, v in aalib.MATS.items()},
        props=entries, hole_dressing_files=hole_files, holes=[holes_block[k] for k in sorted(holes_block)],
        world_instances=world_inst, lights=lights)
    if ONLY is None:
        json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
        for c in sc.collection.children:
            sc.view_layers[0].layer_collection.children[c.name].exclude = False
        sc.view_layers[0].layer_collection.children["_stage"].exclude = True
        x = y = rowz = 0.0
        for name, (prop, root, objs, tris) in built.items():
            mn, mx = aalib.bbox_blender(objs)
            wdt = mx.x - mn.x
            if wdt > 150:
                root.location = (0, -400, 0)
                continue
            if x + wdt > 160:
                x, y, rowz = 0.0, y + rowz + 6, 0.0
            root.location = (x - mn.x, y - mn.y, 0)
            x += wdt + 6
            rowz = max(rowz, mx.y - mn.y)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "aurora_props_p1.blend"), compress=True)
    log(f"build_all done in {time.time() - t0:.0f}s: {len(built)} prop FBX + {len(hole_files)} hole dressing FBX, {len(lights)} lights")


main()
