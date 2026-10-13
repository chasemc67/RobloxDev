# Stage af — H7–H18

| Hole | Cupdrops | Random | Slow | Escapes | Lost | Stuck | Reasons |
|---|---:|---:|---:|---:|---:|---:|---|
| H7 | 3/3 | 8/8 | 0/0 | 0 | 0 | 0 | none |
| H8 | 3/3 | 8/8 | 0/0 | 0 | 0 | 0 | none |
| H9 | 3/3 | 8/8 | 6/6 | 0 | 0 | 0 | none |
| H10 | 3/3 | 8/8 | 0/0 | 0 | 0 | 0 | none |
| H11 | 3/3 | 8/8 | 6/6 | 0 | 0 | 0 | none |
| H12 | 3/3 | 8/8 | 0/0 | 0 | 0 | 0 | none |
| H13 | 3/3 | 8/8 | 0/0 | 0 | 0 | 0 | none |
| H14 | 3/3 | 8/8 | 6/6 | 0 | 0 | 0 | none |
| H15 | 3/3 | 8/8 | 0/0 | 0 | 0 | 3 | seam, wedged |
| H16 | 3/3 | 8/8 | 0/0 | 0 | 0 | 0 | none |
| H17 | 3/3 | 8/8 | 6/6 | 0 | 0 | 0 | none |
| H18 | 3/3 | 8/8 | 0/0 | 0 | 0 | 0 | none |

## Imported triangles

| Prop | Triangles |
|---|---:|
| h07_rope_bridges | 1440 |
| h08_gumdrops | 348 |
| h09_pump_house | 844 |
| h10_sluice_flume | 648 |
| h11_lock_keeper_hut | 546 |
| h12_intake_tower | 1242 |
| h13_maze_rock | 720 |
| h14_cableway_trestle | 224 |
| h15_sugar_dune | 668 |
| h16_sinkhole_rim | 768 |
| h17_gnomon | 116 |
| h18_arch_gate | 264 |

Total: 7,828 triangles in 51 meshes; largest mesh 1,152 triangles. Missing manifest items: none.

## Proximity and sight lines

All new batch3/4 props are outside the 2.2-stud cup clearance. Conservative bounding-box hits below include inherited visuals; an enclosing box intersecting a cup does not prove triangle overlap. New props have CanQuery=false, so the requested query-based tee sight-line check ignores them.

- H7: tee ray → clear; exact felt/walls match: True.
  - Workspace.CourseSugarloaf.Hole7.StageAEVisuals.flag.flag__MintWhite: 0.0000 studs (OBB minimum).
- H8: tee ray → clear; exact felt/walls match: True.
  - Workspace.CourseSugarloaf.Hole8.StageAEVisuals.flag.flag__MintWhite: 0.0000 studs (OBB minimum).
  - Workspace.CourseSugarloaf.Hole8.StageAEVisuals.h08_ground.h08_ground__ClayBrick: 0.0000 studs (OBB minimum).
  - Workspace.CourseSugarloaf.Hole8.StageAEVisuals.h08_ground.h08_ground__Pebble: 0.0000 studs (OBB minimum).
  - Workspace.CourseSugarloaf.Hole8.StageAEVisuals.h08_ground.h08_ground__RedDirt: 0.0000 studs (OBB minimum).
  - Workspace.CourseSugarloaf.Hole8.StageAEVisuals.h08_ground.h08_ground__RedDirtLight: 0.0000 studs (OBB minimum).
  - Workspace.CourseSugarloaf.Hole8.StageAEVisuals.h08_ground.h08_ground__Strata: 0.0000 studs (OBB minimum).
- H9: tee ray → clear; exact felt/walls match: True.
  - Workspace.CourseSugarloaf.Hole9.StageAEVisuals.flag.flag__MintWhite: 0.0000 studs (OBB minimum).
- H10: tee ray → Workspace.CourseSugarloaf.Hole10.Geometry.Wall; exact felt/walls match: True.
  - Workspace.CourseSugarloaf.Hole10.StageAEVisuals.flag.flag__MintWhite: 0.0000 studs (OBB minimum).
- H11: tee ray → clear; exact felt/walls match: True.
  - Workspace.CourseSugarloaf.Hole11.StageAEVisuals.flag.flag__MintWhite: 0.0000 studs (OBB minimum).
- H12: tee ray → Workspace.CourseSugarloaf.Hole12.Geometry.Wall; exact felt/walls match: True.
  - Workspace.CourseSugarloaf.Hole12.StageAEVisuals.flag.flag__MintWhite: 0.0000 studs (OBB minimum).
- H13: tee ray → clear; exact felt/walls match: True.
  - Workspace.CourseSugarloaf.Hole13.StageAEVisuals.flag.flag__MintWhite: 0.0000 studs (OBB minimum).
- H14: tee ray → clear; exact felt/walls match: True.
  - Workspace.CourseSugarloaf.Hole14.StageAEVisuals.flag.flag__MintWhite: 0.0000 studs (OBB minimum).
- H15: tee ray → clear; exact felt/walls match: True.
  - Workspace.CourseSugarloaf.Hole15.StageAEVisuals.flag.flag__MintWhite: 0.0000 studs (OBB minimum).
- H16: tee ray → Workspace.CourseSugarloaf.Hole16.Geometry.Felt; exact felt/walls match: True.
  - Workspace.CourseSugarloaf.Hole16.StageAEVisuals.flag.flag__MintWhite: 0.0000 studs (OBB minimum).
- H17: tee ray → clear; exact felt/walls match: True.
  - Workspace.CourseSugarloaf.Hole17.Movers.Mover_shadow_arm.h17_shadow_arms.h17_shadow_arms__MintWhite: 0.8800 studs (OBB minimum).
  - Workspace.CourseSugarloaf.Hole17.Movers.Mover_shadow_arm.h17_shadow_arms.h17_shadow_arms__Slate: 0.0000 studs (OBB minimum).
  - Workspace.CourseSugarloaf.Hole17.StageAEVisuals.flag.flag__MintWhite: 0.0000 studs (OBB minimum).
- H18: tee ray → Workspace.CourseSugarloaf.Hole18.Geometry.Wall; exact felt/walls match: True.
  - Workspace.CourseSugarloaf.Hole18.StageAEVisuals.flag.flag__MintWhite: 0.0000 studs (OBB minimum).

## H11 measured timing

Offsets are world Y relative to the closed pivot. Samples use server-clock cycle phase, not elapsed time since Play started.

| Run | Target phase | Sample phase | Gate offset | Deck offset | Deck world position |
|---|---:|---:|---:|---:|---|
| before | 2 | 1.98535 | 0.000031 | -0.000038 | [150, 115.99996185302734, -5277] |
| before | 8 | 7.98508 | -1.300034 | 4.000031 | [150, 120.00003051757812, -5277] |
| before | 10.3 | 10.28517 | -1.300034 | -0.001892 | [150, 115.99810791015625, -5277] |
| after | 2 | 1.99924 | -1.300034 | -0.000038 | [150, 115.99996185302734, -5277] |
| after | 8 | 7.99885 | 0.000031 | 4.000214 | [150, 120.00021362304688, -5277] |
| after | 10.3 | 10.29941 | 0.000031 | -0.017784 | [150, 115.98221588134766, -5277] |

Local build checks: FAIL. Overall constraint result: FAIL. Importer automatically created 51 child RenderMesh assets with Upload to Roblox unchecked; strict zero-asset-upload constraint was not achieved. No explicit upload or place publish was performed.
