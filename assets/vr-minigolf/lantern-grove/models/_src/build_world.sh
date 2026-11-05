#!/usr/bin/env bash
# Pass 3: world-scale background pieces. Layout -> FBX/previews/manifest -> fit check -> vistas -> docs.
# Usage: models/_src/build_world.sh [--no-vista]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
BLENDER="${BLENDER:-/home/box/.local/bin/blender}"
python3 "$HERE/textures.py" >/dev/null
python3 "$HERE/world_layout.py"
"$BLENDER" -b --factory-startup -P "$HERE/world_build.py" 2>&1 | grep -E '^\[|Error|Traceback' || true
"$BLENDER" -b --factory-startup -P "$HERE/world_fitcheck.py" 2>&1 | grep -E 'PASS|FAIL|Error' || true
if [ "${1:-}" != "--no-vista" ]; then
  "$BLENDER" -b --factory-startup -P "$HERE/world_vista.py" 2>&1 | grep -E '^\[|Error|Traceback' || true
fi
python3 "$HERE/world_docs.py"
python3 "$HERE/make_docs.py"
