# SRV-132 movers pass 5 (p9b)

Steps 1-2 + first fitcheck: Claude Code claude-opus-5-5; remainder: Codex.

Source of truth: in/holes.json; SHA256 57c1162513139bcbbd9de286cb18a7fb1d9d74fa25b6e0b934f834ac5b6a29bc. Inputs unchanged. All 34 exports round-trip PASS; full fitcheck ALL PASS.

## Changes

H7 pads use the exact p9b positions; exit cup notch removed. Respawn sandstone marker is .8 x .02 x .8, base-centre pivot [0,0,-38.5], static with no red/cream. H17 nine separate numbered stones: XII/I/III/IV/VII/VIII/IX/X/XI; no II/V/VI. XII/III/IX collide and remain unchanged. Six decorative stones have only their inward vertical corner chamfered (.48 along both adjoining edges), inside the exact 1.2 x .8 x 1.2 box.
H9 collision-only mesh contains the exact 48 strips, clipped to r 4.06; visual r .6..4.1 stays collision OFF. H14 collision-only foot contains the exact 14 strips. Skid underside follows the strip bottoms, with raised outer corners; upper skid and rivet vertices may sit above the local strip underside within the bucket footprint as allowed by the addendum. Full sweep confirms the visual never falls below the collider. Unaffected exports preserved.

## Clearances and angles

H9 collider minimum 0.05999982 at 171.5 deg (refined 171.502 deg); visual 0.02000009 at 17 deg, art only. H14 centre strips 0.06015487 at +/-2.5 deg, rest 0.06125031; outer corners 0.15021156 at +/-5.9 deg. Approved .06 override applies only to H9/H14 blocking colliders.
Respawn-to-pad gaps: bridge1_entry 12.1, bridge1_island 2.6, bridge2_island 4.1, bridge2_exit 19.1; nearest rail rope_rail6 1.6; no island pad overlap. Exit cup-rim gap .15.
Hour-stone rail minimum 0.26000201; decorative minimum 0.26558484 (XI, 310 deg; VIII also 40 deg). Exact per-stone angles and per-prop results are in fitcheck_results_pass5.json.

Full checks include unchanged props: rotors .5 deg over 360; bucket .05 deg over +/-9 plus period sampling; H6/H11 timing and approved cuts. Round-trip checks cover mesh counts, triangles, bounding boxes, zero local mesh origins, material merging, embedded textures, and <20k triangles per MeshPart.

## Motion and import

motion.lua unchanged. Both H9 meshes reuse M.windpump / M.windpumpCFrame (20 deg/s, 18 s, +Z, pivot [0,4.12,-17.75]). Both H14 meshes reuse M.oreBucket / M.oreBucketCFrame (+/-9 deg, 4 s, +Z, pivot [0,10.35,-24]). H17 arms/heads retain M.shadowArm. Import at scale 1; FBX -Z forward / Y up; Blender +Y = Roblox -Z. One MeshPart per material. Collision-only meshes: Transparency 1, CanCollide ON, CastShadow OFF. Visual vanes OFF; only XII/III/IX hour stones ON.

## FBX list, triangle totals and pivots

| FBX (relative to out) | Tris | MeshParts | Hole-local pivot | Collision |
|---|---:|---:|---|---|
| fbx/h06_sluice_gate.fbx | 300 | 4 | [0, 0.0, -28.0] | False |
| fbx/h06_sluice_frame.fbx | 476 | 3 | [0, 0, -28] | False |
| fbx/h11_lock_gate.fbx | 180 | 4 | [0, 0.0, -21.25] | False |
| fbx/h11_lock_lift.fbx | 276 | 3 | [0, 0, -25] | False |
| fbx/h11_lock_chamber.fbx | 1684 | 6 | [0, 0, -23] | False |
| fbx/h11_quay_lip.fbx | 72 | 2 | [0, 3.5, -25.45] | False |
| fbx/h09_windpump_vanes.fbx | 520 | 4 | [0, 4.12, -17.75] | False |
| fbx/h09_windpump_hub.fbx | 280 | 4 | [0, 4.12, -17.75] | False |
| fbx/h14_ore_bucket.fbx | 666 | 5 | [0.0, 10.35, -24.0] | False |
| fbx/h14_cableway_trestle.fbx | 380 | 4 | [0, 0, -24.0] | False |
| fbx/h17_shadow_arms.fbx | 336 | 3 | [0.0, 0.0, -36.0] | False |
| fbx/h17_shadow_arm_head_0.fbx | 84 | 3 | [0.0, 0.0, -36.0] | False |
| fbx/h17_shadow_arm_head_90.fbx | 84 | 3 | [0.0, 0.0, -36.0] | False |
| fbx/h17_shadow_arm_head_180.fbx | 84 | 3 | [0.0, 0.0, -36.0] | False |
| fbx/h17_shadow_arm_head_270.fbx | 84 | 3 | [0.0, 0.0, -36.0] | False |
| fbx/h17_plinth.fbx | 1008 | 5 | [0, 0, -36] | False |
| fbx/h07_bridge_parapets.fbx | 912 | 3 | [0, 0, -42] | False |
| fbx/h07_bridge_skirts.fbx | 48 | 1 | [0, 0, -42] | False |
| fbx/h07_gap_floor_mist.fbx | 24 | 2 | [0, -4.25, -42] | False |
| fbx/h07_teleport_pads.fbx | 60 | 2 | [0.0, 0, -25] | False |
| fbx/h07_teleport_pad_exit.fbx | 60 | 2 | [5.15, 0, -59] | False |
| fbx/dam_crest_parapets.fbx | 80 | 2 | [0, 115.7, -305] | False |
| fbx/h09_windpump_vanes_collision.fbx | 568 | 1 | [0, 4.12, -17.75] | True |
| fbx/h14_ore_bucket_foot_collision.fbx | 166 | 1 | [0.0, 10.35, -24.0] | True |
| fbx/h07_island_respawn_stone.fbx | 136 | 2 | [0, 0, -38.5] | False |
| fbx/h17_hour_stone_XII.fbx | 84 | 2 | [0.0, 0.0, -48.5] | True |
| fbx/h17_hour_stone_I.fbx | 52 | 2 | [6.25, 0.0, -46.8253] | False |
| fbx/h17_hour_stone_III.fbx | 72 | 2 | [12.5, 0.0, -36.0] | True |
| fbx/h17_hour_stone_IV.fbx | 74 | 2 | [10.8253, 0.0, -29.75] | False |
| fbx/h17_hour_stone_VII.fbx | 86 | 2 | [-6.25, 0.0, -25.1747] | False |
| fbx/h17_hour_stone_VIII.fbx | 98 | 2 | [-10.8253, 0.0, -29.75] | False |
| fbx/h17_hour_stone_IX.fbx | 72 | 2 | [-12.5, 0.0, -36.0] | True |
| fbx/h17_hour_stone_X.fbx | 64 | 2 | [-10.8253, 0.0, -42.25] | False |
| fbx/h17_hour_stone_XI.fbx | 76 | 2 | [-6.25, 0.0, -46.8253] | False |

## Previews

18 Cycles OptiX views plus contact_sheet_pass5.png, inspected; one framing fix for marker and bucket foot views. Eye height 5 studs; H7 pad assembly and tee, H17 ring eye/top/chamfer and tee, H9 vanes 0/45 with collider overlay and tee, H14 foot/skid -9/0/+9 close-ups and assembly views plus tee. Cyan wire overlay is diagnostic only.
- previews/cycles/pass5/h07_exit_pad_34.png
- previews/cycles/pass5/h07_respawn_pads_34.png
- previews/cycles/pass5/h07_respawn_pads_eye.png
- previews/cycles/pass5/h07_tee_eye.png
- previews/cycles/pass5/h09_tee_eye.png
- previews/cycles/pass5/h09_vanes_0_overlay.png
- previews/cycles/pass5/h09_vanes_45_overlay.png
- previews/cycles/pass5/h14_bucket_-9_34.png
- previews/cycles/pass5/h14_bucket_-9_foot_close.png
- previews/cycles/pass5/h14_bucket_0_34.png
- previews/cycles/pass5/h14_bucket_0_foot_close.png
- previews/cycles/pass5/h14_bucket_9_34.png
- previews/cycles/pass5/h14_bucket_9_foot_close.png
- previews/cycles/pass5/h14_tee_eye.png
- previews/cycles/pass5/h17_decorative_chamfer_34.png
- previews/cycles/pass5/h17_ring_eye.png
- previews/cycles/pass5/h17_ring_top.png
- previews/cycles/pass5/h17_tee_eye.png
- previews/cycles/pass5/contact_sheet_pass5.png

## Spec questions

1. Game Art Bot: exact decorative hour-stone boxes clear the arm blocker sweep by only .04105264, below .15. Per addendum, visual inward-corner chamfers now clear by .26558484; collision remains OFF. Rail stones remain exact and clear by .26000201.
2. Game Art Bot: bridge2_exit exact pad box touches rope_rail13 and rail18 at z=-58 (gap 0). Mesh containment is verified; classified JUNCTION INHERITED per addendum. Flush .02 player pad, no ball collision; position [5.15,0,-59] retained.
3. Source marker thickness is .02 (holes.json), despite the brief describing a low sandstone stone; source dimensions retained.

## Files and execution

Generators: registry_movers.py, gen_pass5.py, gen_p5_profile.py, build_movers.py. Validation: fitcheck_pass5.py, fitcheck_results_pass5.json, fitcheck_movers_pass5_validated.txt, verify_exports_pass5.py, export_verification_pass5.json. Rendering: render_pc_pass5.py, render_batch_pass5.py, render_fix_pass5.py. All Blender invocations used blender_pass4.ps1 sequentially. No Roblox Studio access. No Blender process remains.