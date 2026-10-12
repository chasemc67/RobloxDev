# VR Mini Golf playtest summary

- Run: 2026-10-11 18:42
- Scenarios: progress, ghost
- Cameras: default
- SimulateVR: True

## Club ghosting (SimulateVR)

| Sweep | Max follow error | Max lift | Ball moved | Hits | Club parts non-colliding | Pass |
|---|---|---|---|---|---|---|
| through-rail | 0 | 0.001 | 0 | 0 | yes | yes |
| through-bumper | 0 | 0.001 | 0 | 0 | yes | yes |

VR swing through the ball (putter face 1.2 m/s): hit=yes source=vr ball speed 6.81 studs/s (expected 6.80), outcome rest, 2.90 m. Pass: yes

## Hole-to-hole progression

| Hole | Sunk | Next hole | Ball to next tee | VR rig to ball | HUD | Pass |
|---|---|---|---|---|---|---|
| 1 | yes | 2 | 0 | 1.5 | Hole 2  -  Par 2 | yes |
| 2 | yes | 3 | 0 | 1.5 | Hole 3  -  Par 3 | yes |
| 3 | yes | 4 | 0 | 1.5 | Hole 4  -  Par 3 | yes |
| 4 | yes | 5 | 0 | 1.5 | Hole 5  -  Par 3 | yes |
| 5 | yes | 6 | 0 | 1.5 | Hole 6  -  Par 3 | yes |
| 6 | yes | 7 | 0 | 1.5 | Hole 7  -  Par 3 | yes |
| 7 | yes | 8 | 0 | 1.5 | Hole 8  -  Par 4 | yes |
| 8 | yes | 9 | 0 | 1.5 | Hole 9  -  Par 4 | yes |
| 9 | yes | course complete: yes | | | final scorecard: yes | yes |

Pass: yes

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
