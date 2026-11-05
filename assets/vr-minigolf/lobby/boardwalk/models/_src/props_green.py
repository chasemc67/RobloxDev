"""Practice green group: turf slab + bumper rail with 2 cup holes, windmill + separate blades, cup flag, tee mat."""
import math
from mathutils import Vector, Matrix
import bwlib as L
from registry import prop, FRONT_SOUTH, FRONT_NONE

# lobby.json practiceGreen: centre (145, 0, 65); cups (158, 60) and (150, 58) -> local Roblox (13, -5), (5, -7)
GREEN_C = (145.0, 65.0)
CUPS_RB = [(158.0 - 145.0, 60.0 - 65.0), (150.0 - 145.0, 58.0 - 65.0)]
CUP_R, CUP_DEPTH = 0.5, 0.35
TURF_TOP = 0.4
RAIL_H = 1.2       # 0.8 above the turf


def _boolean_cups(objs):
    import bpy
    tgt = next(o for o in objs if o.name.endswith("__BW_Atlas"))
    for (rx, rz) in CUPS_RB:
        x, y = rx, -rz                                   # Roblox (x, z) -> Blender (x, -z)
        t = L.bmesh.new()
        L.bmesh.ops.create_cone(t, cap_ends=True, cap_tris=False, segments=16, radius1=CUP_R, radius2=CUP_R,
                                depth=0.6)
        L.bmesh.ops.translate(t, vec=(x, y, TURF_TOP - CUP_DEPTH + 0.3), verts=t.verts)
        L.map_uvs(t, ("flat", "awn_cream"))
        me = bpy.data.meshes.new("_cut")
        t.to_mesh(me)
        t.free()
        cut = bpy.data.objects.new("_cut", me)
        bpy.context.scene.collection.objects.link(cut)
        mod = tgt.modifiers.new("cup", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cut
        mod.solver = "EXACT"
        dg = bpy.context.evaluated_depsgraph_get()
        newme = bpy.data.meshes.new_from_object(tgt.evaluated_get(dg))
        old = tgt.data
        tgt.modifiers.clear()
        tgt.data = newme
        newme.name = old.name
        bpy.data.meshes.remove(old)
        bpy.data.objects.remove(cut)
        bpy.data.meshes.remove(me)
    b = L.bmesh.new()
    b.from_mesh(tgt.data)
    L.bmesh.ops.triangulate(b, faces=[f for f in b.faces if len(f.verts) > 3])
    b.to_mesh(tgt.data)
    b.free()
    try:
        tgt.data.set_sharp_from_angle(angle=math.radians(50))
    except Exception:
        pass
    return {"cups": [dict(center=[rx, TURF_TOP, rz], radius=CUP_R, depth=CUP_DEPTH,
                          world=[GREEN_C[0] + rx, TURF_TOP, GREEN_C[1] + rz]) for rx, rz in CUPS_RB],
            "turf_top_y": TURF_TOP, "bumper_top_y": RAIL_H,
            "size_note": "34 x 0.4 x 20 slab; bumper rail (inside the footprint) rises 0.8 above the turf -> bbox Y 1.2"}


@prop("bw_practice_green", "green", target=[34, 1.2, 20], tris_max=2000, front=FRONT_NONE,
      notes="Turf slab 34x0.4x20 (top Y 0.4) with a rounded wooden bumper rail 0.8 above the turf, chunky corner "
            "posts, 2 cup holes (r 0.5, 0.35 deep) at the lobby.json cup positions.")
def practice_green(pb):
    pb.box((34.0, 20.0, TURF_TOP), loc=(0, 0, TURF_TOP / 2), mapping=("trim", "turf", 34.0))
    W = 0.6
    for s in (-1, 1):
        pb.box_minmax((-16.1, s * 10 - (W if s > 0 else 0) + (0 if s > 0 else 0), 0.0),
                      (16.1, s * 10 + (0 if s > 0 else W), RAIL_H), mapping=("trim", "beam", 5.0), bevel=0.22)
        pb.box_minmax((min(s * 17, s * 17 - s * W), -9.1, 0.0), (max(s * 17, s * 17 - s * W), 9.1, RAIL_H),
                      mapping=("trim", "beam", 5.0), bevel=0.22)
    for sx in (-1, 1):
        for sy in (-1, 1):
            pb.box((0.9, 0.9, RAIL_H), loc=(sx * 16.55, sy * 9.55, RAIL_H / 2), mapping=("trim", "beam", 3.0),
                   bevel=0.25)
    return _boolean_cups


# ----------------------------------------------------------------------------- windmill
HUB_Z = 7.0          # hub height above the windmill base (builder blades base Y 3.4 + 4 = 7.4 world = 0.4 + 7.0)
HUB_Y = -3.3         # Blender y of the blade plane centre (Roblox +3.3, builder Z 67.3 vs windmill Z 64)


@prop("bw_windmill", "green", target=[6, 10, 6], tris_max=3500, front=FRONT_SOUTH,
      notes="Octagonal plank tower on a stone plinth with a ball tunnel (2 W x 1.2 H) running north-south, "
            "striped roof. Blade hub (pivot of bw_windmill_blades) at local (0, 7.0, +3.3).")
def windmill(pb):
    st = ("trim", "stone", 3.0)
    pb.box_minmax((-3.0, -3.0, 0.0), (-1.0, 3.0, 1.6), mapping=st, bevel=0.15)
    pb.box_minmax((1.0, -3.0, 0.0), (3.0, 3.0, 1.6), mapping=st, bevel=0.15)
    pb.box_minmax((-1.0, -3.0, 1.2), (1.0, 3.0, 1.6), mapping=st, bevel=0.1)
    ph = math.pi / 8
    pb.lathe([(2.75, 1.6), (2.55, 3.5), (2.3, 5.6), (2.05, 7.8)], segs=8, phase=ph, mapping=("trim", "deck", 8.0),
             smooth=False)
    pb.lathe([(2.35, 7.75), (2.45, 7.85), (2.45, 8.1), (2.3, 8.15)], segs=8, phase=ph, mapping=("flat", "brass"),
             smooth=False)
    pb.lathe([(2.75, 8.0), (2.6, 8.25), (1.6, 8.95), (0.6, 9.5), (0.0, 9.68)], segs=8, phase=ph,
             mapping=("stripes", "awn_red", "awn_cream", 8, 0.0), smooth=False)
    pb.sphere(0.32, loc=(0, 0, 9.68), segs=8, rings=5, mapping=("flat", "brass"))
    # door + windows (dark inset slabs on the south face; tower face at y ~ -2.2)
    for (z0, z1, w) in ((5.2, 6.2, 0.8),):
        pb.box((w, 0.3, z1 - z0), loc=(0, -2.18, (z0 + z1) / 2), rot=(6.4, 0, 0), mapping=("flat", "ink"))
    pb.box((0.8, 0.3, 1.0), loc=(0, 2.18, 4.6), rot=(-6.4, 0, 0), mapping=("flat", "ink"))
    # axle stub out to the blade hub
    pb.cyl(0.35, 0.35, 1.1, segs=8, loc=(0, -2.4, HUB_Z), rot=(90, 0, 0), mapping=("flat", "post"))
    return lambda objs: {"blade_hub": dict(local=[0.0, HUB_Z, -HUB_Y],
                                           note="bw_windmill_blades pivot goes here: world = windmill pivot + "
                                                "(0, 7.0, 3.3) = (150, 7.4, 67.3) for the builder placement")}


@prop("bw_windmill_blades", "green", target=[8, 8, 0.5], tris_max=500, front=FRONT_SOUTH, pivot="hub",
      motion=dict(type="rotate", axis_roblox=[0, 0, 1], rpm=6, pivot="local origin = hub centre",
                  note="spin about the local Z axis (north-south), 6 rpm; place pivot at windmill hub"),
      collision=[dict(center=[0, 0, 0], size=[8, 8, 0.5])],
      notes="4 lattice sails; pivot = hub centre (geometry spans +-4 around it, not base-centred).")
def windmill_blades(pb):
    pb.cyl(0.55, 0.55, 0.5, segs=10, loc=(0, 0, 0), rot=(90, 0, 0), mapping=("flat", "brass"), smooth=False)
    for k in range(4):
        R = Matrix.Rotation(math.radians(90 * k + 12), 4, "Y")
        pb.box((0.35, 0.3, 3.6), loc=(0, 0, 2.2), mapping=("trim", "beam", 3.0), bevel=0.06, segs=1, matrix=R)
        pb.box((1.3, 0.12, 2.9), loc=(0.85, 0.06, 2.55), mapping=("fit", "parch"), matrix=R)
        for z in (1.55, 2.55, 3.55):
            pb.box((1.45, 0.2, 0.3), loc=(0.85, -0.1, z), mapping=("flat", "post"), matrix=R)


# ----------------------------------------------------------------------------- cup flag / tee
@prop("bw_cup_flag", "green", target=[0.6, 5, 0.6], tris_max=200, front=FRONT_NONE,
      notes="Pole on the pivot axis with a red banner hanging from a T-crossbar and a cup-liner collar ring at the "
            "base (0.6 dia). Place the pivot on the cup centre at turf level.")
def cup_flag(pb):
    pb.cyl(0.3, 0.3, 0.06, segs=10, loc=(0, 0, 0.03), mapping=("flat", "awn_cream"), smooth=False)
    pb.cyl(0.12, 0.12, 4.75, segs=8, loc=(0, 0, 2.375), mapping=("flat", "awn_cream"))
    pb.box((0.6, 0.16, 0.16), loc=(0, 0, 4.62), mapping=("flat", "brass"))
    pb.sphere(0.15, loc=(0, 0, 4.85), segs=8, rings=4, mapping=("flat", "brass"))
    pb.prism([(-0.28, 4.54), (0.28, 4.54), (0.28, 3.55), (0.0, 3.3), (-0.28, 3.55)], 0.08, rot=(90, 0, 0),
             mapping=("flat", "awn_red"))


@prop("bw_tee_mat", "green", target=[2, 0.1, 2], tris_max=20, front=FRONT_NONE,
      notes="Flat fringe-green mat 2x0.1x2 (12 tris).")
def tee_mat(pb):
    pb.box((2.0, 2.0, 0.1), loc=(0, 0, 0.05), mapping=("flat", "fringe"))
