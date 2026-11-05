# Sugarloaf Canyon: hole tools

Adapted from `../../lantern-grove/tools/` (the finished reference course). The physics and golfer model are the same:
1 stud = 0.3 m, g 32.7, rolling decel 0.5 + 0.25·v, rails 0.63, bumpers 0.65, cup capture < 5.33 studs/s, V_MAX 19.78.

| File | What it does |
|---|---|
| `build_holes.py` | **Source of truth** for `../holes.json` (18 holes). Placements come from `../world/world.json`; every geometry knob is a `K("name", default)`; `SC_VARIANT` / `SC_OUT` env vars build variants elsewhere. Ends with a fit check against the world.json pads |
| `geom.py` | Authoring helpers (rails with mitred corners, banks, bank walls, movers, teleports, offset polylines, octagons) |
| `sim.py` | Validator, escape fuzz, brute-force ace search, 2000 plays per skill, flag line of sight. `python3 tools/sim.py --tag p5` |
| `test_physics.py` | physics regression cases (including timed deck, quay lip and moving-contact rest handling) |
| `timing_check.py` | Timing obstacles (H6, H9, H11, H14, H17): 96 phases by default (also verify 120), stops vs kicks, Studio estimate = stops + 0.36 kicks, traps, soft-lock fuzz. `--fuzz 100000 --out out/timing-p5.json` |
| `teleport_check.py` | Exit-speed sweep for every teleport and the H11 lift |
| `sweep.py` | Variant sweeps through the `K()` knobs: validator + fuzz + ace search + plays (+ `--timing`) |
| `summarize.py` | Markdown stats table + per-hole target check for `out/sim-<tag>.json` |
| `debug_plays.py` | Traces AI plays over a hole: `python3 tools/debug_plays.py 13 average --k 6 --bad-only` |
| `render_layout.py` | `../hNN-layout.png` per hole and `../course-map.png` (over the canyon heightfield) |
| `write_notes.py` | `../hNN-notes.md` from holes.json + sim + timing results: `python3 tools/write_notes.py p5 --timing tools/out/timing-p5.json` |
| `make_sheets.py` | `../holes_layouts_sheet.jpg` |
| `out/` | Per-round snapshots `holes-<tag>.json`, `sim-<tag>.json`, `timing-<tag>.json`, sweep logs |

Round loop (see `../playtest-log.md`): edit `build_holes.py` → `python3 tools/build_holes.py` → `test_physics.py` → `sim.py --tag <t>` →
`timing_check.py --n 96 --fuzz 100000` and `--n 120` / `teleport_check.py` → `summarize.py <t>` → sweeps for anything off target → render, notes, sheet → `world/tools/build_world.py`
+ `validate.py "note"` (cups and pars flow into world.json).

Round p7 adds `audit_static_fuzz.py` to retain all outcomes (including timeouts) for 100,000 random shots per static hole, `check_p7_clearance.py` for dense phase-by-phase mover/static separation, `check_p7_cuts.py` for full-cycle cut/lip/pocket checks and `rest_audit.py` for fuzz endpoint pins, escapes, and H17 exclusion rests. Use `sim.py --tag p7 --n 2000 --fuzz 100000`. Geometry remains authored only in `build_holes.py`; the lift owns moving felt rather than a static lock floor.

Timing fuzz uses two independent 100,000-shot pools (seed 11 at 96 phases; seed 29 at 120), records escape/timeout/pinned/excluded rests, and excludes physically occupied starting points. The p7 target is 38–50% **pure stops** for H9/H14/H17; kicks and deflections remain separate. `sim.py` escape fuzz alone is not a soft-lock audit.
