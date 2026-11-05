# Hole 15: Sugar Dune (Par 3)

Zone: **Hoodoo Garden**. Gimmick: **Side-slope reading: a long dune face tilted across the line, dropping to a two-tier green**.
Layout: `h15-layout.png`. Geometry: `holes.json` -> holes[14]. World placement (from `world/world.json`): origin [-300.0, 150.0, -115.0], yaw 180.0.
Tee [0, 0, 0], cup [6.0, -4.6, -57.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A powdered-sugar **dune** whose felt face tilts across the line toward the east-north-east, with sand-sled tracks and a striped sled on the lip.

## Gimmick
Side-slope reading: a long dune face tilted across the line, dropping to a two-tier green.

## Intended shots
1. Drop off the lane lip onto the dune face, aimed well uphill (west): the slope curls the ball east and slightly downhill toward the green.
2. Off the dune's lower edge onto the two-tier green; putt down to the cup on the lower tier.

## Hole-in-one line
Brute-force search from the tee found ace lines (92 grid shots). The most robust: aim **275.5°** (atan2(dz,dx): direction (0.10, -1.00) in x/z, i.e. 5.5° right of straight -Z), speed **18.3 studs/s** (93% power). The red dashed line on the layout PNG traces it.

## Challenge
Reading a side slope. Wind-ripple chevrons in the felt show the fall line; chevrons at the lip say the face is one-way.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [6.0, 2.9, -57.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.04 studs).

## Playtest stats (h15lean; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.47 | 3.2% | 100% | 0.0% | 0 / 0 | [65, 937, 998, 0, 0, 0, 0, 0] |
| average | 2.73 | 0.1% | 99% | 0.0% | 0 / 0 | [1, 559, 1413, 27, 0, 0, 0, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Sugar-dune dressing and sled (P1, landmark); felt fall-line chevrons and lip chevrons (P1); dune cliff skirt over the green (P2); tier lip (P2); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [6.0, -4.6, -57.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `sugar_dune` at [0.0, -2.2, -24.0] (LANDMARK) size [30, 6, 34]: Powdered-sugar dune face (the tilted felt plane, yaw 25, falling 2.4 toward the east-north-east), sled tracks, a striped sand-sled propped on the lane lip; dune dressing beyond the rails
- `slope_arrows` at [0.0, -2.2, -24.0] size [20, 0.01, 2]: Faint wind-ripple chevrons printed across the dune felt pointing down the fall line (east-north-east): the reading aid
- `lip_chevrons` at [0, 0, -9.5] size [7, 0.01, 1]: Felt chevrons at the lane lip pointing -Z: the dune face below is one-way (the ball won't come back up)
- `tier_lip` at [0, -4.0, -48] size [32, 0.3, 0.5]: Sugar-sandstone lip trim along the two-tier step
- `dune_cliff` at [6, -4.0, -37] size [16, 2, 1]: Sugar-sandstone cliff face where the dune's lower end overhangs the upper tier (visual skirt down to the green)

## Concept prompt
First-person VR view at eye height at the top of a powdered-sugar dune: the felt drops onto a broad face tilted to the right with sled tracks, curving down to a two-tier green with a red flag; striped hoodoos and the Crown mesa beyond, golden low sun from the left. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
