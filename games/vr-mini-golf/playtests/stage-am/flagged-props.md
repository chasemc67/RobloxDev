# Stage am flagged props

Gap is the signed XZ separating-axis gap in studs used by the checker: negative means bounds overlap, zero means touching. Wall/prop clearance target is 0.15 studs; felt checks use its -0.4 to +8 stud vertical headroom region. These are bounds findings, not triangle-confirmed intersections.

## Source checker — real findings

296 raw findings; **12 real findings on 3 unique props**. Every real finding is listed below; non-prop dressing, flat, envelope and accepted-exception findings are retained in deco_clearance.json.

| Hole | Flagged prop | Class | Gap (studs) | Too close to |
|---|---|---|---:|---|
| 2 | rookery_drift | prop | -0.50000 | wall: drift15 |
| 2 | rookery_drift | prop | -0.50000 | wall: drift16 |
| 2 | rookery_drift | prop | -0.50000 | wall: drift17 |
| 2 | rookery_drift | prop | -0.50000 | wall: drift24 |
| 2 | rookery_drift | prop | -5.00000 | prop: snowpuffs |
| 2 | rookery_drift | prop | -0.50000 | wall: drift19 |
| 2 | rookery_drift | prop | -0.50000 | wall: drift20 |
| 2 | snowpuffs | prop | -5.00000 | wall: drift16 |
| 2 | snowpuffs | prop | -5.00000 | wall: drift18 |
| 2 | snowpuffs | prop | -0.50000 | wall: drift20 |
| 2 | snowpuffs | prop | -7.00000 | felt: mid_burrow |
| 2 | lintel_mid | prop | -0.60000 | felt: mid_burrow |

## Built-place audit — prop class

Actual Studio per-MeshPart oriented bounds projected to hole XZ plus Y intervals; built wall and supporting-piece bounds. Conservative for meshes with holes/disconnected pieces. Coplanar bounds are z-fight candidates, not triangle-confirmed z-fighting.

**56 prop-class findings on 15 unique props** (56 findings pass the source checker real-finding rule). Every prop-class finding is listed, including hits against loose envelopes/decals excluded by that rule. Unique props use (hole, authored anchor), so imported and retained anchor representations do not inflate the count.

| Hole | Built prop | Class | Gap (studs) | Too close to | Real | Meshes |
|---|---|---|---:|---|---|---|
| 2 | h02_rookery_drift | prop | 0.11000 | wall: drift15 | yes | h02_rookery_drift__Snow, h02_rookery_drift__SnowShadow |
| 2 | h02_rookery_drift | prop | -5.39002 | wall: drift16 | yes | h02_rookery_drift__Snow, h02_rookery_drift__SnowShadow |
| 2 | h02_rookery_drift | prop | -3.89000 | wall: drift17 | yes | h02_rookery_drift__Snow, h02_rookery_drift__SnowShadow |
| 2 | h02_rookery_drift | prop | -4.39001 | wall: drift18 | yes | h02_rookery_drift__Snow, h02_rookery_drift__SnowShadow |
| 2 | h02_rookery_drift | prop | 0.11000 | wall: drift19 | yes | h02_rookery_drift__Snow, h02_rookery_drift__SnowShadow |
| 2 | h02_rookery_drift | prop | 0.10999 | wall: drift20 | yes | h02_rookery_drift__Snow, h02_rookery_drift__SnowShadow |
| 2 | h02_rookery_drift | prop | 0.10998 | wall: drift24 | yes | h02_rookery_drift__Snow, h02_rookery_drift__SnowShadow |
| 2 | h02_rookery_drift | prop | -8.39001 | felt: mid_burrow | yes | h02_rookery_drift__Snow, h02_rookery_drift__SnowShadow |
| 2 | h02_rookery_drift | prop | -0.36550 | prop: h02_lintel_left | yes | h02_rookery_drift__Snow, h02_rookery_drift__SnowShadow |
| 2 | h02_rookery_drift | prop | -0.36449 | prop: h02_lintel_mid | yes | h02_rookery_drift__Snow, h02_rookery_drift__SnowShadow |
| 2 | h02_rookery_drift | prop | -0.36550 | prop: h02_lintel_right | yes | h02_rookery_drift__Snow, h02_rookery_drift__SnowShadow |
| 2 | h02_lintel_left | prop | -0.62750 | wall: rail3 | yes | h02_lintel_left__Basalt |
| 2 | h02_lintel_left | prop | -0.62750 | wall: rail4 | yes | h02_lintel_left__Basalt |
| 2 | h02_lintel_left | prop | -0.97550 | wall: rail5 | yes | h02_lintel_left__Basalt |
| 2 | h02_lintel_left | prop | -0.62749 | wall: drift15 | yes | h02_lintel_left__Basalt |
| 2 | h02_lintel_left | prop | -0.97550 | wall: drift24 | yes | h02_lintel_left__Basalt |
| 2 | h02_lintel_left | prop | -0.12750 | felt: plaza | yes | h02_lintel_left__Basalt |
| 2 | h02_lintel_left | prop | -0.97550 | felt: left_burrow | yes | h02_lintel_left__Basalt |
| 2 | h02_lintel_left | prop | -0.36550 | prop: h02_rookery_drift | yes | h02_lintel_left__Basalt |
| 2 | h02_lintel_mid | prop | -0.57250 | wall: drift15 | yes | h02_lintel_mid__Basalt |
| 2 | h02_lintel_mid | prop | -0.97449 | wall: drift16 | yes | h02_lintel_mid__Basalt |
| 2 | h02_lintel_mid | prop | -0.97449 | wall: drift18 | yes | h02_lintel_mid__Basalt |
| 2 | h02_lintel_mid | prop | -0.57250 | wall: drift19 | yes | h02_lintel_mid__Basalt |
| 2 | h02_lintel_mid | prop | -0.07250 | felt: plaza | yes | h02_lintel_mid__Basalt |
| 2 | h02_lintel_mid | prop | -0.97449 | felt: mid_burrow | yes | h02_lintel_mid__Basalt, h02_lintel_mid__Ice, h02_lintel_mid__IceCore |
| 2 | h02_lintel_mid | prop | -0.36449 | prop: h02_rookery_drift | yes | h02_lintel_mid__Basalt |
| 2 | h02_lintel_right | prop | -0.97550 | wall: rail9 | yes | h02_lintel_right__Basalt |
| 2 | h02_lintel_right | prop | -0.59350 | wall: rail10 | yes | h02_lintel_right__Basalt |
| 2 | h02_lintel_right | prop | -0.10001 | wall: rail11 | yes | h02_lintel_right__Basalt |
| 2 | h02_lintel_right | prop | -0.59350 | wall: drift19 | yes | h02_lintel_right__Basalt |
| 2 | h02_lintel_right | prop | -0.97550 | wall: drift20 | yes | h02_lintel_right__Basalt |
| 2 | h02_lintel_right | prop | -0.09350 | felt: plaza | yes | h02_lintel_right__Basalt |
| 2 | h02_lintel_right | prop | -0.97550 | felt: right_burrow | yes | h02_lintel_right__Basalt |
| 2 | h02_lintel_right | prop | -0.36550 | prop: h02_rookery_drift | yes | h02_lintel_right__Basalt |
| 5 | h05_cliff_face_w | prop | 0.00000 | wall: upper_rail9 | yes | h05_cliff_face_w__Basalt |
| 5 | h05_cliff_face_e | prop | 0.00000 | wall: upper_rail11 | yes | h05_cliff_face_e__Basalt |
| 9 | h09_conch_entry | prop | -16.50000 | prop: h09_reef_wall_skins | yes | h09_conch_entry__CoralMint, h09_conch_entry__CoralOrange, h09_conch_entry__CoralPink |
| 10 | h10_bobsled_hut | prop | -1.87500 | prop: h10_snow_wall_skins | yes | h10_bobsled_hut__Brass, h10_bobsled_hut__Canvas, h10_bobsled_hut__HullTeal, h10_bobsled_hut__Timber |
| 10 | h10_bobsled_hut | prop | 0.12500 | wall: snowwall1 | yes | h10_bobsled_hut__Canvas |
| 10 | h10_snow_walls_w | prop | -1.85000 | prop: h10_snow_wall_skins | yes | h10_snow_walls_w__SnowShadow |
| 11 | h11_fishing_hut | prop | -4.00000 | prop: h11_snowbank_skins | yes | h11_fishing_hut__Canvas, h11_fishing_hut__Timber |
| 11 | h11_floe_frame_e | prop | -7.03601 | prop: h11_snowbank_skins | yes | h11_floe_frame_e__Timber |
| 12 | h12_icebreaker | prop | -5.34000 | felt: wheel_channel | yes | h12_icebreaker__Canvas, h12_icebreaker__Glow, h12_icebreaker__HullTeal, h12_icebreaker__Snow |
| 12 | h12_icebreaker | prop | -4.80000 | wall: rail3 | yes | h12_icebreaker__HullTeal |
| 12 | h12_icebreaker | prop | -5.34000 | wall: hull18 | yes | h12_icebreaker__HullTeal |
| 14 | h14_bell_gantry | prop | -1.50000 | felt: lane | yes | h14_bell_gantry__Brass, h14_bell_gantry__Timber |
| 14 | h14_bell_gantry | prop | -1.49000 | prop: h14_icicle_bell | yes | h14_bell_gantry__Brass, h14_bell_gantry__Ice, h14_bell_gantry__Timber |
| 14 | h14_bell_gantry | prop | -5.92000 | prop: h14_rail_bollards | yes | h14_bell_gantry__Brass, h14_bell_gantry__Timber |
| 14 | h14_bell_gantry | prop | -1.85001 | wall: rail1 | yes | h14_bell_gantry__Timber |
| 14 | h14_bell_gantry | prop | -1.85001 | wall: rail9 | yes | h14_bell_gantry__Timber |
| 14 | h14_bell_gantry | prop | -0.62000 | felt: lane2 | yes | h14_bell_gantry__Timber |
| 15 | h15_lip_ice | prop | -0.64999 | felt: lip_lane | yes | h15_lip_ice__Ice |
| 18 | h18_halo_arch | prop | -9.10001 | wall: rail5 | yes | h18_halo_arch__Ice, h18_halo_arch__IceCore |
| 18 | h18_halo_arch | prop | -9.10001 | wall: rail7 | yes | h18_halo_arch__Ice, h18_halo_arch__IceCore |
| 18 | h18_halo_arch | prop | -9.14151 | felt: green | yes | h18_halo_arch__Ice, h18_halo_arch__IceCore |
| 18 | h18_halo_arch | prop | -9.64151 | prop: h18_crystal_chute | yes | h18_halo_arch__Ice, h18_halo_arch__IceCore |

Combined source/built **FLAGGED=16 unique props**; counts are not the number of overlap pairs.
