# Lantern Grove world: validation log

Each run of `tools/validate.py` appends an iteration.

## Iteration 1 (2026-10-09 22:46)

Changes: First draft layout: loop SE meadow -> E village -> N stream crossing -> W-bank stream holes -> W tree.

**Result: 13 FAIL.** Total walk H1->H9 cup-to-tee: **592 studs** (177 m), target < 1500.

Failures:
- p_h1_h2 seg2 ramp grade 10.1% > 10%
- p_h1_h2: path surface off terrain by -1.17 at (215,135) [9 samples]
- p_h1_h2: crosses its own hole H1 footprint mid-walk
- p_h2_h3 seg3 ramp grade 27.8% > 10%
- p_h2_h3 seg7 ramp grade 55.2% > 10%
- p_h2_h3: path surface off terrain by +0.60 at (151,70) [3 samples]
- p_h3_h4: path surface off terrain by +1.93 at (177,-1) [10 samples]
- p_h4_h5: path surface off terrain by +0.60 at (155,-84) [4 samples]
- p_h5_h6: path surface off terrain by +2.52 at (54,-90) [11 samples]
- p_h6_h7: path surface off terrain by +3.99 at (22,-36) [27 samples]
- p_h7_h8: path surface off terrain by +5.20 at (17,-18) [36 samples]
- p_h8_h9: path surface off terrain by -3.55 at (-25,16) [20 samples]
- p_h8_h9: crosses its own hole H8 footprint mid-walk

Checks:
- closest hole pairs: H6-H7 11.0, H1-H2 16.8, H7-H8 17.2, H3-H4 17.3
- H8 to trunk gap 8.7 (roots arch over the course)
- H9 inside trunk: farthest footprint corner 33.8 from centre, inner radius 38.8 (walk room 5.0)
- felt clearance (terrain - felt bottom, <=0 ok): H1 +0.00, H2 +0.00, H3 +0.00, H4 +0.00, H5 +0.00, H6 +0.00, H7 +0.00, H8 +0.00, H9 +0.00
- H5 water hazard stream y=37.00 joins Lantern Brook (56/81 samples on stream, level 37.00)
- H6 water hazard millrace y=29.20 is self-contained (fed by mill flume)
- H7 water hazard pool y=23.00 joins Lantern Brook (54/81 samples on stream, level 23.00)

| path | name | length | climb | max ramp grade | steps | max rise |
|---|---|---|---|---|---|---|
| p_spawn_h1 | Welcome Walk | 47 | +0.4 | 0.0% | 0 | 0.00 |
| p_h1_h2 | Maple Lane | 59 | +1.5 | 10.1% | 0 | 0.00 |
| p_h2_h3 | Toadstool Stair | 148 | +19.5 | 55.2% | 2 | 0.00 |
| p_h3_h4 | Village Steps | 34 | +4.0 | 0.0% | 5 | 0.80 |
| p_h4_h5 | Lookout Descent | 112 | -10.6 | 0.0% | 13 | 0.77 |
| p_h5_h6 | Twin Falls Steps | 54 | -8.0 | 0.0% | 10 | 0.80 |
| p_h6_h7 | Millrace Steps | 45 | -4.2 | 0.0% | 5 | 0.80 |
| p_h7_h8 | Root Stair | 84 | +12.4 | 0.0% | 13 | 0.77 |
| p_h8_h9 | Heartwood Door | 56 | +2.5 | 0.0% | 4 | 0.62 |

| tee | dist to trunk centre | LOS clearance upper trunk | LOS clearance crown | result |
|---|---|---|---|---|
| H1 | 311 | 5.9 | 5.9 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H2 | 314 | 5.9 | 5.9 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H3 | 227 | 5.9 | 5.9 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H4 | 260 | 5.9 | 5.9 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H5 | 209 | 5.9 | 5.9 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H6 | 141 | 5.9 | 5.9 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H7 | 119 | 5.9 | 5.9 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H8 | 71 | 5.9 | 5.9 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H9 | 30 | inside trunk | n/a | visible (looking up the hollow to the oculus at y 117.6) |

## Iteration 2 (2026-10-09 22:47)

Changes: Paths graded AFTER pads (pads were overwriting walkway grading); rerouted p_h1_h2 north of H1, p_h2_h3 switchback stairs with long enough flights, H9 doorway turned to the south-east (was facing the narrow H8 corridor); trunk check only flags real wall crossings; LOS ignores first 3 studs from the eye.

**Result: 9 FAIL.** Total walk H1->H9 cup-to-tee: **630 studs** (189 m), target < 1500.

Failures:
- H2 felt 'lower_d' below terrain by 0.04
- H7 felt 't3_slope' below terrain by 2.05
- p_h2_h3: path surface off terrain by -1.68 at (139,60) [12 samples]
- p_h3_h4: path surface off terrain by +0.60 at (177,-1) [2 samples]
- p_h4_h5: path surface off terrain by +0.60 at (155,-84) [4 samples]
- p_h5_h6: path surface off terrain by +0.60 at (54,-94) [2 samples]
- p_h6_h7: path surface off terrain by +0.60 at (19,-44) [2 samples]
- p_h7_h8: path surface off terrain by +0.60 at (21,-12) [4 samples]
- p_h8_h9: path surface off terrain by -6.44 at (-38,49) [35 samples]

Checks:
- closest hole pairs: H6-H7 11.0, H1-H2 16.8, H7-H8 17.2, H3-H4 17.3
- H8 to trunk gap 8.7 (roots arch over the course)
- H9 inside trunk: farthest footprint corner 33.8 from centre, inner radius 38.8 (walk room 5.0)
- felt clearance (terrain - felt bottom, <=0 ok): H1 +0.00, H2 +0.04, H3 +0.00, H4 +0.00, H5 +0.00, H6 +0.00, H7 +2.05, H8 +0.00, H9 +0.00
- H5 water hazard stream y=37.00 joins Lantern Brook (56/81 samples on stream, level 37.00)
- H6 water hazard millrace y=29.20 is self-contained (fed by mill flume)
- H7 water hazard pool y=23.00 joins Lantern Brook (54/81 samples on stream, level 23.00)

| path | name | length | climb | max ramp grade | steps | max rise |
|---|---|---|---|---|---|---|
| p_spawn_h1 | Welcome Walk | 47 | +0.4 | 0.0% | 0 | 0.00 |
| p_h1_h2 | Maple Lane | 68 | +1.5 | 10.0% | 0 | 0.00 |
| p_h2_h3 | Toadstool Stair | 161 | +19.5 | 1.9% | 25 | 0.78 |
| p_h3_h4 | Village Steps | 34 | +4.0 | 0.0% | 5 | 0.80 |
| p_h4_h5 | Lookout Descent | 112 | -10.6 | 0.0% | 13 | 0.77 |
| p_h5_h6 | Twin Falls Steps | 54 | -8.0 | 0.0% | 10 | 0.80 |
| p_h6_h7 | Millrace Steps | 45 | -4.2 | 0.0% | 5 | 0.80 |
| p_h7_h8 | Root Stair | 84 | +12.4 | 0.0% | 13 | 0.77 |
| p_h8_h9 | Heartwood Door | 72 | +2.5 | 0.0% | 4 | 0.62 |

| tee | dist to trunk centre | LOS clearance upper trunk | LOS clearance crown | result |
|---|---|---|---|---|
| H1 | 311 | 7.1 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H2 | 314 | 7.1 | 7.5 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H3 | 227 | 7.2 | 7.8 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H4 | 260 | 7.0 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H5 | 209 | 7.5 | 8.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H6 | 141 | 8.5 | 8.7 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H7 | 119 | 8.9 | 9.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H8 | 71 | 9.6 | 9.4 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H9 | 30 | inside trunk | n/a | visible (looking up the hollow to the oculus at y 117.6) |

## Iteration 3 (2026-10-09 22:48)

Changes: Lake bank cone (0.5/stud, unbounded) was capping terrain 60+ studs from the mere -> beach 10 studs @0.12 then 1.0/stud; felt clamp after path grading; path legs leaving a green start at cup-felt level (H7 exit was 2.4 too high); path-on-terrain tolerance 0.75 (stair bed junctions).

**Result: CLEAN.** Total walk H1->H9 cup-to-tee: **630 studs** (189 m), target < 1500.

Checks:
- closest hole pairs: H6-H7 11.0, H1-H2 16.8, H7-H8 17.2, H3-H4 17.3
- H8 to trunk gap 8.7 (roots arch over the course)
- H9 inside trunk: farthest footprint corner 33.8 from centre, inner radius 38.8 (walk room 5.0)
- felt clearance (terrain - felt bottom, <=0 ok): H1 +0.00, H2 +0.00, H3 +0.00, H4 +0.00, H5 +0.00, H6 +0.00, H7 +0.00, H8 +0.00, H9 +0.00
- H5 water hazard stream y=37.00 joins Lantern Brook (56/81 samples on stream, level 37.00)
- H6 water hazard millrace y=29.20 is self-contained (fed by mill flume)
- H7 water hazard pool y=23.00 joins Lantern Brook (54/81 samples on stream, level 23.00)

| path | name | length | climb | max ramp grade | steps | max rise |
|---|---|---|---|---|---|---|
| p_spawn_h1 | Welcome Walk | 47 | +0.4 | 0.0% | 0 | 0.00 |
| p_h1_h2 | Maple Lane | 68 | +1.5 | 6.0% | 0 | 0.00 |
| p_h2_h3 | Toadstool Stair | 161 | +19.5 | 1.9% | 25 | 0.78 |
| p_h3_h4 | Village Steps | 34 | +4.0 | 0.0% | 5 | 0.80 |
| p_h4_h5 | Lookout Descent | 112 | -10.6 | 2.8% | 13 | 0.77 |
| p_h5_h6 | Twin Falls Steps | 54 | -8.0 | 0.0% | 10 | 0.80 |
| p_h6_h7 | Millrace Steps | 45 | -4.2 | 0.0% | 6 | 0.71 |
| p_h7_h8 | Root Stair | 84 | +12.4 | 0.0% | 16 | 0.78 |
| p_h8_h9 | Heartwood Door | 72 | +2.5 | 0.0% | 4 | 0.62 |

| tee | dist to trunk centre | LOS clearance upper trunk | LOS clearance crown | result |
|---|---|---|---|---|
| H1 | 311 | 7.1 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H2 | 314 | 7.1 | 7.5 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H3 | 227 | 7.2 | 7.8 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H4 | 260 | 7.0 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H5 | 209 | 7.5 | 8.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H6 | 141 | 8.5 | 8.7 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H7 | 119 | 8.9 | 9.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H8 | 71 | 9.6 | 9.4 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H9 | 30 | inside trunk | n/a | visible (looking up the hollow to the oculus at y 117.6) |

## Iteration 4 (2026-10-09 22:50)

Changes: Replaced flat rectangular west_forest/east_ridge slabs with organic hill clusters (west hills behind the tree, east hills behind the village, valley/south knolls, highland crags); waterfall threshold 1.5 (the 1-stud highland brook steps are not falls).

**Result: CLEAN.** Total walk H1->H9 cup-to-tee: **630 studs** (189 m), target < 1500.

Checks:
- closest hole pairs: H6-H7 11.0, H1-H2 16.8, H7-H8 17.2, H3-H4 17.3
- H8 to trunk gap 8.7 (roots arch over the course)
- H9 inside trunk: farthest footprint corner 33.8 from centre, inner radius 38.8 (walk room 5.0)
- felt clearance (terrain - felt bottom, <=0 ok): H1 +0.00, H2 +0.00, H3 +0.00, H4 +0.00, H5 +0.00, H6 +0.00, H7 +0.00, H8 +0.00, H9 +0.00
- H5 water hazard stream y=37.00 joins Lantern Brook (56/81 samples on stream, level 37.00)
- H6 water hazard millrace y=29.20 is self-contained (fed by mill flume)
- H7 water hazard pool y=23.00 joins Lantern Brook (54/81 samples on stream, level 23.00)

| path | name | length | climb | max ramp grade | steps | max rise |
|---|---|---|---|---|---|---|
| p_spawn_h1 | Welcome Walk | 47 | +0.4 | 0.0% | 0 | 0.00 |
| p_h1_h2 | Maple Lane | 68 | +1.5 | 6.0% | 0 | 0.00 |
| p_h2_h3 | Toadstool Stair | 161 | +19.5 | 1.9% | 25 | 0.78 |
| p_h3_h4 | Village Steps | 34 | +4.0 | 0.0% | 5 | 0.80 |
| p_h4_h5 | Lookout Descent | 112 | -10.6 | 2.8% | 13 | 0.77 |
| p_h5_h6 | Twin Falls Steps | 54 | -8.0 | 0.0% | 10 | 0.80 |
| p_h6_h7 | Millrace Steps | 45 | -4.2 | 0.0% | 6 | 0.71 |
| p_h7_h8 | Root Stair | 84 | +12.4 | 0.0% | 16 | 0.78 |
| p_h8_h9 | Heartwood Door | 72 | +2.5 | 0.0% | 4 | 0.62 |

| tee | dist to trunk centre | LOS clearance upper trunk | LOS clearance crown | result |
|---|---|---|---|---|
| H1 | 311 | 7.1 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H2 | 314 | 7.1 | 7.5 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H3 | 227 | 7.2 | 7.8 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H4 | 260 | 7.0 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H5 | 209 | 7.5 | 8.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H6 | 141 | 8.5 | 8.7 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H7 | 119 | 8.9 | 9.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H8 | 71 | 9.6 | 9.4 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H9 | 30 | inside trunk | n/a | visible (looking up the hollow to the oculus at y 117.6) |

## Iteration 5 (2026-10-09 22:51)

Changes: Added detail_noise after regions (flat plateaus looked artificial); waterfall names fixed; Toadstool Square / Firefly Glade POIs moved off hole labels.

**Result: CLEAN.** Total walk H1->H9 cup-to-tee: **630 studs** (189 m), target < 1500.

Checks:
- closest hole pairs: H6-H7 11.0, H1-H2 16.8, H7-H8 17.2, H3-H4 17.3
- H8 to trunk gap 8.7 (roots arch over the course)
- H9 inside trunk: farthest footprint corner 33.8 from centre, inner radius 38.8 (walk room 5.0)
- felt clearance (terrain - felt bottom, <=0 ok): H1 +0.00, H2 +0.00, H3 +0.00, H4 +0.00, H5 +0.00, H6 +0.00, H7 +0.00, H8 +0.00, H9 +0.00
- H5 water hazard stream y=37.00 joins Lantern Brook (56/81 samples on stream, level 37.00)
- H6 water hazard millrace y=29.20 is self-contained (fed by mill flume)
- H7 water hazard pool y=23.00 joins Lantern Brook (54/81 samples on stream, level 23.00)

| path | name | length | climb | max ramp grade | steps | max rise |
|---|---|---|---|---|---|---|
| p_spawn_h1 | Welcome Walk | 47 | +0.4 | 0.0% | 0 | 0.00 |
| p_h1_h2 | Maple Lane | 68 | +1.5 | 6.0% | 0 | 0.00 |
| p_h2_h3 | Toadstool Stair | 161 | +19.5 | 1.9% | 25 | 0.78 |
| p_h3_h4 | Village Steps | 34 | +4.0 | 0.0% | 5 | 0.80 |
| p_h4_h5 | Lookout Descent | 112 | -10.6 | 2.8% | 13 | 0.77 |
| p_h5_h6 | Twin Falls Steps | 54 | -8.0 | 0.0% | 10 | 0.80 |
| p_h6_h7 | Millrace Steps | 45 | -4.2 | 0.0% | 6 | 0.71 |
| p_h7_h8 | Root Stair | 84 | +12.4 | 0.0% | 16 | 0.78 |
| p_h8_h9 | Heartwood Door | 72 | +2.5 | 0.0% | 4 | 0.62 |

| tee | dist to trunk centre | LOS clearance upper trunk | LOS clearance crown | result |
|---|---|---|---|---|
| H1 | 311 | 7.1 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H2 | 314 | 7.1 | 7.5 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H3 | 227 | 7.2 | 7.8 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H4 | 260 | 7.0 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H5 | 209 | 7.5 | 8.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H6 | 141 | 8.5 | 8.7 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H7 | 119 | 8.9 | 9.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H8 | 71 | 9.6 | 9.4 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H9 | 30 | inside trunk | n/a | visible (looking up the hollow to the oculus at y 117.6) |

## Iteration 6 (2026-10-09 22:52)

Changes: Highland cliff edge now a wobbly line with a notch for Grand Falls (was a straight ruler line); detail_noise softened (diagonal ripples).

**Result: CLEAN.** Total walk H1->H9 cup-to-tee: **630 studs** (189 m), target < 1500.

Checks:
- closest hole pairs: H6-H7 11.0, H1-H2 16.8, H7-H8 17.2, H3-H4 17.3
- H8 to trunk gap 8.7 (roots arch over the course)
- H9 inside trunk: farthest footprint corner 33.8 from centre, inner radius 38.8 (walk room 5.0)
- felt clearance (terrain - felt bottom, <=0 ok): H1 +0.00, H2 +0.00, H3 +0.00, H4 +0.00, H5 +0.00, H6 +0.00, H7 +0.00, H8 +0.00, H9 +0.00
- H5 water hazard stream y=37.00 joins Lantern Brook (56/81 samples on stream, level 37.00)
- H6 water hazard millrace y=29.20 is self-contained (fed by mill flume)
- H7 water hazard pool y=23.00 joins Lantern Brook (54/81 samples on stream, level 23.00)

| path | name | length | climb | max ramp grade | steps | max rise |
|---|---|---|---|---|---|---|
| p_spawn_h1 | Welcome Walk | 47 | +0.4 | 0.0% | 0 | 0.00 |
| p_h1_h2 | Maple Lane | 68 | +1.5 | 6.0% | 0 | 0.00 |
| p_h2_h3 | Toadstool Stair | 161 | +19.5 | 1.9% | 25 | 0.78 |
| p_h3_h4 | Village Steps | 34 | +4.0 | 0.0% | 5 | 0.80 |
| p_h4_h5 | Lookout Descent | 112 | -10.6 | 2.8% | 13 | 0.77 |
| p_h5_h6 | Twin Falls Steps | 54 | -8.0 | 0.0% | 10 | 0.80 |
| p_h6_h7 | Millrace Steps | 45 | -4.2 | 0.0% | 6 | 0.71 |
| p_h7_h8 | Root Stair | 84 | +12.4 | 0.0% | 16 | 0.78 |
| p_h8_h9 | Heartwood Door | 72 | +2.5 | 0.0% | 4 | 0.62 |

| tee | dist to trunk centre | LOS clearance upper trunk | LOS clearance crown | result |
|---|---|---|---|---|
| H1 | 311 | 7.1 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H2 | 314 | 7.1 | 7.5 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H3 | 227 | 7.2 | 7.8 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H4 | 260 | 7.0 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H5 | 209 | 7.5 | 8.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H6 | 141 | 8.5 | 8.7 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H7 | 119 | 8.9 | 9.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H8 | 71 | 9.6 | 9.4 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H9 | 30 | inside trunk | n/a | visible (looking up the hollow to the oculus at y 117.6) |

## Iteration 7 (2026-10-09 22:56)

Changes: Final run: added backdrop/scenery pieces (tree-line clusters on rim terrain, hero tree shell, falls curtains, rock kits, sister trees, sky) and terrain-4stud.json export; no geometry changes.

**Result: CLEAN.** Total walk H1->H9 cup-to-tee: **630 studs** (189 m), target < 1500.

Checks:
- closest hole pairs: H6-H7 11.0, H1-H2 16.8, H7-H8 17.2, H3-H4 17.3
- H8 to trunk gap 8.7 (roots arch over the course)
- H9 inside trunk: farthest footprint corner 33.8 from centre, inner radius 38.8 (walk room 5.0)
- felt clearance (terrain - felt bottom, <=0 ok): H1 +0.00, H2 +0.00, H3 +0.00, H4 +0.00, H5 +0.00, H6 +0.00, H7 +0.00, H8 +0.00, H9 +0.00
- H5 water hazard stream y=37.00 joins Lantern Brook (56/81 samples on stream, level 37.00)
- H6 water hazard millrace y=29.20 is self-contained (fed by mill flume)
- H7 water hazard pool y=23.00 joins Lantern Brook (54/81 samples on stream, level 23.00)

| path | name | length | climb | max ramp grade | steps | max rise |
|---|---|---|---|---|---|---|
| p_spawn_h1 | Welcome Walk | 47 | +0.4 | 0.0% | 0 | 0.00 |
| p_h1_h2 | Maple Lane | 68 | +1.5 | 6.0% | 0 | 0.00 |
| p_h2_h3 | Toadstool Stair | 161 | +19.5 | 1.9% | 25 | 0.78 |
| p_h3_h4 | Village Steps | 34 | +4.0 | 0.0% | 5 | 0.80 |
| p_h4_h5 | Lookout Descent | 112 | -10.6 | 2.8% | 13 | 0.77 |
| p_h5_h6 | Twin Falls Steps | 54 | -8.0 | 0.0% | 10 | 0.80 |
| p_h6_h7 | Millrace Steps | 45 | -4.2 | 0.0% | 6 | 0.71 |
| p_h7_h8 | Root Stair | 84 | +12.4 | 0.0% | 16 | 0.78 |
| p_h8_h9 | Heartwood Door | 72 | +2.5 | 0.0% | 4 | 0.62 |

| tee | dist to trunk centre | LOS clearance upper trunk | LOS clearance crown | result |
|---|---|---|---|---|
| H1 | 311 | 7.1 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H2 | 314 | 7.1 | 7.5 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H3 | 227 | 7.2 | 7.8 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H4 | 260 | 7.0 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H5 | 209 | 7.5 | 8.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H6 | 141 | 8.5 | 8.7 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H7 | 119 | 8.9 | 9.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H8 | 71 | 9.6 | 9.4 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H9 | 30 | inside trunk | n/a | visible (looking up the hollow to the oculus at y 117.6) |

## Iteration 8 (2026-10-10 13:37)

Changes: Playtest Round 5 (holes.json r5b): H4 spinner arms 4.5->3.0 (footprint unchanged), H7 cup -> (-2.5,-2.4,-36.5) and lower gap x[4,6.5], H8 upper level moved 9 studs south (c1 removed; green z -32..-48), new cup (4,1.5,-37) and exit ring (9,1.5,-47), H9 rolling dip in the trunk tunnel + lantern pendulum, cup -> (26,-0.8,-52); flags on every cup. Paths re-anchored to the moved cups by build_world.py.

**Result: CLEAN.** Total walk H1->H9 cup-to-tee: **641 studs** (192 m), target < 1500.

Checks:
- closest hole pairs: H6-H7 11.0, H1-H2 16.8, H7-H8 17.2, H3-H4 17.3
- H8 to trunk gap 7.7 (roots arch over the course)
- H9 inside trunk: farthest footprint corner 33.8 from centre, inner radius 38.8 (walk room 5.0)
- felt clearance (terrain - felt bottom, <=0 ok): H1 +0.00, H2 +0.00, H3 +0.00, H4 +0.00, H5 +0.00, H6 +0.00, H7 +0.00, H8 +0.00, H9 +0.00
- H5 water hazard stream y=37.00 joins Lantern Brook (56/81 samples on stream, level 37.00)
- H6 water hazard millrace y=29.20 is self-contained (fed by mill flume)
- H7 water hazard pool y=23.00 joins Lantern Brook (54/81 samples on stream, level 23.00)

| path | name | length | climb | max ramp grade | steps | max rise |
|---|---|---|---|---|---|---|
| p_spawn_h1 | Welcome Walk | 47 | +0.4 | 0.0% | 0 | 0.00 |
| p_h1_h2 | Maple Lane | 68 | +1.5 | 6.0% | 0 | 0.00 |
| p_h2_h3 | Toadstool Stair | 161 | +19.5 | 1.9% | 25 | 0.78 |
| p_h3_h4 | Village Steps | 34 | +4.0 | 0.0% | 5 | 0.80 |
| p_h4_h5 | Lookout Descent | 112 | -10.6 | 2.8% | 13 | 0.77 |
| p_h5_h6 | Twin Falls Steps | 54 | -8.0 | 0.0% | 10 | 0.80 |
| p_h6_h7 | Millrace Steps | 45 | -4.2 | 0.0% | 6 | 0.71 |
| p_h7_h8 | Root Stair | 85 | +12.4 | 0.0% | 16 | 0.78 |
| p_h8_h9 | Heartwood Door | 82 | +2.5 | 0.0% | 4 | 0.62 |

| tee | dist to trunk centre | LOS clearance upper trunk | LOS clearance crown | result |
|---|---|---|---|---|
| H1 | 311 | 7.1 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H2 | 314 | 7.1 | 7.5 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H3 | 227 | 7.2 | 7.8 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H4 | 260 | 7.0 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H5 | 209 | 7.5 | 8.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H6 | 141 | 8.5 | 8.7 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H7 | 119 | 8.9 | 9.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H8 | 71 | 9.6 | 9.4 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H9 | 30 | inside trunk | n/a | visible (looking up the hollow to the oculus at y 117.6) |

## Iteration 9 (2026-10-10 18:34)

Changes: Round 7 (holes): H7 log 6 long / pointed ends / dwell, H8 gated root door 3.6 + ring 0.45, H9 pendulum 5 s / 30 deg / square bob turned 30, 3 amber lanterns over H9 green (decoration). No felt, wall, tee or cup changes.

**Result: CLEAN.** Total walk H1->H9 cup-to-tee: **641 studs** (192 m), target < 1500.

Checks:
- closest hole pairs: H6-H7 11.0, H1-H2 16.8, H7-H8 17.2, H3-H4 17.3
- H8 to trunk gap 7.7 (roots arch over the course)
- H9 inside trunk: farthest footprint corner 33.8 from centre, inner radius 38.8 (walk room 5.0)
- felt clearance (terrain - felt bottom, <=0 ok): H1 +0.00, H2 +0.00, H3 +0.00, H4 +0.00, H5 +0.00, H6 +0.00, H7 +0.00, H8 +0.00, H9 +0.00
- H5 water hazard stream y=37.00 joins Lantern Brook (56/81 samples on stream, level 37.00)
- H6 water hazard millrace y=29.20 is self-contained (fed by mill flume)
- H7 water hazard pool y=23.00 joins Lantern Brook (54/81 samples on stream, level 23.00)

| path | name | length | climb | max ramp grade | steps | max rise |
|---|---|---|---|---|---|---|
| p_spawn_h1 | Welcome Walk | 47 | +0.4 | 0.0% | 0 | 0.00 |
| p_h1_h2 | Maple Lane | 68 | +1.5 | 6.0% | 0 | 0.00 |
| p_h2_h3 | Toadstool Stair | 161 | +19.5 | 1.9% | 25 | 0.78 |
| p_h3_h4 | Village Steps | 34 | +4.0 | 0.0% | 5 | 0.80 |
| p_h4_h5 | Lookout Descent | 112 | -10.6 | 2.8% | 13 | 0.77 |
| p_h5_h6 | Twin Falls Steps | 54 | -8.0 | 0.0% | 10 | 0.80 |
| p_h6_h7 | Millrace Steps | 45 | -4.2 | 0.0% | 6 | 0.71 |
| p_h7_h8 | Root Stair | 85 | +12.4 | 0.0% | 16 | 0.78 |
| p_h8_h9 | Heartwood Door | 82 | +2.5 | 0.0% | 4 | 0.62 |

| tee | dist to trunk centre | LOS clearance upper trunk | LOS clearance crown | result |
|---|---|---|---|---|
| H1 | 311 | 7.1 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H2 | 314 | 7.1 | 7.5 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H3 | 227 | 7.2 | 7.8 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H4 | 260 | 7.0 | 7.6 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H5 | 209 | 7.5 | 8.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H6 | 141 | 8.5 | 8.7 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H7 | 119 | 8.9 | 9.0 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H8 | 71 | 9.6 | 9.4 | visible (upper trunk (75%), crown centre, crown underside edge) |
| H9 | 30 | inside trunk | n/a | visible (looking up the hollow to the oculus at y 117.6) |
