#!/usr/bin/env python3
"""Dev tool: quick parameter sweeps on a hole (edits an in-memory copy of holes.json)."""
import copy, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim as S

def run(hole, n=1000, seed=11):
    ha = S.HoleArrays(hole)
    g = S.run_plays(ha, "good", n, seed); a = S.run_plays(ha, "average", n, seed + 1)
    return f"good {g['avg']:.2f} hio {g['hio']*100:.1f}% cap {g['capped']*100:.1f}% | avg {a['avg']:.2f} hio {a['hio']*100:.1f}% cap {a['capped']*100:.1f}%"

def variants(num, muts):
    course = json.load(open(os.path.join(S.ROOT, "holes.json")))
    base = course["holes"][num - 1]
    for label, fn in muts:
        h = copy.deepcopy(base); fn(h); print(f"H{num} {label}: {run(h)}")


def run_full(hole, n=1000, seed=11):
    """with brute-force ace search, so the good golfer's ace attempts use this variant's best line"""
    ha = S.HoleArrays(hole)
    hio = S.hio_search(ha)
    ln = hio.get("line")
    g = S.run_plays(ha, "good", n, seed, ace_line=ln); a = S.run_plays(ha, "average", n, seed + 1)
    return (f"lines {hio['hits'] or hio.get('refine_hits', 0)} | good {g['avg']:.2f} hio {g['hio']*100:.1f}% cap {g['capped']*100:.1f}% | "
            f"avg {a['avg']:.2f} hio {a['hio']*100:.1f}% cap {a['capped']*100:.1f}%")


def variants_full(num, muts):
    course = json.load(open(os.path.join(S.ROOT, "holes.json")))
    base = course["holes"][num - 1]
    for label, fn in muts:
        h = copy.deepcopy(base); fn(h); print(f"H{num} {label}: {run_full(h)}", flush=True)
