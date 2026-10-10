# VR Mini Golf playtest summary

- Run: 2026-10-10 12:31
- Scenarios: h1, h2, h3, h4, h5
- Cameras: default
- SimulateVR: False

## Lantern Grove per-hole suites

Intended = the waypoint line played best-of-K per stroke (aim ±3/6°, speed ±10-25% from the same spot; every counted stroke is a real in-engine shot), good / safe. Routes = strokes to hole out with the spec's AI waypoints, one shot per stroke (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Intended (good / safe) | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|---|
| 1 Lantern Gate | 2 | 2 / 2 | 2 | 2 | no (30 tries) | deflector-45: 0.57, lane-rail-30: 0.48 | - | 12/0/0/0 | 0 / 0 / 0 |
| 2 Acorn Ledge | 2 | 2 / 2 | 2 | 2 | no (30 tries) | stump-headon: 0.59, lane-rail-40: 0.54 | - | 12/0/0/0 | 0 / 0 / 0 |
| 3 Toadstool Row | 3 | 3 / 3 | 5 | 5 | no (30 tries) | bank1-ride: 0.42, bank2-ride: 0.49 | - | 12/0/0/0 | 0 / 0 / 0 |
| 4 Spore Spinner | 3 | 2 / 2 | 1 | 3 | yes (aim 273.5°, 17.9 studs/s) | plaza-rail-45: 0.55, ramp-rail: 20.25 | spinner 6/6 clear | 12/0/0/0 | 0 / 0 / 0 |
| 5 Rootbridge Crossing | 3 | 2 / 3 | 2 | 3 | no (30 tries) | shore-rail-45: 0.47, covered-rail: 0.52 | - | 12/1/0/0 | 0 / 0 / 0 |


## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
