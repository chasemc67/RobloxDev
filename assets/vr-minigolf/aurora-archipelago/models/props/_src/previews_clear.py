"""Round 3 'clear' previews -> previews/clear/ (same stage / render setup as build_all.py):
  <mover>_eye.png        player eye (5 studs) from the tee side, felt plane at y 0, mover at its holes.json pivot
  <mover>_34.png         3/4 elevated
  <mover>_side.png       orthographic side view along the motion axis at the lowest point (angle 0: a paddle / the skid
                         centre straight down = min felt gap)
  <mover>_side_gap.png   1-stud-wide close-up of that gap; <mover>_side_gap_collider.png the same with the collision FBX
                         boxes (magenta) instead of the visual mesh
  blender -b --factory-startup -P out_props/_src/previews_clear.py"""
import bpy, os, sys, math, json

SRC = os.path.dirname(os.path.abspath(__file__))
_b = open(os.path.join(SRC, "build_all.py"), encoding="utf8").read()
sys.argv = [sys.argv[0], "--", "--no-render"]
exec(compile(_b[:_b.index("def main():")], "build_all.py[head]", "exec"))
from mathutils import Vector
import holesdata as D
OUTP = os.path.join(OUT, "previews", "clear")
os.makedirs(OUTP, exist_ok=True)
MOV = (("aa_h12_paddle_wheel", 12, "paddle_wheel"), ("aa_h14_icicle_bell", 14, "icicle_bell"))


def look(cam, target):
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def shot(cam, loc, target, path, fov=55, ortho=None):
    cam.location = Vector(loc)
    look(cam, target)
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = ortho
    else:
        cam.data.angle = math.radians(fov)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def felt_plane(col, size, t=0.3):
    """felt slab, top at y 0 (so its side face shows the felt line in the orthographic side views)"""
    import bmesh
    me = bpy.data.meshes.new("felt")
    b = bmesh.new()
    bmesh.ops.create_cube(b, size=1.0)
    for v in b.verts:
        v.co = Vector((v.co.x * size, v.co.y * size, (v.co.z - 0.5) * t))
    aalib.uv_bmesh(b, "Felt")
    b.to_mesh(me)
    me.materials.append(aalib.get_mat("Felt"))
    o = bpy.data.objects.new("felt", me)
    col.objects.link(o)
    return o


sc = reset_scene()
setup_render(sc)
sc.render.resolution_x, sc.render.resolution_y = 1024, 768
stage = make_stage(sc)
stage["ground"].location.z = -0.4
_fl = bpy.data.lights.new("fill", "SUN")
_fl.energy = 1.2
_flo = bpy.data.objects.new("fill", _fl)
_flo.rotation_euler = (math.radians(80), 0, 0)          # from the -Y (camera) side
sc.collection.objects.link(_flo)
for o in [stage.get("capsule")] + list(getattr(stage.get("capsule"), "children", [])):
    if o is not None:
        o.hide_render = True
cam = stage["cam"]
REG = {p["name"]: p for p in registry.PROPS}
done = []
for name, n, mid in MOV:
    m = D.mover(n, mid)
    col = bpy.data.collections.new(name)
    sc.collection.children.link(col)
    pb = aalib.PB(name)
    REG[name]["fn"](pb)
    root, objs = pb.finalize(col, REG[name].get("smooth_angle", 40))
    py = m["pivot"][1]
    root.location = (0, 0, py)
    # collision boxes (hidden except for the collider close-up)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(OUT, "fbx", f"{name}_collision.fbx"))
    cobs = [o for o in bpy.data.objects if o not in before]
    croot = next(o for o in cobs if o.parent is None)
    croot.location = (0, 0, py)
    cm = bpy.data.materials.new("ColliderPreview")
    cm.use_nodes = True
    bs = next(nd for nd in cm.node_tree.nodes if nd.type == "BSDF_PRINCIPLED")
    bs.inputs["Base Color"].default_value = (0.9, 0.0, 0.9, 1)
    bs.inputs["Emission Color"].default_value = (0.9, 0.0, 0.9, 1)
    bs.inputs["Emission Strength"].default_value = 0.6
    for o in cobs:
        if o.type == "MESH":
            o.data.materials[0] = cm
        o.hide_render = True
    fp = felt_plane(col, 16)
    bpy.context.view_layer.update()
    h = 8.2 if n == 12 else 10.6
    c = Vector((0, 0, py - h / 2 if n == 14 else py))
    shot(cam, (2.5, -14.0, 5.0), (0, 0, min(py, 4.5)), os.path.join(OUTP, f"{name}_eye.png"), 60)
    shot(cam, (9.5, -11.0, py + 5.5), c, os.path.join(OUTP, f"{name}_34.png"), 50)
    # side views along the motion axis (Roblox +Z = Blender -Y): camera on the -Y side looking +Y, angle 0 = lowest point
    shot(cam, (0, -30.0, h / 2 if n == 14 else py), (0, 0, h / 2 if n == 14 else py), os.path.join(OUTP, f"{name}_side.png"),
         ortho=(11.5 if n == 12 else 15.0))
    shot(cam, (0, -30.0, 0.12), (0, 0, 0.12), os.path.join(OUTP, f"{name}_side_gap.png"), ortho=1.0)
    for o in objs:
        o.hide_render = True
    for o in cobs:
        o.hide_render = False
    shot(cam, (0, -30.0, 0.12), (0, 0, 0.12), os.path.join(OUTP, f"{name}_side_gap_collider.png"), ortho=1.0)
    bpy.data.collections.remove(col)
    for o in cobs:
        bpy.data.objects.remove(o, do_unlink=True)
    done.append(name)
print("[clear previews]", done, sorted(os.listdir(OUTP)))
