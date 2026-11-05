# Hole 17: Sundial (Par 3)

Zone: **Sugarloaf Crown**. Gimmick: **Four timed shadow arms sweep around a solid central plinth on a square green**.
Layout: `h17-layout.png`. Geometry: `holes.json` -> holes[16]. World placement (from `world/world.json`): origin [-345.0, 190.0, 232.0], yaw 0.0.
Tee [0, 0, 0], cup [10.1, 0.0, -43.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A stone sundial with 4 moving shadow-arm collision boxes around pivot [0.0, 0.0, -36.0]; centre exclusion: 48 solid circumscribed sandstone strips; balls cannot occupy the central disk.

## Gimmick
Four timed shadow arms sweep around a solid central plinth on a square green.

## Intended shots
Choose the side and time the shadow arms at 12 degrees/s, then putt to the cup. Follow the playable route around the centre exclusion.

## Hole-in-one line
Brute-force search from the tee found ace lines (37 grid shots). The most robust: aim **283.0°** (atan2(dz,dx): direction (0.22, -0.97) in x/z, i.e. 13.0° right of straight -Z), speed **15.7 studs/s** (79% power), start phase t=6.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
The centre must not retain a resting ball within 7 studs. Current sloped felt (empty means flat): []. See phase and rest-audit evidence below.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **shadow_arm** (rotate): pivot [0.0, 0.0, -36.0], axis [0, 1, 0], speed 12.0 deg/s, continuous, phase 0.0, cycle 30.00 s. Blockers (relative to pivot at angle/offset 0): box [3.3, 0.9, 3.6] at [9.85, 0.45, 0.0]; box [3.3, 0.9, 3.6] at [0.0, 0.45, -9.85] yaw 90.0; box [3.3, 0.9, 3.6] at [-9.85, 0.45, -0.0] yaw 180.0; box [3.3, 0.9, 3.6] at [-0.0, 0.45, 9.85] yaw 270.0. Visual: Sundial shadow arms: 4 low slate bars (r 8.2..11.5, 3.6 thick, 0.9 tall) sweeping round the gnomon at 12 deg/s

## Timing check (`tools/timing_check.py`, 96, 120 phases; actual fuzz counts per line)
- shadow_arm [intended] tee shot round the gnomon past the sweeping shadow arms: blocked 52/96 (40 stops + 12 kicks), deflected 16, **Studio estimate 46.2%** (stops + 0.36 kicks), passed 29.2%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- shadow_arm [ace] brute-force ace line: blocked 48/96 (40 stops + 8 kicks), deflected 24, **Studio estimate 44.7%** (stops + 0.36 kicks), passed 25%, traps 0
- shadow_arm [intended] tee shot round the gnomon past the sweeping shadow arms: blocked 72/120 (52 stops + 20 kicks), deflected 16, **Studio estimate 49.3%** (stops + 0.36 kicks), passed 26.7%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- shadow_arm [ace] brute-force ace line: blocked 60/120 (52 stops + 8 kicks), deflected 32, **Studio estimate 45.7%** (stops + 0.36 kicks), passed 23.3%, traps 0

### rest_exclusion (exact hole-local studs)

```json
{
  "center": [
    0,
    0,
    -36
  ],
  "radius": 7.0,
  "physical_plinth_radius": 7.5,
  "method": "48 solid circumscribed sandstone strips; balls cannot occupy the central disk"
}
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [10.1, 7.5, -43.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (p9; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.82 | 6.2% | 76% | 0.4% | 0 / 0 | [123, 908, 491, 272, 133, 43, 17, 13] |
| average | 3.75 | 0.1% | 49% | 0.8% | 0 / 0 | [3, 261, 716, 571, 255, 120, 38, 36] |

## Props for the 3D modeler (decoration only, sizes in studs)
Gnomon dressing, moving shadow arms sized exactly to the listed collision boxes, hour stones and flag; preserve the authored centre exclusion and playable ring.

Decoration anchors (position in hole-local studs):
- `cup_flag` at [10.1, 0.0, -43.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `safe_east_wait` at [8.0, 0, -27.0] size [1.4, 0.01, 2.0]: Safe-route waiting marker outside the arm annulus: play here first, then time the short east-side putt to the cup
- `gnomon` at [0.0, 0, -36.0] (LANDMARK) size [1.6, 9, 6]: Tall candy-striped sundial gnomon (triangular fin, 9 tall) on a solid radius-7.5 sandstone plinth, height 1.2, at the dial centre; hour stones in candy colours on a radius-12.5 ring inside the square perimeter (see hour_stone_* anchors)
- `gnomon_plinth` at [0, 0, -36] size [15.0, 1.2, 15.0]: Solid sandstone central plinth: 48 circumscribed box strips enclose radius 7.5; top y=1.2; no walkable or playable surface on top; keeps every ball outside the seven-stud rest exclusion
- `shadow_arm` at [0.0, 0, -36.0] size [23.0, 0.9, 3.6]: Slate shadow-arm mesh(es) (moving, pivot = dial centre, axis +Y)
- `hour_stone_XII` at [0.0, 0.4, -48.5] size [1.2, 0.8, 1.2]: Candy-coloured hour stone 'XII' (roman numeral on top), 1.2 x 0.8 x 1.2, rail-mounted, collision ON (holes.json static block)
- `hour_stone_I` at [6.25, 0.4, -46.8253] size [1.2, 0.8, 1.2]: Candy-coloured hour stone 'I' (roman numeral on top), 1.2 x 0.8 x 1.2, decorative, collision OFF
- `hour_stone_III` at [12.5, 0.4, -36.0] size [1.2, 0.8, 1.2]: Candy-coloured hour stone 'III' (roman numeral on top), 1.2 x 0.8 x 1.2, rail-mounted, collision ON (holes.json static block)
- `hour_stone_IV` at [10.8253, 0.4, -29.75] size [1.2, 0.8, 1.2]: Candy-coloured hour stone 'IV' (roman numeral on top), 1.2 x 0.8 x 1.2, decorative, collision OFF
- `hour_stone_VII` at [-6.25, 0.4, -25.1747] size [1.2, 0.8, 1.2]: Candy-coloured hour stone 'VII' (roman numeral on top), 1.2 x 0.8 x 1.2, decorative, collision OFF
- `hour_stone_VIII` at [-10.8253, 0.4, -29.75] size [1.2, 0.8, 1.2]: Candy-coloured hour stone 'VIII' (roman numeral on top), 1.2 x 0.8 x 1.2, decorative, collision OFF
- `hour_stone_IX` at [-12.5, 0.4, -36.0] size [1.2, 0.8, 1.2]: Candy-coloured hour stone 'IX' (roman numeral on top), 1.2 x 0.8 x 1.2, rail-mounted, collision ON (holes.json static block)
- `hour_stone_X` at [-10.8253, 0.4, -42.25] size [1.2, 0.8, 1.2]: Candy-coloured hour stone 'X' (roman numeral on top), 1.2 x 0.8 x 1.2, decorative, collision OFF
- `hour_stone_XI` at [-6.25, 0.4, -46.8253] size [1.2, 0.8, 1.2]: Candy-coloured hour stone 'XI' (roman numeral on top), 1.2 x 0.8 x 1.2, decorative, collision OFF
- `hour_stones` at [0.0, 0, -36.0] size [26.2, 0.8, 26.2]: Hour-stone ring (radius 12.5, outside the 11.5 arm sweep): 9 placed stones, exact boxes in the hour_stone_* anchors and hole.hour_stones; dropped (not built): II at [10.8253, 0.4, -42.25] (footprint covers the cup [10.1,0,-43]); V at [6.25, 0.4, -25.1747] (the good golfer's planned tee line and the ace line roll through it); VI at [0.0, 0.4, -23.5] (centre of the 15-wide lane mouth, the only approach into the dial)

## Concept prompt
Eye-height VR view of a candy-striped stone sundial, moving slate shadow arms, a sandstone centre plinth excluding the central disk from play, colourful hour stones and a red flag; warm western golden-hour light. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.

## Round p9 hour stones (exact)
Ring radius 12.5 about the gnomon [0.0, 0, -36.0]; arms reach 11.5. XII toward local -Z, clockwise seen from above (III toward +X). Centre y = half-height .4 (stone sits on the felt, top .8). Min arm-to-rail-stone gap over the cycle: 0.26.

| Hour | Centre [x, y, z] | Size (sx, sy, sz) | Collision |
|---|---|---|---|
| XII | [0.0, 0.4, -48.5] | [1.2, 0.8, 1.2] | ON (rail-mounted) |
| I | [6.25, 0.4, -46.8253] | [1.2, 0.8, 1.2] | OFF |
| II | - | [1.2, 0.8, 1.2] | DROPPED: footprint covers the cup [10.1,0,-43] (would be [10.8253, 0.4, -42.25]) |
| III | [12.5, 0.4, -36.0] | [1.2, 0.8, 1.2] | ON (rail-mounted) |
| IV | [10.8253, 0.4, -29.75] | [1.2, 0.8, 1.2] | OFF |
| V | - | [1.2, 0.8, 1.2] | DROPPED: the good golfer's planned tee line and the ace line roll through it (would be [6.25, 0.4, -25.1747]) |
| VI | - | [1.2, 0.8, 1.2] | DROPPED: centre of the 15-wide lane mouth, the only approach into the dial (would be [0.0, 0.4, -23.5]) |
| VII | [-6.25, 0.4, -25.1747] | [1.2, 0.8, 1.2] | OFF |
| VIII | [-10.8253, 0.4, -29.75] | [1.2, 0.8, 1.2] | OFF |
| IX | [-12.5, 0.4, -36.0] | [1.2, 0.8, 1.2] | ON (rail-mounted) |
| X | [-10.8253, 0.4, -42.25] | [1.2, 0.8, 1.2] | OFF |
| XI | [-6.25, 0.4, -46.8253] | [1.2, 0.8, 1.2] | OFF |

| Phases | Line | Blocked (stops + kicks) | Deflected | Studio est. | Passed | Traps | Fuzz 100k: timeouts / escapes / pinned |
|---|---|---|---|---|---|---|---|
| 96 | intended | 52/96 (40 + 12) | 16 | **46.2%** | 29.2% | 0 | 0 / 0 / 0 (seed 11) |
| 96 | ace | 48/96 (40 + 8) | 24 | **44.7%** | 25% | 0 | - |
| 120 | intended | 72/120 (52 + 20) | 16 | **49.3%** | 26.7% | 0 | 0 / 0 / 0 (seed 29) |
| 120 | ace | 60/120 (52 + 8) | 32 | **45.7%** | 23.3% | 0 | - |
