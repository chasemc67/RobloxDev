# Hole 2: Acorn Ledge (Par 2)

Zone: **Sunny Forest Edge**. Gimmick: **Drop between levels through one of two chutes either side of a stump; rabbit-hole pit punishes overcooking the left chute**.
Layout: `h02-layout.png`. Geometry: `holes.json` -> holes[1]. World offset [34, 0, 4], yaw 0.0.
Tee [0, 0, 0], cup [2.5, -1.5, -35] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A **giant acorn** (3x4x3) sits on an old stump that splits the end of the upper lane into two 2.5-stud chutes. Below the 1.5-stud (0.45 m) ledge is a wide lower green with a mossy **rabbit hole** on the left.

## Gimmick
Drop between levels through one of two chutes either side of a stump; rabbit-hole pit punishes overcooking the left chute.

## Intended shots
1. Pick a chute. The **left chute** is the aggressive line: a firm putt drops through it and runs diagonally across the lower green toward the cup in the far right corner. Overcook it and the rabbit hole waits. The **right chute** is safer: drop through softly and leave a short uphill-free putt.
2. Putt out on the flat lower green.

## Hole-in-one line
Brute-force search from the tee found ace lines (45 grid shots). The most robust: aim **252.0°** (atan2(dz,dx): direction (-0.31, -0.95) in x/z, i.e. 18.0° left of straight -Z), speed **18.7 studs/s** (94% power). The red dashed line on the layout PNG traces it.

## Challenge
First drop on the course. Players learn that the ball keeps about 80% of its speed after falling, and that the line changes once it lands. The rabbit hole punishes left-chute shots that are too hard (+1 and replay). Arrow signs and glowing felt arrows show both chutes from the tee, and the 7.5-stud flag is visible over the ledge.

## Moving parts / teleports (exact specs, also in holes.json)
- none

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) standing in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [2.5, 6.0, -35]; visual only, no collision. Line of sight from the tee eye (5.5 studs above the tee) to the flag top: **visible** (min clearance over rails/felt/props +1.76 studs).

## Playtest stats (final, r5b, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 2.01 | 8.5% | 0.0% | [169, 1646, 185, 0, 0, 0, 0, 0] |
| average | 2.63 | 0.0% | 0.0% | [0, 834, 1071, 91, 4, 0, 0, 0] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Giant acorn 3x4x3 (P1); stump (cladding for `stump` block 3x1.2x1) (P1); lantern posts at both chutes 0.5x3x0.5 (P1); rabbit-hole rim 3x0.5x3 (P2); squirrel hut on post 3x5x3 (P3); leaf piles (P3); flag 7.5 (P1); **chute signs (new)**: two carved arrow signs on posts outside the rails at (±5.2, 0, -16.5) 1.8x3.2x0.25 ('Bold Line' left with a rabbit icon, 'Safe Line' right), and two glowing leaf-arrow decals flush on the felt at (±2.75, 0, -17) 1.4x2.0 pointing into the chutes (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [2.5, -1.5, -35] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `giant_acorn` at [0, 0.0, -19.5] (LANDMARK) size [3, 4, 3]: Giant acorn (cap + nut) sitting on the stump between the chutes (size incl. the 1.2 stump)
- `rabbit_hole_rim` at [-5, -1.5, -30] size [3, 0.5, 3]: Rabbit-hole rim of roots and moss around the pit
- `squirrel_hut` at [11, -1.5, -28] size [3, 5, 3]: Tiny squirrel hut on a post outside the right rail
- `ledge_lanterns` at [-4.5, 0, -19.5] size [0.5, 3, 0.5]: Lantern posts at both chute edges (x -4.5 and +4.5, on the rail line)
- `chute_sign_left` at [-5.2, 0, -16.5] size [1.8, 3.2, 0.25]: Carved arrow sign on a post outside the left rail, arrow board angled to point through the LEFT chute; text 'Bold Line' + small rabbit icon (warns of the rabbit hole)
- `chute_sign_right` at [5.2, 0, -16.5] size [1.8, 3.2, 0.25]: Carved arrow sign on a post outside the right rail, arrow board angled to point through the RIGHT chute; text 'Safe Line'
- `chute_arrow_left` at [-2.75, 0.0, -17.0] size [1.4, 0.01, 2.0]: Glowing leaf-arrow decal flush on the felt (0.01 thick), pointing -Z into the left chute
- `chute_arrow_right` at [2.75, 0.0, -17.0] size [1.4, 0.01, 2.0]: Glowing leaf-arrow decal flush on the felt (0.01 thick), pointing -Z into the right chute

## Concept prompt
First-person VR view from a mini golf tee at eye height, looking down a straight green felt lane with stone-and-oak rails. At the end of the lane a huge glossy acorn sits on a mossy stump, splitting the lane edge into two narrow gaps with lantern posts. Beyond and below, a wide lower green with a red flag in the far right corner and a small mossy rabbit hole on the left. Autumn forest edge in warm afternoon light, orange and gold leaves drifting, a tiny squirrel hut on a post, soft hazy sunbeams, cozy storybook fairy-forest style.
