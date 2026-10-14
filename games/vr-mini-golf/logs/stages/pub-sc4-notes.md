# Stage pub-sc4 — publish Sugarloaf fix2

Published the approved fix2 build to the existing Sugarloaf Canyon place **124440050576723**, universe **10769274294**, owned by **MetavrseBuilder**. No other place was opened or modified in Studio.

## Preflight and baseline

- Read the game AGENTS.md, including Publish and verify and Machine rules.
- No competing `codex exec -m` / `claude -p` stage process; Studio was not running (StudioMCP bridge helpers only).
- Launched one Studio and confirmed the screenshot read “Welcome, MetavrseBuilder”.
- Creator Hub Version History, Show published only: Sugarloaf OLD=19. Its newest saved version was 20, unpublished.
- Protected-place baselines: Lantern Grove published 9 / newest saved 11; VR Mini Golf lobby published/newest 248.

## Input and validation

Opened `playtest/playtest-sc-fix2.rbxl` with File > Open from File. MCP confirmed exactly one place, Edit mode, PlaceId/GameId 0, workspace PlaceRole=`sugarloaf_canyon`, and Workspace.CourseSugarloaf.

Ran `python3 tools/run_playtests.py push $(find src -name '*.luau')` successfully, then `python3 tools/run_playtests.py smoke` (exit 0). Smoke passed Sugarloaf desktop arrival, menu, real H1 putt (6.32 studs, one stroke), and menu/finish return-to-lobby requests. Server/client console errors and warnings: zero. Logs: `pub-sc4-push.log`, `pub-sc4-smoke.log`. Test mode and SimulateVR were false afterward.

Confirmed all five al2 HintImage decals before and after testing:

| Hole | Carrier | Asset ID |
|---|---|---|
| H9 | sign_bypass / SignBoard | 107264623944550 |
| H9 | felt_arrow_bypass | 123495746026639 |
| H14 | safe_bank_sign / SignBoard | 131067632603421 |
| H14 | safe_bank_arrow | 82085948994874 |
| H14 | timing_arrow | 139894260913924 |

## Publish and verification

File > Publish to Roblox As > My Experiences > existing VR Mini Golf > existing row named exactly Sugarloaf Canyon > Overwrite. The chooser showed names only, as approved. Neither the VR Mini Golf nor Lantern Grove place row was selected. No new place or experience was created.

Immediately afterward, Creator Hub at `https://create.roblox.com/dashboard/creations/experiences/10769274294/places/124440050576723/version-history` showed newest version **21**, October 13, 2026 at 8:26 PM local time, with the Published Version checkmark. Show published only also included 21 as the newest row. Evidence: `pub-sc4-published-v21.png`.

Studio automatically reopened the published cloud place; MCP confirmed exactly one Studio, Sugarloaf Canyon (placeId: 124440050576723), universe 10769274294, PlaceVersion 21, PlaceRole sugarloaf_canyon, CourseSugarloaf, and all five hints.

Refreshed both protected Creator Hub histories read-only after publishing: Lantern Grove remains published **9**, newest saved **11**; lobby remains published/newest **248**. Place 135374506016678 was not accessed.

## Local snapshot and cleanup

The cloud-place File menu labels the local-save action **Download a Copy** instead of Save to File As. Used that action to save:

`games/vr-mini-golf/playtest/playtest-sugarloaf_canyon-v21.rbxl`

Size: 3,510,844 bytes. SHA-256: `5c6318c620ac199aed1c9a6c7d1b83cbc6c0827cfabbef55de6b15f8c1096d9f`.

No source/tools changes were needed. No asset fetch/import, git push, or RBXL commit occurred. Unrelated existing workspace changes were left alone.

Verified live versions: SC_OLD=19 SC_NEW=21 LG=9 LOBBY=248.

Studio close stalled on “Applying script changes. Studio will close automatically when complete.” Never pressed Escape. After the verified publish and local save, used the publishing runbook fallback: SIGTERM to this stage's Studio PID 49287, then SIGKILL when it remained open. Verified no Studio application process and no connected Studio afterward.
