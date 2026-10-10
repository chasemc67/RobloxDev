# Stage c (2026-10-10): spec v2 re-import, props pass 6 + world pieces

All sweeps: `python3 tools/run_playtests.py holes N.. --opts '{"parts":"fuzz","fuzz":20}'`, 20 random shots per hole
(any direction, 20-100% power, 1 in 3 from the tee).

## Final sweep (`sweep-c-final/`, after pass-6 props + world pieces)

| Hole | Shots | Escapes | Stuck | Auto-resets | Stroke timeouts | Nudges | Water | Holed | Console |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 0 | 0 | - | 0 | 0 | 0 | 0 | 0 |
| 2 | 20 | 0 | 0 | - | 0 | 0 | 0 | 0 | 0 |
| 3 | 20 | 0 | 0 | - | 0 | 0 | 0 | 1 | 0 |
| 4 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 20 | 0 | 0 | - | 0 | 0 | 2 | 1 | 0 |
| 6 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 | 20 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |
| 8 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 9 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Earlier runs
- `sweep-v2/` (H4, H5, H7, H8, H9 right after the v2 regenerate): clean except **H9: 2 auto-resets** in the new tunnel
  dip (a ball rocking in the V between the two sloped pieces never satisfies the rest rule). Fixed: BallController
  `valleyPoint` settles a slow ball within 0.15 of the crease. `sweep-v2-h9/`: same 20 seeded shots, 0 resets.
- `sweep-c/` (all 9 after the world pieces): 0/0/0/0, 0 console errors.
- `h8door/`: H8 door now slides the full +-3.5 into its pockets (through rails 14/16, movers don't collide with
  walls). Phase-aware parked-ball cases: 6/6 pushed aside, 0 pinned (BallController `pushFromSliding`).
  `h7pin` (in the same folder): log stops 0.5 short at +-7; side scrapes <= 1.5 s, handled by the 1.5 s pin nudge.
- Stroke timeout (Config.StrokeTimeout 20 s): verified with a temporary 1.5 s value on H1: 3/3 shots reset exactly to
  their stroke start (flag `autoreset/timeout`); value restored to 20.
- H9 pendulum (server): angle range [-35.1, 35.0], max error 1.06 deg vs 35 sin(2 pi t / 4). H5 respawn point sits on the
  felt at the bridge entry (world 86.5, 38.11, -110).

## Shots
`shots/` (Studio MCP screen_capture, Edit mode): hole01..09, overview, overview_aerial, h9_heart, h9_pendulum,
h2_chutes, h8_alcove. Also copied to `playtests/lantern-v1/overview*.png` and `hole01..09.png`.

## Interim prop overrides (used before 3D Model Bot's pass 6 landed, now removed)
`tools/props_overrides.json` briefly patched the pass-5 manifest for spec v2:
- H8: exit ring to (9, 1.5, -47) at yaw -26.57; bank2 backing stone and the c2 root arch 9 studs nearer the tee.
- H7: gap lantern posts to x 3.75 / 6.75.
- H4: carousel bar scaled to 6 long.
- H9: lantern bar and post removed; lantern_large (x0.85) as the pendulum bob.
- H4: side-gap lantern posts.

Pass 6 covers all of these, so the file is empty again; the mechanism stays for future spec-ahead-of-props gaps.
