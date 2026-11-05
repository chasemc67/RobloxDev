You are on a Windows PC. Playtest Bot may be using Roblox Studio here: do NOT touch Studio or any node/roblox process. One Blender process at a time, background mode only. Run Blender from PowerShell (not Git Bash) with exact paths.
$B = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"; work dir C:\Users\chase\sc_fix\kit1
1) & $B -b --factory-startup --python-exit-code 1 --python C:\Users\chase\sc_fix\kit1\build_kit.py -- C:\Users\chase\sc_fix\kit1\geom C:\Users\chase\sc_fix\kit1\fbx C:\Users\chase\sc_fix\kit1\kit_palette.png *> C:\Users\chase\sc_fix\kit1\build.log
2) & $B -b --factory-startup --python-exit-code 1 --python C:\Users\chase\sc_fix\kit1\render_kit.py -- C:\Users\chase\sc_fix\kit1 *> C:\Users\chase\sc_fix\kit1\render.log
Step 1 builds all kit meshes (one FBX each, kit_*.fbx + palette png). Step 2 renders 3q_<mesh>.png x22, lineup_trees.png, lineup_ground.png, lineup_backdrop.png and dump.json into prev\.
If a step fails, read the log, make the smallest script fix (never change geometry, colours, or export axes) and rerun that step. Workbench only.
Confirm no blender.exe is left running. Write report.txt (exit codes, files, fixes) and create the file DONE in the work dir.
