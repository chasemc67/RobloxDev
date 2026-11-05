# Hole 14: Ore Bucket Swing (Par 3)

Zone: **Hoodoo Garden**. Gimmick: **Pendulum: an ore bucket swings from a cableway trestle across the lane, before a ramp up to the raised loading-dock green**.
Layout: `h14-layout.png`. Geometry: `holes.json` -> holes[13]. World placement (from `world/world.json`): origin [-300.0, 150.0, -200.0], yaw 180.0.
Tee [0, 0, 0], cup [1.0, 0.8, -44.0] (radius 0.5). Units: studs (1 stud = 0.3 m).

## Landmark
A timber **cableway trestle** swings a riveted ore bucket heaped with rock candy across the lane; a ramp climbs to a raised loading-dock green.

## Gimmick
Pendulum: an ore bucket swings from a cableway trestle across the lane, before a ramp up to the raised loading-dock green.

## Intended shots
Time the central line under the bucket, or choose the intentionally signposted SAFE BANK along the west rail outside the bucket; the right edge is another safe option. The legacy 256.5-degree ace bypass is intentional.

## Hole-in-one line
Brute-force search from the tee found ace lines (232 grid shots). The most robust: aim **256.5°** (atan2(dz,dx): direction (-0.23, -0.97) in x/z, i.e. 13.5° left of straight -Z), speed **19.4 studs/s** (98% power), start phase t=0.0s of the moving parts. The red dashed line on the layout PNG traces it.

## Challenge
Pendulum timing with a square collision foot; swing ±9 degrees, period 4s. Stops and deflections are measured below.

## Moving parts / teleports / hazards (exact specs, also in holes.json)
- **ore_bucket** (swing = pendulum): pivot (hinge) [0.0, 10.35, -24.0], axis [0, 0, 1], angle(t) = 9.0° x sin(360°·t/4.0 s + 0.0°), peak 14°/s. Blocker: box [2.1, 2.0, 1.8] centred [0, -9.0, 0] from the pivot hanging straight down; blocker 2: box [0.35, 0.2706, 0.15] centred [-0.875, -10.0103, 0]; blocker 3: box [0.35, 0.3008, 0.15] centred [-0.525, -10.0254, 0]; blocker 4: box [0.35, 0.3188, 0.15] centred [-0.175, -10.0344, 0]; blocker 5: box [0.35, 0.3188, 0.15] centred [0.175, -10.0344, 0]; blocker 6: box [0.35, 0.3008, 0.15] centred [0.525, -10.0254, 0]; blocker 7: box [0.35, 0.2706, 0.15] centred [0.875, -10.0103, 0]. Visual: Ore bucket (2.1x2x1.8) on a 9-stud hanger from the cableway trestle, swinging east-west across the lane; blockers 2..7 = invisible collider foot 2.1 wide x 0.15 deep in 6 yaw-0 strips (north/south faces square to the shot line) under the bucket, chamfered so the underside is a polygonal arc of radius 10.200 about the hinge: lowest corner 0.15 above the felt at every angle of the +-9 deg swing (centre strips 0.1562 at rest; bucket bottom 0.35); the bucket mesh gets a matching base skid plate

## Timing check (`tools/timing_check.py`, 96, 120 phases; actual fuzz counts per line)
- ore_bucket [intended] straight tee shot at the flag under the swinging ore bucket: blocked 0/96 (0 stops + 0 kicks), deflected 0, **Studio estimate 0%** (stops + 0.36 kicks), passed 100%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- ore_bucket [ace] brute-force ace line: blocked 0/96 (0 stops + 0 kicks), deflected 0, **Studio estimate 0%** (stops + 0.36 kicks), passed 100%, traps 0
- ore_bucket [intended] straight tee shot at the flag under the swinging ore bucket: blocked 0/120 (0 stops + 0 kicks), deflected 0, **Studio estimate 0%** (stops + 0.36 kicks), passed 100%, traps 0, fuzz 100000 shots: timeouts 0, pinned rests 0, escapes 0, excluded rests 0
- ore_bucket [ace] brute-force ace line: blocked 0/120 (0 stops + 0 kicks), deflected 0, **Studio estimate 0%** (stops + 0.36 kicks), passed 100%, traps 0

### safe_route (exact hole-local studs)

```json
{
  "kind": "intentional bank bypass",
  "legacy_ace_aim_deg": 256.5,
  "note": "Bank off the west rail to pass west of the bucket; right edge is also safe. Central line is timed."
}
```

## Flag and sightline
Flag: 7.5-stud pole (0.15 diameter) in the cup, [2.0, 1.2, 0.05] #e03c31 banner at the top [1.0, 8.3, -44.0]; visual only, no collision. Tee eye (5.5 up) -> flag top: **visible** (min clearance +5.50 studs).

## Playtest stats (p9; actual plays: good=2000, average=2000)
| Skill | Avg strokes | HIO | Par or better | Capped (8) | Escapes / timeouts | Strokes 1..8 |
|---|---|---|---|---|---|---|
| good | 2.70 | 6.7% | 93% | 0.0% | 0 / 0 | [133, 502, 1232, 99, 32, 1, 1, 0] |
| average | 2.82 | 4.0% | 80% | 0.1% | 0 / 0 | [80, 855, 670, 242, 83, 43, 18, 9] |

## Props for the 3D modeler (decoration only, sizes in studs)
Bucket [2.1, 2.0, 1.8], matching skid-foot [0.35, 0.2706, 0.15], pivot [0.0, 10.35, -24.0]; trestle, SAFE BANK sign and route arrows. See exact blocker offsets below.

Decoration anchors (position in hole-local studs):
- `cup_flag` at [1.0, 0.8, -44.0] size [2.0, 7.5, 0.15]: Flag: 7.5-stud pole (0.15 dia) in the cup, 2.0x1.2 banner at the top, turns to face the tee; no collision
- `cableway_trestle` at [0, 0, -24.0] (LANDMARK) size [10, 11.35, 1.5]: Timber cableway trestle (legs outside the rails at x +-5, beam at y 10.35) with the ore-bucket hanger; the main ore cableway continues overhead to the Hoodoo Garden
- `ore_bucket` at [0.0, 1.3499999999999996, -24.0] size [2.1, 2.0, 1.8]: Riveted ore bucket heaped with rock candy (moving mesh, pivot at the hinge [0.0, 10.35, -24.0]); base skid plate matches the collider foot
- `safe_bank_sign` at [-5.0, 0, -9] size [1.8, 3.2, 0.25]: SAFE BANK: left rail, then outside the bucket. CENTRE: wait for swing.
- `safe_bank_arrow` at [-2, 0, -7] size [1.4, 0.01, 2.0]: Arrow southwest toward west rail: SAFE BANK
- `timing_arrow` at [0, 0, -16] size [1.4, 0.01, 2.0]: CENTRE: wait until bucket swings clear
- `ore_piles` at [10, 0.8, -42] size [3, 1.5, 3]: Spilled rock-candy ore piles outside the green's east rail
- `loading_dock` at [0, 0, -33] size [8, 1, 6]: Timber ore-loading ramp (felt rises 0.8 over 6) up to the raised loading-dock green

## Concept prompt
First-person VR view at eye height on a high bench under an old timber cableway: an ore bucket full of pink rock candy swings slowly across a felt lane, beyond it a short ramp to a raised loading-dock green with a red flag; striped hoodoos and the Crown cliffs. Style: candy-striped sunset desert canyon, pink and cream banded sandstone, rock-candy crystals, lollipop saguaros, warm golden low sun from the west, lilac haze, chunky whimsical Roblox-friendly shapes, no text.

## Round p9 (exact)
- Foot collider chamfered: 6 yaw-0 strips (north/south faces square to the shot line), 0.35 wide x 0.15 deep each; outer bottom corners on a circle of radius 10.2 about the hinge [0.0, 10.35, -24.0]; strip tops at bucket bottom + .125. Centres relative to the hinge (hanging): [-0.875, -10.0103, 0] size [0.35, 0.2706, 0.15]; [-0.525, -10.0254, 0] size [0.35, 0.3008, 0.15]; [-0.175, -10.0344, 0] size [0.35, 0.3188, 0.15]; [0.175, -10.0344, 0] size [0.35, 0.3188, 0.15]; [0.525, -10.0254, 0] size [0.35, 0.3008, 0.15]; [0.875, -10.0103, 0] size [0.35, 0.2706, 0.15].
- Lowest foot corner over the full +-9 deg swing (8,000 samples): **0.15** (was 0.0215); centre strips 0.1562 at rest, outer strips 0.204 at rest. Bucket body unchanged (bottom .35).
- **Target conflict (not met):** the ball radius is 0.08 (0.16 tall). A collider whose lowest point is >= 0.15 above the felt can only overlap the top 0.01 of the ball, so in the simulator it no longer stops balls (block rate measured below). Clearance was treated as the hard requirement; the 35-50% stop target is NOT met. Clearance-vs-stop curve and one-knob fallback values: `_work/p9-report.md`.

| Phases | Line | Blocked (stops + kicks) | Deflected | Studio est. | Passed | Traps | Fuzz 100k: timeouts / escapes / pinned |
|---|---|---|---|---|---|---|---|
| 96 | intended | 0/96 (0 + 0) | 0 | **0%** | 100% | 0 | 0 / 0 / 0 (seed 11) |
| 96 | ace | 0/96 (0 + 0) | 0 | **0%** | 100% | 0 | - |
| 120 | intended | 0/120 (0 + 0) | 0 | **0%** | 100% | 0 | 0 / 0 / 0 (seed 29) |
| 120 | ace | 0/120 (0 + 0) | 0 | **0%** | 100% | 0 | - |

## Round p9b
Foot is 14 strips: centre (|x|≤0.9) at 0.06 clear (blocks); outer corners ≥0.1502 over ±9°. Intended Studio stop rate 43.1% @96 / 42.8% @120.
