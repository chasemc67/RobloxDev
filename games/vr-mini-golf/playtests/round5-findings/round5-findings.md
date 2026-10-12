# VR Mini Golf, round 5 playtest (v153, commit ba87d86), Playtest Bot
2026-10-11, about 17:05–18:45 PT. Claude Code (Opus 5.5) on the Mac Mini ran the checks through the Studio MCP until it hit its session limit. I finished the random-shot sweep, the lantern count and the personal-best review myself, using light runner and MCP calls. Place 87725688219952.
Read-only: nothing was saved or published, nothing in `src/` changed (`git status src` is empty), and no agreement pop-ups appeared. Studio is in Edit mode with the workspace attributes it started with (`SimulateVR=false, GolfTestMode=false, SavedAtm=0.32`, recorded in `attrs_start.json`). Every scripted change happened inside Play sessions that were then stopped.

## Summary
| # | Check | Result | vs round 4 |
|---|---|---|---|
| 1 | VR menus: laser from both hands, hover, trigger | **PASS (34/36 steps).** Every title, course picker, Settings (all 8 controls), How to play, results, Play again, Back to menu and scorecard button hovered and clicked with both the left and right laser. Hover glow wraps the button and the beam shows on hover. The panel stays at (192.5, 29.1, 170) facing −X on every page across all sessions: **0 studs of movement, 0° of turn.** The VR hint now reads "Point with either controller, pull the trigger to click", with no thumbstick hint. The 2 failed steps (Resume and WristMenu, steps 27–28) were the script's mistake: it tried them while only the title panel was open. | R4: panel jumped left/right between pages and buttons were driven by a debug hook. **Fixed** |
| 2a | Wrist trigger: false shows and misses | **PASS. 0 false shows and 0 misses** over 350 scripted segments (right-handed 176, left-handed 174: 279 that should stay hidden, 47 that should show). wrist_sim (seeds 8–11: glance, swings, stance/putt lineup, 25 s of looking around, watch) also had 0 false shows and every watch showed. Delay from look to show: 264–283 ms in wrist_sim, mean 320–338 ms (max 817) in the sequences. Glances of 0.25 s or less never showed, and 0.28 s glances showed. Hidden during play, swings and putt lineup in every case. | new |
| 2b | Card layout and values | **PASS.** Same layout as `store/ui/wrist/wrist_mock.png` (hole and name row, Par/Stroke/Total/Best grid with icons), plus a MENU/SCORES strip under it. Not stretched: the part's aspect matches its canvas (1.306). Upright (roll ±2.2°), not mirrored, facing the eye 0°, on either wrist. Values were correct after each of 9 real strokes across H1–H3 (hole, name, par, stroke, total vs par). Best showed −2 after a 25 on the in-memory best. See `wrist/c2_sbs_*.png` | new |
| 2c | Wrist MENU / SCORES buttons | **FAIL (P2).** Both work at first: MENU opens the title page and SCORES opens the scorecard, which Close shuts. **After MENU → Resume, SCORES stops taking the pointer (no hover, nothing opens). This happened 3 of 3 times** (`wrist/scores-repro/`). After switching hands in Settings, the right-wrist MENU also wouldn't hover, probably the same bug. Separately, after the hand swap the right-wrist card showed Best "−" while the left had shown "−2". This needs another look. | new |
| 3 | Camera wall probe, flat + VR head (483 round-3 spots) | **PASS. Flat 0/5796 bad poses, VR 0/11592.** Flat min distance 6.00, max fill 0.20. VR max fill 0.31 (limit 0.4). Blockers fade in VR: 3.9 parts per pose on average, max 27 | R4: flat only, 0/5796, max fill 0.31. VR fade **now confirmed** |
| 3b | Round-4 polish items | H9 pendulum near the lens: its glow parts are now hidden (LTM 1) at 0.8 and 1.5 studs, so the yellow wash is fixed. H6 tee sign: its occluders fade (10/10). Hollow-tree shell: the H8/H9 fade cases now fade 0–3 parts instead of 39–56. **Improved** | R4 polish 1 and 2 |
| 4 | Ball and putter-head outline through occluders | **PASS in flat at every spot. VR passes at the H9 trunk tunnel, H3 mushroom house, H5 covered bridge, H8 and H9 hollow tree, and H1 rail. H6 mill wheel in VR is flaky (P3):** over 40 time samples it was blocked in 19, but the outline was missing in 16 ball-or-club cases and showed in 8 cases with nothing in the way. It looks like the outline lags behind the spokes (`polish/polish.json`). A live check on the wheel agreed 59/60 for the ball. | R4: not tested |
| 5 | H9 pendulum (±11°, 1.0 plinth), 24 aimed shots | **PASS. 10/24 = 41.7% blocked** (14 touched), 0 traps, 0 stuck, all 24 came to rest normally. Period 4 s, client lag 0.17 s | R4: 8/24 = 33.3% |
| 6a | H7 / H8 block rate (12 shots each) | **H7 6/12 = 50.0%** (touched 6), **H8 6/12 = 50.0%** (touched 6). Both PASS, at the top edge again. The 6 flags on H8 are firefly-ring teleports, which are normal | R4: 50% / 50% |
| 6b | Club in both hands (clubviz) | **PASS.** Same as R4: the shaft leaves the top, 0° off the mount axis, head 0.011 above the plane, both hands | same |
| 6c | Slope arrows | **PASS** (needs a quick look from Game Art Bot). All 17 slopes now use a one-sided chevron, and in every screenshot taken looking downhill it points away from the camera, which is downhill (`slopes/contact.png`). On the 45° banks the direction is hard to read | R4: symmetric zigzag, **fixed** |
| 6d | Lights | 212 props, **178 lit (84%)**. Unlit are the same backdrop pieces: 24 sky_lantern, 8 mere_lantern_boat, old_lantern_tower, lantern_falls_curtain. (The 230 raw count includes tee-sign cap and paper sub-parts, which are lit through their sign.) | same |
| 6e | Personal best | Logic PASS in Studio: kept in memory, Best_lantern_grove=25 got onto the card, writes use UpdateAsync with pcall, settings are clamped. **Live save NOT tested:** it needs a live server or `PBInStudio` plus Studio API access, and I didn't enable either | same |
| 6f | Title background and card | **PASS.** The new painted dusk background, the logo and the Lantern Grove card render on desktop, phone and in VR | new art |
| 6g | Smoke tests | Desktop **PASS** and iPhone 17 Pro **PASS** (stroke, Explore, back; 0 errors). SimulateVR: ledge snap PASS (3/3), club ghosting PASS. **FAIL in 2 VR cases, which need triage (P2):** in the `progress` run, H2 wasn't sunk (ball left 85.7 studs from the next tee), and in the `ghost` run the simulated VR swing through the ball gave **hit=no**, with the ball at 1.82 studs/s against an expected 6.80. Both could be the test harness. Round 4 didn't run them | new |
| 6h | Random-shot sweep (20 per hole × 9) | **PASS.** 180 shots, 0 escapes, 0 stuck, 0 nudges. 4 balls went into hazards, which is expected (2 on H5 water, 2 on H7) | R4: not run (R3/R4 dev sweeps were clean) |
| – | Console | 0 server or client errors or warnings in every run | same |

## Owners
- **RobloxDevBot**
  - (P2) Wrist SCORES dead after MENU → Resume, 3/3 repro. Also check the right-wrist MENU after a hand swap and Best showing "−" on the right wrist.
  - (P2) Triage the VR smoke failures: `progress` H2 not sunk, and the `ghost` VR swing not registering a hit (1.82 vs 6.80 studs/s). Real bug or harness?
  - (P3) H6 mill-wheel outline in VR lags behind the spokes.
  - (P3) H7 and H8 are still exactly at 50%, the top edge of the target.
- **Game Art Bot**
  - Confirm the chevrons read downhill on the 45° banks (H3, H8, H9).
  - Approve the extra MENU/SCORES strip under the card (spec is 1024×640, the in-game canvas is 1024×784).
- **Audio owner / a human:** nothing has been listened to yet.
- **MacBot:** nothing. Note that Claude Code on the Mini hit its usage limit ("resets 7pm PT") partway through the round.

## Files
`vr-menu/` (34 shots + log), `wrist/` (card shots, side-by-sides with the mock, `scores-repro/`), `wrist-sim/`, `camprobe/summary.md` and `camprobe_r5.json`, `xray/` (flat and VR per spot), `polish/`, `blockrate-h9/`, `blockrate-h7h8/`, `clubviz/`, `slopes/`, `ui/`, `ui-phone/`, `vr-smoke/`, `sweep/`, `sweep-b/`, `scripts/` (round 5 scripts), `*.log`.

## Not tested
- A real headset: laser feel and accuracy, card legibility, how the wrist trigger feels on a real arm, comfort. VR was SimulateVR only.
- Audio: nobody listened, and there's still no loopback device on the Mini.
- A real phone (emulator profile only).
- Saving the personal best on a live server or in DataStore (Studio API access off, not enabled).
- A counted 9-hole round played by hand in VR (the `progress` run uses server sinks).
- Multiplayer.
