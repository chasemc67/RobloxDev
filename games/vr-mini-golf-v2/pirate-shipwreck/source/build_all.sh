#!/bin/sh
# regenerate everything: data/*, preview/*, import/import_world.luau
set -e
cd "$(dirname "$0")"
python3 make_blockout.py > /dev/null
python3 make_preview.py
python3 make_import.py
