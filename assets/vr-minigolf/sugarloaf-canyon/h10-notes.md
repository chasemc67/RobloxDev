# Hole 10: Sluice Chute (Par 2)

Zone: **Sugarloaf Dam**. Gimmick: **One-way slope: a steep sluice chute drops 3.6 studs into a basin green; felt arrows and chevrons show it is one-way**.
Layout: `h10-layout.png`. Geometry: `holes.json` -> holes[9]. World placement (from `world/world.json`): origin [290.0, 116.0, -300.0], yaw 180.0.
Tee [0, 0, 0], cup [7.0, -3.6, -33.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A timber **sluice flume** with peppermint-striped gate frames drops the ball 3.6 studs down a 16-long chute into a spillway basin; the Peppermint Dam rises beyond.

## Gimmick
One-way slope: a steep sluice chute drops 3.6 studs into a basin green; felt arrows and chevrons show it is one-way.

## Intended shots
1. Roll into the chute mouth: the ball accelerates down the chute into the basin and climbs its back slope.
2. Putt to the cup on the right side of the basin.

## Hole-in-one line
Brute-force search from the tee found ace lines (12 grid shots). The most robust: aim **305.0°** (atan2(dz,dx): direction (0.57, -0.82) in x/z, i.e. 35.0° right of straight -Z), speed **19.4 studs/s** (98% power). The red dashed line on the layout PNG traces it.

## Challenge
One-way: big glowing chevrons on the chute and a 'ONE WAY' felt arrow on the deck show the ball won't come back. Pace into the chute barely matters; where it comes off the back slope does.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [7.0, 3.9, -33.5]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +3.81 studs).

## Playtest stats (p7; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 1.98 | 6.6% | 96% | 0.0% | 0 / 0 | [131, 1782, 87, 0, 0, 0, 0, 0] |
| average | 2.52 | 0.0% | 56% | 0.0% | 0 / 0 | [0, 1122, 730, 143, 5, 0, 0, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Sluice flume casing 5x4x16 with striped gate frames and a sheet of water beside the felt (P1, landmark); chute chevrons x4 + deck arrow (P1); basin back wall (P2); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [7.0, -3.6, -33.5] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `chevron_1` at [0.0, -0.45, -16.0] size [2.4, 0.01, 1.2]: Glowing felt chevron decal on the chute pointing -Z (one-way: the ball won't come back up)
- `chevron_2` at [0.0, -1.35, -20.0] size [2.4, 0.01, 1.2]: Glowing felt chevron decal on the chute pointing -Z (one-way: the ball won't come back up)
- `chevron_3` at [0.0, -2.25, -24.0] size [2.4, 0.01, 1.2]: Glowing felt chevron decal on the chute pointing -Z (one-way: the ball won't come back up)
- `chevron_4` at [0.0, -3.15, -28.0] size [2.4, 0.01, 1.2]: Glowing felt chevron decal on the chute pointing -Z (one-way: the ball won't come back up)
- `felt_arrow_deck` at [0.0, 0.0, -10.0] size [2.4, 0.01, 3.0]: Big glowing 'ONE WAY' felt arrow on the deck pointing into the chute
- `sluice_flume` at [0, -1.8, -22.0] (LANDMARK) size [5, 4, 16]: Timber sluice flume casing over the chute (open top), peppermint-striped gate frames at the top and bottom, a thin sheet of turquoise water running beside the felt (visual only)
- `basin_bank` at [0, -3.6, -40] size [19, 3, 1]: Spillway-basin back wall of peppermint concrete behind the uphill back slope
- `dam_view` at [0, 0, -60] size [80, 100, 10]: The Peppermint Dam and reservoir beyond the basin (world dressing)

## Concept prompt
First-person VR view at eye height on a high bench beside a peppermint-striped dam: a short felt deck tips into a steep timber sluice chute with glowing chevrons, dropping into a round basin green with a red flag; the reservoir and the dam's spillway falls beyond. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
