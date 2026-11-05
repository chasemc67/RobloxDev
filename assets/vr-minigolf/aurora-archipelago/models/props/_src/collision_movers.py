"""Round 3 'clear': COLLISION FBX for the two blocking movers, built straight from holes.json blockers.
  blender -b --factory-startup -P out_props/_src/collision_movers.py   -> fbx/<mover>_collision.fbx + _src/collision_movers.json
One root empty <mover>_collision at the holes.json pivot (FBX origin = pivot, same frame as the visual FBX) + one 8-vertex
box mesh per blocker, <mover>_collision__Collider_bNN (NN = holes.json blocker index + 1), material Collider. Corners are
the exact holes.json boxes at angle 0: centre + R_y(yaw) * (+-size/2), then rotated by `roll` about the mover axis (+Z)
about the pivot (holes.json schema: roll applies to the blocker's centre and orientation). In Studio: one MeshPart per box,
CollisionFidelity = Box (exact OBB), Transparency 1, CanCollide/CanTouch/CanQuery true, welded to the moving model.
Same FBX settings as build_all.export_fbx."""
import bpy, bmesh, os, sys, json, math

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import holesdata as D

MOVERS = (("aa_h12_paddle_wheel", 12, "paddle_wheel"), ("aa_h14_icicle_bell", 14, "icicle_bell"))
COLOR = "#FF00FF"


def corners(b):
    out = []
    for sx in (-.5, .5):
        for sy in (-.5, .5):
            for sz in (-.5, .5):
                x, z = D.yaw_rot(sx * b["size"][0], sz * b["size"][2], b.get("yaw", 0.0))
                p = [b["center"][0] + x, b["center"][1] + sy * b["size"][1], b["center"][2] + z]
                a = math.radians(b.get("roll", 0.0))
                out.append([p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a), p[2]])
    return out          # index = 4*ix + 2*iy + iz


FACES = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))


def material():
    m = bpy.data.materials.get("Collider") or bpy.data.materials.new("Collider")
    m.use_nodes = True
    bs = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    rgb = [int(COLOR[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    bs.inputs["Base Color"].default_value = (*lin, 1)
    m.diffuse_color = (*lin, 1)
    return m


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "NONE"
mat = material()
report = {}
for name, n, mid in MOVERS:
    m = D.mover(n, mid)
    cname = f"{name}_collision"
    col = bpy.data.collections.new(cname)
    sc.collection.children.link(col)
    root = bpy.data.objects.new(cname, None)
    col.objects.link(root)
    objs, parts = [], []
    for i, b in enumerate(m["blockers"]):
        C = corners(b)
        bm = bmesh.new()
        vs = [bm.verts.new((x, -z, y)) for x, y, z in C]            # Roblox -> Blender
        for f in FACES:
            bm.faces.new([vs[k] for k in f])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        oname = f"{cname}__Collider_b{i + 1:02d}"
        me = bpy.data.meshes.new(oname)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mat)
        ob = bpy.data.objects.new(oname, me)
        col.objects.link(ob)
        ob.parent = root
        objs.append(ob)
        parts.append(dict(mesh=oname, blocker_index=i, center=b["center"], size=b["size"], yaw=b.get("yaw", 0.0),
                          roll=b.get("roll", 0.0), tris=12, corners=[[round(v, 6) for v in p] for p in C]))
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    path = os.path.join(OUT, "fbx", f"{cname}.fbx")
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0,
                             axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True, add_leaf_bones=False,
                             bake_anim=False, mesh_smooth_type="FACE", use_mesh_modifiers=True,
                             object_types={"EMPTY", "MESH"}, use_custom_props=False)
    allc = [p for q in parts for p in q["corners"]]
    mn = [min(p[k] for p in allc) for k in range(3)]
    mx = [max(p[k] for p in allc) for k in range(3)]
    report[name] = dict(
        file=f"fbx/{cname}.fbx", root=cname, prop=name, hole=n, mover=mid, pivot=m["pivot"], axis=m["axis"],
        triangles=12 * len(parts), meshes=len(parts),
        bbox_size_studs=[round(b - a, 3) for a, b in zip(mn, mx)],
        bbox_center_from_origin=[round((a + b) / 2, 3) for a, b in zip(mn, mx)],
        material=dict(name="Collider", color=COLOR, note="preview colour only; set Transparency 1 in Studio"),
        roblox=("one MeshPart per box: CollisionFidelity Box (exact OBB of the holes.json blocker), Transparency 1, "
                "CanCollide/CanTouch/CanQuery true, Massless, welded to the visual model; CFrame = the mover pivot CFrame "
                "(the same CFrame as the visual FBX root) - or keep building the colliders as Parts from holes.json, "
                "they are identical"),
        source="holes.json Round 3 'clear' moving_parts[%s].blockers (exact, no padding)" % mid, parts=parts)
    print(f"[collision] {cname}: {len(parts)} boxes, {12 * len(parts)} tris -> {path}")
json.dump(report, open(os.path.join(SRC, "collision_movers.json"), "w"), indent=1)
