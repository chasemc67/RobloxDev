# VR Mini Golf playtest summary

- Run: 2026-10-10 14:21
- Scenarios: h4, h5, h7, h8, h9
- Cameras: default
- SimulateVR: False

## Lantern Grove per-hole suites

Intended = the waypoint line played best-of-K per stroke (aim ±3/6°, speed ±10-25% from the same spot; every counted stroke is a real in-engine shot), good / safe. Routes = strokes to hole out with the spec's AI waypoints, one shot per stroke (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Intended (good / safe) | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|---|
| 4 Spore Spinner | 3 | - / - | - | - | - | - | - | 20/0/0/0 | 0 / 0 / 0 |
| 5 Rootbridge Crossing | 3 | - / - | - | - | - | - | - | 20/2/0/0 | 0 / 0 / 0 |
| 7 Cascade Steps | 3 | - / - | - | - | - | - | - | 20/1/0/0 | 0 / 0 / 0 |
| 8 Firefly Hollow | 4 | - / - | - | - | - | - | - | 20/0/0/0 | 0 / 0 / 0 |
| 9 Heart of the Grove | 4 | - / - | - | - | - | - | - | 20/0/0/0 | 0 / 0 / 1 |

- h9 issues: autoreset h9-fuzz-6 at [-75.2215, 40.6807, 9.0247]; unstuck h9-fuzz-17 at [-77.1485, 40.7106, 8.014]; autoreset h9-fuzz-17 at [-77.1482, 40.6806, 8.0138]

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
