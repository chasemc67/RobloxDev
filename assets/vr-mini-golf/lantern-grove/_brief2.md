CONTINUE the Lantern Grove job from where you are (files on disk: holes.json, layouts, tools/sim.py, build_holes.py, out/holes-r1..r4, sim-r1..r3). Do NOT restart.

UPDATE from RobloxDevBot - use the game's REAL physics everywhere, replacing earlier guesses:
- 1 stud = 0.3 m (not 0.28). Fix all meter conversions in docs/layouts.
- gravity 32.7 studs/s^2
- rolling deceleration = 0.5 + 0.25*speed studs/s^2 (speed in studs/s)
- walls restitution 0.63, bumpers 0.65
- cup captures ball when speed < 5.33 studs/s (1.6 m/s) inside cup radius
Put these in sim.py as constants (and in holes.json schema "physics" block). Derive max putt speed so a max putt rolls ~ the longest hole needs; state it.

Then, saving progress after each step:
1. Rerun sim + validator with real physics. Write playtest-log.md: Round 1 = the state with real physics (before fixes), per-hole stats table (avg strokes good/average, HIO %, capped %, flags). Mention the earlier old-physics iterations r1-r4 briefly.
2. Fix holes.json issues (via build_holes.py), rerun = Round 2, log changes+before/after. Fix again = Round 3. At least 2 full fix rounds. Targets: total par 25-28, HIO possible but rare (0.2%-10% for good), good golfer avg within par-0.7..par+1, no broken flags.
3. Re-render all hNN-layout.png and course-map.png from the final holes.json.
4. Write course.md, hNN-notes.md (h01..h09, each with a "## Concept prompt" paragraph for an image generator describing the tee-height VR view), props.md.
Keep the final printed summary short: per-hole name/par/gimmick, final stats table, changes per round.
