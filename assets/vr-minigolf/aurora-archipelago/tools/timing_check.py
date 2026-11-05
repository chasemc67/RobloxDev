#!/usr/bin/env python3
"""Timing-obstacle check: fire each hole's intended line at a timing obstacle at many phase offsets of the obstacle's cycle
and report how often the obstacle blocks/deflects the ball, lets it pass, or traps it.

    python3 tools/timing_check.py [--json holes.json] [--n 96] [--fuzz 100000] [--out tools/out/timing-r7.json]

For every obstacle (OBSTACLES below) and every phase offset t0 = k/n * T (plus the playtester's 3 timings t = 0, T/3, 2T/3):
  * the noise-free planned shot of the sim golfer (tools/sim.py plan(): same aim/speed logic as the playtest sim) is fired from
    the obstacle's start point at sim time t0, once with the obstacle and once with it removed ("ghost");
  * touched  = the two paths diverge by > 0.02 stud (the ball hit the obstacle);
  * blocked  = touched and the ball never got past the obstacle line in that stroke;
  * deflected = touched but still got past (knocked off line);
  * passed   = never touched;
  * trap     = stroke timed out (30 s) or the ball came to rest touching the moving blocker (pinned).
The hole's brute-force ace line (from the latest sim json) is checked the same way when it crosses the obstacle.
`--fuzz` adds random soft shots (any aim, 0.3..8 studs/s, any phase) started inside the obstacle's sweep area: timeouts or pins there
are soft-locks a player could hit (Lantern Grove's old H7 'batted along the log track' timeout).
Blocked shots are split into STOPS (head-on, face square to the line) and KICKS (side face / corner); the Studio estimate is
stops + 0.36 kicks (Lantern Grove Round 10 calibration). Aurora: H17's light span blocks by vanishing (the ball falls, +1, respawn):
those blocks are counted as stops ('fall'); H5's geyser column blocks with its square side face while raised.
Target: 25-50% blocked on the intended line judged by stops, aiming ~10 points above the in-game target (sim 35-50%), 0 traps, 0 soft-locks.

"""
import argparse, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim as S

# obstacle id -> start of the intended line and the 'past the obstacle' test on the path (x, y, z arrays).
# line = the timing line through the obstacle (the shot the obstacle is meant to gate); skill = whose noise-free planned shot it is.
OBSTACLES = [
    dict(hole=5, part="geyser_column", skill="good", start="tee",
         past=lambda x, y, z: y > 2.0, line="tee shot onto the geyser platform while it is flush (lifted to the upper green)",
         fuzz_box=((-3.0, 3.0), (-28.0, -22.0))),
    dict(hole=11, part="ice_floe", skill="good", start="tee",
         past=lambda x, y, z: z < -28.5, line="tee shot through the neck past the drifting ice floe (neck waypoint)",
         fuzz_box=((-3.5, 3.5), (-29.0, -27.0))),
    dict(hole=12, part="paddle_wheel", skill="good", start="tee",
         past=lambda x, y, z: z < -18.3, line="tee shot into the icebreaker channel past the paddle wheel",
         fuzz_box=((-4.5, 4.5), (-18.0, -16.0))),
    dict(hole=13, part="carousel_arms", skill="good", start="tee",
         past=lambda x, y, z: z < -38.0, line="tee shot round the carousel hub past the sweeping arms",
         fuzz_box=((-13.0, 13.0), (-49.0, -23.0))),
    dict(hole=14, part="icicle_bell", skill="average", start="tee",
         past=lambda x, y, z: z < -25.0, line="straight tee shot at the flag under the swinging icicle bell",
         fuzz_box=((-3.5, 3.5), (-26.0, -22.0))),
    dict(hole=17, part="aurora_span", skill="good", start="tee",
         past=lambda x, y, z: z < -33.2, line="tee shot straight over the aurora light span (fixed crystal piers either side)",
         fuzz_box=((-1.4, 1.4), (-33.0, -25.0))),
]
KAPPA = 0.36  # Lantern Grove Round 10 fit: Studio blocked ~= stops + KAPPA * kicks (sim kicks are mostly shoved through in-engine)
OC = {0: "stopped", 1: "holed", 2: "hazard", 3: "escape", 4: "TIMEOUT", 5: "respawn"}


def part_index(hole, pid):
    return [m["id"] for m in hole["moving_parts"]].index(pid)


def ghost_args(ha, j):
    """ha.args() with moving part j removed: its blockers gone, a lift on that column always boarding, a toggled span always solid"""
    keep = [k for k in range(ha.nMB) if int(ha.MB[k, 0]) != j]
    MB = ha.MB[keep].copy() if keep else np.zeros((1, 16))
    a = list(ha.args())
    m = ha.hole["moving_parts"][j]
    P = ha.P.copy()
    if m["type"] == "toggle":
        for i, p in enumerate(ha.hole["felt"]):
            if (p.get("timed") or {}).get("part") == m["id"]:
                P[i, 17] = 0.0; P[i, 20] = 1.0
    TP = ha.TP.copy()
    for q, t in enumerate(ha.hole.get("teleports", [])):
        if (t.get("lift") or {}).get("column") == m["id"]:
            TP[q, 16] = 0.0; TP[q, 17] = TP[q, 15] + 1.0
    a[0] = P
    a[5] = MB
    a[6] = len(keep)
    a[7] = TP
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
        if pen > 1e-9 and not (ha.MP[j, 0] == 1 and abs(ha.MP[j, 5]) > 0.9):
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
    kind = None
    if trap:
        cls = "trap"
    elif not touched:
        cls = "passed"
    elif not past:
        cls = "blocked"
        kind = "stop" if ha.hole["moving_parts"][j]["type"] == "toggle" else stop_or_kick(p, g, aim)
    else:
        cls = "deflected"
    return dict(t0=round(float(t0), 3), cls=cls, kind=kind, outcome=OC[int(r[3])], end=[round(r[0], 2), round(r[2], 2), round(r[1], 2)],
                ghost_outcome=OC[int(rg[3])], ghost_past=bool(cfg["past"](g[:,0],g[:,1],g[:,2]).any()), elapsed=round(float(r[4]), 2))


def stop_or_kick(p, g, aim):
    """Lantern Grove Round 10: a sim 'block' is a STOP when the first contact is a face square to the ball's line (the velocity change
    across the contact is mostly along the line of travel: |cos| >= 0.7) - the ball bounces back the way it came. Otherwise it is a KICK
    (a side face or corner throws it sideways), which the engine mostly shoves on through. Judge obstacles by stops."""
    n = min(len(p), len(g))
    dev = np.linalg.norm(p[:n] - g[:n], axis=1) > 0.02
    if not dev.any():
        return "stop"
    i0 = max(int(np.argmax(dev)), 2)
    vb = (p[i0 - 1] - p[i0 - 2])[[0, 2]]
    va = (p[min(i0 + 2, len(p) - 1)] - p[min(i0 + 1, len(p) - 2)])[[0, 2]]
    d = va - vb
    if np.linalg.norm(d) < 1e-9 or np.linalg.norm(vb) < 1e-9:
        return "stop"
    c = abs(float(np.dot(d, vb) / (np.linalg.norm(d) * np.linalg.norm(vb))))
    return "stop" if c >= 0.7 else "kick"


def fuzz(ha, cfg, j, n, seed=11, phase_count=None):
    """random soft shots from inside the obstacle's sweep area: count timeouts and pins"""
    if n <= 0:
        return dict(n=0)
    PH = S.ph_array()
    rng = np.random.default_rng(seed)
    (x0, x1), (z0, z1) = cfg["fuzz_box"]
    X, Y, Z, times = [], [], [], []
    rt, rw, cen = np.empty(9), np.empty(9), np.empty(3)
    while len(X) < n:
        x, z, t = rng.uniform(x0, x1), rng.uniform(z0, z1), rng.uniform(0, 300)
        if phase_count:
            t = int(rng.integers(phase_count)) * S.cycle_period(ha.hole["moving_parts"][j]) / phase_count
        P = ha.P
        b, bh, kb = S.support(P, x, z, 50.0, 100.0, S.BALL_RADIUS)
        if b < 0 or kb >= 0:
            continue
        inside = any(S.sphere_box(x, bh + S.BALL_RADIUS, z, *ha.W[q, 0:6], ha.W[q, 6:15], S.BALL_RADIUS)[0] > 1e-6 for q in range(ha.nW))
        for k in range(ha.nMB):
            if inside: break
            S.blocker_pose(ha.MP,ha.MB,k,t,rt,rw,cen)
            inside = S.sphere_box(x,bh+S.BALL_RADIUS,z,*cen,*ha.MB[k,4:7],rw,S.BALL_RADIUS)[0] > 1e-6
        if not inside:
            X.append(x); Y.append(bh); Z.append(z); times.append(t)
    X, Y, Z, T = np.array(X), np.array(Y), np.array(Z), np.array(times)
    A = rng.uniform(0, 2 * np.pi, n)
    V = rng.uniform(0.3, 8.0, n)
    from rest_audit import audit_batch
    oc, ex, pins = audit_batch(*ha.args(), PH, X, Z, Y, A, V, T)
    to = np.where(oc == 4)[0]
    return dict(n=n, seed=seed, phase_count=phase_count, timeouts=int(len(to)), escapes=int((oc == 3).sum()),
                pinned_rests=int(pins.sum()),
                excluded_rests=int(((oc == 0) & (np.hypot(ex[:,0],ex[:,2]+36) < 7)).sum()) if cfg["hole"] == 13 else 0,
                escape_examples=[dict(start=[float(X[i]),float(Y[i]),float(Z[i])], aim=float(A[i]), speed=float(V[i]), t0=float(T[i]), end=ex[i].tolist()) for i in np.where(oc == 3)[0][:10]],
                pin_examples=[dict(start=[float(X[i]),float(Y[i]),float(Z[i])], aim=float(A[i]), speed=float(V[i]),
                                   t0=float(T[i]), end=ex[i].tolist()) for i in np.where(pins > 0)[0][:5]], examples=[dict(start=[round(X[i], 2), round(Z[i], 2)], aim_deg=round(float(np.degrees(A[i])), 1),
                                                          v=round(float(V[i]), 2), t0=round(float(T[i]), 2)) for i in to[:5]])


def run(course, n=96, nfuzz=20000, ace_lines=None, seed=11, fuzz_phase_grid=False):
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
            cnt["stops"] = sum(g.get("kind") == "stop" for g in grid)
            cnt["kicks"] = sum(g.get("kind") == "kick" for g in grid)
            res.append(dict(hole=cfg["hole"], part=cfg["part"], line=name, desc=cfg["line"] if name == "intended" else "brute-force ace line",
                            start=[round(float(q), 2) for q in st], aim_deg=round(math.degrees(a_) % 360, 2), speed=round(float(v_), 2),
                            period=round(T, 3), n=n, counts=cnt,
                            block_pct=round(100 * (cnt["blocked"] + cnt["deflected"]) / n, 1), pass_pct=round(100 * cnt["passed"] / n, 1),
                            trap=cnt["trap"], ghost_past_count=sum(g["ghost_past"] for g in grid), bot3=[g["cls"] for g in bot], grid=grid,
                            est_pct=round(100 * (cnt["stops"] + KAPPA * cnt["kicks"]) / n, 1),
                            holed_pct=round(100 * sum(g["outcome"] == "holed" for g in grid) / n, 1)))
        res[i_int]["fuzz"] = fuzz(ha, cfg, j, nfuzz, seed=seed, phase_count=n if fuzz_phase_grid else None)
    return res


def table(res):
    out = ["| Hole | Obstacle | Line | Period | Blocked (stops + kicks) | Deflected | Blocked+deflected | Studio est. (stops + 0.36 kicks) | Passed | Traps | "
           "Timings t=0, T/3, 2T/3 | Fuzz soft-locks |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in res:
        c = r["counts"]
        fz = r.get("fuzz")
        fzs = f"{fz['timeouts']}/{fz['n']}" if fz and fz.get("n") else "-"
        out.append(f"| H{r['hole']} | {r['part']} | {r['line']} | {r['period']:g} s | {c['blocked']}/{r['n']} ({c['stops']} + {c['kicks']}) | "
                   f"{c['deflected']}/{r['n']} | {r['block_pct']:g}% | **{r['est_pct']:g}%** | {r['pass_pct']:g}% | {r['trap']} | "
                   f"{', '.join(r['bot3'])} | {fzs} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--holes", type=int, nargs="*")
    ap.add_argument("--json", default=os.path.join(HERE, "..", "holes.json"))
    ap.add_argument("--n", type=int, default=96)
    ap.add_argument("--fuzz", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--fuzz-phase-grid", action="store_true", help="sample fuzz starts on the same n-phase grid as timing shots")
    ap.add_argument("--sim", default=os.path.join(HERE, "out", "sim-latest.json"), help="sim json with the ace lines")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    course = json.load(open(a.json))
    ace = {}
    if a.sim and os.path.exists(a.sim):
        for h in json.load(open(a.sim))["holes"]:
            ln = (h.get("hio_search") or {}).get("line")
            if ln:
                ace[int(h["id"][1:])] = ln
    if a.holes:
        OBSTACLES[:] = [o for o in OBSTACLES if o["hole"] in a.holes]
    res = run(course, a.n, a.fuzz, ace, seed=a.seed, fuzz_phase_grid=a.fuzz_phase_grid)
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
