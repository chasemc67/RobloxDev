"""v210 previews (same stage / look as build_all.py): previews/v210/
  h8_door_pocket_v210_{eye,34}.png      pocket + root door fully open (offset 4 = the min-clearance position), H8 frame
  h8_door_pocket_v210_plan.png          plan section (clipped at y 1.12) at the min-clearance offset 4.0
  h9_timber_v210_{eye,34}.png           timber_deflector_board + bank_backing_stone side by side
Run: LG_HOLES_JSON=<holes.json> blender -b --factory-startup -P models/_src/previews_v210.py"""
import bpy, os, sys, math
from mathutils import Vector

SRC = os.path.dirname(os.path.abspath(__file__))
_b = open(os.path.join(SRC, "build_all.py")).read()
sys.argv = [sys.argv[0], "--", "--no-render"]
exec(compile(_b[:_b.index("def main():")], "build_all.py[head]", "exec"))
REG = {p["name"]: p for p in registry.PROPS}
OUTP = os.path.join(OUT, "previews", "v210")
os.makedirs(OUTP, exist_ok=True)


def build(name, col):
    p = REG[name]
    pb = lglib.PB(name)
    post = p["fn"](pb)
    root, objs = pb.finalize(col, p.get("smooth_angle", 40))
    if callable(post):
        post(root, objs)
        lglib.box_uv_objects(objs)
    return root, objs


def felt(col, x0, x1, y0, y1, z=0.004, mat="FeltBright"):
    import bmesh
    me = bpy.data.meshes.new("felt")
    b = bmesh.new()
    x0, x1, y0, y1 = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    vs = [b.verts.new(v) for v in ((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z))]   # CCW from above: normal +Z
    b.faces.new(vs)
    lglib.box_uv_bmesh(b, 8.0)
    b.to_mesh(me)
    me.materials.append(lglib.get_mat(mat))
    o = bpy.data.objects.new("felt", me)
    col.objects.link(o)
    return o


def shot(cam, loc, target, path, lens_deg=50, ortho=None):
    cam.location = loc
    look_at(cam, target)
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho
    else:
        cam.data.type = "PERSP"
        cam.data.angle = math.radians(lens_deg)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


sc = reset_scene()
setup_render(sc)
sc.render.resolution_x, sc.render.resolution_y = 1024, 768
sc.cycles.samples = 32
stage = make_stage(sc)
for o in [stage["capsule"]] + list(stage["capsule"].children):
    o.hide_render = True
cam = stage["cam"]
B = lambda x, y, z: Vector((x, -z, y))                       # hole-local Roblox -> Blender

# ---------------------------------------------------------------- H8 pocket + door (H8 hole-local frame)
col = bpy.data.collections.new("h8")
sc.collection.children.link(col)
pk, pko = build("h8_door_pocket", col)
pl = REG["h8_door_pocket"]["placements"][0]
pk.location = B(*pl["pos"])
pk.rotation_euler = (0, 0, math.radians(pl["yaw"]))
dr, dro = build("h8_root_door", col)
dpl = REG["h8_root_door"]["placements"][0]
OPEN = 4.0
dr.location = B(dpl["pos"][0], dpl["pos"][1], dpl["pos"][2] + OPEN)
felt(col, -3.5, 3.5, 2.0, -8.0)                               # lane (x -3.5..3.5, z -8..2) - Blender y = -z
felt(col, -20.0, 9.0, 15.0, 8.0)                              # junction (z -15..-8)
bpy.context.view_layer.update()
c = B(4.75, 0.9, -7.0)
shot(cam, B(1.2, 5.0, -15.5), B(4.75, 0.8, -7.2), os.path.join(OUTP, "h8_door_pocket_v210_eye.png"), 55)
shot(cam, c + Vector((5.2, 4.4, 3.6)), c, os.path.join(OUTP, "h8_door_pocket_v210_34.png"), 50)
# plan view at the min-clearance offset: orthographic from above, clipped at y 1.12 (above the door top 1.03, below
# the raised roof 1.37), so the pocket walls / back plate show as cut sections around the door end.
top = 12.0
cam.data.clip_start = top - 1.12
shot(cam, B(4.75, top, -6.6), B(4.75, 0.0, -6.6) + Vector((0, 0.0001, 0)),
     os.path.join(OUTP, "h8_door_pocket_v210_plan.png"), ortho=3.4)
cam.data.clip_start = 0.05
bpy.data.collections.remove(col)

# ---------------------------------------------------------------- H9 timber: deflector board + bank backing stone
col = bpy.data.collections.new("h9")
sc.collection.children.link(col)
tb, tbo = build("timber_deflector_board", col)
bk, bko = build("bank_backing_stone", col)
tb.location = (-1.0, 0, 0)
bk.location = (1.0, 0, 0)
felt(col, -6, 6, -8, 8)
bpy.context.view_layer.update()
shot(cam, Vector((-9.0, -7.5, 5.0)), Vector((0, 0.5, 1.0)), os.path.join(OUTP, "h9_timber_v210_eye.png"), 60)
cc = Vector((0, 0, 1.0))
shot(cam, Vector((-7.5, -9.5, 7.0)), cc, os.path.join(OUTP, "h9_timber_v210_34.png"), 55)
print("[v210 previews]", sorted(os.listdir(OUTP)))
