"""Validate world.json (Aurora Archipelago, concept footprints). Appends an iteration entry to world/validation.md.
Adapted from sugarloaf-canyon/world/tools/validate.py.

usage: python3 world/tools/validate.py ["Changes: what changed this iteration"]
exit code 0 = clean, 1 = failures.

Checks:
  footprints   no overlap (>= 4 studs), inside bounds, pads flat after grading, natural cut/fill <= 6, not under water, not over the
               void, spans really span open sky, span player guards + railed decks
  walkways     continuity, cup -> tee endpoints, walk-in point, grades, stairs/flights/landings, lift/bridge/gondola ends on terrain,
               surface within 0.75 of the terrain, never over the void or water unless bridged, clearance from other holes, own hole
  railings     rails on every walkway side where the ground drops > 4 within 1-5.5 studs (rail_reach) of the edge, bridges railed both sides at
               >= railing_height, pad edges next to a drop, teleport pads and viewpoints next to a drop have parapets
  head room    >= 8 studs clear over every pad and walkway: backdrop pieces (arches use clear_height), other walkways/bridges passing
               overhead, the gondola cable (cabin hangs 6 below it) and lantern posts (never over the walkway)
  comfort      no tee within 45 deg of the moon; lifts <= 4 studs/s, railed, teleport alternative; gondola <= 6 studs/s; teleport pad at
               every zone hub; next-tee teleport pad flat behind every tee; respawn plane below all walkable ground
  view         Starfrost Spire line of sight from every tee eye (tee + 5.5)
  flow         consecutive holes connected; spawn -> H1 and H18 -> hub; total walk < 3000
  variety      one headline gimmick per hole, no repeats; every mover has its own motion type
  world props  teleports flat and near walkways; scenery clear of footprints and walkways; streams downhill; lagoons held by their rim
               (except the runoff mouth); spawn on terrain
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
MOON_MIN = 45.0       # min angle between a tee's play bearing and the moon bearing
WALK_TARGET = 3000.0  # walking (lifts/gondola excluded), spawn -> H18 cup
TERRAIN_TOL = 0.75    # walkway surface vs terrain (< one step)
CABIN_DROP = 6.0      # gondola cabin hangs this far below the cable

world = W.load_world()
HOLES = {h["number"]: h for h in world["holes"]}
rules = world["path_rules"]
VOID = world["void"]
HEAD = rules["head_clearance"]
fails, warns, info = [], [], []


def H(x, z):
    return W.height_at(world, np.asarray(x, float), np.asarray(z, float))


PADS = {n: W.pads_world(h) for n, h in HOLES.items()}

# ------------------------------------------------------------ 1. footprint overlap + bounds
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

# ------------------------------------------------------------ 2. footprints on flat ground, spans, pad-edge parapets
hole_lines = []
edge_lines = []
for n, h in HOLES.items():
    worst_dev = worst_cf = 0.0
    wet_bad = 0
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
        carved = st["final"] < st["paths"] - 0.05
        ok = ~sp & ~carved
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
        if p["y"] < VOID["respawn_plane_y"] + 10:
            fails.append(f"H{n} pad '{p['id']}' y {p['y']} is not >= 10 above the respawn plane")
    if worst_dev > FLAT_TOL:
        fails.append(f"H{n} pad not flat (max deviation {worst_dev:.2f})")
    if worst_cf > MAX_CUTFILL:
        fails.append(f"H{n} sits on uneven natural ground: cut/fill {worst_cf:.1f} > {MAX_CUTFILL} (cliff, void or slope under the footprint)")
    if wet_bad:
        fails.append(f"H{n} footprint under water at {wet_bad} samples")
    spans = h["concept"].get("spans") or []
    span_txt = "-"
    if spans:
        names = ", ".join(s["over"] for s in spans)
        gap = h["placement"]["origin"][1] - span_min if span_min is not None else 0
        span_txt = f"{names}: ground {gap:.0f} below the pad"
        if gap < 1.0:
            fails.append(f"H{n} declares a span over {names} but nothing is below it (gap {gap:.1f})")
        for s in spans:
            g, d = s.get("player_guard"), s.get("player_deck")
            if not g or g.get("height", 0) < 3.5:
                fails.append(f"H{n} span '{s['over']}' has no player guard >= 3.5 on its rims")
            if not d or d.get("rails") != "both" or d.get("width", 0) < 4 or d.get("rail_height", 0) < rules["railing_height"]:
                fails.append(f"H{n} span '{s['over']}' has no railed player deck (width >= 4, rails both sides)")
    # pad-edge parapets: walk each pad side 2.5 studs outside; a drop > rail_drop needs a parapet on that side
    need_sides = set()
    for p in PADS[n]:
        a = math.radians(p["yaw"])
        for side, (du, dv) in (("left", (-1, 0)), ("right", (1, 0)), ("tee", (0, 1)), ("far", (0, -1))):
            if du:
                vs = np.linspace(-p["sz"] / 2, p["sz"] / 2, int(p["sz"]) + 1)
                us = np.full_like(vs, du * (p["sx"] / 2 + 2.5))
            else:
                us = np.linspace(-p["sx"] / 2, p["sx"] / 2, int(p["sx"]) + 1)
                vs = np.full_like(us, dv * (p["sz"] / 2 + 2.5))
            x = p["cx"] + us * math.cos(a) + vs * math.sin(a)
            z = p["cz"] - us * math.sin(a) + vs * math.cos(a)
            inside_other = np.zeros(x.shape, bool)
            for q in PADS[n]:
                inside_other |= W.in_rect(x, z, q["cx"], q["cz"], q["sx"], q["sz"], q["yaw"], grow=0.01)
            m = ~W.in_span(h, x, z) & ~inside_other
            if m.any() and (p["y"] - H(x[m], z[m]) > rules["rail_drop"]).any():
                need_sides.add(side)
    have = set(h.get("comfort", {}).get("edge_parapets", []))
    if need_sides - have:
        fails.append(f"H{n} pad edges {sorted(need_sides - have)} sit next to a drop > {rules['rail_drop']} without a parapet")
    edge_lines.append((n, sorted(need_sides), bool(spans)))
    ys = sorted({round(p['y'], 1) for p in PADS[n]})
    hole_lines.append(f"| H{n} | {h['name']} | {h['par']} | {h['zone']} | {'/'.join(f'{y:g}' for y in ys)} | {worst_dev:.2f} | {worst_cf:.1f} | {span_txt} |")
info.append("pad edges next to a drop > 4 (2.5 studs out): " +
            (", ".join(f"H{n} {s}" for n, s, _ in edge_lines if s) or "none (every pad has >= 11 studs of island apron)") +
            "; spans are guarded by their player guards and decks")

# ------------------------------------------------------------ 3. paths
total_walk = total_ride = 0.0
path_lines = []
seq = []
walk_samples = []     # (x, z, y, path id, segment index, width, station) for head-room checks
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
        e = segs[-1]["start"]
        d = min(float(W.rect_dist(np.array(e[0]), np.array(e[2]), q["cx"], q["cz"], q["sx"], q["sz"], q["yaw"])) for q in PADS[p["to_hole"]])
        if d > 6.0:
            fails.append(f"{pid}: walk-in point {d:.1f} from the H{p['to_hole']} footprint (> 6)")
        u, v = W.hole_local(HOLES[p["to_hole"]], np.array(e[0]), np.array(e[2]))
        if float(v) < 6.0:
            fails.append(f"{pid}: walk-in point is not behind the H{p['to_hole']} tee (local z {float(v):.1f} < 6)")
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
        if t in ("bridge", "deck") and abs(dy) / max(L2, 1e-6) > 0.05:
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
        if t in ("lift", "gondola", "bridge", "deck"):
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
        if t in ("bridge", "deck"):
            k = max(3, int(L2) + 1)
            tt = np.linspace(0.2, 0.8, k)
            xs_ = s["start"][0] + (s["end"][0] - s["start"][0]) * tt
            zs_ = s["start"][2] + (s["end"][2] - s["start"][2]) * tt
            under = float(H(xs_, zs_).min())
            lift_txt.append(f"{s.get('name')} ({s.get('style', '-')}) {L2:.0f} long, {s['start'][1] - under:.0f} above ground")
            if s["start"][1] - under < 1.0:
                info.append(f"{pid}: {s.get('name')} spans nothing (could be a plain walk)")
            if sorted(s.get("rails", [])) != ["left", "right"] or s.get("railing_height", 0) < rules["railing_height"]:
                fails.append(f"{pid} seg{i} {t}: bridges need railings on both sides >= {rules['railing_height']} high")
    # rails at drops: recompute and compare with the flags (1.0 .. rail_reach studs beyond the edge)
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
            worst = max(float((py - H(px + sg * lx * off, pz + sg * lz * off)).max()) for off in [p["width"] / 2 + o for o in (1.0, 2.5, 4.0, rules.get("rail_reach", 2.5))])
            if worst > rules["rail_drop"]:
                if side not in s.get("rails", []):
                    fails.append(f"{pid} seg{i}: {side} side drops {worst:.1f} but has no railing")
                elif s.get("railing_height", 0) < rules["railing_height"]:
                    fails.append(f"{pid} seg{i}: {side} railing lower than {rules['railing_height']}")
    # terrain agreement, void, water, other holes
    xs, zs, ys, kinds = [], [], [], []
    station = 0.0
    for i, s in enumerate(segs):
        s["_station"] = station
        station += W.segment_len2(s)
        if s["type"] in ("lift", "gondola"):
            continue
        L = W.segment_len2(s)
        k = max(2, int(L / 1.0) + 1)
        tt = np.linspace(0, 1, k)
        sx_ = s["start"][0] + (s["end"][0] - s["start"][0]) * tt
        sz_ = s["start"][2] + (s["end"][2] - s["start"][2]) * tt
        sy_ = s["start"][1] + (s["end"][1] - s["start"][1]) * tt
        if s["type"] != "on_hole":
            walk_samples += [(x_, z_, y_, pid, i, p["width"], s["_station"] + tt_ * W.segment_len2(s)) for x_, z_, y_, tt_ in zip(sx_, sz_, sy_, tt)]
        if s["type"] in ("on_hole", "bridge", "deck"):
            continue
        xs += list(sx_)
        zs += list(sz_)
        ys += list(sy_)
        kinds += [s["type"]] * k
    if xs:
        xs, zs, ys = map(np.array, (xs, zs, ys))
        kinds = np.array(kinds)
        hh = H(xs, zs)
        if (hh < VOID["terrain_fill_min_y"]).any():
            fails.append(f"{pid}: walkway over the cloud-floor void at {int((hh < VOID['terrain_fill_min_y']).sum())} samples (needs a bridge)")
        dev = np.where(kinds == "stairs", hh - (ys - world["terrain"]["path_grading"]["stair_bed_drop"]), hh - ys)
        bad = np.abs(dev) > TERRAIN_TOL
        if bad.any():
            j = int(np.argmax(np.abs(dev)))
            fails.append(f"{pid}: walkway off terrain by {dev[j]:+.2f} at ({xs[j]:.0f},{zs[j]:.0f}) [{int(bad.sum())} samples]")
        ws = W.water_surface(world, xs, zs)
        wet = np.isfinite(ws) & (ws > hh + 0.05)
        if wet.any():
            fails.append(f"{pid}: walkway runs through water at {int(wet.sum())} samples (needs a bridge)")
        if (ys < VOID["respawn_plane_y"] + 10).any():
            fails.append(f"{pid}: walkway within 10 of the respawn plane")
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

# ------------------------------------------------------------ 4. head clearance (>= 8 studs over felt and walkways)
surf_pts = []   # (x, z, y, label, width-ish radius)
for n in HOLES:
    for p in PADS[n]:
        us = np.arange(-p["sx"] / 2, p["sx"] / 2 + 0.01, 2.0)
        vs = np.arange(-p["sz"] / 2, p["sz"] / 2 + 0.01, 2.0)
        U, V = np.meshgrid(us, vs)
        a = math.radians(p["yaw"])
        X = p["cx"] + U * math.cos(a) + V * math.sin(a)
        Z = p["cz"] - U * math.sin(a) + V * math.cos(a)
        surf_pts += [(x, z, p["y"], f"H{n} felt", 0.0) for x, z in zip(X.ravel(), Z.ravel())]
surf_pts += [(x, z, y, f"walkway {pid}", w / 2 + 0.75) for (x, z, y, pid, i, w, st_) in walk_samples]
SPID = np.array([""] * sum(1 for s in surf_pts if s[3].endswith("felt")) + [q[3] for q in walk_samples], dtype=object)
SSTA = np.array([0.0] * sum(1 for s in surf_pts if s[3].endswith("felt")) + [q[6] for q in walk_samples])
SX = np.array([s[0] for s in surf_pts])
SZ = np.array([s[1] for s in surf_pts])
SY = np.array([s[2] for s in surf_pts])
SR = np.array([s[4] for s in surf_pts])
SL = [s[3] for s in surf_pts]
head_hits = []
n_checked = 0
for pc in world["backdrop"]["pieces"]:
    if pc.get("walk_through") or pc.get("below_terrain") or pc["kind"] in ("sky", "cloud", "cloud_ring", "far_island", "far_silhouette", "sister_landmark"):
        continue
    x, y0, z = pc["pos"]
    sx, sy, sz = pc["size"]
    near = W.rect_dist(SX, SZ, x, z, sx, sz, pc.get("yaw_deg", 0.0)) <= SR
    if not near.any():
        continue
    n_checked += 1
    lo = y0 + pc.get("clear_height", 0.0)
    hi = y0 + sy
    bad = near & (lo < SY + HEAD) & (hi > SY)
    if bad.any():
        j = int(np.argmax(bad))
        head_hits.append(f"{pc['id']} ({pc['kind']}) intrudes into the 8-stud head room over {SL[j]} at ({SX[j]:.0f},{SZ[j]:.0f})")
# walkways / bridges passing over other surfaces
for p in world["paths"]:
    for i, s in enumerate(p["segments"]):
        if s["type"] in ("on_hole", "lift", "gondola"):
            continue
        d, t = W.seg_dist(SX, SZ, (s["start"][0], s["start"][2]), (s["end"][0], s["end"][2]))
        ys_ = s["start"][1] + (s["end"][1] - s["start"][1]) * t
        own = (SPID == p["id"]) & (SSTA > s["_station"] - 3 * p["width"]) & (SSTA < s["_station"] + W.segment_len2(s) + 3 * p["width"])
        over = ~own & (d <= p["width"] / 2 + SR + 0.5) & (ys_ - 1.0 > SY + 0.5) & (ys_ - 1.0 < SY + HEAD)
        if over.any():
            j = int(np.argmax(over))
            head_hits.append(f"{p['id']} seg{i} passes {ys_[j] - SY[j]:.1f} over {SL[j]} at ({SX[j]:.0f},{SZ[j]:.0f})")
# gondola cable: cabin bottom = cable - CABIN_DROP must stay >= 8 over walked surfaces and terrain
cable_txt = []
for l in world["lifts"]:
    if l["type"] != "gondola":
        continue
    a, b = l["top"], l["bottom"]
    ch = l.get("cable_height_above_station", 14.0)
    d, t = W.seg_dist(SX, SZ, (a[0], a[2]), (b[0], b[2]))
    cy = a[1] + ch + (b[1] - a[1]) * t
    m = (d < 6.0) & (t > 0.02) & (t < 0.98)
    if m.any() and ((cy - CABIN_DROP - SY)[m] < HEAD).any():
        j = int(np.argmax(m & (cy - CABIN_DROP - SY < HEAD)))
        head_hits.append(f"{l['name']} cabin passes {cy[j] - CABIN_DROP - SY[j]:.1f} over {SL[j]} (< {HEAD})")
    L = math.hypot(b[0] - a[0], b[2] - a[2])
    tt = np.linspace(0.03, 0.97, int(L / 2))
    gx, gz = a[0] + (b[0] - a[0]) * tt, a[2] + (b[2] - a[2]) * tt
    gy = a[1] + ch + (b[1] - a[1]) * tt - CABIN_DROP
    clr = gy - H(gx, gz)
    if clr.min() < HEAD:
        head_hits.append(f"{l['name']} cabin only {clr.min():.1f} over terrain")
    cable_txt.append(f"{l['name']}: min cabin clearance over terrain {clr.min():.0f}, over walked surfaces "
                     f"{float(np.min(np.where(m, cy - CABIN_DROP - SY, 999))):.0f}")
# lantern posts: never over the walkway itself
lp = world.get("lantern_posts", {})
for q in lp.get("positions", []):
    x, y, z = q["pos"]
    path = next(p for p in world["paths"] if p["id"] == q["path"])
    for s in path["segments"]:
        if s["type"] in ("on_hole", "lift", "gondola"):
            continue
        d, _ = W.seg_dist(np.array(x), np.array(z), (s["start"][0], s["start"][2]), (s["end"][0], s["end"][2]))
        if float(d) < path["width"] / 2 + 0.5 - 1e-6:
            head_hits.append(f"lantern post at ({x:.0f},{z:.0f}) stands on walkway {q['path']}")
            break
fails += head_hits
info.append("island_underside meshes are fitted inside their island's cliff outline, below its top (below_terrain), so they are not head-room objects")
info.append(f"head room: {len(SX)} felt/walkway samples vs {n_checked} nearby backdrop pieces, overhead walkways, the gondola cabin and "
            f"{len(lp.get('positions', []))} lantern posts; {len(head_hits)} intrusions. " + "; ".join(cable_txt))

# ------------------------------------------------------------ 5. moon not in the eyes
moon = world["moon"]
moon_lines = []
for n, h in HOLES.items():
    pb = h["play_bearing_deg"]
    diff = abs((pb - moon["bearing_deg"] + 180) % 360 - 180)
    ok = diff >= MOON_MIN
    if not ok:
        fails.append(f"H{n} tee plays toward the moon (bearing {pb:.0f}, moon {moon['bearing_deg']:.0f}, {diff:.0f} deg apart)")
    moon_lines.append((n, pb, diff, ok))

# ------------------------------------------------------------ 6. Starfrost Spire line of sight
spire = next(pc for pc in world["backdrop"]["pieces"] if pc["id"] == "starfrost_spire")
LX, LY, LZ = spire["pos"]
LH = spire["size"][1]
targets = (("tip", LY + LH), ("upper", LY + 0.6 * LH), ("waist", LY + 0.3 * LH))
los_lines = []
for n, h in HOLES.items():
    t = h["tee_world"]
    eye = np.array([t[0], t[1] + EYE, t[2]])
    dist = math.hypot(LX - eye[0], LZ - eye[2])
    res = {}
    for name, ty in targets:
        L = math.dist(eye, (LX, ty, LZ))
        k = int(L / 1.0) + 2
        s = np.linspace(0, 1, k)
        px, py, pz = eye[0] + (LX - eye[0]) * s, eye[1] + (ty - eye[1]) * s, eye[2] + (LZ - eye[2]) * s
        m = (np.hypot(px - LX, pz - LZ) > spire["size"][0] / 2) & (s * L > 3.0)
        clear = py[m] - H(px[m], pz[m])
        res[name] = float(clear.min()) if clear.size else 99.0
    vis = sum(v > 0.5 for v in res.values())
    if vis == 0:
        fails.append(f"H{n}: Starfrost Spire not visible from the tee ({res})")
        result = "BLOCKED"
    elif res["tip"] <= 0.5:
        warns.append(f"H{n}: Spire tip hidden from the tee (lower spire visible)")
        result = "partly visible"
    else:
        result = "visible"
    los_lines.append(f"| H{n} | {dist:.0f} | {res['tip']:+.0f} | {res['upper']:+.0f} | {res['waist']:+.0f} | {result} |")

# ------------------------------------------------------------ 7. comfort: lifts, hubs, next-tee pads, respawn
for l in world["lifts"]:
    vmax = 4.0 if l["type"] == "lift" else 6.0
    if l.get("speed_studs_s", 99) > vmax:
        fails.append(f"{l['name']}: speed {l.get('speed_studs_s')} > {vmax} studs/s")
    if not l.get("railed") or not l.get("teleport_alternative") or l.get("accel_jolts", True):
        fails.append(f"{l['name']}: must be railed, jolt-free and have a teleport alternative")
zone_hub = {z["name"]: [tp for tp in world["teleport_points"] if tp["zone"] == z["name"] and tp.get("hub")] for z in world["zones"]}
for zn, tps in zone_hub.items():
    if not tps:
        fails.append(f"zone {zn} has no hub teleport pad")
info.append("hub teleport pads: " + ", ".join(f"{zn}: {', '.join(t['name'] for t in tps)}" for zn, tps in zone_hub.items()))
if not world["comfort"]["next_tee_teleport"]["enabled"] or world["comfort"].get("forced_locomotion", True):
    fails.append("next-tee teleport must be enabled and forced locomotion off")
for n, h in HOLES.items():
    tp = h["tee_teleport"]
    x, y, z = tp["pos"]
    th = np.linspace(0, 2 * np.pi, 8, endpoint=False)
    ring = H(x + tp["radius"] * np.cos(th), z + tp["radius"] * np.sin(th))
    hh = float(H(np.array([x]), np.array([z]))[0])
    if abs(hh - y) > 0.6 or np.abs(ring - y).max() > 0.6:
        fails.append(f"H{n} next-tee teleport pad not on flat ground (centre {hh:.1f} vs {y}, ring dev {np.abs(ring - y).max():.1f})")
if world["void"].get("walkable", True):
    fails.append("void.walkable must be false (cloud floor is not walkable)")
info.append(f"void: no terrain below y {VOID['terrain_fill_min_y']}, cloud deck y {VOID['cloud_deck_y']}, respawn plane y {VOID['respawn_plane_y']}; "
            "every pad and walkway >= 10 above it")

# ------------------------------------------------------------ 8. variety: gimmicks and movers
gims = [h["gimmick"].split(":")[0].strip().lower() for h in HOLES.values()]
dup = {g for g in gims if gims.count(g) > 1}
if dup:
    fails.append(f"headline gimmick repeated: {sorted(dup)}")
mot = [h["motion_type"] for h in HOLES.values() if h.get("motion_type")]
dupm = {m for m in mot if mot.count(m) > 1}
if dupm:
    fails.append(f"mover motion type repeated: {sorted(dupm)}")
info.append(f"{len(set(gims))} distinct headline gimmicks; {len(mot)} movers with distinct motion types: " + ", ".join(
    f"H{h['number']} {h['motion_type']}" for h in HOLES.values() if h.get("motion_type")))

# ------------------------------------------------------------ 9. teleport points, viewpoints, scenery, water
for tp in world["teleport_points"]:
    x, y, z = tp["pos"]
    hh = float(H(np.array([x]), np.array([z]))[0])
    th = np.linspace(0, 2 * np.pi, 8, endpoint=False)
    ring = H(x + 3 * np.cos(th), z + 3 * np.sin(th))
    if abs(hh - y) > 0.6:
        fails.append(f"teleport {tp['id']}: y {y} vs standing surface {hh:.1f}")
    if np.abs(ring - hh).max() > 0.6:
        fails.append(f"teleport {tp['id']}: ground not flat (+-{np.abs(ring - hh).max():.1f} within 3 studs)")
    th16 = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    drop = float((y - H(x + 4.5 * np.cos(th16), z + 4.5 * np.sin(th16))).max())
    if drop > rules["rail_drop"] and not tp.get("parapet"):
        fails.append(f"teleport {tp['id']}: drop {drop:.0f} within 2.5 of the pad without a parapet")
    dpath = min(float(W.seg_dist(np.array(x), np.array(z), (s["start"][0], s["start"][2]), (s["end"][0], s["end"][2]))[0])
                for p in world["paths"] for s in p["segments"] if s["type"] not in ("gondola",))
    if dpath > 14:
        fails.append(f"teleport {tp['id']}: {dpath:.0f} studs from the nearest walkway")
    for n in HOLES:
        for q in PADS[n]:
            if float(W.rect_dist(np.array(x), np.array(z), q["cx"], q["cz"], q["sx"], q["sz"], q["yaw"])) < 3:
                fails.append(f"teleport {tp['id']} inside/next to H{n}")
for poi in world["pois"]:
    if poi["kind"] != "viewpoint":
        continue
    x, y, z = poi["pos"]
    th16 = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    drop = float((y - H(x + 8 * np.cos(th16), z + 8 * np.sin(th16))).max())
    if drop > rules["rail_drop"] and not poi.get("parapet"):
        fails.append(f"viewpoint {poi['id']}: drop {drop:.0f} within 8 studs but no parapet")
info.append(f"{len(world['teleport_points'])} teleport pads checked (flat, <= 14 from a walkway, clear of holes, parapet where a drop is near: "
            f"{', '.join(t['id'] for t in world['teleport_points'] if t.get('parapet')) or 'none'})")

nsc = 0
SMALL = ("snowy_pine", "ice_crystal_cluster", "frosted_palm", "coral_ice", "snowpuff_group", "lantern_hut")
for pc in world["backdrop"]["pieces"]:
    if pc["kind"] not in SMALL:
        continue
    nsc += 1
    x, y, z = pc["pos"]
    r = pc["size"][0] / 2
    for n in HOLES:
        for q in PADS[n]:
            if float(W.rect_dist(np.array(x), np.array(z), q["cx"], q["cz"], q["sx"], q["sz"], q["yaw"])) < r + 2:
                fails.append(f"scenery {pc['id']} on H{n}")
    if y < VOID["terrain_fill_min_y"]:
        fails.append(f"scenery {pc['id']} placed over the void")
info.append(f"{nsc} small scenery pieces clear of every footprint and on island ground")

for st in world["streams"]:
    lv = [q["level"] for q in st["points"]]
    if any(b > a + 1e-6 for a, b in zip(lv, lv[1:])):
        fails.append(f"stream {st['name']} level increases downstream")
th = np.linspace(0, 2 * np.pi, 360, endpoint=False)
for lk in world["lakes"]:
    rr = 1 + (lk["beach_width"] + 3) / min(lk["radii"])
    rx = lk["center"][0] + lk["radii"][0] * rr * np.cos(th)
    rz = lk["center"][1] + lk["radii"][1] * rr * np.sin(th)
    rim = H(rx, rz)
    mouth = np.isfinite(W.water_surface(world, rx, rz))
    for st in world["streams"]:          # the outlet channel's own carved banks drain into the runoff, not off the island
        pts = [(q["x"], q["z"]) for q in st["points"]]
        d, _, _ = W.polyline_nearest(pts, rx, rz)
        mouth |= d < max(q["width"] for q in st["points"]) / 2 + 3.0
    leak = (rim < lk["level"] + 0.5) & ~mouth
    if leak.any():
        fails.append(f"lagoon {lk['name']} rim below water level at {int(leak.sum())} of 360 points")
    info.append(f"{lk['name']}: rim min {float(rim[~mouth].min()):.1f} vs water {lk['level']} ({int(mouth.sum())} ring points are the runoff mouth)")
info.append(f"Starfrost Spire: base y {LY:.0f}, tip y {LY + LH:.0f}, at ({LX:.0f}, {LZ:.0f})")

# ------------------------------------------------------------ report
FIT_L = []
# Phase 2: holes.json fit (every felt/rail corner and mover reach inside the concept pads; placements identical; cups = walkway starts)
HJP = os.path.join(W.WORLD_DIR, "..", "holes.json")
if os.path.exists(HJP):
    hj = {h["number"]: h for h in json.load(open(HJP))["holes"]}
    fit_rows = []
    for h in world["holes"]:
        n = h["number"]; q = hj.get(n)
        if not q:
            fails.append(f"H{n} missing from holes.json"); continue
        same = [round(v, 3) for v in q["world_offset"]] == [round(v, 3) for v in h["placement"]["origin"]] and \
            abs(q.get("world_yaw", 0) - h["placement"]["yaw_deg"]) < 1e-9
        out = q.get("footprint_fit", {}).get("outside", -1)
        cup_ok = all(abs(a - b) < 0.02 for a, b in zip(q["cup"]["position"], h["concept"]["cup_local"]))
        if not same: fails.append(f"H{n} holes.json placement differs from world.json")
        if out != 0: fails.append(f"H{n} holes.json has {out} felt/rail points outside its pads")
        if not cup_ok: fails.append(f"H{n} walkway start {h['concept']['cup_local']} != holes.json cup {q['cup']['position']}")
        fit_rows.append(f"| H{n} | {q['par']} | {'same' if same else 'DIFF'} | {out} | {q['cup']['position']} | {'ok' if same and out == 0 and cup_ok else 'FAIL'} |")
    FIT_L.append("\n| hole | par | placement vs holes.json | holes.json points outside pads | cup (local) = walkway start | ok |\n|---|---|---|---|---|---|")
    FIT_L += fit_rows
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
L.append("\n| path | name | walk | climb | max ramp | steps | max rise | railed segs | lifts / bridges |\n|---|---|---|---|---|---|---|---|---|")
L += path_lines
L += FIT_L
L.append(f"\n| hole | play bearing | angle to moon ({moon['bearing_deg']:g}) | ok |\n|---|---|---|---|")
L += [f"| H{n} | {pb:.0f} | {d:.0f} | {'ok' if ok else 'MOON IN EYES'} |" for n, pb, d, ok in moon_lines]
L.append("\n| tee | dist to Spire | LOS clearance tip | upper | waist | result |\n|---|---|---|---|---|---|")
L += los_lines
report = "\n".join(L)
print(report)

vpath = os.path.join(W.WORLD_DIR, "validation.md")
prev = open(vpath).read() if os.path.exists(vpath) else (
    "# Aurora Archipelago world: validation log\n\nEach run of `world/tools/validate.py` appends an iteration. "
    "Holes start as concept footprints; from Phase 2 holes.json is checked against them.\n")
it = len(re.findall(r"^## Iteration ", prev, flags=re.M)) + 1
note = sys.argv[1] if len(sys.argv) > 1 else ""
entry = f"\n## Iteration {it} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
if note:
    entry += (note if note.startswith("Changes:") else f"Changes: {note}") + "\n\n"
entry += report + "\n"
with open(vpath, "w") as f:
    f.write(prev + entry)
with open(os.path.join(W.WORLD_DIR, "validation_latest.json"), "w") as f:
    json.dump(dict(iteration=it, clean=not fails, fails=fails, warns=warns, info=info, total_walk=round(total_walk, 1)), f, indent=1)
sys.exit(0 if not fails else 1)
