# Pass 6 (holes.json v2) fit checks. exec()'d by fitcheck.py inside its namespace (uses build, check, lines, np,
# DL, WF, HM/HW (world-placed holes), man, DH, KO, OCC, fbx_tris, to_world_tris, rail_dist).
# All gameplay numbers are read from ../holes.json (via HM), never copied.
lines.append("")
lines.append("# pass 6: holes.json v2 (flags, new props, changed moving parts, H9 lantern bar -> pendulum)")
MP = {p["name"]: p for p in man["props"]}
import props_pass6 as P6
_TRI = {}


def prop_tris(name):
    """Prop triangles in its own Roblox frame (x, y up, z), rebuilt from the generator."""
    if name not in _TRI:
        for o in [o for o in bpy.data.objects if o.name == name or o.name.startswith(name + "__") or
                  o.name.startswith(name + ".")]:
            bpy.data.objects.remove(o, do_unlink=True)          # earlier builds would get .001 names
        objs = build(name)
        T, mats = [], []
        for o in objs:
            me = o.data
            me.calc_loop_triangles()
            mw = np.array(o.matrix_world)
            V = np.array([v.co[:] for v in me.vertices], float) @ mw[:3, :3].T + mw[:3, 3]
            idx = np.array([t.vertices[:] for t in me.loop_triangles], int)
            if len(idx):
                T.append(V[idx])
                mats += [lglib.mat_of(o.name)] * len(idx)
        for o in objs:
            bpy.data.objects.remove(o, do_unlink=True)
        T = np.concatenate(T)
        _TRI[name] = (np.stack([T[..., 0], T[..., 2], -T[..., 1]], -1), np.array(mats))
    return _TRI[name]


def placed_local(name, pl):
    """Triangles of a placed prop in its hole's local frame."""
    T, mats = prop_tris(name)
    s_ = pl.get("scale", 1.0)
    S = np.array([s_] * 3 if np.isscalar(s_) else s_, float)
    return (T * S) @ DL.yaw_mat(pl.get("yaw", 0)).T + np.asarray(pl["pos"], float), mats


def heroes_of(n, skip=(), moving=True):
    out = []
    for p in man["props"]:
        if p.get("group") == "dressing" or p["name"] in ("hollow_tree",) + tuple(skip) or \
                (moving is False and p.get("kind") == "moving"):
            continue
        for pl in p.get("placements", []):
            if pl["hole"] == f"H{n}":
                out.append((p["name"], pl))
    return out


def seg_tri_hits(T, a, b):
    """Möller-Trumbore: which triangles the segment a->b crosses."""
    if len(T) == 0:
        return np.zeros(0, bool)
    d = b - a
    e1, e2 = T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]
    p_ = np.cross(d, e2)
    det = (e1 * p_).sum(1)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1), 0)
    tv = a - T[:, 0]
    u = (tv * p_).sum(1) * inv
    q = np.cross(tv, e1)
    v = (d * q).sum(axis=1) * inv
    t = (e2 * q).sum(1) * inv
    return ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t >= 0) & (t <= 1)


def felt_plane_y(h, x, z):
    """Exact felt surface height at hole-local (x, z) over the highest piece containing it (None if no felt)."""
    best = None
    for f in h["felt"]:
        c = f["center"]
        yaw = math.radians(f.get("yaw", 0))
        dx, dz = x - c[0], z - c[2]
        lx, lz = dx * math.cos(yaw) - dz * math.sin(yaw), dx * math.sin(yaw) + dz * math.cos(yaw)
        if abs(lx) > f["size"][0] / 2 + 1e-6 or abs(lz) > f["size"][1] / 2 + 1e-6:
            continue
        sl = f.get("slope") or {}
        y = c[1]
        if sl.get("rise"):
            u = lx / f["size"][0] if sl.get("axis") == "x" else lz / f["size"][1]
            y += sl["rise"] * u
        best = y if best is None else max(best, y)
    return best


# ---------------------------------------------------------------------------- 1. moving parts == holes.json v2
gone = [n for n in ("h9_lantern_bar", "h9_lantern_post_static") if n in MP or
        os.path.exists(os.path.join(OUTD, "fbx", f"{n}.fbx"))]
check("removed: h9_lantern_bar + h9_lantern_post_static (no manifest entry, no FBX)", not gone, ", ".join(gone))
lantern_lights = [q["id"] for q in DH.get("H9", {}).get("spot_lights", []) if "lantern_bar" in q["id"]]
check("removed: no light tied to the H9 lantern bar (spot_lights)", not lantern_lights, ", ".join(lantern_lights))
for n in range(1, 10):
    for mp in HM[n]["moving_parts"]:
        p = [q for q in man["props"] if (q.get("motion") or {}).get("holes_json_id") == mp["id"] and
             q["motion"].get("hole") == f"H{n}"]
        bad = []
        if len(p) != 1:
            bad.append(f"{len(p)} props")
        else:
            mo = p[0]["motion"]
            if mo["type"] != mp["type"]:
                bad.append(f"type {mo['type']}")
            if np.abs(np.array(mo["course_local_pivot"], float) - mp["pivot"]).max() > 1e-6:
                bad.append(f"pivot {mo['course_local_pivot']}")
            if np.abs(np.array(mo["axis_roblox"], float) - mp["axis"]).max() > 1e-6:
                bad.append("axis")
            if p[0]["placements"][0]["pos"] != list(mp["pivot"]):
                bad.append("placement != pivot")
            if mp["type"] == "swing":
                for k in ("amplitude_deg", "period_s", "phase"):
                    if abs(mo[k] - mp[k]) > 1e-6:
                        bad.append(k)
                if list(mo["range"]) != list(mp["range"]) or abs(mo["speed"] - mp["speed"]) > 1e-3:
                    bad.append("range/speed")
            else:
                if abs(mo["speed"] - mp["speed"]) > 1e-6:
                    bad.append(f"speed {mo['speed']} vs {mp['speed']}")
                if (mo["range"] or None) != (mp["range"] or None):
                    bad.append(f"range {mo['range']} vs {mp['range']}")
        desc = (f"swing +-{mp['amplitude_deg']} deg, {mp['period_s']} s" if mp["type"] == "swing" else
                f"{mp['type']} {mp['speed']} range {mp['range']}")
        check(f"H{n} {mp['id']}: manifest motion == holes.json v2 ({desc}, pivot {mp['pivot']})", not bad, "; ".join(bad))
# ranges that matter to the visuals
_h7 = HM[7]
_log = [m for m in _h7["moving_parts"] if m["id"] == "log"][0]
_half = MP["h7_floating_log"]["bbox_size_studs"][0] / 2
_end = max(abs(r) for r in _log["range"]) + _half
_clr = _log.get("end_clearance", 0.5)
check(f"H7 log: at full travel (+-{max(abs(r) for r in _log['range']):g}) the mesh tip stays {_clr:g} short of the "
      "rail line x = +-10", _end <= 10.0 - _clr + 0.05, f"mesh tip |x| {_end:.3f}")

# ---------------------------------------------------------------------------- 2. pendulum rest + swing envelope
h9 = HM[9]
pend = [m for m in h9["moving_parts"] if m["type"] == "swing"][0]
piv = np.array(pend["pivot"], float)
Tp, mp_ = prop_tris("h9_lantern_pendulum")
bob_bot = piv[1] + Tp[..., 1].min()
fy = felt_plane_y(h9, piv[0], piv[2])
_pb = pend["blockers"][0]
_want = piv[1] + min(b_["center"][1] - b_["size"][1] / 2 for b_ in pend["blockers"])   # Round 9: foot 8.996-7.962
check(f"H9 pendulum bob bottom = the lowest holes.json blocker bottom ({_want - fy if fy is not None else 0:.3f} above the "
      "chamber felt at rest) and above the felt", fy is not None and abs(bob_bot - _want) <= 0.01 and bob_bot > fy,
      f"gap {bob_bot - fy:.3f}")
Rw9, _ = DL.hole_xf(h9)
G = 0.25
env = []                  # OBBs (world) of bob + chain over the swing, grown by G
env_local = []
_Yb = DL.yaw_mat(_pb.get("yaw", 0.0))                          # Round 7: square bob turned 30 deg
for ang in np.arange(-pend["amplitude_deg"], pend["amplitude_deg"] + 1e-6, 1.0):
    Rr = DL.axis_angle(pend["axis"], ang)
    for (c, hf, Ry) in [(b_["center"], np.array(b_["size"], float) / 2, DL.yaw_mat(b_.get("yaw", 0.0)))
                        for b_ in pend["blockers"]] + [((0, -3.2, 0), (0.2, 2.9, 0.2), np.eye(3))]:   # pass 9: + foot
        cl = piv + Rr @ np.array(c, float)
        env_local.append(WF.OBB("pendulum", cl, Rr @ Ry, np.array(hf) + G))
        env.append(WF.OBB("pendulum", DL.to_world(h9, cl), Rw9 @ Rr @ Ry, np.array(hf) + G))
# a) dressing of every hole near the pendulum (re-imported FBX groups, world space)
dhit = {}
pw = DL.to_world(h9, piv)
for n in range(1, 10):
    hh = HM[n]
    if np.linalg.norm(np.array(hh["world_offset"], float)[[0, 2]] - pw[[0, 2]]) > 160:
        continue
    for f in DH.get(f"H{n}", {}).get("fbx", []):
        T = to_world_tris(hh, fbx_tris(os.path.join(OUTD, f["fbx"])))
        k = WF.check_tris(T, env)
        if k:
            dhit[f["fbx"]] = sum(k.values())
check(f"H9 pendulum swing envelope (bob + plinth/foot + chain, +-{pend['amplitude_deg']:g} deg, grown 0.25) clear of ALL dressing (exact, re-imported FBX)",
      not dhit, str(dhit) if dhit else f"{len(env)} swept boxes")
# b) static hero props of H9 (except the hinge bracket of the beam, within 0.75 of the hinge)
hh_hits = {}
for name, pl in heroes_of(9, skip=("h9_lantern_pendulum",)):
    T, _m = placed_local(name, pl)
    if name == "h9_pendulum_root_beam":
        T = T[np.linalg.norm(T.mean(1) - piv, axis=1) > 0.75]
    # geometry that stays under the playing surface (e.g. the well rim, top 0.02 below the felt) cannot meet the bob
    cen = T.mean(1)
    fyc = np.array([felt_plane_y(h9, x, z) if felt_plane_y(h9, x, z) is not None else -1e9 for x, z in cen[:, [0, 2]]])
    T = T[T[..., 1].max(1) > fyc + 0.01]
    k = WF.check_tris(T, env_local)
    if k:
        hh_hits[name] = sum(k.values())
check("H9 pendulum swing envelope clear of every H9 hero prop (beam/legs, heart lanterns, well rim, arch, knots)",
      not hh_hits, str(hh_hits))
# c) the spot light over the pendulum is outside the envelope
sp = [q for q in DH["H9"].get("spot_lights", []) if q["over"] == pend["id"]]
check("H9 pendulum spot light present and outside the swing envelope",
      len(sp) == 1 and WF.points_clear(np.array([sp[0]["world_pos"]]), env)[0],
      f"{sp[0]['pos'] if sp else None}")

# ---------------------------------------------------------------------------- 3. H8 door + pockets, rings
h8 = HM[8]
door = [m for m in h8["moving_parts"] if m["id"] == "root_door"][0]
dc = np.array(MP["h8_root_door"]["bbox_center_from_origin"], float)
dh = np.array(MP["h8_root_door"]["bbox_size_studs"], float) / 2
pockets = [(pl, placed_local("h8_door_pocket", pl)[0]) for pl in MP["h8_door_pocket"]["placements"]]
clash, hidden = 0, []
for off in np.arange(door["range"][0], door["range"][1] + 1e-6, 0.25):
    box = WF.OBB("door", np.array(door["pivot"], float) + dc + np.array(door["axis"], float) * off, np.eye(3), dh)
    for pl, T in pockets:
        clash += int(WF.tris_hit_obb(T, box).sum())
for pl, T in pockets:
    zr = pl["pos"][2]
    sgn = 1 if zr > door["pivot"][2] else -1
    end = door["pivot"][2] + dc[2] + sgn * (dh[2] + (door["range"][1] if sgn > 0 else -door["range"][0]))
    zz = T[..., 2]
    back = zz.max() if sgn > 0 else zz.min()
    past = (end - (zr + sgn * 0.25)) * sgn
    hidden.append(past > 0 and (back - end) * sgn >= 0.1)
# Round 7: a pocket only where the door's travel crosses a junction rail line (inner face)
_need = 0
for _rid in ("rail16", "rail14"):
    _w = [w for w in h8["walls"] if w["id"] == _rid][0]
    _sg = 1 if _w["center"][2] > door["pivot"][2] else -1
    _end = door["pivot"][2] + dc[2] + _sg * (dh[2] + (door["range"][1] if _sg > 0 else -door["range"][0]))
    _need += (_end - (_w["center"][2] - _sg * _w["size"][0] / 2)) * _sg > 0
check(f"H8 root door ({door['range'][0]:g}..{door['range'][1]:g}) never touches its pockets; every end that crosses a "
      "junction rail line slides INTO a pocket", clash == 0 and len(pockets) == _need and all(hidden),
      f"{clash} clashing tris, {len(pockets)} pockets for {_need} crossing ends, ends hidden {hidden}")
tp = h8["teleports"][0]
Te, me_ = placed_local("firefly_ring_entry", MP["firefly_ring_entry"]["placements"][0])
V = Te[me_ == "Firefly"].reshape(-1, 3)
ec = np.array(tp["entry"]["center"], float)
pad = V[V[:, 1] < ec[1] + 0.03]
r_pad = float(np.hypot(pad[:, 0] - ec[0], pad[:, 2] - ec[2]).max())
low = V[(V[:, 1] >= ec[1] + 0.03) & (V[:, 1] < ec[1] + 0.5)]
in_gap = low[np.abs(low[:, 2] - ec[2]) < tp["entry"]["radius"] + 0.08] if len(low) else low
check(f"H8 entry ring: glow disc radius == trigger radius {tp['entry']['radius']} and the ring's bottom gap clears the "
      "whole trigger width (+ ball)", abs(r_pad - tp["entry"]["radius"]) <= 0.03 and len(in_gap) == 0,
      f"disc r {r_pad:.3f}, ring verts in the gap {len(in_gap)}")
px = MP["firefly_ring_exit"]["placements"][0]
yw = math.radians(px["yaw"])
dirv = np.array(tp["exit"]["dir"], float) / np.linalg.norm(tp["exit"]["dir"])
check("H8 exit ring at the v2 teleport exit (9, 1.5, -47), local +Z along the exit dir",
      np.abs(np.array(px["pos"]) - tp["exit"]["center"]).max() < 1e-6 and
      abs(math.sin(yw) - dirv[0]) < 0.002 and abs(math.cos(yw) - dirv[1]) < 0.002, f"pos {px['pos']} yaw {px['yaw']}")
ab = [f for f in h8["felt"] if f["id"] == "alcove_bank"][0]
Tc, _m = placed_local("h8_alcove_bank_cladding", MP["h8_alcove_bank_cladding"]["placements"][0])
Vc = Tc.reshape(-1, 3)
x0, x1 = ab["center"][0] - ab["size"][0] / 2, ab["center"][0] + ab["size"][0] / 2
z0, z1 = ab["center"][2] - ab["size"][1] / 2, ab["center"][2] + ab["size"][1] / 2
plane = np.array([felt_plane_y(h8, min(max(x, x0), x1), min(max(z, z0), z1)) for x, z in Vc[:, [0, 2]]])
over = float((Vc[:, 1] - plane).max())
inside = bool(((Vc[:, 0] >= x0 - 0.01) & (Vc[:, 0] <= x1 + 0.01) & (Vc[:, 2] >= z0 - 0.01) & (Vc[:, 2] <= z1 + 0.01)).all())
check("H8 alcove bank cladding lies ON the banked plane (<= 0.03 above it) and inside its footprint x 7.7..9, z -15..-8",
      over <= 0.031 and inside, f"max above plane {over:.3f}, inside {inside}")

# ---------------------------------------------------------------------------- 4. flags (no collision, top, facing)
fl_bad = []
BAN_C = {}
for n in range(1, 10):
    h = HM[n]
    fl = h["cup"]["flag"]
    p = MP.get(f"cup_flag_h{n:02d}")
    if not p:
        fl_bad.append(f"H{n} missing")
        continue
    pl = p["placements"][0]
    T, mats = placed_local(p["name"], pl)
    knob = T[mats == "CapGold"]
    # the knob is the sphere at the pole top; the pennant tie rings are CapGold too -> take the highest cluster
    kv = knob.reshape(-1, 3)
    kv = kv[kv[:, 1] > kv[:, 1].max() - 0.45]
    top = kv.mean(0)
    # pass 7: enlarged flag (props_pass6.FLAG_POLE_D / FLAG_BANNER), pole top still == holes.json cup.flag.top
    pole = T[mats == "Cream"].reshape(-1, 3)
    prad = np.hypot(pole[:, 0] - pl["pos"][0], pole[:, 2] - pl["pos"][2])
    pole = pole[(prad < P6.FLAG_POLE_D / 2 + 0.05) & (pole[:, 1] < fl["top"][1] - P6.FLAG_BANNER[1] - 0.5)]
    rpole = float(np.hypot(pole[:, 0] - pl["pos"][0], pole[:, 2] - pl["pos"][2]).max())
    ban = T[mats == "FlagRed"].reshape(-1, 3)
    ban = ban[ban[:, 1] > fl["top"][1] - P6.FLAG_TOP_GAP - P6.FLAG_BANNER[1] - 0.2]     # pennant, not the pole bands
    bw = float(np.hypot(ban[:, 0] - pl["pos"][0], ban[:, 2] - pl["pos"][2]).max())
    bh = float(ban[:, 1].max() - ban[:, 1].min())
    btop = float(ban[:, 1].max())
    BAN_C[n] = ban.mean(0)
    want_yaw = math.degrees(math.atan2(h["tee"]["position"][0] - pl["pos"][0], h["tee"]["position"][2] - pl["pos"][2]))
    probs = []
    if np.abs(np.array(pl["pos"]) - h["cup"]["position"]).max() > 1e-6:
        probs.append("not at the cup")
    if np.abs(top - np.array(fl["top"])).max() > 0.06:
        probs.append(f"top {np.round(top, 2).tolist()} vs {fl['top']}")
    if abs(rpole - P6.FLAG_POLE_D / 2) > 0.02 or P6.FLAG_POLE_D < fl["pole_diameter"]:
        probs.append(f"pole r {rpole:.3f}")
    if abs(bw - P6.FLAG_BANNER[0]) > 0.2 or abs(bh - P6.FLAG_BANNER[1]) > 0.05 or \
            bw < fl["banner_size"][0] or bh < fl["banner_size"][1]:
        probs.append(f"banner {bw:.2f}x{bh:.2f}")
    if btop > fl["top"][1] - 0.05:
        probs.append(f"banner above the pole top ({btop:.2f})")
    if abs((pl["yaw"] - want_yaw + 180) % 360 - 180) > 0.5:
        probs.append("not facing the tee")
    if pl.get("collision") is not False or fl.get("collision") is not False or "NO COLLISION" not in p["notes"]:
        probs.append("collision flag")
    if not any(b.label == f"H{n}:hero:{p['name']}" for b in KO):
        probs.append("no dressing keep-out")
    if probs:
        fl_bad.append(f"H{n}: " + ", ".join(probs))
check("9 cup flags (pass 7 sizes: pole %.2f dia, pennant %.1f x %.1f, both >= holes.json): at the cup, pole top == "
      "holes.json cup.flag.top, banner under the top, banner faces the tee, " % (P6.FLAG_POLE_D, *P6.FLAG_BANNER[:2]) +
      "collision false (placement + holes.json + notes), dressing keep-out", not fl_bad, "; ".join(fl_bad))
check("manifest decoration rule covers the flags (CanCollide=false on every MeshPart)",
      "CanCollide=false" in man.get("collision", ""))
# tee -> flag sightline vs every hero prop of the hole (holes.json: visible on all holes but H3, by design)
los_bad, los_info = [], []
for n in range(1, 10):
    h = HM[n]
    a = np.array(h["tee"]["position"], float) + [0, 5.5, 0]
    b = np.array(h["cup"]["flag"]["top"], float)
    blk = []
    for name, pl in heroes_of(n, skip=(f"cup_flag_h{n:02d}",), moving=False):   # moving parts: sim reports % of cycle
        T, _m = placed_local(name, pl)
        if seg_tri_hits(T, a, b - (b - a) / np.linalg.norm(b - a) * 0.3).any():
            blk.append(name)
    if n == 3:
        los_info.append(f"H3 blocked by design ({', '.join(blk) or 'none'})")
    elif blk:
        los_bad.append(f"H{n}: {', '.join(blk)}")
check("tee eye (+5.5) -> flag top not blocked by any hero prop (incl. all pass-6 props) on H1-H2, H4-H9",
      not los_bad, "; ".join(los_bad) if los_bad else "; ".join(los_info))
# pass 7: the pennant itself (its centre) is seen from the tee eye on the same holes (not just the knob)
ban_bad, ban_info = [], []
for n in range(1, 10):
    if n not in BAN_C:
        continue
    h = HM[n]
    a = np.array(h["tee"]["position"], float) + [0, 5.5, 0]
    b = BAN_C[n]
    blk = [name for name, pl in heroes_of(n, skip=(f"cup_flag_h{n:02d}",), moving=False)
           if seg_tri_hits(placed_local(name, pl)[0], a, b - (b - a) / np.linalg.norm(b - a) * 0.3).any()]
    if n == 3:
        ban_info.append(f"H3 blocked by design ({', '.join(blk) or 'none'})")
    elif blk:
        ban_bad.append(f"H{n}: {', '.join(blk)}")
check("pass 7: tee eye (+5.5) -> pennant centre not blocked by any hero prop on H1-H2, H4-H9",
      not ban_bad, "; ".join(ban_bad) if ban_bad else "; ".join(ban_info))
Ta, _m = placed_local("trunk_tunnel_arch", MP["trunk_tunnel_arch"]["placements"][0])
check("H9 trunk tunnel arch top <= y 6 (holes.json LOS note: keep the buttress top <= 6)",
      Ta[..., 1].max() <= 6.0, f"top y {Ta[..., 1].max():.3f}")

# ---------------------------------------------------------------------------- 5. flush / on-rail / beside-rail props
h2, h4, h5 = HM[2], HM[4], HM[5]
probs = []
for pl in MP["h2_chute_arrow_decal"]["placements"]:
    T, _m = placed_local("h2_chute_arrow_decal", pl)
    V = T.reshape(-1, 3)
    fy_ = np.array([felt_plane_y(h2, x, z) if felt_plane_y(h2, x, z) is not None else np.nan for x, z in V[:, [0, 2]]])
    if np.isnan(fy_).any() or (V[:, 1] - fy_).max() > 0.0105 or (V[:, 1] - fy_).min() < -1e-4:
        probs.append(f"decal {pl['pos']}")
T, _m = placed_local("h5_respawn_stone", MP["h5_respawn_stone"]["placements"][0])
V = T.reshape(-1, 3)
fy_ = np.array([felt_plane_y(h5, x, z) for x, z in V[:, [0, 2]]], dtype=float)
if np.isnan(fy_).any() or (V[:, 1] - fy_).max() > 0.0205:
    probs.append("respawn stone")
rs = [z_ for z_ in h5["hazards"] if z_.get("reset") == "respawn"][0]["respawn"]
if MP["h5_respawn_stone"]["placements"][0]["pos"] != list(rs):
    probs.append("respawn stone not at hazards.respawn")
check("flush props: H2 felt arrow decals <= 0.01 and the H5 respawn stone <= 0.02 above the felt, fully on felt, "
      "stone at holes.json respawn", not probs, "; ".join(probs))
probs = []
for pl in MP["h4_side_gap_post"]["placements"]:
    w = [w_ for w_ in h4["walls"] if w_.get("kind") is None and
         DL.rect_dist(np.array([pl["pos"][0]]), np.array([pl["pos"][2]]),
                      (w_["center"][0], w_["center"][2], w_["size"][0] / 2, w_["size"][2] / 2, w_.get("yaw", 0), 0))[0] < 1e-6]
    if not w or abs(pl["pos"][1] - (w[0]["center"][1] + w[0]["size"][1] / 2)) > 1e-6:
        probs.append(f"post {pl['pos']} not on a rail top")
check("H4 side-gap lantern posts stand on the plaza rail tops (x = +-7.25, z -17)", not probs, "; ".join(probs))
probs = []
for side in ("left", "right"):
    p = MP[f"h2_chute_sign_{side}"]
    T, _m = placed_local(p["name"], p["placements"][0])
    V = T.reshape(-1, 3)
    d = DL.felt_distance(h2, V[:, 0], V[:, 2])
    rails2 = [w_ for w_ in h2["walls"]]
    rd = np.min([DL.rect_dist(V[:, 0], V[:, 2], (w_["center"][0], w_["center"][2], w_["size"][0] / 2, w_["size"][2] / 2,
                                                  w_.get("yaw", 0), 0)) for w_ in rails2], axis=0)
    if d.min() < 0.5 or rd.min() < 0.1:
        probs.append(f"{side}: felt {d.min():.2f}, rail {rd.min():.2f}")
check("H2 chute signs: whole sign >= 0.5 from the felt and >= 0.1 outside every wall", not probs, "; ".join(probs))
T, _m = placed_local("h9_tunnel_dip_trim", MP["h9_tunnel_dip_trim"]["placements"][0])
V = T.reshape(-1, 3)
rw = [w_ for w_ in h9["walls"] if w_["id"] in ("rail4", "rail8")]
rd = np.min([DL.rect_dist(V[:, 0], V[:, 2], (w_["center"][0], w_["center"][2], w_["size"][0] / 2 + 0.02,
                                              w_["size"][2] / 2, w_.get("yaw", 0), 0)) for w_ in rw], axis=0)
fd = DL.felt_distance(h9, V[:, 0], V[:, 2])
check("H9 tunnel dip trim: every vertex on the tunnel rails' footprint (never over the felt)",
      rd.max() <= 1e-6 and fd.min() >= -1e-6, f"max off-rail {rd.max():.3f}")
Tb, _m = placed_local("h9_pendulum_root_beam", MP["h9_pendulum_root_beam"]["placements"][0])
V = Tb.reshape(-1, 3)
lowv = V[V[:, 1] < 4.0]
fd = DL.felt_distance(h9, lowv[:, 0], lowv[:, 2])
r9 = np.min([DL.rect_dist(lowv[:, 0], lowv[:, 2], (w_["center"][0], w_["center"][2], w_["size"][0] / 2,
                                                   w_["size"][2] / 2, w_.get("yaw", 0), 0)) for w_ in h9["walls"]], axis=0)
check("H9 pendulum root beam: legs (geometry below y 4) stay off the felt (>= 0.3) and outside every rail (>= 0.1)",
      fd.min() >= 0.3 and r9.min() >= 0.1, f"min felt {fd.min():.2f}, min rail {r9.min():.2f}")
sl = [a_ for a_ in HM[7]["decoration_anchors"] if a_["name"] == "step_lanterns"][0]["occluders"]
px7 = sorted(pl["pos"][0] for pl in MP["lantern_post"]["placements"] if pl["hole"] == "H7")
check("H7 gap lantern posts at the v2 gap rail ends (x 3.75 / 6.75, holes.json step_lanterns)",
      px7 == sorted(o["center"][0] for o in sl), str(px7))

# ---------------------------------------------------------------------------- 6. H7 dressing
st7 = DH["H7"]["stats"]
p6 = st7.get("pass6_vs_pass5", {})
check("H7 dressing richer than pass 5 (13 3D props) and still within the near-field budget",
      st7["final_3d"] > (p6.get("pass5_3d") or 13) and st7["near_field_tris_after"] <= NEAR_BUDGET,
      f"3D {p6.get('pass5_3d')} -> {st7['final_3d']}, near-field {st7['near_field_tris_after']}")
