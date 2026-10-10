# Lantern Grove: Consolidated Prop List (for 3D Model Bot)

All sizes are approximate bounding boxes [x, y, z] in studs (1 stud = 0.3 m).
Every prop is decoration only: it has **no collision**, because collision comes from `holes.json`.
Exception: **moving parts must be separate meshes** with their pivot at the stated point, because RobloxDevBot animates them
and attaches the invisible collision blockers to them.

Priority: **P1** = needed for a playable, readable course. **P2** = strong theming. **P3** = polish.

## Moving meshes (separate parts, pivot required)

| Prop | Hole | Size (studs) | Pivot / axis | Motion | Pri |
|---|---|---|---|---|---|
| Puffball carousel bar (2 arms + toadstool hub cap) | H4 | 9 x 4 x 9 (arms 3.8 long, 0.7 thick, 1 high) | Pivot at hub centre (0,0,-21 local), axis +Y | Rotates 36 deg/s continuous | P1 |
| Mill wheel (3 paddles, rim, axle) | H6 | 1 x 7.2 x 8 (radius 3.6, paddles 7.6 wide) | Axle centre (12.5,3.6,-12.5 local), axis +Z | Rotates 30 deg/s continuous | P1 |
| Floating log on hidden rail | H7 | 5 x 0.8 x 0.8 | Centre (0,-1.2,-20.5 local), slides along +X | Ping-pong -6..+6 studs at 5 studs/s | P1 |
| Root portcullis gate | H9 | 0.8 x 1.4 x 7.4 | Base centre (6,1,-25.5 local), slides along +Y | Ping-pong 0..1.2 studs at 0.6 studs/s | P1 |
| Lantern bar (bar + 2 hanging lanterns) | H9 | 6 x 1 x 0.6 (+ lanterns hanging 1.5) | Post top (25,1,-36.5 local), axis +Y | Rotates 40 deg/s continuous | P1 |

## Static hero props

| Prop | Hole(s) | Size (studs) | Notes | Pri |
|---|---|---|---|---|
| Giant hollow golden tree | H8, H9 (skyline for all) | 34 x 60 x 34 | Trunk wraps H9's chamber and heart. An arched opening sits over the heart well. Gold/orange canopy | P1 |
| Mushroom house, large (stem tunnel) | H3 | 10 x 12 x 10 | The felt tunnel runs through the stem: opening 7 wide x 3 high, 5 deep | P1 |
| Mushroom house, medium | H3, H4 (x2) | 7–8 x 9–10 x 7–8 | Round window, door, little porch. Reuse with recolour and rotation | P1 |
| Lantern torii gate | H1 | 9 x 7 x 1.2 | Two posts outside the rails, crossbeam over the ramp, 2 paper lanterns | P1 |
| Water mill house | H6 | 9 x 10 x 8 | Timber frame. The wheel axle enters its wall | P1 |
| Arched root bridge | H5 | 3.5 x 3 x 14 | Gnarled roots under a 2.2-wide felt deck. No rails | P1 |
| Covered plank bridge | H5 | 7 x 6 x 14 | Shingle roof, lanterns at both ends. Felt runs inside | P1 |
| Three-step waterfall cascade | H7 | 8 x 14 x 10 | Rock steps with Beam water into the pool hazard | P1 |
| Firefly ring (entry, in a root knot) | H8 | 3 x 4 x 4 | Root arch with a glowing torus (ring radius 0.35 trigger) | P1 |
| Firefly ring (exit) | H8 | 2.5 x 3 x 1 | Standing torus on the green | P1 |
| Giant acorn on stump | H2 | 3 x 4 x 3 | Sits on the stump block between the chutes | P1 |
| Toadstool hub (static) | H4 | 1.4 x 2 x 1.4 | Under the carousel. Collision is the static `hub` block | P1 |
| Trunk tunnel arch (root buttress) | H9 | 7 x 5 x 8 | Over the felt tunnel | P2 |
| Lantern Knot (secret) | H9 | 1.2 x 1.2 x 0.6 | Small glowing knot-hole in the corridor floor just past the root gate (teleport entry r 0.3) + matching knot on the heart green | P2 |
| Heart-well root rim | H9 | 8 x 0.6 x 1 | Carved edge along the drop | P2 |
| Rabbit-hole rim | H2 | 3 x 0.5 x 3 | Roots and moss around the pit | P2 |
| Stream banks + water surface | H5, H6, H7 | per hazard footprint | Water plane at the hazard `center.y` | P1 |

## Set dressing (reuse everywhere)

| Prop | Size (studs) | Used at | Pri |
|---|---|---|---|
| Paper lantern, small / medium / large | 0.8 / 1.2 / 2 tall | All holes; strings over greens | P1 |
| Lantern post (timber, hook) | 0.5 x 3–3.5 x 0.5 | H2 chutes, H4 green, H7 gap | P1 |
| Lantern string (catenary of 6 lanterns) | 12 x 1 x 0.3 | H3 green entrance, H9 heart | P2 |
| Red maple tree | 10 x 16 x 10 | H1, around the map | P2 |
| Golden birch / oak | 8 x 14 x 8 | Background | P2 |
| Mossy boulder | 4 x 3 x 4 (scale 0.5–1.5) | H1, stream banks | P2 |
| Small toadstool cluster | 3 x 2.5 x 3 | H3, H8 | P2 |
| Glowing mushrooms (bioluminescent) | 2–3 x 1.5–2 x 2–3 | H8 climb, H9 heart | P2 |
| Fern clumps / red leaf bushes | 3 x 2 x 3 | Everywhere | P3 |
| Leaf piles | 2 x 0.6 x 2 | H2, paths | P3 |
| Flour sacks & crates | 2 x 1.5 x 2 | H6 | P3 |
| Squirrel hut on post | 3 x 5 x 3 | H2 | P3 |
| Stepping stones | 2 x 1 x 2 | H5 stream | P3 |
| Welcome sign post | 2 x 3 x 0.4 | H1 tee | P2 |
| Rail kit: stone block + oak cap, straight / 45° / end | 0.5 x 1 x 2–4 | All holes (visual rails) | P1 |
| Hole-number tee sign (lantern-topped) | 1 x 3 x 0.3 | Every tee | P1 |

## Reuse summary

- One **mushroom house** model with 3 scales and 2 cap colours covers H3 and H4 plus the background village.
- One **lantern** model in 3 sizes covers the whole course (day and night).
- The **firefly ring** model is shared by H8 entry, H8 exit and H9's secret knot (scaled down).
- The **rail kit** (straight, 45° and corner pieces) is shared by every hole. The H1, H6 and H9 deflector boards are the same timber plank mesh.
