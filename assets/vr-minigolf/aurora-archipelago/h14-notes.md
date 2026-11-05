# Hole 14: Bell Buoy (Par 3)

Zone: **Icefall Terraces**. Gimmick: **Pendulum: a brass icicle bell swings across the lane from a timber gantry, before a ramp up to a raised green**.
Layout: `h14-layout.png`. Geometry: `holes.json` -> holes[13]. World placement (from `world/world.json`): origin [85.0, 182.0, -300.0], yaw 90.0.
Tee [0, 0, 0], cup [1.0, 0.8, -44.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A timber **bell gantry** hung with icicles swings a brass **icicle bell** across the lane; a short ramp climbs to a raised green.

## Gimmick
Pendulum: a brass icicle bell swings across the lane from a timber gantry, before a ramp up to a raised green.

## Intended shots
**Timing line:** straight at the flag under the bell when it swings clear.
**Safe side:** hug a rail past the bell's touch band, then up the ramp.

## Hole-in-one line
Brute-force search from the tee found ace lines (208 grid shots). The most robust: aim **256.5°** (atan2(dz,dx): direction (-0.23, -0.97) in x/z, i.e. 13.5° left of straight -Z), speed **19.4 studs/s** (98% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Pendulum ±9° over 4 s (peak 14 °/s); the bell is turned 30° to the swing plane and a square collider foot under its lip makes clean stops.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **icicle_bell** (swing = pendulum): pivot (hinge) [0.0, 10.35, -24.0], axis [0, 0, 1], angle(t) = 9.0° x sin(360°·t/4.0 s + 0.0°), peak 14°/s. Blocker: box [2.0, 2.0, 2.0] centred [0, -9.0, 0] from the pivot hanging straight down; blocker 2: box [0.2333, 0.3463, 0.15] centred [-0.9333, -10.0621, 0]; blocker 3: box [0.2333, 0.3675, 0.15] centred [-0.7, -10.0728, 0]; blocker 4: box [0.2333, 0.3835, 0.15] centred [-0.4667, -10.0807, 0]; blocker 5: box [0.2333, 0.394, 0.15] centred [-0.2333, -10.086, 0]; blocker 6: box [0.2333, 0.3993, 0.15] centred [0.0, -10.0887, 0]; blocker 7: box [0.2333, 0.394, 0.15] centred [0.2333, -10.086, 0]; blocker 8: box [0.2333, 0.3835, 0.15] centred [0.4667, -10.0807, 0]; blocker 9: box [0.2333, 0.3675, 0.15] centred [0.7, -10.0728, 0]; blocker 10: box [0.2333, 0.3463, 0.15] centred [0.9333, -10.0621, 0]. Visual: Brass bell (2x2x2 collider, turned 30 deg to the swing plane so no face is square to it) hung with icicles on a 9-stud hanger from the timber gantry, swinging east-west across the lane; blocker 2 = invisible collider foot 2.1x0.4x0.15 (yaw 0, its north/south faces square to the shot line) under the bell lip, bottom 0.061 above the felt at rest (bell bottom 0.35), built from 9 strips whose bottom corners sit on an arc about the hinge (radius 10.289), so no corner ever comes closer than 0.061 to the felt; blockers 2..10; the bell mesh gets a matching brass clapper-skid plate over the foot (its underside follows the arc)

### safe_route (exact hole-local studs)

```json
{
  "kind": "intentional side line",
  "note": "Play down the east side of the lane outside the bell's touch band, or bank off the west rail; the central line is timed."
}
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [1.0, 8.3, -44.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (after-late; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.68 | 6.7% | 94% | 0.0% | 0 / 0 | [133, 507, 1249, 84, 25, 1, 1, 0] |
| average | 3.56 | 0.0% | 62% | 0.2% | 0 / 0 | [0, 237, 1013, 389, 202, 87, 56, 16] |

## Props for the 3D modeler (decoration only, sizes in studs)
Bell gantry with icicles on the beam only (P1, landmark); brass icicle bell with skid plate over the collider foot, pivot at the hinge (P1); safe-side sign + timing arrow (P1); buoys (P3); hand-bell snowpuffs (P3); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [1.0, 0.8, -44.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `bell_gantry` at [0, 0, -24.0] (LANDMARK) size [10, 11.35, 1.5]: Timber bell gantry hung with icicles (legs outside the rails at x +-5, beam at y 10.35); the icicles hang from the beam only, >= 8 above the felt
- `icicle_bell` at [0.0, 1.3499999999999996, -24.0] size [2.0, 2.0, 2.0]: Moving mesh: brass bell with an icicle fringe (pivot at the hinge [0.0, 10.35, -24.0]); base skid plate matches the collider foot; it rings softly at each end of its swing
- `safe_side_sign` at [-5.0, 0, -9] size [1.8, 3.2, 0.25]: SAFE SIDE: hug a rail past the bell. CENTRE: wait for the swing.
- `timing_arrow` at [0, 0, -16] size [1.4, 0.01, 2.0]: CENTRE: wait until the bell swings clear
- `buoy_float` at [9, 0.8, -42] size [3, 2, 3]: Striped harbour buoys and a coil of frosted rope outside the green's east rail
- `snowpuffs` at [-10, 0.8, -42] size [2.5, 2.2, 2.0]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) ringing hand-bells in time with the big bell, on a snow bank beside the green; heads turn to follow the ball (visual only)

## Concept prompt
First-person VR view at eye height from a mini golf tee at night on an icy terrace: a timber gantry hung with icicles swings a big brass bell slowly across the felt lane; beyond it a short ramp climbs to a raised green with a red flag; snowpuffs ring little hand-bells; the Starfrost Spire glows to the south behind you, aurora ahead. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
