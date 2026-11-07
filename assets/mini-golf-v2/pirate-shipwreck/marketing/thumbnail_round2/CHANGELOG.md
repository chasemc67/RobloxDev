# CHANGELOG: pirate thumbnails round 1 → round 2

This round revises A and B in response to `inputs/playtest_round1.md` and the round-2 brief. C was dropped: no C scene, camera or render. Nothing here claims reviewer approval, a two-second test result or CTR. All values below are measured by `out/src/validate_round2.py`, and the full detail is in `out/manifest.json`. Image coordinates run 0..1 with y up.

**Files:** `out/previews/A_round2*.png` and `out/previews/B_round2*.png` (1280x720, 320x180 and 160x90, each with a `_gray` copy), plus `out/pirate_thumbnail_round2.blend` with scenes `Thumbnail_A_Hero_R2` and `Thumbnail_B_Octopus_R2`.

**Round-1 baseline:** the "r1" numbers come from `out/src/measure_round1_baseline.py`. It re-renders round-1 A/B at half resolution from the unchanged round-1 file and samples pixels the same way as round 2: visible polygon centres of each material, ray-cast from the camera, HullWood above z=4 only, median sRGB. The values are in `out/build/r1_baseline/round1_pixel_baseline.json`.

## Both scenes
| Feedback | Change | Measured |
|---|---|---|
| Golf is not identifiable; add a ball and putter as render-only staging, lower-left, with no cup, flag or trail | New render-only `RO2_<A/B>_GolfBall`: real geometry (10,242-vertex sphere with 162 displaced spherical-cap dimples, no texture), white principled material with a light coat. New `RO2_<A/B>_Putter`: low-poly gunmetal mallet, steel face insert, steel shaft, black grip, lying on the sand with its head beside and slightly behind the ball and its shaft toward the left margin. Both are placed by ray-casting from each scene's camera to image targets, and cast shadows from the key sun. | Ball height: **A 13.5%** (target 12–15) at u 0.21–0.29, v 0.09–0.22; **B 16.5%** (target 15–18) at u 0.20–0.31, v 0.05–0.22. Ball bottom sits above the water (z = 3.8 in A, 2.8 in B; water is at 1.0). No cup, flag, trail, avatar or score anywhere. |
| Reserve a quiet upper-left title area (≈35%w x 30%h, 5% margins) with no mast or rigging through it | Solved with camera position, lens shift and palm placement only. Ship geometry and rigging were not moved. | Geometry vertices inside u 0.05–0.40, v 0.65–0.95: **0 in A, 0 in B** (ship, rigging, ropes, palms, props). Pixel luminance std in the zone: A 7.6 (sky gradient), B 3.4. Renders contain **no text**. |
| Broad warm fill on hull and face (+0.5 stop), remove the olive cast, keep material RGB unchanged | No material edits. New per-scene rig: warm key sun, shadowless warm fill, cool rim sun, plus **light-linked** warm fills. The ship/face fill reaches all ship meshes except `Rigging`. A warm upward "sand bounce" reaches only the hull, and a separate one reaches only the octopus; these counter the turquoise lagoon bounce that caused the olive cast. A cream sail-only fill is used in A. Exposure is A −0.40 and B −0.30 (Standard view, as in round 1). | **Hull (HullWood) median:** A 91,87,61 → **131,94,64** (**+0.49 stop** linear luminance); B 83,85,65 → **123,95,70** (**+0.56 stop**). Hull R/G went from 1.05 to 1.39 in A and 0.98 to 1.29 in B, so it now reads brown instead of olive. |
| Coral top 230,120,100 and underside 180,80,70, not dark red | Coral is held at its target by exposure, the face fill and the face-only bounce. | **Coral (top) median:** A 234,124,103 and B 234,122,102. **CoralDk (underside):** A 169,77,60 and B 167,76,60. B underside is +0.23 stop over r1 (143,78,65). A underside was 172,103,79 in r1, a desaturated orange; its hue has moved to the target, but its luminance is lower. |
| Cream sails not blown out | Sails are excluded from the hull/face fill; A gets a sail-only fill. | Sails median: A 150,140,119 → **197,185,163**; B 172,171,153 → **212,197,170**. **0% of sail samples are clipped.** Clipped pixels across the whole frame: A 0.9%, B 1.2%. |
| Palms: 3–5 visible, grouped away from masts, rigging and face; no trunk tangencies | All round-1 kit placements were removed. New per-scene placements reuse the original kit_v1 meshes (see manifest `placed_kit_instances` for exact world positions, scales and yaws). | A: 5 palms, in a small pair on the far left shore below the title zone and a group of 3 on the right edge, plus a fern, a rock and a leaf clump. B: 3 palms on the right edge, plus a fern and a rock; about 2 are clearly visible. No palm sits behind the face or crosses the masts or title zone. |
| Kit assets are reused; staging is render-only and documented | Kit meshes `KIT_*` come from the round-1 file and are unchanged. The round-1 cove terrain, water and sky are reused unchanged. | See manifest `authentic_vs_staged`. |

## A: hero / environmental alternative
| Feedback | Change | Measured |
|---|---|---|
| Orbit toward a bow front three-quarter view, lower and about 20% closer; not a broadside zoom | Camera orbited from azimuth −115° (stern quarter) to **−26°** around the ship centre (bow front three-quarter). Height dropped from z 112 to **z 13** (about 9 studs above the sand). Distance to the ship centre went from 465 to **286** studs (38% closer); the lens went from 30 to 25 mm. | Camera at (276.2, −138.9, 13.0). |
| Whole ship 55–65% of the frame, about 65% | Framing from the camera search plus `dist` and `lens` settings. | Hull, rigging and props span **62.3%** of frame width (u 0.29–0.92) and 70.6% of height. |
| Octopus face visible; broad cream sail faces; clear silhouette | From the bow three-quarter view the octopus faces the camera and the sails are seen near face-on (|view·X| ≈ 0.9). | Octopus full height 47.5%, head (mantle and face) 20.8%. Bowsprit curl margin from the frame edge: 0.056. |
| Remove the cropped left separate pier, leaving one green boarding bridge | `Pier` is not linked into the scene; the scene uses collection `RO2_ShipVisual_NoPier`, which holds links to the original Visual objects except Pier. The Pier object and mesh are unchanged in the file. | `Pier` is absent from scene A (validation `scenes_and_cameras`). The authentic `Ramps` bridge is still shown, at u 0.02–0.32. |
| Less empty bottom-right sand | The lower camera compresses the foreground, and palms, rock and fern on the right shore fill the edge. | Partly fixed only; see the weaknesses below. |

## B: octopus, first choice
| Feedback | Change | Measured |
|---|---|---|
| Orbit 15–25° toward the front of the octopus and closer, so both eyes and the grin read at 160x90 | Camera azimuth around the face went from −64.5° to **−40° (24.5° orbit)**. Height dropped from z 22 to **z 8**, the lens went from 20 to 22 mm, and the view is pitched up 16° with a 10° yaw offset and lens shift −0.19. | Camera at (264.9, −86.1, 8.0), 120 studs from the face (r1: 122). Both eyes and the grin show at 1280 and 320. At 160x90 the eyes read as two dots and the grin is marginal. |
| Friendly frontal face; octopus 22–25% of image height | "Octopus" is measured as the head (mantle and face, z 27–52 on the figurehead mesh). | Head **23.1%**. Full figurehead including the arms on the curl: 53.5% (r1: 49.9%). Body below the curl grip: 28.1% (r1: 27.5%). |
| Enough hull and one sail for pirate identity; the full bowsprit curl tip in frame | Lens shift and pitch keep the curl inside the frame. | The curl tip is inside the frame with a **0.109** minimum margin. The hull and the fore and main sails are visible. |
| Face and arms against clean sky, not palms or rocks | B palms moved to the right edge, away from the face, and the camera was lowered so the face sits above the horizon. | The face background is sky (see the render). |
| The gold hull porthole must not read as the octopus's eye; fix by angle and framing, not by editing the mesh | Only the angle changed: the octopus is larger and more frontal than the porthole. The `ShipV5_BowEyes` mesh is untouched. | Partly fixed only; see the weaknesses below. |
| Ball and putter must not cover the face, and must be separated from the hull by water or sky | The foreground there is lagoon water, so a render-only faceted **`RO2_B_Sandbar`** (top z 3.0, falling below the waterline at its edges) was added under the ball and putter. The ball sits at u 0.20–0.31, and the hull starts at u 0.37 with lagoon water between them. B also drops the separate `Pier` (same method as A) so it does not sit behind the ball. | The ball and face do not overlap. |

## Iterations
1. The proof loop ran at half resolution and 16 samples. It is not a deliverable; its files are in `out/logs/iterprev`. Cameras were chosen with projection searches (`out/logs/camsearch*.py`) against the title zone, octopus size and curl margin.
2. Then there was one bounded polish after the first full-res render, on props only, with no camera change. B ball u moved from 0.15 to 0.25 to reduce off-axis stretch and clear the hull. The putter face insert changed from white to steel, because the white insert made the head read like a remote. B palms moved to the right edge, because the original placements were outside the frame (0 visible).
3. A final rebuild only corrected the dimple-count wording in the docs and report.

## Remaining weaknesses
- **B putter:** it is mostly a dark head at the left edge, and almost none of the shaft is in frame. In B the golf cue is carried by the ball. In A the putter is visible, but its mallet head is boxy.
- **B porthole:** the `ShipV5_BowEyes` porthole, with its painted eye, sits next to the face at a similar scale and can still read as a third eye. This is the authentic mesh, and moving the camera further around would break the title-zone and curl constraints.
- **Grayscale:** the coral octopus and the blue sky have nearly the same luminance in `_gray`, so the face is separated mainly by hue. The white ball has the strongest value contrast in both images.
- **Coral highlights:** 34–37% of the visible coral-top samples hit 255 in the red channel. The medians are on target, but the upper facets are hot.
- **A underside:** CoralDk luminance is −0.44 stop versus r1, a trade-off for the hue correction.
- **A sand:** the bottom ~22% of the frame is still sand, though it now holds the ball and putter. The boarding bridge reads as a wooden walkway; its green felt top is not visible from the low camera.
- **Small sizes:** at 160x90 the grin is marginal. The head (23% of height) follows the brief's number; a larger face would read better.
- **Similar compositions:** A and B are both port-bow diagonals. They differ in distance, height, lens and octopus scale, but they could look alike in a small grid.
- **B ball:** it is still slightly elongated by off-axis perspective (22 mm lens with shift).
- **Ball model:** 162 dimples is fewer than a real ball (~336); it reads as a stylised ball.
- **Staging:** the B sandbar, the cove, the palm positions and the lighting are all staging. None of it is the v31 game layout or a verified course, and nothing suggests a playable hole.
- **Not tested:** there is no human two-second test or CTR measurement. The independent second critique is still pending.
