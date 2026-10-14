## Stage au5 — Aurora published v6; expected-v5 gate failed (Oct 14, 2026)

Aurora (place 79649062523043, universe 10769274294) received all 12 props_fix_overlap replacements, hidden Blockout cleanup, and H14/H6/H5 visual fixes. Scan 1451 → 1093, exposed planar 0; all 615 colliders exact, placeholders 0/0. Untouched v4 and final sweeps both 54 cups / 36 random shots / 0 stuck / 0 escapes / 0 timeouts; desktop smoke has zero console problems. One exact-row overwrite published **v6**, because saved/unpublished v5 already existed from Oct 13 at 10:29 PM. Task's N=5 requirement therefore FAILS; no republish or restore attempted. Saved `playtest/playtest-aurora_archipelago-v6.rbxl`; Studio closed using TERM then KILL after Applying script changes stalled. Protected published versions remain lobby 251, Sugarloaf 23, Lantern Grove 12. No git push or RBXL commit. See `logs/stages/au5-notes.md` and `playtests/stage-au5/`.

## Stage zf3 — Lantern Grove published v12 (Oct 13, 2026)

Lantern Grove (place 91438142503824, universe 10769274294) published v12, verified in Creator Hub published-only history. Visual separation covers Course and World: scan 5114 → 3208, exposed planar candidates 1050 → 0; all 270 colliders unchanged, placeholders 0/0. Baseline and final nine-hole sweeps each passed 27 cup drops and 18 random shots, with zero stuck/escape/timeout findings or console errors; desktop smoke passed. Saved `playtest/playtest-lantern_grove-v12.rbxl`; Studio closed. Protected published versions unchanged: lobby 251, Sugarloaf 23, Aurora 4. No git push or asset edits. See `logs/stages/zf2-notes.md` (Lantern Grove zf3 corrected-gate retry) and `playtests/stage-zf2/lg/`. Live headset/teleport checks and conservative mesh/terrain/transparency review remain open.

## Stage al2 — Sugarloaf hint decals, local fix2 (Oct 13, 2026)

Five approved MetavrseBuilder image assets placed persistently through SugarloafHints/Overrides; 10 primitive placeholder parts removed. Route-relative arrows follow the rotated H9 bypass and H14 left-bank/bucket routes (coordinate ambiguity documented in `logs/stages/al2-notes.md`). H9/H14: cupdrop 6/6, random 16 completed, stuck/escapes/timeouts 0; zero client/server console warnings/errors. All 705 physical colliders unchanged. Saved `playtest/playtest-sc-fix2.rbxl`; Studio closed. No cloud place open/save, publish or git push. Publishing waits for Playtest Bot's clean sweep; H15 findings remain.

## Stage am — Aurora v5 local (Oct 13, 2026)

Local `playtest/playtest-aurora-v5.rbxl` saved; Studio closed. Batch 3: 23 props / 83 meshes, rev2 H18 arch and steamless rev2 H6 pool with low runtime steam. Data-driven H17 fades/lamp/sparkles; 6/6 timed crossings, 3/3 +1 fall/entry respawns. Cupdrop 54/54, random 144, slow 36, stuck 0/escapes 0, zero console warnings/errors. Clearance report lists 16 unique flagged props (12 source real + 56 built prop-class findings). All 55 sources match. No cloud place open/save, publish, asset sync, or git push. See `logs/stages/am-notes.md` and `playtests/stage-am/flagged-props.md`.

# VR Mini Golf: status

## Stage ak — lobby published v248 (2026-10-13)
- Lobby **v248 Published**, verified in Studio Version History: October 13, 11:35 AM, <Auto save>, Published. Publish confirmation at 11:38 AM PT.
- Current src pushed; all 51 scripts verified. Lobby uses OUR VRControls, wrist card, putter, sticks and B/Y scorecard gear; Close/title/gear have no overlap. Desktop retains LobbyRoam.
- Desktop + iPhone smoke and SimulateVR quick check PASS, zero console warnings/errors. SimulateVR=false and GolfTestMode=false. Cloud lobby content retained; no course place opened/saved/published. **LG v9 and SC v19 unchanged.**
- Local copy: `playtest/playtest-lobby-v248.rbxl` (849,772 bytes); all 51 serialized sources match src. Download created no additional history row observed after refresh. Studio closed; no git push.
- Notes: `logs/stages/ak-notes.md`; evidence: `playtests/stage-ak/`.

## Stage ah — local Aurora collider check (2026-10-12)
- H18 ramp foot is continuous; H6 east cup-pad lip is 0.008736 studs and matches the authored slope/pad overlap. H6 pool footprint matches holes.json exactly in X/Z.
- Raised H18 crystal-bank edges and H6 pad/layout improvements remain Game Art Bot design/data issues. No source/geometry fixes or conditional shot regressions were needed.
- Aurora `playtest/playtest-aurora-v3.rbxl` unchanged; no v3b, save, publish, upload or push. Studio closed. Sugarloaf H8 untouched. Evidence: `playtests/stage-ah/`; notes: `logs/stages/ah-notes.md`.

## Stage ab — Sugarloaf kit + lighting + cups, VR feedback, real menu/loading art, lobby portals (2026-10-12, ~18:10 PT)
- Published **Sugarloaf Canyon v19, Lantern Grove v9, Lobby v246** (each confirmed Published in Version History).
- **Chase's VR items** (all places): the wrist card works on either wrist; no thumbstick-click menu (VR menu = B / Y scorecard, then the gear); club setup stick LEFT/RIGHT turns the putter head (saved headYaw) instead of moving it on the ground; the head is level only on / near the ground and rigid with the club when lifted (smooth blend).
- **Real UI art**: menu frame, close X, round menu badge, and the Lantern Grove / Sugarloaf loading cards (Config.UI, tools/stage_ab_assets.json).
- **Sugarloaf**: pass 6 world kit placed (874 instances, decoration only; gondola cabin rides at 6 studs/s), Game Art Bot's lighting preset, Terrain taken out of the cups (WorldBuilder.CapUnderCup) and out of H8's washboard troughs. Cup drop 18/18 holes (54/54 putts), stuck sweep 0 escapes / 0 lost balls.
- **Lantern Grove**: H7 block rate 41.7% (in 38-50%), H9 hidden backing-stone dup removed, H8 floating stone onto its bank, H8 cream rails now limestone. 9/9 regression PASS.
- **Lobby**: pass 10 portal arches, lanterns, portal quads and per-course scenery (crown tips Neon #9FE6F2, low candy glow, lantern shadows off). Default Roblox VR controls in the lobby. Smoke desktop + iPhone PASS.
- 0 console errors in every run. Round 9 report not reachable from the Mini (not read). Notes: logs/stages/ab-notes.md.

## Stage aa — new wrist card + scorecard settings gear (2026-10-12, ~13:50 PT)
- **VR wrist card** uses the new art (`ui/wrist/wrist_card_bg_nobuttons.png`, same file on both wrists) with hole / name / PAR / STROKE / TOTAL / BEST drawn live in the README zones. **No MENU / SCORES buttons**: the menu is the left-stick click, the scorecard is B / Y.
- **Scorecard settings gear** (`ui/scorecard/settings_button{,_pressed}.png`): an ImageButton badge on the card's top-right corner (Close X beside it) that opens Settings. Works on desktop, phone and VR (laser pointer).
- Published all three places: **LG v7, SC v5, Lobby v244**. Smoke (desktop/phone), VR pointer walk and wrist shots pass with 0 console errors. Notes: logs/stages/aa-notes.md.

## Stage z — the place split, phase 1 (2026-10-12, ~12:55 PT)
- **Three places in universe 10769274294** (places.json): **Lobby** "VR Mini Golf" 87725688219952 (start place, live **v243**), **Lantern Grove** 91438142503824 (**v5**) and **Sugarloaf Canyon** 124440050576723 (**v4**), connected by TeleportService (TeleportOptions, a loading screen per course).
- Lobby: no golf ball. Walk around, pick a course on the menu or walk into an arch (10x10x3 Neon portal triggers in the LG and SC arches). The "Best Rounds" leaderboard wall reads OrderedDataStores the course places write, and refreshes every 60 s.
- Course places: hole 1 starts on arrival. Menu > Lobby, results > Back to lobby, or 30 s after finishing takes you back to the lobby. In Studio, teleports are skipped and recorded.
- One **Menu button, top right** (top bar row, TopbarSafeInsets) in every place; the HUD's Menu button is removed. New menu art: 9-slice frame, close X, menu button. **It's stand-in art** (the box's /workspace was unreachable); swap the PNGs in assets/vr-mini-golf/ui/ and re-upload.
- Same scripts in every place, synced from src/ with `run_playtests.py push` (one place open at a time; each place's workspace PlaceRole decides what runs). Tests pass with 0 console errors: lobby smoke (desktop + phone), LG 9/9 in its own place, LG and SC smoke. Notes: logs/stages/z-notes.md.
- Not yet: a live cross-place teleport check, real leaderboard data (live only), VR lobby on a headset, the Sugarloaf scenery kit, lobby dressing and portal meshes (phase 2).

## Stage y — live v241 (2026-10-12, ~09:44 PT)
- **Lobby menu is a window you can close** (Chase on v239: full-screen menu, couldn't walk around the lobby, no way back on mobile). The title/course menu is a centred panel (~60% of the screen, more of the height on phones) with the 3D lobby visible around it, and an X. Closing it in the lobby gives normal Roblox controls (GolfClient.LobbyRoam: WASD/jump/mouse camera, touch thumbstick; VR walks with the left stick). Ball stays hidden in the lobby.
- Reopen: top-left Menu button (top bar row, phone + desktop), M on desktop, left-stick click / wrist MENU in VR. Picking a course still uses SelectCourse.
- `run_playtests.py smoke` now also opens/closes the panel, walks the character 32 studs with W, and reopens it (Menu button + M). Desktop + phone smoke, LG 9/9 regression, 0 console errors. Notes: logs/stages/y-notes.md.

## Stage x — live v239 (2026-10-12, ~09:23 PT)
- **Lobby spawn fix** (Chase: live v235 dropped players on Lantern Grove H1 with no lobby). Cause: the only SpawnLocation sat on LG's Welcome Plaza beside H1 (CourseBuilder put it there), the lobby's LobbySpawn was only a marker, and GolfServer defaulted every join to Lantern Grove and started H1 on Ready.
- Now: workspace.SpawnLocation sits under Lobby.LobbySpawn (CourseBuilder keeps it there). A fresh join has no course (no `Course` attribute); the ball waits hidden on the lobby spot and the menu opens on the title. Picking a course on the course card (SelectCourse) starts that course's hole 1. GolfTestMode keeps the old LG-on-Ready default.
- `run_playtests.py smoke` now checks the lobby spawn first (character in Lobby bounds, no course, title menu, then the LG / Sugarloaf / LG course-card picks each land on hole 1). Smoke + LG 9-hole regression pass, 0 console errors. Notes: logs/stages/x-notes.md.

## Stage w — live v235 (2026-10-12, ~07:23 PT)
- **Sugarloaf Canyon (18 holes, par 54) is playable** in the same place as its own course: workspace.CourseSugarloaf, 5000 studs north of Lantern Grove (SugarloafLayout offset (0,0,-5000)). Players pick it on the course card ("18 holes - Par 54"); each player's course is the player attribute `Course` (ReplicatedStorage.Golf.Courses, GolfServer SelectCourse). Sugarloaf has its own sunset lighting while the camera is in its world box (GolfClient.CourseLighting).
- Rebuild: `python3 tools/sugarloaf_to_lua.py --push`, then in Edit `CourseBuilder.Build(SugarloafCanyon, SugarloafLayout, {folder="CourseSugarloaf", courseId="sugarloaf_canyon", palette="sugarloaf"})`, `SugarloafBuilder.PlaceMeshes()` (pass 5 mover meshes from ServerStorage.SugarloafMovers) and `SugarloafBuilder.CheckClearance()`. Terrain: `python3 tools/world_terrain.py --sugarloaf` (writes Terrain only in Sugarloaf's box).
- Sweeps: `run_playtests.py holes N --opts '{"course":"sugarloaf_canyon","parts":"fuzz,slow"}'`.
- Lantern Grove: round 8 bank-backing/H9 rail/H9 lip art fixes, and H7/H8 block rate ~46% (shorter dwell in the ball's path). Details and numbers: logs/stages/w-notes.md. Local copy playtest-v235.rbxl (gitignored).
- Known gaps: Sugarloaf's world kit (106 cliff/building FBX), walkways/lifts/gondola and water beams are not built (Terrain + part props + mover meshes only). The lobby arch is still decorative.

## Stage v — live v210 (2026-10-12, ~02:29 PT)
- Playtest Bot round 7 fixes (RobloxDevBot items 1, 2+3, 4, 5/6, 9) plus Game Art Bot colour notes, published. Version History marks v210 Published. Local copy playtest-v210.rbxl (gitignored).
- ClubSetup/WristPoseLog DataStore calls guarded like PersonalBest. H8 root door: pocket widened and rail16 cut trimmed (>= 0.187 stud clearance); slow/parked balls get a 1.2 studs/s sideways nudge driven by spec motion (MoverMath, 0.5 s dwell look-ahead). h8door 20/20 (max 1.2 studs/s, 0 pinned), block rate 50%, H8 20-shot sweep clean.
- XRay: VR club outline only at rest while aiming; flat fades 0.06-0.07 s. Course card shows "Play" until the first stroke. Banks 0.78x adjacent felt; H9 oak rail wood #7A4E32, Reflectance 0.
- Evidence playtests/stage-v/, notes logs/stages/v-notes.md.

## Stage t — live v202 (2026-10-11, 23:31 PT)
- Lobby fixes, Peaceful/PVP collision modes, independent progression, wrist event telemetry and rest/aim-only XRay published. Version History explicitly marks v202 Published.
- Untouched v190 local backup retained (3,285,911 bytes, gitignored). Studio left saved in Edit, source export matches src/.
- Modes 13/13, all-nine VR/swing, desktop/iPhone, Stage s wrist checks, club setup, H9 lighting and XRay pass with clean consoles. H6 random sweep has no stuck/escape/reset flags; fixture limitations recorded.
- Wrist behavior verified from actual events; legacy aggregate counter falsely counts new pose events as hides and remains unfixed. Boardwalk exists separately; gameplay-spawn/portal integration remains separate work.
- Full report: logs/stages/e-report.md; evidence: playtests/stage-t/. Audience unchanged, no Robux spent.

## Stage r — live v167 (2026-10-11, 18:50 PT)
- Round5 wrist failures traced to test timing/hand selection/synthetic Best fixtures; final regression passes 23 pointer actions, three resume/scores cycles and both hands with Best-2.
- VR all nine holes + simulated swing pass (6.809 studs/s measured / 6.80 expected). Physics and v12 mount unchanged.
- VR mill-wheel outlines now update every render frame: 600-frame check, 0 misses / 0 false shows for ball and club.
- Banks at 25° or steeper use plain felt tinted 15% darker; gentle slopes retain pattern C; one-step regeneration preserved.
- Reimported five-part bracer; supplied FBX still had old face, fitted to 0.37 × 0.28328125 for exact 1024 × 784 Top canvas. Both-hand screenshots verified. Existing wrist gates unchanged.
- Wrist simulation and desktop/iPhone smoke pass with clean consoles. H9 random20:0 escapes/stuck/resets; all final consoles clean. Saved and published; Version History confirms v167 Published. Studio left in Edit; audience remains Friends and Playtesters.
- Evidence: `playtests/stage-r/`; full report: `logs/stages/e-report.md`; resume notes: `logs/stages/r-notes.md`.

## Where it lives
| | Owner | Universe | Root place | URL |
|---|---|---|---|---|
| **Current (use this)** | MetavrseBuilder (user 1818120139) | 10769274294 | 87725688219952 | https://www.roblox.com/games/87725688219952 |
| ↳ Lantern Grove place (stage z) | MetavrseBuilder | 10769274294 | 91438142503824 | teleport only (from the lobby) |
| ↳ Sugarloaf Canyon place (stage z) | MetavrseBuilder | 10769274294 | 124440050576723 | teleport only (from the lobby) |
| Original (leave alone) | MetavrsePlumber (user 2021224569) | 10769263747 | 135374506016678 | https://www.roblox.com/games/135374506016678 |

- 2026-10-03 ~21:59 PT: re-published as a **new experience under MetavrseBuilder** (Grok Bot, via Studio File > Publish to Roblox As > Create new experience).
  - Name and description: "VR Mini Golf".
  - Devices: Computer, Phone, Tablet, VR.
  - Team Create is on.
  - It is **Private** (new experiences start private) and the maturity questionnaire hasn't been filled in, so playability is `ContextualPlayabilityUnrated`.
- Why: Roblox can't transfer an experience from one user to another (transfers only go to groups), and the game had no players, passes, products or badges. So a fresh publish was the cleanest move.
- Source of the copy: the Team Create state of Plumber's place, downloaded with File > Download a Copy at ~21:53 PT. It includes the 21:00-21:13 PT VR fixes, which were never published to the Plumber experience: `BallRadius` 0.08, `RollDecel` 3.6, `VRGripToPutt`, `VRClubAngle`, Walkabout control map.
  - Local backup: `games/vr-mini-golf/VR-Mini-Golf-from-Plumber.rbxl` (137 KB, gitignored).
- The Plumber original is untouched: still Limited/private, 3 visits. Archive or delete it later only if Chase wants to.

## Verified in Studio as MetavrseBuilder (2026-10-03 ~22:00 PT)
- Place: 323 instances and 9 scripts.
- Asset references:
  - Default Roblox Sky textures: 6444884337, 6412503613, 6444884785, sun 6196665106, moon 6444320592. These are public, not Plumber's.
  - Built-in `rbxasset://sounds/clickfast.wav` and `electronicpingshort.wav`.
  - No meshes, packages, animations, decals or audio uploaded by Plumber, so nothing needed re-uploading. All 7 references `PreloadAsync` → Success under Builder.
- Solo playtest:
  - 0 errors and 0 warnings (server and client).
  - Course, ball and HUD all load ("Hole 1 - Warm Up", "Par 2 | Strokes 0", Reset Ball, Scorecard).

## 2026-10-03 ~23:00 PT: VR playtest fixes (published as v9, ~23:03 PT; audience still Limited: Friends + Playtesters)
Measured with the new harness (`playtesting.md`). Baseline: `playtests/2026-10-03/baseline/`. After: `playtests/2026-10-03/after/` (+ `.mov` clips, kept local). Full table: `playtests/2026-10-03/compare.md`. Physics tuned to `walkabout-reference.md`.

1. **Club origin/axis:**
   - The shaft now starts at the controller tip (`VRClubTipOffset` 0.2 studs = 6 cm in front of the hand origin) and runs along the hand LookVector (pointing axis), pitched by `VRClubAngle`.
   - The grip visual is now a short ferrule at the tip.
   - The axis is an assumption; Chase needs to check it on the Quest (see `playtesting.md`).
2. **Putter head plane:**
   - Felt/CupPlate/Ramp are tagged `GolfSurface` (`CourseBuilder.ApplyPhysics`).
   - Near the ball, the head is clamped to the plane of the felt under the ball (slope-aware) and never to walls.
   - Ledge head Δ went from +0.51 studs (riding the wall top) to +0.011 (the intended 3 mm clearance).
   - Ghost sweeps through a wall and a post: lift 0.001, follow error 0, ball untouched. Club parts don't collide, touch or query.
   - Baseline's 9-stud "lift" was partly a harness artifact (it measured while the club moved from its parked pose). The real climb was the 0.5-stud wall.
3. **Character/VR rig:**
   - Near the ball, the rig floor uses the ball's plane height.
   - Walls, bumpers, house, roof and blades are in collision group `GolfWall`. It collides with the ball but not `GolfPlayer`/`GolfClub`.
   - The VR character is PlatformStand with a local anti-gravity force, pivoted every frame.
   - Rig floor Δ went from -1.0/-2.2 to +0.001, and character feet from -0.34…-0.53 to +0.001 in all 3 ledge cases.
4. **Wall restitution and ball feel:**
   - Walls: `WallElasticity` 0.63, `BumperElasticity` 0.65, `WallFriction` 0.05 (from 0.8/0.92/0.02).
   - Normal restitution went from 0.74–0.90 to 0.59–0.63. Tangential retention is 0.93–0.98, where the bumper used to gain speed (1.05).
   - New post-impact skid (`SpinKeep` 0.5, `SlideFriction` 0.3): a head-on hit leaves at 0.61× and drops to 0.39–0.54× after 0.3 s (Walkabout: ~0.6 then ~⅓).
   - Felt: deceleration is now `RollDecel` 0.5 + `RollDrag` 0.25·v (with `EngineRollLoss` 0.2 compensation), and `workspace.Gravity` 35 → 32.7.
     - Rollout at 2/4/6 m/s went from 1.69/6.76/15.2 m to 4.61/11.34/18.47 m.
     - That's within 3% of the model.
   - `RestTime` is 0.5.
5. **Cup:**
   - `CupCaptureSpeed` 1.6 m/s: a ball over the cup slower than that drops in.
   - 1.3 and 1.6 m/s putts from 60 cm hole on the first pass. 2 m/s (reaching the rim at ~1.8 m/s) is borderline and holed in one of two runs. 2.5–3 m/s skip or lip out.
   - The baseline's "not first pass" for slow putts was mostly a metric artifact: the ball's own drop against the rim counted as a contact. Now only contacts away from the cup count.
6. **Bug fix:** the server ignores out-of-bounds for 0.75 s after any ball placement.
   - Before, a rewind (right stick back) while the ball was rolling could be judged OOB from a stale client position, costing +1 penalty stroke.
   - The cup check is unchanged.
- Normal solo playtest (smoke): 0 errors and 0 warnings on server and client, hole 1 HUD visible.
- Not changed: phone/touch controls. They share `Ball.hit`, so the faster felt affects them too; `TouchMaxSpeed` 26 may now feel strong.

### Check against `walkabout-reference.md`
- Gravity 32.7 studs/s² (Earth at 0.3 m/stud; Roblox's default 196.2 would be 6× Earth): matches.
- Roll deceleration 0.5 + 0.25·v studs/s² (0.15 m/s² + 0.25/s·v): matches the fit. Fast putts (2–6 m/s) roll 5.8–9.4 s, which is what the fit gives. Walkabout's 2–3.5 s putts are slower ones (~0.5–1 m/s).
- Walls: measured normal restitution 0.59–0.63 vs ~0.6; spin kept and skid after the hit (`SlideFriction` 0.3 × 32.7 ≈ 9.8 studs/s²): matches.
- Cup capture below 1.6 m/s; 1.3 and 1.6 m/s putts hole cleanly (reference: clean at ~0.47 m/s): consistent.
- Putter: head held on the ball's plane, shaft length varies, ghosts through all geometry, `VRGripToPutt` makes it see-through (0.65) and unable to hit until grip is held: matches (mode is off by default).
- **Gap:** felt bounce. Felt is Elasticity 0 (weight 100), so drops off ledges land dead. Reference: ~0.6 with drops under ~1.5 studs/s zeroed. Not changed in v9.

## 2026-10-09 ~20:00 PT: VR club runs parallel to the controller handle (published as v12, 20:14 PT; audience still Limited: Friends + Playtesters)
Chase reported that on a real Quest the club came out roughly perpendicular to the controller handle.

**Root cause:** the shaft ran along the hand CFrame LookVector (-Z), which is the **aim ray**. On Quest Touch the handle is ~125° from that ray: it runs along -Y, raked back toward +Z.

**Fix (`VRControls.defaultClubMount`):**
- **Shaft direction:** hand-space `Angles(rad(-90 - VRClubGripPitch), 0, 0) * yaw * roll` applied to LookVector. The -90° turns the aim ray down the handle; the pitch rakes it toward +Z.
- **Start point:** the bottom of the handle, `VRClubButtOffset` along that axis.
- **New Config values:** `VRClubGripPitch` 35, `VRClubGripYaw` 0, `VRClubGripRoll` 0, `VRClubButtOffset` 0.25 studs (7.5 cm).
- **Left hand:** pitch is about hand X, so it is the same for both hands. Yaw and roll are mirrored.
- **Legacy mount:** `VRClubLegacyAim = true` restores the old tip/aim-ray mount (`VRClubAngle`, `VRClubTipOffset`, now legacy-only).
- **A-button refit:** keeps the butt point and re-aims the shaft from it.
- Plane snap, ghosting and the hit math are unchanged.

**Measured in a putting-grip pose** (hand 0.91 m up, handle aimed at the ball):

| | Before | After |
|---|---|---|
| Shaft vs handle | 125° | 0° |
| Shaft start vs handle bottom | 0.40 studs away | 0 |
| Head bottom above the ball's plane | 4.98 studs (floating) | 0.011 (3 mm) |
| Head to the spot behind the ball | 5.13 studs | 0.001 |

- A-button refit: shaft vertical from the handle bottom, head on the plane.
- ledge, ghost and the VR swing (6.80 studs/s, as expected) all pass. Smoke: 0 errors.
- Screenshots (side/front/top/close-ups, before/after) and iteration notes: `playtests/2026-10-09-clubfix/` (`NOTES.md`).
- **Harness additions:**
  - The `clubviz` scenario.
  - `GolfTestAPI` `clubpose`.
  - The `GolfTestClubDebug` overlay (a proxy Quest controller plus axis gizmos).
  - The `look` camera.
  - `run_playtests.py clubviz` (window screenshots).
- Published 2026-10-09 20:14:30 PT as v12 (File > Publish to Roblox; Studio output "Place published. Friends and playtesters can now play"). Audience and settings unchanged.

## 2026-10-10 00:02 PT: Lantern Grove round 1, flat greybox (published as v23)
- 9 holes from `assets/vr-mini-golf/lantern-grove/holes.json` (par 27), built by `ServerStorage.CourseBuilder` from the generated `CourseData.LanternGrove` (`tools/holes_to_lua.py`). Holes still sit on the flat greybox plane (holes.json `world_offset`).
- Per-hole suites (`playtests/lantern-v1/iter1/summary.md`): every hole holed on both AI routes; 0 real escapes, 0 stuck. The one H6 "escape" was a harness artifact (fixed: `LastOOB` now carries a running count so a repeat hazard replicates). H9: 2 unstick nudges at the root gate (the designed safety). Aces found in-engine on H2, H4, H5.
- H7 log pin: fixed with the slide-range clearance + unstick nudge (`playtests/lantern-v1/before-fix` vs `after-fix`). H8 root door clamped to [-1.68, 1.66].
- Screenshot iterations: 1 (run 2, `iter1-shots/`), 2 (`hole01..09.png`, `round1-greybox/`). Fix from iteration 2: H6 north rail (rail5) visual notch at x 5..10 for the mill wheel.
- Progression check fixed (near-cup spot on the cup's felt level). Desktop and iPhone smoke: 0 errors, 0 warnings.
- Published by Codex computer use (File > Publish to Roblox): "Place published. Friends and playtesters can now play this place in Roblox." Version History: v23, 2026-10-10 12:02 AM. Audience unchanged.

## 2026-10-10 13:52 PT: Lantern Grove round 1 with world + team fixes (published as v43)
- World terrain, water, paths and the hollow tree around the 9 holes; Playtest Bot fixes: 0.5-stud mover clearance, 1.5 s pin nudge, H9 Lantern Knot visual, teleport exit FX, H9 gate pushes balls aside, 3 s auto-reset on H4/H6/H7/H8/H9. Cup capture 5.33 studs/s (verified).
- Random-shot sweep (20/hole): 0 escapes, 0 stuck, 0 console errors (`playtests/lantern-v1/sweep-b/`). Shots: `playtests/lantern-v1/overview.png`, `hole01..09.png`.
- Published by Codex computer use (File > Publish to Roblox): "Place published. Friends and playtesters can now play this place in Roblox." Version History: v43, 2026-10-10 1:52 PM. Audience unchanged.
- Re-import after a new holes.json: `python3 tools/holes_to_lua.py --push --build` (course + props + terrain carve).

## 2026-10-10 16:50 PT: Lantern Grove stage c, spec v2 + props pass 6 + world pieces (saved, not published)
- Spec v2 imported and regenerated (H4 short padded spinner, H5 respawn at the bridge entry, H7 log +-7, H8 shorter route + alcove bank + pockets + new exit ring, H9 lantern pendulum + tunnel dip, flags everywhere). Stroke timeout 20 s.
- 3D Model Bot pass-6 props and all world pieces (hollow tree shell + crown, sister trees, falls, cliffs, tree line, hills, mountains) imported and placed. Final sweep 180 shots: 0 escapes/stuck/resets/timeouts, 0 console errors. See `logs/stages/progress.md` and `playtests/lantern-v1/stage-c/README.md`.
- Re-import after a new manifest: `python3 tools/props_to_lua.py --push`, import any new FBX (3D Importer), `PropsBuilder.PrepareLibrary({<imported models>})`, then `holes_to_lua.py --build`. World pieces: `tools/world_pieces_to_lua.py --push`, import, `WorldBuilder.PrepareWorldLibrary()`, `WorldBuilder.BuildScenery()`.

## 2026-10-10 17:11 PT: Lantern Grove stage d, movement + Explore + round-1 UI fixes (published as v79)
- **Movement**:
  - Hole-out -> score -> fade to black -> next tee, measured on desktop.
  - VR trigger warps you to your ball; `progress` passes on all 9 holes in simulated VR.
  - Desktop/phone: the camera follows the ball.
- **Explore mode** (Chase), `GolfClient/Explore.luau` + `GolfServer` `SetExplore`:
  - HUD Explore button: no ball (the server parks it), no score.
  - Walk/jump/sprint/fly, with normal-feeling gravity for the character only.
  - Teleport menu: H1-H9 tee views + Welcome Plaza, Grand Falls, Hollow Tree, Lantern Mere, Lookout Rock.
  - A fall respawns you on the nearest walkway. Invisible players-only walls (`workspace.ExploreBounds`) at the
    terrain edge.
  - Back to golf restores the ball and strokes. Per player.
- **Round-1 (v43) fixes**:
  - Roblox player list hidden (it covered Reset Ball).
  - Own avatar fully hidden in the putting camera.
  - Info panel below the chat area.
  - Help line wraps on narrow screens; compact, scrolling scorecard.
  - Terrain grass cleared 1 stud (+ half a voxel) along every rail (`WorldBuilder.ClearGrassNearRails`, part of the
    carve).
- **Checks**:
  - Sweep: 180 random shots, 0 escapes / stuck / auto-resets / timeouts / console errors.
  - Smoke desktop + iPhone 17 Pro emulation: 0 errors/warnings, Explore round trip clean.
  - Per-hole shots reviewed.
  - Everything is in `playtests/lantern-v1/REPORT.md`.
- **Published** by Codex computer use (Save, then File > Publish to Roblox): "Published new changes in "VR Mini Golf"
  to Roblox." v79, 5:11 PM. Audience unchanged (Friends and Playtesters).
  - Lighting.Technology couldn't be read or set (hidden in this Studio's Properties panel); see the report.

## TODO
- [ ] Felt bounce: ~0.6 elasticity for landings faster than ~1.5 studs/s (e.g. in BallController on landing), then re-run `ledge`/`hill`.
- [ ] Headset check:
  - Shaft continues the handle line out of its bottom (`VRClubGripPitch`/`Yaw`/`Roll`, `VRClubButtOffset`; check both hands; see `playtests/2026-10-09-clubfix/NOTES.md`).
  - Rig height snapping comfort.
  - Hit strength with the new fast felt (`VRHitMultiplier`).
- [x] Publish the 2026-10-09 club-mount fix: v12, 20:14 PT 2026-10-09 (File > Publish to Roblox). Audience unchanged (Friends + Playtesters).
- [ ] Re-tune `TouchMaxSpeed` / `TouchPowerCurve` for the faster felt.
- [x] Publish the Team Create draft: v9, ~23:03 PT (File > Publish to Roblox). Audience Limited (Friends + Playtesters); Maturity questionnaire done (Minimal).
- [ ] Real VR headset test (Quest via Roblox app). Check the club angle and friction, then press A to fit the club.
- [ ] Mobile/2D controls pass (stage d: HUD/Explore checked on the iPhone emulator; touch putting strength still untuned).
- [ ] Verify Lighting.Technology = Future (not visible in Studio's Properties panel on this Mac).
- [ ] Before going public: icon and thumbnails, Maturity & Compliance questionnaire, then set Audience to Public (see `.agents/skills/roblox-publishing`).
- [ ] Optionally archive the Plumber copy (10769263747) to avoid two "VR Mini Golf" listings.

## Files
- `design.md`: what the game is and how it plays.
- `src/`: mirror of every Studio script (11 now, incl. the GolfTest harness modules). Studio is the source of truth; `tools/run_playtests.py export` refreshes the mirror, `push` copies edited files into Studio.
- `playtesting.md`: test harness, runner commands, scenarios, club axis assumption, what needs a headset.
- `playtests/<date>/`: harness outputs (summary.md, results.json, jsonl logs; `.mov` clips are gitignored).
- `walkabout-reference.md`: Walkabout Mini Golf physics/UX reference numbers used for tuning.
- `from-claude-session/`: material from the original Claude Code session (MacBook Pro, Claude desktop "No folder" scratch session "Roblox VR mini golf game"):
  - `CourseBuilder.scratch.lua`: an earlier draft. The live version is `src/ServerStorage/CourseBuilder.luau`.
  - `session-summary.md`: what was built and the decisions made.


## 2026-10-10 Stage j: published v105
- Preserved stages e+g+h with Save to Roblox and Publish to Roblox first (**v102**). Imported and registered 13 replacement/missing prop FBXs at scale 1, removed the three Round 7 stretch overrides, rebuilt the course, and published **v105**. Studio Version History confirms both versions.
- All 37 H8 dressing placements now present. H9 uses the imported hanging lanterns. Asset IDs and source hashes: `logs/stages/j-imports.json`.
- H7–H9: 20 random shots each, no escapes/stuck/resets/timeouts/nudges, no console errors/warnings. Desktop stroke → Explore → back smoke PASS.
- Creator Dashboard updates blocked: Chrome is MetavrsePlumber and presents Updated Agreements; Chase needs to handle the agreement and switch to MetavrseBuilder. Icon, eight thumbnails, description pending. Access/privacy unchanged.
- Full details: Stage j in `logs/stages/e-report.md`. One Studio window, Edit mode, test flags off.


### Stage k — 2026-10-11
Saved and reopened the exact Lantern Grove description in Studio Basic Info. Icon and thumbnail updates blocked: current Studio redirects image management to Creator Hub, while task requires Studio only. No browser used; name/access/privacy/maturity unchanged. Public API reports content restricted, so description cannot be publicly verified. See ../../logs/stages/e-report.md for Stage k report.

## 2026-10-11 Stage m: published v116
- Front end (title, course picker, settings, how to play, results), personal best (DataStore), crowd reactions on hole-out, pass-through + see-through camera, slope felt texture, H9 Round 8 pendulum, all lanterns/glow props lit, H8/H9 cream rail trim.
- Saved + published by Codex computer use 2026-10-11 10:50 PT: "Published new changes in "VR Mini Golf" to Roblox." Version History v116. Audience unchanged. Details: logs/stages/e-report.md (Stage m).

## Stage p (2026-10-11, 16:10 PT): VR laser-pointer menus, wrist scoreboard, VR see-through + ball/club X-ray, H9 Round 10. **Published v145**
- **Menus in VR:** point with either controller, pull the trigger to click (beam + dot + hover glow). The thumbstick-click hint is gone. Turn your other wrist up for the score card with MENU / SCORES buttons.
- **See-through:** the camera fade now runs from the VR head too. The ball (and the VR putter head) get an always-on-top outline when something hides them.
- **H9:** pendulum ±11°, block rate 19/48 (39.6%), 0 traps.
- **Tests:** camprobe 0 bad, 90-shot sweep clean, smoke desktop/phone/VR sim PASS. Report: `logs/stages/e-report.md` (Stage p).

## Stage ae — 2026-10-12, local only
PASS: Aurora H2 cup clearance 2.25, 54/54 Aurora cupdrops; Sugarloaf batch 1+2 visuals and exact H8 floors, 33/33 affected-hole cupdrops, 88 random + 30 slow shots, zero escapes/unrecovered stuck balls. H8 settling median 0.518 s over 12 shots; no >1.5 s flags. H11 phase corrected through generator overrides and measured near 0/5.5/5.8/10.4/10.7 s. Two successful pinned recoveries (H6/H9).
Local files: playtest-aurora-v2.rbxl; playtest/playtest-sc-batch12.rbxl. Studio closed. No cloud edits/publishing, no git push. Lobby keeps our VR controls under VR/SimulateVR. See logs/stages/ae-notes.md and playtests/stage-ae/result.json for evidence and retained limits.

## Stage af — 2026-10-12, local batch3+4
Saved `playtest/playtest-sc-batch34.rbxl`; Studio closed. Imported all 12 landmarks, 51 meshes / 7,828 triangles, no missing manifest items. Exact H7–H18 felt/wall/collider audit passes. Reversed ae H11 gate inversion to match holes.json: offsets -1.3 / 0 / 0 at cycle phases 2 / 8 / 10.3; deck rides while gate is closed.
36/36 cupdrops, 96 random shots, 24 slow rollers; zero console warnings/errors, escapes or lost balls. RESULT=FAIL: three H15 wedged shots remain, and Studio automatically created 51 RenderMesh assets despite Upload to Roblox unchecked. No place publication, cloud place edits, or git push. H15 drift bases are partly hidden by existing terrain. Portability report and full evidence: `logs/stages/af-notes.md`, `logs/stages/af-portability.md`, `playtests/stage-af/result.json`.


## Stage ai — 2026-10-13, local Aurora v4

Saved `playtest/playtest-aurora-v4.rbxl`; Studio closed. LOCAL ONLY: no cloud place opened/saved, no publish or git push. Imported all 74 approved props (188 meshes, 65,088 triangles; zero missing); regenerated current Aurora data including H4 ice decel_scale=0.7, which scales both constant and speed-dependent rolling drag per supporting piece. All visual meshes remain non-colliding/non-queryable/non-touchable at runtime.

Result PARTIAL for clearance: 46 conservative built prop bounds findings across 13 props and two visible coplanar candidates remain; source checker reports 12 real findings. Gameplay passes: cupdrop54/54, 144 random shots,36 mover slow rollers, H4 crawl15=0/12, stuck 0, escapes 0, H17 sync324/324, zero console errors. Full evidence and caveats: `logs/stages/ai-notes.md`, `playtests/stage-ai/`.


## Stage al — 2026-10-13, local Sugarloaf fix2

Saved `playtest/playtest-sc-fix2.rbxl`; Studio closed. H14 dock imported, ore/pump placeholders removed while signs remain, and all 387 rail-top coplanar pairs resolved through idempotent visual-only offsets. Physical collider geometry unchanged. H15 friction 0.1/weight 100 is explicitly a TEST setting and persists through rebuilds.

PARTIAL: paired 80-shot H15 experiment gives wedges 26→26, crawls 38→39, native timeouts 26→33 (timeouts overlap crawls). Full sweep: cupdrop 54/54, 144 random + 30 slow, stuck 0, escapes 0, one H15 native timeout; zero console warnings/errors. Local only, no cloud place open/save or publish, no git push. Details: `logs/stages/al-notes.md`, `playtests/stage-al/`.


## Stage zf2 (Oct 13, 2026) — partial
Aurora published **v4**, verified in Version History; visual separation 3290 → 1451 raw hits, 0 exposed planar; colliders unchanged; 54 cup drops/36 shots, clean console. Local copy `playtest/playtest-aurora_archipelago-v4.rbxl`. Both corrected H6/H18 props imported. Lantern Grove remains published **v9**, saved **v11**, not modified: cloud-launch/wrong-place preflight failed. Lobby remains published **v251**, but unintended brief native opening produced saved-unpublished **v252** without source/geometry edits or a Save/Publish command. Sugarloaf remains published **v23**, saved **v24**. See `logs/stages/zf2-notes.md`. No push.
