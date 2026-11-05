# Round p9: clearance + pad + hour-stone pass (continue from p8; read playtest-log.md Round p8 and _work/p8-report.md first)

Edit via tools/build_holes.py -> holes.json. Box only. Do NOT touch models/, lantern-grove/, or world/ except regenerating layouts/notes for affected holes. Do not post or send anything.

## Changes (all four required)

### 1. H9 windpump — tip clearance ≥ 0.15
Current axle height uses clearance 0.02 (`H9_PY = 0.02 + R_out`). Shrink the vane collision strips and/or raise the hub so the tip (lowest point of a downward vane) clears the felt by **at least 0.15** at every phase. Keep circular tip clipping. Target Studio-est. stop rate (stops + 0.36*kicks) **35–50%** on the intended line at both 96 and 120 phases. Ace line may be lower. 0 traps / soft-locks.

### 2. H14 ore_bucket — foot clearance ≥ 0.15 through ±9°
Current `H14_FOOT_GAP` targets ~0.03 at rest. Chamfer or raise the foot collider so its **lowest corner** clears the felt by **at least 0.15** at every angle in the ±9° swing (amplitude is already 9°). Keep the foot's north/south faces square to the shot line. Target Studio-est. stop rate **35–50%** on the intended line at 96 and 120. Ace line may stay 0%. 0 traps / soft-locks.

### 3. H7 player teleport pads
- **bridge2_exit** (exit pad on the green): move east so its **center x ≥ 4.15** (currently `sum(H7_B2)/2 ≈ 3.8`, overlapping the cup at x=3). Keep it on green felt, flush, optional, player-only, ball_teleport=False. Size stays [3, 0.02, 2] unless a small size tweak is needed to stay on felt.
- **Island pad** that sits on the respawn stone: the respawn stone at `[0, 0, zi0 - 1.5]` **keeps its spot**. Move the conflicting island teleport pad (bridge1_island and/or bridge2_island — whichever overlaps; currently bridge1_island is at `[sum(H7_B1)/2, zi0-1] = [0, -38]`, same as the stone) **≥ 2 studs away** to a clear spot on island felt, still flush and player-only. Prefer staying near the bridge landing so the VR comfort intent holds. Update matching `player_tp_*` anchors.

### 4. H17 hour stones — exact positions
Add **12 decorative hour stones**, each size **1.2 × 0.8 × 1.2** (sx, sy, sz), on a ring of **radius 12.5** around the post/gnomon at `(0, -36)`. Arms reach r_out=11.5, so 12.5 is outside the arm sweep. Place them on the outer border of the square dial (apron half-width 13).
- Collision-off decoration (`collidable=False`, `ball_collision=False`) **unless** a stone would sit on a rail — in that case either drop it or note it as rail-mounted with collision.
- Drop any stone whose footprint would land on playable felt in a way that blocks the cup/approach; prefer keeping all 12 on the ring if they sit outside the arm sweep and clear the play line (ring at r=12.5 is near the dial edge at ±13, so most should be fine as decoration on/near the border).
- Replace the vague `hour_stones` group anchor with **12 individual anchors** (or keep the group plus per-stone exact boxes) listing exact `[x, y, z]` centers. y = half-height 0.4 so they sit on the felt (top at 0.8), or document the chosen y.
- List the 12 exact positions in `_work/p9-report.md` and in the H17 notes.

## Re-sim (affected holes only)
Re-run for H7, H9, H14, H17 (and only those):
1. Rebuild: `python3 tools/build_holes.py` (or whatever the existing entry is — check tools/README.md).
2. `tools/timing_check.py` at **96 and 120** phases for H9, H14, H17 (H7 has no timing obstacle — skip timing for H7).
3. Soft-lock fuzz 100k at 96 and 120 for H9, H14, H17.
4. `tools/sim.py` plays (2000) for H7, H9, H14, H17 at least — confirm ace lines still exist, capped plays stay sane, good/average avgs still in band where previously specified.
5. Physics tests still ALL PASS.
6. Regenerate layouts/notes for H7/H9/H14/H17 and the layouts sheet if the tooling does that cheaply.

## Deliverables
- Updated `tools/build_holes.py` and rebuilt `holes.json`
- `playtest-log.md` — append **Round p9** with before/after clearance numbers, new pad positions, hour-stone table, timing tables for H9/H14/H17 at 96 & 120, fuzz results, play avgs for the four holes
- `_work/p9-report.md` — exact numbers for 3D Model Bot:
  - H9: new `H9_PY`, tip clearance, vane strip params, block rates
  - H14: new foot size/gap/chamfer, min clearance over ±9°, block rates
  - H7: exact new `bridge2_exit` and island pad positions (and which pad moved)
  - H17: table of 12 hour-stone centers `[x,y,z]`, size, collision flag; note any dropped
- Updated `h07-notes.md`, `h09-notes.md`, `h14-notes.md`, `h17-notes.md` (+ layouts if regenerated)

Work autonomously to completion. Do not ask questions. Prefer the smallest change that meets clearance and block-rate targets.
