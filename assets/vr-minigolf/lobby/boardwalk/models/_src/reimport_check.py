import os,sys
SRC=os.path.dirname(__file__);sys.path.insert(0,SRC)
from pass3_checks import run
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
root=args[0] if args else os.path.dirname(SRC)
run(root,kit='--kit' in args)
