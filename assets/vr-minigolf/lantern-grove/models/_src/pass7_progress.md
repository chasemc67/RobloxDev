# Pass 7 progress (cup flags legible from tee, H8 Firefly Hollow dressing, darker felt with stronger nap)

- [x] Step 0 (2026-10-10 14:50): started; manifest snapshot -> _src/manifest_before_pass7.json. Reading sources.
- [x] Step 1 (14:54): flags rewritten in props_pass6.py (FLAG_POLE_D 0.30, FLAG_BANNER 3.2 x 2.0 tapered pennant ->
  tip 1.1, cream hoist band + borders + 1.45 cream number both faces, red/cream banded pole, knob still = flag.top).
  fitcheck_pass6 flag check uses P6.FLAG_* (>= holes.json minimums, banner under the top) + new tee -> pennant-centre LOS
  check. Test build cup_flag_h08 OK (1,240 tris), preview looks right.
- [x] Step 2 (15:12): props_pass7.py (firefly_cluster_low 128, firefly_swarm 208, glow_shroom_patch 276, glow_root_arch
  280 tris), registered in build_all/dressing/dressing_world/fitcheck/assembly. dressing_world: role 'hollow' (cap 26,
  own share 6000), HOLLOW_PLAN pre-seed around the H8 alcove / lane sides / middle; hollow_trim() drops H8 trees behind
  the tee + H8/H9 seed toadstool_trio_small (984 tris); H9 interior pool + glow_shroom_patch; 3 firefly_glow spots max;
  pass7_vs_pass6 stats. Iterations: dw1 pre-seed (H6 -5), dw2 after-seed (only 1/24 fit), dw3 pre-seed cheaper props
  (H6 -5), dw4 + hollow_trim (H6 -3), dw5 dropped climb/green groups (H6 -2 small bushes, 720 tris), dw6 H6-second
  order: identical -> reverted. Result: H8 13 -> 25.
- [x] Step 3 (felt): textures.py felt() darker (~10%) + nap colour 0.22->0.40, normal x2.2->x4.0 (nap 0.7->1.0),
  felt_bright -5%; lglib Felt #478C35, FeltBright #66B547, preview sheen 0.45, normal strength 0.6->1.0. textures regenerated.
- [x] Step 4 (15:18): flags h01-h09 + 4 hollow props rebuilt (build_all --only); flag pole bands stop 0.48 under the
  pennant (H9 overlap); fitcheck_pass6 pennant filter by height. fitcheck_pass7.py (exec'd after pass6): 5 checks.
  dressing_world (dw8) + fitcheck: ALL PASS (174). Rendering tee views (all 9, 32 spp): /tmp/p7/asm1.log
- [x] Step 5 (15:47): tee renders iter 1 reviewed: flags read on H1/2/4/5/7/8/9 (H3 by design, H6 behind the
  millwheel in this framing); H8 hollow too faint (alcove behind rails). Iteration 2: bigger specks, junction_back group,
  firefly_glow Brightness 2.0 / range 12, lane_left dropped, patch 276->214 / root 280->250 tris. Final dw11: H8 13->29,
  H6 19->16, H7 25, H9 26->27, H3 -2 cards. fitcheck ALL PASS (174). make_docs pass-7 section (pass7_readme.md).
  Next: full build.sh (/tmp/p7/build.log) then assembly tee+top all 9 at 32 spp.
- [x] Step 6 (16:21): full build.sh (118 props, .blend, dressing, fitcheck ALL PASS, docs, sheets); assembly tee+top
  all 9 at 32 spp. Review: H9 pennant blown out by the cup spot ~1 stud away -> cup spots now 2 studs off the pole on the
  side away from the pennant (+ fitcheck >= 1.5 from the pennant); dressing_world + fitcheck ALL PASS (175) + H8/H9
  re-rendered; make_docs + tee_sheet. Skill blender-asset-pipeline: 2 lessons added.
- [x] Step 7 (16:22): _src/pass7_summary.md written; README pass-7 section (pass7_readme.md via make_docs). DONE.
