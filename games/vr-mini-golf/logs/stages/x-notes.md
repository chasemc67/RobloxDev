# Stage x notes
- 08:57 PT start: Studio closed; opening live place 87725688219952 via roblox-studio URL.
- 08:58 PT: Studio up, MCP lists exactly one studio, dbe6b3f5 'VR Mini Golf (placeId: 87725688219952)', Edit, PlaceId 87725688219952 / GameId 10769274294.

## Cause
Three things together put every fresh join on Lantern Grove hole 1, and none of them ever pointed at the lobby:
1. **The only SpawnLocation is on Lantern Grove's Welcome Plaza beside hole 1.** workspace.SpawnLocation (Enabled, Neutral, no Teams, not inside Course/CourseSugarloaf) sat at (206, 24.1, 214), facing hole 1. CourseBuilder.Build puts it there on every course build ("spawn beside hole 1's tee": layout.spawn = Welcome Plaza). The lobby (workspace.Lobby, 6000 studs north at z ~6100) only has `LobbySpawn`, an invisible, non-colliding marker Part whose Note says "not a SpawnLocation until the lobby is wired in". No script teleports anyone there; nothing in the game links to it.
2. **GolfServer defaults every player onto Lantern Grove on join.** onPlayerAdded set `st.course = Courses.DEFAULT` and the `Course` attribute to "lantern_grove", parked the ball on LG hole 1's tee, and onReady (GolfMain fires Ready right after start) called startHole(1). So a round was already running on LG H1 when the player arrived. (Stage w's SelectCourse only switched courses; there was no "no course yet" state.)
3. **The client follows that round.** TouchControls' camera and VRControls' rig follow the ball (VR warps you beside it on BallPlaced), and the front end treated the H1 tee as a round in progress (title showed Resume). So the player saw LG hole 1 with no lobby. No PlayerAdded/CharacterAdded PivotTo was involved: the character PivotTo calls are TouchControls.standBesideBall, VRControls' rig and Explore, all driven by the ball/round.

## Fix (09:00-09:05 PT)
- workspace.SpawnLocation moved onto Lobby.LobbySpawn (-10, -0.5, 6100; top flush with the deck at y 0, facing north). Still invisible, Enabled, Neutral. CourseBuilder.Build now places the spawn on LobbySpawn when the lobby exists (else the old Welcome Plaza / H1 spot), so a course rebuild doesn't move it back. LobbySpawn's Note + the LobbyBuilder header comment updated.
- GolfServer: a real player who joins outside the Studio harness has no course (`st.course = nil`, no `Course` attribute). The ball is parked anchored and hidden (Transparency 1) on the LobbySpawn deck; Ready only records `st.ready` and sends BallPlaced(lobby spot, "lobby", 1) so the flat camera and the VR rig frame the lobby. SelectCourse from the lobby starts the round on that course's hole 1 (ball visible again). RequestReset ignores players with no round yet. GolfTestMode keeps the old default (Lantern Grove, started on Ready) so the harness is unchanged.
- FrontEnd: `inLobby()` = no Course attribute. In the lobby there is no Resume and no Explore on the title (Play / Settings / How to play), and the course card's Play always sends SelectCourse (picking Lantern Grove from the lobby would otherwise just close the menu, since Courses.of() falls back to lantern_grove).

## Tests
- Smoke (`run_playtests.py smoke`, desktop, normal play): new lobby check (smoke_lobby): on join the character is inside the Lobby bounds (-10, 3, 6100), Course = nil, ball parked anchored on the lobby spot, menu open on the title page, no Resume/Explore. Then the real course-card PlayCourse buttons (GuiService selection + Return; virtual mouse clicks stopped reaching the game this session): Lantern Grove from the lobby -> LG H1 (ball 0.06 from the tee, character 3.43), Sugarloaf -> SL H1 (0.06 / 3.43), Lantern Grove -> LG H1 (0.06 / 3.43), menu closed, ball unanchored and visible. Then the existing stroke -> Explore -> back flow PASS (strokes 1 -> 1, ball moved 0.000). Console 0 server / 0 client errors or warnings. Output: playtests/stage-x/smoke-desktop.txt.
- LG 9-hole regression (progress, SimulateVR, test mode): 9/9 sunk, ball 0 from each next tee, VR rig 1.5, HUD titles, course complete + final scorecard; 0/0 console. playtests/stage-x/lg-regression/.
- Extra: SimulateVR normal join: rig 3.3 studs from the lobby spawn, camera 5.6, menu panel 4.0 in front of the head on the title page; Sugarloaf pick -> ball 0.06 from SL H1 tee, camera 5.5 from the ball; 0 client problems. SimulateVR/GolfTestMode cleared afterwards.
- `run_playtests.py export`: src/ mirrors Studio (only GolfServer, FrontEnd, CourseBuilder, LobbyBuilder changed).

## Not changed / limits
- The lobby is still a menu backdrop: you spawn and stand there (frozen like on the course; VR can walk with the left stick if the menu is closed), but the arch/portals/course board are still decorative (lobby integration ticket). There is no "back to lobby" button after picking a course; the menu's Play switches courses.
- Tools that relied on a round starting on join without GolfTestMode (ui_shots/menu_shots golf-HUD shots, SkipMenu runs) now start in the lobby and need a SelectCourse first.

## Publish (09:10-09:25 PT)
- The Homebrew Codex CLI (/opt/homebrew/bin/codex 0.153.4) hung with 0 CPU (even `--version`), so tools/codex_ui.sh never started; that run was killed. The same prompt (logs/stages/x-publish-prompt.md) ran with the ChatGPT.app bundled CLI (/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex 0.160.1), clicks only: File > Save to Roblox OK, File > Publish to Roblox OK. Version History newest = **v239, marked Published**; the row below is v238 (9:09 AM auto-save; v236-v238 are this session's auto-saves), so live is above v235. File > Save to File As -> games/vr-mini-golf/playtest-v239.rbxl (3,835,620 bytes, gitignored). Log: logs/stages/x-publish.log.
- After: MCP lists one Studio, 'VR Mini Golf (placeId: 87725688219952)', Edit mode, title "VR Mini Golf - Roblox Studio".

RESULT=PASS
LIVE_VERSION=v239
