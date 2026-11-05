# Lantern Grove props: pass 5 summary (2026-10-10): Playtest Bot review

The Playtest Bot review asked for two things:
- **(11)** H8 (under the root arch) and H9 (inside the tree) were too dark: felt, rails and floor blended together.
- **(12)** H3, H4 and H6 were cluttered near the lanes, and the moving parts did not stand out.

All tasks are done:
- `fitcheck.py` **ALL PASS** (139 checks, 19 of them new).
- The 5 requested tee views were re-rendered at 32 spp after one iteration. The other 4 tee views and all 9 top views
  were re-rendered too, so `tee_contact_sheet.png` is all pass 5.
- holes.json and world.json were only read.

## Changes

### 11) Dark holes H8 / H9
- **Brighter felt variant**: new `FeltBright` material (`#6CBF4C`, Fabric) with `textures/felt_bright.png`. It has
  the same pattern as felt.png, lifted about 45% in value: mean rgb 63/135/54 -> 102/183/74.
  - It also uses `felt_normal.png` and the velvet sheen.
  - Felt brightness measured on the tee renders:
    - H9: 53/93/41 (pass 4) -> 107/166/63;
    - H8: 90/147/67 -> 112/178/75.
- **Light edge trim**: new rail kit `rail_straight_4_trim`, `rail_straight_2_trim` and `rail_end_post_trim`. It has
  light `TrimStone` blocks (`#DDD3BE`) and a cream `TrimCream` cap (`#F6EBD0`).
  - Same 0.5 x 1.0 profile and origin as the base kit, so it drops onto the same walls.
- **Per-hole skins**: `_src/hole_skins.py` -> `manifest.json > hole_skins`. It gives each hole's felt material and
  texture, plus its rail-kit props, block/cap materials and colours. The preview scene uses it.
- **Glowing lanterns**: new prop `cup_lantern_stake` (0.61 x 1.92 x 0.58, 400 tris, PaperOrange lantern + Neon core).
  It is under the 2-stud "tall" line, so it may stand right outside a rail.
  - Placed first, as dressing role `accent`:
    - 2 beside the H8 cup (4.5 / 5.5 studs from it);
    - 2 beside the H9 cup (5.75 / 6.5);
    - 2 either side of the H9 root gate (5.25 each).
  - Each instance has `marks` (cup / root_gate) and `dist_to_target`.
  - All go through the full clash test (felt + 1.25, walls, sweeps, walkways, world occupancy, the H9 inside-the-hollow
    rule).
- **Light spots**: `manifest.dressing.holes.H8/H9.spot_lights[]`. Each entry has `id`, `over`, `kind`, `pos`
  (hole-local), `world_pos`, `color`, `range`, `brightness` and `shadows=false`.
  - Each spot hangs 7 studs above its target's felt (9 over the H9 heart, to clear a world piece). That is above the
    6.5 play clearance, so the host part never enters a keep-out. It is shifted sideways by up to 3 studs if a keep-out
    or world piece is in the way.

  | Id | Over | Colour | Range | Brightness |
  |---|---|---|---|---|
  | H8_root_door_moving_part | H8 door | #FFE6B8 | 16 | 2.5 |
  | H8_cup_cup_pool | H8 cup | #FFC873 | 12 | 2.0 |
  | H9_root_gate_moving_part | H9 gate | #FFE6B8 | 16 | 2.5 |
  | H9_lantern_bar_moving_part | H9 lantern bar (shift 1) | #FFE6B8 | 16 | 2.5 |
  | H9_cup_cup_pool | H9 cup (shift 3) | #FFC873 | 12 | 2.0 |
  | H9_lane / landing / chamber / heart _lane_fill | H9 felt areas (added in iteration 2) | #FFE2B0 | 18 | 1.5 |

### 12) Lane clutter, moving parts, H6 rail
- **Rule**: every dressing prop taller than 2 studs keeps its footprint, and all its geometry below base + 5 (eye
  height), at least **3 studs** (horizontal) from every collision wall of every hole. That covers rails, bank backings,
  boards and deflectors.
  - Enforced in `dressing_world.py` (`tall_rail_clear`; reason `tall_near_rail`). A failing instance is nudged within
    its role's radius, or removed.
  - The lantern-hook refill moved from 2-3.2 to 4-6.5 studs from the felt.
- **Fitcheck**: new per-hole check. It rebuilds the prop geometry from the generators, so it doesn't reuse
  dressing_world's templates, and measures point-to-wall-rectangle distance with its own code. 81 tall instances
  were checked.
  - Negative tests: a maple tree and a lantern hook pair 2 studs outside an H3 rail are flagged.
  - Positive control: a `cup_lantern_stake` at the same spot is allowed.
- **Moving-part colour scheme**: new `MoveRed` (`#D3362A`) and `MoveCream` (`#FFF2D8`), SmoothPlastic bands:
  - H4 spinner: red arms with 6 cream bands, cream puffballs;
  - H6 wheel: red paddles with 5 cream bands, cream arms;
  - H7 log: red body, 3 cream bands, cream end caps;
  - H8 door: alternating red/cream planks;
  - H9 gate: alternating red/cream roots, cream cross-ties;
  - H9 bar: red beam, 5 cream bands, cream upper arm.

  Geometry, pivots and bboxes are unchanged, so the blocker-fit checks and the moving-sweep keep-outs are unchanged.
  The fitcheck checks that all 6 parts carry both colours.
- **H6 rail variant**: `rail_straight_4_mill`, `rail_straight_2_mill` and `rail_end_post_mill`. Dark blue-grey
  `MillSlate` blocks (`#4F5866`, slate texture), with a painted `MillBlue` cap (`#2F6F8F`).

### Preview fix found while iterating
- `world_scene.py` tilted every **z-axis felt slope the wrong way** (pass-4 preview bug). holes.json `rise` is the
  height at the +axis end minus the -axis end, and Roblox +Z = Blender -Y.
  - This made the H9 lane look like separate slabs, with the floor showing between them. It also affected H2, H7 and
    H8 c2.
  - Preview only: the collision/keep-out code uses felt_top and was not affected.

## Iterations
1. **24 spp**:
   - H3/H4/H6: lanes clear; the red-cream parts and the blue H6 rail read well.
   - H8: good.
   - H9: still dark, and its lane looked broken.
   - Fixes:
     - slope sign;
     - preview spot power 160 -> 700 W per unit of Brightness;
     - 4 H9 lane-fill spots.
2. **32 spp** (final): H9 reads with a continuous bright lane and cream rails against the leaf floor. H8, H3, H4 and H6
   are fine.

## Counts per hole

"Pass-4 tall < 3 from a rail" is the number of pass-4 instances that break the new rule. "Moved back" means the same
prop is now within 12 studs of its old spot. "Rule hits" are the seed instances whose first failing test is now
`tall_near_rail`, either removed or nudged in the pass-5 run.
- Some of the removed ones were budget-removed in pass 4 anyway.
- Ground cover and the budget re-flow differ slightly as a result.

| Hole | Pass-4 tall < 3 from a rail | Moved back | Removed | Rule hits: removed / nudged | 3D + cards p4 -> p5 | Own tris p4 -> p5 | Near-field tris p4 -> p5 | Cup/gate lanterns | Spots |
|---|---|---|---|---|---|---|---|---|---|
| H1 | 7 | 5 | 2 | 4 / 6 | 26+22 -> 27+21 | 17,304 -> 16,860 | 33,102 -> 32,308 | - | - |
| H2 | 5 | 4 | 1 | 6 / 6 | 21+25 -> 22+20 | 17,416 -> 18,354 | 33,516 -> 33,998 | - | - |
| H3 | 6 | 6 | 0 | 5 / 6 | 29+14 -> 29+14 | 18,920 -> 18,920 | 32,692 -> 32,204 | - | - |
| H4 | 6 | 6 | 0 | 3 / 5 | 26+12 -> 24+13 | 17,326 -> 16,862 | 34,000 -> 33,536 | - | - |
| H5 | 7 | 7 | 0 | 3 / 7 | 27+7 -> 27+7 | 19,406 -> 19,406 | 28,098 -> 29,958 | - | - |
| H6 | 4 | 3 | 1 | 9 / 4 | 20+1 -> 24+1 | 12,932 -> 13,636 | 33,448 -> 31,392 | - | - |
| H7 | 7 | 5 | 2 | 15 / 5 | 13+0 -> 13+0 | 10,414 -> 9,002 | 33,830 -> 33,922 | - | - |
| H8 | 4 | 3 | 1 | 6 / 4 | 13+0 -> 15+0 | 13,228 -> 14,028 | 33,918 -> 33,862 | 2 | 2 |
| H9 | 1 | 1 | 0 | 0 / 1 | 22+0 -> 27+0 | 15,272 -> 17,016 | 25,222 -> 27,766 | 4 | 7 |
| **Total** | **47** | **40** | **7** | **51 / 44** | 197+81 -> 208+76 | **142,218 -> 144,084** | max 34,000 -> **33,998** | 6 | 9 |

- Pass-4 violators by prop: `lantern_hook_pair` 18, `lantern_string_poles` 10, maple/birch trees 15,
  `lantern_span_12` 2, `toadstool_cluster` 1 and `fern_clump_large` 1 (inside H9).
  - In other words, mostly lantern hooks/strings and framing trees hugging the rails.
- **Tris change**:
  - Dressing total: 142,218 -> 144,084 (+1,866: 6 cup lanterns = 2,400, offset by the re-flow).
  - Near-field budget: still <= 34,000 for every hole.
  - Moving parts: H4 2,226 -> 2,314, H6 1,468 -> 1,492, H7 704 -> 812, H9 bar 1,046 -> 1,058 (H8 door and H9 gate
    unchanged).
  - New props: trim/mill rail kit 88-132 each, cup lantern 400.

## Files
- **New**:
  - `_src/hole_skins.py`, `_src/pass5_progress.md`, this file;
  - `_src/manifest_before_pass5.json` (backup / "before" state);
  - `_src/fitcheck_pass5_validated.txt` (ALL PASS, 139 checks);
  - `_src/fitcheck_vs_round5_wip.txt` (the same checks against the in-progress Round-5 holes.json: 6 FAILs in H8/H9);
  - `textures/felt_bright.png`;
  - `fbx/rail_straight_4_trim.fbx`, `rail_straight_2_trim.fbx`, `rail_end_post_trim.fbx`;
  - `fbx/rail_straight_4_mill.fbx`, `rail_straight_2_mill.fbx`, `rail_end_post_mill.fbx`;
  - `fbx/cup_lantern_stake.fbx`, plus their `previews/*_{eye,34}.png`.
- **Re-exported**:
  - `fbx/h4_carousel_bar.fbx`, `h6_mill_wheel.fbx`, `h7_floating_log.fbx`, `h8_root_door.fbx`,
    `h9_root_portcullis.fbx`, `h9_lantern_bar.fbx` (and their previews);
  - all `fbx/dressing_hNN_*.fbx` (every hole's layout changed under the rule).
- **Changed code**:
  - `lglib.py` (7 materials, TEX, felt sheen for FeltBright);
  - `textures.py`, `props_moving.py`, `props_dressing.py`, `registry.py` (manifest hole_skins);
  - `dressing_world.py` (rule, accents, spot_lights, pass-5 stats, hole_skins);
  - `fitcheck.py`, `world_scene.py` (per-hole felt/rails, spot lights, slope fix);
  - `assembly_world.py` (`--spot-w`; `--holes` already renders only the listed holes);
  - `make_docs.py` (pass-5 README section), `tee_sheet.py`, `readme_extra.md`.
- **Data**:
  - `manifest.json`: new props + materials; `hole_skins`; dressing positions/stats (`pass5_tall_near_rail` per hole),
    `spot_lights`, `lights`/`lights_world` (now incl. the cup lantern cores), and the `tall_near_rail` rule.
  - `README.md` regenerated; `_src/fitcheck.txt`.
- **Renders**:
  - `previews/assembly_h0{1..9}_tee.png`, `previews/assembly_h0{1..9}_top.png`, `tee_contact_sheet.png`.
- **Skill**: `.agents/skills/blender-asset-pipeline/SKILL.md` gained a VR-readability lesson.

## Open issues
- **holes.json changed under this pass (most important)**: a parallel Round-5 design agent (playtest notes 6-10,
  editing via `tools/build_holes.py`) rewrote `../holes.json` during this pass (latest mtime 13:10). Its changes:
  - H4 spinner blockers shortened;
  - H8 felt/cup moved: cup z -43.5 -> -34.5, plus a back-wall bank;
  - H9 lantern bar replaced by a `lantern_pendulum`;
  - H7 log range changed.

  All pass-5 placement, spots and the ALL PASS fitcheck (`_src/fitcheck.txt` = `_src/fitcheck_pass5_validated.txt`)
  were computed against holes.json as of about 12:45-12:53.

  Re-running the (now data-driven) fitcheck against the in-progress Round-5 file gives **6 FAILs, all H8/H9**
  (`_src/fitcheck_vs_round5_wip.txt`):
  - H8 dressing now overlaps the moved felt/walls (groups a-c);
  - an H8 string-pole pair is 2 studs from a new rail;
  - the H8 cup spot is 10.9 from the new cup;
  - the H9 `lantern_bar` spot has no target.

  **When Round 5 is final**, rebuild in this order:
  1. rebuild the moving-part props for the new specs (pendulum, H4 arms, H7 log: keep the MoveRed/MoveCream scheme);
  2. `blender -b -P _src/dressing_world.py` (spots/accents are now data-driven: one spot per moving part + cup);
  3. `fitcheck.py`;
  4. `assembly_world.py --views tee,top`;
  5. `tee_sheet.py`, `make_docs.py`.

  The scene for the H1/H2/H5/H7 tee renders (about 13:02) and the top views (about 13:05) may already include some
  Round-5 geometry.
- After the ALL PASS run, `fitcheck.py` / `dressing_world.py` were made data-driven: no hard-coded `lantern_bar` /
  `root_door` ids, missing targets are reported instead of crashing, and pendulum spots pool over the felt under the
  pivot. The checked rules are the same.
- **Preview vs Roblox light units**: preview spots use 700 W per unit of Roblox Brightness (range 16). Tune
  Brightness in Studio at night. If H9 glares with the 4 lane fills, drop them to Brightness 1.0 first.
- **H9 preview slabs**: the H9 bank1 overlay and the chamber slabs still show their side faces in the preview. That
  comes from preview felt boxes, not real geometry.
- **Not covered by the rule**: the lane-clearance rule covers dressing only. Hero props (H3/H4 mushroom houses, the
  H6 mill house), world lantern posts (`world.json` lanterns) and world pieces were not moved. The H3/H4 houses still
  sit close to the lanes, by design (concept art).
- **H7 is thin**: H7 lost most of its rail-side tall props (15 rule hits) and has 13 3D props. Its views lean on the
  valley world pieces. If it reads bare in Studio, add short ground cover (under 2 studs) by the rails.
- **Not rebuilt**: `lantern_grove_props.blend` (the combined .blend) is only written by a full `build.sh` run (about
  6 minutes), so it still has the pass-4 moving-part colours and lacks the 7 new props. `contact_sheet.png` was
  regenerated by make_docs and includes them. `assembly_hNN.png` (old pass-2 overviews) are still stale.
