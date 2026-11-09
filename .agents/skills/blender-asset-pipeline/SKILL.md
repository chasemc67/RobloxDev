---
name: blender-asset-pipeline
description: Make Roblox-ready 3D assets (meshes, PBR textures) in Blender on the Windows PC with headless Blender Python scripts, keep the saved .blend in Git LFS as the source of truth, export FBX with the right scale, axes and triangle budget, validate on the Blender side, and hand off to the builder. Covers manifests, orientation checks and LFS verification. Use when a game needs custom meshes, props, buildings or textures beyond Studio parts, or when you revise, export or hand off a Blender asset.
---

# Blender asset pipeline (Blender to Roblox)

## Where Blender runs
- **All Blender modeling, rendering and export runs on the Windows PC (`ssh pc`)**, not on the Mac Mini or a cloud box. If the PC can't be reached, coordinate recovery with Chase or the other bots. Don't fall back to another machine.
- Write Blender scripts with **Claude Code on Opus 5.5** (Chase's current choice).
- The PC is shared. Run **one Blender job at a time** (check that no other `blender.exe` is running). Never close or touch another bot's Studio session. Don't render a flythrough unless someone asks for one.
- Run long jobs as **detached scheduled tasks** so an ssh disconnect doesn't kill them. Write stdout/stderr and the exit code to local log files and poll them. `assets/mini-golf-v2/pirate-shipwreck/models/start_ship_whimsy_v5_1/src/run_blender.ps1` is an existing example. Copy the pattern, not its hard-coded paths.
- Keep secrets, tokens and machine-specific auth setup out of scripts, manifests and this repo.
- **No Blender MCP is set up.** Use headless scripts. Before generating a mesh in Blender, check whether the Studio MCP's `generate_mesh`, `generate_procedural_model` or `insert_asset` is faster for the job.

## Roles
- Game Art owns approved concepts and silhouette references. Model to them. Don't invent art direction.
- RobloxDevBot owns Studio integration and publishing. Playtest owns in-engine gameplay validation. **Blender fitchecks are not Studio or physics acceptance.**
- Keep decorative mesh changes separate from authored playable geometry and collision. Never change hole geometry, collision or difficulty silently. Flag the change to the owner instead.
- For course blockouts, the authoritative approved `holes.json` is the geometry input: snapshot it and record the version you used. Generic lobby props don't need one.

## Source of truth and repo layout
- Pull before you start, and serialize source commits with any other bot working in the same folder. Never reset, stash or overwrite someone else's uncommitted files.
- The **saved `.blend` is the source of truth** (Git LFS, see `.gitattributes`). Give objects clear names and group them in collections (for example `Visual`, `Collision`, `Movers`). Pack textures, or reference them with paths that resolve inside the repo.
- **FBX is derived output** and gitignored. Regenerate it from the saved `.blend`. Never hand-edit an export. The `src/` scripts plus the saved `.blend` must reproduce every export.
- Leave a revision you are replacing untouched. Make a new versioned folder and record the base file's commit and sha256 in the manifest.
- Typical folder (what may be committed follows `AGENTS.md` and `.gitignore`):
```text
assets/<game>/<area>/models/<asset>_v<N>/
  <asset>_v<N>.blend   manifest.json   README.md
  src/*.py             # generator / edit / export / validate scripts
  textures/*.png       # final textures
  final/*.png          # optional: a few chosen final previews
```
- Generate local diagnostics (fitcheck dumps, logs, previews), but don't commit them. Summarize the results in the manifest or README.
- `assets/_examples/make_crate.py` is a minimal generator template (builds a beveled crate and exports FBX). It still exports with the older `axis_forward='Z'`, so switch it to the repo convention below and run the marker check.

## Roblox requirements (from create.roblox.com docs, checked Oct 2026; re-check if anything looks off)
- **Formats**: `.fbx` (preferred: hierarchy, PBR textures, rigs, animation, vertex colors), `.gltf`, `.obj` (simple single meshes only).
- **Budget**: each mesh is **at most 20,000 triangles**. Studio auto-simplifies anything above that. Avatar items have tighter budgets.
- Geometry should be watertight, have no zero-thickness faces, and use quads or tris (no n-gons).
- **Scale**: set Blender Scene > Units > Unit System = **None**, so 1 Blender unit = 1 stud. When exporting FBX, set **Apply Scalings = FBX Unit Scale** and leave all other scales at 1.0. (The alternative is export Transform > Scale = 0.01 if you modeled in meters.) A Roblox character is about 5 studs tall. Check the size in Studio after importing.
- **Axes**: the repo's export scripts use `axis_forward='-Z', axis_up='Y'` (Blender Z-up, see the Lantern Grove note below). Don't rely on axis shorthand from memory. Record the exact exporter settings in the manifest, and **check the orientation with an asymmetric marker**: something that can't be mistaken when mirrored or rotated, such as an arrow pointing at the asset's front. Re-import the FBX, or have the builder import it, confirm that front, up and handedness match, and record the result.
- Moving pieces (doors, hinges, windmills, pendulums) are separate objects with their origin at the hinge or pivot. Record their axis, range and clearances.
- Far scenery gets one pass, with no fine polish. Don't carry over fixed clearance numbers from old course examples: derive them from the current approved geometry and record where each came from.
- **Before export**: apply all transforms (`bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)`), and put the origin where the object should pivot or sit (usually bottom-center for props).
- **FBX options**: Path Mode = Copy, Embed Textures on, Add Leaf Bones off, Bake Animation off unless the asset is animated.
- **Textures and PBR**: use the Principled BSDF with Base Color, Normal, Roughness and Metallic image textures. On import, Studio builds a `SurfaceAppearance` from them. Use PNG, power-of-two sizes, at most 1024×1024. Fewer, shared materials is better.

## Script snippet (export)
```python
import bpy
bpy.context.scene.unit_settings.system = 'NONE'
bpy.ops.export_scene.fbx(
    filepath=out, use_selection=False, apply_scale_options='FBX_SCALE_UNITS',
    axis_forward='-Z', axis_up='Y', path_mode='COPY', embed_textures=True,
    add_leaf_bones=False, bake_anim=False, mesh_smooth_type='FACE')
```
Count triangles before exporting:
`sum(len(p.vertices)-2 for o in bpy.data.objects if o.type=='MESH' for p in o.data.polygons)`

## Validation, manifest and handoff
- Run automated checks against the saved `.blend` and its exports on the PC: triangles per mesh (20k limit) and in total, bbox and scale against the approved reference or `holes.json`, textures resolve and UVs exist, unchanged objects really are unchanged in a revision, mover pivots and sweeps, and the orientation marker.
- Render previews at **eye level** (player or VR eye height) plus **one useful overview**, and compare them with the approved art.
- `manifest.json` covers, as they apply: source `.blend` and base revision (commit + sha256), Blender version, export and texture paths, units/scale and the exact export settings plus the orientation check result, and per mesh the triangles, materials/textures, pivot, bbox and collection. Add mover hinges/ranges/clearances, placements, **collision provenance** (where it was authored, exported or not, verified against what), changes against the base, and unresolved caveats.
- **Verify LFS on the remote, not just locally.** `git check-attr filter -- <file>.blend` must print `filter: lfs`. After pushing, `git show origin/<branch>:<file>.blend` must be an LFS pointer. Then retrieve the file from the remote and compare hashes:
```bash
tmp=$(mktemp -d)
GIT_LFS_SKIP_SMUDGE=1 git clone -q --depth 1 --branch <branch> <remote-url> "$tmp/c"
cd "$tmp/c" && git lfs pull --include="<file>.blend" && sha256sum "<file>.blend"   # must equal the pointer oid and the PC's saved file
```
- **Handoff to RobloxDevBot** (cc Game Art for art review) covers:
  - the source branch and commit, the `.blend` path and its LFS sha256, with how you verified it
  - the export, texture and manifest paths, and how to regenerate the FBX
  - coordinates, pivots, scale, the front direction and the orientation result
  - what changed and what didn't
  - what was validated in Blender, what still needs Studio or Playtest acceptance, and the caveats
  - the eye-level and overview previews next to the approved art

## Lessons from Lantern Grove (V1 course history: its numbers are not defaults for new courses; assets/vr-minigolf/lantern-grove/models/_src)
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
