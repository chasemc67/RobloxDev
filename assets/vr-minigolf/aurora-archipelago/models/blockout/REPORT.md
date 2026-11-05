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

# Pass 2c: felt tweak

Completed 2026-10-12. `out_p2c/` is a copy of `out_p2b/`. The only change is the colour of the `Felt` material, from #4FC29E to **#45B892**. Sheen (0.35, tint #DFF7F2), coat (0.12, roughness 0.25), roughness 0.45 and the render-only tee fill light (4000 W) are kept. Geometry is unchanged. Script: `p2c_blockout.py`. It opens the 2b `.blend` in `out_p2c`, recolours Felt, re-exports only the Felt FBX with 2b's exporter settings, saves `aurora_blockout.blend`, renders and reimport-verifies. Then `measure_p2c.py` builds the measurements and the tee sheet.

- **Re-exported:** `holes.fbx` only, the one file that uses Felt. The other 91 FBXs are the 2b files, copied unchanged. `manifest.json` has `"pass": "2c"`, and its notes now say Felt #45B892.
- **Verification** (`fbx_validation.json`, all passed): all 92 FBXs were reimported. Triangle counts and bboxes are identical to 2b (178,128 tris in total). In `holes.fbx`, every material's world-space vertex set is identical to 2b, and the Felt / ice-felt / Timber rail / Snow rail-cap sets are also identical to pass 1. The FBX colours read back as Felt #45B892, Timber #8A5A3C and CloudSea #8A86B8.
- **Renders** (`previews/pass2c/`): only hero_05_h03 and hero_06_h18 were rendered, from the saved 2b scene with 2b's cameras. Settings are the same as 2b and were asserted against 2b's `render_settings.json`: Cycles OptiX, 64 spp, denoised, 1920×1080, AgX, exposure 0.4, Glare/Bloom. `tee_sheet.jpg` puts 2b (left) beside 2c (right). `felt_measurement.json` has the numbers, and `_masks/` has the felt/snow masks.

| View | Felt luma 2b → 2c | Felt mean RGB 2c | Surrounding snow | Felt − snow 2b → 2c | Weber 2b → 2c | Frame mean 2b → 2c |
|---|---:|---|---:|---:|---:|---:|
| hero_05_h03 | 143.99 → **140.09** | #6E958B | 148.3 | −4.6 → **−8.3** | −0.031 → −0.056 | 121.61 → 120.59 |
| hero_06_h18 | 130.10 → **125.21** | #5A8878 | 189.7 | −59.7 → **−64.4** | −0.314 → −0.340 | 119.97 → 119.08 |

Luma is Rec.709 on a 0-255 scale. "Surrounding snow" means `*__Snow` pixels (terrain snow and the snow caps on the rails) within 61 px of the felt. The felt is about 4-5 luma darker and slightly deeper green. Felt-to-snow separation went up by about 4-5 luma in both views. In hero_05 the felt sits almost level with the shaded snow, so the stronger separation matters most there.

- **P1 props (`out_props/`):** two props files use Felt: `fbx/aa_h03_ice_plank.fbx` (the felt strip on top) and `fbx/aa_h03_dressing.fbx`, which merges that plank into H3. Both were re-exported with the unchanged `_src/build_all.py`, patched at run time to write only those two files (`p2c_props.py`). Before that, `aalib.MATS['Felt']` was set to #45B892, and `textures/felt.png` was regenerated with the same noise seeds and the ramp shifted by −10/−10/−12. Its mean went from #4FC09D to #45B691, and it is embedded in both FBXs. Both were reimported: triangle counts, bboxes and vertices are identical to the pre-2c files, and Felt reads back as #45B892. `manifest.json` (Felt colour, parts and a `pass_2c` note), `fbx_validation.json`, README, the summary, and `aurora_props_p1*.blend` (Felt materials and the felt image) were updated. The pre-2c originals are in `props_work/pre_2c_backup/`. The props preview PNGs and tee views (`previews/aa_h03_ice_plank_*`, `tee_h03`) still show the old felt. No other prop or dressing file uses Felt.


# Pass 2d: felt tweak + blocking-mover felt gap

Completed 2026-10-12. `out_p2d/` is a copy of `out_p2c/`, and `out_props/` was backed up to `out_props_bak_2d/` before any change. Scripts: `p2d_blockout.py`, `measure_p2d.py` and `p2d_props.py`, plus the edited `out_props/_src` pipeline.

- **Felt #45B892 → #3EA886.** Sheen (0.35, tint #DFF7F2), coat (0.12, roughness 0.25), roughness 0.45 and the 4000 W tee fill light are kept. Geometry is unchanged. Only `holes.fbx` uses Felt, so it was the only file re-exported, with the same exporter settings. The other 91 FBXs are byte-identical to 2c. `manifest.json` has `"pass": "2d"`, and its notes now say Felt #3EA886.
- **Verification** (`fbx_validation.json`, all passed): all 92 FBXs were reimported (178,128 tris). Triangle counts and bboxes are identical to 2c. In `holes.fbx`, every material's world-space vertex set is identical to 2c, and the Felt / ice-felt / rail / rail-cap sets are also identical to pass 1. The FBX colours read back as Felt #3EA886, Timber #8A5A3C and CloudSea #8A86B8.
- **Renders** (`previews/pass2d/`): only hero_05_h03 and hero_06_h18 were rendered. Cameras and settings were asserted equal to 2b/2c: Cycles OptiX, 64 spp, denoised, 1920×1080, AgX, exposure 0.4, Glare/Bloom, tee fill. `tee_sheet.jpg` puts 2c (left) beside 2d (right). `felt_measurement.json` uses the same method as 2c: Rec.709 luma, with felt/snow masks from Workbench flat renders and a 61 px snow ring. The 2d masks are pixel-identical to 2c's.

| View | Felt luma 2c → 2d | Felt mean RGB 2d | Surrounding snow | Felt − snow 2c → 2d | Weber 2c → 2d | Frame mean 2c → 2d |
|---|---:|---|---:|---:|---:|---:|
| hero_05_h03 | 140.09 → **134.57** | #6A8F86 | 148.0 | -8.2 → **-13.4** | -0.056 → **-0.091** | 120.59 → 119.17 |
| hero_06_h18 | 125.21 → **118.32** | #558172 | 189.5 | -64.4 → **-71.2** | -0.340 → **-0.376** | 119.08 → 117.84 |

The felt is about 5.5-7 luma darker than in 2c. Felt-to-snow separation went up by a further 5-7 luma. In hero_05, the felt now sits clearly below the shaded snow (Weber −0.09).

- **P1 props (`out_props/`), Felt:** the only Felt users are still `fbx/aa_h03_ice_plank.fbx` and `fbx/aa_h03_dressing.fbx`. Both were re-exported with `aalib.MATS['Felt']` = #3EA886 and a regenerated `textures/felt.png` (same seeds, ramp shifted −7/−16/−12; mean #45B691 → #3EA685; the other textures are byte-identical). Both were reimported: vertices and triangles are identical to pre-2d, and Felt reads back as #3EA886. The Felt materials and felt image in `aurora_props_p1*.blend` were updated too.
- **P1 props, blocking movers H12 / H14:** only the visual meshes changed, giving a **0.0625** felt gap over the full motion range (target 0.06-0.065, not the 0.15 static clearance). Pivots, axes and hinges are the holes.json values.
  - `aa_h12_paddle_wheel`: the red tip arc went from r 4.1 to r 4.0575 (hub y 4.12). The fine sweep (0.05°, full 360°) gives a visual minimum of **0.0625**. It is reached whenever a tip-arc vertex points straight down, e.g. 0°, 8.5° and every 90°. The pass 2c value was 0.020.
  - `aa_h14_icicle_bell`: the skid plate is now a rocker skid. Its bottom is flat 0.075 over the felt at rest for |x| ≤ 0.507, and its ends follow an arc of r 10.2875 about the hinge. The fine sweep (0.01°, ±9°) gives a visual minimum of **0.0625**, across ±2.3–6.4° (first at -4.04°). The pass 2c value was 0.0215. Tris went from 542 to 582.
  - **The collider gap is unchanged.** The holes.json blockers themselves come to **0.02** (H12 strip corners r 4.10, at +5.6°) and **0.0215** (H14 collider-foot corner, at -5.83°). Both are still reported as fitcheck FLAGs for the build bot.
  - Both movers were rebuilt with `build_all.py --only`, which also re-rendered their previews. Neither is merged into a per-hole dressing file. The reimport check passed: tris and bbox match the manifest, the untouched material meshes are identical to pre-2d, and an exact sweep of the exported vertices gives 0.0625 for both.
  - The full fitcheck is still **ALL PASS** (209 PASS, 0 FAIL, 6 FLAG; it was 207 before the 2 new fine-sweep checks). A line-by-line diff shows no other clearance changed: H12 walls 0.05, statics 0.25; H14 walls 1.138, statics 0.345. Only the H13-H15 near-field tris rose, by 40.
  - `manifest.json` (Felt colour, the two mover entries, a `pass_2d` note), `fbx_validation.json` (129/129), `props_p1_summary.md` (Pass 2d note and a visual-vs-collider table), README, the contact sheets and both `.blend`s (mover meshes swapped) were updated.
  - The props tee views (`previews/tee_hNN.png`) and the H3 plank previews were not re-rendered, so they still show the 2b/2c felt.


# Pass 2e: course surround tint + felt banks

Completed 2026-10-12. `out_p2e/` is a copy of `out_p2d/`, and `out_props/` was backed up to `out_props_bak_2e/` before any change. Scripts: `p2e_blockout.py` (stages `build` / `test` / `final`) and `measure_p2e.py`, plus `out_props/_src/fitcheck_decor.py` (new) hooked into `fitcheck.py`. Felt stays **#3EA886**. No existing FBX was re-exported: the 92 pass-2d FBXs are byte-identical, and four new decoration FBXs were added.

## 1. SnowCourse surround (#C9D6E0): `course_apron_00.fbx`, `_01`, `_02`

- **What it is.** A separate decoration mesh draped **0.05** above the terrain, in a **5-7 stud band** outside every hole's felt + rail/wall footprint (holes.json rectangles, world.json placement; the band edge is noise-modulated so it isn't a ruled offset). It covers all 18 holes. Terrain FBXs are unchanged.
- **Material.** `SnowCourse`: a copy of `Snow` (roughness 0.55, sheen 0.25) with base colour #C9D6E0. One material per mesh.
- **What it covers.** The ground bordering the course is mostly terrain **Salt** (#C9C3EC, flush with the felt base), with Snow further out. The apron covers both. It skips Rock, cliffs/lips (normal z < 0.6, or > 1 stud rise inside a cell), paths, bridges, water and the H3/H17 gaps.
- **How it is built.** A 1-stud lattice aligned to the 4-stud terrain grid. Each vertex is a terrain raycast hit, and each quad is split along the terrain cell diagonal, so it conforms exactly. The 26 triangles that didn't hug the terrain (jittered island rims) were dropped. Centroid gap to the terrain is 0.029-0.075 (`build_stats_p2e.json`).
- **Under the course.** Where a lattice quad runs under felt it stays at or below felt top − 0.1, i.e. hidden inside the slab, so there is no seam at open felt edges.
- **Files.** Holes 1-6 / 7-12 / 13-18 → 13,793 / 15,173 / 13,042 tris, one mesh each. Decoration only: CanCollide/CanQuery/CanTouch false, CastShadow false.

## 2. Felt banks (FeltBank #308369 = #3EA886 × 0.78): `felt_banks.fbx`

- **Colour.** #3EA886 × 0.78 rounds to **#308369**; the brief's ≈#308368 is the truncated value. `FeltBank` is a copy of `Felt` with the same sheen, coat and roughness.
- **Shape.** A visual-only bank along every exposed felt edge, always **outside the felt rectangle**. It starts at felt top − 0.02 and drops up to **0.3** to the ground, with its foot 0.03 under the apron (drop quantised to 0.02). It is 0.6 wide. A skirt runs down to felt base − 0.48.
  - **Open edges:** the bank starts at the felt edge.
  - **Railed edges:** it starts at the rail/wall outer face (tucked 0.02 in) and passes under the rail.
  - **Convex corners:** the strip is extended past the corner (mitred).
  - **Diagonal walls:** the start offset varies linearly, giving one strip per wall rather than a staircase.
- **Where there is no bank:**
  - edges shared with other felt (junctions, tiers);
  - edges over ground more than 0.15 below the felt base (cliffs, gaps, and raised greens such as H18's +0.8 green);
  - places where the ground almost reaches the felt top;
  - ice felt, overlay (playable banked) felt and H11's edge-support pocket floor.
- **Size.** 314 strips, 2,512 tris, one mesh. CanCollide/CanQuery/CanTouch false. Rail and felt geometry are untouched.

## Verification

- **Blockout FBX reimport** (`fbx_validation.json`, all passed). All 96 FBXs were reimported (**222,648 tris**; 178,128 + 44,520 new).
  - Every mesh and every FBX is < 20k, with one material per mesh, and bboxes are within 0.05.
  - The 92 pass-2d files are byte-identical.
  - In `holes.fbx`, every material's world-space vertex set (Felt, Ice, Timber rails, Snow rail caps, …) is identical to 2d.
  - Colours read back as Felt #3EA886, Snow #EEF4FF, Timber #8A5A3C, SnowCourse #C9D6E0 and FeltBank #308369.
  - `manifest.json` has `"pass": "2e"`, and the four new files are flagged `decoration`, `can_collide: false`.
- **Fitcheck** (`out_props/fitcheck_p1props_validated.txt`): **ALL PASS, 343 PASS, 0 FAIL, 6 FLAG.** The 209 prop lines are identical to pass 2d, and so are the 6 FLAGs (holes.json geometry). The 134 new decoration checks were run per hole in the hole-local frame on 1.38 M bank and 0.45 M apron sample points:
  - **Banks:** never inside a felt rectangle, never above the felt top they border (max −0.02 on every hole), and inside a rail/wall box wherever they are under one. Cup distance ≥ r + 0.5 (min 1.49, H2). None in the tee-lane felt. Clear of every mover's swept blocker volume. In the H3/H17 gap volumes only below the felt plane.
  - **Apron:** over felt only hidden inside the slab, within 8.5 studs of the footprint (max 8.14), and hugging the terrain. Clear of cups, tee lanes, movers and gaps.
- **Props.** No prop FBX changed. 129/129 were reimported again, with results identical to 2d.

## Renders (`previews/pass2e/`)

Only hero_05_h03 and hero_06_h18 were rendered, with cameras and settings asserted equal to 2d: Cycles OptiX, 64 spp, denoised, 1920×1080, AgX, exposure 0.4, Glare/Bloom, 4000 W tee fill. `tee_sheet.jpg` puts 2d (left) beside 2e (right). `felt_measurement.json` uses the same method as 2c/2d; `*__SnowCourse` counts as snow because the mask rule is "`__Snow` in the name".

| View | Felt luma | Ring snow 2d → 2e | Felt − snow 2d → 2e | Weber 2d → 2e | Apron share of ring | Felt − apron region (all apron px) 2d → 2e |
|---|---:|---:|---:|---:|---:|---:|
| hero_05_h03 | 134.57 | 147.98 → 146.62 | **−13.41 → −12.06** | −0.091 → −0.082 | 13.4 % (luma 128.0) | −0.8 → −3.1 |
| hero_06_h18 | 118.32 | 189.51 → 189.56 | **−71.19 → −71.25** | −0.376 → −0.376 | 0 % | +2.3 → −8.4 |

**The ~25 luma target on hero_05 was not reached.** About 87 % of the 61 px ring is rail caps and terrain Snow (#EEF4FF), which this pass doesn't touch. Inside the ring, the apron replaced bright Snow, so the measured gap shrank slightly (−13.41 → −12.06).

Low-res tests (960×540, 32 spp) varied the tint brightness: #BBC8D3 / **#C9D6E0** / #D7E2EA / #E4EDF4 gave −10.1 / −10.6 / −11.0 / −11.3. That is about 0.4 luma per step, so no value near #C9D6E0 gets close to 25. **Final hex: #C9D6E0, as requested.**

Across the whole frame, the apron area (mostly former Salt) got brighter (135.4 → 137.6 on hero_05, 116.1 → 126.8 on hero_06), so the felt reads darker against its surround: −3.1 / −8.4. From the tee eye height the banks are mostly hidden behind the rails (0.02 % / 0.2 % of the frame); they show at open edges and from higher views.

## Notes

- The apron is a mesh layer 0.05 over the blockout terrain mesh. If the island ground becomes Roblox voxel Terrain, re-drape it (or raise the offset) against the final surface.
- The bank and apron rules depend on the terrain and holes.json; re-run `p2e_blockout.py -- build` after any terrain or hole change.
- `p2e_tmp/` holds the low-res tests and QA close-ups. It is a workspace folder and is not part of the deliverable.

# Pass 2g: rail caps + H3 apron #EEF3F7, conditional felt #36997A

Started from pass 2e: `out_p2e` was copied to `out_p2g`. Pass 2f is a separate, unmodified branch (`out_p2f`), and none of its outputs are used here. Pipeline: `_src/p2g_blockout.py` (adapted from p2f_blockout.py), `_src/measure_p2g.py`, `_src/p2g_fitcheck_runner.py`, `_src/p2g_props.py`.

**Stage 1 (colours).** The rail snow caps on all 18 holes (holes.fbx `holes__Snow` renamed to `holes__SnowRailCap`, 3,744 tris) now use their own material, SnowRailCap #EEF3F7. The H3 apron band (the course_apron_00 quads owned by H3 under the 2e nearest-footprint rule, the same split as 2f, 2,490 tris) is now `course_apron_00__SnowCourseH3`, material SnowCourseH3 #EEF3F7. Both materials are copies of Snow / SnowCourse with only the base colour changed. Terrain Snow (#EEF4FF) and the rest of SnowCourse (#C9D6E0) are unchanged. Felt stayed #3EA886 for this stage, and lighting was not changed.

**Stage 2 (felt, conditional).** After stage 1 the hero_05 gap was -13.01, a magnitude below 20, so Felt changed from #3EA886 to #36997A on all 18 holes (`holes__Felt` is the only user of the Felt material). This is a base colour change only. FeltBank #308369 is a separate material and was not changed. The same Felt colour was applied to the props that use felt, `aa_h03_ice_plank.fbx` and `aa_h03_dressing.fbx` in out_props. Their `textures/felt.png` was regenerated with the same seeds and the ramp shifted by -8,-15,-12 (mean #369779). Both FBXs passed the reimport check: tris and world vertices identical to before 2g, Felt colour #36997A, and the embedded texture updated. The props .blends were recoloured, and the manifest was updated (Felt colour + `pass_2g`). Backup: `out_props_bak_p2g`.

Measurement method is the same as 2c-2f: Rec.709 0-255 luma of the final PNGs, with surrounding snow taken from a 61 px max-filter felt neighbourhood (snow-class pixels only). Gap = felt - snow; a negative value means the felt is darker.

| View | 2e | 2f (ref.) | 2g stage 1: caps + H3 apron #EEF3F7 | 2g final: + Felt #36997A | Final felt | Final snow |
|---|---:|---:|---:|---:|---:|---:|
| hero_05_h03 | -12.06 | -4.74 | -13.01 | **-18.01** | 129.24 | 147.25 |
| hero_06_h18 | -71.25 | -61.01 | -70.40 | **-76.91** | 111.63 | 188.54 |

After both requested stages, the hero_05 gap magnitude (18.01) is still slightly below 20. No further changes were made beyond the brief. Stage renders and masks are in `previews/pass2g/colours` and `previews/pass2g/felt`. `previews/pass2g/` holds the final hero_05/06, `tee_sheet.jpg` (2e vs 2g, labelled with luma), `felt_measurement.json` (all stages, plus the 2f reference) and `render_settings.json`. Cameras and settings were asserted identical to 2e: Cycles OptiX, 64 samples, denoise, 1920x1080, AgX, exposure 0.4, bloom, and the 4000 W tee fill.

Reimport: 96/96 FBXs passed. Every mesh and every FBX is under 20,000 tris (largest FBX 19,552, largest mesh 18,000), with one material per mesh and bboxes within 0.001 stud. holes.fbx Felt, Timber (rails), SnowRailCap (= the 2e Snow caps) and every other material have world-space vertex sets identical to 2e (4 dp). course_apron_00 triangles are identical to 2e. Only holes.fbx and course_apron_00.fbx changed; the other 94 FBXs are byte-identical to 2e. Export settings: forward -Z, up Y, scale 1.0. See `models/blockout/fbx_validation.json` (pass 2g) and `build_stats_p2g.json`; the manifest is `"pass": "2g"`.

Full fitcheck (props vs the Round 3 holes.json, plus decoration vs this blockout): **ALL PASS, 361 PASS, 0 FAIL, 4 FLAG**. The flags are the same as in 2e/2f: H11/H12 wall clearances at the 0.05 threshold (holes.json designer geometry), and the stale H5/H17 prop rail-skin FBXs running 0.15 past the Round-3 trimmed ends (rebuilt separately in the props rail-skin job). Results: `models/blockout/fitcheck_p2g_validated.txt` and `fitcheck_report_p2g.json`.

# Pass 2g-walls: Round 4 wall clearance (H11 slot lintel, H12 stern line)

**Request** (playtest-log.md "Round 4: wall clearance (fitcheck)"): holes.json moved walls only, never movers. **H11:** the rail5/berg18 floe-slot lintel underside went from y 1.17 to **1.27**. `__cut1` has centre y 1.835 and height 1.13. The side pieces `__cut2`/`__cut3` have centre y 0.56 and height 1.42. **H12:** the icebreaker stern wall line went from z -18 to **-18.01** (hole-local). rail2/hull13 have centre z -18.26. rail3/hull18 have centre z -21.005 and length 5.99. The mitred rail1 has centre z -8.005 and length 21.01, and hull14 has centre z -26.005 and length 15.99. The felt is unchanged.

**What changed in the blockout.** In `holes.fbx`, the wall boxes (`holes__Timber`) and their rail caps (`holes__SnowRailCap`) for exactly these 12 walls were edited in `aurora_blockout.blend`. Each 8-vertex box was found by its exact pass-2g corners, which are recomputed with `build_blockout_p2b.py`'s `box()`/`local()` from the pre-walls holes.json and the world.json placement. Its corners were then moved to the Round 4 box.
- Timber: 12 boxes, 56 vertices. H11 cut1 bottoms and cut2/cut3 tops moved +0.10 vertically. H12 rail2/hull13 shifted 0.01 back, and the stern/far ends of rail1, rail3, hull14 and hull18 moved 0.01.
- Caps: 10 boxes, 64 vertices. The cut2/cut3 caps rose 0.10. The H12 caps follow their walls. The cut1 caps are unchanged because the lintel top is still y 2.40.
- Topology, vertex order, tri counts (14,256) and every other vertex are unchanged.

`holes.fbx` was re-exported with the 2g exporter (forward -Z, up Y, scale 1.0, world positions). The manifest is now `"pass": "2g-walls"`, with `holes.fbx.walls_round4` and a world_placement_notes entry, and `build_stats_p2g.json` has `notes.walls` and `walls_moved_boxes`. Script: `_src/walls_blockout.py` (`edit` / `validate`).

**Changed files** (vs the backup `out_p2g_bak_walls`): `models/blockout/holes.fbx`, `aurora_blockout.blend`, `manifest.json`, `build_stats_p2g.json`, `fbx_validation.json`. Added: `fitcheck_p2g_walls.txt`, `fitcheck_p2g_walls_validated.txt`, `fitcheck_report_p2g_walls.json`, `_src/walls_blockout.py`, `_src/walls_fitcheck_runner.py`. The other 95 FBXs are byte-identical to 2g. `felt_banks.fbx` and the course aprons were not touched; their fitcheck still passes against the moved walls.

**Reimport:** 96/96 FBXs passed, with tris equal to the manifest, every mesh and FBX under 20,000 tris, one material per mesh, and bboxes within 0.05 studs. In `holes.fbx`, **Felt world-space vertices are identical to 2g**, and so are Ice, Brass, Ink, Flag and CrystalGlow. Timber and SnowRailCap differ from 2g only at the expected moved corners, old corner -> new corner (`fbx_validation.json`, `holes_fbx_vs_2g`).

**Fitcheck** (props vs the Round 4 holes.json + decoration vs this blockout; the H11 lintel expectation is now 1.27): **ALL PASS, 361 PASS, 0 FAIL, 0 FLAG**. See `models/blockout/fitcheck_p2g_walls_validated.txt`, which is identical to the props run `out_props/fitcheck_walls_validated.txt`.
- H11 ice_floe vs rail5__cut1 (lintel): **0.150**, at slide offset -5.10. The floe mesh top is 1.12, under the 1.27 lintel.
- H12 paddle_wheel vs rail3/rail2: **0.060**, at 0 deg.

Both 0.050 flags are gone, and the stale H5/H17 rail-skin flags were already cleared by the props rail-skin job. The only other line that changed: H12 felt banks under rails are now 2,540 / 135,928 samples (was 1,951 / 136,517), all still inside a rail box or outside the rails, because of the 0.01 wall move.

**Props (out_props, pass_walls):** `aa_h11_rails`, `aa_h12_rails`, `aa_h11_dressing` and `aa_h12_dressing` were rebuilt, and they are the only prop FBXs a full regeneration changes. The floe, paddle wheel, icebreaker body and mover collision FBXs are unchanged. See `out_props/props_p1_summary.md` and the previews in `out_props/previews/walls/`.
