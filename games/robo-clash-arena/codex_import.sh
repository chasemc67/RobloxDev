#!/bin/bash
# usage: codex_import.sh <logname> <abs fbx path> [<abs fbx path> ...]
# Drives Roblox Studio's Import 3D dialog via Codex computer use. Log: logs/<logname>.log
export PATH=$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH
NAME=$1; shift
LOG=$HOME/src/RobloxDev/games/robo-clash-arena/logs/$NAME.log
FILES=""
for f in "$@"; do FILES="$FILES
- $f"; done
PROMPT="Use the cua_repl computer-use MCP on this Mac. Roblox Studio is open with the place 'Robo Clash Arena' in Edit mode (another agent edits it via MCP; do not change anything else in the place, do not save or publish).
Task: import these FBX files with Studio's 3D importer, one at a time:$FILES

For each file:
1. Bring Roblox Studio to the front. Make sure it is in Edit mode (not playtesting). Open the importer: File menu > Import 3D (or the Home/Model/Avatar tab's 'Import 3D' button).
2. In the macOS file picker press Cmd+Shift+G, type the absolute path above, press Return, then click Open (or press Return again).
3. In the 3D Importer window: keep the hierarchy as separate parts. If these settings exist, set them: Scale Unit / Unit = Stud (1 unit = 1 stud); Merge Meshes = OFF; Insert Using Scene Position = ON; Set Pivot to Scene Origin = ON; Anchored = ON; leave World Forward/Up at defaults (Front / Top). Note any warnings shown and the reported triangle count / size if visible.
4. Click Import (bottom right). Wait until the import finishes and a Model appears in the Explorer under Workspace (uploading meshes can take up to a minute or two). If a dialog asks to allow uploading/publishing assets or to confirm, accept it.
5. Report the exact name of the inserted Model in Workspace.

Finally report, for every file: the inserted model name, the importer settings you saw (all option names and their values), any warnings/errors, and anything unusual. Keep the report short (under 25 lines)."
codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "$PROMPT" </dev/null > "$LOG" 2>&1
echo EXIT_CODE=$? >> "$LOG"
tail -40 "$LOG"
