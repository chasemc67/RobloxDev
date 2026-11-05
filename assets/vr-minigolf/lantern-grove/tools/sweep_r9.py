#!/usr/bin/env python3
"""Round 9 H9 foot sweep: build a variant (build_holes.py knobs, e.g. {"h9_foot": [1.0, 0.4, 1.6]}), then the in-engine test
line (timing_check --studio-h9) at 24 and 80 phases evenly over one period, swing-vs-felt clearance, and optionally fuzz + full plays.

    python3 tools/sweep_r9.py '{"h9_foot": [1.0, 0.4, 1.6]}' ... [--speeds 7 7.75 8.5 9] [--fuzz 100000] [--full --n 2000]
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim as S
import sweep_r5 as SW
import sweep_r7 as S7
import timing_check as TC


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variants", nargs="+")
    ap.add_argument("--speeds", type=float, nargs="*", default=[7.0, 7.75, 8.5, 9.0])
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--fuzz", type=int, default=0)
    a = ap.parse_args()
    for v in a.variants:
        var = json.loads(v)
        course = SW.build(var)
        hole = course["holes"][8]
        m = next(q for q in hole["moving_parts"] if q["type"] == "swing")
        lo = S.swing_low_points(S.HoleArrays(hole), hole, m)
        out = f"{json.dumps(var)}: gap min {lo['min_gap']:.3f} rest {lo['gap_at_rest']:.3f}"
        for nph in (24, 80):
            st = TC.studio_h9(course, a.speeds, nph=nph)
            out += f" | {nph}ph " + " ".join(f"{r['speed']:g}:{r['counts']['blocked']}" for r in st) + f" t{sum(r['counts']['trap'] for r in st)}"
        tr = S7.timing(course, 9, a.fuzz)[0]
        c = tr["counts"]
        out += (f" | intended b{c['blocked']} d{c['deflected']} p{c['passed']} t{c['trap']}"
                + (f" fuzzTO {tr['fuzz']['timeouts']}" if tr.get("fuzz", {}).get("n") else ""))
        if a.full:
            out += " || " + SW.fmt(SW.evaluate(hole, a.n, True))
        print(out, flush=True)


if __name__ == "__main__":
    main()
