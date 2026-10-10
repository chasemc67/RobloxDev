# VR Mini Golf playtest summary

- Run: 2026-10-09 22:49
- Scenarios: h7pin, h8door, movers
- Cameras: default
- SimulateVR: False

## Hole 7 sliding log pin hunt

Cases: 42, pinned > 0.5 s or nudged: 5, longest pinned contact: 0.5 s

| Case | Touched log | Max pinned (s) | Nudges | Finish zone |
|---|---|---|---|---|
| parked x=8.40 z=-20.50 | no | 0 | 0 | t2 |
| parked x=8.40 z=-19.98 | yes | 0.05 | 0 | t2 |
| parked x=8.40 z=-21.02 | yes | 0.03 | 0 | t2 |
| parked x=8.60 z=-20.50 | no | 0 | 0 | t2 |
| parked x=8.60 z=-19.98 | no | 0 | 0 | t2 |
| parked x=8.60 z=-21.02 | no | 0 | 0 | t2 |
| parked x=9.00 z=-20.50 | no | 0 | 0 | t2 |
| parked x=9.00 z=-19.98 | no | 0 | 0 | t2 |
| parked x=9.00 z=-21.02 | no | 0 | 0 | t2 |
| parked x=9.85 z=-20.50 | no | 0 | 0 | t2 |
| parked x=9.85 z=-19.98 | no | 0 | 0 | t2 |
| parked x=9.85 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-8.40 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-8.40 z=-19.98 | yes | 0.08 | 0 | t2 |
| parked x=-8.40 z=-21.02 | yes | 0.02 | 0 | t2 |
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
| parked x=0.00 z=-19.98 | yes | 0.23 | 1 | t2 |
| parked x=0.00 z=-21.02 | yes | 0.5 | 1 | t2 |
| parked x=5.00 z=-20.50 | yes | 0.25 | 1 | t2 |
| parked x=5.00 z=-19.98 | yes | 0.5 | 1 | t2 |
| parked x=5.00 z=-21.02 | yes | 0.5 | 1 | t2 |
| putt x=7.5 phase=0.0 | yes | 0 | 0 | t2 |
| putt x=-7.5 phase=0.0 | no | 0 | 0 | t2 |
| putt x=0.0 phase=0.0 | yes | 0 | 0 | t2 |
| putt x=7.5 phase=1.2 | no | 0 | 0 | t2 |
| putt x=-7.5 phase=1.2 | no | 0 | 0 | t2 |
| putt x=0.0 phase=1.2 | yes | 0.02 | 0 | t2 |
| putt x=7.5 phase=2.4 | no | 0 | 0 | t2 |
| putt x=-7.5 phase=2.4 | yes | 0 | 0 | t2 |
| putt x=0.0 phase=2.4 | yes | 0 | 0 | t2 |
| putt x=7.5 phase=3.6 | no | 0 | 0 | t2 |
| putt x=-7.5 phase=3.6 | no | 0 | 0 | t2 |
| putt x=0.0 phase=3.6 | yes | 0.05 | 0 | t2 |

## Hole 8 root door vs balls at the alcove rails

Door range: [-1.68, 1.66]

| Start | Max speed | Max rise | Max pinned (s) | Flags | Finish zone |
|---|---|---|---|---|---|
| [4.75, -8.1] | 0.001 | 0 | 0 | - | junction |
| [4.75, -14.9] | 0.001 | 0 | 0 | - | junction |
| [4.5, -8.2] | 0.001 | 0 | 0.05 | - | junction |
| [5, -14.8] | 1.952 | 0 | 0.03 | - | junction |
| [4.75, -9] | 4.103 | 0.001 | 0.08 | - | junction |
| [3.9, -8.1] | 0.001 | 0 | 0 | - | junction |

## Moving parts vs spec

| Mover | Hole | Value error | Blocker pose error (studs) | Server owned | Client lag (s) |
|---|---|---|---|---|---|
| root_gate | Hole9 | -0.000 | 0.000 | yes | 0.185 |
| lantern_bar | Hole9 | -0.009 | 0.000 | yes | 0.185 |
| root_door | Hole8 | -0.000 | 0.000 | yes | 0.185 |
| millwheel | Hole6 | -0.006 | 0.000 | yes | 0.185 |
| spinner | Hole4 | -0.008 | 0.000 | yes | 0.185 |
| log | Hole7 | -0.001 | 0.001 | yes | 0.185 |

Pass: yes

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
