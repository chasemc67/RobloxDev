# Route QA - Prop_SternWheel / Prop_TreasureChest vs continuous cabin->gangplank route

**Verdict: PASS** - both visual-only props are outside the complete swept route corridor. **No model change** (no v3_3 written; v3_2 previews/exports stay final).
Source `source_v3_2.blend` sha256 before = after = `9d75ae96912ff0ca4b7a97b5b6287e3cc10d55edefa0c2719c6cfec2dd0bf333` (unchanged: True). Blender 5.2.2 LTS headless, read-only (never saved).

![top-down](route_topdown.png)

## Results (main corridor, conservative full XZ projection of every triangle)

| prop | min clearance to corridor | closest segment | centreline dist | half-width | closest prop pt (x,z) | closest centreline pt | clipped y23.5-30 | conservative 12 | unyawed F2 | bbox ref |
|---|---|---|---|---|---|---|---|---|---|---|
| Prop_SternWheel | **44.907** | Door->Tee1 | 48.907 | 4.0 | [-71.0925, 32.1947] | [-120.0, 32.1947] | 44.907 | 38.598 (AREA:COL_Outrigger) | 44.907 | 44.907 |
| Prop_TreasureChest | **31.210** | Tee1->RampStart | 35.210 | 4.0 | [-84.7904, 38.9401] | [-120.0, 38.9401] | 31.210 | 24.505 (AREA:COL_Outrigger) | 31.210 | 31.210 |

Prop bboxes (Roblox): Wheel [-71.0925, 23.9, 24.0286] .. [-66.78, 38.6714, 36.9714]; Chest [-84.7904, 23.85, 34.371] .. [-75.1744, 32.8326, 42.9202].
Nearest source vertex to the closest point: Wheel Roblox [-71.0925, 28.1085, 32.1947] (Blender [-71.09249877929688, -32.194698333740234, 28.10849952697754]), Chest Roblox [-84.7904, 24.0, 38.9401] (Blender [-84.79039764404297, -38.940101623535156, 24.0]).
The wheel's closest point is its west rim edge x=-71.09 (rim overhang included); the chest's is its west side x=-84.79 at deck level. Both are ~35-49 studs east of the x=-120 route axis: the "centred" look in the tee view is perspective only (see diagram).

### Per-segment distances
**Prop_SternWheel**

| segment / area | half-width | centreline (or area) dist | clearance |
|---|---|---|---|
| Spawn->Door | 4.0 | 48.924 | 44.924 |
| Door->Tee1 | 4.0 | 48.907 | 44.907 |
| Tee1->RampStart | 4.0 | 48.924 | 44.924 |
| RampStart->Flight1_bottom | 6.0 | 55.421 | 49.421 |
| Flight1_bottom->Landing_centre | 6.0 | 91.866 | 85.866 |
| Landing_centre->Landing_exit | 6.0 | 98.498 | 92.498 |
| Landing_exit->Flight2_axis6 | 6.0 | 105.436 | 99.436 |
| Flight2_axis6->Flight2_bottom | 6.0 | 112.439 | 106.439 |
| Flight2_bottom->Apron_centre | 6.0 | 158.426 | 152.426 |
| AREA:COL_Landing_FloorA | 0.0 | 87.400 | 87.400 |
| AREA:COL_Landing_FloorB | 0.0 | 98.600 | 98.600 |
| AREA:COL_Flight2_Surface | 0.0 | 105.952 | 105.952 |
| AREA:COL_Flight2_Apron | 0.0 | 157.895 | 157.895 |

**Prop_TreasureChest**

| segment / area | half-width | centreline (or area) dist | clearance |
|---|---|---|---|
| Spawn->Door | 4.0 | 38.232 | 34.232 |
| Door->Tee1 | 4.0 | 35.263 | 31.263 |
| Tee1->RampStart | 4.0 | 35.210 | 31.210 |
| RampStart->Flight1_bottom | 6.0 | 41.937 | 35.937 |
| Flight1_bottom->Landing_centre | 6.0 | 81.372 | 75.372 |
| Landing_centre->Landing_exit | 6.0 | 88.362 | 82.362 |
| Landing_exit->Flight2_axis6 | 6.0 | 95.216 | 89.216 |
| Flight2_axis6->Flight2_bottom | 6.0 | 101.988 | 95.988 |
| Flight2_bottom->Apron_centre | 6.0 | 147.945 | 141.945 |
| AREA:COL_Landing_FloorA | 0.0 | 77.635 | 77.635 |
| AREA:COL_Landing_FloorB | 0.0 | 89.374 | 89.374 |
| AREA:COL_Flight2_Surface | 0.0 | 95.406 | 95.406 |
| AREA:COL_Flight2_Apron | 0.0 | 147.349 | 147.349 |

## Intended walking route (not the whole deck)
Spawn (-120,24,2.5) inside the cabin -> straight +Z through the 8-stud door (-120,24,24) -> Tee1 (-120,24.4,37) on deck -> through the low-side bulwark notch onto the outrigger -> RampStart (-120,24,62.5) -> Flight1 down its axis x=-120 to its bottom edge z=114.5 (COL_Flight1_Surface) -> landing centre (-120,122.25) -> SW turn to the landing's south exit midpoint (-124,127.95) (between the end of Landing_RailW at (-126.5,126.9) and the start of Landing_RailS at (-121.5,129.0)) -> onto the Flight2 axis 6 studs below its mouth (first station with full 12-stud rail clearance) -> Flight2 (yawed -30 deg about its origin (-126.7,12,127.5), length 52 = COL_Flight2_Surface) -> apron centre (COL_Flight2_Apron, yawed).
Corridor = union of swept capsules over **every** centreline segment (r=4 i.e. 8 wide in cabin/door/deck; r=6 i.e. 12 wide on outrigger-to-Flight1, landing, Flight2, apron) **plus** the full walkable footprints of COL_Landing_FloorA/B, COL_Flight2_Surface and COL_Flight2_Apron. Conservative variant: r=6 (12 wide) on cabin/deck too (ignores the 8-wide door wall) plus the whole COL_Outrigger platform and COL_Flight1_Surface as areas.
Player capsule radius chosen = 2.0 studs: 8-wide route leaves 4.0 centreline margin; door 8.0 leaves 2.0 per side.

### Joints (union continuity)
| joint | endpoint gap | disc test | turn deg |
|---|---|---|---|
| Door | 0.0 | r4.0 disc in prev True / next True | 0.0 |
| Tee1 | 0.0 | r4.0 disc in prev True / next True | 0.0 |
| RampStart | 0.0 | r4.0 disc in prev True / next True | 0.0 |
| Flight1_bottom | 0.0 | r6.0 disc in prev True / next True | 0.0 |
| Landing_centre | 0.0 | r6.0 disc in prev True / next True | 35.06 |
| Landing_exit | 0.0 | r6.0 disc in prev True / next True | 15.16 |
| Flight2_axis6 | 0.0 | r6.0 disc in prev True / next True | -20.22 |
| Flight2_bottom | 0.0 | r6.0 disc in prev True / next True | 0.0 |

Landing points on the landing floor: [{'point': 'Flight1_bottom', 'on_landing_floor': True, 'dist_to_landing_floor': 0.0}, {'point': 'Landing_centre', 'on_landing_floor': True, 'dist_to_landing_floor': 0.0}, {'point': 'Landing_exit', 'on_landing_floor': False, 'dist_to_landing_floor': 1.25}] (the exit midpoint lies 1.25 past FloorA's edge, on COL_Flight2_Surface / FloorB - walk hit continuous; 3 samples there hit only the Flight2 surface, which overlaps the landing floors: footprint gap 0.0).

### Walk-surface collider joints (footprint gap / top y)
| a | b | gap | top y |
|---|---|---|---|
| COL_CabinFloor | COL_Deck_00 | 0.0 | [24.0, 24.0] |
| COL_Outrigger | COL_Deck_01 | 0.0 | [24.0, 24.0] |
| COL_Outrigger | COL_Flight1_Surface | 0.0 | [24.0, 24.0] |
| COL_Flight1_Surface | COL_Landing_FloorA | 0.0 | [24.0, 12.0] |
| COL_Flight1_Surface | COL_Landing_FloorB | 12.0 | [24.0, 12.0] |
| COL_Landing_FloorA | COL_Landing_FloorB | 0.0 | [12.0, 12.0] |
| COL_Landing_FloorA | COL_Flight2_Surface | 0.0 | [12.0, 12.0] |
| COL_Landing_FloorB | COL_Flight2_Surface | 0.0 | [12.0, 12.0] |
| COL_Flight2_Surface | COL_Flight2_Apron | 0.0 | [12.0, 0.2] |

## Actual clear walking width along the route (horizontal rays perpendicular to the centreline at walk+0.5/2.5/4.5, every 0.5 stud)
| segment | section | min clear width colliders (by) | at xz | min clear width visual | walk samples / no-walk-hit | walk y | max step/0.5 |
|---|---|---|---|---|---|---|---|
| Spawn->Door | cabin | 8.00 (COL_CabinWall_FrontR / COL_CabinWall_FrontL) | [-120.0, 22.5] | 8.00 | 44 / 0 | [24.0, 24.0] | 0.0 |
| Door->Tee1 | deck | 8.00 (COL_CabinWall_FrontR / COL_CabinWall_FrontL) | [-120.0, 24.0] | 8.00 | 27 / 0 | [24.0, 24.0] | 0.0 |
| Tee1->RampStart | deck | 9.70 (COL_PlatRail_E / COL_HullExt_0_07) | [-120.0, 48.5] | 11.20 | 52 / 0 | [24.0, 24.0] | 0.0 |
| RampStart->Flight1_bottom | flight1 | 12.00 (COL_Flight1_RailE / COL_Flight1_RailW) | [-120.0, 63.0] | 11.20 | 105 / 0 | [12.0, 24.0] | 0.2308 |
| Flight1_bottom->Landing_centre | landing | 12.00 (COL_Flight1_RailE / COL_Flight1_RailW) | [-120.0, 114.5] | 12.00 | 16 / 0 | [12.0, 12.0] | 0.0 |
| Landing_centre->Landing_exit | landing_turn | 6.11 (COL_Landing_RailS / COL_Landing_RailW) | [-123.734, 127.571] | 4.68 | 14 / 3 | [12.0, 12.0] | 0.0 |
| Landing_exit->Flight2_axis6 | landing_turn | 6.74 (COL_Flight2_RailE / COL_Landing_RailW) | [-124.768, 128.59] | 5.16 | 15 / 2 | [10.727, 11.903] | 0.1065 |
| Flight2_axis6->Flight2_bottom | flight2 | 12.00 (COL_Flight2_RailE / COL_Flight2_RailW) | [-129.7, 132.696] | 11.20 | 93 / 0 | [0.2, 10.639] | 0.1135 |
| Flight2_bottom->Apron_centre | apron | 12.00 (COL_Flight2_RailE / COL_Flight2_RailW) | [-152.7, 172.533] | 12.00 | 16 / 0 | [0.2, 0.2] | 0.0 |

Door opening measured directly (rays +-X, z 22-24, heights 0.5-8.5): colliders 8.0, DeckCabin visual 8.0 -> door is 8, not 12 (12 is not demanded through the wall).
Landing exit opening (collider footprint gaps, Studio yawed): [{'west': 'COL_Landing_RailW', 'east': 'COL_Landing_RailS', 'gap': 5.4231}, {'west': 'COL_Landing_RailW', 'east': 'COL_Landing_RailE', 'gap': 13.0}, {'west': 'COL_Landing_RailW', 'east': 'COL_Flight2_RailE', 'gap': 6.1517}, {'west': 'COL_Flight2_RailW', 'east': 'COL_Landing_RailS', 'gap': 11.3208}, {'west': 'COL_Flight2_RailW', 'east': 'COL_Landing_RailE', 'gap': 18.363}, {'west': 'COL_Flight2_RailW', 'east': 'COL_Flight2_RailE', 'gap': 12.0}]; min 5.4231. Flight1 rails inner clear 12.0, Flight2 rails 12.0, landing north entry 12.1.

**Widths established:** cabin->door->tee **8** (door bottleneck); Flight1 **12**; Flight2+apron **12**; landing entry 12.1.
**Not established:** (a) landing exit -> Flight2: collider opening **5.42** (> capsule diameter 4, so passable, but neither 8 nor 12; visual ray chord 3.8-4.7 at RampLanding posts, upper bound); (b) **tee -> RampStart through the bulwark notch: COL_HullExt_0_07 / COL_HullExt_1_07** (tilted 2.5-thick hull-skin slabs, x -160.1..-120.3 and -120.5..-80.7, y 13.6..34.6, z 38.9..57.8) occupy the walk band y 24.1-30 over x -128..-112, z 47-55.5 (inside-volume test, 1-stud grid; only a 0.2-stud sliver at x -120.5..-120.3 is free). Visually the notch is open (18.8 wide between the DeckCabin/hull notch faces). These are locked/byte-identical-to-v3_1 colliders, unrelated to the two props, and were **not** changed here - flag for the parent/collision owner and Studio runtime check.

## Collider audit (props are visual only)
- 190 colliders. Collider names matching the props: Wheel [], Chest []. Props in 'Props' collection, not 'Collision'; no parent/children/modifiers.
- Colliders whose footprint or 3D box overlaps the props (actual geometry overlap tested with BVH):

| prop | collider | XZ overlap | 3D AABB overlap | tri overlaps | collider y | prop y |
|---|---|---|---|---|---|---|
| Prop_SternWheel | COL_Deck_05 | True | True | 34 | [22.0, 24.0] | [23.9, 38.6714] |
| Prop_SternWheel | COL_HullExt_2_05 | True | False | 0 | [-2.9357, 4.2147] | [23.9, 38.6714] |
| Prop_SternWheel | COL_HullExt_2_06 | True | False | 0 | [2.0862, 15.324] | [23.9, 38.6714] |
| Prop_TreasureChest | COL_Deck_04 | True | True | 289 | [22.0, 24.0] | [23.85, 32.8326] |
| Prop_TreasureChest | COL_Deck_05 | True | True | 80 | [22.0, 24.0] | [23.85, 32.8326] |
| Prop_TreasureChest | COL_HullExt_1_06 | True | False | 0 | [2.0031, 15.4547] | [23.85, 32.8326] |
| Prop_TreasureChest | COL_HullExt_1_07 | True | True | 0 | [13.5773, 33.8069] | [23.85, 32.8326] |
| Prop_TreasureChest | COL_HullExt_2_06 | True | False | 0 | [2.0862, 15.324] | [23.85, 32.8326] |
| Prop_TreasureChest | COL_HullExt_2_07 | True | True | 0 | [13.4419, 33.335] | [23.85, 32.8326] |

Interpretation: COL_Deck_04/05 are the deck floor slabs (top y 24.0) that the props stand on; the props' bases sink 0.10-0.15 into the deck (prop min y 23.9 / 23.85), which is what the triangle overlaps are. COL_HullExt_1_07/2_07 overlap the chest's 3D box but have 0 triangle overlaps (hull skin outboard/below). No collider exists for, or encloses, either prop; nothing to remove; no collider added.

## Method
1. Opened source_v3_2.blend read-only (`--factory-startup`, never saved; `bpy.data.is_dirty` False at end; sha256 re-verified).
2. Prop geometry: evaluated mesh loop triangles in world space, mapped to Roblox (x, y, z) = (bx, bz, -by); every triangle projected to XZ (wheel 1640 tris incl. rim, chest 980 incl. open lid).
3. Exact 2D distance per triangle to every route segment: segment-vs-triangle-edge distance with proper intersection test (orientation predicates) plus segment-endpoint-in-triangle test; clearance = distance - corridor half-width (capsule). Area elements (landing floors, Flight2 surface, apron, conservative outrigger/Flight1): triangle-vs-convex-polygon distance with edge intersection and two-way containment tests. Min taken over the union of all segments and areas.
4. Route points from source anchors (Spawn/Tee1/RampStart empties), DOORX/cabin front wall, and collider boxes (COL_Flight1_Surface end, landing floors, landing rails, COL_Flight2_Surface length, COL_Flight2_Apron); Flight2 + its colliders yawed -30 deg about RampFlight2's origin (manifest placement_note / prior fitcheck f2_dist); unyawed (as exported) evaluated too.
5. Walk continuity: downward ray every 0.5 stud along the centreline against walk colliders and visual ramps/deck; lateral clear width by horizontal rays (colliders and visual meshes separately) at 3 heights; door opening by direct rays; walk-collider footprint gaps; HullExt walk-band inside-volume probe.
6. Diagram from the same JSON (matplotlib, system Python).

## Limits
- No Studio/runtime validation; Humanoid behaviour on the HullExt slab and through the 5.42 landing exit not tested.
- Height clipping band y23.5-30 is deck-level only (props stand on the deck); full projection is the reported main result (identical minima here).
- Widths are ray chords perpendicular to the centreline (>= true gap at oblique openings); the landing exit gap is taken from collider footprint polygon distances.
- HullExt occupancy probe is a 1-stud x / 0.5-stud z grid at 6 heights.
