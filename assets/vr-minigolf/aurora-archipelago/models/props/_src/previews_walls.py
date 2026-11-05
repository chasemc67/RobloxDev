"""Round 4 'walls' previews -> previews/walls/ (same stage / render setup as build_all.py), hole frame:
the rebuilt per-hole dressing FBX (rail skins + landmark props), the holes.json felt rectangles (top = centre y) and the mover FBX
at the motion position of its minimum wall clearance (fitcheck_walls_validated.txt).
  h11_slot_lintel_eye/_34/_side.png    H11 floe at slide offset -5.10 (inside the rail5 slot), lintel underside y 1.27, floe top 1.12;
                                       side = orthographic view along the slide axis (+x) from inside the pocket: 0.15 under the lintel
  h12_stern_wheel_eye/_34/_side.png    H12 paddle wheel at 0 deg (a paddle straight down), stern wall line z -18.01, paddles z -17.95;
                                       side = orthographic view along x from the bypass: 0.06 between the paddle and the hull13 stern face
  blender -b --factory-startup -P out_props/_src/previews_walls.py"""
import bpy, os, sys, math

SRC = os.path.dirname(os.path.abspath(__file__))
_b = open(os.path.join(SRC, "build_all.py"), encoding="utf8").read()
sys.argv = [sys.argv[0], "--", "--no-render"]
exec(compile(_b[:_b.index("def main():")], "build_all.py[head]", "exec"))
from mathutils import Vector
import holesdata as D
OUTP = os.path.join(OUT, "previews", "walls")
os.makedirs(OUTP, exist_ok=True)


def B(x, y, z):                 # Roblox -> Blender
    return Vector((x, -z, y))


def shot(cam, loc, target, path, fov=55, ortho=None, clip=0.1, clip_end=1000.0):
    cam.location = B(*loc)
    cam.rotation_euler = (B(*target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO" if ortho else "PERSP"
    cam.data.clip_start = clip
    cam.data.clip_end = clip_end
    if ortho:
        cam.data.ortho_scale = ortho
    else:
        cam.data.angle = math.radians(fov)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def felt(col, n, t=0.3):
    import bmesh
    for f in D.H[n]["felt"]:
        me = bpy.data.meshes.new("felt_" + f["id"])
        b = bmesh.new()
        bmesh.ops.create_cube(b, size=1.0)
        c, s, yaw = f["center"], f["size"], f.get("yaw", 0.0)
        for v in b.verts:
            lx, lz, ly = v.co.x * s[0], v.co.y * s[1], (v.co.z - 0.5) * t
            x, z = D.yaw_rot(lx, lz, yaw)
            v.co = B(c[0] + x, c[1] + ly, c[2] + z)
        aalib.uv_bmesh(b, "Felt")
        b.to_mesh(me)
        me.materials.append(aalib.get_mat("Felt"))
        col.objects.link(bpy.data.objects.new("felt_" + f["id"], me))


def imp(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    return next(o for o in new if o.parent is None), new


sc = reset_scene()
setup_render(sc)
sc.render.resolution_x, sc.render.resolution_y = 1280, 860
stage = make_stage(sc)
stage["ground"].location.z = -1.2
_fl = bpy.data.lights.new("fill", "SUN")
_fl.energy = 1.2
_flo = bpy.data.objects.new("fill", _fl)
_flo.rotation_euler = (math.radians(70), 0, math.radians(30))
sc.collection.objects.link(_flo)
for o in [stage.get("capsule")] + list(getattr(stage.get("capsule"), "children", [])):
    if o is not None:
        o.hide_render = True
cam = stage["cam"]
done = []

# ------------------------------------------------------------------ H11 floe slot lintel
col = bpy.data.collections.new("h11")
sc.collection.children.link(col)
felt(col, 11)
_, a = imp(os.path.join(OUT, "fbx", "aa_h11_dressing.fbx"))
m = D.mover(11, "ice_floe")
OFF = -5.10
froot, b = imp(os.path.join(OUT, "fbx", "aa_h11_ice_floe.fbx"))
froot.location = B(m["pivot"][0] + OFF * m["axis"][0], m["pivot"][1], m["pivot"][2])
bpy.context.view_layer.update()
shot(cam, (2.0, 5.0, -19.0), (-3.25, 0.9, -28.0), os.path.join(OUTP, "h11_slot_lintel_eye.png"), 60)
shot(cam, (1.2, 4.2, -23.8), (-3.6, 1.0, -28.0), os.path.join(OUTP, "h11_slot_lintel_34.png"), 50)
# along +x from inside the pocket (x -9.4, past the floe tip -8.6): the floe end-on framed by the rail5 window; far clip at x -2.9
# (just past rail5, before berg18) so the 0.15 frame around the floe reads against the sky
shot(cam, (-9.4, 0.6, -28.0), (0.0, 0.6, -28.0), os.path.join(OUTP, "h11_slot_lintel_side.png"), ortho=2.4, clip=0.05, clip_end=6.5)
for o in a + b:
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.collections.remove(col)
done.append("H11")

# ------------------------------------------------------------------ H12 icebreaker stern + wheel
col = bpy.data.collections.new("h12")
sc.collection.children.link(col)
felt(col, 12)
_, a = imp(os.path.join(OUT, "fbx", "aa_h12_dressing.fbx"))
m = D.mover(12, "paddle_wheel")
wroot, b = imp(os.path.join(OUT, "fbx", "aa_h12_paddle_wheel.fbx"))
wroot.location = B(*m["pivot"])                 # angle 0: a paddle straight down
bpy.context.view_layer.update()
shot(cam, (2.5, 5.0, -9.0), (0.0, 1.8, -18.0), os.path.join(OUTP, "h12_stern_wheel_eye.png"), 60)
shot(cam, (7.5, 6.5, -12.0), (0.0, 1.8, -18.5), os.path.join(OUTP, "h12_stern_wheel_34.png"), 50)
# along -x from the bypass (x 10, inside rail9): hull13 end face at z -18.01 vs the down paddle's back face z -17.95; far clip at
# x -1.4 (just past the paddle, before rail2/rail1) so the 0.06 gap reads against the sky
shot(cam, (10.0, 0.7, -18.0), (0.0, 0.7, -18.0), os.path.join(OUTP, "h12_stern_wheel_side.png"), ortho=2.0, clip=0.05, clip_end=11.4)
done.append("H12")
print("[walls previews]", done, sorted(os.listdir(OUTP)))
