# Stage pub-sc3 — Sugarloaf fix2 publish attempt

RESULT=FAIL DIALOG. No publish occurred.

Preflight found no competing stage job and no Studio application process (StudioMCP bridge helpers only). Launched Studio and visually confirmed “Welcome, MetavrseBuilder”. Opened only `playtest/playtest-sc-fix2.rbxl` through File > Open from File. MCP confirmed one Studio, Edit mode, PlaceId/GameId 0, workspace PlaceRole=sugarloaf_canyon, and Workspace.CourseSugarloaf.

Before publication, Creator Hub Version History for place 124440050576723, with Show published only checked, showed live version 19. The newest saved version was 20, unpublished. Lantern Grove baseline: live 9, newest saved 11. Lobby baseline: live/newest 248.

Ran the requested full source push successfully, then `python3 tools/run_playtests.py smoke` (exit 0). Result: PASS sugarloaf_canyon smoke (desktop), zero server/client console errors or warnings. Real H1 putt moved 7.39 studs and added one stroke; course arrival, menu and finish return-to-lobby requests passed. Logs: `pub-sc3-push.log` and `pub-sc3-smoke.log`.

Confirmed all five al2 HintImage decals in CourseSugarloaf: H9 sign_bypass 107264623944550; H9 felt_arrow_bypass 123495746026639; H14 safe_bank_sign 131067632603421; H14 safe_bank_arrow 82085948994874; H14 timing_arrow 139894260913924.

File > Publish to Roblox As displayed My Experiences. Selected existing VR Mini Golf, then selected the existing Sugarloaf Canyon radio row. The chooser displayed the Sugarloaf Canyon name but no numeric place ID or creator identity. The user's instruction requires the exact place/ID to be clear in the dialog, otherwise cancel. Clicked Cancel; never clicked Overwrite. No new place or experience was created.

Refreshed all three Creator Hub histories after cancellation. Published versions remain Sugarloaf 19, Lantern Grove 9, lobby 248. Saved-version maxima remain 20, 11, 248 respectively. These were read-only browser checks; neither protected place was opened in Studio or modified. Place 135374506016678 was not accessed.

Quit Studio, choosing Don't Save for the temporary source push. The original approved fix2 file remains unchanged. No version-named RBXL was created because no new version was published. No asset fetch/import/upload, git push, or RBXL commit occurred. Source/tools had no local changes; only this stage note is committed. Failure commit wording records the actual outcome rather than claiming a publish.

Final: SC_OLD=19 SC_NEW=19 LG=9 LOBBY=248 RBXL=playtest/playtest-sc-fix2.rbxl (existing input, not a new published snapshot).
