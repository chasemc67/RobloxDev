"""Pass 3: build, export and preview every world piece; write models/world/manifest.json and the `world` section
of models/manifest.json.

  python3 models/_src/world_layout.py                       # placements -> models/world/layout.json
  blender -b -P models/_src/world_build.py [-- --only id1,id2] [-- --no-render]
Outputs: models/world/fbx/<id>[_partN].fbx, models/world/previews/<id>_*.png
"""
import bpy, sys, os, json, math, time, importlib
from mathutils import Vector, Matrix

SRC = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import lglib
import world_pieces as WP

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ONLY = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
RENDER = "--no-render" not in argv
SAMPLES = 20
OUT = os.path.join(MODELS, "world")
FBX = os.path.join(OUT, "fbx")
PREV = os.path.join(OUT, "previews")
os.makedirs(FBX, exist_ok=True)
os.makedirs(PREV, exist_ok=True)
LAYOUT = json.load(open(os.path.join(OUT, "layout.json")))
WPIECES_JSON = {p["id"]: p for p in WP.WORLD["backdrop"]["pieces"]}


# ----------------------------------------------------------------------------- registry
def P(id_, kind, build, notes, origin="base centre (pos = world base centre)", world_id=None, size_target=None):
    return dict(id=id_, kind=kind, build=build, notes=notes, origin=origin, world_id=world_id or id_,
                size_target=size_target)


def single(fn, *a, **k):
    return lambda: [fn(*a, **k)]


PIECES = [
    P("hollow_tree_world_shell", "hero_tree", WP.hero_shell_parts,
      "Giant hollow trunk shell around H9: outer r 45.84 (flared base), inner r 38.84, 100 tall, hollow up to y+78 "
      "under a dome with a 14-radius oculus shaft open through the top. Heartwood Door: 14 wide x 20 high arch at map "
      "angle 53.1 deg (splays to 17.5 wide inside). Parts 1-4 = trunk wall sectors (bark outside, warm Heartwood "
      "inside), 5 = buttress roots (to r 65.8, trimmed so they never touch H8/H9 felt, walls, walkways or lantern "
      "posts), 6 = outer details (door frame + lanterns, glowing windows, bracket fungi, moss), 7 = interior "
      "lantern strings / wall lanterns / glowing mushrooms (all far above or outside H9).",
      origin="trunk base centre [-74, 39.6, 6] (world.json hollow_tree.center); yaw 0",
      size_target=[91.7, 100, 91.7]),
    P("hollow_tree_crown", "hero_tree", WP.crown_parts,
      "Golden/orange crown: 7 lumpy leaf masses (6 in a ring leaving a ~16-radius light gap over the oculus, 1 high "
      "mass west of it), limbs rising from the trunk-top rim, 12 big hanging lanterns under the outer crown.",
      origin="crown base centre [-74, 139.6, 6] (= trunk base + 100); limbs dip ~4 below it into the trunk top",
      size_target=[176, 78, 176]),
    P("sister_tree_nw", "background", single(WP.giant_tree, "sister_tree_nw", (60, 90, 60),
                                             ["Gold", "Gold", "Pumpkin", "Gold", "MapleRed"], 9.0, 44.0, 71, masses=8,
                                             door=True, lanterns=4),
      "Golden cousin of the hero tree (hollow_tree look: furrowed bark, buttress roots, lumpy masses) with a glowing "
      "arched door and windows facing local +Z.", size_target=[60, 90, 60]),
    P("sister_tree_sw", "background", single(WP.giant_tree, "sister_tree_sw", (55, 80, 55),
                                             ["MapleRed", "MapleRed", "Pumpkin", "MapleRed"], 7.6, 38.0, 72, masses=7,
                                             lanterns=3, squat=1.05),
      "Red maple giant on the SW hills.", size_target=[55, 80, 55]),
    P("sister_tree_ne", "background", single(WP.giant_tree, "sister_tree_ne", (50, 75, 50),
                                             ["Gold", "Pumpkin", "Gold", "Gold"], 9.5, 30.0, 73, masses=7, lanterns=3,
                                             squat=0.85, roots=9),
      "Squat golden oak giant on the NE shoulder above the village.", size_target=[50, 75, 50]),
]

for wid, wname, strands, lan, seed, tight in (("grand_falls_curtain", "Grand Falls", 1, False, 1, False),
                                             ("twin_falls_curtain", "Twin Falls", 2, False, 2, True),
                                             ("lantern_falls_curtain", "Lantern Falls", 1, True, 3, False)):
    wf = [w for w in WP.WORLD["waterfalls"] if w["name"] == wname][0]
    pl = LAYOUT[wid][0]
    PIECES.append(P(wid, "waterfall", single(WP.waterfall, wid, wf, pl["pos"], pl["yaw"], strands, lan, seed, tight),
                    f"{wname} curtain {wf['top']} -> {wf['bottom']}: translucent Water sheet (thin closed slab), Foam "
                    "ribbons, plunge foam + Mist puffs, backing slate slab and lip/base rocks"
                    + (", two strands split by a rock" if strands == 2 else "")
                    + (", lantern posts at the lip and floating lanterns at the base" if lan else "")
                    + ". Add a Beam/ParticleEmitter mist at the bottom in Studio.",
                    origin="plunge-pool centre at the bottom water level (world.json pos); local +Z = flow direction"))
for v, style, seed in (("a", "strata", 1), ("b", "columns", 2), ("c", "overhang", 3), ("d", "corner", 4)):
    PIECES.append(P(f"highland_cliff_kit_{v}", "rock", single(WP.cliff_face, f"highland_cliff_kit_{v}", 40, 30, 14, style, seed),
                    f"Highland slate cliff face, style '{style}' (40 x 30 x 14 unscaled), mossy ledges, autumn shrubs "
                    "on the lip. Front = local +Z. Scale per instance (sy = scarp height / 30, sx = sz = sqrt(sy)).",
                    world_id="highland_cliff_kit", origin="base centre of the face (foot of the scarp); front local +Z"))
for v, style, seed in (("a", "strata", 11), ("b", "overhang", 12), ("c", "columns", 13)):
    PIECES.append(P(f"terrace_rock_faces_{v}", "rock", single(WP.cliff_face, f"terrace_rock_faces_{v}", 24, 12, 6, style, seed, 1.0),
                    f"Terrace rock facing, style '{style}' (24 x 12 x 6 unscaled) for the village / mill / root terrace "
                    "walls and the tree mound. Front = local +Z.", world_id="terrace_rock_faces",
                    origin="base centre (foot of the wall); front local +Z"))
PIECES += [
    P("old_lantern_tower", "background", single(WP.lantern_tower),
      "Ruined octagonal stone tower (NE side broken away), timber loft with a shingle roof and a big amber lantern, "
      "glowing slit windows, ivy moss and rubble. Door faces local +Z."),
    P("hill_mushroom_houses", "background", single(WP.mushroom_village),
      "4 mushroom houses (scaled mushroom_house_medium, red / orange / gold caps) with lit windows, toadstools, a "
      "lantern string and path stones."),
    P("mere_dock", "decor", single(WP.mere_dock),
      "Plank dock on pilings, two lantern posts at the water end (local -X), rope coil and crate. Pilings reach 2.7 "
      "below the deck reference.", origin="water-line reference: deck top at local y 0.86 (world 9.36, water 8)"),
    P("mere_lantern_boat", "decor", single(WP.lantern_boat),
      "Tiny paper boat carrying a paper lantern (Glow core). 8 instances drifting on Lantern Mere.",
      world_id="mere_lantern_boats", origin="waterline centre"),
    P("sky_lantern", "sky", single(WP.sky_lantern),
      "Pass 4: small round paper sky lantern 1.1 x 1.35 x 1.1, glowing washi texture (SkyPaper = textures/paper_glow.png, "
      "self-lit) with a Glow flame at the open bottom. 24 instances around the crown (drift upward).",
      world_id="sky_lanterns", origin="bottom centre"),
    P("cloud_card_a", "sky", single(WP.cloud_card, "cloud_card_a", 1), "Golden cumulus card (13 sunlit puffs + 7 "
      "peach underside puffs), 600 x 120 x 200. Faces the play area.", world_id="cloud_banks"),
    P("cloud_card_b", "sky", single(WP.cloud_card, "cloud_card_b", 2, (520, 140, 180)), "Cumulus card variant.",
      world_id="cloud_banks"),
]
for v in "abc":
    for mix in WP.TREELINE_MIXES:
        nm = f"treeline_clump_{v}_{mix}"
        PIECES.append(P(nm, "tree_line", single(WP.treeline_clump, nm, v, mix),
                        f"Tree-line clump variant {v} ({'4 round crowns' if v == 'a' else '6 mixed + a spire' if v == 'b' else '5 tall layered'}), "
                        f"colour mix {mix.replace('_', '+')}, 40 x 45 x 40 unscaled (scale y to the world.json size).",
                        world_id="tree_line", origin="base centre; trunks reach 3 below"))
for v in "ab":
    PIECES.append(P(f"far_hill_{v}", "far_hill", single(WP.far_hill, f"far_hill_{v}", v),
                    f"Far forested hill impostor shell ({'single dome' if v == 'a' else 'double hump'}), 280 x 100 x 160 "
                    "unscaled, open bottom, autumn patches + canopy bumps. Long axis local X.", world_id="far_hills"))
for v in "abc":
    PIECES.append(P(f"mountain_{v}", "mountain", single(WP.mountain, f"mountain_{v}", v),
                    "Low-poly distant mountain silhouette (pass 4 colours): foot = horizon haze #EDC6A8 (fades into the sky), hazy peach "
                    "slopes, dusty mauve ridges, warm-white snowcaps; 500 x 320 x 300 unscaled. "
                    "Long axis local X.", world_id="mountains"))


# ----------------------------------------------------------------------------- scene
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    lglib._scratch = None
    sc = bpy.context.scene
    sc.unit_settings.system = "NONE"
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.render.resolution_x = sc.render.resolution_y = 640
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = 0.2
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.62, 0.8, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.6
    sun.data.color = (1.0, 0.82, 0.62)
    sun.rotation_euler = Vector((0.6, 0.55, -0.55)).normalized().to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens_unit = "FOV"
    cam.data.angle = math.radians(50)
    cam.data.clip_start = 0.5
    cam.data.clip_end = 8000
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


def part_info(objs, tile_scale):
    out = []
    for o in objs:
        mat = lglib.mat_of(o.name)
        hexv, rbx, emis, transp, note = lglib.MATS[mat]
        mn, mx = lglib.bbox_blender([o])
        size, center = lglib.to_roblox_bbox(mn, mx)
        tex = lglib.TEX.get(mat)
        out.append(dict(mesh=o.name, material=mat, color=hexv, roblox_material=rbx,
                        texture=f"textures/{tex[0]}.png" if tex else None,
                        tile_studs=round(tex[1] * tile_scale, 2) if tex else None, transparency=transp,
                        tris=lglib.tri_count([o]), bbox_center_from_origin=[round(v, 2) for v in center],
                        size=[round(v, 2) for v in size]))
    return out


def ground_plane(sc, z=0.0, size=4000):
    import bmesh
    me = bpy.data.meshes.new("_ground")
    b = bmesh.new()
    bmesh.ops.create_grid(b, x_segments=1, y_segments=1, size=size / 2)
    bmesh.ops.translate(b, vec=(0, 0, z), verts=b.verts)
    b.to_mesh(me)
    m = bpy.data.materials.new("_g")
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.2, 0.26, 0.12, 1)
    me.materials.append(m)
    o = bpy.data.objects.new("_ground", me)
    sc.collection.objects.link(o)
    return o


def render_views(sc, cam, pid, objs, views):
    mn, mx = lglib.bbox_blender(objs)
    c = (mn + mx) / 2
    ext = mx - mn
    rad = max(ext.length / 2, 1.0)
    paths = []
    for vname, az, el, fov, tgt, dist_k in views:
        cam.data.angle = math.radians(fov)
        t = Vector(tgt) if tgt is not None else c
        d = rad / math.sin(math.radians(fov) / 2) * dist_k
        cam.location = t + Vector((math.cos(math.radians(el)) * math.cos(math.radians(az)),
                                   math.cos(math.radians(el)) * math.sin(math.radians(az)),
                                   math.sin(math.radians(el)))) * d
        cam.data.clip_end = d * 4 + 100
        look_at(cam, t)
        fp = os.path.join(PREV, f"{pid}_{vname}.png")
        sc.render.filepath = fp
        bpy.ops.render.render(write_still=True)
        paths.append(os.path.relpath(fp, OUT))
    return paths


def h9_felt_boxes(col):
    """Preview helper: H9 felt + walls (world) relative to the trunk origin, as flat boxes."""
    import world_fit as WF, dressing_lib as DL, numpy as np
    H = WF.holes_world(WP.WORLD)
    pb = lglib.PB("_h9")
    for h in H:
        if h["number"] not in (8, 9):
            continue
        for f in h["felt"]:
            c = DL.to_world(h, f["center"])
            yaw = f.get("yaw", 0) + h["world_yaw"]
            loc = WP.wbl(c)
            pb.box("Felt", (f["size"][0], f["size"][1], 0.5), loc=(loc.x, loc.y, loc.z - 0.25), rot=(0, 0, yaw))
        for w in h["walls"]:
            c = DL.to_world(h, w["center"])
            yaw = w.get("yaw", 0) + h["world_yaw"]
            loc = WP.wbl(c)
            pb.box("Limestone", (w["size"][0], w["size"][2], w["size"][1]), loc=loc, rot=(0, 0, yaw))
    for p in WP.WORLD["paths"]:
        if p["id"] not in ("p_h8_h9", "p_h7_h8"):
            continue
        for s in p["segments"]:
            a, b = WP.wbl(s["start"]), WP.wbl(s["end"])
            d = b - a
            L = d.length
            if L < 0.1:
                continue
            pb.box("Thatch", (p["width"], L, 0.3), loc=(a + b) / 2, rot=(0, 0, math.degrees(math.atan2(d.y, d.x)) - 90))
    root, objs = pb.finalize(col)
    return root, objs


def main():
    t0 = time.time()
    entries = {}
    old = {}
    mp = os.path.join(OUT, "manifest.json")
    if os.path.exists(mp):
        try:
            old = {p["id"]: p for p in json.load(open(mp))["pieces"]}
        except Exception:
            old = {}
    for piece in PIECES:
        pid = piece["id"]
        if ONLY and pid not in ONLY:
            continue
        sc, cam = reset()
        col = bpy.data.collections.new(pid)
        sc.collection.children.link(col)
        pbs = piece["build"]()
        parts = []
        all_objs = []
        multi = len(pbs) > 1
        for k, pb in enumerate(pbs):
            if not multi:
                pb.name = pid
            root, objs = pb.finalize(col)
            if pb.post:
                pb.post(root, objs)
                lglib.box_uv_objects(objs)
            fn = f"{pb.name}.fbx"
            export(root, objs, os.path.join(FBX, fn))
            tris = lglib.tri_count(objs)
            mn, mx = lglib.bbox_blender(objs)
            size, center = lglib.to_roblox_bbox(mn, mx)
            parts.append(dict(file=f"fbx/{fn}", role=getattr(pb, "role", "whole piece"), tris=tris,
                              bbox_size_studs=[round(v, 2) for v in size],
                              bbox_center_from_origin=[round(v, 2) for v in center],
                              texture_tile_scale=pb.tile_scale, meshes=part_info(objs, pb.tile_scale)))
            if getattr(pb, "lights", None):
                parts[-1]["lights_world"] = pb.lights
                parts[-1]["lights_note"] = ("PointLight positions (world studs): wall_lantern_cluster -> Range 12, "
                                            "Brightness 1.2, #FFB347; wall_mushroom_clump -> Range 9, Brightness 0.8, "
                                            "#7FE3D0. Parent each to an invisible anchored Attachment/Part.")
            if getattr(pb, "root_angles", None):
                parts[-1]["root_angles_blender_deg_and_reach"] = [[round(a, 1), round(r, 1)] for a, r in pb.root_angles]
            all_objs += objs
        mn, mx = lglib.bbox_blender(all_objs)
        size, center = lglib.to_roblox_bbox(mn, mx)
        tris = sum(p["tris"] for p in parts)
        previews = []
        if RENDER:
            if pid == "hollow_tree_world_shell":
                ground_plane(sc, -0.3)
                previews += render_views(sc, cam, pid, all_objs, [
                    ("34", -125, 22, 50, None, 1.05),
                    ("door", math.degrees(WP.DOOR_A) - 18, 6, 60, (math.cos(WP.DOOR_A) * 46, math.sin(WP.DOOR_A) * 46, 10), 0.32)])
                # cutaway: hide the two sectors facing the camera, show H8/H9 felt + walkways
                h9r, h9o = h9_felt_boxes(col)
                for o in all_objs:
                    if "part1" in o.name or "part4" in o.name or "part6" in o.name:
                        o.hide_render = True
                previews += render_views(sc, cam, pid, all_objs + h9o, [
                    ("cutaway", math.degrees(WP.DOOR_A) - 40, 38, 55, (0, 0, 10), 0.8),
                    ("top_fit", -90, 89.5, 60, (5, 0, 0), 0.75)])
            else:
                el = 22 if piece["kind"] not in ("mountain", "far_hill", "sky") else 12
                ground_plane(sc, min(0.0, mn.z) - 0.05 if piece["kind"] != "sky" else -30)
                previews += render_views(sc, cam, pid, all_objs, [("34", -110, el, 50, None, 1.08)])
        e = dict(id=pid, kind=piece["kind"], world_json_id=piece["world_id"], origin=piece["origin"],
                 notes=piece["notes"], files=[p["file"] for p in parts], tris=tris, max_part_tris=max(p["tris"] for p in parts),
                 bbox_size_studs=[round(v, 2) for v in size], bbox_center_from_origin=[round(v, 2) for v in center],
                 size_target_world_json=piece["size_target"] or WPIECES_JSON.get(piece["world_id"], {}).get("size"),
                 instances=LAYOUT.get(pid, []), parts=parts, previews=previews)
        entries[pid] = e
        print(f"[built] {pid:34s} parts={len(parts)} tris={tris:6d} max={e['max_part_tris']:6d} size={e['bbox_size_studs']} "
              f"inst={len(e['instances'])} {time.time() - t0:.0f}s")
    allp = []
    for piece in PIECES:
        if piece["id"] in entries:
            allp.append(entries[piece["id"]])
        elif piece["id"] in old:
            allp.append(old[piece["id"]])
    man = dict(
        section="Lantern Grove world pieces (pass 3)",
        units="Roblox world studs, +Y up, +X east, -Z north (same as world/world.json and holes.json)",
        placement=("For every instance: Model:PivotTo(CFrame.new(pos) * CFrame.Angles(0, math.rad(yaw), 0)); "
                   "if scale is given use Model:ScaleTo(scale[2]) when the 3 values are equal, otherwise resize "
                   "each MeshPart (Size and its offset from the pivot multiplied per axis). pos is the piece origin "
                   "(base centre unless `origin` says otherwise). Every part FBX of a piece shares that origin."),
        import_settings=("File > Import 3D, scale unit Stud, keep hierarchy; one MeshPart per material named "
                         "<part>__<Material>; Anchored, CanCollide/CanQuery/CanTouch false (decoration only), "
                         "CastShadow false on Neon/Water/Foam/Mist and on far pieces (mountains, far hills, clouds)."),
        texture_note=("Same textures/ as the props; world pieces use box UVs with tile_studs = prop tile x "
                      "texture_tile_scale (listed per mesh)."),
        fbx_export="same as props: Blender 4.5, unit NONE, axis_forward -Z, axis_up Y, FBX_SCALE_UNITS, embedded PNGs",
        fit_check="see world/fitcheck_world.txt (world_fitcheck.py)",
        pieces=allp)
    json.dump(man, open(mp, "w"), indent=1)
    gm = os.path.join(MODELS, "manifest.json")
    g = json.load(open(gm))
    g["world"] = dict(manifest="world/manifest.json", readme="README.md#world-pieces",
                      pieces=[dict(id=p["id"], kind=p["kind"], files=["world/" + f for f in p["files"]],
                                   origin=p["origin"], tris=p["tris"], bbox_size_studs=p["bbox_size_studs"],
                                   instances=p["instances"]) for p in allp])
    for p in allp:
        for q in p.get("parts", []):
            if q.get("lights_world"):
                g["world"]["h9_interior_lights"] = dict(note=q["lights_note"], source=q["file"], lights=q["lights_world"])
    json.dump(g, open(gm, "w"), indent=1)
    print(f"[done] {len(entries)} pieces in {time.time() - t0:.0f}s")


main()
