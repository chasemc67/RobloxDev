# Phase 4 release report (P4): test-course allow-list + free-roam Pirate Shipwreck

Working log (filled in step by step; summary at the end).

## A. Preflight (2026-11-01 ~18:03Z)
- Repo ~/src/vr-mini-golf-v2 main @ e3a1c87 (Merge branch 'test-courses'; Phase 4 commit edf037f). `git status`: only untracked drafts/*.md (pre-existing, outside src/data). `tools/stamp`: sha e3a1c87 dirty=false builderHash 0716f229a84e.
- Rojo: `rojo serve default.project.json` (pid 6233, Rojo 7.7.1, SCREEN v2rojo since 2026-10-31) on :34872, `/api/rojo` answers projectName vr-mini-golf-v2 with the 4 servePlaceIds. It serves the working tree live: the open place got the new BuildInfo (stampedAt 18:03:01Z) and Server.ExploreWorld, so no restart.
- Studio: pid 30870 = MCP ab45911e "Pirate Shipwreck (placeId 131316561222931)", PlaceVersion reads 0 in Edit, log `0.745.0.7451137_20261101T175722Z_Studio_f71ea_last.log` (marker P4_MARKER_7731 landed there; this is the v22 reopen, version=22). Studio user 1818120139 (MetavrseBuilder). Pid 18508 not touched; other old Studio pids (5180, 30033, 30994, 34084, 61461, 62563, 65929, 78191, 93578) untouched.

## B. Pirate Shipwreck (131316561222931), pid 30870
### B0. Sync and baseline (Edit, before Play)
- BuildInfo sha e3a1c87a91bde402557cb6f0dc57527e7d5d2001 == HEAD, dirty false, stampedAt 18:03:01Z; Server.ExploreWorld present; Data.places pirate_shipwreck role=explore access=testers.
- Workspace attribute **PlaceRole was already `pirate_shipwreck`** (set in an earlier world job; deploys v10 row lists it). Nothing to set: the only Workspace attributes are HutTextureId and PlaceRole. I did not write it again.
- World baseline (identical to the v22 report's pre-publish / reopened numbers): chk20 ALL EXPECTED GREEN, meshparts 2962 / instances 3816 / pointlights 74; sig16b rows=3479 desc=3565 hash=26ef2457 x2; terr16b green (hump Air / LeafyGrass 0.26 / Air; Rock 286 / LeafyGrass 0; cliff (115,100,92)).
- Terrain cell counts (new, ReadVoxels res 4 over x -2560..2560, z -2048..2048, y -256..512; 0 non-Air cells on the box edge): nonAir 6728197: Grass 12944, LeafyGrass 275102, Limestone 6101, Rock 2280377, Sand 1630983, Sandstone 9710, Slate 2897, Water 2510083. (`Terrain:CountCellsByMaterial` is not a member in this Studio build.) v22 recorded no whole-terrain cell count, so this is the pre-publish reference for the reopen.

### B1. First Play (sha e3a1c87): 2D passed, VR floor FAILED, one fix
- Server log `[Boot/server] PlaceRole=pirate_shipwreck role=explore sha=e3a1c87…`, client `[Boot/client] PlaceRole=pirate_shipwreck role=explore`. Only other lines: `ContentId: rbxassetid://203785492 failed due to: Asset type does not match requested type` x3 (the known Roblox warning listed in every deploys row; not from our scripts).
- 2D: Exploring true at the first client read; root at (-537.5, 27.80, 238.70) = spawn xz exactly, facing (0.968,0,0.252) = towards spawnLookAt; WalkSpeed 16; ExploreHUD on with FlyButton "Fly (F)" and BackToGolf "Back to lobby"; MoveTo walk 47.1 studs in 3.0 s at 16.0 studs/s; F → PlatformStand + ExploreFlyVelocity, held E 1.6 s → rose 32.3 studs to y 60.13, hovering; F again → landed back on Pad01Plinth y 27.80, Running, WalkSpeed 16. Shots `~/stage/shots_p4/ps_tee_2d.jpg`, `ps_flight_2d.jpg` (first run).
- **SimulateVR (runtime LocalPlayer attribute; ClientBootGen 1→2): mechanics passed, floor wrong.** Toast "Exploring: off-hand stick walks, stick click flies"; left stick walked 5.31 studs; L3 → "Flying (stick click: walk)"; right stick rose 16.33; left stick while flying 12.0 flat; L3 again → "Walking …". **But the playspace origin sat at y 5.3 / 4.7 / 5.9 on the seabed Terrain (-0.06) under the pad, eye at y 10.7 with Pad01Plinth overhead at 17.8**: the VR player spawns and walks inside the hull.
  - Cause: `VR/Club` floorRay only includes GolfSurface, Terrain, Baseplate / SpawnLocation / LobbyPads and Course.Ground. The world has none of those under the pads; its floors are World parts.
  - **Fix (repo, through Rojo, committed locally): 2c83e10 "Phase 4: VR floor stands on world parts in a free-roam world"**: with `Ball.exploreWorld`, `Workspace.World` is a walkable root (queryable parts only). selene 0 / stylua ok. `tools/stamp` 2c83e10 dirty=false; synced into the place (BuildInfo stampedAt 18:09:45Z, Club source has the change).

### B2. Second Play (sha 2c83e10): VR floor fixed; phone panel check FAILED, second fix
- 2D again: walk 47.1, fly +32.0, land 27.80 (shot `ps_flight_2d_b.jpg`).
- SimulateVR: feet on the plinth (camera = eye in SimulateVR, eye 30.20 − head 5.40 = 24.80 = Pad01Plinth top), walk 5.12 with feet 24.80, fly / rise 16.36 / fly-walk 12.06 / walk again. Note: landing from 16 studs up beyond the plinth edge kept the old floor (floor ray reaches 2.2 above / 30 below the current floor; pre-existing in every Explore place), and walking from the seabed towards the 24.8-high plinth goes under it (VR walks through solid geometry by design). Not changed.
- `ui2d` (GolfTestMode at runtime): 18/18 PASS, Explore hint (world) "Exploring: stick to walk, Fly to fly" fits 360 / 390 / 430 (bounds 265 / 348 / 401 × 72), the other three hints fit too.
- **Phone buttons vs touch controls: FAIL.** No harness step covers it, so I read the layout code in StarterPlayer.PlayerModule.ControlModule (TouchJump, ClassicThumbstick, DynamicThumbstick, TouchAbilities). Small screen (min axis ≤ 500, e.g. 750×381): the jump button is 70 @ (W-95, H-90) in the legacy layout, or 72 with a 64 inset = (W-136..W-64, H-136..H-64) in the abilities layout. The Explore panel had Back x W-160..W-10, y H-88..H-48 and Fly at y H-136..H-96, so Back overlaps the jump button in both layouts, and Fly overlaps it in the abilities layout. A jump could press "Back to lobby" (teleport out). The thumbstick (left 40 % / bottom-left) is clear of both buttons.
  - **Fix 2 (repo, Rojo, committed locally): 2165b47 "Phase 4: Explore panel clears the touch jump button"**: `Explore2D` lifts Fly + Back 8 px above `PlayerGui.TouchGui…JumpButton` whenever they overlap horizontally (read every 0.25 s while the panel is up). No TouchGui (desktop) → unchanged. selene 0 / stylua ok.
- VR Settings page in this world: Close, SFX, Club hand, Fit / Reset fit, Debug wrist / pose / ball tuning. No Test courses row (correct: no other tester place), no Back-to-golf row (R51). **There is no way back to the lobby in VR** (R51 specifies the button for 2D only); reported, not changed.
- B5 / B6 PASS (same values as B3).

### B3. Final Play (sha 2165b47): every check
| # | Check | Measured | Result |
|---|---|---|---|
| 1 | Server log, no errors, ExploreWorld | `[Boot/server] PlaceRole=pirate_shipwreck role=explore sha=2165b47…`; `[Boot/client] … role=explore`; only the known `rbxassetid://203785492` warning x3, plus the MCP tool's own "execute_luau changed camera type" notes; Workspace ExploreWorld=true | PASS |
| 2 | 2D: Exploring ≤ 3 s, tee spawn, WalkSpeed 16, HUD, walk 40, fly 30, land; shots | Exploring true at the first client read (game time 6.99 s on the second run; ExploreWorld sets it in PlayerAdded, before the character); root (-537.5, 27.80, 238.70): spawn xz exact, facing spawnLookAt; WalkSpeed 16; ExploreHUD on (Fly (F), Back to lobby); walk 47.0 studs in 3.0 s; F + E → rose 32.0; F → landed y 27.80 Running | PASS (see note a) |
| 3 | SimulateVR at runtime | ClientBootGen 1→2; toast "Exploring: off-hand stick walks, stick click flies"; feet 24.80 at the spawn xz; VRDebug.Stick Thumbstick1 → walked 5.20 (feet 24.80); ButtonL3 → "Flying (stick click: walk)"; Thumbstick2 up → rose 16.34; Thumbstick1 while flying 5.98; L3 → "Walking (stick click: fly)", landed on the place SpawnLocation top 27.00. `VR.exploreState()` is module-only (execute_luau has its own module cache, AGENTS §9), so "exploring" is shown by the toast plus L3 toggling flying, which Club only allows while exploring | PASS (no headset) |
| 4 | Phone hint + buttons | ui2d 19/19, world hint fits 360/390/430; Fly / Back vs a TouchGui JumpButton placed exactly as each PlayerModule layout does (legacy small, legacy large, abilities small, abilities large; IgnoreGuiInset false and true) in this 1292×629 view: overlap 0 px² for both buttons in all 8, 8 px gap, on screen; panel back at (1132,493)/(1132,541) once the TouchGui is gone. Phone-size arithmetic with the same rule (750×381): lift 50 (legacy) / 96 (abilities), Fly top at 195 / 149 px, under the 58 px top bar's bottom, left 40 % (thumbstick) clear | PASS (stand-in TouchGui; no real phone, no Device Emulator) |
| 5 | Access | Config.TestCourseAllowlist {1818120139}; canEnter(1818120139)=true, canEnter(1)=false; allowed(1,pirate_shipwreck)=false, allowed(1818120139,…)=true; isTester true/false; allowed(1,lobby / test_course)=true, (1,workshop)=false; testPlaces=pirate_shipwreck; play player CanTestCourses=true. **Kick path:** Studio never kicks (`not RunService:IsStudio()`), so the kick is checked only through canEnter | PASS |
| 6 | Back to lobby | Real mouse click on ExploreHUD.BackToGolf → `LastTeleportRequest=MetavrseBuilder|lobby|menu|92425959637314`, log `[PlaceTeleport] Studio: skipped teleport of MetavrseBuilder to lobby (place 92425959637314, menu)` | PASS |

Notes:
- a. **The pad 1 felt, base and rims are CanCollide/CanQuery false** (13/13 Blockout Felt parts are non-colliding). The 2D character stands on Pad01Plinth (top 24.8), 2.2 studs below the felt top (27.0), so it is sunk to the knees in the felt (`shots_p4/ps_tee_2d.jpg`). This is world content; the brief says the world must stay unchanged, so I did not touch it.
- b. A "Scorecard (C)" top-bar button shows in the free-roam world (lobby setup); it opens a lobby scorecard. Harmless, reported.
- Shots: `~/stage/shots_p4/ps_tee_2d.jpg` (tee), `ps_flight_2d.jpg`, `ps_flight_2d_b.jpg`, `ps_flight_2d_final.jpg` (in flight, final sha).

### B4. Publish and reopen
- After Stop: Workspace attributes only HutTextureId + PlaceRole; no GolfTestAPI / VRDebug left in ReplicatedStorage (the test flags were LocalPlayer attributes in the play session only); HttpEnabled false; `git status` clean (except the pre-existing untracked drafts/*.md). Studio user 1818120139 = MetavrseBuilder; window title "Pirate Shipwreck - Roblox Studio"; placeId 131316561222931.
- Pre-publish world: meshparts 2962 / instances 3816 / pointlights 74; sig16b 26ef2457; terrain cells identical to B0.
- File > Save to Roblox (System Events on pid 30870, frontmost verified by `/tmp/p4/p.sh`): `Publish succeeded for placeId 131316561222931`, `Saved new changes in "Pirate Shipwreck" to Roblox.` 18:17:19Z.
- File > Publish: **`Published new changes in "Pirate Shipwreck" to Roblox.` 18:17:38.634Z, `→ Add publish notes to v23`.**
- File > Close Place, then `open roblox-studio:1+launchmode:edit+task:EditPlace+placeId:131316561222931+universeId:10771778371` → new pid **65589**. It stopped at Studio's own **"Low System Resources"** dialog (12 Studio instances running); I pressed Continue (System Events, pid 65589 frontmost). I also ran `~/bin/unlock-keychain.sh` while diagnosing it; that was not the cause. Log `0.745.0.7451137_20261101T181807Z_Studio_f1bc9_last.log`: `DataModel Loading …?id=131316561222931&version=23`. MCP studio c36fcc43.
- Reopened: BuildInfo 2165b47 dirty=false; ExploreWorld + both fixes present; PlaceRole kept; chk20 ALL EXPECTED GREEN, meshparts 2962 / instances 3816 / pointlights 74, sig16b rows=3479 desc=3565 hash=26ef2457 x2, terr16b green, terrain cells nonAir 6728197 with every material identical to B0. **World unchanged; version 22 → 23.**

## C. Lobby "VR Mini Golf V2" (92425959637314)
### C0. Open
- Closed Pirate Shipwreck in pid 65589. The first protocol open (pid 73035) hit Studio's **"You have opened the maximum allowed Studio windows"** dialog; I pressed OK (it exited) and **quit pid 30870** (my handed-over session, empty at the Start page after its Close Place) through its Roblox Studio > Quit menu. No other pid touched; 18508 untouched.
- Reopened → pid **75060** (Low System Resources dialog → Continue). Log `0.745.0.7451137_20261101T182337Z_Studio_4947b_last.log`: `DataModel Loading …?id=92425959637314&version=18`. MCP studio c7aabb7f.
- Rojo synced: BuildInfo 2165b47 (stampedAt 18:14:30Z), Server.ExploreWorld present; Workspace attribute PlaceRole=lobby (only attribute).
- **Smoke PASS** `Course.smoke({head=2165b47…, since=now})`: pass true, problems [], dirty false. Without `since` it reported two `Course:21: attempt to index nil with 'HoleFormat'` console errors; **those were my own first two execute_luau calls** (requiring a lone cloned Course module, the mistake docs/phase2h-report.md describes), at 18:24:48 / 18:24:56 local log time, not game code.

### C1. Play (2D, MetavrseBuilder)
| Check | Measured | Result |
|---|---|---|
| Boot | `[Boot/server] PlaceRole=lobby role=lobby sha=2165b47…`; only the known 203785492 warning | PASS |
| lobby-pads (tools/mcp/lobby-pads.luau, Server) | 4/4: workshop at once (0.10 s), test_course after the cooldown 4.18 s after the workshop request, no repeat, fires again after stepping off/on. Pads: Pad_test_course, Pad_workshop (no Pirate Shipwreck pad) | PASS |
| CanTestCourses | true (player attribute) | PASS |
| Settings row (2D, real mouse clicks Scorecard (C) → Settings) | Row "Test courses" `Row_testCourses` with `testCourses_pirate_shipwreck` "Pirate Shipwreck", on screen, TextFits; shot `shots_p4/lobby_settings_2d.jpg` | PASS |
| Click it (real mouse click) | LastTeleportRequest `MetavrseBuilder|test_course|pad|92186005456885` → **`MetavrseBuilder|pirate_shipwreck|menu|131316561222931`**; log `[PlaceTeleport] Studio: skipped teleport of MetavrseBuilder to pirate_shipwreck (place 131316561222931, menu)` | PASS |
| Negative: CanTestCourses false + allowlist emptied (server, runtime) → Settings reopened (2D) | No Row_testCourses / no button; labels Settings, Sound effects, Camera speed, Debug: ball | PASS |
| Negative, VR Settings page (SimulateVR at runtime, ClientBootGen 1→2, ButtonA opens) | No Row_testCourses; rows Sound, Club hand, Club fit, Debug wrist / pose / ball | PASS |
| Negative: RequestTeleport("pirate_shipwreck") from the client | **Not refused by the running game**: TeleportStatus start/skipped and a second `skipped teleport … pirate_shipwreck (menu)` line, no Notice. Cause: execute_luau's `require(Config)` on the play server returns its own copy (AGENTS §9 "execute_luau's require doesn't share the game scripts' module cache"), so removing 1818120139 there did not reach the game's PlaceTeleport. The server's runtime allow-list can't be edited from the MCP without a code change, so this step could not be run as written | NOT RUN AS WRITTEN (test limit, not a code fault) |
| Negative, same refusal code with the real player | A clone of Server.PlaceTeleport, which reads the emptied Config copy: `allowed(player)` false; `send(player,"pirate_shipwreck","menu")` → ok=false, why=denied; the real client received Notice **"That course is for testers only"** (kind bad, shown in GolfHUD.Message); LastTeleportRequest unchanged | PASS |
| Next Play | CanTestCourses true; ui2d 15/15 (same as the v18 deploy row), the row seen on the Settings page during it; SimulateVR: VR Settings has Row_testCourses + "Pirate Shipwreck" button, inside the 660×540 canvas, TextFits, lowest element bottom 530 / 540; shot `shots_p4/lobby_settings_vr.jpg` | PASS |
| vrui (SimulateVR) | **91/91** PASS in 171 s, watcher ok (10,239 frames; beamWithoutUi 0, uiWithoutBeam 0, arcWithoutAim 0, coreLaserOn 0) — same count as the v18 deploy row | PASS |

### C2. Publish
- After Stop: Workspace only PlaceRole=lobby; no GolfTestAPI / VRDebug / Remotes in the Edit place; LobbyPads not saved (runtime); HttpEnabled false; git clean; Studio user 1818120139; window "VR Mini Golf V2 - Roblox Studio"; placeId 92425959637314.
- File > Save to Roblox, then File > Publish (pid 75060, frontmost verified): **`Published new changes in "VR Mini Golf V2" to Roblox.` 18:31:34.045Z, `→ Add publish notes to v19`** (`Publish succeeded for placeId 92425959637314`).
- Quit my empty pid 65589. Close Place in 75060 → protocol open → pid **88840** (Low System Resources → Continue). Log `…183205Z_Studio_1042f_last.log`: `DataModel Loading …?id=92425959637314&version=19`. MCP e1fc5e9b. Reopened: sha 2165b47, ExploreWorld + SettingsModel.addTestCourses present, PlaceRole=lobby, **smoke PASS** (no `since` needed). **Version 18 → 19.**

## D. Test Course (92186005456885) and Workshop (85191839793106)
### D1. Test Course
- Closed the Lobby (pid 88840), protocol open → pid **91677** (Low System Resources → Continue), log `…183339Z_Studio_e4fda_last.log` `version=18`. MCP 6856967a. Rojo synced at once: sha 2165b47.
- **No rebuild:** builderHash 0716f229a84e unchanged; BuildHash Hole01 87f93f05 / Hole02 283bf312 / Hole03 eb0bf1bb + GroundHash 91ab8548 fresh (same as v17/v18). **Smoke PASS** in Edit (48/48 grounded) and on the play server.
- Play (no flags in the place; GolfTestMode / SimulateVR set at runtime on the LocalPlayer):

| Check | Measured | vs last row (v18) | Result |
|---|---|---|---|
| CanTestCourses | true | new | PASS |
| explore 2D (GolfTest `explore`) | **19/19** | 19/19 | PASS |
| ui2d | **22/22** | 20/20: +2 steps = the new `world` / `worldKeyboard` hint checks (the hint table grew); no new failure | PASS |
| 2D Settings layout | Rows Sound, Camera speed, Explore, Debug: ball, **Test courses** ("Pirate Shipwreck"); every element inside the panel (313..978 × 48..580 in 1292×687), all TextFits; shot `shots_p4/tc_settings_2d.jpg` | new row | PASS |
| vrui (SimulateVR) | **112/112** in ~220 s | 112/112 | PASS |
| explore VR | **13/13** | 13/13 | PASS |
| VR Settings page height | 660×540 canvas: Row_SFXVolume 74-114 … Row_ballTuning 374-414, **Row_testCourses 424-464**, footer to 530; nothing outside or clipped (only the laser's PointerDot lies past the edge, not a row) | new row fits | PASS |
| Console | 0 server errors; only the known 203785492 warning | same | PASS |

- After Stop: Workspace only PlaceRole=test_course; no harness leftovers; HttpEnabled false; git clean; window "Test Course - Roblox Studio"; user 1818120139.
- Save to Roblox (`Saved new changes in "Test Course" to Roblox.` 18:40:23Z), Publish: **`Published new changes in "Test Course" to Roblox.` 18:40:38.993Z, `→ Add publish notes to v19`.**
- Quit my empty pid 88840; Close Place in 91677; reopen → pid **4144**, log `…184106Z_Studio_b8b30_last.log` `version=19`; MCP 4b4e4344: sha 2165b47, the Phase 4 code + both fixes present, smoke PASS (3 holes fresh, 48 grounded). **Version 18 → 19.**

### D2. Workshop
- Closed the Test Course (pid 4144), protocol open → pid **6503** (Low System Resources → Continue), log `…184231Z_Studio_ab435_last.log` `version=2`. MCP 24ebf537. Rojo synced: sha 2165b47; Edit place Camera / Baseplate / Terrain / SpawnLocation, only PlaceRole=workshop.
- **`Course.smoke` doesn't fit the Workshop.** Its places.json entry has `ground` but no `holes`, and the ground is built at runtime around the loaded hole (CourseRuntime.luau:77). In Edit, smoke says `Course.Ground is missing: run Course.rebuild("all")`, but `Course.rebuild` asserts `entry.holes`, so it can't run here (and there are no baked holes, so no BuildHash can be stale). On a play server smoke says `GroundHash is stale` (it hashes 0 holes; grounded checked 0). **Checked directly on the play server instead:** GroundHash 9424bad63851 == `Ground.hash(ground, loaded hole straight-walls)`; `Ground.check` pass, 13/13; `tools/mcp/workshop-switch.luau` 3/3 (one Hole01 after 3 back-to-back requests, last request loaded, 0 stray movers); CanTestCourses true; 0 console errors. This is a gap in smoke / AGENTS §10 for the Workshop, not caused by Phase 4; I did not change AGENTS.md or the code.
- Save to Roblox, Publish: **`Published new changes in "Workshop" to Roblox.` 18:44:32.639Z, `→ Add publish notes to v3`.**
- Quit my empty pid 4144; Close Place in 6503; reopen → pid **10698**, log `…184502Z_Studio_6c243_last.log` `version=3`; MCP 64890c20: sha 2165b47, ExploreWorld + both fixes + Test courses code present, PlaceRole=workshop. **Version 2 → 3.** Then quit my empty pid 6503.

## E. Deploys rows
- `docs/deploys.md`: 4 rows (Pirate Shipwreck v23, Lobby v19, Test Course v19, Workshop v3), times PST, SHA 2165b47bd496c5baec70cda5b12e248015844f2c. **Commit 42d7078 "docs: add Phase 4 deploys rows"** (local; not pushed; the branch is 27 commits ahead of origin/main). Nothing else in docs changed. Re-stamped: BuildInfo 42d7078 (gitignored). Rojo will sync that stamp into the open Workshop session (pid 10698); that change is unsaved and unpublished, as in v21 / v22.
- Not changed, for Chase: AGENTS.md "Places" still says `pirate_shipwreck` "needs PlaceRole = pirate_shipwreck set once" (it is set), and §10's "run smoke" can't pass on the Workshop as written (D2).

# Summary

**Result: all 4 places published privately at 2165b47 (Phase 4 + two fixes found during testing).**

| Place | Before → after | Studio log | SHA |
|---|---|---|---|
| Pirate Shipwreck 131316561222931 | 22 → **23** | "Published new changes in "Pirate Shipwreck"" 18:17:38Z, "Add publish notes to v23"; reopen `version=23` | 2165b47 |
| Lobby "VR Mini Golf V2" 92425959637314 | 18 → **19** | "Published new changes in "VR Mini Golf V2"" 18:31:34Z, v19; reopen `version=19` | 2165b47 |
| Test Course 92186005456885 | 18 → **19** | "Published new changes in "Test Course"" 18:40:38Z, v19; reopen `version=19` | 2165b47 |
| Workshop 85191839793106 | 2 → **3** | "Published new changes in "Workshop"" 18:44:32Z, v3; reopen `version=3` | 2165b47 |

Version numbers come from the Studio log and the reopen's `DataModel Loading …&version=N`. Creator Hub Version History was not checked in a browser.

**What existed vs what was added**
- Existed (R27): Explore on course / Workshop places (VR stick walk / stick-click fly, 2D WASD / F / Space / E / Q, phone thumbstick + Fly + Back), the Settings Explore row, PlaceTeleport with the Workshop allow-list.
- Added in edf037f (Phase 4, merged e3a1c87): places.json role `explore` + `access = "testers"` + spawn / spawnLookAt for pirate_shipwreck; Server.ExploreWorld (Exploring from join, spawn pivot, kick of non-listed users outside Studio, `canEnter`); client boots the world as the lobby with `Ball.lobby(true)` and the Explore views ("Back to lobby"); `Config.TestCourseAllowlist`; PlaceTeleport `isTester` / `testPlaces` / testers refusal + Notice / `CanTestCourses`; Settings row "Test courses".
- Added by this job (both through Rojo, committed locally):
  1. **2c83e10** VR floor: in an explore world, `Workspace.World` is walkable for the VR floor ray. Before this, SimulateVR put the player on the seabed under pad 1, inside the hull.
  2. **2165b47** Explore2D: on touch, the Fly / Back panel lifts 8 px above Roblox's jump button. Before this, "Back to lobby" / "Back to golf" sat on the phone jump button in both PlayerModule layouts.

**UserIds in `Config.TestCourseAllowlist`:** 1818120139 (MetavrseBuilder) only. Chase's personal ID is still the commented TODO line `-- 0, -- Chase's personal account`. 2021224569 (MetavrsePlumber) is deliberately left out, per the comment.

**Checks:** every check in B (B3 table) and C (C1 table), and the D tables, PASS on 2165b47, with these exceptions:
- C: the negative "RequestTeleport from the client" step **could not be run as written**. execute_luau gets its own copy of `Config` on the play server (AGENTS §9), so emptying the allow-list there didn't reach the running PlaceTeleport, and the request went through. The same refusal code was exercised with the real player through a PlaceTeleport clone that reads the emptied Config: denied, Notice "That course is for testers only" on the client, no request recorded. The row-hiding half (2D + VR) was tested for real.
- D: Workshop smoke doesn't apply (D2); runtime ground was checked directly instead.

**Could not test**
- No headset: VR is SimulateVR only (stick / button events through ReplicatedStorage.VRDebug).
- No real phone and no Device Emulator: the panel / jump-button check uses a stand-in TouchGui JumpButton in each PlayerModule layout, plus arithmetic for 750×381. Hint fit is the ui2d harness.
- No second account: the kick path is checked only through `ExploreWorld.canEnter` (Studio never kicks), and the non-tester teleport path only through unit calls and the clone above.
- Real teleports (Studio skips them; recorded via LastTeleportRequest).

**Problems / open items for Chase**
1. **VR has no way back to the lobby from Pirate Shipwreck.** R51 only specifies a 2D "Back to lobby" button, and the VR Settings page has no such row.
2. **Pad felt is not solid in Pirate Shipwreck.** The pad Felt / Base / Rims are CanCollide and CanQuery off (13/13 felts), so a 2D player stands on the plinth 2.2 studs under the felt top, sunk to the knees (`shots_p4/ps_tee_2d.jpg`). This is world content; I left it unchanged as the brief asks.
3. A "Scorecard (C)" button shows in the free-roam world (lobby scorecard). Harmless.
4. VR flying: landing more than ~30 studs above the ground keeps the old floor height, and walking from low ground into a tall plinth goes under it. Both are pre-existing locomotion behaviour in every Explore place; not changed.
5. Studio housekeeping: Studio hit "maximum allowed Studio windows" (12 instances open). I quit only Studio instances that were mine and empty at the Start page: 30870 (handed to me, after its Close Place), 65589, 75060, 88840, 91677, 4144, 6503. Every reopen showed Studio's own "Low System Resources" dialog; I pressed Continue. Pid 18508 and the other older pids (5180, 30033, 30994, 34084, 61461, 62563, 65929, 78191, 93578) were not touched. No Screen Recording prompt appeared. I ran `~/bin/unlock-keychain.sh` once while diagnosing the first stuck reopen; it turned out to be the dialog.
6. Smoke in the Lobby first showed two `Course:21` console errors. Those came from my own execute_luau calls, not the game; smoke passed with `since` and again with no `since` on the reopened place.

**Rules kept:** scripts only from Rojo (no Script / LocalScript / ModuleScript created or edited through the MCP; the MCP only read sources and ran test code); one place open at a time; places private, nothing public, no Robux; no Workspace attributes written except runtime test flags on the LocalPlayer in play sessions (PlaceRole on Pirate Shipwreck was already set); nothing deleted (no assets, no Blockout parts); every GUI input went through `/tmp/p4/p.sh` / `act.sh` (activate by pid, then verify the frontmost pid); commits local only, nothing pushed or posted.

**Studio state at the end:** pid 10698 open on the Workshop v3 (MCP 64890c20). Rojo serve (pid 6233) still on :34872.

**Files:** this report; `~/stage/p4s/world_chk.luau`; `~/stage/shots_p4/` (ps_tee_2d, ps_flight_2d, ps_flight_2d_b, ps_flight_2d_final, lobby_settings_2d, lobby_settings_vr, tc_settings_2d); `/tmp/p4/` helpers. Repo commits 2c83e10, 2165b47, 42d7078.

DONE_P4
