# Hole 8: Coral Pinball (Par 3)

Zone: **Candyfrost Reef**. Gimmick: **Bumper field: static flat-faced coral-ice bumpers at set angles bounce the ball down the reef toward the cup**.
Layout: `h08-layout.png`. Geometry: `holes.json` -> holes[7]. World placement (from `world/world.json`): origin [430.0, 112.0, 300.0], yaw 0.0.
Tee [0, 0, 0], cup [-3.5, 0.0, -48.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
Giant **coral-ice branches** in bubblegum pink and tangerine glow from inside; seven flat-faced coral bumpers stand in the reef corridor.

## Gimmick
Bumper field: static flat-faced coral-ice bumpers at set angles bounce the ball down the reef toward the cup.

## Intended shots
1. Read the coral faces: a firm tee shot off the first branches pings the ball down the corridor (bumper restitution 0.65).
2. The cup is tucked into the green's west side, off the natural exit line: usually a second putt.

## Hole-in-one line
Brute-force search from the tee found ace lines (12 grid shots). The most robust: aim **292.5°** (atan2(dz,dx): direction (0.38, -0.92) in x/z, i.e. 22.5° right of straight -Z), speed **18.3 studs/s** (93% power). The red dashed line on the layout PNG traces it.

## Challenge
Angles. The corals turn a straight shot unpredictably; good players pick the line that comes off two faces toward the cup.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-3.5, 7.5, -48.5]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +2.73 studs).

## Playtest stats (p2; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 3.16 | 3.1% | 65% | 0.6% | 0 / 0 | [63, 350, 892, 636, 40, 2, 3, 14] |
| average | 3.75 | 0.0% | 39% | 0.1% | 0 / 0 | [0, 78, 707, 928, 234, 40, 8, 5] |

## Props for the 3D modeler (decoration only, sizes in studs)
Coral-ice branch clusters x7 dressing the bumper bases (P1); giant coral tree (P1, landmark); scorekeeper snowpuffs (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-3.5, 0.0, -48.5] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `coral_1` at [-2.0, 0, -10.0] size [2.2, 4, 2.2]: Coral-ice branch cluster (candy colours, neon core) dressing bumper coral1 (1.8x1.8, yaw 45); the collider is its flat-faced base (bumper restitution 0.65), branches rise to ~4 studs and never overhang the felt beyond the base
- `coral_2` at [3.0, 0, -15.5] size [2.8, 4, 1.4]: Coral-ice branch cluster (candy colours, neon core) dressing bumper coral2 (2.4x1, yaw -35); the collider is its flat-faced base (bumper restitution 0.65), branches rise to ~4 studs and never overhang the felt beyond the base
- `coral_3` at [-3.2, 0, -20.5] size [2.8, 4, 1.4]: Coral-ice branch cluster (candy colours, neon core) dressing bumper coral3 (2.4x1, yaw 35); the collider is its flat-faced base (bumper restitution 0.65), branches rise to ~4 studs and never overhang the felt beyond the base
- `coral_4` at [1.5, 0, -25.0] size [2.2, 4, 2.2]: Coral-ice branch cluster (candy colours, neon core) dressing bumper coral4 (1.8x1.8, yaw 45); the collider is its flat-faced base (bumper restitution 0.65), branches rise to ~4 studs and never overhang the felt beyond the base
- `coral_5` at [-1.5, 0, -30.5] size [2.6, 4, 1.4]: Coral-ice branch cluster (candy colours, neon core) dressing bumper coral5 (2.2x1, yaw 60); the collider is its flat-faced base (bumper restitution 0.65), branches rise to ~4 studs and never overhang the felt beyond the base
- `coral_6` at [3.5, 0, -34.5] size [2.4, 4, 1.4]: Coral-ice branch cluster (candy colours, neon core) dressing bumper coral6 (2x1, yaw -30); the collider is its flat-faced base (bumper restitution 0.65), branches rise to ~4 studs and never overhang the felt beyond the base
- `coral_7` at [2.0, 0, -45.0] size [2.0, 4, 2.0]: Coral-ice branch cluster (candy colours, neon core) dressing bumper coral7 (1.6x1.6, yaw 45); the collider is its flat-faced base (bumper restitution 0.65), branches rise to ~4 studs and never overhang the felt beyond the base
- `giant_coral` at [-10.5, 0, -18] (LANDMARK) size [7, 14, 7]: Giant coral-ice tree (bubblegum and tangerine, glowing) outside the west rail: the hole's landmark
- `snowpuffs` at [10.0, 0, -12] size [2.5, 2.2, 2.0]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) keeping score on a chalk board outside the east rail; heads turn to follow the ball (visual only)

## Concept prompt
First-person VR view at eye height from a mini golf tee at night on a reef island: a wide felt corridor dotted with glowing coral-ice branches in candy pink, tangerine and mint, a giant glowing coral tree on the left, a red flag on the green beyond; snow on the rails, brass lanterns, aurora overhead. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
