# Stage y notes
Chase on v239: "When the game launches it has the menu with no explore button and I can only pick a course and get dropped in it. The menu should be not-full-screen so I can also tell I'm in the lobby, and I should be able to close that menu so I can walk around the lobby. And then on mobile I should get a button somewhere re-open the menu if I closed it."

- 09:25 PT start: MCP lists one Studio, dbe6b3f5 'VR Mini Golf (placeId: 87725688219952)', Edit. Studio scripts matched src/ byte for byte (stage x export).

## Changes (client only)
- **FrontEnd: a windowed menu.** The full-screen GolfMenuBg ScreenGui (title art + navy wash) is gone. The 900x520 panel now has its own background (title art under a navy wash, rounded, amber rim; the same as the VR panel already had), centred and scaled to about 62% of the screen (desktop 1080p ≈ 1120x650). On short screens (safe area under 400 px tall, i.e. phone landscape) it uses 92% of the height so buttons stay finger-sized. Measured: Studio window 829x499 → 0.57x0.54 of the viewport; iPhone 17 Pro emulation 750x381 → 0.68x0.77, lobby visible at the sides. Results page: plain navy panel (VR: no panel art, as before).
- **Close (X)** in the panel's top-right corner on every page except the results (they have their own buttons). Works with mouse, touch, gamepad selection and the VR laser.
- **Menu button**: new ScreenGui GolfMenuButton, a 104x50 amber "Menu" button in the Roblox top bar row, just right of Roblox's own buttons (GuiService.TopbarInset; falls back to under the top bar at the left edge). Shown whenever the menu is closed (lobby and on a course; the HUD's top-right Menu button is still there on a course). **M** toggles the menu on desktop (not over the results). VR: clicking the left stick (ButtonL3) already toggles the menu and the wrist card has MENU; both unchanged. The title footer says how to close/reopen.
- **New GolfClient.LobbyRoam** (phone/desktop): while there is no `Course` attribute, `Ball.lobbyRoam` is true, so `Ball.exploring()` is true and TouchControls stands down (camera + input). Default Roblox camera (Custom, subject = humanoid). Menu closed: PlayerModule controls enabled, StarterPlayer walk speed (16) and jump (JumpHeight 7.2), AutoRotate, touch thumbstick + jump button on. Menu open: standing still (controls off, speed 0) under the windowed menu. On a course pick it hands back to the golf controls (frozen, Scriptable camera; TouchControls stands the character beside the ball). GolfMain's freeze and Explore.applyCharacter skip while lobbyRoam is on, so a respawn in the lobby keeps walking.
- The golf HUD stays hidden in the lobby (no hole/ball yet); it shows once Course is set.
- The ball stays hidden and anchored on the lobby spot (server unchanged).
- VR: locomotion already worked with the menu closed (VRControls' left stick only stops while Ball.menuOpen). The trigger no longer warps you to the hidden lobby ball when no course is picked.
- Files: FrontEnd, LobbyRoam (new), BallController (exploring()), Explore, GolfMain, VRControls. tools/run_playtests.py smoke extended.

## Tests
- `run_playtests.py smoke` (desktop, normal play) — new smoke_lobby_roam step: panel 0.57x0.54 of the viewport, no GolfMenuBg backdrop, CloseMenu present. Real X button (GuiService selection + Return) → menu closed, Menu button shown, camera Custom, WalkSpeed 16, jump 7.2, HRP not anchored, ball hidden, golf HUD hidden, no course. Real W key held 2 s → **moved 32.0 studs**. Menu button (selection + Return) → menu open on title, walk speed 0. M closes, M reopens. Then the stage x picks (LG / Sugarloaf / LG, ball 0.06 / char 3.43 from each H1 tee) and stroke → Explore → back (strokes 1 → 1, ball moved 0.000). **Console 0 server / 0 client errors or warnings.** playtests/stage-y/smoke-desktop.txt
- Same smoke under iPhone 17 Pro emulation (`--device iphone_17_pro`): all PASS, TouchEnabled, 0/0 console. Screenshot check: thumbstick + jump button + Menu button with the menu closed; courses and how-to pages fit, X and Back don't overlap anything. playtests/stage-y/smoke-phone.txt
- LG 9-hole regression (`run progress`, SimulateVR, test mode): **9/9 sunk**, ball 0 from each next tee, VR rig 1.5, HUD titles, course complete + final scorecard; 0/0 console. playtests/stage-y/lg-regression/
- SimulateVR normal join: SurfaceGui menu on the title with the X; close → menu closed, reopen → title; 0 client problems. SimulateVR / GolfTestMode cleared afterwards.
- `run_playtests.py export`: src/ mirrors Studio (only the files above changed, LobbyRoam added).

## Not changed / limits
- VR left-stick walking in the lobby wasn't driven in a test (no virtual thumbstick); its code path is unchanged and only blocked while the menu is open.
- On a course, both the new top-left Menu button and the HUD's top-right Menu button show.
- The lobby portals/course board are still decorative; courses are picked from the menu.

## Publish (09:41-09:44 PT)
- Codex computer use (ChatGPT.app bundled CLI, prompt logs/stages/y-publish-prompt.md): File > Save to Roblox OK, File > Publish to Roblox OK. Version History newest = **v241, Published**; row below is v240 (9:37 AM auto-save). Local copy: games/vr-mini-golf/playtest-v241.rbxl (3,837,166 bytes, gitignored). Log: logs/stages/y-publish.log.
- After: MCP lists one Studio, 'VR Mini Golf (placeId: 87725688219952)', Edit mode, LobbyRoam present.

RESULT=PASS
LIVE_VERSION=v241
