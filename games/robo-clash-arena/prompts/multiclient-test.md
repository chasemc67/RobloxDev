Use the cua_repl computer-use MCP on this Mac (plus the Roblox_Studio MCP for console output if useful). Roblox Studio is open with the place "Robo Clash Arena" in Edit mode. Goal: verify real 2-human matchmaking using Studio's multi-client test. Do NOT edit any scripts or instances in the place.

Steps:
1. In Studio, open the Test tab (ribbon). Find "Clients and Servers" (a Start/Local Server option with a player count dropdown). Set it to 2 players and click Start. Studio will open a Server window and two client windows (Player1, Player2). Wait for them to load (~20-40 s).
2. In Player1's window: click through the title screen (click PLAY or press Enter), on Robot Select pick BOLT (or any) and confirm, then on Mode Select click MATCHMAKING. Screenshot.
3. In Player2's window: same, but pick CRUSHER, then MATCHMAKING.
4. Verify both clients enter the same match: cube drop-in, READY 3-2-1 LAUNCH!, both robots visible in the arena, HUD shows both players' HP. Screenshot both windows.
5. In one client window, play a bit: hold W/A/D to move, click left mouse to fire the gun, right-click for bomb, press E for pod, Space jump, Shift dash, for ~20 seconds, aiming to damage the other player. Check the other window shows HP dropping. Screenshot.
6. Close Player2's client window (or its Leave) and check Player1 gets "OPPONENT LEFT"/win and a results screen.
7. Gather errors: look at the Output window in the Server and client windows (or use the Roblox_Studio MCP get_console_output) and copy any red error lines or warnings from game scripts.
8. Stop the test (Test tab > Cleanup / Stop) so Studio returns to Edit mode, and close the extra windows. Make sure the original Edit window of the place is still open.
Save screenshots you take as PNGs under ~/src/RobloxDev/games/robo-clash-arena/logs/screens/ (mc-*.png) if the tool allows saving.

Report concisely: whether pairing worked, whether hits/HP synced, whether leave handling worked, exact error lines, and any visual/UX problems you noticed (UI overlap, camera, readability).
