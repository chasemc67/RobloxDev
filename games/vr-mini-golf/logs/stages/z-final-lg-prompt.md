You are doing UI clicks only on Chase's Mac Mini (computer use). Do not edit files, do not run Roblox code, do not start a playtest.
Allowed: the Roblox Studio window for the place "Lantern Grove" (place ID 91438142503824; the window title may show "Lantern Grove" or an older default name) and Studio dialogs it opens.
Never publish to or overwrite "VR Mini Golf" (87725688219952) or "Sugarloaf Canyon" (124440050576723).

1. Bring the Lantern Grove Studio window to the front.
2. File > "Save to Roblox" (wait for it to finish).
3. File > "Publish to Roblox" (NOT "Publish As"; this publishes Lantern Grove to itself). Wait until it finishes.
4. Open the Version History for this place (Asset Manager: right-click "Lantern Grove" > View Version History, or File > Version History). Read the newest version number and whether it is marked Published, and the row below it. Close the dialog.
5. File > "Save to File As..." and save to exactly: /Users/chase-mini/src/RobloxDev/games/vr-mini-golf/playtest-lg-v<N>.rbxl where <N> is the newest version number from step 4 (e.g. playtest-lg-v3.rbxl). Replace if it exists. After saving a local copy, Studio may keep editing the cloud place or switch to the file; either is fine.
6. Do NOT quit Studio. Never press Escape on an "Applying script changes" dialog.

Report the version numbers and the saved file path.
End with: LG_RESULT=OK VERSION=<N> FILE=<path>   or   LG_RESULT=FAIL <reason>
