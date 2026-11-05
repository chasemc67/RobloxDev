#!/usr/bin/env python3
"""Timing-obstacle check: fire each hole's intended line at a timing obstacle at many phase offsets of the obstacle's cycle
and report how often the obstacle blocks/deflects the ball, lets it pass, or traps it.

    python3 tools/timing_check.py [--json holes.json] [--n 24] [--fuzz 20000] [--out tools/out/timing-r7.json]

For every obstacle (OBSTACLES below) and every phase offset t0 = k/n * T (plus the Playtest Bot's 3 timings t = 0, T/3, 2T/3):
  * the noise-free planned shot of the sim golfer (tools/sim.py plan(): same aim/speed logic as the playtest sim) is fired from
    the obstacle's start point at sim time t0, once with the obstacle and once with it removed ("ghost");
  * touched  = the two paths diverge by > 0.02 stud (the ball hit the obstacle);
  * blocked  = touched and the ball never got past the obstacle line in that stroke;
  * deflected = touched but still got past (knocked off line);
  * passed   = never touched;
  * trap     = stroke timed out (30 s) or the ball came to rest touching the moving blocker (pinned).
The hole's brute-force ace line (from the latest sim json) is checked the same way when it crosses the obstacle.
`--fuzz` adds random soft shots (any aim, 0.3..8 studs/s, any phase) started inside the obstacle's sweep area: timeouts or pins there
are soft-locks a player could hit (the old H7 'batted along the log track' timeout).

    python3 tools/timing_check.py --studio-h9 [--speeds 6.5 7.0 7.75 8.5 9.0] [--legacy]

Round 8: reproduces RobloxDevBot's in-engine H9 pendulum test (stage-h report section 7, GolfTest BLOCK_LINES): from hole-local
(18.5, 1.0, -25.0), aim dir (0.194, -0.981) = 281.19 deg, 7.75 studs/s, hit at 20 phases t0 = 0, 0.25 .. 4.75 s. Phase = the sim
time of the hit, so the bob angle at the hit is amplitude*sin(2 pi t0/period + phase) (holes.json phase 0: t0 = 0 is the bob at the
bottom moving east, +x). Reports the ghost (no pendulum) arrival time/x/speed at the swing plane z = -38.5 and the
blocked/deflected/passed counts. Engine: blocked = never crossed (the sim's 'blocked'); its deflections that crossed = 'deflected'.
--legacy turns the Round-8 height rule off (swing_pass_tol huge = the Round-7 contact model).
"""
import argparse, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim as S

# obstacle id -> start of the intended line and the 'past the obstacle' test on the path (x, y, z arrays)
OBSTACLES = [
    dict(hole=7, part="log", skill="good", start="tee",
         past=lambda x, y, z: z < -21.0, line="tee shot to the lower gap (t1 -> over the log -> gap x 4..6.5)",
         fuzz_box=((-10, 10), (-22.5, -18.5))),
    dict(hole=8, part="root_door", skill="good", start="tee",
         past=lambda x, y, z: (x > 5.2) | (y > 1.2), line="tee bank shot off the junction's north rail into the alcove ring",
         fuzz_box=((2.0, 9.0), (-15.0, -8.0))),
    dict(hole=9, part="lantern_pendulum", skill="good", start="chamber",
         past=lambda x, y, z: (z < -39.1) | (y < 0.9), line="chamber shot through the well mouth (drop waypoint) under the pendulum",
         fuzz_box=((16.0, 28.0), (-40.0, -37.0))),
]
OC = {0: "stopped", 1: "holed", 2: "hazard", 3: "escape", 4: "TIMEOUT", 5: "respawn"}


def part_index(hole, pid):
    return [m["id"] for m in hole["moving_parts"]].index(pid)


def ghost_args(ha, j):
    """ha.args() with moving part j's blockers removed"""
    keep = [k for k in range(ha.nMB) if int(ha.MB[k, 0]) != j]
    MB = ha.MB[keep].copy() if keep else np.zeros((1, 16))
    a = list(ha.args())
    a[5] = MB
    a[6] = len(keep)
    return tuple(a)


def shot(args, PH, start, aim, v, t0):
    path = np.zeros((8000, 3))
    x, y, z = start
    r = S.sim_shot(*args, PH, x, z, y, v * math.cos(aim), v * math.sin(aim), t0, True, path)
    return path[:r[6]].copy(), r


def planned(ha, skill, start):
    PH = S.ph_array()
    WP, WPM, nWP, CM = ha.waypoints(skill)
    b, bh, kb = S.support(ha.P, start[0], start[2], start[1] + 0.01, PH[8], PH[7])
    zone = ha.pzone[b] if b >= 0 else -1
    aim, v, ch = S.plan(ha.P, ha.pzone, ha.W, ha.nW, ha.CUP, WP, WPM, nWP, CM, PH, start[0], start[2], start[1], zone)
    return aim, v


def start_point(ha, hole, cfg, j):
    """tee, or (H9) where the noise-free planned chain from the tee comes to rest in the named zone (obstacle removed)"""
    tee = tuple(ha.TEE)
    if cfg["start"] == "tee":
        return tee
    PH = S.ph_array()
    ga = ghost_args(ha, j)
    for t0 in np.linspace(0, 8, 33):  # first start time whose chain reaches the zone (other moving parts, e.g. H9 gate, vary)
        p = tee
        for s in range(6):
            aim, v = planned(ha, cfg["skill"], p)
            pth, r = shot(ga, PH, p, aim, v, t0 + 30 * s)
            p = (r[0], r[2], r[1])
            b, bh, kb = S.support(ha.P, p[0], p[2], p[1] + 0.01, PH[8], PH[7])
            if b >= 0 and ha.zones[ha.pzone[b]] == cfg["start"]:
                return p
            if r[3] == 1:
                break
    raise RuntimeError(f"H{hole['number']}: no planned chain reaches zone {cfg['start']}")


def pinned(ha, j, r, t_end):
    """ball at rest touching the moving blocker at the end of the stroke"""
    Rth, Rw, cen = np.empty(9), np.empty(9), np.empty(3)
    for k in range(ha.nMB):
        if int(ha.MB[k, 0]) != j:
            continue
        S.blocker_pose(ha.MP, ha.MB, k, t_end, Rth, Rw, cen)
        pen, _, _ = S.sphere_box(r[0], r[2] + S.BALL_RADIUS, r[1], cen[0], cen[1], cen[2], ha.MB[k, 4] + 0.03, ha.MB[k, 5] + 0.03,
                                 ha.MB[k, 6] + 0.03, Rw, S.BALL_RADIUS)
        if pen > 0:
            return True
    return False


def classify(ha, cfg, j, args, gargs, PH, start, aim, v, t0):
    p, r = shot(args, PH, start, aim, v, t0)
    g, rg = shot(gargs, PH, start, aim, v, t0)
    m = min(len(p), len(g))
    dev = np.linalg.norm(p[:m] - g[:m], axis=1)
    touched = bool((dev > 0.02).any()) or (len(p) != len(g) and float(np.linalg.norm(p[-1] - g[-1])) > 0.02)
    past = bool(cfg["past"](p[:, 0], p[:, 1], p[:, 2]).any())
    trap = r[3] == 4 or (r[3] == 0 and pinned(ha, j, r, t0 + r[4]))
    if trap:
        cls = "trap"
    elif not touched:
        cls = "passed"
    elif not past:
        cls = "blocked"
    else:
        cls = "deflected"
    return dict(t0=round(float(t0), 3), cls=cls, outcome=OC[int(r[3])], end=[round(r[0], 2), round(r[2], 2), round(r[1], 2)],
                ghost_outcome=OC[int(rg[3])], elapsed=round(float(r[4]), 2))


def fuzz(ha, cfg, j, n, seed=11):
    """random soft shots from inside the obstacle's sweep area: count timeouts and pins"""
    if n <= 0:
        return dict(n=0)
    PH = S.ph_array()
    rng = np.random.default_rng(seed)
    (x0, x1), (z0, z1) = cfg["fuzz_box"]
    X, Y, Z = [], [], []
    while len(X) < n:
        x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
        b, bh, kb = S.support(ha.P, x, z, 50.0, 100.0, S.BALL_RADIUS)
        if b < 0 or kb >= 0:
            continue
        inside = any(S.sphere_box(x, bh + S.BALL_RADIUS, z, *ha.W[q, 0:6], ha.W[q, 6:15], S.BALL_RADIUS)[0] > 0 for q in range(ha.nW))
        if not inside:
            X.append(x); Y.append(bh); Z.append(z)
    X, Y, Z = np.array(X), np.array(Y), np.array(Z)
    A = rng.uniform(0, 2 * np.pi, n)
    V = rng.uniform(0.3, 8.0, n)
    T = rng.uniform(0, 300, n)
    oc, ex = S.fuzz_batch(*ha.args(), PH, X, Z, Y, A, V, T)
    to = np.where(oc == 4)[0]
    return dict(n=n, timeouts=int(len(to)), examples=[dict(start=[round(X[i], 2), round(Z[i], 2)], aim_deg=round(float(np.degrees(A[i])), 1),
                                                          v=round(float(V[i]), 2), t0=round(float(T[i]), 2)) for i in to[:5]])


def run(course, n=24, nfuzz=20000, ace_lines=None):
    PH = S.ph_array()
    res = []
    for cfg in OBSTACLES:
        hole = next(h for h in course["holes"] if h["number"] == cfg["hole"])
        ha = S.HoleArrays(hole)
        j = part_index(hole, cfg["part"])
        m = hole["moving_parts"][j]
        T = S.cycle_period(m)
        args, gargs = ha.args(), ghost_args(ha, j)
        start = start_point(ha, hole, cfg, j)
        aim, v = planned(ha, cfg["skill"], start)
        lines = [("intended", start, aim, v)]
        i_int = len(res)
        al = (ace_lines or {}).get(hole["number"])
        if al:
            lines.append(("ace", tuple(ha.TEE), math.radians(al["aim_deg"]), al["speed"]))
        for name, st, a_, v_ in lines:
            grid = [classify(ha, cfg, j, args, gargs, PH, st, a_, v_, k * T / n) for k in range(n)]
            bot = [classify(ha, cfg, j, args, gargs, PH, st, a_, v_, f * T) for f in (0.0, 1 / 3, 2 / 3)]
            if name == "ace" and all(g["cls"] == "passed" for g in grid) and all(g["ghost_outcome"] != "holed" for g in grid):
                continue  # ace line never meets the obstacle and never holes: nothing to report
            cnt = {c: sum(g["cls"] == c for g in grid) for c in ("blocked", "deflected", "passed", "trap")}
            res.append(dict(hole=cfg["hole"], part=cfg["part"], line=name, desc=cfg["line"] if name == "intended" else "brute-force ace line",
                            start=[round(float(q), 2) for q in st], aim_deg=round(math.degrees(a_) % 360, 2), speed=round(float(v_), 2),
                            period=round(T, 3), n=n, counts=cnt,
                            block_pct=round(100 * (cnt["blocked"] + cnt["deflected"]) / n, 1), pass_pct=round(100 * cnt["passed"] / n, 1),
                            trap=cnt["trap"], bot3=[g["cls"] for g in bot], grid=grid,
                            holed_pct=round(100 * sum(g["outcome"] == "holed" for g in grid) / n, 1)))
        res[i_int]["fuzz"] = fuzz(ha, cfg, j, nfuzz)
    return res


def table(res):
    out = ["| Hole | Obstacle | Line | Period | Blocked | Deflected | Blocked+deflected | Passed | Traps | Bot timings t=0, T/3, 2T/3 | "
           "Fuzz soft-locks |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in res:
        c = r["counts"]
        fz = r.get("fuzz")
        fzs = f"{fz['timeouts']}/{fz['n']}" if fz and fz.get("n") else "-"
        out.append(f"| H{r['hole']} | {r['part']} | {r['line']} | {r['period']:g} s | {c['blocked']}/{r['n']} | {c['deflected']}/{r['n']} | "
                   f"**{r['block_pct']:g}%** | {r['pass_pct']:g}% | {r['trap']} | {', '.join(r['bot3'])} | {fzs} |")
    return "\n".join(out)


STUDIO_H9 = dict(start=(18.5, 1.0, -25.0), dir=(0.194, -0.981), speed=7.75, phases=[0.25 * k for k in range(20)],
                 engine=dict(t=(2.5, 2.9), x=21.18, v=(2.7, 3.2), blocked=2, touched=5, n=20))


def swing_crossing(p, z_line, dt=6 * S.PHYS["dt"]):
    """first crossing of z = z_line on a recorded path (every 6 steps): time, x, horizontal speed"""
    for i in range(1, len(p)):
        if p[i, 2] <= z_line < p[i - 1, 2]:
            f = (p[i - 1, 2] - z_line) / (p[i - 1, 2] - p[i, 2])
            v = float(np.linalg.norm(p[i, [0, 2]] - p[i - 1, [0, 2]]) / dt)
            return (i - 1 + f) * dt, float(p[i - 1, 0] + f * (p[i, 0] - p[i - 1, 0])), v
    return None


def studio_h9(course, speeds, legacy=False, nph=None):
    hole = next(h for h in course["holes"] if h["number"] == 9)
    cfg = OBSTACLES[2]
    ha = S.HoleArrays(hole)
    j = part_index(hole, cfg["part"])
    m = hole["moving_parts"][j]
    PH = S.ph_array()
    if legacy:
        PH[S.PH_KEYS.index("swing_pass_tol")] = 1e9
    args, gargs = ha.args(), ghost_args(ha, j)
    st = STUDIO_H9
    aim = math.atan2(st["dir"][1], st["dir"][0])
    phases = st["phases"] if not nph else [round(k * m["period_s"] / nph, 4) for k in range(nph)]
    out = []
    for v in speeds:
        g, _ = shot(gargs, PH, st["start"], aim, v, 0.0)
        cr = swing_crossing(g, m["pivot"][2])
        grid = [classify(ha, cfg, j, args, gargs, PH, st["start"], aim, v, t0) for t0 in phases]
        cnt = {c: sum(q["cls"] == c for q in grid) for c in ("blocked", "deflected", "passed", "trap")}
        out.append(dict(speed=v, cross=None if cr is None else [round(q, 3) for q in cr], counts=cnt, n=len(grid),
                        grid=" ".join(f"{q['t0']:g}:{q['cls'][0]}" for q in grid)))
    return out


def studio_table(res):
    e = STUDIO_H9["engine"]
    rows = ["| Speed | Arrive z=-38.5 (s) | x there | Speed there | Blocked | Deflected (crossed) | Touched | Passed | Traps |",
            "|---|---|---|---|---|---|---|---|---|"]
    for r in res:
        c, n = r["counts"], r["n"]
        cr = r["cross"] or ("-", "-", "-")
        rows.append(f"| {r['speed']:g} | {cr[0]} | {cr[1]} | {cr[2]} | **{c['blocked']}/{n} = {100 * c['blocked'] / n:.0f}%** | "
                    f"{c['deflected']} | {c['blocked'] + c['deflected']} | {c['passed']} | {c['trap']} |")
    rows.append(f"| engine 7.75 | {e['t'][0]}-{e['t'][1]} | {e['x']} | {e['v'][0]}-{e['v'][1]} | {e['blocked']}/{e['n']} = "
                f"{100 * e['blocked'] / e['n']:.0f}% | {e['touched'] - e['blocked']} | {e['touched']} | {e['n'] - e['touched']} | 0 |")
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio-h9", action="store_true", help="RobloxDevBot's in-engine H9 pendulum test conditions (Round 8)")
    ap.add_argument("--speeds", type=float, nargs="*", default=[STUDIO_H9["speed"]])
    ap.add_argument("--phases", type=int, default=None, help="with --studio-h9: N phases evenly over one period (Round 9; default = the 20 legacy phases 0..4.75 s)")
    ap.add_argument("--legacy", action="store_true", help="with --studio-h9: Round-7 contact model (no pendulum height rule)")
    ap.add_argument("--json", default=os.path.join(HERE, "..", "holes.json"))
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--fuzz", type=int, default=20000)
    ap.add_argument("--sim", default=os.path.join(HERE, "out", "sim-latest.json"), help="sim json with the ace lines")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    course = json.load(open(a.json))
    if a.studio_h9:
        res = studio_h9(course, a.speeds, a.legacy, a.phases)
        for r in res:
            print(f"v {r['speed']:g}: {r['grid']}")
        print("\n" + studio_table(res))
        if a.out:
            json.dump(dict(json=os.path.abspath(a.json), legacy=a.legacy, results=res, table=studio_table(res)), open(a.out, "w"), indent=1)
        return
    ace = {}
    if a.sim and os.path.exists(a.sim):
        for h in json.load(open(a.sim))["holes"]:
            ln = (h.get("hio_search") or {}).get("line")
            if ln:
                ace[int(h["id"][1:])] = ln
    res = run(course, a.n, a.fuzz, ace)
    for r in res:
        print(f"H{r['hole']} {r['part']} [{r['line']}] start {r['start']} aim {r['aim_deg']} v {r['speed']} T {r['period']} s: "
              + " ".join(f"{g['t0']:.2f}:{g['cls'][0]}" for g in r["grid"]) + f"  holed {r['holed_pct']}%")
        if r.get("fuzz", {}).get("timeouts"):
            print("   fuzz timeouts e.g.", r["fuzz"]["examples"][:3])
    print("\n" + table(res))
    if a.out:
        json.dump(dict(json=os.path.abspath(a.json), results=res, table=table(res)), open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
