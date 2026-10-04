# VR Mini Golf playtest summary

- Run: 2026-10-03 22:26
- Scenarios: rollout, bank, walls, windmill, hill, cup, ledge, ghost
- Cameras: default
- SimulateVR: True

## Rollout (flat felt test lane)

| Speed | Distance | Time to stop | Time to rest | Ideal v²/2a |
|---|---|---|---|---|
| 2 m/s | 1.69 m | 1.68 s | 2.05 s | 1.85 m |
| 4 m/s | 6.76 m | 3.38 s | 3.75 s | 7.41 m |
| 6 m/s | 15.24 m | 5.08 s | 5.45 s | 16.67 m |

## 45° bank wall (Hole 2 Dogleg)

| Shot | Part | Speed in | Speed out | Angle in | Angle out | Normal restitution | Tangential retention | Speed kept |
|---|---|---|---|---|---|---|---|---|
| bank-4mps | Hole2/Wall | 2.04 m/s | 1.74 m/s | 45° | 51° | 0.76 | 0.94 | 0.85 |
| bank-6mps | Hole2/Wall | 4.84 m/s | 4.23 m/s | 45° | 50.7° | 0.78 | 0.96 | 0.87 |

## Walls and bumper posts

| Shot | Part | Speed in | Speed out | Angle in | Angle out | Normal restitution | Tangential retention | Speed kept |
|---|---|---|---|---|---|---|---|---|
| wall-straight-3mps | ? | 1.88 m/s | 1.39 m/s | 0° | 0° | 0.74 | - | 0.74 |
| wall-straight-6mps | Hole1/Wall | 5.49 m/s | 4.30 m/s | 0° | 0° | 0.78 | - | 0.78 |
| wall-45deg-5mps | Hole1/Wall | 4.69 m/s | 4.11 m/s | 45° | 50.6° | 0.79 | 0.96 | 0.88 |
| post-straight-6mps | Hole2/Bumper | 5.79 m/s | 5.23 m/s | 0° | 0° | 0.90 | - | 0.90 |
| post-45deg-5mps | Hole2/Bumper | 4.74 m/s | 4.42 m/s | 45.6° | 53.5° | 0.79 | 1.05 | 0.93 |

## Windmill (Hole 4)

| Shot | Outcome | Contacts | Distance | Speed at cup |
|---|---|---|---|---|
| mill-phase0 | rest | ? (3.45 m/s in), Hole4/House (4.99 m/s in), Hole4/House (4.06 m/s in), Hole4/Wall (2.48 m/s in) | 11.35 m | - |
| mill-phase45 | rest | none | 11.16 m | - |

## The Hill (Hole 3)

| Shot | Outcome | Reached green | Ended on green | Rolled back | Max height | Final position |
|---|---|---|---|---|---|---|
| hill-strong-5mps | rest | yes | yes | no | 2.32 | [77.3038, 2.2791, 25.7588] |
| hill-weak-3mps | rest | no | no | yes | 1.60 | [75.8569, 1.0792, 5.9327] |

## Cup drop (Hole 1, from 60 cm)

| Putt speed | Speed at rim | Outcome | Holed on first pass |
|---|---|---|---|
| 1.3 m/s | 0.45 m/s | cup | no |
| 1.6 m/s | 0.87 m/s | cup | no |
| 2 m/s | 1.52 m/s | rest | no |
| 2.5 m/s | 2.23 m/s | rest | no |
| 3 m/s | 2.15 m/s | rest | no |
| 4 m/s | 3.84 m/s | rest | no |

## Ledge plane snap (SimulateVR)

Heights are relative to the plane the ball rests on (studs; 1 stud = 30 cm).

| Case | Ball plane Y | VR rig floor Δ | Character feet Δ | Putter head bottom Δ | Pass |
|---|---|---|---|---|---|
| h1-ball-at-wall | 0.999 | -0.995 | -0.532 | 0.511 | no |
| h1-stance-on-wall | 0.999 | -0.995 | -0.340 | 0.511 | no |
| h3-green-edge | 2.199 | -2.199 | -0.436 | 0.511 | no |

## Club ghosting (SimulateVR)

| Sweep | Max follow error | Max lift | Ball moved | Hits | Club parts non-colliding | Pass |
|---|---|---|---|---|---|---|
| through-wall | 2.779 | 8.984 | 0 | 0 | yes | no |
| through-post | 4.016 | 8.977 | 0 | 0 | yes | no |

VR swing through the ball (putter face 1.2 m/s): hit=yes source=vr ball speed 6.80 studs/s (expected 6.80), outcome rest, 1.84 m. Pass: yes

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
