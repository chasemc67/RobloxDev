# SL1 pass 4 implementation

Prepared the pass-4 pipeline in `C:\Users\chase\sl_spires`. Blender was **not launched**, as required. FBX, manifest, preview, reimport, fitcheck and DONE outputs are generated only when the runner is executed; none are claimed as validated or delivered now.

## Files

- `build_sl1_pass4.py`: copied pass-3 helpers and fixed SL1 geometry; builds only SL1 at baked scale 3.0 with the original root, axes and pivot. Adds low-frequency cap relief, three interior cap rings, uneven outlines, a lip and shadow ring. Radius-3 flat patches protect the A/B pylon footprints at unscaled heights 47.4 and 55.4. Warped strata boundary loops at boundary ?0.8 give both adjacent bands 18% darker rims using the approved palette. Five striped capped hoodoos use the new `SL1_spires` BD_VC mesh, behind the cable and hero/cascade foreground.
- `sl1_pass4_approved_sha256.json`: baseline hashes for all 11 approved files. The build checks this baseline at startup and snapshots it again for exit checks; changes cause exit 1.
- `fitcheck_sl1_pass4.py`: plain Python; checks triangle budget, fixed mesh metadata, mesh names, placement, motion endpoints, neon, scale, actual raycast pylon footprint heights, per-axis bbox bounds expanded by 10% of the original axis size, scenery flags, conservative full-face cable corridor clearance, reimport result and approved hashes. Writes `fitcheck_sl1_pass4.txt`, including per-mesh tris, and fails on exceptions.
- `make_sheet_sl1_pass4.py`: Pillow comparison sheet with before/after boardwalk renders, boardwalk silhouettes and 3/4 silhouettes.
- `run_sl1p4.ps1`: runs Blender 5.2 with `--render`, logs stdout/stderr separately, then runs fitcheck and sheet; writes `DONE_sl1p4.txt` containing `exit N`, with nonzero status on failure.

## Runtime outputs

`fbx_pass4/bd_sl1_sugarloaf_canyon_pass4.fbx`, `manifest_sl1_pass4.json`, `_src/reimport_sl1_pass4.json`, `fitcheck_sl1_pass4.txt`, `DONE_sl1p4.txt`, plus these `previews_pass4/` images:

- `SL1_boardwalk_eye.png`, `SL1_34.png`
- `SL1_before_boardwalk_eye.png`, `SL1_before_34.png` (approved FBX imported)
- `SL1_{before,after}_{boardwalk_eye,34}_silhouette.png` (literal black/white)
- `sheet_sl1_pass4_before_after.png`

The boardwalk camera uses exactly the pass-3 eye, target and FOV formula. Reimport starts in a fresh scene and compares mesh names, triangles and bboxes with the export metadata. The new manifest is the original SL1 entry with updated geometry/output fields and additional validation evidence; placement, neon and motion remain copied verbatim. No approved files are written.

## Verification performed

Python AST syntax checks passed for all three Python scripts; PowerShell parser check passed for the runner. SHA256 verification confirmed all 11 approved files unchanged. Static topology accounting estimates **14,126 triangles** (10,208 mesas, 3,160 spires, 758 fixed geometry), below 15,000. Runtime per-mesh counts and all Blender-dependent checks remain pending. Rendered sightlines and final visual quality need inspection after execution. Pillow is required for the sheet.

To execute later: `powershell -ExecutionPolicy Bypass -File _src/run_sl1p4.ps1`.
