# Hole 16: Moonwell (Par 2)

Zone: **Skylight Summit**. Gimmick: **Funnel: a moonstone well bowl gathers the ball into its spout, with the cup set off the funnel's exit line**.
Layout: `h16-layout.png`. Geometry: `holes.json` -> holes[15]. World placement (from `world/world.json`): origin [-110.0, 222.0, -300.0], yaw 0.0.
Tee [0, 0, 0], cup [3.2, -0.8, -35.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The **Moonwell**: a moonstone funnel bowl with silver inlay, ringed with glowing ice crystals, draining through a crescent-moon spout.

## Gimmick
Funnel: a moonstone well bowl gathers the ball into its spout, with the cup set off the funnel's exit line.

## Intended shots
1. Roll into the well: its two slopes gather the ball into the trough and out of the spout.
2. The cup sits off the spout's line, so it is usually a short second putt; a ball that leaves the spout angling right can drop.

## Hole-in-one line
Brute-force search from the tee found ace lines (76 grid shots). The most robust: aim **257.5°** (atan2(dz,dx): direction (-0.22, -0.98) in x/z, i.e. 12.5° left of straight -Z), speed **16.8 studs/s** (85% power). The red dashed line on the layout PNG traces it.

## Challenge
Funnel with the cup deliberately off the exit line so the funnel doesn't make it an ace machine.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [3.2, 6.7, -35.5]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (p2; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.26 | 7.1% | 76% | 0.0% | 0 / 0 | [143, 1386, 303, 144, 19, 4, 1, 0] |
| average | 2.78 | 0.0% | 44% | 0.0% | 0 / 0 | [0, 887, 762, 270, 68, 11, 2, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Moonstone coping and slope dressing (P1, landmark); crystal clusters on the rim (P2); crescent spout glow decal (P1); telescope snowpuff (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [3.2, -0.8, -35.5] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `moonwell` at [0, -0.8, -21.0] (LANDMARK) size [20, 2, 18]: Moonstone well: pale pearl stone coping round the funnel, the two felt slopes dressed as worn moonstone flags with silver inlay, glowing ice-crystal clusters on the rim (outside the rails), a spout carved like a crescent moon at the exit
- `spout_glow` at [0.0, -0.8, -29.0] size [2.0, 0.01, 2.0]: Crescent-moon glow decal in the trough pointing at the spout
- `moon_view` at [0, 0, -300] size [1, 1, 1]: The low moon sits behind the player (bearing 220); from the green you see it framed by the Spire
- `snowpuffs` at [11.5, 0, -36] size [2.5, 2.2, 2.0]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) gazing at the moon through a little brass telescope; heads turn to follow the ball (visual only)

## Concept prompt
First-person VR view at eye height from a mini golf tee at night on the highest summit island: a round pearly moonstone well funnels down to a crescent-shaped spout, glowing ice crystals on its rim, a green beyond with a red flag; a snowpuff peers through a brass telescope; every lower island glitters below in the lilac cloud sea. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
