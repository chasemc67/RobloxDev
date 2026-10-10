# VR Mini Golf playtest summary

- Run: 2026-10-10 01:33
- Scenarios: h1, h2, h3, h4, h5, h6, h7, h8, h9, h7pin, h8door, movers
- Cameras: default
- SimulateVR: False

## Lantern Grove per-hole suites

Routes = strokes to hole out with the spec's AI waypoints (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|
| 1 Lantern Gate | 2 | 2 | 2 | no (24 tries) | deflector-45: 0.57, lane-rail-30: 0.51 | - | 12/0/0/0 | 0 / 0 / 0 |
| 2 Acorn Ledge | 2 | 2 | 2 | yes (aim 281.8°, 16.0 studs/s) | stump-headon: 0.59, lane-rail-40: 0.54 | - | 12/0/0/0 | 0 / 0 / 0 |
| 3 Toadstool Row | 3 | 5 | 5 | no (24 tries) | bank1-ride: 0.48, bank2-ride: 0.47 | - | 12/0/0/0 | 0 / 0 / 0 |
| 4 Spore Spinner | 3 | 4 | 2 | yes (aim 273.2°, 19.3 studs/s) | plaza-rail-45: 1.14, ramp-rail: 20.80 | spinner 6/6 clear | 12/0/0/0 | 0 / 0 / 0 |
| 5 Rootbridge Crossing | 3 | 2 | 4 | no (24 tries) | shore-rail-45: 0.53, covered-rail: 0.53 | - | 12/1/0/0 | 0 / 0 / 0 |
| 6 Mill Wheel Run | 3 | 3 | 3 | no (24 tries) | board1: 0.51, board2: 0.53 | millwheel 6/6 clear | 12/0/0/0 | 0 / 0 / 0 |
| 7 Cascade Steps | 3 | 2 | 3 | no (24 tries) | t2-rail-45: 0.49, t3-rail: 0.56 | log 6/6 clear | 12/0/0/0 | 0 / 4 / 0 |
| 8 Firefly Hollow | 4 | 6 | 4 | no (24 tries) | bank1-ride: 0.48, bank2-ride: 0.49 | root_door 6/6 clear | 12/0/0/0 | 0 / 0 / 0 |
| 9 Heart of the Grove | 4 | 3 | 6 | no (24 tries) | bank1-ride: 18.56, root-deflector: 0.55 | root_gate 6/6 clear; lantern_bar 6/6 clear | 12/0/0/0 | 0 / 0 / 4 |

- h7 issues: forcedrest h7-hio-1 at [38.9607, 23.6691, -0.2476]; forcedrest h7-hio-10 at [38.9808, 23.6771, 0.1209]; forcedrest h7-hio-23 at [34.9025, 23.8286, -0.373]; forcedrest h7-sweep-log-2 at [38.9696, 23.6733, -0.4082]
- h9 issues: unstuck h9-hio-1 at [-78.5162, 41.09, 12.2186]; unstuck h9-hio-2 at [-78.1157, 41.09, 13.9717]; unstuck h9-hio-3 at [-77.7709, 41.09, 14.3556]; unstuck h9-sweep-lantern_bar-5 at [-79.1528, 41.09, 13.7939]

## Hole 7 sliding log pin hunt

Cases: 42, pinned > 0.5 s or nudged: 4, longest pinned contact: 0.5 s

| Case | Touched log | Max pinned (s) | Nudges | Finish zone |
|---|---|---|---|---|
| parked x=8.40 z=-20.50 | yes | 0.03 | 0 | t2 |
| parked x=8.40 z=-19.98 | yes | 0.07 | 0 | t2 |
| parked x=8.40 z=-21.02 | yes | 0.07 | 0 | t2 |
| parked x=8.60 z=-20.50 | no | 0 | 0 | t2 |
| parked x=8.60 z=-19.98 | no | 0 | 0 | t2 |
| parked x=8.60 z=-21.02 | no | 0 | 0 | t2 |
| parked x=9.00 z=-20.50 | no | 0 | 0 | t2 |
| parked x=9.00 z=-19.98 | no | 0 | 0 | t2 |
| parked x=9.00 z=-21.02 | no | 0 | 0 | t2 |
| parked x=9.85 z=-20.50 | no | 0 | 0 | t2 |
| parked x=9.85 z=-19.98 | no | 0 | 0 | t2 |
| parked x=9.85 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-8.40 z=-20.50 | yes | 0.03 | 0 | t2 |
| parked x=-8.40 z=-19.98 | yes | 0.07 | 0 | t2 |
| parked x=-8.40 z=-21.02 | yes | 0.05 | 0 | t2 |
| parked x=-8.60 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-8.60 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-8.60 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-21.02 | no | 0 | 0 | t2 |
| parked x=0.00 z=-20.50 | yes | 0.03 | 0 | t2 |
| parked x=0.00 z=-19.98 | yes | 0.5 | 1 | t2 |
| parked x=0.00 z=-21.02 | yes | 0.5 | 1 | t2 |
| parked x=5.00 z=-20.50 | yes | 0.02 | 0 | t2 |
| parked x=5.00 z=-19.98 | yes | 0.5 | 1 | t2 |
| parked x=5.00 z=-21.02 | yes | 0.5 | 1 | t2 |
| putt x=7.5 phase=0.0 | yes | 0 | 0 | t2 |
| putt x=-7.5 phase=0.0 | no | 0 | 0 | t2 |
| putt x=0.0 phase=0.0 | no | 0 | 0 | t2 |
| putt x=7.5 phase=1.2 | no | 0 | 0 | t2 |
| putt x=-7.5 phase=1.2 | no | 0 | 0 | t2 |
| putt x=0.0 phase=1.2 | yes | 0 | 0 | t2 |
| putt x=7.5 phase=2.4 | no | 0 | 0 | t2 |
| putt x=-7.5 phase=2.4 | yes | 0 | 0 | t2 |
| putt x=0.0 phase=2.4 | no | 0 | 0 | t2 |
| putt x=7.5 phase=3.6 | no | 0 | 0 | t2 |
| putt x=-7.5 phase=3.6 | no | 0 | 0 | t2 |
| putt x=0.0 phase=3.6 | yes | 0.07 | 0 | t2 |

## Hole 8 root door vs balls at the alcove rails

Door range: [-1.68, 1.68]

| Start | Max speed | Max rise | Max pinned (s) | Flags | Finish zone |
|---|---|---|---|---|---|
| [4.75, -8.1] | 0.001 | 0 | 0 | - | junction |
| [4.75, -14.9] | 0.001 | 0 | 0 | - | junction |
| [4.5, -8.2] | 0.001 | 0 | 0 | - | junction |
| [5, -14.8] | 0.001 | 0 | 0.02 | - | junction |
| [4.75, -9] | 3.901 | 0.001 | 0.05 | - | junction |
| [3.9, -8.1] | 0.001 | 0 | 0 | - | junction |

## Moving parts vs spec

| Mover | Hole | Value error | Blocker pose error (studs) | Server owned | Client lag (s) |
|---|---|---|---|---|---|
| millwheel | Hole6 | -0.029 | 0.001 | yes | 0.19 |
| root_gate | Hole9 | -0.001 | 0.001 | yes | 0.19 |
| lantern_bar | Hole9 | -0.039 | 0.000 | yes | 0.19 |
| log | Hole7 | -0.004 | 0.004 | yes | 0.19 |
| root_door | Hole8 | -0.002 | 0.002 | yes | 0.19 |
| spinner | Hole4 | -0.035 | 0.002 | yes | 0.19 |

Pass: yes

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
