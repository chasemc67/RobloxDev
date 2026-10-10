#!/usr/bin/env python3
"""Render hNN-layout.png for every hole and course-map.png from holes.json.

    python3 tools/render_layout.py [--holes 1 2] [--sim tools/out/sim-latest.json]

Top-down map view: +X right, -Z up (north). If a sim result JSON is present the brute-force
hole-in-one line is traced and drawn.
"""
import argparse, json, math, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyArrowPatch, Rectangle
from matplotlib.ticker import MultipleLocator
from matplotlib import cm, colors

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

STUD_M = 0.3
FELT_CMAP = colors.LinearSegmentedColormap.from_list("felt", ["#2f6b2a", "#4f9a3a", "#86c24a", "#c7dd6a"])
WALL_C = "#5b4636"
BLOCK_C = "#3b2a1e"
WATER_C = "#4aa3df"
PIT_C = "#2b1d14"
MOVE_C = "#f08a24"
TP_C = "#c23bd4"


def rotp(lx, lz, yaw):
    a = math.radians(yaw)
    c, s = math.cos(a), math.sin(a)
    return lx * c + lz * s, -lx * s + lz * c


def rect_corners(cx, cz, sx, sz, yaw):
    pts = []
    for lx, lz in [(-sx / 2, -sz / 2), (sx / 2, -sz / 2), (sx / 2, sz / 2), (-sx / 2, sz / 2)]:
        dx, dz = rotp(lx, lz, yaw)
        pts.append((cx + dx, cz + dz))
    return pts


def to_world(hole, x, y, z):
    ox, oy, oz = hole["world_offset"]
    dx, dz = rotp(x, z, hole.get("world_yaw", 0.0))
    return ox + dx, oy + y, oz + dz


def felt_ends(p):
    """(low_pt, high_pt, rise) along slope axis in local hole coords."""
    sl = p.get("slope")
    if not sl:
        return None
    cx, cy, cz = p["center"]
    sx, sz = p["size"]
    if sl["axis"] == "x":
        a, b = rotp(-sx / 2 * 0.7, 0, p["yaw"]), rotp(sx / 2 * 0.7, 0, p["yaw"])
    else:
        a, b = rotp(0, -sz / 2 * 0.7, p["yaw"]), rotp(0, sz / 2 * 0.7, p["yaw"])
    A, B = (cx + a[0], cz + a[1]), (cx + b[0], cz + b[1])
    rise = sl["rise"]
    return (A, B, rise) if rise > 0 else (B, A, -rise)


def height_range(holes):
    ys = []
    for h in holes:
        for p in h["felt"]:
            r = abs(p["slope"]["rise"]) / 2 if p.get("slope") else 0
            ys += [p["center"][1] - r, p["center"][1] + r]
    return min(ys), max(ys)


def piece_mean_h(p):
    return p["center"][1]


def draw_hole(hole, sim_rec, outpath):
    fig = plt.figure(figsize=(18, 12.5), dpi=110)
    ax = fig.add_axes([0.04, 0.06, 0.62, 0.86])
    side = fig.add_axes([0.69, 0.06, 0.29, 0.86])
    side.axis("off")
    ys = [p["center"][1] for p in hole["felt"]]
    hmin = min(p["center"][1] - (abs(p["slope"]["rise"]) / 2 if p.get("slope") else 0) for p in hole["felt"])
    hmax = max(p["center"][1] + (abs(p["slope"]["rise"]) / 2 if p.get("slope") else 0) for p in hole["felt"])
    if hmax - hmin < 0.5:
        hmax = hmin + 0.5
    norm = colors.Normalize(hmin, hmax)

    # bounds
    xs, zs = [], []
    for p in hole["felt"]:
        if p.get("overlay"):
            continue
        for x, z in rect_corners(p["center"][0], p["center"][2], *p["size"], p["yaw"]):
            xs.append(x); zs.append(z)
    for hz in hole.get("hazards", []):
        for x, z in rect_corners(hz["center"][0], hz["center"][2], *hz["size"], hz.get("yaw", 0)):
            xs.append(x); zs.append(z)
    x0, x1, z0, z1 = min(xs) - 4, max(xs) + 4, min(zs) - 4, max(zs) + 5

    # felt (base first, overlays after)
    for p in sorted(hole["felt"], key=lambda q: (bool(q.get("overlay")), q["center"][1])):
        pts = rect_corners(p["center"][0], p["center"][2], *p["size"], p["yaw"])
        col = FELT_CMAP(norm(piece_mean_h(p)))
        if p.get("overlay"):
            # draw only where it lies over base felt (the rest is buried behind rails)
            for q in hole["felt"]:
                if q.get("overlay"):
                    continue
                clip = Polygon(rect_corners(q["center"][0], q["center"][2], *q["size"], q["yaw"]), closed=True,
                               transform=ax.transData, fc="none", ec="none")
                pat = ax.add_patch(Polygon(pts, closed=True, fc=col, ec="#1d3d17", lw=1.0, alpha=0.9, hatch="///", zorder=3))
                pat.set_clip_path(clip)
        else:
            ax.add_patch(Polygon(pts, closed=True, fc=col, ec="#1d3d17", lw=1.2, zorder=2))
            if p.get("tunnel"):
                ax.add_patch(Polygon(pts, closed=True, fc="none", ec="#7a5230", lw=2.5, ls="--", zorder=6))
                ax.text(p["center"][0], p["center"][2] + p["size"][1] * 0.0, "TUNNEL", ha="center", va="center",
                        fontsize=8, color="#5a3a1e", rotation=0, zorder=7, fontweight="bold",
                        bbox=dict(fc="white", ec="none", alpha=0.6, pad=1))
        # dimension label
        cx, cz = p["center"][0], p["center"][2]
        lbl = f"{p['id']}\n{p['size'][0]:g}x{p['size'][1]:g}\ny={p['center'][1]:g}" if not p.get("slope") else \
              f"{p['id']}\n{p['size'][0]:g}x{p['size'][1]:g}"
        if not p.get("overlay"):
            ax.text(cx, cz + (1.6 if p.get("slope") else 0), lbl, ha="center", va="center", fontsize=7, color="#10300c",
                    zorder=5, alpha=0.9)
        ends = felt_ends(p)
        if ends:
            (ax_, az_), (bx_, bz_), rise = ends
            ax.add_patch(FancyArrowPatch((ax_, az_), (bx_, bz_), arrowstyle="-|>", mutation_scale=16, lw=2,
                                         color="#ffffff" if not p.get("overlay") else "#fff2a8", zorder=8))
            ax.text((ax_ + bx_) / 2, (az_ + bz_) / 2, f"up +{rise:g} ({rise * STUD_M:.2f} m)", fontsize=7.5,
                    ha="center", va="center", color="#202020", zorder=9,
                    bbox=dict(fc="#fffbe0", ec="#9a8a40", lw=0.6, alpha=0.9, pad=1.2))

    # hazards
    for hz in hole.get("hazards", []):
        pts = rect_corners(hz["center"][0], hz["center"][2], *hz["size"], hz.get("yaw", 0))
        water = hz["type"] == "water"
        ax.add_patch(Polygon(pts, closed=True, fc=WATER_C if water else PIT_C, ec="#1b4f7a" if water else "black",
                             alpha=0.55 if water else 0.85, hatch="~~" if water else "xx", zorder=1.5 if water else 2.5))
        ax.text(hz["center"][0], hz["center"][2], f"{hz['type'].upper()} '{hz['id']}'\nreset +1",
                ha="center", va="center", fontsize=8, color="white" if not water else "#0c2c4a", zorder=9,
                fontweight="bold")

    # walls
    for w in hole["walls"]:
        pts = rect_corners(w["center"][0], w["center"][2], w["size"][0], w["size"][2], w["yaw"])
        static_block = not w["id"].startswith("rail")
        ax.add_patch(Polygon(pts, closed=True, fc=BLOCK_C if static_block else WALL_C, ec="black", lw=0.4, zorder=10))
        if static_block:
            ax.text(w["center"][0], w["center"][2], w["id"], fontsize=7.5, color="white", ha="center", va="center",
                    zorder=11, fontweight="bold", rotation=0,
                    bbox=dict(fc=BLOCK_C, ec="none", alpha=0.7, pad=0.8))

    # drops
    for d in hole.get("drops", []):
        frm = next((p for p in hole["felt"] if p["id"] == d["from"] or p["zone"] == d["from"]), None)
        if frm:
            pass
    # moving parts
    side_lines = []
    import sim as S
    ha = S.HoleArrays(hole)
    PH = S.ph_array()
    for m in hole.get("moving_parts", []):
        piv = m["pivot"]
        if m["type"] == "rotate":
            ax_ = np.array(m["axis"], float)
            vertical = abs(ax_[1]) > 0.9
            reach = max(math.hypot(b["center"][0], b["center"][2]) + math.hypot(b["size"][0], b["size"][2]) / 2
                        for b in m["blockers"])
            if vertical:
                ax.add_patch(Circle((piv[0], piv[2]), reach, fc=MOVE_C, alpha=0.12, ec=MOVE_C, ls="--", lw=1.5, zorder=12))
                # blockers at t=0
                for b in m["blockers"]:
                    pts = rect_corners(piv[0] + b["center"][0], piv[2] + b["center"][2], b["size"][0], b["size"][2], b["yaw"])
                    ax.add_patch(Polygon(pts, closed=True, fc=MOVE_C, ec="#7a3a00", lw=1, zorder=13))
                th = np.linspace(0.2, 1.3, 20)
                rr = reach + 0.8
                sgn = 1 if m["speed"] > 0 else -1
                # positive rotation about +Y is CCW in map view (x right, -z up) -> in plotted (x, z) coords the angle goes clockwise
                ax.plot(piv[0] + rr * np.cos(th), piv[2] - sgn * rr * np.sin(th), color="#7a3a00", lw=1.5, zorder=13)
                lbl = f"{m['id']}: {abs(m['speed']):g} deg/s {'CCW' if m['speed'] > 0 else 'CW'}\n{len(m['blockers'])} arm(s), r={reach:.1f}"
                ax.text(piv[0], piv[2] + reach + 1.8, lbl, ha="center", fontsize=8, color="#5a2a00", zorder=14,
                        bbox=dict(fc="white", ec=MOVE_C, alpha=0.85, pad=1.5))
            else:
                # horizontal axis wheel: footprint band of the paddles (where they dip into the ball plane)
                ext = max(b["size"][2] for b in m["blockers"]) / 2 if abs(ax_[2]) > 0.5 else max(b["size"][0] for b in m["blockers"]) / 2
                halfw = 1.6
                if abs(ax_[2]) > 0.5:
                    pts = [(piv[0] - halfw, piv[2] - ext), (piv[0] + halfw, piv[2] - ext), (piv[0] + halfw, piv[2] + ext), (piv[0] - halfw, piv[2] + ext)]
                else:
                    pts = [(piv[0] - ext, piv[2] - halfw), (piv[0] + ext, piv[2] - halfw), (piv[0] + ext, piv[2] + halfw), (piv[0] - ext, piv[2] + halfw)]
                ax.add_patch(Polygon(pts, closed=True, fc=MOVE_C, alpha=0.35, ec="#7a3a00", hatch="||", lw=1.5, zorder=12))
                ax.plot([piv[0] - 0.3, piv[0] + 0.3], [piv[2], piv[2]], color="k", zorder=14)
                ax.text(piv[0], piv[2] - ext - 1.6, f"{m['id']}: {abs(m['speed']):g} deg/s about axis {tuple(m['axis'])}\n"
                        f"pivot y={piv[1]:g}; paddles sweep this band", ha="center", fontsize=8, color="#5a2a00", zorder=14,
                        bbox=dict(fc="white", ec=MOVE_C, alpha=0.85, pad=1.5))
        else:
            lo, hi = m["range"]
            axv = m["axis"]
            for b in m["blockers"]:
                for off, alpha in [(lo, 0.25), (hi, 0.25), (m.get("phase", 0.0), 1.0)]:
                    cx = piv[0] + b["center"][0] + axv[0] * off
                    cz = piv[2] + b["center"][2] + axv[2] * off
                    pts = rect_corners(cx, cz, b["size"][0], b["size"][2], b["yaw"])
                    ax.add_patch(Polygon(pts, closed=True, fc=MOVE_C, alpha=alpha, ec="#7a3a00", lw=1, zorder=13))
            if abs(axv[1]) > 0.9:
                lbl = f"{m['id']}: rises/falls {lo:g}..{hi:g} studs at {abs(m['speed']):g} studs/s (vertical slide)"
            else:
                a0 = (piv[0] + axv[0] * lo, piv[2] + axv[2] * lo)
                a1 = (piv[0] + axv[0] * hi, piv[2] + axv[2] * hi)
                ax.add_patch(FancyArrowPatch(a0, a1, arrowstyle="<|-|>", mutation_scale=14, lw=1.5, color="#7a3a00", zorder=14))
                lbl = f"{m['id']}: slides {lo:g}..{hi:g} studs at {abs(m['speed']):g} studs/s"
            ax.text(piv[0], piv[2] + 2.3, lbl, ha="center", fontsize=8, color="#5a2a00", zorder=14,
                    bbox=dict(fc="white", ec=MOVE_C, alpha=0.85, pad=1.5))
        ax.plot(piv[0], piv[2], marker="X", color="black", ms=9, zorder=15)
        side_lines.append(f"- {m['id']} ({m['type']}): pivot {piv}, axis {m['axis']}, speed {m['speed']} {m['speed_units']}, "
                          f"range {m['range']}")

    # teleports
    for t in hole.get("teleports", []):
        e, r = t["entry"]["center"], t["entry"]["radius"]
        x_ = t["exit"]["center"]
        ax.add_patch(Circle((e[0], e[2]), r, fc=TP_C, alpha=0.5, ec=TP_C, lw=2, zorder=15))
        ax.add_patch(Circle((x_[0], x_[2]), r, fc="none", ec=TP_C, lw=2.5, zorder=15))
        ax.add_patch(FancyArrowPatch((e[0], e[2]), (x_[0], x_[2]), connectionstyle="arc3,rad=0.25", arrowstyle="-|>",
                                     mutation_scale=18, lw=1.6, ls="--", color=TP_C, zorder=15))
        d = t["exit"]["dir"]
        ax.add_patch(FancyArrowPatch((x_[0], x_[2]), (x_[0] + 3 * d[0], x_[2] + 3 * d[1]), arrowstyle="-|>",
                                     mutation_scale=16, lw=2, color=TP_C, zorder=15))
        ax.text(e[0], e[2] + r + 1.0, f"TP '{t['id']}' IN (r={r})", ha="center", fontsize=8, color=TP_C, fontweight="bold", zorder=16)
        ax.text(x_[0], x_[2] + r + 1.0, f"TP '{t['id']}' OUT", ha="center", fontsize=8, color=TP_C, fontweight="bold", zorder=16)

    # drops labels
    for d in hole.get("drops", []):
        ax.text(0, 0, "", fontsize=1)
    # decoration anchors
    for a in hole.get("decoration_anchors", []):
        p = a["position"]
        ax.plot(p[0], p[2], marker="*" if a.get("landmark") else "D", ms=14 if a.get("landmark") else 6,
                color="#d4a017" if a.get("landmark") else "#8a6d3b", mec="black", mew=0.6, zorder=16)
        ax.text(p[0] + 0.6, p[2] - 0.6, a["name"], fontsize=7, color="#5b4510", zorder=16, style="italic")

    # HIO line
    hio_txt = "HIO search: not run"
    if sim_rec and sim_rec.get("hio_search"):
        hs = sim_rec["hio_search"]
        if hs.get("line"):
            ln = hs["line"]
            path, r = S.trace_shot(ha, math.radians(ln["aim_deg"]), ln["speed"], ln["phase"])
            ax.plot(path[:, 0], path[:, 2], color="#d62728", lw=1.6, ls=(0, (4, 2)), zorder=17, label="hole-in-one line")
            hio_txt = (f"HIO line (red dashed): aim {ln['aim_deg']:.1f} deg (atan2 dz,dx), {ln['speed']:.2f} studs/s "
                       f"({ln['speed'] / S.V_MAX * 100:.0f}% power), phase t={ln['phase']:.1f}s\n"
                       f"brute force: {hs['hits']}/{hs['shots']} grid shots hole out" +
                       (f"; refine {hs.get('refine_hits')}/{hs.get('refine_shots')}" if hs.get("refined") else ""))
        else:
            hio_txt = f"HIO search: NO line found (closest {hs.get('closest', 0):.2f} studs)"

    # waypoints
    for sk, lst in hole.get("ai_waypoints", {}).items():
        for w in lst:
            ax.plot(w["pos"][0], w["pos"][2], marker="+", color="#555555", ms=8, zorder=16)
            ax.text(w["pos"][0] + 0.3, w["pos"][2] + 0.7, f"ai:{w['id']}" + ("" if sk == "all" else f" ({sk})"),
                    fontsize=6.5, color="#555555", zorder=16)

    # tee & cup
    t = hole["tee"]["position"]
    ax.add_patch(Rectangle((t[0] - 0.9, t[2] - 0.6), 1.8, 1.2, fc="white", ec="black", lw=1.2, zorder=18))
    ax.text(t[0], t[2] + 1.6, "TEE", ha="center", fontsize=10, fontweight="bold", zorder=18)
    c = hole["cup"]["position"]
    ax.add_patch(Circle((c[0], c[2]), hole["cup"]["radius"], fc="black", ec="white", lw=1.2, zorder=18))
    ax.plot([c[0], c[0]], [c[2], c[2] - 2.6], color="#333", lw=1.5, zorder=18)
    ax.add_patch(Polygon([(c[0], c[2] - 2.6), (c[0] + 1.4, c[2] - 2.2), (c[0], c[2] - 1.8)], fc="#e03c31", ec="none", zorder=18))
    ax.text(c[0] + 0.8, c[2] + 1.0, f"CUP r={hole['cup']['radius']}", fontsize=8, fontweight="bold", zorder=18)

    # grid & frame
    ax.set_xlim(x0, x1)
    ax.set_ylim(z1, z0)  # inverted: -z up
    ax.set_aspect("equal")
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.grid(which="major", color="#9a9a9a", lw=0.7, alpha=0.7)
    ax.grid(which="minor", color="#cfcfcf", lw=0.35, alpha=0.6)
    ax.set_facecolor("#f4efe2")
    ax.set_xlabel("x (studs)  ->  east / player's right when facing -Z")
    ax.set_ylabel("z (studs)   (north = -Z is up)")
    ax.tick_params(labelsize=8)

    # overall dimensions
    fx = [x for p in hole["felt"] if not p.get("overlay") for x, _ in rect_corners(p["center"][0], p["center"][2], *p["size"], p["yaw"])]
    fz = [z for p in hole["felt"] if not p.get("overlay") for _, z in rect_corners(p["center"][0], p["center"][2], *p["size"], p["yaw"])]
    X0, X1, Z0, Z1 = min(fx), max(fx), min(fz), max(fz)
    yb = Z1 + 2.2
    ax.add_patch(FancyArrowPatch((X0, yb), (X1, yb), arrowstyle="<|-|>", mutation_scale=10, color="#333", lw=1, zorder=20))
    ax.text((X0 + X1) / 2, yb + 1.0, f"{X1 - X0:g} studs ({(X1 - X0) * STUD_M:.1f} m)", ha="center", fontsize=8.5, zorder=20,
            bbox=dict(fc="#f4efe2", ec="none", pad=0.5))
    xb = X0 - 2.2
    ax.add_patch(FancyArrowPatch((xb, Z0), (xb, Z1), arrowstyle="<|-|>", mutation_scale=10, color="#333", lw=1, zorder=20))
    ax.text(xb - 0.6, (Z0 + Z1) / 2, f"{Z1 - Z0:g} studs ({(Z1 - Z0) * STUD_M:.1f} m)", rotation=90, ha="right", va="center",
            fontsize=8.5, zorder=20, bbox=dict(fc="#f4efe2", ec="none", pad=0.5))
    # scale bar
    sx0, sz0 = x0 + 1.0, z0 + 1.5
    for k in range(2):
        ax.add_patch(Rectangle((sx0 + k * 5, sz0), 5, 0.6, fc="black" if k == 0 else "white", ec="black", zorder=21))
    ax.text(sx0 + 5, sz0 - 0.6, "10 studs = 3.0 m", ha="center", fontsize=8.5, fontweight="bold", zorder=21,
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.5))
    # north arrow
    ax.add_patch(FancyArrowPatch((x1 - 2, z0 + 5), (x1 - 2, z0 + 1.5), arrowstyle="-|>", mutation_scale=18, color="k", zorder=21))
    ax.text(x1 - 2, z0 + 6.2, "N (-Z)", ha="center", fontsize=8, zorder=21)

    sm = cm.ScalarMappable(norm=norm, cmap=FELT_CMAP)
    cb = fig.colorbar(sm, ax=ax, fraction=0.025, pad=0.01)
    cb.set_label("felt top height y (studs)", fontsize=8)
    cb.ax.tick_params(labelsize=7)

    fig.suptitle(f"Hole {hole['number']} - {hole['name']}   |   PAR {hole['par']}", fontsize=20, fontweight="bold", x=0.36, y=0.975)
    fig.text(0.36, 0.935, f"{hole['zone']}  -  {hole['gimmick']}", ha="center", fontsize=11, style="italic")

    # side panel
    lines = [f"Landmark: {hole['landmark']}", "", f"Tee {hole['tee']['position']}   Cup {hole['cup']['position']} (r {hole['cup']['radius']})",
             f"World offset {hole['world_offset']}  yaw {hole.get('world_yaw', 0)}", "",
             "Felt: green shade = height (colorbar); white arrow = uphill, label = rise.",
             "Hatched yellow-arrow pieces = banked plane overlays.", "Brown = rails (1 stud high, 0.5 thick); dark = static blocks.",
             "Orange = moving parts (X = pivot). Blue = water, black = pit.", "Magenta = teleport ring pair.", "+ = AI waypoint.", ""]
    if hole.get("drops"):
        lines.append("Drops:")
        for d in hole["drops"]:
            lines.append(f"- {d['from']} -> {d['to']}: {d['height']} studs ({d['height'] * STUD_M:.2f} m), {d['edge']}")
        lines.append("")
    if side_lines:
        lines.append("Moving parts:")
        lines += side_lines
        lines.append("")
    if hole.get("teleports"):
        lines.append("Teleports:")
        for t in hole["teleports"]:
            lines.append(f"- {t['id']}: in {t['entry']['center']} r{t['entry']['radius']} -> out {t['exit']['center']} "
                         f"dir {t['exit']['dir']}, speed x{t['speed_factor']} clamp [{t['min_speed']},{t['max_speed']}]")
        lines.append("")
    lines.append(hio_txt)
    if sim_rec and sim_rec.get("stats"):
        lines.append("")
        lines.append(f"Sim ({sim_rec.get('_tag', '')}):")
        for sk, st in sim_rec["stats"].items():
            lines.append(f"- {sk}: avg {st['avg']:.2f}, HIO {st['hio'] * 100:.1f}%, capped {st['capped'] * 100:.1f}%")
            lines.append(f"    strokes 1..8: {st['dist']}")
        lines.append(f"flags: {', '.join(sim_rec.get('flags', [])) or 'none'}")
    import textwrap
    wrapped = []
    for ln in lines:
        wrapped += textwrap.wrap(ln, 62, subsequent_indent="   ") or [""]
    side.text(0, 1, "\n".join(wrapped), va="top", ha="left", fontsize=9.5, family="DejaVu Sans Mono")
    fig.savefig(outpath)
    plt.close(fig)


def draw_course(course, outpath):
    holes = course["holes"]
    fig, ax = plt.subplots(figsize=(20, 13), dpi=100)
    ax.set_facecolor("#e9d9b4")
    zone_pts = {}
    landmarks = []
    cups, tees = [], []
    for h in holes:
        for hz in h.get("hazards", []):
            pts = [to_world(h, x, 0, z) for x, z in rect_corners(hz["center"][0], hz["center"][2], *hz["size"], hz.get("yaw", 0))]
            ax.add_patch(Polygon([(p[0], p[2]) for p in pts], fc=WATER_C if hz["type"] == "water" else PIT_C, alpha=0.6, ec="none", zorder=2))
        for p in sorted(h["felt"], key=lambda q: bool(q.get("overlay"))):
            pts = [to_world(h, x, 0, z) for x, z in rect_corners(p["center"][0], p["center"][2], *p["size"], p["yaw"])]
            ax.add_patch(Polygon([(q[0], q[2]) for q in pts], fc="#5aa83c" if not p.get("overlay") else "#7fbf55",
                                 ec="#2c5a1e", lw=0.6, zorder=3))
            zone_pts.setdefault(h["zone"], []).append(to_world(h, *p["center"]))
        for w in h["walls"]:
            pts = [to_world(h, x, 0, z) for x, z in rect_corners(w["center"][0], w["center"][2], w["size"][0], w["size"][2], w["yaw"])]
            ax.add_patch(Polygon([(q[0], q[2]) for q in pts], fc=WALL_C, ec="none", zorder=4))
        for m in h.get("moving_parts", []):
            pv = to_world(h, *m["pivot"])
            ax.plot(pv[0], pv[2], marker="X", color=MOVE_C, ms=10, mec="black", zorder=6)
        for t in h.get("teleports", []):
            for key in ("entry", "exit"):
                pv = to_world(h, *t[key]["center"])
                ax.plot(pv[0], pv[2], marker="o", color=TP_C, ms=8, zorder=6)
        tw = to_world(h, *h["tee"]["position"])
        cw = to_world(h, *h["cup"]["position"])
        tees.append(tw); cups.append(cw)
        ax.add_patch(Circle((tw[0], tw[2]), 3.2, fc="#fff6dc", ec="#5b4636", lw=2, zorder=8))
        ax.text(tw[0], tw[2], str(h["number"]), ha="center", va="center", fontsize=15, fontweight="bold", zorder=9)
        ax.plot(cw[0], cw[2], marker="o", color="black", ms=5, zorder=8)
        ax.plot([cw[0], cw[0]], [cw[2], cw[2] - 4], color="#333", lw=1.2, zorder=8)
        ax.add_patch(Polygon([(cw[0], cw[2] - 4), (cw[0] + 2.2, cw[2] - 3.4), (cw[0], cw[2] - 2.8)], fc="#e03c31", zorder=8))
        # label
        ax.text(tw[0] + 3.8, tw[2] + 2.5, f"{h['name']} (par {h['par']})", fontsize=9, color="#3b2a1e", zorder=9,
                bbox=dict(fc="#fff6dc", ec="none", alpha=0.75, pad=1))
        for a in h.get("decoration_anchors", []):
            if a.get("landmark"):
                landmarks.append((to_world(h, *a["position"]), a["name"]))
    # walking path cup n -> tee n+1
    for i in range(len(holes) - 1):
        a, b = cups[i], tees[i + 1]
        ax.add_patch(FancyArrowPatch((a[0], a[2]), (b[0], b[2]), connectionstyle="arc3,rad=0.15", arrowstyle="-|>",
                                     mutation_scale=16, lw=1.8, ls=(0, (5, 4)), color="#6b4a2b", zorder=5))
    for (p, name) in landmarks:
        ax.plot(p[0], p[2], marker="*", ms=20, color="#ffcf3a", mec="#6b4a10", mew=1, zorder=10)
        ax.text(p[0] + 2, p[2] + 2, name.replace("_", " "), fontsize=9, style="italic", color="#5b3a10", zorder=10)
    # hollow tree
    h9 = holes[-1]
    tree = next(a for a in h9["decoration_anchors"] if a["name"] == "hollow_tree")
    tp = to_world(h9, *tree["position"])
    ax.add_patch(Circle((tp[0], tp[2]), 17, fc="#8b5a2b", alpha=0.25, ec="#5b3a1a", lw=2, ls="--", zorder=1))
    # stream: smooth line through water hazards
    ws = [to_world(h, *hz["center"]) for h in holes for hz in h.get("hazards", []) if hz["type"] == "water"]
    if ws:
        ws = sorted(ws, key=lambda p: p[0])
        xs = [ws[0][0] - 30] + [p[0] for p in ws] + [ws[-1][0] + 30]
        zs = [ws[0][2] + 40] + [p[2] for p in ws] + [ws[-1][2] - 40]
        ax.plot(xs, zs, color=WATER_C, lw=10, alpha=0.35, solid_capstyle="round", zorder=1)
    # zone labels
    for z, pts in zone_pts.items():
        pts = np.array(pts)
        cx, cz = pts[:, 0].mean(), pts[:, 2].min() - 14  # label sits north of the zone's holes
        ax.text(cx, cz, z.upper(), ha="center", fontsize=15, fontweight="bold", color="#7a3b12", alpha=0.85, zorder=11)
    ax.set_aspect("equal")
    ax.autoscale_view()
    allx = [p[0] for p in tees + cups]
    allz = [p[2] for p in tees + cups]
    ax.set_xlim(min(allx) - 40, max(allx) + 40)
    ax.set_ylim(max(allz) + 30, min(allz) - 30)
    ax.xaxis.set_major_locator(MultipleLocator(20))
    ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.grid(color="#b9a77f", lw=0.5)
    ax.set_title(f"LANTERN GROVE - course map (world studs, north = -Z up)   total par {course['total_par']}",
                 fontsize=18, fontweight="bold")
    x0 = ax.get_xlim()[0] + 8
    z0 = ax.get_ylim()[0] - 8
    ax.add_patch(Rectangle((x0, z0), 50, 2, fc="black", zorder=12))
    ax.text(x0 + 25, z0 - 2, "50 studs = 15 m", ha="center", fontsize=10, fontweight="bold", zorder=12)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(ROOT, "holes.json"))
    ap.add_argument("--sim", default=os.path.join(HERE, "out", "sim-latest.json"))
    ap.add_argument("--holes", type=int, nargs="*")
    ap.add_argument("--outdir", default=ROOT)
    a = ap.parse_args()
    course = json.load(open(a.json))
    simd = {}
    if a.sim and os.path.exists(a.sim):
        sd = json.load(open(a.sim))
        for r in sd["holes"]:
            r["_tag"] = sd.get("tag", "")
            simd[r["id"]] = r
    for h in course["holes"]:
        if a.holes and h["number"] not in a.holes:
            continue
        out = os.path.join(a.outdir, f"h{h['number']:02d}-layout.png")
        draw_hole(h, simd.get(h["id"]), out)
        print("wrote", out)
    if not a.holes:
        out = os.path.join(a.outdir, "course-map.png")
        draw_course(course, out)
        print("wrote", out)


if __name__ == "__main__":
    main()
