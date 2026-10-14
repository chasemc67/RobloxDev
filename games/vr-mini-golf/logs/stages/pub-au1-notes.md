# Stage pub-au1 — Aurora Archipelago

Chase approved the new course on Oct 13, 2026. No PC use; no git push.

## Preflight and baselines
- No other active stage job and Studio stopped at entry. Screenshot verified MetavrseBuilder sign-in.
- Creator Hub published-only histories: lobby 248, Lantern Grove 9, Sugarloaf Canyon 21.
- Universe 10769274294; exactly one new place created via Studio Publish As > VR Mini Golf > Add as a new place.
- New place 79649062523043 renamed in Creator Hub to exactly Aurora Archipelago before final overwrite.
- Aurora access matches Sugarloaf: 50 visitors, automatic social slots, Fully Open. Start place remains lobby.

## Source and assets
- Places mapping, playable card, 18 holes / par 53, LoadingAurora, live arch trigger and surface enabled. Par and holes verified against AuroraArchipelago data and CourseAurora.
- CardAuroraPlay: rbxassetid://80814432024313, from store/ui/card_soon_auroraarchipelago_color_clean.png.
- LoadingAurora: rbxassetid://136331763963238, from ui/loading-cards/aurora_loading_card.png. Both uploaded via Studio MCP upload_image.
- Existing shared TeleportScreen selects Config.Courses.loading, so Aurora follows LG/SC loading behavior.
- Smoke harness extended for Aurora role/folder and lobby card/arch checks. Initial smoke hit old lobby-only fallback; corrected role dispatch and reran.
- Local config/manifest/course totals and Python compilation passed; git diff --check passed. No standalone Luau executable found; Luau executed in Studio smoke.

## Aurora
- Opened playtest/playtest-aurora-v5.rbxl, confirmed CourseAurora and PlaceRole=aurora_archipelago. Pushed all src scripts.
- PASS desktop smoke: H1 arrival 0.06 studs from tee, menu closed, one top-right Menu; menu and finished-round lobby requests; real H1 putt moved 7.6 studs, strokes 0→1; zero server/client console errors or warnings.
- Selected exact Aurora Archipelago row in Publish As and overwrote only that row. Creator Hub published-only newest version: 3.
- Evidence: pub-au1-aurora-v3.png; copy: playtest/playtest-aurora_archipelago-v3.rbxl.

## Lobby
- Opened cloud lobby alone; verified place 87725688219952, PlaceRole=lobby, PlaceVersion=248 before pushing.
- Pushed all src scripts and ran LobbyBuilder.BuildPortals in Edit, creating all three arch triggers; Aurora is at (65, 5, 6032).
- PASS expanded desktop smoke: all three menu cards and walk-in arch portals requested the correct place IDs and loading art; zero console errors/warnings. Lobby movement/menu and leaderboard checks passed.
- Aurora menu request: MetavrseBuilder|aurora_archipelago|menu|79649062523043.
- Aurora arch request: MetavrseBuilder|aurora_archipelago|portal|79649062523043.
- Both used aurora_archipelago|rbxassetid://136331763963238; loading screen dismissed after Studio skipped teleport.
- Published to its own place through File > Publish to Roblox. Creator Hub published-only newest version: 249.
- Evidence: pub-au1-lobby-v249.png; copy: playtest/playtest-lobby-v249.rbxl.
- Initial copy download was interrupted by normal shutdown. Reopened only the lobby, confirmed PlaceVersion=249 and persisted Aurora portal, downloaded copy successfully, verified it exists, then closed Studio normally.
- Final published-only recheck: Lantern Grove=9 and Sugarloaf Canyon=21 unchanged. Place 135374506016678 never opened or modified.
- Live cross-place travel itself cannot run in Studio; actual headset join/teleport remains a live-game check.


## Machine cleanup
- Aurora shutdown hung on Applying script changes after verified publish and local copy. Did not press Escape; TERM then KILL used per runbook before opening lobby.


## Deliverables and handoff
- Aurora: `playtest/playtest-aurora_archipelago-v3.rbxl`.
- Lobby: `playtest/playtest-lobby-v249.rbxl`.
- Test in the live experience: Aurora card and arch → Aurora H1, putt, Menu > Back to Lobby. New loading art should display during the trip.
- Only stage source, manifest/runbook, test harness, asset mapping, requested loading PNG, and stage evidence are staged. Other assets and .rbxl files are excluded. No git push.

RESULT=PASS AURORA_ID=79649062523043 AU_NEW=3 LOBBY_OLD=248 LOBBY_NEW=249 LG=9 SC=21 CARD=80814432024313 LOADING=136331763963238
