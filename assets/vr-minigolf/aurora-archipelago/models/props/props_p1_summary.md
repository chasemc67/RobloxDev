# Aurora Archipelago - P1 props summary

Generated 2026-10-12T07:14:10. Fitcheck: **ALL PASS** (361 PASS, 0 FAIL, 0 FLAG) - `fitcheck_p1props_validated.txt`. FBX re-import: **131/131 passed** (`fbx_validation.json`).

**Pass 2d:** Felt #45B892 -> **#3EA886** (terrain pass 2d) in `aa_h03_ice_plank.fbx`, `aa_h03_dressing.fbx` and `textures/felt.png`, the only Felt users. The blocking movers `aa_h12_paddle_wheel` and `aa_h14_icicle_bell` had their visual meshes rebuilt (`build_all.py --only`) for a **0.0625** visual felt gap over the full motion range (was 0.020 / 0.0215). Their holes.json colliders are unchanged and still sit at 0.020 / 0.0215 (see *Pass 2d: blocking movers' felt gap* below). No other geometry or clearance changed.

**Pass 2e:** no prop FBX changed (129/129 byte-identical to `out_props_bak_2e`, re-imported again). The fitcheck now also covers the blockout's new decoration - `felt_banks.fbx` (FeltBank #308369 = Felt x 0.78, visual 0.3-stud bank along exposed felt edges) and `course_apron_00..02.fbx` (SnowCourse #C9D6E0 surround, 5-7 studs outside every felt+rail footprint), both CanCollide false - against holes.json felt, rails, cups, tee lanes, movers and gap volumes (`_src/fitcheck_decor.py`, exec()'d by `fitcheck.py`; see *Pass 2e: blockout decoration fitcheck* below). The earlier prop checks are unchanged line for line.

**Round 3 'clear' (holes.json clearance fix, playtest-log.md):** H12 paddle-wheel hub y 4.12 -> **4.16** (blockers unchanged relative to the hub); H14 icicle-bell foot = **9 strip colliders** whose outer bottom corners sit on an arc r 10.289 about the hinge. Rebuilt `aa_h12_paddle_wheel.fbx` (tip arc r 4.0575 -> 4.1, follows the strip colliders) and `aa_h14_icicle_bell.fbx` (skid plate = envelope of the 9 strips, curved underside on r 10.289: 0.061 over the felt at the centre, 0.115 at the ends, top 0.461); visual and collider felt gaps are now equal: **0.060 / 0.061** (were visual 0.0625 / collider 0.020-0.0215). **New collision FBX** `aa_h12_paddle_wheel_collision.fbx` (24 boxes) and `aa_h14_icicle_bell_collision.fbx` (10 boxes) = the holes.json blockers exactly, FBX origin = pivot (`manifest.json collision_fbx_files`). The per-hole dressing FBX are unaffected (manifest regen identical outside the two movers; every other FBX byte-identical to `out_props_bak_clear`). holes.json also trimmed H5 upper_rail8/12 and the H17 pier rails by 0.15: every fitcheck rule still passes (the H5 column / H17 span wall flags are gone), so per the brief `aa_h05_rails.fbx` / `aa_h17_rails.fbx` were **not** rebuilt; the fitcheck FLAGs that their on-disk meshes still run 0.15 past the new rail ends (visual only). Previews: `previews/clear/`. Inputs: `_src/inputs_clear/` (Round 3 holes.json, pre-clear holes.json, playtest log, clearance table).

**Pass 2g (blockout felt):** Felt #3EA886 -> **#36997A** (blockout pass 2g: the hero_05 felt-snow gap was still < 20 after the rail caps / H3 apron went #EEF3F7) in `aa_h03_ice_plank.fbx`, `aa_h03_dressing.fbx` and `textures/felt.png` (same seeds, ramp -8,-15,-12), the only Felt users; geometry identical (re-import checked), props .blends recoloured. Backup `out_props_bak_p2g`.

**Rail skins (Round 3 trims):** `aa_h05_rails.fbx` / `aa_h17_rails.fbx` and the dressing that embeds them, `aa_h05_dressing.fbx` / `aa_h17_dressing.fbx`, **rebuilt** from the Round 3 holes.json: H5 upper_rail8/12 skins now end at x +-1.65, H17 pier_s/pier_n rail skins are 8.85 long (skin reaches 0.00 past every trimmed wall end, was 0.15). Tris and bboxes unchanged (2808 / 3104 / 3528 / 4462); only the rail-skin vertices moved; every other prop merged into the two dressing files is geometrically identical; rails == generator; mesh data swapped in both props .blends. This supersedes the 'not rebuilt' note above and clears the two stale rail-skin FLAGs. Fitcheck `fitcheck_railskin_validated.txt` (= `fitcheck_p1props_validated.txt`); remaining FLAGs are the H11/H12 holes.json-geometry wall clearances. Previews: `previews/railskin/`. Backup `out_props_bak_railskin`.

**Round 4 'walls' (playtest-log.md 'Round 4: wall clearance (fitcheck)'):** holes.json moved only walls, not movers. **H11:** rail5/berg18 floe-slot lintel underside **1.17 -> 1.27** (`__cut1` centre y 1.835, height 1.13; side pieces `__cut2`/`__cut3` centre y 0.56, height 1.42). **H12:** icebreaker stern wall line **z -18 -> -18.01** (rail2/hull13 centre z -18.26; rail3/hull18 centre z -21.005, length 5.99; mitred rail1 centre -8.005, length 21.01; hull14 centre -26.005, length 15.99), 0.06 behind the paddles. **Rebuilt:** `aa_h11_rails.fbx`, `aa_h12_rails.fbx` and the dressing that embeds them, `aa_h11_dressing.fbx` / `aa_h12_dressing.fbx` (a full regeneration against the old and new holes.json showed these 4 are the only FBXs that change). Tris and overall bboxes are unchanged (1592 / 3264 / 2139 / 3995). Only rail-skin vertices moved (H11 <= 0.10, H12 <= 0.01). Every other prop merged into the two dressing files is identical, the rails equal the generator, and the meshes were swapped in both .blends. `skins.py` bolt plates use `int(L/2 + 0.01)`, so the 5.99 / 15.99 walls keep 3 / 8 plates (no other wall affected). Unchanged: `aa_h11_ice_floe` (top 1.12, now **0.15** under the lintel), `aa_h12_paddle_wheel`, the `aa_h12_icebreaker` body (its hull boxes end at z -18.2 inside the wall skins, which are the stern faces), the mover collision FBX (= holes.json blockers) and the felt. The fitcheck H11 lintel expectation is now **1.27** (read from holes.json collision_cuts and checked against the `__cut1` bottoms). Fitcheck `fitcheck_walls_validated.txt` (= `fitcheck_p1props_validated.txt`): **361 PASS, 0 FAIL, 0 FLAG**. Both 0.050 flags are gone: H11 ice_floe vs rail5__cut1 **0.150**, H12 paddle_wheel vs rail3/rail2 **0.060**. Decoration was checked against the pass 2g-walls blockout. Previews: `previews/walls/` (H11 slot lintel with the floe at -5.10, H12 stern with the wheel at 0 deg; eye, 3/4, side). Backup `out_props_bak_walls`; pre-walls holes.json `props_in/aurora-archipelago/holes_pre_walls.json`.

111 prop FBX files (65,496 tris, single copies) + 18 per-hole merged dressing FBX files; 127 lights in `manifest.json lights[]`. Every mesh and every FBX < 20,000 tris.

## P1 coverage (props-full section 8 P1 rows -> files)

| Hole | P1 item | Built as |
|---|---|---|
| H1 | cup_flag | `aa_kit_flag` |
| H1 | harbour_lantern | `aa_h01_harbour_lantern` |
| H1 | snow_boulder | `aa_h01_snow_boulder` |
| H1 | bank_arrow | `aa_h01_decals` |
| H2 | cup_flag | `aa_kit_flag` |
| H2 | rookery_drift | `aa_h02_rookery_drift` |
| H2 | lintel_left | `aa_h02_lintel_left` |
| H2 | lintel_mid | `aa_h02_lintel_mid` |
| H2 | lintel_right | `aa_h02_lintel_right` |
| H2 | sign_left | `aa_kit_sign_lantern_L` |
| H2 | sign_right | `aa_kit_sign_lantern_R` |
| H2 | felt_arrow_left | `aa_h02_decals` |
| H2 | felt_arrow_right | `aa_h02_decals` |
| H2 | felt_rollback_mid | `aa_h02_decals` |
| H2 | lantern_cue | `aa_h02_lantern_cue` |
| H3 | cup_flag | `aa_kit_flag` |
| H3 | ice_plank | `aa_h03_ice_plank` |
| H3 | ice_bridge | `aa_kit_ice_bridge_deck` |
| H3 | plank_respawn_stone | `aa_h03_decals` |
| H3 | sign_plank | `aa_kit_sign_plank` |
| H3 | sign_bridge | `aa_kit_sign_lantern_R` |
| H3 | route_arrow_plank | `aa_h03_decals` |
| H3 | route_arrow_bridge | `aa_h03_decals` |
| H4 | cup_flag | `aa_kit_flag` |
| H4 | ice_sheen | `aa_h04_ice_sheen` |
| H4 | ice_warning | `aa_h04_decals` |
| H5 | cup_flag | `aa_kit_flag` |
| H5 | steamwhistle_geyser | `aa_kit_geyser_cone`, `aa_kit_geyser_puff_small` |
| H5 | geyser_platform | `aa_h05_geyser_column`, `aa_h05_geyser_steam` |
| H5 | cliff_face | `aa_h05_cliff_face` |
| H5 | signal_lamp | `aa_h05_signal_lamp` |
| H5 | geyser_arrow | `aa_h05_decals` |
| H6 | cup_flag | `aa_kit_flag` |
| H6 | kettle_pool | `aa_h06_kettle_pool` |
| H6 | pool_respawn_stone | `aa_h06_decals` |
| H6 | slope_ripples | `aa_h06_decals` |
| H7 | cup_flag | `aa_kit_flag` |
| H7 | mogul_trim | `aa_h07_rails` |
| H8 | cup_flag | `aa_kit_flag` |
| H8 | coral_1 | `aa_h08_coral_1` |
| H8 | coral_2 | `aa_h08_coral_2` |
| H8 | coral_3 | `aa_h08_coral_3` |
| H8 | coral_4 | `aa_h08_coral_4` |
| H8 | coral_5 | `aa_h08_coral_5` |
| H8 | coral_6 | `aa_h08_coral_6` |
| H8 | coral_7 | `aa_h08_coral_7` |
| H8 | giant_coral | `aa_h08_giant_coral` |
| H9 | cup_flag | `aa_kit_flag` |
| H9 | conch_entry | `aa_h09_conch` |
| H9 | conch_exit | `aa_h09_conch` |
| H9 | reef_lagoon | `aa_h09_reef_lagoon` |
| H9 | sign_spit | `aa_kit_sign_plank` |
| H9 | sign_route | `aa_kit_sign_lantern_L` |
| H9 | felt_arrow_spit | `aa_h09_decals` |
| H9 | felt_arrow_route | `aa_h09_decals` |
| H10 | cup_flag | `aa_kit_flag` |
| H10 | bobsled_hut | `aa_h10_bobsled_hut` |
| H10 | snow_walls | `aa_h10_snow_walls` |
| H10 | run_lip | `aa_h10_rails` |
| H11 | cup_flag | `aa_kit_flag` |
| H11 | ice_floe | `aa_h11_ice_floe` |
| H11 | fishing_hut | `aa_h11_fishing_hut` |
| H11 | sign_channel | `aa_kit_sign_lantern_R` |
| H11 | felt_arrow_channel | `aa_h11_decals` |
| H12 | cup_flag | `aa_kit_flag` |
| H12 | icebreaker | `aa_h12_icebreaker` |
| H12 | paddle_wheel | `aa_h12_paddle_wheel` |
| H12 | sign_bypass | `aa_kit_sign_lantern_R` |
| H12 | felt_arrow_bypass | `aa_h12_decals` |
| H13 | cup_flag | `aa_kit_flag` |
| H13 | safe_east_wait | `aa_h13_decals` |
| H13 | carousel_canopy | `aa_h13_carousel_canopy` |
| H13 | hub_base | `aa_h13_hub_base` |
| H13 | carousel_arms | `aa_h13_carousel_arms` |
| H14 | cup_flag | `aa_kit_flag` |
| H14 | bell_gantry | `aa_h14_bell_gantry` |
| H14 | icicle_bell | `aa_h14_icicle_bell` |
| H14 | safe_side_sign | `aa_kit_sign_lantern` |
| H14 | timing_arrow | `aa_h14_decals` |
| H15 | cup_flag | `aa_kit_flag` |
| H15 | great_frozen_falls | `aa_world_great_frozen_falls` |
| H15 | lip_ice | `aa_h15_lip_ice` |
| H15 | chevron_1 | `aa_h15_decals` |
| H15 | chevron_2 | `aa_h15_decals` |
| H16 | cup_flag | `aa_kit_flag` |
| H16 | moonwell | `aa_h16_moonwell` |
| H17 | cup_flag | `aa_kit_flag` |
| H17 | aurora_ribbon | `aa_h17_aurora_ribbon` |
| H17 | crystal_piers | `aa_h17_crystal_piers` |
| H17 | ice_bridge | `aa_kit_ice_bridge_deck` |
| H17 | span_respawn_stone | `aa_h17_decals` |
| H17 | span_lamp | `aa_h17_span_lamp` |
| H17 | sign_light | `aa_kit_sign_plank` |
| H17 | sign_bridge | `aa_kit_sign_lantern_R` |
| H17 | route_arrow_light | `aa_h17_decals` |
| H17 | route_arrow_bridge | `aa_h17_decals` |
| H18 | cup_flag | `aa_kit_flag` |
| H18 | halo_arch | `aa_h18_halo_arch` |
| H18 | crystal_bank_ne_deco | `aa_h18_crystal_bank_ne_deco` |
| H18 | crystal_bank_sw_deco | `aa_h18_crystal_bank_sw_deco` |
| H18 | felt_arrow_bank | `aa_h18_decals` |
| H18 | crystal_chute | `aa_h18_crystal_chute` |
| H18 | ramp_chevrons | `aa_h18_decals` |

Also P1 from props.md / props-full sections 4-7, 9, 11: rail kit (`aa_kit_rail_*`) + every holes.json wall box skinned per hole (`aa_hNN_rails`, tall-wall variants: snow drift H2/H10, snowbank/berg H11, coral H9, hull H12, moonstone H16, frosted ice H17 piers, crystal H18), bumper plinths (H1 boulder, H8 corals 1-7, H13 hub), floating-deck skirts (H3/H17 decks + piers, H9 spit), brass lantern posts (89 world instances + 9-stud hole post), 12 signs, respawn stones (H3/H6/H17), teleport visuals (H5 platform, H9 conch ring + conch x2), Starfrost Spire + orbiting shards, lift cage, gondola cabin/stations, bridge/stair modules, teleport and tee-arrival pads.

## Prop list (triangles)

| Prop | Class | Holes | Tris | Mesh parts | Size [x,y,z] | Motion |
|---|---|---|---:|---:|---|---|
| `aa_kit_flag` | flag | 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18 | 104 | 2 | [2.199, 7.98, 0.247] |  |
| `aa_kit_rail_straight_1` | kit | world/kit | 80 | 3 | [0.512, 1.5, 1.0] |  |
| `aa_kit_rail_straight_2` | kit | world/kit | 80 | 3 | [0.512, 1.5, 2.0] |  |
| `aa_kit_rail_straight_4` | kit | world/kit | 104 | 3 | [0.512, 1.5, 4.0] |  |
| `aa_kit_rail_straight_8` | kit | world/kit | 152 | 3 | [0.512, 1.5, 8.0] |  |
| `aa_kit_rail_slope_4` | kit | world/kit | 104 | 3 | [0.512, 2.088, 4.0] |  |
| `aa_kit_rail_corner` | kit | world/kit | 204 | 3 | [2.03, 1.58, 2.03] |  |
| `aa_kit_rail_45` | kit | world/kit | 188 | 3 | [1.537, 1.58, 2.737] |  |
| `aa_kit_rail_endcap` | kit | world/kit | 68 | 3 | [0.512, 1.5, 0.512] |  |
| `aa_kit_lantern_post` | kit | world/kit | 270 | 4 | [1.0, 6.944, 1.0] |  |
| `aa_kit_lantern_post9` | kit | world/kit | 270 | 4 | [1.1, 9.02, 1.1] |  |
| `aa_kit_sign_plank` | kit | 3,9,17 | 189 | 4 | [1.6, 2.62, 0.2] |  |
| `aa_kit_sign_plank_L` | kit | world/kit | 189 | 4 | [1.74, 2.62, 0.2] |  |
| `aa_kit_sign_plank_R` | kit | world/kit | 189 | 4 | [1.74, 2.62, 0.2] |  |
| `aa_kit_sign_lantern_L` | kit | 2,9 | 359 | 6 | [2.039, 3.088, 0.42] |  |
| `aa_kit_sign_lantern_R` | kit | 2,3,11,12,17 | 359 | 6 | [2.039, 3.088, 0.42] |  |
| `aa_kit_sign_lantern` | kit | 14 | 359 | 6 | [1.8, 3.088, 0.42] |  |
| `aa_kit_geyser_cone` | kit | 5 | 468 | 5 | [6.0, 7.0, 5.832] |  |
| `aa_kit_geyser_puff_small` | mover_aux | 5 | 80 | 1 | [2.467, 5.489, 2.106] |  |
| `aa_world_geyser_puff60` | world | world/kit | 300 | 1 | [13.814, 63.63, 13.29] |  |
| `aa_kit_teleport_pad` | world | world/kit | 284 | 3 | [4.0, 0.24, 4.0] |  |
| `aa_kit_tee_arrival_pad` | world | world/kit | 284 | 2 | [4.0, 0.2, 4.0] |  |
| `aa_kit_lift_cage` | world | world/kit | 952 | 4 | [10.4, 10.666, 10.4] |  |
| `aa_kit_gondola_cabin` | world | world/kit | 428 | 5 | [6.081, 8.2, 6.081] |  |
| `aa_kit_gondola_station` | world | world/kit | 856 | 4 | [13.152, 12.55, 13.152] |  |
| `aa_kit_bridge_ice_4` | world | world/kit | 248 | 4 | [6.5, 4.28, 4.0] |  |
| `aa_kit_bridge_aurora_4` | world | world/kit | 248 | 4 | [6.5, 4.28, 4.0] |  |
| `aa_kit_stair_flight_10` | world | world/kit | 432 | 2 | [6.46, 11.653, 15.45] |  |
| `aa_kit_stair_flight_5` | world | world/kit | 240 | 2 | [6.46, 7.653, 7.871] |  |
| `aa_world_starfrost_spire` | world | world/kit | 404 | 5 | [60.228, 240.0, 59.128] |  |
| `aa_world_spire_shards` | world | world/kit | 200 | 2 | [155.213, 134.989, 136.068] |  |
| `aa_world_great_frozen_falls` | world | 15 | 1,766 | 3 | [28.198, 146.679, 8.954] |  |
| `aa_h05_geyser_column` | mover | 5 | 228 | 7 | [3.086, 4.005, 3.0] | slide 2.0 studs/s |
| `aa_h05_geyser_steam` | mover_aux | 5 | 28 | 1 | [2.4, 1.0, 2.4] |  |
| `aa_h11_ice_floe` | mover | 11 | 192 | 7 | [7.0, 1.12, 0.636] | slide 3.0 studs/s |
| `aa_h12_paddle_wheel` | mover | 12 | 800 | 4 | [8.2, 8.2, 1.27] | rotate 30.0 deg/s |
| `aa_h13_carousel_arms` | mover | 13 | 2,224 | 9 | [23.0, 3.19, 23.0] | rotate 15.0 deg/s |
| `aa_h14_icicle_bell` | mover | 14 | 682 | 4 | [2.96, 10.539, 2.96] | swing 14.1372 deg/s (peak, at the bottom of the swing) |
| `aa_h17_aurora_span` | mover | 17 | 36 | 2 | [3.0, 0.4, 8.0] | toggle 0.0 - |
| `aa_h01_decals` | decal | 1 | 56 | 1 | [1.273, 0.01, 2.132] |  |
| `aa_h02_decals` | decal | 2 | 84 | 2 | [19.9, 0.355, 9.9] |  |
| `aa_h03_decals` | decal | 3 | 100 | 2 | [7.4, 0.01, 3.9] |  |
| `aa_h04_decals` | decal | 4 | 102 | 1 | [3.04, 0.01, 1.0] |  |
| `aa_h05_decals` | decal | 5 | 20 | 1 | [1.4, 0.01, 2.0] |  |
| `aa_h06_decals` | decal | 6 | 192 | 2 | [14.8, 0.224, 2.2] |  |
| `aa_h09_decals` | decal | 9 | 200 | 2 | [14.9, 0.01, 14.45] |  |
| `aa_h11_decals` | decal | 11 | 20 | 1 | [1.4, 0.01, 2.0] |  |
| `aa_h12_decals` | decal | 12 | 20 | 1 | [1.4, 0.01, 2.0] |  |
| `aa_h13_decals` | decal | 13 | 184 | 1 | [1.32, 0.01, 1.32] |  |
| `aa_h14_decals` | decal | 14 | 32 | 1 | [1.4, 0.01, 1.8] |  |
| `aa_h15_decals` | decal | 15 | 44 | 1 | [2.4, 0.01, 5.2] |  |
| `aa_h17_decals` | decal | 17 | 100 | 2 | [7.4, 0.01, 3.9] |  |
| `aa_h18_decals` | decal | 18 | 100 | 1 | [16.71, 0.482, 25.2] |  |
| `aa_h01_rails` | skin | 1 | 1,584 | 3 | [13.012, 1.5, 41.012] |  |
| `aa_h02_rails` | skin | 2 | 1,344 | 2 | [25.0, 2.9, 54.0] |  |
| `aa_h03_rails` | skin | 3 | 2,976 | 3 | [17.012, 1.5, 72.512] |  |
| `aa_h04_rails` | skin | 4 | 2,324 | 3 | [16.512, 2.1, 60.512] |  |
| `aa_h05_rails` | skin | 5 | 2,808 | 3 | [26.012, 5.5, 58.512] |  |
| `aa_h06_rails` | skin | 6 | 2,632 | 3 | [30.012, 1.918, 62.512] |  |
| `aa_h07_rails` | skin | 7 | 3,744 | 3 | [21.012, 2.7, 58.512] |  |
| `aa_h08_rails` | skin | 8 | 2,392 | 3 | [26.012, 1.5, 56.512] |  |
| `aa_h09_rails` | skin | 9 | 1,040 | 3 | [31.22, 2.9, 73.52] |  |
| `aa_h10_rails` | skin | 10 | 1,168 | 5 | [18.0, 1.8, 53.0] |  |
| `aa_h11_rails` | skin | 11 | 1,592 | 3 | [23.0, 3.2, 53.0] |  |
| `aa_h12_rails` | skin | 12 | 3,264 | 4 | [21.012, 1.5, 51.012] |  |
| `aa_h13_rails` | skin | 13 | 2,296 | 3 | [27.012, 1.5, 52.012] |  |
| `aa_h14_rails` | skin | 14 | 2,144 | 3 | [17.012, 2.3, 51.012] |  |
| `aa_h15_rails` | skin | 15 | 2,048 | 3 | [20.012, 5.5, 42.512] |  |
| `aa_h16_rails` | skin | 16 | 800 | 2 | [20.012, 2.3, 42.512] |  |
| `aa_h17_rails` | skin | 17 | 3,104 | 5 | [17.012, 1.5, 66.512] |  |
| `aa_h18_rails` | skin | 18 | 576 | 2 | [36.012, 3.7, 63.012] |  |
| `aa_h01_harbour_lantern` | anchored | 1 | 474 | 4 | [2.65, 9.0, 1.25] |  |
| `aa_h01_snow_boulder` | anchored | 1 | 64 | 3 | [4.243, 5.064, 4.243] |  |
| `aa_h02_rookery_drift` | anchored | 2 | 456 | 2 | [14.0, 4.6, 17.0] |  |
| `aa_h02_lintel_left` | anchored | 2 | 168 | 4 | [5.0, 7.025, 1.44] |  |
| `aa_h02_lintel_mid` | anchored | 2 | 168 | 4 | [5.0, 7.025, 1.44] |  |
| `aa_h02_lintel_right` | anchored | 2 | 168 | 4 | [5.0, 7.025, 1.44] |  |
| `aa_h02_lantern_cue` | anchored | 2 | 304 | 4 | [6.119, 10.85, 0.738] |  |
| `aa_h03_ice_plank` | anchored | 3 | 120 | 3 | [2.412, 2.2, 26.0] |  |
| `aa_kit_ice_bridge_deck` | anchored | 3,17 | 80 | 2 | [5.0, 2.38, 26.0] |  |
| `aa_h17_crystal_piers` | anchored | 17 | 128 | 2 | [4.0, 3.68, 26.0] |  |
| `aa_h17_aurora_ribbon` | anchored | 17 | 384 | 2 | [2.599, 60.0, 8.0] |  |
| `aa_h17_span_lamp` | anchored | 17 | 118 | 2 | [0.552, 2.395, 0.552] |  |
| `aa_h04_ice_sheen` | decal | 4 | 236 | 2 | [8.0, 0.608, 32.0] |  |
| `aa_h05_cliff_face` | anchored | 5 | 120 | 3 | [16.0, 7.99, 4.55] |  |
| `aa_h05_signal_lamp` | anchored | 5 | 112 | 3 | [0.62, 1.62, 0.42] |  |
| `aa_h06_kettle_pool` | anchored | 6 | 172 | 2 | [6.5, 1.3, 22.0] |  |
| `aa_h08_coral_1` | anchored | 8 | 300 | 3 | [2.546, 4.3, 2.546] |  |
| `aa_h08_coral_2` | anchored | 8 | 300 | 3 | [2.54, 4.3, 2.196] |  |
| `aa_h08_coral_3` | anchored | 8 | 300 | 3 | [2.54, 4.3, 2.196] |  |
| `aa_h08_coral_4` | anchored | 8 | 300 | 3 | [2.546, 4.3, 2.546] |  |
| `aa_h08_coral_5` | anchored | 8 | 300 | 3 | [1.966, 4.3, 2.405] |  |
| `aa_h08_coral_6` | anchored | 8 | 300 | 3 | [2.232, 4.3, 1.866] |  |
| `aa_h08_coral_7` | anchored | 8 | 300 | 3 | [2.263, 4.3, 2.263] |  |
| `aa_h08_giant_coral` | anchored | 8 | 664 | 4 | [5.642, 14.009, 5.485] |  |
| `aa_h09_conch` | anchored | 9 | 990 | 3 | [4.133, 4.53, 4.716] |  |
| `aa_h09_reef_lagoon` | anchored | 9 | 456 | 4 | [25.0, 2.115, 34.0] |  |
| `aa_h10_snow_walls` | anchored | 10 | 296 | 2 | [15.0, 2.85, 40.0] |  |
| `aa_h10_bobsled_hut` | anchored | 10 | 236 | 4 | [3.889, 6.8, 4.065] |  |
| `aa_h11_fishing_hut` | anchored | 11 | 168 | 5 | [2.5, 6.005, 2.5] |  |
| `aa_h12_icebreaker` | anchored | 12 | 352 | 6 | [13.9, 4.65, 5.8] |  |
| `aa_h13_hub_base` | anchored | 13 | 854 | 4 | [15.0, 1.712, 15.0] |  |
| `aa_h13_carousel_canopy` | anchored | 13 | 312 | 6 | [16.0, 11.17, 16.0] |  |
| `aa_h14_bell_gantry` | anchored | 14 | 340 | 4 | [10.8, 11.55, 1.0] |  |
| `aa_h15_lip_ice` | anchored | 15 | 84 | 2 | [7.0, 3.98, 0.413] |  |
| `aa_h15_lip_parapet` | anchored | 15 | 12 | 1 | [8.0, 3.5, 0.3] |  |
| `aa_h16_moonwell` | anchored | 16 | 544 | 4 | [22.627, 3.683, 18.09] |  |
| `aa_h18_halo_arch` | anchored | 18 | 604 | 3 | [50.2, 34.0, 4.2] |  |
| `aa_h18_crystal_bank_ne_deco` | anchored | 18 | 154 | 2 | [8.197, 2.6, 8.176] |  |
| `aa_h18_crystal_bank_sw_deco` | anchored | 18 | 224 | 2 | [12.086, 2.6, 12.065] |  |
| `aa_h18_crystal_chute` | anchored | 18 | 96 | 1 | [3.76, 0.008, 8.0] |  |

## Per-hole near field (Quest; <= 60 studs of the hole's felt)

Own dressing = merged `aa_hNN_dressing.fbx`; loose = flag, movers, puffs; neighbours = other holes' P1 instances within 60 studs; world = lantern posts, pads, bridges, stairs, lifts, gondola, world geyser within 60 (spire / shards / Great Frozen Falls are streamed landmarks, exempt).

| Hole | Own dressing | Own loose | Neighbours | World pieces | **Near-field total** | Budget |
|---|---:|---:|---:|---:|---:|---|
| H1 | 2,178 | 104 | 3,106 | 1,932 | **7,320** |  <= 40k |
| H2 | 3,410 | 104 | 4,466 | 1,648 | **9,628** |  <= 40k |
| H3 | 3,824 | 104 | 1,727 | 3,370 | **9,025** |  <= 40k |
| H4 | 2,662 | 104 | 3,864 | 4,146 | **10,776** |  <= 40k |
| H5 | 3,528 | 440 | 5,866 | 3,452 | **13,286** | lean (H5-8 target) <= 40k |
| H6 | 2,996 | 104 | 1,140 | 4,418 | **8,658** | lean (H5-8 target) <= 40k |
| H7 | 3,744 | 104 | 4,960 | 2,472 | **11,280** | lean (H5-8 target) <= 40k |
| H8 | 5,156 | 104 | 104 | 4,902 | **10,266** | lean (H5-8 target) <= 40k |
| H9 | 4,224 | 104 | 0 | 5,088 | **9,416** |  <= 40k |
| H10 | 1,700 | 104 | 1,971 | 2,884 | **6,659** |  <= 40k |
| H11 | 2,139 | 296 | 3,388 | 1,648 | **7,471** |  <= 40k |
| H12 | 3,995 | 904 | 0 | 2,046 | **6,945** |  <= 40k |
| H13 | 3,646 | 2,328 | 3,557 | 2,450 | **11,981** |  <= 40k |
| H14 | 2,875 | 786 | 5,682 | 1,648 | **10,991** |  <= 40k |
| H15 | 2,188 | 104 | 1,126 | 3,096 | **6,514** |  <= 40k |
| H16 | 1,344 | 104 | 1,398 | 3,268 | **6,114** |  <= 40k |
| H17 | 4,462 | 140 | 1,448 | 4,078 | **10,128** |  <= 40k |
| H18 | 1,754 | 104 | 4,139 | 4,138 | **10,135** |  <= 40k |

## Movers (fitcheck sweep)

| Mover | Steps | Min felt clearance | Min wall clearance | Min static-prop clearance |
|---|---:|---|---|---|
| `aa_h05_geyser_column` | 81 | n/a  | 0.15 (upper_rail8 at 3.5 studs) | 0.1652 |
| `aa_h11_ice_floe` | 141 | 0.0 at -6.45 studs | 0.15 (rail5__cut1 at -5.1 studs) | - |
| `aa_h12_paddle_wheel` | 360 | 0.06 at 17.0 deg | 0.06 (rail3 at 0.0 deg) | 0.25 |
| `aa_h13_carousel_arms` | 360 | 0.0 at 0.0 deg | 0.4 (hub_plinth_47 at 74.0 deg) | 0.2359 |
| `aa_h14_icicle_bell` | 73 | 0.061 at -3.25 deg | 1.1385 (rail1 at -9.0 deg) | 0.3452 |
| `aa_h17_aurora_span` | 1 | n/a  | 0.15 (pier_s_rail6 at 0.0 studs) | 0.0042 |

Flags for the build bot (holes.json geometry, not mesh errors):


### Blocking movers' felt gap (Round 3 'clear': visual mesh == holes.json collider)

The H12 paddle wheel and H14 icicle bell are blocking movers: they must stay under a 0.16 ball but off the felt. Pass 2d moved only the VISUAL meshes to a 0.0625 gap while the holes.json colliders stayed at 0.020 / 0.0215. Round 3 'clear' moved the COLLIDERS to >= 0.06 (H12 hub +0.04, H14 9-strip foot), so the visual meshes follow the colliders again. Fine-step sweeps over the full motion range test the exact mesh vertices and the blocker box corners (and the collision FBX corners) against the holes.json felt tops.

| Mover | Visual mesh (Round 3) | Sweep | Visual min felt gap (2d -> clear) | Collider min felt gap (2d -> clear) | Collision FBX |
|---|---|---|---|---|---|
| `aa_h12_paddle_wheel` | red paddle-tip arc r 4.0575 -> 4.1 = the strip-corner radius (rim, spokes, boards unchanged); pivot hub y 4.16 | 7200 steps of 0.05 deg | 0.0625 -> **0.06** at +11.25 deg (within 0.0005 at 1844 of 7200 steps, e.g. 0.00, 78.10, 101.85, 179.95, 258.05, 281.80 deg; exact min whenever a tip-arc vertex points straight down) | 0.020 -> **0.06** at +5.6 deg | `fbx/aa_h12_paddle_wheel_collision.fbx`: 24 boxes, 288 tris, swept min 0.06 |
| `aa_h14_icicle_bell` | skid plate = envelope of the 9 strip colliders: flat top 0.461 at rest, underside on r 10.289 about the hinge (0.061 centre, 0.115 ends; vertices at every strip edge, never above a strip bottom); body/hanger/icicles unchanged | 1801 steps of 0.01 deg | 0.0625 -> **0.061** at +1.3 deg (within 0.0005 at -6.42..-0.00 and +0.01..+6.42 deg) | 0.0215 -> **0.061** at -0.65 deg | `fbx/aa_h14_icicle_bell_collision.fbx`: 10 boxes, 120 tris, swept min 0.061 |

### Pass 2e: blockout decoration fitcheck (felt banks + SnowCourse apron vs holes.json)

Blockout `out_p2g\models\blockout` (manifest pass 2g-walls); points tested: banks 1,383,436, apron 446,837 (triangle samples at 0.1 / 0.5 studs + every vertex). Banks: never inside a felt rectangle, never above the felt top they border, under a rail only inside the rail box, >= r+0.5 from cups, none in the tee-lane felt, clear of every mover's swept blocker volume. Apron: over felt only hidden inside the slab (<= top - 0.1), within 8.5 studs of the footprint, hugs the terrain (+0.05), clear of cups/tee lanes/movers.

| Hole | Bank pts (under rails / outside) | Max over bordered felt top | Min cup dist | Apron pts (over felt, hidden) | Apron band max dist |
|---|---|---:|---:|---|---:|
| H1 | 54,132 (692 / 53,440) | -0.02 | 2.98 | 16,765 (212) | 7.83 |
| H2 | 152,516 (2,174 / 150,342) | -0.02 | 1.49 | 27,314 (428) | 7.91 |
| H3 | 54,698 (934 / 53,764) | -0.02 | 6.36 | 26,437 (922) | 7.91 |
| H4 | 23,508 (303 / 23,205) | -0.02 | 46.26 | 22,757 (82) | 8.08 |
| H5 | 72,640 (940 / 71,700) | -0.02 | 8.99 | 22,499 (551) | 7.91 |
| H6 | 60,076 (798 / 59,278) | -0.02 | 5.99 | 30,507 (581) | 8.14 |
| H7 | 75,296 (1,368 / 73,928) | -0.02 | 2.99 | 23,484 (141) | 7.5 |
| H8 | 78,360 (1,051 / 77,309) | -0.02 | 5.49 | 24,217 (338) | 7.91 |
| H9 | 139,668 (1,602 / 138,066) | -0.02 | 6.49 | 37,810 (523) | 7.91 |
| H10 | 85,290 (1,075 / 84,215) | -0.02 | 6.73 | 22,371 (372) | 7.91 |
| H11 | 138,734 (6,328 / 132,406) | -0.02 | 5.49 | 27,161 (198) | 7.91 |
| H12 | 138,468 (2,540 / 135,928) | -0.02 | 6.49 | 25,550 (452) | 7.91 |
| H13 | 62,688 (752 / 61,936) | -0.02 | 3.38 | 24,866 (294) | 8.08 |
| H14 | 36,478 (650 / 35,828) | -0.02 | 13.36 | 20,556 (284) | 7.52 |
| H15 | 36,464 (742 / 35,722) | -0.02 | 7.62 | 19,141 (342) | 7.83 |
| H16 | 45,458 (775 / 44,683) | -0.02 | 8.73 | 18,388 (84) | 7.83 |
| H17 | 61,864 (973 / 60,891) | -0.02 | 6.29 | 25,662 (340) | 8.14 |
| H18 | 67,098 (1,147 / 65,951) | -0.02 | 16.21 | 31,352 (567) | 7.91 |

## Conflicts resolved

1. **Halo Arch position** - holes.json H18 anchor [0,0.8,-52] -> world [-235,222.8,-284], depth 4; world.json backdrop `halo_arch` [-235,222,-292], depth 8. **Used holes.json** (one arch, `aa_h18_halo_arch`, legs x +-23, opening >= 18 over the felt). world.json record treated as a stale locator.
2. **Steamwhistle Geyser** - ONE cone mesh (`aa_kit_geyser_cone`, 6 x 7 x 6) used twice: the H5 instance with the small puff (`aa_kit_geyser_puff_small`) and the world.json cone [262,84,380] at scale [2.333,1.429,2.333] (= 14 x 10 x 14) with the 60-stud steam column (`aa_world_geyser_puff60`). Puffs are separate meshes so their scale differs.
3. **H5 geyser anchor lies on the felt** - holes.json anchor [-10.5,4,-33] (6 wide) sits inside the upper green felt (x -12.5..12.5) although its own note says 'outside the upper green's west rail'. A collider-less 7-stud cone on the green would fail the felt-clash rule, so the H5 instance is placed at **[-19,4,-33]** (outside upper_rail9, >= 3 studs clear). Designer to confirm.
4. **Mover specs** - course.md 'starting spec' table superseded by holes.json (H5 dwell 8 s / 1.5 s, H11 3 studs/s, H12 30 deg/s, H13 15 deg/s, H14 9 deg / 4 s, H17 solid 6 s of 9 s). All movers use holes.json pivots/axes exactly (fitcheck verifies).
5. **H5 hexagonal platform vs square collider** - square 3 x 3 contact faces; hex look in the top texture + brass hex vent ring (props-full section 4).
6. **H11 floe** - thickness 0.636 (blocker) not 0.6 (anchor); props.md allows snow/snowpuff to 1.2 but the rail5/berg18 slot lintel (collision_cuts) was at y 1.17, so floe decoration stops at **1.12**; Round 4 'walls' raised the lintel to **1.27**, so the unchanged floe now clears it by 0.15.
7. **H12 paddle tips** - modelled as an arc (props-full: 'model the arc'). Pass 2d pulled it in to r 4.0575 (visual gap 0.0625, colliders 0.020); Round 3 'clear' raised the hub to y 4.16, so the arc is back at the strip-corner radius **r 4.1** and visual and collider both clear the felt by **0.060**. Between strip centres the arc exceeds the stepped strip blockers by up to 0.10 studs (it never falls inside them).
8. **H13 hub** - 48-sided cylinder r 7.5 as specified; the 48 circumscribed box strips step outward by up to ~0.3 at the chord ends, so a ball can touch an invisible corner just outside the visual base.
9. **Great Frozen Falls** - geometry from world.json waterfalls (top [20,182,-398] -> bottom y 36, width 26); the H15 anchor [13.5,-4,-30] is a view cue (props-full section 13).
10. **Red/cream reserved for movers** - the brief allows red/cream bands only on moving parts, but props-full describes a 'striped red-and-cream' bobsled hut, a red-hull/cream-deckhouse icebreaker and a striped fishing hut. Static props were recoloured: violet (`Canvas` #7A5CC8) & snow stripes, deep-teal hull (`HullTeal` #2F5D7A), brass funnel.
11. **Palette vs pass 2b** - course.md timber #8A5A33 / felt #4FA83D; the terrain pass 2b changed timber to #8A5A3C and felt to #4FC29E; pass 2c retuned felt to #45B892 and pass 2d to #3EA886. Props use **#8A5A3C** timber and **#3EA886** felt strips (aa_h03_ice_plank, aa_h03_dressing; textures/felt.png) so they match the terrain FBXs.
12. **Priority of walkway pieces** - props.md lists lifts, bridges and teleport pads under P2, props-full section 11 marks them P1. Built as P1 kits with world instances (lift cage, gondola cabin + stations, ice/aurora bridge modules, stair flights, teleport + tee-arrival pads).
13. **Sign anchors hug the rails** - several sign anchors sit 0.1 stud outside a rail (e.g. H2 sign_left x -12.6 vs rail3 face -12.5). Posts slimmed to 0.18 and the board swung to the side away from rails/felt (`aa_kit_sign_*_L/_R` variants, chosen per anchor by the generator).
14. **H2 lantern cue** - the 'rope between two frosted pines' needs the P2 pines; P1 uses a timber crane post 3.5 studs outside the west green rail with the arm at y 10.6 and the lantern at y 9.
15. **Small fit adjustments** - H11 fishing hut 0.25 south (still inside its occluder) to clear pocket_w21; H1 ship's lantern hangs west of its post (>= 3 studs from rail1); H5 shaft lining 3.7 wide (spec 3.2) and cliff face 0.2 behind the step so the rising platform + gauge keep >= 0.15 clearance; H15 parapet split into its own prop (PlayerGuard envelope).
16. **H3 plank top = felt top (y 0)** - the plank mesh carries the felt look (2-wide Felt strip); the builder should make the 2 x 0.4 felt slab collider invisible there to avoid z-fighting.

## Caveats

- Decoration only: CanCollide/CanQuery/CanTouch false on every MeshPart; gameplay collision stays the invisible holes.json parts (Round 3: the two blocking movers also ship their colliders as `*_collision.fbx`, identical to holes.json).
- Designer-anchored props (signs, lamps, huts, gantry, conch, lip ice ...) keep their exact holes.json anchor positions; where their envelope already overlaps the rail strip or felt the fitcheck reports it as an envelope note instead of a failure (see `fitcheck_report.json > anchored_envelope_overhang`). Geometry outside an anchor envelope obeys all clash/strip/lane rules.
- Decals are thin meshes (0.01) conformed to the felt; they could equally be SurfaceGui/Decal textures. Sign wording goes on SurfaceGuis on the cream boards (front = +Z).
- Glow (Neon) parts carry Blender emission for previews; in Roblox use Material Neon + PointLights from `lights[]`. Glass ice: Transparency 0.3, Reflectance 0.1 (`IceSheen` 0.15/0.15).
- Animated/scripted parts are separate meshes: flag banner (child `aa_kit_flag__FlagRed`, turns about the pole axis), geyser steam column (Size.Y = offset), puffs, signal-lamp lens (`SignalGreen`), span lamp lens (`AuroraMint`), spire shards.
- World instances of walkway kits use world.json positions (lift cages at the bottom stop; bridges in 4-stud modules with the last one scaled). Teleport kiosk signs and P2/P3 dressing (snowpuffs, pines, palms, coral fans, music lanterns) are not part of this pass.
- `aa_world_starfrost_spire` replaces the terrain blockout spire (hide `spire__*` from the blockout FBX set when both are imported).
- Preview renders are Cycles 16 spp (props) / 32 spp (tee views); tee views use the pass-2b scene with the blockout's placeholder rails/flags hidden.
