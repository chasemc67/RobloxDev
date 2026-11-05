# Hole 6: Flash Flood (Par 3)

Zone: **Rock Candy Narrows**. Gimmick: **Timing gate: a sluice gate slides across the slot neck, pauses closed, then opens (slide with dwell); the overflow channel is the safe way round**.
Layout: `h06-layout.png`. Geometry: `holes.json` -> holes[5]. World placement (from `world/world.json`): origin [280.0, 26.0, 255.0], yaw 0.0.
Tee [0, 0, 0], cup [-4.0, 0.0, -45.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
An old timber **sluice gate** with peppermint bands and a hand-wheel winch slides across the slot neck; a little **flood-warning bell tower** stands on the rock beside it.

## Gimmick
Timing gate: a sluice gate slides across the slot neck, pauses closed, then opens (slide with dwell); the overflow channel is the safe way round.

## Intended shots
Time the signed central gate opening, or use the east overflow route. The exact gate dwell times and collision pockets are listed below.

## Hole-in-one line
Brute-force search from the tee found ace lines (214 grid shots). The most robust: aim **290.0°** (atan2(dz,dx): direction (0.34, -0.94) in x/z, i.e. 20.0° right of straight -Z), speed **19.0 studs/s** (96% power), start phase t=1.5s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
First timing obstacle, slow and readable. The gate's pointed ends never bat a ball along its track (Lantern Grove lesson).

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **sluice_gate** (slide): pivot [0, 0.0, -28.0], axis [1, 0, 0], speed 3.0 studs/s, ping-pong -7.0..0.0 studs with pauses 1.2 s at 0, 2 s at -7, phase 0.0, cycle 7.87 s. Blockers (relative to pivot at angle/offset 0): box [6.4, 1.0, 0.636] at [0, 0.5, 0]; box [0.4243, 1.0, 0.4243] at [-3.2, 0.5, 0] yaw 45.0; box [0.4243, 1.0, 0.4243] at [3.2, 0.5, 0] yaw 45.0. Visual: Timber sluice gate board 7 long, 0.6 thick, 1.0 tall (pointed 45-degree ends) on a hidden rail across the neck; closed = centred on the neck (offset 0), open = slid 7 west into a pocket in the slot wall

## Timing check (`tools/timing_check.py`, 96 phases; actual fuzz counts per line)
- sluice_gate [intended] tee shot through the neck under the sluice gate (neck waypoint): blocked 44/96 (44 stops + 0 kicks), deflected 0, **Studio estimate 45.8%** (stops + 0.36 kicks), passed 54.2%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- sluice_gate [ace] brute-force ace line: blocked 42/96 (42 stops + 0 kicks), deflected 2, **Studio estimate 43.8%** (stops + 0.36 kicks), passed 54.2%, traps 0

### collision_cuts (exact hole-local studs)

```json
[
  {
    "mover": "sluice_gate",
    "targets": [
      "rail5",
      "rock18"
    ],
    "min": [
      -10.68,
      -0.15,
      -28.47
    ],
    "max": [
      3.68,
      1.17,
      -27.53
    ],
    "clearance": 0.15
  }
]
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [-4.0, 7.5, -45.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +4.22 studs).

## Playtest stats (p7; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.86 | 5.5% | 76% | 0.4% | 0 / 0 | [111, 960, 449, 257, 109, 60, 25, 29] |
| average | 3.85 | 0.1% | 55% | 0.2% | 0 / 0 | [1, 658, 439, 69, 358, 344, 107, 24] |

## Props for the 3D modeler (decoration only, sizes in studs)
Sliding gate main body [6.4, 1.0, 0.636] plus its exact end-cap blockers listed below; authored rail/rock pocket, frame, bell tower, overflow sign and arrows. Keep all listed cut clearances.

Decoration anchors (position in hole-local studs):
- `cup_flag` at [-4.0, 0.0, -45.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `sluice_gate` at [0, 0, -28] size [7.0, 1.2, 0.6]: Timber sluice gate with peppermint-striped bands and a big hand-wheel winch on the west wall (moving mesh, pivot = gate centre at offset 0)
- `bell_tower` at [-9, 0, -30] (LANDMARK) size [3, 9, 3]: Little timber flood-warning bell tower on the rock between basin and green (rings when the gate closes)
- `gate_frame` at [0, 0, -28] size [24.6, 9, 1]: Timber frame: west post x=-12, east post x=4 (approved 3.86 moved another .14 for clearance), beam 8 above felt; mesh pivot stays [0,0,-28]
- `sign_overflow` at [11.6, 0, -21] size [1.8, 3.2, 0.25]: Painted arrow 'Overflow - the long way round' pointing into the overflow channel
- `felt_arrow_overflow` at [9.5, 0.0, -23.5] size [1.4, 0.01, 2.0]: Glowing felt arrow decal pointing -Z into the overflow channel
- `flood_marks` at [-11.5, 0, -22] size [0.3, 4, 3]: High-water marks and a 'Flash Flood Zone' enamel sign on the basin wall

## Concept prompt
First-person VR view at eye height in a slot canyon: a felt lane widens into a basin, then narrows to a neck crossed by a sliding timber sluice gate with red-and-white stripes and a big winch wheel; a tiny bell tower on the rock; an overflow channel curving off to the right. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.
