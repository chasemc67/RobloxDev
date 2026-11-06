# Fitcheck: start ship whimsy v5 (out/start_ship_whimsy_v5.blend) vs source_v3_2.blend

**Overall hard checks: PASS**

## FAILS
- none

## Warnings
- total visual tris 60343 above ~40k near-field target (source 51307)

## FLAGS for the builder
- **hull-side collider mismatch: widened visual hull extends up to 0.83 studs further outside the (stale v3_2) COL_HullExt boxes (106 samples >0.5); builder must re-fit/verify against Studio v30**

## Collision: NOT verified vs Studio v30
- 190/190 colliders byte-identical to source_v3_2 (mesh, UV, materials, matrix, world verts; max diff 0.0). None modified.
- NOT VERIFIED. These are the stale v3_2 Blender colliders. Studio v30 colliders (landing exit 12.54, HullExt disabled at notch, hull-side refit) are authoritative; no collision FBX is handed off (see out/fbx/UNSYNCED_keep_studio_v30_colliders.txt).
- No collision FBX exported; see `out/fbx/UNSYNCED_keep_studio_v30_colliders.txt`.

## Locks
- DeckCabin: verts True, topology True, UV True, material assignment True, origin matrix True, world-vertex max diff None
- RampFlight1: verts True, topology True, UV True, material assignment True, origin matrix True, world-vertex max diff 0.0
- RampLanding: verts True, topology True, UV True, material assignment True, origin matrix True, world-vertex max diff 0.0
- RampFlight2: verts True, topology True, UV True, material assignment True, origin matrix True, world-vertex max diff 0.0
- anchors exact: Spawn=True, Tee1=True, RampStart=True, CupRef=True
- walk surfaces identical: True; door rays identical: True (80 rays); tee sightlines identical: True; spawn headroom identical: True

## Existing objects: names / origins
- every source mesh present with identical name, origin matrix, mesh datablock name, collections: True
- changed vs source: Hull, Prop_Barnacles, Prop_Figurehead, Prop_PatchPlanks, Prop_Seaweed, Prop_Stovepipe, Rigging
  - hull-belly warp (vertex positions only; topology/UV/materials identical): Hull (max 3.89), Prop_Barnacles (max 3.92), Prop_PatchPlanks (max 4.20), Prop_Seaweed (max 4.07), Rigging (max 0.59)
  - rebuilt in place (same object/mesh/origin): Prop_Figurehead (coral octopus), Prop_Stovepipe (lopsided)
  - Rigging: crow's nest (21 components, 192 verts) rotated 10.89 -> 12.00 deg about its base; plus the warp moved its low anchor-line verts (max 0.59)

## New ShipV5_* meshes (Props collection, visual-only, no colliders)

| mesh | tris | note |
|---|---|---|
| ShipV5_Bottle | 108 | teal glass message bottle with cork and cream label band, lying on deck beside the high bulwark at x64 |
| ShipV5_BowEyes | 456 | sleepy bow face: 2 round brass porthole eyes (dark glass + highlight) with droopy half-lid planks, high on the bow flanks |
| ShipV5_Hammock | 592 | canvas hammock with skeleton-free cream pillow, slung between two free-standing posts on the high side deck (x32-52); visual only |
| ShipV5_MastZigzag | 552 | jury-rigged zigzag topmast out of the main-mast splinter crown: 3 Post segments, 2 zigzag bends (rope lashings + iron bands), brass truck knob |
| ShipV5_Patches | 1300 | 5 hull patches (blue 90,130,170 / teal 70,150,140), 0.7 slab (-0.2..+0.5 about the hull surface) of the widened hull, 6 oversized brass nails each |
| ShipV5_SailEmblem | 2224 | original simple skull & crossbones (darkwood 80,50,30, cream eye/nose/teeth inlays) on the top band of the main lower sail, both faces |
| ShipV5_SailPatches | 1152 | large square sail patches (both faces, slab 0.08-0.36 from the sail mid-surface = embedded through the 0.2 sail face) with dark stitch crosses |
| ShipV5_SheerRise | 888 | banana sheer: bow cap-rail rise board (0 at x86 -> +4 at the stem, both sides) + arched transom crest (+1.6 corners, +4 centre). Exterior trim only; walk surfaces untouched. |
| ShipV5_SternCurl | 876 | tall spiral stern curl on the transom crest centre, curling aft (outboard); Prop_SternCurl corner scrolls kept unchanged |
| ShipV5_Telescope | 212 | bent brass telescope (24 deg kink) resting on the 12-deg-tilted crow's nest rim, pointing to the bow |
| ShipV5_YardNest | 412 | twig nest with 3 eggs (2 cream, 1 pale blue) sitting on the fore lower yard near its +Z arm |

## Hull belly widening (horizontal width in studs, world Z, at world Y): before -> after (ratio)

| Y | x-140 | x-100 | x-60 | x-20 | x20 | x60 | x100 | x130 |
|---|---|---|---|---|---|---|---|---|
| Y-0.6 | 17.238 -> 19.367 (1.1235) | 17.371 -> 19.977 (1.15) | 17.303 -> 19.899 (1.15) | 16.851 -> 19.378 (1.15) | 15.819 -> 18.192 (1.15) | 14.055 -> 16.163 (1.15) | None -> None (None) | None -> None (None) |
| Y6.0 | 40.613 -> 45.423 (1.1184) | 40.853 -> 46.73 (1.1439) | 40.643 -> 46.493 (1.1439) | 39.574 -> 45.272 (1.144) | 37.108 -> 42.474 (1.1446) | 32.586 -> 37.415 (1.1482) | 18.784 -> 21.516 (1.1454) | None -> None (None) |
| Y12.0 | 52.861 -> 55.978 (1.059) | 53.216 -> 57.038 (1.0718) | 52.971 -> 56.796 (1.0722) | 51.564 -> 55.315 (1.0727) | 48.241 -> 51.76 (1.0729) | 42.189 -> 45.298 (1.0737) | 28.668 -> 30.781 (1.0737) | None -> None (None) |
| Y18.0 | 62.427 -> 62.766 (1.0054) | 62.826 -> 63.19 (1.0058) | 62.51 -> 62.838 (1.0052) | 60.813 -> 61.182 (1.0061) | 56.89 -> 57.378 (1.0086) | 49.718 -> 50.196 (1.0096) | 35.633 -> 35.811 (1.005) | 8.197 -> 8.202 (1.0006) |
| Y23.0 | 69.173 -> 69.174 (1.0) | 69.629 -> 69.631 (1.0) | 69.294 -> 69.295 (1.0) | 67.417 -> 67.417 (1.0) | 63.075 -> 63.075 (1.0) | 55.134 -> 55.134 (1.0) | 40.333 -> 40.333 (1.0) | 17.602 -> 17.602 (1.0) |

- horizontal hull width (world Z) at world Y levels; water = -0.6 local. Warp: x1.15 about z=Y*tan15 for Y<=6, smooth to x1.0 at Y18; 1.0 for x in [-130,105]; stern end factor 0.35 at x-160; bow fades to 0 by x150 (stem/bowsprit/figurehead untouched)
- deck level (Y23) unchanged within 0.002 (float noise from hull faces that straddle Y18); DeckCabin/deck/walk footprint untouched.
- hull bottom (keel) max abs delta over 32 stations: 0.01 (the warp is horizontal)

## Hull-side collider mismatch (FLAG; colliders untouched)
- method: outer Hull surface sampled by horizontal rays (x-158..146 step 4, Y-0.5..18 step 1.5, both sides); distance outside the nearest COL_HullExt oriented box, source vs v5 at the same ray
- distance outside: source max/p95 3.161/0.308 -> v5 3.2/0.67; increase max 0.829, p95 0.538; 106 samples >0.5, 0 >1.0
- boxes with >0.5 increase: {'COL_HullExt_1_02': 0.67, 'COL_HullExt_1_06': 0.829, 'COL_HullExt_5_05': 0.565, 'COL_HullExt_5_06': 0.547, 'COL_HullExt_6_05': 0.618, 'COL_HullExt_6_06': 0.677}
- FLAG for builder: the widened visual belly sits outside the OLD v3_2 COL_HullExt volumes by up to the increase above. Colliders were NOT modified here; Studio v30 hull-side refit is authoritative and must be re-checked against this visual hull.

## Route exclusion
- method: (a) prior v3_2 zone boxes: min distance of every vertex + face centre, plus BVH triangle overlap against the zone boundaries; (b) continuous corridor capsules along the x=-120 route (half-width 4 cabin->gangplank, 6 flights, 6.27 landing for the Studio v30 12.54 exit), flight2 both yawed -30 and unyawed.
- intrusions by new/changed meshes vs source: {"zone_triangles": {}, "continuous_points": {}}
- pre-existing in source and unchanged (Hull notch/rail geometry at the gangplank, above Y18 so the warp does not move it): {"Hull": {"zone_tris": {"outrigger": 30}, "continuous_inside": {"cabin_door_tee_gangplank": 28}}}

| prior zone | min clearance new/changed (obj) |
|---|---|
| cabin_interior_spawn | 3.27 (Hull) |
| door_approach | 10.442 (Hull) |
| tee_pad_stance | 1.007 (Hull) |
| outrigger | 0.0 (Hull) |
| flight1 | 7.746 (Hull) |
| landing | 58.818 (Hull) |
| flight2_apron_yawed | 67.771 (Hull) |
| flight2_apron_unyawed | 71.98 (Hull) |
| cup_clear_r12 | 142.239 (Hull) |

| continuous corridor segment | min clearance new/changed (obj) |
|---|---|
| cabin_door_tee_gangplank | 0.0 (Hull) |
| flight1 | 3.901 (Hull) |
| landing (Studio v30 exit 12.54 wide) | 53.956 (Hull) |
| flight2_yawed | 66.644 (Hull) |
| flight2_unyawed | 66.644 (Hull) |

### New-prop clearances (min over prior zones / continuous corridor)

| prop | min prior-zone | min continuous |
|---|---|---|
| ShipV5_Bottle | 154.04 | 178.04 |
| ShipV5_BowEyes | 225.48 | 249.54 |
| ShipV5_Hammock | 123.05 | 147.05 |
| ShipV5_MastZigzag | 116.07 | 139.60 |
| ShipV5_Patches | 20.67 | 31.43 |
| ShipV5_SailEmblem | 106.26 | 130.87 |
| ShipV5_SailPatches | 105.97 | 130.06 |
| ShipV5_SheerRise | 22.49 | 38.01 |
| ShipV5_SternCurl | 28.18 | 47.29 |
| ShipV5_Telescope | 119.96 | 143.72 |
| ShipV5_YardNest | 182.85 | 206.98 |

### Hammock (specific)
- included: True; {'included': True, 'x_range': [31.8, 52.2], 'z': -11.78, 'side': -1, 'overlaps_other_meshes': 0}
- min distance to prior zones 123.05, to the continuous walkway corridor 147.05 studs; triangle overlap with every other visual mesh: 0 (posts stand on the deck slab)

## Bow eyes outside tee view
- high(-Z) eye at [136.0, 53.78, -2.56]: ray from tee eye blocked by ['Rigging', 131.22]; eye faces away from tee: True; 12.9 deg off the tee camera axis
- low(+Z) eye at [136.0, 46.53, 28.74]: ray from tee eye blocked by ['Prop_TreasureChest', 41.6]; eye faces away from tee: True; 18.5 deg off the tee camera axis

## Coplanarity (honest)
- method unchanged (0.03 / |dot|>0.995 / gap<0.02); scan list widened to 28 objects (Hull, Rigging, every warped/rebuilt/new mesh + the v3_2 list); 23475 faces.
- same list on source: 0 pairs; v5: 0 pairs; pairs not in source: 0.
- iteration history: the first build had 13 new pairs (hull/sail patch slabs and long flat emblem faces sagging into the hull or sail plane, and one emblem knob over the old v3_1 fore-sail patch). Fixed by embedding hull patches (-0.2..+0.5), sail patches (0.08..0.36, through the 0.2 sail face), tessellating the emblem to follow the sail curvature, and moving it onto bare sail (every boundary vertex ray-checked).

## Stern curl
- Prop_SternCurl kept unchanged (largest scroll components y-range/height: [([52.17, 76.34], 24.17), ([64.88, 77.69], 12.81), ([42.42, 53.17], 10.75)]).
- ShipV5_SternCurl: {'base_roblox': [-160.6, 66.08, 13.75], 'top_y': 88.53, 'height_above_base': 22.45, 'aft_most_x': -179.31, 'spiral_outer_diameter': 15.0, 'lean': 'stem leans 4.0 studs aft over 15; spiral curls aft/down (outboard)'}

## Triangles

| mesh | status | tris source | tris v5 |
|---|---|---|---|
| DeckCabin | LOCKED_unchanged | 3512 | 3512 |
| Dressing | must_unchanged_unchanged | 516 | 516 |
| Dressing_Glow | must_unchanged_unchanged | 24 | 24 |
| Hull | hull_warp_changed | 4835 | 4835 |
| Pier | must_unchanged_unchanged | 948 | 948 |
| Prop_Barnacles | hull_warp_changed | 1620 | 1620 |
| Prop_BowRaise | must_unchanged_unchanged | 1104 | 1104 |
| Prop_BulwarkFrames | must_unchanged_unchanged | 2952 | 2952 |
| Prop_BulwarkGear | must_unchanged_unchanged | 866 | 866 |
| Prop_CabinWindows | must_unchanged_unchanged | 976 | 976 |
| Prop_Cannons | must_unchanged_unchanged | 1212 | 1212 |
| Prop_CapRails | must_unchanged_unchanged | 1452 | 1452 |
| Prop_CargoCluster | must_unchanged_unchanged | 2216 | 2216 |
| Prop_Crab | must_unchanged_unchanged | 780 | 780 |
| Prop_DoorLantern | must_unchanged_unchanged | 460 | 460 |
| Prop_DoorLantern_Glow | must_unchanged_unchanged | 12 | 12 |
| Prop_Figurehead | rebuilt_in_place_changed | 2712 | 2884 |
| Prop_Flag | must_unchanged_unchanged | 760 | 760 |
| Prop_PatchPlanks | hull_warp_changed | 2420 | 2420 |
| Prop_Portholes | must_unchanged_unchanged | 1316 | 1316 |
| Prop_RoofTrim | must_unchanged_unchanged | 212 | 212 |
| Prop_RopeCoils | must_unchanged_unchanged | 1608 | 1608 |
| Prop_Seaweed | hull_warp_changed | 1376 | 1376 |
| Prop_SheerWale | must_unchanged_unchanged | 1520 | 1520 |
| Prop_SternCastle | must_unchanged_unchanged | 1280 | 1280 |
| Prop_SternCurl | must_unchanged_unchanged | 2796 | 2796 |
| Prop_SternWheel | must_unchanged_unchanged | 1640 | 1640 |
| Prop_Stovepipe | rebuilt_in_place_changed | 196 | 288 |
| Prop_TreasureChest | must_unchanged_unchanged | 980 | 980 |
| RampFlight1 | LOCKED_unchanged | 300 | 300 |
| RampFlight2 | LOCKED_unchanged | 288 | 288 |
| RampLanding | LOCKED_unchanged | 184 | 184 |
| Rigging | hull_warp_changed | 8154 | 8154 |
| RockBumper | must_unchanged_unchanged | 80 | 80 |
| ShipV5_Bottle | NEW | None | 108 |
| ShipV5_BowEyes | NEW | None | 456 |
| ShipV5_Hammock | NEW | None | 592 |
| ShipV5_MastZigzag | NEW | None | 552 |
| ShipV5_Patches | NEW | None | 1300 |
| ShipV5_SailEmblem | NEW | None | 2224 |
| ShipV5_SailPatches | NEW | None | 1152 |
| ShipV5_SheerRise | NEW | None | 888 |
| ShipV5_SternCurl | NEW | None | 876 |
| ShipV5_Telescope | NEW | None | 212 |
| ShipV5_YardNest | NEW | None | 412 |

Total visual: **60343** (source 51307; +9036, of which ShipV5_* 8772). All meshes <20k: True (largest Rigging). Collision tris 2280 (unchanged).

## Textures
- start_ship_palette.png packed=True size=[256, 256]
- new palette cells: Coral [230, 120, 100] cell 23, PatchBlue [90, 130, 170] cell 24, PatchTeal [70, 150, 140] cell 25; existing Wood / WoodDk (80,50,30) / HullWood (130,90,55) / Brass (200,160,70) cells unchanged (stern colours untouched).

## Not checked / limits
- collision NOT verified against Studio v30 (no Studio in this job); Blender colliders are stale v3_2
- no runtime/playtest validation
- props are visual-only (no colliders); ball/player pass through them
- watertightness of the warped Hull not re-proved (topology unchanged, vertices moved only)
