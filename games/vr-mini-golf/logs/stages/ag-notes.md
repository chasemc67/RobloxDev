# Stage ag — shared fixes and local verification

Result: **PARTIAL**. All requested builds and checks completed; H4 has **1/20** shots moving above StopSpeed after 15 seconds. That shot rested at 18.065 s without a timeout or wedge. No publication, cloud-place open/save, new Roblox place, asset upload, or git push.

## Preflight and local files

Read game AGENTS.md, af/ac2/ad notes and both ag-input Playtest Bot reports before changes. No competing stage job matched the requested process check. Launched Studio and visually confirmed **Welcome, MetavrseBuilder**. Each file was the only open place, in Edit with PlaceId/GameId 0 and no NetworkClient before edits. Studio may retain the prior filename in MCP after Save As; native window titles and save confirmations verified the paths.

- Aurora: opened `playtest-aurora-v2.rbxl`; Save to File As `playtest/playtest-aurora-v3.rbxl`.
- Sugarloaf: opened and saved existing `playtest/playtest-sc-batch34.rbxl`.
- Lobby: opened `playtest-lobby-ad.rbxl`; Save to File As `playtest/playtest-lobby-ae2.rbxl`.

Closed each place before the next. All 50 `src/**/*.luau` sources matched in each final Edit model. Original Aurora v2 and lobby ad file hashes are unchanged. Input/output hashes and sizes are in `input-files.json` and `output-files.json`. No protected place 135374506016678 was touched. Binary files and screenshots are not committed.

## Shared fixes

- **H17:** CourseBuilder resolves the toggle mover's `felt_ids` into ObjectValue references to the generated GolfSurface parts. MoverMath reads period, phase_s and the half-open solid_window; Movers switches CanCollide, CanQuery and CanTouch together every PreSimulation. No StaticReason fallback or per-place geometry patch. The bridge felt remains in its generated Geometry folder so course queries still find it. Absolute cycle boundaries avoid modulo roundoff at repeated exact boundaries (e.g. 9.6 s).
- **Ice:** generated static felt, cup surface and mover felt carry `decel_scale`. BallController reads the supporting raycast part each frame; it scales RollDecel, RollDrag, and the rest/slope threshold. Config constants are unchanged. The existing nonnegative EngineRollLoss compensation is retained. Converter already preserves arbitrary felt fields: regenerated Aurora data and explicitly verified H4 ice=0.35 in both converted data and live client felt. Regeneration produced no data diff.
- **Scorecard:** minimum desired width 360, reduced title bounds reserve Close/gear width, and the header/grid spacing accommodates the 56 px VR Close target. Desktop retains its 36 px target. Title is named for bounds checks.
- **Harness:** complete per-shot rows, time-to-rest and first sample at/after 15 s; deterministic biased shots aimed near [182.9,84.1,460.9]. Source changes were pushed to all three local files.

An initial Edit rebuild exposed a cup attribute typo and stopped before completion; it was corrected, the preserved blockout restored, and the full data build rerun successfully. An exact-boundary unit probe also exposed modulo roundoff; final boundary tests pass. These development probes are not counted as final Play failures. All completed Play validations had zero warnings/errors.

## Aurora H17 timing and shots

Spec: **period 9 s, phase 0, solid [0.6,6.6)**; off [0,0.6) and [6.6,9). Final native-server observation: **401 samples spanning 19.999592 s (>2 periods), zero state/flag mismatches**. Sampling requested 0.04 s; actual interval about 0.05 s. Observed transition brackets in cycle phase:

| Edge | Last prior state (s) | First new state (s) | Spec (s) |
|---|---:|---:|---:|
| OFF 1 | 6.594011 | 6.643317 | 6.6 |
| ON 1 | 0.592875 | 0.642698 | 0.6 |
| OFF 2 | 6.592858 | 6.642840 | 6.6 |
| ON 2 | 0.592800 | 0.642635 | 0.6 |

On duration approximately 6.0001 s; off duration approximately 2.9998 s. These are sampled bounds, not claims of zero replication latency. Final boundary probes check 0/0.599999/0.6/6.599999/6.6/8.999999/9/9.6/15.6/18.6.

H17: **cupdrop 3/3; random 8/8; slow rollers 6/6**. No stuck, timeout, nudge or escape flags. Three authored hazard returns (1 random, 2 slow); native falls and subsequent placements are in raw telemetry. The bridge no longer leaves the ball supported during the off window.

## Aurora H4 — per-shot rest and 15 s flags

Seed 20261012. Eight existing random felt/tee fuzz shots (20–100% power), plus twelve starts 2–6 studs before the reported spot, aimed with ±0.4 stud jitter at 1.5–5 studs/s through the real Ball.hit path. This is a focused regression sweep, not a replay of Playtest Bot's entire 90-shot distribution. Cupdrop **3/3** in the focused pass and **3/3** in the all-hole pass.

`Time to rest` is the native rest outcome time, not the first below-StopSpeed sample (which can occur at an uphill turnaround). All 20 shots rested; no timeout resets, forced-rest/wedged, offsurface or stuck flags. **FLAG h4-biased-5:** speed **1.485568** at **15.015312 s**, position [181.082,84.080,462.598]; rested at **18.065 s**. The strict 15-second criterion therefore remains unmet, even though this was moving travel rather than permanent entrapment. No physics/layout tuning beyond the requested decel_scale implementation was applied.

| Shot | Time to rest (s) | Outcome | Speed at 15 s | Moving at 15 s | Flags |
|---|---:|---|---:|---|---|
| h4-fuzz-1 | 11.933 | rest | ended earlier | False | — |
| h4-fuzz-2 | 4.533 | rest | ended earlier | False | — |
| h4-fuzz-3 | 6.466 | rest | ended earlier | False | — |
| h4-fuzz-4 | 11.549 | rest | ended earlier | False | — |
| h4-fuzz-5 | 3.867 | rest | ended earlier | False | — |
| h4-fuzz-6 | 4.249 | rest | ended earlier | False | — |
| h4-fuzz-7 | 5.166 | rest | ended earlier | False | — |
| h4-fuzz-8 | 4.183 | rest | ended earlier | False | — |
| h4-biased-1 | 9.133 | rest | ended earlier | False | — |
| h4-biased-2 | 3.699 | rest | ended earlier | False | — |
| h4-biased-3 | 14.516 | rest | ended earlier | False | — |
| h4-biased-4 | 9.082 | rest | ended earlier | False | — |
| h4-biased-5 | 18.065 | rest | 1.4855680465698242 | True | — |
| h4-biased-6 | 9.783 | rest | ended earlier | False | — |
| h4-biased-7 | 14.599 | rest | ended earlier | False | — |
| h4-biased-8 | 7.582 | rest | ended earlier | False | — |
| h4-biased-9 | 13.55 | rest | ended earlier | False | — |
| h4-biased-10 | 3.165 | rest | ended earlier | False | — |
| h4-biased-11 | 12.865 | rest | ended earlier | False | — |
| h4-biased-12 | 14.165 | rest | ended earlier | False | — |

## Aurora per-hole cupdrops

| Hole | Sunk/attempted | Random | Biased | Slow |
|---|---|---:|---:|---:|
| 1 | 3/3 | — | — | — |
| 2 | 3/3 | — | — | — |
| 3 | 3/3 | — | — | — |
| 4 | 3/3 | 8 | 12 | — |
| 5 | 3/3 | — | — | — |
| 6 | 3/3 | — | — | — |
| 7 | 3/3 | — | — | — |
| 8 | 3/3 | — | — | — |
| 9 | 3/3 | — | — | — |
| 10 | 3/3 | — | — | — |
| 11 | 3/3 | — | — | — |
| 12 | 3/3 | — | — | — |
| 13 | 3/3 | — | — | — |
| 14 | 3/3 | — | — | — |
| 15 | 3/3 | — | — | — |
| 16 | 3/3 | — | — | — |
| 17 | 3/3 | 8 | — | 6 |
| 18 | 3/3 | — | — | — |

All-hole total **54/54**, including the focused H17 cups. The additional focused H4 3/3 are excluded from that total. Final client/server logs: zero warnings/errors. Course rebuilt from regenerated Aurora data, with existing blockout preserved and no import.

## Sugarloaf batch34

Shared sources pushed; H11 geometry and its corrected schedule were retained. Native Play gate Y relative to closed pivot:

| Requested phase | Sample phase | Gate offset |
|---|---:|---:|
| 2 s | 2.032404 | -1.30003357 |
| 8 s | 7.981950 | 0.00003052 |
| 10.3 s | 10.315284 | 0.00003052 |

H4/H11/H15 cupdrops **3/3 each (9/9)**, zero console warnings/errors. This quick smoke does not resolve the prior af H15 dune-seam stuck finding; that broader sweep was not rerun.

## Lobby bounds and desktop smoke

SimulateVR=true: both ButtonB and ButtonY opened and closed the scorecard. Both yielded identical canvas bounds:

| Element | X | Y | Width | Height |
|---|---:|---:|---:|---:|
| title | 164 | 174 | 230 | 44 |
| close | 402 | 182 | 56 | 56 |
| gear | 466 | 150 | 64 | 64 |

Pairwise Title/Close, Title/gear and Close/gear intersection area **0**. Inspected `lobby-ButtonB.png` and `lobby-wrist.png`; B/Y screenshots are retained locally. Wrist: LeftHand, shown=true, alpha=1, faceDeg=0, LOBBY / VR Mini Golf, dash statistics. This was simulated VR, not headset comfort/readability acceptance.

Desktop zero-hole fixture used the real desktop HUD in Aurora Play, temporarily setting only the local course attribute to a folder absent there; restored before Stop. Actual desktop lobby intentionally uses LobbyRoam and does not instantiate this scorecard. Desktop header bounds:

| Element | X | Y | Width | Height |
|---|---:|---:|---:|---:|
| title | 281.165 | 149.316 | 200.806 | 35.342 |
| close | 488.397 | 155.742 | 28.916 | 28.916 |
| gear | 523.739 | 130.039 | 51.406 | 51.406 |

All desktop pairwise overlaps **0**. Screenshot inspected; the prior hole-in-one announcer is visible above the fixture but does not obscure its Title/Close/gear layout. Native lobby `python3 tools/run_playtests.py smoke` passes menu walk/open/close, course cards and local skipped teleport loading, portal requests, leaderboard, and zero console warnings/errors. No actual cloud place traversal occurred. Final SimulateVR=false and GolfTestMode=false; saved locally and Studio closed.

## Evidence and limits

Evidence root: `playtests/stage-ag/`. `aurora-final/results.json`, `h4/results.json`, `h4-shots.md`, native `.jsonl` telemetry, H17 sample/boundary JSON, H11 timing/offset JSON, lobby/desktop bounds and smoke logs, all-source equality checks, file hashes and shutdown checks. Screenshots are local-only. Config physics constants, source holes.json and imported meshes were not changed. Native engine friction/contact behavior can still differ from the designer simulator; this pass implements its authored surface factor and reports the observed remaining >15 s motion honestly.

All requested local artifacts are ready. **PARTIAL** is due solely to H4_CRAWL15=1/20 in this stage, not missing work. No push or publication.
