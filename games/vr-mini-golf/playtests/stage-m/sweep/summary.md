# VR Mini Golf playtest summary

- Run: 2026-10-11 10:44
- Scenarios: h1, h2, h3, h4, h5, h6, h7, h8, h9
- Cameras: default
- SimulateVR: False

## Lantern Grove per-hole suites

Intended = the waypoint line played best-of-K per stroke (aim ±3/6°, speed ±10-25% from the same spot; every counted stroke is a real in-engine shot), good / safe. Routes = strokes to hole out with the spec's AI waypoints, one shot per stroke (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Intended (good / safe) | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|---|
| 1 Lantern Gate | 2 | - / - | - | - | - | - | - | 10/0/0/0 | 0 / 0 / 0 |
| 2 Acorn Ledge | 2 | - / - | - | - | - | - | - | 10/0/0/0 | 0 / 0 / 0 |
| 3 Toadstool Row | 3 | - / - | - | - | - | - | - | 10/0/0/0 | 0 / 0 / 0 |
| 4 Spore Spinner | 3 | - / - | - | - | - | - | - | 10/0/0/0 | 0 / 0 / 0 |
| 5 Rootbridge Crossing | 3 | - / - | - | - | - | - | - | 10/1/0/0 | 0 / 0 / 0 |
| 6 Mill Wheel Run | 3 | - / - | - | - | - | - | - | 10/2/0/0 | 0 / 0 / 0 |
| 7 Cascade Steps | 3 | - / - | - | - | - | - | - | 10/1/0/0 | 0 / 0 / 0 |
| 8 Firefly Hollow | 4 | - / - | - | - | - | - | - | 10/0/0/0 | 0 / 0 / 0 |
| 9 Heart of the Grove | 4 | - / - | - | - | - | - | - | 10/0/0/0 | 0 / 0 / 0 |


## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
