"""Example generator: a 4x4x4-stud beveled crate exported as a Roblox-ready FBX.

Usage:
  /Applications/Blender.app/Contents/MacOS/Blender -b -P assets/_examples/make_crate.py -- --out /tmp/crate.fbx
"""
import sys, argparse, bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser(); ap.add_argument("--out", default="/tmp/crate.fbx"); ap.add_argument("--size", type=float, default=4.0)
args = ap.parse_args(argv)

# Clean scene, 1 Blender unit = 1 stud
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system = 'NONE'

# Build: cube with bevel, origin at bottom-center
bpy.ops.mesh.primitive_cube_add(size=args.size, location=(0, 0, args.size / 2))
crate = bpy.context.active_object; crate.name = "Crate"
bev = crate.modifiers.new("Bevel", "BEVEL"); bev.width = args.size * 0.04; bev.segments = 2
bpy.ops.object.modifier_apply(modifier=bev.name)
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Simple material (Studio converts Principled BSDF textures to SurfaceAppearance)
mat = bpy.data.materials.new("CrateWood"); mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.55, 0.35, 0.18, 1)
crate.data.materials.append(mat)

tris = sum(len(p.vertices) - 2 for o in bpy.data.objects if o.type == 'MESH' for p in o.data.polygons)
assert tris <= 20000, f"{tris} triangles exceeds Roblox's 20k per-mesh limit"

bpy.ops.export_scene.fbx(
    filepath=args.out, use_selection=False, apply_scale_options='FBX_SCALE_UNITS',
    axis_forward='Z', axis_up='Y', path_mode='COPY', embed_textures=True,
    add_leaf_bones=False, bake_anim=False, mesh_smooth_type='FACE')
print(f"Exported {args.out} ({tris} tris)")
