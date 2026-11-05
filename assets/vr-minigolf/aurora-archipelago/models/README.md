# Aurora Archipelago models

## Batch 1

38 assets; 27,878 triangles; largest mesh 3,008. **ALL PASS: YES**, including exported geometry and FBX reimport. No remaining skipped pieces.

[Summary](_src/props_batch1/summary.md), [manifest](props_batch1_manifest.json), [fitcheck](fitcheck_props_batch1.txt), [contact sheet](previews/props_batch1/contact_sheet.jpg).

## Batch 2

36 assets; 26,790 triangles; largest mesh 4,416. **ALL PASS: YES**, including exported geometry and FBX reimport. No remaining skipped pieces.

[Summary](_src/props_batch2/summary.md), [manifest](props_batch2_manifest.json), [fitcheck](fitcheck_props_batch2.txt), [contact sheet](previews/props_batch2/contact_sheet.jpg).

## Skip-fix

18 requested props built/rebuilt against holes.json MD5 `2f1402fe19fc98a303c4e58dae680be9`. Existing exports, including the H12 wheel and H15 world waterfall, preserved byte for byte. Original overwritten artifacts backed up in each batch source folder under `_backup_pre_skipfix`. Updated world pivots, measured fitchecks, changed previews and silhouette comparisons, contact sheets and source scenes.

NOTE: H17 piers/bridge intentionally skin their own railed felt; H15 glass PlayerGuard parapet crosses the lip; H12 wheel retains its authorized 0.06 felt gap. H15 Great Frozen Falls stays at world base [20,36,-398], top [20,182,-398]; all 18 world-space checks pass. Both summaries contain current inventory, measurements and rebuild instructions.

Blender5.2 headless CPU only through `_src/run_blender.ps1`. FBX forward -Z/upY, scale1, exact base/hinge pivots, one mesh per material; decoration noncollidable. Gameplay colliders and motions remain owned by holes.json.


## Coral rev3

18 H7/H8 coral exports updated; overlapping lumpy crowns, flattened branching fans and neon tips. Fitcheck and FBX reimport ALL PASS. Other assets unchanged. See [_src/props_batch1/summary.md](_src/props_batch1/summary.md#coral-rev3) for triangle changes and footprint limits.


## Rev4

21 requested assets revised: 18 H7/H8 corals, H17 ice bridge, H15 ice parapet and H9 coral spit. Separate fan lobes and neon tips; bevelled snow-capped bridge rails/posts; uneven frosted ice blocks/icicles; pink/purple bumpy coral skirt. Every changed piece <=3000 tris. Both exported fitchecks and FBX reimport checks ALL PASS. Unrelated exports, anchors/pivots, exact H8 collider bases and existing exceptions preserved. Spit nose flare reduced to 0.18 and skirt top lowered below felt slab. Backups in each batch `_backup_pre_rev4`. See both summaries Rev4 sections for before/after triangles and measured clearances.


## Coral rev5

18 H7/H8 corals revised with flat forked paddles and 6-10 neon tips. Fitcheck and FBX reimport ALL PASS. Exact bases and placements preserved. See `_src/props_batch1/summary.md` for triangles, measured crown W:H, and geometric constraints. Rev4 files backed up in `_backup_rev4_corals/`.


## Coral rev6

18 H7/H8 corals revised with a 0.5H bare trunk and one lumpy rounded crown. Fitcheck and FBX reimport ALL PASS. Exact bases and placements preserved. See `_src/props_batch1/summary.md` for triangles, measured crown W:H, and geometric constraints. Rev5 files backed up in `_backup_rev5_corals/`.

## Batch 3 (H4, H6, H14, H18 final meshes, 2026-10-13)

19 assets, 14,700 triangles; the largest asset is 1,800 (h06_frosted_palms). Built against holes.json MD5 `fb913741b5dd4812b6d2318e258bcc46` (the 12:24 PM PT file, matched on the box and the PC). The fitcheck on the exported Blender triangles passes everything: >= 0.15 from rails and felt, 8-stud head room, the +-9 deg bell sweep, under 3k tris per asset.
[Manifest](props_batch3_manifest.json), [fitcheck](fitcheck_props_batch3.txt), previews in `previews/props_batch3/` (per asset: 34/front/eye, plus a context shot per hole as hNN_34.png), silhouette sheet `../silhouettes/sheet05-batch3-h04-h06-h14-h18.png`, source and conflicts in `_src/props_batch3/summary.md`.
Static props use no red or cream (snowpuff bellies are Snow, buoys are mint/violet). These replace the P1 placeholders for these holes (models/props/aa_h04..h18_*), which are left untouched. First pass, waiting on Game Art Bot's review.

- Rev 1 (2026-10-13 2:10 PM PT): 23 assets (4 new: h04_ice_channel_edge, h04_crystal_spire, h14_rail_bollards, h06_tee_lantern), 20,096 tris. Real Blender build plus a fresh-scene FBX reimport check (`_src/props_batch3/fbx_validation.json`), both pass. The exported fitcheck passes everything. Rev 0 is backed up in `_src/props_batch3/_backup_rev0_20261013_1341/`. summary.md provenance corrected.
- Rev 2 (2026-10-13 2:44 PM PT): h18_halo_arch tube 2.4 -> 4.8, thickened outward and upward only (inner edge unchanged, feet in place), 12-sided faceted with a lighter IceCore inner edge, 1,664 tris. h06_kettle_pool steam removed (particles instead), 572 tris. Selective Blender build plus FBX reimport check, both pass; the other 21 FBX are byte-identical. Rev 1 is backed up in `_src/props_batch3/_backup_rev1_*`.

## Polish pass (2026-10-13 PT): `_polish` folders
The approved FBXs are unchanged. `fbx/props_batch1/` and `fbx/props_batch3/`, their previews, `props_batch1_manifest.json`, `props_batch3_manifest.json`, `fitcheck_props_batch1.txt` and `fitcheck_props_batch3.txt` are the pre-polish approved versions, restored byte for byte from `_src/_backup_polish_20261013_1520/pre_polish.tar` and verified by SHA256. Import those as before.

The polish variants live only in separate folders and files. All polish exports go there.
- `fbx/props_batch1_polish/` (18 corals): h07_coral_w1-w5/e6-e10 888 tris each, h08_coral_1-7 900 each, h08_giant_coral 2,676. Game Art Bot approved them.
- `fbx/props_batch3_polish/` (10 assets): h04_ice_channel_edge 768, h14_buoy_float 680, h04_frosted_palm_a/b 804, h06_frosted_palms 2,412 (approved); h18_ramp_lanterns 528 with Glow pane #FFB040 Neon; h04/h06/h14/h18_snowpuffs 1,156/960/698/1,366 (rounded bodies and mounds, floating blocks removed).
- `previews/props_batch1_polish/`, `previews/props_batch3_polish/` (including `*_closeup_{34,side,top}.png` 2-stud snowpuff close-ups and `h18_ramp_lanterns_dusk.png`)
- `props_batch1_polish_manifest.json`, `props_batch3_polish_manifest.json` (polish ids only, paths point at the `_polish` folders)
- `fitcheck_props_batch1_polish.txt`, `fitcheck_props_batch3_polish.txt` (ALL PASS)
- Sheets: `../silhouettes/sheet06-polish-before-after.png`, `../silhouettes/sheet07-lanterns-snowpuff-closeups.png`

Same anchors, pivots and clearances as the approved versions, so a polish FBX can replace its approved counterpart once it's signed off. The H18 arch and H6 kettle pool aren't in the polish set.

## Overlap fixes (2026-10-13 PT): `fbx/props_fix_overlap/`
These fix Playtest Bot's cosmetic overlaps. The approved FBXs in props_batch1/2/3 are unchanged; RobloxDevBot can swap these in. Clearances are the true signed 3D distance from the exported mesh to the holes.json (MD5 fb913741…) rail and felt solids, with no skin exemptions.
- `h06_respawn_stone.fbx` (12 tris): lifted straight up 0.173, no tilt or rescale. Felt clearance -0.023 → 0.150; rail 8.60.
- `h18_crystal_chute.fbx` (1,093 tris, was 384): the rail skin is rebuilt as ice cladding offset 0.30 outward on the rail tops and outer faces, with no faces inside the 1.6 chute lane. Rail clearance -1.75 → 0.300; felt -1.06 → 0.150.
- No change needed: h04_ice_channel_edge (rail 0.175, felt 0.675, approved 48-tri version) and h14_rail_bollards (rail 0.40, felt 0.90).
- Manifest `props_fix_overlap_manifest.json`, fitcheck `fitcheck_props_fix_overlap.txt` (ALL PASS), re-import `_src/fix_overlap/fbx_validation.json` (pass), previews `previews/props_fix_overlap/`, sheet `../silhouettes/sheet08-overlap-fixes.png`, source `_src/fix_overlap/`.
- Clearance audit of the approved assets (`_src/fix_overlap/clearance_before.md`), not fixed yet: h02_lintel_left/mid/right and h02_rookery_drift 0.110 from rails; h10_bobsled_hut 0.125 from snowwall1; h15_lip_ice 0.000 from lip_lane felt (touching).
