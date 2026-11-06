# Fitcheck: start ship v3_2 (out/start_ship_v3_2.blend) vs baseline source_v3_1.blend

**Overall hard checks: PASS**

## FAILS
- none

## Warnings
- total visual tris 51307 above ~40k target
- no runtime/Studio validation was run (no Studio in this job)

## Coplanarity (checker unchanged: same 14 objects, find_nearest 0.03, |dot|>0.995, plane gap <0.02)
- v3_1: 4 coplanar pairs; v3_2: **0** (11423 faces checked)
- repair script re-ran the identical test before/after: 4 -> 0

## Repairs (geometry-local, Prop_BowRaise + Prop_CapRails only; Prop_SternCastle not modified)

- **D1 Prop_BowRaise vs Prop_CapRails at Roblox [72.48,55.44,-20.13] (high side)**: BowRaise dark plank line (WoodDk tube, 0.64 tall) climbs into the CapRails underside at a shallow angle; its top face crossed the cap bottom between x71-74 (gap -0.04..+0.06). Fix: trim endpoint: plank line start moved x56 -> x77 (first ring >=0.10 below the cap underside; measured 0.157); 7 rings / 28 verts / 29 faces removed, 1 WoodDk end face added (UVs copied from the old end face). Displacement: no vertex moved; 21.0 studs of the line removed (x56-77, where it was already 0.04-0.44 buried in the cap underside).
- **D2 Prop_BowRaise vs Prop_CapRails at Roblox [72.48,37.95,45.15] (low side)**: mirror of D1. Fix: same trim on the low-side plank line (x56 -> x77, new start 0.157 below cap); 28 verts / 29 faces removed, 1 face added. Displacement: none (trim).
- **D3 Prop_CapRails vs Hull at Roblox [51.54,54.24,-22.28]**: high-side cap underside crosses the Hull WoodDk rail top near x51.5 (gap -0.06 at x50, +0.06 at x53); region lies inside the BowRaise panel / under the cap overhang. Fix: surface displacement on CapRails only: bottom 2 verts of rings x50, x53, x56 set to 0.10 below the Hull rail top (hull-frame vertical, 15 deg tilt); next untouched ring x59 is +0.354 above so the transition face stays >=0.08 clear; Hull untouched. Displacement: 6 verts moved down [-0.035, -0.0457, -0.1555, -0.1651, -0.2929, -0.3011] studs (max 0.3011); cap locally 0.04-0.30 deeper, no topology change.
- **D4 Prop_CapRails vs Prop_SternCastle at Roblox [-118.0,66.93,-27.33]**: high-side cap start face at x-118 lay exactly on the SternCastle lower-tier end face (x-118); both are inside the SternCastle step-end post box (x-118.6..-117.0). Fix: trim endpoint: cap start ring slid 0.5 along the tube toward ring 2 (x-118 -> x-117.5); start face stays hidden inside the post; SternCastle not modified. Displacement: 4 verts moved [0.5002, 0.5001, 0.5, 0.5002] studs.

## Changed meshes vs v3_1: ['Prop_BowRaise', 'Prop_CapRails'] (everything else exact)

| object | category | geometry | UV | material assignment | origin matrix | datablock | collections | tris v3_1 -> v3_2 |
|---|---|---|---|---|---|---|---|---|
| DeckCabin | LOCKED | True | True | True | True | True | True | 3512 -> 3512 |
| Dressing | must_unchanged | True | True | True | True | True | True | 516 -> 516 |
| Dressing_Glow | must_unchanged | True | True | True | True | True | True | 24 -> 24 |
| Hull | must_unchanged | True | True | True | True | True | True | 4835 -> 4835 |
| Pier | must_unchanged | True | True | True | True | True | True | 948 -> 948 |
| Prop_Barnacles | must_unchanged_v3_1 | True | True | True | True | True | True | 1620 -> 1620 |
| Prop_BowRaise | permitted_repair | False | False | False | True | True | True | 1216 -> 1104 |
| Prop_BulwarkFrames | must_unchanged_v3_1 | True | True | True | True | True | True | 2952 -> 2952 |
| Prop_BulwarkGear | must_unchanged_v3_1 | True | True | True | True | True | True | 866 -> 866 |
| Prop_CabinWindows | must_unchanged_v3_1 | True | True | True | True | True | True | 976 -> 976 |
| Prop_Cannons | must_unchanged_v3_1 | True | True | True | True | True | True | 1212 -> 1212 |
| Prop_CapRails | permitted_repair | False | True | True | True | True | True | 1452 -> 1452 |
| Prop_CargoCluster | must_unchanged_v3_1 | True | True | True | True | True | True | 2216 -> 2216 |
| Prop_Crab | must_unchanged_v3_1 | True | True | True | True | True | True | 780 -> 780 |
| Prop_DoorLantern | must_unchanged_v3_1 | True | True | True | True | True | True | 460 -> 460 |
| Prop_DoorLantern_Glow | must_unchanged_v3_1 | True | True | True | True | True | True | 12 -> 12 |
| Prop_Figurehead | must_unchanged_v3_1 | True | True | True | True | True | True | 2712 -> 2712 |
| Prop_Flag | must_unchanged_v3_1 | True | True | True | True | True | True | 760 -> 760 |
| Prop_PatchPlanks | must_unchanged_v3_1 | True | True | True | True | True | True | 2420 -> 2420 |
| Prop_Portholes | must_unchanged_v3_1 | True | True | True | True | True | True | 1316 -> 1316 |
| Prop_RoofTrim | must_unchanged_v3_1 | True | True | True | True | True | True | 212 -> 212 |
| Prop_RopeCoils | must_unchanged_v3_1 | True | True | True | True | True | True | 1608 -> 1608 |
| Prop_Seaweed | must_unchanged_v3_1 | True | True | True | True | True | True | 1376 -> 1376 |
| Prop_SheerWale | must_unchanged_v3_1 | True | True | True | True | True | True | 1520 -> 1520 |
| Prop_SternCastle | permitted_repair | True | True | True | True | True | True | 1280 -> 1280 |
| Prop_SternCurl | must_unchanged_v3_1 | True | True | True | True | True | True | 2796 -> 2796 |
| Prop_SternWheel | must_unchanged_v3_1 | True | True | True | True | True | True | 1640 -> 1640 |
| Prop_Stovepipe | must_unchanged_v3_1 | True | True | True | True | True | True | 196 -> 196 |
| Prop_TreasureChest | must_unchanged_v3_1 | True | True | True | True | True | True | 980 -> 980 |
| RampFlight1 | LOCKED | True | True | True | True | True | True | 300 -> 300 |
| RampFlight2 | LOCKED | True | True | True | True | True | True | 288 -> 288 |
| RampLanding | LOCKED | True | True | True | True | True | True | 184 -> 184 |
| Rigging | must_unchanged_v3_1 | True | True | True | True | True | True | 8154 -> 8154 |
| RockBumper | must_unchanged | True | True | True | True | True | True | 80 -> 80 |

Anchors exact: Spawn=True, Tee1=True, RampStart=True, CupRef=True; all empties identical set True, matrices identical True

## Collision
- 190/190 colliders, names identical True, **all 190 byte-identical to v3_1: 190**, max world vertex diff 0.0
- COL_Mast_Main exact v3_1: True; along-axis height 98.3 (tilt 18.0 deg); history: v3_1 shortened 157.0 -> 98.3 (delta 58.7), bottom fixed, source v3_1 unchanged; untouched here

## Hull / walk / probes
- Hull identical True; bottom/skirt profile identical at all 32 stations: True (same submersion)
- walk surfaces identical True; spawn headroom ['DeckCabin', 29.1953] identical True; door rays identical True; tee sightlines identical True
- floating-part scan (isolated components, same method as v3_1 dump): identical to v3_1 True (897 components)

## Route corridor (zones/method unchanged from prior script)

| zone | min clearance all props (obj) | repaired meshes only (obj) |
|---|---|---|
| cabin_interior_spawn | 1.7 (Prop_CabinWindows) | 16.295 (Prop_SternCastle) |
| door_approach | 4.192 (Prop_RoofTrim) | 28.316 (Prop_SternCastle) |
| tee_pad_stance | 3.672 (Prop_DoorLantern) | 17.65 (Prop_CapRails) |
| outrigger | 10.031 (Prop_CargoCluster) | 12.926 (Prop_CapRails) |
| flight1 | 14.566 (Prop_SternCastle) | 14.566 (Prop_SternCastle) |
| landing | 59.17 (Prop_SternCastle) | 59.17 (Prop_SternCastle) |
| flight2_apron_yawed | 67.324 (Prop_SternCurl) | 67.705 (Prop_SternCastle) |
| flight2_apron_unyawed | 70.448 (Prop_SternCurl) | 71.787 (Prop_SternCastle) |
| cup_clear_r12 | 134.737 (Prop_SternCurl) | 139.776 (Prop_SternCastle) |

Any vertex/centre inside: False. Any triangle intersection: False

## Triangles

| mesh | status | tris |
|---|---|---|
| DeckCabin | unchanged_vs_v3_1 | 3512 |
| Dressing | unchanged_vs_v3_1 | 516 |
| Dressing_Glow | unchanged_vs_v3_1 | 24 |
| Hull | unchanged_vs_v3_1 | 4835 |
| Pier | unchanged_vs_v3_1 | 948 |
| Prop_Barnacles | unchanged_vs_v3_1 | 1620 |
| Prop_BowRaise | repaired_v3_2 | 1104 |
| Prop_BulwarkFrames | unchanged_vs_v3_1 | 2952 |
| Prop_BulwarkGear | unchanged_vs_v3_1 | 866 |
| Prop_CabinWindows | unchanged_vs_v3_1 | 976 |
| Prop_Cannons | unchanged_vs_v3_1 | 1212 |
| Prop_CapRails | repaired_v3_2 | 1452 |
| Prop_CargoCluster | unchanged_vs_v3_1 | 2216 |
| Prop_Crab | unchanged_vs_v3_1 | 780 |
| Prop_DoorLantern | unchanged_vs_v3_1 | 460 |
| Prop_DoorLantern_Glow | unchanged_vs_v3_1 | 12 |
| Prop_Figurehead | unchanged_vs_v3_1 | 2712 |
| Prop_Flag | unchanged_vs_v3_1 | 760 |
| Prop_PatchPlanks | unchanged_vs_v3_1 | 2420 |
| Prop_Portholes | unchanged_vs_v3_1 | 1316 |
| Prop_RoofTrim | unchanged_vs_v3_1 | 212 |
| Prop_RopeCoils | unchanged_vs_v3_1 | 1608 |
| Prop_Seaweed | unchanged_vs_v3_1 | 1376 |
| Prop_SheerWale | unchanged_vs_v3_1 | 1520 |
| Prop_SternCastle | unchanged_vs_v3_1 | 1280 |
| Prop_SternCurl | unchanged_vs_v3_1 | 2796 |
| Prop_SternWheel | unchanged_vs_v3_1 | 1640 |
| Prop_Stovepipe | unchanged_vs_v3_1 | 196 |
| Prop_TreasureChest | unchanged_vs_v3_1 | 980 |
| RampFlight1 | unchanged_vs_v3_1 | 300 |
| RampFlight2 | unchanged_vs_v3_1 | 288 |
| RampLanding | unchanged_vs_v3_1 | 184 |
| Rigging | unchanged_vs_v3_1 | 8154 |
| RockBumper | unchanged_vs_v3_1 | 80 |

Total visual: **51307** (v3_1: 51419). All meshes <20k: True (largest Rigging). Collision tris: 2280.
Caveat: ~51k total is above the ~40k near-field target (counts pier, rocks, rigging; not all near-field). Not reduced in this repair-only pass.

## Textures
- start_ship_palette.png packed=True

## Not checked / limits
- no runtime/Studio validation (no Studio in this job)
- gaps/embeds of the repaired geometry are measured in repair_log.json, not here
- proud relief >0.08 and plate thickness >=0.2 are build-script parameters (see build_log notes), not re-measured here
- watertightness: Hull geometry is byte-identical to source, so no new cutout; new props are not required to be closed
- deck props (wheel, chest, cargo, crab, rope coils, gear) have no collider; ball/player pass through
