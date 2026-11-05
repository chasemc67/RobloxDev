"""v210b previews -> previews/v210b/ (Cycles CPU). In-hole context scenes in the holes.json hole-local frame, built
from the shipped FBX (backing, cladding, lip, dressing) + generator rail kit (placed in Studio, so modelled here with the
RAIL_NOTE rule: one piece per 4 studs on the felt it borders). Each scene: eye (5 studs, player side) + 3/4 view, after
and before.
  h9_bank_corner   H9 bank1: stone backing + mint lip + oak rails (rail4/rail5) + limestone posts | before: OakDeep cap,
                   trim rails, no lip
  h3_bank1_corner  H3 bank1: stone backing (cap now stone) with the base rail kit crossing | before: OakDeep cap
  h8_alcove        H8 alcove bank: stone cladding | before: root-bark cladding + moss streaks
  h3_pole_footing  dressing_h03_a lantern-span pole footing (-10, -4.5): eye + 3/4 + underside (the deleted oak duplicate)
blender -b --factory-startup -P previews_v210b.py -- <before fbx dir>
"""
import bpy, sys, os, math, json, importlib
import numpy as np
from mathutils import Vector, Matrix

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
BEFORE = sys.argv[sys.argv.index("--") + 1:][0]
import lglib, registry
for m in ("props_dressing", "props_moving", "props_hero", "props_p2p3", "props_variants", "props_cards", "props_pass6",
          "props_pass7", "props_pass8", "props_pass10", "props_v210b"):
    importlib.import_module(m)
import bankfit_v210b as BF
import dressing_lib as DL

PV = os.path.join(OUT, "previews", "v210b")
os.makedirs(PV, exist_ok=True)
HOLES = {h["number"]: h for h in DL.load_holes()}
MAN = {p["name"]: p for p in json.load(open(os.path.join(OUT, "manifest.json")))["props"]}
REG = {p["name"]: p for p in registry.PROPS}
FBX = os.path.join(OUT, "fbx")


def rb(x, y, z):
    return Vector((x, -z, y))


def reset():
    _tpl.clear()                    # templates die with the old scene data
    lglib._scratch = None           # and so does lglib's scratch mesh
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "NONE"
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.render.resolution_x, sc.render.resolution_y = 960, 640
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.62, 0.70, 0.85, 1)
    bg.inputs["Strength"].default_value = 0.9
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 2.8
    sun.data.angle = math.radians(8)
    sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens_unit = "FOV"
    cam.data.angle = math.radians(60)
    cam.data.clip_start = 0.02
    sc.collection.objects.link(cam)
    sc.camera = cam
    return sc, cam


def flat_mat(name, hexv, rough=0.85):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*[lglib.srgb_to_lin(c) for c in lglib.hex_rgb(hexv)], 1)
    b.inputs["Roughness"].default_value = rough
    return m


def box(name, T, mat):
    """T = (n,3,3) Roblox-frame triangles -> mesh object."""
    me = bpy.data.meshes.new(name)
    V = [rb(*p) for t in T for p in t]
    me.from_pydata(V, [], [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(T))])
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def felt(h, felt_hex):
    m = flat_mat("felt_prev", felt_hex, 0.95)
    for f in h["felt"]:
        c = np.array(f["center"], float)
        hx, hz = f["size"][0] / 2, f["size"][1] / 2
        R = BF.yaw_mat(f.get("yaw", 0))
        s = f.get("slope")

        def y(lx, lz):
            if not s:
                return c[1]
            t = lx / (2 * hx) if s["axis"] == "x" else lz / (2 * hz)
            return c[1] + s["rise"] * t
        cs = [(-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz)]
        top = [c + R @ np.array([lx, y(lx, lz) - c[1], lz]) for lx, lz in cs]
        bot = [p - [0, 0.3, 0] for p in top]
        q = lambda a, b, c_, d: [[a, b, c_], [a, c_, d]]
        T = q(*top[::-1]) + q(*bot) + sum((q(top[i], top[(i + 1) % 4], bot[(i + 1) % 4], bot[i]) for i in range(4)), [])
        box(f"felt_{f['id']}", np.array(T), m)


def ground(y=-0.35):
    box("ground", np.array([[[-200, y, -200], [200, y, -200], [200, y, 200]], [[-200, y, -200], [200, y, 200], [-200, y, 200]]]),
        flat_mat("ground", "#4A3F33", 0.95))


def place_root(root, pos, yaw, sz=1.0):
    S = Matrix.Diagonal((1, sz, 1, 1))                   # Roblox local Z = Blender local -Y
    root.matrix_world = Matrix.Translation(rb(*pos)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ S @ root.matrix_world


def import_fbx(path, pos, yaw, sz=1.0):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y")
    new = [o for o in bpy.data.objects if o not in before]
    for r in [o for o in new if o.parent is None]:
        place_root(r, pos, yaw, sz)
    bpy.context.view_layer.update()
    return new


_tpl = {}


def gen(name, pos, yaw, sz=1.0):
    """Generator-built prop (rail kit) placed in the hole frame (the template is copied per placement)."""
    if name not in _tpl:
        col = bpy.data.collections.new("_tpl_" + name)
        pb = lglib.PB(name)
        REG[name]["fn"](pb)
        root, objs = pb.finalize(col)
        lglib.box_uv_objects(objs)
        _tpl[name] = (root, objs)
    root, objs = _tpl[name]
    r = root.copy()
    bpy.context.scene.collection.objects.link(r)
    for o in objs:
        c = o.copy()
        c.parent = r
        bpy.context.scene.collection.objects.link(c)
    r.matrix_world = Matrix.Translation(rb(*pos)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ \
        Matrix.Diagonal((1, sz, 1, 1))
    return r


def rails(h, kit, near_c, radius=11.0):
    """RAIL_NOTE rule: 4-stud pieces along each rail wall near near_c, base = felt height under the piece; end posts."""
    for w in h["walls"]:
        if w.get("kind") is not None or not w["id"].startswith("rail"):
            continue
        c = np.array(w["center"], float)
        L = w["size"][2]
        R = BF.yaw_mat(w.get("yaw", 0))
        n = max(1, math.ceil(L / 4.0 - 0.15))
        seg = L / n
        for i in range(n):
            p = c + R @ np.array([0, 0, -L / 2 + seg * (i + 0.5)])
            if math.hypot(p[0] - near_c[0], p[2] - near_c[2]) > radius:
                continue
            yb = BF.felt_height_at(h, p[0], p[2], pad=0.6) or 0.0
            gen(kit["rail_straight_4"], [p[0], yb, p[2]], w.get("yaw", 0), seg / 4.0)
        for s in (-1, 1):
            e = c + R @ np.array([0, 0, s * L / 2])
            if math.hypot(e[0] - near_c[0], e[2] - near_c[2]) <= radius:
                gen(kit["rail_end_post"], [e[0], BF.felt_height_at(h, e[0], e[2], pad=0.6) or 0.0, e[2]], w.get("yaw", 0))


def shoot(cam, eye, tgt, path, lens=60):
    cam.data.angle = math.radians(lens)
    cam.location = rb(*eye)
    cam.rotation_euler = (rb(*tgt) - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("[preview]", os.path.basename(path))


def kitd(hole_skin):
    return dict(rail_straight_4=hole_skin["rail_straight_4"], rail_end_post=hole_skin["rail_end_post"])


import hole_skins
TRIM = kitd(hole_skins.TRIM)
H9K = kitd(hole_skins.SKINS["H9"])
BASEK = kitd(hole_skins.SKINS["H3"])


def backing_scene(H, wid, state, kit, lip, felt_hex, eye, tgt, eye34, tgt34, tag):
    sc, cam = reset()
    h = HOLES[H]
    ground(min(f["center"][1] for f in h["felt"]) - 0.35)
    felt(h, felt_hex)
    pl = [p for p in MAN["bank_backing_stone"]["placements"] if p["hole"] == f"H{H}" and p["note"] == wid][0]
    src = FBX if state == "after" else BEFORE
    import_fbx(os.path.join(src, "bank_backing_stone.fbx"), pl["pos"], pl["yaw"])
    if lip:
        lp = MAN["h9_bank_lip"]["placements"][0]
        import_fbx(os.path.join(FBX, "h9_bank_lip.fbx"), lp["pos"], lp["yaw"])
    rails(h, kit, pl["pos"])
    sfx = "v210b" if state == "after" else "before"
    shoot(cam, eye, tgt, os.path.join(PV, f"{tag}_{sfx}_eye.png"))
    shoot(cam, eye34, tgt34, os.path.join(PV, f"{tag}_{sfx}_34.png"), 50)


# H9 bank1 corner: the player comes up the ramp (+z side) and looks north-west at the bank
for st in ("after", "before"):
    backing_scene(9, "bank1_backing", st, H9K if st == "after" else TRIM, st == "after", "#66B547",
                  eye=(2.2, 6.0, -19.5), tgt=(-1.4, 2.0, -26.8), eye34=(6.5, 9.5, -18.0), tgt34=(-1.0, 1.8, -26.5),
                  tag="h9_bank_corner")
# H9 lip close-up (after only): low eye over the bank, along the top edge
sc, cam = reset()
h = HOLES[9]
ground(-0.35)
felt(h, "#66B547")
pl = [p for p in MAN["bank_backing_stone"]["placements"] if p["hole"] == "H9"][0]
import_fbx(os.path.join(FBX, "bank_backing_stone.fbx"), pl["pos"], pl["yaw"])
lp = MAN["h9_bank_lip"]["placements"][0]
import_fbx(os.path.join(FBX, "h9_bank_lip.fbx"), lp["pos"], lp["yaw"])
rails(h, H9K, pl["pos"])
shoot(cam, (0.9, 3.4, -24.4), (-1.3, 2.25, -26.6), os.path.join(PV, "h9_bank_lip_v210b_closeup.png"), 40)
# H3 bank1 corner (base rail kit, oak caps cross the backing)
for st in ("after", "before"):
    backing_scene(3, "bank1_backing", st, BASEK, False, "#478C35",
                  eye=(1.8, 5.0, -5.0), tgt=(-1.3, 1.2, -13.3), eye34=(6.0, 8.5, -6.5), tgt34=(-1.2, 1.0, -13.0),
                  tag="h3_bank1_corner")
# H8 alcove bank cladding
for st in ("after", "before"):
    sc, cam = reset()
    h = HOLES[8]
    ground(-0.35)
    felt(h, "#66B547")
    pl = MAN["h8_alcove_bank_cladding"]["placements"][0]
    import_fbx(os.path.join(FBX if st == "after" else BEFORE, "h8_alcove_bank_cladding.fbx"), pl["pos"], pl["yaw"])
    rails(h, TRIM, pl["pos"], 7.0)
    sfx = "v210b" if st == "after" else "before"
    shoot(cam, (4.0, 5.0, -11.5), (8.4, 0.3, -11.5), os.path.join(PV, f"h8_alcove_{sfx}_eye.png"))
    shoot(cam, (3.0, 7.0, -4.5), (8.3, 0.2, -11.5), os.path.join(PV, f"h8_alcove_{sfx}_34.png"), 50)
# dressing_h03_a pole footing (lantern_span_20 west pole at (-10, -0.45, -4.5)); underside shows the removed oak face
for st in ("after", "before"):
    sc, cam = reset()
    import_fbx(os.path.join(FBX if st == "after" else BEFORE, "dressing_h03_a.fbx"), (0, 0, 0), 0)
    sfx = "v210b" if st == "after" else "before"
    if st == "after":
        shoot(cam, (-7.0, 4.5, -0.5), (-10.0, 0.6, -4.5), os.path.join(PV, "h3_pole_footing_v210b_eye.png"))
        shoot(cam, (-8.2, 1.8, -2.6), (-10.0, -0.2, -4.5), os.path.join(PV, "h3_pole_footing_v210b_34.png"), 40)
    # underside: camera below the footing looking up, other geometry clipped by the near-field footing only
    shoot(cam, (-10.0, -2.2, -4.5 + 0.001), (-10.0, -0.45, -4.5), os.path.join(PV, f"h3_pole_footing_{sfx}_underside.png"), 30)
print("[done] previews_v210b")
