#!/bin/bash
# usage: tools/codex_ui.sh <logname> <prompt file>
# Runs a Codex computer-use task (Studio UI: 3D Importer, Save/Publish) and logs to logs/<logname>.log.
export PATH=$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH
LOG=$HOME/src/RobloxDev/games/vr-mini-golf/logs/$1.log
codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "$(cat "$2")" </dev/null > "$LOG" 2>&1
echo EXIT_CODE=$? >> "$LOG"
tail -30 "$LOG"
