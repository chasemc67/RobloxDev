"""v210b fit checks (playtest round 8: bank backings render as stone; game-art H9: oak rails + mint bank lip).
Run: LG_HOLES_JSON=<holes.json> blender -b --factory-startup -P models/_src/fitcheck_v210b.py -- --shipped <dir>
  --shipped: the FBX as they were before v210b (v210 output + the 3 job FBX) for byte identity / before counts.
Writes _src/fitcheck_v210b.txt and _src/coplanar_v210b.json.

Runs the latest suite first, unchanged: fitcheck_v210.py sections A (fitcheck.py 1-6), B (pass-6 section 3 + tee
sightline) and C1-C2 (H8 door pocket). The v210 C3/C4 rules (bank_backing_stone cap = OakDeep, every other entry
identical to pre-v210) are superseded by section D below. Same input limits as v210 (no world/, ~100 FBX missing).
"""
import bpy, sys, os, math, json, hashlib

SRC = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.dirname(SRC)
_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SHIPPED_B = _argv[_argv.index("--shipped") + 1] if "--shipped" in _argv else None
sys.argv = [a for a in sys.argv if a != "--shipped" and a != SHIPPED_B]     # v210 part must not see --shipped

sys.path.insert(0, SRC)
import props_v210b          # registers h9_bank_lip before fitcheck.py snapshots the registry (sightline rule sees it)
_v = open(os.path.join(SRC, "fitcheck_v210.py")).read()
exec(compile(_v[:_v.index("# C3. H9 timber colour")], "fitcheck_v210.py[A,B,C1,C2]", "exec"))

import numpy as np
import importlib
import lglib
import registry
for _m in ("props_dressing", "props_moving", "props_hero", "props_p2p3", "props_variants", "props_cards",
           "props_pass6", "props_pass7", "props_pass8", "props_pass10", "props_v210b"):
    importlib.import_module(_m)
import bankfit_v210b as BF
import coplanar_v210b as CP
import hole_skins
import props_v210b as PV

lines.append("")
lines.append("# D. v210b: bank backings stone (H3/H8/H9), H8 alcove cladding stone, H9 oak rails + limestone posts, "
             "H9 bank lip #6CC79F")
MB2 = json.load(open(os.path.join(SRC, "manifest_before_v210b.json")))
PB2 = {p["name"]: p for p in MB2["props"]}
HJ = json.load(open(HOLES_PATH))
_hs = hashlib.sha256(open(HOLES_PATH, "rb").read()).hexdigest()[:16]
_hs_v210 = open(os.path.join(SRC, "fitcheck_v210_validated.txt")).readline().split("sha256 ")[1].split(")")[0]
HOLE = {h["number"]: h for h in HJ["holes"]}
FB = os.path.join(OUTD, "fbx")
OLD2 = os.path.join(SRC, "fbx_before_v210b")
STONE_HEX, OAK_HEX, LIP_HEX = "#B8AFA0", "#7A4E32", "#6CC79F"
CHANGED_B = ("bank_backing_stone", "h8_alcove_bank_cladding")
NEW_B = ("rail_straight_4_h9", "rail_straight_2_h9", "rail_end_post_h9", "h9_bank_lip")
TRIM_META = ("rail_straight_4_trim", "rail_straight_2_trim", "rail_end_post_trim")
mat_of = lambda part: part.split("__", 1)[1]


def fbx_mats(path):
    """fbx_parts + emission of each FBX material."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y")
    new = [o for o in bpy.data.objects if o not in before]
    em = {}
    for o in new:
        if o.type == "MESH" and o.data.materials and o.data.materials[0] and o.data.materials[0].node_tree:
            bs = next((n for n in o.data.materials[0].node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if bs:
                em[o.name.split(".")[0]] = float(bs.inputs["Emission Strength"].default_value) * \
                    max(bs.inputs["Emission Color"].default_value[:3])
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    return em


def subset(A, B, tol=1e-4):
    """max distance from each point of A to its nearest point of B."""
    kd = KDTree(len(B))
    for i, p in enumerate(B):
        kd.insert(Vector(p), i)
    kd.balance()
    return max(kd.find(Vector(p))[2] for p in A)


N2 = {n: fbx_parts(os.path.join(FB, f"{n}.fbx")) for n in CHANGED_B + NEW_B}
O2 = {n: fbx_parts(os.path.join(OLD2, f"{n}.fbx")) for n in CHANGED_B}
PA2 = {p["name"]: p for p in json.load(open(os.path.join(OUTD, "manifest.json")))["props"]}

# ---- D1 bank_backing_stone: one stone part, blocks unchanged, cap encloses a rail-kit cap by 0.02, moss was buried
bn, bo = N2["bank_backing_stone"], O2["bank_backing_stone"]
e = PA2["bank_backing_stone"]
check("v210b bank_backing_stone renders stone only: one part __Limestone #B8AFA0 (manifest + FBX material), no "
      "OakDeep / Oak / Moss part", list(bn) == ["bank_backing_stone__Limestone"] and
      [(q["mesh"], q["color"], q["roblox_material"]) for q in e["parts"]] ==
      [("bank_backing_stone__Limestone", STONE_HEX, "Limestone")] and bn["bank_backing_stone__Limestone"]["color"] == STONE_HEX,
      f"FBX parts {[(k, v['color']) for k, v in bn.items()]}")
check("negative test flagged: the pre-v210b bank_backing_stone fails the stone-only rule (__OakDeep cap #7A4E32 + __Moss)",
      set(map(mat_of, bo)) - {"Limestone"} == {"OakDeep", "Moss"}, f"old parts {[(k, v['color']) for k, v in bo.items()]}")
Vn, Vo = bn["bank_backing_stone__Limestone"]["V"], bo["bank_backing_stone__Limestone"]["V"]
d_blk = subset(Vo, Vn)
check("v210b bank_backing_stone stone blocks unchanged (every pre-v210b __Limestone vertex is in the new part)",
      d_blk <= 1e-4, f"max dev {d_blk:.1e}")
kd = KDTree(len(Vo))
for i, p in enumerate(Vo):
    kd.insert(Vector(p), i)
kd.balance()
capV = np.array([p for p in Vn if kd.find(Vector(p))[2] > 1e-4])
import props_dressing as PD
rc = PD.RAILKIT_CAP
cmn, cmx = capV.min(0), capV.max(0)
enc = dict(x=min(-rc["half_w"] - cmn[0], cmx[0] - rc["half_w"]), y=min(rc["y0"] - cmn[1], cmx[1] - rc["y1"]),
           z=min(-rc["half_l"] - cmn[2], cmx[2] - rc["half_l"]))
check("v210b backing cap (stone) encloses a rail-kit cap laid on the same *_backing wall line (RAIL_NOTE: base = bank "
      "top 1.2, 0.56 x 0.28, wall length 12.1924) by >= 0.02 on every side (was a duplicate oak cap 0.005 under the "
      "old cap top)", all(v >= 0.02 - 1e-4 for v in enc.values()),
      f"cap x {cmn[0]:.3f}..{cmx[0]:.3f} y {cmn[1]:.3f}..{cmx[1]:.3f} z {cmn[2]:.4f}..{cmx[2]:.4f}; margins "
      + ", ".join(f"{k} {v:.4f}" for k, v in enc.items()))
oc = bo["bank_backing_stone__OakDeep"]
Bo_cap = BF._bvh(oc["T"])
mo = bo["bank_backing_stone__Moss"]["V"]
n_in = sum(BF._inside(Bo_cap, p) for p in mo)
check("v210b removed moss was invisible: every pre-v210b __Moss vertex lies inside the old cap (removal changes no "
      "visible pixel; the cap is now stone)", n_in == len(mo), f"{n_in}/{len(mo)} vertices inside")
blk = np.array([p for p in Vn if kd.find(Vector(p))[2] <= 1e-4])
check("v210b backing felt-facing stone faces unchanged at |x| 0.24 (0.01 behind the felt edge at 0.25 on both "
      "sides: the felt is on -X for H3 bank1/H8/H9 and +X for H3 bank2); cap overhang starts >= 0.5 above the bank top "
      "(ball r 0.08)", abs(np.abs(blk[:, 0]).max() - 0.24) < 1e-4 and cmn[1] - 1.2 >= 0.5,
      f"blocks |x| max {np.abs(blk[:, 0]).max():.4f}, cap bottom {cmn[1]:.3f} = bank top + {cmn[1] - 1.2:.2f}")

# ---- D2 placements == holes.json *_backing walls (H8 bank2 was 9 studs off)
def backing_place_ok(pls):
    rows, ok = [], True
    for H in (3, 8, 9):
        h = HOLE[H]
        banks = {f["id"]: f for f in h["felt"] if f.get("kind") == "bank" and f["id"] + "_backing" in
                 {w["id"] for w in h["walls"]}}
        for w in [w for w in h["walls"] if w["id"].endswith("_backing")]:
            m = [p for p in pls if p["hole"] == f"H{H}" and p.get("note") == w["id"]]
            f = banks[w["id"][:-len("_backing")]]
            low = f["center"][1] - abs(f["slope"]["rise"]) / 2
            good = (len(m) == 1 and math.hypot(m[0]["pos"][0] - w["center"][0], m[0]["pos"][2] - w["center"][2]) < 1e-3
                    and (m[0]["yaw"] - w["yaw"]) % 360 == 0 and abs(m[0]["pos"][1] - low) < 1e-3)
            dz = (m[0]["pos"][2] - w["center"][2]) if m else None
            rows.append(f"H{H} {w['id']} {'ok' if good else 'OFF'}" + (f" (dz {dz:+.2f})" if m and not good else ""))
            ok &= good
    return ok, rows


ok, rows = backing_place_ok(PA2["bank_backing_stone"]["placements"])
check("v210b every H3/H8/H9 *_backing wall has exactly one bank_backing_stone placement on it (centre x/z, yaw, base "
      "y = bank low edge)", ok and len(PA2["bank_backing_stone"]["placements"]) == 5, "; ".join(rows))
ok0, rows0 = backing_place_ok(PB2["bank_backing_stone"]["placements"])
check("negative test flagged: pre-v210b placements (H8 bank2_backing at z -49.7753, 9 studs from its wall)",
      not ok0, "; ".join(r for r in rows0 if "OFF" in r))

# ---- D3 h8_alcove_bank_cladding: stone, same skin geometry, moss streaks removed
cn, co = N2["h8_alcove_bank_cladding"], O2["h8_alcove_bank_cladding"]
ce = PA2["h8_alcove_bank_cladding"]
check("v210b h8_alcove_bank_cladding renders stone only: one part __Limestone #B8AFA0 (manifest + FBX), was __RootBark "
      "#5B3A22 + __Moss", list(cn) == ["h8_alcove_bank_cladding__Limestone"] and
      [(q["color"], q["roblox_material"]) for q in ce["parts"]] == [(STONE_HEX, "Limestone")] and
      cn["h8_alcove_bank_cladding__Limestone"]["color"] == STONE_HEX and set(map(mat_of, co)) == {"RootBark", "Moss"},
      f"new {[(k, v['color']) for k, v in cn.items()]}, old {[(k, v['color']) for k, v in co.items()]}")
dv = same_points(cn["h8_alcove_bank_cladding__Limestone"]["V"], co["h8_alcove_bank_cladding__RootBark"]["V"], 1e-4)
check("v210b h8_alcove_bank_cladding skin geometry unchanged (== pre-v210b __RootBark, every vertex)", dv[0],
      f"max dev {dv[1]:.1e}, {len(cn['h8_alcove_bank_cladding__Limestone']['T'])} tris")

# ---- D4 H9 rails: OakDeep tops + faces, limestone posts; trim kit H8 only; hole skin
REG = {p["name"]: p for p in registry.PROPS}
okr, det = True, []
for L in (4, 2):
    n = f"rail_straight_{L}_h9"
    q = PA2[n]["parts"]
    tr = BF.build_tris(f"rail_straight_{L}_trim")
    trV = np.concatenate([t.reshape(-1, 3) for t in tr.values()])
    nV = N2[n][f"{n}__OakDeep"]["V"] if f"{n}__OakDeep" in N2[n] else np.zeros((1, 3))
    g = subset(trV, nV) <= 1e-4 and subset(nV, trV) <= 1e-4
    good = (list(N2[n]) == [f"{n}__OakDeep"] and N2[n][f"{n}__OakDeep"]["color"] == OAK_HEX and
            [(x["color"], x["roblox_material"], x.get("reflectance")) for x in q] == [(OAK_HEX, "WoodPlanks", 0.0)] and g)
    okr &= good
    det.append(f"{n}: {[(x['mesh'].split('__')[1], x['color'], x.get('reflectance')) for x in q]} geometry==trim {g}")
check("v210b H9 rails: rail_straight_4_h9 / _2_h9 tops + faces one part __OakDeep #7A4E32 WoodPlanks Reflectance 0 "
      "(manifest + FBX), same geometry as the trim kit", okr, "; ".join(det))
pq = PA2["rail_end_post_h9"]["parts"]
check("v210b H9 end posts: rail_end_post_h9 one part __Limestone #B8AFA0 (the only limestone on the H9 rails)",
      list(N2["rail_end_post_h9"]) == ["rail_end_post_h9__Limestone"] and
      N2["rail_end_post_h9"]["rail_end_post_h9__Limestone"]["color"] == STONE_HEX and
      [(x["color"], x["roblox_material"]) for x in pq] == [(STONE_HEX, "Limestone")], str([(x["mesh"], x["color"]) for x in pq]))
sk = json.load(open(os.path.join(OUTD, "manifest.json")))["hole_skins"]["holes"]
s9 = sk["H9"]
h9_rail_props = [s9["rail_straight_4"], s9["rail_straight_2"]]
lime_h9 = sorted({x["mesh"] for n in h9_rail_props for x in PA2[n]["parts"] if x["color"] == STONE_HEX})
check("v210b hole_skins.H9 -> rail_*_h9: block + cap OakDeep #7A4E32 Reflectance 0, post Limestone #B8AFA0; no "
      "limestone on any H9 rail piece; trim kit now H8 only (H8 skin unchanged)",
      s9["rail_straight_4"] == "rail_straight_4_h9" and s9["rail_end_post"] == "rail_end_post_h9" and
      s9["rail_block_color"] == s9["rail_cap_color"] == OAK_HEX and s9["rail_block_reflectance"] == 0 and
      s9["rail_post_color"] == STONE_HEX and not lime_h9 and all(PA2[n]["holes"] == ["H8"] for n in TRIM_META) and
      sk["H8"] == MB2["hole_skins"]["holes"]["H8"],
      f"H9 {s9['rail_straight_4']}/{s9['rail_straight_2']}/{s9['rail_end_post']} block {s9['rail_block_color']} cap "
      f"{s9['rail_cap_color']} post {s9['rail_post_color']}; trim holes {[PA2[n]['holes'] for n in TRIM_META]}")
dfl = PA2["timber_deflector_board"]
check("v210b H9 timber_deflector_board keeps the v210 result (manifest entry identical: planks __OakDeep #7A4E32 "
      "Reflectance 0)", dfl == PB2["timber_deflector_board"] and
      [(x["color"], x.get("reflectance")) for x in dfl["parts"] if x["material"] == "OakDeep"] == [(OAK_HEX, 0.0)], "")

# ---- D5 H9 bank lip: separate #6CC79F part, no glow, entirely outside the playable felt, visible
ln = N2["h9_bank_lip"]
le = PA2["h9_bank_lip"]
emi = fbx_mats(os.path.join(FB, "h9_bank_lip.fbx"))
check("v210b h9_bank_lip: separate MeshPart h9_bank_lip__BankLip, colour #6CC79F (manifest + FBX), SmoothPlastic (not "
      "Neon), emission 0 (lglib + FBX), transparency 0, 0.05 x 0.05 section",
      list(ln) == ["h9_bank_lip__BankLip"] and ln["h9_bank_lip__BankLip"]["color"] == LIP_HEX and
      [(x["color"], x["roblox_material"], x["transparency"]) for x in le["parts"]] == [(LIP_HEX, "SmoothPlastic", 0)] and
      lglib.MATS["BankLip"][2] == 0 and emi.get("h9_bank_lip__BankLip", 1) == 0 and
      np.allclose(le["bbox_size_studs"][:2], [0.05, 0.05], atol=1e-3),
      f"FBX colour {ln['h9_bank_lip__BankLip']['color']}, FBX emission {emi}, size {le['bbox_size_studs']}")
check("v210b h9_bank_lip visual only: manifest collision rule CanCollide/CanQuery/CanTouch false (no holes.json "
      "geometry), no PointLight / lights entry", "CanCollide=false" in json.load(open(os.path.join(OUTD, "manifest.json")))
      ["collision"] and "CanCollide/CanQuery/CanTouch off" in le["notes"] and
      not any("h9_bank_lip" in json.dumps(v) for k, v in json.load(open(os.path.join(OUTD, "manifest.json"))).items()
              if k in ("lights", "emissive", "h9_emissive_dim")), "")
h9 = HOLE[9]
lpl = le["placements"]
banks9 = [f for f in h9["felt"] if f.get("kind") == "bank"]
check("v210b one lip per H9 bank, placed in its backing's frame (== the bank_backing_stone placement)",
      len(lpl) == len(banks9) == 1 and all(any(p["pos"] == q["pos"] and p["yaw"] == q["yaw"] for q in
                                               PA2["bank_backing_stone"]["placements"] if q["hole"] == "H9")
                                           for p in lpl), f"banks {[f['id'] for f in banks9]}, lips {lpl}")
TL = BF.place(ln["h9_bank_lip__BankLip"]["T"], lpl[0]["pos"], lpl[0]["yaw"])
LV = np.unique(np.round(np.concatenate([BF.surface_samples(TL, 0.01)[0], TL.reshape(-1, 3)]), 6), axis=0)
wallB = [w for w in h9["walls"] if w["id"] == "bank1_backing"][0]
bank1 = banks9[0]


def in_box_plan(P, c, size_xz, yaw, pad=0.0):
    l = (P - np.array(c, float)) @ BF.yaw_mat(yaw)
    return (np.abs(l[:, 0]) <= size_xz[0] / 2 + pad) & (np.abs(l[:, 2]) <= size_xz[1] / 2 + pad)


def playable(P, h):
    """Points (plan) the ball can roll on: inside a felt rectangle, not inside a wall footprint, and not behind a
    *_backing wall (beyond its felt-facing face, within its length)."""
    on = np.zeros(len(P), bool)
    for f in h["felt"]:
        on |= in_box_plan(P, f["center"], f["size"], f.get("yaw", 0))
    for w in h["walls"]:
        on &= ~in_box_plan(P, w["center"], (w["size"][0], w["size"][2]), w.get("yaw", 0))
    for f in h["felt"]:
        if f.get("kind") != "bank":
            continue
        w = [x for x in h["walls"] if x["id"] == f["id"] + "_backing"][0]
        R = BF.yaw_mat(w["yaw"])
        l = (P - np.array(w["center"])) @ R
        fb = (np.array(f["center"]) - np.array(w["center"])) @ R
        sd = np.sign(fb[0])
        behind = (l[:, 0] * sd <= -w["size"][0] / 2) & (np.abs(l[:, 2]) <= w["size"][2] / 2)
        on &= ~behind
    return on


in_wall = in_box_plan(LV, wallB["center"], (wallB["size"][0], wallB["size"][2]), wallB["yaw"]).all()
lb = (LV - np.array(bank1["center"])) @ BF.yaw_mat(bank1["yaw"])
gap = (np.abs(lb[:, 0]) - bank1["size"][0] / 2).min()
nplay = int(playable(LV, h9).sum())
rails_hit = [w["id"] for w in h9["walls"] if w["id"] != "bank1_backing" and
             in_box_plan(LV, w["center"], (w["size"][0], w["size"][2]), w.get("yaw", 0)).any()]
y_lo, y_hi = LV[:, 1].min(), LV[:, 1].max()
top = bank1["center"][1] + abs(bank1["slope"]["rise"]) / 2
check("v210b h9_bank_lip entirely outside the playable felt (holes.json): every vertex + 0.01 surface sample lies in the "
      "bank1_backing wall footprint, behind the bank1 felt's high edge, on no playable felt (felt rects minus walls "
      "minus the area behind *_backing walls), in no rail wall; bottom at the bank top edge",
      in_wall and gap > 0 and nplay == 0 and not rails_hit and abs(y_lo - top) < 1e-3,
      f"{len(LV)} points: in wall {in_wall}, min gap behind felt edge {gap:.4f}, on playable felt {nplay}, rails "
      f"{rails_hit}, y {y_lo:.3f}..{y_hi:.3f} (bank top {top})")
_tow = (np.array(bank1["center"], float) - np.array(wallB["center"], float)) * [1, 0, 1]
LVs = LV + _tow / np.linalg.norm(_tow) * 0.01             # 0.01 toward the bank felt
check("negative test flagged: the lip moved 0.01 toward the felt is on the playable felt",
      int(playable(LVs, h9).sum()) > 0, f"{int(playable(LVs, h9).sum())} points on felt")
st_face = 0.24
lx = (LV - np.array(lpl[0]["pos"])) @ BF.yaw_mat(lpl[0]["yaw"])
proud = -lx[:, 0].min() - st_face if PV.LIPS[0]["side"] < 0 else lx[:, 0].max() - st_face
check("v210b h9_bank_lip shows: its felt-facing face is in front of the backing's stone face (>= 0.008, no z-fight) "
      "and it runs the bank's top edge between the rails", proud >= 0.008 and le["bbox_size_studs"][2] > 5.0,
      f"proud {proud:.4f}, length {le['bbox_size_studs'][2]} (bank {bank1['size'][1]}, clipped at {rails_hit or 'rail5/rail4 faces'})")

# ---- D6 coplanar overlaps (z-fighting) per FBX file, before / after
cop = {}
files = sorted(f for f in os.listdir(FB) if f.endswith(".fbx"))
for f in files:
    after = CP.count_overlaps({k: v["T"] for k, v in fbx_parts(os.path.join(FB, f)).items()})
    bpath = os.path.join(OLD2, f) if os.path.exists(os.path.join(OLD2, f)) else (
        os.path.join(SHIPPED_B, f) if SHIPPED_B and os.path.exists(os.path.join(SHIPPED_B, f)) else None)
    before = CP.count_overlaps({k: v["T"] for k, v in fbx_parts(bpath).items()}) if bpath else None
    same = bool(bpath) and open(bpath, "rb").read() == open(os.path.join(FB, f), "rb").read()
    cop[f] = dict(before=before, after=after, byte_identical_to_before=same, new=bpath is None)
chg = [f for f in files if not cop[f]["byte_identical_to_before"]]
check("v210b coplanar-overlap (z-fight) check, every changed / new FBX: 0 overlapping same-facing coplanar face pairs "
      f"(plane tol {CP.PLANE_TOL}, area > {CP.AREA_TOL})", all(cop[f]["after"]["pairs"] == 0 for f in chg),
      "; ".join(f"{f[:-4]} {cop[f]['before']['pairs'] if cop[f]['before'] else '-'} -> {cop[f]['after']['pairs']}"
                for f in chg))
unch = [f for f in files if cop[f]["byte_identical_to_before"]]
check("v210b unchanged FBX are byte-identical to the shipped ones (so their coplanar counts are unchanged)",
      len(unch) + len(chg) == len(files) and all(cop[f]["before"]["pairs"] == cop[f]["after"]["pairs"] for f in unch),
      "; ".join(f"{f[:-4]} {cop[f]['after']['pairs']}" for f in unch))

# ---- D6b dedupe of the H3 / H8 dressing (duplicate oak faces)
DD = json.load(open(os.path.join(SRC, "dedupe_v210b.json")))
_ok = all(v["coplanar_after"] == 0 and v["every_other_polygon_position_uv_material_transform_identical"] and
          v["parts_same"] and v["images_same"] and list(v["removed"]) == [f"{k}__Oak"] for k, v in DD.items())
_dn = [k for k in DD]
_inv = all(max(c[2] for c in poly) - min(c[2] for c in poly) < 1e-6        # flat at one height (Blender mesh, Z up)
           for k in _dn for part in DD[k]["removed_polygons_corners"] for poly in part)
check("v210b dressing_h03_a / dressing_h08_a: only the duplicate oak faces removed (each a flat, down-facing lantern-pole "
      "post bottom lying on its slate footing's bottom face); every other polygon, UV, material, image and transform "
      "identical to the shipped FBX; 0 coplanar pairs left", _ok and _inv and set(_dn) == {"dressing_h03_a", "dressing_h08_a"},
      "; ".join(f"{k}: removed {v['removed']}, coplanar {v['coplanar_before']} -> {v['coplanar_after']}, polygons "
                f"identical {v['every_other_polygon_position_uv_material_transform_identical']}" for k, v in DD.items()))

# ---- D7 assembled hole-local scenes: backing (+ H9 lip) vs the rail kit (Studio-placed, modelled from holes.json)
kits = {}


def kit(H):
    s = hole_skins.SKINS[f"H{H}"]
    if H not in kits:
        kits[H] = dict(straight=BF.build_tris(s["rail_straight_4"]), post=BF.build_tris(s["rail_end_post"]))
    return kits[H]


bk_new = {mat_of(k): v["T"] for k, v in bn.items()}
_Tl = bn["bank_backing_stone__Limestone"]["T"]
cap_new = _Tl[np.array([all(kd.find(Vector(p))[2] > 1e-4 for p in t) for t in _Tl])]   # the new stone cap (closed box)
bk_old = {mat_of(k): v["T"] for k, v in bo.items()}
lip_T = ln["h9_bank_lip__BankLip"]["T"]
scen = {}
s1_ok, s2_cap_ok = True, True
for pl in PA2["bank_backing_stone"]["placements"]:
    H = int(pl["hole"][1:])
    h = HOLE[H]
    w = [x for x in h["walls"] if x["id"] == pl["note"]][0]
    near = (np.array(w["center"]), np.array(w["size"]) / 2, BF.yaw_mat(w["yaw"]))
    f = [x for x in h["felt"] if x["id"] == w["id"][:-len("_backing")]][0]
    for tag, bk in (("before", bk_old), ("after", bk_new)):
        B = {m: BF.place(T, pl["pos"], pl["yaw"]) for m, T in bk.items()}
        extra = {}
        if tag == "after" and H == 9:
            extra["lip__BankLip"] = BF.place(lip_T, lpl[0]["pos"], lpl[0]["yaw"])
        # S1: documented - rail kit on the rail* walls only (both height rules); they cross the backing at 45 deg
        for rule in ("note", "assembly"):
            rv = BF.rail_visuals(h, rule, kit(H), near=near)
            parts = {f"backing__{m}": T for m, T in B.items()}
            parts.update(extra)
            for r in rv:
                parts.setdefault(f"rail:{r[0]}:{r[1]}__{r[2]}", []).append(r[3])
            parts = {k: np.concatenate(v) if isinstance(v, list) else v for k, v in parts.items()}
            cp = CP.count_overlaps(parts)
            bp = {k: v for k, v in cp["by_parts"].items() if "backing__" in k or "lip__" in k}
            own = [(f"own:{m}", T) for m, T in B.items() if m in BF.TIMBER]
            occ = [BF.place(cap_new, pl["pos"], pl["yaw"])] if tag == "after" else []
            hid_own = BF.hidden_stone(B["Limestone"], own, eps=0.01, occluders=occ)[0]
            cross = [(f"{r[0]}:{r[1]}:{r[2]}", r[3]) for r in rv if r[2] in BF.TIMBER]
            hid_x = BF.hidden_stone(B["Limestone"], cross, eps=0.01, occluders=occ)[0]
            key = f"S1/{pl['hole']}/{w['id']}/{rule}/{tag}"
            scen[key] = dict(coplanar_with_backing_or_lip=sum(bp.values()), by=bp,
                             stone_under_own_timber=round(hid_own, 4), crossing_rail_footprint=round(hid_x, 4),
                             rails=sorted({r[0] for r in rv}))
            if tag == "after":
                s1_ok &= sum(bp.values()) == 0 and hid_own == 0
        # S2: legacy / misuse - a rail kit also laid on the *_backing wall line (RAIL_NOTE base = bank top)
        top_b = f["center"][1] + abs(f["slope"]["rise"]) / 2
        K = kit(H)
        c = np.array(w["center"], float)
        rl = []
        for mat, T in K["straight"].items():
            rl.append((mat, BF.place(T, [c[0], top_b, c[2]], w["yaw"], (1, 1, w["size"][2] / 4.0))))
        parts = {f"backing__{m}": T for m, T in B.items()}
        parts.update(extra)
        for mat, T in rl:
            parts[f"railkit_line__{mat}"] = T
        cp = CP.count_overlaps(parts)
        bp = {k: v for k, v in cp["by_parts"].items() if "backing__" in k}
        capm = hole_skins.SKINS[f"H{H}"]["rail_cap"]
        # the rail-kit cap = the top 0.28 of the piece
        capT = [T[(T[:, :, 1].min(1) >= top_b + 0.72 - 1e-4)] for m, T in rl if m == capm]
        capT = np.concatenate(capT) if capT else np.zeros((0, 3, 3))
        cap_pairs = CP.count_overlaps({**{f"backing__{m}": T for m, T in B.items()}, "railkit_cap": capT})
        cap_b = sum(v for k, v in cap_pairs["by_parts"].items() if "railkit_cap" in k and "backing__" in k)
        occ = [BF.place(cap_new, pl["pos"], pl["yaw"])] if tag == "after" else []
        hid = BF.hidden_stone(B["Limestone"], [(f"line:{m}", T) for m, T in rl if m in BF.TIMBER] +
                              [(f"own:{m}", T) for m, T in B.items() if m in BF.TIMBER], eps=0.01, occluders=occ)[0]
        key = f"S2/{pl['hole']}/{w['id']}/{tag}"
        scen[key] = dict(coplanar_with_backing=sum(bp.values()), by=bp, railkit_cap_vs_backing=cap_b,
                         stone_inside_or_under_timber=round(hid, 4), rail_kit=hole_skins.SKINS[f"H{H}"]["rail_straight_4"])
        if tag == "after":
            s2_cap_ok &= cap_b == 0
s1b = {k: v for k, v in scen.items() if k.startswith("S1") and k.endswith("/before")}
s1a = {k: v for k, v in scen.items() if k.startswith("S1") and k.endswith("/after")}
check("v210b assembled H3/H8/H9 (documented rail kit on the rail* walls, RAIL_NOTE + assembly heights; H9 = new oak kit "
      "+ lip): 0 coplanar overlaps between a backing / the lip and any rail piece, and no backing stone under its own "
      "timber any more", s1_ok,
      f"stone under own oak cap (within 0.01) before {sum(v['stone_under_own_timber'] for v in s1b.values()):.3f} -> after "
      f"{sum(v['stone_under_own_timber'] for v in s1a.values()):.3f} stud^2; coplanar before "
      f"{sum(v['coplanar_with_backing_or_lip'] for v in s1b.values())} -> after "
      f"{sum(v['coplanar_with_backing_or_lip'] for v in s1a.values())}")
s2b = {k: v for k, v in scen.items() if k.startswith("S2") and k.endswith("/before")}
s2a = {k: v for k, v in scen.items() if k.startswith("S2") and k.endswith("/after")}
check("v210b duplicate cap gone: a rail kit laid on a *_backing wall line (RAIL_NOTE base = bank top) no longer has a "
      "cap face coplanar with the backing (its cap is enclosed by the stone cap)", s2_cap_ok,
      "rail-kit cap vs backing coplanar pairs before " + ", ".join(f"{k.split('/')[1]}/{k.split('/')[2]} {v['railkit_cap_vs_backing']}"
                                                                 for k, v in s2b.items()) +
      " -> after " + ", ".join(f"{v['railkit_cap_vs_backing']}" for v in s2a.values()))
for k in s2a:
    kb = k.replace("/after", "/before")
    lines.append(f"NOTE  S2 {k.split('/')[1]} {k.split('/')[2]}: rail kit on the backing line ({s2a[k]['rail_kit']}): "
                 f"coplanar with backing {s2b[kb]['coplanar_with_backing']} -> {s2a[k]['coplanar_with_backing']}, stone "
                 f"inside/under timber {s2b[kb]['stone_inside_or_under_timber']:.3f} -> "
                 f"{s2a[k]['stone_inside_or_under_timber']:.3f} stud^2. The rest are its 0.48 blocks on the backing's own "
                 f"faces: remove rail-kit pieces from *_backing walls (manifest v210b.roblox).")
for k in sorted(s1a):
    if s1a[k]["crossing_rail_footprint"] > 0:
        lines.append(f"NOTE  S1 {k.split('/')[1]} {k.split('/')[2]} {k.split('/')[3]}: rails {s1a[k]['rails']} cross the "
                     f"backing at 45 deg (T-junction footprint {s1a[k]['crossing_rail_footprint']:.3f} stud^2 where the "
                     f"rail passes through the stone; expected, not coplanar)")
json.dump(dict(per_file=cop, assembled=scen, plane_tol=CP.PLANE_TOL, area_tol=CP.AREA_TOL),
          open(os.path.join(SRC, "coplanar_v210b.json"), "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))

# ---- D8 integrity: manifest diff limited to the v210b entries; holes.json read only; triangles
MA = json.load(open(os.path.join(OUTD, "manifest.json")))
others = [n for n in PB2 if n not in CHANGED_B + TRIM_META]
diff = [n for n in others if PA2.get(n) != PB2[n]]
check("v210b manifest: only bank_backing_stone, h8_alcove_bank_cladding and the trim kit's holes/notes changed; 4 new "
      "entries; every other prop entry identical to pre-v210b", not diff and set(PA2) == set(PB2) | set(NEW_B) and
      all({k: v for k, v in PA2[n].items() if k not in ("holes", "notes")} ==
          {k: v for k, v in PB2[n].items() if k not in ("holes", "notes")} for n in TRIM_META),
      f"{len(others)} entries compared; differ: {diff}")
import copy
_d0, _d1 = copy.deepcopy(MB2["dressing"]), copy.deepcopy(MA["dressing"])
_fx = {}
for _H in ("H3", "H8"):
    _a, _b = _d0["holes"][_H].pop("fbx"), _d1["holes"][_H].pop("fbx")
    _strip = lambda L: [{k: (v if k != "parts" else [{kk: vv for kk, vv in q.items() if kk != "tris"} for q in v])
                         for k, v in f.items() if k not in ("triangles", "v210b")} for f in L]
    _fx[_H] = _strip(_a) == _strip(_b)
_top2 = [k for k in MB2 if k not in ("props", "textures", "hole_skins", "v210b", "dressing") and MB2[k] != MA.get(k)]
if _d0 != _d1 or not all(_fx.values()):
    _top2.append("dressing")
_tx2 = set(MA["textures"]["untextured"]) - set(MB2["textures"]["untextured"])
check("v210b manifest top-level blocks preserved (world, lights, emissive, h9_emissive_dim, v210, ...; dressing except "
      "the H3/H8 near-field fbx[] triangle counts); textures only gains BankLip as untextured; hole_skins only H9 changed",
      not _top2 and _tx2 == {"BankLip"} and {h: v for h, v in MA["hole_skins"]["holes"].items() if h != "H9"} ==
      {h: v for h, v in MB2["hole_skins"]["holes"].items() if h != "H9"}, f"changed {_top2}, textures +{_tx2}")
tri2 = {n: (sum(len(p["T"]) for p in N2[n].values()), PA2[n]["triangles"]) for n in CHANGED_B + NEW_B}
for _H, _n in (("H3", "dressing_h03_a"), ("H8", "dressing_h08_a")):
    _e = [f for f in MA["dressing"]["holes"][_H]["fbx"] if f["fbx"] == f"fbx/{_n}.fbx"][0]
    tri2[_n] = (sum(len(p["T"]) for p in fbx_parts(os.path.join(FB, f"{_n}.fbx")).values()), _e["triangles"])
check("v210b changed / new FBX < 20k tris and manifest triangles == FBX", all(a == b and a < 20000 for a, b in tri2.values()),
      str(tri2))
_r16 = [w for w in HOLE[8]["walls"] if w["id"] == "rail16"][0]
_bk = {f"H{n}:{f['id']}": (f["center"], f["size"], f["slope"]) for n in (3, 8, 9) for f in HOLE[n]["felt"]
       if f.get("kind") == "bank"}
_mv = {f"H{n}:{m['id']}": m.get("speed") for n in (8, 9) for m in HOLE[n]["moving_parts"]}
check("v210b holes.json read only: same sha256 as v210; rail16 + banks untouched; mover speeds unchanged (Studio's job)",
      _hs == _hs_v210 and _r16["center"] == [6.5, 1.7, -7.75] and
      _mv == {"H8:root_door": 3.0, "H9:root_gate": 0.9, "H9:lantern_pendulum": 17.2788},
      f"sha256 {_hs} (v210 {_hs_v210}); banks {len(_bk)}; speeds {_mv}")

# ---------------------------------------------------------------------------- write
nf = sum(1 for l in lines if l.startswith("FAIL"))
npass = sum(1 for l in lines if l.startswith("PASS"))
hdr = [f"# Lantern Grove v210b fitcheck ({'ALL PASS' if nf == 0 else f'{nf} FAIL'}, {npass + nf} checks) - Blender "
       f"{bpy.app.version_string}; holes.json {HOLES_PATH} (sha256 {_hs})",
       "# Latest suite = fitcheck_v210.py A + B + C1-C2 re-run unchanged, then the v210b section D. v210 C3/C4 are",
       "# superseded by D (bank_backing_stone is no longer OakDeep-capped; the manifest gained v210b entries).",
       "# NOT RUN here (inputs not in this job): fitcheck.py pass 4/5 world-dressing sections and the fitcheck_pass6-10",
       "# sections that need world/world.json, terrain, world_occ or the ~100 FBX not shipped.",
       "# Rail kit is placed in Studio (not in the manifest): D7 models it from holes.json with both documented rules.",
       f"# door <-> pocket sweep (v210 C2, unchanged pocket): min {SW['min']:.4f} at slide offset {SW['offset']:.4f}", ""]
out = "\n".join(hdr + lines)
print(out)
open(os.path.join(SRC, "fitcheck_v210b.txt"), "w").write(out + "\n")
