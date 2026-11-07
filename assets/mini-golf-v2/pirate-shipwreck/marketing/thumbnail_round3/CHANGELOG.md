# Round 3 — sketch follow-up (single lead `B_round3.png`, round-2 A frame)

Status: delivered for an independent Art + Playtest critique. **Not approved**, and this is not a final pick.
Trigger: Chase's annotation `inputs/chase_green_placement.png`, which arrived during the first round-3 pass. I read it visually before staging. It is a markup of the round-2 **A** render: a red oval on the right sand at about x 70–96%, y 75–95%, and a red line (the flag) rising from the oval beside the bow toward the octopus. It overrides the earlier B-only camera preference. The sketch is used as a reference only. Its red lines and border are not in the render, and no image is projected.
Checkpoint: the first round-3 output was copied to `out_pre_sketch/` (local, uncommitted) before any change.

## What changed vs the first round-3 pass
1. **The frame is now round-2 scene A's camera, kept exactly.** Location (276.16, −138.94, 13.0), rotation (96.6°, 0°, 64°), 25 mm lens, no shift, no tweak (`camera.mode: keep_base`). The ship composition is the same as A_round2: side view, pier left, palms left and right, rock right, and the quiet sky upper-left (no text). The first pass's raised B camera (z 19, 22 mm, shift −0.19) was dropped.
2. **The scene base swapped from B to A.** Round-2 scene B was deleted, along with its camera, its 6 lights, its 5 dressing objects and its light-link collections. Scene A was renamed `Thumbnail_B_Lead_R3` so there is still ONE thumbnail scene and ONE deliverable named `B_round3`. The A lights were renamed `A_R2_*` → `R3_*`, and the A dressing `RO2_A_*` → `RO3_*`. A's palms, rock and fern are in their round-2 positions, and no dressing was moved.
3. **Every giant ball and putter is gone.** That covers both A's (`RO2_A_GolfBall`, `RO2_A_Putter`, the left foreground of the sketch) and B's, with their meshes and materials.
4. **The green is placed from the sketch oval.** The same RENDER_ONLY models as before are used: chunky low-poly turf top, raised rolled rim, skirt, dark cup, slender white pole, red triangular cloth flag, and a modest white ball. The green outline is now the sketch's **screen-space oval** (centre u 0.825, v 0.15; radii 0.12 × 0.09, slight wobble) ray-cast onto the staged sand. This addresses the brief's point that the low 13-stud A eye needs depth: the green geometry is fitted, rather than the camera being moved.
   - Rendered bounds: u 0.702–0.956, v 0.047–0.249. That is lower-right and whole, with margins of 57 px right and 34 px bottom at 1280×720 (validator rule ≥ 0.04 of the frame).
   - World footprint: about 51 × 62 studs (it is long in depth because of the grazing view). It is centred near (237.8, −91.8) on dry sand (z ≈ 3.8; the lagoon is at z 1.0). Turf is 0.5 above the fitted sand plane.
   - The cup sits up-right on the green, and the ball (r 1.0) is front-left.
5. **The flag stops below the face.** The pole height is clamped so its top projects at v ≤ 0.37. Its height is 9.4 studs, the flag flies toward frame-right, and the octopus's lowest point is v 0.419, a gap of 0.049 of the frame. The sketch's line ran up to the grin, so it was shortened as instructed, and the eyes and grin stay clear.
6. **The softened coral light rig is kept.** It is applied the same way to the A rig: `R3_Sun_Key` (3.6) excludes `Prop_Figurehead` through light linking, and `R3_FaceKey_Soft_Linked` (1.8 = 0.5×) lights only the octopus from the same direction. A's round-2 FaceBounce / ShipFaceFill linked lights were not changed. Exposure (−0.4, A's value), materials and hue are unchanged.

## Process
Build → one proof render → one small correction. The right margin was 0.039, so the oval centre moved from u 0.83 to 0.825. The turf height went from 0.7 to 0.5 so the green reads less like a puck. Then a rebuild, a final render and validation. There was no camera search.

## Validation (`logs/validate_r3.log`; all 11 OK)
- Both input SHA-256 hashes are unchanged: round-2 3837fadb…9d43, approved fd7798af…acd.
- All 239 approved ship objects are identical: mesh, materials, transforms, parents and modifiers.
- Images are packed, there is a single thumbnail scene and camera, Collision is not linked, and the giant balls and putters are gone.
- The whole green is in frame, the flag is clear of the figurehead, the green rendered 34k turf pixels in its box, and all output sizes are correct.

## Limitations / open for critique
- **Pole shorter than the sketch line:** the pole and flag are shorter than the sketch's red line, which reached the grin, so the face stays clear. The flag also overlaps the lower-left edge of the right rock.
- **Green shape and scale:** the green is fairly large and near the camera, so it reads strongly at 160×90. The rim and skirt give it a slightly thick "disc" edge.
- **Not compared to the original A PNG:** the round-2 side of the comparison sheet is a fresh render of the unmodified round-2 scene A (`logs/round2_A_reference.png`), not the original round-2 PNG.
- **Face vs porthole and coral:** these are the round-2 A look. The big bow porthole sits up-left of the octopus face, and some top coral facets are still bright.
- **Green pixel check:** this is a colour heuristic inside the projected box.
- **Scene name:** the scene is named `Thumbnail_B_Lead_R3` for the single deliverable even though its frame is round-2 A.
- **No live-game claim:** the scene export manifest was not used, and nothing here claims to be the live game or a playable hole.

---

# (Superseded) First round-3 pass — B frame (checkpoint in out_pre_sketch/)

Status: delivered for an independent Art + Playtest critique. **Not approved**, and this is not a final pick.
Source: `inputs/pirate_thumbnail_round2.blend` (@d0dd39a, SHA-256 3837fadb…9d43, unchanged). Approved ship: `inputs/start_ship_whimsy_v5_1.blend` (SHA-256 fd7798af…acd, unchanged).

## Exact corrections (from Chase's latest direction)
1. **Giant near-camera ball and putter removed.** `RO2_B_GolfBall`, `RO2_B_Putter` and `RO2_B_Sandbar` (plus their meshes and materials) were deleted. Scene A's ball and putter went with scene A. Nothing from them stays in the file.
2. **Golf cluster moved to the RIGHT beach, close to the bow.** It is a new collection, `RO3_B_GolfGreen_RenderOnly`, built from chunky low-poly geometry (534 tris total):
   - `RO3_RenderOnly_PuttingGreen`: a curved bean-shaped green, 32 × 18 studs, at (196.6, −35.2), on dry sand. It has a flat turf top, a raised rolled rim (+0.55 studs, lighter green) and a darker skirt sunk into the sand. Its plane is fitted to the sand slope.
   - `RO3_RenderOnly_Cup`: a dark cylinder, r 2.3.
   - `RO3_RenderOnly_FlagPole`: a slender white pole, r 0.2, 13 studs tall.
   - `RO3_RenderOnly_FlagCloth`: a red triangular cloth mesh, 7.5 × 4.5, with a gentle wave. It flies toward frame-right, away from the face.
   - `RO3_RenderOnly_GolfBall`: a modest white ball, r 1.1 (cup:ball ≈ 2.1:1), resting on the green short of the cup.
   - Every object is tagged `RENDER_ONLY`. These are thumbnail staging only, not live or playable assets, and they make no claim about a hole in the game.
3. **The whole green is in frame.** It spans u 0.64–0.89 and v 0.06–0.15. The smallest margin is 41 px at the bottom (1280×720), with 135 px on the right. About 13.5k turf pixels are rendered in its box, so it is not hidden. The flag and pole sit below the figurehead with a vertical gap of 0.037 of the frame height, so they never cross the eyes or face.
4. **Small camera change** to open the beach so the green reads as a surface rather than a sliver. The camera was raised from 8 to 19 studs and its pitch went from 16° to 9.5°. Orbit target, azimuth, distance, 22 mm lens and shift_x −0.19 are all unchanged. This keeps the B bow/frontal composition, the full bowsprit curl, the mast and flag, and the quiet upper-left sky (no text). It also shows more of the turquoise lagoon and a little more face-on octopus.
5. **One render-only rock moved.** `kit_rock_m` went from (216, −15) to (230, −2) because it overlapped the right end of the green. The palms and fern were not moved.
6. **Hot coral softened locally through the light rig.** The main key (`B_R3_Sun_Key`, 4.2) now excludes `Prop_Figurehead` via light linking. A face-only key in the same direction at 0.5× (`B_R3_FaceKey_Soft_Linked`, 2.1) replaces it on the octopus. Exposure (−0.3), materials and hue are unchanged. Measured on the face region of the 1280 render, clipped coral facets (R ≥ 250) went from 0.27 to 0.20 of the coral pixels, and the median coral stayed about (203,108,81). That is a measurement of the pixel crop, not of the material colours (230,120,100 / 180,80,70), which are untouched.
7. **Round-2 scene A removed** (its camera, lights, dressing and collections). There is now ONE thumbnail scene and camera, `Thumbnail_B_Lead_R3`. The original source `Scene` stays untouched.

## Validation (`out/logs/validate_r3.log`; all OK)
- Both input SHA-256 hashes are unchanged before, during and after the build.
- All 239 approved-file objects match: mesh, material node values, transforms, parents and modifiers.
- Images are packed, there is one thumbnail scene, Collision is not linked, and the old ball and putter are gone.
- The whole green is in frame (≥ 0.04 margin), the flag is clear of the figurehead, the green is visibly rendered, and all output sizes are correct.

## Limitations / open for critique
- **Face vs bow porthole:** not separated further. The big bow-eye porthole still sits just left of and above the octopus face. I tried no azimuth change, to keep this pass bounded. The paired eyes and grin are visible at 320; at 160 they are small and need a critic's judgment.
- **Green size at 160×90:** the green is about 32×12 px with a red flag and white ball, and it reads as a green-with-flag in the comparison sheet. The cup is small at 160 and mostly reads at full size.
- **Coral:** only partly softened. About 20% of the coral pixels on the top facets are still clipped near pure orange-pink.
- **Raised camera:** this changes the round-2 B view slightly. There is more lagoon in the lower-left and a slightly less heroic low angle. The left lagoon and sand are now a large quiet area.
- **Green pixel check:** it is a colour heuristic inside the projected box, not a per-object occlusion matte.
- The scene export manifest (Edit session, Nov 7 2:51 PM PT, PlaceVersion 0) was not used. Nothing here claims equality with the published place or the live meshes.
- The round-2 comparison image is a fresh render of the unmodified round-2 file's B scene (`out/logs/round2_B_reference.png`), not the original round-2 deliverable PNG.
