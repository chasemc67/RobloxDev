Use computer use (cua_repl) on this Mac. Only touch the Roblox Studio window for "VR Mini Golf" (place 87725688219952, already open in Edit mode). Don't touch any other app or window, don't relaunch Studio, and don't open any other place. Don't change anything in the place itself.

Steps:
1. Make sure Studio is in Edit mode (not playing). In Studio, click File > Save to Roblox. Wait until it finishes and confirm no error dialog.
2. Click File > Publish to Roblox. Wait until it finishes. If a dialog asks for confirmation, confirm the publish to the EXISTING experience "VR Mini Golf" (never "create new").
3. Open Version History (File > Version History, or Window > Version History, whichever this Studio version has). Read the newest version number and whether it is marked Published. Close the Version History window.
4. Save a local copy: File > Save to File As (this Studio version may call it "Download a Copy"), saving to exactly /Users/chase-mini/src/RobloxDev/games/vr-mini-golf/playtest-vNNN.rbxl where NNN is the newest version number from step 3 (e.g. playtest-v203.rbxl). Overwrite if asked. Afterwards make sure Studio is still on the live place (title shows VR Mini Golf, not the .rbxl file name). If the title switched to the local file, reopen the live place with: open "roblox-studio:1+launchmode:edit+task:EditPlace+placeId:87725688219952+universeId:10769274294" (only if needed) and close the local-file window without saving.
5. Run: stat -f 'SAVED_BYTES=%z' /Users/chase-mini/src/RobloxDev/games/vr-mini-golf/playtest-vNNN.rbxl

Finally print these lines exactly:
SAVE_TO_ROBLOX=OK|FAIL
PUBLISH=OK|FAIL
LIVE_VERSION=vNNN (Published yes/no)
SAVED_FILE=<path> SAVED_BYTES=<n>
STUDIO_TITLE=<window title at the end>
