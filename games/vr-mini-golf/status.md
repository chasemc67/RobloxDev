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

## TODO
- [ ] Real VR headset test (Quest via Roblox app). Check the club angle and friction, then press A to fit the club.
- [ ] Mobile/2D controls pass.
- [ ] Before going public: icon and thumbnails, Maturity & Compliance questionnaire, then set Audience to Public (see `.agents/skills/roblox-publishing`).
- [ ] Optionally archive the Plumber copy (10769263747) to avoid two "VR Mini Golf" listings.

## Files
- `design.md`: what the game is and how it plays.
- `src/`: **read-only snapshot** of the 9 Studio scripts, exported from the place file with Lune (`roblox.deserializePlace`). Studio is still the source of truth (no Rojo sync). Re-export after big changes.
- `from-claude-session/`: material from the original Claude Code session (MacBook Pro, Claude desktop "No folder" scratch session "Roblox VR mini golf game"):
  - `CourseBuilder.scratch.lua`: an earlier draft. The live version is `src/ServerStorage/CourseBuilder.luau`.
  - `session-summary.md`: what was built and the decisions made.
