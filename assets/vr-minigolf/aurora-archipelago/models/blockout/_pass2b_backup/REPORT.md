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


---

# Pass 2: art notes 1-5

Completed 2026-10-12T00:31:33. Outputs are in `out_p2/` and keep pass 1's layout: `models/blockout/` holds the FBXs, `manifest.json` (same schema plus `"pass": 2`), `fbx_validation.json`, `build_stats_p2.json` and `aurora_blockout.blend`. Renders are in `previews/pass2/`. Pipeline: `prepare_p2.py` → `make_build_p2.py` generates `build_blockout_p2.py` from pass 1's `build_blockout.py` plus `p2_head.py`, `p2_cloud.py` and `p2_render.py`. Then `verify_exports_p2.py` and `finalize_p2.py`.

Unchanged hard rules: 1 unit = 1 stud; Roblox (x,y,z) = Blender (x,-z,y); FBX forward -Z, up Y, scale 1.0. FBXs carry world positions. Every pass 1 file name still exists with the same chunk pivots. One material per mesh is checked on reimport.

## Changes per note

1. **Floating islands.** The cloud deck moved from y 34-36 to a soft, lumpy cloud sea with mean surface y -30: a polar sheet plus 250 clustered low-poly puff domes, kept low under the islands. Its `CloudSea` material is a noise-driven gradient from #C9B8F0 to #8FD9D2 with matching emission (0.55), sheen and bump. Two lilac/teal area lights facing up from the cloud light the undersides from below; they are hidden from the camera. In renders the cloud receives island shadows but does not shadow itself. Every island (22) now has a short jagged cliff of 8-18 studs below a snow lip, flowing into a tapered, jagged, upside-down cone (`undersides_XX_YY.fbx`, one per terrain chunk, same pivots). Cone depth is about 2.4 × the island's inner radius, and no tip goes below y 12. That leaves an air gap of about 40 studs above the cloud sea, visible under the islands and islets in hero_01. `roots.fbx` now holds 89 glowing #9FE6F2 crystal drips hanging from the undersides, plus jagged rock stalactites under the 25 documented `island_underside` anchors. Waterfalls continue down into the lowered cloud.
2. **Wider islands.** The heightmap already gave at least 18 studs of land around every footprint except the two open-sky span gaps (H3 Glimmer Gap, H17 Aurora Gap). So all 5 course islands grow outward by a noisy, lobed 8-15 studs. Stats: rim falloff squared on 2354 edge cells (mean raise 36.1 studs); 13238 original cells, 3415 void cells within a noisy 8-15 stud outward growth of the 5 course islands (islands keep >=14-stud gaps), 195 excluded (spans/bridges/waterfalls/lifts/paths), 3217 padded cells added (3 disconnected scraps dropped); all padded heights <= nearby felt/rail bottoms. The gaps between islands stay at 14 studs or more, and land is never added under the span gaps, bridges, gondola, lift shafts, waterfalls or teleports, or over a path. Padded land is set at or below the lowest felt/rail bottom within 18 studs. Measured on the built mesh, the worst padded/rim vertex sits 0.00 studs above it (the felt top is +0.28). The heightmap's sloping 6-stud rim falloff was squared up into crisp cliff lips. Boundary corners are chamfered and jittered, so edges read as uneven cliffs rather than 4-stud stairs.
3. **Cooler rock.** `Rock` (cliffs, undersides, stalactites) is now #6E7FA6 and `Slate` #5F6E94. `Snow` is #EEF4FF with slight sheen. Every flat Rock/Slate/Basalt top cell (corner spread ≤ 1.6 studs) is snow-capped, and every cliff edge has a 1.3-stud snow lip that overhangs by 0.9 studs. Rail caps and pine snow get the new colour only.
4. **Glow.** New `CrystalGlow` material (#9FE6F2, emission 2.2) on the crystal clusters, the spire's ice crystals, the underside drips, new glowing strips along both edges of every walk/bridge/stair/landing segment, and new glowing rings lying on the felt around all 18 cups. `Glow` lanterns are now #FFB060 at emission 0.7, and the lantern point lights are #FFB060 at 30 W (was 55 W), so they read warmer and dimmer than the crystals. Bloom is a compositor Glare node, type Bloom, quality High, threshold 0.9, strength 0.7, size 0.6.
5. **Felt.** `Felt` is #3FA58A with roughness 0.45, sheen 0.35 (tint #DFF7F2) and coat 0.12. Recolour only: `verify_exports_p2.py` compares world-space vertices of the felt, ice-felt, rail and rail-cap meshes in pass 2's `holes.fbx` with pass 1's, and they are identical.

Placeholder props (pines, palms, huts, snowpuffs, coral, lift cages, spire, arch, far islands, sky) are unchanged in geometry. Only the shared material colours above changed.

## Triangles

92 FBX files (48 pass 1 names kept, 44 new), 225 meshes, **178,128 triangles** (pass 1: 83,888). Terrain 55,774; undersides 32,910; cloud sea 28,296; roots 5,640; holes 14,256; connections 6,100; props 30,960.
Largest FBX: `props_00.fbx` with 19,552 triangles. Largest mesh: `cloudsea__CloudSea` in `cloudsea_00.fbx` with 18,000. Every mesh and every FBX is under 20,000. All files were reimported: triangle counts match, bboxes are within 0.05 studs, one material per mesh, and felt/rail identity holds.

New files: `cloudsea_00.fbx`, `cloudsea_01.fbx`, `terrain_05_07.fbx`, `undersides_00_00.fbx`, `undersides_00_01.fbx`, `undersides_00_02.fbx`, `undersides_00_03.fbx`, `undersides_00_04.fbx`, `undersides_00_05.fbx`, `undersides_01_02.fbx`, `undersides_01_04.fbx`, `undersides_01_05.fbx`, `undersides_01_06.fbx`, `undersides_02_00.fbx`, `undersides_02_01.fbx`, `undersides_02_02.fbx`, `undersides_02_06.fbx`, `undersides_02_07.fbx`, `undersides_03_01.fbx`, `undersides_03_02.fbx`, `undersides_03_03.fbx`, `undersides_03_04.fbx`, `undersides_03_06.fbx`, `undersides_03_07.fbx`, `undersides_04_01.fbx`, `undersides_04_02.fbx`, `undersides_04_03.fbx`, `undersides_04_04.fbx`, `undersides_04_06.fbx`, `undersides_05_02.fbx`, `undersides_05_03.fbx`, `undersides_05_04.fbx`, `undersides_05_05.fbx`, `undersides_05_06.fbx`, `undersides_05_07.fbx`, `undersides_06_01.fbx`, `undersides_06_02.fbx`, `undersides_06_03.fbx`, `undersides_06_04.fbx`, `undersides_06_05.fbx`, `undersides_06_06.fbx`, `undersides_07_03.fbx`, `undersides_07_04.fbx`, `undersides_07_05.fbx`.

## Renders (`previews/pass2/`)

The six cameras are exactly pass 1's (`out/previews/blockout/render_settings.json`, checked equal). File names are unchanged. Cycles OPTIX, 64 samples, denoised, 1920×1080, AgX, compositor bloom. `contact_sheet.jpg` is a labelled 6-up and `render_settings.json` records the cameras and bloom. Low-resolution iteration renders are in `qa_p2/`.

| Render | Mean brightness | Spread | Check |
|---|---:|---:|---|
| hero_01_overview.png | 152.48 | 26.12 | PASS |
| hero_02_spire.png | 87.67 | 60.72 | PASS |
| hero_03_skybridge.png | 109.98 | 59.7 | PASS |
| hero_04_overlook.png | 95.98 | 49.73 | PASS |
| hero_05_h03.png | 82.9 | 41.83 | PASS |
| hero_06_h18.png | 59.65 | 42.99 | PASS |

## Issues and notes

- **Cloud height changed.** world.json documents the cloud deck at y 36, the respawn plane at y 40 and underside tips at y 36. To get the requested gap, the visual cloud sea is now at y -30 and underside tips reach down to y 12. Gameplay respawn (y 40) is not geometry and is unaffected, but players will now see the islands' undersides below the respawn height.
- **Padding is mostly wider than asked.** Islands already had 18 studs or more of land around the felt. The 8-15 stud padding is therefore added outward from the existing rims, so it widens silhouettes rather than closing gaps at the rails. Inside the two span gaps it is deliberately not applied, because those gaps are gameplay.
- **Rim squaring raised cliff-lip cells.** Cells within 2 cells of the void were raised up to the island level (crisp lips). Any such cell within 18 studs of a hole is clamped to the felt/rail floor; the measured excess is 0.00 studs.
- **Ice-surface felt keeps `Ice`.** The one ice-surface felt piece is a distinct gameplay surface, so it keeps `Ice` rather than the new felt colour. Its geometry is unchanged.
- **FBX carries base colours only.** Emission, the cloud gradient, felt sheen/coat, bloom and the uplights must be recreated in Roblox: SurfaceAppearance/Neon, Bloom post-effect, emissive cloud mesh or particles.
- **Still a static visual blockout**, as noted for pass 1. The dark pit beside the overlook (hero_04) is an interior void in the source heightmap and was present in pass 1.


---

# Pass 2b: cloud sea, felt, wood, tee fill

Completed 2026-10-12T00:52:23. Outputs are in `out_p2b/`: `models/blockout/` has the full set (92 FBXs, `manifest.json` with `"pass": "2b"`, `fbx_validation.json`, `build_stats_p2.json`, `aurora_blockout.blend`). Renders are in `previews/pass2b/`, and `previews/pass2b/_masks/` holds the measurement masks plus the hero_01 sky probe. Pipeline: `make_build_p2b.py` patches `build_blockout_p2.py` into `build_blockout_p2b.py`, with asserted string patches and the geometry code untouched. Then `verify_exports_p2b.py`, `measure_p2b.py` and `finalize_p2b.py`. Low-res iterations are in `qa_p2b/`. The pass 2 deliverables were backed up to `out_p2_backup/` before any work.

## Changes

1. **Cloud sea.** `CloudSea` is now a height gradient: dusky lilac #8A86B8 on the cloud tops fading to deep teal #2E4E66 in the hollows. It is driven by world height plus slight noise over a range of about y -33 to 5, and its base colour in the FBX is #8A86B8. Emission dropped from 0.55 to 0.26 everywhere. An extra +0.45 is added only near and under islands, using a per-vertex `island_glow` mask: exponential falloff of 70 studs from the island footprints, stored as a vertex colour on the cloud meshes, so this is exported too. That faint glow keeps the air gap readable. The big lilac sky fill no longer lights the cloud (Cycles light linking), and the two cloud uplights were reduced from 900 kW to 600 kW. Far cloud fades into the sky horizon colour between 1800 and 5200 studs from the camera (aerial perspective, camera rays only).
   Night sky: the camera now sees a horizon glow of #6866A8 rising to a deep-indigo zenith of #10163C (camera strength 1.05). Lighting rays use a dimmer world (0.45), so the brighter sky does not flatten the islands. Exposure is 0.4000000059604645 (pass 2: 0.25).
2. **Felt.** `Felt` is #4FC29E, with sheen (0.35, tint #DFF7F2), coat and roughness kept. Tee fill: a render-only soft area light (disk 14 studs, 4000 W, warm white #FFF4E6) is parented to the camera 2.5 studs up and 3 studs back, aimed along the view. It is invisible to the camera and in reflections, enabled only for hero_05_h03 and hero_06_h18, and not exported. It is saved hidden in the .blend.
3. **Wood.** `Timber` (rails, posts, bridge rails, lift frames, pine trunks, hut posts) is #8A5A3C.

Geometry is unchanged. `verify_exports_p2b.py` reimported all 92 FBXs and found triangle counts and bboxes identical to pass 2 for every file. Felt, ice-felt, rail and rail-cap vertices in `holes.fbx` are identical to pass 1, and the FBX material colours read back as Felt #4FC29E, Timber #8A5A3C, CloudSea #8A86B8. Total: 178,128 triangles, the same as pass 2. Every mesh and every FBX is under 20,000.
Files containing a changed material, all re-exported: Felt → holes.fbx; Timber → connections.fbx, holes.fbx, props_00.fbx; CloudSea → cloudsea_00.fbx, cloudsea_01.fbx. The whole set was rebuilt from the same seeds, so the other files are re-exports with identical geometry and materials.

## Measurements (`render_validation.json`, `region_luminance.json`)

Luminance is Rec.709 luma, 0-255, measured on the final 1920×1080 PNGs. Region masks are flat Workbench renders from the identical cameras.

- **hero_01 overall: 95.25** (pass 2: 152.48; target 90-120). PASS.
- **hero_01 cloud-sea region: 94.77** (83% of the frame).
- **Night sky: 119.9**, which is brighter than the cloud sea. PASS. hero_01's frame has no sky pixels, because its top edge is about 10.6° below the horizon (pitch 28.6° down, vertical FOV 36°). So the sky was measured with a probe render: same position, FOV and yaw, pitched up to the horizon. Sky regions in the other views: hero_02 86.53, hero_03 112.05, hero_04 123.38, hero_05 114.11, hero_06 118.82. The far cloud band at the top of hero_01 fades into this horizon colour.
- **Tee felt:** hero_05 felt region 143.99 and hero_06 130.1. The overall tee-view means rose from 82.9/59.65 to 121.01/120.23.

| Render | Mean (pass 2b) | Mean (pass 2) | Spread | Check |
|---|---:|---:|---:|---|
| hero_01_overview.png | 95.25 | 152.48 | 22.75 | PASS |
| hero_02_spire.png | 108.29 | 87.67 | 51.6 | PASS |
| hero_03_skybridge.png | 125.08 | 109.98 | 44.63 | PASS |
| hero_04_overlook.png | 122.5 | 95.98 | 34.46 | PASS |
| hero_05_h03.png | 121.01 | 82.9 | 33.13 | PASS |
| hero_06_h18.png | 120.23 | 59.65 | 34.91 | PASS |

Renders: Cycles OPTIX, 64 spp, denoised, 1920×1080, AgX, compositor Glare/Bloom (unchanged). The cameras are exactly pass 1/2's, with the same names.

## Notes

- The brighter night sky also raises hero_02-04 slightly, from 87.67, 109.98, 95.98 to 108.29, 125.08, 122.5. That is mostly sky pixels; island lighting is close to pass 2 because the lighting world is dimmer.
- Roblox: recreate the cloud gradient with a vertical gradient texture, or with two cloud layers (lilac tops, teal below). The emission mask is in the `island_glow` vertex colour, and the night-sky gradient goes in the Sky/Atmosphere. The tee fill light is render-only and has no in-game equivalent requirement.
