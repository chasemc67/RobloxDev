# Pass 6 progress (Round-5 holes.json v2: flags, new props, changed moving parts, H9 bar -> pendulum)

- [x] Step 0 (2026-10-10 13:47): started; manifest snapshot -> _src/manifest_before_pass6.json. Reading sources.
- [x] Step 1 (13:47-14:25): read sources + diff Round-4 -> v2 holes.json (tools/out/holes-r5-start.json). New module
  _src/props_pass6.py (cup_flag_h01..09, h2_chute_sign_left/right, h2_chute_arrow_decal, h4_side_gap_post, h5_respawn_stone,
  h8_alcove_bank_cladding, h8_door_pocket, h9_pendulum_root_beam, h9_tunnel_dip_trim); props_moving: H4 bar 2.3 padded
  arms @30, H7 log +-7, H8 door +-3.5, H9 gate 0..1.8 @0.9, NEW h9_lantern_pendulum (swing), REMOVED h9_lantern_bar +
  h9_lantern_post_static (FBX + previews deleted). Hero fixes: firefly ring entry (R 0.85 ring, 1.1 glow disc), exit ring
  -> (9,1.5,-47) yaw -26.57, root_arch c2 -> z -22, H8 glowing_mushrooms off the c2 felt, H7 gap posts x 3.75/6.75, H9
  tunnel arch top <= y 6 (LOS). lglib FlagRed; dressing_lib.sweep_vols handles 'swing'. build_all --only 29 props OK
  (no-render); render run started (/tmp/p6/build1.log).
- [x] Step 2 (14:25-15:05): dressing_world.py pass-6 changes: pendulum spot beside the hinge (off the swing plane), accent
  rings out to 9 studs (moved H8 cup: only room 7.5-9 out), pass6_vs_pass5 stats, H7 priority (first in the seed
  round-robin + 14 cheap ground-cover / 3 mid props placed pre-seed). Tried a 7000-tri H7 reserve (H6 -12 props, H7 +5)
  and a 10.5k foreign-share cap (H6 -8, H7 +1; H8's near field binds all of H7): both reverted/disabled. Final run
  (dw4): H7 13 -> 25 instances, H6 25 -> 19 (lost 5 small ground-cover + 1 tree), H8 cup lanterns 2, all spots clear.
  fitcheck_pass6.py (exec'd by fitcheck.py) written; world_fitcheck.py negative test retargeted to the pendulum.
- [x] Step 3 (15:05-15:35): fitcheck iteration 1: 4 FAILs -> fixes: heart_lantern_cluster raised to y 7.5 (it BLOCKED the
  H9 tee->flag sightline at y 1.0..7.07), entry ring gap 100 -> 120 deg + motes >= 1 above felt, beam legs out to x
  12.4 / 31.6 (were 0.05 from a rail), envelope check ignores geometry under the felt (well rim). dressing_world re-run
  (dw5) + fitcheck: ALL PASS (168 checks) -> _src/fitcheck.txt = _src/fitcheck_pass6_validated.txt.
  Renders started: assembly_world --views tee,top --samples 32, all 9 holes (/tmp/p6/asm1.log).
- [x] Step 4 (to 14:27 box clock; earlier step times above were estimates): tee + top views for all 9 holes rendered
  (32 spp). Reviewed H1/H7/H8/H9: flags readable, H9 pendulum + beam + raised lantern cluster read, H8 door pockets OK.
  Next: full build.sh (all props + lantern_grove_props.blend + dressing + fitcheck + docs + tee sheet).
- [x] Step 5 (14:28-14:36): full build.sh: 114 props rebuilt (previews, manifest, lantern_grove_props.blend), dressing_world
  (identical numbers), fitcheck ALL PASS (168), README + contact_sheet + tee_contact_sheet (all 9, pass-6 title).
- [x] Step 6: _src/pass6_summary.md written; README pass-6 section (_src/pass6_readme.md via make_docs); repo skill
  blender-asset-pipeline gained 2 lessons (v2 diff + LOS/pendulum, zero-sum near-field budgets). DONE.
