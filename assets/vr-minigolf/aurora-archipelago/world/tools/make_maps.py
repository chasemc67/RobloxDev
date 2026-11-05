"""Render the Aurora Archipelago maps from world.json (adapted from sugarloaf-canyon/world/tools/make_maps.py):

  heightmap.png        16-bit, 1 px = 1 stud, y = gray/65535 * heightmap.y_max (0 = cloud floor / void)
  heightmap-8bit.png   8-bit preview
  materials-map.png    Roblox terrain material per stud, legend in Roblox default material colours
  terrain-4stud.json   heights + material indices on a 4-stud grid for scripted terrain building
  world-map.png        annotated plan (labels placed greedily so they never overlap each other or a footprint)
  world-map-base.png   same plan, shapes only, no text (image-generator reference)

usage: python3 world/tools/make_maps.py [--map-step 2]
"""
import argparse
import json
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
VOIDY = world["void"]["terrain_fill_min_y"]

# ------------------------------------------------------------ heightmap (1 px = 1 stud) + materials
xs, zs, X, Z = W.grid(world)
print("evaluating heightfield", X.shape)
st1 = W.height_at(world, X, Z, stages=True)
Hgt = st1["final"]
y0, y1 = hm["y_min"], hm["y_max"]
g = np.clip((Hgt - y0) / (y1 - y0), 0, 1)
Image.fromarray(np.round(g * 65535).astype(np.uint16)).save(os.path.join(OUT, "heightmap.png"))
Image.fromarray(np.round(g * 255).astype(np.uint8)).save(os.path.join(OUT, "heightmap-8bit.png"))
print("heightmap range %.1f..%.1f" % (Hgt.min(), Hgt.max()))

M1 = W.material_grid(world, X, Z, 1.0, st1)
mat_rgb = np.array([to_rgb(m[1]) for m in W.MATERIALS])
fig = plt.figure(figsize=(14, 14 * 1.0), dpi=110)
ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(mat_rgb[M1], extent=[b["x"][0], b["x"][1], b["z"][1], b["z"][0]], origin="upper", interpolation="nearest")
ax.set_xlim(b["x"][0], b["x"][1])
ax.set_ylim(b["z"][1], b["z"][0])
ax.axis("off")
lx0, lz0 = b["x"][0] + 20, b["z"][0] + 20
ax.add_patch(Rectangle((lx0 - 8, lz0 - 8), 420, 16 * len(W.MATERIALS) + 40, fc="white", ec="black", alpha=0.9, zorder=5))
ax.text(lx0, lz0 + 4, "Roblox terrain materials (default colours) - 1 px = 1 stud", fontsize=9, fontweight="bold", zorder=6, va="center")
counts = np.bincount(M1.ravel(), minlength=len(W.MATERIALS))
for i, (name, col, note) in enumerate(W.MATERIALS):
    yy = lz0 + 22 + 16 * i
    ax.add_patch(Rectangle((lx0, yy - 5), 18, 10, fc=col, ec="black", lw=0.5, zorder=6))
    ax.text(lx0 + 26, yy, f"{name}: {note}  ({counts[i] / M1.size * 100:.1f}%)", fontsize=7.5, va="center", zorder=6)
fig.savefig(os.path.join(OUT, "materials-map.png"), dpi=110)
plt.close(fig)

# terrain-4stud.json: sample at cell centres of a 4-stud grid
xs4, zs4, X4, Z4 = W.grid(world, 4.0)
st4 = W.height_at(world, X4, Z4, stages=True)
M4 = W.material_grid(world, X4, Z4, 4.0, st4)
H4 = np.round(st4["final"], 1)
H4 = np.where(H4 < VOIDY, 0.0, H4)
WS4 = st4["water_surface"]
json.dump(dict(
    note=("Aurora Archipelago terrain on a 4-stud grid. Row r (north -> south), column c (west -> east): cell centre x = x0 + 4*c, "
          "z = z0 + 4*r. height = top surface y; 0 = void (no voxels: cloud floor). material = index into materials. water = water "
          "surface y (null = dry). Fill terrain voxels from y fill_min_y up to height with the cell material (Rock below the top 4 studs "
          "on cliffs), Water from height to water."),
    x0=float(xs4[0]), z0=float(zs4[0]), step=4.0, nx=int(len(xs4)), nz=int(len(zs4)), fill_min_y=VOIDY,
    materials=[m[0] for m in W.MATERIALS],
    height=H4.tolist(), material=M4.astype(int).tolist(),
    water={f"{r},{c}": round(float(WS4[r, c]), 2) for r, c in zip(*np.where(np.isfinite(WS4)))},
), open(os.path.join(OUT, "terrain-4stud.json"), "w"), separators=(",", ":"))
print("materials map + terrain-4stud.json written")

# ------------------------------------------------------------ shaded raster for the maps
step = args.map_step
_, _, Xm, Zm = W.grid(world, step)
st = W.height_at(world, Xm, Zm, stages=True)
Hm = st["final"]
Mm = W.material_grid(world, Xm, Zm, step, st)
WS = st["water_surface"]
wet = np.isfinite(WS) & (Hm < WS - 0.05)
void = Hm < VOIDY
gy, gx = np.gradient(Hm, step)
slope = np.degrees(np.arctan(np.hypot(gx, gy)))

# island tops tinted per tier (snow with a zone hue), cliffs slate-violet rock
top_stops = [(30, "#C9D3EA"), (60, "#DDE7F6"), (84, "#D6F1EC"), (100, "#E4E0F6"), (112, "#F7E3EF"), (146, "#DFEAFB"),
             (182, "#E7E2FA"), (222, "#FFFFFF"), (300, "#FFFFFF")]
ys_, cs_ = zip(*top_stops)
rgb = np.stack([np.interp(Hm, ys_, [to_rgb(c)[i] for c in cs_]) for i in range(3)], -1)
cliff = np.array(to_rgb("#5E6177"))
cw = np.clip((slope - 30) / 20, 0, 1)[..., None]
rgb = rgb * (1 - cw) + cliff * cw
for mname, col in (("Ice", "#A6DDF4"), ("Glacier", "#7FC4F0"), ("Basalt", "#4A4458"), ("Sand", "#6E6272"), ("Cobblestone", "#E6D3AE")):
    rgb = np.where((Mm == W.MAT_INDEX[mname])[..., None], np.array(to_rgb(col)), rgb)
ls = LightSource(azdeg=220, altdeg=40)   # light from the moon side
shade = ls.shade_rgb(rgb, np.where(void, VOIDY, Hm), vert_exag=1.2, blend_mode="soft", fraction=1.0, dx=step, dy=step)
# cloud sea: soft lilac with puffy noise, darker near island cliffs (shadow)
cn = (np.sin(Xm / 23.0) * np.sin(Zm / 31.0) + 0.6 * np.sin(Xm / 9.0 + 1.3) * np.sin(Zm / 13.0 + 0.4) + 0.4 * np.sin((Xm + Zm) / 57.0))
cloud = np.array(to_rgb("#CFC8EE"))[None, None, :] * (0.94 + 0.04 * cn[..., None]) + np.array([0.03, 0.03, 0.05]) * (cn[..., None] > 0.8)
img = np.where(void[..., None], np.clip(cloud, 0, 1), shade)
img = np.where(wet[..., None], np.array(to_rgb("#2FD6C8")) * 0.85 + img * 0.15, img)
ext = [b["x"][0], b["x"][1], b["z"][1], b["z"][0]]

HOLE_COL = "#4FA83D"
TIER_COL = "#86C24A"
BRIDGE_COL = {"ice": "#8FE3FF", "aurora": "#6CFFC0", None: "#8FE3FF"}


def draw_common(ax, text, PX):
    ax.imshow(img, extent=ext, origin="upper", interpolation="bilinear", zorder=0)
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
                ax.plot(xs_, zs_, color="#7A3FB8", lw=1.6, ls=(0, (6, 3)), zorder=7)
                continue
            if t == "lift":
                for e in (s["start"], s["end"]):
                    ax.add_patch(Rectangle((e[0] - 4, e[2] - 4), 8, 8, fc="#7A3FB8", ec="white", lw=0.8, zorder=9))
                ax.plot(xs_, zs_, color="#7A3FB8", lw=2.5, zorder=8)
                continue
            if t in ("bridge", "deck"):
                ax.plot(xs_, zs_, color="#6B4A2B", lw=p["width"] * PX + 2.2, solid_capstyle="butt", zorder=3)   # railings
                ax.plot(xs_, zs_, color=BRIDGE_COL.get(s.get("style")), lw=p["width"] * PX, solid_capstyle="butt", zorder=3.5)
                if s.get("style") == "aurora":
                    ax.plot(xs_, zs_, color="#B07CFF", lw=p["width"] * PX * 0.35, solid_capstyle="butt", zorder=3.6)
                continue
            ax.plot(xs_, zs_, color="#E9D6AE", lw=p["width"] * PX, solid_capstyle="round", zorder=3)
            if s.get("rails"):
                L = math.hypot(xs_[1] - xs_[0], zs_[1] - zs_[0])
                if L > 0:
                    nx, nz = (zs_[1] - zs_[0]) / L, -(xs_[1] - xs_[0]) / L
                    for side in s["rails"]:
                        sg = 1 if side == "left" else -1
                        off = p["width"] / 2 + 0.4
                        ax.plot([xs_[0] + sg * nx * off, xs_[1] + sg * nx * off], [zs_[0] + sg * nz * off, zs_[1] + sg * nz * off],
                                color="#6B4A2B", lw=1.0, zorder=3.7)
            if text:
                ax.plot(xs_, zs_, color="#8a6a40", lw=0.8, ls=(0, (4, 3)), zorder=4)
            if t == "stairs":
                L = math.hypot(xs_[1] - xs_[0], zs_[1] - zs_[0])
                ux, uz = (xs_[1] - xs_[0]) / L, (zs_[1] - zs_[0]) / L
                nx, nz = -uz, ux
                hw = p["width"] / 2
                for k in range(s["steps"] + 1):
                    cx, cz = xs_[0] + ux * s["tread"] * k, zs_[0] + uz * s["tread"] * k
                    ax.plot([cx - nx * hw, cx + nx * hw], [cz - nz * hw, cz + nz * hw], color="#5b3a22", lw=0.6, zorder=5)
    for wf in world["waterfalls"]:
        if wf["frozen"]:
            ax.add_patch(Circle((wf["top"][0], wf["top"][2]), wf["width"] / 2, fc="#BFF3FF", ec="#4FB6E8", lw=1.2, zorder=5))
        else:
            ax.plot([wf["top"][0], wf["bottom"][0]], [wf["top"][2], wf["bottom"][2]], color="white",
                    lw=max(2.5, wf["width"] * PX * 0.6), solid_capstyle="butt", zorder=5)
    # landmark: the Spire
    sp = next(pc for pc in world["backdrop"]["pieces"] if pc["id"] == "starfrost_spire")
    ax.add_patch(Circle((sp["pos"][0], sp["pos"][2]), sp["size"][0] / 2, fc="#9DF7E0", ec="#8A5CFF", lw=2.0, alpha=0.9, zorder=6))
    ax.plot(sp["pos"][0], sp["pos"][2], marker="*", ms=20, color="#B07CFF", mec="white", mew=1.0, zorder=7)
    halo = next(pc for pc in world["backdrop"]["pieces"] if pc["id"] == "halo_arch")
    hx, hz = halo["pos"][0], halo["pos"][2]
    ax.add_patch(Rectangle((hx - halo["size"][0] / 2, hz - halo["size"][2] / 2), halo["size"][0], halo["size"][2],
                           fc="#BFF3FF", ec="#4FB6E8", lw=1.2, alpha=0.75, zorder=7.5))
    for h in world["holes"]:
        pads = W.pads_world(h)
        ymax = max(p["y"] for p in pads)
        for p in pads:
            col = HOLE_COL if (len(pads) == 1 or p["y"] == ymax) else TIER_COL
            ax.add_patch(Polygon(np.array(p["corners"]), closed=True, fc=col, ec="#1f4f1a", lw=1.0, alpha=0.92, zorder=6))
        for spn in h["concept"].get("spans", []):
            x0, x1 = h["concept"]["pads"][0]["x"]
            pl = h["placement"]
            cc = [W.to_world(pl, [x, 0, z])[0::2] for x, z in ((x0, spn["z"][0]), (x1, spn["z"][0]), (x1, spn["z"][1]), (x0, spn["z"][1]))]
            ax.add_patch(Polygon(np.array(cc), closed=True, fc="#CFC8EE", ec="#6B4A2B", lw=0.8, hatch="xxx", zorder=6.5))
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
cs = ax.contour(Xm, Zm, Hm, levels=[45], colors="#3A3470", linewidths=0.6, alpha=0.6, zorder=2)
renderer = fig.canvas.get_renderer()
placed = []          # display-space bboxes of placed labels + obstacles


def disp_box(x0_, z0_, x1_, z1_):
    p0 = ax.transData.transform((x0_, z0_))
    p1 = ax.transData.transform((x1_, z1_))
    return (min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1]))


for lk in world["lakes"]:          # lagoons are obstacles too
    placed.append(disp_box(lk["center"][0] - lk["radii"][0], lk["center"][1] - lk["radii"][1], lk["center"][0] + lk["radii"][0], lk["center"][1] + lk["radii"][1]))
for h in world["holes"]:          # footprints are obstacles for labels
    bb = h["footprint_bbox"]
    placed.append(disp_box(bb["x"][0], bb["z"][0], bb["x"][1], bb["z"][1]))


def overlaps(a, bxs, pad=2):
    return any(not (a[2] + pad < q[0] or q[2] + pad < a[0] or a[3] + pad < q[1] or q[3] + pad < a[1]) for q in bxs)


def place_label(x, z, s, cands, **kw):
    """Try candidate (dx, dz, ha, va) offsets in studs; keep the first label box that hits nothing already placed."""
    best = None
    for (dx, dz, ha, va) in cands:
        t = ax.text(x + dx, z + dz, s, ha=ha, va=va, **kw)
        bb = t.get_window_extent(renderer=renderer).extents
        inside = (bb[0] > 0 and bb[1] > 0 and bb[2] < fig.bbox.width and bb[3] < fig.bbox.height)
        if inside and not overlaps(bb, placed):
            placed.append(tuple(bb))
            if math.hypot(dx, dz) > 14:   # leader line so a pushed-out label still points at its thing
                ax.plot([x, x + dx * 0.92], [z, z + dz * 0.92], color="#3a2a54", lw=0.5, alpha=0.7, zorder=11.5)
            return t
        if best is None:
            best = (dx, dz, ha, va)
        t.remove()
    t = ax.text(x + best[0], z + best[1], s, ha=best[2], va=best[3], **kw)
    placed.append(tuple(t.get_window_extent(renderer=renderer).extents))
    print("label collision kept:", s.split("\n")[0])
    return t


def ring_cands(r, n=16):
    out = []
    for rr in (r, r + 22, r + 46):
        for k in range(n):
            a = 2 * math.pi * k / n
            dx, dz = rr * math.cos(a), rr * math.sin(a)
            ha = "left" if dx > 4 else ("right" if dx < -4 else "center")
            va = "top" if dz > 4 else ("bottom" if dz < -4 else "center")
            out.append((dx, dz, ha, va))
    return out


# hole badges first (fixed), then the big fixed items, then free labels
for h in world["holes"]:
    bb = h["footprint_bbox"]
    cx, cz = (bb["x"][0] + bb["x"][1]) / 2, (bb["z"][0] + bb["z"][1]) / 2
    ax.add_patch(Circle((cx, cz), 9, fc="white", ec="#1f4f1a", lw=1.5, zorder=10))
    ax.text(cx, cz, str(h["number"]), ha="center", va="center", fontsize=9, fontweight="bold", zorder=11)
b0 = dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.9)
ax.text(b["x"][0] + 14, b["z"][0] + 18, "AURORA ARCHIPELAGO - world plan (concept footprints; studs, 1 stud = 0.3 m; void = cloud sea, outline = y 45)",
        fontsize=13, fontweight="bold", zorder=12, va="top", bbox=b0)
placed.append(tuple(ax.texts[-1].get_window_extent(renderer=renderer).extents))
# moon arrow, scale, north, legend (fixed boxes registered as obstacles)
moon = world["moon"]
a = math.radians(moon["bearing_deg"])
sx, sz = math.sin(a), -math.cos(a)
x0s, z0s = b["x"][0] + 150, b["z"][1] - 150
ax.add_patch(FancyArrow(x0s, z0s, sx * 60, sz * 60, width=4, head_width=14, head_length=14, color="#8A7BD8", zorder=12))
ax.add_patch(Circle((x0s + sx * 90, z0s + sz * 90), 14, fc="#F4F1FF", ec="#8A7BD8", lw=2, zorder=12))
ax.text(x0s - 30, z0s - 34, f"low moon + twilight glow\nbearing {moon['bearing_deg']:.0f}, elev {moon['elevation_deg']:.0f}\n(no tee within 45 deg)",
        fontsize=7.5, zorder=12, ha="center", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))
placed.append(disp_box(x0s - 110, z0s - 70, x0s + 40, z0s + 120))
x0, z0 = b["x"][0] + 30, b["z"][1] - 30
for i in range(4):
    ax.add_patch(Rectangle((x0 + i * 25, z0), 25, 6, fc="black" if i % 2 == 0 else "white", ec="black", lw=0.8, zorder=12))
for v, lab, ha_ in ((0, "0", "center"), (50, "50", "center"), (100, "100 studs = 30 m", "left")):
    ax.text(x0 + v + (3 if ha_ == "left" else 0), z0 - 6, lab, fontsize=8, ha=ha_, zorder=12)
placed.append(disp_box(x0 - 10, z0 - 20, x0 + 160, z0 + 10))
nx_, nz_ = b["x"][1] - 45, b["z"][0] + 90
ax.add_patch(FancyArrow(nx_, nz_, 0, -40, width=7, head_width=18, head_length=16, color="black", zorder=12))
ax.text(nx_, nz_ - 62, "N", fontsize=16, fontweight="bold", ha="center", zorder=12)
ax.text(nx_, nz_ + 14, "(-Z)", fontsize=8, ha="center", zorder=12)
placed.append(disp_box(nx_ - 20, nz_ - 80, nx_ + 20, nz_ + 20))
items = [("hole footprint (concept)", HOLE_COL), ("lower/upper tier of a hole", TIER_COL), ("span over open sky (hatched)", "#CFC8EE"),
         ("walkway (dashed), stairs = ticks, brown edge = railing", "#E9D6AE"), ("ice bridge (railed)", "#8FE3FF"), ("aurora skybridge (railed)", "#6CFFC0"),
         ("lift (squares) / gondola (dashed)", "#7A3FB8"), ("hot-spring lagoon", "#2FD6C8"), ("frozen pond", "#A6DDF4"),
         ("frozen waterfall top (circle) / warm falls", "#BFF3FF"), ("teleport pad", "#D8FF6A"), ("cloud sea / void (no terrain)", "#CFC8EE")]
lx0, lz0 = b["x"][0] + 22, b["z"][0] + 50
ax.add_patch(Rectangle((lx0 - 8, lz0 - 12), 298, 225, fc="white", ec="black", alpha=0.9, zorder=11))
for i, (lab, col) in enumerate(items):
    ax.add_patch(Rectangle((lx0, lz0 + i * 15), 16, 9, fc=col, ec="black", lw=0.5, zorder=12))
    ax.text(lx0 + 22, lz0 + i * 15 + 4.5, lab, fontsize=7.3, va="center", zorder=12)
ax.text(lx0, lz0 + len(items) * 15 + 4, "tee = white square, cup = red dot, purple star = Starfrost Spire\nlabels: H# name / par / pad y",
        fontsize=6.8, zorder=12, va="top")
placed.append(disp_box(lx0 - 8, lz0 - 12, lx0 + 290, lz0 + 213))

# teleports + spawn (markers)
for tp in world["teleport_points"]:
    ax.plot(tp["pos"][0], tp["pos"][2], marker="D", ms=6, color="#D8FF6A", mec="black", mew=0.6, zorder=11)
sp = world["spawn"]["pos"]
ax.plot(sp[0], sp[2], marker="P", ms=12, color="#D8FF6A", mec="black", zorder=11)
# scenery dots
SC = {"snowy_pine": "#2F6B4F", "ice_crystal_cluster": "#59D6FF", "frosted_palm": "#3FA06A", "coral_ice": "#FF6FB5",
      "snowpuff_group": "#222233", "lantern_hut": "#C9852F"}
for pc in world["backdrop"]["pieces"]:
    if pc["kind"] in SC:
        ax.plot(pc["pos"][0], pc["pos"][2], marker="o", ms=2.5, color=SC[pc["kind"]], mec="none", zorder=5)
for q in world["lantern_posts"]["positions"]:
    ax.plot(q["pos"][0], q["pos"][2], marker="o", ms=1.6, color="#FFB861", mec="#6B4A2B", mew=0.3, zorder=5.5)

# zone labels (one per zone, pushed outward from the Spire)
spire_xz = next((pc["pos"][0], pc["pos"][2]) for pc in world["backdrop"]["pieces"] if pc["id"] == "starfrost_spire")
ZB = dict(fontsize=10.5, fontweight="bold", color="#3A2A70", style="italic", zorder=11,
          bbox=dict(boxstyle="round,pad=0.25", fc="#F4F1FF", ec="#8A5CFF", alpha=0.85))
for zn in world["zones"]:
    hs = [h for h in world["holes"] if h["number"] in zn["holes"]]
    cx = np.mean([(h["footprint_bbox"]["x"][0] + h["footprint_bbox"]["x"][1]) / 2 for h in hs])
    cz = np.mean([(h["footprint_bbox"]["z"][0] + h["footprint_bbox"]["z"][1]) / 2 for h in hs])
    ox, oz = cx - spire_xz[0], cz - spire_xz[1]
    cands = sorted(ring_cands(80, 24), key=lambda c: -(c[0] * ox + c[1] * oz) / (math.hypot(c[0], c[1]) * math.hypot(ox, oz) + 1e-9))
    place_label(cx, cz, f"{zn['name'].upper()}  y {zn['ground_y']:g}\nH{zn['holes'][0]}-H{zn['holes'][-1]}", cands, **ZB)
# rides and bridges
for p in world["paths"]:
    for s in p["segments"]:
        if s["type"] in ("lift", "bridge", "gondola", "deck") and s.get("name"):
            f = 0.45 if s["type"] != "gondola" else 0.5
            mx = s["start"][0] + (s["end"][0] - s["start"][0]) * f
            mz = s["start"][2] + (s["end"][2] - s["start"][2]) * f
            lab = s["name"] + (f"  {s['end'][1]-s['start'][1]:+.0f}" if s["type"] in ("lift", "gondola") else f"  {W.segment_len2(s):.0f} long")
            place_label(mx, mz, lab, ring_cands(10), fontsize=6.8, color="#5a2d82", fontweight="bold", zorder=12,
                        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="#5a2d82", lw=0.5, alpha=0.85))
# hole labels
for h in world["holes"]:
    n = h["number"]
    bb = h["footprint_bbox"]
    cx, cz = (bb["x"][0] + bb["x"][1]) / 2, (bb["z"][0] + bb["z"][1]) / 2
    r = max(bb["x"][1] - bb["x"][0], bb["z"][1] - bb["z"][0]) / 2 + 6
    ys = sorted({round(p["y"]) for p in W.pads_world(h)})
    place_label(cx, cz, f"H{n} {h['name']}\npar {h['par']} - y {'/'.join(str(y) for y in ys)}", ring_cands(r), fontsize=6.8, zorder=12,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=HOLE_COL, alpha=0.9))
for p in world["paths"]:   # named stairs
    seen = set()
    for s in p["segments"]:
        if s["type"] == "stairs" and s.get("name") and s["name"] not in seen:
            seen.add(s["name"])
            place_label(s["start"][0], s["start"][2], f"{s['name']} (stairs)", ring_cands(12), fontsize=6.6, color="#5b3a22", zorder=12,
                        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8))
# POIs + water
for poi in world["pois"]:
    if poi["id"] in ("lantern_quay_plaza", "great_frozen_falls"):
        continue
    if poi["id"] not in ("starfrost_spire", "halo_arch"):
        ax.plot(poi["pos"][0], poi["pos"][2], marker="*", ms=9, color="#FFB347", mec="#5B3A22", zorder=10)
    big = poi["id"] == "starfrost_spire"
    place_label(poi["pos"][0], poi["pos"][2], poi["name"] + ("\n(skyline landmark, tip y %d)" % round(world['backdrop']['pieces'][0]['pos'][1] + world['backdrop']['pieces'][0]['size'][1]) if big else ""),
                ring_cands(40 if big else 9), fontsize=9 if big else 7, fontweight="bold" if big else "normal", zorder=12, color="#3a1a54",
                bbox=dict(boxstyle="round,pad=0.15", fc="#FFF8EE", ec="#8A5CFF" if big else "none", alpha=0.85))
for wf in world["waterfalls"]:
    place_label(wf["top"][0], wf["top"][2], f"{wf['name']}\n{wf['top'][1]:.0f}->{wf['bottom'][1]:.0f}" + (" (frozen)" if wf["frozen"] else ""),
                ring_cands(10), fontsize=6.3, color="#0b4d6a", zorder=12, bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.75))
for lk in world["lakes"]:
    place_label(lk["center"][0], lk["center"][1], f"{lk['name']}\nwater y {lk['level']:g}", ring_cands(max(lk['radii']) + 4), fontsize=6.8,
                color="#0b5d5a", style="italic", zorder=12, bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.75))
for tp in world["teleport_points"]:
    place_label(tp["pos"][0], tp["pos"][2], "TP " + tp["name"], ring_cands(7), fontsize=6.0, color="#3d5200", zorder=12,
                bbox=dict(boxstyle="round,pad=0.1", fc="#F4FFD8", ec="none", alpha=0.8))
place_label(sp[0], sp[2], "SPAWN / Lantern Quay Plaza", ring_cands(14), fontsize=8, fontweight="bold", zorder=12,
            bbox=dict(boxstyle="round,pad=0.15", fc="#F4FFD8", ec="black", lw=0.5, alpha=0.85))
fig.savefig(os.path.join(OUT, "world-map.png"), dpi=150)
plt.close(fig)
print("maps written")
