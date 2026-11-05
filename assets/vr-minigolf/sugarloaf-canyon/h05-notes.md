# Hole 5: Echo Slot (Par 3)

Zone: **Rock Candy Narrows**. Gimmick: **Half-pipe: an S-bend U-channel with banked felt walls; ride high to carry the bend**.
Layout: `h05-layout.png`. Geometry: `holes.json` -> holes[4]. World placement (from `world/world.json`): origin [280.0, 22.0, 326.0], yaw 0.0.
Tee [0, 0, 0], cup [-0.5, 0.0, -42.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
Wave-carved **Echo Slot**: smooth pink-and-cream walls curve around an S-bend half-pipe channel whose felt banks rise either side.

## Gimmick
Half-pipe: an S-bend U-channel with banked felt walls; ride high to carry the bend.

## Intended shots
1. Tee shot into the first (right-hand) bend, riding the outside bank round.
2. Up the middle straight and round the second (left-hand) bend.
3. Out of the channel mouth onto the green.
A perfect max-power tee shot rides both banks and carries to the cup.

## Hole-in-one line
Brute-force search from the tee found ace lines (6 grid shots). The most robust: aim **288.0°** (atan2(dz,dx): direction (0.31, -0.95) in x/z, i.e. 18.0° right of straight -Z), speed **19.8 studs/s** (100% power). The red dashed line on the layout PNG traces it.

## Challenge
Ride the banks: pace decides how high the ball rides and where it leaves each bend. The slot walls hide the flag from the tee by design: a glowing rock-candy crystal hangs 9.5 studs over the cup as the cue.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-0.5, 7.5, -42.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +4.90 studs).

## Playtest stats (p7; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.62 | 7.3% | 99% | 0.0% | 0 / 0 | [146, 498, 1329, 27, 0, 0, 0, 0] |
| average | 3.33 | 0.0% | 67% | 0.0% | 0 / 0 | [0, 16, 1332, 632, 20, 0, 0, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Wave-carved slot-wall dressing hugging the channel (P1, landmark); rounded sandstone lips on the half-pipe rails (P1); hanging crystal cue over the cup, no collision (P1); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-0.5, 0.0, -42.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `echo_walls` at [3, 0, -22] (LANDMARK) size [16, 44, 46]: Wave-carved slot walls: smooth curving pink/cream sandstone hugging the half-pipe outside the rails, rising 44 studs; the sky is a pink ribbon overhead. They hide the flag from the tee by design (see the crystal cue)
- `pipe_lip` at [3, 0.3, -22] size [1, 0.4, 46]: Rounded sandstone lip on top of both half-pipe rails following the S (felt banks 1.5 wide rise 0.3)
- `crystal_cue` at [-0.5, 9.5, -42.0] size [1.2, 2, 1.2]: Glowing pink rock-candy crystal hanging 9.5 studs over the cup from a rope between the slot walls: the visual cue for the hidden flag (decoration only, no collision, 8+ studs above the felt)

## Concept prompt
First-person VR view at eye height in a deep slot canyon: a green felt half-pipe channel with gently banked sides curves right, then left, between wave-smoothed pink and cream sandstone walls; a glowing pink crystal hangs on a rope far ahead over the hidden cup; soft bounce light. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
