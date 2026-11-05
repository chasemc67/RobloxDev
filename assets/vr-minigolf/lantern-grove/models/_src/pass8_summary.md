# Lantern Grove props: pass 8 summary (2026-10-10): lantern-lit H9, rail lanterns on H7/H8, brighter H8 glow, Round-7 moving props

Brief: `_src/brief_pass8.md`, including the 18:46 addendum ("holes.json Round 7 is FINAL"). Step log:
`_src/pass8_progress.md`. Before: `_src/manifest_before_pass8.json`.
- The holes.json, world and fly files were only read, never edited.
- Pass 7b was unfinished: the tee renders were done, but the contact sheet, README and summary were missing. Those were
  finished first; see `_src/pass7b_summary.md`.

**Result:**
- **Fitcheck: ALL PASS, 209 checks** against the FINAL Round-7 `holes.json` (18:33), i.e. 188 + 21 new pass-8 checks,
  including 9 negative tests.
  - Saved as `_src/fitcheck_pass8_validated.txt` (= `_src/fitcheck.txt`).
  - The 6 Round-7 drift FAILs (H7 log, H8 door + pocket + entry ring, H9 pendulum) are resolved by rebuilding those
    props.
- Tee views re-rendered at 32 spp:
  - H7, H8 and H9 (final run; H9 went through 3 iterations);
  - H6, whose dressing changed.
- `tee_contact_sheet.png`, `contact_sheet.png` (121 props) and `README.md` were rebuilt.

**Renders checked:**
- **H9 reads lantern-lit:** a warm interior, wall lanterns, and the 3 amber lanterns hanging over the heart beside the
  pendulum beam.
- **H8 reads magical:** amber crook lanterns show above its 3.9-tall walls on both sides, and the fireflies / glow
  shrooms are much brighter.
- **H7 lower tiers are lit:** lanterns show by both rails of the middle tier and around the lower green. The new
  pointed log reads, with pale whittled tips.

## What RobloxDevBot must pull in

### 1. New FBX (decoration only: CanCollide / CanTouch / CanQuery = false, Anchored)

| FBX | Tris | Use |
|---|---|---|
| `fbx/lantern_large_hanging.fbx` | 384 | H9 x3, **Model:ScaleTo(0.85)**. It is the `lantern_large` paper lantern (same mesh) plus an 8.35-stud iron cord and a top ring. Origin = lantern bottom centre; the tassel hangs 0.09 lower at scale 0.85. As placed: a 1.2 x 1.8 x 1.2 lantern, bottom at y 7.2, cord top at y ~16. |
| `fbx/rail_lantern_stake.fbx` | 172 | H7 x3: an oak stake with a small paper lantern, 1.9 tall. |
| `fbx/rail_lantern_crook.fbx` | 220 | H7 x5, H8 x15: a crook post, 6.5 tall. The lantern hangs 2.0 out along local +X, 5.25..6.1 above the base. Its yaw points +X at the rail. |

Previews: `previews/<name>_{eye,34}.png`.

### 2. Rebuilt Round-7 moving props (re-import; pivots per props.md / holes.json)

| FBX | Tris | Change | Motion (`manifest.props[].motion`, = holes.json) |
|---|---|---|---|
| `fbx/h7_floating_log.fbx` | 740 | 6 long (was 5): a 5.2 round body plus **whittled pointed ends**. The last 0.4 tapers to a vertical edge at x = +-3.0, in pale MoveCream. | Pivot (0, -1.2, -20.5). Slides X -6..+6 at 3.5 studs/s. Dwell 1.0 s at -6 and 1.5 s at +6; cycle 9.357 s. |
| `fbx/h8_root_door.fbx` | 544 | 3.6 long (was 3.2). | Pivot (4.75, 0, -11.5) = closed. Slides +Z 0..4 at 3 studs/s. Dwell 1.8 s closed and 2.2 s open; cycle 6.667 s. |
| `fbx/h8_door_pocket.fbx` | 416 | Only the **south** pocket is placed now (rail16, z -7.75). It is 2.05 deep, because the open door end passes the rail line by 2.05. The north pocket is gone: the door never reaches rail14. | Static. Notch the visual rail kit at x 4.2..5.3 on rail16. |
| `fbx/h9_lantern_pendulum.fbx` | 1,828 | A **square 1.6 x 1.8 x 1.6 lantern bob turned 30 deg** about the vertical (was 1.6 x 1.8 x 1.0); 7.0 below the hinge; bottom 0.096 above the felt. | Hinge (22, 8.996, -38.5) (was 8.96). Axis +Z. angle(t) = 30 * sin(360 t / 5 s) deg (was +-35 / 4 s). |
| `fbx/h9_pendulum_root_beam.fbx` | 1,650 | The same beam, placed at the new hinge y 8.996. | Static. |
| `fbx/firefly_ring_entry.fbx` | 2,164 | Glow disc r **0.45** (was 0.55) = the Round-7 trigger radius. | Static. |
| `heart_lantern_cluster` | 6,536 | **No longer placed** (props.md: replaced by the 3 hanging amber lanterns). Remove it from the H9 build; the FBX is kept. | - |

### 3. Placements

The instances are in `manifest.dressing.holes.H7/H8/H9.instances[]`:
- role `hang` (H9): `hanging=True`, `anchor = amber_lantern_k`, and `world_pos.y` = the lantern origin, NOT the ground. The
  origin is 0.09 above the tassel tip, which sits at the anchor y 7.2.
- role `rail` (H7/H8): `side`, `wall`, `seq` and `light_id`.

They are also merged into the re-exported dressing groups:
- **Content changed:** `fbx/dressing_h06_a.fbx` (H6 lost ground cover; see the table below), `fbx/dressing_h07_a.fbx`,
  `fbx/dressing_h08_a.fbx`, `fbx/dressing_h09_a.fbx`.
- All other `dressing_hNN_*` files were re-exported with identical content.

Per-instance import: `Model:PivotTo(CFrame.new(world_pos) * CFrame.Angles(0, math.rad(world_yaw), 0))`, then
`Model:ScaleTo(scale)`.

| Instance (light_id) | Prop | Scale | Hole-local pos / yaw | World pos / yaw | Wall / anchor | Gap before |
|---|---|---|---|---|---|---|
| H7_rail_left_03 | rail_lantern_crook | 1 | [-7.25, -3.834, -43.65] / 270 | [47.25, 22.166, 15.65] / 90 | rail12 | 12.63 |
| H7_rail_left_04 | rail_lantern_crook | 1 | [0.75, -2.486, -45.15] / 270 | [39.25, 23.514, 17.15] / 90 | rail12 |  |
| H7_rail_right_02 | rail_lantern_crook | 1 | [13.65, -2.783, -18.25] / 180 | [26.35, 23.217, -9.75] / 0 | rail9 |  |
| H7_rail_right_03 | rail_lantern_crook | 1 | [15.15, -2.133, -36.25] / 180 | [24.85, 23.867, 8.25] / 0 | rail13 | 18.06 |
| H7_rail_right_04 | rail_lantern_crook | 1 | [4.75, -2.674, -43.65] / 270 | [35.25, 23.326, 15.65] / 90 | rail12 |  |
| H7_rail_left_01 | rail_lantern_stake | 1 | [-5.75, -1.008, -12.35] / 90 | [45.75, 24.992, -15.65] / 270 | rail4 |  |
| H7_rail_left_02 | rail_lantern_stake | 1 | [-9.65, -2.983, -29.25] / 0 | [49.65, 23.017, 1.25] / 180 | rail11 | 17.34 |
| H7_rail_right_01 | rail_lantern_stake | 1 | [5.75, -1.392, -12.35] / 90 | [34.25, 24.608, -15.65] / 270 | rail10 |  |
| H8_rail_left_01 | rail_lantern_crook | 1 | [-7.25, -0.44, 1.25] / 0 | [-2.75, 35.56, -25.25] / 180 | rail3 |  |
| H8_rail_left_02 | rail_lantern_crook | 1 | [-10.75, -0.438, -4.25] / 90 | [0.75, 35.562, -19.75] / 270 | rail4 |  |
| H8_rail_left_03 | rail_lantern_crook | 1 | [-23.75, -0.564, -24.25] / 0 | [13.75, 35.436, 0.25] / 180 | rail5 | 21.1 |
| H8_rail_left_04 | rail_lantern_crook | 1 | [-24.75, -0.123, -34.25] / 0 | [14.75, 35.877, 10.25] / 180 | rail5 |  |
| H8_rail_left_05 | rail_lantern_crook | 1 | [-19.75, 0.154, -46.75] / 270 | [9.75, 36.154, 22.75] / 90 | rail6 |  |
| H8_rail_left_06 | rail_lantern_crook | 1 | [-9.75, 0.36, -46.75] / 270 | [-0.25, 36.36, 22.75] / 90 | rail6 |  |
| H8_rail_left_07 | rail_lantern_crook | 1 | [-1.75, 0.368, -52.75] / 270 | [-8.25, 36.368, 28.75] / 90 | rail8 |  |
| H8_rail_left_08 | rail_lantern_crook | 1 | [8.25, 0.459, -52.75] / 270 | [-18.25, 36.459, 28.75] / 90 | rail8 |  |
| H8_rail_right_01 | rail_lantern_crook | 1 | [7.25, -0.359, 2.25] / 180 | [-17.25, 35.641, -26.25] / 0 | rail17 |  |
| H8_rail_right_02 | rail_lantern_crook | 1 | [9.25, -0.341, -4.25] / 90 | [-19.25, 35.659, -19.75] / 270 | rail16 |  |
| H8_rail_right_03 | rail_lantern_crook | 1 | [9.25, -0.298, -18.75] / 270 | [-19.25, 35.702, -5.25] / 90 | rail14 |  |
| H8_rail_right_04 | rail_lantern_crook | 1 | [-2.25, -0.31, -18.75] / 270 | [-7.75, 35.69, -5.25] / 90 | rail14 |  |
| H8_rail_right_05 | rail_lantern_crook | 1 | [-9.25, -0.397, -19.75] / 180 | [-0.75, 35.603, -4.25] / 0 | rail13 |  |
| H8_rail_right_06 | rail_lantern_crook | 1 | [-9.25, 0.401, -29.75] / 180 | [-0.75, 36.401, 5.75] / 0 | rail13 |  |
| H8_rail_right_07 | rail_lantern_crook | 1 | [-1.25, 0.301, -27.75] / 90 | [-8.75, 36.301, 3.75] / 270 | rail10 |  |
| H9_hanging_lantern_1 | lantern_large_hanging | 0.85 | [18.5, 7.29, -47.5] / 0 | [-91.057, 47.29, -7.76] / 62.3 | amber_lantern_1 |  |
| H9_hanging_lantern_2 | lantern_large_hanging | 0.85 | [28.5, 7.29, -46.5] / 0 | [-85.523, 47.29, -16.149] / 62.3 | amber_lantern_2 |  |
| H9_hanging_lantern_3 | lantern_large_hanging | 0.85 | [20.0, 7.29, -51.5] / 0 | [-93.901, 47.29, -10.947] / 62.3 | amber_lantern_3 |  |

### 4. Lights: `manifest.lights[]` (38 PointLights, Shadows = false)

For each entry:
- `Color = Color3.fromRGB(color3)`, plus `Range` and `Brightness` from the entry.
- Parent the light to the Neon part named in `parent`, or to an invisible, non-colliding Attachment at `world_pos`.

What the 38 are:
- **Lanterns (26):** amber **Color3(255, 169, 87)** (#FFA957, ~2700K), each at the lantern's glow-core centre.
  - 3 H9 hanging lanterns: Range 16, Brightness 3.
  - 23 rail lanterns: Range 10, Brightness 1.2.
- **H8 glow (12):** 5 `firefly_glow_low` (#D8FF6A, Range 8, Brightness 1.6) and 7 `shroom_glow` (#7FE3D0, Range 8,
  Brightness 1.4).

The new lanterns' glow cores are **not** in the per-hole `lights[]` / `lights_world[]`, so add only these. Fitcheck
confirms there are no doubles.

| Light id | Kind | Hole-local pos | World pos | Colour | Range | Brightness |
|---|---|---|---|---|---|---|
| H9_hanging_lantern_1 | hanging_lantern | [18.5, 8.06, -47.5] | [-91.06, 48.06, -7.76] | #FFA957 (255, 169, 87) | 16 | 3 |
| H9_hanging_lantern_2 | hanging_lantern | [28.5, 8.06, -46.5] | [-85.52, 48.06, -16.15] | #FFA957 (255, 169, 87) | 16 | 3 |
| H9_hanging_lantern_3 | hanging_lantern | [20.0, 8.06, -51.5] | [-93.9, 48.06, -10.95] | #FFA957 (255, 169, 87) | 16 | 3 |
| H7_rail_left_01 | rail_lantern | [-5.75, 0.49, -12.35] | [45.75, 26.49, -15.65] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H7_rail_left_02 | rail_lantern | [-9.65, -1.49, -29.25] | [49.65, 24.51, 1.25] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H7_rail_left_03 | rail_lantern | [-7.25, 1.77, -41.65] | [47.25, 27.77, 13.65] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H7_rail_left_04 | rail_lantern | [0.75, 3.12, -43.15] | [39.25, 29.12, 15.15] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H7_rail_right_01 | rail_lantern | [5.75, 0.1, -12.35] | [34.25, 26.1, -15.65] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H7_rail_right_02 | rail_lantern | [11.65, 2.82, -18.25] | [28.35, 28.82, -9.75] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H7_rail_right_03 | rail_lantern | [13.15, 3.47, -36.25] | [26.85, 29.47, 8.25] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H7_rail_right_04 | rail_lantern | [4.75, 2.93, -41.65] | [35.25, 28.93, 13.65] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_left_01 | rail_lantern | [-5.25, 5.16, 1.25] | [-4.75, 41.16, -25.25] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_left_02 | rail_lantern | [-10.75, 5.16, -6.25] | [0.75, 41.16, -17.75] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_left_03 | rail_lantern | [-21.75, 5.04, -24.25] | [11.75, 41.04, 0.25] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_left_04 | rail_lantern | [-22.75, 5.48, -34.25] | [12.75, 41.48, 10.25] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_left_05 | rail_lantern | [-19.75, 5.76, -44.75] | [9.75, 41.76, 20.75] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_left_06 | rail_lantern | [-9.75, 5.96, -44.75] | [-0.25, 41.96, 20.75] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_left_07 | rail_lantern | [-1.75, 5.97, -50.75] | [-8.25, 41.97, 26.75] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_left_08 | rail_lantern | [8.25, 6.06, -50.75] | [-18.25, 42.06, 26.75] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_right_01 | rail_lantern | [5.25, 5.24, 2.25] | [-15.25, 41.24, -26.25] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_right_02 | rail_lantern | [9.25, 5.26, -6.25] | [-19.25, 41.26, -17.75] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_right_03 | rail_lantern | [9.25, 5.3, -16.75] | [-19.25, 41.3, -7.25] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_right_04 | rail_lantern | [-2.25, 5.29, -16.75] | [-7.75, 41.29, -7.25] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_right_05 | rail_lantern | [-11.25, 5.21, -19.75] | [1.25, 41.21, -4.25] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_right_06 | rail_lantern | [-11.25, 6.0, -29.75] | [1.25, 42.0, 5.75] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_rail_right_07 | rail_lantern | [-1.25, 5.9, -29.75] | [-8.75, 41.9, 5.75] | #FFA957 (255, 169, 87) | 10 | 1.2 |
| H8_shroom_glow_01 | shroom_glow | [12.75, 0.62, -14.27] | [-22.75, 36.62, -9.73] | #7FE3D0 (127, 227, 208) | 8 | 1.4 |
| H8_shroom_glow_02 | shroom_glow | [12.24, 0.55, -11.22] | [-22.24, 36.55, -12.78] | #7FE3D0 (127, 227, 208) | 8 | 1.4 |
| H8_shroom_glow_03 | shroom_glow | [15.19, 1.22, -13.55] | [-25.19, 37.22, -10.45] | #7FE3D0 (127, 227, 208) | 8 | 1.4 |
| H8_firefly_glow_low_04 | firefly_glow_low | [5.6, 0.79, -19.35] | [-15.6, 36.79, -4.65] | #D8FF6A (216, 255, 106) | 8 | 1.6 |
| H8_firefly_glow_low_05 | firefly_glow_low | [6.89, 0.64, -17.72] | [-16.89, 36.64, -6.28] | #D8FF6A (216, 255, 106) | 8 | 1.6 |
| H8_firefly_glow_low_06 | firefly_glow_low | [2.58, 0.64, -17.65] | [-12.58, 36.64, -6.35] | #D8FF6A (216, 255, 106) | 8 | 1.6 |
| H8_shroom_glow_07 | shroom_glow | [4.28, 0.56, -18.21] | [-14.28, 36.56, -5.79] | #7FE3D0 (127, 227, 208) | 8 | 1.4 |
| H8_firefly_glow_low_08 | firefly_glow_low | [6.17, 0.59, -0.66] | [-16.17, 36.59, -23.34] | #D8FF6A (216, 255, 106) | 8 | 1.6 |
| H8_shroom_glow_09 | shroom_glow | [7.83, 0.58, -0.83] | [-17.83, 36.58, -23.17] | #7FE3D0 (127, 227, 208) | 8 | 1.4 |
| H8_shroom_glow_10 | shroom_glow | [-9.38, 0.78, -26.06] | [-0.62, 36.78, 2.06] | #7FE3D0 (127, 227, 208) | 8 | 1.4 |
| H8_shroom_glow_11 | shroom_glow | [-3.38, 1.23, -28.22] | [-6.62, 37.23, 4.22] | #7FE3D0 (127, 227, 208) | 8 | 1.4 |
| H8_firefly_glow_low_12 | firefly_glow_low | [-3.27, 1.26, -24.6] | [-6.73, 37.26, 0.6] | #D8FF6A (216, 255, 106) | 8 | 1.6 |

**Changed existing lights:**
- `dressing.holes.H8.spot_lights` `H8_firefly_swarm_1_firefly_glow` and `H8_firefly_swarm_2_firefly_glow`:
  Brightness **2.0 -> 3.5**, Range **12 -> 14**. Same positions: (13.55, 2.32, -17.42) and (-5.24, 2.47, -26.3)
  hole-local.
- The H9 pendulum spot (beside the hinge) follows the new hinge y automatically.

### 5. Emissive changes (H8 glow) and textures

`manifest.emissive` covers the Neon materials `Firefly` (#D8FF6A) and `ShroomGlow` (#7FE3D0):
- **Preview emission:** Firefly **4 -> 8**, ShroomGlow **3 -> 6**. The first try, 10 / 8, blew the shroom caps out to
  white.
- **In Studio:** keep Neon and the same Color. Add a SurfaceAppearance to every `*__Firefly` / `*__ShroomGlow`
  MeshPart:
  - `ColorMap` = `textures/firefly_emissive.png` / `textures/shroomglow_emissive.png` (new);
  - `EmissiveMaskContent` = `textures/glow_emissive_mask.png` (new);
  - `EmissiveStrength` = 6 (Firefly) / 5 (ShroomGlow);
  - `EmissiveTint` = the colour.
  - If SurfaceAppearance emissive is unavailable, rely on the raised spot_lights plus the new glow lights.
- **Props using these materials, re-exported** (geometry and colours unchanged apart from the ring disc above):
  - H8 props: `firefly_cluster_low`, `firefly_swarm`, `glow_shroom_patch`, `glow_root_arch`, `glowing_mushrooms`,
    `firefly_ring_entry`, `firefly_ring_exit`, `root_arch_large`, `h8_door_pocket`;
  - the same materials elsewhere: `h2_chute_arrow_decal`, `h5_respawn_stone`, `h9_tunnel_dip_trim`. Their emission
    went up too.

## Dressing per hole (pass 7b -> pass 8, `stats.pass8_vs_pass7b`)

The lanterns are placed first, so the zero-sum near-field budget (<= 34,000) trims the lowest-priority ground cover in
the shared H6/H7/H8 near fields.

| Hole | Instances p7b -> p8 | Lanterns (tris) | Removed or moved > 4.5 | Own tris p7b -> p8 | Near-field p7b -> p8 |
|---|---|---|---|---|---|
| H1 | 48 -> 48 | 0 (0) | - | 16,860 -> 16,860 | 32,308 -> 32,308 |
| H2 | 42 -> 42 | 0 (0) | - | 18,354 -> 18,354 | 33,998 -> 33,998 |
| H3 | 43 -> 43 | 0 (0) | - | 18,920 -> 18,920 | 32,204 -> 32,204 |
| H4 | 37 -> 37 | 0 (0) | - | 16,862 -> 16,862 | 33,536 -> 33,536 |
| H5 | 34 -> 34 | 0 (0) | - | 19,406 -> 19,406 | 26,490 -> 24,002 |
| H6 | 17 -> 10 | 0 (0) | fern_clump_large (mid, 384 tris), fern_clump_large (mid, 384 tris), mossy_boulder (mid, 216 tris), red_leaf_bush (mid, 320 tris), leaf_pile (near, 464 tris), orange_leaf_bush (near, 400 tris), red_leaf_bush (near, 320 tris) | 10,168 -> 7,680 | 32,424 -> 31,296 |
| H7 | 26 -> 32 | 8 (1,616) | maple_tree_tall (tree, 1348 tris), grass_tuft (near, 224 tris), red_leaf_bush (near, 320 tris) | 12,546 -> 13,054 | 33,834 -> 33,918 |
| H8 | 26 -> 37 | 15 (3,300) | golden_birch_tree (tree, 784 tris), maple_tree_tall (tree, 1348 tris), fern_clump (near, 228 tris), grass_tuft (near, 224 tris), firefly_cluster_low (hollow, 128 tris), glow_shroom_patch (hollow, 214 tris) | 13,864 -> 14,580 | 33,962 -> 33,858 |
| H9 | 30 -> 30 | 3 (1,152) | gold_leaf_bush (near, 320 tris), grass_tuft (near, 224 tris), leaf_pile (near, 464 tris), red_leaf_bush (near, 320 tris) | 16,848 -> 17,932 | 29,704 -> 31,412 |

- **H6 pays:** 17 -> 10 instances (-2,488 tris). H7's near field (33,918) covers all of H8 and most of H6.
- H7's refill also re-added a golden birch.
- H1-H5 are unchanged (H5's near-field total moved only with H6).

## Placement rules and checks (`_src/fitcheck_pass8.py`)

**H9 hanging lanterns:**
- Placed on the holes.json anchors `amber_lantern_1..3` (centre x/z and bottom y within 0.05; size ~1.2 x 1.8 x 1.2
  within 0.2).
- Bottom 8.0 above the heart felt (checked 7..9), centre over the corridor / chamber / heart felt.
- Clear of every keep-out, including the pendulum sweep and the root beam.
- An amber light with Range 16 at each centre.
- `heart_lantern_cluster` is no longer placed.
- History:
  1. They first went corridor -> chamber -> heart, evenly spaced, as the brief asked.
  2. Render iteration: scale 1.5, because they read small.
  3. The addendum then moved them onto the props.md anchors.

**Rail lanterns:**
- About every 10 studs outside both rails: on the H7 lower tiers (rail4/5/6/11/12 left, rail10/9/13/12 right) and on
  the whole H8 loop.
- **Rail clip:** none; exact 2D triangle-vs-wall gap >= 0.25.
- **Felt:** none over any felt of any hole; exact.
- **Visibility:** a stake's lantern top is >= the rail top + 0.2; a crook's lantern centre is >= the rail top + 0.8.
  This is why H8 uses crooks, and why H7 falls back to the crook where the ground drops.
- **Spacing:** consecutive pairs are 8..12 studs. Pairs further apart are allowed only where every spot 8..12 studs on
  is blocked; fitcheck re-tests each skipped spot independently:
  - H7 left 17.3 (water, 20 spots) and 12.6 (water, 56 spots);
  - H7 right 18.1 (walkway, 82 spots);
  - H8 left 21.1 (hidden below the rail top / walkway / slope, 27 spots).
- The tall-prop rule, keep-outs, world pieces and the budget all apply.

**`lights[]`:** one entry per lantern / glow prop, ids unique, local == world, amber, at the lantern centre within
0.25.

**Emissive:** >= 2x pass 7, plus `manifest.emissive` and its textures.

**Negative tests (all flagged):**
- a hanging lantern 5 above the felt;
- a hanging lantern over the H9 lane;
- a hanging lantern 1 stud off its anchor;
- a rail lantern on its rail, and over the felt;
- a gap window containing a free spot;
- a rail lantern hidden below a taller rail;
- spacing 15 / 6.5;
- a missing or white light.

**Round-7 moving-part checks** now read their numbers from holes.json:
- motion == holes.json;
- each prop inside the union of its blockers (log with its 45-deg end blockers, the yawed pendulum bob);
- bob bottom == blocker bottom;
- the swing envelope uses the yawed bob;
- the door slides into a pocket at every end that crosses a rail line;
- ring disc = trigger radius.

## Code / files

- **New:**
  - `_src/props_pass8.py`, `_src/fitcheck_pass8.py`, `_src/pass8_readme.md`, `_src/pass8_progress.md`, this file;
  - `_src/fitcheck_pass8_validated.txt`;
  - the textures above.
- **Changed:**
  - `_src/props_moving.py`: log / door / pendulum sizes and motion come from holes.json;
  - `_src/props_pass6.py`: pockets only at crossing ends, depth from the travel; beam note;
  - `_src/props_hero.py`: the ring disc uses the trigger radius; heart_lantern_cluster is unplaced;
  - `_src/dressing_world.py`: pass-8 block (anchors, rail chains), roles `hang` / `rail`, `manifest.lights` /
    `lights_note` / `emissive`, `stats.pass8_vs_pass7b`, firefly spot brightness;
  - `_src/lglib.py`: emission;
  - `_src/textures.py`: `glow_emissive()`;
  - `_src/fitcheck.py` and `_src/fitcheck_pass6.py`: data-driven moving-part checks, hanging-lantern exemptions;
  - `_src/dressing_lib.py`: the `LG_HOLES_JSON` override for validation runs;
  - `_src/world_scene.py`: renders `manifest.lights[]`;
  - `_src/build_all.py`: keeps `lights` / `lights_note` / `emissive`; imports props_pass8;
  - `_src/make_docs.py`, `_src/tee_sheet.py`.
- `lantern_grove_props.blend` was NOT rebuilt (no full `build.sh` this pass). All FBX are current.

## Open issues

1. **H6 is thin: 10 dressing instances** (17 in pass 7b, 25 in pass 5). The H7 near field binds; it holds all of H8 and
   most of H6. The levers:
   - raise `NEAR_BUDGET` above 34k if Quest profiling allows;
   - drop H7's refill birch or H8's far trees;
   - use cheaper rail lanterns (the crook is 220 tris).
2. **Rail-lantern gaps** (verified blocked):
   - H7 left skips most of rail5/6/11 (the stream);
   - H7 right skips rail13 (a walkway);
   - H8 right stops at the green's south rail (rail10): rail9 / east of the green is blocked by roots, heroes and the
     tall-prop rule;
   - H8 left skips the junction's SW bank corner.
3. **Light count on Quest.** H8 has 15 rail + 12 glow + 4 spot PointLights, plus the glow cores. All are shadowless
   and short-range. Drop `shroom_glow` / `firefly_glow_low` first if needed.
4. **The H9 hanging cords end at y ~16 in open air.** The hollow is open for 40+ studs above, and nothing is there to
   tie to now that the cluster's crossbeams are gone. If it reads odd in VR, lengthen the cord (`CORD_L` in
   `props_pass8.py`) so it fades into the dark.
5. **Preview brightness:** preview watts = 700 x Brightness x (Range/16)^2. Tune the Roblox Brightness values in
   Studio.
6. Carry-overs from pass 7: holes.json flag sizes, static fireflies (a bob/flicker script), the felt normal map in
   Studio.
