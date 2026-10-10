# VR Mini Golf playtest summary

- Run: 2026-10-10 10:43
- Scenarios: h1, h2, h3, h4, h5, h6, h7, h8, h9, h7pin, h8door, movers
- Cameras: default
- SimulateVR: False

## Lantern Grove per-hole suites

Intended = the waypoint line played best-of-K per stroke (aim ±3/6°, speed ±10-25% from the same spot; every counted stroke is a real in-engine shot), good / safe. Routes = strokes to hole out with the spec's AI waypoints, one shot per stroke (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Intended (good / safe) | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|---|
| 1 Lantern Gate | 2 | 2 / 2 | 2 | 2 | no (24 tries) | deflector-45: 0.57, lane-rail-30: 0.48 | - | 12/0/0/0 | 0 / 0 / 0 |
| 2 Acorn Ledge | 2 | 2 / 2 | 2 | 2 | yes (aim 281.7°, 14.7 studs/s) | stump-headon: 0.59, lane-rail-40: 0.42 | - | 12/0/0/0 | 0 / 0 / 2 |
| 3 Toadstool Row | 3 | 3 / 3 | 5 | 5 | no (24 tries) | bank1-ride: 0.55, bank2-ride: 0.49 | - | 12/0/0/0 | 0 / 0 / 0 |
| 4 Spore Spinner | 3 | 1 / 2 | 2 | 6 | yes (aim 273.2°, 19.3 studs/s) | plaza-rail-45: 1.14, ramp-rail: 19.64 | spinner 6/6 clear | 12/0/0/0 | 0 / 0 / 0 |
| 5 Rootbridge Crossing | 3 | 2 / 3 | 2 | 3 | no (24 tries) | shore-rail-45: 0.54, covered-rail: 0.46 | - | 12/1/0/0 | 0 / 0 / 0 |
| 6 Mill Wheel Run | 3 | 2 / 2 | 2 | 3 | no (24 tries) | board1: 0.58, board2: 0.58 | millwheel 6/6 clear | 12/0/0/0 | 0 / 1 / 29 |
| 7 Cascade Steps | 3 | 2 / 3 | 2 | 3 | no (24 tries) | t2-rail-45: 0.55, t3-rail: 0.56 | log 6/6 clear | 12/2/0/0 | 0 / 0 / 2 |
| 8 Firefly Hollow | 4 | 6 / 4 | 6 | 4 | no (24 tries) | bank1-ride: 0.48, bank2-ride: 0.41 | root_door 6/6 clear | 12/0/0/0 | 0 / 0 / 1 |
| 9 Heart of the Grove | 4 | 6 / 3 | 3 | 4 | no (24 tries) | bank1-ride: 19.36, root-deflector: 0.55 | root_gate 6/6 clear; lantern_bar 6/6 clear | 12/0/0/0 | 0 / 0 / 6 |

- h2 issues: unstuck None at [210.2527, 21.1252, 98.0033]; unstuck None at [210.2559, 21.1282, 98.0013]
- h6 issues: unstuck h6-good-s1 at [27.0795, 30.1593, -56.772]; unstuck h6-average-s2 at [29.9986, 30.1967, -55.898]; unstuck h6-average-s2 at [29.9986, 30.1, -57.9612]; unstuck h6-int-good-s1-1 at [27.0786, 30.1712, -56.5035]; unstuck h6-int-good-s1-3 at [27.0798, 30.2281, -55.1424]; unstuck h6-int-good-s1-3 at [27.0798, 30.0998, -57.961]; unstuck h6-hio-1 at [27.0797, 30.3154, -53.0502]; unstuck h6-hio-3 at [27.078, 30.3034, -53.3295]; unstuck h6-hio-3 at [27.078, 30.1088, -57.9935]; unstuck h6-hio-5 at [27.0786, 30.3086, -53.2105]; unstuck h6-hio-7 at [27.0779, 30.3143, -53.0775]; unstuck h6-hio-9 at [27.0794, 30.3171, -53.0093]
- h7 issues: unstuck h7-int-average-s2-2 at [38.9787, 23.7062, 0.2578]; unstuck h7-fuzz-5 at [37.3021, 23.7852, 10.8696]
- h8 issues: unstuck h8-int-good-s5-1 at [-15.7797, 36.09, -14.2637]
- h9 issues: unstuck h9-good-s2 at [-83.628, 39.5167, -7.4647]; unstuck h9-good-s2 at [-87.3267, 39.2968, -9.3932]; unstuck h9-hio-16 at [-77.2536, 41.09, 14.4022]; unstuck h9-sweep-root_gate-5 at [-78.6416, 41.09, 11.9745]; unstuck h9-sweep-lantern_bar-1 at [-79.3834, 41.09, 13.4746]; unstuck h9-sweep-lantern_bar-2 at [-79.2698, 41.09, 13.542]

## Hole 7 sliding log pin hunt

Cases: 42, pinned > 0.5 s or nudged: 4, longest pinned contact: 0.5 s

| Case | Touched log | Max pinned (s) | Nudges | Finish zone |
|---|---|---|---|---|
| parked x=8.40 z=-20.50 | yes | 0.03 | 0 | t2 |
| parked x=8.40 z=-19.98 | no | 0 | 0 | t2 |
| parked x=8.40 z=-21.02 | yes | 0.05 | 0 | t2 |
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
| parked x=-8.40 z=-19.98 | yes | 0.1 | 0 | t2 |
| parked x=-8.40 z=-21.02 | yes | 0.1 | 0 | t2 |
| parked x=-8.60 z=-20.50 | yes | 0.03 | 0 | t2 |
| parked x=-8.60 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-8.60 z=-21.02 | yes | 0.03 | 0 | t2 |
| parked x=-9.00 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-21.02 | no | 0 | 0 | t2 |
| parked x=0.00 z=-20.50 | yes | 0.4 | 0 | t2 |
| parked x=0.00 z=-19.98 | yes | 0.2 | 1 | t2 |
| parked x=0.00 z=-21.02 | yes | 0.5 | 1 | t2 |
| parked x=5.00 z=-20.50 | yes | 0.03 | 0 | t2 |
| parked x=5.00 z=-19.98 | yes | 0.43 | 1 | t2 |
| parked x=5.00 z=-21.02 | yes | 0.22 | 1 | t2 |
| putt x=7.5 phase=0.0 | yes | 0 | 0 | t2 |
| putt x=-7.5 phase=0.0 | no | 0 | 0 | t2 |
| putt x=0.0 phase=0.0 | yes | 0 | 0 | t2 |
| putt x=7.5 phase=1.2 | no | 0 | 0 | t2 |
| putt x=-7.5 phase=1.2 | no | 0 | 0 | t2 |
| putt x=0.0 phase=1.2 | yes | 0.08 | 0 | t2 |
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
| [4.75, -14.9] | 0.001 | 0 | 0.03 | - | junction |
| [4.5, -8.2] | 0.001 | 0 | 0 | - | junction |
| [5, -14.8] | 0.001 | 0 | 0 | - | junction |
| [4.75, -9] | 5.286 | 0.002 | 0.07 | - | junction |
| [3.9, -8.1] | 0.001 | 0 | 0 | - | junction |

## Moving parts vs spec

| Mover | Hole | Value error | Blocker pose error (studs) | Server owned | Client lag (s) |
|---|---|---|---|---|---|
| millwheel | Hole6 | -0.023 | 0.001 | yes | 0.175 |
| log | Hole7 | 0.004 | 0.004 | yes | 0.175 |
| root_gate | Hole9 | -0.000 | 0.000 | yes | 0.175 |
| root_door | Hole8 | -0.002 | 0.002 | yes | 0.175 |
| lantern_bar | Hole9 | -0.031 | 0.000 | yes | 0.175 |
| spinner | Hole4 | -0.028 | 0.001 | yes | 0.175 |

Pass: yes

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
