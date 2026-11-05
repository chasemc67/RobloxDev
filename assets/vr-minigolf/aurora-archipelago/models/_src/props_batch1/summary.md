# Props batch 1

Final inventory: 38 assets, 27,878 triangles, largest material mesh 3,008. Exported geometry fitcheck and FBX reimport: ALL PASS: YES. No remaining skipped pieces in this batch. Historical reports are preserved in _backup_pre_skipfix.

## Skip-fix

Source holes.json MD5: `2f1402fe19fc98a303c4e58dae680be9`. 2 requested assets built/rebuilt; 36 existing exports and their manifest records preserved byte for byte. Only requested FBX assets were exported. Overwritten original files are backed up under `_backup_pre_skipfix`, retaining their models-relative paths.

Changed assets: `h05_cliff_face_e`, `h05_cliff_face_w`.

NOTE H1 collider gap 0.0786796564 retained under existing collider-skin ruling.

H5 basalt faces use exact 10.85 x 3.35 x 0.5 source boxes with inset frost streaks and brass shaft-edge rivets. Minimum conservative rail clearance is 0.1499996.

## Validation and placement

Triangle/OBB SAT tests use conservative L-infinity distance lower bounds, source skin footprint tolerance0.001, open felt slab/head volumes and slope shear. Static minimum0.1; authorized movers minimum0.05 in batch2, geyser0.1 in batch1; mover-to-dressing minimum0.15. Full continuous translation prisms or circumscribed 720-facet rotational sweeps; minima and angles in fitcheck JSON. Every material mesh and asset <20k triangles. FBX reimport checks hierarchy, materials, bounds, triangles and root origin.

World pivot = Ry(world_yaw) * local + offset; baked prop geometry has local yaw0. Blender +Y = Roblox -Z; forward -Z/upY, scale1, COPY/embed_textures enabled. One mesh per material; all props CanCollide false. Static props use no red/cream bands. Pivots and motion checked against source.

- h05_cliff_face_w: local [-7.075, 0, -28.4], yaw -90.0, offset [215.0, 84.0, 420.0] -> world [243.4, 84.0, 412.925].
- h05_cliff_face_e: local [7.075, 0, -28.4], yaw -90.0, offset [215.0, 84.0, 420.0] -> world [243.4, 84.0, 427.075].

## Current inventory

| Asset | Tris | Max mesh | World pivot | Rail minimum |
|---|---:|---:|---|---:|
| h01_harbour_lantern | 444 | 264 | [-156.0, 60.0, 521.0] | 1.800000 |
| h01_snow_boulder | 256 | 128 | [-151.3, 60.0, 509.2] | 1.788000 |
| h02_rookery_drift | 752 | 376 | [-93.0, 60.0, 480.0] | 0.110000 |
| h02_lintel_left | 644 | 408 | [-99.0, 68.0, 470.5] | 0.110000 |
| h02_lintel_mid | 644 | 408 | [-99.0, 68.0, 480.0] | 0.110000 |
| h02_lintel_right | 644 | 408 | [-99.0, 68.0, 489.0] | 0.110000 |
| h02_lantern_cue | 224 | 136 | [-69.0, 69.0, 470.25] | 6.600000 |
| h02_lantern_crook | 112 | 96 | [-69.0, 60.0, 466.4] | 0.924999 |
| h02_sign_left | 221 | 188 | [-103.0, 60.0, 466.1] | 0.500000 |
| h02_sign_right | 221 | 188 | [-103.0, 60.0, 493.9] | 0.500000 |
| h03_glimmer_islet | 1384 | 1032 | [2.426406871192853, 40.0, 461.5147186257614] | 5.500000 |
| h03_ice_plank | 60 | 24 | [-13.83704909609774, 60.0, 443.83704909609776] | 0.099999 |
| h03_ice_bridge | 628 | 376 | [-9.594408408978452, 60.0, 448.079689783217] | 4.499999 |
| h05_geyser_column | 372 | 224 | [241.5, 84.0, 420.0] | 3.500000 |
| h05_steamwhistle_geyser | 376 | 220 | [251.0, 88.0, 403.25] | 0.749999 |
| h05_signal_lamp | 376 | 188 | [242.6, 86.0, 410.5] | 0.500000 |
| h05_geyser_steps | 220 | 220 | [238.0, 84.0, 435.0] | 0.489999 |
| h07_coral_w1 | 520 | 364 | [358.5, 112.0, 319.0] | 1.349767 |
| h07_coral_w2 | 688 | 480 | [356.0, 112.0, 312.0] | 3.266928 |
| h07_coral_w3 | 856 | 856 | [359.0, 112.0, 305.5] | 0.903147 |
| h07_coral_w4 | 520 | 364 | [355.0, 112.0, 300.0] | 4.152500 |
| h07_coral_w5 | 688 | 480 | [358.0, 112.0, 295.0] | 1.646616 |
| h07_coral_e6 | 856 | 856 | [372.0, 112.0, 316.5] | 1.663269 |
| h07_coral_e7 | 520 | 364 | [374.5, 112.0, 309.5] | 3.689259 |
| h07_coral_e8 | 688 | 480 | [371.0, 112.0, 304.0] | 0.864852 |
| h07_coral_e9 | 856 | 856 | [373.5, 112.0, 298.5] | 2.936003 |
| h07_coral_e10 | 520 | 364 | [371.5, 112.0, 294.5] | 1.367353 |
| h07_mogul_trim | 3200 | 3008 | [365.0, 112.0, 308.0] | 0.100000 |
| h08_giant_coral | 856 | 596 | [419.5, 112.0, 282.0] | 3.301210 |
| h08_coral_1 | 700 | 492 | [428.0, 112.0, 290.0] | 2.727210 |
| h08_coral_2 | 868 | 608 | [433.0, 112.0, 284.5] | 1.730230 |
| h08_coral_3 | 532 | 376 | [426.8, 112.0, 279.5] | 1.530229 |
| h08_coral_4 | 700 | 492 | [431.5, 112.0, 275.0] | 3.227209 |
| h08_coral_5 | 868 | 608 | [428.5, 112.0, 269.5] | 3.516990 |
| h08_coral_6 | 532 | 376 | [433.5, 112.0, 265.5] | 1.383970 |
| h08_coral_7 | 700 | 492 | [432.0, 112.0, 255.0] | 5.868629 |
| h05_cliff_face_w | 2316 | 1128 | [243.4, 84.0, 412.925] | 0.150000 |
| h05_cliff_face_e | 2316 | 1128 | [243.4, 84.0, 427.075] | 0.150000 |

## Rebuild and previews

Source geometry is retained in parts.json, palette.json and triangles.json. skipfix_prepare.py reuses established geometry builders; build_skipfix.py exports only skipfix_ids.json while constructing the complete context scene. Final refinements are in skipfix_finish_setup.py/build_skipfix_guard.py (glass parapet and preserved waterfall) and skipfix_orient_exit.py/build_skipfix_exit.py (west-facing shell). Historical original generators target old source hashes and must not be run blindly over these final parts. Use run_blender.ps1 only, one headless CPU Blender process at a time; fitcheck_batch*.py then verify_batch*.py. Blender runner logs and final props_batch*.blend retained.

12-sample CPU Cycles, 1280x960. Changed hole/asset previews and silhouette comparisons regenerated; both contact sheets refreshed. All source silhouette sheets and relevant concepts visually inspected; numeric current source takes precedence over older sheet dimensions. No GUI, Studio, restart, process killing or external messages.


## Coral rev3

18 coral assets rebuilt with short thick trunks, three branching stages into 3–5 flattened fans, overlapping rounded swollen crown tips and mint neon cores. All anchors, pivots, colours and unrelated exports preserved. Headless Blender via run_blender.ps1, Cycles CPU. Exported triangle fitcheck ALL PASS: YES; FBX reimport ALL PASS: YES.

| Coral | Tris before | Tris after |
|---|---:|---:|
| h07_coral_w1 | 520 | 716 |
| h07_coral_w2 | 688 | 436 |
| h07_coral_w3 | 856 | 576 |
| h07_coral_w4 | 520 | 716 |
| h07_coral_w5 | 688 | 436 |
| h07_coral_e6 | 856 | 576 |
| h07_coral_e7 | 520 | 716 |
| h07_coral_e8 | 688 | 436 |
| h07_coral_e9 | 856 | 576 |
| h07_coral_e10 | 520 | 436 |
| h08_giant_coral | 856 | 716 |
| h08_coral_1 | 700 | 588 |
| h08_coral_2 | 868 | 728 |
| h08_coral_3 | 532 | 448 |
| h08_coral_4 | 700 | 588 |
| h08_coral_5 | 868 | 728 |
| h08_coral_6 | 532 | 448 |
| h08_coral_7 | 700 | 588 |

Giant crown limited from 7 to 4 studs wide to remain inside its exact 4×14×4 occluder; coral height remains 14. H8 narrow bumper crown depths limited from .96 to .8 to remain in the source occluders, with exact collider bases retained; coral height remains 2.4 above the 1.6 base. Other clumps retain requested crown sizes. Every coral remains under 900 tris; every material mesh under 20k.

Current-state backup: `models\_src\props_batch1\_backup_rev2_corals\current_before_rev3_20261013_030801_487976`. Original backup preserved. Evidence: coral_rev3_preflight.log, coral_rev3_exported.log, coral_rev3_verify.log, coral_rev3_unchanged.json.


## Rev4

18 corals: 3-5 separate flattened fan lobes with visible crown gaps, rounded neon tips and trunks tapering 0.15H to 0.10H at the 0.3H split. Exact H8 collider bases, anchors, pivots and existing hues preserved. Prior giant/narrow-footprint limits retained.

| Asset | Tris before | Tris after | Rail minimum |
|---|---:|---:|---:|
| h07_coral_w1 | 716 | 868 | 1.152637 |
| h07_coral_w2 | 436 | 532 | 2.999999 |
| h07_coral_w3 | 576 | 700 | 0.724029 |
| h07_coral_w4 | 716 | 868 | 4.125000 |
| h07_coral_w5 | 436 | 532 | 1.499999 |
| h07_coral_e6 | 576 | 700 | 1.499999 |
| h07_coral_e7 | 716 | 868 | 3.625000 |
| h07_coral_e8 | 436 | 532 | 0.749999 |
| h07_coral_e9 | 576 | 700 | 2.572114 |
| h07_coral_e10 | 436 | 532 | 1.148883 |
| h08_giant_coral | 716 | 868 | 2.950000 |
| h08_coral_1 | 588 | 712 | 2.727210 |
| h08_coral_2 | 728 | 880 | 1.730230 |
| h08_coral_3 | 448 | 544 | 1.530229 |
| h08_coral_4 | 588 | 712 | 3.227209 |
| h08_coral_5 | 728 | 880 | 3.516990 |
| h08_coral_6 | 448 | 544 | 1.383970 |
| h08_coral_7 | 588 | 712 | 5.868629 |

NOTE H1 collider-to-rail gap 0.0786796564 retained under existing exception.

Every changed piece <=3000 triangles; every material mesh <20k. Exported triangle/OBB fitcheck ALL PASS: YES; FBX reimport ALL PASS: YES. Unrelated FBX hashes and manifest records unchanged. Backups: `_backup_pre_rev4/`, retaining models-relative paths. Changed hole/asset previews, silhouette comparisons and contact sheet refreshed. holes.json MD5 unchanged: `2f1402fe19fc98a303c4e58dae680be9`.

Source pipeline: rev4.py preparation, amend_rev4.py and amend_spit_rev4.py visual/budget refinements, selective build_rev4.py/build_ice_rev4.py/build_spit_rev4.py, fitcheck_batch*.py and verify_batch*.py. All Blender jobs ran headless, serially through run_blender.ps1 with Cycles CPU. Current parts.json is the final source; historical generators must not be rerun blindly. Evidence logs and rev4_audit.json are in props_batch2.


## Coral rev5

18 coral assets: straight flat paddles with one fork per lobe and 6-10 rounded neon tips. Exact collider bases, pivots, anchors and colours preserved. Full split-to-top crown is necessarily taller than wide: fixed 0.7H height and at most 0.5H width. Upper fork/tip cluster carries strong splay; long risers are steeper than the nominal 35-55 degrees to preserve these incompatible dimensions. Giant retains 4-stud width due to its occluder; narrow skins retain 0.8 depth. No rail-driven splay reductions.

| Coral | Tris | Crown width | Crown height | W:H |
|---|---:|---:|---:|---:|
| h07_coral_w1 | 844 | 2.2500 | 3.2530 | 0.6917 |
| h07_coral_w2 | 844 | 3.0000 | 4.3064 | 0.6966 |
| h07_coral_w3 | 844 | 1.7500 | 2.5488 | 0.6866 |
| h07_coral_w4 | 844 | 2.7500 | 3.9555 | 0.6952 |
| h07_coral_w5 | 844 | 2.0000 | 2.9012 | 0.6894 |
| h07_coral_e6 | 844 | 2.0000 | 2.9012 | 0.6894 |
| h07_coral_e7 | 844 | 2.7500 | 3.9555 | 0.6952 |
| h07_coral_e8 | 844 | 1.5000 | 2.1953 | 0.6833 |
| h07_coral_e9 | 844 | 3.0000 | 4.3064 | 0.6966 |
| h07_coral_e10 | 844 | 2.2500 | 3.2530 | 0.6917 |
| h08_giant_coral | 844 | 4.0000 | 9.8772 | 0.4050 |
| h08_coral_1 | 856 | 1.2000 | 1.7686 | 0.6785 |
| h08_coral_2 | 856 | 1.2000 | 1.7686 | 0.6785 |
| h08_coral_3 | 856 | 1.2000 | 1.7686 | 0.6785 |
| h08_coral_4 | 856 | 1.2000 | 1.7686 | 0.6785 |
| h08_coral_5 | 856 | 1.2000 | 1.7686 | 0.6785 |
| h08_coral_6 | 856 | 1.2000 | 1.7686 | 0.6785 |
| h08_coral_7 | 856 | 1.2000 | 1.7686 | 0.6785 |

Exported triangle fitcheck and FBX reimport ALL PASS. Every coral <900 tris, all unrelated FBX SHA256 hashes and manifest records unchanged. holes.json MD5 2f1402fe19fc98a303c4e58dae680be9. Backups: `_backup_rev4_corals/`. CPU Blender serially through run_blender.ps1. Front comparisons use common stud scale; full sheet remains authoritative.


## Coral rev6

18 coral assets revised: bare trunk splits at 0.5H; flat paddles fork into six overlapping rounded blobs forming one solid lumpy dome, with neon tip cores. Crown spans 0.5H by 0.45H, depth 0.4H and top 0.95H. Giant retains its exact 4-wide occluder exception; narrow skins keep existing depth envelope. No rail-driven crown reductions. Exact collider bases, pivots, anchors and colours preserved.

| Coral | Tris | MEASURED crown width | MEASURED crown height | W:H |
|---|---:|---:|---:|---:|
| h07_coral_w1 | 844 | 2.2500 | 2.0250 | 1.1111 |
| h07_coral_w2 | 844 | 3.0000 | 2.7000 | 1.1111 |
| h07_coral_w3 | 844 | 1.7500 | 1.5750 | 1.1111 |
| h07_coral_w4 | 844 | 2.7500 | 2.4750 | 1.1111 |
| h07_coral_w5 | 844 | 2.0000 | 1.8000 | 1.1111 |
| h07_coral_e6 | 844 | 2.0000 | 1.8000 | 1.1111 |
| h07_coral_e7 | 844 | 2.7500 | 2.4750 | 1.1111 |
| h07_coral_e8 | 844 | 1.5000 | 1.3500 | 1.1111 |
| h07_coral_e9 | 844 | 3.0000 | 2.7000 | 1.1111 |
| h07_coral_e10 | 844 | 2.2500 | 2.0250 | 1.1111 |
| h08_giant_coral | 856 | 4.0000 | 6.3000 | 0.6349 |
| h08_coral_1 | 856 | 1.2000 | 1.0800 | 1.1111 |
| h08_coral_2 | 856 | 1.2000 | 1.0800 | 1.1111 |
| h08_coral_3 | 856 | 1.2000 | 1.0800 | 1.1111 |
| h08_coral_4 | 856 | 1.2000 | 1.0800 | 1.1111 |
| h08_coral_5 | 856 | 1.2000 | 1.0800 | 1.1111 |
| h08_coral_6 | 856 | 1.2000 | 1.0800 | 1.1111 |
| h08_coral_7 | 856 | 1.2000 | 1.0800 | 1.1111 |

Exported triangle fitcheck and FBX reimport ALL PASS. Every coral <3000 tris, all unrelated FBX SHA256 hashes and manifest records unchanged. holes.json MD5 2f1402fe19fc98a303c4e58dae680be9. Backups: `_backup_rev5_corals/`. CPU Blender serially through run_blender.ps1. Front comparisons use common stud scale; full sheet remains authoritative.


## Giant coral rev7

Only `h08_giant_coral` changed (per Game Art Bot): bare trunk shortened to ~3.2 studs (rev6 split was 6.65), topped by three stacked, offset, overlapping lumpy domes of different sizes (big low-left, medium mid-right, small top-left), each built from a core dome + 5 shoulder lumps + a top lump, with 9 mint neon cores. Exact 4-stud occluder cap kept in X and Z.

| Coral | Tris | W | H | D | Nearest rail | Clearance | Fitcheck |
|---|---:|---:|---:|---:|---|---:|---|
| h08_giant_coral | 2376 | 4.000 | 9.300 | 4.000 | rail1 | 2.950 | PASS |

Pivot, anchor, yaw, colours/materials and can_collide=false unchanged. All other FBX SHA256 hashes and manifest records unchanged. holes.json MD5 2f1402fe19fc98a303c4e58dae680be9. FBX reimport PASS. Backup: `_backup_rev6_giant_coral/`.


## Polish

18 requested corals: original rev6 crowns and giant rev7 three stacked domes retained; exact bases and placements preserved. Thin leaning trunks fork twice into the retained lumps, with eight small rounded AuroraMint Neon gap cores. Small corals <=900 triangles; giant <3000, 4-stud cap retained. Collision/query/touch disabled.

Current-source Blender actual triangles: ALL PASS. FBX re-import: PASS.

| ID | Old tris | New tris | Nearest rail | Nearest felt | Heavy per hole |
|---|---:|---:|---|---|---:|
| h07_coral_e10 | 844 | 888 | rail17 1.5276 | mogul8 1.3750 | 1 |
| h07_coral_e6 | 844 | 888 | rail22 1.5000 | mogul2 2.0000 | 1 |
| h07_coral_e7 | 844 | 888 | rail20 3.6250 | mogul3 4.1250 | 1 |
| h07_coral_e8 | 844 | 888 | rail19 0.7894 | mogul5 1.2894 | 1 |
| h07_coral_e9 | 844 | 888 | rail17 2.6978 | mogul6 3.0000 | 1 |
| h07_coral_w1 | 844 | 888 | rail2 1.5437 | mogul1 1.3750 | 1 |
| h07_coral_w2 | 844 | 888 | rail3 3.0016 | mogul2 3.5000 | 1 |
| h07_coral_w3 | 844 | 888 | rail6 0.8860 | mogul5 1.1250 | 1 |
| h07_coral_w4 | 844 | 888 | rail7 4.1250 | mogul5 4.6250 | 1 |
| h07_coral_w5 | 844 | 888 | rail9 1.5000 | mogul8 2.0000 | 1 |
| h08_coral_1 | 856 | 900 | rail1 2.7272 | source skin | 1 |
| h08_coral_2 | 856 | 900 | rail7 1.7302 | source skin | 1 |
| h08_coral_3 | 856 | 900 | rail1 1.5302 | source skin | 1 |
| h08_coral_4 | 856 | 900 | rail7 3.2272 | source skin | 1 |
| h08_coral_5 | 856 | 900 | rail1 3.5170 | source skin | 1 |
| h08_coral_6 | 856 | 900 | rail7 1.3840 | source skin | 1 |
| h08_coral_7 | 856 | 900 | rail6 5.8686 | source skin | 1 |
| h08_giant_coral | 2376 | 2676 | rail1 2.9500 | reef_a 2.5000 | 1 |

Pre-existing out-of-scope budget note: h07_mogul_trim remains 3,200 triangles, unchanged; every requested polished asset is below 3,000.

Glow cores emerge 0.133-0.200 studs beyond retained crown surfaces; the original envelope limits a few narrow bumper cores. Most cores emerge 0.200 studs.

Run `python polish_corals.py`, `python fitcheck_batch1.py --preflight`, `python finalize_polish_corals.py`. After the selective user Blender build, run `python fitcheck_batch1.py` and `python finalize_polish_corals.py`. Build requires `-- --only h07_coral_e10,h07_coral_e6,h07_coral_e7,h07_coral_e8,h07_coral_e9,h07_coral_w1,h07_coral_w2,h07_coral_w3,h07_coral_w4,h07_coral_w5,h08_coral_1,h08_coral_2,h08_coral_3,h08_coral_4,h08_coral_5,h08_coral_6,h08_coral_7,h08_giant_coral`.
