"""Hole assembly previews: holes.json felt/rails/hazards + hero placements + per-hole dressing (manifest.json).

  blender -b -P models/_src/assembly.py [-- --holes 1,3] [-- --views tee,top,over] [-- --samples 32]
Writes previews/assembly_hNN_tee.png (VR eye view from the tee, 1280x720), assembly_hNN_top.png (ortho cutaway
with collision boxes) and assembly_hNN.png (3/4 overview).
Look: textured materials, golden-hour sun, warm sky gradient, mist haze + lantern glare (compositor).
The leaf-litter ground is a PREVIEW-ONLY heightfield (dressing_lib.Ground); it is never exported (Studio uses Terrain).
Rails are dressed with repeated rail_straight_4 pieces along every plain rail wall (top = wall top, 1 stud tall).
"""
import bpy, bmesh, sys, os, json, math, importlib
import numpy as np
from mathutils import Vector, Matrix

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
COURSE = os.path.dirname(OUT)
sys.path.insert(0, SRC)
import lglib, registry, dressing_lib as DL
for m in ("props_dressing", "props_moving", "props_hero", "props_p2p3", "props_variants", "props_cards", "props_pass6", "props_pass7", "props_pass8"):
    importlib.import_module(m)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
HOLES = [int(x) for x in argv[argv.index("--holes") + 1].split(",")] if "--holes" in argv else None
VIEWS = argv[argv.index("--views") + 1].split(",") if "--views" in argv else ["tee", "top", "over"]
SAMPLES = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 32

holes = json.load(open(os.path.join(COURSE, "holes.json")))["holes"]
MAN = json.load(open(os.path.join(OUT, "manifest.json")))
man = {p["name"]: p for p in MAN["props"]}
DRESS = MAN.get("dressing", {}).get("holes", {})
REG = {p["name"]: p for p in registry.PROPS}

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "NONE"
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4
sc.cycles.transparent_max_bounces = 4
sc.view_settings.view_transform = "Standard"
sc.view_settings.exposure = 0.3

# ----------------------------------------------------------------------------- world + golden-hour light
world = bpy.data.worlds.new("w")
sc.world = world
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes["Background"]
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
cr = nt.nodes.new("ShaderNodeValToRGB")
nt.links.new(tc.outputs["Generated"], sep.inputs[0])
nt.links.new(sep.outputs["Z"], cr.inputs["Fac"])
els = cr.color_ramp.elements
els[0].position, els[0].color = 0.0, (0.5, 0.3, 0.16, 1)
els[1].position, els[1].color = 0.8, (0.22, 0.42, 0.85, 1)
e = els.new(0.5)
e.color = (1.0, 0.66, 0.34, 1)
e = els.new(0.6)
e.color = (0.85, 0.75, 0.62, 1)
nt.links.new(cr.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.1
world.mist_settings.start = 25
world.mist_settings.depth = 160
world.mist_settings.falloff = "LINEAR"

sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 4.8
sun.data.color = (1.0, 0.74, 0.46)
sun.data.angle = math.radians(3)
# low sun ahead-left of a north-facing player (play direction = Blender +Y), ~24 deg elevation
d = Vector((0.55, -0.62, -0.42)).normalized()   # light travel direction
sun.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
sc.collection.objects.link(sun)
fill = bpy.data.objects.new("fill", bpy.data.lights.new("fill", "SUN"))
fill.data.energy = 0.5
fill.data.color = (0.6, 0.7, 1.0)
fill.rotation_euler = Vector((-0.4, 0.7, -0.6)).normalized().to_track_quat("-Z", "Y").to_euler()
fill.data.use_shadow = False
sc.collection.objects.link(fill)

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.lens_unit = "FOV"
cam.data.sensor_fit = "HORIZONTAL"
cam.data.clip_end = 3000
sc.collection.objects.link(cam)
sc.camera = cam

# ----------------------------------------------------------------------------- compositor: haze + glow
sc.view_layers[0].use_pass_mist = True
sc.use_nodes = True
ct = sc.node_tree
for n in list(ct.nodes):
    ct.nodes.remove(n)
rl = ct.nodes.new("CompositorNodeRLayers")
mul = ct.nodes.new("CompositorNodeMath")
mul.operation = "MULTIPLY"
mul.inputs[1].default_value = 0.2
HAZE = mul.inputs[1]
mix = ct.nodes.new("CompositorNodeMixRGB")
mix.inputs[2].default_value = (1.0, 0.72, 0.42, 1)
glare = ct.nodes.new("CompositorNodeGlare")
glare.glare_type = "FOG_GLOW"
glare.quality = "MEDIUM"
try:
    glare.threshold = 1.2
    glare.size = 7
except Exception:
    pass
comp = ct.nodes.new("CompositorNodeComposite")
ct.links.new(rl.outputs["Mist"], mul.inputs[0])
ct.links.new(mul.outputs[0], mix.inputs[0])
ct.links.new(rl.outputs["Image"], mix.inputs[1])
ct.links.new(mix.outputs[0], glare.inputs[0])
ct.links.new(glare.outputs[0], comp.inputs[0])


# ----------------------------------------------------------------------------- materials / helpers
def simple_mat(name, rgba, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Alpha"].default_value = alpha
    b.inputs["Roughness"].default_value = 0.9
    return m


FELT = lglib.get_mat("Felt")
WATER = lglib.get_mat("Water")
WALL = simple_mat("wall", (0.8, 0.15, 0.1, 1), 0.3)
PIT = simple_mat("pit", (0.02, 0.015, 0.01, 1))
GROUND = bpy.data.materials.new("ground_litter")
GROUND.use_nodes = True
_g = GROUND.node_tree
_tex = _g.nodes.new("ShaderNodeTexImage")
_tex.image = bpy.data.images.load(os.path.join(lglib.TEX_DIR, "leaf_litter.png"), check_existing=True)
_g.links.new(_tex.outputs["Color"], _g.nodes["Principled BSDF"].inputs["Base Color"])
_g.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95


def box_obj(name, size_bl, mat, col, tile=4.0):
    me = bpy.data.meshes.new(name)
    b = bmesh.new()
    bmesh.ops.create_cube(b, size=1.0)
    bmesh.ops.scale(b, vec=size_bl, verts=b.verts)
    lglib.box_uv_bmesh(b, tile)
    b.to_mesh(me)
    b.free()
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    return o


def ground_obj(h, col):
    G = DL.Ground(h, margin=84.0)
    ny, nx = G.H.shape
    me = bpy.data.meshes.new("ground")
    b = bmesh.new()
    vs = [[b.verts.new(lglib.R(G.X[i, j], G.H[i, j], G.Z[i, j])) for j in range(nx)] for i in range(ny)]
    for i in range(ny - 1):
        for j in range(nx - 1):
            b.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
    lglib.box_uv_bmesh(b, 9.0)
    b.to_mesh(me)
    b.free()
    me.materials.append(GROUND)
    o = bpy.data.objects.new("ground", me)
    col.objects.link(o)
    o.matrix_world = Matrix.Identity(4)
    # far apron to the horizon, just under the heightfield edge
    far = box_obj("ground_far", (1600, 1600, 0.1), GROUND, col, tile=12.0)
    far.location = (0, 0, float(G.H.min()) - 0.6)
    return G


def build_prop_template(name, col):
    p = REG[name]
    pb = lglib.PB(name)
    post = p["fn"](pb)
    root, objs = pb.finalize(col, p.get("smooth_angle", 40))
    if callable(post):
        post(root, objs)
        lglib.box_uv_objects(objs)
    return root, objs


def place(root_objs, name, pl, col, base_len_z=None):
    root, objs = root_objs
    new_root = bpy.data.objects.new(f"{name}_inst", None)
    col.objects.link(new_root)
    for o in objs:
        c = bpy.data.objects.new(o.name + "_i", o.data)
        col.objects.link(c)
        c.parent = new_root
    x, y, z = pl["pos"]
    s = pl.get("scale", 1.0)
    S = (s, s, s) if isinstance(s, (int, float)) else (s[0], s[2], s[1])
    if pl.get("scale_z_to") and base_len_z:
        S = (1, pl["scale_z_to"] / base_len_z, 1)
    new_root.location = lglib.R(x, y, z)
    new_root.rotation_euler = (0, 0, math.radians(pl.get("yaw", 0)))
    new_root.scale = S
    return new_root


def felt_obj(f, col):
    sx, sz = f["size"]
    th = 1.4
    o = box_obj(f["id"], (sx, sz, th), FELT, col, tile=8.0)
    yaw = math.radians(f.get("yaw", 0))
    tilt = Matrix.Identity(4)
    if f.get("slope"):
        L = sx if f["slope"]["axis"] == "x" else sz
        ang = math.atan2(f["slope"]["rise"], L)
        tilt = Matrix.Rotation(-ang, 4, "X") if f["slope"]["axis"] == "z" else Matrix.Rotation(-ang, 4, "Y")
    o.matrix_world = (Matrix.Translation(lglib.R(*f["center"])) @ Matrix.Rotation(yaw, 4, "Z") @ tilt @
                      Matrix.Translation((0, 0, -th / 2)))
    return o


templates = {}
tcol = bpy.data.collections.new("_templates")
sc.collection.children.link(tcol)


def get_template(name):
    if name not in templates:
        templates[name] = build_prop_template(name, tcol)
    return templates[name]


def render(path, w, h_):
    sc.render.resolution_x, sc.render.resolution_y = w, h_
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


for h in holes:
    n = h["number"]
    if HOLES and n not in HOLES:
        continue
    col = bpy.data.collections.new(f"h{n:02d}")
    sc.collection.children.link(col)
    for c in sc.collection.children:
        sc.view_layers[0].layer_collection.children[c.name].exclude = c.name != col.name
    G = ground_obj(h, col)
    xs, zs = [], []
    for f in h["felt"]:
        felt_obj(f, col)
        xs += [f["center"][0] - f["size"][0] / 2, f["center"][0] + f["size"][0] / 2]
        zs += [f["center"][2] - f["size"][1] / 2, f["center"][2] + f["size"][1] / 2]
    rail_t = get_template("rail_straight_4")
    coll_boxes = []
    for w in h["walls"]:
        o = box_obj(w["id"], (w["size"][0], w["size"][2], w["size"][1]), WALL, col)
        o.location = lglib.R(*w["center"])
        o.rotation_euler = (0, 0, math.radians(w.get("yaw", 0)))
        coll_boxes.append(o)
        if w.get("kind") is None and w["id"].startswith("rail"):
            top = w["center"][1] + w["size"][1] / 2
            L = w["size"][2]
            k = max(1, math.ceil(L / 4.0 - 0.15))
            seg = L / k
            Ry = DL.yaw_mat(w.get("yaw", 0))
            for i in range(k):
                off = Ry @ np.array([0, 0, -L / 2 + seg * (i + 0.5)])
                r = place(rail_t, "rail", dict(pos=[w["center"][0] + off[0], top - 1.0, w["center"][2] + off[2]],
                                               yaw=w.get("yaw", 0)), col)
                r.scale = (1, seg / 4.0, 1)
    for z in h["hazards"]:
        o = box_obj(z["id"], (z["size"][0], z["size"][1], 0.05), WATER if z["type"] == "water" else PIT, col)
        o.location = lglib.R(*z["center"])
        o.rotation_euler = (0, 0, math.radians(z.get("yaw", 0)))
    for name, p in man.items():
        if name not in REG:
            continue
        for pl in p["placements"]:
            if pl["hole"] != f"H{n}":
                continue
            place(get_template(name), name, pl, col, base_len_z=p["bbox_size_studs"][2])
    for it in DRESS.get(f"H{n}", {}).get("instances", []):
        place(get_template(it["prop"]), it["prop"], it, col)
    # neighbouring holes' dressing (what the player really sees), re-expressed in this hole's frame and
    # dropped onto this preview ground; their own felt/heroes are not drawn
    Rw, off = DL.hole_xf(h)
    fc = DL.to_world(h, [(min(f["center"][0] for f in h["felt"]) + max(f["center"][0] for f in h["felt"])) / 2, 0,
                         (min(f["center"][2] for f in h["felt"]) + max(f["center"][2] for f in h["felt"])) / 2])
    for h2 in holes:
        if h2["number"] == n:
            continue
        for it in DRESS.get(f"H{h2['number']}", {}).get("instances", []):
            pw = DL.to_world(h2, it["pos"])
            if np.hypot(pw[0] - fc[0], pw[2] - fc[2]) > 100:
                continue
            pl = (pw - off) @ Rw
            q = dict(it, pos=[pl[0], G.y(pl[0], pl[2]) - 0.08, pl[2]], yaw=it["yaw"] + h2.get("world_yaw", 0) - h.get("world_yaw", 0))
            place(get_template(it["prop"]), it["prop"], q, col)
    bpy.context.view_layer.update()
    cx, cz = (min(xs) + max(xs)) / 2, (min(zs) + max(zs)) / 2
    ext = max(max(xs) - min(xs), max(zs) - min(zs))

    # beauty views: hide collision boxes (every non-rail wall has a hero visual)
    for o in coll_boxes:
        o.hide_render = True
    HAZE.default_value = 0.2
    if "tee" in VIEWS:
        tee = h["tee"]["position"]
        aim = h["tee"]["aim_hint"]
        cam.data.type = "PERSP"
        cam.data.angle = math.radians(72)
        cam.data.clip_start = 0.1
        cam.location = lglib.R(tee[0] - aim[0] * 1.0, tee[1] + 5.0, tee[2] - aim[1] * 1.0)
        look = lglib.R(tee[0] + aim[0] * 20, tee[1] + 1.5, tee[2] + aim[1] * 20)
        cam.rotation_euler = (look - cam.location).to_track_quat("-Z", "Y").to_euler()
        render(os.path.join(OUT, "previews", f"assembly_h{n:02d}_tee.png"), 1280, 720)
    if "over" in VIEWS:
        tgt = lglib.R(cx, 0, cz)
        d = ext * 1.05 + 10
        az, el = math.radians(-110), math.radians(48)
        cam.data.type = "PERSP"
        cam.data.angle = math.radians(60)
        cam.location = tgt + Vector((d * math.cos(el) * math.cos(az), d * math.cos(el) * math.sin(az), d * math.sin(el)))
        cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
        render(os.path.join(OUT, "previews", f"assembly_h{n:02d}.png"), 1024, 768)
    if "top" in VIEWS:
        # top-down cutaway: camera clips everything higher than 6 studs above the highest felt; collision boxes shown
        for o in coll_boxes:
            o.hide_render = False
        HAZE.default_value = 0.0
        top_y = max(f["center"][1] for f in h["felt"]) + 6.0
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ext + 24
        cam.data.clip_start = 0.01
        cam.location = lglib.R(cx, top_y, cz)
        cam.rotation_euler = (0, 0, 0)
        render(os.path.join(OUT, "previews", f"assembly_h{n:02d}_top.png"), 1024, 1024)
    print(f"[assembly] h{n:02d}")
