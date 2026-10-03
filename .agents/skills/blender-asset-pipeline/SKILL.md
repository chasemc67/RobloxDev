---
name: blender-asset-pipeline
description: Make Roblox-ready 3D assets (meshes, PBR textures) in Blender on Chase's Mac Mini, with headless Blender Python scripts (or a Blender MCP if one is set up), the right scale, axes and triangle budget, and FBX export. Then import through Studio's 3D Importer or upload with Open Cloud. Use when a game needs custom meshes, props, buildings or textures beyond Studio parts.
---

# Blender asset pipeline (Blender to Roblox)

## Tools
- Blender 5.2 LTS: `/Applications/Blender.app/Contents/MacOS/Blender`
- **No Blender MCP is set up yet.** (If one is added later, e.g. `uvx blender-mcp` plus the ahujasid add-on, it needs the Blender GUI running with the add-on's server started.) **Default: headless scripts.**
- Before generating a mesh in Blender, check whether the Studio MCP's `generate_mesh`, `generate_procedural_model` or `insert_asset` is faster for the job.

## Headless workflow
```bash
B=/Applications/Blender.app/Contents/MacOS/Blender
$B -b -P assets/<game>/make_<thing>.py -- --out assets/<game>/<thing>.fbx   # build from scratch
$B -b assets/<game>/<thing>.blend -P script.py                              # modify an existing .blend
$B -b --python-expr "import bpy; print(bpy.app.version_string)"             # quick check
```
- Keep **generator scripts** in `assets/<game>/` (`make_<thing>.py`) so assets can be regenerated and tweaked. Commit the scripts and the final exports. Gitignore `*.blend1`.
- `assets/_examples/make_crate.py` is a working template (builds a beveled crate and exports FBX).
- To preview: render a PNG with `bpy.ops.render.render(write_still=True)` and look at it, or check in Studio after importing.

## Roblox requirements (from create.roblox.com docs, checked Oct 2026; re-check if anything looks off)
- **Formats**: `.fbx` (preferred: hierarchy, PBR textures, rigs, animation, vertex colors), `.gltf`, `.obj` (simple single meshes only).
- **Budget**: each mesh is **at most 20,000 triangles**. Studio auto-simplifies anything above that. Avatar items have tighter budgets.
- Geometry should be watertight, have no zero-thickness faces, and use quads or tris (no n-gons).
- **Scale**: set Blender Scene > Units > Unit System = **None**, so 1 Blender unit = 1 stud. When exporting FBX, set **Apply Scalings = FBX Unit Scale** and leave all other scales at 1.0. (The alternative is export Transform > Scale = 0.01 if you modeled in meters.) A Roblox character is about 5 studs tall. Check the size in Studio after importing.
- **Axes**: Forward = **Z Forward**, Up = **Y Up**.
- **Before export**: apply all transforms (`bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)`), and put the origin where the object should pivot or sit (usually bottom-center for props).
- **FBX options**: Path Mode = Copy, Embed Textures on, Add Leaf Bones off, Bake Animation off unless the asset is animated.
- **Textures and PBR**: use the Principled BSDF with Base Color, Normal, Roughness and Metallic image textures. On import, Studio builds a `SurfaceAppearance` from them. Use PNG, power-of-two sizes, at most 1024×1024. Fewer, shared materials is better.

## Script snippet (export)
```python
import bpy
bpy.context.scene.unit_settings.system = 'NONE'
bpy.ops.export_scene.fbx(
    filepath=out, use_selection=False, apply_scale_options='FBX_SCALE_UNITS',
    axis_forward='Z', axis_up='Y', path_mode='COPY', embed_textures=True,
    add_leaf_bones=False, bake_anim=False, mesh_smooth_type='FACE')
```
Count triangles before exporting:
`sum(len(p.vertices)-2 for o in bpy.data.objects if o.type=='MESH' for p in o.data.polygons)`

## Getting it into Roblox
1. **Studio 3D Importer** (File > Import 3D): a UI dialog, so it needs computer use. Check the scale, the preview and any warnings, then insert. The result is a `Model` with `MeshPart`s, saved as assets on the account.
2. **Open Cloud Assets API** (`POST https://apis.roblox.com/assets/v1/assets`, type Model, with `.fbx`): needs an API key with asset write permission. **None is configured yet**, so ask Chase before setting one up. Afterwards, use `insert_asset` via the Studio MCP with the returned asset ID.
3. After inserting: anchor and position with `execute_luau`, set `CollisionFidelity` (Box or Hull for performance), and check in a playtest.
