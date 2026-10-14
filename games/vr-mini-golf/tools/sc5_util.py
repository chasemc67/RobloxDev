"""Stage sc5 helpers: Studio session on the open Sugarloaf Canyon place + chunked _G string fetch.
  PYTHONPATH=tools python3 tools/sc5_util.py fetch _G.Var out.json      (fetch a _G JSON string)
  PYTHONPATH=tools python3 tools/sc5_util.py run file.luau [out.json]   (run Luau that sets _G.SC5Out, returns its length)
"""
import json, os, sys
from pathlib import Path
os.environ.setdefault('GOLF_STUDIO', '124440050576723')
from run_playtests import Studio
GAME = Path(__file__).resolve().parents[1]
OUT = GAME / 'playtests/stage-sc5'

def studio():
    s = Studio(); assert s.mode()[0] == 'Edit', 'not in Edit'
    assert s.luau('return workspace:GetAttribute("PlaceRole")') == 'sugarloaf_canyon'
    return s

def fetch(s, var, code=None, timeout=600):
    n = int(s.luau(code, timeout=timeout)) if code else int(s.luau('return #' + var))
    return ''.join(json.loads(s.luau('return game.HttpService:JSONEncode(%s:sub(%d,%d))' % (var, i + 1, i + 40000)))
                   for i in range(0, n, 40000))

if __name__ == '__main__':
    s = studio()
    if sys.argv[1] == 'fetch':
        raw = fetch(s, sys.argv[2]); Path(sys.argv[3]).write_text(raw + '\n'); print(len(raw))
    elif sys.argv[1] == 'run':
        raw = fetch(s, '_G.SC5Out', Path(sys.argv[2]).read_text())
        if len(sys.argv) > 3: Path(sys.argv[3]).write_text(raw + '\n')
        print(raw[:3000])
