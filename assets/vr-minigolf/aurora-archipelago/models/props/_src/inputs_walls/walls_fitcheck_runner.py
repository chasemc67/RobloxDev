# Round 4 'walls' fitcheck: the out_props/_src/fitcheck.py (H11 lintel expectation 1.27; incl. fitcheck_decor.py vs AA_BLOCKOUT and
# fitcheck_clear.py), outputs redirected to AA_QA_OUT as fitcheck_<AA_QA_TAG>.txt / fitcheck_report_<AA_QA_TAG>.json / fitcheck_<AA_QA_TAG>_validated.txt
#   AA_BLOCKOUT=out_p2g/models/blockout AA_QA_OUT=out_props AA_QA_TAG=walls blender -b --factory-startup -P walls_fitcheck_runner.py
import os
from pathlib import Path
p = Path(__file__).resolve().parent / 'out_props/_src/fitcheck.py'
src = p.read_text(encoding='utf8')
T = os.environ["AA_QA_TAG"]
for a, b in (('open(os.path.join(OUT, "fitcheck_p1props.txt"), "w")', f'open(os.path.join(os.environ["AA_QA_OUT"], "fitcheck_{T}.txt"), "w")'),
             ('open(os.path.join(OUT, "fitcheck_report.json"), "w")', f'open(os.path.join(os.environ["AA_QA_OUT"], "fitcheck_report_{T}.json"), "w")'),
             ('open(os.path.join(OUT, "fitcheck_p1props_validated.txt"), "w")', f'open(os.path.join(os.environ["AA_QA_OUT"], "fitcheck_{T}_validated.txt"), "w")')):
    assert src.count(a) == 1, a
    src = src.replace(a, b)
__file__ = str(p)
exec(compile(src, str(p), 'exec'))
