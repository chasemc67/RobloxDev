# Pass 5 progress (Playtest Bot review: H8/H9 too dark, H3/H4/H6 lane clutter, moving-part colours)

- [x] Step 0 (2026-10-10): started; reading pass4 summary/progress, README, build.sh, fitcheck, dressing_world, assembly_world, world_scene, lglib, props_moving.
- [x] Step 1: lglib materials FeltBright / TrimStone / TrimCream / MoveRed / MoveCream / MillSlate / MillBlue (+ TEX felt_bright,
  limestone, slate); textures.py felt_bright.png (felt pattern lifted ~45%). Backup: _src/manifest_before_pass5.json.
- [x] Step 2: props_moving.py cream-red scheme (H4 arms, H6 paddles, H7 log, H8 door, H9 gate + bar; geometry unchanged);
  props_dressing.py rail variants rail_straight_{4,2}_{trim,mill} + rail_end_post_{trim,mill}; new cup_lantern_stake (1.95 tall).
  build_all --only (13 props) running in background (pid in /tmp/p5_build.pid).
- [x] Step 3: build_all --only 13 props OK (moving-part bboxes unchanged; checked previews). dressing_world.py: tall_near_rail rule
  (TALL_H 2, RAIL_BACK 3, footprint + geometry below base+5 vs every wall of every hole), accents (cup_lantern_stake at H8/H9 cups +
  H9 root gate, placed first), hooks refill moved to 4-6.5 from felt, spot_lights (H8 door/cup, H9 gate/bar/cup), pass5 stats vs
  manifest_before_pass5.json. Running dressing_world.py.
- [x] Step 4: dressing_world.py run OK (109 s): accents 2+2+2 placed, 5 spots all clear; tall_near_rail removed 51 / nudged ~45;
  tris 142,218 -> 144,084; near-field max 33,998. hole_skins.py + manifest.hole_skins; world_scene per-hole felt/rail
  variants + spot lights; make_docs pass-5 section; fitcheck pass-5 checks written. Next: fitcheck.
- [x] Step 5: fitcheck ALL PASS (140 checks; new: 9 tall_near_rail, 3 rule negatives/positive, spots, accents, light-host negative,
  moving-part scheme, hole skins). Render iteration 1 (tee, H3/H4/H6/H8/H9, 24 spp) started.
- [x] Step 6: render iteration 1 (24 spp, tee H3/H4/H6/H8/H9). H3/H4/H6 lanes clean (no tall dressing by rails; H6 blue mill
  rail distinct; red-cream moving parts read). H8 good (bright felt + cream trim). H9 still dark (felt ~53,93,41 vs H4 70,122,63)
  and its felt pieces looked broken: found a pass-4 PREVIEW bug (world_scene tilted every z-axis felt slope the wrong way).
  Fixes: slope sign in world_scene; preview spot watts 160 -> 700 per Brightness; H9 lane_fill spot_lights over lane/landing/
  chamber/heart (range 18, brightness 1.5); fitcheck spot target for felt fills. Re-running dressing_world -> fitcheck + render it 2.
- [x] Step 7: dressing_world re-run (9 spots: H8 2, H9 7 incl. 4 lane fills, all clear) + fitcheck ALL PASS (139 checks) + render
  iteration 2 (32 spp, tee H3/H4/H6/H8/H9). H9 now reads: continuous bright lane (slope fix), cream trim separates rails from the
  leaf floor; H8 good. Extra: rendering tee H1/H2/H5/H7 (dressing + slope fix changed them) and top views for all 9 (32 spp).
- [!] 13:13 NOTE: a parallel Round-5 design agent (claude pid 393539, playtest notes 6-10) is regenerating ../holes.json
  (mtime 13:10): H4 spinner blockers 3.8->2.3, H8 cup z -43.5->-34.5, H9 lantern_bar -> lantern_pendulum, H7 log range +-7.
  Pass-5 dressing/spots/fitcheck were computed against holes.json as of ~12:45-12:53. Not editing holes.json (not my scope).
  Tee H1/H2/H5/H7 (scene built ~13:02) and the top views (scene ~13:05) may already include some of its changes.
- [x] Step 8: tee H1/H2/H5/H7 + top views (all 9) rendered at 32 spp; tee_contact_sheet.png (all 9 views) + README + contact_sheet
  regenerated. Made dressing_world/fitcheck data-driven for the Round-5 holes.json changes (spot per moving part, missing
  targets reported). Fitcheck vs in-progress Round-5 holes.json: 6 FAILs (H8 felt moved under dressing, H9 lantern_bar gone)
  -> _src/fitcheck_vs_round5_wip.txt; validated pass-5 result kept as fitcheck.txt (= fitcheck_pass5_validated.txt).
- [x] Step 9: _src/pass5_summary.md written; repo skill blender-asset-pipeline lesson added. DONE (rebuild order after Round 5
  lands is in the summary).
