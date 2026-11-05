# Hole 2: Snowpuff Burrows (Par 3)

Zone: **Lanternfall Landing**. Gimmick: **Tunnel choice: three snow burrows - short and tight (left), a dead end that rolls the ball back (middle), long and safe (right)**.
Layout: `h02-layout.png`. Geometry: `holes.json` -> holes[1]. World placement (from `world/world.json`): origin [-115.0, 60.0, 480.0], yaw -90.0.
Tee [0, 0, 0], cup [-11.0, 0.0, -46.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
The **Snowpuff Rookery**: a long rounded snow drift with three round burrow mouths under frosted ice-arch lintels, snowpuffs peeking out of little side holes and sliding down its back.

## Gimmick
Tunnel choice: three snow burrows - short and tight (left), a dead end that rolls the ball back (middle), long and safe (right).

## Intended shots
**Birdie line (left burrow):** a firm tee shot angled into the 3-wide open-top left burrow; it runs 18 studs and pops out on the green near the cup.
**Safe line (right burrow):** into the right burrow, up its length to the crossover, then a long putt across the green.
The middle burrow is a dead end whose floor rises 0.6: it always rolls the ball back into the plaza.

## Hole-in-one line
Brute-force search from the tee found ace lines (27 grid shots). The most robust: aim **238.5°** (atan2(dz,dx): direction (-0.52, -0.85) in x/z, i.e. 31.5° left of straight -Z), speed **19.0 studs/s** (96% power). The red dashed line on the layout PNG traces it.

## Challenge
Route choice. The left burrow is tight and only fair from a good angle, the right one is reliable but costs a stroke, and the dead end punishes anyone who just aims straight. Signs and felt arrows mark each mouth; a brass lantern hangs 9 studs over the cup as the cue when the drift hides the flag.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- none

### vr_clearance (exact hole-local studs)

```json
{
  "burrows": "open-top snow cuts; only ice-arch lintels at the mouths",
  "lintel_bottom_y": 8.0,
  "lantern_bottom_y": 8.0
}
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-11.0, 7.5, -46.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +1.20 studs).

## Playtest stats (p2; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.40 | 5.9% | 92% | 0.0% | 0 / 0 | [117, 1139, 584, 147, 13, 0, 0, 0] |
| average | 3.35 | 0.0% | 60% | 0.0% | 0 / 0 | [0, 279, 925, 647, 121, 23, 2, 3] |

## Props for the 3D modeler (decoration only, sizes in studs)
Rookery drift with three burrow mouths, open-topped cuts (P1, landmark); frosted ice-arch lintels x3, underside y 8 (P1); route signs x2 + felt arrows x2 + roll-back chevrons (P1); lantern cue over the cup (P1); burrow lanterns (P2); snowpuffs (P2); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-11.0, 0.0, -46.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `rookery_drift` at [0.0, 0, -22] (LANDMARK) size [24, 5, 26]: The Snowpuff Rookery: a long rounded snow drift (2.4-high colliders are the burrow walls) along z -16..-42 with three round burrow mouths at z -16 (left 3 wide 'Short & tight', middle 4 wide 'Dead end - it rolls back!', right 4 wide 'Long way round'). The burrows are OPEN-TOPPED snow cuts; only a frosted ice-arch lintel spans each mouth (underside y 8). Drift dressing stays below y 5 so the flag shows over it
- `snowpuffs` at [0.0, 2.4, -20] size [14, 2, 6]: Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, knitted scarves) peeking out of little side holes along the drift top and sliding down its back on their bellies; heads turn to follow the ball (visual only)
- `lintel_left` at [-9.5, 8.0, -16.0] size [5, 1.2, 1.2]: Frosted ice-arch lintel over the 'Short & tight' burrow mouth with a painted plank sign; underside exactly y 8 (VR head clearance), legs outside the clear burrow width
- `lintel_mid` at [0.0, 8.0, -16.0] size [5, 1.2, 1.2]: Frosted ice-arch lintel over the 'Dead end - it rolls back!' burrow mouth with a painted plank sign; underside exactly y 8 (VR head clearance), legs outside the clear burrow width
- `lintel_right` at [9.0, 8.0, -16.0] size [5, 1.2, 1.2]: Frosted ice-arch lintel over the 'Long way round' burrow mouth with a painted plank sign; underside exactly y 8 (VR head clearance), legs outside the clear burrow width
- `sign_left` at [-12.6, 0, -12] size [1.8, 3.2, 0.25]: Arrow sign 'Short & tight!' pointing into the LEFT burrow
- `sign_right` at [12.6, 0, -12] size [1.8, 3.2, 0.25]: Arrow sign 'Long way round - firm putt' pointing into the RIGHT burrow
- `felt_arrow_left` at [-9.5, 0.0, -14.0] size [1.4, 0.01, 2.0]: Glowing mint felt arrow decal (flush) pointing -Z into the left burrow
- `felt_arrow_right` at [9.0, 0.0, -14.0] size [1.4, 0.01, 2.0]: Glowing mint felt arrow decal (flush) pointing -Z into the right burrow
- `felt_rollback_mid` at [0.0, 0.3, -22.0] size [1.4, 0.01, 2.0]: Faint felt chevrons in the middle burrow pointing back +Z (its floor rises 0.6: the ball rolls back)
- `lantern_cue` at [-11.0, 9.0, -46.0] size [0.9, 1.2, 0.9]: Brass lantern (PointLight #FFB861, range 14, brightness 0.8) hanging 9 studs over the cup from a rope between two frosted pines: the visual cue when the drift hides the flag (no collision, 9 above the felt)
- `burrow_lanterns` at [9, 8, -32] size [0.6, 0.8, 0.6]: Small brass lanterns on ice-arch crossbars every 6 studs over the right burrow; lantern bottom y 8; open top

## Concept prompt
First-person VR view at eye height from a mini golf tee at a snowpuff rookery at night: the felt lane opens into a small plaza facing a long rounded snow drift with three round burrow mouths under glowing ice arches, a narrow one on the left, a middle one with a 'dead end' plank, a wide one on the right; dozens of round penguin-puffin snowpuffs in knitted scarves peek out of the drift; a brass lantern glows over the hidden green beyond. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
