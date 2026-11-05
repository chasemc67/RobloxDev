# Hole 7: Rope Bridge Run (Par 4)

Zone: **Taffy Mesa**. Gimmick: **Rope-bridge spans: two railed rope bridges over Taffy Gap with an island between whose ends are open to the gap; a fall respawns at the island**.
Layout: `h07-layout.png`. Geometry: `holes.json` -> holes[6]. World placement (from `world/world.json`): origin [340.0, 70.0, 150.0], yaw 0.0.
Tee [0, 0, 0], cup [3.0, 0.0, -60.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
Two rope-trim bridges with solid 3.5-stud parapets and opaque side skirts cross Taffy Gap via a hoodoo island. A shallow visual floor and mist hide the deep chasm.

## Gimmick
Rope-bridge spans: two railed rope bridges over Taffy Gap with an island between whose ends are open to the gap; a fall respawns at the island.

## Intended shots
**Normal play:** 1) across bridge 1 to the island; 2) from the island through bridge 2 onto the far green; 3-4) putt.
**Ace line:** a near-max-power putt threads both bridges in one straight line (the bridges are offset so only a 0.3°-wide line runs clean).

## Hole-in-one line
Brute-force search from the tee found ace lines (1 grid shots). The most robust: aim **272.5°** (atan2(dz,dx): direction (0.04, -1.00) in x/z, i.e. 2.5° right of straight -Z), speed **19.8 studs/s** (100% power). The red dashed line on the layout PNG traces it.

## Challenge
Long and committed. The island's ends are open to the gap: a ball that falls in **respawns at rest on the island marker stone** (+1).

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **hazard taffy_gap** (pit): +1 stroke, ball placed at rest on the respawn point [0.0, 0.0, -38.5]

### vr_comfort (exact hole-local studs)

```json
{
  "boxes": [
    {
      "id": "rope_rail6",
      "center": [
        -2.25,
        1.5,
        -31.5
      ],
      "size": [
        0.5,
        4.0,
        11.0
      ],
      "yaw": 180.0,
      "role": "solid_parapet",
      "solid": true,
      "collidable": true,
      "collision_source": "walls"
    },
    {
      "id": "rope_rail7",
      "center": [
        2.25,
        1.5,
        -31.5
      ],
      "size": [
        0.5,
        4.0,
        11.0
      ],
      "yaw": 0.0,
      "role": "solid_parapet",
      "solid": true,
      "collidable": true,
      "collision_source": "walls"
    },
    {
      "id": "rope_rail12",
      "center": [
        1.55,
        1.5,
        -51.5
      ],
      "size": [
        0.5,
        4.0,
        13.0
      ],
      "yaw": 180.0,
      "role": "solid_parapet",
      "solid": true,
      "collidable": true,
      "collision_source": "walls"
    },
    {
      "id": "rope_rail13",
      "center": [
        6.05,
        1.5,
        -51.5
      ],
      "size": [
        0.5,
        4.0,
        13.0
      ],
      "yaw": 0.0,
      "role": "solid_parapet",
      "solid": true,
      "collidable": true,
      "collision_source": "walls"
    },
    {
      "id": "bridge1_skirt_west",
      "center": [
        -2.25,
        -2.0,
        -31.5
      ],
      "size": [
        0.5,
        4.0,
        11.0
      ],
      "yaw": 0,
      "role": "solid_side_skirt",
      "solid": true,
      "collidable": false,
      "ball_collision": false
    },
    {
      "id": "bridge1_skirt_east",
      "center": [
        2.25,
        -2.0,
        -31.5
      ],
      "size": [
        0.5,
        4.0,
        11.0
      ],
      "yaw": 0,
      "role": "solid_side_skirt",
      "solid": true,
      "collidable": false,
      "ball_collision": false
    },
    {
      "id": "bridge2_skirt_west",
      "center": [
        1.55,
        -2.0,
        -51.5
      ],
      "size": [
        0.5,
        4.0,
        13.0
      ],
      "yaw": 0,
      "role": "solid_side_skirt",
      "solid": true,
      "collidable": false,
      "ball_collision": false
    },
    {
      "id": "bridge2_skirt_east",
      "center": [
        6.05,
        -2.0,
        -51.5
      ],
      "size": [
        0.5,
        4.0,
        13.0
      ],
      "yaw": 0,
      "role": "solid_side_skirt",
      "solid": true,
      "collidable": false,
      "ball_collision": false
    },
    {
      "id": "gap_comfort_floor",
      "center": [
        0,
        -4.25,
        -42
      ],
      "size": [
        30,
        0.5,
        32
      ],
      "yaw": 0,
      "role": "opaque_gap_floor",
      "solid": true,
      "collidable": false,
      "ball_collision": false,
      "note": "Visual top y=-4. Original taffy_gap ball hazard at -30 and island respawn are unchanged."
    }
  ],
  "note": "Opaque side skirts meet solid parapets at deck height. Player teleport points never transport the ball. The shallow visual floor/mist hide the deep chasm; ball hazard/respawn semantics remain unchanged.",
  "mist": {
    "id": "gap_mist",
    "center": [
      0,
      -3.5,
      -42
    ],
    "size": [
      30,
      1,
      32
    ],
    "yaw": 0,
    "collidable": false,
    "ball_collision": false
  }
}
```

### player_teleport_points (exact hole-local studs)

```json
[
  {
    "id": "bridge1_entry",
    "position": [
      0.0,
      0,
      -25
    ],
    "size": [
      3,
      0.02,
      2
    ],
    "yaw": 0,
    "support_felt": "lane",
    "player_only": true,
    "ball_teleport": false,
    "optional": true,
    "note": "Flush player teleport marker on solid felt, one stud back from the bridge-1 end; paired crossing is optional."
  },
  {
    "id": "bridge1_island",
    "position": [
      4.5,
      0,
      -38.5
    ],
    "size": [
      3,
      0.02,
      2
    ],
    "yaw": 0,
    "support_felt": "island",
    "player_only": true,
    "ball_teleport": false,
    "optional": true,
    "note": "Flush player teleport marker on solid felt, on island felt just east of the bridge-1 landing, clear of the respawn stone (p9: moved from [0,0,-38]); paired crossing is optional."
  },
  {
    "id": "bridge2_island",
    "position": [
      3.8,
      0,
      -44.0
    ],
    "size": [
      3,
      0.02,
      2
    ],
    "yaw": 0,
    "support_felt": "island",
    "player_only": true,
    "ball_teleport": false,
    "optional": true,
    "note": "Flush player teleport marker on solid felt, one stud back from the bridge-2 end; paired crossing is optional."
  },
  {
    "id": "bridge2_exit",
    "position": [
      5.15,
      0,
      -59
    ],
    "size": [
      3,
      0.02,
      2
    ],
    "yaw": 0,
    "support_felt": "green",
    "player_only": true,
    "ball_teleport": false,
    "optional": true,
    "note": "Flush player teleport marker on solid felt, on green felt at the bridge-2 exit, east of the cup (west edge .15 outside the cup rim; p9: moved from x 3.8); paired crossing is optional."
  }
]
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [3.0, 7.5, -60.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (p9; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 3.57 | 1.6% | 90% | 0.0% | 0 / 0 | [32, 131, 780, 856, 126, 69, 5, 1] |
| average | 4.20 | 0.0% | 68% | 0.1% | 0 / 0 | [0, 65, 436, 867, 386, 180, 45, 21] |

## Props for the 3D modeler (decoration only, sizes in studs)
Solid parapets and skirts on both bridges, opaque gap floor/mist, four optional player teleport pads, island hoodoo and respawn marker. Exact boxes and pads are listed below.

Decoration anchors (position in hole-local studs):
- `cup_flag` at [3.0, 0.0, -60.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `rope_bridges` at [0, 0, -42] (LANDMARK) size [8, 4, 32]: Two flat-felt bridges with solid 3.5-stud sandstone parapets, rope trim, opaque side skirts and optional endpoint player teleports
- `island_hoodoo` at [-6.5, 0, -41] size [3, 12, 3]: Striped hoodoo with a gumdrop cap on the island's west end (outside the play line; decoration only)
- `island_respawn_stone` at [0, 0, -38.5] size [0.8, 0.02, 0.8]: Glowing marker stone flush in the island felt at the bridge-1 landing: where a ball that falls into the gap reappears
- `gap_view` at [0, -4.25, -42] size [30, 0.5, 32]: Opaque sandstone comfort floor and mist hide the 30-stud gap; the original pit respawn remains authoritative for balls
- `island_edge_lip` at [0, 0, -37.0] size [18, 0.2, 0.4]: Low crumbly sandstone lip (0.2, visual only) along the open island edges so they read as edges
- `bridge1_skirt_west` at [-2.25, -2.0, -31.5] size [0.5, 4.0, 11.0]: Opaque sandstone side skirt, exactly outside bridge felt, extends down to comfort floor
- `bridge1_skirt_east` at [2.25, -2.0, -31.5] size [0.5, 4.0, 11.0]: Opaque sandstone side skirt, exactly outside bridge felt, extends down to comfort floor
- `bridge2_skirt_west` at [1.55, -2.0, -51.5] size [0.5, 4.0, 13.0]: Opaque sandstone side skirt, exactly outside bridge felt, extends down to comfort floor
- `bridge2_skirt_east` at [6.05, -2.0, -51.5] size [0.5, 4.0, 13.0]: Opaque sandstone side skirt, exactly outside bridge felt, extends down to comfort floor
- `player_tp_bridge1_entry` at [0.0, 0, -25] size [3, 0.02, 2]: Flush player teleport marker on solid felt, one stud back from the bridge-1 end; paired crossing is optional.
- `player_tp_bridge1_island` at [4.5, 0, -38.5] size [3, 0.02, 2]: Flush player teleport marker on solid felt, on island felt just east of the bridge-1 landing, clear of the respawn stone (p9: moved from [0,0,-38]); paired crossing is optional.
- `player_tp_bridge2_island` at [3.8, 0, -44.0] size [3, 0.02, 2]: Flush player teleport marker on solid felt, one stud back from the bridge-2 end; paired crossing is optional.
- `player_tp_bridge2_exit` at [5.15, 0, -59] size [3, 0.02, 2]: Flush player teleport marker on solid felt, on green felt at the bridge-2 exit, east of the cup (west edge .15 outside the cup rim; p9: moved from x 3.8); paired crossing is optional.

## Concept prompt
Eye-height VR view of candy-striped canyon bridges with tall solid parapets and opaque skirts, a hoodoo island, clear teleport pads and soft mist over a shallow visible floor; felt paths and a red flag ahead. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.

## Round p9 (exact)
- `bridge2_exit` moved east: **[5.15, 0, -59]** (was [3.8, 0, -59]); size [3, 0.02, 2], x 3.65..6.65, z -58..-60 on green felt (green x -6..10); west edge .15 outside the cup rim (cup [3,0,-60] r .5).
- `bridge1_island` moved (it overlapped the respawn stone): **[4.5, 0, -38.5]** (was [0, 0, -38]); x 3..6, z -37.5..-39.5 on island felt, 2.6 studs edge-to-edge (4.5 centre-to-centre) from the respawn stone, 0.5 back from the island south rail/edge lip.
- `island_respawn_stone` unchanged at [0, 0, -38.5]. `bridge2_island` [3.8, 0, -44] and `bridge1_entry` [0, 0, -25] unchanged. All pads flush, player-only, ball_teleport=False, optional; `player_tp_*` anchors match.
