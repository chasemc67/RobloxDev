import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from pass5_checks import run
run(os.path.dirname(os.path.dirname(__file__)),fit=False)
