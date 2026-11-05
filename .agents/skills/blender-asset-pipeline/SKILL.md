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

## Lessons from Lantern Grove (assets/vr-minigolf/lantern-grove/models/_src)
- That folder holds a reusable generator library (`lglib.py`: per-material builder, lathe/tube/loft/rock helpers, booleans, text) plus a build/preview/manifest pipeline. Copy it for new prop sets.
- With unit system NONE + `FBX_SCALE_UNITS`, the FBX header says **metres** (UnitScaleFactor 100), but the vertex values are studs. In Import 3D, pick Stud as the scale unit. A prop coming in 3.57x too big means the importer read metres.
- `axis_forward='-Z', axis_up='Y'` maps Blender (x, y, z) to Roblox (x, z, -y), so you can model in a holes.json-style local frame directly (Blender +Y = Roblox -Z).
- Flat-colour props: make one mesh per colour (`<prop>__<Material>`) so each becomes a MeshPart you can recolour. No UVs needed.
- Cheap textures without UV unwrapping: generate tiling 512px PNGs procedurally (`textures.py`: FFT noise is periodic, and stamped shapes wrap at the edges). Give every mesh a box (cube) projection UV in prop space at a fixed studs-per-repeat (`lglib.box_uv_bmesh`), wire an Image Texture into Principled Base Color, and export with `path_mode='COPY', embed_textures=True`. Re-apply the UVs after booleans. Never texture a material that is also used for non-foliage parts (a torii reusing the leaf-red material came out leaf-patterned), so give those parts their own flat accent material.
- Set dressing around gameplay geometry: generate placements against keep-out volumes built from the collision JSON (felt + margin, walls, hazards, moving-part sweeps sampled through their motion, hero bboxes, walking paths), and test every transformed **vertex**, in world space, against every hole. Things may only overhang the play surface above a fixed clearance. Lay out all holes before the far background ring, or the early holes' backdrop steals space from later holes (`dressing_lib.py`, `dressing.py`).
- Re-validate dressing whenever the world layout changes (`dressing_world.py`). Vertex tests miss thin triangles (rope spans, canopy edges) that cross a keep-out between vertices, so finish with an exact triangle-vs-box (SAT) test. Check world meshes with per-part height-interval maps on a 1-stud grid (`world_occ.py`), and ground props on the terrain grid with a footprint-spread limit (1.5 studs small, 3 trees). Prefer nudging to removing, and log a reason for every removal.
- Quest VR budget: count tris of ALL dressing within ~60 studs of each hole's felt (neighbouring holes share that budget) and cap it at about 34k. Give each hole a share per role (lanterns, trees, ground cover) so the first role processed can't starve the rest. Cap heavy small props (1.5-2k-tri toadstool clusters). Replace far clumps with crossed alpha-cut card quads (12 tris) instead of making LODs, because Roblox auto-LODs MeshParts.
- VR readability (playtest lessons): keep every dressing prop taller than 2 studs at least 3 studs (horizontally) back from every rail, measuring the footprint and all geometry below eye height. Enforce it in the placer, check it independently in fitcheck, and add a negative test. Give all moving obstacles one shared signal colour scheme (red/cream bands) that static props never use. In dark areas (under roots, inside trees), use a brighter felt variant, a light rail cap/trim and PointLights pooling over each moving part and cup. Hang the lights above the play clearance so their host parts stay out of keep-outs.
- When the collision JSON changes (a new design round), diff it against the previous snapshot first, then make every placement and check read the JSON (cup, pivots, rail tops, ranges) instead of copying numbers. Also check the tee-eye -> flag-top sightline against every static hero prop's triangles: a lantern cluster the design assumed was "high" blocked it. Pendulums (`swing`): origin at the hinge, keep-out = the bob + chain swept over +-amplitude.
- Shared near-field budgets are zero-sum between neighbouring holes. To enrich one hole, place a fixed set of cheap low props for it BEFORE the general seed pass; a reserve or a per-neighbour cap starves a single neighbour instead.
  Placing them AFTER the seed pass gets almost nothing (the shared fields are already full). Pay for them with explicit
  trims of low-value items (trees behind the tee, heavy small props), and report what each hole lost.
- Legibility from the VR tee (pass 7): flags need a thick banded pole (0.3), a pennant about 3.2 x 2.0, and a big
  number in a contrasting colour. Firefly specks need a radius of 0.1-0.24 to show at 15-25 studs. Re-check light
  positions whenever a prop grows: a PointLight about 1 stud from the bigger pennant blew it out, so keep spots >= 1.5
  studs from it.
- Moving parts: put the origin at the pivot and record each part's bbox-centre offset in a manifest, so PivotOffset can be fixed if the importer recentres.
- Exact booleans fail on targets that contain overlapping pieces. Keep the solid you cut in its own mesh.
- Headless Cycles CPU at 24 samples + denoise renders 512px previews in about 1-2 s. EEVEE works headless but is about 20x slower.
- Rail/edge lanterns: check the lantern is visible over the rail (lantern top above the rail top), not just clear of it. Use a crook post (lantern above the eye band, post >= 3 back) where walls are tall or the ground drops. Where water or walkways block the spacing, record every skipped spot so the fit check can re-test them.
- holes.json can change under you (a design agent runs in parallel). Validate against a snapshot (`LG_HOLES_JSON=tools/out/holes-*.json`), also run against the live file, and report the drift separately.

## Getting it into Roblox
1. **Studio 3D Importer** (File > Import 3D): a UI dialog, so it needs computer use. Check the scale, the preview and any warnings, then insert. The result is a `Model` with `MeshPart`s, saved as assets on the account.
   - **Many small FBX?** Merge them in Blender into one FBX first (one top-level Empty per source file, the same export settings), so it's a single importer pass instead of one computer-use run per file. Example: `assets/vr-mini-golf/sugarloaf-canyon/models/_src/movers/merge_for_import.py` (35 files -> 1, with a bbox round-trip check).
   - **Check sizes after import.** As seen in stage w, the importer can auto-scale the *whole scene* so its widest object lands on 2048 (warning "One of the objects dimensions are larger than can be imported"; a 92-stud piece made everything x22.26), and it also turned the scene 180 deg about Y. Compare MeshPart sizes with the export's bboxes and undo it in Luau: `Size /= k; CFrame = CFrame.Angles(0, math.pi, 0) * CFrame.new(pos / k) * rotation`.
   - Generalized merge script: `games/vr-mini-golf/tools/merge_fbx_for_import.py` (`Blender -b --factory-startup --python merge_fbx_for_import.py -- out.fbx in1.fbx in2.fbx ...`; writes `<out>_merge_report.json`). Stage ab merged 213 kit FBX into 3 files (a few hundred meshes each, 6-10 MB) and 31 lobby FBX into 1; each imported in one Codex run.
   - Stage ab saw the auto-scale on every merged file (x2.9, x16, x3.3, x74; the 180-degree turn too, baked into the mesh data with the part rotation left at 0). The robust fix: set each MeshPart's Size and centre straight from the manifest (`SugarloafBuilder.PrepareKit`), only taking the turn out of the rotation. A single-mesh prop can't show its turn by centre fitting, so give it the common turn.
   - Untextured materials can come in near-white: re-apply colours/materials from your manifest by the `<piece>__<Material>` mesh names.
2. **Open Cloud Assets API** (`POST https://apis.roblox.com/assets/v1/assets`, type Model, with `.fbx`): needs an API key with asset write permission. **None is configured yet**, so ask Chase before setting one up. Afterwards, use `insert_asset` via the Studio MCP with the returned asset ID.
3. After inserting: anchor and position with `execute_luau`, set `CollisionFidelity` (Box or Hull for performance), and check in a playtest.
