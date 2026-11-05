# Hole 6: Palm Lagoon (Par 3)

Zone: **Steamwhistle Lagoons**. Gimmick: **Side-slope green: a snow-felt shelf tilted toward a turquoise hot-spring pool (hazard; misses respawn beside it)**.
Layout: `h06-layout.png`. Geometry: `holes.json` -> holes[5]. World placement (from `world/world.json`): origin [305.0, 84.0, 478.0], yaw 0.0.
Tee [0, 0, 0], cup [-5.0, -0.0, -54.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
**Kettle Lagoon**: a steaming turquoise hot-spring pool cut into the low east edge of a big tilted snow-felt shelf, frosted palms leaning over it.

## Gimmick
Side-slope green: a snow-felt shelf tilted toward a turquoise hot-spring pool (hazard; misses respawn beside it).

## Intended shots
1. Aim left of the flag: the whole shelf falls gently east toward the pool, so a straight putt curls right.
2. Read the break on the second putt too; the cup sits in the middle of the slope.

## Hole-in-one line
Brute-force search from the tee found ace lines (8 grid shots). The most robust: aim **262.5°** (atan2(dz,dx): direction (-0.13, -0.99) in x/z, i.e. 7.5° left of straight -Z), speed **18.7 studs/s** (94% power). The red dashed line on the layout PNG traces it.

## Challenge
Slope reading. The shelf falls 0.42 across 29 studs, the steepest plane where a ball can still come to rest, so every putt breaks. A ball that curls into the pool reappears on the basalt stone beside it (+1).

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **hazard kettle_pool** (water): +1 stroke, ball placed at rest on the respawn point [5.5, -0.1303, -36.25]


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-5.0, 7.5, -54.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (after-late; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.40 | 3.5% | 100% | 0.0% | 0 / 0 | [70, 1068, 862, 0, 0, 0, 0, 0] |
| average | 2.61 | 2.9% | 96% | 0.0% | 0 / 0 | [57, 737, 1133, 70, 3, 0, 0, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Hot-spring pool with basalt rim and steam (P1, landmark); respawn stone (P1); frosted palms x3 (P2); wind-ripple slope chevrons on the felt (P1); snowpuff foot-bath (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-5.0, -0.0, -54.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `kettle_pool` at [11.5, -0.8607, -36.25] (LANDMARK) size [6.0, 1, 24.5]: Turquoise hot-spring pool #2FD6C8 set into the shelf's low east edge (6 x 24.5), steam curling off it, basalt rim on its far (east) side under the rail; a ball that rolls in bubbles back up on the respawn stone beside it
- `pool_respawn_stone` at [5.5, -0.1303, -36.25] size [0.8, 0.02, 0.8]: Warm basalt marker stone flush in the felt beside the pool: where a pooled ball reappears
- `frosted_palms` at [16.5, 0, -35] size [6, 12, 8]: Three frosted palms leaning over the pool from the east rim (fronds >= 8 above the felt)
- `slope_ripples` at [0.0, 0.0, -36.0] size [20, 0.01, 2]: Faint wind-ripple chevrons printed across the shelf felt pointing east (down the fall line toward the pool): the reading aid
- `snowpuffs` at [-16.0, 0.2, -30] size [2.5, 2.2, 2.0]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) in a little steaming foot-bath outside the west rail, towels on their heads; heads turn to follow the ball (visual only)

## Concept prompt
First-person VR view at eye height from a mini golf tee at night: a wide snow-felt green tilts gently to the right toward a steaming turquoise hot-spring pool with a basalt rim, frosted palms leaning over the water, a red flag in the middle of the slope; snowpuffs relax in a little steaming foot-bath with towels on their heads; aurora overhead. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
