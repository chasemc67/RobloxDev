# Pass 6: art rework (Claude, 2026-10-12)

All 9 steps are done.
- Blender 5.2 ran headless only through `run_blender.ps1`, one process at a time.
- Every export comes from generator code; no FBX was hand-edited.
- No collision meshes were made, and Codex was not used.
- The only gondola changes are steps 1 and 1b.

Backups:
- `_src/backup_pass6/` holds the pre-pass-6 snapshots of `manifest.json`, `layout.json`, `README.md`, `pieces_table.md` and `contact_sheet.png`.
- It also holds the changed generator sources (`sclib.py`, `sc_pieces.py`, `gondola_geom.py`, `sc_gondola.py`, `sc_fitcheck_holes.py`, `sc_textures.py`), the 3 old gondola FBX, `rim_silhouette.fbx`, and the 36 old cliff/slot FBX (in `fbx_cliffs/`).

## Results at a glance

| | Before (pass 5) | After (pass 6) |
|---|---:|---:|
| Pieces / FBX files | 102 / 107 | 208 / 213 |
| Placed instances | 820 | 874 |
| **Placed triangles** | **305,982** | **588,476** |
| Cliff kit, placed tris | 192,224 | 295,248 (+54 %) |
| Rim silhouettes, placed tris | 960 | 4,800 |
| Hole dressing, placed tris | 0 | 174,746 |
| Library triangles | 126,491 | 337,934 |
| Max mesh tris (whole kit) | 4,324 | 4,324 |
| Max mesh tris (pass-6 pieces) | n/a | 3,880 (`h13_ground__ClayBrick`) |

- **Fitcheck at 0.15 studs: ALL PASS.**
  - [1] hole play volumes: all 18 holes pass, and all 54 new dressing pieces (53 per-hole merges + the trading post) have **zero** intrusions.
  - [A] footprints: pass.
  - [B] walkways: 77/77 segments pass. **`p_h18_hub` seg 3 PASSES**, with the lowest gondola triangle (cable plus the cabin swept every 1 stud on both lines) **10.04 studs** above the walk. The requirement is ≥ 8.
  - [C] lane rules: pass.
  - Copied to `_src/fitcheck_pass6_validated.txt`.
- **Re-import:** `_src/reimport_pass6.txt` is **ALL PASS** for all 144 new or changed FBX.

## 1. Gondola tower recolour
- **Materials:**
  - Legs, lattice and crossbeam are sun-weathered timber: new material `TimberWeathered`, texture `textures/timber_weathered.png`.
  - The crossbeam baulks alternate `TimberWeathered` and `Timber`.
  - Leg-top saddles, hanger links and cradle beams are dark `Iron`.
  - The cradle bolt plates use the new `Brass` material.
  - Only the turning sheaves keep the red/cream bands (`PepRed`/`MintWhite`), since they are moving parts. The cabin is unchanged.
- **Geometry check:** I rebuilt the cable on the unchanged pass-5 line. It has **2,012 tris = 2,012**, and bbox [553.54, 199.95, 420.0] and centre [-274.41, 99.83, -206.8] are identical. Re-import passed. Details are in `_cache/pass6_step1.json`, and that FBX is kept as `_cache/p6/gondola_cable_step1_recolour_pass5line.fbx`.
- **Note on the tri count:** the first attempt gave 2,000 tris. When all seven butted baulks shared one material, `remove_doubles` dropped their 12 coincident end-face tris. Alternating two timber tones keeps the geometry identical.
- **Brass:** the brass sits on the existing cradle bolt plates. I added no extra bolt geometry, because that would have broken "identical geometry".

## 1b. Gondola clearance
- **New piece `gondola_station_bottom` (2,205 tris, max mesh 744).** It is the station model raised **7.2 studs** (9 × 0.8 risers) onto an open timber/sandstone undercroft.
  - It has iron post caps with brass bolt heads.
  - A 10-riser sandstone side stair (0.8 × 1.5, 5.8 wide) on local +X climbs from the ground at the open end to the back of the deck. The cabin loop only uses the front 7 studs of the deck.
  - Deck top is world y 26.0. The bull wheel is at 14.8 above the ground.
  - Same footprint centre (132, 18, 544) and yaw 53.53.
  - The ground boarding point (130, 18, 540) stays clear under the open end, with ≥ 4.9 studs of headroom.
- The top station keeps `gondola_station`; that FBX is unchanged.
- **New line:**
  - Bottom wheel / attach goes from 25.6 to **32.8**. Tower position, tower crest (221), top attach and sags (10 / 2.5) are unchanged.
  - New arc lengths are 557.18 + 164.95.
  - The motion formula, the 10 s samples and the slope break (now 23.5° up to 11.5° down at the tower, span-end tangents) are recomputed in `manifest.json` `gondola_cabin.motion`.
  - The cabin FBX is unchanged; it parks at (132.65, 32.8, 539.755).
  - `gondola_cable` is still 2,012 tris; its bbox is now [553.54, 192.75, 420.0].
- **Clearance:** `p_h18_hub` seg 3 passes with a **10.04-stud** minimum (it was 2.92).
- **`p_h11_h12` dam railings:** I exempted them, with an explicit rule in `sc_fitcheck_holes.py` [B].
  - The rule skips `railing_12` / `peppermint_dam` triangles only when they lie entirely in the outer 0.6 studs of the 8-wide corridor and top out ≤ 4.0 above the walk.
  - Measured: all of them sit at |v| ≥ 3.42 of 4.0 and are ≤ 3.58 high.
  - They are listed as INFO. Any other triangle from those pieces would still FAIL.

## 2. New kit pieces
Group `dressing_kit` (`trading_post_deck` is `hole_dressing`):

| Piece | Tris | Max mesh |
|---|---:|---:|
| trading_post_deck | 3,840 | 840 |
| barrel_a / barrel_b | 252 / 624 | 96 / 128 |
| lantern_post / lantern_hanging | 244 / 156 | 108 / 108 |
| lollipop_cactus_cluster | 696 | 308 |
| rock_candy_cluster | 264 | 102 |
| gumdrop_shrub_a / b / c | 592 / 356 / 456 | 320 / 160 / 320 |
| boulder_scatter / fallen_rock_scatter | 180 / 100 | 180 / 60 |

- **Lanterns:** they have a Neon core in the new `LanternGlow` material, with `cast_shadow` false in the manifest. Set CastShadow off in Studio.
- **New materials:** TimberWeathered, Brass, LanternGlow, Canvas, CanvasRed, ClayBrick, RedDirt, RedDirtLight, Pebble.
- **New textures:** `timber_weathered`, `clay_brick`, `red_dirt`, `red_dirt_light` (from `sc_textures_pass6.py`). Existing PNGs are untouched.
- **Trading post:** placed at (47.5, 17.36, 469.0) with yaw −90, beside the H1 tee on the west side of the lane, facing the lane.
  - Its 22 × 10 deck spans world x 42.5–52.5 and z 458–480.
  - Everything taller than 2 studs is more than 3 studs from rail1, and it keeps clear of the hitching-post anchor and the 8-wide walk-in from the south.
  - Zero intrusions.
- **Prop clusters:** **68 clusters**, each of 3–5 members, placed at **all 18 tees and all 50 detected turns**. A turn is a route bend of ≥ 30° along tee → felt centres → cup. 308 members in total.
- **Merges:** members are merged per material per hole into `hNN_dress_props` and `hNN_dress_plants`.
- **How placement was checked:** `sc_dress_pass6.py` uses the exported kit triangles and the fitcheck's own volumes. Each member is tested against:
  - every hole's play volumes at 0.15 + 0.1 (SAT);
  - the lane rules (with 0.1 slack);
  - walkway and on-hole corridors + 0.5;
  - boarding points (4 studs);
  - existing kit geometry;
  - the holes.json decoration anchors (occluder boxes, or approx_size rectangles);
  - slope and water.
- **Where it is recorded:** `layout.json` has 53 per-hole merged instances (H4 has no plant merge) plus the trading post. `manifest.json` `pass6.dressing.holes.hNN` lists every member, cluster, tri count and ground stat.

## 3. Ground dressing
- **Kit pieces:** `red_dirt_patch_a/b` (36 tris each), `pebble_scatter` (80), and `clay_brick_edging` (120 tris, an 8-stud run of rounded bricks).
- **Per hole, `hNN_ground`:**
  - A terrain-hugging, two-tone red-dirt carpet: a 3-stud jittered grid at worldlib `height_at` + 0.2, including the Old Sugarloaf dome patch.
  - It covers the floor out to 16 studs from the felt in full, then thins raggedly out to 30.
  - It stops 3+ studs short of steep ground (cliff feet), so sand shows at the edges.
  - Cells that fail are split into 4 sub-cells, so the dirt reaches close to rails, walkways and kit.
  - About 150 pebbles per hole.
  - **1,892 rounded clay bricks** sit 0.2 outside the rails on the felt side's outer edge. They follow the felt outline, skip walkways, and are tested at 0.15 + 0.02.
- **Exclusions:** walkways (+0.3) and walkway kit stay clear. The ground pieces are also held to the lane rule, which removed dirt beside sunken felt at H11, H15 and H16.
- **Per-hole dressing totals** (props + plants + ground, tris):

| Hole | Tris | Hole | Tris | Hole | Tris |
|---|---:|---|---:|---|---:|
| H1 | 7,130 | H7 | 7,578 | H13 | 14,470 |
| H2 | 16,248 | H8 | 8,454 | H14 | 5,256 |
| H3 | 9,888 | H9 | 12,618 | H15 | 5,810 |
| H4 | 4,398 | H10 | 6,362 | H16 | 7,564 |
| H5 | 10,308 | H11 | 9,348 | H17 | 7,746 |
| H6 | 9,616 | H12 | 13,280 | H18 | 14,832 |

## 4. Cliffs
- `sc_cliffs_pass6.py` turns each 24-wide panel into one eroded tower:
  - recessed gaps at both edges, so at the 21-stud spacing the towers stand separate with about 5-stud slots;
  - a 12-stud world-y stepped taper with cap-rock overhangs;
  - noise erosion and fluting;
  - gently wavy strata. V = (z + y0 + wave(x)) / 36, and the wave is 0 at the panel edges, so the world-y banding and seams still line up.
- **New variants:** 36 rounded-top variants (`cliffT_*`, `slotT_*`), swapped onto the top panel of all **309 stacks** (`_cache/pass6_cliffs.json`).
- Same ids, placements and envelope as before, so there are no new footprint or walkway intrusions.
- **Panel tris, old → new:**

| Panel | Old | New | Rounded-top variant |
|---|---:|---:|---:|
| cliff h6 | 76 | 104 | 260 |
| cliff h12 | 136 | 180 | 312 |
| cliff h24 | 256 | 336 | 492 |
| cliff h48 | 496 | 648 | 804 |
| slot h24 | 658 | 738 | 894 |
| slot h48 | 1,436 | 1,588 | 1,744 |

- `rim_silhouette` is now 4 stepped towers with gaps and rounded tops: 12 → 60 tris, × 80 placements.
- **Placed cliff tris: 192,224 → 295,248.**

## Per-hole Quest near-field tris
These count triangles whose centroid lies within 60 studs of each footprint centre. The "dressing" column includes neighbouring holes' dressing. The budget is about 40k per hole; the maximum is **29,086 (H5)**.

| Hole | Before | After | Cliff | Dressing |
|---|---:|---:|---:|---:|
| H1 | 4,082 | 18,001 | 0 | 13,919 |
| H2 | 4,195 | 22,625 | 0 | 18,430 |
| H3 | 2,996 | 12,770 | 0 | 9,774 |
| H4 | 13,433 | 24,765 | 15,591 | 7,827 |
| H5 | 12,471 | 29,086 | 14,095 | 13,732 |
| H6 | 11,834 | 25,617 | 10,954 | 11,257 |
| H7 | 2,535 | 11,572 | 2,933 | 7,757 |
| H8 | 2,022 | 12,964 | 39 | 10,903 |
| H9 | 3,344 | 17,092 | 2,211 | 12,618 |
| H10 | 1,545 | 8,535 | 1,565 | 6,362 |
| H11 | 5,169 | 17,065 | 7,369 | 9,348 |
| H12 | 4,044 | 19,083 | 4,321 | 13,245 |
| H13 | 2,463 | 17,427 | 318 | 14,667 |
| H14 | 2,308 | 11,803 | 1,204 | 8,495 |
| H15 | 319 | 7,253 | 1,183 | 5,951 |
| H16 | 8,368 | 19,141 | 8,647 | 7,932 |
| H17 | 2,505 | 12,330 | 1,550 | 8,338 |
| H18 | 5,983 | 24,714 | 5,449 | 16,485 |

## 5–6. Build, re-import, previews, fitcheck
- **Builds:** everything was built by `sc_build_pass6.py`; the records are in `_cache/pass6_build.json`.
- **Previews:** `<id>_eye.png` and `<id>_34.png` were written for every new or changed piece. Cliff variants follow the old convention: phase 3 for cliffs, phase 4 for slots.
- **Contact sheet:** `contact_sheet.png` was regenerated with 148 thumbnails.
- **Re-import:** `_src/reimport_pass6.txt` is ALL PASS.
- **Fitcheck:** `fitcheck_pass6.txt` is ALL PASS, copied to `_src/fitcheck_pass6_validated.txt`.

## 7. Staged render and the dark slab
- In `_src/render_hero_pass6.py`, the candy-striped staged rails are replaced by **rounded clay-brick curbs**. These are render-only bricks about 1.5 long, with an 11-point rounded profile and a per-brick terracotta tint.
- **Slab finding:** the dark slab to the right of the H1 lane, near the H2 green, is **kit geometry**, not a staging artefact.
  - It is three `walk_boardwalk_6x12` instances: the Junction boardwalk planks on `p_h1_h2` segments 1–2, at (76.36, 18, 432.49), (77.64, 18, 429.51) and (85.82, 18, 422.54).
  - It looks dark because it is dark Timber with plank gaps, seen at a grazing angle.
  - I ray-cast the slab pixels to world positions and matched them to the layout.
  - It is not a shadow, a drop or hazard volume, or staged geometry. I left it unchanged; it is walkway floor kit.

## 8. Render
- **Light:**
  - The key sun is at 277°/4°, orange, energy 24, with shadows.
  - The rim sun is at 285°/3°, strong orange, energy 4, with **shadow off**. At 3–4° the real sun is blocked by the west mesas and the kit cliffs, so most of the floor sits in their shade, and a no-shadow rim from the same bearing is what puts the orange rim on the tower tops.
  - I tested making the terrain a non-shadow-caster and then reverted it, because it did not help.
- **Sky:** the camera-ray sky runs gold #FFC84A → peach → coral → mauve. Fill and bounce are reduced, and the grade is AgX Punchy at +1.15.
- **Previews:** 8 runs at 640×360 / 16 spp, in `pass6_preview*.log`.
- **Final:** Cycles OptiX on the RTX 4090, 1920×1080, 128 spp, denoised, 5.9 s.
- **Outputs:**
  - `previews/hero/V1-hub-tee1_pass6.png`
  - `previews/hero/V1-hub-tee1_pass6_vs_concept.png` (labelled, side by side with `world/vistas/V1-hub-tee1.png`)
  - `previews/hero/pass6_render_report.json`
- **Remaining gaps vs the concept:**
  - The sun is out of frame (it is 85° to the left of this north view).
  - There are no mesa-top greens, rope bridges or waterfall in this direction.
  - The near tee is the straight holes.json lane, not the concept's round tee platform.

## 9. Docs and files
- `README.md` has a new Pass 6 section.
- `manifest.json` has the new pieces plus `pass6` (dressing, cliffs, renders, slab finding, placed before/after) and an updated gondola motion.
- `layout.json` has the bottom station swap, 54 new instances, and 309 stack-top swaps.
- `_src/pieces_table.md` was regenerated.
- **Scripts:**
  - `sc_textures_pass6.py`, `sc_pieces_pass6.py`, `sc_cliffs_pass6.py`, `sc_cliffs_layout_pass6.py`, `sc_dress_pass6.py`
  - `sc_build_pass6.py`, `finalize_pass6.py` (+ `finalize_pass6_ext.py`), `finalize_pass6_art.py`, `render_hero_pass6.py`
- **To reproduce,** run from `models`, in this order:
  1. `python _src/sc_textures_pass6.py`
  2. Blender `--step1` build
  3. Gondola build
  4. `--group dressing_kit` build
  5. `python _src/sc_dress_pass6.py`
  6. `python _src/sc_cliffs_layout_pass6.py`
  7. `--group cliff_kit,far_card,hole_dressing` builds
  8. `python _src/finalize_pass6.py`
  9. `python _src/sc_fitcheck_holes.py`
  10. Render
  11. `python _src/finalize_pass6_art.py [--compare]`
