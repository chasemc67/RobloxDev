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
   - **Many small FBX?** Merge them in Blender into one FBX first (one top-level Empty per source file, the same export settings), so it's a single importer pass instead of one computer-use run per file. Example: `assets/vr-mini-golf/sugarloaf-canyon/models/_src/movers/merge_for_import.py` (35 files -> 1, with a bbox round-trip check).
   - **Check sizes after import.** As seen in stage w, the importer can auto-scale the *whole scene* so its widest object lands on 2048 (warning "One of the objects dimensions are larger than can be imported"; a 92-stud piece made everything x22.26), and it also turned the scene 180 deg about Y. Compare MeshPart sizes with the export's bboxes and undo it in Luau: `Size /= k; CFrame = CFrame.Angles(0, math.pi, 0) * CFrame.new(pos / k) * rotation`.
   - Generalized merge script: `games/vr-mini-golf/tools/merge_fbx_for_import.py` (`Blender -b --factory-startup --python merge_fbx_for_import.py -- out.fbx in1.fbx in2.fbx ...`; writes `<out>_merge_report.json`). Stage ab merged 213 kit FBX into 3 files (a few hundred meshes each, 6-10 MB) and 31 lobby FBX into 1; each imported in one Codex run.
   - Stage ab saw the auto-scale on every merged file (x2.9, x16, x3.3, x74; the 180-degree turn too, baked into the mesh data with the part rotation left at 0). The robust fix: set each MeshPart's Size and centre straight from the manifest (`SugarloafBuilder.PrepareKit`), only taking the turn out of the rotation. A single-mesh prop can't show its turn by centre fitting, so give it the common turn.
   - Untextured materials can come in near-white: re-apply colours/materials from your manifest by the `<piece>__<Material>` mesh names.
2. **Open Cloud Assets API** (`POST https://apis.roblox.com/assets/v1/assets`, type Model, with `.fbx`): needs an API key with asset write permission. **None is configured yet**, so ask Chase before setting one up. Afterwards, use `insert_asset` via the Studio MCP with the returned asset ID.
3. After inserting: anchor and position with `execute_luau`, set `CollisionFidelity` (Box or Hull for performance), and check in a playtest.
