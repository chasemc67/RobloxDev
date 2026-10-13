# VR Mini Golf playtest summary

- Run: 2026-10-12 16:28
- Scenarios: h8, h9, h11, h12, h13, h17
- Cameras: default
- SimulateVR: False

## Lantern Grove per-hole suites

Intended = the waypoint line played best-of-K per stroke (aim ±3/6°, speed ±10-25% from the same spot; every counted stroke is a real in-engine shot), good / safe. Routes = strokes to hole out with the spec's AI waypoints, one shot per stroke (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Intended (good / safe) | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|---|
| 8 Gumdrop Gulch | 3 | - / - | - | - | - | - | - | -/-/-/- | 0 / 3 / 0 |
| 9 Lollipop Windmill | 3 | - / - | - | - | - | - | - | -/-/-/- | 0 / 3 / 0 |

- h8 issues: stuck-timeout h8-cupdrop-0 at [365.0002, 70.0757, -4999.9966]; stuck-timeout h8-cupdrop-1 at [365.0002, 70.0937, -4999.9966]; stuck-timeout h8-cupdrop-2 at [364.9998, 70.0671, -4999.9971]
- h9 issues: stuck-timeout h9-cupdrop-0 at [372.0002, 70.0724, -5111.4976]; stuck-timeout h9-cupdrop-1 at [372.0002, 70.0793, -5111.4976]; stuck-timeout h9-cupdrop-2 at [371.9998, 70.0921, -5111.4976]

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
