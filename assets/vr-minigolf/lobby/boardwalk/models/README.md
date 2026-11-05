# Pass 2 update

Three portal arches replaced; moving lantern sets, snowpuff, full-UV portal quads and flush apron exported separately. 37 prop FBXs, 252 manifest instances, 48764 lobby tris. Portal fitcheck and FBX reimport ALL PASS. Kit: 21 separate decoration assets, independent manifest.

See [_src/pass2_summary.md](_src/pass2_summary.md) for current geometry, collision, hooks, pivots, rebuild commands and caveats; [portal concept comparison](previews/portals/portals_vs_concepts.png) and [kit contact sheet](../../kit/previews/kit_contact_sheet.png). Pass1 backup at `_backup_pass1/`. Earlier pass1 tables/previews below are historical; current manifest is authoritative.

# Golden Hour Boardwalk: lobby props, pass 1 (SRV-137)

Generated 2026-10-11 on the Windows PC with Blender 5.2.2 LTS. Everything is procedural; rebuild
with the scripts in `_src/` (see Rebuild below). Fit check: **ALL PASS**
(`_src/fitcheck_pass1_validated.txt`).

* **29 FBX files** in `fbx/`, named exactly like the `assetName`s in RobloxDevBot's `_src/builder_Lobby.luau`.
  `bw_course_card_plane` is **not** exported (OVERRIDE 2: the cards are RobloxDevBot's, the board has 3 recessed
  card faces instead).
* **Lobby total: 48,656 tris** for 242 builder instances (limit 120,000, target ~115k).
  Deck tiles 1,520 (152 x 10), railings 9,324 (42 x 222).
* One shared atlas `textures/bw_atlas_1024.png` (1024x1024, 8-bit RGB, no metadata) and `manifest.json` with
  per-file bbox, tris, materials, pivot, front, motion, collision boxes, the instance list and totals.

## Files

| file | what |
|---|---|
| `fbx/bw_*.fbx` | 29 props (table below) |
| `textures/bw_atlas_1024.png` | shared atlas, layout `_src/atlas_layout.md` / `_src/atlas_def.py` (embedded in every atlas FBX too) |
| `manifest.json` | per-prop data + `instances[]` (from the builder) + `totals` |
| `previews/props/<name>.png` | 3/4 view + eye-height (5 studs) view with a 2x5 reference capsule |
| `previews/contact_sheet.png` | all props, labelled |
| `previews/spawn_view.png` | whole lobby from the spawn: Roblox (100, 5, 100) looking north, 90 deg hfov, golden hour |
| `previews/topdown.png` | orthographic plan of the assembled lobby |
| `previews/overview.png` | extra: elevated view from behind the spawn |
| `_src/` | generators, fit check, renders, logs, `PROGRESS.md`, `pass1_summary.md` |

## Axes, units, pivots

* 1 Blender unit = 1 stud. Import at **scale 1.0**. FBX exported with forward -Z, up Y, transforms applied (every
  object sits at the prop origin with an identity transform), textures embedded.
* Built in Blender Z-up: Blender +Y = Roblox -Z = north, Blender -Y = Roblox +Z = south.
* Every prop is built at **yaw 0 in the lobby.json frame**; the builder's yaw (`CFrame.Angles(0, rad(yaw), 0)`)
  is applied on top. `front` in the manifest says which local side is the viewer side:
  board, leaderboard panels, signpost, arches, nameplates, coming-soon signs, windmill = **+Z (south, toward
  spawn)**; bench and shack = **-Z (north)** so the builder's yaw 180 (benches face south) and yaw 90 (shack
  counter faces west) come out right.
* **Pivot = base centre** (bbox centre X/Z, min Y = 0) for every prop except `bw_windmill_blades`, whose pivot is the
  **hub** (rotation axis = local Z, 6 rpm; hub sits at windmill local (0, 7.0, +3.3)).
* `bw_cup_flag`: the pole is on the pivot axis (place the pivot on the cup centre at turf height Y 0.4).

## Materials and import notes

* `BW_Atlas`: all opaque parts, one MeshPart per FBX (UVs into the shared atlas). `BW_Neon`: emissive parts as their
  own MeshPart: set **Material = Neon** and Color from `parts[].color` (#FFC867; #9FE6F2 on the Aurora arch).
  `BW_Backdrop`: `bw_sea_stacks` / `bw_rock_arch`, vertex colour only, no texture.
* Decoration only: **Anchored = true, CanCollide = false, CanQuery = false, CanTouch = false** on every MeshPart;
  gameplay collision = the manifest `collision[]` boxes (1 box per prop, arches 3: two legs + lintel) or the
  lobby.json colliders. No mesh collision.
* No alpha anywhere. No real lights baked in: the Neon parts are good PointLight hosts (lantern posts, board
  lanterns, shack lanterns, arch lanterns); keep to ~8 PointLights in the lobby.
* Scalable instances (`scalable` in the manifest; builder sizes are honoured as `instances[].scale`): deck tiles in
  X/Z (the 8-stud last pier row), `bw_railing` in X (8-stud pier ends), `bw_string_lights` in X.
* Named faces for SurfaceGui / art: `bw_arch_nameplate` -> `plate_face`, `bw_birdie_bites_shack` -> `menu_face`, `bw_birdie_bites_shack` -> `sign_face`, `bw_coming_soon_sign` -> `plate_face`, `bw_course_board` -> `card_face_1`, `bw_course_board` -> `card_face_2`, `bw_course_board` -> `card_face_3`, `bw_leaderboard_wall` -> `panel_1`, `bw_leaderboard_wall` -> `panel_2`, `bw_leaderboard_wall` -> `panel_3`, `bw_signpost` -> `arrow_face_1`, `bw_signpost` -> `arrow_face_2`, `bw_signpost` -> `arrow_face_3`.

### Course board card faces (OVERRIDE 2)
3 flat recessed faces on the south face, each 6 x 8 studs, inset 0.15 behind the brass frame surface (local Z +1.0),
2 tris each, normal +Z. Centres in local Roblox studs from the pivot:

| face | centre [x, y, z] | size | insetDepth | normal |
|---|---|---|---|---|
| `card_face_1` | [-8.0, 5.5, 0.85] | [6.0, 8.0] | 0.15 | [0, 0, 1] |
| `card_face_2` | [0.0, 5.5, 0.85] | [6.0, 8.0] | 0.15 | [0, 0, 1] |
| `card_face_3` | [8.0, 5.5, 0.85] | [6.0, 8.0] | 0.15 | [0, 0, 1] |

## Per-file table (bbox in Roblox X x Y x Z studs)

| file | group | bbox | spec | tris | budget | builder count | tris x count | materials | front |
|---|---|---|---|---|---|---|---|---|---|
| `bw_arch_aurora_archipelago.fbx` | arches | 16 x 17.88 x 4 | 16 x 18 x 4 | 1678 | 10000 | 1 | 1678 | BW_Atlas, BW_Neon | +Z |
| `bw_arch_lantern_grove.fbx` | arches | 16 x 17.93 x 3.89 | 16 x 18 x 4 | 9456 | 15000 | 1 | 9456 | BW_Atlas, BW_Neon | +Z |
| `bw_arch_nameplate.fbx` | board | 8 x 2 x 0.5 | 8 x 2 x 0.5 | 176 | 400 | 3 | 528 | BW_Atlas | +Z |
| `bw_arch_sugarloaf_canyon.fbx` | arches | 16 x 18 x 4 | 16 x 18 x 4 | 1356 | 8000 | 1 | 1356 | BW_Atlas | +Z |
| `bw_barrel.fbx` | social | 2 x 3 x 2 | 2 x 3 x 2 | 212 | 300 | 1 | 212 | BW_Atlas | none |
| `bw_beach_umbrella.fbx` | social | 6 x 7.15 x 6 | 6 x 7 x 6 | 334 | 700 | 1 | 334 | BW_Atlas | none |
| `bw_bench.fbx` | social | 6 x 2.5 x 2.05 | 6 x 2.5 x 2 | 300 | 600 | 6 | 1800 | BW_Atlas | -Z |
| `bw_birdie_bites_shack.fbx` | social | 16 x 14.22 x 17.8 | 16 x 14 x 18 | 3754 | 12000 | 1 | 3754 | BW_Atlas, BW_Neon | -Z |
| `bw_coming_soon_sign.fbx` | board | 6 x 2 x 0.5 | 6 x 2 x 0.5 | 184 | 400 | 2 | 368 | BW_Atlas | +Z |
| `bw_course_board.fbx` | board | 26 x 10.75 x 2 | 26 x 10 x 2 | 1606 | 6000 | 1 | 1606 | BW_Atlas, BW_Neon | +Z |
| `bw_crate.fbx` | social | 2 x 2 x 2 | 2 x 2 x 2 | 44 | 50 | 1 | 44 | BW_Atlas | none |
| `bw_cup_flag.fbx` | green | 0.6 x 5 x 0.6 | 0.6 x 5 x 0.6 | 140 | 200 | 2 | 280 | BW_Atlas | none |
| `bw_deck_plank_a.fbx` | structure | 10 x 1 x 10 | 10 x 1 x 10 | 10 | 100 | 76 | 760 | BW_Atlas | none |
| `bw_deck_plank_b.fbx` | structure | 10 x 1 x 10 | 10 x 1 x 10 | 10 | 100 | 76 | 760 | BW_Atlas | none |
| `bw_flower_planter.fbx` | social | 4 x 2 x 2 | 4 x 2 x 2 | 756 | 1000 | 1 | 756 | BW_Atlas | none |
| `bw_lantern_post.fbx` | social | 1 x 7.05 x 1 | 1 x 7 x 1 | 224 | 400 | 6 | 1344 | BW_Atlas, BW_Neon | none |
| `bw_lantern_tree_canopy.fbx` | backdrop | 23.11 x 15.01 x 19.03 | 24 x 16 x 20 | 5600 | 6000 | 1 | 5600 | BW_Atlas, BW_Neon | +Z |
| `bw_leaderboard_wall.fbx` | board | 14 x 10 x 2 | 14 x 10 x 2 | 1736 | 3000 | 1 | 1736 | BW_Atlas | +Z |
| `bw_picnic_table.fbx` | social | 6 x 2.88 x 6 | 6 x 3 x 6 | 588 | 900 | 1 | 588 | BW_Atlas | none |
| `bw_pier_piling.fbx` | structure | 2.02 x 6 x 1.92 | 2 x 6 x 2 | 232 | 250 | 8 | 1856 | BW_Atlas | none |
| `bw_practice_green.fbx` | green | 34 x 1.2 x 20 | 34 x 1.2 x 20 | 576 | 2000 | 1 | 576 | BW_Atlas | none |
| `bw_railing.fbx` | structure | 10.01 x 3.5 x 0.6 | 10 x 3.5 x 0.6 | 222 | 350 | 42 | 9324 | BW_Atlas | none |
| `bw_rock_arch.fbx` | backdrop | 31.68 x 23.74 x 10.02 | 30 x 24 x 10 | 1164 | 1200 | 1 | 1164 | BW_Backdrop | +Z |
| `bw_sea_stacks.fbx` | backdrop | 29.72 x 22.02 x 10.88 | 30 x 22 x 12 | 1088 | 1800 | 1 | 1088 | BW_Backdrop | +Z |
| `bw_signpost.fbx` | board | 2.92 x 7 x 1.05 | 3 x 7 x 1 | 390 | 800 | 1 | 390 | BW_Atlas | +Z |
| `bw_string_lights.fbx` | social | 20 x 0.53 x 0.47 | 20 x 0.5 x 0.5 | 248 | 300 | 1 | 248 | BW_Atlas, BW_Neon | none |
| `bw_tee_mat.fbx` | green | 2 x 0.1 x 2 | 2 x 0.1 x 2 | 12 | 20 | 2 | 24 | BW_Atlas | none |
| `bw_windmill.fbx` | green | 6 x 10 x 6 | 6 x 10 x 6 | 622 | 3500 | 1 | 622 | BW_Atlas | +Z |
| `bw_windmill_blades.fbx` | green | 7.87 x 7.87 x 0.5 | 8 x 8 x 0.5 | 404 | 500 | 1 | 404 | BW_Atlas | +Z |
| **total** | | | | | | **242** | **48,656** | | |

## Instance plan

`manifest.instances[]` is RobloxDevBot's `builder_Lobby.luau` placement list verbatim (id, asset, position = base
centre, yaw, size, solid), plus `scale` where the builder size differs on a scalable axis. Counts:
bw_deck_plank_a x76, bw_deck_plank_b x76, bw_railing x42, bw_pier_piling x8, bw_bench x6, bw_lantern_post x6, bw_arch_nameplate x3, bw_coming_soon_sign x2, bw_cup_flag x2, bw_tee_mat x2, bw_course_board x1, bw_leaderboard_wall x1, bw_signpost x1, bw_arch_lantern_grove x1, bw_arch_sugarloaf_canyon x1, bw_arch_aurora_archipelago x1, bw_practice_green x1, bw_windmill x1, bw_windmill_blades x1, bw_birdie_bites_shack x1, bw_picnic_table x1, bw_barrel x1, bw_crate x1, bw_flower_planter x1, bw_beach_umbrella x1, bw_string_lights x1, bw_sea_stacks x1, bw_rock_arch x1, bw_lantern_tree_canopy x1.

Budget decision (OVERRIDE): deck tiles are top + 4 sides only (**10 tris**, plank gaps and per-plank tint
jitter live in the atlas deck strip; A and B use different U halves so they don't read as a repeat), railing
sections are 222 tris (<= 350). All other props sit at or under their props.md targets.

## Notes / deviations

* `bw_practice_green`: bbox Y is 1.2 (0.4 slab + bumper 0.8 above the turf); the builder lists the slab only (0.4).
  Don't scale it.
* `bw_lantern_tree_canopy` includes its trunks (base at Y 0). The builder's Y 10 floats it (spawn/top renders use
  Y -0.1).
* `bw_windmill_blades`: place at the hub (150, 7.4, 67.3), not the builder's (150, 3.4, 67.3) (see questions).
* `bw_leaderboard_wall`: decorative twin panels on the back because of the yaw question below.
* Railings: the 10-stud section has its post at the centre and the rope swag dips at the section ends, so
  consecutive sections read as one continuous railing.

## Spec questions for Game Art Bot

1. **Leaderboard facing**: The brief puts `panel_1..3` on the local +Z (south) face, "before its -90 yaw". With `CFrame.Angles(0, rad(-90), 0)` local +Z turns to world **west** (toward the west rail at X 10), but lobby.json says the wall faces **east**. I modelled decorative twin parchment panels on the back so both sides read. Fix options: builder uses yaw **+90** (panels face east), or keep -90 and I move `panel_1..3` to the -Z face in pass 2. Which one?
2. **Windmill blade pivot**: `bw_windmill_blades` pivots at the hub (brief). The builder entry (150, 3.4, 67.3) looks like a base-centre placement of an 8x8 box; with a hub pivot it must be **(150, 7.4, 67.3)** (windmill pivot + `blade_hub.local` (0, 7.0, 3.3) in the manifest). Please confirm RobloxDevBot will use the hub position (the spawn render does).
3. **Lantern-tree canopy height**: The builder places `bw_lantern_tree_canopy` with its base at **Y 10**, which floats it: the mesh includes its trunks (base at local Y 0). Suggest Y -0.1 (on the sand strip). The spawn/top renders use -0.1.
4. **Spawn clear radius vs south rail**: lobby.json puts the south deck edge (rail centre line Z 110) exactly 10 studs from spawn (Z 100), so the railing's inner face sits at **9.7** studs. No placed prop is inside 10. OK to treat the mandatory edge railing as an exception, or should the spawn move to Z 99.5?
5. **Practice green size**: Builder size is 34 x 0.4 x 20 (slab only). The mesh is 34 x **1.2** x 20 because the bumper rail rises 0.8 above the turf (inside the footprint). The builder must **not** scale it to 0.4 tall.
6. **String lights span**: `bw_string_lights` is 20 long at Y 7 between X 155..175, but the pier lantern posts are at X 153 and 177 (24 apart, 7.05 tall). Scale X 1.2 (supported: `scalable: x`) or move the posts to 155/175?
7. **Backdrop placement**: `bw_sea_stacks` (Z 210) and `bw_rock_arch` (Z 230) are south of the pier, i.e. behind the spawn view (which looks north); they frame the sunset view from the pier. Intended? If they should also read from spawn, a copy north of the sand strip would be needed.
8. **Budget headroom**: The lobby lands at **48,656** tris with the builder counts (target ~115k), because the deck tile is 10 tris and every hero prop is under its target (arches 12,490 of 33k). Spend the ~65k headroom on hero detail in pass 2 (e.g. Sugarloaf / Aurora / shack), or keep the Quest headroom?
9. **Neon colours**: `BW_Neon` is #FFC867 everywhere except `bw_arch_aurora_archipelago`, whose `BW_Neon` mesh is #9FE6F2 (crystal tips). The manifest `parts[].color` carries the colour per file; OK to keep one material name?
10. **Board lantern height**: The two Neon lanterns on the course board's side posts put its top at Y 10.75 (spec 10, within 10%). OK, or lower them into the 10-stud envelope?

## Rebuild

```
python -I _src/make_atlas.py                                        # atlas (Pillow)
_src/run_blender.ps1 -Script _src/build_all.py -ScriptArgs "--group=structure,board,arches,green,social,backdrop"
python -I _src/build_all.py --assemble                              # manifest.json
_src/run_blender.ps1 -Script _src/fitcheck.py                       # -> _src/fitcheck_pass1_validated.txt
_src/run_blender.ps1 -Script _src/render_props.py ; python -I _src/post_previews.py
_src/run_blender.ps1 -Script _src/render_lobby.py                   # spawn_view / overview / topdown
python -I _src/make_docs.py                                         # README.md + _src/pass1_summary.md
```
Library: `_src/bwlib.py` (adapted from the Lantern Grove `lglib.py`, self-contained), `_src/registry.py`,
generators `_src/props_{structure,board,arches,green,social,backdrop}.py`.

## Pass 3 richer portals

Current portal assets and independently hinged lanterns are documented in [_src/pass3_summary.md](_src/pass3_summary.md). All exported opening/envelope/trigger/budget checks and FBX reimport checks pass. Preview comparison: [previews/portals/portals_vs_concepts.png](previews/portals/portals_vs_concepts.png). Use the pass 3 rebuild commands in the summary; combined pass 2 lantern exports have been replaced by individual anchored files.

## Pass 4 standalone portal scenery

Twelve standalone scenery exports and six canopy-anchored Grove lanterns are complete. See [_src/pass4_summary.md](_src/pass4_summary.md) for triangles, group totals, pivots, collision, clearance minima, anchors and rebuild commands. Both fitcheck and FBX reimport report ALL PASS; preserved exports match the pass3 backup byte-for-byte. Place scenery using manifest `pivot_position_arch_local`, and use only its 2-6 simple collision boxes. Candy tips have separate pink/yellow Neon materials; foliage/crystals never collide. Whole-group previews and concept comparison are in [previews/portals/portals_vs_concepts.png](previews/portals/portals_vs_concepts.png).

## Pass 5 integrated gateways

Current authoritative pass: pass5. All earlier clearance descriptions are superseded. Zone A is X[-5,5] Y[0,12] Z[-12,4]; zone B is X[-11,11] Y[0,18] Z[4,34], in arch-local axes with +Z front. Scenery, canopy, lantern triangles and scenery collision boxes avoid these zones and the trigger. Geometry above Y18 may pass over the approach. Arch FBXs and original portal/shared assets are unchanged.

Integrated side scenery and overhead crowns, twelve rebuilt scenery files and six relocated Grove lanterns. Aurora crown has seven main crystals, a frosted-violet/icy-teal vertex gradient and separate Glow_Tips material for Neon (#9FE6F2). Place at manifest pivots; use only scenery collision boxes, never foliage/crystal mesh collision. Snowpuff position [-6.5,0,1.25], asset origin [0,0,0].

Fitcheck and FBX reimport: ALL PASS. Placed lobby total **112,285**, below 120,000. See [_src/pass5_summary.md](_src/pass5_summary.md) for all file/group triangle tables, measured zone distances, anchors, caveats and rebuild scripts. See [concept comparison](previews/portals/portals_vs_concepts.png) for updated eye/3/4 previews.

## Pass 6 targeted portal fixes

Current authoritative pass: pass6. Clearance remains zones A/B from pass5: X[-5,5] Y[0,12] Z[-12,4] and X[-11,11] Y[0,18] Z[4,34], with +Z front. All scenery/lantern triangles and collision boxes pass clearance. Original arch, surfaces, apron, signs and triggers are preserved.

Rebuilt leaning sandstone towers (9.907 and 9.669 degrees), front joint Neon candy clusters, cactus at 1.9905x prior height, domed autumn canopy, and seven-crystal saturated violet/teal crown. Glow_Tips: Material=Neon, Color=#9FE6F2. Preview Col wiring and actual violet pixels verified.

Fitcheck and FBX reimport: ALL PASS. Placed lobby total **106,405** triangles (<120,000). All files <20k. See [_src/pass6_summary.md](_src/pass6_summary.md) for measurements, hashes, triangles, zone minima, anchors, honest concept review and rebuild instructions; [comparison](previews/portals/portals_vs_concepts.png). Earlier pass summaries are historical.

## Pass 7 current authoritative assets

Pass7 supersedes earlier geometry descriptions. Fitcheck and FBX reimport ALL PASS. Placed lobby **110321** triangles; each file<20k. Fixed arches/surfaces/apron/signs/triggers are unchanged. Clearance zones A=X[-5,5]Y[0,12]Z[-12,4] and B=X[-11,11]Y[0,18]Z[4,34], arch-local+Z front, remain enforced.

Grove: chunkier150degree twisting trunks with three strands, root flares, billowy canopy cascading down outside sides toY6. Canyon: round bevelled sandstone bands,~27.7high/~9.78degree inward lean, doubled joint crystals3-5.7studs, cactus exactly1.5x original height with red/cream spiral disc. Aurora: exact supplied six-crystal source,276triangles,27stud longest crystal startsY14.5 and topsY41.09. Shared arch-base crown pivot; no collision boxes on pure crystals. Glow_Tips separate material: Material=Neon Color=#9FE6F2. Previews use imported Col and emission4.

See [_src/pass7_summary.md](_src/pass7_summary.md) for triangle/group totals, crystal table, zone minima, anchors, measurements and honest notes; [concept comparison](previews/portals/portals_vs_concepts.png) and [crown closeup](previews/portals/aurora_crown_closeup.png). Earlier summaries are historical. No Roblox applications were opened.

## Pass 8 current authoritative assets

Crown v2:6crystals,1716tris, tallest tip27.0studs, source unchanged with allowed SIDES16; Col violet-to-teal, Glow_Tips Neon #9FE6F2 emission1.5. Mirrored supplied rock-candy joint/base clusters use Glow_Crystal Neon from Col. Grove has three240degree spiral strands and varied layered leaf masses; snowy Aurora rubble grounded at legs. Fixed arches/surfaces/apron/signs/triggers unchanged.

Fitcheck/reimport ALL PASS. Placed lobby 107904tris, each mesh<20k; zonesA/B unchanged. Standard previews, neutral ambient0.9. See [_src/pass8_summary.md](_src/pass8_summary.md) for complete tables, anchors, pixels and honest notes about fixed embedded accents. No Roblox applications opened.

## Pass 9 current authoritative assets

Exact pass9_geo.py geometry wired into FBX export, manifest and Standard/Col previews. Flat12-sided beveled crown; explicit Sugarloaf crystals; three-strand twisted trunks with retained pass8 canopy; eight snowy rocks per pile. Glow_Tips Neon #9FE6F2, Glow_Crystal Neon from Col. Lantern anchors unchanged and cords contact canopy. Two collision boxes per trunk/rock pile, clear A/B and snowpuff. Fixed and unrelated exports unchanged.

Fitcheck and reimport ALL PASS; placed lobby 104452 triangles, every mesh<20k. See [_src/pass9_summary.md](_src/pass9_summary.md) for triangle/group tables, zone distances, anchors and honest notes. Source unchanged; no Roblox applications opened.

## Pass 10 current authoritative assets

Only Sugarloaf crystal west/east and Aurora rock west/east FBXs rebuilt using exact pass10_geo.py. Tighter candy bases, taller snowy mounds with two collision boxes per pile clear of zones A/B and the snowpuff footprint. All other FBXs and their manifest entries unchanged from pass9. Standard/Col previews use Glow_Crystal emission 0.2, pink #F59AC8 / yellow #FFF1A8; Glow_Tips remains 1.5. Neon in Roblox: keep Brightness low, or use SmoothPlastic with slight glow if Neon blows out.

Fitcheck and reimport ALL PASS; placed lobby 104772 triangles, every mesh <20k. See [_src/pass10_summary.md](_src/pass10_summary.md) for counts, group totals, clearance and caveats. Pixel checks: _src/preview_colour_pass10.json. Backup: _backup_pass9. No Roblox application opened.
