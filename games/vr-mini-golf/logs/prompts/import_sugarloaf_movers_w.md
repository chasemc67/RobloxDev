Use the cua_repl computer-use MCP on this Mac. Roblox Studio is open with the place "VR Mini Golf" (place 87725688219952) in Edit mode. Another agent edits this place through the Studio MCP; it is paused while you work. You are only doing UI clicks: do not change anything else in the place, do not run scripts, and do not save or publish.

Task: import ONE FBX file with Studio's 3D Importer:
- /Users/chase-mini/src/RobloxDev/assets/vr-mini-golf/sugarloaf-canyon/models/fbx/movers_merged/sugarloaf_movers_pass5.fbx

Steps:
1. Bring Roblox Studio to the front. Make sure it is in Edit mode (if a playtest is running, stop it with the Stop button). Keep only one Studio window. Open the importer: File menu > Import 3D (or the Home/Model tab's "Import 3D" button).
2. In the macOS file picker press Cmd+Shift+G, type the absolute path above, press Return, then click Open.
3. In the 3D Importer window apply the saved preset "LG Stud Scene Anchored" if it exists, and make sure of these settings where present: keep the hierarchy as separate parts; Scale Unit / Unit = Stud (scale factor 1); Merge Meshes = OFF; Insert Using Scene Position = ON; Set Pivot to Scene Origin = ON; Anchored = ON; Upload to Roblox = ON; Import as Package = OFF; Creator = Me (MetavrseBuilder); Add to Workspace = ON; Import Only as a Model = ON; World Forward = Front, World Up = Top. Keep embedded textures ON if the option exists.
4. Click Import. The file has 35 groups and 93 meshes, so the upload can take several minutes. Wait until it finishes and a Model named like the file (sugarloaf_movers_pass5) appears in Workspace. If a dialog asks to allow uploading assets, accept it. If anything asks for payment, Robux or verification, cancel it and report it verbatim.
5. If the import fails, retry once. If it fails twice, report the error verbatim.

Finally report: the inserted model name, its child count, mesh part count, any warnings/errors shown by the importer. Keep the report under 30 lines.
