#!/usr/bin/env python3
"""Round 8 H9 pendulum sweeps: build a variant (build_holes.py knobs), then the in-engine test line at several speeds
(timing_check --studio-h9), the sim golfer's intended line (24 phases), the swing-vs-felt clearance and optionally
the fuzz + full plays.

    python3 tools/sweep_r8.py '{"h9_piv_x": 21.2}' ... [--speeds 6.5 7 7.75 8.5 9] [--full] [--n 2000] [--fuzz 20000]
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
    ap.add_argument("--speeds", type=float, nargs="*", default=[6.5, 7.0, 7.75, 8.5, 9.0])
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
        st = TC.studio_h9(course, a.speeds)
        bl = [r["counts"]["blocked"] / r["n"] for r in st]
        tr = S7.timing(course, 9, a.fuzz)[0]
        c = tr["counts"]
        out = (f"{json.dumps(var)}: gap min {lo['min_gap']:.3f} rest {lo['gap_at_rest']:.3f} | studio blocked "
               + " ".join(f"{r['speed']:g}:{100 * b:.0f}%" for r, b in zip(st, bl))
               + f" (mean {100 * sum(bl) / len(bl):.0f}%, traps {sum(r['counts']['trap'] for r in st)}) | intended v{tr['speed']} b{c['blocked']} d{c['deflected']} "
                 f"p{c['passed']} t{c['trap']}" + (f" fuzzTO {tr['fuzz']['timeouts']}" if tr.get("fuzz", {}).get("n") else ""))
        if a.full:
            out += " || " + SW.fmt(SW.evaluate(hole, a.n, True))
        print(out, flush=True)


if __name__ == "__main__":
    main()
