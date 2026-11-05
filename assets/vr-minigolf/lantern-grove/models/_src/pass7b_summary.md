# Lantern Grove props: pass 7b summary (2026-10-10): plants >= 1.5 studs clear of every rail

Brief: `_src/brief_pass7b.md`. Step log: `_src/pass7b_progress.md`. Before: `_src/manifest_before_pass7b.json`.
The pass-7b job stopped after the tee renders; the contact sheet, README and this summary were finished at the start of
pass 8 (18:08). No holes.json / world / fly files were edited.

**Result:** fitcheck **ALL PASS, 188 checks** (175 + 13 new). Saved as `_src/fitcheck_pass7b_validated.txt`.
Tee views re-rendered for all 9 holes (32 spp) + H1 top; `tee_contact_sheet.png` rebuilt; README updated.
H1 tee checked: no grass or bush is touching or leaning over the rails.

## Rule
- Plant set by category (`registry.CATEGORY` -> `manifest.props[].category`, `manifest.dressing.plant_props`):
  grass, ferns, bushes, toadstool/mushroom clumps, glow shrooms/roots, sapling. Trees, rocks, litter, fireflies excluded.
- `dressing_world.py`: exact 2D triangle-vs-wall-rectangle gap of the whole mesh at its transform; plants < 1.5 are
  nudged outward (same role, up to 3.5 studs) else removed. 3-stud tall-prop rule, keep-outs, 34k budget unchanged.
- `_src/fitcheck_pass7b.py`: independent check per hole + negative tests.

## Per hole (pass 7 -> pass 7b)
| Hole | Pass-7 violators | Min gap before -> after | Moved | Removed | Instances |
|---|---|---|---|---|---|
| H1 | 5 | 1.11 -> 1.73 | 5 | 0 | 48 -> 48 |
| H2 | 3 | 1.10 -> 1.60 | 2 | 1 red_leaf_bush (refilled elsewhere) | 42 -> 42 |
| H3 | 6 | 0.86 -> 1.51 | 7 | 0 | 41 -> 43 |
| H4 | 4 | 0.78 -> 1.57 | 4 | 0 | 37 -> 37 |
| H5 | 3 | 0.90 -> 1.56 | 4 | 0 | 34 -> 34 |
| H6 | 0 | 2.37 -> 2.37 | 0 | 0 | 16 -> 17 |
| H7 | 3 | 1.15 -> 1.59 | 3 | 2 orange_leaf_bush, red_leaf_bush | 25 -> 26 |
| H8 | 4 | 0.76 -> 1.64 | 2 | 5 grass_tuft, 2 glow_root_arch, 2 glow_shroom_patch | 29 -> 26 |
| H9 | 2 | 0.80 -> 1.62 | 3 | 1 toadstool_tall | 27 -> 30 |
Near fields all <= 34,000 (max H2 33,998).

## Changed FBX
All `fbx/dressing_hNN_*.fbx` re-exported (content changed on every hole except H6 cards). No prop meshes changed.
Manifest: `dressing.holes.*.instances` (+ `rail_gap` on plants), `stats.pass7b_vs_pass7`, `rules.plant_rail_clearance`,
`props[].category`.

## Open issues
- H8 lost 4 hollow props near the rails (now 26 instances); pass 8 boosts its glow instead.
- Pass-7 open issues still stand (holes.json flag sizes, thin H6, static fireflies, felt normal map in Studio).
