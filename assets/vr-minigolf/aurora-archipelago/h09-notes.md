# Hole 9: Conch Shortcut (Par 4)

Zone: **Candyfrost Reef**. Gimmick: **Teleport: sink the ball into a giant coral-ice conch at the end of a rail-less reef spit and it shoots out of a second shell by the green, or play the long reef route round the lagoon**.
Layout: `h09-layout.png`. Geometry: `holes.json` -> holes[8]. World placement (from `world/world.json`): origin [535.0, 112.0, 230.0], yaw 0.0.
Tee [0, 0, 0], cup [2.0, 0.0, -64.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
Two **giant spiral conch shells** of candy coral-ice: one lies at the end of a rail-less reef spit over a shallow turquoise lagoon, its twin sits on the green's east edge.

## Gimmick
Teleport: sink the ball into a giant coral-ice conch at the end of a rail-less reef spit and it shoots out of a second shell by the green, or play the long reef route round the lagoon.

## Intended shots
**Shortcut:** a measured putt down the rail-less spit into the conch ring: the twin conch blows the ball out toward the cup (birdie or better).
**Long route:** bank into the reef walk on the west, play up it, then onto the green (par).

## Hole-in-one line
Brute-force search from the tee found ace lines (30 grid shots). The most robust: aim **269.5°** (atan2(dz,dx): direction (-0.01, -1.00) in x/z, i.e. 0.5° left of straight -Z), speed **16.8 studs/s** (85% power). The red dashed line on the layout PNG traces it.

## Challenge
Risk and reward: the spit has no rails and a ball in the lagoon goes back to where it was struck (+1).

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **teleport conch**: entry [0.0, 0.0, -33.0] r 0.3 -> exit [11.0, 0.0, -67.0] dir [-0.9487, 0.3162], exit speed = clamp(in x 0.7, 3.0, 7.0) studs/s. Glowing aurora-lime ring flush in the spit felt 2 studs from its open end, in the mouth of a giant spiral conch -> the twin conch on the green's east side blows the ball out, aimed at the cup
- **hazard reef_lagoon** (water): +1 stroke, ball back to where the stroke started


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [2.0, 7.5, -64.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +1.99 studs).

## Playtest stats (p2; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 3.42 | 4.2% | 76% | 0.5% | 0 / 0 | [83, 383, 841, 204, 373, 35, 71, 10] |
| average | 5.06 | 0.0% | 23% | 0.7% | 0 / 0 | [0, 1, 0, 451, 1062, 414, 53, 19] |

## Props for the 3D modeler (decoration only, sizes in studs)
Conch pair (entry over the ring; exit aimed at the cup) (P1, landmark); spit deck (P1); reef lagoon with coral heads (P2); route signs + felt arrows (P1); snorkelling snowpuffs (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [2.0, 0.0, -64.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `conch_entry` at [0.0, 0.0, -34.0] (LANDMARK) size [5, 4.5, 5]: Giant spiral conch of candy coral-ice (pink/cream, glowing lip) lying at the end of the spit with its mouth over the ring: the ball rolls in. Shell body stays behind the ring and below 5 studs over the spit end
- `conch_exit` at [11.0, 0.0, -67.0] size [4, 4, 4]: Twin conch on the green's east edge, mouth turned toward the cup (teleport exit, a puff of sparkle)
- `reef_lagoon` at [1.5, -1.2, -39] size [25, 1, 34]: Shallow turquoise reef lagoon with glowing coral-ice heads under the water (hazard: +1, back to the stroke start)
- `sign_spit` at [2.2, 0, -20] size [1.6, 2.6, 0.2]: Sign 'Conch express - shoot the shell!' at the spit root
- `sign_route` at [-16.6, 0, -24] size [1.8, 3.2, 0.25]: Sign 'Reef Walk - the long way' pointing north along the reef route
- `felt_arrow_spit` at [0.0, 0.0, -20.0] size [1.4, 0.01, 2.0]: Glowing felt arrow decal pointing -Z onto the spit
- `felt_arrow_route` at [-13.5, 0.0, -24.0] size [1.4, 0.01, 2.0]: Glowing felt arrow decal pointing -Z up the reef route
- `snowpuffs` at [-18.5, 0, -40] size [2.5, 2.2, 2.0]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) snorkelling at the lagoon edge outside the reef route's west rail; heads turn to follow the ball (visual only)

## Concept prompt
First-person VR view at eye height from a mini golf tee at night on a coral reef island: a felt lane leads to a narrow rail-less spit running out over a shallow glowing turquoise lagoon to a giant pink spiral conch shell; a twin conch sits beside a far green with a red flag; a railed reef path curves round the left; coral-ice glows under the water. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
