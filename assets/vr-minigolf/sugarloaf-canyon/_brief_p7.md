# Round p7: Sugarloaf layout revisions (from Playtest Bot review)
Working dir: /workspace/RobloxDev/assets/vr-minigolf/sugarloaf-canyon/. Read tools/README.md, playtest-log.md (latest rounds), course.md, and the review at
/workspace/writerbot/vr-minigolf-post/playtest-bot/sugarloaf-layout-review/review.md fully. Edit geometry ONLY via tools/build_holes.py (holes.json is generated, source of truth). Box only. Do not touch lantern-grove or models/.
Tasks:
1. H17 Sundial: bigger arms or a third arm; target 38-50% blocked BY STOPS at >=96 timings; no ball may rest within 7 studs of the centre post (fix rest points near (4.3,-34.4) at t0~9.1s/24.1s, e.g. tilt/exclusion slope); 0 traps.
2. H9 Windmill: widen vanes 1.8->~2.4 or slow rotor; 38-50% overall, sane rate on ace line too, at >=96 timings.
3. H14 Ore Bucket: resize bucket/foot so it stops rather than deflects (stops dominant 38-50%, deflections low); either close the 256.5deg ace bypass or make it the intended, signposted safe line - decide and document.
4. Make 96 the default phase count in tools/timing_check.py (and any sweeps); re-run ALL movers (H6, H9, H11 gate+lift, H14, H17) at >=96 (try 120 too). 0 traps, 0 soft-locks.
5. H2: remove the left tunnel roof (open-top, roof only at portals ok) or ensure >=8 stud head clearance; widen left tunnel to >=3; raise right-tunnel lanterns to >=8 studs. Make average golfer par-or-better rate ~35%+ (gentler dead end/long route).
6. H4: par 3 (course par 54), keep all targets for par 3.
7. VR comfort: solid parapets + side skirts on the H7 rope bridges and the dam crest walk (crest >=8 wide, tall solid parapet e.g. >=3.5 studs), mist/floor under H7 gap, teleport points at each end of bridges/crest. Put exact sizes/positions in holes.json (H7) and world/world.json (dam crest).
8. world/world.json (via world/tools build script if that's the source - check world/README.md): add landmark "mine-head" at (134, ground, 392) east of H2; retune sun so from Sugarloaf Crown it sets inside the far arch (arch bearing 277deg, elev -12..1deg): sun bearing ~277, elevation ~-3.
Then: test_physics.py, full sim.py --tag p7 (2000 plays), fuzz 100k (0 traps/escapes/soft-locks), teleport_check, summarize, world build + validate.py. Re-render changed hNN-layout.png, course-map.png, holes_layouts_sheet.jpg; regenerate hNN-notes.md (write_notes.py p7 --timing ...); append a "Round p7" section to playtest-log.md with per-change numbers.
Finally write _work/p7-report.md: per-change before/after numbers; new mover dims (H9 vanes, H14 bucket/foot/arm/pivot, H17 arms) for 3D Model Bot; parapet/skirt/teleport sizes+positions; anything missed and why.

## ADDENDUM (supersedes conflicting items above)
A. Sun: world.json IN-GAME sun = golden hour, ~25deg elevation from the west (bearing ~270-277). Store the arch-aligned sun (bearing 277, elevation +2deg, inside arch 277 / -12..1... use +2 per lead, note it sits just above arch top 1deg if so and flag) as a SEPARATE hero-render-only entry (e.g. "hero_render_sun"), not the game sun.
B. Fold in 3D Model Bot's approved mover collision cuts (models/_src/movers/movers_pass2_summary.md - read it) into build_holes.py:
 - H6: pocket through rail5 AND rock18 for the sluice gate slide.
 - H11 gate: slot in the lock felt plus relief at tips of rails 4/5/7/8 (and felt_approach if needed).
 - H11 lift: moving deck carries felt+collision instead of static felt_lock; real gap in quay_rail20 where deck meets quay (plus rail6/felt_quay seam relief).
 - Keep >=0.15 stud clearance between movers and all static geometry. Model these in the sim; re-run H6/H11 timing at >=96 (and 120) phases, confirm 0 stuck balls/traps/soft-locks and that cuts don't open escapes. Report the exact cut boxes.
A previous run was interrupted early; check what is already changed and continue rather than redo.

## ADDENDUM 2 (H11 quay lip + extra checks) - Codex: re-read this file before finishing
- H11: close the quay_rail20 gap with a visible raised lip, 0.4 studs tall, spanning the full gap, red/cream striped like the lift bands, as a MOVING part in holes.json. It is up (blocking) whenever the deck is not fully raised, and sinks flush only while the deck is fully up. Keep >=0.15 clearance.
- In the >=96-phase timing rerun, add shots aimed through that gap with the lift down and mid-travel; confirm none roll off the quay.
- Run H6 with the rail5/rock18 pocket and the gate CLOSED; confirm no escape through the pocket.

## ADDENDUM 3 (overrides Addendum 2 lip height)
- H11 quay lip height = SAME height as quay_rail20 beside the gap (rail20 spans y 3.5..5, so lip top at y=5 / flush with rail top), NOT 0.4. Still sinks flush only while the deck is fully up.
- Add several max-power (V_MAX 19.78) shots straight at the lip (lift down and mid-travel); confirm none hop it or leave the quay.

## ADDENDUM 4 (props.md mismatch list - see end of props.md)
- H11 timing conflict: lift ride needs >=3.5 s but gate closed only 2.8 s; make the gate hold closed through the full lift ride plus margin; re-run H11 timing at >=96.
- world.json: fix stale cup/walkway heights for H10, H15, H16, H18 to match holes.json; dedupe H3 ranger station and H12 intake tower (use hole anchors).
- H6 gate notes vs JSON: JSON is truth, update notes.
- Add route-arrow anchors for H3 and H13 (in build_holes.py).
- Update course.md/notes: H7 respawn, H8 hump count, H10/H16 drop 3.6, H18 speed factor 0.7; flag colour in course.md = #e03c31.
- LAST: copy props.md to props-full.md, then trim props.md to a short priority list (~15 KB) for 3D Model Bot, reflecting the p7 dims.

## ADDENDUM 5 (world.json terrain)
- Add terrain feature for the Old Sugarloaf dome: center (80, 18, -130), radius 72, type "superellipse_dome", formula string "y = 18 + 110*sqrt(max(0, 1-(r/72)^4))", params {base:18, height:110, radius:72, exponent:4}.
- Old Sugarloaf landmark base Y = 18 (fix stale 207.1). Re-run world validator.
- In p7-report.md, list the H11 gate timing numbers explicitly (period, down/up/hold windows, lift ride window, margin, block % at 96/120, traps).

## ADDENDUM 6 (H11 lip window fix - overrides earlier lip timing)
- The lip is currently flush only ~7.5-7.65 s (0.15 s): too short. Make it flush for the whole time the deck is fully raised and level with the quay: sink 0.1 s BEFORE the deck reaches the top, rise only 0.1 s AFTER the deck starts to drop.
- If the deck top dwell is < ~2 s, lengthen it to >= 2.5 s within the 10.6 s period, keeping the gate closed through the entire ride with >= 0.5 s margin each side.
- Re-sim ride-off shots and max-power lip shots at >=96 phases. In p7-report.md give exact phase windows: deck rise/top dwell/descend, lip down/up, gate up/down, margins.
