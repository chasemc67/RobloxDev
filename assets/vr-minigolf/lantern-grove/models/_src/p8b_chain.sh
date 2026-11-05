#!/bin/bash
cd /workspace/RobloxDev/assets/vr-minigolf/lantern-grove/models
while pgrep -f "Follow _src/brief_pass8.md exactly" >/dev/null; do sleep 30; done
CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 /home/box/.local/bin/claude -p "Follow _src/brief_pass8.md, including the Pass 8 addendum at the end. Resume from _src/pass8_progress.md; do not redo finished steps. Work autonomously to completion." --model claude-opus-5-5 --dangerously-skip-permissions --add-dir /workspace/RobloxDev > _src/claude_pass8b.log 2>&1
