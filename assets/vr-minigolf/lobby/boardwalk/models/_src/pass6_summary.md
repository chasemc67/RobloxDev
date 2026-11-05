# Pass 6 targeted portal fixes

Placed lobby: **106,405 triangles**, 271 instances, 56 files. Every file <20,000; placed total <120,000.

Fitcheck and independent FBX reimport: ALL PASS. Immutable arch/portal/apron/nameplate/sign exports SHA256 match _backup_pass5; exact arch collision boxes and trigger metadata remain unchanged. No Roblox application was opened. Each own Blender invocation ran sequentially and completed.

## Geometry and measured lean

Tower centres are independently measured from imported FBX vertices in lower Y0.2-1.4 and upper Y25.8-27.7 slices (bounding-section centres, ignoring surface facet noise); angle = atan(abs(delta X)/delta Y).
- bw_scn_sugarloaf_tower_w: base [-10.105768203735352, 0.8297978639602661, -0.0], top [-5.584991455078125, 26.71430206298828, 0.04600340127944946], inward lean 9.907 degrees.
- bw_scn_sugarloaf_tower_e: base [10.047725677490234, 0.8297978639602661, -0.0], top [5.637421131134033, 26.71430206298828, 0.07581520080566406], inward lean 9.669 degrees.
- bw_scn_sugarloaf_lollipop_cactus: height/pass5 = 1.9905.

Four tower collision boxes track the inward centreline. Canyon joints carry 18 crystals per side: 12 at leg/lintel joints and 6 at bases, each 1.5-2.85 studs. Cactus is rebuilt at scale5.4 with five substantial stem rings and a larger proportional base.

## Triangles per file

| File | Pass6 tris | Instances | Placed tris |
|---|---:|---:|---:|
| bw_arch_aurora_archipelago | 8170 | 1 | 8170 |
| bw_arch_aurora_archipelago_lantern_01 | 144 | 1 | 144 |
| bw_arch_aurora_archipelago_lantern_02 | 144 | 1 | 144 |
| bw_arch_aurora_archipelago_snowpuff | 514 | 1 | 514 |
| bw_arch_lantern_grove | 13252 | 1 | 13252 |
| bw_arch_lantern_grove_lantern_01 | 148 | 1 | 148 |
| bw_arch_lantern_grove_lantern_02 | 148 | 1 | 148 |
| bw_arch_lantern_grove_lantern_03 | 148 | 1 | 148 |
| bw_arch_lantern_grove_lantern_04 | 148 | 1 | 148 |
| bw_arch_lantern_grove_lantern_05 | 148 | 1 | 148 |
| bw_arch_lantern_grove_lantern_06 | 148 | 1 | 148 |
| bw_arch_nameplate | 176 | 3 | 528 |
| bw_arch_sugarloaf_canyon | 7084 | 1 | 7084 |
| bw_arch_sugarloaf_canyon_lantern_01 | 144 | 1 | 144 |
| bw_arch_sugarloaf_canyon_lantern_02 | 144 | 1 | 144 |
| bw_barrel | 212 | 1 | 212 |
| bw_beach_umbrella | 334 | 1 | 334 |
| bw_bench | 300 | 6 | 1800 |
| bw_birdie_bites_shack | 3754 | 1 | 3754 |
| bw_coming_soon_sign | 184 | 2 | 368 |
| bw_course_board | 1606 | 1 | 1606 |
| bw_crate | 44 | 1 | 44 |
| bw_cup_flag | 140 | 2 | 280 |
| bw_deck_plank_a | 10 | 76 | 760 |
| bw_deck_plank_b | 10 | 76 | 760 |
| bw_flower_planter | 756 | 1 | 756 |
| bw_lantern_post | 224 | 6 | 1344 |
| bw_lantern_tree_canopy | 5600 | 1 | 5600 |
| bw_leaderboard_wall | 1736 | 1 | 1736 |
| bw_picnic_table | 588 | 1 | 588 |
| bw_pier_piling | 232 | 8 | 1856 |
| bw_portal_apron | 12 | 3 | 36 |
| bw_portal_surface_aurora_archipelago | 2 | 1 | 2 |
| bw_portal_surface_lantern_grove | 2 | 1 | 2 |
| bw_portal_surface_sugarloaf_canyon | 2 | 1 | 2 |
| bw_practice_green | 576 | 1 | 576 |
| bw_railing | 222 | 42 | 9324 |
| bw_rock_arch | 1164 | 1 | 1164 |
| bw_scn_aurora_crown | 7396 | 1 | 7396 |
| bw_scn_aurora_rocks_e | 2872 | 1 | 2872 |
| bw_scn_aurora_rocks_w | 2877 | 1 | 2877 |
| bw_scn_lantern_grove_planter_e | 2244 | 1 | 2244 |
| bw_scn_lantern_grove_planter_w | 2244 | 1 | 2244 |
| bw_scn_lantern_grove_trunk_e | 5716 | 1 | 5716 |
| bw_scn_lantern_grove_trunk_w | 5716 | 1 | 5716 |
| bw_scn_sugarloaf_crystals_e | 564 | 1 | 564 |
| bw_scn_sugarloaf_crystals_w | 564 | 1 | 564 |
| bw_scn_sugarloaf_lollipop_cactus | 1464 | 1 | 1464 |
| bw_scn_sugarloaf_tower_e | 3960 | 1 | 3960 |
| bw_scn_sugarloaf_tower_w | 3960 | 1 | 3960 |
| bw_sea_stacks | 1088 | 1 | 1088 |
| bw_signpost | 390 | 1 | 390 |
| bw_string_lights | 384 | 1 | 384 |
| bw_tee_mat | 12 | 2 | 24 |
| bw_windmill | 622 | 1 | 622 |
| bw_windmill_blades | 404 | 1 | 404 |

## Geometry change hashes

| Rebuilt Sugarloaf file | Pass5 tris | Pass6 tris | Pass6 SHA256 |
|---|---:|---:|---|
| bw_scn_sugarloaf_crystals_e | 532 | 564 | 9c67d54981620ed97efbba182489db8d575a563447103d9d47266d2a38ca257b |
| bw_scn_sugarloaf_crystals_w | 532 | 564 | e6e0fb30bd8d6da29f9199b66ee9bf5d0976724ef9e8b59d923da3593263446a |
| bw_scn_sugarloaf_lollipop_cactus | 504 | 1464 | 66dace87a1862c40e8ed6185ab6a2013535e7180ce6b829cdae8a88a9e127732 |
| bw_scn_sugarloaf_tower_e | 3372 | 3960 | 45801366835fd0edb670da350f5bfc8b25c22c7e9ba7dc0436a01b642eb59226 |
| bw_scn_sugarloaf_tower_w | 3372 | 3960 | 55ccac44e42491b6fe6f1848d3ea1587e397171250dc6b7b026a9c9f909e4465 |

## Portal group totals

Includes unchanged arch, moving parts, portal quad, scenery, apron and nameplate; Canyon/Aurora also include coming-soon sign.

| Course | Complete display tris |
|---|---:|
| lantern_grove | 30250 |
| sugarloaf_canyon | 18258 |
| aurora_archipelago | 22491 |

## Clearance minima

Arch-local +Z front. A: X[-5,5] Y[0,12] Z[-12,4]. B: X[-11,11] Y[0,18] Z[4,34]. Trigger X[-5,5] Y[0,10] Z[-1.5,1.5]. Full triangle-volume clipping and Euclidean vertex/face and edge/edge distances; collision boxes also checked. Only geometry above Y18 overhangs the approach.

| Mesh | Zone A | Zone B | Trigger |
|---|---:|---:|---:|
| bw_arch_aurora_archipelago_lantern_01 | 1.32447 | 2.36000 | 1.32447 |
| bw_arch_aurora_archipelago_lantern_02 | 1.32447 | 2.36000 | 1.32447 |
| bw_arch_lantern_grove_lantern_01 | 7.88774 | 2.01159 | 9.79472 |
| bw_arch_lantern_grove_lantern_02 | 7.88774 | 2.01159 | 9.79472 |
| bw_arch_lantern_grove_lantern_03 | 8.31459 | 2.75436 | 10.33325 |
| bw_arch_lantern_grove_lantern_04 | 8.31459 | 2.75436 | 10.33325 |
| bw_arch_lantern_grove_lantern_05 | 9.27000 | 3.62305 | 11.28931 |
| bw_arch_lantern_grove_lantern_06 | 9.27000 | 3.62305 | 11.28931 |
| bw_arch_sugarloaf_canyon_lantern_01 | 1.02447 | 2.01000 | 1.14422 |
| bw_arch_sugarloaf_canyon_lantern_02 | 1.02447 | 2.01000 | 1.14422 |
| bw_scn_aurora_crown | 6.08462 | 5.71141 | 8.70016 |
| bw_scn_aurora_rocks_e | 0.49986 | 1.40725 | 1.34911 |
| bw_scn_aurora_rocks_w | 0.64471 | 1.40725 | 1.40857 |
| bw_scn_lantern_grove_planter_e | 1.92600 | 1.57500 | 1.92600 |
| bw_scn_lantern_grove_planter_w | 1.92600 | 1.57500 | 1.92600 |
| bw_scn_lantern_grove_trunk_e | 1.20589 | 1.55507 | 1.20589 |
| bw_scn_lantern_grove_trunk_w | 1.20590 | 1.55507 | 1.20590 |
| bw_scn_sugarloaf_crystals_e | 1.65529 | 0.61700 | 3.19128 |
| bw_scn_sugarloaf_crystals_w | 1.65529 | 0.61700 | 3.02796 |
| bw_scn_sugarloaf_lollipop_cactus | 3.11215 | 1.95000 | 3.31632 |
| bw_scn_sugarloaf_tower_e | 0.47706 | 1.62768 | 0.85520 |
| bw_scn_sugarloaf_tower_w | 0.49217 | 1.71856 | 0.89666 |

## Anchors and materials

Grove canopy branches retain the pass5 hinge anchors, and lanterns were re-exported.

| Lantern | Arch-local anchor |
|---|---|
| bw_arch_lantern_grove_lantern_01 | [-8.2, 21.3, 2.3] |
| bw_arch_lantern_grove_lantern_02 | [8.2, 21.3, 2.3] |
| bw_arch_lantern_grove_lantern_03 | [-6, 22.3, 2.3] |
| bw_arch_lantern_grove_lantern_04 | [6, 22.3, 2.3] |
| bw_arch_lantern_grove_lantern_05 | [-3.5, 23.3, 2.3] |
| bw_arch_lantern_grove_lantern_06 | [3.5, 23.3, 2.3] |

Snowpuff: [-6.5,0,1.25], original export origin [0,0,0], unchanged clear footprint. All scenery uses manifest pivot_position_arch_local; collision centres are pivot-local. Mesh collision off; use only the recorded simple collision boxes.

Aurora: seven main crystals, sizes 5/7/8.8 studs, off-centre tallest X0.8, top Y27. Saturated #6A3FD6 base holds through the lower body then fades toward #7FE3E8. Col vertex colours are exported, explicitly wired in previews, and asserted after FBX import. Glow_Tips is a separate part/material: **Material=Neon, Color=#9FE6F2**, preview emission strength4. Shared BW_Atlas texture, opaque BW_Backdrop, no extra textures or exported lights.

eye preview upper-crown crop contains 14662 violet pixels with saturation >=0.45; mean saturation 0.580. See preview_colour_pass6.json for actual pixel test bounds.
34 preview upper-crown crop contains 23103 violet pixels with saturation >=0.45; mean saturation 0.590. See preview_colour_pass6.json for actual pixel test bounds.

## Honest concept review

Reviewed the complete side-by-side sheet and all six views; iterated canopy depth, crown position/footing, violet gradient and Neon preview exposure. Grove has a rounded billowy silhouette with overlapping large orange/red/gold blobs above Y18, hiding the overhead join and retaining hanging lanterns. Canyon reads as an inward leaning striped sandstone gateway; pink/yellow crystals are visible on the front joints and bases, and the cactus is doubled. Aurora has a violet crown joined into its shoulder rocks with icy tips and snow shelves; the crown covers the upper beam from the eye-height view.

The concept paintings have finer chipped surfaces, rich foliage, dramatic sunset lights and portal particles. These remain stylized toy meshes with preserved original arch silhouettes, no alpha foliage, no real asset lights. The doubled cactus is deliberately more dominant than the reference. The Aurora snow ledges and broad crown footing are chunky; the cyan emission tips can approach white at their brightest pixels. Original arch crystals/leaves remain visible below the new crowns. In-engine validation was prohibited; no Roblox or Studio launch/import/playtest was attempted.

## Rebuild

Run Blender directly, one own instance at a time: build_pass6.py, fitcheck.py -- --pass6, reimport_pass6.py, render_pass6.py. Then Python compose_pass3.py and finalize_pass6.py. Do not use run_blender.ps1. Backup _backup_pass5 contains pre-pass6 FBX, manifest, README, previews and all Python sources.
