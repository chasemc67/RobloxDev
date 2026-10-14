# Sugarloaf ground tiles, fix_zfight3: seam check (offline)

Run 2026-10-14 ~7:10 AM PT on the box with Blender 4.5 (FBX import) and numpy/scipy. 18 sets, 188 tiles. Nothing was opened in Studio, saved or published.

## Within each set: all 18 PASS

| Set | Tiles | Adjacent pairs | Seam verts | Max gap | Max step | Coplanar overlaps | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| h01_ground | 8 | 11 | 348 | 0.00000 | 0.00000 | 0 | PASS |
| h02_ground | 12 | 27 | 694 | 0.00000 | 0.00000 | 0 | PASS |
| h03_ground | 12 | 20 | 530 | 0.00000 | 0.00000 | 0 | PASS |
| h04_ground | 6 | 6 | 148 | 0.00000 | 0.00000 | 0 | PASS |
| h05_ground | 4 | 3 | 152 | 0.00000 | 0.00000 | 0 | PASS |
| h06_ground | 4 | 3 | 190 | 0.00000 | 0.00000 | 0 | PASS |
| h07_ground | 10 | 11 | 340 | 0.00000 | 0.00000 | 0 | PASS |
| h08_ground | 12 | 29 | 798 | 0.00000 | 0.00000 | 0 | PASS |
| h09_ground | 12 | 29 | 722 | 0.00000 | 0.00000 | 0 | PASS |
| h10_ground | 12 | 20 | 472 | 0.00000 | 0.00000 | 0 | PASS |
| h11_ground | 9 | 20 | 426 | 0.00000 | 0.00000 | 0 | PASS |
| h12_ground | 16 | 28 | 728 | 0.00000 | 0.00000 | 0 | PASS |
| h13_ground | 15 | 27 | 686 | 0.00000 | 0.00000 | 0 | PASS |
| h14_ground | 9 | 20 | 542 | 0.00000 | 0.00000 | 0 | PASS |
| h15_ground | 15 | 25 | 660 | 0.00000 | 0.00000 | 0 | PASS |
| h16_ground | 8 | 6 | 252 | 0.00000 | 0.00000 | 0 | PASS |
| h17_ground | 9 | 18 | 518 | 0.00000 | 0.00000 | 0 | PASS |
| h18_ground | 15 | 38 | 954 | 0.00000 | 0.00000 | 0 | PASS |

Every seam vertex on every tile lies exactly on the neighbour's boundary edge (gap 0.00000, step 0.00000), and no neighbouring tiles share coplanar overlapping triangles.

## Between sets (placed with layout.json): 9 tile pairs FLAG

21 tile pairs from neighbouring holes have overlapping placed bounding boxes. 9 of them have coplanar overlapping triangles (normals within 0.8 deg, plane gap under 0.005 studs, overlap above 1e-4 sq studs): 230 triangle pairs, about 21.2 sq studs in total. These are where the edges of two holes' ground slabs sit on top of each other at the same height, which can flash.

| Tile A | Tile B | Coplanar tri pairs | Area (sq studs) | Overlap box, world (min / max) |
|---|---|---:|---:|---|
| h13_ground_s14 | h14_ground_s10 | 96 | 8.8916 | [-311.0, 149.94, -219.64] / [-287.0, 150.45, -218.52] |
| h14_ground_s12 | h15_ground_s10 | 46 | 7.248 | [-311.0, 149.82, -135.64] / [-287.0, 150.43, -134.48] |
| h13_ground_s14 | h14_ground_s00 | 32 | 3.0229 | [-314.0, 149.94, -219.63] / [-311.0, 150.45, -218.52] |
| h14_ground_s22 | h15_ground_s10 | 8 | 0.7732 | [-287.0, 149.82, -135.64] / [-285.0, 150.31, -131.36] |
| h16_ground_s03 | h17_ground_s20 | 30 | 0.7191 | [-331.0, 189.83, 161.45] / [-305.58, 190.44, 171.37] |
| h07_ground_s10 | h08_ground_s03 | 6 | 0.212 | [339.0, 69.94, 60.55] / [349.0, 70.24, 64.66] |
| h07_ground_s11 | h08_ground_s13 | 6 | 0.1782 | [349.0, 69.92, 74.0] / [372.46, 70.42, 78.0] |
| h13_ground_s04 | h14_ground_s00 | 4 | 0.0753 | [-333.4, 149.8, -219.63] / [-314.0, 150.38, -215.42] |
| h17_ground_s00 | h18_ground_s21 | 2 | 0.054 | [-381.38, 189.78, 162.0] / [-380.4, 190.37, 187.0] |

The other 12 overlapping pairs only touch or cross without sharing a plane. Their full list is in seams.json.

## Limits of the method
- **Placement for the cross-set check** comes from layout.json: pos per hole ground, yaw 0, pivot = original, FBX axes converted to Roblox as X, Y = Blender Z, Z = -Blender Y. If the live Studio placement differs, the cross-set results change. With the Z axis flipped, 54 triangle pairs (9.3 sq studs) are still flagged, so the finding doesn't depend on that sign, but the exact pairs do.
- **Flicker in the engine** isn't confirmed. This is a geometry check only; a Studio or headset look at the flagged spots would confirm it.
- **Coplanarity is triangle-against-triangle.** Overlap area comes from projected polygon clipping. Thresholds: 0.005 studs plane gap and 0.9999 normal dot.
- **Gaps and steps** are measured from each tile's boundary vertices to the neighbour's nearest boundary edge, restricted to the overlap of the two tiles' bounding boxes. A gap in the middle of an edge with no vertex nearby would be missed, but the tiles share seam vertices by design, so this is unlikely.
- **Crossing between sets** (slabs cutting through each other at an angle) wasn't measured, and neither were the original non-tiled grounds or props. Ball tests were skipped because the grounds have collision off.

Files: seams.json (all pairs), seams-zflip.json (Z-axis sensitivity run), exp.py (Blender export), an.py (analysis).
