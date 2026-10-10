# Lantern Grove: Consolidated Prop List (for 3D Model Bot)

All sizes are approximate bounding boxes [x, y, z] in studs (1 stud = 0.3 m).
Every prop is decoration only: it has **no collision**, because collision comes from `holes.json`.
Exception: **moving parts must be separate meshes** with their pivot at the stated point, because RobloxDevBot animates them
and attaches the invisible collision blockers to them.

Priority: **P1** = needed for a playable, readable course. **P2** = strong theming. **P3** = polish.

## Moving meshes (separate parts, pivot required)

holes.json is the source of truth for all pivots and motion; this table mirrors it (updated 2026-10-10 for playtest Round 5;
**bold** = changed or new in Round 5).

| Prop | Hole | Size (studs) | Pivot / axis | Motion | Pri |
|---|---|---|---|---|---|
| Puffball carousel bar (2 **padded** arms + toadstool hub cap) | H4 | **6 x 4 x 6 (arms 2.3 long from r 0.7 to 3.0, 0.7 thick, 1 high)** | Pivot at hub centre (0,0,-21 local), axis +Y | Rotates **30 deg/s** continuous. Arms are soft puffball bumpers (restitution 0.65) | P1 |
| Mill wheel (2 opposed paddles, rim, axle) | H6 | 1 x 7.2 x 8 (radius 3.6, paddles 7.6 wide) | Axle centre (7.5,3.6,-8.5 local), axis +Z | Rotates 30 deg/s continuous | P1 |
| Sliding root door | H8 | 0.7 x 1 x 3.2 | Centre (4.75,0,-11.5 local), slides along +Z | Ping-pong **-3.5..+3.5** studs at 2 studs/s (7 s cycle). At the ends it slides **into pockets in the root-knot walls** (passes through the junction rail lines at z -8 / -15 by up to 1.6) | P1 |
| Floating log on hidden rail | H7 | 5 x 0.8 x 0.8 | Centre (0,-1.2,-20.5 local), slides along +X | Ping-pong **-7..+7** studs at 5 studs/s: **log ends stop 0.5 stud short of each rail line (x = ±10)** | P1 |
| Root portcullis gate | H9 | 0.8 x 1.4 x 7.4 | Base centre (6,1,-25.5 local), slides along +Y | Ping-pong **0..1.8 studs at 0.9 studs/s** (same 4 s cycle, open ~70%) | P1 |
| **Great lantern pendulum (NEW, replaces the lantern bar + post)** | H9 | Bob (lantern body) **1.6 x 1.8 x 1.0** (x across the swing, y up, z along the chain axis); chain 7 long from the hinge to the bob centre | **Hinge (22, 8.96, -38.5 local), axis +Z** (swings east-west in the local x-y plane). Model the pivot at the hinge; bob centre 7.0 below it | **Swing: angle(t) = 35° x sin(360°·t / 4 s)**, peak 55 deg/s at the bottom. Bob bottom hangs 0.06 above the felt at rest; it can hit a ball within ±16° of the bottom and lifts clear near the ends | P1 |

## Static hero props

| Prop | Hole(s) | Size (studs) | Notes | Pri |
|---|---|---|---|---|
| Giant hollow golden tree | H8, H9 (skyline for all) | 34 x 60 x 34 | Trunk wraps H9's chamber and heart. An arched opening sits over the heart well. Gold/orange canopy | P1 |
| Mushroom house, large (stem tunnel) | H3 | 10 x 12 x 10 | The felt tunnel runs through the stem: opening 7 wide x 3 high, 5 deep | P1 |
| Mushroom house, medium | H3, H4 (x2) | 7–8 x 9–10 x 7–8 | Round window, door, little porch. Reuse with recolour and rotation | P1 |
| Lantern torii gate | H1 | 9 x 7 x 1.2 | Two posts outside the rails, crossbeam over the ramp, 2 paper lanterns | P1 |
| Water mill house | H6 | 9 x 10 x 8 | Timber frame. The wheel axle enters its wall | P1 |
| Arched root bridge | H5 | 3.5 x 3 x 14 | Gnarled roots under a 1.8-wide felt deck. No rails | P1 |
| Covered plank bridge | H5 | 7 x 6 x 14 | Shingle roof, lanterns at both ends. Felt runs inside | P1 |
| Three-step waterfall cascade | H7 | 8 x 14 x 10 | Rock steps with Beam water into the pool hazard | P1 |
| Firefly ring (entry, in a root knot) | H8 | 3 x 4 x 4 | Root arch with a glowing torus (**ring radius 0.55 trigger**, glow disc 1.1 across) | P1 |
| Firefly ring (exit) | H8 | 2.5 x 3 x 1 | Standing torus on the green, **moved to the north-east corner (9, 1.5, -47 local)** | P1 |
| Giant acorn on stump | H2 | 3 x 4 x 3 | Sits on the stump block between the chutes | P1 |
| Toadstool hub (static) | H4 | 1.4 x 2 x 1.4 | Under the carousel. Collision is the static `hub` block | P1 |
| Trunk tunnel arch (root buttress) | H9 | 7 x 5 x 8 | Over the felt tunnel | P2 |
| Lantern Knot (secret) | H9 | 1.2 x 1.2 x 0.6 | Small glowing knot-hole in the corridor floor at (6.5, 1.0, -23.0): 0.5 past the root gate, 1 in from the south rail (teleport entry r 0.3) + matching exit knot 1.0 x 0.3 x 1.0 in the heart green's north-west corner (15, -0.8, -52) | P2 |
| Heart-well root rim | H9 | 8 x 0.6 x 1 | Carved edge along the drop | P2 |
| Rabbit-hole rim | H2 | 3 x 0.5 x 3 | Roots and moss around the pit | P2 |
| Stream banks + water surface | H5, H6, H7 | per hazard footprint | Water plane at the hazard `center.y` | P1 |

## New in Round 5 (static, decoration only)

| Prop | Hole(s) | Size (studs) | Placement (hole-local) / notes | Pri |
|---|---|---|---|---|
| **Cup flag** (pole + banner) | all 9 | Pole 0.15 dia x **7.5 tall** (H9: **8.0**); banner 2.0 x 1.2 x 0.05, red #e03c31 | Pole stands in the cup centre (`cup.flag` in holes.json, top point = `cup.flag.top`). Banner at the top, turns to face the tee. **No collision** (the ball passes through) | P1 |
| **Chute arrow signs** | H2 | 1.8 x 3.2 x 0.25 (post + angled arrow board) | Posts outside the lane rails at (-5.2, 0, -16.5) and (5.2, 0, -16.5); boards point into the left / right chute (`facing` [±0.35, -1]). Left: 'Bold Line' + rabbit icon; right: 'Safe Line' | P1 |
| **Felt arrow decals** | H2 | 1.4 x 2.0, 0.01 thick, glowing leaf arrow | Flush on the lane felt at (-2.75, 0, -17) and (2.75, 0, -17), pointing -Z into each chute. Decal only | P1 |
| **Alcove back-wall bank** (cladding) | H8 | 1.3 x 0.5 x 7 | Root-bark cladding over the new banked plane `alcove_bank` (felt overlay x 7.7..9, z -8..-15, rises 0.5 to the east against the back rail). The bank is felt (collision from holes.json); the mesh only dresses it | P1 |
| **Bridge respawn marker stone** | H5 | 0.8 x 0.02 x 0.8 | Flush in the felt at (0, 0, -13.5): where a ball that falls off the root bridge reappears | P2 |
| **Root beam** (pendulum hanger) | H9 | 16 x 1.2 x 1.2 | Spans the chamber at y ≈ 9 over z -38.5 (x 14..30); the pendulum hinge is at its middle | P1 |
| **Tunnel dip trim** | H9 | 6 x 0.4 x 7 | Root-and-moss trim on the tunnel rails following the felt dip (down 0.4 from x 8 to 11, back up to x 14) | P2 |
| **Side-gap lantern posts** | H4 | 0.4 x 2.5 x 0.4 | On the plaza rail tops at x ±7.25, z -17: mark the two side gaps | P2 |

Removed in Round 5: H9 lantern bar and its lantern post (replaced by the pendulum).

## Set dressing (reuse everywhere)

| Prop | Size (studs) | Used at | Pri |
|---|---|---|---|
| Paper lantern, small / medium / large | 0.8 / 1.2 / 2 tall | All holes; strings over greens | P1 |
| Lantern post (timber, hook) | 0.5 x 3–3.5 x 0.5 | H2 chutes, H4 green + side gaps, H7 gap (now x 3.75 / 6.75) | P1 |
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
- The **lantern** model scaled up (1.6 x 1.8 x 1.0 body) is the H9 pendulum bob; one **flag** model serves all 9 cups (H9 uses an 8-stud pole).
- The **rail kit** (straight, 45° and corner pieces) is shared by every hole. The H1, H6 and H9 deflector boards are the same timber plank mesh.
