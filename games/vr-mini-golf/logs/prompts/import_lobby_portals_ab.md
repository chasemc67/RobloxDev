Use the cua_repl computer-use MCP on this Mac. Roblox Studio is open with ONE place, "VR Mini Golf" (place 87725688219952, the lobby), in Edit mode. Another agent edits this place through the Studio MCP; it is paused while you work. You are only doing UI clicks: do not change anything else in the place, do not run scripts, and do not save or publish. Do not open any other place.

Task: import this 1 FBX file with Studio's 3D Importer, ONE AT A TIME (the file picker refuses multi-select):
- /Users/chase-mini/src/RobloxDev/assets/vr-mini-golf/lobby/boardwalk/models/fbx_merged/lobby_portals_pass10.fbx  (31 groups, 55 meshes)

For each file:
1. Bring Roblox Studio to the front. Make sure it is in Edit mode (if a playtest is running, stop it with the Stop button). Open the importer: File menu > Import 3D (or the Home/Model tab's "Import 3D" button).
2. In the macOS file picker press Cmd+Shift+G, type the absolute path above, press Return, then click Open.
3. In the 3D Importer window apply the saved preset "LG Stud Scene Anchored" if it exists (each new preview resets to Studio Default, so reapply it for every file), and make sure of these settings where present: keep the hierarchy as separate parts; Scale Unit / Unit = Stud (scale factor 1); Merge Meshes = OFF; Insert Using Scene Position = ON; Set Pivot to Scene Origin = ON; Anchored = ON; Upload to Roblox = ON; Import as Package = OFF; Creator = Me (MetavrseBuilder); Add to Workspace = ON; Import Only as a Model = ON; World Forward = Front, World Up = Top. Keep embedded textures ON if the option exists.
4. Click Import. These files have hundreds of meshes, so the upload can take 5-15 minutes each. Wait until it finishes (the import queue shows a green check) and a Model named like the file (e.g. lobby_portals_pass10) appears in Workspace. If a dialog asks to allow uploading assets, accept it. If anything asks for payment, Robux or verification, cancel it and report it verbatim.
5. Move on to the next file. If one file fails twice, skip it and report the error verbatim.

Finally report, for each file: the inserted model name, its direct child count if visible, any warnings/errors shown by the importer (verbatim). Keep the report under 30 lines.
