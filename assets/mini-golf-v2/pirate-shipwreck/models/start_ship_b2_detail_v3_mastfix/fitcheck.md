# start_ship_b2_detail_v3 - COL_Mast_Main fix: fitcheck (measured)

Source: ORIGINAL v3 release `start_ship_b2_detail_v3/out/start_ship_v3.blend` (local copy `original_v3.blend`, sha256 `87b319a5b6308c1d7d3deaac91b4b4e16b651572ac569a14606a8446442cc92f`). Output `out/start_ship_v3_mastfix.blend` (sha256 `e5a6f20340ff90cb959d5910206f2b1e3427fe7c491ac32236134e605f4c2979`). All values measured by `src/verify.py`.

**Hard checks: PASS**

## Collision delta (the only change)
- `COL_Mast_Main` (mesh datablock `COL_Mast_Main`, material ['Collision']): 8 vertex positions replaced by the donor values (4 move, 4 stay). Origin matrix identical (identity rotation, translation (10.000, -26.730, 82.266) Blender); faces, edges and all other attributes identical.
- Length along the 18 deg mast axis: **157.0000 -> 98.3000** (delta -58.7000). Tilt from vertical 18.000 deg (unchanged). Cross-section 5.0000 x 5.0000 (unchanged; top = bottom).
- Bottom 4 vertices bit-identical to v3. Bottom centre Roblox local (10.000, 7.608, 2.472).
- **Top centre Roblox local: old (10.000, 156.924, 50.988) -> new (10.000, 101.097, 32.849)** (delta (0.000, -55.827, -18.139)); Roblox world (Y + 0.6): old (10.000, 157.524, 50.988) -> new (10.000, 101.697, 32.849).
- Highest collider point Roblox Y: local 157.697 -> 101.870 (world 158.297 -> 102.470).
- Roblox local bbox: old (7.500, 6.836, 0.094) .. (12.500, 157.697, 53.365) -> new (7.500, 6.836, 0.094) .. (12.500, 101.870, 35.226)

| vertex | part | old Roblox local | new Roblox local | moved (studs) |
|---|---|---|---|---|
| 0 | bottom | (7.500, 6.836, 4.850) | (7.500, 6.836, 4.850) | 0.0000 |
| 1 | top | (7.500, 156.152, 53.365) | (7.500, 100.325, 35.226) | 58.7000 |
| 2 | bottom | (7.500, 8.381, 0.094) | (7.500, 8.381, 0.094) | 0.0000 |
| 3 | top | (7.500, 157.697, 48.610) | (7.500, 101.870, 30.471) | 58.7000 |
| 4 | bottom | (12.500, 6.836, 4.850) | (12.500, 6.836, 4.850) | 0.0000 |
| 5 | top | (12.500, 156.152, 53.365) | (12.500, 100.325, 35.226) | 58.7000 |
| 6 | bottom | (12.500, 8.381, 0.094) | (12.500, 8.381, 0.094) | 0.0000 |
| 7 | top | (12.500, 157.697, 48.610) | (12.500, 101.870, 30.471) | 58.7000 |

## Unchanged (byte-identical: geometry, every mesh attribute incl. UVs and material indices, material slots, world transform, name, datablock, collection)
- Visual + ramps + props meshes: **28 / 28** identical; 49405 tris total, largest Rigging 7282.
- Colliders: 190 names identical; the other **189 / 189** byte-identical.
- Materials (node trees), packed palette image, collections, unit scale identical: True. Datablock counts identical: True.

## Anchors (exact)
| empty | Roblox local | Roblox world (Y + 0.6) | exact |
|---|---|---|---|
| Spawn | (-120.000, 24.000, 2.500) | (-120.000, 24.600, 2.500) | True |
| Tee1 | (-120.000, 24.400, 37.000) | (-120.000, 25.000, 37.000) | True |
| RampStart | (-120.000, 24.000, 62.500) | (-120.000, 24.600, 62.500) | True |
| CupRef | (-175.700, 0.000, 212.370) | (-175.700, 0.600, 212.370) | True |

## FBX re-import (each file imported into an empty scene)
| file | objects | tris | names | origins | tris match |
|---|---|---|---|---|---|
| start_ship_b2_visual.fbx | 32 | 49405 | True | True | True |
| start_ship_b2_col.fbx | 190 | 2280 | True | True | True |
| RampFlight1_own_origin.fbx | 1 | 300 | True | True | True |
| RampLanding_own_origin.fbx | 1 | 184 | True | True | True |
| RampFlight2_own_origin.fbx | 1 | 288 | True | True | True |

- col FBX `COL_Mast_Main` world vertices match the blend: True (max diff 1.239776611328125e-05).
