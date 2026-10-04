# VR Mini Golf playtest summary

- Run: 2026-10-03 22:57
- Scenarios: rollout, bank, walls, windmill, hill, cup, ledge, ghost
- Cameras: fixed,topdown,follow
- SimulateVR: True

## Rollout (flat felt test lane)

| Speed | Distance | Time to stop | Time to rest | Ideal distance / time (rolling model) |
|---|---|---|---|---|
| 2 m/s | 4.61 m | 5.80 s | 6.36 s | 4.48 m / 5.87 s |
| 4 m/s | 11.34 m | 8.05 s | 8.62 s | 11.11 m / 8.15 s |
| 6 m/s | 18.47 m | 9.43 s | 9.98 s | 18.25 m / 9.59 s |

## 45° bank wall (Hole 2 Dogleg)

| Shot | Part | Speed in | Speed out | Angle in | Angle out | Normal restitution | Tangential retention | Speed kept | Kept after 0.3 s |
|---|---|---|---|---|---|---|---|---|---|
| bank-4mps | ? | 2.34 m/s | 1.79 m/s | 42.2° | 61.4° | 0.49 | 1 | 0.77 | 0.66 |
| bank-6mps | Hole2/Wall | 4.44 m/s | 3.46 m/s | 45° | 57.4° | 0.59 | 0.93 | 0.78 | 0.70 |

## Walls and bumper posts

| Shot | Part | Speed in | Speed out | Angle in | Angle out | Normal restitution | Tangential retention | Speed kept | Kept after 0.3 s |
|---|---|---|---|---|---|---|---|---|---|
| wall-straight-3mps | ? | 2.19 m/s | 1.34 m/s | 0° | 0° | 0.61 | - | 0.61 | 0.54 |
| wall-straight-6mps | Hole1/Wall | 5.31 m/s | 3.22 m/s | 0° | 0° | 0.61 | - | 0.61 | 0.44 |
| wall-45deg-5mps | Hole1/Wall | 4.63 m/s | 3.60 m/s | 45° | 57.4° | 0.59 | 0.93 | 0.78 | 0.70 |
| post-straight-6mps | Hole2/Bumper | 5.68 m/s | 3.56 m/s | 0° | 0° | 0.63 | - | 0.63 | 0.39 |
| post-45deg-5mps | Hole2/Bumper | 4.69 m/s | 3.74 m/s | 44.7° | 60.3° | 0.56 | 0.98 | 0.80 | 0.47 |

## Windmill (Hole 4)

| Shot | Outcome | Contacts | Distance | Speed at cup |
|---|---|---|---|---|
| mill-phase0 | rest | none | 11.04 m | - |
| mill-phase45 | rest | Hole4/Blade (2.22 m/s in) | 4.11 m | - |

## The Hill (Hole 3)

| Shot | Outcome | Reached green | Ended on green | Rolled back | Max height | Final position |
|---|---|---|---|---|---|---|
| hill-strong-5mps | rest | yes | yes | no | 2.31 | [78.3182, 2.2787, 28.1196] |
| hill-weak-2mps | rest | no | no | yes | 1.40 | [76.0681, 1.0787, 1.1892] |

## Cup drop (Hole 1, from 60 cm)

| Putt speed | Speed at rim | Outcome | Holed on first pass |
|---|---|---|---|
| 1.3 m/s | 0.82 m/s | cup | yes |
| 1.6 m/s | 1.13 m/s | cup | yes |
| 2 m/s | 1.45 m/s | rest | no |
| 2.5 m/s | 2.31 m/s | rest | no |
| 3 m/s | 2.25 m/s | rest | no |
| 4 m/s | 3.83 m/s | cup | no |

## Ledge plane snap (SimulateVR)

Heights are relative to the plane the ball rests on (studs; 1 stud = 30 cm).

| Case | Ball plane Y | VR rig floor Δ | Character feet Δ | Putter head bottom Δ | Wall group (player collides) | Pass |
|---|---|---|---|---|---|---|
| h1-ball-at-wall | 0.999 | 0.001 | 0.001 | 0.011 | GolfWall (no) | yes |
| h1-stance-on-wall | 0.999 | 0.001 | 0.001 | 0.011 | GolfWall (no) | yes |
| h3-green-edge | 2.199 | 0.001 | 0.001 | 0.011 | GolfWall (no) | yes |

## Club ghosting (SimulateVR)

| Sweep | Max follow error | Max lift | Ball moved | Hits | Club parts non-colliding | Pass |
|---|---|---|---|---|---|---|
| through-wall | 0 | 0.001 | 0 | 0 | yes | yes |
| through-post | 0 | 0.001 | 0 | 0 | yes | yes |

VR swing through the ball (putter face 1.2 m/s): hit=yes source=vr ball speed 6.81 studs/s (expected 6.80), outcome rest, 4.54 m. Pass: yes

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

## Clips

- `playtests/2026-10-03/after/rollout-fixed.mov`
- `playtests/2026-10-03/after/rollout-topdown.mov`
- `playtests/2026-10-03/after/rollout-follow.mov`
- `playtests/2026-10-03/after/bank-fixed.mov`
- `playtests/2026-10-03/after/bank-topdown.mov`
- `playtests/2026-10-03/after/bank-follow.mov`
- `playtests/2026-10-03/after/walls-fixed.mov`
- `playtests/2026-10-03/after/walls-topdown.mov`
- `playtests/2026-10-03/after/walls-follow.mov`
- `playtests/2026-10-03/after/windmill-fixed.mov`
- `playtests/2026-10-03/after/windmill-topdown.mov`
- `playtests/2026-10-03/after/windmill-follow.mov`
- `playtests/2026-10-03/after/hill-fixed.mov`
- `playtests/2026-10-03/after/hill-topdown.mov`
- `playtests/2026-10-03/after/hill-follow.mov`
- `playtests/2026-10-03/after/cup-fixed.mov`
- `playtests/2026-10-03/after/cup-topdown.mov`
- `playtests/2026-10-03/after/cup-follow.mov`
- `playtests/2026-10-03/after/ledge-fixed.mov`
- `playtests/2026-10-03/after/ledge-topdown.mov`
- `playtests/2026-10-03/after/ledge-follow.mov`
- `playtests/2026-10-03/after/ghost-fixed.mov`
- `playtests/2026-10-03/after/ghost-topdown.mov`
- `playtests/2026-10-03/after/ghost-follow.mov`

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
