#!/usr/bin/env python3
"""Variant sweeps through build_holes.py's tuning knobs (K(...)), without touching holes.json.
Merges Lantern Grove's sweep_r5.py (validator + fuzz + ace search + plays), sweep_r7.py (timing check) and sweep_r10.py (stop/kick split).

    python3 tools/sweep.py 4 '{"h4_cup": [2.0, 0, -36]}' '{"h4_cup": [3.0, 0, -36]}' [--n 2000] [--no-hio] [--timing] [--fuzz 20000]

Each variant is built to a per-process scratch file (SC_OUT; one file per run so parallel sweeps can't corrupt each other) and runs:
validator, 60k-shot escape fuzz, brute-force ace search (the good golfer's ace attempts use that variant's line), N plays per skill and,
with --timing, the timing-obstacle check of that hole (blocked = stops + kicks, Studio estimate = stops + 0.36 kicks, traps, soft-lock fuzz).
"""
import argparse, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim as S

SCRATCH = os.environ.get("SC_SCRATCH") or os.path.join(HERE, "out", f"scratch-holes-{os.getpid()}.json")


def build(var):
    env = dict(os.environ, SC_OUT=SCRATCH, SC_VARIANT=json.dumps(var))
    subprocess.run([sys.executable, os.path.join(HERE, "build_holes.py")], env=env, check=True, capture_output=True)
    return json.load(open(SCRATCH))


def evaluate(hole, n=2000, hio=True, seed=7, fuzz=True):
    issues = [m for sev, m in S.validate(hole) if sev == "ERROR"]
    ha = S.HoleArrays(hole)
    nesc = S.fuzz_escapes(ha)[0] if fuzz else 0
    hs = S.hio_search(ha) if hio else {}
    st = {}
    for k, sk in enumerate(S.SKILLS):
        st[sk] = S.run_plays(ha, sk, n, seed + 101 * hole["number"] + k, ace_line=hs.get("line"))
    return dict(errors=issues, fuzz=nesc, hio=hs, stats=st)


def par_or_better(st, par):
    return sum(st["dist"][:par]) / st["n"]


def fmt(r, par=None):
    g, a = r["stats"]["good"], r["stats"]["average"]
    hs = r["hio"]
    lines = (hs.get("hits") or hs.get("refine_hits", 0)) if hs else "-"
    pob = f" pob {par_or_better(g, par) * 100:.0f}/{par_or_better(a, par) * 100:.0f}%" if par else ""
    return (f"good {g['avg']:.2f} hio {g['hio'] * 100:.1f}% cap {g['capped'] * 100:.1f}% | "
            f"avg {a['avg']:.2f} hio {a['hio'] * 100:.1f}% cap {a['capped'] * 100:.1f}% haz {a['hazard_per_play']:.2f} | "
            f"gap {a['avg'] - g['avg']:+.2f}{pob} | lines {lines} | fuzz {r['fuzz']} | to {g['timeouts'] + a['timeouts']} | "
            f"err {len(r['errors'])}{(' ' + r['errors'][0][:90]) if r['errors'] else ''}")


def timing(course, hole_no, nfuzz, ace_line=None):
    import timing_check as TC
    obs = [o for o in TC.OBSTACLES if o["hole"] == hole_no]
    if not obs:
        return []
    saved = TC.OBSTACLES[:]
    TC.OBSTACLES[:] = obs
    try:
        return TC.run(course, 96, nfuzz, {hole_no: ace_line} if ace_line else None)
    finally:
        TC.OBSTACLES[:] = saved


def fmt_timing(tr):
    out = []
    for r in tr:
        c = r["counts"]
        out.append(f"{r['line']}: T {r['period']}s blk {c['blocked']}({c['stops']}s+{c['kicks']}k) defl {c['deflected']} est {r['est_pct']:g}% "
                   f"trap {r['trap']}" + (f" fuzzTO {r['fuzz']['timeouts']}/{r['fuzz']['n']}" if r.get("fuzz", {}).get("n") else ""))
    return "; ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hole", type=int)
    ap.add_argument("variants", nargs="+")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--no-hio", action="store_true")
    ap.add_argument("--no-fuzz", action="store_true")
    ap.add_argument("--timing", action="store_true")
    ap.add_argument("--timing-only", action="store_true")
    ap.add_argument("--fuzz", type=int, default=20000, help="timing soft-lock fuzz shots")
    a = ap.parse_args()
    for v in a.variants:
        var = json.loads(v)
        course = build(var)
        hole = course["holes"][a.hole - 1]
        out = f"H{a.hole} {json.dumps(var)}: "
        r = None
        if not a.timing_only:
            r = evaluate(hole, a.n, not a.no_hio, fuzz=not a.no_fuzz)
            out += fmt(r, hole["par"])
        if a.timing or a.timing_only:
            out += " || " + fmt_timing(timing(course, a.hole, a.fuzz, (r or {}).get("hio", {}).get("line") if r else None))
        print(out, flush=True)
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)


if __name__ == "__main__":
    main()
