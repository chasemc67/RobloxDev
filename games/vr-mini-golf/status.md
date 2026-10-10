# VR Mini Golf: status

## Where it lives
| | Owner | Universe | Root place | URL |
|---|---|---|---|---|
| **Current (use this)** | MetavrseBuilder (user 1818120139) | 10769274294 | 87725688219952 | https://www.roblox.com/games/87725688219952 |
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

## 2026-10-09 ~20:00 PT: VR club runs parallel to the controller handle (not published)
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
- The changes are in the Team Create draft. **Not published** (Chase publishes).

## TODO
- [ ] Felt bounce: ~0.6 elasticity for landings faster than ~1.5 studs/s (e.g. in BallController on landing), then re-run `ledge`/`hill`.
- [ ] Headset check:
  - Shaft continues the handle line out of its bottom (`VRClubGripPitch`/`Yaw`/`Roll`, `VRClubButtOffset`; check both hands; see `playtests/2026-10-09-clubfix/NOTES.md`).
  - Rig height snapping comfort.
  - Hit strength with the new fast felt (`VRHitMultiplier`).
- [ ] Publish the 2026-10-09 club-mount fix (Chase).
- [ ] Re-tune `TouchMaxSpeed` / `TouchPowerCurve` for the faster felt.
- [x] Publish the Team Create draft: v9, ~23:03 PT (File > Publish to Roblox). Audience Limited (Friends + Playtesters); Maturity questionnaire done (Minimal).
- [ ] Real VR headset test (Quest via Roblox app). Check the club angle and friction, then press A to fit the club.
- [ ] Mobile/2D controls pass.
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
