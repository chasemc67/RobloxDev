#!/usr/bin/env python3
"""Round 7 sweeps: like sweep_r5.py, plus the timing-obstacle check (tools/timing_check.py) for the hole's obstacle.

    python3 tools/sweep_r7.py 7 '{"h7_dwell": [1.0, 1.5]}' [--timing-only] [--n 2000] [--no-hio] [--fuzz 20000]
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sweep_r5 as SW
import timing_check as TC


def timing(course, hole_no, nfuzz):
    obs = [o for o in TC.OBSTACLES if o["hole"] == hole_no]
    saved = TC.OBSTACLES[:]
    TC.OBSTACLES[:] = obs
    try:
        return TC.run(course, 24, nfuzz)
    finally:
        TC.OBSTACLES[:] = saved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hole", type=int)
    ap.add_argument("variants", nargs="+")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--no-hio", action="store_true")
    ap.add_argument("--timing-only", action="store_true")
    ap.add_argument("--fuzz", type=int, default=20000)
    a = ap.parse_args()
    for v in a.variants:
        var = json.loads(v)
        course = SW.build(var)
        tr = timing(course, a.hole, a.fuzz)
        ts = "; ".join(f"{r['line']}: block {r['block_pct']:g}% pass {r['pass_pct']:g}% trap {r['trap']} bot3 {'/'.join(c[0] for c in r['bot3'])}"
                       + (f" fuzzTO {r['fuzz']['timeouts']}" if r.get('fuzz') else "") for r in tr)
        out = f"H{a.hole} {json.dumps(var)}: T {tr[0]['period']}s | {ts}"
        if not a.timing_only:
            out += " || " + SW.fmt(SW.evaluate(course["holes"][a.hole - 1], a.n, not a.no_hio))
        print(out, flush=True)


if __name__ == "__main__":
    main()
