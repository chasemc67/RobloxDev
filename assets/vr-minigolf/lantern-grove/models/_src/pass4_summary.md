# Lantern Grove props: pass 4 summary (2026-10-10): world-placed dressing, Quest budget, art fixes

The per-hole dressing (manifest.json > dressing) was laid out in pass 2 against holes.json's old flat layout. This
pass re-validates and re-places it in the real world (`../world/world.json` hole origin + yaw; holes.json
`world_offset`/`world_yaw` are ignored). It also cuts it to a Quest VR budget and folds in the art director review.
holes.json and world.json were only read.

## Results

- **1,502 seed instances -> 197 3D props + 81 card clumps.** 152 kept, 37 moved (nudged), 57 backdrop clumps
  converted to cards, 1,256 removed, 32 added (refill).
- **Dressing tris 1,264,612 -> 142,218 (-89%).**
- **Near-field tris per hole**: all dressing from any hole within 60 studs of that hole's felt. Before: 187k-451k.
  After: **25,222-34,000**, enforced at <= 34,000 (target "well under 40k").
- Of the 1,256 removals, **461 were geometric**: walkways/stairs, slope, the tree shell/roots, water, felt, rock
  faces, plus H9 instances outside the hollow or too tall for it. The other 795 were budget cuts, and those placements
  were otherwise valid.
- `fitcheck.py`: **ALL PASS** (120 checks, including 9 new negative tests).
- `world_fitcheck.py`: **ALL PASS** (37 checks, after adding the H9 interior glow part).

| Hole | Seed | Kept | Moved | Backdrop -> card | Removed | Added | Final 3D + cards | Own trees | Own tris before -> after | Near-field tris before -> after (all dressing within 60 studs) |
|---|---|---|---|---|---|---|---|---|---|---|
| H1 | 184 | 17 | 9 | 17 | 141 | 5 | 26 + 22 | 7 | 137,562 -> 17,304 | 247,140 -> **33,102** |
| H2 | 167 | 16 | 5 | 13 | 133 | 12 | 21 + 25 | 5 | 137,780 -> 17,416 | 243,748 -> **33,516** |
| H3 | 187 | 25 | 4 | 13 | 145 | 1 | 29 + 14 | 6 | 159,838 -> 18,920 | 218,208 -> **32,692** |
| H4 | 146 | 22 | 4 | 7 | 113 | 5 | 26 + 12 | 7 | 132,512 -> 17,326 | 249,190 -> **34,000** |
| H5 | 173 | 26 | 1 | 7 | 139 | 0 | 27 + 7 | 7 | 142,234 -> 19,406 | 187,348 -> **28,098** |
| H6 | 119 | 12 | 7 | 0 | 100 | 2 | 20 + 1 | 4 | 80,864 -> 12,932 | 323,026 -> **33,448** |
| H7 | 150 | 9 | 4 | 0 | 137 | 0 | 13 + 0 | 4 | 118,700 -> 10,414 | 355,798 -> **33,830** |
| H8 | 220 | 10 | 3 | 0 | 207 | 0 | 13 + 0 | 4 | 198,968 -> 13,228 | 451,262 -> **33,918** |
| H9 | 156 | 15 | 0 | 0 | 141 | 7 | 22 + 0 | 0 | 156,154 -> 15,272 | 297,518 -> **25,222** |
| **Total** | 1502 | 152 | 37 | 57 | 1256 | 32 | 197 + 81 | | 1,264,612 -> 142,218 | max **34,000** |

Removal reasons per hole (the first test that failed):

| Hole | Removed because | Moved because |
|---|---|---|
| H1 | budget:own_role_share 56, walkway/stairs 24, budget:near_field_tris 23, budget:heavy_small_prop 20, vista_sightline 8, card_too_close_to_felt 5, hero_prop 2, tee 1, slope 1, plaza/flume 1 | overlap 8, card_too_close_to_felt 4, walkway/stairs 3, vista_sightline 2, hero_prop 1, felt 1, lantern_post 1, plaza/flume 1, slope 1 |
| H2 | budget:own_role_share 58, budget:heavy_small_prop 25, budget:near_field_tris 23, walkway/stairs 17, card_too_close_to_felt 5, overlap 4, tee 1 | walkway/stairs 3, overlap 2, card_too_close_to_felt 1 |
| H3 | budget:near_field_tris 76, budget:own_role_share 23, walkway/stairs 13, card_too_close_to_felt 13, slope 12, rock_face 3, vista_sightline 3, felt 1, overlap 1 | overlap 4, slope 3, rock_face 2, card_too_close_to_felt 2, vista_sightline 2, hero_prop 1, felt 1 |
| H4 | budget:near_field_tris 45, budget:heavy_small_prop 37, slope 16, budget:own_role_share 8, walkway/stairs 5, budget:role_cap 1, rock_face 1 | slope 7, overlap 1 |
| H5 | budget:own_role_share 65, budget:heavy_small_prop 26, slope 14, water 13, walkway/stairs 8, vista_sightline 5, budget:role_cap 2, card_too_close_to_felt 2, overlap 2, rock_face 1, tee 1 | vista_sightline 3, slope 2, overlap 2, rock_face 1 |
| H6 | budget:near_field_tris 57, slope 13, card_too_close_to_felt 12, walkway/stairs 8, felt 4, budget:own_role_share 2, tee 2, overlap 2 | walkway/stairs 3, overlap 2, felt 1, hero_prop 1 |
| H7 | budget:near_field_tris 66, water 20, walkway/stairs 17, slope 17, felt 9, vista_sightline 5, card_too_close_to_felt 2, overlap 1 | walkway/stairs 3, slope 1 |
| H8 | budget:near_field_tris 73, budget:heavy_small_prop 46, card_too_close_to_felt 22, slope 21, vista_sightline 12, tree_shell 11, walkway/stairs 9, tree_roots 7, budget:own_role_share 4, felt 1, rock_face 1 | wall 1, walkway/stairs 1, slope 1 |
| H9 | outside_trunk 45, budget:heavy_small_prop 30, budget:near_field_tris 23, too_tall_in_trunk 15, slope 11, budget:own_role_share 6, vista_sightline 6, card_too_close_to_felt 5 | - |

Totals by reason: budget:near_field_tris 386, budget:own_role_share 222, budget:heavy_small_prop 184, slope 105, walkway/stairs 101, card_too_close_to_felt 66, outside_trunk 45, vista_sightline 39, water 33, felt 15, too_tall_in_trunk 15, tree_shell 11, overlap 10, tree_roots 7, rock_face 6, tee 5, budget:role_cap 3, hero_prop 2, plaza/flume 1.
How to read the reasons:
- Reasons are the first test that failed.
- `budget:heavy_small_prop` (more than 2 props over 900 tris per hole) and `budget:role_cap` are checked **before**
  the geometry tests.
- `budget:near_field_tris` and `budget:own_role_share` are checked **after** them, so those instances had a valid spot.
- `outside_trunk` / `too_tall_in_trunk`: H9 is played inside the hollow tree, so H9 dressing must stay inside the
  hollow and be at most 4.5 tall (as pass 2's cavity rule).
- `card_too_close_to_felt`: a card within 32 studs of any felt reads flat (found in the iteration-3 vista).
- `vista_sightline`: a card would block a protected view (iteration 4).

## What was done

1. **World transform + clash test** (`_src/dressing_world.py`, `_src/world_occ.py`,
   `world_fit.dressing_keepouts`).
   - Every seed instance goes through the world README formula.
   - Every prop **vertex**, then every **triangle** (exact SAT), is tested against:
     - all 9 holes: felt +1.25 up to felt top +6.5, walls, hazards, moving-part sweeps, teleports, tee pad + run-up,
       hero props;
     - every walkway/stair/landing segment (width/2 + 0.75, 6.5 high; 12 at the Heartwood Door);
     - the 54 lantern posts, the plazas/viewpoints and the mill flume.
   - World FBX geometry is tested through per-part height-interval maps on a 1-stud grid, built from the re-imported
     world FBX at their layout placements. This covers the tree shell, roots, interior, waterfalls, cliff kits,
     terrace rock faces, tower, dock, sister trees and tree line.
   - Hollow tree rule: non-H9 dressing stays outside trunk r + 1; H9 dressing stays inside r_inner - 0.3.
   - A failing instance is nudged first: same prop, yaw and role, rings of 12 directions, up to 2-12 studs by role.
     If no spot works, it is removed with a reason.
2. **Ground**.
   - Bilinear samples of `terrain-4stud.json` over the stored footprint (centre + 16 points per base).
   - Rejected if the spread is over 1.5 (small props, lantern poles), 3 (trees) or 3.5 (cards), or if the footprint
     touches a water cell.
   - Base y = min + 0.3 x spread - sink.
3. **Manifest**. Every instance now has:
   - `world_pos`, `world_yaw`, `terrain_y`, `footprint`, `ground_spread` and `status`
     (kept / moved / card_from_backdrop / added), plus `moved_by` / `moved_because` / `replaces`;
   - hole-local `pos` (y corrected to the same world height) and `yaw`.

   Each hole has `stats` (counts, reasons, tris before/after, near-field before/after), `removed[]`, `placement`,
   `lights[]` and `lights_world[]` (112 glow cores in total).

   `dressing.budgets` documents the near/far budgets. `dressing.totals` has the overall counts.
4. **FBX groups** (regenerated, old ones deleted).
   - `fbx/dressing_hNN_a..` hold the near-field 3D props, merged per material (repeated pieces become a few MeshParts),
     each file under 20k tris.
   - `fbx/dressing_hNN_cards.fbx` holds the cards.
   - **Origin convention = hole frame**: world.json origin rotated by its yaw, so place each file with
     `Model:PivotTo(holeRoot)`. This is documented in the manifest note and the README.
5. **Fitcheck** (`fitcheck.py`, pass-4 world dressing section). It re-imports every group, moves it to the world and
   checks each hole for:
   - exact SAT vs every keep-out;
   - world-piece occupancy;
   - the tree rule;
   - felt gap >= 1.25 and over-felt >= 6.5;
   - local <-> world consistency;
   - grounding per instance;
   - lights consistency;
   - FBX tri counts;
   - cards >= 32 from any felt and outside the protected vista sightlines;
   - near-field budget <= 34k.

   Negative tests (9), all flagged: a box on H1 felt, in the H6 mill-wheel sweep, on a stair flight and at a lantern post;
   a point in the trunk wall (occupancy and tree rule); an instance in Lantern Mere; a tree on a cliff edge; a card in
   the H1 tee -> tree sightline.
6. **Previews over the real world** (`_src/world_scene.py` + `_src/assembly_world.py`).
   - One preview scene holds:
     - the terrain-4stud terrain, water and apron;
     - all holes at their world placement, with textured felt, rail kits and heroes;
     - walkway ribbons and the lantern posts;
     - every world piece, including the hollow tree;
     - all dressing;
     - PointLights at the dressing lights, the H9 interior spots and the lantern posts.
   - From it come `previews/assembly_hNN_tee.png` (VR eye 5 studs, 72 deg) and `assembly_hNN_top.png` (hole-frame ortho
     cutaway with the collision walls).
   - `world_vista.py` now uses the same scene, so the vistas show the dressing too.

## Iterations (tee views)

- **It 1** (16 spp): placement was clean everywhere, nothing on walkways, water or cliffs.
  - Problem: budget allocation was first-come, so lanterns and trees ate the near field and H1-H4 got zero ground cover.
  - Fix: per-hole own shares per role group (lantern / tree / ground / far / interior). Ground cover is placed before
    trees.
  - Problem: old H9 trees ended up inside the hollow.
  - Fix: the 4.5-tall rule.
  - Problem: `fitcheck` then caught thin rope/canopy triangles crossing walkways and felt between vertices, and a
    footprint mismatch.
  - Fix: the layout now uses the exact triangle test and stores the footprint.
- **It 2** (24 spp): H2-H4 and H6 read well. H1, H5 and H7 were still bare beside the rails, because 1.6-2k-tri
  toadstool clusters ate the ground share. Fixes:
  - at most 2 heavy small props per hole;
  - cheap ground-cover refill (grass, ferns, bushes, boulders) aimed at the first 30 studs of each tee view;
  - at least 2 lantern hooks per hole;
  - ground share 8k.
- **It 3** (32 spp, final): every tee view is framed by maples/birches, lantern strings/hooks and rail-side bushes,
  over the real terrain with the village cliffs, falls, neighbouring holes and the tree. H8 is framed by the giant
  roots, and H9 is lit by the new interior lanterns and mushrooms. The vista showed a converted card too close to
  the H1 tee.
  - Fix: no card within 26 studs of any felt (+ fitcheck).
  - Problem: the final stats showed that putting ground cover first had starved the framing trees in the packed
    valley (H6 1, H7 0, H8 0 own trees).
  - Fix: a `tree1` pass places each hole's first 4 trees before ground cover (ground share 6.5k).
  - Re-rendered everything at 32 spp.
- **It 4** (final, 32 spp): the re-rendered H1 vista showed a flat wall of converted card clumps 26-40 studs out,
  blocking the signature view from the first tee across Lantern Mere to the giant tree. Fixes:
  - **protected sightlines** with no cards inside them: the world README vista cameras, H1 tee -> tree (bearing 302
    +-32 deg), Lookout Rock -> valley (293 +-45) and Root Stair -> tree (326 +-32);
  - card minimum distance from any felt raised to 32 studs;
  - fitcheck check + negative test.

  The valley holes (H5-H8) sit inside the Lookout Rock cone, so they have few or no cards. Their backdrops are the
  world's cliffs, falls, sister trees and tree line.

## Art director review

- **A) Quest performance**: per-hole numbers are in the table above.
  - Own dressing: 80-199k tris -> 10.4-19.4k.
  - Near field: 187-451k -> 25.2-34.0k.
  - No LOD copies were made. Repeated pieces are merged per material in the group FBX, and the preferred import is
    still one instance per prop (shared MeshIds).
  - The pass-2 far ring (203 x 834-tri `tree_backdrop_cluster`, about 169k tris) was dropped as 3D. Where a
    clump still had a valid spot (not on a walkway or slope, >= 32 from felt, outside the protected sightlines),
    it became a `treeline_card_red/_gold` card (57), and refill added more. That is 81 cards in
    total: 3 crossed double-sided quads, 12 tris, with an alpha-cut painted clump texture (`textures/card_red.png`,
    `card_gold.png`). Refill cards go >= 40 studs from their own felt.
  - Budgets are documented in README ("Quest VR budgets") and `manifest.dressing.budgets`.
- **B) Felt**: `textures/felt.png` is softer and slightly darker (#2F6E2C-#56A044, mean about #3F8836), with
  low-contrast mowing bands and faint directional nap.
  - New `felt_normal.png` for SurfaceAppearance.NormalMap.
  - Previews use a velvet sheen + the normal map, so slopes read.
- **C) Mountains** (`mountain_a/b/c`): MountainFoot #EDC6A8 (= horizon haze, fades into the sky) -> hazy peach
  #D8A38E -> dusty mauve #AE8890 (warmed off lavender after the first preview) -> warm-white snowcaps #F8EDE6 on
  peaks and up-facing high faces. Band edges are broken with noise.
- **D) Sky lantern**: 1.1 x 1.35 x 1.1 (was 1.5 x 2 x 1.5), a rounder 12-sided lathe, new `SkyPaper` material
  (`textures/paper_glow.png`: warm washi with bamboo ribs and a bright flame band, self-lit), 250 tris.
- **E) H9 interior**: new `hollow_tree_world_shell_part8.fbx` (16,660 tris) has:
  - 18 low lantern clusters (3 lanterns on an iron bracket, glow 5-9 above the floor);
  - 24 big glowing-mushroom clumps along the inner wall.

  It is clear of all H9/H8 keep-outs (world_fitcheck ALL PASS; door rays still clear). There are **30 PointLight
  spots** in `world/manifest.json` (part8 `lights_world`) and in `manifest.world.h9_interior_lights` (one per
  cluster, one per two mushroom clumps, kept few for Quest). H9 dressing adds 7 floor-level glowing mushrooms, ferns
  and toadstools inside the ring.

Re-rendered: `tee_contact_sheet.png`, `previews/assembly_hNN_{tee,top}.png`, `world/contact_sheet_world.png`,
`world/previews/vista_*.png`, `world/previews/{mountain_*,sky_lantern,hollow_tree_world_shell}_*.png`.

## Files

- **New**:
  - `_src/dressing_world.py`, `_src/world_occ.py` (cache in `_src/cache/`), `_src/world_scene.py`,
    `_src/assembly_world.py`, `_src/props_cards.py`;
  - `_src/dressing_seed_pass2.json` (frozen pass-2 layouts = the "before" state);
  - `_src/manifest_before_pass4.json`;
  - `textures/{felt_normal,paper_glow,card_red,card_gold}.png`;
  - `fbx/treeline_card_{red,gold}.fbx`, `fbx/dressing_hNN_cards.fbx`;
  - `world/fbx/hollow_tree_world_shell_part8.fbx`;
  - `_src/pass4_progress.md`, this file.
- **Changed**:
  - `textures.py`, `lglib.py` (card / emissive texture materials, felt sheen + normal);
  - `world_pieces.py`, `world_build.py`, `world_docs.py`, `world_fit.py` (`dressing_keepouts`);
  - `world_vista.py` (uses world_scene), `fitcheck.py`, `make_docs.py`, `tee_sheet.py`, `readme_extra.md`;
  - `build.sh` (runs `dressing_world.py` and `assembly_world.py`; `dressing.py` stays as the pass-2 seed generator
    and is no longer run).
  - The repo skill `blender-asset-pipeline` gained two lessons (re-validation with exact triangles and world
    occupancy; Quest near-field budgeting with cards).

## Known issues / notes

- **Shared budget**: the packed valley holes (H5-H8, 11-60 studs apart) share one near-field budget. H6-H8 keep
  4 own trees each and lean on world pieces, neighbours and cards. Raise `NEAR_BUDGET` if Quest profiling allows it.
- **Cards seen from above**: from the aerial vista and the stairs, cards read as crossed planes. At tee height they
  are fine. Point the aerial camera lower, or skip the cards for top-down marketing shots.
- **Terrain source**: grounding uses terrain-4stud.json. If Studio Terrain is smoothed or carved differently,
  raycast from `world_pos + (0, 20, 0)`.
- **Old overview renders**: `previews/assembly_hNN.png` (3/4 overviews) are the old pass-2 flat-layout renders and
  were not re-rendered (only tee/top were requested).
- **Preview-only scene**: the terrain is 4-stud cells, so slopes look faceted and water stepped. The felt boxes,
  path ribbons and point lights are not exported.
