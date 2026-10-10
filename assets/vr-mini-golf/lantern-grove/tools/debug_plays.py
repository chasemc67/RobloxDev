#!/usr/bin/env python3
"""Dev tool: trace K AI plays for one hole/skill and draw every stroke path over the layout.

    python3 tools/debug_plays.py 4 good --k 25 [--bad-only]  -> tools/out/debug-h04-good.png
Also prints per-stroke outcomes (0 stop, 1 holed, 2 hazard, 3 ESCAPE, 4 timeout).
"""
import argparse, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim as S
import render_layout as RL
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle


def play_traced(ha, skill, rng, WPs):
    WP, WPM, nWP, CM = WPs
    PH = S.ph_array()
    sk = S.SKILLS[skill]
    x, y, z = ha.TEE
    strokes, out = 0, []
    for s in range(S.CAP):
        if strokes >= S.CAP:
            break
        b, bh, kb = S.support(ha.P, x, z, y + 0.01, PH[8], PH[7])
        zone = int(ha.pzone[b]) if b >= 0 else -1
        aim, v, ch = S.plan(ha.P, ha.pzone, ha.W, ha.nW, ha.CUP, WP, WPM, nWP, CM, PH, x, z, y, zone)
        aim += math.radians(sk["aim_sd"]) * rng.standard_normal()
        v = min(max(v * (1 + sk["pow_sd"] * rng.standard_normal()), 0.3), PH[3])
        path, r = S.trace_shot(ha, aim, v, rng.uniform(0, 600), start=(x, y, z))
        strokes += 1
        out.append(dict(path=path, outcome=int(r[3]), target=int(ch), v=v, zone=ha.zones[zone] if zone >= 0 else None))
        if r[3] == 1:
            break
        if r[3] in (2, 3):
            strokes += 1
        else:
            x, z, y = r[0], r[1], r[2]
    return strokes, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hole", type=int)
    ap.add_argument("skill")
    ap.add_argument("--k", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--bad-only", action="store_true")
    a = ap.parse_args()
    course = json.load(open(os.path.join(HERE, "..", "holes.json")))
    hole = next(h for h in course["holes"] if h["number"] == a.hole)
    ha = S.HoleArrays(hole)
    WPs = ha.waypoints(a.skill)
    rng = np.random.default_rng(a.seed)
    fig, ax = plt.subplots(figsize=(14, 14), dpi=90)
    for p in hole["felt"]:
        pts = RL.rect_corners(p["center"][0], p["center"][2], *p["size"], p["yaw"])
        ax.add_patch(Polygon(pts, fc="#9fd08a" if not p.get("overlay") else "#c9e6a0", ec="#2c5a1e", alpha=0.7))
    for w in hole["walls"]:
        ax.add_patch(Polygon(RL.rect_corners(w["center"][0], w["center"][2], w["size"][0], w["size"][2], w["yaw"]), fc="#5b4636"))
    for hz in hole.get("hazards", []):
        ax.add_patch(Polygon(RL.rect_corners(hz["center"][0], hz["center"][2], *hz["size"], 0), fc="#4aa3df", alpha=0.5))
    c = hole["cup"]["position"]
    ax.add_patch(Circle((c[0], c[2]), 0.5, fc="k"))
    cols = plt.cm.tab10.colors
    tally = {}
    shown = 0
    for k in range(a.k * (5 if a.bad_only else 1)):
        strokes, out = play_traced(ha, a.skill, rng, WPs)
        holed = out[-1]["outcome"] == 1
        tally[strokes if holed else "cap"] = tally.get(strokes if holed else "cap", 0) + 1
        if a.bad_only and strokes <= hole["par"] and holed:
            continue
        if shown >= a.k:
            continue
        shown += 1
        print(f"play {k}: {strokes} strokes, holed={holed}: " +
              " | ".join(f"{o['zone']}->t{o['target']} v{o['v']:.1f} oc{o['outcome']}" for o in out))
        for i, o in enumerate(out):
            pth = o["path"]
            ax.plot(pth[:, 0], pth[:, 2], color=cols[i % 10], lw=0.9, alpha=0.7)
            ax.plot(pth[-1, 0], pth[-1, 2], "o", color=cols[i % 10], ms=3)
            if o["outcome"] in (2, 3):
                ax.plot(pth[-1, 0], pth[-1, 2], "rx", ms=10, mew=2)
    print("tally", tally)
    ax.set_aspect("equal"); ax.autoscale_view(); ax.invert_yaxis(); ax.grid(alpha=0.3)
    ax.set_title(f"H{a.hole} {a.skill}: stroke1=blue, 2=orange, 3=green, 4=red ...  red x = hazard/escape")
    out = os.path.join(HERE, "out", f"debug-h{a.hole:02d}-{a.skill}.png")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
