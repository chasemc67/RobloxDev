# Hole 1: Lantern Gate (Par 2)

Zone: **Sunny Forest Edge**. Gimmick: **Gentle ramp + 45-degree deflector bank onto an offset green**.
Layout: `h01-layout.png`. Geometry: `holes.json` -> holes[0]. World offset [0, 0, 0], yaw 0.0.
Tee [0, 0, 0], cup [-9.5, 0.5, -26.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A timber torii-style **Lantern Gate** straddles the ramp: two posts outside the rails, a curved crossbeam ~6 studs (1.8 m) overhead and two big paper lanterns hanging just above head height in VR. Beyond it a red maple and a mossy boulder frame the green.

## Gimmick
Gentle ramp + 45-degree deflector bank onto an offset green.

## Intended shots
1. Roll up the lane and the gentle 0.5-stud ramp into the **45° timber deflector** at the back-right of the green. The board turns the ball west along the back of the green.
2. The cup is tucked in the **front-left corner** of the green, behind the corner where the lane rail meets the green. The second putt comes back toward you, 6–8 studs.

## Hole-in-one line
Brute-force search from the tee found ace lines (43 grid shots). The most robust: aim **244.3°** (atan2(dz,dx): direction (-0.43, -0.90) in x/z, i.e. 25.7° left of straight -Z), speed **19.8 studs/s** (100% power). The red dashed line on the layout PNG traces it.

## Challenge
Teaches the course's two basics: pace up a ramp, and reading a bank. The cup sits in the shadow of the lane corner, so you can't see a straight line to it from the tee. The safe play is a two-putt off the deflector.

## Moving parts / teleports (exact specs, also in holes.json)
- none

## Playtest stats (final, p4, 2000 plays per skill)
| Skill | Avg strokes | HIO | Capped (8) | Strokes 1..8 |
|---|---|---|---|---|
| good | 2.02 | 0.7% | 0.0% | [14, 1935, 51, 0, 0, 0, 0, 0] |
| average | 2.45 | 0.0% | 0.0% | [0, 1160, 784, 56, 0, 0, 0, 0] |

## Props for 3D Model Bot (decoration only, sizes in studs)
Lantern torii gate 9x7x1.2 (P1); 2 paper lanterns L (P1); welcome sign post 2x3x0.4 (P2); red maple 10x16x10 (P2); mossy boulder 4x3x4 (P2); deflector plank cladding along the `deflector` wall 10x1x0.5 (P1); leaf piles (P3).

Decoration anchors (position in hole-local studs):
- `lantern_gate` at [0, 0.25, -21] (LANDMARK) size [9, 7, 1.2]: Torii-style timber arch over the ramp, 2 paper lanterns hanging inside
- `mossy_boulder` at [-8, 0.5, -21] size [4, 3, 4]: Big mossy boulder outside the green's front-left rail
- `welcome_sign` at [-6, 0, 1] size [2, 3, 0.4]: Carved 'Lantern Grove - Hole 1' sign post
- `maple_tree` at [8, 0, -15] size [10, 16, 10]: Red maple outside right rail

## Concept prompt
First-person VR view from a putting tee at golfer eye height (about 5.5 ft), looking up a short emerald-green mini golf lane edged by low limestone rails with oak caps. A gentle ramp leads through a carved timber torii gate hung with two glowing amber paper lanterns, onto a wide raised green. A slanted timber board guards its back-right corner. The red flag is tucked low at the near-left corner of the green, half-hidden behind the rail corner. Late golden-hour autumn sun through red maples and golden birches, drifting leaves, a mossy boulder, soft haze, warm cozy fairy-forest storybook style, Roblox-friendly chunky shapes.
