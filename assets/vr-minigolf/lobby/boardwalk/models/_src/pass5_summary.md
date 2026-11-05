# Pass 5 integrated portal gateways

All three original arch FBXs, their 16x18x4 envelopes, three collision boxes, portal quads, apron, nameplate, sign and trigger metadata remain unchanged from pass4. Rebuilt twelve scenery files and six Grove lantern files using the existing generator/export pipeline. No Roblox application was opened.

## Clearance and validation

Arch-local axes: X east, Y up, +Z front/approach. This replaces all earlier pass4 clearance rules. Zone A: X[-5,5] Y[0,12] Z[-12,4]. Zone B: X[-11,11] Y[0,18] Z[4,34]. Trigger: X[-5,5] Y[0,10] Z[-1.5,1.5]. Scenery and lantern triangles and scenery collision boxes avoid all three volumes. Below Y18, pieces beside the opening and behind Z4 may hug the arch. Only geometry above Y18 passes over the expanded approach.
Fitcheck and independent FBX reimport: ALL PASS. Distances use triangle/box vertex-face and edge-edge distances with full triangle-volume clipping, not vertex sampling. Every individual mesh is <20k triangles. Placed lobby total is calculated from every manifest instance including all three portal groups. Arch SHA256 preservation is checked against _backup_pass4.

## Triangles per exported file

| File | Triangles | Instances | Placed triangles |
|---|---:|---:|---:|
| bw_arch_aurora_archipelago.fbx | 8,170 | 1 | 8,170 |
| bw_arch_aurora_archipelago_lantern_01.fbx | 144 | 1 | 144 |
| bw_arch_aurora_archipelago_lantern_02.fbx | 144 | 1 | 144 |
| bw_arch_aurora_archipelago_snowpuff.fbx | 514 | 1 | 514 |
| bw_arch_lantern_grove.fbx | 13,252 | 1 | 13,252 |
| bw_arch_lantern_grove_lantern_01.fbx | 148 | 1 | 148 |
| bw_arch_lantern_grove_lantern_02.fbx | 148 | 1 | 148 |
| bw_arch_lantern_grove_lantern_03.fbx | 148 | 1 | 148 |
| bw_arch_lantern_grove_lantern_04.fbx | 148 | 1 | 148 |
| bw_arch_lantern_grove_lantern_05.fbx | 148 | 1 | 148 |
| bw_arch_lantern_grove_lantern_06.fbx | 148 | 1 | 148 |
| bw_arch_nameplate.fbx | 176 | 3 | 528 |
| bw_arch_sugarloaf_canyon.fbx | 7,084 | 1 | 7,084 |
| bw_arch_sugarloaf_canyon_lantern_01.fbx | 144 | 1 | 144 |
| bw_arch_sugarloaf_canyon_lantern_02.fbx | 144 | 1 | 144 |
| bw_barrel.fbx | 212 | 1 | 212 |
| bw_beach_umbrella.fbx | 334 | 1 | 334 |
| bw_bench.fbx | 300 | 6 | 1,800 |
| bw_birdie_bites_shack.fbx | 3,754 | 1 | 3,754 |
| bw_coming_soon_sign.fbx | 184 | 2 | 368 |
| bw_course_board.fbx | 1,606 | 1 | 1,606 |
| bw_crate.fbx | 44 | 1 | 44 |
| bw_cup_flag.fbx | 140 | 2 | 280 |
| bw_deck_plank_a.fbx | 10 | 76 | 760 |
| bw_deck_plank_b.fbx | 10 | 76 | 760 |
| bw_flower_planter.fbx | 756 | 1 | 756 |
| bw_lantern_post.fbx | 224 | 6 | 1,344 |
| bw_lantern_tree_canopy.fbx | 5,600 | 1 | 5,600 |
| bw_leaderboard_wall.fbx | 1,736 | 1 | 1,736 |
| bw_picnic_table.fbx | 588 | 1 | 588 |
| bw_pier_piling.fbx | 232 | 8 | 1,856 |
| bw_portal_apron.fbx | 12 | 3 | 36 |
| bw_portal_surface_aurora_archipelago.fbx | 2 | 1 | 2 |
| bw_portal_surface_lantern_grove.fbx | 2 | 1 | 2 |
| bw_portal_surface_sugarloaf_canyon.fbx | 2 | 1 | 2 |
| bw_practice_green.fbx | 576 | 1 | 576 |
| bw_railing.fbx | 222 | 42 | 9,324 |
| bw_rock_arch.fbx | 1,164 | 1 | 1,164 |
| bw_scn_aurora_crown.fbx | 7,316 | 1 | 7,316 |
| bw_scn_aurora_rocks_e.fbx | 2,872 | 1 | 2,872 |
| bw_scn_aurora_rocks_w.fbx | 2,877 | 1 | 2,877 |
| bw_scn_lantern_grove_planter_e.fbx | 2,244 | 1 | 2,244 |
| bw_scn_lantern_grove_planter_w.fbx | 2,244 | 1 | 2,244 |
| bw_scn_lantern_grove_trunk_e.fbx | 9,796 | 1 | 9,796 |
| bw_scn_lantern_grove_trunk_w.fbx | 9,796 | 1 | 9,796 |
| bw_scn_sugarloaf_crystals_e.fbx | 532 | 1 | 532 |
| bw_scn_sugarloaf_crystals_w.fbx | 532 | 1 | 532 |
| bw_scn_sugarloaf_lollipop_cactus.fbx | 504 | 1 | 504 |
| bw_scn_sugarloaf_tower_e.fbx | 3,372 | 1 | 3,372 |
| bw_scn_sugarloaf_tower_w.fbx | 3,372 | 1 | 3,372 |
| bw_sea_stacks.fbx | 1,088 | 1 | 1,088 |
| bw_signpost.fbx | 390 | 1 | 390 |
| bw_string_lights.fbx | 384 | 1 | 384 |
| bw_tee_mat.fbx | 12 | 2 | 24 |
| bw_windmill.fbx | 622 | 1 | 622 |
| bw_windmill_blades.fbx | 404 | 1 | 404 |

## Portal group totals

Shared display items include apron/nameplate and coming-soon sign for Canyon/Aurora. These totals count one complete group; the lobby total uses actual manifest instance counts.

| Course | Arch and moving parts plus quad | Scenery | Complete display |
|---|---:|---:|---:|
| lantern_grove | 14,142 | 24,080 | 38,410 |
| sugarloaf_canyon | 7,374 | 8,312 | 16,058 |
| aurora_archipelago | 8,974 | 13,065 | 22,411 |

**Placed lobby total: 112,285 triangles / <120,000.** 271 instances, 56 unique files.

## Minimum distances per scenery/accessory file

| File | Zone A (studs) | Zone B (studs) | Trigger (studs) |
|---|---:|---:|---:|
| bw_arch_aurora_archipelago_lantern_01.fbx | 1.32447 | 2.36000 | 1.32447 |
| bw_arch_aurora_archipelago_lantern_02.fbx | 1.32447 | 2.36000 | 1.32447 |
| bw_arch_lantern_grove_lantern_01.fbx | 7.88774 | 2.01159 | 9.79472 |
| bw_arch_lantern_grove_lantern_02.fbx | 7.88774 | 2.01159 | 9.79472 |
| bw_arch_lantern_grove_lantern_03.fbx | 8.31459 | 2.75436 | 10.33325 |
| bw_arch_lantern_grove_lantern_04.fbx | 8.31459 | 2.75436 | 10.33325 |
| bw_arch_lantern_grove_lantern_05.fbx | 9.27000 | 3.62305 | 11.28931 |
| bw_arch_lantern_grove_lantern_06.fbx | 9.27000 | 3.62305 | 11.28931 |
| bw_arch_sugarloaf_canyon_lantern_01.fbx | 1.02447 | 2.01000 | 1.14422 |
| bw_arch_sugarloaf_canyon_lantern_02.fbx | 1.02447 | 2.01000 | 1.14422 |
| bw_scn_aurora_crown.fbx | 6.19030 | 9.34144 | 9.13971 |
| bw_scn_aurora_rocks_e.fbx | 0.49986 | 1.40725 | 1.34911 |
| bw_scn_aurora_rocks_w.fbx | 0.64471 | 1.40725 | 1.40857 |
| bw_scn_lantern_grove_planter_e.fbx | 1.92600 | 1.57500 | 1.92600 |
| bw_scn_lantern_grove_planter_w.fbx | 1.92600 | 1.57500 | 1.92600 |
| bw_scn_lantern_grove_trunk_e.fbx | 1.20584 | 1.55505 | 1.20584 |
| bw_scn_lantern_grove_trunk_w.fbx | 1.20583 | 1.55510 | 1.20583 |
| bw_scn_sugarloaf_crystals_e.fbx | 2.64202 | 0.79581 | 2.64202 |
| bw_scn_sugarloaf_crystals_w.fbx | 2.64202 | 0.79581 | 2.64202 |
| bw_scn_sugarloaf_lollipop_cactus.fbx | 2.74486 | 1.98500 | 2.74486 |
| bw_scn_sugarloaf_tower_e.fbx | 1.35745 | 1.13408 | 1.37721 |
| bw_scn_sugarloaf_tower_w.fbx | 1.39015 | 1.13402 | 1.40593 |

## Anchors and placement

All scenery origins use manifest pivot_position_arch_local. Collision box centres are FBX pivot-local Roblox axes. MeshParts are decorative and noncolliding; only the 2-6 invisible rock/trunk/tower/stone boxes collide. Lantern origins are the cord hinge, with documented swing axis and motion.

| Grove lantern | Arch-local cord anchor |
|---|---|
| bw_arch_lantern_grove_lantern_01 | [-8.2, 21.3, 2.3] |
| bw_arch_lantern_grove_lantern_02 | [8.2, 21.3, 2.3] |
| bw_arch_lantern_grove_lantern_03 | [-6, 22.3, 2.3] |
| bw_arch_lantern_grove_lantern_04 | [6, 22.3, 2.3] |
| bw_arch_lantern_grove_lantern_05 | [-3.5, 23.3, 2.3] |
| bw_arch_lantern_grove_lantern_06 | [3.5, 23.3, 2.3] |

Snowpuff: figure position [-6.5,0,1.25], export origin [0,0,0]. Original footprint X[-7.308,-5.692], Y[0,3], Z[0.55,2] preserved; west snowy rocks below Y3.6 stay outside |X|7.8, leaving this spot clear.

## Art review and materials

Compared all six Cycles GPU previews against the supplied concepts and iterated canopy depth, layered foliage, trunk/lintel overlap, and snowy shoulder growth. Grove trunks overlap the original legs, flare at the roots and grow across the lintel beneath connected layered autumn foliage; lanterns hang at six new canopy anchors. Canyon striped towers touch the leg silhouettes and bend toward lintel ends with candy clusters and a larger side cactus. Aurora has seven main crown crystals in three sizes, tallest off-centre at approximately Y27; snowy shoulder rocks connect the crown to the original legs. No separately exported bridge pieces were introduced.
Grove canopy and Aurora crown geometry sit above Y18. Aurora crown: 7,316 triangles, two-segment beveled facets and layered snowy ledges, frosted-violet to icy-teal exported vertex-colour gradient. Glow_Tips is a separate material mesh: set Material=Neon, Color=#9FE6F2. Other Neon parts use manifest parts[].color. Opaque BW_Backdrop uses Col vertex colours; BW_Atlas uses shared embedded bw_atlas_1024.png. No extra textures or real asset lights.

## Caveats

The unchanged arch geometry and required clearance translate the reference paintings into stylized toy geometry. Original Aurora arch crystals remain visible beneath the seven new crown crystals because the original FBX is preserved. Runtime portal swirl/particles and SurfaceGui text remain implementation tasks; preview portal shaders are display only. Preview lighting is render-scene lighting, not exported lights. No in-engine Roblox import or playtest was performed under the explicit prohibition. Earlier pass3/pass4 reports are historical snapshots; pass5 clearance and budget values supersede them.

## Rebuild

Run one own Blender directly at a time with -b --factory-startup -P. Do not use run_blender.ps1. Scripts: build_pass5.py; fitcheck.py -- --pass5; reimport_pass5.py; render_pass5.py. Then run compose_pass3.py and finalize_pass5.py with Python. Backup _backup_pass4 includes FBX, manifest, README, previews and all pre-existing Python source.
