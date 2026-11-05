# Round p9b: restore H9/H14 block rates while keeping ≥0.15 tip/corner clearance

p9 built H7 pads + H17 hour stones correctly. H9/H14 clearance was applied wrong: raising the whole hub / whole foot to 0.15 made block rate 0% (ball is only 0.16 tall, r=0.08). Read `_work/p9-report.md` and the clearance curves. Do NOT undo H7 pads or H17 stones.

## Correct approach (both targets required: tip/corner clearance ≥0.15 AND Studio-est. stop rate 35–50% at 96 and 120)

### H9 windpump
Do NOT raise the hub. Keep `H9_PY` near the p8 value (~4.12) so mid-vane still hits the ball.
**Shrink the collision strip outer radius** (and/or clip tips more aggressively) so when a vane points straight down its tip is ≥0.15 above the felt: `tip_clearance = H9_PY - R_out_collision ≥ 0.15`.
Visual mesh may keep a longer tip if noted; collision strips are what matter for the sim and for 3D Model Bot's collider.
Tune until intended-line Studio est. (stops + 0.36 kicks) is **35–50%** at both 96 and 120. Soft-lock fuzz 0.

### H14 ore_bucket
Keep a **low centre** that still blocks (gap under centre strips ≈ 0.05–0.07; curve says 0.06 → ~39%).
**Chamfer only the outer corners** so the lowest corner over the whole ±9° swing is ≥0.15 above the felt. The underside should be higher at |x| large and lower at x≈0 — NOT a uniform raise to 0.15.
North/south faces stay square to the shot line. Intended-line Studio est. **35–50%** at 96 and 120. Soft-lock fuzz 0. Validator should no longer say the bob never touches a ball.

## Process
1. Edit `tools/build_holes.py` only (keep H7/H17 p9 changes).
2. Rebuild holes.json.
3. Verify clearance: H9 tip ≥0.15; H14 min corner over ±9° ≥0.15; H14 centre low enough to contact the ball.
4. Re-run timing_check at 96 and 120 with 100k fuzz for H9 and H14 only.
5. Re-run sim.py plays for H9 and H14 (2000).
6. Update playtest-log.md: append **Round p9b** (or revise the p9 section) with the restored block rates.
7. Update `_work/p9-report.md` with final exact numbers for 3D Model Bot (replace the 0% H9/H14 section; keep H7/H17).
8. Refresh h09/h14 notes if needed.

Work autonomously to completion. Prefer smallest change. Box only; no models/, no lantern-grove/, no posting.
