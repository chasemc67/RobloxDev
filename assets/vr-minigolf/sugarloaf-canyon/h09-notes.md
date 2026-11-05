# Hole 9: Lollipop Windmill (Par 3)

Zone: **Taffy Mesa**. Gimmick: **Vertical rotor: a windpump's lollipop vanes turn across the tunnel mouth; the bypass round the pump house is the safe way**.
Layout: `h09-layout.png`. Geometry: `holes.json` -> holes[8]. World placement (from `world/world.json`): origin [330.0, 70.0, -110.0], yaw -90.0.
Tee [0, 0, 0], cup [-1.5, 0.0, -42.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A prospector's windpump turns 4 broad swirl-lollipop vanes across its tunnel mouth.

## Gimmick
Vertical rotor: a windpump's lollipop vanes turn across the tunnel mouth; the bypass round the pump house is the safe way.

## Intended shots
Time the central tunnel shot between vanes, or follow the signed east bypass around the pump house. Measured stop rates appear below.

## Hole-in-one line
Brute-force search from the tee found ace lines (290 grid shots). The most robust: aim **267.5°** (atan2(dz,dx): direction (-0.04, -1.00) in x/z, i.e. 2.5° left of straight -Z), speed **15.3 studs/s** (78% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Second timing obstacle, a different motion (vertical rotor). Good players time the vanes; the bypass costs about a stroke.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **windpump** (rotate): pivot [0, 4.25, -17.75], axis [0, 0, 1], speed 20.0 deg/s, continuous, phase 0.0, cycle 18.00 s. Blockers (relative to pivot at angle/offset 0): box [0.39999999999999997, 3.3204591567825315, 0.4] at [-1.0, -2.260229578391266, 0]; box [0.39999999999999997, 3.42119385257662, 0.4] at [-0.6000000000000001, -2.31059692628831, 0]; box [0.39999999999999997, 3.480441152620633, 0.4] at [-0.20000000000000004, -2.3402205763103163, 0]; box [0.39999999999999997, 3.480441152620633, 0.4] at [0.19999999999999998, -2.3402205763103163, 0]; box [0.39999999999999997, 3.42119385257662, 0.4] at [0.5999999999999999, -2.31059692628831, 0]; box [0.39999999999999997, 3.3204591567825315, 0.4] at [1.0, -2.260229578391266, 0]; box [0.39999999999999997, 3.3204591567825315, 0.4] at [-1.0, -2.260229578391266, 0] roll 90.0; box [0.39999999999999997, 3.42119385257662, 0.4] at [-0.6000000000000001, -2.31059692628831, 0] roll 90.0; box [0.39999999999999997, 3.480441152620633, 0.4] at [-0.20000000000000004, -2.3402205763103163, 0] roll 90.0; box [0.39999999999999997, 3.480441152620633, 0.4] at [0.19999999999999998, -2.3402205763103163, 0] roll 90.0; box [0.39999999999999997, 3.42119385257662, 0.4] at [0.5999999999999999, -2.31059692628831, 0] roll 90.0; box [0.39999999999999997, 3.3204591567825315, 0.4] at [1.0, -2.260229578391266, 0] roll 90.0; box [0.39999999999999997, 3.3204591567825315, 0.4] at [-1.0, -2.260229578391266, 0] roll 180.0; box [0.39999999999999997, 3.42119385257662, 0.4] at [-0.6000000000000001, -2.31059692628831, 0] roll 180.0; box [0.39999999999999997, 3.480441152620633, 0.4] at [-0.20000000000000004, -2.3402205763103163, 0] roll 180.0; box [0.39999999999999997, 3.480441152620633, 0.4] at [0.19999999999999998, -2.3402205763103163, 0] roll 180.0; box [0.39999999999999997, 3.42119385257662, 0.4] at [0.5999999999999999, -2.31059692628831, 0] roll 180.0; box [0.39999999999999997, 3.3204591567825315, 0.4] at [1.0, -2.260229578391266, 0] roll 180.0; box [0.39999999999999997, 3.3204591567825315, 0.4] at [-1.0, -2.260229578391266, 0] roll 270.0; box [0.39999999999999997, 3.42119385257662, 0.4] at [-0.6000000000000001, -2.31059692628831, 0] roll 270.0; box [0.39999999999999997, 3.480441152620633, 0.4] at [-0.20000000000000004, -2.3402205763103163, 0] roll 270.0; box [0.39999999999999997, 3.480441152620633, 0.4] at [0.19999999999999998, -2.3402205763103163, 0] roll 270.0; box [0.39999999999999997, 3.42119385257662, 0.4] at [0.5999999999999999, -2.31059692628831, 0] roll 270.0; box [0.39999999999999997, 3.3204591567825315, 0.4] at [1.0, -2.260229578391266, 0] roll 270.0. Visual: 4 lollipop vanes, width 2.4, radius 0.6..4.1, circular clipped tips built from 6 strips; axle y=4.25; tip clearance 0.150 at every phase

## Timing check (`tools/timing_check.py`, 96, 120 phases; actual fuzz counts per line)
- windpump [intended] tee shot into the pump-house tunnel past the windpump vanes: blocked 0/96 (0 stops + 0 kicks), deflected 8, **Studio estimate 0%** (stops + 0.36 kicks), passed 91.7%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- windpump [ace] brute-force ace line: blocked 0/96 (0 stops + 0 kicks), deflected 0, **Studio estimate 0%** (stops + 0.36 kicks), passed 100%, traps 0
- windpump [intended] tee shot into the pump-house tunnel past the windpump vanes: blocked 0/120 (0 stops + 0 kicks), deflected 12, **Studio estimate 0%** (stops + 0.36 kicks), passed 90%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- windpump [ace] brute-force ace line: blocked 0/120 (0 stops + 0 kicks), deflected 0, **Studio estimate 0%** (stops + 0.36 kicks), passed 100%, traps 0


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-1.5, 7.5, -42.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs). Moving parts crossing the sightline: windpump 75% of its cycle.

## Playtest stats (p9; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.16 | 5.2% | 95% | 0.0% | 0 / 0 | [105, 1589, 208, 77, 19, 2, 0, 0] |
| average | 4.13 | 0.0% | 33% | 0.0% | 0 / 0 | [0, 61, 592, 552, 633, 149, 12, 1] |

## Props for the 3D modeler (decoration only, sizes in studs)
Windpump with 4 clipped-tip vane assemblies, pivot [0, 4.25, -17.75], speed 20 degrees/s; exact collider boxes below. Pump house, tank and bypass signs.

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-1.5, 0.0, -42.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `pump_house` at [-3, 0, -21] (LANDMARK) size [16, 8, 6]: Timber pump house (the rock 'house' block x 1.2..8 plus a matching west half) with the windpump tower on its roof; the tunnel through it is 2.4 wide, 6 long
- `windpump_wheel` at [0, 4.25, -17.75] size [8.2, 8.2, 0.4]: Windpump wheel mesh (moving part, pivot = hub, axis +Z): 4 swirl-lollipop vanes radius 4.1
- `water_tank` at [-7, 0, -40] size [4, 8, 4]: Striped water tank on stilts beside the green
- `sign_bypass` at [11.6, 0, -13] size [1.8, 3.2, 0.25]: Arrow sign 'Round the back - no vanes' pointing into the bypass
- `felt_arrow_bypass` at [9.5, 0.0, -20.0] size [1.4, 0.01, 2.0]: Glowing felt arrow decal pointing -Z into the bypass

## Concept prompt
First-person VR view at eye height on a mesa top: a felt lane leads to a timber pump house whose windpump wheel of giant swirl lollipops turns slowly in front of a small tunnel; a path curves round the back; a striped water tank and a red flag beyond. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.

## Round p9 (exact)
- Hub raised: pivot y **4.25** (was 4.12); vane strips unchanged (4 vanes x 6 strips, width 2.4, radial .6..4.1, depth .4, circular tip clipping r 4.1).
- Tip clearance over the felt, min over the full 18 s cycle (36,000 samples): **0.15** (was 0.02).
- **Target conflict (not met):** the ball radius is 0.08 (0.16 tall). A collider whose lowest point is >= 0.15 above the felt can only overlap the top 0.01 of the ball, so in the simulator it no longer stops balls (block rate measured below). Clearance was treated as the hard requirement; the 35-50% stop target is NOT met. Clearance-vs-stop curve and one-knob fallback values: `_work/p9-report.md`.

| Phases | Line | Blocked (stops + kicks) | Deflected | Studio est. | Passed | Traps | Fuzz 100k: timeouts / escapes / pinned |
|---|---|---|---|---|---|---|---|
| 96 | intended | 0/96 (0 + 0) | 8 | **0%** | 91.7% | 0 | 0 / 0 / 0 (seed 11) |
| 96 | ace | 0/96 (0 + 0) | 0 | **0%** | 100% | 0 | - |
| 120 | intended | 0/120 (0 + 0) | 12 | **0%** | 90% | 0 | 0 / 0 / 0 (seed 29) |
| 120 | ace | 0/120 (0 + 0) | 0 | **0%** | 100% | 0 | - |

## Round p9b
Hub stays at y 4.12. Collision tip clearance **0.06** (R_coll 4.06, 12 strips); intended Studio stop rate 41.7% @96 / 43.3% @120. A 0.15 tip clearance cannot block the 0.16-tall ball. Visual tip may extend to r 4.1 past the collider.
