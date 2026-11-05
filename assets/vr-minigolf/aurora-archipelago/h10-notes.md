# Hole 10: Bobsled Bend (Par 3)

Zone: **Driftfloe Shelf**. Gimmick: **Half-pipe: an S-bend bobsled channel with banked felt walls; ride high to carry the bend**.
Layout: `h10-layout.png`. Geometry: `holes.json` -> holes[9]. World placement (from `world/world.json`): origin [510.0, 146.0, 60.0], yaw 90.0.
Tee [0, 0, 0], cup [-0.5, 0.0, -42.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A striped **bobsled start hut** with brass bells stands at the top of an icy S-bend bobsled run of packed snow.

## Gimmick
Half-pipe: an S-bend bobsled channel with banked felt walls; ride high to carry the bend.

## Intended shots
1. Tee shot into the first (right-hand) bend, riding the outside bank round.
2. Up the middle straight and round the second (left-hand) bend.
3. Out of the run onto the green. A perfect firm tee shot rides both banks and carries to the cup.

## Hole-in-one line
Brute-force search from the tee found ace lines (6 grid shots). The most robust: aim **288.0°** (atan2(dz,dx): direction (0.31, -0.95) in x/z, i.e. 18.0° right of straight -Z), speed **19.8 studs/s** (100% power). The red dashed line on the layout PNG traces it.

## Challenge
Ride the banks: pace decides how high the ball rides and where it leaves each bend.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-0.5, 7.5, -42.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +4.90 studs).

## Playtest stats (p2; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.63 | 7.4% | 99% | 0.0% | 0 / 0 | [148, 473, 1350, 29, 0, 0, 0, 0] |
| average | 3.31 | 0.0% | 69% | 0.0% | 0 / 0 | [0, 14, 1367, 602, 17, 0, 0, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Bobsled start hut with bells (P1, landmark); packed-snow run walls kept low (P1); ice lips on the rails (P1); cheering snowpuff bobsled teams (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-0.5, 0.0, -42.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `bobsled_hut` at [-7.5, 0, -6] (LANDMARK) size [5, 7, 5]: Striped red-and-cream bobsled start hut with brass bells and a parked toy bobsled, outside the run's west wall: the landmark
- `snow_walls` at [3, 0, -22] size [16, 4, 46]: Rounded packed-snow bobsled walls hugging the run outside the rails (dressing up to 4 studs, ice-blue glaze on the inside faces); kept low so the flag stays visible
- `run_lip` at [3, 0.3, -22] size [1, 0.4, 46]: Rounded ice lip on top of both run rails following the S (felt banks 1.5 wide rise 0.3)
- `snowpuffs` at [10.0, 0, -36] size [2.5, 2.2, 2.0]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) in a row of bobsleds outside the east wall, cheering with tiny flags; heads turn to follow the ball (visual only)

## Concept prompt
First-person VR view at eye height from a mini golf tee at night: a green felt bobsled channel with banked icy sides curves right, then left, between rounded packed-snow walls; a striped bobsled start hut with brass bells stands beside the tee; a red flag waits at the end; snowpuffs cheer with tiny flags; aurora and the frozen Floe Pond beyond. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
