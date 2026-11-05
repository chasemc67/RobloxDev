# Aurora Archipelago — terrain blockout and hero renders

Completed: 2026-10-11T23:59:56.

48 FBX files, 186 mesh objects, 83,888 total triangles. Largest FBX: 19,552 triangles; largest mesh: 7,212. Every mesh and every FBX is strictly below 20,000 triangles. All FBXs were reimported into a clean headless Blender scene and passed triangle and Roblox-axis bounding-box checks (tolerance 0.05 studs).

## Deliverables

- `models/blockout/aurora_blockout.blend`: full world, materials, Cycles lights and final camera.
- `models/blockout/manifest.json`: files, object triangle counts, materials, Roblox-axis bounds, pivots and placement notes.
- `models/blockout/fbx_validation.json`: per-file reimport validation.
- `previews/blockout/contact_sheet.jpg`: labelled six-view sheet.
- `previews/blockout/render_settings.json` and `render_validation.json`: cameras, device, settings and brightness results.
- Generator and QA scripts are retained at workspace root; `PROGRESS.md` logs the build and correction steps.

## Geometry and placement

1 Blender unit = 1 stud. Roblox `(x,y,z)` maps to Blender `(x,-z,y)`. FBX forward `-Z`, up `Y`, scale 1.0; rotations and scales applied. Terrain is split into an 8×8 grid of 168-stud chunks; empty chunks are omitted. Terrain origins are grid centres at y=30. Other assemblies use the world centre/base as shared origin. Exported objects contain world locations: import at the world origin and do not apply hole offsets a second time.

The 16-bit heightmap is sampled on a 4-stud grid, with shared corner heights and continuous inward-tapered island skirts. Cells below y=30 are omitted entirely. Documented underside pieces rise from their y=36 anchors. Materials-map PNG colors select terrain materials; terrain-4stud.json supplies material indices where the PNG legend obscures the map. Each exported mesh uses one material. All 18 holes have felt slabs, snow-capped rails, tee markers, cup discs and red flags, transformed by authoritative world.json placement. Felt slopes and raised tiers are represented. Paths, bridge rails, lifts, teleports, waterfalls, lagoons, Starfrost Spire, Halo Arch, pines, crystal clusters, palms, snowpuffs, huts and all lantern posts are included as blockout geometry.

The backdrop includes the documented 16-island far ring and 12 distant silhouettes. The noise-shaded, volume-free cloud plane is extended to 10,000 studs for a continuous render horizon. The sky contains five mint/violet aurora curtains, a moon at the documented position and stars. Aurora is visible to camera rays without lighting the scene. Moon direction follows bearing 220°, elevation 14°; warm lantern points and lilac fill support night readability.

## Renders

Cycles OPTIX, 64 samples, denoising, 1920×1080 PNG. V1 and V3 use the source cameras. V4 retains the southeast aerial direction with a wider camera distance to include the whole world. V2 is raised/moved slightly to clear a railing and show the summit. H03 and H18 views are 5.5 studs above their tees. The vista JSON prompts and all four PNGs informed palette and framing; these are low-poly layout renders.

| Render | Mean brightness (0–255) | Brightness spread | Check |
|---|---:|---:|---|
| hero_01_overview.png | 111.319 | 27.507 | PASS |
| hero_02_spire.png | 72.544 | 60.217 | PASS |
| hero_03_skybridge.png | 91.349 | 60.476 | PASS |
| hero_04_overlook.png | 85.339 | 46.881 | PASS |
| hero_05_h03.png | 57.787 | 35.147 | PASS |
| hero_06_h18.png | 57.493 | 42.743 | PASS |

## FBX file list

| File | Mesh objects | Triangles |
|---|---:|---:|
| terrain_02_00.fbx | 2 | 384 |
| terrain_00_00.fbx | 3 | 198 |
| terrain_02_01.fbx | 3 | 364 |
| terrain_03_01.fbx | 6 | 1,222 |
| terrain_04_01.fbx | 6 | 938 |
| terrain_00_01.fbx | 1 | 24 |
| terrain_06_01.fbx | 1 | 12 |
| terrain_00_02.fbx | 3 | 594 |
| terrain_02_02.fbx | 5 | 2,220 |
| terrain_03_02.fbx | 5 | 942 |
| terrain_04_02.fbx | 5 | 2,152 |
| terrain_06_02.fbx | 3 | 790 |
| terrain_01_02.fbx | 1 | 30 |
| terrain_05_02.fbx | 2 | 472 |
| terrain_00_03.fbx | 3 | 270 |
| terrain_07_03.fbx | 3 | 286 |
| terrain_03_03.fbx | 3 | 1,124 |
| terrain_04_03.fbx | 3 | 708 |
| terrain_05_03.fbx | 5 | 1,050 |
| terrain_06_03.fbx | 6 | 1,678 |
| terrain_03_04.fbx | 3 | 100 |
| terrain_04_04.fbx | 2 | 44 |
| terrain_05_04.fbx | 3 | 610 |
| terrain_06_04.fbx | 6 | 1,426 |
| terrain_07_04.fbx | 5 | 778 |
| terrain_00_04.fbx | 2 | 258 |
| terrain_01_04.fbx | 2 | 26 |
| terrain_00_05.fbx | 3 | 658 |
| terrain_01_05.fbx | 3 | 36 |
| terrain_06_05.fbx | 5 | 2,114 |
| terrain_07_05.fbx | 4 | 578 |
| terrain_05_05.fbx | 2 | 734 |
| terrain_05_06.fbx | 8 | 3,040 |
| terrain_06_06.fbx | 7 | 542 |
| terrain_03_06.fbx | 5 | 1,872 |
| terrain_02_06.fbx | 4 | 434 |
| terrain_04_06.fbx | 5 | 942 |
| terrain_01_06.fbx | 2 | 404 |
| terrain_02_07.fbx | 5 | 944 |
| terrain_03_07.fbx | 5 | 1,034 |
| roots.fbx | 1 | 800 |
| holes.fbx | 7 | 11,376 |
| connections.fbx | 8 | 4,516 |
| props_00.fbx | 5 | 19,552 |
| props_01.fbx | 5 | 11,408 |
| spire.fbx | 3 | 792 |
| backdrop.fbx | 3 | 1,804 |
| sky.fbx | 4 | 1,608 |

## Problems and limits

- This is a static visual blockout. Moving obstacles, transport logic, teleport behavior, ball physics, collision groups and playable cups are not implemented. No Roblox Studio session was used.
- The source heightfield defines narrow islands around the actual course pads. Their silhouettes therefore follow the validated layout, which differs from the broader illustrative vista art. The 4-stud sampling approximates small terrain details; hole slabs and paths remain separate exact-size meshes.
- FBX carries geometry and diffuse material assignments. Recreate Neon emission, aurora transparency, night sky, lights and procedural cloud shading in Roblox using the blend and manifest as reference.
- Compositor bloom was omitted because Blender 5.2 removed the older scene compositor API. PNGs use native emissive shading and denoising.
- Corrected during QA: script encoding, compositor compatibility, shared cliff corner samples, mesh normals, underside anchor interpretation, discontinuous skirt taper, aerial framing and overlook railing occlusion. Final brightness and FBX reimport checks passed.
