# Sugarloaf Canyon: Playtest Log

Simulator: `tools/sim.py` (copied from Lantern Grove, physics unchanged). It validates geometry, fuzzes escapes (60k random shots per hole),
brute-forces an ace-line search from the tee, and plays 2000 AI rounds per hole per skill. Physics tests: `tools/test_physics.py`.
Timing obstacles: `tools/timing_check.py` (24 phases per cycle, stop/kick split, 100k-shot soft-lock fuzz). Teleports and the lift:
`tools/teleport_check.py`. Per-round geometry snapshots are in `tools/out/holes-<tag>.json` and raw results in `tools/out/sim-<tag>.json`
(`tools/summarize.py <tag>` prints the tables below and a per-hole target check).

**Physics (the builder's real Roblox values, measured for Lantern Grove; constants in `sim.py` and the `physics` block of `holes.json`):**
1 stud = 0.3 m. g = 32.7 studs/s². Rolling deceleration = 0.5 + 0.25·v studs/s². Rail restitution 0.63, bumper restitution 0.65 (static
bumpers and every moving blocker). Cup radius 0.5 stud, capture speed < 5.33 studs/s (1.6 m/s). Max putt 19.78 studs/s (5.9 m/s) = a
60-stud roll on flat felt. Drops keep 80% of horizontal speed. Pendulum height rule: a swing blocker only stops the ball if its lowest point
over the ball is at or below the ball's centre.

**AI golfers (fixed, same model as Lantern Grove's final rounds).** Per stroke the golfer aims at the furthest target it has line of sight to:
the cup, else the hole's `ai_waypoints` for its current zone. It hits for distance + carry, adding √(2gΔh) for climbs. Gaussian noise:
**good** aim σ 1.0°, power σ 5%, and on 30% of tee shots it goes for the hole's brute-force ace line (most robust grid hit) with line-memory
error ±1.5° / ±8%; **average** aim σ 2.5°, power σ 12%, never goes for aces. The cap is 8 strokes. A hazard costs +1 and resets the ball to
the stroke start, or to the hazard's `respawn` point when it has one. The golfer model was not changed or tuned per hole in any round below;
only the course geometry and the waypoints (where a golfer of that skill would aim) were.

**Flags.** BROKEN = validator error, fuzz/AI escape, or the cup never reached. IMPOSSIBLE = good players capped >50%.
TRIVIAL = HIO >15% or avg < par−1. TOO-HARD = good avg > par+2. WARN:no-HIO-line = the brute-force search found no ace.

**Targets (Lantern Grove's final bands, from the start):**
- good HIO 0.2–10%, with a brute-force ace line on every hole;
- good average within par − 0.7 … par + 1;
- skill gap (average − good) ≥ 0.3;
- average ≤ par + 1.5;
- stroke-cap hits ≤ 1% for both skills;
- validator 0 errors, fuzz 0 escapes, 0 AI escapes, 0 timeouts;
- timing obstacles: the intended line blocked on 25–50% of phases **judged by stops** (Studio estimate = stops + 0.36 kicks, Lantern Grove's
  Round 10 calibration), 0 traps, 0 soft-locks in a 100k-shot fuzz;
- every cup has a flag, and the tee→flag sightline is clear or the hole has a stated visual cue;
- route choices have signs and felt arrows; one-way slopes and drops have felt arrows or chevrons; rail-less crossings respawn at the entry.

Total par 54 (front 26, back 28), as in `course.md`.

## Round 0: tools and sim changes (before any tuning)

| Change | Why |
|---|---|
| `tools/build_holes.py` (adapted from Lantern Grove): all 18 holes, `K()` tuning knobs, `SC_VARIANT` / `SC_OUT` sweep hooks. `world_offset` / `world_yaw` are read from `world/world.json` placements. At the end it checks every felt and wall corner against the hole's `concept.pads` and prints any point outside | Placement and footprint stay consistent with the world layout |
| `geom.py`: `offset_polyline` (mitred channel rails), `octagon_pts`, `bank_wall(ext_bank, ext_back)`, `teleport(half_size, kind, ...)` | H5 half-pipe, H17 round dial, banks near footprint edges, H11 lift |
| `sim.py`: teleports may use a **rectangular trigger** `entry.half_size` (hole-local axes). Physics unchanged | H11 lock chamber: the whole chamber floor is the lift platform |
| `timing_check.py`: `OBSTACLES` filled in for H6, H9, H11, H14 and H17. Every blocked shot is classified as a **stop** (the first contact's velocity change is mostly along the line of travel, \|cos\| ≥ 0.7: a face square to the line) or a **kick** (side face or corner). The table reports the Studio estimate stops + 0.36 kicks | Lantern Grove Round 10: the engine mostly shoves kicked balls on through, so obstacles are judged by stops |
| `tools/sweep.py` = Lantern Grove `sweep_r5.py` + `sweep_r7.py` + the stop/kick split: per variant the validator, fuzz, ace search, 2000 plays per skill and (`--timing`) the timing check. Each process writes its own scratch file | Iteration tooling (one shared scratch file once corrupted a parallel batch at Lantern Grove) |
| `summarize.py`: adds skill gap, par-or-better rates, escapes/timeouts and a per-hole target check | Reporting |
| `render_layout.py`: course map drawn over the hill-shaded canyon heightfield with the world.json walkways, lifts and gondola; H5's base plate drawn as rock with the channel as felt | 18 holes spread over 1280 studs |
| `test_physics.py`: unchanged, 13/13 pass | - |

## Round 1: first build of all 18 holes (`p1`)

Snapshot `tools/out/holes-p1.json`, results `sim-p1.json`. Every hole implements its `course.md` gimmick inside its `world.json` concept
pads (fit check: 0 points outside after inset corner banks on H2, H6, H12). Validator: 0 errors after two fixes found while building
(H17's dial was first a union of two squares, a star, not an octagon: now a square plus four invisible corner-rock blocks; H5's rock wall
was lower than the banks beside it).

| # | Hole | Par | Good avg | Good HIO | Good ≤par | Good capped | Avg avg | Avg HIO | Avg ≤par | Avg capped | Gap | Haz/play (avg) | Escapes / timeouts | HIO-search hits | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Trailhead Gate | 2 | 1.95 | 6.6% | 99% | 0.0% | 2.38 | 0.0% | 67% | 0.0% | +0.43 | 0.00 | 0 / 0 | 35/34560 | ok |
| 2 | Mine-Cart Junction | 3 | 3.18 | 0.0% | 82% | 0.0% | 5.42 | 0.0% | 20% | 16.1% | +2.24 | 0.00 | 29 / 0 | refine 0/10920 | BROKEN:geometry, WARN:no-HIO-line |
| 3 | Ranger's Riverbend | 3 | 2.60 | 0.1% | 76% | 0.0% | 3.72 | 0.0% | 40% | 0.0% | +1.12 | 0.00 | 0 / 0 | refine 0/10920 | WARN:no-HIO-line |
| 4 | Crystal Corridor | 2 | 4.88 | 10.7% | 39% | 40.6% | 4.54 | 0.0% | 20% | 19.3% | -0.34 | 0.00 | 0 / 0 | 81/34560 | TOO-HARD:good>par+2 |
| 5 | Echo Slot | 3 | 7.41 | 0.0% | 0% | 68.7% | 7.38 | 0.0% | 0% | 69.1% | -0.03 | 0.00 | 0 / 93 | refine 0/10920 | IMPOSSIBLE, TOO-HARD:good>par+2, WARN:no-HIO-line, WARN:timeouts |
| 6 | Flash Flood | 3 | 2.85 | 4.9% | 76% | 0.4% | 4.96 | 0.0% | 53% | 45.1% | +2.11 | 0.00 | 7 / 0 | 215/276480 | BROKEN:geometry |
| 7 | Rope Bridge Run | 4 | 3.58 | 0.0% | 84% | 3.8% | 4.14 | 0.0% | 69% | 1.9% | +0.55 | 0.16 | 0 / 0 | refine 0/10920 | WARN:no-HIO-line |
| 8 | Gumdrop Gulch | 3 | 1.65 | 35.7% | 100% | 0.0% | 1.95 | 19.1% | 99% | 0.0% | +0.30 | 0.00 | 0 / 0 | 98/34560 | TRIVIAL:good-HIO>15%, TRIVIAL:good-avg<par-1, TRIVIAL:average-HIO>15%, TRIVIAL:average-avg<par-1 |
| 9 | Lollipop Windmill | 3 | 2.29 | 7.4% | 92% | 0.0% | 4.30 | 0.0% | 26% | 0.0% | +2.01 | 0.00 | 0 / 0 | 277/276480 | ok |
| 10 | Sluice Chute | 2 | 1.90 | 11.7% | 98% | 0.0% | 2.38 | 0.0% | 66% | 0.0% | +0.48 | 0.00 | 0 / 0 | 127/34560 | ok |
| 11 | Floodgate Lock | 3 | 3.43 | 0.0% | 63% | 1.8% | 4.13 | 0.0% | 42% | 2.8% | +0.70 | 0.00 | 27 / 0 | refine 0/10920 | BROKEN:geometry, WARN:no-HIO-line |
| 12 | Intake Tower | 4 | 3.14 | 5.8% | 81% | 0.2% | 7.87 | 0.0% | 1% | 95.5% | +4.73 | 1.66 | 50 / 0 | 30/34560 | BROKEN:geometry |
| 13 | Hoodoo Maze | 3 | 4.73 | 4.8% | 39% | 15.4% | 4.71 | 0.0% | 36% | 14.0% | -0.02 | 0.00 | 0 / 0 | 25/34560 | ok |
| 14 | Ore Bucket Swing | 3 | 6.17 | 10.3% | 29% | 71.2% | 2.34 | 6.7% | 93% | 0.0% | -3.84 | 0.00 | 0 / 0 | 1562/276480 | IMPOSSIBLE, TOO-HARD:good>par+2 |
| 15 | Sugar Dune | 4 | 7.62 | 0.0% | 2% | 81.1% | 6.34 | 0.0% | 22% | 38.4% | -1.29 | 0.00 | 0 / 0 | refine 0/10920 | IMPOSSIBLE, TOO-HARD:good>par+2, WARN:no-HIO-line |
| 16 | Sinkhole Drop | 2 | 1.93 | 10.3% | 96% | 0.0% | 2.51 | 0.1% | 54% | 0.0% | +0.58 | 0.00 | 0 / 0 | 202/34560 | ok |
| 17 | Sundial | 3 | 2.34 | 3.1% | 92% | 0.2% | 2.89 | 0.4% | 79% | 0.1% | +0.56 | 0.00 | 0 / 0 | 210/276480 | ok |
| 18 | Sunset Arch | 4 | 6.38 | 0.0% | 15% | 28.2% | 6.53 | 0.0% | 6% | 22.4% | +0.15 | 0.00 | 29 / 0 | refine 0/10920 | BROKEN:geometry, TOO-HARD:good>par+2, WARN:no-HIO-line |
| | **Total** | **54** | **68.06** | | | | **78.49** | | | | | | | | |

**Problems found:**
- **Escapes (BROKEN) on H2, H6, H11, H12, H18:** every one is a ball riding up a 1.2-tall corner bank and hopping a 1.0-tall rail where the bank's
  backing ends. Lantern Grove met the same thing and used 2.4-tall invisible rail colliders beside banks.
- **The AI got stuck on most new holes (caps 14-95%)** because zone waypoints pointed at spots *inside* their own zone (H12 shoreline, H13, H14,
  H15, H18, H6 overflow): once the ball reached the point it kept tapping it there. On H4 the planner had one waypoint in the middle of the
  slot and fired back at it from beyond.
- **H5 half-pipe: 69% capped and 93 timeouts.** The steep banks (1.0 over 2.0, 27°) turn forward speed into side-to-side rocking, and the
  speed-dependent drag kills it.
- **TRIVIAL:** H8 (good HIO 36%: the dips line up every ball straight at the cup).
- **No ace line:** H2, H3, H5, H7, H11, H15, H18. **Slightly high aces:** H4, H10, H14, H16 (10-12%).
- H1 and H17 already met every target.

## Round 2: AI waypoints, rails beside banks, H18 front end (`p2`)

| Hole | Change | Why |
|---|---|---|
| H2, H6, H11, H12, H18 | Rails beside corner banks are 2.4 tall (invisible collider; visual rail stays 1 tall) | Bank-hop escapes. All 5 now 0 escapes in 60k fuzz shots |
| H4, H5, H13, H14 | Felt split into zones along the route (`slot_a/slot_b`, `s1..s3`, `maze_s/n`, `lane/lane2`) so every waypoint leads OUT of the zone it is used from | Stuck AI (see Round 1) |
| H6, H12 | Average waypoint chains rebuilt (overflow and shoreline); the H12 corner bank was in the channel instead of the green's NW corner | Average capped 45% / 95% |
| H3, H8, H9, H10, H16 | Cup moves | Ace lines / TRIVIAL |
| H8 | Four humps instead of three, green 8 studs further on | TRIVIAL (36% good aces) |
| H11 | Cup on the lift's exit line 15 studs out; lift exit clamp max 6 -> 7 | No ace line (the exit roll could not reach the cup) |
| H15 | Crest 1.6 -> 1.0, waypoint with a climb | The AI's tee shots rolled back down the ramp every time |
| H18 | Front end rebuilt: lane -> banked NE corner -> west past a hoodoo -> banked NW corner -> ramp north. The stray plateau bank that blocked the rim lane was removed | 28% good caps |

| # | Hole | Par | Good avg | Good HIO | Good ≤par | Good capped | Avg avg | Avg HIO | Avg ≤par | Avg capped | Gap | Haz/play (avg) | Escapes / timeouts | HIO-search hits | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Trailhead Gate | 2 | 1.95 | 6.6% | 99% | 0.0% | 2.38 | 0.0% | 67% | 0.0% | +0.43 | 0.00 | 0 / 0 | 35/34560 | ok |
| 2 | Mine-Cart Junction | 3 | 3.18 | 0.0% | 82% | 0.0% | 5.42 | 0.0% | 20% | 16.1% | +2.24 | 0.00 | 0 / 0 | refine 0/10920 | WARN:no-HIO-line |
| 3 | Ranger's Riverbend | 3 | 2.74 | 9.2% | 68% | 0.0% | 3.70 | 0.0% | 42% | 0.0% | +0.96 | 0.00 | 0 / 0 | 4/34560 | ok |
| 4 | Crystal Corridor | 2 | 3.73 | 10.7% | 52% | 11.1% | 3.79 | 0.0% | 24% | 4.7% | +0.06 | 0.00 | 0 / 0 | 81/34560 | ok |
| 5 | Echo Slot | 3 | 7.64 | 0.0% | 0% | 76.8% | 7.71 | 0.0% | 0% | 74.6% | +0.06 | 0.00 | 0 / 51 | refine 0/10920 | IMPOSSIBLE, TOO-HARD:good>par+2, WARN:no-HIO-line, WARN:timeouts |
| 6 | Flash Flood | 3 | 2.85 | 4.9% | 76% | 0.4% | 4.96 | 0.0% | 53% | 45.1% | +2.11 | 0.00 | 0 / 0 | 215/276480 | ok |
| 7 | Rope Bridge Run | 4 | 3.58 | 0.0% | 84% | 3.8% | 4.14 | 0.0% | 69% | 1.9% | +0.55 | 0.16 | 0 / 0 | refine 0/10920 | WARN:no-HIO-line |
| 8 | Gumdrop Gulch | 3 | 1.68 | 34.0% | 100% | 0.0% | 2.17 | 12.3% | 95% | 0.0% | +0.49 | 0.00 | 0 / 0 | 64/34560 | TRIVIAL:good-HIO>15%, TRIVIAL:good-avg<par-1 |
| 9 | Lollipop Windmill | 3 | 2.48 | 0.0% | 94% | 0.0% | 4.42 | 0.0% | 20% | 0.1% | +1.94 | 0.00 | 0 / 0 | refine 0/10920 | WARN:no-HIO-line |
| 10 | Sluice Chute | 2 | 1.90 | 13.1% | 97% | 0.0% | 2.46 | 0.0% | 60% | 0.0% | +0.56 | 0.00 | 0 / 0 | 53/34560 | ok |
| 11 | Floodgate Lock | 3 | 3.27 | 7.5% | 64% | 1.8% | 3.98 | 0.0% | 46% | 2.5% | +0.71 | 0.00 | 0 / 0 | 745/276480 | ok |
| 12 | Intake Tower | 4 | 3.14 | 5.8% | 81% | 0.2% | 4.99 | 0.0% | 25% | 0.2% | +1.86 | 0.01 | 0 / 0 | 30/34560 | ok |
| 13 | Hoodoo Maze | 3 | 3.72 | 4.8% | 59% | 5.5% | 2.60 | 0.0% | 90% | 0.4% | -1.12 | 0.00 | 0 / 0 | 25/34560 | ok |
| 14 | Ore Bucket Swing | 3 | 1.99 | 10.3% | 100% | 0.0% | 2.34 | 6.7% | 93% | 0.0% | +0.35 | 0.00 | 0 / 0 | 1562/276480 | TRIVIAL:good-avg<par-1 |
| 15 | Sugar Dune | 4 | 8.00 | 0.0% | 0% | 99.9% | 7.51 | 0.0% | 6% | 78.4% | -0.49 | 0.00 | 0 / 0 | refine 0/10920 | IMPOSSIBLE, TOO-HARD:good>par+2, WARN:no-HIO-line |
| 16 | Sinkhole Drop | 2 | 1.99 | 12.3% | 89% | 0.0% | 2.47 | 0.1% | 58% | 0.0% | +0.48 | 0.00 | 0 / 0 | 188/34560 | ok |
| 17 | Sundial | 3 | 2.34 | 3.1% | 92% | 0.2% | 2.89 | 0.4% | 79% | 0.1% | +0.56 | 0.00 | 0 / 0 | 210/276480 | ok |
| 18 | Sunset Arch | 4 | 7.12 | 0.0% | 12% | 61.1% | 7.41 | 0.0% | 5% | 71.2% | +0.29 | 0.00 | 0 / 0 | refine 0/10920 | IMPOSSIBLE, TOO-HARD:good>par+2, WARN:no-HIO-line |
| | **Total** | **54** | **63.28** | | | | **75.34** | | | | | | | | |

**Result vs Round 1:** H1, H3 and H17 pass every target. Escapes 0 everywhere. H5 is still broken (77% capped, timeouts), H15 and H18 too.

## Round 3: sim rule for pinned balls, H5 half-pipe rebuilt (`p3`)

**Sim change (made before tuning, kept fixed afterwards).** Tracing H5's timeouts showed balls frozen in place against the raised end edge of an
overlapping bank: the cliff contact puts the ball back where it was every step while gravity re-adds speed, so the "< 0.4 studs/s" rest rule
never fires and the stroke times out. New rest rule in `sim.py`: **a ball that moved < 0.01 studs in the last 0.5 s is at rest, at any speed.**
It cannot change a Lantern Grove result (those balls always move), H5 random-shot timeouts went 84 -> 0 per 20k, and `test_physics.py` gained
test 14 (rectangular lift trigger) and test 15 (pinned ball rests): **15/15 pass**.

| Hole | Change | Why / sweep evidence (`tools/sweep.py`, 1000-2000 plays per skill) |
|---|---|---|
| H5 | Banks 2.0 wide / 1.0 rise -> **1.5 wide / 0.3 rise** (13°), channel 7 wide. At each bend the bank on the **outside** runs on to the rail mitre and the bank on the **inside stops at its low-edge mitre** | The inside bank used to run back into the previous straight as a raised ridge across the line (the "invisible bump" in the traces). Steep 1.0 / 0.6 / 0.4 rises: 50-96% capped; 0.3: 0% capped |
| H5 | S-bend compacted (54 -> 40 studs of channel), cup (-0.5, -42) | No ace line at 54 studs. Cups (0,-42): HIO 0.3%; (0,-41): 10.9%; **(-0.5,-42): good 2.62, HIO 7.3%, gap +0.71** |
| H2 | Corner bank removed, average target in the crossover, **cup (-9, -46)** on the left tunnel's exit line | Average stuck on the bank; ace closest approach 3.0. (-9,-46): good 2.47, HIO 3.9%; (-8.5,-47): HIO 9.0% |
| H4 | Two "go round crystal 5" waypoints | Good capped 11% firing into crystal 5 |
| H14 | Raised loading-dock green up a 6-stud ramp | Good 1.99 (TRIVIAL): a straight lane under the bucket was too easy |

| # | Hole | Par | Good avg | Good HIO | Good ≤par | Good capped | Avg avg | Avg HIO | Avg ≤par | Avg capped | Gap | Haz/play (avg) | Escapes / timeouts | HIO-search hits | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Trailhead Gate | 2 | 1.95 | 6.6% | 99% | 0.0% | 2.38 | 0.0% | 67% | 0.0% | +0.43 | 0.00 | 0 / 0 | 35/34560 | ok |
| 2 | Mine-Cart Junction | 3 | 3.19 | 0.0% | 80% | 0.0% | 4.17 | 0.0% | 20% | 0.0% | +0.98 | 0.00 | 0 / 0 | refine 0/10920 | WARN:no-HIO-line |
| 3 | Ranger's Riverbend | 3 | 2.74 | 9.2% | 68% | 0.0% | 3.70 | 0.0% | 42% | 0.0% | +0.96 | 0.00 | 0 / 0 | 4/34560 | ok |
| 4 | Crystal Corridor | 2 | 3.73 | 10.7% | 52% | 11.1% | 3.79 | 0.0% | 24% | 4.7% | +0.06 | 0.00 | 0 / 0 | 81/34560 | ok |
| 5 | Echo Slot | 3 | 2.62 | 7.3% | 99% | 0.0% | 3.33 | 0.0% | 67% | 0.0% | +0.71 | 0.00 | 0 / 0 | 6/34560 | ok |
| 6 | Flash Flood | 3 | 2.85 | 4.9% | 76% | 0.4% | 3.88 | 0.0% | 53% | 0.1% | +1.02 | 0.00 | 0 / 0 | 215/276480 | ok |
| 7 | Rope Bridge Run | 4 | 3.58 | 0.0% | 84% | 3.8% | 4.14 | 0.0% | 69% | 1.9% | +0.55 | 0.16 | 0 / 0 | refine 0/10920 | WARN:no-HIO-line |
| 8 | Gumdrop Gulch | 3 | 2.41 | 4.9% | 98% | 0.0% | 2.78 | 0.1% | 88% | 0.0% | +0.36 | 0.00 | 0 / 0 | 14/34560 | ok |
| 9 | Lollipop Windmill | 3 | 2.48 | 0.0% | 94% | 0.0% | 4.42 | 0.0% | 20% | 0.1% | +1.94 | 0.00 | 0 / 0 | refine 0/10920 | WARN:no-HIO-line |
| 10 | Sluice Chute | 2 | 1.91 | 13.1% | 96% | 0.0% | 2.47 | 0.0% | 59% | 0.0% | +0.56 | 0.00 | 0 / 0 | 53/34560 | ok |
| 11 | Floodgate Lock | 3 | 3.28 | 7.5% | 64% | 1.8% | 3.98 | 0.0% | 46% | 2.5% | +0.71 | 0.00 | 0 / 0 | 745/276480 | ok |
| 12 | Intake Tower | 4 | 3.14 | 5.8% | 81% | 0.2% | 4.99 | 0.0% | 25% | 0.2% | +1.86 | 0.01 | 0 / 0 | 30/34560 | ok |
| 13 | Hoodoo Maze | 3 | 3.72 | 4.8% | 59% | 5.5% | 2.60 | 0.0% | 90% | 0.4% | -1.12 | 0.00 | 0 / 0 | 25/34560 | ok |
| 14 | Ore Bucket Swing | 3 | 2.92 | 3.7% | 87% | 0.0% | 2.98 | 2.8% | 76% | 0.1% | +0.06 | 0.00 | 0 / 0 | 76/276480 | ok |
| 15 | Sugar Dune | 4 | 3.73 | 0.0% | 97% | 2.6% | 4.93 | 0.0% | 67% | 23.8% | +1.20 | 0.00 | 0 / 0 | refine 0/10920 | BROKEN:geometry, WARN:no-HIO-line |
| 16 | Sinkhole Drop | 2 | 1.99 | 12.3% | 89% | 0.0% | 2.47 | 0.1% | 58% | 0.0% | +0.48 | 0.00 | 0 / 0 | 188/34560 | ok |
| 17 | Sundial | 3 | 2.34 | 3.1% | 92% | 0.2% | 2.89 | 0.4% | 79% | 0.1% | +0.56 | 0.00 | 0 / 0 | 210/276480 | ok |
| 18 | Sunset Arch | 4 | 5.22 | 0.0% | 60% | 27.4% | 6.99 | 0.0% | 12% | 63.5% | +1.77 | 0.00 | 0 / 0 | refine 0/10920 | WARN:no-HIO-line |
| | **Total** | **54** | **53.78** | | | | **66.88** | | | | | | | | |

**Still failing after Round 3:** H4 (HIO 11%), H7 (no ace line, caps), H9 (no ace line), H10/H16 (HIO 12-13%), H11 (caps 1.8/2.5%), H12 (good 3.14 <
par−0.7), H13 (gap −1.12), H14 (gap +0.06), H15 (broken), H18 (caps). Round 4 handles them one hole at a time with sweeps.

## Round 4: one hole at a time with sweeps; H15 becomes a par 3 (`p4`)

Every change below was picked from a `tools/sweep.py` table (validator + fuzz + ace search + 1000-2000 plays per skill, `--timing` for movers).
The golfer model is unchanged. Logs: `tools/out/sw-*.txt`.

| Hole | Change | Sweep evidence |
|---|---|---|
| H4 | Cup (2.5,-36.5) -> **(4.5,-39)** | The crystals funnel near-lines into one exit: cups at (3,-37), (2,-37.5), (3.5,-36) all gave good HIO 10.7-11%; a moved crystal 5 kept 11%. (4.5,-39): **HIO 1.5%, good 2.56, gap +0.65** |
| H7 | Bridge 2 x[1,5] -> **x[1.8,5.8]**, cup **(3,-60)**, rope rail on the island's **south** edge (ends stay open to the gap) | Bridges in line (x[0.5,4.5]): good 2.64 (a par 3); offset x[2,6]: no ace line; **x[1.8,5.8]: only a ~0.3°-wide straight line threads both bridges -> ace 1.0%, good 3.60, avg 4.22**. South rail: island rebound falls 3.8% -> 0% caps |
| H8 | Cup (4.5,-46.5) -> (5,-55) after 4 humps | (4,-54): HIO 31%; **(5,-55): HIO 6.4%, good 2.38**; 3 humps: 17% capped |
| H9 | Cup **(-1.5,-42)** on the tunnel line | (-6,-45): no ace line (closest 0.88). (-2.5,-43): good 2.27; **(-1.5,-42): good 2.39, HIO 4.3%**; (-4,-46): HIO 9.8% |
| H10 | Cup **(7,-33.5)** | (6,-33): 13%; (6.5,-35) 13.8%; (7,-32) 0.2%; **(7,-33.5) 7.9%** |
| H11 | Gate pauses open/closed 4.0/3.5 s -> **5.5/2.8 s**; cup **(0,4,-43)**; lift exit **clamp(0.5·v, 1.5, 7.0)** | 4.0/3.5: caps 1.5/3.6%, gate stops 54% (above the band). 5.0/3.0: avg caps 0.9%; 5.5/2.8: caps 0.2/0.4%, stops 41.7% but HIO 10.1%; cup -43 + factor 0.5: **HIO 7.1%** (cups -43.5/-44 lose the ace: the 7.0 max exit just reaches -43) |
| H12 | Grate radius 0.45 -> **0.30** | 0.45: good 3.14 (< par−0.7); 0.35: 3.21; **0.30: good 3.35, HIO 4.5%, avg 5.01** |
| H13 | **Rebuilt as a walled maze**: foyer, three corridors (centre 4-wide with 2 staggered hoodoos, west long and safe, east scenic), cup (0.5,-51) | The open pillar field let the AI fire into pillars (caps 15%) or play it in 2.2. A par-4 version was tried (see below) and dropped. **Par 3: good 2.40, HIO 2.7%, avg 4.30, gap +1.90** |
| H14 | Hinge on the centre line, lane 8 wide, **ramp 0.8 to a raised green**, cup **(1,0.8,-44)**; good golfers take the side line clear of the bucket | Cup off-centre: the bucket blocked **0%** of the direct line (the foot rises above the ball centre within ±6° of swing). Centre: stops 33-42%. Ramp 1.0-1.5: avg caps 2.3-2.6%; 0.7: HIO 9.1%; **0.8, cup (1,-44): good 2.68, HIO 6.7%, caps 0/0.4%, stops 37.5%** |
| H15 | **Rebuilt**: the dune is one tilted plane yawed 25° off the hole axis (falls 2.4 across its width toward east-north-east: a side slope with a little downhill), the lane drops onto it and its lower edge drops onto a two-tier green that runs under it. **Par 4 -> 3**, cup **(6,-4.6,-57)** | The old crest-and-face version: AI stuck (99% capped), then good 3.0 with no ace line. Par-4 variants of the new dune: stronger slope -> good 3.63 but gap +0.11; open sugar-sand pit on the low edge -> 21-41% capped or avg caps 4%; west cups -> no ace line. **As a par 3: good 2.71, HIO 4.5%, avg 3.31, gap +0.59** |
| H16 | Cup **(1.8,-3.6,-38.5)** | (1.5,-34): 12.3%; (2,-36): 10.9%; **(1.8,-38.5): 7.5%** |
| H18 | Front end compacted (junction x[-12,4], ramp 8 long rising 0.8, plateau x[-12,-2]); hoodoo at the end of the tee lane; green bank moved to the green's far NW corner (it was across the rim-lane mouth); geode **(-9.5,0.8,-32) r 0.55**, exit min speed 3 -> **1.5** | Only 1 of 43,200 tee shots reached the geode, and its 3 studs/s exit floor left the ball 2.4 short. With min 1.5 only a fast arrival holes out, a soft plateau putt leaves a tap-in. **Good 3.45, HIO 0.6%, avg 4.50, caps 0/0.3%** |

**Par change: total 54 -> 53.** H15 plays as a par 3 under the fixed golfer model. A par-4 Hoodoo Maze (long west corridor, cup far from the
safe exit) was tried to keep 54: good 2.2-2.8 (the centre corridor is a par-3 line) and average 5.2-5.8 with 2-16% caps, so it stayed a 3.
Planned pars are design targets (`course.md`); 53 is inside the 50-56 band. `course.md`, `world/world.json` (via `build_world.py`) and
`world/README.md` are updated.

| # | Hole | Par | Good avg | Good HIO | Good ≤par | Good capped | Avg avg | Avg HIO | Avg ≤par | Avg capped | Gap | Haz/play (avg) | Escapes / timeouts | HIO-search hits | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Trailhead Gate | 2 | 1.95 | 6.6% | 99% | 0.0% | 2.38 | 0.0% | 67% | 0.0% | +0.43 | 0.00 | 0 / 0 | 35/34560 | ok |
| 2 | Mine-Cart Junction | 3 | 2.53 | 4.1% | 88% | 0.0% | 4.30 | 0.0% | 14% | 0.0% | +1.77 | 0.00 | 0 / 0 | 11/34560 | ok |
| 3 | Ranger's Riverbend | 3 | 2.74 | 9.2% | 68% | 0.0% | 3.70 | 0.0% | 42% | 0.0% | +0.96 | 0.00 | 0 / 0 | 4/34560 | ok |
| 4 | Crystal Corridor | 2 | 2.54 | 1.1% | 49% | 0.0% | 3.22 | 0.0% | 18% | 0.0% | +0.67 | 0.00 | 0 / 0 | 13/34560 | ok |
| 5 | Echo Slot | 3 | 2.62 | 7.3% | 99% | 0.0% | 3.33 | 0.0% | 67% | 0.0% | +0.71 | 0.00 | 0 / 0 | 6/34560 | ok |
| 6 | Flash Flood | 3 | 2.85 | 4.9% | 76% | 0.4% | 3.88 | 0.0% | 53% | 0.1% | +1.02 | 0.00 | 0 / 0 | 215/276480 | ok |
| 7 | Rope Bridge Run | 4 | 3.57 | 1.6% | 90% | 0.0% | 4.20 | 0.0% | 68% | 0.1% | +0.63 | 0.02 | 0 / 0 | 1/34560 | ok |
| 8 | Gumdrop Gulch | 3 | 2.41 | 4.9% | 98% | 0.0% | 2.78 | 0.1% | 88% | 0.0% | +0.36 | 0.00 | 0 / 0 | 14/34560 | ok |
| 9 | Lollipop Windmill | 3 | 2.33 | 5.4% | 92% | 0.1% | 4.20 | 0.0% | 30% | 0.0% | +1.87 | 0.00 | 0 / 0 | 242/276480 | ok |
| 10 | Sluice Chute | 2 | 1.99 | 6.6% | 95% | 0.0% | 2.53 | 0.0% | 55% | 0.0% | +0.54 | 0.00 | 0 / 0 | 12/34560 | ok |
| 11 | Floodgate Lock | 3 | 2.77 | 7.1% | 78% | 0.2% | 3.57 | 0.0% | 56% | 0.4% | +0.80 | 0.00 | 0 / 0 | 45/276480 | ok |
| 12 | Intake Tower | 4 | 3.44 | 4.0% | 74% | 0.7% | 4.99 | 0.0% | 25% | 0.2% | +1.56 | 0.01 | 0 / 0 | 30/34560 | ok |
| 13 | Hoodoo Maze | 3 | 2.35 | 2.7% | 92% | 0.1% | 4.27 | 0.0% | 21% | 0.5% | +1.92 | 0.00 | 0 / 0 | 9/34560 | ok |
| 14 | Ore Bucket Swing | 3 | 2.68 | 6.7% | 95% | 0.0% | 3.09 | 2.5% | 72% | 0.4% | +0.41 | 0.00 | 0 / 0 | 204/276480 | ok |
| 15 | Sugar Dune | 3 | 2.72 | 4.5% | 99% | 0.0% | 3.32 | 0.0% | 66% | 0.0% | +0.60 | 0.00 | 0 / 0 | 10/34560 | ok |
| 16 | Sinkhole Drop | 2 | 2.09 | 9.0% | 82% | 0.0% | 2.60 | 0.0% | 46% | 0.0% | +0.51 | 0.00 | 0 / 0 | 124/34560 | ok |
| 17 | Sundial | 3 | 2.34 | 3.1% | 92% | 0.2% | 2.89 | 0.4% | 79% | 0.1% | +0.56 | 0.00 | 0 / 0 | 210/276480 | ok |
| 18 | Sunset Arch | 4 | 3.42 | 0.9% | 83% | 0.0% | 4.46 | 0.0% | 52% | 0.8% | +1.03 | 0.00 | 0 / 0 | 5/34560 | ok |
| | **Total** | **53** | **47.35** | | | | **63.69** | | | | | | | | |

**Result:** all 18 holes meet every play target (gap ≥ 0.36, average ≤ par + 1.30, caps ≤ 0.8%, good HIO 0.85-9.2%, ace line everywhere,
0 escapes, 0 timeouts, 0 validator errors). **Timing check (`timing-p4.txt`):** 0 traps and 0 soft-locks in 100k fuzz shots on every mover, but
H9's windpump stopped only 12.5% of the timing line and H17's sundial arms 8.3% (below 25%), and H6's gate sat on the 50% edge. Round 5 fixes those.

## Round 5: timing obstacles judged by stops (`p5`)

**Timing check before (Round 4 geometry, `timing-p4.txt`, 24 phases, 100k-shot soft-lock fuzz per mover):**

| Hole | Obstacle | Line | Period | Blocked (stops + kicks) | Deflected | Blocked+deflected | Studio est. (stops + 0.36 kicks) | Passed | Traps | Timings t=0, T/3, 2T/3 | Fuzz soft-locks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H6 | sluice_gate | intended | 8.167 s | 12/24 (12 + 0) | 0/24 | 50% | **50%** | 50% | 0 | passed, passed, blocked | 0/100000 |
| H6 | sluice_gate | ace | 8.167 s | 12/24 (12 + 0) | 0/24 | 50% | **50%** | 50% | 0 | blocked, passed, blocked | - |
| H9 | windpump | intended | 12 s | 3/24 (3 + 0) | 0/24 | 12.5% | **12.5%** | 87.5% | 0 | passed, passed, passed | 0/100000 |
| H9 | windpump | ace | 12 s | 3/24 (3 + 0) | 0/24 | 12.5% | **12.5%** | 87.5% | 0 | passed, passed, passed | - |
| H11 | lock_gate | intended | 9.6 s | 10/24 (10 + 0) | 0/24 | 41.7% | **41.7%** | 58.3% | 0 | passed, blocked, passed | 0/100000 |
| H11 | lock_gate | ace | 9.6 s | 10/24 (10 + 0) | 0/24 | 41.7% | **41.7%** | 58.3% | 0 | passed, passed, blocked | - |
| H14 | ore_bucket | intended | 4 s | 9/24 (9 + 0) | 12/24 | 87.5% | **37.5%** | 12.5% | 0 | blocked, deflected, blocked | 0/100000 |
| H14 | ore_bucket | ace | 4 s | 0/24 (0 + 0) | 0/24 | 0% | **0%** | 100% | 0 | passed, passed, passed | - |
| H17 | shadow_arm | intended | 18 s | 2/24 (2 + 0) | 2/24 | 16.7% | **8.3%** | 83.3% | 0 | passed, passed, blocked | 0/100000 |
| H17 | shadow_arm | ace | 18 s | 10/24 (10 + 0) | 2/24 | 50% | **41.7%** | 50% | 0 | passed, blocked, passed | - |

| Hole | Part | Round 4 | Round 5 | Sweep evidence (stops = Studio estimate here: no kicks) |
|---|---|---|---|---|
| H6 | sluice gate | closed pause 1.5 s | **1.2 s** (open 2.0 s, 3 studs/s, cycle 7.87 s) | 1.5 s: 50% (top edge). **1.2 s: 45.8%** |
| H9 | windpump | 3 vanes 1.2 wide, 30°/s | **4 vanes 1.8 wide, 20°/s** (cycle 18 s) | 3 vanes: 12.5%; 4 vanes: 16.7%; 4 x 1.6: 22.7% (4 of the 8 blocks are kicks); 3 x 2.0 @ 24: 25%; **4 x 1.8 @ 20: 33.3%, all stops** |
| H17 | shadow arms | 2 arms 1.0-6.5, 0.6 thick, 20°/s | **2 arms 1.0-7.0, 1.2 thick, 12°/s** (cycle 30 s) | 3 arms @ 20: 12.5%; 3 @ 15: 25%; 4 @ 15: 33% but gap +0.28; arms to 7.5: 33% but the tip reaches the cup's edge; **1.0-7.0 x 1.2 @ 12: 33.3%, gap +0.63** |

Windpump vane clearance is recomputed from the vane width (corner 0.02 above the felt at the bottom of the turn). Sundial arms stay 0.9 tall
and clear the cup (arm corner reach 7.03 vs cup edge 7.5).

**Timing check after (`timing-p5.txt`):**

| Hole | Obstacle | Line | Period | Blocked (stops + kicks) | Deflected | Blocked+deflected | Studio est. (stops + 0.36 kicks) | Passed | Traps | Timings t=0, T/3, 2T/3 | Fuzz soft-locks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H6 | sluice_gate | intended | 7.867 s | 11/24 (11 + 0) | 0/24 | 45.8% | **45.8%** | 54.2% | 0 | passed, passed, blocked | 0/100000 |
| H6 | sluice_gate | ace | 7.867 s | 10/24 (10 + 0) | 1/24 | 45.8% | **41.7%** | 54.2% | 0 | blocked, passed, blocked | - |
| H9 | windpump | intended | 18 s | 8/24 (8 + 0) | 0/24 | 33.3% | **33.3%** | 66.7% | 0 | passed, passed, blocked | 0/100000 |
| H9 | windpump | ace | 18 s | 4/24 (4 + 0) | 0/24 | 16.7% | **16.7%** | 83.3% | 0 | passed, passed, passed | - |
| H11 | lock_gate | intended | 9.6 s | 10/24 (10 + 0) | 0/24 | 41.7% | **41.7%** | 58.3% | 0 | passed, blocked, passed | 0/100000 |
| H11 | lock_gate | ace | 9.6 s | 10/24 (10 + 0) | 0/24 | 41.7% | **41.7%** | 58.3% | 0 | passed, passed, blocked | - |
| H14 | ore_bucket | intended | 4 s | 9/24 (9 + 0) | 12/24 | 87.5% | **37.5%** | 12.5% | 0 | blocked, deflected, blocked | 0/100000 |
| H14 | ore_bucket | ace | 4 s | 0/24 (0 + 0) | 0/24 | 0% | **0%** | 100% | 0 | passed, passed, passed | - |
| H17 | shadow_arm | intended | 30 s | 8/24 (8 + 0) | 0/24 | 33.3% | **33.3%** | 66.7% | 0 | passed, blocked, passed | 0/100000 |
| H17 | shadow_arm | ace | 30 s | 10/24 (10 + 0) | 4/24 | 58.3% | **41.7%** | 41.7% | 0 | deflected, blocked, passed | - |

All five timing lines are inside 25-50% **judged by stops** (no sim block on any of them is a kick), with **0 traps** and **0 soft-locks in
100,000 fuzz shots per mover**. At the playtester's three timings (t = 0, T/3, 2T/3) each obstacle blocks at least once. "Ace" rows are each
hole's brute-force ace line fired at every phase (H14's ace line plays the side line clear of the bucket).

**Teleport / lift exit check (`teleport-p5.txt`):** H11 lift (exit speeds 1.5-7.0): stops 14.5 to 1.9 short, holes only at the 7.0 maximum (the
ace needs a firm entry). H12 pipe (3-7): stops 4.8 to 1.4 short below 4.8 studs/s, holes from 4.8 up; H18 geode (1.5-7): stops 5.6 to 1.6 short
below 3.9, holes above. **No exit speed carries the ball past its cup into a rail**, so no backstop is needed.

**Plays (`sim-p5.json`):** 16 holes inside every target. Two came out over the 1% cap at 2000 plays with the round's seeds, though the
1000-play sweeps had been under it: **H17 average 1.65%** (balls behind the gnomon fired at the cup through it, with no other target)
and **H18 average 2.2%** (ramp shots rolling back). Round 6 fixes both.

## Round 6: final (`p6`)

| Hole | Change | Why / evidence |
|---|---|---|
| H17 | Two "go round the gnomon" waypoints on the dial (-4.5/+4.5, -42) | Average balls behind the gnomon fired at the cup through it: caps 1.65% -> **0.4%** (2000 plays, same seeds) |
| H18 | Plateau shot power scale 1.3 -> **1.4** | Average ramp shots rolled back: caps 2.2% -> **0.3%** (ps 1.4 + rim carry 6: 0.2% but no better elsewhere) |
| H2 | Decoration only: rock face over the portals capped at y 5, headframe 1 stud east (occluders updated) | Flag sightline was blocked by those props (-9.6); now **visible, +1.2** |

Snapshot `tools/out/holes-p6.json` (= `holes-final.json` apart from the H2 decoration anchors, which have no physics), results `sim-p6.json`,
`timing-p6.json`, `teleport-p6.txt`. Physics tests 15/15 pass. Validator 0 errors on all 18 holes. World validation (iteration 7) **CLEAN**:
every holes.json felt and rail corner lies inside its world.json pads, placements equal, walkways start at the final cups.

**Timing check (`timing-p6.txt`, 24 phases, 100k-shot soft-lock fuzz per mover):**

| Hole | Obstacle | Line | Period | Blocked (stops + kicks) | Deflected | Blocked+deflected | Studio est. (stops + 0.36 kicks) | Passed | Traps | Timings t=0, T/3, 2T/3 | Fuzz soft-locks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H6 | sluice_gate | intended | 7.867 s | 11/24 (11 + 0) | 0/24 | 45.8% | **45.8%** | 54.2% | 0 | passed, passed, blocked | 0/100000 |
| H6 | sluice_gate | ace | 7.867 s | 10/24 (10 + 0) | 1/24 | 45.8% | **41.7%** | 54.2% | 0 | blocked, passed, blocked | - |
| H9 | windpump | intended | 18 s | 8/24 (8 + 0) | 0/24 | 33.3% | **33.3%** | 66.7% | 0 | passed, passed, blocked | 0/100000 |
| H9 | windpump | ace | 18 s | 4/24 (4 + 0) | 0/24 | 16.7% | **16.7%** | 83.3% | 0 | passed, passed, passed | - |
| H11 | lock_gate | intended | 9.6 s | 10/24 (10 + 0) | 0/24 | 41.7% | **41.7%** | 58.3% | 0 | passed, blocked, passed | 0/100000 |
| H11 | lock_gate | ace | 9.6 s | 10/24 (10 + 0) | 0/24 | 41.7% | **41.7%** | 58.3% | 0 | passed, passed, blocked | - |
| H14 | ore_bucket | intended | 4 s | 9/24 (9 + 0) | 12/24 | 87.5% | **37.5%** | 12.5% | 0 | blocked, deflected, blocked | 0/100000 |
| H14 | ore_bucket | ace | 4 s | 0/24 (0 + 0) | 0/24 | 0% | **0%** | 100% | 0 | passed, passed, passed | - |
| H17 | shadow_arm | intended | 30 s | 8/24 (8 + 0) | 0/24 | 33.3% | **33.3%** | 66.7% | 0 | passed, blocked, passed | 0/100000 |
| H17 | shadow_arm | ace | 30 s | 10/24 (10 + 0) | 4/24 | 58.3% | **41.7%** | 41.7% | 0 | deflected, blocked, passed | - |

### Final stats per hole (2000 plays per skill)

| # | Hole | Par | Gimmick | Good avg | Good HIO | Good ≤par | Good capped | Avg avg | Avg HIO | Avg ≤par | Avg capped | Gap | Escapes / timeouts | Ace lines | Timing stops (Studio est.) | Traps / soft-locks | Flag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Trailhead Gate | 2 | Bank shot off a striped boulder's 45° face | 1.95 | 6.6% | 99% | 0.0% | 2.38 | 0.0% | 67% | 0.0% | +0.43 | 0 / 0 | 35 | - | 0 / - | visible |
| 2 | Mine-Cart Junction | 3 | Tunnel choice: tight / dead end / long | 2.53 | 4.1% | 88% | 0.0% | 4.30 | 0.0% | 14% | 0.0% | +1.77 | 0 / 0 | 11 | - | 0 / - | visible |
| 3 | Ranger's Riverbend | 3 | River: rail-less log plank or railed footbridge (respawn) | 2.74 | 9.2% | 68% | 0.0% | 3.70 | 0.0% | 42% | 0.0% | +0.96 | 0 / 0 | 4 | - | 0 / - | visible |
| 4 | Crystal Corridor | 2 | Pinball rock-candy crystal bumpers | 2.54 | 1.1% | 49% | 0.0% | 3.22 | 0.0% | 18% | 0.0% | +0.67 | 0 / 0 | 13 | - | 0 / - | visible |
| 5 | Echo Slot | 3 | S-bend half-pipe with banked felt | 2.62 | 7.3% | 99% | 0.0% | 3.33 | 0.0% | 67% | 0.0% | +0.71 | 0 / 0 | 6 | - | 0 / - | visible |
| 6 | Flash Flood | 3 | Sliding sluice gate with pauses (timing) | 2.84 | 5.5% | 76% | 0.4% | 3.80 | 0.1% | 56% | 0.2% | +0.96 | 0 / 0 | 213 | 45.8% (11+0k /24) | 0 / 0 of 100k | visible |
| 7 | Rope Bridge Run | 4 | Two rope bridges over Taffy Gap, island (respawn) | 3.57 | 1.6% | 90% | 0.0% | 4.20 | 0.0% | 68% | 0.1% | +0.63 | 0 / 0 | 1 | - | 0 / - | visible |
| 8 | Gumdrop Gulch | 3 | Four rolling gumdrop humps (pace) | 2.41 | 4.9% | 98% | 0.0% | 2.78 | 0.1% | 88% | 0.0% | +0.36 | 0 / 0 | 14 | - | 0 / - | visible |
| 9 | Lollipop Windmill | 3 | Windpump lollipop vanes, vertical rotor (timing) | 2.52 | 5.6% | 86% | 0.1% | 4.24 | 0.0% | 27% | 0.0% | +1.72 | 0 / 0 | 257 | 33.3% (8+0k /24) | 0 / 0 of 100k | visible |
| 10 | Sluice Chute | 2 | One-way sluice chute (chevrons) into a basin | 1.99 | 6.6% | 95% | 0.0% | 2.53 | 0.0% | 55% | 0.0% | +0.54 | 0 / 0 | 12 | - | 0 / - | visible |
| 11 | Floodgate Lock | 3 | Lock gate + 4-stud lift platform (timing) | 2.77 | 7.1% | 78% | 0.2% | 3.57 | 0.0% | 56% | 0.4% | +0.80 | 0 / 0 | 45 | 41.7% (10+0k /24) | 0 / 0 of 100k | visible |
| 12 | Intake Tower | 4 | Intake-grate pipe teleport vs shoreline route | 3.44 | 4.0% | 74% | 0.7% | 4.99 | 0.0% | 25% | 0.2% | +1.56 | 0 / 0 | 30 | - | 0 / - | visible |
| 13 | Hoodoo Maze | 3 | Hoodoo maze, three corridors | 2.35 | 2.7% | 92% | 0.1% | 4.27 | 0.0% | 21% | 0.5% | +1.92 | 0 / 0 | 9 | - | 0 / - | visible |
| 14 | Ore Bucket Swing | 3 | Swinging ore bucket, pendulum (timing), ramp to raised green | 2.68 | 6.7% | 95% | 0.0% | 3.09 | 2.5% | 72% | 0.4% | +0.41 | 0 / 0 | 204 | 37.5% (9+0k /24) | 0 / 0 of 100k | visible |
| 15 | Sugar Dune | 3 | Tilted dune side slope to a two-tier green | 2.72 | 4.5% | 99% | 0.0% | 3.32 | 0.0% | 66% | 0.0% | +0.60 | 0 / 0 | 10 | - | 0 / - | visible |
| 16 | Sinkhole Drop | 2 | Sinkhole drop into a funnel bowl | 2.09 | 9.0% | 82% | 0.0% | 2.60 | 0.0% | 46% | 0.0% | +0.51 | 0 / 0 | 124 | - | 0 / - | visible |
| 17 | Sundial | 3 | Sundial shadow arms, horizontal sweeper (timing) | 2.64 | 2.2% | 84% | 0.4% | 3.19 | 0.2% | 69% | 0.4% | +0.55 | 0 / 0 | 146 | 33.3% (8+0k /24) | 0 / 0 of 100k | visible |
| 18 | Sunset Arch | 4 | Finale: banks round a hoodoo, ramp under the arch, geode shortcut | 3.45 | 0.9% | 83% | 0.0% | 4.25 | 0.0% | 57% | 0.3% | +0.80 | 0 / 0 | 5 | - | 0 / - | visible |
| | **Total** | **53** | | **47.85** | | | | **63.75** | | | | | | | | | |

**Every hole meets every target:** good HIO 0.9-9.2% with a brute-force ace line on all 18 holes; good average within par − 0.7 … par + 1
everywhere; skill gap ≥ +0.36 (smallest H8); average ≤ par + 1.30 (worst H2); stroke-cap hits ≤ 0.7% for both skills; 0 validator errors,
0 escapes in 60k fuzz shots per hole and in 72,000 AI plays, 0 timeouts; timing lines blocked 33-46% of phases **by stops** (no kicks), 0 traps,
0 soft-locks in 500,000 fuzz shots; every flag visible from its tee (H5's slot walls are within the clearance, its crystal cue stays as decoration;
H13 has a lantern cue); no teleport or lift exit carries the ball past its cup.

### LG playtest lessons applied

- **Cup visibility:** 7.5-stud flag on every cup and a tee-eye sightline check against rails, felt and prop occluders; 18/18 visible. Visual cues
  over the cup where tall dressing may still hide it (H5 crystal, H13 lantern).
- **Skill over luck:** every timing obstacle has a reliable safe route about a stroke longer (H6 overflow, H9 bypass, H14 side line, H17 either side;
  H11 has a signal lamp), and good golfers use it where it pays.
- **Respawn on misses:** H3's river and H7's gap respawn at the plank / island marker (+1), never back at the tee.
- **Felt arrows on one-way slopes:** chevrons on the H10 chute and deck, the H15 dune lip and fall line, and arrows into every route choice
  (H2, H3, H6, H9, H11, H12, H13, H16, H18) plus route signs.
- **Moving obstacles judged by stops, not kicks:** square faces on every mover (gate board, vane faces, lock gate, bucket foot square to the line,
  sundial arms), pointed ends on the sliding gate, pendulum foot and small swing per Lantern Grove Round 10. Every block on every timing line is a stop.
- **Rails beside banks 2.4 tall** (invisible), **no settling point under a mover**, **teleports on open floor** and exit speeds checked.

### Caveats (what the sim can't settle)

- **Studio calibration needed for all five movers and the lift.** The stop/kick model is calibrated on one Lantern Grove pendulum; Sugarloaf's
  sliding gate, rotors, lock gate and pendulum have no in-engine measurement yet. Ask the builder to fire each timing line (start, aim, speed in
  `timing-p6.json`) at 24-48 phases in Studio and compare blocked counts; first check CanCollide and per-frame motion.
- **H11 lift:** the sim moves the ball instantly to the quay at clamp(0.5·v, 1.5, 7) studs/s. In the game the platform must reproduce this
  (hold, ride 2 s, push the ball out at that speed) and keep the gate up while it rides. The ace needs the maximum 7.0 exit, so the builder's
  push speed should be exact.
- **H12 / H18 teleports** are generous by design (any exit at ≥ 4-4.8 studs/s holes): aces stay rare only because reaching the grate/geode fast is rare.
- **Par 53, not 54:** H15 plays as a par 3 (see Round 4). If the owner wants 54 back, H15 needs a genuinely longer layout (a new footprint), not tuning.
- **Close to the edge:** H5 (6 ace grid hits), H7 (1 ace grid hit: a 0.3°-wide line, so aces are rare in VR too), H8 gap +0.36, H13 good 2.35
  (band starts at 2.3). They meet the targets with the fixed golfer model, but a playtest may move them.
- **H5 base plate:** H5's collision felt is three big plates that run under the slot rock; only the channel between the rails is reachable.
  Hide the rest under the wall meshes.
- Decoration and props aren't modelled for physics; the 3D modeler must keep visuals over the colliders (bumper bases, bucket skid plate,
  vane and arm meshes at their pivots).

## Round p7 — layout, moving collision and VR comfort

This round supersedes the p6 par 53 and old mover/lift caveats above. Course par 54; H4 is par 3. The brief and Addenda 1–6 are implemented; two world sightline requirements conflict with the exact lowered dome and remain reported failures. Geometry remains authored in build_holes.py; models/ was not edited.

Changes: H2 open-top 3-wide west passage, overhead/lantern clearance 8, gentler route; H9 four 2.4-wide circular-tip vanes; H14 raised2.1×2×1.8 bucket and2.1×.4×.15 foot, signposted 256.5° safe bank; H17 four 3.6-wide arms and solid 7.5-radius plinth; H6/H11 real cuts, moving felt, full-height striped quay lip, fully closed gate through lift cycle. H7/dam solid parapets, skirts, mist/floor and player teleports. World minehead, separate game/hero suns, exact 128-summit dome, corrected cup/path heights, deduplicated landmarks, H3/H13 arrows.

### Final 2,000-play results

### p7
| # | Hole | Par | Good avg | Good HIO | Good ≤par | Good capped | Avg avg | Avg HIO | Avg ≤par | Avg capped | Gap | Haz/play (avg) | Escapes / timeouts | HIO-search hits | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Trailhead Gate | 2 | 1.95 | 6.6% | 99% | 0.0% | 2.38 | 0.0% | 67% | 0.0% | +0.43 | 0.00 | 0 / 0 | 35/34560 | ok |
| 2 | Mine-Cart Junction | 3 | 2.40 | 5.9% | 92% | 0.0% | 3.35 | 0.0% | 60% | 0.0% | +0.95 | 0.00 | 0 / 0 | 27/34560 | ok |
| 3 | Ranger's Riverbend | 3 | 2.74 | 9.2% | 68% | 0.0% | 3.70 | 0.0% | 42% | 0.0% | +0.96 | 0.00 | 0 / 0 | 4/34560 | ok |
| 4 | Crystal Corridor | 3 | 2.54 | 1.1% | 96% | 0.0% | 3.22 | 0.0% | 67% | 0.0% | +0.67 | 0.00 | 0 / 0 | 13/34560 | ok |
| 5 | Echo Slot | 3 | 2.62 | 7.3% | 99% | 0.0% | 3.33 | 0.0% | 67% | 0.0% | +0.71 | 0.00 | 0 / 0 | 6/34560 | ok |
| 6 | Flash Flood | 3 | 2.86 | 5.5% | 76% | 0.4% | 3.85 | 0.1% | 55% | 0.2% | +0.99 | 0.00 | 0 / 0 | 214/276480 | ok |
| 7 | Rope Bridge Run | 4 | 3.57 | 1.6% | 90% | 0.0% | 4.20 | 0.0% | 68% | 0.1% | +0.63 | 0.02 | 0 / 0 | 1/34560 | ok |
| 8 | Gumdrop Gulch | 3 | 2.42 | 4.9% | 98% | 0.0% | 2.78 | 0.1% | 88% | 0.0% | +0.36 | 0.00 | 0 / 0 | 14/34560 | ok |
| 9 | Lollipop Windmill | 3 | 2.83 | 3.4% | 78% | 0.2% | 4.33 | 0.0% | 23% | 0.0% | +1.50 | 0.00 | 0 / 0 | 230/276480 | ok |
| 10 | Sluice Chute | 2 | 1.98 | 6.6% | 96% | 0.0% | 2.52 | 0.0% | 56% | 0.0% | +0.54 | 0.00 | 0 / 0 | 12/34560 | ok |
| 11 | Floodgate Lock | 3 | 4.79 | 3.2% | 37% | 17.5% | 5.24 | 0.0% | 26% | 19.2% | +0.45 | 0.00 | 0 / 0 | 38/276480 | ok |
| 12 | Intake Tower | 4 | 3.44 | 4.0% | 74% | 0.7% | 4.99 | 0.0% | 25% | 0.2% | +1.56 | 0.01 | 0 / 0 | 30/34560 | ok |
| 13 | Hoodoo Maze | 3 | 2.35 | 2.7% | 92% | 0.1% | 4.27 | 0.0% | 21% | 0.5% | +1.92 | 0.00 | 0 / 0 | 9/34560 | ok |
| 14 | Ore Bucket Swing | 3 | 2.68 | 6.7% | 95% | 0.0% | 3.15 | 1.9% | 70% | 0.4% | +0.47 | 0.00 | 0 / 0 | 201/276480 | ok |
| 15 | Sugar Dune | 3 | 2.72 | 4.5% | 99% | 0.0% | 3.32 | 0.0% | 66% | 0.0% | +0.60 | 0.00 | 0 / 0 | 10/34560 | ok |
| 16 | Sinkhole Drop | 2 | 2.09 | 9.0% | 82% | 0.0% | 2.60 | 0.0% | 46% | 0.0% | +0.51 | 0.00 | 0 / 0 | 124/34560 | ok |
| 17 | Sundial | 3 | 2.75 | 6.2% | 79% | 0.6% | 3.58 | 0.1% | 54% | 0.7% | +0.84 | 0.00 | 0 / 0 | 33/276480 | ok |
| 18 | Sunset Arch | 4 | 3.45 | 0.9% | 83% | 0.0% | 4.25 | 0.0% | 57% | 0.3% | +0.80 | 0.00 | 0 / 0 | 5/34560 | ok |
| | **Total** | **54** | **50.18** | | | | **65.05** | | | | | | | | |

H1 Trailhead Gate: OK
H2 Mine-Cart Junction: OK
H3 Ranger's Riverbend: OK
H4 Crystal Corridor: OK
H5 Echo Slot: OK
H6 Flash Flood: OK
H7 Rope Bridge Run: OK
H8 Gumdrop Gulch: OK
H9 Lollipop Windmill: OK
H10 Sluice Chute: OK
H11 Floodgate Lock: good avg 4.79 vs [2.3,4.0]; avg avg 5.24 > 4.5; capped 17.5/19.2%
H12 Intake Tower: OK
H13 Hoodoo Maze: OK
H14 Ore Bucket Swing: OK
H15 Sugar Dune: OK
H16 Sinkhole Drop: OK
H17 Sundial: OK
H18 Sunset Arch: OK



### Timing results

**96 phases**

| Hole | Obstacle | Line | Period | Blocked (stops + kicks) | Deflected | Blocked+deflected | Studio est. (stops + 0.36 kicks) | Passed | Traps | Timings t=0, T/3, 2T/3 | Fuzz soft-locks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H6 | sluice_gate | intended | 7.867 s | 44/96 (44 + 0) | 0/96 | 45.8% | **45.8%** | 54.2% | 0 | passed, passed, blocked | 0/100000 |
| H6 | sluice_gate | ace | 7.867 s | 42/96 (42 + 0) | 2/96 | 45.8% | **43.8%** | 54.2% | 0 | blocked, passed, blocked | - |
| H9 | windpump | intended | 18 s | 40/96 (40 + 0) | 0/96 | 41.7% | **41.7%** | 58.3% | 0 | passed, blocked, blocked | 0/100000 |
| H9 | windpump | ace | 18 s | 28/96 (28 + 0) | 12/96 | 41.7% | **29.2%** | 58.3% | 0 | passed, passed, blocked | - |
| H11 | lock_gate | intended | 10.6 s | 74/96 (74 + 0) | 1/96 | 78.1% | **77.1%** | 21.9% | 0 | blocked, blocked, passed | 0/100000 |
| H11 | lock_gate | ace | 10.6 s | 74/96 (74 + 0) | 1/96 | 78.1% | **77.1%** | 21.9% | 0 | passed, blocked, blocked | - |
| H14 | ore_bucket | intended | 4 s | 44/96 (44 + 0) | 6/96 | 52.1% | **45.8%** | 47.9% | 0 | passed, passed, blocked | 0/100000 |
| H14 | ore_bucket | ace | 4 s | 0/96 (0 + 0) | 0/96 | 0% | **0%** | 100% | 0 | passed, passed, passed | - |
| H17 | shadow_arm | intended | 30 s | 52/96 (40 + 12) | 16/96 | 70.8% | **46.2%** | 29.2% | 0 | blocked, blocked, passed | 0/100000 |
| H17 | shadow_arm | ace | 30 s | 48/96 (40 + 8) | 24/96 | 75% | **44.7%** | 25% | 0 | blocked, blocked, deflected | - |

- H6: {'n': 100000, 'seed': 11, 'timeouts': 0, 'escapes': 0, 'pinned_rests': 0, 'excluded_rests': 0, 'escape_examples': [], 'pin_examples': [], 'examples': []}
- H9: {'n': 100000, 'seed': 11, 'timeouts': 0, 'escapes': 0, 'pinned_rests': 0, 'excluded_rests': 0, 'escape_examples': [], 'pin_examples': [], 'examples': []}
- H11: {'n': 100000, 'seed': 11, 'timeouts': 0, 'escapes': 0, 'pinned_rests': 0, 'excluded_rests': 0, 'escape_examples': [], 'pin_examples': [], 'examples': []}
- H14: {'n': 100000, 'seed': 11, 'timeouts': 0, 'escapes': 0, 'pinned_rests': 0, 'excluded_rests': 0, 'escape_examples': [], 'pin_examples': [], 'examples': []}
- H17: {'n': 100000, 'seed': 11, 'timeouts': 0, 'escapes': 0, 'pinned_rests': 0, 'excluded_rests': 0, 'escape_examples': [], 'pin_examples': [], 'examples': []}
**120 phases**

| Hole | Obstacle | Line | Period | Blocked (stops + kicks) | Deflected | Blocked+deflected | Studio est. (stops + 0.36 kicks) | Passed | Traps | Timings t=0, T/3, 2T/3 | Fuzz soft-locks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H6 | sluice_gate | intended | 7.867 s | 54/120 (54 + 0) | 1/120 | 45.8% | **45%** | 54.2% | 0 | passed, passed, blocked | 0/100000 |
| H6 | sluice_gate | ace | 7.867 s | 53/120 (53 + 0) | 2/120 | 45.8% | **44.2%** | 54.2% | 0 | blocked, passed, blocked | - |
| H9 | windpump | intended | 18 s | 52/120 (52 + 0) | 0/120 | 43.3% | **43.3%** | 56.7% | 0 | passed, blocked, blocked | 0/100000 |
| H9 | windpump | ace | 18 s | 44/120 (44 + 0) | 8/120 | 43.3% | **36.7%** | 56.7% | 0 | passed, passed, blocked | - |
| H11 | lock_gate | intended | 10.6 s | 92/120 (92 + 0) | 2/120 | 78.3% | **76.7%** | 21.7% | 0 | blocked, blocked, passed | 0/100000 |
| H11 | lock_gate | ace | 10.6 s | 93/120 (93 + 0) | 1/120 | 78.3% | **77.5%** | 21.7% | 0 | passed, blocked, blocked | - |
| H14 | ore_bucket | intended | 4 s | 55/120 (55 + 0) | 8/120 | 52.5% | **45.8%** | 47.5% | 0 | passed, passed, blocked | 0/100000 |
| H14 | ore_bucket | ace | 4 s | 0/120 (0 + 0) | 0/120 | 0% | **0%** | 100% | 0 | passed, passed, passed | - |
| H17 | shadow_arm | intended | 30 s | 72/120 (52 + 20) | 16/120 | 73.3% | **49.3%** | 26.7% | 0 | blocked, blocked, passed | 0/100000 |
| H17 | shadow_arm | ace | 30 s | 60/120 (52 + 8) | 32/120 | 76.7% | **45.7%** | 23.3% | 0 | blocked, blocked, deflected | - |

- H6: {'n': 100000, 'seed': 29, 'timeouts': 0, 'escapes': 0, 'pinned_rests': 0, 'excluded_rests': 0, 'escape_examples': [], 'pin_examples': [], 'examples': []}
- H9: {'n': 100000, 'seed': 29, 'timeouts': 0, 'escapes': 0, 'pinned_rests': 0, 'excluded_rests': 0, 'escape_examples': [], 'pin_examples': [], 'examples': []}
- H11: {'n': 100000, 'seed': 29, 'timeouts': 0, 'escapes': 0, 'pinned_rests': 0, 'excluded_rests': 0, 'escape_examples': [], 'pin_examples': [], 'examples': []}
- H14: {'n': 100000, 'seed': 29, 'timeouts': 0, 'escapes': 0, 'pinned_rests': 0, 'excluded_rests': 0, 'escape_examples': [], 'pin_examples': [], 'examples': []}
- H17: {'n': 100000, 'seed': 29, 'timeouts': 0, 'escapes': 0, 'pinned_rests': 0, 'excluded_rests': 0, 'escape_examples': [], 'pin_examples': [], 'examples': []}

H11 Addendum6 cycle10.6s: gate down0–2.3, rises2.3–2.95, closed2.95–9.95, lowers9.95–10.6. Deck rises3.45–5.45, LEVEL top dwell5.45–7.95, descends7.95–9.45. Lip flush5.35–8.05, raised otherwise. Gate margins0.5s before/after motion; lip margins0.1s before top/after descent starts.

### Checks and limits

PASS max putt distance: 59.9 studs (18.0 m) at V_MAX=19.78, analytic 60.0
PASS wall restitution: in 4.76 out 2.91 ratio 0.611
PASS ramp climb: v7.5 ends y=0.00 z=-5.0; v15 ends y=1.00 z=-31.1
PASS drop: ends y=-1.50 z=-21.5
PASS cliff blocks: ends z=-19.10 y=-1.50
PASS cup capture: gentle putt outcome 1, blast outcome 3
PASS side slope break: ball drifted to x=-5.01 (downhill = -x)
PASS static arm blocks: ball stopped at z=-2.79
PASS hazard respawn: outcome 5, placed at (0.00,-2.00)
PASS pendulum: bob at rest: ball stops z=-2.48; bob swung out 30 deg: z=-22.33
PASS dip settles: outcome 0 after 5.5 s at z=-2.99
PASS slider dwell: period 7.5 s, offsets [0.0, 1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 1.0, 0.0, 0.0]
PASS pendulum height rule: bob bottom 0.10: ball z=-22.33 (rolled under); bottom 0.06: z=-2.48
PASS rect teleport trigger: ended y=4.00 z=-17.52 (lifted onto the upper deck)
PASS pinned ball rests: outcome 0 after 2.5 s
PASS lift carries felt: no static lock floor; deck owns its felt
PASS lift real cycle: [0.0, 0.0, 2.0, 4.0, 4.0, 2.0000000000000013, 0.0]
PASS lip interlock: top y5; flush y4 from0.1s before top until0.1s after descent starts
PASS lift level dwell and margins: level top5.45–7.95; lip5.35–8.05; gate closed2.95–9.95
PASS incline turnaround continues: outcome 3 at z=40.01
PASS H8 repeated seam crossing settles: outcome 0 after 13.5s at z=-32.018494
ALL PASS


World: 2 failures, 3 warnings; walk 2700.4 studs.
- H17: Old Sugarloaf not visible from the tee ({'summit': -9.983153337097548, 'upper dome': -10.919861090130922})
- H18: Old Sugarloaf not visible from the tee ({'summit': -16.763691223205058, 'upper dome': -17.958416254179667})
- H4 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H5 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee
- H6 (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee

Global valid-felt fuzz, all terminal outcomes: {'n': 1800000, 'escapes': 0, 'timeouts': 0, 'pinned_rests': 0, 'excluded_rests': 0}. Evidence `_work/p7-global-fuzz-100k.json`.

Maximum-power quay lip/gate-pocket regression and full-cycle clearance results: tools/out/p7-cuts-regressions.json and p7-clearance.json. The H6 board intentionally rests on neck felt; that support contact is excluded from the adjacent-static clearance certificate. The simulator models rolling/contact, not ballistic hopping or Studio physics. Lift captures advance to scheduled release; late gate-top arrivals use an explicit gate-sill retention controller until the next ride. Studio must implement that controller; the simulation does not certify passive containment without it. Continuous deck/lip collision geometry is checked separately. Exact Addendum 5 dome hides behind protected Crown foundations from H17/H18, so these two visibility checks remain failed rather than carving playable terrain.

Full before/after numbers, cut boxes, mover dimensions and comfort placements: `_work/p7-report.md`. Layouts, contact sheet, course/world maps and all notes were regenerated. `props-full.md` preserves the pre-trim inventory; `props.md` gives current p7 priorities.

## Round p8 — H11 retune and world visibility exemption

Option 1's 6–7 s cycles failed (72.9–85.4% stops); the indexed idle gate in option 2 gave 0% stops. Adopted option 3: 11-wide return lane, approach extended south to Z=-6, 4.4-wide quay with safer lip-side pockets, one-second up/down travel and a 5.5 s entry window. Cycle10.7 s, top dwell2 s, gate margins0.3 s, lip flush7.0–9.2 around top7.1–9.1. Cuts retain≥0.15 clearance. No new indexed-gate requirement; existing sill/deck retention contract remains.

Good average 3.0675 (p7 4.7945), average golfer 3.7055 (p7 5.2420); capped 0.95%/1.30%. Intended stops46/96 (47.92%) and57/120 (47.50%), zero traps. Two100k phase-grid mover fuzz audits plus100k broad-felt audit: zero escapes/timeouts/pins. The extra broad test found one pre-final lip-corner timeout; widened pockets fix it and the exact shot is a permanent regression. Physics, ride-off, max-power lip, gate-top/sill, and full-cycle clearance checks pass. World validator CLEAN: H17/H18 Old Sugarloaf tee LOS now exempt, dome unchanged; three existing slot-canyon warnings remain.

Updated H11 notes/layout, layouts sheet and course map. Full evidence, timeline, before/after stats, simulator limits and engine requirements: `_work/p8-report.md`.

## Round p9 — clearance, H7 pads, H17 hour stones (H7/H9/H14/H17 only)

**Clearance (built exactly to brief):** H9 hub raised from y 4.12 to **4.25**. Vane strips are unchanged (4 × 6 strips, 2.4 wide, r 0.6..4.1, circular tips), so **tip clearance goes from 0.020 to 0.150** at every phase. The H14 foot is chamfered into 6 yaw-0 strips (0.35 × 0.15 deep), with the underside on an r 10.1998 arc about the hinge. **Lowest corner over ±9° goes from 0.0215 to 0.1502**; rest gap is 0.075 → 0.156 (centre) / 0.204 (outer).
**Stop-rate target NOT met on H9/H14.** The ball is 0.16 tall (r 0.08), so a collider ≥ 0.15 up bites only 0.01 and the ball rolls under. Both now block 0% at 96 and 120. Trade-off curve: H9 37.5%/36.7% at 0.06; 0% at 0.15. H14 39.6%/39.2% at 0.06; 0% from 0.08 up. One-knob fallbacks (`h9_clear`, `h14_foot_clear` = 0.06) are documented in `_work/p9-report.md`; they were not applied.

**H7 pads:** `bridge2_exit` [3.8,0,-59] → **[5.15,0,-59]** (west edge 0.15 outside the cup rim). `bridge1_island` [0,0,-38] → **[4.5,0,-38.5]** (2.6 edge-to-edge from the respawn stone, which stays at [0,0,-38.5]). `bridge2_island` [3.8,0,-44] and `bridge1_entry` [0,0,-25] unchanged. All four pads are flush, player-only and `ball_teleport=False`.

**H17 hour stones** (r 12.5 about (0,-36), 1.2×0.8×1.2, centre y 0.4, XII toward −Z, clockwise):

| Hour | Centre | Collision |
|---|---|---|
| XII | [0, 0.4, -48.5] | ON, rail-mounted |
| I | [6.25, 0.4, -46.8253] | off |
| II | [10.8253, 0.4, -42.25] | DROPPED (covers cup) |
| III | [12.5, 0.4, -36] | ON, rail-mounted |
| IV | [10.8253, 0.4, -29.75] | off |
| V | [6.25, 0.4, -25.1747] | DROPPED (good tee line + ace line) |
| VI | [0, 0.4, -23.5] | DROPPED (lane-mouth centre) |
| VII | [-6.25, 0.4, -25.1747] | off |
| VIII | [-10.8253, 0.4, -29.75] | off |
| IX | [-12.5, 0.4, -36] | ON, rail-mounted |
| X | [-10.8253, 0.4, -42.25] | off |
| XI | [-6.25, 0.4, -46.8253] | off |

Minimum arm-to-rail-stone gap: 0.26.

**Timing** (Studio est. = stops + 0.36 kicks; 0 traps everywhere):

| Hole | Line | 96 phases | 120 phases |
|---|---|---|---|
| H9 | intended | 0% (0 stops, 8 defl) (p8 41.7%) | 0% (0 stops, 12 defl) (p8 43.3%) |
| H9 | ace | 0% (p8 29.2%) | 0% (p8 36.7%) |
| H14 | intended | 0% (p8 45.8%) | 0% (p8 45.8%) |
| H14 | ace | 0% | 0% |
| H17 | intended | 46.2% (40+12) | 49.3% (52+20) |
| H17 | ace | 44.7% (40+8) | 45.7% (52+8) |

**Fuzz:** 100k shots for each of H9/H14/H17 on the 96-phase grid (seed 11) and the 120-phase grid (seed 29): 0 timeouts, 0 escapes, 0 pinned rests (H17: 0 excluded rests). Escape fuzz in `sim.py` (100k): 0 on H7/H9/H14/H17. Physics tests: ALL PASS.

**Plays** (2000/skill, avg p7 → p9):

| Hole | Good | Average |
|---|---|---|
| H7 | 3.5725 → 3.5725 | 4.1995 → 4.1995 |
| H9 | 2.8305 → 2.1610 | 4.3340 → 4.1285 |
| H14 | 2.6795 → 2.7010 | 3.1460 → 2.8195 |
| H17 | 2.7465 → 2.8230 | 3.5820 → 3.7530 |

Capped plays ≤ 0.8% on every hole. Ace lines unchanged on all four holes: H7 272.5°, H9 267.5°, H14 256.5°, H17 283°. H9 good (2.16) now sits below the 2.3 band floor because the tunnel is free.

Notes, layouts and the layouts sheet are regenerated for H7/H9/H14/H17. Full numbers: `_work/p9-report.md`.

## Round p9b — H9/H14 block-rate restore (clearance-aware)

Continues Round p9. H7 pads and H17 hour stones are unchanged from p9. H9/H14 were retuned so the timing gimmicks block again; a literal 0.15 tip clearance on a radial vane cannot stop a 0.16-tall ball (r 0.08).

### Geometry
- **H9:** hub stays at **y 4.12** (p8). Collision strips use 12 strips across 2.4 width; full-width centre clearance **0.06** (collision tip clearance 0.06, R_coll 4.06). Visual tip may still read to r 4.1. A true 0.15 collision tip clearance drops the stop rate to 0%; 0.06 is the highest clearance that stays in band.
- **H14:** 14 yaw-0 foot strips (0.15 wide). Centre strips (|x| ≤ 0.9) on a low arc (**0.06** min / **0.0613** at rest) so they block. Outer strips chamfered: **outer-corner min over ±9° = 0.1502**. Bucket body unchanged.

### Timing (Studio est. = stops + 0.36 kicks; 0 traps)

| Hole | Line | 96 phases | 120 phases |
|---|---|---|---|
| H9 | intended | **41.7%** (40+0) (p9 was 0%; p8 41.7%) | **43.3%** (52+0) (p8 43.3%) |
| H9 | ace | 30.7% (28+4) | 33.3% (40+0) |
| H14 | intended | **43.1%** (41+1) (p9 was 0%; p8 45.8%) | **42.8%** (51+1) (p8 45.8%) |
| H14 | ace | 0% | 0% |

**Fuzz:** 100k phase-grid shots each for H9/H14 at 96 (seed 11) and 120 (seed 29): 0 timeouts / 0 escapes / 0 pinned. sim.py 100k escape fuzz on H9/H14: 0. Physics: ALL PASS.

### Plays (2000/skill)

| Hole | Good avg | Avg avg | Good HIO | Notes |
|---|---|---|---|---|
| H9 | 2.82 (p7 2.83) | 4.32 (p7 4.33) | 3.3% | Ace 267.5° still exists (244/276480) |
| H14 | 2.69 (p7 2.68) | 3.03 (p7 3.15) | 6.7% | Ace 256.5° still exists (205/276480) |

Capped ≤ 0.6%. H7/H17 play and timing unchanged from p9.

Exact handoff numbers for 3D Model Bot: `_work/p9-report.md` (p9b section) and `_work/p9/clearance-p9b.json`.

## Oct 12 2026 — H8 rest-time fix (crease floors)
RobloxDevBot: a ball resting in the H8 washboard dips took ~3.3 s to count as stopped (target 0.5 s).
Probe `_work/h8-rest/rest_time.py` (810 low-speed releases into the 3 hollows; Studio-style counter = speed < 0.4 studs/s for 0.5 s, measured from when the ball stays within 0.16 studs of its rest spot):
- Before (sharp V hollows): delay median 2.02 s, p90 3.20 s, max 4.0 s — reproduces the ~3.3 s.
- Depth/spacing sweeps alone (depth 0.1–1.4 studs, seg 3–5 studs) never got below p90 ~2.4 s: a planar V always rocks.
- Fix: 0.5-stud flat crease floor at the bottom of each hollow (`h8_flat` 0 -> 0.5), dip slopes `h8_seg` 4.0 -> 3.8125 studs so hole length is unchanged; depth unchanged (+0.5 / -0.3).
- After: delay median 0.55 s, mean 0.66 s, p90 0.98 s (residual is ordinary slow rolling on the floor); 0.25-stud floor gave median 0.67 s.
- Difficulty (sim.py H8, n 2000): good 2.42 -> 2.42 (par or better 97.8% -> 97.9%, HIO 4.9% -> 4.8%); average 2.78 -> 2.78 (par or better 87.8% -> 87.8%); ace search 14/34560 both; 0 fuzz escapes.
- test_physics ALL PASS (H8 seam regression now accepts a rest anywhere on the -32 crease floor), test_validation pass, world validate CLEAN.

## 2026-10-12 late: game stop rule (slope < 0.015) — H8 humps, H15 lean rail
- Sim: `tools/rest_timing.py` now uses the game rule (gentle < 0.015: 0.5 s under 0.2 studs/s; steeper: 2 s wedge), reports wedged rests; Studio plans only for H8. `test_physics.py` +2 H8 checks (rest on gentle ground, no near-threshold slopes).
- H8: h8_dip_hi 0.3 -> 0.12, h8_seg 2.3125 -> 0.3 (0.4 ramps), h8_flat 4.5 -> 9.8667. Rest tail (480 shots, seed 5) p90 0.53 -> 0.50, max 5.95 -> 2.55 (seeds 6-9 max 3.0-3.55). Plays good 2.49 -> 2.44, avg 2.81 -> 2.79.
- H15: new knob h15_rail_in 8: a lean rail `dune_lean` inside the east edge (south end 8 in) so balls pressed on it slide north to the green. Random-shot wedges on reachable felt 133/397 -> 0. Plays good 2.72 -> 2.47, avg 3.32 -> 2.73.
