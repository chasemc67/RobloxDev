# Hole 1: Trailhead Gate (Par 2)

Zone: **Sugarloaf Junction**. Gimmick: **Bank shot: a striped boulder's 45-degree face turns the ball east onto an offset green**.
Layout: `h01-layout.png`. Geometry: `holes.json` -> holes[0]. World placement (from `world/world.json`): origin [60.0, 18.0, 470.0], yaw 0.0.
Tee [0, 0, 0], cup [6.0, 0.0, -30.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A candy-striped timber **trailhead arch** spans the lane with a swirl-lollipop sign; at the far end a big pink-and-cream striped **boulder** sits in the back-left corner of the green, its flat south-east face turned 45° to the lane.

## Gimmick
Bank shot: a striped boulder's 45-degree face turns the ball east onto an offset green.

## Intended shots
1. Roll straight up the 7-wide lane into the boulder's 45° face: it turns the ball east along the back of the offset green.
2. The cup sits off that line toward the front of the green, so the second putt comes back toward you (two-putt par).

## Hole-in-one line
Brute-force search from the tee found ace lines (35 grid shots). The most robust: aim **249.5°** (atan2(dz,dx): direction (-0.35, -0.94) in x/z, i.e. 20.5° left of straight -Z), speed **19.0 studs/s** (96% power). The red dashed line on the layout PNG traces it.

## Challenge
Teaches the bank. Pace matters more than line: too soft and the ball dies on the face, too firm and it runs the length of the green into the east rail. The ace needs a slightly angled tee shot so the bank sends the ball back toward the cup.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [6.0, 7.5, -30.5]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (p7; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 1.95 | 6.6% | 99% | 0.0% | 0 / 0 | [132, 1851, 11, 6, 0, 0, 0, 0] |
| average | 2.38 | 0.0% | 67% | 0.0% | 0 / 0 | [0, 1349, 563, 71, 17, 0, 0, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Trailhead arch 9.5x10x1.2 with lollipop sign (P1); striped boulder dressing over the 3x3 bumper turned 45°, visual up to 6 tall, must cover the collider at felt level (P1); lollipop saguaro 4x12x4 (P2); hitching post + trough (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [6.0, 0.0, -30.5] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `trailhead_arch` at [0, 0, -12] (LANDMARK) size [9.5, 10, 1.2]: Candy-striped timber trailhead arch over the lane with a hanging swirl-lollipop sign 'Sugarloaf Canyon - Hole 1'; posts outside the rails at x +-4.25, crossbeam bottom 8 above the felt
- `striped_boulder` at [-1.3, 0, -35.8] size [4.4, 6, 4.4]: Striped sandstone boulder (pink/cream bands) dressing the 3x3 bumper turned 45 deg; its flat south-east face is the bank. Visual may rise to 6 studs but must cover the collider exactly at felt level
- `lollipop_cactus_1` at [6, 0, -18] size [4, 12, 4]: Saguaro wearing a swirl lollipop, outside the green's south rail
- `hitching_post` at [-6, 0, -4] size [3, 2, 1]: Hitching post and water trough outside the west rail

## Concept prompt
First-person VR view from a mini golf tee at eye height on a sandy canyon floor: a straight emerald felt lane with pink sandstone rails runs under a candy-striped timber trailhead arch hung with a giant swirl lollipop sign, toward a huge pink-and-cream striped boulder in the far left corner and a green that opens to the right with a red flag. Old Sugarloaf, a striped dome, on the skyline. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
