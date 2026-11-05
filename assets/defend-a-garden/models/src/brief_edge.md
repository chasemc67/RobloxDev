You are on a Windows PC. Playtest Bot may be using Roblox Studio here: do NOT touch Studio. One Blender process at a time, background mode only. Run Blender from PowerShell (not Git Bash) with exact paths.
$B = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"; work dir C:\Users\chase\sc_fix\edge
1) & $B -b --factory-startup --python-exit-code 1 --python C:\Users\chase\sc_fix\edge\build_edge.py -- C:\Users\chase\sc_fix\edge\edge_geom.json C:\Users\chase\sc_fix\edge\out C:\Users\chase\sc_fix\edge\edge_palette.png *> C:\Users\chase\sc_fix\edge\build.log
2) & $B -b --factory-startup --python-exit-code 1 --python C:\Users\chase\sc_fix\edge\render_edge.py -- C:\Users\chase\sc_fix\edge *> C:\Users\chase\sc_fix\edge\render.log
If a step fails, read the log, make the smallest script fix (never change geometry, layout or export axes) and rerun that step. Workbench only, keep it light.
Confirm no blender.exe is left running. Write report.txt (exit codes, files, fixes) and create the file DONE in the work dir.
