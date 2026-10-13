# Stage ab: Sugarloaf kit + lighting + cups, Chase's VR feedback, real menu/loading art, lobby portals (2026-10-12)
(The prompt asked for aa-notes.md; stage aa (wrist card + scorecard gear, commit d459940) already wrote that file,
so this stage's notes are here.)

## Published (Codex computer use: Save to Roblox, Publish to Roblox, then Version History read in Studio)
| Place | Place ID | Version | Version History newest row |
|---|---|---|---|
| Sugarloaf Canyon | 124440050576723 | **v19** (v5 before; Team Create auto-saves in between) | v19, Oct 12 2026 5:37 PM, Published |
| Lantern Grove | 91438142503824 | **v9** (v7 before) | v9, Oct 12 2026 5:55 PM, Published |
| Lobby "VR Mini Golf" (start place) | 87725688219952 | **v246** (v244 before) | v246, Oct 12 2026 6:06 PM, Published |
One place open at a time. Every place got the full src/ push (`run_playtests.py push $(find src -name '*.luau')`) right before its publish. No Studio quit hung this time.
Logs: logs/stages/ab-publish-{sc,lg,lobby}.log. (First SC try: Codex read Team Create's NetworkClient as "in a playtest" and stopped; the prompt now says that's normal in Edit.)

## Shared code (src/, all three places)
- **Chase VR 1:10 PM feedback**
  - Wrist card works on **either wrist** (VRControls picks the wrist you look at while the card is hidden, off hand wins ties; `HUD.wristLookScore`, `HUD.isWristShown`). The putting-stance gate doesn't apply to the club-hand wrist (that hand is at your face, not putting).
  - Wrist MENU / SCORES pills: already gone in stage aa.
  - **No thumbstick-click menu at all** (FrontEnd's ButtonL3 handler removed; VRControls no longer passes L3 through an open menu). VR way in: B / Y scorecard -> gear -> Settings -> Back -> title. Help and footer text updated.
  - **Club setup**: the stick no longer moves the head on the ground. The marker stays where the head was when setup started and your hand angle sets the shaft (as before). **Stick LEFT / RIGHT turns the putter head yaw about the shaft** (±30°, 25°/s), saved with the fit as `headYaw` (server ClubSetup validates/clamps ±45; old saves read 0).
  - **Putter head** is level on the ground only on / near it: level up to 0.15 studs over its rest height, rigid with the club from 0.6, smoothstep blend between (`HEAD_LEVEL_NEAR/FAR`). Rigid keeps the club-frame relation from the last grounded frame.
- **Real UI art** (assets/vr-mini-golf/ui/menu, ui/loading; IDs in tools/stage_ab_assets.json and Config.UI): MenuFrame 101738563295695, CloseX 136135028155789, MenuButton 120033471344558 (round 128x128 badge, no label now; the top-right button is square), LoadingLanternGrove 126025818593472, LoadingSugarloaf 107743406289905 (loading_sugarloaf.png), LoadingAurora 133372645732228 (for later). Stand-ins retired.
- **CourseLighting**: Game Art Bot's Sugarloaf preset (the Sugarloaf place's own Lighting holds the same values, set in Edit).
- **SugarloafGondola** (new LocalScript): moves the tagged cabin along the manifest ride (two parabolic spans per line, 6 studs/s, 8 s dwell each end) from `GetServerTimeNow`, so every client sees the same cabin. Measured 5.95 studs/s in play.
- Harness: GolfTest `cupdrop` part (3 gentle putts from 1.4 studs, must sink; refused hits skipped), the test lane and physics header no longer assume `workspace.Course` (the Sugarloaf place has only CourseSugarloaf; before this every Sugarloaf-place harness run hung). VRControls Studio hooks `headBlend`, `wrist "club"/"down"`, `state.scorecard/menuOpen`. tools/stage_ab_vr.py runs the VR checks.

## Sugarloaf Canyon place
- **Pass 6 kit imported**: 213 FBX merged by tools/merge_fbx_for_import.py (generalized stage w script) into fbx/kit_merged_pass6/sugarloaf_kit_pass6_{a,b,c}.fbx (geometry/texture round trip PASS; the only "FAIL" lines are shared-material names). Codex imported the 3 files. The importer auto-scaled them x2.93 / x16.15 / x3.30 and turned them 180°; `SugarloafBuilder.PrepareKit(roots, 180)` puts every MeshPart back from the manifest (size + centre), keeps the material/colour/Neon/CastShadow rules, decoration only (no collide/query/touch). `PlaceKit()` placed **874 instances (1530 MeshParts)** into CourseSugarloaf.Kit at SugarloafLayout.offset. Data: CourseData.SugarloafKit (+ SugarloafKitFiles1/2: Studio caps a script Source at 200,000 chars) from tools/sugarloaf_kit_to_lua.py. Checked by eye: trading post sign reads right, gondola line from the raised bottom station, hoodoos, water tower, balloons.
- **Lighting preset** (Edit, Lighting service): ClockTime 16.3 + lat 17 (sun bearing 277.2 / elev 25.3), Brightness 2.2, Ambient #6B4A52, OutdoorAmbient #B07A6A, ColorShift_Top #FFC890, EnvDiffuse 0.6, EnvSpec 0.4; Atmosphere .38/.15 #FFB98A #C2607A glare .6 haze 2.2; Sky textures blank (plain), SunAngularSize 18; ColorCorrection (renamed SugarloafGrade) tint #FFE9D6 sat .12 contrast .08; SunRays .12/.6; Bloom .6/24/.95.
- **Cups (P1)**: the Terrain sat inside the 0.35-deep cups (WorldBuilder.CarveHoles capped it 0.1 under the CupPlate top). H8/H9/H11/H12/H13/H17 had it at the rim, H1-H5 0.06-0.19 down. New `WorldBuilder.CapUnderCup` (in CarveHoles) takes the voxels within 3 studs of each cup down to cup depth + 0.6 + a 1.5 "surface step" bias. Measured: the smoothed Terrain surface steps (a 0.76 voxel under full neighbours reads at the rim, 0.5 drops it 2 studs), and Terrain collision only updates a frame after WriteVoxels. Every cup now has ≥0.40 (most 1-2.6) of air under the rim; the CupPlate bottom stops the ball as designed. The same bias re-caps felt pieces the Terrain still reached: **H8's washboard "dip" troughs were filled flat by Terrain at 70** and now play as designed; H15 lower_tier intrusions (1.08 above felt, already in stage w) are down to 0.75 and all inside walls. `python3 tools/world_terrain.py --sugarloaf` rebuilt the Terrain with it.
- **Tests** (playtests/stage-ab/sc-final-{a,b}): **cup drop 18/18 holes, 54/54 putts sunk**. Stuck sweep (8 random shots per hole + 6 slow rollers on each mover hole: H6, H9, H11, H14, H17): **0 escapes, 0 lost balls**; flags: H8 2x "stuck-3s" = the ball settles in a washboard trough and the game declares rest after ~3.3 s (normal 0.5 s; the troughs used to be filled), H15 3x "forcedrest" = ball against dune_rail2 on the dune slope, the game's wedge handling rests it (playable). Desktop smoke PASS (smoke-sc-desktop.txt). VR checks PASS (vr-sc). 0 console errors/warnings in every run.

## Lantern Grove place
- **H7 block rate**: 10/24 = **41.7%** in two runs (blockrate, 24 intended-line shots; stage w 45.8%). In range, nothing changed.
- **H9 hidden stone dup**: the bank_backing_stone's Limestone face sat coplanar inside Rail_bank1_backing; removed (oak cap + moss stay). props_overrides.json `hide` (new PropsBuilder field) keeps it out of rebuilds.
- **H8 floating stone (1.66 up)**: the bank2 stone hung 9 studs past the end of its bank over lower terrain (local z -49.775 vs the backing's -40.775); moved onto the bank, bottom 0.02 over the felt like bank1's. props_overrides.json.
- **H8 cream #DDD3BE rails**: the 17 plain rails are limestone #B8AFA0 like H1-H7; CourseBuilder no longer applies the old H8 skin block colour (cap kept).
- **Tests**: LG 9/9 regression (run progress, SimulateVR: 9/9 sunk, ball 0 from next tee, VR rig 1.5, course complete + final scorecard), desktop smoke PASS, VR checks PASS (vr-lg). 0 console errors.

## Lobby place
- **Portal kit** (lobby/boardwalk/models pass 10: 3 arches, 10 lanterns, Aurora snowpuff + crown, portal quads, aprons, per-course scenery): merged into fbx_merged/lobby_portals_pass10.fbx, imported by Codex; the importer scaled it x73.96 (undone), `LobbyBuilder.PrepareLibrary()` then `Build()` (271 instances, 0 missing). Crown Glow_Tips Neon #9FE6F2 (manifest); Sugarloaf candy crystals a low glow (plastic with their vertex colours + one dim pink PointLight, not full Neon); arch lanterns CastShadow off. The portal quads are now the glowing surface (Neon, course colour; Aurora dim icy), the walk-in triggers are invisible. tools/lobby_to_lua.py handles the pass 10 text "motion" notes. Fix: PrepareLibrary picked yaw 0 for single-mesh props (any yaw fits); 5 were turned by hand and the decisive test now needs two meshes with different XZ centres.
- **Default VR controls**: the lobby runs no VRControls; Roblox's own VR camera/locomotion/laser pointer (VRService LaserPointer = Pointer, controller models on, default PlayerModule, CameraType Custom, walk speed 16 when the menu is closed). Checked by code path + settings + smoke; there's no headset or VR emulation on the Mini, so not on a headset.
- **Tests**: lobby smoke desktop + iPhone 17 Pro PASS (cards and walking through both new arches request the right place and show the real loading art), 0 console errors.

## Not done / limits
- **Round 9 report** (/workspace/writerbot/vr-minigolf-post/playtest-bot/round9/round9-findings-v235.md) isn't reachable from the Mini (no /workspace here, same as stage z), so its items weren't read. H7 was measured instead.
- Not checked on a headset: either-wrist card, head yaw, head blend, lobby VR (simulated VR only).
- The H8 trough rest takes ~3.3 s; arch lantern sway / snowpuff bob from the pass 10 notes isn't animated; old stage w part props around Sugarloaf holes (holes.json Decor) are kept alongside the kit.
- Live cross-place teleports still untested outside Studio (stage z limit).
