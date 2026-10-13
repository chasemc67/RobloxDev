# Stage ak — lobby-only publication

Chase approved October 13, 2026 at 10:11 AM PT. Scope is cloud lobby 87725688219952 in universe 10769274294 only. No course place opened, saved, or published; protected place 135374506016678 untouched. No new place, asset import, or git push.

## Preflight and baseline

Read game AGENTS.md and ag/ah/af notes plus af-portability. No competing stage job. Studio welcome screenshot confirmed MetavrseBuilder. The protocol launch left an empty launcher alongside the lobby; MCP reported “Place is not open” for that launcher, which was closed. Exactly one loaded place: lobby in Edit, correct PlaceId/GameId and PlaceRole=lobby. Initial SimulateVR=false and GolfTestMode=false.

Version History read before edits: October 12, 2026 — v247, 7:48 PM, MetavrseBuilder, unpublished; v246, 6:06 PM, MetavrseBuilder, Published. No Restore/Revert used.

## Script push and checks

Ran `python3 tools/run_playtests.py push $(find src -name '*.luau')`. All 51 current source files match Studio, including GolfMain.client, HUD, VRControls and LobbyServer. The push created the current SugarloafOverrides script in ServerStorage; it did not open a course or rebuild any content. No game source edits were made during ak.

Cloud lobby content retained. No local ae2 file was opened or merged. A read-only workspace content inventory hit MCP's 100,000-character response cap; batched reads succeeded. The 725-row post-push baseline covers non-script instance paths/classes/attributes and BasePart geometry, appearance, collision flags, mesh and texture IDs. This is not a full binary comparison against ae2 or a terrain voxel dump.

Desktop and iPhone 17 Pro smoke passed, with zero server/client console warnings/errors. Both exercised lobby spawn, menu close/walk/reopen, course-card requests, skipped Studio teleport loading, portal requests and leaderboard. Studio teleport requests did not open course places. Evidence: `playtests/stage-ak/smoke-desktop.log`, `smoke-iphone.log`, `push.log`, and `source-equality.json`.

## Final VR and content gate

`tools/stage_ak_vr.py`: PASS. Simulated left wrist shown at alpha=1, LOBBY / VR Mini Golf and dash stats; VRPutter exists. Left stick moved 3.124 studs, right stick turned 30.000 degrees. Both B and Y opened/closed the scorecard. Title [164,174,230,44], Close [402,182,56,56], gear [466,150,64,64]; every pairwise intersection area is zero. The right-hand laser hovered SettingsButton and its trigger opened Settings. Wrist/scorecard/Settings screenshots visually inspected. Server and client each had zero warnings/errors. This is a simulated VR check, not headset acceptance.

Returned to Edit with SimulateVR=false and GolfTestMode=false. The 725-row non-script workspace inventory is identical before and after testing. No lobby geometry, meshes, lighting or terrain was edited. No non-script differences against ae2 were discovered; no exhaustive ae2 binary/content comparison was performed.

## Publish and local copy

File > Publish to Roblox. Studio Output: 11:38:12.225 — Place published; Add publish notes to v248; 11:38:12.253 — Published new changes in VR Mini Golf to Roblox.

Version History newest row, read after publication and again after Download a Copy + explicit refresh:
**October 13, 2026 — v248 — 11:35 AM — <Auto save> — 1 collaborator — Published.**
The displayed 11:35 AM is the saved version timestamp; the actual publish confirmation was 11:38 AM PT. Previous v246 now says Previously Published. History closed without Restore/Revert.

Downloaded via File > Download a Copy to `games/vr-mini-golf/playtest/playtest-lobby-v248.rbxl`. Download emitted “Saving to Roblox...” in Output, but the refreshed history still had v248 as its newest row: **no extra unpublished save observed**.

- Size: 849,772 bytes.
- SHA256: `427f7b8a3d578d9a43946545e9d4bdf893e1576f008a2589ddda266322b28dcf`.
- Read-only binary inspection: all 51 src file contents occur exactly in serialized Script Source properties. Workspace attributes serialize PlaceRole=lobby, SimulateVR=false, GolfTestMode=false (and existing SavedAtm).
- Verification evidence: `playtests/stage-ak/local-copy-verification.json`, `vr-results.json`, `content-baseline.json`, `content-after.json`; screenshots retained locally only.

Studio quit normally. MCP returned `{"studios":[]}` and OS process check found no RobloxStudio process. Lantern Grove remains v9 and Sugarloaf Canyon v19 by the supplied baseline; neither course was opened or independently rechecked. No git push, course saves/publications, new places, or binary commits.

RESULT=PASS LOBBY_LIVE=v248 VH="v248 | Oct 13 2026 11:35 AM PT | <Auto save> | Published" LOBBY_RBXL=games/vr-mini-golf/playtest/playtest-lobby-v248.rbxl
