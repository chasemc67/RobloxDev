# Lantern Grove: Playtest Log

Simulator: `tools/sim.py`. It validates geometry, fuzzes escapes (60k random shots per hole), brute-forces an ace-line search from the tee,
and plays 2000 AI rounds per hole per skill. Physics tests: `tools/test_physics.py`.
Per-round geometry snapshots are in `tools/out/holes-<tag>.json` and raw results in `tools/out/sim-<tag>.json`.

**Physics (RobloxDevBot real values, constants in `sim.py` and the `physics` block of `holes.json`):**
1 stud = 0.3 m. g = 32.7 studs/s². Rolling deceleration = 0.5 + 0.25·v studs/s². Rail restitution 0.63, bumper restitution 0.65.
Cup radius 0.5 stud, capture speed < 5.33 studs/s (1.6 m/s). The **max putt speed of 19.78 studs/s (5.9 m/s)** is derived so a full putt
rolls 60 studs (18 m) on flat felt. 60 studs is the longest single-stroke run the course asks for: the H6 and H9 ace lines are about 45 studs of travel
plus a climb and two deflections. The long holes (H8's long route is ~95 studs) are multi-shot by design.

**AI golfers.** Per stroke, the golfer aims at the furthest target it has line of sight to: the cup, else the hole's `ai_waypoints` for its
current zone. It hits for distance + carry, adding √(2gΔh) for climbs. Gaussian noise is applied per skill:
**good** aim σ 1.0°, power σ 5%; **average** aim σ 2.5°, power σ 12%.
The cap is 8 strokes, and hazards/escapes reset the ball to the stroke start with +1 stroke.

**Flags.** BROKEN = validator error, fuzz/AI escape, or the cup never reached. IMPOSSIBLE = good players capped >50%.
TRIVIAL = HIO >15% or avg < par−1. TOO-HARD = good avg > par+2. WARN:no-HIO-line = the brute-force search found no ace.

**Targets for this pass:** total par 25–28. HIO possible but rare: 0.2–10% for good players. Good average within par−0.7 … par+1. No BROKEN flags.

## Earlier iterations (old guessed physics, superseded)

Before the real values arrived, four rounds (r1–r4, snapshots `tools/out/holes-r1..r4.json`) ran with guessed physics
(0.28 m/stud, g 35, decel 1.2 + 0.06v, restitution 0.75, capture < 3.0). Those rounds:
- fixed two sim bugs: the off-felt check ran before wall collision, letting balls faster than 19 studs/s skip rails; and a gate engulfing the ball
  pushed it out along the wrong axis;
- replaced gentle 45° bank corners (which turned only 16 of 48 test shots) with steep 45°-pitch banks backed by a rail (35 of 48);
- moved AI waypoints off deflector centre-lines, made the H4 spinner a slow 2-arm bar, lowered the H4/H6/H9 ramps,
  moved H9's lantern bar to guard the heart well, added the H9 secret "Lantern Knot" teleport, added H2's rabbit-hole pit,
  and rebuilt H5 (wide tee shore) and H8 (shorter lane, smaller ring).

The r4 geometry is the starting point below.

## Round 1: r4 geometry under the real physics (before fixes)

Tag `p1`. Validator: 0 errors. Fuzz: 0 escapes. Physics tests: all pass.

| # | Hole | Par | Good avg | Good HIO | Good capped | Avg avg | Avg HIO | Avg capped | Haz/play (avg) | HIO-search hits | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lantern Gate | 2 | 1.97 | 3.1% | 0.0% | 2.14 | 7.3% | 0.0% | 0.00 | 189/34560 | ok |
| 2 | Acorn Ledge | 2 | 2.02 | 0.0% | 0.0% | 2.44 | 0.0% | 0.0% | 0.00 | 366/34560 | ok |
| 3 | Toadstool Row | 3 | 3.00 | 0.0% | 0.0% | 3.23 | 0.0% | 0.0% | 0.00 | refine 0/10920 | WARN:no-HIO-line |
| 4 | Spore Spinner | 3 | 3.76 | 1.1% | 1.4% | 4.09 | 0.8% | 2.5% | 0.00 | 98/276480 | ok |
| 5 | Rootbridge Crossing | 3 | 3.16 | 0.0% | 0.0% | 3.78 | 0.0% | 0.0% | 0.00 | 7/34560 | ok |
| 6 | Mill Wheel Run | 3 | 4.70 | 0.0% | 2.6% | 4.53 | 0.0% | 2.8% | 0.01 | refine 0/10920 | WARN:no-HIO-line |
| 7 | Cascade Steps | 3 | 2.91 | 0.0% | 0.1% | 3.07 | 0.0% | 0.0% | 0.01 | 59/276480 | WARN:timeouts |
| 8 | Firefly Hollow | 4 | 3.13 | 0.0% | 0.0% | 4.95 | 0.0% | 4.2% | 0.00 | 20/34560 | ok |
| 9 | Heart of the Grove | 4 | 3.37 | 1.9% | 0.9% | 3.73 | 9.3% | 0.8% | 0.00 | 1087/276480 | ok |
| | **Total** | **27** | **28.04** | | | **31.95** | | | | | |


**Problems found:**
- **No ace for good players** on H2, H3, H5, H6, H7 and H8. On H3 and H6 the brute force finds **no ace line at all**, because the higher
  speed-dependent drag (0.25·v) bleeds the long two-bank and three-deflection routes.
- **H6 too hard**: good 4.70 > par+1. Balls lose too much speed to the wheel and deflector boards and roll back down the ramp.
- **H8 too easy for good** (3.13 < par−0.7 = 3.3). The firefly ring is a near-automatic birdie.
- **H9 secret knot too generous**: average players ace 9.3%, because their wider tee spread wanders into the knot and its exit lines up with the cup.
- H7: a few timeouts (ball rocking on the side-sloped green against a rail).

## Round 2: fixes for real physics

Snapshot `holes-p2.json`, results `sim-p2.json`. Sim change: a ball that is nearly stopped (<0.3 studs/s) while pressed against a
rail or cliff now counts as at rest. Before, gravity on a side slope kept it "rolling" into the wall until the 30 s timeout (the H7 timeouts).

| Hole | Change | Why |
|---|---|---|
| H2 | Cup (0,−26) → (−2.4,−22), on the left-chute line. Good golfer's chute carry 4 → 6.5 | Good players had 0% aces. Putting the cup near the line a well-struck chute shot follows makes an ace possible from the tee |
| H3 | Whole hole compacted: lane 21.5 → 15.5, cross 20 → 17.5, leg/green shorter (path ~60 → ~46 studs). Cup (18,−27.5). Good tee shot planned to ride both banks (carry 40) | Brute force found **no ace line**: under 0.25·v drag a full putt cannot run two 45° banks over 60 studs |
| H5 | Re-laid with the tee in line with the root bridge (everything shifted −3.1 x). Cup (2.5,−35) | Good players had 0% aces. The risky line is now the straight tee shot across the rail-less bridge |
| H6 | Compacted: lane 16 → 12, flume 18.5 → 14.5, ramp rise 0.4 → 0.25, wheel moved to x 7.5. Cup (15.5,−21.5). Good tee shot planned at full power | Good avg 4.70 (> par+1), and no ace line: balls lost too much speed to two 0.63 deflections plus the climb |
| H7 | Cup (−3,−35.5) → (−2.5,−31), where tee shots that make the lower gap actually finish | 0% good aces |
| H8 | New **sliding root door** (slider, 2 studs/s over ±2.5) across the alcove mouth. Ring exit moved and the cup moved to the far corner (8,−43.5). Good golfer banks the tee shot into the ring | Good 3.13 < par−0.7: the ring was a free birdie |
| H9 | Secret knot radius 0.4 → 0.3, exit (21,−45.5) angled (0.15,−1) instead of straight at the cup | Average players aced 9.3% via the knot |

| # | Hole | Par | Good avg | Good HIO | Good capped | Avg avg | Avg HIO | Avg capped | Haz/play (avg) | HIO-search hits | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lantern Gate | 2 | 1.97 | 3.1% | 0.0% | 2.14 | 7.3% | 0.0% | 0.00 | 189/34560 | ok |
| 2 | Acorn Ledge | 2 | 2.21 | 12.6% | 0.0% | 2.43 | 9.2% | 0.0% | 0.01 | 235/34560 | ok |
| 3 | Toadstool Row | 3 | 2.00 | 0.5% | 0.0% | 3.32 | 0.0% | 0.0% | 0.00 | 32/34560 | TRIVIAL:good-avg<par-1 |
| 4 | Spore Spinner | 3 | 3.77 | 1.1% | 1.4% | 4.09 | 0.8% | 2.5% | 0.00 | 98/276480 | ok |
| 5 | Rootbridge Crossing | 3 | 2.20 | 0.0% | 0.0% | 3.81 | 0.0% | 0.0% | 0.00 | refine 9/10920 | ok |
| 6 | Mill Wheel Run | 3 | 3.75 | 0.0% | 1.4% | 3.70 | 0.0% | 0.0% | 0.01 | 164/276480 | ok |
| 7 | Cascade Steps | 3 | 2.82 | 0.5% | 0.1% | 2.87 | 1.7% | 0.0% | 0.01 | 97/276480 | WARN:timeouts |
| 8 | Firefly Hollow | 4 | 4.14 | 0.0% | 5.3% | 4.95 | 0.0% | 4.2% | 0.00 | 66/276480 | ok |
| 9 | Heart of the Grove | 4 | 3.40 | 0.8% | 0.9% | 3.85 | 6.2% | 1.1% | 0.00 | 824/276480 | ok |
| | **Total** | **27** | **26.24** | | | **31.17** | | | | | |


**Result vs Round 1:** H3 and H6 now have ace lines (32 and 164 grid hits). H6 good 4.70 → 3.75. H8 good 3.13 → 4.14. H9 average aces 9.3% → 6.2%.
**New problems:** H2 good aces 12.6% (>10%). H3 good 2.00 is TRIVIAL (the aggressive tee shot runs to ~2.7 studs from the cup).
H5 good 2.20 (< par−0.7). Still 0% good aces on H5, H6 and H8.

## Round 3: tuning, plus the ace-attempt golfer model

Snapshot `holes-p3.json`, results `sim-p3.json`.

**Golfer model change (made once, before this round, and fixed from here on).** The waypoint planner never attempts precise bank/timing
ace lines, so good-player ace rates were 0% on holes that do have ace lines. Skilled VR players do go for known aces, so now:
- **good golfers go for the hole's brute-force ace line on 30% of tee shots**;
- the line used is the most *robust* grid hit (the one with the most hitting neighbours within ±1° and ±0.6 studs/s), not an arbitrary one.

| Hole | Change | Why |
|---|---|---|
| H2 | Cup (−2.4,−22) → (−2.3,−22) | Sweep: −1.9 to −2.2 gave 0% aces, −2.3 gave ~9% (planner only) |
| H3 | Cup (18,−27.5) → (15.5,−30.5). New `toadstool_stool` bumper (1.6×1.5×1.6) at (16.8,−27.8). Good tee carry 40 → 24. New `green_in` waypoint for the leg zone | Good 2.00 was TRIVIAL |
| H5 | Root bridge narrowed 2.2 → 1.8. Cup (2.5,−35) → (1.5,−37) | Good 2.20 < par−0.7 |
| H6 | Mill wheel 3 → 2 paddles (blocked ~19% instead of ~28%) | Full-power tee shots stalled at the wheel |
| H8 | Ring exit livelier (speed ×1.2, min 4, max 8.5) | The aggressive bank-into-ring tee shot (carry 30) was tested and rejected: good 5.11, 23% capped. Kept carry 14 with the livelier exit |

| # | Hole | Par | Good avg | Good HIO | Good capped | Avg avg | Avg HIO | Avg capped | Haz/play (avg) | HIO-search hits | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lantern Gate | 2 | 1.79 | 20.9% | 0.0% | 2.14 | 7.3% | 0.0% | 0.00 | 189/34560 | TRIVIAL:good-HIO>15% |
| 2 | Acorn Ledge | 2 | 1.97 | 33.0% | 0.0% | 2.51 | 7.2% | 0.0% | 0.01 | 202/34560 | TRIVIAL:good-HIO>15% |
| 3 | Toadstool Row | 3 | 2.52 | 0.0% | 0.0% | 3.90 | 0.0% | 0.3% | 0.00 | refine 0/10920 | WARN:no-HIO-line |
| 4 | Spore Spinner | 3 | 3.80 | 2.8% | 1.4% | 4.09 | 0.8% | 2.5% | 0.00 | 98/276480 | ok |
| 5 | Rootbridge Crossing | 3 | 2.44 | 4.5% | 0.0% | 3.79 | 0.0% | 0.0% | 0.00 | 8/34560 | ok |
| 6 | Mill Wheel Run | 3 | 3.19 | 14.7% | 1.5% | 3.68 | 0.0% | 0.0% | 0.01 | 216/276480 | ok |
| 7 | Cascade Steps | 3 | 2.66 | 4.4% | 0.1% | 2.87 | 1.7% | 0.0% | 0.01 | 97/276480 | WARN:timeouts |
| 8 | Firefly Hollow | 4 | 3.15 | 11.1% | 3.6% | 4.95 | 0.0% | 4.2% | 0.00 | 610/276480 | ok |
| 9 | Heart of the Grove | 4 | 2.82 | 23.3% | 0.7% | 3.85 | 6.2% | 1.1% | 0.00 | 824/276480 | TRIVIAL:good-HIO>15%, TRIVIAL:good-avg<par-1 |
| | **Total** | **27** | **24.34** | | | **31.79** | | | | | |


**Problems found:** with ace attempts, **robust ace lines** show up. H1 (20.9%), H2 (33%) and H9 (23%) have lines a skilled player
can repeat. H6 (14.7%) and H8 (11.1%) are over the 10% target too. H3's new stool blocked its only ace line (WARN:no-HIO-line).
Shot-fan plots (`tools/out/debug-acelines.png`) show the causes:
- H1: the deflector turns any near-line into the same exit, and the cup sat on it.
- H2: chute + drop funnel.
- H9: the bank slid balls along the rail straight into the corner knot, whose exit pointed at the cup.

**Sanity check on the attempt model.** An ace attempt that remembers the line perfectly is unrealistic. Attempts now carry extra
line-memory error (±1.5° aim, ±8% power) on top of normal stroke noise. This was set once and not tuned per hole.

## Round 4: final (fixes for the robust ace lines)

Snapshot `holes-p4.json` (= final `holes.json`), results `sim-p4.json`. Each fix was picked from a sweep that re-ran the ace search
and the plays for every candidate (`tools/sweep.py`, `tools/try_variants.py`). The golfer model was unchanged.

| Hole | Change | Why / sweep evidence |
|---|---|---|
| H1 | Cup (−7.5,−33) → (−9.5,−26.5): the front-left corner of the green, tucked behind the lane-rail corner | Cup off the deflector's exit line. Aces 20.9% → 0.7%. A post bumper next to the old cup only got 10–18% |
| H2 | Lengthened: lane 18 → 22, lower green 14 → 18 deep, pit moved to z[−29,−31]. Cup (2.5,−35), far-right corner | At ~28 studs any ace line hits ~43% of attempts with line-memory error. Cup moves and wider/narrower chutes all stayed at 12–24%. Side-sloping the lower green broke the planner (up to 80% capped), so it was rejected. Lengthening got aces to 8.5% |
| H3 | Stool → (17,−28.8). Good tee carry 24 → 16 | Restores an ace line (3 grid hits) while keeping the stool's guard. Good 2.27 → 2.81 |
| H6 | Cup (15.5,−21.5) → (16.5,−22.5) | Aces 14.7% → 8.0%. Cups further away removed the line altogether |
| H8 | Ring radius 0.5 → 0.35 | Aces 11.1% → 5.7%, good 3.15 → 3.30 |
| H9 | Lantern Knot moved out of the corridor corner (5,−28.6) to open floor just past the gate (6.5,−23.0), r 0.3. Exit moved to the heart's SW corner (15,−52), aimed at the cup, speed ×1.0 clamp [4,10] | The corner knot caught balls sliding along the rail (23% aces). Exit angles pointed away from the cup removed the ace entirely. Open-floor knot: aces 3.2% |

| # | Hole | Par | Good avg | Good HIO | Good capped | Avg avg | Avg HIO | Avg capped | Haz/play (avg) | HIO-search hits | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lantern Gate | 2 | 2.02 | 0.7% | 0.0% | 2.45 | 0.0% | 0.0% | 0.00 | refine 43/10920 | ok |
| 2 | Acorn Ledge | 2 | 2.01 | 8.5% | 0.0% | 2.63 | 0.0% | 0.0% | 0.00 | 45/34560 | ok |
| 3 | Toadstool Row | 3 | 2.79 | 2.6% | 0.4% | 3.81 | 0.0% | 0.4% | 0.00 | 3/34560 | ok |
| 4 | Spore Spinner | 3 | 3.84 | 1.8% | 1.7% | 4.09 | 0.8% | 2.5% | 0.00 | 98/276480 | ok |
| 5 | Rootbridge Crossing | 3 | 2.49 | 2.2% | 0.0% | 3.79 | 0.0% | 0.0% | 0.00 | 8/34560 | ok |
| 6 | Mill Wheel Run | 3 | 3.18 | 8.0% | 0.9% | 3.63 | 0.0% | 0.0% | 0.01 | 46/276480 | ok |
| 7 | Cascade Steps | 3 | 2.74 | 2.1% | 0.1% | 2.87 | 1.7% | 0.0% | 0.01 | 97/276480 | WARN:timeouts |
| 8 | Firefly Hollow | 4 | 3.30 | 5.7% | 4.0% | 4.95 | 0.0% | 4.2% | 0.00 | 468/276480 | ok |
| 9 | Heart of the Grove | 4 | 3.50 | 3.2% | 0.9% | 4.02 | 1.4% | 1.6% | 0.00 | 459/276480 | ok |
| | **Total** | **27** | **25.87** | | | **32.25** | | | | | |


All targets met:
- Total par **27** (25–28).
- **Good** HIO 0.7–8.5% on every hole (0.2–10%), and every hole has a brute-force-confirmed ace line.
- **Good** average within par −0.7…+1 on every hole. Range: H8 +0.70 under par (shortcut) to H4 +0.84 over.
- No BROKEN/IMPOSSIBLE/TRIVIAL/TOO-HARD flags. Validator 0 errors, fuzz 0 escapes in 60k random shots per hole, 0 AI escapes.
- One remaining WARN: 1 timeout in 2000 average plays on H7 (the sliding log pinning a ball against a rail for 30 s). Negligible.

**Average golfers** total 32.25 (+5.3 over par), mostly because they take the safe routes on H5 and H8.

### Before/after (Round 1 real physics → Round 4)

| Hole | Par | Good avg | Good HIO | Avg avg | Avg HIO |
|---|---|---|---|---|---|
| 1 Lantern Gate | 2 | 1.97 → **2.02** | 3.1% → **0.7%** | 2.14 → **2.45** | 7.3% → **0.0%** |
| 2 Acorn Ledge | 2 | 2.02 → **2.01** | 0.0% → **8.5%** | 2.44 → **2.63** | 0.0% → **0.0%** |
| 3 Toadstool Row | 3 | 3.00 → **2.79** | 0.0% → **2.6%** | 3.23 → **3.81** | 0.0% → **0.0%** |
| 4 Spore Spinner | 3 | 3.76 → **3.84** | 1.1% → **1.8%** | 4.09 → **4.09** | 0.8% → **0.8%** |
| 5 Rootbridge Crossing | 3 | 3.16 → **2.49** | 0.0% → **2.2%** | 3.78 → **3.79** | 0.0% → **0.0%** |
| 6 Mill Wheel Run | 3 | 4.70 → **3.18** | 0.0% → **8.0%** | 4.53 → **3.63** | 0.0% → **0.0%** |
| 7 Cascade Steps | 3 | 2.91 → **2.74** | 0.0% → **2.1%** | 3.07 → **2.87** | 0.0% → **1.7%** |
| 8 Firefly Hollow | 4 | 3.13 → **3.30** | 0.0% → **5.7%** | 4.95 → **4.95** | 0.0% → **0.0%** |
| 9 Heart of the Grove | 4 | 3.37 → **3.50** | 1.9% → **3.2%** | 3.73 → **4.02** | 9.3% → **1.4%** |

Note: Round 1 good-HIO numbers come from the waypoint planner only. From Round 3 on, good golfers also go for the ace line on 30% of tee shots.

## Round 5: Playtest Bot notes 6–10 (2026-10-10)

Starting point: Round 4 geometry, re-run as tag `r5-base` (identical to `sim-p4.json`). Snapshots: `tools/out/holes-r5-start.json` (= Round 4),
`holes-r5a.json`, `holes-r5b.json` (final = `holes.json`); results `sim-r5-base.json`, `sim-r5a.json`, `sim-r5b.json`. Tool backups from before
this round are in `tools/out/r5/`. Physics constants are unchanged (checked in `sim.py`: `CUP_CAPTURE_SPEED = 5.33`, g 32.7, decel 0.5 + 0.25·v,
rails 0.63, bumpers 0.65, 0.3 m/stud).

**New targets (Playtest Bot):** a clear skill gap on every hole (good avg at least ~0.3 below average avg); average ≤ par+1.5 on every hole;
stroke-cap hits ≤ 1% (both skills); hole-in-ones possible but rare. Round 4 against them: skill gap failed on H4 (0.25) and H7 (0.13); cap failed on
H4 (1.7% / 2.5%), H8 (4.0% / 4.2%) and H9 average (1.6%).

### Sim and schema changes (made before tuning, kept fixed afterwards)

| Change | Why |
|---|---|
| Hazards may have `reset: "respawn"` + a `respawn` point: the ball gets +1 and is placed at rest on that point (sim outcome 5). Documented in the holes.json schema | Note 8 (H5) |
| New moving-part type `swing` (pendulum): pivot, horizontal axis, `amplitude_deg`, `period_s`, `phase`; angle(t) = amp·sin(2πt/period + phase). The blocker rotates about the hinge, and contact velocity is ω×r, as for rotors. The validator checks that the bob never cuts into the felt and reports the angle band where it can touch a ball | Note 10 (H9) |
| Rest rule: a ball that moved < 0.05 studs in the last 0.5 s at < 0.4 studs/s counts as at rest | Without it, a ball rocking in the crease of a V-shaped dip never "stopped" (every point is on a slope): 15k timeouts in the first H9 dip test |
| `cup_from` can be per skill (`{skill: zones}`) | H4: lets the good golfer play the side gap instead of firing at the flag through the carousel |
| `cup.flag` on every hole (pole height, diameter, banner, `top`, `collision: false`), plus a `cup_flag` decoration anchor. Anchors may carry `occluders` (solid boxes of the prop) and `facing` | Note 9 |
| `flag_los()` in `sim.py` (runs in every sim; `--los-only` for just the report): sightline from the tee eye (tee + 5.5) to the flag top, tested against rails/blocks, felt + the ground column under it, prop occluders, and moving blockers (% of their cycle) | Note 9 |
| `tools/teleport_check.py`: launches the ball from each teleport exit at speeds across its clamp range and reports finish / pass-over-cup speed / first rail-contact speed | Note 6 (H8 exit check) |
| `tools/sweep_r5.py` + `K()` tuning knobs and `LG_VARIANT`/`LG_OUT` in `build_holes.py`: variants are built to `tools/out/scratch-holes.json` and run through validator, ace search and 2000 plays per skill, without touching `holes.json` | Iteration tooling |
| `test_physics.py`: new tests for respawn, pendulum (blocks at rest, lifts clear when swung out) and dip settling. All 11 tests pass | - |

The golfer model (aim/power noise, ace attempts) is unchanged.

### Changes per hole (Round 5, `r5a`)

| Hole | Change | Why / sweep evidence (2000 plays per skill) |
|---|---|---|
| All | Flag on every cup: 7.5-stud pole (H9 8.0), 2.0 x 1.2 banner, no collision. Occluder boxes added to the solid props near sightlines | Note 9. Before (no flag, i.e. aiming at the cup itself), the cup was hidden by rails on H1, H3, H7, H8 and H9 and only grazed (+0.01) on H2. With flags, 8 of 9 are visible (table below) |
| H2 | Arrow signs on posts outside both rails at (±5.2, 0, -16.5) pointing into each chute ('Bold Line' with rabbit icon / 'Safe Line'), glowing leaf-arrow decals on the felt at (±2.75, 0, -17) | Note 9. Geometry unchanged, so the stats are identical |
| H4 | Spinner 36 → **30°/s**; arms **4.5 → 3.0** (bar 9 → 6 across; padded puffballs, bumper restitution 0.65 as for every moving blocker); side gaps between arm tips and rails are now 3.9 wide. Good golfers take the side gap (stop just past the carousel at (4.3, -25), then straight up the ramp); average golfers still fire at the flag through the carousel | Note 7. Slowing to 30°/s alone left average at 4.09 (arms 4.5). A first side-gap shot that ran through to the far NE pocket left good *worse* than average (good 4.10–4.39 with arms 3.5–4.5): the second shot went diagonally up the ramp and curled back. With the side shot stopping just past the carousel: arms 3.5 gave good 3.24 / avg 3.83 (gap +0.59) but average capped 1.1%; **arms 3.0: good 3.15 / avg 3.73 (gap +0.58), capped 0% / 0.7%** |
| H5 | Stream hazard: `reset: respawn` at the root-bridge entry (0, 0, -13.5); bridge width kept at **1.8** | Note 8. The note asked to "widen the bridge to ~1.5", but it is already 1.8 (the props list said 2.2, which was stale and is now fixed). A 1.5-wide variant (with respawn) was tested: good 2.59 vs 2.46, so no gain. With respawn, the share of good plays taking 5+ strokes fell from 3.4% to 1.2% (dist 5..8: 44/20/1/2 → 21/3/0/0); avg 2.49 → 2.46 |
| H7 | Log travel ±6 → **±7** (ends stop **0.5 stud short of each rail**, as built). Lower gap 3.5 → **2.5 wide (x 4..6.5)**. Cup (-2.5, -31) → **(-2.5, -36.5)** | Note (H7 log). The skill gap was 0.13–0.19 for every gap width because the sloped half of t3 funnels tee shots to within ~2 studs of the old cup. Moving the cup 5.5 deeper, past where the funnel drops the ball, makes the second putt real: gap +0.38 (with the 2.5 gap; 0.32 with 3.5). Cups further west killed the ace line (0–3 hits) |
| H8 | Ring radius 0.35 → **0.55**. The flat c1 run (9 studs) is removed: climb, top, connector and green all move 9 studs toward the tee. New banked plane `alcove_bank` on the alcove back wall (x 7.7..9, rising 0.5 east) feeds misses back out. Root door travel ±2.5 → **±4.0**, sliding into pockets in the root-knot walls. Exit speed factor 1.2 → **0.8**. Average waypoints re-fit to the shorter route (soft into the corner, then one committed climb shot that rides the top bank) | Note 6. With only the shortening, average got worse (5.45): the bank-turned ball stalled on the climb. Good capped 3.6–5.1% in every variant until the door was fixed: the 3.2-long door sliding ±2.5 across a 7-wide mouth blocked the ring line ~67% of the time, and a run of bounce-backs capped out. Door 2.4 long: caps 0.7%, but good 2.78 (TRIVIAL). Door ±4.0 + factor 0.8: **good 3.06 / avg 4.69, capped 0.4% / 0.1%** |
| H9 | Rotating lantern bar + post → **swinging lantern pendulum**: hinge (22, 8.96, -38.5), axis +Z, ±35°, period 4 s, bob 1.6 x 1.8 x 1.0 hanging 7 below the hinge, 0.06 above the felt at rest (touches a ball within ±16°). **Rolling dip** through the trunk tunnel: two opposing planar slopes, x 8..11 down 1.0 → 0.6 and x 11..14 back up. Root gate travel 0..1.2 @ 0.6 → **0..1.8 @ 0.9** (same 4 s cycle, open ~62% → ~70%). Cup (22, -50) → **(26, -52)**; the knot exit now aims at the cup automatically. Lantern Knot text fixed | Note 10. First try put the dip across the chamber in front of the well, with the pendulum over its crease: **60% capped**. Balls settled at the east end of the 16-wide crease and every shot out ran along the trough. Moving the pendulum to a flat lip still left 27–39% capped. A 7-wide tunnel dip with a straight approach works: good 3.77 / avg 4.05. The remaining average caps (1.5%) were gate bounce-backs: a corridor shot rebounding off the closed gate rides the landing bank back down the ramp. The longer gate travel fixes that (0.2%) but shrank the gap to 0.21; the deeper cup restores it: **good 3.74 / avg 4.12 (gap +0.38)** |

Lantern Knot text: it is at (6.5, 1.0, -23.0), **0.5 stud past (east of) the root gate at x = 6 and 1 stud in from the corridor's south rail (z = -22)**,
not "in the corridor's south-west corner". Its exit (15, -0.8, -52) is in the heart green's **north-west** corner (it was described as south-west).
Both the teleport `visual` text and the `lantern_knot` anchor in holes.json now say this.

H7 log: holes.json `moving_parts[log].range` = [-7, 7], `end_clearance` 0.5, visual text "log ends stop 0.5 studs short of each rail line (x=±10)".

### Round 6 (`r5b`): H8 average route

Round 5 met every target, but H8 average golfers were still at 4.69 (only -0.26) and never birdied. Changes:

| Hole | Change | Why / sweep evidence |
|---|---|---|
| H8 | Cup (8, -34.5) → **(4, 1.5, -37)**, nearer the end of the long route. Exit ring (-4, -47) → **(9, 1.5, -47)** (north-east corner), aimed at the cup. Exit speed factor 0.8 → **0.7**. Door travel ±4.0 → **±3.5** | Cup (4, -37) alone: avg 4.50 but good 2.99 (≈TRIVIAL). Moving the exit away and softening it: good 3.01. Door ±3.5 restores the challenge: **good 3.17 / avg 4.50, capped 0.8% / 0.1%, good HIO 4.9%**. Exit speed minimum 4 → 3 made no difference (ring entries are fast) |

**H8 teleport exit check** (`tools/teleport_check.py`, exit (9, 1.5, -47) toward the cup, every speed in the clamp [4, 8.5]): at 4.0–5.0 studs/s the
ball stops 1.2–4.0 studs short; at 5.5–8.5 it drops in, crossing the cup below the 5.33 capture speed. **No exit speed carries the ball past the cup
into the back rail**, so no backstop is needed. (For comparison, H9's secret knot at its top speeds of 9.3–10 crosses the cup at 6–6.7 studs/s,
rebounds off the east rail at 3.6–4.6 and settles 1.6–2.7 from the cup, still on the green.)

### Final stats (Round 4 → Round 6)

| # | Hole | Par | Good avg | Avg avg | Skill gap (avg − good) | Good HIO | Avg HIO | Good capped | Avg capped | Flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lantern Gate | 2 | 2.02 → 2.02 | 2.45 → 2.45 | 0.43 → **0.43** | 0.7% → 0.7% | 0.0% → 0.0% | 0.0% → 0.0% | 0.0% → 0.0% | ok |
| 2 | Acorn Ledge | 2 | 2.01 → 2.01 | 2.63 → 2.63 | 0.62 → **0.62** | 8.5% → 8.5% | 0.0% → 0.0% | 0.0% → 0.0% | 0.0% → 0.0% | ok |
| 3 | Toadstool Row | 3 | 2.79 → 2.79 | 3.81 → 3.81 | 1.02 → **1.02** | 2.6% → 2.6% | 0.0% → 0.0% | 0.4% → 0.4% | 0.4% → 0.4% | ok |
| 4 | Spore Spinner | 3 | 3.84 → **3.15** | 4.09 → **3.73** | 0.25 → **0.58** | 1.8% → 2.8% | 0.8% → 1.3% | 1.7% → **0.0%** | 2.5% → **0.7%** | ok |
| 5 | Rootbridge Crossing | 3 | 2.49 → **2.46** | 3.79 → 3.79 | 1.30 → **1.33** | 2.2% → 2.2% | 0.0% → 0.0% | 0.0% → 0.0% | 0.0% → 0.0% | ok |
| 6 | Mill Wheel Run | 3 | 3.18 → 3.15 | 3.63 → 3.62 | 0.45 → **0.47** | 8.0% → 8.0% | 0.0% → 0.0% | 0.9% → 0.9% | 0.0% → 0.0% | ok |
| 7 | Cascade Steps | 3 | 2.74 → **2.90** | 2.87 → **3.27** | 0.13 → **0.37** | 2.1% → 1.8% | 1.7% → 0.1% | 0.1% → 0.1% | 0.0% → 0.3% | WARN:timeouts (3/2000 avg) |
| 8 | Firefly Hollow | 4 | 3.30 → **3.17** | 4.95 → **4.50** | 1.65 → **1.33** | 5.7% → 4.9% | 0.0% → 0.0% | 4.0% → **0.8%** | 4.2% → **0.1%** | ok |
| 9 | Heart of the Grove | 4 | 3.50 → **3.74** | 4.02 → **4.12** | 0.52 → **0.38** | 3.2% → 3.0% | 1.4% → 0.2% | 0.9% → **0.1%** | 1.6% → **0.4%** | ok |
| | **Total** | **27** | **25.87 → 25.39** | **32.25 → 31.93** | | | | | | |

(H6's small change comes from the new rest rule: the same geometry with a slightly different settle point.)

Full sim table (`sim-r5b.json`):

| # | Hole | Par | Good avg | Good HIO | Good capped | Avg avg | Avg HIO | Avg capped | Haz/play (avg) | HIO-search hits | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lantern Gate | 2 | 2.02 | 0.7% | 0.0% | 2.45 | 0.0% | 0.0% | 0.00 | refine 43/10920 | ok |
| 2 | Acorn Ledge | 2 | 2.01 | 8.5% | 0.0% | 2.63 | 0.0% | 0.0% | 0.00 | 45/34560 | ok |
| 3 | Toadstool Row | 3 | 2.79 | 2.6% | 0.4% | 3.81 | 0.0% | 0.4% | 0.00 | 3/34560 | ok |
| 4 | Spore Spinner | 3 | 3.15 | 2.8% | 0.0% | 3.73 | 1.3% | 0.7% | 0.00 | 94/276480 | ok |
| 5 | Rootbridge Crossing | 3 | 2.46 | 2.2% | 0.0% | 3.79 | 0.0% | 0.0% | 0.00 | 8/34560 | ok |
| 6 | Mill Wheel Run | 3 | 3.15 | 8.0% | 0.9% | 3.62 | 0.0% | 0.0% | 0.01 | 46/276480 | ok |
| 7 | Cascade Steps | 3 | 2.90 | 1.8% | 0.1% | 3.27 | 0.1% | 0.3% | 0.01 | 155/276480 | WARN:timeouts |
| 8 | Firefly Hollow | 4 | 3.17 | 4.9% | 0.8% | 4.50 | 0.0% | 0.1% | 0.00 | 352/276480 | ok |
| 9 | Heart of the Grove | 4 | 3.74 | 3.0% | 0.1% | 4.12 | 0.2% | 0.4% | 0.00 | 55/276480 | ok |
| | **Total** | **27** | **25.39** | | | **31.93** | | | | | |

Targets: **skill gap ≥ 0.37 on every hole** (smallest: H7 0.37, H9 0.38); **average ≤ par+1.5 everywhere** (worst H3 +0.81, H4 +0.73);
**caps ≤ 0.9%** for both skills on every hole (worst: H6 good 0.9%, H8 good 0.8%); **good HIO 0.7–8.5%, average 0–1.3%**, with a brute-force ace line
on every hole. Validator 0 errors, fuzz 0 escapes in 60k random shots per hole, 0 AI escapes, physics tests pass.
H8 average golfers now par or better in 56% of plays (Round 4: 31%), and 1% birdie.

**Known, accepted:** H7 `WARN:timeouts`, 3 of 2000 average plays (Round 4: 1). A ball sitting exactly in the log's track gets batted into the east
rail, rolls back and is batted again, all along x, so it never leaves the track. With the log now reaching 0.5 from the rail this happens slightly more
often. In Roblox, solver noise and spin almost always knock the ball out of the track. RobloxDevBot should still have a stroke timeout (e.g. 20 s:
ball stays where it is, stroke counted) as a safety net for any soft-lock.

### Flag line of sight (tee eye 5.5 studs above the tee → flag top)

| # | Hole | Before (cup itself, no flag) | After (flag) | Min clearance after | Blocked by / notes |
|---|---|---|---|---|---|
| 1 | Lantern Gate | BLOCKED (rail, -0.53) | **VISIBLE**, 7.5 pole | +3.80 | - |
| 2 | Acorn Ledge | grazing (+0.01) | **VISIBLE**, 7.5 | +1.76 | Over the giant acorn (occluder) and the ledge |
| 3 | Toadstool Row | BLOCKED (rails) | BLOCKED, 7.5 | -6.04 | The stem house (cap up to y 12) sits on the S-bend, so the flag cannot be seen by design. The lantern string over the green entrance is the visual cue |
| 4 | Spore Spinner | grazing | **VISIBLE**, 7.5 | +5.50 | Spinner arms (1 high) never cross the sightline |
| 5 | Rootbridge Crossing | grazing | **VISIBLE**, 7.5 | +5.50 | - |
| 6 | Mill Wheel Run | grazing | **VISIBLE**, 7.5 | +4.98 | The mill wheel's paddles cross the sightline 44% of their cycle (spoked wheel, flag visible between paddles) |
| 7 | Cascade Steps | BLOCKED (t2 ledge) | **VISIBLE**, 7.5 | +5.35 | - |
| 8 | Firefly Hollow | BLOCKED (junction rail) | **VISIBLE**, 7.5 | +3.02 | - |
| 9 | Heart of the Grove | BLOCKED (chamber floor, rails) | **VISIBLE**, 8.0 pole | +0.20 | Just clears the root buttress over the trunk tunnel (solid y 4..6). Keep the buttress top ≤ y 6 (hole-local), or raise the pole |

### Rejected in this round (for the record)

- H9 dip across the 16-wide chamber with the pendulum over its crease, or over a flat lip: 27–60% capped (see above).
- H8 door shortened to 2.0–2.4: caps fixed but good 2.56–2.78 (TRIVIAL). H8 exit factor 0.7 with the old cup/exit: good 3.24 but only 15 ace grid hits (HIO 0.1%).
- H4 side-gap shot into the far NE pocket (arms 3.5–4.5): good 4.10–4.39, worse than average.
- H7 cups at (-5, -31), (-6, -29.5), (-5.5, -36): skill gap -0.11 to +0.16 and 0–3 ace lines.

## Round 7: Playtest Bot round 2 (v79), timing obstacles + H9 lanterns (2026-10-10)

**Note:** the H7 sliding log, the H8 sliding root door and the H9 lantern pendulum *never* blocked a shot at 3 test timings in-game, but
they are meant to be timing obstacles. Widen and/or slow them (longer dwell in the blocking position) so they block some shots at some
timings, never trap or pin the ball, and fix the H7 log soft-lock. Also: H9's green is now lit by 3 hanging amber lanterns.

**What the sim said before any change.** On the Round 6 geometry the new timing check (below) already showed all three obstacles blocking
the intended line at some timings: H7 46%, H8 **79%**, H9 29% of 24 phases. At the bot's own three timings (t = 0, T/3, 2T/3) each obstacle
blocked once in the sim. So "never blocked" in v79 points to a **sim ↔ game mismatch**, not only to obstacle size. RobloxDevBot should
check, in Studio, that the three moving parts have **CanCollide = true** and are moved every frame (CFrame/PrismaticConstraint), not just
tweened visuals over non-colliding parts, and that their motion follows holes.json (axis, range, speed, phase, and now `dwell`).
The retune below still makes each obstacle a clearer gate: a visible pause in the blocking position and an obvious open window.

Snapshots: `tools/out/holes-r7-start.json` (= Round 6), `holes-r7a.json` / `holes-r7-final.json`; `sim-r7-start.json` (= `sim-r5b.json`),
`sim-r7a.json` = `sim-r7-final.json`; timing checks `timing-r7-start.json` / `timing-r7-final.json`. Pre-round copies in `tools/out/r7/`.
One round was enough: no Round 8.

### Sim / schema / tool changes

| Change | Why |
|---|---|
| Slides may **pause**: `dwell: [{at, s}]` in holes.json (a stop at a range end pauses once per visit, an interior stop on both passes; `phase` = offset at t=0 on the forward pass). `period_s` = full cycle (info). `sim.py`: `slide_dwell_state()`, `cycle_period()`, `dwell_stops()`, `slide_time_at()`. Schema text updated | "Longer dwell in the blocking position" |
| `tools/timing_check.py` (new): fires the sim golfer's **noise-free planned shot** (same `plan()` as the playtest sim) at each obstacle at 24 evenly spaced phase offsets of its cycle plus the bot's 3 timings t = 0, T/3, 2T/3. It compares each shot with a "ghost" run with that obstacle removed. **touched** = paths diverge > 0.02; **blocked** = touched and never got past the obstacle line; **deflected** = touched but got past; **passed** = untouched; **trap** = 30 s timeout or at rest touching the blocker. Also checks the brute-force ace line, and fuzzes 100k random soft shots (0.3–8 studs/s, any aim/phase) started inside the obstacle's sweep area to find soft-locks | Note |
| `tools/sweep_r7.py` (new): `sweep_r5` + the timing check per variant | Iteration |
| `test_physics.py`: test 12, slider dwell profile (positions over a cycle, period incl. pauses). All 12 tests pass | - |
| `render_layout.py` / `write_notes.py` show pauses and cycle times; the pendulum touch band uses the turned bob's real width; `write_notes.py` can write single holes | Docs |

Intended lines used: **H7** the tee shot to the lower gap (aim 281°, 12.0 studs/s; crosses the log track at x ≈ 4.0). **H8** the tee bank
shot off the junction's north rail into the ring (aim 291.3°, 11.2 studs/s; crosses the door line at z ≈ -12.1). **H9** the chamber shot to
the well mouth (from where the planned chain stops in the chamber, (18.5, -25.0), aim 281.2°, 7.75 studs/s; passes under the pendulum at x ≈ 21.2).

### Changes per hole

| Hole | Part | Round 6 | Round 7 | Why / evidence |
|---|---|---|---|---|
| H7 | log size | 5 x 0.8 x 0.8, flat ends | **6 x 0.8 x 0.8, pointed 45° ends** (collision 5.2 box + two 0.566 x 0.8 x 0.566 boxes turned 45°) | The soft-lock: a ball in the log's track was batted along x against the rail forever (Round 6: 3/2000 average plays; the fuzz found **610 per 100k** soft shots in the track). Pointed ends alone: **0**. A flat-ended log with a bigger end gap + pauses also gave 0 in 20k but leaves the mechanism in place |
| H7 | travel / speed | ±7 at 5 studs/s, ends 0.5 from the rails | **±6 at 3.5 studs/s, ends 1.0 from the rails** | Slower = readable. Longer log keeps the east-end position across the gap line (x 3.0–9.0 covers the crossing at x ≈ 4) |
| H7 | dwell / period | none, 5.6 s | **1.0 s at the west end (gap line open), 1.5 s at the east end (log across the gap line); 9.36 s** | Longest pause in the blocking position. 24 phases: blocked 46%, passed 54%, 0 traps |
| H8 | door | 0.7 x 1 x 3.2, ping-pong −3.5..+3.5 at 2 studs/s, 7.0 s | **0.7 x 1 x 3.6; gate: closed (offset 0, centred on the ring line) 1.8 s → slides +4.0 into the south pocket at 3 studs/s → open 2.2 s → back; 6.67 s** | Round 6 blocked the intended line 79% of the time (too much for a timing gate; the bot never saw a block in-game, see above). Gate tuning (good avg / blocked %): dwell 1.5/2.5 → 2.88 / 46% (good < par−1 = TRIVIAL), 1.5/3.0 → 2.81 / 42%, 2.0/2.0 → 3.11 / 54%, 1.8/1.8 at 2.5 studs/s → 3.06 / 50% |
| H8 | ring radius | 0.55 | **0.45** | With a fair open window more ring shots get in; the smaller ring keeps good ≥ par−1: ring 0.45 + dwell 1.5/2.5 → 3.02; ring 0.5 + 1.8/2.2 → 3.08; **ring 0.45 + 1.8/2.2 → good 3.13 / avg 4.50, 50% blocked**. Exit position/speed unchanged (teleport exit check from Round 6 still holds) |
| H9 | pendulum bob | 1.6 x 1.8 x 1.0 box, square to the swing | **1.6 x 1.8 x 1.6 square lantern turned 30° about the vertical**: 1.6 → **2.19** wide across the swing; touch band ±16° → **±18°** (middle ~6.5 of the 8-stud mouth) | Widening a square-on bob (2.0–2.4 wide) created a new soft-lock: the ball rolls purely along the swing plane, is batted into the east rail and back forever (up to 154 per 100k fuzz shots). Turning the bob 45° fixed that, but its faces were then parallel to the 45° root deflector, so the ball bounced bob → deflector → bob (23 per 100k at a 4 s period). **30°: 0 per 150k at 4, 5 and 6 s** |
| H9 | swing | ±35°, 4 s (peak 55°/s) | **±30°, 5 s (peak 38°/s)** | Slower swing and more time inside the touch band. 24 phases: blocked/deflected 38%, passed 62%, 0 traps (±35° @ 5 s: 29%; ±30° @ 6 s: 25%) |
| H9 | hinge | y 8.96, bob 0.06 above the felt at rest | **y 8.996, bob 0.096 above the felt at rest** | A tilted bob's low corner dips (half-width)²/(2(L + h/2)) mid-swing. The rest gap is now computed so ≥ 0.02 of air stays under the corner (validator: min gap 0.021) |
| H9 | lanterns | "dozens of hanging lanterns" cluster anchor | **3 hanging amber lanterns** `amber_lantern_1..3` at (18.5, -47.5), (28.5, -46.5), (20.0, -51.5), 1.2 x 1.8 x 1.2, **bottoms at y 7.2 = 8 studs above the green felt**, chains up into the canopy | The game now lights the green with these 3. **Decoration only, no collision.** Measured clearances (box edge): ≥ **7.6** studs from every point the pendulum bob sweeps (x 17.1..26.9, y 1.02..4.26, z −39.6..−37.4), ≥ 6.3 north of its swing plane/chain/beam (z −38.5), ≥ **3.9** from the tee→flag sightline. They are LOS occluders and the flag stays **VISIBLE (+0.20, unchanged)**; 7.8 above the top of a ball, 2.4 m above the felt (clear of a VR player's head) |

### Timing check (24 evenly spaced phases per cycle; `tools/timing_check.py`)

Before (Round 6 geometry):

| Hole | Obstacle | Line | Period | Blocked | Deflected | Blocked+deflected | Passed | Traps | Bot timings t=0, T/3, 2T/3 | Fuzz soft-locks |
|---|---|---|---|---|---|---|---|---|---|---|
| H7 | log | intended | 5.6 s | 10/24 | 1/24 | **45.8%** | 54.2% | 0 | passed, passed, blocked | **610/100000** |
| H7 | log | ace | 5.6 s | 9/24 | 2/24 | **45.8%** | 54.2% | 0 | deflected, passed, deflected | - |
| H8 | root_door | intended | 7 s | 11/24 | 8/24 | **79.2%** | 20.8% | 0 | passed, blocked, deflected | 0/100000 |
| H8 | root_door | ace | 7 s | 12/24 | 1/24 | **54.2%** | 45.8% | 0 | passed, passed, blocked | - |
| H9 | lantern_pendulum | intended | 4 s | 3/24 | 4/24 | **29.2%** | 70.8% | 0 | passed, blocked, passed | 0/100000 |
| H9 | lantern_pendulum | ace | 4 s | 0/24 | 0/24 | **0%** | 100% | 0 | passed, passed, passed | - |

After (final):

| Hole | Obstacle | Line | Period | Blocked | Deflected | Blocked+deflected | Passed | Traps | Bot timings t=0, T/3, 2T/3 | Fuzz soft-locks |
|---|---|---|---|---|---|---|---|---|---|---|
| H7 | log | intended | 9.36 s | 11/24 | 0/24 | **45.8%** | 54.2% | 0 | blocked, passed, passed | **0/100000** |
| H7 | log | ace | 9.36 s | 7/24 | 2/24 | **37.5%** | 62.5% | 0 | passed, blocked, passed | - |
| H8 | root_door | intended | 6.67 s | 12/24 | 0/24 | **50%** | 50% | 0 | blocked, passed, passed | 0/100000 |
| H8 | root_door | ace | 6.67 s | 7/24 | 0/24 | **29.2%** | 70.8% | 0 | blocked, passed, passed | - |
| H9 | lantern_pendulum | intended | 5 s | 5/24 | 4/24 | **37.5%** | 62.5% | 0 | blocked, deflected, passed | 0/100000 |
| H9 | lantern_pendulum | ace | 5 s | 0/24 | 0/24 | **0%** | 100% | 0 | passed, passed, passed | - |

(The H9 ace line goes through the secret Lantern Knot teleport and never meets the pendulum. "Ace" rows = the hole's brute-force ace line
fired at every phase. All intended lines are now inside the 25–50% target, with 0 traps and 0 fuzz soft-locks.)

### Final stats (Round 6 → Round 7, 2000 plays per skill, same seeds)

| # | Hole | Par | Good avg | Avg avg | Skill gap | Good HIO | Avg HIO | Good capped | Avg capped | Flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lantern Gate | 2 | 2.02 | 2.45 | 0.43 | 0.7% | 0.0% | 0.0% | 0.0% | ok |
| 2 | Acorn Ledge | 2 | 2.01 | 2.63 | 0.62 | 8.5% | 0.0% | 0.0% | 0.0% | ok |
| 3 | Toadstool Row | 3 | 2.79 | 3.81 | 1.02 | 2.6% | 0.0% | 0.4% | 0.4% | ok |
| 4 | Spore Spinner | 3 | 3.15 | 3.73 | 0.58 | 2.8% | 1.3% | 0.0% | 0.7% | ok |
| 5 | Rootbridge Crossing | 3 | 2.46 | 3.79 | 1.33 | 2.2% | 0.0% | 0.0% | 0.0% | ok |
| 6 | Mill Wheel Run | 3 | 3.15 | 3.62 | 0.47 | 8.0% | 0.0% | 0.9% | 0.0% | ok |
| 7 | Cascade Steps | 3 | 2.90 → **2.95** | 3.27 → **3.40** | 0.37 → **0.45** | 1.8% → 2.2% | 0.1% → 0.1% | 0.1% → 0.1% | 0.3% → **0.2%** | WARN:timeouts → **ok** |
| 8 | Firefly Hollow | 4 | 3.17 → **3.13** | 4.50 → 4.50 | 1.33 → **1.37** | 4.9% → 6.2% | 0.0% → 0.0% | 0.8% → **0.3%** | 0.1% → 0.1% | ok |
| 9 | Heart of the Grove | 4 | 3.74 → **3.64** | 4.12 → **4.07** | 0.38 → **0.43** | 3.0% → 3.0% | 0.2% → 0.2% | 0.1% → 0.1% | 0.4% → **0.2%** | ok |
| | **Total** | **27** | **25.39 → 25.30** | **31.93 → 31.99** | | | | | | |

H1–H6 are unchanged (same geometry and seeds, identical numbers). Targets: skill gap ≥ 0.43 on every hole (smallest H1 and H9, 0.43);
average ≤ par+1.5 everywhere (worst H3 +0.81); caps ≤ 0.9% (H6 good 0.9%); good HIO 0.7–8.5%, average 0–1.3%, with an ace line on every hole
(H7 137, H8 235, H9 55 grid hits). **0 timeouts on every hole** (H7's soft-lock is gone). Validator 0 errors, fuzz 0 escapes, physics tests 12/12.

**H9 difficulty/readability:** good 3.64, average 4.07 (gap 0.43; Round 6 3.74 / 4.12). The slower 5 s swing is easier to read and to time,
so good players gain a little more than average ones. The pendulum still blocks or deflects 38% of fired chamber shots. The 3 amber lanterns
are decoration only: no collision, not in the physics, 8 studs above the felt and ≥ 7.6 studs from the pendulum sweep. They are included
as occluders in the flag sightline check, and the flag stays visible with the same +0.20 clearance (still set by the tunnel's root buttress).

World: `world/tools/validate.py` iteration 9 **CLEAN** (no felt, wall, tee or cup moved; walk 641 studs).

### What RobloxDevBot must rebuild

- **H7 log:** 6 long with pointed ends (collision 5.2 box + two 45°-turned 0.566 end boxes, or a wedge-ended union with the same footprint), range ±6, 3.5 studs/s,
  **pauses 1.0 s at −6 and 1.5 s at +6**, phase 0 = centre moving east (holes.json `dwell`, `period_s` 9.357).
- **H8 root door:** 3.6 long; offset range 0..+4.0 along +Z; **pauses 1.8 s at 0 (closed) and 2.2 s at +4.0 (open)**, 3 studs/s, t=0 = start of
  the closed pause; single pocket in the south root-knot wall. **Ring trigger radius 0.45** (glow disc 0.9).
- **H9 pendulum:** hinge y 8.996; ±30°, 5 s; bob 1.6 x 1.8 x 1.6 turned 30° about the vertical. **3 amber lanterns** (no collision) per `amber_lantern_1..3`.
- **All three:** check CanCollide and real per-frame motion (see the note at the top of this round). The sim says each blocks the intended line
  at about 38–50% of timings, so at 3 random timings a playtester should see at least one block 76–88% of the time.

### Rejected in this round

- H7 flat-ended log with pauses only (end gap 1.5, dwell 1.0/1.0): 0 soft-locks in 20k, but the batting mechanism remains. Pointed ends remove it.
- H8 gate without a ring change (dwell 1.5/2.5, 1.5/3.0, 1.5/3.0 at 4.2 travel): good 2.74–2.88 (TRIVIAL, < par−1). Ring 0.4: good 3.11, but it undoes most of Round 5's ring enlargement.
- H8 door range −4..0 (closing from the north): 58% blocked.
- H9 wider square-on bobs (2.0–2.4 wide, ±25–40°): fuzz soft-locks along the swing plane (0–154 per 100k, very sensitive to amplitude/period). Bob turned 45°: deflector retro-bounce at 4 s (23 per 100k).
