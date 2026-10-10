# Hole 6: Mill Wheel Run (Par 3)

Zone: **Stream Crossing**. Gimmick: **Paddle wheel (horizontal axle) dips across the flume; timber deflector boards; mill-race water hazard; ramp to green**.
Layout: `h06-layout.png`. Geometry: `holes.json` -> holes[5]. World offset [84, -2, -70], yaw 0.0.
Tee [0, 0, 0], cup [16.5, 0.25, -22.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A timber **water mill** whose big paddle wheel (radius 3.6, 2 paddle boards) turns slowly across the flume. Its paddles dip through a slot in the felt and sweep downstream. A mill race sits behind a gap in the near rail.

## Gimmick
Paddle wheel (horizontal axle) dips across the flume; timber deflector boards; mill-race water hazard; ramp to green.

## Intended shots
1. Bank off the first timber deflector board into the flume and time the run under the wheel.
2. The second board kicks the ball north up the low 0.25-stud ramp onto the green beside the waterfall.
3. Putt out. A full-power, well-timed tee shot can ride everything to the green (the ace line).

## Hole-in-one line
Brute-force search from the tee found ace lines (46 grid shots). The most robust: aim **278.0°** (atan2(dz,dx): direction (0.14, -0.99) in x/z, i.e. 8.0° right of straight -Z), speed **19.8 studs/s** (100% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Timing a vertical obstacle: the paddles block the flume about 19% of the time, and a paddle that catches the ball shoves it downstream. The gap into the mill race punishes a ball deflected sideways.

## Moving parts / teleports (exact specs, also in holes.json)
- **millwheel** (rotate): pivot [7.5, 3.6, -8.5], axis [0, 0, 1], speed 30.0 deg/s, continuous, phase 0.0, cycle 12.0 s. Blockers (relative to pivot at angle/offset 0): box [0.6, 1.4, 7.6] at [0, -2.9, 0]; box [0.6, 1.4, 7.6] at [0, -2.9, 0] roll 180. Visual: Water-mill wheel, radius 3.6, 2 opposed paddle boards spanning the flume; felt has a 0.8-wide slot under it

## Playtest stats (final, p4, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 3.18 | 8.0% | 0.9% | [160, 349, 909, 352, 112, 55, 29, 34] |
| average | 3.63 | 0.0% | 0.0% | [0, 129, 809, 812, 193, 35, 15, 7] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Mill wheel (moving, axle centre, axis +Z, 30°/s) 1x7.2x8 (P1); mill house 9x10x8 (P1); timber deflector boards x2 cladding 10x1x0.5 (P1); mill race water + banks (P1); waterfall beside the green 6x12x4 (P1); flour sacks & crates (P3).

Decoration anchors (position in hole-local studs):
- `water_mill` at [7.5, 0, 0] (LANDMARK) size [9, 10, 8]: Timber mill house on the south side; wheel axle enters it
- `mill_wheel` at [7.5, 3.6, -8.5] size [1, 7.2, 8]: Wheel mesh (moving part) radius 3.6, axle along Z
- `waterfall` at [24, 0.25, -24] size [6, 12, 4]: Waterfall cascading down rocks east of the green
- `sacks` at [-6, 0, -6] size [2, 1.5, 2]: Flour sacks & crates

## Concept prompt
First-person VR view from a mini golf tee at eye height. The green felt lane turns right at a slanted timber board into a wooden flume, where a large water-mill paddle wheel slowly turns, its paddles dipping through the felt and splashing. A rustic timber mill house stands beside it with lanterns in the windows. Beyond, a second board turns the course up a short ramp to a green beside a tumbling waterfall with a red flag. A glinting mill race, autumn leaves, warm golden light and spray mist, cozy storybook style.
