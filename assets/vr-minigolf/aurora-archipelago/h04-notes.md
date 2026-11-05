# Hole 4: Glissade (Par 3)

Zone: **Steamwhistle Lagoons**. Gimmick: **Ice felt: a glassy low-friction strip where the ball barely slows; pace control into a snow-felt green**.
Layout: `h04-layout.png`. Geometry: `holes.json` -> holes[3]. World placement (from `world/world.json`): origin [185.0, 84.0, 470.0], yaw 0.0.
Tee [0, 0, 0], cup [9.0, 0.15, -54.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
Two **frosted palms** lean over a long glassy **ice slide** in the steam of Steamwhistle Lagoon; the snow-felt green waits at the end.

## Gimmick
Ice felt: a glassy low-friction strip where the ball barely slows; pace control into a snow-felt green.

## Intended shots
1. Stroke the ball gently onto the ice: it barely slows on the glassy strip (about 0.35 x normal rolling deceleration) and glides onto the snow-felt green.
2. Putt out on normal felt. A perfectly weighted tee shot can glide all the way to the cup.

## Hole-in-one line
Brute-force search from the tee found ace lines (3 grid shots). The most robust: aim **248.5°** (atan2(dz,dx): direction (-0.37, -0.93) in x/z, i.e. 21.5° left of straight -Z), speed **19.8 studs/s** (100% power). The red dashed line on the layout PNG traces it.

## Challenge
Pace control. On ice a 5% power error moves the finish several studs; too hard and the ball runs to the back rail and bounces back, too soft and it stops on the ice where every putt is touchy. **The ice friction must be calibrated in Studio** (see the physics block).

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [9.0, 7.65, -54.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.31 studs).

## Playtest stats (after-late; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.04 | 3.9% | 100% | 0.0% | 0 / 0 | [77, 1763, 160, 0, 0, 0, 0, 0] |
| average | 2.57 | 0.0% | 97% | 0.0% | 0 / 0 | [0, 907, 1041, 51, 1, 0, 0, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Glassy ice felt strip (Glass look, Transparency 0.15, Reflectance 0.15) over a custom-friction collider (P1); frosted palms x2 (P1, landmark); ice-edge snowflake decal (P1); steam vents (P2); snowpuff on a belly-slide (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [9.0, 0.15, -54.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `frosted_palms` at [-8.0, 0, -22] (LANDMARK) size [6, 12, 6]: Two frosted palms (teal fronds dusted white) leaning over the ice slide from outside the west rail; fronds stay >= 8 above the felt
- `ice_sheen` at [0, 0, -24.0] size [8.0, 0.02, 32.0]: Glassy ice felt #9FE3F2 (Glass look: Transparency 0.15, Reflectance 0.15) over the collider; chevron frost lines every 4 studs; the strip is 8 wide and 32 long
- `steam_vents` at [9.0, 0, -20] size [2, 1.5, 6]: Little basalt steam vents puffing warm mist outside the east rail (particles only)
- `snowpuffs` at [-9.0, 0, -44] size [2.5, 2.2, 2.0]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) on a snow bank by the green, one sliding past on its belly in a bobble hat; heads turn to follow the ball (visual only)
- `ice_warning` at [0.0, 0.0, -7.0] size [3.0, 0.01, 1.2]: Felt decal at the ice edge: a snowflake and three chevrons 'ICE - gentle!'

## Concept prompt
First-person VR view at eye height from a mini golf tee at night beside steaming turquoise hot springs: a short felt lane runs onto a long shiny glassy ice strip that reflects the lantern light and the green and violet aurora, ending at a wide snow-felt green with a red flag; frosted palm trees dusted with snow lean over the slide; steam curls past brass lanterns. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
