# Hole 4: Crystal Corridor (Par 3)

Zone: **Rock Candy Narrows**. Gimmick: **Pinball crystals: static flat-faced rock-candy bumpers bounce the ball down the slot**.
Layout: `h04-layout.png`. Geometry: `holes.json` -> holes[3]. World placement (from `world/world.json`): origin [200.0, 18.0, 330.0], yaw -90.0.
Tee [0, 0, 0], cup [4.5, 0.0, -39.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A giant cracked-open **pink geode** glows in the west wall of Rock Candy Narrows; five flat-faced rock-candy crystal clusters stand in the 12-wide slot as pinball bumpers.

## Gimmick
Pinball crystals: static flat-faced rock-candy bumpers bounce the ball down the slot.

## Intended shots
1. Read the crystal faces and bank into the corridor. 2. Approach the offset cup corner. 3. Finish the putt. A precise bank can beat par.

## Hole-in-one line
Brute-force search from the tee found ace lines (13 grid shots). The most robust: aim **269.5°** (atan2(dz,dx): direction (-0.01, -1.00) in x/z, i.e. 0.5° left of straight -Z), speed **16.1 studs/s** (81% power). The red dashed line on the layout PNG traces it.

## Challenge
Par 3: reading crystal-face angles and controlling the exit pace.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [4.5, 7.5, -39.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +2.32 studs).

## Playtest stats (p7; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.54 | 1.1% | 96% | 0.0% | 0 / 0 | [22, 952, 946, 77, 3, 0, 0, 0] |
| average | 3.22 | 0.0% | 67% | 0.0% | 0 / 0 | [0, 364, 970, 547, 111, 6, 1, 1] |

## Props for the 3D modeler (decoration only, sizes in studs)
Rock-candy crystal clusters x5 (glass, neon core) dressing the bumper bases (P1); giant geode in the slot wall (P1, landmark); slot-wall crystal sprinkles (P2); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [4.5, 0.0, -39.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `crystal_1` at [-1.8, 0, -11.0] size [2.0, 4, 2.0]: Rock-candy crystal cluster (pink/amber glass, faint neon core) dressing bumper crystal1 (1.6x1.6, yaw 45); the collider is its flat-faced base, the spikes rise to ~4 studs
- `crystal_2` at [2.6, 0, -16.0] size [2.6, 4, 1.4]: Rock-candy crystal cluster (pink/amber glass, faint neon core) dressing bumper crystal2 (2.2x1, yaw -35); the collider is its flat-faced base, the spikes rise to ~4 studs
- `crystal_3` at [-3.0, 0, -21.0] size [2.6, 4, 1.4]: Rock-candy crystal cluster (pink/amber glass, faint neon core) dressing bumper crystal3 (2.2x1, yaw 35); the collider is its flat-faced base, the spikes rise to ~4 studs
- `crystal_4` at [1.4, 0, -25.5] size [2.0, 4, 2.0]: Rock-candy crystal cluster (pink/amber glass, faint neon core) dressing bumper crystal4 (1.6x1.6, yaw 45); the collider is its flat-faced base, the spikes rise to ~4 studs
- `crystal_5` at [-1.2, 0, -31.0] size [2.4, 4, 1.4]: Rock-candy crystal cluster (pink/amber glass, faint neon core) dressing bumper crystal5 (2x1, yaw 60); the collider is its flat-faced base, the spikes rise to ~4 studs
- `geode_wall` at [-9, 0, -20] (LANDMARK) size [3, 14, 18]: Giant pink geode cracked open in the west slot wall, glowing
- `slot_walls` at [0, 0, -20] size [20, 44, 48]: Slot canyon walls (sage-shadowed sandstone, banded) rise 44 studs either side, beyond the footprint

## Concept prompt
First-person VR view at eye height in a narrow slot canyon: tall smooth pink-and-cream banded walls, a ribbon of rose sky above, a green felt corridor dotted with glowing pink and amber rock-candy crystal clusters, a huge glowing geode in the left wall, a red flag at the far end. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
