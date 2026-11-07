# Pirate Shipwreck thumbnail — round 3 sketch follow-up (single lead `B_round3`, round-2 A frame)

The frame follows Chase's annotation `inputs/chase_green_placement.png`. The round-2 scene A camera is kept exactly, and the green sits lower-right as in the sketch oval. The first round-3 pass on the B frame is kept locally in `out_pre_sketch/`. See `CHANGELOG.md`.

## Contents
- `pirate_thumbnail_round3.blend`: compressed, with all images packed. It holds one thumbnail scene and camera, `Thumbnail_B_Lead_R3`, plus the untouched original `Scene`.
- `previews/`: `B_round3.png` (1280×720, no text), `B_round3_320x180.png`, `B_round3_160x90.png`, a grayscale copy of each, and `round2_vs_round3_small_comparison.png` (a review sheet with small labels).
- `manifest.json`: authentic vs staged objects and counts, camera, lights, golf cluster, source hashes and validation checks.
- `CHANGELOG.md`: the exact corrections and limitations.
- `src/`: the scripts for building, rendering, downsampling and validating, plus `round3_config.json` and `rebuild_round3.ps1`.
- `logs/`: build and validation logs, `build_report_r3.json`, proof renders and the round-2 scene A reference render.

## Rebuild (Windows PC)
Run one Blender process at a time on CPU Cycles. Never touch Roblox Studio.
```powershell
powershell -ExecutionPolicy Bypass -File out\src\rebuild_round3.ps1 `
  -Source inputs\pirate_thumbnail_round2.blend -Approved inputs\start_ship_whimsy_v5_1.blend -Output out\pirate_thumbnail_round3.blend
```
Or run the steps one by one:
```
blender -b --factory-startup --python-exit-code 1 --python out/src/build_thumbnail_round3.py -- --source inputs/pirate_thumbnail_round2.blend --approved inputs/start_ship_whimsy_v5_1.blend --output out/pirate_thumbnail_round3.blend --report out/logs/build_report_r3.json
blender -b out/pirate_thumbnail_round3.blend --python-exit-code 1 --python out/src/render_round3.py -- --output out/previews/B_round3.png
blender -b inputs/pirate_thumbnail_round2.blend --python-exit-code 1 --python out/src/render_round3.py -- --scene Thumbnail_A_Hero_R2 --output out/logs/round2_A_reference.png
python out/src/make_downsamples_r3.py --previews out/previews --round2 out/logs/round2_A_reference.png
blender -b --factory-startup --python-exit-code 1 --python out/src/validate_round3.py -- --source inputs/pirate_thumbnail_round2.blend --approved inputs/start_ship_whimsy_v5_1.blend --output out/pirate_thumbnail_round3.blend --previews out/previews --report out/logs/build_report_r3.json --manifest out/manifest.json
```
You can tune the result in `src/round3_config.json` with these settings:
- camera (`mode: keep_base` keeps the round-2 A camera; optional small `tweak`)
- green placement (`uv` = image centre of the oval, `radius_uv` = oval radii, ray-cast onto the sand) and `pole_top_v_max` (keeps the flag below the face), plus the cup, ball, pole and flag sizes
- face key scale
- render-only dressing moves

The build fails if the green's footprint leaves dry sand.

## Staging rules
Everything except the approved ship collections (Visual, Props, Ramps) is RENDER_ONLY thumbnail staging. That covers the cove terrain and water, palms and rock, the lights, and the putting green, cup, flag and ball. None of it is a game asset, and none of it shows a live or playable hole. The validator checks that the approved ship is unchanged against `start_ship_whimsy_v5_1.blend`.
