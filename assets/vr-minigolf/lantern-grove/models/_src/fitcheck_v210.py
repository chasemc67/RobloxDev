"""v210 fit checks (H8 door pocket x1.4 / +0.17 / 0.05 deeper; H9 timber OakDeep #7A4E32, Reflectance 0).
Run: LG_HOLES_JSON=<holes.json> blender -b --factory-startup -P models/_src/fitcheck_v210.py -- [--shipped <dir>]
  --shipped: the models/fbx dir as delivered before v210 (byte-identity of the FBX that must not change).
Writes _src/fitcheck_v210.txt.

The v210 job only ships holes.json + the H8/H9 FBX (no world/, no other FBX), so the full fitcheck.py chain
(pass 4..10, 235 checks) cannot run here: its world / dressing / per-FBX sections need world/world.json, the terrain
and ~100 FBX that are not in the job. This script runs everything that CAN run on the shipped data:
  A. fitcheck.py sections 1-6 (generator-only rules: tunnels, bridges, moving parts vs blockers, hollow tree);
  B. fitcheck_pass6.py section 3 (H8 door + pockets, entry/exit rings, alcove cladding) and the tee -> flag-top
     sightline rule, in the holes.json hole-local frame (the pass-6 code is exec'd unchanged);
  C. new v210 rules on the re-imported FBX, with negative tests.
"""
import bpy, sys, os, math, json, hashlib

SRC = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.dirname(SRC)
_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SHIPPED = _argv[_argv.index("--shipped") + 1] if "--shipped" in _argv else None

# ---------------------------------------------------------------------------- A. fitcheck.py sections 1-6
_fc = open(os.path.join(SRC, "fitcheck.py")).read()
_cut = _fc.index("# ============================================================================ pass 4: world dressing")
lines_hdr = ["# A. fitcheck.py sections 1-6 (generator-only rules)"]
exec(compile(_fc[:_cut], "fitcheck.py[1-6]", "exec"))
lines[:0] = lines_hdr

import numpy as np
import dressing_lib as DL
import world_fit as WF

man = json.load(open(os.path.join(OUTD, "manifest.json")))
HM = {h["number"]: h for h in DL.load_holes()}          # hole-local frame (the pass-6 rules below only use local data)
HOLES_PATH = os.environ.get("LG_HOLES_JSON") or os.path.join(os.path.dirname(OUTD), "holes.json")

# ---------------------------------------------------------------------------- B. pass-6 rules (unchanged code)
_p6 = open(os.path.join(SRC, "fitcheck_pass6.py")).read()
_i1 = _p6.index("# ---------------------------------------------------------------------------- 1. moving parts")
_i3 = _p6.index("# ---------------------------------------------------------------------------- 3. H8 door + pockets")
_i4 = _p6.index("# ---------------------------------------------------------------------------- 4. flags")
_s0 = _p6.index("# tee -> flag sightline vs every hero prop")
_s1 = _p6.index("# pass 7: the pennant itself")
exec(compile(_p6[:_i1], "fitcheck_pass6.py[helpers]", "exec"))
lines.append("# B. fitcheck_pass6.py section 3 + tee sightline (hole-local)")
exec(compile(_p6[_i3:_i4], "fitcheck_pass6.py[3]", "exec"))
exec(compile(_p6[_s0:_s1], "fitcheck_pass6.py[4:sightline]", "exec"))

# ---------------------------------------------------------------------------- C. v210
lines.append("")
lines.append("# C. v210: H8 door pocket (X x1.4, +0.17, 0.05 deeper) + H9 timber OakDeep #7A4E32 Reflectance 0")
import props_pass6 as _P6
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

MB = json.load(open(os.path.join(SRC, "manifest_before_v210.json")))
PB_ = {p["name"]: p for p in MB["props"]}
PA_ = {p["name"]: p for p in man["props"]}
ORIG = os.path.join(SRC, "fbx_before_v210")
CHANGED = ("h8_door_pocket", "timber_deflector_board", "bank_backing_stone")
MIN_CLR = 0.187


def lin2hex(c):
    s = [(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055) for v in c[:3]]
    return "#" + "".join(f"{max(0, min(255, round(v * 255))):02X}" for v in s)


def fbx_parts(path):
    """{part: dict(V=Roblox verts (prop frame), T=Roblox tris, color=hex of the FBX material base colour)}"""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y")
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    out = {}
    for o in new:
        if o.type != "MESH":
            continue
        me = o.data
        me.calc_loop_triangles()
        mw = np.array(o.matrix_world)
        V = np.array([v.co[:] for v in me.vertices], float) @ mw[:3, :3].T + mw[:3, 3]
        V = np.stack([V[:, 0], V[:, 2], -V[:, 1]], -1)
        idx = np.array([t.vertices[:] for t in me.loop_triangles], int)
        col = None
        if me.materials and me.materials[0] and me.materials[0].node_tree:
            bs = next((n for n in me.materials[0].node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if bs:
                col = lin2hex(bs.inputs["Base Color"].default_value)
        out[o.name.split(".")[0]] = dict(V=V, T=V[idx], color=col)
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    return out


def same_points(A, B, tol=1e-4):
    if len(A) != len(B):
        return False, float("inf")
    kd = KDTree(len(B))
    for i, p in enumerate(B):
        kd.insert(Vector(p), i)
    kd.balance()
    d = max(kd.find(Vector(p))[2] for p in A)
    return d <= tol, d


NEW = {n: fbx_parts(os.path.join(OUTD, "fbx", f"{n}.fbx")) for n in CHANGED}
OLD = {n: fbx_parts(os.path.join(ORIG, f"{n}.fbx")) for n in CHANGED}

# C1. pocket mesh == original mesh scaled X x1.4 about the origin, +0.17 up, 0.05 deeper (local -Z, away from door)
xf = lambda V: V * [_P6.POCKET_SX, 1, 1] + [0, _P6.POCKET_RAISE, -_P6.POCKET_DEEPER]
res = {k: same_points(NEW["h8_door_pocket"][k]["V"], xf(OLD["h8_door_pocket"][k]["V"]), 2e-4)
       for k in OLD["h8_door_pocket"]}
check("v210 h8_door_pocket FBX == pre-v210 FBX x1.4 in X about the origin, +0.17 Y, -0.05 local Z (every vertex, "
      "every part)", set(NEW["h8_door_pocket"]) == set(OLD["h8_door_pocket"]) and all(r[0] for r in res.values()),
      "max dev " + ", ".join(f"{k.split('__')[1]} {v[1]:.1e}" for k, v in res.items()))
pa, pb_ = PA_["h8_door_pocket"], PB_["h8_door_pocket"]
dc = np.array(pa["bbox_center_from_origin"]) - pb_["bbox_center_from_origin"]
check("v210 h8_door_pocket manifest: placement + origin unchanged; bbox X 1.4x, Y/Z sizes same, centre +0.17 Y / "
      "-0.05 Z (local) / X same", pa["placements"] == pb_["placements"] and pa["origin"] == pb_["origin"] and
      abs(pa["bbox_size_studs"][0] - 1.4 * pb_["bbox_size_studs"][0]) <= 0.003 and
      np.allclose(pa["bbox_size_studs"][1:], pb_["bbox_size_studs"][1:], atol=0.002) and
      np.allclose(dc, [_P6.POCKET_SX * pb_["bbox_center_from_origin"][0] - pb_["bbox_center_from_origin"][0], 0.17, -0.05],
                  atol=0.002), f"size {pb_['bbox_size_studs']} -> {pa['bbox_size_studs']}, centre shift {np.round(dc, 3).tolist()}")
pl = pa["placements"][0]
yaw_ok = pl["yaw"] == 180 and pl["pos"][2] > HM[8]["moving_parts"][0]["pivot"][2]
check("v210 'deeper' = away from the door: pocket yaw 180 sits on the +Z side of the door pivot, so local -Z = world "
      "+Z = the door's opening direction (axis +Z)", yaw_ok and [m for m in HM[8]["moving_parts"]
                                                                   if m["id"] == "root_door"][0]["axis"] == [0, 0, 1],
      f"pocket pos {pl['pos']} yaw {pl['yaw']}")
Vp = np.concatenate([p["V"] for p in NEW["h8_door_pocket"].values()])
check("v210 h8_door_pocket still reaches below the felt (no gap under the raised walls)", Vp[:, 1].min() <= 0.0,
      f"min y {Vp[:, 1].min():.3f}")

# C2. door <-> pocket clearance over the whole slide (exact meshes from the FBX, dense edge sampling, both ways)
_door = [m for m in HM[8]["moving_parts"] if m["id"] == "root_door"][0]
_ax = np.array(_door["axis"], float)


def _yaw(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _place(T, pl):
    return T @ _yaw(pl.get("yaw", 0)).T + np.asarray(pl["pos"], float)


def _samples(T, sp=0.005):
    P = [T.reshape(-1, 3)]
    for i, j in ((0, 1), (1, 2), (2, 0)):
        A, B = T[:, i], T[:, j]
        L = np.linalg.norm(B - A, axis=1)
        for k in range(len(T)):
            n = int(L[k] / sp)
            if n > 1:
                P.append(A[k] + (B[k] - A[k]) * (np.arange(1, n) / n)[:, None])
    return np.unique(np.round(np.concatenate(P), 6), axis=0)


def _bvh(T):
    return BVHTree.FromPolygons([Vector(v) for v in T.reshape(-1, 3)], [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(T))])


def sweep(Tp, Td, coarse=0.01, fine=0.0005):
    Sd, Sp = _samples(Td), _samples(Tp)
    Bd, Bp = _bvh(Td), _bvh(Tp)
    pmn, pmx = Tp.reshape(-1, 3).min(0), Tp.reshape(-1, 3).max(0)

    def clr(off, cut=0.6):
        sh = _ax * off
        best = (1e9, None, None)
        D = Sd + sh
        for p in D[np.all((D > pmn - cut) & (D < pmx + cut), axis=1)]:
            r = Bp.find_nearest(Vector(p))
            if r[0] is not None and r[3] < best[0]:
                best = (r[3], tuple(p), tuple(r[0]))
        dmn, dmx = Td.reshape(-1, 3).min(0) + sh, Td.reshape(-1, 3).max(0) + sh
        for p in Sp[np.all((Sp > dmn - cut) & (Sp < dmx + cut), axis=1)]:
            r = Bd.find_nearest(Vector(p - sh))
            if r[0] is not None and r[3] < best[0]:
                best = (r[3], tuple(np.array(r[0]) + sh), tuple(p))
        return best
    lo, hi = _door["range"]
    cs = [(float(o), clr(o)[0]) for o in np.round(np.arange(lo, hi + 1e-9, coarse), 5)]
    o0 = min(cs, key=lambda t: t[1])[0]
    fs = [(float(o), clr(o)) for o in np.round(np.arange(max(lo, o0 - 2 * coarse), min(hi, o0 + 2 * coarse) + 1e-9, fine), 6)]
    ob, (d, pd, pp) = min(fs, key=lambda t: t[1][0])
    return dict(min=float(d), offset=ob, door_point=pd, pocket_point=pp, n_coarse=len(cs), n_fine=len(fs),
                profile=cs)


_Td = _place(np.concatenate([p["T"] for p in fbx_parts(os.path.join(OUTD, "fbx", "h8_root_door.fbx")).values()]),
             PA_["h8_root_door"]["placements"][0])
_Tp = _place(np.concatenate([p["T"] for p in NEW["h8_door_pocket"].values()]), pl)
SW = sweep(_Tp, _Td)
_sd = {k: v for k, v in SW.items() if k != "profile"}
_sd["profile_every_0.1"] = [[o, round(c, 4)] for o, c in SW["profile"][::10] if c < 1e8]
json.dump(_sd, open(os.path.join(SRC, "door_pocket_sweep_v210.json"), "w"), indent=1)
check(f"v210 H8 root door <-> h8_door_pocket mesh clearance >= {MIN_CLR} over the whole slide "
      f"[{_door['range'][0]:g}, {_door['range'][1]:g}] ({SW['n_coarse']} offsets at 0.01 + {SW['n_fine']} at 0.0005 "
      "around the minimum; 0.005 edge sampling both ways)", SW["min"] >= MIN_CLR,
      f"min {SW['min']:.4f} at offset {SW['offset']:.4f} (door {np.round(SW['door_point'], 3).tolist()} -> pocket "
      f"{np.round(SW['pocket_point'], 3).tolist()})")
# negative tests: the pre-v210 pocket, and the pocket moved 0.05 TOWARD the door instead of away
_To = _place(np.concatenate([p["T"] for p in OLD["h8_door_pocket"].values()]), pl)
SWo = sweep(_To, _Td, coarse=0.02)
check(f"negative test flagged: pre-v210 pocket (clearance < {MIN_CLR})", SWo["min"] < MIN_CLR,
      f"min {SWo['min']:.4f} at offset {SWo['offset']:.4f}")
SWw = sweep(_Tp - _ax * 0.10, _Td, coarse=0.02)
check(f"negative test flagged: pocket moved 0.05 toward the door instead of away (clearance < {MIN_CLR})",
      SWw["min"] < MIN_CLR, f"min {SWw['min']:.4f} at offset {SWw['offset']:.4f}")

# C3. H9 timber colour / reflectance; stone + everything else unchanged
for n, stone in (("timber_deflector_board", None), ("bank_backing_stone", "bank_backing_stone__Limestone")):
    e = PA_[n]
    od = [q for q in e["parts"] if q["material"] == "OakDeep"]
    ok = (len(od) == 1 and od[0]["color"] == "#7A4E32" and od[0].get("reflectance") == 0 and
          od[0]["roblox_material"] == "WoodPlanks" and not any(q["material"] == "Oak" for q in e["parts"]) and
          NEW[n].get(f"{n}__OakDeep", {}).get("color") == "#7A4E32" and f"{n}__Oak" not in NEW[n])
    check(f"v210 {n}: oak timber part = {n}__OakDeep, colour #7A4E32 (manifest + FBX material), Roblox Reflectance 0, "
          "no __Oak part left", ok, f"manifest {[(q['mesh'], q['color'], q.get('reflectance')) for q in od]}, "
                                    f"FBX {NEW[n].get(f'{n}__OakDeep', {}).get('color')}")
    geo = {k: same_points(NEW[n][k]["V"], OLD[n][k.replace("__OakDeep", "__Oak")]["V"], 1e-4) for k in NEW[n]}
    check(f"v210 {n}: geometry unchanged (every part incl. the timber == pre-v210 FBX)", all(g[0] for g in geo.values()),
          ", ".join(f"{k.split('__')[1]} {v[1]:.1e}" for k, v in geo.items()))
    keep = [q for q in e["parts"] if q["material"] != "OakDeep"]
    kb = {q["mesh"]: q for q in PB_[n]["parts"]}
    check(f"v210 {n}: non-timber parts keep their colour/material (manifest + FBX)" +
          (" - stone faces stay Limestone #B8AFA0 in their own part" if stone else ""),
          all(q == kb.get(q["mesh"]) for q in keep) and all(NEW[n][q["mesh"]]["color"] == q["color"] for q in keep)
          and (stone is None or [q["color"] for q in keep if q["mesh"] == stone] == ["#B8AFA0"]),
          ", ".join(f"{q['mesh'].split('__')[1]} {q['color']}" for q in keep))
check("negative test flagged: the pre-v210 timber_deflector_board FBX fails the colour rule (__Oak #8A5A33)",
      "timber_deflector_board__OakDeep" not in OLD["timber_deflector_board"] and
      OLD["timber_deflector_board"]["timber_deflector_board__Oak"]["color"] != "#7A4E32",
      f"old __Oak {OLD['timber_deflector_board']['timber_deflector_board__Oak']['color']}")

# C4. tris, manifest consistency, nothing else touched
tri_ok = {n: (sum(len(p["T"]) for p in NEW[n].values()), PA_[n]["triangles"]) for n in CHANGED}
check("v210 changed FBX < 20k tris and manifest triangles == FBX", all(a == b and a < 20000 for a, b in tri_ok.values()),
      str(tri_ok))
others = [n for n in PB_ if n not in CHANGED]
diff = [n for n in others if PA_.get(n) != PB_[n]]
check("v210 every other manifest prop entry identical to pre-v210 (incl. h8_root_door, rail kit, H9 props)",
      not diff and set(PA_) == set(PB_), f"{len(others)} entries compared; differ: {diff}")
_top = [k for k in MB if k not in ("props", "textures") and MB[k] != man.get(k)]
_tx = (set(man["textures"]["untextured"]) - set(MB["textures"]["untextured"]),
       {k: v for k, v in man["textures"].items() if k != "untextured" and MB["textures"].get(k) != v})
check("v210 manifest top-level blocks preserved (dressing, world, lights, emissive, h9_emissive_dim, ...); textures "
      "block only gains OakDeep as untextured", not _top and _tx == ({"OakDeep"}, {}), f"changed {_top}, textures {_tx}")
if SHIPPED:
    keep_f = [f for f in os.listdir(SHIPPED) if f.endswith(".fbx") and f[:-4] not in CHANGED]
    same = {f: open(os.path.join(SHIPPED, f), "rb").read() == open(os.path.join(OUTD, "fbx", f), "rb").read()
            for f in keep_f}
    check("v210 unchanged FBX byte-identical to the shipped ones (door, H8/H9 dressing)", all(same.values()),
          ", ".join(f"{k} {'same' if v else 'DIFF'}" for k, v in same.items()))
_hs = hashlib.sha256(open(HOLES_PATH, "rb").read()).hexdigest()[:16]
_r16 = [w for w in HM[8]["walls"] if w["id"] == "rail16"][0]
check("v210 holes.json read only (rail16 / banks untouched): rail16 still centre (6.5, 1.7, -7.75) size 0.5x4.4x6",
      _r16["center"] == [6.5, 1.7, -7.75] and _r16["size"] == [0.5, 4.4, 6.0], f"sha256 {_hs}")

# ---------------------------------------------------------------------------- write
nf = sum(1 for l in lines if l.startswith("FAIL"))
npass = sum(1 for l in lines if l.startswith("PASS"))
hdr = [f"# Lantern Grove v210 fitcheck ({'ALL PASS' if nf == 0 else f'{nf} FAIL'}, {npass + nf} checks) - Blender "
       f"{bpy.app.version_string}; holes.json {HOLES_PATH} (sha256 {_hs})",
       "# NOT RUN here (inputs not in the v210 job): fitcheck.py pass 4/5 world-dressing sections and fitcheck_pass6-10",
       "# sections that need world/world.json, terrain, world_occ or FBX not shipped (dressing H1-H7, pendulum, bracer,",
       "# ...). The 2 H9 props keep their exact geometry (C3), so only colour changed for them; the H8 pocket mesh grew",
       "# (C1) - world keep-out sets that include it were not re-run here.",
       f"# door <-> pocket sweep: min {SW['min']:.4f} at slide offset {SW['offset']:.4f} (pre-v210 {SWo['min']:.4f})", ""]
out = "\n".join(hdr + lines)
print(out)
open(os.path.join(SRC, "fitcheck_v210.txt"), "w").write(out + "\n")
