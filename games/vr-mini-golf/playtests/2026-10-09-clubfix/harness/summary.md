# VR Mini Golf playtest summary

- Run: 2026-10-09 19:59
- Scenarios: clubviz, ledge, ghost
- Cameras: default
- SimulateVR: True

## Ledge plane snap (SimulateVR)

Heights are relative to the plane the ball rests on (studs; 1 stud = 30 cm).

| Case | Ball plane Y | VR rig floor Δ | Character feet Δ | Putter head bottom Δ | Wall group (player collides) | Pass |
|---|---|---|---|---|---|---|
| h1-ball-at-wall | 0.999 | 0.001 | 0.001 | 0.011 | GolfWall (no) | yes |
| h1-stance-on-wall | 0.999 | 0.001 | 0.001 | 0.011 | GolfWall (no) | yes |
| h3-green-edge | 2.199 | 0.001 | 0.001 | 0.011 | GolfWall (no) | yes |

## VR club mount (SimulateVR, putting-grip hand pose)

| Mount | Shaft vs handle | Shaft start gap (studs) | Shaft lean | Head bottom above plane | Head to target | Aim ray elevation |
|---|---|---|---|---|---|---|
| legacy | 125° | 0.400 | 136.4° | 4.976 | 5.130 | 46.4° |
| grip | 0° | 0 | 11.4° | 0.011 | 0.001 | 46.4° |

A-button re-fit from that pose: shaft lean 0°, shaft start gap 0, head bottom above plane 0.011, length 2.538 -> 2.748 studs (pass yes)

Pass (grip mount + re-fit): yes

## Club ghosting (SimulateVR)

| Sweep | Max follow error | Max lift | Ball moved | Hits | Club parts non-colliding | Pass |
|---|---|---|---|---|---|---|
| through-wall | 0 | 0.008 | 0 | 0 | yes | yes |
| through-post | 0 | 0.001 | 0 | 0 | yes | yes |

VR swing through the ball (putter face 1.2 m/s): hit=yes source=vr ball speed 6.80 studs/s (expected 6.80), outcome rest, 4.70 m. Pass: yes

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
