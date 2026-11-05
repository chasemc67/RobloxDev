# Hole 2: Mine-Cart Junction (Par 3)

Zone: **Sugarloaf Junction**. Gimmick: **Tunnel choice: open-top 3-wide shortcut (left), gentle dead end (middle), shorter forgiving long haul (right)**.
Layout: `h02-layout.png`. Geometry: `holes.json` -> holes[1]. World placement (from `world/world.json`): origin [100.0, 18.0, 410.0], yaw 0.0.
Tee [0, 0, 0], cup [-11.0, 0.0, -46.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
Candy-striped mine headframe and three portals: open-top left shortcut 3 studs wide, gentle middle dead end, and right route 26 studs long.

## Gimmick
Tunnel choice: open-top 3-wide shortcut (left), gentle dead end (middle), shorter forgiving long haul (right).

## Intended shots
Choose the open-top left shortcut for the short line, or the signed right route and crossover. The middle dead end gently returns the ball to the plaza.

## Hole-in-one line
Brute-force search from the tee found ace lines (27 grid shots). The most robust: aim **238.5°** (atan2(dz,dx): direction (-0.52, -0.85) in x/z, i.e. 31.5° left of straight -Z), speed **19.0 studs/s** (96% power). The red dashed line on the layout PNG traces it.

## Challenge
Route choice with clear sightlines. Middle floor rise 0.6; right-route lanterns keep at least 8 studs of head clearance.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none

### vr_clearance (exact hole-local studs)

```json
{
  "left_channel": {
    "open_top": true,
    "clear_width": 3.0,
    "x_range": [
      -11.0,
      -8.0
    ],
    "z_range": [
      -34,
      -16
    ]
  },
  "all_channel_roofs": "none except portal lintels",
  "portal_lintel_bottom_y": 8.0,
  "right_lantern_bottom_y": 8.0
}
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-11.0, 7.5, -46.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +1.20 studs).

## Playtest stats (p7; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.40 | 5.9% | 92% | 0.0% | 0 / 0 | [117, 1139, 584, 147, 13, 0, 0, 0] |
| average | 3.35 | 0.0% | 60% | 0.0% | 0 / 0 | [0, 279, 925, 647, 121, 23, 2, 3] |

## Props for the 3D modeler (decoration only, sizes in studs)
Open-top left channel with roof only at the portals; timber portals, mine headframe, elevated lanterns, route signs and felt arrows. Use exact anchors below.

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-11.0, 0.0, -46.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `headframe` at [1.0, 0, -22] (LANDMARK) size [8, 16, 6]: Candy-striped timber mine headframe (pulley wheel on top) above the middle tunnel; the three tunnel portals are timber-framed openings in a striped rock face along z -16 (left 3 wide, middle 4 wide with a 'DEAD END - NO GOLD' plank sign, right 4 wide). All overhead beams/roof undersides y>=8; headframe legs stay outside the clear middle channel
- `rock_face` at [0, 0, -17] size [26, 5, 2]: Striped rock face flanking the three open-top channels; no roof except portal lintels with underside y=8. Solid side piers stay outside the clear channel widths; fade dressing between camera and ball
- `sign_left` at [-12.6, 0, -12] size [1.8, 3.2, 0.25]: Arrow sign 'Short Cut - tight!' pointing into the LEFT tunnel
- `sign_mid` at [-1.2, 8, -15.4] size [3.0, 1.0, 0.2]: Plank sign 'DEAD END - NO GOLD' above the middle portal; sign bottom y=8
- `sign_right` at [12.6, 0, -12] size [1.8, 3.2, 0.25]: Arrow sign 'Long Haul - safe; firm putt' pointing into the RIGHT tunnel
- `felt_arrow_left` at [-9.5, 0.0, -14.0] size [1.4, 0.01, 2.0]: Glowing sour-apple felt arrow decal (flush) pointing -Z into the left tunnel
- `felt_arrow_right` at [9.0, 0.0, -14.0] size [1.4, 0.01, 2.0]: Glowing sour-apple felt arrow decal (flush) pointing -Z into the right tunnel
- `ore_carts` at [-14.5, 0, -42] size [3, 2.5, 6]: Two parked ore carts heaped with rock candy on a short rail spur outside the green and concept pad west edge; visual only, no ball/player collision; fade if occluding camera
- `tunnel_lanterns` at [9, 8, -32] size [0.6, 0.8, 0.6]: Lanterns on overhead portal-style crossbars every 6 studs; anchor is lantern bottom y=8 (top y=8.8); channel stays open-top
- `left_open_cut` at [-9.5, 0, -25] size [3.0, 8, 18]: Open-top mine cut: no roof over z=-16..-34. Portal lintel only at z=-16; underside y=8; no camera obstruction down the channel

## Concept prompt
Eye-height VR view of a candy-striped mine with three timber portals, an open-top shortcut on the left, a gentle dead-end route and lanterns high above the right route; clear view of the ball. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
