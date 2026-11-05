"""One Blender process: generate, export only four snowpuffs, then read-only closeups."""
import sys,runpy,os,traceback
from pathlib import Path
S=Path(__file__).resolve().parent
sys.path.insert(0,str(S));sys.path.insert(0,str(S.parent))
from polish_guard import start_guard
VERIFY=start_guard()
IDS='h04_snowpuffs,h06_snowpuffs,h14_snowpuffs,h18_snowpuffs'
if __name__=='__main__':
    try:
        runpy.run_path(str(S/'gen_batch3.py'),run_name='__main__')
        sys.argv=['build_batch3.py','--','--only',IDS,'--export-only']
        build=runpy.run_path(str(S/'build_batch3.py'))
        try:build['main']()
        except SystemExit as exc:
            if exc.code not in (None,0):raise
        sys.argv=['polish2_blender.py','--','--closeup-only']
        runpy.run_path(str(S/'polish2_blender.py'),run_name='__main__')
        VERIFY()
    except BaseException:
        traceback.print_exc()
        try:
            VERIFY()
        finally:
            sys.stdout.flush();sys.stderr.flush();os._exit(1)
