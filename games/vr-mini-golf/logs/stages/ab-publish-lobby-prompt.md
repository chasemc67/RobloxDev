You are doing UI clicks only on Chase's Mac Mini (computer use). Do not edit files, do not run Roblox code, do not start a playtest.
Allowed: the Roblox Studio window for the place "VR Mini Golf" (place ID 87725688219952, the lobby and start place) and Studio dialogs it opens.
Never publish to or overwrite "Lantern Grove" (91438142503824) or "Sugarloaf Canyon" (124440050576723).

1. Bring the VR Mini Golf Studio window to the front. Studio is in Edit mode (confirmed through the Studio MCP just now). This is a Team Create place, so a NetworkClient in the Explorer is normal in Edit mode and does NOT mean a playtest. Only if the window title or toolbar clearly shows a running playtest (the viewport has a "Client"/"Server" label and the Stop button is red), click Stop once and continue.
2. File > "Save to Roblox" (wait for it to finish).
3. File > "Publish to Roblox" (NOT "Publish As"; this publishes VR Mini Golf to itself). Wait until it finishes and read the confirmation text (and a version number if one is shown). The last published version was 244.
4. Open Version History (File > Version History, or the place's Version History in Studio) and read the newest row: its version number, date/time and whether it is marked Published. Close the dialog without clicking Restore or Revert.
5. Then quit Roblox Studio (Cmd+Q); if asked to save, choose Save. Do not save to a local file. Never press Escape on an "Applying script changes" dialog. If the quit hangs for more than 2 minutes on "Applying script changes", stop and report it (do not force anything).

End with: LOBBY_RESULT=OK <confirmation text / version> VH=<newest row: version, time, Published yes/no>   or   LOBBY_RESULT=FAIL <reason>
