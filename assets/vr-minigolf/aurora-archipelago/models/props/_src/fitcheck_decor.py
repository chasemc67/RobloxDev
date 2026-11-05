# Pass 2e decoration fit check, exec()'d at the end of fitcheck.py (shares its namespace: check, flag, LINES, REPORT, samples,
# tris_of, in_boxes, box_dist, yaw_inv, GAPS, D, np, bpy, os, math, json).
# Blockout decoration meshes (world positions, Roblox studs) from the latest blockout (AA_BLOCKOUT, default ../../out_p2e/models/blockout):
#   felt_banks.fbx      FeltBank (#3EA886 x 0.78) visual 0.3-stud bank along exposed felt edges, CanCollide false
#   course_apron_0N.fbx SnowCourse surround draped 0.05 over the terrain Snow/Salt, 5-7 studs outside each felt+rail footprint
# Tested per hole in the hole-local frame against holes.json. Felt heights: holes.json felt y is the collider top; the blockout felt slab
# is 0.28 thick above it (visual felt top = y + 0.28, slope included).
#  banks  B1 no point inside any felt rectangle (shrunk 0.01): stays outside the playable felt
#         B2 no point above the visual felt top of the felt it borders (highest felt within 1.3 studs, slope-aware at its nearest point;
#            lower tiers next to a drop don't count - those banks sit on the upper ground, outside the lower felt rectangle by B1)
#         B3 points inside a rail/wall footprint stay inside that wall box's height range (hidden "under rails"); the rest are outside rails
#         B4 cups: horizontal distance to every cup >= radius + 0.5;  tee lanes: no point inside the felt that holds the tee, every point
#            within r 2.5 of the tee lies outside felt and below the felt top
#         B5 movers: no point inside any holes.json blocker's swept volume (rotate/swing: full circle of the blocker corners about the
#            pivot axis, +0.05; slide: blocker boxes over the whole range, +0.05)
#         B6 gap volumes (H3/H17, the fitcheck GAPS boxes also cover the rim ground): only below the felt plane or within 1.3 studs of a crossing felt
#  apron  A1 inside a felt rectangle only below the visual felt top - 0.1 (hidden in the slab); outside felt it lies on the terrain
#            (build_stats_p2e.json: every vertex = terrain Snow/Salt raycast hit + 0.05, triangle centroids 0.05 +- 0.025 over the terrain)
#         A2 band: every point within 8.5 studs (7 + 1 lattice cell + tolerance) of its hole's felt+rail footprint
#         A3 cups/tee/movers as B4/B5; gap volumes: none
#  files  manifest decoration/can_collide false, one material per mesh, every mesh/FBX < 20,000 tris
BLK = os.environ.get("AA_BLOCKOUT", os.path.join(os.path.dirname(OUT), "out_p2e", "models", "blockout"))
_man_b = json.load(open(os.path.join(BLK, "manifest.json")))
DECOR = [f for f in _man_b["files"] if f.get("decoration")]
REPORT["decoration"] = {"blockout": os.path.abspath(BLK), "pass": _man_b.get("pass"), "files": {}, "holes": {}}
LINES.append(f"INFO  pass 2e decoration (blockout {os.path.abspath(BLK)}, manifest pass {_man_b.get('pass')}): " + ", ".join(f["file"] for f in DECOR))
check("pass 2e decoration files present: felt_banks.fbx + course_apron_00..02.fbx",
      {f["file"] for f in DECOR} == {"felt_banks.fbx", "course_apron_00.fbx", "course_apron_01.fbx", "course_apron_02.fbx"}, str([f["file"] for f in DECOR]))


def _import(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    return [o for o in bpy.data.objects if o not in before and o.type == "MESH"]


PTS = {"bank": [], "apron": []}
for f in DECOR:
    obs = _import(os.path.join(BLK, f["file"]))
    tri = {}
    for o in obs:
        o.data.calc_loop_triangles()
        tri[o.name] = len(o.data.loop_triangles)
    one = all(len(o.material_slots) == 1 for o in obs)
    kind = "bank" if f["file"] == "felt_banks.fbx" else "apron"
    check(f"decoration {f['file']}: CanCollide false + decoration in manifest, one material per mesh, every mesh/FBX < 20,000 tris "
          f"({sum(tri.values())} tris, {len(obs)} mesh)",
          f.get("can_collide") is False and one and max(tri.values()) < 20000 and sum(tri.values()) < 20000 and sum(tri.values()) == f["total_tris"])
    P = samples([t for o in obs for t in tris_of([o], o.matrix_world)], 0.1 if kind == "bank" else 0.5)      # Blender world -> Roblox world
    V = np.concatenate([np.array([tuple(o.matrix_world @ v.co) for v in o.data.vertices]) for o in obs])
    PTS[kind].append(np.concatenate([P, np.stack([V[:, 0], V[:, 2], -V[:, 1]], 1)]))
    REPORT["decoration"]["files"][f["file"]] = dict(tris=sum(tri.values()), meshes=len(obs), material=f["materials"], points_tested=len(P) + len(V))
    for o in obs:
        me = o.data
        bpy.data.objects.remove(o)
        bpy.data.meshes.remove(me)
PTS = {k: np.concatenate(v) for k, v in PTS.items()}


def _local(n, P):
    h = D.H[n]
    o = h["world_offset"]
    a = math.radians(-h["world_yaw"])
    dx, dz = P[:, 0] - o[0], P[:, 2] - o[2]
    return np.stack([dx * math.cos(a) + dz * math.sin(a), P[:, 1] - o[1], -dx * math.sin(a) + dz * math.cos(a)], 1)


def _felt_raw(n):
    return [f for f in D.H[n]["felt"]]


def _foot_dist(n, Q):
    d = np.full(len(Q), 1e9)
    for f in D.H[n]["felt"]:
        d = np.minimum(d, box_dist(Q, dict(center=f["center"], size=[f["size"][0], 0, f["size"][1]], yaw=f.get("yaw", 0.0))))
    for w in D.H[n]["walls"]:
        if "center" in w and "size" in w:
            d = np.minimum(d, box_dist(Q, w))
    return d


def _inside_felt(n, Q, shrink=0.0):
    m = np.zeros(len(Q), bool)
    for f in _felt_raw(n):
        lx, lz = yaw_inv(Q[:, 0], Q[:, 2], f["center"], f.get("yaw", 0.0))
        m |= (np.abs(lx) < f["size"][0] / 2 - shrink) & (np.abs(lz) < f["size"][1] / 2 - shrink)
    return m


def _visual_top_nearest(n, Q):
    """visual felt top (y + 0.28, slope) of the nearest felt rectangle, evaluated at the nearest point of it; and the distance"""
    bd = np.full(len(Q), 1e9)
    by = np.zeros(len(Q))
    for f in _felt_raw(n):
        c, s, yaw = f["center"], f["size"], f.get("yaw", 0.0)
        lx, lz = yaw_inv(Q[:, 0], Q[:, 2], c, yaw)
        cx, cz = np.clip(lx, -s[0] / 2, s[0] / 2), np.clip(lz, -s[1] / 2, s[1] / 2)
        d = np.hypot(lx - cx, lz - cz)
        y = np.full(len(Q), c[1] + 0.28)
        sl = f.get("slope")
        if sl:
            y = y + ((cx / s[0]) if sl["axis"] == "x" else (cz / s[1])) * sl["rise"]
        upd = d < bd - 1e-9
        bd = np.where(upd, d, bd)
        by = np.where(upd, y, by)
    return by, bd


def _max_top_within(n, Q, r=2.6):
    """highest visual felt top among the felt rectangles within r studs (2.6 >= a bank's reach: rail 1.2 + 0.62, x sqrt2 at corner
    extensions) - the felt a bank lines; lower tiers next to a drop don't count"""
    best = np.full(len(Q), -1e9)
    for f in _felt_raw(n):
        c, s, yaw = f["center"], f["size"], f.get("yaw", 0.0)
        lx, lz = yaw_inv(Q[:, 0], Q[:, 2], c, yaw)
        cx, cz = np.clip(lx, -s[0] / 2, s[0] / 2), np.clip(lz, -s[1] / 2, s[1] / 2)
        y = np.full(len(Q), c[1] + 0.28)
        sl = f.get("slope")
        if sl:
            y = y + ((cx / s[0]) if sl["axis"] == "x" else (cz / s[1])) * sl["rise"]
        best = np.where((np.hypot(lx - cx, lz - cz) <= r) & (y > best), y, best)
    return np.where(best < -1e8, _visual_top_nearest(n, Q)[0], best)


def _top_inside(n, Q):
    """highest visual felt top over each point (nan outside felt)"""
    best = np.full(len(Q), np.nan)
    for f in _felt_raw(n):
        c, s, yaw = f["center"], f["size"], f.get("yaw", 0.0)
        lx, lz = yaw_inv(Q[:, 0], Q[:, 2], c, yaw)
        m = (np.abs(lx) <= s[0] / 2) & (np.abs(lz) <= s[1] / 2)
        y = np.full(len(Q), c[1] + 0.28)
        sl = f.get("slope")
        if sl:
            y = y + ((lx / s[0]) if sl["axis"] == "x" else (lz / s[1])) * sl["rise"]
        best = np.where(m & (np.isnan(best) | (y > best)), y, best)
    return best


def _swept(n, Q, pad=0.05):
    bad = np.zeros(len(Q), bool)
    for m in D.H[n]["moving_parts"]:
        piv = np.array(m["pivot"], float)
        bl = m.get("blockers", [])
        if not bl:
            continue
        if m["type"] in ("rotate", "swing"):
            ax = np.array(m["axis"], float)
            ax /= np.linalg.norm(ax)
            corners = []
            for b in bl:
                c, s, yaw = np.array(b["center"], float), b["size"], math.radians(b.get("yaw", 0.0))
                for sx in (-.5, .5):
                    for sy in (-.5, .5):
                        for sz in (-.5, .5):
                            x, z = sx * s[0], sz * s[2]
                            corners.append(c + [x * math.cos(yaw) + z * math.sin(yaw), sy * s[1], -x * math.sin(yaw) + z * math.cos(yaw)])
            Cn = np.array(corners)
            t = Cn @ ax
            rmax = np.linalg.norm(Cn - np.outer(t, ax), axis=1).max()
            R = Q - piv
            tq = R @ ax
            rq = np.linalg.norm(R - np.outer(tq, ax), axis=1)
            bad |= (rq <= rmax + pad) & (tq >= t.min() - pad) & (tq <= t.max() + pad)
        elif m["type"] == "slide":
            ax = np.array(m["axis"], float)
            for off in np.arange(m["range"][0], m["range"][1] + 1e-9, 0.25):
                boxes = [dict(center=list(piv + np.array(b["center"], float) + ax * off), size=b["size"], yaw=b.get("yaw", 0.0)) for b in bl]
                bad |= in_boxes(Q, boxes, pad=pad)
    return bad


CROSS = ("bridge", "pier")
tot = {"bank": 0, "apron": 0}
for kind, P in PTS.items():
    # assign every point to the hole whose felt+rail footprint is nearest
    owner = np.zeros(len(P), int)
    bestd = np.full(len(P), 1e9)
    for n in sorted(D.H):
        Q = _local(n, P)
        near = (np.abs(Q[:, 0]) < 120) & (np.abs(Q[:, 2]) < 120) & (np.abs(Q[:, 1]) < 30)
        d = np.full(len(P), 1e9)
        d[near] = _foot_dist(n, Q[near])
        upd = d < bestd
        owner[upd] = n
        bestd[upd] = d[upd]
    check(f"{kind}: every decoration point belongs to a hole (footprint distance <= 9)", bestd.max() <= 9.0, f"max {bestd.max():.2f}")
    for n in sorted(D.H):
        sel = owner == n
        if not sel.any():
            check(f"H{n} {kind}: present", False, "no points")
            continue
        Q = _local(n, P[sel])
        H = D.H[n]
        rep = REPORT["decoration"]["holes"].setdefault(n, {})
        tot[kind] += int(sel.sum())
        topn, dn = _visual_top_nearest(n, Q)
        tin = _top_inside(n, Q)
        cups = [H["cup"]]
        dcup = min(float(np.hypot(Q[:, 0] - c["position"][0], Q[:, 2] - c["position"][2]).min()) for c in cups)
        rcup = max(c["radius"] for c in cups)
        tee = H["tee"]["position"]
        lanes = [f for f in H["felt"] if abs(yaw_inv(np.array([tee[0]]), np.array([tee[2]]), f["center"], f.get("yaw", 0.0))[0][0]) <= f["size"][0] / 2
                 and abs(yaw_inv(np.array([tee[0]]), np.array([tee[2]]), f["center"], f.get("yaw", 0.0))[1][0]) <= f["size"][1] / 2]
        in_lane = np.zeros(len(Q), bool)
        for f in lanes:
            lx, lz = yaw_inv(Q[:, 0], Q[:, 2], f["center"], f.get("yaw", 0.0))
            in_lane |= (np.abs(lx) < f["size"][0] / 2 - 0.01) & (np.abs(lz) < f["size"][1] / 2 - 0.01)
        dtee = np.hypot(Q[:, 0] - tee[0], Q[:, 2] - tee[2])
        sw = _swept(n, Q)
        gap = in_boxes(Q, [GAPS[n]]) if n in GAPS else np.zeros(len(Q), bool)
        if gap.any():
            cross = [f for f in H["felt"] if f.get("kind") in CROSS or f["id"] == "plank"]
            dc = np.full(len(Q), 1e9)
            for f in cross:
                dc = np.minimum(dc, box_dist(Q, dict(center=f["center"], size=[f["size"][0], 0, f["size"][1]], yaw=f.get("yaw", 0.0))))
            gap_bad = gap & (dc > 1.3) & (Q[:, 1] > topn - 0.02 + 1e-3)    # in a gap volume only below the felt plane (cannot block a crossing)
        else:
            gap_bad = gap
        if kind == "bank":
            inside = _inside_felt(n, Q, 0.01)
            tmax = _max_top_within(n, Q)
            above = Q[:, 1] > tmax + 1e-3
            inwall = np.zeros(len(Q), bool)
            hidden = np.zeros(len(Q), bool)
            for w in H["walls"]:
                if "center" not in w or "size" not in w:
                    continue
                lx, lz = yaw_inv(Q[:, 0], Q[:, 2], w["center"], w.get("yaw", 0.0))
                m = (np.abs(lx) < w["size"][0] / 2 - 1e-3) & (np.abs(lz) < w["size"][2] / 2 - 1e-3)
                inwall |= m
                hidden |= m & (Q[:, 1] >= w["center"][1] - w["size"][1] / 2 - 1e-3) & (Q[:, 1] <= w["center"][1] + w["size"][1] / 2 + 1e-3)
            wall_bad = inwall & ~hidden          # over a wall footprint but outside every wall box (e.g. above a slot sill)
            tee_near = dtee < 2.5
            rep["bank"] = dict(points=int(len(Q)), inside_felt=int(inside.sum()), above_felt_top=int(above.sum()),
                               max_above_bordered_felt_top=round(float((Q[:, 1] - tmax).max()), 3), max_above_nearest_felt_top=round(float((Q[:, 1] - topn).max()), 3), in_wall_footprint=int(inwall.sum()),
                               outside_walls=int((~inwall).sum()), wall_height_violations=int(wall_bad.sum()), min_cup_dist=round(dcup, 2),
                               in_tee_lane=int(in_lane.sum()), within_2_5_of_tee=int(tee_near.sum()), in_mover_sweep=int(sw.sum()),
                               in_gap_volume=int(gap.sum()), max_dist_from_felt=round(float(dn.max()), 3))
            check(f"H{n} felt banks ({len(Q)} pts): outside every felt rectangle (B1), never above the felt top "
                  f"(max {rep['bank']['max_above_bordered_felt_top']:+.3f} vs the highest visual felt top within 1.3 studs) (B2)", not inside.any() and not above.any(),
                  f"inside {int(inside.sum())} e.g. {where(Q, inside)}, above {int(above.sum())} e.g. {where(Q, above)}")
            check(f"H{n} felt banks under rails stay inside a rail/wall box, the rest lie outside the rails (B3: {int(inwall.sum())} under, "
                  f"{int((~inwall).sum())} outside)", not wall_bad.any(), f"{int(wall_bad.sum())} e.g. {where(Q, wall_bad)}")
            check(f"H{n} felt banks vs cup (min {dcup:.2f} >= r {rcup} + 0.5) and tee lane ({len(lanes)} felt: none inside; "
                  f"{int(tee_near.sum())} pts within r 2.5 of the tee, all outside felt and below its top) (B4)",
                  dcup >= rcup + 0.5 and not in_lane.any() and not (tee_near & (inside | above)).any())
            check(f"H{n} felt banks clear of mover swept volumes (B5) and gap volumes except at crossing felt (B6)", not sw.any() and not gap_bad.any(),
                  f"sweep {int(sw.sum())} {where(Q, sw)}, gap {int(gap_bad.sum())} {where(Q, gap_bad)}")
        else:
            inside = _inside_felt(n, Q, 0.0)
            tin_ok = ~inside | (Q[:, 1] <= np.nan_to_num(tin, nan=1e9) - 0.1 + 1e-3)
            fd = _foot_dist(n, Q)
            rep["apron"] = dict(points=int(len(Q)), inside_felt_rect=int(inside.sum()), 
                                band_max_dist=round(float(fd.max()), 2), band_p50=round(float(np.median(fd)), 2), min_cup_dist=round(dcup, 2),
                                in_tee_lane=int(in_lane.sum()), in_mover_sweep=int(sw.sum()), in_gap_volume=int(gap.sum()))
            check(f"H{n} SnowCourse apron ({len(Q)} pts, {int(inside.sum())} over felt rectangles): over felt only hidden inside the slab (<= visual top - 0.1) (A1)",
                  tin_ok.all(), f"in slab {int((~tin_ok).sum())} {where(Q, ~tin_ok)}")
            check(f"H{n} SnowCourse apron band: max {fd.max():.2f} studs from the felt+rail footprint (<= 8.5) (A2)", fd.max() <= 8.5)
            check(f"H{n} SnowCourse apron vs cup/tee lane/movers/gaps (A3: cup min {dcup:.2f}; lane pts only hidden in the slab; sweep {int(sw.sum())}; gap volume {int(gap.sum())} pts on the rim ground, {int(gap_bad.sum())} above the felt plane)",
                  dcup >= rcup + 0.1 and (not (in_lane & ~tin_ok).any()) and not sw.any() and not gap_bad.any(),
                  f"sweep {where(Q, sw)} gap {where(Q, gap)}")
REPORT["decoration"]["points"] = tot
_bs = json.load(open(os.path.join(BLK, "build_stats_p2e.json")))
_g = [(k, v["gap_to_terrain_min"], v["gap_to_terrain_max"]) for k, v in _bs["apron"].items()]
check("SnowCourse apron hugs the terrain: triangle-centroid gap to the terrain Snow/Salt 0.025..0.075 in every apron mesh (A4)",
      all(0.025 <= a and b <= 0.075 for _, a, b in _g), str(_g))
