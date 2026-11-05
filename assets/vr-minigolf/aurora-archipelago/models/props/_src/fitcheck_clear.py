# Round 3 'clear' fit checks. exec()'d by fitcheck.py after fitcheck_decor.py (uses its namespace: check, flag, LINES,
# REPORT, build, place_matrix, tris_of, samples, felt_top, rot_points, D, REG, registry, np, math, bpy, os, OUT, SRC).
# Everything here reads the re-imported FBX on disk (what Studio gets), not only the generators.
LINES.append("")
LINES.append("# Round 3 'clear' (holes.json clearance fix): collision FBX, visual vs collider, FBX on disk vs generator")
_man = json.load(open(os.path.join(OUT, "manifest.json")))
_MP = {p["name"]: p for p in _man["props"]}
_CF = {c["prop"]: c for c in _man.get("collision_fbx_files", [])}
_MOV = (("aa_h12_paddle_wheel", 12, "paddle_wheel"), ("aa_h14_icicle_bell", 14, "icicle_bell"))
REPORT["clear"] = {}


def _fbx_meshes(path):
    """{object name: (Roblox verts in the FBX/prop frame, tris, n materials)} of a re-imported FBX; also the roots."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y")
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    out, roots = {}, []
    for o in new:
        if o.parent is None:
            roots.append((o.name.split(".")[0], tuple(o.matrix_world.translation)))
        if o.type != "MESH":
            continue
        me = o.data
        me.calc_loop_triangles()
        mw = np.array(o.matrix_world)
        V = np.array([v.co[:] for v in me.vertices], float) @ mw[:3, :3].T + mw[:3, 3]
        out[o.name.split(".")[0]] = (np.stack([V[:, 0], V[:, 2], -V[:, 1]], 1), len(me.loop_triangles), len(me.materials))
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    return out, roots


def _corners(b):
    C = []
    for sx in (-.5, .5):
        for sy in (-.5, .5):
            for sz in (-.5, .5):
                x, z = D.yaw_rot(sx * b["size"][0], sz * b["size"][2], b.get("yaw", 0.0))
                C.append([b["center"][0] + x, b["center"][1] + sy * b["size"][1], b["center"][2] + z])
    C = np.array(C)
    return rot_points(C, [0, 0, 1], b["roll"]) if b.get("roll") else C


# ---------------------------------------------------------------- 1. collision FBX == holes.json blockers
for name, n, mid in _MOV:
    m = D.mover(n, mid)
    cf = _CF.get(name)
    path = os.path.join(OUT, cf["file"]) if cf else None
    if not cf or not os.path.exists(path):
        check(f"H{n} {name}: collision FBX present", False, str(cf))
        continue
    ms, roots = _fbx_meshes(path)
    dev, bad = 0.0, []
    for i, b in enumerate(m["blockers"]):
        k = f"{name}_collision__Collider_b{i + 1:02d}"
        if k not in ms:
            bad.append(f"missing {k}")
            continue
        V, nt, nm = ms[k]
        U = np.unique(V.round(6), axis=0)
        C = _corners(b)
        d = max(np.linalg.norm(U[:, None, :] - C[None, :, :], axis=2).min(1).max(),
                np.linalg.norm(C[:, None, :] - U[None, :, :], axis=2).min(1).max())
        dev = max(dev, float(d))
        if len(U) != 8 or nt != 12 or nm != 1 or d > 1e-4:
            bad.append(f"{k}: {len(U)} verts, {nt} tris, {nm} mats, dev {d:.1e}")
    extra = sorted(set(ms) - {f"{name}_collision__Collider_b{i + 1:02d}" for i in range(len(m["blockers"]))})
    rootok = len(roots) == 1 and max(abs(v) for v in roots[0][1]) < 1e-6
    check(f"H{n} {cf['file']}: {len(m['blockers'])} box meshes == the {len(m['blockers'])} Round-3 holes.json blockers exactly "
          f"(8 corners each, yaw/roll applied, max corner deviation {dev:.1e}); 12 tris + 1 material each; root at the pivot "
          f"(FBX origin = holes.json pivot {m['pivot']}, same frame as the visual FBX)",
          not bad and not extra and rootok and len(ms) == len(m["blockers"]), "; ".join(bad + extra) + ("" if rootok else f" roots {roots}"))
    tri = sum(v[1] for v in ms.values())
    check(f"H{n} {name}: manifest collision_fbx_files entry consistent (file, {tri} tris, pivot) and the prop entry points to it",
          cf["triangles"] == tri and cf["pivot"] == m["pivot"] and _MP[name].get("collision_fbx") == cf["file"] and tri < 20000)
    # felt sweep of the collision FBX itself (its box corners), same steps as the pass-2d fine sweep
    P = np.concatenate([v[0] for v in ms.values()])
    angs = np.arange(0, 360, 0.05) if m["type"] == "rotate" else np.arange(-m["amplitude_deg"], m["amplitude_deg"] + 1e-9, 0.01)
    best = (1e9, None)
    piv = np.array(m["pivot"], float)
    for a in angs:
        W = rot_points(P, m["axis"], a) + piv
        ft = felt_top(n, W, shrink=0.01)
        k = ~np.isnan(ft)
        if k.any():
            g = float((W[k, 1] - ft[k]).min())
            if g < best[0]:
                best = (g, float(a))
    REPORT["clear"][f"{name}_collision_felt_sweep"] = dict(min_gap=round(best[0], 4), at_deg=round(best[1], 3), steps=len(angs))
    check(f"H{n} {name}_collision.fbx swept ({len(angs)} steps): lowest collider corner {best[0]:.4f} over the felt at {best[1]:+.2f} deg "
          f"(Round 3 target >= 0.06, < 0.16)", 0.06 - 1e-4 <= best[0] < 0.16)
    pv = _MP[name]["placements"][0]["pos"]
    check(f"H{n} {name}: manifest placement / motion pivot == holes.json pivot {m['pivot']} (Round 3)",
          list(pv) == list(m["pivot"]) and _MP[name]["motion"]["course_local_pivot"] == m["pivot"])

# ---------------------------------------------------------------- 2. visual FBX envelopes the colliders
vis = {name: _fbx_meshes(os.path.join(OUT, "fbx", f"{name}.fbx"))[0] for name, n, mid in _MOV}
# H14: skid underside (Brass vertices on the z faces below the cube bottom) never above any strip bottom
m14 = D.mover(14, "icicle_bell")
Vb = vis["aa_h14_icicle_bell"]["aa_h14_icicle_bell__Brass"][0]
U = Vb[(np.abs(np.abs(Vb[:, 2]) - 0.075) < 1e-4) & (Vb[:, 1] < -10.0 - 1e-6)]
U = U[np.argsort(U[:, 0])]
ux, uy = np.unique(U[:, 0].round(6), return_index=True)
uy = U[uy, 1]
worst, rbad = -1e9, []
for b in m14["blockers"][1:]:
    x0, x1 = b["center"][0] - b["size"][0] / 2, b["center"][0] + b["size"][0] / 2
    xs_ = np.concatenate([[x0, x1], ux[(ux > x0) & (ux < x1)]])
    yv = np.interp(xs_, ux, uy)
    d = float((yv - (b["center"][1] - b["size"][1] / 2)).max())
    worst = max(worst, d)
r_on = np.hypot(ux, uy)
check(f"H14 visual skid underside covers all 9 strip colliders: never above a strip bottom (max {worst:+.5f}); its {len(ux)} "
      f"underside vertices lie on r {r_on.min():.4f}..{r_on.max():.4f} about the hinge (holes.json strip-corner arc "
      f"{sys.modules['props_movers'].H14_SKID_R:g}); spans x {ux.min():+.3f}..{ux.max():+.3f}",
      worst <= 1e-4 and abs(r_on.min() - sys.modules["props_movers"].H14_SKID_R) < 2e-4 and
      abs(r_on.max() - sys.modules["props_movers"].H14_SKID_R) < 2e-4 and abs(ux.min() + 1.05) < 1e-3 and abs(ux.max() - 1.05) < 1e-3)
# H12: at every strip's outer corners the red tip reaches at least the corner radius
m12 = D.mover(12, "paddle_wheel")
Vr = vis["aa_h12_paddle_wheel"]["aa_h12_paddle_wheel__MoveRed"][0]
short = 0.0
for b in m12["blockers"]:
    Q = rot_points(Vr, [0, 0, 1], -b.get("roll", 0.0))
    for sx in (-.5, .5):
        for sz in (-.5, .5):
            cx, cz = b["center"][0] + sx * b["size"][0], sz * b["size"][2]
            cy = b["center"][1] - b["size"][1] / 2
            sel = Q[(np.abs(Q[:, 0] - cx) < 1e-4) & (np.abs(Q[:, 2] - cz) < 1e-4) & (Q[:, 1] < -3.5)]
            short = max(short, (cy - sel[:, 1].min()) * -1 if len(sel) else 9.0)
rr = np.hypot(Vr[:, 0], Vr[:, 1]).max()
check(f"H12 visual paddle tips cover all 24 strip colliders (tip arc r {rr:.4f} = strip-corner radius; at every strip corner "
      f"the tip reaches >= the strip end, worst {short:+.5f})", short <= 1e-4 and abs(rr - 4.1) < 2e-4)

# ---------------------------------------------------------------- 3. FBX on disk == current generator (holes 5, 12, 14, 17)
LINES.append("# FBX on disk vs the generator run against the Round 3 holes.json (holes touched by Round 3: H5, H12, H14, H17)")
_names = sorted({p["name"] for p in registry.PROPS for pl in p["placements"] if pl["hole"] in (5, 12, 14, 17)})
_stale = {}
for nm_ in _names:
    path = os.path.join(OUT, "fbx", f"{nm_}.fbx")
    if not os.path.exists(path):
        continue
    F, _r = _fbx_meshes(path)
    G = {}
    for o in build(nm_):
        V = np.array([tuple(v.co) for v in o.data.vertices]) if len(o.data.vertices) else np.zeros((0, 3))
        G[o.name.split(".")[0]] = np.stack([V[:, 0], V[:, 2], -V[:, 1]], 1) if len(V) else V
    diff = {}
    for k in sorted(set(F) | set(G)):
        if k not in F or k not in G:
            diff[k] = "missing"
            continue
        a, b = np.unique(F[k][0].round(4), axis=0), np.unique(G[k].round(4), axis=0)
        if a.shape != b.shape or np.abs(a - b).max() > 2e-4:
            diff[k] = f"{len(a)} vs {len(b)} unique verts"
    if diff:
        _stale[nm_] = diff
REPORT["clear"]["fbx_vs_generator"] = dict(compared=_names, stale=_stale)
_expected_stale = {"aa_h05_rails", "aa_h17_rails"}
LINES.append(f"INFO  {len(_names)} prop FBX compared; differ from the Round-3 generator output: {sorted(_stale) or 'none'}")
check("Round 3 movers: aa_h12_paddle_wheel.fbx and aa_h14_icicle_bell.fbx == the generator (rebuilt this pass)",
      not any(k in _stale for k in ("aa_h12_paddle_wheel", "aa_h14_icicle_bell")), str({k: v for k, v in _stale.items() if "h12_paddle" in k or "h14_icicle" in k}))
check("no prop FBX of H5/H12/H14/H17 other than the two rail skins is stale vs the Round-3 generator",
      set(_stale) <= _expected_stale, str({k: v for k, v in _stale.items() if k not in _expected_stale}))

# ---------------------------------------------------------------- 4. rail skins vs the Round-3 trimmed walls (on-disk FBX)
_TRIM = {5: ("upper_rail8", "upper_rail12"), 17: ("pier_s_rail6", "pier_s_rail7", "pier_n_rail8", "pier_n_rail9")}
_old_h = json.load(open(os.path.join(SRC, "inputs_clear", "holes_pre_clear.json")))["holes"]
for n, ids in _TRIM.items():
    name = f"aa_h{n:02d}_rails"
    pl = _MP[name]["placements"][0]
    F, _r = _fbx_meshes(os.path.join(OUT, "fbx", f"{name}.fbx"))
    Gm = {o.name.split(".")[0]: o for o in build(name)}
    out = {}
    for tag, P0 in (("fbx", np.concatenate([v[0] for v in F.values()])),
                    ("generator", np.concatenate([np.stack([np.array([tuple(v.co) for v in o.data.vertices])[:, i] for i in (0, 2, 1)], 1) * [1, 1, -1] for o in Gm.values()]))):
        Mx = np.array(place_matrix(pl))
        Pb = np.stack([P0[:, 0], -P0[:, 2], P0[:, 1]], 1) @ Mx[:3, :3].T + Mx[:3, 3]       # Roblox -> Blender, placed
        P = np.stack([Pb[:, 0], Pb[:, 2], -Pb[:, 1]], 1)                                    # hole-local Roblox
        for wid in ids:
            w = D.wall(n, wid)
            wo = next(x for x in next(h for h in _old_h if h["number"] == n)["walls"] if x["id"] == wid)
            lx, lz = yaw_inv(P[:, 0], P[:, 2], w["center"], w.get("yaw", 0.0))
            yb, yt = w["center"][1] - w["size"][1] / 2, w["center"][1] + w["size"][1] / 2 + 0.35
            sel = (np.abs(lx) <= w["size"][0] / 2 + 0.02) & (P[:, 1] >= yb - 0.01) & (P[:, 1] <= yt) & (np.abs(lz) <= w["size"][2] / 2 + 0.6)
            over = float((np.abs(lz[sel]) - w["size"][2] / 2).max()) if sel.any() else None
            # the trimmed end = the end that moved (old vs new centre)
            out.setdefault(wid, {})[tag] = round(over, 3) if over is not None else None
            out[wid]["trim"] = round(wo["size"][2] - w["size"][2], 3)
    REPORT["clear"][f"{name}_vs_trimmed_walls"] = out
    gen_ok = all(v["generator"] is not None and v["generator"] <= 0.02 + 1e-3 for v in out.values())
    check(f"H{n} {name} GENERATOR follows the Round-3 trimmed walls ({', '.join(ids)}): skin reaches <= 0.02 past each wall end",
          gen_ok, json.dumps({k: v["generator"] for k, v in out.items()}))
    stale = {k: v["fbx"] for k, v in out.items() if v["fbx"] is not None and v["fbx"] > 0.02 + 1e-3}
    if stale:
        flag(f"H{n} {name}.fbx on disk (not rebuilt, per brief: the fitcheck rules above pass) still runs past the Round-3 trimmed "
             f"ends by {json.dumps(stale)} studs = the 0.15 trim (playtest-log modeler action: "
             f"{'upper-rail meshes end at x +-1.65' if n == 5 else 'pier rail meshes 8.85 long'}); visual only, CanCollide false. "
             f"Rebuild: build_all.py -- --only {name}")
