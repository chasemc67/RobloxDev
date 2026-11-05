# start_ship_b2_detail_v3 fitcheck (measured)

Source: `..\source.blend` (sha256 before be3c04090d8b49a2 / after be3c04090d8b49a2 -> UNCHANGED). v3: `out/start_ship_v3.blend`. All numbers below are computed by `src/fitcheck_v3.py` (dump on source.blend, check on v3).

**Hard checks (anchors exact, 190 colliders byte-identical, ramps identical, no new geometry inside the route corridor, every mesh <20k): PASS**

## Anchors (exact float equality of location/rotation/scale/matrix_world vs source)
| empty | Roblox (x,y,z) | exact | max abs diff |
|---|---|---|---|
| Spawn | [-120.0, 24.0, 2.5] | True | 0 |
| Tee1 | [-120.0, 24.4, 37.0] | True | 0 |
| RampStart | [-120.0, 24.0, 62.5] | True | 0 |
| CupRef | [-175.7, 0.0, 212.3705] | True | 0 |

## Collision
- count source 190 / v3 190, names identical: True, collection membership identical: True
- byte-identical (vertex co float32 sha256 + loops + polys + matrix_world + world-vertex sha): **190 / 190**
- max |world vertex diff| over all 190x8 transformed vertices: **0**

## Meshes vs source
| mesh | geometry | materials | UVs | origin | tris src -> v3 |
|---|---|---|---|---|---|
| Hull | False | False | False | True | 4219 -> 4835 |
| DeckCabin | True | True | True | True | 3512 -> 3512 |
| Rigging | False | False | False | True | 400 -> 7282 |
| Pier | True | True | True | True | 948 -> 948 |
| RockBumper | True | True | True | True | 80 -> 80 |
| Dressing | True | True | True | True | 516 -> 516 |
| Dressing_Glow | True | True | True | True | 24 -> 24 |
| RampFlight1 | True | True | True | True | 300 -> 300 |
| RampLanding | True | True | True | True | 184 -> 184 |
| RampFlight2 | True | True | True | True | 288 -> 288 |
- RampFlight1 world-vertex max abs diff: 0
- RampLanding world-vertex max abs diff: 0
- RampFlight2 world-vertex max abs diff: 0
- Hull: 4207/4219 source triangles still present at identical positions; 12 removed, all within 1.95 of the old bowsprit beam axis: True

## Walking surfaces
- DeckCabin byte-identical (see table). Level deck tops at Y24: 382 faces / 16654.784 sq studs (source 382 / 16654.784); forecastle tops Y30 429.043 (source 429.043). Identical: True. Collider tops unchanged (collision section).

## Spawn headroom, door, tee sightline (ray probes against ALL visual meshes incl. new props)
- Spawn headroom (ray straight up from Spawn): source ['DeckCabin', 29.1953], v3 ['DeckCabin', 29.1953], identical True
- Cabin door (cabin door from gen_start_ship.py: x=-120 +-4, 10 high, front wall z=24): 80 rays from inside the cabin (z=18) out through the opening to z=30 on a 1-stud grid x -123.5..-116.5, Y 24.5..33.5: blocked source 0, v3 0, identical True
- Tee eye = Tee1 + 5 studs Y = [-120.0, 29.4, 37.0]. Sightlines (first hit before target):
  - RampStart+1 (dist 25.88): v3 None, source None
  - Landing_centre+1 (dist 87.06): v3 None, source None
  - Flight2_mouth+1 (dist 92.22): v3 ['RampFlight1', 77.077], source ['RampFlight1', 77.077]
  - Flight1_mid+1 (dist 52.54): v3 None, source None
  - identical to source: True (the flight2-mouth ray grazes RampFlight1 in BOTH; no new geometry on any sightline)

## Route corridor clearance (new + rebuilt geometry only)
Method: min distance from every vertex and face centre of each new/rebuilt mesh to each corridor volume (Roblox coords). Zones (Roblox min/max): {"cabin_interior_spawn": [[-148.0, 24.0, -17.0], [-92.0, 40.0, 22.0]], "door_approach": [[-126.0, 24.0, 18.0], [-114.0, 35.0, 30.0]], "tee_pad_stance": [[-128.0, 24.0, 28.0], [-112.0, 31.0, 46.0]], "outrigger": [[-131.0, 24.0, 43.0], [-109.0, 31.0, 63.0]], "flight1": [[-128.0, 11.0, 62.0], [-112.0, 31.0, 116.0]], "landing": [[-129.0, 10.0, 113.0], [-111.0, 20.0, 132.0]]}; flight2 local frame: along -1..72, lateral +-9, height -13..+7 (yawed -30 deg as built in Studio, and unyawed as exported); 12-stud clear radius around CupRef.

| zone | min clearance (studs) | closest new mesh |
|---|---|---|
| cabin_interior_spawn | 1.700 | Prop_CabinWindows |
| door_approach | 5.200 | Prop_DoorLantern |
| tee_pad_stance | 3.672 | Prop_DoorLantern |
| outrigger | 10.031 | Prop_CargoCluster |
| flight1 | 29.058 | Prop_CargoCluster |
| landing | 61.646 | Prop_SternCurl |
| flight2_apron_yawed | 67.324 | Prop_SternCurl |
| flight2_apron_unyawed | 70.448 | Prop_SternCurl |
| cup_clear_r12 | 134.737 | Prop_SternCurl |

**Minimum clearance: 1.700 studs (cabin_interior_spawn, Prop_CabinWindows).** Anything inside a zone: False. Caveat: the cabin_interior zone min (1.7) is the cabin windows sitting on the OUTSIDE of the 2-stud cabin wall (embedded 0.3, never inside the room); door_approach min is the door lantern (12.5 studs east of the door centre, bottom 8.6 above deck).

## Hull submersion (lowest Hull point per x station; water = world Y0 = local -0.6)
| x | source bottom | v3 bottom | identical | submerged (studs) |
|---|---|---|---|---|
| -158 | -2.072 | -2.072 | True | 1.472 |
| -148 | -2.0734 | -2.0734 | True | 1.473 |
| -138 | -2.0747 | -2.0747 | True | 1.475 |
| -128 | -2.076 | -2.076 | True | 1.476 |
| -118 | -2.0771 | -2.0771 | True | 1.477 |
| -108 | -2.0781 | -2.0781 | True | 1.478 |
| -98 | -2.0791 | -2.0791 | True | 1.479 |
| -88 | -2.0802 | -2.0802 | True | 1.48 |
| -78 | -2.0814 | -2.0814 | True | 1.481 |
| -68 | -2.0827 | -2.0827 | True | 1.483 |
| -58 | -2.0841 | -2.0841 | True | 1.484 |
| -48 | -2.0855 | -2.0855 | True | 1.486 |
| -38 | -2.0776 | -2.0776 | True | 1.478 |
| -28 | -2.077 | -2.077 | True | 1.477 |
| -18 | -2.0785 | -2.0785 | True | 1.478 |
| -8 | -2.0691 | -2.0691 | True | 1.469 |
| 2 | -2.0699 | -2.0699 | True | 1.47 |
| 12 | -2.0604 | -2.0604 | True | 1.46 |
| 22 | -2.0588 | -2.0588 | True | 1.459 |
| 32 | -2.0481 | -2.0481 | True | 1.448 |
| 42 | -2.0354 | -2.0354 | True | 1.435 |
| 52 | -2.0198 | -2.0198 | True | 1.42 |
| 62 | -2.0249 | -2.0249 | True | 1.425 |
| 72 | -2.0427 | -2.0427 | True | 1.443 |
| 82 | -1.9895 | -1.9895 | True | 1.389 |
| 92 | -0.9468 | -0.9468 | True | 0.347 |
| 102 | 3.0598 | 3.0598 | True | -3.66 |
| 112 | 9.0513 | 9.0513 | True | -9.651 |
| 122 | 14.1874 | 14.1874 | True | -14.787 |
| 132 | 17.2038 | 17.2038 | True | -17.804 |
| 142 | 19.8114 | 19.8114 | True | -20.411 |
| 152 | 22.7278 | 22.7278 | True | -23.328 |

Stern to midships (x -158..72) stay 1.42-1.49 studs submerged, identical to source; x 82 is 1.39, x 92 0.35, and from x 102 the bow rises onto the beach as in the source (unchanged skirt).

## Coplanarity
- each new/rebuilt face centre: nearest surface of every other visual mesh within 0.03 with parallel normal (|dot|>0.995) and plane gap <0.02
- faces checked 19041, coplanar pairs found **0**.
- Design offsets: hull/wall relief pieces embedded 0.1-0.3 and proud >=0.12 (portholes ~0.7, port frames >=0.6, patch planks >=0.2 at the worst corner + nails 0.35, barnacles 0.7-1.15, sail patches 0.12, flag emblem 0.12, cabin windows 0.8); deck props start 0.1 below the deck top (bottoms hidden); thinnest pieces 0.22 (sail patches/flag emblem), 0.28 (seaweed ribbons), 0.3 (crab legs).

## Tris
| mesh | collection | tris |
|---|---|---|
| Prop_Barnacles | Props | 2728 |
| Prop_BulwarkFrames | Props | 2952 |
| Prop_CabinWindows | Props | 976 |
| Prop_Cannons | Props | 2328 |
| Prop_CapRails | Props | 2712 |
| Prop_CargoCluster | Props | 2216 |
| Prop_Crab | Props | 780 |
| Prop_DoorLantern | Props | 460 |
| Prop_DoorLantern_Glow | Props | 12 |
| Prop_Figurehead | Props | 2712 |
| Prop_Flag | Props | 760 |
| Prop_PatchPlanks | Props | 2420 |
| Prop_Portholes | Props | 1316 |
| Prop_RopeCoils | Props | 1608 |
| Prop_Seaweed | Props | 648 |
| Prop_SternCurl | Props | 2796 |
| Prop_SternWheel | Props | 1640 |
| Prop_TreasureChest | Props | 2372 |
| RampFlight1 | Ramps | 300 |
| RampFlight2 | Ramps | 288 |
| RampLanding | Ramps | 184 |
| DeckCabin | Visual | 3512 |
| Dressing | Visual | 516 |
| Dressing_Glow | Visual | 24 |
| Hull | Visual | 4835 |
| Pier | Visual | 948 |
| Rigging | Visual | 7282 |
| RockBumper | Visual | 80 |
| **total** | | **49405** |

Largest single mesh: Rigging (7282). All <20k: True.

## Envelope / caveats (honest)
- Source floater scan (merged-by-position components whose bbox touches nothing else): 324 components, isolated: none -> nothing removed.
- Source artifact found: DeckCabin deck-slab stern end face coplanar with the Hull stern cap at x=-160 (inward-facing, rendered as a black band). Not edited (walking-surface mesh); covered by a proud WoodDk deck-line trim plank in Prop_SternCurl.
- Hull extends beyond the source collider union envelope: X+ by 44.01 (scenery, no collider)
- Prop_Figurehead extends beyond the source collider union envelope: X+ by 14.99 (scenery, no collider)
- Prop_Portholes extends beyond the source ship visual envelope (Hull+DeckCabin+Rigging+Dressing): X- by 0.38
- Prop_SternCurl extends beyond the source ship visual envelope (Hull+DeckCabin+Rigging+Dressing): X- by 14.01, Z- by 2.19, Z+ by 3.45
- Rigging extends beyond the source collider union envelope: X+ by 38.84 (scenery, no collider)
- Deck props (cargo, crab, chest, wheel, rope coils) stand on the walkable deck with NO collider: players/balls pass through them unless the build bot adds simple CanCollide boxes. They are all outside the route corridor.
- COL_Mast_Main (unchanged) still spans the original 8..165 mast; the visual main mast is now snapped at ~106 (+ splinters to ~113) -> the collider sticks ~50 studs above the visible stump (it is the optional mast collider; consider disabling or shortening it in Studio).
- Stern curl, figurehead, curled bowsprit, cap rails and hull dressing are scenery with no collider (same as the source hull/rigging scenery).
