#!/usr/bin/env bash
# Rebuild every Lantern Grove prop (textures, FBX, previews, manifest, .blend), the per-hole dressing layouts,
# run fit checks, write docs/contact sheets.
# Usage: models/_src/build.sh [--only a,b] [--no-render] [--assembly]
#   --assembly also renders previews/assembly_hNN_{tee,top}.png over the real world (about 12 extra minutes)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
BLENDER="${BLENDER:-/home/box/.local/bin/blender}"
ARGS=(); ASM=0
for a in "$@"; do if [ "$a" = "--assembly" ]; then ASM=1; else ARGS+=("$a"); fi; done
python3 "$HERE/textures.py"
"$BLENDER" -b --factory-startup -P "$HERE/build_all.py" -- "${ARGS[@]}" 2>&1 | grep -E '^\[|Error|Traceback|line [0-9]+' || true
# pass 4: world re-placement of the frozen pass-2 seed (dressing_seed_pass2.json). dressing.py (the pass-2 hole-local
# generator) is NOT run: it would overwrite manifest.dressing with the old flat layout.
"$BLENDER" -b --factory-startup -P "$HERE/dressing_world.py" 2>&1 | grep -E '^\[dw\] H|Error|Traceback|line [0-9]+' || true
"$BLENDER" -b --factory-startup -P "$HERE/fitcheck.py" 2>&1 | grep -E 'PASS|FAIL|Error' || true
if [ "$ASM" = 1 ]; then
  "$BLENDER" -b --factory-startup -P "$HERE/assembly_world.py" 2>&1 | grep -E '^\[|Error|Traceback' || true
fi
python3 "$HERE/make_docs.py"
python3 "$HERE/tee_sheet.py"
