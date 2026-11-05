"""Generate heightmap.png (16-bit), heightmap-8bit.png, materials-map.png, materials-legend.png,
world-map.png and world-map-base.png from world.json (+ holes.json footprints).

usage: python3 tools/make_maps.py
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LightSource, LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Circle, Polygon, FancyArrow, Rectangle  # noqa: E402
from PIL import Image  # noqa: E402
from scipy import ndimage  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worldlib as W  # noqa: E402

OUT = W.WORLD_DIR
world = W.load_world()
holes = W.load_holes()
HB = {h["number"]: h for h in holes["holes"]}
PL = {h["number"]: h["placement"] for h in world["holes"]}
b = world["bounds"]
hm = world["heightmap"]
step = hm["stud_per_px"]

xs, zs, X, Z = W.grid(world)
print("evaluating heightfield", X.shape)
st = W.height_at(world, holes, X, Z, stages=True)
Hgt = st["final"]
WS = W.water_surface(world, holes, X, Z)
wet = np.isfinite(WS) & (Hgt < WS - 0.05)


# ------------------------------------------------------------ heightmap
y0, y1 = hm["y_min"], hm["y_max"]
g = np.clip((Hgt - y0) / (y1 - y0), 0, 1)
Image.fromarray(np.round(g * 65535).astype(np.uint16)).save(os.path.join(OUT, "heightmap.png"))
Image.fromarray(np.round(g * 255).astype(np.uint8)).save(os.path.join(OUT, "heightmap-8bit.png"))
print("heightmap range", float(Hgt.min()), float(Hgt.max()))

# ------------------------------------------------------------ materials
mat = world["materials"]
leg = {m["key"]: m for m in mat["legend"]}
gy, gx = np.gradient(Hgt, step)
slope = np.degrees(np.arctan(np.hypot(gx, gy)))
cls = np.full(Hgt.shape, "grass", dtype=object)
leafy = np.zeros(Hgt.shape, bool)
rim = world["terrain"]["rim"]
for zn in mat["material_zones"]:
    if "rim_q_min" in zn:
        p = rim["exponent"]
        q = ((np.abs(X - rim["center"][0]) / rim["half_size"][0]) ** p + (np.abs(Z - rim["center"][1]) / rim["half_size"][1]) ** p) ** (1 / p)
        leafy |= q > zn["rim_q_min"]
    else:
        leafy |= W._shape_dist(zn["shape"], X, Z) == 0
cls[leafy] = "leafy"
# sand near water
stream_wet = np.zeros(Hgt.shape, bool)
_, surf_sl = W.water_profile(world, X, Z)
dist_w = ndimage.distance_transform_edt(~wet) * step
lake_mask = np.zeros(Hgt.shape, bool)
for lk in world["lakes"]:
    q = np.hypot((X - lk["center"][0]) / lk["radii"][0], (Z - lk["center"][1]) / lk["radii"][1])
    lake_mask |= q <= 1
dist_lake = ndimage.distance_transform_edt(~lake_mask) * step
# water level reference near each dry pixel: nearest wet pixel's surface
idx = ndimage.distance_transform_edt(~wet, return_distances=False, return_indices=True)
near_surf = np.where(wet, WS, WS[idx[0], idx[1]]) if wet.any() else np.full(Hgt.shape, -1e9)
sand = (~wet) & (((dist_w <= 3) | (dist_lake <= 10)) & (Hgt < near_surf + 1.5))
cls[sand] = "sand"
cls[slope > 40] = "rock"
# paths + plazas
pathm = np.zeros(Hgt.shape, bool)
for p in world["paths"]:
    for s in p["segments"]:
        if s["type"] == "on_hole":
            continue
        d, _ = W.seg_dist(X, Z, (s["start"][0], s["start"][2]), (s["end"][0], s["end"][2]))
        pathm |= d <= p["width"] / 2
for poi in world["pois"]:
    if poi.get("kind") == "plaza":
        pathm |= np.hypot(X - poi["pos"][0], Z - poi["pos"][2]) <= poi["radius"]
cls[pathm] = "path"
cls[wet] = "water"
rgb = np.zeros(Hgt.shape + (3,), np.uint8)
counts = {}
for k, m in leg.items():
    sel = cls == k
    rgb[sel] = m["rgb"]
    counts[k] = round(100 * sel.mean(), 1)
Image.fromarray(rgb).save(os.path.join(OUT, "materials-map.png"))
print("materials %", counts)

# legend image
fig, ax = plt.subplots(figsize=(4.2, 3.0), dpi=150)
ax.axis("off")
for i, m in enumerate(mat["legend"]):
    ax.add_patch(Rectangle((0, -i), 0.8, 0.8, color=np.array(m["rgb"]) / 255))
    ax.text(1.0, -i + 0.4, f"{m['key']}  ->  {m['roblox']}  rgb{tuple(m['rgb'])}", va="center", fontsize=8)
ax.set_xlim(0, 8)
ax.set_ylim(-len(mat["legend"]) + 0.6, 1)
ax.set_title("materials-map.png legend", fontsize=9)
fig.savefig(os.path.join(OUT, "materials-legend.png"), bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------ maps
ext = [b["x"][0], b["x"][1], b["z"][1], b["z"][0]]  # imshow: top row = north (min z)
terr_cmap = LinearSegmentedColormap.from_list("lg", [
    (0.0, "#5f8f4a"), (0.15, "#7aa456"), (0.30, "#a9b866"), (0.45, "#c9b66a"),
    (0.62, "#b08a55"), (0.80, "#8f7a6a"), (1.0, "#d9d2c5")])
ls = LightSource(azdeg=300, altdeg=40)
norm = np.clip((Hgt - 0) / 120, 0, 1)
rgb_t = terr_cmap(norm)[..., :3]
# leafy zones a touch more orange (autumn forest floor)
lf = ndimage.gaussian_filter(leafy.astype(float), 12 / step)[..., None] * (~wet[..., None])
rgb_t = rgb_t * (1 - 0.18 * lf) + np.array([0.85, 0.45, 0.2]) * 0.18 * lf
shade = ls.shade_rgb(rgb_t, Hgt, vert_exag=1.3, blend_mode="soft", dx=step, dy=step)
water_rgb = np.array([0x4A, 0xA3, 0xDF]) / 255
img = np.where(wet[..., None], water_rgb * 0.85 + shade * 0.15, shade)


def rect_poly(c):
    return np.array(c)


def draw_common(ax, text):
    ax.imshow(img, extent=ext, origin="upper", interpolation="bilinear", zorder=0)
    # paths
    for p in world["paths"]:
        for s in p["segments"]:
            xs_ = [s["start"][0], s["end"][0]]
            zs_ = [s["start"][2], s["end"][2]]
            if s["type"] == "on_hole":
                if text:
                    ax.plot(xs_, zs_, color="#6b4a2b", lw=1.0, ls=":", zorder=3)
                continue
            lw = p["width"] * PX
            ax.plot(xs_, zs_, color="#e9d3a4", lw=lw, solid_capstyle="round", zorder=3)
            if text:
                ax.plot(xs_, zs_, color="#7a5530", lw=1.2, ls=(0, (4, 3)), zorder=4)
            if s["type"] == "stairs":
                L = math.hypot(xs_[1] - xs_[0], zs_[1] - zs_[0])
                ux, uz = (xs_[1] - xs_[0]) / L, (zs_[1] - zs_[0]) / L
                nx, nz = -uz, ux
                hw = p["width"] / 2
                for k in range(s["steps"] + 1):
                    cx, cz = xs_[0] + ux * s["tread"] * k, zs_[0] + uz * s["tread"] * k
                    ax.plot([cx - nx * hw, cx + nx * hw], [cz - nz * hw, cz + nz * hw], color="#5b3a22", lw=0.7, zorder=5)
    # holes
    for n, pl in PL.items():
        h = HB[n]
        for f in W.felt_world(h, pl):
            col = "#86C24A" if f["overlay"] else ("#4F9A3A" if not f["bridge"] else "#a07a4a")
            ax.add_patch(Polygon(rect_poly(f["corners"]), closed=True, fc=col, ec="none", zorder=6))
        for w in W.walls_world(h, pl):
            ax.add_patch(Polygon(rect_poly(w["corners"]), closed=True, fc="#8A5A33" if text else "#B8AFA0", ec="none", zorder=7))
        for hz in h["hazards"]:
            c = W.to_world(pl, hz["center"])
            cc = W.rect_corners(c[0], c[2], hz["size"][0], hz["size"][1], hz["yaw"] + pl["yaw_deg"])
            ax.add_patch(Polygon(np.array(cc), closed=True, fc="#4AA3DF" if hz["type"] == "water" else "#3b2a1a", ec="none", alpha=0.9, zorder=5.5))
    # tree
    t = world["hollow_tree"]
    tc = (t["center"][0], t["center"][2])
    ax.add_patch(Circle(tc, t["crown"]["radius_xz"], fc="#F2B632", ec="#E8862E", lw=1.5, alpha=0.22 if text else 0.30, zorder=8))
    ax.add_patch(Circle(tc, t["root_flare_radius"], fc="none", ec="#5B3A22", lw=1.0, ls="--" if text else "-", alpha=0.6, zorder=8))
    ax.add_patch(Circle(tc, t["trunk_outer_radius"], fc="none", ec="#5B3A22", lw=(t["wall_thickness"]) * PX, alpha=0.85, zorder=8.5))
    # doorway gap
    a = math.radians(t["doorway"]["angle_deg"])
    half = t["doorway"]["width"] / 2 / t["trunk_outer_radius"]
    th = np.linspace(a - half, a + half, 12)
    rr = t["trunk_outer_radius"]
    ax.plot(tc[0] + rr * np.cos(th), tc[1] + rr * np.sin(th), color="#e9d3a4", lw=(t["wall_thickness"] + 1) * PX, zorder=8.6)
    # waterfalls
    for wf in world["waterfalls"]:
        ax.plot([wf["top"][0], wf["bottom"][0]], [wf["top"][2], wf["bottom"][2]], color="white", lw=max(2, wf["width"] * PX * 0.7), zorder=5, solid_capstyle="butt")


PX = 0  # set per figure (points per stud)


def make_fig(text):
    global PX
    W_in = 16
    span_x = b["x"][1] - b["x"][0]
    span_z = b["z"][1] - b["z"][0]
    fig = plt.figure(figsize=(W_in, W_in * span_z / span_x), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    PX = W_in * 72 / span_x  # points per stud
    draw_common(ax, text)
    ax.set_xlim(b["x"][0], b["x"][1])
    ax.set_ylim(b["z"][1], b["z"][0])
    ax.axis("off")
    return fig, ax


# ---- base (no text)
fig, ax = make_fig(False)
fig.savefig(os.path.join(OUT, "world-map-base.png"), dpi=150)
plt.close(fig)

# ---- annotated
fig, ax = make_fig(True)
lev = np.arange(0, 141, 4)
cs = ax.contour(X, Z, Hgt, levels=lev, colors="#3d3426", linewidths=0.35, alpha=0.55, zorder=2)
cs2 = ax.contour(X, Z, Hgt, levels=np.arange(0, 141, 20), colors="#2b2419", linewidths=0.9, alpha=0.7, zorder=2)
ax.clabel(cs2, fmt="%d", fontsize=7, inline=True, inline_spacing=2)
for n, pl in PL.items():
    h = HB[n]
    hw = next(x for x in world["holes"] if x["number"] == n)
    bb = hw["footprint_bbox"]
    cx = (bb["x"][0] + bb["x"][1]) / 2
    cz = (bb["z"][0] + bb["z"][1]) / 2
    t = hw["tee_world"]
    c = hw["cup_world"]
    ax.plot(t[0], t[2], marker="s", ms=4, color="white", mec="black", zorder=9)
    ax.plot(c[0], c[2], marker="o", ms=4, color="#D8392B", mec="black", zorder=9)
    tr_ = world["hollow_tree"]
    LAB = {6: (bb["x"][0] - 6, cz, "right"), 7: (bb["x"][1] + 18, cz + 14, "left"),
           8: (bb["x"][1] + 4, cz + 18, "left"), 3: (bb["x"][1] + 4, cz + 22, "left"), 9: (tr_["center"][0], tr_["center"][2] - tr_["trunk_outer_radius"] - 16, "center")}
    lx, cz, ha = LAB.get(n, (bb["x"][1] + 4, cz, "left"))
    ax.text(lx, cz, f"H{n}  par {h['par']}\n{h['name']}\ny {pl['origin'][1]:.0f}", fontsize=9, fontweight="bold", ha=ha, va="center",
            color="black", zorder=12, bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#4F9A3A", alpha=0.85))
tr = world["hollow_tree"]
ax.text(tr["center"][0], tr["center"][2] + tr["trunk_outer_radius"] + 22, "Giant Hollow Tree\n(H9 inside)", ha="center", fontsize=9,
        fontweight="bold", color="#5B3A22", zorder=12, bbox=dict(boxstyle="round,pad=0.2", fc="#fff3d6", ec="#E8862E", alpha=0.85))
for wf in world["waterfalls"]:
    ax.text(wf["top"][0] + 7, (wf["top"][2] + wf["bottom"][2]) / 2, f"{wf['name']}\n{wf['top'][1]:.0f}->{wf['bottom'][1]:.0f}", fontsize=6.5,
            color="#0b4d7a", zorder=12, va="center", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.7))
for poi in world["pois"]:
    if poi["kind"] == "waterfall":
        continue
    if poi["id"] in ("lantern_torii", "mill"):
        ax.plot(poi["pos"][0], poi["pos"][2], marker="*", ms=7, color="#FFB347", mec="#5B3A22", zorder=10)
        continue
    ax.plot(poi["pos"][0], poi["pos"][2], marker="*", ms=9, color="#FFB347", mec="#5B3A22", zorder=10)
    ax.text(poi["pos"][0] + 4, poi["pos"][2] - 4, poi["name"], fontsize=7, zorder=12, color="#3a2a14",
            bbox=dict(boxstyle="round,pad=0.12", fc="#fff8e6", ec="none", alpha=0.75))
lp = np.array([l["pos"] for l in world["lanterns"]["points"]])
ax.scatter(lp[:, 0], lp[:, 2], s=4, color="#FFB347", edgecolors="#8a5a00", linewidths=0.3, zorder=9)
sp = world["spawn"]["pos"]
ax.plot(sp[0], sp[2], marker="P", ms=11, color="#D8FF6A", mec="black", zorder=11)
ax.text(sp[0] + 5, sp[2] + 6, "SPAWN", fontsize=8, fontweight="bold", zorder=12)
lk = world["lakes"][0]
ax.text(lk["center"][0], lk["center"][1], f"{lk['name']}\nwater {lk['level']:.0f}", ha="center", fontsize=9, color="white", style="italic", zorder=12)
st_ = world["stream"]["points"]
ax.text(st_[2]["x"] + 8, st_[2]["z"], f"{world['stream']['name']}", fontsize=8, color="#0b4d7a", style="italic", zorder=12)
# scale bar
x0, z0 = b["x"][0] + 25, b["z"][1] - 30
for i in range(4):
    ax.add_patch(Rectangle((x0 + i * 25, z0), 25, 5, fc="black" if i % 2 == 0 else "white", ec="black", lw=0.8, zorder=12))
ax.text(x0, z0 + 13, "0", fontsize=8, ha="center", zorder=12)
ax.text(x0 + 100, z0 + 13, "100 studs = 30 m", fontsize=8, ha="center", zorder=12)
ax.text(x0 + 50, z0 + 13, "50", fontsize=8, ha="center", zorder=12)
# north arrow
nx_, nz_ = b["x"][1] - 40, b["z"][0] + 60
ax.add_patch(FancyArrow(nx_, nz_, 0, -35, width=6, head_width=16, head_length=14, color="black", zorder=12))
ax.text(nx_, nz_ - 56, "N", fontsize=16, fontweight="bold", ha="center", zorder=12)
ax.text(nx_, nz_ + 12, "(-Z)", fontsize=8, ha="center", zorder=12)
# title + legend
ax.text(b["x"][0] + 12, b["z"][0] + 16, "LANTERN GROVE - world plan (studs; contours 4, labels 20; 1 stud = 0.3 m)", fontsize=13,
        fontweight="bold", zorder=12, va="top", bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.85))
leg_items = [("felt / green", "#4F9A3A"), ("rails", "#8A5A33"), ("walkway (dashed), stairs = ticks", "#e9d3a4"),
             ("water", "#4AA3DF"), ("waterfall", "white"), ("lantern post", "#FFB347"), ("tree crown", "#F2B632")]
lx0, lz0 = b["x"][1] - 210, b["z"][1] - 110
ax.add_patch(Rectangle((lx0 - 6, lz0 - 10), 210, 104, fc="white", ec="black", alpha=0.85, zorder=11))
for i, (lab, col) in enumerate(leg_items):
    ax.add_patch(Rectangle((lx0, lz0 + i * 13), 14, 8, fc=col, ec="black", lw=0.5, zorder=12))
    ax.text(lx0 + 20, lz0 + i * 13 + 4, lab, fontsize=7.5, va="center", zorder=12)
ax.text(lx0, lz0 + 7 * 13 + 2, "tee = white square, cup = red dot, star = POI", fontsize=7, zorder=12)
fig.savefig(os.path.join(OUT, "world-map.png"), dpi=150)
plt.close(fig)
print("maps written")

# ------------------------------------------------------------ 4-stud voxel export for scripted terrain building
import json  # noqa: E402
s4 = 4
xs4 = np.arange(b["x"][0] + s4 / 2, b["x"][1], s4)
zs4 = np.arange(b["z"][0] + s4 / 2, b["z"][1], s4)
X4, Z4 = np.meshgrid(xs4, zs4)
H4 = W.height_at(world, holes, X4, Z4)
WS4 = W.water_surface(world, holes, X4, Z4)
# material per cell = majority of the 1-stud class map in that cell
keys = [m["key"] for m in mat["legend"]]
code = np.zeros(cls.shape, np.int8)
for i, k in enumerate(keys):
    code[cls == k] = i
ny, nx = H4.shape
cm = code[: ny * 4, : nx * 4].reshape(ny, 4, nx, 4).transpose(0, 2, 1, 3).reshape(ny, nx, 16)
maj = np.apply_along_axis(lambda v: np.bincount(v, minlength=len(keys)).argmax(), 2, cm)
out = dict(note="Row-major, row 0 = north (z min). Cell (i=col, j=row) centre x = x0 + (i+0.5)*cell, z = z0 + (j+0.5)*cell. "
                "height = terrain surface y; water = water surface y or null; mat = index into materials.",
           x0=b["x"][0], z0=b["z"][0], cell=s4, cols=int(nx), rows=int(ny), materials=[m["roblox"] for m in mat["legend"]],
           height=np.round(H4, 1).tolist(), water=[[None if not np.isfinite(v) else round(float(v), 2) for v in row] for row in WS4],
           mat=maj.astype(int).tolist())
with open(os.path.join(OUT, "terrain-4stud.json"), "w") as f:
    json.dump(out, f, separators=(",", ":"))
print("terrain-4stud.json", nx, "x", ny)
