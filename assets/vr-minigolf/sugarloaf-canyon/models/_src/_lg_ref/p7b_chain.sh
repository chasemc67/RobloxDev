#!/bin/bash
cd /workspace/RobloxDev/assets/vr-minigolf/lantern-grove/models
while pgrep -f "brief_pass7.md" >/dev/null; do sleep 30; done
/home/box/.local/bin/claude -p "Follow _src/brief_pass7b.md exactly. Work autonomously to completion." --model opus --dangerously-skip-permissions --add-dir /workspace/RobloxDev/assets/vr-minigolf/lantern-grove > _src/claude_pass7b.log 2>&1
