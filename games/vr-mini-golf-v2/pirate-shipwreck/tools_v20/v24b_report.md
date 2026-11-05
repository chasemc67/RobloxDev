# v24b report: publish the new TestCourseAllowlist (MetavrseBuilder 1818120139 + MetavrsePlumber 2021224569)

Working log; summary at the end.

## A. Preflight (2026-11-01 ~21:57Z)
- Repo ~/src/vr-mini-golf-v2 main @ 98cb502 (code 00280d8). `tools/stamp`: sha 98cb502 dirty=false builderHash 0716f229a84e (stampedAt 21:57:19Z). Rojo 7.7.1 on :34872.
- Pid 15860 (Workshop v4, MCP 4be43a8a): Rojo had already synced the new Config (allow-list {1818120139,2021224569}). File > Close Place → "Save changes to Workshop?" → **Don't Save** (cliclick at (1005,518) after the frontmost check; a System Events `click at` did not reach the Qt dialog). Quit the empty pid 15860.

## B. Pirate Shipwreck (131316561222931)
- Protocol open → pid **31723** (no resources dialog), MCP 53ca76b6. Log `…20261101T215853Z_Studio_5d7a4_last.log`: `version=24`.
- Edit: BuildInfo 98cb502 dirty false; Config.TestCourseAllowlist {1818120139, 2021224569}; Workspace.Gravity 196.2; TrunkColliders 706; HttpEnabled false; user 1818120139.
- World = v24: **chk20 ALL EXPECTED GREEN** (meshparts 2922 / instances 4482 / pointlights 74), **sig16b rows=4145 desc=4231 hash=37177214 ×2** (same as the v24 publish).
- Play server: allow-list #2, table.find 1→1818120139 / 2→2021224569, nil for 1 and 12345; isTester true/true/false/false; player CanTestCourses true, Exploring true; PlaceTeleport.allowed true; Gravity 196.2; felts 18 solid; TrunkColliders 706 (`shots_v24b/allowlist_pirate_v24b.txt`).
- Client: character on rock_l@Set (-371.8,189.5): feet 17.48 = rock top; jump apex +7.31; landed 17.48 on Plastic (rock); ExploreHUD on (`pirate_explore_v24b.jpg`).
- Console: Boot server/client lines (sha 98cb502), the known 203785492 warning ×3, 0 errors.
- After Stop: attributes HutTextureId + PlaceRole only, no VRDebug / GolfTestAPI, HttpEnabled false.
- Save to Roblox: `Saved new changes in "Pirate Shipwreck" to Roblox.` 22:00:45Z. Publish: **`→ Add publish notes to v25` / `Published new changes in "Pirate Shipwreck" to Roblox.` 22:01:06Z = 14:01:06 PST.**
- Close Place (no prompt), quit pid 31723, reopen → pid **36643**, log `…20261101T220146Z_Studio_7cd76_last.log` **`version=25`**. Reopened: sha 98cb502 dirty false, allow-list {1818120139, 2021224569}, Gravity 196.2, TrunkColliders 706. **24 → 25.**

PIRATE_PUBLISHED_V25

## C. Test Course (92186005456885)
- Closed Pirate (no prompt), quit pid 36643, protocol open → pid **39122**, MCP a6bd3398, log `…20261101T220310Z_Studio_58417_last.log` `version=20`.
- Edit: sha 98cb502 dirty false; allow-list {1818120139, 2021224569}; PlaceRole test_course; HttpEnabled false. **Smoke PASS** (3 holes fresh, 48 grounded, groundFresh); builderHash unchanged, so no rebuild.
- Play server: allow-list #2; table.find 1 / 2 for the two ids, nil for 1 and 12345; isTester true/true/false/false; player CanTestCourses true; allowed(player, pirate_shipwreck) true; **Workspace.Gravity 32.7** (not exploring); play-server smoke PASS.
- Client: GolfTest **explore 2D 19/19 PASS**. Gravity timeline (client): `0.0s 32.7/nil → 4.8s 196.2/true → 11.2s 32.7/false → 15.4s 196.2/true → 15.8s 32.7/false`.
- Console: Boot lines (sha 98cb502), `[CourseRuntime] course: 3 holes`, the known 203785492 warning ×3, GOLFTEST lines; 0 errors.
- After Stop: Workspace only PlaceRole; no GolfTestAPI / VRDebug; HttpEnabled false.
- Save to Roblox printed the publish itself this time: **`Published new changes in "Test Course" to Roblox.` / `→ Add publish notes to v21` 22:04:46Z = 14:04:46 PST.** The File > Publish click 15 s later logged nothing (nothing new to publish).
- Close Place (no prompt), quit pid 39122, reopen → pid **43071**, log `…20261101T220525Z_Studio_3012b_last.log` **`version=21`**; sha 98cb502, allow-list correct, smoke PASS (48). **20 → 21.**

## D. Workshop (85191839793106)
- Closed the Test Course (no prompt), quit pid 43071, protocol open → pid **44370**, MCP cd859b5a, log `…20261101T220612Z_Studio_e81bb_last.log` `version=4`.
- Edit: sha 98cb502 dirty false; allow-list {1818120139, 2021224569}; only PlaceRole=workshop; HttpEnabled false.
- Play server: allow-list #2; table.find 1 / 2, nil for 1 and 12345; isTester true/true/false/false; CanTestCourses true; **Workspace.Gravity 32.7**. Loaded hole ramp-ice; **GroundHash 9424bad63851… == Ground.hash(entry.ground, Hole01)**; **Ground.check pass, 15/15** (same as v23). Smoke doesn't apply to the Workshop (p4 D2).
- Console: Boot lines (sha 98cb502), `[CourseRuntime] Workshop: built ramp-ice`, the known warning ×3. One error line, `Value is not a valid member of ModuleScript "ReplicatedStorage.Data.places"` (Script 'AssistantCommand', line 9). That was my own first check script (a typo, `.Value` on the places module), not game code. The game itself logged 0 errors.
- After Stop: only PlaceRole, no Course left over (runtime-built), no GolfTestAPI, HttpEnabled false.
- Save to Roblox, then Publish: **`Published new changes in "Workshop" to Roblox.` / `→ Add publish notes to v5` 22:07:11Z = 14:07:11 PST.**
- Close Place (no prompt), quit pid 44370, reopen → pid **47081**, log `…20261101T220747Z_Studio_b058a_last.log` **`version=5`**; sha 98cb502, allow-list correct, PlaceRole workshop. **4 → 5.**

## E. Lobby "VR Mini Golf V2" (92425959637314)
- Closed the Workshop (no prompt), quit pid 47081, protocol open → pid **48300**, MCP df358bb6, log `…20261101T220830Z_Studio_2ece1_last.log` `version=19`.
- Edit: sha 98cb502 dirty false; allow-list {1818120139, 2021224569}; only PlaceRole=lobby; HttpEnabled false; **smoke PASS**.
- Play server: allow-list #2; table.find 1 / 2, nil for 1 and 12345; isTester true/true/false/false; player CanTestCourses true; **PlaceTeleport.allowed(player, "pirate_shipwreck") = true** (I did not click the button or teleport); **Workspace.Gravity 32.7**.
- 2D Settings, opened with real mouse clicks (Scorecard (C) → Settings): rows Sound effects, Camera speed, Debug: ball, **Test courses** (`Row_testCourses`, button `testCourses_pirate_shipwreck` "Pirate Shipwreck"), all TextFits, inside the panel. Shot `lobby_settings_testcourses_v24b.jpg`.
- Console: Boot lines (sha 98cb502), the known warning ×3, 0 errors.
- After Stop: only PlaceRole, no LobbyPads / GolfTestAPI left, HttpEnabled false.
- Save to Roblox: `Saved new changes in "VR Mini Golf V2" to Roblox.` 22:09:49Z. Publish: **`Published new changes in "VR Mini Golf V2" to Roblox.` / `→ Add publish notes to v20` 22:10:06Z = 14:10:06 PST.**
- Close Place (no prompt), quit pid 48300, reopen → pid **52091**, MCP 41c2bf50, log `…20261101T221043Z_Studio_6825c_last.log` **`version=20`**; sha 98cb502, allow-list correct, smoke PASS. **19 → 20.**

## F. Deploys rows
- `docs/deploys.md`: 4 rows (Pirate Shipwreck v25 14:01, Test Course v21 14:04, Workshop v5 14:07, Lobby v20 14:10; times PST like the earlier 2026-11-01 rows; SHA 98cb502b933d711098b8d6fb38948553534c2bdd). **Commit 0bedef4 "docs: add allow-list deploys rows"**, local only, not pushed.
- Re-stamped: BuildInfo 0bedef4 dirty=false (gitignored). Rojo will sync that stamp into the open Lobby session (pid 52091); it stays unsaved and unpublished.

# Summary

**Result: DONE.** All four places are published privately at **98cb502**. The new `Config.TestCourseAllowlist` = {1818120139 MetavrseBuilder, 2021224569 MetavrsePlumber} was verified on each play server and again after each reopen.

| Place | Version | Publish time (PST) | SHA | Studio log | Allow-list check |
|---|---|---|---|---|---|
| Pirate Shipwreck 131316561222931 | 24 → **25** | 14:01:06 | 98cb502 | "Published new changes in "Pirate Shipwreck"" 22:01:06Z, "Add publish notes to v25"; reopen `version=25` | PASS (play server + reopen); Gravity 196.2; chk20 GREEN, sig16b 37177214, TrunkColliders 706, felts solid |
| Test Course 92186005456885 | 20 → **21** | 14:04:46 | 98cb502 | "Published new changes in "Test Course"" 22:04:46Z, v21; reopen `version=21` | PASS; Gravity 32.7 (196.2 only while Exploring); explore 19/19; smoke PASS |
| Workshop 85191839793106 | 4 → **5** | 14:07:11 | 98cb502 | "Published new changes in "Workshop"" 22:07:11Z, v5; reopen `version=5` | PASS; Gravity 32.7; Ground.check 15/15, GroundHash matches |
| Lobby 92425959637314 | 19 → **20** | 14:10:06 | 98cb502 | "Published new changes in "VR Mini Golf V2"" 22:10:06Z, v20; reopen `version=20` | PASS; Gravity 32.7; "Test courses" row visible; allowed(pirate_shipwreck) true; smoke PASS |

On every play server: `#list == 2`, `table.find` = 1 and 2 for the two ids and nil for 1 and 12345, `PlaceTeleport.isTester` true/true/false/false, and the local user 1818120139 has CanTestCourses true (set by the running game).

**Problems / notes**
1. **Test Course:** the publish was logged on the "Save to Roblox" click (22:04:46Z, v21), and the "Publish" click after it logged nothing. On the other three places, Save logged "Saved…" and Publish logged "Published…". Either way each place gained exactly one version (the reopens show 21 / 25 / 5 / 20).
2. **Workshop console:** one error line, from my own check script (`.Value` on the places ModuleScript, Script 'AssistantCommand'). It was not game code, and the game logged 0 errors.
3. **Pid 15860's "Save changes?" dialog:** the System Events `click at` didn't reach the Qt dialog. `cliclick` at (1005,518) after the frontmost check pressed Don't Save.
4. **Experience access:** the Studio start page shows the "VR Mini Golf V2" card tagged **"Playtesters"**, not "Private". I didn't change any access or audience setting in this job (no Manage Audience, no Experience Settings). I'm flagging it in case Chase expects "Private".
5. **Reopen check limit:** Rojo serves live, so the Config read after a reopen is Rojo's synced copy. It's the same file that was verified on the play server before each publish.
6. Creator Hub Version History was not checked in a browser. The versions come from the Studio log and the reopens.
7. No headset, phone or second account: only the local tester user was tested live. Non-tester ids were checked through `table.find` / `PlaceTeleport.isTester`.

**Rules kept:** no Script / LocalScript / ModuleScript was created or edited through the MCP (the Config change is Chase's 00280d8 through Rojo). One place open at a time. All places were published privately with no access changes and no Robux. No Screen Recording prompt appeared. Pid 18508 and the old pids (5180, 30033, 30994, 34084, 61461, 62563, 65929, 78191, 93578) were not touched. GUI input went through `/tmp/p4/p.sh` / `act.sh` (frontmost check) plus one frontmost-checked cliclick. No assets were deleted. The commit is local only: nothing pushed or posted.

**Studio state at the end:** pid **52091** is open on the Lobby v20 (MCP 41c2bf50), with the 0bedef4 BuildInfo stamp unsaved. Pids I opened (or was handed) and quit after they were empty: 15860, 31723, 36643, 39122, 43071, 44370, 47081, 48300. New helper: `/tmp/p4/cycle.sh <pid> <placeId>` (Close Place, quit, protocol reopen, print the log's version).

**Files:** this report; `~/stage/shots_v24b/`: pirate_explore_v24b.jpg, allowlist_pirate_v24b.txt, lobby_settings_testcourses_v24b.jpg, publish_pirate_v24b.txt, publish_testcourse_v24b.txt, publish_workshop_v24b.txt, publish_lobby_v24b.txt. Repo commit 0bedef4.

DONE_V24B
