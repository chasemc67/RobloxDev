# SRV-131 pass 2: completed on Windows

100 pieces / 105 FBX / 818 placed instances / 309,074 placed triangles. Library: 129,583 triangles; max mesh 4,324 (<20k). Added one 12-triangle rim asset, 80 placements, 960 placed triangles. Existing FBX files were retained; only `fbx/rim_silhouette.fbx` was built in Blender 5.2.2 LTS.

## A. Visible outer rim

80 of 80 candidate 64-stud stretches were visible from at least one of 363 tee/walkway observer samples (eyes +5). Crest visibility tests sampled endpoints/centre and traced the 16-bit heightfield at <=2-stud intervals. Walkway observer spacing <=16 studs. Full per-stretch observer evidence: `layout.json pass2.rim_coverage`. Added short low-poly striped silhouette blades, buried 12 studs beneath the sampled crest, with irregular tops; CastShadow false. No outer rim cliff kit. Existing interior cliff kit retained.

## B. Scatter sightlines

Checked every member in all six scatter clusters, using final holes.json world_offset/world_yaw and the specified transform, tee eye +5 to cup+7.5 and cup+1, with a 1.5-stud corridor. Conservative seed-expanded variant bounds and an independent final exported triangle-bounds check both found zero intersections. Removed counts: H1-H18 **0 each**; unique removals **0**. Existing footprint keep-outs already clear these lines. No scatter FBX rebuild was required. Stable member seeds are stored for reproducible future filtering.

## C. Validation and artifacts

`sc_fitcheck.py`: **ALL PASS**; results in [fitcheck_pass2_validated.txt](fitcheck_pass2_validated.txt). All 18 footprints clear >=2 studs (minimum 2.10); all 74 walkway segments clear (minimum overhead 9.25); all 36 scatter sightline corridors clear. Far cards + sky including rim: 2,598 placed triangles, CastShadow off. The original H3 rail/footbridge conservative lower-bound note (2.9 studs) remains in pass1 validation.

Updated layout assumptions/counts, manifest placements/totals, README, contact_sheet.png, and reproducible pass2 rules integrated into sc_layout.py. Fixed deprecated material blend API access for Blender 5.2. Paths resolve from script directories. NumPy, Pillow and Matplotlib are installed in system Python; Blender supplies bpy/NumPy. The Windows launcher checks Get-Process blender before each launch, waits/polls 60 seconds if occupied, launches hidden, and waits for exit. No SSH or external messages.

## D. Hero stills

Cycles / OptiX / NVIDIA GeForce RTX 4090 / denoise / 1920x1080 / 128 samples. Terrain from the 16-bit source heightmap, sampled every 2 studs with boundary vertices at -640..640; y=gray/65535*260. Brown-sugar sand, peach mesa sand and six-band sandstone follow course.md. Water/lake/stream/fall surfaces use world.json levels. All placed FBX assets are assembled as shared instances. Render-only cards use geometric alpha cutouts and native node materials. Vista omits distant cards/clouds; Crown omits overlapping mesa/butte cards. Warm rose/tangerine sky and bounce illumination keep below-horizon dusk readable.

Sun lamp and disc: **hardcoded compass bearing 277°, elevation -3°**; world.json sun is ignored. The disc is on that ray from Crown (-370,196,165), 2,500 studs away. Terrain and rim can obscure the below-horizon disc in the Crown shot; near Sunset Arch and the far arch retain their source placements. Source spillway/deck geometry similarly obscures portions of the waterfall from crest eye height. No scene geometry was moved to force visibility.

Render script: [render_hero.py](render_hero.py). Packed reusable scene: [sugarloaf_canyon_hero.blend](../previews/hero/sugarloaf_canyon_hero.blend). Shot definitions are stored in the scene; `--reuse` reloads it. All six images were visually inspected; PNG metadata independently confirms Cycles 128 samples. Final render order ends with sunset_arch_from_crown. No flythrough.

| Render | Samples | Render time |
|---|---:|---:|
| [old_sugarloaf_skyline](../previews/hero/old_sugarloaf_skyline.png) | 128 | 4.91 s |
| [dam_crest_walk](../previews/hero/dam_crest_walk.png) | 128 | 4.98 s |
| [narrows_crystal_walls](../previews/hero/narrows_crystal_walls.png) | 128 | 5.66 s |
| [junction_town](../previews/hero/junction_town.png) | 128 | 4.68 s |
| [world_vista](../previews/hero/world_vista.png) | 128 | 4.39 s |
| [sunset_arch_from_crown](../previews/hero/sunset_arch_from_crown.png) | 128 | 4.24 s |

Scene assembly plus final six renders: 33.66 s; rendering total 28.86 s. Detailed eyes/targets/FOV/timings in [render_report.json](../previews/hero/render_report.json). [Hero contact sheet](../previews/hero/contact_sheet.png); [full piece and hero contact sheet](../contact_sheet.png).

Reproduce from models directory:
```powershell
python _src/pass2_rules.py
& _src/run_blender.ps1 -Script _src/sc_build.py -ScriptArgs '--only','rim_silhouette' -Log build_pass2.log
python _src/sc_fitcheck.py
& _src/run_blender.ps1 -Script _src/render_hero.py -Log hero_final.log
python _src/finalize_pass2.py
```
