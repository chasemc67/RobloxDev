# Aurora Archipelago: Playtest Log

Simulator: `tools/sim.py` (copied from Sugarloaf Canyon / Lantern Grove; the calibrated physics is unchanged). It validates geometry,
fuzzes escapes (60k random shots per hole), brute-forces an ace-line search from the tee (34,560 shots, 276,480 with 8 moving phases) and
plays 2000 AI rounds per hole per skill. Physics tests: `tools/test_physics.py`. Timing obstacles: `tools/timing_check.py` (96 phases, also
verified at 120, stop/kick split, 100k-shot soft-lock fuzz per mover). Teleport and lift exits: `tools/teleport_check.py`. Per-round geometry
snapshots are in `tools/out/holes-<tag>.json` and raw results in `tools/out/sim-<tag>.json` (`tools/summarize.py <tag>` prints the tables
below and a per-hole target check).

**Physics (the builder's real Roblox values, measured for Lantern Grove; constants in `sim.py` and the `physics` block of `holes.json`):**
1 stud = 0.3 m. g = 32.7 studs/s². Rolling deceleration = 0.5 + 0.25·v studs/s². Rail restitution 0.63, bumper restitution 0.65 (static
bumpers and every moving blocker). Cup radius 0.5 stud, capture speed < 5.33 studs/s (1.6 m/s). Max putt 19.78 studs/s (5.9 m/s) = a
60-stud roll on flat felt. Drops keep 80% of horizontal speed. Pendulum height rule: a swing blocker only stops the ball if its lowest point
over the ball is at or below the ball's centre. dt = 1/240 s, 30 s per stroke, cap 8 strokes. **New for Aurora:** ice felt (H4) multiplies the
rolling deceleration by `decel_scale` = 0.35 (start value, **needs Studio calibration**).

**AI golfers (fixed, same model as Lantern Grove and Sugarloaf).** Per stroke the golfer aims at the furthest target it has line of sight to:
the cup, else the hole's `ai_waypoints` for its current zone. It hits for distance + carry, adding √(2gΔh) for climbs. Gaussian noise:
**good** aim σ 1.0°, power σ 5%, and on 30% of tee shots it goes for the hole's brute-force ace line (most robust grid hit) with line-memory
error ±1.5° / ±8%; **average** aim σ 2.5°, power σ 12%, never goes for aces. A hazard costs +1 and resets the ball to the stroke start, or to
the hazard's `respawn` point. The golfer fires at a random phase of every moving part (it never waits for a gap). The model was fixed in
Round 0 and never tuned per hole; only the course geometry and the waypoints (where a golfer of that skill would aim) change.

**Flags.** BROKEN = validator error, fuzz/AI escape, or the cup never reached. IMPOSSIBLE = good players capped >50%.
TRIVIAL = HIO >15% or avg < par−1. TOO-HARD = good avg > par+2. WARN:no-HIO-line = the brute-force search found no ace.

**Targets (Lantern Grove / Sugarloaf bands, from the start):**
- good HIO 0.2–10%, with a brute-force ace line on every hole;
- good average within par − 0.7 … par + 1;
- skill gap (average − good) ≥ 0.3;
- average ≤ par + 1.5;
- stroke-cap hits ≤ 1% for both skills;
- validator 0 errors, fuzz 0 escapes, 0 AI escapes, 0 timeouts;
- timing obstacles: the intended line blocked on 25–50% of phases **judged by stops** (Studio estimate = stops + 0.36 kicks); with no Studio
  calibration yet the sim aims ~10 points above the in-game target, i.e. **35–50% stops**; 0 traps, 0 soft-locks in a 100k-shot fuzz;
- every cup has a 7.5-stud flag, and the tee→flag sightline is clear or the hole has a stated visual cue;
- VR: ≥ 8 studs head clearance for anything over felt, parapets/guards on every drop, respawn (+1) on misses over gaps.

Total par 53 (front 27, back 26), as in `course.md`.

## Round 0: tools and sim changes (before any tuning)

| Change | Why |
|---|---|
| `tools/build_holes.py` rewritten for Aurora (helpers kept from Sugarloaf): all 18 holes, `K()` knobs, `SC_VARIANT` / `SC_OUT` sweep hooks, placements read from `world/world.json`, fit check of every felt corner, wall corner and mover reach against the hole's `concept.pads` | Single source of truth that can't drift from the world layout |
| `sim.py`: **ice felt** (`felt.surface='ice'`, `decel_scale`): rolling deceleration and the at-rest slope threshold scale by 0.35 on that piece | H4 Glissade (course.md: start 0.35x, calibrate in Studio) |
| `sim.py`: **timed surfaces** (`felt.timed = {part, period_s, solid:[on, off], phase_s}` + moving part type `toggle` with the full fade-in / solid / fade-out / gone profile). The piece supports and blocks only inside its solid window; a ball over it at any other time falls into the hazard below (+1, respawn) | H17 aurora light span: "collider only when fully solid" |
| `sim.py`: **lifts** (`teleports[].kind='lift'`, `lift = {cycle_s, board, release_s, column}`): a ball entering the platform rectangle while the platform is flush (or dropping in from the upper tier) is held and released at the scheduled time at clamp(entry speed × factor, min, max). The platform column is an ordinary vertical `slide` mover with dwell, whose side faces block while raised; vertical pistons never count as "pinning" a ball | H5 geyser lift. Replaces Sugarloaf's H11-only lock/lip/gate-sill code, which was removed |
| `sim.py` golfer planner made **surface-aware**: on a hole with ice it picks the putt speed by rolling the straight line over the real surfaces (same distance + carry rule). Identical on every other hole | Without it the golfer would fire ice putts 3x too hard; decided once, before tuning, not per hole |
| `sim.py` ace search phase grid = 8 phases over the hole's longest cycle (movers, timed felt, lift) instead of a fixed 0-12 s | Movers here have 7-18 s cycles |
| `test_physics.py`: Sugarloaf's H11 lock tests replaced by **ice roll distance** (28.5 studs at 5 studs/s vs 10.0 on felt, = analytic), **surface-aware planner** (rolls the requested 40 studs over felt-ice-felt), **timed bridge** (crosses while solid; falls and respawns when gone) and **geyser lift** (boards in the window; bounces off the raised column). **20/20 pass** | Pins every new rule |
| `timing_check.py`: OBSTACLES = H5 geyser column, H11 ice floe, H12 paddle wheel, H13 carousel arms, H14 icicle bell, H17 aurora span. Ghost runs remove the part (lift always boarding, span always solid). H17 blocks are falls, counted as stops | Six movers, one motion type each |
| `render_layout.py`, `write_notes.py`, `make_sheets.py`: ice felt, light span, lift trigger, player guards/decks, night course map, Aurora text and teaser-card-style concept prompts | Outputs |
| `world/tools/build_world.py` reads the real cups and pars from `holes.json` (as Sugarloaf did), so walkways start at the real cups | Phase 2 hook |
| Removed Sugarloaf-only checks (`check_p7_*.py`, `test_validation.py`) | They tested Sugarloaf's H6/H11 apertures |

## Round 1: first build of all 18 holes (`p1`)

Snapshot `tools/out/holes-p1.json`, results `sim-p1.json` / `sim-p1.log`. Every hole implements its `course.md` gimmick inside its world.json
concept pads (fit check: 0 points outside). Validator: 0 errors, 0 warnings on all 18 holes; every flag visible from its tee. Eleven holes
already met every target. Holes adapted from Sugarloaf's tuned layouts (H1, H2, H3, H9, H10, H11, H12, H13, H14) started close to their
reference numbers.

| # | Hole | Par | Good avg | Good HIO | Good ≤par | Good capped | Avg avg | Avg HIO | Avg ≤par | Avg capped | Gap | Haz/play (avg) | Escapes / timeouts | HIO-search hits | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lantern Quay | 2 | 1.95 | 6.6% | 99% | 0.0% | 2.38 | 0.0% | 67% | 0.0% | +0.43 | 0.00 | 0 / 0 | 35/34560 | ok |
| 2 | Snowpuff Burrows | 3 | 2.40 | 5.9% | 92% | 0.0% | 3.35 | 0.0% | 60% | 0.0% | +0.95 | 0.00 | 0 / 0 | 27/34560 | ok |
| 3 | Glimmer Crossing | 3 | 2.72 | 7.0% | 68% | 0.0% | 3.54 | 0.0% | 53% | 0.0% | +0.81 | 0.00 | 0 / 0 | 4/34560 | ok |
| 4 | Glissade | 3 | 1.71 | 29.1% | 100% | 0.0% | 2.00 | 11.4% | 100% | 0.0% | +0.29 | 0.00 | 0 / 0 | 98/34560 | TRIVIAL:good-HIO>15%, TRIVIAL:good-avg<par-1, TRIVIAL:average-avg<par-1 |
| 5 | Geyser Hop | 3 | 2.96 | 9.3% | 73% | 0.9% | 3.63 | 0.0% | 55% | 1.1% | +0.67 | 0.00 | 0 / 0 | 1957/276480 | ok |
| 6 | Palm Lagoon | 3 | 2.54 | 3.9% | 100% | 0.0% | 2.85 | 2.5% | 90% | 0.0% | +0.31 | 0.05 | 0 / 0 | 27/34560 | ok |
| 7 | Mogul Meadow | 3 | 1.88 | 15.2% | 99% | 0.0% | 2.21 | 4.8% | 94% | 0.0% | +0.33 | 0.00 | 0 / 0 | 29/34560 | TRIVIAL:good-HIO>15%, TRIVIAL:good-avg<par-1 |
| 8 | Coral Pinball | 3 | 3.19 | 0.0% | 69% | 0.8% | 3.75 | 0.0% | 41% | 0.2% | +0.56 | 0.00 | 0 / 0 | refine 3/10920 | ok |
| 9 | Conch Shortcut | 4 | 3.42 | 4.2% | 76% | 0.5% | 5.06 | 0.0% | 23% | 0.7% | +1.64 | 0.03 | 0 / 0 | 30/34560 | ok |
| 10 | Bobsled Bend | 3 | 2.63 | 7.4% | 99% | 0.0% | 3.31 | 0.0% | 69% | 0.0% | +0.68 | 0.00 | 0 / 0 | 6/34560 | ok |
| 11 | Floe Drift | 3 | 2.83 | 3.4% | 77% | 0.7% | 3.84 | 0.0% | 54% | 0.1% | +1.01 | 0.00 | 0 / 0 | 190/276480 | ok |
| 12 | Icebreaker Wheel | 3 | 2.86 | 2.9% | 77% | 0.4% | 4.31 | 0.0% | 23% | 0.0% | +1.46 | 0.00 | 0 / 0 | 144/276480 | ok |
| 13 | Snowpuff Carousel | 3 | 2.64 | 11.0% | 84% | 1.1% | 3.26 | 0.3% | 68% | 2.1% | +0.62 | 0.00 | 0 / 0 | 304/276480 | ok |
| 14 | Bell Buoy | 3 | 2.68 | 6.7% | 95% | 0.0% | 3.15 | 1.9% | 70% | 0.4% | +0.47 | 0.00 | 0 / 0 | 201/276480 | ok |
| 15 | Frozen Falls | 2 | 1.93 | 9.2% | 98% | 0.0% | 2.47 | 0.1% | 63% | 0.0% | +0.54 | 0.00 | 0 / 0 | 207/34560 | ok |
| 16 | Moonwell | 2 | 2.26 | 7.1% | 76% | 0.0% | 2.78 | 0.0% | 44% | 0.0% | +0.52 | 0.00 | 0 / 0 | 76/34560 | ok |
| 17 | Aurora Bridge | 3 | 3.06 | 13.6% | 69% | 4.2% | 3.55 | 0.0% | 53% | 0.0% | +0.49 | 0.00 | 0 / 0 | 73/276480 | ok |
| 18 | Halo Arch | 4 | 7.07 | 0.0% | 18% | 79.0% | 6.64 | 0.0% | 28% | 64.7% | -0.43 | 0.00 | 22 / 0 | refine 0/10920 | BROKEN:geometry, BROKEN:escapes, IMPOSSIBLE, TOO-HARD:good>par+2, WARN:no-HIO-line |
| | **Total** | **53** | **50.71** | | | | **62.08** | | | | | | | | |


Per-hole target check (`summarize.py p1`): H4 TRIVIAL (good HIO 29%, everyone aims straight at a cup on the ice line); H5 caps 0.9/1.1%
(the geyser blocks ~50% of phases and there is no way round, so 5-6 blocks in a row cap a play); H7 TRIVIAL (good HIO 15%, cup in line
of sight over the moguls); H8 no realistic ace (0.0% good HIO, 3 refine hits); H13 good HIO 11%, caps 1.1/2.1%; H17 good HIO 13.6%,
good caps 4.2% (good golfers re-try the light span after every fall); **H18 BROKEN**: 21 fuzz escapes over the 1-high rails beside the
crystal banks, and 79% of good plays capped (the golfer aimed from the plaza straight at the ramp top through the ramp's corner).

## Round 2: one hole at a time with sweeps (`p2`)

Every variant below was built to its own scratch file and run with validator + 60k fuzz + ace search + 2000 plays per skill
(`tools/sweep.py`, logs `tools/out/sweep-*.log`); movers also with `--timing` (96 phases, 20k fuzz). Chosen variant in **bold**.

| Hole | Variants tried (good avg / good HIO / good cap / avg avg / gap) | Chosen and why |
|---|---|---|
| H4 | straight cup on the ice line 1.71/29%; dogleg green east of the ice exit, cup (7.5,-50) 1.97/5.2%/+0.41; cup (6.5,-52) 1.95/7.2%; mirrored west 1.99/3.6%; longer ice to -44 1.96/7.1%; **uphill ice: rise 0.4** 2.09 but **871 timeouts** (a weak putt crawls 40 studs up the ice and slides back for >30 s: real physics, not a trap), rise 0.6 2.35/6.1%/+0.76, rise 0.8 1.99, **rise 0.6 + cup (9,-54) 2.39/6.6%/0%/3.24/+0.85** | Dogleg green (no line of sight to the cup, so nobody fires straight at it) and an ice strip that climbs 0.6 to the green: an under-hit ball slides all the way back down to the snow lane, an over-hit one hits the back rail. Pace is the whole hole |
| H5 | boarding pause 6.0 s: caps 0.9/1.1%; **8.0 s: 2.78/9.0%/0.1%/3.47/+0.69, timing 40/96 stops (41.7%)**; 9.0 s 2.67, 38.5% | Fewer back-to-back blocks; still a slow, obvious window (course.md's 2.0 s was the starting spec) |
| H7 | cup (7,-51) 2.48/0.4%; cup (7.5,-49) 4.39/21% cap (balls park in the last hollow); **moguls +0.6/-0.4, cup (6,-53) 2.40/5.9%/0%/2.83/+0.43** | Taller moguls and a cup out of the tee's line of sight |
| H8 | cup (-4.5,-47.5) 0.1%; **cup (-3.5,-48.5) 3.16/3.1%/0.6%/3.75/+0.58**; without the green coral 3.41/0.0% | The cup sits where a two-coral line can reach it |
| H13 | 20 °/s caps 1.1/2.1%; 15 °/s 2.80/7.8%/0.9%; 12 °/s 2.76/6.7%/1.1%; 20 °/s + cup (10.6,-47) 2.56/6.2%/0.9/0.9%; **15 °/s + cup (10.1,-46) 2.75/4.2%/0.5%/3.69/+0.94** | Slower arms (more readable) and the cup a little further round the ring. course.md's 20-25 °/s was a starting spec; 15 keeps caps ≤ 0.5% |
| H17 | as built 3.06/13.6%/4.2%; respawn zone `rim` from which good golfers take the safe bridge: cup (3,-56) 3.34/4.5%/0.5%/+0.21; cup (2.2,-56) 3.24/6.5%/0.4%/+0.33; cup west of the line (-1.2,-56) 16% HIO; (-2,-57) gap 0.00; **solid 6.0 s (cycle 9.0 s) + cup (2.2,-56) 3.10/6.9%/0.4%/3.57/+0.47, 40/96 falls (41.7%)**; solid 6.5 s 3.04, 38.5% | After one fall, a good golfer waits... the sim golfer can't wait, so after a fall it takes the safe bridge (smart play). Longer solid window = more crossings for the skilled line, bigger gap |
| H18 | rails beside the banks 2.4 high (collision only): 0 escapes. Plaza split into `plaza` / `plaza_w` with a ramp-foot waypoint: good 4.05, cap 2.2% (ramp 1.2 too steep), ramp 0.8 + ramp-shot power ×1.2: 3.18 but **no ace line** (two banks + a climb scatter every line; cups at (-12,-42), (-10,-43.5), (-13.5,-44), (-7,-42) all 0 lines). Added the **Halo Run**, a narrow crystal chute up through the plaza's north wall west of the bank: 2.0 wide 3.16/1.2%; **1.6 wide + tee carry 10: 3.57/3.8%/0%/4.28/+0.71** | The finale keeps its two-bank reading route; the chute is a risky one-shot line for aces |

H1, H2, H3, H6, H9, H10, H11, H12, H14, H15, H16 unchanged from p1 (already on target).

### Round 2 results (`p2` = final geometry, 2000 plays per skill)

Snapshot `tools/out/holes-p2.json` (identical to `holes.json`), results `sim-p2.json`, `timing-p2.json` / `timing-p2.txt` (96 phases, fuzz seed 11), `timing-p2-120.json` / `.txt` (120 phases, seed 29), `teleport-p2.txt`. Physics tests 20/20. Validator 0 errors / 0 warnings on all 18 holes, 0 fuzz escapes (60k per hole), 0 AI escapes, 0 timeouts. Every flag visible from its tee.

| # | Hole | Par | Good avg | Good HIO | Good ≤par | Good capped | Avg avg | Avg HIO | Avg ≤par | Avg capped | Gap | Haz/play (avg) | Escapes / timeouts | HIO-search hits | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lantern Quay | 2 | 1.95 | 6.6% | 99% | 0.0% | 2.38 | 0.0% | 67% | 0.0% | +0.43 | 0.00 | 0 / 0 | 35/34560 | ok |
| 2 | Snowpuff Burrows | 3 | 2.40 | 5.9% | 92% | 0.0% | 3.35 | 0.0% | 60% | 0.0% | +0.95 | 0.00 | 0 / 0 | 27/34560 | ok |
| 3 | Glimmer Crossing | 3 | 2.72 | 7.0% | 68% | 0.0% | 3.54 | 0.0% | 53% | 0.0% | +0.81 | 0.00 | 0 / 0 | 4/34560 | ok |
| 4 | Glissade | 3 | 2.39 | 6.6% | 90% | 0.0% | 3.24 | 0.0% | 69% | 0.4% | +0.85 | 0.00 | 0 / 0 | 34/34560 | ok |
| 5 | Geyser Hop | 3 | 2.78 | 9.0% | 78% | 0.1% | 3.47 | 0.0% | 58% | 0.4% | +0.69 | 0.00 | 0 / 0 | 2419/276480 | ok |
| 6 | Palm Lagoon | 3 | 2.54 | 3.9% | 100% | 0.0% | 2.85 | 2.5% | 90% | 0.0% | +0.31 | 0.05 | 0 / 0 | 27/34560 | ok |
| 7 | Mogul Meadow | 3 | 2.40 | 5.9% | 98% | 0.0% | 2.83 | 0.0% | 86% | 0.0% | +0.43 | 0.00 | 0 / 0 | 13/34560 | ok |
| 8 | Coral Pinball | 3 | 3.16 | 3.1% | 65% | 0.6% | 3.75 | 0.0% | 39% | 0.1% | +0.58 | 0.00 | 0 / 0 | 12/34560 | ok |
| 9 | Conch Shortcut | 4 | 3.42 | 4.2% | 76% | 0.5% | 5.06 | 0.0% | 23% | 0.7% | +1.64 | 0.03 | 0 / 0 | 30/34560 | ok |
| 10 | Bobsled Bend | 3 | 2.63 | 7.4% | 99% | 0.0% | 3.31 | 0.0% | 69% | 0.0% | +0.68 | 0.00 | 0 / 0 | 6/34560 | ok |
| 11 | Floe Drift | 3 | 2.83 | 3.4% | 77% | 0.7% | 3.84 | 0.0% | 54% | 0.1% | +1.01 | 0.00 | 0 / 0 | 190/276480 | ok |
| 12 | Icebreaker Wheel | 3 | 2.86 | 2.9% | 77% | 0.4% | 4.31 | 0.0% | 23% | 0.0% | +1.46 | 0.00 | 0 / 0 | 144/276480 | ok |
| 13 | Snowpuff Carousel | 3 | 2.75 | 4.2% | 80% | 0.5% | 3.69 | 0.1% | 51% | 0.5% | +0.94 | 0.00 | 0 / 0 | 52/276480 | ok |
| 14 | Bell Buoy | 3 | 2.68 | 6.7% | 95% | 0.0% | 3.15 | 1.9% | 70% | 0.4% | +0.47 | 0.00 | 0 / 0 | 201/276480 | ok |
| 15 | Frozen Falls | 2 | 1.93 | 9.2% | 98% | 0.0% | 2.47 | 0.1% | 63% | 0.0% | +0.54 | 0.00 | 0 / 0 | 207/34560 | ok |
| 16 | Moonwell | 2 | 2.26 | 7.1% | 76% | 0.0% | 2.78 | 0.0% | 44% | 0.0% | +0.52 | 0.00 | 0 / 0 | 76/34560 | ok |
| 17 | Aurora Bridge | 3 | 3.10 | 6.9% | 62% | 0.4% | 3.57 | 0.0% | 52% | 0.0% | +0.47 | 0.00 | 0 / 0 | 48/276480 | ok |
| 18 | Halo Arch | 4 | 3.57 | 3.8% | 93% | 0.0% | 4.28 | 0.0% | 64% | 0.1% | +0.71 | 0.00 | 0 / 0 | 6/34560 | ok |
| | **Total** | **53** | **48.38** | | | | **61.86** | | | | | | | | |


**Every hole meets every play target** (`summarize.py p2`: 18/18 OK).

**Timing obstacles, 96 phases (100k-shot soft-lock fuzz per mover):**

| Hole | Obstacle | Line | Period | Blocked (stops + kicks) | Deflected | Blocked+deflected | Studio est. (stops + 0.36 kicks) | Passed | Traps | Timings t=0, T/3, 2T/3 | Fuzz soft-locks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H5 | geyser_column | intended | 13.5 s | 40/96 (40 + 0) | 0/96 | 41.7% | **41.7%** | 58.3% | 0 | passed, blocked, blocked | 0/100000 |
| H5 | geyser_column | ace | 13.5 s | 39/96 (39 + 0) | 0/96 | 40.6% | **40.6%** | 59.4% | 0 | passed, passed, blocked | - |
| H11 | ice_floe | intended | 7.867 s | 44/96 (44 + 0) | 0/96 | 45.8% | **45.8%** | 54.2% | 0 | passed, passed, blocked | 0/100000 |
| H11 | ice_floe | ace | 7.867 s | 42/96 (42 + 0) | 2/96 | 45.8% | **43.8%** | 54.2% | 0 | deflected, passed, blocked | - |
| H12 | paddle_wheel | intended | 12 s | 40/96 (40 + 0) | 4/96 | 45.8% | **41.7%** | 54.2% | 0 | passed, blocked, passed | 0/100000 |
| H12 | paddle_wheel | ace | 12 s | 36/96 (36 + 0) | 4/96 | 41.7% | **37.5%** | 58.3% | 0 | passed, blocked, passed | - |
| H13 | carousel_arms | intended | 24 s | 40/96 (32 + 8) | 32/96 | 75% | **36.3%** | 25% | 0 | blocked, deflected, passed | 0/100000 |
| H13 | carousel_arms | ace | 24 s | 32/96 (32 + 0) | 20/96 | 54.2% | **33.3%** | 45.8% | 0 | passed, blocked, passed | - |
| H14 | icicle_bell | intended | 4 s | 44/96 (44 + 0) | 6/96 | 52.1% | **45.8%** | 47.9% | 0 | passed, passed, blocked | 0/100000 |
| H14 | icicle_bell | ace | 4 s | 0/96 (0 + 0) | 0/96 | 0% | **0%** | 100% | 0 | passed, passed, passed | - |
| H17 | aurora_span | intended | 9 s | 40/96 (40 + 0) | 0/96 | 41.7% | **41.7%** | 58.3% | 0 | passed, passed, blocked | 0/100000 |
| H17 | aurora_span | ace | 9 s | 0/96 (0 + 0) | 0/96 | 0% | **0%** | 100% | 0 | passed, passed, passed | - |

**Verified at 120 phases (independent 100k fuzz, seed 29):**

| Hole | Obstacle | Line | Period | Blocked (stops + kicks) | Deflected | Blocked+deflected | Studio est. (stops + 0.36 kicks) | Passed | Traps | Timings t=0, T/3, 2T/3 | Fuzz soft-locks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H5 | geyser_column | intended | 13.5 s | 49/120 (49 + 0) | 0/120 | 40.8% | **40.8%** | 59.2% | 0 | passed, blocked, blocked | 0/100000 |
| H5 | geyser_column | ace | 13.5 s | 49/120 (49 + 0) | 0/120 | 40.8% | **40.8%** | 59.2% | 0 | passed, passed, blocked | - |
| H11 | ice_floe | intended | 7.867 s | 54/120 (54 + 0) | 1/120 | 45.8% | **45%** | 54.2% | 0 | passed, passed, blocked | 0/100000 |
| H11 | ice_floe | ace | 7.867 s | 53/120 (53 + 0) | 2/120 | 45.8% | **44.2%** | 54.2% | 0 | deflected, passed, blocked | - |
| H12 | paddle_wheel | intended | 12 s | 52/120 (52 + 0) | 0/120 | 43.3% | **43.3%** | 56.7% | 0 | passed, blocked, passed | 0/100000 |
| H12 | paddle_wheel | ace | 12 s | 40/120 (40 + 0) | 8/120 | 40% | **33.3%** | 60% | 0 | passed, blocked, passed | - |
| H13 | carousel_arms | intended | 24 s | 52/120 (44 + 8) | 40/120 | 76.7% | **39.1%** | 23.3% | 0 | blocked, deflected, passed | 0/100000 |
| H13 | carousel_arms | ace | 24 s | 40/120 (40 + 0) | 24/120 | 53.3% | **33.3%** | 46.7% | 0 | passed, blocked, passed | - |
| H14 | icicle_bell | intended | 4 s | 55/120 (55 + 0) | 8/120 | 52.5% | **45.8%** | 47.5% | 0 | passed, passed, blocked | 0/100000 |
| H14 | icicle_bell | ace | 4 s | 0/120 (0 + 0) | 0/120 | 0% | **0%** | 100% | 0 | passed, passed, passed | - |
| H17 | aurora_span | intended | 9 s | 50/120 (50 + 0) | 0/120 | 41.7% | **41.7%** | 58.3% | 0 | passed, passed, blocked | 0/100000 |
| H17 | aurora_span | ace | 9 s | 0/120 (0 + 0) | 0/120 | 0% | **0%** | 100% | 0 | passed, passed, passed | - |

Intended lines blocked 41.7-45.8% of phases (H13 36.3% Studio estimate: 32 stops + 8 kicks at 96 phases, 39.1% at 120), all within the
25-50% band and ~10 points above a 25-35% in-game expectation; **0 traps, 0 soft-locks, 0 pinned rests, 0 escapes in 1.2M fuzz shots**.
H17's blocks are falls (the span is gone): the ball respawns at the light-route entry (+1). Teleport/lift exits (`teleport-p2.txt`): the
H5 geyser puffs hole for exit speeds 7.3-10.1 studs/s; at the 12.0 cap the ball passes over the cup at 7.3 and meets the back rail at only
3.5 studs/s. The H9 conch holes at every exit speed ≥ 4.8 (generous by design, like Sugarloaf's pipe: reaching the ring is the hard part).

### World (Phase 2 hook)

`world/tools/build_world.py` now reads each cup and par from `holes.json`; walkways start at the real cups. Placements and pads are
unchanged. `world/tools/validate.py` gained a holes.json check (placement identical, 0 points outside pads, cup = walkway start).
Iterations 12-13 in `world/validation.md`: **CLEAN, 0 warnings**; walk spawn -> H18 cup 1955 studs (was 1904). Maps re-rendered.

### What the builder must build (Phase 2 numbers, all in holes.json)

- Collision straight from holes.json (invisible, Anchored, CanCollide; felt `center` = top surface). Workspace.Gravity 32.7, max putt 19.78.
- **H4 ice felt:** calibrate first (5 putts at 5.0 studs/s on the ice should roll 28.5 studs; felt rolls 10.0) and report the distance.
- **H5 geyser:** column = vertical slide 0 -> 4 at 2 studs/s, pauses 8.0 s down / 1.5 s up (cycle 13.5 s). Hold the ball once its centre is
  on the platform during the down pause (or drops in from above); at t = 10.1 s set its velocity along exit.dir from (0, 4, -29.6) at
  clamp(entry speed × 0.9, 3.5, 12.0).
- **H11 floe** 3.0 studs/s, pauses 1.2 s blocking / 2.0 s parked; **H12 wheel** 30 °/s; **H13 carousel** 15 °/s; **H14 bell** ±9° / 4 s;
  **H17 light span** cycle 9.0 s: fade in 0.6 / solid 6.0 / fade out 0.6 / gone 1.8, collider only in [0.6, 6.6) s.
- Player-only geometry (`vr_comfort`): PlayerGuard panels on the H3/H17 gap rims and rail-less crossings, H15 lip parapet, railed decks
  beside the H3/H17 safe bridges, timber steps beside the H5 and H15 tier drops. Stroke timeout safety net 20 s, cap 8.

### Caveats (what the sim can't settle)

- **H4 ice friction is a guess (0.35x).** Every H4 number depends on it. If Studio measures a different roll, refit `decel_scale` and re-run
  H4 (the uphill rise and the cup are the knobs).
- **Movers are uncalibrated.** The stop/kick factor (0.36) comes from one Lantern Grove pendulum. Fire each intended line (start/aim/speed in
  `timing-p2.json`) at 24-48 phases in Studio. First check CanCollide and per-frame motion.
- **H5 lift and H17 span are scripted behaviours**, not passive physics: the hold-and-puff rule and the CanCollide toggle must match exactly.
- **The sim golfer never waits for a gap**; real players will, so movers will feel easier than these averages. H17 encodes "after a fall,
  take the safe bridge" through its `rim` respawn zone.
- Ice rise 0.4 timed out 871 strokes (a very slow slide back); 0.6 is clear but don't lower the rise without re-running.
- Starting specs changed in tuning: H5 boarding pause 2.0 -> 8.0 s, H13 20-25 -> 15 °/s, H17 solid 2.2 -> 6.0 s with the light span 8 long
  between fixed crystal piers (a 26-long span can't be crossed in 2.2 s).
- Close to the edge: H4 good 2.39 (floor 2.3), H5 good HIO 9.0% (cap 10), H17 gap +0.47, H13 pure stops 33%.

## Round 3: clearance fix (`clear`)

**Request (owner).** (1) Blocking movers 0.06 over the felt (the ball is 0.16 tall, so they must still block): H12 lowest paddle edge 0.02 -> 0.06;
H14 foot bottom -> 0.06, with every corner of every collider >= 0.06 at every swing angle. (2) >= 0.15 between a mover collider (whole cycle)
and adjacent rails/walls: H5 geyser_column, H17 light span, H11 ice floe. Smallest change, no gap a 0.16 ball can slip through or get stuck in.
(3) Everything else unchanged; all targets must still pass. Geometry edited only in `build_holes.py`; pre-fix snapshot `tools/out/holes-p2-preclear.json`.

**New tool:** `tools/check_clearance.py` gives exact OBB-OBB distances (SAT + vertex/edge pairs) from each mover to every rail/wall over 2001 samples
of the cycle, plus the lowest collider corner over the felt at 7201 angles (H12/H14). `--probe` fires 40k shots into each new rail-end slot.

**Clearances** (`tools/out/clearance-preclear.txt` -> `clearance-clear.txt`):

| Hole | Mover | Measured | Before | After | Target |
|---|---|---|---|---|---|
| H5 | geyser_column | vs upper_rail8/12 ends (full cycle) | **0.000** (rail ends flush with the column at x +-1.5) | **0.150** | >= 0.15 |
| H11 | ice_floe | vs rails/pocket walls (full cycle) | 0.150 (cut stub under the track; pocket walls 0.152) | 0.150 (no change needed) | >= 0.15 |
| H17 | aurora_span (light_span collider) | vs pier rails | **0.000** (pier rail ends touch the span corners) | **0.150** (green rails >= 9 away) | >= 0.15 |
| H12 | paddle_wheel | lowest corner over felt, full turn | 0.020 | **0.060** | >= 0.06, < 0.16 |
| H14 | icicle_bell foot | lowest corner over felt, +-9 deg | 0.021 (0.075 at rest) | **0.061** (0.062 at rest, centre) | >= 0.06, < 0.16 |
| H14 | icicle_bell body | lowest corner over felt | 0.257 (0.35 at rest) | 0.257 (gap 0.35 kept) | >= 0.06 |

Felt contacts (info, not rails/walls, unchanged): the column rides its cliff face and sinks into the basin felt (the shaft must be cut in
Studio), the floe slides on the neck felt, and the span butts onto its piers.

**What changed and why (including two fixes beyond the literal request):**
- **H12:** `H12_LOW` 0.06: axle y 4.12 -> 4.16.
- **H17:** pier_s/pier_n rails stop 0.15 short of the span (9 -> 8.85 long). The 0.15 notch opens onto the same open gap as the span's
  rail-less edge. Probe: 0 escapes, 0 timeouts, slot rests 38 (39 before).
- **H5:** upper_rail8/12 trimmed 0.15 at the shaft (ends at x +-1.65). Trimming alone opened a real leak: balls crossing the cliff edge
  diagonally at the shaft corners fell past the 1.5 lift trigger into the basin. 461 + 1263 of 2 x 100k upper-green fuzz shots (0 before).
  A 0.16 ball can't pass the 0.15 slot while the column is up, but it can wedge there and drop when the column sinks. Inward rail hooks didn't
  fix it (240 leaks). **Fix:** the lift's drop-in trigger is 0.15 wider each side (`lift.drop_half_size` [1.65, 1.5]; `sim.py` honours it,
  3 lines). Leaks are back to 0/200k; basin boarding is unchanged (16856/89840 lifts, same as before). Basin boarding stays +-1.5.
- **H14:** with the 2.1-wide flat foot, "rest 0.06" and "every corner >= 0.06" conflict: the end corners dip 0.053 below the rest bottom at
  +-5.8 deg. Raising the flat foot to clear that (rest 0.115) broke blocking. Under the sim's pendulum rule (Round 8: a bob whose bottom is
  above the ball centre 0.08 rolls over it), the intended line dropped 45.8% -> **10.4%**. **Fix:** the foot is now 9 strips (same 2.1 x 0.4
  x 0.15 envelope) whose bottom corners sit on an arc r 10.289 about the hinge, like H12's clipped tips. The centre is 0.062 over the felt at
  rest, the ends 0.115, and no corner is ever below 0.061. Blocking is back (46.9%); 7 strips gave 42%, 9 gave 47.9-46.9%.

**Stats before -> after** (`sim.py --tag preclear` vs `--tag clear`, same seeds, 2000 plays/skill, 100k fuzz; `summarize.py`: all 5 OK):

| Hole | Good avg | Good HIO | Avg avg | Avg HIO | HIO-search hits | Validator / fuzz escapes | Intended line Studio est. (96 ph) | Traps | Soft-locks (100k) |
|---|---|---|---|---|---|---|---|---|---|
| H5 | 2.78 -> 2.78 | 9.0% -> 9.0% | 3.47 -> 3.47 | 0.0% -> 0.0% | 2419 -> 2419 | 0 / 0 | 41.7% -> 41.7% | 0 | 0 -> 0 |
| H11 | 2.83 -> 2.83 | 3.4% -> 3.4% | 3.84 -> 3.84 | 0.0% -> 0.0% | 190 -> 190 | 0 / 0 | 45.8% -> 45.8% | 0 | 0 -> 0 |
| H12 | 2.86 -> 2.80 | 2.9% -> 3.5% | 4.31 -> 4.27 | 0.0% -> 0.0% | 144 -> 172 | 0 / 0 | 41.7% -> 37.5% | 0 | 0 -> 0 |
| H14 | 2.68 -> 2.68 | 6.7% -> 6.7% | 3.15 -> 3.08 | 1.9% -> 2.1% | 201 -> 208 | 0 / 0 | 45.8% -> 46.9% | 0 | 0 -> 0 |
| H17 | 3.10 -> 3.12 | 6.9% -> 6.9% | 3.57 -> 3.57 | 0.0% -> 0.0% | 48 -> 48 | 0 / 0 | 41.7% -> 41.7% | 0 | 0 -> 0 |

The 100k timing fuzz per mover had 0 timeouts, 0 pinned rests, 0 escapes and 0 excluded rests, before and after. `test_physics.py`: ALL PASS. The H12 ace line
moved (new search pick), and its blocking is 37.5% -> 20.8% (info; the band applies to intended lines). The 120-phase verification was not re-run.

**Builder actions (Studio):**
- H5: upper_rail8/12 -> centre x -/+7.325, length 11.35 (ends at x +-1.65). Geyser script: a ball dropping in from the upper green is held
  if its centre is within x +-1.65, z +-1.5 of the platform centre; basin boarding stays +-1.5.
- H12: paddle_wheel hub y 4.16 (world y 150.16); blockers unchanged relative to the hub.
- H14: replace the single foot collider with the 9 strip colliders in holes.json (icicle_bell blockers 1..9); hinge, bell and timing unchanged.
- H17: pier_s_rail6/7 -> z centre -20.425, length 8.85; pier_n_rail8/9 -> z centre -37.575, length 8.85.

**Modeler actions:**
- H5: upper-rail meshes end at x +-1.65. Keep the 0.15 slot beside the column free of colliding dressing (cliff/shaft trim must be non-colliding there).
- H12: no mesh change; the wheel rides 0.04 higher with its hub.
- H14: skid plate underside = arc r 10.289 about the hinge (0.062 over the felt at the centre, 0.115 at the ends), top y 0.461 at rest.
- H17: pier rail meshes 8.85 long, ending 0.15 short of the light span at both piers.

Files: `holes.json`, `h05/h11/h12/h14/h17-layout.png` and `-notes.md`, `props.md` / `props-full.md` (only the changed numbers),
`tools/build_holes.py`, `tools/sim.py` (lift drop-in trigger), `tools/check_clearance.py` (new), `tools/out/*preclear*` / `*clear*`.

## Round 4: wall clearance (fitcheck) (`walls`)

**Request.** 3D Model Bot's fitcheck (`models/props/fitcheck_railskin_validated.txt`) flagged H11 ice_floe at 0.050 to `rail5__cut1` (offset
-5.10) and H12 paddle_wheel at 0.050 to `rail2`, but our `check_clearance.py` said H11 0.150 and didn't check H12 against walls. Fix the checker
so it reproduces both findings. Then move or trim only the walls (not the movers) to get H11 floe-to-wall >= 0.15 and H12 wheel-to-wall >= 0.06
over the full motion. Make the smallest change, leave no gap a 0.16 ball can slip through or get stuck in, and change nothing else.
Pre-fix snapshot: `tools/out/holes-clear-prewalls.json`.

**Why our check missed them.** H11: the floe colliders are 1.0 tall (0.17 under the 1.17 lintel), but the modelled floe (snow + snowpuff) tops
out at 1.12, which is 0.05 under the lintel. The fitcheck measures that mesh. H12: the paddles are z +-0.2 about the axle (z -17.75), and the
stern wall line was z -18.0, a constant 0.05 at every angle to rail2, rail3, hull13 and hull18. **Checker changes:** a new H11 *visual*
row (the blocker footprints extended to `VISUAL_TOP` 1.12), H12 paddle_wheel vs every wall over a full turn (target 0.06), and the motion position
at each minimum. Every wall is checked, including the `__cut0-3` residual pieces, with exact OBB distances (corners, edges and faces).

**Clearances** (`tools/out/clearance-prewalls.txt` -> `clearance-walls.txt`, 2001 samples of the cycle):

| Hole | Mover | Measured | Before | After | Target |
|---|---|---|---|---|---|
| H11 | ice_floe (visual top 1.12) | vs rail5__cut1 / berg18__cut1 (lintels) | **0.050** | **0.150** | >= 0.15 |
| H11 | ice_floe (collider) | vs sill cut0 / pocket walls | 0.150 / 0.152 | 0.150 / 0.152 | >= 0.15 |
| H12 | paddle_wheel (collider) | vs rail2, rail3, hull13, hull18 | **0.050** | **0.060** | >= 0.06 |
| H5, H17, H12 felt, H14 felt | (unchanged) | | 0.150, 0.150, 0.060, 0.061 | same | |

**Wall changes** (`build_holes.py` knobs `h11_lintel`, `h12_mouth_z`; nothing else in holes.json changed):
- H11: the slot window top (lintel underside) moved 1.17 -> 1.27 in rail5 and berg18. `rail5__cut1`/`berg18__cut1` centre y 1.785 -> 1.835, height 1.23 -> 1.13.
  The side pieces `__cut2`/`__cut3` follow the window: centre y 0.51 -> 0.56, height 1.32 -> 1.42. Only the part above the ball changes (a 0.16
  ball on the felt never reaches y 1.17).
- H12: the stern wall line at the wheel moved z -18 -> -18.01. rail2/hull13 centre z -18.25 -> -18.26. rail3/hull18 centre z -21 -> -21.005, length 6 -> 5.99.
  The mitred neighbours follow: rail1 centre z -8 -> -8.005, length 21 -> 21.01; hull14 centre z -26 -> -26.005, length 16 -> 15.99. Felt is unchanged.
  The 0.01 strip behind the felt edge is far narrower than the ball (r 0.08), so nothing can enter it.

**Stats before -> after** (`sim-clear` -> `sim-walls`, 2000 plays/skill; validator 0 issues and 0 escapes in the 60k fuzz; `summarize.py walls`: both OK):

| Hole | Good avg | Good HIO | Avg avg | Avg HIO | HIO-search hits | Intended line Studio est. (96 ph) | Traps | Soft-locks / escapes / timeouts (100k) |
|---|---|---|---|---|---|---|---|---|
| H11 | 2.83 -> 2.83 | 3.4% -> 3.4% | 3.84 -> 3.84 | 0.0% -> 0.0% | 190 -> 190 | 45.8% -> 45.8% | 0 | 0 / 0 / 0 |
| H12 | 2.80 -> 2.81 | 3.5% -> 3.5% | 4.27 -> 4.28 | 0.0% -> 0.0% | 172 -> 172 | 37.5% -> 37.5% | 0 | 0 / 0 / 0 |

`test_physics.py`: ALL PASS. Ace lines are unchanged (H11 43.8%, H12 20.8% blocked; for info only). This round's sim fuzz was 60k (Round 3 used 100k).

**Builder actions (Studio):**
- H11: in rail5 and berg18, raise the floe slot's lintel underside to y 1.27. rail5__cut1/berg18__cut1 -> centre y 1.835, size y 1.13. cut2/cut3 -> centre y 0.56, size y 1.42.
- H12: rail2/hull13 -> centre z -18.26. rail3/hull18 -> centre z -21.005, length 5.99. rail1 -> centre z -8.005, length 21.01. hull14 -> centre z -26.005, length 15.99.

**Modeler actions (3D Model Bot):**
- H11: rail/snowbank skins: open window y -0.15..1.27, lintel skin from y 1.27 up. Keep the floe mesh top <= 1.12 (now 0.15 under the lintel).
  Update the fitcheck's lintel constant 1.17 -> 1.27.
- H12: icebreaker stern faces (rail2/hull13, rail3/hull18 ends) move to z -18.01, 0.06 behind the paddles. Paddle wheel unchanged.

Files: `holes.json`, `tools/build_holes.py`, `tools/check_clearance.py`, `h11/h12-layout.png` and `-notes.md`, `props.md` / `props-full.md`
(the changed numbers only), `tools/out/*prewalls*` / `*walls*`.
