# Sugarloaf Canyon world: validation log

Each run of `tools/validate.py` appends an iteration. Holes are concept footprints (no holes.json yet).

## Iteration 1 (2026-10-11 15:37)

Changes: First draft layout: town (H1-3) -> Narrows slot (H4-6) -> Taffy Mesa (H7-9) -> Reservoir Bench/dam (H10-12) -> Hoodoo Bench (H13-15) -> Crown (H16-18), gondola home

**Result: 22 FAIL** (3 warnings). Walking spawn -> H18 cup: **2678 studs** (803 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Failures:
- H3 declares a span over Sugarloaf River but nothing is below it (gap 0.3)
- H11 pad 'upper' is cut by water outside a declared span (45 samples)
- p_h8_h9 seg2 bridge end (360,-26) y 70.0 vs terrain 65.4
- p_h8_h9 seg2 bridge end (360,-80) y 70.0 vs terrain 63.9
- p_h8_h9: walkway off terrain by -6.13 at (360,-80) [12 samples]
- p_h11_h12: does not end at H12 tee
- p_h11_h12: walk-in point 8.0 from the H12 footprint (> 6)
- p_h11_h12 seg6 dam_crest end (46,-305) y 116.0 vs terrain 45.5
- p_h11_h12 seg6 dam_crest end (-46,-305) y 116.0 vs terrain 45.5
- p_h11_h12: walkway off terrain by -70.51 at (46,-305) [179 samples]
- H10: Old Sugarloaf not visible from the tee ({'summit': -8.028497488578537, 'upper dome': -4.344728640732399})
- H12: Old Sugarloaf not visible from the tee ({'summit': -3.044131486497534, 'upper dome': -8.601464579687814})
- H13: Old Sugarloaf not visible from the tee ({'summit': -5.712518245484887, 'upper dome': -9.626352279320002})
- H14: Old Sugarloaf not visible from the tee ({'summit': -5.244544874007971, 'upper dome': -9.247998122876936})
- H15: Old Sugarloaf not visible from the tee ({'summit': -4.609004034643846, 'upper dome': -8.34576053298116})
- H16: Old Sugarloaf not visible from the tee ({'summit': -1.2254436809973868, 'upper dome': -2.612082103532856})
- H17: Old Sugarloaf not visible from the tee ({'summit': -10.858072217941896, 'upper dome': -13.816264405918332})
- H18: Old Sugarloaf not visible from the tee ({'summit': -25.738326882598074, 'upper dome': -31.27669002526099})
- teleport tp_junction: 15 studs from the nearest walkway
- teleport tp_dam: y 116.0 vs terrain 60.3
- teleport tp_dam: ground not flat (+-2.4 within 3 studs)
- reservoir rim below water level at 56 of 360 points (outside the dam)

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- 6 teleport points checked (on flat ground, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 44.8 (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 86.3

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 0.3 below the pad |
| H4 | Crystal Corridor | 2 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112/116 | 0.00 | 4.3 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.04 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 4 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186/190 | 0.00 | 4.6 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 59 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 244 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 244 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 72 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 55 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 77 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 87 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 173 | +0.0 | 0.0% | 0 | 0.00 | 4 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 270 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 162 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 405 | -4.0 | 0.0% | 5 | 0.80 | 6 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 211 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 81 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 76 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 143 | +40.0 | 0.0% | 0 | 0.00 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h17_h18 | Rim Walk | 145 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 85 | -172.0 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (262) | ok |
|---|---|---|---|
| H1 | 0 | 98 | ok |
| H2 | 0 | 98 | ok |
| H3 | 90 | 172 | ok |
| H4 | 90 | 172 | ok |
| H5 | 0 | 98 | ok |
| H6 | 0 | 98 | ok |
| H7 | 0 | 98 | ok |
| H8 | 0 | 98 | ok |
| H9 | 90 | 172 | ok |
| H10 | 180 | 82 | ok |
| H11 | 0 | 98 | ok |
| H12 | 90 | 172 | ok |
| H13 | 180 | 82 | ok |
| H14 | 180 | 82 | ok |
| H15 | 180 | 82 | ok |
| H16 | 180 | 82 | ok |
| H17 | 0 | 98 | ok |
| H18 | 0 | 98 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +5.9 | +5.8 | visible |
| H2 | 540 | +6.0 | +5.8 | visible |
| H3 | 492 | +6.0 | +5.9 | visible |
| H4 | 475 | -39.5 | -40.1 | hidden (slot canyon) |
| H5 | 498 | -35.1 | -37.1 | hidden (slot canyon) |
| H6 | 434 | -31.5 | -33.4 | hidden (slot canyon) |
| H7 | 382 | +5.6 | +2.3 | visible |
| H8 | 336 | +5.6 | +4.6 | visible |
| H9 | 251 | +5.7 | +5.6 | visible |
| H10 | 270 | -8.0 | -4.3 | BLOCKED |
| H11 | 141 | +1.6 | +1.7 | visible |
| H12 | 313 | -3.0 | -8.6 | BLOCKED |
| H13 | 412 | -5.7 | -9.6 | BLOCKED |
| H14 | 386 | -5.2 | -9.2 | BLOCKED |
| H15 | 380 | -4.6 | -8.3 | BLOCKED |
| H16 | 451 | -1.2 | -2.6 | BLOCKED |
| H17 | 558 | -10.9 | -13.8 | BLOCKED |
| H18 | 620 | -25.7 | -31.3 | BLOCKED |

## Iteration 2 (2026-10-11 15:38)

Changes: Bank cones limited to bank_reach (they were capping Old Sugarloaf and the bench); river starts below the dam; missing walk leg on p_h11_h12; span gap measured on final terrain

**Result: 3 FAIL** (3 warnings). Walking spawn -> H18 cup: **2687 studs** (806 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Failures:
- H17: Old Sugarloaf not visible from the tee ({'summit': -0.9336355493411475, 'upper dome': -11.000431952551821})
- H18: Old Sugarloaf not visible from the tee ({'summit': -4.152492503081646, 'upper dome': -18.02996335302626})
- reservoir rim below water level at 4 of 360 points (outside the dam)

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- 6 teleport points checked (on flat ground, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 106.8 (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 167.1

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 2 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112/116 | 0.00 | 4.3 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 4 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186/190 | 0.00 | 4.6 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 59 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 244 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 244 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 72 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 55 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 77 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 87 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 173 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 270 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 162 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 414 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 211 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 81 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 76 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 143 | +40.0 | 0.0% | 0 | 0.00 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h17_h18 | Rim Walk | 145 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 85 | -172.0 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (262) | ok |
|---|---|---|---|
| H1 | 0 | 98 | ok |
| H2 | 0 | 98 | ok |
| H3 | 90 | 172 | ok |
| H4 | 90 | 172 | ok |
| H5 | 0 | 98 | ok |
| H6 | 0 | 98 | ok |
| H7 | 0 | 98 | ok |
| H8 | 0 | 98 | ok |
| H9 | 90 | 172 | ok |
| H10 | 180 | 82 | ok |
| H11 | 0 | 98 | ok |
| H12 | 90 | 172 | ok |
| H13 | 180 | 82 | ok |
| H14 | 180 | 82 | ok |
| H15 | 180 | 82 | ok |
| H16 | 180 | 82 | ok |
| H17 | 0 | 98 | ok |
| H18 | 0 | 98 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.4 | +6.2 | visible |
| H2 | 540 | +6.5 | +6.3 | visible |
| H3 | 492 | +6.6 | +6.4 | visible |
| H4 | 475 | -34.8 | -35.3 | hidden (slot canyon) |
| H5 | 498 | -24.9 | -29.4 | hidden (slot canyon) |
| H6 | 434 | -21.4 | -25.7 | hidden (slot canyon) |
| H7 | 382 | +6.4 | +6.1 | visible |
| H8 | 336 | +6.5 | +6.1 | visible |
| H9 | 251 | +6.9 | +6.4 | visible |
| H10 | 270 | +6.2 | +5.6 | visible |
| H11 | 141 | +6.7 | +5.7 | visible |
| H12 | 313 | +6.1 | +5.6 | visible |
| H13 | 412 | +5.6 | +0.5 | visible |
| H14 | 386 | +5.6 | +0.8 | visible |
| H15 | 380 | +5.6 | +1.2 | visible |
| H16 | 451 | +3.8 | +1.0 | visible |
| H17 | 558 | -0.9 | -11.0 | BLOCKED |
| H18 | 620 | -4.2 | -18.0 | BLOCKED |

## Iteration 3 (2026-10-11 15:38)

Changes: Old Sugarloaf raised to summit ~208 (was hidden by the Crown plateau from H17/H18); rim check skips the creek mouth

**Result: CLEAN** (3 warnings). Walking spawn -> H18 cup: **2687 studs** (806 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- 6 teleport points checked (on flat ground, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 207.1

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 2 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112/116 | 0.00 | 4.3 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 4 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186/190 | 0.00 | 4.6 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 59 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 244 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 244 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 72 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 55 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 77 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 87 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 173 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 270 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 162 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 414 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 211 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 81 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 76 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 143 | +40.0 | 0.0% | 0 | 0.00 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h17_h18 | Rim Walk | 145 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 85 | -172.0 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (262) | ok |
|---|---|---|---|
| H1 | 0 | 98 | ok |
| H2 | 0 | 98 | ok |
| H3 | 90 | 172 | ok |
| H4 | 90 | 172 | ok |
| H5 | 0 | 98 | ok |
| H6 | 0 | 98 | ok |
| H7 | 0 | 98 | ok |
| H8 | 0 | 98 | ok |
| H9 | 90 | 172 | ok |
| H10 | 180 | 82 | ok |
| H11 | 0 | 98 | ok |
| H12 | 90 | 172 | ok |
| H13 | 180 | 82 | ok |
| H14 | 180 | 82 | ok |
| H15 | 180 | 82 | ok |
| H16 | 180 | 82 | ok |
| H17 | 0 | 98 | ok |
| H18 | 0 | 98 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.7 | +6.4 | visible |
| H2 | 540 | +6.8 | +6.5 | visible |
| H3 | 492 | +6.9 | +6.6 | visible |
| H4 | 475 | -31.3 | -34.6 | hidden (slot canyon) |
| H5 | 498 | -19.8 | -25.5 | hidden (slot canyon) |
| H6 | 434 | -16.2 | -21.8 | hidden (slot canyon) |
| H7 | 382 | +6.8 | +6.4 | visible |
| H8 | 336 | +6.9 | +6.5 | visible |
| H9 | 251 | +7.3 | +6.8 | visible |
| H10 | 270 | +6.7 | +6.0 | visible |
| H11 | 141 | +7.6 | +6.6 | visible |
| H12 | 313 | +6.5 | +6.0 | visible |
| H13 | 412 | +6.0 | +5.2 | visible |
| H14 | 386 | +6.0 | +5.3 | visible |
| H15 | 380 | +6.0 | +5.4 | visible |
| H16 | 451 | +5.6 | +2.9 | visible |
| H17 | 558 | +5.6 | -4.0 | visible |
| H18 | 620 | +5.6 | -8.3 | visible |

## Iteration 4 (2026-10-11 15:40)

Changes: Waterfall naming (Fizzwater Cascade); no layout change

**Result: CLEAN** (3 warnings). Walking spawn -> H18 cup: **2687 studs** (806 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- 6 teleport points checked (on flat ground, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 207.1

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 2 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112/116 | 0.00 | 4.3 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 4 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186/190 | 0.00 | 4.6 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 59 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 244 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 244 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 72 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 55 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 77 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 87 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 173 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 270 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 162 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 414 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 211 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 81 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 76 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 143 | +40.0 | 0.0% | 0 | 0.00 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h17_h18 | Rim Walk | 145 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 85 | -172.0 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (262) | ok |
|---|---|---|---|
| H1 | 0 | 98 | ok |
| H2 | 0 | 98 | ok |
| H3 | 90 | 172 | ok |
| H4 | 90 | 172 | ok |
| H5 | 0 | 98 | ok |
| H6 | 0 | 98 | ok |
| H7 | 0 | 98 | ok |
| H8 | 0 | 98 | ok |
| H9 | 90 | 172 | ok |
| H10 | 180 | 82 | ok |
| H11 | 0 | 98 | ok |
| H12 | 90 | 172 | ok |
| H13 | 180 | 82 | ok |
| H14 | 180 | 82 | ok |
| H15 | 180 | 82 | ok |
| H16 | 180 | 82 | ok |
| H17 | 0 | 98 | ok |
| H18 | 0 | 98 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.7 | +6.4 | visible |
| H2 | 540 | +6.8 | +6.5 | visible |
| H3 | 492 | +6.9 | +6.6 | visible |
| H4 | 475 | -31.3 | -34.6 | hidden (slot canyon) |
| H5 | 498 | -19.8 | -25.5 | hidden (slot canyon) |
| H6 | 434 | -16.2 | -21.8 | hidden (slot canyon) |
| H7 | 382 | +6.8 | +6.4 | visible |
| H8 | 336 | +6.9 | +6.5 | visible |
| H9 | 251 | +7.3 | +6.8 | visible |
| H10 | 270 | +6.7 | +6.0 | visible |
| H11 | 141 | +7.6 | +6.6 | visible |
| H12 | 313 | +6.5 | +6.0 | visible |
| H13 | 412 | +6.0 | +5.2 | visible |
| H14 | 386 | +6.0 | +5.3 | visible |
| H15 | 380 | +6.0 | +5.4 | visible |
| H16 | 451 | +5.6 | +2.9 | visible |
| H17 | 558 | +5.6 | -4.0 | visible |
| H18 | 620 | +5.6 | -8.3 | visible |

## Iteration 5 (2026-10-11 17:21)

Changes: holes.json exists (18 holes, tools/build_holes.py): cup positions and pars (H15 par 4 -> 3, total 53) now read from holes.json; new check: every holes.json felt/rail corner inside the concept pads, tee at the local origin, placements equal

**Result: CLEAN** (3 warnings). Walking spawn -> H18 cup: **2691 studs** (807 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- holes.json: 18 holes, total par 53; every felt and rail corner checked against the pads
- 6 teleport points checked (on flat ground, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 207.1

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 2 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112/116 | 0.00 | 4.3 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186/190 | 0.00 | 4.6 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |
|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | 2 / 7 | 36 | 0 | (66.0, 18.0, 439.5) |
| H2 | Mine-Cart Junction | 3 | 7 / 24 | 124 | 0 | (91.0, 18.0, 364.0) |
| H3 | Ranger's Riverbend | 3 | 4 / 14 | 72 | 0 | (-39.5, 18.0, 331.0) |
| H4 | Crystal Corridor | 2 | 2 / 9 | 44 | 0 | (239.0, 18.0, 334.5) |
| H5 | Echo Slot | 3 | 14 / 20 | 136 | 0 | (279.5, 22.0, 284.0) |
| H6 | Flash Flood | 3 | 7 / 18 | 100 | 0 | (276.0, 26.0, 210.0) |
| H7 | Rope Bridge Run | 4 | 5 / 18 | 92 | 0 | (343.0, 70.0, 90.0) |
| H8 | Gumdrop Gulch | 3 | 11 / 28 | 156 | 0 | (365.0, 70.0, 0.0) |
| H9 | Lollipop Windmill | 3 | 6 / 18 | 96 | 0 | (372.0, 70.0, -111.5) |
| H10 | Sluice Chute | 2 | 4 / 14 | 72 | 0 | (283.0, 112.4, -266.5) |
| H11 | Floodgate Lock | 3 | 7 / 22 | 116 | 0 | (150.0, 120.0, -295.0) |
| H12 | Intake Tower | 4 | 7 / 13 | 80 | 0 | (-142.0, 116.0, -268.0) |
| H13 | Hoodoo Maze | 3 | 7 / 21 | 112 | 0 | (-300.5, 150.0, -239.0) |
| H14 | Ore Bucket Swing | 3 | 4 / 10 | 56 | 0 | (-301.0, 150.8, -156.0) |
| H15 | Sugar Dune | 3 | 5 / 11 | 64 | 0 | (-306.0, 145.4, -58.0) |
| H16 | Sinkhole Drop | 2 | 8 / 8 | 64 | 0 | (-301.8, 186.4, 150.5) |
| H17 | Sundial | 3 | 2 / 17 | 76 | 0 | (-345.0, 190.0, 188.0) |
| H18 | Sunset Arch | 4 | 9 / 18 | 108 | 0 | (-412.0, 190.8, 172.0) |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 229 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 251 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 68 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 57 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 82 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 90 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 165 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 274 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 168 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 421 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 209 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 82 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 77 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 145 | +40.0 | 0.0% | 0 | 0.00 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h17_h18 | Rim Walk | 146 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 91 | -172.0 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (262) | ok |
|---|---|---|---|
| H1 | 0 | 98 | ok |
| H2 | 0 | 98 | ok |
| H3 | 90 | 172 | ok |
| H4 | 90 | 172 | ok |
| H5 | 0 | 98 | ok |
| H6 | 0 | 98 | ok |
| H7 | 0 | 98 | ok |
| H8 | 0 | 98 | ok |
| H9 | 90 | 172 | ok |
| H10 | 180 | 82 | ok |
| H11 | 0 | 98 | ok |
| H12 | 90 | 172 | ok |
| H13 | 180 | 82 | ok |
| H14 | 180 | 82 | ok |
| H15 | 180 | 82 | ok |
| H16 | 180 | 82 | ok |
| H17 | 0 | 98 | ok |
| H18 | 0 | 98 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.7 | +6.4 | visible |
| H2 | 540 | +6.8 | +6.5 | visible |
| H3 | 492 | +6.9 | +6.6 | visible |
| H4 | 475 | -31.3 | -34.6 | hidden (slot canyon) |
| H5 | 498 | -19.8 | -25.5 | hidden (slot canyon) |
| H6 | 434 | -16.2 | -21.8 | hidden (slot canyon) |
| H7 | 382 | +6.8 | +6.4 | visible |
| H8 | 336 | +6.9 | +6.5 | visible |
| H9 | 251 | +7.3 | +6.8 | visible |
| H10 | 270 | +6.7 | +6.0 | visible |
| H11 | 141 | +7.6 | +6.6 | visible |
| H12 | 313 | +6.5 | +6.0 | visible |
| H13 | 412 | +6.0 | +5.2 | visible |
| H14 | 386 | +6.0 | +5.3 | visible |
| H15 | 380 | +6.0 | +5.4 | visible |
| H16 | 451 | +5.6 | +2.9 | visible |
| H17 | 558 | +5.6 | -4.0 | visible |
| H18 | 620 | +5.6 | -8.3 | visible |

## Iteration 6 (2026-10-11 17:36)

Changes: Final hole geometry (playtest-log Round 6): walkways start at the final cups (H6, H9, H11, H14, H17, H18 cups moved in tuning); every holes.json felt/rail corner inside its pads

**Result: CLEAN** (3 warnings). Walking spawn -> H18 cup: **2691 studs** (807 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- holes.json: 18 holes, total par 53; every felt and rail corner checked against the pads
- 6 teleport points checked (on flat ground, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 207.1

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 2 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112/116 | 0.00 | 4.3 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186/190 | 0.00 | 4.6 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |
|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | 2 / 7 | 36 | 0 | (66.0, 18.0, 439.5) |
| H2 | Mine-Cart Junction | 3 | 7 / 24 | 124 | 0 | (91.0, 18.0, 364.0) |
| H3 | Ranger's Riverbend | 3 | 4 / 14 | 72 | 0 | (-39.5, 18.0, 331.0) |
| H4 | Crystal Corridor | 2 | 2 / 9 | 44 | 0 | (239.0, 18.0, 334.5) |
| H5 | Echo Slot | 3 | 14 / 20 | 136 | 0 | (279.5, 22.0, 284.0) |
| H6 | Flash Flood | 3 | 7 / 18 | 100 | 0 | (276.0, 26.0, 210.0) |
| H7 | Rope Bridge Run | 4 | 5 / 18 | 92 | 0 | (343.0, 70.0, 90.0) |
| H8 | Gumdrop Gulch | 3 | 11 / 28 | 156 | 0 | (365.0, 70.0, 0.0) |
| H9 | Lollipop Windmill | 3 | 6 / 18 | 96 | 0 | (372.0, 70.0, -111.5) |
| H10 | Sluice Chute | 2 | 4 / 14 | 72 | 0 | (283.0, 112.4, -266.5) |
| H11 | Floodgate Lock | 3 | 7 / 22 | 116 | 0 | (150.0, 120.0, -295.0) |
| H12 | Intake Tower | 4 | 7 / 13 | 80 | 0 | (-142.0, 116.0, -268.0) |
| H13 | Hoodoo Maze | 3 | 7 / 21 | 112 | 0 | (-300.5, 150.0, -239.0) |
| H14 | Ore Bucket Swing | 3 | 4 / 10 | 56 | 0 | (-301.0, 150.8, -156.0) |
| H15 | Sugar Dune | 3 | 5 / 11 | 64 | 0 | (-306.0, 145.4, -58.0) |
| H16 | Sinkhole Drop | 2 | 8 / 8 | 64 | 0 | (-301.8, 186.4, 150.5) |
| H17 | Sundial | 3 | 2 / 17 | 76 | 0 | (-345.0, 190.0, 188.0) |
| H18 | Sunset Arch | 4 | 9 / 18 | 108 | 0 | (-412.0, 190.8, 172.0) |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 229 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 251 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 68 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 57 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 82 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 90 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 165 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 274 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 168 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 421 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 209 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 82 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 77 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 145 | +40.0 | 0.0% | 0 | 0.00 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h17_h18 | Rim Walk | 146 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 91 | -172.0 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (262) | ok |
|---|---|---|---|
| H1 | 0 | 98 | ok |
| H2 | 0 | 98 | ok |
| H3 | 90 | 172 | ok |
| H4 | 90 | 172 | ok |
| H5 | 0 | 98 | ok |
| H6 | 0 | 98 | ok |
| H7 | 0 | 98 | ok |
| H8 | 0 | 98 | ok |
| H9 | 90 | 172 | ok |
| H10 | 180 | 82 | ok |
| H11 | 0 | 98 | ok |
| H12 | 90 | 172 | ok |
| H13 | 180 | 82 | ok |
| H14 | 180 | 82 | ok |
| H15 | 180 | 82 | ok |
| H16 | 180 | 82 | ok |
| H17 | 0 | 98 | ok |
| H18 | 0 | 98 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.7 | +6.4 | visible |
| H2 | 540 | +6.8 | +6.5 | visible |
| H3 | 492 | +6.9 | +6.6 | visible |
| H4 | 475 | -31.3 | -34.6 | hidden (slot canyon) |
| H5 | 498 | -19.8 | -25.5 | hidden (slot canyon) |
| H6 | 434 | -16.2 | -21.8 | hidden (slot canyon) |
| H7 | 382 | +6.8 | +6.4 | visible |
| H8 | 336 | +6.9 | +6.5 | visible |
| H9 | 251 | +7.3 | +6.8 | visible |
| H10 | 270 | +6.7 | +6.0 | visible |
| H11 | 141 | +7.6 | +6.6 | visible |
| H12 | 313 | +6.5 | +6.0 | visible |
| H13 | 412 | +6.0 | +5.2 | visible |
| H14 | 386 | +6.0 | +5.3 | visible |
| H15 | 380 | +6.0 | +5.4 | visible |
| H16 | 451 | +5.6 | +2.9 | visible |
| H17 | 558 | +5.6 | -4.0 | visible |
| H18 | 620 | +5.6 | -8.3 | visible |

## Iteration 7 (2026-10-11 17:41)

Changes: Final check after decoration-only anchor edits on H2 (no felt/rail/cup change)

**Result: CLEAN** (3 warnings). Walking spawn -> H18 cup: **2691 studs** (807 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- holes.json: 18 holes, total par 53; every felt and rail corner checked against the pads
- 6 teleport points checked (on flat ground, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 207.1

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 2 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112/116 | 0.00 | 4.3 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186/190 | 0.00 | 4.6 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |
|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | 2 / 7 | 36 | 0 | (66.0, 18.0, 439.5) |
| H2 | Mine-Cart Junction | 3 | 7 / 24 | 124 | 0 | (91.0, 18.0, 364.0) |
| H3 | Ranger's Riverbend | 3 | 4 / 14 | 72 | 0 | (-39.5, 18.0, 331.0) |
| H4 | Crystal Corridor | 2 | 2 / 9 | 44 | 0 | (239.0, 18.0, 334.5) |
| H5 | Echo Slot | 3 | 14 / 20 | 136 | 0 | (279.5, 22.0, 284.0) |
| H6 | Flash Flood | 3 | 7 / 18 | 100 | 0 | (276.0, 26.0, 210.0) |
| H7 | Rope Bridge Run | 4 | 5 / 18 | 92 | 0 | (343.0, 70.0, 90.0) |
| H8 | Gumdrop Gulch | 3 | 11 / 28 | 156 | 0 | (365.0, 70.0, 0.0) |
| H9 | Lollipop Windmill | 3 | 6 / 18 | 96 | 0 | (372.0, 70.0, -111.5) |
| H10 | Sluice Chute | 2 | 4 / 14 | 72 | 0 | (283.0, 112.4, -266.5) |
| H11 | Floodgate Lock | 3 | 7 / 22 | 116 | 0 | (150.0, 120.0, -295.0) |
| H12 | Intake Tower | 4 | 7 / 13 | 80 | 0 | (-142.0, 116.0, -268.0) |
| H13 | Hoodoo Maze | 3 | 7 / 21 | 112 | 0 | (-300.5, 150.0, -239.0) |
| H14 | Ore Bucket Swing | 3 | 4 / 10 | 56 | 0 | (-301.0, 150.8, -156.0) |
| H15 | Sugar Dune | 3 | 5 / 11 | 64 | 0 | (-306.0, 145.4, -58.0) |
| H16 | Sinkhole Drop | 2 | 8 / 8 | 64 | 0 | (-301.8, 186.4, 150.5) |
| H17 | Sundial | 3 | 2 / 17 | 76 | 0 | (-345.0, 190.0, 188.0) |
| H18 | Sunset Arch | 4 | 9 / 18 | 108 | 0 | (-412.0, 190.8, 172.0) |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 229 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 251 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 68 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 57 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 82 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 90 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 165 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 274 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 168 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 421 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 209 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 82 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 77 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 145 | +40.0 | 0.0% | 0 | 0.00 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h17_h18 | Rim Walk | 146 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 91 | -172.0 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (262) | ok |
|---|---|---|---|
| H1 | 0 | 98 | ok |
| H2 | 0 | 98 | ok |
| H3 | 90 | 172 | ok |
| H4 | 90 | 172 | ok |
| H5 | 0 | 98 | ok |
| H6 | 0 | 98 | ok |
| H7 | 0 | 98 | ok |
| H8 | 0 | 98 | ok |
| H9 | 90 | 172 | ok |
| H10 | 180 | 82 | ok |
| H11 | 0 | 98 | ok |
| H12 | 90 | 172 | ok |
| H13 | 180 | 82 | ok |
| H14 | 180 | 82 | ok |
| H15 | 180 | 82 | ok |
| H16 | 180 | 82 | ok |
| H17 | 0 | 98 | ok |
| H18 | 0 | 98 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.7 | +6.4 | visible |
| H2 | 540 | +6.8 | +6.5 | visible |
| H3 | 492 | +6.9 | +6.6 | visible |
| H4 | 475 | -31.3 | -34.6 | hidden (slot canyon) |
| H5 | 498 | -19.8 | -25.5 | hidden (slot canyon) |
| H6 | 434 | -16.2 | -21.8 | hidden (slot canyon) |
| H7 | 382 | +6.8 | +6.4 | visible |
| H8 | 336 | +6.9 | +6.5 | visible |
| H9 | 251 | +7.3 | +6.8 | visible |
| H10 | 270 | +6.7 | +6.0 | visible |
| H11 | 141 | +7.6 | +6.6 | visible |
| H12 | 313 | +6.5 | +6.0 | visible |
| H13 | 412 | +6.0 | +5.2 | visible |
| H14 | 386 | +6.0 | +5.3 | visible |
| H15 | 380 | +6.0 | +5.4 | visible |
| H16 | 451 | +5.6 | +2.9 | visible |
| H17 | 558 | +5.6 | -4.0 | visible |
| H18 | 620 | +5.6 | -8.3 | visible |

## Iteration 8 (2026-10-11 18:38)

Changes: p7: golden-hour game sun, separate hero sun, mine-head, solid wide dam crest and endpoint teleports

**Result: 2 FAIL** (3 warnings). Walking spawn -> H18 cup: **2691 studs** (807 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Failures:
- teleport tp_dam_crest_east: ground not flat (+-2.7 within 3 studs)
- teleport tp_dam_crest_west: ground not flat (+-2.7 within 3 studs)

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- holes.json: 18 holes, total par 53; every felt and rail corner checked against the pads
- 8 teleport points checked (on flat ground, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 207.1

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 2 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112/116 | 0.00 | 4.3 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186/190 | 0.00 | 4.6 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |
|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | 2 / 7 | 36 | 0 | (66.0, 18.0, 439.5) |
| H2 | Mine-Cart Junction | 3 | 7 / 24 | 124 | 0 | (91.0, 18.0, 364.0) |
| H3 | Ranger's Riverbend | 3 | 4 / 14 | 72 | 0 | (-39.5, 18.0, 331.0) |
| H4 | Crystal Corridor | 2 | 2 / 9 | 44 | 0 | (239.0, 18.0, 334.5) |
| H5 | Echo Slot | 3 | 14 / 20 | 136 | 0 | (279.5, 22.0, 284.0) |
| H6 | Flash Flood | 3 | 7 / 18 | 100 | 0 | (276.0, 26.0, 210.0) |
| H7 | Rope Bridge Run | 4 | 5 / 18 | 92 | 0 | (343.0, 70.0, 90.0) |
| H8 | Gumdrop Gulch | 3 | 11 / 28 | 156 | 0 | (365.0, 70.0, 0.0) |
| H9 | Lollipop Windmill | 3 | 6 / 18 | 96 | 0 | (372.0, 70.0, -111.5) |
| H10 | Sluice Chute | 2 | 4 / 14 | 72 | 0 | (283.0, 112.4, -266.5) |
| H11 | Floodgate Lock | 3 | 7 / 22 | 116 | 0 | (150.0, 120.0, -295.0) |
| H12 | Intake Tower | 4 | 7 / 13 | 80 | 0 | (-142.0, 116.0, -268.0) |
| H13 | Hoodoo Maze | 3 | 7 / 21 | 112 | 0 | (-300.5, 150.0, -239.0) |
| H14 | Ore Bucket Swing | 3 | 4 / 10 | 56 | 0 | (-301.0, 150.8, -156.0) |
| H15 | Sugar Dune | 3 | 5 / 11 | 64 | 0 | (-306.0, 145.4, -58.0) |
| H16 | Sinkhole Drop | 2 | 8 / 8 | 64 | 0 | (-301.8, 186.4, 150.5) |
| H17 | Sundial | 3 | 2 / 17 | 76 | 0 | (-345.0, 190.0, 188.0) |
| H18 | Sunset Arch | 4 | 9 / 18 | 108 | 0 | (-412.0, 190.8, 172.0) |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 229 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 251 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 68 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 57 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 82 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 90 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 165 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 274 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 168 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 421 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 209 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 82 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 77 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 145 | +40.0 | 0.0% | 0 | 0.00 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h17_h18 | Rim Walk | 146 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 91 | -172.0 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (277) | ok |
|---|---|---|---|
| H1 | 0 | 83 | ok |
| H2 | 0 | 83 | ok |
| H3 | 90 | 173 | ok |
| H4 | 90 | 173 | ok |
| H5 | 0 | 83 | ok |
| H6 | 0 | 83 | ok |
| H7 | 0 | 83 | ok |
| H8 | 0 | 83 | ok |
| H9 | 90 | 173 | ok |
| H10 | 180 | 97 | ok |
| H11 | 0 | 83 | ok |
| H12 | 90 | 173 | ok |
| H13 | 180 | 97 | ok |
| H14 | 180 | 97 | ok |
| H15 | 180 | 97 | ok |
| H16 | 180 | 97 | ok |
| H17 | 0 | 83 | ok |
| H18 | 0 | 83 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.7 | +6.4 | visible |
| H2 | 540 | +6.8 | +6.5 | visible |
| H3 | 492 | +6.9 | +6.6 | visible |
| H4 | 475 | -31.3 | -34.6 | hidden (slot canyon) |
| H5 | 498 | -19.8 | -25.5 | hidden (slot canyon) |
| H6 | 434 | -16.2 | -21.8 | hidden (slot canyon) |
| H7 | 382 | +6.8 | +6.4 | visible |
| H8 | 336 | +6.9 | +6.5 | visible |
| H9 | 251 | +7.3 | +6.8 | visible |
| H10 | 270 | +6.7 | +6.0 | visible |
| H11 | 141 | +7.6 | +6.6 | visible |
| H12 | 313 | +6.5 | +6.0 | visible |
| H13 | 412 | +6.0 | +5.2 | visible |
| H14 | 386 | +6.0 | +5.3 | visible |
| H15 | 380 | +6.0 | +5.4 | visible |
| H16 | 451 | +5.6 | +2.9 | visible |
| H17 | 558 | +5.6 | -4.0 | visible |
| H18 | 620 | +5.6 | -8.3 | visible |

## Iteration 9 (2026-10-11 18:39)

Changes: p7: crest endpoint pads on flat approach landings four studs from ends

**Result: 2 FAIL** (3 warnings). Walking spawn -> H18 cup: **2691 studs** (807 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Failures:
- teleport tp_dam_crest_east: ground not flat (+-2.1 within 3 studs)
- teleport tp_dam_crest_west: ground not flat (+-2.1 within 3 studs)

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- holes.json: 18 holes, total par 53; every felt and rail corner checked against the pads
- 8 teleport points checked (on flat ground, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 207.1

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 2 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112/116 | 0.00 | 4.3 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186/190 | 0.00 | 4.6 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |
|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | 2 / 7 | 36 | 0 | (66.0, 18.0, 439.5) |
| H2 | Mine-Cart Junction | 3 | 7 / 24 | 124 | 0 | (91.0, 18.0, 364.0) |
| H3 | Ranger's Riverbend | 3 | 4 / 14 | 72 | 0 | (-39.5, 18.0, 331.0) |
| H4 | Crystal Corridor | 2 | 2 / 9 | 44 | 0 | (239.0, 18.0, 334.5) |
| H5 | Echo Slot | 3 | 14 / 20 | 136 | 0 | (279.5, 22.0, 284.0) |
| H6 | Flash Flood | 3 | 7 / 18 | 100 | 0 | (276.0, 26.0, 210.0) |
| H7 | Rope Bridge Run | 4 | 5 / 18 | 92 | 0 | (343.0, 70.0, 90.0) |
| H8 | Gumdrop Gulch | 3 | 11 / 28 | 156 | 0 | (365.0, 70.0, 0.0) |
| H9 | Lollipop Windmill | 3 | 6 / 18 | 96 | 0 | (372.0, 70.0, -111.5) |
| H10 | Sluice Chute | 2 | 4 / 14 | 72 | 0 | (283.0, 112.4, -266.5) |
| H11 | Floodgate Lock | 3 | 7 / 22 | 116 | 0 | (150.0, 120.0, -295.0) |
| H12 | Intake Tower | 4 | 7 / 13 | 80 | 0 | (-142.0, 116.0, -268.0) |
| H13 | Hoodoo Maze | 3 | 7 / 21 | 112 | 0 | (-300.5, 150.0, -239.0) |
| H14 | Ore Bucket Swing | 3 | 4 / 10 | 56 | 0 | (-301.0, 150.8, -156.0) |
| H15 | Sugar Dune | 3 | 5 / 11 | 64 | 0 | (-306.0, 145.4, -58.0) |
| H16 | Sinkhole Drop | 2 | 8 / 8 | 64 | 0 | (-301.8, 186.4, 150.5) |
| H17 | Sundial | 3 | 2 / 17 | 76 | 0 | (-345.0, 190.0, 188.0) |
| H18 | Sunset Arch | 4 | 9 / 18 | 108 | 0 | (-412.0, 190.8, 172.0) |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 229 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 251 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 68 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 57 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 82 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 90 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 165 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 274 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 168 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 421 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 209 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 82 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 77 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 145 | +40.0 | 0.0% | 0 | 0.00 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h17_h18 | Rim Walk | 146 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 91 | -172.0 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (277) | ok |
|---|---|---|---|
| H1 | 0 | 83 | ok |
| H2 | 0 | 83 | ok |
| H3 | 90 | 173 | ok |
| H4 | 90 | 173 | ok |
| H5 | 0 | 83 | ok |
| H6 | 0 | 83 | ok |
| H7 | 0 | 83 | ok |
| H8 | 0 | 83 | ok |
| H9 | 90 | 173 | ok |
| H10 | 180 | 97 | ok |
| H11 | 0 | 83 | ok |
| H12 | 90 | 173 | ok |
| H13 | 180 | 97 | ok |
| H14 | 180 | 97 | ok |
| H15 | 180 | 97 | ok |
| H16 | 180 | 97 | ok |
| H17 | 0 | 83 | ok |
| H18 | 0 | 83 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.7 | +6.4 | visible |
| H2 | 540 | +6.8 | +6.5 | visible |
| H3 | 492 | +6.9 | +6.6 | visible |
| H4 | 475 | -31.3 | -34.6 | hidden (slot canyon) |
| H5 | 498 | -19.8 | -25.5 | hidden (slot canyon) |
| H6 | 434 | -16.2 | -21.8 | hidden (slot canyon) |
| H7 | 382 | +6.8 | +6.4 | visible |
| H8 | 336 | +6.9 | +6.5 | visible |
| H9 | 251 | +7.3 | +6.8 | visible |
| H10 | 270 | +6.7 | +6.0 | visible |
| H11 | 141 | +7.6 | +6.6 | visible |
| H12 | 313 | +6.5 | +6.0 | visible |
| H13 | 412 | +6.0 | +5.2 | visible |
| H14 | 386 | +6.0 | +5.3 | visible |
| H15 | 380 | +6.0 | +5.4 | visible |
| H16 | 451 | +5.6 | +2.9 | visible |
| H17 | 558 | +5.6 | -4.0 | visible |
| H18 | 620 | +5.6 | -8.3 | visible |

## Iteration 10 (2026-10-11 18:39)

Changes: p7: explicit collidable endpoint landings support flat 3-stud teleport standing rings

**Result: CLEAN** (3 warnings). Walking spawn -> H18 cup: **2691 studs** (807 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- holes.json: 18 holes, total par 53; every felt and rail corner checked against the pads
- 8 teleport points checked (on flat ground or verified collidable landing, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 207.1

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 2 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112/116 | 0.00 | 4.3 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186/190 | 0.00 | 4.6 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |
|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | 2 / 7 | 36 | 0 | (66.0, 18.0, 439.5) |
| H2 | Mine-Cart Junction | 3 | 7 / 24 | 124 | 0 | (91.0, 18.0, 364.0) |
| H3 | Ranger's Riverbend | 3 | 4 / 14 | 72 | 0 | (-39.5, 18.0, 331.0) |
| H4 | Crystal Corridor | 2 | 2 / 9 | 44 | 0 | (239.0, 18.0, 334.5) |
| H5 | Echo Slot | 3 | 14 / 20 | 136 | 0 | (279.5, 22.0, 284.0) |
| H6 | Flash Flood | 3 | 7 / 18 | 100 | 0 | (276.0, 26.0, 210.0) |
| H7 | Rope Bridge Run | 4 | 5 / 18 | 92 | 0 | (343.0, 70.0, 90.0) |
| H8 | Gumdrop Gulch | 3 | 11 / 28 | 156 | 0 | (365.0, 70.0, 0.0) |
| H9 | Lollipop Windmill | 3 | 6 / 18 | 96 | 0 | (372.0, 70.0, -111.5) |
| H10 | Sluice Chute | 2 | 4 / 14 | 72 | 0 | (283.0, 112.4, -266.5) |
| H11 | Floodgate Lock | 3 | 7 / 22 | 116 | 0 | (150.0, 120.0, -295.0) |
| H12 | Intake Tower | 4 | 7 / 13 | 80 | 0 | (-142.0, 116.0, -268.0) |
| H13 | Hoodoo Maze | 3 | 7 / 21 | 112 | 0 | (-300.5, 150.0, -239.0) |
| H14 | Ore Bucket Swing | 3 | 4 / 10 | 56 | 0 | (-301.0, 150.8, -156.0) |
| H15 | Sugar Dune | 3 | 5 / 11 | 64 | 0 | (-306.0, 145.4, -58.0) |
| H16 | Sinkhole Drop | 2 | 8 / 8 | 64 | 0 | (-301.8, 186.4, 150.5) |
| H17 | Sundial | 3 | 2 / 17 | 76 | 0 | (-345.0, 190.0, 188.0) |
| H18 | Sunset Arch | 4 | 9 / 18 | 108 | 0 | (-412.0, 190.8, 172.0) |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 229 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 251 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 68 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 57 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 82 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 90 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 165 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 274 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 168 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 421 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 209 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 82 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 77 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 145 | +40.0 | 0.0% | 0 | 0.00 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h17_h18 | Rim Walk | 146 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 91 | -172.0 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (277) | ok |
|---|---|---|---|
| H1 | 0 | 83 | ok |
| H2 | 0 | 83 | ok |
| H3 | 90 | 173 | ok |
| H4 | 90 | 173 | ok |
| H5 | 0 | 83 | ok |
| H6 | 0 | 83 | ok |
| H7 | 0 | 83 | ok |
| H8 | 0 | 83 | ok |
| H9 | 90 | 173 | ok |
| H10 | 180 | 97 | ok |
| H11 | 0 | 83 | ok |
| H12 | 90 | 173 | ok |
| H13 | 180 | 97 | ok |
| H14 | 180 | 97 | ok |
| H15 | 180 | 97 | ok |
| H16 | 180 | 97 | ok |
| H17 | 0 | 83 | ok |
| H18 | 0 | 83 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.7 | +6.4 | visible |
| H2 | 540 | +6.8 | +6.5 | visible |
| H3 | 492 | +6.9 | +6.6 | visible |
| H4 | 475 | -31.3 | -34.6 | hidden (slot canyon) |
| H5 | 498 | -19.8 | -25.5 | hidden (slot canyon) |
| H6 | 434 | -16.2 | -21.8 | hidden (slot canyon) |
| H7 | 382 | +6.8 | +6.4 | visible |
| H8 | 336 | +6.9 | +6.5 | visible |
| H9 | 251 | +7.3 | +6.8 | visible |
| H10 | 270 | +6.7 | +6.0 | visible |
| H11 | 141 | +7.6 | +6.6 | visible |
| H12 | 313 | +6.5 | +6.0 | visible |
| H13 | 412 | +6.0 | +5.2 | visible |
| H14 | 386 | +6.0 | +5.3 | visible |
| H15 | 380 | +6.0 | +5.4 | visible |
| H16 | 451 | +5.6 | +2.9 | visible |
| H17 | 558 | +5.6 | -4.0 | visible |
| H18 | 620 | +5.6 | -8.3 | visible |

## Iteration 11 (2026-10-11 19:10)

Changes: p7 final: corrected XYZ cup exits, deduplicated landmarks, exact Addendum5 superellipse dome, VR crest and game/hero suns

**Result: 2 FAIL** (3 warnings). Walking spawn -> H18 cup: **2700 studs** (810 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Failures:
- H17: Old Sugarloaf not visible from the tee ({'summit': -9.983153337097548, 'upper dome': -10.919861090130922})
- H18: Old Sugarloaf not visible from the tee ({'summit': -16.763691223205058, 'upper dome': -17.958416254179667})

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- holes.json: 18 holes, total par 54; every felt and rail corner checked against the pads
- 8 teleport points checked (on flat ground or verified collidable landing, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 128.0

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 3 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112.4/116 | 0.00 | 3.9 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186.4/190 | 0.00 | 4.2 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |
|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | 2 / 7 | 36 | 0 | (66.0, 18.0, 439.5) |
| H2 | Mine-Cart Junction | 3 | 7 / 24 | 124 | 0 | (89.0, 18.0, 364.0) |
| H3 | Ranger's Riverbend | 3 | 4 / 14 | 72 | 0 | (-39.5, 18.0, 331.0) |
| H4 | Crystal Corridor | 3 | 2 / 9 | 44 | 0 | (239.0, 18.0, 334.5) |
| H5 | Echo Slot | 3 | 14 / 20 | 136 | 0 | (279.5, 22.0, 284.0) |
| H6 | Flash Flood | 3 | 8 / 30 | 152 | 0 | (276.0, 26.0, 210.0) |
| H7 | Rope Bridge Run | 4 | 5 / 18 | 92 | 0 | (343.0, 70.0, 90.0) |
| H8 | Gumdrop Gulch | 3 | 11 / 28 | 156 | 0 | (365.0, 70.0, 0.0) |
| H9 | Lollipop Windmill | 3 | 6 / 18 | 96 | 0 | (372.0, 70.0, -111.5) |
| H10 | Sluice Chute | 2 | 4 / 14 | 72 | 0 | (283.0, 112.4, -266.5) |
| H11 | Floodgate Lock | 3 | 21 / 51 | 288 | 0 | (150.0, 120.0, -295.0) |
| H12 | Intake Tower | 4 | 7 / 13 | 80 | 0 | (-142.0, 116.0, -268.0) |
| H13 | Hoodoo Maze | 3 | 7 / 21 | 112 | 0 | (-300.5, 150.0, -239.0) |
| H14 | Ore Bucket Swing | 3 | 4 / 10 | 56 | 0 | (-301.0, 150.8, -156.0) |
| H15 | Sugar Dune | 3 | 5 / 11 | 64 | 0 | (-306.0, 145.4, -58.0) |
| H16 | Sinkhole Drop | 2 | 8 / 8 | 64 | 0 | (-301.8, 186.4, 150.5) |
| H17 | Sundial | 3 | 2 / 56 | 232 | 0 | (-334.9, 190.0, 189.0) |
| H18 | Sunset Arch | 4 | 9 / 18 | 108 | 0 | (-412.0, 190.8, 172.0) |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 227 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 251 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 68 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 57 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 82 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 90 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 165 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 274 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 168 | +3.6 | 0.0% | 5 | 0.72 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 421 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 209 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 82 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 77 | -0.8 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 146 | +44.6 | 0.0% | 6 | 0.77 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +3.6 | 0.0% | 5 | 0.72 | 0 | - |
| p_h17_h18 | Rim Walk | 156 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 91 | -172.8 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (277) | ok |
|---|---|---|---|
| H1 | 0 | 83 | ok |
| H2 | 0 | 83 | ok |
| H3 | 90 | 173 | ok |
| H4 | 90 | 173 | ok |
| H5 | 0 | 83 | ok |
| H6 | 0 | 83 | ok |
| H7 | 0 | 83 | ok |
| H8 | 0 | 83 | ok |
| H9 | 90 | 173 | ok |
| H10 | 180 | 97 | ok |
| H11 | 0 | 83 | ok |
| H12 | 90 | 173 | ok |
| H13 | 180 | 97 | ok |
| H14 | 180 | 97 | ok |
| H15 | 180 | 97 | ok |
| H16 | 180 | 97 | ok |
| H17 | 0 | 83 | ok |
| H18 | 0 | 83 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.2 | +6.2 | visible |
| H2 | 540 | +6.3 | +6.3 | visible |
| H3 | 492 | +6.3 | +6.4 | visible |
| H4 | 475 | -35.9 | -35.2 | hidden (slot canyon) |
| H5 | 498 | -29.8 | -29.3 | hidden (slot canyon) |
| H6 | 434 | -26.2 | -25.6 | hidden (slot canyon) |
| H7 | 382 | +6.0 | +6.1 | visible |
| H8 | 336 | +6.1 | +6.1 | visible |
| H9 | 251 | +6.3 | +6.4 | visible |
| H10 | 270 | +5.6 | +5.6 | visible |
| H11 | 141 | +5.7 | +5.7 | visible |
| H12 | 313 | +5.6 | +5.6 | visible |
| H13 | 412 | +1.0 | +0.5 | visible |
| H14 | 386 | +1.2 | +0.8 | visible |
| H15 | 380 | +1.6 | +1.2 | visible |
| H16 | 451 | +1.3 | +1.0 | visible |
| H17 | 558 | -10.0 | -10.9 | BLOCKED |
| H18 | 620 | -16.8 | -18.0 | BLOCKED |

## Iteration 12 (2026-10-11 19:24)

Changes: p7 final: exact Addendum 5 dome and all cup XYZ/route descriptions synchronized; two protected Crown sightlines remain blocked

**Result: 2 FAIL** (3 warnings). Walking spawn -> H18 cup: **2700 studs** (810 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Failures:
- H17: Old Sugarloaf not visible from the tee ({'summit': -9.983153337097548, 'upper dome': -10.919861090130922})
- H18: Old Sugarloaf not visible from the tee ({'summit': -16.763691223205058, 'upper dome': -17.958416254179667})

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- holes.json: 18 holes, total par 54; every felt and rail corner checked against the pads
- 8 teleport points checked (on flat ground or verified collidable landing, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 128.0

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 3 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112.4/116 | 0.00 | 3.9 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186.4/190 | 0.00 | 4.2 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |
|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | 2 / 7 | 36 | 0 | (66.0, 18.0, 439.5) |
| H2 | Mine-Cart Junction | 3 | 7 / 24 | 124 | 0 | (89.0, 18.0, 364.0) |
| H3 | Ranger's Riverbend | 3 | 4 / 14 | 72 | 0 | (-39.5, 18.0, 331.0) |
| H4 | Crystal Corridor | 3 | 2 / 9 | 44 | 0 | (239.0, 18.0, 334.5) |
| H5 | Echo Slot | 3 | 14 / 20 | 136 | 0 | (279.5, 22.0, 284.0) |
| H6 | Flash Flood | 3 | 8 / 30 | 152 | 0 | (276.0, 26.0, 210.0) |
| H7 | Rope Bridge Run | 4 | 5 / 18 | 92 | 0 | (343.0, 70.0, 90.0) |
| H8 | Gumdrop Gulch | 3 | 11 / 28 | 156 | 0 | (365.0, 70.0, 0.0) |
| H9 | Lollipop Windmill | 3 | 6 / 18 | 96 | 0 | (372.0, 70.0, -111.5) |
| H10 | Sluice Chute | 2 | 4 / 14 | 72 | 0 | (283.0, 112.4, -266.5) |
| H11 | Floodgate Lock | 3 | 21 / 51 | 288 | 0 | (150.0, 120.0, -295.0) |
| H12 | Intake Tower | 4 | 7 / 13 | 80 | 0 | (-142.0, 116.0, -268.0) |
| H13 | Hoodoo Maze | 3 | 7 / 21 | 112 | 0 | (-300.5, 150.0, -239.0) |
| H14 | Ore Bucket Swing | 3 | 4 / 10 | 56 | 0 | (-301.0, 150.8, -156.0) |
| H15 | Sugar Dune | 3 | 5 / 11 | 64 | 0 | (-306.0, 145.4, -58.0) |
| H16 | Sinkhole Drop | 2 | 8 / 8 | 64 | 0 | (-301.8, 186.4, 150.5) |
| H17 | Sundial | 3 | 2 / 56 | 232 | 0 | (-334.9, 190.0, 189.0) |
| H18 | Sunset Arch | 4 | 9 / 18 | 108 | 0 | (-412.0, 190.8, 172.0) |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 227 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 251 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 68 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 57 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 82 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 90 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 165 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 274 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 168 | +3.6 | 0.0% | 5 | 0.72 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 421 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 209 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 82 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 77 | -0.8 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 146 | +44.6 | 0.0% | 6 | 0.77 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +3.6 | 0.0% | 5 | 0.72 | 0 | - |
| p_h17_h18 | Rim Walk | 156 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 91 | -172.8 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (277) | ok |
|---|---|---|---|
| H1 | 0 | 83 | ok |
| H2 | 0 | 83 | ok |
| H3 | 90 | 173 | ok |
| H4 | 90 | 173 | ok |
| H5 | 0 | 83 | ok |
| H6 | 0 | 83 | ok |
| H7 | 0 | 83 | ok |
| H8 | 0 | 83 | ok |
| H9 | 90 | 173 | ok |
| H10 | 180 | 97 | ok |
| H11 | 0 | 83 | ok |
| H12 | 90 | 173 | ok |
| H13 | 180 | 97 | ok |
| H14 | 180 | 97 | ok |
| H15 | 180 | 97 | ok |
| H16 | 180 | 97 | ok |
| H17 | 0 | 83 | ok |
| H18 | 0 | 83 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.2 | +6.2 | visible |
| H2 | 540 | +6.3 | +6.3 | visible |
| H3 | 492 | +6.3 | +6.4 | visible |
| H4 | 475 | -35.9 | -35.2 | hidden (slot canyon) |
| H5 | 498 | -29.8 | -29.3 | hidden (slot canyon) |
| H6 | 434 | -26.2 | -25.6 | hidden (slot canyon) |
| H7 | 382 | +6.0 | +6.1 | visible |
| H8 | 336 | +6.1 | +6.1 | visible |
| H9 | 251 | +6.3 | +6.4 | visible |
| H10 | 270 | +5.6 | +5.6 | visible |
| H11 | 141 | +5.7 | +5.7 | visible |
| H12 | 313 | +5.6 | +5.6 | visible |
| H13 | 412 | +1.0 | +0.5 | visible |
| H14 | 386 | +1.2 | +0.8 | visible |
| H15 | 380 | +1.6 | +1.2 | visible |
| H16 | 451 | +1.3 | +1.0 | visible |
| H17 | 558 | -10.0 | -10.9 | BLOCKED |
| H18 | 620 | -16.8 | -18.0 | BLOCKED |

## Iteration 13 (2026-10-11 19:57)

Changes: Round p8: remove Old Sugarloaf visibility requirement for H17/H18 tees only; retain measured LOS, all other visibility checks, and unchanged Addendum 5 dome.

**Result: CLEAN** (3 warnings). Walking spawn -> H18 cup: **2700 studs** (810 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- holes.json: 18 holes, total par 54; every felt and rail corner checked against the pads
- p8: H17/H18 tees are exempt from Old Sugarloaf visibility; measured sightlines remain reported, dome unchanged
- 8 teleport points checked (on flat ground or verified collidable landing, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 128.0

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 3 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112.4/116 | 0.00 | 3.9 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186.4/190 | 0.00 | 4.2 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |
|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | 2 / 7 | 36 | 0 | (66.0, 18.0, 439.5) |
| H2 | Mine-Cart Junction | 3 | 7 / 24 | 124 | 0 | (89.0, 18.0, 364.0) |
| H3 | Ranger's Riverbend | 3 | 4 / 14 | 72 | 0 | (-39.5, 18.0, 331.0) |
| H4 | Crystal Corridor | 3 | 2 / 9 | 44 | 0 | (239.0, 18.0, 334.5) |
| H5 | Echo Slot | 3 | 14 / 20 | 136 | 0 | (279.5, 22.0, 284.0) |
| H6 | Flash Flood | 3 | 8 / 30 | 152 | 0 | (276.0, 26.0, 210.0) |
| H7 | Rope Bridge Run | 4 | 5 / 18 | 92 | 0 | (343.0, 70.0, 90.0) |
| H8 | Gumdrop Gulch | 3 | 11 / 28 | 156 | 0 | (365.0, 70.0, 0.0) |
| H9 | Lollipop Windmill | 3 | 6 / 18 | 96 | 0 | (372.0, 70.0, -111.5) |
| H10 | Sluice Chute | 2 | 4 / 14 | 72 | 0 | (283.0, 112.4, -266.5) |
| H11 | Floodgate Lock | 3 | 21 / 51 | 288 | 0 | (150.0, 120.0, -295.0) |
| H12 | Intake Tower | 4 | 7 / 13 | 80 | 0 | (-142.0, 116.0, -268.0) |
| H13 | Hoodoo Maze | 3 | 7 / 21 | 112 | 0 | (-300.5, 150.0, -239.0) |
| H14 | Ore Bucket Swing | 3 | 4 / 10 | 56 | 0 | (-301.0, 150.8, -156.0) |
| H15 | Sugar Dune | 3 | 5 / 11 | 64 | 0 | (-306.0, 145.4, -58.0) |
| H16 | Sinkhole Drop | 2 | 8 / 8 | 64 | 0 | (-301.8, 186.4, 150.5) |
| H17 | Sundial | 3 | 2 / 56 | 232 | 0 | (-334.9, 190.0, 189.0) |
| H18 | Sunset Arch | 4 | 9 / 18 | 108 | 0 | (-412.0, 190.8, 172.0) |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 227 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 251 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 68 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 57 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 82 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 90 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 165 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 274 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 168 | +3.6 | 0.0% | 5 | 0.72 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 421 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 209 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 82 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 77 | -0.8 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 146 | +44.6 | 0.0% | 6 | 0.77 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +3.6 | 0.0% | 5 | 0.72 | 0 | - |
| p_h17_h18 | Rim Walk | 156 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 91 | -172.8 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (277) | ok |
|---|---|---|---|
| H1 | 0 | 83 | ok |
| H2 | 0 | 83 | ok |
| H3 | 90 | 173 | ok |
| H4 | 90 | 173 | ok |
| H5 | 0 | 83 | ok |
| H6 | 0 | 83 | ok |
| H7 | 0 | 83 | ok |
| H8 | 0 | 83 | ok |
| H9 | 90 | 173 | ok |
| H10 | 180 | 97 | ok |
| H11 | 0 | 83 | ok |
| H12 | 90 | 173 | ok |
| H13 | 180 | 97 | ok |
| H14 | 180 | 97 | ok |
| H15 | 180 | 97 | ok |
| H16 | 180 | 97 | ok |
| H17 | 0 | 83 | ok |
| H18 | 0 | 83 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.2 | +6.2 | visible |
| H2 | 540 | +6.3 | +6.3 | visible |
| H3 | 492 | +6.3 | +6.4 | visible |
| H4 | 475 | -35.9 | -35.2 | hidden (slot canyon) |
| H5 | 498 | -29.8 | -29.3 | hidden (slot canyon) |
| H6 | 434 | -26.2 | -25.6 | hidden (slot canyon) |
| H7 | 382 | +6.0 | +6.1 | visible |
| H8 | 336 | +6.1 | +6.1 | visible |
| H9 | 251 | +6.3 | +6.4 | visible |
| H10 | 270 | +5.6 | +5.6 | visible |
| H11 | 141 | +5.7 | +5.7 | visible |
| H12 | 313 | +5.6 | +5.6 | visible |
| H13 | 412 | +1.0 | +0.5 | visible |
| H14 | 386 | +1.2 | +0.8 | visible |
| H15 | 380 | +1.6 | +1.2 | visible |
| H16 | 451 | +1.3 | +1.0 | visible |
| H17 | 558 | -10.0 | -10.9 | hidden (p8 visibility exemption) |
| H18 | 620 | -16.8 | -18.0 | hidden (p8 visibility exemption) |

## Iteration 14 (2026-10-11 20:02)

Changes: Round p8 final: H11 approach widened and quay side pockets expanded; H17/H18 Old Sugarloaf tee visibility exemptions retained, dome unchanged.

**Result: CLEAN** (3 warnings). Walking spawn -> H18 cup: **2700 studs** (810 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- holes.json: 18 holes, total par 54; every felt and rail corner checked against the pads
- p8: H17/H18 tees are exempt from Old Sugarloaf visibility; measured sightlines remain reported, dome unchanged
- 8 teleport points checked (on flat ground or verified collidable landing, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 128.0

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 3 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112.4/116 | 0.00 | 3.9 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186.4/190 | 0.00 | 4.2 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |
|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | 2 / 7 | 36 | 0 | (66.0, 18.0, 439.5) |
| H2 | Mine-Cart Junction | 3 | 7 / 24 | 124 | 0 | (89.0, 18.0, 364.0) |
| H3 | Ranger's Riverbend | 3 | 4 / 14 | 72 | 0 | (-39.5, 18.0, 331.0) |
| H4 | Crystal Corridor | 3 | 2 / 9 | 44 | 0 | (239.0, 18.0, 334.5) |
| H5 | Echo Slot | 3 | 14 / 20 | 136 | 0 | (279.5, 22.0, 284.0) |
| H6 | Flash Flood | 3 | 8 / 30 | 152 | 0 | (276.0, 26.0, 210.0) |
| H7 | Rope Bridge Run | 4 | 5 / 18 | 92 | 0 | (343.0, 70.0, 90.0) |
| H8 | Gumdrop Gulch | 3 | 11 / 28 | 156 | 0 | (365.0, 70.0, 0.0) |
| H9 | Lollipop Windmill | 3 | 6 / 18 | 96 | 0 | (372.0, 70.0, -111.5) |
| H10 | Sluice Chute | 2 | 4 / 14 | 72 | 0 | (283.0, 112.4, -266.5) |
| H11 | Floodgate Lock | 3 | 21 / 51 | 288 | 0 | (150.0, 120.0, -295.0) |
| H12 | Intake Tower | 4 | 7 / 13 | 80 | 0 | (-142.0, 116.0, -268.0) |
| H13 | Hoodoo Maze | 3 | 7 / 21 | 112 | 0 | (-300.5, 150.0, -239.0) |
| H14 | Ore Bucket Swing | 3 | 4 / 10 | 56 | 0 | (-301.0, 150.8, -156.0) |
| H15 | Sugar Dune | 3 | 5 / 11 | 64 | 0 | (-306.0, 145.4, -58.0) |
| H16 | Sinkhole Drop | 2 | 8 / 8 | 64 | 0 | (-301.8, 186.4, 150.5) |
| H17 | Sundial | 3 | 2 / 56 | 232 | 0 | (-334.9, 190.0, 189.0) |
| H18 | Sunset Arch | 4 | 9 / 18 | 108 | 0 | (-412.0, 190.8, 172.0) |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 227 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 251 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 68 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 57 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 82 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 90 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 165 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 274 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 168 | +3.6 | 0.0% | 5 | 0.72 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 421 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 209 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 82 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 77 | -0.8 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 146 | +44.6 | 0.0% | 6 | 0.77 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +3.6 | 0.0% | 5 | 0.72 | 0 | - |
| p_h17_h18 | Rim Walk | 156 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 91 | -172.8 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (277) | ok |
|---|---|---|---|
| H1 | 0 | 83 | ok |
| H2 | 0 | 83 | ok |
| H3 | 90 | 173 | ok |
| H4 | 90 | 173 | ok |
| H5 | 0 | 83 | ok |
| H6 | 0 | 83 | ok |
| H7 | 0 | 83 | ok |
| H8 | 0 | 83 | ok |
| H9 | 90 | 173 | ok |
| H10 | 180 | 97 | ok |
| H11 | 0 | 83 | ok |
| H12 | 90 | 173 | ok |
| H13 | 180 | 97 | ok |
| H14 | 180 | 97 | ok |
| H15 | 180 | 97 | ok |
| H16 | 180 | 97 | ok |
| H17 | 0 | 83 | ok |
| H18 | 0 | 83 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.2 | +6.2 | visible |
| H2 | 540 | +6.3 | +6.3 | visible |
| H3 | 492 | +6.3 | +6.4 | visible |
| H4 | 475 | -35.9 | -35.2 | hidden (slot canyon) |
| H5 | 498 | -29.8 | -29.3 | hidden (slot canyon) |
| H6 | 434 | -26.2 | -25.6 | hidden (slot canyon) |
| H7 | 382 | +6.0 | +6.1 | visible |
| H8 | 336 | +6.1 | +6.1 | visible |
| H9 | 251 | +6.3 | +6.4 | visible |
| H10 | 270 | +5.6 | +5.6 | visible |
| H11 | 141 | +5.7 | +5.7 | visible |
| H12 | 313 | +5.6 | +5.6 | visible |
| H13 | 412 | +1.0 | +0.5 | visible |
| H14 | 386 | +1.2 | +0.8 | visible |
| H15 | 380 | +1.6 | +1.2 | visible |
| H16 | 451 | +1.3 | +1.0 | visible |
| H17 | 558 | -10.0 | -10.9 | hidden (p8 visibility exemption) |
| H18 | 620 | -16.8 | -18.0 | hidden (p8 visibility exemption) |

## Iteration 15 (2026-10-12 19:12)

Changes: H8 crease floors: h8_flat 0.5, h8_seg 4.0->3.8125 (rest-time fix)

**Result: CLEAN** (3 warnings). Walking spawn -> H18 cup: **2700 studs** (810 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- holes.json: 18 holes, total par 54; every felt and rail corner checked against the pads
- p8: H17/H18 tees are exempt from Old Sugarloaf visibility; measured sightlines remain reported, dome unchanged
- 8 teleport points checked (on flat ground or verified collidable landing, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 128.0

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 3 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112.4/116 | 0.00 | 3.9 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186.4/190 | 0.00 | 4.2 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |
|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | 2 / 7 | 36 | 0 | (66.0, 18.0, 439.5) |
| H2 | Mine-Cart Junction | 3 | 7 / 24 | 124 | 0 | (89.0, 18.0, 364.0) |
| H3 | Ranger's Riverbend | 3 | 4 / 14 | 72 | 0 | (-39.5, 18.0, 331.0) |
| H4 | Crystal Corridor | 3 | 2 / 9 | 44 | 0 | (239.0, 18.0, 334.5) |
| H5 | Echo Slot | 3 | 14 / 20 | 136 | 0 | (279.5, 22.0, 284.0) |
| H6 | Flash Flood | 3 | 8 / 30 | 152 | 0 | (276.0, 26.0, 210.0) |
| H7 | Rope Bridge Run | 4 | 5 / 18 | 92 | 0 | (343.0, 70.0, 90.0) |
| H8 | Gumdrop Gulch | 3 | 14 / 34 | 192 | 0 | (365.0, 70.0, 0.0) |
| H9 | Lollipop Windmill | 3 | 6 / 18 | 96 | 0 | (372.0, 70.0, -111.5) |
| H10 | Sluice Chute | 2 | 4 / 14 | 72 | 0 | (283.0, 112.4, -266.5) |
| H11 | Floodgate Lock | 3 | 21 / 51 | 288 | 0 | (150.0, 120.0, -295.0) |
| H12 | Intake Tower | 4 | 7 / 13 | 80 | 0 | (-142.0, 116.0, -268.0) |
| H13 | Hoodoo Maze | 3 | 7 / 21 | 112 | 0 | (-300.5, 150.0, -239.0) |
| H14 | Ore Bucket Swing | 3 | 4 / 10 | 56 | 0 | (-301.0, 150.8, -156.0) |
| H15 | Sugar Dune | 3 | 5 / 11 | 64 | 0 | (-306.0, 145.4, -58.0) |
| H16 | Sinkhole Drop | 2 | 8 / 8 | 64 | 0 | (-301.8, 186.4, 150.5) |
| H17 | Sundial | 3 | 2 / 59 | 244 | 0 | (-334.9, 190.0, 189.0) |
| H18 | Sunset Arch | 4 | 9 / 18 | 108 | 0 | (-412.0, 190.8, 172.0) |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 227 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 251 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 68 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 57 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 82 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 90 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 165 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 274 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 168 | +3.6 | 0.0% | 5 | 0.72 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 421 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 209 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 82 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 77 | -0.8 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 146 | +44.6 | 0.0% | 6 | 0.77 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +3.6 | 0.0% | 5 | 0.72 | 0 | - |
| p_h17_h18 | Rim Walk | 156 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 91 | -172.8 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (277) | ok |
|---|---|---|---|
| H1 | 0 | 83 | ok |
| H2 | 0 | 83 | ok |
| H3 | 90 | 173 | ok |
| H4 | 90 | 173 | ok |
| H5 | 0 | 83 | ok |
| H6 | 0 | 83 | ok |
| H7 | 0 | 83 | ok |
| H8 | 0 | 83 | ok |
| H9 | 90 | 173 | ok |
| H10 | 180 | 97 | ok |
| H11 | 0 | 83 | ok |
| H12 | 90 | 173 | ok |
| H13 | 180 | 97 | ok |
| H14 | 180 | 97 | ok |
| H15 | 180 | 97 | ok |
| H16 | 180 | 97 | ok |
| H17 | 0 | 83 | ok |
| H18 | 0 | 83 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.2 | +6.2 | visible |
| H2 | 540 | +6.3 | +6.3 | visible |
| H3 | 492 | +6.3 | +6.4 | visible |
| H4 | 475 | -35.9 | -35.2 | hidden (slot canyon) |
| H5 | 498 | -29.8 | -29.3 | hidden (slot canyon) |
| H6 | 434 | -26.2 | -25.6 | hidden (slot canyon) |
| H7 | 382 | +6.0 | +6.1 | visible |
| H8 | 336 | +6.1 | +6.1 | visible |
| H9 | 251 | +6.3 | +6.4 | visible |
| H10 | 270 | +5.6 | +5.6 | visible |
| H11 | 141 | +5.7 | +5.7 | visible |
| H12 | 313 | +5.6 | +5.6 | visible |
| H13 | 412 | +1.0 | +0.5 | visible |
| H14 | 386 | +1.2 | +0.8 | visible |
| H15 | 380 | +1.6 | +1.2 | visible |
| H16 | 451 | +1.3 | +1.0 | visible |
| H17 | 558 | -10.0 | -10.9 | hidden (p8 visibility exemption) |
| H18 | 620 | -16.8 | -18.0 | hidden (p8 visibility exemption) |

## Iteration 16 (2026-10-12 19:12)

Changes: H8 crease floors check

**Result: CLEAN** (3 warnings). Walking spawn -> H18 cup: **2700 studs** (810 m, target < 3000); lifts 4 (ride 868 studs incl. the gondola home).

Warnings:
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Checks:
- closest hole pairs: H5-H6 7.0, H7-H8 17.0, H1-H2 22.8, H14-H15 25.0, H4-H5 26.0
- holes.json: 18 holes, total par 54; every felt and rail corner checked against the pads
- p8: H17/H18 tees are exempt from Old Sugarloaf visibility; measured sightlines remain reported, dome unchanged
- 8 teleport points checked (on flat ground or verified collidable landing, <= 14 from a walkway, clear of holes)
- 122 small scenery pieces clear of every footprint
- reservoir rim min 109.5 (10 ring points are the Fizzwater Creek mouth) (water 108.0); held by the dam over x -44..44
- Old Sugarloaf summit y 128.0

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H2 | Mine-Cart Junction | 3 | Sugarloaf Junction | 18 | 0.00 | 0.7 | - |
| H3 | Ranger's Riverbend | 3 | Sugarloaf Junction | 18 | 0.00 | 0.5 | Sugarloaf River: ground 6.1 below the pad |
| H4 | Crystal Corridor | 3 | Rock Candy Narrows | 18 | 0.00 | 0.6 | - |
| H5 | Echo Slot | 3 | Rock Candy Narrows | 22 | 0.00 | 1.1 | - |
| H6 | Flash Flood | 3 | Rock Candy Narrows | 26 | 0.00 | 1.5 | - |
| H7 | Rope Bridge Run | 4 | Taffy Mesa | 70 | 0.00 | 5.8 | Taffy Gap: ground 30.3 below the pad |
| H8 | Gumdrop Gulch | 3 | Taffy Mesa | 70 | 0.00 | 0.5 | - |
| H9 | Lollipop Windmill | 3 | Taffy Mesa | 70 | 0.00 | 0.6 | - |
| H10 | Sluice Chute | 2 | Sugarloaf Dam | 112.4/116 | 0.00 | 3.9 | - |
| H11 | Floodgate Lock | 3 | Sugarloaf Dam | 116/120 | 0.00 | 3.9 | - |
| H12 | Intake Tower | 4 | Sugarloaf Dam | 116 | 0.00 | 0.5 | - |
| H13 | Hoodoo Maze | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H14 | Ore Bucket Swing | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H15 | Sugar Dune | 3 | Hoodoo Garden | 150 | 0.00 | 0.6 | - |
| H16 | Sinkhole Drop | 2 | Sugarloaf Crown | 186.4/190 | 0.00 | 4.2 | - |
| H17 | Sundial | 3 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |
| H18 | Sunset Arch | 4 | Sugarloaf Crown | 190 | 0.00 | 0.6 | - |

| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |
|---|---|---|---|---|---|---|
| H1 | Trailhead Gate | 2 | 2 / 7 | 36 | 0 | (66.0, 18.0, 439.5) |
| H2 | Mine-Cart Junction | 3 | 7 / 24 | 124 | 0 | (89.0, 18.0, 364.0) |
| H3 | Ranger's Riverbend | 3 | 4 / 14 | 72 | 0 | (-39.5, 18.0, 331.0) |
| H4 | Crystal Corridor | 3 | 2 / 9 | 44 | 0 | (239.0, 18.0, 334.5) |
| H5 | Echo Slot | 3 | 14 / 20 | 136 | 0 | (279.5, 22.0, 284.0) |
| H6 | Flash Flood | 3 | 8 / 30 | 152 | 0 | (276.0, 26.0, 210.0) |
| H7 | Rope Bridge Run | 4 | 5 / 18 | 92 | 0 | (343.0, 70.0, 90.0) |
| H8 | Gumdrop Gulch | 3 | 14 / 34 | 192 | 0 | (365.0, 70.0, 0.0) |
| H9 | Lollipop Windmill | 3 | 6 / 18 | 96 | 0 | (372.0, 70.0, -111.5) |
| H10 | Sluice Chute | 2 | 4 / 14 | 72 | 0 | (283.0, 112.4, -266.5) |
| H11 | Floodgate Lock | 3 | 21 / 51 | 288 | 0 | (150.0, 120.0, -295.0) |
| H12 | Intake Tower | 4 | 7 / 13 | 80 | 0 | (-142.0, 116.0, -268.0) |
| H13 | Hoodoo Maze | 3 | 7 / 21 | 112 | 0 | (-300.5, 150.0, -239.0) |
| H14 | Ore Bucket Swing | 3 | 4 / 10 | 56 | 0 | (-301.0, 150.8, -156.0) |
| H15 | Sugar Dune | 3 | 5 / 11 | 64 | 0 | (-306.0, 145.4, -58.0) |
| H16 | Sinkhole Drop | 2 | 8 / 8 | 64 | 0 | (-301.8, 186.4, 150.5) |
| H17 | Sundial | 3 | 2 / 59 | 244 | 0 | (-334.9, 190.0, 189.0) |
| H18 | Sunset Arch | 4 | 9 / 18 | 108 | 0 | (-412.0, 190.8, 172.0) |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Junction Walk | 40 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Boardwalk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Ranger Footbridge | 227 | +0.0 | 0.0% | 0 | 0.00 | 1 | Ranger Footbridge 54 long, 6 above ground |
| p_h3_h4 | Narrows Trail | 251 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h4_h5 | Geode Steps | 68 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h5_h6 | Slot Steps | 57 | +4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Rock Candy Lift | 82 | +44.0 | 0.0% | 0 | 0.00 | 0 | Rock Candy Lift +44 |
| p_h7_h8 | Gap Rim Trail | 90 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Licorice Rope Bridge | 165 | +0.0 | 0.0% | 0 | 0.00 | 1 | Licorice Rope Bridge 54 long, 26 above ground |
| p_h9_h10 | Taffy Cliff Lift | 274 | +46.0 | 0.0% | 0 | 0.00 | 0 | Taffy Cliff Lift +46 |
| p_h10_h11 | Bench Rim Walk | 168 | +3.6 | 0.0% | 5 | 0.72 | 0 | - |
| p_h11_h12 | Dam Crest Walk | 421 | -4.0 | 0.0% | 5 | 0.80 | 3 | Peppermint Dam crest 92 long, 102 above ground |
| p_h12_h13 | Gumdrop Lift | 209 | +34.0 | 0.0% | 0 | 0.00 | 0 | Gumdrop Lift +34 |
| p_h13_h14 | Hoodoo Lane | 82 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Cableway Walk | 77 | -0.8 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crown Lift | 146 | +44.6 | 0.0% | 6 | 0.77 | 0 | Crown Lift +40 |
| p_h16_h17 | Crown Steps | 134 | +3.6 | 0.0% | 5 | 0.72 | 0 | - |
| p_h17_h18 | Rim Walk | 156 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Sunset Gondola | 91 | -172.8 | 0.0% | 0 | 0.00 | 0 | Sunset Gondola -172 over 682 |

| hole | play bearing | angle to sun (277) | ok |
|---|---|---|---|
| H1 | 0 | 83 | ok |
| H2 | 0 | 83 | ok |
| H3 | 90 | 173 | ok |
| H4 | 90 | 173 | ok |
| H5 | 0 | 83 | ok |
| H6 | 0 | 83 | ok |
| H7 | 0 | 83 | ok |
| H8 | 0 | 83 | ok |
| H9 | 90 | 173 | ok |
| H10 | 180 | 97 | ok |
| H11 | 0 | 83 | ok |
| H12 | 90 | 173 | ok |
| H13 | 180 | 97 | ok |
| H14 | 180 | 97 | ok |
| H15 | 180 | 97 | ok |
| H16 | 180 | 97 | ok |
| H17 | 0 | 83 | ok |
| H18 | 0 | 83 | ok |

| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |
|---|---|---|---|---|
| H1 | 600 | +6.2 | +6.2 | visible |
| H2 | 540 | +6.3 | +6.3 | visible |
| H3 | 492 | +6.3 | +6.4 | visible |
| H4 | 475 | -35.9 | -35.2 | hidden (slot canyon) |
| H5 | 498 | -29.8 | -29.3 | hidden (slot canyon) |
| H6 | 434 | -26.2 | -25.6 | hidden (slot canyon) |
| H7 | 382 | +6.0 | +6.1 | visible |
| H8 | 336 | +6.1 | +6.1 | visible |
| H9 | 251 | +6.3 | +6.4 | visible |
| H10 | 270 | +5.6 | +5.6 | visible |
| H11 | 141 | +5.7 | +5.7 | visible |
| H12 | 313 | +5.6 | +5.6 | visible |
| H13 | 412 | +1.0 | +0.5 | visible |
| H14 | 386 | +1.2 | +0.8 | visible |
| H15 | 380 | +1.6 | +1.2 | visible |
| H16 | 451 | +1.3 | +1.0 | visible |
| H17 | 558 | -10.0 | -10.9 | hidden (p8 visibility exemption) |
| H18 | 620 | -16.8 | -18.0 | hidden (p8 visibility exemption) |
