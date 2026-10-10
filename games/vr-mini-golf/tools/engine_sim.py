#!/usr/bin/env python3
"""Engine-calibrated copy of the designer's Lantern Grove simulator, for finding ace lines fast.

The designer's sim (assets/vr-mini-golf/lantern-grove/tools/sim.py) treats a rail hit as "normal component x 0.63,
tangential kept". The game keeps the measured numbers from the harness (`walls`/`bank` scenarios): normal restitution
~0.60, tangential retention ~0.93, and then the post-impact skid of BallController (SpinKeep 0.5, slip closing at
3.5 mu g), whose net effect on the rolling velocity is  v_final = v_out + SpinKeep * (v_in - v_out) / 3.5.
This script loads sim.py, patches those two collision blocks, sets the measured constants, and brute-forces
aim x speed (x mover phase) from each tee. The best lines are printed as JSON for the in-game harness
(GolfTestOpts.hioLines) to verify, since only an in-engine ace counts.

  uv run --with numpy --with numba python tools/engine_sim.py --holes 1 2 3 --top 6
"""
import argparse
import importlib.util
import json
import math
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SPEC_DIR = os.path.join(REPO, "assets", "vr-mini-golf", "lantern-grove")

RESTITUTION = 0.60
TANGENTIAL = 0.93
SKID = 0.5 / 3.5  # Config.SpinKeep / 3.5

CLIFF_OLD = """            vn = vx * wx + vz * wz
            touching = True
            if vn < 0:
                vx -= (1 + e) * vn * wx
                vz -= (1 + e) * vn * wz"""
CLIFF_NEW = """            vn = vx * wx + vz * wz
            touching = True
            if vn < 0:
                ix = vx; iz = vz
                tx = vx - vn * wx; tz = vz - vn * wz
                ox_ = -e * vn * wx + ENG_TR * tx; oz_ = -e * vn * wz + ENG_TR * tz
                vx = ox_ + ENG_SK * (ix - ox_); vz = oz_ + ENG_SK * (iz - oz_)"""
WALL_OLD = """            rvx = vx - bvx; rvz = vz - bvz
            vn = rvx * bnx + rvz * bnz
            if vn < 0:
                rvx -= (1 + ec) * vn * bnx
                rvz -= (1 + ec) * vn * bnz
            vx = rvx + bvx; vz = rvz + bvz"""
WALL_NEW = """            rvx = vx - bvx; rvz = vz - bvz
            vn = rvx * bnx + rvz * bnz
            if vn < 0:
                ix = rvx; iz = rvz
                tx = rvx - vn * bnx; tz = rvz - vn * bnz
                ox_ = -ec * vn * bnx + ENG_TR * tx; oz_ = -ec * vn * bnz + ENG_TR * tz
                rvx = ox_ + ENG_SK * (ix - ox_); rvz = oz_ + ENG_SK * (iz - oz_)
            vx = rvx + bvx; vz = rvz + bvz"""


def load_sim(spec_dir, drop_keep):
    src = open(os.path.join(spec_dir, "tools", "sim.py")).read()
    for old, new in ((CLIFF_OLD, CLIFF_NEW), (WALL_OLD, WALL_NEW)):
        if src.count(old) != 1:
            raise SystemExit("sim.py changed: patch block not found:\n" + old)
        src = src.replace(old, new)
    src = src.replace("cache=True", "cache=False")  # the patched copy is loaded under a synthetic name
    src = src.replace("HERE = os.path.dirname(os.path.abspath(__file__))",
                      "HERE = %r\nENG_TR = %r\nENG_SK = %r" % (os.path.join(spec_dir, "tools"), TANGENTIAL, SKID), 1)
    d = os.path.join(tempfile.gettempdir(), "lantern_engine_sim")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "sim_engine.py")
    if not os.path.exists(path) or open(path).read() != src:
        open(path, "w").write(src)
    sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location("sim_engine", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sim_engine"] = mod  # numba's on-disk cache re-imports the module by name
    spec.loader.exec_module(mod)
    mod.PHYS.update(restitution=RESTITUTION, bumper_restitution=0.62, drop_damp=drop_keep)
    return mod


def search(sim, hole, top, phases=None, step=0.25, n_pow=60):
    import numpy as np
    ha = sim.HoleArrays(hole)
    PH = sim.ph_array()
    tee = ha.TEE
    hio = hole.get("hio") or {}
    if phases is None:
        phases = [0.0] if ha.nMP == 0 else [hio.get("phase") or 0.0]
    aims = np.radians(np.arange(0, 360, step))
    pows = np.linspace(0.3, 1.0, n_pow) * sim.PHYS["v_max"]
    A, V, T = np.meshgrid(aims, pows, np.array(phases, dtype=float), indexing="ij")
    A, V, T = A.ravel(), V.ravel(), T.ravel()
    oc, md, _ = sim.shot_batch_chunked(ha, PH, tee[0], tee[2], tee[1], A, V, T)
    hits = np.where(oc == 1)[0]
    lines = []
    if len(hits):
        Ah, Vh = A[hits], V[hits]
        # robustness = hitting neighbours within +-0.75 deg and +-0.5 studs/s
        score = np.array([int(((np.abs(Ah - Ah[j]) <= math.radians(0.75)) & (np.abs(Vh - Vh[j]) <= 0.5)).sum()) for j in range(len(hits))])
        order = np.argsort(-score)
        for j in order:
            a, v = float(np.degrees(Ah[j]) % 360), float(Vh[j])
            if all(abs(a - l[0]) > 1.5 or abs(v - l[1]) > 1.0 for l in lines):
                lines.append([round(a, 2), round(v, 2), float(T[hits[j]]), int(score[j])])
            if len(lines) >= top:
                break
    return dict(hole=hole["number"], shots=int(len(A)), hits=int(len(hits)), lines=lines,
                closest=float(md.min()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", default=SPEC_DIR)
    ap.add_argument("--holes", type=int, nargs="*")
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--drop-keep", type=float, default=0.95, help="horizontal speed kept on a drop (sim: 0.8)")
    ap.add_argument("--step", type=float, default=0.25, help="aim grid step (deg)")
    ap.add_argument("--phases", type=int, default=1, help="mover start phases to try, evenly over the hole's cycle "
                    "(1 = the notes' phase only)")
    args = ap.parse_args()
    sim = load_sim(args.spec, args.drop_keep)
    course = json.load(open(os.path.join(args.spec, "holes.json")))
    sys.path.insert(0, HERE)
    import holes_to_lua  # noqa: E402  (adds the notes' hio lines)
    _, data = holes_to_lua.convert(os.path.join(args.spec, "holes.json"))
    hio = {h["number"]: h.get("hio") for h in data["holes"]}
    out = {}
    for hole in course["holes"]:
        if args.holes and hole["number"] not in args.holes:
            continue
        hole = dict(hole, hio=hio.get(hole["number"]))
        phases = None
        if args.phases > 1 and hole.get("moving_parts"):
            per = 1.0
            for m in hole["moving_parts"]:
                p = 2 * (m["range"][1] - m["range"][0]) / abs(m["speed"]) if m.get("range") else 360 / abs(m["speed"])
                per = max(per, p)
            phases = [per * k / args.phases for k in range(args.phases)]
        r = search(sim, hole, args.top, phases=phases, step=args.step)
        out[str(hole["number"])] = r["lines"]
        print("hole %d: %d/%d hits, closest %.2f, lines %s" % (r["hole"], r["hits"], r["shots"], r["closest"], r["lines"]), file=sys.stderr)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
