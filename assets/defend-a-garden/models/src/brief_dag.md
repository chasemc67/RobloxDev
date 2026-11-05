You are on a Mac Mini. Another bot runs Roblox Studio here: do NOT touch Studio/Roblox. Keep it light: one Blender process at a time, background mode only.
Working dir: ~/3dmb/dag. Blender: /Applications/Blender.app/Contents/MacOS/Blender
Run exactly these two commands, sequentially, from ~/3dmb/dag, logging output:
1) "$B" -b --factory-startup --python-exit-code 1 --python build_dag.py -- dag_geom.json out dag_palette.png > build.log 2>&1
2) "$B" -b --factory-startup --python-exit-code 1 --python render_dag.py -- prev out/*/*.fbx > render.log 2>&1
If a step fails, read the log, make the smallest fix to the script (do not change geometry), and rerun that step. Do not change export axes.
Finally make sure no Blender process is left (pkill -x Blender only if one of ours remains), write a short report to report.txt (exit codes, files produced, any fixes), and create the file DONE.
