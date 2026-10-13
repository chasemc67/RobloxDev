# Stage aj — Sugarloaf fix1 (local only)

**RESULT: PARTIAL.** The requested source fixes, imports, local build and checks are complete. H15 retains wedged seam behavior and one ordinary-sweep timeout reset. Decoration clearance is reported as unresolved; this is not a zero-violation acceptance.

## Local boundary and preflight

Read game AGENTS.md and ag/ah/af/af-portability notes. Process preflight found no competing stage job. Studio Welcome screenshot confirmed MetavrseBuilder. Opened only `playtest/playtest-sc-batch34.rbxl` from disk and immediately used Save to File As `playtest/playtest-sc-fix1.rbxl`. MCP confirmed one place, PlaceId/GameId 0, no NetworkClient, role sugarloaf_canyon before source push. Studio retains its old batch34 MCP label after Save As; native window/save confirmation identifies fix1. No cloud place was opened/saved, no publish, new place, protected-place edit, or git push.

## Persistent build changes

- Regenerated SugarloafCanyon/Layout from the synced Oct 13 holes.json. Replaced changed H8/H15 pieces/walls and reapplied WorldBuilder.CapUnderCup terrain clearance. Final independent multiset reference audit matches H8 132 and H15 50 generated Geometry/Rails parts, including physics/query flags. CapUnderCup is a terrain operation, not a named Part.
- Imported only approved h08_ground (7 meshes) and h09_water_tank (5 meshes); FBX merge round-trip passed, 6,398 triangles, max mesh 2,320. Bounds and pivots match manifests plus SugarloafLayout offset. Both visuals have collision/query/touch disabled and persist through rebuilds via StageAJProps and SugarloafOverrides. Did not import h14_loading_dock.
- All 17 Trading Post decorative parts, including trading_post_deck Iron/TimberWeathered, have collision/query/touch disabled. CameraOcclusion no longer re-enables their queries.
- Removed H9 water_tank and H14 loading_dock placeholders. Preserved hidden obsolete H8 gumdrop skins.
- Added seven invisible block Part proxies from holes.json bounds: H7 island_hoodoo and H17 hour stones I/IV/VII/VIII/X/XI; GolfWall and Config wall physics. Existing obstacle colliders retained.
- Lifted 254 RailCap visuals by 0.02 studs. Reapply is idempotent (0 further raises). Baseline scan had 253; new H15 adds one cap. Zero remaining cap-top coplanar pairs and zero additional named trim/lip top candidates. Colliders unchanged by the visual lift. Full names and per-hole before/after counts: `playtests/stage-aj/railcap-fixed-list.json` and `clearance-report.md`.

Importer used Upload to Roblox unchecked. As established in af, that option does not prevent automatic child mesh asset creation. This requested FBX import used that workflow; no claim of offline/self-contained meshes or zero child assets is made.

## Clearance

Ran the exact requested deco_clearance.py --all command. It reports 492 raw rows, 88 is_real findings and 24 authored coplanar rows. Actual built OBB audit at 0.15 gap, ball headroom and felt-0.4..felt+8 player headroom reports 15,652 conservative candidates: 5,198 likely dressing envelopes and 10,454 other candidates. These are not 15,652 confirmed rendered intersections. Of 88 authored real rows, 41 map exactly to corresponding built bounds candidates, 43 have no exact visible-model mapping, and 4 lack equivalent pair/plane comparisons. Full grouped violations, mapping limits and rail table are in `playtests/stage-aj/clearance-report.md`; all raw rows retained. No blanket clearance pass is claimed.

## Physics checks

| Hole | Cupdrops | Random | Slow | Stuck | Timeout | Escape |
|---|---:|---:|---:|---:|---:|---:|
| H1 | 3/3 | 8 | 0 | 0 | 0 | 0 |
| H7 | 3/3 | 8 | 0 | 0 | 0 | 0 |
| H8 | 3/3 | 8 | 0 | 0 | 0 | 0 |
| H15 | 3/3 | 8 | 0 | 0 | 1 | 0 |
| H17 | 3/3 | 8 | 6 | 0 | 0 | 0 |

H8 seed 2026101208, original 80 plans and ground rays retained; setup/ownership/reporting adapted to current build. Stop time = last sampled speed > Config.StopSpeed through native ready/rest. Median **0.516741 s**, nearest-rank p90 **0.517311 s**. Every shot >1.5 s: **none (0/80)**. Forced rests 0, timeouts 0. All 80 shot rows and traces retained. Four independent noncolliding BallController workers; this is native physics with server ownership, not a claim of headset/client timing equivalence.

H15 targeted seam seed 2026101315: **72/80 wedged forced rests**, 0 timeouts. Every wedged finish/event position is in h15-timing-summary.json and h15-diagnosis.json. All 72 wedged starts were deliberately placed on the rail2 side of the new dune_lean3 deflector. This bypasses the deflector and is not directly comparable to the old 19/80 general sweep (seed132148). Native final distances to rail2 ~0.07944–0.07993 match the 0.08 ball radius; no physics/layout tuning was substituted for the authored data.

Additional reachable-side approach test, seed2026101316: 0/80 wedged forced rests, 50 timeouts. Starts are 0.5–4 studs on the approach side of lean3, aimed toward old rail2 seam ±20 degrees, speeds2–12. Separate h15-approach-timing files retain all positions and do not replace the required seam result. Final summaries include native AutoReset(timeout) events; the original stdout summary counted only the harness wall-clock timeout and was corrected offline from retained shot events.

Ordinary H15 random shot h15-fuzz-2 hit the native 20-second StrokeTimeout and reset near [-306.8198,147.0338,-5085.6489]. It was still moving at speed0.4873 at15.015 s; no wedge flag. Recorded terminal rest is after reset, not a successful uninterrupted stop. See h15-random-timeout.json.

## Camera and verification

- control: camera-to-head 12.1234–13.3615 studs; 3 jumps.
- outside_post: camera-to-head 12.1234–13.5093 studs; 3 jumps.
- near_iron: camera-to-head 12.1234–13.2371 studs; 3 jumps.

Actual Explore camera test repeated the supplied three positions and jump protocol, zoom locked at12.5. Complete frame samples and blockers are in camera-samples.json.

Final normal play/test console checks report zero server/client warnings/errors. One H17 random-placement attempt was refused because the moving arm changed state; harness retried and completed8 accepted random shots. A diagnostic H8 trace export failed during transport; all80 traces were separately recovered, exporter now uses chunked _G storage, and this transport issue did not change shot results. Initial selective rebuild used duplicated part names; corrected multiset matching and independent final reference audit ensure exact current geometry.

Final local save, hash, source equality and Studio shutdown are in result.json/source-check.json/shutdown.json. Screenshots stay local; named hole views were framed while the player remained in H1 Explore, so the HUD hole label differs from the framed hole. No rbxl, FBX or PNG is committed.
