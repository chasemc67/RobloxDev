# Hole 18: Halo Arch (Par 4)

Zone: **Skylight Summit**. Gimmick: **Finale: read two crystal banks round the plaza, climb the ramp onto the raised green under the Halo Arch**.
Layout: `h18-layout.png`. Geometry: `holes.json` -> holes[17]. World placement (from `world/world.json`): origin [-235.0, 222.0, -232.0], yaw 0.0.
Tee [0, 0, 0], cup [-4.0, 0.5, -46.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The **Halo Arch**, a translucent glowing ice arch 34 studs tall, spans the raised final green and frames the aurora; the Starfrost Spire rises to the south-east and every island lies below.

## Gimmick
Finale: read two crystal banks round the plaza, climb the ramp onto the raised green under the Halo Arch.

## Intended shots
1. Tee shot up the lane into the north-east crystal bank: it turns the ball west across the plaza.
2. The south-west crystal bank turns it north up the ramp onto the raised green under the arch.
3. Putt out; the cup sits east of the ramp line.

## Hole-in-one line
Brute-force search from the tee found ace lines (2 grid shots). The most robust: aim **257.0°** (atan2(dz,dx): direction (-0.22, -0.97) in x/z, i.e. 13.0° left of straight -Z), speed **18.3 studs/s** (93% power). The red dashed line on the layout PNG traces it.

## Challenge
Finale: read two crystal banks and the 1.2-stud ramp. Grand but not punishing.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none


## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-4.0, 8.0, -46.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +4.12 studs).

## Playtest stats (after-late; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 3.59 | 0.5% | 94% | 0.0% | 0 / 0 | [11, 191, 532, 1150, 110, 6, 0, 0] |
| average | 4.18 | 0.0% | 68% | 0.0% | 0 / 0 | [0, 0, 319, 1037, 611, 31, 2, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Halo Arch (P1, landmark, world dressing; opening 18 clear); crystal walls over both banks (P1); ramp lanterns (P2); felt arrows + chevrons (P1); snowpuff grandstand (P2); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-4.0, 0.5, -46.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `halo_arch` at [0, 0.5, -52] (LANDMARK) size [46, 34, 4]: Halo Arch: a translucent glowing ice arch (Glass 0.3 + crystal-core neon) 46 wide and 34 tall spanning the green east-west; its feet stand outside the footprint at x +-23 (world dressing), clear opening 18 high, so nothing is lower than 18 over the felt; it frames the aurora to the north
- `crystal_bank_ne_deco` at [0.0, 0, -26.0] size [9, 4, 2]: Faceted ice-crystal wall dressing the 45-degree banked felt and its backing rail (crystal clusters 3-5 tall behind the rail, glowing cyan); the banked felt itself is frosted glass-green
- `crystal_bank_sw_deco` at [-11.5, 0, -22.0] size [9, 4, 2]: Faceted ice-crystal wall dressing the 45-degree banked felt and its backing rail (crystal clusters 3-5 tall behind the rail, glowing cyan); the banked felt itself is frosted glass-green
- `ramp_lanterns` at [-8.5, 0, -33.0] size [1, 9, 10]: Brass lanterns on posts lining the ramp's east side (outside the rail)
- `felt_arrow_bank` at [0.0, 0.0, -10.0] size [2.0, 0.01, 2.6]: Glowing felt arrow decal: 'off the crystals, round and up'
- `crystal_chute` at [-6.5, 0.25, -33.0] size [3.5999999999999996, 3, 10]: The Halo Run: a narrow 1.6-wide crystal chute (rails dressed as glowing ice-crystal walls) straight up through the plaza's north wall onto the green: the risky shortcut / ace line
- `ramp_chevrons` at [-13.5, 0.25, -33.0] size [6, 0.01, 2]: Felt chevrons up the ramp pointing -Z
- `snowpuffs` at [14.0, 0.5, -44] size [6, 3, 4]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) in a grandstand of snow blocks beside the final green, holding up score cards; heads turn to follow the ball (visual only)

## Concept prompt
First-person VR view at eye height from a mini golf tee at night on the highest summit: a felt lane runs into faceted glowing ice-crystal bank walls, a ramp climbs to a raised green under a huge translucent glowing ice arch framing the green and violet aurora; a red flag on the green; snowpuffs in a grandstand of snow blocks; the giant Starfrost Spire glows to the right. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
