"""Assemble the whole lobby from the exported FBX files + builder_Lobby.luau instances and render
previews/spawn_view.png (camera at Roblox (100, 5, 100) looking north, 90 deg hfov, golden hour) and
previews/topdown.png (orthographic). Blender: -P render_lobby.py [-- --only=spawn|topdown]"""
import bpy, os, sys, math, json
from mathutils import Vector, Matrix

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import bwlib as L  # noqa: E402
import render_lib as RL  # noqa: E402
import parse_builder  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
argv = [a for x in argv for a in x.replace("=", " ").split(" ") if a]
ONLY = argv[argv.index("--only") + 1] if "--only" in argv else None
# The builder puts the lantern-tree canopy base at Y 10, which floats it (trunks are part of the mesh).
# For the render it stands on the sand; flagged as a spec question in README / pass1_summary.md.
Y_OVERRIDE = {"bw_lantern_tree_canopy": -0.1}


def main():
    man = json.load(open(os.path.join(OUT, "manifest.json")))
    props = {p["name"]: p for p in man["props"]}
    sc = L.reset_scene()
    RL.setup_cycles(sc, samples=96, res=(1920, 1080))
    env = bpy.data.collections.new("_env")
    sc.collection.children.link(env)
    assets = bpy.data.collections.new("_assets")
    sc.collection.children.link(assets)
    lobby = bpy.data.collections.new("lobby")
    sc.collection.children.link(lobby)
    # sun low in the WSW (golden hour), #FFB46A
    RL.sun(env, (0.86, 0.42, -0.22), hexv="#FFB46A", energy=4.2, angle_deg=2.0)
    # ocean, sand strip
    RL.plane(env, "ocean", (3000, 3000), (110, -75, -4.0), RL.flat_mat("ocean", "#3E8FB0", 0.18))
    RL.plane(env, "shallows", (240, 70), (110, -15, -3.9), RL.flat_mat("shallows", "#6FC2D1", 0.3))
    sand = RL.flat_mat("sand", "#F0C9A0", 0.95)
    me_sand = RL.plane(env, "sand", (220, 40), (110, -20, -0.1), sand)
    # sand skirt sloping into the water
    import bmesh
    b = bmesh.new()
    vs = [b.verts.new(p) for p in ((0, 0, -0.1), (220, 0, -0.1), (220, 8, -4.2), (0, 8, -4.2))]
    b.faces.new(vs)
    me = bpy.data.meshes.new("sand_slope")
    b.to_mesh(me)
    me.materials.append(sand)
    o = bpy.data.objects.new("sand_slope", me)
    env.objects.link(o)
    # import every asset once
    src = {}
    for name, p in props.items():
        objs = RL.import_fbx(os.path.join(OUT, p["fbx"]), assets)
        src[name] = objs
    RL.fix_imported_materials(neon_strength=8.0)
    assets.hide_render = True
    for o in assets.objects:
        o.hide_render = True
    # instances
    inst = man["instances"]
    n = 0
    for i in inst:
        a = i["asset"]
        p = props[a]
        x, y, z = i["position"]
        y = Y_OVERRIDE.get(a, y)
        sx, sy, sz = i.get("scale", [1, 1, 1])
        if a == "bw_windmill_blades":
            hub = props["bw_windmill"]["blade_hub"]["local"]
            wm = next(j for j in inst if j["asset"] == "bw_windmill")
            x, y, z = wm["position"][0] + hub[0], wm["position"][1] + hub[1], wm["position"][2] + hub[2]
        Mw = (Matrix.Translation((x, -z, y)) @ Matrix.Rotation(math.radians(i.get("yaw", 0.0)), 4, "Z") @
              Matrix.Diagonal((sx, sz, sy, 1)))
        for so in src[a]:
            ob = bpy.data.objects.new(f"{i['id']}__{so.name}", so.data)
            ob.matrix_world = Mw @ so.matrix_world
            lobby.objects.link(ob)
        n += 1
    print("instances placed", n)
    # spawn pad marker (thin disc) so the spawn reads in the topdown
    if ONLY in (None, "spawn"):
        RL.world(sc, "#F6B88E", 0.75, zenith_hex="#8EA9D6")
        cam = RL.camera(env, "spawn_cam", fov_deg=90.0)
        cam.location = (100.0, -100.0, 5.0)
        cam.rotation_euler = (math.radians(90), 0, 0)
        beauty = os.path.join(OUT, "previews", "spawn_view.png")
        sc.render.filepath = beauty
        bpy.ops.render.render(write_still=True)
        # fog pass: view distance -> lobby.json fog (start 180, end 420) as grey emission
        fogp = os.path.join(SRC, "_fog_pass.png")
        fm = bpy.data.materials.new("_fog")
        fm.use_nodes = True
        nt = fm.node_tree
        for nd in list(nt.nodes):
            if nd.type != "OUTPUT_MATERIAL":
                nt.nodes.remove(nd)
        outn = next(nd for nd in nt.nodes if nd.type == "OUTPUT_MATERIAL")
        cd = nt.nodes.new("ShaderNodeCameraData")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 180.0
        mr.inputs["From Max"].default_value = 420.0
        em = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(cd.outputs["View Distance"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], em.inputs["Strength"])
        nt.links.new(em.outputs["Emission"], outn.inputs["Surface"])
        bpy.context.view_layer.material_override = fm
        wf = bpy.data.worlds.new("fogworld")
        wf.use_nodes = True
        bgn = next(nd for nd in wf.node_tree.nodes if nd.type == "BACKGROUND")
        bgn.inputs["Color"].default_value = (1, 1, 1, 1)
        bgn.inputs["Strength"].default_value = 0.45
        old_world = sc.world
        sc.world = wf
        sun_obj = bpy.data.objects.get("sun")
        sun_obj.hide_render = True
        sc.cycles.samples, sc.cycles.use_denoising = 16, False
        sc.view_settings.view_transform = "Standard"
        sc.render.filepath = fogp
        bpy.ops.render.render(write_still=True)
        bpy.context.view_layer.material_override = None
        sc.world = old_world
        sun_obj.hide_render = False
        sc.cycles.samples, sc.cycles.use_denoising = 64, True
        import numpy as np
        ib = bpy.data.images.load(beauty)
        ifg = bpy.data.images.load(fogp)
        B = np.array(ib.pixels[:]).reshape(-1, 4)
        F = np.array(ifg.pixels[:]).reshape(-1, 4)[:, :1]
        fogc = np.array([*L.lin("#F2A57E"), 1.0])
        # images load as linear floats from sRGB PNGs; fog factor stored via Standard transform -> undo sRGB
        f = np.where(F <= 0.04045, F / 12.92, ((F + 0.055) / 1.055) ** 2.4)
        f = np.clip(f, 0.0, 1.0) * 0.85
        ib.pixels[:] = (B * (1 - f) + fogc * f).ravel()
        ib.pixels[:] = ib.pixels[:]
        ib.filepath_raw = beauty
        ib.file_format = "PNG"
        ib.save()
        L.log("render_lobby: previews/spawn_view.png (fog composited from depth, lobby.json start 180 end 420)")
    if ONLY in (None, "overview"):
        RL.world(sc, "#F6B88E", 0.8, zenith_hex="#8EA9D6")
        sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
        cam = RL.camera(env, "over_cam", fov_deg=70.0)
        cam.location = (100.0, -150.0, 45.0)
        RL.look_at(cam, (105.0, -62.0, 0.0))
        sc.render.filepath = os.path.join(OUT, "previews", "overview.png")
        bpy.ops.render.render(write_still=True)
        L.log("render_lobby: previews/overview.png (extra: elevated view from behind spawn)")
    if ONLY in (None, "topdown"):
        RL.world(sc, "#F6B88E", 0.9, zenith_hex="#8EA9D6")
        sc.render.resolution_x, sc.render.resolution_y = 1760, 1360
        sc.cycles.samples = 64
        cam = RL.camera(env, "top_cam", ortho=310.0)
        cam.data.sensor_fit = "HORIZONTAL"
        cam.location = (110.0, -122.0, 300.0)
        cam.rotation_euler = (0, 0, 0)
        sc.render.filepath = os.path.join(OUT, "previews", "topdown.png")
        bpy.ops.render.render(write_still=True)
        L.log("render_lobby: previews/topdown.png")


try:
    main()
except Exception:
    import traceback
    traceback.print_exc()
