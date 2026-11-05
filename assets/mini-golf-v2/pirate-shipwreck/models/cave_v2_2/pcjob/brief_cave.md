You are on a Windows PC. Playtest Bot may be using Roblox Studio here: do NOT touch Studio or any node/roblox process. One Blender process at a time, background mode only. Run Blender from PowerShell (not Git Bash) with exact paths.
$B = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"; work dir C:\Users\chase\sc_fix\cave22
1) & $B -b --factory-startup --python-exit-code 1 --python C:\Users\chase\sc_fix\cave22\build_cave.py -- C:\Users\chase\sc_fix\cave22\geom C:\Users\chase\sc_fix\cave22\fbx C:\Users\chase\sc_fix\cave22\cave_palette.png *> C:\Users\chase\sc_fix\cave22\build.log
2) & $B -b --factory-startup --python-exit-code 1 --python C:\Users\chase\sc_fix\cave22\render_cave.py -- C:\Users\chase\sc_fix\cave22 3q,front,mouth_closeup,tunnel_depth *> C:\Users\chase\sc_fix\cave22\render.log
Step 1 builds all six parts (geom has all six JSONs). Step 2 renders only 3q, front, mouth_closeup, tunnel_depth.
If a step fails, read the log, make the smallest script fix (never change geometry, colours, or export axes) and rerun that step. Workbench only.
Confirm no blender.exe is left running. Write report.txt (exit codes, files, fixes) and create the file DONE in the work dir.
