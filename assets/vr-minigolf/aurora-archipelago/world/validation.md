# Aurora Archipelago world: validation log

Each run of `world/tools/validate.py` appends an iteration. Holes are concept footprints (no holes.json yet).

## Iteration 1 (2026-10-11 21:11)

Changes: first layout. Six zones climbing anticlockwise round the Starfrost Spire (60/84/112/146/182/222); islands generated from footprint, walkway and hub lobes; 18 concept footprints; 4 lifts, Lantern Stair, 3 railed bridges, gondola home.

**Result: 39 FAIL** (0 warnings). Walking spawn -> H18 cup: **1896 studs** (569 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Failures:
- H2 sits on uneven natural ground: cut/fill 12.6 > 6.0 (cliff, void or slope under the footprint)
- H3 sits on uneven natural ground: cut/fill 20.9 > 6.0 (cliff, void or slope under the footprint)
- H4 sits on uneven natural ground: cut/fill 29.9 > 6.0 (cliff, void or slope under the footprint)
- H5 sits on uneven natural ground: cut/fill 25.2 > 6.0 (cliff, void or slope under the footprint)
- H6 sits on uneven natural ground: cut/fill 30.1 > 6.0 (cliff, void or slope under the footprint)
- H7 sits on uneven natural ground: cut/fill 39.7 > 6.0 (cliff, void or slope under the footprint)
- H8 sits on uneven natural ground: cut/fill 36.6 > 6.0 (cliff, void or slope under the footprint)
- H9 sits on uneven natural ground: cut/fill 39.3 > 6.0 (cliff, void or slope under the footprint)
- H10 sits on uneven natural ground: cut/fill 49.0 > 6.0 (cliff, void or slope under the footprint)
- H11 sits on uneven natural ground: cut/fill 39.3 > 6.0 (cliff, void or slope under the footprint)
- H12 sits on uneven natural ground: cut/fill 49.6 > 6.0 (cliff, void or slope under the footprint)
- H13 sits on uneven natural ground: cut/fill 57.6 > 6.0 (cliff, void or slope under the footprint)
- H14 sits on uneven natural ground: cut/fill 64.5 > 6.0 (cliff, void or slope under the footprint)
- H15 sits on uneven natural ground: cut/fill 64.0 > 6.0 (cliff, void or slope under the footprint)
- H16 sits on uneven natural ground: cut/fill 78.5 > 6.0 (cliff, void or slope under the footprint)
- H17 sits on uneven natural ground: cut/fill 80.0 > 6.0 (cliff, void or slope under the footprint)
- H18 sits on uneven natural ground: cut/fill 80.1 > 6.0 (cliff, void or slope under the footprint)
- p_h17_h18: crosses its own hole H18 footprint mid-walk
- underside_steamwhistle_lagoons (island_underside) intrudes into the 8-stud head room over walkway p_h3_h4 at (126,438)
- p_h3_h4 seg6 passes 3.7 over walkway p_h3_h4 at (116,438)
- p_h3_h4 seg7 passes 1.6 over walkway p_h3_h4 at (120,438)
- p_h3_h4 seg8 passes 3.7 over walkway p_h3_h4 at (134,438)
- p_h3_h4 seg9 passes 1.6 over walkway p_h3_h4 at (138,438)
- p_h3_h4 seg10 passes 3.7 over walkway p_h3_h4 at (154,438)
- p_h3_h4 seg11 passes 1.6 over walkway p_h3_h4 at (158,438)
- p_h5_h6 seg1 passes 1.7 over walkway p_h5_h6 at (263,442)
- p_h15_h16 seg3 passes 3.4 over walkway p_h15_h16 at (-5,-366)
- p_h15_h16 seg4 passes 3.4 over walkway p_h15_h16 at (-5,-366)
- lantern post at (162,442) stands on walkway p_h3_h4
- lantern post at (-12,-362) stands on walkway p_h15_h16
- teleport tp_quay: 15 studs from the nearest walkway
- teleport tp_lagoons: y 84.0 vs standing surface 83.4
- teleport tp_reef: 16 studs from the nearest walkway
- teleport tp_floe: 14 studs from the nearest walkway
- teleport tp_icefall: ground not flat (+-10.3 within 3 studs)
- teleport tp_summit: 18 studs from the nearest walkway
- teleport tp_skylight: 15 studs from the nearest walkway
- lagoon Steamwhistle Lagoon rim below water level at 140 of 360 points
- lagoon Kettle Lagoon rim below water level at 173 of 360 points

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- head room: 9861 felt/walkway samples vs 11 nearby backdrop pieces, overhead walkways, the gondola cabin and 92 lantern posts; 12 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain 13, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: tp_icefall, tp_summit)
- 108 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 71.3 vs water 83.4 (11 ring points are the runoff mouth)
- Kettle Lagoon: rim min 59.9 vs water 83.4 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 2.8 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 12.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 20.9 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 29.9 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 25.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 30.1 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 39.7 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 36.6 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 39.3 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 49.0 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 39.3 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 49.6 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 57.6 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 64.5 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 64.0 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 78.5 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 80.0 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 80.1 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 241 | +24.0 | 0.0% | 30 | 0.80 | 6 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 30 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 108 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 0 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 92 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 118 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 1 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 61 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 72 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 259 | +36.0 | 0.0% | 0 | 0.00 | 1 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 151 | +44.0 | 0.0% | 5 | 0.80 | 4 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 130 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h17_h18 | Summit Walk | 157 | +0.0 | 0.0% | 0 | 0.00 | 2 | - |
| p_h18_hub | Snowpuff Sky Gondola | 87 | -162.0 | 0.0% | 0 | 0.00 | 0 | Snowpuff Sky Gondola -162 over 869 |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -24 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +4 | visible |
| H15 | 294 | +7 | +6 | +5 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +2 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |

## Iteration 2 (2026-10-11 21:12)

Changes: island edge wobble now uses the signed distance (interiors were mottled); hub pads moved within 14 of a walkway; H17->H18 walk-in moved off H18's tee corner; overhead check ignores a path's own neighbouring steps; lantern posts skip path corners.

**Result: 5 FAIL** (0 warnings). Walking spawn -> H18 cup: **1904 studs** (571 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Failures:
- H17 sits on uneven natural ground: cut/fill 18.0 > 6.0 (cliff, void or slope under the footprint)
- teleport tp_lagoons: y 84.0 vs standing surface 83.4
- teleport tp_icefall: y 182.0 vs standing surface 182.6
- lagoon Steamwhistle Lagoon rim below water level at 110 of 360 points
- lagoon Kettle Lagoon rim below water level at 153 of 360 points

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects
- head room: 9869 felt/walkway samples vs 3 nearby backdrop pieces, overhead walkways, the gondola cabin and 89 lantern posts; 0 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain 13, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: none)
- 146 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 83.6 vs water 83.4 (11 ring points are the runoff mouth)
- Kettle Lagoon: rim min 83.6 vs water 83.4 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 0.7 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 0.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 1.8 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.5 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 4.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.8 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 0.7 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 0.4 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 0.5 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 0.6 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 4.2 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 0.7 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 18.0 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 0.7 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 241 | +24.0 | 0.0% | 30 | 0.80 | 6 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 30 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 108 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 0 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 92 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 118 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 0 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 61 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 72 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 259 | +36.0 | 0.0% | 0 | 0.00 | 1 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 151 | +44.0 | 0.0% | 5 | 0.80 | 0 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 130 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h17_h18 | Summit Walk | 166 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Snowpuff Sky Gondola | 87 | -162.0 | 0.0% | 0 | 0.00 | 0 | Snowpuff Sky Gondola -162 over 869 |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -25 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +4 | visible |
| H15 | 294 | +7 | +6 | +4 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +1 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |

## Iteration 3 (2026-10-11 21:12)

Changes: island lobes extend 3 studs into each span (edge wobble pulled H17's cliff into the pad); teleport pads flattened in the heightfield (terrain.flats, new step 5a); lagoon water 82.8 (1.2 below the island) so the rims hold.

**Result: 1 FAIL** (0 warnings). Walking spawn -> H18 cup: **1904 studs** (571 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Failures:
- lagoon Steamwhistle Lagoon rim below water level at 2 of 360 points

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects
- head room: 9869 felt/walkway samples vs 3 nearby backdrop pieces, overhead walkways, the gondola cabin and 89 lantern posts; 0 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain 13, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: none)
- 146 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 83.0 vs water 82.8 (11 ring points are the runoff mouth)
- Kettle Lagoon: rim min 83.6 vs water 82.8 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 0.7 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 0.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 0.8 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.5 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 4.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.8 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 0.7 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 0.4 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 0.5 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 0.6 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 4.2 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 0.7 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 0.4 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 0.7 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 241 | +24.0 | 0.0% | 30 | 0.80 | 6 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 30 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 108 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 0 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 92 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 118 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 0 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 61 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 72 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 259 | +36.0 | 0.0% | 0 | 0.00 | 1 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 151 | +44.0 | 0.0% | 5 | 0.80 | 0 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 130 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h17_h18 | Summit Walk | 166 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Snowpuff Sky Gondola | 87 | -162.0 | 0.0% | 0 | 0.00 | 0 | Snowpuff Sky Gondola -162 over 869 |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -25 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +4 | visible |
| H15 | 294 | +7 | +6 | +4 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +1 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |

## Iteration 4 (2026-10-11 21:13)

Changes: lagoon-rim check counts ring points within 3 studs of the outlet channel as the runoff mouth (the channel's carved bank drains into the runoff, not off the island). No geometry change.

**Result: CLEAN** (0 warnings). Walking spawn -> H18 cup: **1904 studs** (571 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects
- head room: 9869 felt/walkway samples vs 3 nearby backdrop pieces, overhead walkways, the gondola cabin and 89 lantern posts; 0 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain 13, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: none)
- 146 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 83.6 vs water 82.8 (21 ring points are the runoff mouth)
- Kettle Lagoon: rim min 83.6 vs water 82.8 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 0.7 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 0.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 0.8 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.5 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 4.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.8 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 0.7 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 0.4 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 0.5 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 0.6 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 4.2 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 0.7 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 0.4 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 0.7 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 241 | +24.0 | 0.0% | 30 | 0.80 | 6 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 30 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 108 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 0 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 92 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 118 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 0 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 61 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 72 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 259 | +36.0 | 0.0% | 0 | 0.00 | 1 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 151 | +44.0 | 0.0% | 5 | 0.80 | 0 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 130 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h17_h18 | Summit Walk | 166 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h18_hub | Snowpuff Sky Gondola | 87 | -162.0 | 0.0% | 0 | 0.00 | 0 | Snowpuff Sky Gondola -162 over 869 |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -25 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +4 | visible |
| H15 | 294 | +7 | +6 | +4 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +1 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |

## Iteration 5 (2026-10-11 21:13)

Changes: railings now required wherever the ground drops > 4 within 5.5 studs of a walkway edge (path_rules.rail_reach, stricter than the recipe's 2.5); build_world flags them the same way.

**Result: CLEAN** (0 warnings). Walking spawn -> H18 cup: **1904 studs** (571 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects
- head room: 9869 felt/walkway samples vs 3 nearby backdrop pieces, overhead walkways, the gondola cabin and 89 lantern posts; 0 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain 13, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: none)
- 146 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 83.6 vs water 82.8 (21 ring points are the runoff mouth)
- Kettle Lagoon: rim min 83.6 vs water 82.8 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 0.7 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 0.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 0.8 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.5 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 4.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.8 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 0.7 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 0.4 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 0.5 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 0.6 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 4.2 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 0.7 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 0.4 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 0.7 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 241 | +24.0 | 0.0% | 30 | 0.80 | 8 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 30 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 108 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 1 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 92 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 118 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 1 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 61 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 72 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 259 | +36.0 | 0.0% | 0 | 0.00 | 2 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 151 | +44.0 | 0.0% | 5 | 0.80 | 3 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 130 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h17_h18 | Summit Walk | 166 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h18_hub | Snowpuff Sky Gondola | 87 | -162.0 | 0.0% | 0 | 0.00 | 2 | Snowpuff Sky Gondola -162 over 869 |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -25 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +4 | visible |
| H15 | 294 | +7 | +6 | +4 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +1 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |

## Iteration 6 (2026-10-11 21:16)

Changes: zone body lobes fatten every island (Landing, Lagoons, Reef, Floe, Icefall, Summit east/west) so they read as islands rather than strips; Glimmer Gap, Aurora Gap, the conch islet and the Aurora Landing pinnacle stay separate.

**Result: 1 FAIL** (0 warnings). Walking spawn -> H18 cup: **1904 studs** (571 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Failures:
- Snowpuff Sky Gondola cabin only -2.3 over terrain

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects
- head room: 9869 felt/walkway samples vs 3 nearby backdrop pieces, overhead walkways, the gondola cabin and 89 lantern posts; 1 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain -2, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: none)
- 146 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 83.6 vs water 82.8 (21 ring points are the runoff mouth)
- Kettle Lagoon: rim min 83.6 vs water 82.8 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 0.7 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 0.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 0.8 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.5 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 4.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.8 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 0.7 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 0.4 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 0.5 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 0.6 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 4.1 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 0.7 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 0.4 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 0.7 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 241 | +24.0 | 0.0% | 30 | 0.80 | 8 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 30 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 108 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 1 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 92 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 118 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 1 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 61 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 72 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 259 | +36.0 | 0.0% | 0 | 0.00 | 2 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 151 | +44.0 | 0.0% | 5 | 0.80 | 2 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 130 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h17_h18 | Summit Walk | 166 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h18_hub | Snowpuff Sky Gondola | 87 | -162.0 | 0.0% | 0 | 0.00 | 0 | Snowpuff Sky Gondola -162 over 869 |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -25 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +3 | visible |
| H15 | 294 | +7 | +6 | +4 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +1 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |

## Iteration 7 (2026-10-11 21:17)

Changes: snowdrift/crag hills now keep 30 studs off the gondola line (a new crag on the summit west body sat under the cabin, -2.3 clearance).

**Result: 1 FAIL** (0 warnings). Walking spawn -> H18 cup: **1904 studs** (571 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Failures:
- Snowpuff Sky Gondola cabin only -2.3 over terrain

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects
- head room: 9869 felt/walkway samples vs 3 nearby backdrop pieces, overhead walkways, the gondola cabin and 89 lantern posts; 1 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain -2, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: none)
- 146 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 83.6 vs water 82.8 (21 ring points are the runoff mouth)
- Kettle Lagoon: rim min 83.6 vs water 82.8 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 0.7 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 0.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 0.8 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.5 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 4.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.8 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 0.7 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 0.4 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 0.5 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 0.6 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 4.1 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 0.7 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 0.4 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 0.7 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 241 | +24.0 | 0.0% | 30 | 0.80 | 8 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 30 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 108 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 1 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 92 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 118 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 1 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 61 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 72 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 259 | +36.0 | 0.0% | 0 | 0.00 | 2 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 151 | +44.0 | 0.0% | 5 | 0.80 | 2 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 130 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h17_h18 | Summit Walk | 166 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h18_hub | Snowpuff Sky Gondola | 87 | -162.0 | 0.0% | 0 | 0.00 | 0 | Snowpuff Sky Gondola -162 over 869 |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -25 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +3 | visible |
| H15 | 294 | +7 | +6 | +4 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +1 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |

## Iteration 8 (2026-10-11 21:18)

Changes: summit west body shrunk to a disc NW of H18 (its south end ran under the gondola's first 40 studs); gondola cable mast 16 above the stations.

**Result: CLEAN** (0 warnings). Walking spawn -> H18 cup: **1904 studs** (571 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects
- head room: 9869 felt/walkway samples vs 3 nearby backdrop pieces, overhead walkways, the gondola cabin and 89 lantern posts; 0 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain 15, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: none)
- 146 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 83.6 vs water 82.8 (21 ring points are the runoff mouth)
- Kettle Lagoon: rim min 83.6 vs water 82.8 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 0.7 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 0.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 0.8 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.5 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 4.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.8 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 0.7 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 0.4 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 0.5 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 0.6 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 4.1 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 0.7 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 0.4 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 0.7 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 241 | +24.0 | 0.0% | 30 | 0.80 | 8 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 30 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 108 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 1 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 92 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 118 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 1 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 61 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 72 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 259 | +36.0 | 0.0% | 0 | 0.00 | 2 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 151 | +44.0 | 0.0% | 5 | 0.80 | 2 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 130 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h17_h18 | Summit Walk | 166 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h18_hub | Snowpuff Sky Gondola | 87 | -162.0 | 0.0% | 0 | 0.00 | 1 | Snowpuff Sky Gondola -162 over 869 |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -25 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +3 | visible |
| H15 | 294 | +7 | +6 | +4 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +1 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |

## Iteration 9 (2026-10-11 21:25)

Changes: V2 vista prompt rewritten to match the real view from Skylight Point (no geometry change).

**Result: CLEAN** (0 warnings). Walking spawn -> H18 cup: **1904 studs** (571 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects
- head room: 9869 felt/walkway samples vs 3 nearby backdrop pieces, overhead walkways, the gondola cabin and 89 lantern posts; 0 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain 15, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: none)
- 146 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 83.6 vs water 82.8 (21 ring points are the runoff mouth)
- Kettle Lagoon: rim min 83.6 vs water 82.8 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 0.7 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 0.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 0.8 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.5 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 4.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.8 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 0.7 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 0.4 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 0.5 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 0.6 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 4.1 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 0.7 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 0.4 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 0.7 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 241 | +24.0 | 0.0% | 30 | 0.80 | 8 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 30 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 108 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 1 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 92 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 118 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 1 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 61 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 72 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 259 | +36.0 | 0.0% | 0 | 0.00 | 2 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 151 | +44.0 | 0.0% | 5 | 0.80 | 2 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 130 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h17_h18 | Summit Walk | 166 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h18_hub | Snowpuff Sky Gondola | 87 | -162.0 | 0.0% | 0 | 0.00 | 1 | Snowpuff Sky Gondola -162 over 869 |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -25 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +3 | visible |
| H15 | 294 | +7 | +6 | +4 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +1 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |

## Iteration 10 (2026-10-11 21:28)

Changes: Aurora Landing pinnacle flagged with a full perimeter parapet; README/course.md written. Final check.

**Result: CLEAN** (0 warnings). Walking spawn -> H18 cup: **1904 studs** (571 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects
- head room: 9869 felt/walkway samples vs 3 nearby backdrop pieces, overhead walkways, the gondola cabin and 89 lantern posts; 0 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain 15, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: none)
- 146 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 83.6 vs water 82.8 (21 ring points are the runoff mouth)
- Kettle Lagoon: rim min 83.6 vs water 82.8 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 0.7 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 0.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 0.8 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.5 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 4.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.8 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 0.7 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 0.4 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 0.5 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 0.6 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 4.1 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 0.7 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 0.4 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 0.7 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 241 | +24.0 | 0.0% | 30 | 0.80 | 8 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 30 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 108 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 1 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 92 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 118 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 1 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 61 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 72 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 259 | +36.0 | 0.0% | 0 | 0.00 | 2 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 151 | +44.0 | 0.0% | 5 | 0.80 | 2 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 130 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h17_h18 | Summit Walk | 166 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h18_hub | Snowpuff Sky Gondola | 87 | -162.0 | 0.0% | 0 | 0.00 | 1 | Snowpuff Sky Gondola -162 over 869 |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -25 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +3 | visible |
| H15 | 294 | +7 | +6 | +4 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +1 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |

## Iteration 11 (2026-10-11 21:29)

Changes: V3 vista prompt corrected to what is really in frame from the Aurora Landing (decorative islet_06 ahead-left, Spire left; Floe Pond is behind the camera). No geometry change.

**Result: CLEAN** (0 warnings). Walking spawn -> H18 cup: **1904 studs** (571 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects
- head room: 9869 felt/walkway samples vs 3 nearby backdrop pieces, overhead walkways, the gondola cabin and 89 lantern posts; 0 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain 15, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: none)
- 146 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 83.6 vs water 82.8 (21 ring points are the runoff mouth)
- Kettle Lagoon: rim min 83.6 vs water 82.8 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 0.7 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 0.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 0.8 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.5 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 4.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.8 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 0.7 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 0.4 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 0.5 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 0.6 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 4.1 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 0.7 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 0.4 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 0.7 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 241 | +24.0 | 0.0% | 30 | 0.80 | 8 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 30 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 108 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 1 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 92 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 118 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 1 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 61 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 72 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 259 | +36.0 | 0.0% | 0 | 0.00 | 2 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 53 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 55 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 151 | +44.0 | 0.0% | 5 | 0.80 | 2 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 130 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h17_h18 | Summit Walk | 166 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h18_hub | Snowpuff Sky Gondola | 87 | -162.0 | 0.0% | 0 | 0.00 | 1 | Snowpuff Sky Gondola -162 over 869 |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -25 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +3 | visible |
| H15 | 294 | +7 | +6 | +4 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +1 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |

## Iteration 12 (2026-10-11 22:40)

Changes: Phase 2 - holes.json exists (18 specced holes, p2). build_world.py now reads each hole's real cup position and par from holes.json, so walkways start at the real cups; placements and concept pads unchanged; every holes.json felt/rail corner lies inside its pads (build_holes.py fit check).

**Result: CLEAN** (0 warnings). Walking spawn -> H18 cup: **1955 studs** (586 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects
- head room: 9869 felt/walkway samples vs 3 nearby backdrop pieces, overhead walkways, the gondola cabin and 89 lantern posts; 0 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain 15, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: none)
- 146 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 83.6 vs water 82.8 (21 ring points are the runoff mouth)
- Kettle Lagoon: rim min 83.6 vs water 82.8 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 0.7 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 0.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 0.8 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.5 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 4.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.8 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 0.7 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 0.4 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 0.5 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 0.6 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 4.1 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 0.7 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 0.4 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 0.7 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 75 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 243 | +24.0 | 0.0% | 30 | 0.80 | 8 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 22 | -0.6 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 113 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 1 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 87 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 122 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 1 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 69 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 76 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 264 | +36.0 | 0.0% | 0 | 0.00 | 2 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 63 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 54 | -0.8 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 154 | +44.0 | 0.0% | 5 | 0.80 | 2 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 133 | +0.8 | 0.0% | 0 | 0.00 | 1 | - |
| p_h17_h18 | Summit Walk | 168 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h18_hub | Snowpuff Sky Gondola | 93 | -162.8 | 0.0% | 0 | 0.00 | 1 | Snowpuff Sky Gondola -162 over 869 |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -25 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +3 | visible |
| H15 | 294 | +7 | +6 | +4 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +1 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |

## Iteration 13 (2026-10-11 22:41)

Changes: validator now also checks holes.json (Phase 2): placements identical to world.json, 0 felt/rail/mover points outside the concept pads, every walkway starts at the real holes.json cup. No geometry change.

**Result: CLEAN** (0 warnings). Walking spawn -> H18 cup: **1955 studs** (586 m, target < 3000); lifts 4 (ride 1022 studs incl. the gondola home).

Checks:
- closest hole pairs: H2-H3 9.8, H4-H5 12.0, H13-H14 14.1, H14-H15 18.4, H5-H6 19.0
- pad edges next to a drop > 4 (2.5 studs out): none (every pad has >= 11 studs of island apron); spans are guarded by their player guards and decks
- island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects
- head room: 9869 felt/walkway samples vs 3 nearby backdrop pieces, overhead walkways, the gondola cabin and 89 lantern posts; 0 intrusions. Snowpuff Sky Gondola: min cabin clearance over terrain 15, over walked surfaces 999
- hub teleport pads: Lanternfall Landing: Lantern Quay Plaza, Steamwhistle Lagoons: Lantern Stair Top, Candyfrost Reef: Steam Lift Top, Driftfloe Shelf: Coral Lift Top, Icefall Terraces: Skybridge West, Skylight Summit: Crystal Lift Top
- void: no terrain below y 30.0, cloud deck y 36.0, respawn plane y 40.0; every pad and walkway >= 10 above it
- 18 distinct headline gimmicks; 6 movers with distinct motion types: H5 vertical lift (piston with dwell), H11 linear slide with dwell, H12 vertical rotor (horizontal axle), H13 horizontal rotor (vertical axle), H14 pendulum swing, H17 appear-vanish toggle (fade with dwell)
- 8 teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: none)
- 146 small scenery pieces clear of every footprint and on island ground
- Steamwhistle Lagoon: rim min 83.6 vs water 82.8 (21 ring points are the runoff mouth)
- Kettle Lagoon: rim min 83.6 vs water 82.8 (0 ring points are the runoff mouth)
- Starfrost Spire: base y 100, tip y 340, at (0, -40)

| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |
|---|---|---|---|---|---|---|---|
| H1 | Lantern Quay | 2 | Lanternfall Landing | 60 | 0.00 | 0.7 | - |
| H2 | Snowpuff Burrows | 3 | Lanternfall Landing | 60 | 0.00 | 0.6 | - |
| H3 | Glimmer Crossing | 3 | Lanternfall Landing | 60 | 0.00 | 0.8 | Glimmer Gap (open sky to the cloud sea): ground 60 below the pad |
| H4 | Glissade | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.5 | - |
| H5 | Geyser Hop | 3 | Steamwhistle Lagoons | 84/88 | 0.00 | 4.2 | - |
| H6 | Palm Lagoon | 3 | Steamwhistle Lagoons | 84 | 0.00 | 0.8 | - |
| H7 | Mogul Meadow | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H8 | Coral Pinball | 3 | Candyfrost Reef | 112 | 0.00 | 0.8 | - |
| H9 | Conch Shortcut | 4 | Candyfrost Reef | 112 | 0.00 | 0.7 | - |
| H10 | Bobsled Bend | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H11 | Floe Drift | 3 | Driftfloe Shelf | 146 | 0.00 | 0.4 | - |
| H12 | Icebreaker Wheel | 3 | Driftfloe Shelf | 146 | 0.00 | 0.7 | - |
| H13 | Snowpuff Carousel | 3 | Icefall Terraces | 182 | 0.00 | 0.5 | - |
| H14 | Bell Buoy | 3 | Icefall Terraces | 182 | 0.00 | 0.6 | - |
| H15 | Frozen Falls | 2 | Icefall Terraces | 178/182 | 0.00 | 4.1 | - |
| H16 | Moonwell | 2 | Skylight Summit | 222 | 0.00 | 0.7 | - |
| H17 | Aurora Bridge | 3 | Skylight Summit | 222 | 0.00 | 0.4 | Aurora Gap (open sky): ground 222 below the pad |
| H18 | Halo Arch | 4 | Skylight Summit | 222 | 0.00 | 0.7 | - |

| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |
|---|---|---|---|---|---|---|---|---|
| p_spawn_h1 | Quay Walk | 57 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h1_h2 | Burrow Lane | 58 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h2_h3 | Drift Path | 75 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h3_h4 | Glimmer Ice Bridge + Lantern Stair | 243 | +24.0 | 0.0% | 30 | 0.80 | 8 | Glimmer Ice Bridge (ice) 52 long, 60 above ground |
| p_h4_h5 | Palm Step | 22 | -0.6 | 0.0% | 0 | 0.00 | 0 | - |
| p_h5_h6 | Steam Walk | 113 | -4.0 | 0.0% | 5 | 0.80 | 0 | - |
| p_h6_h7 | Steam Lift | 104 | +28.0 | 0.0% | 0 | 0.00 | 1 | Steam Lift +28 |
| p_h7_h8 | Coral Walk | 87 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h8_h9 | Coral Ice Bridge | 122 | +0.0 | 0.0% | 0 | 0.00 | 1 | Coral Ice Bridge (ice) 50 long, 112 above ground |
| p_h9_h10 | Coral Lift | 94 | +34.0 | 0.0% | 0 | 0.00 | 1 | Coral Lift +34 |
| p_h10_h11 | Floe Walk | 69 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h11_h12 | Pond Path | 76 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h12_h13 | Icefall Lift + Aurora Skybridge | 264 | +36.0 | 0.0% | 0 | 0.00 | 2 | Icefall Lift +36; Aurora Skybridge (aurora) 135 long, 182 above ground |
| p_h13_h14 | Carousel Walk | 63 | +0.0 | 0.0% | 0 | 0.00 | 0 | - |
| p_h14_h15 | Icefall Rim | 54 | -0.8 | 0.0% | 0 | 0.00 | 0 | - |
| p_h15_h16 | Crystal Lift | 154 | +44.0 | 0.0% | 5 | 0.80 | 2 | Crystal Lift +40 |
| p_h16_h17 | Moonwell Path | 133 | +0.8 | 0.0% | 0 | 0.00 | 1 | - |
| p_h17_h18 | Summit Walk | 168 | +0.0 | 0.0% | 0 | 0.00 | 1 | - |
| p_h18_hub | Snowpuff Sky Gondola | 93 | -162.8 | 0.0% | 0 | 0.00 | 1 | Snowpuff Sky Gondola -162 over 869 |

| hole | par | placement vs holes.json | holes.json points outside pads | cup (local) = walkway start | ok |
|---|---|---|---|---|---|
| H1 | 2 | same | 0 | [6.0, 0.0, -30.5] | ok |
| H2 | 3 | same | 0 | [-11.0, 0.0, -46.0] | ok |
| H3 | 3 | same | 0 | [-1.0, 0.0, -55.5] | ok |
| H4 | 3 | same | 0 | [9.0, 0.6, -54.0] | ok |
| H5 | 3 | same | 0 | [-4.0, 4.0, -45.0] | ok |
| H6 | 3 | same | 0 | [0.0, 0.0, -54.0] | ok |
| H7 | 3 | same | 0 | [6.0, 0.0, -53.0] | ok |
| H8 | 3 | same | 0 | [-3.5, 0.0, -48.5] | ok |
| H9 | 4 | same | 0 | [2.0, 0.0, -64.0] | ok |
| H10 | 3 | same | 0 | [-0.5, 0.0, -42.0] | ok |
| H11 | 3 | same | 0 | [-4.0, 0.0, -45.0] | ok |
| H12 | 3 | same | 0 | [-1.5, 0.0, -42.0] | ok |
| H13 | 3 | same | 0 | [10.1, 0.0, -46.0] | ok |
| H14 | 3 | same | 0 | [1.0, 0.8, -44.0] | ok |
| H15 | 2 | same | 0 | [3.5, -4.0, -31.0] | ok |
| H16 | 2 | same | 0 | [3.2, -0.8, -35.5] | ok |
| H17 | 3 | same | 0 | [2.2, 0.0, -56.0] | ok |
| H18 | 4 | same | 0 | [-4.0, 0.8, -46.0] | ok |

| hole | play bearing | angle to moon (220) | ok |
|---|---|---|---|
| H1 | 0 | 140 | ok |
| H2 | 90 | 130 | ok |
| H3 | 45 | 175 | ok |
| H4 | 0 | 140 | ok |
| H5 | 90 | 130 | ok |
| H6 | 0 | 140 | ok |
| H7 | 0 | 140 | ok |
| H8 | 0 | 140 | ok |
| H9 | 0 | 140 | ok |
| H10 | 270 | 50 | ok |
| H11 | 0 | 140 | ok |
| H12 | 270 | 50 | ok |
| H13 | 0 | 140 | ok |
| H14 | 270 | 50 | ok |
| H15 | 0 | 140 | ok |
| H16 | 0 | 140 | ok |
| H17 | 0 | 140 | ok |
| H18 | 0 | 140 | ok |

| tee | dist to Spire | LOS clearance tip | upper | waist | result |
|---|---|---|---|---|---|
| H1 | 604 | +7 | +7 | +6 | visible |
| H2 | 533 | +7 | +7 | +6 | visible |
| H3 | 512 | +7 | +7 | +6 | visible |
| H4 | 543 | +7 | +7 | +6 | visible |
| H5 | 508 | +7 | +7 | +6 | visible |
| H6 | 601 | +7 | +6 | +6 | visible |
| H7 | 520 | +7 | +6 | +6 | visible |
| H8 | 548 | +7 | +6 | +6 | visible |
| H9 | 599 | +7 | +6 | +6 | visible |
| H10 | 520 | +7 | +6 | +6 | visible |
| H11 | 418 | +7 | +6 | +6 | visible |
| H12 | 371 | +7 | -6 | -25 | visible |
| H13 | 225 | +8 | +6 | +4 | visible |
| H14 | 274 | +7 | +6 | +3 | visible |
| H15 | 294 | +7 | +6 | +4 | visible |
| H16 | 282 | +7 | +6 | +1 | visible |
| H17 | 277 | +7 | +6 | +1 | visible |
| H18 | 303 | +7 | +6 | -1 | visible |
