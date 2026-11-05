# Hole 11: Floe Drift (Par 3)

Zone: **Driftfloe Shelf**. Gimmick: **Drifting ice floe: a flat floe slides across the neck, pauses, and drifts back (slide with dwell; pointed 45-degree ends); the side channel is the safe way round**.
Layout: `h11-layout.png`. Geometry: `holes.json` -> holes[10]. World placement (from `world/world.json`): origin [410.0, 146.0, 40.0], yaw 0.0.
Tee [0, 0, 0], cup [-4.0, 0.0, -45.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
Frozen **Floe Pond** with toy floes frozen in, a snowpuff **ice-fishing hut** puffing from its stove pipe; an ice floe with pointed ends drifts back and forth across the neck.

## Gimmick
Drifting ice floe: a flat floe slides across the neck, pauses, and drifts back (slide with dwell; pointed 45-degree ends); the side channel is the safe way round.

## Intended shots
**Timing line:** tee shot through the 6-wide neck while the floe is parked in its pocket, into the green: birdie chance.
**Safe line:** from the pond into the east side channel, up it to the crossover, then putt: a sure par.

## Hole-in-one line
Brute-force search from the tee found ace lines (190 grid shots). The most robust: aim **290.0°** (atan2(dz,dx): direction (0.34, -0.94) in x/z, i.e. 20.0° right of straight -Z), speed **17.2 studs/s** (87% power), start phase t=1.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Linear slide with dwell: 3 studs/s, pauses 1.2 s blocking and 2 s parked (cycle 7.87 s). Pointed 45° ends never bat a ball along the track.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **ice_floe** (slide): pivot [0, 0.0, -28.0], axis [1, 0, 0], speed 3.0 studs/s, ping-pong -7.0..0.0 studs with pauses 1.2 s at 0, 2 s at -7, phase 0.0, cycle 7.87 s. Blockers (relative to pivot at angle/offset 0): box [6.4, 1.0, 0.636] at [0, 0.5, 0]; box [0.4243, 1.0, 0.4243] at [-3.2, 0.5, 0] yaw 45.0; box [0.4243, 1.0, 0.4243] at [3.2, 0.5, 0] yaw 45.0. Visual: Ice floe slab 7 long, 0.6 thick, 1.0 tall with pointed 45-degree ends, gliding on a hidden track across the neck; blocking = centred on the neck (offset 0), parked = drifted 7 west into a pocket in the snowbank

## Timing check (`tools/timing_check.py`, 96 phases; actual fuzz counts per line)
- ice_floe [intended] tee shot through the neck past the drifting ice floe (neck waypoint): blocked 44/96 (44 stops + 0 kicks), deflected 0, **Studio estimate 45.8%** (stops + 0.36 kicks), passed 54.2%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- ice_floe [ace] brute-force ace line: blocked 42/96 (42 stops + 0 kicks), deflected 2, **Studio estimate 43.8%** (stops + 0.36 kicks), passed 54.2%, traps 0

### collision_cuts (exact hole-local studs)

```json
[
  {
    "mover": "ice_floe",
    "targets": [
      "rail5",
      "berg18"
    ],
    "min": [
      -10.68,
      -0.15,
      -28.47
    ],
    "max": [
      3.68,
      1.27,
      -27.53
    ],
    "clearance": 0.15
  }
]
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-4.0, 7.5, -45.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +4.22 studs).

## Playtest stats (walls; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.83 | 3.4% | 77% | 0.7% | 0 / 0 | [68, 1026, 454, 243, 115, 51, 19, 24] |
| average | 3.84 | 0.0% | 54% | 0.1% | 0 / 0 | [0, 635, 442, 112, 357, 340, 92, 22] |

## Props for the 3D modeler (decoration only, sizes in studs)
Ice floe slab with pointed ends, a snowpuff riding it (moving mesh, pivot = floe centre at offset 0) (P1); marker posts (P2); ice-fishing hut (P1, landmark); side-channel sign + felt arrow (P1); flag 7.5 (P1).

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-4.0, 0.0, -45.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `ice_floe` at [0, 0, -28] size [7.0, 1.2, 0.6]: Moving mesh: a chunky ice floe (glacier cyan, snow on top, a little snowpuff riding it) with pointed ends, pivot = floe centre at offset 0; must cover the collider exactly
- `fishing_hut` at [-9, 0, -30] (LANDMARK) size [3, 6, 3]: Snowpuff ice-fishing hut (striped canvas, stove-pipe chimney puffing) on the berg between pond and green: the landmark
- `floe_frame` at [0, 0, -28] size [24.6, 3, 1]: Two frosted timber marker posts at x -12 and x 4 where the floe track meets the snowbanks (no crossbeam)
- `sign_channel` at [11.6, 0, -21] size [1.8, 3.2, 0.25]: Painted arrow 'Side channel - the long way round' pointing into the channel
- `felt_arrow_channel` at [9.5, 0.0, -23.5] size [1.4, 0.01, 2.0]: Glowing felt arrow decal pointing -Z into the side channel
- `floe_pond` at [0, -0.2, -22] size [30, 0.2, 20]: Floe Pond ice (terrain Ice at y 145.6) round the hole with toy floes frozen in

## Concept prompt
First-person VR view at eye height from a mini golf tee at night on a frozen pond shelf: a felt lane widens into a basin, then narrows to a neck where a chunky ice floe with a snowpuff riding on it drifts sideways across the way; a striped ice-fishing hut puffs smoke on the bank; a side channel curves off to the right; a red flag beyond. Style: stylised 3D storybook render matching the Aurora Archipelago menu card: floating snow-capped slate-violet rock islands over a soft lilac cloud sea at night, thick rounded moonlit snow, translucent glowing glacier-cyan ice and crystal clusters, warm brass lanterns on chunky snow-capped timber posts, snowy blue-green pines, bright green felt with a white ball and a red flag, green and violet aurora ribbons across a starry indigo sky, the Starfrost Spire glowing on the skyline, soft bloom, cosy and whimsical, chunky Roblox-friendly shapes, no text, no UI.
