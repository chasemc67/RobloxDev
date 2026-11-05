"""Pass 4: re-validate and re-place the per-hole set dressing in the REAL world layout, under a Quest tri budget.

  blender -b --factory-startup -P models/_src/dressing_world.py

Input: _src/dressing_seed_pass2.json (the pass-2 hole-local layouts, frozen), ../world/world.json (hole origin + yaw;
holes.json world_offset/world_yaw are ignored), ../world/terrain-4stud.json, models/world layout + FBX.

1. Every seed instance is moved to world space with the world README formula (world_fit.holes_world).
2. Clash test (every prop vertex, world space) against:
     - every hole: felt +1.25 up to felt top +6.5, collision walls, hazards, moving-part sweeps, teleports, tee pad +
       run-up, hero props (world_fit.hole_obbs);
     - every walkway / stair / landing segment: width/2 + 0.75, 6.5 high (12 at the Heartwood Door) and the 54 lantern
       posts (world_fit.path_obbs / lantern_obbs); plazas / viewpoints (POI radius) and the mill flume;
     - the world FBX geometry: tree shell, roots, interior, waterfalls, cliff kits, terrace rock faces, tower, dock,
       sister trees, tree line (world_occ: per-part height intervals on a 1-stud grid);
     - the hollow tree: non-H9 dressing may not come within the trunk's outer radius + 1; H9 dressing must stay
       inside the hollow (r < inner radius - 0.3).
3. Ground: terrain heights (bilinear, terrain-4stud.json) sampled over the footprint. Rejected if the footprint
   spans > 1.5 studs (small props, lantern poles) / > 3 (trees) / > 3.5 (cards), or touches a water cell.
   Base y = min + 0.3 * spread - sink (trees sink 0.25, small 0.05).
4. A clashing / badly grounded instance is NUDGED to the nearest valid spot (rings of 12 directions, same prop,
   same yaw, same role) within a per-role radius; otherwise removed with a reason.
5. Quest budget: NEAR_D = 60 studs. For every hole, the tris of ALL dressing (any hole) within 60 studs of its felt
   must stay <= NEAR_BUDGET. Lanterns and framing trees are placed first (round-robin over holes, tee-view first),
   then ground cover. Every pass-2 backdrop clump (tree_backdrop_cluster, 834 tris) becomes a card clump
   (treeline_card_*, 12 tris); cards are also used for any refill beyond CARD_MIN_D.
6. Pass 5 (playtest review): every TALL prop (> TALL_H = 2 studs high) keeps its footprint AND all its geometry below
   eye height (base + 5) >= RAIL_BACK = 3 studs (horizontal) from every rail / collision wall of every hole
   ("tall_near_rail"); nudged back or removed. Cup / gate lanterns (cup_lantern_stake, 1.95 tall, role 'accent') are
   placed first beside the H8 + H9 cups and the H9 root gate, and light spots (spot_lights[]: PointLight pos, colour,
   range, brightness) pool over the H8 door, H9 gate, H9 lantern bar and the H8/H9 cups.
7. Pass 7b (playtest: tall grass clipped the H1 rails): every PLANT instance (registry.category == 'plant': grass,
   ferns, bushes, mushroom clumps, glow shrooms / roots, saplings) keeps its WHOLE mesh footprint (exact 2D distance of
   every projected triangle to every wall rectangle) >= PLANT_RAIL_CLEAR = 1.5 studs from every rail / collision wall
   of every hole ("plant_near_rail"); nudged OUTWARD (away from the nearest wall, same role, up to 3.5) or removed.
8. Refill: cards in each tee view's far field, framing trees / ground cover where removals left gaps (budget
   permitting), glowing mushrooms + ferns along the inside of the trunk for H9.
Writes manifest.json > dressing (world + local transforms, stats, budgets, lights) and fbx/dressing_hNN_*.fbx.
"""
import bpy, bmesh, sys, os, json, math, random, importlib, time
import numpy as np
from mathutils import Vector, Matrix

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import lglib, registry, dressing_lib as DL, world_fit as WF, world_occ
for m in ("props_dressing", "props_moving", "props_hero", "props_p2p3", "props_variants", "props_cards", "props_pass6", "props_pass7", "props_pass8"):
    importlib.import_module(m)
REG = {p["name"]: p for p in registry.PROPS}
T0 = time.time()

# ----------------------------------------------------------------------------- knobs
NEAR_D = 60.0             # near field = within this many studs of a hole's felt
NEAR_BUDGET = 34000       # max dressing tris (all holes' dressing) inside any hole's near field
CARD_ANY_D = 32.0         # no card closer than this to ANY hole's felt (cards read flat up close)
# protected sightlines (world/README vista cameras): no card clumps inside these cones, so the signature views
# (H1 tee -> mere + giant tree, Lookout Rock -> valley, Root Stair -> tree) stay open: (eye, bearing deg, half-angle, length)
SIGHTLINES = [((190.0, 170.0), 302, 32, 260), ((166.0, -80.0), 293, 45, 260), ((22.0, -10.0), 326, 32, 120)]
CARD_MIN_D = 40.0         # refill cards only this far from their own felt (and >= 26 from any felt)
TRI_FILE = 19000
CAPS = dict(span=2, string=2, hook=4, tree=11, far=2, near=34, mid=14, card=30, interior=26, accent=6, hollow=26, rail=30, hang=3)
ROLE_SEQ = ["span", "string", "hook", "tree1", "near", "tree", "far", "mid", "card"]   # tree1 = first TREE_FIRST trees per hole
TREE_FIRST = 4
TALL_H = 2.0              # pass 5: props taller than this ...
RAIL_BACK = 3.0           # ... stay this far (horizontal) from every rail, footprint + geometry below base + EYE_BAND
EYE_BAND = 5.0
PLANTS = {p["name"] for p in registry.PROPS if registry.category(p["name"]) == "plant"}    # pass 7b
PLANT_CLEAR = registry.PLANT_RAIL_CLEAR
PLANT_NUDGE = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]      # outward nudge radii for plant_near_rail (any role)
NUDGE = dict(span=[0.5, 1.0, 1.5, 2.0], string=[0.5, 1.0, 1.5, 2.0], hook=[0.5, 1.0, 1.5, 2.0],
             tree=[1, 2, 3, 4, 5, 6], far=[1, 2, 3, 4, 5, 6], near=[0.5, 1, 1.5, 2, 2.5, 3],
             mid=[0.5, 1, 1.5, 2, 2.5, 3], card=[2, 4, 6, 8, 10, 12], interior=[0.4, 0.8], accent=[0.3, 0.6],
             hollow=[0.4, 0.8, 1.2], rail=[], hang=[])
# own-dressing tri budget per hole and role group (inside the shared NEAR_BUDGET), so lanterns + framing trees +
# ground cover all get a share instead of the first roles eating the near field
ROLE_GROUP = dict(span="lantern", string="lantern", hook="lantern", tree="tree", far="far", near="ground",
                  mid="ground", interior="interior", card="card", accent="accent", hollow="hollow",
                  rail="lantern8", hang="lantern8")
GROUP_BUDGET = dict(lantern=5200, tree=7400, far=2600, ground=6500, interior=9000, card=10 ** 9, accent=4000,
                    hollow=6000, lantern8=4500)
# pass 6: H7 was the barest hole (13 3D props) because its near field (and H8's, which covers all of H7) is shared
# with H6/H8/H9 dressing that filled the budget first. H7 now goes first in every round-robin role of the seed pass,
# and gets an extra low-ground-cover / framing refill (REFILL_H7) right after the seed pass, before the other holes'
# refills.
RESERVE = {}             # (reserve experiment: H7 7000 starved H6 by 12 props and gave H7 +5 -> priority instead)
H_ORDER = [7, 1, 2, 3, 4, 5, 6, 8, 9]     # pass 6: H7 first in every round-robin role of the seed pass
# ... and no single OTHER hole may put more than FOREIGN_CAP tris into a PROTECTed hole's near field (pass 5: H6 put
# 13.3k and H8 11.5k into H7's 34k), so H7's own share can grow
PROTECT = (7,)
FOREIGN_CAP = 10 ** 9     # (cap experiment, 10500: H6 lost 8 props, H7 +1 because H8's near field binds) -> off
FOREIGN = {m: {o: 0 for o in range(1, 10)} for m in PROTECT}
RESERVE_ON = [True]
REFILL_H7 = dict(near_extra=14, mid_extra=3)
HEAVY_SMALL = 900          # near/mid props above this many tris (toadstool clusters, glowing mushrooms): max 2 per hole
HEAVY_CAP = 2
SPREAD = dict(tree=3.0, far=3.0, card=3.5)      # max terrain spread under the footprint (default 1.5)
TREES = {
    "forest": ["maple_tree_round", "red_maple_tree", "maple_tree_tall", "golden_birch_tree", "maple_tree_lanterns"],
    "village": ["maple_tree_round", "red_maple_tree", "maple_tree_tall", "oak_tree_orange", "maple_tree_lanterns"],
    "stream": ["oak_tree_orange", "maple_tree_round", "golden_birch_tree", "maple_tree_tall", "red_maple_tree"],
    "hollow": ["oak_tree_orange", "maple_tree_lanterns", "maple_tree_round", "golden_birch_tree"],
}
CHEAP_NEAR = ["red_leaf_bush", "orange_leaf_bush", "gold_leaf_bush", "grass_tuft", "grass_tuft", "fern_clump",
              "fern_clump", "fern_clump_large", "red_bush_tall", "mossy_boulder", "red_leaf_bush"]
THEME = {1: "forest", 2: "forest", 3: "village", 4: "village", 5: "stream", 6: "stream", 7: "stream", 8: "hollow",
         9: "hollow"}

# ----------------------------------------------------------------------------- templates (same as dressing.py)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "NONE"
OCC = world_occ.build_or_load()
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "NONE"
lglib._scratch = None
TCOL = bpy.data.collections.new("_dress_templates")
sc.collection.children.link(TCOL)
TPL = {}


def template(name):
    if name in TPL:
        return TPL[name]
    p = REG[name]
    pb = lglib.PB(name)
    post = p["fn"](pb)
    root, objs = pb.finalize(TCOL, p.get("smooth_angle", 40))
    if callable(post):
        post(root, objs)
        lglib.box_uv_objects(objs)
    vb = np.concatenate([np.array([v.co[:] for v in o.data.vertices]) for o in objs])
    v = np.stack([vb[:, 0], vb[:, 2], -vb[:, 1]], 1)
    rad = np.hypot(v[:, 0], v[:, 2])
    low = v[:, 1] < 1.0
    base_r = float(rad[low].max()) if low.any() else 0.5
    hi = v[:, 1] > 5.0
    is_tree = ("tree" in name or "sapling" in name) and not name.startswith("treeline_card")
    crown_r = float(rad[hi].max()) if is_tree and hi.any() else 0.0
    bases = [(0.0, 0.0, min(base_r, 2.2 if crown_r else base_r))]
    if name.startswith("lantern_span_") or name == "lantern_string_poles":
        hx = float(np.abs(v[:, 0]).max()) - 0.3
        bases = [(-hx, 0.0, 0.5), (hx, 0.0, 0.5)]
    if name == "lantern_hook_pair":
        bases = [(0.0, 0.0, 0.5)]
    if name.startswith("treeline_card"):
        bases = [(0.0, 0.0, 6.0)]
    lights = []
    for o in objs:
        if lglib.mat_of(o.name) != "Glow":
            continue
        b = bmesh.new()
        b.from_mesh(o.data)
        seen = set()
        for vert in b.verts:
            if vert.index in seen:
                continue
            stack, isl = [vert], []
            seen.add(vert.index)
            while stack:
                q = stack.pop()
                isl.append(q.co.copy())
                for e in q.link_edges:
                    w = e.other_vert(q)
                    if w.index not in seen:
                        seen.add(w.index)
                        stack.append(w)
            c = sum(isl, Vector()) / len(isl)
            lights.append((c.x, c.z, -c.y))
        b.free()
    tris_l = []
    for o in objs:
        me = o.data
        me.calc_loop_triangles()
        V = np.array([vv.co[:] for vv in me.vertices], float)
        idx = np.array([t.vertices[:] for t in me.loop_triangles], int)
        if len(idx):
            tris_l.append(V[idx])
    Tb = np.concatenate(tris_l)
    Tr = np.stack([Tb[..., 0], Tb[..., 2], -Tb[..., 1]], -1)
    TPL[name] = dict(name=name, objs=objs, v=v, T=Tr, height=float(v[:, 1].max()), base_r=base_r, crown_r=crown_r,
                     bases=bases, tris=lglib.tri_count(objs), lights=lights)
    return TPL[name]


# ----------------------------------------------------------------------------- world data + keep-outs
W = WF.load_world()
H = WF.holes_world(W)
HM = {h["number"]: h for h in H}
TER = WF.Terrain()
TREE = W["hollow_tree"]
TO = np.array(TREE["center"], float)
R_IN, R_OUT = TREE["trunk_inner_radius"], TREE["trunk_outer_radius"]
SEED = json.load(open(os.path.join(SRC, "dressing_seed_pass2.json")))["holes"]

KO = WF.dressing_keepouts(W, H)
KC = np.array([b.c for b in KO])
KR = np.array([b.rad for b in KO])
print(f"[dw] keep-outs: {len(KO)} boxes, occupancy grids: {len(OCC.g)}  ({time.time() - T0:.0f}s)")

# pass 5: every collision wall (rails, backings, boards, deflectors, bumpers) of every hole as a world 2D rectangle
_rl = []
for _h in H:
    for _w in _h["walls"]:
        _c = DL.to_world(_h, _w["center"])
        _a = math.radians(_w.get("yaw", 0) + _h["world_yaw"])
        _rl.append((_c[0], _c[2], math.cos(_a), math.sin(_a), _w["size"][0] / 2, _w["size"][2] / 2))
RAILS2D = np.array(_rl)


def rail_dist(X, Z):
    """Horizontal distance from points (X, Z world) to the nearest wall rectangle of any hole."""
    X, Z = np.atleast_1d(np.asarray(X, float)), np.atleast_1d(np.asarray(Z, float))
    R = RAILS2D
    dx, dz = X[:, None] - R[None, :, 0], Z[:, None] - R[None, :, 1]
    c, s_ = R[None, :, 2], R[None, :, 3]
    lx = dx * c - dz * s_
    lz = dx * s_ + dz * c                      # (= R^T of DL.yaw_mat)
    ex = np.maximum(np.abs(lx) - R[None, :, 4], 0)
    ez = np.maximum(np.abs(lz) - R[None, :, 5], 0)
    return np.hypot(ex, ez).min(1)


def tall_rail_clear(T, s, bases, P, y):
    """pass 5 rule: True if the prop is <= TALL_H high, or its footprint and its geometry below y + EYE_BAND stay
    >= RAIL_BACK from every wall."""
    if T["height"] * s <= TALL_H:
        return True
    for (bx, bz, br) in bases:
        if rail_dist(bx, bz)[0] - br < RAIL_BACK - 1e-6:
            return False
    low = P[P[:, 1] < y + EYE_BAND]
    if len(low) and rail_dist(low[:, 0], low[:, 2]).min() < RAIL_BACK - 1e-6:
        return False
    return True


def rail_gap_tris(Tw, lim=None):
    """pass 7b: exact horizontal distance from a world triangle soup (N, 3, 3) to the nearest wall rectangle of any
    hole: projected triangle vs rectangle (2D convex polygons): 0 if they overlap (SAT on the 2 rectangle axes + 3 edge
    normals), else min(triangle vertex -> rectangle, rectangle corner -> triangle edge)."""
    A = Tw[..., [0, 2]]
    lo, hi = A.reshape(-1, 2).min(0), A.reshape(-1, 2).max(0)
    R = RAILS2D
    reach = np.hypot(R[:, 4], R[:, 5]) + (lim if lim is not None else 1e9)
    cx = np.clip(R[:, 0], lo[0], hi[0])
    cz = np.clip(R[:, 1], lo[1], hi[1])
    cand = np.nonzero(np.hypot(R[:, 0] - cx, R[:, 1] - cz) <= reach)[0]
    best = 1e9
    for k in cand:
        wx, wz, c, s_, hx, hz = R[k]
        dx, dz = A[..., 0] - wx, A[..., 1] - wz
        L = np.stack([dx * c - dz * s_, dx * s_ + dz * c], -1)            # (N, 3, 2) in the wall frame
        hxz = np.array([hx, hz])
        d1 = np.hypot(*np.maximum(np.abs(L) - hxz, 0).transpose(2, 0, 1)).min(1)       # tri verts -> rect
        corners = np.array([[hx, hz], [-hx, hz], [-hx, -hz], [hx, -hz]])
        P0, E = L, np.roll(L, -1, axis=1) - L                                # edges (N, 3, 2)
        Q = corners[None, None] - P0[:, :, None]                            # (N, 3, 4, 2)
        ee = (E * E).sum(-1)[..., None]
        t = np.clip((Q * E[:, :, None]).sum(-1) / np.maximum(ee, 1e-12), 0, 1)
        d2 = np.linalg.norm(Q - t[..., None] * E[:, :, None], axis=-1).min((1, 2))
        # SAT overlap: separated along x / z of the rect, or along an edge normal of the triangle
        sep = (L[..., 0].min(1) > hx) | (L[..., 0].max(1) < -hx) | (L[..., 1].min(1) > hz) | (L[..., 1].max(1) < -hz)
        Nrm = np.stack([-E[..., 1], E[..., 0]], -1)                          # (N, 3, 2)
        pt = (L[:, None] * Nrm[:, :, None]).sum(-1)                          # (N, 3 normals, 3 verts)
        pc = (corners[None, None] * Nrm[:, :, None]).sum(-1)                 # (N, 3 normals, 4 corners)
        sep |= ((pt.min(2) > pc.max(2) + 1e-9) | (pt.max(2) < pc.min(2) - 1e-9)).any(1)
        d = np.where(sep, np.minimum(d1, d2), 0.0)
        best = min(best, float(d.min()))
    return best


def outward_dir(x, z):
    """Unit XZ direction away from the nearest wall (numerical gradient of rail_dist), or None."""
    e = 0.05
    g = np.array([rail_dist(x + e, z)[0] - rail_dist(x - e, z)[0], rail_dist(x, z + e)[0] - rail_dist(x, z - e)[0]])
    L = float(np.linalg.norm(g))
    return g / L if L > 1e-6 else None


def in_sightline(x, z):
    for (ex, ez), brg, half, length in SIGHTLINES:
        dx, dz = x - ex, z - ez
        L = math.hypot(dx, dz)
        if L < 1 or L > length:
            continue
        b = math.degrees(math.atan2(dx, -dz)) % 360          # bearing: 0 = north (-Z), 90 = east (+X)
        if abs((b - brg + 180) % 360 - 180) < half:
            return True
    return False


def ko_hits(P, first_only=True):
    cxz = (P[:, [0, 2]].min(0) + P[:, [0, 2]].max(0)) / 2
    rxz = float(np.linalg.norm(P[:, [0, 2]].max(0) - P[:, [0, 2]].min(0)) / 2)
    cand = np.nonzero(np.linalg.norm(KC[:, [0, 2]] - cxz, axis=1) < KR + rxz + 0.01)[0]
    out = {}
    for k in cand:
        b = KO[k]
        L = (P - b.c) @ b.Rm
        n = int(np.all(np.abs(L) < b.hf, axis=1).sum())
        if n:
            out[b.label] = n
            if first_only:
                return out
    return out


def reason_of(label):
    if label.startswith("path:"):
        return "walkway/stairs"
    if label.startswith("lantern_post"):
        return "lantern_post"
    if label.startswith(("poi:", "mill_flume")):
        return "plaza/flume"
    if label.startswith("world:"):
        p = label[6:]
        if "shell_part5" in p:
            return "tree_roots"
        if p.startswith("hollow_tree"):
            return "tree_shell"
        if "falls" in p:
            return "waterfall"
        if p.startswith("highland_cliff"):
            return "cliff_kit"
        if p.startswith("terrace_rock"):
            return "rock_face"
        return "world_piece"
    if label.startswith("sweep:"):
        return "moving_sweep"
    parts = label.split(":")
    if len(parts) >= 2:
        k = parts[1]
        return {"felt": "felt", "wall": "wall", "hazard": "hazard", "teleport": "teleport", "tee_pad": "tee",
                "hero": "hero_prop"}.get(k, k)
    return label


def local_of(n, p):
    Rw, off = DL.hole_xf(HM[n])
    return (np.asarray(p, float) - off) @ Rw


def felt_dist_world(n, x, z):
    L = local_of(n, [x, 0, z])
    return float(DL.felt_distance(HM[n], np.array([L[0]]), np.array([L[2]]))[0])


def holes_near(x, z):
    return [n for n in HM if felt_dist_world(n, x, z) < NEAR_D]


def water_at(xs, zs):
    i = np.clip(np.floor((np.asarray(xs) - TER.x0) / TER.cell).astype(int), 0, TER.cols - 1)
    j = np.clip(np.floor((np.asarray(zs) - TER.z0) / TER.cell).astype(int), 0, TER.rows - 1)
    w = TER.W[j, i]
    h = TER.H[j, i]
    return np.any(~np.isnan(w) & (w > h + 0.05))


# ----------------------------------------------------------------------------- placed footprints
PLACED = []          # dict(bases=[(x,z,r)], crown=(x,z,r)|None, small, card, n)


def overlaps(bases, crown, small, card):
    for q in PLACED:
        if card or q["card"]:
            if card and q["card"]:
                if math.hypot(bases[0][0] - q["bases"][0][0], bases[0][1] - q["bases"][0][1]) < 11.0:
                    return True
                continue
            k = 0.5
        else:
            k = 0.55 if (small and q["small"]) else 0.62 if (small or q["small"]) else 1.0
        for (ax, az, ar) in bases:
            for (bx, bz, br) in q["bases"]:
                if abs(ax - bx) > 30 or abs(az - bz) > 30:
                    continue
                if math.hypot(ax - bx, az - bz) < (ar + br) * k + 0.2:
                    return True
        if crown and q["crown"] and math.hypot(crown[0] - q["crown"][0], crown[1] - q["crown"][1]) < \
                0.62 * (crown[2] + q["crown"][2]):
            return True
    return False


def evaluate(n, prop, x, z, yaw_w, s, role):
    """-> (ok, reason, data). data: y, P, bases, crown, small, terrain_y."""
    T = template(prop)
    Rm = DL.yaw_mat(yaw_w)
    card = prop.startswith("treeline_card")
    if card and min(felt_dist_world(m, x, z) for m in HM) < CARD_ANY_D:
        return False, "card_too_close_to_felt", None
    if card and in_sightline(x, z):
        return False, "vista_sightline", None
    bases, foot = [], []
    xs, zs = [], []
    for (bx, bz, br) in T["bases"]:
        c = np.array([x, 0, z]) + Rm @ np.array([bx * s, 0, bz * s])
        r = br * s
        fr = max(r, 1.5) if T["crown_r"] else max(r, 0.6)
        bases.append((c[0], c[2], r))
        foot.append([round(float(c[0]), 3), round(float(c[2]), 3), round(float(fr), 3)])
        xs.append(c[0])
        zs.append(c[2])
        for k in range(8):
            a = math.tau * k / 8
            for f in (0.5, 1.0):
                xs.append(c[0] + math.cos(a) * fr * f)
                zs.append(c[2] + math.sin(a) * fr * f)
    xs, zs = np.array(xs), np.array(zs)
    if water_at(xs, zs):
        return False, "water", None
    hs = TER.height(xs, zs)
    spread = float(hs.max() - hs.min())
    lim = SPREAD.get("tree" if T["crown_r"] else role, 1.5)
    if spread > lim:
        return False, "slope", None
    sink = 0.25 if T["crown_r"] else (0.0 if card else 0.05)
    y = float(hs.min() + 0.3 * spread - sink)
    P = T["v"] * s @ Rm.T + np.array([x, y, z])
    r = np.hypot(P[:, 0] - TO[0], P[:, 2] - TO[2])
    if n == 9:
        if r.max() > R_IN - 0.3:
            return False, "outside_trunk", None
        if T["height"] * s > 4.5:          # inside the hollow only low props (as pass 2's cavity rule)
            return False, "too_tall_in_trunk", None
    elif r.min() < R_OUT + 1.0:
        return False, "tree_shell", None
    if not tall_rail_clear(T, s, bases, P, y):
        return False, "tall_near_rail", None
    gap = None
    if prop in PLANTS:                     # pass 7b: whole plant footprint >= 1.5 from every rail / wall
        gap = rail_gap_tris(T["T"] * s @ Rm.T + np.array([x, y, z]), PLANT_CLEAR + 1.0)
        if gap < PLANT_CLEAR - 1e-6:
            return False, "plant_near_rail", None
    crown = (x, z, T["crown_r"] * s) if T["crown_r"] else None
    small = T["height"] * s < 3.6
    if overlaps(bases, crown, small, card):
        return False, "overlap", None
    k = ko_hits(P)
    if k:
        return False, reason_of(next(iter(k))), None
    Tw = T["T"] * s @ Rm.T + np.array([x, y, z])          # exact triangle test (thin ropes / canopies)
    k = WF.check_tris(Tw, KO)
    if k:
        return False, reason_of(next(iter(k))), None
    o = OCC.hits(np.concatenate([P, Tw.mean(1)]), first_only=True)
    if o:
        return False, reason_of(next(iter(o))), None
    return True, "", dict(y=y, P=P, bases=bases, crown=crown, small=small, card=card, foot=foot, spread=spread, gap=gap,
                          terrain_y=float(TER.height(np.array([x]), np.array([z]))[0]))


NEAR_LOAD = {n: 0 for n in HM}
NEAR_LOAD_BEFORE = {n: 0 for n in HM}


def commit(n, prop, x, z, yaw_w, s, role, data, status, extra=None):
    T = template(prop)
    OWN_GROUP[n][ROLE_GROUP[role]] += T["tris"]
    for m in holes_near(x, z):
        NEAR_LOAD[m] += T["tris"]
        if m in PROTECT and m != n:
            FOREIGN[m][n] += T["tris"]
    PLACED.append(dict(bases=data["bases"], crown=data["crown"], small=data["small"], card=data["card"], n=n))
    h = HM[n]
    L = local_of(n, [x, data["y"], z])
    it = dict(prop=prop, role=role, status=status,
              pos=[round(float(L[0]), 3), round(float(L[1]), 3), round(float(L[2]), 3)],
              yaw=round((yaw_w - h["world_yaw"]) % 360, 1), scale=round(s, 3),
              world_pos=[round(x, 3), round(data["y"], 3), round(z, 3)], world_yaw=round(yaw_w % 360, 1),
              terrain_y=round(data["terrain_y"], 3), footprint=data["foot"], ground_spread=round(data["spread"], 3))
    if data.get("gap") is not None:
        # pass 7b: plant footprint -> nearest wall (exact up to PLANT_CLEAR + 1; 2.5 means ">= 2.5")
        it["rail_gap"] = round(min(data["gap"], PLANT_CLEAR + 1.0), 3)
    if extra:
        it.update(extra)
    return it


OWN_GROUP = {n: {g: 0 for g in GROUP_BUDGET} for n in range(1, 10)}


def budget_ok(prop, x, z, n=None, role=None, owner=None):
    t = template(prop)["tris"]
    if n is not None and OWN_GROUP[n][ROLE_GROUP[role]] + t > GROUP_BUDGET[ROLE_GROUP[role]]:
        return False

    def lim(m):
        return NEAR_BUDGET - (RESERVE.get(m, 0) if RESERVE_ON[0] and owner is not None and owner != m else 0)
    near = holes_near(x, z)
    if owner is not None and any(FOREIGN[m][owner] + t > FOREIGN_CAP for m in near if m in PROTECT and m != owner):
        return False
    return all(NEAR_LOAD[m] + t <= lim(m) for m in near)


# ----------------------------------------------------------------------------- seed queue
def tee_frame(n):
    h = HM[n]
    tee = DL.to_world(h, h["tee"]["position"])
    aim_l = np.array([h["tee"]["aim_hint"][0], 0, h["tee"]["aim_hint"][1]], float)
    aim = DL.hole_xf(h)[0] @ aim_l
    return tee, aim / np.linalg.norm(aim)


def in_view(n, x, z, cone=42):
    tee, aim = tee_frame(n)
    d = np.array([x, 0, z]) - (tee - aim)
    L = np.linalg.norm(d)
    return L > 1 and (d @ aim) / L > math.cos(math.radians(cone))


CARD_COL = {"forest": ["treeline_card_red", "treeline_card_red", "treeline_card_gold"],
            "village": ["treeline_card_red", "treeline_card_gold"],
            "stream": ["treeline_card_gold", "treeline_card_gold", "treeline_card_red"],
            "hollow": ["treeline_card_gold", "treeline_card_red"]}

STATS = {n: dict(seed=0, kept=0, moved=0, converted_to_card=0, removed=0, added=0, removed_by=dict(),
                 moved_because=dict()) for n in HM}
INST = {n: [] for n in HM}
REMOVED = {n: [] for n in HM}
COUNT = {n: {r: 0 for r in CAPS} for n in HM}
HEAVY = {n: 0 for n in HM}
queues = {r: {n: [] for n in HM} for r in ROLE_SEQ if r != "tree1"}
tris_before = {}
for n in HM:
    h = HM[n]
    seed = SEED[f"H{n}"]["instances"]
    STATS[n]["seed"] = len(seed)
    tb = 0
    rnd = random.Random(400 + n)
    for it in seed:
        T = template(it["prop"])
        tb += T["tris"]
        pw = DL.to_world(h, it["pos"])
        for m in holes_near(pw[0], pw[2]):
            NEAR_LOAD_BEFORE[m] += T["tris"]
        role = it["role"]
        q = dict(seed=it, x=float(pw[0]), z=float(pw[2]), yaw_w=it["yaw"] + h["world_yaw"], s=it["scale"],
                 prop=it["prop"], role=role, convert=False)
        if role == "backdrop":
            q.update(role="card", prop=rnd.choice(CARD_COL[THEME[n]]), s=it["scale"] * rnd.uniform(0.85, 1.05),
                     convert=True)
        tee, aim = tee_frame(n)
        q["score"] = (0 if in_view(n, q["x"], q["z"]) else 1,
                      1 if (q["role"] in ("near", "mid") and T["tris"] > 1000) else 0,
                      float(np.hypot(q["x"] - tee[0], q["z"] - tee[2])))
        queues[q["role"]][n].append(q)
    tris_before[n] = tb
    for r in queues:
        queues[r][n].sort(key=lambda q: q["score"])


def try_with_nudge(n, prop, x, z, yaw_w, s, role):
    ok, why, data = evaluate(n, prop, x, z, yaw_w, s, role)
    if ok:
        return x, z, data, why, 0.0
    first = why
    if why in ("outside_trunk", "too_tall_in_trunk"):
        return None, None, None, first, None
    if why == "plant_near_rail":
        # pass 7b: nudge OUTWARD, away from the nearest wall (within +-90 deg of the outward direction), same role
        od = outward_dir(x, z)
        if od is not None:
            base_a = math.atan2(od[1], od[0])
            for r in PLANT_NUDGE:
                for da in (0, 20, -20, 40, -40, 60, -60, 90, -90):
                    a = base_a + math.radians(da)
                    xx, zz = x + math.cos(a) * r, z + math.sin(a) * r
                    ok, why, data = evaluate(n, prop, xx, zz, yaw_w, s, role)
                    if ok:
                        return xx, zz, data, first, r
            return None, None, None, first, None
    for r in NUDGE[role]:
        for k in range(12):
            a = math.tau * k / 12 + (r * 0.37)
            xx, zz = x + math.cos(a) * r, z + math.sin(a) * r
            ok, why, data = evaluate(n, prop, xx, zz, yaw_w, s, role)
            if ok:
                return xx, zz, data, first, r
    return None, None, None, first, None


def bump(d, k):
    d[k] = d.get(k, 0) + 1


# ----------------------------------------------------------------------------- pass 5: cup / gate lanterns (first)
ACCENT = "cup_lantern_stake"
ACCENT_R = 9.0
ACCENT_TARGETS = [(8, "cup", HM[8]["cup"]["position"]), (9, "cup", HM[9]["cup"]["position"])] + \
    [(9, m["id"], m["pivot"]) for m in HM[9]["moving_parts"] if m["id"] == "root_gate"]     # skipped if renamed


def place_accents(n, tag, target_l, want=2, min_sep=4.0):
    tw = DL.to_world(HM[n], target_l)
    cands = []
    # pass 6: rings out to ACCENT_R (the moved H8 cup only has room 7.5-9 studs out: tree roots south of the green)
    for r in np.arange(1.0, ACCENT_R + 0.01, 0.25):
        for k in range(36):
            a = math.tau * k / 36
            x, z = tw[0] + math.cos(a) * r, tw[2] + math.sin(a) * r
            d = felt_dist_world(n, x, z)
            if 1.35 <= d <= 2.6:
                cands.append((r + 0.6 * d, x, z))
    cands.sort()
    got = []
    why_ = {}
    for _, x, z in cands:
        if len(got) >= want:
            break
        if any(math.hypot(x - gx, z - gz) < min_sep for gx, gz in got):
            continue
        yaw = math.degrees(math.atan2(tw[0] - x, tw[2] - z))
        ok, why, data = evaluate(n, ACCENT, x, z, yaw, 1.0, "accent")
        if not ok or not budget_ok(ACCENT, x, z, owner=n):
            why_[why or "budget"] = why_.get(why or "budget", 0) + 1
            continue
        INST[n].append(commit(n, ACCENT, x, z, yaw, 1.0, "accent", data, "added",
                              dict(marks=tag, dist_to_target=round(math.hypot(x - tw[0], z - tw[2]), 2))))
        COUNT[n]["accent"] += 1
        STATS[n]["added"] += 1
        got.append((x, z))
    print(f"[dw] H{n} {tag}: {len(got)} lanterns ({len(cands)} candidates; rejected {why_})")
    return got


for n_, tag_, tl_ in ACCENT_TARGETS:
    place_accents(n_, tag_, tl_)


# ----------------------------------------------------------------------------- pass 8: lantern light (placed first)
# Game Art Bot lighting direction: H9 lantern-lit (3 hanging paper lanterns over the corridor -> chamber -> heart,
# bottom HANG_BOTTOM above the local felt), small rail lanterns ~every RAIL_STEP studs outside BOTH rails of the H7
# lower tiers and the whole of H8. Placed right after the cup lanterns, before every other role, so the zero-sum
# near-field budget trims the lowest-priority ground cover instead. Each lantern gets a PointLight in LIGHTS8
# (manifest.lights[]; amber Color3(255, 169, 87) ~2700K) and its id on the instance (light_id).
import props_pass8 as P8
AMBER, AMBER_RGB = "#FFA957", [255, 169, 87]
LIGHTS8 = []
HANG_PROP, HANG_BOTTOM, HANG_N = "lantern_large_hanging", 8.0, 3
HANG_SCALE = 1.5          # render iteration 1: at 1.0 (2-stud lantern) the corridor lantern read small from the tee
# pass 8 addendum (holes.json Round 7 final): the 3 lanterns hang on the holes.json decoration anchors amber_lantern_1..3
# over the heart green (props.md: 1.2 x 1.8 x 1.2 lantern -> lantern_large x 0.85, bottom = anchor y = 8 above the
# felt, cord top y ~16). They replace the heart_lantern_cluster (no longer placed). Without anchors: the even
# corridor -> chamber -> heart spacing above.
HANG_ANCHOR, HANG_ANCHOR_SCALE = "amber_lantern_", 0.85
HANG_PATH = [(5.75, -25.5), (22.0, -29.0), (23.0, -49.5)]     # H9 corridor (corr1) -> chamber -> heart green centres
# H7: stake first; where the ground beside the lower tiers drops so far that a stake lantern hides below the rail
# top, the crook post (lantern 5.25+ above its base, post >= 3 back) is used instead. H8 (3.9-tall walls): crook only.
RAIL_PROP = {7: ("rail_lantern_stake", "rail_lantern_crook"), 8: ("rail_lantern_crook",)}
RAIL_STEP, RAIL_LO, RAIL_HI = 10.0, 8.0, 12.0
RAIL_OFF = {7: 1.4, 8: 1.5}       # lantern centre -> wall centreline (felt keep-out: felt edge + 1.25 + lantern r)
RAIL_OFF_EXTRA = (0.0, 0.5, 1.0, 1.5)     # ... or this much further out (water / roots / slopes beside the rail)
RAIL_SEE = {"rail_lantern_stake": 0.2, "rail_lantern_crook": 0.8}   # lantern top / centre this far above the rail top
RAIL_LIGHT = dict(range=10.0, brightness=1.2)
HANG_LIGHT = dict(range=16.0, brightness=3.0)
# per side: (start point near the tee, [(wall id, clip(local p) or None), ...]) in play order; walls are walked from
# the end nearest the previous wall, the lantern line runs outside the wall (side away from the hole's felt)
RAIL_CHAINS = {
    7: dict(left=((0.0, -13.75), [("rail4", None), ("rail5", None), ("rail6", None), ("rail11", None),
                                  ("rail12", lambda p: p[0] <= 1.0)]),
            right=((0.0, -13.75), [("rail10", None), ("rail9", None), ("rail13", None),
                                   ("rail12", lambda p: p[0] > 1.0)])),
    8: dict(left=((0.0, 2.25), [("rail3", None), ("rail4", None), ("bank1_backing", None), ("rail5", None),
                                ("bank2_backing", None), ("rail6", None), ("rail7", None), ("rail8", None)]),
            right=((0.0, 2.25), [("rail17", None), ("rail16", None), ("rail15", None), ("rail14", None),
                                 ("rail13", None), ("rail12", None), ("rail11", None), ("rail10", None),
                                 ("rail9", None)])),
}


def yaw_to(v):
    """yaw (deg) that turns prop-local +X onto the XZ direction v (DL.yaw_mat: +X -> (cos, 0, -sin))."""
    return math.degrees(math.atan2(-v[2], v[0]))


def felt_top_at(n, lx, lz):
    tops = [r[5] for r in DL.felt_rects(HM[n]) if DL.rect_dist(np.array([lx]), np.array([lz]), r)[0] <= 0]
    return max(tops) if tops else None


def light_entry(n, lid, kind, lp, col, rgb, rng, bri, **kw):
    pw = DL.to_world(HM[n], lp)
    e = dict(id=lid, hole=f"H{n}", kind=kind, light="PointLight", color=col, color3=rgb, range=rng, brightness=bri,
             shadows=False, pos=[round(float(v), 2) for v in lp], world_pos=[round(float(v), 2) for v in pw])
    e.update(kw)
    LIGHTS8.append(e)
    return e


def rail_candidates(n, side):
    h = HM[n]
    start, chain = RAIL_CHAINS[n][side]
    last = np.array([start[0], 0.0, start[1]])
    out = []
    for wid, clip in chain:
        w = ([w for w in h["walls"] if w["id"] == wid] or [None])[0]
        if w is None:
            continue
        Ry = DL.yaw_mat(w.get("yaw", 0))
        c = np.array(w["center"], float)
        ax, nrm = Ry @ np.array([0, 0, 1.0]), Ry @ np.array([1.0, 0, 0])
        best, sgn = -1.0, 1
        for s_ in (1, -1):
            p = c + nrm * s_ * (w["size"][0] / 2 + 0.6)
            fd = float(DL.felt_distance(h, np.array([p[0]]), np.array([p[2]]))[0])
            if fd > best:
                best, sgn = fd, s_
        if best < 0.3:
            continue
        nout = nrm * sgn
        L = w["size"][2]
        pts = [c + ax * t for t in np.arange(-L / 2 + 0.25, L / 2 - 0.25 + 1e-6, 0.5)]
        if np.linalg.norm((pts[-1] - last)[[0, 2]]) < np.linalg.norm((pts[0] - last)[[0, 2]]):
            pts = pts[::-1]
        top = w["center"][1] + w["size"][1] / 2
        for p in pts:
            if clip and not clip(p):
                continue
            for ex in RAIL_OFF_EXTRA:
                lp = p + nout * (RAIL_OFF[n] + ex)
                for prop in RAIL_PROP[n]:
                    out.append(dict(wall=wid, lp=lp, nout=nout, wall_top=top, off=RAIL_OFF[n] + ex, prop=prop))
        last = pts[-1]
    return out


def place_rail_lanterns(n, side):
    h = HM[n]
    cands = rail_candidates(n, side)

    def reach_of(prop):
        return P8.CROOK_REACH if prop == "rail_lantern_crook" else 0.0
    cache = {}

    def ok(k):
        if k in cache:
            return cache[k]
        c = cands[k]
        prop = c["prop"]
        T = template(prop)
        op = c["lp"] + c["nout"] * reach_of(prop)
        yaw_l = yaw_to(-c["nout"])
        pw = DL.to_world(h, op)
        yaw_w = yaw_l + h["world_yaw"]
        good, why, data = evaluate(n, prop, pw[0], pw[2], yaw_w, 1.0, "rail")
        if good:     # visible over its rail: stake lantern top / crook lantern centre above the rail top
            ly = data["y"] - h["world_offset"][1] + T["lights"][0][1] + (0.37 if prop == "rail_lantern_stake" else 0)
            if ly < c["wall_top"] + RAIL_SEE[prop]:
                good, why = False, "below_rail_top"
        if good and not (budget_ok(prop, pw[0], pw[2], owner=n) and budget_ok(prop, pw[0], pw[2], n, "rail")):
            good, why = False, "budget"
        cache[k] = (good, why, data, pw, yaw_w)
        return cache[k]

    chosen, why_ = [], {}
    k = 0
    while k < len(cands) and not ok(k)[0]:
        why_[ok(k)[1]] = why_.get(ok(k)[1], 0) + 1
        k += 1
    if k >= len(cands):
        print(f"[dw] H{n} rail lanterns {side}: none ({why_})")
        return []
    chosen.append((k, None))
    while True:
        prev = cands[chosen[-1][0]]["lp"]
        later = range(chosen[-1][0] + 1, len(cands))
        dist = {j: float(np.linalg.norm((cands[j]["lp"] - prev)[[0, 2]])) for j in later}
        pick = None
        for lo, hi in ((9.5, 10.5), (RAIL_LO + 0.1, RAIL_HI - 0.1)):
            for j in sorted((j for j in later if lo <= dist[j] <= hi), key=lambda j: abs(dist[j] - RAIL_STEP)):
                if ok(j)[0]:
                    pick = j
                    break
                why_[ok(j)[1]] = why_.get(ok(j)[1], 0) + 1
            if pick is not None:
                break
        gap = None
        if pick is None:          # blocked stretch: restart the line at the next valid spot further on
            for j in later:
                if dist[j] > RAIL_HI - 0.1 and ok(j)[0]:
                    pick, gap = j, round(dist[j], 2)
                    break
        if pick is None:
            break
        if gap is not None:       # every spot 8..12 from the previous lantern was blocked: record them for fitcheck
            win = []
            for j in later:
                if RAIL_LO <= dist[j] <= RAIL_HI and j < pick:
                    c = cands[j]
                    op = c["lp"] + c["nout"] * reach_of(c["prop"])
                    win.append(dict(prop=c["prop"], origin=[round(float(v), 3) for v in DL.to_world(h, op)],
                                    yaw=round(yaw_to(-c["nout"]) + h["world_yaw"], 2), wall=c["wall"],
                                    wall_top=c["wall_top"], why=ok(j)[1]))
            gap = dict(dist=gap, window=win)
        chosen.append((pick, gap))
    got = []
    for seq, (k, gap) in enumerate(chosen):
        good, why, data, pw, yaw_w = ok(k)
        c = cands[k]
        prop = c["prop"]
        T = template(prop)
        lid = f"H{n}_rail_{side}_{seq + 1:02d}"
        it = commit(n, prop, pw[0], pw[2], yaw_w, 1.0, "rail", data, "added",
                    dict(marks=f"rail_lantern:{side}", side=side, wall=c["wall"], wall_top=c["wall_top"],
                         seq=seq + 1, light_id=lid, chain_gap_before=gap["dist"] if gap else None,
                         gap_window=gap["window"] if gap else None))
        lp = DL.transform_verts(np.array([T["lights"][0]]), it["pos"], it["yaw"], 1.0)[0]
        it["lantern_pos"] = [round(float(v), 3) for v in lp]
        INST[n].append(it)
        COUNT[n]["rail"] += 1
        STATS[n]["added"] += 1
        light_entry(n, lid, "rail_lantern", lp, AMBER, AMBER_RGB, RAIL_LIGHT["range"], RAIL_LIGHT["brightness"],
                    prop=prop, side=side, wall=c["wall"], parent="the Neon Glow part of this rail lantern instance")
        got.append(it)
    sp = [round(float(np.linalg.norm((np.array(a["lantern_pos"]) - np.array(b["lantern_pos"]))[[0, 2]])), 2)
          for a, b in zip(got, got[1:])]
    print(f"[dw] H{n} rail lanterns {side}: {len(got)} of {len(cands)} candidates, spacing {sp}, "
          f"breaks {[(g['dist'], len(g['window'])) for _, g in chosen if g]}, rejected {why_}")
    return got


# the heart green already carries the hero heart_lantern_cluster (dozens of lanterns on cords, y 7.5..13.6 over the
# heart): its keep-out OBB covers the whole heart, but its real mesh leaves room. A hanging lantern may enter that OBB
# only if its mesh (vertices, edge midpoints, centroids) stays >= CLUSTER_CLEAR from the cluster's mesh.
CLUSTER_LBL, CLUSTER_CLEAR = "H9:hero:heart_lantern_cluster", 0.6
_CL = []


def tri_pts(Tw):
    return np.concatenate([Tw.reshape(-1, 3), Tw.mean(1), (Tw + np.roll(Tw, -1, axis=1)).reshape(-1, 3) / 2])


def cluster_gap(Tw):
    if not _CL:
        pl = REG["heart_lantern_cluster"]["placements"][0]
        Tl = template("heart_lantern_cluster")["T"] @ DL.yaw_mat(pl.get("yaw", 0)).T + np.asarray(pl["pos"], float)
        _CL.append(tri_pts(DL.to_world(HM[9], Tl.reshape(-1, 3)).reshape(-1, 3, 3)))
    C, P = _CL[0], tri_pts(Tw)
    d = np.full(len(P), 1e9)
    for i in range(0, len(C), 4000):
        d = np.minimum(d, np.linalg.norm(P[:, None] - C[None, i:i + 4000], axis=2).min(1))
    return float(d.min())


def hang_eval(n, prop, lx, lz, bottom=None, scale=None):
    """H9 hanging lantern: bottom HANG_BOTTOM above the local felt (or at local y `bottom`); must clear keep-outs
    (heroes, moving-part sweeps, walls), world pieces, and stay inside the hollow."""
    h = HM[n]
    sc_ = scale or HANG_SCALE
    ft = felt_top_at(n, lx, lz)
    if ft is None:
        return None
    T = template(prop)
    y0 = (ft + HANG_BOTTOM if bottom is None else bottom) - float(T["v"][:, 1].min()) * sc_   # mesh bottom (tassel)
    pw = DL.to_world(h, [lx, y0, lz])
    Rm = DL.yaw_mat(h["world_yaw"])
    P = T["v"] * sc_ @ Rm.T + pw
    Tw = T["T"] * sc_ @ Rm.T + pw
    r = np.hypot(P[:, 0] - TO[0], P[:, 2] - TO[2])
    if r.max() > R_IN - 0.3 or OCC.hits(np.concatenate([P, Tw.mean(1)]), first_only=True):
        return None
    bad = set(ko_hits(P, first_only=False)) | set(WF.check_tris(Tw, KO))
    cg = None
    if CLUSTER_LBL in bad:
        cg = cluster_gap(Tw)
        if cg >= CLUSTER_CLEAR:
            bad.discard(CLUSTER_LBL)
    if bad:
        return None
    return ft, pw, cg


def place_hanging(n=9):
    h = HM[n]
    pts = np.array(HANG_PATH, float)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])

    def at(s):
        i = min(int(np.searchsorted(cum, s, side="right")) - 1, len(seg) - 1)
        u = (s - cum[i]) / seg[i]
        return pts[i] + (pts[i + 1] - pts[i]) * u

    best = None
    anchors = [a for a in h.get("decoration_anchors", []) if a["name"].startswith(HANG_ANCHOR)]
    sc_ = HANG_ANCHOR_SCALE if anchors else HANG_SCALE
    if anchors:
        anchors.sort(key=lambda a: a["name"])
        res = [hang_eval(n, HANG_PROP, a["position"][0], a["position"][2], a["position"][1], sc_) for a in anchors]
        bad_ = [a["name"] for a, r in zip(anchors, res) if r is None]
        if bad_:
            print(f"[dw] H9 hanging lanterns: anchors {bad_} NOT clear -> skipped")
        best = ([None] * len(anchors), res, anchors)
    for b in (np.arange(cum[-1], 10.0, -0.5) if not anchors else ()):          # furthest end towards the heart first, then the earliest start
        for a in np.arange(0.0, 3.01, 0.5):
            ss = np.linspace(a, b, HANG_N)
            res = [hang_eval(n, HANG_PROP, *at(s)) for s in ss]
            if all(res):
                best = (ss, res, [None] * len(ss))
                break
        if best:
            break
    if best is None:
        print("[dw] H9 hanging lanterns: no valid evenly spaced set")
        return []
    T = template(HANG_PROP)
    got = []
    for k, (s, r_, anc) in enumerate(zip(*best)):
        if r_ is None:
            continue
        ft, pw, cg = r_
        lx, lz = (anc["position"][0], anc["position"][2]) if anc else at(s)
        data = dict(y=float(pw[1]), bases=[(pw[0], pw[2], 0.75 * HANG_SCALE)], crown=None, small=True, card=False,
                    foot=[[round(float(pw[0]), 3), round(float(pw[2]), 3), 0.75 * HANG_SCALE]], spread=0.0, gap=None,
                    terrain_y=float(TER.height(np.array([pw[0]]), np.array([pw[2]]))[0]))
        lid = f"H{n}_hanging_lantern_{k + 1}"
        zone = ([f["zone"] for f, r in zip(h["felt"], DL.felt_rects(h))
                 if DL.rect_dist(np.array([lx]), np.array([lz]), r)[0] <= 0] or ["?"])[0]
        it = commit(n, HANG_PROP, pw[0], pw[2], h["world_yaw"], sc_, "hang", data, "added",
                    dict(marks=f"hanging_lantern:{zone}", hanging=True, felt_top=round(ft, 3),
                         heart_cluster_gap=round(cg, 3) if cg is not None else None,
                         bottom_above_felt=round(float((anc["position"][1] if anc else ft + HANG_BOTTOM) - ft), 3),
                         anchor=anc["name"] if anc else None,
                         path_s=round(float(s), 2) if s is not None else None, light_id=lid))
        INST[n].append(it)
        COUNT[n]["hang"] += 1
        STATS[n]["added"] += 1
        lp = DL.transform_verts(np.array([T["lights"][0]]), it["pos"], it["yaw"], sc_)[0]
        it["lantern_pos"] = [round(float(v), 3) for v in lp]
        light_entry(n, lid, "hanging_lantern", lp, AMBER, AMBER_RGB, HANG_LIGHT["range"], HANG_LIGHT["brightness"],
                    prop=HANG_PROP, zone=zone, parent="the Neon Glow part of this hanging lantern instance")
        got.append(it)
    print(f"[dw] H9 hanging lanterns ({'anchors' if anchors else 'path'}): at {[it['lantern_pos'] for it in got]}")
    return got


place_hanging(9)
for n_ in (7, 8):
    for side_ in ("left", "right"):
        place_rail_lanterns(n_, side_)
print(f"[dw] pass 8 lanterns: {len(LIGHTS8)} lights ({time.time() - T0:.0f}s)")

def add(n, prop, x, z, yaw_w, s, role):
    if COUNT[n][role] >= CAPS[role]:
        return False
    ok, why, data = evaluate(n, prop, x, z, yaw_w, s, role)
    if not ok or not budget_ok(prop, x, z, owner=n) or not budget_ok(prop, x, z, n, role):
        return False
    INST[n].append(commit(n, prop, x, z, yaw_w, s, role, data, "added"))
    COUNT[n][role] += 1
    STATS[n]["added"] += 1
    return True


# pass 6: H7 (barest hole) gets a fixed extra set of cheap, low ground cover + mid props BEFORE the seed pass. Its
# near field and H8's (which covers all of H7) are shared with H6/H8/H9 dressing; placing these first spreads the
# cost thinly over the other holes' lowest-priority seed items instead of starving one hole.
H7_BEFORE = len(INST[7])
rnd = random.Random(1707)
tee, aim = tee_frame(7)
right = np.array([-aim[2], 0, aim[0]])
_caps_saved = dict(CAPS)
CAPS.update(dict(CAPS, near=CAPS["near"] + REFILL_H7["near_extra"], mid=CAPS["mid"] + REFILL_H7["mid_extra"]))
for want, rng_t, rng_u, dlim, pool, role in (
        (REFILL_H7["near_extra"], (-2, 45), (1, 13), (1.4, 4.5), ["grass_tuft", "fern_clump", "red_leaf_bush",
                                                               "gold_leaf_bush", "fern_clump", "mossy_boulder",
                                                               "orange_leaf_bush", "leaf_pile"], "near"),
        (REFILL_H7["mid_extra"], (0, 45), (3, 14), (2.0, 7.0), ["mossy_boulder", "fern_clump_large", "gold_leaf_bush"],
         "mid")):
    tries, got = 0, 0
    while got < want and tries < 2000:
        tries += 1
        t = rnd.uniform(*rng_t)
        u = rnd.choice((-1, 1)) * rnd.uniform(*rng_u)
        p = tee + aim * t + right * u
        d = felt_dist_world(7, p[0], p[2])
        if not (dlim[0] <= d <= dlim[1]):
            continue
        if add(7, rnd.choice(pool), p[0], p[2], rnd.uniform(0, 360), rnd.uniform(0.85, 1.15), role):
            got += 1
CAPS.clear()
CAPS.update(_caps_saved)
print(f"[dw] H7 extra (pre-seed) ground cover: +{len(INST[7]) - H7_BEFORE} instances ({time.time() - T0:.0f}s)")

# pass 7: H8 'Firefly Hollow' read bare (13 props, none glowing near the alcove). Cheap firefly clusters / swarms,
# glow-shroom patches and glowing surface roots (props_pass7, role 'hollow', 128..250 tris each) are placed BEFORE
# the seed pass (after the H7 extras), around the alcove first, then the lane sides, the climb and the green. The near
# fields are zero-sum: placed after the seed pass (iteration 2) only 1 of 24 fitted (H6/H7/H8 near fields are full), so
# they go first and the cost lands on the lowest-priority seed items of the shared near fields. See pass7_vs_pass6.
H8_BEFORE = len(INST[8])
HOLLOW_PLAN = [   # (prop, hole-local centre (x, z), r range or None for a rect (x0, x1, z0, z1), want, tag)
    ("firefly_swarm", (8.5, -11.5), (2.0, 8.0), 2, "alcove"),
    ("glow_root_arch", (8.5, -11.5), (2.0, 7.0), 3, "alcove"),
    ("glow_shroom_patch", (8.5, -11.5), (1.5, 7.0), 2, "alcove"),
    ("firefly_cluster_low", (8.5, -11.5), (2.0, 9.0), 3, "alcove"),
    # iteration 2 (tee render): the alcove sits behind the right rails -> a group in the open ground just past the
    # junction's back rail, straight down the tee view
    ("firefly_swarm", (2.0, -20.0), (0.0, 4.5), 1, "junction_back"),
    ("glow_shroom_patch", (2.0, -20.0), (0.0, 4.5), 2, "junction_back"),
    ("firefly_cluster_low", (2.0, -20.0), (0.0, 4.5), 1, "junction_back"),
    ("firefly_cluster_low", (6.5, -4.0), (0.0, 3.5), 2, "lane_right"),
    ("glow_shroom_patch", (6.5, -4.0), (0.0, 3.5), 1, "lane_right"),
    ("firefly_swarm", (-2.0, -23.0), (0.0, 8.0), 1, "middle"),
    ("glow_root_arch", (-2.0, -23.0), (0.0, 8.0), 1, "middle"),
    ("glow_shroom_patch", (-2.0, -23.0), (0.0, 8.0), 1, "middle"),
    ("firefly_cluster_low", (-2.0, -23.0), (0.0, 8.0), 1, "middle"),
]
# (dropped: a climb patch + cluster at (-22.4, -26), a swarm 9-13 from the cup and a lane-left patch + cluster beside
# the tee: they sit in H7's full near field, cost H6 ground cover and are outside the tee view)
HOLLOW_GOT = {}


def hollow_trim(n, q, role):
    """Pass 7: what pays for the Firefly Hollow in the full H7/H8 near fields (instead of H6's thin ground cover):
    H8's own framing trees BEHIND its tee (local z > 4, never in the tee view) and the heavy 984-tri
    toadstool_trio_small ground cover of H8/H9 (seed roles near/mid)."""
    if n == 8 and role == "tree" and local_of(8, [q["x"], 0, q["z"]])[2] > 4.0:
        return True
    return n in (8, 9) and role in ("near", "mid") and q["prop"] == "toadstool_trio_small"


rnd = random.Random(808)
for prop_, (cx, cz), (r0, r1), want, tag in HOLLOW_PLAN:
    got, tries = 0, 0
    while got < want and tries < 600:
        tries += 1
        a, rr = rnd.uniform(0, math.tau), rnd.uniform(r0, r1)
        pw = DL.to_world(HM[8], [cx + math.cos(a) * rr, 0.0, cz + math.sin(a) * rr])
        if add(8, prop_, pw[0], pw[2], rnd.uniform(0, 360), rnd.uniform(0.9, 1.1), "hollow"):
            INST[8][-1]["marks"] = f"firefly_hollow:{tag}"
            got += 1
    HOLLOW_GOT[f"{tag}:{prop_}"] = f"{got}/{want}"
print(f"[dw] H8 Firefly Hollow (pre-seed): +{len(INST[8]) - H8_BEFORE} instances {HOLLOW_GOT} "
      f"({time.time() - T0:.0f}s)")


for role_key in ROLE_SEQ:
    role = "tree" if role_key == "tree1" else role_key
    active = True
    while active:
        active = False
        for n in H_ORDER:
            if not queues[role][n]:
                continue
            if role_key == "tree1" and COUNT[n]["tree"] >= TREE_FIRST:
                continue
            active = True
            q = queues[role][n].pop(0)
            st = STATS[n]
            if role in ("near", "mid") and template(q["prop"])["tris"] > HEAVY_SMALL:
                if HEAVY[n] >= HEAVY_CAP:
                    st["removed"] += 1
                    bump(st["removed_by"], "budget:heavy_small_prop")
                    REMOVED[n].append(dict(prop=q["seed"]["prop"], role=q["seed"]["role"], reason="budget:heavy_small_prop"))
                    continue
            if COUNT[n][role] >= CAPS[role]:
                st["removed"] += 1
                bump(st["removed_by"], "budget:role_cap")
                REMOVED[n].append(dict(prop=q["seed"]["prop"], role=q["seed"]["role"], reason="budget:role_cap"))
                continue
            if hollow_trim(n, q, role):
                st["removed"] += 1
                bump(st["removed_by"], "pass7_trim:firefly_hollow")
                REMOVED[n].append(dict(prop=q["seed"]["prop"], role=q["seed"]["role"], reason="pass7_trim:firefly_hollow",
                                       world_pos=[round(q["x"], 1), round(q["z"], 1)]))
                continue
            x, z, data, why, moved = try_with_nudge(n, q["prop"], q["x"], q["z"], q["yaw_w"], q["s"], role)
            if data is None:
                st["removed"] += 1
                bump(st["removed_by"], why)
                REMOVED[n].append(dict(prop=q["seed"]["prop"], role=q["seed"]["role"], reason=why,
                                       world_pos=[round(q["x"], 1), round(q["z"], 1)]))
                continue
            if not budget_ok(q["prop"], x, z, owner=n):
                st["removed"] += 1
                bump(st["removed_by"], "budget:near_field_tris")
                REMOVED[n].append(dict(prop=q["seed"]["prop"], role=q["seed"]["role"], reason="budget:near_field_tris"))
                continue
            if not budget_ok(q["prop"], x, z, n, role):
                st["removed"] += 1
                bump(st["removed_by"], "budget:own_role_share")
                REMOVED[n].append(dict(prop=q["seed"]["prop"], role=q["seed"]["role"], reason="budget:own_role_share"))
                continue
            extra = {}
            if q["convert"]:
                status = "card_from_backdrop"
                st["converted_to_card"] += 1
                extra["replaces"] = q["seed"]["prop"]
            elif moved:
                status = "moved"
            else:
                status = "kept"
            if moved:
                extra.update(moved_by=round(moved, 2), moved_because=why)
                if not q["convert"]:
                    st["moved"] += 1
                bump(st["moved_because"], why)
            elif not q["convert"]:
                st["kept"] += 1
            INST[n].append(commit(n, q["prop"], x, z, q["yaw_w"], q["s"], role, data, status, extra))
            COUNT[n][role] += 1
            if role in ("near", "mid") and template(q["prop"])["tris"] > HEAVY_SMALL:
                HEAVY[n] += 1
print(f"[dw] seed pass done ({time.time() - T0:.0f}s) near loads {NEAR_LOAD}")



# ----------------------------------------------------------------------------- refill
def felt_dist_all(x, z):
    return min(felt_dist_world(m, x, z) for m in HM)


REFILL = dict(cards_view=12, trees_min=7, near_min=30, hooks_min=2)
for n in HM:
    if n == 9:
        continue
    rnd = random.Random(900 + n)
    tee, aim = tee_frame(n)
    right = np.array([-aim[2], 0, aim[0]])
    th = THEME[n]
    # far-field cards across the tee view (so the view never ends in bare ground)
    pts = []
    for _ in range(500):
        ang = math.radians(rnd.uniform(-55, 55))
        dist = rnd.uniform(45, 110)
        d = aim * math.cos(ang) + right * math.sin(ang)
        p = tee + d * dist
        pts.append(p)
    k = 0
    for p in pts:
        if k >= REFILL["cards_view"]:
            break
        if felt_dist_world(n, p[0], p[2]) < CARD_MIN_D or felt_dist_all(p[0], p[2]) < 26:
            continue
        if add(n, rnd.choice(CARD_COL[th]), p[0], p[2], rnd.uniform(0, 360), rnd.uniform(1.0, 1.35), "card"):
            k += 1
    # framing trees where removals left gaps
    tries = 0
    while COUNT[n]["tree"] < REFILL["trees_min"] and tries < 500:
        tries += 1
        t = rnd.uniform(-2, 40)
        u = rnd.choice((-1, 1)) * rnd.uniform(5, 22)
        p = tee + aim * t + right * u
        d = felt_dist_world(n, p[0], p[2])
        if not (3.0 <= d <= 22):
            continue
        add(n, rnd.choice(TREES[th]), p[0], p[2], rnd.uniform(0, 360), rnd.uniform(0.9, 1.15), "tree")
    # lantern hooks beside the lane (the concepts' hanging lanterns), facing along the nearest felt edge
    tries = 0
    while COUNT[n]["hook"] < REFILL["hooks_min"] and tries < 400:
        tries += 1
        t = rnd.uniform(2, 35)
        u = rnd.choice((-1, 1)) * rnd.uniform(5, 12)
        p = tee + aim * t + right * u
        d = felt_dist_world(n, p[0], p[2])
        if not (4.0 <= d <= 6.5):          # pass 5: hooks are tall (4.6) -> >= 3 back from the rails
            continue
        add(n, "lantern_hook_pair", p[0], p[2], math.degrees(math.atan2(aim[0], aim[2])) - 90, 1.0, "hook")
    # ground cover along the rails, tee view first
    tries = 0
    while COUNT[n]["near"] < REFILL["near_min"] and tries < 1200:
        tries += 1
        t = rnd.uniform(0, 30) if tries < 600 else rnd.uniform(0, 50)
        u = rnd.choice((-1, 1)) * rnd.uniform(1, 12)
        p = tee + aim * t + right * u
        d = felt_dist_world(n, p[0], p[2])
        if not (1.4 <= d <= 4.5):
            continue
        add(n, rnd.choice(CHEAP_NEAR), p[0], p[2], rnd.uniform(0, 360), rnd.uniform(0.85, 1.15), "near")

# H9: glowing mushrooms, ferns and tiny toadstools along the inside of the trunk wall
rnd = random.Random(909)
door_a = math.radians(TREE["doorway"]["angle_deg"])
tries = 0
while COUNT[9]["interior"] < CAPS["interior"] and tries < 1500:
    tries += 1
    a = rnd.uniform(0, math.tau)
    if abs((a - door_a + math.pi) % math.tau - math.pi) < math.radians(14):
        continue
    rr = rnd.uniform(R_IN - 3.2, R_IN - 1.2)
    x, z = TO[0] + math.cos(a) * rr, TO[2] + math.sin(a) * rr
    nm = rnd.choice(["glowing_mushrooms", "glowing_mushrooms", "glow_shroom_patch", "glow_shroom_patch", "fern_clump",
                     "toadstool_trio_small"])      # pass 7: + glow_shroom_patch (~210 tris vs 2,040)
    add(9, nm, x, z, rnd.uniform(0, 360), rnd.uniform(0.8, 1.1), "interior")
print(f"[dw] refill done ({time.time() - T0:.0f}s); foreign shares in protected near fields {FOREIGN}")


# ----------------------------------------------------------------------------- FBX groups (hole frame)
def inst_matrix_bl(it):
    x, y, z = it["pos"]
    s = it["scale"]
    return Matrix.Translation(lglib.R(x, y, z)) @ Matrix.Rotation(math.radians(it["yaw"]), 4, "Z") @ Matrix.Diagonal((s, s, s, 1))


def export_group(name, insts):
    col = bpy.data.collections.new(name)
    sc.collection.children.link(col)
    acc = {}
    scratch = bpy.data.meshes.new("_scr")
    for it in insts:
        T = template(it["prop"])
        Mx = inst_matrix_bl(it)
        for o in T["objs"]:
            m = lglib.mat_of(o.name)
            tb = bmesh.new()
            tb.from_mesh(o.data)
            bmesh.ops.transform(tb, matrix=Mx, verts=tb.verts)
            tb.to_mesh(scratch)
            tb.free()
            acc.setdefault(m, bmesh.new()).from_mesh(scratch)
    root = bpy.data.objects.new(name, None)
    col.objects.link(root)
    objs = []
    for m, b in sorted(acc.items()):
        me = bpy.data.meshes.new(f"{name}__{m}")
        b.to_mesh(me)
        b.free()
        me.materials.append(lglib.get_mat(m))
        ob = bpy.data.objects.new(f"{name}__{m}", me)
        col.objects.link(ob)
        ob.parent = root
        objs.append(ob)
    for c in sc.collection.children:
        sc.view_layers[0].layer_collection.children[c.name].exclude = (c.name != name)
    bpy.ops.object.select_all(action="DESELECT")
    for o in [root] + objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(OUT, "fbx", f"{name}.fbx"), use_selection=True, apply_scale_options="FBX_SCALE_UNITS",
        global_scale=1.0, axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True, add_leaf_bones=False,
        bake_anim=False, mesh_smooth_type="FACE", use_mesh_modifiers=True, object_types={"EMPTY", "MESH"},
        use_custom_props=False)
    tris = lglib.tri_count(objs)
    parts = [dict(mesh=o.name, material=lglib.mat_of(o.name), tris=lglib.tri_count([o])) for o in objs]
    for o in objs:
        bpy.data.meshes.remove(o.data)
    bpy.data.objects.remove(root)
    bpy.data.collections.remove(col)
    return tris, parts


ORDER = ["accent", "hang", "rail", "span", "string", "hook", "tree", "far", "mid", "near", "interior", "hollow",
         "card"]
man_path = os.path.join(OUT, "manifest.json")
manifest = json.load(open(man_path))
out = {}
# ----------------------------------------------------------------------------- pass 5: light spots
# PointLights pooling over the moving parts of the dark holes (H8 under the root arch, H9 inside the tree) and over
# their cups. Hung SPOT_H above the part's felt (above the 6.5 play clearance, so an invisible host part / Attachment
# never enters a keep-out); checked against every keep-out box and the world occupancy, shifted if needed.
SPOT_H = 7.0
# data-driven: one spot over EVERY moving part of H8/H9 (holes.json may rename / replace them), one over each cup
SPOT_DEFS = {
    8: [(m["id"], "moving_part", "#FFE6B8", 16.0, 2.5) for m in HM[8]["moving_parts"]] +
       [("cup", "cup_pool", "#FFC873", 12.0, 2.0)],
    9: [(m["id"], "moving_part", "#FFE6B8", 16.0, 2.5) for m in HM[9]["moving_parts"]] +
       [("cup", "cup_pool", "#FFC873", 12.0, 2.0),
        # iteration 2: H9 still read dark from the tee -> warm fills over the main felt areas inside the tree
        ("felt:lane", "lane_fill", "#FFE2B0", 18.0, 1.5), ("felt:landing", "lane_fill", "#FFE2B0", 18.0, 1.5),
        ("felt:chamber", "lane_fill", "#FFE2B0", 18.0, 1.5), ("felt:heart", "lane_fill", "#FFE2B0", 18.0, 1.5)],
}


SPOTS = {n: [] for n in HM}
for n, defs in SPOT_DEFS.items():
    h = HM[n]
    for tid, kind, col, rng, bri in defs:
        if tid == "cup":
            base = np.array(h["cup"]["position"], float)
        elif tid.startswith("felt:"):
            f_ = ([f for f in h["felt"] if f["id"] == tid[5:]] or [None])[0]
            if f_ is None:
                continue
            base = np.array([f_["center"][0], DL.felt_top(f_), f_["center"][2]], float)
        else:
            mp = [m for m in h["moving_parts"] if m["id"] == tid][0]
            # pool over the felt under the pivot (pendulums etc. hang from a pivot high above the lane)
            base = np.array(mp["pivot"], float)
            under = [r[5] for r in DL.felt_rects(h) if DL.rect_dist(np.array([base[0]]), np.array([base[2]]), r)[0] <= 0]
            if under:
                base[1] = max(under)
        chosen, shift = None, None
        if tid != "cup" and not tid.startswith("felt:") and mp["type"] == "swing":
            # pass 6: pendulum -> hang the spot BESIDE the hinge, off the swing plane (along the swing axis), at hinge
            # height: clear of the swept bob + chain and of the root beam, still >= 6.5 above the felt under it
            piv = np.array(mp["pivot"], float)
            ax = np.array(mp["axis"], float)
            for off in (2.0, -2.0, 2.5, -2.5, 3.0, -3.0):
                lp = piv + ax * off
                pw = DL.to_world(h, lp)
                in_tree = np.hypot(pw[0] - TO[0], pw[2] - TO[2]) < R_IN - 0.3
                if lp[1] - base[1] >= WF.CLEAR and not ko_hits(np.array([pw])) and \
                        not OCC.hits(np.array([pw]), first_only=True) and (in_tree or n != 9):
                    chosen, shift = (lp, pw), (round(abs(off), 2), round(float(lp[1] - base[1]), 2))
                    break
        if tid == "cup":
            # pass 7: the bigger pennant was blown out by a cup spot hanging ~1 stud from it -> hang the cup spot on
            # the side of the pole AWAY from the pennant, >= 1.8 from it (still within 0.7 x range of the cup)
            fpl = REG[f"cup_flag_h{n:02d}"]["placements"][0]
            bdir = DL.yaw_mat(fpl["yaw"]) @ np.array([1.0, 0.0, 0.0])
            for off, dy in ((2.0, SPOT_H), (2.5, SPOT_H), (2.0, 6.5), (3.0, SPOT_H)):
                lp = base - bdir * off + np.array([0, dy, 0])
                pw = DL.to_world(h, lp)
                in_tree = np.hypot(pw[0] - TO[0], pw[2] - TO[2]) < R_IN - 0.3
                if not ko_hits(np.array([pw])) and not OCC.hits(np.array([pw]), first_only=True) and (in_tree or n != 9):
                    chosen, shift = (lp, pw), (off, dy)
                    break
        for dy in (() if chosen else (SPOT_H, 7.5, 8.0, 9.0)):
            for r in (0.0, 1.0, 2.0, 3.0):
                for k in range(8 if r else 1):
                    a = math.tau * k / 8
                    lp = base + np.array([math.cos(a) * r, dy, math.sin(a) * r])
                    pw = DL.to_world(h, lp)
                    in_tree = np.hypot(pw[0] - TO[0], pw[2] - TO[2]) < R_IN - 0.3
                    if not ko_hits(np.array([pw])) and not OCC.hits(np.array([pw]), first_only=True) and \
                            (in_tree or n != 9):
                        chosen, shift = (lp, pw), (round(r, 2), dy)
                        break
                if chosen:
                    break
            if chosen:
                break
        if chosen is None:
            lp = base + np.array([0, SPOT_H, 0])
            chosen, shift = (lp, DL.to_world(h, lp)), None
        lp, pw = chosen
        SPOTS[n].append(dict(id=f"H{n}_{tid.replace('felt:', '')}_{kind}", over=tid, kind=kind, light="PointLight",
                             pos=[round(float(v), 2) for v in lp], world_pos=[round(float(v), 2) for v in pw],
                             color=col, range=rng, brightness=bri, shadows=False,
                             height_above_target=shift[1] if shift else None,
                             lateral_shift=shift[0] if shift else None, clear=shift is not None))
    print(f"[dw] H{n} spot lights: {[(q['id'], q['clear'], q['lateral_shift']) for q in SPOTS[n]]}")

# pass 7: soft firefly-green glow over the H8 firefly swarms (alcove first), so the hollow reads at night
FF_SPOTS = 3
FF_GLOW = dict(range=14.0, brightness=3.5)       # pass 8: was range 12, Brightness 2.0 (brighter emissives)
for k, it in enumerate([q for q in INST[8] if q["prop"] == "firefly_swarm"][:FF_SPOTS]):
    for dy in (2.4, 2.0, 2.8, 1.6):
        lp = np.array(it["pos"], float) + [0, dy, 0]
        pw = DL.to_world(HM[8], lp)
        if not ko_hits(np.array([pw])) and not OCC.hits(np.array([pw]), first_only=True):
            SPOTS[8].append(dict(id=f"H8_firefly_swarm_{k + 1}_firefly_glow", over=f"firefly_swarm:{k + 1}",
                                 kind="firefly_glow", light="PointLight", pos=[round(float(v), 2) for v in lp],
                                 world_pos=[round(float(v), 2) for v in pw], target_pos=it["pos"],
                                 marks=it.get("marks"), color="#D8FF6A", range=FF_GLOW["range"],
                                 brightness=FF_GLOW["brightness"], shadows=False,
                                 height_above_target=dy, lateral_shift=0.0, clear=True))
            break
print(f"[dw] H8 firefly spots: {[q['id'] for q in SPOTS[8] if q['kind'] == 'firefly_glow']}")

# pass 8: H8 reads more magical: every other H8 glow prop gets a soft PointLight of its own colour (manifest.lights[],
# parented to the prop's Neon part, ~1 above its base), on top of the brighter Firefly / ShroomGlow emission
GLOW8 = {"firefly_cluster_low": ("firefly_glow_low", "#D8FF6A", [216, 255, 106], 8.0, 1.6, 1.0),
         "glow_shroom_patch": ("shroom_glow", "#7FE3D0", [127, 227, 208], 8.0, 1.4, 0.9),
         "glow_root_arch": ("shroom_glow", "#7FE3D0", [127, 227, 208], 8.0, 1.4, 0.8),
         "glowing_mushrooms": ("shroom_glow", "#7FE3D0", [127, 227, 208], 10.0, 1.6, 1.1)}
for k, it in enumerate(q for q in INST[8] if q["prop"] in GLOW8):
    kind, col, rgb, rng, bri, dy = GLOW8[it["prop"]]
    lid = f"H8_{kind}_{k + 1:02d}"
    it["light_id"] = lid
    light_entry(8, lid, kind, np.array(it["pos"], float) + [0, dy, 0], col, rgb, rng, bri, prop=it["prop"],
                target_pos=it["pos"], parent=f"the Neon {'Firefly' if 'firefly' in kind else 'ShroomGlow'} part of "
                                            "this instance")
print(f"[dw] pass 8 lights: {len(LIGHTS8)} ({sum(1 for q in LIGHTS8 if q['hole'] == 'H8')} on H8)")

# ----------------------------------------------------------------------------- pass 5: tall-near-rail before/after
OLD = json.load(open(os.path.join(SRC, "manifest_before_pass5.json"))).get("dressing", {}).get("holes", {})
TALL5 = {}
for n in HM:
    viol = []
    for it in OLD.get(f"H{n}", {}).get("instances", []):
        T = template(it["prop"])
        s_ = it["scale"]
        if T["height"] * s_ <= TALL_H:
            continue
        Rm = DL.yaw_mat(it["world_yaw"])
        wp = np.array(it["world_pos"], float)
        bases = []
        for (bx, bz, br) in T["bases"]:
            c = wp + Rm @ np.array([bx * s_, 0, bz * s_])
            bases.append((c[0], c[2], br * s_))
        P = T["v"] * s_ @ Rm.T + wp
        if not tall_rail_clear(T, s_, bases, P, wp[1]):
            viol.append(it)
    moved, removed, props = 0, 0, {}
    for it in viol:
        near = [q for q in INST[n] if q["prop"] == it["prop"] and
                math.hypot(q["world_pos"][0] - it["world_pos"][0], q["world_pos"][2] - it["world_pos"][2]) < 12.0]
        if near:
            moved += 1
        else:
            removed += 1
        props[it["prop"]] = props.get(it["prop"], 0) + 1
    TALL5[n] = dict(pass4_violators=len(viol), moved_back=moved, removed=removed, violators_by_prop=props,
                    now_moved_because_rule=sum(1 for q in INST[n] if q.get("moved_because") == "tall_near_rail"),
                    now_removed_because_rule=STATS[n]["removed_by"].get("tall_near_rail", 0))
    print(f"[dw] H{n} tall_near_rail: {TALL5[n]}")

# ----------------------------------------------------------------------------- pass 6: before/after vs pass 5
_P5 = os.path.join(SRC, "manifest_before_pass6.json")
OLD6 = json.load(open(_P5)).get("dressing", {}).get("holes", {}) if os.path.exists(_P5) else {}
P6 = {}
for n in HM:
    old = OLD6.get(f"H{n}", {}).get("instances", [])
    new = list(INST[n])
    used = set()
    kept = moved = removed = 0
    for it in old:
        best, bd = None, 1e9
        for j, q in enumerate(new):
            if j in used or q["prop"] != it["prop"]:
                continue
            dd = math.hypot(q["world_pos"][0] - it["world_pos"][0], q["world_pos"][2] - it["world_pos"][2])
            if dd < bd:
                best, bd = j, dd
        if best is not None and bd < 12.0:
            used.add(best)
            if bd < 0.05 and abs(new[best]["world_pos"][1] - it["world_pos"][1]) < 0.05:
                kept += 1
            else:
                moved += 1
        else:
            removed += 1
    ost = OLD6.get(f"H{n}", {}).get("stats", {})
    P6[n] = dict(pass5_instances=len(old), unchanged=kept, moved=moved, removed=removed, added=len(new) - len(used),
                 instances_after=len(new),
                 pass5_3d=ost.get("final_3d"), pass5_cards=ost.get("final_cards"),
                 pass5_tris=ost.get("tris_after"), pass5_near_field_tris=ost.get("near_field_tris_after"))
    print(f"[dw] H{n} vs pass 5: {P6[n]}")

# ----------------------------------------------------------------------------- pass 7: before/after vs pass 6
_P6 = os.path.join(SRC, "manifest_before_pass7.json")
OLD7 = json.load(open(_P6)).get("dressing", {}).get("holes", {}) if os.path.exists(_P6) else {}
P7 = {}
for n in HM:
    old = OLD7.get(f"H{n}", {}).get("instances", [])
    new = list(INST[n])
    used, kept, moved, gone = set(), 0, 0, []
    for it in old:
        best, bd = None, 1e9
        for j, q in enumerate(new):
            if j in used or q["prop"] != it["prop"]:
                continue
            dd = math.hypot(q["world_pos"][0] - it["world_pos"][0], q["world_pos"][2] - it["world_pos"][2])
            if dd < bd:
                best, bd = j, dd
        if best is not None and bd < 12.0:
            used.add(best)
            if bd < 0.05 and abs(new[best]["world_pos"][1] - it["world_pos"][1]) < 0.05:
                kept += 1
            else:
                moved += 1
        else:
            gone.append(f"{it['prop']} ({it['role']}, {template(it['prop'])['tris'] if it['prop'] in REG else '?'} tris)")
    ost = OLD7.get(f"H{n}", {}).get("stats", {})
    P7[n] = dict(pass6_instances=len(old), unchanged=kept, moved=moved, removed=len(gone), removed_props=gone,
                 added=len(new) - len(used), added_props=sorted(new[j]["prop"] for j in range(len(new)) if j not in used),
                 instances_after=len(new), pass6_tris=ost.get("tris_after"),
                 pass6_near_field_tris=ost.get("near_field_tris_after"))
    print(f"[dw] H{n} vs pass 6: {P7[n]}")

# ----------------------------------------------------------------------------- pass 7b: plants vs pass 7
_P7 = os.path.join(SRC, "manifest_before_pass7b.json")
OLD7B = json.load(open(_P7)).get("dressing", {}).get("holes", {}) if os.path.exists(_P7) else {}
P7B = {}
for n in HM:
    old = OLD7B.get(f"H{n}", {}).get("instances", [])
    new = list(INST[n])
    viol, gaps_old = [], []
    for it in old:
        if it["prop"] not in PLANTS:
            continue
        g = rail_gap_tris(template(it["prop"])["T"] * it["scale"] @ DL.yaw_mat(it["world_yaw"]).T +
                          np.array(it["world_pos"], float), PLANT_CLEAR + 1.0)
        gaps_old.append(g)
        if g < PLANT_CLEAR - 1e-6:
            viol.append((it, g))
    used, kept, moved, gone, moved_l, gone_l = set(), 0, 0, [], [], []
    for it in old:
        best, bd = None, 1e9
        for j, q in enumerate(new):
            if j in used or q["prop"] != it["prop"]:
                continue
            dd = math.hypot(q["world_pos"][0] - it["world_pos"][0], q["world_pos"][2] - it["world_pos"][2])
            if dd < bd:
                best, bd = j, dd
        lim_ = 4.5 if it["prop"] in PLANTS else 12.0
        if best is not None and bd < lim_:
            used.add(best)
            if bd < 0.05 and abs(new[best]["world_pos"][1] - it["world_pos"][1]) < 0.05:
                kept += 1
            else:
                moved += 1
                if it["prop"] in PLANTS:
                    moved_l.append(f"{it['prop']} {bd:.2f}")
        else:
            gone.append(f"{it['prop']} ({it['role']})")
            if it["prop"] in PLANTS:
                gone_l.append(it["prop"])
    vio_ids = {id(it) for it, _ in viol}
    plants_new = [q for q in new if q["prop"] in PLANTS]
    ost = OLD7B.get(f"H{n}", {}).get("stats", {})
    P7B[n] = dict(pass7_instances=len(old), pass7_plants=sum(1 for it in old if it["prop"] in PLANTS),
                  pass7_plant_violations=len(viol),
                  pass7_violators=[f"{it['prop']} gap {g:.2f}" for it, g in sorted(viol, key=lambda v: v[1])],
                  pass7_min_plant_gap=round(min(gaps_old), 3) if gaps_old else None,
                  plants_after=len(plants_new),
                  min_plant_gap_after=round(min(q["rail_gap"] for q in plants_new), 3) if plants_new else None,
                  plants_moved=len(moved_l), plants_moved_list=moved_l, plants_removed=len(gone_l),
                  plants_removed_list=gone_l, unchanged=kept, moved=moved, removed=len(gone), removed_props=gone,
                  added=len(new) - len(used),
                  added_props=sorted(new[j]["prop"] for j in range(len(new)) if j not in used),
                  instances_after=len(new), seed_moved_because_rule=sum(
                      1 for q in new if q.get("moved_because") == "plant_near_rail"),
                  seed_removed_because_rule=STATS[n]["removed_by"].get("plant_near_rail", 0),
                  pass7_tris=ost.get("tris_after"), pass7_near_field_tris=ost.get("near_field_tris_after"))
    print(f"[dw] H{n} vs pass 7 (plants): {P7B[n]}")

# ----------------------------------------------------------------------------- pass 8: vs pass 7b
_P7B = os.path.join(SRC, "manifest_before_pass8.json")
OLD8 = json.load(open(_P7B)).get("dressing", {}).get("holes", {}) if os.path.exists(_P7B) else {}
P8S = {}
for n in HM:
    old = OLD8.get(f"H{n}", {}).get("instances", [])
    new = list(INST[n])
    used, kept, moved, gone = set(), 0, 0, []
    for it in old:
        best, bd = None, 1e9
        for j, q in enumerate(new):
            if j in used or q["prop"] != it["prop"]:
                continue
            dd = math.hypot(q["world_pos"][0] - it["world_pos"][0], q["world_pos"][2] - it["world_pos"][2])
            if dd < bd:
                best, bd = j, dd
        if best is not None and bd < 4.5:
            used.add(best)
            if bd < 0.05 and abs(new[best]["world_pos"][1] - it["world_pos"][1]) < 0.05:
                kept += 1
            else:
                moved += 1
        else:
            gone.append(f"{it['prop']} ({it['role']}, {template(it['prop'])['tris'] if it['prop'] in REG else '?'} tris)")
    ost = OLD8.get(f"H{n}", {}).get("stats", {})
    P8S[n] = dict(pass7b_instances=len(old), unchanged=kept, moved=moved, removed=len(gone), removed_props=gone,
                  added=len(new) - len(used),
                  added_props=sorted(new[j]["prop"] for j in range(len(new)) if j not in used),
                  lanterns_added=sum(1 for q in new if q["role"] in ("rail", "hang")),
                  lantern_tris=sum(template(q["prop"])["tris"] for q in new if q["role"] in ("rail", "hang")),
                  instances_after=len(new), pass7b_tris=ost.get("tris_after"),
                  pass7b_near_field_tris=ost.get("near_field_tris_after"))
    print(f"[dw] H{n} vs pass 7b: {P8S[n]}")

for fn in os.listdir(os.path.join(OUT, "fbx")):
    if fn.startswith("dressing_h"):
        os.remove(os.path.join(OUT, "fbx", fn))
for n in HM:
    h = HM[n]
    insts = sorted(INST[n], key=lambda it: (ORDER.index(it["role"]), it["prop"]))
    near = [it for it in insts if it["role"] != "card"]
    cards = [it for it in insts if it["role"] == "card"]
    groups, cur, ct = [], [], 0
    for it in near:
        t = template(it["prop"])["tris"]
        if cur and ct + t > TRI_FILE:
            groups.append(cur)
            cur, ct = [], 0
        cur.append(it)
        ct += t
    if cur:
        groups.append(cur)
    files = []
    for gi, g in enumerate(groups):
        nm = f"dressing_h{n:02d}_{'abcdefghijklmnop'[gi]}"
        tris, parts = export_group(nm, g)
        files.append(dict(fbx=f"fbx/{nm}.fbx", kind="near_field_3d", triangles=tris, instances=len(g), parts=parts))
    if cards:
        nm = f"dressing_h{n:02d}_cards"
        tris, parts = export_group(nm, cards)
        files.append(dict(fbx=f"fbx/{nm}.fbx", kind="far_field_cards", triangles=tris, instances=len(cards), parts=parts))
    lights, lights_w = [], []
    for it in insts:
        T = template(it["prop"])
        if it.get("light_id"):          # pass 8 lanterns: their PointLight is in manifest.lights[] instead
            continue
        for c in T["lights"]:
            p = DL.transform_verts(np.array([c]), it["pos"], it["yaw"], it["scale"])[0]
            lights.append([round(float(v), 2) for v in p])
            lights_w.append([round(float(v), 2) for v in DL.to_world(h, p)])
    own3d = sum(template(it["prop"])["tris"] for it in near)
    own_cards = sum(template(it["prop"])["tris"] for it in cards)
    own_near = sum(template(it["prop"])["tris"] for it in insts if felt_dist_world(n, *it["world_pos"][::2]) < NEAR_D)
    st = STATS[n]
    st.update(final_instances=len(insts), final_3d=len(near), final_cards=len(cards),
              tris_before=tris_before[n], tris_after=own3d + own_cards, tris_after_3d=own3d, tris_after_cards=own_cards,
              near_field_tris_before=NEAR_LOAD_BEFORE[n], near_field_tris_after=NEAR_LOAD[n],
              near_field_own_tris_after=own_near, counts={k: v for k, v in COUNT[n].items() if v},
              pass5_tall_near_rail=TALL5[n], pass6_vs_pass5=dict(P6[n], tris_after=own3d + own_cards,
                                                                  near_field_tris_after=NEAR_LOAD[n],
                                                                  final_3d=len(near), final_cards=len(cards)),
              pass7_vs_pass6=dict(P7[n], tris_after=own3d + own_cards, near_field_tris_after=NEAR_LOAD[n]),
              pass7b_vs_pass7=dict(P7B[n], tris_after=own3d + own_cards, near_field_tris_after=NEAR_LOAD[n]),
              pass8_vs_pass7b=dict(P8S[n], tris_after=own3d + own_cards, near_field_tris_after=NEAR_LOAD[n]))
    out[f"H{n}"] = dict(theme=THEME[n], placement=dict(origin=h["world_offset"], yaw_deg=h["world_yaw"]),
                        stats=st, triangles=own3d + own_cards, instances=insts, fbx=files, lights=lights,
                        lights_world=lights_w, spot_lights=SPOTS[n], removed=REMOVED[n])
    print(f"[dw] H{n}: seed {st['seed']} kept {st['kept']} moved {st['moved']} cards {st['converted_to_card']} "
          f"removed {st['removed']} added {st['added']} | tris {tris_before[n]} -> {own3d + own_cards} | near-field "
          f"{NEAR_LOAD_BEFORE[n]} -> {NEAR_LOAD[n]} | {st['removed_by']}")

tot = {k: sum(STATS[n][k] for n in HM) for k in ("seed", "kept", "moved", "converted_to_card", "removed", "added",
                                                  "tris_before", "tris_after")}
rb = {}
for n in HM:
    for k, v in STATS[n]["removed_by"].items():
        rb[k] = rb.get(k, 0) + v
tot["removed_by"] = dict(sorted(rb.items(), key=lambda kv: -kv[1]))
manifest["dressing"] = dict(
    note=("Pass 4 (world-corrected) set dressing. Every instance has world_pos [x, y, z] (y = base on Terrain), "
          "world_yaw and terrain_y (terrain height under the origin), plus the hole-local pos/yaw (pos.y corrected "
          "to the same world height: world = holeRoot * local, holeRoot = CFrame.new(world.json origin) * "
          "CFrame.Angles(0, math.rad(yaw_deg), 0)). Preferred import: one Model per instance from fbx/<prop>.fbx, "
          "Model:PivotTo(CFrame.new(world_pos) * CFrame.Angles(0, math.rad(world_yaw), 0)); Model:ScaleTo(scale). "
          "Blockout alternative: fbx[] = the same instances merged per material (repeated pieces merged into a few "
          "MeshParts); ORIGIN CONVENTION: each dressing_hNN_* file is in the hole frame, origin = that hole's "
          "world.json placement origin, axes rotated by its yaw_deg -> Model:PivotTo(holeRoot). "
          "dressing_hNN_cards.fbx = far-field card clumps (alpha-cut textures). lights[] = glow-core centres "
          "(hole-local), lights_world[] = the same in world studs (PointLight Range 8, Brightness 0.6 day / 1.6 "
          "night, #FFB347). Terrain heights come from world/terrain-4stud.json (bilinear); if Studio Terrain "
          "differs, raycast down from world_pos + (0, 20, 0). Pass 5: role 'accent' = cup_lantern_stake beside "
          "the H8/H9 cups and the H9 root gate (marks = cup / root_gate). spot_lights[] (H8, H9) = extra PointLights "
          "pooling over the moving parts and cups: pos (hole-local), world_pos, color, range, brightness; host each "
          "on an invisible, non-colliding Attachment/Part at world_pos (all are >= 6.5 above the felt and outside "
          "every keep-out). Pass 6 (holes.json v2): the H9 lantern-bar spot is replaced by a spot beside the "
          "lantern_pendulum hinge (off the swing plane); H7 got a reserved share of its near field and an extra "
          "low-ground-cover / framing refill; stats.pass6_vs_pass5 = unchanged / moved / removed / added vs pass 5. "
          "Pass 7: H8 'Firefly Hollow' role 'hollow' (marks firefly_hollow:<area>) = firefly clusters / swarms, "
          "glow-shroom patches and glowing surface roots around the alcove, lane, climb and green, placed before "
          "the seed pass; H8 spot_lights kind 'firefly_glow' (over firefly_swarm:<k>, target_pos = the swarm's "
          "pos) sit ~2.4 above a swarm's base, off the felt, clear of every keep-out; stats.pass7_vs_pass6 lists "
          "what each hole gained / lost vs pass 6. "
          "Pass 7b: every plant instance (props[].category == 'plant', see rules.plant_rail_clearance) has rail_gap = "
          "exact horizontal distance from its whole mesh footprint to the nearest wall of any hole (>= 1.5; capped "
          "at 2.5, i.e. 2.5 means >= 2.5); "
          "stats.pass7b_vs_pass7 lists the pass-7 violators and the plants moved / removed. "
          "Pass 8: role 'hang' (H9 lantern_large_hanging, hanging=True: world_pos y = lantern bottom, 8 above the "
          "felt; NOT grounded, terrain_y is the ground under it) and role 'rail' (H7 rail_lantern_stake, H8 "
          "rail_lantern_crook; marks rail_lantern:<left|right>, wall, seq, chain_gap_before). Every one has "
          "light_id -> manifest.lights[] (its glow core is NOT repeated in lights[] / lights_world[]); H8 glow "
          "props also carry light_id. stats.pass8_vs_pass7b lists what each hole gained / lost."),
    budgets=dict(
        near_field_radius_studs=NEAR_D, near_field_tri_budget=NEAR_BUDGET,
        definition=("near-field tris of hole N = all dressing instances (any hole) whose origin lies within "
                    f"{NEAR_D:g} studs of hole N's felt. Target well under 40k for Quest; enforced <= {NEAR_BUDGET}."),
        far_field=("every pass-2 backdrop clump (tree_backdrop_cluster, 834 tris) is replaced by a card clump "
                   "(treeline_card_red / _gold, 3 crossed quads, 12 tris); refill beyond the near field uses cards "
                   f"only (>= {CARD_MIN_D:g} studs from their own felt, >= 26 from any felt)."),
        no_lods=("No separate LOD / far versions: Roblox auto-LODs MeshParts and streams nearby parts. Repeated "
                 "pieces are merged per material in the fbx[] groups."),
        role_caps_per_hole=CAPS, own_tri_share_per_hole=dict((k, v) for k, v in GROUP_BUDGET.items() if k != "card")),
    rules=dict(clear_above_felt=WF.CLEAR, felt_margin=DL.FELT_MARGIN, walkway_corridor="width/2 + 0.75, 6.5 high",
               ground=("footprint terrain spread <= 1.5 (small props, lantern poles), <= 3 (trees), <= 3.5 (cards); "
                       "no water cells"),
               tall_near_rail=(f"pass 5: every prop taller than {TALL_H:g} studs keeps its footprint and all geometry "
                               f"below base + {EYE_BAND:g} >= {RAIL_BACK:g} studs (horizontal) from every collision "
                               "wall (rails, backings, boards, deflectors) of every hole"),
               plant_rail_clearance=(f"pass 7b: every plant instance (category 'plant': {', '.join(sorted(PLANTS))}) "
                                     f"keeps its whole mesh footprint (every triangle projected to XZ) >= "
                                     f"{PLANT_CLEAR:g} studs (horizontal) from every rail / collision wall of every "
                                     "hole; violators are nudged outward (same role) or removed"),
               checked_by="_src/fitcheck.py (world dressing section) -> _src/fitcheck.txt",
               keepouts=__doc__.split("2. Clash test")[1].split("3. Ground")[0].strip()),
    totals=tot,
    holes=out,
)
uses = {}
for d in out.values():
    for it in d["instances"]:
        uses[it["prop"]] = uses.get(it["prop"], 0) + 1
manifest["dressing"]["prop_use_counts"] = dict(sorted(uses.items(), key=lambda kv: -kv[1]))
manifest["dressing"]["plant_props"] = sorted(PLANTS)
for p in manifest["props"]:
    p["dressing_uses"] = uses.get(p["name"], 0)
    p["category"] = registry.category(p["name"])          # pass 7b (also written by build_all via registry)
import hole_skins
manifest["hole_skins"] = hole_skins.manifest_block()      # pass 5 (also written by build_all via registry)
# pass 8: one flat list of the PointLights added / changed in pass 8 (lanterns + H8 glow), and the emissive boost
manifest["lights"] = LIGHTS8
manifest["lights_note"] = (
    "Pass 8 PointLights (one per entry): pos = hole-local, world_pos = world studs (same frame as dressing "
    "world_pos). Create a PointLight with Color = Color3.fromRGB(color3), Range, Brightness, Shadows = false and "
    "parent it to the Neon part named in 'parent' (or an invisible, non-colliding Attachment at world_pos). "
    "kind hanging_lantern (H9, lantern_large_hanging), rail_lantern (H7 rail_lantern_stake / H8 rail_lantern_crook): "
    "amber Color3(255, 169, 87) ~2700K; firefly_glow_low / shroom_glow (H8): soft glow over the firefly clusters and "
    "glow mushrooms. The H8 firefly_glow spot_lights (dressing.holes.H8.spot_lights) were raised to Brightness "
    f"{FF_GLOW['brightness']}, Range {FF_GLOW['range']:g} in pass 8 (not repeated here).")
manifest["emissive"] = dict(
    note=("Pass 8: brighter H8 glow. Firefly (fireflies, teleport rings, glowing-mushroom spots) and ShroomGlow "
          "(glow-mushroom caps) stay Neon with the same Color; preview emission Firefly 4 -> 8, ShroomGlow 3 -> 6. "
          "In Studio add a SurfaceAppearance to every *__Firefly / *__ShroomGlow MeshPart: ColorMap = the "
          "emissive texture, EmissiveMaskContent = glow_emissive_mask.png (white = all emissive), EmissiveStrength "
          "and EmissiveTint as below. If SurfaceAppearance emissive is unavailable, keep Neon and rely on the raised "
          "PointLights (spot_lights firefly_glow + lights[] firefly_glow_low / shroom_glow)."),
    materials={m: dict(color=lglib.MATS[m][0], roblox_material="Neon", preview_emission_before=b,
                       preview_emission=lglib.MATS[m][2], color_map=f"textures/{t}.png",
                       emissive_mask="textures/glow_emissive_mask.png", emissive_strength=es,
                       emissive_tint=lglib.MATS[m][0])
               for m, b, t, es in (("Firefly", 4.0, "firefly_emissive", 6.0),
                                   ("ShroomGlow", 3.0, "shroomglow_emissive", 5.0))})
json.dump(manifest, open(man_path, "w"), indent=1)
print(f"[dw] totals {tot}  ({time.time() - T0:.0f}s)")
