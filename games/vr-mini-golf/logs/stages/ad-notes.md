# Stage ad — lobby VR path (local test only)

Scope: `playtest-lobby-v247.rbxl` opened via File > Open from File and immediately saved via Save to File As to `playtest-lobby-ad.rbxl`. No cloud place opened/saved, no publishing, no new Roblox place, no git push. RBXL files are not committed.

Preflight: no competing stage process; Studio welcome screenshot confirmed MetavrseBuilder. Exactly one Studio place. MCP Edit inspection: PlaceRole=lobby, PlaceId=0, GameId=0, no NetworkClient. Studio's MCP label retained the original filename after Save As; the native window title and save confirmation showed the ad file's full local path.

Changes:
- GolfMain checks UIS/VRService before the lobby branch, including the existing one-second startup wait (now checks both services throughout). Real VR and SimulateVR initialize HUD, VRControls, and FrontEnd's VR path. Desktop keeps LobbyRoam and its existing menu/TeleportScreen wiring.
- An inert lobby adapter supplies canHit=false, no hole/ball/strokes, no-op reset, and placement/teleport signals without loading BallController or waiting for a course.
- VR starts at the lobby character's spawn, with default walking disabled; VRControls still moves the replicated character for portal touches.
- Wrist shows LOBBY/VR Mini Golf and dashes for absent golf stats.
- LobbyServer initializes the existing ClubSetup handler. The first exploratory run exposed its missing remote as an infinite-yield warning; this was fixed before the clean verification run.

Validation uses Studio SimulateVR and VRDebug Head/Hands/Button/Stick, plus existing GolfPointerDebug poses and laser targeting. No physical headset was available/tested.
- Both wrists under each handedness: Left 2/2 and Right 2/2, visible alpha=1 and lobby text.
- VRPutter exists; no ball and no strokes.
- Left stick moved the character 6.61 studs; right stick changed view direction 14.87 degrees (initial simulated head pose was pitched down).
- Both ButtonB and ButtonY opened scorecard. Laser clicked SettingsButton gear; Settings included ClubSetup; Back returned to title and Close worked.
- Left-stick walk through Lantern Grove and Sugarloaf arches requested place IDs 91438142503824 and 124440050576723 with reason=portal. Both emitted TeleportStatus start/skipped; no real teleport.
- Final VR client/server logs: zero warnings/errors.

Evidence: `playtests/stage-ad/result.json`, `vr-test.txt`, `portals-test.txt`, `desktop-smoke.txt`, `push.txt`, and local screenshots `wrist-lobby-visible.jpg` / `settings-visible.jpg`. Screenshot binaries remain local, outside the commit.

Desktop `python3 tools/run_playtests.py smoke`: PASS, including course cards, loading-screen cycle, both portal arches, leaderboard and 0 console errors/warnings. Final four source equality checks passed. SimulateVR=false; Edit PlaceId/GameId=0 and no NetworkClient rechecked. File > Save to File confirmed the local ad path; Studio quit and process absence verified.

RESULT=PASS LOBBY_RBXL=games/vr-mini-golf/playtest-lobby-ad.rbxl WRIST=L2/2,R2/2 PUTTER=pass STICKS=pass SCORECARD_GEAR=pass DESKTOP_SMOKE=pass
