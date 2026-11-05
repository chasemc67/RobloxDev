"""Render heightmap.png (16-bit), heightmap-8bit.png, world-map.png (annotated) and world-map-base.png (shapes only, no text)
from world.json. Adapted from lantern-grove/world/tools/make_maps.py.

usage: python3 tools/make_maps.py [--map-step 2]
"""
import argparse
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LightSource, to_rgb  # noqa: E402
from matplotlib.patches import Circle, FancyArrow, Polygon, Rectangle  # noqa: E402
from PIL import Image  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worldlib as W  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--map-step", type=float, default=2.0, help="studs per pixel for the shaded map raster")
args = ap.parse_args()

OUT = W.WORLD_DIR
world = W.load_world()
b = world["bounds"]
hm = world["heightmap"]

# ------------------------------------------------------------ heightmap (1 px = 1 stud)
xs, zs, X, Z = W.grid(world)
print("evaluating heightfield", X.shape)
Hgt = W.height_at(world, X, Z)
y0, y1 = hm["y_min"], hm["y_max"]
g = np.clip((Hgt - y0) / (y1 - y0), 0, 1)
Image.fromarray(np.round(g * 65535).astype(np.uint16)).save(os.path.join(OUT, "heightmap.png"))
Image.fromarray(np.round(g * 255).astype(np.uint8)).save(os.path.join(OUT, "heightmap-8bit.png"))
print("heightmap range %.1f..%.1f" % (Hgt.min(), Hgt.max()))

# ------------------------------------------------------------ shaded raster for the maps
step = args.map_step
_, _, Xm, Zm = W.grid(world, step)
st = W.height_at(world, Xm, Zm, stages=True)
Hm = st["final"]
WS = st["water_surface"]
wet = np.isfinite(WS) & (Hm < WS - 0.05)
gy, gx = np.gradient(Hm, step)
slope = np.degrees(np.arctan(np.hypot(gx, gy)))

# mesa tops: warm sand by elevation; cliffs: candy strata bands by world y
top_stops = [(0, "#CF8150"), (20, "#D88E5C"), (30, "#DE9C6C"), (70, "#E59C7C"), (104, "#E9AF8E"), (116, "#EDBE98"),
             (150, "#F2D1AF"), (190, "#F9E6CF"), (260, "#FFF5EA")]
ys_, cs_ = zip(*top_stops)
top_rgb = np.stack([np.interp(Hm, ys_, [to_rgb(c)[i] for c in cs_]) for i in range(3)], -1)
strata = world["terrain"]["strata"]
band_cols = np.array([to_rgb(c) for c in strata["colors"]])
band = (np.floor(Hm / strata["band"]).astype(int)) % len(band_cols)
cliff_rgb = band_cols[band]
cw = np.clip((slope - 25) / 20, 0, 1)[..., None]
rgb = top_rgb * (1 - cw) + cliff_rgb * cw
# low canyon floor slightly greener near water (riparian), sand elsewhere
ls = LightSource(azdeg=300, altdeg=35)
shade = ls.shade_rgb(rgb, Hm, vert_exag=1.6, blend_mode="soft", fraction=1.0, dx=step, dy=step)
water_rgb = np.array(to_rgb("#3FB7C9"))
img = np.where(wet[..., None], water_rgb * 0.8 + shade * 0.2, shade)
ext = [b["x"][0], b["x"][1], b["z"][1], b["z"][0]]

HOLE_COL = "#4FA83D"
TIER_COL = "#86C24A"


def draw_common(ax, text, PX):
    ax.imshow(img, extent=ext, origin="upper", interpolation="bilinear", zorder=0)
    # paths
    for p in world["paths"]:
        for s in p["segments"]:
            xs_ = [s["start"][0], s["end"][0]]
            zs_ = [s["start"][2], s["end"][2]]
            t = s["type"]
            if t == "on_hole":
                if text:
                    ax.plot(xs_, zs_, color="#6b4a2b", lw=0.8, ls=":", zorder=3)
                continue
            if t == "gondola":
                ax.plot(xs_, zs_, color="#5a2d82", lw=1.6, ls=(0, (6, 3)), zorder=4)
                continue
            if t == "lift":
                for e in (s["start"], s["end"]):
                    ax.add_patch(Rectangle((e[0] - 4, e[2] - 4), 8, 8, fc="#5a2d82", ec="white", lw=0.8, zorder=9))
                ax.plot(xs_, zs_, color="#5a2d82", lw=2.5, zorder=8)
                continue
            col = "#8A5A33" if t in ("bridge", "dam_crest") else "#F7E8C8"
            ax.plot(xs_, zs_, color=col, lw=p["width"] * PX, solid_capstyle="round" if t not in ("bridge", "dam_crest") else "butt", zorder=3)
            if t in ("bridge", "dam_crest"):
                ax.plot(xs_, zs_, color="#E8C27A", lw=p["width"] * PX * 0.45, ls=(0, (2, 1)), zorder=3.5)
            elif text:
                ax.plot(xs_, zs_, color="#7a5530", lw=1.0, ls=(0, (4, 3)), zorder=4)
            if t == "stairs":
                L = math.hypot(xs_[1] - xs_[0], zs_[1] - zs_[0])
                ux, uz = (xs_[1] - xs_[0]) / L, (zs_[1] - zs_[0]) / L
                nx, nz = -uz, ux
                hw = p["width"] / 2
                for k in range(s["steps"] + 1):
                    cx, cz = xs_[0] + ux * s["tread"] * k, zs_[0] + uz * s["tread"] * k
                    ax.plot([cx - nx * hw, cx + nx * hw], [cz - nz * hw, cz + nz * hw], color="#5b3a22", lw=0.6, zorder=5)
    # dam
    d = world["dam"]
    ax.add_patch(Rectangle((d["x"][0], d["z_center"] - d["thickness"] / 2), d["x"][1] - d["x"][0], d["thickness"],
                           fc="#F4F0EC", ec="#D9343A", lw=2.0, hatch="////" if text else None, zorder=6))
    # waterfalls
    for wf in world["waterfalls"]:
        ax.plot([wf["top"][0], wf["bottom"][0]], [wf["top"][2], wf["bottom"][2]], color="white",
                lw=max(2.5, wf["width"] * PX * 0.6), solid_capstyle="butt", zorder=5)
    # hole footprints
    for h in world["holes"]:
        pads = W.pads_world(h)
        ymax = max(p["y"] for p in pads)
        for p in pads:
            col = HOLE_COL if (len(pads) == 1 or p["y"] == ymax) else TIER_COL
            ax.add_patch(Polygon(np.array(p["corners"]), closed=True, fc=col, ec="#1f4f1a", lw=1.0, alpha=0.92, zorder=6))
        for sp in h["concept"].get("spans", []):
            p0 = pads[0]
            x0, x1 = h["concept"]["pads"][0]["x"]
            pl = h["placement"]
            cc = [W.to_world(pl, [x, 0, z])[0::2] for x, z in ((x0, sp["z"][0]), (x1, sp["z"][0]), (x1, sp["z"][1]), (x0, sp["z"][1]))]
            ax.add_patch(Polygon(np.array(cc), closed=True, fc="none", ec="#8A5A33", lw=0.8, hatch="xxx", zorder=6.5))
        t = h["tee_world"]
        c = h["cup_world_approx"]
        ax.plot(t[0], t[2], marker="s", ms=3.5, color="white", mec="black", mew=0.6, zorder=9)
        ax.plot(c[0], c[2], marker="o", ms=3.5, color="#D9343A", mec="black", mew=0.6, zorder=9)


def make_fig(text):
    W_in = 16
    span_x = b["x"][1] - b["x"][0]
    span_z = b["z"][1] - b["z"][0]
    fig = plt.figure(figsize=(W_in, W_in * span_z / span_x), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    PX = W_in * 72 / span_x
    draw_common(ax, text, PX)
    ax.set_xlim(b["x"][0], b["x"][1])
    ax.set_ylim(b["z"][1], b["z"][0])
    ax.axis("off")
    return fig, ax


fig, ax = make_fig(False)
fig.savefig(os.path.join(OUT, "world-map-base.png"), dpi=150)
plt.close(fig)

# ------------------------------------------------------------ annotated map
fig, ax = make_fig(True)
cs = ax.contour(Xm, Zm, Hm, levels=[45, 95, 135, 172, 200], colors="#4a2a20", linewidths=0.5, alpha=0.45, zorder=2)
ax.clabel(cs, fmt="%d", fontsize=6.5, inline=True, inline_spacing=1)
# hole number badges + name labels
LAB_OFF = {1: (-20, 0, "right"), 2: (18, 0, "left"), 3: (0, -24, "center"), 4: (0, -40, "center"), 5: (22, 0, "left"),
           6: (22, 0, "left"), 7: (22, 0, "left"), 8: (22, 0, "left"), 9: (0, 26, "center"), 10: (18, 0, "left"),
           11: (0, 30, "center"), 12: (0, 30, "center"), 13: (-20, 0, "right"), 14: (-20, 0, "right"), 15: (-20, 0, "right"),
           16: (16, 0, "left"), 17: (14, 30, "left"), 18: (0, 26, "center")}
for h in world["holes"]:
    n = h["number"]
    bb = h["footprint_bbox"]
    cx, cz = (bb["x"][0] + bb["x"][1]) / 2, (bb["z"][0] + bb["z"][1]) / 2
    ax.add_patch(Circle((cx, cz), 9, fc="white", ec="#1f4f1a", lw=1.5, zorder=10))
    ax.text(cx, cz, str(n), ha="center", va="center", fontsize=9, fontweight="bold", zorder=11)
    dx, dz, ha = LAB_OFF[n]
    lx = (bb["x"][1] + dx) if ha == "left" else ((bb["x"][0] + dx) if ha == "right" else cx + dx)
    lz = cz + dz if ha != "center" else ((bb["z"][1] + dz) if dz > 0 else (bb["z"][0] + dz))
    ys = sorted({round(p["y"]) for p in W.pads_world(h)})
    ax.text(lx, lz, f"H{n} {h['name']}\npar {h['par']} - y {'/'.join(str(y) for y in ys)}", fontsize=6.8, ha=ha, va="center",
            zorder=12, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=HOLE_COL, alpha=0.88))
# zone labels
ZONES = {"Sugarloaf Junction": (-20, 600), "Rock Candy Narrows": (300, 430), "Taffy Mesa": (470, 220),
         "Sugarloaf Dam": (150, -360), "Hoodoo Garden": (-430, -330), "Sugarloaf Crown": (-370, 300)}
for zn, (x, z) in ZONES.items():
    zone = next(q for q in world["zones"] if q["name"] == zn)
    ax.text(x, z, f"{zn.upper()}\nH{zone['holes'][0]}-H{zone['holes'][-1]}", fontsize=10.5, fontweight="bold", color="#6b1f3a",
            ha="center", va="center", alpha=0.85, zorder=11, style="italic",
            bbox=dict(boxstyle="round,pad=0.25", fc="#FFF4EA", ec="#C8463F", alpha=0.7))
# POIs
SKIP = {"junction_plaza"}
for poi in world["pois"]:
    if poi["id"] in SKIP:
        continue
    ax.plot(poi["pos"][0], poi["pos"][2], marker="*", ms=10, color="#FFB347", mec="#5B3A22", zorder=10)
    dx_, dz_ = {"narrows_mouth": (-8, 14), "sunset_arch": (-10, 16), "dam": (-75, -10)}.get(poi["id"], (6, -6))
    ax.text(poi["pos"][0] + dx_, poi["pos"][2] + dz_, poi["name"], fontsize=7, zorder=12, color="#3a1a14",
            bbox=dict(boxstyle="round,pad=0.12", fc="#FFF8EE", ec="none", alpha=0.8))
# waterfalls, water names
for wf in world["waterfalls"]:
    ax.text(wf["bottom"][0] + 8, wf["bottom"][2] + {"Spillway Falls": 28, "Fizzwater Falls": -26}.get(wf["name"], 10), f"{wf['name']}\n{wf['top'][1]:.0f}->{wf['bottom'][1]:.0f}", fontsize=6.5,
            color="#0b4d6a", zorder=12, bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.75))
lk = world["lakes"][0]
ax.text(lk["center"][0], lk["center"][1], f"{lk['name']}\nwater y {lk['level']:.0f}", ha="center", fontsize=10, color="white",
        style="italic", fontweight="bold", zorder=12)
for stv, (i, dx) in zip(world["streams"], ((7, 10), (1, 0), (1, 0))):
    p = stv["points"][i]
    ax.text(p["x"] + dx, p["z"] + 14, stv["name"], fontsize=7.5, color="#0b4d6a", style="italic", zorder=12)
# lifts / bridges / gondola labels
for p in world["paths"]:
    for s in p["segments"]:
        if s["type"] in ("lift", "bridge", "gondola", "dam_crest") and s.get("name"):
            mx = (s["start"][0] + s["end"][0]) / 2
            mz = (s["start"][2] + s["end"][2]) / 2
            if s["type"] == "gondola":
                mx, mz = s["start"][0] + (s["end"][0] - s["start"][0]) * 0.45, s["start"][2] + (s["end"][2] - s["start"][2]) * 0.45
            lab = s["name"] + (f"  {s['end'][1]-s['start'][1]:+.0f}" if s["type"] in ("lift", "gondola") else "")
            ax.text(mx + 7, mz + 4, lab, fontsize=6.8, color="#5a2d82", fontweight="bold", zorder=12,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="#5a2d82", lw=0.5, alpha=0.8))
# teleports + spawn
for tp in world["teleport_points"]:
    ax.plot(tp["pos"][0], tp["pos"][2], marker="D", ms=6, color="#D8FF6A", mec="black", mew=0.6, zorder=11)
sp = world["spawn"]["pos"]
ax.plot(sp[0], sp[2], marker="P", ms=12, color="#D8FF6A", mec="black", zorder=11)
ax.text(sp[0] + 8, sp[2] + 10, "SPAWN / Junction Plaza", fontsize=8, fontweight="bold", zorder=12)
# scenery dots
for pc in world["backdrop"]["pieces"]:
    if pc["kind"] in ("hoodoo_spire", "lollipop_cactus", "rock_candy_crystal") and abs(pc["pos"][0]) < 640 and abs(pc["pos"][2]) < 640:
        col = {"hoodoo_spire": "#B5523B", "lollipop_cactus": "#3E8E41", "rock_candy_crystal": "#FF6FA8"}[pc["kind"]]
        ax.plot(pc["pos"][0], pc["pos"][2], marker="o", ms=2.5, color=col, mec="none", zorder=5)
# sun arrow
sun = world["sun"]
a = math.radians(sun["bearing_deg"])
sx, sz = math.sin(a), -math.cos(a)
x0s, z0s = b["x"][0] + 110, b["z"][0] + 140
ax.add_patch(FancyArrow(x0s, z0s, sx * 60, sz * 60, width=4, head_width=14, head_length=14, color="#F28C28", zorder=12))
ax.add_patch(Circle((x0s + sx * 90, z0s + sz * 90), 14, fc="#FFD36B", ec="#F28C28", lw=2, zorder=12))
ax.text(x0s + 10, z0s + 28, f"sunset sun\nbearing {sun['bearing_deg']:.0f}, elev {sun['elevation_deg']:.0f}", fontsize=7.5, zorder=12)
# scale bar + north arrow + title + legend
x0, z0 = b["x"][0] + 30, b["z"][1] - 40
for i in range(4):
    ax.add_patch(Rectangle((x0 + i * 25, z0), 25, 6, fc="black" if i % 2 == 0 else "white", ec="black", lw=0.8, zorder=12))
for v, lab in ((0, "0"), (50, "50"), (100, "100 studs = 30 m")):
    ax.text(x0 + v, z0 + 16, lab, fontsize=8, ha="center", zorder=12)
nx_, nz_ = b["x"][1] - 45, b["z"][0] + 70
ax.add_patch(FancyArrow(nx_, nz_, 0, -40, width=7, head_width=18, head_length=16, color="black", zorder=12))
ax.text(nx_, nz_ - 62, "N", fontsize=16, fontweight="bold", ha="center", zorder=12)
ax.text(nx_, nz_ + 14, "(-Z)", fontsize=8, ha="center", zorder=12)
ax.text(b["x"][0] + 14, b["z"][0] + 18, "SUGARLOAF CANYON - world plan (concept footprints; studs, 1 stud = 0.3 m; contours 45/95/135/172/200)",
        fontsize=13, fontweight="bold", zorder=12, va="top", bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.88))
items = [("hole footprint (concept)", HOLE_COL), ("lower/upper tier of a hole", TIER_COL), ("walkway (dashed), stairs = ticks", "#F7E8C8"),
         ("bridge / dam crest", "#8A5A33"), ("lift (squares) / gondola (dashed)", "#5a2d82"), ("water", "#3FB7C9"),
         ("waterfall", "white"), ("teleport point", "#D8FF6A")]
lx0, lz0 = b["x"][1] - 240, b["z"][1] - 150
ax.add_patch(Rectangle((lx0 - 8, lz0 - 12), 236, 150, fc="white", ec="black", alpha=0.88, zorder=11))
for i, (lab, col) in enumerate(items):
    ax.add_patch(Rectangle((lx0, lz0 + i * 15), 16, 9, fc=col, ec="black", lw=0.5, zorder=12))
    ax.text(lx0 + 22, lz0 + i * 15 + 4.5, lab, fontsize=7.5, va="center", zorder=12)
ax.text(lx0, lz0 + 8 * 15 + 4, "tee = white square, cup = red dot (approx), star = landmark\nhatched = span (hole bridges a gap / river)",
        fontsize=6.8, zorder=12, va="top")
fig.savefig(os.path.join(OUT, "world-map.png"), dpi=150)
plt.close(fig)
print("maps written")
