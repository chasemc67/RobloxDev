You are on a Windows PC. Playtest Bot may be using Roblox Studio here: do NOT touch Studio. One Blender process at a time, background mode only. Run Blender from PowerShell (not Git Bash) with exact paths.
$B = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"; work dir C:\Users\chase\sc_fix\edge2 (fbx_edge\ already holds the approved v1 FBXs; do not modify them)
1) & $B -b --factory-startup --python-exit-code 1 --python C:\Users\chase\sc_fix\edge2\build_edge.py -- C:\Users\chase\sc_fix\edge2\edge_geom_v2.json C:\Users\chase\sc_fix\edge2\fbx_edge_v2 C:\Users\chase\sc_fix\edge2\edge_palette_v2.png *> C:\Users\chase\sc_fix\edge2\build.log
2) & $B -b --factory-startup --python-exit-code 1 --python C:\Users\chase\sc_fix\edge2\render_edge_v2.py -- C:\Users\chase\sc_fix\edge2 *> C:\Users\chase\sc_fix\edge2\render.log
If a step fails, read the log, make the smallest script fix (never change geometry, layout, colours or export axes) and rerun that step. Workbench only.
Confirm no blender.exe is left running. Write report.txt (exit codes, files, fixes) and create the file DONE in the work dir.
