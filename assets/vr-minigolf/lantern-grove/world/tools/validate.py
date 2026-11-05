"""Validate world.json against holes.json. Appends an iteration entry to world/validation.md.

usage: python3 tools/validate.py ["note describing what changed this iteration"]
exit code 0 = clean, 1 = failures.
"""
import datetime
import json
import math
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worldlib as W  # noqa: E402

MARGIN = 4.0          # min clearance between hole footprints
EYE = 5.5             # eye height above tee
TOL = 0.02
WALK_TARGET = 1500.0

world = W.load_world()
holes = W.load_holes()
HB = {h["number"]: h for h in holes["holes"]}
PL = {h["number"]: h["placement"] for h in world["holes"]}
rules = world["path_rules"]
tree = world["hollow_tree"]
TC = np.array([tree["center"][0], tree["center"][2]])

fails, warns, info = [], [], []


def H(x, z):
    return W.height_at(world, holes, np.asarray(x, float), np.asarray(z, float))


def hole_rects(n):
    return W.footprint_rects(HB[n], PL[n])


# ------------------------------------------------------------ 1. footprint overlap
foot = {n: hole_rects(n) for n in PL}
mind = {}
for a in PL:
    for b in PL:
        if b <= a:
            continue
        d = min(W.convex_overlap_dist(r1, r2) for r1 in foot[a] for r2 in foot[b])
        mind[(a, b)] = d
        if d < MARGIN:
            fails.append(f"overlap: H{a}-H{b} clearance {d:.2f} < {MARGIN}")
closest = sorted(mind.items(), key=lambda kv: kv[1])[:4]
info.append("closest hole pairs: " + ", ".join(f"H{a}-H{b} {d:.1f}" for (a, b), d in closest))

# tree vs holes
for n in PL:
    pts = np.array([c for r in foot[n] for c in r])
    dist = np.hypot(pts[:, 0] - TC[0], pts[:, 1] - TC[1])
    if n == 9:
        far = dist.max()
        room = tree["trunk_inner_radius"] - far
        info.append(f"H9 inside trunk: farthest footprint corner {far:.1f} from centre, inner radius {tree['trunk_inner_radius']:.1f} (walk room {room:.1f})")
        if room < 3.0:
            fails.append(f"H9 footprint not inside trunk interior with >=3 room (room {room:.2f})")
    else:
        # min distance of rects to the trunk circle
        dmin = min(float(W.poly_edge_dist(r, np.array(TC[0]), np.array(TC[1]))) if not W.poly_contains(r, np.array([TC[0]]), np.array([TC[1]]))[0] else 0.0 for r in foot[n])
        gap = dmin - tree["trunk_outer_radius"]
        if gap < 2.0:
            fails.append(f"H{n} footprint within {gap:.2f} of the trunk (need >= 2)")
        if n == 8:
            info.append(f"H8 to trunk gap {gap:.1f} (roots arch over the course)")

# ------------------------------------------------------------ 2. felt on/above terrain, water below felt
felt_report = {}
for n in PL:
    worst = -1e9
    worst_id = None
    wet_bad = 0
    for f in W.felt_world(HB[n], PL[n]):
        if f["overlay"]:
            continue
        us = np.linspace(-f["sx"] / 2 + 0.05, f["sx"] / 2 - 0.05, max(2, int(f["sx"] / 0.5) + 1))
        vs = np.linspace(-f["sz"] / 2 + 0.05, f["sz"] / 2 - 0.05, max(2, int(f["sz"] / 0.5) + 1))
        U, V = np.meshgrid(us, vs)
        a = math.radians(f["yaw"])
        x = f["cx"] + U * math.cos(a) + V * math.sin(a)
        z = f["cz"] - U * math.sin(a) + V * math.cos(a)
        top = W.felt_surface(f, x, z)
        h = H(x, z)
        exc = (h - (top - 0.4)).max()
        if exc > worst:
            worst, worst_id = exc, f["id"]
        ws = W.water_surface(world, holes, x, z)
        wet = np.isfinite(ws) & (ws > top - 0.4 + TOL)
        wet_bad += int(wet.sum())
    felt_report[n] = (worst, worst_id)
    if worst > TOL:
        fails.append(f"H{n} felt '{worst_id}' below terrain by {worst:.2f}")
    if wet_bad:
        fails.append(f"H{n} felt submerged at {wet_bad} sample points")
info.append("felt clearance (terrain - felt bottom, <=0 ok): " + ", ".join(f"H{n} {v[0]:+.2f}" for n, v in felt_report.items()))

# hazards: terrain under hazard is below its surface; water hazard levels agree with stream where they meet
for n in PL:
    for hz in HB[n]["hazards"]:
        c = W.to_world(PL[n], hz["center"])
        yaw = hz["yaw"] + PL[n]["yaw_deg"]
        us = np.linspace(-hz["size"][0] / 2 + 0.1, hz["size"][0] / 2 - 0.1, 9)
        vs = np.linspace(-hz["size"][1] / 2 + 0.1, hz["size"][1] / 2 - 0.1, 9)
        U, V = np.meshgrid(us, vs)
        a = math.radians(yaw)
        x = c[0] + U * math.cos(a) + V * math.sin(a)
        z = c[2] - U * math.sin(a) + V * math.cos(a)
        h = H(x, z)
        if (h > c[1] - 0.5).any():
            fails.append(f"H{n} hazard {hz['id']} terrain not below its surface (max {h.max():.2f} vs {c[1]:.2f})")
        if hz["type"] == "water":
            _, surf = W.water_profile(world, x, z)
            s = surf[np.isfinite(surf)]
            if s.size and np.abs(s - c[1]).max() > 0.15:
                fails.append(f"H{n} water hazard level {c[1]:.2f} disagrees with stream ({s.min():.2f}..{s.max():.2f})")
            elif s.size:
                info.append(f"H{n} water hazard {hz['id']} y={c[1]:.2f} joins Lantern Brook ({s.size}/81 samples on stream, level {s.mean():.2f})")
            else:
                info.append(f"H{n} water hazard {hz['id']} y={c[1]:.2f} is self-contained (fed by mill flume)" if n == 6 else
                            f"H{n} water hazard {hz['id']} y={c[1]:.2f} self-contained")

# stream monotonic
lv = [p["level"] for p in world["stream"]["points"]]
if any(b > a + 1e-6 for a, b in zip(lv, lv[1:])):
    fails.append("stream level increases downstream")

# ------------------------------------------------------------ 3. paths
total_walk = 0.0
path_lines = []
for p in world["paths"]:
    segs = p["segments"]
    pid = p["id"]
    if p["width"] < rules["min_width"]:
        fails.append(f"{pid}: width {p['width']} < {rules['min_width']}")
    # continuity
    for s1, s2 in zip(segs, segs[1:]):
        if math.dist(s1["end"], s2["start"]) > 0.05:
            fails.append(f"{pid}: gap between segments at {s1['end']}")
    # endpoints
    if p["from_hole"]:
        cw = W.to_world(PL[p["from_hole"]], HB[p["from_hole"]]["cup"]["position"])
        if math.dist(cw, segs[0]["start"]) > 0.1:
            fails.append(f"{pid}: does not start at H{p['from_hole']} cup")
    tw = W.to_world(PL[p["to_hole"]], HB[p["to_hole"]]["tee"]["position"])
    if math.dist(tw, segs[-1]["end"]) > 0.1:
        fails.append(f"{pid}: does not end at H{p['to_hole']} tee")
    max_g = 0.0
    max_rise = 0.0
    nsteps = 0
    prev_flight = False
    for i, s in enumerate(segs):
        L2 = W.segment_len2(s)
        dy = s["end"][1] - s["start"][1]
        if s["type"] in ("walk", "ramp", "landing", "bridge"):
            g = abs(dy) / L2 if L2 > 1e-6 else (0 if abs(dy) < 1e-3 else 9)
            max_g = max(max_g, g)
            if g > rules["max_ramp_grade"] + 1e-3:
                fails.append(f"{pid} seg{i} {s['type']} grade {g*100:.1f}% > 10%")
            if s["type"] == "landing" and prev_flight and L2 < rules["landing_length"] - 0.05 and i + 1 < len(segs) and segs[i + 1]["type"] == "stairs":
                fails.append(f"{pid} seg{i} landing {L2:.1f} < {rules['landing_length']}")
        if s["type"] == "stairs":
            if prev_flight:
                fails.append(f"{pid} seg{i}: two flights without a landing")
            r = abs(s["rise"])
            max_rise = max(max_rise, r)
            nsteps += s["steps"]
            if r > rules["max_step_rise"] + 1e-6:
                fails.append(f"{pid} seg{i}: step rise {r} > {rules['max_step_rise']}")
            if s["tread"] < 1.2:
                fails.append(f"{pid} seg{i}: tread {s['tread']:.2f} < 1.2 (leg too short for the climb)")
            if s["steps"] > rules["max_steps_per_flight"]:
                fails.append(f"{pid} seg{i}: {s['steps']} steps in one flight")
            if abs(s["steps"] * s["rise"] - dy) > 0.02 or abs(s["steps"] * s["tread"] - L2) > 0.05:
                fails.append(f"{pid} seg{i}: flight geometry inconsistent")
            prev_flight = True
        elif s["type"] != "landing" or L2 >= rules["landing_length"] - 0.05:
            prev_flight = False if s["type"] != "landing" or L2 >= rules["landing_length"] - 0.05 else prev_flight
        if s["type"] == "on_hole" and i not in (0, len(segs) - 1):
            fails.append(f"{pid} seg{i}: on_hole segment in the middle")
    # terrain agreement + clearance from holes + water + trunk
    xs, zs, ys, kinds = [], [], [], []
    for s in segs:
        if s["type"] in ("on_hole",):
            continue
        L = W.segment_len2(s)
        k = max(2, int(L / 1.0) + 1)
        t = np.linspace(0, 1, k)
        xs += list(s["start"][0] + (s["end"][0] - s["start"][0]) * t)
        zs += list(s["start"][2] + (s["end"][2] - s["start"][2]) * t)
        ys += list(s["start"][1] + (s["end"][1] - s["start"][1]) * t)
        kinds += [s["type"]] * k
    xs, zs, ys = map(np.array, (xs, zs, ys))
    kinds = np.array(kinds)
    h = H(xs, zs)
    stair = kinds == "stairs"
    dev = np.where(stair, h - (ys - world["terrain"]["path_grading"]["stair_bed_drop"]), h - ys)
    nonbridge = kinds != "bridge"
    bad = np.abs(dev[nonbridge]) > 0.75  # < one step
    if bad.any():
        j = np.argmax(np.abs(dev[nonbridge]))
        fails.append(f"{pid}: path surface off terrain by {dev[nonbridge][j]:+.2f} at ({xs[nonbridge][j]:.0f},{zs[nonbridge][j]:.0f}) [{int(bad.sum())} samples]")
    ws = W.water_surface(world, holes, xs, zs)
    wet = np.isfinite(ws) & nonbridge & (ws > h + 0.05)
    if wet.any():
        fails.append(f"{pid}: walkway runs through water at {int(wet.sum())} samples (needs a bridge)")
    for n in PL:
        rects = foot[n]
        dmin = np.full(xs.shape, np.inf)
        for r in rects:
            dmin = np.minimum(dmin, np.where(W.poly_contains(r, xs, zs), 0.0, W.poly_edge_dist(r, xs, zs)))
        if n in (p["from_hole"], p["to_hole"]):
            # may touch its own holes only near the ends (first/last 6 studs of walkway)
            cum = np.concatenate([[0], np.cumsum(np.hypot(np.diff(xs), np.diff(zs)))])
            mid = (cum > 6) & (cum < cum[-1] - 6)
            if (dmin[mid] < 0.5).any():
                fails.append(f"{pid}: crosses its own hole H{n} footprint mid-walk")
        else:
            need = p["width"] / 2 + 1.0
            if (dmin < need).any():
                fails.append(f"{pid}: passes within {dmin.min():.1f} of H{n} (need {need})")
    dt = np.hypot(xs - TC[0], zs - TC[1])
    if p["to_hole"] != 9:
        if (dt < tree["trunk_outer_radius"] + p["width"] / 2).any():
            fails.append(f"{pid}: runs into the hollow tree trunk")
    else:
        ang = np.degrees(np.arctan2(zs - TC[1], xs - TC[0]))
        wall = (dt > tree["trunk_inner_radius"] - 0.5) & (dt < tree["trunk_outer_radius"] + 0.5)
        da = np.abs((ang[wall] - tree["doorway"]["angle_deg"] + 180) % 360 - 180)
        half = math.degrees((tree["doorway"]["width"] / 2 - p["width"] / 2) / tree["trunk_outer_radius"])
        if (da > half).any():
            fails.append(f"{pid}: crosses the trunk wall outside the doorway (max {da.max():.1f} deg off, allowed {half:.1f})")
        if not wall.any():
            fails.append(f"{pid}: never passes through the trunk doorway")
    L3 = sum(W.segment_len3(s) for s in segs)
    if p["from_hole"]:
        total_walk += L3
    climb = segs[-1]["end"][1] - segs[0]["start"][1]
    path_lines.append(f"| {pid} | {p['name']} | {L3:.0f} | {climb:+.1f} | {max_g*100:.1f}% | {nsteps} | {max_rise:.2f} |")

if total_walk > WALK_TARGET:
    fails.append(f"total walk {total_walk:.0f} > {WALK_TARGET}")

# consecutive holes connected
for n in range(1, 9):
    if not any(p["from_hole"] == n and p["to_hole"] == n + 1 for p in world["paths"]):
        fails.append(f"no path H{n}->H{n+1}")
if not any(p["from_hole"] is None and p["to_hole"] == 1 for p in world["paths"]):
    fails.append("no path spawn->H1")

# spawn on terrain
sp = world["spawn"]["pos"]
hs = float(H(np.array([sp[0]]), np.array([sp[2]]))[0])
if abs(hs - sp[1]) > 0.6:
    fails.append(f"spawn y {sp[1]} vs terrain {hs:.2f}")

# ------------------------------------------------------------ 4. tree line of sight
los_lines = []
crown = tree["crown"]
base = tree["base_y"]
for n in range(1, 10):
    t = W.to_world(PL[n], HB[n]["tee"]["position"])
    eye = np.array([t[0], t[1] + EYE, t[2]])
    dxz = np.array([TC[0] - eye[0], TC[1] - eye[2]])
    dist = float(np.hypot(*dxz))
    if dist < tree["trunk_inner_radius"]:
        los_lines.append(f"| H{n} | {dist:.0f} | inside trunk | n/a | visible (looking up the hollow to the oculus at y {tree['oculus']['y']}) |")
        continue
    u = dxz / dist
    targets = {
        "upper trunk (75%)": np.array([TC[0] - u[0] * tree["trunk_outer_radius"], base + 0.75 * tree["trunk_height"], TC[1] - u[1] * tree["trunk_outer_radius"]]),
        "crown centre": np.array([TC[0], crown["center_y"], TC[1]]),
        "crown underside edge": np.array([TC[0] - u[0] * crown["radius_xz"] * 0.8, crown["center_y"] - crown["height"] * 0.35, TC[1] - u[1] * crown["radius_xz"] * 0.8]),
    }
    res = {}
    for name, tg in targets.items():
        L = math.dist(eye, tg)
        k = int(L / 1.0) + 2
        s = np.linspace(0, 1, k)
        px = eye[0] + (tg[0] - eye[0]) * s
        pz = eye[2] + (tg[2] - eye[2]) * s
        py = eye[1] + (tg[1] - eye[1]) * s
        # ignore samples inside the trunk/crown itself
        rr = np.hypot(px - TC[0], pz - TC[1])
        m = (rr > tree["trunk_outer_radius"] + 1) & (s * L > 3.0)
        ht = H(px[m], pz[m])
        clear = py[m] - ht
        res[name] = float(clear.min()) if clear.size else 99.0
    vis = [k for k, v in res.items() if v > 0.5]
    ok = "upper trunk (75%)" in vis or "crown centre" in vis
    if not ok:
        fails.append(f"H{n}: giant tree not visible from tee (min clearances {res})")
    los_lines.append(f"| H{n} | {dist:.0f} | {res['upper trunk (75%)']:.1f} | {res['crown centre']:.1f} | {'visible' if ok else 'BLOCKED'} ({', '.join(vis)}) |")

# ------------------------------------------------------------ report
status = "CLEAN" if not fails else f"{len(fails)} FAIL"
lines = []
lines.append(f"**Result: {status}.** Total walk H1->H9 cup-to-tee: **{total_walk:.0f} studs** ({total_walk*0.3:.0f} m), target < {WALK_TARGET:.0f}.")
if fails:
    lines.append("\nFailures:")
    lines += [f"- {f}" for f in fails]
lines.append("\nChecks:")
lines += [f"- {i}" for i in info]
lines.append("\n| path | name | length | climb | max ramp grade | steps | max rise |\n|---|---|---|---|---|---|---|")
lines += path_lines
lines.append("\n| tee | dist to trunk centre | LOS clearance upper trunk | LOS clearance crown | result |\n|---|---|---|---|---|")
lines += los_lines
report = "\n".join(lines)
print(report)

# append to validation.md
vpath = os.path.join(W.WORLD_DIR, "validation.md")
prev = open(vpath).read() if os.path.exists(vpath) else "# Lantern Grove world: validation log\n\nEach run of `tools/validate.py` appends an iteration.\n"
it = len(re.findall(r"^## Iteration ", prev, flags=re.M)) + 1
note = sys.argv[1] if len(sys.argv) > 1 else ""
entry = f"\n## Iteration {it} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
if note:
    entry += f"Changes: {note}\n\n"
entry += report + "\n"
with open(vpath, "w") as f:
    f.write(prev + entry)
with open(os.path.join(W.WORLD_DIR, "validation_latest.json"), "w") as f:
    json.dump(dict(iteration=it, clean=not fails, fails=fails, info=info, total_walk=round(total_walk, 1)), f, indent=1)
sys.exit(0 if not fails else 1)
