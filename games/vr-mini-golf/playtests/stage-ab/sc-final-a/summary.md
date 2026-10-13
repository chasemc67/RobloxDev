# VR Mini Golf playtest summary

- Run: 2026-10-12 17:15
- Scenarios: h1, h2, h3, h4, h5, h6, h7, h8, h9
- Cameras: default
- SimulateVR: False

## Lantern Grove per-hole suites

Intended = the waypoint line played best-of-K per stroke (aim ±3/6°, speed ±10-25% from the same spot; every counted stroke is a real in-engine shot), good / safe. Routes = strokes to hole out with the spec's AI waypoints, one shot per stroke (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Intended (good / safe) | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|---|
| 1 Trailhead Gate | 2 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 2 Mine-Cart Junction | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 3 Ranger's Riverbend | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 4 Crystal Corridor | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 5 Echo Slot | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 6 Flash Flood | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 1 |
| 7 Rope Bridge Run | 4 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 8 Gumdrop Gulch | 3 | - / - | - | - | - | - | - | 8/0/0/2 | 0 / 2 / 0 |
| 9 Lollipop Windmill | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 1 |

- h6 issues: unstuck h6-fuzz-8 at [276.9238, 26.09, -4770.2856]
- h8 issues: stuck-3s h8-fuzz-2 at [356.0893, 69.7814, -4961]; stuck-3s h8-fuzz-7 at [362.4256, 69.7814, -4969]
- h9 issues: unstuck h9-fuzz-4 at [347.0711, 70.09, -5110.3945]

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
