#!/bin/bash
# usage: mkjob.sh <dirname> <taskname>   (packages pcjob/ and launches the detached schtask on the PC)
set -e;D=$1;T=$2;cd "$(dirname "$0")";rm -rf pcjob;mkdir -p pcjob/geom pcjob/fbx
cp work/geom/*.json pcjob/geom/;cp src/build_kit22.py src/render_kit22.py work/kit_palette.png pcjob/
for f in ../kit_v2_4/kit_*.fbx;do b=$(basename $f .fbx);[ -f work/geom/$b.json ] || cp $f pcjob/fbx/;done
cp ../kit_v2_6/kit_ruin_wall.fbx pcjob/fbx/kit_ruin_wall_old.fbx
cat > pcjob/brief_kit2.md <<EOT
You are on a Windows PC. Playtest Bot may be using Roblox Studio here: do NOT touch Studio or any node/roblox process. One Blender process at a time, background mode only. Run Blender from PowerShell (not Git Bash) with exact paths.
\$B = "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe"; work dir C:\\Users\\chase\\sc_fix\\$D
1) & \$B -b --factory-startup --python-exit-code 1 --python C:\\Users\\chase\\sc_fix\\$D\\build_kit22.py -- C:\\Users\\chase\\sc_fix\\$D\\geom C:\\Users\\chase\\sc_fix\\$D\\fbx C:\\Users\\chase\\sc_fix\\$D\\kit_palette.png *> C:\\Users\\chase\\sc_fix\\$D\\build.log
2) & \$B -b --factory-startup --python-exit-code 1 --python C:\\Users\\chase\\sc_fix\\$D\\render_kit22.py -- C:\\Users\\chase\\sc_fix\\$D *> C:\\Users\\chase\\sc_fix\\$D\\render.log
Step 1 builds every geom json into one FBX each (main mesh, optional *_Glow mesh, LightAttach empty) plus a palette png. Step 2 renders 3q_<mesh>.png for every FBX, the lineup_*.png images and dump.json into prev\\.
If a step fails, read the log, make the smallest script fix (never change geometry, colours, or export axes) and rerun that step. Workbench only.
Confirm no blender.exe is left running. Write report.txt (exit codes, files, fixes) and create the file DONE in the work dir.
EOT
printf 'Set-Location C:\\Users\\chase\\sc_fix\\%s\nGet-Content brief_kit2.md -Raw | claude -p --model claude-opus-5-5 --dangerously-skip-permissions *> claude.log\n' $D > pcjob/run_kit2.ps1
ssh pc "tasklist | findstr /i blender; schtasks /query | findstr /i 3dmb; powershell -NoProfile -Command \"Remove-Item -Recurse -Force C:\\Users\\chase\\sc_fix\\$D -ErrorAction SilentlyContinue; New-Item -ItemType Directory -Force C:\\Users\\chase\\sc_fix\\$D | Out-Null\"" || true
scp -r pcjob/* pc:"C:/Users/chase/sc_fix/$D/"
ssh pc "schtasks /create /tn $T /tr \"powershell -NoProfile -ExecutionPolicy Bypass -File C:\\Users\\chase\\sc_fix\\$D\\run_kit2.ps1\" /sc once /st 23:59 /f; schtasks /run /tn $T"
