# Hole 15: Frozen Falls (Par 2)

Zone: **Icefall Terraces**. Gimmick: **Drop between levels: putt over the lip of a frozen waterfall and fall 4 studs into a basin green**.
Layout: `h15-layout.png`. Geometry: `holes.json` -> holes[14]. World placement (from `world/world.json`): origin [12.0, 182.0, -334.0], yaw 0.0.
Tee [0, 0, 0], cup [3.5, -4.0, -31.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The **Great Frozen Falls** pour 146 studs off the terrace edge into the clouds right beside the basin green; the hole's own lip is a little frozen fall.

## Gimmick
Drop between levels: putt over the lip of a frozen waterfall and fall 4 studs into a basin green.

## Intended shots
1. Putt over the open lip: the ball drops 4 studs into the basin (keeping ~80% of its speed) and rolls toward the cup.
2. Tap in. The basin's back slope returns firm shots.

## Hole-in-one line
Brute-force search from the tee found ace lines (207 grid shots). The most robust: aim **315.5°** (atan2(dz,dx): direction (0.71, -0.70) in x/z, i.e. 45.5° right of straight -Z), speed **18.3 studs/s** (93% power). The red dashed line on the layout PNG traces it.

## Challenge
Pace and line over a blind drop; felt chevrons warn it is one-way. A clear ice parapet across the lip keeps players (not balls) back.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none

### vr_comfort (exact hole-local studs)

```json
{
  "player_guards": [
    {
      "id": "lip_parapet",
      "center": [
        0,
        1.75,
        -19.8
      ],
      "size": [
        8.0,
        3.5,
        0.3
      ],
      "yaw": 0,
      "note": "clear ice parapet (PlayerGuard: the ball passes) across the open lip so nobody steps off the 4-stud drop"
    }
  ],
  "tier_steps": {
    "id": "falls_steps",
    "where": "outside the west rail, x -6..-9.5 from z -12 to -20 then onto the basin apron",
    "rise": 4.0,
    "steps": 5,
    "tread": 1.5,
    "railing": "3.5-high railing on the open side + parapet along the upper pad edge"
  },
  "note": "player-only; the ball sees felt, rails and the drop"
}
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [3.5, 3.5, -31.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +4.21 studs).

## Playtest stats (p2; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 1.93 | 9.2% | 98% | 0.0% | 0 / 0 | [184, 1784, 30, 2, 0, 0, 0, 0] |
| average | 2.47 | 0.1% | 63% | 0.0% | 0 / 0 | [1, 1252, 611, 92, 39, 4, 1, 0] |

## Props for the 3D modeler (decoration only, sizes in studs)
Icicle curtain under the lip (P1); lip parapet, clear ice, PlayerGuard (P1); chevrons x2 (P1); player steps beside the drop (P1); snowpuff on an ice ledge (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [3.5, -4.0, -31.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `great_frozen_falls` at [13.5, -4.0, -30] (LANDMARK) size [26, 40, 8]: The Great Frozen Falls: a 26-wide frozen cascade pouring off the terrace edge east of the basin into the cloud sea (world.json waterfall); the hole's lip is a little frozen-fall of its own
- `lip_ice` at [0, -2.0, -20.0] size [7.0, 4, 1]: Frozen-fall lip: glassy icicle curtain down the 4-stud step under the lane's open end (visual skirt from felt to basin)
- `chevron_1` at [0.0, 0.0, -12.0] size [2.4, 0.01, 1.2]: Glowing felt chevron pointing -Z: one-way drop ahead (the ball won't come back up)
- `chevron_2` at [0.0, 0.0, -16.0] size [2.4, 0.01, 1.2]: Glowing felt chevron pointing -Z: one-way drop ahead (the ball won't come back up)
- `snowpuffs` at [-12.0, -4.0, -30] size [2.5, 2.2, 2.0]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) on an ice ledge beside the basin, one about to slide down the frozen falls; heads turn to follow the ball (visual only)

## Concept prompt
First-person VR view at eye height from a mini golf tee at night on the edge of a terrace: a short felt lane ends at an icicle-fringed lip with a clear ice parapet, dropping to a basin green below with a red flag; right beside it a huge frozen waterfall pours off the island edge into the glowing lilac clouds far below; aurora overhead. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
