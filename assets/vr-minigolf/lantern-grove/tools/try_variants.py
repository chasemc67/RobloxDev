#!/usr/bin/env python3
"""Dev tool: try text-replacement variants of build_holes.py on one hole; restores the original afterwards.
usage (python): try_variants(hole_num, [(label, [(old, new), ...]), ...], n=1000)"""
import subprocess, os
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "build_holes.py")

def try_variants(num, variants, n=1000):
    orig = open(P).read()
    try:
        for label, reps in variants:
            s = orig
            for a, b in reps:
                assert a in s, (label, a[:60]); s = s.replace(a, b)
            open(P, "w").write(s)
            subprocess.run(["python3", P], capture_output=True, check=True)
            r = subprocess.run(["python3", os.path.join(HERE, "sim.py"), "--holes", str(num), "--n", str(n), "--tag", "scratch"],
                               capture_output=True, text=True).stdout
            lines = [l for l in r.splitlines() if l.startswith(f"H{num}") or "ERROR" in l]
            print(f"[{label}]", " / ".join(l[:260] for l in lines), flush=True)
    finally:
        open(P, "w").write(orig)
        subprocess.run(["python3", P], capture_output=True)
