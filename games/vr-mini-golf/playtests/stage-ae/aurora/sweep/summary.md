# VR Mini Golf playtest summary

- Run: 2026-10-12 21:44
- Scenarios: h2
- Cameras: default
- SimulateVR: False

## Per-hole suites

Intended = the waypoint line played best-of-K per stroke (aim ±3/6°, speed ±10-25% from the same spot; every counted stroke is a real in-engine shot), good / safe. Routes = strokes to hole out with the spec's AI waypoints, one shot per stroke (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Intended (good / safe) | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|---|
| 2 Snowpuff Burrows | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |


## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
