"""After user Blender builds: fitcheck both batches, finalize, and make sheet. No Blender launcher."""
import sys

def main():
    import subprocess,sys
    from pathlib import Path
    S=Path(__file__).resolve().parent
    for relative in ['props_batch1/fitcheck_batch1.py','props_batch3/fitcheck_batch3.py','props_batch1/finalize_polish_corals.py','props_batch3/finalize_batch3.py','make_polish_sheet.py']:
        subprocess.run([sys.executable,str(S/relative)],cwd=S,check=True)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
