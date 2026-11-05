# PROGRESS (pass 4 driver)
See pass4_progress.md for step detail. As of 02:28 PT 2026-10-10: Claude pass-4 job (pid 250230) still running, Blender render iteration 2 (assembly_world.py, pid 267651) in progress. Steps 0-4a, 5a, fitcheck done. Remaining: render iter 2, tee_contact_sheet, world contact sheet, README, pass4_summary.md. Do NOT start a duplicate job while pid 250230 lives.

## Flythrough v1 (started 10:25 PT)
_src/flythrough.py (Eevee, taa 2, 1280x720, 76 s timeline). _src/fly_run.sh renders even frames (12 fps) to previews/fly_frames/, resumable.
Then: ffmpeg -framerate 12 -pattern_type glob -i 'previews/fly_frames/f_*.png' -vf minterpolate=fps=24:mi_mode=blend -c:v libx264 -crf 18 -pix_fmt yuv420p previews/flythrough_v1.mp4 ; poster = frame 0 (Cycles still or copy).
- fly_run.sh switched to 1 worker (2 parallel was slower). fly_encode.sh waits for ALLDONE then encodes the MP4 and poster. ETA ~13:20 PT.

## Pass 5 (started 12:45 PT): Claude job running brief_pass5.md; detail in pass5_progress.md. If it dies, relaunch the same command (see _src/claude_pass5.log header / brief).
- pass5 step 0: started, reading sources
- pass5 step 1-2: new materials/felt_bright, moving-part recolour, rail variants, cup_lantern_stake; build_all --only running
- pass5 step 3: props built; dressing_world rule/accents/spots coded, running
- pass5 step 4: dressing_world re-run OK; next fitcheck
- pass5 step 5: fitcheck ALL PASS (140); render iter 1 started
- pass5 step 6: iter 1 reviewed; H9 dark + preview slope bug fixed; iter 2 (dw + fitcheck + 32 spp render)
- flythrough moved to MacBook (Eevee 24 spp, 24fps, ~/LanternGroveRender); box fly_run stopped 12:55
- pass5 step 7: iter 2 final renders OK (H3/4/6/8/9); rendering tee H1/2/5/7 + all top views
- pass5 NOTE: holes.json being changed concurrently by the Round-5 design agent; pass-5 validated vs ~12:50 snapshot
- pass5 DONE: summary in pass5_summary.md; holes.json Round-5 drift -> rerun dressing_world/fitcheck/renders after Round 5 lands

## Pass 6 (started 13:46 PT): Claude job on brief_pass6.md; detail in pass6_progress.md. Relaunch same command if it dies.
- pass6 step 0: started, manifest snapshot taken, reading sources
- pass6 step 1: new/changed prop generators written, build OK; previews rendering
- pass6 step 2: dressing_world re-run OK (H7 13->25 instances); fitcheck running
- pass6 step 3: fitcheck ALL PASS (168); rendering all 9 tee + top views
- pass6 step 4: renders done (all 9 tee+top); running full build.sh
- pass6 DONE: fitcheck ALL PASS (168), all 9 tee/top re-rendered, .blend rebuilt; summary in pass6_summary.md
- Pass 6 DONE (verified 14:50 PT).

## Pass 7 (started 14:52 PT): Claude job on brief_pass7.md; detail in pass7_progress.md. Relaunch same command if it dies.
- pass7 step 0: started, manifest snapshot taken, reading sources
- pass7 step 1: flags enlarged (pennant 3.2x2.0, pole 0.30), fitcheck flag checks updated
- pass7 step 2-3: H8 Firefly Hollow props + dressing (H8 13->25, H6 -2 bushes), felt darker + stronger nap; fitcheck next
- pass7 step 4: fitcheck ALL PASS (174); rendering tee views all 9 (32 spp)
- 15:42 PT: pass7 job still alive (not relaunched). Queued pass 7b (plant 1.5-stud rail clearance) via _src/p7b_chain.sh -> brief_pass7b.md, starts when pass7 exits.
- pass7 step 5: H8 iteration 2 done (H8 13->29), fitcheck ALL PASS (174); running full build.sh
- pass7 step 6: full build + all 9 tee/top renders, cup spots moved off the pennant, fitcheck ALL PASS (175)
- pass7 DONE (16:22 PT): fitcheck ALL PASS (175), all 9 tee/top re-rendered, H8 13->29, summary in pass7_summary.md

## Pass 7b (started 16:23 PT): Claude job on brief_pass7b.md; detail in pass7b_progress.md. Relaunch same command if it dies.
- pass7b step 0: started, manifest snapshot taken, reading sources
- pass7b step 1: plant category + plant_near_rail rule coded in dressing_world; dressing run 1 started
- pass7b step 2: dressing run 1 OK (30 pass-7 plant violators fixed, all plant gaps >= 1.5); fitcheck running
- pass7b step 3: fitcheck ALL PASS (188); rendering tee views all 9 + H1 top

## Pass 8 (started 18:07 PT): Claude job on brief_pass8.md (H9 hanging lanterns, H7/H8 rail lanterns, H8 brighter emissives); detail in pass8_progress.md. Relaunch same command if it dies.
- pass8 step 0: started, manifest snapshot taken; pass 7b found unfinished (sheet/README/summary) -> finishing it first
- pass7b DONE (18:10 PT, finished by pass-8 job): fitcheck ALL PASS (188), all 9 tee re-rendered, sheet/README/summary written
- pass8 step 1: pass 7b finished; reading sources for lanterns
- pass8 step 2: new lantern props + dressing/lights code written; building props
- pass8 step 3: props built, fitcheck_pass8 written; dressing run 1
- pass8 step 4: dressing run 3 OK (H9 3 hanging, H7 8, H8 15 rail lanterns); fitcheck running
- pass8 step 5: fitcheck run 1 (lantern checks ok; Round-7 holes.json drift FAILs); H9 3rd lantern moved over the heart; dressing run 4
- pass8 step 6: fitcheck ALL PASS (209) vs Round-7-start snapshot; live Round-7 WIP = 6 moving-prop FAILs (not pass 8); rendering H7-H9 tee
- pass8 step 7: renders iter 1 checked; H9 hanging lanterns scaled 1.5; rerunning dressing/fitcheck/renders
- 18:47 PT: steering addendum (Round 7 final: H7 log, H8 root door, H9 bob, props.md lantern positions) appended to brief_pass8.md; queued continuation via _src/p8b_chain.sh after current job exits.
- pass8 step 8: fitcheck ALL PASS (209, Round-7-start snapshot), H7-H9 tee re-rendered, README + sheets rebuilt
- pass8 main steps 1-6 done (18:58 PT; addendum still to do): fitcheck ALL PASS (209, vs Round-7-start snapshot; live Round-7 WIP = 6 moving-prop FAILs, see pass8_summary), H9 3 hanging lanterns, H7 8 + H8 15 rail lanterns, 38 lights in manifest.lights[], H8 emission x2; H6-H9 tee re-rendered; summary in pass8_summary.md
- pass8 addendum A1: Round-7 moving props rebuilt (data-driven), H9 lanterns on props.md anchors; build + dressing + fitcheck + renders running
- pass8 addendum A2: fitcheck ALL PASS (209) vs final Round-7 holes.json; rendering H7-H9 tee
- pass8 DONE (19:21 PT): addendum included. Fitcheck ALL PASS (209) vs FINAL Round-7 holes.json (drift resolved: log/door/pocket/pendulum/ring rebuilt), H9 3 amber lanterns on props.md anchors (cluster unplaced), H7 8 + H8 15 rail lanterns, 38 lights in manifest.lights[], H8 emission x2; H6-H9 tee re-rendered; summary in pass8_summary.md
- 19:28 PT: pass8 job completed addendum itself; queued p8b continuation cancelled (not needed).

## Pass 9 (started 12:31 PT): Claude job on brief_pass9.md (H9 pendulum plinth); detail in pass9_progress.md. Relaunch same command if it dies.
- pass9 step 0: started, manifest snapshot taken (_src/manifest_before_pass9.json)
- pass9 step 1: plinth code written; building h9_lantern_pendulum + root beam
- pass9 step 2: pendulum + beam built; fitcheck_pass9 written; fitcheck run 1
- pass9 step 3: fitcheck 1 pass-9 OK; root beam re-centred on its x-22 anchor (legs hit a rail at hinge 21.2)
- pass9 step 4: fitcheck ALL PASS (218) -> fitcheck_pass9_validated.txt; rendering H9 tee
- pass9 step 5: H9 tee re-rendered; README + tee sheet rebuilt
- pass9 DONE (12:38 PT): H9 pendulum base plinth 0.9x0.4x1.6 yaw 0 (-30 vs body) merged into __Iron, 1820 tris; hinge (21.2, 8.996, -38.5) per holes.json; min felt clearance 0.0213 at +-3.235 deg over [-13,13]; root beam re-centred on x 22; fitcheck ALL PASS (218); H9 tee re-rendered; summary in pass9_summary.md

## Pass 10 (started 15:17 PT): Claude job on brief_pass10.md (H9 plinth Round 10 resize first, then vr_wrist_bracer); detail in pass10_progress.md. Relaunch same command if it dies.
- pass10 step 0: started, manifest snapshot taken; holes.json Round 10 = brief (foot 1.0x0.4x1.6 @-7.759, hinge 21.2/8.996/-38.5, +-11 deg 4 s)
- pass10 step 1: H9 pendulum rebuilt w/ Round-10 plinth 1.0x0.4x1.6 (fbx/h9_lantern_pendulum.fbx exported, previews refreshed); fitcheck running
- pass10 JOB 1 FBX READY (15:21 PT): fbx/h9_lantern_pendulum.fbx re-exported (1820 tris, same 5 MeshParts; plinth 1.0x0.4x1.6 yaw 0 in __Iron, bottom 0.059 below body); pivot = hinge (21.2, 8.996, -38.5) = holes.json; swing 11*sin(2*pi*t/4) deg; min felt clearance 0.0213 at +-3.595 deg; fitcheck ALL PASS (226) -> fitcheck_pass10_validated.txt
- pass10 step 3: vr_wrist_bracer generator written; building
- pass10 step 4: fbx/vr_wrist_bracer.fbx built (978 tris; WristFace 0.32x0.20 16:10, normal +Y, UVs 0-1 verified on re-import); fitcheck ALL PASS (234); docs next
- pass10 DONE (15:26 PT): H9 plinth 1.0x0.4x1.6 (Round 10), hinge (21.2, 8.996, -38.5), +-11 deg/4 s, min felt clearance 0.0213 at +-3.595 deg; new fbx/vr_wrist_bracer.fbx 978 tris, WristFace 0.32x0.20 (16:10) centre (0,0.238,0) normal +Y, +X fingers; fitcheck ALL PASS (234); summary in pass10_summary.md

## Pass 10b (18:20 PT): vr_wrist_bracer face resize (Round 5: 1024x784 wrist card)
- WristFace 0.32x0.20 -> 0.37x0.28 (ratio 1.321; card 1.306); bezel frame widened (outer 0.414x0.324), pad 0.45x0.34 (bottom 0.110). Straps, rings, sleeve unchanged.
- Built + fitchecked headless on the Windows PC (Blender 5.2, C:\lg10b); outputs copied back. fbx/vr_wrist_bracer.fbx 978 tris, same 5 MeshParts; re-import: 0.3700x0.2800, centre (0,0.238,0), normal +Y, UVs 0-1. fitcheck ALL PASS (235, +1 negative test for the old 0.32x0.20 face) -> fitcheck_pass10b_validated.txt. Old FBX/previews kept in _src/pass10b_old/.

## H9 emissive dim (19:16 PT Oct 11): 14 *_h9dim.fbx (Neon Glow/Firefly/ShroomGlow colour x0.7), originals untouched; manifest.h9_emissive_dim; preview previews/h9_emissive_dim.png; script _src/h9dim/h9dim.py.
