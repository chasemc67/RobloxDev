# Pass 8 fit checks (lantern-lit H9, rail lanterns on the H7 lower tiers and H8, brighter H8 emissives). exec()'d by
# fitcheck.py after fitcheck_pass7b.py (uses its namespace: man, DH, HM, HW, RAILS2D, prop_tris, tri_wall_gap,
# _seg_seg_hit, _in_tri, check, lines, np, DL, lglib). Generic dressing checks (keep-outs, world pieces, felt margin,
# clear-above-felt, tall props >= 3 from rails, near field <= 34k) already cover every new instance; hanging lanterns
# are exempt from terrain grounding (checked here instead: height above the felt).
lines.append("")
lines.append("# pass 8: hanging lanterns (H9), rail lanterns (H7 lower tiers, H8), lights[], H8 emissives")
AMBER3 = [255, 169, 87]
LIGHTS = man.get("lights", [])
LBY = {q["id"]: q for q in LIGHTS}
HANG_ZONES = ("corridor", "chamber", "heart")              # the H9 corridor -> chamber -> heart green footprint
H7_LOWER = ("rail4", "rail5", "rail6", "rail9", "rail10", "rail11", "rail12", "rail13")


def placed_world(it):
    T, mats = prop_tris(it["prop"])
    return (T * it["scale"]) @ DL.yaw_mat(it["world_yaw"]).T + np.array(it["world_pos"], float), mats


def glow_core(it):
    Tw, mats = placed_world(it)
    return Tw[mats == "Glow"].reshape(-1, 3).mean(0)


def felt_top_under(n, x, z):
    """highest felt top (hole-local y) of hole n under world (x, z), or None."""
    Rw, off = DL.hole_xf(HM[n])
    L = (np.array([x, 0, z]) - off) @ Rw
    tops = [(r[5], f) for r, f in zip(DL.felt_rects(HM[n]), HM[n]["felt"])
            if DL.rect_dist(np.array([L[0]]), np.array([L[2]]), r)[0] <= 0]
    return max(tops, key=lambda t: t[0]) if tops else None


FELT2D = []
for _h in HW:
    for _f in _h["felt"]:
        _c = DL.to_world(_h, _f["center"])
        _a = math.radians(_f.get("yaw", 0) + _h["world_yaw"])
        FELT2D.append((_c[0], _c[2], math.cos(_a), math.sin(_a), _f["size"][0] / 2, _f["size"][1] / 2))


def over_felt(Tw):
    """True if any triangle of Tw (world) overlaps any felt rectangle of any hole in XZ (exact 2D test)."""
    A = Tw[..., [0, 2]]
    ctr = A.reshape(-1, 2).mean(0)
    rad = float(np.linalg.norm(A.reshape(-1, 2) - ctr, axis=1).max())
    for (cx, cz, c, s_, hx, hz) in FELT2D:
        if math.hypot(cx - ctr[0], cz - ctr[1]) > math.hypot(hx, hz) + rad:
            continue
        ux, uz = np.array([c, -s_]), np.array([s_, c])
        Q = np.array([cx, cz]) + np.array([ux * a + uz * b for a, b in ((hx, hz), (-hx, hz), (-hx, -hz), (hx, -hz))])
        Lx, Lz = (A - [cx, cz]) @ ux, (A - [cx, cz]) @ uz
        if ((np.abs(Lx) <= hx) & (np.abs(Lz) <= hz)).any() or _in_tri(Q, A).any():
            return True
        for i in range(3):
            for j in range(4):
                if _seg_seg_hit(A[:, i], A[:, (i + 1) % 3], Q[j], Q[(j + 1) % 4]).any():
                    return True
    return False


def light_problem(it, kind, rng_lo, rng_hi):
    q = LBY.get(it.get("light_id"))
    if q is None:
        return "no lights[] entry"
    if q["kind"] != kind or q["light"] != "PointLight" or list(q["color3"]) != AMBER3 or \
            q["color"].upper() != "#FFA957":
        return f"{q['id']} not an amber PointLight ({q['color3']})"
    if not (rng_lo <= q["range"] <= rng_hi) or not (0.3 <= q["brightness"] <= 5):
        return f"{q['id']} range/brightness {q['range']}/{q['brightness']}"
    d = float(np.linalg.norm(np.array(q["world_pos"]) - glow_core(it)))
    if d > 0.25:
        return f"{q['id']} {d:.2f} from the lantern centre"
    return None


def hang_problem(it, n=9):
    """height of the lantern bottom above the local felt 7..9, centre over the corridor / chamber / heart felt."""
    Tw, mats = placed_world(it)
    lant = Tw[np.isin(mats, ["Paper", "RootBark", "Glow", "ToadRed"])].reshape(-1, 3)
    c = lant.mean(0)
    ft = felt_top_under(n, c[0], c[2])
    if ft is None or ft[1]["zone"] not in HANG_ZONES:
        return f"not over the H9 corridor/chamber/heart felt ({ft[1]['zone'] if ft else 'no felt'})"
    bottom = float(lant[:, 1].min()) - DL.to_world(HM[n], [0, ft[0], 0])[1]
    if not (7.0 - 1e-3 <= bottom <= 9.0 + 1e-3):
        return f"bottom {bottom:.2f} above the {ft[1]['id']} felt"
    return None


SEE = {"rail_lantern_stake": 0.2, "rail_lantern_crook": 0.8}


def lantern_visible(n, it, Tw=None, mats=None):
    """stake: lantern top >= rail top + 0.2; crook: lantern centre >= rail top + 0.8 (H8's 3.9-tall walls)."""
    if Tw is None:
        Tw, mats = placed_world(it)
    lant = Tw[np.isin(mats, ["Paper", "Glow"])].reshape(-1, 3)
    y = (lant[:, 1].max() if it["prop"] == "rail_lantern_stake" else lant[:, 1].mean()) - HM[n]["world_offset"][1]
    return y >= it["wall_top"] + SEE[it["prop"]] - 1e-3, y


def rail_problem(it, n=None):
    Tw, mats = placed_world(it)
    g = tri_wall_gap(Tw)
    if g < 0.25:
        return f"clips a rail (gap {g:.2f})"
    if over_felt(Tw):
        return "over felt"
    if n is not None and not lantern_visible(n, it, Tw, mats)[0]:
        return f"hidden below its rail top ({lantern_visible(n, it, Tw, mats)[1]:.2f} vs {it['wall_top']})"
    return None


def rail_spot_blocked(n, prop, origin, yaw_w, wall_top):
    """independent re-test of a skipped rail-lantern spot: why a lantern could NOT stand there (None = it could)."""
    xs, zs = [origin[0]], [origin[2]]
    for k in range(8):
        for f_ in (0.3, 0.6):
            xs.append(origin[0] + math.cos(k * math.tau / 8) * f_)
            zs.append(origin[2] + math.sin(k * math.tau / 8) * f_)
    if water_at(xs, zs):
        return "water"
    hs = TER.height(np.array(xs), np.array(zs))
    if hs.max() - hs.min() > 1.5 + 1e-3:
        return "slope"
    it = dict(prop=prop, scale=1.0, world_yaw=yaw_w, wall_top=wall_top,
              world_pos=[origin[0], float(hs.min() + 0.3 * (hs.max() - hs.min()) - 0.05), origin[2]])
    Tw, mats = placed_world(it)
    P = np.concatenate([Tw.reshape(-1, 3), Tw.mean(1)])
    k = WF.check_tris(Tw, KO)
    if k:
        return kind_of(next(iter(k)))
    o = OCC.hits(P, first_only=True)
    if o:
        return kind_of(next(iter(o)))
    if tree_rule(n, P):
        return "tree_shell"
    if tall_rail_problem(it) is not None:
        return "tall_near_rail"
    if not lantern_visible(n, it, Tw, mats)[0]:
        return "below_rail_top"
    return None


# 1. H9 hanging lanterns
hang = [it for it in DH["H9"]["instances"] if it["role"] == "hang"]
bad, info = [], []
for it in hang:
    p_ = hang_problem(it) or light_problem(it, "hanging_lantern", 16, 16)
    if p_:
        bad.append(f"{it['marks']}: {p_}")
    info.append(f"{it['marks'].split(':')[1]} {np.round(glow_core(it), 1).tolist()}")
check("H9: 3 hanging paper lanterns (lantern_large_hanging), bottom 7..9 above the local felt, centre over the "
      "corridor / chamber / heart felt, amber PointLight (Range 16) at each lantern centre",
      len(hang) == 3 and not bad, "; ".join(bad) if bad else "; ".join(info))
# Round 7 final (brief addendum): positions = holes.json decoration anchors amber_lantern_1..3 (props.md), the
# lantern bottom at the anchor y, lantern size ~1.2 x 1.8 x 1.2
ANC = {a["name"]: a for a in HM[9].get("decoration_anchors", []) if a["name"].startswith("amber_lantern_")}


def anchor_problem(it):
    a = ANC.get(it.get("anchor"))
    if a is None:
        return "no holes.json amber_lantern anchor"
    Tw, mats = placed_world(it)
    lant = Tw[np.isin(mats, ["Paper", "RootBark", "Glow", "ToadRed"])].reshape(-1, 3)
    Rw, off = DL.hole_xf(HM[9])
    L = (lant - off) @ Rw
    c = (L.min(0) + L.max(0)) / 2
    sz = L.max(0) - L.min(0)
    if abs(c[0] - a["position"][0]) > 0.05 or abs(c[2] - a["position"][2]) > 0.05:
        return f"centre ({c[0]:.2f}, {c[2]:.2f}) != anchor {a['position']}"
    if abs(L[:, 1].min() - a["position"][1]) > 0.05:
        return f"bottom {L[:, 1].min():.2f} != anchor y {a['position'][1]}"
    if np.abs(sz - np.array(a.get("approx_size", sz))).max() > 0.2:
        return f"size {np.round(sz, 2).tolist()} vs props.md {a.get('approx_size')}"
    return None


ap = [f"{it.get('anchor')}: {anchor_problem(it)}" for it in hang if anchor_problem(it)]
check("H9 hanging lanterns on the holes.json Round-7 anchors amber_lantern_1..3 (centre x/z and bottom y within "
      "0.05, size ~1.2 x 1.8 x 1.2 within 0.2)", len(ANC) == 3 and len(hang) == 3 and not ap and
      {it.get("anchor") for it in hang} == set(ANC), "; ".join(ap) if ap else
      ", ".join(f"{it['anchor']} {it['pos']}" for it in hang))
th = [p["triangles"] for p in man["props"] if p["name"] == "lantern_large_hanging"]
check("lantern_large_hanging reuses the lantern_large paper lantern (same Paper/Glow tris) + cord, < 20k tris",
      bool(th) and th[0] < 20000 and
      {q["material"]: q["tris"] for q in MP["lantern_large"]["parts"] if q["material"] != "Iron"}.items() <=
      {q["material"]: q["tris"] for q in MP["lantern_large_hanging"]["parts"] if q["material"] != "Iron"}.items(),
      f"{th[0] if th else '?'} tris")

check("hero heart_lantern_cluster no longer placed (Round 7: replaced by the 3 hanging lanterns); any hanging "
      "lantern inside a cluster box would need a >= 0.6 mesh gap (none now)",
      not MP["heart_lantern_cluster"]["placements"] and all(g >= 0.6 - 1e-3 for g in CL_GAPS),
      f"placements {MP['heart_lantern_cluster']['placements']}, mesh gaps {CL_GAPS}")
_off = dict(hang[0], world_pos=(np.array(hang[0]["world_pos"]) + [1.0, 0, 0.0]).tolist())
check("negative test flagged: hanging lantern 1 stud off its anchor", anchor_problem(_off) is not None,
      anchor_problem(_off) or "")

# 2. rail lanterns
n_rail = 0
for n in (7, 8):
    rl = [it for it in DH[f"H{n}"]["instances"] if it["role"] == "rail"]
    n_rail += len(rl)
    bad, sps = [], {}
    for it in rl:
        p_ = rail_problem(it, n) or light_problem(it, "rail_lantern", 8, 12)
        if n == 7 and it["wall"] not in H7_LOWER:
            p_ = p_ or f"wall {it['wall']} is not on the H7 lower tiers"
        if p_:
            bad.append(f"{it['light_id']}: {p_}")
    for side in ("left", "right"):
        seq = sorted((it for it in rl if it["side"] == side), key=lambda q: q["seq"])
        cs = [glow_core(it) for it in seq]
        sps[side] = [round(float(np.linalg.norm((a - b)[[0, 2]])), 2) for a, b in zip(cs, cs[1:])]
    nl = {s: len(v) + 1 for s, v in sps.items()}
    check(f"H{n} rail lanterns ({'lower tiers' if n == 7 else 'whole hole'}): >= 2 per side, none clips a rail "
          "(exact gap >= 0.25), none over any felt (exact), each with an amber PointLight (Range 8..12) at its centre",
          all(v >= 2 for v in nl.values()) and not bad, "; ".join(bad[:4]) if bad else f"{len(rl)} lanterns {nl}")
    allsp = sps["left"] + sps["right"]
    # a pair > 12 apart is allowed only where EVERY candidate spot 8..12 from the previous lantern is blocked
    # (re-tested here independently: water, slope, keep-outs incl. walkways / felt / heroes, world pieces, tall rule,
    # hidden below the rail top)
    gaps, gap_bad = [], []
    for it in rl:
        if it.get("chain_gap_before") is None:
            continue
        win = it.get("gap_window") or []
        why = {}
        for q in win:
            r_ = rail_spot_blocked(n, q["prop"], q["origin"], q["yaw"], q["wall_top"])
            why[r_ or "FREE"] = why.get(r_ or "FREE", 0) + 1
        gaps.append(f"{it['light_id']} {it['chain_gap_before']} ({why})")
        if not win or "FREE" in why:
            gap_bad.append(f"{it['light_id']}: {why or 'no window'}")
    okp = [v for v in allsp if v <= 12.0 + 1e-3]
    check(f"H{n} rail lantern spacing ~10 along each rail (consecutive pairs 8..12; longer only across a stretch "
          "where every spot 8..12 out is blocked, re-tested)",
          bool(allsp) and all(v >= 8.0 - 1e-3 for v in allsp) and len(allsp) - len(okp) == len(gaps) and not gap_bad,
          f"left {sps['left']}; right {sps['right']}" + (f"; gaps: {'; '.join(gaps)}" if gaps else "") +
          (f"; NOT BLOCKED: {'; '.join(gap_bad)}" if gap_bad else ""))
lines.append(f"  rail lanterns checked: {n_rail}")

# 3. lights[] bookkeeping: every new lantern / glow light has exactly one entry, ids unique, local == world
ids = [q["id"] for q in LIGHTS]
inst_ids = {it["light_id"]: (n, it) for n in range(1, 10) for it in DH[f"H{n}"]["instances"] if it.get("light_id")}
bad = []
for q in LIGHTS:
    n = int(q["hole"][1:])
    if np.abs(DL.to_world(HM[n], q["pos"]) - np.array(q["world_pos"])).max() > 0.02:
        bad.append(f"{q['id']} local/world")
    if q["id"] not in inst_ids:
        bad.append(f"{q['id']} has no instance")
    if not all(k in q for k in ("color", "color3", "range", "brightness", "light")):
        bad.append(f"{q['id']} fields")
missing = [k for k in inst_ids if k not in LBY]
check("manifest.lights[]: one entry per pass-8 lantern / H8 glow prop (ids unique, local == world, all fields)",
      len(ids) == len(set(ids)) and not bad and not missing,
      "; ".join(bad[:4] + missing[:4]) if bad or missing else
      f"{len(LIGHTS)} lights: " + ", ".join(f"{k} {sum(1 for q in LIGHTS if q['kind'] == k)}"
                                           for k in sorted({q['kind'] for q in LIGHTS})))
dup = [it["light_id"] for n in range(1, 10) for it in DH[f"H{n}"]["instances"]
       if it.get("light_id") and it["role"] in ("rail", "hang") and
       any(np.linalg.norm(np.array(p) - np.array(LBY[it["light_id"]]["world_pos"])) < 0.05
           for p in DH[f"H{n}"].get("lights_world", []))]
check("pass-8 lantern glow cores are not repeated in the per-hole lights[] (no double PointLights)", not dup,
      ", ".join(dup[:4]))

# 4. H8 emissives: brighter Firefly / ShroomGlow, brighter firefly spots, a glow light on every H8 glow prop
fe, se = lglib.MATS["Firefly"][2], lglib.MATS["ShroomGlow"][2]
em = man.get("emissive", {}).get("materials", {})
tx_ok = all(os.path.exists(os.path.join(OUTD, v[k])) for v in em.values() for k in ("color_map", "emissive_mask"))
check("H8 emissives noticeably brighter: Firefly / ShroomGlow emission >= 2x pass 7 (4 / 3), manifest.emissive + "
      "textures present", fe >= 8.0 and se >= 6.0 and set(em) == {"Firefly", "ShroomGlow"} and tx_ok,
      f"Firefly {fe:g}, ShroomGlow {se:g}, textures {'ok' if tx_ok else 'MISSING'}")
ffs = [q for q in DH["H8"].get("spot_lights", []) if q.get("kind") == "firefly_glow"]
g8 = [it for it in DH["H8"]["instances"] if it["prop"] in ("firefly_cluster_low", "glow_shroom_patch",
                                                           "glow_root_arch", "glowing_mushrooms")]
check("H8 firefly_glow spots raised (Brightness >= 3, was 2) and every other H8 glow prop has a lights[] glow",
      ffs and all(q["brightness"] >= 3.0 for q in ffs) and all(it.get("light_id") in LBY for it in g8),
      f"{len(ffs)} swarm spots at {[q['brightness'] for q in ffs]}, {len(g8)} glow props lit")

# 5. negative tests
_h9 = HM[9]
_ok = hang[0]
_low = dict(_ok, world_pos=[_ok["world_pos"][0], _ok["world_pos"][1] - 3.0, _ok["world_pos"][2]])
_lane = [f for f in _h9["felt"] if f["id"] == "lane"][0]
_lw = DL.to_world(_h9, [_lane["center"][0], DL.felt_top(_lane) + 8.0, _lane["center"][2]])
_out = dict(_ok, world_pos=[float(v) for v in _lw])
check("negative test flagged: hanging lantern only 5 above the felt", hang_problem(_low) is not None,
      hang_problem(_low) or "")
check("negative test flagged: hanging lantern over the H9 lane (outside the corridor/green footprint)",
      hang_problem(_out) is not None, hang_problem(_out) or "")
_r = [it for it in DH["H8"]["instances"] if it["role"] == "rail"][0]
_w = [w for w in HM[8]["walls"] if w["id"] == _r["wall"]][0]
_wc = DL.to_world(HM[8], _w["center"])
_gc = glow_core(_r)
_shift = np.array([_wc[0] - _gc[0], 0, _wc[2] - _gc[2]])
_nrm = DL.yaw_mat(_w.get("yaw", 0) + HM[8]["world_yaw"]) @ np.array([1.0, 0, 0])
_shift = _nrm * float(_shift @ _nrm)                     # move the lantern straight onto the wall line
_clip = dict(_r, world_pos=(np.array(_r["world_pos"]) + _shift).tolist())
check("negative test flagged: rail lantern moved onto its rail (clip)", rail_problem(_clip) is not None,
      rail_problem(_clip) or "")
_r7 = [it for it in DH["H7"]["instances"] if it["role"] == "rail"][0]          # stake: no arm, moved 3 x inward
_w7 = [w for w in HM[7]["walls"] if w["id"] == _r7["wall"]][0]
_wc7 = DL.to_world(HM[7], _w7["center"])
_n7 = DL.yaw_mat(_w7.get("yaw", 0) + HM[7]["world_yaw"]) @ np.array([1.0, 0, 0])
_d7 = _n7 * float(np.array([_wc7[0] - _r7["world_pos"][0], 0, _wc7[2] - _r7["world_pos"][2]]) @ _n7)
_over = dict(_r7, world_pos=(np.array(_r7["world_pos"]) + _d7 * 3.0).tolist())
check("negative test flagged: rail lantern moved in over the felt", over_felt(placed_world(_over)[0]),
      rail_problem(_over) or "")
_rr = [it for it in DH["H8"]["instances"] if it["role"] == "rail"][1]
_free = rail_spot_blocked(8, _rr["prop"], _rr["world_pos"], _rr["world_yaw"], _rr["wall_top"])
check("negative test flagged: a gap window containing a free spot (an existing lantern's own spot re-tests as "
      "free, so a gap over it would fail)", _free is None, f"re-test -> {_free}")
_hid = dict(_rr, wall_top=_rr["wall_top"] + 3.0)
check("negative test flagged: rail lantern hidden below a rail 3 studs taller", rail_problem(_hid, 8) is not None,
      rail_problem(_hid, 8) or "")
_s = [8.0 <= v <= 12.0 for v in (15.0, 6.5)]
check("negative test flagged: rail lantern spacing 15 / 6.5 (outside 8..12)", not any(_s))
_nolight = dict(_r, light_id="H8_rail_missing")
_wrong = dict(LBY[_r["light_id"]], color3=[255, 255, 255], color="#FFFFFF")
LBY["_neg"] = _wrong
check("negative test flagged: rail lantern without a lights[] entry / with a white light",
      light_problem(_nolight, "rail_lantern", 8, 12) is not None and
      light_problem(dict(_r, light_id="_neg"), "rail_lantern", 8, 12) is not None)
del LBY["_neg"]
