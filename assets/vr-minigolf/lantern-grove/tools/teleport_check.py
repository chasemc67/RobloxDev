#!/usr/bin/env python3
"""Teleport exit check: launch the ball from every teleport exit at each speed in its clamp range
[min_speed, max_speed] and report what happens (holed / finish distance from the cup / rail contacts / fastest pass over the cup).

    python3 tools/teleport_check.py [--holes 8 9] [--json holes.json]

A good exit never sends a max-speed ball flying past the cup into a rail at speed: the "rail hit speed" column is the
ball speed at its first rail/blocker contact after the exit (0 = no contact).
"""
import argparse, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim as S


def run(hole, speeds=None):
    ha = S.HoleArrays(hole)
    PH = S.ph_array()
    cup = np.array(hole["cup"]["position"])
    rows = []
    for t in hole.get("teleports", []):
        ex = t["exit"]["center"]
        d = t["exit"]["dir"]
        sp = speeds or list(np.round(np.linspace(t["min_speed"], t["max_speed"], 10), 2))
        for v in sp:
            path = np.zeros((4000, 3))
            # start just past the exit with the cooldown already running: sim_shot starts at the exit point
            r = S.sim_shot(*ha.args(), PH, ex[0], ex[2], ex[1], v * d[0], v * d[1], 0.0, True, path)
            p = path[:r[6]]
            # speed along the path (6 steps per sample)
            vel = np.linalg.norm(np.diff(p[:, [0, 2]], axis=0), axis=1) / (6 * PH[12])
            dc = np.hypot(p[:, 0] - cup[0], p[:, 2] - cup[2])
            over = np.where(dc[:-1] < hole["cup"]["radius"])[0]
            pass_v = float(vel[over].max()) if len(over) else 0.0
            # first rail contact = first sample where the speed drops by > 20% in one sample
            jumps = np.where(vel[1:] < 0.8 * vel[:-1] - 0.2)[0]
            hit_v = float(vel[jumps[0]]) if len(jumps) else 0.0
            rows.append(dict(teleport=t["id"], v=float(v), outcome=int(r[3]), end=[round(r[0], 2), round(r[1], 2), round(r[2], 2)],
                             end_cup_dist=round(float(math.hypot(r[0] - cup[0], r[1] - cup[2])), 2),
                             min_cup_dist=round(float(r[5]), 2), pass_over_cup_speed=round(pass_v, 2),
                             first_contact_speed=round(hit_v, 2)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(HERE, "..", "holes.json"))
    ap.add_argument("--holes", type=int, nargs="*")
    a = ap.parse_args()
    course = json.load(open(a.json))
    oc_name = {0: "stopped", 1: "HOLED", 2: "hazard", 3: "ESCAPE", 4: "timeout", 5: "hazard->respawn"}
    for h in course["holes"]:
        if not h.get("teleports") or (a.holes and h["number"] not in a.holes):
            continue
        print(f"H{h['number']} {h['name']}: cup {h['cup']['position']}")
        print("| teleport | exit speed | outcome | finish (x,z) | finish to cup | closest to cup | speed over cup | first contact speed |")
        print("|---|---|---|---|---|---|---|---|")
        for r in run(h):
            print(f"| {r['teleport']} | {r['v']:.2f} | {oc_name[r['outcome']]} | ({r['end'][0]}, {r['end'][1]}) | {r['end_cup_dist']} | "
                  f"{r['min_cup_dist']} | {r['pass_over_cup_speed'] or '-'} | {r['first_contact_speed'] or '-'} |")


if __name__ == "__main__":
    main()
