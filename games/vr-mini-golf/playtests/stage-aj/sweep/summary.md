# VR Mini Golf playtest summary

- Run: 2026-10-13 11:18
- Scenarios: h1, h7, h8, h15
- Cameras: default
- SimulateVR: False

## Per-hole suites

Intended = the waypoint line played best-of-K per stroke (aim ±3/6°, speed ±10-25% from the same spot; every counted stroke is a real in-engine shot), good / safe. Routes = strokes to hole out with the spec's AI waypoints, one shot per stroke (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Intended (good / safe) | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|---|
| 1 Trailhead Gate | 2 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 7 Rope Bridge Run | 4 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 8 Gumdrop Gulch | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 15 Sugar Dune | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |

- h15 issues: autoreset h15-fuzz-2 at [-306.8198, 147.0338, -5085.6489]

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
