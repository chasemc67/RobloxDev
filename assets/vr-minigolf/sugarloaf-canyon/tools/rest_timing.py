"""H8 (or any hole) rest timing with the GAME's stop rule (Studio BallController):
  stopped once speed < 0.2 studs/s continuously for 0.5 s on a gentle slope; a ball held < 0.2 on a steeper
  slope (wedged) is set to rest after 2 s. tail = stop time - first time speed < 0.2.
Physics = sim.py with its artificial 'settled' checkpoints disabled (patched copy in out/_sim_game.py), so the
ball keeps rocking until the game rule fires.
Shots: Playtest Bot's 80 Studio plans (seed 2026101208; tee world (360,-4945) = local (0,0)) + N random shots.
usage: python3 tools/rest_timing.py [holes.json] [--hole 8] [--n 400] [--variant '{"h8_flat":1.5}'] [--out f]"""
import sys, os, json, argparse, subprocess, importlib, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
PLANS = "/workspace/writerbot/vr-minigolf-post/playtest-bot/sc-batch12/results_v20.json"
GENTLE = 0.015  # BallController.luau: |slope| < 0.015 = gentle (0.5 s under 0.2 studs/s); steeper = 2 s wedge rule
# (the game first allows up to 3 downhill seam hops; here physics keeps running, so a ball that can still roll does, and
# one held < 0.2 on steep ground for 2 s counts as a wedge rest)
def game_sim():
    src = open(os.path.join(HERE, "sim.py")).read()
    key = "if step > 0 and step % 120 == 0 and not near_mover:"
    assert src.count(key) == 1
    src = src.replace(key, "if False:")
    p = os.path.join(HERE, "out", "_sim_game.py")
    if not os.path.exists(p) or open(p).read() != src: open(p, "w").write(src)
    sys.path.insert(0, os.path.join(HERE, "out")); sys.path.insert(0, HERE)
    return importlib.import_module("_sim_game")
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("json", nargs="?", default=os.path.join(ROOT, "holes.json"))
    ap.add_argument("--hole", type=int, default=8); ap.add_argument("--n", type=int, default=400)  # + 80 Studio plans = 480 shots
    ap.add_argument("--variant"); ap.add_argument("--out"); ap.add_argument("--seed", type=int, default=5)
    a = ap.parse_args(); jf = a.json
    if a.variant:
        jf = os.path.join(HERE, "out", f"scratch-rest-{os.getpid()}.json")
        subprocess.run([sys.executable, os.path.join(HERE, "build_holes.py")], check=True, capture_output=True,
                       env=dict(os.environ, SC_OUT=jf, SC_VARIANT=a.variant))
    S = game_sim()
    hole = [h for h in json.load(open(jf))["holes"] if h["number"] == a.hole][0]
    ha = S.HoleArrays(hole); PH = S.ph_array(); PH[10] = 1e-4; PH[13] = 40.0
    dtp = 6 * PH[12]; path = np.zeros((int(PH[13] / dtp) + 10, 3))
    shots = []
    for p in (json.load(open(PLANS))["plans"] if a.hole == 8 else []):  # Studio plans are H8 shots
        shots.append((p["start"][0] - 360, p["start"][2] + 4945, p["velocity"][0], p["velocity"][2], "studio"))
    rng = np.random.default_rng(a.seed); cup = hole["cup"]["position"] if isinstance(hole.get("cup"), dict) else [5, 0, -55]
    XR = (min(f["center"][0] - max(f["size"]) / 2 for f in hole["felt"]), max(f["center"][0] + max(f["size"]) / 2 for f in hole["felt"])) if a.hole != 8 else (-9, 9)
    ZR = (min(f["center"][2] - max(f["size"]) / 2 for f in hole["felt"]), max(f["center"][2] + max(f["size"]) / 2 for f in hole["felt"])) if a.hole != 8 else (-60, 2)
    for i in range(a.n):  # tee + random felt starts, heading toward cup +/-100 deg, speed 2-19.78 (every 5th 0.5-3)
        if i % 2 == 0: x, z = 0.0, 0.0
        else:
            while True:
                x, z = rng.uniform(*XR), rng.uniform(*ZR)
                if S.support(ha.P, x, z, 5.0 if a.hole == 8 else 50.0, 0.15, 0.08)[0] >= 0: break
        ang = np.arctan2(cup[0] - x, cup[2] - z) + np.radians(rng.uniform(-100, 100))
        v = rng.uniform(0.5, 3) if i % 5 == 0 else rng.uniform(2, 19.78)
        shots.append((x, z, v * np.sin(ang), v * np.cos(ang), "random"))
    rows = []
    for x, z, vx, vz, kind in shots:
        cur, y, _ = S.support(ha.P, x, z, 5.0 if a.hole == 8 else 50.0, 0.15, 0.08)
        if cur < 0: continue
        r = S.sim_shot(*ha.args(), PH, x, z, y, vx, vz, 0.0, True, path)
        if int(r[3]) not in (0, 4): continue  # holed / hazard
        p = path[:int(r[6])]
        if len(p) < 3: continue
        tail_pad = int(2.5 / dtp)  # after sim stop the ball sits still
        p = np.vstack([p, np.repeat(p[-1:], tail_pad, 0)])
        spd = np.hypot(np.diff(p[:, 0]), np.diff(p[:, 2])) / dtp
        grad = np.array([np.hypot(*S.piece_grad(ha.P, c)) if c >= 0 else 0.0 for c in
                         [S.support(ha.P, q[0], q[2], q[1] + 0.3, 0.15, 0.08)[0] for q in p[1:]]])
        slow = spd < 0.2; first = None; since = None; stop = None
        for q in range(len(slow)):
            t = (q + 1) * dtp
            if slow[q]:
                if first is None: first = t
                if since is None: since = t
                need = 0.5 if grad[q] < GENTLE else 2.0
                if t - since >= need and (grad[q] < GENTLE or t - since >= 2.0): stop = t; break
            else: since = None
        if stop is None or first is None: continue
        rows.append(dict(kind=kind, tail=stop - first, stop=stop, wedge=bool(grad[q] >= GENTLE), x=float(p[q+1, 0]), z=float(p[q+1, 2])))
    def st(v):
        v = np.array(v); return dict(n=len(v), median=round(float(np.median(v)), 2), p90=round(float(np.percentile(v, 90)), 2),
                                     max=round(float(v.max()), 2), over1_5=int((v > 1.5).sum()), over3=int((v > 3).sum()))
    out = dict(json=jf, variant=a.variant, studio80=st([r["tail"] for r in rows if r["kind"] == "studio"]) if a.hole == 8 else None,
               all=st([r["tail"] for r in rows]), stop_all=st([r["stop"] for r in rows]), wedged=sum(r["wedge"] for r in rows), wedge_pts=[(round(r["x"], 1), round(r["z"], 1)) for r in rows if r["wedge"]][:12])
    print(json.dumps(out))
    if a.out: json.dump(dict(out, rows=rows), open(a.out, "w"))
    if a.variant: os.remove(jf)
main()
