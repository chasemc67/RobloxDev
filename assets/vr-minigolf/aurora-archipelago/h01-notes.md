# Hole 1: Lantern Quay (Par 2)

Zone: **Lanternfall Landing**. Gimmick: **Bank shot: a snow-capped boulder's 45-degree face turns the ball east onto an offset green**.
Layout: `h01-layout.png`. Geometry: `holes.json` -> holes[0]. World placement (from `world/world.json`): origin [-150.0, 60.0, 545.0], yaw 0.0.
Tee [0, 0, 0], cup [6.0, 0.0, -30.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A big brass **harbour lantern** on a frosted driftwood post glows beside the lane at Lantern Quay; at the far end a chunky snow-capped slate **boulder** sits in the back-left corner of the green, its flat south-east face turned 45° to the lane. The Starfrost Spire rises straight ahead.

## Gimmick
Bank shot: a snow-capped boulder's 45-degree face turns the ball east onto an offset green.

## Intended shots
1. Roll straight up the 7-wide quay lane into the boulder's 45° face: it turns the ball east along the back of the offset green.
2. The cup sits off that line toward the front of the green, so the second putt comes back toward you (two-putt par).

## Hole-in-one line
Brute-force search from the tee found ace lines (35 grid shots). The most robust: aim **249.5°** (atan2(dz,dx): direction (-0.35, -0.94) in x/z, i.e. 20.5° left of straight -Z), speed **19.0 studs/s** (96% power). The red dashed line on the layout PNG traces it.

## Challenge
Teaches the bank. Pace matters more than line: too soft and the ball dies on the face, too firm and it runs the length of the green into the east rail. The ace needs a slightly angled tee shot so the bank sends the ball back toward the cup.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [6.0, 7.5, -30.5]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (p2; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 1.95 | 6.6% | 99% | 0.0% | 0 / 0 | [132, 1851, 11, 6, 0, 0, 0, 0] |
| average | 2.38 | 0.0% | 67% | 0.0% | 0 / 0 | [0, 1349, 563, 71, 17, 0, 0, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Harbour lantern on a 9-stud driftwood post (P1, landmark); snow-capped boulder over the 3x3 bumper turned 45° (visual up to 5 tall, must cover the collider at felt level) (P1); mooring bollards (P2); snowpuff trio (P2); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [6.0, 0.0, -30.5] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `harbour_lantern` at [-6.0, 0, -24.0] (LANDMARK) size [0.9, 9.0, 0.9]: Brass lantern (on a 9-stud warm-timber post, PointLight #FFB861, range 14, brightness 0.8) beside the west rail where the lane meets the green: the hole's landmark. A big ship's lantern (1.2 x 1.6) hangs from a driftwood post with frosted rope; it never overhangs the felt
- `snow_boulder` at [-1.3, 0, -35.8] size [4.4, 5, 4.4]: Chunky slate-violet boulder with a thick rounded snow cap dressing the 3x3 bumper turned 45 deg; its flat south-east face is the bank (a faint aurora-mint glow line marks it). Visual may rise to 5 studs but must cover the collider exactly at felt level
- `quay_bollards` at [5.5, 0, -12] size [1.2, 1.4, 4]: Two brass-capped timber mooring bollards with frosted rope coils outside the east rail
- `snowpuffs` at [-6.5, 0, -8] size [2.5, 2.2, 2.0]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) three of them on a snow drift outside the west rail, the smallest waving a flipper at the tee; heads turn to follow the ball (visual only)
- `spire_view` at [0, 0, -400] size [1, 1, 1]: Starfrost Spire straight up the lane (world landmark, tip y 340): the hole is aimed at it
- `bank_arrow` at [0.0, 0.0, -22.0] size [1.4, 0.01, 2.0]: Glowing mint felt arrow decal curving right: 'bank it off the boulder'

## Concept prompt
First-person VR view from a mini golf tee at eye height on a snowy harbour quay at night: a straight green felt lane with chunky snow-capped timber rails runs past a big glowing brass harbour lantern on a driftwood post toward a huge snow-capped slate boulder in the far left corner, where the green opens to the right with a red flag; three round snowpuffs watch from a drift; the giant glowing Starfrost Spire rises dead ahead over the lilac cloud sea. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
