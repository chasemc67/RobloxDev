# VR Mini Golf playtest summary

- Run: 2026-10-09 23:54
- Scenarios: h1, h2, h3, h4, h5, h6, h7, h8, h9
- Cameras: default
- SimulateVR: False

## Lantern Grove per-hole suites

Routes = strokes to hole out with the spec's AI waypoints (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|
| 1 Lantern Gate | 2 | 3 | 3 | no (24 tries) | deflector-45: 0.51, lane-rail-30: 0.50 | - | 12/0/0/0 | 0 / 0 / 0 |
| 2 Acorn Ledge | 2 | 2 | 2 | yes (aim 281.8°, 14.6 studs/s) | stump-headon: 0.60, lane-rail-40: 0.52 | - | 12/0/0/0 | 0 / 0 / 0 |
| 3 Toadstool Row | 3 | 5 | 5 | no (24 tries) | bank1-ride: 0.51, bank2-ride: 0.48 | - | 12/0/0/0 | 0 / 0 / 0 |
| 4 Spore Spinner | 3 | 1 | 3 | yes (aim 273.2°, 19.3 studs/s) | plaza-rail-45: 1.14, ramp-rail: 19.60 | spinner 6/6 clear | 12/0/0/0 | 0 / 0 / 0 |
| 5 Rootbridge Crossing | 3 | 2 | 3 | yes (aim 271.3°, 19.6 studs/s) | shore-rail-45: 0.49, covered-rail: 0.52 | - | 12/1/0/0 | 0 / 0 / 0 |
| 6 Mill Wheel Run | 3 | 2 | 3 | no (24 tries) | board1: 0.58, board2: 0.58 | millwheel 6/6 clear | 12/0/0/0 | 1 / 0 / 0 |
| 7 Cascade Steps | 3 | 2 | 5 | no (24 tries) | t2-rail-45: 0.54, t3-rail: 0.56 | log 6/6 clear | 12/1/0/0 | 0 / 0 / 0 |
| 8 Firefly Hollow | 4 | 5 | 4 | no (24 tries) | bank1-ride: 0.49, bank2-ride: 0.46 | root_door 6/6 clear | 12/0/0/0 | 0 / 0 / 0 |
| 9 Heart of the Grove | 4 | 3 | 5 | no (24 tries) | bank1-ride: 18.24, root-deflector: 0.55 | root_gate 6/6 clear; lantern_bar 6/6 clear | 12/0/0/0 | 0 / 0 / 2 |

- h6 issues: escape h6-hio-20 at [92.8267, 4.5838, -73.0409]
- h9 issues: unstuck h9-hio-5 at [217.099, 11.0893, -91.994]; unstuck h9-sweep-root_gate-5 at [220.6531, 11.09, -97.2872]

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
