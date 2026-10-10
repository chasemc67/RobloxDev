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
