"""Numeric fit checks for the hard constraints. Run: blender -b -P models/_src/fitcheck.py
Writes _src/fitcheck.txt."""
import bpy, sys, os, math, importlib
from mathutils import Vector

SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC)
import lglib, registry
for m in ("props_dressing", "props_moving", "props_hero", "props_p2p3", "props_variants", "props_cards", "props_pass6", "props_pass7", "props_pass8", "props_pass10"):
    importlib.import_module(m)
REG = {p["name"]: p for p in registry.PROPS}
bpy.ops.wm.read_factory_settings(use_empty=True)
col = bpy.data.collections.new("c")
bpy.context.scene.collection.children.link(col)
lines = []


def build(name):
    p = REG[name]
    pb = lglib.PB(name)
    post = p["fn"](pb)
    root, objs = pb.finalize(col)
    if callable(post):
        post(root, objs)
    bpy.context.view_layer.update()
    return objs


def ray_hits(objs, origin, direction, dist=50.0):
    for o in objs:
        ok, loc, n, i = o.ray_cast(Vector(origin), Vector(direction).normalized(), distance=dist)
        if ok:
            return True
    return False


def check(label, cond, detail=""):
    lines.append(f"{'PASS' if cond else 'FAIL'}  {label}  {detail}")


def rb(objs):
    mn, mx = lglib.bbox_blender(objs)
    return mn, mx


# 1. mushroom tunnel: rays along X through the stem must pass inside |z|<=3.45, h<=2.0 (walls) / 2.9 (crown)
objs = build("mushroom_house_large_tunnel")
inside = all(not ray_hits(objs, (-8, y, z), (1, 0, 0), 16) for y in (-3.45, -2, 0, 2, 3.45) for z in (0.05, 1.0, 2.0))
crown = not ray_hits(objs, (-8, 0, 2.9), (1, 0, 0), 16)
wall = ray_hits(objs, (-8, 3.7, 1.0), (1, 0, 0), 16) and ray_hits(objs, (-8, -3.7, 1.0), (1, 0, 0), 16)
roof = ray_hits(objs, (-8, 0, 3.2), (1, 0, 0), 16)
check("H3 tunnel opening 7 wide x 3 high clear", inside and crown, "(rays at |z|<=3.45, y<=2.0, crown y=2.9)")
check("H3 tunnel side walls at |z|=3.7 and roof above 3.1", wall and roof)
stem = [o for o in objs if o.name.endswith("__Cream")]
xs = [(o.matrix_world @ v.co).x for o in stem for v in o.data.vertices if (o.matrix_world @ v.co).z < 2.9]
check("H3 tunnel depth 5 (stem |x|<=2.5 below y 2.9)", max(abs(x) for x in xs) <= 2.51, f"max |x| {max(abs(x) for x in xs):.2f}")

# 2. torii posts outside rails (rail outer face |x|=4.0) at ball/rail height
objs = build("lantern_torii_gate")
xs = [abs((o.matrix_world @ v.co).x) for o in objs for v in o.data.vertices if (o.matrix_world @ v.co).z < 2.0]
check("H1 torii posts outside rails", min(xs) >= 4.0, f"min |x| below y2 = {min(xs):.3f}")

# 3. root bridge: nothing above the felt surface; deck width
objs = build("root_bridge_arched")
worst = -9
for o in objs:
    for v in o.data.vertices:
        w = o.matrix_world @ v.co
        zr = -w.y + (-21.5)  # roblox z
        felt = 0.4 - 0.4 * abs(max(min(zr, -15), -28) + 21.5) / 6.5
        worst = max(worst, (w.z - 2.6) - felt)
check("H5 root bridge never rises above the felt (no rails)", worst <= 0.0, f"max height over felt {worst:.3f}")
deck = [o for o in objs if o.name.endswith("__RootBark")][0]
mn, mx = rb([deck])
check("H5 root bridge deck >= 2.2 wide", (mx.x - mn.x) >= 2.2, f"{mx.x - mn.x:.2f}")

# 4. covered bridge interior clear between posts (rails outer face at +-3.0 from centre) up to 3.2
objs = build("covered_bridge")
clear = True
for o in objs:
    for v in o.data.vertices:
        w = o.matrix_world @ v.co
        if 1.4 + 0.05 < w.z < 1.4 + 3.2 and abs(w.x) < 3.0 and abs(w.y) < 6.6 and "Glow" not in o.name and "Paper" not in o.name \
                and "Iron" not in o.name and "RootBark" not in o.name:
            clear = False
check("H5 covered bridge interior clear |x|<3.0 (felt 5 + rails) up to 3.2 above felt", clear)

# 5. moving parts vs blockers
def within(objs, lo, hi, tol=0.05, skip=()):
    mn, mx = rb([o for o in objs if not any(s in o.name for s in skip)])
    return all(mn[i] >= lo[i] - tol and mx[i] <= hi[i] + tol for i in range(3)), (mn, mx)

import dressing_lib as _DL0
_MP0 = {(h["number"], m["id"]): m for h in _DL0.load_holes() for m in h["moving_parts"]}


def in_blockers(objs, mp, tol=0.05):
    """pass 8 (Round 7): every vertex (Blender, pivot frame) inside the UNION of the holes.json blockers (yawed boxes,
    Roblox centre/size/yaw relative to the pivot). Returns (ok, n_outside)."""
    out = 0
    for o in objs:
        for v in o.data.vertices:
            w = o.matrix_world @ v.co
            p_ = np.array([w.x, w.z, -w.y])                    # Roblox, pivot frame
            inside = False
            for bl in mp["blockers"]:
                L = (p_ - np.array(bl["center"], float)) @ _DL0.yaw_mat(bl.get("yaw", 0.0))
                if np.all(np.abs(L) <= np.array(bl["size"], float) / 2 + tol):
                    inside = True
                    break
            out += not inside
    return out == 0, out


import numpy as np
objs = build("h7_floating_log")
_m = _MP0[(7, "log")]
ok, nout = in_blockers(objs, _m, tol=0.1)
mn_, mx_ = rb(objs)
check(f"H7 log inside its holes.json blockers ({' + '.join('x'.join(f'{v:g}' for v in b_['size']) for b_ in _m['blockers'])}"
      f"; pointed ends)", ok, f"{nout} verts outside; x {mn_.x:.2f}..{mx_.x:.2f}")
objs = build("h9_root_portcullis")
ok, b = within(objs, (-0.4, -3.7, -0.3), (0.4, 3.7, 1.1), tol=0.1)
check("H9 portcullis within blocker 0.8x1.4x7.4", ok, f"{tuple(round(x, 2) for x in b[0])}..{tuple(round(x, 2) for x in b[1])}")
objs = build("h8_root_door")
_m = _MP0[(8, "root_door")]
ok, nout = in_blockers(objs, _m, tol=0.1)
mn_, mx_ = rb(objs)
check(f"H8 root door inside its holes.json blocker {'x'.join(f'{v:g}' for v in _m['blockers'][0]['size'])}", ok,
      f"{nout} verts outside; z {-mx_.y:.2f}..{-mn_.y:.2f}")
objs = build("h4_carousel_bar")
low = [(o.matrix_world @ v.co) for o in objs for v in o.data.vertices if (o.matrix_world @ v.co).z < 1.0]
check("H4 carousel (pass 6, padded 2.3 arms): below y=1 everything inside the arm blockers (|x|<=3.0, |z|<=0.35)",
      all(abs(p.x) <= 3.03 and abs(p.y) <= 0.36 for p in low),
      f"max |x| {max(abs(p.x) for p in low):.3f}, max |z| {max(abs(p.y) for p in low):.3f}")
objs = build("h9_lantern_pendulum")
_m = _MP0[(9, "lantern_pendulum")]
_bl = _m["blockers"][0]
_top = _bl["center"][1] + _bl["size"][1] / 2
bob = [(o.matrix_world @ v.co) for o in objs for v in o.data.vertices if (o.matrix_world @ v.co).z < _top + 1e-4]
chain = [(o.matrix_world @ v.co) for o in objs for v in o.data.vertices if _top + 1e-4 <= (o.matrix_world @ v.co).z < -0.3]
_BL = [(np.array([p.x, p.z, -p.y]) - np.array(_bl["center"], float)) @ _DL0.yaw_mat(_bl.get("yaw", 0.0)) for p in bob]
# pass 9 (Round 9): blocker 2 = collider foot; the base plinth fills it, so the bob test is against the UNION
_in_u = [any(np.all(np.abs((np.array([p.x, p.z, -p.y]) - np.array(b_["center"], float)) @ _DL0.yaw_mat(b_.get("yaw", 0.0)))
                    <= np.array(b_["size"]) / 2 + 1e-3) for b_ in _m["blockers"]) for p in bob]
check(f"H9 pendulum bob inside its holes.json blockers ({' + '.join('x'.join(f'{v:g}' for v in b_['size']) + ' yaw ' + format(b_.get('yaw', 0), 'g') for b_ in _m['blockers'])}), "
      f"body centred {-_bl['center'][1]:g} below the hinge", all(_in_u),
      f"{len(_in_u) - sum(_in_u)} verts outside; body max |x| {max(abs(q[0]) for q in _BL):.3f}, "
      f"bottom {min(p.z for p in bob):.3f}")
check("H9 pendulum chain slim (|x|, |z| <= 0.2 between hinge and bob)",
      all(abs(p.x) <= 0.2 and abs(p.y) <= 0.2 for p in chain), f"{len(chain)} verts")
objs = build("h6_mill_wheel")
# anything sweeping within 3.6 of the axle inside the felt width |z|<3.5 must be a paddle board (blocker radial 2.2..3.6)
bad = 0
for o in objs:
    for v in o.data.vertices:
        w = o.matrix_world @ v.co
        r = math.hypot(w.x, w.z)
        if abs(w.y) < 3.5 and r > 2.15 and not (abs(w.x) <= 0.31 and 2.15 <= abs(w.z) <= 3.62):
            bad += 1
check("H6 wheel: only the 2 paddle boards reach r>2.15 over the felt", bad == 0, f"{bad} stray verts")
check("H6 wheel radius <= 3.6", all(math.hypot((o.matrix_world @ v.co).x, (o.matrix_world @ v.co).z) <= 3.61
                                    for o in objs for v in o.data.vertices))
mn, mx = rb(objs)
check("H6 axle reaches the mill wall (course z=-1 -> local +7.5 = Blender y -7.5)", mn.y <= -7.5, f"axle end y={mn.y:.2f}")

# 6. hollow tree: H9 rails inside cavity at felt height (rays from cavity centre outward)
objs = build("hollow_tree")
trunk = [o for o in objs if "trunk" in o.name]
ok = True
for (x, z) in ((13.5, -17.5), (32.5, -17.5), (13.5, -54.5), (32.5, -54.5), (13.5, -40), (32.5, -36)):
    p = Vector((x - 23.0, -(z + 36.0), 2.0 + 0.5))
    if ray_hits(trunk, (0, 0, 2.5), p - Vector((0, 0, 2.5)), (p - Vector((0, 0, 2.5))).length):
        ok = False
check("H9 chamber/heart rail corners inside the trunk cavity", ok)
tun = not ray_hits(trunk, (-25, -10.5, 2.0 + 1.0), (1, 0, 0), 25) and not ray_hits(trunk, (-25, -7.0, 2.0 + 3.5), (1, 0, 0), 25)
check("H9 corridor tunnel through the trunk wall is open (felt+1, felt+3.5)", tun)

# ============================================================================ pass 4: world dressing
# Every dressing FBX group is RE-IMPORTED (what Studio gets), moved from the hole frame to the world with the
# world.json placement and tested triangle by triangle (exact SAT) against every keep-out (world_fit.dressing_keepouts:
# all holes' felt/walls/hazards/sweeps/teleports/tee pads/heroes, walkways + stairs + landings, lantern posts, plazas,
# flume), against the world FBX occupancy (world_occ: tree shell/roots/interior, falls, cliff kits, rock faces, ...)
# and the hollow-tree rule. Per instance: local <-> world consistency, terrain grounding (spread, water, base y),
# and the Quest near-field budget per hole. Negative tests must be flagged.
import json
import numpy as np
import dressing_lib as DL
import world_fit as WF
import world_occ

OUTD = os.path.dirname(SRC)
man = json.load(open(os.path.join(OUTD, "manifest.json")))
PT = {p["name"]: p["triangles"] for p in man["props"]}
W = WF.load_world()
HW = WF.holes_world(W)
HM = {h["number"]: h for h in HW}
KO = WF.dressing_keepouts(W, HW)
OCC = world_occ.build_or_load()
TER = WF.Terrain()
TREE = W["hollow_tree"]
TO = np.array(TREE["center"], float)
R_IN, R_OUT = TREE["trunk_inner_radius"], TREE["trunk_outer_radius"]
dress = man.get("dressing", {})
DH = dress.get("holes", {})
BUD = dress.get("budgets", {})
NEAR_D, NEAR_BUDGET = BUD.get("near_field_radius_studs", 60.0), BUD.get("near_field_tri_budget", 34000)


def fbx_tris(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y")
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    T = []
    for o in new:
        if o.type != "MESH":
            continue
        me = o.data
        me.calc_loop_triangles()
        mw = np.array(o.matrix_world)
        V = np.array([v.co[:] for v in me.vertices], float) @ mw[:3, :3].T + mw[:3, 3]
        idx = np.array([t.vertices[:] for t in me.loop_triangles], int)
        if len(idx):
            T.append(V[idx])
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    T = np.concatenate(T) if T else np.zeros((0, 3, 3))
    return np.stack([T[..., 0], T[..., 2], -T[..., 1]], axis=-1)


def to_world_tris(h, T):
    return DL.to_world(h, T.reshape(-1, 3)).reshape(-1, 3, 3)


def tree_rule(n, P):
    r = np.hypot(P[:, 0] - TO[0], P[:, 2] - TO[2])
    if n == 9:
        return int((r > R_IN - 0.3 + 1e-3).sum())
    return int((r < R_OUT + 1.0 - 1e-3).sum())


def felt_dist_world(n, x, z):
    Rw, off = DL.hole_xf(HM[n])
    L = (np.array([x, 0, z]) - off) @ Rw
    return float(DL.felt_distance(HM[n], np.array([L[0]]), np.array([L[2]]))[0])


def water_at(xs, zs):
    i = np.clip(np.floor((np.asarray(xs) - TER.x0) / TER.cell).astype(int), 0, TER.cols - 1)
    j = np.clip(np.floor((np.asarray(zs) - TER.z0) / TER.cell).astype(int), 0, TER.rows - 1)
    w, hh = TER.W[j, i], TER.H[j, i]
    return bool(np.any(~np.isnan(w) & (w > hh + 0.05)))


def ground_check(it):
    """Re-sample the stored footprint ([x, z, r] per base: centre + 8 points at r/2 and r) on terrain-4stud: spread
    limit, water, base y (= min + 0.3 * spread - sink) and terrain_y. Returns a problem string or ''."""
    x, y, z = it["world_pos"]
    if it.get("hanging"):         # pass 8: H9 hanging lanterns are not grounded (height checked in fitcheck_pass8)
        ty = float(TER.height(np.array([x]), np.array([z]))[0])
        return "" if abs(it["terrain_y"] - ty) <= 0.01 and y > ty + 5.0 else "hanging lantern below 5 / terrain_y"
    card = it["prop"].startswith("treeline_card")
    big = it["role"] in ("tree", "far") or card or "tree" in it["prop"]
    xs, zs = [], []
    for (cx, cz, r) in it.get("footprint", [[x, z, 0.6]]):
        xs.append(cx)
        zs.append(cz)
        for k in range(8):
            for f_ in (0.5, 1.0):
                xs.append(cx + math.cos(k * math.tau / 8) * r * f_)
                zs.append(cz + math.sin(k * math.tau / 8) * r * f_)
    if water_at(xs, zs):
        return "water"
    hs = TER.height(np.array(xs), np.array(zs))
    lim = 3.5 if card else 3.0 if big else 1.5
    if hs.max() - hs.min() > lim + 1e-3:
        return f"spread {hs.max() - hs.min():.2f}"
    if not (hs.min() - 0.31 <= y <= hs.min() + 0.3 * (hs.max() - hs.min()) + 0.01):
        return f"base y {y:.2f} vs terrain {hs.min():.2f}..{hs.max():.2f}"
    if abs(it["terrain_y"] - float(TER.height(np.array([x]), np.array([z]))[0])) > 0.01:
        return "terrain_y mismatch"
    return ""


def kind_of(label):
    if label.startswith("path:"):
        return "walkway"
    if label.startswith("world:"):
        return label.split(":")[1].split("_part")[0].split("#")[0]
    if label.startswith(("lantern_post", "poi:", "mill_flume", "sweep:")):
        return label.split(":")[0]
    p = label.split(":")
    return f"{p[0]}:{p[1]}" if len(p) > 1 else label


# pass 8: the hero heart_lantern_cluster's keep-out box covers the whole H9 heart; a hanging lantern may enter it
# if its mesh stays >= 0.6 from the cluster's mesh (vertices, edge midpoints and centroids of both, re-imported FBX)
CL_LBL, CL_GAPS, _CLP = "H9:hero:heart_lantern_cluster", [], []


def _tri_pts(Tw):
    return np.concatenate([Tw.reshape(-1, 3), Tw.mean(1), (Tw + np.roll(Tw, -1, axis=1)).reshape(-1, 3) / 2])


def cluster_mesh_gap(Tw):
    if not _CLP:
        pl = [p for p in man["props"] if p["name"] == "heart_lantern_cluster"][0]["placements"][0]
        Tc = fbx_tris(os.path.join(OUTD, "fbx", "heart_lantern_cluster.fbx"))
        Tl = Tc @ DL.yaw_mat(pl.get("yaw", 0)).T + np.asarray(pl["pos"], float)
        _CLP.append(_tri_pts(to_world_tris(HM[9], Tl)))
    C, P = _CLP[0], _tri_pts(Tw)
    d = np.full(len(P), 1e9)
    for i in range(0, len(C), 4000):
        d = np.minimum(d, np.linalg.norm(P[:, None] - C[None, i:i + 4000], axis=2).min(1))
    return float(d.min()) if len(P) else 1e9


check("pass-4 world dressing present for all 9 holes (world_pos/world_yaw/terrain_y on every instance)",
      len(DH) == 9 and all("world_pos" in it and "terrain_y" in it for d in DH.values() for it in d["instances"]),
      f"{sum(len(d['instances']) for d in DH.values())} instances")
lines.append(f"  keep-out boxes: {len(KO)}; world occupancy grids: {len(OCC.g)}")
allw = []
for n in range(1, 10):
    H = f"H{n}"
    h = HM[n]
    d = DH.get(H, {})
    insts = d.get("instances", [])
    # 1. exact triangle test of the re-imported groups
    hits, occ_hits, tree_bad, ntri = {}, {}, 0, 0
    min_gap, min_over = 1e9, 1e9
    ok_files = True
    for f in d.get("fbx", []):
        p = os.path.join(OUTD, f["fbx"])
        if not os.path.exists(p):
            ok_files = False
            continue
        T = to_world_tris(h, fbx_tris(p))
        ntri += len(T)
        ok_files &= len(T) < 20000 and len(T) == f["triangles"]
        for k, v in WF.check_tris(T, KO).items():
            if k == CL_LBL:       # pass 8: H9 hanging lantern inside the heart cluster's box: test the real meshes
                box = [b for b in KO if b.label == k][0]
                g = cluster_mesh_gap(T[WF.tris_hit_obb(T, box)])
                CL_GAPS.append(round(g, 3))
                if g >= 0.6 - 1e-3:
                    continue
            hits[kind_of(k)] = hits.get(kind_of(k), 0) + v
        P = np.concatenate([T.reshape(-1, 3), T.mean(1)])
        for k, v in OCC.hits(P).items():
            occ_hits[kind_of(k)] = occ_hits.get(kind_of(k), 0) + v
        tree_bad += tree_rule(n, P)
        for h2 in HW:
            Rw, off = DL.hole_xf(h2)
            L = (P - off) @ Rw
            for r in DL.felt_rects(h2):
                dd = DL.rect_dist(L[:, 0], L[:, 2], r)
                if dd.min() > 30:
                    continue
                low = L[:, 1] < r[5] + DL.CLEAR
                if low.any():
                    min_gap = min(min_gap, float(dd[low].min()))
                over = dd <= 0
                if over.any():
                    min_over = min(min_over, float((L[over, 1] - r[5]).min()))
    check(f"{H} dressing FBX groups re-imported: {len(d.get('fbx', []))} files, {ntri} tris, each < 20k, counts match",
          ok_files and ntri == d.get("triangles", -1), f"manifest {d.get('triangles')}")
    check(f"{H} no dressing triangle inside any keep-out (holes, walkways/stairs/landings, posts, plazas, flume)",
          not hits, str(hits) if hits else f"exact SAT vs {len(KO)} boxes")
    check(f"{H} no dressing geometry inside world pieces (tree shell/roots, falls, cliff kits, rock faces, ...)",
          not occ_hits, str(occ_hits) if occ_hits else "occupancy clear")
    check(f"{H} hollow-tree rule ({'inside the hollow, r < inner - 0.3' if n == 9 else 'outside trunk r + 1'})",
          tree_bad == 0, f"{tree_bad} verts")
    check(f"{H} low geometry >= {DL.FELT_MARGIN} from every felt edge (all holes, world placement)",
          min_gap >= DL.FELT_MARGIN - 1e-3, f"min gap {min_gap:.2f}")
    check(f"{H} anything over felt is >= {DL.CLEAR} above it", min_over >= DL.CLEAR - 1e-3,
          "nothing overhangs felt" if min_over > 1e8 else f"min height over felt {min_over:.2f}")
    # 2. per-instance consistency + grounding
    bad_xf, bad_ground = [], []
    for it in insts:
        pw = DL.to_world(h, it["pos"])
        if np.abs(pw - np.array(it["world_pos"])).max() > 0.01 or \
                abs(((it["yaw"] + h["world_yaw"]) - it["world_yaw"] + 180) % 360 - 180) > 0.11:
            bad_xf.append(it["prop"])
        g = ground_check(it)
        if g:
            bad_ground.append(f"{it['prop']}: {g}")
        allw.append((n, it))
    check(f"{H} hole-local pos/yaw == world_pos/world_yaw via world.json placement", not bad_xf, ", ".join(bad_xf[:4]))
    check(f"{H} every instance grounded on terrain-4stud (spread <= 1.5 small / 3 trees / 3.5 cards, no water)",
          not bad_ground, "; ".join(bad_ground[:4]) if bad_ground else f"{len(insts)} instances")
    lw = d.get("lights_world", [])
    check(f"{H} lights[] and lights_world[] match", len(lw) == len(d.get("lights", [])), f"{len(lw)} lights")

# cards read flat up close: none within 26 studs of any felt
close = [f"{m}:{it['prop']}" for m, it in allw if it["prop"].startswith("treeline_card") and
         min(felt_dist_world(k, it["world_pos"][0], it["world_pos"][2]) for k in range(1, 10)) < 32.0 - 1e-3]
check("card clumps >= 32 studs from every hole's felt", not close, ", ".join(close[:5]) if close else
      f"{sum(1 for m, it in allw if it['prop'].startswith('treeline_card'))} cards")

import importlib.util as _ilu
SL = [((190.0, 170.0), 302, 32, 260), ((166.0, -80.0), 293, 45, 260), ((22.0, -10.0), 326, 32, 120)]


def in_sl(x, z):
    for (ex, ez), brg, half, length in SL:
        L = math.hypot(x - ex, z - ez)
        if 1 <= L <= length and abs((math.degrees(math.atan2(x - ex, -(z - ez))) % 360 - brg + 180) % 360 - 180) < half:
            return True
    return False


blk = [f"{m}:{it['prop']}" for m, it in allw if it["prop"].startswith("treeline_card") and in_sl(it["world_pos"][0], it["world_pos"][2])]
check("no card clumps in the protected vista sightlines (H1 tee -> tree, Lookout Rock, Root Stair)", not blk, ", ".join(blk[:5]))
check("negative test flagged: card in the H1 tee -> tree sightline", in_sl(122.2, 127.6))

# 3. Quest budget: tris of all dressing within NEAR_D of each hole's felt
for n in range(1, 10):
    tot = sum(PT[it["prop"]] for m, it in allw if felt_dist_world(n, it["world_pos"][0], it["world_pos"][2]) < NEAR_D)
    st = DH[f"H{n}"]["stats"]
    check(f"H{n} near-field dressing tris (any hole, within {NEAR_D:g} studs of felt) <= {NEAR_BUDGET}",
          tot <= NEAR_BUDGET and tot == st["near_field_tris_after"], f"{tot} (before pass 4: {st['near_field_tris_before']})")

# 4. negative tests: the checker must flag these
def box_tris(c, s=0.5):
    c = np.asarray(c, float)
    return np.array([[c + [-s, 0, -s], c + [s, 0, -s], c + [0, s, s]], [c + [-s, s, s], c + [s, s, s], c + [0, 0, -s]]])


h1, h6 = HM[1], HM[6]
lane = h1["felt"][0]
neg = {}
neg["box on H1 felt"] = bool(WF.check_tris(box_tris(DL.to_world(h1, [lane["center"][0], lane["center"][1] + 0.3,
                                                                     lane["center"][2]])), KO))
mw = [m for m in h6["moving_parts"] if m["type"] == "rotate"][0]
neg["box in the H6 mill-wheel sweep"] = bool(WF.check_tris(box_tris(DL.to_world(h6, np.array(mw["pivot"]) + [0, 2.5, 0]), 0.3), KO))
st_seg = [s for p in W["paths"] for s in p["segments"] if s["type"] == "stairs"][0]
mid = (np.array(st_seg["start"]) + np.array(st_seg["end"])) / 2
neg["box on a stair flight"] = bool(WF.check_tris(box_tris(mid + [0, 1.0, 0]), KO))
lp = np.array(W["lanterns"]["points"][5]["pos"]) + [0, 2.0, 0]
neg["box at a lantern post"] = bool(WF.check_tris(box_tris(lp, 0.3), KO))
wall_p = TO + [R_IN + 3.5, 6.0, 0]
neg["point in the trunk wall (occupancy)"] = bool(OCC.hits(np.array([wall_p])))
neg["point in the trunk wall (tree rule)"] = tree_rule(3, np.array([wall_p])) > 0
neg["instance in Lantern Mere"] = ground_check(dict(world_pos=[14.0, 8.0, 146.0], role="near", prop="fern_clump",
                                                    scale=1.0, terrain_y=0.0)) == "water"
cliff = None
for j in range(TER.rows - 1):
    for i in range(TER.cols - 1):
        if abs(TER.H[j, i + 1] - TER.H[j, i]) > 6 and np.isnan(TER.W[j, i]):
            cliff = (TER.x0 + (i + 1) * TER.cell, TER.z0 + (j + 0.5) * TER.cell)
            break
    if cliff:
        break
neg["tree on a cliff edge (spread)"] = ground_check(dict(world_pos=[cliff[0], 0.0, cliff[1]], role="tree",
                                                     prop="maple_tree_round", scale=1.0, terrain_y=0.0,
                                                     footprint=[[cliff[0], cliff[1], 1.5]])).startswith("spread")
for k, v in neg.items():
    check(f"negative test flagged: {k}", v)

# ============================================================================ pass 5: playtest review
# a) tall props (> 2 studs) keep all geometry below base + 5 (and so the footprint) >= 3 studs from every collision
#    wall of every hole. Prop geometry is rebuilt from the generators (independent of dressing_world's templates).
TALL_H, RAIL_BACK, EYE_BAND = 2.0, 3.0, 5.0
_rl = []
for _h in HW:
    for _w in _h["walls"]:
        _c = DL.to_world(_h, _w["center"])
        _a = math.radians(_w.get("yaw", 0) + _h["world_yaw"])
        _rl.append((_c[0], _c[2], math.cos(_a), math.sin(_a), _w["size"][0] / 2, _w["size"][2] / 2))
RAILS2D = np.array(_rl)


def rail_dist(X, Z):
    X, Z = np.atleast_1d(np.asarray(X, float)), np.atleast_1d(np.asarray(Z, float))
    best = np.full(len(X), 1e9)
    for (cx, cz, c, s_, hx, hz) in RAILS2D:            # point -> rectangle, one wall at a time (no shared code)
        dx, dz = X - cx, Z - cz
        lx, lz = c * dx - s_ * dz, s_ * dx + c * dz
        best = np.minimum(best, np.hypot(np.maximum(np.abs(lx) - hx, 0), np.maximum(np.abs(lz) - hz, 0)))
    return best


_geo = {}


def prop_verts(name):
    if name not in _geo:
        objs = build(name)
        V = np.array([(o.matrix_world @ v.co)[:] for o in objs if o.type == "MESH" for v in o.data.vertices], float)
        _geo[name] = np.stack([V[:, 0], V[:, 2], -V[:, 1]], 1)
        for o in objs:
            bpy.data.objects.remove(o, do_unlink=True)
    return _geo[name]


def tall_rail_problem(it):
    v = prop_verts(it["prop"]) * it["scale"]
    if v[:, 1].max() <= TALL_H:
        return None
    P = v @ DL.yaw_mat(it["world_yaw"]).T + np.array(it["world_pos"], float)
    base = it["terrain_y"] if it.get("hanging") else it["world_pos"][1]      # pass 8: hanging -> the ground
    low = P[P[:, 1] < base + EYE_BAND]
    d = float(rail_dist(low[:, 0], low[:, 2]).min()) if len(low) else 1e9
    return d if d < RAIL_BACK - 1e-3 else None


n_tall = 0
for n in range(1, 10):
    bad = []
    for it in DH[f"H{n}"]["instances"]:
        if it["prop"].startswith("treeline_card"):
            continue
        d_ = tall_rail_problem(it)
        if prop_verts(it["prop"])[:, 1].max() * it["scale"] > TALL_H:
            n_tall += 1
        if d_ is not None:
            bad.append(f"{it['prop']} {d_:.2f}")
    check(f"H{n} every tall dressing prop (> {TALL_H:g} high) >= {RAIL_BACK:g} studs from all rails "
          f"(footprint + geometry below base + {EYE_BAND:g})", not bad, "; ".join(bad[:4]) if bad else "")
lines.append(f"  tall dressing props checked: {n_tall}")
_h3 = HM[3]
_w = [w for w in _h3["walls"] if w["id"].startswith("rail")][0]
_c = DL.to_world(_h3, _w["center"])
_out = DL.yaw_mat(_w.get("yaw", 0) + _h3["world_yaw"]) @ np.array([1.0, 0, 0])
neg_t = dict(prop="maple_tree_round", scale=1.0, world_yaw=0.0,
             world_pos=[float(_c[0] + _out[0] * 2.0), float(_c[1]), float(_c[2] + _out[2] * 2.0)])
neg_l = dict(neg_t, prop="lantern_hook_pair")
neg_s = dict(neg_t, prop="cup_lantern_stake")
check("negative test flagged: tall tree 2 studs outside an H3 rail", tall_rail_problem(neg_t) is not None)
check("negative test flagged: lantern hook pair 2 studs outside an H3 rail", tall_rail_problem(neg_l) is not None)
check("short prop (cup_lantern_stake, 1.92 tall) at the same spot is allowed", tall_rail_problem(neg_s) is None)

# b) dark holes: cup / gate lanterns, light spots over every moving part + cup, clear of keep-outs
for n in (8, 9):
    need = tuple(m["id"] for m in HM[n]["moving_parts"]) + ("cup",)      # every moving part + the cup
    d = DH[f"H{n}"]
    sp = d.get("spot_lights", [])
    over = {q["over"] for q in sp}
    bad = []
    for q in sp:
        pw = DL.to_world(HM[n], q["pos"])
        if np.abs(pw - np.array(q["world_pos"])).max() > 0.02:
            bad.append(f"{q['id']} local/world")
        if not WF.points_clear(np.array([q["world_pos"]]), KO)[0] or OCC.hits(np.array([q["world_pos"]])):
            bad.append(f"{q['id']} in keep-out/world piece")
        if not all(k in q for k in ("color", "range", "brightness")):
            bad.append(f"{q['id']} fields")
        if q["over"] == "cup":
            tgt = HM[n]["cup"]["position"]
        elif q["over"].startswith("firefly_swarm:"):        # pass 7: glow over an H8 firefly swarm instance
            tgt = q.get("target_pos")
            if tgt is None or not any(it["prop"] == "firefly_swarm" and it["pos"] == tgt for it in d["instances"]):
                bad.append(f"{q['id']}: no firefly_swarm instance at its target")
                continue
        elif q["over"].startswith("felt:"):
            f_ = [f for f in HM[n]["felt"] if f["id"] == q["over"][5:]][0]
            tgt = [f_["center"][0], DL.felt_top(f_), f_["center"][2]]
        else:
            tgt = ([m["pivot"] for m in HM[n]["moving_parts"] if m["id"] == q["over"]] or [None])[0]
        if tgt is None:
            bad.append(f"{q['id']}: target '{q['over']}' no longer in holes.json")
            continue
        dist = float(np.linalg.norm(np.array(q["pos"]) - np.array(tgt)))
        if dist > 0.7 * q["range"]:
            bad.append(f"{q['id']} too far ({dist:.1f})")
    check(f"H{n} spot_lights pool over {', '.join(need)} (local == world, clear of keep-outs + world pieces, "
          "within 0.7 x range)", set(need) <= over and not bad, "; ".join(bad) if bad else f"{len(sp)} spots")
    acc = [it for it in d["instances"] if it["role"] == "accent"]
    marks = {}
    for it in acc:
        marks[it["marks"]] = marks.get(it["marks"], 0) + 1
    want = ("cup",) + (("root_gate",) if n == 9 and any(m["id"] == "root_gate" for m in HM[9]["moving_parts"]) else ())
    check(f"H{n} glowing cup_lantern_stake at {' + '.join(want)} (within 9 studs; pass 6: was 7)",
          all(marks.get(w, 0) >= 1 for w in want) and all(it["dist_to_target"] <= 9 for it in acc),
          f"{marks}, max dist {max([it['dist_to_target'] for it in acc] or [0])}")
neg_spot = DL.to_world(HM[8], np.array(HM[8]["moving_parts"][0]["pivot"]) + [0, 2.0, 0])
check("negative test flagged: a light host 2 studs above the H8 moving part (inside the play clearance)",
      bool(WF.check_tris(box_tris(neg_spot, 0.1), KO)))

# c) moving parts carry the cream-red signal scheme; rail / felt variants exist
mv = {p["name"]: {q["material"] for q in p["parts"]} for p in man["props"]}
need_mv = ["h4_carousel_bar", "h6_mill_wheel", "h7_floating_log", "h8_root_door", "h9_root_portcullis",
           "h9_lantern_pendulum"]
check("moving parts use MoveRed + MoveCream (H4 arms, H6 paddles, H7 log, H8 door, H9 gate + pendulum)",
      all({"MoveRed", "MoveCream"} <= mv.get(n, set()) for n in need_mv),
      ", ".join(n for n in need_mv if not {"MoveRed", "MoveCream"} <= mv.get(n, set())))
sk = man.get("hole_skins", {}).get("holes", {})
okv = sk.get("H6", {}).get("rail_cap") == "MillBlue" and sk.get("H8", {}).get("felt_material") == "FeltBright" and \
    sk.get("H9", {}).get("rail_cap") == "TrimCream" and \
    all(os.path.exists(os.path.join(OUTD, "fbx", f"{s_[k]}.fbx")) for s_ in sk.values()
        for k in ("rail_straight_4", "rail_straight_2", "rail_end_post")) and \
    os.path.exists(os.path.join(OUTD, "textures", "felt_bright.png"))
check("hole skins: H6 mill rail variant, H8/H9 bright felt + cream trim rails (FBX + texture present)", okv)

exec(open(os.path.join(SRC, "fitcheck_pass6.py")).read())
exec(open(os.path.join(SRC, "fitcheck_pass7.py")).read())
exec(open(os.path.join(SRC, "fitcheck_pass7b.py")).read())
exec(open(os.path.join(SRC, "fitcheck_pass8.py")).read())
exec(open(os.path.join(SRC, "fitcheck_pass9.py")).read())
exec(open(os.path.join(SRC, "fitcheck_pass10.py")).read())

big = [p["name"] for p in man["props"] if p["triangles"] >= 20000]
check("every prop FBX < 20k tris", not big, f"max {max(p['triangles'] for p in man['props'])}")

nf = sum(1 for l in lines if l.startswith("FAIL"))
lines.append("")
lines.append("ALL PASS" if nf == 0 else f"{nf} FAIL(S)")
out = "\n".join(lines)
print(out)
open(os.path.join(SRC, "fitcheck.txt"), "w").write(out + "\n")
