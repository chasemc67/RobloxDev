# Stage e report: Playtest round 2 fixes (v79 -> next publish)

2026-10-10, 18:05–19:00 PT.

**Version: NOT PUBLISHED. Live is still v79; Studio has the changes but they are NOT saved.**
- Save and publish both need a click in Studio's File menu.
- The only route for that, Codex computer use, is over its usage limit until 2026-10-17 00:03.
- This session can't send input to Studio. Both routes fail:
  - `osascript` UI scripting: "not allowed assistive access";
  - Quartz key events: `CGPreflightPostEventAccess` = False, so Cmd+S never reached Studio (no "Saved new changes" in the Studio log).

To finish, do one of:
- In Studio: **File > Save to Roblox**, then **File > Publish to Roblox**.
- Grant Accessibility to the process that runs the stage scripts, then rerun the save/publish step.
- Run `tools/codex_ui.sh` after Oct 17.

If Studio closes before that, nothing is lost. All changes are in `src/` (this commit), and `python3 tools/run_playtests.py push <files>` restores them:
- `src/ReplicatedStorage/Golf/CameraOcclusion.luau`
- `GolfServer.server.luau`
- `TouchControls.luau`
- `GolfTest.luau`
- `Explore.luau`

Studio is in Edit mode, one window, with GolfTestMode false.

## What changed
1. **H8 camera clipping (camera occlusion).**
   - **Cause.** All 1,767 decor parts are built with CanQuery off, so the putting camera's raycast never saw the H8 root-arch beams or foliage. The test "follow" camera had no occlusion check at all.
   - **New module `ReplicatedStorage.Golf.CameraOcclusion`.** At startup, GolfServer puts the visible, non-colliding decor in collision group `GolfDecor` with CanQuery on: 1,893 parts.
     - This skips parts under 1 stud, see-through parts and the far mountains, hills and clouds.
     - `GolfDecor` only "collides" with `GolfCamera`, the group the camera casts use. Ball, club, player, harness and server raycasts all still ignore decor, and decor still never collides.
   - **Camera behaviour.** A 0.25-stud spherecast runs from the ball to the camera, ignoring felt, balls, the character and see-through parts. The camera is pulled in front of the first hit. When that would leave it closer than 1.5 studs (ball against a rail, under a beam), the camera swings up toward top-down instead.
   - **Where it's used:** the desktop/phone putting camera (TouchControls), the harness follow camera (GolfTest) and the Explore follow camera (Roblox's own camera can't see the decor either).
   - **Check across all 9 holes.** Felt points every 3 studs × 8 view directions, ~5,500 spots, counting cameras that end up inside geometry:
     - before: 343;
     - after: 15. These are 13 on H6, test follow camera only (ball pressed against a board), and 2 on H8 putting camera.
     - Per hole after: H1–H5, H7 and H9 have 0.
   - **H8 frames.** 30 frames, follow and putting cameras, 6 putts through the ring and arch. No black or clipped frames.
2. **Explore spawn points.**
   - Teleports now pick the stand spot by scoring the base point and rings 4 and 6 studs out. A spot scores well when:
     - the camera has room behind (12.5 studs, ±15°);
     - the view ahead is clear;
     - the character isn't inside a mesh;
     - it isn't in tall Terrain grass if that can be avoided.
   - After a teleport the camera is set to a fixed 20° down along the facing, re-applied for 0.4 s. It's never pitched up at a high subject; that pitch is what put the phone camera in the Grand Falls grass.
   - Results, phone emulation:
     - **Lantern Mere** moved 4 studs (176,118 → 178.8,120.8). No trunk in view.
     - **H9 tee** moved 4 studs away from the trunk wall. The course and arches are visible, but the camera only gets 7.4 studs of room inside the tree (was 3.5), so it frames tighter than elsewhere.
     - **Grand Falls** keeps its spot: it's the only sand there and the view is now clear. The fix was the camera pitch.
     - All other 11 destinations: full 12.5-stud camera, nothing in the way.
3. **Explore message on phone.** "Explore! No ball, no score" is now the small top-centre toast. It fades after 3 s and clears the info panel and the Sprint/Fly buttons (`stage-e/ui/phone_explore_toast.png`).
4. **Smoke test: stroke → Explore → back.** `smoke` now takes one real putt (`BallController.hit` through the Studio-only `GolfExploreDebug` hook), runs the Explore round trip and asserts strokes == 1 and the ball within 0.1 stud.
   - Desktop: PASS, ball moved 0.007.
   - iPhone 17 Pro: PASS, ball moved 0.000.
   - 0 errors or warnings on either.
5. **Contact log part names.** Contacts are now logged with `GetFullName()` (+ `:WallId` / `:MoverId`).
   - The cast uses the ball's collision group, so movers are found, with a nearest-part fallback.
   - The putt itself is no longer logged as a contact; that was most of the "?".
   - Velocity jumps with no part nearby are labelled `(no part: landing or slope change)`.
   - Sweep: 0 of 185 contacts are "?" (Playtest Bot saw 30–50%).

**Asset fixes:** nothing has landed in `assets/` since v79: no file newer than 16:52, and v79 already used those. That covers the H9 canopy lights, the H7/H8 rail lanterns and the H1 treeline card re-upload, so I skipped them. The H1 `treeline_card_gold` texture (139226561598751) is still on 3D Model Bot.

## Tests
- **Sweep:** 90 random shots, 10 per hole, seed 79 (`playtests/lantern-v1/stage-e/sweep-e`, `sweep-e2`):
  - 0 escapes, 0 stuck, 0 auto-resets, 0 timeouts, 0 nudges, 0 console errors or warnings;
  - 6 hazard drops (expected): H5 4, H6 1, H7 1;
  - 3 holed.
- **Smoke:** desktop and phone PASS (`stage-e/smoke/`).
- **UI shots:** desktop and iPhone 17 Pro, 11 each (`stage-e/ui/`): golf HUD, scorecard, Explore toast, menu, fly, Grand Falls, Lantern Mere, H5, H9, Hollow Tree, back to golf. Nothing covers the HUD.

---

# Stage g report: VR club flip + H7/H8/H9 Round 7 re-import (2026-10-10, 18:54–19:50 PT)

**Version: NOT PUBLISHED, NOT SAVED. Live is still v79.** Codex is over its usage limit until 2026-10-17 00:03 (`logs/codex-publish-g.log`), and this session still can't send input to Studio (`CGPreflightPostEventAccess` = 0). Studio is in Edit mode, one window, holding stage e + g unsaved; `src/` has everything. To finish: in Studio, **File > Save to Roblox**, then **File > Publish to Roblox**. The next version will be the first one with stage e and stage g.

## 1. VR club direction flip (Chase, v79)
- `Config.VRClubFlip = true` (new, default). `VRControls.defaultClubMount` adds 180° about hand X (base pitch `90 - VRClubGripPitch` instead of `-90 - VRClubGripPitch`) and negates yaw. The shaft is now **+Y raked 35° toward -Z, the exact negation** of the v12–v79 vector. It starts `VRClubButtOffset` (0.25) along the shaft, i.e. on the top side of the handle. `VRClubFlip = false` restores the old mount.
- Putter face: RightVector (face normal) is hand +X before and after, so the face is unchanged (`faceDotRight` 1 → 1). Only the unused toe vector flips. Left-hand mirroring still applies to yaw/roll.
- Debug proxy (`GolfTest` club overlay): an orange cap marks the end the shaft leaves (top when flipped) plus a grey link from the handle top to the shaft start. Grip-mount poses aim the shaft at the ball, so the flipped shots show the controller held top-down with the shaft leaving its top. `clubpose` takes `hand` ("left"/"right") and `flip`; `clubviz` now uses MCP screen_capture and shoots flip off/on for both hands.
- Screenshots: `playtests/club-flip/{before,after}_{right,left}_{side,front,side_close}.png` + `clubpose.json`:

| | before R | after R | before L | after L |
|---|---|---|---|---|
| shaft vs handle-bottom axis | 0° | 180° | 0° | 180° |
| shaft vs intended end (bottom / top) | 0° | 0° | 0° | 0° |
| shaft start gap | 0 | 0 | 0 | 0 |
| face · golfer right | 1 | 1 | 1 | 1 |
| head bottom above plane | 0.011 | 0.011 | 0.011 | 0.011 |

0 console errors/warnings. Not verified in a headset; that's Chase's next VR check.

## 2. H7/H8/H9 Round 7 re-import (one regenerate step: `holes_to_lua.py --push --build`)
- **Dwell:** new `ReplicatedStorage.Golf.MoverMath` (shared by GolfServer.Movers, CourseBuilder, GolfTest) implements the `dwell` slide profile: end stops pause once per visit, interior stops pause on both passes, and t=0 is the start of the pause at `phase`. Period includes the pauses (log 9.357 s, door 6.667 s, as in holes.json `period_s`). When CourseBuilder clamps a range for rail clearance, dwell stops at the ends move with it (H7 log +6 → +5.98).
- H7 log 6 long, pointed ends (3 blockers), ±6 at 3.5 studs/s, dwell 1.0 s W / 1.5 s E. H8 door 3.6, 0..4 at 3 studs/s, dwell 1.8 s shut / 2.2 s open; ring radius 0.45. H9 pendulum bob 1.6×1.8×1.6 yaw 30, ±30°, 5 s, hinge y 8.996.
- **Do the colliders move?** Yes. Each mover is an unanchored assembly: invisible `Blocker` parts (CanCollide true, group GolfMover, which collides with GolfBall) welded to a MoverRoot and driven by a motorised Prismatic/Hinge constraint. The server phase-locks it to the spec every physics step. The visual meshes are welded on with CanCollide false. Nothing was only a visual.
- **Block rate**: `run blockrate` fires Game Art Bot's intended lines (playtest-log Round 7) at 20 evenly spaced phases. blocked = touched the Blocker and never crossed its line (`playtests/lantern-v1/stage-g/blockrate`):

| Hole | mover | blocked | touched | sim (touched, 24 phases) |
|---|---|---|---|---|
| H7 | log | **11/20 = 55%** | 55% | 45.8% |
| H8 | root door | **10/20 = 50%** | 50% | 50% |
| H9 | lantern pendulum | **1/20 = 5%** | 25% | 37.5% (5 blocked + 4 deflected) |

  0 traps, 0 timeouts, 0 errors. H7/H8 block in-engine roughly as the sim says (H7 a bit high). **H9 is below target.** The bob bottom hangs 0.096 above the felt and the ball is 0.16 tall, so the face only meets the top 0.064 of the ball. In-engine most touches glance off the top and the ball rolls under. For Game Art Bot: lower the bob ~0.05 (collision box only) or make it taller at the bottom if H9 should really block.
- Mover meshes (3D Model Bot pass 8, still the Round 6 sizes) are stretched to the new blockers via `tools/props_overrides.json`: log ×1.179 X, door ×1.106 Z, pendulum yaw 30 + ×1.613 Z. The log mesh keeps flat ends; the pointed end blockers are 0.4 longer visually. 3D Model Bot should re-export these.

## 3. Art
- **Cards:** `card_gold_v2.png` / `card_red_v2.png` are byte-identical to v1. Re-uploading them returned the asset ids already in use (gold 119241826373121, red 79137228052052), so the v2 art is already what's in the game. 139226561598751 fails to load (AssetFetchStatus.Failure) and nothing references it.
- **PointLights from `models/manifest.json` lights[]** (new `pointLights` in PropPlacements, built into `Decor/Props/Lights`):
  - H7: 8 amber rail lanterns (range 10, brightness 1.2) on the lower tiers.
  - H8: 15 rail lanterns, plus 12 mushroom/firefly glows (brightness 1.4–1.6, range 8).
  - The rail_lantern_stake/crook meshes aren't imported (that needs the 3D Importer via Codex), so each rail light gets a stand-in: an oak stake with a `lantern_small` on top.
- **H9:** 3 amber hanging lanterns at the holes.json `amber_lantern_1..3` spots (`lantern_medium` scaled to 1.2×1.8×1.2, bottom y 7.2, chain to y 16, PointLight 255/169/87, range 16, brightness 2.5, no collision). They replace the heart lantern cluster + string (`playtests/lantern-v1/stage-g/shots/h9_amber_lanterns.jpg`). The manifest's own H9 hanging-lantern lights (corridor/chamber spots) are superseded by these.
- The regenerate also picked up 3D Model Bot's newer manifest dressing (18:36). Instances of props not imported yet are skipped (H8: 21 of 37).

## Tests
- Sweep H7–H9, 20 random shots each (seed 80, `stage-g/sweep-g`): 0 escapes, 0 stuck, 0 auto-resets, 0 nudges, 0 console errors.
- Smoke (desktop): PASS, 0 errors/warnings, stroke → Explore → back ok.
- clubviz: 0 errors.

---

# Stage h report: pass 8 refit, lights, rail16 notch, H9 collider check, game page screenshots (2026-10-10, 19:42–20:35 PT)

**Version: NOT PUBLISHED, NOT SAVED. Live is still v79.** Save/Publish is still blocked: Codex is over its usage limit until 2026-10-17 00:03, and this session has no input permission (`CGPreflightPostEventAccess` False). Studio is in Edit mode, one window, holding stage e + g + h unsaved; `src/` has everything. To finish: **File > Save to Roblox**, then **File > Publish to Roblox**.

## 1. Pass 8 FBX: NOT imported (no route); stage-g meshes kept and refit
- The 3D Importer needs Codex computer use (limit). Studio-side alternatives all failed:
  - `AssetImportService` isn't reachable from MCP Luau (nil).
  - `AssetService:CreateAssetAsync` returns "not available yet".
  - An EditableMesh MeshPart wouldn't survive Save to Roblox.
  - No Open Cloud key is configured (skill: ask Chase first).
- So `h7_floating_log`, `h8_root_door` and `h9_lantern_pendulum` stay as the stage-g library meshes, stretched to the Round-7 blockers via `tools/props_overrides.json`. The colliders are unchanged; the H9 collider is verified below.
- `h9_pendulum_root_beam` stays at the hinge (y 8.996). `rail_lantern_*` and `lantern_large_hanging` are still not in the library.
- **To do when Codex is back:** import `h7_floating_log`, `h8_root_door`, `h8_door_pocket`, `h9_lantern_pendulum`, `h9_pendulum_root_beam`, `firefly_ring_entry`, `lantern_large_hanging`, `rail_lantern_stake` and `rail_lantern_crook`. Then drop the three stretch overrides and run `holes_to_lua.py --push --build`. PropsBuilder already uses the real meshes when they're in `ServerStorage.LanternGroveProps`.

## 2. Lights (manifest lights[], data-driven)
- **All 38 manifest lights are placed.**
  - 23 rail lanterns (amber 255/169/87, Range 10, Brightness 1.2).
  - 12 H8 glows: 5 firefly_glow_low #D8FF6A at 8/1.6, and 7 shroom_glow #7FE3D0 at 8/1.4.
  - 3 H9 hanging lanterns at Range 16, Brightness 3, on the lantern's own Neon glow core at hole-local y 8.06. `props_overrides.json` adds now carry `light_id`, and `props_to_lua.py` fills in range/brightness/colour from manifest lights[].
- **H8 glow x2:** the two `H8_firefly_swarm_*_firefly_glow` spot lights (manifest `spot_lights`) are now built at Brightness 3.5, Range 14. They were never built before.
- **H9 hanging lanterns:** now the library `lantern_large` at 0.85, which is the same lantern as `lantern_large_hanging` (1.2 x 1.8 x 1.15). Origin is at hole-local y 7.29, so the bottom is at 7.2, and a chain runs to y 16 in place of the FBX cord. This replaces the stage-g `lantern_medium` stand-ins.
- **Rail-lantern stand-ins fixed:**
  - Stage g built them at light height, so the H8 ones floated ~5.6 studs over the ground.
  - Each one now stands on the ground at its manifest dressing instance (`base`/`yaw` via `light_id`), with `lantern_small` centred on the light point.
  - Stakes are a stake; crooks are a 6.5-tall post with an arm out to the lantern.
- **Ring glow disc r 0.45:** CourseBuilder's part-built glow disc at the H8 ring trigger is 0.9 across, i.e. r 0.45. The old ring mesh has no disc of its own.
- Workspace PointLights: 192 → 193. All lights have no shadows. 0 decor parts collide or touch.

## 3. Removals / notch
- `heart_lantern_cluster` isn't placed: the manifest dropped it, and its stale override is gone. Only the south `h8_door_pocket` is placed now (z -7.75); the old north pocket is gone.
- **rail16 notch:** `RAIL_NOTCHES[8].rail16 = x 4.2..5.3`. The rail kit's cut is now square to a sloped rail and measured low on the body: the gap is x 4.22..5.32 at the bottom and 4.03..5.13 at the cap. The door spans x 4.4..5.1. The collision wall is untouched (as for H6).

## 4. Tests (all after the rebuild)

| Hole | mover | intended-line shots | blocked | touched | stage g |
|---|---|---|---|---|---|
| H7 | log | 20 | **10 = 50%** | 50% | 55% |
| H8 | root door | 20 | **10 = 50%** | 50% | 50% |
| H9 | lantern pendulum | 20 | **2 = 10%** | 25% | 5% |

(`playtests/lantern-v1/stage-h/blockrate-h7|h8|h9`, 0 errors)

- **Random sweep, 20 shots per hole, seed 81** (`stage-h/sweep-h7|h8|h9`): 0 escapes, 0 stuck, 0 auto-resets, 0 timeouts, 0 console errors/warnings.
  - H7 had 1 hazard drop and 1 `seam` hop. The hop is the existing parked-ball slope kick, not a stuck ball.
- **Smoke (desktop):** PASS, 0 errors/warnings, stroke → Explore → back OK.

## 7. H9 pendulum: the collider is right; the block rate is still low
- **Verified in Play on the server.**
  - `Mover_lantern_pendulum` has a single CanCollide `Blocker` (group GolfMover), 1.6 x 1.8 x 1.6, at yaw **30.00°** relative to the hole.
  - It swings **±30.0°** with a **5.0 s** period about axis world (0.885, 0, 0.465) = hole +Z. Measured: 30.0°, then -29.7°, 2.5 s apart.
  - Its centre stays exactly 7.000 from the hinge.
  - Hinge world **(-81.461, 48.996, -6.675)** = hole-local (22, 8.996, -38.5). The H9 frame is origin (-57.6, 40, 30.7), yaw 62.3.
  - The felt under the hinge is at world y 41.0. The bob bottom is 41.096 at the bottom of the swing. The yawed box's lowest corner dips to 41.02–41.03 at about ±5–10°. The ball is r 0.08, so its top is at 41.16.
  - Nothing to fix; it matches holes.json Round 7.
- **Shot line used** (GolfTest `BLOCK_LINES`): from hole-local (18.5, y 1.0, -25.0), i.e. world (-71.135, 41.08, 2.699).
  - Aim 281.2° (`aimDir`: local dir = (cos a, sin a) in x/z, i.e. (0.194, -0.981)), speed 7.75 studs/s.
  - Phases 0, 0.25 … 4.75 s.
- **In-engine,** the ball reaches the swing line (z -38.5) at **x ≈ 21.18** (0.82 west of the hinge), **2.5–2.9 s after the hit**, at only **2.7–3.2 studs/s**, slowed by the 0.5 + 0.25v decel.
  - Touches happen only in two windows near the bottom of the swing (phases 4.75–0.25 and 2.25–2.5).
  - Most other phases cross under a raised bob.
  - Blocked 2/20, touched 5/20; 3 touches were deflections that still crossed.
- **For Game Art Bot:** if the sim gets 37.5%, compare its arrival time and speed at z -38.5 (engine: ~2.6 s, ~3 studs/s, x 21.18).
  - To raise the rate: lower the bob ~0.05 so it doesn't lift clear so soon, widen it along the swing, or shorten the chain so the low window lasts longer.

## 5. Game page screenshots: `games/vr-mini-golf/marketing/screens/`
- 8 PNGs at 1920x1080, no UI: `01_h1_red_gate`, `02_h4_spinner`, `03_h5_water`, `04_h8_firefly_ring`, `05_h9_lanterns`, `06_grove_dusk` (ClockTime 18.3, restored to 17.1), `07_explore_lookout` (Lookout Rock), `08_explore_hollow_tree`. Plus `extra_explore_welcome_plaza`.
- `older/`: the two best earlier stills (stage-c `h2_chutes`, `h9_heart`, 1914x596).
- **How they're made:** the Studio viewport is only 1469x789 and can't be resized without UI input, so each still is 4 Edit-mode MCP `screen_capture` tiles.
  - The tiles share one camera point and use a narrow FOV with yaw/pitch offsets.
  - They're reprojected exactly (pure rotation = homography) onto a 1920x1080 camera with feathered seams.
  - Script: `tools/marketing/tiled.py shots.json OUT RAW [names]`.
  - Edit mode shows no player UI. The movers are at their rest poses.

---

# Stage i report: follow-ups 7-10 (2026-10-10, ~20:30 PT): all blocked, no Studio changes

**Version: NOT PUBLISHED, NOT SAVED. Live is still v79.** The last Save to Roblox in the Studio log was 2026-10-11 00:14 UTC (17:14 PT), before stages e, g and h. Studio has one window in Edit mode, holding stages e+g+h unsaved. `src/` is current. To finish: **File > Save to Roblox**, then **File > Publish to Roblox**.

**What this session can't do:**
- No Open Cloud API key in the env or the repo.
- No Claude computer-use or browser tools: no `mcp__computer-use__*`, `Claude_Browser` or `claude-in-chrome`. Only the Studio MCP is available.
- Codex is over its usage limit until 2026-10-17 00:03.

**Items:**
- **7. H9 pendulum collider:** already done in stage h (see section 7 above). The collider is the 1.6x1.8x1.6 bob at yaw 30, swinging ±30°/5 s about the hinge at world (-81.461, 48.996, -6.675). Block rate 10%. The shot line and arrival time/speed are written up for Game Art Bot. Not re-run, since nothing changed.
- **8. Game page:** NOT done. It needs a publish first (blocked), and there's no API key and no browser/computer use. Nothing was uploaded.
  - Ready to upload: `assets/vr-mini-golf/store/icon.png`, then `thumb1.png`, `thumb2.png`, `thumb3.png`, then `marketing/screens/` `02_h4_spinner`, `03_h5_water`, `04_h8_firefly_ring`, `05_h9_lanterns`, `06_grove_dusk`.
  - Draft description: *"Welcome to Lantern Grove, a 9-hole autumn mini golf course lit by lanterns and fireflies. Putt Walkabout-style in VR with a real swing, or play on phone (drag to aim, release to putt) or desktop (mouse aim and power). Dodge swinging lanterns, sliding logs and root doors, then switch to Explore mode and wander the grove: falls, lookout rock and the hollow tree."*
- **9 + 10. Mesh imports:** NOT done, because there's no importer route. Still missing, all FBX in `lantern-grove/models/fbx/`:
  - `h7_floating_log`, `h8_root_door` and `h9_lantern_pendulum` (Round 7 size, scale 1).
  - `h8_door_pocket`, `h9_pendulum_root_beam`, `firefly_ring_entry`, `lantern_large_hanging`, `rail_lantern_stake` and `rail_lantern_crook`.
  - The 21 skipped H8 decor meshes.
- **Stretch overrides kept on purpose.** Removing them before the import would shrink the old library meshes below their colliders. After the import:
  - Delete the 3 `props_overrides.json` placements whose `why` says "(Round 7)": the H7 log x1.179, the H8 door z1.106, and the H9 bob z1.613. The H9 entry also sets pos y 8.996 and yaw 30. The manifest pivots already match, so the plain manifest placement is right.
  - Pivots per manifest: log bottom centre H7 [0,-1.2,-20.5], door base centre H8 [4.75,0,-11.5] (closed), pendulum hinge H9 [22,8.996,-38.5].
  - Then run `tools/holes_to_lua.py --push --build` and re-run the H9 block rate.
- **Tests:** not re-run. No Studio or src changes this stage, so the stage h sweep stands: 0 escapes, 0 stuck, 0 resets, 0 errors.

---

# Stage j report (2026-10-10): saved prior stages, imported replacement props

## Preservation and publishing
- Used Roblox_Studio MCP `list_roblox_studios` first: exactly one Studio, place **87725688219952**, universe **10769274294**, MetavrseBuilder. Kept that window open.
- Before editing: File > Save to Roblox succeeded at **2026-10-11 04:18:25 UTC**, then File > Publish to Roblox succeeded at **04:18:41 UTC**. Studio log confirms both actions. Version History confirms this preserved build as **v102** (later marked Previously Published).

## Mesh imports and rebuild
- Imported 13 original FBXs with Studio's 3D Importer, Stud units / scale 1: `h7_floating_log`, `h8_root_door`, `h9_lantern_pendulum`, `h8_door_pocket`, `h9_pendulum_root_beam`, `firefly_ring_entry`, `lantern_large_hanging`, `rail_lantern_stake`, `rail_lantern_crook`, `glow_root_arch`, `firefly_cluster_low`, `glow_shroom_patch`, `firefly_swarm`. Temporary staging copies are byte-identical to the source FBXs.
- Registered with the existing `PropsBuilder.PrepareLibrary(sources)` in `ServerStorage.LanternGroveProps`: **13 models / 56 mesh parts**, **0 unknown materials**, **0 scale corrections**. Importer rotations normalized by the existing pipeline. Mesh asset IDs, source paths, and SHA-256 hashes: `logs/stages/j-imports.json`.
- The handoff's “21 skipped H8 decor meshes” were repeated placements, not 21 unique FBXs. Current pre-import audit: 29 missing placements across five types (2 glow_root_arch, 5 firefly_cluster_low, 5 glow_shroom_patch, 15 rail_lantern_crook, 2 firefly_swarm). After rebuild: **37 H8 dressing placements, no skipped H8 props**.
- Removed exactly the three `(Round 7)` stretch entries in `tools/props_overrides.json`. Retained the obsolete H9 lantern-string removal. Replaced the three H9 lantern_large stand-ins with the newly imported lantern_large_hanging at scale 1, preserving bottom y 7.2 and manifest light settings.
- Ran `props_to_lua.py --push` and `holes_to_lua.py --push --build`. Terrain clearance: **zero intrusions on all 9 holes**. Runtime H7–H9 decor: **zero colliding/touching parts**.

## Tests and final publish
- Random sweep (seed 82): **20 shots each on H7/H8/H9**, zero escapes, stuck balls, resets, timeouts, nudges, or console warnings/errors. H7: two expected hazard drops and one holed shot. Raw evidence: `playtests/lantern-v1/stage-j/sweep/`.
- Desktop smoke: **PASS** stroke → Explore → back; strokes 1 → 1, ball moved 0.000, zero server/client warnings/errors. Evidence: `playtests/lantern-v1/stage-j/smoke/desktop.log`.
- Final File > Save to Roblox: **04:33:56 UTC**; File > Publish to Roblox: **04:34:09 UTC**. Version History visually confirms **v105 Published**, **v102 Previously Published**. Save/publish log evidence: `logs/stages/j-publish.log`.
- Left exactly one Studio connected in Edit mode; GolfTestMode and SimulateVR false. Visually checked rebuilt H8 in the viewport.

## Game page
- Blocked at Creator Dashboard: Chrome is signed in as **MetavrsePlumber**, not MetavrseBuilder, and displays an **Updated Agreements** modal effective November 1, 2026. Asked Chase to switch accounts and handle the agreement. Did not accept terms or edit the Plumber experience.
- Icon, eight ordered thumbnails, and description remain pending. Access/privacy settings untouched.

---

# Stage m report (2026-10-11, 10:50 PT): Chase feedback + H9 Round 8 + Playtest round 3 fixes. **Published v116**

**Version:** File > Save to Roblox 17:49:52Z, then File > Publish to Roblox 17:50:06Z. Both are in the Studio log. Codex read **v116** in Version History (`logs/codex-publish-m.log`). Audience is unchanged (Friends and Playtesters), and no Robux was spent. Studio is left in Edit mode, one window, and `src/` matches Studio (export diff empty).

1. **Camera: pass-through and see-through.**
   - The putting/orbit camera (TouchControls) and the test follow camera now use `CameraOcclusion.passThrough`. Walls, rails, props and movers never push the camera; only Terrain still pulls it in, since Terrain can't be faded.
   - `CameraOcclusion.fade` sets LocalTransparencyModifier 0.7 on everything between the camera and the ball, and restores it when the view clears. That covers rails, caps, felt banks, movers and the camera-queryable decor. Decor models with 80 parts or fewer fade as a whole.
   - What gets faded: the sight line, four rays 0.3 off it, a 12-ray cone within ±10°×±8° (felt skipped, so the green in front of the ball stays), and any part the camera sits inside. It's cleared when entering Explore.
   - Explore's walking camera keeps the old `resolve` (out of scope).
   - Cost: 0.03–0.3 ms per frame.
2. **Slope felt.** CourseBuilder `SLOPE_FELT` checks each felt part's top normal. Any tilt over 2° gets Game Art Bot's chevron felt (`slope_felt_A` turned into a neutral mask, `art/slope/`), tinted with that hole's felt colour, chevron tips (+V) pointing downhill.
   - On a Top-face Texture, +U = part −X and +V = part −Z (measured with a UV test image), so the mask is uploaded in 4 rotations.
   - 18 sloped pieces are textured and no flat felt is. There was no SurfaceAppearance set from 3D Model Bot.
3. **Hole-in audio.** The cup sound is gone. Each hole-out plays a cup plunk (PSE 9117183624), then a reaction 0.25 s later:

   | Score | Sound |
   |---|---|
   | Hole-in-one / eagle | Big cheer 125361506894319 + applause 7367718809 |
   | Birdie | Cheer 105154404054447 |
   | Par | Polite applause 72098222084567 |
   | Bogey | Light claps (PSE) 9114762131 |
   | Worse / max strokes | "Aww" 77211275419736 |

   - Long sounds fade from 4 s. All of them are free Creator Store audio and public (GetProductInfo).
   - All load and play in a Play client (IsLoaded, TimeLength > 0, TimePosition advancing). **Nobody has listened to them yet.**
   - All sounds go through the SoundService.SFX group.
4. **Front end** (`GolfClient/FrontEnd`).
   - **Screens:** title (L1 logo on title_bg) with Play / Explore / Settings / How to play. Course picker: Lantern Grove card with par 27 and best; Sugarloaf Canyon and Aurora Archipelago cards marked "Coming soon". Settings: music and SFX volume, camera sensitivity 0.5–2x, VR club hand. How to play: VR / phone / desktop. Results: per-hole scorecard vs par, total ±, personal best, "New best!", Play again / Back to menu.
   - **How it fits the round:** the menu overlays a round that's already set up, so the harness and smoke are unchanged. GolfTestMode or workspace `SkipMenu` skips it. Golf input is blocked while it's open (including VR buttons).
   - **Reopening:** a HUD Menu button, or clicking the left thumbstick in VR.
   - **VR panel:** a world-space SurfaceGui 4 studs ahead at eye height that lazily re-centres when it's more than 70° out of view. `AlwaysOnTop` had to be false or it doesn't draw.
   - **Shots:** desktop, phone (iPhone 17 Pro emulator) and SimulateVR in `playtests/stage-m/ui/`, via `tools/menu_shots.py`.
   - **Music:** the game has no music yet, so the Music slider has nothing to control.
5. **Personal best** (`GolfServer/PersonalBest`). DataStore `VRMiniGolf_PB_v1`, key `u_<UserId>`: `{best = {lantern_grove = total}, settings}`.
   - Every call is in pcall with 4 tries and backoff. UpdateAsync keeps the lower total, and settings saves are batched, then flushed on leave/BindToClose.
   - Only full 9-hole rounds from hole 1 count (no harness, no DebugStartHole).
   - The best shows on the course card and the results screen.
   - **Not exercised against a live DataStore.** This place has Studio API access off, so in Studio it stays in memory. Set workspace `PBInStudio` to try the real store.
6. **H9 Round 8.** Rebuilt from holes.json in one regenerate step.
   - Hinge is at world (−81.833, 48.996, −5.967), 0.8 west of the old one. Swing is ±13°, 4 s.
   - New invisible foot collider (0.8x0.4x1.6, yaw 30, GolfMover group) welded to the bob, 7.741 below the hinge. The lantern mesh now follows the spec hinge (PropsBuilder: swing props are placed at the mover pivot). The root beam stays at x 22.
   - **Block rate** (20 BLOCK_LINES shots, (18.5, −25) at 281.2°, 7.75 studs/s): **5/20 = 25% blocked, 9/20 touched**. That's up from 2/20 = 10%; the fixed sim expected 7/20. Movers vs spec PASS. Raw data: `playtests/stage-m/blockrate/`.
7. **Lights.** The per-hole dressing-light cap (6) left props unlit. Every lantern/glow/firefly prop is now always lit: amber #FFB347, teal #7FE3D0 for glow shrooms/roots, firefly green #D8FF6A, range 8.
   - Lit counts: crooks 39/39, stakes 6/6, hook pairs 16/16, firefly_cluster_low 5/5, firefly_swarm 2/2, glow_shroom_patch 9/9, glow_root_arch 2/2.
   - New check `PropsBuilder.UnlitProps` runs on every build (in the report as `unlit`, and it warns): **0 unlit**. There are 233 PointLights in total.
8. **H8 decor names.**
   - The part-built tee signs (number + name + par) are grouped as Models named `tee_sign_h01..09`. The number-only mesh is still skipped on purpose.
   - The three trims are the manifest's H8/H9 rail-kit *skin* (no placements). props_to_lua now exports `hole_skins`, and CourseBuilder colours H8/H9 plain rails cream (block #DDD3BE, cap #F6EBD0 Limestone). Each rail piece is tagged with attribute `ManifestProp` = `rail_straight_4_trim` / `rail_straight_2_trim`.
   - The trim FBXs aren't imported, and there are no end-post parts.
   - `toadstool_cluster` is placed only on H3 in the manifest. It's present there; nothing is needed on H8.
9. **Camera probe** (`tools/camprobe.py`). It replays round 3's 483 listed wall spots × 12 yaws through the real camera code. **0 of 5,796 poses bad** (ball hidden, or more than 40% of the view around the ball covered by an unfaded opaque part), across all 9 holes including the H9 trunk tunnel, H3 mushroom tunnel, H5 bridge, H6 mill wheel and movers. The camera never moved. Before the cone rays, H9 had 18 bad spots (tunnel arch beside the ball).
10. **Club flip:** no change.

**Tests.**

| Test | Result |
|---|---|
| Random sweep, 10 shots × 9 holes (seed 113) | 0 escapes, 0 stuck, 0 resets, 0 timeouts, 0 console warnings/errors. 4 expected water drops (H5 1, H6 2, H7 1). `playtests/stage-m/sweep/` |
| `progress` (full 9-hole round to the results screen) | PASS |
| Smoke, desktop and phone | PASS: stroke → Explore → back, 0 errors. `playtests/stage-m/smoke/` |

# Stage n report (2026-10-11, 13:35 PT): Playtest round 4 (v116) fixes + slope pattern C + H9 Round 9. **Published v131**

**Version:** File > Save to Roblox 20:31:14Z, then File > Publish to Roblox 20:31:26Z. Both are in the Studio log. Codex read **v131** (Oct 11, 1:31 PM) in Version History (`logs/codex-publish-n.log`). Audience is unchanged (Friends and Playtesters), and no Robux was spent. Studio is left in Edit mode, one window, workspace attributes `SimulateVR=false, GolfTestMode=false`, and `src/` matches Studio (export diff = only this stage's edits).

1. **Slopes: pattern C (one-way arrowheads).**
   - Source: 3D Model Bot's `models/textures/slope_felt_color.png`, 8 studs per tile, +V = downhill.
   - The slope pieces are plain Parts, so they can't take a SurfaceAppearance (normal/roughness maps unused; the nap comes from Fabric). They use a Top-face Texture instead.
   - A Texture can't be rotated or brightened past its image, so `art/slope/make_slope_C.py` bakes the colour map into the three felt tones (felt / feltHi / feltLo) × 4 rotations. That's 12 uploads, keyed in CourseBuilder `SLOPE_FELT` by tone and part-local downhill axis. Pattern A is gone.
   - **All 17 sloped pieces are textured.** `tools/slope_shots.py` shoots each one from above and uphill (occluders hidden with LocalTransparencyModifier, nothing saved) into `playtests/stage-n/slopes/` (17 PNGs, `contact.png`, `slopes.json`).
   - **Verified:** I checked H4, H3 bank, H8 alcove (21°) and H9 tunnel up close: bright tips point away from the camera (downhill) with the dark fill toward it. The contact sheet shows the same orientation on every piece.
2. **H9 Round 9.** Re-imported from holes.json in one regenerate step.
   - The foot measures 0.9×0.4×1.6, yaw 0 (square to the swing), 7.762 below the hinge, invisible, CanCollide, GolfMover, welded to the bob. The hinge and the ±13°/4 s swing are unchanged.
   - **0.9 block rate:** 9/24 = **37.5%** (13 touched), so under 38%.
   - **1.0×0.4×1.6, as the spec says:** 7/24 = **29.2%** (11 touched).
   - Both runs fire at the same swing angles but some outcomes flip (e.g. 12.7° blocked vs 12.6° not), so a 24-shot run is about ±2 shots of noise. At 48 shots: **0.9 = 14/48 (29%), 1.0 = 15/48 (31%)**, 24–25 touched. **0 traps** in every run, 0 errors.
   - **Shipped at 1.0×0.4×1.6.** That's my edit to holes.json's foot size, flagged for Game Art Bot. Studio blocks about 30%, not the 45% their sim predicts. Widening the foot doesn't move it, since many touches still cross (the swinging foot pushes the ball on), so the fix is a design call: timing or a taller/wider bob.
   - Raw data: `playtests/stage-n/blockrate*/`.
3. **VR menu.**
   - The panel is anchored once per menu session: placed when the menu opens, and re-anchored only if a teleport moves the head more than 6 studs. Page changes and the lazy 70° follow no longer move it. `menu_shots.py --vr` now logs the panel position on every page: **max jump 0.000 studs across all 5 pages, PASS**.
   - `menu_shots.py --vr` levels the simulated head (`VRDebug.Head`, position and yaw kept) before opening the menu, so the shots frame the panel.
   - Also fixed: `UITextSizeConstraint` caps the post-UIScale size, so every capped label and button on the VR canvas (UIScale 1.6) drew at about 1/1.6 size. The caps now scale with VR_SCALE.
4. **Camera see-through, thicker.**
   - New `THICK_R` 1.5 spherecast along the camera→ball line (felt skipped), stopping 2.5 short of the ball so rails beside it stay. The near-camera fade radius went from 0.45 to 1.5.
   - At the H6 spot, the tee sign now fades (15 part-hits over 12 yaws).
   - **Near-camera glow:** Neon parts and light carriers within 3 studs of the camera hide (LTM 1) and their lights switch off, restored after. H9 pendulum: core hidden and both lights (bob glow + LanternGlow) off at 0.5–2.5 studs, back on at 4+.
   - Cost: about 0.43 ms/frame at H9.
5. **Hollow tree.**
   - Round 4's whole-tree fade came from the near-camera overlap: it tests bounding boxes, and the shell meshes (40–128 studs) have boxes that contain the whole H8/H9 play area. On top of that, the model (35 parts) faded as a group.
   - Now whole-model fades only apply to models ≤ 16 studs. Parts over 12 studs are left to the rays and the sphere sweep, which test real geometry.
   - Shell parts faded per pose: H8 1 → **0**, H9 14 → **0** (of 35). Total faded per pose at H9: 19 → 5.
6. **H8 rails.** PropsBuilder `RAIL_LANTERN_DIM[8]` caps all 30 H8 rail-crook lanterns (manifest lights + dressing) at brightness 0.5, range 7 (was 0.9–1.2 / 8–10), and scales their neon cores to 60%. Before/after: `playtests/stage-n/h8_rails_{before,after}_edit.jpg`. Other holes are unchanged.
7. **How to play.**
   - One platform per page with VR / Phone / Desktop tabs, defaulting to the player's device, and a fixed TextSize of 31.
   - Effective size: **desktop 27.8 px, iPhone 17 Pro emulator 18.5 pt** (root scale 0.60), **VR 49.6 canvas px** = 0.145 studs at 4 studs (~2.1°). `TextFits = true` on all three; the longest tab (VR) measures 341 of 348 px.
   - Shots: `playtests/stage-n/ui/{desktop,phone,vr}_menu_*.png`.
8. **Personal best on the real DataStore: PASS.**
   - Studio access to API services: OFF → **ON** (Codex, Game Settings > Security, other toggles unchanged).
   - Test: Play-mode server, fresh module clones per "server", mock UserId -424242, real store `VRMiniGolf_PB_v1`. Save 30 → reload 30 → 33 kept at 30 → 26 saved → reload 26. Test key removed afterwards.
   - The real Studio player also loads from the store (SettingsLoaded). 0 errors. `PBInStudio` was removed afterwards, so Studio test runs stay in memory.
   - Details: `playtests/stage-n/personal_best.md`.

**Tests.**

| Test | Result |
|---|---|
| Camprobe (483 round-3 spots × 12 yaws) | **0 / 5,796 bad** on all 9 holes |
| Random sweep 10 × 9 holes (seed 114) | 0 escapes, 0 stuck, 0 resets, 0 timeouts, 0 console warnings/errors. Expected hazard drops: H2 2, H5 3, H7 1. H2 logged 2 seam-hop nudges during ball placement (0.35 s apart, not stuck) |
| Smoke desktop / iPhone 17 Pro | PASS / PASS (stroke → Explore → back, 0 errors) |
| Menu shots desktop / phone / VR | 0 errors; VR panel jump 0.000 |

# Stage o report (2026-10-11, 15:25 PT): H9 pendulum plinth mesh import. **Published v135**

**Version:** File > Save to Roblox 22:19:12Z, then File > Publish to Roblox 22:19:35Z. Both are in the Studio log. Codex read **v135** (Oct 11, 3:19 PM) in Version History (`logs/codex-publish-o.log`). Audience is unchanged (Friends and Playtesters), and no Robux was spent. Studio is left in Edit mode, one window, workspace attributes `SimulateVR=false, GolfTestMode=false`, and `src/` matches Studio (the export diff shows only this stage's edits).

1. **Import.** Codex used the 3D Importer (preset "LG Stud Scene Anchored", one file per import, `logs/codex-import-h9-o.log`) for two files, with no warnings:
   - `h9_lantern_pendulum.fbx`: 5 MeshParts, 1,820 polys, 2.16×8.07×2.16.
   - `h9_pendulum_root_beam.fbx`: 6 MeshParts, 1,650 polys, 20.45×9.58×1.44.
   - `PropsBuilder.PrepareLibrary` registered both: 11 parts, 0 unknown meshes, no scale fix needed. The root beam came in turned 180° by the importer and was turned back automatically.
2. **Data-driven refresh.** 3D Model Bot re-exported these two FBXs (12:45) but didn't update `models/manifest.json` (still 10-10). So:
   - New `tools/fbx_bounds.py` reads per-mesh bounds straight from a binary FBX. Checked against the manifest on the unchanged meshes (CapGold, Glow, MoveCream): exact.
   - `props_to_lua.py` now applies `props_overrides.json` `fbx_refresh` (per-mesh centres + prop bbox from the FBX) for `h9_lantern_pendulum` and `h9_pendulum_root_beam`.
   - A placement override moves the beam's pivot to the hinge, x 21.2.
   - When the manifest is updated, delete those entries. The re-import is still one step: `props_to_lua.py --push`, then `holes_to_lua.py --push --build`.
3. **Result in Studio** (hole-local):
   - Beam pivot is at (21.2, 8.996, −38.5) and the beam bbox centre is at x 22.00. Only the bracket is at the hinge.
   - Pendulum `Iron` = 0.9×8.072×1.6 with the plinth. Its bottom is 7.962 below the hinge, which is exactly the foot's bottom, and its rotation relative to the foot is identity (yaw 0).
   - The 5 pendulum MeshParts are welded to the mover's MoverRoot. The bob Blocker and the foot are welded to the same root, so all of it is one rigid assembly. Every MeshPart is CanCollide/CanTouch/CanQuery false and Massless.
   - The only colliders on the mover are the Blocker 1.6×1.8×1.6 and the invisible foot 1.0×0.4×1.6.
4. **Swing (Play, 40 samples).**
   - Angle vs `13·sin(2π·t/4)` about hole +Z at the hinge: max error 0.33° (servo lag, as before).
   - Plinth-to-foot offset drift: 0.0001 studs.
5. **Visual overlap.** Shots are in `playtests/stage-o/plinth/`, at 0°, −13° and +13° with the foot tinted cyan for the check (restored afterwards), plus a wide shot.
   - The dark plinth covers the foot at every angle.
   - Only 0.05-stud slivers show on each side along the swing, because the shipped foot is 1.0 wide (stage n) and the plinth is 0.9. The foot is invisible in game, so nothing shows there.
   - **Game Art Bot:** to close the slivers, either widen the plinth to 1.0 or decide on the 0.9 foot.
   - The large cyan patch in the first tinted shots was z-fighting between the coplanar 1.6-deep faces. It went away when the debug tint was 1% shallower.

**Tests.**

| Test | Result |
|---|---|
| H9 block rate, 24 shots, same opts as stage n (`blockShots 24`) | **7/24 = 29.2% blocked (stage n: 7/24), 12 touched (stage n: 11)**, all at rest, 0 traps, 0 console warnings/errors. `playtests/stage-o/blockrate/` |
| Random sweep, H9, 20 shots (seed 115) | 0 escapes, 0 stuck, 0 resets, 0 timeouts, 0 nudges, 0 console warnings/errors. `playtests/stage-o/sweep/` |
| Smoke desktop / iPhone 17 Pro | PASS / PASS (stroke → Explore → back, 0 errors) |
