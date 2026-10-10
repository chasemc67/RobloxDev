# Stage b random-shot sweep (2026-10-10)

`python3 tools/run_playtests.py holes N.. --opts '{"parts":"fuzz","fuzz":20}'`: 20 random shots per hole (any direction, 20-100% power; 1 in 3 from the tee, the rest from random felt spots).

| Hole | Shots | Escapes | Stuck | Auto-resets | Nudges | Water | Holed | Console |
|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 0 | 0 | - | 0 | 0 | 0 | 0 |
| 2 | 20 | 0 | 0 | - | 0 | 1 | 0 | 0 |
| 3 | 20 | 0 | 0 | - | 0 | 0 | 1 | 0 |
| 4 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 20 | 0 | 0 | - | 0 | 2 | 1 | 0 |
| 6 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 | 20 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| 8 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 9 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

`tpcheck` (targeted, `run tpcheck`): H8 ring entries at 4-12 studs/s exit at 4.2-8.5 and end in the cup (8-12) or rest on the green (4-6), never off the back rail; H9 Lantern Knot entries at 4-12 all teleport (exit 4-10), 4-10 hole out. H9 root gate: 5 balls parked under/next to it are pushed ~3 studs aside (2.5 studs/s) as it closes, no pins, no hops. Auto-reset: a moving ball held still on H4 resets to the stroke start after 3.2 s; on H1 (no movers) it does not. 0 console errors/warnings; smoke (normal solo play) 0/0.
