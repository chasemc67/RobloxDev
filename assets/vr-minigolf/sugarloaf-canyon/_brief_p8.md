# Round p8: H11 retune + validator tweak (continue from p7 state; read _work/p7-report.md first)
Edit via tools/build_holes.py -> holes.json. Box only; don't touch models/ or lantern-grove.
H11 targets: timing block rate 35-50% (stops) at 96 and 120 phases; good golfer avg 2.3-4.0; average golfer avg <=4.5; capped plays <3% for both; 0 traps/escapes/timeouts/pinned rests (fuzz 100k at 96 and 120).
Hard rules: gate closed whenever the deck is off the bottom (>=0.3 s margin each side); quay lip flush the entire time the deck is level at the top (sink 0.1s before arrival, rise 0.1s after descent starts is fine); top dwell >=2.0 s; lip top = quay_rail20 height; >=0.15 clearance kept for all cuts.
Options in order - try 1 first, only move on if it fails:
 1. Shorten cycle: rise and descend ~1.0-1.2 s each, cycle ~6-7 s.
 2. Indexed gate: gate rises only when a ball is actually on the deck (trigger-based). If chosen, document it as an engine requirement for RobloxDevBot.
 3. Widen the approach so blocked shots return to an easy re-putt.
Re-run: ride-off shots (lift down/mid/top), max-power lip shots, gate-top/sill retention cases, timing_check at 96 and 120, fuzz, full sim.py (2000 plays) for H11 at least (full course if cheap), summarize.
World: in world validator drop the Old Sugarloaf visibility requirement for the H17 and H18 tees (dome unchanged); note it in world/validation.md; re-run validate.py so it is clean.
Update holes.json, h11-notes.md, h11-layout.png, holes_layouts_sheet.jpg, course-map if changed, playtest-log.md (Round p8). Write _work/p8-report.md: which option(s) used, final H11 timing table (gate open/rise/closed/lower, deck rise/top dwell/descend, lip flush window, margins), before(p7)/after stats, ride-off/lip results, world validation result, any engine requirements.
