## Pass 7b: plants >= 1.5 studs clear of every rail (playtest: tall grass clipping the H1 rails)

Full log: `_src/pass7b_summary.md`.

**Rule `plant_rail_clearance`:** every dressing instance of a **plant** prop keeps its whole mesh footprint at least
**1.5 studs** (horizontal) from every rail and collision wall of every hole.
- **Measured on the real mesh:** every triangle of the prop at its instance transform, projected to XZ, against every
  wall rectangle. This is an exact 2D distance, not just the origin.
- **Plant set:** defined by prop category (`registry.CATEGORY`, written to `manifest.props[].category` and
  `manifest.dressing.plant_props`). `plant` = `grass_tuft`, `fern_clump`, `fern_clump_large`, `red_leaf_bush`,
  `orange_leaf_bush`, `gold_leaf_bush`, `red_bush_tall`, `toadstool_cluster`, `toadstool_tall`,
  `toadstool_orange_cluster`, `toadstool_trio_small`, `glowing_mushrooms`, `glow_shroom_patch`, `glow_root_arch` and
  `maple_sapling`.
- **Not plants:**
  - trees (`tree`): their trunks and everything below eye height already stay >= 3 studs from rails, and the canopy is
    meant to overhang;
  - rocks (`rock`), leaf litter (`litter`), fireflies (`fauna`), cards and structures.
- **Enforcement** (`dressing_world.py`): a plant that is too close is nudged **outward**, away from the nearest wall
  (same role, up to 3.5 studs, within ±90° of the outward direction); if no spot fits, it is removed.
  - The 3-stud tall-prop rule, keep-outs, grounding and the 34k near-field budget all still apply.
  - Each plant instance stores `rail_gap` (the exact gap, capped at 2.5).
- **Checked by** `_src/fitcheck_pass7b.py`, an independent implementation with negative tests: a grass tuft whose
  origin is 1.8 studs out but whose blades reach within 1.5 is flagged.
