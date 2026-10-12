#!/bin/zsh
sleep $(( $(date -j -f "%H:%M" "00:09" +%s) - $(date +%s) > 0 ? $(date -j -f "%H:%M" "00:09" +%s) - $(date +%s) : 0 ))
~/bin/unlock-keychain.sh
cd ~/src/RobloxDev
claude -p --model claude-opus-5-5 --dangerously-skip-permissions "$(cat games/vr-mini-golf/logs/stages/u-prompt.md)" > games/vr-mini-golf/logs/stages/u.md 2>&1
echo EXIT=$? >> games/vr-mini-golf/logs/stages/u.md
