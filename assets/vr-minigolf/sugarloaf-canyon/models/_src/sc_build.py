"""Sugarloaf Canyon pass 1: build, export and preview every world piece; write models/manifest.json.

  python3 models/_src/sc_textures.py && python3 models/_src/sc_layout.py
  blender -b --factory-startup -P models/_src/sc_build.py [-- --only id1,id2] [--no-render]
Outputs: models/fbx/<file>.fbx, models/previews/<id>_{eye,34}.png, models/manifest.json,
         models/_src/_cache/tris/<file>.npy (Roblox-local triangles for sc_fitcheck.py)
"""
import bpy, sys, os, json, math, time
import numpy as np
from mathutils import Vector, Matrix

SRC = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import sclib as L
import sc_pieces as P
import sc_specs as SP

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ONLY = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
RENDER = "--no-render" not in argv
FBX = os.path.join(MODELS, "fbx")
PREV = os.path.join(MODELS, "previews")
CACHE = os.path.join(SRC, "_cache", "tris")
for d in (FBX, PREV, CACHE):
    os.makedirs(d, exist_ok=True)
LAYOUT = json.load(open(os.path.join(MODELS, "layout.json")))
WORLD = json.load(open(os.path.join(os.path.dirname(MODELS), "world", "world.json")))
WP = {p["id"]: p for p in WORLD["backdrop"]["pieces"]}
INST = {}
for e in LAYOUT["instances"]:
    INST.setdefault(e["piece"], []).append({k: e[k] for k in ("pos", "yaw", "scale", "src", "note") if k in e})


# ----------------------------------------------------------------------------- registry
def E(id_, group, build, notes, origin="base centre", preview=True, views=("eye", "34"), world_ids=None, az=35.0):
    return dict(id=id_, group=group, build=build, notes=notes, origin=origin, preview=preview, views=views,
                world_ids=world_ids or [], az=az)


REG = [
    E("old_sugarloaf_shell", "hero", P.old_sugarloaf,
      "Striped rock-face shell hugging the Old Sugarloaf terrain dome (r 72, summit y 208) 0.6 above it, strata ledges by "
      "world y, 4 sector parts + a 24-tall summit lollipop cactus part.", "dome base centre (80, 18, -130)",
      world_ids=["old_sugarloaf_dome"]),
    E("sunset_arch", "hero", P.sunset_arch, "Natural striped arch on the Crown's west rim: 16 thick, 50 wide, 46 tall, "
      "opening 30 x 34 (axis = local X, faces west/east).", world_ids=["sunset_arch"]),
    E("peppermint_dam", "hero", P.peppermint_dam,
      "88 x 101 x 10 peppermint-banded dam: body (part1) + crest deck at +99 (world 116), parapets to +101, iron railings, "
      "20-wide spillway slot (lip +91 = world 108) bridged by the crest deck, arched relief on the downstream face.",
      world_ids=["peppermint_dam"], az=205.0),
    E("intake_tower", "hero", P.intake_tower, "Domed peppermint intake tower in the reservoir, 14 x 26; base 8 below water.",
      world_ids=["intake_tower"]),
    E("ranger_station", "building", P.ranger_station, "Timber ranger station with porch, lookout cupola, flagpole.",
      world_ids=["ranger_station"]),
    E("junction_town", "building", P.junction_town,
      "5 false-front shops (Candy Co., Saloon, Assay, General Store, Taffy Pull) with peppermint awnings, boardwalk, barrels. "
      "Row along local X (80), fronts face local -Z.", world_ids=["junction_town"]),
    E("water_tower", "building", P.water_tower, "Candy-striped water tower, 10 x 30.", world_ids=["water_tower"]),
    E("mine_head", "building", P.mine_head, "Candy-striped headframe + sheave wheel, timber portal in a rock mound, ore cart."),
    E("gondola_station", "structure", P.gondola_station,
      "Sunset Gondola station (top + bottom use the same model): platform, peppermint roof, bull wheel at the open (front) end.",
      world_ids=["gondola_top_station", "gondola_bottom_station"]),
    E("cableway_trestle", "structure", P.cableway_trestle, "Old ore-cableway trestle 6 x 30 x 6 (x3).",
      world_ids=["cableway_trestles"]),
]
P.LIFTS.update(SP.lift_params(WORLD))
for k in P.LIFTS:
    REG.append(E(f"lift_frame_{k}", "lift", lambda k=k: P.lift_frame(k),
                 "Static lift shaft frame + headframe at the bottom boarding point and a railed gangway at the top level "
                 "running local -Z to the top boarding point.", "bottom boarding point"))
REG += [
    E("lift_cage", "lift", P.lift_cage, "Static 8 x 8 cage frame (floor, posts, side rails, roof frame at 9.5). Animate in Studio.",
      "cage floor centre"),
    E("ranger_footbridge", "bridge", P.ranger_footbridge, "Ranger Footbridge 54 x 6: plank deck, trestle bents, rope railings.",
      "deck top centre (walkway y)"),
    E("licorice_rope_bridge", "bridge", P.licorice_rope_bridge,
      "Licorice Rope Bridge 54 x 6: planks on licorice ropes, red-licorice hand ropes, end posts with a sign bar at 9.6.",
      "deck top centre (walkway y)"),
    E("walk_boardwalk_6x12", "walkway", lambda: P.walk_boardwalk(6, 12), "Boardwalk 6 x 12, top = pivot.", "deck top centre"),
    E("walk_boardwalk_8x12", "walkway", lambda: P.walk_boardwalk(8, 12), "Boardwalk 8 x 12 (Junction Walk width).",
      "deck top centre"),
    E("stair_flight_5", "walkway", P.stair_flight, "5 sandstone steps (rise 0.8, tread 1.5), 5.8 wide, timber nosings.",
      "bottom edge centre"),
    E("landing_6x4", "walkway", P.landing, "Sandstone landing 5.8 x 4 (scale Z = landing length / 4).", "top centre"),
    E("railing_12", "walkway", P.railing_12, "Railing run 12 long: timber posts every 4, rope rails, timber cap rail.",
      "base centre of the run"),
]
for h in SP.KIT_HEIGHTS:
    for ph in range(6):
        REG.append(E(f"cliff_w24_h{h}_p{ph}", "cliff_kit", lambda h=h, ph=ph: P.cliff_panel(f"cliff_w24_h{h}_p{ph}", h, ph),
                     f"Striped cliff panel 24 wide x {h} tall, strata phase {ph} (use when base y / 6 mod 6 = {ph}).",
                     "base centre of the front face", preview=(ph == 3)))
for h in SP.SLOT_HEIGHTS:
    for ph in range(6):
        REG.append(E(f"slot_w24_h{h}_p{ph}", "cliff_kit",
                     lambda h=h, ph=ph: P.cliff_panel(f"slot_w24_h{h}_p{ph}", h, ph, slot=True, seed=7),
                     f"Slot-canyon wall panel 24 x {h} with rock-candy crystal clusters, strata phase {ph}.",
                     "base centre of the front face", preview=(ph == 4)))
for k in "abcd":
    REG.append(E(f"hoodoo_spire_{k}", "scenery", lambda k=k: P.hoodoo_variant(k), "Striped hoodoo with capstone + gumdrop cap."))
for k in "abc":
    REG.append(E(f"crystal_cluster_{k}", "scenery", lambda k=k: P.crystal_variant(k), "Rock-candy crystal cluster."))
for k in "abc":
    REG.append(E(f"lollipop_cactus_{k}", "scenery", lambda k=k: P.cactus_variant(k),
                 "Saguaro with swirl lollipops and gumball fruit."))
for k in ("scrub_a", "scrub_b", "rock_a", "rock_b", "gumdrop_boulder_a", "gumdrop_boulder_b"):
    REG.append(E(k, "scenery", lambda k=k: P.scatter_variant(k), "Scatter variant (also baked into the scatter_* clusters)."))
for k in "ab":
    REG.append(E(f"sugar_dune_cap_{k}", "scenery", lambda k=k: P.dune_cap(k), "Powdered-sugar dune cap (half buried)."))
for name, cl in LAYOUT["clusters"].items():
    REG.append(E(name, "cluster", lambda name=name, cl=cl: P.cluster(name, cl),
                 f"Merged {cl['kind']} cluster: {len(cl['members'])} members baked at their world pos/yaw/size.",
                 f"cluster pivot {cl['pivot']} (world)", world_ids=[m["id"] for m in cl["members"]][:60]))
REG += [
    E('rim_silhouette', 'far_card', P.rim_silhouette,
      '64-wide low-poly striped rim silhouette; visible stretches only, CastShadow off.', views=('34',)),
    E("distant_mesa_card", "far_card", lambda: P.card_piece("distant_mesa_card", "CardMesa", 400, 200, 5, 30,
                                                            "bent alpha-cut card 400 x 200 (10 tris)"),
      "Distant mesa card (scale per instance).", "base centre", views=("34",)),
    E("butte_spire_card", "far_card", lambda: P.card_piece("butte_spire_card", "CardButte", 80, 200, 3, 8,
                                                           "bent alpha-cut card 80 x 200 (6 tris)"),
      "Butte spire card.", "base centre", views=("34",)),
    E("far_arch_card", "far_card", lambda: P.card_piece("far_arch_card", "CardArch", 420, 300, 6, 30,
                                                        "bent alpha-cut card 420 x 300 (12 tris)"),
      "Far natural arch card.", "base centre", views=("34",)),
    E("far_butte_card", "far_card", lambda: P.card_piece("far_butte_card", "CardTwins", 260, 380, 4, 20,
                                                         "bent alpha-cut card 260 x 380 (8 tris)"),
      "Sugarloaf Twins card.", "base centre", views=("34",)),
    E("sun_disc", "sky", P.sun_disc, "Sun disc card 260 x 260 (Neon).", "centre", views=("34",)),
    E("cloud_streak", "sky", P.cloud_streak, "Cloud streak card 700 x 70.", "centre", views=("34",)),
]
for k in "abc":
    REG.append(E(f"balloon_{k}", "sky", lambda k=k: P.balloon(k), "Candy-striped hot-air balloon 24 x 30.", "basket bottom",
                 views=("34",)))


# ----------------------------------------------------------------------------- scene
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    L.lglib._scratch = None
    sc = bpy.context.scene
    sc.unit_settings.system = "NONE"
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "TEXTURE"
    sh.show_shadows = True
    sh.shadow_intensity = 0.35
    sh.show_cavity = True
    sh.cavity_type = "WORLD"
    sc.display.light_direction = (-0.55, -0.35, 0.75)
    sc.render.resolution_x, sc.render.resolution_y = 640, 480
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w")
    w.color = (0.95, 0.62, 0.55)
    sc.world = w
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens_unit = "FOV"
    cam.data.clip_start = 0.3
    cam.data.clip_end = 20000
    sc.collection.objects.link(cam)
    sc.camera = cam
    return sc, cam


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def export(root, objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0,
                             axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True,
                             add_leaf_bones=False, bake_anim=False, mesh_smooth_type="FACE", use_mesh_modifiers=True,
                             object_types={"EMPTY", "MESH"}, use_custom_props=False)


def cache_tris(objs, fname):
    arr = []
    for o in objs:
        me = o.data
        me.calc_loop_triangles()
        co = np.empty(len(me.vertices) * 3, np.float32)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        idx = np.empty(len(me.loop_triangles) * 3, np.int32)
        me.loop_triangles.foreach_get("vertices", idx)
        t = co[idx.reshape(-1, 3)]
        arr.append(t)
    t = np.concatenate(arr) if arr else np.zeros((0, 3, 3), np.float32)
    rb = np.stack([t[..., 0], t[..., 2], -t[..., 1]], axis=-1)      # Blender -> Roblox local
    np.save(os.path.join(CACHE, fname + ".npy"), rb.astype(np.float32))


def mesh_info(o):
    mat = L.lglib.mat_of(o.name)
    hexv, rbx, emis, transp, note = L.MATS[mat]
    mn, mx = L.bbox_blender([o])
    size, center = L.to_roblox_bbox(mn, mx)
    tex = L.TEX.get(mat)
    d = dict(mesh=o.name, material=mat, color=hexv, roblox_material=rbx, tris=L.tri_count([o]),
             texture=f"textures/{tex[0]}.png" if tex else None, tile_studs=tex[1] if tex else None,
             transparency=transp, cast_shadow=mat not in L.NO_SHADOW, size=[round(v, 2) for v in size],
             bbox_center_from_origin=[round(v, 2) for v in center])
    if emis:
        d["neon"] = True
    if mat in L.CARDS:
        d["alpha"] = "SurfaceAppearance AlphaMode Transparency (alpha-cut PNG)"
    return d


def ground(sc, z, size, mat="FloorSand"):
    import bmesh
    me = bpy.data.meshes.new("_ground")
    b = bmesh.new()
    bmesh.ops.create_grid(b, x_segments=1, y_segments=1, size=size / 2)
    bmesh.ops.translate(b, vec=(0, 0, z), verts=b.verts)
    uv = b.loops.layers.uv.new("UVMap")
    for f in b.faces:
        for l in f.loops:
            l[uv].uv = (l.vert.co.x / 8, l.vert.co.y / 8)
    b.to_mesh(me)
    me.materials.append(L.lglib.get_mat(mat))
    o = bpy.data.objects.new("_ground", me)
    sc.collection.objects.link(o)
    return o


def capsule(sc, loc):
    import bmesh
    m = bpy.data.materials.new("_ref")
    m.diffuse_color = (0.25, 0.45, 0.85, 1)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.25, 0.45, 0.85, 1)
    me = bpy.data.meshes.new("_cap")
    b = bmesh.new()
    bmesh.ops.create_uvsphere(b, u_segments=12, v_segments=8, radius=1.0)
    for v in b.verts:
        v.co.z = v.co.z + (3.5 if v.co.z > 0 else 0) + 1.0
    b.to_mesh(me)
    me.materials.append(m)
    o = bpy.data.objects.new("_capsule", me)
    o.location = loc
    sc.collection.objects.link(o)
    return o


def render(sc, cam, path, loc, target, fov):
    cam.data.angle = math.radians(fov)
    cam.location = Vector(loc)
    look_at(cam, target)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def previews(sc, cam, entry, objs):
    mn, mx = L.bbox_blender(objs)
    c = (mn + mx) / 2
    ext = mx - mn
    rad = max(ext.length / 2, 2.0)
    out = []
    group = entry["group"]
    gz = 0.0 if group not in ("sky",) else mn.z - 20
    if group == "far_card":
        gz = -2.0
    ground(sc, gz - 0.02, max(4000, rad * 12), "MesaTop" if group != "sky" else "FloorSand")
    for v in entry["views"]:
        fp = os.path.join(PREV, f"{entry['id']}_{v}.png")
        if v == "34":
            fov = 45
            d = rad / math.sin(math.radians(fov) / 2) * 1.02
            az, el = math.radians(entry["az"]), math.radians(24)
            loc = c + Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))) * d
            cap = capsule(sc, (mx.x + 2.5, c.y, 0.0)) if group not in ("sky", "far_card") else None
            render(sc, cam, fp, loc, c, fov)
        else:
            fov = 60
            hmax = max(ext.z, 2.0)
            d = max(ext.x, ext.y, hmax * 1.25, 6.0) * 1.05 + max(ext.x, ext.y) / 2
            if entry["id"] in ("old_sugarloaf_shell",):
                d = 260
            az = math.radians(entry["az"] - 17)
            loc = Vector((c.x + math.sin(az) * d, c.y + math.cos(az) * d, gz + 5.0))
            tgt = Vector((c.x, c.y, gz + min(hmax * 0.45, max(5.0, hmax * 0.45))))
            cap = capsule(sc, (mx.x + 2.5, c.y, gz))
            render(sc, cam, fp, loc, tgt, fov)
        if cap:
            bpy.data.objects.remove(cap)
        out.append(os.path.relpath(fp, MODELS))
    return out


# ----------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    mp = os.path.join(MODELS, "manifest.json")
    old = {}
    if os.path.exists(mp) and ONLY:
        try:
            old = {p["id"]: p for p in json.load(open(mp))["pieces"]}
        except Exception:
            old = {}
    entries = {}
    warn = []
    for entry in REG:
        pid = entry["id"]
        if ONLY and pid not in ONLY:
            continue
        sc, cam = reset()
        col = bpy.data.collections.new(pid)
        sc.collection.children.link(col)
        pbs = entry["build"]()
        parts, all_objs = [], []
        for pb in pbs:
            if len(pbs) == 1:
                pb.name = pid
            root, objs = L.finalize(pb, col, pb.y0)
            fn = pb.name
            export(root, objs, os.path.join(FBX, fn + ".fbx"))
            cache_tris(objs, fn)
            meshes = [mesh_info(o) for o in objs]
            if entry['group'] in ('far_card', 'sky'):
                for m in meshes:
                    m['cast_shadow'] = False
            for m in meshes:
                if m["tris"] >= 20000:
                    warn.append(f"{fn}: {m['mesh']} has {m['tris']} tris (>= 20k)")
            mn, mx = L.bbox_blender(objs)
            size, center = L.to_roblox_bbox(mn, mx)
            parts.append(dict(file=f"fbx/{fn}.fbx", role=pb.role, strata_y0=pb.y0, tris=L.tri_count(objs),
                              meshparts=len(objs), bbox_size=[round(v, 2) for v in size],
                              bbox_center_from_origin=[round(v, 2) for v in center], meshes=meshes))
            all_objs += objs
        mn, mx = L.bbox_blender(all_objs)
        size, center = L.to_roblox_bbox(mn, mx)
        prev = []
        if RENDER and entry["preview"]:
            prev = previews(sc, cam, entry, all_objs)
        mats = sorted({m["material"] for p in parts for m in p["meshes"]})
        e = dict(id=pid, group=entry["group"], notes=entry["notes"], pivot=entry["origin"],
                 files=[p["file"] for p in parts], tris=sum(p["tris"] for p in parts),
                 max_mesh_tris=max(m["tris"] for p in parts for m in p["meshes"]),
                 meshparts=sum(p["meshparts"] for p in parts), materials=mats,
                 bbox_size=[round(v, 2) for v in size], bbox_center_from_origin=[round(v, 2) for v in center],
                 world_json_size=[WP[w]["size"] for w in entry["world_ids"] if w in WP][:1] or None,
                 world_json_ids=entry["world_ids"], instances=INST.get(pid, []), parts=parts, previews=prev)
        entries[pid] = e
        print(f"[built] {pid:28s} parts={len(parts)} tris={e['tris']:6d} max_mesh={e['max_mesh_tris']:6d} "
              f"mp={e['meshparts']:2d} size={e['bbox_size']} inst={len(e['instances'])} {time.time() - t0:.0f}s", flush=True)
    allp = [entries.get(r["id"]) or old.get(r["id"]) for r in REG]
    allp = [p for p in allp if p]
    man = dict(
        name="Sugarloaf Canyon world pieces (pass 2)",
        generated=time.strftime("%Y-%m-%d %H:%M"),
        units="Roblox studs, +Y up, +X east, -Z north (world/world.json axes). 1 Blender unit = 1 stud.",
        fbx_export=f"Blender {bpy.app.version_string} for pass2 affected files; prior files Blender 4.5; unit NONE, axis_forward -Z, axis_up Y, scale 1 (FBX_SCALE_UNITS), embedded PNG textures",
        import_settings=("Import 3D at scale 1 (Stud), keep hierarchy: one MeshPart per material named <part>__<Material>. "
                         "Anchored, CanCollide/CanQuery/CanTouch false (decoration only). CastShadow false where "
                         "cast_shadow is false (cards, sky, Neon, glass cores) and on everything in far_card/sky."),
        placement=LAYOUT["placement"],
        strata=("Material Strata = SurfaceAppearance ColorMap textures/strata.png; UV V = world y / 36, so band "
                "floor(y/6) mod 6 shows strata colour 1-6 (course.md order). Kit pieces come in phases p0-p5: use phase "
                "(base_y / 6) mod 6 and keep base_y on a multiple of 6. Hero pieces/clusters bake their own world y (strata_y0)."),
        textures="textures/*.png 512x512 (tiling, 8-bit); card_*.png and sun_disc.png are RGBA alpha-cut cards",
        layout="layout.json (all instances; clusters list their merged world.json members)",
        warnings=warn,
        totals=dict(pieces=len(allp), files=sum(len(p["files"]) for p in allp),
                    placed_instances=len(LAYOUT["instances"])),
        pieces=allp)
    existing=json.load(open(mp)) if os.path.exists(mp) else {}
    existing.update(man)
    json.dump(existing, open(mp, "w"), indent=1)
    print(f"[done] {len(entries)} pieces in {time.time() - t0:.0f}s; warnings: {warn}")


main()
