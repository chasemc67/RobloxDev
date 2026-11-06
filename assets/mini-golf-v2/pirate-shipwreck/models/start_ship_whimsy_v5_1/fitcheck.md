# Fitcheck: start ship whimsy v5_1 (out/start_ship_whimsy_v5_1.blend) vs source_v5.blend

**Overall hard checks: PASS**

## FAILS
- none

## Warnings
- total visual tris 63635 above ~40k near-field target (source 60343)

## FLAGS for the builder
- **hull-side colliders: v5_1 visual belly sits up to 3.21 studs outside the stale v3_2 COL_HullExt boxes (p95 2.43, 419 samples >1 stud). Studio v30 hull-side/under bands must be REGENERATED against this Hull.**

## Collision: NOT verified vs Studio v30
- 190/190 Blender colliders byte-identical to source_v5 (mesh verts, loops, polys, UV, material slots, matrix_world, world verts). Changed: none
- NOT VERIFIED against Studio v30. These are the stale v3_2 boxes. No collision FBX exported; see `out/fbx/UNSYNCED_keep_studio_v30_colliders.txt`.

## Locks
- DeckCabin: EXACT (verts, loops, polys, materials, UV, matrix, world verts, datablock, collection)
- RampFlight1: EXACT (verts, loops, polys, materials, UV, matrix, world verts, datablock, collection)
- RampLanding: EXACT (verts, loops, polys, materials, UV, matrix, world verts, datablock, collection)
- RampFlight2: EXACT (verts, loops, polys, materials, UV, matrix, world verts, datablock, collection)
- anchors exact: Spawn=True [np.float64(-120.0), np.float64(24.0), np.float64(2.5)], Tee1=True [np.float64(-120.0), np.float64(24.4), np.float64(37.0)], RampStart=True [np.float64(-120.0), np.float64(24.0), np.float64(62.5)], CupRef=True [np.float64(-175.7), np.float64(0.0), np.float64(212.37)]
- spawn headroom identical True; door rays identical True (80 rays); tee sightlines identical True; deck walk surfaces identical True

## Names / origins
- every source object present, same name, same origin matrix_world, same mesh datablock, same collection: **True** (missing [], new [], origin changed [])
- must-unchanged (sails emblem, flag, zigzag mast, crab, lantern + glow, sail patches, Prop_SternCurl corner scrolls, pier, rock, dressing): changed = none
- Rigging: 20 of 4269 verts moved (belly warp of low anchor lines only), max 0.554; max displacement above Y14 = 0.0 (sails/masts untouched)

## Changed meshes (all keep name + origin)
| mesh | what changed | tris v5 -> v5_1 |
|---|---|---|
| Hull | belly warp (vertex positions only) | 4835 -> 4835 |
| Prop_Barnacles | belly warp (vertex positions only) | 1620 -> 1620 |
| Prop_CargoCluster | prop mesh moved out of the tee sightline (vertex positions only) | 2216 -> 2216 |
| Prop_Figurehead | REBUILT in place (vertices rebuilt, same object/mesh datablock/origin) | 2884 -> 3404 |
| Prop_PatchPlanks | belly warp (vertex positions only) | 2420 -> 2420 |
| Prop_RopeCoils | prop mesh moved out of the tee sightline (vertex positions only) | 1608 -> 1608 |
| Prop_Seaweed | belly warp (vertex positions only) | 1376 -> 1376 |
| Prop_SternWheel | prop mesh moved out of the tee sightline (vertex positions only) | 1640 -> 1640 |
| Prop_TreasureChest | prop mesh moved out of the tee sightline (vertex positions only) | 980 -> 980 |
| Rigging | belly warp (vertex positions only) | 8154 -> 8154 |
| ShipV5_BowEyes | REBUILT in place (vertices rebuilt, same object/mesh datablock/origin) | 456 -> 848 |
| ShipV5_Patches | REBUILT in place (vertices rebuilt, same object/mesh datablock/origin) | 1300 -> 3344 |
| ShipV5_SheerRise | REBUILT in place (vertices rebuilt, same object/mesh datablock/origin) | 888 -> 1224 |
| ShipV5_SternCurl | EDITED: vertices scaled 1.8x about the crest base and lifted with the +3 crest (same object/origin/topology/UV/materials) | 876 -> 876 |

## Route QA (triangle-swept, player r=2.0)
- triangle-swept: every triangle densely sampled (barycentric grid, spacing <= 0.20 studs, so true clearance >= reported - 0.12) and measured against each walkway segment: (a) prior corridor volume (half-width hw about the centreline, walk band -1..+10) and (b) swept player capsule r=2.0, 5.5 tall, centre path within hw-2 of the centreline.
- segments: cabin_door_tee_gangplank hw 4.00; flight1 hw 6.00; landing (Studio v30 exit 12.54 wide) hw 6.27; flight2_yawed hw 6.00; flight2_unyawed hw 6.00
- new intrusions by changed meshes: none; new exact BVH corridor-volume overlaps: none

### Moved tee props: exact measured clearances vs the cabin->door->tee->gangplank walkway (x=-120, z-17..62.5)
| prop | object | player clearance before -> after (studs) | corridor(hw4) clearance before -> after | min player clearance, all segments (after) | tee-frame visible verts before -> after | offset from tee axis after (deg) |
|---|---|---|---|---|---|---|
| wheel | Prop_SternWheel | 44.908 -> 35.599 | 44.908 -> 35.529 | 35.599 | 387/434 -> 0/434 | [20.0, 28.2] |
| chest | Prop_TreasureChest | 31.257 -> 35.771 | 31.210 -> 35.771 | 35.771 | 385/512 -> 0/512 | [30.5, 39.3] |
| tee rope coil | Prop_RopeCoils | 23.603 -> 9.997 | 23.550 -> 9.883 | 9.997 | 130/408 -> 172/408 | [6.6, 38.7] |
| barrels | Prop_CargoCluster | 9.143 -> 11.524 | 9.143 -> 11.524 | 11.524 | 504/582 -> 180/582 | [0.0, 180.0] |

- Prop_RopeCoils and Prop_CargoCluster are multi-part meshes: only the tee coil (x-90) and the 3 barrels moved; their other parts (mast/forecastle coils, the crab's crate stack) did not, so the object-level numbers above include the unmoved parts.
- Physical route was already clear in v5 (before values above); this pass is a VISUAL sightline fix, not a physical-obstruction fix.

### All meshes: min player clearance per segment (v5 -> v5_1)
| mesh | cabin_door_tee_gangplank | flight1 | landing (Studio v30 exit 12.54 wide) | flight2_yawed | flight2_unyawed |
|---|---|---|---|---|---|
| Dressing | 3.70 -> 3.70 | 1.72 -> 1.72 | 46.55 -> 46.55 | 60.09 -> 60.09 | 60.09 -> 60.09 |
| Dressing_Glow | 6.06 -> 6.06 | 4.78 -> 4.78 | 49.05 -> 49.05 | 62.07 -> 62.07 | 62.07 -> 62.07 |
| Hull * | 0.21 -> 0.21 | 4.51 -> 4.51 | 55.00 -> 55.00 | 68.29 -> 68.29 | 68.29 -> 68.29 |
| Pier | 87.31 -> 87.31 | 83.88 -> 83.88 | 83.57 -> 83.57 | 41.17 -> 41.17 | 77.00 -> 77.00 |
| Prop_Barnacles * | 59.62 -> 59.62 | 66.72 -> 64.83 | 98.01 -> 94.33 | 113.50 -> 109.71 | 113.50 -> 109.71 |
| Prop_BowRaise | 166.16 -> 166.16 | 164.78 -> 164.78 | 176.95 -> 176.95 | 188.73 -> 188.73 | 188.73 -> 188.73 |
| Prop_BulwarkFrames | n/a(>12 prefilter) -> n/a(>12 prefilter) | n/a(>12 prefilter) -> n/a(>12 prefilter) | n/a(>12 prefilter) -> n/a(>12 prefilter) | n/a(>12 prefilter) -> n/a(>12 prefilter) | n/a(>12 prefilter) -> n/a(>12 prefilter) |
| Prop_BulwarkGear | 22.41 -> 22.41 | 23.31 -> 23.31 | 63.75 -> 63.75 | 79.08 -> 79.08 | 79.08 -> 79.08 |
| Prop_CabinWindows | 13.14 -> 13.14 | 35.57 -> 35.57 | 85.47 -> 85.47 | 98.43 -> 98.43 | 98.43 -> 98.43 |
| Prop_Cannons | 63.16 -> 63.16 | 76.18 -> 76.18 | 98.08 -> 98.08 | 112.32 -> 112.32 | 112.32 -> 112.32 |
| Prop_CapRails | 18.83 -> 18.83 | 17.82 -> 17.82 | 57.57 -> 57.57 | 71.80 -> 71.80 | 71.80 -> 71.80 |
| Prop_CargoCluster * | 9.14 -> 11.52 | 26.35 -> 21.34 | 75.50 -> 67.51 | 90.74 -> 79.97 | 90.74 -> 79.97 |
| Prop_Crab | 18.16 -> 18.16 | 33.28 -> 33.28 | 81.36 -> 81.36 | 96.68 -> 96.68 | 96.68 -> 96.68 |
| Prop_DoorLantern | 8.61 -> 8.61 | 30.63 -> 30.63 | 81.65 -> 81.65 | 96.52 -> 96.52 | 96.52 -> 96.52 |
| Prop_DoorLantern_Glow | 9.08 -> 9.08 | 31.10 -> 31.10 | 82.10 -> 82.10 | 96.97 -> 96.97 | 96.97 -> 96.97 |
| Prop_Figurehead * | n/a(>12 prefilter) -> n/a(>12 prefilter) | n/a(>12 prefilter) -> n/a(>12 prefilter) | n/a(>12 prefilter) -> n/a(>12 prefilter) | n/a(>12 prefilter) -> n/a(>12 prefilter) | n/a(>12 prefilter) -> n/a(>12 prefilter) |
| Prop_Flag | 226.46 -> 226.46 | 226.24 -> 226.24 | 241.79 -> 241.79 | 252.53 -> 252.53 | 252.53 -> 252.53 |
| Prop_PatchPlanks * | 73.20 -> 73.20 | 75.90 -> 75.03 | 102.22 -> 100.05 | 117.29 -> 115.01 | 117.29 -> 115.01 |
| Prop_Portholes | 33.89 -> 33.89 | 35.19 -> 35.19 | 70.67 -> 70.67 | 86.34 -> 86.34 | 86.34 -> 86.34 |
| Prop_RoofTrim | 9.69 -> 9.69 | 30.92 -> 30.92 | 82.88 -> 82.88 | 96.66 -> 96.66 | 96.66 -> 96.66 |
| Prop_RopeCoils * | 23.60 -> 10.00 | 31.66 -> 18.19 | 74.92 -> 65.66 | 90.59 -> 81.02 | 90.59 -> 81.02 |
| Prop_Seaweed * | 57.34 -> 57.34 | 62.45 -> 60.66 | 87.19 -> 87.19 | 101.32 -> 101.32 | 101.32 -> 101.32 |
| Prop_SheerWale | 20.00 -> 20.00 | 19.77 -> 19.77 | 60.13 -> 60.13 | 75.59 -> 75.59 | 75.59 -> 75.59 |
| Prop_SternCastle | 18.55 -> 18.55 | 17.58 -> 17.58 | 57.25 -> 57.25 | 68.75 -> 68.75 | 68.75 -> 68.75 |
| Prop_SternCurl | 35.94 -> 35.94 | 37.43 -> 37.43 | 72.88 -> 72.88 | 82.75 -> 82.75 | 82.75 -> 82.75 |
| Prop_SternWheel * | 44.91 -> 35.60 | 49.47 -> 67.84 | 85.90 -> 114.58 | 101.42 -> 130.19 | 101.42 -> 130.19 |
| Prop_Stovepipe | 21.49 -> 21.49 | 47.73 -> 47.73 | 98.07 -> 98.07 | 110.76 -> 110.76 | 110.76 -> 110.76 |
| Prop_TreasureChest * | 31.26 -> 35.77 | 35.98 -> 78.61 | 74.68 -> 125.00 | 90.39 -> 140.69 | 90.39 -> 140.69 |
| Rigging * | 41.55 -> 41.55 | 54.34 -> 54.34 | 100.47 -> 100.47 | 112.41 -> 112.41 | 112.41 -> 112.41 |
| RockBumper | 119.39 -> 119.39 | 65.74 -> 65.74 | 48.69 -> 48.69 | 6.43 -> 6.43 | -2.00 -> -2.00 |
| ShipV5_Bottle | 178.05 -> 178.05 | 190.36 -> 190.36 | 214.55 -> 214.55 | 228.37 -> 228.37 | 228.37 -> 228.37 |
| ShipV5_BowEyes * | 249.94 -> 247.88 | 249.98 -> 254.00 | 262.09 -> 272.16 | 273.25 -> 284.44 | 273.25 -> 284.44 |
| ShipV5_Hammock | 147.07 -> 147.07 | 162.30 -> 162.30 | 189.98 -> 189.98 | 204.42 -> 204.42 | 204.42 -> 204.42 |
| ShipV5_MastZigzag | 142.44 -> 142.44 | 143.81 -> 143.81 | 166.60 -> 166.60 | 178.52 -> 178.52 | 178.52 -> 178.52 |
| ShipV5_Patches * | 32.33 -> 11.36 | 37.34 -> 12.79 | 75.32 -> 58.16 | 91.11 -> 73.43 | 91.11 -> 73.43 |
| ShipV5_SailEmblem | 131.97 -> 131.97 | 136.52 -> 136.52 | 161.11 -> 161.11 | 174.72 -> 174.72 | 174.72 -> 174.72 |
| ShipV5_SailPatches | 130.49 -> 130.49 | 133.94 -> 133.94 | 156.53 -> 156.53 | 170.04 -> 170.04 | 170.04 -> 170.04 |
| ShipV5_SheerRise * | 42.27 -> 24.49 | 40.89 -> 23.90 | 71.65 -> 62.29 | 79.71 -> 73.24 | 79.71 -> 73.24 |
| ShipV5_SternCurl * | 51.31 -> 52.62 | 66.95 -> 67.17 | 111.11 -> 110.87 | 121.26 -> 120.84 | 121.26 -> 120.84 |
| ShipV5_Telescope | 146.34 -> 146.34 | 147.49 -> 147.49 | 169.74 -> 169.74 | 181.78 -> 181.78 | 181.78 -> 181.78 |
| ShipV5_YardNest | 207.49 -> 207.49 | 208.04 -> 208.04 | 222.60 -> 222.60 | 234.38 -> 234.38 | 234.38 -> 234.38 |

(* = changed in v5_1. Negative = pre-existing geometry inside the player envelope, e.g. Hull rail/notch at the gangplank and the pier/ramp-adjacent meshes; identical in v5 and v5_1.)

## Tee sightline (art: wheel/chest blocked the tee centreline)
- Prop_SternWheel: visible verts from the tee eye 387/434 -> 0/434; azimuth offset from tee camera axis [0.3, 15.0] -> [20.0, 28.2] deg
- Prop_TreasureChest: visible verts from the tee eye 385/512 -> 0/512; azimuth offset from tee camera axis [11.2, 23.0] -> [30.5, 39.3] deg
- Prop_RopeCoils: visible verts from the tee eye 130/408 -> 172/408; azimuth offset from tee camera axis [6.6, 17.7] -> [6.6, 38.7] deg
- Prop_CargoCluster: visible verts from the tee eye 504/582 -> 180/582; azimuth offset from tee camera axis [0.0, 23.9] -> [0.0, 180.0] deg
- Prop_Crab: visible verts from the tee eye 403/428 -> 403/428; azimuth offset from tee camera axis [0.0, 13.3] -> [0.0, 13.3] deg
- Prop_DoorLantern: visible verts from the tee eye 214/248 -> 214/248; azimuth offset from tee camera axis [17.6, 33.5] -> [17.6, 33.5] deg
- ShipV5_BowEyes: visible verts from the tee eye 0/244 -> 0/452; azimuth offset from tee camera axis [5.6, 13.8] -> [5.0, 12.9] deg

## Coplanarity
- face centre within 0.03 of another visual mesh, |dot|>0.995, plane gap <0.02 (prior method); 18773 faces; source pairs 0, v5_1 pairs 0, NEW pairs 0 

## Belly (horizontal Hull width, world Z, studs): v5 -> v5_1
- f = 1 + 0.16 * sin^2(pi*(Y-(-8))/(22)) * gX(x); peak at world Y3.0; 0 at/below Y-8 and at/above Y14 (deck Y24 untouched); same as v5: 1.0 for x in [-130,105]; stern end 0.35 at x-160; bow fades to 0 by x150
| Y | x-140 | x-100 | x-60 | x-20 | x20 | x60 | x100 |
|---|---|---|---|---|---|---|---|
| Y-2.0 | 2.784 -> 3.009 (x1.081) | 2.871 -> 3.147 (x1.096) | 2.857 -> 3.13 (x1.096) | 2.792 -> 3.059 (x1.096) | 2.814 -> 3.079 (x1.094) | 4.027 -> 4.398 (x1.092) | None -> None |
| Y-0.6 | 19.367 -> 21.34 (x1.102) | 19.977 -> 22.442 (x1.123) | 19.899 -> 22.353 (x1.123) | 19.378 -> 21.77 (x1.123) | 18.192 -> 20.439 (x1.124) | 16.163 -> 18.152 (x1.123) | None -> None |
| Y1.5 | 30.663 -> 34.499 (x1.125) | 31.614 -> 36.428 (x1.152) | 31.489 -> 36.287 (x1.152) | 30.687 -> 35.359 (x1.152) | 28.808 -> 33.177 (x1.152) | 25.352 -> 29.167 (x1.150) | None -> None |
| Y3.0 | 36.432 -> 41.039 (x1.126) | 37.506 -> 43.261 (x1.153) | 37.317 -> 43.043 (x1.153) | 36.345 -> 41.92 (x1.153) | 34.113 -> 39.357 (x1.154) | 30.029 -> 34.721 (x1.156) | 11.528 -> 13.277 (x1.152) |
| Y6.0 | 45.423 -> 50.076 (x1.102) | 46.73 -> 52.537 (x1.124) | 46.493 -> 52.255 (x1.124) | 45.272 -> 50.883 (x1.124) | 42.474 -> 47.788 (x1.125) | 37.415 -> 42.234 (x1.129) | 21.516 -> 24.252 (x1.127) |
| Y9.0 | 52.173 -> 55.15 (x1.057) | 53.445 -> 57.199 (x1.070) | 53.122 -> 56.871 (x1.071) | 51.703 -> 55.333 (x1.070) | 48.467 -> 51.774 (x1.068) | 42.174 -> 44.972 (x1.066) | 27.3 -> 29.207 (x1.070) |
| Y12.0 | 55.978 -> 56.983 (x1.018) | 57.038 -> 58.171 (x1.020) | 56.796 -> 57.857 (x1.019) | 55.315 -> 56.354 (x1.019) | 51.76 -> 52.918 (x1.022) | 45.298 -> 46.451 (x1.025) | 30.781 -> 31.505 (x1.024) |
| Y18.0 | 62.766 -> 62.766 (x1.000) | 63.19 -> 63.196 (x1.000) | 62.838 -> 62.847 (x1.000) | 61.182 -> 61.191 (x1.000) | 57.378 -> 57.38 (x1.000) | 50.196 -> 50.196 (x1.000) | 35.811 -> 35.812 (x1.000) |
| Y23.0 | 69.174 -> 69.174 (x1.000) | 69.631 -> 69.631 (x1.000) | 69.295 -> 69.295 (x1.000) | 67.417 -> 67.417 (x1.000) | 63.075 -> 63.075 (x1.000) | 55.134 -> 55.134 (x1.000) | 40.333 -> 40.333 (x1.000) |
- deck level (Y23) max width change 0.0000 (deck footprint fixed); water = local Y-0.6.

## Sheer (top of exterior silhouette: cap rail / sheer rise / bow raise / hull / stern castle, per station, studs): v5 -> v5_1
| station | v5 | v5_1 | delta |
|---|---|---|---|
| x-158_high | 77.44 | 77.44 | 0.0 |
| x-158_low | 54.8 | 60.85 | 6.05 |
| x-150_high | 58.1 | 81.16 | 23.06 |
| x-150_low | 35.45 | 58.87 | 23.42 |
| x-140_high | 78.7 | 81.68 | 2.98 |
| x-140_low | 49.99 | 50.58 | 0.59 |
| x-130_high | 67.25 | 73.88 | 6.63 |
| x-130_low | 23.0 | 23.0 | 0.0 |
| x90_high | 57.73 | 58.4 | 0.67 |
| x90_low | 43.14 | 43.66 | 0.52 |
| x100_high | 57.48 | 57.48 | 0.0 |
| x100_low | 44.8 | 44.8 | 0.0 |
| x110_high | 60.42 | 61.86 | 1.44 |
| x110_low | 48.4 | 49.85 | 1.45 |
| x120_high | 59.31 | 59.31 | 0.0 |
| x120_low | 49.01 | 49.01 | 0.0 |
| x130_high | 62.87 | 65.48 | 2.61 |
| x130_low | 54.4 | 57.02 | 2.62 |
| x140_high | 59.58 | 59.58 | 0.0 |
| x140_low | 52.21 | 60.25 | 8.04 |
| x150_high | 63.48 | 66.63 | 3.15 |
| x150_low | 59.88 | 63.05 | 3.17 |
| x154_high | 64.17 | 67.31 | 3.14 |
| x154_low | 55.95 | 55.95 | 0.0 |
- bow rise board: 0 at x82 -> +7.0 at the stem (v5: +4.0); transom crest corners +4.6 / centre +7.0 above the castle top (v5: +1.6 / +4.0); new stern side rise boards 0 -> +4.6 on the stern castle tops. Exterior trim only (no walk surface touched).

## Stern curl
- ShipV5_SternCurl scaled 1.8x about its crest base [-160.6, 66.08, 13.75] -> [-160.6, 69.075, 13.75]: height above base 22.26 -> 40.07, top Y 88.34 -> 109.15, aft-most x -179.01 -> -193.74. Prop_SternCurl corner scrolls unchanged.

## Octopus figurehead
- Prop_Figurehead rebuilt 1.6x (same origin): bbox [[154.25, 31.12, 3.87], [194.38, 69.52, 19.7]] -> [[np.float64(153.47), np.float64(20.81), np.float64(-1.62)], [np.float64(198.46), np.float64(69.8), np.float64(20.55)]]; height 38.4 -> 49.0; 441 CoralDk underside faces.

## Bow eyes
- v5: [{"side": "high(-Z)", "centre": [136.0, 53.78, -2.56], "rim_radius": 2.55}, {"side": "low(+Z)", "centre": [136.0, 46.53, 28.74], "rim_radius": 2.55}]
- v5_1: [{"side": "high(-Z)", "x": 136.0, "centre": [136.32, 52.62, -2.93], "normal": [0.396, 0.238, -0.887], "below_cap_top": 7.15, "rim_radius": 5.1, "rim_min_surface_offset": -1.7}, {"side": "low(+Z)", "x": 152.0, "centre": [152.44, 47.71, 21.15], "normal": [0.544, -0.217, 0.81], "below_cap_top": 8.15, "rim_radius": 5.1, "rim_min_surface_offset": -1.16}]
- tee view: visible verts 0/452 (source 0/244)

## Hull patches
- [{"side": "low(+Z)", "x": 115.0, "Y": 31.0, "mat": "PatchBlue", "size": [20.0, 14.0], "rot_deg": 7, "nails": 10}, {"side": "low(+Z)", "x": 85.0, "Y": 23.0, "mat": "PatchTeal", "size": [20.0, 14.0], "rot_deg": -9, "nails": 10}, {"side": "low(+Z)", "x": -95.0, "Y": 21.0, "mat": "PatchTeal", "size": [20.0, 14.0], "rot_deg": -6, "nails": 10}, {"side": "low(+Z)", "x": -65.0, "Y": 19.0, "mat": "PatchBlue", "size": [20.0, 14.0], "rot_deg": 10, "nails": 10}]
- linear scale vs v5 patch 2.67x, area 6.79x

## Hull-side collider FLAG (colliders untouched)
- outer Hull sampled by horizontal rays (x-158..146 step 4, Y-0.5..18 step 1.5, both sides); distance outside the nearest STALE v3_2 COL_HullExt oriented box
- v5: {'max': 3.2, 'p95': 0.67, 'n_over_0_5': 158, 'n_over_1': 32}; v5_1: {'max': 3.206, 'p95': 2.426, 'n_over_0_5': 565, 'n_over_1': 419, 'n_over_2': 148}; increase vs v5: {'max': 2.57, 'n_over_0_5': 508, 'n_over_1': 365, 'boxes_over_1': ['COL_HullExt_1_02', 'COL_HullExt_1_06']}
- Studio v30 hull-side/under bands (930 COL_HullSide* + 80 COL_HullUnder*) were fitted to the v3_2 hull. The v5_1 belly is rounder (up to ~+15% width at Y1.5-3). Builder must REGENERATE the bands against the new Hull; do not paste v30 band transforms.

## Triangles
| mesh | v5 | v5_1 |
|---|---|---|
| DeckCabin | 3512 | 3512 |
| Dressing | 516 | 516 |
| Dressing_Glow | 24 | 24 |
| Hull | 4835 | 4835 |
| Pier | 948 | 948 |
| Prop_Barnacles | 1620 | 1620 |
| Prop_BowRaise | 1104 | 1104 |
| Prop_BulwarkFrames | 2952 | 2952 |
| Prop_BulwarkGear | 866 | 866 |
| Prop_CabinWindows | 976 | 976 |
| Prop_Cannons | 1212 | 1212 |
| Prop_CapRails | 1452 | 1452 |
| Prop_CargoCluster | 2216 | 2216 |
| Prop_Crab | 780 | 780 |
| Prop_DoorLantern | 460 | 460 |
| Prop_DoorLantern_Glow | 12 | 12 |
| Prop_Figurehead | 2884 | 3404 |
| Prop_Flag | 760 | 760 |
| Prop_PatchPlanks | 2420 | 2420 |
| Prop_Portholes | 1316 | 1316 |
| Prop_RoofTrim | 212 | 212 |
| Prop_RopeCoils | 1608 | 1608 |
| Prop_Seaweed | 1376 | 1376 |
| Prop_SheerWale | 1520 | 1520 |
| Prop_SternCastle | 1280 | 1280 |
| Prop_SternCurl | 2796 | 2796 |
| Prop_SternWheel | 1640 | 1640 |
| Prop_Stovepipe | 288 | 288 |
| Prop_TreasureChest | 980 | 980 |
| RampFlight1 | 300 | 300 |
| RampFlight2 | 288 | 288 |
| RampLanding | 184 | 184 |
| Rigging | 8154 | 8154 |
| RockBumper | 80 | 80 |
| ShipV5_Bottle | 108 | 108 |
| ShipV5_BowEyes | 456 | 848 |
| ShipV5_Hammock | 592 | 592 |
| ShipV5_MastZigzag | 552 | 552 |
| ShipV5_Patches | 1300 | 3344 |
| ShipV5_SailEmblem | 2224 | 2224 |
| ShipV5_SailPatches | 1152 | 1152 |
| ShipV5_SheerRise | 888 | 1224 |
| ShipV5_SternCurl | 876 | 876 |
| ShipV5_Telescope | 212 | 212 |
| ShipV5_YardNest | 412 | 412 |
| **total visual** | **60343** | **63635** |
- largest mesh: Rigging (8154); all < 20k: True