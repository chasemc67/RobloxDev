#!/usr/bin/env python3
"""Rest timing + short-putt cup-ins with the GAME's stop rule (BallController.luau, 2026-10-12):
  a ball stops after 0.5 s under 0.2 studs/s only where the support slope < 0.015 (RollDecel 0.5, gravity 32.7);
  on steeper ground the 2 s wedge rule applies (after up to 3 downhill seam hops; here physics keeps running, so a ball
  that can still roll does, and one held < 0.2 studs/s on steep ground for 2 s counts as a wedged rest).
Physics = sim.py with its own 'settled' checkpoints disabled (patched copy out/_sim_game.py), v_stop 1e-4, t_max 40.
Random shots: half from the tee, half from random felt points, heading at the cup +/-100 deg, speed 2..V_MAX (every 5th 0.5..3).
--putts: rings of starts 0.5..3 studs from the cup (24 angles each), 5 speeds per start (reach the cup + 0.3..1.5 studs on flat felt);
  reports per-distance cup-in rate (any speed / all speeds) and where misses came to rest.
usage: python3 tools/rest_timing.py [holes.json] --hole 6 [--n 400] [--putts] [--variant '{...}'] [--out f]"""
import sys, os, json, argparse, subprocess, importlib, math, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
GENTLE = 0.015
def game_sim():
    src = open(os.path.join(HERE, "sim.py")).read()
    key = "if step > 0 and step % 120 == 0 and not near_mover:"
    assert src.count(key) == 1
    src = src.replace(key, "if False:")
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "_sim_game.py")
    if not os.path.exists(p) or open(p).read() != src: open(p, "w").write(src)
    sys.path.insert(0, os.path.join(HERE, "out")); sys.path.insert(0, HERE)
    return importlib.import_module("_sim_game")
def game_rest(S, ha, p, dtp):
    """apply the game rule to a recorded path; returns (stop_t, first_slow_t, wedged, x, z) or None"""
    p = np.vstack([p, np.repeat(p[-1:], int(2.5 / dtp), 0)])
    spd = np.hypot(np.diff(p[:, 0]), np.diff(p[:, 2])) / dtp
    first = since = None
    for q in range(len(spd)):
        t = (q + 1) * dtp
        if spd[q] < 0.2:
            if first is None: first = t
            if since is None: since = t
            c = S.support(ha.P, p[q + 1, 0], p[q + 1, 2], p[q + 1, 1] + 0.3, 0.15, 0.08)[0]
            g = float(np.hypot(*S.piece_grad(ha.P, c))) if c >= 0 else 0.0
            if t - since >= (0.5 if g < GENTLE else 2.0):
                return t, first, g >= GENTLE, float(p[q + 1, 0]), float(p[q + 1, 2])
        else: since = None
    return None
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("json", nargs="?", default=os.path.join(ROOT, "holes.json"))
    ap.add_argument("--hole", type=int, required=True); ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--putts", action="store_true"); ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--variant"); ap.add_argument("--out")
    a = ap.parse_args(); jf = a.json
    if a.variant:
        jf = os.path.join(HERE, "out", f"scratch-rest-{os.getpid()}.json")
        subprocess.run([sys.executable, os.path.join(HERE, "build_holes.py")], check=True, capture_output=True,
                       env=dict(os.environ, SC_OUT=jf, SC_VARIANT=a.variant))
    S = game_sim()
    hole = [h for h in json.load(open(jf))["holes"] if h["number"] == a.hole][0]
    ha = S.HoleArrays(hole); PH = S.ph_array(); PH[10] = 1e-4; PH[13] = 40.0
    dtp = 6 * PH[12]; path = np.zeros((int(PH[13] / dtp) + 10, 3))
    cup = hole["cup"]["position"]; tee = hole["tee"]["position"]
    xs = [f["center"][0] - max(f["size"]) / 2 for f in hole["felt"]] + [f["center"][0] + max(f["size"]) / 2 for f in hole["felt"]]
    zs = [f["center"][2] - max(f["size"]) / 2 for f in hole["felt"]] + [f["center"][2] + max(f["size"]) / 2 for f in hole["felt"]]
    rng = np.random.default_rng(a.seed)
    def shoot(x, z, vx, vz, y=None):
        cur, yy, _ = S.support(ha.P, x, z, 50.0 if y is None else y + 0.3, 0.15, 0.08)
        if cur < 0: return None, None
        r = S.sim_shot(*ha.args(), PH, x, z, yy, vx, vz, 0.0, True, path)
        return r, path[:int(r[6])].copy()
    out = dict(json=jf, variant=a.variant, hole=a.hole)
    rows = []; outc = {}
    for i in range(a.n):
        if i % 2 == 0: x, z = tee[0], tee[2]
        else:
            while True:
                x, z = rng.uniform(min(xs), max(xs)), rng.uniform(min(zs), max(zs))
                if S.support(ha.P, x, z, 50.0, 0.15, 0.08)[0] >= 0: break
        ang = math.atan2(cup[0] - x, cup[2] - z) + math.radians(rng.uniform(-100, 100))
        v = rng.uniform(0.5, 3) if i % 5 == 0 else rng.uniform(2, S.V_MAX)
        r, p = shoot(x, z, v * math.sin(ang), v * math.cos(ang))
        if r is None: continue
        oc = int(r[3]); outc[oc] = outc.get(oc, 0) + 1
        if oc not in (0, 4) or len(p) < 3: continue
        g = game_rest(S, ha, p, dtp)
        if g is None: rows.append(dict(stop=99.0, tail=99.0, wedge=False, x=float(p[-1, 0]), z=float(p[-1, 2]), unstopped=True)); continue
        rows.append(dict(stop=g[0], tail=g[0] - g[1], wedge=g[2], x=g[3], z=g[4]))
    def st(v):
        v = np.array(v); return dict(n=len(v), median=round(float(np.median(v)), 2), p90=round(float(np.percentile(v, 90)), 2),
                                     max=round(float(v.max()), 2), over10=int((v > 10).sum()), over15=int((v > 15).sum()))
    if rows:
        out.update(stop=st([r["stop"] for r in rows]), tail=st([r["tail"] for r in rows]), wedged=sum(r["wedge"] for r in rows),
                   outcomes={str(k): v for k, v in sorted(outc.items())}, slowest=sorted(rows, key=lambda r: -r["stop"])[:5])
    if a.putts:
        P = {}
        for d in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
            anyin = allin = n = 0; miss = []
            for k in range(24):
                th = 2 * math.pi * k / 24
                x, z = cup[0] + d * math.sin(th), cup[2] + d * math.cos(th)
                hits = 0
                for extra in (0.3, 0.6, 0.9, 1.2, 1.5):
                    v = S.speed_for(d + extra, S.ROLL_DECEL_CONST, S.ROLL_DECEL_PER_SPEED, S.V_MAX)
                    r, p = shoot(x, z, -v * math.sin(th), -v * math.cos(th), y=cup[1])
                    if r is None: continue
                    if int(r[3]) == 1: hits += 1
                    elif len(miss) < 4: miss.append([round(float(r[0]), 2), round(float(r[1]), 2)])
                n += 1; anyin += hits > 0; allin += hits == 5
            P[str(d)] = dict(starts=n, any_speed_in=anyin, all_speeds_in=allin, sample_miss_rests=miss)
        out["putts"] = P
    print(json.dumps(out))
    if a.out: json.dump(dict(out, rows=rows), open(a.out, "w"))
    if a.variant: os.remove(jf)
main()
