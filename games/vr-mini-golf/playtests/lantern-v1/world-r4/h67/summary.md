# VR Mini Golf playtest summary

- Run: 2026-10-10 11:44
- Scenarios: h6, h7, h7pin
- Cameras: default
- SimulateVR: False

## Lantern Grove per-hole suites

Intended = the waypoint line played best-of-K per stroke (aim ±3/6°, speed ±10-25% from the same spot; every counted stroke is a real in-engine shot), good / safe. Routes = strokes to hole out with the spec's AI waypoints, one shot per stroke (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Intended (good / safe) | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|---|
| 6 Mill Wheel Run | 3 | 2 / 2 | 3 | 3 | no (30 tries) | board1: 0.57, board2: 0.58 | millwheel 6/6 clear | 12/0/0/0 | 0 / 0 / 0 |
| 7 Cascade Steps | 3 | 3 / 2 | 3 | 3 | no (30 tries) | t2-rail-45: 0.45, t3-rail: 0.56 | log 6/6 clear | 12/2/0/0 | 0 / 2 / 3 |

- h7 issues: unstuck h7-int-good-s2-2 at [38.9933, 23.7095, 0.6545]; unstuck h7-hio-23 at [38.9828, 23.7058, 0.8789]; unstuck h7-hio-25 at [38.9501, 23.6917, -0.0736]; stuck-timeout h7-hio-25 at [39.462, 23.6793, -0.0736]; stuck-timeout h7-hio-26 at [38.9538, 23.6633, -0.0452]

## Hole 7 sliding log pin hunt

Cases: 42, pinned > 0.5 s or nudged: 5, longest pinned contact: 0.5 s

| Case | Touched log | Max pinned (s) | Nudges | Finish zone |
|---|---|---|---|---|
| parked x=8.40 z=-20.50 | no | 0 | 0 | t2 |
| parked x=8.40 z=-19.98 | no | 0 | 0 | t2 |
| parked x=8.40 z=-21.02 | no | 0 | 0 | t2 |
| parked x=8.60 z=-20.50 | no | 0 | 0 | t2 |
| parked x=8.60 z=-19.98 | no | 0 | 0 | t2 |
| parked x=8.60 z=-21.02 | no | 0 | 0 | t2 |
| parked x=9.00 z=-20.50 | no | 0 | 0 | t2 |
| parked x=9.00 z=-19.98 | no | 0 | 0 | t2 |
| parked x=9.00 z=-21.02 | no | 0 | 0 | t2 |
| parked x=9.85 z=-20.50 | no | 0 | 0 | t2 |
| parked x=9.85 z=-19.98 | no | 0 | 0 | t2 |
| parked x=9.85 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-8.40 z=-20.50 | yes | 0.03 | 0 | None |
| parked x=-8.40 z=-19.98 | yes | 0.03 | 0 | t2 |
| parked x=-8.40 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-8.60 z=-20.50 | yes | 0.02 | 0 | t2 |
| parked x=-8.60 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-8.60 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-21.02 | no | 0 | 0 | t2 |
| parked x=0.00 z=-20.50 | yes | 0.25 | 1 | t2 |
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
| putt x=0.0 phase=3.6 | yes | 0.08 | 0 | t2 |

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
