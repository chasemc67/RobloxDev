#!/usr/bin/env python3
"""Round 10 H9 pendulum design sweep with an honest split of the sim's 'blocked' results.

Studio v131 measured 15/48 blocked for a foot the frictionless sim scores 22/48. Tracing the sim shows two kinds of block:
  * stop  = the first contact is a face square to the shot line (velocity change across the contact |nz| >= 0.7: the
            foot's north face). The ball
            meets a flat face head-on and bounces back the way it came. The face only slides sideways past the ball, so it can't
            carry the ball through.
  * kick  = the first contact is a side face or a corner (the swing-facing foot faces, the yaw-30 lantern body's corners dipping
            at 5-10 deg). The moving face shoves the ball sideways, and whether it ends north of the line or carried on through
            depends on contact details the sim can't resolve (the shove-through Studio sees). Coin flip.
Studio estimate = stops + KAPPA * kicks, with KAPPA fitted to v116 (Round 8 foot, 8/24) and v131 (1.0 x 0.4 x 1.6 yaw 0, 15/48).

    python3 tools/sweep_r10.py '{"h9_amp": 9}' ... [--speeds 7 7.75 8.5 9] [--fuzz 100000] [--full --n 2000] [--calib]
Knobs: build_holes.py K(...) names (h9_amp, h9_period, h9_piv_x, h9_foot, h9_foot_yaw, h9_body_collide ...).
"""
import argparse, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim as S
import sweep_r5 as SW
import sweep_r7 as S7
import timing_check as TC

CALIB = [("v116 Round 8 foot", {"h9_foot": [0.8, 0.4, 1.6], "h9_foot_yaw": 30.0, "h9_amp": 13.0, "h9_period": 4.0}, 24, 8),
         ("v131 1.0x0.4x1.6 yaw 0", {"h9_foot": [1.0, 0.4, 1.6], "h9_foot_yaw": 0.0, "h9_amp": 13.0, "h9_period": 4.0}, 48, 15)]
_ghost = TC.ghost_args


def ghost_all_swings(ha, j):
    """ghost = no pendulum at all (the 'h9_pend2' variant has two)"""
    keep = [k for k in range(ha.nMB) if int(ha.MB[k, 0]) != j and ha.MP[int(ha.MB[k, 0]), 0] != 2]
    MB = ha.MB[keep].copy() if keep else np.zeros((1, 16))
    a = list(ha.args())
    a[5] = MB
    a[6] = len(keep)
    return tuple(a)


TC.ghost_args = ghost_all_swings
KAPPA = 0.36  # fitted with --calib: least squares over v116 (8/24) + v131 (15/48) gives 0.359 (see Round 10 in playtest-log.md)


def contact_normal(p, i0):
    """direction of the ball's velocity change across the first contact (recorded path p, first deviating sample i0). For a
    frictionless hit on a moving face the change is along the face normal, so this is the normal of the face that was hit."""
    i0 = max(i0, 2)
    vb = p[i0 - 1] - p[i0 - 2]
    va = p[min(i0 + 2, len(p) - 1)] - p[min(i0 + 1, len(p) - 2)]
    d = (va - vb)[[0, 2]]
    return d / max(np.linalg.norm(d), 1e-9)


def split(course, speeds, nph):
    """studio line at nph phases: per speed counts of stop / kick / deflected / passed / trap"""
    hole = course["holes"][8]
    cfg = TC.OBSTACLES[2]
    ha = S.HoleArrays(hole)
    j = TC.part_index(hole, cfg["part"])
    m = hole["moving_parts"][j]
    PH = S.ph_array()
    dt = 6 * PH[12]
    args, gargs = ha.args(), TC.ghost_args(ha, j)
    st = TC.STUDIO_H9
    aim = math.atan2(st["dir"][1], st["dir"][0])
    out = []
    for v in speeds:
        c = dict(stop=0, kick=0, deflected=0, passed=0, trap=0)
        for q in range(nph):
            t0 = q * m["period_s"] / nph
            cls = TC.classify(ha, cfg, j, args, gargs, PH, st["start"], aim, v, t0)["cls"]
            if cls == "blocked":
                p, _ = TC.shot(args, PH, st["start"], aim, v, t0)
                g, _ = TC.shot(gargs, PH, st["start"], aim, v, t0)
                n = min(len(p), len(g))
                i0 = int(np.argmax(np.linalg.norm(p[:n] - g[:n], axis=1) > 0.02))
                cls = "stop" if abs(contact_normal(p, i0)[1]) >= 0.7 else "kick"
            c[cls] += 1
        c["blocked"] = c["stop"] + c["kick"]
        c["est"] = c["stop"] + KAPPA * c["kick"]
        out.append(dict(speed=v, n=nph, **c))
    return out


def fmt_split(rs):
    return " ".join(f"{r['speed']:g}:{r['blocked']}({r['stop']}s{r['kick']}k)~{100 * r['est'] / r['n']:.0f}%" for r in rs)


def main():
    global KAPPA
    ap = argparse.ArgumentParser()
    ap.add_argument("variants", nargs="*")
    ap.add_argument("--speeds", type=float, nargs="*", default=[7.0, 7.75, 8.5, 9.0])
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--fuzz", type=int, default=0)
    ap.add_argument("--calib", action="store_true", help="fit KAPPA to the two Studio measurements")
    a = ap.parse_args()
    if a.calib:
        rows = []
        for name, var, nph, studio in CALIB:
            r = split(SW.build(var), [7.75], nph)[0]
            rows.append((name, r, studio))
            print(f"{name}: sim blocked {r['blocked']}/{nph} = {r['stop']} stops + {r['kick']} kicks; Studio {studio}/{nph}")
        num = sum((s - r["stop"]) * r["kick"] for _, r, s in rows)
        den = sum(r["kick"] ** 2 for _, r, s in rows)
        KAPPA = num / den
        print(f"least-squares KAPPA = {KAPPA:.3f}: " + ", ".join(f"{n} est {r['stop'] + KAPPA * r['kick']:.1f} vs {s}" for n, r, s in rows))
    for v in a.variants:
        var = json.loads(v)
        course = SW.build(var)
        hole = course["holes"][8]
        m = next(q for q in hole["moving_parts"] if q["type"] == "swing")
        lo = S.swing_low_points(S.HoleArrays(hole), hole, m)
        out = f"{json.dumps(var)}: gap min {lo['min_gap']:.3f} rest {lo['gap_at_rest']:.3f}"
        for nph in (24, 80):
            rs = split(course, a.speeds, nph)
            out += f" | {nph}ph " + fmt_split(rs) + f" t{sum(r['trap'] for r in rs)}"
        tr = S7.timing(course, 9, a.fuzz)[0]
        c = tr["counts"]
        out += (f" | intended b{c['blocked']} d{c['deflected']} p{c['passed']} t{c['trap']}"
                + (f" fuzzTO {tr['fuzz']['timeouts']}" if tr.get("fuzz", {}).get("n") else ""))
        if a.full:
            out += " || " + SW.fmt(SW.evaluate(hole, a.n, True))
        print(out, flush=True)


if __name__ == "__main__":
    main()
