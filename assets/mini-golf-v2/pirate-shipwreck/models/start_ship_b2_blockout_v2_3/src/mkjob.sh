#!/bin/bash
# usage: mkjob.sh <dirname> <taskname>  (packages the job and launches the detached schtask on the PC)
set -e;D=$1;T=$2;cd "$(dirname "$0")/..";rm -rf pcjob;mkdir -p pcjob
cp work/geom.json work/palette.png src/build_ship.py src/render_ship.py pcjob/;mkdir -p pcjob/before;cp ../start_ship_b2_blockout_v2_2/start_ship_b2_visual.fbx pcjob/before/
cat > pcjob/brief.md <<EOT
You are on a Windows PC. Playtest Bot may be using Roblox Studio here: do NOT touch Studio or any node/roblox process. One Blender process at a time, background mode only. Run Blender from PowerShell (not Git Bash) with exact paths.
\$B = "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe"; work dir C:\\Users\\chase\\sc_fix\\$D
1) & \$B -b --factory-startup --python-exit-code 1 --python C:\\Users\\chase\\sc_fix\\$D\\build_ship.py -- C:\\Users\\chase\\sc_fix\\$D *> C:\\Users\\chase\\sc_fix\\$D\\build.log
2) & \$B -b --factory-startup --python-exit-code 1 --python C:\\Users\\chase\\sc_fix\\$D\\render_ship.py -- C:\\Users\\chase\\sc_fix\\$D *> C:\\Users\\chase\\sc_fix\\$D\\render.log
3) & \$B -b --factory-startup --python-exit-code 1 --python C:\\Users\\chase\\sc_fix\\$D\\render_ship.py -- C:\\Users\\chase\\sc_fix\\$D C:\\Users\\chase\\sc_fix\\$D\\before\\start_ship_b2_visual.fbx prev_before *> C:\\Users\\chase\\sc_fix\\$D\\render_before.log
Step 1 builds geom.json into out\\ (visual FBX, collision FBX, three ramp FBXs). Step 2 imports the visual FBX and renders (Workbench, one render at a time) hero_3q.png, side_section_raw.png, plan_raw.png, door_view.png plus dump.json and plan_meta.json plus the *_raw.png preview shots into prev\\.
If a step fails, read the log, make the smallest script fix (never change geometry, colours or export axes) and rerun that step. Step 3 renders the same scene from the OLD v2.2 visual FBX (before\\) into prev_before\\ (only the *_raw.png preview shots matter there). Workbench only.
Confirm no blender.exe is left running. Write report.txt (exit codes, files, fixes) and create the file DONE in the work dir.
EOT
printf 'Set-Location C:\\Users\\chase\\sc_fix\\%s\nGet-Content brief.md -Raw | claude -p --model claude-opus-5-5 --dangerously-skip-permissions *> claude.log\n' $D > pcjob/run.ps1
ssh pc "tasklist | findstr /i blender; schtasks /query | findstr /i 3dmb; powershell -NoProfile -Command \"Remove-Item -Recurse -Force C:\\Users\\chase\\sc_fix\\$D -ErrorAction SilentlyContinue; New-Item -ItemType Directory -Force C:\\Users\\chase\\sc_fix\\$D | Out-Null\"" || true
scp -r pcjob/* pc:"C:/Users/chase/sc_fix/$D/"
ssh pc "schtasks /create /tn $T /tr \"powershell -NoProfile -ExecutionPolicy Bypass -File C:\\Users\\chase\\sc_fix\\$D\\run.ps1\" /sc once /st 23:59 /f; schtasks /run /tn $T"
