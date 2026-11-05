# Props batch 2

Final inventory: 36 assets, 26,790 triangles, largest material mesh 4,416. Exported geometry fitcheck and FBX reimport: ALL PASS: YES. No remaining skipped pieces in this batch. Historical reports are preserved in _backup_pre_skipfix.

## Skip-fix

Source holes.json MD5: `2f1402fe19fc98a303c4e58dae680be9`. 16 requested assets built/rebuilt; 20 existing exports and their manifest records preserved byte for byte. Only requested FBX assets were exported. Overwritten original files are backed up under `_backup_pre_skipfix`, retaining their models-relative paths.

Changed assets: `h09_conch_exit`, `h09_conch_exit_ring`, `h09_coral_spit`, `h10_snow_walls_e`, `h10_snow_walls_w`, `h11_floe_frame_e`, `h11_floe_frame_w`, `h12_icebreaker`, `h15_ice_parapet`, `h15_lip_ice`, `h15_steps`, `h16_crescent_spout_e`, `h16_crescent_spout_w`, `h17_crystal_piers`, `h17_ice_bridge`, `h17_span_lamp`.

NOTE H17 crystal_piers and ice_bridge intentionally cover their own railed felt; below-felt deck exemption and own rail footprint containment remain checked.
NOTE H15 ice_parapet intentionally crosses the lip as a PlayerGuard visual; rail clearance and triangle budget pass; felt/head hits are reported and authorized by brief_skipfix.md. IceGuard Glass transparency 0.9; frosted Snow top edge.
NOTE H12 paddle_wheel unchanged: source lowest contact face remains 0.06 above felt; continuous sweep minimum and critical angle are retained in report.

Split packed-snow banks, individual floe marker posts and paired crescent horns match the new anchors. Conch exit mouth faces west toward the cup; teleport exit ring is flush at [11,0,-67]. Coral spit skirt is wholly under felt. H12 integrates both shrunk hull blocks in icebreaker; hull_face_skins is obsolete. H15 lip curtain uses 6.7 x 3.45 x 0.5 at [0,-3.85,-19.6]. Steps follow detailed source notes z -12..-19.35 (7.35 overall, five nominal 1.5 treads, last shortened); source approx_size depth6.7 is approximate. Handrail endpoint inset to -19.25; measured rail minimum is in table. H17 deck outer ends and rail skins stop at -16.65/-41.35; inner pier skirts stop at -24.85/-33.15 to retain 0.15 separation from the timed span. Reachable felt and gameplay rail geometry unchanged.

Unmoved Great Frozen Falls preserved at world base [20,36,-398], top [20,182,-398], 26x146x8; all 18 holes checked again using actual pre-existing FBX triangles (h15_fitcheck.json). Backdrop has collision/query/touch off and persistent streaming. Its original separate source scene remains intact and it is also included in current H15 context preview.

## Validation and placement

Triangle/OBB SAT tests use conservative L-infinity distance lower bounds, source skin footprint tolerance0.001, open felt slab/head volumes and slope shear. Static minimum0.1; authorized movers minimum0.05 in batch2, geyser0.1 in batch1; mover-to-dressing minimum0.15. Full continuous translation prisms or circumscribed 720-facet rotational sweeps; minima and angles in fitcheck JSON. Every material mesh and asset <20k triangles. FBX reimport checks hierarchy, materials, bounds, triangles and root origin.

World pivot = Ry(world_yaw) * local + offset; baked prop geometry has local yaw0. Blender +Y = Roblox -Z; forward -Z/upY, scale1, COPY/embed_textures enabled. One mesh per material; all props CanCollide false. Static props use no red/cream bands. Pivots and motion checked against source.

- h09_conch_exit: local [16.65, 0.0, -67.0], yaw 0.0, offset [535.0, 112.0, 230.0] -> world [551.65, 112.0, 163.0].
- h12_icebreaker: local [-3, 0, -21], yaw 90.0, offset [370.0, 146.0, -60.0] -> world [349.0, 146.0, -57.0].
- h10_snow_walls_w: local [-6.4, 0, -23.0], yaw 90.0, offset [510.0, 146.0, 60.0] -> world [487.0, 146.0, 66.4].

## Current inventory

| Asset | Tris | Max mesh | World pivot | Rail minimum |
|---|---:|---:|---|---:|
| h09_conch_entry | 1230 | 896 | [535.0, 112.0, 196.0] | 8.499999 |
| h09_reef_lagoon | 12 | 12 | [536.5, 110.8, 191.0] | 0.660000 |
| h09_reef_wall_skins | 1352 | 1196 | [535.0, 112.0, 230.0] | 100.000000 |
| h10_bobsled_hut | 344 | 168 | [504.0, 146.0, 67.5] | 0.125000 |
| h10_snow_wall_skins | 2560 | 2080 | [510.0, 146.0, 60.0] | 100.000000 |
| h11_fishing_hut | 224 | 188 | [401.0, 146.0, 10.0] | 0.280000 |
| h11_snowbank_skins | 3120 | 2760 | [410.0, 146.0, 40.0] | 100.000000 |
| h11_ice_floe | 386 | 140 | [410.0, 146.0, 12.0] | 0.150000 |
| h12_paddle_wheel | 1152 | 864 | [352.25, 150.16, -60.0] | 0.060000 |
| h13_hub_base | 4992 | 4416 | [120.0, 182.0, -266.0] | 5.499949 |
| h13_carousel_canopy | 188 | 92 | [120.0, 182.0, -266.0] | 12.599999 |
| h13_carousel_arms | 984 | 416 | [120.0, 182.0, -266.0] | 0.224999 |
| h16_moonstone_coping | 1040 | 920 | [-110.0, 222.0, -300.0] | 100.000000 |
| h16_moonwell | 552 | 376 | [-110.0, 221.2, -321.0] | 0.150000 |
| h17_aurora_ribbon | 80 | 40 | [-165.0, 222.0, -291.0] | 9.000000 |
| h17_aurora_span | 12 | 12 | [-165.0, 222.0, -291.0] | 0.150000 |
| h09_conch_ring | 384 | 384 | [535.0, 112.0, 197.0] | 10.200000 |
| h16_spout_glow | 260 | 260 | [-110.0, 221.2, -329.0] | 0.526362 |
| h17_span_respawn_stone | 12 | 12 | [-165.0, 222.0, -276.5] | 1.099999 |
| h09_conch_exit | 1230 | 896 | [551.65, 112.0, 163.0] | 0.720000 |
| h12_icebreaker | 672 | 564 | [349.0, 146.0, -57.0] | 0.150000 |
| h10_snow_walls_w | 376 | 188 | [487.0, 146.0, 66.4] | 0.150000 |
| h10_snow_walls_e | 376 | 188 | [493.825, 146.0, 48.599999999999994] | 0.150000 |
| h11_floe_frame_w | 204 | 188 | [398.0, 146.0, 12.0] | 0.570000 |
| h11_floe_frame_e | 204 | 188 | [414.65, 146.0, 12.0] | 0.252666 |
| h16_crescent_spout_w | 76 | 76 | [-120.9, 222.0, -330.0] | 0.300000 |
| h16_crescent_spout_e | 76 | 76 | [-99.1, 222.0, -330.0] | 0.300000 |
| h09_coral_spit | 24 | 12 | [535.0, 110.8, 201.1] | 0.300000 |
| h09_conch_exit_ring | 384 | 384 | [546.0, 112.0, 163.0] | 2.299999 |
| h15_lip_ice | 68 | 68 | [12.0, 178.15, -353.6] | 0.150000 |
| h15_ice_parapet | 24 | 12 | [12.0, 182.0, -353.8] | 0.150000 |
| h15_steps | 236 | 236 | [4.25, 178.0, -349.675] | 0.150000 |
| h17_crystal_piers | 184 | 160 | [-165.0, 222.0, -291.0] | 0.150000 |
| h17_ice_bridge | 48 | 24 | [-159.0, 222.0, -291.0] | 0.150000 |
| h17_span_lamp | 60 | 44 | [-167.75, 222.0, -278.95] | 0.335870 |
| h15_great_frozen_falls | 3664 | 2068 | [20.0, 36.0, -398.0] | 20.990487 |

## Rebuild and previews

Source geometry is retained in parts.json, palette.json and triangles.json. skipfix_prepare.py reuses established geometry builders; build_skipfix.py exports only skipfix_ids.json while constructing the complete context scene. Final refinements are in skipfix_finish_setup.py/build_skipfix_guard.py (glass parapet and preserved waterfall) and skipfix_orient_exit.py/build_skipfix_exit.py (west-facing shell). Historical original generators target old source hashes and must not be run blindly over these final parts. Use run_blender.ps1 only, one headless CPU Blender process at a time; fitcheck_batch*.py then verify_batch*.py. Blender runner logs and final props_batch*.blend retained.

12-sample CPU Cycles, 1280x960. Changed hole/asset previews and silhouette comparisons regenerated; both contact sheets refreshed. All source silhouette sheets and relevant concepts visually inspected; numeric current source takes precedence over older sheet dimensions. No GUI, Studio, restart, process killing or external messages.


## Rev4

Bridge: bevelled timber rails, posts every 4 studs, connected lumpy ~0.3 white snow caps and frosted deck edges. Parapet: seven chunky ice blocks with tops varying -0.4..+0.4, frosted tops and front icicles. Spit: bumpy pink/purple rock sides with polyp bumps, irregular skirt flaring 0.3; nose flare locally reduced to 0.18. Top lowered below the felt slab to y=-0.45. Purple rock uses the existing AuroraViolet hue without emission.

| Asset | Tris before | Tris after | Rail minimum |
|---|---:|---:|---:|
| h09_coral_spit | 24 | 2696 | 0.279818 |
| h15_ice_parapet | 24 | 920 | 0.159000 |
| h17_ice_bridge | 48 | 2560 | 0.150000 |

NOTE H17 crystal_piers and ice_bridge intentionally cover their own railed felt; own rail skins and below-felt decks are exempt only within authorized footprints.
NOTE H15 ice_parapet intentionally crosses the lip; felt/head overlap authorized, rail clearance still checked. IceGuard transparency 0.9 retained.
NOTE H12 paddle_wheel unchanged; authorized 0.06 felt clearance retained.
NOTE Rev4 coral_spit nose flare reduced locally from 0.3 to 0.18; top y=-0.45 below felt slab.

Every changed piece <=3000 triangles; every material mesh <20k. Exported triangle/OBB fitcheck ALL PASS: YES; FBX reimport ALL PASS: YES. Unrelated FBX hashes and manifest records unchanged. Backups: `_backup_pre_rev4/`, retaining models-relative paths. Changed hole/asset previews, silhouette comparisons and contact sheet refreshed. holes.json MD5 unchanged: `2f1402fe19fc98a303c4e58dae680be9`.

Source pipeline: rev4.py preparation, amend_rev4.py and amend_spit_rev4.py visual/budget refinements, selective build_rev4.py/build_ice_rev4.py/build_spit_rev4.py, fitcheck_batch*.py and verify_batch*.py. All Blender jobs ran headless, serially through run_blender.ps1 with Cycles CPU. Current parts.json is the final source; historical generators must not be rerun blindly. Evidence logs and rev4_audit.json are in props_batch2.
