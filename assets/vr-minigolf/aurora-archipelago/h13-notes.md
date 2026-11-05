# Hole 13: Snowpuff Carousel (Par 3)

Zone: **Icefall Terraces**. Gimmick: **Horizontal sweeper: a carousel of snowpuff sleds sweeps four arms round a solid central hub on a square green**.
Layout: `h13-layout.png`. Geometry: `holes.json` -> holes[12]. World placement (from `world/world.json`): origin [120.0, 182.0, -230.0], yaw 0.0.
Tee [0, 0, 0], cup [10.1, 0.0, -46.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A brass-and-ice **carousel** with a striped canopy and a snowpuff weathervane stands in the middle of a square green; four sled-runner arms carrying snowpuffs on little sleds sweep round its solid round base.

## Gimmick
Horizontal sweeper: a carousel of snowpuff sleds sweeps four arms round a solid central hub on a square green.

## Intended shots
**Timing line:** a tee shot round the base past the sweeping arms to the east-side cup.
**Safe line:** stop at the marker outside the sweep, then time a short putt.

## Hole-in-one line
Brute-force search from the tee found ace lines (52 grid shots). The most robust: aim **287.5°** (atan2(dz,dx): direction (0.30, -0.95) in x/z, i.e. 17.5° right of straight -Z), speed **19.4 studs/s** (98% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Horizontal rotor at 15 °/s. The solid base keeps every ball out of the middle (no rests within 7 studs of the hub).

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **carousel_arms** (rotate): pivot [0.0, 0.0, -36.0], axis [0, 1, 0], speed 15.0 deg/s, continuous, phase 0.0, cycle 24.00 s. Blockers (relative to pivot at angle/offset 0): box [3.3, 0.9, 3.6] at [9.85, 0.45, 0.0]; box [3.3, 0.9, 3.6] at [0.0, 0.45, -9.85] yaw 90.0; box [3.3, 0.9, 3.6] at [-9.85, 0.45, -0.0] yaw 180.0; box [3.3, 0.9, 3.6] at [-0.0, 0.45, 9.85] yaw 270.0. Visual: Carousel sweep: 4 low sled-runner arms (r 8.2..11.5, 3.6 wide, 0.9 tall), each carrying a snowpuff on a little sled above the collider, sweeping round the hub at 15 deg/s

## Timing check (`tools/timing_check.py`, 96 phases; actual fuzz counts per line)
- carousel_arms [intended] tee shot round the carousel hub past the sweeping arms: blocked 40/96 (32 stops + 8 kicks), deflected 32, **Studio estimate 36.3%** (stops + 0.36 kicks), passed 25%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- carousel_arms [ace] brute-force ace line: blocked 32/96 (32 stops + 0 kicks), deflected 20, **Studio estimate 33.3%** (stops + 0.36 kicks), passed 45.8%, traps 0

### rest_exclusion (exact hole-local studs)

```json
{
  "center": [
    0,
    0,
    -36.0
  ],
  "radius": 7.0,
  "physical_plinth_radius": 7.5,
  "method": "48 solid circumscribed box strips (the carousel's round base); balls cannot occupy the central disk"
}
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [10.1, 7.5, -46.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (p2; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.75 | 4.2% | 80% | 0.5% | 0 / 0 | [85, 906, 619, 263, 97, 11, 6, 13] |
| average | 3.69 | 0.1% | 51% | 0.5% | 0 / 0 | [3, 276, 733, 546, 295, 92, 31, 24] |

## Props for the 3D modeler (decoration only, sizes in studs)
Carousel canopy (underside y 9) and brass pole (P1, landmark); solid round base r 7.5 (P1); four arm meshes with sled snowpuffs, pivot = hub (P1); music-box lanterns (P2); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [10.1, 0.0, -46.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `safe_east_wait` at [8.0, 0, -27.0] size [1.4, 0.01, 2.0]: Safe-route waiting marker outside the arm sweep: play here first, then time the short east-side putt
- `carousel_canopy` at [0.0, 0, -36.0] (LANDMARK) size [16, 12, 16]: Brass-and-ice carousel: a striped canopy on a central brass pole, topped by a snowpuff weathervane. Canopy underside y 9 (>= 8 over the felt), pole inside the hub; the solid r 7.5 round base (collider 1.2 high) is the hub
- `hub_base` at [0, 0, -36.0] size [15.0, 1.2, 15.0]: Solid round carousel base: 48 circumscribed box strips enclose r 7.5; top y 1.2; not a playing surface
- `carousel_arms` at [0.0, 0, -36.0] size [23.0, 0.9, 3.6]: Moving mesh (pivot = hub centre, axis +Y): four sled-runner arms with snowpuffs riding little sleds; mesh covers the collider boxes exactly
- `music_lanterns` at [-14.5, 0, -24] size [1, 9, 1]: Brass music-box lanterns on posts at the green's corners (outside the rails)

## Concept prompt
First-person VR view at eye height from a mini golf tee at night on an icy terrace: a square green with a brass-and-ice carousel in the middle, its striped canopy topped by a snowpuff weathervane, four low arms carrying snowpuffs on little sleds sweeping round over the felt; a red flag at the far right; the Great Frozen Falls glowing at the terrace edge. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
