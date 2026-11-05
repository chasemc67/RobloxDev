# Hole 12: Icebreaker Wheel (Par 3)

Zone: **Driftfloe Shelf**. Gimmick: **Vertical rotor: the icebreaker's paddle wheel turns across the channel on a horizontal axle; the signed bypass is the safe way**.
Layout: `h12-layout.png`. Geometry: `holes.json` -> holes[11]. World placement (from `world/world.json`): origin [370.0, 146.0, -60.0], yaw 90.0.
Tee [0, 0, 0], cup [-1.5, 0.0, -42.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A beached toy **icebreaker** (red hull, cream deckhouse, red funnel) straddles the channel; its red-and-cream **paddle wheel** turns across the channel on a horizontal axle.

## Gimmick
Vertical rotor: the icebreaker's paddle wheel turns across the channel on a horizontal axle; the signed bypass is the safe way.

## Intended shots
**Timing line:** a firm putt through the 2.4-wide channel between paddles: birdie chance.
**Safe line:** the signed bypass round the stern, then putt: par.

## Hole-in-one line
Brute-force search from the tee found ace lines (172 grid shots). The most robust: aim **267.5°** (atan2(dz,dx): direction (-0.04, -1.00) in x/z, i.e. 2.5° left of straight -Z), speed **15.3 studs/s** (78% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Vertical rotor at 30 °/s: broad paddles with clipped tips; pick the gap or take the bypass.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **paddle_wheel** (rotate): pivot [0, 4.16, -17.75], axis [0, 0, 1], speed 30.0 deg/s, continuous, phase 0.0, cycle 12.00 s. Blockers (relative to pivot at angle/offset 0): box [0.39999999999999997, 3.3204591567825315, 0.4] at [-1.0, -2.260229578391266, 0]; box [0.39999999999999997, 3.42119385257662, 0.4] at [-0.6000000000000001, -2.31059692628831, 0]; box [0.39999999999999997, 3.480441152620633, 0.4] at [-0.20000000000000004, -2.3402205763103163, 0]; box [0.39999999999999997, 3.480441152620633, 0.4] at [0.19999999999999998, -2.3402205763103163, 0]; box [0.39999999999999997, 3.42119385257662, 0.4] at [0.5999999999999999, -2.31059692628831, 0]; box [0.39999999999999997, 3.3204591567825315, 0.4] at [1.0, -2.260229578391266, 0]; box [0.39999999999999997, 3.3204591567825315, 0.4] at [-1.0, -2.260229578391266, 0] roll 90.0; box [0.39999999999999997, 3.42119385257662, 0.4] at [-0.6000000000000001, -2.31059692628831, 0] roll 90.0; box [0.39999999999999997, 3.480441152620633, 0.4] at [-0.20000000000000004, -2.3402205763103163, 0] roll 90.0; box [0.39999999999999997, 3.480441152620633, 0.4] at [0.19999999999999998, -2.3402205763103163, 0] roll 90.0; box [0.39999999999999997, 3.42119385257662, 0.4] at [0.5999999999999999, -2.31059692628831, 0] roll 90.0; box [0.39999999999999997, 3.3204591567825315, 0.4] at [1.0, -2.260229578391266, 0] roll 90.0; box [0.39999999999999997, 3.3204591567825315, 0.4] at [-1.0, -2.260229578391266, 0] roll 180.0; box [0.39999999999999997, 3.42119385257662, 0.4] at [-0.6000000000000001, -2.31059692628831, 0] roll 180.0; box [0.39999999999999997, 3.480441152620633, 0.4] at [-0.20000000000000004, -2.3402205763103163, 0] roll 180.0; box [0.39999999999999997, 3.480441152620633, 0.4] at [0.19999999999999998, -2.3402205763103163, 0] roll 180.0; box [0.39999999999999997, 3.42119385257662, 0.4] at [0.5999999999999999, -2.31059692628831, 0] roll 180.0; box [0.39999999999999997, 3.3204591567825315, 0.4] at [1.0, -2.260229578391266, 0] roll 180.0; box [0.39999999999999997, 3.3204591567825315, 0.4] at [-1.0, -2.260229578391266, 0] roll 270.0; box [0.39999999999999997, 3.42119385257662, 0.4] at [-0.6000000000000001, -2.31059692628831, 0] roll 270.0; box [0.39999999999999997, 3.480441152620633, 0.4] at [-0.20000000000000004, -2.3402205763103163, 0] roll 270.0; box [0.39999999999999997, 3.480441152620633, 0.4] at [0.19999999999999998, -2.3402205763103163, 0] roll 270.0; box [0.39999999999999997, 3.42119385257662, 0.4] at [0.5999999999999999, -2.31059692628831, 0] roll 270.0; box [0.39999999999999997, 3.3204591567825315, 0.4] at [1.0, -2.260229578391266, 0] roll 270.0. Visual: 4 broad timber paddles (width 2.4, radius 0.6..4.1, tips clipped to a circle, built from 6 strips each); axle y=4.16; lowest paddle edge 0.06 over the felt

## Timing check (`tools/timing_check.py`, 96 phases; actual fuzz counts per line)
- paddle_wheel [intended] tee shot into the icebreaker channel past the paddle wheel: blocked 36/96 (36 stops + 0 kicks), deflected 8, **Studio estimate 37.5%** (stops + 0.36 kicks), passed 54.2%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- paddle_wheel [ace] brute-force ace line: blocked 20/96 (20 stops + 0 kicks), deflected 8, **Studio estimate 20.8%** (stops + 0.36 kicks), passed 70.8%, traps 0


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-1.5, 7.5, -42.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs). Moving parts crossing the sightline: paddle_wheel 72% of its cycle.

## Playtest stats (walls; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.81 | 3.5% | 79% | 0.6% | 0 / 0 | [69, 1076, 438, 205, 97, 60, 29, 26] |
| average | 4.28 | 0.0% | 25% | 0.1% | 0 / 0 | [0, 52, 455, 593, 718, 152, 26, 4] |

## Props for the 3D modeler (decoration only, sizes in studs)
Icebreaker hull + deckhouse + funnel (P1, landmark); paddle wheel, 4 paddles r 4.1, pivot = hub, axis +Z (P1); bypass sign + felt arrow (P1); sailor snowpuffs (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-1.5, 0.0, -42.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `icebreaker` at [-3, 0, -21] (LANDMARK) size [16, 8, 6]: Beached toy icebreaker (red hull, cream deckhouse, red funnel puffing steam) straddling the channel; the 'hull' block x 1.2..8 plus a matching west half; the paddle wheel turns in a 2.4-wide slot through its stern
- `paddle_wheel` at [0, 4.16, -17.75] size [8.2, 8.2, 0.4]: Moving mesh: red-and-cream paddle wheel (pivot = hub, axis +Z), 4 broad timber paddles radius 4.1
- `sign_bypass` at [11.6, 0, -13] size [1.8, 3.2, 0.25]: Arrow sign 'Round the stern - no paddles' pointing into the bypass
- `felt_arrow_bypass` at [9.5, 0.0, -20.0] size [1.4, 0.01, 2.0]: Glowing felt arrow decal pointing -Z into the bypass
- `snowpuffs` at [-7.5, 0, -40] size [2.5, 2.2, 2.0]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) in sailor hats on a stack of crates beside the green; heads turn to follow the ball (visual only)

## Concept prompt
First-person VR view at eye height from a mini golf tee at night on a frozen shelf: a small toy icebreaker boat sits across a felt channel, its big red-and-cream paddle wheel turning over the felt; a red funnel puffs steam; a bypass lane curves round its stern to a green with a red flag; snowpuffs in sailor hats on crates. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
