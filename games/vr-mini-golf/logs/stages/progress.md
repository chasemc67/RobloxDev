FLYTHROUGH DONE /Users/chase-mini/src/RobloxDev/games/vr-mini-golf/playtests/flythrough/flythrough-v1.mp4 73.4s 42.0MB

## Stage b (2026-10-10, 13:55 PT): team fixes, world terrain check, random-shot sweep, shots, PUBLISHED v43
- Team fixes: slide clearance 0.5 studs to rails (CourseBuilder SLIDE_CLEARANCE, per-mover `clearance`); H7 log already 1.5/2.6 studs clear at +-6, H8 door clamped [-2.5,2.5] -> [-1.4,1.4]. Pin nudge after 1.5 s contact (Config.PinNudgeTime; riding a mover still 0.5 s). Cup capture verified 1.6/0.3 = 5.33 studs/s. H9 Lantern Knot: teleport entry + new knot-hole visual (dark hollow, bark ring, no collision) at hole-local (6.5, 1.0, -23.0). Teleport exit FX ~0.3 s (chime, firefly burst, flash; BallController.teleportFx). H9 gate (and any part coming down onto the ball) pushes the ball out along its thin axis (pushFromDescending). Auto-reset after 3 s stuck on every hole with movers/teleports (H4, H6, H7, H8, H9; hole attribute AutoResetStill from Config or spec `auto_reset_still`).
- One-step re-import: `python3 tools/holes_to_lua.py --push --build` now rebuilds the course, re-places the props and re-carves/checks the terrain.
- Terrain (written earlier from terrain-4stud.json): re-carved after the rebuild, 0 intrusions on all 9 holes; H9 hollow-tree interior clear (only the floor, <=1.9 studs over the felt bottom).
- Sweep: 180 random shots, 0 escapes, 0 stuck, 0 auto-resets, 0 nudges, 0 console errors (playtests/lantern-v1/sweep-b/README.md). tpcheck: H8 exit <=8.5 never overshoots off the back rail.
- Shots: playtests/lantern-v1/overview.png, overview_aerial.png, hole01..09.png (Studio MCP capture, Edit mode). Nothing glaring.
- For Game Art Bot: the H9 Lantern Knot exit holes out at entry speeds 4-10 studs/s (5 of 5 in tpcheck) - balance call is theirs.
- PUBLISHED v43, 2026-10-10 1:52 PM PT (Codex computer use, File > Publish to Roblox): "Place published. Friends and playtesters can now play this place in Roblox." Audience unchanged. Studio left in Edit mode, saved.

## Stage c (2026-10-10, 16:50 PT): spec v2 re-import, props pass 6 + world pieces, SAVED (not published)
- **Spec v2** (Game Art Bot 13:39) copied over holes.json, hNN-notes.md, props.md, world/world.json, world/terrain-4stud.json (v1 kept in `assets/.../lantern-grove/spec-v1/`). Regenerated with the existing one-step tools (`holes_to_lua.py --push --build`, `world_to_lua.py`, `world_terrain.py`, `WorldBuilder.BuildScenery`): course, terrain (0 intrusions on all 9 holes), H7-H8 and H8-H9 walkways from the new paths.
- Builder support added for v2 (all data-driven):
  - `swing` movers (H9 lantern pendulum: hinge + 35 sin(360t/4), server error <= 1.1 deg);
  - hazard `reset: respawn` (H5 stream miss -> bridge entry; part-built glowing stone);
  - `cup.flag` (pole/banner size, colour, turned to the tee);
  - `end_clearance`;
  - spinner puffballs follow the spec arms.
- **H8 door pockets**: the slide clamp now treats a wall the blocker passes fully through as a pocket, so the door travels the spec +-3.5. BallController `pushFromSliding` moves a ball sideways off a blocker end that is closing on a wall, and bumps it ahead on open felt (resting client balls did not get the contact). h8door phase-aware: 6/6 clean.
- **H9 tunnel dip**: two auto-resets in the V between the sloped pieces. Fix: BallController `valleyPoint` rests a slow ball on the crease.
- **Stroke timeout**: Config.StrokeTimeout = 20 s. A stroke still moving after 20 s resets to the stroke start (AutoReset reason `timeout`, counted separately by the sweep).
- **Props**: 3D Model Bot pass 6 (14:35, covers spec v2) via `props_to_lua.py`.
  - Imported with the Studio 3D Importer (Codex computer use, one file at a time; the picker refuses multi-select): 23 new/changed props, 3 card props and all 51 world-piece FBX (39 pieces). 0 failures, no Robux.
  - New `WorldBuilder.PrepareWorldLibrary/PlaceWorldPieces` + `tools/world_pieces_to_lua.py` (CourseData.WorldPieces): fit each import's origin and the importer's 180-degree turn from the per-mesh centres, apply manifest materials, and place the 168 instances. This retires 94 part-built stand-ins (hollow tree, tree line, hills, mountains, sister trees, ...). Also adds the oculus light-shaft Beam, the 30 H9 interior PointLights and the door lanterns.
  - PrepareLibrary now handles single-file prop imports the same way.
  - Treeline cards: the importer drops PNG alpha, so `card_*.png` were uploaded (MCP upload_image) and applied as a SurfaceAppearance with AlphaMode Transparency.
  - Mesh flags and the H5 respawn stone hide their part-built stand-ins.
  - Interim overrides used before pass 6 landed (H8 exit ring/bank2/arch, H7 gap posts, H4 bar scale, H9 bar removal) are now empty (`tools/props_overrides.json`).
- Moving decor rides the phase-locked physics movers (welded PropVisual: H4 bar, H6 wheel, H7 log, H8 door, H9 gate + pendulum). H6 rail notch from stage a kept. Lighting unchanged (Future, Atmosphere, Bloom, warm 17.1 sun); Beams on falls/stream/flume + oculus.
- **Perf (phone-ish)**:
  - 3.3k parts (2.1k MeshParts, 467 unique meshes);
  - ~0.95M tris total: course decor 245k (was 809k), world pieces 701k, mostly far hills/tree line/mountains on Performance render fidelity with no shadows;
  - 157 lights, 0 with shadows;
  - 35 Beams, 8 emitters;
  - 0 colliding/touching decor parts.
- **Sweeps**: final 180 random shots: 0 escapes, 0 stuck, 0 auto-resets, 0 timeouts, 0 nudges, 0 console errors/warnings (`playtests/lantern-v1/stage-c/README.md`).
- **Shots**: `playtests/lantern-v1/overview*.png`, `hole01..09.png` and `stage-c/shots/` (incl. h9_pendulum, h2_chutes, h8_alcove).
- Saved twice with File > Save to Roblox ("Saved new changes in "VR Mini Golf" to Roblox."), not published. Studio left in Edit mode, one window.
- **For the team**: the H8 door end now sweeps balls aside (not pinned) at the pockets. The H9 dip rests balls in the crease. Light count (157) is the first thing to cut if phones struggle.

## Stage d (2026-10-10, 17:15 PT): movement, Explore mode, round-1 UI fixes, sweep, PUBLISHED v79
- **Movement**:
  - Fade to black + next tee: existing HUD/GolfServer flow, re-verified. Desktop tint goes black ~3.4 s after the
    hole-out and the hole switches while black.
  - `progress` (simulated VR): all 9 holes, VR rig 1.5 studs from the ball on each tee, final scorecard.
  - VR trigger = warp to ball (VRControls). Desktop/phone: the camera follows the ball, and the avatar stands
    beside it.
- **Explore mode** (Chase 13:37):
  - New `GolfClient/Explore.luau`, HUD Explore bar/teleport menu, `GolfServer` `SetExplore` remote (parks the ball
    anchored, resume spot; placeBall while exploring just moves the parked spot), `ReplicatedStorage.Golf.ExploreData`
    (views, walkway points, bounds from WorldLayout), `workspace.ExploreBounds` walls (collision group
    `ExploreBounds`, players only).
  - Studio-only `GolfExploreDebug` BindableFunction drives it for tests.
  - `smoke` now runs an Explore round trip. New `tools/ui_shots.py` takes the HUD/Explore screenshots.
- **Round-1 UI fixes**:
  - player list hidden;
  - own avatar LocalTransparencyModifier = 1 every frame in golf;
  - info panel below the chat rect;
  - wrapped help;
  - compact scrolling scorecard.
- **Rail grass**: `WorldBuilder.ClearGrassNearRails` (called from CarveHoles) swaps Grass for LeafyGrass within
  1 stud + 2 of every rail; applied to all 9 holes.
- **Sweep**: 180 shots, 0 escapes, 0 stuck, 0 auto-resets, 0 timeouts, 0 nudges, 0 console errors
  (`playtests/lantern-v1/stage-d/sweep-d`, `sweep-d2`).
- **Smoke**: desktop + iphone_17_pro, 0 errors/warnings.
- **Shots**: `stage-d/shots/` and `stage-d/ui/`. `shots` now uses MCP screen_capture (no screen-recording
  permission).
- **PUBLISHED v79**, 5:11 PM PT (Codex: Save, then Publish): "Published new changes in "VR Mini Golf" to Roblox."
  Audience unchanged.
  - Lighting.Technology isn't shown in the Properties panel (two Codex attempts), so it's unverified.
  - Studio left in Edit mode, one window, free.
- **Report**: `playtests/lantern-v1/REPORT.md`.
- **Playtest Bot handoff**: `~/playtest/READY-v79.md` (no Playtest Bot session was reachable to message).

## Stage e (2026-10-10, 19:00 PT): Playtest round 2 fixes. NOT saved/published (live stays v79)
- **H8 camera clipping**: new `ReplicatedStorage.Golf.CameraOcclusion`.
  - GolfServer puts 1,893 visible decor parts in a camera-only collision group (`GolfDecor`, CanQuery on, still never collides).
  - The putting, harness follow and Explore cameras spherecast from the ball/character and pull in or swing up in front of hits.
  - Camera-inside-geometry over ~5,500 spots on all 9 holes: 343 → 15. The H8 frames are clean.
- **Explore spots**: teleports score the base point and spots 4–6 studs out (camera room, view, tall grass) and use a fixed 20° camera.
  - Lantern Mere and the H9 tee moved ~4 studs.
  - Grand Falls is fixed by the camera pitch.
  - All 14 destinations are clear. H9 gets 7.4 studs of camera room inside the tree.
- **Phone Explore message**: now a short top-centre toast that fades after 3 s.
- **Smoke**: now asserts 1 stroke → Explore → back gives strokes 1 and the ball within 0.1 stud. Desktop and phone PASS.
- **Contact log**: full part paths. 0 "?" in the sweep, down from 30–50%.
- **Sweep**: 90 shots, 0 escapes, 0 stuck, 0 resets, 0 timeouts, 0 errors.
- **UI shots**: desktop and phone in `playtests/lantern-v1/stage-e/ui`.
- **Asset fixes**: none landed, skipped.
- **BLOCKED**: Save to Roblox and Publish. Codex is over its usage limit until 10-17, and this session has no Accessibility or event-post permission (Cmd+S didn't reach Studio). Studio is in Edit mode with the changes unsaved; `src/` has everything.
  Next step: File > Save to Roblox, then Publish. Report: `logs/stages/e-report.md`.

## Stage g (2026-10-10, 19:50 PT): VR club flip + H7/H8/H9 Round 7 + art. NOT saved/published (live stays v79)
- **Club flip:** `Config.VRClubFlip = true`. The shaft is the exact negation of the v12–v79 vector (+Y raked toward -Z), out of the handle top, offset 0.25. The face is unchanged and the left hand is mirrored. Debug proxy shows the shaft leaving the top; before/after shots for both hands are in `playtests/club-flip/`.
- **H7/H8/H9 re-imported** from holes.json Round 7 with one regenerate step. Shared `MoverMath` adds slide `dwell` pauses.
- **Movers collide:** the moving parts are CanCollide Blockers on motorised constraints, not just visuals. Block rate on the intended lines, 20 phases each: H7 55%, H8 50%, H9 5% blocked / 25% touched. The H9 bob skims the top of the ball; flagged to Game Art Bot.
- **Art:** 35 manifest PointLights on H7/H8 (rail lanterns + glows) and 3 amber hanging lanterns over the H9 green. The v2 card textures are byte-identical to v1 and already live; 139226561598751 isn't used.
- **Tests:** sweep H7–H9 60 shots with 0 escapes, stuck, resets or errors; smoke PASS.
- **BLOCKED:** Save/Publish (Codex usage limit until 10-17, no input permission). Studio is in Edit with stage e+g unsaved. Report: `logs/stages/e-report.md` (stage g section).

## Stage h (2026-10-10, 20:35 PT): pass 8 refit, 38 lights, rail16 notch, H9 collider check, game page screenshots. NOT saved/published (live stays v79)
- **Pass 8 FBX not imported.** No importer route: Codex is at its limit, AssetImportService/CreateAssetAsync are unavailable, and there's no Open Cloud key. The stage-g meshes stay, stretched to the Round-7 blockers, with the colliders unchanged. The import list is in e-report.
- **Lights:** all 38 manifest lights[] are placed. The 3 H9 hanging lanterns (now `lantern_large` x0.85, bottom y 7.2, Brightness 3 / Range 16 via `light_id`) carry their light on the glow core. The H8 firefly-swarm glows x2 are at 3.5/14. Rail-lantern stand-ins now stand on the ground (stage g floated them ~5.6 studs on H8). The ring glow disc is r 0.45.
- `heart_lantern_cluster` is gone, and only the south door pocket remains. The **rail16 notch** is at x 4.2..5.3, cut square on the sloped rail kit.
- **Block rate** (20 intended-line shots each): H7 50%, H8 50%, H9 10% (25% touched).
  - The H9 collider is verified: 1.6x1.8x1.6, yaw 30, ±30°/5 s, hinge world (-81.461, 48.996, -6.675).
  - The ball arrives at x 21.18 ~2.6 s after the hit at ~3 studs/s. Hinge and shot line are written up for Game Art Bot.
- **Sweep** H7–H9, 20 random shots each: 0 escapes, 0 stuck, 0 resets, 0 errors. Smoke PASS.
- **Screenshots:** 8 x 1920x1080 in `marketing/screens/`, from 4-tile reprojected MCP captures (`tools/marketing/tiled.py`), plus 2 older stills.
- **BLOCKED:** Save/Publish. Studio is in Edit with stages e+g+h unsaved. Report: `logs/stages/e-report.md` (stage h section).

## Stage i (2026-10-10, ~20:30 PT): follow-ups 7-10, all blocked. No Studio changes, NOT saved/published (live stays v79)
- **Item 7 (H9 collider):** already verified and handed off in stage h.
- **Items 8-10 (game page, mesh imports, dropping the stretch overrides):** BLOCKED. There's no Open Cloud key and no Claude computer-use/browser tool in this session, and Codex is at its limit until 10-17. The game page also needs a publish first.
- The upload list, a draft description, the missing-mesh list and the exact post-import steps are in `logs/stages/e-report.md` (stage i section).
- Studio: Edit mode, one window, stages e+g+h still unsaved (last save 17:14 PT).

## Stage m (2026-10-11, 10:50 PT): camera pass-through/see-through, slope felt, crowd audio, front end + personal best, H9 Round 8, lights, H8 names. **Published v116**
- **Camera:** golf cameras pass through geometry (only Terrain pulls in) and fade what's between camera and ball (LocalTransparencyModifier 0.7). Camprobe: 0/5,796 bad poses on all 9 holes.
- **Slope felt:** chevron felt (slope_felt_A mask, 4 rotations) on the 18 felt pieces tilted > 2°, tips downhill; built by CourseBuilder.
- **Audio:** cup plunk + score-based crowd (HIO/eagle cheer+applause, birdie cheer, par applause, bogey claps, worse "aww"). Free, public Creator Store audio; verified to load/play, not listened to.
- **Front end:** title/course picker (2 "Coming soon")/settings/how to play/results with "New best!", on desktop, phone and VR (world-space panel). Personal best in DataStore VRMiniGolf_PB_v1 (Studio stays in memory: API access off).
- **H9 Round 8:** hinge x 21.2, ±13°/4 s, invisible foot collider. Block rate 25% (5/20), touched 45%.
- **Lights:** every lantern/glow prop lit (0 unlit, build check). **H8 names:** tee_sign_hNN models, H8/H9 cream rail-trim skin + ManifestProp tags.
- **Tests:** 90-shot sweep clean, progress PASS, desktop + phone smoke PASS. Report: `logs/stages/e-report.md` (Stage m).

## Stage n (2026-10-11, 13:35 PT): round 4 fixes, slope pattern C, H9 Round 9. **Published v131**
- **Slopes:** pattern C arrowheads (3D Model Bot colour map baked into 3 felt tones × 4 rotations, 8 studs/tile) on all 17 slopes. Tips point downhill, checked from top-down shots in `playtests/stage-n/slopes/`.
- **H9 Round 9:** the foot was 0.9 at 37.5% (9/24), so I switched to 1.0×0.4×1.6 per spec, which gave 29% (7/24). 48-shot runs give about 30% for both widths, with 0 traps. Shipped at 1.0; Game Art Bot needs to retune.
- **Fixes:**
  - VR menu has one anchor per session (0.000 jump).
  - `menu_shots --vr` levels the head.
  - VR text caps now scale with the canvas.
  - The camera fades big decor just off the sight line (H6 sign) and hides near-lens glows and lights (H9 pendulum).
  - The hollow tree no longer fades as a whole (0 shell parts per pose).
  - H8 rail lanterns are dimmed.
  - How-to page uses tabs, at 18.5 pt on phone.
- **Personal best:** Studio API access is on. A DataStore save/load round-trip on the live store PASSES.
- **Tests:** camprobe 0/5,796; 90-shot sweep clean; desktop and phone smoke PASS. Report: `logs/stages/e-report.md` (Stage n).

## Stage o (2026-10-11, 15:25 PT): H9 pendulum plinth mesh import. **Published v135**
- **Imported** `h9_lantern_pendulum` (5 parts, Iron now includes the 0.9×0.4×1.6 dark plinth) and `h9_pendulum_root_beam` (pivot at hinge x 21.2, beam still at x 22) via Codex's 3D Importer.
- **Pipeline:** `tools/fbx_bounds.py` + the `fbx_refresh` entry in `props_overrides.json` replace the stale manifest data. Rebuilt with the usual regenerate step.
- **Pendulum:** the 5 MeshParts are welded to the mover root, all non-colliding. The foot (1.0×0.4×1.6) is still the only foot collider. The swing matches the spec formula within 0.33°.
- **Plinth:** flush with the foot at 0°/±13°. 0.05-stud slivers on each side, because the foot is 1.0 wide and the plinth 0.9. Flagged to Game Art Bot.
- **Tests:** block rate 7/24 (29.2%), unchanged from stage n. H9 sweep (20 shots) clean. Desktop and phone smoke PASS. Report: `logs/stages/e-report.md` (Stage o).

## Stage p (2026-10-11, 16:10 PT): Chase's VR feedback + H9 Round 10. **Published v145**
- **VR menus:** a laser pointer from either controller (`GolfClient.VRPointer`): amber beam, dot, hover glow, trigger = click. It works on the title/courses/settings/how-to/results pages, the VR scorecard (new Close button) and the wrist buttons. The thumbstick-click hint is gone, and the beam is hidden in play. Pointer walk-through PASS 14/14 (`menu_shots.py --vr --pointer`).
- **Wrist card:** Walkabout-style card on the off-hand wrist (Game Art Bot's parchment art): hole + name, par, stroke, total vs par, best vs par, plus MENU and SCORES buttons. It fades in when the back of the wrist faces the eyes (35°). VR only; there was no bracer FBX, so it's a plain panel. PASS (`--wrist`).
- **See-through:** the occluder fade now also runs in VR, from the head to the ball. The new `GolfClient.XRay` outlines the ball (+ VR putter head) through anything that blocks it. X-ray check PASS 14/14 (H3 tunnel, H6 wheel, H9 tunnel, hollow tree, rail, open control; VR + flat).
- **H9 Round 10:** ±11° swing. 48-shot block rate **19/48 (39.6%)**, 0 traps.
- **Tests:** camprobe 0/5,796; 90-shot sweep clean (0 escapes/stuck/resets/timeouts, 0 errors); smoke desktop + phone + VR sim PASS. Report: `logs/stages/e-report.md` (Stage p).

## Stage q (2026-10-11, 16:55 PT): VR art polish. **Published v153**
- **Front end v2:** title_bg_v2 + card_lanterngrove_v2. The L1 logo is 900/1920 wide, 40/1080 from the top (desktop + VR panel).
- **Meshes (Codex 3D Importer):**
  - `h9_lantern_pendulum.fbx` (1.0×0.4×1.6 plinth): re-imported and rebuilt. Felt is at y 1.0 with 0.021 clearance at the lowest point. The pendulum lights were already at x 21.2.
  - `vr_wrist_bracer.fbx` → `ReplicatedStorage.Golf.WristBracer`. Its 180° import turn is undone and the colours come from the FBX.
- **Wrist:** the bracer sits on the off-hand wrist with the card on its 16:10 WristFace and a MENU/SCORES strip. Both are hidden unless you look at the wrist:
  - Show: the back of the wrist faces the eyes within 32° and the wrist is within 25° of gaze, held 0.25 s.
  - Hide: 0.4 s after either goes out (45° / 35°).
  - Never shows mid-swing (> 3 studs/s, +0.5 s) or in a putting stance. All thresholds are Config values.
  - `tools/wrist_sim.py`: 0 false shows across glances, swings, stance and 25 s of head motion (3 seeds); 3/3 deliberate looks show in ~270 ms.
- **Tests:** H9 48 shots 18/48 blocked, 0 traps; H9 20-shot sweep clean; VR pointer walk 14/14; VR progress Pass; smoke desktop + phone PASS. Report: `logs/stages/e-report.md` (Stage q).

## Stage r — 2026-10-11 — published v167
- Round5 wrist failures traced to harness swing-gate timing, wrong pointer hand after switch, and synthetic Best setup. Corrected regression passes23 real pointer actions: three MENU→Resume→SCORES cycles, both switched-hand buttons, Best-2.
- All9 VR smoke passes; simulated swing6.809/6.80stud/s expected. H2 near-cup fixture and stale results-menu/test hit telemetry corrected; physics untouched.
- VR XRay updates every frame with current spokes.600-frame independent check:0misses/0false shows, ball+club, logical and actual Highlight state.
- Data-driven felt:>=25° plain at0.85 tint; under25° patternC. Regenerated9holes; five45° banks clean, twelve gentler slopes retain chevrons.
- Reimported5-part bracer. Supplied FBX was still old.32x.20 face; fitted to.37x.28328125 exact1024x784 Top canvas; corrected Top axis mapping and retained.256 rim clearance. Both-hand screenshots upright/full, gates unchanged. Upstream FBX remains stale.
- Wrist sim seed7:3/3 looks,0 false shows. Desktop+iPhone smoke PASS. H9 random20 seed118:0escapes/stuck/resets/timeouts/nudges, max stationary moving interval.383s. Every final console clean.
- Mirrored scripts. File>Save confirmed18:50:01; File>Publish confirmed18:50:25. Version History v167 Published,6:50PM,MetavrseBuilder. Friends and Playtesters unchanged; no Robux. Studio left Edit/test flags off.
- Report: logs/stages/e-report.md; evidence: playtests/stage-r/.

## Stage s (2026-10-11) — published v190
Round 6 fixes (bank tint from adjacent felt, TOTAL excludes current hole, H1 pre-stroke Resume), H9 variance = noise (same-build 41.7/37.5/37.5%), wrist card text grid (64/120/64 px FredokaOne #3B2412 + 2px #FFF4DC stroke), see-through only at rest while aiming, H9 lighting/dim props/zone exposure+bloom with exact restore, wrist trigger loosened (70°/55°, either face) + off-hand X/A toggle + WristPoseLog DataStore, VR club setup in Settings (thumbstick ground target, trigger save, reset, 6-image explainer, DataStore). Sweeps H1–H9 0 stuck/escapes, all smokes/sims PASS, 0 console errors. Codex did most of it; Claude Code finished the sweeps, reruns, publish. Details: e-report.md "Stage s report".

# Stage t report (2026-10-11): Lobby fixes SRV-138 + Course modes SRV-139

**Live version: v202.** File > Save to Roblox completed at 23:31:19 PT; File > Publish to Roblox completed at 23:31:35 PT. Opened Window > Version History: newest entry **v202, Published**, dated October 11, 11:14 PM (the underlying autosave timestamp). This is newer than v190. Single Studio window left in Edit mode, test flags off. Audience unchanged; no Robux spent. Claude implemented the stage; Codex resumed verification, export, UI publication and reporting without coding.

| Item | Result |
|---|---|
| 0 Backup | Untouched v190 saved before edits as `playtest-v190.rbxl`, 3,285,911 bytes. Already covered by `*.rbxl` ignore; not committed. No second backup required. |
| A1 Windmill | Blades fitted to hub (150,7.4,67.3), with +0.15 Z clearance offset (final pivot 150,7.4,67.45). Existing full-rotation probe passes at 0.15 studs against 19 static parts; prior probes bracketed clearance at 0.2–0.3 studs. |
| A2 Canopy | Base lowered to Y -0.1. |
| A3 Green | Native full 1.2-stud height retained; no 0.4 scale. |
| A4 Leaderboard | Yaw +90; panels face east. |
| A5 Course board | Faces spawn at (74,0,89), yaw 67.07. The suggested (86,0,85) obscured the Lantern Grove arch; the nearby adjusted position exposes all three arch openings (sightline check 1.0 each). |
| A6 String lights | New 24-stud FBX imported; spans X153–177, endpoints Y7.0 against posts Y7.05. Decor noncolliding/nonqueryable/nontouchable. |
| A Evidence/data | Five images in `playtests/stage-t/lobby/`, including three spawn views, visually reviewed. 29 imported asset types, 242 instances, 32 walking colliders, one spinner. Rebuild data in LobbyLayout/LobbyBuilder, generated by `tools/lobby_to_lua.py` with `lobby_overrides.json`. |
| B Modes | Peaceful balls pass through; PVP balls collide with other PVP balls. Mixed pairs pass through. Independent next-hole-only progression; late joiner starts at H1 and can stroke immediately. Mode selector in course card, server validation and ball collision groups. No legacy group/timer/skip/spectate/vote paths found in the prior implementation. Final simulated-player tests: 13/13 PASS (`playtests/stage-t/modes.json`, extracted unchanged from Claude's final test result). |
| C Pose events | Added open/close/button/nearFace events; client/server throttling 1.5s, server cap 20 events/min, bounded 120 samples. Existing periodic samples retained. Persistence is real-headset-only; not claimed tested on hardware. |
| D XRay | Ball outline uses the same rest + aiming/swinging gate as fading. H6 test PASS: 602 rest frames, zero misses/false shows; rolling 165 frames (149 occluded), zero outline frames; consoles clean. |

**Verification:**

- VR all-nine progression + simulated swing, ghosting and ledge checks: PASS, swing 6.80/6.80 studs/s. Desktop and iPhone smoke: PASS, stroke→Explore→back preserves one stroke; drift 0.010 / 0.000 studs. Existing VR/desktop evidence was completed after the final source pushes and retained.
- `stage_s_checks`: PASS (H1 zero-stroke Resume, TOTAL, off-hand toggle/dismiss/rearm, palm-up, wrist text and fade gate); club setup simulation PASS; H9 lighting PASS 8/8 with exact restoration. Zero server/client warnings and errors in the recorded final tests.
- Wrist simulation: **behavior passes, existing aggregate counter falsely fails.** Raw events show watch=3 shows/3 hides, plus 3 new `pose` records. The old counter treats every non-show event as a hide and reports 6. Glance/swings/stance have zero false shows. Preserved original output and added `wrist-sim/event-audit.json`. A narrow counter correction was attempted through Cursor, but it could not start because the login keychain was locked. No Codex source edit was made. Counter maintenance remains open; the card behavior is independently covered by the passing Stage s regression.
- H6 quick random sweep, seed122: 20 attempts, 19 accepted hits; aggregate reports zero escapes, stuck, resets, timeouts, hazards and nudges; maximum stationary interval while moving 0.25s. One attempt was refused because the ball was moving, and one random placement transitioned to H7. These are fixture limitations, not hidden clean-shot claims. No par, intended-line or hole-in-one searches ran. No hole geometry was changed in Stage t.
- Exported every Studio script with the existing runner; `git diff -- src` is empty against the Stage t checkpoint. Gravity remains 32.7 and test flags are false. Physics and v12 mount unchanged.

**Remaining scope/limitations:** the newly built boardwalk is at the existing Stage t origin (-110,0,6000). It is not wired as the gameplay spawn; portal/course-board integration remains the separate lobby integration work identified in LobbyBuilder. Native headset interaction and persisted pose events still need a hardware check. The wrist aggregate counter and random-placement fixture limitations above remain documented. No game console error was observed.

Evidence: `playtests/stage-t/`; resume notes: `logs/stages/t-notes.md`. Published version evidence: `playtests/stage-t/published-version.json`.

**Repository delivery blocker:** local `main` contains the Stage t release commit, but `git push origin main` failed with macOS keychain -25308 / unavailable GitHub credentials. `gh` authentication also fails; no SSH key is configured. Restore authentication and retry push. Roblox v202 is verified Published; Studio is saved in Edit.
