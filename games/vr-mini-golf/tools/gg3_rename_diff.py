"""Stage gg3: compare an LG inventory against gg2's v51 inventory with the goose renamed (Hole19 -> Hole10,
tee_sign_h19 -> tee_sign_h10). Identical = the renumber moved nothing (every compared key of every part, colliders too).
  PYTHONPATH=tools python3 tools/gg3_rename_diff.py GG2.json GG3.json OUT.json
"""
import json
import sys
from pathlib import Path

import gg3_stage  # noqa: F401  (sets FX1_ROLE / GOLF_STUDIO for fx1_stage)
import fx1_stage
import sc5_stage


def renamed(d):
    def fix(p):
        return p.replace('Workspace.Course.Hole19', 'Workspace.Course.Hole10').replace('tee_sign_h19', 'tee_sign_h10')
    return {**d, 'parts': [{**p, 'path': fix(p['path'])} for p in d['parts']]}


a, b, out = sys.argv[1:4]
x = renamed(json.loads(Path(a).read_text()))
y = json.loads(Path(b).read_text())
tmp = Path('/tmp/gg3/_a.json')
tmp.parent.mkdir(exist_ok=True)
tmp.write_text(json.dumps(x))
r = fx1_stage.compare(tmp, b, out)
cols = 'same' if sc5_stage.canon(x['parts']) == sc5_stage.canon(y['parts']) else 'DIFF'
print(json.dumps({'identical': r['identical'], 'changed': r['changedCount'], 'onlyA': r['onlyACount'], 'onlyB': r['onlyBCount'],
                  'colliders': cols, 'colliderCount': len(sc5_stage.canon(y['parts']))}))
