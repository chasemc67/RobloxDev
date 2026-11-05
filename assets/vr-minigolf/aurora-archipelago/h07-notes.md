# Hole 7: Mogul Meadow (Par 3)

Zone: **Candyfrost Reef**. Gimmick: **Rolling dips: four snow moguls built from opposing planar slopes; pace the ball over the humps**.
Layout: `h07-layout.png`. Geometry: `holes.json` -> holes[6]. World placement (from `world/world.json`): origin [365.0, 112.0, 330.0], yaw 0.0.
Tee [0, 0, 0], cup [6.0, 0.0, -53.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
Candy-bright **coral-ice fans** glow in clumps along a snowy meadow; the lane runs over four rounded snow **moguls**.

## Gimmick
Rolling dips: four snow moguls built from opposing planar slopes; pace the ball over the humps.

## Intended shots
1. A firm, straight tee shot over the four moguls (each a hump and a hollow of opposing planar slopes) onto the green.
2. Putt out.

## Hole-in-one line
Brute-force search from the tee found ace lines (13 grid shots). The most robust: aim **249.5°** (atan2(dz,dx): direction (-0.35, -0.94) in x/z, i.e. 20.5° left of straight -Z), speed **19.0 studs/s** (96% power). The red dashed line on the layout PNG traces it.

## Challenge
Pace: too soft and the ball settles in a hollow between moguls; too hard and it runs to the back rail. The humps rise +0.5 and dip -0.3.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [6.0, 7.5, -53.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.23 studs).

## Playtest stats (p2; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.40 | 5.9% | 98% | 0.0% | 0 / 0 | [118, 995, 846, 41, 0, 0, 0, 0] |
| average | 2.83 | 0.0% | 86% | 0.0% | 0 / 0 | [0, 686, 1040, 207, 58, 7, 1, 1] |

## Props for the 3D modeler (decoration only, sizes in studs)
Coral-ice fan clumps in candy colours outside both rails (P1, landmark); snow-capped mogul rail trim (P1); toboggan snowpuff (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [6.0, 0.0, -53.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `coral_fans` at [-12.0, 0, -24] (LANDMARK) size [3, 6, 30]: Candy coral-ice fans (bubblegum #FF6FB5, tangerine #FFA552, mint #6FFFD2, neon cores) in clumps outside both rails along the moguls; nothing over the felt
- `mogul_trim` at [0, 0, -22.0] size [9, 0.4, 28.0]: Snow-capped timber rail trim following the 4 moguls (felt humps rise to +0.6 and dip to -0.4); thick rounded snow on the hump crests
- `snowpuffs` at [11.5, 0, -46] size [2.5, 2.2, 2.0]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) riding a tiny toboggan over a mogul-shaped drift outside the green's east rail; heads turn to follow the ball (visual only)

## Concept prompt
First-person VR view at eye height from a mini golf tee at night: a felt lane rolls over four rounded snowy humps and hollows toward a wide green with a red flag; glowing candy-coloured coral made of ice (bubblegum pink, tangerine, mint) lines both sides; a snowpuff rides a tiny toboggan; aurora and stars above, floating islands in the distance. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
