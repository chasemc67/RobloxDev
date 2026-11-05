"""Pass 3 fit check for the world-scale hero tree (and the computed rock-face placements).

  blender -b -P models/_src/world_fitcheck.py     -> models/world/fitcheck_world.txt

Re-imports the exported FBX files (so the check sees exactly what Studio gets), moves them to their world
placement (layout.json) and tests EVERY TRIANGLE (exact separating-axis test, not just vertices) against:
  * H9 + H8 (transformed with world.json placements): felt grown 1.25 up to felt top + 6.5, collision walls grown 0.4,
    hazards, moving-part sweeps (blockers + hero visual bbox through the full motion, +0.5), teleports, tee pad +
    8-stud run-up, hero props placed on those holes;
  * walkways p_h7_h8 and p_h8_h9 (width/2 + 0.75 per side, 6.5 high; 12 high near the Heartwood Door) and their
    lantern posts.
Plus: radial clearance of the inner wall vs H9's footprint, ray casts along the door walkway (1..11 studs high,
+-3.5 sideways) and negative tests (a triangle on H9 felt / in the lantern-bar sweep / in the door corridor must be
flagged). Also: every world FBX < 20k tris.
"""
import bpy, sys, os, json, math, glob
import numpy as np

SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC)
import world_fit as WF

MODELS = WF.MODELS
OUTD = os.path.join(MODELS, "world")
W = WF.load_world()
LAY = json.load(open(os.path.join(OUTD, "layout.json")))
TREE = W["hollow_tree"]
O = np.array(TREE["center"], float)
lines = []
fails = 0


def check(name, ok, detail=""):
    global fails
    fails += 0 if ok else 1
    s = f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else "")
    lines.append(s)
    print(s)


def load_tris(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y")
    T = []
    n = 0
    for o in bpy.context.scene.objects:
        if o.type != "MESH":
            continue
        me = o.data
        me.calc_loop_triangles()
        mw = np.array(o.matrix_world)
        V = np.array([v.co[:] for v in me.vertices], float)
        V = V @ mw[:3, :3].T + mw[:3, 3]
        idx = np.array([t.vertices[:] for t in me.loop_triangles], int)
        n += len(idx)
        if len(idx):
            T.append(V[idx])
    T = np.concatenate(T) if T else np.zeros((0, 3, 3))
    # Blender (x, y, z) -> Roblox (x, z, -y)
    R = np.stack([T[..., 0], T[..., 2], -T[..., 1]], axis=-1)
    return R, n


def place(R, inst):
    a = math.radians(inst.get("yaw", 0.0))
    c, s = math.cos(a), math.sin(a)
    S = np.array(inst.get("scale", [1, 1, 1]), float)
    L = R * S
    x = L[..., 0] * c + L[..., 2] * s
    z = -L[..., 0] * s + L[..., 2] * c
    p = inst["pos"]
    return np.stack([x + p[0], L[..., 1] + p[1], z + p[2]], axis=-1)


def ray_tri(orig, d, T):
    """Moller-Trumbore, returns min t > 0 or inf."""
    v0, v1, v2 = T[:, 0], T[:, 1], T[:, 2]
    e1, e2 = v1 - v0, v2 - v0
    p = np.cross(d, e2)
    det = (e1 * p).sum(1)
    ok = np.abs(det) > 1e-9
    inv = np.where(ok, 1.0 / np.where(ok, det, 1), 0)
    tv = orig - v0
    u = (tv * p).sum(1) * inv
    q = np.cross(tv, e1)
    v = (q * d).sum(1) * inv
    t = (e2 * q).sum(1) * inv
    hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)
    return t[hit].min() if hit.any() else np.inf


# ----------------------------------------------------------------------------- load hero tree
H = WF.holes_world(W)
hole_boxes = WF.hole_obbs(H, numbers=(8, 9))
path_boxes = WF.path_obbs(W, ids=("p_h7_h8", "p_h8_h9"), door_center=O)
post_boxes = [b for b in WF.lantern_obbs(W) if "p_h8_h9" in b.label or "p_h7_h8" in b.label]
lines.append(f"Hero tree fit vs H8/H9 (holes.json transformed with world.json placements) and walkways p_h7_h8/p_h8_h9")
lines.append(f"keep-out boxes: {len(hole_boxes)} hole elements, {len(path_boxes)} walkway segments, {len(post_boxes)} lantern posts")
lines.append("")
files = sorted(glob.glob(os.path.join(OUTD, "fbx", "hollow_tree_world_shell*.fbx"))) + \
    sorted(glob.glob(os.path.join(OUTD, "fbx", "hollow_tree_crown*.fbx")))
ALL = []
for f in files:
    pid = "hollow_tree_crown" if "crown" in f else "hollow_tree_world_shell"
    R, n = load_tris(f)
    Tw = place(R, LAY[pid][0])
    ALL.append(Tw)
    hits = WF.check_tris(Tw, hole_boxes + path_boxes + post_boxes)
    check(f"{os.path.basename(f)}: {n} tris, no triangle inside any H8/H9/walkway/post keep-out", not hits,
          ", ".join(f"{k} x{v}" for k, v in list(hits.items())[:8]))
TA = np.concatenate(ALL)

# radial clearance: inner wall vs H9 footprint (felt + walls, no margins)
h9 = [h for h in H if h["number"] == 9][0]
import dressing_lib as DL
corners = []
for el, key in [(f, "felt") for f in h9["felt"]] + [(w, "wall") for w in h9["walls"]]:
    sx, sz = (el["size"][0], el["size"][1]) if key == "felt" else (el["size"][0], el["size"][2])
    for ux in (-1, 1):
        for uz in (-1, 1):
            lp = np.array(el["center"], float) + DL.yaw_mat(el.get("yaw", 0)) @ np.array([ux * sx / 2, 0, uz * sz / 2])
            corners.append(DL.to_world(h9, lp))
corners = np.array(corners)
r_fp = np.hypot(corners[:, 0] - O[0], corners[:, 2] - O[2]).max()
shell = np.concatenate([place(load_tris(f)[0], LAY["hollow_tree_world_shell"][0])
                        for f in files if "shell_part" in f and any(f"part{k}" in f for k in (1, 2, 3, 4))])
low = shell[(shell[..., 1].max(1) < O[1] + 8)]
c = low.mean(1)
rr = np.hypot(c[:, 0] - O[0], c[:, 2] - O[2])
# inner wall triangles = those facing the centre, outside the door bore
door_a = math.radians(TREE["doorway"]["angle_deg"])
ang = np.arctan2(c[:, 2] - O[2], c[:, 0] - O[0])
away = np.abs((ang - door_a + np.pi) % (2 * np.pi) - np.pi) > math.radians(16)
vr = np.hypot(low[..., 0] - O[0], low[..., 2] - O[2]).min(1)
r_inner = vr[away & (rr < 42)].min()
check(f"inner wall (lowest 8 studs, outside the door bore) r >= H9 footprint r + 4.5", r_inner >= r_fp + 4.5,
      f"inner wall min r {r_inner:.2f}, H9 felt+walls max r {r_fp:.2f}, walking room {r_inner - r_fp:.2f}")

# door: rays along the walkway through the doorway at several heights / lateral offsets
p = [q for q in W["paths"] if q["id"] == "p_h8_h9"][0]
segs = [s for s in p["segments"] if s["type"] == "walk"][-2:]
a = np.array(segs[0]["start"], float)
b = np.array(segs[-1]["end"], float)
d = b - a
L = np.linalg.norm(d)
d /= L
side = np.array([d[2], 0, -d[0]])
blocked = []
for off in (-3.5, -2.0, 0.0, 2.0, 3.5):
    for hgt in (0.6, 2.0, 4.0, 6.0, 8.0, 11.0):
        o = a + side * off + np.array([0, hgt, 0]) - d * 2.0
        t = ray_tri(o, d, TA)
        if t < L + 2.0:
            blocked.append(f"off {off} h {hgt}: hit at {t:.1f}")
check(f"Heartwood Door: 30 rays along p_h8_h9 ({L:.1f} studs from {a.round(1).tolist()} through the arch to "
      f"{b.round(1).tolist()}, 7 wide, up to 11 high) are unobstructed", not blocked, "; ".join(blocked[:5]))
# door opening size at the outer face (measure free width / height in the door plane)
dd = np.array([math.cos(door_a), 0, math.sin(door_a)])
tv = np.array([-dd[2], 0, dd[0]])
base = O + dd * (TREE["trunk_outer_radius"] + 4)
free_w = []
for u in np.arange(-8, 8.01, 0.25):
    o = base + tv * u + np.array([0, 1.0, 0])
    free_w.append(ray_tri(o, -dd, TA) > 14)
free_w = np.array(free_w)
us = np.arange(-8, 8.01, 0.25)[free_w]
w_open = us.max() - us.min() + 0.25 if len(us) else 0
hs = []
for hgt in np.arange(0.5, 24, 0.25):
    o = base + np.array([0, hgt, 0])
    if ray_tri(o, -dd, TA) > 14:
        hs.append(hgt)
h_open = max(hs) if hs else 0
check("door opening at the outer face ~14 wide x ~20 high", 13.0 <= w_open <= 15.5 and 18.5 <= h_open <= 21.5,
      f"free width {w_open:.2f} at 1 above the floor, free height {h_open:.2f} at the centreline")

# negative tests: the checker must flag these
felt = [f for f in h9["felt"] if f["id"] == "lane"][0]
fc = DL.to_world(h9, [felt["center"][0], felt["center"][1] + 0.5, felt["center"][2]])
neg1 = np.array([[fc + [-0.5, 0, 0], fc + [0.5, 0, 0], fc + [0, 0.5, 0.5]]])
# pass 6: holes.json v2 replaced the lantern bar with the lantern pendulum (bob 7 below the hinge)
mp = [m for m in h9["moving_parts"] if m["id"] in ("lantern_pendulum", "lantern_bar")][0]
pc = DL.to_world(h9, np.array(mp["pivot"]) + ([0, -7.0, 0] if mp["type"] == "swing" else [2.5, 0.5, 0]))
neg2 = np.array([[pc + [-0.2, 0, 0], pc + [0.2, 0, 0], pc + [0, 0.3, 0]]])
dc = O + dd * (TREE["trunk_outer_radius"]) + np.array([0, 9.0, 0])
neg3 = np.array([[dc + tv * -1, dc + tv * 1, dc + [0, 1, 0]]])
for nm, t in (("triangle on H9 lane felt", neg1), ("triangle in the lantern-pendulum sweep", neg2),
              ("triangle in the door corridor at 9 studs", neg3)):
    hits = WF.check_tris(t, hole_boxes + path_boxes + post_boxes)
    check(f"negative test flagged: {nm}", bool(hits), ", ".join(list(hits)[:2]))

# rock faces placed by world_layout must not cover any hole / walkway either
lines.append("")
allholes = WF.hole_obbs(H) + WF.path_obbs(W) + WF.lantern_obbs(W)
for pid in sorted(k for k in LAY if k.startswith(("terrace_rock_faces", "highland_cliff_kit", "grand_falls", "twin_falls",
                                                  "lantern_falls", "mere_dock", "sister_tree", "old_lantern", "hill_mush"))):
    fp = os.path.join(OUTD, "fbx", f"{pid}.fbx")
    if not os.path.exists(fp):
        continue
    R, n = load_tris(fp)
    bad = {}
    for inst in LAY[pid]:
        bad.update(WF.check_tris(place(R, inst), allholes))
    check(f"{pid} x{len(LAY[pid])}: clear of every hole, walkway and lantern post", not bad,
          ", ".join(f"{k} x{v}" for k, v in list(bad.items())[:6]))

# tri budget
lines.append("")
over = []
cnt = 0
for f in sorted(glob.glob(os.path.join(OUTD, "fbx", "*.fbx"))):
    R, n = load_tris(f)
    cnt += 1
    if n >= 20000:
        over.append(f"{os.path.basename(f)} {n}")
check(f"all {cnt} world FBX files < 20k tris", not over, ", ".join(over))
lines.append("")
lines.append(f"{'ALL PASS' if fails == 0 else str(fails) + ' FAIL(S)'}")
open(os.path.join(OUTD, "fitcheck_world.txt"), "w").write("\n".join(lines) + "\n")
