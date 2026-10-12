#!/bin/zsh
~/bin/unlock-keychain.sh
cd ~/src/RobloxDev
claude -p --model claude-opus-5-5 --dangerously-skip-permissions "$(cat games/vr-mini-golf/logs/stages/v-prompt.md)" > games/vr-mini-golf/logs/stages/v.md 2>&1
echo EXIT=$? >> games/vr-mini-golf/logs/stages/v.md
