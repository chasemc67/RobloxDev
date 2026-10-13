# VR Mini Golf playtest summary

- Run: 2026-10-12 21:09
- Scenarios: h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15, h16, h17, h18
- Cameras: default
- SimulateVR: False

## Per-hole suites

Intended = the waypoint line played best-of-K per stroke (aim ±3/6°, speed ±10-25% from the same spot; every counted stroke is a real in-engine shot), good / safe. Routes = strokes to hole out with the spec's AI waypoints, one shot per stroke (good = aggressive/risk line, average = safe line). Banks = normal restitution of the first rail contact. Fuzz = shots / hazards / escapes / stuck.

| Hole | Par | Intended (good / safe) | Good line | Safe line | Hole-in-one | Banks (restitution) | Mover timing sweep | Fuzz | Escapes / stuck / nudges |
|---|---|---|---|---|---|---|---|---|---|
| 1 Lantern Quay | 2 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 2 Snowpuff Burrows | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 3 Glimmer Crossing | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 4 Glissade | 3 | - / - | - | - | - | - | - | 8/0/0/1 | 0 / 1 / 0 |
| 5 Geyser Hop | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 1 |
| 6 Palm Lagoon | 3 | - / - | - | - | - | - | - | 8/1/0/0 | 0 / 0 / 0 |
| 7 Mogul Meadow | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 8 Coral Pinball | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 9 Conch Shortcut | 4 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 10 Bobsled Bend | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 11 Floe Drift | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 12 Icebreaker Wheel | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 13 Snowpuff Carousel | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 14 Bell Buoy | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 15 Frozen Falls | 2 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 16 Moonwell | 2 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 17 Aurora Bridge | 3 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |
| 18 Halo Arch | 4 | - / - | - | - | - | - | - | 8/0/0/0 | 0 / 0 / 0 |

- h4 issues: forcedrest h4-fuzz-4 at [182.914, 84.0989, 460.9039]
- h5 issues: unstuck h5-slow-2 at [242.3398, 84.09, 418.0385]

## Console

- Server warnings/errors: 0
- Client warnings/errors: 0

Raw logs: `<scenario>[-<cam>].jsonl` and `results.json` in this folder.
