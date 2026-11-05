"""Pass 10: VR wrist bracer (decoration on the off-hand forearm, carries a SurfaceGui face).

  vr_wrist_bracer  leather sleeve (forearm ~0.35 dia) with brass end rings, two dark straps with brass buckles under
                   the wrist, a raised leather pad + brass bezel on the back of the wrist, and the flat 16:10 face
                   quad `WristFace` (0.32 x 0.20) in the bezel for a SurfaceGui. A tiny amber Glow gem on the bezel's
                   finger end ties it to the course lanterns.

Prop frame (Roblox axes; Blender (x, y, z) = Roblox (x, -z, y)):
  +X = along the forearm toward the FINGERS (wrist end, slightly narrower)
  +Y = out of the BACK of the wrist = WristFace normal (toward the viewer's face when the wrist is turned up to look)
  +Z = X cross Y = across the wrist (thumb side on a LEFT arm, little-finger side on a right arm; the mesh is
       mirror-symmetric in Z, so it fits either arm)
  origin / pivot = wrist centre: on the forearm axis, at the bracer's mid-length (face centre is straight above it)
"""
import math
import bmesh
from mathutils import Matrix
from registry import prop

TAU = 2 * math.pi
ARM_D = 0.35                      # brief: Roblox VR forearm ~0.35 stud diameter
L = 0.46                          # sleeve length along the forearm (x -0.23..+0.23)
R_ELBOW, R_WRIST = 0.214, 0.199   # sleeve outer radius at the elbow end (-X) / wrist end (+X)
T_LEATHER = 0.022                 # sleeve thickness (inner radius 0.177..0.192 >= ARM_D / 2)
SEG = 14
FACE_W, FACE_H = 0.32, 0.20       # brief: EXACT 16:10 face; W along +X (forearm), H along Z (across the wrist)
FACE_Y = 0.238                    # face plane height above the pivot (Roblox +Y)
PAD = (0.40, 0.28)                # leather pad under the bezel (x, z)
BEZ_IN = 0.002                    # bezel plate top sits this far below the face (separate MeshPart, no z-fight)
FRAME_W, FRAME_TOP = 0.022, 0.252 # bezel frame bars around the face: width, top height (face recessed 0.014)


def _ring_tube(pb, mat, stations, segs=SEG, matrix=None):
    """Open-ended thick tube along Blender X. stations: [(x, r_out, r_in)]: outer + inner walls + end annuli."""
    t = bmesh.new()
    outer, inner = [], []
    for (x, ro, ri) in stations:
        outer.append([t.verts.new((x, ro * math.cos(TAU * i / segs), ro * math.sin(TAU * i / segs)))
                      for i in range(segs)])
        inner.append([t.verts.new((x, ri * math.cos(TAU * i / segs), ri * math.sin(TAU * i / segs)))
                      for i in range(segs)])
    for k in range(len(stations) - 1):
        for i in range(segs):
            j = (i + 1) % segs
            t.faces.new((outer[k][i], outer[k][j], outer[k + 1][j], outer[k + 1][i]))
            t.faces.new((inner[k][j], inner[k][i], inner[k + 1][i], inner[k + 1][j]))
    for i in range(segs):
        j = (i + 1) % segs
        t.faces.new((outer[0][j], outer[0][i], inner[0][i], inner[0][j]))
        t.faces.new((outer[-1][i], outer[-1][j], inner[-1][j], inner[-1][i]))
    bmesh.ops.recalc_face_normals(t, faces=t.faces)
    pb.add(mat, t, matrix)


def _r_out(x):
    return R_ELBOW + (R_WRIST - R_ELBOW) * (x + L / 2) / L


def _face_quad(pb):
    """WristFace: one flat quad (2 tris), Blender +Z (Roblox +Y) normal, centred over the pivot."""
    t = bmesh.new()
    hw, hh = FACE_W / 2, FACE_H / 2
    vs = [t.verts.new(p) for p in ((-hw, -hh, FACE_Y), (hw, -hh, FACE_Y), (hw, hh, FACE_Y), (-hw, hh, FACE_Y))]
    t.faces.new(vs)                    # CCW seen from +Z -> normal +Z
    pb.add("WristFace", t)


def _post(root, objs):
    """Rename the face MeshPart to `WristFace` and give it exact 0-1 UVs (U along +X = toward the fingers,
    V along Roblox -Z = Blender +Y, so image top-left lands at the face's (-X, -Z) corner)."""
    for o in objs:
        if o.name.endswith("__WristFace"):
            o.name = o.data.name = "WristFace"
            o["lg_mat"] = "WristFace"
            o["lg_keep_uv"] = 1
            me = o.data
            uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name="UVMap")
            for poly in me.polygons:
                for li in poly.loop_indices:
                    co = me.vertices[me.loops[li].vertex_index].co
                    uv.data[li].uv = ((co.x + FACE_W / 2) / FACE_W, (co.y + FACE_H / 2) / FACE_H)


def _uv_test_image():
    """16:10 test card for the face-on preview only: grid, red = top-left, green = top-right, blue = bottom-left."""
    import bpy
    import numpy as np
    w, h = 640, 400
    a = np.zeros((h, w, 4), np.float32)
    a[..., :3] = (0.93, 0.88, 0.76)
    a[..., 3] = 1
    a[::50, :, :3] = a[:, ::40, :3] = (0.35, 0.3, 0.25)       # 16 x 8 grid
    a[:6, :, :3] = a[-6:, :, :3] = a[:, :6, :3] = a[:, -6:, :3] = (0.1, 0.1, 0.1)
    # numpy rows run bottom (V 0) -> top (V 1) in Blender images
    a[h - 100:h - 6, 6:120, :3] = (0.85, 0.15, 0.1)          # top-left  (U 0, V 1)
    a[h - 100:h - 6, w - 120:w - 6, :3] = (0.15, 0.7, 0.2)   # top-right (U 1, V 1)
    a[6:100, 6:120, :3] = (0.15, 0.3, 0.85)                  # bottom-left (U 0, V 0)
    a[190:210, 160:480, :3] = (0.1, 0.1, 0.1)                # arrow shaft -> +U (toward the fingers)
    for k in range(40):
        a[200 - 40 + k:200 + 40 - k, 480 + k, :3] = (0.1, 0.1, 0.1)
    img = bpy.data.images.new("wristface_uvtest", w, h, alpha=True)
    img.pixels.foreach_set(a.ravel())
    return img


def _previews(sc, stage, root, objs, prev_dir, look_at):
    """eye: what the player sees glancing at the turned-up wrist (~1.1 studs away); 34: 3/4 elevated; face: straight
    down the face normal with a UV test card on WristFace (preview only, the FBX material stays flat)."""
    import bpy, os
    from mathutils import Vector
    cap = stage["cap"] if "cap" in stage else stage["capsule"]
    for o in [cap] + list(cap.children):
        o.hide_render = True
    lift = 0.2                                              # sleeve bottom just above the ground
    root.location = (0, 0, lift)
    bpy.context.view_layer.update()
    cam = stage["cam"]
    c = Vector((0, 0, lift))
    fc = Vector((0, 0, lift + FACE_Y))

    def shot(view, loc, tgt, fov=40):
        cam.data.angle = math.radians(fov)
        cam.location = loc
        look_at(cam, tgt)
        sc.render.filepath = os.path.join(prev_dir, f"vr_wrist_bracer_{view}.png")
        bpy.ops.render.render(write_still=True)

    # eye: viewer above the face, a little toward the elbow and off the thumb side, looking down onto the wrist
    shot("eye", fc + Vector((-0.45, -0.35, 0.95)), fc + Vector((0.02, 0, -0.04)), 40)
    shot("34", c + Vector((-0.75, -0.95, 0.75)), c + Vector((0, 0, 0.05)), 40)
    face = [o for o in objs if o.name == "WristFace"][0]
    m0 = face.data.materials[0]
    m = m0.copy()
    nt = m.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _uv_test_image()
    bsdf = nt.nodes.get("Principled BSDF")
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    face.data.materials[0] = m
    shot("face", fc + Vector((0, 0, 1.0)), fc, 32)
    face.data.materials[0] = m0
    bpy.data.materials.remove(m)
    root.location = (0, 0, 0)
    cam.data.angle = math.radians(60)
    bpy.context.view_layer.update()
    return ("eye", "34", "face")


VR_ATTACH = dict(
    attach="Off-hand forearm (weld to the VR hand part / UserCFrame hand CFrame with an offset back up the wrist)",
    pivot="wrist centre: on the forearm axis at the bracer's mid-length (the model's root / PrimaryPart pivot)",
    axes=dict(
        x="+X = along the forearm toward the FINGERS",
        y="+Y = out of the BACK of the wrist = WristFace normal (toward the viewer's face when the wrist is turned up)",
        z="+Z = X cross Y = across the wrist (thumb side on a left arm; the mesh is mirror-symmetric in Z)"),
    forearm_diameter_fit=ARM_D,
    sleeve=dict(length=L, outer_radius_elbow=R_ELBOW, outer_radius_wrist=R_WRIST,
                inner_radius_elbow=round(R_ELBOW - T_LEATHER, 3), inner_radius_wrist=round(R_WRIST - T_LEATHER, 3)),
    wrist_face=dict(
        meshpart="WristFace", size_studs=[FACE_W, FACE_H], aspect="16:10 (1.6 exactly)",
        size_axes="0.32 along +X (forearm), 0.20 along Z (across the wrist); flat quad, 2 tris, zero thickness",
        center_offset_from_pivot=[0.0, FACE_Y, 0.0], normal="+Y",
        uv="0..1 fills the quad exactly: U 0 -> 1 along +X (toward the fingers), V 0 -> 1 along -Z",
        surfacegui=("SurfaceGui on WristFace, Face = Top (the +Y face); canvas 0.32 x 0.20 studs, e.g. SizingMode "
                    "FixedSize CanvasSize 800 x 500 (or PixelsPerStud 2500). The Top face's GUI width runs along +X; "
                    "GUI up should be -Z (the same as the UV V direction) - confirm in Studio once, and if text reads "
                    "upside down rotate the content 180 (UIs can't be mirrored, but nothing here is mirrored)."),
        recess="brass bezel frame bars rise 0.014 above the face around its edges (none over the face itself)"),
    collision="decoration only: CanCollide / CanTouch / CanQuery = false, Massless = true",
)


@prop("vr_wrist_bracer", ["VR"], "P1", target=[L, 0.49, 0.43], group="vr", view="x",
      origin="PIVOT = WRIST CENTRE (forearm axis, bracer mid-length); +X fingers, +Y back of wrist / face normal",
      front="+Y = WristFace normal (back of the wrist); +X toward the fingers",
      extra=dict(vr_attach=VR_ATTACH),
      previews_fn=_previews,
      notes=f"Pass 10: Lantern Grove leather-and-brass wrist bracer for the VR off-hand forearm (~{ARM_D:g} dia), "
            f"decoration only. Flat 16:10 SurfaceGui face `WristFace` {FACE_W:g} x {FACE_H:g} studs, centre "
            f"(0, {FACE_Y:g}, 0) from the pivot, normal +Y; see vr_attach for axes and SurfaceGui setup. Glow gem: "
            "optional tiny PointLight (Range 2, Brightness 0.5, #FFB347) or none.")
def vr_wrist_bracer(pb):
    hx = L / 2
    # leather sleeve, slight taper toward the wrist, 3 stations (a soft bulge mid-way)
    xs = (-hx, 0.0, hx)
    _ring_tube(pb, "Leather", [(x, _r_out(x) + (0.004 if x == 0 else 0), _r_out(x) - T_LEATHER) for x in xs])
    # brass end rings
    for x in (-hx + 0.012, hx - 0.012):
        pb.torus("Brass", _r_out(x) + 0.004, 0.013, SEG, 4, loc=(x, 0, 0), rot=(0, 90, 0), smooth=False)
    # dark leather straps + brass buckles under the wrist (Roblox -Y = Blender -Z)
    for x in (-0.11, 0.11):
        ro = _r_out(x) + 0.004
        _ring_tube(pb, "LeatherDark", [(x - 0.026, ro + 0.012, ro - 0.006), (x + 0.026, ro + 0.012, ro - 0.006)])
        pb.box("Brass", (0.072, 0.056, 0.016), loc=(x, 0, -(ro + 0.016)), bevel=0.004)
        pb.box("LeatherDark", (0.03, 0.05, 0.012), loc=(x + 0.05, 0, -(ro + 0.01)))       # strap tail
    # raised leather pad on the back of the wrist, brass bezel plate + frame around the face
    pb.box("Leather", (PAD[0], PAD[1], 0.07), loc=(0, 0, 0.18), bevel=0.012, segs=1)
    bz_top = FACE_Y - BEZ_IN
    pb.box("Brass", (FACE_W + 2 * FRAME_W, FACE_H + 2 * FRAME_W, bz_top - 0.2), loc=(0, 0, (bz_top + 0.2) / 2))
    hw, hh = FACE_W / 2, FACE_H / 2
    fh = FRAME_TOP - bz_top
    for sx in (-1, 1):
        pb.box("Brass", (FRAME_W, FACE_H + 2 * FRAME_W, fh), loc=(sx * (hw + FRAME_W / 2), 0, bz_top + fh / 2))
    for sy in (-1, 1):
        pb.box("Brass", (FACE_W, FRAME_W, fh), loc=(0, sy * (hh + FRAME_W / 2), bz_top + fh / 2))
    # rivets at the pad corners, amber Glow gem on the bezel's finger end
    for sx in (-1, 1):
        for sy in (-1, 1):
            pb.sphere("Brass", 0.012, loc=(sx * (PAD[0] / 2 - 0.016), sy * (PAD[1] / 2 - 0.016), 0.215),
                      segs=6, rings=3, smooth=False)
    pb.sphere("Glow", 0.016, loc=(hw + FRAME_W + 0.014, 0, 0.226), scale=(1, 1, 0.7), segs=8, rings=4, smooth=False)
    _face_quad(pb)
    return _post
