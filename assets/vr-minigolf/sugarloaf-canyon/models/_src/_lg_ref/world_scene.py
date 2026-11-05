"""Pass 4: shared PREVIEW scene of the whole Lantern Grove world (never exported; Studio uses Terrain).
Imported by world_vista.py (vistas) and assembly_world.py (per-hole tee / top views).

Builds: terrain-4stud.json heightfield (legend colours) + water cells + far apron; every hole's felt (textured Felt:
softer felt.png + felt_normal.png nap) placed with world.json placements; plain rail walls dressed with
rail_straight_4 (other collision walls in COLL, hidden in beauty views); walkway ribbons; hero props, the 54 lantern
posts and every world piece (models/world layout.json); the pass-4 dressing at world_pos / world_yaw (fbx/<prop>.fbx,
shared mesh data) and PointLights at dressing lights_world, the H9 interior light spots and the lantern posts.
Options (set before import): world_scene.OPTS = dict(samples=24, res=1280, dressing=True, lights=True).
"""
import bpy, bmesh, sys, os, json, math, glob
import numpy as np
from mathutils import Vector, Matrix

SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC)
import lglib, world_fit as WF, dressing_lib as DL
import world_pieces as WP   # registers the world materials
import props_cards          # registers the card materials
import hole_skins           # pass 5: per-hole felt material + rail-kit variant

OPTS = dict(samples=24, res=1280, dressing=True, lights=True, spot_w=700.0)
_o = sys.modules.get("__main__")
OPTS.update(getattr(_o, "SCENE_OPTS", {}) or {})
SAMPLES, RES = OPTS["samples"], OPTS["res"]
SPOT_W = OPTS["spot_w"]      # preview watts per unit of Roblox PointLight Brightness (range 16)
MODELS = WF.MODELS
OUTD = os.path.join(MODELS, "world")
W = WF.load_world()
LAY = json.load(open(os.path.join(OUTD, "layout.json")))
MAN = json.load(open(os.path.join(MODELS, "manifest.json")))


def BL(p):
    return Vector((p[0], -p[2], p[1]))


def place_matrix(pos, yaw, scale=None):
    s = scale or [1, 1, 1]
    return (Matrix.Translation(BL(pos)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @
            Matrix.Diagonal((s[0], s[2], s[1], 1.0)))


# ----------------------------------------------------------------------------- scene / look
bpy.ops.wm.read_factory_settings(use_empty=True)
lglib._scratch = None
sc = bpy.context.scene
sc.unit_settings.system = "NONE"
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 3
sc.cycles.transparent_max_bounces = 4
sc.render.resolution_x = RES
sc.render.resolution_y = RES * 9 // 16
sc.view_settings.view_transform = "Standard"
sc.view_settings.exposure = 0.35
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
els[0].position, els[0].color = 0.0, (0.55, 0.36, 0.22, 1)
els[1].position, els[1].color = 0.85, (0.26, 0.40, 0.78, 1)
e = els.new(0.5)
e.color = (1.0, 0.70, 0.40, 1)
e = els.new(0.6)
e.color = (0.86, 0.72, 0.66, 1)
nt.links.new(cr.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.0
world.mist_settings.start = 60
world.mist_settings.depth = 1400
world.mist_settings.falloff = "QUADRATIC"

az, el = math.radians(242), math.radians(14)
to_sun = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 4.4
sun.data.color = (1.0, 0.72, 0.45)
sun.data.angle = math.radians(2)
sun.rotation_euler = (-to_sun).to_track_quat("-Z", "Y").to_euler()
sc.collection.objects.link(sun)
fill = bpy.data.objects.new("fill", bpy.data.lights.new("fill", "SUN"))
fill.data.energy = 0.7
fill.data.color = (0.6, 0.7, 1.0)
fill.data.use_shadow = False
fill.rotation_euler = Vector((-0.3, -0.4, -0.85)).normalized().to_track_quat("-Z", "Y").to_euler()
sc.collection.objects.link(fill)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.lens_unit = "FOV"
cam.data.sensor_fit = "HORIZONTAL"
cam.data.clip_start = 0.3
cam.data.clip_end = 6000
sc.collection.objects.link(cam)
sc.camera = cam

sc.view_layers[0].use_pass_mist = True
sc.use_nodes = True
ct = sc.node_tree
for n in list(ct.nodes):
    ct.nodes.remove(n)
rl = ct.nodes.new("CompositorNodeRLayers")
mul = ct.nodes.new("CompositorNodeMath")
mul.operation = "MULTIPLY"
mul.inputs[1].default_value = 0.42
mix = ct.nodes.new("CompositorNodeMixRGB")
mix.inputs[2].default_value = (0.98, 0.76, 0.56, 1)
glare = ct.nodes.new("CompositorNodeGlare")
glare.glare_type = "FOG_GLOW"
glare.quality = "MEDIUM"
try:
    glare.threshold = 1.3
    glare.size = 7
except Exception:
    pass
comp = ct.nodes.new("CompositorNodeComposite")
ct.links.new(rl.outputs["Mist"], mul.inputs[0])
ct.links.new(mul.outputs[0], mix.inputs[0])
ct.links.new(rl.outputs["Image"], mix.inputs[1])
ct.links.new(mix.outputs[0], glare.inputs[0])
ct.links.new(glare.outputs[0], comp.inputs[0])


def flat_mat(name, rgb, rough=0.95, noise_amt=0.25, scale=0.05, tex=None, tile=8.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    t = m.node_tree
    b = t.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    lin = [lglib.srgb_to_lin(c / 255.0) for c in rgb]
    if tex:
        img = t.nodes.new("ShaderNodeTexImage")
        img.image = bpy.data.images.load(os.path.join(MODELS, "textures", tex + ".png"), check_existing=True)
        co = t.nodes.new("ShaderNodeTexCoord")
        mp = t.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1 / tile, 1 / tile, 1 / tile)
        t.links.new(co.outputs["Object"], mp.inputs["Vector"])
        t.links.new(mp.outputs["Vector"], img.inputs["Vector"])
        mx = t.nodes.new("ShaderNodeMixRGB")
        mx.blend_type = "MULTIPLY"
        mx.inputs[0].default_value = 1.0
        mx.inputs[1].default_value = (*[min(1, c * 2.2) for c in lin], 1)
        t.links.new(img.outputs["Color"], mx.inputs[2])
        t.links.new(mx.outputs[0], b.inputs["Base Color"])
        return m
    nz = t.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    ramp = t.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*[c * (1 - noise_amt) for c in lin], 1)
    ramp.color_ramp.elements[1].color = (*[min(1, c * (1 + noise_amt)) for c in lin], 1)
    t.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    t.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return m


# ----------------------------------------------------------------------------- terrain (preview only)
T = WF.Terrain()
legend = {d["key"]: d for d in W["materials"]["legend"]}
key_of = {"Grass": "grass", "LeafyGrass": "leafy", "Rock": "rock", "Ground": "path", "Water": "water", "Sand": "sand"}
tmats = []
for i, nm in enumerate(T.mats):
    k = key_of.get(nm, "grass")
    rgb = {"grass": (122, 140, 62), "leafy": (140, 128, 66), "rock": (112, 112, 118), "path": (150, 120, 80),
           "water": (70, 74, 60), "sand": (190, 168, 122)}[k]
    tex = {"rock": "slate_stone", "leafy": "leaf_litter"}.get(k)
    tmats.append(flat_mat(f"terr_{k}", rgb, tex=tex, tile=16.0 if k == "rock" else 10.0))
me = bpy.data.meshes.new("terrain")
xs = T.x0 + (np.arange(T.cols) + 0.5) * T.cell
zs = T.z0 + (np.arange(T.rows) + 0.5) * T.cell
V = [(x, -z, T.H[j, i]) for j, z in enumerate(zs) for i, x in enumerate(xs)]
F = []
mi = []
C = T.cols
for j in range(T.rows - 1):
    for i in range(T.cols - 1):
        a = j * C + i
        F.append((a, a + C, a + C + 1, a + 1))
        mi.append(int(T.M[j, i]))
me.from_pydata(V, [], F)
for m in tmats:
    me.materials.append(m)
me.polygons.foreach_set("material_index", mi)
me.polygons.foreach_set("use_smooth", [True] * len(F))
terr = bpy.data.objects.new("terrain", me)
sc.collection.objects.link(terr)
# water cells
wv, wf = [], []
for j in range(T.rows):
    for i in range(T.cols):
        y = T.W[j, i]
        if np.isnan(y):
            continue
        x0, z0 = T.x0 + i * T.cell, T.z0 + j * T.cell
        n = len(wv)
        wv += [(x0, -z0, y), (x0 + 4, -z0, y), (x0 + 4, -z0 - 4, y), (x0, -z0 - 4, y)]
        wf.append((n, n + 3, n + 2, n + 1))
wme = bpy.data.meshes.new("water")
wme.from_pydata(wv, [], wf)
wm = bpy.data.materials.new("water_v")
wm.use_nodes = True
b = wm.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.16, 0.45, 0.62, 1)
b.inputs["Roughness"].default_value = 0.06
b.inputs["Metallic"].default_value = 0.0
wme.materials.append(wm)
sc.collection.objects.link(bpy.data.objects.new("water", wme))
# far apron (between the terrain edge and the far hills)
ap = bpy.data.meshes.new("apron")
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=3500)
bmesh.ops.translate(bm, vec=(40, 0, 6.0), verts=bm.verts)
bm.to_mesh(ap)
ap.materials.append(flat_mat("apron", (96, 92, 52)))
sc.collection.objects.link(bpy.data.objects.new("apron", ap))

# ----------------------------------------------------------------------------- holes: felt + walls
H = WF.holes_world(W)
pb = lglib.PB("_holes")
lglib.MATS["CollWall"] = ("#D0301A", "SmoothPlastic", 0, 0.5, "preview-only collision wall")
pbc = lglib.PB("_coll")
RAILS = []
for h in H:
    for f in h["felt"]:
        c = DL.to_world(h, f["center"])
        yaw = f.get("yaw", 0) + h["world_yaw"]
        sl = (f.get("slope") or {})
        rot = (0, 0, yaw)
        if sl.get("rise"):
            ang = math.degrees(math.atan2(sl["rise"], f["size"][1 if sl.get("axis", "z") == "z" else 0]))
            # rise = height(+axis end) - height(-axis end); Roblox +Z = Blender -Y, so a z-slope tilts by -ang about
            # Blender X (pass 5 fix: pass 4 tilted every z-slope the wrong way in the previews)
            rot = (-ang, 0, yaw) if sl.get("axis", "z") == "z" else (0, -ang, yaw)
        skin = hole_skins.SKINS[f"H{h['number']}"]
        pb.box(skin["felt_material"], (f["size"][0], f["size"][1], 0.6), loc=BL(c) - Vector((0, 0, 0.3)), rot=rot)
    for w_ in h["walls"]:
        c = DL.to_world(h, w_["center"])
        if w_.get("kind") is None and w_["id"].startswith("rail"):
            top = w_["center"][1] + w_["size"][1] / 2
            L = w_["size"][2]
            k = max(1, math.ceil(L / 4.0 - 0.15))
            Ry = DL.yaw_mat(w_.get("yaw", 0))
            for i in range(k):
                off = Ry @ np.array([0, 0, -L / 2 + L / k * (i + 0.5)])
                pw = DL.to_world(h, [w_["center"][0] + off[0], top - 1.0, w_["center"][2] + off[2]])
                RAILS.append((pw, w_.get("yaw", 0) + h["world_yaw"], L / k / 4.0,
                              hole_skins.SKINS[f"H{h['number']}"]["rail_straight_4"]))
        pbc.box("CollWall", (w_["size"][0], w_["size"][2], w_["size"][1]), loc=BL(c), rot=(0, 0, w_.get("yaw", 0) + h["world_yaw"]))
    for z in h["hazards"]:
        c = DL.to_world(h, z["center"])
        pb.box("Water", (z["size"][0], z["size"][1], 0.2), loc=BL(c), rot=(0, 0, z.get("yaw", 0) + h["world_yaw"]))
for p in W["paths"]:
    for s in p["segments"]:
        if s["type"] == "on_hole":
            continue
        a, b_ = BL(s["start"]), BL(s["end"])
        d = b_ - a
        if d.length < 0.2:
            continue
        mid = (a + b_) / 2
        ang = math.degrees(math.atan2(d.y, d.x))
        tilt = math.degrees(math.atan2(d.z, Vector((d.x, d.y, 0)).length))
        pb.box("Oak", (Vector((d.x, d.y, 0)).length + 0.4, p["width"], 0.5), loc=mid + Vector((0, 0, -0.1)), rot=(0, -tilt, ang))
col = bpy.data.collections.new("world")
sc.collection.children.link(col)
pb.finalize(col)
_cr, COLL = pbc.finalize(col)
for o in COLL:
    o.hide_render = True


# ----------------------------------------------------------------------------- FBX instancing
_cache = {}


def load_fbx(path):
    if path in _cache:
        return _cache[path]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y")
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    meshes = []
    for o in new:
        if o.type == "MESH":
            for i, m in enumerate(o.data.materials):
                base = m.name.split(".")[0] if m else None
                if base in lglib.MATS:
                    o.data.materials[i] = lglib.get_mat(base)
            meshes.append((o.data, o.matrix_world.copy()))
    for o in new:
        bpy.data.objects.remove(o)
    _cache[path] = meshes
    return meshes


def instance(path, M_, name):
    for me_, mw in load_fbx(path):
        o = bpy.data.objects.new(name, me_)
        o.matrix_world = M_ @ mw
        col.objects.link(o)


hm = {f"H{h['number']}": h for h in H}
n_props = 0
for p in MAN["props"]:
    if p.get("group") == "dressing" or p["name"] == "hollow_tree":
        continue
    fp = os.path.join(MODELS, p["fbx"])
    for pl in p.get("placements", []):
        h = hm.get(pl["hole"])
        if not h:
            continue
        s = pl.get("scale", 1.0)
        S = [s] * 3 if np.isscalar(s) else s
        if pl.get("scale_z_to"):
            S = [1, 1, pl["scale_z_to"] / max(p["bbox_size_studs"][2], 1e-6)]
        pos = DL.to_world(h, pl["pos"])
        instance(fp, place_matrix(pos, pl.get("yaw", 0) + h["world_yaw"], S), p["name"])
        n_props += 1
for q in W["lanterns"]["points"]:
    instance(os.path.join(MODELS, "fbx", "lantern_post.fbx"), place_matrix(q["pos"], 0), "post")
n_world = 0
for pid, insts in LAY.items():
    files = sorted(glob.glob(os.path.join(OUTD, "fbx", f"{pid}.fbx")) + glob.glob(os.path.join(OUTD, "fbx", f"{pid}_part*.fbx")))
    for f in files:
        for ins in insts:
            instance(f, place_matrix(ins["pos"], ins.get("yaw", 0), ins.get("scale")), pid)
            n_world += 1
for pw, yaw, sz, rk in RAILS:
    instance(os.path.join(MODELS, "fbx", f"{rk}.fbx"), place_matrix(pw, yaw, [1, 1, sz]), "rail")
n_dress = 0
DRESS = MAN.get("dressing", {}).get("holes", {})
if OPTS["dressing"]:
    for H_, d in DRESS.items():
        for it in d["instances"]:
            s_ = it["scale"]
            instance(os.path.join(MODELS, "fbx", f"{it['prop']}.fbx"), place_matrix(it["world_pos"], it["world_yaw"], [s_] * 3),
                     it["prop"])
            n_dress += 1
LIGHTS = []


def point_light(p, energy, rgb, radius=0.25):
    L = bpy.data.lights.new("pl", "POINT")
    L.energy = energy
    L.color = rgb
    L.shadow_soft_size = radius
    o = bpy.data.objects.new("pl", L)
    o.location = BL(p)
    col.objects.link(o)
    LIGHTS.append(o)


if OPTS["lights"]:
    amber = (1.0, 0.62, 0.25)
    for H_, d in DRESS.items():
        for p in d.get("lights_world", []):
            point_light(p, 6.0, amber)
    il = MAN.get("world", {}).get("h9_interior_lights", {}).get("lights", [])
    for q in il:
        if q["kind"] == "wall_lantern_cluster":
            point_light(q["pos"], 220.0, amber, 0.6)
        else:
            point_light(q["pos"], 60.0, (0.45, 0.95, 0.85), 0.4)
    for q in W["lanterns"]["points"]:
        point_light(np.array(q["pos"]) + [0.6, 2.9, 0], 20.0, amber)
    # pass 5: spot_lights pooling over the H8/H9 moving parts and cups (Roblox Brightness -> preview watts)
    for H_, d in DRESS.items():
        for q in d.get("spot_lights", []):
            rgb = tuple(lglib.srgb_to_lin(c) for c in lglib.hex_rgb(q["color"]))
            point_light(q["world_pos"], SPOT_W * q["brightness"] * (q["range"] / 16.0) ** 2, rgb, 0.8)
    # pass 8: manifest.lights[] (H9 hanging lanterns, H7/H8 rail lanterns, H8 glow lights), same Brightness mapping
    for q in MAN.get("lights", []):
        rgb = tuple(lglib.srgb_to_lin(c) for c in lglib.hex_rgb(q["color"]))
        point_light(q["world_pos"], SPOT_W * q["brightness"] * (q["range"] / 16.0) ** 2, rgb, 0.3)
print(f"[scene] hero props {n_props}, world instances {n_world}, dressing {n_dress}, rails {len(RAILS)}, lights {len(LIGHTS)}")
