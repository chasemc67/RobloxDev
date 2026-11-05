# Hole 16: Sinkhole Drop (Par 2)

Zone: **Sugarloaf Crown**. Gimmick: **Drop between levels: putt into a sinkhole in the upper deck and fall 3.6 studs into a funnel bowl**.
Layout: `h16-layout.png`. Geometry: `holes.json` -> holes[15]. World placement (from `world/world.json`): origin [-300.0, 190.0, 112.0], yaw 180.0.
Tee [0, 0, 0], cup [1.8, -3.6, -38.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A crystal-lined **sinkhole** in the sandstone deck, glowing pink, with a rope railing; the funnel bowl green lies 3.6 studs below.

## Gimmick
Drop between levels: putt into a sinkhole in the upper deck and fall 3.6 studs into a funnel bowl.

## Intended shots
1. Putt into the 2.4x2.4 sinkhole: the ball drops into the bowl under the deck and rolls out north.
2. Putt in the funnel bowl.

## Hole-in-one line
Brute-force search from the tee found ace lines (124 grid shots). The most robust: aim **273.0°** (atan2(dz,dx): direction (0.05, -1.00) in x/z, i.e. 3.0° right of straight -Z), speed **16.4 studs/s** (83% power). The red dashed line on the layout PNG traces it.

## Challenge
Pace through the drop: the ball keeps 80% of its speed, and the bowl's side slopes gather it toward the centre line.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [1.8, 3.9, -38.5]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +3.48 studs).

## Playtest stats (p7; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.09 | 9.0% | 82% | 0.0% | 0 / 0 | [181, 1469, 337, 13, 0, 0, 0, 0] |
| average | 2.60 | 0.0% | 46% | 0.0% | 0 / 0 | [0, 919, 970, 108, 3, 0, 0, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Sinkhole rim with crystals (P1, landmark); deck slab over the bowl's south end (P1); felt arrow (P1); bowl rim crystals (P2); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [1.8, -3.6, -38.5] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `sinkhole_rim` at [0.0, 0, -16.2] (LANDMARK) size [3.4, 0.3, 3.4]: Crystal-lined sinkhole rim flush with the deck (rock-candy crystals inside the shaft glowing pink), a low rope railing on posts outside the deck rails
- `deck_overhang` at [0, -1.8, -18] size [8.5, 3.6, 12]: Sandstone deck slab over the bowl's south end (the bowl runs 12 studs back under it, lit by the crystals); deck underside 3.2 above the bowl felt
- `felt_arrow_sink` at [0.0, 0.0, -10.0] size [1.4, 0.01, 2.0]: Glowing felt arrow decal pointing at the sinkhole
- `bowl_rim` at [0, -3.6, -40] size [17, 1.5, 1]: Crystal-studded bowl rim behind the north rail

## Concept prompt
First-person VR view at eye height on the top of a mesa: a short felt deck with a glowing crystal-lined hole in it, rope railing round the deck, and below beyond the deck edge a sunken bowl green with a red flag; panorama of striped mesas at sunset. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
