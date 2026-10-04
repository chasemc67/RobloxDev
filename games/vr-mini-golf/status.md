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

## 2026-10-03 ~23:00 PT: VR playtest fixes (Studio Team Create draft, NOT published)
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

## TODO
- [ ] Headset check: club comes out of the controller tip along the pointing axis (`VRClubTipOffset`, `VRClubAngle`); rig height snapping comfort; hit strength with the new fast felt (`VRHitMultiplier`).
- [ ] Re-tune `TouchMaxSpeed` / `TouchPowerCurve` for the faster felt.
- [ ] Publish the Team Create draft (orchestrator).
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
