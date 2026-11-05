#!/bin/bash
# usage: mkjob.sh <dirname> <taskname>   (packages pcjob/ and launches the detached schtask on the PC)
set -e;D=$1;T=$2;cd "$(dirname "$0")";rm -rf pcjob;mkdir -p pcjob/geom pcjob/fbx
cp work/geom/prop_cannon.json work/geom/prop_coconut.json pcjob/geom/;cp prop_flytrap.fbx prop_croc.fbx prop_captain.fbx prop_flytrap.png prop_croc.png prop_captain.png pcjob/fbx/;cp src/build_props.py src/render_props.py work/props_palette.png pcjob/
cat > pcjob/brief_props.md <<EOT
You are on a Windows PC. Playtest Bot may be using Roblox Studio here: do NOT touch Studio or any node/roblox process. One Blender process at a time, background mode only. Run Blender from PowerShell (not Git Bash) with exact paths.
\$B = "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe"; work dir C:\\Users\\chase\\sc_fix\\$D
1) & \$B -b --factory-startup --python-exit-code 1 --python C:\\Users\\chase\\sc_fix\\$D\\build_props.py -- C:\\Users\\chase\\sc_fix\\$D\\geom C:\\Users\\chase\\sc_fix\\$D\\fbx C:\\Users\\chase\\sc_fix\\$D\\props_palette.png *> C:\\Users\\chase\\sc_fix\\$D\\build.log
2) & \$B -b --factory-startup --python-exit-code 1 --python C:\\Users\\chase\\sc_fix\\$D\\render_props.py -- C:\\Users\\chase\\sc_fix\\$D *> C:\\Users\\chase\\sc_fix\\$D\\render.log
Step 1 builds two props (prop_cannon, prop_coconut; the other three FBX are already in fbx\\). Step 2 renders 3q_<prop>.png x5, lineup.png and dump.json into prev\\.
If a step fails, read the log, make the smallest script fix (never change geometry, colours, or export axes) and rerun that step. Workbench only.
Confirm no blender.exe is left running. Write report.txt (exit codes, files, fixes) and create the file DONE in the work dir.
EOT
printf 'Set-Location C:\\Users\\chase\\sc_fix\\%s\nGet-Content brief_props.md -Raw | claude -p --model claude-opus-5-5 --dangerously-skip-permissions *> claude.log\n' $D > pcjob/run_props.ps1
ssh pc "tasklist | findstr /i blender; schtasks /query | findstr /i 3dmb; powershell -NoProfile -Command \"Remove-Item -Recurse -Force C:\\Users\\chase\\sc_fix\\$D -ErrorAction SilentlyContinue; New-Item -ItemType Directory -Force C:\\Users\\chase\\sc_fix\\$D | Out-Null\"" || true
scp -r pcjob/* pc:"C:/Users/chase/sc_fix/$D/"
ssh pc "schtasks /create /tn $T /tr \"powershell -NoProfile -ExecutionPolicy Bypass -File C:\\Users\\chase\\sc_fix\\$D\\run_props.ps1\" /sc once /st 23:59 /f; schtasks /run /tn $T"
