"""Pass 3: world placements for every world piece (pure numpy; system python or Blender).

  python3 models/_src/world_layout.py   -> models/world/layout.json

Positions are Roblox WORLD studs (base centre / piece origin), yaw in degrees about +Y
(PivotTo(CFrame.new(pos) * CFrame.Angles(0, math.rad(yaw), 0))), scale = [sx, sy, sz] (Model:ScaleTo uses one
number; non-uniform instances list it per axis: resize via MeshPart.Size or keep uniform sy).
Computed placements: highland cliff faces along the scarp, terrace rock faces on steep Rock cells, dock yaw,
boats, sky lanterns, clouds. Others copy world.json backdrop.pieces.
"""
import json, math, os, random
import numpy as np
import world_fit as WF

OUT = os.path.join(WF.MODELS, "world")
W = WF.load_world()
T = WF.Terrain()
PIECES = {p["id"]: p for p in W["backdrop"]["pieces"]}
CEN = W["backdrop"]["center"]


def r3(v):
    return [round(float(x), 2) for x in v]


def yaw_facing(dx, dz):
    """yaw so local +Z points along world (dx, dz)."""
    return math.degrees(math.atan2(dx, dz))


def inst(pos, yaw=0.0, scale=None, note="", src=None):
    d = dict(pos=r3(pos), yaw=round(float(yaw), 1))
    if scale is not None:
        d["scale"] = r3(scale)
    if note:
        d["note"] = note
    if src:
        d["world_json_id"] = src
    return d


def slope_grid():
    gz, gx = np.gradient(T.H, T.cell)
    return gx, gz, np.degrees(np.arctan(np.hypot(gx, gz)))


def keep_boxes():
    H = WF.holes_world(W)
    return WF.hole_obbs(H) + WF.path_obbs(W) + WF.lantern_obbs(W)


def obb_clear(c, yaw, hf, boxes):
    """Sample a piece's oriented footprint box (corners + centre + mids) against keep-outs."""
    a = math.radians(yaw)
    ca, sa = math.cos(a), math.sin(a)
    P = []
    for u in (-1, -0.5, 0, 0.5, 1):
        for w in (-1, 0, 1):
            for v in (0.1, 0.5, 0.9):
                lx, lz = u * hf[0], w * hf[2]
                P.append([c[0] + lx * ca + lz * sa, c[1] + v * 2 * hf[1], c[2] - lx * sa + lz * ca])
    return bool(WF.points_clear(np.array(P), boxes, grow=1.2).all())


def highland(boxes):
    """Cliff faces along the 20-50 stud highland scarp (z ~ -170..-260), facing downhill (south)."""
    out = []
    falls_x = W["waterfalls"][0]["top"][0]
    k = 0
    for x in np.arange(-96, 360, 36.0):
        if abs(x - falls_x) < 22:
            continue
        zs = np.arange(-262, -168, 2.0)
        h = T.height(np.full_like(zs, x), zs)
        dh = -np.gradient(h, 2.0)            # drop going south
        i = int(np.argmax(dh))
        z_mid = zs[i]
        top = float(h[:max(i - 4, 1)].max()) if i > 4 else float(h[0])
        foot_i = min(i + 6, len(zs) - 1)
        bot = float(h[i:foot_i + 1].min())
        drop = top - bot
        if drop < 12:
            continue
        z_foot = zs[i + int(np.argmin(h[i:foot_i + 1]))]
        # local gradient direction for yaw
        e = 3.0
        gx = (T.height(x + e, z_mid) - T.height(x - e, z_mid)) / (2 * e)
        gz = (T.height(x, z_mid + e) - T.height(x, z_mid - e)) / (2 * e)
        yaw = yaw_facing(-gx, -gz)
        pos = [x, bot - 1.5, z_foot - 3.0]
        sy = min(max((drop + 2.5) / 30.0, 0.6), 2.4)
        sxz = sy ** 0.5
        v = "abcd"[k % 4]
        if not obb_clear(pos, yaw, (20 * sxz, 15 * sy, 7 * sxz), boxes):
            continue
        out.append((v, inst(pos, yaw, [sxz, sy, sxz], f"scarp drop {drop:.0f} (top {top:.0f})")))
        k += 1
    return out


def terraces(boxes, n_max=20):
    gx, gz, sl = slope_grid()
    xs = T.x0 + (np.arange(T.cols) + 0.5) * T.cell
    zs = T.z0 + (np.arange(T.rows) + 0.5) * T.cell
    X, Z = np.meshgrid(xs, zs)
    cand = (T.M == 2) & (X > -175) & (X < 250) & (Z > -168) & (Z < 125) & (sl > 50)
    js, is_ = np.nonzero(cand)
    order = np.argsort(-sl[js, is_])
    picked = []
    k = 0
    for o in order:
        j, i = js[o], is_[o]
        x, z = X[j, i], Z[j, i]
        if any(math.hypot(x - p[0], z - p[2]) < 22 for p, _ in picked):
            continue
        tx, tz = W["hollow_tree"]["center"][0], W["hollow_tree"]["center"][2]
        if math.hypot(x - tx, z - tz) < 110 and sum(math.hypot(p[0] - tx, p[2] - tz) < 110 for p, _ in picked) >= 4:
            continue   # at most 4 faces on the tree mound (more reads as a castle wall)
        g = np.array([gx[j, i], gz[j, i]])
        d = -g / (np.linalg.norm(g) + 1e-9)            # downhill
        hs = T.height(x + d[0] * np.arange(-10, 12, 2.0), z + d[1] * np.arange(-10, 12, 2.0))
        top, bot = float(hs.max()), float(hs.min())
        drop = top - bot
        if drop < 4:
            continue
        yaw = yaw_facing(d[0], d[1])
        foot = np.array([x, z]) + d * 3.0
        pos = [foot[0], bot - 1.0, foot[1]]
        sy = min(max((drop + 1.5) / 12.0, 0.6), 2.6)
        if not obb_clear(pos, yaw, (13.5 * sy ** 0.5, 7.5 * sy, 5 * sy ** 0.5), boxes):
            continue
        picked.append((pos, (yaw, sy, drop)))
        if len(picked) >= n_max:
            break
    out = []
    for k, (pos, (yaw, sy, drop)) in enumerate(picked):
        out.append(("abc"[k % 3], inst(pos, yaw, [sy ** 0.5, sy, sy ** 0.5], f"rock face drop {drop:.0f}")))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    boxes = keep_boxes()
    L = {}
    P = PIECES
    tree = W["hollow_tree"]
    L["hollow_tree_world_shell"] = [inst(tree["center"], 0, note="trunk base centre; door at map angle 53.1 deg",
                                         src="hollow_tree_world_shell")]
    L["hollow_tree_crown"] = [inst(P["hollow_tree_crown"]["pos"], 0, note="crown base centre = trunk base + 100",
                                   src="hollow_tree_crown")]
    for sid in ("sister_tree_nw", "sister_tree_sw", "sister_tree_ne"):
        p = P[sid]["pos"]
        L[sid] = [inst([p[0], float(T.height(p[0], p[2])), p[2]], random.Random(sid).uniform(0, 360) if sid != "sister_tree_nw" else 20,
                       note=f"world.json y {p[1]}; y = terrain", src=sid)]
    for wid, wf_name in (("grand_falls_curtain", "Grand Falls"), ("twin_falls_curtain", "Twin Falls"),
                         ("lantern_falls_curtain", "Lantern Falls")):
        wf = [w for w in W["waterfalls"] if w["name"] == wf_name][0]
        dx, dz = wf["bottom"][0] - wf["top"][0], wf["bottom"][2] - wf["top"][2]
        L[wid] = [inst(P[wid]["pos"], yaw_facing(dx, dz), note=f"{wf_name}: top {wf['top']} -> bottom {wf['bottom']}",
                       src=wid)]
    for v, d in highland(boxes):
        L.setdefault(f"highland_cliff_kit_{v}", []).append(d)
    for v, d in terraces(boxes):
        L.setdefault(f"terrace_rock_faces_{v}", []).append(d)
    p = P["old_lantern_tower"]["pos"]
    L["old_lantern_tower"] = [inst([p[0], float(T.height(p[0], p[2])) - 0.5, p[2]], 200, src="old_lantern_tower")]
    p = P["hill_mushroom_houses"]["pos"]
    L["hill_mushroom_houses"] = [inst([p[0], float(T.height(p[0], p[2])) - 0.2, p[2]], -100,
                                      note="doors face roughly west toward the village", src="hill_mushroom_houses")]
    # dock: long axis along the mere's outward normal at the dock point (shore end = local +X)
    lake = W["lakes"][0]
    cx, cz = lake["center"]
    rx, rz = lake["radii"]
    p = P["mere_dock"]["pos"]
    nx, nz = (p[0] - cx) / rx ** 2, (p[2] - cz) / rz ** 2
    n = np.array([nx, nz]) / math.hypot(nx, nz)
    yaw = math.degrees(math.atan2(-n[1], n[0]))       # local +X -> world (cos yaw, -sin yaw) = n
    L["mere_dock"] = [inst([p[0], lake["level"] + 0.5, p[2]], yaw, note="deck top = water + 1.25; shore end local +X",
                           src="mere_dock")]
    rnd = random.Random(8)
    boats = []
    for k in range(8):
        a = TAU * k / 8 + rnd.uniform(-0.3, 0.3)
        q = rnd.uniform(0.25, 0.72)
        boats.append(inst([cx + math.cos(a) * rx * q, lake["level"], cz + math.sin(a) * rz * q], rnd.uniform(0, 360),
                          note="waterline; tween slowly", src="mere_lantern_boats"))
    L["mere_lantern_boat"] = boats
    rnd = random.Random(24)
    sky = []
    tx, tz = tree["center"][0], tree["center"][2]
    while len(sky) < 24:
        y = rnd.uniform(150, 280)
        r = rnd.uniform(100, 170) if y < 225 else rnd.uniform(30, 150)
        a = rnd.uniform(0, TAU)
        sky.append(inst([tx + math.cos(a) * r, y, tz + math.sin(a) * r], rnd.uniform(0, 360), note="drift up slowly",
                        src="sky_lanterns"))
    L["sky_lantern"] = sky
    rnd = random.Random(77)
    for k in range(7):
        az = math.radians(242 - 75 + k * 25 + rnd.uniform(-6, 6)) if k < 4 else math.radians(rnd.uniform(0, 360))
        r = rnd.uniform(1800, 2400)
        x, z = CEN[0] + math.sin(az) * r, CEN[1] - math.cos(az) * r   # compass bearing: 0 = north (-Z)
        L.setdefault(f"cloud_card_{'ab'[k % 2]}", []).append(
            inst([x, rnd.uniform(500, 850), z], yaw_facing(CEN[0] - x, CEN[1] - z), [rnd.uniform(0.8, 1.2)] * 3,
                 note="faces the play area", src="cloud_banks"))
    for k, (pid, p) in enumerate(sorted((i, q) for i, q in P.items() if q["kind"] == "tree_line_cluster")):
        mix = p["colors"].replace("+", "_")
        v = "abc"[k % 3]
        L.setdefault(f"treeline_clump_{v}_{mix}", []).append(
            inst(p["pos"], p["yaw_deg"], [p["size"][0] / 40, p["size"][1] / 45, p["size"][2] / 40], src=pid))
    for k, (pid, p) in enumerate(sorted((i, q) for i, q in P.items() if q["kind"] == "far_forest_hill")):
        v = "ab"[k % 2]
        L.setdefault(f"far_hill_{v}", []).append(
            inst(p["pos"], p["yaw_deg"], [p["size"][0] / 280, p["size"][1] / 100, p["size"][2] / 160], src=pid))
    for k, (pid, p) in enumerate(sorted((i, q) for i, q in P.items() if q["kind"] == "distant_mountain")):
        v = "abc"[k % 3]
        L.setdefault(f"mountain_{v}", []).append(
            inst(p["pos"], p["yaw_deg"], [p["size"][0] / 500, p["size"][1] / 320, p["size"][2] / 300], src=pid))
    json.dump(L, open(os.path.join(OUT, "layout.json"), "w"), indent=1)
    for k, v in L.items():
        print(f"{k:34s} {len(v):3d}")


TAU = math.tau
if __name__ == "__main__":
    main()
