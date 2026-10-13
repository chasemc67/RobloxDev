# Stage al — Sugarloaf fix2 (local)

Status: PARTIAL. All requested changes and test passes are complete; fix2 is saved locally and Studio is closed. The friction test did not resolve H15 wedges or crawls.

## Local boundary

Read game AGENTS.md and ag/ah/af/af-portability notes before work. No competing stage job matched the requested process check. Studio welcome screenshot confirmed MetavrseBuilder. Opened only `playtest/playtest-sc-fix1.rbxl` with File > Open from File, then immediately Save to File As `playtest/playtest-sc-fix2.rbxl`; native UI confirmed the output path. MCP retained the original fix1 label. Preflight confirmed PlaceId=0, GameId=0, no NetworkClient, role sugarloaf_canyon. No cloud place open/save, publish, new place, protected-place edit, or git push.

Initial shared src was pushed before the experiment. File-only helpers prepared the H15 harness and visual-top module; only the primary agent operated the one Studio place. `input-file.json` records fix1's hash.

## H15 friction TEST

`SugarloafOverrides.Apply` marks every H15 Geometry wall with WallId, including every dune_lean piece and dune_rail2, with friction=0.1 and friction weight=100. Current build has 12 colliders; dune_lean3 is the supplied lean piece. Density, elasticity and elasticity weight are preserved. `CourseBuilder.ApplyPhysics` honors the per-wall attributes, so a rebuild does not reset the TEST value. No global Config tuning or holes.json geometry change.

Paired native client harness `h15friction`, seed 20261013: 20 tee shots toward rail2, 30 close seam approaches, 30 low-speed approaches along lean. The explicit 80-shot manifest is generated from collider frames and felt raycasts; no refused/placement attempts count as completed shots. These deliberately targeted close approaches stress the seam and are not directly comparable to Playtest Bot's 1 wedge in 40 general shots. The same fixed manifest and harness are used before/after. Physics changes only after the completed 80-shot baseline. Visual edits preceded the baseline but the 705 colliders were verified identical.

CSV has one row per shot and retains actual start, launch speed/direction, terminal harness outcome, stop time, first position whose continuous speed<1 interval lasts >3s, category, native flags and timeout boolean. Crawl-location follows the requested literal threshold and can include ordinary settled rest; crawl_lean classification requires that low-speed interval while the controller is still moving near lean. Wedge means native forcedrest near rail2 or a nearly stationary moving ball there for >3s. Primary category priority is sunk, wedge_seam, crawl_lean, timeout, rest. Native timeout counts are also reported independently because a crawling shot can later time out. Terminal `rest` after an AutoReset is not an uninterrupted successful stop. Stop time is the controller rest/end time relative to launch, including recovery when applicable.

The baseline's aggregate result exceeded MCP's 100,000-character response limit after all 80 shots completed. Complete per-shot native JSONL was already saved through shot80; results were reconstructed from those 80 native row events and the validated manifest. No shot was synthesized or replayed to fill evidence. The after runner exports aggregate results in 45k chunks and checkpoints rows every 30 s.

Paired results (80 completed each; manifests identical):

| Run | Wedge seam | Crawl lean | Primary timeout category | Rest | Sunk | Native timeout events |
|---|---:|---:|---:|---:|---:|---:|
| Before (friction 0.05) | 26 | 38 | 0 | 16 | 0 | 26 |
| After (friction 0.1 TEST) | 26 | 39 | 0 | 15 | 0 | 33 |

All native timeouts overlap the crawl category, hence zero *primary-category* timeouts does not mean zero timeout events. The final RESULT line uses native timeout counts (26/33), which overlap crawl counts. No escapes in either focused pass. This test shows no wedge improvement and seven more native timeout events; it does not establish a general-play failure rate. Final after-pass server/client consoles have zero warnings/errors.

## Dock and placeholders

Imported only the supplied `models/fbx/props_h09h14/h14_loading_dock.fbx`, rev2 manifest: 5 meshes, 1,688 triangles, maximum mesh 564. Source FBX bounds normalize mesh centers/sizes, with importer rotation correction. Manifest anchor pivot [-300,150,-167], yaw180, plus SugarloafLayout [0,0,-5000], gives [-300,150,-5167]. The geometry retains its west-of-rail2 offset; the anchor is not recentered onto mesh bounds. Colors/materials follow the manifest. All five meshes are visual-only, with CanCollide/CanQuery/CanTouch=false and VisualQueryDisabled=true.

Library copy in ServerStorage.StageAJProps plus approved placement in SugarloafOverrides restores the dock after rebuild. Deleted Hole14.Decor.ore_piles.Placeholder and Hole9.Decor.pump_house.Placeholder. Bypass, safe-bank, timing signs and arrows are retained. Prior stage-aj removed loading_dock and water_tank placeholders; that behavior remains.

Importer options: Upload to Roblox unchecked, scene position and scene-origin pivot on, anchored on, cages off. As documented in af, unchecked does not prevent child mesh asset creation; this local file contains URI-backed meshes and is not an offline embedded geometry bundle. No place upload/publication was performed.

## Rail flicker

The unchanged supplied `scan-all-rail-tops.luau` reproduced 387 coplanar pairs. New `SugarloafRailTops` uses the same normal/gap/polygon-overlap criteria and deterministic greedy levels in 0.02-stud increments. Simple neighbours alternate levels; multiway overlaps and cross-height cap/body conflicts need additional levels, maximum 0.10. 209 visual parts change. Rail bodies extend only their visual top with their bottom fixed; caps move along local up. Original CFrame/Size attributes eliminate cumulative drift. Every present Rail_/RailCap_ is already a nonphysical visual; no defensive visual-copy fallback was needed. Physical Geometry colliders retain their exact position, size and orientation.

Original-method scan after changes: 0. Reapplying overrides changes 0 poses/sizes. Temporary H9/H14/H15 reference rebuild inside the same place verifies dock/placeholder persistence, all 12 H15 friction overrides, and 0 coplanar pairs, then is destroyed. This reference is a folder, not another place.

A diagnostic call to generic ApplyPhysics changed two unrelated imported mover Blocker elasticities from 0.65 to 0.63. Their original values are restored before the general sweep and final save; final collider comparison verifies only the intended H15 friction differences.

## Final checks and save

All 18 holes: **54/54 cupdrops**, 144 random shots, and 30 slow rollers (six each on mover holes 6, 9, 11, 14, 17). **Stuck 0, escapes 0**. One native timeout on H15 fuzz shot 2 followed seam recovery; no harness timeouts. This is retained as a failed recovery outcome even though the controller eventually rested after reset. Server and client consoles have zero warnings/errors. See `verification-summary.json` and per-hole CSV.

Final source equality: 52/52. Final comparison: all 705 physical collider poses/sizes unchanged, with only the 12 intended H15 friction-property differences; original density/elasticity retained. Runtime audit confirms all five dock meshes are nonphysical in server and client, and the requested signs remain. Original-method rail scan: 0 remaining pairs.

File > Save to File visibly confirmed the exact fix2 path at 16:39:49 PT; Studio then quit. Process check and MCP instance list confirm shutdown. Last Edit state: PlaceId=0, GameId=0, no NetworkClient, TestMode=false, SimulateVR=false. Original fix1 SHA-256 is unchanged. Output size: 3,498,909 bytes; SHA-256 `b136231f22aa80bf80ca0df0eeb4d672155658e7cd44bbeb11a6f6ea1ac1c8c1`. See `final-state.json`.

Evidence root: `playtests/stage-al/`. Source, tools, notes and text evidence are committed with the requested stage-al message. No RBXL, FBX or images are committed; no git push.
