# Hole 3: Glimmer Crossing (Par 3)

Zone: **Lanternfall Landing**. Gimmick: **Rail-less glowing ice plank straight over the open-sky Glimmer Gap (risky) or the railed ice bridge to the right (safe); a ball in the gap respawns at the plank entry (+1)**.
Layout: `h03-layout.png`. Geometry: `holes.json` -> holes[2]. World placement (from `world/world.json`): origin [-40.0, 60.0, 470.0], yaw -45.0.
Tee [0, 0, 0], cup [-1.0, 0.0, -55.5] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
**Glimmer Islet** floats just east of the hole with its crystal cluster and the Glimmer Icefall pouring into the clouds. The hole crosses the open-sky **Glimmer Gap**: a rail-less glowing ice plank straight from the tee, or the railed ice bridge to the right with a railed walk-on deck beside it.

## Gimmick
Rail-less glowing ice plank straight over the open-sky Glimmer Gap (risky) or the railed ice bridge to the right (safe); a ball in the gap respawns at the plank entry (+1).

## Intended shots
**Risky line:** straight down the 2-wide rail-less plank, 26 studs over open sky, to the north island and the cup.
**Safe line:** to the ice-bridge mouth on the right, across the railed bridge, then two putts on the north green.

## Hole-in-one line
Brute-force search from the tee found ace lines (4 grid shots). The most robust: aim **269.0°** (atan2(dz,dx): direction (-0.02, -1.00) in x/z, i.e. 1.0° left of straight -Z), speed **19.0 studs/s** (96% power). The red dashed line on the layout PNG traces it.

## Challenge
Nerve and line. A ball that falls off the plank costs a stroke and **reappears at rest on the glowing marker stone at the plank entry** (not back at the tee). The ice bridge is a sure par. Player-only guards line both rims and the plank, so nobody walks into the gap.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **hazard glimmer_gap** (pit): +1 stroke, ball placed at rest on the respawn point [0.0, 0.0, -22.5]

### vr_comfort (exact hole-local studs)

```json
{
  "player_guards": [
    {
      "id": "guard_south_rim",
      "center": [
        0,
        2.0,
        -23.75
      ],
      "size": [
        26,
        4,
        0.3
      ],
      "yaw": 0,
      "note": "south gap rim, x -13..13 except where the ball crosses (the guard is PlayerGuard: the ball passes)"
    },
    {
      "id": "guard_north_rim",
      "center": [
        0,
        2.0,
        -50.25
      ],
      "size": [
        26,
        4,
        0.3
      ],
      "yaw": 0,
      "note": "north gap rim"
    },
    {
      "id": "guard_plank_w",
      "center": [
        -1.15,
        2.0,
        -37.0
      ],
      "size": [
        0.3,
        4,
        26
      ],
      "yaw": 0,
      "note": "both sides of the rail-less plank"
    },
    {
      "id": "guard_plank_e",
      "center": [
        1.15,
        2.0,
        -37.0
      ],
      "size": [
        0.3,
        4,
        26
      ],
      "yaw": 0,
      "note": ""
    }
  ],
  "player_deck": {
    "id": "ice_walk_deck",
    "x": [
      8.5,
      12.5
    ],
    "z": [
      -24.0,
      -50.0
    ],
    "y": 0.0,
    "width": 4.0,
    "rails": "both, 3.5 high with solid lower board (its inner railing replaces the ball bridge's east rail visually; the 1-high ball rail collider stays)",
    "note": "railed walk-on ice deck beside the safe ball bridge so the player can follow the ball"
  },
  "note": "The ball sees only the felt, rails and the pit/respawn; every box here is player-only."
}
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-1.0, 7.5, -55.5]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (p2; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.72 | 7.0% | 68% | 0.0% | 0 / 0 | [141, 1029, 197, 562, 25, 41, 3, 2] |
| average | 3.54 | 0.0% | 53% | 0.0% | 0 / 0 | [0, 0, 1064, 809, 121, 1, 4, 1] |

## Props for the 3D modeler (decoration only, sizes in studs)
Rail-less glowing ice plank 2.4x0.8x26 (P1); railed ice bridge + 4-wide railed player deck (P1); respawn marker stone (P1); route signs x2 + felt arrows x2 (P1); clear PlayerGuard panels on both rims and plank sides (P1); snowpuff with binoculars (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-1.0, 0.0, -55.5] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `glimmer_islet` at [24, -20, -36] (LANDMARK) size [20, 30, 20]: Glimmer Islet: a small floating island 24 studs east of the gap, a glowing ice-crystal cluster on top and the Glimmer Icefall pouring off it into the clouds (world dressing; see world.json)
- `ice_plank` at [0, 0, -37.0] size [2.4, 0.8, 26]: Rail-less glowing ice plank, felt on top, 2 wide, 26 long straight over the gap; translucent glacier-cyan with a crystal-core neon strip down each edge
- `ice_bridge` at [6.0, 0, -37.0] size [5.0, 2, 26]: Railed ice bridge: glass deck under the felt, chunky snow-capped timber ball rails
- `plank_respawn_stone` at [0, 0, -22.5] size [0.8, 0.02, 0.8]: Glowing aurora-lime marker stone set flush in the felt at the plank entry: where a ball that falls into the gap reappears
- `sign_plank` at [-2.2, 0, -21.5] size [1.6, 2.6, 0.2]: Sign 'Ice plank - no rails!' with a falling-ball icon beside the plank entry
- `sign_bridge` at [8.6, 0, -19.0] size [1.8, 3.2, 0.25]: Lantern sign 'Ice bridge - the safe way' pointing to the railed bridge
- `route_arrow_plank` at [0, 0, -20.0] size [1.4, 0.01, 2.0]: RISKY PLANK: straight north toward the narrow crossing
- `route_arrow_bridge` at [6.0, 0, -20.0] size [1.4, 0.01, 2.0]: SAFE BRIDGE: north along the railed crossing
- `snowpuffs` at [-10.5, 0, -12] size [2.5, 2.2, 2.0]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) on a snow bank outside the shore's west rail, one with binoculars watching the plank; heads turn to follow the ball (visual only)

## Concept prompt
First-person VR view at eye height from a mini golf tee on a snowy island edge at night: a narrow rail-less glowing ice plank runs straight across an open-sky gap high above a lilac cloud sea to a green with a red flag; to the right a railed ice bridge with snow-capped timber rails and a walkway; a small floating islet with a glowing crystal cluster and a frozen waterfall hangs nearby. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
