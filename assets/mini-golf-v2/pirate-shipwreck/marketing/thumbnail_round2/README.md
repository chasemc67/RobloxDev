# Pirate ship thumbnails: ROUND 2 (revised A hero / B octopus)

These are round-2 proofs, made after the round-1 Art and Playtest critique (`inputs/playtest_round1.md`). They are **not final and not approved**. Work stops here until an independent second critique has been done. C was dropped as instructed, so there is no C scene, camera or render.

## Deliverables
| Path | What |
|---|---|
| `out/pirate_thumbnail_round2.blend` | Packed, compressed. Scenes `Thumbnail_A_Hero_R2` and `Thumbnail_B_Octopus_R2`, each with its saved camera of the same name. The untouched original `Scene` from the approved ship file is still in the file. It is not a thumbnail. |
| `out/previews/A_round2.png`, `B_round2.png` | 1280x720 Cycles renders with **no text** |
| `out/previews/*_320x180.png`, `*_160x90.png` | Lanczos downsamples of the same renders |
| `out/previews/*_gray.png` | Grayscale review copies (all three sizes) |
| `out/previews/round2_small_review_sheet.png`, `round1_vs_round2_small_comparison.png` | Review aids at native small size. Only the sheets have labels. |
| `out/manifest.json` | Authentic vs staged assets, counts, cameras, lights, settings, input hashes before/after, validation and measurements |
| `out/CHANGELOG.md` | Each critique point mapped to the exact change and its measured value |
| `out/src/` | Portable build, render, downsample, validation and baseline scripts, plus `round2_config.json` |
| `out/logs/` | Logs and debug only (proof-loop helpers and half-res proof renders live here too) |
| `out/DONE` | Completion marker |

## Runbook (Windows PC, one Blender process at a time, CPU Cycles)
```powershell
powershell -ExecutionPolicy Bypass -File out\src\rebuild_round2.ps1 `
  [-Blender "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"] [-Python python] `
  [-Source inputs\pirate_thumbnail_round1.blend] [-Approved inputs\start_ship_whimsy_v5_1.blend] `
  [-Output out\pirate_thumbnail_round2.blend] [-Samples 64]
```
The approved ship (`-Approved`) is `start_ship_whimsy_v5_1.blend`, SHA-256 `fd7798af4ca9bd107dba927bdf663e7017c04f8c4c7649b518b5c78c8d4bcacd`. It is no longer in RobloxDev: stage it from chasemc67/vr-mini-golf-v2, `assets/pirate-shipwreck/models/start_ship_whimsy_v5_1/start_ship_whimsy_v5_1.blend` (Git LFS).
It runs four steps, and each one stops the rebuild on a non-zero exit code (`--python-exit-code 1`):
1. `build_thumbnail_round2.py --source <round1.blend> --approved <ship.blend> --output <round2.blend>` opens the round-1 file read-only and saves a copy. It refuses to write over either input and records the SHA-256 of both inputs before and after.
2. `render_round2.py -- --scene A`, then `--scene B`. Optional `--out/--samples/--percent` flags make quick proofs.
3. `make_downsamples.py` (needs Pillow) writes the 320x180 and 160x90 copies, the grayscale copies and the review sheets.
4. `validate_round2.py` checks the inputs and the output, takes the measurements and writes `out/manifest.json`. Its exit code is non-zero if any check fails.

Optional: `blender -b inputs/pirate_thumbnail_round1.blend --python out/src/measure_round1_baseline.py -- --outdir out/build/r1_baseline` re-renders the round-1 A/B at half resolution and samples the same pixel medians. That gives the round-1 baseline for the lighting comparison. It does not save the input.

All staging is set in `out/src/round2_config.json`:
- Cameras use a horizontal orbit (`az`, `dist`) around a target, an absolute `cam_z`, a `look_z` or `pitch`, a lens, an optional `yaw_offset` and a shift.
- Each scene has its own lights and exposure.
- Kit dressing is given either as world coordinates or as `@uv` image points. An `@uv` point is ray-cast onto the staged terrain, and the build stops if the hit is not dry sand.
- The golf ball is placed from its image position (`ball_uv`) and its projected height fraction (`ball_frac`).
- Putter offset and yaw are set per scene, and there is an optional `sandbar_z`.

## What is authentic and what is staged
- **Authentic, unchanged:** every object in `inputs/start_ship_whimsy_v5_1.blend`, compared object by object against the output: mesh coordinate, loop and material-index hashes, basis transforms, parent inverse, matrix_world, parent, modifiers and material node values. Nothing was moved, edited, re-originated or re-posed to fake a pose.
  - The separate left `Pier` object and mesh are still in the file and unchanged. They are simply not linked into either thumbnail scene. Scene A has to drop the pier per the critique; B also drops it so it does not sit behind the ball.
  - The ship collections are only *linked* into extra collections: `RO2_ShipVisual_NoPier` and the light-linking receiver collections.
  - `Collision` is not linked into the thumbnail scenes.
- **Staged, render-only** (collection `RENDER_ONLY_Environment_R2`):
  - The round-1 cove terrain, water, sea floor and sky world, reused unchanged.
  - Original kit_v1 / kit_v22 palm, rock and fern meshes, reused with new per-scene placements.
  - Golf ball, putter and the B sandbar.
  - All lights.

  None of this is the v31 game layout. Nothing shows a cup, flag, hole, shot trail, avatar, score or playable course.

## Known limitations
See the end of `CHANGELOG.md`, which has the measured values and the remaining weaknesses.

Note: logs written by `rebuild_round2.ps1` (`out/logs/build_r2.log`, `render_r2_*.log`, `validate_r2.log`) are UTF-16, because PowerShell 5.1 `*>` writes UTF-16. Read them with `Get-Content`, or with `iconv -f UTF-16`.
