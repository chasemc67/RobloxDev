# VR Mini Golf playtest summary

- Run: 2026-10-12 02:18
- Scenarios: h7pin, movers
- Cameras: default
- SimulateVR: False

## Hole 7 sliding log pin hunt

Cases: 42, pinned > 0.5 s or nudged: 3, longest pinned contact: 0.92 s

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
| parked x=-8.40 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-8.40 z=-19.98 | yes | 0.03 | 0 | t2 |
| parked x=-8.40 z=-21.02 | yes | 0.03 | 0 | t2 |
| parked x=-8.60 z=-20.50 | yes | 0.67 | 0 | t2 |
| parked x=-8.60 z=-19.98 | yes | 0.92 | 0 | t2 |
| parked x=-8.60 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-9.00 z=-21.02 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-20.50 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-19.98 | no | 0 | 0 | t2 |
| parked x=-9.85 z=-21.02 | no | 0 | 0 | t2 |
| parked x=0.00 z=-20.50 | no | 0 | 0 | t2 |
| parked x=0.00 z=-19.98 | no | 0 | 0 | t2 |
| parked x=0.00 z=-21.02 | no | 0 | 0 | t2 |
| parked x=5.00 z=-20.50 | no | 0 | 0 | t2 |
| parked x=5.00 z=-19.98 | no | 0 | 1 | t2 |
| parked x=5.00 z=-21.02 | no | 0 | 0 | t2 |
| putt x=7.5 phase=0.0 | no | 0 | 0 | t2 |
| putt x=-7.5 phase=0.0 | no | 0 | 0 | t2 |
| putt x=0.0 phase=0.0 | no | 0 | 0 | t2 |
| putt x=7.5 phase=1.2 | no | 0 | 0 | t2 |
| putt x=-7.5 phase=1.2 | no | 0 | 0 | t2 |
| putt x=0.0 phase=1.2 | no | 0 | 0 | t2 |
| putt x=7.5 phase=2.4 | no | 0 | 0 | t2 |
| putt x=-7.5 phase=2.4 | no | 0 | 0 | t2 |
| putt x=0.0 phase=2.4 | yes | 0 | 0 | t2 |
| putt x=7.5 phase=3.6 | no | 0 | 0 | t2 |
| putt x=-7.5 phase=3.6 | yes | 0.05 | 0 | t2 |
| putt x=0.0 phase=3.6 | no | 0 | 0 | t2 |

## Moving parts vs spec

| Mover | Hole | Value error | Blocker pose error (studs) | Server owned | Client lag (s) |
|---|---|---|---|---|---|
| root_gate | Hole9 | -0.001 | 0.001 | yes | 0.18 |
| log | Hole7 | -0.005 | 0.005 | yes | 0.18 |
| lantern_pendulum | Hole9 | -0.014 | 0.002 | yes | 0.26 |
| spinner | Hole4 | -0.045 | 0.001 | yes | 0.18 |
| millwheel | Hole6 | -0.045 | 0.002 | yes | 0.18 |
| root_door | Hole8 | -0.006 | 0.006 | yes | 0.225 |

Pass: yes

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
