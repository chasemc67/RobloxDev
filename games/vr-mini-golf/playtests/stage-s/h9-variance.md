# H9 historical block-rate variance — Stage s

The 33.3% versus 41.7% difference is four phase samples changing their **post-contact crossing result**, for a net difference of two blocked shots. It is not a random-seed change: this old harness uses a fixed launch position, direction and speed and evenly spaced pendulum phases. No new aimed shots were run for this analysis.

| Saved run | Blocked | Touched | Cached client lag | Recorded launch phase error | Outcomes |
|---|---:|---:|---:|---:|---|
| Round 4 | 8/24 (33.3%) | 12/24 | 0.164 s | 0 to +0.01 s | 24 rest, 0 flags |
| Round 5 | 10/24 (41.7%) | 14/24 | 0.168 s | −0.01 to +0.02 s | 24 rest, 0 flags |
| Round 6 | 8/24 (33.3%) | 13/24 | 0.174 s | −0.01 to +0.01 s | 24 rest, 0 flags |
| Stage p | 19/48 (39.6%) | 32/48 | 0.163 s | −0.01 to +0.01 s | 48 rest, 0 flags |
| Stage q | 18/48 (37.5%) | 31/48 | 0.163 s | −0.01 to +0.01 s | 48 rest, 0 flags |

All periods were 4 seconds. Round 5 and Round 6 raw-log physics and Config headers are identical, including gravity 32.7, drag/deceleration, wall restitution 0.63 and bumper restitution 0.65. Stage p/q are supporting historical observations, not controlled identical-build repeats.

## What changed between Round 5 and Round 6

The old definition is `blocked = touched mover AND never crossed the obstacle line by >0.5 studs`. Touching the pendulum by itself does **not** mean blocked.

| Requested launch phase | R5 blocked | R6 blocked | R5/R6 actual phase | R5/R6 observed pendulum angle |
|---|---|---|---|---|
| 3.17 s | yes | no | 3.16 / 3.18 s | −10.65 / −10.56° |
| 3.33 s | yes | no | 3.35 / 3.34 s | −9.50 / −9.41° |
| 3.50 s | yes | no | 3.51 / 3.51 s | −7.54 / −7.61° |
| 3.83 s | no | yes | 3.84 / 3.84 s | −2.44 / −2.68° |

Every row above touched the pendulum in both runs. Three shots crossed in R6 that did not cross in R5; one changed the other way. Thus 10 − 3 + 1 = 8. The extra touch-only difference at phase 1.83 did not change either block count.

## Cause and limits of the evidence

`GolfTest.luau`'s historic `blockrate` scenario waits on Heartbeat using `(GetServerTimeNow() - lag) % period`, accepts a −5/+20 ms window, and records the launch phase and angle rounded to two decimals. `holeLag` averages five position-derived lag estimates once and caches the result for the entire run (Round 6 lasted ~260 s). Each lag estimate fits one observed pose, without velocity information, so near a pendulum turning point the inverse phase estimate can be ambiguous. The observed lag differs by 6 ms between R5 and R6. The recorded pose also differs even when rounded launch phases match.

`Movers.luau` drives a server-owned physical hinge toward an absolute-server-time sinusoid using a feedback motor in PreSimulation. The ball is client-owned physics. The historic setup therefore does not guarantee identical contact phase, network interpolation or physics substep state across sessions. A small difference at a grazing contact can produce a different path and flip the coarse crossing boolean. The saved data directly establishes contact/crossing sensitivity plus timing/pose mismatch; it does **not** isolate the precise contribution of network timing versus contact solver integration. Calling this a proven geometry or restitution regression would exceed the evidence.

No pendulum width, period or physics change is justified by these logs. All five runs stopped normally with zero flags. Tuning the rate into a difficulty target belongs to Playtest Bot / Game Art Bot and is excluded by Chase's scope cut. If they resume rate measurement later, they should log unrounded launch/contact poses, velocity, time and lag per shot and distinguish touch/crossing counts. Stage s random-shot sweeps are robustness checks and must report their own seeds, resets, stuck/escape/console results; any random contact rate has a different sampling distribution and must not be presented as a repeat of the old aimed block-rate percentage.

## Reproduction

Run `python3 tools/analyze_h9_history.py` to regenerate `h9-historical-analysis.json`. It only reads saved files and fires zero shots. Sources are `playtests/round4/blockrate`, `playtests/round5/blockrate-h9`, `playtests/round6/blockrate-h9`, `playtests/stage-p/blockrate`, and `playtests/stage-q/blockrate` (`results.json` and raw `blockrate.jsonl`).

## Stage s fresh repeats, same build, back-to-back (Claude Code, 2026-10-11 ~21:40 PT)

Three identical `blockrate` runs (`run blockrate --no-vr --opts '{"blockShots":24,"blockHoles":"9"}'`), with no code or data changes between them:

| Run | Blocked | Touched | Cached lag | Flags |
|---|---:|---:|---:|---:|
| run1 | 10/24 (41.7%) | 16/24 | 0.168 s | 0 (24 rest) |
| run2 | 9/24 (37.5%) | 14/24 | 0.170 s | 0 (24 rest) |
| run3 | 9/24 (37.5%) | 16/24 | 0.171 s | 0 (24 rest) |

Mean 38.9%, spread ±1 shot. The identical build swings between 37.5% and 41.7% from run to run. The R4 to R6 33.3% vs 41.7% gap (±2 shots out of 24) is therefore within measurement noise: grazing pendulum contacts flip with ~ms launch-phase/lag error between the client-owned ball and the server-driven hinge. It is not a game regression. There is no gameplay stabilisation to do, and the scope cut rules out difficulty tuning. Random 20-shot sweeps (seeds 119, 120, 121) are reported separately: 0 stuck, 0 escapes, 0 console errors. Evidence: `blockrate-h9-run{1,2,3}/`.
