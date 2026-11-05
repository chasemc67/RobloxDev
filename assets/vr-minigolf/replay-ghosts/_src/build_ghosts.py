"""Bug-recorder replay ghosts (Lantern Grove VR mini golf).
blender -b --factory-startup -P build_ghosts.py -- <outdir>
1 Blender unit = 1 stud. Built Z-up; FBX exported axis_forward -Z, axis_up Y, so
Roblox X = Blender X, Roblox Y = Blender Z, Roblox Z = -Blender Y."""
import bpy, bmesh, sys, os, json, math
from mathutils import Matrix, Vector
OUT = sys.argv[sys.argv.index("--") + 1]
FBX = os.path.join(OUT, "fbx"); PRV = os.path.join(OUT, "previews")
os.makedirs(FBX, exist_ok=True); os.makedirs(PRV, exist_ok=True)
HEX = "#9FE6F2"

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
def srgb2lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
rgb = [srgb2lin(int(HEX[i:i + 2], 16) / 255) for i in (1, 3, 5)]
mat = bpy.data.materials.new("GhostCyan"); mat.use_nodes = True
bs = mat.node_tree.nodes["Principled BSDF"]
bs.inputs["Base Color"].default_value = (*rgb, 1); bs.inputs["Roughness"].default_value = 0.5
mat.diffuse_color = (*rgb, 1)

def R(x, y, z):  # roblox coords -> blender
    return Vector((x, -z, y))

def add_ellipsoid(bm, c, r, segs, rings, smooth=True):
    res = bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    m = Matrix.Translation(c) @ Matrix.Diagonal((*r, 1))
    bmesh.ops.transform(bm, matrix=m, verts=res["verts"])
    for f in {f for v in res["verts"] for f in v.link_faces}: f.smooth = smooth

def add_cyl(bm, p0, p1, r, segs=8):
    d = p1 - p0
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r, radius2=r, depth=d.length)
    rot = d.normalized().to_track_quat("Z", "Y").to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation((p0 + p1) / 2) @ rot, verts=res["verts"])
    for f in {f for v in res["verts"] for f in v.link_faces}:
        f.smooth = abs(f.normal.normalized().dot(d.normalized())) < 0.5 if False else True
    return res

def add_box(bm, c, size, bevel=0.0):
    res = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ Matrix.Diagonal((*size, 1)), verts=res["verts"])
    if bevel:
        edges = list({e for v in res["verts"] for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=edges, offset=bevel, segments=2, affect="EDGES", profile=0.5)
    return res

def finish(name, bm, flat_box=False):
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    return o

objs = {}
# head: rounded head/visor, 0.8 W x 1.0 H x 0.9 D studs, pivot centre
bm = bmesh.new(); add_ellipsoid(bm, R(0, 0, 0), (0.4, 0.45, 0.5), 16, 10)  # blender (x, y=depth, z=height)
objs["ghost_head"] = (finish("ghost_head", bm), "centre of the head (bbox centre)", "front = Roblox -Z (look direction)")

# hands: mitten, fingers forward (-Z roblox), palm faces the body centre, pivot at grip centre
def mitten(name, side):  # side +1 right, -1 left
    bm = bmesh.new()
    add_ellipsoid(bm, R(0.0, 0.0, -0.04), (0.10, 0.24, 0.17), 14, 8)          # palm+fingers mitt (X thick, Z long, Y tall)
    add_ellipsoid(bm, R(-side * 0.07, 0.11, -0.10), (0.05, 0.12, 0.05), 10, 6)  # thumb, on top, toward palm side
    return finish(name, bm)
objs["ghost_hand_left"] = (mitten("ghost_hand_left", -1), "grip centre (centre of the closed mitt, where a club grip sits)", "fingers = Roblox -Z, thumb +Y, palm faces +X (toward body centre)")
objs["ghost_hand_right"] = (mitten("ghost_hand_right", 1), "grip centre (centre of the closed mitt, where a club grip sits)", "fingers = Roblox -Z, thumb +Y, palm faces -X (toward body centre)")

# putter: 3.05 studs (34 in at 0.28 m/stud), grip end at origin, shaft down -Y, toe +X, face -Z
L = 3.05
bm = bmesh.new()
add_cyl(bm, R(0, 0, 0), R(0, -0.95, 0), 0.055, 8)            # grip
add_cyl(bm, R(0, -0.95, 0), R(0, -(L - 0.08), 0), 0.03, 8)   # shaft
add_box(bm, R(0.08, -(L - 0.045), 0), (0.40, 0.11, 0.09), bevel=0.015)  # head (x=len, y=depth, z=height)
objs["ghost_club"] = (finish("ghost_club", bm), "grip end (top of the grip, on the shaft axis)", "shaft = Roblox -Y, toe +X, face normal -Z")

# ball: radius 0.08 stud (holes.json ball_radius), pivot centre
bm = bmesh.new(); add_ellipsoid(bm, R(0, 0, 0), (0.08, 0.08, 0.08), 16, 10)
objs["ghost_ball"] = (finish("ghost_ball", bm), "centre", "n/a")

man = {"set": "Bug-recorder replay ghosts (Lantern Grove VR mini golf)", "units": "studs; 1 Blender unit = 1 stud (1 stud = 0.28 m)",
       "axes": "Roblox Y-up; FBX axis_forward -Z, axis_up Y, transforms applied (identity objects)",
       "material": {"name": "GhostCyan", "color": HEX, "opaque": True, "note": "set Transparency in Roblox"},
       "assets": []}
for name, (o, pivot, orient) in objs.items():
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
    p = os.path.join(FBX, name + ".fbx")
    bpy.ops.export_scene.fbx(filepath=p, use_selection=True, apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0,
        apply_unit_scale=True, bake_space_transform=True, axis_forward="-Z", axis_up="Y", add_leaf_bones=False,
        bake_anim=False, mesh_smooth_type="FACE", object_types={"MESH"}, use_metadata=False)
    vs = [v.co for v in o.data.vertices]
    mn = Vector([min(v[i] for v in vs) for i in range(3)]); mx = Vector([max(v[i] for v in vs) for i in range(3)])
    rmn = [mn.x, mn.z, -mx.y]; rmx = [mx.x, mx.z, -mn.y]
    tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
    man["assets"].append(dict(name=name, fbx=f"fbx/{name}.fbx", tris=tris,
        dims_studs=[round(b - a, 3) for a, b in zip(rmn, rmx)], bbox_min_roblox=[round(x, 3) for x in rmn],
        bbox_max_roblox=[round(x, 3) for x in rmx], pivot=pivot, orientation=orient))
    print("ASSET", name, tris)
man["notes"] = ["ghost_club: no putter entry exists in lantern-grove/models/manifest.json; sized as a standard 34 in putter (3.05 studs grip end to sole). Scale on Y if the in-game putter differs.",
                "ghost_ball: radius 0.08 stud from lantern-grove/holes.json ball_radius."]
json.dump(man, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)

# previews: workbench, one render per asset, framed to its bbox
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
sc.display.shading.show_cavity = True
sc.render.resolution_x = sc.render.resolution_y = 512; sc.render.film_transparent = False
w = bpy.data.worlds.new("w"); sc.world = w; w.color = (0.12, 0.13, 0.16)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"
for name, (o, _, _) in objs.items():
    for n2, (o2, _, _) in objs.items(): o2.hide_render = (n2 != name)
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    c = sum(bb, Vector()) / 8; ext = max((b - c).length for b in bb)
    d = Vector((1, -1.3, 0.8)).normalized()
    cam.location = c + d * (ext * 4 + 1); cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = ext * 2.3
    sc.render.filepath = os.path.join(PRV, name + ".png"); bpy.ops.render.render(write_still=True)
print("GHOSTS_DONE")
