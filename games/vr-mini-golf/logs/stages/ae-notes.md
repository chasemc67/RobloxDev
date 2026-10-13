# Stage ae — local only

Chase confirmed: the lobby keeps OUR VR controls under VR/SimulateVR; stage ad direction is correct.

Preflight: no competing stage job. Studio screenshot confirmed Welcome, MetavrseBuilder. Sole local Aurora file: PlaceId=0, GameId=0, role=aurora_archipelago, no NetworkClient. Saved as playtest-aurora-v2.rbxl before changes. No cloud place opened, saved, or published.

## Aurora v2
- Regenerated AuroraArchipelago/AuroraLayout with aurora_to_lua.py; rebuilt CourseAurora through the ac2 aurora_build.py path. Retained the nonphysical blockout.
- H2 cup [-9.75,0,-46]: centre-to-wall clearance 2.25 studs to rail7, passing 2.2. Geometry audit matches all 18 holes; cup depth 0.35.
- Cupdrop 54/54; H2 random sweep 8 shots, zero escapes/stuck/lost, zero warnings/errors. Saved and closed playtest-aurora-v2.rbxl before Sugarloaf.

## Sugarloaf local build
- Opened playtest-sc-v20.rbxl using File > Open from File. PlaceId=0, GameId=0, no NetworkClient; sole connected place. Immediately saved as playtest/playtest-sc-batch12.rbxl.
- Pushed all current src, generated and pushed Sugarloaf data. Only H8 felt and walls differ from holes.pre-ae.json. A temporary single-hole build supplied only changed PieceId/WallId instances: removed 91, added 115; untouched pieces and other holes retained. CapUnderCup(h8,nil,6) applied; terrain ray is 2 studs below cup.
- Imported merged batch1 + batch2 + h08_ground FBX with Upload to Roblox UNCHECKED; scene origin/position and anchored enabled. Merge round-trip PASS (13 sources, 51 meshes, 11,490 triangles, max mesh 2,280). All mesh sizes/centres reset from source FBX bounds, rotations corrected for importer 180-degree Y bake, materials restored from manifests.
- Manifest positions plus Sugarloaf offset [0,0,-5000]. H3 [-75,18,-4689], H4 [220,18,-4679]. Five timing models welded to existing MoverRoot assemblies with exact collision proxies retained. 18 flags, 6 landmarks, 5 timing models, 1 H8 ground model: 85 visual BaseParts total; zero CanCollide/CanQuery/CanTouch and zero missing mover welds. Old corresponding visuals and placeholders hidden/replaced.
- H8 ground visual only. Exact floor/wall audit passes, including 0.5-stud crease floors. Imported content renders on this machine with Upload to Roblox unchecked. Meshes carry rbxassetid references; importer-internal mesh upload/cache behavior and cross-machine portability are unverified. No extra cloud upload was needed/requested to show the props.

## H11 timing correction
- Measured old cycle in Play: actual offset -1.3 at phases 1 and 5 (sunk/open), 0 at phases 6 and 10 (raised/closed). Supplied JSON/manifest phase -1.3 and dwells -1.3:5.5;0:4.6 inverted the requested closed/open meanings.
- Reproducible config source tools/sugarloaf_motion_overrides.json changes phase to 0 and dwells to 0:5.5;-1.3:4.6. sugarloaf_to_lua.py applies it during generation; stage_ae_apply_h11.py updates existing mover attributes from generated data. No hand-edited timing constants in Studio; art JSON left intact. Speed 4.3333333333 and period 10.7 unchanged; lift/quay timetables unchanged.
- Actual constraint sample interval ~0.033 s, endpoint tolerance 0.05 stud. Measured full cycle: CLOSED 0–5.530, OPENING 5.530–5.796, OPEN 5.796–10.429, CLOSING 10.429–10.696, CLOSED by 10.696. Desired boundaries 5.5/5.8/10.4/10.7. Both timing Play runs had zero server/client warnings/errors.

## Limits
- No cloud place opened, saved, or published; no new place, no explicit asset/model upload requested, no git push. Protected place 135374506016678 untouched.
- Aurora ac2 H4 wedge and H17 static-toggle limitation remain outside this stage's H2 sweep scope.
- One initial props-normalization call ran before asynchronous local import had finished and returned missing import; no mutation occurred. Retried after import appeared. All completed Play console checks are recorded separately.

- H6 slow roller 5 triggered a successful pinned-ball recovery nudge; retained as an `unstuck/pinned` event, not an unrecovered stuck ball.

## Completed affected-hole sweep
- Sugarloaf: H1–H6, H8, H9, H11, H14, H17 cupdrops 33/33; 88 random shots and initially 29 slow rollers completed; final count audit found one H17 candidate placement skipped. Zero escapes, lost balls, unrecovered stuck balls, timeouts, server/client warnings or errors.
- H6 slow-5 and H9 slow-3 had successful `unstuck/pinned` recovery nudges; reasons and coordinates retained per hole.
- H17's four obsolete nonphysical head skins were hidden after the sweep. Colliders/welds unchanged.

## H8 settling measurement
- 12 shots: four from alternating sides of each of the three crease troughs, speeds 1.15–1.6 studs/s. Every shot rested in a trough floor.
- Measured from last PostSimulation velocity magnitude > Config.StopSpeed (0.2) while moving to first ready/rest sample. Median **0.51815 s**, range 0.5158–0.5351 s (faster than the ~1.2 s target); zero >1.5 s flags, zero stuck flags, zero console warnings/errors.

| Shot | Trough | Stop interval (s) | >1.5 s |
|---|---|---|---|
| h8-floor-1-1 | 1 | 0.5170 | no |
| h8-floor-1-2 | 1 | 0.5182 | no |
| h8-floor-1-3 | 1 | 0.5189 | no |
| h8-floor-1-4 | 1 | 0.5182 | no |
| h8-floor-2-1 | 2 | 0.5181 | no |
| h8-floor-2-2 | 2 | 0.5180 | no |
| h8-floor-2-3 | 2 | 0.5174 | no |
| h8-floor-2-4 | 2 | 0.5351 | no |
| h8-floor-3-1 | 3 | 0.5177 | no |
| h8-floor-3-2 | 3 | 0.5158 | no |
| h8-floor-3-3 | 3 | 0.5185 | no |
| h8-floor-3-4 | 3 | 0.5183 | no |

## Final validation and files
- Slow-roller harness now retries rejected/missing placement candidates, counting completed putts. H17's final recheck completed 6/6 slow rollers with no issues or console warnings/errors. Final required totals use these six in place of the original five; baseline telemetry is retained without double-counting.
- Final totals: Aurora 54/54 cupdrops and 8 H2 random shots; Sugarloaf 33/33 cupdrops, 88 random shots, 30 slow rollers; H8 12 targeted settling shots. Zero escapes, unrecovered/lost balls, stuck shots, timeouts, or final Play console warnings/errors. Two successful pinned recoveries (H6/H9).
- Inspected local screenshots for H3 station, H4 geode wall, H8 floors, H9 rotor, H11 lock. Old matching mover placeholders and H17 head skins hidden; collision unchanged. Screenshots retained locally under playtests/stage-ae/screens and excluded from git.
- Final Edit audit: local PlaceId 0, no NetworkClient, correct role; test mode and SimulateVR false. File > Save to File confirmed playtest/playtest-sc-batch12.rbxl. Studio quit; MCP studios=[] and application process absent.
- No cloud version created in ae. Input Sugarloaf file is ac2's downloaded unpublished v20 (published v19 at that time); no cloud version was re-opened or changed here.
- Output paths: games/vr-mini-golf/playtest-aurora-v2.rbxl and games/vr-mini-golf/playtest/playtest-sc-batch12.rbxl. File sizes and SHA256 hashes are in playtests/stage-ae/result.json.
- RESULT=PASS for this stage's requested scope. Inherited Aurora ac2 H4/H17 limitations and importer portability uncertainty are retained above.

## Per-hole results
Aurora sweeps were requested only for H2; unrun sweep cells on other Aurora holes are intentional.

| Course | Hole | Cupdrop | Random / slow | Escapes | Lost | Stuck | Reasons |
|---|---|---|---|---|---|---|---|
| aurora | H01 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H02 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| aurora | H03 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H04 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H05 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H06 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H07 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H08 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H09 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H10 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H11 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H12 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H13 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H14 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H15 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H16 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H17 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| aurora | H18 | 3/3 | unrun / unrun | unrun | unrun | unrun | — |
| sugarloaf | H01 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| sugarloaf | H02 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| sugarloaf | H03 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| sugarloaf | H04 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| sugarloaf | H05 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| sugarloaf | H06 | 3/3 | 8 / 6 | 0 | 0 | 0 | pinned |
| sugarloaf | H08 | 3/3 | 8 / 0 | 0 | 0 | 0 | — |
| sugarloaf | H09 | 3/3 | 8 / 6 | 0 | 0 | 0 | pinned |
| sugarloaf | H11 | 3/3 | 8 / 6 | 0 | 0 | 0 | — |
| sugarloaf | H14 | 3/3 | 8 / 6 | 0 | 0 | 0 | — |
| sugarloaf | H17 | 3/3 | 8 / 6 | 0 | 0 | 0 | — |

## Stage af follow-up: portability and H11 (Oct 12, 2026)
- Af proved that the importer creates child RenderMesh assets even with Upload to Roblox unchecked: all 51 af mesh metadata records identify MetavrseBuilder and import-time creation timestamps. Unchecked suppresses the inventory Model, not all cloud asset creation. Therefore ae's importer portability uncertainty must not be read as a guarantee of zero asset uploads.
- Af MeshId/MeshContent inspection shows URI-backed render geometry. Copying the local file does not embed that geometry or grant a second account permission. Cheapest next test: open the copied file on the PC as Builder; Plumber access remains unverified and may need explicit collaborator grants. No PC transfer, account/permission change, or extra upload was performed. Full report and official sources: [af portability report](af-portability.md).
- Af measured ae's H11 gate at ~0, -1.3, -1.3 for phases 2, 8, 10.3, then removed the inverted override to follow holes.json. Rebuilt gate measurements are ~-1.3, 0, 0; the lift/deck schedule was retained. See `playtests/stage-af/h11-before.json`, `h11-after.json`, and `h11-rebuild.json`.
