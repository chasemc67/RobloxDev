# Pass 7b progress (plant/grass dressing >= 1.5 studs footprint clearance from every rail/wall)

- [x] Step 0 (16:23): started; pass 7 confirmed finished (summary, tee renders, sheet, README present); manifest snapshot -> _src/manifest_before_pass7b.json. Reading sources.
- [x] Step 1 (16:26): plant set defined by category in registry.py (CATEGORY / category(); plant = grass, ferns, bushes,
  toadstool/mushroom clumps, glow shrooms/roots, sapling; trees/rocks/litter/fireflies excluded; manifest props[].category).
  dressing_world.py: rail_gap_tris() exact 2D tri-vs-wall-rect distance (SAT + vertex/edge), evaluate() rejects
  plant_near_rail (< 1.5), try_with_nudge nudges plants OUTWARD (gradient of rail_dist, +-90 deg, r 0.5..3.5) else
  removed; instance rail_gap; stats.pass7b_vs_pass7; manifest rules.plant_rail_clearance. Run dw1: /tmp/p7b/dw1.log
- [x] Step 2 (16:29): dw1 OK (139 s). Pass-7 plant violators (exact gap < 1.5): H1 5 (min 1.11), H2 3, H3 6 (0.86), H4 4
  (0.78), H5 3, H6 0, H7 3, H8 4 (0.76), H9 2 (0.80) = 30. After: min gap >= 1.51 every hole. H8 hollow 17 -> 14 (all 4
  kinds, 7 alcove). Near fields all <= 34k. Running fitcheck: /tmp/p7b/fc1.log
- [x] Step 3 (16:32): fitcheck run 1: 1 FAIL (manifest rail_gap vs fitcheck on a far H9 fern: both exact only up to
  2.5 because of the wall pre-filter) -> rail_gap capped at 2.5 in both. dw2 + fitcheck run 2: ALL PASS (188 = 175 +
  13 new: plant set, 9 per-hole plant_rail_clearance, 3 negative/positive tests). Saved fitcheck_pass7b_validated.txt.
  Rendering tee views all 9 (32 spp) + H1 top: /tmp/p7b/asm.log
- [x] Step 4 (18:10, finished by pass 8): tee renders were done; contact sheet + README rebuilt, H1 tee checked (no grass at rails), pass7b_summary.md written. DONE.
