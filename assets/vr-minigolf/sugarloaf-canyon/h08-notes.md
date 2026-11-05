# Hole 8: Gumdrop Gulch (Par 3)

Zone: **Taffy Mesa**. Gimmick: **Rolling humps: four gumdrop humps (planar ramps) with level hollow floors between them; pace the ball through**.
Layout: `h08-layout.png`. Geometry: `holes.json` -> holes[7]. World placement (from `world/world.json`): origin [360.0, 70.0, 55.0], yaw 0.0.
Tee [0, 0, 0], cup [5.0, 0.0, -55.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
Car-sized sugar-dusted **gumdrops** in cherry, lemon and lime line Gumdrop Gulch; two smaller ones guard the green.

## Gimmick
Rolling humps: four gumdrop humps (planar ramps) with level hollow floors between them; pace the ball through.

## Intended shots
1. Pace the tee shot over the four humps (short gumdrop bumps: each rises 0.12 over a 0.3-stud ramp and drops back over 0.3, with 9.87-stud level floors between) and onto the green.
2. Putt round the gumdrops to the cup.

## Hole-in-one line
Brute-force search from the tee found ace lines (11 grid shots). The most robust: aim **252.0°** (atan2(dz,dx): direction (-0.31, -0.95) in x/z, i.e. 18.0° left of straight -Z), speed **19.4 studs/s** (98% power). The red dashed line on the layout PNG traces it.

## Challenge
Pace control: too soft settles on a level floor between humps (every rest is on level ground: ramps are 0.4 slope, floors 0), too firm runs through the green. Aces need exactly the right pace from the tee.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [5.0, 7.5, -55.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (h8steep; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.44 | 4.4% | 99% | 0.0% | 0 / 0 | [88, 958, 932, 22, 0, 0, 0, 0] |
| average | 2.79 | 0.1% | 88% | 0.0% | 0 / 0 | [2, 689, 1066, 224, 17, 2, 0, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Big gumdrop boulders (P2); 2 gumdrop dressings over the 1.8 bumpers (P1, landmark); taffy-striped rail trim following the humps (P2); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [5.0, 0.0, -55.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `gumdrops` at [0, 0, -50.0] (LANDMARK) size [2.4, 2.4, 2.4]: Giant sugar-dusted gumdrops (cherry, lemon, lime) dressing the two gumdrop bumpers on the green (1.8 x 1.8 octagon-ish bases turned 22.5 deg)
- `dip_trim` at [0, 0, -24.0] size [9, 0.4, 32.0]: Taffy-striped rail trim following the 4 humps (felt humps rise to +0.12; hollow floors at 0)
- `big_gumdrop_bg` at [11, 0, -18] size [6, 5, 6]: Car-sized gumdrop boulders outside the east rail

## Concept prompt
First-person VR view at eye height on a sunny mesa top: a felt lane rolls over four gentle humps like a ribbon of taffy toward a green guarded by giant sugar-dusted gumdrops in cherry, lemon and lime, a red flag beyond; candy-striped mesas all around. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.

## h08_ground Z-profile (2026-10-12 late, game stop rule 0.015)
Width 8 (x -4..4) for lane, humps, floors and run; green x -9..9, all at Y 0 except the humps. Every piece is planar: level (slope 0, where the ball rests) or a 0.4 ramp (the ball never rests on one; the 2 s wedge rule never fired in the sim). A hump = up ramp + down ramp, peak 0.12 at the shared edge. Keep the peak a crisp edge or a round-over of 0.05 or less, with no flat top. Floor lengths are exactly (32 − 8 × 0.3) / 3 = 9.8667.

| Piece | z start | z end | length | Y at start | Y at end | slope |
|---|---|---|---|---|---|---|
| lane | 2 | -8 | 10 | 0 | 0 | 0 |
| dip1 | -8 | -8.3 | 0.3 | 0 | 0.12 | 0.4 |
| dip2 | -8.3 | -8.6 | 0.3 | 0.12 | 0 | 0.4 |
| crease1 | -8.6 | -18.467 | 9.8667 | 0 | 0 | 0 |
| dip3 | -18.467 | -18.767 | 0.3 | 0 | 0.12 | 0.4 |
| dip4 | -18.767 | -19.067 | 0.3 | 0.12 | 0 | 0.4 |
| crease2 | -19.067 | -28.933 | 9.8667 | 0 | 0 | 0 |
| dip5 | -28.933 | -29.233 | 0.3 | 0 | 0.12 | 0.4 |
| dip6 | -29.233 | -29.533 | 0.3 | 0.12 | 0 | 0.4 |
| crease3 | -29.533 | -39.4 | 9.8667 | 0 | 0 | 0 |
| dip7 | -39.4 | -39.7 | 0.3 | 0 | 0.12 | 0.4 |
| dip8 | -39.7 | -40 | 0.3 | 0.12 | 0 | 0.4 |
| run | -40 | -44 | 4 | 0 | 0 | 0 |
| green | -44 | -58 | 14 | 0 | 0 | 0 |

## Rest timing (game rule, tools/rest_timing.py: 80 Studio plans + 400 random shots, seed 5)
Rest time = game stop time minus the first moment the ball dropped under 0.2 studs/s.

| Build | Studio 80 p90 / max | All ~475 p90 / max | > 3 s | Wedged rests |
|---|---|---|---|---|
| Before (0.3 humps, 2.3125 ramps, 4.5 floors) | 0.50 / 4.48 | 0.53 / 5.95 | 18 | 0 |
| Now (0.12 humps, 0.3 ramps, 9.87 floors) | 0.50 / 1.65 | 0.50 / 2.55 | 0 | 0 |

Seeds 6-9: all-shot max 3.0-3.55 s, with 0-2 shots over 3 s (balls that fail to crest a hump roll back across a floor); p90 stays 0.50.
