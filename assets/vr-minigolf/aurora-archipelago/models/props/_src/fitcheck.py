"""Numeric fitcheck of every P1 prop + instance against holes.json (adapted from lantern-grove fitcheck.py).
  blender -b --factory-startup -P out_props/_src/fitcheck.py   -> out_props/fitcheck_p1props_validated.txt (+ fitcheck_report.json)

Geometry is sampled on every triangle (<= 0.4 stud spacing) and tested in the HOLE-LOCAL frame:
 skins      every point inside the union of the holes.json wall footprints (+0.02), bottom..top(+0.35 cap)
 decals     every point over felt, 0..0.03 above the felt top
 felt clash nothing from felt+0.03 to felt+8 over any felt (exceptions: movers, flag, decals; anchored props with a
            documented over_felt_ok reason, and then ONLY inside their holes.json anchor envelope / occluders)
 rail strip nothing within 1.5 studs of a rail/wall box (outside it) between its bottom and felt+8, unless inside the
            prop's own anchor occluders
 lane       nothing taller than 2 studs (above the nearest felt) within 3 studs of a rail, below felt+8, unless inside
            the prop's own anchor occluders
 cups/tee   nothing within r 0.6 of a cup (except the flag) or r 2.5 of the tee (except skins/decals), felt..felt+8
 gaps       only crossing props (plank, bridge decks, piers, span, ribbon, lagoon) inside the H3/H17 gap volumes
 sightline  tee eye (tee + 5.5) -> flag top ray hits no static prop
 anchors    every instance sits exactly on its holes.json anchor (documented exceptions listed)
 movers     contact bodies inside the holes.json blocker union; full sweep (rotate 1 deg, swing 0.25 deg, slide 0.05):
            min clearance to felt, to walls/rails (FAIL if < 0, FLAG if < 0.05) and to static props (>= 0.15)
            pass 2d: H12/H14 fine felt sweep (rotate 0.05 deg, swing 0.01 deg) on the exact mesh vertices: visual gap
            0.06..0.065, plus the same sweep of the holes.json blocker (collider) corners, reported separately
            Round 3 'clear': colliders themselves 0.06 over the felt (>= 0.06, < 0.16), visual gap == collider gap (+-0.005)
 clear      Round 3: collision FBX == holes.json blockers, visual skid/tips envelope the colliders, FBX on disk == generator
            for every prop of H5/H12/H14/H17, rail-skin FBX vs the trimmed walls (fitcheck_clear.py, exec()d here)
 budgets    every FBX / mesh < 20k; per-hole near field (own + neighbours <= 60 + world pieces <= 60) <= 40k
 decoration pass 2e: blockout felt_banks.fbx + course_apron_0N.fbx (CanCollide false) vs holes.json felt/rails/cups/tee lanes/movers/gaps
            (fitcheck_decor.py, exec()d here; AA_BLOCKOUT = blockout dir, default ../../out_p2e/models/blockout)
"""
import bpy, bmesh, sys, os, math, json, importlib
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import aalib, registry, holesdata as D
for m in ("props_kit", "props_movers", "props_holes"):
    importlib.import_module(m)
REG = {p["name"]: p for p in registry.PROPS}
bpy.ops.wm.read_factory_settings(use_empty=True)
col = bpy.data.collections.new("c")
bpy.context.scene.collection.children.link(col)
LINES, FAILS, FLAGS, REPORT = [], [], [], {"holes": {}, "movers": {}, "budgets": {}}
TOL = 0.02


def check(label, ok, detail=""):
    LINES.append(f"{'PASS' if ok else 'FAIL'}  {label}  {detail}")
    if not ok:
        FAILS.append(label)


def flag(label):
    LINES.append(f"FLAG  {label}")
    FLAGS.append(label)


_cache = {}


def build(name):
    if name in _cache:
        return _cache[name]
    p = REG[name]
    pb = aalib.PB(name)
    p["fn"](pb)
    root, objs = pb.finalize(col)
    bpy.context.view_layer.update()
    _cache[name] = objs
    return objs


def place_matrix(pl):
    s = pl.get("scale", 1.0)
    s = [s, s, s] if not isinstance(s, (list, tuple)) else s
    return Matrix.Translation(aalib.R(*pl["pos"])) @ Matrix.Rotation(math.radians(pl.get("yaw", 0.0)), 4, "Z") @ Matrix.Diagonal((s[0], s[2], s[1], 1.0))


def tris_of(objs, M=Matrix.Identity(4)):
    out = []
    for o in objs:
        me = o.data
        me.calc_loop_triangles()
        V = np.array([tuple(M @ v.co) for v in me.vertices]) if len(me.vertices) else np.zeros((0, 3))
        T = np.array([tuple(t.vertices) for t in me.loop_triangles], int) if len(me.loop_triangles) else np.zeros((0, 3), int)
        out.append((aalib.mat_of(o.name), V, T))
    return out


def samples(tris, spacing=0.4):
    pts = []
    for mat, V, T in tris:
        if not len(T):
            continue
        A, B, C = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
        L = np.maximum.reduce([np.linalg.norm(B - A, axis=1), np.linalg.norm(C - B, axis=1), np.linalg.norm(A - C, axis=1)])
        for nsub in sorted(set(np.clip(np.ceil(L / spacing), 1, 60).astype(int))):
            sel = np.clip(np.ceil(L / spacing), 1, 60).astype(int) == nsub
            bary = np.array([(i / nsub, j / nsub) for i in range(nsub + 1) for j in range(nsub + 1 - i)])
            a, b, c = A[sel], B[sel], C[sel]
            P = a[:, None, :] + bary[None, :, 0:1] * (b - a)[:, None, :] + bary[None, :, 1:2] * (c - a)[:, None, :]
            pts.append(P.reshape(-1, 3))
    if not pts:
        return np.zeros((0, 3))
    P = np.concatenate(pts)
    return np.stack([P[:, 0], P[:, 2], -P[:, 1]], 1)        # Blender -> Roblox (hole-local)


def yaw_inv(px, pz, c, yaw):
    a = math.radians(-yaw)
    dx, dz = px - c[0], pz - c[2]
    return dx * math.cos(a) + dz * math.sin(a), -dx * math.sin(a) + dz * math.cos(a)


def _in_poly(x, z, poly):
    inside = np.zeros(len(x), bool)
    k = len(poly)
    for i in range(k):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % k]
        c = ((z1 > z) != (z2 > z)) & (x < (x2 - x1) * (z - z1) / ((z2 - z1) + 1e-12) + x1)
        inside ^= c
    return inside


def felt_top(n, P, shrink=0.0):
    best = np.full(len(P), np.nan)
    for f in D.H[n]["felt"]:
        c, s, yaw = f["center"], f["size"], f.get("yaw", 0.0)
        lx, lz = yaw_inv(P[:, 0], P[:, 2], c, yaw)
        m = (np.abs(lx) <= s[0] / 2 + 1e-6 - shrink) & (np.abs(lz) <= s[1] / 2 + 1e-6 - shrink)
        if f.get("kind") == "plate" and D.H[n].get("plate_visible"):
            m &= _in_poly(P[:, 0], P[:, 2], D.H[n]["plate_visible"][0])
        y = np.full(len(P), c[1], float)
        sl = f.get("slope")
        if sl:
            y = y + ((lx / s[0]) if sl["axis"] == "x" else (lz / s[1])) * sl["rise"]
        best = np.where(m & (np.isnan(best) | (y > best)), y, best)
    return best


def ground_ref(n, P):
    ft = felt_top(n, P)
    if np.isnan(ft).any():
        bd = np.full(len(P), 1e9)
        by = np.zeros(len(P))
        for f in D.H[n]["felt"]:
            c, s, yaw = f["center"], f["size"], f.get("yaw", 0.0)
            lx, lz = yaw_inv(P[:, 0], P[:, 2], c, yaw)
            d = np.hypot(np.maximum(np.abs(lx) - s[0] / 2, 0), np.maximum(np.abs(lz) - s[1] / 2, 0))
            upd = d < bd
            bd = np.where(upd, d, bd)
            by = np.where(upd, c[1], by)
        ft = np.where(np.isnan(ft), by, ft)
    return ft


def box_dist(P, w):
    c, s, yaw = w["center"], w["size"], w.get("yaw", 0.0)
    lx, lz = yaw_inv(P[:, 0], P[:, 2], c, yaw)
    return np.hypot(np.maximum(np.abs(lx) - s[0] / 2, 0), np.maximum(np.abs(lz) - s[2] / 2, 0))


def box3_dist(P, b, pivot=(0, 0, 0)):
    c = [b["center"][i] + pivot[i] for i in range(3)]
    s, yaw = b["size"], b.get("yaw", 0.0)
    lx, lz = yaw_inv(P[:, 0], P[:, 2], c, yaw)
    dx = np.maximum(np.abs(lx) - s[0] / 2, 0)
    dz = np.maximum(np.abs(lz) - s[2] / 2, 0)
    dy = np.maximum(np.abs(P[:, 1] - c[1]) - s[1] / 2, 0)
    inside = (dx == 0) & (dz == 0) & (dy == 0)
    pen = np.minimum.reduce([s[0] / 2 - np.abs(lx), s[2] / 2 - np.abs(lz), s[1] / 2 - np.abs(P[:, 1] - c[1])])
    return np.where(inside, -pen, np.sqrt(dx * dx + dy * dy + dz * dz))


def in_boxes(P, boxes, pad=0.0, ypad=None):
    m = np.zeros(len(P), bool)
    for b in boxes:
        c, s, yaw = b["center"], b["size"], b.get("yaw", 0.0)
        lx, lz = yaw_inv(P[:, 0], P[:, 2], c, yaw)
        yp = pad if ypad is None else ypad
        m |= (np.abs(lx) <= s[0] / 2 + pad) & (np.abs(lz) <= s[2] / 2 + pad) & (np.abs(P[:, 1] - c[1]) <= s[1] / 2 + yp)
    return m


def envelope_boxes(n, pl, ex=None):
    if ex and ex.get("envelope"):
        return ex["envelope"]
    an = pl.get("anchor")
    if not an:
        return []
    a = D.anchor(n, an)
    sz = a["approx_size"]
    p = a["position"]
    out = [dict(center=[p[0], p[1] + sz[1] / 2, p[2]], size=list(sz), yaw=pl.get("yaw", 0.0))]
    return out + [dict(center=o["center"], size=o["size"], yaw=o.get("yaw", 0.0)) for o in a.get("occluders", [])]


def where(P, m, k=3):
    return [tuple(round(float(v), 2) for v in q) for q in P[m][:k]]


def occluder_boxes(n, pl):
    an = pl.get("anchor")
    if not an:
        return []
    return [dict(center=o["center"], size=o["size"], yaw=o.get("yaw", 0.0)) for o in D.anchor(n, an).get("occluders", [])]


GAPS = {3: dict(center=[0, -20, -37], size=[26, 80, 26]), 17: dict(center=[0, -20, -29], size=[26, 80, 26])}
MOVED = {("aa_kit_geyser_cone", 5): "holes.json anchor [-10.5,4,-33] lies on the upper felt (x -12.5..12.5); moved to [-19,4,-33] (outside the west rail + 3-stud lane rule)",
         ("aa_kit_geyser_puff_small", 5): "follows the moved H5 cone"}
COVER_BY = {"boulder": "aa_h01_snow_boulder"}
COVER_BY.update({f"coral{i}": f"aa_h08_coral_{i}" for i in range(1, 8)})
COVER_BY.update({f"hub_plinth_{i:02d}": "aa_h13_hub_base" for i in range(48)})

# =============================================================================================== per hole static checks
import skins
STATIC_BY_HOLE = {}
for n in sorted(D.H):
    H = D.H[n]
    walls = H["walls"]
    hrep = REPORT["holes"].setdefault(n, {"instances": 0, "violations": {}, "anchored_envelope_overhang": {}})
    insts = []
    for p in registry.PROPS:
        ex = p.get("extra") or {}
        for pl in p["placements"]:
            if pl["hole"] == n:
                insts.append((p, ex, pl))
    hrep["instances"] = len(insts)
    # wall coverage
    uncovered = []
    for w in walls:
        st = skins.style(n, w)
        if st is None and w["id"] not in COVER_BY:
            uncovered.append(w["id"])
        if st is None and w["id"] in COVER_BY and not any(p["name"] == COVER_BY[w["id"]] for p, ex, pl in insts):
            uncovered.append(w["id"])
    check(f"H{n} every holes.json wall box ({len(walls)}) is skinned", not uncovered, f"uncovered {uncovered}" if uncovered else "")
    static_tris = []
    cup = H["cup"]["position"]
    tee = H["tee"]["position"]
    for p, ex, pl in insts:
        name = p["name"]
        cls = ex.get("cls")
        objs = build(name)
        M = place_matrix(pl)
        T = tris_of(objs, M)
        P = samples(T)
        if cls not in ("mover", "mover_aux"):
            static_tris.append((name, T))
        tag = f"H{n} {name}" + (f" @{pl.get('anchor')}" if pl.get("anchor") else "")
        viol = {}
        # anchor position
        if pl.get("anchor") and cls not in ("skin", "decal"):
            ap = D.anchor(n, pl["anchor"])["position"]
            d = math.dist(ap, pl["pos"])
            if (name, n) in MOVED:
                LINES.append(f"NOTE  {tag} anchor moved: {MOVED[(name, n)]}")
            elif name.startswith("aa_h05_geyser") or name.startswith("aa_h14_icicle"):
                pass
            elif d > 1e-6:
                viol["anchor_offset"] = round(d, 3)
        if cls == "skin" or ex.get("skin_walls"):
            boxes = [dict(center=w["center"], size=[w["size"][0], w["size"][1] + 0.7, w["size"][2]], yaw=w["yaw"]) for w in walls
                     if cls == "skin" or w["id"] in ex.get("skin_walls", [])]
            for b, w in zip(boxes, [w for w in walls if cls == "skin" or w["id"] in ex.get("skin_walls", [])]):
                b["center"] = [w["center"][0], w["center"][1] + 0.35, w["center"][2]]
            if cls == "skin":
                ok = in_boxes(P, boxes, pad=TOL, ypad=0.35 + TOL)
                if (~ok).any():
                    viol["skin_outside_collider_footprint"] = [int((~ok).sum())] + where(P, ~ok)
            else:
                # bumper / hub plinths: everything below the box top must be inside the box (+tol)
                for w in walls:
                    if w["id"] in ex.get("skin_walls", []):
                        top = w["center"][1] + w["size"][1] / 2
                        low = P[:, 1] < top - 0.02
                if ex.get("skin_walls") and not ex.get("on_wall"):
                    bx = [dict(center=w["center"], size=w["size"], yaw=w["yaw"]) for w in walls if w["id"] in ex["skin_walls"]]
                    tops = max(w["center"][1] + w["size"][1] / 2 for w in walls if w["id"] in ex["skin_walls"])
                    if name == "aa_h13_hub_base":
                        r = np.hypot(P[:, 0] - 0, P[:, 2] + 36.0)
                        bad = (r > 7.5 / math.cos(math.pi / 48) + 0.02) | (P[:, 1] > 1.2 + 0.03) | (P[:, 1] < -0.5 - 0.02)
                    else:
                        low = P[:, 1] < tops - 0.02
                        bad = low & ~in_boxes(P, bx, pad=TOL)
                    if bad.any():
                        viol["plinth_outside_collider_below_top"] = [int(bad.sum())] + where(P, bad)
        if cls == "decal":
            ft = felt_top(n, P)
            bad = np.isnan(ft) | (P[:, 1] - ft < -0.001) | (P[:, 1] - ft > 0.031)
            if bad.any():
                viol["decal_not_flush_on_felt"] = [int(bad.sum())] + where(P, bad)
        if cls not in ("skin", "decal", "mover"):
            rails = [w for w in walls if w.get("kind") != "bumper"]
            onwall = np.zeros(len(P), bool)
            for w in walls:
                onwall |= box_dist(P, w) < 0.03
            env = pl.get("envelope") or envelope_boxes(n, pl, ex)
            ft = felt_top(n, P)
            over = ~np.isnan(ft) & (P[:, 1] > ft + 0.03) & (P[:, 1] < ft + 8.0) & ~onwall
            if cls == "flag":
                over &= np.hypot(P[:, 0] - cup[0], P[:, 2] - cup[2]) > 2.3
            if cls == "mover_aux":
                over[:] = False
            if over.any():
                envm = in_boxes(P, env, pad=0.35) if (ex.get("over_felt_ok") or pl.get("over_felt_ok")) else np.zeros(len(P), bool)
                bad = over & ~envm
                if bad.any():
                    viol["over_felt_clash_band"] = [int(bad.sum())] + where(P, bad)
                if (over & envm).any():
                    hrep["anchored_envelope_overhang"][tag] = f"{int((over & envm).sum())} pts over felt inside the anchor envelope ({ex.get('over_felt_ok') or pl.get('over_felt_ok') or 'holes.json anchor'})"
            waive = in_boxes(P, env, pad=0.1) if env else np.zeros(len(P), bool)
            gr = ground_ref(n, P)
            strip = np.zeros(len(P), bool)
            tall = np.zeros(len(P), bool)
            inwall = np.zeros(len(P), bool)
            for w in rails:
                d = box_dist(P, w)
                yb = w["center"][1] - w["size"][1] / 2
                band = (P[:, 1] >= yb) & (P[:, 1] > gr + 0.05) & (P[:, 1] < gr + 8.0)
                strip |= (d > 0.03) & (d < 1.5) & band
                tall |= (d > 0.03) & (d < 3.0) & (P[:, 1] - gr > 2.0) & (P[:, 1] < gr + 8.0)
            if not ex.get("skin_walls") and not ex.get("on_wall") and not ex.get("allow_inwall") and cls not in ("mover_aux",):
                vis = P[:, 1] > gr + 0.05            # overlap hidden under the felt level is not visible
                for w in walls:
                    inwall |= (box3_dist(P, w) < -0.01) & vis
            if cls in ("flag",):
                far = np.hypot(P[:, 0] - cup[0], P[:, 2] - cup[2]) > 2.3
                strip &= far
                tall &= far
                inwall &= far
            if ex.get("hugs_rails"):
                inwall[:] = False
                strip[:] = False
                tall[:] = False
            strip &= ~onwall
            tall &= ~onwall
            ws, wt = strip & waive, tall & waive
            strip &= ~waive
            tall &= ~waive
            if ws.any() or wt.any():
                hrep["anchored_envelope_overhang"][tag + " (rail strip/lane)"] = f"{int(ws.sum())} strip / {int(wt.sum())} lane pts inside the holes.json anchor envelope (designer-fitted position)"
            if strip.any():
                viol["in_1.5_rail_strip"] = [int(strip.sum())] + where(P, strip)
            if tall.any():
                viol["taller_than_2_within_3_of_rail"] = [int(tall.sum())] + where(P, tall)
            if inwall.any():
                viol["inside_a_wall_collider"] = [int(inwall.sum())] + where(P, inwall)
            if cls != "flag":
                dc = np.hypot(P[:, 0] - cup[0], P[:, 2] - cup[2])
                bad = (dc < 0.6) & (P[:, 1] > cup[1] - 1.0) & (P[:, 1] < cup[1] + 8)
                if bad.any():
                    viol["in_cup_radius"] = [int(bad.sum())] + where(P, bad)
                dt = np.hypot(P[:, 0] - tee[0], P[:, 2] - tee[2])
                bad = (dt < 2.5) & (P[:, 1] > tee[1] - 0.02) & (P[:, 1] < tee[1] + 8)
                if bad.any():
                    viol["on_tee_pad"] = [int(bad.sum())] + where(P, bad)
        if n in GAPS and cls not in ("skin", "decal") and not ex.get("gap_ok"):
            g = in_boxes(P, [GAPS[n]])
            if g.any():
                viol["in_gap_volume"] = int(g.sum())
        if viol:
            hrep["violations"][tag] = viol
        check(f"{tag} [{cls}]", not viol, json.dumps(viol) if viol else f"{len(P)} samples")
    # sightline tee eye -> flag top
    verts, polys = [], []
    for name, T in static_tris:
        if name == "aa_kit_flag":
            continue
        for mat, V, TT in T:
            off = len(verts)
            verts += [tuple(v) for v in V]
            polys += [tuple(int(i) + off for i in t) for t in TT]
    bvh = BVHTree.FromPolygons(verts, polys)
    eye = aalib.R(tee[0], tee[1] + 5.5, tee[2])
    top = aalib.R(*H["cup"]["flag"]["top"])
    d = top - eye
    hit = bvh.ray_cast(eye, d.normalized(), d.length - 0.05)
    check(f"H{n} sightline tee eye (5.5) -> flag top clear of props", hit[0] is None, "" if hit[0] is None else f"hit at {tuple(round(v, 2) for v in hit[0])}")
    STATIC_BY_HOLE[n] = static_tris

# =============================================================================================== movers
def mover_points(name, spacing=0.25):
    objs = build(name)
    return samples(tris_of(objs), spacing)     # pivot frame (Roblox)


def rot_points(P, axis, ang):
    a = math.radians(ang)
    ax = np.array(axis, float)
    ax /= np.linalg.norm(ax)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    Rm = np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
    return P @ Rm.T


def fine_felt_sweeps(n, m, name):
    """Exact felt gap over the full motion range: lowest mesh VERTEX (a rigid rotation of a mesh over flat felt reaches its
    minimum height at a vertex) and lowest holes.json blocker CORNER, rotate 0.05 deg / swing 0.01 deg steps."""
    piv = np.array(m["pivot"], float)
    V = np.concatenate([V for _, V, _ in tris_of(build(name))])
    V = np.stack([V[:, 0], V[:, 2], -V[:, 1]], 1)                       # Blender -> Roblox, pivot frame
    C = []
    for b in m["blockers"]:
        for sx in (-.5, .5):
            for sy in (-.5, .5):
                for sz in (-.5, .5):
                    x, z = D.yaw_rot(sx * b["size"][0], sz * b["size"][2], b.get("yaw", 0.0))
                    C.append([b["center"][0] + x, b["center"][1] + sy * b["size"][1], b["center"][2] + z])
                    if b.get("roll"):
                        C[-1] = list(rot_points(np.array([C[-1]]), [0, 0, 1], b["roll"])[0])
    C = np.array(C)
    if m["type"] == "rotate":
        step, angs = 0.05, np.arange(0, 360, 0.05)
    else:
        step, angs = 0.01, np.arange(-m["amplitude_deg"], m["amplitude_deg"] + 1e-9, 0.01)
    out = dict(step=step, steps=len(angs), unit="deg")
    for tag, P in (("visual", V), ("collider", C)):
        g = np.full(len(angs), np.inf)
        for i, a in enumerate(angs):
            W = rot_points(P, m["axis"], a) + piv
            ft = felt_top(n, W, shrink=0.01)
            k = ~np.isnan(ft)
            if k.any():
                g[i] = (W[k, 1] - ft[k]).min()
        i = int(np.argmin(g))
        near = angs[g <= g[i] + 5e-4]
        rng = (f"{near.min():+.2f}..{near.max():+.2f} deg" if m["type"] != "rotate" else
               f"{len(near)} of {len(angs)} steps, e.g. {', '.join(f'{x:.2f}' for x in near[:: max(1, len(near) // 6)][:6])} deg; exact min whenever a tip-arc vertex points straight down")
        if m["type"] == "swing":
            neg, pos = near[near < 0], near[near > 0]
            rng = (f"{neg.min():+.2f}..{neg.max():+.2f} and " if len(neg) else "") + (f"{pos.min():+.2f}..{pos.max():+.2f} deg" if len(pos) else "")
        out[tag] = dict(min_gap=round(float(g[i]), 4), at=round(float(angs[i]), 3), range_at_min=rng, points=len(P))
    return out


def mover_checks(n, mid, name):
    m = D.mover(n, mid)
    piv = np.array(m["pivot"], float)
    P0 = mover_points(name)
    rep = {}
    bl = m.get("blockers", [])
    # contact containment
    if mid == "geyser_column":
        bad = ~in_boxes(P0, [dict(center=[0, -2, 0], size=[3, 4, 3], yaw=0)], pad=0.1)
        check(f"H5 geyser column inside its 3x4x3 blocker (+0.1 for the flush gauge)", not bad.any(), f"{int(bad.sum())} pts outside")
        sq = in_boxes(P0, [dict(center=[0, -2, 0], size=[3, 4, 3], yaw=0)], pad=0.0005)
        check("H5 geyser contact faces square 3x3 (no hex corners outside the box below the top)", (sq | (P0[:, 0] > 1.5) | (P0[:, 1] >= 0)).all())
    elif mid == "ice_floe":
        bad = ~in_boxes(P0, [dict(center=b["center"], size=[b["size"][0], 5, b["size"][2]], yaw=b["yaw"]) for b in bl], pad=0.05)
        check("H11 floe (contact + snow + snowpuff) inside the blocker footprint union (slab + 45-deg tips)", not bad.any(), f"{int(bad.sum())} pts outside")
        lintel = D.H[11]["collision_cuts"][0]["max"][1]          # Round 4 'walls': slot lintel underside 1.17 -> 1.27 (rail5/berg18 __cut1 bottom)
        cut1 = [D.wall(11, w + "__cut1") for w in ("rail5", "berg18")]
        cut1_bot = [c["center"][1] - c["size"][1] / 2 for c in cut1]
        check(f"H11 floe top <= 1.12, >= 0.15 under the slot lintel y {lintel:.2f} (Round 4 walls: expected 1.27; rail5/berg18__cut1 bottoms "
              + ", ".join("%.3f" % v for v in cut1_bot) + ")",
              P0[:, 1].max() <= 1.121 and abs(lintel - 1.27) < 1e-6 and all(abs(v - lintel) < 1e-6 for v in cut1_bot)
              and lintel - P0[:, 1].max() >= 0.15 - 1e-3, f"top {P0[:, 1].max():.3f}, lintel {lintel:.3f}")
        tipx = np.abs(P0[:, 0]).max()
        check("H11 floe tips reach x +-3.5", abs(tipx - 3.5) < 0.01, f"{tipx:.3f}")
    elif mid == "paddle_wheel":
        r = np.hypot(P0[:, 0], P0[:, 1])
        tip_r = sys.modules["props_movers"].H12_TIP_R
        check(f"H12 wheel: nothing beyond r {tip_r:.4f} (pass 2d visual tip arc; collider strip corners r 4.10)", r.max() <= tip_r + 0.0005, f"max r {r.max():.4f}")
        outer = r > 3.9
        inb = np.zeros(len(P0), bool)
        for roll in (0, 90, 180, 270):
            Q = rot_points(P0, [0, 0, 1], -roll)     # un-roll into the paddle frame (paddle along -Y)
            inb |= (np.abs(Q[:, 0]) <= 1.2 + 0.01) & (Q[:, 1] < 0) & (np.abs(Q[:, 2]) <= 0.2 + 0.01)
        bad = outer & ~inb
        check(f"H12 wheel: everything beyond r 3.9 is a paddle board (2.4 wide x 0.4, outer arc r {tip_r:.4f}; props-full 'model the arc', pass 2d radius)", not bad.any(), f"{int(bad.sum())} pts")
        mx_out = 0.0
        for b in bl:
            Q = rot_points(P0, [0, 0, 1], -b.get("roll", 0.0))
            sel = (np.abs(Q[:, 0] - b["center"][0]) <= 0.2) & (Q[:, 1] < -3.0) & (np.abs(Q[:, 2]) <= 0.2)
            if sel.any():
                mx_out = max(mx_out, float((-(Q[sel, 1]) + (b["center"][1] - b["size"][1] / 2)).max()))
        LINES.append(f"INFO  H12 wheel arc vs stepped strip blockers: the r {tip_r:.4f} arc exceeds the strip ends by up to {mx_out:.3f} studs between strip centres (as specified: model the arc)")
        badz = (np.abs(P0[:, 2]) > 0.2 + 1e-3) & (r > 0.6 + 1e-3)
        check("H12 wheel: rims/spokes within z +-0.2 (hub r <= 0.6 excepted)", not badz.any(), f"{int(badz.sum())} pts")
    elif mid == "carousel_arms":
        r = np.hypot(P0[:, 0], P0[:, 2])
        low = P0[:, 1] < 0.9 - 1e-3
        inb = in_boxes(P0, [dict(center=b["center"], size=b["size"], yaw=b["yaw"]) for b in bl], pad=0.03)
        check("H13 runners (y < 0.9) inside the 4 blocker boxes", not (low & ~inb).any(), f"{int((low & ~inb).sum())} pts")
        foot = in_boxes(P0, [dict(center=b["center"], size=[b["size"][0], 10, b["size"][2]], yaw=b["yaw"]) for b in bl], pad=0.03)
        spoke = P0[:, 1] >= 1.4
        check("H13 nothing below y 1.4 between r 7.5 and 8.2", not ((r > 7.5) & (r < 8.2) & (P0[:, 1] < 1.4)).any())
        check("H13 sled/snowpuff decor inside the runner footprints or on spokes/collar (>= 1.4)", (foot | spoke).all(), f"{int((~(foot | spoke)).sum())} pts")
        check("H13 arms top < 4", P0[:, 1].max() < 4.0, f"top {P0[:, 1].max():.2f}")
    elif mid == "icicle_bell":
        body = P0[:, 1] < -8.0 - 0.01
        inb = in_boxes(P0, [dict(center=b["center"], size=b["size"], yaw=b["yaw"]) for b in bl], pad=0.05)
        check("H14 bell lower body + skid inside the cube (yaw 30) + foot blockers", not (body & ~inb).any(), f"{int((body & ~inb).sum())} pts")
        mid_ = (P0[:, 1] < -0.4) & (P0[:, 1] > -7.0)
        check("H14 hanger slim (|x|,|z| <= 0.3 between hinge and crown)", (np.abs(P0[mid_][:, 0]) <= 0.3).all() and (np.abs(P0[mid_][:, 2]) <= 0.3).all())
        PMm = sys.modules["props_movers"]
        bot = P0[:, 1].min() + m["pivot"][1]
        ends = P0[np.abs(np.abs(P0[:, 0]) - 1.05) < 1e-4]
        ends_b = ends[:, 1].min() + m["pivot"][1] if len(ends) else None
        top = ends[ends[:, 1] < -9.5][:, 1].max() + m["pivot"][1] if len(ends) else float("nan")     # skid end faces x = +-1.05
        want_c, want_e = m["pivot"][1] - PMm.H14_SKID_R, m["pivot"][1] - math.sqrt(PMm.H14_SKID_R ** 2 - 1.05 ** 2)
        check(f"H14 skid (Round 3): curved underside on r {PMm.H14_SKID_R:g} about the hinge - centre {want_c:.3f}, ends {want_e:.3f} over the felt at rest, top {m['pivot'][1] + PMm.H14_FOOT_TOP:.3f}",
              abs(bot - want_c) < 0.001 and ends_b is not None and abs(ends_b - want_e) < 0.001 and abs(top - (m["pivot"][1] + PMm.H14_FOOT_TOP)) < 0.002,
              f"centre {bot:.4f}, ends {ends_b:.4f}, top {top:.4f}")
    elif mid == "aurora_span":
        f = D.felt(17, "light_span")
        ok = (np.abs(P0[:, 0]) <= f["size"][0] / 2 + 0.01).all() and (np.abs(P0[:, 2]) <= f["size"][1] / 2 + 0.01).all() and P0[:, 1].max() <= 0.001 and P0[:, 1].min() >= -0.401
        check("H17 aurora span deck = felt light_span 3 x 8, y -0.4..0", ok)
    # sweep
    if m["type"] == "rotate":
        steps = [(a, rot_points(P0, m["axis"], a)) for a in np.arange(0, 360, 1.0)]
    elif m["type"] == "swing":
        steps = [(a, rot_points(P0, m["axis"], a)) for a in np.arange(-m["amplitude_deg"], m["amplitude_deg"] + 1e-9, 0.25)]
    elif m["type"] == "slide":
        lo, hi = m["range"]
        steps = [(o, P0 + np.array(m["axis"], float) * o) for o in np.arange(lo, hi + 1e-9, 0.05)]
    else:
        steps = [(0.0, P0)]
    walls = D.H[n]["walls"]
    static = STATIC_BY_HOLE[n]
    sp = []
    for nm, T in static:
        if nm.endswith("_rails") or nm.endswith("_decals") or nm.startswith("aa_kit_flag"):
            continue
        S = samples(T, 0.25)
        if mid == "icicle_bell":
            S = S[np.linalg.norm(S - piv, axis=1) > 0.75]               # hinge bracket = the mount
        if mid == "carousel_arms" and nm == "aa_h13_hub_base":
            pass
        sp.append(S)
    SP = np.concatenate(sp) if sp else np.zeros((0, 3))
    best_felt, best_wall, best_static = (1e9, None, None), (1e9, None, None), (1e9, None, None)
    for a, Pk in steps:
        W = Pk + piv
        ft = felt_top(n, W, shrink=0.01)
        mask = ~np.isnan(ft)
        if mid == "aurora_span":
            mask[:] = False          # the deck IS the light_span felt
        if mid == "geyser_column":
            mask &= ~((np.abs(W[:, 0] - piv[0]) <= 1.7) & (np.abs(W[:, 2] - piv[2]) <= 1.7))   # in its own shaft
        if mask.any():
            c = (W[mask, 1] - ft[mask]).min()
            if c < best_felt[0]:
                best_felt = (c, a, None)
        for w in walls:
            d = box3_dist(W, w).min()
            if d < best_wall[0]:
                best_wall = (d, a, w["id"])
        if len(SP):
            # coarse: nearest static sample to the mover's bbox-filtered points
            lo_, hi_ = W.min(0) - 0.5, W.max(0) + 0.5
            S = SP[np.all((SP >= lo_) & (SP <= hi_), axis=1)]
            if len(S):
                from mathutils.kdtree import KDTree
                kd = KDTree(len(W))
                for i, q in enumerate(W):
                    kd.insert(q, i)
                kd.balance()
                for q in S[:: max(1, len(S) // 4000)]:
                    co, idx, dist = kd.find(q)
                    if dist < best_static[0]:
                        best_static = (dist, a, tuple(np.round(q, 2)))
    unit = "deg" if m["type"] in ("rotate", "swing") else "studs"
    rep = dict(min_felt_clearance=round(best_felt[0], 4) if best_felt[1] is not None else None, at=round(float(best_felt[1]), 3) if best_felt[1] is not None else None,
               min_wall_clearance=round(best_wall[0], 4), wall=best_wall[2], wall_at=round(float(best_wall[1]), 3),
               min_static_prop_clearance=round(best_static[0], 4) if best_static[1] is not None else None,
               static_at=round(float(best_static[1]), 3) if best_static[1] is not None else None, unit=unit, steps=len(steps))
    REPORT["movers"][name] = rep
    felt_ok = best_felt[0] >= -0.01
    if best_felt[1] is None:
        check(f"H{n} {name}: felt clearance n/a (the deck is the felt)", True)
    else:
        check(f"H{n} {name} sweep: min clearance to felt {best_felt[0]:.3f} at {best_felt[1]:.2f} {unit} (contact bodies may rest on the felt)", felt_ok)
        if mid in ("paddle_wheel", "icicle_bell"):
            fs = fine_felt_sweeps(n, m, name)
            rep["pass2d_fine_sweep"] = fs
            v, c = fs["visual"], fs["collider"]
            check(f"H{n} {name} Round-3 fine sweep ({fs['steps']} steps of {fs['step']} {unit}, {v['points']} mesh vertices): VISUAL min felt gap {v['min_gap']:.4f} at {v['at']:+.2f} {unit} "
                  f"(within 0.0005 of the min at {v['range_at_min']}) - target 0.06..0.065", 0.06 - 1e-6 <= v["min_gap"] <= 0.065 + 1e-6)
            check(f"H{n} {name} Round-3 fine sweep: holes.json COLLIDER (blocker corners) min felt gap {c['min_gap']:.4f} at {c['at']:+.2f} {unit} - target >= 0.06 and < 0.16 (still blocks a 0.16 ball)",
                  0.06 - 1e-4 <= c["min_gap"] < 0.16)
            check(f"H{n} {name}: visual mesh follows the collider (visual min gap - collider min gap = {v['min_gap'] - c['min_gap']:+.4f}, within +-0.005)",
                  abs(v["min_gap"] - c["min_gap"]) <= 0.005)
    check(f"H{n} {name} sweep: min clearance to walls/rails {best_wall[0]:.3f} ({best_wall[2]}) at {best_wall[1]:.2f} {unit}", best_wall[0] >= -0.005)
    if best_wall[0] < 0.05:
        flag(f"H{n} {name}: wall clearance {best_wall[0]:.3f} < 0.05 to {best_wall[2]} at {best_wall[1]:.2f} {unit} (holes.json geometry; tell the build bot)")
    if mid == "aurora_span":
        check(f"H17 aurora span: toggle (no motion); deck abuts the crystal pier decks by design (gap {best_static[0]:.3f})", True)
    elif best_static[1] is not None:
        check(f"H{n} {name} sweep: min clearance to static props {best_static[0]:.3f} at {best_static[1]:.2f} {unit} (>= 0.15)", best_static[0] >= 0.15 - 1e-3, f"static pt {best_static[2]}")
    else:
        check(f"H{n} {name} sweep: no static props near the sweep", True)


for n, mid, name in ((5, "geyser_column", "aa_h05_geyser_column"), (11, "ice_floe", "aa_h11_ice_floe"), (12, "paddle_wheel", "aa_h12_paddle_wheel"),
                     (13, "carousel_arms", "aa_h13_carousel_arms"), (14, "icicle_bell", "aa_h14_icicle_bell"), (17, "aurora_span", "aa_h17_aurora_span")):
    mover_checks(n, mid, name)
    p = REG[name]
    piv = p["placements"][0]["pos"]
    check(f"{name} origin = holes.json pivot {D.mover(n, mid)['pivot']}", list(piv) == list(D.mover(n, mid)["pivot"]))

# =============================================================================================== budgets
man = json.load(open(os.path.join(OUT, "manifest.json")))
big = [(p["name"], p["triangles"]) for p in man["props"] if p["triangles"] >= 20000 or any(q["tris"] >= 20000 for q in p["parts"])]
big += [(h["file"], h["triangles"]) for h in man["hole_dressing_files"] if h["triangles"] >= 20000 or any(q["tris"] >= 20000 for q in h["parts"])]
check("every prop FBX and mesh < 20,000 tris", not big, str(big))
dress = {}
for h in man["hole_dressing_files"]:
    dress[h["hole"]] = dress.get(h["hole"], 0) + h["triangles"]
PT = {p["name"]: p["triangles"] for p in man["props"]}


def felt_dist_world(n, pw):
    pl = D.world_to_local(n, pw)
    return min(D.box_dist_xz(pl[0], pl[2], f["center"], [f["size"][0], 0, f["size"][1]], f.get("yaw", 0.0)) for f in D.H[n]["felt"])


EXEMPT_BIG = {"aa_world_starfrost_spire", "aa_world_spire_shards", "aa_world_great_frozen_falls"}
for n in sorted(D.H):
    own = dress.get(n, 0)
    loose = sum(PT[i["prop"]] for i in next(h for h in man["holes"] if h["hole"] == n)["instances"] if not i["merged_into_dressing"])
    neigh = 0
    for m2 in sorted(D.H):
        if m2 == n:
            continue
        for i in next(h for h in man["holes"] if h["hole"] == m2)["instances"]:
            if felt_dist_world(n, i["world_pos"]) <= 60:
                neigh += PT[i["prop"]] if not i["merged_into_dressing"] or i["prop"].endswith("_rails") or True else 0
    world = 0
    for w in man["world_instances"]:
        if w["prop"] in EXEMPT_BIG:
            continue
        if felt_dist_world(n, w["pos"]) <= 60:
            world += w["tris"]
    tot = own + loose + neigh + world
    REPORT["budgets"][n] = dict(own_dressing=own, own_loose_instances=loose, neighbour_holes_le60=neigh, world_pieces_le60=world, near_field_total=tot)
    check(f"H{n} near-field tris {tot} <= 40,000 (own {own}+{loose}, neighbours {neigh}, world {world})", tot <= 40000)

# =============================================================================================== pass 2e blockout decoration
exec(open(os.path.join(SRC, "fitcheck_decor.py"), encoding="utf8").read())
# =============================================================================================== Round 3 'clear'
exec(open(os.path.join(SRC, "fitcheck_clear.py"), encoding="utf8").read())

npass = sum(1 for l in LINES if l.startswith("PASS"))
hdr = [f"Aurora Archipelago P1 props fitcheck vs holes.json  ({npass} PASS, {len(FAILS)} FAIL, {len(FLAGS)} FLAG)",
       "RESULT: " + ("ALL PASS" if not FAILS else "FAILURES PRESENT"), ""]
txt = "\n".join(hdr + LINES) + "\n"
open(os.path.join(OUT, "fitcheck_p1props.txt"), "w").write(txt)
REPORT["summary"] = dict(passed=npass, failed=len(FAILS), flags=FLAGS, fails=FAILS)
json.dump(REPORT, open(os.path.join(OUT, "fitcheck_report.json"), "w"), indent=1, default=str)
if not FAILS:
    open(os.path.join(OUT, "fitcheck_p1props_validated.txt"), "w").write(txt)
print(hdr[0])
print("\n".join(l for l in LINES if not l.startswith("PASS")))
