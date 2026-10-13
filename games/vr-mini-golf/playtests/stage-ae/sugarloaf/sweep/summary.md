# VR Mini Golf playtest summary

- Run: 2026-10-12 22:08
- Scenarios: h1, h2, h3, h4, h5, h6, h8, h9, h11, h14, h17
- Cameras: default
- SimulateVR: False

## Per-hole suites

Intended = the waypoint line played best-of-K per stroke (aim ±3/6°, speed ±10-25% from the same spot; every counted stroke is a real in-engine shot), good / safe. Routes = strokes to hole out with the spec's AI waypoints, one shot per stroke (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Intended (good / safe) | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|---|
| 1 Trailhead Gate | 2 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 2 Mine-Cart Junction | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 3 Ranger's Riverbend | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 4 Crystal Corridor | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 5 Echo Slot | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 6 Flash Flood | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 1 |
| 8 Gumdrop Gulch | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 9 Lollipop Windmill | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 1 |
| 11 Floodgate Lock | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 14 Ore Bucket Swing | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 17 Sundial | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |

- h6 issues: unstuck h6-slow-5 at [273.1874, 26.09, -4770.6387]
- h9 issues: unstuck h9-slow-3 at [348.6211, 70.09, -5109.5562]

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
