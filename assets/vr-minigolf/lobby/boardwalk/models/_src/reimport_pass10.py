import sys
from pathlib import Path
s=Path(__file__).parent;sys.path.insert(0,str(s))
from pass10_checks import run
run(str(s.parent))
