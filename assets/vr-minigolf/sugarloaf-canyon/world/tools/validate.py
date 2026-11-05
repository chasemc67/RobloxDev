"""Validate world.json (Sugarloaf Canyon, concept footprints). Appends an iteration entry to world/validation.md.
Adapted from lantern-grove/world/tools/validate.py.

usage: python3 tools/validate.py ["note describing what changed this iteration"]
exit code 0 = clean, 1 = failures.

Checks: footprint overlap (>= 4 studs), footprints on flat ground (pads flat, natural cut/fill <= 6, not under water, spans
really span something), paths (continuity, cup -> tee endpoints, grades, stairs, landings, lifts, bridges, terrain agreement,
water crossings, clearance from other holes, rails at drops), sun not in the eyes at any tee, Old Sugarloaf visible from every
open tee except H17/H18 (p8 Crown exemptions), walk length, teleport points, scenery clear of play, streams downhill,
reservoir held, spawn on terrain.
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
EYE = 5.5             # VR eye height above the tee
FLAT_TOL = 0.05       # pad flatness after grading
MAX_CUTFILL = 6.0     # natural terrain may differ from a pad by at most this much
SUN_MIN = 45.0        # min angle between a tee's play bearing and the sun bearing
WALK_TARGET = 3000.0  # walking (lifts/gondola excluded), spawn -> H18 cup
TERRAIN_TOL = 0.75    # walkway surface vs terrain (< one step)
SUGARLOAF_TEE_EXEMPTIONS = {17, 18}  # p8: preserve the dome and protected Crown foundations

world = W.load_world()
HOLES = {h["number"]: h for h in world["holes"]}
rules = world["path_rules"]
fails, warns, info = [], [], []


def H(x, z):
    return W.height_at(world, np.asarray(x, float), np.asarray(z, float))


def Hn(x, z):
    return W.height_natural(world, np.asarray(x, float), np.asarray(z, float))


PADS = {n: W.pads_world(h) for n, h in HOLES.items()}

# ------------------------------------------------------------ 1. footprint overlap
mind = {}
for a in HOLES:
    for b in HOLES:
        if b <= a:
            continue
        d = min(W.convex_overlap_dist(p["corners"], q["corners"]) for p in PADS[a] for q in PADS[b])
        mind[(a, b)] = d
        if d < MARGIN:
            fails.append(f"overlap: H{a}-H{b} clearance {d:.2f} < {MARGIN}")
closest = sorted(mind.items(), key=lambda kv: kv[1])[:5]
info.append("closest hole pairs: " + ", ".join(f"H{a}-H{b} {d:.1f}" for (a, b), d in closest))
bx, bz = world["bounds"]["x"], world["bounds"]["z"]
for n, pads in PADS.items():
    for p in pads:
        for (x, z) in p["corners"]:
            if not (bx[0] + 60 < x < bx[1] - 60 and bz[0] + 60 < z < bz[1] - 60):
                fails.append(f"H{n} footprint corner ({x:.0f},{z:.0f}) within 60 of the terrain edge")

# ------------------------------------------------------------ 2. footprints on flat ground
hole_lines = []
for n, h in HOLES.items():
    worst_dev = 0.0
    worst_cf = 0.0
    wet_bad = 0
    span_pts = 0
    span_min = None
    for p in PADS[n]:
        us = np.linspace(-p["sx"] / 2 + 0.25, p["sx"] / 2 - 0.25, max(3, int(p["sx"]) + 1))
        vs = np.linspace(-p["sz"] / 2 + 0.25, p["sz"] / 2 - 0.25, max(3, int(p["sz"]) + 1))
        U, V = np.meshgrid(us, vs)
        a = math.radians(p["yaw"])
        x = p["cx"] + U * math.cos(a) + V * math.sin(a)
        z = p["cz"] - U * math.sin(a) + V * math.cos(a)
        st = W.height_at(world, x, z, stages=True)
        sp = W.in_span(h, x, z)
        surf = st["water_surface"]
        carved = st["final"] < st["paths"] - 0.05          # cut by the river/creek carve
        ok = ~sp & ~carved
        span_pts += int(sp.sum())
        if sp.any():
            m = float(st["final"][sp].min())
            span_min = m if span_min is None else min(span_min, m)
        if ok.any():
            worst_dev = max(worst_dev, float(np.abs(st["final"][ok] - p["y"]).max()))
            worst_cf = max(worst_cf, float(np.abs(st["natural"][ok] - p["y"]).max()))
        wet = np.isfinite(surf) & ~sp & (surf > p["y"] - 0.3)
        wet_bad += int(wet.sum())
        if carved[~sp].any():
            fails.append(f"H{n} pad '{p['id']}' is cut by water outside a declared span ({int(carved[~sp].sum())} samples)")
    if worst_dev > FLAT_TOL:
        fails.append(f"H{n} pad not flat (max deviation {worst_dev:.2f})")
    if worst_cf > MAX_CUTFILL:
        fails.append(f"H{n} sits on uneven natural ground: cut/fill {worst_cf:.1f} > {MAX_CUTFILL} (cliff or slope under the footprint)")
    if wet_bad:
        fails.append(f"H{n} footprint under water at {wet_bad} samples")
    spans = h["concept"].get("spans") or []
    span_txt = "-"
    if spans:
        names = ", ".join(s["over"] for s in spans)
        gap = h["placement"]["origin"][1] - span_min if span_min is not None else 0
        span_txt = f"{names}: ground {gap:.1f} below the pad"
        if gap < 1.0:
            fails.append(f"H{n} declares a span over {names} but nothing is below it (gap {gap:.1f})")
    ys = sorted({round(p['y'], 1) for p in PADS[n]})
    hole_lines.append(f"| H{n} | {h['name']} | {h['par']} | {h['zone']} | {'/'.join(f'{y:g}' for y in ys)} | {worst_dev:.2f} | {worst_cf:.1f} | {span_txt} |")

# ------------------------------------------------------------ 2b. real hole geometry (holes.json) inside the footprints
HJ_PATH = os.path.join(W.WORLD_DIR, "..", "holes.json")
fit_lines = []
if os.path.exists(HJ_PATH):
    hjson = json.load(open(HJ_PATH))
    for hh in hjson["holes"]:
        n = hh["number"]
        pl = HOLES[n]["placement"]
        if [round(v, 3) for v in hh["world_offset"]] != [round(v, 3) for v in pl["origin"]] or abs(hh["world_yaw"] - pl["yaw_deg"]) > 1e-6:
            fails.append(f"H{n}: holes.json world_offset/yaw differ from world.json placement")
        pads = HOLES[n]["concept"]["pads"]

        def inside(x, z, tol=0.02):
            return any(p["x"][0] - tol <= x <= p["x"][1] + tol and p["z"][0] - tol <= z <= p["z"][1] + tol for p in pads)

        out_pts = 0
        npts = 0
        for kind, items in (("felt", hh["felt"]), ("wall", hh["walls"])):
            for it in items:
                sx, sz = (it["size"][0], it["size"][1]) if kind == "felt" else (it["size"][0], it["size"][2])
                for (x, z) in W.rect_corners(it["center"][0], it["center"][2], sx, sz, it.get("yaw", 0.0)):
                    npts += 1
                    out_pts += not inside(x, z)
        tee_ok = max(abs(v) for v in hh["tee"]["position"]) < 1e-6
        if out_pts:
            fails.append(f"H{n}: {out_pts} felt/rail corners of holes.json lie outside the world.json pads")
        if not tee_ok:
            fails.append(f"H{n}: holes.json tee is not at the local origin")
        cw = W.to_world(pl, hh["cup"]["position"])
        if math.dist(cw, HOLES[n]["cup_world_approx"]) > .02:
            fails.append(f"H{n}: world cup does not match holes.json XYZ")
        if math.dist(hh["cup"]["position"], HOLES[n]["concept"]["cup_local"]) > .02:
            fails.append(f"H{n}: concept cup does not match holes.json XYZ")
        fit_lines.append(f"| H{n} | {hh['name']} | {hh['par']} | {len(hh['felt'])} / {len(hh['walls'])} | {npts} | {out_pts} | "
                         f"({cw[0]:.1f}, {cw[1]:.1f}, {cw[2]:.1f}) |")
    info.append(f"holes.json: {len(hjson['holes'])} holes, total par {hjson['total_par']}; every felt and rail corner checked against the pads")
else:
    info.append("no holes.json yet: footprints are concept pads only")

# ------------------------------------------------------------ 3. paths
total_walk = 0.0
total_ride = 0.0
path_lines = []
seq = []
for p in world["paths"]:
    segs = p["segments"]
    pid = p["id"]
    seq.append((p["from_hole"], p["to_hole"]))
    if p["width"] < rules["min_width"]:
        fails.append(f"{pid}: width {p['width']} < {rules['min_width']}")
    for s1, s2 in zip(segs, segs[1:]):
        if math.dist(s1["end"], s2["start"]) > 0.05:
            fails.append(f"{pid}: gap between segments at {s1['end']}")
    if p["from_hole"]:
        cw = HOLES[p["from_hole"]]["cup_world_approx"]
        if math.dist(cw, segs[0]["start"]) > 0.1:
            fails.append(f"{pid}: does not start at H{p['from_hole']} cup")
        if segs[0]["type"] != "on_hole":
            fails.append(f"{pid}: first leg should be on_hole (leaving the green)")
    if p["to_hole"]:
        tw = HOLES[p["to_hole"]]["tee_world"]
        if math.dist(tw, segs[-1]["end"]) > 0.1:
            fails.append(f"{pid}: does not end at H{p['to_hole']} tee")
        # the walk-in point must sit just outside the tee end of the footprint
        e = segs[-1]["start"]
        d = min(float(W.rect_dist(np.array(e[0]), np.array(e[2]), q["cx"], q["cz"], q["sx"], q["sz"], q["yaw"])) for q in PADS[p["to_hole"]])
        if d > 6.0:
            fails.append(f"{pid}: walk-in point {d:.1f} from the H{p['to_hole']} footprint (> 6)")
    max_g, max_rise, nsteps, prev_flight = 0.0, 0.0, 0, False
    lift_txt = []
    for i, s in enumerate(segs):
        L2 = W.segment_len2(s)
        dy = s["end"][1] - s["start"][1]
        t = s["type"]
        if t in ("walk", "ramp", "landing"):
            g = abs(dy) / L2 if L2 > 1e-6 else (0 if abs(dy) < 1e-3 else 9)
            max_g = max(max_g, g)
            if g > rules["max_ramp_grade"] + 1e-3:
                fails.append(f"{pid} seg{i} {t} grade {g*100:.1f}% > {rules['max_ramp_grade']*100:.0f}%")
        if t in ("bridge", "dam_crest") and abs(dy) / max(L2, 1e-6) > 0.05:
            fails.append(f"{pid} seg{i} {t} slopes {abs(dy)/L2*100:.1f}% (> 5%)")
        if t == "stairs":
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
        elif t != "landing":
            prev_flight = False
        elif L2 >= rules["landing_length"] - 0.05:
            prev_flight = False
        if t == "on_hole" and i not in (0, len(segs) - 1):
            fails.append(f"{pid} seg{i}: on_hole segment in the middle")
        if t in ("lift", "gondola", "bridge", "dam_crest"):
            for end in (s["start"], s["end"]):
                hh = float(H(np.array([end[0]]), np.array([end[2]]))[0])
                if abs(hh - end[1]) > TERRAIN_TOL:
                    fails.append(f"{pid} seg{i} {t} end ({end[0]:.0f},{end[2]:.0f}) y {end[1]} vs terrain {hh:.1f}")
        if t == "lift":
            if abs(dy) > rules["max_lift_rise"]:
                fails.append(f"{pid} seg{i}: lift rise {abs(dy):.0f} > {rules['max_lift_rise']}")
            if L2 > rules["max_lift_offset"]:
                fails.append(f"{pid} seg{i}: lift boarding points {L2:.0f} apart (> {rules['max_lift_offset']})")
            lift_txt.append(f"{s.get('name')} {dy:+.0f}")
            total_ride += abs(dy)
        if t == "gondola":
            lift_txt.append(f"{s.get('name')} {dy:+.0f} over {L2:.0f}")
            total_ride += math.dist(s["start"], s["end"])
        if t in ("bridge", "dam_crest"):
            k = max(3, int(L2) + 1)
            tt = np.linspace(0.2, 0.8, k)
            xs_ = s["start"][0] + (s["end"][0] - s["start"][0]) * tt
            zs_ = s["start"][2] + (s["end"][2] - s["start"][2]) * tt
            under = float(H(xs_, zs_).min())
            lift_txt.append(f"{s.get('name')} {L2:.0f} long, {s['start'][1] - under:.0f} above ground")
            if s["start"][1] - under < 1.0:
                info.append(f"{pid}: {s.get('name')} spans nothing (could be a plain walk)")
    # rails at drops: recompute and compare with the flags
    for i, s in enumerate(segs):
        if s["type"] in ("on_hole", "lift", "gondola"):
            continue
        a, b = s["start"], s["end"]
        L = math.hypot(b[0] - a[0], b[2] - a[2])
        if L < 1e-6:
            continue
        ux, uz = (b[0] - a[0]) / L, (b[2] - a[2]) / L
        lx, lz = uz, -ux
        tt = np.linspace(0, 1, max(2, int(L / 1.5) + 1))
        px = a[0] + (b[0] - a[0]) * tt
        pz = a[2] + (b[2] - a[2]) * tt
        py = a[1] + (b[1] - a[1]) * tt
        for side, sg in (("left", 1), ("right", -1)):
            off = p["width"] / 2 + 2.5
            hh = H(px + sg * lx * off, pz + sg * lz * off)
            if (py - hh > rules["rail_drop"]).any() and side not in s.get("rails", []):
                fails.append(f"{pid} seg{i}: {side} side drops {float((py - hh).max()):.1f} but has no railing")
    # terrain agreement, water, other holes
    xs, zs, ys, kinds = [], [], [], []
    for s in segs:
        if s["type"] in ("on_hole", "lift", "gondola", "bridge", "dam_crest"):
            continue
        L = W.segment_len2(s)
        k = max(2, int(L / 1.0) + 1)
        tt = np.linspace(0, 1, k)
        xs += list(s["start"][0] + (s["end"][0] - s["start"][0]) * tt)
        zs += list(s["start"][2] + (s["end"][2] - s["start"][2]) * tt)
        ys += list(s["start"][1] + (s["end"][1] - s["start"][1]) * tt)
        kinds += [s["type"]] * k
    if xs:
        xs, zs, ys = map(np.array, (xs, zs, ys))
        kinds = np.array(kinds)
        hh = H(xs, zs)
        dev = np.where(kinds == "stairs", hh - (ys - world["terrain"]["path_grading"]["stair_bed_drop"]), hh - ys)
        bad = np.abs(dev) > TERRAIN_TOL
        if bad.any():
            j = int(np.argmax(np.abs(dev)))
            fails.append(f"{pid}: walkway off terrain by {dev[j]:+.2f} at ({xs[j]:.0f},{zs[j]:.0f}) [{int(bad.sum())} samples]")
        ws = W.water_surface(world, xs, zs)
        wet = np.isfinite(ws) & (ws > hh + 0.05)
        if wet.any():
            fails.append(f"{pid}: walkway runs through water at {int(wet.sum())} samples (needs a bridge)")
        for n in HOLES:
            dmin = np.full(xs.shape, np.inf)
            for q in PADS[n]:
                dmin = np.minimum(dmin, W.rect_dist(xs, zs, q["cx"], q["cz"], q["sx"], q["sz"], q["yaw"]))
            if n in (p["from_hole"], p["to_hole"]):
                cum = np.concatenate([[0], np.cumsum(np.hypot(np.diff(xs), np.diff(zs)))])
                mid = (cum > 6) & (cum < cum[-1] - 6)
                if (dmin[mid] < 0.5).any():
                    fails.append(f"{pid}: crosses its own hole H{n} footprint mid-walk")
            else:
                need = p["width"] / 2 + 1.0
                if (dmin < need).any():
                    fails.append(f"{pid}: passes within {dmin.min():.1f} of H{n} (need {need})")
    walk = sum(W.segment_len3(s) for s in segs if s["type"] not in ("lift", "gondola"))
    if p["to_hole"]:
        total_walk += walk
    climb = segs[-1]["end"][1] - segs[0]["start"][1]
    nrail = sum(1 for s in segs if s.get("rails"))
    path_lines.append(f"| {pid} | {p['name']} | {walk:.0f} | {climb:+.1f} | {max_g*100:.1f}% | {nsteps} | {max_rise:.2f} | {nrail} | {'; '.join(lift_txt) or '-'} |")

if total_walk > WALK_TARGET:
    fails.append(f"total walk {total_walk:.0f} > {WALK_TARGET}")
need = [(None, 1)] + [(n, n + 1) for n in range(1, 18)] + [(18, None)]
for pair in need:
    if pair not in seq:
        fails.append(f"no path {pair[0]} -> {pair[1]}")

sp = world["spawn"]["pos"]
hs = float(H(np.array([sp[0]]), np.array([sp[2]]))[0])
if abs(hs - sp[1]) > 0.6:
    fails.append(f"spawn y {sp[1]} vs terrain {hs:.2f}")

# ------------------------------------------------------------ 4. sun not in the eyes
sun = world["sun"]
sun_lines = []
for n, h in HOLES.items():
    pb = h["play_bearing_deg"]
    diff = abs((pb - sun["bearing_deg"] + 180) % 360 - 180)
    ok = diff >= SUN_MIN
    if not ok:
        fails.append(f"H{n} tee plays toward the sun (bearing {pb:.0f}, sun {sun['bearing_deg']:.0f}, {diff:.0f} deg apart)")
    sun_lines.append((n, pb, diff, ok))

# ------------------------------------------------------------ 5. Old Sugarloaf line of sight
lm = next(r for r in world["terrain"]["regions"] if r["id"] == "old_sugarloaf")
LX, LZ = lm["center"][0], lm["center"][-1]
summit = float(H(np.array([LX]), np.array([LZ]))[0])
los_lines = []
for n, h in HOLES.items():
    t = h["tee_world"]
    eye = np.array([t[0], t[1] + EYE, t[2]])
    dist = math.hypot(LX - eye[0], LZ - eye[2])
    u = np.array([LX - eye[0], LZ - eye[2]]) / dist
    res = {}
    for name, frac in (("summit", 0.0), ("upper dome", 0.35)):
        r_ = lm["radius"] * frac
        tg = np.array([LX - u[0] * r_, 0, LZ - u[1] * r_])
        tg[1] = float(H(np.array([tg[0]]), np.array([tg[2]]))[0]) - 1.0
        L = math.dist(eye, tg)
        k = int(L / 1.0) + 2
        s = np.linspace(0, 1, k)
        px, py, pz = (eye[0] + (tg[0] - eye[0]) * s, eye[1] + (tg[1] - eye[1]) * s, eye[2] + (tg[2] - eye[2]) * s)
        m = (np.hypot(px - LX, pz - LZ) > lm["radius"] * 0.9) & (s * L > 3.0)
        clear = py[m] - H(px[m], pz[m])
        res[name] = float(clear.min()) if clear.size else 99.0
    vis = max(res.values()) > 0.5
    if n in SUGARLOAF_TEE_EXEMPTIONS:
        result = f"{'visible' if vis else 'hidden'} (p8 visibility exemption)"
    elif not vis:
        if h.get("enclosed"):
            warns.append(f"H{n} (slot canyon, enclosed by design): Old Sugarloaf hidden from the tee")
            result = "hidden (slot canyon)"
        else:
            fails.append(f"H{n}: Old Sugarloaf not visible from the tee ({res})")
            result = "BLOCKED"
    else:
        result = "visible"
    los_lines.append(f"| H{n} | {dist:.0f} | {res['summit']:+.1f} | {res['upper dome']:+.1f} | "
                     f"{result} |")
info.append("p8: H17/H18 tees are exempt from Old Sugarloaf visibility; measured sightlines remain reported, dome unchanged")

# ------------------------------------------------------------ 6. teleport points, scenery, water
for tp in world["teleport_points"]:
    x, y, z = tp["pos"]
    hh = float(H(np.array([x]), np.array([z]))[0])
    ring = H(x + 3 * np.cos(np.linspace(0, 2 * np.pi, 8, endpoint=False)), z + 3 * np.sin(np.linspace(0, 2 * np.pi, 8, endpoint=False)))
    if tp.get("support_box"):
        # A built landing, not underlying eroded shoreline, supports these teleports.
        box = next((b for b in world["dam"]["crest_walk"]["boxes"] if b["id"] == tp["support_box"]), None)
        if box is None or not box.get("collidable") or box.get("yaw_deg", 0) != 0:
            fails.append(f"teleport {tp['id']}: invalid collidable landing support")
        else:
            cx, cy, cz = box["center"]
            sx, sy, sz = box["size"]
            if abs(x-cx)+3 > sx/2 or abs(z-cz)+3 > sz/2:
                fails.append(f"teleport {tp['id']}: standing ring outside landing")
            hh = cy + sy/2
            ring = np.full(8, hh)
    if abs(hh - y) > 0.6:
        fails.append(f"teleport {tp['id']}: y {y} vs standing surface {hh:.1f}")
    if np.abs(ring - hh).max() > 0.6:
        fails.append(f"teleport {tp['id']}: ground not flat (+-{np.abs(ring - hh).max():.1f} within 3 studs)")
    dpath = min(float(W.seg_dist(np.array(x), np.array(z), (s["start"][0], s["start"][2]), (s["end"][0], s["end"][2]))[0])
                for p in world["paths"] for s in p["segments"] if s["type"] not in ("gondola",))
    if dpath > 14:
        fails.append(f"teleport {tp['id']}: {dpath:.0f} studs from the nearest walkway")
    for n in HOLES:
        for q in PADS[n]:
            if float(W.rect_dist(np.array(x), np.array(z), q["cx"], q["cz"], q["sx"], q["sz"], q["yaw"])) < 3:
                fails.append(f"teleport {tp['id']} inside/next to H{n}")
info.append(f"{len(world['teleport_points'])} teleport points checked (on flat ground or verified collidable landing, <= 14 from a walkway, clear of holes)")

nsc = 0
for pc in world["backdrop"]["pieces"]:
    if pc["kind"] not in ("hoodoo_spire", "rock_candy_crystal", "lollipop_cactus"):
        continue
    nsc += 1
    x, _, z = pc["pos"]
    r = pc["size"][0] / 2
    for n in HOLES:
        for q in PADS[n]:
            if float(W.rect_dist(np.array(x), np.array(z), q["cx"], q["cz"], q["sx"], q["sz"], q["yaw"])) < r + 2:
                fails.append(f"scenery {pc['id']} on H{n}")
info.append(f"{nsc} small scenery pieces clear of every footprint")

for st in world["streams"]:
    lv = [q["level"] for q in st["points"]]
    if any(b > a + 1e-6 for a, b in zip(lv, lv[1:])):
        fails.append(f"stream {st['name']} level increases downstream")
lk = world["lakes"][0]
th = np.linspace(0, 2 * np.pi, 360, endpoint=False)
rr = 1 + (lk["beach_width"] + 3) / min(lk["radii"])
rx = lk["center"][0] + lk["radii"][0] * rr * np.cos(th)
rz = lk["center"][1] + lk["radii"][1] * rr * np.sin(th)
rim = H(rx, rz)
dam = world["dam"]
atdam = (rx > dam["x"][0]) & (rx < dam["x"][1]) & (rz > dam["z_center"] - 12)
inflow = np.isfinite(W.water_surface(world, rx, rz))      # a creek mouth flowing in
leak = (rim < lk["level"] + 0.5) & ~atdam & ~inflow
if leak.any():
    fails.append(f"reservoir rim below water level at {int(leak.sum())} of 360 points (outside the dam)")
info.append(f"reservoir rim min {float(rim[~atdam & ~inflow].min()):.1f} ({int(inflow.sum())} ring points are the Fizzwater Creek mouth) (water {lk['level']}); held by the dam over x {dam['x'][0]:.0f}..{dam['x'][1]:.0f}")
info.append(f"Old Sugarloaf summit y {summit:.1f}")

# ------------------------------------------------------------ report
status = "CLEAN" if not fails else f"{len(fails)} FAIL"
L = []
L.append(f"**Result: {status}** ({len(warns)} warnings). Walking spawn -> H18 cup: **{total_walk:.0f} studs** ({total_walk*0.3:.0f} m, "
         f"target < {WALK_TARGET:.0f}); lifts {sum(1 for p in world['paths'] for s in p['segments'] if s['type']=='lift')} "
         f"(ride {total_ride:.0f} studs incl. the gondola home).")
if fails:
    L.append("\nFailures:")
    L += [f"- {f}" for f in fails]
if warns:
    L.append("\nWarnings:")
    L += [f"- {w}" for w in warns]
L.append("\nChecks:")
L += [f"- {i}" for i in info]
L.append("\n| hole | name | par | zone | pad y | pad flat dev | natural cut/fill | span |\n|---|---|---|---|---|---|---|---|")
L += hole_lines
if fit_lines:
    L.append("\n| hole | name | par | felt / walls | corners checked | outside pads | cup (world) |\n|---|---|---|---|---|---|---|")
    L += fit_lines
L.append("\n| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |\n|---|---|---|---|---|---|---|---|---|")
L += path_lines
L.append(f"\n| hole | play bearing | angle to sun ({sun['bearing_deg']:g}) | ok |\n|---|---|---|---|")
L += [f"| H{n} | {pb:.0f} | {d:.0f} | {'ok' if ok else 'SUN IN EYES'} |" for n, pb, d, ok in sun_lines]
L.append("\n| tee | dist to Old Sugarloaf | LOS clearance summit | LOS clearance upper dome | result |\n|---|---|---|---|---|")
L += los_lines
report = "\n".join(L)
print(report)

vpath = os.path.join(W.WORLD_DIR, "validation.md")
prev = open(vpath).read() if os.path.exists(vpath) else ("# Sugarloaf Canyon world: validation log\n\nEach run of `tools/validate.py` appends an iteration. "
                                                         "Holes are concept footprints (no holes.json yet).\n")
it = len(re.findall(r"^## Iteration ", prev, flags=re.M)) + 1
note = sys.argv[1] if len(sys.argv) > 1 else ""
entry = f"\n## Iteration {it} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
if note:
    entry += f"Changes: {note}\n\n"
entry += report + "\n"
with open(vpath, "w") as f:
    f.write(prev + entry)
with open(os.path.join(W.WORLD_DIR, "validation_latest.json"), "w") as f:
    json.dump(dict(iteration=it, clean=not fails, fails=fails, warns=warns, info=info, total_walk=round(total_walk, 1)), f, indent=1)
sys.exit(0 if not fails else 1)
