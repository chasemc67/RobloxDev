# Pass 7b fit check: plant_rail_clearance (playtest: tall grass clipped the H1 rails). exec()'d by fitcheck.py after
# fitcheck_pass7.py (uses its namespace: man, DH, HW, RAILS2D, prop_tris from fitcheck_pass6.py, check, lines, np, DL).
# Every dressing instance whose prop has manifest category 'plant' must keep its WHOLE mesh footprint (every triangle
# of the generator geometry at the instance transform, projected to XZ) >= 1.5 studs from every rail / collision wall
# rectangle of every hole. Exact 2D distance, written independently of dressing_world.rail_gap_tris: per wall,
# clip-free polygon distance = 0 if the triangle and rectangle intersect (edge-edge crossing or containment), else
# min over vertex -> segment distances both ways.
lines.append("")
lines.append("# pass 7b: plant_rail_clearance (whole plant footprint >= 1.5 studs from every rail / wall)")
PLANT_CLEAR = 1.5
PLANTS_M = sorted(p["name"] for p in man["props"] if p.get("category") == "plant")


def _seg_pt(P, A, B):
    """distance from points P (..., 2) to segments A->B (..., 2), broadcast."""
    E = B - A
    t = np.clip(((P - A) * E).sum(-1) / np.maximum((E * E).sum(-1), 1e-12), 0, 1)
    return np.linalg.norm(P - (A + t[..., None] * E), axis=-1)


def _cross(a, b):
    return a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0]


def _seg_seg_hit(A, B, C, D):
    """proper or touching intersection of segments A->B and C->D (broadcast)."""
    d1, d2 = _cross(B - A, C - A), _cross(B - A, D - A)
    d3, d4 = _cross(D - C, A - C), _cross(D - C, B - C)
    return (d1 * d2 <= 0) & (d3 * d4 <= 0) & ~((d1 == 0) & (d2 == 0) & (d3 == 0) & (d4 == 0))


def _in_tri(P, T):
    """points P (M, 2) inside triangles T (N, 3, 2) -> (N, M)."""
    s = [_cross(T[:, (i + 1) % 3, None] - T[:, i, None], P[None] - T[:, i, None]) for i in range(3)]
    return ((s[0] >= 0) & (s[1] >= 0) & (s[2] >= 0)) | ((s[0] <= 0) & (s[1] <= 0) & (s[2] <= 0))


def tri_wall_gap(Tw):
    """exact min horizontal distance from world triangles Tw (N, 3, 3) to any wall rectangle (world)."""
    A = Tw[..., [0, 2]]
    ctr = A.reshape(-1, 2).mean(0)
    rad = float(np.linalg.norm(A.reshape(-1, 2) - ctr, axis=1).max())
    best = 1e9
    for (cx, cz, c, s_, hx, hz) in RAILS2D:
        if math.hypot(cx - ctr[0], cz - ctr[1]) - math.hypot(hx, hz) - rad > PLANT_CLEAR + 1.0:
            continue
        # rectangle corners in world XZ (local x axis = (c, -s), local z axis = (s, c): inverse of rail_dist's frame)
        ux, uz = np.array([c, -s_]), np.array([s_, c])
        Q = np.array([cx, cz]) + np.array([ux * a + uz * b for a, b in ((hx, hz), (-hx, hz), (-hx, -hz), (hx, -hz))])
        # triangle vertices -> rectangle edges, rectangle corners -> triangle edges
        d = np.full(len(A), 1e9)
        for i in range(4):
            d = np.minimum(d, _seg_pt(A, Q[i], Q[(i + 1) % 4]).min(1))
        for i in range(3):
            d = np.minimum(d, _seg_pt(Q[None], A[:, i, None], A[:, (i + 1) % 3, None]).min(1))
        # intersection: any edge pair crosses, a triangle vertex inside the rectangle, or a corner inside the triangle
        hit = np.zeros(len(A), bool)
        for i in range(3):
            for j in range(4):
                hit |= _seg_seg_hit(A[:, i], A[:, (i + 1) % 3], Q[j], Q[(j + 1) % 4])
        Lx = (A - [cx, cz]) @ ux
        Lz = (A - [cx, cz]) @ uz
        hit |= ((np.abs(Lx) <= hx) & (np.abs(Lz) <= hz)).any(1)
        hit |= _in_tri(Q, A).any(1)
        d = np.where(hit, 0.0, d)
        best = min(best, float(d.min()))
    return best


def plant_gap(it):
    T, _m = prop_tris(it["prop"])
    return tri_wall_gap((T * it["scale"]) @ DL.yaw_mat(it["world_yaw"]).T + np.array(it["world_pos"], float))


_need = {"grass_tuft", "fern_clump", "red_leaf_bush", "glow_shroom_patch", "toadstool_trio_small"}
_dress_props = {it["prop"] for d in DH.values() for it in d["instances"]}
check("plant set defined by manifest props[].category == 'plant' (covers grass, ferns, bushes, mushroom clumps; "
      "every dressing prop has a category)",
      _need <= set(PLANTS_M) and all(MP[p_].get("category") for p_ in _dress_props),
      f"{len(PLANTS_M)} plant props: {', '.join(PLANTS_M)}")
n_pl, worst = 0, (1e9, "")
for n in range(1, 10):
    bad, gmin = [], 1e9
    for it in DH[f"H{n}"]["instances"]:
        if it["prop"] not in PLANTS_M:
            continue
        n_pl += 1
        g = plant_gap(it)
        gmin = min(gmin, g)
        if g < worst[0]:
            worst = (g, f"H{n} {it['prop']}")
        if g < PLANT_CLEAR - 1e-3:
            bad.append(f"{it['prop']} {g:.2f} at {it['world_pos']}")
        elif "rail_gap" in it and abs(min(it["rail_gap"], 2.5) - min(g, 2.5)) > 0.02:     # both exact up to 2.5
            bad.append(f"{it['prop']} manifest rail_gap {it['rail_gap']} != {g:.3f}")
    check(f"H{n} plant_rail_clearance: every plant's whole footprint >= {PLANT_CLEAR:g} studs from every rail / wall "
          "of every hole (exact triangle vs wall rectangle)", not bad,
          "; ".join(bad[:4]) if bad else f"min gap {gmin:.2f}" if gmin < 1e8 else "no plants")
lines.append(f"  plant instances checked: {n_pl}; closest: {worst[1]} {worst[0]:.2f}")

# negative tests: a grass tuft whose ORIGIN is 1.8 outside an H1 rail but whose blades reach within 1.5 must be
# flagged (footprint, not origin), a tuft right against the rail must be flagged, and one 4 studs out must pass
_h1 = HM[1]
_Tg, _ = prop_tris("grass_tuft")
_rg = float(np.hypot(_Tg[..., 0], _Tg[..., 2]).max())
_pick = None
for _w1 in [w for w in _h1["walls"] if w["id"].startswith("rail")]:
    _c1 = DL.to_world(_h1, _w1["center"])
    _a1 = math.radians(_w1.get("yaw", 0) + _h1["world_yaw"])
    c_, s_ = math.cos(_a1), math.sin(_a1)
    for _dir, _half in (((c_, -s_), _w1["size"][0] / 2), ((-c_, s_), _w1["size"][0] / 2),
                        ((s_, c_), _w1["size"][2] / 2), ((-s_, -c_), _w1["size"][2] / 2)):
        q = np.array([_c1[0], _c1[2]]) + np.array(_dir) * (_half + 4.0)
        if rail_dist(q[0], q[1])[0] >= 4.0 - 1e-3 and rail_dist(q[0], q[1])[0] <= 4.0 + 1e-3:
            _pick = (_c1, np.array(_dir), _half, _w1["id"])
            break
    if _pick:
        break


def _tuft_at(dist_out, scale=1.0):
    c1, d1, half, _id = _pick
    p = np.array([c1[0], c1[2]]) + d1 * (half + dist_out)
    return dict(prop="grass_tuft", scale=scale, world_yaw=0.0, world_pos=[float(p[0]), float(c1[1]), float(p[1])])


_neg_a = _tuft_at(1.8)              # origin 1.8 out, blades (radius ~0.8) reach ~1.0 from the rail
_neg_b = _tuft_at(0.3)
_pos = _tuft_at(4.0)
check(f"negative test flagged: grass_tuft with its origin 1.8 outside H1 {_pick[3]} (blades reach within 1.5)",
      plant_gap(_neg_a) < PLANT_CLEAR and _rg > 0.35, f"gap {plant_gap(_neg_a):.2f}, blade radius {_rg:.2f}")
check("negative test flagged: grass_tuft 0.3 outside an H1 rail (overlapping the rail)",
      plant_gap(_neg_b) < PLANT_CLEAR, f"gap {plant_gap(_neg_b):.2f}")
check("grass_tuft 4 studs outside the same rail is allowed", plant_gap(_pos) >= PLANT_CLEAR,
      f"gap {plant_gap(_pos):.2f}")
