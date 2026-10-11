# VR Mini Golf playtest summary

- Run: 2026-10-11 10:12
- Scenarios: blockrate, movers
- Cameras: default
- SimulateVR: True

## Moving parts vs spec

| Mover | Hole | Value error | Blocker pose error (studs) | Server owned | Client lag (s) |
|---|---|---|---|---|---|
| root_gate | Hole9 | 0.001 | 0.001 | yes | 0.185 |
| root_door | Hole8 | 0.002 | 0.002 | yes | 0 |
| millwheel | Hole6 | 0.002 | 0.000 | yes | 0.18 |
| lantern_pendulum | Hole9 | -0.019 | 0.003 | yes | 0.19 |
| log | Hole7 | -0.000 | 0.000 | yes | 0.18 |
| spinner | Hole4 | 0.002 | 0.000 | yes | 0.18 |

Pass: yes

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
