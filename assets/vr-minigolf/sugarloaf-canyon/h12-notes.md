# Hole 12: Intake Tower (Par 4)

Zone: **Sugarloaf Dam**. Gimmick: **Pipe teleport: sink the ball in the intake grate at the end of a rail-less pier and it shoots out of an outflow pipe by the green, or play the long shoreline route**.
Layout: `h12-layout.png`. Geometry: `holes.json` -> holes[11]. World placement (from `world/world.json`): origin [-200.0, 116.0, -270.0], yaw -90.0.
Tee [0, 0, 0], cup [2.0, 0.0, -58.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A domed peppermint **intake tower** stands in Sugarloaf Reservoir beside a rail-less timber pier with a glowing brass intake grate.

## Gimmick
Pipe teleport: sink the ball in the intake grate at the end of a rail-less pier and it shoots out of an outflow pipe by the green, or play the long shoreline route.

## Intended shots
**Shortcut:** 1) putt along the pier and sink the ball in the intake grate 2 studs from the open end (r 0.3); it shoots out of the outflow pipe on the green aimed at the cup. 2) putt.
**Shoreline route:** 1) into the shoreline channel, 2) up it to the green, 3-4) putt across.

## Hole-in-one line
Brute-force search from the tee found ace lines (30 grid shots). The most robust: aim **269.5°** (atan2(dz,dx): direction (-0.01, -1.00) in x/z, i.e. 0.5° left of straight -Z), speed **16.8 studs/s** (85% power). The red dashed line on the layout PNG traces it.

## Challenge
Risk/reward: overshoot the pier and the ball goes in the reservoir (+1, back to the stroke start). The shoreline is the reliable par.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **teleport intake_pipe**: entry [0.0, 0.0, -33.0] r 0.3 -> exit [11.0, 0.0, -61.0] dir [-0.9487, 0.3162], exit speed = clamp(in x 0.7, 3.0, 7.0) studs/s. Brass intake grate (glowing lime ring) set in the pier deck 2 studs from its open end -> outflow pipe mouth on the green's east side
- **hazard reservoir** (water): +1 stroke, ball back to where the stroke started


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [2.0, 7.5, -58.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +4.81 studs).

## Playtest stats (p7; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 3.44 | 4.0% | 74% | 0.7% | 0 / 0 | [80, 419, 800, 176, 410, 27, 68, 20] |
| average | 4.99 | 0.0% | 25% | 0.2% | 0 / 0 | [0, 1, 0, 497, 1077, 374, 42, 9] |

## Props for the 3D modeler (decoration only, sizes in studs)
Intake tower 7x16x7 (P1, landmark); timber pier without rails (P1); brass grate with lime glow ring (P1); outflow pipe mouth (P1); signs x2 + felt arrows x2 (P1); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [2.0, 0.0, -58.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `intake_tower` at [6, -1.2, -38] (LANDMARK) size [7, 16, 7]: Domed peppermint intake tower standing in the water east of the pier (visual), a pipe running under the water from the grate to the outflow on the green
- `intake_grate` at [0.0, 0.0, -33.0] size [1.4, 0.02, 1.4]: Round brass intake grate flush in the pier deck with a glowing lime ring (0.6 across)
- `outflow_pipe` at [11.0, 0.0, -61.0] size [2.5, 2.5, 3]: Big riveted outflow pipe mouth on the green's east edge, angled at the cup (teleport exit, splash particles)
- `pier_posts` at [0, -1.2, -28] size [3.2, 1.4, 13]: Timber pier on posts (no railings: the open sides and end drop into the reservoir)
- `sign_pier` at [2.2, 0, -20] size [1.6, 2.6, 0.2]: Sign 'Intake - shoot the pipe!' at the pier root
- `sign_shore` at [-16.6, 0, -24] size [1.8, 3.2, 0.25]: Sign 'Shoreline Trail' pointing north along the shore
- `felt_arrow_pier` at [0.0, 0.0, -20.0] size [1.4, 0.01, 2.0]: Glowing felt arrow decal pointing -Z onto the pier
- `felt_arrow_shore` at [-13.5, 0.0, -24.0] size [1.4, 0.01, 2.0]: Glowing felt arrow decal pointing -Z up the shoreline

## Concept prompt
First-person VR view at eye height on a reservoir shore at sunset: a felt lane leads onto a narrow rail-less timber pier ending at a glowing brass grate, a domed red-and-white intake tower standing in turquoise water; a channel follows the shoreline to a green with a red flag. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
