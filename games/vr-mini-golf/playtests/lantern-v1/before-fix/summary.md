# VR Mini Golf playtest summary

- Run: 2026-10-09 22:42
- Scenarios: h7pin, h8door
- Cameras: default
- SimulateVR: False

## Hole 7 sliding log pin hunt

Cases: 42, pinned > 0.5 s or nudged: 4, longest pinned contact: 1.45 s

| Case | Touched log | Max pinned (s) | Nudges | Finish zone |
|---|---|---|---|---|
| parked x=8.40 z=-20.50 | yes | 0.03 | 0 | t2 |
| parked x=8.40 z=-19.98 | yes | 0.08 | 0 | t2 |
| parked x=8.40 z=-21.02 | yes | 0.08 | 0 | t2 |
| parked x=8.60 z=-20.50 | yes | 0.07 | 0 | t2 |
| parked x=8.60 z=-19.98 | no | 0 | 0 | t2 |
| parked x=8.60 z=-21.02 | no | 0 | 0 | t2 |
| parked x=9.00 z=-20.50 | no | 0 | 0 | t2 |
| parked x=9.00 z=-19.98 | no | 0 | 0 | t2 |
| parked x=9.00 z=-21.02 | no | 0 | 0 | t2 |
| parked x=9.85 z=-20.50 | no | 0 | 0 | t2 |
| parked x=9.85 z=-19.98 | no | 0 | 0 | t2 |
| parked x=9.85 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-8.40 z=-20.50 | yes | 0.02 | 0 | t2 |
| parked x=-8.40 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-8.40 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-8.60 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-8.60 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-8.60 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-21.02 | no | 0 | 0 | t2 |
| parked x=0.00 z=-20.50 | no | 0 | 0 | t2 |
| parked x=0.00 z=-19.98 | yes | 1.02 | 0 | t2 |
| parked x=0.00 z=-21.02 | yes | 1.07 | 0 | t2 |
| parked x=5.00 z=-20.50 | yes | 0.03 | 0 | t2 |
| parked x=5.00 z=-19.98 | yes | 1.43 | 0 | t2 |
| parked x=5.00 z=-21.02 | yes | 1.45 | 0 | t2 |
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
| putt x=0.0 phase=3.6 | yes | 0.02 | 0 | t2 |

## Hole 8 root door vs balls at the alcove rails

Door range: [-2.5, 2.5]

| Start | Max speed | Max rise | Max pinned (s) | Flags | Finish zone |
|---|---|---|---|---|---|
| [4.75, -8.1] | 9.011 | 0 | 0.32 | - | junction |
| [4.75, -14.9] | 3.276 | 0 | 0.15 | - | None |
| [4.5, -8.2] | 3.209 | 0.005 | 0.5 | unstuck | junction |
| [5, -14.8] | 4.849 | 0.001 | 0.57 | - | junction |
| [4.75, -9] | 3.8 | 0.004 | 0.5 | unstuck | junction |
| [3.9, -8.1] | 0.001 | 0 | 0 | - | junction |

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
