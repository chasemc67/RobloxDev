# Stage af — local batch3/4 build

## Scope and preflight
- Read game AGENTS.md and stage ae notes first. No competing stage job matched `pgrep -fl "codex exec -m|claude -p"`.
- Launched Studio; screenshot showed **Welcome, MetavrseBuilder**. Opened only `playtest/playtest-sc-batch12.rbxl` through File > Open from File and immediately used Save to File As for `playtest/playtest-sc-batch34.rbxl`.
- MCP confirmed one open place, PlaceId 0, GameId 0, role sugarloaf_canyon, no NetworkClient. MCP retained the initial batch12 display name after Save As; the Studio window/save confirmation showed the batch34 path.
- Original batch12 remains byte-identical to ae: SHA256 `2151b35683ee807fd57ee4ba8a5dce5656bc93c8dfa62c0c04d8d775f099d81f`.
- Current src was pushed before edits. No cloud place was opened or saved; no place was published or created. Protected place 135374506016678 was not touched. No git push.

## Instructions and import
- Both repository AGENTS.md files now explicitly record Chase's Oct 12 ad/ae decision: OUR VRControls, wrist card, VR putter, sticks, and B/Y scorecard gear under real VR and SimulateVR; desktop keeps LobbyRoam. No remaining contradictory AGENTS.md statement was found.
- Reused ae's merge tool and source-FBX-bound normalization approach: reconstruct each library model at source origin, restore per-mesh sizes and centers, compensate the importer 180-degree Y rotation, restore manifest material/color, and place with manifest pivot/yaw plus SugarloafLayout offset [0,0,-5000].
- Imported one merged FBX with Upload to Roblox visibly unchecked, scene position/origin enabled, and anchored enabled. Merge round trip PASS: 12 sources, 51 meshes, 7,828 triangles, max mesh 1,152. All source/material/bounds comparisons passed; zero missing manifest items.
- Batch3/4 manifests mark every supplied landmark visual-only; no new timing prop is in these batches. Existing ae timing models remain welded to exact MoverRoot assemblies. Physical/query/touch flags on audited imported visuals are all false, and mover weld audit found no missing/wrong root welds.
- Matching older landmark placeholders were hidden. H8's two obsolete nonphysical `Rails.Bumper_gumdrop*` skins were identified in visual QA for hiding, independently of the exact Geometry colliders.
- Fresh holes.json-generated reference geometry matches all H7–H18 felt/base/wall/rail PieceId/WallId geometry signatures (positions, orientation, sizes, collision flags). Reference folders were destroyed after inspection; they were not separate places.

## H11 correction
- Before fixing: gate Y relative to closed pivot at cycle phases 2/8/10.3 was approximately **0 / -1.3 / -1.3**. Deck offsets approximately **0 / 4 / 0**. This proved ae's inversion was active.
- Removed the H11 entry from `tools/sugarloaf_motion_overrides.json`, retaining holes.json as authority. Regenerated/pushed SugarloafCanyon/Layout. Built a temporary H11 reference and replaced only the gate assembly; preserved its imported visual model and reconnected its existing welds to the fresh exact MoverRoot. Other H11 geometry and lift/quay timetables stayed unchanged.
- After fixing: measured gate offsets **-1.3000336 / +0.0000305 / +0.0000305** at phases **1.99924 / 7.99885 / 10.29941**. Deck world positions: `[150,115.99996,-5277]`, `[150,120.00021,-5277]`, `[150,115.98222,-5277]`; corresponding deck offsets `-0.00004 / 4.00021 / -0.01778`. Closed gate pivot Y = 116.
- Both completed timing runs had zero server/client warnings or errors. First high-frequency measurement exceeded MCP's 100k response limit and was retried at lower frequency; that failed read made no edit.
- Corrected H11 shot checks: 3/3 cupdrops, 8/8 random shots, 6/6 slow rollers; zero escapes, lost balls, stuck shots, timeouts or nudges.

## Harness and diagnostic runs
- Random fuzz previously counted placement attempts, silently skipping invalid candidates. It now retries placements and refused hits until the requested completed-shot count (bounded attempts), matching ae's slow-roller convention. Final evidence checks counts explicitly.
- The first invocation omitted the course option, allowing the test spec remote to default to Lantern Grove. It was invalid for this stage; H10–H18 then emitted boolean-spec warnings. Those runs are retained under `sweep` and `sweep-wrong-spec` and excluded from final totals. The final invocation explicitly uses `course: sugarloaf_canyon` in `sweep-final`.
- Exact geometry and H11 timing measurements directly addressed CourseSugarloaf and were not affected by the wrong-spec invocation.

## Portability and no-upload exception
**The strict zero-asset-upload constraint was not achieved by Studio's importer.** Even with Upload to Roblox unchecked, all 51 child RenderMesh assets were created in the cloud under MetavrseBuilder at import time. This was discovered by read-only public metadata lookup after import. No explicit asset upload endpoint or additional import/upload was invoked during the research. No inventory model upload or place publication was requested.

Full findings, costs, permission caveats, saved-file inspection, and official sources: [af portability report](af-portability.md). Ae notes were also updated with this finding and the H11 reversal. The cheapest next test is to copy the local file to PC and open it as MetavrseBuilder using the existing mesh IDs; MetavrsePlumber access and PC rendering remain unverified. No transfer, permission change, XML/model packaging, or extra upload was performed.

## Final evidence
Final totals, local file hash, console checks and shutdown status are in `playtests/stage-af/result.json` and `per-hole.md`. Raw final shot telemetry is retained under `sweep-final/`. Screenshots are local-only and excluded from git.

## H15 stuck finding (geometry retained)
- Three of eight random shots (1, 4, 8) ended in forcedrest/wedged after three seam nudges each. No escapes or timeouts; cupdrops 3/3. Full shot flags and coordinates are in final telemetry and `h15-stuck-diagnosis.json`.
- Read-only proximity checks locate all three at the exact `dune` felt / `dune_rail2` boundary (~0.08 studs, the ball radius); the first also lies near `green_s_rail`. New meshes have all physical flags false. This is a course-geometry/ball-recovery finding, not an imported-prop collision. Felt, walls, and colliders were not changed. Stage af fails the zero-stuck sweep criterion.

## Completion
- Saved locally through File > Save to File; UI confirmed the batch34 path. File: 3447258 bytes, SHA256 `3bde4e643dae002a2422ee929887a400a6126810b16590622eaab8d57e7292ff`. All 51 AF MeshIds verified in the saved binary.
- Final checks: 36/36 cupdrops, 96 random shots, 24 slow rollers (6 each H9/H11/H14/H17); zero escapes, lost balls, timeouts, or console warnings/errors. Three H15 stuck shots remain as documented above.
- H8 obsolete skins are now hidden. Twelve hole screenshots were inspected. H15 drift bases are partly occluded by existing terrain at the strict manifest placement; placement and terrain were retained.
- Studio quit successfully; MCP reports no studios and OS process check found no RobloxStudio process. No git push or place publication.
- Overall RESULT=FAIL: H15 stuck findings and the automatic child-mesh upload constraint exception.

RESULT=FAIL H11_Y=t2:-1.3000,t8:0.0000,t10.3:0.0000 H11_FIXED=yes
